# Steps 15 to 18 in one session, the stele, and the cave ascent (2026-09-26)

HEAD `b4aa1de` as built: `shared/build/` matched `ARTIFACTS.sha256` for all
four artifacts (EUSECODE `7b916203`, FIXED `bf233644`); `session.sh start`
synced FIXED.DAT (both copies) into `shared/u8-lv-patched/`. Binary
`scummvm-lv/scummvm`, 640x400 canvas, crop `+565+336`, `usehighres=true`.
Plates are in `docs/playtest-2026-09-26-steps-15-18/`, named by test ID.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| A1 | Map 17 to Map 10 on foot | Map 17 exit trigger fired at y 11520; Map 13 descended tile by tile, z 120 to 0, no fall; trigger 206 landed (7168, 23296, 8) on Map 10 | **PASS** |
| A2 | Sacred Circle ceremony (step 15) | hatched on a walk-in; answers **Let's be reasonable!**, **Yes, Priestess.**, **Please, High Priestess.** from the menus on screen; `avatarPoisoned` 1 to 0, `shieldFixed` 0 to 1, `inShadeScene` 0 | **PASS** |
| A3 | Restored shield into the pack | "I take up the Shield of the Ancients..." bark; `findShape 539` = 1 item, 12938 frame 2, contained; weight 320 to 280 | **PASS** |
| A4 | Camera follows afterwards | snapped back to the Avatar with the elders gone; `f: 0x2041` held over an 8,000-unit walk; no `CameraProcess` command used all session | **PASS** |
| A5 | EggShades method frame (09-25) | quarrel barks, Shade speeches, and the send-home all ran; Atli, Thordis, Ezrekal read at home coordinates after the scene | **PASS** |
| A6 | Hrodny's chest key (step 16) | her post-ceremony tier opened on the second talk; "How can I open the temple?" spawned bag 14387 at (19588, 23284, 0) holding key 14386 q 20; `spokeTemple` 1 | **PASS** |
| A7 | Tiny Tar from the chest | key on chest: shape 618 to 78; three frame-8 potions dragged into the pack, weight 300 to 330 | **PASS** |
| A8 | Crack, full size (negative control) | three south pushes at (2880, 6096): zero displacement | **PASS** |
| A9 | Crack as Tiny Tar, `templeOpen` | shape 708 at x 2872 passed to (2872, 6256); `EggTempleEntry` fired; `templeOpen` 0 to 1 | **PASS** |
| A10 | **Shield on the altar (step 17), first hatch** | `EggAOCeremony` hatched; first bark shown; about 10 s later **ScummVM segfaulted** (`Segmentation fault (core dumped)`) | **FAIL (run broken here)** |
| A10r | Same hatch, reloaded from the engine's autosave taken 90 s earlier, twice, under gdb | both runs completed: white fade, the three-god pan, "It is done..."; `godsFree` 0 to 1; god frames 3/4/5; no SIGSEGV, so no backtrace | **PASS 2 of 2 (crash 1 in 3 overall)** |
| A11 | Leaving the sanctum | full size north: refused; second potion drunk inside, x 2848, out to (2868, 6044) as shape 708 | **PASS (needs a second potion)** |
| A12 | Endgame (step 18) | `EggEndgame` hatched on the walk north from the pad; `endgameStarted` 1, `hasBag` 1; bag 12424 holds six reagent stacks of q 25; weight 330 to 490; Avatar walks after the scene | **PASS** |
| A13 | EggEndgame `topUpReagents` (09-25 frame) | scene ended with stasis released, nothing stuck; three `UCProcess` live; the refill itself was not exercised (no player action lowers a carried stack) | **PARTIAL** |
| A14 | Closing bark of the endgame | the screen is fully black while "And with the power of the Ancient Ones..." plays; no text visible in any of 10 frames | **FAIL (invisible bark)** |
| B1 | Stele at (4159, 7679) free of the dais | floor tiles show between the stele's top and the dais's near tier (`B1-stele-zoom.png`); the dais ends at y 7423 | **PASS** |
| B2 | Plaque q55 double-click from 120 units | event 1 @ 04EB:00A9; gump reads **ADMIRE / BUT / TOUCH NOT**; no crash | **PASS** |
| C1 | Cave ascent, in window x 29504..29524 | **10 of 10 climbed** to z 56; `flags` 0 or 0x400 before every SPACE; nearest ghoul about 4,200 units away | **PASS** |
| C2 | Out of window x 29500, 29532 (controls) | 0 of 2; walked west to x 28900 and 28932 at z 0 | **PASS (refused as predicted)** |
| C3 | Combat mode (positive control) | 0 of 2 with `flags: 800`; both ended at (29228, 23622, 0), 288 units west | **PASS** |

