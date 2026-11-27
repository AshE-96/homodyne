#!/usr/bin/env python3
"""Homodyne HMD-009 - figures from the real TLC data (our rendering).

  python3 -I make_figures.py map --shp cache/zones/taxi_zones --out ../media/beat07_nyc_taxi_zones_midtown_jfk.png
        TLC taxi-zone map (NYC TLC shapefile, NY State Plane feet, drawn as is),
        Midtown zones 161/162/163/164/230 and JFK (132) in amber. Needs matplotlib.
  python3 make_figures.py svg [--csv derived/hourly_profile.csv]
        prints the inline SVG of the weekday hour-of-day chart used in deck beat 7
        (median and 10th-90th percentile band of Midtown -> JFK trip minutes). Stdlib only.
  python3 make_figures.py --selftest
"""
from __future__ import annotations

import argparse
import csv
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIDTOWN, JFK = {161, 162, 163, 164, 230}, {132}
AMBER, INK, LINE, PAPER = "#E8A33D", "#16181B", "#CFCAC0", "#F3F1EC"


# ---------------------------------------------------------------- minimal shapefile reader (polygons only)
def read_dbf_ids(path: Path, field="LocationID") -> list[int]:
    data = path.read_bytes()
    n, hlen, rlen = struct.unpack("<IHH", data[4:12])
    fields, off = [], 32
    while data[off] != 0x0D:
        name = data[off:off + 11].split(b"\0")[0].decode()
        fields.append((name, data[off + 16]))
        off += 32
    pos, start = 1, {}
    for name, length in fields:
        start[name] = (pos, length)
        pos += length
    p, ln = start[field]
    return [int(float(data[hlen + i * rlen + p: hlen + i * rlen + p + ln].strip() or 0)) for i in range(n)]


def read_polygons(path: Path) -> list[list[list[tuple[float, float]]]]:
    data = path.read_bytes()
    out, off = [], 100
    while off < len(data):
        _, clen = struct.unpack(">II", data[off:off + 8])
        rec = data[off + 8: off + 8 + 2 * clen]
        off += 8 + 2 * clen
        if struct.unpack("<i", rec[:4])[0] != 5:
            out.append([])
            continue
        nparts, npts = struct.unpack("<ii", rec[36:44])
        parts = list(struct.unpack(f"<{nparts}i", rec[44:44 + 4 * nparts])) + [npts]
        base = 44 + 4 * nparts
        pts = [struct.unpack("<dd", rec[base + 16 * i: base + 16 * i + 16]) for i in range(npts)]
        out.append([pts[parts[i]:parts[i + 1]] for i in range(nparts)])
    return out


