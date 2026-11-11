# Full 1→18 run on the current build, cheats off — NOT COMPLETED (2026-10-08)

Claim under test: `TODO.md:59`, "A complete 1-18 run on the current build
(2026-10-07 compiler), cheats off." Build: main `6aba6a4`, EUSECODE
`1ca0e93b…`, FIXED `6dc98430…`, fork `ed924d30`. Plates are in
`docs/playtest-2026-10-08-full-run-1-18/` at 640x400.

**Outcome: the run did not get past the base-game prologue on Map 3.** The
session hit its request budget after two harness deaths and three fresh
starts. No Lost Vale quest step was reached in this chain, so every step
verdict is NOT DEMONSTRATED. The useful results are the standard checks, the
prologue route that a walked new game has to take, and a static finding
that the Mythran leg is walkable after all.

## Verdicts

| ID | Claim / check | Verdict |
|---|---|---|
| C0 | `tools/run_all_tests.sh` | **PASS**: `OVERALL: PASS — 42/42 test file(s)` |
| C1 | Full `tools/build_artifacts.sh`, hashes | **PASS**: rc 0, `RESULT: PASS — all 4 artifacts match`, TYPEFLAG `9f534e59`, U8SHAPES `a611e9be`, EUSECODE `1ca0e93b`, FIXED `6dc98430`. The Compilation Report has 48 files, 46 OK, and 2 failures, exactly `EALOGO.UNK` and `TJORVI.UNK` |
| C2 | `./install_lv.sh`; the session loads the canonical bytes | **PASS**: rc 0. The game copy `/tmp/claude-1000/fr/game` is an rsync of `shared/data/u8-install` without the `.bak` files, and all four artifacts hash to `ARTIFACTS.sha256`. The log reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `usecode/eusecode.flx: e1fed4c8…, 1524731 bytes` |
| C3 | Fork patch equals the fork diff; binary postdates `ed924d30` | **PASS**: `PATCH_EQUAL`. The binary is dated 10:16:18 and the commit 10:16:10 |
| S1–S18 | Quest steps 1–18 walked in one save chain | **NOT DEMONSTRATED**. The chain ends on Map 3 after the Tenebrae execution scene: `lbSpoke`, `lbStarted` and `lbDone` all read 0, with no LV step taken |
| H1 | Hrodny's chest refuses other keys and opens with the q20 key | **NOT DEMONSTRATED** (step 16 not reached) |
| L | Log hygiene, all three session logs | `Unhandled intrinsic` 0/0/0 (no chest used). `Non-existent process` 7/2/1. `stuck in process loop`, Segmentation and Assertion all 0 |

## What happened

A new game is required, and it starts on **Map 3** at Devon's camp
(14527, 5887, 8). The only exit is the trigger to Map 40 at
(11516, 1660, 48), behind Tenebrae's south gate.

1. **The camp fire costs 9–10 hp.** The Avatar starts beside Devon's
   campfire (CAMPFIRE, 010B). A walk west from the start drops hp 30 → 20
   every time; the replay was deterministic across three fresh worlds.
   This is retail behaviour and is not lethal.
2. **The gate stays shut until the execution.** GUARDEGG (04A1) at
   (11494, 2330) sends the guardsman (NPC 4, GUARD1) to the Avatar. His
   "Open the gate!" answer is "This gate ain't gonna be openin' til after
   the execution!" The EXCUTION egg (0483, NONFIXED, (11732, 5844, 48),
   range 0xBB) is on the dock just west of the stairs. Walked into from
   (11679, 5439), it plays Toran's execution and the Lurker, followed by a
   guardsman's questions. The answers I picked were "What just happened
   here?", then "I go by Avatar." / "The beach." / "To get home." (the menus
   differ between worlds). After that the gate is open. In world 2 I walked
   Map 3 → Map 40 (13038, 14946) → Map 39 (19034, 14070) on foot. The
   AVATAR detour fired on Map 40 (`Loading Fixed items in map 0`, then back
   to 40) and set `lbSpoke` to 1.
3. **Death 1, world 1, Map 3:** before I knew about the execution gate, the
   walker's stall probes pushed the Avatar from the closed gate east into
   the harbour, and he drowned (hp 21 → 0 over about 40 s). This is a
   harness fault (the deadly-water trap).
4. **Death 2, world 2, Map 39:** I walked a straight line from the city
   interior (18294, 16010) toward the south gate. At (17834, 17750) he
   dropped from z 48 to z 8 into water and died on the next read. This is
   the "gate pool" the 10-03 report also died in. It is a harness fault,
   with a map hazard behind it (finding 3).
5. World 3 replayed the prologue and banked it after the execution. I
   stopped there on the session budget.

## Findings outside the brief

