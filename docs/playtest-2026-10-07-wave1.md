# Wave-1 defect batch, verified statically and in engine (2026-10-07)

Change under test: the uncommitted working tree on `main` (TYPE_SHAPES retail
audit, schedule/DMG/status constants, run-time loopscript filters, waiting
`if pathfind`, string concat, `&`, `x.enterConvo()`, POTION/HRODNY/MAGNET/SIGRID
fixes, map moves on Maps 8/10/11/17/18/39) plus fork `lost-vale` tip
`0d1f7b21` (`976f3125` fast-area fix, `0d1f7b21` mover recreate).

Artifacts: EUSECODE `6b12ab85` (1,515,110 bytes, md5-5000 `e4b2b3fd`), FIXED
`14774b0b`. Session log: `usecode/eusecode.flx: e4b2b3fd..., 1515110 bytes`,
`Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)`. Plates are
in `docs/playtest-2026-10-07-wave1/` (640x400). The integrator's `M1`-`M4`/`M2b`
plates there are theirs and are kept; mine are `C*`.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| A0 | `tools/run_all_tests.sh` | **PASS** — `OVERALL: PASS — 41/41` |
| A1 | Full `tools/build_artifacts.sh` | **PASS** — exit 0, all four OK, byte-identical to the recorded hashes |
| A2 | Compilation Report | **PASS** — 48 files, 46 succeed; failures exactly `EALOGO.UNK`, `TJORVI.UNK`; warnings 544 |
| A3 | Fork patch equals fork diff; binary current | **PASS** — `diff -q` silent; `scummvm-lv/` tree diff equals the patch; binary 09:55:11, after `0d1f7b21` (09:54:07); detection table carries `e4b2b3fd`/1515110 |
| C1 | Passage Test with shape-481 whirlwinds | **PASS** (two clean runs; Shades-scene negative control PASS) |
| C2 | Aramina, Map 41 | **PARTIAL** — idle and forced-schedule halves hold; marker order and greeting not demonstrated; she was on Map 40, not 41 |
| C3 | Fast-area engine fix | **PASS** for the fix; **FAIL** on the claim's own premise (finding 1) |
| C4 | Hrodny "Tell me more of the cliffs." | **PASS** |
| C5 | NE village paint cycles, workbenches, abacus | **PASS** (old-save carryover caveat, finding 3) |
| C6 | Map 8 apparition | **NOT DEMONSTRATED** (budget) |
| C7 | Map 39 walls, Map 17 cushion, Map 18 urns, Map 11 boulder | **NOT DEMONSTRATED** (budget) |
| C8 | Key to the Clouds and elixir hand-overs | **NOT DEMONSTRATED** (budget) |
| C9 | Poison potion frame 4 | **NOT DEMONSTRATED** — no debugger verb creates an item, and no map places 859 frame 4 |
| C10 | Sigrid's leaveFastArea | **PASS** |
| C11 | Mover recreate | **PASS** (normal path only) |

## Method and harness writes

Saves (46 files) and `scummvm.ini` were backed up to
`/tmp/claude-1000/vfy1/bak/` with an md5 list. `./install_lv.sh` exited 0;
`session.sh start` found `shared/u8-lv-patched/` already current (sha256
checked). One session, one ScummVM pid. Checkpoints were loaded by copying over
`ultima8.001` and `Ultima8Engine::loadGame 1`: `run-s7-ragnar-stone.sav` (C1, three
times), `run-s13-shield-halves.sav` (C1 negative control), `cp22-hastea.sav` (C3, C4,
C5, C10, C11, C2). Writes: teleports with cheats on, each followed by `Cheat::toggle`
back to false; `Item::grab 15048`; `MainActor::toggleCombat` once; `Cheat::items`
once (500 coins, C5); `UCMachine::setGlobal 0x663 2 1` (C2);
`Ultima8Engine::saveGame vfy` into slot 1 (C11); `CameraProcess::moveToAvatar`;
`UCMachine::traceAll`/`stopTrace` once. Every menu answer was clicked from the
screen. Both egg scenes were entered on foot.

## C1: Passage Test, PASS

`run-s7-ragnar-stone.sav`, `Item::grab 15048` (weight 30 to 40), teleport to
(12800, 29720, 64), one 1.6 s walk north: `Item: 7570 (shape 73) calling usecode
event 7 @ 059A:0080` 1.1 s into the walk. The scene then ran with nothing touched.

- Mid-scene `findShape 481` read one item at 15 s, 29 s and 43 s, for example
  `Item 12371 (class Item, shape 481) (uc: MINIAIR), 28, (12745, 29673, 64)`;
  `findShape 400` read 0 every time. Frame 28 exists on 481 (36 frames).
