# Quirks merge: altar Shield, Atli's shield option, the elixir, Ezrekal's patience (2026-10-09)

**Build under test.** `main` at `f3d83af`, plus the uncommitted `ARTIFACTS.sha256` and `build_scummvm.sh` detection change.
- **Game copy.** `/tmp/claude-1000/vquirks/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Its sha256 values match `shared/build/ARTIFACTS.sha256`: EUSECODE `760d631e592d…`, U8SHAPES `69fbd86123e8…`, TYPEFLAG `6bdb303654a5…`, ANIM `77e9705da254…`, and FIXED `9fbe86da9083…` in both places.
- **Engine log.** It reads `usecode/eusecode.flx: 2619303567614e4576432b19b0797332, 1525855 bytes`.
- **Binary.** `scummvm-lv/scummvm` has mtime 20:29:38, which is newer than fork `4ccd3fe7` (10:09:25).
- **Plates.** They are in `docs/playtest-2026-10-09-quirks/`, at 640x400.

**The session was cut short by the request budget.** Q3, Q4 and L were run to completion. Q1 and Q2 were not started in-engine. Q2 was stopped at its first talk attempt, which did not land.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| Q1 | The altar moves the q83 Shield to (3056,8176,40). It is clickable, the god pan runs, godsFree is set, and the endgame proceeds. Negative controls: no Shield, or Pagan's q0 828 | **NOT DEMONSTRATED**: the request budget ran out before the run. See "Q1 plan" for the route and the saves |
| Q2 | Atli's first meeting offers "I have this shield!" for a q0 828 and not for the q83 Shield | **NOT DEMONSTRATED**. The q0 half was set up (`cp7-map10-entry`, atliMet 0, no 828 in the pack), but the budget ran out after one failed strike. The q83 half has no natural save (see Q2) |
| Q3 | The elixir is 868 f0, drawn sea-green, looks "Tyorvi's elixir" and does not stack with blood. Both drink paths consume it, the Key follows, and blood is untouched | **PASS**, with one wording note: the engine reads it as `q: 0`, a single item; see finding 1 |
| Q4 | Every "Is Tyorvi's elixir ready yet?" pick barks one of the three lines | **PASS**: 16 picks out of 16 barked and none was silent |
| L | Log hygiene | **PASS**. In 7,575 lines there are 0 `Unhandled intrinsic`, 0 process-loop, 0 Segmentation, 0 Assertion, 0 segment-access and 0 `Cycle in paint` lines. There are 25 `Non-existent process PID (0) in implies`, which is exactly one per LV conversation end (see L) |
| C | `run_all_tests.sh`, `build_artifacts.sh`, `install_lv.sh`, `build_scummvm.sh`, fork patch check | **SKIPPED** on instruction. The sha256 match and the binary mtime above stand in for them |

## Method

- **Isolation.**
  - Xvfb `:90` (1280x800); the ScummVM window sat at (480,300).
  - Scratch `/tmp/claude-1000/vquirks/` holds `scummvm.ini` (`usehighres=true`, `frameLimit=false`) and `saves/`. Audio was `SDL_AUDIODRIVER=dummy`.
  - `run.sh` runs `scummvm-lv/scummvm --config=… --savepath=… --extrapath=scummvm-lv/dists/engine-data --debuglevel=1 --path=vquirks/game --save-slot=1 ultima8`.
  - The driver was the `vfin` `drv.py`/`h.py`, re-pointed to `:90`, with the mouse-walk reference at (320,214).
  - Only my own pids were started and stopped.
- **Saves.**
  - `run-s11-tyorvi-key.sav` (md5 `96e20997…`; tyorviDreams 1, givenRoot 0) was loaded at launch.
  - My own `sp/q3-pre-drink.sav` was used for the drunk retry.
  - `cp7-map10-entry.sav` was loaded for Q2.
  - Every load was by copying the file over `ultima8.001`.
- **Game-state writes.**
  - Teleports with cheats on, each followed by a toggle back off.
  - `MainActor::toggleCombat` once.
  - `debugflag_enable Object` after each load.
  - `Ultima8Engine::saveGame` three times, never mid-conversation.
  - `Item::grab` three times, none of them on the item under test:
    - blood vials 624 (395 frame 5) and 931 (395 frame 0), out of containers on Map 62;
    - the root, 1063 (399 f9), on Map 10.
  - **No `setGlobal`, no `setQuantity`, and no item creation.** Every dialogue answer, talk, drag and look was a click on the screen.
- **Finding the blood.** I decoded the save's `MAPS` section (`vquirks/maps.py`) to locate shape-395 frames 0-5 by map. The run-s11 world had no blood near Map 10. Map 62 has world vials at (26943,21503) and (26975,21535) frame 5, plus containers holding frames 0-5.

## Q3: the elixir, PASS

**The root.** The talk logged `Item: 116 (shape 200) calling usecode event 1 @ 0474:034A`.
- The menu was **I have found the root. / Can you help me? / bye** (`E1-01`).
- The pick gave "Ah, good that is. Take it I will and brew the tea I will." (`E1-02`).
- The next menu was **Can you help me? / Is Tyorvi's elixir ready yet? / bye** (`E1-03`).
- Afterwards: givenRoot 1, justGotRoot 1, `findShape 399: 0 found`, and weight 42 → 32.

**The brewing wait.** I walked from (12020,11970) to (14564,14190). The log shows `Item: 116 (shape 200) calling usecode event 16 @ 0474:0264`, and justGotRoot then read 0 (`E3-00`). I walked back, without teleporting.
- **The menu.** It read **Can you help me? / Have you made the elixir? / bye** (`E3-01`).
- **The pick.** It gave "Yes, I have. Take it to him now you can." (`E3-02`), then "Hope it helps him, I do." (`E3-03`).
- **The item.** givenElixir 1, hasTea 1, and the read was:
  ```
  findShape 868: Item 10115 (class Item, shape 868) (uc: TYPEELIX), 0, (0, 0) q: 0, ... f: 0xc   — 1 found
  findShape 395: 624 (frame 5, q 1) and 931 (frame 0, q 1) — unchanged
  ```
  So it is shape 868, frame 0 and **one item**, and weight went 32 → 42 (+10, bottle 180's weight). The engine prints `q: 0`, not q1 (finding 1).

**Sprite and look.**
- **The sprite.** In the pack the elixir is a sea-green vial with a red stopper (`E4-01`, `E4-01b`).
- **Beside the blood.** With the items separated it sits next to the two red blood vials and is clearly different from them (`E4-03`, `E4-03b`).
- **The looks:**
  - the elixir: `Item: 10115 (shape 868) calling usecode event 0 @ 0364:0080`, barking **"Tyorvi's elixir"** (`E4-02`);
  - each blood: `event 0 @ 018B:0080`, barking **"1 vial of blood"** (`E4-04` is all three side by side).

**No stacking with blood.**
- **The drag.** I dragged 10115 in the pack onto blood 931. The log shows `Dragging item 10115` / `Dropping object 10115`.
- **The result.** 10115 now sits at 931's own gump spot (54,34), and **both items still exist**: 931 is still `q: 1` and findShape 868 still reads 1, with weight unchanged at 42 (`E5-01`, `E5-01b`).
- **Why it cannot merge.** `ContainerGump::DropItem` merges only when `item->getShapeInfo()->hasQuantity()` and `canMergeWith` hold (`container_gump.cpp:530-546`). `canMergeWith` refuses a shape mismatch first (`item.cpp:2556`).
- **Positive control** (after the sober drink). I dragged blood 624 (frame 5) onto blood 931 (frame 0). The result was `findShape 395: 1 found`, with 931 at `q: 2`, and the look reads **"2 vials of blood"** (`E5-02`). So the same drag does merge when it should.

**Sober drink** (in the first world). The talk logged `event 1 @ 0473:0354`.
- **The menu.** It read **I have spoken to Ezrekal. / Do you have the Key to the Clouds? / I have something for you from Ezrekal. / bye**.
- **The picks.** Each line below is a pick, then the bark it gave; the next menu is shown in `E6-05`.
  1. **something from Ezrekal** → "Want nothing from that old hag…" (`E6-01`, `E6-02`)
  2. **It is an elixar.** → "Take nothing from that hag I will!" (`E6-03`)
  3. **It will heal your dreams.** → "Heal my dreams, you say?…" (`E6-04`)
  4. **Just try it, please.** (`E6-05`) → "Oh, all right. Give it to me." (`E6-06`)
- **Read during the wait(1000).** `findShape 868: 0 found`. Blood 624 (f5 q1) and 931 (f0 q1) were unchanged, and weight went 42 → 32.
- **The Key.** The menu read **May I have the Key to the Clouds? / bye** (`E6-08`). The pick gave "Well, treacherous it is… Here, here the Key to the Clouds is." (`E6-09`).
- **Afterwards.**
  - A new `Item 6363 (shape 82) … q: 0` is in the pack.
  - givenTea 1, and weight 42.
  - Both bloods are still q1.
  - The pack shows the two red vials, the new key, and no green vial (`E6-10`, `E6-10b`).
  - The pack gump open before the talk was closed at talk start, which is retail enterConvo; this is incidental evidence for the convo merge.

**Drunk drink** (`q3-pre-drink.sav` reloaded: elixir 10115, bloods 624 and 931).
- **Getting him drunk.** Rolls 0-3 were sober (same menu, then bye). Roll 4 offered **Are you OK, Tyorvi? / Do you have the Key… / I have something for you from Ezrekal. / bye** (`E7-01`).
- **Setting iAmDrunk.** **Are you OK, Tyorvi?** gave the drunk story. **No, that's not funny.** gave "…Now, leave me alone." and ended the talk. iAmDrunk read 1.
- **The next talk.** The menu read **What is your name? / What do you do? / Do you have the Key… / I have something for you from Ezrekal. / bye** (`E7-02`).
- **The picks.** Each line below is a pick, then the bark it gave; the drunk-path menu is shown in `E7-07`.
  1. **something from Ezrekal** → "Shomething from Ezkkre…Eshak…" (`E7-03`)
  2. **It is an elixar.** → "A what?" (`E7-04`; the bark was short and the plate shows the next menu)
  3. **It is a potion.** → "A poshun?…" (`E7-05`)
  4. **It will heal your dreams.** → "Heal -hic- my dreams?…" (`E7-06`)
  5. **Shut up and drink it!** (`E7-07`) → "All right, all right! Have to shout you do not! Try it I will." (`E7-08`)
- **Read after the drink.** `findShape 868: 0 found`, and bloods 624 f5 q1 and 931 f0 q1 were unchanged.
- **The Key.** **May I have the Key to the Clouds?** (`E7-09`) → "Well, treacherous it is…" (`E7-10`).
- **Afterwards.** A new `Item 5278 (shape 82) … q: 0` is in the pack, givenTea 1, and weight 32 → 42.

The "Hmmm, taste too bad that did not…" bark was not captured on either path, because my console reads paused the world across it. The key menu that follows it appeared both times.

## Q4: "Is Tyorvi's elixir ready yet?", PASS

There were 16 picks over 16 separate talks, all with justGotRoot 1.
- **The menu.** Every one was **Can you help me? / Is Tyorvi's elixir ready yet? / bye**, with the row the same width (166 px) every time (`Q4-00`).
- **Each pick.**
  - Each was a single click on that row. I filmed 9 frames at 0.35 s.
  - Each bark was classified by the hash of its green-pixel (49,254,49) pattern. Each of the three hashes was read on a plate.
  - Every pick also ended the conversation: there were no red menu pixels in the last frame.

| Bark | Picks | Plate |
|---|---|---|
| "Ah, always in a hurry the young are. No, ready it is not." | 7 (picks 1, 2, 10, 13, 16, 20, 25) | `Q4-01` |
| "Not so quickly. Long ago it was. Wish to make a mistake I do not." | 6 (picks 3, 5, 15, 17, 19, 24) | `Q4-02` |
| "Patience, my friend, patience. Time these things take." | 3 (picks 4, 22, 23) | `Q4-03` |
| silent | **0** | — |

Under the old `urandom(4)`, 0 silent in 16 has probability 0.75^16 ≈ 1%. The 10-08 batch-a run had 5 silent picks in 14. (The pick numbers skip because failed strikes consumed loop indices.)

## Q1: NOT DEMONSTRATED (plan, for the rerun)

No in-engine step was taken. I checked which saves can host the test (`vquirks/flags.py`, which decodes UCGLOBALS from every checkpoint):
- **`cp34-altar-ready-head` and `cp31-altar-armed`** have templeOpen 1 and shieldFixed 1. But they were saved on an older build: the 10-08 batch-b report shows cp34 holding a **539 f2, not a q83 828**. They serve only the "no Shield" negative control.
- **The positive run** needs `run-s13-shield-halves` → the EggShades ceremony on Map 10 (q83 828 created) → the Map 18 sanctum walk across EggTempleEntry, as batch-b did with its teleport shortcut → the altar egg entered from the south-west.
- **Pagan's q0 828.** It is at Map 8 (1090,1678,64), with a second one at Map 54 (12319,10367,8) (both in the save's MAPS section).
- **Suggested adversarial case.** Carry both the q0 and the q83 828 when the altar fires. Expected: only the q83 moves to (3056,8176,40), and the q0 stays in the pack.

## Q2: NOT DEMONSTRATED

- **The q0 half.** I loaded `cp7-map10-entry.sav`: atliMet 0, no 828 in the world map read (`findShape 828: 0 found` on Map 10), Atli at (19200,6400). I teleported to (19350,6750). The first strike did not land, and the budget ran out there.
  - **Route for the rerun.** Grab Pagan's 828 on Map 8, then **May I speak with you? → I am not a Pagan. → How do you know it is treacherous? → I am from Brittania. → On the other side of the barrier. → I -am- from Brittania!** (`lv-patched/ATLI.UNK:703-1118`).
  - **Negative control.** The same chain with no 828, after a reload: atliMet is set at `:715`.
- **The q83 half has no natural save.** No checkpoint has atliMet 0 together with a q83 828. That Shield is created only by the SHADES ceremony, and every save past it has atliMet 1. Per the brief, no item was created or altered.
  - **Synthetic route** [INFERENCE: not run]. The fork's `Item::setQuantity <objid> 83` writes quality, so Pagan's 828 could be raised to q83 to exercise the compiled `getQ() != 83` guard. That would be a fabricated state, so it was not used.

## L: log hygiene

`vquirks/lv_run.log` is 7,575 lines over one launch and two in-game loads.

| Pattern | Count | Context |
|---|---|---|
| `Unhandled intrinsic`, `stuck in process loop`, Segmentation, Assertion, `Trying to access segment`, `Cycle in paint` | 0 each | |
| `Non-existent process PID (0) in implies` | 25 | **Exactly one per LV conversation end**, from retail exitConvo, as the brief expects. 16 Ezrekal "ready yet?" exits + 1 hand-over + 1 Hrodny bye + 4 Tyorvi roll byes + "not funny" exit + 2 Key exits = 25 |
| `No SchedulerProcess in savegame; recreating` | 1 | The run-s11 load (no scheduler in that save) |
| `ActorAnimProcess [7777]: ANIMLOCK set on actor 112` | 1 | At launch; Ingjald |
| Other warnings | 5 | GUI theme/translations/icons, timestamps, one MIDI transition |

## Findings outside the brief

1. **The elixir's `q` is 0, not 1.** `give(Avatar, TypeBottle, 0:Frame, 0, 1)` makes exactly one 868. Because 868 is SF_GENERIC, there is no quantity field, so `dumpInfo` prints `q: 0`. This is consistent with EZREKAL V2's note ("FREE::give makes exactly one item of a non-quantity family for quan 1"). The brief's "q1" should read "one item". This is not a defect. Confidence: high.
2. **Hand-overs land at gump (0,0), on the pack's flap.**
   - **The evidence.** The elixir (and both Tyorvi Keys, 6363 and 5278) came out of `give()` at `(0, 0)`. The first pack view drew the elixir over the brown flap at the top-left, outside the dark interior (`E4-01b`). After that view, `objectInfo` read it at (3,10), with the two grabbed bloods stacked under it at the same spot.
   - **History.** This is the same "(0,0)" behaviour the 10-08 batch-a finding 1 recorded for the old vial; it survives on the new shape.
   - **Impact.** Cosmetic: items overlap and the top one hides the rest until moved. The fix would be [INFERENCE] `randomGumpLocation()` in the give path.
3. **Pack-internal drags are refused intermittently.** Two drops inside the same pack logged `Dropping object N` with nothing after it, and the item stayed put. One drop at a target item's spot was accepted. This is the same anomaly as the 10-08 reports; dropping onto the Avatar always worked. The probable cause [INFERENCE] is `DraggingItem`'s frame-fits-area test (`container_gump.cpp:447-453`) with the grab offset near the gump's top-left edge.
4. **A strike aimed at Tyorvi hit Hrodny once.** She stood in front of him. Her first-meeting menu (**What is your name? / What do you do? / bye**) opened instead (`event 1 @ 0471:0D5B`). This is a harness note for Gunnar strikes, not a game defect.

## Harness anomalies

- `con()` with an expectation regex timed out on `Ultima8Engine::saveGame`, but the save happened anyway (the slot's mtime moved). Use `raw()` for saves.
- `findShape` lists only the first 40 matches (`debugger.cpp:1379`), so on a map with 113 reagents the world vials were invisible. Instead I used the save's MAPS section to choose, then grabbed contained vials.
- Console reads pause the world, so barks that span a read are missed (the "taste too bad" line both times).

## Disk changes

- **Wrote** this report and 40 plates in `docs/playtest-2026-10-09-quirks/` (E1-E7 and Q4-*).
- **Scratch in `/tmp/claude-1000/vquirks/`:**
  - `game/`, `scummvm.ini`, `run.sh` and `lv_run.log`;
  - `saves/` (`ultima8.001` = the cp7 world; the engine wrote `ultima8.000` and `timestamps`);
  - `sp/`: frames, plus `q3-post-root.sav`, `q3-post-elixir.sav` and `q3-pre-drink.sav`;
  - `py/` (driver), `flags.py`, `scan.py`, `scan2.py` and `maps.py` (save decoders).
- **Stopped:** my ScummVM and Xvfb `:90`.
- **Not touched:** `shared/`, `~/lv-checkpoints` (read only), `~/.config/scummvm`, and every source, builder, map, fork, TODO or HANDOFF file. Nothing was committed.
