"""HMD-S02 · chess_report.py — turns a run (artifact/data/runs/NAME/) into results/NAME/: report.md, summary.json,
games.pgn (with every illegal attempt as a comment), events.jsonl (for --replay) and spoken-fa.txt (draft [RUN] lines).

    python3 chess_run.py report [--run NAME]
"""
import json
import re
import statistics
import sys

import chess_core as cc
from chess_core import chess


def fa_digits(text):
    """Persian digits for numbers only (not inside move names like Ke0)."""
    tr = str.maketrans('0123456789.', '۰۱۲۳۴۵۶۷۸۹٫')
    return re.sub(r'(?<![A-Za-z\d])\d+(?:\.\d+)?(?![A-Za-z])', lambda m: m.group(0).translate(tr), text)


# ── report ───────────────────────────────────────────────────────────────────────────────────────
def load_games(run):
    by = {}
    for line in (run / 'games.jsonl').read_text(encoding='utf-8').splitlines():
        g = json.loads(line)
        by[g['gid']] = g          # the last record of a game wins (resume)
    return [g for g in by.values() if g['result'] != 'aborted'], [g for g in by.values() if g['result'] == 'aborted']


def pct(a, b):
    return None if not b else round(100 * a / b, 1)


def stats(games, sl):
    out = {}
    for s in sl:
        k = s['slot']
        mine = [g for g in games if k in (g['white'], g['black'])]
        recs = [p for g in mine for p in g['plies'] if p['slot'] == k]
        pts = w = d = l = forf = 0
        for g in mine:
            r = g['result']
            score = 0.5 if r == '1/2-1/2' else 1.0 if (r == '1-0') == (g['white'] == k) else 0.0
            pts += score
            w, d, l = w + (score == 1), d + (score == 0.5), l + (score == 0)
            forf += score == 0 and g['reason'].startswith('forfeit')
        first = [p['attempts'][0] for p in recs if p['attempts']]
        bad = [a for p in recs for a in p['attempts'] if a.get('kind')]
        kinds = {}
        for a in bad:
            kinds[a['kind']] = kinds.get(a['kind'], 0) + 1
        book_in = [p for p in recs if p['in_book_before'] and p['attempts']]
        book_out = [p for p in recs if not p['in_book_before'] and p['attempts']]
        ev = [p for p in recs if p.get('cpl') is not None]
        ev_out = [p for p in ev if not p['in_book_before']]
        lat = [a['latency_s'] for p in recs for a in p['attempts']]
        dollars = [a['usd'] for p in recs for a in p['attempts'] if not a.get('cached')]
        retried = [p for p in recs if p['attempts'] and p['attempts'][0].get('kind')]
        out[k] = {
            'label': s['label'], 'model': s['model'], 'games': len(mine), 'points': pts, 'w': w, 'd': d, 'l': l,
            'forfeits': forf, 'decisions': len(first), 'moves': sum('san' in p for p in recs),
            'first_try_legal_pct': pct(sum(not a.get('kind') for a in first), len(first)),
            'illegal': len(bad), 'illegal_kinds': kinds,
            'truncated': sum(str(a.get('stop', '')).lower() in ('max_tokens', 'length') for a in bad),
            'recovered_pct': pct(sum('san' in p for p in retried), len(retried)),
            'illegal_in_book_pct': pct(sum(bool(p['attempts'][0].get('kind')) for p in book_in), len(book_in)),
            'illegal_out_of_book_pct': pct(sum(bool(p['attempts'][0].get('kind')) for p in book_out), len(book_out)),
            'n_in_book': len(book_in), 'n_out_of_book': len(book_out),
            'acpl': round(statistics.mean(min(p['cpl'], cc.CP_CEIL) for p in ev), 1) if ev else None,
            'acpl_out_of_book': round(statistics.mean(min(p['cpl'], cc.CP_CEIL) for p in ev_out), 1) if ev_out else None,
            'accuracy': round(statistics.mean(p['accuracy'] for p in ev), 1) if ev else None,
            'blunders_per_100': round(100 * sum(p.get('judgement') == 'blunder' for p in ev) / len(ev), 1) if ev else None,
            'median_s': round(statistics.median(lat), 1) if lat else None,
            'out_tokens_per_call': round(statistics.mean(a['output_tokens'] for p in recs for a in p['attempts']))
            if lat else None,
            'usd': None if any(x is None for x in dollars) else round(sum(dollars), 3),
        }
    return out


