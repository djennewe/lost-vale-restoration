#!/bin/bash
# tools/integrate.sh — the integration cascade, in order, as one command.
#
# After any merge that touches usecode, maps, art or the ScummVM fork, these
# steps used to be run by hand, about ten times a session, and every one of
# them drifted at least once (TODO.md §7):
#
#   0. preflight refuse at once if a running game would be affected (below)
#   1. patch    the engine patch equals the fork's diff over the pinned base
#               (--fork regenerates it from the fork first)
#   2. build    tools/build_artifacts.sh: rebuild the six artifacts and
#               verify them against ARTIFACTS.sha256 (--record rewrites it)
#   3. pins     derive_map_pins.py: map_pins.json follows FIXED.DAT
#   4. engine   ./build_scummvm.sh: re-sync scummvm-lv/ to base + patch,
#               write the detection entry for THIS EUSECODE.FLX, make
#   5. install  ./install_lv.sh, then compare the installed bytes
#   6. harness  sync shared/u8-lv-patched (the playtest game dir; FIXED.DAT
#               lives there twice), then compare its bytes
#   7. estate   tools/run_all_tests.sh, which by now also checks steps 4-6
#               (test_integration_state.py)
#
# Each step checks its own result and the script stops at the first
# failure, naming the step and the fix. It ends with a summary: artifact
# hashes, md5-5000 and size, patch status, the estate result, and the
# installed and harness hashes. It is idempotent: a second run changes no
# file content and passes.
#
# A RUNNING GAME IS NEVER PULLED OUT FROM UNDER. A preflight lists every
# running scummvm. The engine step refuses while a process runs THIS
# tree's binary, and the install/harness steps refuse while a process has
# that game dir open (-p/--path). A playtest that restarts would come up on
# a new binary or new bytes mid-run. The preflight refuses before the
# build, and each step checks again. A verifier on a pinned copy elsewhere
# is unaffected and blocks nothing. --force overrides.
#
# Usage:
#   tools/integrate.sh               # verify: rebuild, must match ARTIFACTS
#   tools/integrate.sh --record      # deliberate artifact change: re-record
#   tools/integrate.sh --fork        # regenerate the patch from the fork first
#   tools/integrate.sh --no-engine   # skip build_scummvm.sh
#   tools/integrate.sh --no-install  # skip install_lv.sh
#   tools/integrate.sh --force       # run steps a live game would block
#
# Env: LV_SCUMMVM_DIR (the ScummVM tree, default scummvm-lv/),
#      LV_SCUMMVM_FORK (the fork, default scummvm-lv-console/).
# The skill: .claude/skills/integrate/SKILL.md

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

MODE=verify
ENGINE=1
INSTALL=1
FORK=0
FORCE=0
for arg in "$@"; do
    case "$arg" in
        --record)     MODE=record ;;
        --no-engine)  ENGINE=0 ;;
        --no-install) INSTALL=0 ;;
        --fork)       FORK=1 ;;
        --force)      FORCE=1 ;;
        -h|--help)    sed -n '2,46p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *)            echo "unknown option: $arg (see --help)" >&2; exit 2 ;;
    esac
done

cd "$REPO_DIR" || exit 2

LV_TOOL="$REPO_DIR/tools/lv_scummvm.py"
SCUMMVM_DIR="${LV_SCUMMVM_DIR:-$REPO_DIR/scummvm-lv}"
FORK_DIR="${LV_SCUMMVM_FORK:-$REPO_DIR/scummvm-lv-console}"
HARNESS="$REPO_DIR/shared/u8-lv-patched"
BUILD_DIR="$REPO_DIR/shared/build"
MANIFEST="$BUILD_DIR/ARTIFACTS.sha256"
PINS="agents/map-populator/src/map_pins.json"
ARTIFACTS=(TYPEFLAG.DAT U8SHAPES.FLX ANIM.DAT EUSECODE.FLX FIXED.DAT GLOB.FLX)
# artifact:path-under-a-game-dir. The install writes the first six; the
# harness also carries FIXED.DAT at its top level.
GAME_FILES=(EUSECODE.FLX:USECODE/EUSECODE.FLX U8SHAPES.FLX:STATIC/U8SHAPES.FLX
            TYPEFLAG.DAT:STATIC/TYPEFLAG.DAT ANIM.DAT:STATIC/ANIM.DAT
            FIXED.DAT:STATIC/FIXED.DAT GLOB.FLX:STATIC/GLOB.FLX)
