# Playtest 2026-10-31: talisman re-entry on Map 11 (phase E finding F4)

This session settles `docs/playtest-2026-10-30-phaseE-verify.md` finding **F4**. After a debug hop onto Map 11, the four talismans (shape 596, `TypeTalisman`, frames 0-3 = Earth/Air/Fire/Water) lay on the floor again while the carried ones stayed in the pack (`findShape 596`: 4 → 8). The suspicion was that EggReapply (`lv-new/REAPPLY.UNK`, class `0x5B2`, a quality-307 UnkEgg) runs only on Map 11's two arrival pads, and that the debug hop skipped them. The pads are 203 at (9728,1792,0) in the hub hall, the arrival from Map 9, and 204 at (8291,22639,0) in the teleporter room, the arrival from Map 10 (`build_map_11.py:312`, `:1002`).

**Build under test.**
- main `0752338`. The harness `shared/u8-lv-patched` matched `shared/build/ARTIFACTS.sha256`: TYPEFLAG `e25d7224`, U8SHAPES `2b274856`, ANIM `97ae5fc9`, EUSECODE `b47c324c`, FIXED `fc92ee5f`.
- Game directory: a pinned copy at `/tmp/claude-1000/tal1031/game`, with `u8monsters.ini` `fda1bef8`. Binary: a copy of `scummvm-lv-console/scummvm`, `e0518ced…`.
- `sha256sum -c pinned-start.sha256` was OK at the end for all eight pinned files (five artifacts, top-level FIXED, the ini, the binary).
- Display: Xvfb :95, 640×400 with `usehighres`. Driver: the replay `lv.py`, repointed at the pinned copy. The `debugflag_enable Object` channel was on in every session.
- Saves: `replay1017-s04a-m11-four-talismans-hp20` (all four talismans in the pack, no pillar used) and `replay1017-s03b-m11-arrival-hp27` (Map 11 arrival, none picked up). Both were loaded with `--save-slot`.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| T1 | Carried, walked in: EggReapply fires on arrival; no floor copy of a carried frame; uncarried ones still lie on the floor | **PASS, both variants, pad 203.** **T1a** (all four carried): walked 202 → Map 9 → 203 → Map 11 pad 203. The log shows `event 7 @ 05B2:0080`, and `findShape 596` = 4, all in the pack. **T1b** (Earth and Air dragged into the pack, Fire and Water left): the same walk gave the `05B2` hatch, and `findShape 596` = 4: f0 and f1 in the pack, and f2 and f3 on the floor at their placements under fresh ids |
| T2 | Used, walked in: the talisman tied to a destroyed pillar is not back on the floor | **PASS, pad 204.** The Fire receptacle used the Water talisman: the bark "The water talisman glows with a cold light!", 06A2 (FireColumnDestroyed) = 1, and the Fire pillar was gone. I then walked 205 → Map 10 → 204 → Map 11 pad 204. The log shows the `05B2` hatch. `findShape 596` = 3, all in the pack, so the Water record (f3) was not back. `findShape 865` = 3 (Fire still gone), and the q299 boulders still stand, as they should with three pillars up |
| T3 | Negative control: a debug teleport onto Map 11 (no pad) reproduces F4 | **PASS (F4 reproduced, twice), and the pad cures it.** **T3a**, the T1a state: walked out to Map 9, then debug-teleported to (9728,1600), off the pad. There was no `05B2` event, and `findShape 596` = **8** (4 pack + 4 floor). A walk onto pad 203 then logged `05B2` and returned **4**. **T3b**, the T2 state: walked out to Map 10, then debug-teleported to (8400,22850), off pad 204. No `05B2`; `596` = **7**, including the spent Water talisman, and `865` = **4**, with the Fire pillar back. A walk onto pad 204 logged `05B2` and returned 3 and 3 |
| T4 | On a T1/T2 failure, capture the evidence and the cause | **Not needed.** T1 and T2 passed |

