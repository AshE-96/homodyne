"""dashboard.py — a live terminal dashboard (plain ANSI escape codes, no curses, no extra packages).

Made for screen recording: one screen, redrawn twice a second, amber only where the SLO is broken.
"""
import asyncio
import shutil
import sys

from metrics import INF, pct, ttft, e2e

AMBER, GREEN, DIM, BOLD, RESET = '\x1b[38;5;214m', '\x1b[38;5;114m', '\x1b[2m', '\x1b[1m', '\x1b[0m'
SPARK = ' ▁▂▃▄▅▆▇█'


def bar(n, scale, width):
    full = min(width, round(n / scale * width)) if scale else 0
    return '█' * full + DIM + '░' * (width - full) + RESET


def spark(values, width):
    v = values[-width:]
    top = max(v + [1])
    return ''.join(SPARK[min(8, round(x / top * 8))] for x in v)


def secs(x, timeout):
    if x is None:
        return '   -  '
    return f'>{timeout:.0f}s ' if x == INF else f'{x:5.1f}s'


def render(live, cfg, width=None):
    width = width or min(100, shutil.get_terminal_size((100, 40)).columns)
    w = max(20, width - 34)
    t = live.samples[-1]['t'] if live.samples else 0
    waiting = sum(1 for s in list(live.state.values()) if s == 'waiting')
    streaming = len(live.state) - waiting
    done = [r for r in live.recs if r['status']]
    t1 = [ttft(r) for r in done]
    t2 = [e2e(r) for r in done]
    good = sum(1 for r in done if r['status'] == 'ok' and ttft(r) <= live.slo_ttft)
    share = good / len(done) if done else None
    fails = sum(1 for r in done if r['status'] != 'ok')
    slo_ok = share is not None and share >= 0.95 and fails / len(done) <= 0.01
    by = lambda s: sum(1 for r in done if r['status'] == s)
    tag = f'{AMBER}SIMULATED SERVICE (ILLUSTRATIVE){RESET}' if live.simulated else f'{GREEN}REAL RUN · {cfg.get("model")}{RESET}'
    slots = cfg.get('slots')
    out = [
        f'{BOLD}HOMODYNE · AI LOAD LAB · HMD-023{RESET}   {tag}',
        f'{DIM}target {cfg["host"]}:{cfg["port"]}' + (f' · {slots} slots' if slots else '') +
        (f' · OLLAMA_NUM_PARALLEL={cfg.get("num_parallel")}' if not live.simulated else '') + RESET,
        f'stage {BOLD}{live.stage}{RESET} · {live.load} · t = {t:5.0f}s / {live.duration:.0f}s',
        f'{DIM}SLO: 95% of requests see the first word within {live.slo_ttft:g}s · fewer than 1% fail{RESET}',
        '',
        f'waiting for first word  {bar(waiting, max([25, waiting] + [x["waiting"] for x in live.samples]), w)} {waiting:4d}',
        f'streaming an answer     {bar(streaming, max(slots or 0, streaming, 1), w)} {streaming:4d}',
        f'queue over time         {AMBER if waiting > (slots or 4) else ""}{spark([s["waiting"] for s in live.samples], w)}{RESET}',
        '',
        f'this stage  sent {len(live.recs):4d} · ok {by("ok"):4d} · timeout {by("timeout"):3d} · '
        f'busy (503) {by("rejected"):3d} · error {by("error"):3d}',
        f'first word   p50 {secs(pct(t1, 50), live.timeout)}   p95 {secs(pct(t1, 95), live.timeout)}   ' +
        ((GREEN + f'SLO kept ({share:.0%} good)') if slo_ok else (AMBER + (f'SLO broken ({share:.0%} good)' if share is not None else 'SLO -'))) + RESET,
        f'full answer  p50 {secs(pct(t2, 50), live.timeout)}   p95 {secs(pct(t2, 95), live.timeout)}',
        f'throughput   {by("ok") / max(t, 1e-9):.2f} answers/s',
        '',
        f'{DIM}finished stages      sent   ok%   first-word p95   full p95    SLO{RESET}',
    ]
    for label, row in live.history[-8:]:
        okp = row['ok'] / row['sent'] if row['sent'] else 0
        mark = f'{GREEN}kept{RESET}' if row['slo_met'] else f'{AMBER}broken{RESET}'
        out.append(f'  {label:<18} {row["sent"]:5d}  {okp:4.0%}   {secs(row["ttft_p95"], live.timeout):>12}   '
                   f'{secs(row["e2e_p95"], live.timeout):>8}   {mark}')
    return out


async def run(live, cfg, stop, period=0.5):
    if not sys.stdout.isatty() or cfg.get('no_dash'):
        return
    sys.stdout.write('\x1b[?25l\x1b[2J')
    try:
        while not stop.is_set():
            lines = render(live, cfg)
            sys.stdout.write('\x1b[H' + '\n'.join(ln + '\x1b[K' for ln in lines) + '\x1b[J')
            sys.stdout.flush()
            await asyncio.sleep(period)
    finally:
        sys.stdout.write('\x1b[?25h\n')
        sys.stdout.flush()
