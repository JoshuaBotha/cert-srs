// Plays every variant of the given concepts through the real app (test.html) in jsdom, with an in-memory database.
// Usage: node play_chunk.js <first order> <last order>   (concept "order" range, inclusive)
const { JSDOM } = require('jsdom'), fs = require('fs'), path = require('path'), assert = require('assert');
const { makeStore } = require('./fakeclaude.js');
const html = fs.readFileSync(path.join(__dirname, 'test.html'), 'utf8');
const content = JSON.parse(fs.readFileSync(path.join(__dirname, '../content/all.json'), 'utf8'));
const exam = content['exams/databricks-dea'];
const [lo, hi] = process.argv.slice(2).map(Number);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const plain = s => String(s).replace(/`/g, '').replace(/\s+/g, ' ').trim();
const now = Date.now(), DAY = 86400000;
const st = (track, kind, seen, last, due) => ({ track, concept: track.split(':')[0], kind, introduced: now - 5 * DAY, seen, lastVariant: last,
  fsrs: { due, stability: 4, difficulty: 5, elapsedDays: 0, scheduledDays: 4, learningSteps: 0, reps: 2, lapses: 0, state: 2, lastReview: now - 4 * DAY } });
function seed(cid, kind, vid) {
  const s = JSON.parse(JSON.stringify(content));
  for (const k of Object.keys(content)) if (k.startsWith('concepts/')) {
    const c = k.split('/')[1];
    for (const [kd, suf] of [['recall', 'r'], ['scenario', 's']]) if (content[k][kd]) s[`data/users/u1/state/tracks/${c}:${suf}`] = st(`${c}:${suf}`, kd, {}, null, now + 30 * DAY);
  }
  const ids = content['concepts/' + cid][kind].variants.map(v => v.id), suf = kind === 'recall' ? 'r' : 's';
  const seen = {}; ids.forEach((v, i) => { if (v !== vid) seen[v] = now - (i + 2) * DAY; });
  s[`data/users/u1/state/tracks/${cid}:${suf}`] = st(`${cid}:${suf}`, kind, seen, ids.find(v => v !== vid), now - DAY);
  return s;
}
async function open(store) {
  const d = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://claude.ai/artifact/x',
    beforeParse(w) { w.scrollTo = () => {}; w.claude = { use: async n => n === 'db' ? store.db : n === 'user' ? { id: async () => 'u1', isOwner: async () => true } : null }; } });
  for (let i = 0; i < 40 && !d.window.document.querySelector('#reveal, .opts'); i++) await sleep(25);
  return d;
}
(async () => {
  const ids = Object.keys(content).filter(k => k.startsWith('concepts/') && content[k].order >= lo && content[k].order <= hi).map(k => k.split('/')[1]);
  let played = 0, wrongRuns = 0; const fails = [];
  for (const cid of ids) {
    const c = content['concepts/' + cid], dom = exam.domains.find(d => d.n === c.domain);
    for (const kind of ['recall', 'scenario']) {
      if (!c[kind]) continue;
      for (const [vi, v] of c[kind].variants.entries()) for (const wrong of kind === 'scenario' && vi === 0 ? [false, true] : [false]) {
        const tag = `${cid}/${v.id}${wrong ? ' (wrong pick)' : ''}`;
        try {
          const store = makeStore(seed(cid, kind, v.id)), d = await open(store), doc = d.window.document, $ = s => doc.querySelector(s);
          const text = () => plain($('main').textContent);
          const lead = plain((v.prompt || v.stem || v.text).split('{{gap}}')[0]).slice(0, 40);
          assert(text().includes(lead), 'shown card is not this variant');
          assert(!$('.where'), 'domain visible before answering');
          if (kind === 'recall') {
            if (v.type === 'code' || v.type === 'cloze') { assert.equal(doc.querySelectorAll('.gap').length, 1, 'one gap'); assert(!$('.gap.filled'), 'gap pre-filled'); }
            if (v.type === 'occlusion') assert($('.mask:not(.open)'), 'mask missing');
            $('#reveal').click(); await sleep(5);
            if (v.type === 'code' || v.type === 'cloze') assert.equal($('.gap.filled').textContent, v.answer, 'gap fills with the answer');
            else assert.equal(plain($('.a').textContent), plain(v.answer), 'answer shown');
            assert.equal(plain($('.r').textContent), plain(v.why), 'reason shown');
            assert.equal($('.src a').href, c.sources[v.src || 0].url, 'source link'); assert($('.where').textContent.includes(dom.name), 'domain shown after');
            $('#pass').click();
          } else {
            const opts = [...doc.querySelectorAll('.opt')]; assert.equal(opts.length, 4, 'four options');
            const right = new Set(v.correct.map(o => plain(o.text)));
            const okIdx = opts.map((b, i) => right.has(plain(b.querySelector('span:nth-child(2)').textContent)) ? i : -1).filter(i => i >= 0);
            assert.equal(okIdx.length, v.pick, 'correct options shown');
            assert.equal(/Choose two/.test(text()), v.pick === 2, 'pick-two label');
            const pickIdx = wrong ? [opts.findIndex((b, i) => !okIdx.includes(i)), ...okIdx.slice(1)] : okIdx;
            for (const i of pickIdx) { doc.querySelectorAll('.opt')[i].click(); await sleep(2); }
            assert(!$('#check').disabled, 'check enabled'); $('#check').click(); await sleep(5);
            assert.equal($('.result').textContent, wrong ? 'Not this time.' : 'Right.', 'scored');
            assert.equal(doc.querySelectorAll('.opt .why').length, 4, 'every option explained');
            assert.equal($('.src a').href, c.sources[v.src || 0].url, 'source link'); assert($('.where').textContent.includes(dom.name), 'domain shown after');
            $('#next').click();
          }
          await sleep(30);
          const rows = [...store.docs.entries()].filter(([k]) => k.includes('/state/reviews/')).map(([, r]) => r);
          assert.equal(rows.length, 1, 'one review row'); assert.equal(rows[0].variant, v.id); assert.equal(rows[0].result, wrong ? 'fail' : 'pass');
          assert.equal(rows[0].contentRev, c.rev);
          d.window.close(); played++; if (wrong) wrongRuns++;
        } catch (e) { fails.push(`${tag}: ${e.message}`); }
      }
    }
  }
  console.log(`played ${played} cards from ${ids.length} concepts (orders ${lo}-${hi}), incl. ${wrongRuns} wrong-pick runs`);
  fails.forEach(f => console.log('  FAIL ' + f));
  process.exit(fails.length ? 1 : 0);
})();
