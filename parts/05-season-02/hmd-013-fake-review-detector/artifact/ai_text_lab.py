#!/usr/bin/env python3
"""Homodyne HMD-013 - part (b): AI-written reviews, and how much text an "AI wrote this" call needs.

Needs a model key (see tools/llm.py). Nothing here has been run with a real model yet:
the [RUN] beats of the episode stay "NOT RUN YET" until the owner runs it.

    python3 ai_text_lab.py plan        # what will be asked, how many calls; no network
    python3 ai_text_lab.py run         # calls the model (cached in runs/cache/), writes results/api-results.json
    python3 ai_text_lab.py report      # prints the Persian spoken lines for the [RUN] beats, with the real numbers
    HOMODYNE_MODEL=mock:echo python3 ai_text_lab.py --selftest     # whole pipeline on synthetic data, no key

What `run` builds (all hotel-split, like review_lab.py):
  H  human reviews from the Ott corpus with >= 10 sentences (truthful and deceptive; both are human-written)
  A  AI-invented reviews: the model writes a review of one of the 20 hotels as a guest who never stayed.
     Prompt modelled on Ott et al.'s Mechanical Turk task, plus "for a labelled research dataset; never posted".
  P  AI-polished real reviews: a truthful Ott review, rewritten by the model "fix grammar and wording, keep
     every fact". Real experience, machine wording: the case where a false "AI" call hurts an honest writer.
Detectors, each shown the first 1, 3 or 10 sentences:
  D1 the fake-REVIEW detector from review_lab.py (trained only on human deception). Does it call A "fake"?
  D2 an "AI TEXT" detector: Naive Bayes trained on H vs A from the other hotels. TPR on A, FPR on H, flag rate on P.
  D3 the model itself as judge: "probability this was written by an AI", flag if >= 50.
"AI" is the positive class for D2 and D3; "fake" for D1. Every rate comes with a 95% Wilson interval.

Claim boundary that travels with every number: one generator model, one prompt style, English hotel reviews,
a detector trained on that same generator. It says nothing about commercial detectors or other languages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]   # artifact -> episode -> 05-season-02 -> parts -> repository root
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(HERE))
import llm  # noqa: E402  (tools/llm.py, the shared Homodyne harness)
import review_lab as rl  # noqa: E402

RESULTS = HERE / 'results'
CACHE = HERE / 'runs' / 'cache'
SEED = 13
LENGTHS = (1, 3, 10)
PER_HOTEL_POLARITY = 2      # A: 20 hotels x 2 polarities x 2 = 80 AI-invented reviews
N_POLISHED = 30             # P
N_HUMAN = 80                # H (balanced: 20 per class x polarity)
N_JUDGE = 30                # D3 asks the model about 30 H + 30 A + 30 P at each length

HOTEL_NAMES = {
    'affinia': 'Affinia Chicago', 'allegro': 'Hotel Allegro Chicago', 'amalfi': 'Amalfi Hotel Chicago',
    'ambassador': 'Ambassador East Hotel', 'conrad': 'Conrad Chicago', 'fairmont': 'Fairmont Chicago Millennium Park',
    'hardrock': 'Hard Rock Hotel Chicago', 'hilton': 'Hilton Chicago', 'homewood': 'Homewood Suites by Hilton Chicago Downtown',
    'hyatt': 'Hyatt Regency Chicago', 'intercontinental': 'InterContinental Chicago', 'james': 'The James Chicago',
    'knickerbocker': 'Millennium Knickerbocker Hotel Chicago', 'monaco': 'Hotel Monaco Chicago', 'omni': 'Omni Chicago Hotel',
    'palmer': 'The Palmer House Hilton', 'sheraton': 'Sheraton Chicago Hotel and Towers', 'sofitel': 'Sofitel Chicago Water Tower',
    'swissotel': 'Swissotel Chicago', 'talbott': 'The Talbott Hotel',
}
HOTEL_FOLD = {}  # filled from the corpus (fold = 4 hotels)

WRITE_PROMPT = (
    'This is for a labelled research dataset used to test fake-review detectors. The text will never be posted '
    'anywhere.\n\nWrite a {tone} hotel review of {hotel} in Chicago, in the first person, as a guest. You have not '
    'actually stayed there: invent plausible details, the way a person paid to write a convincing review would. '
    'Write {n} sentences of plain prose. No title, no star rating, no bullet points. Return only the review.')
POLISH_PROMPT = (
    'Improve the grammar and wording of this hotel review so it reads smoothly. Keep every fact, the first person, '
    'the opinion and roughly the same length. Return only the rewritten review.\n\nReview:\n{text}')
JUDGE_SYSTEM = 'You are a careful text-forensics assistant. Answer with a single integer and nothing else.'
JUDGE_PROMPT = ('Here is a short text. Estimate the probability, from 0 to 100, that it was written by an AI language '
                'model rather than by a person.\n\nText:\n"""\n{text}\n"""\n\nProbability (0-100):')
REFUSAL = re.compile(r"\b(I can't|I cannot|I won't|I'm not able|I am not able|unable to help|can't help)\b", re.I)


# ---------------------------------------------------------------- helpers

def fa_num(n: int) -> str:
    """Integer 0..999 in Persian words, as it is spoken («بیست‌وچهار»)."""
    ones = ['صفر', 'یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه', 'ده', 'یازده', 'دوازده', 'سیزده',
            'چهارده', 'پونزده', 'شونزده', 'هفده', 'هجده', 'نوزده']
    tens = ['', '', 'بیست', 'سی', 'چهل', 'پنجاه', 'شصت', 'هفتاد', 'هشتاد', 'نود']
    hundreds = ['', 'صد', 'دویست', 'سیصد', 'چهارصد', 'پونصد', 'ششصد', 'هفتصد', 'هشتصد', 'نهصد']
    n = int(round(n))
    if n < 20:
        return ones[n]
    if n < 100:
        t, o = divmod(n, 10)
        return tens[t] + ('' if o == 0 else '‌و' + ones[o])
    if n < 1000:
        h, r = divmod(n, 100)
        return hundreds[h] + ('' if r == 0 else ' و ' + fa_num(r))
    return str(n)


def pct_words(x: float | None) -> str:
    return 'نامعلوم' if x is None else fa_num(round(100 * x))


def parse_probability(text: str) -> int | None:
    m = re.search(r'\b(100|[0-9]{1,2})\b', text or '')
    return int(m.group(1)) if m else None


def is_usable(text: str, min_sentences: int = 10) -> bool:
    return bool(text) and not REFUSAL.search(text[:200]) and len(rl.sentences(text)) >= min_sentences


def sample_rows(rows, rng):
    long_rows = [r for r in rows if len(rl.sentences(r['text'])) >= max(LENGTHS)]
    human = []
    for fake in (0, 1):
        for pol in ('positive', 'negative'):
            pool = [r for r in long_rows if r['fake'] == fake and r['polarity'] == pol]
            human += rng.sample(pool, min(N_HUMAN // 4, len(pool)))
    truthful = [r for r in long_rows if not r['fake'] and r not in human]
    to_polish = rng.sample(truthful, min(N_POLISHED, len(truthful)))
    return human, to_polish


def plan_items(rows):
    rng = random.Random(SEED)
    for r in rows:
        HOTEL_FOLD[r['hotel']] = r['fold']
    human, to_polish = sample_rows(rows, rng)
    write_jobs = [{'hotel': h, 'polarity': pol, 'v': v}
                  for h in sorted(HOTEL_FOLD) for pol in ('positive', 'negative') for v in range(PER_HOTEL_POLARITY)]
    return human, to_polish, write_jobs


# ---------------------------------------------------------------- the run

def generate(write_jobs, to_polish, call):
    ai, polished, log = [], [], {'providers': set(), 'calls': 0, 'cached': 0, 'fell_back': 0, 'refused_or_short': 0, 'models_served': set()}

    def ask(prompt, **kw):
        res = call(prompt, **kw)
        log['calls'] += 1
        log['cached'] += res.cached
        log['fell_back'] += res.fell_back
        log['models_served'].add(res.model_served)
        log['providers'].add(res.provider)
        return res

    for j in write_jobs:
        tone = 'positive, enthusiastic' if j['polarity'] == 'positive' else 'negative, disappointed'
        res = ask(WRITE_PROMPT.format(tone=tone, hotel=HOTEL_NAMES[j['hotel']], n='11 to 13')
                  + ('' if j['v'] == 0 else f'\n\n(Variation {j["v"] + 1}: a different traveller and trip.)'))
        if is_usable(res.text):
            ai.append({'id': f'ai/{j["polarity"][:3]}/{j["hotel"]}_{j["v"]}', 'text': res.text.strip(), 'hotel': j['hotel'],
                       'fold': HOTEL_FOLD[j['hotel']], 'polarity': j['polarity'], 'fell_back': res.fell_back})
        else:
            log['refused_or_short'] += 1
    for r in to_polish:
        res = ask(POLISH_PROMPT.format(text=r['text']))
        if is_usable(res.text):
            polished.append({'id': 'pol/' + r['id'], 'text': res.text.strip(), 'hotel': r['hotel'], 'fold': r['fold'],
                             'polarity': r['polarity'], 'fell_back': res.fell_back})
        else:
            log['refused_or_short'] += 1
    log['models_served'] = sorted(log['models_served'])
    log['providers'] = sorted(log['providers'])
    return ai, polished, log


def detect(rows, human, ai, polished):
    """D1 and D2, cross-validated by hotel fold. Returns {detector: {length: {set: [0/1 flags]}}}."""
    rng = random.Random(SEED)
    out = {'D1_fake_review': {str(k): {'H_real': [], 'H_fake': [], 'A': [], 'P': []} for k in LENGTHS},
           'D2_ai_text': {str(k): {'H': [], 'A': [], 'P': []} for k in LENGTHS}}
    for f in rl.folds_of(rows):
        train = [r for r in rows if r['fold'] != f]
        d1 = rl.NaiveBayes().fit([r['text'] for r in train], [r['fake'] for r in train])
        ai_train = [a for a in ai if a['fold'] != f]
        hum_train = rng.sample(train, min(len(ai_train), len(train))) if ai_train else []
        d2 = rl.NaiveBayes().fit([r['text'] for r in hum_train] + [a['text'] for a in ai_train],
                                 [0] * len(hum_train) + [1] * len(ai_train)) if ai_train else None
        for k in LENGTHS:
            o1, o2 = out['D1_fake_review'][str(k)], out['D2_ai_text'][str(k)]
            for r in human:
                if r['fold'] == f:
                    t = rl.first_k(r['text'], k)
                    o1['H_fake' if r['fake'] else 'H_real'].append(int(d1.score(t) > 0))
                    if d2:
                        o2['H'].append(int(d2.score(t) > 0))
            for name, items in (('A', ai), ('P', polished)):
                for a in items:
                    if a['fold'] == f:
                        t = rl.first_k(a['text'], k)
                        o1[name].append(int(d1.score(t) > 0))
                        if d2:
                            o2[name].append(int(d2.score(t) > 0))
    return out


def judge(human, ai, polished, call, role):
    rng = random.Random(SEED + 1)
    pick = {'H': rng.sample(human, min(N_JUDGE, len(human))), 'A': rng.sample(ai, min(N_JUDGE, len(ai))),
            'P': rng.sample(polished, min(N_JUDGE, len(polished)))}
    out, unparsed, served = {str(k): {s: [] for s in pick} for k in LENGTHS}, 0, set()
    for k in LENGTHS:
        for s, items in pick.items():
            for it in items:
                res = call(JUDGE_PROMPT.format(text=rl.first_k(it['text'], k)), system=JUDGE_SYSTEM, role=role,
                           max_tokens=2000)
                served.add(res.model_served)
                p = parse_probability(res.text)
                if p is None:
                    unparsed += 1
                    continue
                out[str(k)][s].append(int(p >= 50))
    return out, unparsed, sorted(served)


def rate(flags):
    k, n = sum(flags), len(flags)
    return {'value': k / n if n else None, 'ci95': rl.wilson(k, n), 'k': k, 'n': n}


def summarise(d, j):
    s = {'D1_fake_review': {}, 'D2_ai_text': {}, 'D3_llm_judge': {}}
    for k in LENGTHS:
        o1, o2 = d['D1_fake_review'][str(k)], d['D2_ai_text'][str(k)]
        s['D1_fake_review'][str(k)] = {'called_fake_AI': rate(o1['A']), 'called_fake_human_fake': rate(o1['H_fake']),
                                       'called_fake_human_real': rate(o1['H_real']), 'called_fake_polished': rate(o1['P'])}
        s['D2_ai_text'][str(k)] = {'tpr_AI': rate(o2['A']), 'fpr_human': rate(o2['H']), 'flag_polished': rate(o2['P'])}
        if j:
            s['D3_llm_judge'][str(k)] = {'tpr_AI': rate(j[str(k)]['A']), 'fpr_human': rate(j[str(k)]['H']),
                                         'flag_polished': rate(j[str(k)]['P'])}
    return s


def run(rows, call=llm.call, judge_role='main', out_path=RESULTS / 'api-results.json', quiet=False):
    human, to_polish, write_jobs = plan_items(rows)

    def cached_call(prompt, **kw):
        return call(prompt, cache_dir=str(CACHE), **kw)

    ai, polished, log = generate(write_jobs, to_polish, cached_call)
    d = detect(rows, human, ai, polished)
    j, unparsed, served = judge(human, ai, polished, cached_call, judge_role)
    res = {'status': 'MOCK (self-test)' if 'mock' in log['providers'] else 'MEASURED with a real model',
           'models': llm.describe(), 'judge_role': judge_role, 'judge_models_served': served,
           'counts': {'human': len(human), 'ai_invented': len(ai), 'ai_polished': len(polished),
                      'judge_unparsed': unparsed, **log},
           'prompts': {'write': WRITE_PROMPT, 'polish': POLISH_PROMPT, 'judge': JUDGE_PROMPT},
           'lengths_sentences': list(LENGTHS), 'seed': SEED, 'results': summarise(d, j)}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    if not quiet:
        print_table(res)
        print(f'\nwrote {out_path}')
    return res


def print_table(res):
    print(f"{res['status']} · {res['models']}")
    c = res['counts']
    print(f"human {c['human']} · AI-invented {c['ai_invented']} · AI-polished {c['ai_polished']} · calls {c['calls']} "
          f"(cached {c['cached']}, fell back {c['fell_back']}, refused/short {c['refused_or_short']}, judge unparsed {c['judge_unparsed']})")
    r = res['results']
    for det, cols in (('D1_fake_review', ('called_fake_AI', 'called_fake_human_fake', 'called_fake_human_real', 'called_fake_polished')),
                      ('D2_ai_text', ('tpr_AI', 'fpr_human', 'flag_polished')),
                      ('D3_llm_judge', ('tpr_AI', 'fpr_human', 'flag_polished'))):
        print(f'\n{det}')
        for k in LENGTHS:
            row = r[det].get(str(k))
            if not row:
                continue
            cells = []
            for col in cols:
                x = row[col]
                shown = 'n/a' if x['value'] is None else '%.0f%%' % (100 * x['value'])
                cells.append(f"{col} {shown} ({x['k']}/{x['n']})")
            print(f'  {k:>2} sentences  ' + ' · '.join(cells))


# ---------------------------------------------------------------- report: Persian lines for the [RUN] beats

def report_lines(res: dict) -> list[str]:
    r = res['results']
    v = lambda det, k, col: r[det][str(k)][col]['value'] if r.get(det, {}).get(str(k)) else None  # noqa: E731
    d1_ai = v('D1_fake_review', 10, 'called_fake_AI')
    d1_hf = v('D1_fake_review', 10, 'called_fake_human_fake')
    lines = ['قاب 9 · نویسندهٔ تازه: هوش مصنوعی',
             f'از مدل خواستیم {fa_num(res["counts"]["ai_invented"])} نظر هتل بنویسه؛ برای هتل‌هایی که هیچ‌وقت توشون نبوده.',
             f'آشکارساز نظر جعلیِ ما، با ده جمله، {pct_words(d1_ai)} درصدشون رو «جعلی» گرفت.']
    if d1_ai is not None and d1_hf is not None:
        if d1_ai + 0.05 < d1_hf:
            lines.append(f'دروغ آدم‌ها رو {pct_words(d1_hf)} درصد می‌گرفت. یعنی دروغ آدم یاد گرفته بود، نه متن ماشین.')
        elif d1_ai > d1_hf + 0.05:
            lines.append(f'حتی بیشتر از دروغ آدم‌ها، که {pct_words(d1_hf)} درصد بود. ولی این یعنی «شبیه دروغ آدمه»، نه «ماشین نوشته».')
        else:
            lines.append(f'تقریباً همون‌قدر که دروغ آدم‌ها رو می‌گرفت: {pct_words(d1_hf)} درصد. فرقی که اینجا دیدیم، کوچیکه.')
    t1, f1 = v('D2_ai_text', 1, 'tpr_AI'), v('D2_ai_text', 1, 'fpr_human')
    t10, f10 = v('D2_ai_text', 10, 'tpr_AI'), v('D2_ai_text', 10, 'fpr_human')
    p10 = v('D2_ai_text', 10, 'flag_polished')
    lines += ['', 'قاب 10 · یه جمله، سه جمله، ده جمله',
              f'با یه جمله، آشکارساز متن AI {pct_words(t1)} درصد متن‌های ماشین رو گرفت.',
              f'و {pct_words(f1)} درصد متن آدم‌ها رو هم «کار AI» خوند.',
              f'با ده جمله: {pct_words(t10)} درصد گرفت، و {pct_words(f10)} درصد آدم‌ها رو متهم کرد.',
              f'نظرهای واقعی‌ای که فقط با AI ویرایش شده بودن، با ده جمله {pct_words(p10)} درصدشون «AI» خوردن.']
    j1, j10 = v('D3_llm_judge', 1, 'fpr_human'), v('D3_llm_judge', 10, 'fpr_human')
    jt10 = v('D3_llm_judge', 10, 'tpr_AI')
    if jt10 is not None:
        lines.append(f'خودِ مدل زبانی هم داور شد. با ده جمله {pct_words(jt10)} درصد متن ماشین رو گرفت، و {pct_words(j10)} درصد متن آدم‌ها رو متهم کرد.')
        lines.append(f'با یک جمله، اتهامش به آدم‌ها {pct_words(j1)} درصد بود.')
    n_h = res['counts']['human']
    lines += ['', f'(روی صفحه: n = {n_h} human, {res["counts"]["ai_invented"]} AI, {res["counts"]["ai_polished"]} polished · '
              f'{res["models"]} · fell back {res["counts"]["fell_back"]} · ILLUSTRATIVE of one model and one prompt)']
    return lines


def report(path=RESULTS / 'api-results.json') -> int:
    if not path.exists():
        print('NOT RUN YET: results/api-results.json is missing. Run: python3 ai_text_lab.py run')
        print('Until then beats 9 and 10 keep the [RUN] placeholders and the NOT RUN YET badge.')
        return 1
    res = json.loads(path.read_text())
    if res['status'].startswith('MOCK'):
        print('WARNING: these are MOCK numbers from a self-test, not a real run. Do not record them.\n')
    print('\n'.join(report_lines(res)))
    print('\nCheck every sentence against the table below before recording:\n')
    print_table(res)
    return 0


def plan() -> int:
    rows = rl.load()
    human, to_polish, write_jobs = plan_items(rows)
    gen = len(write_jobs) + len(to_polish)
    judge_calls = 3 * len(LENGTHS) * N_JUDGE
    print(f'model: {llm.describe()}')
    print(f'H {len(human)} human reviews (>= {max(LENGTHS)} sentences) · A {len(write_jobs)} AI-invented · P {len(to_polish)} AI-polished')
    print(f'calls: {gen} writing (~400 output tokens each) + {judge_calls} judging (short) = {gen + judge_calls}')
    print(f'cache: {CACHE.relative_to(HERE)} (re-running is free and gives the same numbers)')
    print('\nwriting prompt:\n' + WRITE_PROMPT.format(tone='positive, enthusiastic', hotel='Hilton Chicago', n='11 to 13'))
    return 0


# ---------------------------------------------------------------- self-test (mock model, synthetic corpus)

def _synthetic_rows():
    rng = random.Random(5)
    real_w = ['bathroom', 'small', 'elevator', 'blocks', 'station', 'lobby', 'floor', 'carpet', 'noise', 'desk']
    fake_w = ['my', 'husband', 'amazing', 'vacation', 'luxury', 'wonderful', 'I', 'loved', 'perfect', 'my']
    rows, hotels = [], sorted(HOTEL_NAMES)
    for i, h in enumerate(hotels):
        for fake in (0, 1):
            for pol in ('positive', 'negative'):
                for n in range(4):
                    w = fake_w if fake else real_w
                    text = ' '.join(f'The {rng.choice(w)} was {rng.choice(w)} and {rng.choice(w)}.' for _ in range(12))
                    rows.append({'id': f'{pol[:3]}/{"d" if fake else "t"}_{h}_{n}', 'text': text, 'fake': fake,
                                 'hotel': h, 'fold': i // 4 + 1, 'polarity': pol})
    return rows


def _mock(prompt):
    h = int(hashlib.sha256(prompt.encode()).hexdigest(), 16)
    if prompt.startswith('Here is a short text'):
        return str(h % 101)
    if prompt.startswith('Improve the grammar'):
        body = prompt.split('Review:\n', 1)[1]
        return body.replace(' was ', ' was truly ')
    words = ['stunning', 'impeccable', 'seamless', 'delightful', 'exceptional', 'memorable']
    return ' '.join(f'The stay was {words[(h >> i) % 6]} in every way.' for i in range(12))


def selftest() -> int:
    if not os.environ.get('HOMODYNE_MODEL', '').startswith('mock'):
        print('Set HOMODYNE_MODEL=mock:echo for the self-test (no key, no network).')
        return 2
    checks = []

    def ok(name, cond):
        checks.append(bool(cond))
        print(('ok  ' if cond else 'FAIL') + ' ' + name)

    ok('fa_num 24 = بیست‌وچهار', fa_num(24) == 'بیست‌وچهار')
    ok('fa_num 0, 10, 100', (fa_num(0), fa_num(10), fa_num(100)) == ('صفر', 'ده', 'صد'))
    ok('parse_probability "72"', parse_probability('72') == 72)
    ok('parse_probability "Probability: 100%"', parse_probability('Probability: 100%') == 100)
    ok('parse_probability refusal -> None', parse_probability('I cannot estimate that.') is None)
    ok('refusal text is not usable', not is_usable("I can't help write fake reviews. " * 12))
    rows = _synthetic_rows()
    with tempfile.TemporaryDirectory() as tmp:
        global CACHE
        CACHE = Path(tmp) / 'cache'
        out = Path(tmp) / 'api-results.json'
        call = lambda prompt, **kw: llm.call(prompt, mock=_mock, **kw)  # noqa: E731
        res = run(rows, call=call, out_path=out, quiet=True)
        c = res['counts']
        ok(f'80 AI-invented reviews written (got {c["ai_invented"]})', c['ai_invented'] == 80)
        ok(f'30 polished reviews (got {c["ai_polished"]})', c['ai_polished'] == 30)
        ok('mock answers are never cached', not CACHE.exists() or not any(CACHE.iterdir()))
        ok('status says MOCK', res['status'].startswith('MOCK'))
        r = res['results']
        ok('D2 has rates at 1, 3 and 10 sentences', all(r['D2_ai_text'][str(k)]['tpr_AI']['n'] > 0 for k in LENGTHS))
        ok('D3 judge parsed every answer', c['judge_unparsed'] == 0)
        ok('D2 separates synthetic AI text at 10 sentences', r['D2_ai_text']['10']['tpr_AI']['value'] > 0.9)
        lines = report_lines(res)
        ok('report prints Persian lines for beats 9 and 10', any('قاب 9' in x for x in lines) and any('قاب 10' in x for x in lines))
        ok('report has no ASCII digits inside spoken sentences',
           not any(re.search(r'[0-9]', x) for x in lines if x and not x.startswith(('قاب', '('))))
        ok('every spoken sentence <= 22 words', all(len(s.split()) <= 22 for x in lines if x and not x.startswith(('قاب', '('))
                                                       for s in re.split(r'(?<=[.!?؟])\s+', x)))
    print(f'{sum(checks)}/{len(checks)} checks passed')
    return 0 if all(checks) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('command', nargs='?', choices=('plan', 'run', 'report'), default='plan')
    ap.add_argument('--judge-role', choices=('main', 'small'), default='main', help='model that plays judge (D3)')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.command == 'plan':
        return plan()
    if args.command == 'report':
        return report()
    rows = rl.load()
    print(f'calling {llm.describe()} (cached in {CACHE.relative_to(HERE)}) ...')
    run(rows, judge_role=args.judge_role)
    return 0


if __name__ == '__main__':
    sys.exit(main())
