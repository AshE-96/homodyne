#!/usr/bin/env python3
"""
llm.py — one switch for every language-model call in Homodyne experiments.

Set ONE key, then run any episode's experiment. Nothing else to configure.

    export ANTHROPIC_API_KEY=...      # Claude (uses the official `anthropic` package: pip install anthropic)
    # or
    export GEMINI_API_KEY=...         # Google Gemini (standard library only)
    # or
    export OPENAI_API_KEY=...         # OpenAI or any OpenAI-compatible gateway (standard library only)
    export OPENAI_BASE_URL=https://…/v1   # only for a gateway; then also set HOMODYNE_MODEL
    # or
    export OPENROUTER_API_KEY=...     # OpenRouter (standard library only); always name the model:
                                      #   HOMODYNE_MODEL=openrouter:qwen/qwen3-vl-235b-a22b-instruct  (or model=...)

    python3 tools/llm.py check        # one tiny call: provider, model, latency, tokens
    python3 tools/llm.py selftest     # no key, no network: provider routing and cache-key checks

Safer than export: put the same KEY=value line in private/keys.env (git-ignored). The key is then read
by this module only and never enters any process environment, so code an experiment runs can't see it.

Optional:
    HOMODYNE_MODEL=provider:model         main model   (e.g. anthropic:claude-opus-5-5, gemini:gemini-2.5-pro)
    HOMODYNE_MODEL_SMALL=provider:model   the cheaper model in two-model experiments
    HOMODYNE_EFFORT=low|medium|high       Claude effort (default medium)
    HOMODYNE_NO_FALLBACK=1                Claude: turn off server-side refusal fallback (see below)
    HOMODYNE_TEMPERATURE=0.2              sampling temperature (unset = provider default). Sent to Gemini, Ollama and
                                          OpenAI-compatible models; NOT sent to OpenAI reasoning models (o1/o3/o4,
                                          gpt-5*) or to Claude, whose current models reject sampling parameters
                                          (a one-line note goes to stderr). Result.extra['temperature'] says what was sent.
    HOMODYNE_MAX_ATTEMPTS=5               tries per request, first one included (default 5; 1 = no retries). For
                                          Claude it sets the SDK's max_retries to this minus one.
    HOMODYNE_HTTP_TIMEOUT=900             seconds to wait for one reply (Gemini, OpenAI, OpenRouter, Ollama; default 180);
                                          a slower reply raises LLMError and is not retried
    HOMODYNE_THINKING_BUDGET=1024         Gemini only: generationConfig.thinkingConfig.thinkingBudget (unset = default)
    HOMODYNE_MODEL=mock:echo              no key, no network: deterministic fake answers for self-tests
    HOMODYNE_MODEL=openrouter:vendor/model  any model on OpenRouter (https://openrouter.ai/api/v1, OpenAI-compatible;
                                          key OPENROUTER_API_KEY). Never picked automatically: name it explicitly.
                                          Result.extra['cost_usd'] = the cost OpenRouter reports for the call, if any.

Reasoning tokens: when OpenAI or OpenRouter report them (usage.completion_tokens_details.reasoning_tokens), they are
copied to Result.extra['reasoning_tokens']; they are already inside output_tokens. Gemini's are extra['thoughts_tokens'].
    HOMODYNE_MODEL=ollama:llama3.2:3b     a model running on this computer through Ollama (no key, no internet;
                                          OLLAMA_HOST defaults to http://localhost:11434; "0.0.0.0:11434" or a
                                          host without http:// also works)

Every answer is cached on disk (keyed by provider, model, prompt and settings), so re-running an
experiment costs nothing and gives the same numbers. Delete the cache folder to re-ask.

Structured output (optional): call(..., schema={JSON Schema dict}) asks the provider's own schema-constrained
decoding to return JSON that fits the schema: Anthropic `output_config.format` (json_schema), Gemini
`generationConfig.responseMimeType` + `responseJsonSchema`, OpenAI-compatible `response_format` json_schema with
`strict: true` (also sent to Ollama). Without `schema` nothing changes, and old cache entries stay valid; with it the
schema is part of the cache key. `$comment`, `$schema` and `$id` are removed before sending. For Claude, keywords the API rejects (minimum, maximum, minLength, ...) are moved
into the field's description, as the official SDK helpers do, so check those ranges in your own code. A schema only
constrains the form of the answer, never whether its values are right.

Claude refusals: on Claude Opus/Sonnet/Fable models the request asks the API to re-run a declined
request on a fallback model (`fallbacks: "default"`). That keeps an experiment from stalling, but a
different model then wrote that answer, so every result records `model_served` and `fell_back`, and
experiments report how many rows fell back. Set HOMODYNE_NO_FALLBACK=1 to record refusals instead.
"""

