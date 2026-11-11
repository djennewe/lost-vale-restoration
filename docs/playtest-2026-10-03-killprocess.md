# killProcess, NPC references, and `within N cells`, verified statically and in engine (2026-10-03)

Change under test: the staged merge of `worktree-agent-a53dc9188e43323be`
(`b943ed2`) on `main` at `81deebd`, `--no-commit`, plus the unstaged
`build_scummvm.sh` and `ARTIFACTS.sha256`. Three compiler fixes:
`lv-patched/FREE.UNK` `killProcess` calls `resetRef` (it compiled to `push
0; ret`); an NPC class name in expression position pushes the npc number as a
byte (it pushed the class id); `within N cells` emits `push N; push 32; mul`
(it pushed N).

Artifacts: EUSECODE `a908cb53` (1,505,828 bytes, md5-5000 `4f47de88`), FIXED
`f92973ee`. Binary `scummvm-lv/scummvm` built 2026-10-03 11:04 CDT, after the
fork tip `e0d6084d` (2026-09-19), and carries `4f47de88...`. All three
session logs read `usecode/eusecode.flx: 4f47de88..., 1505828 bytes`. Plates
are in `docs/playtest-2026-10-03-killprocess/`, 640x400, named by test ID.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| C0 | Test estate | `tools/run_all_tests.sh` 36/36; round-trip 516/516; the new test 19/19, and 10 passed, 9 failed against HEAD's compiler | **PASS** |
| C1 | Full build and hashes | `tools/build_artifacts.sh` exit 0, all four OK, byte-identical to the bytes on disk; HEAD `81deebd` rebuilt to scratch gives `c9180526` | **PASS** |
| C2 | Compilation Report | 48 files, 46 succeed; failures `EALOGO.UNK`, `TJORVI.UNK`; warnings 509 to 508, and the one removed is `FREE.UNK: unknown identifier 'Kernel'` | **PASS** |
| C3 | ScummVM fork and cascade | tip `e0d6084d`; `diff -q` against the tracked patch silent; no `a6c0b72b`, `c91805264aed`, or `1505739` outside `docs/` | **PASS** |
| C4 | Maps, shapes | no builder, map, or shape-ID change in the diff | **not triggered** (finding 1 is a shape-ID defect it exposes) |
| S | Static claims | killProcess, two NPC-ref sites, two cells sites match retail byte for byte; 24 classes classified; no killProcess site kills its own process | **PASS** (one misclassification, finding 7) |
| 1 | Aramina, Map 41 | flood gone (0 lines); leave logs `resetRef item=13 type=0x0205` and kills atHome; each return starts one atHome; she does not walk her route | **PARTIAL** (route sub-claim **FAIL**, finding 1) |
| 2 | Shades scene and the three elders | scene completes, flags as on 10-02; Atli, Thordis, Ezrekal each loiter on approach, die on leave, restart once on return; all three dialogues open and offer the next step | **PASS** |
| 3 | Passage Test | without the stone nothing plays; with it the scene plays, all four flags 1, stone consumed; Thordis afterwards is in combat with the Avatar at 8 of 20 hp, and her dialogue opens | **PARTIAL** (leave and return at the test grounds not demonstrated; finding 2) |
| 4 | Ragnar, Tyorvi, Ezrekal, Thordis, Ingjald, Hrodny | every leave kills that NPC's loiter only; every return starts exactly one; all six dialogues open | **PASS** |
| 5 | Regression spot checks | LB frame 9 at 164 s with `lbDone` 1; potion ACT_IMMORTAL set at 17 s, cleared by 67 s, 31 laps 64 ticks apart | **PASS** |
| 6 | Log and CPU | 0 `Non-existent process`, 0 `stuck in process loop`, 0 `Segmentation`, 0 `Assertion` in three sessions; Map 41 CPU 100.2, 100.4, 98.4% against the 10-02 control 98.4, 98.2, 99.6% | **PASS** |

## Method and harness writes

Saves and `scummvm.ini` were copied first (`/tmp/claude-1000/v1003/bak/`, 48
save files with an md5 list). `./install_lv.sh` exited 0; `session.sh start`
synced EUSECODE into `shared/u8-lv-patched/` (it held `c9180526`). Three
sessions, one ScummVM pid each.

