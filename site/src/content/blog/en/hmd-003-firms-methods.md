---
title: "How to read and rerun NASA FIRMS fire data"
description: "Each FIRMS row is the centre of a 375 m VIIRS pixel. The columns, the free-key area API, a stdlib timeline script, and why no precision is reported."
lang: en
translationKey: hmd-003-deep-dive
hmd: HMD-003
kind: deep-dive
date: 2026-12-04
tags: ["NASA FIRMS", "VIIRS", "MODIS", "remote sensing", "reproducibility", "wildfire"]
sources:
  - title: "NASA FIRMS (Fire Information for Resource Management System)"
    url: "https://firms.modaps.eosdis.nasa.gov/"
  - title: "NASA FIRMS · Area API"
    url: "https://firms.modaps.eosdis.nasa.gov/api/area/"
  - title: "NASA MODAPS · VNP14IMGTDL_NRT product page (VIIRS 375 m active fire)"
    url: "https://modaps.modaps.eosdis.nasa.gov/services/about/products/viirs-land-c2-nrt/vnp14imgtdl_nrt.html"
  - title: "NASA Earthdata · VIIRS Active Fire User Guide (PDF)"
    url: "https://www.earthdata.nasa.gov/sites/default/files/imported/VIIRS_activefire_User_Guide.pdf"
  - title: "NASA FIRMS · Fire Alerts: Important Notes"
    url: "https://firms.modaps.eosdis.nasa.gov/alerts/notes.php"
  - title: "Earth Fire Alliance & Muon Space · First light and first active fire images from operational FireSat (16 Sep 2026)"
    url: "https://earthfirealliance.org/news-article/earth-fire-alliance-and-muon-space-release-first-light-and-first-active-fire-images-from-operational-firesat-constellation/"
  - title: "Google · A breakthrough in wildfire detection (16 Sep 2024)"
    url: "https://blog.google/outreach-initiatives/sustainability/google-ai-wildfire-detection/"
  - title: "Iran International (Persian) · Elit forest fire report (27 Nov 2025)"
    url: "https://www.iranintl.com/fa/202511276713"
  - title: "Wikipedia · Elit, Iran"
    url: "https://en.wikipedia.org/wiki/Elit,_Iran"
  - title: "Google Earth Engine catalog · FIRMS terms of use (NASA data policy, LANCE citation and disclaimer)"
    url: "https://developers.google.com/earth-engine/datasets/catalog/FIRMS"
datasets:
  - title: "NASA FIRMS · VIIRS 375 m active fire (S-NPP, NOAA-20, NOAA-21; SP and NRT)"
    url: "https://firms.modaps.eosdis.nasa.gov/"
    license: "NASA full and open data; acknowledge LANCE FIRMS and link its disclaimer"
  - title: "NASA FIRMS · MODIS 1 km active fire (for comparison; supported by the script)"
    url: "https://firms.modaps.eosdis.nasa.gov/"
    license: "NASA full and open data; acknowledge LANCE FIRMS and link its disclaimer"
  - title: "HMD-003 artifact · firms_timeline.py and two ILLUSTRATIVE files (18 synthetic rows, one made-up site)"
    url: "https://github.com/AshE-96/homodyne/tree/main/parts/03-standalone/hmd-003-wildfire-from-space/artifact"
    license: "Synthetic (ILLUSTRATIVE); see the Homodyne LICENSE.md (code MIT)"
---

Read each FIRMS row as "the centre of a roughly 375 m pixel that was hotter than its surroundings when the satellite passed", not as the exact location of a confirmed fire. To reproduce the analysis, download from the FIRMS area API with a free MAP_KEY and run `firms_timeline.py`, which needs only the Python standard library. The Elit fire timeline has not been run with this method yet; this post shows how you can run it.

> **Key Takeaways**
> - The main product is VIIRS active-fire detections at about 375 m, from the S-NPP, NOAA-20 and NOAA-21 satellites. MODIS, at about 1 km, is older and coarser.
> - The area API returns at most 5 days per request, and a free MAP_KEY allows 5,000 transactions per 10 minutes.
> - The `type` column (static source, volcano and so on) exists only in the standard (SP) product, not in NRT.
> - The script does three things: a confidence filter, a near-industrial-site flag and a recurring-spot flag. It reports no precision or recall.
> - The bundled sample is ILLUSTRATIVE; none of its numbers describe the Elit fire.

## Which datasets, and on what terms?

All real data in this episode comes from [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/), which publishes hot spots from two instrument families.

| Dataset | Pixel size | API source name | Access |
|---|---|---|---|
| VIIRS on S-NPP | about 375 m | `VIIRS_SNPP_SP`, `VIIRS_SNPP_NRT` | free MAP_KEY |
| VIIRS on NOAA-20 | about 375 m | `VIIRS_NOAA20_SP`, `VIIRS_NOAA20_NRT` | free MAP_KEY |
| VIIRS on NOAA-21 | about 375 m | `VIIRS_NOAA21_*` | free MAP_KEY |
| MODIS | about 1 km | `MODIS_*` | free MAP_KEY |

