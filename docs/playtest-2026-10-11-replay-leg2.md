# Single-build replay of the 1→18 run, leg 2: step 2 done, step 3 done, step 4 at 3 of 4 talismans (2026-10-11)

Leg 2 of the one-build replay. It continues from leg 1's banked save on the same pinned game copy (`docs/playtest-2026-10-11-replay-leg1.md`).

## Build pinned (re-checked)

- **Game copy.** `/tmp/claude-1000/replay/game`, as leg 1 left it; it was not re-copied. `sha256sum -c pinned.sha256` run inside it gives OK for all six files, both at the start and at the end of the session: EUSECODE `4182e079…`, FIXED (root and `STATIC/`) `122b4374…`, U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…`, ANIM `77e9705d…`.
- **Binary.** The session ran on one process, launched at 17:38 from `scummvm-lv/scummvm` (04:17). The log shows `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `usecode/eusecode.flx: d00d0d5962e966129c2277c7cea7844b, 1526311 bytes`, with no `Couldn't identify`.
  - Main's later notice pinned a copy at `/tmp/claude-1000/pinned-bin/scummvm-4182e079` (sha256 `1502d576…`). The driver was switched to that path for any relaunch, but none was needed.
- **Harness.**
  - Leg 1's ini: 320×200, no width/height keys (`Setting Video Mode 320x200`), music on, `SDL_AUDIODRIVER=dummy`. Xvfb `:95`.
  - Leg 1's `rp.py`/`navr.py`, used from the eval kernel. The log was retargeted to `replay/lv_run2.log` and the trace to `trace2.txt`.
  - The prime left click was turned off (traps.md jump trap). In its place, each move starts with a sacrificial 0.2 s right press, which absorbs the input swallowed after a console close.
- **Cheats: 0.** `Cheat` appears 0 times in `lv_run2.log` (44,450 lines). The console was used only for `objectInfo`, `findShape`, `getGlobal`, `debugflag_enable Object`, `saveGame` and `loadGame`. Every move, drag, key use, door and menu pick was player input.
- **Deaths: 3, plus 4 reloads before death.** All three deaths are explained below; no `w3-m7-mid`-type bad save was banked.

## Verdicts

