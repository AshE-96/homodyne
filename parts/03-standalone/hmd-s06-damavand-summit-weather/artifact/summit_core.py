"""summit_core.py · HMD-S06 · the physics and the alert logic of the summit service, standard library only.

Everything the page shows is computed here from model numbers at grid points:
  * standard atmosphere (ISA): which height a pressure level sits at on an average day;
  * three ways to get a summit temperature: the model's own 2 m value (at the model's lower, smoothed
    "Damavand"), the same corrected with a lapse rate, and the free-air value interpolated between
    pressure levels at the real height;
  * wind from (u, v); relative humidity from specific humidity (for AIFS, which has no r);
  * wind chill: Environment Canada / US NWS 2001 formula (T in °C, V in km/h at 10 m);
  * the editorial alert thresholds and the go / no-go window logic.
Nothing here is a safety rule. The thresholds are an editorial choice and are printed on the page as such.
"""
import math

G0 = 9.80665          # m s-2, standard gravity (geopotential -> geopotential height)
RD = 287.053          # J kg-1 K-1, dry air (ISA value)
ISA_T0, ISA_P0, ISA_L = 288.15, 1013.25, 0.0065   # K, hPa, K/m (troposphere)
LAPSE_STD = 6.5       # K per km, the "standard" lapse rate used in the simple correction

# Places. Summit and hut coordinates: see ../sources.md (S10, S11) - both [VERIFY] before recording.
SITES = {
    'summit': dict(name_fa='قلهٔ دماوند', name_en='Damavand summit', lat=35.9553, lon=52.1100, z=5610),
    'camp3': dict(name_fa='بارگاه سوم', name_en='Bargah-e Sevom (Camp 3)', lat=35.9317, lon=52.1083, z=4220),
}

# Editorial thresholds (km/h, °C, %, mm per 6 h). Amber = "near", red = "over". Chosen by the editor,
# loosely anchored on Environment Canada's frostbite bands (-28: skin freezes in 10-30 min; -40: 5-10 min).
THRESHOLDS = dict(
    wind=dict(amber=40, red=60, unit='km/h', fa='باد', en='wind'),
    chill=dict(amber=-28, red=-40, unit='°C', fa='سرمای باد', en='wind chill'),
    cloud=dict(amber=90, red=None, unit='% RH', fa='در ابر (رطوبت نسبی)', en='in cloud (RH)'),
    precip=dict(amber=1.0, red=5.0, unit='mm/6h', fa='بارش', en='precipitation'),
)
SPREAD_WIND = 25      # km/h: if the models' summit winds differ by more than this, the step is "uncertain"


def isa_height(p_hpa):
    """Height (m) of a pressure level in the ICAO standard atmosphere (troposphere only)."""
    return ISA_T0 / ISA_L * (1 - (p_hpa / ISA_P0) ** (RD * ISA_L / G0))


def isa_pressure(z):
    return ISA_P0 * (1 - ISA_L * z / ISA_T0) ** (G0 / (RD * ISA_L))


def hypsometric_thickness(p_low, p_high, t_mean_k):
    """Thickness (m) between two pressure levels for a mean layer temperature (K)."""
    return RD * t_mean_k / G0 * math.log(p_low / p_high)


def wind_chill(t_c, v_kmh):
    """Wind chill index (Environment Canada / NWS 2001). Defined for T <= 10 °C and V >= 4.8 km/h;
    outside that range the air temperature is returned unchanged."""
    if t_c is None or v_kmh is None:
        return None
    if t_c > 10 or v_kmh < 4.8:
        return t_c
    v16 = v_kmh ** 0.16
    return 13.12 + 0.6215 * t_c - 11.37 * v16 + 0.3965 * t_c * v16


def wind_chill_f(t_f, v_mph):
    """The same formula in US units (NWS): used only to cross-check the metric version."""
    v16 = v_mph ** 0.16
    return 35.74 + 0.6215 * t_f - 35.75 * v16 + 0.4275 * t_f * v16


def speed_kmh(u, v):
    return math.hypot(u, v) * 3.6


def direction_from(u, v):
    """Meteorological direction the wind blows FROM, degrees."""
    return (math.degrees(math.atan2(-u, -v)) + 360) % 360


def rh_from_q(q, t_k, p_hpa):
    """Relative humidity (%, over water) from specific humidity (kg/kg), temperature (K), pressure (hPa)."""
    e = q * p_hpa / (0.622 + 0.378 * q)
    tc = t_k - 273.15
    es = 6.112 * math.exp(17.67 * tc / (tc + 243.5))     # Bolton (1980)
    return max(0.0, min(100.0, 100 * e / es))