Writes, all disclosed:

- **Teleports with cheats on**, each followed by `Cheat::toggle` back to
  `Cheats = false` before any movement or click: Map 41 (16671, 19200, 48);
  Map 10 (20304, 17600, 4), (6144, 9400, 0), (19200, 9300, 0), (12800,
  14700, 0), (19200, 8300, 0), (5118, 10700, 0), (12800, 29720, 64) twice;
  Map 39 (17070, 20050, 48) twice, by the 10-02 `lb.py`.
- **Checkpoint loads** through slot 1: `~/lv-checkpoints/run-s13-shield-halves.sav`
  (claims 2 and 4), `~/lv-checkpoints/run-s7-ragnar-stone.sav` twice (claim 3),
  `/tmp/claude-1000/v1002/sp/slot1-patched.sav` (potion).
- `MainActor::toggleCombat` once (the shield-halves save loads in combat);
  `Item::grab 15048` (the Passage stone, positive run only);
  `CameraProcess::moveToAvatar` three times; `debugflag_enable Object` and
  `UCMachine::traceClass 1037`/`1253` (logging); `Kernel::listProcesses`,
  `objectInfo`, `findShape`, `getGlobal` (reads).

Plates were routed by changing the copied driver's `PLATES` default to this
report's folder; `LV_PLATES` itself was not exported.

Every fast-area entry and both egg scenes were entered on foot. Every
deliberate menu answer was clicked from the screen; the exceptions are in
Harness anomalies.

## S: static claims, PASS

**killProcess.** New LVFREE `0x0CDE` against retail FREE `0x0581:2A56`:

```
new     0CDE: 5A 00  init 00h       retail  2A56: 5A 00  init 00h
        0CE0: 3F 08  push [BP+08h]          2A58: 3F 08  push [BP+08h]
        0CE2: 3F 06  push [BP+06h]          2A5A: 3F 06  push [BP+06h]
        0CE4: 0F 04 CB 00  calli resetRef   2A5C: 0F 04 CB 00  calli resetRef
        0CE8: 6E FC  add sp -4              2A60: 6E FC  add sp -4
        0CEA: 50     ret                    2A62: 50     ret
```

The old routine was `0CDB: 5A 00 0A 00 50` (`init; push byte 0; ret`). Calls
to it: 43 before, 43 after, in the same 14 classes (AVATAR 4, ARAMINA 2,
SIGRID 1, RAGNAR 3, THORDIS 4, ATLI 4, INGJALD 3, HRODNY 3, TYORVI 3, EZREKAL
3, EGGPLANT 2, TYPEPOIS 4, EGGSHADE 6, LVFREE 1).

**Two NPC-ref and cells sites**, ARAMINA atHome, new against retail 0x40D:

```
new     0401: 0A 0A 0A 20 1E 0A 0D   push 10; push 32; mul; push byte 13
retail  0475: 0A 0A 0A 20 1E 0A 0D
new     043D: 0A 32 0A 20 1E 0A 0D   push 50; push 32; mul; push byte 13
retail  04B6: 0A 32 0A 20 1E 0A 0D
```

The old build had `0A 0A 0B 0D 04` there (`push 10; push 040Dh`). The other
NPC-ref sites push 106, 107, 116 (Thordis, Atli, Ezrekal in EGGPLANT,
TYPEPOIS, EGGSHADE) and 27 (`Malchir:Referent` into `Item::pop`, LVFREE).
CYRRUS, XAVIER, DARION, MORDEA, SALKIND, STELLOS, TORWIN are byte-identical
to retail in the FLX (they are never recompiled), so their agreement is
retail evidence only; the test's eight retail checks confirm it.

**Class diff**, `c9180526` (reproduced from `81deebd`) against `a908cb53`: 24
of 1,458 classes. A normalized instruction diff, call and spawn offsets and
jump displacements masked:

