# Batch merge B, C, D on main, verified statically and in engine (2026-10-03)

Change under test: `dc5ef31` (D, breach rubble rework, `eaf6e72`),
`071d552` (C, Map 39 grass edge and Map 17 tapestry, `dfa73f5`), and `55414d4`
(B, reagent bag slow refill, `f1a1302`), on top of `28933d5` (killProcess).
Plus the uncommitted rehash: `shared/build/ARTIFACTS.sha256` (EUSECODE
`2efc9e91`, 1,507,070 bytes; FIXED `7650fba3`) and `build_scummvm.sh`
(`LV_SIZE 1507070`, `LV_MD5 4f47de88` unchanged).

Artifacts: `tools/build_artifacts.sh` reproduced all four recorded hashes.
Binary `scummvm-lv/scummvm` built 2026-10-03 20:31 CDT, after the fork tip
`e0d6084d` (2026-09-19); its `detection_tables.h:297` reads
`4f47de88..., 1507070`. All five session logs read
`usecode/eusecode.flx: 4f47de8811f7fc091c3fa2fabe988283, 1507070 bytes.`
Plates are in `docs/playtest-2026-10-03-batch-merge/`, 640x400, named by
test ID.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| C0 | Build, hashes, estate, detection | estate 37/37; build exit 0, all four OK; Compilation Report 46 of 48 (`EALOGO.UNK`, `TJORVI.UNK`); fork patch equals the fork diff; every session log reads `4f47de88..., 1507070 bytes` | **PASS** |
| B1 | Reagent bag slow refill | tag `q: 1` on the new bag; split curve 13, 18, 23, 25; recreated frame 5, 10, 15, 20, 25; ground, backpack, and whole-stack-in-backpack controls all hold; a split made inside the bag gives two stacks that both refill, 25 to 50 in about 38 s | **PARTIAL** (metering FAIL, finding 4) |
| C1 | Map 39 south grass edge | straight and diagonal pushes hold at z 48 at eight x from 15500 to 20300, and the oaks refuse a directional jump (the targeted jump was not demonstrated); the black band south of the oaks is reached on foot from the lane by two routes, the platform rim and the avenue east edge | **FAIL** (closure) |
| C2 | Map 17 NE tapestry | loaded at (6016, 5121, 0); only a small dark mark shows above the east wall's top, the same as the 09-26 plate; the east wall stands in front of the tapestry | **FAIL** |
| D1 | Map 18 breach rubble | from the hall the spill and piles show over the wall under the crack; all frames exist, all z 0; 0 `Cycle in paint`; the new hall-side rock is hidden behind the wall; the open-breach view was not reached | **PARTIAL** |
| D2 | Crack hint once-only and nudge | first arrival without potions: three observation barks in order, flag 0 to 1; return without potions: egg hatches, silence; return with potions: no observation bark, the nudge only, three times | **PASS** (finding 9) |
| A1 | Map 41 Aramina regression | leave logs `resetRef item=13` 0x0205, 0x0204, 0x00F0, 0x0200; no item-13 process after; 0 `Invalid item 1037` | **PASS** |
| L | Log health, five sessions | 0 `Non-existent process`, 0 segfaults, 0 assertions, 0 `Cycle in paint`; 3 `stuck in process loop` in session 2, all from my teleport into a retail wall | **PASS** (3 lines attributed to the harness) |

## Method and harness writes

Saves (48 files, md5 list) and `scummvm.ini` (`a143fa3b`) were copied to
`/tmp/claude-1000/v1003b/bak/` first and restored at the end. `./install_lv.sh`
exited 0. The first `session.sh start` synced EUSECODE (`a908cb53` to
`2efc9e91`) and both FIXED.DAT copies (`f92973ee` to `7650fba3`) into
`shared/u8-lv-patched/`. Five sessions, one ScummVM pid each. Devon's opening
menu was closed at each fresh start by clicking **Goodbye** off the screen.

