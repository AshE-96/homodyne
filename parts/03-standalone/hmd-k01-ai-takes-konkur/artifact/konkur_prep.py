#!/usr/bin/env python3
"""HMD-K01 · konkur_prep.py — from the official PDFs to validated question files (all in private/konkur/).

    python3 konkur_prep.py render                    # raw/*.pdf → pages/<pdf>/page-NN.png   (pdftoppm, 150 dpi)
    python3 konkur_prep.py text                      # raw/*.pdf → pages/<pdf>/text.txt       (pdftotext, if a text layer)
    python3 konkur_prep.py template 1405 tajrobi --subjects bio:101-150,phys:151-185,chem:186-220,math:221-250
    python3 konkur_prep.py crop questions/1405-tajrobi.json     # every figure with a crop box → crops/…png
    python3 konkur_prep.py validate                  # every questions/*.json against the schema (protocol.md §2)
    python3 konkur_prep.py diff A.json B.json        # two independent transcriptions, field by field
    python3 konkur_prep.py keys questions/1405-tajrobi.json keys-1405-tajrobi.txt   # "101 2" lines, final key
    python3 konkur_prep.py sample --n 25             # random questions for the owner's spot check (seeded)
    python3 konkur_prep.py --selftest                # synthetic fixture only, temp folder, no real questions

Standard library + poppler's pdftoppm/pdftotext (brew install poppler). Crops use pdftoppm's own -x/-y/-W/-H, so
Pillow is not needed. A crop box is [x, y, w, h] in pixels of the page rendered at `dpi` (read them off
pages/<pdf>/page-NN.png in any image viewer).

Two-pass transcription (protocol.md §2): pass A and pass B are made independently (fresh context, B from a
re-render at 200 dpi, B never sees A). `diff` lists every field that differs after whitespace/digit folding;
each one is settled against the page image and written down in `notes`. Only then does a file go to questions/.
"""
import argparse
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

import kcore

FIXTURE = kcore.HERE / 'fixtures' / 'synthetic-exam.json'


def need(tool):
    if not shutil.which(tool):
        sys.exit(f'{tool} not found: brew install poppler')


def raw_pdfs():
    d = kcore.private_dir() / 'raw'
    pdfs = sorted(d.glob('*.pdf')) if d.exists() else []
    if not pdfs:
        sys.exit(f'no PDFs in {d} — put the official booklets and final keys there (prep-fa.md §2)')
    return pdfs


def cmd_render(args):
    need('pdftoppm')
    for pdf in raw_pdfs():
        out = kcore.private_dir() / 'pages' / pdf.stem
        out.mkdir(parents=True, exist_ok=True)
        subprocess.run(['pdftoppm', '-r', str(args.dpi), '-png', str(pdf), str(out / 'page')], check=True)
        print(f'{pdf.name}: {len(list(out.glob("page-*.png")))} pages → {out}')
    return 0


def cmd_text(args):
    need('pdftotext')
    for pdf in raw_pdfs():
        out = kcore.private_dir() / 'pages' / pdf.stem
        out.mkdir(parents=True, exist_ok=True)
        subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', str(pdf), str(out / 'text.txt')], check=True)
        n = len((out / 'text.txt').read_text(encoding='utf-8', errors='replace').strip())
        print(f'{pdf.name}: {n} characters of text layer' + (' (none: scanned pages, transcribe from images)'
                                                              if n < 200 else '') + f' → {out / "text.txt"}')
    return 0


def crop_one(crop, dest, pdf_dir=None):
    """Render one box of one page to dest (PNG) with pdftoppm."""
    pdf = Path(pdf_dir or kcore.private_dir() / 'raw') / crop['pdf']
    x, y, w, h = (int(v) for v in crop['box'])
    dest.parent.mkdir(parents=True, exist_ok=True)
    stem = str(dest)[:-4] if str(dest).endswith('.png') else str(dest)
    subprocess.run(['pdftoppm', '-r', str(crop.get('dpi', 150)), '-f', str(crop['page']), '-l', str(crop['page']),
                    '-x', str(x), '-y', str(y), '-W', str(w), '-H', str(h), '-png', '-singlefile', str(pdf), stem],
                   check=True)
    return Path(stem + '.png')