**F4 is not a player-facing defect.** Both arrivals a player can make onto Map 11 run EggReapply, and it removes exactly the records it should. The duplicates appear only when an arrival skips the pad. Of the routes tested here, only the debugger's teleport does that. As soon as the Avatar steps onto a pad, the same egg cleans them up. The 10-30 report's `[INFERENCE]` that "a player who re-enters Map 11 after collecting them sees them again" is disproved for walked re-entry.

The excerpts behind every number below are in `docs/playtest-2026-10-31-talisman-reentry/log-excerpts.txt`, filtered from the session logs with their line numbers.

## T1: carried, walked in (PASS)

**T1a. All four carried, pad 203.**
- **Before.** s04a put the Avatar on Map 11 at (12706,18870,0), weight 80. `findShape 596` = 4, all at `(255,255)` (inside the pack). 06A1-06A4 = 0, `865` = 4.
- **Setup.** A positioning teleport on the same map to (9728,1600,0), between pad 203's egg box and trigger 202's box. It caused no map load.
- **Out.** A 1.0 s walk N entered trigger 202, logging `Unloading map 11` → `Loading Fixed items in map 9`. He arrived on Map 9 at (14336,15856).
- **Back.** A 1.6 s walk S entered trigger 203. The log shows `Loading Fixed items in map 11` (T1a log line 252), then **`Item: 16240 (shape 73) calling usecode event 7 @ 05B2:0080`** (line 289). He stood at (9728,1792,0), on the pad (`T1a-m11-pad203-arrival`).
- **After.** `findShape 596: 4 found`, all four in the pack, with no floor record. `865` = 4, which is right with all flags 0.

**T1b. A mixed pack, pad 203.** This is the case that shows the guard is per frame, not "remove all".
- **Before.** s03b at (9728,1896), weight 40. `findShape 596` = 4, all on the floor: 17586 f0 (2047,5631,4), 18134 f1 (17152,5120,0), 21148 f2 (5631,18943,4) and 27725 f3 (12799,18943,4).
- **Pickups.** Real drags onto the Avatar, each after a positioning teleport beside the talisman:
  - Air 18134: `Dragging item 18134` → `Dropped item in backpack`, weight 40 → 50 (`T1b-1-air-picked`).
  - Earth 17586: the same three lines, weight 50 → 60 (`T1b-2-earth-picked`).
- **Out and back.** A setup teleport to (9728,1600,0). A walk N entered 202 → Map 9 (14336,16128), and a walk S entered 203 → Map 11. Then **`Item: 3748 (shape 73) calling usecode event 7 @ 05B2:0080`** (T1b log line 389) (`T1b-3-m11-pad203-arrival`).
- **After.** `findShape 596: 4 found`:
  - 17586 f0 and 18134 f1 in the pack (`(255,255)`).
  - **25208 f2 at (5631,18943,4) and 592 f3 at (12799,18943,4)**, both on the floor. These are fresh ids, re-read from FIXED, so the uncarried ones were kept.
  - No floor f0 or f1.
  - `865` = 4.

## T2: used, walked in (PASS)

**Use.**
- This started from the T1a/T3a state (four carried, nothing used). A positioning teleport went to (8063,21759,0), beside the Fire receptacle.
- A double-click on receptacle 6264 (7935,21759) q203 logged `Item: 6264 (shape 866) calling usecode event 1 @ 0478:00B4` (T1a log line 794). The Avatar barked **"The water talisman glows with a cold light!"** (`T2-1-fire-receptacle-bark`).
- **Right after.** `596` = 3 (f0, f1 and f2 in the pack; Water 27725 consumed), weight 80 → 70. `865` = 3, with the Fire pillar (f2, (7680,21504)) gone.
- **Flags, read again a few seconds later.** 06A1 = 0, **06A2 = 1**, 06A3 = 0, 06A4 = 0, 06EC = 0. So 06A2 is FireColumnDestroyed, which matches `FLAGS.UNK`'s order: Water, Fire, Earth, Air. (The first read gave 06A2 = 0; see H4.)

