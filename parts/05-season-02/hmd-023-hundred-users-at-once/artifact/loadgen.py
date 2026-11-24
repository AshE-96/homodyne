"""loadgen.py — virtual users and a streaming client for HMD-023.

One client works against both targets, because the fake server speaks Ollama's streaming /api/chat:
  * POST /api/chat with stream=true; the response is newline-delimited JSON (chunked).
  * TTFT = time from sending to the first chunk that carries text. E2E = time to the `done` chunk.

Two ways to make load (the "users are not requests per second" lesson):
  * closed loop: N users; each sends, waits for the whole answer, thinks (random, mean `think` s), sends again.
    When the service slows down, users send less often: the load quietly adapts to the service.
  * open loop: requests arrive at a fixed average rate (Poisson), whatever the service is doing.
    Nothing slows the arrivals down, so a queue that starts growing keeps growing.

Only localhost targets are allowed (load only a service you own and run yourself).
Standard library only.
"""
import asyncio
import json
import random
import time

LOCAL = ('127.0.0.1', 'localhost', '::1')

PROMPT_TEMPLATE = 'درخواست شمارهٔ {rid}. {q} حدود صد و پنجاه کلمه جواب بده.'
PROMPTS_FA = [
    'برای یه مهمونی ده‌نفره، یه منوی ساده و ارزون پیشنهاد بده.',
    'فرق حساب جاری و حساب پس‌انداز رو ساده توضیح بده.',
    'چطور برای یه مصاحبهٔ کاری آماده بشم؟ چند نکتهٔ عملی بگو.',
    'یه برنامهٔ ورزشی سبک برای کسی که پشت میز کار می‌کنه بنویس.',
    'چرا آسمون آبیه؟ برای یه بچهٔ ده‌ساله توضیح بده.',
    'یه ایمیل کوتاه و مؤدبانه برای عقب‌انداختن یه جلسه بنویس.',
    'سه راه برای کم کردن مصرف برق خونه در تابستون بگو.',
    'خلاصهٔ داستان رستم و سهراب رو در چند خط بگو.',
    'برای یادگرفتن یه زبان تازه، روزی بیست دقیقه وقت دارم. چه برنامه‌ای بریزم؟',
    'فرق ویروس و باکتری چیه؟ ساده بگو.',
    'یه متن تبریک تولد برای همکارم بنویس.',
    'چطور یه بودجهٔ ماهانهٔ ساده برای خودم بنویسم؟',
    'برای سفر سه‌روزه به شیراز چه جاهایی رو ببینم؟',
    'قانون پایستگی انرژی رو با یه مثال روزمره توضیح بده.',
    'یه پیام کوتاه برای پیگیری سفارشی که دیر رسیده بنویس.',
    'چند نکته برای خواب بهتر در شب‌های امتحان بگو.',
]


class Clock:
    """Service time. timescale k < 1 runs the simulation k times faster; every reading stays in service seconds."""

    def __init__(self, k=1.0):
        self.k = k
        self.t0 = time.monotonic()

    def now(self):
        return (time.monotonic() - self.t0) / self.k

    async def sleep(self, s):
        if s > 0:
            await asyncio.sleep(s * self.k)


class Live:
    """Shared state the dashboard reads while a stage runs."""

    def __init__(self, target, simulated, slo_ttft, timeout):
        self.target, self.simulated, self.slo_ttft, self.timeout = target, simulated, slo_ttft, timeout
        self.stage = ''
        self.load = ''
        self.t_start = 0.0
        self.duration = 0.0
        self.state = {}          # rid -> 'waiting' | 'streaming'
        self.recs = []
        self.samples = []
        self.server = {}
        self.history = []        # (stage label, summary row) of finished stages


def parse_ollama_host(value=None):
    """OLLAMA_HOST as Ollama accepts it ('127.0.0.1:11434', 'http://localhost:11434', '[::1]:11434', 'localhost')
    -> (host, port). The host is checked: anything that is not this computer's loopback is refused."""
    v = (value or 'http://127.0.0.1:11434').strip()
    v = v.split('://', 1)[1] if '://' in v else v
    v = v.split('/', 1)[0]
    if v.startswith('['):                       # [::1]:11434
        host, _, rest = v[1:].partition(']')
        port = rest.lstrip(':') or '11434'
    elif v.count(':') == 1:
        host, port = v.split(':')
    else:
        host, port = v, '11434'
    check_local(host)
    return host, int(port)


