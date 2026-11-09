const { JSDOM } = require('jsdom'), fs = require('fs'), assert = require('assert');
const { makeStore } = require('./fakeclaude.js');
const html = fs.readFileSync(__dirname + '/test.html', 'utf8');
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function open(store, opts = {}) {
  const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://claude.ai/artifact/x', beforeParse(w) {
    w.alert = () => {}; w.scrollTo = () => {};
    if (opts.noClaude) return;
    w.claude = { use: async (n) => n === 'db' ? (opts.noDb ? null : store.db) : n === 'user' ? { id: async () => opts.uid === undefined ? 'u1' : opts.uid, isOwner: async () => opts.owner !== false } : null };
    if (w.HTMLDialogElement && !w.HTMLDialogElement.prototype.showModal) { w.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); }; w.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.dispatchEvent(new w.Event('close')); }; }
  } });
  await sleep(150);
  return dom;
}
const $ = (d, s) => d.window.document.querySelector(s);
const text = d => $(d, 'main').textContent.replace(/\s+/g, ' ').trim();
async function answerOne(d, pass) {
  const doc = d.window.document;
  if ($(d, '#reveal')) {
    const before = text(d); assert(!/A1|GAP|alpha|beta/.test(before.replace('Name the hidden label.', '')), 'answer visible before reveal: ' + before);
    $(d, '#reveal').click(); await sleep(5);
    assert($(d, '.ans'), 'answer section shown'); assert($(d, '.where'), 'domain shown after answer');
    $(d, pass ? '#pass' : '#fail').click(); await sleep(5); return 'recall';
  }
  if ($(d, '.opts')) {
    assert(!$(d, '.where'), 'domain hidden before answer');
    const opts = [...doc.querySelectorAll('.opt')]; assert.equal(opts.length, 4);
    const pickTwo = /Choose two/.test(text(d));
    const card = d.window.eval('null'); // no access to internals; choose by label text
    const isRight = o => /^(Right|R1|R2)$/.test(o.textContent.slice(1).trim());
    const chosen = pass ? opts.filter(isRight) : opts.filter(o => !isRight(o)).slice(0, pickTwo ? 2 : 1);
    assert.equal($(d, '#check').disabled, true, 'check disabled before picking');
    chosen.forEach(o => o.click());
    await sleep(5);
    assert.equal($(d, '#check').disabled, false, 'check enabled after picking'); $(d, '#check').click(); await sleep(5);
    assert(doc.querySelectorAll('.opt .why').length === 4, 'every option explained');
    assert(/Right\.|Not this time\./.test(text(d)));
    if (pass) assert($(d, '#guess'), 'guessed button offered on a correct pick'); else assert(!$(d, '#guess'));
    $(d, '#next').click(); await sleep(5); return pickTwo ? 'pick2' : 'pick1';
  }
  return null;
}
(async () => {
  const fixture = require('./testdata.js');
  // 1) a full first session
  let store = makeStore(fixture);
  let d = await open(store);
  assert(/due/.test($(d, '#due').textContent), 'header shows due count');
  const seen = [];
  for (let i = 0; i < 12; i++) { const k = await answerOne(d, i % 3 !== 2); if (!k) break; seen.push(k); }
  await sleep(50);
  assert(/Everything is saved/.test(text(d)), 'save note updates'); console.log('session 1 cards:', seen.join(', '), '| end screen:', text(d).slice(0, 90));
  const rows = [...store.docs.keys()].filter(k => k.includes('/state/reviews/'));
  const tracks = [...store.docs.keys()].filter(k => k.includes('/state/tracks/'));
  assert(!tracks.some(k => k.includes('t-c')), 'draft concept never shown');
  assert(rows.length === seen.length, `one review row per answer (${rows.length} vs ${seen.length})`);
  const r0 = store.docs.get(rows[0]);
  ['t', 'track', 'variant', 'result', 'rating', 'durationMs', 'sched', 'stateBefore', 'elapsedDays'].forEach(f => assert(f in r0, 'review row has ' + f));
  const st = store.docs.get('data/users/u1/state'); assert(st && Object.values(st.days)[0].n === seen.length, 'day summary counts every review');
  const tr = store.docs.get(tracks[0]); assert(tr.fsrs && tr.seen && tr.lastVariant, 'track state saved');
  assert(/waiting|minute|today|Tomorrow/i.test(text(d)), 'session ends on a wait or done screen');
  // sibling rule: t-a recall and scenario never both on day one
  const kinds = tracks.map(k => k.split('/').pop());
  assert(!(kinds.includes('t-a:r') && kinds.includes('t-a:s')), 'sibling waited until tomorrow: ' + kinds);
  console.log('tracks introduced:', kinds.join(', '));

  // 2) flag a card
  store = makeStore(fixture); d = await open(store);
  $(d, '#flagBtn').click(); await sleep(5);
  d.window.document.querySelector('input[value="gives-away"]').checked = true;
  $(d, '#flagSave').click(); await sleep(30);
  const flags = [...store.docs.keys()].filter(k => k.includes('/state/flags/'));
  assert.equal(flags.length, 1); const f = store.docs.get(flags[0]); assert.equal(f.reason, 'gives-away'); assert.equal(f.status, 'open');
  // "Other" needs a note
  $(d, '#flagBtn').click(); d.window.document.querySelector('input[value="other"]').checked = true; $(d, '#flagSave').click(); await sleep(20);
  assert.equal([...store.docs.keys()].filter(k => k.includes('/state/flags/')).length, 1, 'Other without a note is not saved');
  console.log('flag saved:', f.reason, f.track);

  // 3) a transient outage is retried, nothing lost
  store = makeStore(fixture, { failNext: 2 }); d = await open(store);
  await answerOne(d, true); await sleep(5000);
  assert.equal([...store.docs.keys()].filter(k => k.includes('/state/reviews/')).length, 1, 'review saved after retries');
  assert.equal($(d, '#sync').hidden, true, 'no error shown after recovery');
  console.log('retry after outage: ok');

  // 4) budget used -> end screen; empty content; no db; outside Claude
  store = makeStore(Object.assign({}, fixture, { 'data/users/u1/state': { days: { [new Date(Date.now() - 4 * 3600e3).toLocaleDateString('sv-SE')]: { ms: 20 * 60000, n: 40 } } } }));
  d = await open(store); assert(/today’s 20 minutes/.test(text(d)), 'budget end screen: ' + text(d));
  d = await open(makeStore({ 'exams/databricks-dea': fixture['exams/databricks-dea'] })); assert(/No cards yet/.test(text(d)));
  d = await open(makeStore(fixture), { noDb: true }); assert(/can’t load here/.test(text(d)));
  d = await open(makeStore(fixture), { uid: null }); assert(/Sign in/.test(text(d)));
  d = await open(makeStore(fixture), { noClaude: true }); assert(/Open this page in Claude/.test(text(d)));
  console.log('end and error screens: ok');

  // 5) day two: recall track seen 3 days ago and not due -> the scenario track is new today
  for (let run = 0; run < 6; run++) {
    const now = Date.now(), DAY = 864e5;
    const seeded = Object.assign({}, fixture, {
      'data/users/u1/state/tracks/t-a:r': { track: 't-a:r', concept: 't-a', kind: 'recall', introduced: now - 3 * DAY, seen: { r1: now - 3 * DAY }, lastVariant: 'r1',
        fsrs: { due: now + 10 * DAY, stability: 12, difficulty: 5, elapsedDays: 0, scheduledDays: 13, learningSteps: 0, reps: 2, lapses: 0, state: 2, lastReview: now - 3 * DAY } },
      'data/users/u1/state/tracks/t-b:r': { track: 't-b:r', concept: 't-b', kind: 'recall', introduced: now - 3 * DAY, seen: { r1: now - 3 * DAY }, lastVariant: 'r1',
        fsrs: { due: now - DAY, stability: 2, difficulty: 5, elapsedDays: 0, scheduledDays: 2, learningSteps: 0, reps: 1, lapses: 0, state: 2, lastReview: now - 3 * DAY } } });
    store = makeStore(seeded); d = await open(store);
    // due first: t-b:r (occlusion), and it must not repeat variant r1
    assert($(d, '.dia img'), 'occlusion diagram rendered'); assert($(d, '.mask'), 'mask rendered');
    const maskStyle = $(d, '.mask').getAttribute('style'); assert(/left:\s*36\.6/.test(maskStyle), 'variant r2 (mask m2) shown, not r1 again: ' + maskStyle);
    await answerOne(d, true);
    const k = await answerOne(d, run % 2 === 0);
    assert(k === 'pick1' || k === 'pick2', 'scenario question shown next, got ' + k);
    await sleep(30);
    const sc = [...store.docs.keys()].filter(x => x.includes('/reviews/') && x.endsWith('t-a:s')).map(x => store.docs.get(x))[0];
    assert(sc && 'guessed' in sc && Array.isArray(sc.picked) && sc.picked.length === (k === 'pick2' ? 2 : 1), 'scenario row records picks');
    assert.equal(sc.result, run % 2 === 0 ? 'pass' : 'fail');
    process.stdout.write(k + (run % 2 === 0 ? ' pass, ' : ' fail, '));
  }
  console.log('day-two scenario runs: ok');
  // guessed turns a correct pick into a fail
  {
    const now = Date.now(), DAY = 864e5;
    store = makeStore(Object.assign({}, fixture, { 'concepts/t-b': Object.assign({}, fixture['concepts/t-b'], { status: 'retired' }),
      'data/users/u1/state/tracks/t-a:r': { track: 't-a:r', concept: 't-a', kind: 'recall', introduced: now - 3 * DAY, seen: {}, lastVariant: 'r1',
        fsrs: { due: now + 10 * DAY, stability: 12, difficulty: 5, elapsedDays: 0, scheduledDays: 13, learningSteps: 0, reps: 2, lapses: 0, state: 2, lastReview: now - 3 * DAY } } }));
    d = await open(store);
    const doc = d.window.document, opts = [...doc.querySelectorAll('.opt')], pickTwo = /Choose two/.test(text(d));
    opts.filter(o => /^(Right|R1|R2)$/.test(o.textContent.slice(1).trim())).forEach(o => o.click()); await sleep(5);
    $(d, '#check').click(); await sleep(5); $(d, '#guess').click(); await sleep(5);
    assert.equal($(d, '#guess').getAttribute('aria-pressed'), 'true'); $(d, '#next').click(); await sleep(30);
    const row = [...store.docs.keys()].filter(x => x.includes('/reviews/')).map(x => store.docs.get(x))[0];
    assert(row.correct === true && row.guessed === true && row.result === 'fail' && row.rating === 1, 'guessed correct pick graded as fail');
    console.log('guessed -> fail: ok (' + (pickTwo ? 'pick-two' : 'pick-one') + ')');
  }
  console.log('\nall UI checks passed'); process.exit(0);
})().catch(e => { console.error('FAIL', e.message || e); process.exit(1); });
