# The ceremony camera, the shield hand-over, the plaques and the receptacle look in the engine (2026-09-25)

Verification of commit f9a9aba (EUSECODE `7c3db807`, FIXED `b9cc0da8`).
`session.sh start` synced FIXED.DAT (both copies) and EUSECODE.FLX into
`shared/u8-lv-patched/`, and all four harness artifacts matched
`ARTIFACTS.sha256` before play. `scummvm-lv/scummvm`, 640×400 canvas, crop
`+565+336`. Checkpoints were loaded through save slot 1 (see harness
anomalies). Travel by `MainActor::teleport` with cheats on; the ceremony
answers and every click test are player input. Plates are in
`docs/playtest-2026-09-25-ceremony-plaques/`.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| C1 | Post-ceremony state | `getGlobal 1106` (inShadeScene) = 0, `1033` (shieldFixed) = 1, `1028` (avatarPoisoned) = 0; `objectInfo 1` `ef: 0x122` (carries 0x20 EXT_CAMERA) | **PASS** |
| C2 | Walk after the ceremony, view follows | (20504, 17152) to (20292, 19580), about 2,430 units; `f: 0x2041` held at every read; Avatar centred in every plate | **PASS** |
| C3 | Negative control, `cp23-ceremony-done.sav` | loads at `ef: 0x102` (no 0x20); after a 1,556-unit walk the Avatar is off-screen and the view stays on the circle | **PASS** (defect reproduced on the old save) |
| C4 | The camera snaps back when the scene ends | one plate the scene framing, the next the Avatar centred with the elders gone | **PASS** |
| S1 | Hand-over bark | "I take up the Shield of the Ancients. Its place is on the temple altar." over the Avatar | **PASS** |
| S2 | Shield in the pack | pack gump shows the round shield; `findShape 539` = 1 item, 14884, frame 2, container slot (8, 19), `f: 0xc`; total weight 320 → 280 | **PASS** |
| S3 | Nothing left on the grass | `findShape 539: 1 found`, still on Map 10, the one being the contained item; the ground sprite at the Avatar's feet is gone in the bark plate | **PASS** |
| P1 | Plaque q68, Arrival Plaza north wall | on the wall at head height, look bark "plaque" | **PASS** |
| P2 | Plaque q69, Main Plaza north wall, west doorway | on the wall beside the doorway, look bark "plaque" | **PASS** |
| P3 | Plaque q70, Main Plaza north wall, east doorway | on the wall beside the doorway, look bark "plaque" | **PASS** |
| P4 | Double-click opens the plaque gump with the text | ScummVM aborts: `readable_gump.cpp:108 ... I_readPlaque ... Assertion 'item' failed`, on q68 and again on q69 | **FAIL** |
| R1 | Receptacle look | "pillar receptacle", class 1144 event 0 | **PASS** |
| R2 | Receptacle double-click empty-handed | "The column flares with energy and repels you!" | **PASS** |

## C: the camera re-attaches, PASS

Loaded `cp22-shield-halves.sav` (Map 17, both halves in the pack:
`findShape 539` lists 2632 frame 0 and 7936 frame 1 in a container,
weight 320, `S0-halves-in-pack-before.png`). Teleported to Map 10
(20480, 17900), outside the egg's ±256 box, and walked north into it; the
scene hatched on the walk (`C0-ceremony-hatched.png`). The console stayed
closed from the hatch to the end.

Answers, each from the menu on screen: **Let's be reasonable!**
(`C1-first-ask.png`), **Yes, Priestess.** (`C2-second-ask.png`),
**Please, High Priestess.** (`C4-heal-ask.png`). The reforge and the Shades
played (`C3-shield-reforged-shades-speak.png`), then "I feel better... But
I'm still so weak!" (`C5-cured-bark.png`), then the hand-over bark (S1).
About 6 s after it the view jumped from the scene framing to the Avatar at
the window centre with the three elders gone (`C6-camera-back-on-avatar.png`):
the snap-back the FREE.UNK header predicts.

