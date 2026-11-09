# Fact check: opens every source page linked by the milestone 3 concepts (HTTP 200 required) and tests each
# concept's EVIDENCE regexes against the page text. Usage: python3 factcheck.py [concept-id-prefix ...]
import json, os, re, sys, urllib.request
from bs4 import BeautifulSoup
from markdownify import markdownify as md
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import batch_m3
for ch in batch_m3.CHUNKS: ch(lambda *a, **k: (a[0], None), lambda t, w: None)  # fills EVIDENCE
allc = json.load(open(os.path.join(here, 'all.json')))
want = sys.argv[1:]
cache, bad, n = {}, [], 0
def page(url):
    if url not in cache:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 cert-srs-factcheck'}), timeout=30)
        soup = BeautifulSoup(r.read().decode('utf-8', 'replace'), 'lxml'); art = soup.find('article') or soup.find('main') or soup.body
        cache[url] = (r.status, r.geturl(), md(str(art), heading_style='ATX', bullets='-'))
    return cache[url]
for cid, ev in batch_m3.EVIDENCE.items():
    if want and not any(cid.startswith(w) for w in want): continue
    c = allc['concepts/' + cid]
    for i, s in enumerate(c['sources']):
        st, final, _ = page(s['url'])
        if st != 200: bad.append(f'{cid}: source {i} HTTP {st}')
        if final.rstrip('/') != s['url'].rstrip('/'): bad.append(f'{cid}: source {i} redirects to {final}')
    used = {v.get('src', 0) for v in c['recall']['variants'] + (c.get('scenario') or {}).get('variants', [])}
    for i, rx in ev:
        n += 1
        if not re.search(rx, page(c['sources'][i]['url'])[2]): bad.append(f'{cid}: evidence not found in source {i}: {rx}')
    if not used <= set(range(len(c['sources']))): bad.append(f'{cid}: variant points at a missing source')
print(f'fact check: {n} evidence lines across {len(cache)} pages')
for b in bad: print('  MISSING', b)
sys.exit(1 if bad else 0)
