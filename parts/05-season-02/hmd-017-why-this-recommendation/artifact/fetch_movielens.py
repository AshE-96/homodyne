#!/usr/bin/env python3
"""Download MovieLens "ml-latest-small" from GroupLens and verify it.

The data is NOT committed to this repository. GroupLens allows
redistribution only under its own licence terms (non-commercial use,
acknowledgement, no implied endorsement), so every viewer fetches the
original file from GroupLens instead:

    python3 fetch_movielens.py            # -> ./data/ml-latest-small/

Licence: https://files.grouplens.org/datasets/movielens/ml-latest-small-README.html
Cite:    F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets:
         History and Context. ACM TiiS 5(4): 19:1-19:19. doi:10.1145/2827872

Standard library only.
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
# Checked on 13 Nov 2026. The MD5 matches GroupLens's own ml-latest-small.zip.md5.
SHA256 = "696d65a3dfceac7c45750ad32df2c259311949efec81f0f144fdfb91ebc9e436"
MD5 = "31a303aabbc519bd33d025e44d6c2570"
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"


def main() -> int:
    DATA.mkdir(exist_ok=True)
    zpath = DATA / "ml-latest-small.zip"
    if not zpath.exists():
        print(f"downloading {URL}")
        urllib.request.urlretrieve(URL, zpath)
    blob = zpath.read_bytes()
    sha, md5 = hashlib.sha256(blob).hexdigest(), hashlib.md5(blob).hexdigest()
    if sha != SHA256 or md5 != MD5:
        print(f"checksum mismatch:\n  sha256 {sha}\n  md5    {md5}\n"
              "GroupLens may have replaced the file. Results will differ from the episode.")
        return 1
    with zipfile.ZipFile(zpath) as z:
        for name in z.namelist():  # refuse paths that escape the data folder
            if name.startswith("/") or ".." in Path(name).parts:
                print(f"refusing suspicious path in zip: {name}")
                return 1
        z.extractall(DATA)
    print(f"ok  sha256 {sha[:16]}…  ->  {DATA / 'ml-latest-small'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
