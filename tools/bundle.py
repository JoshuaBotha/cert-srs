"""Regenerate cert-srs-build.txt from the files git tracks.

The bundle is the one-text-file export of this repo for the claude.ai Project
(Project files don't accept zips). The repo is the source of truth; the bundle
is generated and git-ignored.

    python3 tools/bundle.py            # writes cert-srs-build.txt at the repo root

Format: HEADER below, then for each tracked file (git ls-files order) a line
"===== FILE: <path> | chars=<n> =====", exactly n characters of content and a
newline, then "===== END BUNDLE =====".
"""
import os
import subprocess
import sys

HEADER = '''Cert SRS build bundle — the cert-srs-build folder as one text file (Project files don't accept zip).
Each file below starts with a header line giving its path and exact length in characters.

To unpack in a Claude sandbox, run:

python3 - <<'UNPACK'
import glob, os, re
src = open(sorted(glob.glob('/mnt/project/*cert-srs-build*'))[0], encoding='utf-8').read()
i = src.index('\\n===== FILE: ') + 1
while not src.startswith('===== END BUNDLE =====', i):
    j = src.index('\\n', i)
    m = re.match(r'===== FILE: (.+) \\| chars=(\\d+) =====$', src[i:j])
    path, n = os.path.join('cert-srs-build', m.group(1)), int(m.group(2))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(src[j + 1:j + 1 + n])
    i = j + 1 + n + 1
print('unpacked into', os.path.abspath('cert-srs-build'))
UNPACK

Then follow cert-srs-build/README.md. The empty content/out/ folder is created when build_content.py runs.

'''
END = '===== END BUNDLE =====\n'
OUT = 'cert-srs-build.txt'


def git(root, *args):
    return subprocess.run(['git', '-C', root, *args], check=True, capture_output=True, text=True).stdout


def build(root, paths):
    parts = [HEADER]
    for p in paths:
        with open(os.path.join(root, p), encoding='utf-8', newline='') as f:
            body = f.read()
        parts.append(f'===== FILE: {p} | chars={len(body)} =====\n{body}\n')
    parts.append(END)
    return ''.join(parts)


def main():
    root = git(os.path.dirname(os.path.abspath(__file__)), 'rev-parse', '--show-toplevel').strip()
    paths = [p for p in git(root, 'ls-files', '-z').split('\0') if p]
    dirty = git(root, 'status', '--porcelain', '--untracked-files=no').strip()
    if dirty:
        print('warning: tracked files have uncommitted changes; the bundle uses the working tree:\n' + dirty, file=sys.stderr)
    text = build(root, paths)
    out = os.path.join(root, OUT)
    with open(out, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    print(f'{out}: {len(paths)} files, {len(text)} chars')


if __name__ == '__main__':
    main()
