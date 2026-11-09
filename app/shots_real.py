import json, os, asyncio, time
from playwright.async_api import async_playwright
store_js = open('fakeclaude.js').read().replace('module.exports = { makeStore };', '')
content = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../content/all.json')))
now = int(time.time()*1000); DAY = 86400000
def st(track, kind, seen, last, due):
    return {"track": track, "concept": track.split(':')[0], "kind": kind, "introduced": now-5*DAY, "seen": seen, "lastVariant": last,
            "fsrs": {"due": due, "stability": 4, "difficulty": 5, "elapsedDays": 0, "scheduledDays": 4, "learningSteps": 0, "reps": 2, "lapses": 0, "state": 2, "lastReview": now-4*DAY}}
A = dict(content); B = dict(content)
far = now + 30*DAY
for k in list(content):
    if k.startswith('concepts/'):
        cid = k.split('/')[1]
        for kind, suf in (('recall', 'r'), ('scenario', 's')):
            if content[k].get(kind):
                A[f'data/users/u1/state/tracks/{cid}:{suf}'] = st(f'{cid}:{suf}', kind, {}, None, far)
                B[f'data/users/u1/state/tracks/{cid}:{suf}'] = st(f'{cid}:{suf}', kind, {}, None, far)
A['data/users/u1/state/tracks/dea-7-2-usage-privileges:r'] = st('dea-7-2-usage-privileges:r', 'recall', {'r1': now-9*DAY, 'r2': now-8*DAY, 'r3': now-7*DAY, 'r5': now-4*DAY}, 'r5', now-DAY)
B['data/users/u1/state/tracks/dea-7-2-usage-privileges:s'] = st('dea-7-2-usage-privileges:s', 'scenario', {'s2': now-8*DAY, 's3': now-4*DAY}, 's3', now-DAY)
C = dict(B); C['data/users/u1/state/tracks/dea-7-2-usage-privileges:s'] = st('dea-7-2-usage-privileges:s', 'scenario', {}, None, far)
C['data/users/u1/state/tracks/dea-2-2-copy-into-idempotent:r'] = st('dea-2-2-copy-into-idempotent:r', 'recall', {'r1': now-9*DAY, 'r3': now-8*DAY, 'r4': now-7*DAY}, 'r4', now-DAY)
def init(seed): return store_js + "\nconst __s = makeStore(" + json.dumps(seed) + ");\nwindow.claude = { use: async n => n==='db' ? __s.db : n==='user' ? { id: async () => 'u1' } : null };"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        async def page(seed, scheme):
            pg = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2, color_scheme=scheme)
            await pg.add_init_script(init(seed)); await pg.goto('file://' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.html') + ''); await pg.wait_for_timeout(700); return pg
        pg = await page(A, 'light'); await pg.screenshot(path='real-1.png'); await pg.click('#reveal'); await pg.wait_for_timeout(150); await pg.screenshot(path='real-2.png')
        pg = await page(A, 'dark'); await pg.click('#reveal'); await pg.wait_for_timeout(150); await pg.screenshot(path='real-3.png')
        pg = await page(C, 'light'); await pg.screenshot(path='real-4.png')
        pg = await page(B, 'light')
        opts = await pg.query_selector_all('.opt'); await opts[0].click(); await (await pg.query_selector_all('.opt'))[2].click(); await pg.wait_for_timeout(100)
        await pg.screenshot(path='real-5.png'); await pg.click('#check'); await pg.wait_for_timeout(150); await pg.screenshot(path='real-6.png')
        await b.close()
asyncio.run(main())
from PIL import Image
ims = [Image.open(f'real-{i}.png').resize((390, 844)) for i in range(1, 7)]
m = Image.new('RGB', (400*6, 844), 'grey')
for i, im in enumerate(ims): m.paste(im, (i*400, 0))
m.save('real-montage.png'); print('ok')
