# The Bag of Reagents from Ezrekal, verified in engine (2026-09-27)

Change under test: the uncommitted B1 on HEAD `4f981fe`. `lv-patched/EZREKAL.UNK`
hands over a TypeBag (637) of six TypeReagent (395) stacks, frames 0, 6, 8,
9, 10, and 14 at q 25, in the hasBag-false branch of "I have freed your
gods!", then sets `hasBag`. `lv-new/ENDGAME.UNK` no longer creates the bag;
`topUpReagents` loops on `endgameStarted` and refills only when `hasBag` is
set. `test_uc_eggs.py` P9 asserts `hasBag` stays 0 after ENDGAME.

Artifacts: a full `tools/build_artifacts.sh` exited 0 and reproduced all four
canonical hashes, EUSECODE.FLX `7f885f5e...` (1,505,576 bytes), FIXED.DAT
`4a3d3e18...`. `session.sh start` synced `USECODE/EUSECODE.FLX` into
`shared/u8-lv-patched/`, and the engine logged `usecode/eusecode.flx:
aae44805..., 1505576 bytes` and `Running Ultima VIII: Pagan (Gold Edition +
Lost Vale/DOS/English)`. Binary `scummvm-lv/scummvm` linked 15:19:25, after
the `build_scummvm.sh` edit at 15:19:22. `shared/data/u8-install/` already
held `7f885f5e...`, so `install_lv.sh` was not re-run. One ScummVM process
(PID 71446) ran every test; 0 `Segmentation` or `Assertion` lines in its log.
Plates are in `docs/playtest-2026-09-27-bag-ezrekal/`, named by test ID,
640x400.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| S1 | Test estate | `tools/run_all_tests.sh` 31 PASS, exit 0; `test_uc_eggs.py` 49 passed; round-trip 516/516 | **PASS** |
| S2 | Build and hashes | full build exit 0; TYPEFLAG `9f534e59`, U8SHAPES `a611e9be`, EUSECODE `7f885f5e`, FIXED `4a3d3e18` all OK | **PASS** |
| S3 | Compilation Report | 48 files, 46 succeed; failures `EALOGO.UNK` (unterminated block comment) and `TJORVI.UNK` (unterminated string), the allowlist pair | **PASS** |
| S4 | New class | none; EZREKAL (npcnum dispatch `0474`) and ENDGAME (`05AA`) are existing classes, both dispatched in engine below | **not triggered** |
| S5 | Maps, shapes | FIXED.DAT unchanged; TypeBag 637 and TypeReagent 395 already used by RAGNAR, HRODNY, and the old ENDGAME | **not triggered** |
| S6 | ScummVM fork | no fork commit; `lost-vale` at `e0d6084d`; the patch-equality diff is silent | **PASS** |
| 1 | Endgame with `godsFree` | `05AA` hatched; six barks, none about a bag; `endgameStarted` 1, `hasBag` 0; bags 2 and reagents 0 before and after; walked east 208 units | **PASS** |
| 2 | "I have freed your gods!" gives the bag | offered in the menu; both pages of her bark; `hasBag` 0 to 1; bag 5606 (vol 18/32, six items) holding frames 14, 10, 9, 8, 6, 0, each q 25; weight 330 to 490 | **PASS** |
| 3 | Asking again | "Yes yes! I know!... the bag I gave you is..."; still three bags, the same six stacks, weight 490 | **PASS** |
| 4 | Top-up | split 10 of stack 15430 to the ground: q 15 at 5 s after **OK**, q 25 at 22 s; the ground stack stayed q 10; again after save and reload (8 to 25); with `hasBag` written to 0 the stack held at 12 for 35 s | **PASS** |
| 5 | Other Ezrekal dialogue | the Tyorvi branch and **bye** played normally; nothing else was offered from this state | **PARTIAL** |
| 6 | Endgame egg bypassed (added) | walked around the egg to Ezrekal: bag given, but no top-up process; a split stack held at q 10 for 45 s; crossing the egg later started it and refilled to 25 | **finding 1** |
| 7 | No-backpack fallback (`popToEnd`) | not exercised; the Avatar kept his backpack throughout | **NOT DEMONSTRATED** |

