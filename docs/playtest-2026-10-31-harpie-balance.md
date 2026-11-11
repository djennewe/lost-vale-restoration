# Harpie balance after the stat cut: in-engine measurement (2026-10-31)

This measures the uncommitted `u8monsters.ini [harpie]` change from `agents/map-populator/src/lv_monsters.py`. The new row is hp 22-32 (was 30-45), damage 3-7 (was 5-10) and armour 8 (was 11). Dex 8-12 and defense 0 are unchanged. One row serves all four Map 13 waves, and each wave is one harpie. The Avatar is the same new-game one used on 10-24 and 10-30: STR 15, DEX 15, 30 hp, no armour. The fight loop is the reach-aware v3 from `docs/playtest-2026-10-30-zombie-balance.md`. It never blocks, retreats, drinks a potion or rests.

**Verdict: fair now as a fight, on the easy side.** The cut did not fix what killed the Avatar in 10-30 F1:

- **New row, fought.** He won all 14 armed fights and lost 3.5 hp per fight on average (worst 12). The full four-harpie climb, with no rest, cost him 5 hp. One unarmed run against a lane harpie was also won, 30 → 27.
- **Old row, same driver (control).** Fought at the summit with the axe, the old row lost 6 of 6, and he finished on 30, 30, 30, 25, 11 and 23. Standing and fighting already won at the summit before the cut.
- **Running past is still deadly.** Three dashes from the turn to teleporter 209 that never swung (new row): two died, and one arrived on Map 17 at 5 hp. F1's three deaths were one fight started at 18 hp and two runs to 209. The run-past mode is unchanged by the cut. **[INFERENCE]** Stats alone will not fix it, because the harpie ends up in the neck the route has to pass through.

## Verdicts

| Claim | Verdict | Evidence |
|---|---|---|
| **B1** Hatched harpies carry the new row | **PASS, 15 of 15 hatches** | Hatch reads (`findShape 873`) gave hp **23-32** (mean 26.4), dex 8-12, `ac: 8` on every new-row harpie. Every logged harpie blow had a pre-armour `dmg` of **3-7** (73 blows, dashes included). Control hatches on the old row read hp 34-45 and `ac: 11`, with blows of 5-10 |
| **B2** Summit harpie (group 2), axe ×4 | **4 of 4 won** | He ended on 18, 30, 21 and 30 hp |
| **B3** Summit harpie, sword ×3 | **3 of 3 won** | He ended on 19, 30 and 24 hp |
| **B4** Top harpie (group 4), axe ×3 | **3 of 3 won** | He ended on 24, 30 and 30 hp |
| **B5** Full climb, axe, four harpies in order, no rest | **Won** | His hp went 30 → **30** → **30** → **30** → **25**, after H1, H2, H3 and the summit harpie |
| **B6** Unarmed against one lane harpie (group 3) | **Won (recorded)** | He went 30 → **27**. Fists (`type=1`) did 1-6 per blow, 7 damaging of 10 connecting |
| **B7** Every hatch was walked into | **PASS** | Each run log holds exactly one `event 7 @ 0481` per wave, from that wave's trigger: 21196 summit, 29011 top, 29181 lane, 28753 first lane. The sword and unarmed saves use other ids (2038, 1530). CL1 holds four, in order. Each was fired by a walk: about 260-300 units for the single-wave runs, 680-760 to the first lane trigger, and 900-1,500 between CL1's waves. Inside a run, the logs hold 0 `Cheats =` lines, and the only `MainActor::teleport` is pad 209's own (DN1) |
| **B8** Control: old row, same driver, summit, axe ×6 | **6 of 6 won** | He ended on 30, 30, 30, 25, 11 and 23 hp. This is not part of the brief. It is here so the comparison does not depend on the driver |
| **B9** Run past without fighting (new row) ×3 | **1 of 3 reached 209** | DN1 arrived on Map 17 at 5 hp. DN2 and DN3 died. The harpie landed 19 damaging blows of 40 connecting on a fleeing Avatar |

## Run table

- **Hatched hp** is the hatch read.
- **hp** is the Avatar's start → end.
- **Wall time** runs from combat on (just after the hatch read) to the last read. It includes the paused console reads.
- **Live time** subtracts the reads. It is approximate (harness anomaly 3), and SAX1 predates the live-time counter.
- **Landed** and **taken** are logged `received hit` lines, damaging / connecting (sum of logged `Damage:`). The sums are not capped at the target's remaining hp, as on 10-30.