HARNESS_FILES=("${GAME_FILES[@]}" FIXED.DAT:FIXED.DAT)

LOG_DIR="$(mktemp -d "${TMPDIR:-/tmp}/lv-integrate.XXXXXX")"
STEPS=(preflight patch build pins engine install harness estate)
declare -A RESULT
for s in "${STEPS[@]}"; do RESULT[$s]="not reached"; done
CURRENT=""

sha_of()   { sha256sum "$1" 2>/dev/null | awk '{print $1}'; }
want_of()  { grep -E "  $1\$" "$MANIFEST" | awk '{print $1}'; }

step() {
    CURRENT="$1"
    echo
    echo "── $1: $2"
}

# Run a command with its output in a per-step log; show the log tail if it
# fails. Returns the command's exit code.
logged() {
    local log="$LOG_DIR/$CURRENT.log"
    "$@" >>"$log" 2>&1
    local rc=$?
    [ "$rc" = 0 ] && return 0
    echo "   ...last 25 lines of $log:"
    tail -25 "$log" | sed 's/^/   | /'
    return $rc
}

summary() {
    echo
    echo "════════════════════════════════════════════════════════════"
    echo "Integration summary ($MODE)"
    echo "════════════════════════════════════════════════════════════"
    local a got want
    for a in "${ARTIFACTS[@]}"; do
        got="$(sha_of "$BUILD_DIR/$a")"; want="$(want_of "$a")"
        if [ -z "$got" ]; then
            printf '  %-13s MISSING\n' "$a"
        elif [ "$got" = "$want" ]; then
            printf '  %-13s %s  canonical\n' "$a" "$got"
        else
            printf '  %-13s %s  != canonical %s\n' "$a" "$got" "${want:0:16}"
        fi
    done
    if [ -f "$BUILD_DIR/EUSECODE.FLX" ]; then
        read -r md5 size < <(python3 "$LV_TOOL" values "$BUILD_DIR/EUSECODE.FLX")
        echo "  detection     md5-5000 $md5  size $size"
    fi
    for s in "${STEPS[@]}"; do
        printf '  %-13s %s\n' "$s" "${RESULT[$s]}"
    done
    local dirty
    dirty="$(git status --porcelain -- shared/build/ARTIFACTS.sha256 \
        shared/build/lv_manifest.json "$PINS" tools/scummvm-patches 2>/dev/null)"
    if [ -n "$dirty" ]; then
        echo "  to commit:"
        echo "$dirty" | sed 's/^/    /'
    fi
    echo "  logs          $LOG_DIR"
    echo "════════════════════════════════════════════════════════════"
}

fail() {
    RESULT[$CURRENT]="FAILED — $1"
    echo "   FAILED: $1"
    [ -n "${2:-}" ] && echo "   Fix: $2"
    summary
    echo "STOPPED at step '$CURRENT'. Later steps were not run."
    exit 1
}

# Compare a game dir with the canonical hashes. Prints the stale paths.
stale_paths() {   # <dir> <entries...>
    local dir="$1"; shift
    local e art rel
    for e in "$@"; do
        art="${e%%:*}"; rel="${e#*:}"
        [ "$(sha_of "$dir/$rel")" = "$(want_of "$art")" ] || echo "$rel"
    done
}