| Class | Real change |
|---|---|
| LVFREE 0x5AE | killProcess body; 1 cells site (`findNearest`, `within range cells of Avatar`); 4 `push 041Bh` to `push byte 27` |
| ARAMINA 0x40D | 8 searches: `push 040Dh` to `push 32; mul; push byte 13` |
| EGGMAGNE 0x598 | 21 cells sites (unplaced egg) |
| EGGPLANT 0x59A | 1 cells site; 2 NPC refs |
| TYPEPOIS 0x59C | 4 NPC refs |
| EGGSHADE 0x5A5 | 3 NPC refs |
| AVATAR 0x401 | 1 cells site |
| TYPEPEDE 0x4E9 | 1 cells site (`EAPUZL.UNK:89`, 140 cells) |
| EGGCANDL 0x597 | 1 cells site (unplaced egg) |
| the other 15 | offsets only, TYPEPOTI and TYPEBEDR included |

**Self-kill.** `Kernel::killProcesses` skips no process (`kernel.cpp:309-321`),
so a site that names its own (item, type) would end itself. At every one of
the 43 sites the caller's last `set info` differs from the target: the
NPC sites run as 0x217, 0x218, or 0x219 and kill 0x205 or 0x200; ARAMINA
`07F2` runs as 0x205 and kills 0xF0; EGGPLANT, TYPEPOIS, EGGSHADE run as
0x20F or 0x209 on the egg and kill NPCs 106, 107, 116, or the egg's 0x200
and 0x0001; AVATAR `008D` and LVFREE `19B0` set item 0, which
`killProcesses` never matches.

## 1: Aramina, PARTIAL

**Flood gone: holds.** 0 `Invalid item 1037` lines in session 1 (3,423
lines), against 41,570 on 10-02.

**Leaving kills atHome: holds.** Three walk-outs; each logged `LV: I_resetRef
item=13 type=0x0205`, then 0x0204, 0x00F0, 0x0200, and the ARAMINA process
list was empty afterwards (`B4-aramina-out-of-fast-area.png`). The waiting
enterFastArea (10-02 finding 4) woke when atHome failed and ended with it.

**Returning starts one: holds.** Two re-entries each gave exactly one
`UCProcess, item 13, type 205` and one type-0x217 enterFastArea
(`B5-reentry-one-atHome.png`, `B7-cycle3-in.png`). Map 41 had no other 0x205
process to serve as a negative control; claim 4 carries it.

**atHome finds its path eggs and walks her route: false.** On the first entry
she stood at (16671, 16671) for 50 s while atHome cycled through
`randomBarkAtHome` waits (20 s trace: offsets 06F5, 0704, 4511, 15 slices).
After a re-entry she held five `PathfinderProcess, item 13, type 204` at once,
walked west, and stopped at (15247, 16867) beside egg 13230 (shape 73,
quality 56) (`B6-aramina-walked-west-off-screen.png`). Her route markers are
the 46 shape-174 items on Map 41. Finding 1 has the cause.

**CPU.** 100.2, 100.4, 98.4% with atHome live; the 10-02 control at this map
read 98.4, 98.2, 99.6%. Map 10 read 89.6, 88.7%. The render loop keeps Map 41
near 100% with or without atHome, so this reading can show a hang and little
finer.

## 2: Shades scene and the three elders, PASS

`run-s13-shield-halves.sav` (Map 17, combat mode, `avatarPoisoned` 1,
`shieldFixed` 0). Combat off, teleport to (20304, 17600, 4), then a walk onto
the dais into egg 9679's box at (20480, 17152). The 10-02 recipe's 1.5 s walk
north missed the box; `goto` to the egg centre entered it.

Scene start logged `resetRef` 0x205 for 107, 106, and 116: the three
killProcess calls now land. Menus, each clicked from the screen: **Let's be
reasonable!** (`K1-first-menu.png`), **Yes, Priestess.** (`K2-second-menu.png`),
**Please, High Priestess.** (`K3-heal-menu.png`). Scene end logged
`item=9679` 0x0200 and 0x0001, then the elders' four-type sets. After:
`avatarPoisoned` 0, `shieldFixed` 1, `inShadeScene` 0, one shape-539 at frame
2 in the pack, no EGGSHADE process (`K4-scene-ended.png`). Same as 10-02.

The scene sends the elders home, out of the Avatar's fast area, with no
process. Each was approached on foot:

| NPC | On approach | Leave | Return | Dialogue |
|---|---|---|---|---|
| Thordis 106 | loiter 13601, moving (6148, 6770) to (6334, 6356) | 13601 killed; `item=106` 0x205, 0x204, 0xF0, 0x200 | one loiter, 15399 | menu opens (`E4-thordis-dialogue-opens.png`); **bye**, then loiter 16, moving |
| Atli 107 | loiter 5787, moving | 5787 killed; `item=107` 0x205; Hrodny's 10887 survives | one loiter, 7454 | **I am no longer poisoned!**, then **I found the Shield.**, then **bye** (`F3b`..`F8`); loiter 11036, moving |
| Ezrekal 116 | loiter 592, moving | 592 killed; `item=116` four types | one loiter, 2891 | **I would speak to you of Tyorvi.** leads to **He needs help.** (`G3b`, `G5`); **bye**; loiter 4124, moving |

## 3: Passage Test, PARTIAL

`run-s7-ragnar-stone.sav` (`thordisToldTest` 0, so Thordis is the elder the
scene fetches).

**Negative control, no stone in the pack:** stone 15048 left in its bag,
weight 30. Teleport to (12800, 29720, 64), walk to (12800, 29416, 72) inside
the egg box: nothing played; `plantScene`, `firstPoisoned`, `haveMark`,
`avatarPoisoned` all 0; 15048 still present; weight 30
(`M1-no-stone-at-egg.png`).