**The unbroken run broke at step 17**, on an engine segfault during
AOSCENE. Everything before it ran in one session, cheats off, on foot, with
debugger reads only. The rest of the chain was exercised from the engine's
own autosave: a reload, and no debugger write was ever needed.

## Method

Part A started from `~/lv-checkpoints/cp22-shield-halves.sav`, copied over
`ultima8.001` and loaded with `Ultima8Engine::loadGame 1`. Console use in
Part A: `ObjectManager::objectInfo`, `ObjectManager::findShape`,
`UCMachine::getGlobal`, `Kernel::processTypes`, and one
`debugflag_enable Object` (logging only; it touches no world state). No
`Cheat::toggle` appears in the Part A log (`grep -c "Cheats = "` = 0), and no
`CameraProcess`, `Item::grab`, `setGlobal`, or teleport was sent. Every
answer, pickup, key use, and potion was a mouse action on what the screen
showed.

The console was driven by a scratchpad script that confirms the console is
open from its border row (y 268, colour (65, 64, 65)) before typing, and
closed after. One early read, before that check existed, went unanswered and
its letters reached the world (pack and minimap opened); `flags` read 0
afterwards, and both were closed with `i` and `m`.

Maps: cp22 was taken on Map 17, so Map 17 in Part A is the save's own
2 September map (dark floor, statues). Maps 13, 10, and 18 loaded from HEAD's
FIXED.DAT.

## A1: Cloud City to the vale, PASS

Start (7212, 1652, 0) on Map 17, both halves in the pack (2632 frame 0,
7936 frame 1), weight 320 (`A0-start-map17-memorial-hall.png`). Walked south
through the old Cloud City to (5368, 10928) and crossed y 11520 in one burst:
`Unloading map 17` / `Loading Fixed items in map 13`, arrival
(4096, 832, 120) (`A1-map13-summit-arrival.png`).

The descent followed `build_map_13.climb_tiles()` in reverse, 89 tiles, at
walk gait: z 120 down to 0 through every lattice level, both switchbacks,
no fall, base (4032, 10240, 0) (`A1-map13-base-after-descent.png`). The
walk west to trigger 206 landed on Map 10 at (7168, 23296, 8).

## A2 to A5: the Sacred Circle, PASS

Map 10 route from `pathfind.py` (DryMixin default): 13 waypoints to
(20456, 17936). The straight line north stops at a standing stone at about
y 17700; a sidestep to x 20352 and a walk north from (20352, 17536) hatched
the egg (`A2-circle-approach-before-hatch.png`,
`A3-ceremony-hatched-elders-arrive.png`). The console stayed closed from the
hatch to the scene's end.

