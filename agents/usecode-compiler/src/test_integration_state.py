#!/usr/bin/env python3
"""
test_integration_state.py — the parts of the integration cascade
(tools/integrate.sh, the /integrate skill) that can be checked offline.

After every merge that moved an artifact, the cascade used to be run by
hand, and each hand step drifted at least once: build_scummvm.sh's
hand-recorded detection values went stale for weeks, an existing
scummvm-lv/ was recompiled without the newer engine patch, and the playtest
harness ran stale bytes that looked exactly like a fix that did nothing.

Always checked (no game data needed):
  * build_scummvm.sh records no detection constants: LV_MD5/LV_SIZE are
    computed from shared/build/EUSECODE.FLX by tools/lv_scummvm.py;
  * that computation is md5(first 5000 bytes) + size, the entry update is
    bounded to the Lost Vale entry (vanilla entries untouched), and a
    SIZE-only change reads as stale (the old md5-only test missed it).

Checked when present, SKIPPED when absent (a fresh worktree has none):
  * shared/build/EUSECODE.FLX matches ARTIFACTS.sha256, and the Lost Vale
    entry in scummvm-lv/engines/ultima/detection_tables.h carries its
    md5-5000 and size;
  * scummvm-lv/'s engine sources are base + the tracked patch;
  * the harness dir shared/u8-lv-patched/ holds the canonical bytes in all
    seven places (FIXED.DAT twice);
  * the install target install_lv.sh writes to holds the canonical bytes —
    only once it has been installed into (a .bak exists) and this checkout
    has built artifacts (a worktree's copied u8-install is nobody's
    install). LV_SKIP_INSTALL_CHECK=1 skips it (integrate.sh --no-install).

The fork-vs-patch check is test_scummvm_patch_sync.py.

    python3 agents/usecode-compiler/src/test_integration_state.py

Plain script: exit 0 on pass/skip, 1 on fail.
"""

import hashlib
import os
import re
import sys
import tempfile

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SRC_DIR, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'tools'))
import lv_scummvm  # noqa: E402

BUILD = os.path.join(REPO_ROOT, 'shared', 'build')
MANIFEST = os.path.join(BUILD, 'ARTIFACTS.sha256')
SCUMMVM_DIR = os.environ.get('LV_SCUMMVM_DIR',
                             os.path.join(REPO_ROOT, 'scummvm-lv'))
HARNESS = os.path.join(REPO_ROOT, 'shared', 'u8-lv-patched')

# (artifact, path under a game directory). FIXED.DAT lives twice in the
# harness (top level and STATIC/); the install only writes STATIC/.
GAME_FILES = [('EUSECODE.FLX', 'USECODE/EUSECODE.FLX'),
              ('U8SHAPES.FLX', 'STATIC/U8SHAPES.FLX'),
              ('TYPEFLAG.DAT', 'STATIC/TYPEFLAG.DAT'),
              ('ANIM.DAT', 'STATIC/ANIM.DAT'),
              ('FIXED.DAT', 'STATIC/FIXED.DAT'),
              ('GLOB.FLX', 'STATIC/GLOB.FLX')]
HARNESS_FILES = GAME_FILES + [('FIXED.DAT', 'FIXED.DAT')]

passed = failed = skipped = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def skip(desc, why):
    global skipped
    skipped += 1
    print(f'  SKIP  {desc} — {why}')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def canonical():
    out = {}
    with open(MANIFEST) as fh:
        for line in fh:
            m = re.match(r'([0-9a-f]{64})  (\S+)$', line.strip())
            if m:
                out[m.group(2)] = m.group(1)
    return out


def check_game_dir(label, root, files, want):
    stale = []
    for art, rel in files:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            stale.append(f'{rel} missing')
        elif sha256(p) != want.get(art):
            stale.append(f'{rel} != canonical {art}')
    check(f'{label} ({root}) holds the canonical bytes in all '
          f'{len(files)} places', not stale,
          '; '.join(stale) + ' — run tools/integrate.sh')


print('=' * 70)
print('Integration state (tools/integrate.sh)')

# ── build_scummvm.sh computes, never records ─────────────────────────────
script = open(os.path.join(REPO_ROOT, 'build_scummvm.sh')).read()
recorded = re.findall(r'^\s*(LV_MD5|LV_SIZE)="?[0-9a-f]+"?\s*$', script,
                      re.M)
check('build_scummvm.sh hand-records no LV_MD5/LV_SIZE constant',
      not recorded, f'found {recorded}: these go stale on every usecode '
      f'change; compute them with tools/lv_scummvm.py values')
check('build_scummvm.sh computes them from EUSECODE.FLX via lv_scummvm.py',
      re.search(r'read -r LV_MD5 LV_SIZE < <\(python3 "\$LV_TOOL" values '
                r'"\$BUILD_FLX"\)', script) is not None)
check('build_scummvm.sh re-syncs an existing tree to base + patch',
      '"$LV_TOOL" engine-sync "$SCUMMVM_DIR"' in script)

