"""wind_core.py · HMD-S11 · the physics and the indicator of the takeoff-wind demo, standard library only.

Everything the page shows is computed here from model numbers at a few grid points:
  * units and wind components (speed/direction <-> u/v, head- and crosswind on a takeoff);
  * gusts: gust factor (gust / mean) and gust spread (gust - mean);
  * a wind profile by height from pressure levels, starting at the model's 10 m wind (levels below the
    model ground are dropped), and the shear between two heights;
  * a dry-parcel thermal top, a thermal index, cloud base from the dew-point spread, and Deardorff's
    convective velocity w* as a rough thermal-strength proxy;
  * the editorial "inside / wait / no" indicator, anchored on USHPA SOP 12-02 novice and intermediate
    paragliding limits where such a limit exists, and on editorial choices where it does not;
  * forecast-vs-observation error measures (bias, MAE, RMSE).
interp_height() and the u/v helpers follow HMD-S06 (summit_core.py); the rest is new for this episode.
Nothing here is a safety rule and the indicator never says "safe".
"""
import math

G0 = 9.80665            # m s-2
RD = 287.053            # J kg-1 K-1
CP = 1004.0             # J kg-1 K-1
DRY_LAPSE = 9.8         # K per km: a rising dry thermal cools this fast
COARSE = 800.0          # m: with no pressure level this close above the ground, no thermal top is computed
CLOUDBASE_M_PER_K = 125.0   # m of cloud base per kelvin of (T - Td) spread (Espy's rule, ~400 ft per °F)
KMH_PER_MS, KMH_PER_KT, KMH_PER_MPH = 3.6, 1.852, 1.609344

# Places. Shahran takeoff: OSM node 10207682763 and the FlyAPPI "Shahran (Peak)" take-off; height from SRTM.
# The club decides which slope is used; FACING is the direction the slope looks towards (wind should come FROM there).
SITES = {
    'shahran': dict(name_fa='سایت پرواز شهران (قله)', name_en='Shahran takeoff (peak)', lat=35.8076, lon=51.2851,
                    z=2325, facing=180, verify=True),
    'oiii': dict(name_fa='فرودگاه مهرآباد (METAR OIII)', name_en='Tehran Mehrabad airport (METAR OIII)',
                 lat=35.6857, lon=51.3036, z=1208, facing=None, verify=True),
}

# Indicator thresholds. 'src' says where a number comes from; USHPA = SOP 12-02 (amended Sept 2023), P2 novice
# and P3 intermediate "Recommended Operating Limitations" for paragliding (12/15 mph base wind, 15/18 mph peak
# gusts, wind within 25° of straight up the slope, thermals 200/500 fpm, "significant vertical cloud development").
THRESHOLDS = dict(
    wind=dict(amber=19, red=24, unit='km/h', src='USHPA P2 12 mph / P3 15 mph base wind',
              fa='باد میانگین سکو', en='mean wind at takeoff'),
    gust=dict(amber=24, red=29, unit='km/h', src='USHPA P2 15 mph / P3 18 mph peak gusts',
              fa='تندباد', en='peak gust'),
    spread=dict(amber=8, red=16, unit='km/h', src='editorial; USHPA gust rate 5 mph (8 km/h) in 5 s is a different measure',
                fa='فاصلهٔ تندباد و میانگین', en='gust minus mean'),
    crossing=dict(amber=25, red=45, unit='°', src='USHPA P2: within 25° of straight up the slope; 45° editorial',
                  fa='زاویهٔ باد با شیب', en='angle off the slope'),
    aloft=dict(amber=25, red=35, unit='km/h', src='editorial; below typical paraglider trim speed [VERIFY]',
               fa='باد ۱۰۰۰ متر بالای سکو', en='wind 1,000 m above takeoff'),
    shear=dict(amber=15, red=25, unit='km/h', src='editorial (vector change from takeoff to +1,000 m)',
               fa='چینش باد', en='wind shear'),
    thermal=dict(amber=1.0, red=2.5, unit='m/s', src='USHPA P2 200 fpm / P3 500 fpm climb; w* is only a proxy',
                 fa='قدرت گرمیک (w*)', en='thermal strength (w*)'),
    cape=dict(amber=300, red=1000, unit='J/kg', src='editorial; USHPA P3 "significant vertical cloud development"',
              fa='انرژی همرفت (CAPE)', en='convective energy (CAPE)'),
)
LABELS = ['inside', 'wait', 'no']        # the page never shows "safe"; 'inside' = numbers inside the textbook limits


