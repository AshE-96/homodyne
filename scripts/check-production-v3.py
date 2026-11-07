#!/usr/bin/env python3
"""Verify the revised plan, nine scripts, matching decks, and JS syntax."""
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/'private/planning/production-v3'


def main():
    cards = json.loads((PLAN/'episodes.json').read_text())
    scripts = json.loads((PLAN/'script-manifest.json').read_text())
    refs = json.loads((PLAN/'references.json').read_text())
    assert len(cards) == 30
    assert [c['future'] for c in cards] == list(range(1, 31))
    assert [c['hmd'] for c in cards] == [f'HMD-{i:03}' for i in range(2, 32)]
    assert len(scripts) == 9
    assert sum(c['new'] for c in cards) == 11
    for c in cards:
        assert c['sources'] and all(x in refs for x in c['sources'])
        assert c['hook'] and c['build'] and c['metrics'] and c['boundary'] and c['fallback']
    # E01-E09 were rewritten for season 01 (v5); scripts/check-season-01.py checks them.
    for s in [s for s in scripts if s['status'] != 'MOVED_TO_SEASON_01']:
        folder = ROOT/'parts/02-benchmarking'/s['slug']
        md = (folder/'script-fa.md').read_text()
        deck = (folder/'deck.html').read_text()
        assert md.count('**متن گفتاری:**') == s['beats'] == 10
        assert md.count('**در یک جمله:**') == s['beats']
        assert deck.count('<section class="frame ') == s['beats']
        assert md.count('**ON SCREEN:**') == s['beats']
        assert 'https://fonts.' not in deck and '<script src=' not in deck
        assert 'id="next"' in deck and 'id="prev"' in deck
        if s['episode'] == 8:
            assert s['status'] == 'DATA_LOCK_REQUIRED'
            assert deck.count('EMPIRICAL VALUES INTENTIONALLY ABSENT') == 10
        # Do not apply the archived v1 M2Deck checker to a different v3 engine.
        js = re.search(r'<script>(.*?)</script>', deck, re.S).group(1)
        with tempfile.NamedTemporaryFile(suffix='.js', mode='w') as f:
            f.write(js);f.flush()
            subprocess.run(['node','--check',f.name], check=True, capture_output=True)
        for target in re.findall(r'\]\(([^)]+)\)', md):
            if not target.startswith(('https://','http://','#')):
                assert (folder/target).exists(), (folder, target)
    print('PASS: 30 future episodes, 11 new topics, 36 source IDs; benchmark course E01-E09 checked by check-season-01.py.')


if __name__ == '__main__':
    main()
