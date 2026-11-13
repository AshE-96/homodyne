#!/usr/bin/env python3
"""
HMD-015 · The answer is in the file. Why does the AI still get it wrong?

Three ways to answer an employee's question from the same invented company documents
(ILLUSTRATIVE: company "Dayereh", its handbook, two amendments, two insurance contracts,
a travel policy and an IT policy):

    full    give the model every passage of the pack
    rag     "search, then answer": word-level BM25 picks the top 5 passages
    hybrid  word BM25 + character 4-gram BM25, merged with reciprocal rank fusion, top 5

Every wrong answer gets one label, so "never found it" is kept apart from "found it and misused it":
    retrieval_miss   the gold passage was not in what the model saw (rag / hybrid only)
    stale_version    the gold passage was there, but the answer used an older version of the rule
    false_abstain    the gold passage was there, but the model said the answer is not in the file
    misread          the gold passage was there, and the answer is wrong in some other way
    invented         a question whose answer is NOT in the documents got an answer anyway
    format_error     the reply was not the JSON we asked for

Commands (run from anywhere; standard library only, plus tools/llm.py for the model calls):

    python3 answer_in_file.py retrieval            # LOCAL, free: Recall@k for BM25 and hybrid, both packs
    python3 answer_in_file.py estimate             # number of model calls and a rough token count, no calls
    python3 answer_in_file.py run [--limit 3]      # API: asks the model (costs money; answers cached in runs/)
    python3 answer_in_file.py report               # tables + the Persian spoken lines for the [RUN] beats
    HOMODYNE_MODEL=mock:echo python3 answer_in_file.py --selftest    # no key, no network, no cost

Grading is by exact gold answer (normalised whole-token match), never by an LLM judge.
"""

import argparse
import json
import math
import os
import random
import re
import statistics
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / 'pack'
RESULTS = HERE / 'results'
RUNS = HERE / 'runs'
PRICES = HERE / 'prices.json'
sys.path.insert(0, str(HERE.parents[3] / 'tools'))

# ── fixed before any run (see protocol.md); never tuned on the test split ───────────────────
SEED = 15
K_ANSWER = 5            # passages given to the model in rag / hybrid
KS = (1, 3, 5, 10)      # Recall@k reported locally
BM25_K1, BM25_B = 1.2, 0.75   # textbook defaults (Robertson & Zaragoza 2009)
RRF_K = 60              # Cormack, Clarke & Buettcher 2009
N_DISTRACTORS = 160     # generated filler passages in the long pack
MAX_TOKENS = 1000
TODAY_FA = '۱۴۰۵/۰۸/۲۲'
POSITIONS = ('start', 'middle', 'end')
ARMS = ('full', 'rag', 'hybrid')
PACKS = ('short', 'long')

FA = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
TO_FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


# ── text normalisation ───────────────────────────────────────────────────────────────────────
def norm(text):
    t = text.translate(FA)
    t = t.replace('ي', 'ی').replace('ى', 'ی').replace('ك', 'ک').replace('ة', 'ه').replace('أ', 'ا').replace('إ', 'ا')
    t = re.sub('[ً-ٰٟ]', '', t)          # harakat and the hamza above in «دورهٔ»
    t = t.replace('‌', ' ').replace('‏', '').replace('‎', '')
    t = t.replace('٫', '.').replace('٬', '').replace('،', ' ')
    t = re.sub(r'(?<=\d)[,](?=\d{3})', '', t)
    t = re.sub(r'(?<=\d)/(?=\d)', '.', t)
    return re.sub(r'\s+', ' ', t).strip().lower()


STOP = set(norm('''و در به از که این را با برای تا یا هم آن است می ها های شود شده نمی هر چه چند اگر
باید بر پس اند ای ام ات اش رو هست نیست کنم کنه کنی چی چیه ه یه یک دو من تو ما شما خود خودم کدوم کدام
آیا چقدر چنده چند ترین تر بعد قبل همه ولی اما''').split())


def words(text):
    return [w for w in re.findall(r'\w+', norm(text)) if w not in STOP]


def char_grams(text, n=4):
    out = []
    for w in words(text):
        w = f'#{w}#'
        out += [w] if len(w) <= n else [w[i:i + n] for i in range(len(w) - n + 1)]
    return out


# ── the document pack ────────────────────────────────────────────────────────────────────────
def load_docs():
    passages = []
    for path in sorted((DATA / 'docs').glob('*.md')):
        text = path.read_text(encoding='utf-8')
        title = re.search(r'^# (.+)$', text, re.M).group(1).strip()
        meta = dict(re.findall(r'^- (\w+): (.+)$', text, re.M))
        for pid, sec, body in re.findall(r'^## ([A-Z0-9-]+) · (.+?)\n(.*?)(?=^## |\Z)', text, re.M | re.S):
            passages.append({'id': pid, 'doc': meta['doc'], 'doc_title': title, 'date': meta['date'],
                             'section': sec.strip(), 'text': ' '.join(body.split()), 'pack': meta.get('pack', 'short')})
    return passages


def fa(n):
    return str(n).translate(TO_FA)


def toman_fa(n):
    if n >= 1_000_000:
        m, r = divmod(n, 1_000_000)
        return f'{fa(m)} میلیون' + (f' و {fa(r // 1000)} هزار' if r else '') + ' تومان'
    return f'{fa(n // 1000)} هزار تومان'