# ── units and components ──────────────────────────────────────────────────────
def kt_to_kmh(x):
    return None if x is None else x * KMH_PER_KT


def mph_to_kmh(x):
    return x * KMH_PER_MPH


def ms_to_kmh(x):
    return None if x is None else x * KMH_PER_MS


def speed_kmh(u, v):
    return math.hypot(u, v) * KMH_PER_MS


def direction_from(u, v):
    """Meteorological direction the wind blows FROM, degrees (0 = from north)."""
    return (math.degrees(math.atan2(-u, -v)) + 360) % 360


def uv_from(speed_kmh_, dir_from):
    """u, v in m/s from speed (km/h) and direction FROM (degrees)."""
    s = speed_kmh_ / KMH_PER_MS
    return -s * math.sin(math.radians(dir_from)), -s * math.cos(math.radians(dir_from))


def angle_diff(a, b):
    """Smallest absolute difference between two directions, 0..180."""
    return abs((a - b + 180) % 360 - 180)


def takeoff_components(speed, dir_from, facing):
    """Head- and crosswind (same unit as speed) for a slope that looks towards `facing`.
    Headwind > 0: the wind blows up the slope into the pilot's face. Crosswind > 0: from the pilot's right."""
    off = math.radians((dir_from - facing + 180) % 360 - 180)
    return speed * math.cos(off), speed * math.sin(off)


def gust_factor(gust, mean):
    """Gust factor G = gust / mean (None for calm air)."""
    if gust is None or mean is None or mean < 1.0:
        return None
    return gust / mean


def gust_spread(gust, mean):
    return None if gust is None or mean is None else max(0.0, gust - mean)


# ── profiles and interpolation ────────────────────────────────────────────────
def interp(x, x0, x1, y0, y1):
    return y0 + (x - x0) / (x1 - x0) * (y1 - y0)


def interp_height(levels, z, key):
    """Linear interpolation in height (as in HMD-S06). Returns (value, how)."""
    lv = sorted((l for l in levels if l.get(key) is not None and l.get('gh') is not None), key=lambda l: l['gh'])
    if len(lv) < 2:
        return None, 'missing'
    for a, b in zip(lv, lv[1:]):
        if a['gh'] <= z <= b['gh']:
            return interp(z, a['gh'], b['gh'], a[key], b[key]), f'{a["p"]}-{b["p"]}'
    a, b = (lv[0], lv[1]) if z < lv[0]['gh'] else (lv[-2], lv[-1])
    return interp(z, a['gh'], b['gh'], a[key], b[key]), 'extrapolated'


def column(levels, z_ground, u10=None, v10=None, t2=None, td2=None):
    """The model's air column above its own ground: a 10 m point first, then the pressure levels whose
    height is at least 50 m above the model ground (levels below ground are the model's fiction)."""
    col = []
    if u10 is not None and v10 is not None:
        col.append(dict(p='10m', gh=z_ground + 10.0, u=u10, v=v10, t=t2, td=td2))
    for l in sorted(levels, key=lambda l: -l['p']):
        if l.get('gh') is not None and l['gh'] >= z_ground + 50:
            col.append(dict(l))
    return col