import base64
import hashlib
import inspect
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

DEFAULTS = {
    # provider: (main, small)
    'anthropic': ('claude-opus-5-5', 'claude-haiku-5-5'),
    'gemini': ('gemini-2.5-pro', 'gemini-2.5-flash'),
    'openai': (None, None),  # gateways name models differently: set HOMODYNE_MODEL / HOMODYNE_MODEL_SMALL
}
KEYS = {'anthropic': 'ANTHROPIC_API_KEY', 'gemini': 'GEMINI_API_KEY', 'openai': 'OPENAI_API_KEY',
        'openrouter': 'OPENROUTER_API_KEY'}
AUTO = ('anthropic', 'gemini', 'openai')   # providers resolve() may pick on its own (openrouter must be named)
OPENROUTER_BASE = 'https://openrouter.ai/api/v1'
FALLBACK_FAMILIES = ('claude-opus-5', 'claude-sonnet-5-5', 'claude-fable-5')
KEY_FILE = Path(__file__).resolve().parent.parent / 'private' / 'keys.env'


def _file_keys():
    out = {}
    if KEY_FILE.exists():
        for line in KEY_FILE.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                out[k.strip().removeprefix('export ').strip()] = v.strip().strip('\'"')
    return out


def key(name):
    """An API key from the environment, else from private/keys.env (never copied into os.environ)."""
    return os.environ.get(name) or _file_keys().get(name)


def secrets():
    """Every key value this module could use, for redacting experiment output."""
    return [v for v in (key(k) for k in KEYS.values()) if v and len(v) >= 8]


class LLMError(RuntimeError):
    pass


@dataclass
class Result:
    text: str
    provider: str
    model_requested: str
    model_served: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_s: float = 0.0
    stop_reason: str = ''
    fell_back: bool = False
    cached: bool = False
    extra: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


def resolve(role='main'):
    """Return (provider, model) for role 'main' or 'small' from the environment."""
    var = 'HOMODYNE_MODEL' if role == 'main' else 'HOMODYNE_MODEL_SMALL'
    spec = os.environ.get(var)
    if spec:
        if ':' not in spec:
            raise LLMError(f'{var} must look like provider:model, got {spec!r}')
        provider, model = spec.split(':', 1)
        return provider, model
    for provider in AUTO:
        if key(KEYS[provider]):
            model = DEFAULTS[provider][0 if role == 'main' else 1]
            if not model:
                raise LLMError(f'{KEYS[provider]} is set; also set {var}=openai:<model name your gateway uses>')
            return provider, model
    raise LLMError('No model key found. Set ANTHROPIC_API_KEY, GEMINI_API_KEY or OPENAI_API_KEY, '
                   'or put it in private/keys.env (or HOMODYNE_MODEL=mock:echo for a dry run). See tools/llm.py.')


def _image_part(path):
    data = Path(path).read_bytes()
    mime = mimetypes.guess_type(str(path))[0] or 'image/png'
    return mime, base64.standard_b64encode(data).decode('ascii')


def max_attempts():
    try:
        return max(1, int(os.environ.get('HOMODYNE_MAX_ATTEMPTS', '5')))
    except ValueError:
        raise LLMError('HOMODYNE_MAX_ATTEMPTS must be a whole number') from None


def temperature():
    v = os.environ.get('HOMODYNE_TEMPERATURE')
    if v in (None, ''):
        return None
    try:
        return float(v)
    except ValueError:
        raise LLMError('HOMODYNE_TEMPERATURE must be a number') from None


def http_timeout():
    """Seconds to wait for one HTTP reply (HOMODYNE_HTTP_TIMEOUT, default 180). Long reasoning calls need more."""
    try:
        return max(1.0, float(os.environ.get('HOMODYNE_HTTP_TIMEOUT') or 180))
    except ValueError:
        raise LLMError('HOMODYNE_HTTP_TIMEOUT must be a number of seconds') from None


