# Armed Avatar vs the Map 13 lane harpie pair: 10 runs, sword and axe, no invincibility (2026-10-18)

This is an isolated balance test, not a step of the no-cheats chain. It asks whether "the player has a weapon by Map 13" is a safe design assumption for the lane harpie pair (`build_map_13.py:363-411`, trigger `0481` at (5119,4479,84), eggs `HARPIE_LANE` (5023,3999) and (5183,3967)). The 2026-10-17 replay's Avatar was unarmed and the pair killed him twice (`docs/playtest-2026-10-17-replay-leg5.md` findings 1-2). The one earlier armed fight (`docs/playtest-2026-10-11-monsters2.md` M2) had one harpie and invincibility on.

## Verdicts

| Claim | Verdict | Evidence |
|---|---|---|
| **An armed 30-hp Avatar reliably beats the pair** | **FAIL** | **5 wins in 10 runs.** With the sword he won 3 of 7, and with the axe 2 of 3. The winners ended at hp **2, 10, 17, 22 and 22**. Every loss was a death, in 22-78 s |
| Both lane harpies hatch on a walked arrival | **PASS, 10 of 10** | `Item … (shape 73) … event 7 @ 0481:0080` in every run, and `findShape 873` listed 160 and 161 at their egg spots at the first read. monsters2 finding 4 (only one hatched) did not reproduce |
| Harpie hp is within 30-45 | **PASS** | The 20 hatches read 30-45, mean 38.4 |
| The weapon damages the harpie | **PASS** | Sword blows did 5-14 (mean 9.0) and axe blows 6-15 (mean 9.3), `type=2` and `type=6` |
| Rest point (5087,3039) is quiet after the pair is dead | **PASS** (X2 only) | 90 s standing at (5120,3032,112): 0 `0481` hatches, 0 hits. `findShape 873` listed only the two lane corpses |
| Rest point lets him recover **between the two harpies** | **NOT DEMONSTRATED; there is no "between"** | The pair arrive together. The first blow on him landed 9-23 s after the hatch. In 8 of the 10 runs both harpies were still alive when it did; in S5 and X2 he had killed one first. Healing is the global 1 hp a minute, at the rest point or anywhere else |

## Build pinned

- **Game copy, binary and ini.** These are the replay's own: `/tmp/claude-1000/replay1017/game`, `bin/scummvm-console` and `scummvm.ini` (320×200, `scale_factor=2`). `sha256sum -c ../pinned.sha256` gave OK for all six files at the start and at the end. The log reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `usecode/eusecode.flx: 84615e29d097543ed69da844fbc3948f, 1528891 bytes.`
- **Scratch.** Everything this session wrote is in `/tmp/claude-1000/harpie1018/`: the saves dir `saves/`, one log per run `lv_<run>.log`, the fetch logs `lv_harpie.log` and `lv_axefetch.log`, the frames `sp/`, the trace and the per-run records `runs.json`. The replay's `saves/` (slot files md5 `902249b4`/`2503687e`) and its `replay1017-*` banks were not written.
- **Display.** Xvfb `:95`, using the `py/lv.py` driver with its `SAVES`, `LOG`, `CMDS`, `SP` and `TRACE` pointed at the scratch dir.

## The Avatar at s13b

`replay1017-s13b-m13-pre-lane-z80-hp30.sav`, Map 13 (5128,4776,80). `objectInfo 1` read **hp 30, mp 30, str 15, dex 15, int 15, ac 0, defense 0**, weight 60. The paperdoll gave STR 15, INT 15, DEX 15, ARMR 0, HITS 30, MANA 30 (`A0-s13b-stats-paperdoll`).

- **Max hp is 2 × STR = 30** (`Actor::getMaxHP`, `actor.cpp:104`). These are the new-game numbers, because the replay's Avatar never fought.
- **What fighting along the way would change.** Every swing and every blow received accrues STR and DEX (`u8_avatar_mover_process.cpp:170-172`, `actor.cpp:1176-1180`). STR raises max hp. DEX shortens the attack cooldown, which is `25 − DEX` frames (`u8_avatar_mover_process.cpp:792`). Two runs here rose to STR 16 mid-fight.
- He has no armour. Nothing in this test added any.

