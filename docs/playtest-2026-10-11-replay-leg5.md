# Single-build replay of the 1→18 run, leg 5: steps 13-18 done. The replay is COMPLETE (2026-10-11)

This is leg 5, the last leg of the one-build replay. It continues from leg 4's banked save (`docs/playtest-2026-10-11-replay-leg4.md`) on the same pinned game copy, and it finishes the quest. With legs 1-4, the whole no-cheats 1→18 run has now been played on one build.

## Build pinned (re-checked)

- **Game copy.** `/tmp/claude-1000/replay/game`, as legs 1-4 left it; it was not re-copied. Running `sha256sum -c ../pinned.sha256` inside it gave OK for all six files at the start (22:24) and at the end (23:51): EUSECODE `4182e079…`, FIXED (root and `STATIC/`) `122b4374…`, U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…`, ANIM `77e9705d…`.
- **Binary.** `/tmp/claude-1000/pinned-bin/scummvm-4182e079` (sha256 `1502d576…`). One process ran the whole session. The log (`replay/lv_run5.log`, 18,114 lines) reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)`, `usecode/eusecode.flx: d00d0d5962e966129c2277c7cea7844b, 1526311 bytes` and `Setting Video Mode 320x200...`.
- **Harness.**
  - The ini is the same (320×200, music on, `SDL_AUDIODRIVER=dummy`), on Xvfb `:95`.
  - The driver is leg 1's `rp.py`/`navr.py` from the eval kernel, with `rp.PRIME=False`. `rp.start` was replaced in the kernel by one that launches the pinned binary.
  - **Lattices were built from the pinned files.** `navr.get_er` was replaced in the kernel by one that calls `exact_reach.load_map(m, fixed=game/STATIC/FIXED.DAT, typeflag=game/STATIC/TYPEFLAG.DAT)` (leg 4 note 5). They were kept in memory only; no `er_*.pkl` was written or read.
  - Menus were read from the screen. Menu rows are the exact menu red (213,48,49), and two or more rows share a bullet column. Every pick is on a plate.
- **Cheats: 0.** `Cheat` appears 0 times in `lv_run5.log`. The console was used only for `objectInfo`, `findShape`, `getGlobal`, `debugflag_enable Object` and `saveGame`. There were no loads.
- **Deaths: 0.** hp was 30 at every read.

## Outcome

- **The quest is complete.** The final state (`replay1011-s18c-…`):
  - godsFree 1038 = 1, endgameStarted 1814 = 1, hasBag 1037 = 1, templeOpen 1042 = 1, shieldFixed 1033 = 1, avatarPoisoned 1028 = 0.
  - Ezrekal's bag 17099 (shape 637, q1, `f: 0xc`, vol 18/32) holds six shape-395 stacks of q25, in frames 0, 6, 8, 9, 10 and 14. Weight 240, hp 30.
  - The Avatar is at Map 10 (13120,13808,0), just outside Ezrekal's garden.
- **Taken with leg 4's (`docs/playtest-2026-10-11-replay-leg4.md`), the two-sided rule held.** Every step of 1-18 was reached by input on build EUSECODE `4182e079` / FIXED `122b4374`.

## Verdicts

