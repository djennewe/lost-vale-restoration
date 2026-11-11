# Playtest traps

Every one of these cost real session time at least once. Recovered from
`HANDOFF.md` on 2026-08-11 before it was archived; original detail in
`docs/archive/HANDOFF-log-through-2026-07-31.md` and
`docs/playtest-2026-07-26-results.md`.

## Things that look exactly like "input is not reaching the game"

Four unrelated causes produce the identical symptom. **Screenshot first** —
it separates them in one step.

1. **The debugger is attached, and attached means PAUSED.** `dbg` leaves it
   attached. Keystrokes and mouse drags sent while it is attached do nothing
   whatsoever. Sandwich every in-world interaction: `dbg ...` → `resume` →
   click/walk/keys → `dbg ...`. This wasted most of an afternoon before the
   pattern was obvious.
2. **The intro movie is still up.** A fresh `start` comes up inside it. The
   debugger answers and teleports land, but the world is not drawn and mouse
   input goes nowhere. `start` presses Escape for you now, and also answers
   the modal "Give thy name:" book — without which the world is never drawn
   at all.
3. **The Avatar walks on the RIGHT mouse button.** A held *left* button makes
   him turn on the spot. Use the `walk` verb, which holds button 3.
4. **X focus is not sticky** — there is no window manager on the private
   display. Run `xdotool windowfocus` before the ctrl+alt+d chord after any
   mouse use.

Also verify `pgrep -f scummvm-lv/scummvm` returns exactly **one** pid. A stale
instance silently eats input while you read the fresh one's log.

## The harness directory is hand-fed (2026-09-15)

`install_lv.sh` writes into `shared/data/u8-install` (the base install; its
`.bak` copies are what the builders read as the pristine base). The harness
runs `shared/u8-lv-patched`, and nothing in the repo populates it. After a
rebuild, copy all five artifacts there by hand — `USECODE/EUSECODE.FLX`,
`STATIC/U8SHAPES.FLX`, `STATIC/TYPEFLAG.DAT`, `STATIC/ANIM.DAT` (since
2026-10-08: shape 867's animation, without which the Tiny Tar Avatar cannot
move), and `FIXED.DAT` in **both** places it exists (top level and
`STATIC/`) — then `session.sh stop`/`start`.
Check with `sha256sum` against `shared/build/`; a session on stale bytes
looks exactly like a change that did nothing. Since 2026-10-11
`tools/integrate.sh` does the copy and the check as its harness step, and
`test_integration_state.py` fails the estate while the harness is stale
(`/integrate`). It refuses the copy while a session has the dir open.

## A checkpoint carries its map's fixed items from the day it was saved (2026-10-10)

A save stores the current map's fixed items, so a checkpoint keeps every
placement as it was that day until the Avatar leaves the map and comes
back. Map 10 checkpoints from before 2026-10-07 still hold the Gunnar
still's workbench across the hut wall, and they logged 22,590 "Cycle in
paint" lines that the shipped FIXED.DAT does not produce
(`docs/research/2026-10-10-map10-paint-cycles.md`). Before judging any
placement, sort order or collision on an old checkpoint, hop to another
map and back. The numbers in a "Cycle in paint" line are shape numbers,
not object ids. Also, `run-s1-lbdone.sav` loads with the Avatar inside a
table: teleport him before the first move
(`docs/research/2026-10-10-lb-egg-freeze.md`).

## A left click just before a right hold is a jump (2026-10-11)

A left click less than 400 ms before a right-button hold makes the mover
see a double-click, and it sets MOVE_JUMP
(`u8_avatar_mover_process.cpp:436`). If the Avatar already faces the mouse
direction, he jumps at the land item under the pointer instead of running.
He can land on a palisade top and drop back outside a door. Facing any
other way, the turn swallows the jump, which looks like a "facing-dependent
stop". A driver that "primes" focus with a left click must wait at least
0.5 s before it holds the right button
(`docs/research/2026-10-11-ezrekal-door-run-stop.md`).

## `session.sh dbg` gets no reply on this build — use `dbg.sh` (2026-09-15)

