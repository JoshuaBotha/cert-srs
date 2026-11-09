# Weekly-review workspace: the database is the master copy of content, and this edits a copy of it as JSON.
#   init <dump_dir> <ws>     copy exams/ and concepts/ from a read_db out_dir dump into <ws>/ (editable) and <ws>/base/ (as read),
#                            and write <ws>/all.json for validate.py, factcheck.py, play_chunk.js and shots_batch.py
#   build <ws>               rebuild <ws>/all.json after editing or adding files under <ws>/concepts/
#   diff <ws> <versions.json> list documents that differ from base/ or are new, and write <ws>/write_batches.json:
#                            write_db batch entries of at most 50, each existing document pinned with if_version from
#                            versions.json ({"concepts/<id>": n, ...}, the versions read_db reported for this run's read)
import json, os, shutil, sys
COLS = ('exams', 'concepts')
def load(d):
    out = {}
    for col in COLS:
        p = os.path.join(d, col)
        for f in sorted(os.listdir(p)) if os.path.isdir(p) else []:
            if f.endswith('.json'): out[f'{col}/{f[:-5]}'] = json.load(open(os.path.join(p, f), encoding='utf-8'))
    return out
def build(ws):
    allc = load(ws)
    json.dump(allc, open(os.path.join(ws, 'all.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(allc), 'documents in', os.path.join(ws, 'all.json'))
cmd = sys.argv[1]
if cmd == 'init':
    dump, ws = sys.argv[2], os.path.abspath(sys.argv[3])
    for col in COLS:
        for dst in (os.path.join(ws, col), os.path.join(ws, 'base', col)):
            shutil.rmtree(dst, ignore_errors=True); shutil.copytree(os.path.join(dump, col), dst)
    build(ws)
elif cmd == 'build':
    build(os.path.abspath(sys.argv[2]))
elif cmd == 'diff':
    ws = os.path.abspath(sys.argv[2]); ver = json.load(open(sys.argv[3], encoding='utf-8'))
    cur, base = load(ws), load(os.path.join(ws, 'base'))
    writes, changed, new = [], [], []
    for key, body in sorted(cur.items()):
        if base.get(key) == body: continue
        col, doc_id = key.split('/', 1)
        w = {'op': 'set', 'collection': col, 'doc_id': doc_id, 'file_path': os.path.join(ws, col, doc_id + '.json')}
        if key in base:
            assert key in ver, f'no version for {key}: add it to {sys.argv[3]} from this run\'s read'
            w['if_version'] = ver[key]; changed.append(key)
        else: new.append(key)
        writes.append(w)
    gone = sorted(set(base) - set(cur))
    assert not gone, f'documents removed from the workspace (deleting is held, never done here): {gone}'
    batches = [writes[i:i + 50] for i in range(0, len(writes), 50)]
    json.dump(batches, open(os.path.join(ws, 'write_batches.json'), 'w'), indent=1)
    print(f'{len(changed)} changed, {len(new)} new, {len(batches)} batch(es) in', os.path.join(ws, 'write_batches.json'))
    for k in changed: print('  changed', k)
    for k in new: print('  new', k)
else: sys.exit(__doc__)
