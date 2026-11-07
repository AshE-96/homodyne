#!/usr/bin/env python3
"""Verify the season-01 episode packages (HMD-002..HMD-010).

Reads channel/season-01/manifest.json (or the manifest given as the first
argument, e.g. channel/global/manifest.json) and checks, for every episode folder:
required files, beat structure, spoken word count, deck/script beat match,
deck self-containment and JS syntax, Persian/English deck parity, banned words,
and local links.
Warnings (not failures) list open [RUN] / [VERIFY] items to resolve before recording.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/(sys.argv[1] if len(sys.argv) > 1 else 'channel/season-01/manifest.json')
FILES = ['README.md', 'script-fa.md', 'hooks-fa.md', 'package-fa.md', 'deck.src.html', 'deck-fa.html', 'deck-en.html', 'sources.md']
DECKS = ('deck-fa.html', 'deck-en.html')
WORDS = (1400, 1900)
BEATS = (12, 16)
BANNED = ['انقلابی', 'باورنکردنی', 'همه‌چیز را عوض کرد', 'رازی که نمی‌گویند', 'ممنون که دیدید']


def spoken_words(md):
    """Count words in the paragraphs under each **متن گفتاری:** label."""
    total = 0
    for block in re.split(r'\*\*متن گفتاری:\*\*', md)[1:]:
        block = re.split(r'\*\*در یک جمله:\*\*|\n### ', block)[0]
        block = re.sub(r'\*\*\[[A-Z\- ]+\]\*\*', ' ', block)
        total += len(re.findall(r'\S+', block))
    return total


def frame_shape(deck):
    """Frame ids, start times and the sequence of component classes: must be identical in fa and en."""
    out = []
    for attrs, body in re.findall(r'<section ([^>]*)>(.*?)</section>', deck, re.S):
        body = re.sub(r'<aside class="notes">.*?</aside>', '', body, flags=re.S)
        out.append((re.search(r'id="([^"]+)"', attrs).group(1), re.search(r'data-start="(\d+)"', attrs) and
                    re.search(r'data-start="(\d+)"', attrs).group(1),
                    tuple(c for c in re.findall(r'class="([^"]+)"', body) if c not in ('sep', 'long'))))  # sep: fa-only separator; long: per-language cover title size
    return out


def check_deck(path, beats, script_starts):
    deck = path.read_text()
    errors = []
    frames = deck.count('<section class="frame ')
    if frames != beats + 1:
        errors.append(f'{frames} frames, expected {beats} beats + cover')
    starts = [int(x) for x in re.findall(r'data-start="(\d+)"', deck)]
    if starts != sorted(starts):
        errors.append('data-start values are not ascending')
    if script_starts and starts != script_starts:
        errors.append(f'data-start {starts} does not match the script beat times {script_starts}')
    if re.search(r'</?t-(fa|en)\b', deck):
        errors.append('unbuilt <t-fa>/<t-en> tags left in the deck')
    if 'https://fonts.' in deck or '<script src=' in deck or '<link ' in deck:
        errors.append('loads external fonts, styles or scripts')
    if 'id="next"' not in deck or 'id="prev"' not in deck:
        errors.append('missing prev/next buttons')
    js = re.search(r'<script>(.*?)</script>', deck, re.S)
    if js:
        with tempfile.NamedTemporaryFile(suffix='.js', mode='w') as f:
            f.write(js.group(1))
            f.flush()
            if subprocess.run(['node', '--check', f.name], capture_output=True).returncode:
                errors.append('JS has a syntax error')
    else:
        errors.append('no inline script')
    return errors


def check(ep):
    folder = ROOT/ep['path']
    errors, notes = [], []
    for name in FILES:
        if not (folder/name).exists():
            errors.append(f'missing {name}')
    if not (folder/'artifact').is_dir():
        errors.append('missing artifact/')
    if errors:
        return errors, notes, {}

    md = (folder/'script-fa.md').read_text()
    beats = md.count('**متن گفتاری:**')
    words = spoken_words(md)
    stats = {'beats': beats, 'words': words}

    if md.count('**ON SCREEN:**') != beats or md.count('**در یک جمله:**') != beats:
        errors.append('each beat needs one ON SCREEN, one متن گفتاری and one در یک جمله')
    if not BEATS[0] <= beats <= BEATS[1]:
        errors.append(f'{beats} beats, expected {BEATS[0]}-{BEATS[1]}')
    if not WORDS[0] <= words <= WORDS[1]:
        errors.append(f'{words} spoken words, expected {WORDS[0]}-{WORDS[1]}')
    script_starts = [int(m) * 60 + int(s) for m, s in re.findall(r'^### قاب \d+ · (\d+):(\d+)', md, re.M)]
    shapes = {}
    for name in DECKS:
        errors += [f'{name}: {e}' for e in check_deck(folder/name, beats, script_starts)]
        shapes[name] = frame_shape((folder/name).read_text())
    stats['deck'] = f'{beats}+cover ×2'
    if shapes['deck-fa.html'] != shapes['deck-en.html']:
        errors.append('deck-fa.html and deck-en.html differ in frames, timings or components')

    for name in ('script-fa.md', 'hooks-fa.md', 'package-fa.md'):
        text = (folder/name).read_text()
        for word in BANNED:
            if word in text and f'«{word}»' not in text:
                errors.append(f'banned phrase "{word}" in {name}')
        for target in re.findall(r'\]\(([^)\s]+)\)', text):
            if not target.startswith(('https://', 'http://', '#', 'mailto:')):
                if not (folder/target.split('#')[0]).exists():
                    errors.append(f'broken link {target} in {name}')

    for tag in ('[RUN]', '[VERIFY]'):
        n = sum((folder/f).read_text().count(tag) for f in FILES if f.endswith('.md'))
        if n:
            notes.append(f'{n}× {tag}')
    return errors, notes, stats


def main():
    episodes = json.loads(MANIFEST.read_text())
    failed = 0
    for ep in episodes:
        errors, notes, stats = check(ep)
        status = 'FAIL' if errors else 'ok  '
        detail = ' · '.join(f'{k} {v}' for k, v in stats.items())
        print(f'{status} {ep["hmd"]}  {detail}  {"  ".join(notes)}')
        for e in errors:
            print(f'       - {e}')
        failed += bool(errors)
    print(f'\n{len(episodes) - failed}/{len(episodes)} episodes pass')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
