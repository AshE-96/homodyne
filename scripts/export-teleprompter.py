#!/usr/bin/env python3
"""Export a recording kit for each episode in a manifest.

For every episode folder this writes recording/ with:
  teleprompter-fa.txt   spoken text only, one block per beat (paste into any teleprompter app)
  teleprompter-fa.html  self-contained RTL scroller: Space play/pause, arrows speed, +/- size, M mirror
  recording-sheet-fa.md one page for the shoot: timing, open checklist items, B-roll, on-screen commands

Usage:
  python3 scripts/export-teleprompter.py                       # season-01 + global manifests
  python3 scripts/export-teleprompter.py --only HMD-002 HMD-G01
"""
import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ['channel/season-01/manifest.json', 'channel/global/manifest.json']
WPM = 125  # spoken pace used in the episode bible
MARKERS = re.compile(r'\*\*(Grab|Promise|Stakes):\*\*\s*|\*\*\[[A-Z\- ]+\]\*\*\s*')
BEAT = re.compile(r'^### قاب (\d+) · ([\d:]+)[–-]([\d:]+) · (.+)$', re.M)


def beats(md):
    """Yield (number, start, end, title, on_screen, visual, spoken) for each beat."""
    heads = list(BEAT.finditer(md))
    for i, h in enumerate(heads):
        body = md[h.end():heads[i + 1].start() if i + 1 < len(heads) else len(md)]
        body = body.split('\n## ')[0]
        on_screen = re.search(r'\*\*ON SCREEN:\*\*\s*`?([^`\n]*)`?', body)
        visual = re.search(r'\*\*تصویر / اجرا:\*\*\s*(.+)', body)
        spoken = body.split('**متن گفتاری:**', 1)[1].split('**در یک جمله:**', 1)[0]
        spoken = '\n'.join(MARKERS.sub('', line).strip() for line in spoken.strip().splitlines() if line.strip())
        yield (int(h.group(1)), h.group(2), h.group(3), h.group(4).strip(),
               on_screen.group(1).strip() if on_screen else '', visual.group(1).strip() if visual else '', spoken)


def open_items(folder):
    items = []
    for name in ('README.md', 'script-fa.md'):
        for line in (folder / name).read_text().splitlines():
            if line.lstrip().startswith('- [ ]'):
                items.append(line.strip())
    return items


def code_blocks(text):
    return [b.strip() for b in re.findall(r'```(?:bash)?\n(.*?)```', text, re.S)]


HTML = """<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · teleprompter</title>
<style>
:root{{--bg:#111214;--fg:#F3F1EC;--amber:#F0B45A;--muted:#8f8c84}}
html,body{{margin:0;background:var(--bg);color:var(--fg);font-family:Vazirmatn,Tahoma,sans-serif}}
#text{{max-width:1100px;margin:0 auto;padding:45vh 6vw;font-size:var(--size,52px);line-height:1.75}}
h2{{font:600 .45em monospace;color:var(--amber);margin:2.2em 0 .4em;direction:ltr;text-align:right}}
.screen{{font:.38em monospace;color:var(--muted);direction:ltr;text-align:right;margin:0 0 .8em}}
p{{margin:0 0 .7em}}
.mirror{{transform:scaleX(-1)}}
#guide{{position:fixed;top:40vh;left:0;right:0;height:2px;background:var(--amber);opacity:.35;pointer-events:none}}
#hud{{position:fixed;bottom:8px;left:8px;font:12px monospace;color:var(--muted);direction:ltr}}
</style><body><div id="guide"></div><div id="text">{body}</div>
<div id="hud">Space play · ↑↓ speed · +/- size · M mirror · <span id="s"></span></div>
<script>
let speed=40,play=false,size=52,last=null;const t=document.getElementById('text'),s=document.getElementById('s');
function hud(){{s.textContent=(play?'playing':'paused')+' · '+speed+' px/s · '+size+'px'}}
function step(ts){{if(play&&last!==null)window.scrollBy(0,speed*(ts-last)/1000);last=ts;requestAnimationFrame(step)}}
document.addEventListener('keydown',e=>{{if(e.key===' '){{play=!play;e.preventDefault()}}
else if(e.key==='ArrowUp'){{speed+=5;e.preventDefault()}}else if(e.key==='ArrowDown'){{speed=Math.max(5,speed-5);e.preventDefault()}}
else if(e.key==='+'||e.key==='='){{size+=4}}else if(e.key==='-'){{size=Math.max(24,size-4)}}
else if(e.key.toLowerCase()==='m'){{t.classList.toggle('mirror')}}t.style.setProperty('--size',size+'px');hud()}});
hud();requestAnimationFrame(step);
</script></body></html>
"""


