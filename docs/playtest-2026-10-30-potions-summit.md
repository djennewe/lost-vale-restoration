# Map 10 one-time potions and Map 13 single summit harpies: in-engine check (2026-10-30)

This checks two uncommitted changes on the integrated build:

1. **Map 10 potions.** `lv-patched/POTION.UNK` change 2 sets `potionProtectionDrunk` (bit 1830, `0x726`) when a frame-5 potion is drunk and `potionInvisDrunk` (bit 1831, `0x727`) for frame 7. `lv-new/REAPPLY.UNK` (EggReapply, class `0x5B2`) runs on Map 10's arrival pads. It destroys Map 10's frame-5 or frame-7 world potion when that potion's flag is set or the Avatar carries one of that frame.
2. **Map 13 summit harpies.** The summit pair is split into two waves of one: a new group-4 trigger at (5119,2687,120) hatches one harpie at (5183,2175,120), and the group-2 trigger at (4863,1663,120) now hatches one at (4287,2175,120).

## Verdicts

| Claim | Verdict | Evidence |
|---|---|---|
| **P1** Drink protection from the pack, leave, return: it is gone | **PASS** | Drunk from the pack (`P7-protection-drink-a`), so `0x726` reads 1 and the bottle in the pack reads frame 0. After a walked 204 → Map 11 → 205 round trip, `findShape 859` lists no frame 5 on the map, and the hut floor is empty (`P1-hut-after-trip3`). It was also absent after a later arrival by pad 206 (`P1P2-pad206-arrival`) |
| **P2** The same for invisibility | **PASS** | Drunk from the pack, so `0x727` reads 1 and the bottle reads frame 0. After a walked round trip into pad 205, and after a separate walk into pad 206 from Map 13, `findShape 859` lists no frame 7 on the map |
| **P3** Carry an undrunk protection potion off and back: no second copy | **PASS** | I carried both f5 and f7 undrunk, with both flags at 0. After the round trip, `findShape 859` listed no f5 or f7 on the map, only the two in the pack, and the floor was empty (`P3-hut-after-trip1`). **Negative control:** with f5 dropped on the hut floor rather than carried, the next round trip deleted the dropped copy and put the record back (`P3x-*`): one copy, neither duplicated nor lost |
| **P4** Health and mana, taken and drunk, are back after re-entry | **PASS** | Both were dragged to the pack and drunk there: mana gave "Yummm..." and health took hp 15 → 30. After **each** of five later Map 10 entries, `findShape 859` again listed f1 at (13760,12800,4) and f2 at (13696,12800,4), with new object ids each time |
| **P5** Hrodny's chest Tiny Tars are still there after re-entry | **PASS** | After every Map 10 entry (6 of 6), there were three contained f8 records with new ids at the chest. The save's own three, already in the pack, stayed there too |
| **P6** Nothing drunk or carried: all four stand after re-entry | **PASS** | On the first walked arrival (205, from the old save, flags 0, no f5 or f7 carried), EggReapply ran (`event 7 @ 05B2`) and f1, f2, f5 and f7 all stood at their placements (`P6-hut-after-reentry0`) |
| **P7** Effects still work; EggReapply does not bark | **PASS** | **Protection:** the bark "I feel like fighting!" and Actor flags `40000` (immortal). **Invisibility:** Avatar item flags `0x2041` → `0x2055`, and the sprite went translucent (`P7-invis-compare`). Plates at 1 s and 2 s after landing on pad 205 show no bark (`P7-pad205-arrival-*`). One thing went untested: a second invisibility dose taken while already invisible, because only one f7 potion exists |
| **H1** Nothing hatches at the rest point. Crossing y≈2700 hatches exactly one harpie | **PASS (4 of 4 walk-ons)** | I stood 60 s at (5087,3039,112): 0 `event 7`, 0 harpies. Walking N, the step that read y 2839 hatched nothing; the next, at **y 2743**, logged `Item: 6575 (shape 73) calling usecode event 7 @ 0481:0080` and exactly one live 873 (id 160, hp 34-42). Same in R1-R4 |
| **H2** After the kill, walking W across x≈4863 at y≈1663 hatches exactly one more | **PASS (5 of 5 walk-ons)** | The step that read x 4991 hatched nothing; the next, at **x 4887**, logged `Item: 2094 (shape 73) … event 7 @ 0481:0080`. The only live 873 was then id 161 (hp 31-40), with 160's corpse beside it. Seen in R1, R3, R4, R5 and R6 |
| **H3** The walk reaches teleporter 209 → Map 17 | **PASS (2 of 2)** | R3: the summit body lay at (4771,1635), north of the neck, and the walk logged `teleporting to map 17, egg 209` → (4608,9984,0) at hp 25. R6: the body lay at (4647,1783), on the straight W line; the route went round it to the north and down at x≈4451, then 209 → (4672,10048,0) at hp 19. Neither body lay in the neck itself, so the documented "body in the neck" case was not reproduced |
| **H4** Armed fights (sword) against each new single harpie | **DONE (measured)** | **Top harpie (group 4), from 30 hp:** won 3 of 4, ending on 21, 23 and **3** hp. R2 died, with the harpie untouched at 42: 3 connecting blows, 0 damaging. **Summit harpie (group 2), from 22-24 hp:** won 2 of 4, ending on 24 and 18 hp. R1 died with the harpie on 17, and R5 with it on **1**. A fifth summit fight (R4) began at 3 hp and is not counted. Table below |
| Log hygiene | **PASS** | All 7 logs: 0 each of `Cycle in paint`, assert, `ERROR`, `Segmentation`, `Non-existent process` and `Unhandled intrinsic`. `Enabled debug flag 'Object'` comes after every load, and the Object-channel `calling usecode event` lines only appear after it |
| Build and engine | **PASS** | Each log reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `usecode/eusecode.flx: 84615e29…, 1529089 bytes`. `sha256sum -c pinned.sha256` gave OK for all 8 pinned files at the start and the end |
| Verifier "always" checks (`run_all_tests.sh`, `build_artifacts.sh`) | **NOT RUN** | The brief said no rebuilds. The pinned bytes were hash-checked against `shared/build/ARTIFACTS.sha256` instead |