The `dbg` verb writes to a command file the console stopped draining after
the 2026-09-03 rebuild (see the header of `tools/playtest-linux/dbg.sh`).
Every call returns "no response after attach+retry" whatever the game is
showing. `tools/playtest-linux/dbg.sh "<command>"` types the command into
the overlay console and exits it, and its replies land in `lv_run.log`.
Send `Cheat::toggle` first: until it lands, every `MainActor::teleport`
prints only `Cheats are disabled`. Verify a command by log growth, not by
the verb's exit code.

## A fresh `start` comes up with the backpack gump open (2026-09-15)

Three fresh starts in one session, three times the pack was over the
centre of the screen. Escape opens the pause book instead, and `i`
reopened it. A **double-click on the pack's own frame** closes it
(`ContainerGump::onMouseDouble` treats a double-click on the gump as `use`
on its owner). Clear it before any plate or any click test.

## The void is never cleared: set `usehighres=true` for plates at a map's edge (2026-09-15)

`Ultima8Engine::paint()` fills the frame black only when `_highRes` is set
(`ultima8.cpp:711`), and that comes from the `usehighres` config key. Without
it, wherever no item paints — the void beyond a map's terrain — the previous
frame's pixels stay. Plates of Map 17's cloud islands, which stand in void,
came back with the plaza, Map 18's hall and even earlier islands painted
around them, identical across three different teleports; it looked like
teleport residue and was not. `usehighres=true` under `[scummvm]` in
`~/.config/scummvm/scummvm.ini` (kept there since 2026-09-15) makes the void
black. The 640×400 canvas keys still apply. A player without that key sees
the same stale pixels beyond the Arrival Plaza's wall — HANDOFF carries that
as an open question.

## Clicks did not log on 2026-09-15

**Likely cause, found 2026-09-25: the Avatar was in combat mode.**
`GameMapGump::onMouseClick` and `onMouseDouble` both `break` on
`isInCombat()` before the `dumpInfo` line, so in combat (`objectInfo 1`
reads `flags: 800`) no click logs, barks, or uses anything.
`MainActor::toggleCombat` restores it. The combat mode itself usually
comes from the leaked `exit` below.

The "every click logs `dumpInfo()`" rule below held in earlier sessions
and did not hold in this one: with `Enabled debug flag 'Object'` in the
log, a single click on an item grew the log by 0 bytes. Take the plate
within 0.5 s of the click and use `ObjectManager::findShape` /
`objectInfo` for the item's identity instead of relying on the click line.

## Use `dbg`, never `cmd`

`cmd` is fire-and-forget: it appends to a file ScummVM drains only *while the
debugger is attached*. Anything sent while it is closed queues and executes
later, out of order — including stale `exit` lines that close it again.

That backlog is why teleports silently do not happen, and why `Cheat::toggle`
lands on the wrong parity, whose only symptom is `Cheats are disabled`.

`dbg` attaches if needed, sends one command, waits for the log to grow, and
prints the reply.

## Standard session setup

Add `debugflag_enable Object`. Every click then logs the clicked item's
`dumpInfo()`, which is the only reliable way to know what you hit — **the
cursor never reflects the item under it**, and barks render transiently at the
top viewport edge, so screenshot within ~0.5 s or you will falsely conclude
"no response".

## Item pickup: `Item::grab <objid>` first, the drag second

