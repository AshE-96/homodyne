#!/usr/bin/env python3
"""HMD-006 · turn two public downloads into the small files the episode shows.

    python3 -I artifact/real_data.py vectara   artifact/data/vectara-2026-11-26/README.md   artifact/derived
    python3 -I artifact/real_data.py charlotin artifact/data/charlotin-2026-11-26/download.csv artifact/derived
    python3 -I artifact/real_data.py --selftest

vectara   : parses the leaderboard table between <!-- LEADERBOARD_START/END --> in the README of
            github.com/vectara/hallucination-leaderboard (Apache-2.0) and writes
            vectara_leaderboard_<date>.csv and same_model_two_definitions.csv (joins two rows with
            the AA-Omniscience numbers that are printed in the text of arXiv 2511.13029).
charlotin : counts the AI Hallucination Cases database CSV (Damien Charlotin, CC BY 4.0) by
            quarter of decision and writes charlotin_cases_by_quarter.csv + charlotin_summary.json.

Every number written is either copied from a source or a plain count of its rows; nothing is
modelled. Downloads are untrusted: they are parsed as text/CSV only. Standard library only.
"""
import csv
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

# AA-Omniscience (Artificial Analysis, arXiv 2511.13029 v1, section 3.1 text; checked 26 Nov 2026).
# Only numbers printed in the paper's text are used; Figure 7 is an image and is not transcribed.
AA_TEXT = {
    'openai/gpt-5-high-2025-08-07': ('GPT-5 (high)', 81.0, 'S3.1: "hallucination rates of 64% and 81%" (Grok 4, GPT-5 (high))'),
    'anthropic/claude-haiku-4-5-20251001': ('Claude 4.5 Haiku', 26.0, 'S3.1: "16% accuracy but a 26% hallucination rate"'),
}
MONTHS = {m: i for i, m in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July',
                                      'August', 'September', 'October', 'November', 'December'], 1)}


def pct(cell):
    m = re.fullmatch(r'\s*([0-9]+(?:\.[0-9]+)?)\s*%\s*', cell)
    if not m:
        raise ValueError(f'not a percentage: {cell!r}')
    return float(m.group(1))


def parse_vectara(text):
    """Return (iso_date, rows). rows: dicts with model and four numbers, in table order."""
    block = re.search(r'<!-- LEADERBOARD_START -->(.*?)<!-- LEADERBOARD_END -->', text, re.S)
    if not block:
        raise ValueError('leaderboard markers not found')
    body = block.group(1)
    d = re.search(r'Last updated on (\w+) (\d{1,2}), (\d{4})', body)
    if not d or d.group(1) not in MONTHS:
        raise ValueError('no "Last updated on <Month> <d>, <yyyy>" line')
    date = f'{int(d.group(3)):04d}-{MONTHS[d.group(1)]:02d}-{int(d.group(2)):02d}'
    rows = []
    header = None
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if header is None:
            header = cells
            want = ['Model', 'Hallucination Rate', 'Factual Consistency Rate', 'Answer Rate',
                    'Average Summary Length (Words)']
            if header != want:
                raise ValueError(f'unexpected header {header}')
            continue
        if set(''.join(cells)) <= set('-: '):
            continue
        if len(cells) != 5:
            raise ValueError(f'bad row {line[:80]}')
        rows.append({'model': cells[0], 'hallucination_rate_pct': pct(cells[1]),
                     'factual_consistency_pct': pct(cells[2]), 'answer_rate_pct': pct(cells[3]),
                     'avg_summary_words': float(cells[4])})
    if not rows:
        raise ValueError('no rows')
    for r in rows:  # the README defines hallucination rate as 100 - factual consistency
        if abs(r['hallucination_rate_pct'] + r['factual_consistency_pct'] - 100) > 0.11:
            raise ValueError(f'{r["model"]}: rates do not sum to 100')
    return date, rows


def join_two_definitions(rows):
    by = {r['model']: r for r in rows}
    out = []
    for key, (aa_name, aa_rate, aa_quote) in AA_TEXT.items():
        if key not in by:
            raise ValueError(f'{key} missing from the Vectara table')
        out.append({'vectara_model': key, 'aa_model': aa_name,
                    'vectara_hallucination_rate_pct': by[key]['hallucination_rate_pct'],
                    'vectara_answer_rate_pct': by[key]['answer_rate_pct'],
                    'aa_hallucination_rate_pct': aa_rate, 'aa_source_text': aa_quote})
    return out