## Console commands used (all runs)

- `debugflag_enable Object` and `debugflag_enable Actor`, after every start. The `Actor` channel is what logs `received hit`.
- `ObjectManager::objectInfo 1` and `ObjectManager::findShape 873` (also `420` and `419` during the fetches). These were the fight driver's only reads.
- `Cheat::toggle`, 4 times: on before each weapon fetch and off after it, each echoed `Cheats = true` / `Cheats = false`. It was off for every fight.
- `MainActor::teleport`, 4 times, only for the fetches:
  - `9 13850 14230 0` to Galjeron's sword, then `13 5128 4776 80` back to the s13b spot;
  - `11 9540 4400 0` to the hub axe, then `13 5128 4776 80` back.
- `Ultima8Engine::saveGame`, 2 times, for the two banks below.
- **Not used:** invincibility, heal, `Cheat::items`, setGlobal, loadGame, `MainActor::toggleCombat`. The log has 0 `invincib` and 0 `Cheat::heal`. The only `Cheat` lines are the four `Cheats = …` echoes in the two fetch logs.
- **Reloads** were done by restart: stop, copy the bank over scratch `saves/ultima8.001`, relaunch with `--save-slot=1`.
- **Combat mode** was the real `c` key. The paperdoll was the real `z` key.

## Weapon fetch

- **The sword** (`B1-m9-sword-on-floor`, `B2-sword-equipped-paperdoll`).
  - Item 20227 SWORD2 (420) lay at (13920,14304,0) beside Galjeron.
  - With the paperdoll open, a real left-drag from the floor onto the doll logged `Dragging item 20227` → `Dropping object 20227`. The doll showed the sword in hand, and weight went 60 → 90 (WGHT 6 → 9).
  - Back on Map 13, the walk went S to (5128,4880), then E to **(5232,4880,80)**. Bank **`harpie1018-s13b-armed-sword-hp30`**.
- **The axe** (`C1-m11-axe-on-floor`, `C2-axe-equipped-paperdoll`).
  - This fetch started from the **unarmed** s13b save, so the axe runs carry no sword.
  - Item 23360 AXE2 (419) lay at (9599,4479,0). The same drag gave `Dragging item 23360` → `Dropping object 23360`, the axe in hand, and weight 60 → 110 (WGHT 11).
  - The same walk back gave **(5232,4880,80)**. Bank **`harpie1018-s13b-armed-axe-hp30`**.

The trigger box spans y 4415-4543, x 4927-5311 (npcnum `0x62`). Each run loaded the bank and walked into it:

- **S2-S7, X1-X3:** W 0.7 s (5232 → 5032, 200 units), then N 1.15 s (4880 → 4584, 296 units). That is **≈ 500 units walked, ≈ 470 before the box.**
- **S1:** the W press was dropped. The walk was 296 units N along x 5232, and only **≈ 270 before the box**. That is below the 300 asked for. It is still a walked arrival from a save, with no teleport.

## Runs

Read the table this way:

- **hp start → end** is the Avatar's own hp.
- **"Landed"** and **"taken"** count logged `received hit` lines, as damaging / total (total damage). A blow that connected but rolled `No damage.` is in the total and not in the first number. A swing that met nothing logs nothing.
- **Elapsed** runs from the end of the walk into the trigger to the last read.