| Run | Weapon | Wave (trigger) | Hatched hp | hp start → end | Outcome | Wall / live | Landed | Taken |
|---|---|---|---|---|---|---|---|---|
| SAX1 | axe | summit (4863,1663) | 25 | 30 → **18** | **killed** | 30.2 s / – | 3/5 (39) | 2/3 (13) |
| SAX2 | axe | summit | 25 | 30 → **30** | **killed** | 19.7 / 8.8 s | 2/3 (26) | 0/1 (0) |
| SAX3 | axe | summit | 24 | 30 → **21** | **killed** | 21.9 / 8.6 s | 2/2 (24) | 2/2 (9) |
| SAX4 | axe | summit | 27 | 30 → **30** | **killed** | 22.1 / 8.8 s | 3/5 (33) | 0/1 (0) |
| SSW1 | sword | summit | 30 | 30 → **19** | **killed** | 43.4 / 13.2 s | 4/6 (41) | 3/6 (12) |
| SSW2 | sword | summit | 27 | 30 → **30** | **killed** | 28.8 / 7.3 s | 3/3 (29) | 0/3 (0) |
| SSW3 | sword | summit | 28 | 30 → **24** | **killed** | 34.2 / 13.9 s | 4/9 (28) | 1/2 (6) |
| TAX1 | axe | top (5119,2687) | 30 | 30 → **24** | **killed** | 18.3 / 5.7 s | 2/2 (31) | 1/1 (6) |
| TAX2 | axe | top | 32 | 30 → **30** | **killed** | 16.8 / 7.5 s | 4/4 (39) | 0/2 (0) |
| TAX3 | axe | top | 24 | 30 → **30** | **killed** | 15.0 / 3.0 s | 2/3 (24) | 0/1 (0) |
| CL1-H1 | axe | first lane (5119,6143) | 26 | 30 → **30** | **killed** | 16.6 / 7.4 s | 3/5 (32) | 0/1 (0) |
| CL1-H2 | axe | lane (5119,4479) | 28 | 30 → **30** | **killed** | 18.7 / 5.9 s | 2/3 (30) | 0/1 (0) |
| CL1-H3 | axe | top | 24 | 30 → **30** | **killed** | 13.1 / 4.4 s | 2/2 (28) | 0/2 (0) |
| CL1-H4 | axe | summit | 23 | 30 → **25** | **killed** | 102.2 / 35.0 s | 3/6 (30) | 1/4 (5) |
| UN1 | none | first lane | 23 | 30 → **27** | **killed** | 28.5 / 12.0 s | 7/10 (25) | 1/3 (4) |

In CL1 the hp between fights equals the hp after the last one, because nothing was rested. CL1-H4 is long because that harpie loitered at its egg for about 20 s of live time (finding 4).

### Control and dash runs

| Run | Row | What | Hatched hp | hp start → end | Outcome | Wall / live | Landed | Taken |
|---|---|---|---|---|---|---|---|---|
| CTL1 | old | summit, axe, fought | 45 | 30 → **30** | **killed** | 34.6 / 8.9 s | 4/4 (46) | 0/3 (0) |
| CTL2 | old | summit, axe, fought | 34 | 30 → **30** | **killed** | 23.9 / 7.4 s | 3/3 (42) | 0/1 (0) |
| CTL3 | old | summit, axe, fought | 37 | 30 → **30** | **killed** | 28.6 / 12.2 s | 5/9 (49) | 0/3 (0) |
| CTL4 | old | summit, axe, fought | 34 | 30 → **25** | **killed** | 51.8 / 17.1 s | 5/6 (44) | 1/4 (5) |
| CTL5 | old | summit, axe, fought | 42 | 30 → **11** | **killed** | 45.4 / 17.1 s | 5/12 (48) | 2/5 (19) |
| CTL6 | old | summit, axe, fought | 37 | 30 → **23** | **killed** | 30.2 / 10.6 s | 4/7 (40) | 1/3 (8) |
| DN1 | new | turn → 209, axe, no swings | 23 | 30 → **5** | **arrived Map 17** (4608,9984,0) | 85.7 / 27.9 s | 0/0 | 5/10 (26) |
| DN2 | new | turn → 209, axe, no swings | 26 | 30 → **0** | **died** at (4424,1472) | 70.9 / 21.1 s | 0/0 | 7/14 (31) |
| DN3 | new | turn → 209, axe, no swings | 24 | 30 → **0** | **died** | 65.7 / 26.6 s | 0/0 | 7/16 (36) |

