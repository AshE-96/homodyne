#!/usr/bin/env python3
"""Download the Deceptive Opinion Spam Corpus v1.4 (Ott et al. 2011, 2013) into artifact/data/.

    python3 fetch_data.py

The corpus is licensed CC BY-NC-SA 3.0 (see data/op_spam_v1.4/LICENSE after download).
It is NOT committed to this repository: every viewer downloads it from the authors' site.
If you use it, cite the two papers listed in README.md.

The script tries the authors' URL first and checks the SHA-256 of the archive. On
13 Nov 2026 that URL answered with a truncated file, so it falls back to the
Internet Archive copy of the same URL, which matches the checksum below.

Standard library only.
"""
import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / 'data'
SHA256 = 'e3a61b3709ccaca842aeec7f525e273988cf3b1bab35151712cf89759a6724fa'
URLS = [
    'https://myleott.com/op_spam_v1.4.zip',
    'https://web.archive.org/web/2024id_/https://myleott.com/op_spam_v1.4.zip',
]


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'homodyne-artifact/1.0'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main():
    target = DATA / 'op_spam_v1.4'
    if (target / 'README.md').exists():
        print(f'already there: {target.relative_to(HERE)}')
        return 0
    DATA.mkdir(exist_ok=True)
    zpath = DATA / 'op_spam_v1.4.zip'
    for url in URLS:
        try:
            blob = fetch(url)
        except Exception as e:  # network errors: try the next mirror
            print(f'  failed {url}: {e}')
            continue
        digest = hashlib.sha256(blob).hexdigest()
        if digest != SHA256:
            print(f'  {url}: checksum mismatch ({len(blob)} bytes) - trying the next source')
            continue
        zpath.write_bytes(blob)
        print(f'  ok {url} ({len(blob)} bytes, sha256 verified)')
        break
    else:
        print('Could not download a verified copy. Get op_spam_v1.4.zip by hand and put it in artifact/data/.')
        return 1
    with zipfile.ZipFile(zpath) as z:
        for name in z.namelist():
            if name.startswith('/') or '..' in Path(name).parts:
                raise SystemExit(f'refusing unsafe path in archive: {name}')
        z.extractall(DATA)
    n = len(list(target.glob('*/*/fold*/*.txt')))
    print(f'extracted {n} reviews to {target.relative_to(HERE)} (expected 1600)')
    print('Licence: CC BY-NC-SA 3.0 - non-commercial use, attribution, share-alike. Do not commit the data.')
    return 0 if n == 1600 else 1


if __name__ == '__main__':
    sys.exit(main())