- 0 `Skipping invalid shape`, 0 `Cycle in paint`, 0 `CombatProcess`.
- After: `avatarPoisoned`, `haveMark`, `plantScene`, `firstPoisoned` all 1;
  weight 30; `findShape 798` lists only the Map 0 copy (15048 consumed); Thordis
  `hp: 20`, `flags: 0`, and no process of any kind for item 106.
- Plates: `C1-scene-start.png`, `C1-whirlwind.png`, `C1-after-scene.png`.
  The integrator's `M1`-`M4`/`M2b` plates show the same run.

A first attempt was contaminated (my position-polling walk kept driving the
Avatar during the scene); its end state matched anyway and is not counted.

**Negative control, the Shades scene** (its two wind items are also
`TypeMiniAirTitan`). `run-s13-shield-halves.sav`, combat off, teleport Map 10
(20304, 17600, 4), walk into egg 9679 (`event 7 @ 05A5:0080`). Clicked from the
screen: **Let's be reasonable!**, **Yes, Priestess.**, **Please, High Priestess.**
(`C1x-shades-menu1..3.png`). After: `avatarPoisoned` 0, `shieldFixed` 1,
`inShadeScene` 0 (it read 1 for a few seconds after the egg's final resetRef);
Thordis, Atli, Ezrekal each `hp: 20`, flags unchanged from load; 0
`Skipping invalid shape`, 0 `receiveHit`, 0 `Unhandled intrinsic`
(`C1x-shades-after.png`).

## C2: Aramina, PARTIAL

In `cp22-hastea.sav` Aramina is on **Map 40** at (12927, 8575, 48), not Map 41,
and `araminaSchedule` (`0x663`, 2 bits) reads 0.

- **Idle, global 0: holds.** Arrival logged `event 15 @ 040D:0197` and the four
  resetRefs, then nothing: no process for item 13, 0 `Invalid item`, 0
  `stuck in process loop` (`C2-aramina-idle-schedule0.png`). CPU 95.8, 95.4,
  96.4%; the render loop keeps every map near 100%, so this reading shows a hang
  and little finer.
- **Forced, global 1:** `setGlobal 0x663 2 1` (read back `[0663 02] = 1`);
  leaving logged `event 16 @ 040D:022C` and the four resetRefs; returning logged
  `event 15`. Five reads 6 s apart: one `UCProcess, item 13, type 205` (atHome)
  throughout, `PathfinderProcess` count 0, 1, 1, 0, 0 (never two), then
  `ActorBarkNotifyProcess` type 200; she moved (12947,8835) to (13097,9013) to
  (13115,8867) to (12811,8779) (`C2-aramina-athome-forced.png`).
- **Not demonstrated:** that her searches matched shape-174 markers, and their
  order (no trace was run), and her "Yes, I am Aramina." greeting.
- One `Non-existent process PID (0) in implies` during this re-entry (see
  finding 6).

## C3: fast-area fix, PASS for the fix, FAIL as claimed

`cp22-hastea.sav`. **First approach** (same-map teleport to (21200, 8000, 0) +
`moveToAvatar`): `Item: 113 calling usecode event 15 @ 0471:0283`, resetRef
0x200, and **no LoiterProcess**. `hrodnySchedule` (`0x45F`) read 0. Finding 1.

**Round trip** to Map 3 (14527, 5887, 8) and back: `event 8` (schedule) set
`hrodnySchedule` to 1, `event 15` fired on return, and `LoiterProcess 3230, item
113, type 205` existed. Two reads 10 s apart: (22120, 8328) then (22000, 8208)
(`C3-hrodny-loiter.png`). That `event 15` on return is the fix's behaviour.

**Camera follow:** after a map-switch teleport with no `moveToAvatar`, a walk
from (21200, 8000) to (21424, 7776) left the Avatar centred
(`C3-camera-follow-after-mapswitch-2.png`). `moveToAvatar` itself parks a static
camera (`debugger.cpp:1277`, `new CameraProcess(pt)`); `C3-camera-follows.png`
is that parked camera, not a defect. `Kernel::listProcesses` always prints
`item 0` for the camera, because `CameraProcess` shadows `_itemNum`
(`camera_process.h:116`), so that listing cannot show what it follows.

Whole-session log: 0 `already exists in map chunk`, 0 `Segmentation`, 0
`Assertion`, 0 `stuck in process loop`; 13 `Non-existent process PID (0) in
implies` (finding 6).

## C4: Hrodny, PASS

Same save: `hrodnyMet`, `avatarPoisoned`, `haveMark`, `toldCliffs` all 1.
Double-click on her (`event 1 @ 0471:0BA4`) offered **Tell me more of the
cliffs.** and **bye** (`C4-hrodny-menu.png`). Picking it: "What more to tell is
there? Dangerous, they are in the old tales. Forbidden to climb they were! For
somewhere above the clouds, to the home of the gods." (`C4-hrodny-cliffs-answer.png`).
The next menu was **What about Tyorvi?** / **bye**: the option was removed after it
ran. Reaching her needed a teleport into the hut (finding 2).

## C5: NE village, PASS

- Standing at (21760, 8544, 0) for 60.0 s: 0 `Cycle in paint`
  (`C5-ne-village-standing.png`). After the map had been re-entered, 0 more for
  the rest of the session.
- Workbenches: `Item 8576 (shape 208) (uc: DESKNS), (21536, 7904, 0)` and
  `Item 27805 ... (21536, 9952, 0)`, both free-standing beside the hut corner
  (`C5-workbench-still-21536-7904.png`, `C5-workbench-workshop-21536-9952.png`).
- Abacus `Item 27814 (shape 375), (21836, 9808, 0)`, n 230. From (21960, 9808) a
  double-click ran `event 1 @ 04E6:00A9` and barked "You have 0 obsidian coins"
  (`C5-abacus-0-coins.png`); after `Cheat::items` (shape 143 x500, weight 110 to
  850), "You have 500 obsidian coins" (`C5-abacus-500-coins.png`). That proves the
  143 search, not just a bark.

## C6, C7, C8: NOT DEMONSTRATED

Not run: the session hit its request budget after C2. Setups for whoever runs
them:
- C6: `run-s1-lbdone.sav` (lbDone 1, Map 8 never visited), teleport Map 8 near
  (1696, 1216, 48); do not walk into the backstop egg at (2200, 2230).
- C8: `run-s12-root-given.sav` precedes Ezrekal's **Have you made the elixir?**;
  the Key hand-over follows it at Tyorvi (09-02 report P: **I have something for
  you from Ezrekal.** chain; the drunk branch is random, so retry).

## C9: NOT DEMONSTRATED

No debugger verb creates an item (`Item::grab` and `Item::setQuantity` only), and
no builder places 859 frame 4 (frames 1, 2, 8 only). Shape 859 has 9 frames, so
frame 4 exists.

## C10: Sigrid, PASS

Teleport to (7680, 6560): `event 15 @ 0466:01A9`; then `LoiterProcess`,
`PathfinderProcess 3849`, `ActorAnimProcess`. Adversarial run: waited until a
PathfinderProcess (5481) was live, then left by a fast teleport. Log:
`event 16 @ 0466:01CD`, then resetRef `item=102` 0x0205, 0x0204, 0x00F0, 0x0200.
Afterwards no process for item 102, and two reads 12 s apart both
(8100, 6340): she stopped. In 10-04 she walked for over a minute.

## C11: mover recreate, PASS (normal path)

`strings scummvm-lv/scummvm` has `%s AvatarMoverProcess in savegame; recreating`.
`saveGame vfy` into slot 1, `loadGame 1`: `U8AvatarMoverProcess` pid 3, 0
`recreating` lines in the whole session, and the Avatar walked (12000, 12000) to
(11696, 12000) (`C11-walk-after-save-load.png`). The recreate branch itself was
not triggered (it needs a save with a dead mover).

## Findings outside the plan

1. **The new schedule constants leave Thordis and Hrodny without an activity
   whenever their schedule global is 0, and in real saves it often is.**
   `at_home` is now 1 and `in_field`/`at_work` 2, so `enterFastArea`'s two
   branches (`THORDIS.UNK:282-291`, HRODNY likewise) match neither 0. The
   globals are written only in `schedule()`, and only when `canSafeTeleport`
   succeeds. `run-s7-ragnar-stone.sav` has `thordisSchedule`, `hrodnySchedule`,
   `ingyaldSchedule`, `araminaSchedule` all 0, and **no SchedulerProcess** in its
   process list. `cp22-hastea.sav` also has `hrodnySchedule` 0: Hrodny got no
   loiter on approach until a map round trip ran her `schedule()`. Worse,
   `Thordis::schedule` returns early while `plantScene = true` (`:234`), and
   `plantScene` stays 1 after the Passage Test, so a world with
   `thordisSchedule` 0 at that point never gives Thordis an activity again. After
   both C1 runs she stood at the test grounds with no process at all. The
   symbols comment ("at most 900 game seconds") assumes the scheduler runs and
   the write succeeds; neither held here. Confidence high on the mechanism, from
   the source plus the observed 0 values. Fix candidates: map global 0 to the
   home branch, or have `enterFastArea` fall back to loiter.
2. **Hrodny wedges in the NE village hut's south wall.** Her loiter took her to
   about (21370, 8598) and she jittered within 40 units there for minutes.
   Within seconds of a map reload putting her back on her slot (21760, 8448), she
   was back there. Only her head and shoulders clear the wall top (pixel
   (306, 228) with the Avatar inside the hut), so a player outside cannot click
   her. Not shown to be new.
3. **An old save carries the old Map 10 layout until the map is re-entered.**
   `cp22-hastea.sav` (08-17) logged 4,818 `Cycle in paint` lines (`426 -> 208`,
   `426 -> 856`, `859 -> 526`, 1,606 each) between load and the first Map 3 hop,
   then 0 for the rest of the session. Players with existing saves keep the
   cycles until they leave Map 10 once.
4. **`Unhandled intrinsic 101 'process Item::combine()'` is not shape 400's.**
   It and `Trying to access segment 0000!` fired once per Passage Test in both
   clean runs, with no shape 400 in the world. 10-03 finding 2 attributed it to
   the fire field's events; the source is elsewhere in the scene, most likely a
   `combine` call that resolves to the intrinsic outside LVFREE. Not localized.
5. **Thordis is still stranded at the test grounds** (12927, 29823, 64) after the
   Passage Test (09-02 report N), and `run-s13-shield-halves.sav` already carries
   her there.
6. **13 `Non-existent process PID (0) in implies` lines** this session. The
   first 8,600 log lines (C1, Shades, C3, C4, C5) had 0. They came during
   C10/C11/C2, one of them on Aramina's forced atHome re-entry. Not attributed.
7. **`Kernel::listProcesses` shows every CameraProcess as `item 0`** (shadowed
   `_itemNum`). Any earlier report that read "camera static" from that column is
   unsupported.

## Harness anomalies

1. `h.py`'s `cheats()` is a toggle; calling it to "read" the state flipped cheats
   on once (caught by its echo and flipped back).
2. My position-polling `goto` walked the Avatar through the first Passage Test
   scene; that run was discarded and redone hands-off.
3. A first Shades attempt teleported to Map 17 (the 10-03 report's coordinates
   are Map 10).
4. ScummVM rewrote `ultima8.000` (slot 0) during the session; restored from
   backup.

## Disk changes

- Wrote `docs/playtest-2026-10-07-wave1.md` (this file) and the `C*` plates in
  `docs/playtest-2026-10-07-wave1/`. The integrator's `M*` plates are untouched.
- `./install_lv.sh` and `tools/build_artifacts.sh` rewrote `shared/build/*` and
  the installed copy, byte-identical to the recorded hashes.
- Saves: all 46 files in `~/.local/share/scummvm/saves/` restored and
  md5-verified against the pre-session list; `scummvm.ini` md5 `af255300`
  unchanged. The session's own slot-1 save is kept at
  `/tmp/claude-1000/vfy1/sp/slot1-vfy-session.sav`, and the session log at
  `/tmp/claude-1000/vfy1/session.log`.
- No source, builder, map, fork, TODO, or commit touched. Session stopped.

# Part 2: retest after the finding-1 fixes (2026-10-07, second verifier)

Change under test: the same uncommitted batch, plus three changes made after
part 1 that answer its finding 1. In `u8c_codegen.py`, an unresolved
function or method used as a value now pushes 0 instead of `push retval`.
`lv-patched/THORDIS.UNK` change 2 now reads `!= in_field`, and
`lv-patched/HRODNY.UNK` change 5 now reads `!= at_work`. Artifacts: EUSECODE
`f24e5491` (md5-5000 `1a038851`, 1,515,119 bytes), FIXED `14774b0b`. Session
log: `usecode/eusecode.flx: 1a038851e689625f430e78573f708e94, 1515119 bytes`.
Plates are the `R*` files in `docs/playtest-2026-10-07-wave1/`.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| A0 | `tools/run_all_tests.sh` | **PASS**: `OVERALL: PASS — 41/41` |
| A1 | Full `tools/build_artifacts.sh` | **PASS**: exit 0; TYPEFLAG `9f534e59`, U8SHAPES `a611e9be`, EUSECODE `f24e5491` and FIXED `14774b0b` all OK |
| A2 | Compilation Report | **PASS**: 48 files compiled, 46 succeeded; the only failures are `EALOGO.UNK` and `TJORVI.UNK`; 544 warnings |
| A3 | Fork patch, detection entry, binary | **PASS**: `diff -q` prints nothing; `build_scummvm.sh` has `LV_MD5="1a038851…"` and `LV_SIZE="1515119"`; the binary (11:32:06) contains `1a038851` once and `e4b2b3fd` zero times |
| A4 | Static check of the `canSafeTeleport` fix | **PASS**: in `schedule()` of both classes the condition is `push byte 0; jne` around the `pop global` (HRODNY 0471:0277, THORDIS 046A:0297); `enterFastArea` is `push global …; push byte 2; ne` |
| R1 | Finding 1 fixed (Hrodny, Thordis, Thordis after the Passage Test) | **PASS**, with a new defect found in the process (finding P2-1) |
| R2 | Passage Test rerun on the new bytes | **PASS** on the claim's five points; 3 new `Cycle in paint 707 -> 481` lines in run 1 |
| R3 | Hrodny "Tell me more of the cliffs." | **PASS** |
| R4 | Map 8 apparition, 0 paint-cycle lines | **PASS** |
| R5 | Map 39 walls, Map 17 cushion, Map 18 urns, Map 11 boulder | **PASS** for Map 39, the cushion and the boulder; **PARTIAL** for the urns (the walls hide them from the camera) |
| R6 | Elixir and Key to the Clouds hand-overs | **PARTIAL**: the elixir hand-over passes; the Key chain was not completed (budget) |
| R7 | Log hygiene | **PASS**: 0 `PID (0) in implies` in 4,429 log lines; 3 `Cycle in paint`, 0 `stuck in process loop`, 0 Segmentation, 0 Assertion |

## Method

I backed up all 48 save files and `scummvm.ini` (md5 list) to
`/tmp/claude-1000/vfy2/bak/` and ran `./install_lv.sh` (exit 0).
`session.sh start` synced `USECODE/EUSECODE.FLX`. One session ran, with one
ScummVM pid. I loaded each checkpoint by copying it over `ultima8.001` and
running `Ultima8Engine::loadGame 1`: `cp22-hastea.sav` (R1 and R3),
`run-s7-ragnar-stone.sav` (R1 and R2, loaded twice), `run-s1-lbdone.sav` (R4
and R5) and `run-s12-root-given.sav` (R6).

The game state was changed only by the following:
- teleports with cheats on, each followed by `Cheat::toggle` back to false;
- `Item::grab 15048`, twice;
- `MainActor::toggleCombat`, once, because `run-s12` loads in combat;
- `CameraProcess::moveToAvatar`;
- `UCMachine::traceClass 0x46A` and `stopTrace`;
- `MainActor::useBackpack`.

Every menu answer was clicked from the screen. The Passage Test egg was
entered on foot.

**Camera note.** `run-s7`, `run-s12` and `cp22` all load with a parked
camera. After a same-map teleport the Avatar therefore lands outside the
fast area (`f: 0x41`, with no `0x2000` bit) and cannot walk until
`moveToAvatar` runs. A map-switch teleport gives a camera that follows the
Avatar. The first-approach tests below use the second kind.

## R1: finding 1 fixed, PASS

**Hrodny, `cp22-hastea.sav`.** At load, `hrodnySchedule` (`0x45F`) read 0 and
Hrodny was at (21658, 8338) with `f: 0x40`, so she was outside the fast area
and had no process. I did a same-map teleport to (19600, 8000), then
`moveToAvatar`. That logged `Item: 113 calling usecode event 15 @ 0471:0284`
and `I_resetRef item=113 type=0x0200`. Before any map change she then had
`LoiterProcess 3281, item 113, type 205`, plus a pathfinder. Four reads 13 s
apart showed her moving: (21602, 8282) → (21782, 8462) → (21722, 8062) →
(21606, 8342).

After a hop to Map 3 and back, `event 8` (`schedule`) ran for 106 and for 113.
Both globals still read 0. That is the negative control for the codegen fix:
in part 1, the same round trip wrote 1 from the stale retval.

When I came back to her, `event 15` fired again. After the R3 conversation she
was loitering again (`LoiterProcess 5927`). The branch bytecode decides
home or work: with global 0, `ne 2` takes the home spawn (0471:041A).
`randomBarkAtHome` (`HRODNY.UNK`, the patched file) is a one-shot process,
not a loop: it barks once, or not at all on 5 of 12 rolls when the Avatar is
more than 200 away. So I did not count "no bark seen" as a failure.

**Thordis, `cp22`, first approach on foot.** She was at (6140, 6720) with
`f: 0x60` and `thordisSchedule` (`0x453`) read 0. I turned on
`UCMachine::traceClass 0x46A` and walked west from (8100, 6656). At
(7804, 6656) she entered the fast area, and the trace logged:

    Item: 106 (shape 707) calling usecode event 15 @ 046A:02A4
    tick 2304660 running process 3837, item 0, type 0, class 1130, offset 1108

Offset 1108 = 0x454 is the home branch's spawn target (`spawn … 046A 0454` at
046A:02FC). The field branch would spawn at 0x847. After that she had
`LoiterProcess 3835` and moved (5800, 6960) → (6440, 6780) → (5840, 6540).
Plate: `R1-thordis-first-approach-loiter.png`; she is top left.

