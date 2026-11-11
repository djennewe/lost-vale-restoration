# Map 13 lane harpies one at a time: in-engine check and re-measured fight (2026-10-24)

This checks the uncommitted `build_map_13.py` `build_harpies()` change: a new group-3 trigger at (5119,6143,76) hatches one harpie at (5183,5631,76), and the y-4479 trigger now hatches one harpie at (5183,3967,96) instead of a pair. The fights were re-measured with the scripted loop described in `docs/playtest-2026-10-18-armed-harpie-pair.md`. The Avatar is the same new-game one as on 10-18: STR 15, DEX 15, 30 hp, no armour.

## Verdicts

| Claim | Verdict | Evidence |
|---|---|---|
| **C1** The first trigger hatches exactly one harpie, and it fights on the flat stretch | **PASS, 17 of 17 runs** | Each run logged one `Item: 27280 (shape 73) calling usecode event 7 @ 0481:0080` (1251 in the axe save, 31423 in the unarmed one). At the first read, `findShape 873` listed **one** harpie, id 160, at (5183,5631,76); in S7 and UN1 it had already drifted to y 5685 and 5676. Across all 17 first fights the harpie read **z 76 at every read** and y 5633-6227. The Avatar stood at z 72-76, y 5745-6319 |
| **C2** The second harpie does not hatch until the Avatar walks into the y-4479 trigger, and exactly one hatches there | **PASS, 14 of 14 walk-ons** | **At most one live harpie at every read of every run.** Between the fights, `findShape 873` listed only 160's corpse. In the 13 walk-ons the driver recorded (all but S2, whose hatch came during my probe walk), the last read before the second hatch had him at y 4599-5443 with no 161. 161 first appeared once he was at y 4339-4571 (4059 in S3, which overshot), with one `event 7 @ 0481` from trigger 15148 (964 in the axe save, 25030 in the unarmed one), logged after the first fight ended. After both hatches, `findShape 500` listed only the two summit eggs |
| **C3** Armed fights, 5 sword and 3 axe runs | **DONE (measured): sword 3 of 5, axe 3 of 3, armed 6 of 8** | See the run table. On 10-18 the pair gave 3 of 7, 2 of 3 and 5 of 10. Both armed deaths were by one harpie alone. In SW5 the first harpie killed a 30-hp Avatar in 17.7 s with 4 blows in a row, all damaging (31). In SW3 he went into the second fight at **1 hp**, because the driver never rests |
| **C4** No regression | **PASS** | **Rest point:** about 99 s at (5067,3083,112) gave 0 `event 7` and 0 `received hit` (`R1-*`). That spot is 20 W and 44 S of `HARPIE_REST` (5087,3039), and his 64-deep box overlaps its y band. It was tested once, in UN1 after both lane kills. **Summit:** walking in fired trigger 17491 once and hatched **two** harpies, 162 and 163 (`C4-summit-pair-hatch`). **Logs:** 0 `Cycle in paint` in all 21 logs, with `Enabled debug flag 'Object'` in every run log after its load. Also 0 each of `Assertion`, `Segmentation`, `stuck in process loop`, `Unhandled intrinsic`, `ERROR`, `Non-existent process` and `failed to set stats` |
| **C5** One unarmed run, for contrast | **PASS (recorded)** | UN1 **won**, 30 → 24 → 17. Fists did 1-5 per blow (`type=1`), and 25 of his 34 connecting blows did damage. The harpies landed only 2 damaging blows in 7. That is one run, and the harpies' rolls decided it |

## Build pinned

