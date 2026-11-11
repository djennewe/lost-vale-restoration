#!/usr/bin/env python3
"""tools/lv_scummvm.py — the facts build_scummvm.sh and tools/integrate.sh
must never hand-edit: the ScummVM detection values, and whether a ScummVM
tree carries exactly base + the tracked engine patch.

Detection. ScummVM recognises the expansion by the md5 of the first 5000
bytes of USECODE/EUSECODE.FLX plus its size. Both move whenever the
compiled usecode moves, and build_scummvm.sh used to carry them as
hand-edited constants that went stale for weeks at a time. They are now
computed from shared/build/EUSECODE.FLX on every run.

Engine sync. build_scummvm.sh applied tools/scummvm-patches/ only when it
cloned a fresh tree, so an existing scummvm-lv/ was recompiled without any
newer patch and fork commits had to be copied in by hand. `engine-sync`
rewrites exactly the files that differ from base + patch, and refuses to
touch a fork (a tree with commits past the base), whose commits are where
the patch comes FROM.

    lv_scummvm.py base                        print the pinned upstream base SHA
    lv_scummvm.py values [FLX]                print "<md5-5000> <size>"
    lv_scummvm.py detection-check H [FLX]     exit 1 unless the Lost Vale entry
                                              in detection_tables.h H carries
                                              FLX's values
    lv_scummvm.py detection-update H [FLX]    rewrite that entry in place
                                              (exit 1 if H has no LV entry)
    lv_scummvm.py engine-check TREE           exit 1 unless TREE's engines/ is
                                              base + patch
    lv_scummvm.py engine-sync TREE            make it so (build trees only)
    lv_scummvm.py patch-check FORK            exit 1 unless the patch equals
                                              FORK's committed diff over base
    lv_scummvm.py patch-regen FORK            rewrite the patch from FORK
    lv_scummvm.py install-target              print the directory install_lv.sh
                                              installs into

FLX defaults to shared/build/EUSECODE.FLX; the patch to
tools/scummvm-patches/0001-lost-vale-engine.patch ($LV_ENGINE_PATCH
overrides it).
"""

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Upstream ScummVM commit the engine patch is generated against and applied
# over. The single copy: build_scummvm.sh and the tests read it from here.
# Bump it together with the patch (tools/scummvm-patches/README.md).
BASE_SHA = '01bd88796f47b21ce8e985a94a6c284439b6f032'

PATCH = os.environ.get('LV_ENGINE_PATCH', os.path.join(
    REPO_ROOT, 'tools', 'scummvm-patches', '0001-lost-vale-engine.patch'))
BUILD_FLX = os.path.join(REPO_ROOT, 'shared', 'build', 'EUSECODE.FLX')

# build_scummvm.sh / build_eusecode.py generate this file's Lost Vale entry,
# so it is never part of the patch or of the engine comparison.
DETECTION_REL = 'engines/ultima/detection_tables.h'
PATHSPEC = ['--', 'engines/', ':!' + DETECTION_REL]

# The Lost Vale entry's eusecode line. Bounded to the text after the
# 'Lost Vale' marker: the vanilla U8 variants list eusecode.flx too, and an
# unbounded match hits the first of them (that bug shipped once).
_ENTRY_RE = re.compile(r'("usecode/eusecode\.flx",\s*")([0-9a-f]{32})(",\s*)(\d+)')


# ── Detection ────────────────────────────────────────────────────────────

def detection_values(flx=BUILD_FLX):
    """(md5 of the first 5000 bytes, size) — what ScummVM matches on."""
    with open(flx, 'rb') as fh:
        head = fh.read(5000)
    return hashlib.md5(head).hexdigest(), os.path.getsize(flx)


def lv_entry(detection_text):
    """(md5, size) of the Lost Vale entry, or None if there is none."""
    pos = detection_text.find('Lost Vale')
    if pos < 0:
        return None
    m = _ENTRY_RE.search(detection_text, pos)
    return (m.group(2), int(m.group(4))) if m else None


def update_lv_entry(detection_text, md5, size):
    pos = detection_text.find('Lost Vale')
    if pos < 0:
        raise ValueError('no Lost Vale entry')
    tail, n = _ENTRY_RE.subn(rf'\g<1>{md5}\g<3>{size}',
                             detection_text[pos:], count=1)
    if n != 1:
        raise ValueError('Lost Vale entry has no eusecode.flx line')
    return detection_text[:pos] + tail


# ── Git helpers ──────────────────────────────────────────────────────────

def git(tree, *args, check=True, text=True):
    r = subprocess.run(['git', '-C', tree] + list(args),
                       capture_output=True, text=text)
    if check and r.returncode != 0:
        err = r.stderr if text else r.stderr.decode(errors='replace')
        raise RuntimeError(f'git {" ".join(args)} failed in {tree}: '
                           f'{err.strip()}')
    return r


