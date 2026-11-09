const assert = require('assert'), F = require('ts-fsrs'), S = require('./scheduler.js');
let seed = 7; const rng = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const s = S.create(F, { fuzz: false, rng });
const T0 = new Date(2026, 10, 16, 7, 0).getTime(), MIN = 60000, DAY = 86400000;
let pass = 0; const t = (name, fn) => { fn(); pass++; console.log('ok -', name); };

t('first-sight pass graduates at once; fail returns after 10 minutes', () => {
  const p = s.grade(null, true, T0), f = s.grade(null, false, T0);
  assert.equal(p.fsrs.state, F.State.Review);
  assert.equal(f.fsrs.state, F.State.Learning);
  assert.equal(f.fsrs.due - T0, 10 * MIN);
  const r = s.grade(p.fsrs, false, T0 + 3 * DAY);
  assert.equal(r.fsrs.state, F.State.Relearning); assert.equal(r.fsrs.due - (T0 + 3 * DAY), 10 * MIN);
});
t('variants: never the same twice running, least recently seen first', () => {
  const ids = ['v1', 'v2', 'v3']; let st = { seen: {}, lastVariant: null }, prev = null;
  const order = [];
  for (let i = 0; i < 30; i++) {
    const v = s.pickVariant(st, ids); assert.notEqual(v, prev); order.push(v);
    st = { seen: Object.assign({}, st.seen, { [v]: T0 + i }), lastVariant: v }; prev = v;
  }
  // after the first three, rotation is strict round-robin
  for (let i = 3; i < 30; i++) assert.equal(order[i], order[i - 3]);
  assert.equal(s.pickVariant({ seen: { only: 1 }, lastVariant: 'only' }, ['only']), 'only');
});
t('options: 4 shown, correct count kept, reshuffled, scoring incl. pick-two', () => {
  const v1 = { pick: 1, correct: [{ text: 'A' }], distractors: ['B', 'C', 'D', 'E', 'F'].map(x => ({ text: x })) };
  const v2 = { pick: 2, correct: [{ text: 'A' }, { text: 'B' }], distractors: ['C', 'D', 'E', 'F'].map(x => ({ text: x })) };
  const firsts = new Set(), drawn = new Set();
  for (let i = 0; i < 200; i++) {
    const o = s.buildOptions(v1); assert.equal(o.length, 4); assert.equal(o.filter(x => x.ok).length, 1);
    firsts.add(o.findIndex(x => x.ok)); o.forEach(x => drawn.add(x.text));
    const q = s.buildOptions(v2); assert.equal(q.length, 4); assert.equal(q.filter(x => x.ok).length, 2);
    const okIdx = q.map((x, j) => x.ok ? j : -1).filter(j => j >= 0), badIdx = q.map((x, j) => x.ok ? -1 : j).filter(j => j >= 0);
    assert(s.scoreOptions(q, okIdx)); assert(!s.scoreOptions(q, [okIdx[0], badIdx[0]])); assert(!s.scoreOptions(q, [okIdx[0]]));
  }
  assert.equal(firsts.size, 4, 'correct answer appears in every position'); assert.equal(drawn.size, 6, 'whole distractor pool used');
});
const cat = {
  'a:r': { track: 'a:r', concept: 'a', kind: 'recall', domain: '2', objective: '2.1', order: 1 },
  'a:s': { track: 'a:s', concept: 'a', kind: 'scenario', domain: '2', objective: '2.1', order: 1 },
  'b:r': { track: 'b:r', concept: 'b', kind: 'recall', domain: '1', objective: '1.1', order: 2 },
  'c:r': { track: 'c:r', concept: 'c', kind: 'recall', domain: '3', objective: '3.1', order: 3 },
  'c:s': { track: 'c:s', concept: 'c', kind: 'scenario', domain: '3', objective: '3.1', order: 3 },
};
const W = { 1: 0.06, 2: 0.21, 3: 0.22 };
t('new tracks: highest weight x coverage gap first; sibling waits until tomorrow', () => {
  const ctx = { catalog: cat, states: {}, weights: W, usedMs: 0, budgetMs: 20 * MIN, quota: 9 };
  const now = T0, seq = [];
  for (let i = 0; i < 6; i++) {
    const n = s.next(ctx, now); if (!n.track) { seq.push(n.done || 'wait'); break; }
    seq.push(n.track); ctx.states[n.track] = s.applyReview(ctx.states[n.track], cat[n.track], 'v1', true, now).state;
  }
  assert.deepEqual(seq, ['c:r', 'a:r', 'b:r', 'empty']);   // c (22%) then a (21%) then b (6%); no scenario sibling today
  const tomorrow = T0 + DAY, n = s.next(ctx, tomorrow);
  assert.equal(n.isNew, true); assert.equal(n.track, 'c:s');
});
t('due first, lowest retrievability first; budget ends the session; quota caps new', () => {
  const ctx = { catalog: cat, states: {}, weights: W, usedMs: 0, budgetMs: 20 * MIN, quota: 1 };
  ctx.states['b:r'] = s.applyReview(null, cat['b:r'], 'v1', true, T0 - 10 * DAY).state;
  ctx.states['c:r'] = s.applyReview(null, cat['c:r'], 'v1', true, T0 - 3 * DAY).state;
  const a = s.next(ctx, T0); assert.equal(a.track, 'b:r');            // more overdue = lower R
  ctx.states['b:r'] = s.applyReview(ctx.states['b:r'], cat['b:r'], 'v2', true, T0).state;
  assert.equal(s.next(ctx, T0).track, 'c:r');
  ctx.states['c:r'] = s.applyReview(ctx.states['c:r'], cat['c:r'], 'v2', true, T0).state;
  const nw = s.next(ctx, T0); assert.equal(nw.isNew, true); assert.equal(nw.track, 'a:r');
  ctx.states['a:r'] = s.applyReview(null, cat['a:r'], 'v1', true, T0).state;
  assert.equal(s.next(ctx, T0).done, 'empty');                        // quota of 1 used; c:s blocked by sibling
  ctx.usedMs = 20 * MIN; assert.equal(s.next(ctx, T0).done, 'budget');
});
t('learn-ahead: a missed card returns at once when nothing else is left, with a different variant', () => {
  const ctx = { catalog: cat, states: {}, weights: W, usedMs: 0, budgetMs: 20 * MIN, quota: 0 };
  ctx.states['b:r'] = s.applyReview(null, cat['b:r'], 'v1', false, T0).state;
  const n = s.next(ctx, T0 + MIN); assert.equal(n.track, 'b:r'); assert.equal(n.early, true);
  assert.notEqual(s.pickVariant(ctx.states['b:r'], ['v1', 'v2', 'v3']), 'v1');
});
t('learn-ahead: due reviews and new cards still come before a missed card', () => {
  const ctx = { catalog: cat, states: {}, weights: W, usedMs: 0, budgetMs: 20 * MIN, quota: 2 };   // b:r was new today too
  ctx.states['b:r'] = s.applyReview(null, cat['b:r'], 'v1', false, T0).state;            // missed, back at T0+10m
  ctx.states['c:r'] = s.applyReview(null, cat['c:r'], 'v1', true, T0 - 3 * DAY).state;   // due review
  assert.equal(s.next(ctx, T0 + MIN).track, 'c:r');
  ctx.states['c:r'] = s.applyReview(ctx.states['c:r'], cat['c:r'], 'v2', true, T0 + MIN).state;
  const nw = s.next(ctx, T0 + 2 * MIN); assert.equal(nw.isNew, true); assert.equal(nw.track, 'a:r');
  ctx.states['a:r'] = s.applyReview(null, cat['a:r'], 'v1', true, T0 + 2 * MIN).state;
  const back = s.next(ctx, T0 + 3 * MIN); assert.equal(back.track, 'b:r'); assert.equal(back.early, true);
  ctx.states['b:r'] = s.applyReview(ctx.states['b:r'], cat['b:r'], 'v2', true, T0 + 3 * MIN).state;
  assert.equal(s.next(ctx, T0 + 4 * MIN).done, 'empty');
});
t('learn-ahead: only within 20 minutes, and never past the budget', () => {
  const ctx = { catalog: cat, states: {}, weights: W, usedMs: 0, budgetMs: 20 * MIN, quota: 0 };
  const st = s.applyReview(null, cat['b:r'], 'v1', false, T0).state;
  st.fsrs = Object.assign({}, st.fsrs, { due: T0 + 25 * MIN });                        // a step longer than the look-ahead
  ctx.states['b:r'] = st;
  assert.equal(s.next(ctx, T0).wait, 25 * MIN);
  assert.equal(s.next(ctx, T0 + 6 * MIN).track, 'b:r');
  ctx.usedMs = 20 * MIN; assert.equal(s.next(ctx, T0 + 6 * MIN).done, 'budget');
});
t('throttle: thresholds of the spec simulation, over days studied in the last 7', () => {
  const k = '2026-11-20', d = m => ({ ms: m * MIN, n: 1 });
  assert.equal(s.newQuota({}, k, 20), 9);
  assert.equal(s.newQuota({ '2026-11-19': d(15.9) }, k, 20), 9);
  assert.equal(s.newQuota({ '2026-11-19': d(18) }, k, 20), 7);
  assert.equal(s.newQuota({ '2026-11-19': d(20) }, k, 20), 5);
  assert.equal(s.newQuota({ '2026-11-19': d(22) }, k, 20), 2);
  assert.equal(s.newQuota({ '2026-11-12': d(30), '2026-11-19': d(15) }, k, 20), 9, 'day 8 back is outside the window');
  assert.equal(s.newQuota({ '2026-11-20': d(40), '2026-11-19': d(15) }, k, 20), 9, 'today does not count');
});
t('study day rolls over at 04:00 local', () => {
  assert.equal(s.dayKey(new Date(2026, 10, 17, 3, 59).getTime()), '2026-11-16');
  assert.equal(s.dayKey(new Date(2026, 10, 17, 4, 0).getTime()), '2026-11-17');
});
t('measured time is capped at 3 minutes per card', () => { assert.equal(s.measured(10 * MIN), 3 * MIN); assert.equal(s.measured(-5), 0); });
console.log(`\n${pass} tests passed`);
