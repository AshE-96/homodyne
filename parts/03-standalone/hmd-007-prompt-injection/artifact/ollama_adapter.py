#!/usr/bin/env python3
"""HMD-007 [RUN] path: let injection_lab.py drive a model running on THIS computer through Ollama.

Free and offline: the only connection is to Ollama on the loopback address. Any OLLAMA_HOST that is
not localhost / 127.0.0.1 / ::1 is refused, so the fictional cases never leave the machine and no
paid API can be reached by mistake. The illustrative stand-ins stay the default of injection_lab.py.

    ollama pull llama3.2:3b                      # once, outside this script
    export HMD007_OLLAMA_MODEL=llama3.2:3b       # required; there is no default model
    python3 injection_lab.py --model ollama_adapter:model \
        --out results-ollama-llama3.2-3b-<date>.md --json results-ollama-llama3.2-3b-<date>.json
    python3 injection_lab.py --model ollama_adapter:model --trace A01   # the on-camera trace

    python3 ollama_adapter.py --selftest         # offline; never opens a connection

Optional: HMD007_TEMPERATURE (default 0), HMD007_TIMEOUT seconds (default 180).
Record for the video: `ollama --version`, `ollama show <model>` (exact digest), date, temperature, full JSON.
Small local models are weak at following the JSON protocol: count `errors` and empty answers before
reading any rate. Standard library only.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

LOOPBACK = {'localhost', '127.0.0.1', '::1'}


def ollama_url(host=None):
    """OLLAMA_HOST -> base URL on loopback, or ValueError. '0.0.0.0' (a bind address) means this machine."""
    raw = (host if host is not None else os.environ.get('OLLAMA_HOST', '')).strip() or 'http://127.0.0.1:11434'
    if '://' not in raw:
        raw = 'http://' + raw
    u = urllib.parse.urlsplit(raw)
    name = (u.hostname or '').lower()
    if name == '0.0.0.0':
        name = '127.0.0.1'
    if name not in LOOPBACK:
        raise ValueError(f'refusing non-loopback OLLAMA_HOST {raw!r}: this lab only talks to a model on this computer')
    if u.scheme != 'http':
        raise ValueError(f'unexpected scheme in OLLAMA_HOST {raw!r}; use http://127.0.0.1:11434')
    netloc = f'[{name}]' if ':' in name else name
    return f'http://{netloc}:{u.port or 11434}'


def to_ollama(messages):
    """Ollama has no 'tool' role for this text protocol: tool results go back as a user turn."""
    return [m if m['role'] != 'tool' else {'role': 'user', 'content': f"TOOL RESULT ({m.get('name')}): {m['content']}"}
            for m in messages]


def parse(text):
    """Model text -> harness dict. Non-JSON text is kept as a plain answer with no tool calls."""
    start, end = text.find('{'), text.rfind('}')
    try:
        out = json.loads(text[start:end + 1]) if start != -1 else None
    except ValueError:
        out = None
    if not isinstance(out, dict):
        return {'answer': text.strip(), 'tool_calls': []}
    calls = out.get('tool_calls') or []
    calls = [c for c in calls if isinstance(c, dict) and isinstance(c.get('name'), str)] if isinstance(calls, list) else []
    return {'answer': str(out.get('answer', '')), 'tool_calls': calls}


def _post(url, payload, timeout):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def model(messages, tools, post=_post):
    name = os.environ.get('HMD007_OLLAMA_MODEL', '').strip()
    if not name:
        raise RuntimeError('set HMD007_OLLAMA_MODEL to a model you have pulled with Ollama (e.g. llama3.2:3b)')
    payload = {'model': name, 'messages': to_ollama(messages), 'stream': False, 'format': 'json',
               'options': {'temperature': float(os.environ.get('HMD007_TEMPERATURE', '0'))}}
    reply = post(ollama_url() + '/api/chat', payload, float(os.environ.get('HMD007_TIMEOUT', '180')))
    return parse((reply.get('message') or {}).get('content') or '')


def selftest():
    for ok, want in [(None, 'http://127.0.0.1:11434'), ('', 'http://127.0.0.1:11434'),
                     ('localhost:11500', 'http://localhost:11500'), ('0.0.0.0:11434', 'http://127.0.0.1:11434'),
                     ('http://[::1]:11434', 'http://[::1]:11434')]:
        saved = os.environ.pop('OLLAMA_HOST', None)
        try:
            got = ollama_url(ok)
        finally:
            if saved is not None:
                os.environ['OLLAMA_HOST'] = saved
        assert got == want, (ok, got)
    for bad in ['http://192.168.1.5:11434', 'example.com', 'https://api.example.invalid', 'http://127.0.0.1.example.com',
                'https://127.0.0.1:11434']:
        try:
            ollama_url(bad)
        except ValueError:
            continue
        raise AssertionError(f'should refuse {bad}')
    assert parse('{"answer": "Total: 4,800 USD", "tool_calls": []}') == {'answer': 'Total: 4,800 USD', 'tool_calls': []}
    assert parse('Sure! {"answer": "x", "tool_calls": [{"name": "send_email", "args": {}}, "junk"]}')['tool_calls'] == \
        [{'name': 'send_email', 'args': {}}]
    assert parse('no json here') == {'answer': 'no json here', 'tool_calls': []}
    assert parse('[1, 2]')['tool_calls'] == []
    assert to_ollama([{'role': 'tool', 'name': 'read_file', 'content': 'C'}]) == \
        [{'role': 'user', 'content': 'TOOL RESULT (read_file): C'}]
    seen = {}

    def fake_post(url, payload, timeout):
        seen.update(url=url, payload=payload)
        return {'message': {'content': '{"answer": "ok", "tool_calls": []}'}}

    old = {k: os.environ.pop(k, None) for k in ('HMD007_OLLAMA_MODEL', 'OLLAMA_HOST')}
    try:
        try:
            model([], [], post=fake_post)
        except RuntimeError:
            pass
        else:
            raise AssertionError('a missing model name must fail')
        os.environ['HMD007_OLLAMA_MODEL'] = 'toy:1b'
        assert model([{'role': 'user', 'content': 'hi'}], [], post=fake_post) == {'answer': 'ok', 'tool_calls': []}
        assert seen['url'] == 'http://127.0.0.1:11434/api/chat' and seen['payload']['format'] == 'json'
        os.environ['OLLAMA_HOST'] = 'http://10.0.0.2:11434'
        try:
            model([], [], post=fake_post)
        except ValueError:
            pass
        else:
            raise AssertionError('non-loopback host must be refused before any request')
    finally:
        for k, v in old.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v
    print('selftest ok')


if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']:
        selftest()
    else:
        print(__doc__)
