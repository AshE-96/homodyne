"""HMD-024 · DEMO stand-ins for the self-test. NOT a model and NOT a result.

- demo_answer(task, profile): writes a reply straight from the answer key, with deliberate mistakes on a fixed
  list of tasks, so every branch of the graders and the report runs (right, wrong, invented, bad JSON, wrong label…).
- A fake Ollama server (python3 demo.py serve --port N) bound to 127.0.0.1 only. It speaks the same /api/chat
  NDJSON stream as Ollama, plus /api/version, /api/tags, /api/show and /api/ps, and holds a little memory so the
  memory sampler has something to measure. Its command line contains "ollama-fake runner", which is what the
  sampler looks for.
"""
import hashlib
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from task_bank import NOT_IN_TEXT, SYSTEM, TASKS

BY_PROMPT = {t['prompt']: t for t in TASKS}

# which task ids each demo profile gets wrong (chosen to exercise branches, not to look like any real model)
WRONG = {
    'demo-small:q4': {'sum-3', 'ext-2', 'qa-3', 'tr-4', 'cls-3', 'nogo-1', 'nogo-2', 'nogo-5', 'sum-5', 'ext-5', 'qa-5'},
    'demo-big:q4': {'ext-2', 'nogo-2', 'nogo-5', 'tr-1', 'qa-3'},
    'mock:echo': {'nogo-5'},
}
SPOKEN = {'demo-small:q4': 'مدل نمایشی کوچیک', 'demo-big:q4': 'مدل نمایشی بزرگ'}
FAKE_MODELS = {'demo-small:q4': dict(size=1_300_000_000, params='1.9B', tps=60, load=0.25),
               'demo-big:q4': dict(size=3_100_000_000, params='4.2B', tps=25, load=0.4)}


def demo_answer(task, profile):
    wrong = task['id'] in WRONG.get(profile, set())
    g = task['grader']
    if g == 'points':
        pts = [' '.join(group[0] for group in kp) for kp in task['keypoints']]
        if wrong:
            pts = pts[:-1]
        return '\n'.join('- ' + p for p in pts)
    if g == 'fields':
        d = {}
        for k, (kind, want) in task['fields'].items():
            d[k] = want[0] if isinstance(want, list) else want
        if wrong:
            k = list(d)[-2]
            d[k] = '30 میلیون' if isinstance(d[k], (int, float)) else 'نامشخص'
        return json.dumps(d, ensure_ascii=False)
    if g == 'short':
        return NOT_IN_TEXT if wrong else task['accept'][0]
    if g == 'absent':
        return '۵۰ هزار تومان' if wrong else NOT_IN_TEXT
    if g == 'terms':
        groups = task['terms'][:-1] if wrong else task['terms']
        words = ' '.join(group[0] for group in groups)
        return ('ترجمه: ' + words) if task['direction'] == 'en→fa' else ('Translation: ' + words)
    if g == 'label':
        return [l for l in task['labels'] if l != task['answer']][0] if wrong else task['answer']
    if g == 'final':
        return 'Step 1 … step 2 …\nANSWER: ' + ('12' if wrong else task['accept'][0])
    raise ValueError(g)


def mock_online(prompt):
    """llm.call(mock=…) hook: the mock 'online model' answers from the key with one deliberate miss."""
    t = BY_PROMPT.get(prompt)
    return demo_answer(t, 'mock:echo') if t else '[mock] unknown prompt'


# ── fake Ollama server ───────────────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    loaded = {}
    ballast = []

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/api/version':
            return self._json({'version': '0.0.0-demo'})
        if self.path == '/api/tags':
            return self._json({'models': [{'name': m, 'model': m, 'size': v['size'],
                                           'digest': hashlib.sha256(m.encode()).hexdigest(),
                                           'details': {'format': 'gguf', 'family': 'demo', 'parameter_size': v['params'],
                                                       'quantization_level': 'Q4_K_M'}} for m, v in FAKE_MODELS.items()]})
        if self.path == '/api/ps':
            return self._json({'models': [{'name': m, 'model': m, 'size': int(FAKE_MODELS[m]['size'] * 1.15),
                                           'size_vram': int(FAKE_MODELS[m]['size'] * 1.15), 'context_length': 8192}
                                          for m in self.loaded]})
        self._json({'error': 'not found'}, 404)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
        if self.path == '/api/show':
            m = body.get('model')
            if m not in FAKE_MODELS:
                return self._json({'error': f"model '{m}' not found"}, 404)
            v = FAKE_MODELS[m]
            return self._json({'details': {'format': 'gguf', 'family': 'demo', 'parameter_size': v['params'],
                                           'quantization_level': 'Q4_K_M'},
                               'capabilities': ['completion', 'thinking'] if 'small' in m else ['completion'],
                               'license': 'DEMO — not a model', 'modified_at': '2026-11-23T00:00:00Z',
                               'model_info': {'general.parameter_count': 1}})
        if self.path != '/api/chat':
            return self._json({'error': 'not found'}, 404)
        m = body.get('model')
        if m not in FAKE_MODELS:
            return self._json({'error': f"model '{m}' not found, try pulling it first"}, 404)
        v = FAKE_MODELS[m]
        load = 0.0
        if m not in self.loaded:
            load = v['load']
            time.sleep(load)
            Handler.ballast.append(bytearray(40_000_000 if 'small' in m else 80_000_000))  # some real RSS
            self.loaded[m] = True
        prompt = body['messages'][-1]['content']
        t = BY_PROMPT.get(prompt)
        text = demo_answer(t, m) if t else 'ok'
        pieces = [text[i:i + 6] for i in range(0, len(text), 6)] or ['']
        self.send_response(200)
        self.send_header('Content-Type', 'application/x-ndjson')
        self.end_headers()
        start = time.perf_counter()
        prompt_s = len(prompt) / 40000
        time.sleep(prompt_s)
        if body.get('think') is None and 'small' in m:
            self.wfile.write((json.dumps({'model': m, 'message': {'role': 'assistant', 'content': '', 'thinking': 'hmm'},
                                          'done': False}) + '\n').encode())
        for p in pieces:
            time.sleep(1 / v['tps'])
            self.wfile.write((json.dumps({'model': m, 'message': {'role': 'assistant', 'content': p}, 'done': False})
                              + '\n').encode())
            self.wfile.flush()
        gen = time.perf_counter() - start - prompt_s
        n_out = len(pieces)
        final = {'model': m, 'message': {'role': 'assistant', 'content': ''}, 'done': True, 'done_reason': 'stop',
                 'total_duration': int((time.perf_counter() - start + load) * 1e9), 'load_duration': int(load * 1e9),
                 'prompt_eval_count': len(prompt) // 3, 'prompt_eval_duration': int(prompt_s * 1e9),
                 'eval_count': n_out, 'eval_duration': int(gen * 1e9)}
        self.wfile.write((json.dumps(final) + '\n').encode())


def serve(port):
    srv = ThreadingHTTPServer(('127.0.0.1', port), Handler)  # loopback only
    print(f'ollama-fake listening on 127.0.0.1:{srv.server_address[1]}', flush=True)
    srv.serve_forever()


if __name__ == '__main__':
    # argv: demo.py serve --port N ollama-fake runner
    if len(sys.argv) >= 2 and sys.argv[1] == 'serve':
        serve(int(sys.argv[sys.argv.index('--port') + 1]) if '--port' in sys.argv else 0)
    else:
        print(__doc__)
        _ = SYSTEM
