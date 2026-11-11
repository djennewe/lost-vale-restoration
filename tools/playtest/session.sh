#!/bin/bash
# tools/playtest/session.sh , macOS session manager for Lost Vale playtesting.
#
# Mirrors tools/playtest-linux/session.sh so the two platforms have the same
# verbs. The difference is only in how input is delivered:
#
#   Linux   private Xvfb display, ScummVM is the only client, xdotool
#   macOS   CGEvent.postToPid, delivered to a background process
#
# Neither takes focus. On macOS that property comes from postToPid; see
# README.md for why the obvious routes (osascript, orca press-key) do not.
#
#   session.sh start           launch ScummVM with stdin wired to a file
#   session.sh stop            kill it
#   session.sh status          what is running, and which binary
#   session.sh cmd <line>      write a line to the debugger's stdin
#   session.sh key <keys...>   send.py key
#   session.sh type <text>     send.py text
#   session.sh debugger        open the debugger (ctrl+alt+d)
#   session.sh shot [out.png]  capture the window
#   session.sh log [n]         tail the run log
#
# Env:
#   LV_SCUMMVM   which binary. Point it at scummvm-lv-console/scummvm to get
#                the --enable-text-console build, whose debugger reads stdin
#                (gui/debugger.cpp:282). With that binary `cmd` is the whole
#                debugger interface: no synthetic keystrokes, no "::" problem,
#                no Tab-completion trick, and every response lands in the log.
#                Build that second tree with:
#                  LV_SCUMMVM_DIR=$PWD/scummvm-lv-console \
#                  LV_CONFIGURE_EXTRA="--enable-text-console --disable-readline" \
#                  ./build_scummvm.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCUMMVM="${LV_SCUMMVM:-$REPO_DIR/scummvm-lv/scummvm}"
GAME_DIR="$REPO_DIR/shared/u8-lv-patched"
RUN_DIR="${TMPDIR:-/tmp}/lv-playtest"
LOG="$RUN_DIR/lv_run.log"
# Plain file rather than a fifo, same reasoning as the Linux harness: a fifo
# needs a holder process to avoid EOF, and a plain file doubles as a record of
# everything the session was sent.
CMDS="$RUN_DIR/commands.txt"

mkdir -p "$RUN_DIR"

# Exactly one pid, or fail loudly. A stale instance silently eats input while
# you read the fresh one's log, which invalidated a control run on 2026-07-26
# and was only caught because an argument count happened to break.
game_pids() { pgrep -f "scummvm-lv.*/scummvm" 2>/dev/null; }
game_pid() {
    local p; p="$(game_pids)"
    local n; n="$(printf '%s\n' "$p" | grep -c . )"
    if [ "$n" -gt 1 ]; then
        echo "ERROR: $n ScummVM instances running: $(echo $p | tr '\n' ' ')" >&2
        echo "  kill the stale one before trusting any observation" >&2
        return 2
    fi
    [ -n "$p" ] || return 1
    printf '%s' "$p"
}

case "${1:-status}" in
start)
    [ -x "$SCUMMVM" ] || { echo "no ScummVM binary at $SCUMMVM" >&2; exit 1; }
    [ -d "$GAME_DIR" ] || { echo "no patched game dir at $GAME_DIR" >&2; exit 1; }
    if game_pids | grep -q .; then
        echo "already running (pid $(game_pids | tr '\n' ' ')); stop first" >&2; exit 1
    fi

    # Engine data lives in dists/engine-data/ in a fresh build tree; play.sh
    # looks for it at the top of scummvm-lv/, which only holds on a checkout
    # where it was copied up by hand. Lesson from the Linux port: a clean
    # clone otherwise dies in a GUI error dialog with nothing in the log.
    SVM_DIR="$(dirname "$SCUMMVM")"
    EXTRA=()
    for d in "$SVM_DIR/dists/engine-data" "$SVM_DIR"; do
        if [ -f "$d/ultima.dat" ] || [ -f "$d/ultima8.dat" ]; then
            EXTRA=(--extrapath="$d"); break
        fi
    done

    : > "$CMDS"
    ( tail -f -n +1 "$CMDS" | "$SCUMMVM" --debuglevel=1 \
        "${EXTRA[@]}" -p "$GAME_DIR" ultima8 ) >"$LOG" 2>&1 &
    sleep 4
    P="$(game_pid)" || { echo "ScummVM died on startup; log:" >&2; tail -20 "$LOG" >&2; exit 1; }
    echo "ScummVM pid $P ($(basename "$SVM_DIR"))"
    echo "log  $LOG"
    echo "cmds $CMDS"
    if [ "$(basename "$SVM_DIR")" = "scummvm-lv-console" ]; then
        echo "text-console build: use \`cmd\` for the debugger"
    else
        echo "overlay build: \`cmd\` will NOT work; use \`debugger\` then \`type\`"
    fi
    ;;
stop)
    for P in $(game_pids); do kill "$P" 2>/dev/null && echo "killed scummvm $P"; done
    pkill -f "tail -f -n \+1 $CMDS" 2>/dev/null
    sleep 1
    game_pids | grep -q . && { echo "still alive, forcing"; pkill -9 -f "scummvm-lv.*/scummvm"; }
    exit 0
    ;;
status)
    P="$(game_pid)"; rc=$?
    if [ $rc -eq 2 ]; then exit 2; fi
    if [ -z "${P:-}" ]; then echo "not running"; exit 1; fi
    echo "scummvm pid $P"
    echo "binary $SCUMMVM"
    echo "log    $LOG ($(wc -l < "$LOG" 2>/dev/null || echo 0) lines)"
    command -v orca >/dev/null && orca computer list-windows --app scummvm 2>/dev/null | head -2
    ;;
cmd)
    shift
    game_pid >/dev/null || exit $?
    if [ "$(basename "$(dirname "$SCUMMVM")")" != "scummvm-lv-console" ]; then
        echo "WARNING: $SCUMMVM is not the text-console build; stdin is ignored." >&2
        echo "  Build it (see header) or use: session.sh debugger + type" >&2
    fi
    printf '%s\n' "$*" >> "$CMDS"
    sleep 0.5
    tail -5 "$LOG"
    ;;
key)    shift; game_pid >/dev/null || exit $?; "$SCRIPT_DIR/send.py" key "$@" ;;
type)   shift; game_pid >/dev/null || exit $?; "$SCRIPT_DIR/send.py" text "$*" ;;
debugger) game_pid >/dev/null || exit $?
          "$SCRIPT_DIR/postchord" "$(game_pid)" 2 ctrl,alt ;;
shot)   shift; "$SCRIPT_DIR/shot.sh" "${1:-$RUN_DIR/shot.png}" ;;
log)    shift; tail -n "${1:-40}" "$LOG" ;;
*)      sed -n '3,32p' "$0" ; exit 1 ;;
esac