def wind_at(col, z):
    """Wind speed (km/h) and direction FROM at height z: u and v are interpolated, not speed."""
    u, how = interp_height(col, z, 'u')
    v, _ = interp_height(col, z, 'v')
    if u is None or v is None:
        return None
    return dict(speed=round(speed_kmh(u, v), 1), dir=round(direction_from(u, v)), u=u, v=v, how=how)


def shear(col, z1, z2):
    """Vector wind change between two heights (km/h) and the turn of direction (degrees)."""
    a, b = wind_at(col, z1), wind_at(col, z2)
    if a is None or b is None:
        return None
    return dict(vector=round(speed_kmh(b['u'] - a['u'], b['v'] - a['v']), 1), turn=round(angle_diff(a['dir'], b['dir'])))


def interp_time(series, hours):
    """series: sorted [(hour, value)]; linear in time; None outside the range (never extrapolated)."""
    out = []
    for h in hours:
        val = None
        for (h0, y0), (h1, y1) in zip(series, series[1:]):
            if h0 <= h <= h1 and y0 is not None and y1 is not None:
                val = y0 if h1 == h0 else interp(h, h0, h1, y0, y1)
                break
        out.append(val)
    return out


# ── thermals ──────────────────────────────────────────────────────────────────
def cloudbase(t2_c, td2_c, z_ground):
    """Cumulus base (m above sea level) from the dew-point spread: about 125 m per kelvin."""
    if t2_c is None or td2_c is None:
        return None
    return z_ground + CLOUDBASE_M_PER_K * max(0.0, t2_c - td2_c)


def thermal_top(t2_c, z_ground, col, trigger=0.0):
    """Dry-parcel method: lift air at the 2 m temperature (+ trigger K) along the dry adiabat until it is
    no longer warmer than the environment. Returns the top height (m above sea level); the ground itself
    when the first layer is already stable; the highest level when the parcel never stops (capped there);
    None when the first level above the ground is more than COARSE m up (too coarse to say anything)."""
    env = sorted((l for l in col if l.get('t') is not None and l.get('gh') is not None and l['p'] != '10m'),
                 key=lambda l: l['gh'])
    if t2_c is None or len(env) < 2:
        return None
    z0, tp0 = z_ground + 2.0, t2_c + trigger
    zl, dl = z0, -trigger                     # at the start the parcel is `trigger` K warmer than the air
    for l in env:
        if l['gh'] <= z0:
            continue
        if zl == z0 and l['gh'] - z0 > COARSE:
            return None
        d = l['t'] - (tp0 - DRY_LAPSE * (l['gh'] - z0) / 1000.0)   # environment minus parcel
        if d >= 0:
            return z0 if dl >= 0 else zl + (0 - dl) / (d - dl) * (l['gh'] - zl)
        zl, dl = l['gh'], d
    return zl


def thermal_index(t2_c, z_ground, col, z):
    """TI at height z: environment temperature minus the dry parcel (°C). About -2 or lower: usable thermals."""
    t_env, _ = interp_height(col, z, 't')
    if t_env is None or t2_c is None:
        return None
    return round(t_env - (t2_c - DRY_LAPSE * (z - z_ground - 2.0) / 1000.0), 1)


def w_star(shf_wm2, zi_m, t2_c, p_hpa):
    """Deardorff convective velocity scale w* = (g/T · H/(rho cp) · zi)^(1/3), m/s. 0 when the surface cools."""
    if shf_wm2 is None or zi_m is None or t2_c is None or p_hpa is None or shf_wm2 <= 0:
        return 0.0 if shf_wm2 is not None and shf_wm2 <= 0 else None
    tk = t2_c + 273.15
    rho = p_hpa * 100 / (RD * tk)
    return (G0 / tk * shf_wm2 / (rho * CP) * zi_m) ** (1 / 3)


# ── the indicator ─────────────────────────────────────────────────────────────
def level(value, key):
    if value is None:
        return None
    th = THRESHOLDS[key]
    return 2 if value >= th['red'] else 1 if value >= th['amber'] else 0


