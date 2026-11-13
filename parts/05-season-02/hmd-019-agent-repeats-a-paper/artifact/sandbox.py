#!/usr/bin/env python3
"""Fresh workspaces and isolated execution for HMD-019's agent lab.

Two executors run the code a model writes. Be honest about each:

* docker (DEFAULT, recommended). Every code step runs as
      docker run --rm --network none --memory 512m --cpus 1 --pids-limit 128 --read-only
                 --tmpfs /tmp -v <workspace>:/work -w /work --user <uid>:<gid> -e HOME=/tmp
                 <image> python3 -I /work/<script>
  No network, a read-only root, only the task folder mounted (writable), no home folder,
  and no environment variable from the host except HOME=/tmp: no API keys. On macOS the
  container even runs in a separate Linux VM, so it cannot see host processes.
  The image (default python:3.11-slim) is never pulled by this code: if it or the daemon
  is missing, `run` prints what to do and stops.

* macos-sandbox (OPT-IN ONLY: --executor macos-sandbox --i-accept-key-exposure).
  `sandbox-exec` (deprecated by Apple, still shipped): no network, writes only in the
  task folder, no reads under the home folder (so not this repository, the answer key,
  private/keys.env or ~/.ssh). BUT the code runs as your user on your machine and can
  read the environment of your other processes (sysctl KERN_PROCARGS2 / `ps eww`). An API
  key exported in any shell of yours is therefore readable. This mode refuses to start if
  a *_KEY / *_TOKEN / *SECRET* variable is in this process's environment; keep keys in
  private/keys.env (tools/llm.py reads them without exporting) and make sure no other
  shell exports them. The probe's leak test shows the weakness on purpose.

Every executor also gets: a wall-clock timeout, output trimming, and redaction: every
value from llm.secrets() and every environment value whose name contains KEY, TOKEN or
SECRET is replaced by [REDACTED] before the output reaches the model, a transcript or the
cache. For the strongest isolation use Docker, or a separate macOS user, or a VM.

Standard library only (plus tools/llm.py for the list of secrets).
"""
from __future__ import annotations

import hashlib
import os
import re
import resource
import secrets as pysecrets
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / 'tools'))
import llm  # noqa: E402

PY = os.path.realpath(sys.executable)
PY_PREFIX = os.path.realpath(sys.base_prefix)
HOME = os.path.realpath(os.path.expanduser('~'))
DEFAULT_IMAGE = 'python:3.11-slim'
DOCKER = shutil.which('docker') or '/usr/local/bin/docker'
EXECUTORS = ('docker', 'macos-sandbox')
MAX_OUT = 3000          # characters of stdout / stderr shown to the agent
MAX_FILE = 20 * 2**20   # bytes, RLIMIT_FSIZE (macos-sandbox)
SECRET_NAME = re.compile(r'KEY|TOKEN|SECRET', re.I)
BLOCK_SIGNS = ('Operation not permitted', 'PermissionError', 'Network is unreachable', 'Read-only file system')
_EXTRA_SECRETS: set[str] = set()


class PathEscape(ValueError):
    """A read_file / write_file path that points outside the workspace."""


# ── secrets ────────────────────────────────────────────────────────────────────
def env_secret_names(env=None) -> list[str]:
    """Names of environment variables that look like credentials (*KEY*, *TOKEN*, *SECRET*)."""
    env = os.environ if env is None else env
    return sorted(k for k, v in env.items() if SECRET_NAME.search(k) and v)


def register_secret(value: str) -> None:
    if value and len(value) >= 8:
        _EXTRA_SECRETS.add(value)


def secret_values() -> list[str]:
    vals = set(llm.secrets()) | _EXTRA_SECRETS
    vals |= {os.environ[k] for k in env_secret_names() if len(os.environ[k]) >= 8}
    return sorted(vals, key=len, reverse=True)