- **Copy.** `shared/u8-lv-patched` and `scummvm-lv-console/scummvm` were copied once to `/tmp/claude-1000/harpie1024/` (`game/`, `bin/scummvm-console`). The ini is the 10-18 one: 320×200, `scale_factor=2`, `usehighres=true`.
- **Hashes.** `sha256sum -c pinned.sha256` gave OK for all eight pinned files at the start and at the end:
  - FIXED.DAT `1a9ce209…` (top level and `STATIC/`);
  - EUSECODE `2e3b71c2…`, U8SHAPES `efb16af1…`, TYPEFLAG `d26d1531…`, ANIM `696dbeb9…`;
  - `u8monsters.ini` `7f666fe9…`;
  - binary `d371f7ce…`, the same binary as 10-18.
- **Display.** Xvfb `:95`, driven by the replay's `lv.py` with its paths pointed at the scratch dir.
- **Not run.** The verifier's "always" checks (`run_all_tests.sh`, `build_artifacts.sh`). The brief said no rebuilds, and Main reports `test_monster_eggs.py` at 428/428.

## Setup

The three banks were built the same way:

1. Load the 10-18 save.
2. Hop to Map 9 and back to Map 13 at the climb's south end (5119,6911,72), so that the map reloads from the new FIXED.
3. Read the eggs.
4. Run a mobility check, then bank.

After each hop, `findShape 500/73` listed:

- trigger 27280 (5119,6143,76) with range 6,2, and harpie egg 27278 at (5183,5631,76);
- trigger 15148 (5119,4479,84), and egg 8371 at (5183,3967,96). **The old west egg (5023,3999) is gone;**
- the summit trigger (4863,1663,120) and its eggs (4287,2175) and (4287,2047).

Before the hop, the old save itself still listed the old pair at (5023,3999) and (5183,3967), and no y-6143 trigger.

| Bank (`~/lv-checkpoints/`) | md5 | State |
|---|---|---|
| `harpie1024-m13-south-sword-hp30.sav` | `2d5dc63d` | (5119,6911,72), hp 30, sword, weight 90 |
| `harpie1024-m13-south-axe-hp30.sav` | `b254ef80` | (5143,6943,72), hp 30, axe, weight 110. The mobility check left him 40 units off the sword spot |
| `harpie1024-m13-south-unarmed-hp30.sav` | `2efcbb31` | (5119,6911,72), hp 30, unarmed (from `replay1017-s13b`), weight 60 |

**Each run** worked like this:

1. Stop ScummVM, copy the bank to slot 1, and relaunch with `--save-slot=1`.
2. Enable `Object` and `Actor`.
3. Walk north about 700-770 units into trigger 1, then press `c` and fight.
4. Press `c` again and walk north about 1,600-1,900 units into trigger 2, then press `c` and fight.

Every trigger was a walked arrival. No teleport was used inside a run.

### Console commands used (whole session)

- `debugflag_enable Object` and `debugflag_enable Actor`, after every start.
- Reads: `ObjectManager::objectInfo 1`, and `ObjectManager::findShape 873`, `500` and `73`.
- `Cheat::toggle` 6 times: on and off around each of the 3 setup hops. The logs hold exactly 3 `Cheats = true` and 3 `Cheats = false`, all in `lv_setup*.log`. Cheats were off for every fight.
- `MainActor::teleport` 6 times, all during setup: `9 13850 14230 0`, then `13 5119 6911 72`, once per bank.
- `Ultima8Engine::saveGame` 3 times, for the banks.
- **Not used:** `loadGame` (reloads were restarts), `MainActor::toggleCombat` (combat used the real `c` key), invincibility, heal, `Cheat::items` and setGlobal. A grep of every log for `invincib|Cheat::heal|Cheat::items|setGlobal` found nothing.

### The fight driver

The 10-18 loop's source was not on disk. Only its prose and `runs.json` survived, so I rebuilt **v2** from the prose. Each cycle reads `findShape 873` plus `objectInfo 1`. It then measures the box gap: the harpie is 128×128 with its anchor at the max corner, and the Avatar is 64×64.

- If the gap is 40 or less, it double-clicks twice, 0.7 s apart.
- Otherwise it takes a 0.45 s advance toward the harpie and swings once.
- A short prime press goes before each action, because the first input after a console close is often lost.

