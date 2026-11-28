#!/usr/bin/env python3
"""chalus_prep.py · HMD-S07 · turn the owner's 141.ir traffic-counter export into the common hourly table. Stdlib only.

    python3 -I artifact/chalus_prep.py --inspect artifact/data/raw/*.xlsx      # show which columns were recognised; writes nothing
    python3 -I artifact/chalus_prep.py artifact/data/raw/*.xlsx                # → artifact/data/chalus_hourly.csv (git-ignored)
    python3 -I artifact/chalus_prep.py raw/a.csv=N raw/b.csv=S                 # a file without a counter-code column: say its direction
    python3 -I artifact/chalus_prep.py --map '{"total": "my count column"}' raw/*.csv     # rename a column we did not recognise

The 141 export format is NOT known to us (the page is behind the owner's login). [VERIFY] on the first download.
ASSUMED, from older public RMTO hourly Excel files as we remember them (one row per counter per hour):
    کد محور · نام محور · زمان شروع · زمان پایان · مدت زمان کارکرد (دقیقه) · تعداد کل وسیله نقلیه ·
    تعداد وسیله نقلیه کلاس ۱ … کلاس ۵ · سرعت متوسط · تعداد تخلف سرعت غیر مجاز · تعداد تخلف فاصله غیر مجاز ·
    تعداد تخلف سبقت غیر مجاز · تعداد برآورد شده
with times like «۱۴۰۴/۰۱/۰۱ ۰۰:۰۰» (Jalali, sometimes Persian digits). The reader is tolerant on purpose:
  · headers: Arabic ي/ك or Persian ی/ک, spaces, ZWNJ, digits in any script, English names — all normalised;
  · times: one start-time column, or separate date + hour columns; Jalali (year < 1700) or Gregorian; Excel serials;
  · intervals shorter than an hour (5/15 min) are summed to hours, speed weighted by count; an hour with fewer than
    45 operating minutes gets no count; identical rows from overlapping downloads are counted once;
  · one counter (one code) per direction: use --only CODE,CODE when the export holds several places;
  · files: .csv/.tsv/.txt (UTF-8 or Windows-1256) and .xlsx (first sheet). Old .xls or .rar: open and save as .xlsx first.
Direction comes from artifact/counters.csv (counter code → N or S), or from `file=N` on the command line.
Police one-way hours come from artifact/closures.csv (announcements) and from a heuristic (chalus_core.detect_closures).
"""
import argparse
import csv
import datetime as dt
import io
import json
import math
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chalus_core as cc  # noqa: E402

OUT = HERE / 'data' / 'chalus_hourly.csv'
DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')


def norm(h):
    """Header → comparable key: Persian letters, ASCII digits, no spaces/ZWNJ/punctuation, lower case."""
    h = (h or '').translate(DIGITS).replace('ي', 'ی').replace('ك', 'ک').replace('ة', 'ه').replace('أ', 'ا').replace('إ', 'ا')
    return re.sub(r'[\s‌‏‎_\-–.:()\[\]/]+', '', h).lower()


