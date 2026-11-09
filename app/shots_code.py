import json, os, asyncio, time, sys
from playwright.async_api import async_playwright
html = sys.argv[1]; prefix = sys.argv[2]
store_js = open('fakeclaude.js').read().replace('module.exports = { makeStore };', '')
content = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../content/all.json')))
now = int(time.time()*1000); DAY = 86400000
def st(track, kind, seen, last, due):
    return {"track": track, "concept": track.split(':')[0], "kind": kind, "introduced": now-5*DAY, "seen": seen, "lastVariant": last,
            "fsrs": {"due": due, "stability": 4, "difficulty": 5, "elapsedDays": 0, "scheduledDays": 4, "learningSteps": 0, "reps": 2, "lapses": 0, "state": 2, "lastReview": now-4*DAY}}
def seed_for(cid, vid):
    s = dict(content)
    for k in content:
        if k.startswith('concepts/'):
            c = k.split('/')[1]
            for kind, suf in (('recall', 'r'), ('scenario', 's')):
                if content[k].get(kind): s[f'data/users/u1/state/tracks/{c}:{suf}'] = st(f'{c}:{suf}', kind, {}, None, now + 30*DAY)
    ids = [v['id'] for v in content['concepts/' + cid]['recall']['variants']]
    seen = {v: now - (i + 2) * DAY for i, v in enumerate(ids) if v != vid}
    s[f'data/users/u1/state/tracks/{cid}:r'] = st(f'{cid}:r', 'recall', seen, ids[-1] if ids[-1] != vid else ids[0], now - DAY)
    return s
cards = [('dea-2-3-autoloader-schema-evolution', 'r2'), ('dea-2-2-copy-into-idempotent', 'r3'), ('dea-3-7-expectations', 'r2'), ('dea-7-3-masks-and-filters', 'r2')]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for i, (cid, vid) in enumerate(cards):
            pg = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
            await pg.add_init_script(store_js + "\nconst __s = makeStore(" + json.dumps(seed_for(cid, vid)) + ");\nwindow.claude = { use: async n => n==='db' ? __s.db : n==='user' ? { id: async () => 'u1' } : null };")
            await pg.goto('file://' + html); await pg.wait_for_timeout(600)
            await pg.click('#reveal'); await pg.wait_for_timeout(150)
            await pg.screenshot(path=f'{prefix}-{i}.png', clip={'x': 0, 'y': 0, 'width': 390, 'height': 520})
            sw = await pg.evaluate("(() => { const p = document.querySelector('pre.code'); return p ? [p.scrollWidth, p.clientWidth] : null })()")
            print(cid, vid, 'code scrollWidth/clientWidth:', sw)
        await b.close()
asyncio.run(main())
from PIL import Image
ims = [Image.open(f'{prefix}-{i}.png').resize((390, 520)) for i in range(len(cards))]
m = Image.new('RGB', (400 * len(ims), 520), 'grey')
for i, im in enumerate(ims): m.paste(im, (i * 400, 0))
m.save(f'{prefix}-montage.png')