## Method and harness writes

Saves and `scummvm.ini` were copied to the scratchpad first.
`~/lv-checkpoints/cp34-altar-ready-head-20260926.sav` was copied over
`ultima8.001` and loaded with `Ultima8Engine::loadGame 1`: Map 18 at
(3400, 7696), `templeOpen` 1, `godsFree` 0, `shieldFixed` 1, `hasBag` 0,
`endgameStarted` 0; bags 1754 and 14387 (shape 637) in the pack; no shape
395 anywhere (`findShape 395: 0 found`); Tiny Tar 8982 and 8983 at frame 8.

Played from there in one process: the altar (`05A7:0080`, the fade, the pan,
"It is done..." at `A0-altar-it-is-done-bark.png`; `godsFree` 0 to 1), out
through the crack with potion 8982 (`04E5:00A9`,
`A0-drink-tiny-tar-at-crack.png`; cp34 carries the pre-breach wall), the
x 3080 wall gap, and trigger 210 to Map 10 at (18432, 22480).

Cheats stayed off: 0 `Cheats =` lines and 0 teleports in the log. Every
walk was a right-button burst, every answer a click on the row the screen
showed, and every pickup, split, and container open a mouse action.
Console use: `debugflag_enable Object`, `objectInfo`, `findShape`,
`getGlobal`, `Kernel::listProcesses`, three `Ultima8Engine::saveGame`, and
three `loadGame 1`. **Two debugger writes, both in test 4's negative
control:** `UCMachine::setGlobal 0x40D 1 0` (log line 9425) and
`UCMachine::setGlobal 0x40D 1 1` (log line 9472), `hasBag` being bit 1037.

Checkpoints taken on the way, in the scratchpad (see Disk changes):
`godsfree-map18-2026-09-27.sav` (Map 18 after the altar),
`pre-endgame-map10-2026-09-27.sav` (Map 10 pad, `godsFree` 1,
`endgameStarted` 0, the save the brief asked for), and
`bag-received-map10-2026-09-27.sav`.

## 1: endgame with `godsFree`, PASS

On arrival: `godsFree` 1, `hasBag` 0, `endgameStarted` 0
(`A0-map10-arrival-endgame-not-run.png`). A 1.4 s walk north hatched
`Item: 11562 (shape 73) calling usecode event 7 @ 05AA:0080`. Frames every
0.7 s for 145 s, console closed, segmented by the bark text mask:

| t after walk start (s) | Screen |
|---|---|
| about 1 | black (opening fade) |
| 4.2 to 14.8 | "With the Ancient Ones freed..." (`A1-endgame-first-bark.png`) |
| 21.5 to 32.1, 38.9 to 50.5 | the two middle barks |
| 53.4 to 70.7 | "An elder steps forward... They are thanking me. The Vale is restored." (`A1-endgame-elder-thanks-bark.png`) |
| 73.6 to 88.1 | "And with the power of the Ancient Ones now restored..." (`A1-endgame-closing-bark1-follows-elder.png`) |
| 89.1 to 95.8 | "The Guardian's prison weakens. It is time to go home." (`A1-endgame-closing-bark2.png`) |
| 98.7 | black (`A1-endgame-fade-black.png`) |
| 99.6 on | world |

The closing pair now follows the elder's bark directly
(`A1-endgame-last-three-barks-zoom.png`); on 09-26 the "worn bag" bark sat
between them for about 20 s, and the scene is that much shorter.