def base_blob(tree, path):
    """File bytes at BASE_SHA, or None if the path is not in the base."""
    r = git(tree, 'show', f'{BASE_SHA}:{path}', check=False, text=False)
    return r.stdout if r.returncode == 0 else None


def patch_files(patch_text):
    files = []
    for line in patch_text.splitlines():
        m = re.match(r'diff --git a/(\S+) b/(\S+)$', line)
        if m:
            files.append(m.group(2))
    return files


def is_fork(tree):
    """A tree with commits past the base is a fork — the patch's source."""
    head = git(tree, 'rev-parse', 'HEAD').stdout.strip()
    return head != BASE_SHA


def require_base(tree):
    if not os.path.isdir(os.path.join(tree, '.git')):
        raise RuntimeError(f'{tree} is not a git checkout, so its engine '
                           f'sources cannot be compared with base + patch. '
                           f'Remove it and re-run build_scummvm.sh to clone '
                           f'a fresh one.')
    if git(tree, 'cat-file', '-e', f'{BASE_SHA}^{{commit}}',
           check=False).returncode != 0:
        raise RuntimeError(f'{tree} does not contain the pinned base '
                           f'{BASE_SHA[:8]}; it was cloned from another '
                           f'upstream commit. Remove it and re-run '
                           f'build_scummvm.sh.')