**Thordis after the Passage Test, leave and re-enter.** Run 1 of R2 left her
with `LoiterProcess 7465`. I did a same-map teleport to (12518, 12062) plus
`moveToAvatar`. That logged `event 16 @ 046A:0332` and resetRefs 0x205,
0x204, 0xF0 and 0x200, and left her with no process. Coming back to
(13055, 30079, 64) logged `event 15 @ 046A:02A4`, and she had
`LoiterProcess 953`. In part 1 she had no process at all here. Plate:
`R1-thordis-reentry.png`, which also shows finding P2-1.

**Hrodny's wedge (part 1, finding 2): not seen.** I read her position 11 times
over about 4 minutes, at x 21422-22236 and y 8062-8920. She never stopped
near (21370, 8598).

## R2: Passage Test, PASS

`run-s7-ragnar-stone.sav`, `Item::grab 15048` (weight 30 → 40), teleport to
(12800, 29720, 64), `moveToAvatar`, one 1.6 s walk north.
`Item: 7570 (shape 73) calling usecode event 7 @ 059A:0080` logged 1.8 s
after the walk started.

- At 15.4 s, `findShape 481` found `Item 3692 (class Item, shape 481) (uc:
  MINIAIR), 8, (12745, 29673, 64)`. `findShape 400` found 0. Plates:
  `R2-scene-start.png`, `R2-scene-10s.png`, `R2-whirlwind.png`.