The fork's debugger has `Item::grab <objid>` (2026-09-24 finding): it puts
the item in the Avatar's pack by the same path a drag onto the Avatar
takes, with no pointer to land. Get the objid from `findShape`. Use it
unless the pickup itself is the thing under test. The drag recipe below
took four attempts on 2026-09-24 (pack open, out of reach, item hidden
behind the Avatar's own sprite); a release that lands on the Avatar as a
plain click opens the pack gump, or the LV debug menu.

## Item pickup by drag: follow this, don't improvise

Took a long time to establish (2026-07-28, corrected 2026-07-31):

1. Open the pack with `i`, drag the gump clear of the item by its brown frame.
2. Move the cursor onto the item, `mousedown 1`, **wait ~0.8 s**.
3. Move in small increments (~8 px) until the item lifts onto the cursor.
   Screenshot to confirm — a single big jump usually does NOT start a drag.
4. Release **on the Avatar's sprite**, not inside the open pack gump.
   Dropping onto the pack's dark interior gives a red-X refusal.

Verify with `total weight` from `ObjectManager::objectInfo 1`, not by eye. U8
weights are TYPEFLAG weight × 10, so a shield half is +40 and a sprawled
skeleton is +190.

**If the Avatar's back looks bare, restart the session.** An imprecise grab
can pull his own backpack off, after which `i` silently does nothing and the
ceremony's shield search cannot run at all.

## The shield halves sit under a skeleton, and the skeleton wins the click

`build_map_17` puts each half (shape **539**, small white studded shield)
64/32 units off a sprawled skeleton (shape **332**, a 2×3 `SF_CONTAINER` that
renders as a grey mass). They overlap on screen and the skeleton is the bigger
target. Two of them got carried around before the +190 weight gave it away.

The half is the **white studded shield, slightly below and right** of the grey
mass.

## The ceremony bails at a known instruction

With no halves in the pack, `EggShades::hatch` reaches **offset 0x1A1 (417)**
— the `ret` closing Ezrekal's "Bring the sacred shield" branch.

The elder teleport-ins are the three `calli 158` (`Actor::I_teleport`) at
0x1A8-0x1D6, right after `pop global 1106` (`inShadeScene`), so they are real
calls and would fire. The scene simply never gets there.

If a run ends with `shieldFixed`/`godsFree` still 0 and all three elders at
home coordinates, **that is this branch, not a teleport bug.**

Note the ceremony needs both halves in the **BACKPACK** — `SHADES.UNK` does
`foreach ... within container Avatar.getEquip(EQ_BACKPACK)`. Equipping is no
use.

## Locked doors

Use the key **on** the door: double-click key → target cursor → click door.
The door's own `use()` barking `Locked Door` is it working as intended, not a
bug.

## Other

- **Class ids are offset from FLX entries by two.** Use
  `UsecodeFlexArchive.get_class_data(classid)`, never raw `FlexArchive[i]`.
- **Village NPCs wander.** Use `talk_to.py`, which locates and clicks in one
  invocation.
- **Muting needs `mute=true` in both `[scummvm]` and `[ultima8]`**, and
  ScummVM rewrites its config on exit — edit with the game stopped.

## The text-console build is the better path

`--enable-text-console` sets `USE_TEXT_CONSOLE_FOR_DEBUGGER`, replacing the
in-game overlay with a `fgets(stdin)` loop (`gui/debugger.cpp:282`). Debugger
commands become stdin lines and every response lands in the log — no
screenshot-reading of console output.

```bash
LV_SCUMMVM_DIR=$PWD/scummvm-lv-console \
LV_CONFIGURE_EXTRA="--enable-text-console --disable-readline" ./build_scummvm.sh
LV_SCUMMVM=$PWD/scummvm-lv-console/scummvm tools/playtest-linux/session.sh start
```

Keep the normal `scummvm-lv/` for human play — the text-console build has no
overlay console.

## macOS

`tools/playtest/` delivers input via `CGEvent.postToPid`, so the game runs
while you work in other windows. Read its README first: modifier chords need
real `flagsChanged` events, `::` cannot be typed into a background app at all
(Tab completion supplies it), and captures must use
`screencapture -l <window-id>` rather than `-R`.

## Lessons of 2026-08-17 (the all-night steps 3-8 run)

- **Never let resume() write `exit` before testing the console.** The old
  nav.resume() stacked 53 stale exits in one evening; every attach then died
  instantly on the next one. nav.py now tests first (query answered → one
  exit). If the queue is ever poisoned anyway: append a
  `UCMachine::getGlobal 0x7FE 1` sentinel and chord in a loop until its
  output appears (each attach burns the queue up to the next stale exit).
- **`debugflag_enable Object` does not survive loadGame.** Re-enable after
  every load, or every probe silently returns [] and you will chase click
  ghosts for an hour.
- **A debug teleport onto an LV map skips EggReapply.** FIXED.DAT reloads
  on every map entry, and the arrival-pad eggs (`lv-new/REAPPLY.UNK`)
  remove used and carried quest items and keep destroyed pillars down.
  Teleport in off a pad and you see duplicate talismans, Shield halves or
  potions, and destroyed pillars standing again; that is not a defect.
  Walk onto a pad before counting them
  (`docs/playtest-2026-10-31-talisman-reentry.md`).
- **pos() can leave the console attached (world paused).** Before a
  hands-off scene watch, verify the world is LIVE by comparing two
  screenshot md5s 2-3 s apart — log growth is not proof, and a paused U8
  frame is pixel-identical.
- **Stale frames lie.** When the engine pauses mid-scene the last painted
  frame lingers; aiming clicks against it misses by 100+ px. Force a
  repaint with `InverterProcess::invertScreen` (capture between two calls,
  PIL-invert to read it), then re-aim.
- **After ANY death: reload a save.** The continue state renders the Avatar
  as garbage (bad frame, invisible, unclickable), the death book refuses
  Escape while the Avatar is dead (menu_gump.cpp guard), and blind clicks
  on the book start the CREDITS, which ignore synthetic Escape. Recovery:
  `Ultima8Engine::loadGame` → chooser → double-click the slot thumbnail →
  one Escape for the reopened book.
- **Teleports wedge.** Landings snap to chunk seams and/or settle below the
  floor, leaving the Avatar walking in place (`event 18` justMoved spam,
  zero displacement, all four directions). Always follow a positioning
  teleport with a mobility check (one walk burst + pos comparison) and
  relocate rather than fight it. Landing INSIDE an egg hatch box also
  reads as a "wedge" — the scene has simply taken the mover.
- **Wandering-NPC conversations: standstill-strike.** Poll the NPC via
  `ObjectManager::objectInfo <npcnum>`; when two reads agree within 8 units
  and distance < ~400, aim at the sprite pixel (plane projection, −30 px y)
  and fire three double-clicks at 120 ms spacing; confirm by
  `event 1 @ <class>` appearing in the log. Screenshot-based confirmation
  alone misses item-relative ask gumps.
- **Avatar walking dead but world alive?** Check `avatarInStasis` (toggle
  twice to read it), but only OUTSIDE scripted scenes — toggling it during
  a scene inverts the scene's own bookkeeping and wedges the scene instead.

## Addenda from part 2 of 2026-08-17

- **zd=0 floor tiles (shapes 242/301, footpad (4,4,0)) support nothing
  above z0.** Standing sticks (until gravity or a step), walking is
  refused in all directions, teleports snap/bury. Everything raised that
  is built from them is unwalkable until the TYPEFLAG zd fix lands. At
  z<=0 the engine's freebie support rule hides all of it.
- **Drag pickups: verify via the log**, not the screen: "Dragging item
  N" → "Dropping object N" → "Dropped item in backpack" (kDebugObject).
  Release on a probe-verified MainActor body pixel. Shields, keys and
  potion 859 stash (859 refused on 2026-08-17; real drags worked on
  2026-10-30, `docs/playtest-2026-10-30-potions-summit.md`) — if two items
  behave differently under the same drag, believe the log.
- **Probes cannot see into gumps** (the Object click-dump is a
  GameMapGump path) and cannot see roof-occluded NPCs. An NPC indoors is
  unclickable from outside; go in (or accept the block).
- **Egg classes: quality + 0x47F, resolved via lv_manifest.json.** On
  map 18: q305=temple entry, q306=crack HINT, q296=the AO altar
  ceremony. Scene eggs hatch on teleport-arrival; teleport TRIGGERS
  (207/208) do not.
- **Items north of the Avatar render and hit-test BEHIND his sprite.**
  Approach pickups from the north-west so the item paints in front.

## Part-3 addenda (2026-08-17)

- **Poisoned-state sessions: run `Cheat::heal` between steps.** The
  poison kills the Avatar during long harness cycles; the death book
  then eats/redirects every click (one engine quit came from a probe
  sweep crossing "6.Quit"). Every "phantom pause book" of the night was
  a death.
- **The loiter leash (scummvm-lv-console patch) is required for NPC
  work.** Without it strikes take 20+ attempts or fail; with it, 1-2.
- **Book detection: check the NAVY menu text pixels, not tan fields** —
  tan matches village huts, and a false positive leads to an Escape that
  OPENS the book (then click sweeps can hit Credits/Quit).
- Load-chooser slot layout REFLOWS as saves change — never click a
  thumbnail blind; screenshot the chooser and match the label first.

## NPC talk is a DOUBLE-click (2026-08-17)

A single left click on an NPC is LOOK — it prints the Object-debugflag
item trace and nothing else. That trace is the probe: single-click to
confirm the NPC is under the cursor, then double-click the same pixel to
talk (`xdotool click --repeat 2 --delay 80 1`). An entire night was spent
"failing to click" NPCs with single clicks that were landing perfectly.

## Ask-menu answers: click the row, trust the release (2026-08-17)

The fork's AskGump now dispatches on mouse-release (F18), so a plain
single click on the option row works. If a menu appears to IGNORE clicks
— closing gump + notifyClosing in the log but the same menu redisplays,
often growing duplicate entries — the answer is dispatching and the
USECODE has no matching case (F17 family: the 1994 files contain
menu-add/case text mismatches; the compiler dispatches on exact
English-stripped text). Diagnose with the string scanner in the part-4
report, not with more clicking.

## Debugger pipe parity (2026-08-17)

`commands.txt` lines are consumed only while the console is attached, and
a queued `exit` ends that attach's drain — everything after it waits for
the NEXT attach. Never fire-and-forget `Cheat::toggle` (or
`Kernel::toggleFrameByFrame`): verify each by its echoed "Cheats = ..."
line before queueing the next command, and end every batch with a unique
`UCMachine::getGlobal 0x7Fx 1` sentinel so you know the drain finished.
Teleports need cheats ON and print nothing on success; verify by
`ObjectManager::objectInfo 1`.

## Drag pickups need reach; saves keep gumps (2026-08-17)

- A drag-drop onto the Avatar silently bounces if the item is out of
  reach (~150 units): "Dropping object N" with no "Dropped item in
  backpack" and the item back at its origin. Walk adjacent first.
- Saving mid-conversation embeds the open AskGump; on load it is an
  orphan that eats clicks over the menu area. Bye out before saving.

## The console runs ONE command per attach

Discovered the hard way 2026-08-19, after a whole session of "the debugger
is eating my commands". Each `ctrl+alt+d` attach drains exactly one line
from `commands.txt` and then closes again. A batch of three appended lines
executes one line per attach, not three in a row — so a multi-command
setup needs a chord between every command.

`session.sh dbg` also SENDS TWICE when its first send times out (it
attaches and retries). For anything with parity — `Cheat::toggle` above
all — that silently flips the state back. Send toggles as a single raw
append while already attached, and always confirm by the echoed
`Cheats = true` line.

Every `resume` sent while already detached queues an `exit` that nothing
consumes. A stack of them makes the next attaches close instantly. When
`dbg` starts failing to stay attached, restart the session rather than
fighting the backlog.

## Climbing needs a HELD SPACE and a keyboard direction

The jump/climb branch needs `MOVE_JUMP` **and** `MOVE_ANY_DIRECTION`, and
the climb scan inside it runs only when `MOVE_MOUSE_DIRECTION` is CLEAR —
so the direction must come from a keyboard action (stock `UP`/`DOWN` are
`MOVE_FORWARD`/`MOVE_BACK` and qualify), never the mouse.

And **SPACE must be HELD, not tapped**: `xdotool key space` presses and
releases inside one frame, `onActionUp` clears `MOVE_JUMP` immediately,
and `AvatarMoverProcess::run()` returns early whenever the Avatar is
busy — which he is for most of a walk. A tap therefore does nothing at
all, which reads exactly like "climbing is broken".

Facing decides WHERE he climbs (`direction = avatar->getDir()`), and
`checkTurn` is mouse-gated, so keyboard movement alone never turns him.
Recipe: mouse-walk into the wall to set facing, release the mouse, hold a
direction key, hold SPACE.

## Two recovered hazards (2026-08-22)

Left off this file when the standing-hazards list moved out of HANDOFF;
both live in dated docs only until now.

- **Deadly water does NOT block walking** (pool-crossing F4,
  `docs/playtest-2026-08-16-pool-crossing.md`). Walkers stroll straight
  in and drown — which, plus the fixed-jump chord, explains most
  historical deaths there. Verify aim pixels before any pathfinder/jump
  click; never blind-walk near water. Related: `exact_reach` treats the
  whole water surface as standable (`z<=0` freebie support), so trust
  its `lands` list, not its footprint.
- **Cheats ON turns every NPC talk into the retail dev menu.** Teleports
  need cheats ON, so the sequence teleport → double-click an NPC opens
  the dev menu instead of dialogue. Toggle cheats off (verify the echoed
  state line) before any talk check, and remember the dev menu's Quit is
  live under blind click sweeps.

## Addenda from the 1→18 run (2026-09-05 … 2026-09-07)

- **Let a cutscene run untouched.** Attaching the debugger PAUSES the world,
  and a scene sets its flag only at the END of its waits and barks — AOSCENE
  needs ~450 ticks for `godsFree`. Polling froze the scene and read 0 every
  time, which was misdiagnosed as a crash for a whole session. The same pause
  makes the Avatar refuse all four directions, indistinguishable from a
  teleport wedge and unfixable by `Cheat::hackMover`; `AOSCENE::hatch` opens
  with `setAvatarInStasis(true)`, so stasis is expected. Close the console,
  wait the scene out, *then* query. Frame-diffing does not separate the two —
  a static sanctum gives identical frames.
- **The console is a toggle with no readable state.** Probe it with `help`
  and watch the log grow; do NOT detect it by green pixels (grass matches).
  An `exit` typed at a CLOSED console leaks its letters into the game — `i`
  opens the pack, `m` the minimap, Escape the Pagan menu.
- **A scene egg hatches once per map instance, and the savegame stores that.**
  Teleport-arrival is still the reliable trigger, but re-arming one means
  leaving the map and coming back.
- **Occlusion is world-determined, not camera-determined.** U8's view angle is
  fixed, so walking the Avatar around does not uncover an NPC behind scenery —
  you have to catch a wanderer when he is clear of it. Corollary for items:
  one is clickable only if nothing tall stands SOUTH of it, and neither the
  map validator nor `exact_reach` can see that.
- **Before `f9a9aba` (2026-09-25), the camera stopped following the Avatar
  after the Sacred Circle ceremony** and after the Lord British scene (both
  retested on the fix). He
  froze once he left the fast area, and NPC strikes missed. Cause: LVFREE's
  `scrollBack` compiled to nothing (its `Camera::setCenterOn(1)` was dropped
  by the parser), so a finished `scrollTo` left the camera parked. Fixed in
  `lv-patched/FREE.UNK` fix 2. A save taken on an older build keeps the
  parked camera; recover it with `CameraProcess::moveToAvatar`. See
  `.claude/rules/camera-intrinsics.md`.
- **The villages defeat short-step drivers.** `walkto.py`, `trek.py` and
  `hike.py` all pin in the Gunnar village; what gets through is a 2.5 s burst
  at mag 240 with a diagonal. The Avatar has also climbed onto a hut roof and
  been shut inside a hut whose only standable level reads as the roof.
- **A process spawned from `hatch` must be the LAST statement.** `spawn X →
  return` emits an implies, so a process that never returns freezes the scene
  with the Avatar in permanent stasis and the game unsaveable (2026-09-07,
  the reagent top-up process).

## Addenda from the god-placement look (2026-09-13)

**The harness game directory was stale, and nothing said so.** `install_lv.sh`
installs into `shared/data/u8-install/`; the harness runs
`shared/u8-lv-patched/`. A session spent several minutes looking for new art
and seeing the *previous* build's props. `session.sh start` now copies all
five artifacts from `shared/build/` and prints each one it replaced — read
those lines. If it prints nothing, the tree was already current.

**Send the chord as explicit key events.** `xdotool key ctrl+alt+d` reaches
ScummVM only intermittently on this harness; the reliable form is

```bash
DISPLAY=:77 xdotool keydown ctrl keydown alt key d keyup alt keyup ctrl
```

Hours went into "the console toggle is inverted" before this was the actual
cause of most of it.

**The `ctrl+alt+d` chord does not reach the game while a conversation menu is
up.** A fresh `start` lands in Devon's opening conversation. Keystrokes then
go to the game: they open the inventory backpack and the minimap, neither of
which closes with Escape, and the session is effectively wedged. Click the
conversation's own options through to the end first (`Goodbye.` sits near
x=920,y=338 on the default 1450x873 display), then open the console.