The quarrel (squabble, 09-25 frame) played first: "Liar! Gunnar's clan,
tradition broke!", "Hoskuld, the shield stole! Upon your head, the blood of
Gunnar is!", "The hero, I am not..." (`A3-squabble-*.png`). The menus, in
order: **Let's be reasonable!** (`A3-first-ask.png`), the Priestess's
condition (`A3-priestess-shield-condition.png`), **Yes, Priestess.**
(`A3-second-ask.png`), the halves on the grass
(`A3-halves-on-ground.png`), a white flash and the whole shield
(`A3-reforge-flash.png`, `A3-shield-restored-whole.png`), the Shades
(`A3-shade-*.png`), the Priestess's offer
(`A3-priestess-offers-heal.png`), **Please, High Priestess.**
(`A3-heal-ask.png`), "I feel better... But I'm still so weak!"
(`A3-cured-bark.png`), her temple hint, and the hand-over bark
(`A4-take-up-shield-bark.png`). In the next sheet, within about 4 to 6 s, the view was on the Avatar
with the three elders gone (`A4-scene-ended-camera-on-avatar.png`).

Read after the scene: `[0404 01] = 0`, `[0409 01] = 1`, `[0452 01] = 0`;
`findShape 539` = 1 found, item 12938 frame 2, `f: 0xc`, in the pack
(`A4-restored-shield-in-pack.png`); weight 280. The send-home: Atli (107) at
(19200, 6400), Thordis (106) at (6144, 6656), Ezrekal (116) at
(12800, 12544).

The camera then followed a walk of about 8,000 units north to the Gunnar
village; the Avatar is centred in the plate at the far end
(`A5-walk-north-camera-follows.png`), and `f: 0x2041` held at every read on the way.

## A6 to A7: Hrodny, the key, the potions, PASS