### Win rates

| Case | New row (10-31) | Winners' final hp |
|---|---|---|
| Summit, axe | **4 of 4** | 18, 30, 21, 30 (mean 24.8) |
| Summit, sword | **3 of 3** | 19, 30, 24 (mean 24.3) |
| Top, axe | **3 of 3** | 24, 30, 30 (mean 28.0) |
| Full climb, axe (4 fights) | **1 of 1** (4 of 4 fights) | 30, 30, 30, 25 |
| Armed fights, all | **14 of 14** | mean 26.5; mean loss per fight 3.5 hp |
| Unarmed, first lane | 1 of 1 | 27 |
| *Control: summit, axe, old row* | *6 of 6* | *30, 30, 30, 25, 11, 23 (mean 24.8)* |
| *Run past to 209, new row* | *1 of 3 arrived* | *5* |

Pooled blows, new row, armed fights:

- **The Avatar's blows.** 39 of 58 connecting blows did damage. After armour 8, the axe did 7-17 per blow (pre-armour 9-23) and the sword 6-15 (pre-armour 8-21). Each kill took 2-4 damaging blows.
- **The harpies' blows.** 10 of 30 connecting blows did damage, 3-7 each. On a fleeing Avatar (dashes) it was 19 of 40.
- **The control's blows (old row).** The axe did 6-15 after armour 11 (26 of 41 damaging). The harpie's blows did damage 4 times in 19 connecting, for 5, 8, 9 and 10.

### Small samples

- **Losses.** No new-row armed fight was lost, but there were only 14. A 0-in-14 loss count is still consistent with a true loss rate of up to about 19% per fight (95% upper bound).
- **New vs old at the summit.** The new and old rows are not separable at the summit with this sample. Mean loss was 5.3 hp with the axe on the new row (4 runs) and 5.2 on the old (6 runs). What the cut changed, measurably, is the per-blow numbers: hp at hatch fell from 34-45 to 23-32, and a harpie blow from 5-10 to 3-7.

## Comparison with earlier numbers

| | 10-24 (old row, v2 driver, lane harpies) | 10-30 F1 (old row, hand/scripted play) | 10-31 (new row, v3 driver) | 10-31 control (old row, v3 driver) |
|---|---|---|---|---|
| Harpie hp at hatch | 31-45, mean 38 (30 hatches) | – | 23-32, mean 26.4 (15) | 34-45, mean 38.2 (6) |
| Harpie blow | 5-10; 20 damaging of 42 connecting | – | 3-7; 10 of 30 (fought), 19 of 40 (fled) | 5-10; 4 of 19 |
| Armed single-harpie fights won | 13 of 15 (two deaths, SW5 at H1 and SW3 at H2 from 1 hp) | lane: 1 won, 1 lost (from 21); summit fight: lost from 18 | **14 of 14** | **6 of 6** (summit) |
| Summit | (then a pair; not run) | 3 of 3 lost: one fight from 18, two runs to 209 | 7 of 7 fought; run past 1 of 3 | 6 of 6 fought |

Caveats:

- **Different drivers.**
  - **10-24.** The v2 loop swung at box gap 40 or less. On 10-30 that rule stalled once (that report's anomaly 2), and v3 replaced it.
  - **10-30 F1.** Those were not driver fights. Two of the three summit deaths were runs to 209.
- **The control removes the driver difference for the summit.** Under v3, the old row and the new row both lose to an Avatar who stands and swings.

## Build pinned

- **Copy.** `shared/u8-lv-patched` and `scummvm-lv-console/scummvm` were copied once to `/tmp/claude-1000/harpie1031/` (`game/`, `bin/scummvm-console`). The ini is the 10-30 one: 320×200, `scale_factor=2`, `usehighres=true`.
- **The copy's `[harpie]` row** reads `hp_min=22 hp_max=32 dex_min=8 dex_max=12 damage_min=3 damage_max=7 armour=8`, with `defense_type=0x0000`.
- **Hashes.** `sha256sum -c pinned.sha256` was OK for all eight files at the end:
  - FIXED.DAT `fc92ee5f…` (top level and `STATIC/`), EUSECODE `b47c324c…`, U8SHAPES `2b274856…`, TYPEFLAG `e25d7224…`, ANIM `97ae5fc9…`;
  - these five equal `shared/build/ARTIFACTS.sha256`;
  - `u8monsters.ini` `fda1bef8…`;
  - binary `e0518ced…`, today's `scummvm-lv-console/scummvm`. It is **not** the `d371f7ce…` binary of 10-18, 10-24 and 10-30 (harness anomaly 1).
- **Control copy.** `game_old/` is a hard-link copy of `game/` with only `u8monsters.ini` replaced: its `[harpie]` row is `hp 30-45, damage 5-10, armour 11`, and every other line is unchanged. Its ini hash is `0642d689…`, the same file as the 10-30 pin. The control runs (CTL1-CTL6) are the only ones that used it.
- **Display.** Xvfb `:95`, driven by the replay's `lv.py` through this session's `py/hdrv.py`.

## Setup

**Banks.** Each 10-24 bank was loaded, then:

1. Cheats on, teleport to Map 9 (13850,14230,0), teleport to Map 13, cheats off. The hop reloads Map 13 from the pinned FIXED.
2. A mobility check (E/W, or S/N at the summit), a teleport back to the spot if the check moved him, then a bank.

After every hop, `findShape 500/73` listed all four harpie eggs and the five shape-73 eggs, every one `hatched=0`:

- eggs (5183,5631,76), (5183,3967,96), (5183,2175,120) and (4287,2175,120);
- triggers (5119,6143,76) range 6,2; (5119,4479,84) 6,2; (5119,2687,120) 6,2; and (4863,1663,120) range 1,6;
- plus Map 13's arrival egg (4096,11264,0).

No `event 7` was logged during setup.

| Bank (`~/lv-checkpoints/`) | md5 | State |
|---|---|---|
| `harpie1031-m13-south-axe-hp30.sav` | `03e2c502` | (5067,6979,72), hp 30, axe, weight 110 |
| `harpie1031-m13-rest-axe-hp30.sav` | `ed6831b2` | (5087,3039,112), the rest point, hp 30, axe |
| `harpie1031-m13-summit-east-axe-hp30.sav` | `f2f372db` | (5200,1728,120), the turn, hp 30, axe |
| `harpie1031-m13-summit-east-sword-hp30.sav` | `e8d3fb69` | (5200,1728,120), hp 30, sword, weight 90 |
| `harpie1031-m13-south-unarmed-hp30.sav` | `3ef216b5` | (4963,6851,72), hp 30, unarmed, weight 60 |

The turn spot lies outside every trigger box. The summit strip's box covers x 4831-4926; the top trigger's covers y 2623-2750. The hit types confirm the weapon in every run: axe `type=6`, sword `type=2`, fists `type=1`.

**Each run:**

1. Stop ScummVM, copy the bank to slot 1, and relaunch with `--save-slot=1`.
2. Enable `Object` and `Actor`.
3. Walk in 0.8 s presses (110 px, steered by the world vector) until a new live harpie is listed. The routes:
   - summit: W from x 5200 (hatch read at x 4904-4944);
   - top: N from y 3039 (hatch read at y 2735-2775);
   - first lane: N from y 6851-6979 (hatch read at y 6171-6219).
4. Press `c`, then fight until the harpie or the Avatar reads hp 0.
5. In CL1 only: press `c` again and walk on to the next trigger. The summit leg went via (5180,1760) at the turn.

**Dashes (DN1-DN3).** These were held run-gait presses (200 px, 1.0 s). They went W to x 4355, then S toward 209's box at (4351,2303), with no combat mode and no swings. They sidestepped after two stalled reads.

### The fight driver (v3, kept on disk this time)

The v3 loop from 10-30, rebuilt from that report's prose because its source again lived only in an eval kernel. It is now at `/tmp/claude-1000/harpie1031/py/hdrv.py`.

- **Read.** Each cycle reads `findShape 873` and `objectInfo 1` in one console attach. The world is paused while the console is attached.
- **When to swing.** If the Avatar's 64×64 box, shifted 32 units in one of the 8 directions, overlaps the harpie's 128×128 box (both anchored at the max corner), he double-clicks twice, 0.7 s apart. The direction picked is the overlapping one nearest the harpie's centre.
- **Otherwise.** He takes a 0.45 s advance toward it and swings once. After two reads with no movement, he sidesteps perpendicular.
- **Attach.** It releases both mouse buttons, polls every 50 ms and retries up to 8 times. No `ATTACH FAILED` occurred.

He never blocks, retreats, drinks a potion or rests.

### Console commands used (whole session)

- `debugflag_enable Object` and `debugflag_enable Actor`, after each of the 24 starts (3 setup, 21 runs). Every log holds `Enabled debug flag 'Object'`.
- Reads:
  - `ObjectManager::objectInfo 1` and `ObjectManager::findShape 873`, every driver cycle;
  - `ObjectManager::findShape 500` and `73`, 4 times at setup.
- `Cheat::toggle` 22 times, on and off around each setup teleport. The logs hold 11 `Cheats = true` and 11 `Cheats = false`, all in `lv_setup_*.log`. Every run log holds 0 of each.
- `MainActor::teleport` 11 times, all during setup:
  - `9 13850 14230 0` ×3;
  - `13 5119 6911 72` ×2;
  - `13 5087 3039 112` ×2;
  - `13 5200 1728 120` ×4.
- `Ultima8Engine::saveGame` 5 times, for the banks.
- **Not used:**
  - `loadGame`: reloads were restarts with `--save-slot`;
  - `MainActor::toggleCombat`: combat used the real `c` key;
  - invincibility, heal, item cheats, `Item::grab` and `setGlobal`.

  A grep of every log for `invincib|Cheat::heal|Cheat::items|setGlobal|Item::grab|loadGame|toggleCombat` found nothing.

The text console does not echo commands into the log. The teleport and save counts therefore come from the driver calls (`trace.txt` holds the `BANK` lines), and the cheat counts from the logged `Cheats =` lines.

## Findings

1. **Severity: info (balance). Fought, the harpie is no longer a threat to a 30-hp armed Avatar.**
   - **Results.** 14 of 14 armed fights were won, with a mean loss of 3.5 hp and a worst of 12 (SAX1). The four-harpie climb cost 5 hp. Fists beat a lane harpie, 30 → 27.
   - **The yardstick.** On 10-30 a single water zombie (wave 2) cost the armed Avatar 0-2 hp, and that report called the zombie fair. So a single harpie now sits close to a single zombie.
   - **How to read it.** Whether that is right for the climb's last guardian is a design call. The new row is clearly not too strong for a player who fights.
2. **Severity: medium (balance, for the `lv_monsters.py` / `build_map_13` owner). The stand-and-fight summit fight was already winnable on the old row, so the cut is not what F1 needed.**
   - **The control.** With the same driver at the same spot, the old row lost 6 of 6. He ended on 30, 30, 30, 25, 11 and 23, a mean loss of 5.2 hp, against 5.3 on the new row with the axe.
   - **What F1 recorded.** Of the three 10-30 summit deaths, one was a fight started at 18 hp. The other two were runs to 209 that were stun-locked at y 2044.
   - **The new code comment.** The new `lv_monsters.py` docstring says "each talon interrupts his run, so he cannot break off". That is the run-past mode, and B9 shows it survives the cut.
3. **Severity: medium (route, for the `build_map_13` owner). Running past the summit harpie still kills 2 of 3 times.**
   - **The dashes.** All three hatched it and then ran for 209. DN2 and DN3 died; DN1 arrived at 5 hp. Fleeing, he took 19 damaging blows of 40 connecting (48%), against 10 of 30 (33%) when he stood and fought.
   - **Where it stood.** In DN2 the harpie held (4479,1799) → (4543,1727) for most of the run. Its 128×128 body covers the plateau's east edge, at the neck the route to 209 must pass. The Avatar's sidesteps took him north (y 1472-1664) instead of past it.
   - **Known for corpses.** `build_map_13.py:433-438` records that a summit harpie's corpse in the neck can close the walk to 209. [INFERENCE] A live harpie standing there does the same, and no stat row changes that.
   - **Caveat.** The dash loop is crude (harness anomaly 4). A human could weave better. The deaths were still combat deaths with damaging blows logged (`DN2-end`).
4. **Severity: low. The summit harpie sometimes loiters after hatching.**
   - **What happened.** In CL1-H4 the trigger fired with the Avatar at (4871,1791). The harpie stayed at its egg, (4287,2175) → (4287,2303) → (4279,2175), for about 20 s of live time. It came at him only once he had closed to x ≈ 4580.
   - **The other runs.** In every other summit run it closed within a few seconds. The Avatar there stood at y 1728, not 1791.
   - **Seek square.** By `lv_monster_eggs.seek_square` (range 768), both spots lie inside the egg's seek square. The cause is not established.
5. **Severity: info. No lane respawn and no new hatch problems.** Every walked trigger fired once and hatched exactly one harpie. In CL1, after each kill nothing else was alive until the next trigger.

## Harness anomalies

1. **The binary changed since 10-30.** `scummvm-lv-console/scummvm` hashes `e0518ced…`, not the `d371f7ce…` pinned on 10-18, 10-24 and 10-30. It was pinned as found. The fork's change log was not checked, so a combat-relevant engine change between the binaries cannot be ruled out. The control (old row, this binary) is the comparison that holds the binary fixed.
2. **The v3 loop was lost again.** The 10-30 loop lived in an eval kernel, so it was rebuilt from that report's prose. The source is now kept at `py/hdrv.py`.
3. **Time.**
   - **Cycle length.** One driver cycle took about 3 s of wall time, against about 1.9 s on 10-24, because each read costs a console attach.
   - **Live time.** It subtracts the read time. The world keeps running for part of each attach (the chord until `Debugger entered`) and for 0.6 s after `exit`, so live time slightly undercounts.
   - **SAX1.** It ran before the live-time counter was added.
4. **The dash loop is crude.**
   - **Overshoot.** The held run gait overshoots. In DN1 he ran from x 4248 back east to x 4920 when the waypoint lay at x 4355.
   - **Sidesteps.** The two-stall sidestep sent DN2 north, away from 209.
   - **What it shows.** The dashes show the hazard. They are not a skilled run past.
5. **Short presses after a turn often moved him 0** during the mobility checks (the turn takes them), as on 10-24 anomaly 3. Each check was repeated, or followed by a teleport back to the bank spot.
6. **Output order.** `findShape` prints its item lines after the following `objectInfo` reply. The read parses the whole reply, so this cost nothing.

## Log hygiene

The 21 run logs and 3 setup logs hold 0 of each of these:

- `Cycle in paint`, `Assertion`, `Segmentation` and `stuck in process loop`;
- `Unhandled intrinsic`, `ERROR`, `Non-existent process` and `failed to set stats`.

DN1 holds `MainActor::teleport(): teleporting to map 17, egg 209`, `Unloading map 13`, `Loading Fixed items in map 17` and `event 7 @ 05B2`. That is the pad's own teleport, not a console command.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-31-harpie-balance/` (51 plates):
  - `<run>-hatch` and `<run>-end` for SAX1-4, SSW1-3, TAX1-3, UN1 and CTL1-6;
  - `CL1-H1`…`CL1-H4`, each `-hatch` and `-end`;
  - `DN1-end`, `DN2-end` and `DN3-end`;
  - `setup-00`…`setup-05`.
- **Wrote** the five `harpie1031-m13-*` banks in `~/lv-checkpoints/`. Nothing was overwritten.
- **Scratch** is `/tmp/claude-1000/harpie1031/`. It holds:
  - the pinned `game/` and `bin/`, `pinned.sha256` and the control `game_old/`;
  - `saves/`, the logs `lv_*.log` and `runs.json` (per-run reads, hits and hatch reads);
  - `trace.txt`, the frames in `sp/`, and `py/` (`lv.py` and `hdrv.py`).
- **Stopped** my ScummVM and Xvfb `:95`.
- **Not touched:**
  - source, including the uncommitted `lv_monsters.py`, maps, the fork, `shared/` and `TODO.md`;
  - the older scratch dirs and every older bank.
- **No** rebuilds and no commits.
