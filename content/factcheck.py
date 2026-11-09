# Fact check: opens every source page a concept links (HTTP 200, no redirect) and tests the concept's own
# `evidence` regexes ([source index, regex] pairs stored on the concept document) against the page text.
# Usage: python3 factcheck.py [--all <path to all.json>] [concept-id-prefix ...]
# Default all.json is content/all.json (from build_content.py); the weekly review passes its workspace's.
import json, os, re, sys, urllib.request
from bs4 import BeautifulSoup
from markdownify import markdownify as md
here = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]; path = os.path.join(here, 'all.json')
if args[:1] == ['--all']: path, args = args[1], args[2:]
allc = json.load(open(path, encoding='utf-8'))
want = args
cache, bad, n, noev = {}, [], 0, []
def page(url):
    if url not in cache:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 cert-srs-factcheck'}), timeout=30)
        soup = BeautifulSoup(r.read().decode('utf-8', 'replace'), 'lxml'); art = soup.find('article') or soup.find('main') or soup.body
        cache[url] = (r.status, r.geturl(), md(str(art), heading_style='ATX', bullets='-'))
    return cache[url]
for key, c in sorted(allc.items()):
    if not key.startswith('concepts/'): continue
    cid = key.split('/', 1)[1]
    if want and not any(cid.startswith(w) for w in want): continue
    ev = c.get('evidence')
    if not ev: noev.append(cid); continue
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
if noev: print(f'no evidence (check by hand): {len(noev)}: ' + ', '.join(noev))
for b in bad: print('  MISSING', b)
sys.exit(1 if bad else 0)
