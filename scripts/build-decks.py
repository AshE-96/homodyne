#!/usr/bin/env python3
"""
build-decks.py — build each episode's two recording decks from one bilingual source.

    parts/<episode>/deck.src.html  ──►  deck-fa.html  (Persian, right to left)
                                   └─►  deck-en.html  (English, left to right)

The source holds every frame once. Each piece of visible text is a pair,
<t-fa>…</t-fa><t-en>…</t-en>, so the two decks always have the same frames in
the same order with the same content; only the language differs. Text outside a
pair (terminal output, token chips, model names) appears identically in both.

Both outputs are single self-contained files: the shared engine
(channel/season-01/deck-engine/deck.css + deck.js), the Vazirmatn font
(brand/fonts/, SIL OFL) and the Homodyne mark are inlined.

    python3 scripts/build-decks.py               # build all
    python3 scripts/build-decks.py --only hmd-005
    python3 scripts/build-decks.py --check       # fail if any output is stale or a source is broken

Standard library only.
"""

import argparse
import base64
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENGINE = ROOT / 'channel/season-01/deck-engine'
FONTS = ROOT / 'brand/fonts'
MARK = ROOT / 'brand/logo/homodyne-mark-small-night.svg'
META_EN = ROOT / 'site/src/data/episodes-meta.json'
MANIFESTS = [ROOT / 'channel/season-01/manifest.json', ROOT / 'channel/global/manifest.json']

SERIES_FA = {
    'Benchmark Lab': 'آزمایشگاه بنچمارک',
    'Silent Breakthrough': 'پیشرفت بی‌صدا',
    'AI in Production': 'هوش مصنوعی در محصول',
    'Algorithm X-Ray': 'الگوریتم زیر ذره‌بین',
    'Global': 'جهانی',
    'Bridge': 'پل',
}
FA_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
ARABIC = re.compile(r'[؀-ۿﭐ-﷿ﹰ-﻿]')
PAIR = re.compile(r'<t-fa>(.*?)</t-fa>\s*<t-en>(.*?)</t-en>', re.S)
SECTION = re.compile(r'<section\b([^>]*)>(.*?)</section>', re.S)
VOID = {'br', 'img', 'hr', 'wbr', 'use', 'path', 'rect', 'polyline', 'circle', 'line', 'meta', 'input'}


def series_label(fmt, lang):
    """'Benchmark Lab · E01' -> 'آزمایشگاه بنچمارک · جلسهٔ ۱' / unchanged in English."""
    parts = [p.strip() for p in fmt.split('·')]
    if lang == 'en':
        return ' · '.join(parts)
    out = []
    for p in parts:
        m = re.fullmatch(r'E0*(\d+)', p)
        out.append(('جلسهٔ ' + m.group(1).translate(FA_DIGITS)) if m else SERIES_FA.get(p, p))
    return ' · '.join(out)


def episodes():
    meta_en = json.loads(META_EN.read_text(encoding='utf-8'))
    eps = []
    for mf in MANIFESTS:
        for e in json.loads(mf.read_text(encoding='utf-8')):
            en = meta_en.get(e['hmd'])
            if not en:
                continue
            eps.append({'hmd': e['hmd'], 'slug': en['slug'], 'format': e['format'],
                        'folder': ROOT / e['path'], 'title_fa': e['title'], 'title_en': en['en']['title']})
    return eps


def pick(text, lang):
    return PAIR.sub(lambda m: m.group(1 if lang == 'fa' else 2), text)


def plain(fragment):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()


# ── bidi: isolate every Latin run inside Persian text ─────────────────────────
LATIN_RUN = re.compile(r"[A-Za-z0-9\uE000-\uF8FF][A-Za-z0-9\uE000-\uF8FF .,:/+\-−–×=<>≈≠≤≥→_'’\"()%~·…*^#@!?\[\]{}|$]*[A-Za-z0-9\uE000-\uF8FF%)\]]|[A-Za-z0-9]")
ENTITY = re.compile(r'&[#A-Za-z0-9]+;')