def quarter_counts(records):
    """records: iterable of dicts with 'Date' = YYYY-MM-DD. Returns (Counter{(y,q):n}, bad_count)."""
    c, bad = Counter(), 0
    for r in records:
        m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', (r.get('Date') or '').strip())
        if not m or not 1 <= int(m.group(2)) <= 12:
            bad += 1
            continue
        c[(int(m.group(1)), (int(m.group(2)) - 1) // 3 + 1)] += 1
    return c, bad


def summarise_charlotin(records):
    q, bad = quarter_counts(records)
    dates = sorted(r['Date'] for r in records if re.fullmatch(r'\d{4}-\d{2}-\d{2}', r.get('Date', '')))
    first_id = [r for r in records if r.get('case_id', '').strip() == '1']
    return q, {
        'rows': len(records),
        'rows_without_valid_date': bad,
        'latest_decision_date_in_file': dates[-1] if dates else None,
        'earliest_decision_date_in_file': dates[0] if dates else None,
        'by_party_top': Counter(r.get('Party(ies)', '') for r in records).most_common(4),
        'by_country_top': Counter(r.get('State(s)', '') for r in records).most_common(5),
        'alleged_only_yes': sum(1 for r in records if r.get('Alleged', '').strip() == 'Yes'),
        'case_id_1': ({k: first_id[0].get(k, '') for k in ('Case Name', 'Court', 'Date', 'AI Tool',
                                                         'Monetary Penalty')} if first_id else None),
    }


def write_csv(path, fields, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def cmd_vectara(raw, outdir):
    date, rows = parse_vectara(Path(raw).read_text(encoding='utf-8'))
    out = Path(outdir)
    fields = ['rank', 'model', 'hallucination_rate_pct', 'factual_consistency_pct', 'answer_rate_pct',
              'avg_summary_words']
    write_csv(out / f'vectara_leaderboard_{date}.csv', fields,
              [dict(rank=i, **r) for i, r in enumerate(rows, 1)])
    pairs = join_two_definitions(rows)
    write_csv(out / 'same_model_two_definitions.csv', list(pairs[0]), pairs)
    lo, hi = rows[0], rows[-1]
    print(f'vectara {date}: {len(rows)} models, lowest {lo["model"]} {lo["hallucination_rate_pct"]}%, '
          f'highest {hi["model"]} {hi["hallucination_rate_pct"]}%')
    for p in pairs:
        print(f'  {p["vectara_model"]}: Vectara {p["vectara_hallucination_rate_pct"]}% · '
              f'AA-Omniscience {p["aa_hallucination_rate_pct"]}%')


def cmd_charlotin(raw, outdir):
    with open(raw, encoding='utf-8-sig', newline='') as f:
        records = list(csv.DictReader(f))
    q, summary = summarise_charlotin(records)
    out = Path(outdir)
    last = max(q) if q else None
    write_csv(out / 'charlotin_cases_by_quarter.csv', ['quarter', 'cases', 'note'],
              [{'quarter': f'{y}-Q{n}', 'cases': q[(y, n)],
                'note': 'partial quarter (file ends here)' if (y, n) == last else ''} for (y, n) in sorted(q)])
    (out / 'charlotin_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1) + '\n',
                                                encoding='utf-8')
    print(f'charlotin: {summary["rows"]} rows; latest decision {summary["latest_decision_date_in_file"]}; '
          f'{len(q)} quarters; peak {max(q.values()) if q else 0}')


SAMPLE_README = """intro
<!-- LEADERBOARD_START -->
Last updated on November 24, 2026

|Model|Hallucination Rate|Factual Consistency Rate|Answer Rate|Average Summary Length (Words)|
|----|----:|----:|----:|----:|
|antgroup/finix_s1_32b|1.8 %|98.2 %|99.5 %|172.4|
|anthropic/claude-haiku-4-5-20251001|9.8 %|90.2 %|99.5 %|115.1|
|openai/gpt-5-high-2025-08-07|15.1 %|84.9 %|99.9 %|162.7|
<!-- LEADERBOARD_END -->
tail
"""
SAMPLE_CSV = ('case_id,Case Name,Date,Party(ies),State(s),Alleged,Court,AI Tool,Monetary Penalty\n'
              '1,Mata v. Avianca,2023-06-22,Lawyer,USA,No,S.D. New York,ChatGPT,5000 USD\n'
              '2,B,2023-04-14,Lawyer,Brazil,No,X,,\n'
              '3,C,2026-11-20,Pro Se Litigant,USA,Yes,Y,,\n'
              '4,D,not a date,Lawyer,UK,No,Z,,\n')


def selftest():
    date, rows = parse_vectara(SAMPLE_README)
    assert date == '2026-11-24', date
    assert [r['model'] for r in rows][0] == 'antgroup/finix_s1_32b'
    assert rows[2]['hallucination_rate_pct'] == 15.1 and rows[2]['answer_rate_pct'] == 99.9
    pairs = join_two_definitions(rows)
    assert pairs[0]['aa_hallucination_rate_pct'] == 81.0 and pairs[0]['vectara_hallucination_rate_pct'] == 15.1
    for bad in (SAMPLE_README.replace('84.9', '80.0'), SAMPLE_README.replace('LEADERBOARD_END', 'X'),
                SAMPLE_README.replace('15.1 %', 'n/a')):
        try:
            parse_vectara(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('bad README accepted')
    records = list(csv.DictReader(io.StringIO(SAMPLE_CSV)))
    q, s = summarise_charlotin(records)
    assert q == Counter({(2023, 2): 2, (2026, 4): 1}), q
    assert s['rows'] == 4 and s['rows_without_valid_date'] == 1 and s['alleged_only_yes'] == 1
    assert s['case_id_1']['Case Name'] == 'Mata v. Avianca' and s['earliest_decision_date_in_file'] == '2023-04-14'
    print('selftest ok')
    return 0


def main(argv):
    if argv == ['--selftest']:
        return selftest()
    if len(argv) == 3 and argv[0] in ('vectara', 'charlotin'):
        (cmd_vectara if argv[0] == 'vectara' else cmd_charlotin)(argv[1], argv[2])
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