def distractors(n=N_DISTRACTORS, seed=SEED):
    """Deterministic filler for the long pack: realistic shared-drive clutter that shares words
    (سقف، بیمه، مرخصی، هزینه، فرانشیز) with the questions but never answers a test question."""
    rnd = random.Random(seed)
    months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    events = ['اردوی تابستانی', 'مسابقهٔ فوتسال', 'جشن یلدا', 'کلاس یوگا', 'بازدید از نمایشگاه کتاب', 'کارگاه عکاسی',
              'برنامهٔ کوه‌پیمایی یک‌روزه', 'جشن پایان سال', 'تور بازدید از کاشان', 'مسابقهٔ شطرنج']
    places = ['آشپزخانهٔ طبقهٔ دوم', 'اتاق جلسهٔ «البرز»', 'اتاق جلسهٔ «دماوند»', 'پارکینگ طبقهٔ منفی یک',
              'چاپگر طبقهٔ سوم', 'سامانهٔ «همراه»', 'سرور ایمیل', 'آسانسور شرقی']
    reasons = ['تعمیرات دوره‌ای', 'سم‌پاشی', 'به‌روزرسانی نرم‌افزار', 'تعویض کف‌پوش', 'بازرسی ایمنی', 'قطع برق برنامه‌ریزی‌شده']
    regions = ['تهران', 'اصفهان', 'تبریز', 'شیراز', 'مشهد', 'رشت', 'کرمان', 'اهواز']
    seasons = ['بهار', 'تابستان', 'پاییز', 'زمستان']
    contractors = ['پاکان', 'نگهبان‌پارس', 'آذرخدمت', 'سپیدار', 'آرمان‌کار']
    assets = ['بدنهٔ خودروهای شرکت', 'تجهیزات دفتر', 'آتش‌سوزی ساختمان', 'مسئولیت مدنی کارفرما', 'سرقت تجهیزات انبار']
    courses = ['مدیریت پروژه', 'تحلیل داده', 'زبان انگلیسی تجاری', 'امنیت شبکه', 'طراحی تجربهٔ کاربر', 'مذاکرهٔ فروش']
    teams = ['فروش', 'پشتیبانی', 'محصول', 'زیرساخت', 'مالی', 'بازاریابی']
    topics = [('چاپگر طبقهٔ سوم رنگی چاپ نمی‌کند', 'کارتریج رنگی سفارش داده شده و تا پایان هفته نصب می‌شود.'),
              ('رمز وای‌فای مهمان چیست', 'رمز وای‌فای مهمان هر دوشنبه عوض می‌شود و از پذیرش بگیرید.'),
              ('صفحه‌نمایش دوم می‌دهید', 'برای تیم‌های طراحی و داده، با درخواست مدیر تیم، صفحه‌نمایش دوم داده می‌شود.'),
              ('تقویم مشترک جلسه‌ها کجاست', 'تقویم مشترک در سامانهٔ «همراه» بخش جلسه‌ها قرار دارد.'),
              ('هدست برای جلسه‌های آنلاین هست', 'تعداد محدودی هدست در واحد فناوری برای امانت موجود است.')]
    out = []
    for i in range(n):
        kind = i % 8
        amount = rnd.choice([2, 3, 4, 5, 6, 8, 12, 15, 18, 25, 40]) * 1_000_000
        d = f'{fa(rnd.randint(1, 29))} {rnd.choice(months)}'
        if kind == 0:
            ev = rnd.choice(events)
            title, text = 'صورت‌جلسهٔ کمیتهٔ رفاه', (
                f'در جلسهٔ شمارهٔ {fa(rnd.randint(20, 90))} کمیتهٔ رفاه دربارهٔ {ev} گفت‌وگو شد. مقرر شد هزینهٔ {ev} '
                f'تا سقف {toman_fa(amount)} از بودجهٔ رفاهی پرداخت شود و ثبت‌نام تا {d} در سامانهٔ «همراه» انجام شود.')
        elif kind == 1:
            title, text = 'اطلاعیهٔ واحد اداری', (
                f'به دلیل {rnd.choice(reasons)}، {rnd.choice(places)} روز {d} از ساعت {fa(rnd.randint(8, 12))} تا '
                f'{fa(rnd.randint(13, 18))} در دسترس نیست. از همکاران خواهش می‌کنیم برنامهٔ خود را با این زمان تنظیم کنند.')
        elif kind == 2:
            r = rnd.choice(regions)
            title, text = f'گزارش فصلی فروش منطقهٔ {r}', (
                f'فروش اشتراک سالانه در فصل {rnd.choice(seasons)} در منطقهٔ {r} به {fa(rnd.randint(40, 400))} مشتری رسید. '
                f'هزینهٔ تبلیغات منطقه {toman_fa(amount)} بود و {fa(rnd.randint(2, 30))} قرارداد تازه بسته شد.')
        elif kind == 3:
            c = rnd.choice(contractors)
            title, text = f'قرارداد شرکت خدماتی {c}', (
                f'کارکنان شرکت خدماتی {c} طبق قرارداد جداگانهٔ خود از مرخصی، بیمه و کمک‌هزینه‌ها استفاده می‌کنند و '
                f'آیین‌نامهٔ کارکنان دایره شامل آن‌ها نمی‌شود. مدت این قرارداد {fa(rnd.randint(6, 24))} ماه است.')
        elif kind == 4:
            a = rnd.choice(assets)
            title, text = f'بیمهٔ {a}', (
                f'سقف پوشش خسارت در بیمه‌نامهٔ {a} {toman_fa(amount * 10)} است و فرانشیز آن {fa(rnd.choice([10, 15, 20, 25]))} درصد است. '
                f'خسارت باید ظرف {fa(rnd.choice([3, 5, 7, 10]))} روز به واحد اداری گزارش شود.')
        elif kind == 5:
            q, a = rnd.choice(topics)
            title, text = 'پرسش و پاسخ کانال داخلی فناوری', f'پرسش: {q}؟ پاسخ واحد فناوری: {a}'
        elif kind == 6:
            t = rnd.choice(teams)
            title, text = f'خبرنامهٔ داخلی شمارهٔ {fa(rnd.randint(10, 120))}', (
                f'تیم {t} پروژهٔ «{rnd.choice(["ستاره", "نسیم", "پل", "آینه", "رود"])}» را به مرحلهٔ آزمایش رساند. '
                f'جلسهٔ مرور این پروژه روز {d} در اتاق جلسهٔ «البرز» برگزار می‌شود.')
        else:
            t = rnd.choice(teams)
            title, text = 'برنامهٔ آموزشی واحدها', (
                f'دورهٔ {rnd.choice(courses)} با مدرس بیرونی در {fa(rnd.randint(4, 12))} جلسه برای تیم {t} برگزار می‌شود. '
                f'هزینهٔ دوره {toman_fa(amount)} است و از بودجهٔ آموزشی واحد {t} پرداخت می‌شود، نه از بودجهٔ فردی کارکنان.')
        y = rnd.choice(['1402', '1403', '1404', '1405'])
        out.append({'id': f'GEN-{i + 1:03d}', 'doc': 'GEN', 'doc_title': 'اسناد متفرقهٔ درایو مشترک (تولیدشده)',
                    'date': f'{y}-{rnd.randint(1, 7 if y == "1405" else 12):02d}-{rnd.randint(1, 28):02d}', 'section': title,
                    'text': text, 'pack': 'long'})
    return out


def build_pack(name):
    core = load_docs()
    if name == 'short':
        return [p for p in core if p['pack'] == 'short']
    return core + distractors()


def load_questions(split='test'):
    qs = json.loads((DATA / 'questions.json').read_text(encoding='utf-8'))['questions']
    return [q for q in qs if split == 'all' or q['split'] == split]