def isolate_latin(text):
    ents = []

    def hold(m):
        ents.append(m.group(0))
        return chr(0xE000 + len(ents) - 1)

    t = ENTITY.sub(hold, text)
    def wrap(m):
        run, tail = m.group(0), ''
        # a closing bracket that opens outside the run belongs to the Persian sentence, not to the Latin run
        while run and run[-1] in ')]' and run.count('(') + run.count('[') < run.count(')') + run.count(']'):
            tail = run[-1] + tail
            run = run[:-1].rstrip()
        return '<bdi dir="ltr">' + run + '</bdi>' + tail if run else tail

    t = LATIN_RUN.sub(wrap, t)
    return re.sub(r'[\uE000-\uF8FF]', lambda m: ents[ord(m.group(0)) - 0xE000], t)


def walk(fragment, on_text):
    """Call on_text(text, ctx) for each text node; ctx has 'skip' (inside bdi/code/ltr/svg) and 'fa' (inside lang=fa)."""
    out, stack = [], [{'skip': False, 'fa': False}]
    for tok in re.split(r'(<[^>]+>)', fragment):
        if not tok:
            continue
        if tok.startswith('<'):
            m = re.match(r'<\s*(/?)\s*([a-zA-Z0-9-]+)', tok)
            if m and not tok.startswith('<!'):
                closing, name = m.group(1) == '/', m.group(2).lower()
                if closing:
                    if len(stack) > 1:
                        stack.pop()
                elif not (tok.endswith('/>') or name in VOID):
                    top = stack[-1]
                    skip = top['skip'] or name in ('bdi', 'code', 'pre', 'script', 'style', 'svg') \
                        or 'dir="ltr"' in tok or re.search(r'class="[^"]*\b(code|formula|mono|ltr)\b', tok) is not None
                    stack.append({'skip': skip, 'fa': top['fa'] or 'lang="fa"' in tok})
            out.append(tok)
        else:
            out.append(on_text(tok, stack[-1]))
    return ''.join(out)


# ── assembling one deck ───────────────────────────────────────────────────────
def mark_symbol():
    svg = MARK.read_text(encoding='utf-8')
    svg = re.sub(r'<metadata>.*?</metadata>', '', svg, flags=re.S)
    inner = re.search(r'<svg[^>]*>(.*)</svg>', svg, re.S).group(1).strip()
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
            '<symbol id="hmd-mark" viewBox="0 0 512 512">' + inner + '</symbol></svg>')


def font_faces():
    rng = {
        'arabic': 'U+0600-06FF,U+0750-077F,U+200C-200E,U+2010-2011,U+204F,U+FB50-FDFF,U+FE70-FEFC',
        'latin': 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD',
    }
    css = []
    for subset in ('arabic', 'latin'):
        for w in (400, 700):
            data = base64.b64encode((FONTS / f'vazirmatn-{subset}-{w}-normal.woff2').read_bytes()).decode()
            css.append(f'@font-face{{font-family:"Vazirmatn";font-style:normal;font-weight:{w};font-display:block;'
                       f'src:url(data:font/woff2;base64,{data}) format("woff2");unicode-range:{rng[subset]}}}')
    return '\n'.join(css)


def build_frame(attrs, body, lang, series, n):
    footer = re.search(r'<footer>(.*?)</footer>', body, re.S)
    notes = re.search(r'<aside class="notes">(.*?)</aside>', body, re.S)
    content = body
    for m in (footer, notes):
        if m:
            content = content.replace(m.group(0), '')
    brand = 'هومودین' if lang == 'fa' else 'Homodyne'
    label = f'قاب {str(n).translate(FA_DIGITS)}' if lang == 'fa' else f'Beat {n}'
    attrs = re.sub(r'\s*aria-label="[^"]*"', '', attrs).strip()
    return (f'<section {attrs} aria-label="{label}">\n'
            f'<header class="chrome"><svg class="mark" aria-hidden="true"><use href="#hmd-mark"/></svg>'
            f'<span class="brand">{brand}</span><span class="series">{series}</span><span class="count"></span></header>\n'
            f'<main><div class="fit">\n{content.strip()}\n</div></main>\n'
            f'<footer>{footer.group(1).strip() if footer else ""}</footer>\n'
            + (f'<aside class="notes">{notes.group(1).strip()}</aside>\n' if notes else '')
            + '</section>')