def expected_contents(tree, patch_path=None):
    """{path: bytes} for every file the patch touches, after applying it
    to the base blobs. Applied in a scratch directory, so `tree` is only
    read."""
    patch_path = patch_path or PATCH
    with open(patch_path) as fh:
        files = patch_files(fh.read())
    tmp = tempfile.mkdtemp(prefix='lv-engine-')
    try:
        for f in files:
            blob = base_blob(tree, f)
            if blob is not None:
                dst = os.path.join(tmp, f)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, 'wb') as fh:
                    fh.write(blob)
        # Outside any repository `git apply` patches plain files, relative
        # to the working directory. The ceiling stops discovery at tmp.
        env = {k: v for k, v in os.environ.items()
               if k not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE')}
        env['GIT_CEILING_DIRECTORIES'] = os.path.dirname(tmp)
        r = subprocess.run(['git', 'apply', '--whitespace=nowarn',
                            os.path.abspath(patch_path)],
                           cwd=tmp, capture_output=True, text=True, env=env)
        if r.returncode != 0:
            raise RuntimeError(f'{patch_path} does not apply to base '
                               f'{BASE_SHA[:8]}: {r.stderr.strip()}')
        out = {}
        for f in files:
            p = os.path.join(tmp, f)
            out[f] = open(p, 'rb').read() if os.path.exists(p) else None
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def engine_mismatches(tree, patch_path=None):
    """[(path, expected bytes or None)] for every engine file whose content
    is not base + patch. Covers the files the patch names and every file
    the tree changed from the base (tracked or untracked, not ignored)."""
    require_base(tree)
    expected = expected_contents(tree, patch_path)
    changed = set(git(tree, 'diff', '--name-only', BASE_SHA,
                      *PATHSPEC).stdout.split())
    changed |= set(git(tree, 'ls-files', '--others', '--exclude-standard',
                       *PATHSPEC).stdout.split())
    bad = []
    for f in sorted(set(expected) | changed):
        want = expected[f] if f in expected else base_blob(tree, f)
        p = os.path.join(tree, f)
        have = open(p, 'rb').read() if os.path.exists(p) else None
        if have != want:
            bad.append((f, want))
    return bad, len(expected)


def fork_diff(fork):
    return git(fork, 'diff', BASE_SHA, 'HEAD', *PATHSPEC).stdout


def install_target():
    """Where install_lv.sh installs: ScummVM's registered [ultima8] path if
    that directory exists, else shared/data/u8-install (install_lv.sh
    detect_scummvm_path and the fallback after check_prereqs)."""
    for prefs in (os.path.expanduser('~/Library/Preferences/'
                                     'ScummVM Preferences'),
                  os.path.expanduser('~/.config/scummvm/scummvm.ini')):
        if os.path.isfile(prefs):
            section = None
            with open(prefs, errors='replace') as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith('['):
                        section = line
                    elif section == '[ultima8]' and line.startswith('path='):
                        if os.path.isdir(line[5:]):
                            return line[5:]
                        break
            break
    return os.path.join(REPO_ROOT, 'shared', 'data', 'u8-install')


# ── Commands ─────────────────────────────────────────────────────────────

def cmd_engine(tree, sync):
    tree = os.path.abspath(tree)
    require_base(tree)
    if is_fork(tree):
        # The fork's COMMITS are where the patch comes from, so they are
        # compared with the patch and never overwritten.
        committed = fork_diff(tree)
        with open(PATCH) as fh:
            if fh.read() != committed:
                print(f'ERROR: {tree} is a fork (HEAD is past base '
                      f'{BASE_SHA[:8]}) and its committed engine diff does '
                      f'not equal {os.path.relpath(PATCH, REPO_ROOT)}.\n'
                      f'  The patch is stale: regenerate it with '
                      f'`tools/integrate.sh --fork` (or `{sys.argv[0]} '
                      f'patch-regen {tree}`) and commit it.', file=sys.stderr)
                return 1
        dirty = git(tree, 'diff', '--name-only', 'HEAD',
                    *PATHSPEC).stdout.split()
        print(f'  fork tree: committed engine diff equals the patch')
        if dirty:
            print(f'  WARNING: {len(dirty)} uncommitted engine file(s) in '
                  f'the fork will be compiled in but are NOT in the patch:')
            for f in dirty:
                print(f'    {f}')
        return 0

    bad, n = engine_mismatches(tree)
    if not bad:
        print(f'  engine sources = base {BASE_SHA[:8]} + patch '
              f'({n} patched files)')
        return 0
    if not sync:
        print(f'ERROR: {len(bad)} engine file(s) in {tree} differ from base '
              f'+ patch:', file=sys.stderr)
        for f, _ in bad:
            print(f'    {f}', file=sys.stderr)
        return 1
    print(f'  re-syncing {len(bad)} engine file(s) to base + patch:')
    for f, want in bad:
        p = os.path.join(tree, f)
        if want is None:
            os.remove(p)
            print(f'    removed  {f}')
        else:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'wb') as fh:
                fh.write(want)
            print(f'    rewrote  {f}')
    still, _ = engine_mismatches(tree)
    if still:
        print(f'ERROR: {len(still)} file(s) still differ after the re-sync: '
              f'{", ".join(f for f, _ in still)}', file=sys.stderr)
        return 1
    print(f'  engine sources = base {BASE_SHA[:8]} + patch ({n} patched '
          f'files)')
    return 0


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0 if argv else 2
    cmd, args = argv[0], argv[1:]
    try:
        if cmd == 'base':
            print(BASE_SHA)
        elif cmd == 'install-target':
            print(install_target())
        elif cmd == 'values':
            md5, size = detection_values(args[0] if args else BUILD_FLX)
            print(md5, size)
        elif cmd in ('detection-check', 'detection-update'):
            h = args[0]
            md5, size = detection_values(args[1] if len(args) > 1
                                         else BUILD_FLX)
            text = open(h).read()
            have = lv_entry(text)
            if cmd == 'detection-check':
                if have == (md5, size):
                    print(f'  detection entry current: md5={md5} '
                          f'size={size}')
                    return 0
                print(f'ERROR: detection entry in {h} is {have}, '
                      f'EUSECODE.FLX needs ({md5!r}, {size})',
                      file=sys.stderr)
                return 1
            if have is None:
                print(f'ERROR: no Lost Vale entry in {h}', file=sys.stderr)
                return 1
            with open(h, 'w') as fh:
                fh.write(update_lv_entry(text, md5, size))
            print(f'  updated Lost Vale detection entry: md5={md5} '
                  f'size={size} (was md5={have[0]} size={have[1]})')
        elif cmd in ('engine-check', 'engine-sync'):
            return cmd_engine(args[0], sync=(cmd == 'engine-sync'))
        elif cmd in ('patch-check', 'patch-regen'):
            fork = os.path.abspath(args[0])
            require_base(fork)
            live = fork_diff(fork)
            with open(PATCH) as fh:
                committed = fh.read()
            if live == committed:
                print(f'  patch equals the fork diff '
                      f'({len(patch_files(live))} files, {len(live)} bytes)')
                return 0
            if cmd == 'patch-check':
                print(f'ERROR: {os.path.relpath(PATCH, REPO_ROOT)} '
                      f'({len(committed)} bytes) differs from the fork diff '
                      f'({len(live)} bytes) — the fork gained a commit. '
                      f'Run tools/integrate.sh --fork.', file=sys.stderr)
                return 1
            with open(PATCH, 'w') as fh:
                fh.write(live)
            print(f'  regenerated the patch from {fork}: '
                  f'{len(patch_files(committed))} -> '
                  f'{len(patch_files(live))} files, {len(committed)} -> '
                  f'{len(live)} bytes (commit it)')
        else:
            print(f'unknown command: {cmd}', file=sys.stderr)
            return 2
    except (RuntimeError, ValueError, OSError, IndexError) as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
