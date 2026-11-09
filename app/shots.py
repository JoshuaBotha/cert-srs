import json, asyncio, time
from playwright.async_api import async_playwright
store_js = open('fakeclaude.js').read().replace('module.exports = { makeStore };', '')
fixture = json.loads(open('fixture.json').read())
now = int(time.time()*1000); DAY = 86400000
fixture['data/users/u1/state/tracks/t-a:r'] = {"track":"t-a:r","concept":"t-a","kind":"recall","introduced":now-3*DAY,"seen":{"r1":now-3*DAY},"lastVariant":"r1","fsrs":{"due":now+10*DAY,"stability":12,"difficulty":5,"elapsedDays":0,"scheduledDays":13,"learningSteps":0,"reps":2,"lapses":0,"state":2,"lastReview":now-3*DAY}}
fixture['data/users/u1/state/tracks/t-b:r'] = {"track":"t-b:r","concept":"t-b","kind":"recall","introduced":now-3*DAY,"seen":{"r1":now-3*DAY},"lastVariant":"r1","fsrs":{"due":now-DAY,"stability":2,"difficulty":5,"elapsedDays":0,"scheduledDays":2,"learningSteps":0,"reps":1,"lapses":0,"state":2,"lastReview":now-3*DAY}}
init = store_js + "\nconst __s = makeStore(" + json.dumps(fixture) + ");\nwindow.claude = { use: async n => n==='db' ? __s.db : n==='user' ? { id: async () => 'u1' } : null };"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for scheme in ['light', 'dark']:
            pg = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2, color_scheme=scheme)
            await pg.add_init_script(init)
            await pg.goto('file://' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.html') + ''); await pg.wait_for_timeout(600)
            await pg.screenshot(path=f'shot-{scheme}-1-occlusion.png')
            await pg.click('#reveal'); await pg.wait_for_timeout(150)
            await pg.screenshot(path=f'shot-{scheme}-2-revealed.png')
            await pg.click('#pass'); await pg.wait_for_timeout(200)
            await pg.screenshot(path=f'shot-{scheme}-3-scenario.png')
            opts = await pg.query_selector_all('.opt')
            pick2 = 'Choose two' in (await pg.inner_text('main'))
            await opts[0].click()
            if pick2: await (await pg.query_selector_all('.opt'))[1].click()
            await pg.wait_for_timeout(100); await pg.click('#check'); await pg.wait_for_timeout(150)
            await pg.screenshot(path=f'shot-{scheme}-4-answered.png', full_page=True)
            await pg.click('#flagBtn'); await pg.wait_for_timeout(150)
            await pg.screenshot(path=f'shot-{scheme}-5-flag.png')
        await b.close()
asyncio.run(main())
print('ok')
