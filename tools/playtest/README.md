# Driving ScummVM from an agent session, without stealing focus

Verified working 2026-07-26. This **supersedes** the note at the bottom of
`HANDOFF.md`, which concluded that driving the game requires taking focus with
`osascript`. It does not.

`osascript` sends to the frontmost app, and `orca computer press-key` activates
the target app before typing, so both take focus. `CGEvent.postToPid` delivers
input straight to a process's event queue and needs no activation. The whole
playtest below was driven with ScummVM in the background.

```bash
./build.sh                    # compile the four Swift helpers
./session.sh start            # launches ScummVM, wires stdin, starts the log
```

## Tools

| Tool | Does |
|---|---|
| `session.sh` | `start` / `stop` / `status` / `cmd` / `key` / `type` / `debugger` / `shot` / `log` |
| `postkey <pid> <keycode> [flags]` | one key |
| `postchord <pid> <keycode> <mods>` | key under real modifiers |
| `postmouse <pid> <x> <y> [move\|left\|double\|right]` | pointer, screen points |
| `winid <pid>` | `id x y w h` for the game window |
| `send.py` | `text` / `line` / `key` / `chord` / `cmd` |
| `talk_to.py` | locate an NPC sprite and click it, in one invocation |
| `shot.sh <out.png>` | window capture, cropped to a clean coordinate space |

`session.sh` is the front door and mirrors `tools/playtest-linux/session.sh`
verb for verb, so a procedure written against one runs on the other. It starts
ScummVM with stdin wired to a commands file, which is what makes `cmd` work
against a `--enable-text-console` build.

```bash
tools/playtest/session.sh start      # or LV_SCUMMVM=.../scummvm-lv-console/scummvm
tools/playtest/session.sh debugger
tools/playtest/session.sh status
```

`send.py` finds the running `scummvm-lv` itself; `LV_PID` overrides.

```bash
./send.py chord ctrl+alt d                             # open the debugger
./send.py cmd "Cheat::toggle"
./send.py cmd "MainActor::teleport 10 7936 6656 0"
./send.py key Up Up Left                               # walk
./shot.sh /tmp/now.png
```

## Three things that bite

**Modifier chords need real `flagsChanged` events.** Setting `.flags` on the key
event is not enough: SDL tracks modifier state from `flagsChanged`, so a
flags-only chord arrives as an unmodified key. This is why `Ctrl+Alt+D` reached
the game as a bare `d` in earlier attempts and the debugger never opened.
`postchord` presses and releases the modifiers around the key, accumulating
flags the way a real keyboard does.

**`::` cannot be typed into a background app, so use Tab.** ScummVM reads the
real character from `SDL_TEXTINPUT`, and macOS does not run text input for a
process that is not frontmost. It falls back to `mapKey`
(`backends/events/sdl/sdl2-events.cpp:161`), which uppercases `a`-`z` under
shift and returns every other key raw, so `:` comes out `;`. Attaching a
Unicode payload to the event with `keyboardSetUnicodeString` does *not* fix it
(that route was tried and dropped).

The console's Tab completion supplies the `::` instead. For `Cheat`,
`MainActor`, `UCMachine`, `Ultima8Engine`, `Kernel`, `GameMapGump` and
`ObjectManager`, the longest common prefix of the registered commands is exactly
`Class::`, so class-name + Tab always lands there. `send.py cmd` does this.
Adding a class to `TAB_SAFE_CLASSES` means checking that its commands share no
longer prefix. If a class had exactly one command, Tab would complete the whole
thing and the typed remainder would double up.

**Capture with `-l <window-id>`, never `-R`.** A screen-rect capture takes
whatever is topmost at those coordinates, which is the wrong window precisely
when ScummVM is in the background. `shot.sh` crops the 68px shadow padding so
image pixels equal window-frame points; add the window origin from
`winid <pid>` to get the screen points `postmouse` expects.

## What still needs a human

Nothing found yet for input. Reading is fully covered by `shot.sh` plus the
`--debuglevel=1` log. The one real constraint is that the mouse cursor position
is tracked by SDL from posted motion events, so always move before clicking.
`postmouse` does this on every call.

## See also

`tools/playtest-linux/session.sh` is the Linux equivalent. It gives ScummVM a
private Xvfb display where it is the only client, so plain `xdotool` works and
the focus problem this harness exists to solve does not arise.

Better still on either platform: build ScummVM with `--enable-text-console`
(`LV_SCUMMVM_DIR` and `LV_CONFIGURE_EXTRA` in `build_scummvm.sh` build a second
tree beside the normal one). That swaps the overlay console for a
`fgets(stdin)` loop at `gui/debugger.cpp:282`, so debugger commands are lines on
stdin and responses land in the log. It makes `TAB_SAFE_CLASSES`, the `SHIFTED`
table and `postchord` dead code for the debugger surface. `postkey`,
`postmouse` and `shot.sh` are still needed for gameplay input and capture.

## Lessons taken from the Linux harness

`tools/playtest-linux/` was written second and got several things right that
this one had wrong. Those fixes are now here too:

- **One instance, or fail.** `send.py find_pid()` refuses to run when more than
  one ScummVM is alive instead of silently picking the first. A stale instance
  ate the input while the fresh one's log was being read, and it invalidated a
  control run before anyone noticed.
- **`session.sh` owns the lifecycle.** Launch, log path and stdin plumbing were
  previously improvised per command, which is how the duplicate instance
  survived. Same verbs as the Linux script.
- **Engine data lookup.** `dists/engine-data/` is checked before the top of the
  build tree. `play.sh` only checks the top, which holds on a checkout where
  someone copied the `.dat` files up by hand and fails on a clean clone with a
  GUI error dialog and nothing in the log.
- **`winid` replaces `orca computer list-windows`.** orca reports "No windows
  found" when ScummVM is started from `session.sh`'s pipeline subshell, even
  though the window exists and AppleScript counts it.

The one not taken yet is the big one: on Linux the debugger is driven over
stdin, so `TAB_SAFE_CLASSES`, the `SHIFTED` table and `postchord` are all
unnecessary there. The same is available here and `session.sh cmd` already
speaks that protocol, but it needs the second build tree to exist.
