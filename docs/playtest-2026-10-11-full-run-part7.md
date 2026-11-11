# Full 1→18 run, cheats off, part 7: steps 17 and 18 done, music on. COMPLETED (2026-10-10)

**Build under test.** main `3e52ca6`, fork `b867a30c` ("U8 MidiPlayer: lock the parsers against the audio thread"); the `scummvm-lv/scummvm` binary is dated 2026-10-10 22:41, after the commit (20:30). Game copy `/tmp/claude-1000/vrun7/game`. Its sha256 matches `shared/build/ARTIFACTS.sha256`: EUSECODE `2ca7b486…` (1,526,011 B), FIXED `e03510ec…` (root and `STATIC/`), U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…`, ANIM `77e9705d…`.
- **Harness.** Xvfb `:95`. The ini is part 6's (320×200, no width/height keys, `frameLimit=true`) **without** `music_driver=null`, with `mute=true` and `music_volume=0`, under `SDL_AUDIODRIVER=dummy`. The driver is `vrun7/py/v7.py` + `nav7.py` (part 6's, re-pointed).
- **Start.** `~/lv-checkpoints/run1010-s17b-m18-temple-open.sav` (md5 `3b7c71c4`): Map 18 (2849,6532,0), templeOpen 1, godsFree 0, shieldFixed 1, avatarPoisoned 0, crackHintGiven 1.
- **Cheats: 0.** `Cheat` appears 0 times in `vrun7/lv_run.log`. Console use was reads only (`objectInfo`, `findShape`, `getGlobal`, `debugflag_enable Object`) plus `saveGame` and one `loadGame`.
- **One death, one load.** Both were caused by the harness (finding 1).

## Outcome

- **The quest is complete, with no cheats.** godsFree 1038 = 1, endgameStarted 1814 = 1, hasBag 1037 = 1, templeOpen 1, shieldFixed 1, avatarPoisoned 0.
- **The endgame ends cleanly, and no credits play.** After the closing fade the game returns to normal play on the Map 10 pad: stasis is released, the Avatar walks, and saves work. By design, `EggEndgame::hatch` ends with `FadeFromBlack(); wait(30); setAvatarInStasis(false);` and then spawns the reagent top-up (`lv-new/ENDGAME.UNK:86-109`). It has no credits call.
- **Music was on the whole session and nothing hung.** That covers 102 combat-mode key toggles (51 `Doing a MIDI transition!` lines), 16 runs in combat mode, the altar scene, the endgame and two map changes.

## Verdicts

| Step / leg | Verdict | Evidence |
|---|---|---|
| 17: sanctum route to the altar | **PASS** | (2849,6532) → (3277,6304) → (3465,7732) → (3493,8624) → W 0.9 s to (3189,8624). There was no hatch at that point, so I walked N 0.8 s |
| 17: EggAOCeremony, the Shield placed on the altar | **PASS** | `Item: 27939 (shape 73) calling usecode event 7 @ 05A7:0080`. Then, with the console closed for 90 s, frames every 0.8 s: the bark "I place the artifact upon the altar. The ancient symbols begin to glow." (`A1`), the white fade (`A2`), the three-god pan with the shatters (`A3-*`), and "It is done. The Ancient Ones are free. I can feel their gratitude -- and their power." (`A4`). The whole run is on `A0-ceremony-sheet` |
| 17: state after the altar | **PASS** | godsFree 1038 = 1, templeOpen 1, shieldFixed 1, poisoned 0 (`A5`). `findShape 828`: one Shield only, item 26343 q83 at **(3056,8176,40)**, `f: 0x2004`, i.e. on the altar and not in the pack. Weight 100 → 70. `findShape 860`: frames 5/3/4 (q303/301/302), the freed frames |
| 18: leaving the sanctum | **PASS (full size, no potion)** | W along y≈6370, then N at **x 2800**: (2800,6370) → (2800,5986) at full size (`A6`). The last Tiny Tar was not needed. Parts 6 and 2026-09-26 needed a potion at x 2848-2872 (finding 3) |
| 18: Map 18 → 10 (trigger 210) | **PASS** | (3019,4628) → (3087,1752), then a N 1.4 s run. `Unloading map 18` → `Loading Fixed items in map 10`. The landing hatched `05B2:0080` and **EggEndgame `Item: 11446 (shape 73) … event 7 @ 05AA:0080`** with no further step |
| 18: endgame scene | **PASS** | It ran untouched for 170 s, with frames every 0.7 s. All six barks were readable: "With the Ancient Ones freed…" (`B1`), "Green returns to the withered earth…" (`B2`), "The Zealans gather around me… hope." (`B3`), "An elder steps forward… The Vale is restored." (`B4`), "And with the power of the Ancient Ones now restored, I feel the path to Britannia opening before me at last." (`B5`), and "The Guardian's prison weakens. It is time to go home." (`B6`). Then a fade to black (`B7`) and back to play (`B8`) |
| 18: closing bark visible (A14 FAILs on 2026-09-26) | **PASS** | Both closing lines show before the fade (`B5`, `B6`). The 09-26 "fully black while the bark plays" defect did not recur |
| 18: state after the endgame | **PASS** | endgameStarted 1814 = 1, hasBag 0 at this point, godsFree 1 (`B9`). The Avatar was at (18432,22784,0), flags 0, and a W 1.0 s run moved him 296 units, so stasis was released |
| 18: Ezrekal, "I have freed your gods!" | **PASS** | Menu "I have freed your gods! / I would speak to you of Tyorvi. / bye" (`D1`) → "What a wonderful time this is! Once again be able to fulfill my duties as High Priestess I will! Nothing there is I can give you to repay you for your trouble, but…" (`D2`). I clicked through the later pages too fast to capture them. Afterwards hasBag 1037 = 1 (`D3`), and bag 32758 (shape 637, q1, `f: 0xc`, vol 18/32) holds six shape-395 stacks of q25: frames 0, 6, 8, 9, 10, 14. Weight 70 → 230 |
| 18: negative control, second pick | **PASS** | The same option on a second talk → "Yes yes! I know! Wonderful it is. I know not enough to repay you the bag I gave you is. Thank you again for your help…" (`D4`). `findShape 637` still lists exactly one q1 bag (32758), and the weight stayed 230 |
| MIDI hang fix (fork `b867a30c`), music on | **PASS (no hang)** | Map 18 sanctum, after the altar: 40 `c` presses at random 0.15-1.2 s gaps, then 1 (flags 400 → **c00**, so combat really toggled; `E1`), then 16 combat-mode runs of 0.6 s, then 30 `c` presses at 0.1-0.7 s gaps, then 1. Map 10 garden, after the endgame: 30 more `c` presses at 0.1-0.6 s gaps. That is **102 toggles and 51 `Doing a MIDI transition! trans: 9` lines**. The console answered after every batch. The process ran 32 min with an `SDLAudioP1` thread live and never froze. The driver was not identified in the log; that it is Miles AdLib is [INFERENCE] from the same ini and env as `docs/research/2026-10-11-midi-hang.md:93` |
| Log hygiene (`vrun7/lv_run.log`) | **PASS** | 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Unhandled intrinsic`, `Cycle in paint`, `ERROR`. The 55 WARNINGs are the 51 MIDI transitions plus 4 startup lines (themes, translations, timestamps) |

