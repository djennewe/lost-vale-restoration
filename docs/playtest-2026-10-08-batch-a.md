# Batch A: elixir wait, frame-5 vial, crack hint, Tiny Tar shape 867, potions 5/7 (2026-10-08)

The build under test is `main` at `dfff626`, plus the uncommitted `build_scummvm.sh` and `ARTIFACTS.sha256`.

**Session facts:**
- The log reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `usecode/eusecode.flx: e5f36c956873ace1a550c08f7b7a680f, 1525085 bytes`.
- All five artifacts in the game copy match `shared/build` by sha256 (EUSECODE `d4915144`, U8SHAPES `bb0e4cda`, TYPEFLAG `794d4b80`, ANIM.DAT `77e9705d`, FIXED `1e954b7a`).
- One ScummVM pid ran the whole session.
- Plates are in `docs/playtest-2026-10-08-batch-a/`, at 640x400.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| E1 | Root → "Ah, good that is…"; menu then has "Is Tyorvi's elixir ready yet?" and no root option; givenRoot=1, justGotRoot=1 | **PASS** |
| E2 | Patience pick closes with a bark (1 in 4 silent); "Have you made the elixir?" not offered while justGotRoot=1 | **PASS**. 14 picks: 9 barks, 5 silent. All three barks were seen. No menu offered the hand-over |
| E3 | Walk away (leaveFastArea) → justGotRoot=0, hand-over offered, lines play, givenElixir=1, one 395 f5 in the pack | **PASS** |
| E3b | A save/reload or map switch right after the root never leaves neither option | **PASS**. Both kept justGotRoot=1 and offered "ready yet?" |
| E4 | The elixir draws as a red vial; record its look text | **PASS**, with a finding. It is a red vial. The look text is **"0 vials of blood"** (finding 1) |
| E5 | Re-picking the hand-over gives the "already" line and no second vial | **PASS** |
| E6 | "Shut up and drink it!" destroys the f5 vial and the Key menu follows | **PASS**. Negative finding on the *sober* path (finding 2) |
| E7 | First hint visit plays the "pale block" bark; the pale block is visible; a tiny Avatar hugging its east edge goes through | **PARTIAL**. Bark: PASS, with three controls. Block visible: PASS. The tiny passage was **NOT DEMONSTRATED** (see T4) |
| T1 | A frame-8 Tiny Tar makes the Avatar shape 867, the shrink frames play, and inventory is kept | **PASS** |
| T2 | Shrunk, he walks, runs and turns in all directions (ANIM.DAT live) | **PARTIAL**. A tiny Avatar walked from (2852,5400) to (2740,5352) through 8 walk bursts and 2 run bursts, and filmed facings change. I did not measure the displacement of each burst |
| T3 | Shrunk, pack weight and capacity read like full size | **PASS**. Before, during and after all read `vol 175/250, total weight 100` |
| T4 | Tiny fits the crack; full size does not | **PARTIAL**. The full-size negative control PASSES. The tiny passage was **NOT DEMONSTRATED**: the last potion was not drunk, because an empty bottle won the click (finding 4), and the session budget ran out |
| T5 | On wear-off he regrows to shape 1 with normal animation | **PASS**. Shape 1, and he walked in all 8 directions plus two runs, every one of which moved him |
| T6 | Map 10 children (708) look and behave as before | **PASS**. Static and in-engine (see section) |
| P5/P7 | Potions beside Hrodny's chest, clickable, can be picked up; f5 immortality starts and expires; f7 INVISIBLE toggles | **PASS** |
| L | Log hygiene | 17,334 lines. **0** `Unhandled intrinsic` (no chest was used), **0** `Non-existent process`, **0** `stuck in process loop`, **0** Segmentation, **0** Assertion, 0 `Cycle in paint`. 1 `Skipping invalid shape in sorter: 539,4` came from loading the 09-07 save `run-s16-tinytar` |

These checks were not run, as the brief told me: `run_all_tests.sh`, `build_artifacts.sh`, `install_lv.sh`, `build_scummvm.sh`, and the fork patch check. The brief says the estate is 42/42 and the fork `ed924d30` is unchanged.

## Method

- **Isolation.**
  - Display `:82` (Xvfb 1280x800); the window sat at (480,300).
  - The game copy was `/tmp/claude-1000/vet/game`, an rsync of `shared/u8-lv-patched` without `.bak` files.
  - Config `vet/scummvm.ini` (`usehighres=true`), saves in `vet/saves/`, `SDL_AUDIODRIVER=dummy`.
  - Command: `scummvm-lv/scummvm --config=… --savepath=… --extrapath=scummvm-lv/dists/engine-data --debuglevel=1 --path=vet/game --save-slot=1 ultima8`.
  - The driver was the `vcl` `drv.py`/`h.py`, re-pointed to `:82`.