def check_local(host):
    if host not in LOCAL:
        raise SystemExit(f'Refusing to load {host}: HMD-023 only loads a service on this computer (127.0.0.1). '
                         'Load testing someone else\'s service needs their written permission.')


async def _read_chunked(reader):
    """Yield decoded lines from a chunked or plain body."""
    buf = b''
    while True:
        size_line = await reader.readline()
        if not size_line:
            break
        size = int(size_line.strip().split(b';')[0] or b'0', 16)
        if size == 0:
            break
        data = await reader.readexactly(size)
        await reader.readexactly(2)
        buf += data
        while b'\n' in buf:
            line, buf = buf.split(b'\n', 1)
            if line.strip():
                yield line
    if buf.strip():
        yield buf


async def _read_plain(reader):
    while True:
        line = await reader.readline()
        if not line:
            break
        if line.strip():
            yield line


async def stream_chat(host, port, payload, clock, live, rid, rec):
    """Send one request, fill `rec` in place. Raises nothing; the caller applies the timeout."""
    reader, writer = await asyncio.open_connection(host, port)
    try:
        body = json.dumps(payload, ensure_ascii=False).encode()
        writer.write(f'POST /api/chat HTTP/1.1\r\nHost: {host}:{port}\r\nContent-Type: application/json\r\n'
                     f'Content-Length: {len(body)}\r\nConnection: close\r\n\r\n'.encode() + body)
        await writer.drain()
        head = (await reader.readuntil(b'\r\n\r\n')).decode('latin-1')
        code = int(head.split(' ', 2)[1])
        rec['code'] = code
        if code != 200:
            rec['status'] = 'rejected' if code in (429, 503) else 'error'
            rec['t_end'] = clock.now()
            return
        lines = _read_chunked(reader) if 'chunked' in head.lower() else _read_plain(reader)
        n_chunks = 0
        async for line in lines:
            msg = json.loads(line)
            if msg.get('error'):
                rec['status'] = 'error'
                rec['detail'] = str(msg['error'])[:120]
                rec['t_end'] = clock.now()
                return
            if (msg.get('message') or {}).get('thinking') and rec.get('t_first_any') is None:
                rec['t_first_any'] = clock.now()     # a thinking model's hidden text; not the first visible word
            text = (msg.get('message') or {}).get('content') or ''
            if text and rec['t_first'] is None:
                rec['t_first'] = clock.now()
                live.state[rid] = 'streaming'
            if text:
                n_chunks += 1
            if msg.get('done'):
                rec['t_end'] = clock.now()
                rec['status'] = 'ok'
                rec['out_tokens'] = msg.get('eval_count') or n_chunks
                rec['in_tokens'] = msg.get('prompt_eval_count') or rec.get('in_tokens')
                rec['load_s'] = (msg.get('load_duration') or 0) / 1e9
                rec['degraded'] = bool((msg.get('homodyne') or {}).get('degraded'))
                return
        rec['status'] = 'error'
        rec['detail'] = 'stream ended without done'
        rec['t_end'] = clock.now()
    finally:
        writer.close()