State read after the scene: `[0452 01] = 0`, `[0409 01] = 1`,
`[0404 01] = 0`, and `ef: 0x122` on the Avatar.

The walk: from (20504, 17152) south in bursts, reading `objectInfo 1`
between them: (20292, 18132), (20292, 18964), (20292, 19580), each with
`f: 0x2041`. `C7-before-walk.png` and `C8-after-2400-unit-walk.png` both have
the Avatar at the centre; the second is 2,400 units south, at a cliff edge
the circle plate does not contain.

**C3, the negative control.** `cp23-ceremony-done.sav` (taken after the
2026-09-02 ceremony on the old build) loads at `ef: 0x102`, and a 1,556-unit
walk south left the view parked over the circle with the Avatar walked out
of it (`N1-cp23-camera-parked-after-walk.png`). `f:` still read `0x2041` at
that distance, so the freeze itself was not reproduced; the missing 0x20 and
the parked view were. The same save also logs
`WARNING: Skipping invalid shape in sorter: 539,4!`, the frame-4 item that
LV-RESTORE change 13 now destroys.

## S: the shield hand-over, PASS

`S1-take-up-shield-bark.png` is the bark. In the frame before it
(`C5-cured-bark.png`) the white shield lies at the Avatar's feet; in the
bark frame it is gone. `S2-whole-shield-in-pack.png` is the pack opened
afterwards on Map 10: the round shield top left, the halves gone. Weight
320 → 280 is two halves out (−80) and one whole shield in (+40). The Map 18
altar was not attempted.

## P: the plaques, look PASS, use FAIL

`findShape 614` on Map 17 lists three, each `n: 235`, dispatching to class
1259 (`TYPENSGOLDPLAQUE`, 04EB):

    Item 2784 ... (5055, 9217, 16) q: 68, n: 235 ...
    Item 6230 ... (2495, 5121, 16) q: 69, n: 235 ...
    Item 6171 ... (5055, 5121, 16) q: 70, n: 235 ...

`(uc: PLAQUEEW)` in that listing is the class the shape would get; the
npcnum override wins, the same as the receptacles.

**On the wall (P1-P3).** Each reads as a small gold plate set flat on the
wall face, slanted with the wall, at about the Avatar's head height:
`P1-plaque68-on-wall.png` (with `P1-plaque68-zoom.png`),
`P2-plaque69-on-wall.png` and `P3-plaque70-on-wall.png`, the last two just
west of their hall doorways.

**Look.** A single click on each logged, for q68,

    Item: 2784 (shape 614) calling usecode event 0 @ 04EB:0080
    tick 1278334 running process 2375, item 2784, type 520, class 1259, offset 167

and barked **plaque** above it (`P1-plaque68-look-bark.png`,
`P2-plaque69-look-bark.png`, `P3-plaque70-look-bark.png`). The bark is the
English-only "plaque" of the build, one word.