Each source comes in two versions. **NRT** is near-real-time data, useful for the last couple of months. **SP** is the standard-processing archive, published later, and it carries the `type` column. If a source has no data for a date, FIRMS returns an empty table or a message, and the script prints that message; try the other version or the Archive Download section of the FIRMS site.

Area API rules (checked 2 November 2026):

- URL pattern: `/api/area/csv/[MAP_KEY]/[SOURCE]/[W,S,E,N]/[DAY_RANGE]/[DATE]`
- `DAY_RANGE` is 1 to 5, so a month has to be split into 5-day chunks. The script does this for you.
- The MAP_KEY is free and allows 5,000 transactions per 10-minute interval. A multi-day request can count as more than one transaction; "Check status" on the same page shows what is left.

On terms of use: NASA promotes full and open sharing of its data. If you pass FIRMS data on to others, NASA asks you to follow the LANCE citation, acknowledgement and disclaimer guidelines and to replicate or link the disclaimer (as summarised in the [Earth Engine FIRMS catalog entry](https://developers.google.com/earth-engine/datasets/catalog/FIRMS)). Read those terms before you republish raw rows.

The artifact folder also holds two synthetic files: `sample_firms_ILLUSTRATIVE.csv`, 18 rows in the VIIRS column layout, and `sites_ILLUSTRATIVE.csv`, one made-up industrial site called SITE-A. Both were written by hand for teaching; they are not FIRMS data and describe no real event.

## What does each column in a FIRMS row mean?

Column definitions come from NASA MODAPS's [VIIRS product page](https://modaps.modaps.eosdis.nasa.gov/services/about/products/viirs-land-c2-nrt/vnp14imgtdl_nrt.html) and the [VIIRS user guide](https://www.earthdata.nasa.gov/sites/default/files/imported/VIIRS_activefire_User_Guide.pdf):

- **`latitude`, `longitude`:** "Center of nominal 375 m fire pixel". The pixel centre, not the fire.
- **`acq_date`, `acq_time`:** the overpass date and time in UTC, as HHMM. For Tehran add three and a half hours; Iran has not used daylight saving time since 2023.
- **`satellite`:** which satellite saw it, for example `N` for S-NPP and `N20` for NOAA-20.
- **`confidence`:** for VIIRS one of `l`, `n`, `h` (low, nominal, high). Low-confidence daytime pixels are "typically associated with areas of Sun glint". For MODIS this column is 0 to 100, and the script maps it as below 30 low, 30 to 79 nominal, 80 and above high.
- **`frp`:** fire radiative power in megawatts, a rough measure of how much heat that pixel radiated.
- **`daynight`:** `D` for day, `N` for night.
- **`type`:** SP product only. 0 presumed vegetation fire, 1 volcano, 2 other static land source, 3 offshore.

Columns such as `bright_ti4` and `bright_ti5` are also in the file, but this episode's script does not use them.

## What exactly does the script do?

`firms_timeline.py` needs only the Python 3.9+ standard library and makes no network call unless you pass `--fetch`. Its steps:

1. **Read:** parse the CSV. Lines starting with `#` are comments; if they contain the word ILLUSTRATIVE, a warning banner is printed.
2. **Box and dates:** keep only rows inside the W,S,E,N box and the date range.
3. **Confidence threshold:** drop rows below `--min-confidence` (default `nominal`). The output always shows how many rows each of the three thresholds would keep.
4. **Near a site:** compute the haversine distance from each detection to the nearest site in your list; flag it if closer than `--near-km` (default 2).
5. **Recurring:** flag detections whose `--repeat-km` neighbourhood (default 0.5) was hot on `--repeat-days` (default 3) or more different days. The detection's own day counts.
6. **type column:** if present and equal to 2, flag as a static source.
7. **Report:** a day-by-day timeline (count, flagged count, max FRP), a detection table in UTC and Tehran time, and a summary including the first unflagged detection.

There is no machine-learning model and no decision that a dot is a fire. The script only says what was seen, when, and with which flags.

## How do you run it yourself?

All commands run from the repository root.

**1. Offline, on ILLUSTRATIVE data (no key):**

```bash
python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --demo --region mazandaran
python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --demo --region mazandaran --min-confidence low --quiet
python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --demo --region mazandaran --min-confidence high --quiet
```

With the wider `mazandaran` box, this synthetic sample gives 18 rows in the box; 18, 15 and 7 rows kept at low, nominal and high; and a first kept detection next to SITE-A, flagged as recurring over five days. At `low`, a faint detection appears at the sample fire's location about 12 hours before the first `nominal` one there. With `--demo` and no `--region`, the script uses this same `mazandaran` box, because that is the area the sample rows cover; `--region elit` narrows it to 12 of the 18 rows (12, 10 and 5 kept), with SITE-A outside, so nothing is flagged. These numbers only check that your setup works. They describe no real fire.

**2. Get a MAP_KEY:** open the [FIRMS area API page](https://firms.modaps.eosdis.nasa.gov/api/area/), choose Get MAP_KEY, enter your e-mail and confirm the key you receive. Keep it in your shell, never in the repository:

```bash
export FIRMS_MAP_KEY=your_key_here
```

**3. Download the Elit period:**

```bash
mkdir -p data
python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --fetch --region elit \
    --start 2025-10-28 --end 2025-11-27 \
    --sources VIIRS_SNPP_SP,VIIRS_NOAA20_SP \
    --save data/elit_2025-11.csv
```

The window from 28 October to 27 November 2025 covers both the reported start (1 November) and the flare-up (15 November). If the SP version has no data for those months, try `--sources VIIRS_SNPP_NRT,VIIRS_NOAA20_NRT,VIIRS_NOAA21_NRT` or Archive Download.

**4. Re-run offline so your numbers stay reproducible:**

```bash
python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --csv data/elit_2025-11.csv --region elit --min-confidence low
```

**5. Your industrial-site list:** make a CSV with `name,lat,lon,kind` and pass it with `--sites my_sites.csv`. The script ships no real site coordinates. Build each row from a source you checked (OpenStreetMap, an official map) and note that source next to the row.

## How is the "elit" box defined?

In the script, `--region elit` is the box (W, S, E, N) = (50.95, 36.20, 51.45, 36.55). It is anchored on Elit village at about 36.32 N, 51.11 E, in Kuhestan rural district, Marzanabad district, Chalus County. Kojur, at about 36.38 N, 51.72 E, falls outside. The box is approximate: check it on a map before publishing any result, or pass your own with `--bbox`. If the table in `artifact/README.md` shows different numbers, the value inside the script is the one that runs.

## Why are precision and recall not reported?

Precision is the share of alerts that were real fires; recall is the share of real fires that were detected. Both need an independent list from the ground: location, time and extent of every fire. We have no such reliable list for northern Iran. Even for a well-known fire like Elit, official burned-area estimates run from about 8 ha (the deputy agriculture minister and the governor) and about 10 ha (Natural Resources) to 150 to 180 ha (a deputy head of the Department of Environment).

A real evaluation would need at least an independent ground list with times and coordinates, a matching rule fixed in advance (what distance and time window count as "the same fire"), and a way to set aside fires that could not have been seen at all. FIRMS names those cases directly: fires that "started and ended between satellite overpasses", or fires under "cloud cover, heavy smoke, or tree canopy". Without all of this, any accuracy percentage is unsupported.

## What are the method's limitations?

- **Coordinates are approximate:** the centre of a roughly 14-hectare pixel, not the fire.
- **Sampling is discrete:** only overpass moments are seen; the first detection is not the first moment of the fire.
- **Canopy:** in dense Hyrcanian forest, a fire under the canopy can look faint or not show at all.
- **Flags are heuristics:** proximity and recurrence can both flag a real fire or miss a static source, and they are only as good as your site list.
- **No `type` in NRT:** for recent data, that help is missing.
- **This is not FireSat:** according to Earth Fire Alliance (16 September 2026), FireSat's infrared bands can detect fires as small as 5 by 5 metres, with global access planned for 2028. Our script works with VIIRS data and reproduces no FireSat or Google model.

## What this does not show

- No FIRMS number about the Elit fire; that run has not been done.
- How accurate VIIRS is in northern Iran.
- That a satellite saw the Elit fire before people on the ground.
- Anything about a real place or fire from the ILLUSTRATIVE output.

## Further reading

- [VIIRS Active Fire User Guide](https://www.earthdata.nasa.gov/sites/default/files/imported/VIIRS_activefire_User_Guide.pdf), for the algorithm and column meanings.
- [FIRMS Fire Alerts: Important Notes](https://firms.modaps.eosdis.nasa.gov/alerts/notes.php), for why fires are missed.
- [Earth Fire Alliance's FireSat announcement](https://earthfirealliance.org/news-article/earth-fire-alliance-and-muon-space-release-first-light-and-first-active-fire-images-from-operational-firesat-constellation/) and [Google's description of the AI role](https://blog.google/outreach-initiatives/sustainability/google-ai-wildfire-detection/).
- The plain-language companion: [Can satellites spot a small forest fire from space?](/en/blog/hmd-003-small-fires-from-space/)
- The video and deck: [HMD-003 episode page](/en/episodes/hmd-003/); next: [HMD-004](/en/episodes/hmd-004/)
- Persian original: [دادهٔ آتش FIRMS را چطور بخوانیم و خودمان اجرا کنیم؟](/fa/blog/hmd-003-firms-methods/)