def redact(text: str) -> str:
    if not isinstance(text, str):
        return text
    for v in secret_values():
        text = text.replace(v, '[REDACTED]')
    return text


def redact_tree(root: Path) -> int:
    """Redact secrets inside every file under root (e.g. the model-answer cache). Returns files changed."""
    vals = secret_values()
    n = 0
    if not vals or not root.exists():
        return 0
    for f in root.rglob('*'):
        if f.is_file():
            t = f.read_text(encoding='utf-8', errors='replace')
            r = redact(t)
            if r != t:
                f.write_text(r, encoding='utf-8')
                n += 1
    return n


# ── workspace helpers ──────────────────────────────────────────────────────────
def safe_path(ws: Path, rel: str) -> Path:
    """Resolve an agent-supplied relative path; refuse anything outside the workspace."""
    if not isinstance(rel, str) or not rel or rel.startswith(('/', '~')) or '\x00' in rel:
        raise PathEscape(f'path must be relative to the workspace: {rel!r}')
    p = (ws / rel).resolve()
    if p != ws and ws not in p.parents:
        raise PathEscape(f'path leaves the workspace: {rel!r}')
    return p


def sha_tree(root: Path) -> dict[str, str]:
    """{relative path: sha256} for every file under root."""
    out = {}
    if root.exists():
        for f in sorted(root.rglob('*')):
            if f.is_file() and not f.is_symlink():
                out[str(f.relative_to(root))] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def new_root(prefix: str = 'hmd019-') -> Path:
    """A fresh temporary root holding one workspace and one canary folder outside it."""
    root = Path(tempfile.mkdtemp(prefix=prefix)).resolve()
    canary = root / 'canary'
    canary.mkdir()
    (canary / 'do-not-touch.txt').write_text('If this file changes, code escaped its workspace.\n')
    (canary / 'notes.csv').write_text('id,value\nkeep,1\n')
    return root


# ── executors ──────────────────────────────────────────────────────────────────
def docker_status(image: str = DEFAULT_IMAGE) -> tuple[bool, str]:
    """(ready, message). Never pulls anything."""
    if not os.path.exists(DOCKER):
        return False, 'Docker is not installed. Install Docker Desktop, start it, then run: docker pull ' + image
    env = {k: v for k, v in os.environ.items() if k not in env_secret_names()}
    try:
        r = subprocess.run([DOCKER, 'info', '--format', '{{.ServerVersion}}'], capture_output=True, text=True,
                           timeout=20, env=env)
    except (OSError, subprocess.TimeoutExpired):
        r = None
    if not r or r.returncode != 0:
        return False, ('The Docker daemon is not running. Start Docker Desktop (macOS: open -a Docker), wait until it '
                       f'says "running", then run once: docker pull {image}   and retry.')
    r = subprocess.run([DOCKER, 'image', 'inspect', image, '--format', '{{.Id}}'], capture_output=True, text=True,
                       timeout=20, env=env)
    if r.returncode != 0:
        return False, f'The image {image} is not on this machine. Run: docker pull {image}   (this code never pulls it), then retry.'
    return True, f'docker {r.stdout.strip()[:19]} ready'


def _profile(ws: str) -> str:
    q = lambda s: s.replace('\\', '\\\\').replace('"', '\\"')
    return f'''(version 1)
(allow default)
(deny network*)
(deny file-write* (subpath "/"))
(allow file-write* (subpath "{q(ws)}") (literal "/dev/null") (literal "/dev/tty") (literal "/dev/dtracehelper"))
(deny file-read* (subpath "{q(HOME)}"))
(allow file-read* (subpath "{q(PY_PREFIX)}") (subpath "{q(os.path.dirname(os.path.dirname(PY)))}") (subpath "{q(ws)}"))
(allow file-read-metadata)
'''