- **Saves.** Each was copied over `ultima8.001` and loaded with `Ultima8Engine::loadGame 1`:
  - `run-s12-key-in-pack.sav` was loaded at launch. It turned out to be past the elixir (givenTea=1), so it was not used.
  - `run-s11-tyorvi-key.sav` was used for E1-E6: tyorviDreams 1, givenRoot 0.
  - My own saves in the scratch dir: `post-root-justgot1.sav` (E3b), `post-elixir.sav` (the E6 drunk retry) and `s16-after-p5p7.sav`.
  - `run-s16-tinytar.sav` was used for P5/P7, T*, E7 and T6: crackHintGiven 0, templeOpen 0, three f8 Tiny Tars.
- **Fresh maps.** Every world was refreshed with a Map 3 hop before testing.
- **Game-state writes:**
  - teleports with cheats on, each followed by a toggle back off;
  - `debugflag_enable Object`;
  - `MainActor::toggleCombat` once;
  - `Item::grab` for the root (7822) and for re-collecting the Tiny Tars I had dropped on Map 18;
  - `Ultima8Engine::saveGame 1` three times, never mid-conversation.

  Every dialogue pick, drink and potion pickup was a click or drag on the screen.

## E1, PASS

- **The root.** Root 7822 (399 f9) was on Map 10 at (21376,16640). I put it in the pack with `Item::grab`.
- **Talk.** Talking to Ezrekal logged `event 1 @ 0474:0333`. The menu was **I have found the root. / Can you help me? / bye** (`E1-01`).
- **The pick.** The answer was "Ah, good that is. Take it I will and brew the tea I will." (`E1-02`). The next menu was **Can you help me? / Is Tyorvi's elixir ready yet? / bye**, with no root option (`E1-03`).
- **Afterwards.** givenRoot (0x427) = 1, justGotRoot (0x428) = 1, `findShape 399` = 0, and weight went 40 → 30.

## E2, PASS

There were 14 "ready yet?" picks over 14 separate talks, picks 13 and 14 after the E3b reload and map switch. Every menu had the same three rows (pixel row signature identical to `E1-03`); the hand-over never appeared (`E2-01`). Each pick ended the conversation.

| Outcome | Count | Plate |
|---|---|---|
| "Not so quickly. Long ago it was. Wish to make a mistake I do not." | 3 | `E2-02` |
| "Ah, always in a hurry the young are. No, ready it is not." | 5 | `E2-03` |
| "Patience, my friend, patience. Time these things take." | 1 | `E2-04` |
| silent | 5 | `E2-05` |

**How a pick was judged silent.** A pick counted as silent only if no green Ezrekal bark pixel appeared in 10 frames over 3.5 s, with her on screen. I checked picks 1, 4, 5, 7 and 12 on the plates. 5 silent out of 14 is consistent with `urandom(4)` = 0.

## E3, PASS

- **Walking away.** I walked from (12198,12510) to (14662,14214). The log shows `Item: 116 (shape 200) calling usecode event 16 @ 0474:024D` (leaveFastArea) and 4 resetRefs. justGotRoot then read **0** (`E3-00`).
- **The return.** I came back by a same-map teleport.
  - Talk gave **Can you help me? / Have you made the elixir? / bye**, and "ready yet?" was gone (`E3-01`).
  - Picking the hand-over gave "Yes, I have. Take it to him now you can." (`E3-02`) and then "Hope it helps him, I do." (`E3-03`).
- **Afterwards.**
  - givenElixir (0x723) = 1, hasTea = 1, justGotRoot = 0.
  - `findShape 395: 1 found`: `Item 1229 (shape 395) (uc: ERTHREAG), 5, (0,0) q: 0, f: 0xc` (contained). The Avatar holds only the backpack, so the vial is in the pack.

## E3b, PASS

- **Save and reload.** Right after the root I ran `saveGame 1` then `loadGame 1`. justGotRoot read 1, and the menu offered "ready yet?" (`E3b-01`).
- **Map switch.** A hop to Map 3 and back to Map 10 left justGotRoot at 1, and the menu again offered "ready yet?" (`E3b-02`).
- **Leaving the fast area.** It was cleared only by the real walk-away in E3. No menu ever lacked both options.