- Log: 0 `Skipping invalid shape`, 0 `CombatProcess`, 0 `receiveHit`. One
  `Trying to access segment 0000!` and one `Unhandled intrinsic 101
  'process Item::combine()'` (part 1, finding 4, unchanged).
- After the scene: `avatarPoisoned`, `haveMark`, `plantScene` and
  `firstPoisoned` all read 1. Weight was 30. `findShape 798` found only the
  Map 0 copy (13751), so 15048 was consumed. Thordis had `hp: 20` and flags
  `800408` (PATHFINDING|FIRSTSTEP|ANIMLOCK, not INCOMBAT). Plate:
  `R2-after-scene.png`.
- **New in run 1:** 3 `Cycle in paint dependency graph 707 -> 481 -> ... ->
  707`, logged while Thordis overlapped the whirlwind. Part 1 had 0. A second
  run logged 0. The cause is in finding P2-1: Thordis now moves during the
  scene.

Run 2 (reloaded and repeated) ended in the same state: four flags 1, weight
30, stone consumed, `hp: 20`, flags 0.

## R3: Hrodny, PASS

`cp22` again, with the Avatar beside her in the NE village. A double-click
logged `event 1 @ 0471:0BA5`, and the menu offered **Tell me more of the
cliffs.** and **bye** (`R3-hrodny-menu.png`). Picking it gave "What more to tell
is there? Dangerous, they are in the old tales. Forbidden to climb, they were.
For somewhere above the clouds, to the home of the gods."
(`R3-hrodny-cliffs-answer.png`).