def _post(url, payload, headers, timeout=None, meta=None):
    """POST JSON with retries on 408/409/429/5xx and network errors. If `meta` (a dict) is given, it receives
    `attempts` (tries made) and `last_attempt_s` (duration of the last try, without the waits between tries).
    A reply slower than `timeout` (default http_timeout()) raises LLMError without a retry: the provider may already
    have billed the long generation, so it is not silently paid for twice."""
    timeout = timeout or http_timeout()
    body = json.dumps(payload).encode('utf-8')
    tries = max_attempts()
    meta = meta if meta is not None else {}
    for attempt in range(tries):
        req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json', **headers})
        t = time.time()
        meta['attempts'] = attempt + 1
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out = json.loads(r.read().decode('utf-8'))
            meta['last_attempt_s'] = round(time.time() - t, 3)
            return out
        except urllib.error.HTTPError as e:
            meta['last_attempt_s'] = round(time.time() - t, 3)
            detail = e.read().decode('utf-8', 'replace')[:500]
            if (e.code in (408, 409, 429) or e.code >= 500) and attempt < tries - 1:
                time.sleep(min(60, 2 ** attempt * 3))
                continue
            if e.code in (408, 409, 429) or e.code >= 500:
                break
            raise LLMError(f'HTTP {e.code}: {detail}') from None
        except TimeoutError:                # waiting for the reply (urllib does not wrap this one in URLError)
            meta['last_attempt_s'] = round(time.time() - t, 3)
            raise LLMError(f'no reply within {timeout:.0f} s (HOMODYNE_HTTP_TIMEOUT)') from None
        except urllib.error.URLError as e:
            meta['last_attempt_s'] = round(time.time() - t, 3)
            if attempt == tries - 1:
                raise LLMError(f'network error: {e.reason}') from None
            time.sleep(2 ** attempt * 3)
    raise LLMError(f'gave up after {tries} attempts (rate limit or server error)')


_NOTED = set()


def _note_once(msg):
    if msg not in _NOTED:
        _NOTED.add(msg)
        print('llm.py: ' + msg, file=sys.stderr)


# ── providers ──────────────────────────────────────────────────────────────
ANTHROPIC_UNSUPPORTED = ('minimum', 'maximum', 'exclusiveMinimum', 'exclusiveMaximum', 'multipleOf', 'minLength',
                         'maxLength', 'maxItems', 'uniqueItems', 'minProperties', 'maxProperties')
ANTHROPIC_FORMATS = ('date-time', 'time', 'date', 'duration', 'email', 'hostname', 'uri', 'ipv4', 'ipv6', 'uuid')


SCHEMA_META_KEYS = ('$comment', '$schema', '$id')


def clean_schema(schema):
    """A copy without annotation keywords some providers reject ($comment anywhere; $schema / $id at any level)."""
    if isinstance(schema, list):
        return [clean_schema(x) for x in schema]
    if not isinstance(schema, dict):
        return schema
    return {k: (v if k in ('enum', 'const', 'default') else clean_schema(v)) for k, v in schema.items()
            if k not in SCHEMA_META_KEYS}


def anthropic_schema(schema):
    """A copy of a JSON Schema that Claude's structured outputs accept: unsupported numeric/string/array constraints
    and unknown string formats are moved into `description` (they are no longer enforced by decoding), and every
    object gets additionalProperties: false."""
    if isinstance(schema, list):
        return [anthropic_schema(x) for x in schema]
    if not isinstance(schema, dict):
        return schema
    out, moved = {}, []
    for k, v in schema.items():
        if k in ANTHROPIC_UNSUPPORTED or (k == 'minItems' and v not in (0, 1)) or \
                (k == 'format' and v not in ANTHROPIC_FORMATS):
            moved.append(f'{k}: {json.dumps(v)}')
        elif k in ('properties', '$defs', 'definitions') and isinstance(v, dict):
            out[k] = {name: anthropic_schema(sub) for name, sub in v.items()}
        else:
            out[k] = anthropic_schema(v)
    if out.get('type') == 'object' or 'properties' in out:
        out['additionalProperties'] = False
    if moved:
        out['description'] = (out.get('description', '') + ' {' + ', '.join(moved) + '}').strip()
    return out


