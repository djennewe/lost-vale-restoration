# Menu fixes (`wt/menus`), checked in the engine (2026-10-10)

**Build under test.** `main` `4e1eb70`, plus the uncommitted `build_scummvm.sh` and `ARTIFACTS.sha256`.
- **Game copy.** `/tmp/claude-1000/vmenu/game` is an rsync of `shared/u8-lv-patched` with the `.bak` files left out. Every hash matches `shared/build/ARTIFACTS.sha256`: EUSECODE `0e39b0b7…` (1,523,614 B), FIXED `29abf906…` in both places it exists, U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…` and ANIM `77e9705d…`.
- **Engine log line.** `usecode/eusecode.flx: 7545064984f3c73b6142d1a87f6d279e, 1523614 bytes`.
- **Binary.** `scummvm-lv/scummvm` has mtime 2026-10-10 06:37:40.
- **Harness.**
  - Xvfb `:94` (1280x800), with the game window at (480,300).
  - `scummvm.ini` sets `frameLimit=true`, `usehighres=true` and mute. Audio was `SDL_AUDIODRIVER=dummy`, and saves went to a private `saves/`.
  - The driver is the `vdlg` `drv.py`/`h.py`, re-pointed to this display and directory.
- **How options were picked.** A menu reader finds the AskGump bullets by their pixel pattern. Each answer was a click on a bullet found on screen. Option text was read from 2×/4× zoom crops (`*-menu-zoom.png`), and replies from full-frame plates (`*-bark0..n.png`).
- **How talks were started.** Every talk was a double-click on the NPC, confirmed by `event 1 @ <class>` in the log.
- **Not run, on instruction:** `run_all_tests.sh`, `build_artifacts.sh`, `install_lv.sh` and `build_scummvm.sh`. The hash match stands in for them.

**The run stopped at the request budget,** after D2. T1, D6 and the E2 "did not mention" variant were not played.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| R1 | Ragnar, first meeting: "What do you do here?" leaves the menu after its reply | **PASS** |
| R2 | Ragnar's Passage-Stone thread: the option reads "No, I don't" with no period, gets "Then why bother me…" and ends the talk; "Yes, I do." still gets "Legends say found the body…" | **PASS**, both halves, from two loads of the same save |
| E1 | Ezrekal, templeOpen and gods not freed: "I have opened your temple!" → "I found great treasure!" gets "Great treasure? What sort of treasure it is?" and leaves the menu | **PASS** |
| E2 | Ezrekal, first meeting: name → Britannia → outside → heard from the Ancient Ones → mention reply → "Tell me of the Shield." tells the shield story and leaves the menu | **PASS** through "They did mention you." The "did not mention" variant was **not played** |
| H1 | Hrodny, second visit: "What place is this?" → "Zealan Vale?" offers "Anything new?" and "Shades?", each answered and each leaving the menu | **PASS**. The follow-ups this unlocked ("Tied to the land?", "Pagan?", "But I'm not a Pagan!") also answer |
| H2 | Hrodny, healed with the Mark, temple not open: "The Shield of the Ancients is restored!" gets "See, so I do! For you, good!", and both healed options leave the menu | **PASS** |
| T1 | Thordis, poisoned, no Mark, after she told you to take her Test: "The plant exploded!" / "What is happening to me?" get the "Survive, you would…" reply and give the Mark | **NOT DEMONSTRATED**. No natural save is in this state, and the budget ran out before it could be reached by play (see below) |
| D2 | Hrodny / Ingjald / Tyorvi after the cure: "opened the temple", "found the Ancient Ones" and "freed the Ancient Ones" are answered, and so is Ingjald's "Shield … restored!" | **PASS**, all 10 option × NPC cells. Finding 1 describes a world where Tyorvi's cells cannot be reached |
| D6 | Tyorvi's drunk path ("Shut up and drink it!" and the Key) | **NOT DEMONSTRATED** (request budget). It last passed on 10-09 (`playtest-2026-10-09-quirks.md` Q3) |
| L | Log hygiene | **PASS** with one qualification. 0 each of `stuck in process loop`, `Unhandled intrinsic`, Segmentation, Assertion, `Trying to access segment` and `PID (0) in implies`. There are 46,709 `Cycle in paint` lines, **all** from checkpoints saved on Map 10. There were **0** on the freshly loaded Map 10 fixed items (finding 3) |

**State writes.**
- **Loads.** `Ultima8Engine::loadGame 1`, each over a fresh copy of a checkpoint.
- **Teleports with cheats on.** Each was followed by a verified `Cheats = false` before any talk.
- **Other commands.** `CameraProcess::moveToAvatar` and `MainActor::toggleCombat` (`run-s9`, `cp30` and `cp32` load in combat mode).
- **Not used:** `setGlobal`, `setQuantity`, a save, or a time skip. Every flag in this report was set by play or came from the checkpoint.

## R1: Ragnar, first meeting, PASS

**The world.** `run-s5-rite-granted` (ragnarMet 0). The talk logged `event 1 @ 0469:0237`.
1. **The menu.** It read **What is your name? / What do you do here? / Farewell.** (`R1-01-first-menu`).
2. **What do you do here?** gave "Do here? Hard to understand you are. Strangly you speak… A hunter I am. Bring back food for the clan I do. When find it I can." (`R1-02-…-bark0`).
   - The menu became **What is your name? / When you can find game? / Farewell.** (`R1-02-…-menu`).
   - **The option is gone.** The 10-10 dialogue run (finding 1) saw it stay.
3. **What is your name?** led to **When you can find game? / From very far away. / I am new to your land. / Farewell.** (`R1-03`). It still did not come back.
4. **Farewell.** ended the talk, and ragnarMet then read 1.

## R2: Ragnar's Passage-Stone thread, PASS

**The world.** `cp7c-ragnar-referral`. Read in the engine before the talk: ragnarMet 1, ragnarToldStone 0, ragnarPissed 0, atliMet 1.

**The thread.** Each step is a pick, then the menu it gave:
1. The top menu was **Atli sent me to you. / Farewell.** (`R2-01`).
2. **Atli sent me to you.** → Atli admires you. / Atli does curse a lot. (`R2-02`)
3. **Atli admires you.** → Atli does curse a lot. / **I believe that he is sincere.** (`R2-03`)
4. **I believe that he is sincere.** → He spoke of you and Hrodny. / **He said you know many things.** (`R2-04`)
5. **He said you know many things.** → **Do you know of the Passage Stone?** / How do you know so much? (`R2-05`)
6. **Do you know of the Passage Stone?** gave "Yes, seek it do you?" (`R2-06-…-bark0`).
   - The menu then read **Yes, I do. • No, I don't** on one row.
   - **"No, I don't" has no period**, while "Yes, I do." has one (`R2-06-passage-stone-menu-zoom4`).

**(a) No, I don't.** It gave **"Then why bother me with these questions do you? Leave me now. Bothersome you are."** (`R2-07-no-i-dont-bark0`).
- The talk ended, and no menu came back.
- Read afterwards: ragnarPissed **1** and ragnarToldStone 0.
- **This is the 1994 "No" case, not the crush rant.** The crush case barks "Blind are you? Stupid?…" and does not set ragnarPissed.

**(b) Yes, I do.** This was a second load of the same save, down the same path (`R2b-01` … `R2b-06`). It gave **"Hmmmm, Legends say found the body was by the waters of the southern lakes. Go there often I do not."** (`R2b-07-yes-i-do-bark0`).
- The menu then read … **Tell me of the legends. / Why do you not go there?** / Farewell., and **both** Yes and No were gone (`R2b-07-…-menu`).
- After Farewell., ragnarPissed was still 0.

## E1: Ezrekal, temple open, PASS

**The world.** `cp31-altar-armed`. Read in the engine: ezrekalMet 1, not poisoned, templeOpen 1, godsFree 0, spokeOfOpenTemple 0, shieldFixed 1. The talk logged `event 1 @ 0474:034A`.
1. **The menu.** It read **I have opened your temple! / I would speak to you of Tyorvi. / bye** (`E1-01`).
2. **I have opened your temple!** → **I found the Ancient Ones! / I found great treasure! / I found nothing. / bye** (`E1-02`).
3. **I found great treasure!** gave **"Great treasure? What sort of treasure it is?"** (`E1-03-great-treasure-bark0`).
   - The menu became **I found the Ancient Ones! / I found gold. / I found gems! / bye**, so "I found great treasure!" left it (`E1-03-…-menu-zoom`).
4. **bye.** spokeOfOpenTemple still read 0, because the Ancient Ones thread was not taken.

## E2: Ezrekal, first meeting, the shield story, PASS (the "did mention" path)

**The world.** `run-s9-mark-given` (ezrekalMet 0, haveMark 1, poisoned). The talk logged `event 1 @ 0474:034A`.

**The thread.** Each step is a pick, then the menu it gave:
1. **May I know your name?** → Can you help me? / I am from Britannia. / What do you do? (`E2-02`)
2. **I am from Britannia.** → **Yes, I am from outside.** / No, I am not from outside. (`E2-03`)
3. **Yes, I am from outside.** → … Who are the Ancient Ones? / **I have heard from the Ancient Ones.** / I have not heard… (`E2-04`)
4. **I have heard from the Ancient Ones.** gave "You have? Oh what great news this is!…" (`E2-05-…-bark1`). The menu then offered **They did mention you. / They did not mention you.** / I was in their temple. (`E2-05`)
5. **They did mention you.** gave "Oh, wonderful! Ready to return they must be. If only the Shield of the Ancients I had." (`E2-06-…-bark1`). The menu then had **Tell me of the Shield.** at the top (`E2-06-…-menu-zoom`).

**The pick.** **Tell me of the Shield.** gave the shield story, "…a great powerful artifact the Shield is. Used it to communicate with us the Ancients did. So powerful their magic is, sear the flesh from the High Priestess it…" (`E2-07-tell-shield-bark0..5`).
- The menu then read Can you help me? / What do you do? / I was in their temple. / **How was it lost? / Can you make another shield?** / bye. "Tell me of the Shield." was gone (`E2-07-…-menu-zoom`).
- mentionShield then read 1.

**Not played:** the "They did not mention you." branch, which uses the same add text.

## H1: Hrodny, second visit, PASS

**The world.** `run-s5-rite-granted` (hrodnyMet 0, no Mark, not poisoned, spokeVale 0, spokeOnce 0).
1. **First visit.** The menu was What is your name? / What do you do? / bye (`H1-01`). **What is your name?** gave "Hrodny, daughter of Ulnar, I am." (`H1-02`). Then bye, and hrodnyMet read 1.
2. **Second visit.** The menu was **What place is this? / I'd like to speak to you. / bye** (`H1-04`).
3. **What place is this?** gave "This, the Zealan Vale, is…". The menu became **Zealan Vale? • Work area? / Why can't you speak with me? / bye** (`H1-05`).
4. **Zealan Vale?** gave "Zealan, I am. My home, this is…", then "…Be gone, lest you, the shades find!" (`H1-06-…-bark0..3`).
   - The menu became Work area? / Why can't…? / **Anything new? • Shades?** / bye (`H1-06-…-menu-zoom`).
5. **Anything new?** gave "People. Ideas. Whatever…", and its option left the menu (`H1-07`).
6. **Shades?** gave "Ghosts... Spirits... Tied to the land, Zealans are…". Its option left the menu, which gained **Tied to the land? • Pagan?** (`H1-08`).
7. **The follow-ups, also unreachable before this fix:**
   - **Tied to the land?** gave "Looking for strings, are you? Overly bright, you are not." (`H1-09`).
   - **Pagan?** gave "YOU, thick-wit!… So Pagan, must you be…" (`H1-10`) and added **But I'm not a Pagan!**.
   - **But I'm not a Pagan!** gave "To your gods, go cry…", and the talk ended, as its case's `exitConvo` says (`H1-11`).

## H2: Hrodny, healed, temple not open, PASS

**The world.** `cp30-altar-ready`. Read in the engine: hrodnyMet 1, not poisoned, haveMark 1, templeOpen 0, spokeTemple 1. The talk logged `event 1 @ 0471:0D5B`.
1. **The menu.** It read **I have been healed! / The Shield of the Ancients is restored! / bye** (`H2-01`).
2. **The Shield of the Ancients is restored!** gave **"See, so I do! For you, good! Perhaps something to these god stories, there is. So now, open the temple, will you?"** (`H2-02-…-bark0`).
3. **Both healed options were gone.** The menu read **How can I open the temple? / bye** (`H2-02-…-menu-zoom`).

## D2: The healed-branch options across the three elders, PASS

| NPC | World | Option picked | Reply (plate) |
|---|---|---|---|
| Ingjald | `cp30` (templeOpen 0) | **The Shield of the Ancients is restored!** | "Smile upon you, the gods have! … But wait, open the temple is not." Both healed options left, leaving How can I open the temple? / bye (`D2-ing-01`, `-02`) |
| Hrodny | `cp31` (templeOpen 1, gods 0) | I have opened the temple. | "So? Wrong, was I. But stop working, I will not, until green, the land is…", then the talk ends (`D2-hr-01`, `-02`) |
| Hrodny | `cp31`, second talk | I have found the Ancient Ones. | the same shared case and reply; the talk ends (`D2-hr-03`, `-04`) |
| Ingjald | `cp31` | I have opened the temple. | "Why green the Vale is not? Why spoken, the gods have not? … Wake Ezrekal…", then the talk ends (`D2-ing-11`, `-12`) |
| Ingjald | `cp31`, second talk | I have found the Ancient Ones. | the same shared case; the talk ends (`D2-ing-13`, `-14`) |
| Tyorvi | `vqb/sp/q1-pre-altar` (tyorviPissed 0, iAmDrunk 0, givenTea 1) | I have opened the temple. | "Look, really getting tired of you I am…" (`D2-ty-11`, `-12`) |
| Tyorvi | same, second talk | I have found the Ancient Ones. | "Great, now, please get out of my way would you? … musty old bones…" (`D2-ty-13`, `-14`) |
| Tyorvi | `vqb/sp/q1-gods-free` | I have freed the Ancient Ones. | "Well, Pagan, maybe misjudged you I did. A small amount of hope…" (`D2-ty-21`, `-22`) |
| Hrodny | `q1-gods-free` | I have freed the Ancient Ones. | "To you, say what, can I? Thank you, so shallow, seems…" (`D2-hr-21`, `-22`) |
| Ingjald | `cp32-endgame-done` (ingyaldMet 1, gods 1) | I have freed the Ancient Ones. | "Even if, restore my legs, the gods do not, all that I have, yours is. Brought back hope to our world, you have…" (`D2-ing-21`, `-22`) |

## T1: Thordis, NOT DEMONSTRATED

**The state needed.** Thordis offers the three options only with: thordisMet, avatarPoisoned, zealanMark 0 and thordisToldTest 1 (`lv-patched/THORDIS.UNK` 815-822).

**No natural save has it.** thordisToldTest is 1 only in `cp24-zealanmark` and `slot1-before-2026-09-03`, and both already have zealanMark 1. I scanned every checkpoint and every `vqb`/`vquirks` bank.

**The path by play.** thordisToldTest is written only by her "How can I prove myself to you?" and "How may I be accepted?" cases, and both are offered only while the Avatar is not poisoned. So the state needs this chain, and the run's budget ended before it:
1. Start from a not-poisoned save with testFromAtli 0, such as `cp10-passage-stone` or `cp9b-thordis-spoken`.
2. Pick "Why will no one speak to me?" → … → "How can I prove myself to you?".
3. Take the plant test.
4. Talk to Thordis.

**Not used:** a `setGlobal` shortcut.

## D6: Tyorvi's drunk path, NOT DEMONSTRATED

The request budget ran out. Use `vquirks/sp/q3-pre-drink.sav`, which has tyorviPissed 0, givenTea 0 and the elixir in the pack, as in 10-09 Q3.

## Findings outside the brief

1. **Every checkpoint that holds the restored Shield also has `tyorviPissed` = 1**: `cp23`–`cp34` and the four `bag-q1-*` banks.
   - **In those worlds Tyorvi's top menu is "Calm down, Tyorvi."** It is an assignment, as `cp31` showed: **Calm down, Tyorvi. / Do you have the Key to the Clouds? / bye** (`D2-ty-01`), so his healed-branch options are not offered.
   - **"I wish to apologize for my rudeness." does not clear the flag** (`TYORVI.UNK` ~2275-2300). It adds only "I have spoken to Ezrekal." or "I have something for you from Ezrekal.".
   - **This is the same trap RAGNAR change 12 fixed for Ragnar:** anger Tyorvi once, and his post-cure lines ("I have been healed!", the temple, the gods) are gone for the rest of the game.
   - **Not established:** I did not check whether D19b pins it.
2. **Tyorvi's "The Shield of the Ancients is repaired!" (`TYORVI.UNK` 378, case 1371) still says "repaired"**, where Hrodny and Ingjald say "restored". It is internally consistent (add, case and removal agree), so it is not a dead option. I did not play it, because the only worlds that offer it are pissed (finding 1).
3. **Every one of the 46,709 `Cycle in paint` lines came from a checkpoint saved on Map 10.** The pairs are `426 -> 208` (23,365) and `426 -> 856` (23,344). The saves were `run-s5`, `cp7c`, `run-s9` and `cp32`.
   - **The control:** the four sessions where the Avatar came onto Map 10 fresh from Map 18 (log 44385-46638, `Loading Fixed items in map 10`) logged **0**.
   - **Reading:** this confirms the 2026-10-10 traps entry (stale fixed items carried in the save), not a defect in the shipped FIXED.DAT.
4. **Ezrekal's "I have opened your temple!" assigns her menu** (`askList=`). That drops "I would speak to you of Tyorvi." for the rest of the talk (`E1-02`). This is 1994 behaviour, and is noted only because it hides that option.

## Harness anomalies

1. **Wandering NPCs defeated the standstill strike.** A single-read projection strike, with `moveToAvatar` after every teleport, worked within 1-8 clicks.
2. **The camera parks after a teleport on old saves,** so projections were off by more than 200 px until `moveToAvatar` (`sp/s10.png`).
3. **`run-s5` loaded with the pack and minimap open.** I closed them with a frame double-click and `m`.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-10-menus/`, 237 plates (R1-*, R2-*, R2b-*, E1-*, E2-*, H1-*, H2-*, D2-*).
- **Scratch** in `/tmp/claude-1000/vmenu/`:
  - `game/`, `scummvm.ini`, `run.sh` and `lv_run.log` (49,767 lines);
  - `saves/` (`ultima8.001` is a copy of `cp32-endgame-done`);
  - `py/`, `fl2.py` and `sp/`.
- **Stopped:** my ScummVM and Xvfb `:94`.
- **Not touched:** source, builders, maps, the fork, `shared/`, `TODO.md`, `HANDOFF.md`, `~/lv-checkpoints` (nothing banked), `vqb/` and `vquirks/`.