**Positive:** reloaded, `Item::grab 15048` (weight 40), same teleport, walk
north: `Item: 7570 (shape 73) calling usecode event 7 @ 059A:0080`;
`resetRef item=106 type=0x0205` (the killProcess; Thordis was at home,
outside the Avatar's fast area); the whirlwind and plant scene played
(`M3-passage-test-scene.png`); afterwards all four flags 1, weight 30, 15048
gone (`M4-after-scene.png`).

**Thordis afterwards:** `CombatProcess, item 106, type f2, target: 1` and a
`LoiterProcess ... notify: 7632`, hp 8 of 20, flags 0x800, wandering and
pathfinding after the Avatar without striking him (Avatar hp 30 throughout)
(`M5-thordis-combat-after-scene.png`). A double-click ran her `use()`
(`event 1 @ 046A:0CA7`): "Oh my, terrible this is. Sent you here Atli did?"
(`M8b-thordis-after-test-dialogue.png`). The combat process outlived the
conversation (`M10-thordis-speech-done.png`). Finding 2.

**Not demonstrated:** leave and return at the test grounds. It is an isolated
plateau; the walk away dropped the Avatar off it to z 0 at (12487, 27642)
while Thordis stayed in her fast area. Atli was not involved in this run
(`thordisToldTest` 0).

## 4: six NPCs, leave and return, PASS

`run-s13-shield-halves.sav` world after the Shades scene. "Census" lists
every type-0x205 process in the world before and after each leave.

| NPC | Cycles | Leave kills | Other NPC's 0x205 alive through the leave | Return | Dialogue |
|---|---|---|---|---|---|
| Ragnar 105 | 1 | 14382; `item=105` 0x205 | none in range | one, 7271 | via sprite colour; **I met someone named Thordis.**, **Farewell** (`L5`..`L8`); loiter 994, moving |
| Thordis 106 | 1 | see claim 2 | none in range | one | see claim 2 |
| Atli 107 | 1 | see claim 2 | Hrodny 10887 | one | see claim 2 |
| Ingjald 112 | 1 | 10458; `item=112` four types, twice | Hrodny 1189 | one, 3060 | **What is your name?** ("Ingyald, my name is."), **bye** (`J6b`..`J8`); loiter 13675, moving |
| Hrodny 113 | 1 | 5239; `item=113` four types | none in range | one, 11784 | **What is your name?** ("Hrodny, daughter of Ulmar, I am."), **bye** (`J3b`..`J5`); loiter 12173, moving |
| Tyorvi 115 | 2 | 11331, 13751; `item=115` four types | Hrodny 14971 (cycle 2) | one each, 13751, 7112 | **The Shield of the Ancients is repaired!**, **bye** (`H2b`..`H5`); loiter 6524, moving |
| Ezrekal 116 | 1 | see claim 2 | none in range | one | see claim 2 |

Every `resetRef` a leave produced named that NPC's own item number. The
negative control is Hrodny's loiter surviving three other NPCs' leaves.

## 5: regression spot checks, PASS

**Lord British** (fresh world, 10-02 `lb.py`): run 1 read frames to 137 s,
then missed 150 to 279 s, and ended with `lbDone` 1 and `findShape 411: 0
found`. Run 2 (fresh world, 0.5 s polling after 115 s): frames 0, 3, 5, 1, 2,
8, 5, 2, 4, 6, 8, 2, 1, 3, 5, 2, then **9 at 164 s** with `lbDone` 1
(`A2b-frame9-read-164s.png`); the Avatar walked (17194, 19718) to (17194,
19950) (`A3b-avatar-walks-after-scene.png`).

**Protection potion:** Int 15; double-click on 14823 (frame 5) in the pack:
flags `400`, `40400` at 17 s (`D2-immortal-flag-set.png`), `400` at 67 s
(`D3-immortal-cleared.png`); class 1253 traced 31 laps at offset 1250, 64
ticks apart; 14823 at frame 0.

## 6: log and CPU, PASS

| Session | Lines | Invalid item 1037 | Non-existent | stuck | Segmentation | Assertion | Unhandled intrinsic | Cycle in paint |
|---|---|---|---|---|---|---|---|---|
| 1 (Map 41, Shades, NPCs, Passage Test) | 3,423 | 0 | 0 | 0 | 0 | 0 | 25 | 7 |
| 2 (LB run 1) | 126 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 (LB run 2, potion) | 261 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

The 25 are 24 `Npc::getNpcSlot()` (finding 6) and one `process
Item::combine()` in the Passage Test (finding 2). CPU is under claim 1.

## Findings outside the plan

1. **Aramina's atHome still cannot walk her route; three compiler defects
   past this change.** The search centre and range now match retail; the
   rest of the search does not.
   - Type filter: the new loopscript is `41 49 00` (`A`, one shape, 0x0049 =
     73), from `TYPE_SHAPES['TypePathMarker'] = 73` (`u8c_symbols.py:408`).
     Retail is `% 00AE @ =`, shape 174. Live Map 41 holds 40 shape-73 eggs
     and the 46 shape-174 markers. ARAMINA's other four filters are off too:
     plate 377 against retail 284, tankard 340 against 178, friction grenade
     435 against 592, door 69 against 68. AVATAR's 20-cell search also uses
     shape 73 for `TypePathMarker`.
   - Frame filter: `(frame = counter)` compiles to `61 00 00`, frame 0
     (build warning `ARAMINA.UNK:236`); retail tests the counter.
   - `if pathfind(...)`: ours tests the pushed pid (`0451 calli pathfind;
     push retval; jne`); retail waits (`04CB calli; push retval; implies 01
     01; pop temp; suspend; push process result`). So she launches a
     pathfinder per matching egg per lap, which is the five concurrent
     `PathfinderProcess` seen.
   Before this change the bad centre made every search match nothing; this
   change is what makes these defects reachable in play. Sure of the bytes
   and the observation.
2. **Thordis ends the Passage Test in combat with the Avatar at 8 of 20 hp.**
   The scene pops five shape-400 items (`TypeMiniAirTitan`, legacy table) and
   steps them through frames 25 to 34, which shape 400 does not have (`Skipping
   invalid shape in sorter: 400,30..34`); base class 0x190's event 2 runs on
   every frame change, followed by `Trying to access segment 0000` and
   `Unhandled intrinsic 101 'process Item::combine()'`. Her killProcess is
   unlikely to be the cause: at the hatch she stood at home, about 23,000
   units from the Avatar and outside his fast area, where she gets no
   loiter. That is inference; no process list was dumped between the
   positive run's load (log line 2402) and the hatch (line 2448), and the old
   build was not run in engine, so this is not shown to predate the change.
   Dialogue still opens.
3. **A 44th killProcess site still compiles as nothing.**
   `lv-patched/MAGNET.UNK:564` `killProcess(referent, PT_UNKHATCH)` warns
   `unknown function 'killProcess'` ("call compiled as no-op") in both builds:
   the file has no `uses "free"`. EggMagnet is unplaced
   (`build_map_17.py:299-310`), so nothing reaches it today.
4. **The NPC-ref rule covers 60 egg and scene classes it should not.**
   `u8c_codegen.py` maps every class id 0x0400 to 0x04FF to `push byte (id -
   0x400)`. 0x480 onward are classes such as MAPTELE, DOOREGG, GHOSTEGG, and
   `push byte` sign-extends: a probe compiling `DOOREGG:Referent` emitted `0A
   AA`, which the VM reads as 0xFFAA. No source in the build hits it (every
   replaced push in the 24-class diff is 040D, 041B, 046A, 046B, or 0474).
   Latent.
5. **`within N cells` is 32 times wider everywhere, and one comment still
   assumes units.** PLNTST's plant-clearing search covers 3,200 units (Map 10
   `FIXED.DAT` holds one shape-126 frame-0 item, 32 units from the egg, and
   Map 10 is builder-generated, so nothing extra should be destroyed; the
   live map was not searched); `build_map_10.py:105-109` still says "within 100 world units of
   the EGG". EAPUZL's TypePedestals search is 4,480 units; MAGNET's 21 and
   CANTRK's one are 1,600 (both unplaced).
