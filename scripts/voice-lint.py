#!/usr/bin/env python3
"""Voice lint for a Homodyne script-fa.md (v6 rules in docs/narration-style.md).

    python3 scripts/voice-lint.py parts/05-season-02/<slug>/script-fa.md

Reports, per beat, spoken words and pace (words per minute over the beat's time), then any
sentence over 22 words, any sentence with more than one English word (AI does not count),
banned calques, and how often «یک» appears. Exit code 1 if any issue is found.
"""
import re
import sys

CALQ = ['در نظر داشته باش که', 'بیا ببینیم که', 'این به این معنیه که', 'در پایان روز', 'نصف داستان',
        'نشون می‌ده که', 'نشان می‌دهد که']


def main(path):
    md = open(path, encoding='utf-8').read()
    beats = re.findall(r'^### قاب (\d+) · (\d+):(\d+)–(\d+):(\d+) · .*?\n(.*?)(?=^### |^## |\Z)', md, re.M | re.S)
    tot = yek = 0
    issues = []
    for n, m1, s1, m2, s2, body in beats:
        dur = (int(m2) * 60 + int(s2)) - (int(m1) * 60 + int(s1))
        disp = re.search(r'نمایش \+(\d+)s', body)
        disp = int(disp.group(1)) if disp else 0
        if '**متن گفتاری:**' not in body:
            issues.append((n, 'no spoken block'))
            continue
        sp = body.split('**متن گفتاری:**')[1].split('**در یک جمله:**')[0]
        sp = re.sub(r'\*\*\[[A-Z\- ]+\]\*\*|\*\*(Grab|Promise|Stakes):\*\*|\*\*شاخهٔ[^*]*\*\*', ' ', sp)
        sp = re.sub(r'<[^>]+>|\[RUN[^\]]*\]', ' ', sp)
        w = len(re.findall(r'\S+', sp))
        tot += w
        wpm = w / max(1, (dur - disp)) * 60
        yek += len(re.findall(r'(?<![\w‌])یک(?![\w‌])', sp))
        for sent in re.split(r'[.!?؟…:؛]\s*|\n', sp):
            ws = re.findall(r'\S+', sent)
            if len(ws) > 22:
                issues.append((n, f'long {len(ws)}w: ' + sent.strip()[:50]))
            en = [x for x in re.findall(r'[A-Za-z][A-Za-z\-]+', sent) if x != 'AI']
            if len(en) > 1:
                issues.append((n, 'english×%d: %s' % (len(en), ' '.join(en[:4]))))
        for c in CALQ:
            if c in sp:
                issues.append((n, 'calque ' + c))
        flag = '' if 110 <= wpm <= 155 else '  <-- pace'
        print(f'beat {n:>2} {dur:3}s words {w:3} wpm {wpm:4.0f}{flag}')
    print(f'total {tot} words · «یک» {yek} ({100 * yek / max(tot, 1):.2f}/100)')
    for i in issues:
        print('ISSUE', *i)
    return 1 if issues else 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
