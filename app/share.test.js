// Sharing (app 1.3.0): the db rules, colleague feedback, the owner's inbox and the colleague-facing copy. Run after build.js.
const { JSDOM } = require('jsdom'), fs = require('fs'), assert = require('assert'), path = require('path');
const { makeStore, viewAs } = require('./fakeclaude.js');
const html = fs.readFileSync(path.join(__dirname, 'test.html'), 'utf8');
const content = JSON.parse(fs.readFileSync(path.join(__dirname, '../content/all.json'), 'utf8'));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const OWNER = 'u1', ALICE = 'u2', VIC = 'u3', EDDIE = 'u4';
const LEVELS = { [OWNER]: 'owner', [ALICE]: 'interact', [VIC]: 'view', [EDDIE]: 'admin' };
const NAMES = { [OWNER]: 'Josh', [ALICE]: 'Alice', [VIC]: 'Vic', [EDDIE]: 'Eddie' };

async function open(store, uid, opts = {}) {
  const ls = opts.localStorage || {};
  const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://claude.ai/artifact/x' + (opts.hash || ''), beforeParse(w) {
    w.alert = () => {}; w.scrollTo = () => {};
    Object.keys(ls).forEach(k => w.localStorage.setItem(k, ls[k]));
    w.claude = { use: async n => n === 'db' ? viewAs(store, uid, LEVELS[uid]) : n === 'user'
      ? { id: async () => uid, isOwner: async () => uid === OWNER, profiles: async ids => Object.fromEntries([].concat(ids).map(i => [i, { id: i, name: NAMES[i] || '' }])) }
      : n === 'downloads' ? { save: async () => ({ status: 'saved' }) } : null };
    if (w.HTMLDialogElement && !w.HTMLDialogElement.prototype.showModal) { w.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); }; w.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.dispatchEvent(new w.Event('close')); }; }
  } });
  await sleep(200);
  return dom;
}
const $ = (d, s) => d.window.document.querySelector(s);
const text = (d, s = 'main') => ($(d, s) ? $(d, s).textContent.replace(/\s+/g, ' ').trim() : '');
async function tab(d, v) { $(d, `#tabs button[data-v="${v}"]`).click(); await sleep(60); }
async function click(d, s) { const el = $(d, s); assert(el, 'missing ' + s); el.click(); await sleep(60); }
function setVal(d, s, v) { const el = $(d, s); assert(el, 'missing ' + s); el.value = v; el.dispatchEvent(new d.window.Event('input', { bubbles: true })); }
const reports = (store, uid) => [...store.docs.keys()].filter(k => k.startsWith(`reports/${uid}/items/`)).map(k => store.docs.get(k));

