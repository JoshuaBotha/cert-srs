# Card-rule validator for Cert SRS concept documents. Shared by content/build_content.py and the
# claude.ai weekly review, which validates the database's own JSON (see tools/workspace.py).
# Usage: python3 validate.py <workspace dir>   (reads <dir>/all.json; exit 1 on problems)
import json, re, sys

def check(C):
  """C: list of (concept id, concept document). Returns (problems, notes)."""
  problems, notes = [], []
  if len({cid for cid, _ in C}) != len(C): problems.append('duplicate concept ids')
  if len({c['order'] for _, c in C}) != len(C): problems.append('duplicate order values')
  def prose_fields(v):
    for k in ('prompt', 'text', 'stem', 'answer', 'why'):
      if k in v: yield k, v[k]
  for cid, c in C:
    r = c['recall']['variants']; s = (c['scenario'] or {}).get('variants', [])
    if len(r) < 3: problems.append(f'{cid}: recall track has {len(r)} variants')
    if c['scenario'] and len(s) < 3: problems.append(f'{cid}: scenario track has {len(s)} variants')
    if len({v['id'] for v in r}) != len(r) or len({v['id'] for v in s}) != len(s): problems.append(f'{cid}: duplicate variant ids')
    for v in r:
      if v['type'] in ('cloze', 'code'):
        field = v['text'] if v['type'] == 'cloze' else v['code']
        if field.count('{{gap}}') != 1: problems.append(f'{cid}/{v["id"]}: needs exactly one gap')
      if v['type'] == 'occlusion' and v['mask'] not in c['diagrams'][v['diagram']]['labels']: problems.append(f'{cid}/{v["id"]}: bad mask')
      if v.get('src', 0) >= len(c['sources']): problems.append(f'{cid}/{v["id"]}: bad source index')
    for v in s:
      k = v['pick']
      if len(v['correct']) != k: problems.append(f'{cid}/{v["id"]}: pick {k} but {len(v["correct"])} correct')
      if not 4 <= len(v['distractors']) <= 6: problems.append(f'{cid}/{v["id"]}: distractor pool {len(v["distractors"])}')
      allo = v['correct'] + v['distractors']
      if any(not o.get('why') for o in allo): problems.append(f'{cid}/{v["id"]}: option without explanation')
      if any(re.search(r'all of the above|none of the above', o['text'], re.I) for o in allo): problems.append(f'{cid}/{v["id"]}: “of the above” option')
      L = [len(re.sub(r'`', '', o['text'])) for o in allo]
      ratio = max(L) / min(L)
      if ratio > 2.2: notes.append(f'{cid}/{v["id"]}: option length ratio {ratio:.1f}')
      if v.get('flip'):
        mate = next((x for x in s if x['id'] == v['flip']), None)
        if not mate or mate.get('flip') != v['id']: problems.append(f'{cid}/{v["id"]}: flip partner {v["flip"]} missing or not paired back')
        elif {o['text'] for o in v['correct']} == {o['text'] for o in mate['correct']}: problems.append(f'{cid}/{v["id"]}: flip pair has the same answer')
      texts = [o['text'] for o in allo]
      if len(set(texts)) != len(texts): problems.append(f'{cid}/{v["id"]}: duplicate option text')
    for v in r + s:
      for k, t in prose_fields(v):
        bare = re.sub(r'`[^`]*`', '', t)
        if "'" in bare or '"' in bare: problems.append(f'{cid}/{v["id"]}.{k}: straight quote in prose: {bare[:60]}')
    for v in r + s:
      q = v.get('prompt') or v.get('text') or v.get('stem') or ''
      if not v.get('settingIsAnswer') and not any(t.lower() in q.lower() for t in c['setting']):
        problems.append(f'{cid}/{v["id"]}: prompt doesn’t name its setting ({" / ".join(c["setting"])})')
    for v in r:
      for ln in (v.get('code') or '').split('\n'):
        if len(ln.replace('{{gap}}', 'x' * 9)) > 40:
          problems.append(f'{cid}/{v["id"]}: code line over 40 characters, too wide for a phone: {ln[:45]}')
    if len(json.dumps(c)) > 200_000: problems.append(f'{cid}: document too large')
  for cid, c in C:
    ev = c.get('evidence')
    if ev is not None and (not isinstance(ev, list) or any(not (isinstance(e, list) and len(e) == 2 and isinstance(e[0], int)
        and 0 <= e[0] < len(c['sources']) and isinstance(e[1], str)) for e in ev)):
      problems.append(f'{cid}: evidence must be a list of [source index, regex] pairs')
    exam = c.get('exam', '')
    if exam == 'databricks-dea' and not cid.startswith('dea-'): problems.append(f'{cid}: id must start with dea-')
  return problems, notes

def summary(C):
  n_tracks = sum(1 + (1 if c.get('scenario') else 0) for _, c in C)
  n_var = sum(len(c['recall']['variants']) + len((c.get('scenario') or {}).get('variants', [])) for _, c in C)
  return f'{len(C)} concepts, {n_tracks} tracks, {n_var} variants'

if __name__ == '__main__':
  allc = json.load(open(sys.argv[1].rstrip('/') + '/all.json', encoding='utf-8'))
  C = sorted(((k.split('/', 1)[1], v) for k, v in allc.items() if k.startswith('concepts/') and v.get('status') != 'retired'), key=lambda x: x[1]['order'])
  for _, c in C: c.setdefault('scenario', None)
  problems, notes = check(C)
  print(summary(C))
  for n in notes: print('note:', n)
  if problems:
    print('PROBLEMS:'); [print(' -', p) for p in problems]; sys.exit(1)
  print('validator: no problems')