# ── Running games ───────────────────────────────────────────────────────
# One line per process named scummvm: pid, the binary it runs
# (/proc/PID/exe; a rebuilt binary reads "... (deleted)"), its game dir
# (-p DIR, --path=DIR or --path DIR, made absolute against its cwd), and
# its command line, tab-separated.
game_dir_of() {   # <pid>
    local prev="" a dir=""
    while IFS= read -r -d '' a; do
        case "$prev" in -p|--path) dir="$a" ;; esac
        case "$a" in --path=*) dir="${a#--path=}" ;; esac
        prev="$a"
    done < "/proc/$1/cmdline"
    [ -z "$dir" ] && return 0
    [ "${dir#/}" = "$dir" ] && dir="$(readlink "/proc/$1/cwd")/$dir"
    realpath -m "$dir"
}
scan_games() {
    GAMES="$(for pid in $(pgrep -x scummvm 2>/dev/null); do
        exe="$(readlink "/proc/$pid/exe" 2>/dev/null)"
        printf '%s\t%s\t%s\t%s\n' "$pid" "${exe% (deleted)}" \
            "$(game_dir_of "$pid" 2>/dev/null)" \
            "$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null)"
    done)"
}
scan_games

# Refuse while a running game has <path> as its binary (field 2) or its
# game dir (field 3). A pinned copy elsewhere matches neither. Called in
# the preflight (fail before the build) and again at the step (a session
# may have started during the build).
busy() {   # <what> <2|3> <path>
    local hits
    scan_games
    hits="$(printf '%s\n' "$GAMES" | awk -F'\t' -v f="$2" -v p="$(realpath -m "$3")" \
        'NF && $f == p')"
    [ -z "$hits" ] && return 0
    echo "   a running game uses $1:"
    printf '%s\n' "$hits" | sed 's/^/     pid /'
    if [ "$FORCE" = 1 ]; then
        echo "   --force given: continuing anyway"
        return 0
    fi
    fail "a running game uses $1" \
        "let the playtest finish (or have it run a pinned copy: cp the binary and game dir elsewhere), or pass --force"
}

echo "════════════════════════════════════════════════════════════"
echo "Lost Vale integration — $MODE"
echo "  repo     $REPO_DIR"
echo "  scummvm  $SCUMMVM_DIR"
echo "  fork     $FORK_DIR"
echo "  logs     $LOG_DIR"
echo "════════════════════════════════════════════════════════════"
TARGET="$(python3 "$LV_TOOL" install-target)"
step preflight "running games"
if [ -n "$GAMES" ]; then
    echo "   WARNING: ScummVM is running. Steps that would change what it runs"
    echo "   refuse (see --force). Running now:"
    printf '%s\n' "$GAMES" | sed 's/^/     pid /'
    # Refuse here, before a five-minute build, not at the step itself.
    [ "$ENGINE" = 1 ] && busy "$SCUMMVM_DIR/scummvm" 2 "$SCUMMVM_DIR/scummvm"
    [ "$INSTALL" = 1 ] && busy "the install dir $TARGET" 3 "$TARGET"
    [ -d "$HARNESS" ] && busy "the harness dir $HARNESS" 3 "$HARNESS"
    RESULT[preflight]="$(printf '%s\n' "$GAMES" | grep -c .) game(s) running; none uses what this run changes"
    [ "$FORCE" = 1 ] && RESULT[preflight]="game(s) running; --force"
else
    RESULT[preflight]="no ScummVM running"
fi
echo "   ${RESULT[preflight]}"

# ── 1. patch ────────────────────────────────────────────────────────────
step patch "engine patch vs the fork"
if [ "$FORK" = 1 ]; then
    [ -d "$FORK_DIR/.git" ] || fail "--fork given but $FORK_DIR is not a git checkout" \
        "set LV_SCUMMVM_FORK to the fork, or drop --fork"
    logged python3 "$LV_TOOL" patch-regen "$FORK_DIR" || fail "could not regenerate the patch from $FORK_DIR"
    sed 's/^/   /' "$LOG_DIR/patch.log"
fi
if [ -d "$FORK_DIR/.git" ]; then
    logged env LV_SCUMMVM_FORK="$FORK_DIR" python3 agents/usecode-compiler/src/test_scummvm_patch_sync.py \
        || fail "tools/scummvm-patches/0001-lost-vale-engine.patch differs from the fork diff" \
                "the fork gained a commit: rerun with --fork, then commit the patch"
    RESULT[patch]="equals the fork diff ($(grep -c '^diff --git' tools/scummvm-patches/0001-lost-vale-engine.patch) files)"
    [ "$FORK" = 1 ] && grep -q regenerated "$LOG_DIR/patch.log" \
        && RESULT[patch]="REGENERATED from the fork, ${RESULT[patch]}"