# canonical name → normalised aliases (first match wins). Persian forms are our assumption ([VERIFY]).
ALIASES = {
    'code': ['کدمحور', 'کدترددشمار', 'کددستگاه', 'کدایستگاه', 'کد', 'code', 'axiscode', 'countercode', 'sitecode', 'stationcode'],
    'name': ['ناممحور', 'نامترددشمار', 'نامایستگاه', 'محور', 'name', 'axisname', 'sitename'],
    'start': ['زمانشروع', 'تاریخوزمانشروع', 'تاریخوساعتشروع', 'شروع', 'ازساعت', 'starttime', 'start', 'from', 'datetime', 'timestamp'],
    'end': ['زمانپایان', 'تاریخوزمانپایان', 'پایان', 'تاساعت', 'endtime', 'end', 'to'],
    'date': ['تاریخ', 'روز', 'date', 'day'],
    'hour': ['ساعت', 'hour', 'hr'],
    'minutes': ['مدتزمانکارکرددقیقه', 'مدتزمانکارکرد', 'مدتکارکرد', 'زمانکارکرد', 'operatingminutes', 'minutes', 'uptime'],
    'total': ['تعدادکلوسیلهنقلیه', 'تعدادکلوسایلنقلیه', 'تعدادکل', 'کلتردد', 'حجمتردد', 'تردد', 'total', 'totalvehicles', 'volume', 'count'],
    'speed': ['سرعتمتوسط', 'میانگینسرعت', 'متوسطسرعت', 'سرعت', 'avgspeed', 'meanspeed', 'averagespeed', 'speed'],
    'estimated': ['تعدادبرآوردشده', 'برآوردشده', 'تعدادبراوردشده', 'estimated', 'estimatedcount'],
    'speeding': ['تعدادتخلفسرعتغیرمجاز', 'تخلفسرعت', 'speeding'],
    'headway': ['تعدادتخلففاصلهغیرمجاز', 'تخلففاصله', 'فاصلهکمتراز2ثانیه', 'headway'],
}
for k in range(1, 6):
    ALIASES['class%d' % k] = ['تعدادوسیلهنقلیهکلاس%d' % k, 'تعدادوسایلنقلیهکلاس%d' % k, 'کلاس%d' % k, 'رده%d' % k, 'class%d' % k]


def map_columns(headers, override=None):
    """{canonical: original header}. An override {'total': 'my column'} wins."""
    keys = {norm(h): h for h in headers}
    found = {}
    for canon, alias in ALIASES.items():
        for a in alias:
            hit = next((orig for k, orig in keys.items() if k == a), None)
            if hit and hit not in found.values():
                found[canon] = hit
                break
    for canon, orig in (override or {}).items():
        found[canon] = orig
    return found


# ── readers ───────────────────────────────────────────────────────────────────────────────────────────────────
def read_table(path):
    """List of row dicts from .csv/.tsv/.txt or .xlsx."""
    p = Path(path)
    suf = p.suffix.lower()
    if suf in ('.xls', '.rar', '.zip'):
        raise SystemExit(f'{p.name}: {suf} is not read here. Open it in Excel or LibreOffice and save as .xlsx or .csv.')
    if suf == '.xlsx':
        return read_xlsx(p)
    raw = p.read_bytes()
    for enc in ('utf-8-sig', 'cp1256'):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise SystemExit(f'{p.name}: neither UTF-8 nor Windows-1256')
    if text.lstrip().startswith('# SYNTHETIC'):
        raise SystemExit(f'{p.name} is the SYNTHETIC fixture; it is already in the hourly format and must never be passed off as 141 data.')
    dialect = csv.Sniffer().sniff(text[:4096], delimiters=',;\t|')
    return list(csv.DictReader(io.StringIO(text), dialect=dialect))


