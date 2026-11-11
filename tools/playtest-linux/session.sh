#!/bin/bash
# tools/playtest-linux/session.sh — run Lost Vale on a private X display.
#
# The macOS harness (tools/playtest/) exists to deliver input to ScummVM
# WITHOUT taking focus, which on macOS needs CGEvent.postToPid and three
# Swift helpers. On X11 the problem dissolves: give ScummVM a display of
# its own and it is the only client on it, permanently focused, so plain
# XTEST input (xdotool) is indistinguishable from hardware and nothing is
# ever taken from the user's desktop session.
#
#   session.sh start          launch Xvfb + ScummVM, skip the intro movie
#   session.sh stop           kill both
#   session.sh status         report what is running
#   session.sh key <keys...>  xdotool key, e.g. Escape / ctrl+alt+d / Up
#   session.sh type <text>    xdotool type
#   session.sh cmd <line>     write a line to the debugger's stdin (raw)
#   session.sh dbg <line>     send a debugger command AND wait for its reply
#                             — use this one; see the note on the verb
#   session.sh resume         detach the console so the game runs again
#                             (dbg leaves it attached, and attached = PAUSED)
#   session.sh debugger       open the debugger (ctrl+alt+d)
#   session.sh walk <dx> <dy> [secs]   walk the Avatar (see below)
#
# TWO TRAPS, both of which cost real time on 2026-07-28:
#
#   THE AVATAR WALKS ON THE RIGHT MOUSE BUTTON, not the left. U8's mover
#   sets MOVE_MOUSE_DIRECTION from _mouseButton[1] (u8_avatar_mover_process
#   .cpp), and left-drag is use/look — a held LEFT button makes the Avatar
#   turn on the spot and nothing else, which reads exactly like "input is
#   not reaching the game". Use the `walk` verb.
#
#   THE INTRO MOVIE COVERS THE WORLD. A fresh `start` comes up inside
#   StartU8Process's intro; debugger commands still work, teleports still
#   happen, screenshots show the movie and mouse input goes nowhere useful.
#   `start` now presses Escape a few times for you. If a session ever looks
#   inert, screenshot it before debugging anything else.
#
# Also: after any mouse interaction, run `xdotool windowfocus` before the
# ctrl+alt+d chord. There is no window manager on this display, so focus is
# not sticky and the chord silently misses.
#
# Env:
#   LV_DISPLAY   default :77
#   LV_GEOM      default 1450x873x24 (the virtual screen; the game window
#                itself is 640x480, which is the analysis space)
#   LV_SCUMMVM   which binary. Point it at scummvm-lv-console/scummvm to
#                get the --enable-text-console build, whose debugger reads
#                stdin (gui/debugger.cpp:282) instead of the in-game
#                overlay. With that binary `cmd` is the whole interface:
#                no synthetic keystrokes, no "::" problem, no Tab-completion
#                trick, and every response lands in the log.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DISP="${LV_DISPLAY:-:77}"
GEOM="${LV_GEOM:-1450x873x24}"
GAME_DIR="$REPO_DIR/shared/u8-lv-patched"
SCUMMVM="${LV_SCUMMVM:-$REPO_DIR/scummvm-lv/scummvm}"
RUN_DIR="${XDG_RUNTIME_DIR:-/tmp}/lv-playtest"
LOG="$RUN_DIR/lv_run.log"
# ScummVM's stdin is `tail -f` on this plain file rather than a fifo: a fifo
# needs a holder process to avoid EOF, and a plain file doubles as a record
# of everything the session was sent.
CMDS="$RUN_DIR/commands.txt"

mkdir -p "$RUN_DIR"

xvfb_pid() { pgrep -f "Xvfb $DISP " | head -1; }
# The ScummVM on THIS display: sessions on other displays run the same
# binary on the same game dir, and a bare pgrep made one session's `stop`
# kill another's game (2026-10-31, parallel captures).
game_pid() {
    local p
    for p in $(pgrep -f "scummvm.* -p $GAME_DIR"); do
        tr '\0' '\n' < "/proc/$p/environ" 2>/dev/null | grep -qx "DISPLAY=$DISP" \
            && { echo "$p"; return; }
    done
}
win_id()   { DISPLAY="$DISP" xdotool search --class scummvm 2>/dev/null | tail -1; }