else
    RESULT[patch]="not checked: no fork at $FORK_DIR"
fi
echo "   ${RESULT[patch]}"

# ── 2. build ────────────────────────────────────────────────────────────
if [ "$MODE" = record ]; then
    step build "tools/build_artifacts.sh --record (rewrites ARTIFACTS.sha256)"
    logged tools/build_artifacts.sh --record || fail "build_artifacts.sh --record failed" \
        "read the log; a builder failed"
    moved="$(git diff --numstat -- shared/build/ARTIFACTS.sha256 2>/dev/null | awk '{print $1}')"
    RESULT[build]="RECORDED ARTIFACTS.sha256 (${moved:-0} line(s) changed; review the diff)"
else
    step build "tools/build_artifacts.sh (rebuild, verify against ARTIFACTS.sha256)"
    logged tools/build_artifacts.sh || fail "the rebuilt artifacts do not match ARTIFACTS.sha256" \
        "if the change was intended, rerun with --record (the /artifact-rehash skill); otherwise a builder changed behaviour"
    RESULT[build]="rebuilt; all ${#ARTIFACTS[@]} match ARTIFACTS.sha256"
fi
echo "   ${RESULT[build]}"

# ── 3. pins ─────────────────────────────────────────────────────────────
step pins "derive_map_pins.py ($PINS)"
cp "$PINS" "$LOG_DIR/map_pins.before.json" 2>/dev/null || : > "$LOG_DIR/map_pins.before.json"
logged python3 agents/map-populator/src/derive_map_pins.py || fail "derive_map_pins.py failed"
# The file carries the date it was generated. A run whose only change is
# that date restores the old file, so a no-op run stays a no-op.
pins_state="$(python3 - "$LOG_DIR/map_pins.before.json" "$PINS" <<'EOF'
import json, sys
def load(p):
    try:
        d = json.load(open(p))
    except (OSError, ValueError):
        return None
    d.pop('generated', None)
    return d
print('same' if load(sys.argv[1]) == load(sys.argv[2]) else 'changed')
EOF
)"
if [ "$pins_state" = same ]; then
    cp "$LOG_DIR/map_pins.before.json" "$PINS"
    RESULT[pins]="unchanged"
else
    RESULT[pins]="UPDATED — commit $PINS"
fi
echo "   ${RESULT[pins]}"

# ── 4. engine ───────────────────────────────────────────────────────────
DET="$SCUMMVM_DIR/engines/ultima/detection_tables.h"
if [ "$ENGINE" = 1 ]; then
    step engine "./build_scummvm.sh ($SCUMMVM_DIR)"
    busy "$SCUMMVM_DIR/scummvm" 2 "$SCUMMVM_DIR/scummvm"
    logged ./build_scummvm.sh || fail "build_scummvm.sh failed" "read the log"
    grep -E '^  (engine sources =|re-syncing|fork tree)|^    (rewrote|removed) ' "$LOG_DIR/engine.log" | sed 's/^/ /'
    python3 "$LV_TOOL" engine-check "$SCUMMVM_DIR" >/dev/null 2>&1 \
        || fail "$SCUMMVM_DIR is not base + patch after the build"
    python3 "$LV_TOOL" detection-check "$DET" >/dev/null 2>&1 \
        || fail "the detection entry in $DET does not match EUSECODE.FLX after the build"
    [ -x "$SCUMMVM_DIR/scummvm" ] || fail "no binary at $SCUMMVM_DIR/scummvm"
    resynced="$(grep -c '^    \(rewrote\|removed\)' "$LOG_DIR/engine.log")"
    RESULT[engine]="built; base + patch$([ "$resynced" -gt 0 ] && echo " (RE-SYNCED $resynced file(s))"); detection current"