| Step / leg | Verdict | Evidence |
|---|---|---|
| Hut door → island | **PASS** | DOOR_NS 7820 `event 1 @ 0044:0098`. A walk W 1.6 s gave `2546 (shape 73) event 7 @ 04C6`, landing at the island (6078,1786,0) |
| Island walkway | **PASS on the second line** (finding 4) | The first line drifted to y≈2000 into a sphere row: hp 30 → 2. I reloaded `s01c`. Second line: walk S 0.5 s to y 1818, then run bursts to 5294, 4710 and 4326 at hp 30. Trigger 4 fired and the run carried on up the stair to (1848,1632,8), then (1448,1632,48) |
| **Step 2: Mythran** | **PASS** | NPC 33 strike `event 1 @ 0421:A125` (`s02-mythran-opening`). Picks, from the screen: Lord British says they can help me. → Who searched for the Zealans? → What happened to him? → Where are these double doors? → How do I open the doors? → Farewell. After: `[0717]`-`[071B]` = 1 (ToldZealans/Galjeron/Doors/Key, IntroDone), `[071C]` = 0, lbDone `[06A6]` = 1 (`s02-mythran-flags`) |
| Island exit egg 2 → plateau | **PASS** | E along y 1836, then NE → (14138,15118,48) |
| Plateau → T26 → north pad | **PASS after 1 death** (finding 5) | Death 1: drowned (`shape 347 event 6 @ 015B`) after an overshoot on the cliff-edge corridor at y≈13400. The retry used axis runs along y 13382 → T26 → pad 26 (14540,7924,0), hp 30 |
| Spitter 1 → safe pocket | **PASS after 1 death, 1 reload** | Death 2 (finding 6): the engine refused N at x 17532 (y 5588-5260), and FIREMISS 697 hits killed the Avatar while he was wedged. Retry 1: hp 30 → 15 (reload). Retry 2 was the waypoint line (15608,7208) → E → (16623,7208) → NE → (17450,6381) → N → E, one held run: (18164,5084), hp 30 |
| Pocket → doors chamber, first contact | **FAIL ×3 (808 pair), and 1 skip** (findings 1-2) | Plain RUN10 (E 3.54 s, N 2.5 s) from y 5020 walked over the T212 slab → **Map 10** (finding 1). E 3.0 s, N 2.5 s reached (20212,3596,8), and the chest gump opened (`event 1 @ 004E:00A9`), but the 808s took hp 30 → 9 within about 12 s (`F2`). Death 3 came during my think time with the gump open |
| **Step 3: key → leaves → T201 → Map 9** | **PASS** (via the 213 return, finding 2) | I came back from Map 10 by its trigger 213 → Map 8 (19975,3351,8): `findShape 808` read 0 found. Chest 21663 → key 21664 (`event 1 @ 0052:04BB`). The first target, from about 280 units, left q 1635 unchanged (finding 3). From (20327,3151) one use set **22113 1635 → 611 and 22115 1123 → 99**. A double-click opened both leaves (shape 340, (20255,3071)/(20479,3071)) (`s03-doors-open`). Run N 1.5 s → **Map 9 (13696,13408)** (`s03-m9-arrival`) |
| Map 9 → T203 → Map 11 | **PASS** | Box x[13952,14784) y[16408,17176). Run S from x 14292 → **Map 11 (9728,2664,0)** (`s03-m11-arrival`) |
| Step 4: talismans | **PARTIAL, 3 of 4** | Earth 26109 q101 (w 20 → 30), Air 26454 q102 (w → 40, finding 7), Water 27433 q104 (w → 50, `s04-three-talismans`). Each logged `Dropped item in backpack`. hp 30 throughout Map 11, and no egg hatched. The routes forbade the 318/435-437 hazards, the 409 lakes (+192) and every shape-500 egg column |
| Step 4: Fire, pillars, T205; steps 5-18 | **NOT DEMONSTRATED** (budget) | — |
| Music on | **PASS (no hang)** | About 90 min, the console answered throughout |
| Log hygiene (`lv_run2.log`) | **PASS for LV code** | 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, ERROR. **4 × `Unhandled intrinsic 254 'isGameRunning()'`**: the known CHEST_EW `004E:00A9` family, from 3 chest opens. **20,577 `Cycle in paint`**: 20,552 are the retail `590 -> 235` bone-chamber pair, 17 are `235 -> 65` and **8 are `10 -> 1`**. The `10 -> 1` lines are not traced; shape 10 is retail. 3,144 `shape 227 event 2 @ 00E3` lines: an animated retail door ticking while loaded, not a fault |

## Findings

1. **First visit: the natural way into the doors chamber walks over trigger 212's slab and sends a player to Map 10 with steps 3 and 4 skipped.** Severity: high (a sequence break).
   - **Repro.** Load `~/lv-checkpoints/replay1011-s02d-m8-pocket-t212-repro.sav`: Map 8 (18164,5020,0), hp 30, step 2 done, Map 8 fixed items from this build.
   - **The run.** A held mouse run E for 3.54 s, then N for 2.5 s. That is part 4's "RUN10", which part 4 started 12 units further west and which then ended at (20212,3592).
   - **Result.** It ended on **Map 10 (13824,2288,0)** with the doors still locked, the key in the chest and no talismans. The log shows `Unloading map 8` → `Loading Fixed items in map 10`. Plate `F1-t212-skip-map10-arrival`; evidence save `replay1011-s02x-m10-via-t212-slab-SKIP.sav`.
   - **The trigger.** In the pinned FIXED it is the teleporter at (20575,3903,0), q `0x1d4`, npcnum `0x11`, map 10 (`build_map_08.py:314-351`, `TELE_213_TRIGGER_*`). Its box covers a body max corner in x [20543,20671), y [3871,3999).
   - **Why it is in the way.** The builder comment proves only that the **arrival pads'** headings miss it (`arrival_corridors`). It does not consider the **first-visit approach from the south**, the spitter corridor. A run north on x≈20575, only 300 east of part 4's line, crosses the slab.
   - **Effect.** `TeleportEgg::hatch` is unconditional (route guide line 105), so a player who drifts east on the way in arrives in the Vale with steps 3 and 4 undone.
   - **Classification.** An LV map defect. Gate it on quest state, or move it off the corridor's northbound lines.