**Out and back.**
- **Setup.** A positioning teleport on the same map into the teleporter room, at (8400,22850,0). The room is sealed from the pillars by the q299 boulders, and the spot is outside pad 204's egg box and trigger 205's box.
- **Out.** A walk SE entered 205. The log shows `Loading Fixed items in map 10`, Map 10 pad 205's own EggReapply (`32746 … 05B2`), and an arrival at (12864,2624) (`T2-2-map10-pad205`).
- **Back.** Walks NW (1.3 s + 1.2 s) entered trigger 204. The log shows `Loading Fixed items in map 11` (T1a log line 1064), then **`Item: 7937 (shape 73) calling usecode event 7 @ 05B2:0080`** (line 1109). He stood at (8259,22607), on pad 204 (`T2-3-m11-pad204-arrival`).

**After.**
- `findShape 596: 3 found`, all three in the pack. **No floor record of f3**, the used Water talisman. Its removal can only come from the FireColumnDestroyed gate, because no f3 is carried.
- `findShape 865: 3 found`, frames 0, 1 and 3. The Fire pillar stayed down.
- `findShape 66` still lists both q299 sealing boulders, 25040 and 25041 at (8576/8704,22528). That is correct: 06EC (allColumnsDestroyed) = 0.

(Q1-11 of `docs/playtest-2026-10-11-gates.md` already covered the all-four-used case on pad 204, with 0 talismans and 0 pillars. This test covers one used and three carried.)

## T3: negative control, debug arrival (PASS, F4 reproduced)

**T3a. The T1a state, pad 203 skipped.**
- From the T1a arrival (four carried, 0 on the floor), a walk N entered 202 → Map 9 (14336,16024).
- `Cheat::toggle` → `MainActor::teleport 11 9728 1600 0` → `Cheat::toggle`. The log shows `Loading Fixed items in map 11` (T1a log line 451), and **no `05B2` event** between that load and the reads (`T3a-1-debug-arrival-hall`).
- **`findShape 596: 8 found`** (line 518). The pack holds 17586, 18134, 21148 and 27725. The floor holds 23538 f0 (2047,5631,4), 6093 f1 (17152,5120,0), 4619 f2 (5631,18943,4) and 6139 f3 (12799,18943,4). This is F4 exactly.
- **The cure.** I walked S from (9696,1568) to (9696,1968), across pad 203's egg box. The log shows **`Item: 5990 (shape 73) calling usecode event 7 @ 05B2:0080`** (line 700), and **`findShape 596: 4 found`**, all in the pack (`T3a-2-walk-onto-pad203`, taken mid-walk). (The walk started only after H1.)

**T3b. The T2 state, pad 204 skipped.**
- From the T2 arrival (three carried, Fire used), a walk SE entered 205 → Map 10 pad 205 (12800,2560).
- A debug teleport to Map 11 (8400,22850,0) logged `Loading Fixed items in map 11` (T1a log line 1315), with **no `05B2` event** (`T3b-1-debug-arrival-telroom`).
- **`findShape 596: 7 found`**: the three in the pack, plus floor 15052 f0, 4588 f1, 24499 f2 and **5956 f3**. The spent Water talisman was back.
- **`findShape 865: 4 found`**: the **Fire pillar 8577 (f2) was back** too. The pillar half of REAPPLY depends on the pad in the same way.
- **The cure.** A walk NW to (8340,22790), into pad 204's egg box, logged **`Item: 1821 (shape 73) calling usecode event 7 @ 05B2:0080`** (line 1438). After it, `596` = 3 (all in the pack) and `865` = 3 (`T3b-2-walked-onto-pad204`).

**What the control shows.** The game state and the Map 11 reload were the same in both cases. The arrival kind decides the outcome: a walked arrival lands on the pad, EggReapply hatches, and the records go. A debug teleport lands off the pad, so nothing hatches until the Avatar walks onto it.

## Findings