Negative control: the next menu was **What about Tyorvi?** / **bye**, so the
option was gone after it ran (`R3-hrodny-next-menu.png`).

## R4: Map 8 apparition, PASS

`run-s1-lbdone.sav` loads on Map 8, inside the backstop egg's box at
(2200, 2300, 8), with `findShape 411` = 0: the old save's cleanup has
already run. A hop to Map 3 and back reloaded the fixed items. After that,
`Item 15487 (class Container, shape 411) (uc: GHOST), 0, (2200, 2208, 8)` was
in the fast area.

I stood outside the egg box at (2200, 2470, 8) for 60 s with the apparition
and the cups in view. `ObjectManager::findShape` put cups at (2230, 2266, 16)
and (2228, 2300, 16) and the table 263 at (2260, 2340, 0). That window logged
0 `Cycle in paint`, as did the whole Map 8 visit (`R4-map8-apparition-60s.png`).

The egg box was worked out with the engine's own arithmetic
(`EggHatcherProcess::run`: npcnum 0x44 → ±128). It is x 2072-2328 and
y 2102-2358. `justTeleported` suppresses only *teleport* eggs, so arriving
by teleport inside a scene egg's box hatches it anyway; that is why I stayed
outside.

## R5: art placements, PASS / PARTIAL

**Map 39:** I plated three positions: (14064, 20300, 8), (14064, 19720, 8) and
(14260, 19950, 48). The `R5-map39-*.png` plates show no tuft line on the
wall faces.

