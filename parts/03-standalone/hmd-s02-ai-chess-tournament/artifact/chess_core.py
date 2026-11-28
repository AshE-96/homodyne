"""HMD-S02 · shared core: the locked prompt, reply parsing, illegal-move diagnosis, opening book, engine metrics.

Everything that defines the experiment lives here, so `chess_run.py` can fingerprint it (sha256) before a paid run.
Rules of chess: python-chess (GPL-3.0; `pip3 install --user chess`). Engine: Stockfish, optional
(`brew install stockfish`, or STOCKFISH=/path/to/stockfish); without it every eval/centipawn field is None.
Model calls: tools/llm.py. Metrics follow Lichess's published code (lichess-org/lila, lichess-org/scalachess):
    win%      = 50 + 50 · (2 / (1 + exp(−0.00368208 · cp)) − 1),  cp clipped to ±1000 (mate = ±1000)
    accuracy  = 103.1668 · exp(−0.04354 · (win%_before − win%_after)) − 3.1669 + 1, clipped to 0…100
    judgement = drop in winning chances (−1…+1 scale) ≥ 0.3 blunder · ≥ 0.2 mistake · ≥ 0.1 inaccuracy
"""
import hashlib
import json
import math
import random
import re
import shutil
import os
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
if str(ROOT / 'tools') not in sys.path:
    sys.path.insert(0, str(ROOT / 'tools'))

try:
    import chess
    import chess.engine
    import chess.pgn
except ImportError:  # pragma: no cover
    sys.exit('python-chess is missing: pip3 install --user chess   (prep-fa.md §2)')

DATA = HERE / 'data'                 # git-ignored (parts/*/*/artifact/data/): runs, per-game answer caches
RESULTS = HERE / 'results'           # committed: aggregates, PGN, events for replay
OPENINGS = HERE / 'derived' / 'openings.tsv'
MAX_TOKENS = 16000
CP_CEIL = 1000

SYSTEM = ('You are playing a game of chess. Each turn you get the current position as FEN and the full move history '
          'in standard algebraic notation (SAN). Choose one legal move for the side to move. You have no tools, no '
          'engine and no list of legal moves. Reply with JSON only: {"move": "<your move in SAN, e.g. Nf3, exd5, '
          'O-O, e8=Q>"}. UCI such as g1f3 is also accepted.')
SCHEMA = {'type': 'object', 'properties': {'move': {'type': 'string'}}, 'required': ['move'],
          'additionalProperties': False}
RETRY_NOTE = ('Your previous reply "{text}" was not a legal move in this position. This is your last chance: a '
              'second illegal move loses the game. Reply with JSON only.')

KINDS = {   # illegal-move diagnosis → what it suggests (study-fa.md §5)
    'no_answer': 'no move found in the reply',
    'bad_notation': 'not chess notation (e.g. e9, "knight to f3")',
    'ghost_piece': 'names a piece the side no longer has, or an empty/enemy square: board state lost',
    'unreachable': 'the piece exists but cannot reach that square: geometry or blocked path',
    'leaves_king_in_check': 'would be legal if not for check or a pin: ignores the king',
    'castling_illegal': 'castling not allowed here (rights lost, pieces in between, or through check)',
    'ambiguous': 'SAN fits two pieces and does not say which',
}
SAN_RE = re.compile(r'^([NBRQK])?([a-h])?([1-8])?(x)?([a-h][1-8])(=?[NBRQ])?$')
UCI_RE = re.compile(r'^[a-h][1-8][a-h][1-8][qrbn]?$')


# ── prompt ───────────────────────────────────────────────────────────────────────────────────────
def history_text(sans):
    if not sans:
        return '(none: this is the first move of the game)'
    out = []
    for i, s in enumerate(sans):
        out.append((f'{i // 2 + 1}. ' if i % 2 == 0 else '') + s)
    return ' '.join(out)


