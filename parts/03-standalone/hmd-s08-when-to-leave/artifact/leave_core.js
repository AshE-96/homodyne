// leave_core.js · HMD-S08 · the same arithmetic as leave_core.py, for the live page (inlined by leave_live.py).
// --selftest runs selfCheck() in node and compares it with Python.
function quantile(xs, q) {               // xs sorted; linear interpolation (type 7)
  const n = xs.length; if (!n) return null;
  const h = (n - 1) * q, lo = Math.floor(h), hi = Math.min(lo + 1, n - 1);
  return xs[lo] + (h - lo) * (xs[hi] - xs[lo]);
}
function mean(xs) { let s = 0; for (const x of xs) s += x; return xs.length ? s / xs.length : null; }
function makeIndex(trips) {              // trips: [[dayIdx, dep, min]] -> minute buckets
  const by = Array.from({ length: 1440 }, () => []);
  for (const t of trips) by[t[1]].push(t[2]);
  return by;
}
function sample(by, t, half) {
  const xs = [];
  for (let d = t - half; d <= t + half; d++) if (d >= 0 && d < 1440) for (const m of by[d]) xs.push(m);
  return xs.sort((a, b) => a - b);
}
function leaveBy(by, D, conf, P) {       // latest grid t with t + Q_conf(t) <= D; conf = 'mean' for the mean rule
  let t = D - (D % P.step);
  for (; t >= D - P.horizon; t -= P.step) {
    const xs = sample(by, t, P.half);
    if (xs.length < P.min_n) continue;
    const v = conf === 'mean' ? mean(xs) : quantile(xs, conf);
    if (t + v <= D) return t;
  }
  return null;
}
function backtest(test, t, D, half) {    // test: [[dayIdx, dep, min]] on held-out days
  const per = new Map();
  for (const x of test) if (Math.abs(x[1] - t) <= half) {
    const v = per.get(x[0]) || [0, 0]; v[0]++; v[1] += (t + x[2] > D) ? 1 : 0; per.set(x[0], v);
  }
  let n = 0, late = 0; for (const v of per.values()) { n += v[0]; late += v[1]; }
  return { trips: n, late, share: n ? late / n : null, per };
}
function splitRoute(D, code) {
  const s = D.days.indexOf(D.days.find(d => d >= D.split));
  const tr = [], te = [];
  for (const x of D.routes[code].trips) (x[0] < s ? tr : te).push(x);
  return { tr, te, splitIdx: s };
}
function selfCheck(D) {
  const c = D.check, P = D, sp = splitRoute(D, c.route), by = makeIndex(sp.tr);
  const l95 = leaveBy(by, c.deadline, 0.95, P), lm = leaveBy(by, c.deadline, 'mean', P);
  const late = backtest(sp.te, l95, c.deadline, D.bt_half).late;
  return { ok: l95 === c.leave95 && lm === c.leave_mean && late === c.late95, l95, lm, late, want: c };
}
if (typeof module !== 'undefined') module.exports = { quantile, mean, makeIndex, sample, leaveBy, backtest, splitRoute, selfCheck };