else
    step engine "skipped (--no-engine)"
    if [ -f "$DET" ] && python3 "$LV_TOOL" detection-check "$DET" >/dev/null 2>&1; then
        RESULT[engine]="skipped (--no-engine); detection entry is current"
    elif [ -f "$DET" ]; then
        RESULT[engine]="skipped (--no-engine); detection entry is STALE — run without --no-engine"
    else
        RESULT[engine]="skipped (--no-engine); no tree at $SCUMMVM_DIR"
    fi
fi
echo "   ${RESULT[engine]}"

# ── 5. install ──────────────────────────────────────────────────────────
# (TARGET was resolved before the preflight.)
if [ "$INSTALL" = 1 ]; then
    step install "./install_lv.sh --in-place ($TARGET)"
    busy "the install dir $TARGET" 3 "$TARGET"
    logged ./install_lv.sh --in-place || fail "install_lv.sh failed" "read the log"
    stale="$(stale_paths "$TARGET" "${GAME_FILES[@]}")"
    [ -z "$stale" ] || fail "installed bytes differ from ARTIFACTS: $(echo $stale)"
    RESULT[install]="all ${#GAME_FILES[@]} installed files canonical ($TARGET)"
else
    step install "skipped (--no-install)"
    RESULT[install]="skipped (--no-install)"
fi
echo "   ${RESULT[install]}"

# ── 6. harness ──────────────────────────────────────────────────────────
if [ -d "$HARNESS" ]; then
    step harness "sync $HARNESS"
    busy "the harness dir $HARNESS" 3 "$HARNESS"
    synced=0
    for e in "${HARNESS_FILES[@]}"; do
        art="${e%%:*}"; rel="${e#*:}"
        [ -d "$(dirname "$HARNESS/$rel")" ] || fail "$HARNESS/$(dirname "$rel") is missing"
        if ! cmp -s "$BUILD_DIR/$art" "$HARNESS/$rel"; then
            cp "$BUILD_DIR/$art" "$HARNESS/$rel" || fail "could not copy $art to $HARNESS/$rel"
            echo "   synced $rel <- shared/build/$art"
            synced=$((synced + 1))
        fi
    done
    # u8monsters.ini is not a build artifact: install_lv.sh writes it into
    # the game dir (engine rows + the LV monsters 872/873). The harness needs
    # the same file, or the LV monsters lose their stats there.
    if [ -f "$TARGET/u8monsters.ini" ] \
            && ! cmp -s "$TARGET/u8monsters.ini" "$HARNESS/u8monsters.ini"; then
        cp "$TARGET/u8monsters.ini" "$HARNESS/u8monsters.ini" \
            || fail "could not copy u8monsters.ini to $HARNESS"
        echo "   synced u8monsters.ini <- $TARGET"
        synced=$((synced + 1))
    fi
    stale="$(stale_paths "$HARNESS" "${HARNESS_FILES[@]}")"
    [ -z "$stale" ] || fail "harness bytes differ from ARTIFACTS: $(echo $stale)"
    if [ -f "$TARGET/u8monsters.ini" ] \
            && ! cmp -s "$TARGET/u8monsters.ini" "$HARNESS/u8monsters.ini"; then
        fail "harness u8monsters.ini differs from $TARGET/u8monsters.ini"
    fi
    RESULT[harness]="all ${#HARNESS_FILES[@]} harness files canonical, u8monsters.ini synced ($synced synced)"
else
    step harness "skipped: no $HARNESS"
    RESULT[harness]="absent (no shared/u8-lv-patched here)"
fi
echo "   ${RESULT[harness]}"

# ── 7. estate ───────────────────────────────────────────────────────────
step estate "tools/run_all_tests.sh"
rc=0
if [ "$INSTALL" = 0 ]; then
    logged env LV_SKIP_INSTALL_CHECK=1 tools/run_all_tests.sh || rc=$?
else
    logged tools/run_all_tests.sh || rc=$?
fi
overall="$(grep -E '^OVERALL:' "$LOG_DIR/estate.log" | tail -1)"
[ "$rc" = 0 ] || fail "${overall:-run_all_tests.sh exited $rc}" "read the failure detail in the log"
RESULT[estate]="${overall#OVERALL: }"
echo "   ${RESULT[estate]}"

summary
echo "RESULT: PASS"
exit 0
