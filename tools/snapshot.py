# Assemble a read_db dump (Artifact tool, out_dir) into one Cert SRS backup file, the same format the app's
# Settings > Back up writes, so the app can restore it. Usage: python3 snapshot.py <out_dir> <backup.json> [note]
import json, os, sys, time, datetime
src, dst = sys.argv[1], sys.argv[2]
note = sys.argv[3] if len(sys.argv) > 3 else 'chat snapshot'
CONTENT = ('exams', 'concepts', 'heldout')
content, private, uid = {}, {}, None
for root, _, files in os.walk(src):
    for f in sorted(files):
        if not f.endswith('.json'): continue
        rel = os.path.relpath(os.path.join(root, f), src)[:-5].replace(os.sep, '/')
        body = json.load(open(os.path.join(root, f), encoding='utf-8'))
        if rel.split('/')[0] in CONTENT: content[rel] = body
        elif rel.startswith('data/users/'):
            parts = rel.split('/'); uid = uid or parts[2]
            assert parts[2] == uid, 'more than one user in the dump'
            private['/'.join(parts[3:])] = body
def count(prefix): return sum(1 for k in private if k.startswith(prefix))
now = int(time.time() * 1000)
out = {'format': 'cert-srs-backup', 'version': 1, 'created': datetime.datetime.fromtimestamp(now / 1000, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
       'createdMs': now, 'source': note, 'uid': uid, 'content': dict(sorted(content.items())), 'private': dict(sorted(private.items())),
       'counts': {'concepts': sum(1 for k in content if k.startswith('concepts/')), 'heldout': sum(1 for k in content if k.startswith('heldout/')),
                  'tracks': count('state/tracks/'), 'reviews': count('state/reviews/'), 'flags': count('state/flags/'),
                  'notes': count('state/notes/'), 'mocks': count('state/mocks/')}}
json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=False)
print(dst, os.path.getsize(dst), 'bytes', out['counts'], 'private docs:', len(private), 'content docs:', len(content))