It never blocks, retreats, drinks a potion or rests. One cycle took about 1.9 s, the same as 10-18's records. The read writes its commands and `exit` in one batch, so it costs no live time: the world is paused while the console is attached.

**Driver revision (see harness anomaly 2).** S1-S8 aimed by screen projection measured from the mover origin. That skewed every advance toward world north, so they are **pilot runs**, kept out of the tally. SW1-SW5, AX1-AX3 and UN1 aim from the world vector.

## Runs (corrected driver, the tally)

**hp** is the Avatar's hp at the start → after the first harpie → after the second. **Landed** and **taken** count logged `received hit` lines, as damaging / connecting (total damage). The time is from the hatch to the last read of that fight.

| Run | Weapon | Hatched hp (H1 / H2) | hp start → after H1 → after H2 | Outcome | H1 time | H2 time | H1 landed / taken | H2 landed / taken |
|---|---|---|---|---|---|---|---|---|
| SW1 | sword | 43 / 33 | 30 → **24** → **19** | **both killed** | 31.9 s | 21.9 s | 8/20 (43) / 1/6 (7) | 5/8 (37) / 1/4 (5) |
| SW2 | sword | 41 / 31 | 30 → **12** → **12** | **both killed** | 25.6 s | 15.8 s | 6/8 (41) / 2/3 (18) | 4/7 (35) / 0/2 (0) |
| SW3 | sword | 44 / 35 | 30 → **1** → **0** | **died to H2** (161 at 21) | 36.0 s | 11.3 s | 10/14 (47) / 3/7 (29) | 2/3 (14) / 1/2 (6) |
| SW4 | sword | 42 / 43 | 30 → **30** → **22** | **both killed** | 15.1 s | 11.3 s | 4/4 (42) / 0/1 (0) | 6/6 (45) / 1/2 (8) |
| SW5 | sword | 34 / – | 30 → **0** | **died to H1** (160 at 22) | 17.7 s | – | 2/4 (12) / 4/4 (31) | – |
| AX1 | axe | 34 / 33 | 30 → **16** → **16** | **both killed** | 17.0 s | 9.7 s | 3/4 (40) / 2/2 (14) | 5/8 (41) / 0/2 (0) |
| AX2 | axe | 34 / 40 | 30 → **15** → **16** | **both killed** | 28.1 s | 17.0 s | 7/9 (40) / 2/3 (15) | 6/9 (41) / 0/1 (0) |
| AX3 | axe | 37 / 37 | 30 → **30** → **12** | **both killed** | 15.5 s | 22.5 s | 5/6 (39) / 0/0 (0) | 5/8 (38) / 3/3 (19) |
| UN1 | none | 37 / 45 | 30 → **24** → **17** | **both killed** | 30.7 s | 34.7 s | 12/17 (40) / 1/3 (6) | 13/17 (47) / 1/4 (8) |

- **hp between the fights** equals hp after H1. The walk to trigger 2 took 15-30 s, and the global heal is about 1 hp a minute. AX2 gained 1.
- **Per-blow damage.** The Avatar's sword landed 47 damaging blows of 74 connecting, and the axe 31 of 44. The harpies' blows on him did **5-10**: 20 damaging of 42 connecting, armed runs only. "Damage" totals are capped by the target's remaining hp, so a killing blow can read as low as 1.
- **The 30 hatches** (pilot included) read hp 31-45, mean 38.

### Pilot runs (first driver, excluded from the tally)