async def one_request(cfg, clock, live, rid, user, stage, rng):
    if cfg['simulated']:
        n_in, n_out = rng.randint(*cfg['in_range']), rng.randint(*cfg['out_range'])
        payload = {'model': 'fake', 'stream': True,
                   'messages': [{'role': 'user', 'content': 'x' * (4 * n_in)}],
                   'options': {'num_predict': n_out, 'homodyne_input_tokens': n_in}}
    else:
        n_in, n_out = None, cfg['max_tokens']
        q = PROMPTS_FA[rid % len(PROMPTS_FA)]
        # the request number goes first, so no two prompts share a prefix the server could reuse from cache
        payload = {'model': cfg['model'], 'stream': True, 'keep_alive': '30m',
                   'messages': [{'role': 'user', 'content': PROMPT_TEMPLATE.format(rid=rid, q=q)}],
                   'options': {'num_predict': n_out}}
        if cfg.get('no_think'):
            payload['think'] = False      # thinking models (e.g. qwen3.5): answer directly, so TTFT means a visible word
    rec = {'rid': rid, 'stage': stage, 'user': user, 't_send': clock.now(), 't_first': None, 't_end': None,
           'status': None, 'code': None, 'in_tokens': n_in, 'out_tokens': None, 'planned_out': n_out,
           'degraded': False, 'load_s': 0.0}
    live.state[rid] = 'waiting'
    live.recs.append(rec)
    try:
        await asyncio.wait_for(stream_chat(cfg['host'], cfg['port'], payload, clock, live, rid, rec),
                               timeout=cfg['timeout'] * clock.k)
    except asyncio.TimeoutError:
        rec['status'] = 'timeout'
        rec['t_end'] = clock.now()
    except (OSError, asyncio.IncompleteReadError, ValueError) as e:
        rec['status'] = 'error'
        rec['detail'] = type(e).__name__
        rec['t_end'] = clock.now()
    finally:
        live.state.pop(rid, None)
    return rec


async def fetch_metrics(host, port):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), 1.0)
        writer.write(f'GET /metrics HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'.encode())
        await writer.drain()
        raw = await asyncio.wait_for(reader.read(), 1.0)
        writer.close()
        return json.loads(raw.split(b'\r\n\r\n', 1)[1])
    except Exception:
        return {}


async def sampler(cfg, clock, live, stop):
    period = cfg.get('sample_every', 0.5)
    while not stop.is_set():
        waiting = sum(1 for s in list(live.state.values()) if s == 'waiting')
        streaming = len(live.state) - waiting
        s = {'t': clock.now() - live.t_start, 'waiting': waiting, 'streaming': streaming,
             'in_flight': waiting + streaming}
        if cfg['simulated']:
            m = await fetch_metrics(cfg['host'], cfg['port'])
            live.server = m
            s['server_queue'] = m.get('queue')
            s['server_active'] = m.get('active')
        live.samples.append(s)
        await clock.sleep(period)


async def run_stage(cfg, clock, live, stage, users=None, rate=None, seed=0):
    """Closed loop with `users`, or open loop at `rate` requests/s. Returns (records, samples, window)."""
    arr = random.Random(seed)              # arrivals, ramp and think times
    rng = random.Random(seed + 7919)       # request lengths: a separate stream, so the same seed gives the
                                           # same arrival pattern at every rate (common random numbers)
    live.stage, live.recs, live.samples = stage, [], []
    live.load = f'closed loop, think ~{cfg["think"]:.0f}s' if users else 'open loop, Poisson arrivals'
    live.t_start, live.duration = clock.now(), cfg['duration']
    counter = {'n': 0}
    base = cfg.setdefault('_rid', 0)

    def next_rid():
        counter['n'] += 1
        return base + counter['n']

    async def user_loop(u):
        await clock.sleep(arr.uniform(0, cfg['ramp']))
        while clock.now() - live.t_start < cfg['duration']:
            await one_request(cfg, clock, live, next_rid(), u, stage, rng)
            pause = arr.expovariate(1 / cfg['think'])
            if clock.now() - live.t_start + pause >= cfg['duration']:
                break                     # no new request would start in this stage: don't idle through the tail
            await clock.sleep(pause)

    async def open_loop():
        tasks, t = [], 0.0
        while True:
            t += arr.expovariate(1.0) / rate
            if t >= cfg['duration']:
                break
            await clock.sleep(live.t_start + t - clock.now())
            tasks.append(asyncio.ensure_future(one_request(cfg, clock, live, next_rid(), None, stage, rng)))
        await asyncio.gather(*tasks)

    stop = asyncio.Event()
    samp = asyncio.ensure_future(sampler(cfg, clock, live, stop))
    if users:
        await asyncio.gather(*(user_loop(u) for u in range(users)))
    else:
        await open_loop()
    window = clock.now() - live.t_start
    stop.set()
    await samp
    cfg['_rid'] = base + counter['n']
    return list(live.recs), list(live.samples), window