cp22 had `hrodnyMet` 0, so the first talk offered only name and job
(`A6-hrodny-first-menu.png`). **What is your name?** ("Hrodny, daughter of
Ulmar, I am."), then **bye**. The second talk opened the post-ceremony tier:
**I have been healed!**, **The Shield of the Ancients is restored!**, **bye**
(`A6-hrodny-post-ceremony-tier.png`). **I have been healed!** added
**How can I open the temple?** (`A6-hrodny-how-open-temple.png`), which
played the potion story and the thief lead ("dragging a bright small weight
up the old temple road, southward", `A6-hrodny-thief-lead.png`) and ended
the conversation. The "Shield of the Ancients is restored!" option was gone
from the second menu.

`findShape 637` then listed bag 14387 at (19588, 23284, 0) holding key
14386 q 20. The walk south took a detour: the pathfinder's line at
(19783, 11327) runs into a fence at about y 11260, and the gap is near
x 20420. The bag drag logged `Dragging item 14387` / `Dropped item in
backpack` (`A7-key-bag-on-temple-road.png`); weight 280 to 300.

Back at the chest (21152, 8832): double-click on the key inside the bag,
then a click on the chest logged `Target result: Item 8981 ... shape 618
(uc: LCHST_EW)`, and `findShape 78` then listed 8981. The chest opened on
three potions (`A8-chest-open-three-potions.png`); all three dragged in,
each `Dropped item in backpack`, weight 300 to 330, chest empty
(`A8-three-potions-taken-chest-empty.png`).

## A8 to A9: the crack, PASS

Trigger 211 landed at (3072, 2024) on Map 18
(`A9-map18-temple-arrival.png`). At the crack, `EggCrackHint` (05B1) barked
"The stone here is split from top to bottom -- and there is open air beyond
it. But the gap is no wider than my hand." (`A10-crack-hint-bark.png`).

**Negative control:** three 1.2 s south pushes at full size from
(2880, 6096): position unchanged.

The drink needs the Avatar's x in 2848..2879, and he stood at 2880, one unit
out. Orthogonal walk steps come in about 96 units and diagonal ones in about
76 (x 2880 to 2792, then 2680, then 2888); a diagonal step reached 2872.
Drinking 8984 logged `event 1 @ 04E5:00A9` (`A11-drink-tiny-tar.png`), the
Avatar became `shape 708 (uc: CHILD)`, and two south pushes carried him from
(2872, 6136) to (2872, 6256). `EggTempleEntry` (05B0) fired, `templeOpen`
read 1, and he barked "I am through. The air in here is old and very still."
(`A11-through-the-crack.png`). He regrew to shape 1, hp 30, in place (`A11-regrown-in-sanctum.png`).

## A10: the altar, FAIL on the first hatch

`pathfind.py`'s route over the dais wedged at (3248, 7928, 8) against the
candelabrum south of it. Walking round the dais's east side to
(3268, 8580, 0) and then north-west hatched `EggAOCeremony`:
`Item: 12752 (shape 73) calling usecode event 7 @ 05A7:0080`.

The first bark came up at once, "I place the artifact upon the altar. The
ancient symbols begin to glow." (`A12-altar-hatch-t0s.png`). Frames at 2, 4,
6, and 8 s show the same view with no further bark and no fade; from about
10 s the window was gone and the log ended:

    tools/playtest-linux/session.sh: line 135: ... Broken pipe  tail -f -n +1 "$CMDS"
         1571802 Segmentation fault      (core dumped) | ... ultima8

Nothing else was logged between the hatch and the fault (the 860 god
`event 2` ticks only). The fault fell 8 to 10 s after the hatch; in R2
below the white fade began about 11 s after the hatch, so the fault lands in
or just before the stretch where AOSCENE runs `spawn safePlaySFX(RUMBLE1,
255)` and `FadeToWhite()`. That placement is from frame timing only. The core
went to apport and was not recoverable.

State at the hatch: `shieldFixed` 1, `templeOpen` 1, `godsFree` 0, weight
330, shield 12938 in the pack, potions 8982 and 8983 at frame 8 and 8984 at
frame 0.

### A10r: two reruns under gdb, both PASS

The engine had written its autosave `ultima8.000` at 01:39:06; the crash was
at 01:40:38. That save loads on Map 18 at (3400, 7696, 0) with the same
flags and weight, and is kept as
`~/lv-checkpoints/cp34-altar-ready-head-20260926.sav`. Two reruns from it,
under `gdb -batch` with `handle SIGSEGV stop`, walked the same route into
the box:

- **R1** (Object logging off): the scene ran to "It is done. The Ancient
  Ones are free." (`R1-gdb-rerun-it-is-done-bark.png`); `godsFree` 1; god
  frames 4, 3, and 5.
- **R2** (Object logging on, as in the crash run): white from about 12 s
  after the hatch (`A13-fade-to-white.png`), then the pan across the three
  gods breaking out of the amber (`A13-pan-*.png`), and back to the altar.
  `godsFree` 1.

Neither run faulted, so there is no backtrace. The count on HEAD is one
segfault in three hatches of the same scene. The 2026-09-05 record also saw
one unreproduced AOSCENE segfault.

## A11: out of the sanctum, PASS with a second potion

At full size, two north pushes from (2872, 6224) inside the sanctum moved
him only east, to (2896, 6208). After lining up at x 2848 (one east and one
diagonal step), drinking 8983 inside and pushing north brought shape 708 out
to (2868, 6044). The first push ran before the shrink took effect and
walked him off the column to x 2804; a second push slid him back to 2868.
The walk north to trigger 210 was uneventful; he regrew on the way.

## A12 to A14: the endgame, PASS with an invisible closing bark

From the pad at (18432, 22688), one walk north hatched `EggEndgame`:
`Item: 8552 (shape 73) calling usecode event 7 @ 05AA:0080`. The barks
played over the Avatar ("With the Ancient Ones freed...", "Green returns...",
"The Zealans gather...", "An elder steps forward...", and "The elder presses
a worn bag into my hands..."; `A16-endgame-*.png`). Then the screen went to
black for about 20 s. Every frame in that stretch is black apart from the
cursor (`A16-endgame-black-closing-bark-invisible.png`, brightened eight
times: still black), so the closing line about the path to Britannia is never
seen. The view faded back in with the Avatar centred
(`A16-endgame-after-fade.png`).

Read afterwards: `[0716 01] = 1`, `[040D 01] = 1`, `godsFree` 1; weight 330
to 490; `findShape 637` lists the new bag 12424 (vol 18/32, six items) and
`findShape 395` six stacks, frames 14, 10, 9, 8, 6, 0, each q 25, in it
(`A16-reagent-bag-open.png`, the six stacks overdraw at slot (0, 0) as
recorded before). A walk east moved him 208 units, so stasis was released.
`Kernel::processTypes` listed three `UCProcess`, consistent with the
top-up process being alive; lowering a carried stack needs a spell or a
debugger write, so the refill was not exercised.

## B: the obelisk stele, PASS

In the gdb session after Part A (cheats on, teleports), Map 17 was loaded
fresh from HEAD. `findShape 614` listed four plaques, q55 at
(4127, 7680, 16); `findShape 861` the obelisk at (4095, 7167, 16).
`B1-stele-dais-obelisk.png` and the 3x zoom `B1-stele-zoom.png` show the
stele standing on the floor with floor tiles between its top edge and the
dais's near tier. The gap on screen is small (a few pixels at 1x), because
the iso view puts the stele's top close to the dais's front lip; in the zoom
the two read as separate objects.

From (4160, 7800, 0), 120 units south, a double-click on the plaque logged
`Item: 14433 (shape 614) calling usecode event 1 @ 04EB:00A9`, and the gump
read **ADMIRE / BUT / TOUCH NOT** (`B2-plaque-gump.png`).

## C: the cave ascent, 10 of 10

Fresh session (new game), `Cheat::toggle`, teleport to
(x, 23622, 0) on Map 8, the Guardian scene waited out. Per attempt: teleport
(no trailing `exit`), position check, a 0.3 s right-mouse burst west, then
`objectInfo 1` and `findShape 142`, a 2.5 s settle, `keydown --window` SPACE
and 60 ms later Up, both held 1.6 s. Success is z 56.

| # | start x | flags before | ghouls (nearest) | end | climbed |
|---|---|---|---|---|---|
| 1 | 29516 | 0 | 5 (~4,200) | (29364, 23622, 56) | yes |
| 2 | 29508 | 400 | 5 | (29348, 23622, 56) | yes |
| 3 | 29524 | 0 | 5 | (29372, 23622, 56) | yes |
| 4 | 29516 | 400 | 5 | (29356, 23622, 56) | yes |
| 5 | 29516 | 0 | 5 | (29364, 23622, 56) | yes |
| 6 | 29512 | 400 | 5 | (29352, 23622, 56) | yes |
| 7 | 29520 | 0 | 5 | (29368, 23622, 56) | yes |
| 8 | 29504 | 400 | 5 | (29344, 23622, 56) | yes |
| 9 | 29516 | 0 | 5 | (29364, 23622, 56) | yes |
| 10 | 29524 | 400 | 5 | (29364, 23622, 56) | yes |
| c1 | 29500 | 0 | 5 | (28900, 23622, 0) | no |
| c2 | 29532 | 0 | 5 | (28932, 23622, 0) | no |
| k1 | 29516 | **800** | 5 | (29228, 23622, 0) | no |
| k2 | 29516 | **800** | 5 | (29228, 23622, 0) | no |

`0x800` (combat) was clear before all ten in-window attempts. Four of the
five ghouls sit near (2000..2400, 1900..2400) and the fifth, item 65, at
(29087, 27807, 56), about 4,200 units south; none came near. x 29504 had
never been tried in engine; it climbed, as `climb_sim.py` predicts, and the
two out-of-window controls refused, also as predicted.

**Combat mode reproduces the canonical failures.** With combat toggled on
(k1, k2), SPACE did nothing and the hold carried the Avatar 288 units west
to x 29228. The 2026-09-25 record's failed canonical attempts ended at
"x≈29230 at z=0" after "286 units in the 1.6 s hold". Normal-mode failures
(c1, c2) walk about 600 units instead. So the 2/11 on canonical fits a
leaked `c` putting the Avatar in combat, and no floor is needed for the
climb (`C-s1-*-climbed.png`, `C-combat-control-1.png`).

## Findings outside the plan

1. **AOSCENE can segfault the engine**, one hatch in three on HEAD, about
   10 s in, before the white fade. It did not recur under gdb in two tries,
   so the cause is unread. A player who hits it loses everything since the
   last save, at the quest's climax. For whoever picks it up: AOSCENE last
   ran in engine on 2026-09-14, before `1b0bf9a` and `2f27d51`, and
   `2f27d51` moved TYPEAOFRIZBEE's `shieldMonitor`, the class of the
   shape-539 item the scene searches for. That is a lead, unread.
2. **The Inner Sanctum has no full-size exit.** The crack is the only way
   out and needs a second Tiny Tar. The chest holds three, so a player who
   takes all three is fine; one who takes one, or drinks two on the way in,
   is sealed in with the freed gods.
3. **The endgame's last line is invisible.** It is barked during
   `FadeToBlack`, and the palette fade blacks the text too.
4. **Lining up on the crack is fiddly.** The shrunken body needs x in
   2848..2879 (a 32-unit column) and walk steps come in 76 to 96 units; it
   took three to five bursts each way. The hint bark says the gap is narrow
   and says nothing about where.
5. **The Shades speak from off camera.** Their yellow barks sit clamped at
   the screen's bottom-left and the Shade sprites are never in frame
   (`A3-shade-hoskuld-speaks.png`). The 2026-09-25 plate
   `C3-shield-reforged-shades-speak.png`, taken before `2f27d51`, shows the
   same clamping, so the method-frame change did not cause it.
6. **Weight while shrunk read 820** (`Container vol: 175/200`), against 520
   on 2026-09-25; after the regrow it read 330 again.
7. **21,611 `Cycle in paint dependency graph` lines** (shapes 526, 426, and
   707) were logged on Map 10 between (20616, 10308) and (20624, 8852), the
   Gunnar fence and village edge.
8. **`Unhandled intrinsic 154 'Npc::getNpcSlot()'`** logged six times during
   the Hrodny talks; the talks worked.
9. Route geometry the pathfinder does not see: the fence at y 11260 north of
   (19783, 11327), the candelabrum south of the altar dais at
   (3248, 7928, 8), and the standing stone at about (20456, 17700) on the
   circle's south approach.

## Harness anomalies

- **The engine's periodic autosave is what saved the run.** ScummVM wrote
  `ultima8.000` about every five minutes; the copy from 90 s before the
  crash is how steps 17 and 18 were reached with no debugger write. After a
  crash, copy `ultima8.000` out before starting the engine again.
- The scrollbar test for "console open" fails on a fresh console, which has
  no scrollbar yet; the border row at y 268 works in both cases.
- Hatch events (`calling usecode event 7`) log only with
  `debugflag_enable Object`; the first gdb rerun had it off, so its hatch was
  detected from frames.
- The run-gait walker oscillates across short waypoints (tolerance 96 at
  600 units a second); short hops at walk gait fixed it.
- The console failed to open four chords in a row twice right after a walk
  burst; the next attempt opened it.

## Disk changes

- `docs/playtest-2026-09-26-steps-15-18.md` and the plates directory (new).
- `~/lv-checkpoints/cp34-altar-ready-head-20260926.sav` (new): the engine's
  autosave from 90 s before the crash, Map 18, `templeOpen` 1, `godsFree` 0,
  shield and two potions carried.
- `~/.local/share/scummvm/saves/ultima8.000` and `ultima8.001` were
  overwritten during the session and restored from copies taken first (md5
  `3e7dc241...` and `083de199...`, as before). `timestamps` and
  `scummvm-history.txt` in that directory were rewritten by the engine.
- `~/.config/scummvm/scummvm.ini` restored byte for byte (md5 `a143fa3b...`);
  ScummVM had reordered its keys.
- `shared/u8-lv-patched/FIXED.DAT` and `STATIC/FIXED.DAT` synced from
  `shared/build/` by `session.sh start`.
- `TODO.md` and `traps.md` not edited. The session is stopped.