6. **Every conversation still kills every loiter in the world** (10-02 finding
   2). Atli's conversation killed Hrodny's loiter 5362 and Tyorvi's 5551;
   24 `Npc::getNpcSlot()` warnings. A walk out and back restores them.
7. **The author's class list misplaces TYPEBEDR.** It is offsets only (its
   one killProcess call moved); TYPEPOTI is offsets only too. The real changes
   are the nine classes in the S table.
8. **A comment cites a test file that does not exist.** The NPC-ref block in
   `u8c_codegen.py` names `test_npc_ref_cells.py`; the file is
   `test_killprocess_npc_ref_cells.py`.
9. **The new test's retail checks cover origin and range only.** "every area
   search is `N*32` around its own npc" passes for ARAMINA while finding 1's
   type and frame filters differ from retail.

## Harness anomalies

- Six clicks meant to advance Thordis's first speech (session 1) landed on
  menus and picked **What is this place?**, **How are you called?**, and two
  follow-ups (`sp/E6_grid.png`). Those picks were incidental; the deliberate
  **What is it you do?** and **bye** were read off the screen first.
- `proj()` assumes the camera is centred on the Avatar. After the Passage
  Test it was not, and two Thordis clicks missed until
  `CameraProcess::moveToAvatar`. Ragnar moved between reads; he was clicked by
  locating his blue sprite in a screenshot.
- The first Ingjald cycle's walk west stalled and he never left; a walk south
  worked. Two driver runs hit the shell timeout mid-cycle (Aramina cycle 2,
  Thordis at the test grounds); their partial output is reported, nothing
  more.
- The minimap opened during the potion setup; `m` closed it and `i` opened
  the pack.
- LB run 1's console missed eight consecutive reads (150 to 279 s).

## Disk changes

- `docs/playtest-2026-10-03-killprocess.md` (this report) and 92 plates in
  `docs/playtest-2026-10-03-killprocess/`.
- `shared/build/` rebuilt by `tools/build_artifacts.sh`: byte-identical
  (`a908cb53`, `f92973ee`, new mtimes).
- `shared/data/u8-install/` rewritten by `./install_lv.sh` (EUSECODE
  `a908cb53`).
- `shared/u8-lv-patched/USECODE/EUSECODE.FLX` synced by `session.sh start`
  from `c9180526` to `a908cb53`.
- `~/.local/share/scummvm/saves/`: `ultima8.000`, `ultima8.001`, and
  `scummvm-history.txt` were overwritten and restored from the backup;
  `md5sum -c` passes on all 48 files. `~/.config/scummvm/scummvm.ini` was
  rewritten by ScummVM (keys reordered) and restored (md5 `a143fa3b...`).
- Scratch only: `/tmp/claude-1000/v1003/` (HEAD tree extract and its
  `EUSECODE-81deebd.FLX`, disassemblies, drivers, session logs, film frames).
- No tracked file modified; the staged merge and unstaged edits are as the
  author left them. `TODO.md` not touched. An untracked
  `docs/reviews/2026-10-03-fable-review-pending.md` appeared during the
  session; it is not mine.