def _anthropic(model, system, prompt, images, max_tokens, schema=None):
    try:
        import anthropic
    except ImportError:
        raise LLMError('Claude needs the official SDK: pip install anthropic') from None
    retries = max_attempts() - 1
    client = anthropic.Anthropic(api_key=key('ANTHROPIC_API_KEY'), max_retries=retries)
    if temperature() is not None:
        _note_once('HOMODYNE_TEMPERATURE is not sent to Claude: current Claude models reject sampling parameters.')
    content = [{'type': 'image', 'source': {'type': 'base64', 'media_type': m, 'data': d}}
               for m, d in (_image_part(p) for p in images)]
    content.append({'type': 'text', 'text': prompt})
    kwargs = dict(model=model, max_tokens=max_tokens, messages=[{'role': 'user', 'content': content}])
    if system:
        kwargs['system'] = system
    effort = os.environ.get('HOMODYNE_EFFORT', 'medium')
    if not model.startswith('claude-haiku-4'):
        kwargs['output_config'] = {'effort': effort}
    if schema is not None:
        kwargs.setdefault('output_config', {})['format'] = {'type': 'json_schema', 'schema': anthropic_schema(schema)}
    use_fallback = model.startswith(FALLBACK_FAMILIES) and not os.environ.get('HOMODYNE_NO_FALLBACK')
    t = time.time()
    try:
        if use_fallback:
            r = client.beta.messages.create(betas=['server-side-fallback-2026-07-01'], fallbacks='default', **kwargs)
        else:
            r = client.messages.create(**kwargs)
    except anthropic.APIStatusError as e:
        raise LLMError(f'Claude API {e.status_code}: {e.message}') from None
    except anthropic.APIConnectionError:
        raise LLMError('network error reaching the Claude API') from None
    latency = time.time() - t
    text = ''.join(b.text for b in r.content if getattr(b, 'type', '') == 'text')
    fell_back = any(getattr(it, 'type', '') == 'fallback_message' for it in (getattr(r.usage, 'iterations', None) or []))
    return Result(text, 'anthropic', model, r.model, r.usage.input_tokens, r.usage.output_tokens,
                  latency, r.stop_reason or '', fell_back,
                  extra={'refusal_category': getattr(getattr(r, 'stop_details', None), 'category', None),
                         'stop_reason': r.stop_reason or '', 'model_served': r.model, 'fallback_enabled': use_fallback,
                         'max_retries': retries, 'temperature': None, 'last_attempt_s': round(latency, 3)})


def _gemini(model, system, prompt, images, max_tokens, schema=None):
    parts = [{'inline_data': {'mime_type': m, 'data': d}} for m, d in (_image_part(p) for p in images)]
    parts.append({'text': prompt})
    payload = {'contents': [{'role': 'user', 'parts': parts}], 'generationConfig': {'maxOutputTokens': max_tokens}}
    if schema is not None:
        payload['generationConfig'].update({'responseMimeType': 'application/json', 'responseJsonSchema': schema})
    temp = temperature()
    if temp is not None:
        payload['generationConfig']['temperature'] = temp
    budget = os.environ.get('HOMODYNE_THINKING_BUDGET')
    if budget not in (None, ''):
        try:
            payload['generationConfig']['thinkingConfig'] = {'thinkingBudget': int(budget)}
        except ValueError:
            raise LLMError('HOMODYNE_THINKING_BUDGET must be a whole number') from None
    if system:
        payload['systemInstruction'] = {'parts': [{'text': system}]}
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    t = time.time()
    meta = {}
    r = _post(url, payload, {'x-goog-api-key': key('GEMINI_API_KEY')}, meta=meta)
    latency = time.time() - t
    cand = (r.get('candidates') or [{}])[0]
    text = ''.join(p.get('text', '') for p in cand.get('content', {}).get('parts', []))
    u = r.get('usageMetadata', {})
    thoughts = u.get('thoughtsTokenCount', 0) or 0       # thinking tokens are billed as output tokens
    return Result(text, 'gemini', model, r.get('modelVersion', model), u.get('promptTokenCount', 0),
                  (u.get('candidatesTokenCount', 0) or 0) + thoughts, latency, cand.get('finishReason', ''),
                  extra={'thoughts_tokens': thoughts, 'temperature': temp,
                         'thinking_budget': payload['generationConfig'].get('thinkingConfig', {}).get('thinkingBudget'),
                         **meta})