def prompt_for(board, sans, gid, retry_text=None):
    side = 'White' if board.turn == chess.WHITE else 'Black'
    p = (f'Game {gid} of a round-robin. You play {side}.\n'
         f'Position (FEN): {board.fen()}\n'
         f'Moves so far: {history_text(sans)}\n'
         f'It is your move as {side} (move {board.fullmove_number}).')
    if retry_text is not None:
        p += '\n' + RETRY_NOTE.format(text=retry_text[:60].replace('"', "'"))
    return p


# ── parsing and diagnosis ────────────────────────────────────────────────────────────────────────
def extract_move(text):
    """The move string a reply proposes, or None. JSON first, then the first notation-like token."""
    t = (text or '').strip()
    t = re.sub(r'^```(?:json)?\s*|\s*```$', '', t)
    try:
        d = json.loads(t)
        if isinstance(d, dict) and isinstance(d.get('move'), str):
            return d['move'].strip() or None
    except ValueError:
        pass
    m = re.search(r'"move"\s*:\s*"([^"]*)"', t)
    if m:
        return m.group(1).strip() or None
    for tok in re.split(r'[\s,;]+', t):
        if SAN_RE.match(normalise(tok) or '') or UCI_RE.match((normalise(tok) or '').lower()) or \
                normalise(tok) in ('O-O', 'O-O-O'):
            return tok
    return t if 0 < len(t) <= 12 else None


def normalise(s):
    if s is None:
        return None
    s = s.strip().replace('×', 'x').replace('0-0-0', 'O-O-O').replace('0-0', 'O-O').replace(' ', '')
    s = re.sub(r'^\d+\.+', '', s)            # "12." / "12..." move numbers
    s = re.sub(r'[+#!?.]+$', '', s)          # check, mate, annotation marks, a trailing full stop
    s = re.sub(r'(e\.p|ep)$', '', s)          # en passant suffix (its last dot already removed)
    return re.sub(r'[+#!?.]+$', '', s)


def judge(board, text):
    """→ (move or None, info). info = {proposed, notation 'san'|'uci', kind (if illegal)}."""
    raw = extract_move(text)
    info = {'proposed': raw}
    s = normalise(raw)
    if not s:
        return None, dict(info, kind='no_answer')
    if s in ('O-O', 'O-O-O'):
        try:
            return board.parse_san(s), dict(info, notation='san')
        except ValueError:
            return None, dict(info, kind='castling_illegal')
    if UCI_RE.match(s):                      # lower-case from-to squares: UCI (a pawn SAN never has both)
        mv = chess.Move.from_uci(s)
        if mv in board.legal_moves:
            return mv, dict(info, notation='uci')
        if board.is_castling(mv) or (board.piece_type_at(mv.from_square) == chess.KING
                                     and abs(chess.square_file(mv.from_square) - chess.square_file(mv.to_square)) == 2):
            return None, dict(info, kind='castling_illegal')
        pc = board.piece_at(mv.from_square)
        if pc is None or pc.color != board.turn:
            return None, dict(info, kind='ghost_piece')
        if mv in board.pseudo_legal_moves:
            return None, dict(info, kind='leaves_king_in_check')
        return None, dict(info, kind='unreachable')
    m = SAN_RE.match(s)
    if not m:
        return None, dict(info, kind='bad_notation')
    try:
        return board.parse_san(s), dict(info, notation='san')
    except chess.AmbiguousMoveError:
        return None, dict(info, kind='ambiguous')
    except ValueError:
        pass
    piece = 'PNBRQK'.index(m.group(1)) + 1 if m.group(1) else chess.PAWN
    to = chess.parse_square(m.group(5))
    ff = 'abcdefgh'.index(m.group(2)) if m.group(2) else None
    fr = int(m.group(3)) - 1 if m.group(3) else None
    if not board.pieces(piece, board.turn):
        return None, dict(info, kind='ghost_piece')
    if piece == chess.PAWN and not m.group(6) and chess.square_rank(to) in (0, 7):
        return None, dict(info, kind='bad_notation')     # pawn reaches the last rank without naming a promotion
    cands = [mv for mv in board.pseudo_legal_moves if mv.to_square == to and board.piece_type_at(mv.from_square) == piece
             and (ff is None or chess.square_file(mv.from_square) == ff)
             and (fr is None or chess.square_rank(mv.from_square) == fr)]
    if cands and not any(board.is_legal(c) for c in cands):
        return None, dict(info, kind='leaves_king_in_check')
    return None, dict(info, kind='unreachable')