def build_cover(body, ep, lang, series):
    h1 = re.search(r'<h1>(.*?)</h1>', body, re.S)
    promise = re.search(r'<p class="promise">(.*?)</p>', body, re.S)
    brand = 'هومودین' if lang == 'fa' else 'Homodyne'
    long_title = ' class="long"' if h1 and len(plain(h1.group(1))) > 50 else ''
    bottom = ('متن، منبع‌ها و کد این قسمت:' if lang == 'fa' else 'Script, sources and code for this episode:')
    note = ('<b>کاور</b><p>بعد از هوک و «من محمدم، اینجا هومودینه» دو تا سه ثانیه روی این قاب بمان، بعد → برای قاب ۱.</p>'
            if lang == 'fa' else
            '<b>Cover</b><p>Hold for two or three seconds after the hook and the channel intro, then → for beat 1.</p>')
    return (f'<section class="frame night cover" id="cover" aria-label="{"کاور" if lang == "fa" else "Cover"}">\n'
            f'<div class="top"><svg class="mark" aria-hidden="true"><use href="#hmd-mark"/></svg>'
            f'<span class="brand">{brand}</span><span class="hmd">{ep["hmd"]}</span></div>\n'
            f'<main><div class="fit"><p class="series">{series}</p>'
            f'<h1{long_title}>{h1.group(1).strip() if h1 else ""}</h1>'
            + (f'<p class="promise">{promise.group(1).strip()}</p>' if promise else '')
            + '</div></main>\n<svg class="wave" aria-hidden="true"></svg>\n'
            f'<div class="bottom"><span>{bottom}</span><span class="site">homodyne.m2gh.ir</span></div>\n'
            f'<aside class="notes">{note}</aside>\n</section>')