def run_python(ws: Path, rel: str, timeout: float = 30.0, executor: str = 'docker', image: str = DEFAULT_IMAGE) -> dict:
    """Run a script that lives inside the workspace. Returns exit code and trimmed, redacted output."""
    script = safe_path(ws, rel)
    if not script.is_file():
        return {'exit': 2, 'stdout': '', 'stderr': f'no such file in the workspace: {rel}', 'timeout': False, 'blocked': 0}
    wss = str(ws)
    relp = str(script.relative_to(ws))
    name = None
    if executor == 'docker':
        name = 'hmd019-' + pysecrets.token_hex(6)
        cmd = [DOCKER, 'run', '--rm', '--name', name, '--network', 'none', '--memory', '512m', '--cpus', '1',
               '--pids-limit', '128', '--read-only', '--tmpfs', '/tmp', '-v', f'{wss}:/work', '-w', '/work',
               '--user', f'{os.getuid()}:{os.getgid()}', '-e', 'HOME=/tmp', '-e', 'PYTHONDONTWRITEBYTECODE=1',
               image, 'python3', '-I', '/work/' + relp]
        env = {k: v for k, v in os.environ.items() if k not in env_secret_names()}   # the docker CLI only
        pre = None
    elif executor in ('macos-sandbox', 'local'):   # 'local' = trusted mock code in --selftest only
        (ws / 'tmp').mkdir(exist_ok=True)
        cmd = (['sandbox-exec', '-p', _profile(wss)] if executor == 'macos-sandbox' else []) + [PY, '-I', str(script)]
        env = {'PATH': '/usr/bin:/bin', 'HOME': wss, 'TMPDIR': wss + '/tmp', 'LANG': 'en_US.UTF-8',
               'PYTHONHASHSEED': '0', 'PYTHONDONTWRITEBYTECODE': '1', 'MPLBACKEND': 'Agg'}

        def pre():
            os.setsid()
            resource.setrlimit(resource.RLIMIT_CPU, (int(timeout) + 1, int(timeout) + 2))
            resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_FILE, MAX_FILE))
    else:
        raise ValueError(f'unknown executor {executor!r}')

    proc = subprocess.Popen(cmd, cwd=wss, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=pre)
    timed_out = False
    try:
        out, err = proc.communicate(timeout=timeout + (15 if executor == 'docker' else 0))
    except subprocess.TimeoutExpired:
        timed_out = True
        if name:
            subprocess.run([DOCKER, 'kill', name], capture_output=True, timeout=30, env=env)
        try:
            os.killpg(proc.pid, signal.SIGKILL) if pre else proc.kill()
        except ProcessLookupError:
            pass
        out, err = proc.communicate()

    def clean(b: bytes) -> str:
        s = b.decode('utf-8', 'replace').replace(wss + '/', '').replace(wss, '.').replace('/work/', '')
        s = redact(s)
        return s if len(s) <= MAX_OUT else s[:MAX_OUT] + f'\n…[{len(s) - MAX_OUT} more characters cut]'

    err_s = clean(err)
    if timed_out:
        err_s += f'\nKILLED: the script ran longer than {timeout:g} seconds.'
    return {'exit': -9 if timed_out else proc.returncode, 'stdout': clean(out), 'stderr': err_s, 'timeout': timed_out,
            'blocked': sum(any(s in l for s in BLOCK_SIGNS) for l in err_s.splitlines())}