# ── opening book (lichess-org/chess-openings, CC0) ───────────────────────────────────────────────
_BOOK = None


def book():
    """→ (positions: set of EPD reached by any named line, names: {EPD: (eco, name)})."""
    global _BOOK
    if _BOOK is not None:
        return _BOOK
    raw = OPENINGS.read_bytes()
    cache = DATA / 'cache' / f'book-{hashlib.sha256(raw).hexdigest()[:12]}.json'
    if cache.exists():
        d = json.loads(cache.read_text(encoding='utf-8'))
        _BOOK = (set(d['pos']), {k: tuple(v) for k, v in d['names'].items()})
        return _BOOK
    if True:
        pos, names = set(), {}
        for line in OPENINGS.read_text(encoding='utf-8').splitlines()[1:]:
            eco, name, pgn = line.split('\t')
            b = chess.Board()
            for tok in pgn.split():
                if tok[0].isdigit():
                    continue
                b.push_san(tok)
                pos.add(b.epd())
            names[b.epd()] = (eco, name)
        _BOOK = (pos, names)
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps({'pos': sorted(pos), 'names': names}), encoding='utf-8')
        except OSError:
            pass
    return _BOOK


def book_info(board):
    pos, names = book()
    epd = board.epd()
    return epd in pos, names.get(epd)


# ── metrics ──────────────────────────────────────────────────────────────────────────────────────
def clip_cp(cp):
    return max(-CP_CEIL, min(CP_CEIL, cp))


def winning_chances(cp):
    return 2 / (1 + math.exp(-0.00368208 * clip_cp(cp))) - 1


def win_pct(cp):
    return 50 + 50 * winning_chances(cp)


def accuracy(cp_before, cp_after):
    """Lichess move accuracy from the mover's point of view (both evals in mover POV centipawns)."""
    wb, wa = win_pct(cp_before), win_pct(cp_after)
    if wa >= wb:
        return 100.0
    raw = 103.1668100711649 * math.exp(-0.04354415386753951 * (wb - wa)) - 3.166924740191411 + 1
    return max(0.0, min(100.0, raw))


def judgement(cp_before, cp_after):
    d = winning_chances(cp_before) - winning_chances(cp_after)
    return 'blunder' if d >= 0.3 else 'mistake' if d >= 0.2 else 'inaccuracy' if d >= 0.1 else None


def expected_score(ra, rb):
    """Elo: expected score of A against B."""
    return 1 / (1 + 10 ** ((rb - ra) / 400))


# ── engine (optional) ────────────────────────────────────────────────────────────────────────────
def find_stockfish():
    p = os.environ.get('STOCKFISH') or shutil.which('stockfish')
    for c in ([p] if p else []) + ['/opt/homebrew/bin/stockfish', '/usr/local/bin/stockfish', '/usr/games/stockfish']:
        if c and Path(c).exists():
            return c
    return None


class Engine:
    """Stockfish at a fixed depth, serialised by a lock (games run in threads). eval() → White-POV cp, mate."""

    def __init__(self, path, depth=12):
        self.path, self.depth, self.lock = path, depth, threading.Lock()
        self.eng = chess.engine.SimpleEngine.popen_uci(path)
        self.name = self.eng.id.get('name', 'Stockfish')

    def eval(self, board):
        with self.lock:
            info = self.eng.analyse(board, chess.engine.Limit(depth=self.depth))
        sc = info['score'].white()
        mate = sc.mate()
        cp = sc.score(mate_score=100000)
        return clip_cp(cp), mate

    def close(self):
        try:
            self.eng.quit()
        except Exception:   # engine already gone
            pass


