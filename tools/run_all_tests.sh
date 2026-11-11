#!/bin/bash
# tools/run_all_tests.sh — run every test file in the repo, aggregate the
# exit codes, and report once. (Adversarial-review finding M18.)
#
# Before this existed there was no single command that ran the test estate.
# Each file had to be remembered and invoked by hand, so "the tests pass"
# meant "the tests I thought of passed", and a test file added by one agent
# was invisible to the next.
#
# What it does:
#   1. DISCOVERS tests rather than listing them: every agents/*/src/test_*.py.
#      A new test file is picked up with no edit here. A discovery that finds
#      fewer than MIN_TESTS files fails the run outright, so a bad glob, a
#      deleted test, or a rename can never look like a green suite.
#   2. Runs each in its own process from the repo root, capturing output and
#      wall time.
#   3. Treats the EXIT CODE as the verdict (M5/M6/M7 gave every file real
#      exit-code discipline), with a secondary net: output containing a
#      top-level `FAILED` or a Python traceback fails the test even if it
#      exited 0. That catches a regression IN the exit discipline itself.
#   4. Prints a one-line result per test, then the full output of anything
#      that failed, then a summary. Exits nonzero if anything failed.
#
# What it does NOT do: build. It runs against the artifacts committed in
# shared/build/ (their md5s are printed at the top of every run, so a result
# says which bits it was about). Several tests read those artifacts and pin
# them — if you changed a builder, rebuild before trusting a green run:
#   python3 agents/usecode-compiler/src/build_eusecode.py --full
#   python3 agents/map-populator/src/build_all_maps.py
# The full clean-room rebuild-and-verify path is tools/cleanroom_test.sh,
# which calls this script for its unit-test step.
#
# Usage:
#   tools/run_all_tests.sh                 # everything
#   tools/run_all_tests.sh flx map         # only tests whose path matches
#   tools/run_all_tests.sh -v              # stream every test's output
#   tools/run_all_tests.sh -l              # list discovered tests, run none

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Ratchet: 18 compiler tests + 6 map-pipeline tests. This may only go UP.
# If you deliberately remove a test file, lower it in the same commit and
# say why.
#   2026-07-25: 14
#   2026-07-26: 15 (test_png2shape.py)
#   2026-08-11: 24 — catch-up bump. The floor sat at 15 while nine test
#     files landed, so it stopped detecting removals. Recount with
#     `ls agents/*/src/test_*.py | wc -l` when you add one.
#   2026-08-12: 25 (test_multivalue_case.py), 26 (test_pt_period_constants.py)
#   2026-10-08: 43 — catch-up recount on adding test_schedule_destinations.py.
#   2026-10-09: 44 (test_map39_lane.py)
#   2026-10-11: 47 — recount (46) plus test_integration_state.py.
MIN_TESTS=47

VERBOSE=0
LIST_ONLY=0
PATTERNS=()

usage() {
    sed -n '2,40p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit "${1:-0}"
}

while [ $# -gt 0 ]; do
    case "$1" in
        -v|--verbose) VERBOSE=1 ;;
        -l|--list)    LIST_ONLY=1 ;;
        -h|--help)    usage 0 ;;
        -*)           echo "unknown option: $1" >&2; usage 2 ;;
        *)            PATTERNS+=("$1") ;;
    esac
    shift
done

cd "$REPO_DIR" || exit 2

# ── Discovery ────────────────────────────────────────────────────────────
ALL_TESTS=()
while IFS= read -r t; do
    [ -n "$t" ] && ALL_TESTS+=("$t")