| Run | Weapon | hp start → after H1 → after H2 | Outcome | Why it is excluded or qualified |
|---|---|---|---|---|
| S1 | sword | 30 → 30 → 0 | H1 killed. Died to H2 (161 at 21) | Skewed aim. During H2, two `ATTACH FAILED` left the driver blind for 36 s. **H2 invalid** |
| S2 | sword | 30 → 15 → (19) → 0 | H1 killed | Skewed aim. My own probe walk entered trigger 2, and the Avatar then stood idle in a timing test while 161 killed him. **H2 not a fight** |
| S3 | sword | 30 → 23 → 0 | Died to H2 (161 at 37) | Skewed aim. A 1.8 s walk chunk overshot to (5051,4059), 92 from the egg. He then stood at box gap 60 for about 30 s and landed nothing |
| S4 | sword | 30 → 8 → 0 | Died to H2 (161 at 3) | Skewed aim |
| S5 | sword | 30 → 30 → 30 | **Both killed** | Skewed aim |
| S6 | sword | 30 → 0 | Died to H1 (160 at 34) | Skewed aim. He drifted west while it stood east |
| S7 | sword | 30 → 30 → 0 | Died to H2 (161 at 23) | Skewed aim |
| S8 | sword | 30 → 0 | Died to H1 (160 at 20) | Skewed aim. He advanced north while it was east-south-east |

C1 and C2 count the pilot runs, because hatch behaviour does not depend on the aim.

## Comparison with 10-18 (the pair)

| | 10-18: pair at y 4479 | 10-24: one at y 6143, then one at y 4479 |
|---|---|---|
| Sword wins | 3 of 7 | **3 of 5** |
| Axe wins | 2 of 3 | **3 of 3** |
| Armed total | 5 of 10 | **6 of 8** |
| Winners' final hp | 2, 10, 17, 22, 22 (mean 14.6) | 19, 12, 22, 16, 16, 12 (mean 16.2) |
| Armed deaths | 5, all with both harpies up, in 22-78 s | 2, each to **one** harpie: SW5 at H1 from 30 hp, SW3 at H2 from 1 hp |
| Harpies alive at once | both, in every run | never more than one |
| Unarmed | 10-17: killed twice by the pair (not this driver) | 1 of 1 won |

Caveats:

- **Small samples.** The armed difference, 6/8 against 5/10, is within the noise for samples this small.
- **The drivers are not the same code.** My corrected v2 aims from the world vector. I do not know whether the 10-18 v2 had the skew my pilot had.
- **What the pilot shows.** The same staggered layout, fought with the skewed pilot driver, gave 1 of 5 (S4-S8).
- **The design-relevant change is structural.** He now faces 31-45 hp at a time instead of 63-88. Nothing is alive between the first kill and the y-4607 line.

## Findings

1. **Severity: medium (balance, for the `build_map_13` owner). One harpie can still kill a fresh 30-hp armed Avatar.**
   - **The deaths.** SW5 took 4 damaging blows from 4 connecting (31) and died in 17.7 s. The harpie's per-blow damage is 5-10, so 4 damaging blows kill him.
   - **The staggered win rate.** The corrected driver won 6 of 8 armed runs. The pilot also lost two first fights outright (S6, S8).
   - **The real "between".** The stagger now gives one. After the first kill, nothing hatches until the Avatar's box reaches the y-4479 trigger. A player can wait anywhere on the flat stretch and heal at the global 1 hp a minute. The rest point is not needed for this. SW3 died because the driver walked on at 1 hp. A human who waited would not have.
   - **What the data cannot say.** Whether a human who blocks, backs off or drinks would lose at all.
2. **Severity: low. The first harpie's corpse often stalls the walk north.**
   - **How often.** The first fight happens on the lane the player then walks up. The corpse (shape 873, 128×128, solid) stopped the walker's N press in **8 of 14 walk-ons** (S1, S2, S3, S5, SW4, AX1, AX2, AX3). In S1 he stood at (5151,6159) with the corpse at (5147,6083) (`S1-stuck`). In S2 he stood at (5133,5997) with the corpse at (5227,5931) (`S2-stall`).
   - **The way round.** A 1 s W or E sidestep always cleared it.
   - **Same mechanism as before.** This is 10-18 finding 2, moved down the hill.