**Use (P4), FAIL.** A double-click on q68 from 90 units:

    Item: 2784 (shape 614) calling usecode event 1 @ 04EB:00A9
    tick 1279664 running process 2407, item 0, type 0, class 1259, offset 201
    WARNING: Trying to access segment 0000!
    WARNING: Trying to access segment 0000!
    scummvm: engines/ultima/ultima8/gumps/readable_gump.cpp:108: static uint32
      Ultima::Ultima8::ReadableGump::I_readPlaque(const uint8*, unsigned int):
      Assertion `item' failed.

and ScummVM aborted (core dumped). Reproduced on q69 in a second session
with the same four lines. No plaque gump was ever drawn, so the three texts
are unverified.

The bytes say why. Class 04EB `use()` in the shipped EUSECODE:

    00B4: 59                    push pid
    00B5: 0C 00 00 00 00        push dword 00000000h
    00BA: 57 00 00 EB 04 C9 00  spawn 00h 00h 04EBh 00C9h

`readPlaque` at 00C9 starts with `push dword [BP+06h]` into
`Item::getQuality` and hands the same `this` to `Plaque::read`, so it runs
on item 0. Retail class 0257 (PLAQUENS) compiles the same source line as

    00B5: 40 06                 push dword [BP+06h]
    00B7: 57 00 02 57 02 C2 00  spawn 00h 02h 0257h 00C2h

with the plaque as `this`. The fault is in the compiler: `_gen_spawn`'s
same-class branch (`u8c_codegen.py`, the `resolved = self._resolve_function`
block near line 1952) always pushes a null `this` with `this_size` 0, which
is right for a free process and wrong for a typeclass method that reads
`this`. `readPlaque` is declared on the parent `GoldPlaque`, which is the
shape that hits it. Even without the assertion the gump would have read
**NO SOLICITING**: `getQuality` on item 0 returns 0 and falls to the
`else`. The two `segment 0000` warnings are that `getQuality`.

Not established: how many other LV classes spawn a `this`-reading method
through the same branch. The discriminator is a spawn with `this_size` 0
whose target pushes `[BP+06h]` before anything else; not scanned. The
base-game plaques on shape 614 dispatch to 0266 by shape and were not
tested.

## R: the receptacle look, PASS

Map 11, Avatar at (7600, 20690), the Earth receptacle (item 32132, q201,
`n: 120`) at (7680, 20736), `traceClass 1144` armed. A single click:

    Item: 32132 (shape 866) calling usecode event 0 @ 0478:0080
    tick 1208506 running process 13853, item 32132, type 520, class 1144, offset 178

and **pillar receptacle** over the socket (`R1-receptacle-look-bark.png`).
A double-click with no talisman carried (`findShape 596` lists all four in
the world) ran event 1 at `0478:00B4` and barked **The column flares with
energy and repels you!** (`R2-receptacle-repel-bark.png`).

## Findings outside the plan

1. **The plaque use crash (P4)** is the one thing here that bites a
   player: every double-click on any of the three plaques kills the game.
2. **Combat mode is why clicks "never log".** Twice in this session the
   Avatar read `flags: 800` (`ACT_INCOMBAT`), and in that state single and
   double clicks on the plaque logged nothing and barked nothing, because
   `GameMapGump::onMouseClick` and `onMouseDouble` both `break` on
   `isInCombat()` before the `dumpInfo` line. `MainActor::toggleCombat`
   put `flags: 0` back, and the next click logged its `dumpInfo`, its usecode
   event and the bark. This is a likely explanation for the 2026-09-15
   "clicks did not log" trap and for D1 being NOT DEMONSTRATED on
   2026-09-24. The combat came from finding 3.
3. **`dbg.sh` leaks `exit` into the world after any command that closes the
   console itself.** `cmdTeleport` returns `false` on success
   (`debugger.cpp`), which closes the console, so `dbg.sh`'s trailing
   `exit` is typed at the game: its `i` opens the pack. That is the
   "pack gump reappears after a teleport" trap. The open pack then blocks
   the next chord, and that command's letters go to the world too: `c`
   toggles combat, `m` the minimap. Sending teleports with the chord, the
   command and Return, and no `exit`, gave clean teleports with no pack,
   no minimap and no combat for the rest of the session. `loadGame` and
   `toggleCombat` behave the same way.
4. **A save taken on Map 17 before this build has no plaques.**
   `findShape 614` read `0 found` after loading `cp22` on Map 17 and
   teleporting within it; after a hop to Map 10 and back it read 3. The
   save carries the map's fixed items, so an old save sees new fixed items
   only after leaving the map and returning.
5. **Two wall lamps hang in doorway openings on Map 17**, as reported:
   `F2-lamp-in-doorway-5568-5152.png` (with a zoom) shows a lamp
   floating in front of the gap in the Main Plaza's east wall section, and
   `F3-lamp-in-doorway-2816-2080.png` (with a zoom) one over a dark opening
   in a wall face. Both were identified by projecting the reported
   coordinates from the Avatar's position; the lamp items were not listed
   by `findShape`.
6. **Map 11 on `cp22` shows the Earth, Fire and Water pillars standing and
   the Air pillar gone.** Not investigated; the save's column flags were
   not read.

## Harness anomalies

- `Ultima8Engine::loadGame N` ignores `N` and always loads slot 1
  (`debugger.cpp:198`). Checkpoints were loaded by copying them over
  `ultima8.001` (backed up first, restored after).
- `dbg.sh` replies sometimes arrive late or not at all; a helper that
  waited up to 3 s for a matching log line before resending read them
  reliably. Resending too early is one way the chord parity flips.
- `walkto.py` ran past a 400 s timeout with no output on the post-ceremony
  walk; manual `session.sh walk` bursts did the job.
- ScummVM aborted twice by design of P4; each abort leaves Xvfb running
  until `session.sh stop`.

## Disk changes

- `shared/u8-lv-patched/`: FIXED.DAT (both copies) and EUSECODE.FLX synced
  from `shared/build/` by `session.sh start`.
- `~/.local/share/scummvm/saves/ultima8.001`: overwritten with `cp23`, then
  `cp22`, during the session; restored from the backup, md5
  `083de1999baf65e68faf56aeca661710` as before. No other slot written, no
  save taken.
- `~/.config/scummvm/scummvm.ini`: nothing toggled; `[scummvm]` unchanged
  (`usehighres=true`, 640×400).
- No core file in the repository. The playtest session is stopped.
- `TODO.md` and `traps.md` not edited (the caller scoped this session to
  the report).

## Retest after the spawn fix (HEAD)

Verification of commit 1b0bf9a (EUSECODE `31d59466`; the engine logged
`usecode/eusecode.flx: 9a5295c3...`, 1,505,317 bytes, the md5-5000 the
commit names). `shared/build/ARTIFACTS.sha256` checked OK for all four;
`session.sh start` synced EUSECODE.FLX (the other three already matched).
Same binary, canvas and crop as above. Fresh world from `session.sh start`
(new game, name entered), so Map 17 was entered fresh and all three plaques
were present on the first `findShape 614`. Every teleport and `loadGame`-class
command was sent with the chord, the command and Return, and no `exit`.

| ID | Test | Observed | Verdict |
|---|---|---|---|
| P5 | q68 (5055, 9217, 16) double-click | item 7029, `calling usecode event 1 @ 04EB:00A9`; gump reads **FORBIDDEN / TO / MORTALS**; no crash | **PASS** |
| P6 | q69 (2495, 5121, 16) double-click | item 7344, event 1 @ 04EB:00A9; gump reads **FELICITAR / DOLORAS / TIMYRA**; no crash | **PASS** |
| P7 | q70 (5055, 5121, 16) double-click | item 7345, event 1 @ 04EB:00A9; gump reads **AMORAS / APATHAS / ODION**; no crash | **PASS** |
| T1 | Tiny Tar regression | item 8972 (859 frame 8, `n: 229`), event 1 @ 04E5:00A9; bark "Something strange is happening to me."; Avatar `shape 708 (uc: CHILD)`; potion then frame 0; back to `shape 1`, hp 30, same position | **PASS** |
| T2 | Frame 5 or 7 potion empties and acts | no frame 5 or 7 potion exists in the world and the debugger cannot create or reframe one | **NOT DEMONSTRATED** |

### P5-P7: the plaques read, PASS

Avatar teleported to 45 units west and 113 south of each plaque (for q68,
(5010, 9330, 0)); `findShape 614` then put the plaque at `px=(40,-4)` from
the Avatar, and it drew at window (351, 183). A double-click there logged,
for q68,

    Item 7029 (class Item, shape 614) (uc: PLAQUEEW), 0, (5055, 9217, 16) q: 68, m: 0, n: 235, ...
    Item: 7029 (shape 614) calling usecode event 1 @ 04EB:00A9

and 1.5 s later the gold plaque gump was up with the text. q69 and q70 gave
the same two lines with their own item numbers. No
`Trying to access segment 0000` and no `Assertion` line anywhere in the
session log (`grep -c` = 0), and the ScummVM pid was unchanged after each.
A single click on the gump closed it.

Plates: `P5-retest-plaque68-before.png` (the plaque on the wall beside the
Avatar), `P5-retest-plaque68-gump.png`, `P6-retest-plaque69-gump.png`,
`P7-retest-plaque70-gump.png`, and `P5-P7-retest-plaque-text-zoom.png`
(the three gump faces at 2x, stacked in order q68, q69, q70).

### T1: the Tiny Tar still shrinks and regrows, PASS

On Map 10, `findShape 859` listed the three chest potions (8972-8974,
frame 8, `n: 229`, contained) and the two ground ones (9056 frame 1, 9057
frame 2). `Item::grab 8972` answered `grab: 8972 in pack`; pack weight 20 →
30. With the Avatar on open paving at (22016, 6400, 0), the pack opened
(`T1-tiny-tar-in-pack.png`) and a double-click on the potion logged

    Item 8972 (class Item, shape 859), 8, (5, 13) q: 0, m: 0, n: 229, f: 0x200c, ...
    Item: 8972 (shape 859) calling usecode event 1 @ 04E5:00A9

with the bark **Something strange is happening to me.**
(`T1-drunk-strange-bark.png`, zoom `T1-drunk-strange-bark-zoom.png`; the
potion in the pack already shows the empty bottle). `objectInfo 1` then
read `shape 708) (uc: CHILD)`, same position (`T1-avatar-shrunk.png`), and
`objectInfo 8972` read frame **0**, still in the pack. About 70 s of wall
clock after drinking (the console was attached for part of that, which
pauses the game) `objectInfo 1` read `shape 1`, (22016, 6400, 0), hp 30,
weight 30 (`T1-avatar-regrown.png`). The frame-8 path spawns
`05AE` (`makeAvatarTiny`/`makeAvatarBig`) with a null `this` in the shipped
bytes, unchanged by the fix, which is what this run exercised.

While shrunk, `objectInfo 1` read `Container vol: 175/200, total weight:
520`; after regrowing, `175/250, total weight: 30`. Not investigated.

### T2: protection and invisibility potions, NOT DEMONSTRATED

No 859 potion of frame 5 or 7 is placed anywhere (`build_map_10.py` places
only frames 8, 1 and 2), and the fork's debugger has no create or
set-frame command. Static evidence only, from the shipped EUSECODE class
04E5 (`u8_usecode_disasm.py shared/build/EUSECODE.FLX 0x4E5`):

    034F: 40 06                    push dword [BP+06h]
    0351: 57 00 02 E5 04 65 04     spawn 00h 02h 04E5h 0465h   ; protection()
    03FF: 40 06                    push dword [BP+06h]
    0401: 57 00 02 E5 04 21 05     spawn 00h 02h 04E5h 0521h   ; invisible()

so both now receive the potion as `this`; whether `setFrame(0)` and the
effects run cleanly in the engine is untested.

### Harness notes for this retest

- The first `Cheat::toggle` after `start` produced no echo; the second gave
  `Cheats = true`.
- Twice a `dbg.sh`-style call got no reply and its letters reached the world:
  the minimap toggled and the backpack's `use` (item 512, class 0211) logged.
  Neither affected a test; each missed call was resent.

### Disk changes (retest)

- `shared/u8-lv-patched/USECODE/EUSECODE.FLX` synced from `shared/build/`.
- `~/.local/share/scummvm/saves/ultima8.000` was rewritten by the engine
  at 15:01; restored from a pre-session copy (md5
  `3e7dc241315324a28da53bca89c9621f`). `ultima8.001` untouched
  (`083de199...`).
- `~/.config/scummvm/scummvm.ini`: not edited. ScummVM rewrote it on
  launch (md5 `af255300...` before, `a143fa3b...` after); the result holds
  the expected eight keys (`usehighres=true`, 640×400, `scaler=normal`,
  `aspect_ratio=false`) and is byte-identical to an earlier session's copy
  in the scratchpad. The pre-session bytes were not kept, so a key-order
  change is the likeliest difference but is not proven.
- The playtest session is stopped; no core file.
