"""HMD-S09 · a hand-written program that solves exactly one ARC task: 007bbfb7 (puzzle 2, "a shape inside itself").

    python3 solve_fractal.py          # checks the rule on all 5 demonstrations and the test pair

The rule a person sees in seconds: make a 3x3 grid of copies; put a copy of the shape wherever the shape itself has a
coloured cell, and leave the block empty where it has a black cell. Written by us, after looking at the task. That is
the point of beat 12: the program is skill (ours, poured in), not the program's own intelligence. It solves this one
task and no other.
"""
import json
from pathlib import Path


def solve(grid):
    n = len(grid)                                   # 3 in every pair of this task
    return [[grid[r % n][c % n] if grid[r // n][c // n] else 0   # cell (r, c) = shape cell, if block (r//n, c//n) is on
             for c in range(n * n)]
            for r in range(n * n)]


if __name__ == '__main__':
    task = json.loads((Path(__file__).resolve().parent / 'data/tasks/007bbfb7.json').read_text(encoding='utf-8'))
    pairs = task['train'] + task['test']
    ok = [solve(p['input']) == p['output'] for p in pairs]
    print(f'007bbfb7: {sum(ok)}/{len(pairs)} pairs exactly right ({len(task["train"])} demonstrations + test)')
    raise SystemExit(0 if all(ok) else 1)