3. **Severity: info. No respawn on the way back down, though the triggers re-arm.**
   - **The triggers re-arm.** `MONEGG` sets bit 0x80 of the trigger's map array when it hatches, and clears it in its `leaveFastArea` event (`replay1017/monegg.dis` 010D-0119 and 0133-013E). `Egg::leaveFastArea` also resets `_hatched` (`egg.cpp:60-62`). Standing at the rest point, trigger 31423 read `m: 3, hatched=0`, re-armed. The y-4479 trigger 25030 read `m: 129, hatched=1`.
   - **Nothing is left to hatch.** The lane eggs are frame 1, and `MONEGG` destroys an egg whose frame is non-zero after hatching it (`monegg.dis` 00EC-00FB). `findShape 500` listed only the two summit eggs.
   - [INFERENCE] Walking back south re-fires the trigger with nothing to hatch. Not walked.
4. **Severity: info. Corpses are removed when they leave the fast area.** At the rest point, `findShape 873` listed only 161. By y 1611 it listed nothing.

## Harness anomalies

1. **The 10-18 fight loop was not preserved** (it lived in an eval kernel). Only its prose and `runs.json` were on disk, so the loop here is a re-implementation. The loop used here (writes its commands and `exit` in one batch, no live time) is in this session's eval kernel. The per-run records are in `/tmp/claude-1000/harpie1024/runs.json`.
2. **Aim skew in my first rebuild (S1-S8).**
   - **What it did.** It placed the mouse at the harpie's screen projection, lifted 16 for the box centre, and measured the direction from `morigin()`, the screen centre plus 28 px. At typical ranges this rotated the heading toward screen-up, which is world N.
   - **Example.** In S8 the harpie was east-south-east, and each advance moved him 96 north.
   - **The fix.** The heading is the world vector (dx, dy) turned into a screen vector and applied at `morigin()`. It is correct by construction: east gives (0.89, 0.45).
3. **Short right-button presses (0.4-0.6 s) often moved him 0.** The turn takes them, or they are lost after a console close; a clean bench with E/W alternation showed 0 on most presses. The walker therefore uses presses of at least 0.8 s, so trigger entries overshot by up to about 250 units. The second hatch read the Avatar at y 4339-4571, against an egg at 3967.
4. **`ATTACH FAILED` twice in S1's second fight** left 36 s with no input. The replacement attach polls every 50 ms and retries 8 times, releasing the mouse buttons between tries. It did not fail again.
5. **`lv_S5.log` holds two attempts:** the aborted S5x (0.4 s presses, no hatch) and S5. `lv_S1.log` and `lv_S2.log` contain my probe walks. `lv_timing.log` is a press-timing bench on the sword bank.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-24-harpies-one-at-a-time/` (58 plates):
  - `<run>-hatch1`, `-h1end`, `-hatch2` and `-end` for SW1-SW5, AX1-AX3, UN1 and pilot S4-S8;
  - the setup plates `setup-01-m13-south`, `setup-axe` and `setup-unarmed`;
  - `R1-rest-point-start`, `R1-rest-point-90s` and `C4-summit-pair-hatch`;
  - `S1-stuck` and `S2-stall`.
- **Wrote** the three `harpie1024-m13-south-*` banks in `~/lv-checkpoints/`. Nothing was overwritten.
- **Scratch** is `/tmp/claude-1000/harpie1024/`: the pinned `game/` and `bin/`, `pinned.sha256`, `saves/`, the logs `lv_*.log`, `runs.json`, `trace.txt`, the frames in `sp/` and `py/`, a copy of the replay driver.
- **Stopped** my ScummVM and Xvfb `:95`.
- **Not touched:** source, maps, the fork, `shared/`, `TODO.md`, `HANDOFF.md`, the replay and harpie1018 scratch, and every older bank.