**The console is a toggle with no readable state, so make every batch
self-normalizing.** End each batch with `exit`. A batch that leaves the
console open makes the *next* batch's chord close it, and that batch's
commands are typed into the world instead — which looks exactly like the
commands failing.

**`dbg` does not work against `scummvm-lv`.** It waits on a stdin reply only
the `--enable-text-console` build gives, and `scummvm-lv-console/scummvm` is
stale (2026-08-19 vs 2026-09-13). Use the chord and read the overlay.

**Read a sprite's identity from the engine, not from the screenshot.**
`ObjectManager::findShape <id>` lists every instance with its coordinates,
frame, shapeinfo flags and `px=(dx,dy)` *relative to the Avatar*, which is
the camera centre. The Inner Sanctum has eight torches, and the god crystals
are the same gold; a screenshot alone could not tell them apart. To see what
the shipped bytes actually decode to, render the shape out of the installed
FLX with `png2shape.render_preview` — no engine needed.

**Typing into the world opens gumps that then block the chord.** A leaked
command string contains `i` and `m`, which open the backpack and the minimap.
Neither closes with Escape, the minimap covers the top-left quadrant of the
view (it hid a god through four screenshots), and the backpack blocks the
chord outright. Press `i` and `m` again to toggle them off.

**Do not blind-skip the intro when you are about to load a save**
(2026-09-14). A script that pressed Escape eight times and typed a name — the
NEW-game path — ran against a session whose intro was already over, so the
Escapes opened the Pagan menu and the name walked it into the LOAD GUMP. The
run then captured 1214 frames of a save browser while still reporting
`godsFree = 1`, because the flag came from the loaded slot rather than from
the scene. `Ultima8Engine::loadGame` leaves the intro by itself; a few
Escapes are enough, and no text should ever be typed at the world.