OPENAI_REASONING = re.compile(r'^(o\d|gpt-5)')


def reasoning_tokens(usage):
    """Reasoning tokens from an OpenAI-style usage block (OpenAI, OpenRouter), or None when not reported."""
    for v in ((usage.get('completion_tokens_details') or {}).get('reasoning_tokens'), usage.get('reasoning_tokens')):
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return int(v)
    return None


def _openai(model, system, prompt, images, max_tokens, base=None, auth=True, schema=None, provider=None):
    """OpenAI chat completions, or a compatible gateway. `provider` names the gateway in Result.provider and picks its
    key from KEYS (default: 'openai' with auth, 'ollama' without)."""
    provider = provider or ('openai' if auth else 'ollama')
    content = [{'type': 'text', 'text': prompt}]
    content += [{'type': 'image_url', 'image_url': {'url': f'data:{m};base64,{d}'}}
                for m, d in (_image_part(p) for p in images)]
    messages = ([{'role': 'system', 'content': system}] if system else []) + \
               [{'role': 'user', 'content': content if images else prompt}]
    custom = base or os.environ.get('OPENAI_BASE_URL')
    base = (custom or 'https://api.openai.com/v1').rstrip('/')
    t = time.time()
    # OpenAI itself: max_completion_tokens (max_tokens is deprecated there and rejected by reasoning models).
    # Ollama and other OpenAI-compatible gateways keep max_tokens, which they document.
    limit = 'max_tokens' if custom else 'max_completion_tokens'
    payload = {'model': model, 'messages': messages, limit: max_tokens}
    temp = temperature()
    if temp is not None and auth and not custom and OPENAI_REASONING.match(model):
        _note_once(f'HOMODYNE_TEMPERATURE is not sent to {model}: OpenAI reasoning models reject it.')
        temp = None
    if temp is not None:
        payload['temperature'] = temp
    if schema is not None:
        payload['response_format'] = {'type': 'json_schema',
                                      'json_schema': {'name': 'homodyne_output', 'strict': True, 'schema': schema}}
    meta = {}
    if auth and not key(KEYS[provider]):
        raise LLMError(f'{KEYS[provider]} is not set (environment or private/keys.env)')
    r = _post(f'{base}/chat/completions', payload,
              {'Authorization': 'Bearer ' + key(KEYS[provider])} if auth else {}, meta=meta)
    latency = time.time() - t
    choice = (r.get('choices') or [{}])[0]
    u = r.get('usage') or {}
    extra = {'temperature': temp, **meta}
    rt = reasoning_tokens(u)
    if rt is not None:                      # already counted inside completion_tokens
        extra['reasoning_tokens'] = rt
    if provider == 'openrouter':
        if isinstance(u.get('cost'), (int, float)):
            extra['cost_usd'] = u['cost']
        if r.get('provider'):
            extra['upstream_provider'] = r['provider']
    return Result(choice.get('message', {}).get('content') or '', provider, model,
                  r.get('model', model),
                  u.get('prompt_tokens', 0), u.get('completion_tokens', 0), latency,
                  choice.get('finish_reason', ''), extra=extra)


def _accepts_schema(fn):
    try:
        params = inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False
    return 'schema' in params or any(p.kind == p.VAR_KEYWORD for p in params.values())


def ollama_base():
    """OLLAMA_HOST as a client URL: adds http:// when missing and uses 127.0.0.1 for a 0.0.0.0 bind address."""
    host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434').strip().rstrip('/')
    bare = '://' not in host
    scheme, rest = ('http', host) if bare else host.split('://', 1)
    if rest == '0.0.0.0' or rest.startswith(('0.0.0.0:', '0.0.0.0/')):
        rest = '127.0.0.1' + rest[len('0.0.0.0'):]
    hostport, _, path = rest.partition('/')
    if bare and ':' not in hostport:          # "0.0.0.0" or "myhost" alone: Ollama's default port
        hostport += ':11434'
    return f'{scheme}://{hostport}' + (f'/{path}' if path else '')


def _mock(model, system, prompt, images, max_tokens, mock=None, schema=None):
    if mock and schema is not None and _accepts_schema(mock):
        text = mock(prompt, schema=schema)  # a self-test mock may imitate schema-constrained decoding
    elif mock:
        text = mock(prompt)
    else:
        text = '[mock] ' + hashlib.sha256(prompt.encode()).hexdigest()[:12]
    return Result(text, 'mock', model, model, len(prompt.split()), len(text.split()), 0.0, 'end_turn',
                  extra={'mock': True})


