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

    python3 tools/llm.py check        # one tiny call: provider, model, latency, tokens

Safer than export: put the same KEY=value line in private/keys.env (git-ignored). The key is then read
by this module only and never enters any process environment, so code an experiment runs can't see it.

Optional:
    HOMODYNE_MODEL=provider:model         main model   (e.g. anthropic:claude-opus-5-5, gemini:gemini-2.5-pro)
    HOMODYNE_MODEL_SMALL=provider:model   the cheaper model in two-model experiments
    HOMODYNE_EFFORT=low|medium|high       Claude effort (default medium)
    HOMODYNE_NO_FALLBACK=1                Claude: turn off server-side refusal fallback (see below)
    HOMODYNE_MODEL=mock:echo              no key, no network: deterministic fake answers for self-tests

Every answer is cached on disk (keyed by provider, model, prompt and settings), so re-running an
experiment costs nothing and gives the same numbers. Delete the cache folder to re-ask.

Claude refusals: on Claude Opus/Sonnet/Fable models the request asks the API to re-run a declined
request on a fallback model (`fallbacks: "default"`). That keeps an experiment from stalling, but a
different model then wrote that answer, so every result records `model_served` and `fell_back`, and
experiments report how many rows fell back. Set HOMODYNE_NO_FALLBACK=1 to record refusals instead.
"""

import base64
import hashlib
import json
import mimetypes
import os
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
KEYS = {'anthropic': 'ANTHROPIC_API_KEY', 'gemini': 'GEMINI_API_KEY', 'openai': 'OPENAI_API_KEY'}
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
    for provider in ('anthropic', 'gemini', 'openai'):
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


def _post(url, payload, headers, timeout=180):
    body = json.dumps(payload).encode('utf-8')
    for attempt in range(5):
        req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json', **headers})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            detail = e.read().decode('utf-8', 'replace')[:500]
            if e.code in (408, 409, 429) or e.code >= 500:
                time.sleep(min(60, 2 ** attempt * 3))
                continue
            raise LLMError(f'HTTP {e.code}: {detail}') from None
        except urllib.error.URLError as e:
            if attempt == 4:
                raise LLMError(f'network error: {e.reason}') from None
            time.sleep(2 ** attempt * 3)
    raise LLMError('gave up after 5 attempts (rate limit or server error)')


# ── providers ──────────────────────────────────────────────────────────────
def _anthropic(model, system, prompt, images, max_tokens):
    try:
        import anthropic
    except ImportError:
        raise LLMError('Claude needs the official SDK: pip install anthropic') from None
    client = anthropic.Anthropic(api_key=key('ANTHROPIC_API_KEY'))
    content = [{'type': 'image', 'source': {'type': 'base64', 'media_type': m, 'data': d}}
               for m, d in (_image_part(p) for p in images)]
    content.append({'type': 'text', 'text': prompt})
    kwargs = dict(model=model, max_tokens=max_tokens, messages=[{'role': 'user', 'content': content}])
    if system:
        kwargs['system'] = system
    effort = os.environ.get('HOMODYNE_EFFORT', 'medium')
    if not model.startswith('claude-haiku-4'):
        kwargs['output_config'] = {'effort': effort}
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
                  extra={'refusal_category': getattr(getattr(r, 'stop_details', None), 'category', None)})


def _gemini(model, system, prompt, images, max_tokens):
    parts = [{'inline_data': {'mime_type': m, 'data': d}} for m, d in (_image_part(p) for p in images)]
    parts.append({'text': prompt})
    payload = {'contents': [{'role': 'user', 'parts': parts}], 'generationConfig': {'maxOutputTokens': max_tokens}}
    if system:
        payload['systemInstruction'] = {'parts': [{'text': system}]}
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    t = time.time()
    r = _post(url, payload, {'x-goog-api-key': key('GEMINI_API_KEY')})
    latency = time.time() - t
    cand = (r.get('candidates') or [{}])[0]
    text = ''.join(p.get('text', '') for p in cand.get('content', {}).get('parts', []))
    u = r.get('usageMetadata', {})
    return Result(text, 'gemini', model, r.get('modelVersion', model), u.get('promptTokenCount', 0),
                  u.get('candidatesTokenCount', 0), latency, cand.get('finishReason', ''))


def _openai(model, system, prompt, images, max_tokens):
    content = [{'type': 'text', 'text': prompt}]
    content += [{'type': 'image_url', 'image_url': {'url': f'data:{m};base64,{d}'}}
                for m, d in (_image_part(p) for p in images)]
    messages = ([{'role': 'system', 'content': system}] if system else []) + \
               [{'role': 'user', 'content': content if images else prompt}]
    base = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
    t = time.time()
    r = _post(f'{base}/chat/completions', {'model': model, 'messages': messages, 'max_tokens': max_tokens},
              {'Authorization': 'Bearer ' + key('OPENAI_API_KEY')})
    latency = time.time() - t
    choice = (r.get('choices') or [{}])[0]
    u = r.get('usage', {})
    return Result(choice.get('message', {}).get('content') or '', 'openai', model, r.get('model', model),
                  u.get('prompt_tokens', 0), u.get('completion_tokens', 0), latency,
                  choice.get('finish_reason', ''))


def _mock(model, system, prompt, images, max_tokens, mock=None):
    if mock:
        text = mock(prompt)
    else:
        text = '[mock] ' + hashlib.sha256(prompt.encode()).hexdigest()[:12]
    return Result(text, 'mock', model, model, len(prompt.split()), len(text.split()), 0.0, 'end_turn',
                  extra={'mock': True})


# ── public API ─────────────────────────────────────────────────────────────
def call(prompt, system=None, images=(), role='main', max_tokens=16000, cache_dir=None, mock=None, model=None):
    """Ask the configured model once. Returns a Result. Cached in cache_dir when given.

    `mock` is a function prompt -> text used only when the provider is mock (self-tests).
    `model` overrides the role's model as 'provider:model'.
    """
    provider, name = model.split(':', 1) if model else resolve(role)
    images = [str(p) for p in images]
    key = hashlib.sha256(json.dumps([provider, name, system, prompt,
                                     [hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in images],
                                     max_tokens, os.environ.get('HOMODYNE_EFFORT', 'medium')],
                                    ensure_ascii=False).encode()).hexdigest()
    path = Path(cache_dir) / f'{key}.json' if cache_dir and provider != 'mock' else None
    if path and path.exists():
        d = json.loads(path.read_text(encoding='utf-8'))
        d['cached'] = True
        return Result(**d)
    if provider == 'anthropic':
        res = _anthropic(name, system, prompt, images, max_tokens)
    elif provider == 'gemini':
        res = _gemini(name, system, prompt, images, max_tokens)
    elif provider == 'openai':
        res = _openai(name, system, prompt, images, max_tokens)
    elif provider == 'mock':
        res = _mock(name, system, prompt, images, max_tokens, mock)
    else:
        raise LLMError(f'unknown provider {provider!r}; use anthropic, gemini, openai or mock')
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


def main():
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
