# firms_timeline.py · read satellite hot spots like an analyst

Homodyne HMD-003 artifact. Python 3.9+, **standard library only**. No network call unless you pass `--fetch`.

It reads NASA FIRMS VIIRS active-fire detections for a box in northern Iran (the Hyrcanian forests of
Gilan, Mazandaran and Golestan), filters them by confidence, flags detections close to industrial
sites **you** list, flags spots that are hot on several different days, and prints a per-day timeline.

> This is not FireSat and does not reproduce any FireSat or Google model. FIRMS hot spots come from
> the VIIRS and MODIS instruments. A hot spot is a heat anomaly in one pixel (about 375 m for VIIRS);
> its coordinate is the pixel centre, not the exact fire. Without ground truth the script reports no
> precision or recall.

## 1 · Run it offline (no key needed)

```bash
python3 artifact/firms_timeline.py --demo
python3 artifact/firms_timeline.py --demo --min-confidence low --quiet
python3 artifact/firms_timeline.py --demo --min-confidence high --quiet
```

`--demo` reads `sample_firms_ILLUSTRATIVE.csv` and `sites_ILLUSTRATIVE.csv`. Both are **synthetic**:
written by hand to teach the columns and the checks. They are not FIRMS data and not a real event;
the script prints an ILLUSTRATIVE banner whenever it reads them.

## 2 · Get a free FIRMS MAP_KEY

1. Open the FIRMS API page: <https://firms.modaps.eosdis.nasa.gov/api/area/>.
2. Choose **Get MAP_KEY**, enter your e-mail address, and confirm the key that arrives by e-mail.
3. Keep it out of the repository. Put it in your shell only:

```bash
export FIRMS_MAP_KEY=your_key_here
```

The API page (checked 2 Nov 2026) allows 5,000 transactions per 10-minute interval, and a request for
several days can count as more than one transaction. "Check status" on the same page shows what is left.

## 3 · Download a real period

```bash
python3 artifact/firms_timeline.py --fetch --region elit \
    --start 2025-10-28 --end 2025-11-27 \
    --sources VIIRS_SNPP_SP,VIIRS_NOAA20_SP \
    --save data/elit_2025-11.csv --sites my_sites.csv
```

- The area API takes at most 5 days per call (`DAY_RANGE` 1..5), so the script splits the range.
- `*_SP` sources are the standard-processing archive; for the last couple of months use `*_NRT`
  (for example `VIIRS_SNPP_NRT,VIIRS_NOAA20_NRT,VIIRS_NOAA21_NRT`). If a source has no data for a
  date, FIRMS answers with an empty table or a message; the script prints what FIRMS said.
- URL pattern used: `/api/area/csv/[MAP_KEY]/[SOURCE]/[W,S,E,N]/[DAY_RANGE]/[YYYY-MM-DD]`.
- Save the raw CSV with `--save` and re-run offline with `--csv` so the numbers you show are reproducible.
- `data/` is not in the repository. Check FIRMS data-use terms before you re-publish raw rows.

## 4 · Regions (approximate — check on a map)

| `--region` | W, S, E, N | Note |
|---|---|---|
| `elit` | 50.95, 36.20, 51.45, 36.55 | Elit village (36.32N 51.11E), Marzanabad, Chalus County |
| `mazandaran` | 50.30, 35.80, 54.20, 36.90 | |
| `golestan` | 54.00, 36.50, 56.30, 38.10 | |
| `gilan` | 48.50, 36.50, 50.60, 38.50 | |
| `hyrcanian` | 48.50, 35.80, 56.30, 38.50 | whole southern Caspian strip |

Or pass your own box: `--bbox 51.2,36.35,51.5,36.6`.

## 5 · Your industrial-site list

A CSV with `name,lat,lon,kind`. The script never ships real site coordinates; build your own list from
sources you have checked (OpenStreetMap, official maps) and keep the source next to each row.

```csv
name,lat,lon,kind
my-site-1,36.5000,51.4000,power plant (source: ...)
```

## 6 · What the flags mean (and do not mean)

| Flag | Rule | Can be wrong when… |
|---|---|---|
| `near SITE (x km)` | a listed site is within `--near-km` (default 2 km) | a real fire burns next to a factory; your list is incomplete |
| `recurring (n days)` | hot within `--repeat-km` (0.5 km) on `--repeat-days` (3) or more different days | a slow fire smoulders in one place for days |
| `FIRMS type 2` | the CSV has a `type` column (some archive downloads) and it says 2 = other static land source | the column is absent in NRT data |

Confidence: VIIRS reports `l`, `n`, `h` (low, nominal, high). MODIS reports 0–100; the script maps
it to low (<30), nominal (30–79), high (≥80). Raising the threshold removes weak false alarms **and**
weak early signs of real fires. That trade-off is the point of the episode.

## 7 · Times

`acq_time` is UTC (HHMM). The script also prints Tehran time (UTC+03:30; Iran has not used daylight
saving time since 2023).