2. **The shape-808 pair makes the honest first visit unwinnable without a map change, and the T212 → 213 round trip is what defuses it.**
   - **First visit.** Within about 12 s of reaching the chest the pair had taken hp 30 → 9, before the key reached the leaves.
   - **After a map change.** On the 213 return (Map 10 trigger 213 → Map 8 (19975,3351,8)), `findShape 808` read 0, and the whole chest/key/door sequence ran unhurt. This matches part 4's finding 3, but by a second map-change route.
   - **The step-3 PASS above depends on this.** A player can do it (the slab and 213 are both in the world), but it rests on finding 1's skip.
   - **Classification.** Retail monsters with LV routing; this is the balance question parts 3 and 4 raised.
3. **The key use needs the Avatar close to the leaf.**
   - **From about 280 units:** at (20327,3351) the target logged `Target result: Item 22113 … q: 1635` and q stayed 1635.
   - **From the leaf face:** at (20327,3151) the same use unlocked both leaves.
   - **So** part 4's finding 4 ("first use did nothing") is reach, not line of sight [INFERENCE: KEYRING's `canReach(target,128)`]. There was no bark to tell the player why.
4. **The island walkway's sphere rows hit at y≈1986-2014.** The landing (6078,1786) is 32 north of the safe lane. A W burst slid onto a post at (5954,1766), and a recovery S walk overshot to y 2014 into a sphere row: hp 30 → 28 → 2. A 0.5 s walk-gait S step (mouse offset 50 px) lands exactly on y 1818. Harness and route note; no defect.
5. **The plateau's west corridor at y≈13400 runs along a cliff above water, and overshoot drowns.**
   - **What happened.** Death 1 came after a NW/W burst from (10442,13822): `5206`/`2331 (shape 347) event 6 @ 015B`.
   - **The geometry.** The water tiles start at y≈13695 (z 0) and the shrooms crowd the north side, so the only lane is y≈13382-13470.
   - **What worked.** A walk N to y 13382, then pure W runs.
   - **Classification.** Retail geometry; a route-guide note.
6. **North corridor: at x≈17532, y 5260-5588 the engine refuses N where `exact_reach` (erode 2, NONFIXED included) allows it.**
   - **What happened.** The Avatar wedged there in the MISSTRAP lanes and died (FIREMISS `02B9` hits).
   - **What worked.** The x≈17450 line (part 3) went through.
   - **Classification.** The same model/engine step mismatch as `.claude/rules/map-geometry.md`; retail geometry.
7. **The Air talisman's pick pixel is narrow.** It rests at z 0 on LV floor tile 301 item 12994 (17151,5119,0).
   - **What happened.** A press at the ring's centre (421-426, 244-250) grabs the tile ("Dragging item 12994", "Dropping object", no pickup). Only the ring's top (426,238) or bottom (428,256) pixels hit 596.
   - **Effect.** A player will feel it as "the talisman won't pick up". Low severity.
   - **Contrast.** The Earth talisman is at z 4 and has no such problem.
8. **The `10 -> 1` paint cycle (8 lines)** is new in this log. Its location was not traced. It is listed for whoever owns the item_sorter port.

## Harness anomalies

