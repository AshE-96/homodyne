"""HMD-024 · a small Ollama client (standard library; psutil optional) with streaming timing and memory sampling.

Uses Ollama's native API (docs.ollama.com/api): POST /api/chat with stream=true (NDJSON chunks; the last one has
done=true plus total_duration, load_duration, prompt_eval_count, prompt_eval_duration, eval_count, eval_duration,
all durations in nanoseconds), POST /api/show, GET /api/tags, /api/ps, /api/version.

Timing we take ourselves (wall clock, this process):
  ttft_s        request sent → first chunk with non-empty message.content   ("time to first token")
  first_any_s   request sent → first chunk with content OR thinking text
  total_s       request sent → final chunk
Tokens per second comes from Ollama's own counters: eval_count / eval_duration.

Memory: a background thread samples the resident memory (RSS) of the Ollama runner process every 0.1 s. On Apple
silicon the GPU shares RAM with the CPU, and memory Ollama hands to Metal may not all show up as RSS of the runner.
So we also record what Ollama itself reports for the loaded model (/api/ps: size, size_vram), the lowest free
system memory and the highest swap use during the task. Report those as three separate numbers.
"""
import json
import os
import subprocess
import threading
import time
import urllib.error
import urllib.request

try:
    import psutil
except ImportError:  # memory falls back to `ps`
    psutil = None


def host():
    h = os.environ.get('OLLAMA_HOST', '127.0.0.1:11434').strip().rstrip('/')
    if not h.startswith(('http://', 'https://')):
        h = 'http://' + h
    if h.count(':') == 1:
        h += ':11434'
    return h.replace('0.0.0.0', '127.0.0.1')


class OllamaError(RuntimeError):
    pass


def _req(path, payload=None, timeout=10, base=None):
    url = (base or host()) + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise OllamaError(f'HTTP {e.code} on {path}: {e.read().decode("utf-8", "replace")[:300]}') from None
    except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
        raise OllamaError(f'cannot reach Ollama at {url}: {getattr(e, "reason", e)}') from None


def version(base=None):
    return _req('/api/version', base=base).get('version')


def tags(base=None):
    return _req('/api/tags', base=base).get('models', [])


def show(model, base=None):
    return _req('/api/show', {'model': model}, timeout=30, base=base)


def ps(base=None):
    return _req('/api/ps', base=base).get('models', [])


def unload(model, base=None):
    """Ask Ollama to drop a model from memory now (keep_alive 0), so the next model starts clean."""
    try:
        _req('/api/generate', {'model': model, 'keep_alive': 0}, timeout=30, base=base)
        return True
    except OllamaError:
        return False


# ── memory sampler ────────────────────────────────────────────────────────────────────────────
def _runner_rss_ps():
    """Fallback without psutil: sum RSS (bytes) of processes whose command mentions ollama and runner."""
    try:
        out = subprocess.run(['ps', '-axo', 'rss=,command='], capture_output=True, text=True, timeout=5).stdout
    except Exception:
        return 0, 'ps-failed'
    rows = [l.strip().split(None, 1) for l in out.splitlines() if 'ollama' in l.lower()]
    run = [int(r[0]) * 1024 for r in rows if len(r) == 2 and 'runner' in r[1] and 'grep' not in r[1]]
    return sum(run), 'ps:runner'