## Findings

1. **Harness death: the Avatar drowned in the Vale lake on a long open-loop run** (`C1-harness-drowning-tombstone.png`). This was on the walk from the pad to Ezrekal, with the route planned on `exact_reach` at erosion 1 and bursts up to 4 s. The last read was (16968,16488,0), hp 30. The next burst was NW 0.38 / W 0.21 / **NW 1.6 / W 1.35 s**. The log then shows two shape-347 (water) items `event 6 @ 015B:0080`, and the Avatar was dead: `(0,0,0)`, hp 0, flags 1000, "HERE LIES THE AVATAR". I reloaded `run1010-s18b-m10-endgame-done.sav`. The same trip at erosion 3 with bursts ≤ 1.6 s arrived safely by the same corridor (N to y≈18300, then NW to (15520,15272), then W/NW to (13168,13784)). I read this as overshoot from the long NW leg, not a map defect. I did not identify the drowning tile (objids changed on reload).
2. **Ezrekal wanders fast inside her stockade.** She was at (12799,12543), then (13087,12447), (12511,12639), (12751,12783), (12737,12563) and (12947,12679) over about 3 minutes. Two double-clicks aimed from an `objectInfo` read missed, because she had moved by the time the console closed. A colour-tracked double-click on her robe worked. A player can do this; it is only fiddly. Low severity.
3. **The breach is passable at full size at x 2800.** The 2026-09-26 run and part 6 were refused at full size at x 2848-2872 and drank a second Tiny Tar. 2026-10-09 got through at x 2860. Here the Avatar went (2800,6370) → (2800,5986) without shrinking. So one Tiny Tar suffices for the temple round trip [INFERENCE: once templeOpen removes the q307 wall pieces, as wave2-c observed]. Not a blocker. It is a design note: the crack is not a one-way squeeze after opening.
4. **The route guide's "walk ~1.4 s north from the pad" is obsolete** (also 2026-10-09 finding 4). The trigger-210 landing hatched EggEndgame at once.
5. **The altar egg did not hatch on the westward walk into (3240,8600).** It hatched only on the following 0.8 s walk north from (3189,8624). The resume recipe should say "west, then north", or (3052,8620) → north as 10-09 did.

## Harness anomalies

- `getGlobal` prints only to the console (`debugPrintf`), not to the log, so globals were read from console screenshots (`A5`, `B9`, `D3`).
- Fast clicks on conversation text skip pages. Ezrekal's bag pages after the first were not captured.
- The first input after a console close is swallowed (part 6 finding 4). It cost two missed talk double-clicks.
- `saveGame` worked every time this session (5 of 5).

## Checkpoints (all new)

| Name | md5 | State |
|---|---|---|
| `run1010-s17c-m18-pre-altar.sav` | `47dca0af…` | Map 18 (3493,8624,0) south of the dais, Shield in pack, godsFree 0. Rerun point for the ceremony |
| `run1010-s17d-m18-gods-free.sav` | `4d4e702b…` | Map 18 (3189,8528), godsFree 1, Shield on the altar |
| `run1010-s18a-m18-pre-exit-gods-free.sav` | `5a67f5ab…` | Map 18 (3087,1752) just south of trigger 210, godsFree 1, endgameStarted 0 |
| `run1010-s18b-m10-endgame-done.sav` | `39ce22f8…` | Map 10 pad (18432,22784), endgameStarted 1, hasBag 0 |
| **`run1010-s18c-m10-reagent-bag.sav`** | `18feec54…` | Map 10 Ezrekal's stockade (13168,12824), hasBag 1, bag of six q25 stacks. **Final state of the run** |

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-full-run-part7/` (25 plates).
- **Wrote** the 5 checkpoints above in `~/lv-checkpoints/`. No existing file was touched.
- **Scratch** `/tmp/claude-1000/vrun7/` (game copy with the build's five artifacts, ini, saves, `sp/`, `py/`, `lv_run.log`, `trace.txt`, `er_*.pkl`).
- **Stopped** my ScummVM (pid 3776506) and Xvfb `:95` (pid 3776492).
- **Not touched:** source, builders, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`.
