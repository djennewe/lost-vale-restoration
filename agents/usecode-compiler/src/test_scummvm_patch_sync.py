#!/usr/bin/env python3
"""
test_scummvm_patch_sync.py — tools/scummvm-patches/0001-lost-vale-engine.patch
still equals the fork diff it claims to be.

CLAUDE.md ("The ScummVM fork") says plainly that nothing tested this: the
patch is what actually travels (scummvm-lv-console/ has no remote to push
the `lost-vale` branch to, so a clean clone rebuilds the whole engine from
the patch alone), and it was found carrying only 3 of 7 changed files on
2026-08-18 — a fresh clone had been silently building without the loiter
leash and the AskGump dispatch. The regenerate command is documented but
nothing ran it to check:

    cd scummvm-lv-console
    git diff 01bd88796f47b21ce8e985a94a6c284439b6f032 HEAD -- engines/ \\
      ':!engines/ultima/detection_tables.h' > ../tools/scummvm-patches/0001-lost-vale-engine.patch

This test runs exactly that command (read-only: `git diff` and `git
cat-file -e`, nothing that writes to the fork) and byte-compares its output
against the committed patch file.

scummvm-lv-console/ is untracked and lives only in the MAIN checkout
(~/projects/lost-vale/scummvm-lv-console), per CLAUDE.md's
Coordination Protocol note that a worktree lacks it. So this test:

  * looks at $LV_SCUMMVM_FORK if set, else <repo root>/scummvm-lv-console;
  * SKIPS (exit 0, clear message) if that path is not a git worktree/repo
    at all — the common case inside an isolated agent worktree;
  * FAILS LOUDLY if the path exists but the pinned base commit is not
    reachable in it (a fork too shallow or too different to compare);
  * otherwise FAILS if the live diff and the committed patch disagree, and
    PASSES if they match byte-for-byte.

    python3 agents/usecode-compiler/src/test_scummvm_patch_sync.py

Plain script: exit 0 on pass/skip, 1 on fail.
"""

import os
import subprocess
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SRC_DIR, '..', '..', '..'))

FORK_DIR = os.environ.get('LV_SCUMMVM_FORK',
                          os.path.join(REPO_ROOT, 'scummvm-lv-console'))
PATCH = os.path.join(REPO_ROOT, 'tools', 'scummvm-patches',
                     '0001-lost-vale-engine.patch')
sys.path.insert(0, os.path.join(REPO_ROOT, 'tools'))
from lv_scummvm import BASE_SHA as BASE_COMMIT  # noqa: E402  the one pin
EXCLUDE = ':!engines/ultima/detection_tables.h'

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def run_git(args):
    """A read-only git call against the fork. Never mutates it."""
    return subprocess.run(['git', '-C', FORK_DIR] + args,
                          capture_output=True, text=True)


print('=' * 70)
print('tools/scummvm-patches/0001-lost-vale-engine.patch vs the fork diff')

if not os.path.isdir(os.path.join(FORK_DIR, '.git')):
    print(f'  {FORK_DIR} is not a git checkout — SKIPPING (expected inside '
          f'an isolated agent worktree; the fork lives only in the main '
          f'checkout, per CLAUDE.md). Set LV_SCUMMVM_FORK to point at it '
          f'to run this test for real.')
    sys.exit(0)

if not os.path.exists(PATCH):
    print(f'  {PATCH} is missing')
    sys.exit(1)

base_check = run_git(['cat-file', '-e', f'{BASE_COMMIT}^{{commit}}'])
check(f'pinned base commit {BASE_COMMIT[:8]} is reachable in the fork',
      base_check.returncode == 0,
      f'git cat-file -e failed: {base_check.stderr.strip()} — the fork is '
      f'too shallow, or missing the commit build_scummvm.sh applies the '
      f'patch over')

if base_check.returncode != 0:
    print()
    print('=' * 70)
    print(f'FAILED: {passed} passed, {failed} failed')
    sys.exit(1)

diff_result = run_git(['diff', BASE_COMMIT, 'HEAD', '--', 'engines/',
                       EXCLUDE])
check('`git diff` against the fork ran cleanly',
      diff_result.returncode == 0,
      f'git diff exited {diff_result.returncode}: '
      f'{diff_result.stderr.strip()}')

if diff_result.returncode == 0:
    with open(PATCH) as fh:
        committed = fh.read()
    live = diff_result.stdout

    check('committed patch is byte-identical to the live fork diff '
          '(engines/, detection_tables.h excluded)',
          committed == live,
          f'committed patch is {len(committed)} bytes, live diff is '
          f'{len(live)} bytes — regenerate with the command in CLAUDE.md '
          f'("The ScummVM fork") and commit the patch diff')

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)