def build(ep, lang, src, problems, warnings):
    picked = pick(src, lang)
    for m in re.finditer(r'</?t-(fa|en)\b', picked):
        problems.append(f'{lang}: unpaired <t-{m.group(1)}> near offset {m.start()}')
        break
    series = series_label(ep['format'], lang)

    sections = SECTION.findall(picked)
    cover = [b for a, b in sections if 'class="cover"' in a]
    frames = [(a, b) for a, b in sections if 'class="frame' in a]
    if len(cover) != 1:
        problems.append(f'{lang}: needs exactly one <section class="cover">')
        cover = ['']
    out = [build_cover(cover[0], ep, lang, series)]

    starts = []
    for i, (attrs, body) in enumerate(frames, 1):
        fid = re.search(r'id="([^"]+)"', attrs)
        start = re.search(r'data-start="([0-9]+)"', attrs)
        if not fid or fid.group(1) != f'beat-{i}':
            problems.append(f'{lang}: frame {i} must have id="beat-{i}"')
        if not start:
            problems.append(f'{lang}: frame {i} has no numeric data-start')
        else:
            starts.append(int(start.group(1)))
        out.append(build_frame(attrs, body, lang, series, i))
    if starts != sorted(starts):
        problems.append(f'{lang}: data-start values are not ascending')

    frames_html = '\n\n'.join(out)

    if lang == 'fa':
        def fa_text(t, ctx):
            if ctx['skip']:
                return t
            if ARABIC.search(t) and re.search(r'(?<![A-Za-z0-9.\-_])(?<![A-Za-z] )[0-9]+(?![A-Za-z0-9\-_])', t):
                warnings.append(f'fa: ASCII digits in Persian text: «{plain(t)[:60]}»')
            # « · » next to Persian digits reads like «۰»: draw separators as a thin rule instead
            t = t.replace(' · ', '\x01')
            return isolate_latin(t).replace('\x01', ' <span class="sep">·</span> ')
        frames_html = walk(frames_html, fa_text)
    else:
        def en_text(t, ctx):
            if ARABIC.search(t) and not ctx['fa']:
                warnings.append(f'en: Persian text outside lang="fa": «{plain(t)[:60]}»')
            return t
        frames_html = walk(frames_html, en_text)

    title_seen = plain(re.search(r'<h1>(.*?)</h1>', cover[0], re.S).group(1)) if '<h1>' in cover[0] else ''
    title_want = ep['title_fa'] if lang == 'fa' else ep['title_en']
    if title_seen != title_want:
        problems.append(f'{lang}: cover title «{title_seen}» differs from the manifest title «{title_want}»')

    css = (ENGINE / 'deck.css').read_text(encoding='utf-8')
    # an episode may add its own rules (charts, diagrams) in <style> blocks of the source
    css += ''.join('/* episode */\n' + block.strip() + '\n' for block in re.findall(r'<style>(.*?)</style>', src, re.S))
    js = (ENGINE / 'deck.js').read_text(encoding='utf-8')
    direction = 'rtl' if lang == 'fa' else 'ltr'
    title = (f'هومودین {ep["hmd"]} · دک ضبط' if lang == 'fa' else f'Homodyne {ep["hmd"]} · recording deck')
    return (f'<!doctype html>\n<html lang="{lang}" dir="{direction}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>\n'
            f'<!-- Generated by scripts/build-decks.py from deck.src.html. Edit the source, then run: make decks -->\n'
            f'<style>\n{font_faces()}\n{css}</style></head><body>\n{mark_symbol()}\n'
            f'<div class="stage">\n{frames_html}\n</div>\n'
            '<nav><button id="prev" aria-label="Previous">←</button><span id="counter"></span><span id="time"></span>'
            '<button id="next" aria-label="Next">→</button><span class="keys">F fullscreen · H hide bar · N notes</span></nav>'
            '<div class="progress"></div>\n'
            f'<script>\n{js}</script>\n</body></html>\n'), len(frames)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--check', action='store_true', help='do not write; fail if outputs are stale or sources broken')
    ap.add_argument('--only', help='episode slug, e.g. hmd-005')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    failed = 0
    built = 0
    for ep in episodes():
        if args.only and ep['slug'] != args.only:
            continue
        src_path = ep['folder'] / 'deck.src.html'
        if not src_path.exists():
            print(f'  MISSING  {ep["hmd"]}: {src_path.relative_to(ROOT)}')
            failed += 1
            continue
        src = src_path.read_text(encoding='utf-8')
        problems, warnings = [], []
        counts = {}
        for lang in ('fa', 'en'):
            doc, counts[lang] = build(ep, lang, src, problems, warnings)
            target = ep['folder'] / f'deck-{lang}.html'
            if args.check:
                if not target.exists() or target.read_text(encoding='utf-8') != doc:
                    problems.append(f'{target.name} is stale: run make decks')
            elif not problems:
                target.write_text(doc, encoding='utf-8')
        if counts.get('fa') != counts.get('en'):
            problems.append(f'frame count differs: fa {counts.get("fa")} vs en {counts.get("en")}')
        status = 'FAIL' if problems else 'ok'
        if problems or not args.quiet:
            print(f'  {status:4}  {ep["hmd"]}  {counts.get("fa", 0)} beats + cover'
                  + (f'  ({len(warnings)} warning(s))' if warnings else ''))
        for p in problems:
            print('        ✗ ' + p)
        for w in warnings if not args.quiet else []:
            print('        · ' + w)
        failed += bool(problems)
        built += 1
    print(f'{built} episode(s), {failed} failed' + (' (check only)' if args.check else ''))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
