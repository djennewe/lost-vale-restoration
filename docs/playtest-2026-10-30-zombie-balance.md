# Water Zombie balance after the stat cut: in-engine measurement (2026-10-30)

This measures the uncommitted `u8monsters.ini [waterzombie]` change from `agents/map-populator/src/lv_monsters.py`. The new row is hp 25-35 (was 35-50), damage 3-7 (was 6-12), dex 10-12 (was 14-16) and armour 8 (was 15). The defense type is unchanged. The fights were run on the Map 10 Lake pier with the scripted loop from `docs/playtest-2026-10-24-harpies-one-at-a-time.md`. The loop never blocks, retreats, drinks a potion or rests. The Avatar is the same new-game one used there: STR 15, DEX 15, 30 hp, no armour.

**Verdict: fair now.** Armed, he won 10 of 10, but this is no walkover:

- Wave 1 (two zombies) with the sword left him on 3, 5 and 11 hp.
- Unarmed, he lost wave 1.
- Before the cut, one zombie killed the armed Avatar in about 10 s, 2 of 2.

## Verdicts

| Claim | Verdict | Evidence |
|---|---|---|
| **Z1** Hatched zombies carry the new stats | **PASS, 21 of 21 hatches** | At the hatch read, `findShape 872` gave hp **25-35** (mean 31.5) for every zombie, pilot included. Every logged zombie blow had a pre-armour `dmg` of **3-7**, against 6-12 on 10-25. The Avatar's weapon damage came through armour 8: the axe did 19 → 14 and 22 → 16 (−24%), against −45% at armour 15 |
| **Z2** Wave 1 (two zombies), axe ×4 | **4 of 4 won** | The Avatar ended on 23, 16, 30 and 9 hp. The fights took 18-32 s |
| **Z3** Wave 1 (two zombies), sword ×3 | **3 of 3 won, narrowly** | He ended on 3, 11 and 5 hp. The fights took 22-41 s |
| **Z4** Wave 2 (one zombie), axe ×3 | **3 of 3 won** | He ended on 30, 28 and 30 hp. The zombies landed 1 damaging blow (3) in 8 connecting |
| **Z5** Wave 1, unarmed ×1 | **Lost (recorded)** | He died at 32.4 s, with the zombies on 20 and 9 hp |
| **Z6** Every hatch was walked into | **PASS** | Each run logged exactly one `event 7 @ 0481` from the wave's trigger, fired by a walk that started 300-500 units south of it. No teleport was used inside a run |
| **Z7** Drownings | **None** | The run logs hold 0 CLRWATER hits (`(shape 347) … event 6`) and 0 `I_resetRef`. Every final position had z 8 on the pier or causeway. Both deaths (UN1, pilot P1) were combat deaths at hp 0, with damaging blows logged |

## Run table

**Hatched hp** is the hatch read. **hp** is the Avatar's hp at the start → the end. **Time** runs from combat on, just after the hatch read, to the last read; it includes the zombies' 6-9 s walk to him. **Landed** and **taken** count logged `received hit` lines as damaging / connecting, then the logged damage sum. The `Damage:` values are not capped at the target's remaining hp (harness anomaly 5).

| Run | Weapon | Wave | Hatched hp | hp start → end | Outcome | Time | Landed | Taken | Ended in water? |
|---|---|---|---|---|---|---|---|---|---|
| AX1 | axe | 1 (2) | 35 / 32 | 30 → **23** | **both killed** | 25.3 s | 7/9 (87) | 1/2 (7) | no |
| AX2 | axe | 1 (2) | 30 / 35 | 30 → **16** | **both killed** | 18.7 s | 8/12 (77) | 2/5 (14) | no |
| AX3 | axe | 1 (2) | 30 / 25 | 30 → **30** | **both killed** | 18.4 s | 6/8 (64) | 0/4 (0) | no |
| AX4 | axe | 1 (2) | 32 / 29 | 30 → **9** | **both killed** | 32.4 s | 8/13 (84) | 5/9 (22) | no; ended at the pier's south foot (13768,20516,8) |
| SW1 | sword | 1 (2) | 27 / 35 | 30 → **3** | **both killed** | 33.3 s | 8/14 (74) | 5/10 (27) | no |
| SW2 | sword | 1 (2) | 25 / 32 | 30 → **11** | **both killed** | 41.2 s | 7/12 (63) | 4/8 (19) | no |
| SW3 | sword | 1 (2) | 29 / 33 | 30 → **5** | **both killed** | 21.9 s | 7/8 (58) | 4/6 (25) | no |
| W2AX1 | axe | 2 (1) | 29 | 30 → **30** | **killed** | 25.0 s | 4/5 (35) | 0/3 (0) | no |
| W2AX2 | axe | 2 (1) | 34 | 30 → **28** | **killed** | 43.7 s | 3/6 (37) | 1/2 (3) | no |
| W2AX3 | axe | 2 (1) | 35 | 30 → **30** | **killed** | 26.9 s | 3/7 (35) | 0/3 (0) | no |
| UN1 | none | 1 (2) | 33 / 35 | 30 → **0** | **died** (zombies on 20 / 9) | 32.4 s | 11/17 (39) | 7/13 (34) | no; combat death at the east rail (13948,20448,8) |

