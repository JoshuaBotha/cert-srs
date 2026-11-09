"""Compare an Artifact read of the live page with a local file, byte for byte.

Publishing from Claude Code wraps the page in a one-line document skeleton
(first line, ending in <body>) and a trailing </body></html>. The read returns
that wrapper, so it is stripped before comparing.

    python3 tools/live_compare.py <saved live read> <local file>
"""
import difflib
import sys

SKELETON = '<!doctype html><html><head><meta charset=utf8>'
TAIL = '\n</body></html>'


def unwrap(s):
    if s.startswith(SKELETON):
        s = s[s.index('\n') + 1:]
        if s.endswith(TAIL):
            s = s[:-len(TAIL)]
    return s


def main(live_path, local_path):
    live = unwrap(open(live_path, encoding='utf-8', newline='').read())
    local = open(local_path, encoding='utf-8', newline='').read()
    if live == local:
        print(f'Live page is identical to {local_path}.')
        return 0
    sys.stdout.writelines(difflib.unified_diff(local.splitlines(True), live.splitlines(True), local_path, 'live'))
    print(f'\nLive page differs from {local_path}.')
    return 1


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
