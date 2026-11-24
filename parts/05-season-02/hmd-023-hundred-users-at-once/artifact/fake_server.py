#!/usr/bin/env python3
"""fake_server.py — a SIMULATED LLM service for HMD-023 (no model, no network beyond 127.0.0.1).

It speaks the same streaming protocol as Ollama's POST /api/chat (newline-delimited JSON, chunked),
so one load generator can measure both this fake and a real Ollama on the owner's laptop.

What it simulates (every number is a parameter we chose, so results are ILLUSTRATIVE):
  * N "GPU slots" (like bank tellers). A request holds one slot from prefill to its last token.
  * A FIFO queue in front of the slots. --max-queue bounds it; when full, the server answers 503
    at once ("busy, try again"), like Ollama does when OLLAMA_MAX_QUEUE is exceeded.
  * Prefill: input tokens are read at --prefill-tps before the first output token.
  * Decode: each slot streams tokens at --decode-tps, slowed by --contention for every other busy
    slot (sharing one GPU is not free).
  * Cold start: the first request after start waits --cold-load seconds ("loading the model").
  * Controlled degradation: when the queue holds >= --degrade-at requests on arrival, the answer
    is capped at --degrade-tokens tokens.
  * A client that hangs up (timeout) frees its queue place or its slot; slot time already spent
    on it is counted as wasted.

--timescale k makes every sleep k times shorter; all reported durations stay in simulated seconds.

    python3 fake_server.py --port 0 --slots 4         # prints "LISTENING 127.0.0.1 <port>"
    GET /metrics  ->  queue, active, served, rejected, cancelled, busy and wasted slot-seconds

Binds 127.0.0.1 only. Standard library only.
"""
import argparse
import asyncio
import json
import sys
import time
from collections import deque

HOST = '127.0.0.1'


class Engine:
    def __init__(self, a):
        self.a = a
        self.k = a.timescale
        self.t0 = time.monotonic()
        self.free = a.slots
        self.waiters = deque()          # futures waiting for a slot (FIFO)
        self.active = 0
        self.loaded = a.cold_load <= 0
        self.loading = None
        self.served = self.rejected = self.cancelled = self.degraded = 0
        self.busy_slot_s = 0.0          # slot-seconds spent on any request
        self.wasted_slot_s = 0.0        # slot-seconds spent on requests the client abandoned

    def now(self):
        return (time.monotonic() - self.t0) / self.k

    async def sleep(self, sim_s):
        if sim_s > 0:
            await asyncio.sleep(sim_s * self.k)

    def queued(self):
        return sum(1 for f in self.waiters if not f.done())

    async def acquire(self):
        if self.free > 0 and not self.queued():
            self.free -= 1
            return
        fut = asyncio.get_running_loop().create_future()
        self.waiters.append(fut)
        try:
            await fut
        except asyncio.CancelledError:
            if fut.done() and not fut.cancelled():   # got the slot just as we were cancelled
                self.release()
            raise

    def release(self):
        while self.waiters:
            fut = self.waiters.popleft()
            if not fut.done():
                fut.set_result(True)
                return
        self.free += 1

    async def ensure_loaded(self):
        if self.loaded:
            return 0.0
        if self.loading is None:
            self.loading = asyncio.ensure_future(self.sleep(self.a.cold_load))
        t = self.now()
        await asyncio.shield(self.loading)
        self.loaded = True
        return self.now() - t

    def decode_rate(self):
        return self.a.decode_tps / (1 + self.a.contention * max(0, self.active - 1))


async def read_request(reader):
    head = await reader.readuntil(b'\r\n\r\n')
    lines = head.decode('latin-1').split('\r\n')
    method, path, _ = lines[0].split(' ', 2)
    headers = {}
    for ln in lines[1:]:
        if ':' in ln:
            k, v = ln.split(':', 1)
            headers[k.strip().lower()] = v.strip()
    body = b''
    n = int(headers.get('content-length', '0') or 0)
    if n:
        body = await reader.readexactly(n)
    return method, path, headers, body


def send_simple(writer, code, obj, extra=''):
    data = json.dumps(obj).encode()
    reason = {200: 'OK', 404: 'Not Found', 503: 'Service Unavailable', 400: 'Bad Request'}.get(code, 'OK')
    writer.write(f'HTTP/1.1 {code} {reason}\r\nContent-Type: application/json\r\nContent-Length: {len(data)}\r\n'
                 f'{extra}Connection: close\r\n\r\n'.encode() + data)


def chunk(writer, obj):
    data = (json.dumps(obj, ensure_ascii=False) + '\n').encode()
    writer.write(b'%x\r\n' % len(data) + data + b'\r\n')


