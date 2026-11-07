#!/usr/bin/env python3
"""Read NASA FIRMS VIIRS hot spots for a box in northern Iran and print a timeline.

Homodyne HMD-003 · "Can we find a forest fire while it is still small?"

What it does
  1. Reads a FIRMS CSV (or downloads one with your own MAP_KEY).
  2. Keeps detections inside a bounding box and a date range.
  3. Filters by detection confidence (VIIRS: low / nominal / high).
  4. Flags detections near industrial sites YOU list (name,lat,lon,kind CSV).
  5. Flags "recurring" spots: the same place hot on several different days,
     a hint of a static heat source rather than a spreading fire.
  6. Prints a per-day timeline and a detection table (UTC and Tehran time).

What it does NOT do
  - It is not FireSat and does not reproduce any FireSat or Google model.
  - A hot spot is a heat anomaly in one satellite pixel (~375 m for VIIRS);
    the coordinate is the pixel centre, not the exact fire location.
  - Without ground truth it cannot say how many detections were real fires,
    so it prints no precision / recall.

Standard library only (Python 3.9+). No API call is made unless you pass --fetch.

Examples
  python3 firms_timeline.py --demo
  python3 firms_timeline.py --csv my_firms.csv --sites my_sites.csv --region elit
  FIRMS_MAP_KEY=xxxx python3 firms_timeline.py --fetch --region elit \
      --start 2025-10-28 --end 2025-11-27 --save elit_2025.csv --sites my_sites.csv
"""
from __future__ import annotations

import argparse
import csv
import io
import math
import os
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEMO_CSV = HERE / "sample_firms_ILLUSTRATIVE.csv"
DEMO_SITES = HERE / "sites_ILLUSTRATIVE.csv"

API = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{source}/{bbox}/{days}/{start}"
MAX_DAYS_PER_CALL = 5  # FIRMS area API accepts DAY_RANGE 1..5

# Approximate boxes (west, south, east, north). Check them on a map before you publish.
REGIONS = {
    "elit":       (50.95, 36.20, 51.45, 36.55),  # Elit village 36.32N 51.11E, Marzanabad, Chalus County
    "mazandaran": (50.30, 35.80, 54.20, 36.90),
    "golestan":   (54.00, 36.50, 56.30, 38.10),
    "gilan":      (48.50, 36.50, 50.60, 38.50),
    "hyrcanian":  (48.50, 35.80, 56.30, 38.50),  # whole southern Caspian strip
}

TEHRAN_OFFSET = timedelta(hours=3, minutes=30)  # Iran Standard Time, no DST since 2023
CONF_RANK = {"low": 0, "nominal": 1, "high": 2}


# ---------------------------------------------------------------- reading

def read_rows(text: str) -> tuple[list[dict], bool]:
    """Parse FIRMS CSV text. Lines starting with '#' are comments.
    Returns (rows, illustrative_flag)."""
    lines = text.splitlines()
    illustrative = any(l.startswith("#") and "ILLUSTRATIVE" in l for l in lines)
    body = [l for l in lines if l.strip() and not l.startswith("#")]
    if not body:
        return [], illustrative
    return list(csv.DictReader(io.StringIO("\n".join(body)))), illustrative


def confidence_class(raw: str) -> str:
    """VIIRS gives l/n/h; MODIS gives 0-100 (FIRMS guidance: <30 low, 30-79 nominal, >=80 high)."""
    raw = (raw or "").strip().lower()
    if raw in ("l", "low"):
        return "low"
    if raw in ("n", "nominal"):
        return "nominal"
    if raw in ("h", "high"):
        return "high"
    try:
        v = float(raw)
    except ValueError:
        return "low"
    return "low" if v < 30 else "nominal" if v < 80 else "high"


def normalise(row: dict) -> dict | None:
    try:
        lat, lon = float(row["latitude"]), float(row["longitude"])
        d = datetime.strptime(row["acq_date"].strip(), "%Y-%m-%d").date()
        hhmm = str(row.get("acq_time", "0")).strip().zfill(4)
        utc = datetime(d.year, d.month, d.day, int(hhmm[:2]), int(hhmm[2:]))
    except (KeyError, ValueError):
        return None
    frp = row.get("frp", "")
    return {
        "lat": lat, "lon": lon, "date": d, "utc": utc, "local": utc + TEHRAN_OFFSET,
        "sat": (row.get("satellite") or row.get("source") or "?").strip(),
        "conf": confidence_class(row.get("confidence", "")),
        "frp": float(frp) if frp not in ("", None) else None,
        "daynight": (row.get("daynight") or "?").strip(),
        "type": (row.get("type") or "").strip(),  # present in some archive downloads
        "flags": [],
    }