## Build pinned

- **Copy.** `shared/u8-lv-patched` → `/tmp/claude-1000/pot1030/game/`, and `scummvm-lv-console/scummvm` → `bin/scummvm-console`, copied once.
- **Hashes.** `pinned.sha256` was checked OK at both the start and the end:
  - FIXED.DAT `039f6775…` (top level and `STATIC/`);
  - EUSECODE `b47c324c…`, U8SHAPES `f64cbfd8…`, TYPEFLAG `7faaaf23…`, ANIM `97ae5fc9…`;
  - `u8monsters.ini` `0642d689…`;
  - binary `e0518ced…` (built 20:33).
- **Harness.** Xvfb `:95`. The ini was the 10-30 zombie one: 320×200, `scale_factor=2`, `usehighres=true`. The driver was the replay `lv.py`, with its paths pointed at the scratch dir.

## Potions (P1-P7)

**Start.** `replay1017-s16b-m10-three-tiny-tar-chest-open-hp30.sav`, Map 10, in Hrodny's hut at (21196,8924,0).

**Before the first hop**, the save itself read:
- `0x726` = 0 and `0x727` = 0;
- `findShape 859`: f1, f2, f5 and f7 at their placements, plus three f8 already in the Avatar's pack. The chest held nothing.

**Every re-entry was a walk**, by one of two routes:
- **The 204/205 round trip.** A setup teleport to (12560,2640,0) on Map 10, beside pad 205 and outside every trigger box. Then a 1.2 s NW walk into trigger 204 → Map 11 pad 204 (8291,22639,0), then a 1.5 s SE walk into trigger 205 → Map 10 pad 205. Each arrival logged `Loading Fixed items in map 10` and `Item: N (shape 73) calling usecode event 7 @ 05B2:0080` (EggReapply).
- **Pad 206.** A setup teleport to Map 13's arrival pad 207 (4096,11776,0), then a 1.5 s W walk into trigger 206 → Map 10 pad 206 (7072,23296,8), again with the EggReapply event.

**Pickups** were real drags onto the Avatar. The log showed `Dragging item N` → `Dropping object N` → `Dropped item in backpack` for f5 (twice), f7, f1 and f2. `Item::grab` was never needed.

