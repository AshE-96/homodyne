#!/usr/bin/env python3
"""Homodyne HMD-B07 - photo geolocation lab.

What it does
  strip     Reads your own JPEG photos, saves the true GPS position from EXIF to
            truth.csv, and writes clean copies with every metadata segment
            (EXIF, XMP, IPTC, comments) removed. These clean copies are what
            you give to the AI models.
  prompt    Prints the one prompt every model gets, so the test is fair.
  score     Reads truth.csv and guesses.csv, computes the distance error of
            every guess (haversine, km), and reports per model and mask level:
            median error with a bootstrap 90% interval, and the share of guesses
            within 1 / 25 / 200 / 750 / 2500 km (street / city / region /
            country / continent, the radii used by PIGEON, CVPR 2024).
  selftest  Checks the EXIF reader, the stripper and the distance maths on
            synthetic data. Writes nothing.

Privacy
  truth.csv holds real coordinates of where you stood. By default everything is
  written to private/geo-lab/ at the repo root, which git ignores. results.md
  reports errors only, never coordinates. Use photos taken away from home and
  without people in them.

What it is NOT
  It does not call any AI service. You paste each clean photo into each model
  with the same prompt and type its answer into guesses.csv. A small sample of
  one person's photos shows what happened to those photos, not a model's
  accuracy in general.

Standard library only. Python 3.9+. JPEG only (export HEIC as JPEG first).
  python3 geo_lab.py strip ~/Pictures/geo-test        # -> private/geo-lab/
  python3 geo_lab.py prompt
  python3 geo_lab.py score                            # reads private/geo-lab/
  python3 geo_lab.py selftest
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import struct
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT/'private'/'geo-lab'
RADII = [1, 25, 200, 750, 2500]  # km
EARTH_KM = 6371.0088
DROP = {0xE1, 0xED, 0xFE} | set(range(0xE3, 0xED)) | {0xEE, 0xEF}  # APP1, APP13, COM, APP3-12, APP14-15
PROMPT = """Where was this photo taken? Look only at the image.
Answer with your single best guess as decimal latitude and longitude,
then one line on the clues you used. Format:
LAT, LON
clues: ..."""


def haversine(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*EARTH_KM*math.asin(math.sqrt(a))


# ── JPEG / EXIF ────────────────────────────────────────────────────────────

def segments(data: bytes):
    """Yield (marker, start, end) for each segment before the image data."""
    if data[:2] != b'\xff\xd8':
        raise ValueError('not a JPEG')
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            raise ValueError(f'bad marker at {i}')
        marker = data[i+1]
        if marker == 0xDA:  # start of scan: the rest is image data
            yield marker, i, len(data)
            return
        length = struct.unpack('>H', data[i+2:i+4])[0]
        yield marker, i, i + 2 + length
        i += 2 + length


def gps_from_exif(data: bytes):
    """Return (lat, lon) from the EXIF GPS block, or None."""
    for marker, start, end in segments(data):
        body = data[start+4:end]
        if marker == 0xE1 and body[:6] == b'Exif\x00\x00':
            return _gps_from_tiff(body[6:])
    return None


def _gps_from_tiff(t: bytes):
    order = '<' if t[:2] == b'II' else '>'
    u16 = lambda o: struct.unpack(order + 'H', t[o:o+2])[0]
    u32 = lambda o: struct.unpack(order + 'I', t[o:o+4])[0]

    def ifd(offset):
        tags = {}
        for k in range(u16(offset)):
            e = offset + 2 + 12*k
            tags[u16(e)] = (u16(e+2), u32(e+4), e + 8)
        return tags

    gps_ptr = ifd(u32(4)).get(0x8825)
    if not gps_ptr:
        return None
    gps = ifd(u32(gps_ptr[2]))

    def ref(tag):
        return chr(t[gps[tag][2]]) if tag in gps else None

    def dms(tag):
        _, count, field = gps[tag]
        off = u32(field)
        nums = [u32(off + 8*j) / (u32(off + 8*j + 4) or 1) for j in range(count)]
        return nums[0] + nums[1]/60 + nums[2]/3600

    if not all(k in gps for k in (1, 2, 3, 4)):
        return None
    lat, lon = dms(2), dms(4)
    return (-lat if ref(1) == 'S' else lat, -lon if ref(3) == 'W' else lon)


def strip(data: bytes) -> bytes:
    """Copy a JPEG without its metadata segments."""
    out = bytearray(b'\xff\xd8')
    for marker, start, end in segments(data):
        if marker not in DROP:
            out += data[start:end]
    return bytes(out)


# ── commands ───────────────────────────────────────────────────────────────

def cmd_strip(args):
    out = Path(args.out)
    (out/'clean').mkdir(parents=True, exist_ok=True)
    truth = out/'truth.csv'
    new = not truth.exists()
    taken = 0 if new else sum(1 for _ in csv.DictReader(truth.open()))
    rows, skipped = [], []
    for path in sorted(p for p in Path(args.folder).iterdir() if p.suffix.lower() in ('.jpg', '.jpeg')):
        data = path.read_bytes()
        pos = gps_from_exif(data)
        if not pos:
            skipped.append(path.name)
            continue
        photo = f'p{taken + len(rows) + 1:02d}'
        (out/'clean'/f'{photo}.jpg').write_bytes(strip(data))
        rows.append({'photo': photo, 'set': args.set, 'lat': f'{pos[0]:.6f}', 'lon': f'{pos[1]:.6f}',
                     'source': path.name})
    with truth.open('a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['photo', 'set', 'lat', 'lon', 'source'])
        if new:
            w.writeheader()
        w.writerows(rows)
    guesses = out/'guesses.csv'
    if not guesses.exists():
        guesses.write_text('photo,model,mask,lat,lon\n')
    print(f'{len(rows)} photos -> {out/"clean"}  (truth in {truth})')
    if skipped:
        print('no GPS in EXIF, skipped:', ', '.join(skipped))
    print('Check: the clean copies must show no location in your photo viewer before you upload them.')


def bootstrap_median(errors, reps=2000, seed=2026):
    rng = random.Random(seed)
    meds = sorted(statistics.median(rng.choices(errors, k=len(errors))) for _ in range(reps))
    return meds[int(0.05*reps)], meds[int(0.95*reps)]


def summarise(errors):
    lo, hi = bootstrap_median(errors)
    return {'n': len(errors), 'median_km': statistics.median(errors), 'ci90_km': [lo, hi],
            'within': {f'{r}km': sum(e <= r for e in errors)/len(errors) for r in RADII}}


def cmd_score(args):
    out = Path(args.out)
    truth = {r['photo']: r for r in csv.DictReader((out/'truth.csv').open())}
    groups = {}
    for g in csv.DictReader((out/'guesses.csv').open()):
        t = truth[g['photo']]
        err = haversine(float(t['lat']), float(t['lon']), float(g['lat']), float(g['lon']))
        for key in ((g['model'], g['mask'], t['set']), (g['model'], g['mask'], 'all')):
            groups.setdefault(key, []).append(err)
    results = [{'model': m, 'mask': k, 'set': s, **summarise(e)} for (m, k, s), e in sorted(groups.items())]
    head = '| model | mask | set | n | median km (90% CI) | ' + ' | '.join(f'≤{r} km' for r in RADII) + ' |'
    lines = ['# HMD-B07 geolocation results', '', 'Errors only; no coordinates.', '', head,
             '|' + '---|'*(5 + len(RADII))]
    for r in results:
        ci = r['ci90_km']
        lines.append(f"| {r['model']} | {r['mask']} | {r['set']} | {r['n']} | "
                     f"{r['median_km']:.1f} ({ci[0]:.1f}-{ci[1]:.1f}) | "
                     + ' | '.join(f"{v:.0%}" for v in r['within'].values()) + ' |')
    (out/'results.md').write_text('\n'.join(lines) + '\n')
    (out/'results.json').write_text(json.dumps(results, indent=1))
    print('\n'.join(lines))


def _fake_jpeg(lat, lon):
    """SOI + APP0 + APP1(EXIF with GPS) + COM + SOS + EOI, little-endian TIFF."""
    def rat(v):
        d = int(v); m = int((v - d)*60); s = round(((v - d)*60 - m)*60*10000)
        return struct.pack('<6I', d, 1, m, 1, s, 10000)
    # TIFF: header(8) + IFD0 (1 entry: GPS pointer) at 8 -> 8+2+12+4 = 26; GPS IFD at 26 (4 entries)
    gps_ifd = 26
    data_off = gps_ifd + 2 + 4*12 + 4
    tiff = b'II*\x00' + struct.pack('<I', 8)
    tiff += struct.pack('<H', 1) + struct.pack('<HHII', 0x8825, 4, 1, gps_ifd) + struct.pack('<I', 0)
    entries = [(1, 2, 2, b'S' if lat < 0 else b'N'), (2, 5, 3, data_off),
               (3, 2, 2, b'W' if lon < 0 else b'E'), (4, 5, 3, data_off + 24)]
    tiff += struct.pack('<H', 4)
    for tag, typ, count, val in entries:
        v = val.ljust(4, b'\x00') if isinstance(val, bytes) else struct.pack('<I', val)
        tiff += struct.pack('<HHI', tag, typ, count) + v
    tiff += struct.pack('<I', 0) + rat(abs(lat)) + rat(abs(lon))
    app1 = b'Exif\x00\x00' + tiff
    seg = lambda m, body: bytes([0xFF, m]) + struct.pack('>H', len(body) + 2) + body
    return (b'\xff\xd8' + seg(0xE0, b'JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00')
            + seg(0xE1, app1) + seg(0xFE, b'taken at home') + b'\xff\xda\x00\x02' + b'\x12\x34' + b'\xff\xd9')


def cmd_selftest(_args):
    tehran, shiraz = (35.6892, 51.3890), (29.5918, 52.5837)
    d = haversine(*tehran, *shiraz)
    assert 670 < d < 700, d
    assert haversine(0, 0, 0, 180) - math.pi*EARTH_KM < 1e-6
    jpg = _fake_jpeg(-33.8568, 151.2153)
    lat, lon = gps_from_exif(jpg)
    assert abs(lat + 33.8568) < 1e-4 and abs(lon - 151.2153) < 1e-4, (lat, lon)
    clean = strip(jpg)
    assert gps_from_exif(clean) is None and b'Exif' not in clean and b'taken at home' not in clean
    assert clean.endswith(b'\xff\xd9') and b'JFIF' in clean
    s = summarise([0.5, 3, 20, 150, 900])
    assert s['median_km'] == 20 and s['within']['25km'] == 0.6
    with tempfile.TemporaryDirectory() as tmp:  # end to end: strip two batches, score one guess each
        src, out = Path(tmp)/'photos', Path(tmp)/'lab'
        src.mkdir()
        (src/'a.jpg').write_bytes(_fake_jpeg(*tehran))
        cmd_strip(argparse.Namespace(folder=src, set='iran', out=out))
        (src/'a.jpg').write_bytes(_fake_jpeg(*shiraz))
        cmd_strip(argparse.Namespace(folder=src, set='abroad', out=out))
        with (out/'guesses.csv').open('a') as f:
            f.write(f'p01,test,L0,{tehran[0]},{tehran[1]}\np02,test,L0,{tehran[0]},{tehran[1]}\n')
        cmd_score(argparse.Namespace(out=out))
        rows = json.loads((out/'results.json').read_text())
        both = next(r for r in rows if r['set'] == 'all')
        assert both['n'] == 2 and both['within']['1km'] == 0.5, both
    print(f'\nok: Tehran-Shiraz {d:.0f} km; EXIF GPS read and removed; strip -> score end to end')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('strip', help='save true GPS and write metadata-free copies')
    s.add_argument('folder')
    s.add_argument('--set', default='iran', help='label for this batch, e.g. iran or abroad')
    s.add_argument('--out', default=str(OUT))
    sub.add_parser('prompt', help='print the prompt every model gets')
    sc = sub.add_parser('score', help='score guesses.csv against truth.csv')
    sc.add_argument('--out', default=str(OUT))
    sub.add_parser('selftest', help='check the maths and the EXIF code')
    args = ap.parse_args()
    {'strip': cmd_strip, 'prompt': lambda a: print(PROMPT), 'score': cmd_score,
     'selftest': cmd_selftest}[args.cmd](args)


if __name__ == '__main__':
    sys.exit(main())