def read_sites(path: Path | None) -> list[dict]:
    if not path:
        return []
    text = path.read_text(encoding="utf-8")
    body = [l for l in text.splitlines() if l.strip() and not l.startswith("#")]
    sites = []
    for r in csv.DictReader(io.StringIO("\n".join(body))):
        try:
            sites.append({"name": r["name"].strip(), "lat": float(r["lat"]),
                          "lon": float(r["lon"]), "kind": (r.get("kind") or "").strip()})
        except (KeyError, ValueError):
            print(f"warning: skipped site row {r}", file=sys.stderr)
    return sites


# ---------------------------------------------------------------- fetching

def fetch(key: str, sources: list[str], bbox: tuple, start: date, end: date) -> str:
    """Download FIRMS area CSVs in chunks of up to 5 days and concatenate them."""
    box = ",".join(f"{v:g}" for v in bbox)
    header, out = None, []
    for source in sources:
        day = start
        while day <= end:
            days = min(MAX_DAYS_PER_CALL, (end - day).days + 1)
            url = API.format(key=key, source=source, bbox=box, days=days, start=day.isoformat())
            try:
                with urllib.request.urlopen(url, timeout=60) as resp:
                    text = resp.read().decode("utf-8", "replace")
            except urllib.error.URLError as exc:
                sys.exit(f"download failed for {source} {day}: {exc}")
            lines = [l for l in text.splitlines() if l.strip()]
            if not lines or "," not in lines[0]:
                sys.exit(f"FIRMS answered for {source} {day}: {text.strip()[:200]}")
            if header is None:
                header = lines[0] + ",source"
            out += [l + "," + source for l in lines[1:]]
            print(f"  {source:<18} {day} +{days}d  {len(lines) - 1:>4} rows", file=sys.stderr)
            day += timedelta(days=days)
    return "\n".join([header or "latitude,longitude,acq_date,acq_time,confidence,source"] + out)


# ---------------------------------------------------------------- analysis