Reads after: `endgameStarted` 1, `hasBag` 0, `godsFree` 1, `templeOpen` 1;
`findShape 637` lists only 1754 and 14387, as before the scene;
`findShape 395: 0 found`; weight 330. A 1.0 s walk east moved him from
(18432, 22280) to (18640, 22280) (`A2-walked-east-after-endgame.png`).
`Kernel::listProcesses` showed the top-up alive and idle: process 2170
(`EGGENDGA`, `05AA:04C0`, the hatch waiting on its spawn) and process 1460
(`05AA:04E6`, notify 2170).

**Negative control:** the scene that used to hand over the bag created
neither a bag nor a reagent, and wrote no `hasBag`.

## 2: Ezrekal gives the bag, PASS

Route from the pad: (17200, 22288), (17200, 14608), (14032, 14608),
(14032, 12656), then west through the stockade's east opening to
(13072, 12556). `route.py` chose these; the straight route hugs the lake's
east edge at x 15408. Ezrekal (116) wanders inside the stockade; the second
strike opened her menu: **I have freed your gods!**, **I would speak to you
of Tyorvi.**, **bye** (`B1-ezrekal-menu-first.png`,
`B1-ezrekal-menu-first-zoom.png`).

**I have freed your gods!**: frames every 0.85 s for 45 s. Page 1, 0 to
22.3 s, "What a wonderful time this is! Once again be able to fulfill my
duties as High Priestess I will! Nothing there is I can give you to repay
you for your trouble, but"; page 2, 23.1 to 41.3 s, "this I can give you
there is. A magical bag it is. Provide you it will with any magical
reagents you need. Take it, with our heartfelt thanks!"
(`B2-ezrekal-bag-bark-page1.png`, `B2-ezrekal-bag-bark-page2.png`,
`B2-ezrekal-bag-bark-zoom.png`).

Reads after: `hasBag` **1**; `findShape 637` 3 found, new bag **5606**,
`Container vol: 18/32, total weight: 160, items: 6`; `findShape 395` 6
found: 15430 frame 14, 15834 frame 10, 15835 frame 9, 15836 frame 8, 15837
frame 6, 16890 frame 0, each **q 25**, `f: 0xc` (owned, contained); Avatar
weight 330 to **490**. Double-clicking the bag logged `Item: 5606 (shape
637) calling usecode event 1 @ 027D:00A7` and opened it
(`B3-bag-opened-in-pack.png`, `B3-bag-opened-zoom.png`): the six stacks sit
together in its top-left corner (finding 4).

## 3: asking again, PASS

Second talk (`event 1 @ 0474:031C`), same three options
(`B4-ezrekal-menu-second.png`). **I have freed your gods!**: page 1, 0 to
21.5 s, "Yes yes! I know! Wonderful it is. I know not enough to repay you
the bag I gave you is. Thank you again for your help. Now, much there is for
me to do. If excuse"; page 2, 22.3 to 23.3 s, "me you will?"
(`B5-ezrekal-bag-i-gave-you-page1.png`, `-page2.png`, `-zoom.png`).

Reads after: `hasBag` 1; `findShape 637` still 3 (1754, 5606, 14387);
`findShape 395` 7, the six in the bag plus the ground stack from test 4
(which ran between the two talks); weight 490. No second bag, no new stack.

## 4: the top-up, PASS

The player action that lowers a stack: dragging a reagent from the open bag
onto the ground, which the engine answers with a quantity slider
(`C1-split-slider.png`). Eleven clicks on the slider's left arrow set it to
10 (`C1-split-slider-set.png`); **OK** logged `SplitItemProcess splitting:
10: 15-10`.

| Read (s after **OK**) | Stack 15430 in the bag | Stack 7380 on the ground |
|---|---|---|
| 5.0 | q **15** | q 10 at (13372, 12544, 0) |
| 21.9 | q **25** | q 10 |

The five other stacks read q 25 throughout. The loop is `wait(200)` between
passes, and each console read pauses the world, so the refill is bounded
between those two reads; it was not timed more closely. The ground stack
staying at 10 is the scope working: the loop searches `within container
Avatar`.

