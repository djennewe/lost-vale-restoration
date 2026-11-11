# Playtest 2026-10-10: gateway placements on the mover model, and Map 13's summit edges (verifier)

This verifies `03e3e8a` (gateway2) and `f971dda` (edge13), as integrated in `main` `4a40dc8`. The session was cut short on Main's instruction because a newer build that moves these placements again is waiting. Unfinished claims are marked NOT DEMONSTRATED.

- **Build under test.** `/tmp/claude-1000/vmaps3/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Every hash matches `shared/build/ARTIFACTS.sha256`: FIXED `22cada6f…` (top level and `STATIC/`), EUSECODE `709c6bd1…`, U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…` and ANIM `77e9705d…`. The engine log reads `eusecode.flx: … 1525518 bytes`.
- **Binary.** `scummvm-lv/scummvm` (mtime 11:00), with fork HEAD `8af4f74e`. `PATCH_EQUAL`.
- **Harness.**
  - Xvfb `:93` (1280x800), with the window at (480,300).
  - A private `scummvm.ini` sets `frameLimit=true` and `usehighres=false`, with mute on and `SDL_AUDIODRIVER=dummy`. From the third launch on it also sets **`music_driver=null`** (finding 2).
  - The save is `run-s4-columns-done.sav` (md5 `cc6ed3a1…`, unchanged at the end): the doors are open, and it loads on Map 11.
  - Launches 2 and 3 ran under gdb.
- **Input and method.** The same as `playtest-2026-10-10-gateways.md`:
  - Mouse run is the right button at 240 px (capped at 185 px vertically). Mouse walk is 110 px.
  - `key` is `Up` after a 0.25 s facing burst, and `skey` is `Shift+Up`.
  - Each hold is released N s after the log shows `Loading Fixed items in map <dest>`. "15" means continuous.
  - Every source trigger was entered on foot, from outside its box.
- **Debug teleports.** After the first hour, `MainActor::teleport` was used to position the Avatar *outside* the source trigger, always with cheats toggled back off. None of them was the egg under test.
- **Plates** are in `docs/playtest-2026-10-10-maps3/`. The full per-hold record (210 rows) is `/tmp/claude-1000/vmaps3/results.json`.

