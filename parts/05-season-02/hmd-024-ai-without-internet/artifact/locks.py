"""HMD-024 · the rule lock: hashes of the files that decide a result, recorded at `run` and checked at `report`.

rules.json (decision rules), task_bank.py (tasks and keys) and graders.py (what "pass" means) are hashed with
SHA-256 when a run starts. `report` refuses to build a card if any of them changed since, or if two runs were
made under different versions, unless `--allow-changed-rules` is given (and then the card says so).
If git shows these files committed and unchanged, the commit is recorded too.
"""
import hashlib
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCKED = ['rules.json', 'task_bank.py', 'graders.py']


def hashes(folder=HERE):
    return {f: hashlib.sha256((Path(folder) / f).read_bytes()).hexdigest() for f in LOCKED}


def git_state(folder=HERE):
    def git(*a):
        r = subprocess.run(['git', '-C', str(folder), *a], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else None
    try:
        commit = git('rev-parse', '--short=12', 'HEAD')
        tracked = all(git('ls-files', '--error-unmatch', f) is not None for f in LOCKED)
        dirty = git('status', '--porcelain', '--', *LOCKED)
    except Exception:  # noqa: BLE001 — no git: just no commit on the card
        return {'commit': None, 'locked_files_committed_and_clean': False}
    clean = bool(commit) and tracked and dirty == ''
    return {'commit': commit if clean else None, 'locked_files_committed_and_clean': clean}


def record(folder=HERE):
    return {'sha256': hashes(folder), 'git': git_state(folder)}


def problems(runs, current=None):
    """List of human-readable lock problems across runs (empty = all good)."""
    current = current or hashes()
    out = []
    for run in runs:
        rec = (run['meta'].get('locks') or {}).get('sha256')
        name = run['dir'].name
        if not rec:
            out.append(f'{name}: no lock hashes recorded (run made before the lock existed?)')
            continue
        for f, h in current.items():
            if rec.get(f) != h:
                out.append(f'{name}: {f} changed since this run (run {rec.get(f, "?")[:12]}, now {h[:12]})')
    return out