**After save and reload:** `saveGame`, then `loadGame 1`. Processes 2170 and
1460 came back from the save at the same IPs. A split of 17 left 15430 at
q 8 at 5.0 s and q 25 at 20.0 s (`E3-slider-after-reload.png`).

**Negative control, with the two disclosed writes:** `hasBag` set to 0, a
split of 13 left 15430 at q 12; it read **12 at 5.0 s and 12 at 34.9 s**.
With `hasBag` set back to 1, it read 25 at 17 s. The `if hasBag` guard holds
the loop idle.

## 5: other Ezrekal dialogue, PARTIAL

Only **I would speak to you of Tyorvi.** and **bye** were offered besides
the bag option. Third talk (`D1-ezrekal-menu-third.png`): **I would speak to
you of Tyorvi.** barked "Tyorvi? Thordis' brother he is."
(`D2-tyorvi-branch-reply.png`) and returned a menu of **I have freed your
gods!**, **He needs help.**, **Yes, he is Thordis' brother**, **bye**
(`D2-tyorvi-branch-submenu.png`, `-zoom.png`). **bye** closed it
(`D3-after-bye.png`). **He needs help.** was left unpicked because it may
write step-11 flags. The branches gated on `avatarPoisoned`, `templeOpen` 0,
or `godsFree` 0 (for example **I have opened your temple!**) cannot be
reached from this state, so the claim 2 menu condition's negative side (no
bag option before `godsFree`) was not shown in engine.

## 6: the endgame egg bypassed, added (finding 1)

`pre-endgame-map10-2026-09-27.sav` reloaded: (18432, 22480), `godsFree` 1,
`hasBag` 0, `endgameStarted` 0 (`F0-pre-endgame-save-loaded.png`). The egg
is at (18432, 22016) with npcnum 0x88, a hatch box of x 18176..18688,
y 21760..22272 (`build_map_10.py:1423`); the pad is 208 units south of it.
A walk west along y 22480 to (17232, 22480) passed between the colonnade's
pillars with no `05AA` in the log (`F1-west-of-colonnade-no-endgame.png`),
and the route north to Ezrekal's never crossed it.

Ezrekal offered the same menu (`F2-ezrekal-menu-no-endgame.png`) and gave
the bag (`F3-bag-bark-no-endgame.png`): `hasBag` 1, `endgameStarted` 0, six
stacks q 25. `Kernel::listProcesses` listed **no `EGGENDGA` process**. A
split of 15 left stack 2676 at q 10 at 5.1 s and **q 10 at 50.0 s**
(`F5-no-endgame-stack-stays-low.png`).

Recovery: walking back and crossing the egg hatched `05AA` with `hasBag`
already 1. The scene played the same six barks at the same times as test 1
(`F6-late-endgame-closing-bark1.png`), spawned processes 1471 and 723, and
stack 2676 then read q 25. A walk east moved him 208 units.

## Findings outside the plan