def read_xlsx(path):
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', ns):
                shared.append(''.join(t.text or '' for t in si.iter('{%s}t' % ns['m'])))
        sheets = sorted(n for n in z.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml', n))
        root = ET.fromstring(z.read(sheets[0]))
    table = []
    for row in root.iter('{%s}row' % ns['m']):
        cells = {}
        for c in row.findall('m:c', ns):
            col = re.match(r'[A-Z]+', c.get('r', 'A')).group(0)
            idx = 0
            for ch in col:
                idx = idx * 26 + ord(ch) - 64
            t, v = c.get('t'), c.find('m:v', ns)
            if t == 's' and v is not None:
                val = shared[int(v.text)]
            elif t == 'inlineStr':
                val = ''.join(x.text or '' for x in c.iter('{%s}t' % ns['m']))
            else:
                val = v.text if v is not None else ''
            cells[idx - 1] = val
        if cells:
            table.append([cells.get(i, '') for i in range(max(cells) + 1)])
    if not table:
        return []
    head = [str(h) for h in table[0]]
    return [dict(zip(head, r + [''] * (len(head) - len(r)))) for r in table[1:]]


# ── values ────────────────────────────────────────────────────────────────────────────────────────────────────
def num(x):
    if x is None:
        return None
    s = str(x).translate(DIGITS).replace('٫', '.').replace('٬', '').replace(',', '').strip()
    try:
        v = float(s)
    except ValueError:
        return None
    return v if math.isfinite(v) else None                          # 'NaN' / 'inf' cells are missing, not numbers


PM = re.compile(r'(pm|p\.m\.|ب\.?\s?ظ|بعدازظهر|بعد از ظهر|عصر|شب)', re.I)
AM = re.compile(r'(am|a\.m\.|ق\.?\s?ظ|قبل‌?ازظهر|قبل از ظهر|صبح)', re.I)


def _clock(text, hh, mm):
    """12-hour labels: '1:00 PM', '۰۱:۰۰ ب.ظ' → 13:00; '12:00 AM' → 00:00."""
    if hh <= 12 and PM.search(text) and hh != 12:
        hh += 12
    elif hh == 12 and AM.search(text):
        hh = 0
    return hh, mm


def parse_time(x, hour=None):
    """'1404/01/01 13:00', '2025-03-21 13:15:00', '21/03/2025 13:00', Excel serial 45737.54, or a date plus a separate
    hour. Returns None for anything that is not a real date (e.g. 30 Esfand in a common year), never raises.
    Hour 24 (an hour-ending label) is read as 00:00 of the next day; if the file labels hours 1–24, check with --inspect."""
    if x is None or str(x).strip() == '':
        return None
    s = str(x).translate(DIGITS).strip()
    hh = mm = 0
    if re.fullmatch(r'\d{5}(\.\d+)?', s):                          # Excel serial date (Gregorian)
        t = dt.datetime(1899, 12, 30) + dt.timedelta(days=float(s), seconds=30)   # +30 s: 13:59:59.99 is 14:00
        day, hh, mm = t.date(), t.hour, t.minute
    else:
        m = re.match(r'(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})(?:[ T]+(\d{1,2})(?::(\d{2}))?(?::\d{2})?)?', s)
        m2 = None if m else re.match(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})(?:[ T]+(\d{1,2})(?::(\d{2}))?(?::\d{2})?)?', s)
        if m:
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            hh, mm = int(m.group(4) or 0), int(m.group(5) or 0)
        elif m2:                                                        # 21/03/2025 13:00 (day first)
            y, mo, d = int(m2.group(3)), int(m2.group(2)), int(m2.group(1))
            hh, mm = int(m2.group(4) or 0), int(m2.group(5) or 0)
        else:
            return None
        hh, mm = _clock(s, hh, mm)
        try:
            if y < 1700:                                                # Jalali
                if not (1 <= mo <= 12 and 1 <= d <= (31 if mo <= 6 else 30 if mo <= 11 else 29 + cc.is_leap(y))):
                    return None
                day = cc.j2g(y, mo, d)
            else:
                day = dt.date(y, mo, d)
        except ValueError:
            return None
    if hour is not None:
        hs = str(hour).translate(DIGITS).strip()
        mh = re.match(r'(\d{1,2})(?::(\d{2}))?', hs)
        if mh:
            hh, mm = _clock(hs, int(mh.group(1)), int(mh.group(2) or 0))
    if hh == 24 and mm == 0:
        day, hh = day + dt.timedelta(days=1), 0
    if not (0 <= hh <= 23 and 0 <= mm <= 59):
        return None
    return dt.datetime.combine(day, dt.time(hh, mm))


def load_counters(path=HERE / 'counters.csv'):
    if not Path(path).exists():
        return {}
    rows = csv.DictReader(line for line in open(path, encoding='utf-8') if not line.startswith('#'))
    return {norm(r['code']): r['dir'].strip().upper() for r in rows if r.get('code', '').strip() and r.get('dir', '').strip()}