def lapse_correct(t_c, z_from, z_to, lapse=LAPSE_STD):
    """Move a temperature from height z_from to z_to with a fixed lapse rate (K/km)."""
    return t_c - lapse * (z_to - z_from) / 1000.0


def interp_height(levels, z, key):
    """Linear interpolation in height between the two pressure levels around z.
    levels: list of dicts with 'p', 'gh' (m) and the key; sorted any order. Extrapolates from the
    nearest pair if z is outside, and says so."""
    lv = sorted((l for l in levels if l.get(key) is not None and l.get('gh') is not None), key=lambda l: l['gh'])
    if len(lv) < 2:
        return None, 'missing'
    for a, b in zip(lv, lv[1:]):
        if a['gh'] <= z <= b['gh']:
            f = (z - a['gh']) / (b['gh'] - a['gh'])
            return a[key] + f * (b[key] - a[key]), f'{a["p"]:.0f}-{b["p"]:.0f} hPa'
    a, b = (lv[0], lv[1]) if z < lv[0]['gh'] else (lv[-2], lv[-1])
    f = (z - a['gh']) / (b['gh'] - a['gh'])
    return a[key] + f * (b[key] - a[key]), 'extrapolated'


def free_air(levels, z):
    """Free-air conditions at height z from pressure-level data (t in °C, u/v in m/s, rh in %)."""
    t, how = interp_height(levels, z, 't')
    u, _ = interp_height(levels, z, 'u')
    v, _ = interp_height(levels, z, 'v')
    rh, _ = interp_height(levels, z, 'rh')
    if t is None or u is None or v is None:
        return None
    w = speed_kmh(u, v)
    return dict(t=round(t, 1), wind=round(w, 1), dir=round(direction_from(u, v)),
                chill=round(wind_chill(t, w), 1), rh=None if rh is None else round(rh), layer=how)


def level(value, th):
    """0 = under the amber line, 1 = amber ("near"), 2 = red ("over"). Wind chill counts downwards."""
    if value is None:
        return None
    a, r = th['amber'], th['red']
    if a < 0 or (r is not None and r < 0):          # colder is worse
        return 2 if r is not None and value <= r else 1 if value <= a else 0
    return 2 if r is not None and value >= r else 1 if value >= a else 0


def step_flags(fa, precip=None):
    """Alert levels for one model at one time step."""
    if fa is None:
        return None
    f = dict(wind=level(fa['wind'], THRESHOLDS['wind']), chill=level(fa['chill'], THRESHOLDS['chill']),
             cloud=level(fa['rh'], THRESHOLDS['cloud']), precip=level(precip, THRESHOLDS['precip']))
    f['worst'] = max(v for v in f.values() if v is not None)
    return f


def combine(per_model, member_winds=None):
    """One time step across models (and optionally ensemble members).
    Returns the label the page shows; never 'safe'.
      'over'      at least one model is red
      'near'      at least one model is amber
      'under'     every model is under every amber line
      +uncertain  when the models' winds differ by more than SPREAD_WIND, or ensemble members split
    """
    flags = [m['flags'] for m in per_model if m.get('flags')]
    if not flags:
        return dict(label='no data', worst=None, n=0)
    worst = max(f['worst'] for f in flags)
    winds = [m['fa']['wind'] for m in per_model if m.get('fa')]
    spread = max(winds) - min(winds) if len(winds) > 1 else 0.0
    n_red = sum(1 for f in flags if f['worst'] == 2)
    out = dict(worst=worst, n=len(flags), n_red=n_red, n_amber=sum(1 for f in flags if f['worst'] == 1),
               spread=round(spread, 1), label=['under', 'near', 'over'][worst])
    uncertain = spread > SPREAD_WIND or (0 < n_red < len(flags))
    if member_winds:
        p = sum(1 for w in member_winds if w >= THRESHOLDS['wind']['amber']) / len(member_winds)
        out['p_wind_amber'] = round(p, 2)
        uncertain = uncertain or 0.1 < p < 0.9
    out['uncertain'] = uncertain
    return out


def windows(steps, min_len=2):
    """Runs of consecutive steps that are 'under' for every model and not uncertain.
    These are 'quieter windows in the models', not safe windows."""
    runs, cur = [], []
    for s in steps:
        c = s['combined']
        if c.get('worst') == 0 and not c.get('uncertain'):
            cur.append(s['valid'])
        else:
            if len(cur) >= min_len:
                runs.append((cur[0], cur[-1]))
            cur = []
    if len(cur) >= min_len:
        runs.append((cur[0], cur[-1]))
    return runs