def header(p):
    return f"[{p['id']}] {p['doc_title']} · تاریخ سند: {p['date'].translate(TO_FA).replace('-', '/')} · {p['section']}"


def index_text(p):
    return f"{p['doc_title']} {p['section']} {p['text']}"


# ── retrieval ───────────────────────────────────────────────────────────────────────────────
class BM25:
    def __init__(self, docs, analyzer):
        self.analyzer = analyzer
        self.tf = [Counter(analyzer(d)) for d in docs]
        self.len = [sum(t.values()) for t in self.tf]
        self.avg = sum(self.len) / len(self.len)
        df = Counter(w for t in self.tf for w in t)
        n = len(docs)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}

    def scores(self, query):
        q = self.analyzer(query)
        out = []
        for tf, ln in zip(self.tf, self.len):
            s = 0.0
            for w in q:
                f = tf.get(w)
                if f:
                    s += self.idf[w] * f * (BM25_K1 + 1) / (f + BM25_K1 * (1 - BM25_B + BM25_B * ln / self.avg))
            out.append(s)
        return out


class Retriever:
    def __init__(self, pack):
        self.pack = pack
        texts = [index_text(p) for p in pack]
        self.word = BM25(texts, words)
        self.char = BM25(texts, char_grams)

    def _rank(self, scores):
        # ties broken by passage id, so the ranking never depends on the order of the pack
        order = sorted(range(len(scores)), key=lambda i: (-scores[i], self.pack[i]['id']))
        return [self.pack[i]['id'] for i in order]

    def rank(self, method, query):
        if method == 'rag':
            return self._rank(self.word.scores(query))
        if method == 'char':
            return self._rank(self.char.scores(query))
        if method == 'hybrid':
            fused = defaultdict(float)
            for ranking in (self.rank('rag', query), self.rank('char', query)):
                for r, pid in enumerate(ranking):
                    fused[pid] += 1 / (RRF_K + r + 1)
            return sorted(fused, key=lambda pid: (-fused[pid], pid))
        raise ValueError(method)


def present(q, ids):
    """True when the passages the model sees contain the gold: one of them ('any') or all of them ('all')."""
    ids = set(ids)
    if not q['gold']:
        return None
    return all(g in ids for g in q['gold']) if q['gold_mode'] == 'all' else any(g in ids for g in q['gold'])


def gold_in_pack(q, pack_ids):
    return [g for g in q['gold'] if g in pack_ids]


def answerable(q):
    return bool(q['gold'])


# ── LOCAL: retrieval experiment ─────────────────────────────────────────────────────────────
def cmd_retrieval(args):
    out = {'about': 'HMD-015 local retrieval run. ILLUSTRATIVE documents and questions. No model was called.',
           'settings': {'seed': SEED, 'bm25_k1': BM25_K1, 'bm25_b': BM25_B, 'rrf_k': RRF_K, 'k_answer': K_ANSWER,
                        'n_distractors': N_DISTRACTORS, 'hybrid': 'word BM25 + char 4-gram BM25, reciprocal rank fusion'},
           'packs': {}}
    rows = []
    for pack_name in PACKS:
        pack = build_pack(pack_name)
        ids = {p['id'] for p in pack}
        ret = Retriever(pack)
        n_words = sum(len(p['text'].split()) + len(header(p).split()) for p in pack)
        out['packs'][pack_name] = info = {'passages': len(pack), 'words': n_words, 'chars': sum(len(header(p)) + len(p['text']) + 2 for p in pack)}
        for split in ('test', 'dev'):
            qs = [q for q in load_questions(split) if answerable(q)]
            for method in ('rag', 'char', 'hybrid'):
                res = {}
                hits = defaultdict(list)
                for q in qs:
                    ranking = ret.rank(method, q['q'])
                    gold_ranks = [ranking.index(g) + 1 for g in q['gold'] if g in ids]
                    first = min(gold_ranks) if gold_ranks else None
                    stale_present = [s for s in q['stale_ids'] if s in ids]
                    stale_above = bool(stale_present and first and min(ranking.index(s) + 1 for s in stale_present) < first)
                    for k in KS:
                        hits[k].append(bool(present(q, ranking[:k])))
                    if split == 'test':
                        rows.append({'pack': pack_name, 'method': method, 'qid': q['id'], 'type': q['type'],
                                     'overlap': q['overlap'], 'first_gold_rank': first,
                                     'hit@5': bool(present(q, ranking[:K_ANSWER])),
                                     'stale_in_top5': any(s in ranking[:K_ANSWER] for s in stale_present),
                                     'stale_above_gold': stale_above, 'top5': ' '.join(ranking[:K_ANSWER])})
                res['n'] = len(qs)
                res['recall'] = {f'@{k}': round(sum(v) / len(v), 3) for k, v in hits.items()}
                res['hits@5'] = sum(hits[K_ANSWER])
                if split == 'test':
                    mine = [r for r in rows if r['pack'] == pack_name and r['method'] == method]
                    for field in ('type', 'overlap'):
                        groups = defaultdict(list)
                        for r in mine:
                            groups[r[field]].append(r['hit@5'])
                        res[f'recall@5_by_{field}'] = {g: f'{sum(v)}/{len(v)}' for g, v in sorted(groups.items())}
                    latest = [r for r in mine if r['type'] == 'latest' or load_q(r['qid'])['stale_ids']]
                    latest = [r for r in latest if [s for s in load_q(r['qid'])['stale_ids'] if s in ids]]
                    res['with_older_version_in_pack'] = len(latest)
                    res['older_version_in_top5'] = sum(r['stale_in_top5'] for r in latest)
                    res['older_version_ranked_above_gold'] = sum(r['stale_above_gold'] for r in latest)
                    res['misses_at_5'] = [r['qid'] for r in mine if not r['hit@5']]
                info[f'{split}:{method}'] = res
        # position check: shuffle the pack five times; BM25 rankings must not change
        base = {q['id']: Retriever(pack).rank('hybrid', q['q'])[:K_ANSWER] for q in load_questions('test')}
        same = True
        for s in range(5):
            shuffled = pack[:]
            random.Random(100 + s).shuffle(shuffled)
            r2 = Retriever(shuffled)
            same &= all(r2.rank('hybrid', q['q'])[:K_ANSWER] == base[q['id']] for q in load_questions('test'))
        info['position_invariant'] = same
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / 'retrieval-local.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    with (RESULTS / 'retrieval-per-question.csv').open('w', encoding='utf-8') as f:
        cols = list(rows[0])
        f.write(','.join(cols) + '\n')
        for r in rows:
            f.write(','.join(str(r[c]) for c in cols) + '\n')
    export_packs()
    print_retrieval(out)
    return 0