async def chat(eng, reader, writer, req):
    a = eng.a
    opts = req.get('options') or {}
    prompt = ' '.join(m.get('content', '') for m in req.get('messages', []))
    n_in = int(opts.get('homodyne_input_tokens') or max(1, len(prompt) // 4))
    n_out = int(opts.get('num_predict') or 128)
    # bounded queue: refuse at once instead of making the caller wait
    if eng.free == 0 and eng.queued() >= a.max_queue:
        eng.rejected += 1
        send_simple(writer, 503, {'error': 'server busy, please retry'}, 'Retry-After: 2\r\n')
        return
    degraded = a.degrade_at > 0 and eng.queued() >= a.degrade_at
    if degraded:
        n_out = min(n_out, a.degrade_tokens)
        eng.degraded += 1
    t_arrive = eng.now()
    hung_up = asyncio.ensure_future(reader.read())      # resolves with b'' when the client disconnects
    work = asyncio.ensure_future(serve(eng, writer, req, n_in, n_out, degraded, t_arrive))
    hung_up.add_done_callback(lambda f: f.cancelled() or f.exception())   # a reset is just a hang-up
    done, _ = await asyncio.wait({hung_up, work}, return_when=asyncio.FIRST_COMPLETED)
    if work in done:
        hung_up.cancel()
        work.result()
    else:
        work.cancel()
        try:
            await work
        except (asyncio.CancelledError, Exception):
            pass
        eng.cancelled += 1


async def serve(eng, writer, req, n_in, n_out, degraded, t_arrive):
    a = eng.a
    model = req.get('model', 'fake')
    load_s = await eng.ensure_loaded()
    await eng.acquire()
    t_slot = eng.now()
    eng.active += 1
    got = 0
    try:
        writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: application/x-ndjson\r\n'
                     b'Transfer-Encoding: chunked\r\nConnection: close\r\n\r\n')
        await eng.sleep(n_in / a.prefill_tps)
        t_prefill = eng.now()
        loop = asyncio.get_running_loop()
        t_next = loop.time()                       # absolute schedule: sleep overhead does not pile up
        for i in range(n_out):
            t_next += eng.k / eng.decode_rate()
            delay = t_next - loop.time()
            if delay > 0:
                await asyncio.sleep(delay)
            chunk(writer, {'model': model, 'message': {'role': 'assistant', 'content': ' tok'}, 'done': False})
            got += 1
            if i % 8 == 0:
                await writer.drain()
        t_end = eng.now()
        ns = 1e9
        chunk(writer, {'model': model, 'message': {'role': 'assistant', 'content': ''}, 'done': True,
                       'done_reason': 'length', 'total_duration': int((t_end - t_arrive) * ns),
                       'load_duration': int(load_s * ns), 'prompt_eval_count': n_in,
                       'prompt_eval_duration': int((t_prefill - t_slot) * ns), 'eval_count': got,
                       'eval_duration': int((t_end - t_prefill) * ns),
                       'homodyne': {'simulated': True, 'queue_wait_s': round(t_slot - t_arrive - load_s, 4),
                                    'degraded': degraded}})
        writer.write(b'0\r\n\r\n')
        await writer.drain()
        eng.served += 1
    except asyncio.CancelledError:
        eng.wasted_slot_s += eng.now() - t_slot
        raise
    finally:
        eng.busy_slot_s += eng.now() - t_slot
        eng.active -= 1
        eng.release()


async def handle(eng, reader, writer):
    try:
        method, path, headers, body = await read_request(reader)
        if method == 'GET' and path == '/metrics':
            send_simple(writer, 200, {'t': round(eng.now(), 3), 'queue': eng.queued(), 'active': eng.active,
                                      'slots': eng.a.slots, 'served': eng.served, 'rejected': eng.rejected,
                                      'cancelled': eng.cancelled, 'degraded': eng.degraded, 'loaded': eng.loaded,
                                      'busy_slot_s': round(eng.busy_slot_s, 3),
                                      'wasted_slot_s': round(eng.wasted_slot_s, 3), 'simulated': True})
        elif method == 'GET' and path == '/api/version':
            send_simple(writer, 200, {'version': 'homodyne-fake-1', 'simulated': True})
        elif method == 'POST' and path == '/api/chat':
            await chat(eng, reader, writer, json.loads(body or b'{}'))
        else:
            send_simple(writer, 404, {'error': 'not found'})
        await writer.drain()
    except (asyncio.IncompleteReadError, ConnectionError, asyncio.CancelledError):
        pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


def parse(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--port', type=int, default=0, help='0 = any free port (printed on start)')
    p.add_argument('--slots', type=int, default=4)
    p.add_argument('--max-queue', type=int, default=512, help='512 mirrors the Ollama default OLLAMA_MAX_QUEUE')
    p.add_argument('--prefill-tps', type=float, default=600.0)
    p.add_argument('--decode-tps', type=float, default=80.0)
    p.add_argument('--contention', type=float, default=0.10)
    p.add_argument('--cold-load', type=float, default=4.0)
    p.add_argument('--degrade-at', type=int, default=0, help='queue length that switches on short answers (0 = off)')
    p.add_argument('--degrade-tokens', type=int, default=40)
    p.add_argument('--timescale', type=float, default=1.0)
    return p.parse_args(argv)


async def main(argv=None):
    a = parse(argv)
    eng = Engine(a)
    srv = await asyncio.start_server(lambda r, w: handle(eng, r, w), HOST, a.port, backlog=1024)
    port = srv.sockets[0].getsockname()[1]
    print(f'LISTENING {HOST} {port}', flush=True)
    async with srv:
        await srv.serve_forever()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
