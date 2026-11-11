# Full 1→18 run, cheats off, part 4: step 3 done through the doors, Map 11 with 3 of 4 talismans, NOT COMPLETED (2026-10-10)

**Build under test.** main `4a40dc8`, fork `8af4f74e`, binary `scummvm-lv/scummvm`.
- **Game copy.** `/tmp/claude-1000/vrun4/game` is an rsync of the part-3 copy with no `.bak` files. sha256 matches `shared/build/ARTIFACTS.sha256`: EUSECODE `709c6bd1…`, FIXED `22cada6f…` (root and `STATIC/`), U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…` and ANIM `77e9705d…`. The log line reads `usecode/eusecode.flx: 7545064984f3c73b6142d1a87f6d279e, 1525518 bytes`.
- **Harness.** Xvfb `:95`, window at (480,300), `frameLimit=true`, `usehighres=false`, `scale_factor=2`. The ini has no width/height keys, and the log reads `Setting Video Mode 320x200`. The save dir is private.
  - The driver is new: `vrun4/py/v4.py` and `nav.py`.
  - `nav.py` routes over `exact_reach` (`pathfind.DryReach`, 8-connected, with erosion and forbidden boxes), turns the route into 8-direction held-run legs at 640 u/s, then rereads the position and replans.
- **Start.** `~/lv-checkpoints/run1010-s02c-m8-corridor-gap-hp30.sav`: Map 8 (18172,5032,0), hp 30, step 2 done.

**Outcome.**
- **Furthest step completed: 3.** I found the key in the chamber chest and used it on both leaves. Both opened, and I walked north onto trigger 201, which took me to Map 9. From there trigger 203 took me to Map 11.
- **Step 4 partial.** I carried the Earth, Air and Water talismans; the Fire talisman, the four pillars and the exit are still to do.
- **Cheats: 0.** `Cheats` appears 0 times in `vrun4/lv_run.log`.
- **Console use.** Only `objectInfo`, `findShape`, `debugflag_enable Object`, `saveGame` and `loadGame`.
- **Everything else was player input:** mouse runs, look clicks, double-clicks, drags and gump drags.

## Verdicts

| Step / leg | Verdict | Evidence |
|---|---|---|
| Plan the lane with `exact_reach` before moving (erosion ≥ 2, NONFIXED solids, globs expanded) | **PASS, with a caveat** (finding 6) | `vrun4/py/plan.py`/`plan8.py` use `avatar_mover.map_items(8)` (FIXED plus new-game NONFIXED) and `ExactReach`, which expands globs. The erode-2 flood is in `vrun4/flood2.png`, and the spitter fast-area model reimplementing `updateFastArea` is in `vrun4/zones.png` |
| Gap → spitter-2 corridor → lane → SP3-free pocket (20600,7100) | **PASS**, hp 30 → 30 (RUN2) | A held run E 3.32 s → SE 1.65 s → S 1.75 s. It slid through the boxes at (20031-20095,5375-5439) and (20255-20383,5215-5343) and down the x 20543-20607 lane (plate `s03-01`). RUN1 was the same plan and took 25 hp from a hit in a MISSTRAP lane at x≈18431 (finding 5) |
| Bone Crusher chest (23824,7128) | **FAIL (not obtained)**: 3 deaths, all to one retail skeleton (finding 1) | `findShape 119`: item 148, SKELETON, hp 38-42, ac 17, rose from the bones at (23302,7154). Egg 9184 SKELEGG (23758,7194), `m: 101, hatched=1` after the hatch (plate `s03-02`) |
| Plateau healing potions | **NOT DEMONSTRATED** (skipped for budget) | — |
| Doors chamber reached from the gap | **PASS**, hp 30 | RUN10 (E 3.54 s, N 2.5 s) → (20212,3592,8), saved `w-chamber-arrive` |
| Kill the two shape-808 monsters | **NOT DEMONSTRATED.** I did not fight them | They were adjacent about 10 s after arrival (items 146/147, plate `s03-03`). They are avoidable after a map change (finding 3) |
| First Map 9 arrival | **DISCARDED as a skip** (finding 2) | The monsters' knockback shoved the Avatar against the closed leaves, and the checkpoint's stale T201 box fired → Map 9 (13696,14208). Banked only as `…s03x…-SKIP` |
| **Step 3, done properly:** key → both leaves → open → T201 → Map 9 → T203 → Map 11 | **PASS** | Map 9 T200 back to Map 8 dest 200 (20111,3175,8), now on current fixed items. Chest double-click → gump (`s03-05`). Key 6343 double-click → target **TDOOR_EW 2305** q 1123 → **99**; target **8428** q 1635 → **611** (second try, finding 4). Double-click the leaf → both became **TDOOR_NS 340** at (20255,3071)/(20479,3071) (`s03-06`). Run E then N → **Map 9 (13696,13760)** (`s03-m9-arrival-proper`). Run S → **Map 11 pad 203 (9728,1792,0)** (`s03-m11-arrival`). No 808s spawned on that visit (finding 3) |
| Step 4: talismans | **PARTIAL, 3 of 4** | I dragged each onto the Avatar; the log reads `Dropped item in backpack` each time. Weight 20 → 30 (Earth 2608 q101), → 40 (Air 30752 q102), → 50 (Water 3942 q104). The routes avoided every monster egg's hatch box; no monster hatched and hp stayed 30 throughout Map 11 |
| Step 4: Fire talisman, pillars, exit; steps 5-18 | **NOT DEMONSTRATED** (budget) | The last leg oscillated at (6212,18204-19236) in the Water section. My driver drops held legs under 0.4 s, so the router's 104-unit west jog into the Fire doorway never ran. This is a harness limitation, not a geometry finding |
| Log hygiene | **PASS for LV code** | 0 each of: `stuck in process loop`, Segmentation, Assertion. There was 1 `Unhandled intrinsic 254 'isGameRunning()'`, raised by the retail CHEST_EW (class 004E) use on the doors-chamber chest; the gump opened anyway. 13,357 `Cycle in paint 590 -> 235`, the retail bone-chamber pair |

## Findings

1. **The Bone Crusher chest is guarded by a guaranteed retail skeleton, and an unarmed Avatar cannot loot it.**
   - **The egg.** SKELEGG (class 04AD, egg q 46, npcnum 0x63) sits at (23758,7194). Its range is x ±192, y ±96. Any Avatar anchor in x [23566,24014), y [7098,7354) hatches it, and so does every spot within the 128-unit `use` reach of the chest: I checked all four sides against `Item::canReach`.
   - **Why it always fires.** With eggId 1 (the egg's mapnum) the hatch is unconditional. The 10% roll applies only to other ids (`00CD`-`00EB` in the disassembly). It converts up to two non-NPC shape-119 bone piles within 640, here the one at (23302,7154), into a hostile SKELETON (`u8monsters.ini`: hp 35-45, dmg 7-13, armour 17).
   - **The damage race.**
     - The Bone Crusher (`u8weapons.ini`: base 11, mod 9, damage type 0x24 = BLUNT|MAGIC, **not** UNDEAD) deals about 9 per hit after the skeleton's 51% armour cut.
     - The skeleton deals about 3.7 hp/s against AC 0; the observed rate was 30 → 22 in about 5 s.
     - So looting under attack and then fighting is a losing race at 30 hp.
   - **The bones are too heavy to move.** Their weight is 200 (×10).
   - **Deaths.** Three, saved as scratch `w-chest-east-hp30` (skeleton adjacent) and `w-room-east` (skeleton adjacent, hp 30 → 22 within seconds of load).
   - **Classification.** Retail content, not an LV defect. It does mean the "arm first" plan from part 3 is not available to a prologue Avatar.
2. **A stale-checkpoint skip: the old T201 box reaches 3 units south of the closed doors.**
   - **The two boxes.**
     - The checkpoint was saved on an older build, so its Map 8 fixed items carry T201 at (20415,**2786**) with npcnum 0xC9 (±384 × ±288). That puts anchor y < **3138** in the hatch box.
     - The current build has (20415,**2783**), so y < 3135. That is flush with the leaves (y [3039,3071)), whose south face stops the Avatar at y ≥ 3135.
   - **The model check.**
     - I flooded the chamber with exact_reach from (20212,3592,8), at erode 0 with the closed leaves solid.
     - It found **63** reachable lattice positions inside the old box, at y 3135, both in front of the leaves and in the niche.
     - In the current box it found **0**.
   - **What happened.** Knockback from the 808s pushed the Avatar there, and the trigger fired with the doors locked. I discarded that arrival.
   - **Classification.** Not a current-build defect. Any checkpoint taken before the 2783 change carries it until a map change. A map change (Map 9 T200 → Map 8) refreshed the fixed items, as `traps.md` says.
3. **The shape-808 pair did not respawn when I arrived from Map 9.**
   - **What I saw.** After T200 → Map 8 dest 200, `findShape 808` read 0 found, and the whole key/door sequence (about 2 min of game time) ran with no attacker.
   - **[INFERENCE]** MONFAST's `enterFastArea` hatches only while `mapArray & 0x80` is clear. Its `leaveFastArea` clears that bit, and that probably never ran when the map unloaded while the egg chunk was fast. If so, the flag stays set and the egg stays dormant.
   - **A player route past the 808s.** Get hit to Map 9, or arrive there any other way, then come back through T200.
   - **For a clean run.** Whether a fresh arrival from the corridor also leaves the bit set is untested.
4. **The first key use on the west leaf did nothing.** The target logged `Target result: Item 8428 … q: 1635`, but q stayed 1635. A second identical use set it to 611 (0x263). The east leaf unlocked on its first use (1123 → 99).
   - **[INFERENCE]** The Avatar was at (20279,3239). KEYRING calls `canReach(target, 128)` with line of sight, and the first click's screen point may have hit the leaf at a spot whose line of sight was blocked. The leaf bark is transient and was not captured.
   - **Classification.** Not a blocker.
5. **MISSTRAP lanes also hit at the gap.** The first corridor run took 25 hp at about (18250-18460, 5032-5240) before spitter 2's earliest bomb time was possible: the run stopped, then slid. The identical second run took 0. Crossing the x≈18431 lane is a dice roll; reload and retry.
6. **Per-level erosion breaks mixed-level terrain.** `pathfind.eroded_mask` erodes each z level separately. Where a floor alternates z 0 and z 8, for example the bone piles in the doors chamber or the Map 11 Fire causeways, erode ≥ 1 opens a gap between level masks and the router returns NO PATH, although the engine walks it. I used erode 2 for the corridor and the lane, and erode 0 with hazard margins in the chamber and on the Fire leg.
7. **STALEGG drop sites become solid stalagmites in the SP3 corridor.** STALEGG (class 049D, eggs q 30 at (22074,7198), (22542,7298), (22694,7178) and (22968,7328)) leaves STALAG 330 (64×64×32, SOLID). After the first one dropped, a run east at y 7256 stopped on the stalagmite at (22074,7198) and stalled beside the rock at x 22175, inside SP3's zone. Run at y ≥ 7300 past x 21900.
8. **The Map 11 monster eggs are avoidable.** Shape-500 eggs with npcnum 1 hatch only on the egg's own column (x ±0 × y ±32). Routing with those boxes forbidden took the Avatar to three talismans with no hatch and no damage.

## Harness anomalies

- **Short presses do nothing.** Held-run legs under about 0.4 s are dropped. The same goes for a 45° leg that starts a run. The `nav.py` replan loop therefore oscillates on routes whose last leg is a short jog.
- **Prime click.** The first mouse press after a `loadGame` is swallowed. A single left click (a look) at (320,150) before the first run fixed it reliably. A prime walk does not, because it is the press that gets swallowed.
- **Projection base.** The camera puts the Avatar's anchor at window (320,228) in 320×200 ×2, not at (320,200). Clicking an object's anchor projection, minus about 15/25 px, hits it.
- **"Saving game is currently unavailable"** appears while a hostile is engaging. `saveGame` then fails silently, so check the slot mtime.

## Checkpoints (all new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `run1010-s03x-m9-via-stale-t201-SKIP.sav` | `f2ea1567…` | Map 9 (13696,14208), hp 23, reached via the stale T201 box. **Evidence only, not a resume point** |
| `run1010-s03a-m8-door-niche-current-fixed.sav` | `3d234d7a…` | Map 8 dest 200 (20111,3175,8), hp 26. Current fixed items, no 808s present, doors locked, key still in the chest |
| `run1010-s03b-m8-doors-unlocked-open.sav` | `1fef59eb…` | Map 8 (20279,3239,8), both leaves unlocked and open (TDOOR_NS), chest gump open |
| `run1010-s03c-m9-arrival-via-doors.sav` | `0a52588c…` | Map 9 (13696,13760,0), hp 28, **step 3 done properly** |
| `run1010-s03d-m11-arrival.sav` | `5b36f832…` | Map 11 pad 203 (9728,1792,0), hp 29 |
| `run1010-s04a-m11-earth-air-talismans.sav` | `e1aaa532…` | Map 11 (17024,5184,0), hp 30, weight 40, holding the Earth and Air talismans |
| **`run1010-s04b-m11-three-talismans.sav`** | `96b151ad…` | Map 11 (6212,18204,0) in the Water section, west side, hp 30, weight 50, holding the Earth, Air and Water talismans. **Resume point** |

## Resume here

1. **Setup.** Use a 320×200 ini. Load `run1010-s04b-m11-three-talismans.sav` and send `debugflag_enable Object`. Then one look-click at (320,150).
2. **Fire talisman** (5631,18943,4).
   - Enter through the Fire doorway (y 16384..16896, x≈6144) from the Water section, on the E-W causeway (y 16640..17023).
   - Follow the N-S spine (x 3328..3711), then the row-35 branch (y 18688..18815).
   - Forbid lava 318 and flames 435-437 plus margins: `vrun4/m11forbid2.pkl` holds them along with the shape-500 egg boxes.
   - Daemon eggs: (2048,15104), (4608,15360), (3072,16896), (5120,17920) and (2048,18944).
   - Approach from the north and drag the talisman onto the Avatar.
3. **Pillars chamber** (6144-10240, 19456-22528).
   - Stand within about 64 of each receptacle, close the pack, and double-click the socket.
   - Pairs: Earth pillar ← Air, Air ← Earth, Fire ← Water, Water ← Fire.
   - Then go through the opened doorway x 8448..8704 to T205 (8960,23296) → Map 10 (step 4 complete). After that, follow `/tmp/claude-1000/run1009/route-guide.md` from step 5.

## Disk changes

- **Wrote** this report and its plates in `docs/playtest-2026-10-10-full-run-part4/`: `s03-01…06`, `s03-04b`, `s03-06b`, `s03-m9-arrival-proper`, `s03-m11-arrival`, `s04-01` and `s04-three-talismans`.
- **Wrote** the 7 checkpoints above in `~/lv-checkpoints/`.
- **Scratch** in `/tmp/claude-1000/vrun4/`: `game/`, `saves/`, `sp/` (screens and `w-*.sav`), `py/` (`v4.py`, `nav.py`, `plan*.py`, `zones.py`, `sim.py`), `lv_run.log`, `trace.txt`, `scummvm.ini`, `er8.pkl`, `flood2.*`, `zones.png`, `chamber.png` and `m11forbid*.pkl`.
- **Stopped:** my ScummVM and Xvfb `:95`.
- **Not touched:** source, builders, maps, the fork, `TODO.md`, `HANDOFF.md` and `shared/`.