def pgn_text(games, sl, date):
    lab = {s['slot']: f'{s["label"]} ({s["model"]})' for s in sl}
    out = []
    for g in games:
        pg = chess.pgn.Game()
        pg.headers.update({'Event': 'Homodyne HMD-S02 LLM round-robin', 'Round': g['gid'], 'Date': date,
                           'White': lab.get(g['white'], g['white']), 'Black': lab.get(g['black'], g['black']),
                           'Result': g['result'], 'Termination': g['reason']})
        node = pg
        for p in g['plies']:
            bad = ['%s (%s)' % (a.get('proposed'), a['kind']) for a in p['attempts'] if a.get('kind')]
            if 'san' in p:
                node = node.add_variation(chess.Move.from_uci(p['uci']))
                if bad:
                    node.comment = 'illegal first: ' + '; '.join(bad)
            elif bad:
                node.comment = (node.comment + ' ' if node.comment else '') + 'forfeit after: ' + '; '.join(bad)
        out.append(str(pg))
    return '\n\n'.join(out) + '\n'


KIND_FA = {'ghost_piece': 'مهرهٔ خیالی', 'unreachable': 'مهره به آن خانه نمی‌رسد', 'leaves_king_in_check': 'شاه زیر کیش',
           'castling_illegal': 'قلعهٔ غیرمجاز', 'ambiguous': 'حرکت دوپهلو', 'bad_notation': 'نماد نادرست',
           'no_answer': 'بی‌جواب'}


def spoken_lines(st, games, events):
    """Draft sentences for the script's [RUN] slots, keyed by beat. The owner reads them against report.md."""
    v = list(st.values())
    first = None
    if events.exists():
        for line in events.read_text(encoding='utf-8').splitlines():
            e = json.loads(line)
            if e['type'] == 'illegal':
                first = e
                break
    out = []
    if first:
        out.append(f'[قاب ۷] اولین حرکت غیرقانونی: {st.get(first["slot"], {}).get("label", first["slot"])}، بازی '
                   f'{first["gid"][1:]}، نیم‌حرکت {first["ply"]}: «{first["proposed"]}» ({KIND_FA.get(first["kind"])}).')
    kinds = {}
    for x in v:
        for k, n in x['illegal_kinds'].items():
            kinds[k] = kinds.get(k, 0) + n
    tot = sum(kinds.values())
    if tot:
        k, n = max(kinds.items(), key=lambda kv: kv[1])
        out.append(f'[قاب ۸] از {tot} حرکت غیرقانونی، {n} تا ({round(100 * n / tot)} درصد) از نوع «{KIND_FA[k]}» بود.')
    out.append('[قاب ۹] حرکت غیرقانونی در تلاش اول، داخل و بیرون کتاب گشایش: ' + '؛ '.join(
        f'{x["label"]} {x["illegal_in_book_pct"]} و {x["illegal_out_of_book_pct"]} درصد' for x in v))
    ev = [x for x in v if x['acpl'] is not None]
    if ev:
        lo, hi = min(ev, key=lambda x: x['acpl']), max(ev, key=lambda x: x['acpl'])
        out.append(f'[قاب ۱۰] کمترین افت میانگین: {lo["label"]} با {lo["acpl"]} سانتی‌پیاده؛ بیشترین: {hi["label"]} '
                   f'با {hi["acpl"]}. اشتباه بزرگ در هر صد حرکت: {lo["blunders_per_100"]} و {hi["blunders_per_100"]}.')
    else:
        out.append('[قاب ۱۰] Stockfish در این اجرا نبود: افت و دقت حساب نشد.')
    top = max(v, key=lambda x: x['points'])
    worst = min(v, key=lambda x: x['first_try_legal_pct'] or 0)
    out.append(f'[قاب ۱۱] اول جدول: {top["label"]} با {top["points"]} امتیاز از {top["games"]}. کمترین نرخ حرکت '
               f'قانونی در تلاش اول: {worst["label"]}، {worst["first_try_legal_pct"]} درصد.')
    tok = [x for x in v if x['out_tokens_per_call']]
    if tok:
        a, b = max(tok, key=lambda x: x['out_tokens_per_call']), min(tok, key=lambda x: x['out_tokens_per_call'])
        out.append(f'[قاب ۱۲] توکن خروجی هر درخواست: {a["label"]} حدود {a["out_tokens_per_call"]}، {b["label"]} حدود '
                   f'{b["out_tokens_per_call"]}. دلار کل: ' + '؛ '.join(
                       f'{x["label"]} {x["usd"] if x["usd"] is not None else "نامعلوم"}' for x in v) + '.')
    best = max(v, key=lambda x: x['first_try_legal_pct'] or 0)
    out.append(f'[قاب ۱۴] نرخ حرکت قانونی در تلاش اول از {worst["first_try_legal_pct"]} درصد ({worst["label"]}) تا '
               f'{best["first_try_legal_pct"]} درصد ({best["label"]}).')
    return out


