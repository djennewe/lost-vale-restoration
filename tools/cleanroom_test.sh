#!/bin/bash
# tools/cleanroom_test.sh — Milestone 0 exit test.
#
# "clean-room rebuild (fresh clone plus game data) exits 0, produces
# identical artifacts twice in a row, and a scripted break-one-file run
# exits nonzero." (PLAN.md section 1)
#
# What it does:
#   1. Clones this worktree/repo into a temp dir (a true clean-room checkout:
#      no leftover build state, no absolute paths pointing back at the
#      source checkout).
#   2. Symlinks the real game data (shared/data/ is gitignored) into the
#      clone — the "plus game data" half of the exit test.
#   3. Runs `build_eusecode.py --full` twice; asserts exit 0 both times and
#      that the two runs produce byte-identical EUSECODE.FLX, and that run 1
#      matches the canonical hash in shared/build/ARTIFACTS.sha256.
#   3b. Runs `tools/build_artifacts.sh` to produce the other four artifacts
#      (TYPEFLAG.DAT, U8SHAPES.FLX, ANIM.DAT, FIXED.DAT) from the symlinked
#      game data and verify all five against their canonical hashes. Since M22 the
#      artifacts are no longer committed, so the clean room builds them the
#      way a player will.
#   4. Corrupts lv-new/MYTHRDLG.UNK, asserts the build exits nonzero with a
#      FAIL line naming MYTHRDLG, restores the file, asserts green again.
#   5. Asserts --stealth exits nonzero (M0.3: stealth is a retired stub).
#   6. Runs tools/run_all_tests.sh in the clone — the WHOLE test estate,
#      discovered rather than listed, so a test file added later is covered
#      here automatically (M18). All of it must pass.
#   7. Asserts shared/build/lv_manifest.json gained no new pins from any of
#      the green builds above (git status must be clean for that file).
#
# On success the temp clone is deleted. On failure it is left in place and
# the path is printed, for post-mortem.
#
# Usage: tools/cleanroom_test.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REAL_GAME_DATA="${LV_GAME_DATA:-$REPO_DIR/shared/data}"

TMPDIR="$(mktemp -d "${TMPDIR:-/tmp}/lv-cleanroom.XXXXXX")"
CLONE="$TMPDIR/lv-cleanroom"

RESULTS=()   # "PASS name" / "FAIL name: detail" lines for the final summary
OVERALL_OK=1

pass() { RESULTS+=("PASS  $1"); echo "PASS  $1"; }
fail() { RESULTS+=("FAIL  $1: $2"); echo "FAIL  $1: $2" >&2; OVERALL_OK=0; }

# Fatal assertion: records the failure, prints the summary, and exits.
# Used for setup steps where continuing would just cascade confusing
# secondary failures (clone, symlink, initial build).
die() {
    fail "$1" "$2"
    print_summary
    echo
    echo "Clean-room checkout left at: $CLONE"
    exit 1
}

md5_of() {
    python3 -c "import hashlib,sys; print(hashlib.md5(open(sys.argv[1],'rb').read()).hexdigest())" "$1"
}

# Runs build_eusecode.py --full in the clone. Prints its output, returns its
# exit code via $BUILD_EXIT, and captures full output in $BUILD_OUTPUT.
run_build() {
    set +e
    BUILD_OUTPUT="$(cd "$CLONE" && python3 agents/usecode-compiler/src/build_eusecode.py --full 2>&1)"
    BUILD_EXIT=$?
    set -e
    echo "$BUILD_OUTPUT"
}

print_summary() {
    echo
    echo "════════════════════════════════════════════════════════════"
    echo "Clean-room exit test summary"
    echo "════════════════════════════════════════════════════════════"
    for line in "${RESULTS[@]}"; do
        echo "  $line"
    done
    if [ "$OVERALL_OK" = "1" ]; then
        echo "────────────────────────────────────────────────────────────"
        echo "OVERALL: PASS"
    else
        echo "────────────────────────────────────────────────────────────"
        echo "OVERALL: FAIL"
    fi
    echo "════════════════════════════════════════════════════════════"
}

echo "== Clean-room test =="
echo "Source repo:  $REPO_DIR"
echo "Clone target: $CLONE"
echo

# ── Step 1: clone ────────────────────────────────────────────────────────
echo "-- Step 1: clone --"
if git clone "$REPO_DIR" "$CLONE" >/tmp/lv-cleanroom-clone.log 2>&1; then
    pass "clone"
else
    cat /tmp/lv-cleanroom-clone.log >&2
    die "clone" "git clone of $REPO_DIR failed"
fi

