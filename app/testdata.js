// Small fixture: exam + 3 concepts covering every renderer (basic, cloze, code, occlusion, scenario pick-1, pick-2).
const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 120"><rect x="10" y="40" width="80" height="30" fill="none" stroke="#333"/><text x="20" y="60">alpha</text><rect x="110" y="40" width="80" height="30" fill="none" stroke="#333"/><text x="120" y="60">beta</text></svg>';
module.exports = {
  'exams/databricks-dea': { name: 'Test exam', domains: [{ n: '1', name: 'One', weight: 0.4, objectives: [{ code: '1.1', text: 'Obj one' }] }, { n: '2', name: 'Two', weight: 0.6, objectives: [{ code: '2.1', text: 'Obj two' }] }] },
  'concepts/t-a': { domain: '1', objective: '1.1', order: 1, status: 'live', rev: 1, sources: [{ title: 'Doc A', url: 'https://example.com/a' }],
    recall: { variants: [
      { id: 'r1', type: 'basic', prompt: 'Basic `q`?', answer: 'A1', why: 'because' },
      { id: 'r2', type: 'cloze', text: 'Fill {{gap}} here.', answer: 'GAP', why: 'w' },
      { id: 'r3', type: 'code', prompt: 'Complete it.', lang: 'sql', code: 'SELECT {{gap}} FROM t', answer: '*', why: 'w' }] },
    scenario: { variants: [
      { id: 's1', stem: 'Pick one.', pick: 1, correct: [{ text: 'Right', why: 'yes' }], distractors: [{ text: 'W1', why: 'n' }, { text: 'W2', why: 'n' }, { text: 'W3', why: 'n' }, { text: 'W4', why: 'n' }] },
      { id: 's2', stem: 'Pick two.', pick: 2, correct: [{ text: 'R1', why: 'y' }, { text: 'R2', why: 'y' }], distractors: [{ text: 'X1', why: 'n' }, { text: 'X2', why: 'n' }, { text: 'X3', why: 'n' }, { text: 'X4', why: 'n' }] }] } },
  'concepts/t-b': { domain: '2', objective: '2.1', order: 2, status: 'live', rev: 1, sources: [{ title: 'Doc B', url: 'https://example.com/b' }],
    diagrams: { d1: { svg, w: 300, h: 120, box: [80, 30], labels: { m1: [10, 40], m2: [110, 40] } } },
    recall: { variants: [
      { id: 'r1', type: 'occlusion', diagram: 'd1', mask: 'm1', prompt: 'Name the hidden label.', answer: 'alpha', why: 'w' },
      { id: 'r2', type: 'occlusion', diagram: 'd1', mask: 'm2', prompt: 'Name the hidden label.', answer: 'beta', why: 'w' }] } },
  'concepts/t-c': { domain: '2', objective: '2.1', order: 3, status: 'draft', recall: { variants: [{ id: 'r1', type: 'basic', prompt: 'draft', answer: 'x', why: 'x' }] } },
};
