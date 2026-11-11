# Single-build replay, leg 6: steps 16-18 done (Hrodny's errand and the three Tiny Tars, the rebuilt Map 18 sanctum and the 879 Shield on the altar, the endgame and Ezrekal's reagent bag). The replay is COMPLETE (2026-10-18)

Leg 6 continues from leg 5's bank `replay1017-s15-m10-shield-879-restored-cured-hp30.sav` (`docs/playtest-2026-10-17-replay-leg5.md`), on the same pinned game copy. It finishes the quest.

## Build pinned (re-checked)

- **Game copy.** `/tmp/claude-1000/replay1017/game` was not re-copied or modified. `sha256sum -c ../pinned.sha256` gave OK for all six files at the start and at the end: EUSECODE `2e3b71c2…`, FIXED (root and `STATIC/`) `8db11ee3…`, U8SHAPES `efb16af1…`, TYPEFLAG `d26d1531…`, ANIM `696dbeb9…`.
- **Binary.** `/tmp/claude-1000/replay1017/bin/scummvm-console`, the same file as legs 1-5. The log reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `usecode/eusecode.flx: 84615e29d097543ed69da844fbc3948f, 1528891 bytes.`
- **Ini.** `scummvm.ini` unchanged: 320×200, `scale_factor=2` (window 640×400), `usehighres=true`. Xvfb `:95`.
- **Log.** `/tmp/claude-1000/replay1017/lv_run6.log` (13,890 lines, one process for the whole leg). The trace is `trace6.txt`.
- **Cheats: 0.** `Cheat` appears 0 times in the log. The console was used only for `objectInfo`, `findShape`, `getGlobal`, `debugflag_enable Object` and `saveGame`. There were no loads after the start. Every move, drag, door, potion and menu pick was player input. The Map 10 → 18 and 18 → 10 crossings were walked into.
- **Deaths: 0. Reloads: 0.** hp was 30 at every read.

## Outcome

- **The quest is complete.** The final state (`replay1017-s18c-m10-reagent-bag-hp30.sav`):
  - godsFree 1038 = 1, endgameStarted 1814 = 1, hasBag 1037 = 1, templeOpen 1042 = 1, shieldFixed 1033 = 1, avatarPoisoned 1028 = 0.
  - Ezrekal's bag **22089** (shape 637, **q1**, `f: 0xc`, vol 18/32, weight 160) holds six shape-395 (ERTHREAG) stacks of **q25**, in frames **0, 6, 8, 9, 10 and 14** (items 22087, 22084, 20796, 20716, 20328, 20092). That is the same six frames 10-11 leg 5 recorded.
  - The Avatar is at Map 10 (12676,13263,0), just outside Ezrekal's garden. hp 30, weight 270.
- The restored Shield **879** (item 2680, q83) is on the Map 18 altar at **(3111,8167,16)**, `f: 0x2004`.

## Verdicts

