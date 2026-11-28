# Homodyne: episode packages, recording kit and website.
PY ?= python3
.PHONY: help decks episodes teleprompter selftest site site-dev preview deploy check

help:
	@echo "make decks         build deck-fa.html + deck-en.html from each deck.src.html"
	@echo "make episodes      check every episode package (beats, words, decks, links)"
	@echo "make teleprompter  write parts/…/recording/ (teleprompter + recording sheet) for every episode"
	@echo "make selftest      run the artifact self-tests"
	@echo "make site          build homodyne.m2gh.ir into site/dist"
	@echo "make site-dev      local dev server with future posts visible"
	@echo "make preview       build and serve the site as it will go live (http://localhost:4321)"
	@echo "make deploy        check, build and upload to Cloudflare (homodyne.m2gh.ir)"
	@echo "make check         episodes + selftest + site"

decks:
	$(PY) scripts/build-decks.py --quiet

episodes:
	$(PY) scripts/build-decks.py --check --quiet
	$(PY) scripts/check-season-01.py
	$(PY) scripts/check-season-01.py channel/global/manifest.json
	$(PY) scripts/check-season-01.py channel/season-02/manifest.json
	@if [ -d private/planning/production-v3 ]; then $(PY) scripts/check-production-v3.py; else echo "skip check-production-v3 (private/ not present)"; fi

teleprompter:
	$(PY) scripts/export-teleprompter.py

selftest:
	$(PY) tools/test_bluff_lab.py
	$(PY) parts/04-global/hmd-b07-photo-geolocation/artifact/geo_lab.py selftest
	$(PY) parts/04-global/hmd-g01-model-collapse/artifact/collapse_lab.py --quick > /dev/null
	$(PY) parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --demo --quiet > /dev/null
	$(PY) parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/artifact/power_lab.py --selftest > /dev/null
	$(PY) parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py --selftest > /dev/null
	$(PY) parts/02-benchmarking/e08-which-model-knows-when-to-abstain/artifact/abstain_report.py --selftest > /dev/null
	$(PY) parts/02-benchmarking/e09-how-do-you-publish-a-refutable-result/artifact/recompute_check.py --selftest > /dev/null
	$(PY) parts/02-benchmarking/e02-which-benchmark-answers-your-question/artifact/real_data.py --selftest > /dev/null
	$(PY) parts/03-standalone/hmd-005-persian-tokens/artifact/crosscheck.py --selftest > /dev/null
	$(PY) parts/03-standalone/hmd-005-persian-tokens/artifact/token_view.py --selftest > /dev/null
	$(PY) parts/02-benchmarking/e03-what-exactly-are-we-measuring/artifact/real_data.py --selftest > /dev/null
	$(PY) parts/03-standalone/hmd-007-prompt-injection/artifact/cve_record.py --selftest > /dev/null
	env -u OLLAMA_HOST $(PY) parts/03-standalone/hmd-007-prompt-injection/artifact/ollama_adapter.py --selftest > /dev/null
	$(PY) parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/mmlu_redux_audit.py --selftest > /dev/null
	$(PY) parts/03-standalone/hmd-009-maps-eta/artifact/nyc_eta.py --selftest > /dev/null
	$(PY) parts/03-standalone/hmd-009-maps-eta/artifact/make_figures.py --selftest > /dev/null
	$(PY) parts/02-benchmarking/e05-how-do-you-penalise-a-bluff/artifact/penalty_threshold.py --selftest > /dev/null
	$(PY) parts/03-standalone/hmd-s01-riemann-and-ai/artifact/zeta_live.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) tools/llm.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-k01-ai-takes-konkur/artifact/konkur_prep.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-k01-ai-takes-konkur/artifact/konkur_run.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-k01-ai-takes-konkur/artifact/rank_estimate.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-k01-ai-takes-konkur/artifact/konkur_live.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-s02-ai-chess-tournament/artifact/chess_live.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-s03-alphafold-iranian-diseases/artifact/fold_live.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-s04-ai-hurricane-forecast/artifact/storm_live.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-s05-ai-at-the-math-olympiad/artifact/imo_live.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-s06-damavand-summit-weather/artifact/summit_live.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-s07-chalus-traffic/artifact/chalus_live.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-s08-when-to-leave/artifact/leave_live.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-s09-arc-agi-puzzles/artifact/arc_live.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-s10-erdos-problems/artifact/erdos_live.py --selftest > /dev/null
	env -u GEMINI_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY $(PY) parts/03-standalone/hmd-s11-paragliding-wind/artifact/wind_live.py --selftest > /dev/null
	HOMODYNE_MODEL=mock:echo $(PY) tools/llm.py which > /dev/null
	$(PY) parts/05-season-02/hmd-011-solar-storm-forecast/artifact/storm_replay.py --selftest > /dev/null
	$(PY) parts/05-season-02/hmd-013-fake-review-detector/artifact/review_lab.py --selftest > /dev/null
	HOMODYNE_MODEL=mock:echo $(PY) parts/05-season-02/hmd-013-fake-review-detector/artifact/ai_text_lab.py --selftest > /dev/null
	HOMODYNE_MODEL=mock:echo $(PY) parts/05-season-02/hmd-015-answer-in-the-file/artifact/answer_in_file.py --selftest > /dev/null
	$(PY) parts/05-season-02/hmd-017-why-this-recommendation/artifact/recsys_xray.py --selftest > /dev/null
	HOMODYNE_MODEL=mock:echo $(PY) parts/05-season-02/hmd-019-agent-repeats-a-paper/artifact/selftest.py > /dev/null
	HOMODYNE_MODEL=mock:echo $(PY) parts/05-season-02/hmd-020-valid-json-wrong-answer/artifact/testbench.py --selftest > /dev/null
	HOMODYNE_MODEL=mock:echo $(PY) parts/05-season-02/hmd-021-same-resume-different-name/artifact/resume_audit.py --selftest > /dev/null
	HOMODYNE_MODEL=mock:echo $(PY) parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/routing_lab.py --selftest > /dev/null
	$(PY) parts/05-season-02/hmd-023-hundred-users-at-once/artifact/load_lab.py --selftest > /dev/null
	HOMODYNE_MODEL=mock:echo $(PY) parts/05-season-02/hmd-024-ai-without-internet/artifact/offline_lab.py --selftest > /dev/null

site:
	cd site && npm ci && npm run build

site-dev:
	cd site && SHOW_ALL=1 npm run dev

preview: site
	cd site && npx astro preview

# Posts go live when their date has arrived, so deploy on each release day.
deploy: episodes selftest
	cd site && npm ci && npm run deploy

check: episodes selftest site