def load_closures(path=HERE / 'closures.csv'):
    """Police announcements → {(date, hour, dir)}. Columns: date (Gregorian), from_hour, to_hour (exclusive), closed_dir."""
    out = set()
    if not Path(path).exists():
        return out
    for r in csv.DictReader(line for line in open(path, encoding='utf-8') if not line.startswith('#')):
        if not r.get('date', '').strip():
            continue
        d = dt.date.fromisoformat(r['date'].strip())
        a, b = int(r['from_hour']), int(r['to_hour'])
        for k in range(a, b if b > a else b + 24):
            out.add((d + dt.timedelta(days=k // 24), k % 24, r['closed_dir'].strip().upper()))
    return out


# ── the conversion ────────────────────────────────────────────────────────────────────────────────────────────
PARTIAL_MIN = 45      # an hour in which the counter worked fewer minutes than this has no usable count


def convert(files, override=None, counters=None, closures=None, inspect=False, only=None):
    """only: counter codes to keep. Without it, a direction fed by two or more codes is refused: summing two counters
    (e.g. Karaj end + Marzanabad) would double the count and mix two places into one series."""
    counters = load_counters() if counters is None else counters
    only = {norm(c) for c in only} if only else None
    seen, dup = set(), 0
    acc = defaultdict(lambda: dict(count=0.0, speed_w=0.0, speed_n=0.0, minutes=0.0, has_min=False, has_cls=False, est=0.0, heavy=0.0, n=0,
                                      codes=set(), src=set()))
    report = []
    for spec in files:
        path, _, forced = str(spec).partition('=')
        rows = read_table(path)
        if not rows:
            report.append(f'{Path(path).name}: empty')
            continue
        cols = map_columns(rows[0].keys(), override)
        missing = [c for c in ('total',) if c not in cols] + ([] if 'start' in cols or 'date' in cols else ['start or date'])
        unknown = [h for h in rows[0] if h not in cols.values()]
        report.append(f'{Path(path).name}: {len(rows)} rows · recognised {json.dumps(cols, ensure_ascii=False)}'
                      + (f' · not used {unknown}' if unknown else '') + (f' · MISSING {missing}' if missing else ''))
        if missing:
            continue
        skipped = 0
        for r in rows:
            t = parse_time(r.get(cols.get('start')) if 'start' in cols else r.get(cols['date']),
                           r.get(cols['hour']) if 'hour' in cols and 'start' not in cols else None)
            code = str(r.get(cols.get('code'), '') or '').translate(DIGITS).strip()
            code = code[:-2] if code.endswith('.0') else code                # a code cell Excel stored as a number
            if only is not None and norm(code) not in only:
                continue
            dirn = forced.upper() if forced else counters.get(norm(code))
            if t is None or dirn not in cc.DIRS:
                skipped += 1
                continue
            key = (code, dirn, t, r.get(cols['total']), r.get(cols.get('speed')))
            if key in seen:                                                  # the same row in two overlapping downloads
                dup += 1
                continue
            seen.add(key)
            a = acc[t.date(), t.hour, dirn]
            c = num(r.get(cols['total']))
            mins = num(r.get(cols['minutes'])) if 'minutes' in cols else None
            if c is not None and (mins is None or mins > 0):
                a['count'] += c
                a['n'] += 1
                s = num(r.get(cols['speed'])) if 'speed' in cols else None
                if s is not None and s > 0 and c > 0:
                    a['speed_w'] += s * c
                    a['speed_n'] += c
                if any('class%d' % k in cols for k in (3, 4, 5)):
                    a['heavy'] += sum(num(r.get(cols['class%d' % k])) or 0 for k in (3, 4, 5) if 'class%d' % k in cols)
                    a['has_cls'] = True
            if mins is not None:
                a['minutes'] += mins
                a['has_min'] = True
            if 'estimated' in cols:
                a['est'] += num(r.get(cols['estimated'])) or 0
            a['codes'].add(code)
            a['src'].add(Path(path).name)
        if skipped:
            report.append(f'  {skipped} rows skipped (no valid time, or no direction: add the counter code to counters.csv or use file=N)')
        if inspect:
            for r in rows[:3]:
                report.append('  sample ' + json.dumps({k: r.get(v) for k, v in cols.items()}, ensure_ascii=False))
    if dup:
        report.append(f'{dup} duplicate rows ignored (same counter, time and values in more than one file)')
    per_dir = defaultdict(set)
    for (d, h, dirn), a in acc.items():
        per_dir[dirn] |= a['codes']
    several = {x: sorted(c) for x, c in per_dir.items() if len(c) > 1}
    if several and inspect:
        report.append(f'NOTE more than one counter per direction {several}: the real run needs --only CODE,CODE')
    if several and not inspect:
        raise SystemExit(f'more than one counter per direction {several}: pick one place, e.g. --only 183120,183170 '
                         '(one code per direction). Run once per place if you want several.')
    out = []
    partial = 0
    shut = load_closures() if closures is None else closures
    for (d, h, dirn), a in sorted(acc.items()):
        short = a['has_min'] and a['minutes'] < PARTIAL_MIN
        partial += short
        out.append(dict(date=d, hour=h, dir=dirn, count=int(round(a['count'])) if a['n'] and not short else None,
                        speed=round(a['speed_w'] / a['speed_n'], 1) if a['speed_n'] else None,
                        closed=1 if (d, h, dirn) in shut else 0,
                        minutes=round(min(a['minutes'], 60)) if a['has_min'] else '',
                        estimated=int(a['est']), heavy_share=round(a['heavy'] / a['count'], 3) if a['count'] and a['has_cls'] else '',
                        codes='|'.join(sorted(a['codes'])), source='|'.join(sorted(a['src']))))
    if partial:
        report.append(f'{partial} hours with the counter working < {PARTIAL_MIN} min: count left empty (not a quiet hour)')
    return out, report


def write(rows, path=OUT):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ['date', 'jalali', 'hour', 'dir', 'count', 'speed', 'closed', 'minutes', 'estimated', 'heavy_share', 'codes', 'source']
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write('# HMD-S07 · hourly table from the owner\'s 141.ir export · made by chalus_prep.py · raw data: do not publish until the 141 terms allow it\n')
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({**r, 'date': r['date'].isoformat(), 'jalali': cc.jstr(r['date']),
                        'count': '' if r['count'] is None else r['count'], 'speed': '' if r['speed'] is None else r['speed']})


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('files', nargs='+', help='export files; add =N or =S if a file has no counter-code column')
    ap.add_argument('--inspect', action='store_true', help='report recognised columns and three sample rows; write nothing')
    ap.add_argument('--map', help='JSON {canonical: header} for columns we did not recognise (see ALIASES)')
    ap.add_argument('--only', help='comma-separated counter codes to keep (one per direction), e.g. 183120,183170')
    ap.add_argument('--out', type=Path, default=OUT)
    a = ap.parse_args()
    rows, report = convert(a.files, json.loads(a.map) if a.map else None, inspect=a.inspect,
                           only=a.only.split(',') if a.only else None)
    print('\n'.join(report))
    if a.inspect:
        return 0
    if not rows:
        print('no rows: run with --inspect and check the column names and counters.csv')
        return 1
    n_det = cc.detect_closures(rows)
    write(rows, a.out)
    days = sorted({r['date'] for r in rows})
    print(f'wrote {a.out} · {len(rows)} hour-rows · {days[0]} … {days[-1]} ({cc.jstr(days[0])} … {cc.jstr(days[-1])})'
          f' · police-table closed {sum(r["closed"] == 1 for r in rows)} · heuristic closed {n_det}'
          f' · no count {sum(r["count"] is None for r in rows)} · with estimated vehicles {sum(r["estimated"] > 0 for r in rows)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
