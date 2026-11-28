#!/usr/bin/env python3
"""deck_figures.py · HMD-S08 · print the three inline SVG charts of deck.src.html from the derived data (stdlib).

    python3 -I artifact/deck_figures.py            # prints <svg> blocks for beats 4, 6 and 11
    python3 -I artifact/deck_figures.py --selftest

The deck copies these blocks verbatim (between the <!-- fig:… --> markers); re-run after any data change.
"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import leave_core as L  # noqa: E402


def hist_1645():
    tr, _ = L.split(L.load()['jfk'])
    xs = L.Index(tr).sample(16 * 60 + 45)
    lo, hi, bw = 40, 130, 2.5
    bins = [sum(1 for x in xs if b <= x < b + bw) for b in [lo + i * bw for i in range(int((hi - lo) / bw))]]
    W, H, x0, x1, y0, y1 = 1600, 460, 60, 1560, 30, 400
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)  # noqa: E731
    Y = lambda n: y1 - n / max(bins) * (y1 - y0)  # noqa: E731
    out = [f'<svg class="chart hist" viewBox="0 0 {W} {H}" role="img">']
    for i, n in enumerate(bins):
        b = lo + i * bw
        cls = 'late' if b + bw / 2 > 75 else 'bar'
        out.append(f'<rect class="{cls}" x="{X(b) + 2:.1f}" y="{Y(n):.1f}" width="{X(b + bw) - X(b) - 4:.1f}" height="{y1 - Y(n):.1f}"/>')
    out.append(f'<line class="ax" x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}"/>')
    for v in range(40, 131, 10):
        out.append(f'<text x="{X(v):.0f}" y="{y1 + 40}" text-anchor="middle">{v}</text>')
    for v, cls in ((L.quantile(xs, .5), 'med'), (75, 'left'), (L.quantile(xs, .95), 'p95')):
        out.append(f'<line class="{cls}" x1="{X(v):.1f}" y1="{y0 - 10}" x2="{X(v):.1f}" y2="{y1}"/>')
    out.append('</svg>')
    return '\n'.join(out), len(xs)


def fan():
    tr, _ = L.split(L.load()['jfk'])
    idx = L.Index(tr)
    ts = list(range(12 * 60, 20 * 60 + 1, 5))
    st = {t: L.stats(idx.sample(t)) for t in ts}
    W, H, x0, x1, y0, y1 = 1600, 470, 90, 1560, 20, 400
    X = lambda t: x0 + (t - ts[0]) / (ts[-1] - ts[0]) * (x1 - x0)  # noqa: E731
    Y = lambda m: y1 - (m - 30) / (110 - 30) * (y1 - y0)  # noqa: E731
    path = lambda k: ' '.join(f'{"M" if i == 0 else "L"}{X(t):.1f},{Y(st[t][k]):.1f}' for i, t in enumerate(ts))  # noqa: E731
    out = [f'<svg class="chart fan" viewBox="0 0 {W} {H}" role="img">']
    for m in (40, 60, 80, 100):
        out.append(f'<line class="grid" x1="{x0}" y1="{Y(m):.0f}" x2="{x1}" y2="{Y(m):.0f}"/><text x="{x0 - 12}" y="{Y(m) + 9:.0f}" text-anchor="end">{m}</text>')
    for t in range(12 * 60, 20 * 60 + 1, 60):
        out.append(f'<text x="{X(t):.0f}" y="{y1 + 44}" text-anchor="middle">{L.hhmm(t)}</text>')
    out.append(f'<path class="p95" d="{path("p95")}"/><path class="p50" d="{path("p50")}"/>')
    for t in (960, 990, 1050, 1110):
        out.append(f'<circle class="pt" cx="{X(t):.1f}" cy="{Y(st[t]["p95"]):.1f}" r="10"/>')
    out.append('</svg>')
    return '\n'.join(out)


def weeks():
    data = L.load()['jfk']
    wk = {}
    for d, dep, m in data:
        if 900 <= dep < 1080:
            day = date.fromisoformat(d)
            wk.setdefault(day - timedelta(days=day.weekday()), []).append(m)
    keys = sorted(wk)
    med = [L.quantile(sorted(wk[k]), .5) for k in keys]
    W, H, x0, y1 = 1600, 420, 40, 340
    bw = (W - 2 * x0) / len(keys)
    out = [f'<svg class="chart weeks" viewBox="0 0 {W} {H}" role="img">']
    for i, (k, m) in enumerate(zip(keys, med)):
        cls = 'test' if str(k) >= L.SPLIT else ('quiet' if str(k) in ('2026-03-30', '2026-04-06') else 'train')
        h = m / 90 * (y1 - 20)
        x = x0 + i * bw
        out.append(f'<rect class="{cls}" x="{x + 14:.0f}" y="{y1 - h:.0f}" width="{bw - 28:.0f}" height="{h:.0f}"/>'
                   f'<text x="{x + bw / 2:.0f}" y="{y1 - h - 14:.0f}" text-anchor="middle">{m:.1f}</text>'
                   f'<text class="sm" x="{x + bw / 2:.0f}" y="{y1 + 40}" text-anchor="middle">{k.strftime("%d %b")}</text>')
    out.append('</svg>')
    return '\n'.join(out)


if __name__ == '__main__':
    h, n = hist_1645()
    if '--selftest' in sys.argv:
        assert n == 234, n
        assert fan().count('<circle') == 4 and weeks().count('<rect') == 9
        print('selftest ok')
        sys.exit(0)
    print('<!-- fig:hist (beat 4) -->\n' + h + '\n<!-- fig:fan (beat 6) -->\n' + fan() + '\n<!-- fig:weeks (beat 11) -->\n' + weeks())