# ── The computation itself, on synthetic bytes ───────────────────────────
with tempfile.TemporaryDirectory() as tmp:
    flx = os.path.join(tmp, 'EUSECODE.FLX')
    body = bytes(range(256)) * 40          # 10240 bytes
    with open(flx, 'wb') as fh:
        fh.write(body)
    md5, size = lv_scummvm.detection_values(flx)
    check('detection values are md5(first 5000 bytes) and the file size',
          (md5, size) == (hashlib.md5(body[:5000]).hexdigest(), len(body)))

    vanilla = ('\t\t\tAD_ENTRY2s("usecode/eusecode.flx", '
               '"c61f1dacde591cb39d452264e281f234", 1251108,\n')
    table = (vanilla + '\t// GOG Gold Edition + The Lost Vale expansion\n'
             '\t\t\tAD_ENTRY2s("usecode/eusecode.flx", "' + md5 + '", '
             + str(size) + ',\n')
    check('the Lost Vale entry is read, not the vanilla one before it',
          lv_scummvm.lv_entry(table) == (md5, size))

    with open(flx, 'ab') as fh:                  # append past byte 5000
        fh.write(b'\0' * 933)
    md5b, sizeb = lv_scummvm.detection_values(flx)
    check('a size-only change keeps md5-5000 and moves the size',
          md5b == md5 and sizeb == size + 933)
    check('...and the old entry then reads as stale',
          lv_scummvm.lv_entry(table) != (md5b, sizeb))
    updated = lv_scummvm.update_lv_entry(table, md5b, sizeb)
    check('the update rewrites only the Lost Vale entry',
          updated.startswith(vanilla)
          and lv_scummvm.lv_entry(updated) == (md5b, sizeb))

# ── The real artifacts, tree, harness and install ────────────────────────
want = canonical()
flx = os.path.join(BUILD, 'EUSECODE.FLX')
if not os.path.exists(flx):
    skip('shared/build/EUSECODE.FLX vs ARTIFACTS.sha256 and detection',
         'no built artifacts (fresh clone or worktree)')
else:
    check('shared/build/EUSECODE.FLX matches ARTIFACTS.sha256',
          sha256(flx) == want.get('EUSECODE.FLX'),
          'rebuild with tools/build_artifacts.sh (or --record if intended)')
    md5, size = lv_scummvm.detection_values(flx)
    det = os.path.join(SCUMMVM_DIR, lv_scummvm.DETECTION_REL)
    if not os.path.exists(det):
        skip(f'{det} carries md5-5000 {md5[:8]} size {size}',
             'no ScummVM tree here')
    else:
        have = lv_scummvm.lv_entry(open(det).read())
        check(f'detection entry in {os.path.relpath(det, REPO_ROOT)} is '
              f'md5-5000 {md5[:8]} size {size}', have == (md5, size),
              f'it is {have} — run ./build_scummvm.sh (tools/integrate.sh)')

if not os.path.isdir(os.path.join(SCUMMVM_DIR, '.git')):
    skip(f'{SCUMMVM_DIR} engine sources = base + patch', 'no ScummVM tree')
else:
    try:
        bad, n = lv_scummvm.engine_mismatches(SCUMMVM_DIR)
        check(f'{os.path.basename(SCUMMVM_DIR)}/ engine sources are base + '
              f'patch ({n} patched files)', not bad,
              f'{len(bad)} differ: {", ".join(f for f, _ in bad[:5])} — '
              f'run ./build_scummvm.sh, which re-syncs them')
    except RuntimeError as e:
        check(f'{SCUMMVM_DIR} engine sources = base + patch', False, str(e))

binary = os.path.join(SCUMMVM_DIR, 'scummvm')
if not os.path.exists(binary):
    skip(f'{binary} is newer than its engine sources', 'no binary')
else:
    # make's own rule: a source newer than the binary means the binary was
    # not rebuilt after it changed (e.g. build_eusecode.py rewrote the
    # detection entry, or the engine sync rewrote a patched file).
    with open(lv_scummvm.PATCH) as fh:
        sources = lv_scummvm.patch_files(fh.read())
    sources.append(lv_scummvm.DETECTION_REL)
    built = os.path.getmtime(binary)
    newer = [f for f in sources
             if os.path.exists(os.path.join(SCUMMVM_DIR, f))
             and os.path.getmtime(os.path.join(SCUMMVM_DIR, f)) > built]
    check(f'{os.path.basename(SCUMMVM_DIR)}/scummvm is newer than the '
          f'detection entry and every patched source', not newer,
          f'{len(newer)} newer: {", ".join(newer[:5])} — the binary is '
          f'stale; run ./build_scummvm.sh (tools/integrate.sh)')

if not os.path.isdir(HARNESS):
    skip('harness dir shared/u8-lv-patched holds the canonical bytes',
         'no harness dir in this checkout')
else:
    check_game_dir('harness dir', HARNESS, HARNESS_FILES, want)

target = lv_scummvm.install_target()
if os.environ.get('LV_SKIP_INSTALL_CHECK') == '1':
    skip('install target holds the canonical bytes',
         'LV_SKIP_INSTALL_CHECK=1 (integrate.sh --no-install)')
elif not os.path.exists(flx):
    skip('install target holds the canonical bytes',
         'no built artifacts here, so nothing of this checkout was installed')
elif not os.path.exists(os.path.join(target, 'USECODE', 'EUSECODE.FLX.bak')):
    skip('install target holds the canonical bytes',
         f'{target} was never installed into (no EUSECODE.FLX.bak)')
else:
    check_game_dir('install target', target, GAME_FILES, want)

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} '
      f'failed, {skipped} skipped')
sys.exit(1 if failed else 0)