# ── Step 2: symlink game data ───────────────────────────────────────────
# shared/data/ is only *partially* gitignored: subpaths like USECODE.FLX,
# u8-install/, and lv-usecode/ are (see .gitignore), but a few tracked
# files (lv-screenshots/, INVENTORY.md) live directly under shared/data/
# too, so the clone's checkout already has a real shared/data/ directory
# containing those. `ln -s ... "$CLONE/shared/data"` onto an existing
# directory doesn't replace it — it nests the link inside as
# shared/data/data. The clone's shared/data/ is disposable (this is a
# throwaway temp clone), and the real one is a superset of it, so replace
# it outright rather than trying to merge.
echo
echo "-- Step 2: symlink game data --"
if [ ! -d "$REAL_GAME_DATA" ]; then
    die "symlink-data" "$REAL_GAME_DATA does not exist on this machine"
fi
rm -rf "$CLONE/shared/data"
ln -s "$REAL_GAME_DATA" "$CLONE/shared/data"
if [ -e "$CLONE/shared/data/USECODE.FLX" ]; then
    pass "symlink-data"
else
    die "symlink-data" "symlinked shared/data but USECODE.FLX is not visible through it"
fi

# ── Step 3: build twice, compare ────────────────────────────────────────
echo
echo "-- Step 3: build x2, compare artifacts --"

# M22: the artifacts are no longer committed, so there is no "the bytes in
# the clone" to compare against. The canonical hashes are, in
# shared/build/ARTIFACTS.sha256 — which is the stronger check anyway, since
# it pins all FOUR artifacts rather than only the FLX. Read the canonical
# FLX hash here; Step 3b verifies the full set after they are all built.
CANONICAL_SHA=""
if [ -f "$CLONE/shared/build/ARTIFACTS.sha256" ]; then
    CANONICAL_SHA="$(grep -E '  EUSECODE.FLX$' "$CLONE/shared/build/ARTIFACTS.sha256" | awk '{print $1}')"
fi
sha_of() { shasum -a 256 "$1" | awk '{print $1}'; }

echo "  build 1..."
run_build
echo "$BUILD_OUTPUT" | tail -20
if [ "$BUILD_EXIT" -eq 0 ]; then
    pass "build-1-exit-0"
else
    echo "$BUILD_OUTPUT" >&2
    die "build-1-exit-0" "build_eusecode.py --full exited $BUILD_EXIT on a clean, uncorrupted clone"
fi
MD5_1="$(md5_of "$CLONE/shared/build/EUSECODE.FLX")"

echo "  build 2..."
run_build
echo "$BUILD_OUTPUT" | tail -20
if [ "$BUILD_EXIT" -eq 0 ]; then
    pass "build-2-exit-0"
else
    echo "$BUILD_OUTPUT" >&2
    die "build-2-exit-0" "build_eusecode.py --full exited $BUILD_EXIT on the second run"
fi
MD5_2="$(md5_of "$CLONE/shared/build/EUSECODE.FLX")"

if [ "$MD5_1" = "$MD5_2" ]; then
    pass "run1-vs-run2-identical ($MD5_1)"
else
    die "run1-vs-run2-identical" "run 1 md5 $MD5_1 != run 2 md5 $MD5_2 — build is not reproducible"
fi

if [ -n "$CANONICAL_SHA" ]; then
    CLONE_SHA="$(sha_of "$CLONE/shared/build/EUSECODE.FLX")"
    if [ "$CANONICAL_SHA" = "$CLONE_SHA" ]; then
        pass "canonical-vs-run1-identical"
    else
        # Flagged loudly: a mismatch means either the path relativization
        # changed build behaviour (it must not), or the canonical hash was
        # not re-recorded after a deliberate artifact change.
        fail "canonical-vs-run1-identical" "canonical $CANONICAL_SHA != rebuilt $CLONE_SHA — INVESTIGATE; if the change was intended, rerun tools/build_artifacts.sh --record"
    fi
else
    fail "canonical-vs-run1-identical" "no EUSECODE.FLX line in shared/build/ARTIFACTS.sha256 to compare against"
fi

# ── Step 3b: build the other four artifacts ─────────────────────────────
# M22: FIXED.DAT, U8SHAPES.FLX and TYPEFLAG.DAT used to arrive with the
# clone. Now the clean room must produce them the way a player will — from
# owned game data — which is also what makes Step 6's map tests meaningful
# here at all.
echo
echo "-- Step 3b: build the remaining artifacts + verify all five --"
set +e
ARTIFACTS_OUTPUT="$(cd "$CLONE" && tools/build_artifacts.sh 2>&1)"
ARTIFACTS_EXIT=$?
set -e
echo "$ARTIFACTS_OUTPUT" | tail -12
if [ "$ARTIFACTS_EXIT" -eq 0 ]; then
    pass "build_artifacts.sh (all five match the canonical hashes)"
else
    fail "build_artifacts.sh" "exit=$ARTIFACTS_EXIT — see output above"
fi

# ── Step 4: break one file ──────────────────────────────────────────────
echo
echo "-- Step 4: break-one-file (corrupt lv-new/MYTHRDLG.UNK) --"