**Assert the world state before a long capture.** The same run read the gods
as `{}` twice and captured anyway. `findShape` returning fewer items than
exist has always meant a desynced console or a gump on top, never a missing
item — so check the count and the expected frames up front and abort, rather
than spending two minutes filming a menu.

**Reading a sprite's position: `px` in findShape is relative to the Avatar,
and carries a constant +20 in y.** Screen offset from the Avatar is
`dx = (gx-gy)/4 - (ax-ay)/4` and `dy = (gx+gy)/8 - (ax+ay)/8 + 20`. Invert it
to place the Avatar so a given item lands where you want it on screen — that
is how frame 0 was finally framed clear of the gumps.

**`session.sh cmd`/`dbg` do not work on `scummvm-lv`.** They append to
`commands.txt`, which only drains on the `--enable-text-console` build. The
overlay console driven by `xdotool type` is the whole interface here, and
debugger replies DO land in `lv_run.log`, which is how to read them back.
**`nav.py` was rewritten on 2026-09-18 to match**: `nav.console()` shells to
`dbg.sh`, `nav.pos()` parses the reply out of the log, and `nav.resume()` is
a documented no-op because `dbg.sh` exits the console itself. Everything
built on nav — `walkto.py`, `hike.py`, `route.py` — works again. Do not
"optimise" `console()` back to inline keystrokes: the ctrl+alt+d chord
TOGGLES, so against an already-open console it closes it and the command
plus its `exit` are typed INTO THE WORLD. That cost a session once — every
walk silently did nothing while position reads kept answering, and the
stray keys left the Avatar on map 0.