**Drinks** were double-clicks on the bottle in the open pack gump. Each logged `Item: N (shape 859) calling usecode event 1 @ 04E5:00A9`.

### Sequence and reads

| Step | Pack: f5 / f7 | Flags `0x726` / `0x727` | World after the step, from `findShape 859` |
|---|---|---|---|
| Trip 0: old save → Map 11 → walk 205 | none / none | 0 / 0 | f1, f2, **f5 (21216,8832,0)** and **f7 (21280,8832,0)** all stand. The chest has 3 new f8 (**P6**, **P5**) |
| Picked up f5 and f7. Picked up and drank f1 and f2 | — | — | — |
| Trip 1: 204 → 205 | **undrunk / undrunk** | 0 / 0 | f1 and f2 are back. **No f5, no f7.** The chest has 3 f8 (**P3**, **P4**, **P5**) |
| Dropped the undrunk f5 on the hut floor at (21254,8850,0) | dropped / undrunk | 0 / 0 | — |
| Trip 2: 204 → 205 | none / undrunk | 0 / 0 | **f5 is back at its placement and the dropped copy is gone.** f1, f2 and 3 f8 are present. No f7 (**P3 negative control**) |
| Picked f5 up again and **drank it** from the pack | empty / undrunk | **1** / 0 | — |
| Trip 3: 204 → 205 | empty / undrunk | 1 / 0 | **No f5** (no undrunk f5 carried, so the flag alone did it). No f7. f1, f2 and 3 f8 are present (**P1**) |
| **Drank f7** from the pack | empty / empty | 1 / **1** | — |
| Trip 4: 204 → 205 | empty / empty | 1 / 1 | No f5 and **no f7** (flag alone). f1, f2 and 3 f8 are present (**P2**) |
| Trip 5: Map 13 → walk into 206 | empty / empty | 1 / 1 | No f5 and no f7. f1 and f2 are present. A second pad was exercised (`P1P2-pad206-arrival`) |

### Effects (P7)

- **Protection.** Drinking it barked "I feel like fighting!", and `objectInfo 1` read Actor `flags: 40000` (immortal). The flag was still set after trip 3 (`40400`) and had cleared by the next read.
- **Invisibility.**
  - **Flags.** The Avatar's item flags went `0x2041` → `0x2055`: +0x10 (invisible), from `toggleStatus(INVISIBLE)`, and +0x04 (owned), from `toggleStatus(OWNED)`.
  - **On screen.** The sprite drew translucent (`P7-invis-compare`: before on the left, after on the right).
  - **Expiry.** By the trip-4 arrival the flags read `0x2045`, so the effect had expired. See finding 2.
- **No barks from EggReapply.** No text appeared in the plates at 1 s and 2 s after landing on pad 205. The only barks seen all session were village NPCs' green lines in the hut, far from any pad.

## Summit harpies (H1-H4)

**Setup** used `harpie1024-m13-south-sword-hp30.sav` (sword, 30 hp, STR 15, DEX 15):
- teleport to Map 9 (13850,14230,0), then to Map 13 at the rest point (5087,3039,112), with cheats on only around the teleports;
- after the hop, `findShape 500/73` listed:
  - **trigger 6575 at (5119,2687,120)**, range 6,2, with egg 3368 at (5183,2175,120), m 33 (group 4);
  - trigger 2094 at (4863,1663,120), range 1,6, with **one** egg, 2041 at (4287,2175,120), m 17 (group 2). The old (4287,2047) egg is gone;
  - the lane groups 1 and 3, unchanged and unhatched;
- 60 s of standing at the rest point (H1), then a scratch save there (`sp/H-rest-newfixed.sav`, hp 30). R2-R4 each start from that save with no teleport. R5 and R6 start from R3's save taken after the top-harpie kill (`sp/R3-afterH1.sav`, hp 23).

**Walking:**
- **H1.** 0.6 s N presses, reading position after each.
- **H2.** 0.8 s N presses up the leg to y ≤ 1720, then 0.6 s W presses.
- **H3.** The `follow.py` distance-field walker, on an exact_reach lattice of the pinned FIXED with the body's box forbidden.

