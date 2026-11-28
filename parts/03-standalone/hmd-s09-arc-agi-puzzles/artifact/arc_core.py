"""HMD-S09 · shared core: the five chosen ARC tasks, grid text, the locked prompt, reply parsing, exact match.

Standard library only. Everything that defines the model experiment lives here (PROMPT_HEAD, prompt_for, parse_reply,
MAX_TOKENS), so arc_run.py can fingerprint it (sha256) before a paid run.

Data: five public ARC tasks are committed in data/tasks/ (Apache-2.0; data/SOURCE.txt, data/LICENSE-*.txt).
The full public sets are NOT committed; `python3 arc_core.py fetch` downloads them at run time into cache/ (git-ignored).
"""
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DATA = HERE / 'data' / 'tasks'
CACHE = HERE / 'cache'
MAX_TOKENS = 16000

# The five puzzles of the episode, in the order they are played. `set` says where each task file comes from.
PUZZLES = [
    dict(n=1, id='1e0a9b12', set='ARC-AGI-1 training (also in ARC-AGI-2 training)', prior='objects + gravity',
         fa='همه‌چیز می‌افتد', en='Everything falls', beat=1),
    dict(n=2, id='007bbfb7', set='ARC-AGI-1 training (also in ARC-AGI-2 training)', prior='copy a shape into itself',
         fa='شکل داخل خودش', en='A shape inside itself', beat=5),
    dict(n=3, id='a5313dff', set='ARC-AGI-1 training (also in ARC-AGI-2 training)', prior='inside vs outside',
         fa='داخلِ بسته را پر کن', en='Fill what is enclosed', beat=4),
    dict(n=4, id='3aa6fb7a', set='ARC-AGI-1 training (also in ARC-AGI-2 training)', prior='corners, orientation',
         fa='گوشهٔ خالی', en='The missing corner', beat=6),
    dict(n=5, id='1ae2feb7', set='ARC-AGI-2 public evaluation', prior='counting + projection + priority',
         fa='طول، فاصله می‌شود', en='Length becomes spacing', beat=8),
]
SOURCES = {
    'ARC-AGI-1': ('https://github.com/fchollet/ARC-AGI', '399030444e0ab0cc8b4e199870fb20b863846f34', 'master'),
    'ARC-AGI-2': ('https://github.com/arcprize/ARC-AGI-2', 'f3283f727488ad98fe575ea6a5ac981e4a188e49', 'main'),
}

PROMPT_HEAD = (
    'You are solving one ARC-AGI puzzle. Each grid is a rectangle of integers 0-9 (each integer is a colour). '
    'Below are demonstration pairs: an input grid and the output grid it was transformed into. The same hidden rule '
    'turns every input into its output. Then comes one test input. Work out the rule and produce the output grid for '
    'the test input, including its exact height and width.\n'
    'You may give two different candidate answers (as in ARC Prize, two attempts; one exact match counts as solved).\n'
    'Reply with JSON only, no prose: {"attempt_1": [[...], ...], "attempt_2": [[...], ...]} where each attempt is a '
    'list of rows and each row is a list of integers.\n')


# ── tasks ──────────────────────────────────────────────────────────────────────────────────────
def load_task(task_id):
    for p in (DATA / f'{task_id}.json', *sorted(CACHE.glob(f'**/{task_id}.json'))):
        if p.exists():
            t = json.loads(p.read_text(encoding='utf-8'))
            check_task(t, task_id)
            return t
    raise FileNotFoundError(f'{task_id}.json not in data/tasks/ or cache/ (python3 arc_core.py fetch)')


def check_task(t, name='task'):
    if not isinstance(t, dict) or not t.get('train') or not t.get('test'):
        raise ValueError(f'{name}: needs non-empty "train" and "test"')
    for pair in t['train'] + t['test']:
        for k in ('input', 'output'):
            if k in pair:
                check_grid(pair[k], name)


def check_grid(g, name='grid'):
    ok = (isinstance(g, list) and 1 <= len(g) <= 30 and all(isinstance(r, list) and r for r in g)
          and len({len(r) for r in g}) == 1 and len(g[0]) <= 30
          and all(isinstance(c, int) and not isinstance(c, bool) and 0 <= c <= 9 for r in g for c in r))
    if not ok:
        raise ValueError(f'{name}: not a rectangular 1x1..30x30 grid of integers 0-9')
    return g