def cmd_crop(args):
    need('pdftoppm')
    path = Path(args.file)
    doc = json.loads(path.read_text(encoding='utf-8'))
    n = 0
    for q in doc['questions']:
        for f in q.get('figures', []):
            if 'crop' in f:
                crop_one(f['crop'], kcore.private_dir() / f['path'])
                n += 1
    print(f'{n} figure crops written under {kcore.private_dir() / "crops"}')
    return 0


def parse_ranges(spec):
    out = []
    for part in spec.split(','):
        subj, rng = part.split(':')
        a, b = (int(x) for x in rng.split('-'))
        if subj not in kcore.SUBJECTS:
            sys.exit(f'unknown subject {subj}; use {list(kcore.SUBJECTS)}')
        out += [(subj, n) for n in range(a, b + 1)]
    return out


def template(year, group, ranges):
    return {'exam': {'year': year, 'group': group, 'booklet': f'{year}-{group}.pdf (code …)',
                     'key_source': f'{year}-{group}-key.pdf (کلید نهایی)', 'key_version': 'final',
                     'transcribed_by': 'Claude, two passes + diff', 'checked_by_owner': None, 'notes': ''},
            'questions': [{'id': f'{year}-{group}-{n:03d}', 'year': year, 'group': group, 'subject': subj, 'number': n,
                           'stem': '', 'options': ['', '', '', ''], 'figures': [], 'key': [], 'key_status': 'final',
                           'notes': ''} for subj, n in ranges]}


def cmd_template(args):
    doc = template(args.year, args.group, parse_ranges(args.subjects))
    out = Path(args.out or kcore.private_dir() / 'drafts' / f'{args.year}-{args.group}.A.json')
    if out.exists() and not args.force:
        sys.exit(f'{out} exists (use --force)')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{len(doc["questions"])} empty questions → {out}')
    return 0


def cmd_validate(args):
    files = [Path(f) for f in args.files] or kcore.question_files()
    if not files:
        print(f'no question files in {kcore.private_dir() / "questions"}')
        return 1
    bad = 0
    for f in files:
        errs = kcore.validate_exam(json.loads(f.read_text(encoding='utf-8')))
        print(f'{"ok  " if not errs else "FAIL"} {f.name}' + ('' if not errs else f' ({len(errs)} problems)'))
        for e in errs[:40]:
            print('     ' + e)
        bad += bool(errs)
    return 1 if bad else 0


def norm(s):
    s = unicodedata.normalize('NFC', str(s)).translate(kcore.DIGITS)
    s = s.replace('ي', 'ی').replace('ك', 'ک').replace('‌', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def diff_docs(a, b):
    """Field-level differences between two transcriptions of the same exam."""
    out = []
    qa = {q['number']: q for q in a['questions']}
    qb = {q['number']: q for q in b['questions']}
    for n in sorted(set(qa) | set(qb)):
        if n not in qa or n not in qb:
            out.append((n, 'question', 'only in ' + ('A' if n in qa else 'B'), ''))
            continue
        x, y = qa[n], qb[n]
        for k in ('subject', 'stem', 'key', 'key_status'):
            if norm(x.get(k)) != norm(y.get(k)):
                out.append((n, k, x.get(k), y.get(k)))
        for i in range(4):
            ox, oy = (x.get('options') or [''] * 4)[i:i + 1], (y.get('options') or [''] * 4)[i:i + 1]
            if norm(ox) != norm(oy):
                out.append((n, f'option {i + 1}', ox[0] if ox else '', oy[0] if oy else ''))
        if len(x.get('figures', [])) != len(y.get('figures', [])):
            out.append((n, 'figures', len(x.get('figures', [])), len(y.get('figures', []))))
    return out


def cmd_diff(args):
    a, b = (json.loads(Path(p).read_text(encoding='utf-8')) for p in (args.a, args.b))
    d = diff_docs(a, b)
    for n, field, x, y in d:
        print(f'Q{n:>4} {field:10} A: {str(x)[:90]}\n{"":16}B: {str(y)[:90]}')
    print(f'{len(d)} differences in {len(a["questions"])} questions' + (' — settle each against the page image, '
                                                                       'note it, then diff again' if d else ''))
    return 1 if d else 0


def apply_keys(doc, text):
    keys = {}
    for line in text.splitlines():
        line = line.split('#')[0].translate(kcore.DIGITS).strip()
        if not line:
            continue
        parts = re.split(r'[\s,;:]+', line)
        n, rest = int(parts[0]), parts[1:]
        keys[n] = 'cancelled' if rest and rest[0].lower() in ('x', 'cancelled', 'حذف') else [int(v) for v in rest]
    missing = []
    for q in doc['questions']:
        k = keys.get(q['number'])
        if k is None:
            missing.append(q['number'])
        elif k == 'cancelled':
            q['key'], q['key_status'] = None, 'cancelled'
        else:
            q['key'], q['key_status'] = k, 'final'
    return missing


def cmd_keys(args):
    path = Path(args.file)
    doc = json.loads(path.read_text(encoding='utf-8'))
    missing = apply_keys(doc, Path(args.keys).read_text(encoding='utf-8'))
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'keys applied to {path.name}' + (f'; no key for {missing}' if missing else ''))
    return 1 if missing else 0