_QCACHE = {}


def load_q(qid):
    if not _QCACHE:
        _QCACHE.update({q['id']: q for q in load_questions('all')})
    return _QCACHE[qid]


def export_packs():
    """Write both packs as plain text, so a viewer can paste them into any chatbot and ask the questions."""
    gen = DATA / 'generated'
    gen.mkdir(exist_ok=True)
    for name in PACKS:
        pack = build_pack(name)
        body = '\n\n'.join(header(p) + '\n' + p['text'] for p in pack)
        (gen / f'pack-{name}.txt').write_text(
            'ILLUSTRATIVE · شرکت دایره و همهٔ این اسناد ساختگی‌اند (هومودین HMD-015).\n\n' + body + '\n', encoding='utf-8')


def print_retrieval(out):
    print('HMD-015 · local retrieval (ILLUSTRATIVE documents; no model called)\n')
    print(f'{"pack":6} {"passages":>8} {"words":>6}   {"method":7} {"R@1":>5} {"R@3":>5} {"R@5":>5} {"R@10":>5}  hits@5   older version in top 5')
    for name, info in out['packs'].items():
        for m in ('rag', 'char', 'hybrid'):
            r = info[f'test:{m}']
            rc = r['recall']
            label = {'rag': 'bm25', 'char': 'char4', 'hybrid': 'hybrid'}[m]
            print(f'{name:6} {info["passages"]:8} {info["words"]:6}   {label:7} {rc["@1"]:5.2f} {rc["@3"]:5.2f} {rc["@5"]:5.2f} {rc["@10"]:5.2f}  '
                  f'{r["hits@5"]:2}/{r["n"]}    {r["older_version_in_top5"]}/{r["with_older_version_in_pack"]} '
                  f'(ranked above gold: {r["older_version_ranked_above_gold"]})')
    for name, info in out['packs'].items():
        print(f'\n{name}: misses at 5 → bm25 {info["test:rag"]["misses_at_5"]} · hybrid {info["test:hybrid"]["misses_at_5"]}')
        print(f'{name}: recall@5 by overlap (bm25) {info["test:rag"]["recall@5_by_overlap"]} · (hybrid) {info["test:hybrid"]["recall@5_by_overlap"]}')
        print(f'{name}: same top-5 after shuffling the pack 5 times: {info["position_invariant"]}')
    print('\nOnly the 42 answerable test questions count. Dev split is in results/retrieval-local.json.')


# ── API: prompts, grading ───────────────────────────────────────────────────────────────────
SYSTEM = f'''تو دستیار پاسخ‌گویی به پرسش‌های کارکنان شرکت دایره هستی. تاریخ امروز {TODAY_FA} است.
فقط از بندهای داده‌شده استفاده کن، نه از دانسته‌های خودت.
هر بند یک شناسه در کروشه دارد و تاریخ سندش کنارش آمده. اگر چند نسخه از یک قاعده هست، نسخهٔ جدیدتر معتبر است.
اگر جواب در بندها نیست، حدس نزن.
فقط یک شیء JSON برگردان و هیچ متن دیگری ننویس:
{{"answer": "<جواب کوتاه>", "passage_ids": ["<شناسهٔ بندهایی که جواب از آن‌ها آمده>"], "not_in_docs": false}}
مبلغ‌ها را به تومان، با رقم لاتین و بدون جداکننده بنویس (مثل 4500000). عددهای دیگر را هم با رقم لاتین بنویس.
اگر جواب در بندها نیست: {{"answer": "", "passage_ids": [], "not_in_docs": true}}'''