Writes, all disclosed:

- **Teleports with cheats on**, each followed by `Cheat::toggle` back to
  `Cheats = false` before movement or clicks. Session 1: Map 39 (14700, 20150,
  48) and (14700, 19980, 48). Session 2: Map 39 (15500, 20040, 48),
  (14600, 19980, 48) twice, (14600, 20060, 48). Session 3: Map 39
  (14600, 20060, 48), (17000, 20060, 48); Map 17 (5950, 5450, 0); Map 41
  (16671, 19200, 48). Session 5: Map 10 (18432, 22680, 0). Two of these
  landed inside solids (harness anomalies 1 and 2).
- **Checkpoint loads** through slot 1: the 09-29 scratch save
  `godsfree-at-exit-map18-2026-09-29.sav` (session 4) and
  `~/lv-checkpoints/run-s16-tinytar.sav` (session 5).
- `Ultima8Engine::saveGame 1` once, after the bag hand-over; copied to
  `/tmp/claude-1000/v1003b/sp/bag-q1-map10-2026-10-03.sav` (a world whose bag
  carries the `q 1` tag; no earlier checkpoint has one).
- `Item::grab` six times: three stale ids that answered `grab: no item`, then
  potions 5757, 8137, 8618.
- `CameraProcess::moveToAvatar` once (the run-s16 save's parked camera).
- Logging and display: `debugflag_enable Object`, `UCMachine::traceClass
  1457` and `stopTrace`, `GameMapGump::toggleFootpads` (left off).
- Reads: `objectInfo`, `findShape`, `getGlobal`, `Kernel::listProcesses`.

Every egg in this report hatched from a walk: the endgame pad (crossing from
Map 18), every Map 18 entry through trigger 211, and all four crack-hint
hatches. The Map 39, Map 17, and Map 41 positions were reached by teleport,
because those tests are geometry and process lifetime. Every menu answer was
clicked from the screen.

## C0: build, hashes, estate, PASS

- `tools/run_all_tests.sh`: `OVERALL: PASS`, 37/37, including
  `test_map39_south_edge.py` 17 passed and `test_uc_eggs.py` 80 passed.
- `tools/build_artifacts.sh`: exit 0; `TYPEFLAG.DAT OK 9f534e59`,
  `U8SHAPES.FLX OK a611e9be`, `EUSECODE.FLX OK 2efc9e91`, `FIXED.DAT OK
  7650fba3`. EUSECODE 1,507,070 bytes; `head -c 5000 | md5sum` gives
  `4f47de88...`; FIXED 1,848,976 bytes.
- Compilation Report: 48 files, 46 succeed, failures `EALOGO.UNK` (line 14,
  unterminated block comment) and `TJORVI.UNK` (line 575, unterminated
  string), the `DEV_ALLOWLIST` pair; 508 warnings, none in `ENDGAME.UNK` or
  `CRACKHNT.UNK`.
- Fork: `lost-vale` tip `e0d6084d`; the patch-equality `diff -q` is silent.
  No fork commit in this change.

## B1: reagent bag slow refill, PARTIAL

**Getting a tagged bag.** No checkpoint holds a bag made after `setQ(1)`
landed (30 September), so the bag came from Ezrekal in this build. The 09-29
save (Map 18 at the exit, `godsFree` 1, `endgameStarted` 0, `hasBag` 0): a
walk north into the exit trigger loaded Map 10 0.70 s into the walk; the
endgame scene played; `endgameStarted` 1, and the top-up was process 632
(`EGGENDGA`, item 0, `05AA:04E6`). The 09-29 route on foot to the stockade,
a double-click on Ezrekal (`event 1 @ 0474:031C`), menu
(`B1-01-ezrekal-menu.png`): **I have freed your gods!** Afterwards
`hasBag` 1; bag **12442** reads **`q: 1`**; six shape-395 stacks of 25,
frames 0, 6, 8, 9, 10, 14 (`B1-03-after-handover.png`).

Quantities below come from `findShape 395`, which lists every stack with its
quantity and either a world position (W) or gump coordinates.

| Test | Action | Readings | Result |
|---|---|---|---|
| T1 | 12 of frame-9 stack 12444 to the ground (`B1-07`, `B1-08`) | bag stack 13 (5.3 s), 18 (10.8 s), 23 (23.6 s), 25 (29.0 s), then 25; ground stack 12 throughout | holds |
| T1 control | the two ground stacks (5078, 15288) | 12 at every read for about 4 minutes | holds |
| T2 | 12 of 12444 into the backpack | backpack stack 6770 at 12 for 44 s; bag stack 18, 23, 25 | holds |
| T3 | all of 12444 onto 6770 in the backpack (`SplitItemProcess splitting: 25: 0-37`) | bag holds 5 items, no frame 9, for 49 s; 6770 stays 37 | holds |
| T4 | all 37 of 6770 to the ground (`37: 0-37`) | new stack 16178 inside the bag at 5 (12.7 s), 10, 15, 20, 25; ground stack 37 untouched (`B1-16-T4-after.png`) | holds |
| T5 | 12 of 16178 dropped on the same bag's own floor (`12: 13-12`, `B1-17-T5-in-bag-slider.png`) | 16178 13, 18, 23, 25 and new 15432 12, 17, 22, 25, both inside the bag (bag holds 7 items) | **frame 9 in the bag doubled, 25 to 50, in about 38 s** |

The first T1 run read 13 at 5.2 s and 25 at 19.4 s, which looked like a
single step of 12. The repeat with reads every few seconds shows three polls
inside that gap; the bytecode does one `setQuantity` per stack per poll
(`05AA:0557` to `057A`). The steps land 6 to 13 s of wall time apart,
including the time each console read pauses the world.

T5 is the case the claim does not cover: `ContainerGump::DropItem` makes the
split a new item in the same container when it lands on the gump's own floor
(`container_gump.cpp:512-513`), and the top-up raises every stack of a frame
it finds in the bag. Finding 4.

## C1: Map 39 south grass edge, FAIL (closure)

**What holds.** From y 20040 on the lane, a 3 s push due south and 1.5 s
pushes south-west and south-east at each x:

| Start x | After the south push | Lowest z seen | Plate |
|---|---|---|---|
| 15500 | (15480, 20164) | 48 | `C1-10-x15500-west-end-push-south.png` |
| 16300 | (16244, 20176) | 48 | |
| 17150 | (17040, 20180) | 48 | `C1-11-x17150-egg-area-push-south.png` |
| 17700 | (17712, 20156) | 48 | |
| 18000 | (17912, 20116) | 48 | |
| 18431 | (18412, 20184) | 48 | `C1-12-x18431-east-end-push-south.png` |
| 19500 | (19360, 20176) | 48 | |
| 20300 | (20144, 20164) | 48 | |

East face: a push east from (20036, 20080) stopped at (20164, 20112, 48)
(`C1-13`). Avenue stub: a push south from (20604, 19528) stopped at
(20584, 19676, 48) (`C1-14`). Platform north end: a push north stopped at
(14244, 19428, 48), against the fence (`C1-05`). Jumps: with the cursor on a void
plate past the oaks, three both-button presses each showed a crouch frame and
left the Avatar at (16904, 20156, 48) (`C1-24-after-both-button-jumps.png`).
With the right button held that input takes the directional branch
(`u8_avatar_mover_process.cpp:460-500`), a jump into the oak face, and the
oaks refused it. The targeted jump (`jump()`, `:749-775`, the path that could
arc onto a land plate) fires only on a jump with no direction held, which is
the Space press, and three held Space presses produced nothing (harness
anomaly 4). **The targeted jump over the oaks is NOT DEMONSTRATED.** 0
`Cycle in paint dependency graph` lines in all three Map 39 sessions,
including frames beside the west-end oaks on the platform.

**What fails.** A player on the lane reaches the black band south of the oaks
on foot by two routes:

1. **The platform rim.** From (14600, 20060, 48) the Avatar walked west onto
   the platform, then due south: (14136, 20060, 48), then (14136, 20172, 8),
   then (14064, 20812, 0) (`C1-19-rim-step-west-off-platform.png`,
   `C1-20-rim-route-into-void.png`). The platform has no 94 tile at
   x 14079..14207 for y 19583..19839 or 20095..20351, so a walk south along
   it drops 40 onto the gate pool's rim (shape 126, z 0..8, x 13951..14079,
   running to y 20479). The rim ends at y 20479 directly against void plates
   (shape 564, `SI_LAND`, z 0), an 8-unit step down.