need_display() {
    DISPLAY="$DISP" xdpyinfo >/dev/null 2>&1 || {
        echo "no X display $DISP — run: session.sh start" >&2; exit 1; }
}

case "${1:-status}" in
start)
    [ -x "$SCUMMVM" ] || { echo "no ScummVM binary at $SCUMMVM" >&2; exit 1; }
    [ -d "$GAME_DIR" ] || { echo "no patched game dir at $GAME_DIR" >&2; exit 1; }

    # Sync the five merged artifacts from shared/build/ before every launch.
    # install_lv.sh installs into shared/data/u8-install/, NOT here, so this
    # tree was maintained by hand and silently went stale — a playtest then
    # validates the wrong bytes with no visible symptom (found 2026-08-18,
    # and it bit again on 2026-09-13: a session looking for the new god
    # crystals was rendering the previous build's rock spires).
    BUILD_DIR="$REPO_DIR/shared/build"
    sync_one() {   # <artifact> <destination path under GAME_DIR>
        local src="$BUILD_DIR/$1" dst="$GAME_DIR/$2"
        [ -f "$src" ] || return 0
        [ -f "$dst" ] || return 0
        if ! cmp -s "$src" "$dst"; then
            cp "$src" "$dst" && echo "  synced $2 <- shared/build/$1"
        fi
    }
    echo "syncing artifacts into $(basename "$GAME_DIR")"
    sync_one FIXED.DAT    STATIC/FIXED.DAT
    sync_one FIXED.DAT    FIXED.DAT
    sync_one U8SHAPES.FLX STATIC/U8SHAPES.FLX
    sync_one TYPEFLAG.DAT STATIC/TYPEFLAG.DAT
    sync_one ANIM.DAT     STATIC/ANIM.DAT
    sync_one EUSECODE.FLX USECODE/EUSECODE.FLX

    if [ -z "$(xvfb_pid)" ]; then
        Xvfb "$DISP" -screen 0 "$GEOM" -nolisten tcp >"$RUN_DIR/xvfb.log" 2>&1 &
        for _ in $(seq 20); do
            DISPLAY="$DISP" xdpyinfo >/dev/null 2>&1 && break
            sleep 0.25
        done
    fi
    need_display
    echo "Xvfb $DISP up ($GEOM), pid $(xvfb_pid)"

    # The engine data files (ultima.dat, ultima8.dat) live in
    # dists/engine-data/ in a fresh build tree. play.sh looks for
    # ultima8.dat at the TOP of scummvm-lv/, which only works on a checkout
    # where someone copied it up by hand; a clean clone leaves it in dists/,
    # and ScummVM then dies in a GUI "Error" dialog with nothing in the log.
    SVM_DIR="$(dirname "$SCUMMVM")"
    EXTRA=()
    for d in "$SVM_DIR/dists/engine-data" "$SVM_DIR"; do
        if [ -f "$d/ultima.dat" ] || [ -f "$d/ultima8.dat" ]; then
            EXTRA=(--extrapath="$d"); break
        fi
    done

    : > "$CMDS"
    # No --fullscreen: there is no window manager on this display to honor
    # it, so SDL makes a normal 640x480 window, centres it on the virtual
    # screen, and then renders as though the surface were the full screen
    # size. Frames come out offset by the centring margin with the right
    # and bottom cropped. Windowed is correct.
    ( tail -f -n +1 "$CMDS" | DISPLAY="$DISP" "$SCUMMVM" --debuglevel=1 \
        "${EXTRA[@]}" -p "$GAME_DIR" ultima8 ) >"$LOG" 2>&1 &
    sleep 3
    PID="$(game_pid)"
    [ -n "$PID" ] || { echo "ScummVM died on startup; log:" >&2; tail -20 "$LOG" >&2; exit 1; }
    echo "ScummVM pid $PID ($(basename "$(dirname "$SCUMMVM")"))"
    # Skip the intro movie. Without this the session comes up with
    # StartU8Process's movie over the world: the debugger still answers and
    # teleports still land, but the game surface shows the movie and mouse
    # input does nothing, which is indistinguishable from a broken harness.
    sleep 2
    for _ in 1 2 3 4; do
        DISPLAY="$DISP" xdotool key --clearmodifiers Escape 2>/dev/null
        sleep 1
    done
    # Escaping the intro lands on the MODAL "Give thy name:" book. Until it
    # is answered the world is not drawn and mouse input goes nowhere, while
    # the debugger answers normally — so a session looks half-alive.
    DISPLAY="$DISP" xdotool type --delay 120 "Avatar"
    sleep 1
    DISPLAY="$DISP" xdotool key Return
    sleep 2
    DISPLAY="$DISP" xdotool key Return
    sleep 2
    echo "intro skipped, name entered (world should be up)"
    echo "log $LOG"
    echo "cmds $CMDS"
    ;;