def full_order(pack, q, position):
    """Seeded shuffle of the pack; the decisive gold passage is then moved to the start, middle or end."""
    order = pack[:]
    random.Random(SEED).shuffle(order)
    if position in POSITIONS and q['gold']:
        target = next((p for g in q['gold'] for p in order if p['id'] == g), None)
        if target:
            order.remove(target)
            at = {'start': 0, 'middle': len(order) // 2, 'end': len(order)}[position]
            order.insert(at, target)
    return order


def context_for(arm, q, pack, retriever, position):
    if arm == 'full':
        return full_order(pack, q, position)
    by_id = {p['id']: p for p in pack}
    return [by_id[i] for i in retriever.rank(arm, q['q'])[:K_ANSWER]]


def build_prompt(passages, question):
    return 'بندها:\n\n' + '\n\n'.join(header(p) + '\n' + p['text'] for p in passages) + f'\n\nپرسش: {question}'


def amount_aliases(n):
    out = [str(n)]
    if n >= 1_000_000:
        m = n / 1_000_000
        out += [f'{m:g} میلیون', f'{m:g}میلیون']
        mm, r = divmod(n, 1_000_000)
        if r:
            out.append(f'{mm} میلیون و {r // 1000} هزار')
    else:
        out += [f'{n // 1000} هزار', f'{n // 1000}هزار']
    return out


def aliases(items):
    out = []
    for a in items:
        out += amount_aliases(int(a.split(':')[1])) if a.startswith('amount:') else [a]
    return [norm(a) for a in out]


def matches(text, items):
    t = norm(text)
    return any(re.search(r'(?<![\w.])' + re.escape(a) + r'(?!\w|\.\d)', t) for a in aliases(items))


def parse_reply(text):
    m = re.search(r'\{.*\}', text or '', re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(d, dict) or 'answer' not in d:
        return None
    ids = d.get('passage_ids') or []
    return {'answer': str(d.get('answer') or ''), 'passage_ids': [str(i) for i in ids] if isinstance(ids, list) else [],
            'not_in_docs': bool(d.get('not_in_docs'))}


def grade(q, parsed, context_ids):
    g = {'gold_in_context': present(q, context_ids) if answerable(q) else None}
    if parsed is None:
        g.update(category='format_error', acceptable=False, correct=False)
        return g
    if not answerable(q):
        ok = parsed['not_in_docs'] and not parsed['answer'].strip()
        ok = ok or (parsed['not_in_docs'] and not re.search(r'\d', norm(parsed['answer'])))
        g.update(category='correct_abstain' if ok else 'invented', acceptable=ok, correct=ok)
        return g
    stale_hit = bool(q['stale']) and matches(parsed['answer'], q['stale'])
    right = matches(parsed['answer'], q['accept']) and not stale_hit and not parsed['not_in_docs']
    g['stale_hit'] = stale_hit
    g['cited_gold'] = any(i in q['gold'] for i in parsed['passage_ids'])
    if right:
        cat = 'correct'
    elif not g['gold_in_context']:
        cat = 'retrieval_miss'
    elif parsed['not_in_docs']:
        cat = 'false_abstain'
    elif stale_hit:
        cat = 'stale_version'
    else:
        cat = 'misread'
    g.update(category=cat, acceptable=right, correct=right)
    if cat == 'retrieval_miss':
        g['miss_then'] = 'abstained' if parsed['not_in_docs'] else 'answered'
    return g


def plan(args):
    qs = load_questions(args.split)
    if args.limit:
        qs = qs[:args.limit]
    jobs = []
    for pack in args.packs:
        for arm in args.arms:
            for q in qs:
                positions = args.positions if (arm == 'full' and answerable(q)) else ['na']
                for pos in positions:
                    jobs.append((pack, arm, pos, q))
    return jobs


def model_slug():
    import llm
    provider, name = llm.resolve('main')
    return f'{provider}:{name}', re.sub(r'[^A-Za-z0-9._-]+', '-', f'{provider}-{name}')


def cmd_estimate(args):
    jobs = plan(args)
    packs = {p: build_pack(p) for p in args.packs}
    rets = {p: Retriever(packs[p]) for p in args.packs}
    chars = defaultdict(int)
    calls = Counter()
    for pack, arm, pos, q in jobs:
        ctx = context_for(arm, q, packs[pack], rets[pack], pos)
        chars[(pack, arm)] += len(SYSTEM) + len(build_prompt(ctx, q['q']))
        calls[(pack, arm)] += 1
    print(f'{len(jobs)} model calls · rough input tokens = characters / {args.chars_per_token} (Persian; measure with run --limit 3)\n')
    tot = 0
    for key in sorted(chars):
        t = chars[key] / args.chars_per_token
        tot += t
        print(f'{key[0]:6} {key[1]:7} {calls[key]:4} calls  ~{t / 1e6:6.2f} M input tokens  (~{t / calls[key]:,.0f} per call)')
    print(f'\ntotal ~{tot / 1e6:.2f} M input tokens + up to {len(jobs) * MAX_TOKENS / 1e6:.2f} M output tokens (cap, not expected)')
    return 0


def mock_reader(prompt):
    """Self-test stand-in for a model: reads perfectly when the gold passage is in the prompt, except it
    'loses' gold passages sitting in the middle of a long prompt, and it invents answers for half of the
    questions that are not in the documents. Exists only to exercise every branch of the grader."""
    qtext = prompt.rsplit('پرسش: ', 1)[-1].strip()
    q = next(x for x in load_questions('all') if x['q'] == qtext)
    ids = re.findall(r'^\[([A-Z0-9-]+)\]', prompt, re.M)
    if not answerable(q):
        if int(q['id'][-1]) % 2:
            return json.dumps({'answer': '3000000', 'passage_ids': [ids[0]], 'not_in_docs': False})
        return json.dumps({'answer': '', 'passage_ids': [], 'not_in_docs': True})
    if not present(q, ids):
        return json.dumps({'answer': '', 'passage_ids': [], 'not_in_docs': True})
    first = next(g for g in q['gold'] if g in ids)
    where = ids.index(first) / max(1, len(ids) - 1)
    if len(ids) > 100 and 0.3 < where < 0.7:
        wrong = q['stale'][0] if q['stale'] else 'نامشخص'
        wrong = str(amount_aliases(int(wrong.split(':')[1]))[0]) if wrong.startswith('amount:') else wrong
        return json.dumps({'answer': wrong, 'passage_ids': [ids[0]], 'not_in_docs': False}, ensure_ascii=False)
    a = q['accept'][0]
    a = a.split(':')[1] if a.startswith('amount:') else a
    return json.dumps({'answer': a, 'passage_ids': q['gold'], 'not_in_docs': False}, ensure_ascii=False)


def cmd_run(args, out_root=RUNS):
    import llm
    model_id, slug = model_slug()
    out = out_root / slug
    out.mkdir(parents=True, exist_ok=True)
    rows_path = out / 'rows.jsonl'
    rows = {}
    if rows_path.exists():
        for line in rows_path.read_text(encoding='utf-8').splitlines():
            r = json.loads(line)
            rows[(r['pack'], r['arm'], r['position'], r['qid'])] = r
    jobs = plan(args)
    packs = {p: build_pack(p) for p in args.packs}
    rets = {p: Retriever(packs[p]) for p in args.packs}
    print(f'{llm.describe()}\n{len(jobs)} calls → {rows_path}')
    fell_back = 0
    for n, (pack, arm, pos, q) in enumerate(jobs, 1):
        ctx = context_for(arm, q, packs[pack], rets[pack], pos)
        ctx_ids = [p['id'] for p in ctx]
        res = llm.call(build_prompt(ctx, q['q']), system=SYSTEM, max_tokens=MAX_TOKENS,
                       cache_dir=out / 'cache', mock=mock_reader)
        parsed = parse_reply(res.text)
        row = {'qid': q['id'], 'split': q['split'], 'type': q['type'], 'overlap': q['overlap'], 'arm': arm,
               'pack': pack, 'position': pos, 'n_passages': len(ctx),
               'gold_index': next((i for i, x in enumerate(ctx_ids) if x in q['gold']), None),
               'context_top': ctx_ids[:K_ANSWER] if arm != 'full' else [],
               'model': model_id, 'model_served': res.model_served, 'fell_back': res.fell_back,
               'input_tokens': res.input_tokens, 'output_tokens': res.output_tokens,
               'latency_s': round(res.latency_s, 3), 'cached': res.cached, 'stop_reason': res.stop_reason,
               'reply': res.text, 'parsed': parsed}
        row.update(grade(q, parsed, ctx_ids))
        rows[(pack, arm, pos, q['id'])] = row
        fell_back += bool(res.fell_back)
        if n % 25 == 0 or n == len(jobs):
            print(f'  {n}/{len(jobs)}')
    rows_path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows.values()), encoding='utf-8')
    if fell_back:
        print(f'  note: {fell_back} replies came from a fallback model (see model_served)')
    return 0


# ── report ──────────────────────────────────────────────────────────────────────────────────
ONES = ['صفر', 'یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه', 'ده', 'یازده', 'دوازده', 'سیزده',
        'چهارده', 'پانزده', 'شانزده', 'هفده', 'هجده', 'نوزده']
TENS = ['', '', 'بیست', 'سی', 'چهل', 'پنجاه', 'شصت', 'هفتاد', 'هشتاد', 'نود']
HUNDREDS = ['', 'صد', 'دویست', 'سیصد', 'چهارصد', 'پانصد', 'ششصد', 'هفتصد', 'هشتصد', 'نهصد']