def puzzles():
    """The five puzzles with their task data (for the page and the run)."""
    return [{**p, 'task': load_task(p['id'])} for p in PUZZLES]


def test_items():
    """(puzzle n, task id, test index) for every test input; a task is solved only if all its test inputs are."""
    return [(p['n'], p['id'], i) for p in PUZZLES for i in range(len(load_task(p['id'])['test']))]


# ── how the model sees a grid ─────────────────────────────────────────────────────────────────
def grid_text(g):
    """One line per row, cells separated by a space: '0 4 0 9'. This exact text goes into the prompt."""
    return '\n'.join(' '.join(str(c) for c in row) for row in g)


def prompt_for(task, test_index=0):
    parts = [PROMPT_HEAD]
    for i, pair in enumerate(task['train'], 1):
        parts.append(f'\nDemonstration {i} input ({len(pair["input"])}x{len(pair["input"][0])}):\n'
                     + grid_text(pair['input']))
        parts.append(f'\nDemonstration {i} output ({len(pair["output"])}x{len(pair["output"][0])}):\n'
                     + grid_text(pair['output']))
    g = task['test'][test_index]['input']
    parts.append(f'\nTest input ({len(g)}x{len(g[0])}):\n' + grid_text(g))
    return '\n'.join(parts) + '\n'


def column_gap(g):
    """Characters between a cell and the cell directly below it in grid_text: the row's width in text plus a newline.
    Neighbours to the left/right are 2 characters apart; neighbours above/below are this far apart."""
    return 2 * len(g[0])


# ── replies and scoring ───────────────────────────────────────────────────────────────────────
def _grid_or_none(x):
    try:
        return check_grid(x)
    except (ValueError, TypeError):
        return None


def parse_reply(text):
    """Return ([attempt_1, attempt_2], flag). Grids that are not valid count as no answer. Never raises."""
    text = (text or '').strip()
    m = re.search(r'```(?:json)?\s*(.*?)```', text, re.S)
    body = m.group(1) if m else text
    cands = []
    try:
        obj = json.loads(body[body.find('{'):body.rfind('}') + 1]) if '{' in body else json.loads(body)
        if isinstance(obj, dict):
            cands = [obj.get('attempt_1'), obj.get('attempt_2')]
        elif isinstance(obj, list):
            cands = [obj]
    except (ValueError, TypeError):
        lists = re.findall(r'\[\s*\[[\d,\s\[\]]*\]\s*\]', body)
        cands = []
        for s in lists[:2]:
            try:
                cands.append(json.loads(s))
            except ValueError:
                cands.append(None)
    grids = [_grid_or_none(c) for c in cands[:2]] + [None, None]
    grids = grids[:2]
    flag = 'ok' if grids[0] or grids[1] else 'unparsed'
    return grids, flag


def exact(a, b):
    """ARC's rule: same height, same width, every cell equal. Nothing partial."""
    return a is not None and b is not None and len(a) == len(b) and all(ra == rb for ra, rb in zip(a, b))


def cells_right(a, b):
    """For the page only (never a score): how many cells match when the sizes agree."""
    if not a or not b or len(a) != len(b) or len(a[0]) != len(b[0]):
        return None
    return sum(x == y for ra, rb in zip(a, b) for x, y in zip(ra, rb))


def solved(attempts, truth):
    return any(exact(a, truth) for a in attempts if a)


# ── full public sets, at run time only ─────────────────────────────────────────────────────────
def fetch(which=('ARC-AGI-1', 'ARC-AGI-2')):
    """Download the full public sets (pinned commits) into cache/<name>/. Not needed for the episode itself."""
    for name in which:
        url, sha, _ = SOURCES[name]
        zurl = url.replace('https://github.com/', 'https://codeload.github.com/') + f'/zip/{sha}'
        print(f'{name}: {zurl}')
        raw = urllib.request.urlopen(zurl, timeout=120).read()
        out = CACHE / name
        n = 0
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for info in z.infolist():
                parts = Path(info.filename).parts
                if len(parts) >= 4 and parts[1] == 'data' and parts[-1].endswith('.json') and '..' not in parts:
                    target = out / parts[2] / parts[-1]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    t = json.loads(z.read(info).decode('utf-8'))
                    check_task(t, parts[-1])
                    target.write_text(json.dumps(t), encoding='utf-8')
                    n += 1
        print(f'  {n} task files → {out}')


if __name__ == '__main__':
    if sys.argv[1:] == ['fetch']:
        fetch()
    else:
        print(__doc__)
