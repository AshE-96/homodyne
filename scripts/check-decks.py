#!/usr/bin/env python3
"""
check-decks.py — structural checks for the episode screen layers.

These decks are driven live during a recording session. A broken build hook or
a config pointing at an element that isn't there does not throw a visible
error; it just silently renders a slide that never advances, which is only
discovered mid-take. So the things that would fail quietly get checked here.

    ./scripts/check-decks.py            # all decks
    ./scripts/check-decks.py 2 3        # only episodes 2 and 3

Exit code is non-zero if any deck fails.
"""

import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BUILD_ATTRS = ("data-build", "data-track", "data-since")


class Deck(HTMLParser):
    """Collects just enough structure to answer the questions below."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.slides = []          # list of dicts, one per <section class="slide">
        self.hooks = []           # (attr, raw_value, tag)
        self.depth_stack = []
        self._slide = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "")

        if a.get("id"):
            self.ids.append(a["id"])

        for attr in BUILD_ATTRS:
            if attr in a:
                self.hooks.append((attr, a[attr], tag))
                if self._slide is not None:
                    self._slide["hooks"].append((attr, a[attr]))

        if tag == "section" and "slide" in cls.split():
            self._slide = {
                "comp": a.get("data-comp"),
                "time": a.get("data-time"),
                "theme": a.get("data-theme"),
                "focus": a.get("data-focus"),
                "start": a.get("data-start"),
                "hooks": [],
            }
            self.slides.append(self._slide)

    def handle_endtag(self, tag):
        if tag == "section" and self._slide is not None:
            self._slide = None


def check(path):
    name = os.path.relpath(path, ROOT)
    problems = []
    warnings = []

    with open(path, encoding="utf-8") as fh:
        html = fh.read()

    # ── the shared design language must actually be inlined ──────────────
    for kind, needle in (("css", ":root{"), ("js", "window.M2Deck")):
        m = re.search(
            r"/\* @shared:%s:start \*/(.*?)/\* @shared:%s:end \*/" % (kind, kind),
            html, re.DOTALL)
        if not m:
            problems.append("missing @shared:%s marker pair" % kind)
        elif needle not in m.group(1):
            problems.append(
                "@shared:%s block looks empty — run scripts/sync-design-language.sh" % kind)

    deck = Deck()
    deck.feed(html)

    # ── ids must be unique; the engine looks elements up by id ───────────
    for dup, n in Counter(deck.ids).items():
        if n > 1:
            problems.append("duplicate id %r (%d times)" % (dup, n))

    for required in ("deck", "viewport"):
        if required not in deck.ids:
            problems.append("missing required element #%s" % required)

    # ── slides ───────────────────────────────────────────────────────────
    if not deck.slides:
        problems.append("no .slide sections found")

    for i, s in enumerate(deck.slides, 1):
        if not s["comp"]:
            problems.append("slide %d has no data-comp label" % i)
        if not s["time"]:
            warnings.append("slide %d has no data-time" % i)
        if s["theme"] not in (None, "graphite"):
            problems.append("slide %d has unknown data-theme %r" % (i, s["theme"]))
        if s["focus"] not in (None, "off"):
            problems.append("slide %d has unknown data-focus %r" % (i, s["focus"]))
        if s["start"] is not None and not re.fullmatch(r"\d+", s["start"]):
            problems.append("slide %d has non-numeric data-start %r" % (i, s["start"]))

        # An interior gap in the step numbers is always a bug: pressing right
        # would consume a beat and change nothing on screen. A gap at step 1 is
        # fine and often deliberate — that is a slide that opens on a held
        # composition (a bare number, empty axes) and only then starts moving.
        nums = set()
        for attr, raw in s["hooks"]:
            if not re.fullmatch(r"\d+", raw or "") or int(raw) < 1:
                problems.append("slide %d: %s=%r is not a positive integer" % (i, attr, raw))
            else:
                nums.add(int(raw))
        if nums:
            missing = sorted(set(range(2, max(nums))) - nums)
            if missing:
                problems.append(
                    "slide %d (%s): build steps %s are skipped — those beats show nothing new"
                    % (i, s["comp"], ", ".join(map(str, missing))))

    # ── every id the config points at has to exist in the markup ─────────
    # Look only after the shared block: its header comment contains a worked
    # example of an init() call, which would otherwise be parsed as real config.
    tail = html.split("/* @shared:js:end */")[-1]
    cfg = re.search(r"M2Deck\.init\(\s*\{(.*)\}\s*\)\s*;", tail, re.DOTALL)
    if not cfg:
        problems.append("no M2Deck.init({...}) call found")
    else:
        body = cfg.group(1)
        present = set(deck.ids)

        for section in ("tables", "entities", "lists"):
            block = re.search(section + r"\s*:\s*\{", body)
            if not block:
                continue
            # keys at the top level of that section
            start = block.end()
            depth, j = 1, start
            while j < len(body) and depth:
                if body[j] == "{":
                    depth += 1
                elif body[j] == "}":
                    depth -= 1
                j += 1
            chunk = body[start:j]
            for key in re.findall(r"'([A-Za-z0-9_-]+)'\s*:\s*\{", chunk):
                # only top-level keys look like element ids; inner ones are options
                if key in ("head", "rows", "term", "strike", "chips", "items", "countId"):
                    continue
                if key not in present:
                    problems.append("config targets #%s, which is not in the markup" % key)

        for extra in re.findall(r"(?:chips|countId)\s*:\s*'([A-Za-z0-9_-]+)'", body):
            if extra not in present:
                problems.append("config references #%s, which is not in the markup" % extra)

        ep = re.search(r"episode\s*:\s*'([^']+)'", body)
        rt = re.search(r"runtime\s*:\s*(\d+)", body)
        if not ep:
            warnings.append("no episode label in config (chrome will say Ep.01)")
        if not rt:
            warnings.append("no runtime in config (scrubber will be wrong)")
        elif deck.slides:
            starts = [int(s["start"]) for s in deck.slides if s["start"] is not None]
            if starts and max(starts) > int(rt.group(1)):
                problems.append(
                    "a slide starts at %ss but runtime is %ss" % (max(starts), rt.group(1)))

    # ── a syntax error in the inlined script would break the deck in silence,
    #    and it would only be discovered with a camera running ──────────────
    if shutil.which("node"):
        scripts = re.findall(r"<script>(.*?)</script>", html, re.DOTALL)
        tmp = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                             encoding="utf-8") as fh:
                fh.write("\n;\n".join(scripts))
                tmp = fh.name
            r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
            if r.returncode:
                first = (r.stderr.strip().splitlines() or [""])[0]
                problems.append("javascript does not parse: %s" % first[:160])
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)
    else:
        warnings.append("node not found — skipped the javascript syntax check")

    return name, problems, warnings, len(deck.slides)


def main(argv):
    if argv:
        paths = []
        for ep in argv:
            paths += glob.glob(os.path.join(ROOT, "parts", "02-benchmarking", "_archive", "v1-m2lab", ep, "*Design_Mockup.html"))
    else:
        paths = sorted(glob.glob(os.path.join(ROOT, "parts", "02-benchmarking", "_archive", "v1-m2lab", "*", "*Design_Mockup.html")))

    if not paths:
        print("no decks found", file=sys.stderr)
        return 1

    failed = 0
    for path in paths:
        name, problems, warnings, n = check(path)
        status = "FAIL" if problems else "ok  "
        print("%s  %-52s %2d slides" % (status, name, n))
        for w in warnings:
            print("        warn: %s" % w)
        for p in problems:
            print("        %s" % p)
        if problems:
            failed += 1

    print()
    print("%d deck(s) checked, %d failed" % (len(paths), failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