1. **Mythran's island is reachable on foot. `TODO.md:49` ("reached by a
   scripted arrival, not on foot") and the 09-01 report's conclusion are
   wrong.**
   - **The class.** Retail egg class `04C6 MYTHAUS` is not in FIXED.DAT. It
     is in NONFIXED (`SAVEGAME/U8SAVE.000`), so the 09-01 scan, which
     looked only for `Actor::I_teleport` (158) in FIXED, missed it.
     MYTHAUS calls `teleportToEgg` (intrinsic 0xCC).
   - **The plateau egg.** Egg id 1 at Map 8 (13988, 15084, 48), range 0x23,
     is on the plateau. When it hatches, MYTHAUS teleports the Avatar to Map
     8 egg **20**, (6078, 1786, 0), inside the house, or to egg 4 if global
     0x120 is set.
   - **The house egg.** Egg id 2 at (3071, 1791, 0) sends an Avatar at
     z ≥ 48 back to egg **22**, (14138, 15118, 48) on the plateau.
   - **Why the targets looked orphaned.** These are exactly the "orphan"
     targets 20 and 22 that the earlier analysis said nothing triggers.
   - **The walking route.** Map 3 → 40 → 7 → 8 (cave, trench, gate corridor
     to (14590, 11210, 48)), then across the plateau to (13988, 15084, 48).
   - **Status.** Not walked here; this is static evidence. Disassembly is in
     `/tmp/claude-1000/fr/retail_all.dis`.
2. **The doors region shows a void-level route from the plateau's north
   shuttle landing.**
   - **The route.** `pathfind.py --map 8 --from 14540,7972,0 --to
     20430,3250,0 --engine-void` finds 25 waypoints, z 0 all the way except
     for a short z-8 stretch.
   - **Status.** [INFERENCE] that the engine walks it. It is untested, and
     the 09-01 report shows the void model can be wrong in both directions.
   - **What it would close.** This is the step 2 → 3 link that no one has
     walked.
3. **Map 39's south-gate lane has no safe walking route from inside the
   city.**
   - **What the model says.** With every teleport trigger box masked,
     `exact_reach` finds no route from any Map 39 arrival pad (targets 0, 1
     and 2) to the LB egg at (17150, 19700, 48). Unmasked, the only route
     runs through the east-gate trigger zone.
   - **What the engine does.** It walked further than the model allows: out
     of the east-gate pocket into the city, to (18562, 14406). A straight
     walk south then fell into water at (17834, 17750).
   - **Effect.** Quest step 1's primary egg has no recorded walking approach.
     Every earlier verification of it reached the lane by debug teleport (the
     10-04 report says so).
   - **What it needs.** Someone should walk that approach and write it down
     before the next full run.
4. **A new game must play the retail prologue before any LV content.** That
   means Devon, the execution egg and the gate guard. None of it is in the
   playtest skill or the earlier run reports, which all started from
   checkpoints.
5. **`Non-existent process` appears in a fresh world before any LV map
   loads.**
   - **Counts.** It appears 1 to 7 times per world, on Map 3 / Map 40.
   - **Earlier record.** The 10-04 report already recorded one per fresh
     world (`PID (0) in implies`, after Devon's farewell).
   - **This session.** The count grows with the prologue (7 in world 1).
     It was not investigated.

## Cheats used

None. No teleport, item creation, flag write, `Item::grab` or
`Cheat::toggle` was used. The console was used only for `objectInfo`,
`getGlobal`, `debugflag_enable Object` and `Ultima8Engine::saveGame`
(slot 1).

## Wall time

| Leg | Time |
|---|---|
| Checks (tests, build, install) | 213 s |
| World 1, start to death at the harbour | about 12 min |
| World 2, start to death in the Map 39 pool | about 35 min, including prologue discovery |
| World 3, start to the banked post-execution state | about 10 min |
| Steps 1–18 | not timed, not reached |

## Checkpoints

- `~/lv-checkpoints/run1008-s00-prologue-after-execution.sav`. Map 3,
  (11747, 5811, 48), hp 26, after the execution scene and its questions.
  The gate is open, and `lbSpoke`, `lbStarted` and `lbDone` are 0. Saved
  with `Ultima8Engine::saveGame` and copied after the slot's mtime moved.
  It has **not** been reloaded and re-read.
- No per-step `run1008-sNN` checkpoints exist, because no step was reached.

## Harness anomalies

- The bark and option colours vary by speaker (white, green, orange and
  red), so a "text present" pixel detector misfires. I clicked barks
  through until a red option menu appeared.
- The walker's stall probe is lethal near water: it pushes in eight
  directions blind. Use `pathfind.py`'s water margin, and do not let the
  probe run near water.
- `exact_reach` / `pathfind` disagree with the engine on Map 39's gate
  pockets. The engine got out of a pocket the model calls closed.

## Disk changes

- **Wrote** this report and plates `s01-00-new-game-devon.png` and
  `s00-prologue-after-execution.png` in
  `docs/playtest-2026-10-08-full-run-1-18/`.
- **Wrote** `~/lv-checkpoints/run1008-s00-prologue-after-execution.sav`
  (new file, nothing overwritten).
- **Regenerated by the checks:** `shared/build/*` (all four hashes
  unchanged) and `shared/data/u8-install/` via `install_lv.sh`.
- **Scratch** in `/tmp/claude-1000/fr/`:
  - the game copy, `saves/`, `bank/`, the three `lv_run*.log` files and
    `tests.log` / `build.log` / `install.log`;
  - `retail_all.dis` (the retail EUSECODE disassembly), the driver
    `py/drv.py`, and frames in `sp/`.
- **Not touched:** source, builders, maps, the fork, `TODO.md`,
  `HANDOFF.md`, `~/.config/scummvm`. ScummVM and Xvfb `:81` are stopped.