**Combat mode.** `run-s4` loads with the Avatar **in combat mode** (actor flag `0x800`; finding 5). The first G1/G4/G5 series therefore ran in combat stance: mouse and keyboard walks were `advance`, and a run toggled combat off. I turned combat off with `c` and re-ran every G1/G4/G5/G7 hold in normal mode (the `G1n`/`G4n`/`G5n` rows). The verdicts below rest on the normal-mode runs. The combat-mode runs agree with them.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| G1 | Map 10→213 arrives at the niche; N/NE/NW holds never load Map 9 or 10, doors open and closed; walking out S/SE works; the Avatar is visible | **PASS**. **Doors open: 24 of 24** normal-mode holds (N, NE, NW × mouse run 2/4/15 s, mouse walk 4 s, key 2/4/15 s, Shift+Up 4 s) loaded only Map 8. Each ended in the niche, at (20095..20159, 3135..3151), z 8 (z 16 twice). **Doors closed: 12 of 12** (N/NE/NW × mouse run 4, key 4, Shift+Up 4, mouse walk 15) did the same. The combat-mode series added 19 more, with the same result. Walking out by mouse walk S/SE and by key S works. A mouse *run* SE stalls on the bone piles at (20187,3227,16), the known running-step trap. The Avatar is visible on arrival (`G1-213-arrival-N-mrun2`) |
| G2 | Map 9→200 arrives at the niche; holding N stops there | **PASS**, 10 of 10: N × mouse run 2/4/15, key 2/4, Shift+Up 4, plus NE/NW × 4. All ended at (20095..20151, 3135..3151, 8) (`G2-200-arrival-niche`) |
| G3 | Pushes N at x 20450/20464 never load Map 10; with the doors open, walking N through them loads Map 9 | **PASS**. **Doors closed: 8 of 8** pushes (mouse run, key, Shift+Up and mouse walk, 6 s each, at both x) loaded nothing. Two keyboard pushes wall-followed away, to (20316,4715) and (20044,3518). **Doors open: 8 of 8** went through the doorway to Map 9 and **0 to Map 10**. The doors were closed and reopened by double-click in-session (`G1-doors-closed-view`) |
| G4 | Walking E to the east wall at y 3330-3450 onto the slab loads Map 10; on Map 10, E/NE holds do not bounce | **PARTIAL**. **Mouse walk, mouse run and Shift+Up** fired 212 every time: 22 in normal mode and 16 in combat mode, at y 3335-3600. **No arrival bounced**: E for 2/4/15 s and NE for 4 s ended at Map 10 (14552..22528, 1096..3612). **Keyboard walk E at the slab rows fails 2 of 4**: one stopped at (21094,3394) for 10 s, and one wall-followed **south out of the chamber to (20211,5747)**, taking an 8 HP fall. The key also cannot step onto the slab (finding 3). **The trigger strip is inside a black occluder: the Avatar is not drawn there and the slab is not visible** (finding 4) |
| G5 | Map 10→204 arrives at (8291,22639); W/NW held 4 s never loads Map 10; the north doorway is reachable | **PARTIAL**. **Holds: 20 of 20** (W/NW × mouse run, mouse walk, key, Shift+Up 4 s, key 15 s, in both modes) loaded only Map 11. They ended at (8259..8271, 22599..22639). **The doorway is reachable** on foot from the pad (8259 → 8651, along the north wall). **It is impassable after any map hop**, because the sealing boulders and all four pillars come back (finding 1, outside this change) |
| G6 | On Map 13, S holds never load Map 10; walking W off pad 207 onto the slab (3328,11520) loads Map 10 | **PASS**. 9 arrivals on Map 13 under S holds: mouse run 2/4/15 (×2), mouse walk 4, key 4, key 15, Shift+Up 4 and Shift+Up 15. **0 loaded Map 10.** The keyboard slide along the rim ended at (3296,12272), 240 south of the box, as designed. Shift+Up wall-followed to (1608,12288) and, on the 15 s hold, up the valley to (1612,4932). **Walking W off the pad fired 206, 3 of 3** (mouse walk, key, mouse run). Whether the slab is *visible* is NOT DEMONSTRATED (`G6-206-slab-view-from-pad207` shows no distinct slab; see finding 6) |
| G7 | The previously passing 212, 205 and 200 still pass | **PASS**. 205: 5 of 5 (S 2/4 s, E 4 s; ends (12800,3072..5760)). 212: see G4. 200: see G2 |
| E1 | Summit edges: N at x 3404 stops ~y 64; W/E stop at faces; S at x 3000 stops ~y 1024 | **PASS** for the valid runs. **N, 4 of 4** (mouse walk/run, key, Shift+Up): stopped at y 64..76, z 120, hp unchanged (the key wall-followed W along the face to (2624,64)). **W, 2 of 2:** x 2624. **E, 3 of 3:** x 4608 / 4608 / (4588,68). **S, 2 of 2:** (2836,1020) and (2984,1024). **NW, 3 of 3:** (2624..2628, 68..92). The NE/SW/SE corner pushes are **invalid**: the positioning walk crossed 209 and they ran on Map 17. Nothing fell; hp stayed 30 throughout |
| E2 | 209 → Map 17 works from the summit; 208 back; walk down into the harpie zone | **PASS (by accident, and partial)**. The positioning walk N at x ~4096 hatched 209 → Map 17 twice. 208 (walked S from (5376,11300) on Map 17) → summit pad worked 2 of 2. One arrival walked on S down the climb to (4096,2008,108), in the harpie zone. The path width was not measured |
| E3 | Upper-climb parapets, ledge below 2816 open, fall non-lethal, jump at a parapet | **NOT DEMONSTRATED**: cut short |
| E4 | 0 `Cycle in paint` at the summit faces and parapets with `debugflag_enable Object` | **NOT DEMONSTRATED**: the flag was never enabled. The log has 0 `Cycle in paint` lines, but that proves nothing without the flag |
| L | Log hygiene | **PASS** for this change: 0 `stuck in process loop`, `Unhandled intrinsic`, Segmentation, Assertion, `Trying to access segment`, `popToContainer`, `stale gravity` and `Non-existent process`. There were 225 stock `Invalid item N passed to area search` lines over 241 map loads, and 566 `Doing a MIDI transition` warnings (finding 2). **But there were two hard hangs** (finding 2) |
| — | `tools/run_all_tests.sh` | **PASS**: `OVERALL: PASS — 44/44` (220 s) |
| — | Patch equals fork diff | **PASS** (`PATCH_EQUAL`) |
| — | `build_artifacts.sh`, `install_lv.sh` | **Not run**, on instruction. The hash match stands in for them |

