// Replays the reported session: first day, every card failed once, then passed.
const { JSDOM } = require('jsdom'), fs = require('fs'), assert = require('assert');
const { makeStore } = require('./fakeclaude.js');
const html = fs.readFileSync(__dirname + '/test.html', 'utf8');
const content = JSON.parse(fs.readFileSync(require('path').join(__dirname, '../content/all.json'), 'utf8'));
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const store = makeStore(content);
  const d = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://claude.ai/artifact/x', beforeParse(w) { w.scrollTo = () => {}; w.claude = { use: async n => n === 'db' ? store.db : n === 'user' ? { id: async () => 'u1', isOwner: async () => true } : null }; } });
  await sleep(200);
  const $ = s => d.window.document.querySelector(s), log = [], firstSeen = {};
  for (let i = 0; i < 40; i++) {
    const main = $('main').textContent.replace(/\s+/g, ' ').trim();
    assert(!/until the next card/.test(main), 'wait screen appeared: ' + main);
    if (!$('#reveal')) break;
    const prompt = main.replace(/^Flag/, '').slice(0, 50);
    $('#reveal').click(); await sleep(3);
    const again = Object.values(firstSeen).length === 9;
    log.push((again ? 'again  ' : 'first  ') + prompt);
    if (!again) firstSeen[prompt] = 1; else assert(!firstSeen[prompt], 'same wording shown twice running: ' + prompt);
    $(again ? '#pass' : '#fail').click(); await sleep(3);
  }
  await sleep(100);
  const end = $('main').textContent.replace(/\s+/g, ' ').trim();
  log.forEach(x => console.log('  ' + x));
  console.log('end screen:', end.slice(0, 70));
  assert.equal(log.length, 18, '9 first sights + 9 returns'); assert(/Nothing else is due today/.test(end));
  const rows = [...store.docs.keys()].filter(k => k.includes('/reviews/')).map(k => store.docs.get(k));
  assert(rows.every(r => r.sched === 'cert-srs-sched/1.1.0'), 'review rows carry the new scheduler version');
  console.log('no wait screen; every missed card came back in-session with different wording; rows tagged', rows[0].sched);
  process.exit(0);
})().catch(e => { console.error('FAIL', e.message); process.exit(1); });
