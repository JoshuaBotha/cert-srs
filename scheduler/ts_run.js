const F = require('ts-fsrs'), S = require('./scheduler.js');
const s = S.create(F, { fuzz: false });
const cards = {}, out = [];
for (const r of require('./history.json')) {
  const g = s.grade(cards[r.card] || null, r.pass, r.t);
  cards[r.card] = g.fsrs;
  out.push({ card: r.card, t: r.t, state: g.fsrs.state, stability: g.fsrs.stability, difficulty: g.fsrs.difficulty, due: g.fsrs.due });
}
require('fs').writeFileSync('ts_out.json', JSON.stringify(out));
console.log('ts-fsrs done', out.length);