# ── public API ─────────────────────────────────────────────────────────────
def call(prompt, system=None, images=(), role='main', max_tokens=16000, cache_dir=None, mock=None, model=None,
         schema=None):
    """Ask the configured model once. Returns a Result. Cached in cache_dir when given.

    `mock` is a function prompt -> text used only when the provider is mock (self-tests); when `schema` is given it
    is called as mock(prompt, schema=schema) if it accepts that.
    `model` overrides the role's model as 'provider:model'.
    `schema` (optional JSON Schema dict) turns on the provider's native structured output (see the module docstring).
    """
    provider, name = model.split(':', 1) if model else resolve(role)
    images = [str(p) for p in images]
    parts = [provider, name, system, prompt, [hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in images],
             max_tokens, os.environ.get('HOMODYNE_EFFORT', 'medium')]
    send = clean_schema(schema) if schema is not None else None
    if send is not None:  # appended only when used, so cache keys of calls without a schema are unchanged
        parts.append({'schema': send})
    if temperature() is not None:  # same rule for the optional sampling settings
        parts.append({'temperature': temperature()})
    if provider == 'gemini' and os.environ.get('HOMODYNE_THINKING_BUDGET'):
        parts.append({'thinking_budget': os.environ['HOMODYNE_THINKING_BUDGET']})
    key = hashlib.sha256(json.dumps(parts, ensure_ascii=False).encode()).hexdigest()
    path = Path(cache_dir) / f'{key}.json' if cache_dir and provider != 'mock' else None
    if path and path.exists():
        d = json.loads(path.read_text(encoding='utf-8'))
        d['cached'] = True
        return Result(**d)
    if provider == 'anthropic':
        res = _anthropic(name, system, prompt, images, max_tokens, schema=send)
    elif provider == 'gemini':
        res = _gemini(name, system, prompt, images, max_tokens, schema=send)
    elif provider == 'openai':
        res = _openai(name, system, prompt, images, max_tokens, schema=send)
    elif provider == 'openrouter':
        res = _openai(name, system, prompt, images, max_tokens, base=OPENROUTER_BASE, schema=send,
                      provider='openrouter')
    elif provider == 'ollama':
        res = _openai(name, system, prompt, images, max_tokens,
                      base=ollama_base() + '/v1', auth=False,
                      schema=send)
    elif provider == 'mock':
        res = _mock(name, system, prompt, images, max_tokens, mock, schema=schema)
    else:
        raise LLMError(f'unknown provider {provider!r}; use anthropic, gemini, openai, openrouter, ollama or mock')
    if schema is not None:
        res.extra['structured_output'] = True
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(res.to_dict(), ensure_ascii=False, indent=1), encoding='utf-8')
    return res


def describe():
    """One line naming the models that will be used, for experiment logs."""
    out = []
    for role in ('main', 'small'):
        try:
            out.append('%s=%s:%s' % ((role,) + resolve(role)))
        except LLMError as e:
            out.append(f'{role}=unset ({e})')
    return ' · '.join(out)