2. **The avenue's east edge.** From (20896, 19300, 48), a push east dropped
   the Avatar to (21176, 19300, 0) (`C1-16-avenue-east-edge-push-east.png`).
   From there, south through the east plates into the south band:
   (21176, 21516, 0), (20508, 22184, 0) (`C1-17`), then west to
   **(17152, 20692, 0), directly below the apparition** (`C1-18-south-band-
   below-egg-x17150.png`).

Both are the edges `TENEBRAE_OPEN_EDGES` leaves open on purpose. Each was
described as harmless ("retail, map-long"; "drops onto retail floor, not
void"), and each connects to the void band through the void plates this same
commit lays. `TODO.md` says the avenue edge still drops; it does, to z 0 on
black plates, and the Avatar walks on from there.

Offline, `exact_reach` on the shipped FIXED.DAT with the void plates in,
seeded on the rim at (14015, 20000, 8), reaches 117,640 positions with the
body wholly south of y 20479 (x 12807..21599, z 0). Finding 1 has why the
test cannot see it.

## C2: Map 17 NE tapestry, FAIL

`findShape 329` lists item 2348, frame 5, at (6016, 5121, 0). From (5950,
5450, 0) the corner shows the lamp and, right of it, one small dark mark directly
above the east wall's top (`C2-01-ne-tapestry-from-5950-5450.png`, zoom in
the scratchpad). The 09-26 plate `L2-lamp-east-wall-section.png` shows the
same mark in the same place. The footpad overlay (`C2-03-footpads-overlay.png`)
did not separate the tapestry's box from the wall lines.