1. **The bag is bottomless only after the endgame egg has hatched, and that
   egg can be walked around.** `build_map_10.py:1414-1416` calls it "on the
   only path back"; in engine the colonnade lets a player step west off the
   pad and never cross the box. Before this change that player also got no
   bag; now they get a finite pouch whose promise ("Provide you it will with
   any magical reagents you need") fails until they happen to cross the egg,
   at which point it recovers. The ENDGAME comment "topUpReagents below
   still keeps the stacks full, from whenever hasBag is set" holds only for
   the egg-first order. Options: spawn the top-up from Ezrekal's hand-over
   too (with a guard against running two), or widen the egg across the
   whole approach. Confidence high; test 6 is the evidence.
2. **Nothing sends the player back to Ezrekal after the Vale is restored.**
   The ENDGAME comment this change deleted gave that as the reason the bag
   lived in the scene. The bag is now reached only by a player who returns
   to her unprompted. A design call for Douglas; the 1994 dialogue supports
   the move.
3. **`scummvm-lv/engines/ultima/detection_tables.h` held the wrong entry
   before this session's build.** At 15:20:54 (after the 15:19:25 link) its
   Lost Vale line read md5 `340c79139de8bc60a0151ca620bed65d`, size
   1505765, which matches no artifact here; the author's `install_lv.sh` log
   from 15:21 (`i2.log` in the scratchpad) printed "Installed EUSECODE.FLX
   hash (aae44805...) not in ScummVM detection table". The linked binary was
   right (it contains `aae44805...` and the engine detected the game), but
   a bare `make` in `scummvm-lv/` would have linked a build that cannot find
   the game (traps.md, 2026-09-19). This session's `build_artifacts.sh`
   rewrote the entry to `aae44805...`, 1505576. What wrote the stray entry
   is unknown; no FLX of 1,505,765 bytes was found on disk.
4. **The six stacks sit in one clump, and the bag looks like the other two.**
   Usecode `pop` leaves gump position (0, 0): the bag appeared at (0, 0) in
   the pack over the shield, and the six stacks at the bag's top-left
   corner, drawn as one pile. The reagent bag is the third identical shape
   637 in the pack alongside 1754 and 14387. Cosmetic; a player will find it
   by opening each.
5. **The top-up refills any partial reagent stack the Avatar carries.** By
   the code (`foreach recursive ... within container Avatar`, `< 25` guard),
   a stack split off onto the ground and picked up again becomes a new
   stack of 25, so reagents duplicate without limit, bounded by weight.
   This predates the change and was not exercised.
6. **"me you will?" gets a page of its own for about 1 s** at the end of the
   second-ask bark, the pattern of the 09-26 E-F1 finding, in 1994 text.
7. `EZREKAL.UNK:126` and the `lv-patched-inventory.md` B1 entry still say
   "Not yet verified in engine".

## Harness anomalies

- This shell has `noclobber` set: the first `> log` redirects for the test
  estate and build failed with "cannot overwrite existing file", leaving
  stale logs that looked like results. They were rerun with `>|` into
  `v-tests.log` and `v-build.log`.
- `Ultima8Engine::saveGame` prints no console reply on this build, so the
  driver's retry sent it twice (both into slot 1, harmless).
- Ezrekal wanders fast; each talk took one to six standstill strikes.
- The 09-26 driver (`drv.py`) was reused with its plate directory pointed
  at this report's folder.

## Disk changes

- This report and `docs/playtest-2026-09-27-bag-ezrekal/` (36 plates).
- `shared/build/` rewritten by `tools/build_artifacts.sh` with the canonical
  bytes (new mtimes); `shared/build/ARTIFACTS.sha256` untouched.
- `scummvm-lv/engines/ultima/detection_tables.h` rewritten by the same build
  (Lost Vale entry `340c79.../1505765` to `aae44805.../1505576`, finding 3).
  The binary was not rebuilt.
- `shared/u8-lv-patched/USECODE/EUSECODE.FLX` synced from `shared/build/` by
  `session.sh start` (untracked).
- `~/.local/share/scummvm/saves/` (all 48 files) and
  `~/.config/scummvm/scummvm.ini` restored from copies taken first;
  `ultima8.000` md5 `3e7dc241...`, `ultima8.001` `083de199...`, `timestamps`
  `e5a2abea...`, `scummvm-history.txt` `47c7389b...`, `scummvm.ini`
  `a143fa3b...`, as before.
- Scratchpad: `v-tests.log`, `v-build.log`, the session log
  (`bag-ezrekal-session.log`), the three checkpoints named in Method, frame
  sequences, and the `drv.py` plate-directory edit.
- No source edited, nothing committed, `TODO.md` not edited. Session
  stopped (ScummVM and Xvfb killed).
