#!/bin/bash
# dbg.sh <command...> — drive ScummVM's on-screen console with the keyboard.
# The stdin pipe stopped being consumed after the 2026-09-03 rebuild; the
# console takes keystrokes instead.
W=$(DISPLAY=:77 xdotool search --class scummvm | tail -1)
DISPLAY=:77 xdotool windowfocus "$W"; sleep 0.5
DISPLAY=:77 xdotool keydown ctrl keydown alt key d keyup alt keyup ctrl
sleep 1.2
DISPLAY=:77 xdotool type --window "$W" --delay 40 "$*"
sleep 0.4
DISPLAY=:77 xdotool key --window "$W" Return
sleep 1.5
DISPLAY=:77 xdotool type --window "$W" --delay 40 "exit"
sleep 0.3
DISPLAY=:77 xdotool key --window "$W" Return
sleep 1.0
