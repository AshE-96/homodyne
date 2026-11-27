#!/usr/bin/env python3
"""HMD-007 — boil the public CVE-2025-32711 (EchoLeak) records down to the few fields beat 4 shows.

Inputs (raw downloads, git-ignored, see derived/SOURCE.txt for URLs and sha256):
  NVD API 2.0 record       data/cve-2025-32711/nvd/nvd.json
  MSRC vulnerability API   data/cve-2025-32711/msrc-vuln/vulnerability.json
  MSRC acknowledgement API data/cve-2025-32711/msrc-ack/acknowledgement.json
Output: derived/cve-2025-32711.json  (facts copied verbatim; nothing is computed except picking fields)

    python3 -I cve_record.py --nvd data/cve-2025-32711/nvd/nvd.json \
        --msrc data/cve-2025-32711/msrc-vuln/vulnerability.json \
        --ack data/cve-2025-32711/msrc-ack/acknowledgement.json --out derived/cve-2025-32711.json
    python3 cve_record.py --selftest

Standard library only. No network: download the three files yourself (commands in SOURCE.txt).
"""
import argparse
import json
import re
import sys
from pathlib import Path


def _strip_tags(s):
    return re.sub(r'<[^>]+>', '', s or '').strip()


def extract(nvd, msrc, ack):
    cve = nvd['vulnerabilities'][0]['cve']
    v = msrc['value'][0]
    if cve['id'] != v['cveNumber']:
        raise ValueError(f"NVD record {cve['id']} and MSRC record {v['cveNumber']} disagree")
    desc = next(d['value'] for d in cve['descriptions'] if d['lang'].startswith('en'))
    cvss = {m['source']: {'score': m['cvssData']['baseScore'], 'severity': m['cvssData']['baseSeverity'],
                          'vector': m['cvssData']['vectorString']}
            for m in cve.get('metrics', {}).get('cvssMetricV31', [])}
    faq = next((_strip_tags(a['description']) for a in v.get('articles', []) if a.get('articleType') == 'FAQ'), '')
    return {
        'cve': cve['id'],
        'title_msrc': v['cveTitle'],
        'product': 'Microsoft 365 Copilot',
        'description_cna': desc,
        'published_nvd': cve['published'][:10],
        'released_msrc': v['releaseDate'][:10],
        'severity_msrc': v['severity'],
        'cvss_by_source': cvss,
        'exploited_msrc': v['exploited'],
        'publicly_disclosed_msrc': v['publiclyDisclosed'],
        'customer_action_required_msrc': v['customerActionRequired'],
        'msrc_faq': faq,
        'finders_msrc': [_strip_tags(a['ackText']) for a in ack.get('value', [])],
        'cwe': v.get('cweList', []),
    }


def selftest():
    nvd = {'vulnerabilities': [{'cve': {
        'id': 'CVE-0000-0001', 'published': '2025-06-11T14:15:31.530',
        'descriptions': [{'lang': 'es', 'value': 'x'}, {'lang': 'en', 'value': 'Toy description.'}],
        'metrics': {'cvssMetricV31': [{'source': 'cna@example.invalid', 'cvssData': {
            'baseScore': 9.3, 'baseSeverity': 'CRITICAL', 'vectorString': 'CVSS:3.1/AV:N'}}]}}}]}
    msrc = {'value': [{'cveNumber': 'CVE-0000-0001', 'cveTitle': 'Toy title', 'releaseDate': '2025-06-11T07:00:00-07:00',
                       'severity': 'Critical', 'exploited': 'No', 'publiclyDisclosed': 'No',
                       'customerActionRequired': False, 'cweList': ['CWE-74'],
                       'articles': [{'articleType': 'FAQ', 'description': '<p>Fully <b>mitigated</b>.</p>'}]}]}
    ack = {'value': [{'ackText': '<a href="https://x.invalid">Person A</a> with Org'}, {'ackText': 'Lab B'}]}
    r = extract(nvd, msrc, ack)
    assert r['description_cna'] == 'Toy description.', r
    assert r['cvss_by_source']['cna@example.invalid']['score'] == 9.3
    assert r['exploited_msrc'] == 'No' and r['customer_action_required_msrc'] is False
    assert r['msrc_faq'] == 'Fully mitigated.' and r['finders_msrc'] == ['Person A with Org', 'Lab B']
    assert r['published_nvd'] == '2025-06-11' and r['released_msrc'] == '2025-06-11'
    msrc['value'][0]['cveNumber'] = 'CVE-0000-0002'
    try:
        extract(nvd, msrc, ack)
    except ValueError:
        pass
    else:
        raise AssertionError('mismatched CVE ids must fail')
    print('selftest ok')


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--nvd')
    ap.add_argument('--msrc')
    ap.add_argument('--ack')
    ap.add_argument('--out')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.nvd and a.msrc and a.ack):
        ap.error('--nvd, --msrc and --ack are required (or --selftest)')
    load = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    text = json.dumps(extract(load(a.nvd), load(a.msrc), load(a.ack)), ensure_ascii=False, indent=1) + '\n'
    if a.out:
        Path(a.out).write_text(text, encoding='utf-8')
    sys.stdout.write(text)


if __name__ == '__main__':
    main()