1. **F4 (10-30) is a debug-teleport artifact, not a defect.** Severity: info. Recommendation: close it, with a pointer to `docs/playtest-2026-10-11-gates.md` finding 2, which reported the same dependency on Map 10. A tester who hops onto Map 11 with the debugger should walk across pad 203 or 204 before counting talismans or pillars. The pillars come back on a debug hop as well, once one is down (T3b: the Fire pillar). In the 10-30 E3b run all four flags were still 0 at the hop, so only the talismans were stale there: the four floor duplicates it counted. Not tested: whether any non-pad arrival exists for a player. The REAPPLY header says none does, and the 10-11 gates report audited the usecode teleports. Loading a save made on Map 11 was not part of this run.
2. **The guard's two gates work independently and per frame.** T1b kept the uncarried f2/f3 and removed the carried f0/f1. T2 removed the used f3 by its flag alone, with no f3 carried.

## Harness anomalies

- **H1. The Avatar would not move after a cross-map debug teleport, for a while.**
  - **After 9 → 11 (T3a).** Four `run()` holds (S, then E/W/N/SE probes) logged `event 18` with zero displacement. So did two more holds after a same-map relocation to (9696,1568). A plain right-button hold then moved him 400 units S (`H1-no-move-after-debug-teleport`, taken while he was stuck).
  - **After 10 → 11 (T3b).** The first hold did nothing, and the second moved him.
  - **Where it did not happen.** Walked arrivals and same-map setup teleports never did this.
  - **Interpretation.** It looks like the teleport-wedge trap, but it cleared without relocating [INFERENCE: transient].
- **H2. One `ATTACH FAILED` on the T3a teleport.** The console turned out to be attached already, so the teleport was sent straight to it. Every `Cheat::toggle` pair stayed balanced, each verified by its echo.
- **H3. The first drag at the Air talisman lifted floor tile 7649 (shape 301) instead.** The log shows `Dragging item 7649`. The tile read back at its place, (17151,5119,0). Single-click probes found the talisman 3 px lower, at (321,239), and the next drag took it.
- **H4. A `getGlobal` right after the receptacle use read 06A2 = 0.** COLPUZZL sets the flag after `wait (30)`, and an attached console pauses the world, so the read came before the scene ended. A later read gave 1.

## Console commands used

- **Reads:**
  - `ObjectManager::objectInfo` 1 and 7649;
  - `ObjectManager::findShape` 596, 865, 866, 66, 1;
  - `UCMachine::getGlobal` 0x6A1-0x6A4, 0x6EC (and 0x7FE as a console probe).
- **Flags:** `debugflag_enable Object` after each start.
- **`Cheat::toggle`:** only in on/off pairs around teleports.
- **`MainActor::teleport`, setup (same map, no map load):**
  - 11 (9728,1600,0) twice;
  - (9696,1568,0), the H1 relocation;
  - (8063,21759,0), (8400,22850,0), (17056,5024,0), (1952,5560,0).
- **`MainActor::teleport`, T3 only (cross-map):**
  - 9 → 11 (9728,1600,0);
  - 10 → 11 (8400,22850,0).
- **`Ultima8Engine::saveGame`:** three times to the scratch slot; the copies are in `sp/`.
- **Not used:** setGlobal, heal, invincibility, item cheats, `Item::grab`.

## Disk changes

- **Wrote:**
  - this report;
  - `docs/playtest-2026-10-31-talisman-reentry/` (11 plates named by test ID, `H1-…`, and `log-excerpts.txt`).
- **Scratch only, `/tmp/claude-1000/tal1031/`:**
  - the pinned game and binary;
  - `py/` (the replay drivers, repointed);
  - `saves/` (checkpoint copies in slots 3 and 4, scratch slot 1);
  - `lv_T1a.log`, `lv_T1b.log`, `trace.txt`, and `sp/` (plates and the three scratch saves).
- **Not changed:**
  - `~/lv-checkpoints` (s03b `4fdbe669` and s04a `308b3937` re-hashed at the end);
  - `shared/`, source, TODO and HANDOFF;
  - no rebuild, no commit.
- My ScummVM and Xvfb :95 are stopped.