# ── probe ──────────────────────────────────────────────────────────────────────
PROBE = r'''
import ctypes, ctypes.util, glob, os, socket, subprocess, sys
C = CANARY_VALUE
res = {}
try:
    socket.create_connection(("1.1.1.1", 80), timeout=3); res["network"] = "OPEN"
except Exception:
    res["network"] = "blocked"
try:
    open(OUTSIDE_FILE, "a").write("x"); res["write_outside"] = "OPEN"
except Exception:
    res["write_outside"] = "blocked"
try:
    open(REPO_FILE).read(10); res["read_repo"] = "OPEN"
except Exception:
    res["read_repo"] = "blocked"
open("inside.txt", "w").write("ok"); res["write_inside"] = "ok"
found = set()
if C in repr(dict(os.environ)): found.add("own-env")
try:
    if C in subprocess.run(["ps", "eww", "-A"], capture_output=True, text=True, timeout=10).stdout: found.add("ps")
except Exception:
    pass
for p in glob.glob("/proc/*/environ"):
    try:
        if C.encode() in open(p, "rb").read(): found.add("/proc")
    except Exception:
        pass
if sys.platform == "darwin":
    try:
        libc = ctypes.CDLL(ctypes.util.find_library("c"))
        for pid in PIDS:
            mib = (ctypes.c_int * 3)(1, 49, pid)          # CTL_KERN, KERN_PROCARGS2
            size = ctypes.c_size_t(0)
            libc.sysctl(mib, 3, None, ctypes.byref(size), None, 0)
            buf = ctypes.create_string_buffer(max(size.value, 1))
            if libc.sysctl(mib, 3, buf, ctypes.byref(size), None, 0) == 0 and C.encode() in buf.raw[:size.value]:
                found.add("sysctl")
    except Exception:
        pass
res["key_leak"] = ("FOUND via " + "+".join(sorted(found))) if found else "blocked"
print(res)
'''


def probe(executor: str = 'docker', image: str = DEFAULT_IMAGE) -> dict:
    """Prove the executor blocks network, outside writes, repository reads and reading a key
    from another process's environment; and that a runaway script is killed."""
    if executor == 'docker':
        ok, msg = docker_status(image)
        if not ok:
            return {'executor': executor, 'safe': False, 'ready': False, 'message': msg}
    root = new_root('hmd019-probe-')
    ws = root / 'ws'
    ws.mkdir()
    canary_dir = root / 'canary'
    before = sha_tree(canary_dir)
    fake = 'hmd019-canary-' + pysecrets.token_hex(12)
    register_secret(fake)
    # a stand-in for "a shell of yours that exported a key": a process started with the fake key in its env
    helper = subprocess.Popen([PY, '-c', 'import time; time.sleep(60)'],
                              env={'PATH': '/usr/bin:/bin', 'HMD019_PROBE_API_KEY': fake})
    try:
        code = (PROBE.replace('CANARY_VALUE', repr(fake))
                .replace('OUTSIDE_FILE', repr(str(canary_dir / 'do-not-touch.txt')))
                .replace('REPO_FILE', repr(str(Path(__file__).resolve())))
                .replace('PIDS', repr([helper.pid, os.getpid(), os.getppid()])))
        (ws / 'probe.py').write_text(code)
        r = run_python(ws, 'probe.py', timeout=20, executor=executor, image=image)
        (ws / 'loop.py').write_text('while True:\n    pass\n')
        t = run_python(ws, 'loop.py', timeout=3, executor=executor, image=image)
    finally:
        helper.kill()
        helper.wait()
    after = sha_tree(canary_dir)
    shutil.rmtree(root, ignore_errors=True)
    try:
        res = eval(r['stdout'].strip().splitlines()[-1], {})
    except Exception:
        res = {'error': redact(r['stdout'] + r['stderr'])[:300]}
    res['timeout_kill'] = 'ok' if t['timeout'] else 'FAILED'
    res['canary_unchanged'] = before == after
    res['executor'] = executor
    res['ready'] = True
    res['isolation_ok'] = (res.get('network') == 'blocked' and res.get('write_outside') == 'blocked'
                           and res.get('read_repo') == 'blocked' and res.get('write_inside') == 'ok'
                           and res['timeout_kill'] == 'ok' and res['canary_unchanged'])
    res['safe'] = res['isolation_ok'] and res.get('key_leak') == 'blocked'
    return res


if __name__ == '__main__':
    ex = sys.argv[1] if len(sys.argv) > 1 else 'docker'
    print(probe(ex))