stop)
    P="$(game_pid)"; [ -n "$P" ] && kill "$P" 2>/dev/null && echo "killed scummvm $P"
    pkill -f "tail -f -n \+1 $CMDS" 2>/dev/null
    # Belt and braces: a tail that survives a stop keeps holding the command
    # file open, and several of them at once is a real source of "the console
    # answered a moment ago and now does not". Kill any tail on THIS file,
    # by its full path: a basename match killed every concurrent session's
    # console feed (2026-10-30, three agents on separate displays).
    pkill -f "tail -f .*$CMDS" 2>/dev/null
    X="$(xvfb_pid)"; [ -n "$X" ] && kill "$X" 2>/dev/null && echo "killed Xvfb $X"
    ;;
status)
    echo "display  $DISP  $( DISPLAY=$DISP xdpyinfo >/dev/null 2>&1 && echo up || echo down )"
    echo "Xvfb     $(xvfb_pid || true)"
    echo "scummvm  $(game_pid || true)"
    echo "window   $(win_id || true)"
    echo "binary   $SCUMMVM"
    echo "log      $LOG"
    ;;
key)
    need_display; shift
    for k in "$@"; do DISPLAY="$DISP" xdotool key --clearmodifiers "$k"; sleep 0.15; done
    ;;
type)
    need_display; shift
    DISPLAY="$DISP" xdotool type --clearmodifiers --delay 90 "$*"
    ;;
debugger)
    need_display
    # `xdotool key ctrl+alt+d` does NOT reach the engine: SDL tracks
    # modifier state from the press/release stream, and a chord delivered
    # as one synthesized event leaves that state untouched, so the keymapper
    # never matches "C+A+d". Holding the modifiers around the key the way a
    # real keyboard does works. This is the same lesson as postchord on
    # macOS (tools/playtest/README.md, "Modifier chords need real
    # flagsChanged events") arriving by a different route.
    # No window manager here, so X input focus is not sticky: after any
    # mouse interaction the chord misses unless the window is refocused.
    W="$(win_id)"; [ -n "$W" ] && DISPLAY="$DISP" xdotool windowfocus "$W"
    DISPLAY="$DISP" xdotool keydown ctrl keydown alt key d keyup alt keyup ctrl
    sleep 1
    ;;
walk)
    # walk <dx> <dy> [seconds] — hold the RIGHT mouse button at an offset
    # from the centre of the 640x480 game surface, which is where the Avatar
    # stands. Direction is the 2:1 isometric basis (CORRECTED 2026-07-31 —
    # the old text here had it wrong and cost the playtest real time):
    # world +x -> screen (+2,+1), world +y -> screen (-2,+1). So:
    #   world N (-y) = dx +140 dy -70      world S (+y) = dx -140 dy +70
    #   world E (+x) = dx +140 dy +70      world W (-x) = dx -140 dy -70
    # Distance from centre sets speed (Mouse::getMouseLength), so keep the
    # offset well clear of the middle or the Avatar only turns.
    need_display; shift
    DX="${1:-0}"; DY="${2:-0}"; SECS="${3:-2}"
    W="$(win_id)"; [ -n "$W" ] && DISPLAY="$DISP" xdotool windowfocus "$W"
    # Game surface origin on the virtual screen, then its centre.
    eval "$(DISPLAY="$DISP" xdotool getwindowgeometry --shell "$W")"
    CX=$((X + WIDTH / 2 + DX)); CY=$((Y + HEIGHT / 2 + DY))
    DISPLAY="$DISP" xdotool mousemove "$CX" "$CY"
    sleep 0.3
    DISPLAY="$DISP" xdotool mousedown 3
    sleep "$SECS"
    DISPLAY="$DISP" xdotool mouseup 3
    echo "walked ${SECS}s toward (${DX},${DY}) from surface centre"
    ;;
