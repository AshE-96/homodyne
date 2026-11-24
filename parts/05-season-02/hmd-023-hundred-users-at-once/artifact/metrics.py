"""metrics.py — turn request records into the numbers HMD-023 talks about.

A record is one request: when it was sent, when its first token arrived, when it ended, and how it ended
(ok, timeout, rejected = 503 busy, error). All times are seconds of service time.

Rules that keep the numbers honest:
  * Denominator = every request SENT in the stage. Timeouts and errors stay in it.
  * TTFT/E2E percentiles are over all sent requests; a request that never got a first token counts as
    "infinitely late" (it shows as "> timeout"). Percentiles over successes only would hide the failures.
  * The SLO is a share of requests, not of users: good = first token within the target AND no error.
  * Percentiles use the nearest-rank method; with n < 20 the p95 is basically the maximum (say n aloud).
  * Throughput = successful answers / the stage's real span (stage start to the last answer or hang-up),
    not the 120 s of arrivals: answers keep finishing while the queue drains.
  * A timeout is not "no answer": many timed-out requests already showed a first word. Both are counted.
"""
import math

INF = float('inf')


def pct(values, p):
    """Nearest-rank percentile; values may contain inf."""
    v = sorted(values)
    if not v:
        return None
    rank = max(1, math.ceil(p / 100 * len(v)))
    return v[rank - 1]


def mean(values):
    v = [x for x in values if x is not None and x != INF]
    return sum(v) / len(v) if v else None


def ttft(r):
    return r['t_first'] - r['t_send'] if r.get('t_first') is not None else INF


def e2e(r):
    return r['t_end'] - r['t_send'] if r['status'] == 'ok' else INF


def summarize(recs, duration, slo_ttft=3.0, slo_err=0.01, slots=None, samples=None, timeout=None, window=None):
    """One row per stage. duration = seconds during which new requests could start (rates are per second
    of load). window = stage start to the end of the drain, i.e. every request's whole life; Little's law is
    checked over it: mean number in the system L  vs  arrival rate (n / window) x mean time in the system W."""
    n = len(recs)
    ok = [r for r in recs if r['status'] == 'ok']
    span = window or duration
    by = lambda s: sum(1 for r in recs if r['status'] == s)
    t1 = [ttft(r) for r in recs]
    t2 = [e2e(r) for r in recs]
    good = sum(1 for r in recs if r['status'] == 'ok' and ttft(r) <= slo_ttft)
    row = {
        'sent': n, 'ok': len(ok), 'timeout': by('timeout'), 'rejected': by('rejected'), 'error': by('error'),
        'timeout_after_first_word': sum(1 for r in recs if r['status'] == 'timeout' and r.get('t_first') is not None),
        'no_first_word': sum(1 for r in recs if r.get('t_first') is None),
        'span_s': span,
        'fail_rate': (n - len(ok)) / n if n else None,
        'ttft_p50': pct(t1, 50), 'ttft_p95': pct(t1, 95),
        'e2e_p50': pct(t2, 50), 'e2e_p95': pct(t2, 95),
        'ttft_p95_ok_only': pct([ttft(r) for r in ok], 95),
        'slo_good_share': good / n if n else None,
        'throughput_rps': len(ok) / span if span else None,
        'tokens_per_s': sum(r.get('out_tokens') or 0 for r in ok) / span if span else None,
        'mean_in_tokens': mean([r.get('in_tokens') for r in recs]),
        'mean_out_tokens': mean([r.get('out_tokens') for r in ok]),
        'degraded_share': (sum(1 for r in ok if r.get('degraded')) / len(ok)) if ok else None,
        'offered_rps': n / duration if duration else None,
    }
    row['slo_met'] = (row['slo_good_share'] is not None and row['slo_good_share'] >= 0.95
                      and row['fail_rate'] <= slo_err)
    # Little's law check: L (mean requests in the system, sampled) vs lambda * W (throughput x mean time in system)
    if samples:
        L = mean([s['in_flight'] for s in samples])
        W = mean([r['t_end'] - r['t_send'] for r in recs if r.get('t_end') is not None])
        lam = n / (window or duration) if (window or duration) else None
        row['little_L_measured'] = L
        row['little_lambda_W'] = lam * W if (lam and W) else None
        row['mean_waiting'] = mean([s['waiting'] for s in samples])
        row['max_waiting'] = max(s['waiting'] for s in samples)
        row['max_streaming'] = max(s['streaming'] for s in samples)   # observed concurrency (verifies the slot setting)
    if slots:
        row['slot_s_per_success'] = slots * span / len(ok) if ok else None
    if timeout:
        row['timeout_s'] = timeout
    return row


def fmt_s(x, timeout=None):
    if x is None:
        return '-'
    if x == INF:
        return f'>{timeout:.0f}s' if timeout else 'inf'
    return f'{x:.2f}s'


def capacity_from_open(rows, slo_ttft=3.0):
    """Highest offered rate whose p95 TTFT still met the target (open-loop sweep)."""
    okr = [r for r in rows if r['ttft_p95'] is not None and r['ttft_p95'] <= slo_ttft and r['fail_rate'] <= 0.01]
    return max((r['rate'] for r in okr), default=None)
