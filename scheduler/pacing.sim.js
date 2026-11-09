// Pacing check: drives the app's own scheduler (next/applyReview/newQuota) over the planned pack.
// Assumptions are the spec simulation's: recall 12 s pass / 20 s fail (+6 s first sight),
// scenario 50 s / 75 s (+15 s first sight), 55% pass on first sight, then pass with p = FSRS R.
const F = require('ts-fsrs'), S = require('./scheduler.js');
const MIN = 60000, DAY = 86400000;
const PLAN = { 1: [0.06, 2, 13], 2: [0.21, 7, 46], 3: [0.22, 7, 48], 4: [0.16, 4, 35], 5: [0.10, 4, 22], 6: [0.10, 5, 22], 7: [0.15, 4, 33] };
const SECS = { recall: { pass: 12, fail: 20, first: 6 }, scenario: { pass: 50, fail: 75, first: 15 } };
function mulberry(a) { return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function run(seed, days = 150, budgetMin = 20) {
  const rng = mulberry(seed), s = S.create(F, { fuzz: true, rng });
  const catalog = {}, weights = {}; let order = 0, ids = [];
  for (const [d, [w, nObj, nCon]] of Object.entries(PLAN)) {
    weights[d] = w;
    for (let i = 0; i < nCon; i++) ids.push({ d, obj: `${d}.${(i % nObj) + 1}`, c: `c${d}_${i}` });
  }
  // 153 of 219 concepts also get a scenario track (spec: about 70%)
  const scen = new Set(ids.map(x => x.c).sort(() => rng() - 0.5).slice(0, 153));
  for (const x of ids) {
    order++;
    catalog[x.c + ':r'] = { track: x.c + ':r', concept: x.c, kind: 'recall', domain: x.d, objective: x.obj, order };
    if (scen.has(x.c)) catalog[x.c + ':s'] = { track: x.c + ':s', concept: x.c, kind: 'scenario', domain: x.d, objective: x.obj, order };
  }
  const total = Object.keys(catalog).length, states = {}; let dayLog = {}, daily = [], news = [], leftover = [], introDay = null;
  const start = new Date(2026, 10, 30, 7, 0).getTime();
  for (let d = 0; d < days; d++) {
    let now = start + d * DAY; const key = s.dayKey(now);
    const quota = s.newQuota(dayLog, key, 20);
    const ctx = { catalog, states, weights, usedMs: 0, budgetMs: budgetMin * MIN, quota, lastDomain: null };
    let nNew = 0;
    for (let guard = 0; guard < 2000; guard++) {
      const n = s.next(ctx, now);
      if (n.done) break;
      if (n.wait) { now += n.wait; continue; }
      const m = catalog[n.track], st = states[n.track];
      const p = n.isNew ? 0.55 : s.retrievability(st.fsrs, now);
      const ok = rng() < p;
      const ms = (SECS[m.kind][ok ? 'pass' : 'fail'] + (n.isNew ? SECS[m.kind].first : 0)) * 1000;
      states[n.track] = s.applyReview(st, m, 'v' + Math.floor(rng() * 3), ok, now).state;
      ctx.usedMs += ms; ctx.lastDomain = m.domain; dayLog = s.addDay(dayLog, now, ms); now += ms;
      if (n.isNew) nNew++;
    }
    const left = s.counts(ctx, now).due; leftover.push(left);
    daily.push(ctx.usedMs / MIN); news.push(nNew);
    if (introDay === null && Object.keys(states).length === total) introDay = d + 1;
  }
  const mean = a => a.reduce((x, y) => x + y, 0) / a.length;
  const weeks = []; for (let i = 0; i + 7 <= introDay; i += 7) weeks.push(mean(daily.slice(i, i + 7)));
  return { introDay, meanIntro: mean(daily.slice(0, introDay)), peakWeek: Math.max(...weeks), after: mean(daily.slice(introDay, introDay + 28)), newPerDay: mean(news.slice(0, introDay)), maxDay: Math.max(...daily.slice(0, introDay)), total, leftDays: leftover.slice(0, introDay + 28).filter(x => x > 0).length, leftMean: mean(leftover.slice(0, introDay + 28).filter(x => x > 0)) };
}

for (const [label, b] of [['20-minute cap (spec rule)', 20], ['no cap (original sim)', 1e9]]) {
  const res = []; for (let seed = 1; seed <= 8; seed++) res.push(run(seed, 150, b));
  const m = k => res.reduce((a, r) => a + r[k], 0) / res.length;
  console.log(`${label}: intro weeks ${Math.min(...res.map(r => r.introDay / 7)).toFixed(1)}–${Math.max(...res.map(r => r.introDay / 7)).toFixed(1)} | new/day ${m('newPerDay').toFixed(1)} | mean ${m('meanIntro').toFixed(1)} min | peak week ${Math.max(...res.map(r => r.peakWeek)).toFixed(1)} | after ${m('after').toFixed(1)} min | days ending with reviews undone ${m('leftDays').toFixed(1)} of ~${Math.round(m('introDay')+28)} (avg ${(m('leftMean')||0).toFixed(1)} cards left)`);
}