### Pilot run, excluded from the tally

| Run | Weapon | Wave | Hatched hp | hp | Outcome | Why excluded |
|---|---|---|---|---|---|---|
| P1 | axe | 1 (2) | 34 / 33 | 30 → 0 | Died at 99.5 s. 161 was killed; 160 was untouched at 34 | Driver stall (harness anomaly 2). For about 55 s he stood at box gap 37, diagonal to zombie 160. His attack cycles logged no blow on it, while it landed 23 connecting blows (6 damaging, 36). Combat death, not water |

### Win rates

| Weapon / wave | 10-30 (new stats) | Winners' final hp |
|---|---|---|
| Axe, wave 1 | **4 of 4** | 23, 16, 30, 9 (mean 19.5) |
| Sword, wave 1 | **3 of 3** | 3, 11, 5 (mean 6.3) |
| Axe, wave 2 | **3 of 3** | 30, 28, 30 (mean 29.3) |
| Armed, all | **10 of 10** | mean 18.5 |
| Unarmed, wave 1 | 0 of 1 | – |

Pooled blow counts, armed runs only:

- **The Avatar's blows.** The axe was damaging in 39 of 60 connecting blows and the sword in 22 of 34. Damage after armour 8 was 3-16 per blow for the axe and 1-15 for the sword.
- **The zombies' blows.** 22 of 52 connecting blows did damage, for 3-7 each. On the sword runs, 13 of 24 did damage; on the axe runs, 9 of 28.

### Small samples

- **Sample size.** No armed run was lost, but there were only 10 of them. A 0-in-10 loss count is still consistent with a true loss rate of up to about 26% (95% upper bound).
- **The sword margin.** Wave 1 with the sword is the closest case. One more damaging blow (3-7) would have killed SW1.

## Comparison with 10-25 (finding F2, the old stats)

| | 10-25: old row (hp 35-50, dmg 6-12, dex 14-16, armour 15) | 10-30: new row (hp 25-35, dmg 3-7, dex 10-12, armour 8) |
|---|---|---|
| Zombie hp at hatch | 41, 43 (wave 1); 49 (wave 2) | 25-35, mean 31.5 (21 hatches) |
| Zombie blows on the Avatar | 12, 11, 8 (wave 1); 11, 8, 8, 6 (wave 2) | 3-7 each; 22 damaging of 52 connecting (armed runs) |
| Axe blows on a zombie | 8 and 9 after armour (2 of about 8 swings) | 3-16 after armour; 39 damaging of 60 connecting |
| Wave 1, armed | **died** in about 8-10 s (1 attempt, axe) | **won 7 of 7** (axe 4, sword 3), in 18-41 s |
| Wave 2, armed | **died** in about 10 s, zombie on 32 (axe) | **won 3 of 3**, losing 0-2 hp |

Caveats:

- **Different drivers.** The 10-25 numbers came from three short attempts with that session's own click loop. These came from the reach-aware loop described below.
- **What survives the caveat.** The per-blow figures depend on no driver, and they moved from 6-12 per blow and 41-49 hp to 3-7 per blow and 25-35 hp.

## Build pinned

- **Copy.** `shared/u8-lv-patched` and `scummvm-lv-console/scummvm` were copied once to `/tmp/claude-1000/zombie1030/` (`game/`, `bin/scummvm-console`). The ini is the 10-24 one: 320×200, `scale_factor=2`, `usehighres=true`.
- **The copy's `[waterzombie]` row** reads `hp_min=25 hp_max=35 dex_min=10 dex_max=12 damage_min=3 damage_max=7 armour=8`, with `defense_type=0x0050`.
- **Hashes.** `sha256sum -c pinned.sha256` was OK for all eight files at the end:
  - FIXED.DAT `9e666935…` (top level and `STATIC/`), EUSECODE `2e3b71c2…`, U8SHAPES `f64cbfd8…`, TYPEFLAG `7faaaf23…`, ANIM `97ae5fc9…`;
  - these five equal `shared/build/ARTIFACTS.sha256`;
  - `u8monsters.ini` `0642d689…`;
  - binary `d371f7ce…`, the same binary as 10-18 and 10-24.
- **Display.** Xvfb `:95`, driven by the replay's `lv.py` with its paths pointed at the scratch dir.

## Setup

