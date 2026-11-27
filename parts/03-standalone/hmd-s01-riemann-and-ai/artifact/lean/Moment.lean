/-
HMD-S01 · optional "Lean moment" (about 20 seconds on screen). NOT compiled in this repository: nothing was installed.
Before filming, build it once (prep-fa.md, section «Lean»). If a name below has moved in your Mathlib version,
search Mathlib for it (`#find` or the docs site) and fix the name; do not change what the statements say.

What to show:
  1. A fact Lean accepts only with a proof: ζ(2) = π²/6.
  2. A statement Lean can WRITE but nobody can prove: the Riemann hypothesis itself. `sorry` = "proof missing".
     Lean then warns: declaration uses 'sorry'. That warning is the honest state of mathematics in 2026.
  3. Anthropic's repository states its theorem against the SAME `riemannZeta` (see the paper, Appendix A):
     ∀ ε > 0, ∃ T₀, ∀ T ≥ T₀, (2/3 − ε) · N(T, 2T) ≤ N₀*(T, 2T)
-/
import Mathlib

open Complex Real  -- `π` is notation scoped in `Real`

-- 1 · proved: Mathlib's lemma `riemannZeta_two` [VERIFY name in your Mathlib version]
example : riemannZeta 2 = (π : ℂ) ^ 2 / 6 := riemannZeta_two

-- 2 · stated, not proved: Mathlib defines `RiemannHypothesis : Prop` [VERIFY name]
theorem riemann_hypothesis_attempt : RiemannHypothesis := by
  sorry