## Findings outside the brief

1. **Map 11's column puzzle undoes itself on every map entry (high severity; not this change).**
   - **What happens.** The sealing boulders (shape 66, q 299) and the four pillars (865) are FIXED.DAT records. `World::switchMap` reloads every fixed item on entry (`world.cpp:178-196`). So `COLPUZZL`'s `item.destroy()` lasts only until the player leaves Map 11.
   - **Evidence.** On `run-s4` (columns done) I walked through the doorway, took 205 to Map 10 and 204 back, and the doorway was plugged again. `findShape 66` lists items 3562/12719 at (8704/8576, 22528), and `findShape 865` lists all four pillars, at frames 0-3 (`G5-doorway-boulders-reloaded`). From the pad the Avatar cannot go north (12 bursts, every heading).
   - **Consequences.** Every return from the Vale by 204 lands the player in a sealed room whose only exit is 205. Map 11's other rooms (and 202 → Map 9) are cut off. Talismans are spent, so a player coming back from Map 9 meets a puzzle they cannot redo [INFERENCE: the talismans are consumed].
   - **Related.** The same mechanism as the accepted Tiny Tar refill (TODO, 2026-10-08), but here it breaks progress.
2. **Engine hang: the MIDI parser spins with the mixer lock held, and the game freezes (2 of 2, before music was disabled).**
   - **What was frozen.** Both times the game stopped on Map 8 around (20600..20723, 3275), after a `Doing a MIDI transition! trans: 9` warning. The frame was frozen and the input dead. The main thread ran at 107% CPU.
   - **gdb (launch 2).**
     - Thread 1 is blocked in `Audio::MixerImpl::isSoundHandleActive` ← `AudioProcess::playSFX(144)` ← `ActorAnimProcess::doSpecial` (a footstep).
     - The audio thread is in `MidiParser::determineNextEvent` (`midiparser.cpp:356`) ← `MidiPlayer::onTimer` ← `Audio::MixerImpl::mixCallback`, holding the mixer mutex.
     - The parser state: `_activeTrack 9` of `_numTracks 10`, every subtrack `_playPos = 0x0` and `_position` all zero. So no subtrack is tracking, `_nextEvent` stays on subtrack 0, and `onTimer`'s loop never advances.
   - **The trigger.** The transitions come from combat-music toggles: each mouse run in combat mode calls `toggleInCombat` + `playCombatMusic` (`u8_avatar_mover_process.cpp` handleCombatMode). The harness's console open/close adds more. This session logged 566 of them.
   - **Workaround.** With `music_driver=null` there were no further hangs over about 6 hours.
   - **Whose bug.** Upstream ScummVM code [INFERENCE], but a player who runs in and out of combat with AdLib music on can presumably hit it. Not caused by this change.
3. **Keyboard players can miss 212.**
   - **The slab.** It sits at z=1 with zero height (`301` box z[1,1), SOLID|LAND). Stepping onto it from z 0 is a +1 riser, which is not in `{0,±4,±8}`.
   - **Keyboard walk.** Facing E along the slab rows, it stops at the slab's edge, or slides ±45° and wall-follows. 2 of 4 attempts failed: stopped at (21094,3394), or carried away to (20211,5747).
   - **Mouse walk and runs** succeeded, apparently by sliding north of the slab into the strip's y 3200..3326 [INFERENCE from t_load ≈ 4 s for 300 units].
   - **The test.** `deliberate_use` passes, so it presumably walks a row or input the engine treats differently. Worth putting the keyboard case into the mover model.