| Run | Weapon, driver | Hatched (hp) | hp start → end | Outcome | Elapsed | Landed by him | Taken |
|---|---|---|---|---|---|---|---|
| S1 | sword, v1 | 2 (44, 30) | 30 → **17** | **both killed** (25.6 s, 52.2 s) | 52.9 s | 9/10 (77) | 2/4 (14) |
| S2 | sword, v1 | 2 (41, 39) | 30 → **2** | **both killed** (23.6 s, 50.6 s) | 54.7 s | 10/22 (98) | 4/9 (29) |
| S3 | sword, v1 | 2 (39, 37) | 30 → **0** | **died**. 160 killed, 161 at 34 | 78.3 s | 4/7 (39) | 4/19 (32) |
| S4 | sword, v2 | 2 (41, 36) | 30 → **0** | **died**. 160 at 17, 161 at 24 | 28.0 s | 5/11 (36) | 5/7 (33) |
| S5 | sword, v2 | 2 (44, 38) | 30 → **22** | **both killed** (15.3 s, 36.1 s) | 40.3 s | 10/14 (91) | 1/4 (8) |
| S6 | sword, v2 | 2 (37, 44) | 30 → **0** | **died**. 160 killed, 161 at **4** | 41.5 s | 8/11 (80) | 4/9 (36) |
| S7 | sword, v2 | 2 (45, 43) | 30 → **0** | **died**. 161 killed, 160 at 30 | 50.2 s | 7/10 (54) | 5/10 (37) |
| X1 | axe, v2 | 2 (30, 38) | 30 → **10** | **both killed** (22.2 s, 43.7 s) | 44.5 s | 7/12 (71) | 3/10 (21) |
| X2 | axe, v2 | 2 (41, 38) | 30 → **22** | **both killed** (23.2 s, 36.8 s) | 40.9 s | 10/17 (86) | 1/11 (8) |
| X3 | axe, v2 | 2 (31, 32) | 30 → **0** | **died**. 160 at 21, 161 at 32 | 22.9 s | 1/4 (10) | 4/6 (32) |

**Totals.**

- **Sword: 3 of 7.** v1 won 2 of 3 and v2 won 1 of 4.
- **Axe: 2 of 3.**
- **All: 5 of 10.**
- **His blows:** 71 of 118 that connected did damage, 5-15, mean about 9.
- **The harpies' blows:** 33 of 89 did damage, **5-10, mean 7.6**. Four damaging blows kill a 30-hp Avatar.

Plates `<run>-hatch` (the Avatar at the trigger) and `<run>-end` (the last frame) are in `docs/playtest-2026-10-18-armed-harpie-pair/`. `S1-end`, `S2-end` and `X2-end` show both corpses. `S4-end`, `S6-end` and `X3-end` show the Avatar dead with harpies still flying.

### The fight driver

No human played these runs. A scripted loop stood in for the player, and it reads the world through the console. Each read is a `findShape 873` plus an `objectInfo 1` in one attach. The world is paused while attached, and a polled chord with no trailing sleeps costs about 0.1-0.3 s of live time per read. Between reads it takes one action:

- **v1** (S1-S3):
  - Stand at the trigger in combat mode.
  - If the nearest harpie's anchor is within 170 units, double left-click toward it twice, 0.7 s apart.
  - After 4 reads with nothing that close, take one 0.6 s combat advance toward it.
- **v2** (S4-S7, X1-X3):
  - Measure the **box gap**. A harpie is footpad 4×4×4 (128×128×32) and the Avatar is 64×64.
  - Aim at the centre of its box.
  - If the gap is 40 or less, double-click twice. Otherwise, take a 0.45 s combat advance toward it and swing once.

Neither driver blocks, retreats, drinks a potion, or uses the fast-area escape (leg 5 finding 2). A human could do all four.

## Findings

1. **Severity: high (balance). A weapon does not make the lane pair a fair fight for the Avatar as he arrives on the mandatory route (STR 15, DEX 15, 30 hp, no armour).**
   - **The numbers.** He won half the time. Two of the five wins ended at 2 and 10 hp.
   - **Why.** The pair together have 63-88 hp, mean about 77. That takes him about 9 damaging blows, at 9 a blow and roughly 60 % of connecting swings, with a swing at most every `25 − DEX` frames. They need only about 4 damaging blows (5-10 each, about 37 % of their blows).
   - **Both of them engage at once.** In every v2 run, wins included, both harpies stood within a 60-unit box gap of him at the same moment in 2-5 of the reads.
   - **Which driver did better.** v1 waited at the trigger. In S1 the fight came staggered: 161 withdrew to y ≈ 4071 at hp 18 for about 20 s, and he finished 160 meanwhile. v1 won 2 of 3; v2 won 1 of 4 with the sword. The sample is too small to call this a real tactic.
   - **Not settled.** Whether the assumption holds for a player who fought along the way. Max hp is 2 × STR, so every STR point is 2 hp. The data here cannot say how many STR points the earlier route gives.
   - **Options for whoever owns `build_map_13`.** This is for the design owner, not a decision made here. Hatch one harpie instead of two; lower the row's hp or damage in `u8monsters.ini`; or put armour or a healing potion on the route before Map 13.
