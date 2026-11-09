# Content restore from a Cert SRS backup, done from chat because content is read-only to the app.
# Usage: python3 restore_content.py <backup.json> <out_dir>
# Writes one JSON file per content document (exams/, concepts/, heldout/) under <out_dir>/<collection>/<id>.json,
# plus write_batches.json: lists of {op:"set", collection, doc_id, file_path} of at most 50, ready for the
# Artifact tool's write_db "batch". Pin each existing document with if_version from a read_db first.
import json, os, sys
b = json.load(open(sys.argv[1], encoding='utf-8')); out = os.path.abspath(sys.argv[2])
assert b.get('format') == 'cert-srs-backup' and b.get('version') == 1, 'not a Cert SRS backup v1'
writes = []
for key, body in sorted((b.get('content') or {}).items()):
    col, doc_id = key.split('/', 1)
    assert col in ('exams', 'concepts', 'heldout') and '/' not in doc_id, key
    p = os.path.join(out, col, doc_id + '.json'); os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(body, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    writes.append({'op': 'set', 'collection': col, 'doc_id': doc_id, 'file_path': p})
batches = [writes[i:i + 50] for i in range(0, len(writes), 50)]
json.dump(batches, open(os.path.join(out, 'write_batches.json'), 'w'), indent=1)
print(len(writes), 'content documents in', len(batches), 'batch(es) under', out)