class MemorySampler:
    """Peak runner RSS, lowest available system memory and highest swap, sampled while a task runs."""

    def __init__(self, interval=0.1, match=None):
        self.interval = interval
        self.match = match  # self-test: only processes whose command line contains this string
        self.source = 'psutil:runner' if psutil else 'ps:runner'
        self._stop = threading.Event()
        self._procs = []
        self._last_scan = 0

    def _scan(self):
        procs, fallback = [], []
        for p in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = ' '.join(p.info['cmdline'] or []).lower()
                name = (p.info['name'] or '').lower()
            except (psutil.Error, TypeError):
                continue
            if self.match:
                if self.match in cmd:
                    procs.append(p)
                continue
            if 'ollama' in name or 'ollama' in cmd:
                if 'runner' in cmd:
                    procs.append(p)
                elif 'serve' in cmd or name == 'ollama':
                    fallback.append(p)
        self.source = 'psutil:runner' if procs else ('psutil:ollama-serve' if fallback else 'psutil:none')
        self._procs = procs or fallback

    def _rss(self):
        if not psutil:
            rss, self.source = _runner_rss_ps()
            return rss
        if time.time() - self._last_scan > 2 or not self._procs:
            self._scan()
            self._last_scan = time.time()
        total = 0
        for p in list(self._procs):
            try:
                total += p.memory_info().rss
            except psutil.Error:
                self._procs.remove(p)
        return total

    def _loop(self):
        while not self._stop.is_set():
            self.sample()
            self._stop.wait(self.interval)

    def sample(self):
        rss = self._rss()
        self.peak_rss = max(self.peak_rss, rss)
        if psutil:
            vm, sw = psutil.virtual_memory(), psutil.swap_memory()
            self.min_avail = min(self.min_avail, vm.available)
            self.max_swap = max(self.max_swap, sw.used)

    def __enter__(self):
        self.peak_rss, self.min_avail, self.max_swap = 0, float('inf'), 0
        self.sample()
        self._t = threading.Thread(target=self._loop, daemon=True)
        self._t.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._t.join(timeout=2)
        self.sample()
        if self.min_avail == float('inf'):
            self.min_avail = None

    def result(self):
        return {'peak_runner_rss_bytes': self.peak_rss, 'min_available_bytes': self.min_avail,
                'max_swap_used_bytes': self.max_swap if psutil else None, 'mem_source': self.source}


# ── streaming chat ────────────────────────────────────────────────────────────────────────────
def chat_stream(model, system, prompt, options, think=None, keep_alive='10m', base=None, timeout=600,
                sampler_interval=0.1, mem_match=None):
    """One streamed chat call. Returns a dict with the text, timings, Ollama counters and memory."""
    payload = {'model': model, 'stream': True, 'keep_alive': keep_alive, 'options': options,
               'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt}]}
    if think is not None:
        payload['think'] = think
    req = urllib.request.Request((base or host()) + '/api/chat', data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'})
    text, thinking, final = [], [], {}
    ttft = first_any = None
    with MemorySampler(sampler_interval, mem_match) as mem:
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                for raw in r:
                    if not raw.strip():
                        continue
                    chunk = json.loads(raw.decode('utf-8'))
                    if chunk.get('error'):
                        raise OllamaError(chunk['error'])
                    msg = chunk.get('message') or {}
                    now = time.perf_counter() - t0
                    if msg.get('thinking'):
                        thinking.append(msg['thinking'])
                        first_any = first_any if first_any is not None else now
                    if msg.get('content'):
                        text.append(msg['content'])
                        ttft = ttft if ttft is not None else now
                        first_any = first_any if first_any is not None else now
                    if chunk.get('done'):
                        final = chunk
                        break
        except urllib.error.HTTPError as e:
            raise OllamaError(f'HTTP {e.code}: {e.read().decode("utf-8", "replace")[:300]}') from None
        except urllib.error.URLError as e:
            raise OllamaError(f'cannot reach Ollama: {e.reason}') from None
        total = time.perf_counter() - t0
    try:
        loaded = [m for m in ps(base) if m.get('name') == model or m.get('model') == model]
    except OllamaError:
        loaded = []
    ec, ed = final.get('eval_count'), final.get('eval_duration')
    out = {
        'text': ''.join(text), 'thinking_chars': len(''.join(thinking)),
        'ttft_s': ttft, 'first_any_s': first_any, 'total_s': total,
        'eval_count': ec, 'eval_duration_s': ed / 1e9 if ed else None,
        'tokens_per_s': (ec / (ed / 1e9)) if ec and ed else None,
        'prompt_eval_count': final.get('prompt_eval_count'),
        'prompt_eval_duration_s': (final.get('prompt_eval_duration') or 0) / 1e9 or None,
        'load_duration_s': (final.get('load_duration') or 0) / 1e9,
        'ollama_total_duration_s': (final.get('total_duration') or 0) / 1e9 or None,
        'done_reason': final.get('done_reason'),
        'ps_size_bytes': loaded[0].get('size') if loaded else None,
        'ps_size_vram_bytes': loaded[0].get('size_vram') if loaded else None,
        'ps_context_length': loaded[0].get('context_length') if loaded else None,
    }
    out['possibly_truncated'] = bool(out['prompt_eval_count'] and options.get('num_ctx')
                                     and out['prompt_eval_count'] >= 0.98 * options['num_ctx'])
    out.update(mem.result())
    return out