2. **Severity: low. The two harpie corpses can close the centre lane to the north.**
   - **What happened.** After X2, the corpses lay at (4991,4327,92) and (5163,4331,92). They are shape 873, `SI_SOLID`, 128×128. The gap between their boxes, x 4991-5035, is 44 units, narrower than the Avatar's 64.
   - **The stall.** From (5024,4400), 20 follower rounds N, with unsticks, did not move him (`F2-corpses-block-centre-lane`). S, SW, W and E walks all moved him.
   - **The way round.** He went round by the east lane: (5236,4468) → (5236,4204) → N.
   - **Why it is low.** A player who looks will walk round. [INFERENCE] That the corpses, and not terrain, block that cell. The cell is open before the fight on the pinned FIXED, and the field routed straight through it.
3. **Severity: info. The harpies hit each other.** In S3, 160 and 161 traded 6 blows, 2 of them damaging (3 and 5). In S7, 161 took 4 from 160. It did not save the Avatar in either run.
4. **Severity: info. The rest point works as a quiet spot, but it is not a heal source.**
   - **The test.** After X2 he walked round the corpses to (5120,3032,112), on the `HARPIE_REST` y band 3008-3070. Standing there 90 s logged no hatch and no hit (`R1-rest-point-90s-quiet`).
   - **Healing.** hp went 22 → 30 between the end of X2 and the rest test, over several minutes of walking and console work. I did not time it. The rate is the global `HealProcess` one: 1 hp per 1800 frames, wherever he stands (`heal_process.cpp:48-66`). Leg 5 measured it at 1 hp a minute on Map 17. The rest point does not change it.
   - **What it means for a 2-hp winner like S2.** He needs about half an hour idle there before the summit pair (28 hp at about 1 hp a minute). Nothing stops him doing so.

## Harness anomalies

1. **Hatch-moment read raced the hatch once.** In X1, the read right after the walk returned no harpies, and the next read 0.2 s later listed both. The table uses the first read that had them.
2. **The first press after a console close was dropped**, as on 10-17. S1's W leg was lost this way; see the caveat above. `prime()` before each press fixed the later runs.
3. **4 `Cycle in paint` lines (`574 -> 1`) on Map 9 during the sword drag**, with the Avatar at (13850,14262) next to shape 574 frame 146 at (13824,14336,0), beside Galjeron. It happened on a teleport-only visit. It is not part of this test, and it is noted for the Map 9 owner. The run logs themselves have 0.
4. **Log hygiene across all 12 logs** (10,872 lines): 0 each of `stuck in process loop`, Segmentation, Assertion, `Unhandled intrinsic`, ERROR, `Non-existent process` and `failed to set stats`.

## Checkpoints (new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `harpie1018-s13b-armed-sword-hp30.sav` | `144849c3` | Map 13 (5232,4880,80), hp 30, sword 420 equipped, w 90. Every other item and flag is as in s13b. Built with the fetch teleports above |
| `harpie1018-s13b-armed-axe-hp30.sav` | `0fad5625` | Map 13 (5232,4880,80), hp 30, axe 419 equipped, no sword, w 110. Same provenance |

**Repro.** Load either bank. Walk W about 200, then N about 300 into the trigger. Press `c`, then double left-click toward each harpie.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-18-armed-harpie-pair/` (27 plates):
  - `A0-s13b-stats-paperdoll`;
  - `B1`-`B2` (the sword) and `C1`-`C2` (the axe);
  - `S1`-`S7` and `X1`-`X3`, each `-hatch` and `-end`;
  - `F2-corpses-block-centre-lane` and `R1-rest-point-90s-quiet`.
- **Wrote** the two `harpie1018-*` banks in `~/lv-checkpoints/`.
- **Scratch:** `/tmp/claude-1000/harpie1018/` (saves, logs, frames, `runs.json`, trace).
- **Stopped:** my ScummVM and Xvfb `:95`.
- **Not touched:** source, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, the replay's `game/`, `saves/` and `py/`, and every `replay1017-*` bank. The game copy's hashes were re-checked at the end: all OK.
