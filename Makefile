# Homodyne: episode packages, recording kit and website.
PY ?= python3
.PHONY: help episodes teleprompter selftest site site-dev check

help:
	@echo "make episodes      check every episode package (beats, words, decks, links)"
	@echo "make teleprompter  write parts/…/recording/ (teleprompter + recording sheet) for every episode"
	@echo "make selftest      run the artifact self-tests"
	@echo "make site          build homodyne.m2gh.ir into site/dist"
	@echo "make site-dev      local dev server with future posts visible"
	@echo "make check         episodes + selftest + site"

episodes:
	$(PY) scripts/check-season-01.py
	$(PY) scripts/check-season-01.py channel/global/manifest.json
	@if [ -d private/planning/production-v3 ]; then $(PY) scripts/check-production-v3.py; else echo "skip check-production-v3 (private/ not present)"; fi

teleprompter:
	$(PY) scripts/export-teleprompter.py

selftest:
	$(PY) tools/test_bluff_lab.py
	$(PY) parts/04-global/hmd-b07-photo-geolocation/artifact/geo_lab.py selftest
	$(PY) parts/04-global/hmd-g01-model-collapse/artifact/collapse_lab.py --quick > /dev/null
	$(PY) parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --demo --quiet > /dev/null

site:
	cd site && npm ci && npm run build

site-dev:
	cd site && SHOW_ALL=1 npm run dev

check: episodes selftest site