**Attached means paused, so a walk between two position reads does nothing.**
Send `exit` before every movement and re-attach afterwards.

**Position: `ObjectManager::objectInfo 1`.** The reply carries the map in
`m:` — check it. A teleport that silently did nothing (cheats off prints
`Cheats are disabled`) leaves you reading a valid position on the wrong map.

**A running Avatar refuses the 8-unit step a walking one takes.** On Map 10
inside Hoskuld's palisade (2026-09-18) `walkto.py` at its default RUN gait
(240 px offset) could not move the Avatar west across the worn-earth track
for ten probe cycles — every advance came from the 8-direction probe, which
uses a ~156 px offset and therefore WALKS. The same ground at `--walk`
crossed at ~500 units per burst with no stall at all. The track tiles (425)
are `SI_SOLID|SI_LAND` 8 units tall, so stepping onto one is an 8-unit rise:
inside the lattice `scanForValidPosition` accepts, and the run animation
does not. **Walk every leg that climbs anything** — ramps, stairs, decks,
track lips. Run only on open flat ground, and only where a chaser is the
bigger risk.

**`pgrep -f` matches your own shell.** `pgrep -f 'walkto.py'` inside a Bash
tool call matches the `bash -c` that is running it, so counts are always one
too high and `pkill -f` kills the calling shell (exit 144). Bracket a
character — `pgrep -f 'walkto[.]py'` — so the pattern cannot match its own
command line.