**Banks.** The armed banks `harpie1018-s13b-armed-{sword,axe}-hp30.sav` and the unarmed `harpie1024-m13-south-unarmed-hp30.sav` are all on Map 13. Each was loaded, and then:

1. A positioning teleport to Map 10 (13820,20800,0) on the dry south shore, 384 units south of the wave 1 trigger's box. Cheats were toggled on and off around it.
2. A mobility check (E, then W).
3. A teleport back to the spot, then a bank.
4. For wave 2, a teleport to (13824,19760,8) on the pier and a second bank. That spot lies between the wave 1 trigger and the wave 2 trigger, so it touches neither.

The map hop reloads Map 10 from the pinned FIXED.DAT. Before any run, `findShape 500/73` listed:

- wave 1: trigger (13824,20352,8), range 4,2, with eggs (13888,19936) and (13792,19744);
- wave 2: trigger (13824,19456,8), range 4,1, with egg (13344,19008);
- wave 3: trigger (13312,18816,8), with eggs (13855,18271) and (14016,18400). Wave 3 was not run.

All triggers read `hatched=0`. No `event 7` was logged during setup.

| Bank (`~/lv-checkpoints/`) | md5 | State |
|---|---|---|
| `zombie1030-m10-lake-south-axe-hp30.sav` | `12a8e92b` | (13820,20800,0), hp 30, axe, weight 110 |
| `zombie1030-m10-lake-south-sword-hp30.sav` | `9ec9d076` | (13820,20800,0), hp 30, sword, weight 90 |
| `zombie1030-m10-lake-south-unarmed-hp30.sav` | `3f8e4994` | (13820,20800,0), hp 30, unarmed, weight 60 |
| `zombie1030-m10-pier-w2-axe-hp30.sav` | `90f1f468` | (13824,19760,8), hp 30, axe |
| `zombie1030-m10-pier-w2-sword-hp30.sav` | `e4190ccd` | (13824,19760,8), hp 30, sword. Not used |

**Weapons.** The hit types in the logs confirm the weapon in every run: the axe hits read `type=6`, the sword hits `type=2` and the fists `type=1`.

**Each run:**

1. Stop ScummVM, copy the bank to slot 1, and relaunch with `--save-slot=1`.
2. Enable `Object` and `Actor`.
3. Walk north in 0.8 s presses until the zombies are listed:
   - wave 1: from y 20800, the hatch read had him at y 20296-20400;
   - wave 2: from y 19760, the hatch read had him at y 19464.
4. Press `c`, then fight until every hatched zombie or the Avatar reads hp 0.

### The fight driver (v3)

v3 is the 10-24 v2 loop with a reach rule for a 64×64 monster. Each cycle reads `findShape 872` and `objectInfo 1`. The read writes its commands and `exit` in one batch, so it takes no live time.

- **Target.** The nearest live zombie by box gap. Both boxes are 64×64, anchored at the max corner.
- **When to swing.** If the Avatar's box, shifted 32 units in one of the 8 directions, overlaps the zombie's box, he faces that direction and double-clicks twice, 0.7 s apart.
- **Otherwise.** He takes a 0.45 s advance toward the zombie, then swings once. After two reads with no movement (a corpse or the rail in the way), he sidesteps perpendicular.

He never blocks, retreats, drinks a potion or rests. v2 swung whenever the gap was 40 or less. That stalled in P1 (harness anomaly 2), and v3 is the fix.

### Console commands used (whole session)

- `debugflag_enable Object` and `debugflag_enable Actor`, after every start (17 starts: 4 setup, 13 runs), and again after each setup teleport.
- Reads: `ObjectManager::objectInfo 1`, `ObjectManager::findShape 872` (every driver cycle), and `ObjectManager::findShape 500` and `73` (once, at setup).
- `Cheat::toggle` 20 times: on and off around each setup teleport. The logs hold 10 `Cheats = true` and 10 `Cheats = false`, all in `lv_setup_*.log`. Every run log holds 0 of each, so cheats were off for every fight.
- `MainActor::teleport` 10 times, all during setup: `10 13820 20800 0` 7 times (one in the interrupted first axe setup) and `10 13824 19760 8` 3 times.
- `Ultima8Engine::saveGame` 5 times, for the banks.
- **Not used:**
  - `loadGame`: reloads were restarts with `--save-slot`;
  - `MainActor::toggleCombat`: combat used the real `c` key;
  - invincibility, heal, item cheats, `Item::grab` and `setGlobal`.

  A grep of every log for `invincib|Cheat::heal|Cheat::items|setGlobal` found nothing.

## Findings

1. **Severity: info (balance). The cut lands where intended.**
   - **Armed.** An armed 30-hp Avatar now beats wave 1 and wave 2 with a driver that never defends.
   - **Unarmed.** Wave 1 still kills him.
   - **Old numbers.** On 10-25, one zombie killed the armed Avatar in about 10 s.