(async () => {
  const store = makeStore(JSON.parse(JSON.stringify(content)));

  // Rules, checked directly.
  const as = u => viewAs(store, u, LEVELS[u]);
  await assert.rejects(as(ALICE).doc('concepts/x').set({ a: 1 }), 'a Contributor cannot write cards');
  await assert.rejects(as(EDDIE).doc('exams/x').set({ a: 1 }), 'an Editor cannot write cards');
  await assert.rejects(as(VIC).doc(`data/users/${VIC}/settings`).set({ a: 1 }), 'a Viewer cannot save even their own progress');
  await assert.rejects(as(ALICE).doc(`data/users/${OWNER}/settings`).set({ a: 1 }), 'nobody writes another viewer\'s progress');
  await assert.rejects(as(ALICE).doc(`reports/${EDDIE}/items/x`).set({ a: 1 }), 'nobody writes another colleague\'s reports');
  await as(ALICE).doc(`data/users/${ALICE}/settings`).set({ dailyMinutes: 15 });
  assert.equal((await as(OWNER).doc(`data/users/${ALICE}/settings`).get()).exists, false, 'progress is private, even from the owner');
  console.log('rules: ok');

  // Colleague: welcome once, flag goes to the maintainer, feedback, a suggested card.
  let a = await open(store, ALICE);
  assert($(a, '#infoDlg').hasAttribute('open') && /beta/i.test(text(a, '#infoBody')), 'welcome shows on first visit');
  const flag = [...a.window.document.querySelectorAll('button')].find(b => b.textContent.trim() === 'Flag');
  assert(flag, 'a card is showing'); flag.click(); await sleep(30);
  assert(/maintains these cards/.test(text(a, '#flagSub')), 'flag dialog speaks to a colleague');
  a.window.document.querySelector('input[name="reason"][value="ambiguous"]').checked = true;
  setVal(a, '#flagNote', 'two answers fit'); await click(a, '#flagSave'); await sleep(200);
  assert.equal([...store.docs.keys()].filter(k => k.startsWith(`data/users/${ALICE}/state/flags/`)).length, 0, 'a colleague\'s flag is not a private flag');
  await tab(a, 'notes');
  assert(/private to you/.test(text(a)) && !/Project chat|weekly session/.test(text(a)), 'Notes copy speaks to a colleague');
  await click(a, '#newFeedback'); setVal(a, '#fText', 'More Unity Catalog scenarios'); await click(a, '#formSave'); await sleep(200);
  await click(a, '#newMissed');
  assert($(a, '#mSuggest') && $(a, '#mSuggest').checked, 'suggest-a-card is offered and ticked');
  setVal(a, '#mQuestion', 'Which clause makes MERGE skip matched rows?'); await click(a, '#formSave'); await sleep(250);
  const mine = reports(store, ALICE).map(r => r.kind).sort();
  assert.deepEqual(mine, ['feedback', 'flag', 'missed'], 'three reports filed: ' + mine);
  assert(reports(store, ALICE).every(r => r.from === ALICE && r.status === 'open'), 'reports carry the sender id and start open');
  assert(store.docs.has(`reports/${ALICE}`), 'the parent doc exists so the owner can list senders');
  assert(/Sent to the maintainer/.test(text(a)) && /Open/.test(text(a)), 'colleague sees what they sent');
  await tab(a, 'preferences');
  assert(!/Project chat/.test(text(a)) && /About/.test(text(a)), 'Settings copy speaks to a colleague');
  a.window.close();
  a = await open(store, ALICE, { localStorage: { 'cert-srs-welcome-1': '1' } });
  assert(!$(a, '#infoDlg').hasAttribute('open'), 'welcome shows only once'); a.window.close();
  console.log('colleague: ok');

  // Owner: no welcome, own copy unchanged, inbox with names, mark done.
  let o = await open(store, OWNER, { hash: '#notes' }); await sleep(200);
  assert(!$(o, '#infoDlg').hasAttribute('open'), 'the owner gets no welcome');
  assert(/weekly session/.test(text(o)), 'owner copy unchanged');
  assert(/From colleagues/.test(text(o)) && /Alice/.test(text(o, '#inbox')), 'inbox lists Alice by name');
  assert.equal(o.window.document.querySelectorAll('#inbox [data-done]').length, 3, 'three open items');
  await click(o, '#inbox [data-done]'); await sleep(150);
  assert.equal(reports(store, ALICE).filter(r => r.status === 'resolved').length, 1, 'mark done writes to the colleague\'s report');
  assert(/Recently done/.test(text(o, '#inbox')));
  o.window.close();
  a = await open(store, ALICE, { hash: '#notes', localStorage: { 'cert-srs-welcome-1': '1' } }); await sleep(200);
  assert(/Done/.test(text(a, '#sent')), 'the colleague sees it marked done'); a.window.close();
  console.log('owner inbox: ok');

  // Viewer: can't save, so a colleague must be shared as Contributor.
  const before = [...store.docs.keys()].filter(k => k.startsWith(`data/users/${VIC}/`)).length;
  const v = await open(store, VIC, { localStorage: { 'cert-srs-welcome-1': '1' } });
  assert.equal([...store.docs.keys()].filter(k => k.startsWith(`data/users/${VIC}/`)).length, before, 'nothing saved for a Viewer'); v.window.close();
  console.log('viewer: ok');

  console.log('\nall sharing checks passed');
  process.exit(0);
})().catch(e => { console.error(e); process.exit(1); });
