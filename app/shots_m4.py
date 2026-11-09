# Milestone 4 screens at 390x844, light and dark. Usage: python3 shots_m4.py [backup.json]  (seeds private rows from a backup if given)
import json, os, sys, asyncio, time
from playwright.async_api import async_playwright
here = os.path.dirname(os.path.abspath(__file__))
store_js = open(os.path.join(here, 'fakeclaude.js')).read().replace('module.exports = { makeStore };', '')
content = json.load(open(os.path.join(here, '../content/all.json')))
now = int(time.time() * 1000); DAY = 86400000
seed = {k: v for k, v in content.items()}
priv = json.load(open(sys.argv[1]))['private'] if len(sys.argv) > 1 else {}
for k, v in priv.items(): seed['data/users/u1/' + k] = v
seed[f'data/users/u1/state/notes/{now-DAY}_missed'] = {'t': now - DAY, 'kind': 'missed', 'status': 'open', 'where': 'Lakeflow Jobs course, module 3 quiz', 'question': 'A job must run one notebook task per region in a list, each with the region as a parameter. Which task type does that without copying the task?', 'mine': '', 'right': '', 'domain': '4'}
seed[f'data/users/u1/state/notes/{now-2*DAY}_score'] = {'t': now - 2 * DAY, 'kind': 'score', 'status': 'open', 'date': time.strftime('%Y-%m-%d', time.localtime((now - 2 * DAY) / 1000)), 'percent': 68, 'test': 'Practice exam', 'questions': 45, 'domains': {'2': '60%', '7': 'weak on ABAC'}, 'note': ''}
seed[f'data/users/u1/state/flags/{now-3*DAY}_dea-3-2-joins:r'] = {'t': now - 3 * DAY, 'track': 'dea-3-2-joins:r', 'concept': 'dea-3-2-joins', 'kind': 'recall', 'variant': 'r1', 'reason': 'ambiguous', 'note': 'Could be read as a left join too', 'status': 'open', 'contentRev': 1, 'phase': 'open'}
backup = json.dumps({'format': 'cert-srs-backup', 'version': 1, 'createdMs': now - DAY, 'source': 'app', 'private': priv or {'settings': {}}, 'content': {}})
open('/tmp/m4-restore.json', 'w').write(backup)
init = store_js + "\nconst __s = makeStore(" + json.dumps(seed) + ");\nwindow.claude = { use: async n => n==='db' ? __s.db : n==='user' ? { id: async () => 'u1' } : n==='downloads' ? { save: async () => ({status:'saved'}) } : null };"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); out = []
        for scheme in ('light', 'dark'):
            async def pg(hash):
                g = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2, color_scheme=scheme)
                await g.add_init_script(init); await g.goto('file://' + os.path.join(here, 'test.html') + hash); await g.wait_for_timeout(700); return g
            async def shot(g, name, full=True):
                f = f'm4-{name}-{scheme}.png'; await g.screenshot(path=f, full_page=full); out.append(f)
                w = await g.evaluate('[document.documentElement.scrollWidth, window.innerWidth]'); assert w[0] <= w[1], (name, scheme, w)
            g = await pg('#progress'); await shot(g, '1-progress'); await g.click('#howBtn'); await g.wait_for_timeout(150); await shot(g, '2-formula', False)
            g = await pg('#notes'); await g.wait_for_timeout(200); await shot(g, '3-notes')
            await g.click('#newMissed'); await g.wait_for_timeout(100); await g.fill('#mWhere', 'Data Ingestion course, quiz 2'); await g.fill('#mQuestion', 'Auto Loader with a new column in source files: which option keeps the stream running and adds the column?'); await shot(g, '4-missed', False)
            await g.click('#formCancel'); await g.click('#newScore'); await g.wait_for_timeout(100); await g.fill('#sPct', '72'); await g.fill('#sTest', 'Practice exam'); await g.click('details.more summary'); await g.wait_for_timeout(100); await shot(g, '5-score')
            g = await pg('#preferences'); await shot(g, '6-settings')
            await g.set_input_files('#restoreFile', '/tmp/m4-restore.json'); await g.wait_for_timeout(400); await g.evaluate('window.scrollTo(0, document.body.scrollHeight)'); await shot(g, '7-restore', False)
            g = await pg(''); await shot(g, '8-today', False)
        await b.close(); print(len(out), 'screenshots, no sideways scroll')
asyncio.run(main())
from PIL import Image
for scheme in ('light', 'dark'):
    names = ['1-progress', '2-formula', '3-notes', '4-missed', '5-score', '6-settings', '7-restore', '8-today']
    ims = [Image.open(f'm4-{n}-{scheme}.png') for n in names]; ims = [im.resize((390, int(im.height * 390 / im.width))) for im in ims]
    H = max(im.height for im in ims); m = Image.new('RGB', (400 * len(ims), H), 'grey')
    for i, im in enumerate(ims): m.paste(im, (i * 400, 0))
    m.save(f'm4-montage-{scheme}.png'); print(f'm4-montage-{scheme}.png', m.size)