| Step / segment | Verdict | Evidence |
|---|---|---|
| Resume | **PASS** | `s15` loaded by `--save-slot=1` at (20496,17088,0), hp 30, w 90. shieldFixed 1, poisoned 0, hrodnyMet 0, spokeTemple 0 (`s15-resume-start`) |
| 16: to Hrodny | **PASS** | An erode-1 field from the Circle N to her hut. NPC 113 was wandering around (21636-22032, 7834-8338) |
| **16: Hrodny, first talk** | **PASS** | Strike `event 1 @ 0471:0D5B`. Menu "What is your name? / What do you do? / bye" (`s16a`) → **What is your name?** → "Hrodny, daughter of Ulrar, I am." (`s16b`) → menu "What do you do? / bye" → **bye**. hrodnyMet 1116 = 1 |
| **16: Hrodny, the errand** | **PASS** | Talk 2: "I have been healed! / The Shield of the Ancients is restored! / bye" (`s16c`) → **I have been healed!** → "See, so I do! For you, good! Perhaps something to these god stories, there is. So now, open the temple, will you?" (`s16d`) → menu "How can I open the temple? / bye" (`s16e`) → **How can I open the temple?** → the potions-and-lost-key story, ending "Seen something, the children have. A thief-thing, dragging a bright small weight up the old temple road, southward. Laughed at them, I did. Laugh now, I do not. Look along that road, I would, if you, I were." (`s16f`, `s16g`). spokeTemple 1782 = 1. Bag **17317** appeared at **(19588,23284,0)** holding key **23296, q20** |
| 16: the bag | **PASS** | The field ran S down x 20640 → 19588 to (19676,23196). The bag lay on the stone road (`s16h`). The drag logged `Dragging item 17317` → `Dropping object 17317` → `Dropped item in backpack`, w 90 → 110 (`s16i`). Bank `s16a` |
| **16: HER key on the chest** | **PASS on the second try** (finding 1) | The chest is **30050 LCHST_EW (618) at (21216,8768,0), inside a hut**. Try 1, from outside at (20868,8892): pack → bag (`s16k`) → double-click key 23296 (`event 1 @ 0052:04BB`) → click the chest's screen spot. `Target result: Item 27712 (shape 412)`, the hut's roof (`s16j`). Try 2: I walked in through the hut's south doorway (x ≈ 21088, y 9180 → 8920) to (21196,8924), where the roof is cut away (`s16l`). Key → chest gave `Target result: Item 30050 … shape 618`. `findShape 78`: **30050 is now CHEST_EW (78)**, and 618 reads 0 (`s16m`) |
| **16: the three Tiny Tars** | **PASS** | The chest double-click logged `event 1 @ 004E:00A9`, one `Unhandled intrinsic 254 'isGameRunning()'` (the known stub) and the trap `Item: 30049 (shape 756) … event 1 @ 02F4:0080`, with no damage (hp 30). The chest gump showed three potions (`s16n`). Three drags onto the Avatar's sprite each logged `Dropped item in backpack`: 30048, 28748, 29636, all **859 f8**, `f: 0x200c`. w 110 → 140 (`s16o`). Bank `s16b`. **Step 16 done** |
| 17: Map 10 → Map 18 | **PASS** | A field S along x 20072, then W along y 23800. A NW walk from (18720,23808) entered teleporter **508 q467 (id 211) at (18432,23552)**: `Unloading map 10` → `Loading Fixed items in map 18`, Avatar at **(2968,1688,0)** (`s17a`). Bank `s17a` |
| 17: the hall and the crack hint | **PASS** | Lattice from the pinned FIXED: S down the hall (x 2968 → 3184, y 1688 → 6072), then W to (2836,6044). The hall logged `0481:0080` (trigger 26183 at (3072,2752)) then `0481:011D` (event 16); no monster appeared. Then `05B1` ×2. **crackHintGiven 1829 = 1** (`s17b`). The bark itself was not captured |
| 17: negative control, full size at the crack | **PASS** | From (2908,6064), two 1.2 s S walks stopped at **(2908,6108)**. The wall line is y 6143, and templeOpen stayed 0 (`s17c`) |
| **17: the crack, one Tiny Tar** | **PASS on the first potion** | I set x into the tiny band with a NW diagonal step: (2916,6108) → **(2872,6064)**. Straight walk steps came in ~100-unit quanta (2908 → 2812 → 2916). Pack → single-click to identify `Item 29636 … shape 859, 8` → double-click: `event 1 @ 04E5:00A9`, "I'm feeling funny." (`s17d`), then "Something strange is happening to me." (`s17e`). `objectInfo` read **shape 867** at (2872,6096). Thirteen S bursts at mouse offset 200 took the Avatar through to **(2872,6376)**. The temple-entry egg logged `Item: 13700 (shape 73) … event 7 @ 05B0:0080`. **templeOpen 1042 = 1** (`s17f`). The "split stone groans" bark was not captured. Bank `s17b` |
| 17: shrine → altar | **PASS** (finding 5) | The field went (2872,6376) → SE (3576,7088) → S (3576,7920) → W (3332,7876). One amber god was visible on its plinth beside the bare altar (`s17g`). Bank `s17c`. Two 1.0 s S walks at x 3332 went to y 8572 **without** hatching the altar egg. A 0.55 s W walk then logged **`Item: 16475 (shape 73) … event 7 @ 05A7:0080`** |
| **17: AOSCENE, Shield 879 on the altar** | **PASS** | The console stayed closed for 100 s, with frames grabbed every 0.8 s (31 distinct frames, `s17l`, `s17m`). "I place the artifact upon the altar. The ancient symbols begin to glow." (`s17h`) → white fade (`s17i`) → camera visits to the three gods, each shattering out of the amber (`s17j`) → "It is done. The Ancient Ones are free. I can feel their gratitude -- and their power." (`s17k`) |
| 17: state after the altar | **PASS** | **godsFree 1038 = 1**, templeOpen 1, shieldFixed 1, poisoned 0. `findShape 879`: one item, 2680 q83 at **(3111,8167,16)**, `f: 0x2004`. `findShape 860`: 16432 f4 q302 at (3039,7903,16), 16433 f3 q301 at (2783,8031,16), 16481 f5 q303 at (3039,8415,16). w 140 → 110 (`s17n`). Bank `s17d`. **Step 17 done** |
| 18: out through the breach at full size | **PASS** | Shape 1 at (2804,6324): one 1.5 s N walk reached **(2804,5828)** (`s18a`). The two spare Tiny Tars were not needed |
| **18: Map 18 → 10 and EggEndgame** | **PASS** | Field N up the hall to (3008,1752); bank `s18a`. A 1.6 s N walk: `Unloading map 18` → `Loading Fixed items in map 10` → `05B2:0080` → **EggEndgame `Item: 9869 (shape 73) … event 7 @ 05AA:0080`**. The Avatar landed on pad 210 at **(18432,22719,112)** |
| **18: all six closing barks** | **PASS** | Untouched for 215 s, frames every 0.7 s (149 distinct frames). "With the Ancient Ones freed, their power flows through the land. The Vale begins to change." / "Green returns to the withered earth. Water flows where dust once lay. The vale is healing." (`s18b`) / "The Zealans gather around me. Their faces show something I have not seen here before -- hope." / "An elder steps forward. Though I cannot understand all the words, the meaning is clear. They are thanking me. The Vale is restored." / "And with the power of the Ancient Ones now restored, I feel the path to Britannia opening before me at last." / "The Guardian's prison weakens. It is time to go home." (`s18c`) |
| 18: state after the endgame | **PASS** | endgameStarted 1814 = 1, hasBag 0, godsFree 1. Bank `s18b`. A S walk moved him off the pad (18432,22719,112) → (18496,23015,64), so stasis was released |
| 18: shelf → Ezrekal | **PASS, hp 30** (finding 3) | The shelf stair descends S, slowly (about 20-40 units per walk press), to a foot beside trigger 211. A walk there wedged at (18524,23251,8): S, E and SE were refused, and N freed it. A step-8 lattice with trigger 211's box forbidden routes off the foot **only to the east** (x ≥ 18924), round the box. I walked that way, then N/NW across the Vale (x 20164 → 16448 → 13544) to (12676,13263). Ezrekal (116) was in her garden |
| **18: "I have freed your gods!"** | **PASS** | Strike `event 1 @ 0474:034A`. Menu "I have freed your gods! / I would speak to you of Tyorvi. / bye" (`s18e`) → **I have freed your gods!** → "What a wonderful time this is! Once again be able to fulfill my duties as High Priestess I will! Nothing there is I can give you to repay you for your trouble, but" / "this I can give you there is. A magical bag it is. Provide you it will with any magical reagents you need. Take it, with our heartfelt thanks!" (`s18f`). **hasBag 1037 = 1**. w 110 → 270 (`s18g`). Bank `s18c` |
| 18: negative control, second pick | **PASS** | Talk 2, the same menu (`s18h`) → **I have freed your gods!** → "Yes yes! I know! Wonderful it is. I know not enough to repay you the bag I gave you is. Thank you again for your help. Now, much there is for me to do. If excuse me you will?" (`s18i`). `findShape 637` still lists exactly one q1 bag (22089), and the weight stayed 270 |
| GHOST 411 follower | **Not seen** | `findShape 411: 0 found` on Map 18 after the altar, and again on Map 10 at the end |
| Log hygiene (`lv_run6.log`) | **PASS** | 0 `stuck in process loop`, 0 Segmentation, 0 Assertion, 0 `Non-existent process`, **2** `Unhandled intrinsic` (both 254 `isGameRunning()`, the known `I_true` stub: one at the chest open, one when a double-click on the chest gump's frame re-used the chest to close it), 0 `Cycle in paint` (finding 4), 0 ERROR, 0 `Cheat`. The other 3 WARNINGs are startup lines (translations, gui-icons, theme). 187 `LV: I_resetRef` debug lines |

## What the rebuilt Map 18 did differently from 10-11 leg 5

- **Arrival.** The Avatar landed at (2968,1688,0) after a NW walk-in from the SE. 10-11 landed at (3072,2024) and verify3 at (3072,1792).
- **Hall.** The lattice route ran along x 3184 rather than x 3015. The hall's monster trigger 0481 at (3072,2752) fired (events 7 and 16), and no monster appeared. On 10-11 the golem was destroyed off-screen.
- **Crack.** It behaved the same: crackHintGiven was set on approach, full size was refused at the wall line, and one Tiny Tar was enough. The Avatar read shape 1 again at the first position read inside, (2872,6376). That read came about 15 s after the drink, with the `05B0` temple-entry egg logged in between (finding 6).
- **Sanctum.** This is the 1994 screen04 cave shrine, with amber god statues on plinths (`s17g`). The 10-11 processional wedge at (3248,7928) did not occur on this route.
- **Altar egg.** Egg 16475 (q296, range 6×6 → x 2880-3264) is at (3072,8320). A S walk at x 3332 passed the whole y range without hatching it; a W step hatched it. On 10-11 the S approach at x 3456 also missed, and a N walk hatched it.
- **Shield.** It pops to (3111,8167,16), the new altar top. 10-11 had (3056,8176,40). The scene set godsFree within the 100-s window. The gods end on frames 4/3/5 at the verify3 spots.
- **Return.** The return lands on the **pad 210 shelf at z 112** (18432,22719). 10-11 landed at (18432,22784,0). The way off the shelf is a stair whose foot sits beside trigger 211 (finding 3).

## Findings

1. **Severity: low (UX). Hrodny's chest takes the key only from inside the hut.**
   - **The chest.** Chest 30050 (618 → 78) is at (21216,8768,0), inside the hut walled at x 21023-21503, y 8223-9087.
   - **From outside.** From (20868,8892) the key's target click landed on the roof, `Target result: Item 27712 (shape 412)`. The roof covers the chest's screen spot (`s16j`).
   - **The way in.** The hut's door gap is on its south wall at x ≈ 21055-21151. Inside, the roof is cut away, and the key works at once (`s16l`, `s16m`).
   - **10-11.** Leg 5 then used the key from (20904,8884), also outside the west wall. [INFERENCE: it aimed at an unroofed pixel; I did not reproduce it.]
   - **Blocker: no.** A player sees the roof and goes in.
   - **Repro.** `replay1017-s16a` → walk to (20868,8892) → bag key → click the hut roof.
2. **Severity: info. The Sacred Circle egg 28745 (`05A5`) hatched again after the ceremony, as a no-op.**
   - **When.** It logged at line 2941, as the field passed (20720,16996) on the return N with the bag.
   - **What ran.** shieldFixed was 1, and nothing ran: no barks, no elders, no stasis.
   - **Compare.** This matches the EggEndgame re-arm in 10-11 leg 5 finding 2. These scene eggs re-hatch and gate on their own flags.
3. **Severity: low (route; latent bounce). The pad 210 shelf's stair foot sits beside trigger 211.**
   - **The stair.** It goes S from the shelf (18432,22719,112) to a foot at about (18348-18428, 23275-23347, 0). It walks slowly, and it wedged once at (18524,23251,8): S, E and SE were refused, and N freed it.
   - **The box.** Trigger 211 is 508 q467 at (18432,23552), with npcnum 0xD3. [INFERENCE from the egg range encoding (xrange = npcnum>>4, yrange = npcnum&15, ×32): its box is x 18016-18848, y 23456-23648.]
   - **The lattice.** In a step-8 lattice from the pinned FIXED, the shortest route from the foot to the west (S 32, SW 240, W …) passes through that box. With the box forbidden, the only way off is east round it (x ≥ 18924).
   - **The consequence.** A player who walks off the stair S or SW toward the village would be teleported straight back to Map 18. I did not walk into it, so the bounce is NOT DEMONSTRATED.
   - **Blocker: no.** Map 18's hall leads back to pad 210.
   - **Repro.** `replay1017-s18b-m10-endgame-done-hp30.sav`.
4. **Severity: info (closes a known defect on this build). The finale logged 0 `Cycle in paint` on the pad 210 shelf.**
   - **The run.** The Object channel was on all leg: it was enabled at start, with no `loadGame` after. A click on shelf slab 11639 (shape 125) right after the scene logged its `dumpInfo`. The whole 215-s EggEndgame on the shelf then logged **0** knots.
   - **Before.** Vignettes-verify3 F1 logged 28,712 `125 -> 107` lines at this spot on FIXED `ab720e17`. Verify4 saw 1 transient `125 -> 1`.
   - **So** the knot does not reproduce on FIXED `8db11ee3` in normal play.
5. **Severity: info. The altar egg needs the body inside x 2880-3264.**
   - **What happened.** A S approach at x 3332 crosses y 7876 → 8572 without a hatch, and a W step hatches it.
   - **The trap.** A player coming down the east side of the sanctum walks past the altar until he turns toward it. This is the same shape as 10-11 (W did not hatch, N did).
6. **Severity: info. One Tiny Tar did the whole crack.**
   - **The first bursts.** Nine 0.5 s bursts moved the tiny Avatar only 6064 → 6096; four 0.6 s bursts then carried him through to 6376.
   - **Size.** By the first read inside, he was full size again, about 15 s after the drink.
   - **The way out.** He walked out at full size at x 2804.
   - **Spares.** Two Tiny Tars (28748, 30048) remain unused in the pack.
7. **Severity: info. No GHOST 411 follower was seen** (`findShape 411` = 0 on Maps 18 and 10).

## Harness anomalies

1. **Intermittent `ATTACH FAILED`.** It happened about 6 times. `lv.pos()`'s retry loop recovered every time, and no command was lost.
2. **Gump-to-gump drag did not store.** A potion dragged from the chest gump onto the pack gump's interior logged `Dropping object 30048` with no `Dropped item in backpack`, and it stayed in the chest. Dropping onto the Avatar's sprite stored all three. I moved the chest gump aside to uncover him.
3. **Closing a container gump by double-clicking its frame "uses" the owner.** For the chest that re-ran its use handler, which is the second `isGameRunning` warning. It did no harm.
4. **The eval cell's default 30 s timeout** interrupted the first follow mid-route; the Avatar simply stopped. Later cells set an explicit timeout.
5. **Follower `NO RAY`** happened twice, at z 8 off-lattice spots (Circle stones, the hut's west eave). One manual step resumed it.
6. **`py/` is unchanged.** The kernel-only helpers were `gdrag` (a gump drag with the drop log) and `sheet`/`tsheet` (contact sheets). The Map 18 lattice was `nav.get_er(18,(1500,1000,5000,10000),step=8)`. The Map 10 lattices were leg 5's `erA`, plus `erB`/`erS1`, which forbid trigger 211's box `(17990,23430,18920,23720)`.

## Checkpoints (all new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `replay1017-s16a-m10-hrodny-bag-key-in-pack-hp30.sav` | `e786e2a5` | (19676,23196), hrodnyMet/spokeTemple 1, her bag (key 23296 q20) in the pack, w 110 |
| `replay1017-s16b-m10-three-tiny-tar-chest-open-hp30.sav` | `32022d03` | Inside the chest hut (21196,8924), chest now 78, three 859 f8 in the pack, w 140. **Step 16 done** |
| `replay1017-s17a-m18-arrival-hp30.sav` | `4754c7ee` | Map 18 (2968,1688,0) |
| `replay1017-s17b-m18-temple-open-two-tiny-tar-hp30.sav` | `fe1e6a9c` | Map 18 (2872,6376,0) inside, templeOpen 1, two Tiny Tars left |
| `replay1017-s17c-m18-pre-altar-hp30.sav` | `061d2f68` | Map 18 (3332,7876,0), godsFree 0. Rerun point for the altar (step W, not S) |
| `replay1017-s17d-m18-gods-free-hp30.sav` | `551446e4` | Map 18 (3228,8572), godsFree 1, Shield 879 on the altar. **Step 17 done** |
| `replay1017-s18a-m18-pre-exit-gods-free-hp30.sav` | `a4dacba2` | Map 18 (3008,1752), just S of trigger 210, endgameStarted 0 |
| `replay1017-s18b-m10-endgame-done-hp30.sav` | `dc9b57e4` | Map 10 pad 210 (18432,22719,112), endgameStarted 1, hasBag 0 |
| **`replay1017-s18c-m10-reagent-bag-hp30.sav`** | `2503687e` | Map 10 (12676,13263,0) by Ezrekal's garden, hasBag 1, six q25 stacks. **Final state of the replay** |

## Final state

- **Save:** `~/lv-checkpoints/replay1017-s18c-m10-reagent-bag-hp30.sav`. The ini is unchanged (320×200, `scale_factor=2`).
- **Position:** Map 10 (12676,13263,0). hp 30, weight 270.
- **Globals:** godsFree 1038 = 1, endgameStarted 1814 = 1, hasBag 1037 = 1, templeOpen 1042 = 1, shieldFixed 1033 = 1, avatarPoisoned 1028 = 0.
- **Pack (from `findShape`):**
  - Ezrekal's bag 22089: 395 f0, f6, f8, f9, f10 and f14, each q25.
  - Key to the Clouds 18739 q170.
  - Hrodny's bag 17317, holding key 23296 q20.
  - Ragnar's bag 19729, empty.
  - Tiny Tars 28748 and 30048 (859 f8).
  - Leg 5's POTION f1 and f3, carried over and not re-checked this leg.
- **Shield 879:** on the Map 18 altar.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-17-replay-leg6/`, which holds 39 plates: `s15`, `s16a`-`s16o`, `s17a`-`s17n` and `s18a`-`s18i`.
- **Wrote** the 9 checkpoints above in `~/lv-checkpoints/`.
- **Scratch** in `/tmp/claude-1000/replay1017/`:
  - `lv_run6.log`, `trace6.txt`, and the working frames `sp/l6-*`, `sp/s1[678]*`, `sp/aos/`, `sp/end/` and `sp/sheet-*`.
  - Slot 1 (`saves/ultima8.001`) holds the `s18c` state.
  - `py/` is unchanged.
- **Stopped:** my ScummVM (`bin/scummvm-console`) and my Xvfb `:95`. Other agents' displays (`:101`, `:104`) were left alone.
- **Not touched:** source, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, and the binaries. The game copy's hashes were re-checked at the end: all OK.

## The whole chain

Legs 1-6 of this replay were played on one build: EUSECODE `2e3b71c2` / FIXED `8db11ee3` / U8SHAPES `efb16af1` / TYPEFLAG `d26d1531` / ANIM `696dbeb9`, one pinned game copy, one binary. Between them they reached every quest step 1-18 by input, from a new game's prologue to Ezrekal's reagent bag, with 0 cheats:

- leg 1: step 1;
- legs 2-3: steps 2-6;
- leg 4: steps 7-11;
- leg 5: steps 12-15;
- leg 6: steps 16-18.

Deaths and reloads across the chain were 3/4, 3/2, 0/0, 0/0, 2/3 and 0/0. Each was a reload of a banked save, as each leg's report records. No leg needed a teleport, a global write or a cheat toggle.