def selftest():
    """No network, no real key: the OpenRouter route, reasoning-token extraction and unchanged cache keys."""
    import tempfile
    global _post
    real_post, saved = _post, {k: os.environ.get(k) for k in
                               ('OPENAI_API_KEY', 'OPENROUTER_API_KEY', 'OPENAI_BASE_URL', 'HOMODYNE_MODEL',
                                'HOMODYNE_TEMPERATURE', 'HOMODYNE_EFFORT', 'HOMODYNE_THINKING_BUDGET',
                                'HOMODYNE_HTTP_TIMEOUT')}
    seen = []

    def fake(url, payload, headers, timeout=180, meta=None):
        seen.append((url, payload, headers))
        usage = {'prompt_tokens': 11, 'completion_tokens': 40, 'completion_tokens_details': {'reasoning_tokens': 31}}
        if 'openrouter' in url:
            usage['cost'] = 0.00042
        return {'choices': [{'message': {'content': '{"choice": 2}'}, 'finish_reason': 'stop'}], 'usage': usage,
                'model': payload['model'] + '-served', **({'provider': 'Example'} if 'openrouter' in url else {})}
    try:
        for k in saved:
            os.environ.pop(k, None)
        os.environ['OPENAI_API_KEY'], os.environ['OPENROUTER_API_KEY'] = 'sk-test-openai-000', 'sk-or-test-000000'
        _post = fake
        r = call('q', system='s', model='openrouter:vendor/model-a', max_tokens=64)
        url, payload, headers = seen[-1]
        assert url == OPENROUTER_BASE + '/chat/completions', url
        assert headers == {'Authorization': 'Bearer sk-or-test-000000'}, 'OpenRouter must use OPENROUTER_API_KEY'
        assert payload['max_tokens'] == 64 and 'max_completion_tokens' not in payload
        assert r.provider == 'openrouter' and r.model_served == 'vendor/model-a-served'
        assert (r.input_tokens, r.output_tokens) == (11, 40)
        assert r.extra['reasoning_tokens'] == 31 and r.extra['cost_usd'] == 0.00042
        assert r.extra['upstream_provider'] == 'Example'
        r = call('q', system='s', model='openai:gpt-x', max_tokens=64)
        url, payload, headers = seen[-1]
        assert url == 'https://api.openai.com/v1/chat/completions' and payload['max_completion_tokens'] == 64
        assert headers == {'Authorization': 'Bearer sk-test-openai-000'} and r.provider == 'openai'
        assert r.extra['reasoning_tokens'] == 31 and 'cost_usd' not in r.extra
        assert reasoning_tokens({}) is None and reasoning_tokens({'reasoning_tokens': 5}) == 5
        assert reasoning_tokens({'completion_tokens_details': {'reasoning_tokens': None}}) is None
        # cache keys of existing calls must not move (hashes recorded with the previous llm.py, 2026-11-27)
        for schema, want in ((None, '23171b2b5e3032b5a286be506027a6f60c34294b3eb044316d362424ffeb3bdd'),
                             ({'type': 'object'}, '7413aa32132bb8ca08563707bb18dcf30c8555836aeeaf7c4cb69e3795777314')):
            with tempfile.TemporaryDirectory() as d:
                call('hi', system='s', model='openai:gpt-x', cache_dir=d, schema=schema, max_tokens=50)
                got = [f[:-5] for f in os.listdir(d)]
                assert got == [want], f'cache key changed: {got}'
                n = len(seen)
                assert call('hi', system='s', model='openai:gpt-x', cache_dir=d, schema=schema, max_tokens=50).cached
                assert len(seen) == n, 'a cached call must not reach the network'
        real_open = urllib.request.urlopen
        urllib.request.urlopen = lambda req, timeout=None: (_ for _ in ()).throw(TimeoutError('timed out'))
        _post = real_post
        try:                                # a read timeout becomes LLMError (urllib does not wrap it)
            call('slow', system='s', model='openai:gpt-x', max_tokens=64)
            raise AssertionError('timeout must raise LLMError')
        except LLMError as e:
            assert 'HOMODYNE_HTTP_TIMEOUT' in str(e)
        finally:
            urllib.request.urlopen, _post = real_open, fake
        assert 'sk-or-test-000000' in secrets()
        try:                                # openrouter is never chosen on its own
            assert resolve()[0] != 'openrouter'
        except LLMError:
            pass
        os.environ.pop('OPENROUTER_API_KEY')
        if not _file_keys().get('OPENROUTER_API_KEY'):
            try:
                call('q', model='openrouter:vendor/model-a')
                raise AssertionError('missing key must raise LLMError')
            except LLMError as e:
                assert 'OPENROUTER_API_KEY' in str(e)
    finally:
        _post = real_post
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    print('llm.py selftest ok (openrouter route, reasoning tokens, cost, cache keys unchanged)')
    return 0


def main():
    if len(sys.argv) >= 2 and sys.argv[1] in ('selftest', '--selftest'):
        return selftest()
    if len(sys.argv) < 2 or sys.argv[1] not in ('check', 'which'):
        print(__doc__)
        return 0
    print(describe())
    if sys.argv[1] == 'which':
        return 0
    r = call('Reply with exactly one word: ready', max_tokens=2000)
    print(json.dumps({k: v for k, v in r.to_dict().items() if k != 'extra'}, ensure_ascii=False))
    return 0 if r.text.strip() else 1


if __name__ == '__main__':
    sys.exit(main())