def export(ep):
    folder = ROOT / ep['path']
    md = (folder / 'script-fa.md').read_text()
    readme = (folder / 'README.md').read_text()
    title = re.search(r'^## (.+)$', md, re.M).group(1).strip()
    rows = list(beats(md))
    out = folder / 'recording'
    out.mkdir(exist_ok=True)

    words = sum(len(r[6].split()) for r in rows)
    txt = [f'{ep["hmd"]} · {title}', f'{len(rows)} قاب · {words} واژه · حدود {words // WPM} دقیقه گفتار', '']
    body = []
    for n, start, end, beat_title, screen, _, spoken in rows:
        txt += [f'— قاب {n} · {start} · {beat_title}', spoken, '']
        paras = ''.join(f'<p>{html.escape(p)}</p>' for p in spoken.splitlines())
        body.append(f'<h2>{n} · {start} · {html.escape(beat_title)}</h2>'
                    f'<div class="screen">{html.escape(screen)}</div>{paras}')
    (out / 'teleprompter-fa.txt').write_text('\n'.join(txt))
    (out / 'teleprompter-fa.html').write_text(HTML.format(title=html.escape(title), body=''.join(body)))

    hook = re.search(r'\*\*هوک انتخاب‌شده:\*\*\s*([^\n(—.؛]+)', md)
    broll = [(n, start, v) for n, start, _, _, _, v, _ in rows if '[B-ROLL CUE]' in v]
    sheet = [f'# برگهٔ ضبط · {ep["hmd"]} · {title}', '',
             f'- **قاب:** {len(rows)} · **واژهٔ گفتاری:** {words} · **گفتار:** حدود {words // WPM} دقیقه (به‌اضافهٔ زمان نمایش دک)',
             f'- **هوک:** {hook.group(1).strip() if hook else "—"}',
             f'- **دک:** [`deck.html`](../deck.html) (← →، F تمام‌صفحه، N یادداشت راوی؛ هنگام ضبط N خاموش)',
             '- **تله‌پرامپتر:** [`teleprompter-fa.html`](teleprompter-fa.html) (Space پخش/توقف، ↑↓ سرعت، M آینه) یا [`teleprompter-fa.txt`](teleprompter-fa.txt)',
             '', '## نقشهٔ قاب‌ها', '', '| قاب | شروع | عنوان | روی صفحه |', '|---:|---|---|---|']
    sheet += [f'| {n} | {start} | {t} | `{s}` |' for n, start, _, t, s, _, _ in rows]
    items = open_items(folder)
    sheet += ['', '## باز پیش از ضبط', ''] + (items or ['- هیچ مورد بازی نیست.'])
    blocks = code_blocks(readme)
    if blocks:
        sheet += ['', '## دستورهای روی صفحه (از README)', '']
        sheet += [f'```bash\n{b}\n```' for b in blocks]
    if broll:
        sheet += ['', '## B-roll', ''] + [f'- قاب {n} ({start}): {v}' for n, start, v in broll]
    sheet += ['', 'ساخته‌شده با `python3 scripts/export-teleprompter.py`. متن اصلی همیشه `script-fa.md` است.', '']
    (out / 'recording-sheet-fa.md').write_text('\n'.join(sheet))
    return words, len(rows), len(items)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--only', nargs='*', help='HMD ids to export (default: all in the manifests)')
    ap.add_argument('--manifest', nargs='*', default=MANIFESTS)
    args = ap.parse_args()
    for m in args.manifest:
        for ep in json.loads((ROOT / m).read_text()):
            if args.only and ep['hmd'] not in args.only:
                continue
            words, n, items = export(ep)
            print(f'{ep["hmd"]}  {n} beats · {words} words · {items} open items -> {ep["path"]}/recording/')


if __name__ == '__main__':
    main()