I compared the plates with part 1's `R2-C1f-02` from the same position. They
differ in 957 pixels, all inside the south wall's west face (the band at
y 210-260, where the green line used to be). The north-wall region is
identical, byte for byte. `findShape 15` lists the z 48 courses at y 19455
and 20511 as frame 0.

**Map 17:** `Item 11655 (shape 812) (uc: CUSION), 3, (6752, 3248, 0)` is
visible in front of the desk (`R5-map17-hall-b-cushion.png`). A single click
on it logged that same item, so it can be clicked.

**Map 18 urns, PARTIAL:** the engine places them at (5087, 6272, 0),
(1120, 8671, 0) and (5087, 8671, 0). Each box ends at the first unit the
wall owns, and there were 0 cycles. However, these three urns stand in the
inside corners of the east and south walls, and U8's fixed view angle draws
those walls in front of them. None of the three can be seen from any
position (`R5-map18-urn-*.png`), so "sits flush" could not be shown on
screen. See finding P2-2 for what those plates showed instead.

**Map 11:** the boulder `Item 8823 (shape 796) (uc: FALLROCK), 3,
(2592, 1248, 0)` stands on the floor, clear of the stalactite `Item 8699
(shape 186), (2524, 1248, 48)`. There were 0 cycles
(`R5-map11-boulder-2592-1248.png`).

