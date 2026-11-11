#!/bin/bash
# lv.sh — one-command-per-attach debugger helper with no double-send and no
# stray `exit`. Every verb refocuses the window first.
DISP=:77
RUN=/run/user/1000/lv-playtest
LOG=$RUN/lv_run.log
CMDS=$RUN/commands.txt
win() { DISPLAY=$DISP xdotool search --class scummvm 2>/dev/null | tail -1; }
focus() { W=$(win); [ -n "$W" ] && DISPLAY=$DISP xdotool windowfocus "$W"; }
attached() { [ "$(tail -1 "$LOG")" = "debug> " ] || tail -1 "$LOG" | grep -q '^debug>'; }
attach() {
  focus
  local b=$(grep -c 'Debugger entered' "$LOG")
  DISPLAY=$DISP xdotool keydown ctrl keydown alt key d keyup alt keyup ctrl
  for _ in 1 2 3 4 5 6; do
    sleep 0.5
    [ "$(grep -c 'Debugger entered' "$LOG")" -gt "$b" ] && return 0
  done
  return 1
}
# q <command> : ensure attached, run one command, print the reply
q() {
  local before=$(wc -l < "$LOG")
  local bp=$(grep -c '^debug>' "$LOG")
  printf '%s\n' "$*" >> "$CMDS"
  for _ in $(seq 8); do
    sleep 0.4
    [ "$(grep -c '^debug>' "$LOG")" -gt "$bp" ] && { sleep 0.6; tail -n +$((before+1)) "$LOG" | grep -v 'FIRST egg\|below Z=0'; return 0; }
  done
  attach || { echo "ATTACH FAILED"; return 1; }
  for _ in $(seq 8); do
    sleep 0.4
    [ "$(grep -c '^debug>' "$LOG")" -gt "$bp" ] && { sleep 0.6; tail -n +$((before+1)) "$LOG" | grep -v 'FIRST egg\|below Z=0'; return 0; }
  done
  echo "NO REPLY"; return 1
}
pos() { q "ObjectManager::objectInfo 1" | grep -o 'Item 1 (class MainActor, shape 1), [0-9]*, ([-0-9]*, [-0-9]*, [-0-9]*)'; }
# detach: send exit, do NOT wait for a prompt (exit prints none), then prove
# the world is live by comparing two frames.
detach() {
  printf 'exit\n' >> "$CMDS"
  sleep 1.2
  local a=$(DISPLAY=$DISP import -window root png:- 2>/dev/null | md5sum)
  sleep 1.2
  local b=$(DISPLAY=$DISP import -window root png:- 2>/dev/null | md5sum)
  if [ "$a" = "$b" ]; then echo "WARNING: frames identical - world may still be PAUSED"; return 1; fi
  return 0
}
case "$1" in
  q)   shift; q "$@" ;;
  detach) detach ;;
  pos) pos ;;
  attach) attach ;;
  focus) focus ;;
  *) echo "usage: lv.sh q <cmd> | pos | attach | focus" ;;
esac