**The fight driver** ran in this session's eval kernel. It is the 10-24 v3 rule set: if the Avatar's box, shifted 32 units in one of the 8 directions, overlaps the harpie's box, he double-clicks twice toward it, 0.7 s apart. Otherwise he takes a 0.45 s advance and one swing, and after two reads without moving he sidesteps. It never blocks, retreats or rests, and combat mode came from the real `c` key.

**Times** are wall-clock and include the paused console reads, so they overstate live time.

| Run | Fight | Harpie hp at hatch | Avatar hp start → end | Outcome | Wall time | Avatar's blows: damaging / connecting (dmg) | Harpie's blows: damaging / connecting (dmg) |
|---|---|---|---|---|---|---|---|
| R1 | top (g4) | 38 | 30 → **21** | killed | 36.7 s | 5/5 (50) | 2/9 (10) |
| R1 | summit (g2) | 39 | 22 → **0** | **died**, harpie on 17 | 46.3 s | 3/7 (22) | 3/8 (28) |
| R2 | top (g4) | 42 | 30 → **0** | **died**, harpie untouched on 42 | 58.6 s | 0/3 (0) | 4/6 (31) |
| R3 | top (g4) | 34 | 30 → **23** | killed | 45.1 s | 4/5 (34) | 1/4 (7) |
| R3 | summit (g2) | 37 | 24 → **24** | killed | 26.7 s | 5/7 (39) | 0/7 (0) |
| R4 | top (g4) | 34 | 30 → **3** | killed | 46.6 s | 3/5 (31) | 3/6 (28) |
| R4 | summit (g2) | 31 | 3 → 0 | died (the driver walked on at 3 hp; **not counted**) | 26.4 s | 0/0 | 1/2 (5) |
| R5 | summit (g2), from R3's save | 40 | 24 → **0** | **died**, harpie on **1** | 86.5 s (2 `ATTACH FAILED`) | 4/4 (39) | 4/7 (25) |
| R6 | summit (g2), from R3's save | 38 | 24 → **18** | killed | 29.5 s | 4/5 (41) | 1/3 (6) |

**Reading the table:**
- **Harpie blows** did 5-10 per damaging hit, the same range as 10-24.
- **R2's death** came from 4 damaging blows of 6 (31) while all 3 of the Avatar's connecting sword blows did no damage.
- **Summit fights from 22-24 hp:** 2 won, 2 lost (R5 by one hit point).
- **A player can rest before the summit.** Between the two waves nothing is alive, so a player can heal at the global rate first (finding 5). No run here rested.

## Findings outside the brief

1. **Info: a real drag of a shape-859 potion works.** Five drags all logged `Dropped item in backpack`. traps.md's 2026-08-17 note "potion 859 refuses (open bug)" is stale, at least on this build. `Item::grab` was not used.
2. **Low: invisibility leaves the Avatar `OWNED` for good.**
   - **What happened.** `invisible()` toggles OWNED on and only ever toggles INVISIBLE off. After the effect expired, the Avatar read `0x2045` against `0x2041` before.
   - **Not new.** This is 1994 code, unchanged by this diff.
   - **Effect.** Not determined. [INFERENCE] OWNED on the Avatar probably does nothing.
3. **Info: Ezrekal's restocking health potion is a trap at full hp.**
   - **What happens.** Frame 1 at full hp sets hp to STR: "Augh!", 30 → 15. The retail 766 potion in the save's pack did exactly that when drunk by mistake (harness anomaly 2).
   - **Not new.** The 1994 `POTION.UNK` frame-1 branch is unchanged.
   - **Why mention it.** It matters more now that the potion restocks on every visit.
4. **Low: the top harpie's body stalls the walk north.**
   - **How often.** In every run where the top harpie died near the trigger (R1, R3, R4, R5, R6), its corpse lay at about (5071-5115, 2531-2687), right ahead on the Avatar's lane. The next N press moved him 0.
   - **The way round.** A 0.8 s E sidestep cleared it each time.
   - **Same mechanism as before.** This is 10-24 finding 2, now at the top of the leg, and `test_harpie_corpses.py` holds that one body never closes the leg.
5. **Info: the split works as designed.**
   - **Never two at once.** At every read of every run there was at most one live harpie. Between the waves only the corpse was listed.
   - **A rest after the top harpie.** After the top harpie's kill, nothing hatched on the leg up to x 4991, y 1631. So a player can rest anywhere on the top of the leg before the summit. The rest point is no longer the only rest.