4. **212's strip is invisible.**
   - **What the plates show.** East of x ≈ 20700, Map 8 is covered by a black occluder whose boxes stand above floor level (`G4-slab-approach-footpads`). Standing at (20900,3420,0), the camera centred, **the Avatar is not drawn** (`G4-slab-approach-view`). The slab at (21247,3455) and the "east wall" cannot be seen either.
   - **What it means.** The deliberate route to the Vale is a blind walk into black. The old 212 spot (20900,3300) was in the same zone [INFERENCE: the gateways report does not mention it].
5. **`run-s4-columns-done.sav` loads in combat mode** (flags `c00`). The 10-10 gateways report used the same save, so its keyboard and mouse-walk rows were probably combat `advance` moves [INFERENCE]. Toggle with `c` and check `flags` before any movement test.
6. **The 206 slab on Map 13 is at z=0.**
   - **What the plates show.** No distinct slab is visible at (3328,11520) from pad 207 (`G6-206-slab-view-from-pad207`, `-footpads`).
   - **Why [INFERENCE].** Map 8's slab was put at z=1 because a z=0 slab loses the depth sort to coplanar terrain. Not confirmed.
7. **The Avatar took unexplained damage on Map 8 four times, and died once.**
   - **The losses:** 30→10 during a 15 s NW hold in the niche; 30→13 around the door double-click; 19→0 at (20265,3290) during a walk between the niche and the chest (`F-death-map8`); and two 8 HP falls on keyboard wall-follows.
   - **No repro.** Idle for 20 s at (20370,3230): no loss. An instrumented walk niche → (20775,3295): no loss. Reopening the doors: no loss.
   - **Not a monster I could see.** No monster was visible, and actor ids 256-275 are empty. Cause not identified.
8. **Keyboard wall-follows from both 212 and 207 sources carry the Avatar thousands of units.** Two examples: Map 10 from the 207 gate to (6592,20564), and Map 8 to (20316,4715). Neither reached another trigger, but the "where does a held key end" bound is large.

## Harness anomalies

1. **`gdb run >>log` drops the program arguments.** It came up in the launcher. Give the full argument list on the `run` line.
2. **`goto` from the Map 10 court to the NE start crossed 213** several times, and from the summit it crossed 209. Four holds then ran on the wrong map. They are marked `invalid` in `results.json` and excluded above (the two `G1n-…-anomaly` plates, and the E1 NE/SW/SE rows).
3. **My first `hold()` with no release time never released** after a load (G3's first push). Fixed, and that push was re-run.
4. **The read tool intermittently failed** to open freshly written PNGs. A second read worked.
5. **The Map 10 207 gate gap has item 114** (SOLID, z 8-48) at (7168,23552). A start due north of it at x 7168 blocks before the trigger, so 10 G6 approach holds never reached 207. They are marked invalid; the holds were re-run from x 7262.

## Disk changes

- **Repo:** this report, plus `docs/playtest-2026-10-10-maps3/` (18 PNGs). `run_all_tests.sh` wrote only `__pycache__`.
- **Scratch** in `/tmp/claude-1000/vmaps3/`:
  - `game/`, `scummvm.ini` (with `music_driver=null`), `run.sh`, `rungdb.sh`, `gdbinit`, `xv.sh` and `go.sh`;
  - `saves/ultima8.001` (run-s4, md5 unchanged), `lv_run.log` and `results.json`;
  - `py/drv.py` and `sp/`.
- **Stopped:** my ScummVM (and its gdb), and Xvfb `:93`.
- **Not touched:** source, builders, maps, the fork, `shared/`, `TODO.md`, `HANDOFF.md` and `~/lv-checkpoints` (read only; nothing banked).