**A bare `make` in `scummvm-lv/` can build an engine that cannot find the
game.** The checkout's `engines/ultima/detection_tables.h` goes stale
whenever `EUSECODE.FLX` moves, and the linked binary keeps working until
something forces `detection.o` to recompile — then the next launch prints
`WARNING: Couldn't identify game 'ultima8' for the engine 'ultima'`, the
session comes up in the ScummVM launcher, and every debugger command times
out with no reply. **Rebuild with `./build_scummvm.sh`**: it rewrites the
detection entry from the actual FLX before running make. Found 2026-09-19.

**`Cheat::toggle` is a toggle, and a fresh session starts with cheats OFF.**
`MainActor::teleport` then prints `Cheats are disabled` and does nothing,
while `objectInfo` keeps answering — so position reads look healthy and the
Avatar never moves. Read the reply: it prints `Cheats = true` or
`Cheats = false`. Calling it twice puts you back where you started.

**The first teleport of a session fires the Guardian cutscene.** Class 0x0401
`AVATAR` at 0x1908 runs once per game, gated on the global at bit offset
0405, the moment the Avatar is on a map that is neither 3 nor 0: it freezes
him, teleports to (15967, 19711, 0) on map 0, creates and uses the
apparition, then teleports back to where he was. It takes roughly ten
seconds. A walk started inside that window pushes a frozen Avatar on map 0
and looks exactly like a wedge. **Teleport, wait 20 seconds, confirm `m: 10`
with `objectInfo 1`, then walk.** Found 2026-09-19.

