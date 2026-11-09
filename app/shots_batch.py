# Phone-width (390x844) screenshots of chosen cards, as a phone shows them, plus a horizontal-overflow check.
# Usage: python3 shots_batch.py test.html <prefix> '<json list of [concept, kind, variant, phase]>'   phase: ask | open
import json, os, re, sys, time, asyncio
from playwright.async_api import async_playwright
from PIL import Image
html, prefix, cards = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
store_js = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fakeclaude.js')).read()
store_js = re.sub(r'^module\.exports = .*$', '', store_js, flags=re.M)  # browser has no module
content = json.load(open(os.environ.get('CERT_SRS_ALL') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '../content/all.json')))  # CERT_SRS_ALL: a workspace's all.json
now = int(time.time() * 1000); DAY = 86400000
def st(track, kind, seen, last, due):
    return {'track': track, 'concept': track.split(':')[0], 'kind': kind, 'introduced': now - 5 * DAY, 'seen': seen, 'lastVariant': last,
            'fsrs': {'due': due, 'stability': 4, 'difficulty': 5, 'elapsedDays': 0, 'scheduledDays': 4, 'learningSteps': 0, 'reps': 2, 'lapses': 0, 'state': 2, 'lastReview': now - 4 * DAY}}
def seed(cid, kind, vid):
    s = dict(content)
    for k in content:
        if k.startswith('concepts/'):
            c = k.split('/')[1]
            for kd, suf in (('recall', 'r'), ('scenario', 's')):
                if content[k].get(kd): s[f'data/users/u1/state/tracks/{c}:{suf}'] = st(f'{c}:{suf}', kd, {}, None, now + 30 * DAY)
    ids = [v['id'] for v in content['concepts/' + cid][kind]['variants']]; suf = 'r' if kind == 'recall' else 's'
    seen = {v: now - (i + 2) * DAY for i, v in enumerate(ids) if v != vid}
    s[f'data/users/u1/state/tracks/{cid}:{suf}'] = st(f'{cid}:{suf}', kind, seen, next(v for v in ids if v != vid), now - DAY)
    return s
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for i, (cid, kind, vid, phase) in enumerate(cards):
            pg = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
            await pg.add_init_script(store_js + "\nconst __s = makeStore(" + json.dumps(seed(cid, kind, vid)) + ");\nwindow.claude = { use: async n => n==='db' ? __s.db : n==='user' ? { id: async () => 'u1', isOwner: async () => true } : null };")
            await pg.goto('file://' + os.path.abspath(html)); await pg.wait_for_selector('#reveal, .opts')
            if phase == 'open':
                if kind == 'recall': await pg.click('#reveal')
                else:
                    right = [o['text'].replace('`', '') for o in next(v for v in content['concepts/' + cid][kind]['variants'] if v['id'] == vid)['correct']]
                    await pg.evaluate("r => document.querySelectorAll('.opt').forEach(b => { if (r.includes(b.children[1].textContent.trim())) b.click(); })", right)
                    await pg.click('#check')
                await pg.wait_for_timeout(150)
            await pg.screenshot(path=f'{prefix}-{i}.png')
            ov = await pg.evaluate("[document.documentElement.scrollWidth, ...[...document.querySelectorAll('pre.code')].map(p => p.scrollWidth - p.clientWidth)]")
            print(f'{i}: {cid} {vid} {phase}  page width {ov[0]}px, code overflow {ov[1:] or "none"}')
        await b.close()
asyncio.run(main())
ims = [Image.open(f'{prefix}-{i}.png').resize((390, 844)) for i in range(len(cards))]
m = Image.new('RGB', (400 * len(ims), 844), 'grey')
for i, im in enumerate(ims): m.paste(im, (i * 400, 0))
m.save(f'{prefix}-montage.png'); print('montage', f'{prefix}-montage.png')