def words_fa(n):
    """Integer → spoken Persian, written the way the channel writes it (بیست‌وچهار)."""
    n = int(round(n))
    if n < 0:
        return 'منفی ' + words_fa(-n)
    if n < 20:
        return ONES[n]
    if n < 100:
        t, o = divmod(n, 10)
        return TENS[t] + ('‌و' + ONES[o] if o else '')
    if n < 1000:
        h, r = divmod(n, 100)
        return HUNDREDS[h] + (' و ' + words_fa(r) if r else '')
    for size, name in ((10 ** 9, 'میلیارد'), (10 ** 6, 'میلیون'), (1000, 'هزار')):
        if n >= size:
            h, r = divmod(n, size)
            return (words_fa(h) + ' ' if h > 1 or size > 1000 else '') + name + (' و ' + words_fa(r) if r else '')
    return str(n)


def dec_fa(x, places=1):
    x = round(x, places)
    whole = int(x)
    frac = round((x - whole) * 10 ** places)
    return words_fa(whole) + (f' ممیز {words_fa(frac)}' if frac else '')


def load_rows(slug=None, root=RUNS):
    folders = [p for p in root.glob('*/rows.jsonl')] if root.exists() else []
    if slug:
        folders = [root / slug / 'rows.jsonl']
    if not folders:
        raise SystemExit('No runs yet. Run: python3 answer_in_file.py run   (or --selftest for a dry run)')
    if len(folders) > 1:
        raise SystemExit('Several models in runs/: pass --model ' + ' | '.join(p.parent.name for p in folders))
    rows = [json.loads(l) for l in folders[0].read_text(encoding='utf-8').splitlines() if l.strip()]
    return [r for r in rows if r['split'] == 'test'], folders[0].parent.name


def prices_for(model_id, path=PRICES):
    if not path.exists():
        return None, None
    d = json.loads(path.read_text(encoding='utf-8'))
    p = (d.get('models') or {}).get(model_id) or {}
    if p.get('input_per_mtok') is None or p.get('output_per_mtok') is None:
        return None, d
    return p, d


def summarise(rows, price):
    s = {}
    for key in sorted({(r['pack'], r['arm']) for r in rows}):
        rs = [r for r in rows if (r['pack'], r['arm']) == key]
        ans = [r for r in rs if r['type'] != 'unanswerable']
        una = [r for r in rs if r['type'] == 'unanswerable']
        cats = Counter(r['category'] for r in ans)
        tin, tout = sum(r['input_tokens'] for r in rs), sum(r['output_tokens'] for r in rs)
        acc_ok = sum(r['acceptable'] for r in rs)
        cost = (tin * price['input_per_mtok'] + tout * price['output_per_mtok']) / 1e6 if price else None
        correct = [r for r in ans if r['correct']]
        s[key] = {
            'calls': len(rs), 'answerable': len(ans), 'correct': len(correct),
            'accuracy': len(correct) / len(ans) if ans else 0,
            'unanswerable': len(una), 'invented': sum(r['category'] == 'invented' for r in una),
            'acceptable': acc_ok, 'acceptable_rate': acc_ok / len(rs) if rs else 0,
            'categories': dict(cats),
            'read_errors': cats['stale_version'] + cats['misread'] + cats['false_abstain'],
            'retrieval_miss': cats['retrieval_miss'],
            'citation_support': sum(r['cited_gold'] for r in correct) / len(correct) if correct else 0,
            'tokens_in': tin, 'tokens_out': tout,
            'tokens_per_acceptable': (tin + tout) / acc_ok if acc_ok else None,
            'cost': cost, 'cost_per_100_acceptable': 100 * cost / acc_ok if (cost is not None and acc_ok) else None,
            'latency_median': statistics.median(r['latency_s'] for r in rs) if rs else 0,
            'fell_back': sum(r['fell_back'] for r in rs),
        }
        if key[1] == 'full':
            s[key]['by_position'] = {}
            for pos in POSITIONS:
                pr = [r for r in ans if r['position'] == pos]
                if pr:
                    s[key]['by_position'][pos] = (sum(r['correct'] for r in pr), len(pr))
            byq = defaultdict(dict)
            for r in ans:
                byq[r['qid']][r['position']] = r['correct']
            both = [v for v in byq.values() if all(p in v for p in POSITIONS)]
            s[key]['middle_only_wrong'] = sum((not v['middle']) and v['start'] and v['end'] for v in both)
            s[key]['middle_only_right'] = sum(v['middle'] and (not v['start']) and (not v['end']) for v in both)
            s[key]['paired_questions'] = len(both)
    return s


def sign_test(a, b):
    """Two-sided exact sign test on discordant pairs (questions that flip with position only)."""
    n, k = a + b, max(a, b)
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n)


def money_fa(usd):
    """Dollars as spoken: under one dollar in cents, otherwise dollars with one decimal."""
    if usd < 1:
        return f'{words_fa(max(1, round(usd * 100)))} سنت'
    return f'{dec_fa(usd, 1)} دلار'


ARM_FA = {'full': 'دادن کل پرونده', 'rag': 'جست‌وجوی ساده', 'hybrid': 'جست‌وجوی ترکیبی'}
PACK_FA = {'short': 'کوتاه', 'long': 'بلند'}