Projection arithmetic (screen x follows x minus y; screen y follows (x+y)/8
minus z): the east wall pieces (shape 10, x 6111..6143, y 5119..5375, two
courses, z 0..80) have larger x+y than the tapestry in every one of its
screen columns, so they paint in front. At the tapestry's west end
(x 5920) the wall's top edge sits about 16 px below the tapestry's top; at
x 6016 the wall's top is above it. Only a sliver at the west end can ever
show. Occlusion in U8 is fixed by the world, so no camera position changes
this. The plate re-anchor in `build_map_17.py` may well have fixed a real
plate-wall ambiguity, and the tapestry still does not show. Sure of the
plates; the occluder is my reading of the geometry, about four chances in
five.

## D1: Map 18 breach rubble, PARTIAL

`findShape 526` lists the hall rock 7547 at (2975, 5887, 0) and chips at
(2975, 6231), (2543, 6239), (3135, 6399), all z 0, frames 6, 6, 7, 8. The
built map holds nine shape-6 gravel tiles (frames 1 to 25) and two shape-524
piles (frames 2, 3), all z 0 on the z-0 floor. The shipped `U8SHAPES.FLX`
gives shape 6 30 frames, 524 six, and 526 nine, so every placed frame exists;
the session logs hold no `Skipping invalid shape` line for 6, 524, or 526
(the one sorter line is `539,4`, the old save's invisShield, as on 10-01).
0 `Cycle in paint dependency graph` lines in sessions 4 and 5.

From the hall at (2852, 5628), the sanctum-side spill and piles show over the
wall under the crack as a ragged dark spread with grey heaps on both sides
of the stub (`D1-01-hall-approach-y5640.png`; also behind every bark in
`D2-01` to `D2-03`). Nothing floats; nothing is buried.

**The hall rock is not visible.** It is 224 units north of the wall's north
face. From (2852, 5628) and from (2828, 6108) its projected position is wall
face (`D1-02-hall-rock-position-plain.png`, `D1-03-hall-rock-footpads.png`).
The 10-01 report measured that a flat item is hidden closer than about 480
units behind this 120-unit wall; for a 16-unit rock the figure is about 416.
This is the hall plate's defect again, which the commit's "256 units north
of the wall so the camera can see it" meant to avoid. Finding 8.

**Not demonstrated:** the rubble from the sanctum side with the breach open.
A double-click on a Tiny Tar in the pack did not register (harness anomaly
6), and I stopped there.

## D2: crack hint, PASS

`run-s16-tinytar.sav`: Map 10, `templeOpen` 0, `crackHintGiven` (bit 0x725)
0, three frame-8 potions in the pack. The three were dropped on the ground
beside trigger 211 (`D2-00-potions-dropped-on-map10.png`); `findShape 859`
then listed none in the pack.

| Visit | Carrying | Hatch | Screen | `crackHintGiven` |
|---|---|---|---|---|
| 1 | no potions | `Item: 15854 (shape 73) calling usecode event 7 @ 05B1:0080` | "The stone here is split from top to bottom, and there is open air beyond it." then "Grit has sifted down from the crack and lies heaped on the flags below it." then "But the gap is no wider than my hand." (`D2-01`, `D2-02`, `D2-03`); no nudge | 0 to 1 |
| 2 | no potions | egg 11041, `event 7 @ 05B1:0080` | 46 frames over about 60 s, no bark text (`D2-04-return-no-potions-silent.png`) | 1 |
| 3 | three potions | egg 9008, `event 7 @ 05B1:0080` | "Hrodny's dark potions are in my pack. For the moment of miracles, she said they were. I wonder." for about 40 s; no observation bark (`D2-05-return-with-potions-nudge.png`) | 1 |
| 4 | three potions, class traced | egg 12420; the process started at offset 128 and resumed three times at offset 694 | nudge only | 1 |

Each visit left Map 18 on foot through the exit trigger and came back through
trigger 211, so each was a fresh map instance. Offset 694 (0x2B6) is the
`loopnext` after the nudge bark's `suspend` in the potion loop, so visit 4
ran the nudge three times and no observation bark. Visits 2 and 3 are the
negative controls: no repeat without potions, no repeat with them.

## A1: Map 41 Aramina, PASS

Fresh world, teleport to (16671, 19200, 48), three walks north to (16611,
17540): processes 1427 (type 0x217), 1431 (type 0x205, `040D:4511`), and an
`ActorBarkNotifyProcess` for item 13 (`A1-01-aramina-fast-area-in.png`).
Four walks south to (16691, 19580): the log gained `LV: I_resetRef item=13
type=0x0205`, then 0x0204, 0x00F0, 0x0200, and `Kernel::listProcesses`
listed no item-13 process (`A1-02`). 0 `Invalid item 1037`, 0
`Non-existent process`, 0 `stuck` across the whole session. Map 41 has no
other NPC's 0x205 process to leave alive, so this section has no negative
control of its own; claim 4 of `docs/playtest-2026-10-03-killprocess.md`
carries the cross-NPC control for the same `resetRef` path.

## L: log health, PASS (3 lines attributed)

| Session | Content | Lines | Non-existent | stuck | Segmentation | Assertion | Cycle in paint | Unhandled intrinsic |
|---|---|---|---|---|---|---|---|---|
| 1 | Map 39 (died in the gate pool) | 161 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | Map 39 | 301 | 0 | **3** | 0 | 0 | 0 | 0 |
| 3 | Map 39, Map 17, Map 41 | 207 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | endgame, bag, B1 | 2,397 | 0 | 0 | 0 | 0 | 0 | 3 |
| 5 | Map 10, Map 18 four visits | 15,457 | 0 | 0 | 0 | 0 | 0 | 0 |

The three `Seem to be stuck in process loop` lines (session 2, log lines
271-273) follow my teleport to (14600, 19980, 48), whose body box overlaps
retail wall piece 15 at (14623, 19967, 48) (box y 19935..19967, z 48..88).
The Avatar then stood at frame 490 and refused every direction; the session
was restarted. A player cannot be placed inside that wall. The three
unhandled intrinsics in session 4 are `Npc::getNpcSlot()` for item 116
(Ezrekal's conversation; killprocess finding 6).

## Findings outside the plan

1. **`test_map39_south_edge.py` cannot see either route in C1.** Its flood
   seeds at the egg, moves only by the engine's step deltas (0, ±4, ±8), and
   removes the void plates. The 40-unit drop onto the rim is never followed,
   so the rim is pinned as an "open" exposure and nothing beyond it is
   checked; the void plates that make the rim's south end and the avenue's
   east side walkable are left out. A flood seeded on the rim with the
   plates in reaches 117,640 positions south of y 20479. Sure.
2. **The platform has gaps in its top.** The 94 tiles at x 14079..14207
   cover y 19455..19583, 19839..20095, and 20351..20479 only; between them
   is the rim at z 0..8. A walk due south along the platform drops 40 with no
   westward step (session 3, (14136, 20060, 48) to (14136, 20172, 8)). Sure.
3. **The west end leads into deadly water.** In session 1 a 2 s north-west
   push from the fence at (14244, 19428, 48) slid along the fence, past its
   west end at x 14079, and the next read was hp 0 with the Pagan book open.
   The gate pool (shape 347, `SI_SEA`) lies directly west of the rim
   (x 13695..13951). This is retail water, and the lane now leads the player
   along it. The position at death was not read, so the drowning is inferred
   from the map, about four chances in five.
4. **The bag's metering can be multiplied without anything leaving the bag.**
   T5: one split dropped on the bag's own floor makes a second stack, and
   both climb 5 per poll to 25. Repeated splits give N stacks of 25, so the
   "5 per frame per poll" ceiling in `ENDGAME.UNK:221-227` scales with the
   number of splits, and the bag can then be merged back into one stack of
   50 or more, which the top-up never touches (q 25 or above is left alone).
   Sure of the observation (25 to 50 in about 38 s).
5. **The poll is faster than the comment says.** `ENDGAME.UNK:221` quotes
   "a 200-tick poll (measured 20-28 s)". Steps here landed 6 to 13 s of wall
   time apart, and that includes the world-paused console reads. The farming
   rate per minute is two to four times the comment's figure. Sure of the
   readings; the cause (200 engine frames against the quoted measurement) is
   inference.
6. **The other two TypeBags were in the Avatar's pack.** The comments in
   `ENDGAME.UNK` and `EZREKAL.UNK` say Ragnar's and Hrodny's bags are popped
   to world coordinates and stay there. In the 09-29 world bags 1754 (empty)
   and 14387 (one item) were in the backpack (`B1-04`). Both read `q: 0`, so
   the tag is still unique and the refill found the right bag. Sure.
7. **The six reagent stacks arrive drawn as one pile.** Opening the new bag
   shows a single reagent icon in its top-left corner (`B1-05-bag-open.png`);
   `findShape` lists all six at gump (0, 0) until the gump is opened. A player
   sees one stack where the bark promises six kinds.
8. **D's hall rock is hidden by the wall it was meant to clear** (D1 above).
   Sure of the plates and the projection.
9. **The potion nudge repeats once per potion.** With Hrodny's three potions
   the line held the screen for about 40 s, three barks in a row (visit 4's
   trace). The review's "repeats at most the one-line nudge" holds per potion.
   Sure.
10. **The oak row reads as a hedge.** Shape 199 has one frame, and 29 copies
    on a near-straight line read as one repeating band in `C1-11` and `C1-12`.
    The map dressing standard asks for a hand-authored look with no lattice.
    Judgement.
11. **`iso_render.py` and the engine disagree about this tapestry.**
    `dfa73f5` cites `iso_render.py` as rendering the tapestry in full after
    the plate re-anchor; the engine shows a sliver at most (C2). Until the
    renderer's occlusion is reconciled with the engine's, it cannot stand in
    for an in-engine plate of a wall-mounted flat. Sure of the disagreement;
    the renderer's cause was not examined.
12. **Tiny Tars dropped on Map 10 do not survive a map change.** The three I
    dropped beside trigger 211 were gone after one Map 18 round trip;
    `findShape 859` instead listed three frame-8 potions contained at gump
    (255, 255) with `EXT_FIXED` (ef 0x9). They are FIXED contents of
    Hrodny's chest (`build_map_10.py:800-830`), and the pack potions carry
    `EXT_FIXED` too. That fits the chest re-reading its contents on every
    Map 10 load. If so, a player who drops his potions loses them, and a
    player who keeps them may find the chest full again on each visit (not
    tested). Predates this change. About two chances in three on the
    mechanism.

## Harness anomalies

1. **The first Map 39 landing was inside an oak.** (14700, 20150) overlaps
   oak 14284's box (x 14521..14809, y 20124..20412); the engine ignores a
   solid the mover starts inside, so the Avatar walked straight through to
   (14700, 20670, 0) (`C1-01-harness-landing-inside-oak-void.png`). That push
   is excluded from the verdict.
2. **A landing inside a retail wall** (session 2, L above). The shell's
   noclobber then refused to overwrite a driver file and re-ran the old one,
   which teleported to the same spot a second time.
3. **The session 1 Avatar drowned** (finding 3); sessions were restarted
   fresh after it and after anomaly 2.
4. **Held Space did not jump.** Three 0.4 s presses with the cursor on a void
   plate gave no turn and no animation. The both-button press did reach the
   mover.
5. `GameMapGump::toggleFootpads` through the retrying console helper toggled
   four times; a single-send helper was used after.
6. **The Tiny Tar drink did not register.** A double-click on the pack's top
   potion logged nothing; the pack was later closed by a click on its flap.
7. `run-s16-tinytar.sav` loads with the camera parked away from the Avatar
   and, after the teleport, the minimap open (`m` closed it).
8. After a Map 10 reload the potion ids changed, so the first three
   `Item::grab` calls used stale ids and answered `grab: no item`.

## Disk changes

- `docs/playtest-2026-10-03-batch-merge.md` (this report) and 46 plates in
  `docs/playtest-2026-10-03-batch-merge/`.
- `shared/build/` rebuilt by `tools/build_artifacts.sh`: byte-identical to
  the recorded hashes, new mtimes.
- `shared/data/u8-install/` rewritten by `./install_lv.sh` (same bytes).
- `shared/u8-lv-patched/`: EUSECODE `a908cb53` to `2efc9e91` and both
  FIXED.DAT copies `f92973ee` to `7650fba3`, synced by `session.sh start`.
- `~/.local/share/scummvm/saves/ultima8.001` overwritten three times and
  restored with the other 47 files; `md5sum -c` passes on all 48, and no new
  save file remains. `~/.config/scummvm/scummvm.ini` restored (`a143fa3b`).
- Scratch only: `/tmp/claude-1000/v1003b/` (backup, five session logs,
  drivers, film frames, disassemblies of 0x5AA and 0x5B1, and the
  `bag-q1-map10-2026-10-03.sav` checkpoint).
- No tracked file modified; the author's uncommitted edits are untouched.
  `TODO.md` not touched (the brief says to edit nothing outside this record).