done < <(ls agents/*/src/test_*.py 2>/dev/null | sort)

if [ "${#ALL_TESTS[@]}" -lt "$MIN_TESTS" ]; then
    echo "ERROR: discovered only ${#ALL_TESTS[@]} test file(s), expected at" >&2
    echo "       least $MIN_TESTS (MIN_TESTS in $0). Discovery is broken, or" >&2
    echo "       a test file was deleted without lowering the pin." >&2
    # bash 3.2 + `set -u`: expanding an EMPTY array is an "unbound variable"
    # error, so guard the listing on the count rather than iterating blind.
    if [ "${#ALL_TESTS[@]}" -gt 0 ]; then
        for t in "${ALL_TESTS[@]}"; do echo "         $t" >&2; done
    fi
    exit 2
fi

# Optional substring filter
TESTS=()
if [ "${#PATTERNS[@]}" -eq 0 ]; then
    TESTS=("${ALL_TESTS[@]}")
else
    for t in "${ALL_TESTS[@]}"; do
        for p in "${PATTERNS[@]}"; do
            case "$t" in *"$p"*) TESTS+=("$t"); break ;; esac
        done
    done
    if [ "${#TESTS[@]}" -eq 0 ]; then
        echo "ERROR: no test file matches: ${PATTERNS[*]}" >&2
        exit 2
    fi
fi

if [ "$LIST_ONLY" = "1" ]; then
    for t in "${TESTS[@]}"; do echo "$t"; done
    exit 0
fi

# ── Header ───────────────────────────────────────────────────────────────
md5_of() {
    if [ -f "$1" ]; then
        python3 -c "import hashlib,sys; print(hashlib.md5(open(sys.argv[1],'rb').read()).hexdigest())" "$1"
    else
        echo "MISSING"
    fi
}

echo "════════════════════════════════════════════════════════════"
echo "Lost Vale test estate — ${#TESTS[@]} of ${#ALL_TESTS[@]} discovered file(s)"
echo "════════════════════════════════════════════════════════════"
echo "  repo:      $REPO_DIR"
echo "  python:    $(python3 --version 2>&1)"
echo "  EUSECODE:  $(md5_of shared/build/EUSECODE.FLX)"
echo "  FIXED.DAT: $(md5_of shared/build/FIXED.DAT)"
echo

# ── Run ──────────────────────────────────────────────────────────────────
OUT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/lv-tests.XXXXXX")"
RESULTS=()
FAILED_TESTS=()
FAILED_LOGS=()
PASSED=0
TIMEFORMAT='%3R'

# A green run must never print these. `FAIL` alone is NOT usable as a marker:
# test_parser_all.py legitimately prints per-file "  FAIL  EALOGO.UNK" lines
# for its 23 pinned, known-unparseable sources while passing overall.
FAILURE_MARKERS='^FAILED|^Traceback \(most recent call last\)'

# `time`'s report goes to the enclosing shell's stderr, so it is collected
# via a file rather than a command substitution — capturing the substitution
# would swallow the test's own output instead of streaming it in -v mode.
TIME_FILE="$OUT_DIR/.time"

for t in "${TESTS[@]}"; do
    name="$(basename "$t")"
    log="$OUT_DIR/${name%.py}.log"

    if [ "$VERBOSE" = "1" ]; then
        echo
        echo "──── $name ────"
        { time python3 -u "$t" 2>&1 | tee "$log"; } 2>"$TIME_FILE"
        code="${PIPESTATUS[0]}"
    else
        { time python3 -u "$t" >"$log" 2>&1; } 2>"$TIME_FILE"
        code=$?
    fi
    dur="$(tail -1 "$TIME_FILE")"
    printf '  %-28s ' "$name"

    marker=""
    if grep -qE "$FAILURE_MARKERS" "$log"; then
        marker=" (output reports failure)"
    fi

    if [ "$code" -eq 0 ] && [ -z "$marker" ]; then
        PASSED=$((PASSED + 1))
        # The estate's own summary line, when it has one
        summary="$(grep -E 'passed|^OK[:!]|baseline|successfully|correct\.$' "$log" | tail -1 \
                   | sed 's/^[[:space:]]*//' | cut -c1-72)"
        printf 'PASS  %6ss  %s\n' "$dur" "$summary"
        RESULTS+=("PASS  $name")
    else
        if [ "$code" -eq 0 ]; then
            # Exit-discipline regression: the file said it failed but exited 0
            printf 'FAIL  %6ss  exit 0 but output reports failure\n' "$dur"
            RESULTS+=("FAIL  $name: exited 0 while reporting failure")
        else
            printf 'FAIL  %6ss  exit %d\n' "$dur" "$code"
            RESULTS+=("FAIL  $name: exit $code")
        fi
        FAILED_TESTS+=("$name")
        FAILED_LOGS+=("$log")
    fi
done

# ── Failure detail ───────────────────────────────────────────────────────
if [ "${#FAILED_TESTS[@]}" -gt 0 ] && [ "$VERBOSE" != "1" ]; then
    i=0
    while [ "$i" -lt "${#FAILED_TESTS[@]}" ]; do
        echo
        echo "────────────────────────────────────────────────────────────"
        echo "OUTPUT: ${FAILED_TESTS[$i]}"
        echo "────────────────────────────────────────────────────────────"
        cat "${FAILED_LOGS[$i]}"
        i=$((i + 1))
    done
fi

# ── Summary ──────────────────────────────────────────────────────────────
echo
echo "════════════════════════════════════════════════════════════"
if [ "${#FAILED_TESTS[@]}" -eq 0 ]; then
    echo "OVERALL: PASS — $PASSED/${#TESTS[@]} test file(s)"
    echo "════════════════════════════════════════════════════════════"
    rm -rf "$OUT_DIR"
    exit 0
fi

echo "OVERALL: FAIL — ${#FAILED_TESTS[@]}/${#TESTS[@]} test file(s) failed"
for line in "${RESULTS[@]}"; do
    case "$line" in FAIL*) echo "  $line" ;; esac
done
echo "════════════════════════════════════════════════════════════"
echo
echo "Logs kept at: $OUT_DIR"
exit 1
