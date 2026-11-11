# Quest bits the round-two verifiers could not reach: altar Shield, ceremony bracket, Hrodny (2026-10-09)

**Build under test.** `main` at `909206d`, plus the uncommitted `ARTIFACTS.sha256`, `build_scummvm.sh` and engine patch.
- **Game copy.** `/tmp/claude-1000/vqb/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Its sha256 values match `shared/build/ARTIFACTS.sha256`: EUSECODE `49f44ee3a16c…`, U8SHAPES `69fbd86123e8…`, TYPEFLAG `6bdb303654a5…`, ANIM `77e9705da254…`, and FIXED `511902e8e753…` in both places.
- **Engine log.** It reads `usecode/eusecode.flx: 7545064984f3c73b6142d1a87f6d279e, 1523441 bytes`.
- **Binary.** `scummvm-lv/scummvm` has mtime 22:40:35, which is newer than fork tip `bbcfa209` (22:29:19).
- **Harness.** Xvfb `:92` (1280x800), with the window at (480,300). The scratch directory `/tmp/claude-1000/vqb/` holds my own `scummvm.ini` (`usehighres=true`, **`frameLimit=true`**) and save directory, with `SDL_AUDIODRIVER=dummy`. The driver is the `vconvo` `drv.py`/`h.py`, re-pointed, with the walk reference at (320,214).
- **Plates.** They are in `docs/playtest-2026-10-09-questbits/`, at 640x400.

**The session hit the request budget after Q1, Q4, Q6 and L.** I did not start Q2, Q3 or Q5 in-engine.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| Q1 | Altar: the q83 Shield leaves the pack and lands on the altar top at (3056,8176,40). It is clickable and looks "Ceremonial Shield of the Ancients Ones". The god pan runs, godsFree is 1, and the endgame proceeds. Negative: approaching without the Shield is refused | **PASS**. The whole route was natural from the ceremony on, except for three positioning teleports on Map 10 (listed under Method). The endgame egg fired: endgameStarted 1 |
| Q1 adversarial | Carry both the q0 and the q83 828 to the altar | **NOT DEMONSTRATED**. It was set up (Pagan's 8949 located on Map 8, q83 in the pack) and stopped by the budget before the walk |
| Q2 | Atli's "I have this shield!" appears for Pagan's q0 828 with atliMet 0, and not for the q83 | **NOT DEMONSTRATED** (budget). Static note: no checkpoint has atliMet 0 together with a q83 828 (`flags.py`: every save past the ceremony has atli1), so the q83 half has no natural save |
| Q3 | Tyorvi's drunk "Shut up and drink it!" path and the Key | **NOT DEMONSTRATED** (budget) |
| Q4 | Hrodny's temple talk works end to end | **PASS**, but **in the run-s13 world after the ceremony, not on `cp24-temple`**. The chain ran talk → q20 key bag → chest → Tiny Tar |
| Q5 | Mythran: after the talk the camera scrolls back once | **NOT DEMONSTRATED** (budget) |
| Q6 | The Sacred Circle ceremony completes with the new bracket. Atli, Thordis and Ezrekal stand still during inShadeScene and go home after | **PASS** |
| L | Log hygiene | **PASS**. In 20,813 lines: 0 `Unhandled intrinsic`, 0 process-loop, 0 Segmentation, 0 Assertion, 0 segment-access, 0 `Cycle in paint`, 0 `popToContainer`, and **0 `Non-existent process PID (0) in implies`** (finding 1) |
| — | `run_all_tests.sh`, `build_artifacts.sh`, `install_lv.sh`, `build_scummvm.sh`, the patch check | **SKIPPED** on instruction. The sha256 match and the binary mtime above stand in for them |

## Method

**The save.** `run-s13-shield-halves.sav` (md5 `5200e87e…`) was loaded at launch. Its Avatar was in combat mode (`flags: c00`); one `MainActor::toggleCombat` cleared it.

**Game-state writes.**
- **Teleports with cheats on**, each followed by a verified `Cheats = false`:
  - Map 10 (20304,17600), south of the circle;
  - next to Hrodny's yard (21500,8700);
  - to the key bag (19588,23200);
  - to the chest (21152,8940);
  - to the processional (18432,23200);
  - Map 8 (1150,1750,64) for the unfinished adversarial case.
- **`Item::grab`**: the key bag 25681, the three Tiny Tar 10904/10947/10948 out of the unlocked chest, and the q83 Shield 24553 back off the floor after the negative control. **None of these grabs is the item under test.**
- **Saves.** `Ultima8Engine::saveGame` through the save gump, never mid-conversation.
- **One reload** of my own bank.
- **No `setGlobal`, no item creation.**

**What was played, not set.**
- Every egg was walked into: EggShades, EggCrackHint, EggTempleEntry, EggAOCeremony, and the Map 18 → 10 trigger 210, whose landing hatched EggEndgame.
- Every menu answer, every key use and every drink was a click on the screen.

## Q6: Sacred Circle ceremony, PASS

**The hatch.** A walk north from (20304,17536) logged `Item: 8487 (shape 73) calling usecode event 7 @ 05A5:0080`. Then:
```
Item: 107 … event 15 @ 046B:0290   Item: 106 … event 15 @ 046A:02E8   Item: 116 … event 15 @ 0474:021C
LV: I_resetRef item=107/106/116 type=0x0205
```
That is the elders teleported in, enterFastArea fired, and each handler ran and returned.

**During the scene.** I read the elders four times: at the opening barks, at menu 1, at menu 2 and at menu 3.

| NPC | Every read | Processes |
|---|---|---|
| Atli 107 | (20224,17216,0) | only an `ActorBarkNotifyProcess` (a bark), no Loiter or activity process |
| Thordis 106 | (20672,17312,0) | none |
| Ezrekal 116 | (20480,17472,0) | none |

**An adversarial event landed mid-scene.** A schedule tick (`event 8` for 106, 107 and 116, at 046A:023F, 046B:0196 and 0474:018B) fired between menus 2 and 3. The next read had all three at the same coordinates, so the schedule's inShadeScene guard held.

**The menu picks:**
1. **Let's be reasonable!** (`Q6-01`);
2. **Yes, Priestess.** (`Q6-02`);
3. **Please, High Priestess.** The reforged Shield is on the grass by Ezrekal (`Q6-03`).

**After the scene.**
- **Flags:** shieldFixed 1, avatarPoisoned 0, inShadeScene 0.
- **Items:** `findShape 539: 0 found`, and the pack holds `Item 24553 (class Item, shape 828) (uc: AORTA) … q: 83`. Weight went 130 → 80.
- **The elders are home:** Atli (19231,6943), Thordis (4415,7423), Ezrekal (12799,12543).
- **The camera** followed the Avatar again.

## Q4: Hrodny's temple talk, PASS (run-s13 world, not cp24)

**Talk 1.** The click logged `event 1 @ 0471:0D5B`. The menu was **What is your name? / What do you do? / bye** (`Q4-01`).
- **What is your name?** set hrodnyMet 1.
- **bye** left her with a new `LoiterProcess 14558`, and 0x0F read 0.

**Talk 2.** The menu was **I have been healed! / The Shield of the Ancients is restored! / bye** (`Q4-02`).
- **I have been healed!** led to the menu **How can I open the temple? / bye** (`Q4-03`).
- **How can I open the temple?** gave the potion story (`Q4-04`), then the talk ended and the camera went back to the Avatar (`Q4-05`).

**After talk 2.**
- spokeTemple 1 and 0x0F 0.
- `Item 25681 (class Container, shape 637) (uc: BAG) … (19588, 23284, 0)`, holding key 25682 q20.
- Hrodny had a new `LoiterProcess 15136`.

**Key → chest → Tiny Tar.**
- Double-clicking key 25682 in the bag gump and clicking the chest logged `Target result: Item 11486 … shape 618 … q: 20`. The chest became `shape 78 (uc: CHEST_EW)`.
- The three 859 f8 Tiny Tars came out of it into the pack. Weight went 100 → 130.

## Q1: the altar, PASS

**Into Map 18.** I walked south from (18432,23200) onto trigger 211 and arrived on Map 18 at (3072,1896,0). The route on was (3080,4560) → (2847,4780) → (2847,5700); EggCrackHint hatched twice (`05B1`).

**Full-size negative.** At **(2868,6108)**, the column inside the 2848..2879 aperture, two 1.2 s south pushes stayed at (2868,6108) (`Q1-00`).

**The crack.**
- **The first potion was wasted.** I pushed with the mouse, and the tiny Avatar only turned to facing 3 and never moved (harness anomaly 1).
- **The second potion.** I dragged the empty off the stack inside the pack, then drank 10947 (`event 1 @ 04E5:00A9`) facing south.
- **Keyboard Up pushes** took him through. EggTempleEntry logged `event 7 @ 05B0:0080` and barked "I am through…" (`Q1-01`, `Q1-02`). templeOpen was 1, and he regrew at (2868,7188,8).

**To the altar.** I walked to (3452,8620) and banked `q1-pre-altar`; the altar top is empty there (`Q1-03`). Then (3052,8620) → north at walk gait, and the hatch logged `Item: 28480 (shape 73) calling usecode event 7 @ 05A7:0080`.

**The scene, with no console attached:**
1. The Shield appears on the altar top as the bark **"I place the artifact upon the altar. The ancient symbols begin to glow."** shows (`Q1-04`, zoom `Q1-04b`). The pack weight read 130 → 100 just after the hatch.
2. The fade to white (`Q1-05`).
3. The god pan with the shatters (`Q1-06`, `Q1-07`).
4. The camera returns to the Avatar and **"It is done. The Ancient Ones are free…"** (`Q1-08`). The whole scene is on the sheet `Q1-09`.

**After the scene.**
```
godsFree 1, templeOpen 1, shieldFixed 1
Item 24553 (class Item, shape 828) (uc: AORTA), 0, (3056, 8176, 40) q: 83, … f: 0x2004
```
- **It is a world item at exactly (3056,8176,40)**, and nothing else in the pack is an 828.
- **Click.** A single click on its sprite logged `Item 24553 … (3056, 8176, 40)` and then `event 0 @ 033C:0080`. The bark is **"Ceremonial Shield of the Ancients Ones"** (`Q1-10`).

**The endgame proceeds.**
- I walked out through the breach at full size: (2860,6244) → (2860,5844), then north to (3068,1748), then north onto trigger 210.
- That gave **Map 10 (18432,22784,0)**, inside EggEndgame's box, which logged `event 7 @ 05AA:0080`.
- The scene played for about 130 s untouched (`Q1-11`), and then **endgameStarted 1**.

**Negative control: no Shield, PASS.**
- **Setup.** I reloaded `q1-pre-altar`, walked north to (3452,7916), and dragged the Shield out of the pack onto the floor: `Throwing item to (3690, 7910, 0)`, landing at **(3739,7867,0)**. Weight went 130 → 100.
- **The approach.** I walked back the same way and north into the egg: `event 7 @ 05A7:0080`.
- **The result.** The bark is **"I sense great power here, but I lack the artifact needed for the ceremony."** (`Q1-12`). godsFree stayed 0, the altar top stayed empty, and the Shield was still at (3739,7867,0).

**Adversarial q0 + q83: NOT DEMONSTRATED.**
- **The setup.** After the negative, I `Item::grab`bed the q83 back and teleported this world to Map 8. `findShape 828` shows Pagan's `Item 8949 … (1090, 1678, 64) q: 0, f: 0x3400` on the wall. Its objid is 8949 in this world, not the 16262 of batch-b.
- **Where it stopped.** The budget ran out there, before 8949 was taken or the altar walked.

## Q2, Q3, Q5: NOT DEMONSTRATED (budget)

None of these was started.

**Q2.** For a rerun: `run-s1-lbdone` / `run-s2-mythran-done` have atliMet 0 on Map 8, in a world where 8949 or its equivalent hangs in Mythran's house.
- Take it by drag, then teleport to Map 10 near Atli's home (19232,6944).
- Walk the chain **May I speak with you? → I am not a Pagan. → How do you know it is treacherous? → I am from Brittania. → On the other side of the barrier. → I -am- from Brittania!**
- The same world serves Q5 (Mythran upstairs).
- No natural save combines atliMet 0 with a q83 Shield, so the q83 half of Q2 cannot be demonstrated without fabricating state.

**Q3.** For a rerun: `run-s12-root-given` (justGotRoot 1). Leave Ezrekal's fast area, return for the 868 elixir, then roll Tyorvi drunk.

## L: log hygiene

`vqb/lv_run.log` has 20,813 lines, from one launch and one in-game load.

| Pattern | Count |
|---|---|
| `Unhandled intrinsic`, `stuck in process loop`, Segmentation, Assertion, `Trying to access segment` | 0 each |
| `Cycle in paint`, `popToContainer` | 0 |
| `Non-existent process PID (0) in implies` | **0** (finding 1) |
| `No SchedulerProcess in savegame; recreating!` | 1 (the run-s13 load, which has no scheduler) |

## Findings outside the brief

1. **On this build the per-farewell implies warning is gone.**
   - **The evidence.** The 10-09 round-two reports logged exactly one `Non-existent process PID (0) in implies` per LV conversation end. This session had three Hrodny farewells and the whole ceremony with **0**.
   - **The likely cause** [INFERENCE]. `c44b84a` removed the extra own-handler spawn and the `cSetActivity(0)` fallback from exitConvo.
   - **Why it matters.** Anyone still counting that warning as a farewell marker will now read 0.
2. **Hrodny's talk-2 option "The Shield of the Ancients is restored!"** was gone from the menu after "I have been healed!" (`Q4-03` shows only **How can I open the temple? / bye**). I did not pick it, so I did not test what it does.
3. **Mid-scene schedule tick.** A period boundary fired `event 8` for all Vale NPCs, the elders included, during the Sacred Circle scene, and the guards held (Q6). This is incidental adversarial coverage.
4. **The Map 18 → 10 return lands the Avatar inside EggEndgame's box** (18432,22784), so the scene fires on arrival with no walk. The route guide's "walk ~1.4 s north from the pad" is obsolete for this landing.
5. **EggCrackHint's flag.** It hatched twice (both copies), yet `getGlobal 0x725` (crackHintGiven, 1829) read 0 right after. My console reads may have paused the barks before the write [INFERENCE]. I did not chase it.

## Harness anomalies

1. **Tiny Tar plus a mouse walk does not move.** A 0.5 s mouse burst with vector (-60,30) turned the tiny Avatar to facing 3 and never moved him (nine pushes). Keyboard **Up** (MOVE_FORWARD) after facing south at full size went straight through. Use the keyboard for the crack.
2. **The mouse-direction sectors are not the iso projection.** (-60,20..40) gives world S; (-50,50) gives SW; (0..-35,60) gives SE. Ctrl+Up held 0.35 s is a 32-unit careful step, which is how I aligned on x 2868.
3. **The ask menu and the Avatar's own barks are the same red** (213,48,49). I told them apart by the menu bullet's column gap.
4. **Dragging an item from the pack onto a wall face bounces** (`Dropping object` with nothing after it). A drag to another spot inside the pack worked.
5. **The image reader caches by path**, so plates need unique names.

## Disk changes

- **Wrote** this report and 22 plates in `docs/playtest-2026-10-09-questbits/` (Q1-00..12, Q4-01..05, Q6-01..03).
- **Scratch in `/tmp/claude-1000/vqb/`:**
  - `game/`, `scummvm.ini`, `run.sh` and `lv_run.log`;
  - `py/` (the driver), `flags.py` and `savinfo.py`;
  - `saves/` (`ultima8.001` is the post-negative world, now on Map 8);
  - `sp/`, holding frames plus the banks `q1-after-ceremony`, `q1-tinytar`, `q1-pre-altar`, `q1-gods-free` and `q1-endgame` (endgameStarted 1, Shield on the altar).
- **Stopped:** my ScummVM and Xvfb `:92`.
- **Not touched:** `~/lv-checkpoints` (read-only), `shared/`, source, builders, maps, the fork, `TODO.md` and `HANDOFF.md`.
