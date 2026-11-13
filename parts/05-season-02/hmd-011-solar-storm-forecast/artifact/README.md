# storm_replay.py · replay eight years of real storm forecasts

Homodyne HMD-011 artifact. Python 3.9+, **standard library only** (no numpy). No API key. The only network
call is `--fetch`.

It asks one narrow question: **on a given UT day, did the largest 3-hour planetary Kp reach 5− (4.667) or more?**
That is NOAA scale G1 or stronger. It then scores the probabilities NOAA SWPC published for that day one, two
and three days ahead, next to four simple rules, using only what was known when each forecast was issued.

> This is an educational replay, not an official verification and not a warning service. For real decisions use
> the official SWPC watches, warnings and alerts. Solar flares, coronal mass ejections (CMEs) and geomagnetic
> storms are different phenomena; this script forecasts none of the first two. It makes no claim about any
> specific outage or damage.

## 1 · Run it (offline, about 15 seconds)

```bash
python3 artifact/storm_replay.py              # prints the report, rewrites results/results.json and results.md
python3 artifact/storm_replay.py --cost 0.2 --lead 2   # your own user: cost ratio and days ahead you must decide
python3 artifact/storm_replay.py --selftest   # about 1 second; used by `make selftest`
```

The run reads the three small CSVs in `derived/` (committed) and writes `results/`. The bootstrap uses a fixed
seed, so a re-run gives the same numbers.

## 2 · Rebuild from the original archives

```bash
python3 artifact/storm_replay.py --fetch
```

Downloads about 7 MB into `artifact/data/` (git-ignored by the repository's `parts/*/*/artifact/data/` rule),
rebuilds `derived/` and writes `derived/FETCHED.txt` with the URLs and the time. Files used (downloaded
2026-11-12 21:28–21:31 UTC):

| File | Source | Licence / terms |
|---|---|---|
| `Kp_ap_Ap_SN_F107_since_1932.txt` | GFZ Helmholtz Centre for Geosciences, <https://kp.gfz.de/app/files/Kp_ap_Ap_SN_F107_since_1932.txt> | Kp: **CC BY 4.0** (file header). Cite Matzka et al. 2021, Space Weather, doi:10.1029/2020SW002641 and the data DOI 10.5880/Kp.0001. The sunspot column (CC BY-NC 4.0) is not used. |
| `YYYY_RSGA.tar.gz`, 2018–2025 | NOAA SWPC warehouse, `ftp://ftp.swpc.noaa.gov/pub/warehouse/YYYY/` | NOAA/NWS information is public domain unless noted (weather.gov/disclaimer). |
| `YYYY_DGD.txt`, 2018–2025 | same warehouse (Daily Geomagnetic Data: Fredericksburg K) | same |

The FTP server has no HTTPS mirror that answered from here; Python's `urllib` speaks `ftp://` directly.

## 3 · What is compared

| Name | Forecast for day D | Known at |
|---|---|---|
| `noaa_d1`, `noaa_d2`, `noaa_d3` | RSGA section VI, middle latitudes: P(minor storm) + P(major-severe storm) | 22:00 UT, 1/2/3 days before D. Reports issued on or after 00:00 UT of the day they call "day 1" are dropped for that lead; an amended report replaces the earlier one only if it was still issued in time. |
| `climatology` | storm-day rate 1996–2017 (14.4%) | always |
| `persistence_d1..3` | storm-day rate 1996–2017 given whether the issue day had Kp ≥ 5− **up to 21:00 UT** (same cutoff as the RSGA) | issue time |
| `recurrence_27d` | storm-day rate 1996–2017 given whether day D−27 was a storm day | 27 days ahead |
| `always_warn` | 1 every day | always |

**Time-based split.** Only base rates are fitted, and only on 1996-01-01 … 2017-12-31. The test years
2018-01-01 … 2025-12-31 are never used to build a forecast. 78 of 2,922 test days lack one of the three NOAA
leads and are dropped from every forecaster, so all of them are scored on the same 2,844 days.

## 4 · Scores

- **Brier score** = mean of (p − outcome)²; **skill** = 1 − Brier / Brier(climatology).
- **Reliability**: days grouped by forecast probability; mean forecast vs observed storm rate in each group.
- **Warnings at a threshold**: hits, misses, false alarms, false alarms per year.
- **Lead time per storm episode** (a run of consecutive storm days): was the first day warned 1, 2, 3 days ahead?
- **Cost-loss value** (static model, L = 1): warn when p ≥ C/L. Value = (E_climate − E_forecast) / (E_climate − E_perfect),
  where E_climate is the cheaper of "always act" and "never act". 1 = perfect, 0 = no better than that, < 0 = worse.
- **Block bootstrap** of Brier skill (27-day blocks, 2,000 resamples, seed 11): a 95% interval that keeps storm
  clusters together. It answers "how much could this number wobble?", which is the next episode's question.

## 5 · Headline results (run of 2026-11-12, `results/results.md`)

- 2,844 scored days, 315 storm days (11.1%), 191 storm episodes, 11 episodes reaching Kp ≥ 8− (G4+).
- Brier skill vs climatology: NOAA 1 day ahead **+0.152** (95% 0.110 … 0.198), 2 days +0.110, 3 days +0.089;
  persistence 1 day +0.083, 2 and 3 days ≈ 0; 27-day recurrence +0.032; always warn −7.9.
- NOAA 1 day ahead vs persistence 1 day ahead: +0.075 (95% 0.028 … 0.125).
- Reliability, NOAA 1 day ahead: said 31.1% on 202 days → storms on 28.2%; said 45.3% on 126 days → 34.9%; said 69.7% on 78 days → 59.0% (roughly honest below 40%, a little overconfident above).
- Thresholds, NOAA 1 day ahead: ≥5% catches 94% of storm days with 220.5 false alarms a year; ≥50% catches 19.4%
  with 6.5 false alarms a year. Always warn: 324.8 false alarms a year.
- First day of the 191 episodes, NOAA ≥30%: 35.1% warned one day ahead, 21.5% three days ahead.
- May 2024: for 10 May NOAA said 11% (3 days ahead), 40% (2 days), 40% (1 day); GFZ Kp reached 8.667.
  For 11 May: 60%, 85%, 95%.

## 6 · Three users (ILLUSTRATIVE)

The cost ratios are teaching assumptions, not measured costs: aurora photographer C/L 0.25, decides 1 day
ahead; satellite operator 0.10, 3 days; power-grid operator 0.05, 2 days. The value numbers are computed on the
real forecasts. Pass `--cost` and `--lead` for your own case. The two-question card is
[`warning-decision-card.md`](warning-decision-card.md).

## 7 · Caveats you should keep

- **Definition mismatch.** RSGA middle-latitude probabilities were defined against the Fredericksburg K index
  (SWPC verification page, archived 2009: minor storm = K 5, major-severe = K 6–9). We score them against
  planetary Kp because that is the G scale the public uses. Against Fredericksburg K ≥ 5 (also in
  `results.md`), the same numbers run about double reality in every group (said 31% → 13.6%) and lose to the in-period storm rate (skill −0.036).
- **Legacy product.** SWPC calls the RSGA "a legacy USAF/NOAA bulletin" kept "for continuity purposes". Its
  current Kp forecasts (3-Day Forecast, Forecast Discussion) and its watches and warnings are not scored here.
- **Truth is definitive Kp**, published after the fact; forecasters worked with real-time estimates.
- **Few big storms.** 11 G4+ episodes are far too few to rank forecasters on big storms.