MYTHRDLG="$CLONE/agents/usecode-compiler/src/lv-new/MYTHRDLG.UNK"
python3 - "$MYTHRDLG" <<'PYEOF'
import sys
path = sys.argv[1]
with open(path) as f:
    content = f.read()
marker = 'They were called the Zealans'
idx = content.index(marker)
# Truncate mid-string-literal: no closing quote, no closing brace/paren,
# file just stops. Same class of defect as the documented TJORVI.UNK
# 1994 source bug (unterminated string).
truncated = content[:idx + 40]
with open(path, 'w') as f:
    f.write(truncated)
PYEOF
pass "corrupt-mythrdlg"

run_build
echo "$BUILD_OUTPUT" | tail -30
if [ "$BUILD_EXIT" -ne 0 ]; then
    pass "broken-build-exit-nonzero ($BUILD_EXIT)"
else
    echo "$BUILD_OUTPUT" >&2
    die "broken-build-exit-nonzero" "build exited 0 with a truncated MYTHRDLG.UNK in lv-new/ — M0.4 gate did not fire"
fi

if echo "$BUILD_OUTPUT" | grep -q "FAIL:.*MYTHRDLG"; then
    pass "broken-build-fail-line-names-mythrdlg"
else
    die "broken-build-fail-line-names-mythrdlg" "build exited nonzero but no 'FAIL: ...MYTHRDLG...' line was printed"
fi

echo "  restoring MYTHRDLG.UNK..."
(cd "$CLONE" && git checkout -- "agents/usecode-compiler/src/lv-new/MYTHRDLG.UNK")
if git -C "$CLONE" diff --quiet -- "agents/usecode-compiler/src/lv-new/MYTHRDLG.UNK"; then
    pass "restore-mythrdlg"
else
    die "restore-mythrdlg" "git checkout did not restore MYTHRDLG.UNK to a clean state"
fi

echo "  build after restore (must be green again)..."
run_build
echo "$BUILD_OUTPUT" | tail -20
if [ "$BUILD_EXIT" -eq 0 ]; then
    pass "build-after-restore-exit-0"
else
    echo "$BUILD_OUTPUT" >&2
    die "build-after-restore-exit-0" "build exited $BUILD_EXIT after restoring MYTHRDLG.UNK — restore did not actually fix it"
fi

# ── Step 5: --stealth is retired ────────────────────────────────────────
echo
echo "-- Step 5: --stealth exits nonzero --"
set +e
STEALTH_OUTPUT="$(cd "$CLONE" && python3 agents/usecode-compiler/src/build_eusecode.py --stealth 2>&1)"
STEALTH_EXIT=$?
set -e
echo "$STEALTH_OUTPUT" | head -5
if [ "$STEALTH_EXIT" -ne 0 ]; then
    pass "stealth-exit-nonzero ($STEALTH_EXIT)"
else
    die "stealth-exit-nonzero" "--stealth exited 0; M0.3 retirement stub is not wired up"
fi

# ── Step 6: the whole test estate ────────────────────────────────────────
echo
echo "-- Step 6: tools/run_all_tests.sh --"

# M18: this used to name three test files by hand, which meant the other
# eleven never ran in the clean room and a newly added test file was invisible
# here forever. The runner discovers agents/*/src/test_*.py, enforces its own
# minimum-count ratchet, and aggregates exit codes — including a check that a
# test reporting failure did not exit 0.
set +e
ESTATE_OUTPUT="$(cd "$CLONE" && tools/run_all_tests.sh 2>&1)"
ESTATE_EXIT=$?
set -e
echo "$ESTATE_OUTPUT"
ESTATE_LINE="$(echo "$ESTATE_OUTPUT" | grep -E '^OVERALL:' | tail -1)"
if [ "$ESTATE_EXIT" -eq 0 ]; then
    pass "run_all_tests.sh ($ESTATE_LINE)"
else
    fail "run_all_tests.sh" "exit=$ESTATE_EXIT, $ESTATE_LINE"
fi

# ── Step 7: manifest gained no new pins ─────────────────────────────────
echo
echo "-- Step 7: lv_manifest.json unchanged by the green builds --"
MANIFEST_STATUS="$(git -C "$CLONE" status --porcelain -- shared/build/lv_manifest.json)"
if [ -z "$MANIFEST_STATUS" ]; then
    pass "manifest-unchanged"
else
    fail "manifest-unchanged" "shared/build/lv_manifest.json is dirty after the green builds: $MANIFEST_STATUS"
fi

# ── Summary / cleanup ────────────────────────────────────────────────────
print_summary

if [ "$OVERALL_OK" = "1" ]; then
    rm -rf "$TMPDIR"
    exit 0
else
    echo
    echo "Clean-room checkout left at: $CLONE"
    exit 1
fi