def km(a_lat, a_lon, b_lat, b_lon) -> float:
    r = 6371.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp, dl = p2 - p1, math.radians(b_lon - a_lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def flag(dets: list[dict], sites: list[dict], near_km: float, repeat_km: float, repeat_days: int):
    for d in dets:
        best = min(((km(d["lat"], d["lon"], s["lat"], s["lon"]), s) for s in sites),
                   key=lambda t: t[0], default=None)
        if best and best[0] <= near_km:
            d["flags"].append(f"near {best[1]['name']} ({best[0]:.1f} km)")
        days = {o["date"] for o in dets if km(d["lat"], d["lon"], o["lat"], o["lon"]) <= repeat_km}
        if len(days) >= repeat_days:
            d["flags"].append(f"recurring ({len(days)} days)")
        if d["type"] == "2":
            d["flags"].append("FIRMS type 2: static land source")


def report(dets_all: list[dict], args, bbox, illustrative: bool, label: str):
    w, s, e, n = bbox
    inside = [d for d in dets_all if w <= d["lon"] <= e and s <= d["lat"] <= n
              and (not args.start or d["date"] >= args.start)
              and (not args.end or d["date"] <= args.end)]
    floor = CONF_RANK[args.min_confidence]
    kept = [d for d in inside if CONF_RANK[d["conf"]] >= floor]
    sites = read_sites(args.sites)
    flag(kept, sites, args.near_km, args.repeat_km, args.repeat_days)
    kept.sort(key=lambda d: d["utc"])

    print(f"FIRMS hot-spot timeline · {label}")
    if illustrative:
        print("!! ILLUSTRATIVE SAMPLE: synthetic rows for teaching, not FIRMS data !!")
    print(f"box W,S,E,N = {w:g},{s:g},{e:g},{n:g} · min confidence: {args.min_confidence}"
          f" · near-site radius: {args.near_km:g} km · sites listed: {len(sites)}")
    print(f"rows in box/dates: {len(inside)} · kept: {len(kept)}"
          f" · dropped below '{args.min_confidence}': {len(inside) - len(kept)}")
    by_conf = {c: sum(CONF_RANK[d['conf']] >= r for d in inside) for c, r in CONF_RANK.items()}
    print("kept if threshold were:  " + "  ".join(f"{c} -> {v}" for c, v in by_conf.items()))
    if not kept:
        print("\nNo detections kept. Possible reasons: no fire, clouds or smoke, canopy,"
              " a fire between overpasses, or a box/date/source mismatch.")
        return

    print("\nTimeline (dates in UTC)")
    print(f"{'date':<11} {'n':>3} {'flagged':>8} {'max FRP':>8}  bar")
    per_day = defaultdict(list)
    for d in kept:
        per_day[d["date"]].append(d)
    day = kept[0]["date"]
    while day <= kept[-1]["date"]:
        ds = per_day.get(day, [])
        nflag = sum(bool(d["flags"]) for d in ds)
        frps = [d["frp"] for d in ds if d["frp"] is not None]
        frp = f"{max(frps):.1f}" if frps else "-"
        bar = "x" * nflag + "#" * (len(ds) - nflag)
        print(f"{day.isoformat():<11} {len(ds):>3} {nflag:>8} {frp:>8}  {bar}")
        day += timedelta(days=1)
    print("            # = unflagged detection   x = flagged (near a listed site / recurring)")

    if not args.quiet:
        print("\nDetections")
        print(f"{'UTC':<16} {'Tehran':<6} {'sat':<5} {'conf':<8} {'FRP':>6} {'lat':>8} {'lon':>8}  flags")
        for d in kept[: args.limit]:
            frp = f"{d['frp']:.1f}" if d["frp"] is not None else "-"
            print(f"{d['utc']:%Y-%m-%d %H:%M} {d['local']:%H:%M}  {d['sat']:<5} {d['conf']:<8} {frp:>6}"
                  f" {d['lat']:>8.3f} {d['lon']:>8.3f}  {'; '.join(d['flags'])}")
        if len(kept) > args.limit:
            print(f"... {len(kept) - args.limit} more (use --limit)")

    clean = [d for d in kept if not d["flags"]]
    print("\nSummary")
    print(f"  first kept detection : {kept[0]['utc']:%Y-%m-%d %H:%M} UTC ({kept[0]['local']:%H:%M} Tehran)")
    print(f"  last kept detection  : {kept[-1]['utc']:%Y-%m-%d %H:%M} UTC")
    print(f"  days with detections : {len(per_day)}")
    print(f"  flagged detections   : {len(kept) - len(clean)}")
    print(f"  unflagged detections : {len(clean)}"
          + (f" (first: {clean[0]['utc']:%Y-%m-%d %H:%M} UTC)" if clean else ""))
    print("\nA hot spot is a heat anomaly in one pixel, not a confirmed forest fire."
          "\nNo ground truth here, so no precision or recall.")


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    src = p.add_mutually_exclusive_group()
    src.add_argument("--demo", action="store_true", help="run on the bundled ILLUSTRATIVE sample")
    src.add_argument("--csv", type=Path, help="a FIRMS CSV you already downloaded")
    src.add_argument("--fetch", action="store_true", help="download from the FIRMS area API")
    p.add_argument("--region", choices=sorted(REGIONS), default=None,
                   help="default: elit; with --demo, mazandaran (the area the sample rows cover)")
    p.add_argument("--bbox", help="W,S,E,N in degrees; overrides --region")
    p.add_argument("--start", type=parse_date, help="first date, YYYY-MM-DD (UTC)")
    p.add_argument("--end", type=parse_date, help="last date, YYYY-MM-DD (UTC)")
    p.add_argument("--sources", default="VIIRS_SNPP_SP,VIIRS_NOAA20_SP",
                   help="FIRMS sources, comma-separated (use *_NRT for the last ~2 months)")
    p.add_argument("--map-key", default=os.environ.get("FIRMS_MAP_KEY", ""),
                   help="FIRMS MAP_KEY (default: $FIRMS_MAP_KEY)")
    p.add_argument("--save", type=Path, help="with --fetch: also write the raw CSV here")
    p.add_argument("--sites", type=Path, help="CSV of known industrial sites: name,lat,lon,kind")
    p.add_argument("--min-confidence", choices=list(CONF_RANK), default="nominal")
    p.add_argument("--near-km", type=float, default=2.0, help="flag if a listed site is this close")
    p.add_argument("--repeat-km", type=float, default=0.5)
    p.add_argument("--repeat-days", type=int, default=3, help="flag spots hot on this many days")
    p.add_argument("--limit", type=int, default=40, help="max rows in the detection table")
    p.add_argument("--quiet", action="store_true", help="timeline and summary only")
    args = p.parse_args()

    region = args.region or ("mazandaran" if args.demo else "elit")
    bbox = tuple(float(v) for v in args.bbox.split(",")) if args.bbox else REGIONS[region]
    if len(bbox) != 4:
        sys.exit("--bbox needs four numbers: W,S,E,N")

    if args.fetch:
        if not args.map_key:
            sys.exit("Set FIRMS_MAP_KEY or pass --map-key (free key: see artifact/README.md).")
        if not (args.start and args.end):
            sys.exit("--fetch needs --start and --end")
        text = fetch(args.map_key, [s.strip() for s in args.sources.split(",") if s.strip()],
                     bbox, args.start, args.end)
        if args.save:
            args.save.write_text(text + "\n", encoding="utf-8")
            print(f"saved raw CSV to {args.save}", file=sys.stderr)
        label = f"FIRMS API · {args.sources} · {args.start}..{args.end}"
    else:
        path = args.csv or DEMO_CSV
        if not args.csv and args.sites is None:
            args.sites = DEMO_SITES
        text = path.read_text(encoding="utf-8")
        label = path.name

    rows, illustrative = read_rows(text)
    dets = [d for d in (normalise(r) for r in rows) if d]
    if len(dets) < len(rows):
        print(f"warning: {len(rows) - len(dets)} rows could not be parsed", file=sys.stderr)
    report(dets, args, bbox, illustrative, label)


if __name__ == "__main__":
    main()