def indicator(hour, facing):
    """hour: dict with any of wind, dir, gust, aloft, shear, w_star, cape. Returns per-check levels, the
    overall label and the reasons. Missing inputs are listed, never counted as fine."""
    checks, reasons, missing = {}, [], []
    spread = gust_spread(hour.get('gust'), hour.get('wind'))
    crossing = None
    if hour.get('dir') is not None and facing is not None and (hour.get('wind') or 0) >= 5:
        crossing = angle_diff(hour['dir'], facing)
    values = dict(wind=hour.get('wind'), gust=hour.get('gust'), spread=spread, crossing=crossing,
                  aloft=hour.get('aloft'), shear=hour.get('shear'), thermal=hour.get('w_star'), cape=hour.get('cape'))
    for k, v in values.items():
        lv = level(v, k)
        if k == 'crossing' and v is None and (hour.get('wind') or 0) < 5:
            lv = 0                                       # light and variable: direction does not count
        checks[k] = dict(value=None if v is None else round(v, 1), level=lv)
        if lv is None:
            missing.append(k)
        elif lv:
            reasons.append(f"{THRESHOLDS[k]['en']} {round(v)} {THRESHOLDS[k]['unit']} ≥ "
                           f"{THRESHOLDS[k]['red' if lv == 2 else 'amber']}")
    if hour.get('wind') and hour.get('dir') is not None and facing is not None:
        head, _ = takeoff_components(hour['wind'], hour['dir'], facing)
        if head < -5:                                   # tailwind on launch
            checks['crossing']['level'] = 2
            reasons.append(f'tailwind {round(-head)} km/h on this slope')
    worst = max([c['level'] for c in checks.values() if c['level'] is not None] or [0])
    return dict(label=LABELS[worst], worst=worst, checks=checks, reasons=reasons, missing=missing)


# ── forecast vs observation ───────────────────────────────────────────────────
def errors(pairs):
    """pairs: [(forecast, observed)]. Bias (mean of f - o), MAE, RMSE, n."""
    p = [(f, o) for f, o in pairs if f is not None and o is not None]
    if not p:
        return dict(n=0, bias=None, mae=None, rmse=None)
    d = [f - o for f, o in p]
    return dict(n=len(p), bias=round(sum(d) / len(d), 1), mae=round(sum(map(abs, d)) / len(d), 1),
                rmse=round(math.sqrt(sum(x * x for x in d) / len(d)), 1))


def lag1_autocorr(xs):
    """Lag-1 autocorrelation of a series (how much one day's error predicts the next day's)."""
    xs = [x for x in xs if x is not None]
    if len(xs) < 3:
        return None
    m = sum(xs) / len(xs)
    num = sum((a - m) * (b - m) for a, b in zip(xs, xs[1:]))
    den = sum((a - m) ** 2 for a in xs)
    return None if den == 0 else round(num / den, 2)


def effective_n(n, r1):
    """Effective number of independent samples for an AR(1)-like series: n (1 - r) / (1 + r), at most n."""
    if r1 is None or n == 0:
        return None
    r = max(0.0, min(0.99, r1))          # negative r is treated as 0: we never claim more than n samples
    return round(n * (1 - r) / (1 + r), 1)


def paired_abs_diff(pairs_a, pairs_b, n_eff=None):
    """Mean of |error A| - |error B| over the same cases, with a rough standard error (sd / sqrt(n_eff))."""
    d = [abs(fa - o) - abs(fb - o2) for (fa, o), (fb, o2) in zip(pairs_a, pairs_b)
         if None not in (fa, o, fb, o2)]
    if len(d) < 3:
        return None
    m = sum(d) / len(d)
    sd = math.sqrt(sum((x - m) ** 2 for x in d) / (len(d) - 1))
    ne = n_eff or len(d)
    return dict(n=len(d), mean=round(m, 2), se=round(sd / math.sqrt(ne), 2))
