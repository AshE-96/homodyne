#!/usr/bin/env python3
"""HMD-K01 · rank_estimate.py — درصد → a coarse rank RANGE, always labelled ESTIMATE.

    python3 rank_estimate.py --group tajrobi --year 1405 --pct bio=62,chem=58,phys=55,math=50
    python3 rank_estimate.py --selftest

What public evidence allows (tables/SOURCE.txt, read 2026-11-27):
- solid: the final score is 40% exam + 60% school records in 1404 and 1405 (50/50 in 1403), and the group sizes;
- missing: any official percent→rank or تراز→rank table, the per-subject national mean/SD needed to rebuild تراز,
  official 1404/1405 coefficients, and dated «آخرین رتبهٔ قبولی» for پزشکی تهران or Sharif.
So this script does NOT compute a rank. It compares the model's coefficient-weighted percents with a handful of
published کارنامه rows (undated, unverified; see tables/anchors.json) on the subjects both have, and reports the
range between the nearest row it beats and the nearest row it does not beat. Two bounds for school records:
- full marks: the range itself (it assumes the model's records would be as strong as those students' records);
- average grades: no range — records carry 60% of the score, and no public table says how far that moves a rank.
No university is predicted; the card only says which published rows the model's percents are above.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FACTS = json.loads((HERE / 'tables' / 'konkur_facts.json').read_text(encoding='utf-8'))
ANCHORS = json.loads((HERE / 'tables' / 'anchors.json').read_text(encoding='utf-8'))
FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def fa_n(n):
    return f'{n:,}'.replace(',', '٬').translate(FA)


def weighted(percents, group, subjects=None):
    w = FACTS['exam_weights'][group]
    use = [s for s in (subjects or percents) if s in w and percents.get(s) is not None]
    if not use:
        return None
    return sum(w[s] * percents[s] for s in use) / sum(w[s] for s in use)


def estimate(group, year, percents):
    """A dict with the range, the two school-record bounds, what it is beside, and the reasons it is coarse."""
    percents = {k: v for k, v in (percents or {}).items() if v is not None}
    share = FACTS['sabeqe_share'].get(str(year), {})
    n = FACTS['participants'].get(group, {}).get(str(year))
    out = {'label': 'ESTIMATE', 'evidence': 'very low', 'group': group, 'year': year,
           'weighted_exam_percent': weighted(percents, group), 'participants': n,
           'school_records_share': share.get('school_records'), 'above': [], 'below': [],
           'why_coarse': ['no official percent→rank or تراز→rank table', 'school records carry '
                          f'{round(100 * (share.get("school_records") or 0.6))}% of the final score',
                          'anchor rows are undated consultancy pages, probably recycled',
                          f'exam coefficients for {year} are ' + FACTS['exam_weights']['status'].get(str(year), 'assumed')]}
    for a in ANCHORS.get(group, []):
        common = [s for s in a['percents'] if s in percents]
        if len(common) < 2:
            continue
        mine, theirs = weighted(percents, group, common), weighted(a['percents'], group, common)
        side = 'above' if mine >= theirs else 'below'
        out[side].append({'rank_national': a['rank_national'], 'label_fa': a['label_fa'], 'label_en': a['label_en'],
                          'mine': round(mine, 1), 'theirs': round(theirs, 1), 'subjects': common})
    best_not_beaten = max((x['rank_national'] for x in out['below']), default=None)
    worst_beaten = min((x['rank_national'] for x in out['above']), default=None)
    if worst_beaten is None and best_not_beaten is None:
        rng, kind = None, 'none'
    elif worst_beaten is None:
        rng, kind = (best_not_beaten, None), 'worse_than'
    elif best_not_beaten is None:
        rng, kind = (None, worst_beaten), 'better_than'
    elif best_not_beaten <= worst_beaten:
        rng, kind = (best_not_beaten, worst_beaten), 'between'
    else:                                                   # rows disagree with each other: show the whole span
        rng, kind = (min(worst_beaten, best_not_beaten), max(worst_beaten, best_not_beaten)), 'anchors_disagree'
    out['range_full_marks'], out['range_kind'] = rng, kind
    out['range_average_grades'] = None
    out['summary_fa'], out['summary_en'], out['range_fa'] = texts(out)
    return out


def texts(e):
    lo, hi = e['range_full_marks'] or (None, None)
    k = e['range_kind']
    if k == 'between' or k == 'anchors_disagree':
        fa_r, en_r = f'رتبهٔ کشوری حدود {fa_n(lo)} تا {fa_n(hi)}', f'national rank ~{lo:,}–{hi:,}'
    elif k == 'better_than':
        fa_r, en_r = f'بهتر از رتبهٔ حدود {fa_n(hi)}', f'better than ~{hi:,}'
    elif k == 'worse_than':
        fa_r, en_r = f'پایین‌تر از رتبهٔ حدود {fa_n(lo)} (بازه باز است)', f'below ~{lo:,} (open range)'
    else:
        fa_r, en_r = 'بازه‌ای نمی‌شود گفت (ردیف قابل مقایسه نیست)', 'no range (no comparable published row)'
    if k == 'anchors_disagree':
        fa_r, en_r = fa_r + '؛ ردیف‌های منتشرشده با هم نمی‌خوانند', en_r + '; published rows disagree'
    side = '، '.join(x['label_fa'] for x in e['above'][:2])
    fa_s = (f'تخمین · {fa_r} — فقط با فرض سوابق تحصیلی نزدیک به کامل؛ با معدل متوسط، بازه‌ای نمی‌شود گفت.'
            + (f' درصدهایش بالاتر از: {side}.' if side else ''))
    en_s = (f'ESTIMATE · {en_r} — only if school records were near full marks; with average grades no range can be '
            'given.' + (' Percents above: ' + ', '.join(x['label_en'] for x in e['above'][:2]) + '.' if e['above'] else ''))
    return fa_s, en_s, fa_r


def selftest():
    e = estimate('tajrobi', 1405, {'bio': 70, 'chem': 68, 'phys': 80, 'math': 70})
    assert e['label'] == 'ESTIMATE' and e['range_average_grades'] is None
    assert e['range_kind'] in ('between', 'anchors_disagree') and 'ESTIMATE' in e['summary_en'], e
    top = estimate('tajrobi', 1405, {'bio': 99, 'chem': 99, 'phys': 99, 'math': 99})
    assert top['range_kind'] == 'better_than' and top['range_full_marks'] == (None, 1)
    low = estimate('riazi', 1404, {'math': 10, 'phys': 5, 'chem': 0})
    assert low['range_kind'] == 'worse_than' and low['range_full_marks'][0] == 829
    assert estimate('riazi', 1403, {'math': 50})['range_kind'] == 'none'      # one subject is not comparable
    assert abs(weighted({'math': 60, 'phys': 30, 'chem': 30}, 'riazi') - (12 * 60 + 9 * 30 + 7 * 30) / 28) < 1e-9
    assert e['participants'] == 451522 and e['school_records_share'] == 0.6
    assert 'تخمین' in e['summary_fa'] and '٬' in fa_n(1000)
    print('rank_estimate selftest passed')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--group', choices=('tajrobi', 'riazi'))
    ap.add_argument('--year', type=int, choices=(1403, 1404, 1405))
    ap.add_argument('--pct', help='bio=62,chem=58,…  (Konkur درصد with −1/3)')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.group and a.year and a.pct):
        ap.print_help()
        return 0
    e = estimate(a.group, a.year, {k: float(v) for k, v in (x.split('=') for x in a.pct.split(','))})
    print(json.dumps(e, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