2. **Severity: low (balance, for the `lv_monsters.py` owner). The sword is markedly weaker than the axe against wave 1.**
   - **Final hp.** Sword winners ended on 3, 5 and 11; axe winners on 9-30.
   - **The zombies' hit rate.** On wave 1 with the sword, 13 of 24 connecting zombie blows did damage; with the axe, 8 of 20.
   - **Cause.** [INFERENCE] `MainActor::getDefendingDex` reads the equipped weapon (`main_actor.cpp:462-465`), so the axe may carry the larger defensive dex. The weapons' bonus values were not checked.
   - **Margin.** One more damaging blow would have killed SW1. If Douglas wants the sword to be as safe as the axe here, this is the margin to look at. Wave 3 also hatches two zombies, at the island; it was not run.
3. **Severity: info. No drownings, and the rails hold.**
   - **The log record.** Across all 11 run logs (13 sessions, P0 and P1 included) there were 0 CLRWATER `event 6` and 0 `I_resetRef`.
   - **Where the fights went.** They pressed the Avatar against the east rail (x 13948) and once to the pier's south foot (AX4, y 20516). He stayed at z 8 every time.
   - **Setup logs.** The `I_resetRef` lines there are the map-load resets of NPCs 3, 7 and 13 that follow each teleport to Map 10, not water.
4. **Severity: info. The player sees them coming.** Wave 1's zombies hatch 400-600 units north of the trigger. They need 6-9 s to reach him, so the hatch is visible before the first blow.

## Harness anomalies

1. **Walk drift (P0, no hatch).**
   - **What happened.** The first AX1 attempt walked with `lv.run([('N', …)], mag=240)`. That drifted 160 units east, and he wedged at the pier's south-east corner (13980,20544,0), against rail 498 at x 13983 (`P0-walk-drift-pier-se-corner`). 13 presses moved him 0, and nothing hatched.
   - **The fix.** The walk now steers by the world vector toward x 13860, at 110 px. Every later walk went straight north up the pier's centre line.
2. **v2 stall (P1).**
   - **What happened.** With the 10-24 rule (gap 40 or less → swing), he stood at box gap 37 from zombie 160 (it NW, he SE) from t 21.6 to 75.3 s. Neither moved. None of his attack cycles logged a blow on 160, while it landed 23 connecting blows.
   - **Why it was not reach.** ANIM.DAT gives the Avatar's attack frames 0,1,2,1,0,0 in all eight directions, and a range-2 frame there would have overlapped 160's box. Range alone therefore does not explain it.
   - **Cause.** [INFERENCE] His swing never started. Likely the prime press's advance into the 161 corpse west of him left the double-clicks unconsumed. Not proven.
   - **Status.** v3 replaced the rule, and no later run stalled. P1 is reported but kept out of the tally.
3. **P1's plates were overwritten.** P1 reused the `AX1-hatch`/`AX1-end` names. `lv_AX1.log` holds three sessions in order: P0, P1, then the counted AX1. Its 2 `event 7` lines are P1's and AX1's.
4. **Interrupted axe setup.** The kernel's 30 s default cell timeout interrupted the first axe-bank build mid-mobility-check. It was rebuilt from scratch in the same log, which accounts for its extra cheat pair and teleport.
5. **Logged `Damage:` is not capped at the target's hp.** AX1 logged 87 against two zombies holding 67. The 10-24 report says its totals are capped. Here they are not, so treat the sums as dealt, not absorbed.

## Log hygiene

The 11 run logs and 3 setup logs hold 0 of each of these:

- `Cycle in paint`, `Assertion`, `Segmentation` and `stuck in process loop`;
- `Unhandled intrinsic`, `ERROR`, `Non-existent process` and `failed to set stats`.

`Enabled debug flag 'Object'` follows every start.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-30-zombie-balance/` (27 plates):
  - `<run>-hatch` and `<run>-end` for the 11 tallied runs;
  - `setup-01`…`setup-04`;
  - `P0-walk-drift-pier-se-corner`.
- **Wrote** the five `zombie1030-m10-*` banks in `~/lv-checkpoints/`. Nothing was overwritten.
- **Scratch** is `/tmp/claude-1000/zombie1030/`: the pinned `game/` and `bin/`, `pinned.sha256`, `saves/` (with the `.bak` bank copies), the logs `lv_*.log`, `runs.json` (per-run reads and hits), `trace.txt`, the frames in `sp/` and the copied `py/`.
- **Stopped** my ScummVM and Xvfb `:95`.
- **Not touched:**
  - source, including the uncommitted `lv_monsters.py`, maps, the fork, `shared/` and `TODO.md`;
  - the older scratch dirs and every older bank.
- **No** rebuilds and no commits.