def spoken(s, prices_meta, model_id):
    """The Persian lines for the [RUN] beats, with real numbers, in the channel's spoken style."""
    out = []
    pct = lambda x: words_fa(round(100 * x)) + ' درصد'
    for pack in PACKS:
        arms = [a for a in ARMS if (pack, a) in s]
        if not arms:
            continue
        out.append(f'— قاب ۱۰ · پروندهٔ {PACK_FA[pack]} —')
        # the full arm asks every answerable question at three positions (3 × 42 trials); the search arms once (42):
        # always say the denominator, so raw counts are never compared across arms
        parts = [f'{ARM_FA[a]} {pct(s[(pack, a)]["accuracy"])}' + ('، میانگین سه جای بند' if a == 'full' else '')
                 for a in arms]
        out.append(f'روی پروندهٔ {PACK_FA[pack]}، سهم جواب درست: ' + '؛ '.join(parts) + '.')
        for a in arms:
            x = s[(pack, a)]
            wrong = x['answerable'] - x['correct']
            stale = words_fa(x['categories'].get('stale_version', 0))
            if a == 'full':
                n = words_fa(x['answerable'])
                out.append(f'راه اول هر سؤال رو سه بار پرسید، با بند توی سه جای مختلف؛ یعنی {n} بار.')
                out.append(f'«پیدا نکردن» اونجا ممکن نیست. پس هر {words_fa(wrong)} اشتباهش از این {n} بار، '
                           f'بد خوندن بود؛ {stale} بارش نسخهٔ قدیمی.')
            else:
                out.append(f'{ARM_FA[a]} از {words_fa(x["answerable"])} سؤال، {words_fa(wrong)} تا رو غلط جواب داد: '
                           f'{words_fa(x["retrieval_miss"])} تا «پیدا نکرد»، {words_fa(x["read_errors"])} تا '
                           f'«پیدا کرد، بد خوند»؛ {stale} بارش نسخهٔ قدیمی.')
        f = s.get((pack, 'full'))
        if f and f.get('by_position'):
            out.append(f'— قاب ۱۱ · جای بند جواب · پروندهٔ {PACK_FA[pack]} —')
            bp = f['by_position']
            seg = '؛ '.join(f'{ {"start": "اول فایل", "middle": "وسط", "end": "آخر"}[p]} {pct(c / n)}' for p, (c, n) in bp.items())
            out.append(f'وقتی کل پرونده رو دادیم، درصد جواب درست بر اساس جای بند: {seg}.')
            out.append(f'سؤال‌به‌سؤال: {words_fa(f["middle_only_wrong"])} سؤال فقط وقتی بند وسط بود غلط شد، '
                       f'و {words_fa(f["middle_only_right"])} سؤال برعکس.')
            if sign_test(f['middle_only_wrong'], f['middle_only_right']) >= 0.05:
                out.append('این اختلاف اون‌قدر نیست که با این تعداد سؤال بشه چیزی ازش گفت.')
            elif f['middle_only_wrong'] > f['middle_only_right']:
                out.append('یعنی برای این مدل و این فایل، وسط پرونده هنوز جای خطرناک‌تریه؛ ولی فقط با همین چهل‌ودو سؤال.')
            else:
                out.append('یعنی اون الگوی قدیمی «گم‌شدن وسط» اینجا دیده نشد؛ برای همین مدل و همین فایل.')
    out.append('— قاب ۱۲ · هزینهٔ هر جواب درست —')
    have_cost = all(v['cost_per_100_acceptable'] is not None for v in s.values())
    for pack in PACKS:
        arms = [a for a in ARMS if (pack, a) in s]
        if not arms:
            continue
        if have_cost:
            date = str((prices_meta or {}).get('checked_on') or '[تاریخ قیمت]').translate(TO_FA)
            parts = [f'{ARM_FA[a]} حدود {money_fa(s[(pack, a)]["cost_per_100_acceptable"])}' for a in arms]
            out.append(f'پروندهٔ {PACK_FA[pack]}، با قیمت‌هایی که {date} چک کردیم، هر صد جواب قابل‌قبول: ' + '، '.join(parts) + '.')
            best = min(arms, key=lambda a: s[(pack, a)]['cost_per_100_acceptable'])
        else:
            parts = [f'{ARM_FA[a]} حدود {words_fa(round(s[(pack, a)]["tokens_per_acceptable"] or 0, -2))} توکن' for a in arms]
            out.append(f'پروندهٔ {PACK_FA[pack]}، به‌ازای هر جواب قابل‌قبول: ' + '، '.join(parts) + '. (قیمت در prices.json پر نشده.)')
            best = min(arms, key=lambda a: s[(pack, a)]['tokens_per_acceptable'] or 1e18)
        lat = '، '.join(f'{ARM_FA[a]} {dec_fa(s[(pack, a)]["latency_median"])} ثانیه' for a in arms)
        out.append(f'زمان جواب، میانه: {lat}.')
        safest = min(arms, key=lambda a: s[(pack, a)]['invented'])
        out.append(f'پس برای این اندازهٔ سند و این نوع سؤال، کم‌خرج‌ترین جواب درست مال «{ARM_FA[best]}» بود.')
        if s[(pack, best)]['invented'] > s[(pack, safest)]['invented']:
            out.append(f'ولی همین مسیر {words_fa(s[(pack, best)]["invented"])} بار برای سؤال بی‌جواب، جواب ساخت؛ '
                       f'«{ARM_FA[safest]}» {words_fa(s[(pack, safest)]["invented"])} بار.')
    inv = sum(v['invented'] for v in s.values())
    una = sum(v['unanswerable'] for v in s.values())
    out.append('— قاب ۱۵ · پل به قسمت بعد (اختیاری) —')
    out.append(f'و از {words_fa(una)} باری که جواب اصلاً توی فایل نبود، {words_fa(inv)} بار یه جواب ساخت.')
    out.append(f'[مدل: {model_id} · فقط همین ۵۰ سؤال ساختگی، همین مدل، همین تاریخ]')
    return out


def cmd_report(args, root=RUNS, prices_path=PRICES):
    rows, slug = load_rows(args.model, root)
    model_id = rows[0]['model']
    price, meta = prices_for(model_id, prices_path)
    s = summarise(rows, price)
    print(f'HMD-015 · report · {model_id} · {len(rows)} test rows · ILLUSTRATIVE documents\n')
    print(f'{"pack":6} {"arm":7} {"calls":>5} {"correct":>9} {"acc":>5} {"miss":>5} {"read":>5} {"stale":>5} '
          f'{"invent":>7} {"cite":>5} {"tok/acc":>9} {"$/100acc":>9} {"lat(s)":>7}')
    for (pack, arm), x in s.items():
        c = x['cost_per_100_acceptable']
        print(f'{pack:6} {arm:7} {x["calls"]:5} {x["correct"]:4}/{x["answerable"]:<4} {x["accuracy"]:5.2f} {x["retrieval_miss"]:5} '
              f'{x["read_errors"]:5} {x["categories"].get("stale_version", 0):5} {x["invented"]:3}/{x["unanswerable"]:<3} '
              f'{x["citation_support"]:5.2f} {(x["tokens_per_acceptable"] or 0):9.0f} {("%.3f" % c) if c is not None else "  n/a":>9} '
              f'{x["latency_median"]:7.2f}')
    for (pack, arm), x in s.items():
        if arm == 'full' and x.get('by_position'):
            print(f'\n{pack} full by position: ' + ', '.join(f'{p} {c}/{n}' for p, (c, n) in x['by_position'].items())
                  + f' · paired: middle-only wrong {x["middle_only_wrong"]}, middle-only right {x["middle_only_right"]}'
                  f' (of {x["paired_questions"]}; sign test p = {sign_test(x["middle_only_wrong"], x["middle_only_right"]):.3f})')
    fb = sum(x['fell_back'] for x in s.values())
    if fb:
        print(f'\nnote: {fb} rows were answered by a fallback model')
    if price is None:
        print('\nprices.json has no price for this model: cost columns show n/a; tokens per acceptable answer are shown instead.')
    print('\nmiss = gold passage never reached the model · read = found it, answered wrong (stale + misread + false abstain)')
    print('\n# Spoken lines for the [RUN] beats (paste into script-fa.md, keep one branch per beat)\n')
    print('\n'.join(spoken(s, meta, model_id)))
    (root / slug / 'summary.json').write_text(json.dumps({f'{k[0]}:{k[1]}': v for k, v in s.items()},
                                                         ensure_ascii=False, indent=1), encoding='utf-8')
    return 0