## E4, PASS (finding 1)

- **The sprite.** The pack shows a small red vial at the gump's top-left (`E4-01`, zoom `E4-05-pack-vial-clear-zoom`). It is not a grey shard.
- **The look.** A single click logged `event 0 @ 018B:0080`, and the text is **"0 vials of blood"** (`E4-03`, `E4-04`).

## E5, PASS

On a new talk the menu still offered the hand-over (givenTea=0) (`E5-01`). Picking it gave "Yes, and gave it to you already I did. Now, bother me anymore about it, do not!" (`E5-02`). The menu then dropped the option, leaving **Can you help me? / bye** (`E5-03`). `findShape 395` was still exactly 1 (item 1229).

## E6, PASS (finding 2 on the sober route)

**Drunk route** (`post-elixir.sav`).
- **Getting him drunk.** 15 talks rolled sober (`Dead gods? / A portion of food?` after "something from Ezrekal"). Roll 16 offered **Are you OK, Tyorvi?** (`E6-11`). Picking it then **No, that's not funny.** set iAmDrunk. The next talk had the drunk menu **What is your name? / What do you do? / Do you have the Key… / I have something for you from Ezrekal. / bye** (`E6-12`).
- **Path:**
  1. **something from Ezrekal**
  2. **It is an elixar.** → "A what?"
  3. **It is a potion.**
  4. **It will heal your dreams.**
  5. **Shut up and drink it!** (`E6-13`) → "All right, all right! Have to shout you do not! Try it I will." (`E6-14`) → "Hmmm, taste too bad that did not…" (`E6-15`)
  6. Menu **May I have the Key to the Clouds? / bye** (`E6-16`) → **May I have…** → "Well, treacherous it is, but brave you are… Here, here the Key to the Clouds is." (`E6-17`), then "Now, rest I must…"
- **Afterwards.** `findShape 395: 0 found`. A new q0 key 5001 is in the pack. givenTea = 1.

**Sober route** (the first Tyorvi talk in the same world, before the reload):
1. **something from Ezrekal** → "Want nothing from that old hag…"
2. **It is an elixar.** → "Take nothing from that hag…"
3. **It will heal your dreams.** (`E6-03`)
4. **Just try it, please.** → "Oh, all right. Give it to me." (`E6-04`) → "Hmmm…" (`E6-05`)
5. **May I have the Key** (`E6-06`) → the Key was handed over, and givenTea = 1.

The vial was **still in the pack**: `Item 1229 (shape 395), 5, (3,10) … f: 0xc`, `findShape 395: 1 found` (`E6-07…-zoom`). See finding 2.

## E7, PARTIAL

`run-s16-tinytar` world, Map 18. The egg is 13557 (2864,6048), `range: 6, 6`.
- **Re-arming.** Between visits I teleported to (3072,2100), which takes the egg out of the fast area: `Egg::leaveFastArea → reset`. Its `hatched=0` was checked before each re-visit.
- **Entry.** Each visit was a walk south from (2852,5640) into the egg. Every visit logged `Item: 13557 (shape 73) calling usecode event 7 @ 05B1:0080`.

| Visit | crackHintGiven before | Carrying f8 | Barks (1 fps film) | Plates |
|---|---|---|---|---|
| 1 | 0 | none (three dropped in the hall) | "The stone here is split…", "Grit has sifted down…", "But the gap is no wider than my hand.", **"The crack lies hard against the east side of the pale block set into the wall."**; no nudge | `E7-01`..`E7-05` |
| 2 | 1 | 3 | pale-block bark, then the "Hrodny's dark potions…" nudge; no observation | `E7-07`..`E7-09` |
| 3 | 1 | 1 (a drop slipped) | pale-block bark + nudge | `E7-10` |
| 4 | 1 | none | **silent** (negative control) | `E7-11` |

**The pale block.** Stub 12109 (shape 47, q307) stands at (2816,6143). It shows as the white dressed-stone column in the wall, with the dark gap of the crack on its right (`E7-06-pale-block-zoom`). The tiny passage was not demonstrated (T4).

## T1, PASS

