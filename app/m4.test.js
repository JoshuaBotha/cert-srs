// Milestone 4: navigation, Notes, Progress, Settings, backup and restore. Run after build.js.
// CERT_SRS_SNAPSHOT=/path/to/backup.json seeds the restore round trip with real rows (rewritten to test users);
// without it the round trip uses synthetic rows.
const { JSDOM } = require('jsdom'), fs = require('fs'), assert = require('assert'), path = require('path');
const { makeStore } = require('./fakeclaude.js');
const html = fs.readFileSync(path.join(__dirname, 'test.html'), 'utf8');
const content = JSON.parse(fs.readFileSync(path.join(__dirname, '../content/all.json'), 'utf8'));
// The database drops null fields (scenario: null); compare against what it actually holds.
const stripNull = o => JSON.parse(JSON.stringify(o, (k, v) => v === null ? undefined : v));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const DAY = 864e5;
const clone = o => JSON.parse(JSON.stringify(o));

async function open(store, opts = {}) {
  const dl = opts.dl || { saves: [] };
  const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://claude.ai/artifact/x' + (opts.hash || ''), beforeParse(w) {
    w.alert = () => {}; w.scrollTo = () => {};
    w.claude = { use: async n => n === 'db' ? store.db : n === 'user' ? { id: async () => opts.uid || 'u1', isOwner: async () => opts.owner !== false }
      : n === 'downloads' ? (opts.noDownloads ? null : { save: async r => { if (dl.reject) throw dl.reject; dl.saves.push(r); return { status: 'saved' }; } }) : null };
    if (w.HTMLDialogElement && !w.HTMLDialogElement.prototype.showModal) { w.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); }; w.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.dispatchEvent(new w.Event('close')); }; }
  } });
  await sleep(150);
  dom.dl = dl;
  return dom;
}
const $ = (d, s) => d.window.document.querySelector(s);
const $$ = (d, s) => [...d.window.document.querySelectorAll(s)];
const text = (d, s = 'main') => ($(d, s) ? $(d, s).textContent.replace(/\s+/g, ' ').trim() : '');
async function tab(d, v) { $(d, `#tabs button[data-v="${v}"]`).click(); await sleep(30); }
async function click(d, s) { const el = $(d, s); assert(el, 'missing ' + s); el.click(); await sleep(20); }
function setVal(d, s, v) { const el = $(d, s); assert(el, 'missing ' + s); el.value = v; el.dispatchEvent(new d.window.Event('input', { bubbles: true })); el.dispatchEvent(new d.window.Event('change', { bubbles: true })); }
const priv = (store, uid = 'u1') => { const o = {}; [...store.docs.keys()].filter(k => k.startsWith(`data/users/${uid}/`)).sort().forEach(k => { o[k.slice(`data/users/${uid}/`.length)] = store.docs.get(k); }); return o; };
const contentOf = store => { const o = {}; [...store.docs.keys()].filter(k => /^(exams|concepts|heldout)\//.test(k)).sort().forEach(k => { o[k] = store.docs.get(k); }); return o; };
function track(id, kind, now, stability, lastAgoDays, due) {
  return { track: id, concept: id.split(':')[0], kind, introduced: now - 5 * DAY, seen: { r1: now - lastAgoDays * DAY }, lastVariant: 'r1', sched: 'cert-srs-sched/1.1.0',
    fsrs: { due, stability, difficulty: 5, elapsedDays: 0, scheduledDays: 3, learningSteps: 0, reps: 3, lapses: 0, state: 2, lastReview: now - lastAgoDays * DAY } };
}
function seedPrivate(uid, now, nReviews) {
  const p = {}, ids = Object.keys(content).filter(k => k.startsWith('concepts/')).map(k => k.split('/')[1]);
  ids.slice(0, 12).forEach((c, i) => { p[`state/tracks/${c}:r`] = track(`${c}:r`, 'recall', now, 1 + i * 2, 1 + (i % 4), now + (i % 3 - 1) * DAY); });
  for (let i = 0; i < nReviews; i++) { const t = now - 20 * DAY + i * 60000, c = ids[i % 12]; p[`state/reviews/${t}_${c}:r`] = { t, track: c + ':r', concept: c, result: i % 3 ? 'pass' : 'fail', durationMs: 12000, sched: 'cert-srs-sched/1.1.0' }; }
  p['state'] = { days: { [new Date(now).toLocaleDateString('sv-SE')]: { ms: 5 * 60000, n: 12 } }, sched: 'cert-srs-sched/1.1.0', updated: now };
  p[`state/flags/${now - 3 * DAY}_${ids[0]}:r`] = { t: now - 3 * DAY, track: ids[0] + ':r', concept: ids[0], kind: 'recall', variant: 'r1', reason: 'gives-away', note: 'the code shows it', status: 'open', contentRev: 1, phase: 'open' };
  p[`state/flags/${now - 4 * DAY}_${ids[1]}:r`] = { t: now - 4 * DAY, track: ids[1] + ':r', concept: ids[1], kind: 'recall', variant: 'r2', reason: 'wrong', note: '', status: 'resolved', resolution: 'fixed', resolvedOn: '2026-11-06', fixedInRev: 2 };
  p[`state/notes/${now - DAY}_missed`] = { t: now - DAY, kind: 'missed', status: 'open', where: 'Lakeflow Jobs course', question: 'Which task type loops over a list?', mine: '', right: '', domain: '4', exam: 'databricks-dea' };
  p['settings'] = { exam: 'databricks-dea', dailyMinutes: 20, keepMe: 'yes' };
  return p;
}
const seed = (uid, p) => { const s = clone(content); Object.keys(p).forEach(k => { s[`data/users/${uid}/${k}`] = clone(p[k]); }); return s; };
async function restoreFrom(d, json, name = 'backup.json') {
  const w = d.window, input = $(d, '#restoreFile');
  Object.defineProperty(input, 'files', { value: [new w.File([json], name, { type: 'application/json' })], configurable: true });
  input.dispatchEvent(new w.Event('change')); await sleep(120);
}
async function confirmRestore(d, waitMs = 300) { await click(d, '#restoreGo'); assert(/Tap again/.test($(d, '#restoreGo').textContent), 'restore needs a second tap'); await click(d, '#restoreGo'); await sleep(waitMs); }

(async () => {
  const sched = fs.readFileSync(path.join(__dirname, '../scheduler/scheduler.js'), 'utf8');
  assert(html.includes(sched), 'scheduler.js is inlined unchanged');

  /* 1) navigation: tabs, hash routes, the review timer pauses away from Today and the same card comes back */
  {
    const store = makeStore(clone(content));
    const d = await open(store);
    assert.equal($(d, '#tabs').hidden, false, 'tabs shown once loaded');
    assert.equal($(d, '#tabs button[aria-current="page"]').textContent, 'Today');
    const first = text(d); assert($(d, '#reveal') || $(d, '.opts'), 'a card on Today');
    const logBefore = store.log.length;
    await tab(d, 'notes'); assert.equal(d.window.location.hash, '#notes'); assert(/Notes/.test(text(d)), 'notes shown');
    assert($(d, '#top').classList.contains('away'), 'review header hidden away from Today');
    await tab(d, 'progress'); assert(/Estimate/.test(text(d)));
    await tab(d, 'preferences'); assert(/Settings/.test(text(d)));
    await sleep(700);
    await tab(d, 'today'); assert.equal(text(d), first, 'the same card is back, in the same state');
    assert(!$(d, '#top').classList.contains('away'));
    assert.equal(store.log.length, logBefore, 'browsing the new screens writes nothing');
    if ($(d, '#reveal')) { await click(d, '#reveal'); await click(d, '#pass'); }
    else { $$(d, '.opt')[0].click(); await sleep(5); if ($(d, '#check').disabled) $$(d, '.opt')[1].click(); await click(d, '#check'); await click(d, '#next'); }
    await sleep(50);
    const row = [...store.docs.keys()].filter(k => k.includes('/reviews/')).map(k => store.docs.get(k))[0];
    assert(row && row.rawMs < 600, 'time away from Today is not counted: rawMs ' + (row && row.rawMs));
    assert.equal(row.sched, 'cert-srs-sched/1.1.0');
    const d2 = await open(makeStore(clone(content)), { hash: '#notes' });
    assert(/Notes/.test(text(d2)) && $(d2, '#tabs button[aria-current="page"]').textContent === 'Notes', 'a #notes link opens on Notes');
    await tab(d2, 'today'); assert($(d2, '#reveal') || $(d2, '.opts'), 'Today still starts a session after opening on Notes');
    const d3 = await open(makeStore(clone(content)), { hash: '#bogus' }); assert($(d3, '#reveal') || $(d3, '.opts'), 'unknown hash falls back to Today');
    console.log('navigation: ok (rawMs ' + row.rawMs + ' after 700 ms away)');
  }

  /* 2) Notes: a missed question, with draft, edit and delete */
  {
    const store = makeStore(clone(content));
    const d = await open(store, { hash: '#notes' });
    assert(/Nothing waiting/.test(text(d)) && /No open flags/.test(text(d)) && /No scores yet/.test(text(d)), 'empty Notes states');
    await click(d, '#newMissed');
    await click(d, '#formSave'); assert(/own words first/.test(text(d, '#formErr')), 'question required');
    assert.equal([...store.docs.keys()].filter(k => k.includes('/notes/')).length, 0);
    setVal(d, '#mWhere', 'Lakeflow Jobs course, module 3 quiz');
    setVal(d, '#mQuestion', 'Which task type runs a nested task once per item in a list?');
    // draft survives leaving the form and coming back
    await tab(d, 'today'); await tab(d, 'notes'); await click(d, '#newMissed');
    assert.equal($(d, '#mQuestion').value, 'Which task type runs a nested task once per item in a list?', 'draft kept');
    assert(d.window.localStorage.getItem('cert-srs-draft-missed'), 'draft kept in browser storage too');
    setVal(d, '#mMine', 'If/else'); setVal(d, '#mDomain', '4');
    await click(d, '#formSave'); await sleep(30);
    const keys = [...store.docs.keys()].filter(k => k.startsWith('data/users/u1/state/notes/'));
    assert.equal(keys.length, 1); const n = store.docs.get(keys[0]);
    assert.deepEqual([n.kind, n.status, n.where, n.domain, n.mine, n.exam], ['missed', 'open', 'Lakeflow Jobs course, module 3 quiz', '4', 'If/else', 'databricks-dea']);
    assert(/_missed$/.test(keys[0]) && typeof n.t === 'number');
    assert(/runs a nested task once per item/.test(text(d, '#waiting')), 'listed under waiting');
    assert.equal(d.window.localStorage.getItem('cert-srs-draft-missed'), null, 'draft cleared after saving');
    await click(d, '#newMissed'); assert.equal($(d, '#mQuestion').value, '', 'a new note starts empty');
    await click(d, '#formCancel');
    await click(d, '[data-edit]'); assert.equal($(d, '#mQuestion').value, n.question, 'edit is prefilled');
    setVal(d, '#mRight', 'For each task'); await click(d, '#formSave'); await sleep(30);
    const e = store.docs.get(keys[0]); assert.equal(e.right, 'For each task'); assert.equal(e.t, n.t); assert(e.edited, 'edit keeps id and time');
    await click(d, '[data-del]'); assert(store.docs.has(keys[0]), 'first tap only arms delete');
    await click(d, '[data-del]'); await sleep(30); assert(!store.docs.has(keys[0]), 'second tap deletes');
    console.log('notes, missed question: ok');
  }

  /* 3) Notes: Academy score, shown on Progress; open flags listed */
  {
    const now = Date.now(), p = seedPrivate('u1', now, 3);
    const store = makeStore(seed('u1', p));
    const d = await open(store, { hash: '#notes' });
    const fl = text(d, '#flagged');
    assert(/Gives itself away/.test(fl) && /the code shows it/.test(fl), 'open flag listed with reason and note');
    assert(!/Wrong/.test(fl), 'resolved flag not listed as awaiting');
    assert(/Which task type loops/.test(text(d, '#waiting')), 'seeded note listed');
    await click(d, '#newScore');
    assert.equal($(d, '#sDate').value, new Date(now).toLocaleDateString('sv-SE'), 'date defaults to today');
    setVal(d, '#sPct', '105'); await click(d, '#formSave'); assert(/0 to 100/.test(text(d, '#formErr')));
    setVal(d, '#sPct', '72'); setVal(d, '#sTest', 'Practice exam'); setVal(d, '#sQs', '45'); setVal(d, '#sD2', '60%'); setVal(d, '#sD7', 'weak on ABAC');
    await click(d, '#formSave'); await sleep(30);
    const s = [...store.docs.keys()].filter(k => /\/notes\/\d+_score$/.test(k)).map(k => store.docs.get(k))[0];
    assert(s && s.percent === 72 && s.questions === 45 && s.test === 'Practice exam' && s.status === 'open', 'score saved');
    assert.deepEqual(s.domains, { 2: '60%', 7: 'weak on ABAC' });
    assert(/72%/.test(text(d, '#scores')) && /D2: 60%/.test(text(d, '#scores')));
    await tab(d, 'progress'); await sleep(30);
    assert(/Latest Academy practice score: 72% \(Practice exam\)/.test(text(d, '#latestScore')), 'latest score beside the estimate: ' + text(d, '#latestScore'));
    console.log('notes, score log and flags: ok');
  }

  /* 4) Progress: the spec formula, checked against an independent computation */
  {
    const now = Date.now(), p = seedPrivate('u1', now, 0);
    for (const examDate of [null, new Date(now + 40 * DAY).toLocaleDateString('sv-SE')]) {
      const pp = clone(p); if (examDate) pp.settings.examDate = examDate;
      const store = makeStore(seed('u1', pp));
      const d = await open(store, { hash: '#progress' });
      const w = d.window, S = w.CertSched.create(w.FSRS, { retention: 0.9, fuzz: true });
      const exam = content['exams/databricks-dea'];
      const tExam = examDate ? +new Date(+examDate.slice(0, 4), +examDate.slice(5, 7) - 1, +examDate.slice(8, 10), 9) : now + 14 * DAY;
      const tracks = {}; Object.keys(content).filter(k => k.startsWith('concepts/')).forEach(k => { const c = content[k]; ['recall', 'scenario'].forEach(kind => { if (c[kind] && c[kind].variants.length) tracks[k.split('/')[1] + ':' + kind[0]] = String(c.objective); }); });
      let overall = 0; const per = {};
      exam.domains.forEach(dm => {
        let sum = 0;
        dm.objectives.forEach(o => {
          const ids = Object.keys(tracks).filter(t => tracks[t] === o.code), live = ids.filter(t => pp['state/tracks/' + t]);
          if (!live.length) return;
          sum += live.length / ids.length * live.reduce((a, t) => a + S.retrievability(pp['state/tracks/' + t].fsrs, tExam), 0) / live.length;
        });
        per[dm.n] = sum / dm.objectives.length; overall += dm.weight * per[dm.n];
      });
      const shown = text(d, '#overall'), drift = Math.abs(Date.now() - now) / DAY;
      assert.equal(shown, Math.round(100 * overall) + '%', 'overall matches the formula');
      assert(overall > 0 && overall < 0.2, 'sane: ' + overall);
      const rows = $$(d, '.dom'); assert.equal(rows.length, 7, 'seven domains');
      exam.domains.forEach((dm, i) => assert(rows[i].textContent.includes(Math.round(100 * per[dm.n]) + '%'), 'domain ' + dm.n));
      const lede = text(d, '.lede');
      if (examDate) assert(/your exam day/.test(lede) && !/14 days/.test(lede), 'booked date used: ' + lede);
      else assert(/No exam date is set/.test(lede) && /14 days from today/.test(lede), 'default horizon stated: ' + lede);
      assert(/Estimate/.test(text(d)) && /trust the scores/.test(text(d)), 'labelled as an estimate');
      const cov = rows.map(r => r.textContent.match(/coverage (\d+) of (\d+)/).slice(1).map(Number));
      assert.equal(cov.reduce((a, c) => a + c[0], 0), 12, 'introduced tracks counted'); assert.equal(cov.reduce((a, c) => a + c[1], 0), Object.keys(tracks).length, 'written tracks counted');
      await click(d, '#howBtn'); assert($(d, '#infoDlg').hasAttribute('open') && /Readiness = Σ/.test(text(d, '#infoBody')), 'formula one tap away');
      assert(drift < 1);
    }
    const d = await open(makeStore(clone(content)), { hash: '#progress' });
    assert.equal(text(d, '#overall'), '0%', 'nothing introduced reads 0%');
    console.log('progress and readiness: ok');
  }

  /* 5) Settings: exam date and daily minutes, merged into the settings document */
  {
    const now = Date.now(), p = seedPrivate('u1', now, 0);
    const store = makeStore(seed('u1', p));
    const d = await open(store, { hash: '#preferences' });
    assert.equal($(d, '#prefsSave').disabled, true, 'save disabled until something changes');
    await click(d, '#minUp'); await click(d, '#minUp'); assert.equal($(d, '#mins').value, '30');
    setVal(d, '#examDate', '2027-02-26');
    assert.equal($(d, '#prefsSave').disabled, false);
    await click(d, '#prefsSave'); await sleep(30);
    const s = store.docs.get('data/users/u1/settings');
    assert.equal(s.dailyMinutes, 30); assert.equal(s.examDate, '2027-02-26'); assert.equal(s.keepMe, 'yes', 'other settings kept'); assert.equal(s.exam, 'databricks-dea');
    assert(!('retention' in s), 'retention not written');
    await tab(d, 'today'); assert(/25 min left/.test(text(d, '#left')), 'new budget in the header: ' + text(d, '#left'));
    await tab(d, 'preferences'); await click(d, '#clearDate'); await click(d, '#prefsSave'); await sleep(30);
    assert(!('examDate' in store.docs.get('data/users/u1/settings')), 'cleared date removed');
    setVal(d, '#mins', '3'); await click(d, '#prefsSave'); assert(/5 to 120/.test(text(d, '#prefsErr')));
    console.log('settings: ok');
  }

  /* 6) Backup: content and every private row, reviews paged past 1,000 */
  let realBackup = null;
  {
    const now = Date.now(), p = seedPrivate('u1', now, 1203);
    const store = makeStore(seed('u1', p));
    const d = await open(store, { hash: '#preferences' });
    await click(d, '#backupBtn'); await sleep(200);
    assert.equal(d.dl.saves.length, 1, 'one download offered');
    const sv = d.dl.saves[0]; assert(/^cert-srs-backup-\d{4}-\d{2}-\d{2}-\d{4}\.json$/.test(sv.filename), sv.filename);
    const b = JSON.parse(sv.data);
    assert.equal(b.format, 'cert-srs-backup'); assert.equal(b.version, 1); assert.equal(b.uid, 'u1');
    assert.deepEqual(b.content, contentOf(store), 'all content exported');
    const want = clone(priv(store));
    const got = clone(b.private);
    assert.deepEqual(got, want, 'every private row exported');
    assert.equal(b.counts.reviews, 1203); assert.equal(b.counts.concepts, Object.keys(b.content).filter(k => k.startsWith('concepts/')).length);
    const pages = store.queries.filter(q => q.path.endsWith('/reviews') && q.limit === 500);
    assert(pages.length >= 3, 'reviews read in pages: ' + pages.length);
    assert(/Backup saved/.test(text(d, '#backupMsg')) && /Last backup/.test(text(d, '#lastBackup')));
    assert(d.window.localStorage.getItem('cert-srs-last-backup'), 'backup date remembered in the browser');
    assert.deepEqual(clone(priv(store)), clone(p), 'a backup writes nothing to the database');
    const d2 = await open(makeStore(seed('u1', p)), { hash: '#preferences', noDownloads: true });
    await click(d2, '#backupBtn'); await sleep(200);
    assert(JSON.parse($(d2, '#backupJson').value).counts.reviews === 1203, 'fallback shows the JSON when downloads are unavailable');
    const d3 = await open(makeStore(seed('u1', p)), { hash: '#preferences', dl: { saves: [], reject: { code: 'declined' } } });
    await click(d3, '#backupBtn'); await sleep(200); assert(/declined/.test(text(d3, '#backupMsg')));
    console.log('backup: ok (1203 reviews in ' + pages.length + ' pages, ' + Math.round(sv.data.length / 1024) + ' kB)');
  }

  /* 7) Restore round trip on a copy: back up, change things, restore, compare */
  {
    const now = Date.now();
    let base = seedPrivate('u1', now, 60), label = 'synthetic rows';
    if (process.env.CERT_SRS_SNAPSHOT) { realBackup = JSON.parse(fs.readFileSync(process.env.CERT_SRS_SNAPSHOT, 'utf8')); base = realBackup.private; label = 'real snapshot (' + Object.keys(base).length + ' private rows)'; }
    const store = makeStore(seed('u1', base));
    const original = clone(priv(store)), contentBefore = clone(contentOf(store));
    let d = await open(store, { hash: '#preferences' });
    await click(d, '#backupBtn'); await sleep(200);
    const json = d.dl.saves[0].data, b = JSON.parse(json);
    const atBackup = clone(priv(store));
    assert.deepEqual(atBackup, clone(b.private), 'backup equals the rows at that moment');
    // change things after the backup, through the app and directly
    d = await open(store, { hash: '#notes' });
    await click(d, '#newMissed'); setVal(d, '#mQuestion', 'A note written after the backup'); await click(d, '#formSave'); await sleep(30);
    await tab(d, 'today'); if ($(d, '#reveal')) { await click(d, '#reveal'); await click(d, '#fail'); } await sleep(30);
    const someTrack = Object.keys(atBackup).find(k => k.startsWith('state/tracks/'));
    if (someTrack) { const t = clone(atBackup[someTrack]); t.fsrs.stability = 999; store.docs.set('data/users/u1/' + someTrack, t); }
    const someFlag = Object.keys(atBackup).find(k => k.startsWith('state/flags/')); if (someFlag) store.docs.delete('data/users/u1/' + someFlag);
    assert.notDeepEqual(priv(store), atBackup, 'state changed after the backup');
    const extra = Object.keys(priv(store)).filter(k => !(k in atBackup));
    // restore through the app
    d = await open(store, { hash: '#preferences' });
    const writesBefore = store.log.length;
    await restoreFrom(d, json);
    assert(/Backup from/.test(text(d, '#restorePlan')) && new RegExp('deletes ' + extra.length + ' row').test(text(d, '#restorePlan')), 'plan: ' + text(d, '#restorePlan'));
    assert.equal(store.log.length, writesBefore, 'choosing a file writes nothing');
    await confirmRestore(d, 600);
    assert(/Restored/.test(text(d, '#restoreMsg')), text(d, '#restoreMsg'));
    assert.deepEqual(priv(store), atBackup, 'private rows equal the backup exactly');
    assert.deepEqual(contentOf(store), contentBefore, 'content untouched by restore');
    const dels = store.log.slice(writesBefore).filter(x => x[0] === 'delete').map(x => x[1]);
    assert.deepEqual(dels.sort(), extra.map(k => 'data/users/u1/' + k).sort(), 'deleted exactly the rows made after the backup');
    await tab(d, 'today'); assert($(d, '#reveal') || $(d, '.opts') || /due today|minutes/.test(text(d)), 'Today runs on the restored rows');
    // idempotent: restoring again changes nothing
    d = await open(store, { hash: '#preferences' }); await restoreFrom(d, json); await confirmRestore(d, 600);
    assert.deepEqual(priv(store), atBackup, 'a second restore is a no-op');
    // into a different user (fresh account): paths follow the signed-in user
    const other = makeStore(clone(content));
    d = await open(other, { hash: '#preferences', uid: 'u2' }); await restoreFrom(d, json); await confirmRestore(d, 600);
    assert.deepEqual(priv(other, 'u2'), atBackup, 'restores into another user id');
    // a transient outage partway: it stops, says so, and a rerun finishes
    const flaky = makeStore(clone(content));
    d = await open(flaky, { hash: '#preferences' }); await restoreFrom(d, json);
    flaky.setFail(5); await confirmRestore(d, 10500); // one write fails 5 times: the first try plus 4 retries
    assert(/Stopped after/.test(text(d, '#restoreMsg')), 'reports a stopped restore: ' + text(d, '#restoreMsg'));
    await click(d, '#restoreGo'); await click(d, '#restoreGo'); await sleep(800);
    assert.deepEqual(priv(flaky), atBackup, 'rerun completes the restore');
    // the original rows, too, when restoring the chat-made snapshot itself
    if (realBackup) {
      const fresh = makeStore(clone(content));
      d = await open(fresh, { hash: '#preferences' }); await restoreFrom(d, JSON.stringify(realBackup), 'snapshot.json'); await confirmRestore(d, 600);
      assert.deepEqual(priv(fresh), realBackup.private, 'chat snapshot restores exactly');
      assert.deepEqual(stripNull(realBackup.content), stripNull(content), 'snapshot content equals the built content');
    }
    void original; void b;
    console.log('restore round trip: ok on ' + label);
  }

  /* 8) Restore refuses anything that isn't a clean Cert SRS backup, before writing */
  {
    const store = makeStore(seed('u1', seedPrivate('u1', Date.now(), 2)));
    const d = await open(store, { hash: '#preferences' });
    const before = store.log.length;
    const good = { format: 'cert-srs-backup', version: 1, createdMs: Date.now(), private: { settings: { dailyMinutes: 20 } } };
    const cases = [['not json', 'isn’t a JSON file'], [JSON.stringify({ format: 'anki' }), 'isn’t a Cert SRS backup'],
      [JSON.stringify(Object.assign({}, good, { version: 2 })), 'version 2'], [JSON.stringify(Object.assign({}, good, { private: { '../../concepts/x': {} } })), 'won’t write'],
      [JSON.stringify(Object.assign({}, good, { private: { 'state/evil/x': {} } })), 'won’t write'], [JSON.stringify(Object.assign({}, good, { private: { 'state/tracks/..': {} } })), 'won’t write'],
      [JSON.stringify(Object.assign({}, good, { private: { 'state/tracks/a': [1] } })), 'won’t write'], [JSON.stringify(Object.assign({}, good, { private: null })), 'no private rows']];
    for (const [j, want] of cases) { await restoreFrom(d, j); assert(text(d, '#restorePlan').includes(want), want + ' -> ' + text(d, '#restorePlan')); assert(!$(d, '#restoreGo')); }
    assert.equal(store.log.length, before, 'nothing written for a bad file');
    console.log('restore validation: ok (' + cases.length + ' bad files refused)');
  }

  console.log('\nall milestone 4 checks passed'); process.exit(0);
})().catch(e => { console.error('FAIL', e && (e.stack || e.message || e)); process.exit(1); });