# ── self-test ───────────────────────────────────────────────────────────────────────────────
def selftest():
    if not os.environ.get('HOMODYNE_MODEL', '').startswith('mock:'):
        print('selftest needs HOMODYNE_MODEL=mock:echo (no key, no network, no cost)')
        return 2
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(('  ok    ' if cond else '  FAIL  ') + name)

    check('normaliser: Persian digits, separators, decimal', norm('۴٬۵۰۰٬۰۰۰ و ۱٫۴') == '4500000 و 1.4')
    check('whole-token match: 3 is not found inside 30', not matches('30 روز', ['3']) and matches('3 ماه', ['3']))
    check('amount aliases: 4.5 میلیون', matches('4.5 میلیون تومان', ['amount:4500000']))
    check('words_fa', words_fa(24) == 'بیست‌وچهار' and words_fa(140) == 'صد و چهل')
    short = build_pack('short')
    long_ = build_pack('long')
    check('pack sizes', len(short) == 53 and len(long_) == 53 + 12 + N_DISTRACTORS)
    check('every gold and stale id exists in the long pack',
          all(g in {p['id'] for p in long_} for q in load_questions('all') for g in q['gold'] + q['stale_ids']))
    q = load_q('L01')
    for pos, at in (('start', 0), ('middle', len(long_) // 2), ('end', len(long_) - 1)):
        check(f'full context puts the gold passage at the {pos}', [p['id'] for p in full_order(long_, q, pos)].index('INS-1405-01') == at)
    check('grader: stale value is a stale_version', grade(q, {'answer': '3000000', 'passage_ids': ['INS-1404-01'], 'not_in_docs': False}, ['INS-1405-01'])['category'] == 'stale_version')
    check('grader: hedged answer with both values is not correct', not grade(q, {'answer': '4500000 یا 3000000', 'passage_ids': [], 'not_in_docs': False}, ['INS-1405-01'])['correct'])
    check('grader: missing passage is a retrieval_miss', grade(q, {'answer': '', 'passage_ids': [], 'not_in_docs': True}, ['HB-01'])['category'] == 'retrieval_miss')
    check('grader: unanswerable + answer = invented', grade(load_q('U01'), {'answer': '2000000', 'passage_ids': [], 'not_in_docs': False}, [])['category'] == 'invented')
    check('parse_reply tolerates text around the JSON', parse_reply('بفرما: {"answer": "12", "passage_ids": ["HB-05"], "not_in_docs": false}')['answer'] == '12')

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        args = argparse.Namespace(split='test', limit=0, packs=list(PACKS), arms=list(ARMS), positions=list(POSITIONS))
        cmd_run(args, out_root=root)
        rows, slug = load_rows(None, root)
        check('row count = 2 packs × (42×3 full + 8 full + 50 rag + 50 hybrid)', len(rows) == 2 * (42 * 3 + 8 + 50 + 50))
        s = summarise(rows, {'input_per_mtok': 3.0, 'output_per_mtok': 15.0})
        # with a perfect reader, rag accuracy must equal the local Recall@5 of the same retriever
        for pack in PACKS:
            ret = Retriever(build_pack(pack))
            qs = [x for x in load_questions('test') if answerable(x)]
            r5 = sum(bool(present(x, ret.rank('rag', x['q'])[:K_ANSWER])) for x in qs)
            check(f'{pack}: rag correct ({s[(pack, "rag")]["correct"]}) = local BM25 hits@5 ({r5})', s[(pack, 'rag')]['correct'] == r5)
            check(f'{pack}: every rag error is a retrieval miss for a perfect reader', s[(pack, 'rag')]['read_errors'] == 0)
        bp = s[('long', 'full')]['by_position']
        check('long full: the simulated middle loss shows up', bp['middle'][0] < bp['start'][0])
        check('short full: no simulated loss in a short prompt', s[('short', 'full')]['accuracy'] == 1.0)
        check('invented answers are counted', s[('long', 'full')]['invented'] == 4)
        check('cost per 100 acceptable is computed', s[('long', 'rag')]['cost_per_100_acceptable'] is not None)
        pfile = root / 'prices.json'
        pfile.write_text(json.dumps({'checked_on': '2027-01-01', 'models': {'mock:echo': {'input_per_mtok': 3.0, 'output_per_mtok': 15.0}}}))
        try:
            cmd_report(argparse.Namespace(model=None), root=root, prices_path=pfile)
            check('report renders, with the spoken lines', True)
        except Exception as e:  # noqa: BLE001
            check(f'report renders ({e})', False)
    print('selftest ' + ('passed' if ok else 'FAILED'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description='HMD-015 · full context vs search-then-answer vs hybrid')
    ap.add_argument('--selftest', action='store_true')
    sub = ap.add_subparsers(dest='cmd')
    sub.add_parser('retrieval', help='LOCAL, free: Recall@k on both packs, writes results/')
    for name in ('estimate', 'run'):
        p = sub.add_parser(name)
        p.add_argument('--split', default='test', choices=['test', 'dev'])
        p.add_argument('--limit', type=int, default=0, help='first N questions only (try 3 first)')
        p.add_argument('--packs', nargs='+', default=list(PACKS), choices=PACKS)
        p.add_argument('--arms', nargs='+', default=list(ARMS), choices=ARMS)
        p.add_argument('--positions', nargs='+', default=list(POSITIONS), choices=POSITIONS)
        if name == 'estimate':
            p.add_argument('--chars-per-token', type=float, default=2.5)
    rp = sub.add_parser('report')
    rp.add_argument('--model', help='folder name under runs/ when several models were run')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.cmd == 'retrieval':
        return cmd_retrieval(args)
    if args.cmd == 'estimate':
        return cmd_estimate(args)
    if args.cmd == 'run':
        return cmd_run(args)
    if args.cmd == 'report':
        return cmd_report(args)
    ap.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