- **The drink.** I double-clicked Tiny Tar 14459 in the pack: `event 1 @ 04E5:00A9`, "I'm feeling funny", "Something strange is happening to me".
- **The shrink.** The full-size body turns. Then the small body appears lying and rises (708's 60-69 ramp), and stands. The frames are `t1s-*` in scratch; contact sheet in finding 5. There were no black frames.
- **Afterwards.** `objectInfo 1` reads **shape 867**. The Avatar keeps its 1 item (the backpack), and weight and volume are unchanged (T3).

## T2, PARTIAL

The second drink was potion 8603.
- **After the shrink.** I ran 8 walk bursts (0.7 s, mag 120, S/SE/E/NE/N/NW/W/SW), then a run E and a run W (mag 240).
- **End point.** The Avatar ended **tiny** (`shape 867`) at (2740,5352), against the start (2852,5400).
- **What the frames show.** They show the tiny sprite in different facings and positions.

What is missing is a position read after each burst. The first attempt (potion 14459) regrew after one burst, because I spent the window on console reads; in that burst the tiny Avatar walked (2852,5500) → (2852,5620). So movement is proven for S and for the sum of the sequence, but not for each direction separately.

## T3, PASS

| State | `objectInfo 1` |
|---|---|
| Full size before | shape 1, `Container vol: 175/250, total weight: 100` |
| Tiny (867) | shape 867, `vol: 175/250, total weight: 100` |
| Regrown | shape 1, `vol: 175/250, total weight: 100` |

The tiny reading is no longer 520/200.

## T4, PARTIAL

**Negative control, full size.** templeOpen was 0. I started at x = 2852, 2879 and 2866, each at y 6060, with three 1.3 s south pushes at each. Every one stopped at y 6106-6108 (the wall face at 6112..6143), at x 2828/2855/2842 (`T4-01-fullsize-refused`).

**Positive, tiny: NOT DEMONSTRATED.** I double-clicked the stack slot for the last potion (3963), but the empty bottle 8603 sat on top and took the click (finding 4). The Avatar stayed shape 1 and the pushes were refused again (`T4-02..04`). templeOpen stayed 0.

## T5, PASS

**First Tiny Tar regrow.** It came back to shape 1, hp 30. Bursts in all 8 directions then moved him:

| Burst | Position |
|---|---|
| E | (2852,5620) → (3060,5620) |
| NE | → (3212,5468) |
| N | → (3212,5172) |
| NW | → (3108,5068) |
| W | → (2908,5068) |
| SW | → (2760,5216) |
| run S | → (2760,5664) |
| run N | → (2760,5568) |

The facing frames were 0-7, each matching its direction.

**Second regrow.** It also came back to shape 1, at (2740,5352).

## T6, PASS

- **Map 10 children.** `findShape 708` = 2: CHILD 104 at (5376,7424) and CHILD 111 at (19712,6656). Both read `Container vol: 0/200, total weight: 500`, the unchanged 708 row.
- **In engine.** Child 111 is drawn as the small brown child, standing (`T6-01`, `T6-02`). A click hits it (dump logged). It stood in place for 12 s, and a double-click logged no use event.
- **Static checks:**
  - CHILD class 708 is byte-identical to retail (2,584 bytes).
  - TYPEFLAG 708 = `22601041000132c8`, equal to the base `.bak`.
  - ANIM.DAT 708 → offset 377728, equal to the base.
  - The new 867 row is `22601041000101fa`: 708's bytes 0-5 plus shape 1's weight 1 and volume 250. 867's ANIM entry points at the same 377728.

## P5/P7, PASS

- **Fresh map.** After the hop, Map 10 listed potion 4067 (859 f5) at (21216,8832,0) and 4703 (f7) at (21280,8832,0), both `n: 229`, beside chest 4927 (618) at (21152,8832) (`P-01`, zoom `P-02`).
- **Clickable.** A single click on each logged `event 0 @ 04E5:0080` with the bark "potion" (`P-03`, `P-04`).
- **Pickup.** I dragged each onto the Avatar: `Dragging item 4067` / `Dropping object` / `Dropped item in backpack`, and the same for 4703. Weight went 80 → 100.
- **Frame 5.** A double-click in the pack logged `event 1 @ 04E5:00A9` and "I feel like fighting!" (`P5-01`). Actor flags went `400` → **`40400`** (ACT_IMMORTAL 0x40000). They still read 40400 at 20 s and 33 s and were back to `400` at about 50 s.
- **Frame 7.** Item flags went `0x2041` → **`0x2055`** (FLG_INVISIBLE 0x10, plus OWNED 0x04), and the Avatar draws translucent (`P7-01`). At about 51 s the flags read **`0x2045`** and he draws solid again (`P7-02`). OWNED stayed set (finding 3).

## L: log hygiene

| Pattern | Count |
|---|---|
| `Unhandled intrinsic` | 0 (no chest was opened this session, so the expected 254 never fired) |
| `Non-existent process` | 0 |
| `stuck in process loop` | 0 |
| Segmentation / Assertion | 0 / 0 |
| `Cycle in paint` | 0 |
| `Skipping invalid shape in sorter: 539,4` | 1, on loading the old `run-s16-tinytar` save (known) |

## Findings

1. **The elixir looks "0 vials of blood".** EZREKAL `give(Avatar, TypeBottle, 5, 0, 0)` creates it with quantity 0, and retail class 395's look prints the quantity.
   - **Evidence.** `Item 1229 … q: 0`, and the look bark is "0 vials of blood" (`E4-04`). The commit text expected "vial(s) of blood".
   - **The pack slot.** The item also lands at gump (0,0), half on the pack frame.
   - **Likely fix.** Quantity 1 in the give/createNear. Note that TYORVI's foreach destroys the whole item regardless of quantity.
   - **Confidence.** High.
2. **Tyorvi's sober "Just try it, please." route hands over the Key without consuming the elixir.** That case's foreach is `foreach item where (type = TypeBottle) and (frame = 5) within container Avatar` (`lv-patched/TYORVI.UNK:2101`), which is **not recursive**. The vial lives in the backpack, so the loop never sees it.
   - **In engine.** After "Oh, all right. Give it to me." → Key → givenTea=1, `findShape 395` was still 1 (`E6-07…-zoom`).
   - **Comparison.** The drunk route's `foreach recursive` (line 2131) does destroy it.
   - **Scope.** The defect predates V1, which only changed the frame on that line. The player keeps a red "vial of blood" after the quest step.
   - **Likely fix.** Make line 2101 `foreach recursive`.
   - **Confidence.** High.
3. **The invisibility potion leaves the Avatar `FLG_OWNED`.** `TypePotion::invisible()` toggles OWNED on and never back. `f` was 0x2041 before and 0x2045 after expiry.
   - **Origin.** This is 1994 code, and no gameplay effect was seen.
   - **Confidence** in any consequence: low.
4. **A drunk Tiny Tar's empty bottle sits on the pack stack and wins the next click.** This is the 09-30 anomaly 2, reproduced twice.
   - **What happened.** After drinking from the frame-8 stack at gump (5,13), the next double-click there hit the empty bottle ("It's empty...", `t2b-pre-00`). That is what blocked T4's tiny attempt.
   - **Workaround.** A player has to drag the empty away first.
5. **The shrink renders.** The film shows the 708 fall-and-rise ramp, with no black frames this run (`/tmp/claude-1000/vet/sp/t1-sheet2.png`).
   - **Contrast.** The wave2-b report saw about 2 s of black during the shrink and regrow.
   - **Note.** The regrow itself was not filmed.
6. **Tyorvi drunkenness needs "Are you OK, Tyorvi?" first.** A drunk roll only *offers* that option; iAmDrunk is set by picking it. "Shut up and drink it!" on a roll where it was not picked angers him.
   - **The odds.** 15 of 16 talks rolled sober, against an expected rate of about 75%.
   - **Effect.** Players may find the drunk route hard to reach. Combined with finding 2, the reachable sober route leaves the vial behind.
7. **`run-s12-key-in-pack.sav` is past the elixir.** Its flags are givenRoot 1, givenElixir 1 and givenTea 1. Use `run-s11-tyorvi-key.sav` for the root and elixir step.

## Harness anomalies

- **Strikes.** Double-clicks with `yoff -30` missed the shorter Tyorvi and child sprites. -14 worked. Talks also fail beyond about 150 units, so I walked adjacent first.
- **Option syntax.** `--config`/`--path` needed the `=` form on this binary.
- **Console reads do not stop the Tiny Tar clock in practice.** Two `pos()` reads plus one burst used up the first window.
- **Drops.** One drag-drop from the pack re-grabbed an item already dropped, which left a potion in the pack for visit 3.

## Disk changes

- **Wrote** this report and 64 plates in `docs/playtest-2026-10-08-batch-a/`.
- **Scratch** in `/tmp/claude-1000/vet/`:
  - the game copy, `scummvm.ini` and `saves/` (`ultima8.001` overwritten by loads and saves; the engine wrote `ultima8.000` and `timestamps`);
  - `lv_run.log`;
  - the driver in `py/`;
  - frames and the three checkpoint saves in `sp/`.
- **Not touched:** `shared/`, `~/lv-checkpoints` (read only), `~/.config/scummvm`, and every source, builder, map, fork, TODO or HANDOFF file. Nothing was committed.
- **Stopped:** ScummVM and Xvfb `:82`.