def draw_map(shp_stem: Path, out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon

    ids = read_dbf_ids(shp_stem.with_suffix(".dbf"))
    polys = read_polygons(shp_stem.with_suffix(".shp"))
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    for zid, rings in zip(ids, polys):
        hot = zid in MIDTOWN or zid in JFK
        for ring in rings:
            ax.add_patch(Polygon(ring, closed=True, facecolor=AMBER if hot else "#E4E0D7",
                                 edgecolor=INK if hot else "#B9B3A7", linewidth=0.9 if hot else 0.4, zorder=3 if hot else 1))
    # frame Manhattan + Queens + JFK; NY State Plane feet
    ax.set_xlim(960000, 1068000)
    ax.set_ylim(160000, 232000)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(out, dpi=100, facecolor=PAPER)
    print(f"wrote {out}")


# ---------------------------------------------------------------- hour-of-day chart as inline SVG
def chart_svg(rows: list[dict], h0=2, h1=22, w=1300, h=420) -> str:
    rows = [r for r in rows if h0 <= int(r["weekday_departure_hour"]) <= h1]
    left, right, top, bottom = 90, 30, 20, 60
    ymax = 100.0
    x = lambda hr: left + (hr - h0) / (h1 - h0) * (w - left - right)
    y = lambda m: top + (1 - m / ymax) * (h - top - bottom)
    hrs = [int(r["weekday_departure_hour"]) for r in rows]
    p10 = [float(r["p10_min"]) for r in rows]
    p90 = [float(r["p90_min"]) for r in rows]
    med = [float(r["median_min"]) for r in rows]
    band = " ".join(f"{x(a):.0f},{y(b):.0f}" for a, b in zip(hrs, p90)) + " " + \
        " ".join(f"{x(a):.0f},{y(b):.0f}" for a, b in reversed(list(zip(hrs, p10))))
    line = " ".join(f"{x(a):.0f},{y(b):.0f}" for a, b in zip(hrs, med))
    out = [f'<svg class="chart hours" viewBox="0 0 {w} {h}" role="img" aria-label="Midtown to JFK taxi trip minutes by weekday departure hour">']
    for m in (0, 30, 60, 90):
        out.append(f'<line class="grid" x1="{left}" y1="{y(m):.0f}" x2="{w - right}" y2="{y(m):.0f}"/>'
                   f'<text class="ax" x="{left - 14}" y="{y(m) + 9:.0f}" text-anchor="end">{m}</text>')
    out.append(f'<polygon class="band" points="{band}"/>')
    out.append(f'<polyline class="med" points="{line}"/>')
    for hr in range(h0, h1 + 1, 2):
        out.append(f'<text class="ax" x="{x(hr):.0f}" y="{h - 18}" text-anchor="middle">{hr:02d}</text>')
    for hr in (3, 16):
        r = rows[hrs.index(hr)]
        mm = float(r["median_min"])
        out.append(f'<circle class="dot" cx="{x(hr):.0f}" cy="{y(mm):.0f}" r="10"/>')
    out.append("</svg>")
    return "\n".join(out)


def selftest() -> None:
    import tempfile
    rows = [{"weekday_departure_hour": str(hr), "p10_min": "20", "median_min": str(30 + hr), "p90_min": "60"} for hr in range(24)]
    s = chart_svg(rows)
    assert s.startswith("<svg") and s.endswith("</svg>") and s.count('class="dot"') == 2
    assert 'points="90,' in s  # the band starts at the left margin
    # a one-square polygon shapefile + dbf written by hand, then read back
    with tempfile.TemporaryDirectory() as d:
        ring = [(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)]
        rec = struct.pack("<i4d2i", 5, 0, 0, 1, 1, 1, 5) + struct.pack("<i", 0) + b"".join(struct.pack("<dd", *p) for p in ring)
        shp = b"\0" * 100 + struct.pack(">II", 1, len(rec) // 2) + rec
        Path(d, "z.shp").write_bytes(shp)
        hdr = struct.pack("<4xIHH20x", 1, 32 + 32 + 1, 1 + 4) + b"LocationID\0" + b"N" + b"\0" * 4 + bytes([4]) + b"\0" * 15 + b"\x0d"
        Path(d, "z.dbf").write_bytes(hdr + b" " + b" 132")
        assert read_dbf_ids(Path(d, "z.dbf")) == [132]
        polys = read_polygons(Path(d, "z.shp"))
        assert polys == [[ring]], polys
    print("selftest ok")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    m = sub.add_parser("map")
    m.add_argument("--shp", type=Path, default=HERE / "cache/zones/taxi_zones/taxi_zones")
    m.add_argument("--out", type=Path, default=HERE.parent / "media/beat07_nyc_taxi_zones_midtown_jfk.png")
    s = sub.add_parser("svg")
    s.add_argument("--csv", type=Path, default=HERE / "derived/hourly_profile.csv")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
    elif a.cmd == "map":
        draw_map(a.shp, a.out)
    elif a.cmd == "svg":
        with open(a.csv, newline="") as f:
            print(chart_svg(list(csv.DictReader(f))))
    else:
        ap.print_help()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
