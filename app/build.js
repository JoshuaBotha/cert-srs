// Inlines ../scheduler/scheduler.js into app.src.html -> build/cert-srs.html (the published page)
// and writes test.html, where the jsDelivr script is replaced by the same pinned UMD build from node_modules.
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'app.src.html'), 'utf8');
const sched = fs.readFileSync(path.join(__dirname, '../scheduler/scheduler.js'), 'utf8');
if (!src.includes('/*__SCHEDULER__*/')) throw new Error('placeholder missing');
const out = src.replace('/*__SCHEDULER__*/', () => sched);
fs.mkdirSync(path.join(__dirname, 'build'), { recursive: true });
fs.writeFileSync(path.join(__dirname, 'build/cert-srs.html'), out);
const umd = fs.readFileSync(path.join(__dirname, '../scheduler/node_modules/ts-fsrs/dist/index.umd.js'), 'utf8');
fs.writeFileSync(path.join(__dirname, 'test.html'), out.replace('<script src="https://cdn.jsdelivr.net/npm/ts-fsrs@5.4.2/dist/index.umd.js"></script>', () => '<script>' + umd + '</script>'));
console.log('built', out.length, 'bytes');