def report(args):
    runs = sorted((cc.DATA / 'runs').glob('*/games.jsonl'), key=lambda p: p.stat().st_mtime)
    run = cc.DATA / 'runs' / args.run if args.run else (runs[-1].parent if runs else None)
    if not run or not (run / 'games.jsonl').exists():
        sys.exit('no finished games yet: chess_run.py run …')
    meta = json.loads((run / 'meta.json').read_text(encoding='utf-8'))
    sl, (games, aborted) = meta['slots'], load_games(run)
    st = stats(games, sl)
    res = cc.RESULTS / run.name
    res.mkdir(parents=True, exist_ok=True)
    mock = meta['mode'] == 'mock' or any(s['model'].startswith('mock:') for s in sl)
    tag = '**MOCK · ساختگی: هیچ عددی از این گزارش در ویدیو نمی‌آید.**\n\n' if mock else ''
    L = [f'# HMD-S02 · report · run `{run.name}`', '', tag + f'Started {meta["started"]} · engine: {meta["engine"]} · '
         f'max plies {meta["max_plies"]} · cap {meta["cap_usd"]} USD · fingerprints {meta["fingerprints"]}', '',
         f'{len(games)} games scored, {len(aborted)} aborted (not scored).', '',
         '| model | pts | W-D-L | forfeits | first-try legal % | illegal | recovered % | illegal in book % | '
         'illegal out of book % | ACPL | ACPL out of book | accuracy | blunders/100 | median s | out tok/call | $ |',
         '|' + '---|' * 16]
    for k, v in sorted(st.items(), key=lambda kv: -kv[1]['points']):
        L.append(f'| {v["label"]} `{v["model"]}` | {v["points"]}/{v["games"]} | {v["w"]}-{v["d"]}-{v["l"]} | '
                 f'{v["forfeits"]} | {v["first_try_legal_pct"]} | {v["illegal"]} | {v["recovered_pct"]} | '
                 f'{v["illegal_in_book_pct"]} (n={v["n_in_book"]}) | {v["illegal_out_of_book_pct"]} '
                 f'(n={v["n_out_of_book"]}) | {v["acpl"]} | {v["acpl_out_of_book"]} | {v["accuracy"]} | '
                 f'{v["blunders_per_100"]} | {v["median_s"]} | {v["out_tokens_per_call"]} | {v["usd"]} |')
    L += ['', '## Illegal moves by kind', '', '| model | ' + ' | '.join(cc.KINDS) + ' |', '|' + '---|' * (len(cc.KINDS) + 1)]
    L += [f'| {v["label"]} | ' + ' | '.join(str(v['illegal_kinds'].get(k, 0)) for k in cc.KINDS) + ' |'
          for v in st.values()]
    L += ['', 'Of these, cut off by the output-token limit (stop = max_tokens/length; a harness limit, read before '
          'blaming the model): ' + ', '.join(f'{v["label"]} {v["truncated"]}' for v in st.values())]
    L += ['', '## Games', '', '| game | white | black | result | reason | plies |', '|---|---|---|---|---|---|']
    L += [f'| {g["gid"]} | {g["white"]} | {g["black"]} | {g["result"]} | {g["reason"]} | {len(g["sans"])} |'
          for g in sorted(games + aborted, key=lambda g: g['gid'])]
    L += ['', 'What this cannot show: an Elo. Eight games per model give a 95% interval of roughly ±35 points of '
          'score (hundreds of Elo points). ACPL depends on engine depth and on the position; compare models only '
          'within this run. See protocol.md §6 and study-fa.md.']
    (res / 'report.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    (res / 'summary.json').write_text(json.dumps({'run': run.name, 'meta': meta, 'models': st}, ensure_ascii=False,
                                                 indent=1), encoding='utf-8')
    (res / 'games.pgn').write_text(pgn_text(games, sl, meta['started'][:10].replace('-', '.')), encoding='utf-8')
    evs = sorted(run.glob('events-*.jsonl'), key=lambda p: p.stat().st_size)
    if evs:
        (res / 'events.jsonl').write_text(evs[-1].read_text(encoding='utf-8'), encoding='utf-8')
    sp = spoken_lines(st, games, res / 'events.jsonl')
    (res / 'spoken-fa.txt').write_text(''.join(('[MOCK] ' if mock else '') + fa_digits(x) + '\n' for x in sp),
                                       encoding='utf-8')
    print('\n'.join(L[:8 + len(st)]))
    print(f'→ {res}/report.md · summary.json · games.pgn · events.jsonl · spoken-fa.txt')
    return 0