## R6: hand-overs, PARTIAL

**Elixir: PASS.** `run-s12-root-given.sav` (loads in combat; toggled off). The
double-click logged `event 1 @ 0474:031C`, and the menu offered **Can you help
me?**, **Have you made the elixir?** and **bye** (`R6-ezrekal-menu.png`).
Picking the elixir option gave "Yes, I have. Take it to him now you can."
(`R6-ezrekal-elixir-answer.png`) and then "Hope it helps him, I do."

Afterwards, `hasTea` (1062) went from 0 to 1. `Item 11991 (shape 395), frame
13`, flags `0xc`, sits in the pack at pack position (0, 0)
(`R6-pack-after-elixir.png`). Total weight stayed at 30: shape 395 is family
9 (reagent), which seems to carry no weight. The pack also already held
`Item 4528 (shape 82), q 99` before this hand-over; this checkpoint follows
`run-s12-key-in-pack`.

**Key chain: not completed.** At Tyorvi (`event 1 @ 0473:032A`,
`R6-tyorvi-menu.png`) I clicked:

    I have something for you from Ezrekal.
    It is an elixir.
    It will heal your dreams.
    Just try it, please.

The replies were drunk-branch lines ("Want nothing from that old bag", "Take
nothing from that bag I will!"), then "Oh, all right. Give it to me"
(`R6-tyorvi-give-it-to-me.png`).

The conversation then closed by itself. `givenTea` stayed 0, the bottle 11991
was still in a container, and `findShape 82` was unchanged. **May I have the
Key to the Clouds?** was never offered. I stopped there because of the
budget. I could not tell whether this is the documented drunk branch (the
2026-09-02 report says to re-open until the sober one comes up) or a defect.
Retry it with several re-opens.

## R7: log hygiene, PASS

The whole session was 4,429 log lines (copied to
`/tmp/claude-1000/vfy2/session.log`). It logged 0 `Non-existent process PID`,
0 `stuck in process loop`, 0 `Segmentation`, 0 `Assertion`, 0 `Skipping
invalid shape` and 0 `already exists in map chunk`. It also logged
3 `Cycle in paint` (R2 run 1, 707 → 481) and 2 `Unhandled intrinsic 101`
(one per Passage Test).

Because none occurred, the PID-0 lines could not be attributed. The tool is
in place, though: `UCMachine::traceClass` logs `tick N running process P,
item I, type T, class C, offset O` before each run, so the most recent such
line ahead of a warning names the class and resume offset. `DEBUG_USECODE` is
off in this build, so there is no per-opcode trace. Part 1's 13 lines came
during C10/C11/C2 (Sigrid, save/load, Aramina), which I did not rerun. The
2026-10-04 report attributes one such line to Devon's farewell. This session
clicked through that farewell, then loaded about 6 s later and saw none.

## Findings (part 2)

1. **The fix makes Thordis loiter *during* the Passage Test, and in one of two
   runs she ended up under the test grounds' floor.**

   `PLNTST.UNK:91-92` does `killProcess(Thordis, PT_ACTIVITY)` and then
   `Thordis.teleport(12927, 29823, 64)`. The teleport puts her into the fast
   area, so `enterFastArea` runs: in the log, resetRef 0x205 is followed
   immediately by `event 15 @ 046A:02A4`. With global 0 that now spawns the
   loiter and bark. The scene's kill is undone, and she wanders through the
   whirlwinds; part 1 had her standing still.

   In run 1 she was on the plateau in `R2-whirlwind.png`. By 72 s she was at
   (13047, 29871, **0**), and later reads all had z 0 at x 12399-13119,
   y 29463-30003. That is inside the footprint of the z 64 plateau. Only her
   head shows, below its south-west edge (`R1-thordis-reentry.png`, at about
   (280, 218)), and she cannot be clicked there. Run 2 kept her at z 64-72
   for 5 minutes.

   `Thordis::schedule` returns while `plantScene` is set, and its teleport
   is now permanently dead (`canSafeTeleport` → 0). So a Thordis who drops
   there stays under the floor. Later steps that need her (the bag, for
   example) would then be unreachable.

   Confidence: high that the loiter runs during the scene (log order, plus
   the source). Medium on how she reached z 0; I did not film the drop.
   Pre-pin builds took the same branch (`at_home` was 0), so this is old
   behaviour coming back, not new code. Possible fixes: kill the activity
   *after* the teleport in PLNTST, or have `enterFastArea` skip the loiter
   while `plantScene` is set.

2. **The Inner Sanctum's south-wall columns are embedded in the wall.** This
   is the same class of defect as the urns and the cushion.
   - Plinth 113 sits at (1584, 8720, 0) and at (4656, 8720, 0), and is
     128x128 according to the Map 17 comment in this diff. Its box is
     y(8592, 8720], which crosses the south wall's y(8671, 8703] and sticks
     17 units out of its outer face.
   - Their columns, shape 249, are at (1536, 8672) and (4608, 8672).
   - From outside, plinth and column are painted on the wall's face: in
     `R5-map18-urn-SE-5087-8671.png` at about (200, 200), and in `R5-map18-urn-SW-1120-8671.png`
     at about (310, 270).
   - This predates the change; `build_map_18.py`'s diff touches only the
     urns.
3. **Saves that load with a parked camera.** `run-s7`, `run-s12` and `cp22`
   load with a parked camera, and `run-s7`'s also has the minimap open. A
   same-map teleport then leaves the Avatar outside the fast area, and he
   cannot walk. The first R2 walk did nothing for that reason, and the scene
   egg could not fire. Anyone repeating the part-1 recipe needs
   `moveToAvatar` after the teleport. The checkpoints predate `f9a9aba`.
4. **The stated test for the codegen change is weaker than it reads.**
   `test_codegen_retail_forms.py` §8 checks `b'\x5e' not in data`, which
   would also fail on any 0x5E operand byte, and it does not cover `push byte
   retval` (0x5D) or `push long retval` (0x5F). The shipped bytes are right
   (row A4); this note is only about how much the test can catch.

## Harness anomalies (part 2)

1. The `con()` expect pattern for `UCMachine::traceClass` never matched, so it
   reported "no reply" twice. The trace was on all the same (its lines are
   in the log).
2. The first R2 attempt ran with the parked camera, so the walk did nothing
   and the egg never fired. I took no flags from it. Its plates were deleted;
   the `R2-*` files that remain are from the counted run.
3. Single-click identification hit floor, wall and furniture objects several
   times before reaching the moving NPCs (Hrodny 4 misses, Ezrekal 6).

## Disk changes (part 2)

- Appended this section to `docs/playtest-2026-10-07-wave1.md` and added the
  26 `R*` plates in `docs/playtest-2026-10-07-wave1/`. Part 1's `C*` plates
  and the integrator's `M*` plates are untouched.
- `tools/build_artifacts.sh` and `./install_lv.sh` rewrote `shared/build/*` and
  the installed copy, byte-identical to the recorded hashes. `session.sh start`
  synced `shared/u8-lv-patched/USECODE/EUSECODE.FLX`, which was stale.
- Saves: all 48 files restored. They and `scummvm.ini` md5-match the
  pre-session list (`diff bak.md5 after.md5` prints nothing). The session is
  stopped and no ScummVM process is left.
- Scratch files, drivers, logs and the backup are in `/tmp/claude-1000/vfy2/`.
- No source, builder, map, fork, TODO or commit was touched.

# Part 3: Thordis stands still during the Passage Test (2026-10-07, integrator)

Answers part 2's finding 1. `lv-patched/THORDIS.UNK` change 3 makes
`enterFastArea` return while `plantScene` is set, the guard `schedule()`
already has. Build EUSECODE `3943f176` (md5-5000 `1a038851`, 1,515,130
bytes), FIXED `14774b0b`; estate 41/41; the ScummVM log names the same bytes.

| Test | Verdict |
|---|---|
| T1 Thordis gets no loiter mid-scene and stays on the plateau | **PASS** |
| T2 Her dialogue still opens afterwards | **PASS** |

**T1.** `run-s7-ragnar-stone.sav`, `Item::grab 15048`, teleport Map 10
(12800, 29720, 64), `CameraProcess::moveToAvatar`, walk north into the egg.
One `resetRef item=106 type=0x0205` (the scene's killProcess; no 0x0200
follows, because `enterFastArea` now returns before its bark reset). After
40 s `plantScene`, `haveMark` and `avatarPoisoned` read 1. Three reads 20 s
apart: no process for item 106, position (12927, 29823, 64) every time
(`M6-thordis-guard.png`).

**T2.** A double-click on her ran `use()`; her speech starts "Oh my, terrible
this is. Sent you here Atli did?" (`M7-thordis-talk.png`), and the
conversation's resetRefs name only item 106.

**Not demonstrated:** the loiter after the scene-end conversation clears
`plantScene`, and whether a later loiter on the plateau walks her off it.

Disk changes: slot 1 was overwritten with the checkpoint and restored
(md5 `083de199` before and after); session stopped.