**`walkto.py` carries its stall counter across the whole run.** A leg that
thrashes around a waypoint early can exhaust the budget and leave every later
leg unwalked. Re-invoking with just the remaining waypoints resets it and
usually clears the leg on the first burst, so a `BUDGET`/`FAILED` is worth
one retry before it is called a map defect.

## The first plate after a map switch can be black (2026-09-25)

Taken 2 s after `Loading Fixed items in map 11` reached the log, the plate
showed the Avatar and one monster sprite on black; 6 s after the teleport
the same view was drawn. The load line says the items are in, and the
first draw lags it. Wait a few seconds past the line before a plate.

## `dbg.sh` leaks `exit` into the game after a command that closes the console (2026-09-25)

`MainActor::teleport`, `Ultima8Engine::loadGame` and
`MainActor::toggleCombat` close the console themselves (`cmdTeleport`
returns `false` on success). `dbg.sh`'s trailing `exit` is then typed at
the game: `i` opens the backpack, which is the pack-reappears trap below.
The open pack swallows the next chord, and that command's letters reach
the world too: `c` toggles combat, `m` the minimap. Send those three
commands as chord, command, Return, and no `exit`.

## `loadGame N` loads slot 1 whatever N is (2026-09-25)

`Ultima8Engine::loadGame N` ignores `N` (`debugger.cpp:198`). Load a
checkpoint by copying it over `ultima8.001` (back that up first, restore
it after).

## An old save does not see new fixed items until you leave the map (2026-09-25)

A save carries the current map's fixed items. A save taken on Map 17
before the plaques existed showed `findShape 614` as 0 on load; after a
hop to Map 10 and back it read 3. Re-enter the map before judging a new
placement from an old save.

## The pack gump can reappear after a `dbg.sh` teleport (2026-09-25)

Cause: the leaked `exit` above.

Closed by a double-click on its left frame edge (window (278, 150)), it was
open again after the next `dbg.sh "MainActor::teleport …"` and closed
after the one after that. Probe for it before every plate: the flap's
brown at window (320, 120) reads red well above blue, the floor does not.

## "Cycle in paint" prints only with the Object debug channel on (2026-10-17)

The engine reports a draw-order knot with `debugC(kDebugObject, ...)`, so
the line reaches the log only while `debugflag_enable Object` is set. A
`loadGame` clears the flag. A check that greps the log for `Cycle in paint`
after loading a save therefore reads 0 whatever the map does. Re-enable the
channel after every load, and prove it is on with a negative control: a
spot that logged knots on an older build
(`docs/playtest-2026-10-17-vignettes-verify4.md`, F1).

A second trap is the one-shot capture loop: a second `MainActor::teleport`
in one console session did not land (2026-10-17).
`tools/playtest-linux/vignette_capture.py` restarts the session for each
shot for that reason.