def open_engine(depth=12, want=True):
    if not want:
        return None, 'engine off (--no-engine)'
    p = find_stockfish()
    if not p:
        return None, 'Stockfish not installed: no eval, no centipawn loss (brew install stockfish; prep-fa.md §2)'
    e = Engine(p, depth)
    return e, f'{e.name} · depth {depth}'


# ── MOCK players (no key, no network) ────────────────────────────────────────────────────────────
VALUE = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
MOCK_STYLE = {   # p_illegal in book, ×factor after move 8, p_illegal on retry, skill, sec/move, tokens out, chars/token
    'gemini': (0.01, 4, 0.15, 0.75, 9.0, 2600, 3.6), 'claude': (0.02, 4, 0.20, 0.70, 6.0, 1500, 3.8),
    'gpt': (0.01, 3, 0.15, 0.80, 11.0, 3400, 3.7), 'open1': (0.04, 4, 0.35, 0.45, 4.0, 900, 3.5),
    'open2': (0.05, 5, 0.40, 0.35, 3.0, 700, 3.4), 'always_illegal': (1.0, 1, 1.0, 0.0, 1.0, 10, 4.0)}


def _mock_illegal(board, rng):
    """One plausible illegal reply, of a random kind."""
    opts = []
    have = {p for p in range(1, 7) if board.pieces(p, board.turn)}
    gone = [p for p in (chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT) if p not in have]
    if gone:
        opts.append('%s%s' % ('PNBRQK'[gone[0] - 1], chess.square_name(rng.choice(list(chess.SQUARES)))))
    pseudo = [m for m in board.pseudo_legal_moves if not board.is_legal(m)]
    if pseudo:
        opts.append(rng.choice(pseudo).uci())
    opts.append(rng.choice(['Nf9', 'e9', 'Ke0']))
    empties = [s for s in chess.SQUARES if board.piece_at(s) is None]
    a, b = rng.sample(empties, 2) if len(empties) > 1 else (0, 1)
    opts.append(chess.square_name(a) + chess.square_name(b))
    return rng.choice(opts)


def _mock_pick(board, rng, skill):
    moves = list(board.legal_moves)
    if rng.random() > skill:
        return rng.choice(moves)

    def score(m):
        s = 0.0
        cap = board.piece_at(m.to_square)
        if cap:
            s += VALUE[cap.piece_type] * 10 - VALUE[board.piece_type_at(m.from_square)]
        if m.promotion:
            s += 80
        board.push(m)
        if board.is_checkmate():
            s += 1000
        elif board.is_check():
            s += 2
        if board.is_attacked_by(board.turn, m.to_square) and not board.is_attacked_by(not board.turn, m.to_square):
            s -= VALUE[board.piece_type_at(m.to_square)] * 8
        board.pop()
        return s + rng.random()
    return max(moves, key=score)


def mock_reply(slot, prompt, gid=''):
    """A MOCK player's reply text. Deterministic per (slot, game, position, attempt). Labelled MOCK everywhere."""
    style = MOCK_STYLE.get(slot, MOCK_STYLE['open1'])
    fen = re.search(r'Position \(FEN\): (.+)', prompt).group(1).strip()
    retry = 'previous reply' in prompt
    rng = random.Random(hashlib.sha256(f'{slot}|{gid}|{fen}|{retry}'.encode()).hexdigest())
    board = chess.Board(fen)
    p = style[2] if retry else style[0] * (style[1] if board.fullmove_number > 8 else 1)
    if rng.random() < p:
        mv = _mock_illegal(board, rng)
    else:
        m = _mock_pick(board, rng, style[3])
        mv = m.uci() if rng.random() < 0.1 else board.san(m)
    return json.dumps({'move': mv})


def mock_cost(slot, prompt):
    """Simulated latency (s), input and output tokens for a MOCK call."""
    st = MOCK_STYLE.get(slot, MOCK_STYLE['open1'])
    r = random.Random(prompt)
    return (round(st[4] * (0.5 + r.random()), 2), int((len(SYSTEM) + len(prompt)) / st[6]),
            int(st[5] * (0.5 + r.random())))