6. **Info: no summit body landed in the neck in 5 summit fights.**
   - **Where the bodies fell.** The two that died fell at (4771,1635) and (4647,1783), on the plateau's east side. Both left a way to 209.
   - **Not exercised.** The accepted "body in the neck" case (x 4255-4479, or the column below it) did not occur, so the "walk back down clears it" remedy was not tested.

## Harness anomalies

1. **`ATTACH FAILED`** occurred 9 times across the sessions (`trace.txt`):
   - **Lost Cheat::toggle replies.** Twice it ate the echo of a `Cheat::toggle`. I re-read the `Cheats = …` lines in the log and re-toggled, and every log ends with as many `true` as `false` (P0 13/13, setup 2/2).
   - **One teleport not sent.** One `MainActor::teleport 13 4096 11776 0` never went out; the Avatar stayed on Map 10, and the command was resent.
   - **Blind time in R5.** It left R5's fight blind twice; that run is still counted.
2. **Two wrong items moved, both scratch-only:**
   - **The 809 flask.** At Ezrekal's shelf the mana potion was hidden behind the Avatar, and one drag lifted an 809 flask (GIRLSSTU dressing) into the pack.
   - **The retail potion.** In the pack, a double-click aimed at the red LV health potion hit the save's retail **766** potion (id 31220) and drank it: hp 30 → 15.
   - **Effect on the results.** Neither touches the claims. The LV health potion was drunk next and restored hp to 30.
3. **One eval cell hit its 30 s timeout** between a cheats-on toggle and its teleport. Cheats were found on, so I sent the teleport and turned them off (confirmed by `Cheats = false`) before any further input.

## Console commands used (every session)

- **Reads:**
  - `ObjectManager::objectInfo` on 1, the harpie ids 160/161, and the potion ids 10175, 20429, 26900, 27161, 27162, 27312, 28748, 29636, 30048, 31220;
  - `ObjectManager::findShape` 859, 873, 500 and 73;
  - `UCMachine::getGlobal 0x726 1` and `0x727 1`.
- **Flags:** `debugflag_enable Object` after every start, and `debugflag_enable Actor` in the harpie sessions.
- **`Cheat::toggle`:** only around setup teleports. The log echoes were 15 `Cheats = true` and 15 `Cheats = false`, all in `lv_P0.log` and `lv_Hsetup.log`. Run logs R2-R6 hold none, so every fight and every walk into a pad had cheats off.
- **`MainActor::teleport`, setup only:**
  - Map 10: (21196,8924,0) ×5, (12560,2640,0) ×4, (13790,12900,0) and (13650,12760,0);
  - Map 11: (8291,22700,0);
  - Map 13: (4096,11776,0) ×2, one of which never sent, and (5087,3039,112);
  - Map 9: (13850,14230,0).
- **`Ultima8Engine::saveGame`:** `H-rest-newfixed`, `R3-afterH1`, `R3-afterH2`, `R4-afterH1` and `R6-afterH2`, all to scratch.
- **Not used:** `loadGame` (reloads were restarts with `--save-slot=1`), `Item::grab`, `setGlobal`, `Cheat::heal`, invincibility, item cheats, `MainActor::toggleCombat` (combat used the `c` key).

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-30-potions-summit/`, 44 plates named by test (`P*`, `H*`, `R<n>-*`, plus `shape859.png`, the frame sheet used to tell the potions apart in the pack).
- **Scratch** is `/tmp/claude-1000/pot1030/`:
  - the pinned `game/` and `bin/`, and `pinned.sha256`;
  - `lv_P0.log`, `lv_Hsetup.log` (R1) and `lv_R2-6.log`;
  - `trace.txt` and `runs.json`;
  - `sp/` (all frames, and the scratch saves `H-rest-newfixed.sav`, `R3-afterH1.sav`, `R3-afterH2.sav`, `R4-afterH1.sav`, `R6-afterH2.sav`);
  - `py/`, a copy of the replay driver.
- **Not touched:** source, builders, `shared/`, the fork, `TODO.md`, `HANDOFF.md`, `~/lv-checkpoints/` (nothing banked) and the other scratch dirs.
- **Stopped** my ScummVM and Xvfb `:95`.
