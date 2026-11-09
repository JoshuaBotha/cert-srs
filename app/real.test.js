const { JSDOM } = require('jsdom'), fs = require('fs'), assert = require('assert');
const { makeStore } = require('./fakeclaude.js');
const html = fs.readFileSync(__dirname + '/test.html', 'utf8');
const content = JSON.parse(fs.readFileSync(require('path').join(__dirname, '../content/all.json'), 'utf8'));
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const store = makeStore(content);
  const d = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://claude.ai/artifact/x', beforeParse(w) { w.scrollTo = () => {}; w.claude = { use: async n => n === 'db' ? store.db : n === 'user' ? { id: async () => 'u1', isOwner: async () => true } : null }; } });
  await sleep(200);
  const $ = s => d.window.document.querySelector(s), shown = [];
  for (let i = 0; i < 30; i++) {
    const main = $('main').textContent.replace(/\s+/g, ' ').trim();
    if ($('#reveal')) { shown.push('R ' + main.replace(/^Flag/, '').slice(0, 60)); $('#reveal').click(); await sleep(3); $('#pass').click(); await sleep(3); continue; }
    if ($('.opts')) { const k = /Choose two/.test(main) ? 2 : 1; shown.push('S ' + main.replace(/^Flag/, '').slice(0, 60)); [...d.window.document.querySelectorAll('.opt')].slice(0, k).forEach(b => b.click()); await sleep(3); $('#check').click(); await sleep(3); $('#next').click(); await sleep(3); continue; }
    break;
  }
  await sleep(100);
  console.log(shown.length + ' cards on day one:'); shown.forEach(x => console.log('  ' + x));
  console.log('end:', $('main').textContent.replace(/\s+/g, ' ').trim().slice(0, 80));
  const concepts = new Set(shown.length && [...store.docs.keys()].filter(k => k.includes('/tracks/')).map(k => k.split('/').pop().split(':')[0]));
  assert.equal(shown.length, 9, 'quota of 9 new tracks on day one'); assert.equal(concepts.size, 9, 'one track per concept (sibling rule)');
  const doms = [...store.docs.keys()].filter(k => k.includes('/tracks/')).map(k => content['concepts/' + k.split('/').pop().split(':')[0]].domain);
  console.log('domains introduced in order:', doms.join(' '));
  process.exit(0);
})().catch(e => { console.error('FAIL', e.message); process.exit(1); });
