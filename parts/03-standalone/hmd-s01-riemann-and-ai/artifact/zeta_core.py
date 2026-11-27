"""zeta_core.py · HMD-S01 · the mathematics behind the live demo, standard library only.

    zeta(s)        Riemann zeta by Euler–Maclaurin summation (any s != 1, |Im s| up to a few thousand)
    theta(t)       Riemann–Siegel theta, Im log Gamma(1/4 + it/2) - (t/2) log pi
    hardy_z(t)     Hardy's Z(t) = e^{i theta(t)} zeta(1/2 + it), real for real t
    zeros(k)       the first k nontrivial zeros 1/2 + i gamma (sign changes of Z, refined by bisection)
    n_smooth(T)    Riemann–von Mangoldt main term theta(T)/pi + 1
    psi(x)         Chebyshev psi: sum of log p over prime powers p^m <= x (the weighted prime staircase)
    psi_explicit   the explicit formula: x - sum_rho x^rho/rho - log(2 pi) - 1/2 log(1 - x^-2), first k zeros

Nothing here assumes the Riemann hypothesis: zeros() only finds zeros ON the critical line (sign changes of Z).
That every zero up to the height we use is on the line is a published numerical fact (Platt–Trudgian 2021),
and the selftest checks our count against the Riemann–von Mangoldt formula.
"""
import cmath
import math
from fractions import Fraction

# B_2, B_4, ..., B_24 (Bernoulli numbers)
_B = [Fraction(1, 6), Fraction(-1, 30), Fraction(1, 42), Fraction(-1, 30), Fraction(5, 66), Fraction(-691, 2730),
      Fraction(7, 6), Fraction(-3617, 510), Fraction(43867, 798), Fraction(-174611, 330), Fraction(854513, 138),
      Fraction(-236364091, 2730)]
_EM = [float(b / math.factorial(2 * k + 2)) for k, b in enumerate(_B)]   # B_2k / (2k)!


def zeta(s, terms=12):
    """Riemann zeta via Euler–Maclaurin. Accurate to ~1e-10 for |Im s| < 5000 and Re s in [-1, 3]."""
    s = complex(s)
    if s == 1:
        raise ZeroDivisionError('zeta has a pole at s = 1')
    n = int(abs(s.imag) / 2) + 20   # 2*pi*n ~ 3 t, so each correction term is ~10x smaller than the last
    total = sum(k ** -s for k in range(1, n))
    total += n ** (1 - s) / (s - 1) + 0.5 * n ** -s
    rising = s                      # s (s+1) ... (s+2k-2)
    npow = n ** (-s - 1)            # n^{-s-2k+1}
    for k in range(terms):
        total += _EM[k] * rising * npow
        rising *= (s + 2 * k + 1) * (s + 2 * k + 2)
        npow /= n * n
    return total


def loggamma(z):
    """Complex log Gamma with a continuous imaginary part for Re z > 0 (shift + Stirling)."""
    z = complex(z)
    shift = 0j
    while z.real < 10:
        shift += cmath.log(z)
        z += 1
    zi = 1 / z
    z2 = zi * zi
    series = zi * (1 / 12 + z2 * (-1 / 360 + z2 * (1 / 1260 + z2 * (-1 / 1680 + z2 / 1188))))
    return (z - 0.5) * cmath.log(z) - z + 0.5 * math.log(2 * math.pi) + series - shift


def theta(t):
    """Riemann–Siegel theta function."""
    return loggamma(0.25 + 0.5j * t).imag - 0.5 * t * math.log(math.pi)


def hardy_z(t):
    """Hardy's Z function: real, |Z(t)| = |zeta(1/2+it)|, sign changes = zeros on the critical line."""
    return (cmath.exp(1j * theta(t)) * zeta(0.5 + 1j * t)).real


def _bisect(f, a, b, fa, tol=1e-11):
    for _ in range(80):
        m = 0.5 * (a + b)
        fm = f(m)
        if fa * fm <= 0:
            b = m
        else:
            a, fa = m, fm
        if b - a < tol:
            break
    return 0.5 * (a + b)


def zeros(count=None, t_max=None, step=0.05):
    """Ordinates gamma of zeros 1/2 + i gamma found as sign changes of Z(t), in increasing order."""
    out, t, zt = [], 1.0, hardy_z(1.0)
    while (count is None or len(out) < count) and (t_max is None or t < t_max):
        t2 = t + step
        z2 = hardy_z(t2)
        if zt * z2 < 0:
            out.append(_bisect(hardy_z, t, t2, zt))
        t, zt = t2, z2
    return out


def n_smooth(T):
    """Riemann–von Mangoldt: N(T) = theta(T)/pi + 1 + S(T); this is the smooth part without S(T)."""
    return theta(T) / math.pi + 1


def n_asymptotic(T):
    """The textbook form (T/2pi) log(T/2pi e) + 7/8, valid for large T."""
    return T / (2 * math.pi) * math.log(T / (2 * math.pi * math.e)) + 7 / 8


def primes_upto(n):
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b'\x00\x00'
    for p in range(2, int(n ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = bytearray(len(sieve[p * p::p]))
    return [i for i in range(n + 1) if sieve[i]]


def prime_pi(x):
    return len(primes_upto(int(x)))


def psi(x):
    """Chebyshev psi(x) = sum over prime powers p^m <= x of log p."""
    total = 0.0
    for p in primes_upto(int(x)):
        pm = p
        while pm <= x:
            total += math.log(p)
            pm *= p
    return total


def psi_explicit(x, gammas):
    """von Mangoldt's explicit formula truncated to the zeros given (each paired with its conjugate)."""
    lx = math.log(x)
    wave = 0.0
    for g in gammas:
        rho = complex(0.5, g)
        wave += 2 * (cmath.exp(rho * lx) / rho).real
    return x - wave - math.log(2 * math.pi) - 0.5 * math.log(1 - x ** -2)