| Step / leg | Verdict | Evidence |
|---|---|---|
| 13: Map 13 descent | **PASS, 0 falls** | Erosion-0 lattice from the pinned FIXED, with 1.0 s legs: (4096,512,120) → (4128,3016,100) → (4592,5120,68) → (5052,5476,60) → (4348,5884,52) → (3952,8136,20) → (4088,10544,0). There was no `DROP` and hp stayed 30. One stall at (4348,5884,52): running was refused, and walking freed it (finding 7a) |
| 13: Map 13 → Map 10 (teleporter 206) | **PASS** | (3956,11060) → W/SW → **Map 10 (7064,23296,8)** (`A1`). `findShape 539` showed both halves, q81 and q82, `f: 0xc` |
| 14: to the Sacred Circle | **PASS** | Terrace → (9216,21584) → E along y 21476 (lake to the N) → (16236,21316) → NE → (20312,17744). The lattices were erosion 0 with the default 128-unit water margin |
| **14-15: the ceremony** | **PASS** | A 1.2 s walk N logged `Item: 7773 (shape 73) … event 7 @ 05A5:0080`. Then the elders' quarrel (`B1`). The menu "Can't you two get along!? / Let's be reasonable!" → **Let's be reasonable!** (`B2`). Then "Yes, Priestess. / No, … is mine now." → **Yes, Priestess.** (`B3`). The halves were laid down and fused, and the shades of Hoskuld and Gunnar spoke (`B4`, `B4b`). Then "Please, High Priestess. / No, thanks anyway." → **Please, High Priestess.** (`B5`). Ezrekal's barks followed: "I feel better... But I'm still so weak!" (`B6`) and "I take up the Shield of the Ancients. Its place is on the temple altar." |
| 15: state after the ceremony | **PASS** | shieldFixed 1033 = 1, avatarPoisoned 1028 = 0, inShadeScene 1106 = 1 at the first read (`B7`) and **0** about 60 s later (`B8`), finding 3. `findShape 828`: item 25423, **q83**, `f: 0xc` (in the pack). Weight went 110 → 60 |
| 16: Hrodny, first talk | **PASS** | NPC 113 was at (21639,8447), beside her hut. The double-click logged `event … @ 0471`. Menu "What is your name? / What do you do? / bye" (`C1`) → What is your name? → "Hrodny, daughter of Ulrar, I am." → bye. hrodnyMet 1116 = 1 |
| **16: Hrodny, the errand** | **PASS** | Talk 2: **I have been healed! / The Shield of the Ancients is restored! / bye** (`C2`) → I have been healed! → **How can I open the temple? / bye** (`C3`) → the potions-and-lost-key story. It closes with "Seen something, the children have. A thief-thing, dragging a bright small weight up the old temple road, southward…" (`C4`). spokeTemple 1782 = 1 (`C5`). Bag 29472 appeared at **(19588,23284,0)** holding key 29471, q20 |
| 16: the bag | **PASS** | I walked there along x≈20300 (route below). The bag was on the grass (`C6`). The drag logged `Dragging item 29472` → `Dropped item in backpack`, and weight went 60 → 80 |
| **16: the spare key** | **NOT PRESENT on this build** (finding 1) | `findShape 82` on Map 10 lists only key 4185 (q170, in the pack) and 29471 (q20, in her bag). The pinned `game/STATIC/FIXED.DAT` holds **no shape-82 record on Map 10**. Nothing was at (22016,6144) |
| **16: the chest, with HER key** | **PASS** | The first try logged `Target result: … shape 618` and showed "can't reach" from (20964,9040). The second try, from (20904,8884), went: pack → bag → double-click key 29471 (`event 1 @ 0052:04BB`) → click the chest. `findShape 78`: **item 19766 is now CHEST_EW, shape 78**, and 618 reads 0 (`D1`). The double-click logged `event 1 @ 004E:00A9` and the TRAP `event 1 @ 02F4:0080`, with no damage. Three drags out of the chest gump each logged `Dropped item in backpack` (19626, 19557, 19627; all shape 859, frame 8). Weight went 80 → 110 |
| 17: Map 10 → Map 18 | **PASS** | Down x≈20300 → (18340,22968) → a 1.5 s walk S onto trigger 211 (18432,23552). `Unloading map 10` → `Loading Fixed items in map 18`, and the Avatar was at (3072,2024,0) (`A2`). On the way, EggEndgame hatched while godsFree was 0 (line 9015, `05AA`); see finding 2 |
| 17: crack hint | **PASS** | crackHintGiven 1829 = 1 on reaching (2896,5880). The bark itself was not captured |
| 17: negative control, full size at the sealed breach | **PASS** | From (2736,6056), two S walks stopped at (2716,6108). The wall line is y 6143, and templeOpen was still 0 (`E2`) |
| **17: crack with one Tiny Tar** | **PASS on the first potion** | From (2836,6108): pack → double-click potion 19557 (`event 1 @ 04E5:00A9`), "Something strange is happening to me." (`E3`, `E4`). Nine 0.5 s S bursts at mouse offset 200 took the Avatar (2872,6144) → (2872,6504). `objectInfo 1` read **shape 867**. **templeOpen 1042 = 1** (`E5`), and the bark read "Behind me the split stone groans and slumps, and the crack falls open into a gap a man could walk through." (`E6`) |
| 17: sanctum → altar | **PASS** | → (3080,6864,8) on the processional → (3248,7928,8), where it wedged (E and S refused; N moved it; finding 7c) → (3248,7728) → E to (3456,7728,0) → S to (3456,8640). The W walk did not hatch the egg; the **N 0.8 s walk did**: `Item: 10391 (shape 73) … event 7 @ 05A7:0080` |
| **17: AOSCENE, the Shield on the altar** | **PASS** | The console stayed closed for 80 s, with frames every 0.8 s (`F1`). "I place the artifact upon the altar. The ancient symbols begin to glow." (`F2`) → white fade → god pan with the shatters → "It is done. The Ancient Ones are free. I can feel their gratitude -- and their power." (`F3`) |
| 17: state after the altar | **PASS** | godsFree 1038 = 1, templeOpen 1, shieldFixed 1, poisoned 0 (`F4`). `findShape 828`: one Shield only, 25423 q83 at **(3056,8176,40)**, `f: 0x2004`. `findShape 860`: frames 4/3/5 for q302/q301/q303. Weight went 110 → 80 |
| 18: out through the breach at full size | **PASS** | From (2736,6368) at shape 1, a N walk reached (2808,5992) (`G1`). The two remaining Tiny Tars were not needed |
| **18: Map 18 → 10 and EggEndgame** | **PASS** | (3064,1712) → N walk → `Unloading map 18` → `Loading Fixed items in map 10`. The landing hatched `05B2:0080` and **EggEndgame `Item: 26305 (shape 73) … event 7 @ 05AA:0080`** at log line 16657 |
| **18: all six closing barks** | **PASS** | The scene ran untouched for 190 s, with frames every 0.7 s (`H0`). Each bark was on screen for about 12-16 s: "With the Ancient Ones freed, their power flows through the land. The Vale begins to change." (`H1`), "Green returns to the withered earth. Water flows where dust once lay. The vale is healing." (`H2`), "The Zealans gather around me. Their faces show something I have not seen here before -- hope." (`H3`), "An elder steps forward. Though I cannot understand all the words, the meaning is clear. They are thanking me. The Vale is restored." (`H4`), "And with the power of the Ancient Ones now restored, I feel the path to Britannia opening before me at last." (`H5`) and "The Guardian's prison weakens. It is time to go home." (`H6`). Then a fade to black (frames 107-109, `H7`) and back to play (`H8`). Both closing lines show before the fade |
| 18: state after the endgame | **PASS** | endgameStarted 1814 = 1, hasBag 1037 = 0, godsFree 1 (`H9`). The Avatar was at (18432,22784,0), and a W 1.0 s walk moved him 304 units, so stasis was released |
| 18: to Ezrekal | **PASS, hp 30** | Erosion-2 pinned lattice, then corner waypoints with ≤1.6 s bursts: (18032,22784) → N to (18032,17624) → NW to (15560,15152) → W to (14536,15224) → NW to (13120,13808). Ezrekal (NPC 116) was in her garden at (13183,13727) |
| **18: "I have freed your gods!"** | **PASS** | Menu "I have freed your gods! / I would speak to you of Tyorvi. / bye" (`J1`) → "What a wonderful time this is! Once again be able to fulfill my duties as High Priestess I will! Nothing there is I can give you to repay you for your trouble, but" (`J2`) / "this I can give you there is. A magical bag it is. Provide you it will with any magical reagents you need. Take it, with our heartfelt thanks!" (`J3`). Both pages were captured this time. hasBag 1037 = 1 (`J4`), and the bag is as in Outcome. Weight went 80 → 240 |
| 18: negative control, second pick | **PASS** | The same option on a second talk gave "Yes yes! I know! Wonderful it is. I know not enough to repay you the bag I gave you is. Thank you again for your help. Now, much there is for me to do. If excuse…" (`J5`). `findShape 637` still lists exactly one q1 bag (17099), and the weight stayed 240 |
| Music on | **PASS (no hang)** | 85 min of play; the console answered throughout |
| Log hygiene (`lv_run5.log`) | **PASS** | 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Cycle in paint` and ERROR. There was **1** `Unhandled intrinsic 254 'isGameRunning()'`, at the chest open, which is the known `I_true` stub (as in part 6 and the key-removal check). The other 3 WARNINGs are startup lines (theme, translations, gui-icons). There are also 349 `LV: I_resetRef item=… type=…` debug lines, all from the ceremony, with elders 106 and 107 and egg 7773 |

## Findings

1. **The spare q20 key is not on this pinned build, so the brief's premise is wrong. On this build, Hrodny's errand is the only way into the chest.**
   - **What I found.** The pinned FIXED `122b4374` *is* the post-removal FIXED. `docs/playtest-2026-10-11-key-removal.md:3,15` records the change: FIXED went `eff07302` → `122b4374` when the shape-82 q20 record at (22016,6144,0) was removed.
   - **Two ways I checked.**
     - Reading `game/STATIC/FIXED.DAT`'s Map 10 directly finds no shape-82 record.
     - In-engine, `findShape 82` lists only the Key to the Clouds and the key in her bag.
   - **What I used.** HER bag key 29471. I did not see a spare.
2. **EggEndgame re-arms on map re-entry. Part 6 marked this [INFERENCE]; it is now observed.**
   - **First hatch, a no-op.** The walk down the processional crossed its box with godsFree 0. That hatched `05AA` as a no-op (log line 9015), and nothing ran.
   - **Second hatch, the real one.** After Map 18, the trigger-210 landing hatched it again (line 16657), and the whole scene played.
   - **So** crossing the box early does not spend the finale.
3. **inShadeScene (1106) lags the ceremony's end.** It read 1 at the first query after "I take up the Shield…" and the elders walking off, and it read 0 about 60 s later. Part 6 read 0. Low severity; nothing gates on it here.
4. **One Tiny Tar did the whole temple, both ways.**
   - **This run.** The first potion took the Avatar through the crack (nine 0.5 s bursts at mouse offset 200, x 2872). Part 6 needed a second potion.
   - **The way out.** The breach let him out at full size at x 2736-2808, which reproduces part 7 finding 3. The two spare Tiny Tars are still in the pack.
5. **Hrodny's errand reads well as a player experience.** Her reply ends by pointing the player south down "the old temple road", and the bag sits in the open on the grass beside that road at (19588,23284) (`C6`).
   - **The cost.** The chest → bag → chest round trip is about 14,400 units each way across the Vale, the longest walk in steps 14-18.
   - **The menu.** After "I have been healed!", the "Shield of the Ancients is restored!" option dropped out of the menu, and "How can I open the temple?" took its place.
6. **The chest's "can't reach" range is tighter than it looks.** From (20964,9040), about 210 units from the chest's anchor, the key's target click gave "can't reach". From (20904,8884), right beside it, the key worked. A player sees the bark and steps closer, so this is a note only.
7. **Three spots where a held run stalls (harness or retail, low severity).**
   - a. **Map 13 (4348,5884,52)**, on the descent. A run W was refused for a dozen rounds; a walk W/SW at mag 110 freed it at once. This is the traps.md "a running Avatar refuses the 8-unit step" pattern on the cliff ledges.
   - b. **The Map 10 fence at (20752-20760, 11220-11228)**, south of Hrodny's hut. S was refused at x 20752 and 20760, both times I came this way. The erosion-1 lattice built from the pinned FIXED routes S through that point. A W step to x 20656 passed at once. [INFERENCE: a lattice-versus-engine disagreement at one fence post. I did not trace it, and I did not run `exact_reach` on the aperture.]
   - c. **Map 18 (3248,7928,8)**, on the processional beside the candelabrum. E and S were refused and N moved. This is the same spot part 6 stalled at. Detour: N to (3248,7728), E to x 3456, then S.
8. **Ragnar's step-7 bag is still on the ruin dais**: (16447,25727,64), `items: 1`, weight 20. It was outside this leg's scope. I note it only because it appears in every `findShape 637` beside the quest bags.

## Harness anomalies

- **The first input after a console close is swallowed** (part 6 finding 4). A 0.3 s sacrificial press before each walk worked. Exact positioning moved about 200 units per 0.7 s walk, so I made fine steps with a 0.3 s press followed by a 0.45 s one.
- **`getGlobal` replies were read from console screenshots** (`B7`, `B8`, `C5`, `E5`, `F4`, `H9`, `J4`). They do not reach the log.
- **NPC strikes.** The projected point −30 px y, after a sacrificial right press, hit Hrodny 2 times out of 3 tries and Ezrekal 2 times out of 4.
- **Replans on a large ROI are slow.** Whole-ROI Map 10 lattices took 10-22 s per route; corner-waypoint following avoided replanning.
- `saveGame` worked every time (13 of 13).

## Checkpoints (all new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `replay1011-s13e-m10-back-with-halves.sav` | `72c8b7ed` | Map 10 (7064,23296,8) after pad 206, both halves. **Step 13 done** |
| `replay1011-s15-m10-shield-restored-cured.sav` | `303f5d53` | Sacred Circle (20476,17092), shieldFixed 1, cured, Shield 828 in the pack |
| `replay1011-s16a-m10-hrodny-bag-key-in-pack.sav` | `3c3e8a15` | (19616,23228), 1116/1782 = 1, Hrodny's bag (key q20) in the pack |
| `replay1011-s16b-m10-three-tiny-tar-bag-key.sav` | `d4acc2b6` | At the chest (20904,8884), chest now shape 78, three Tiny Tars in the pack, w 110. **Step 16 done** |
| `replay1011-s17a-m18-arrival.sav` | `4aedac16` | Map 18 (3072,2024,0) |
| `replay1011-s17b-m18-temple-open.sav` | `e9bb0a39` | Map 18 (2872,6504,0) inside, shrunk, templeOpen 1, two Tiny Tars left |
| `replay1011-s17c-m18-pre-altar.sav` | `e16e44a0` | Map 18 (3456,8640,0) south-east of the dais, godsFree 0. Rerun point for the altar |
| `replay1011-s17d-m18-gods-free.sav` | `aecf91ce` | Map 18 (3256,8544), godsFree 1, Shield on the altar. **Step 17 done** |
| `replay1011-s18a-m18-pre-exit-gods-free.sav` | `afa9433a` | Map 18 (3064,1712) just south of trigger 210, endgameStarted 0 |
| `replay1011-s18b-m10-endgame-done.sav` | `80090b4a` | Map 10 (18128,22784), endgameStarted 1, hasBag 0 |
| **`replay1011-s18c-m10-reagent-bag.sav`** | `a49eff59` | Map 10 (13120,13808) outside Ezrekal's garden, hasBag 1, six q25 stacks. **Final state of the replay** |

Scratch saves are in `/tmp/claude-1000/replay/sp/l5-*.sav`.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-replay-leg5/`, which holds 44 plates: `A1-A2`, `B1-B8` (with `B4b`), `C1-C6`, `D1`, `E1-E6`, `F1-F4`, `G1`, `H0-H9` and `J1-J5`.
- **Wrote** the 11 checkpoints above in `~/lv-checkpoints/`.
- **Scratch** in `/tmp/claude-1000/replay/`:
  - `lv_run5.log`, `trace5.txt`, `sp/l5-*.sav` and the working frames `sp/*.png`;
  - `saves/ultima8.001`, which now holds the final state.
  - No lattice cache files were written; all lattices lived in the kernel.
- The game copy is unchanged; its hashes were re-checked at the end.
- **Stopped:** my ScummVM (pid 1233985, `pinned-bin/scummvm-4182e079 --config=/tmp/claude-1000/replay/scummvm.ini`) and my Xvfb `:95` (pid 1233972). Other agents' Xvfb (`:92`, `:93`, `:94`, `-displayfd`) and their ScummVMs (`vmon2`, `vgate2`) were left alone.
- **Not touched:** source, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, and both binaries.