dbg)
    # dbg <debugger command> — the reliable way to talk to the console.
    #
    # `cmd` alone is fire-and-forget: it appends to the command file, which
    # ScummVM only drains WHILE THE DEBUGGER IS ATTACHED. Anything sent
    # while it is closed queues up and executes later, out of order, the
    # next time it opens — including stale `exit` lines that close it again.
    # That backlog is what makes teleports silently not happen and
    # `Cheat::toggle` land on the wrong parity ("Cheats are disabled" with
    # no other clue). This verb attaches first if needed, sends one command,
    # and waits for the log to actually grow before returning.
    need_display; shift
    [ -e "$CMDS" ] || { echo "no session (missing $CMDS)" >&2; exit 1; }
    # Whether the console is attached CANNOT be read from the log: the
    # "debug>" prompt is the last line written whether it is still open or
    # was closed by a command that returns false (teleport, exit, and others
    # all do). So do not guess — send the command, and if nothing comes back,
    # attach and send it again. One retry is enough in practice.
    attach() {
        W="$(win_id)"; [ -n "$W" ] && DISPLAY="$DISP" xdotool windowfocus "$W"
        before_att="$(grep -c 'Debugger entered' "$LOG" 2>/dev/null)"
        DISPLAY="$DISP" xdotool keydown ctrl keydown alt key d keyup alt keyup ctrl
        for _ in 1 2 3 4 5; do
            sleep 1
            now_att="$(grep -c 'Debugger entered' "$LOG" 2>/dev/null)"
            [ "$now_att" -gt "$before_att" ] && return 0
        done
        return 1
    }
    send() {
        # Wait for a new DEBUGGER PROMPT, not just for the log to grow: the
        # engine spams warnings continuously (StartU8Process's "FIRST egg"
        # among them), so a plain line-count check reports success for a
        # command the console never even received.
        before="$(wc -l < "$LOG")"
        before_p="$(grep -c '^debug>' "$LOG" 2>/dev/null)"
        printf '%s\n' "$*" >> "$CMDS"
        for _ in 1 2 3 4 5 6 7 8 9 10; do
            sleep 0.5
            [ "$(grep -c '^debug>' "$LOG" 2>/dev/null)" -gt "$before_p" ] && return 0
        done
        return 1
    }
    if send "$@"; then
        # The first new prompt can be the ATTACH prompt rather than this
        # command's reply, so let the reply land before printing.
        sleep 1
        tail -n +"$((before + 1))" "$LOG" | grep -v 'FIRST egg' | head -20
    else
        attach
        if send "$@"; then
            sleep 1
            tail -n +"$((before + 1))" "$LOG" | grep -v 'FIRST egg' | head -20
        else
            echo "no response after attach+retry — screenshot the game, it is" >&2
            echo "probably showing a modal gump or a movie" >&2
            exit 1
        fi
    fi
    ;;
resume)
    # `dbg` leaves the console ATTACHED, and while it is attached the engine
    # is PAUSED: keystrokes and mouse drags sent then do nothing at all.
    # Every in-world interaction must be sandwiched: dbg ... ; resume ;
    # click/walk ; dbg ...
    [ -e "$CMDS" ] || { echo "no session (missing $CMDS)" >&2; exit 1; }
    printf 'exit\n' >> "$CMDS"
    sleep 1
    ;;
cmd)
    shift
    [ -e "$CMDS" ] || { echo "no session (missing $CMDS)" >&2; exit 1; }
    printf '%s\n' "$*" >> "$CMDS"
    sleep 0.6
    ;;
*)
    sed -n '2,30p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit 2
    ;;
esac