- **Menu clicks.** Only a mousemove, a 0.4 s settle, then a down/up with a 0.25 s hold registers a conversation click (part 5's rule). The first click after a console close is dropped, so Mythran's Farewell needed a second click.
- **Short presses.** Run presses with a first leg under about 0.3 s do nothing. A one-direction walk-gait press (offset 110 px, 0.45 s) moves about 100 units and fixes "short first leg" stalls.
- **The router.** 8-unit lattice routes are zigzags. A lookahead follower (an 8-direction heading to the point 650 path-units ahead, with neighbour headings when stuck) crossed Map 11 from Air to Water in one cell.
- **Thinking time is game time.** In the doors chamber, every tool-call gap let the 808s act. Death 3 came while I read a screenshot.
- **Chest gump.** It drifts with the camera when the Avatar moves; re-locate the key by screenshot after any move.
- **A banked file was wrong once.** `bank()` copied the slot after a `saveGame` that had failed. The bad file was removed at once and re-banked after a good save. Make `bank` assert the save first.

## Checkpoints (all new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `replay1011-s02-m8-mythran-intro-done.sav` | `eeb4ef8d` | Mythran upstairs (1560,1388,48), step 2 flags set |
| `replay1011-s02b-m8-north-pad26.sav` | `a70fd1e9` | North pad (14540,7924,0), hp 30 |
| `replay1011-s02c-m8-corridor-pocket-hp30.sav` | `369c52d1` | Pocket (18164,5084,0), hp 30 |
| `replay1011-s02d-m8-pocket-t212-repro.sav` | `01106c08` | Pocket (18164,5020,0): **finding 1 repro start** |
| `replay1011-s02x-m10-via-t212-slab-SKIP.sav` | `05b722c7` | Map 10 (13824,2288) via the slab. **Evidence only** |
| `replay1011-s02e-m8-niche-via-213-no808.sav` | `6c555fbb` | Map 8 (19975,3351,8) after the 213 return, 0 × 808, doors locked |
| `replay1011-s03a-m8-doors-unlocked-open.sav` | `121cee0f` | (20327,3151), both leaves open, chest gump open |
| `replay1011-s03b-m9-arrival-via-doors.sav` | `4bc1cfba` | Map 9 (13696,13408), **step 3 done** |
| `replay1011-s03c-m11-arrival.sav` | `c74d97ca` | Map 11 (9728,2664,0) |
| `replay1011-s04a-m11-earth-talisman.sav` | `c816ace2` | (2120,5508), w 30 |
| `replay1011-s04b-m11-earth-air-talismans.sav` | `39a91314` | (17000,5180), w 40 |
| **`replay1011-s04c-m11-three-talismans.sav`** | `2f4007ad` | Map 11 (12848,18904,0) by the Water talisman island, hp 30, w 50, holding Earth, Air and Water. **Leg 3 resume point** |

## Resume (leg 3)

1. **Start.** Use the same game copy and ini, and launch with **`/tmp/claude-1000/pinned-bin/scummvm-4182e079`**. Main's rebuilt `scummvm-lv/scummvm` no longer detects EUSECODE 4182e079. Copy `replay1011-s04c-…` to `saves/ultima8.001`, start with `--save-slot=1`, then send `debugflag_enable Object`.
2. **Fire talisman (5631,18943,4).** Enter by the Fire doorway (x≈6144, y 16384..16896) from the Water section. Forbid 318, 435-437 (+160), the 409 lakes (+192) and the shape-500 columns. Drag it from the north.
3. **Pillars.** Use the receptacles at (7680/8704, 20736/21760) with the pack closed: Earth ← Air, Air ← Earth, Fire ← Water, Water ← Fire. Then T205 (8960,23296) → Map 10. After that, steps 5-18 per parts 5-7.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-replay-leg2/` (10 plates).
- **Wrote** the 12 checkpoints above in `~/lv-checkpoints/`.
- **Scratch** in `/tmp/claude-1000/replay/`: `lv_run2.log`, `trace2.txt`, `sp/l2-*.png|sav`, and new `er_*.pkl` for Maps 8, 9 and 11. The game copy is unchanged; its hashes were re-checked at the end.
- **Stopped:** my ScummVM (pid 820198) and Xvfb `:95` (pid 820192). Another agent's `vmon` ScummVM was left alone.
- **Not touched:** source, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, and both binaries.