def cmd_sample(args):
    qs = kcore.load_exams(kcore.question_files())
    rng = random.Random(args.seed)
    for q in sorted(rng.sample(qs, min(args.n, len(qs))), key=lambda q: q['id']):
        print(f'{q["id"]}  ({kcore.SUBJECTS[q["subject"]]})  check stem, 4 options, figure and key against the page')
    return 0


# ── synthetic fixture (no real questions anywhere) ──────────────────────────────────────────────
def tiny_pdf(path):
    """A one-page PDF (A4) with a grey box and the word SYNTHETIC, written by hand (stdlib only)."""
    stream = b'0.6 g 100 500 300 200 re f 0 g BT /F1 28 Tf 120 590 Td (SYNTHETIC) Tj ET'
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R '
            b'/Resources << /Font << /F1 5 0 R >> >> >>',
            b'<< /Length %d >>\nstream\n' % len(stream) + stream + b'\nendstream',
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    out, offs = bytearray(b'%PDF-1.4\n'), []
    for i, o in enumerate(objs, 1):
        offs.append(len(out))
        out += b'%d 0 obj\n' % i + o + b'\nendobj\n'
    xref = len(out)
    out += b'xref\n0 %d\n0000000000 65535 f \n' % (len(objs) + 1) + b''.join(b'%010d 00000 n \n' % o for o in offs)
    out += b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objs) + 1, xref)
    Path(path).write_bytes(bytes(out))


def synthetic(years=kcore.YEARS, groups=('tajrobi', 'riazi'), per_subject=5, seed=7):
    """Made-up arithmetic questions shaped like Konkur files, for mock runs and the live page. ILLUSTRATIVE."""
    rng = random.Random(seed)
    subjects = {'tajrobi': ('bio', 'chem', 'phys', 'math'), 'riazi': ('math', 'phys', 'chem')}
    docs = []
    for y in years:
        for g in groups:
            qs, n = [], 100
            for s in subjects[g]:
                for _ in range(per_subject):
                    n += 1
                    a, b = rng.randint(2, 40), rng.randint(2, 40)
                    right = a + b
                    opts = [right, right + 1, right - 1, right + 10]
                    rng.shuffle(opts)
                    qs.append({'id': f'{y}-{g}-{n:03d}', 'year': y, 'group': g, 'subject': s, 'number': n,
                               'stem': f'[SYNTHETIC] حاصل ${a} + {b}$ چند است؟', 'options': [str(o) for o in opts],
                               'figures': [], 'key': [opts.index(right) + 1], 'key_status': 'final', 'notes': ''})
            docs.append({'exam': {'year': y, 'group': g, 'booklet': 'SYNTHETIC', 'key_source': 'SYNTHETIC',
                                  'synthetic': True}, 'questions': qs})
    return docs


def selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f'{"ok  " if cond else "FAIL"} {name}')

    check('kcore self-check (parsing, −1/3 scoring, intervals)', kcore.selfcheck())
    fx = json.loads(FIXTURE.read_text(encoding='utf-8'))
    check('fixture is marked synthetic', fx['exam'].get('synthetic') is True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        kcore.os.environ['KONKUR_PRIVATE'] = str(tmp)
        try:
            check('fixture fails validation while its figure file is missing',
                  any('figure file not found' in e for e in kcore.validate_exam(fx)))
            (tmp / 'raw').mkdir()
            tiny_pdf(tmp / 'raw' / 'synthetic.pdf')
            if shutil.which('pdftoppm'):
                subprocess.run(['pdftoppm', '-r', '72', '-png', str(tmp / 'raw/synthetic.pdf'), str(tmp / 'page')],
                               check=True)
                check('pdftoppm renders the hand-written PDF', any(tmp.glob('page*.png')))
                fig = fx['questions'][2]['figures'][0]
                png = crop_one(fig['crop'], tmp / fig['path'])
                check('crop box → PNG (pdftoppm -x -y -W -H)', png.exists() and png.read_bytes()[:4] == b'\x89PNG')
            else:
                print('skip pdftoppm checks (poppler not installed)')
                (tmp / fx['questions'][2]['figures'][0]['path']).parent.mkdir(parents=True)
                (tmp / fx['questions'][2]['figures'][0]['path']).write_bytes(b'\x89PNG')
            check('fixture validates once the crop exists', kcore.validate_exam(fx) == [])
            bad = json.loads(json.dumps(fx))
            bad['questions'][0]['options'] = ['a', 'b', 'c']
            bad['questions'][1]['key'] = [5]
            bad['questions'][3]['number'] = bad['questions'][0]['number']
            errs = kcore.validate_exam(bad)
            check('validator catches 3 options, key 5 and a duplicate number',
                  any('4 non-empty' in e for e in errs) and any('accepted options' in e for e in errs)
                  and any('duplicate number' in e for e in errs))
            b = json.loads(json.dumps(fx))
            b['questions'][0]['stem'] = b['questions'][0]['stem'].replace('۲', '2') + '  '
            b['questions'][1]['options'][2] = 'چیز دیگری'
            d = diff_docs(fx, b)
            check('diff ignores digit/space folding, flags a changed option', [x[:2] for x in d] == [(2, 'option 3')])
            missing = apply_keys(b, '1 3\n2 ۴\n# comment\n3 x\n')
            check('keys: Persian digits, cancelled, missing reported',
                  b['questions'][1]['key'] == [4] and b['questions'][2]['key_status'] == 'cancelled'
                  and missing == [4, 5, 6])
            t = template(1405, 'riazi', parse_ranges('math:101-103,phys:104-104'))
            check('template has 4 empty questions that do not validate yet',
                  len(t['questions']) == 4 and kcore.validate_exam(t, check_files=False))
            syn = synthetic(per_subject=2)
            check('synthetic exams validate (6 files)', len(syn) == 6 and all(kcore.validate_exam(s) == [] for s in syn))
            check('prompt shows Persian option numbers and the figure note',
                  '۱) ' in kcore.prompt_for(fx['questions'][2]) and 'تصویر پیوست' in kcore.prompt_for(fx['questions'][2]))
        finally:
            kcore.os.environ.pop('KONKUR_PRIVATE', None)
    print('konkur_prep selftest ' + ('passed' if ok else 'FAILED'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--selftest', action='store_true')
    sub = ap.add_subparsers(dest='cmd')
    s = sub.add_parser('render')
    s.add_argument('--dpi', type=int, default=150)
    sub.add_parser('text')
    s = sub.add_parser('template')
    s.add_argument('year', type=int, choices=kcore.YEARS)
    s.add_argument('group', choices=list(kcore.GROUPS))
    s.add_argument('--subjects', required=True, help='bio:101-150,phys:151-185,…  (booklet numbers)')
    s.add_argument('--out')
    s.add_argument('--force', action='store_true')
    s = sub.add_parser('crop')
    s.add_argument('file')
    s = sub.add_parser('validate')
    s.add_argument('files', nargs='*')
    s = sub.add_parser('diff')
    s.add_argument('a')
    s.add_argument('b')
    s = sub.add_parser('keys')
    s.add_argument('file')
    s.add_argument('keys')
    s = sub.add_parser('sample')
    s.add_argument('--n', type=int, default=25)
    s.add_argument('--seed', type=int, default=1405)
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    cmds = {'render': cmd_render, 'text': cmd_text, 'template': cmd_template, 'crop': cmd_crop,
            'validate': cmd_validate, 'diff': cmd_diff, 'keys': cmd_keys, 'sample': cmd_sample}
    if args.cmd not in cmds:
        ap.print_help()
        return 0
    return cmds[args.cmd](args)


if __name__ == '__main__':
    sys.exit(main())
