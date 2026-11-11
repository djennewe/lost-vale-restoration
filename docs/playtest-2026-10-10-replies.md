# Replies, Cataclysm, Tyorvi's apology: in-engine (2026-10-10)

**Build under test.** main `4a40dc8`, which merges `fce4723`.
- **Game copy.** `/tmp/claude-1000/vrepl/game` is an rsync of `shared/u8-lv-patched` without the `.bak` files. Its sha256 values match `shared/build/ARTIFACTS.sha256`:
  - EUSECODE `709c6bd1…` (1,525,518 B);
  - FIXED `22cada6f…`, in both places it exists;
  - U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…` and ANIM `77e9705d…`.
- **Engine log line.** `usecode/eusecode.flx: 7545064984f3c73b6142d1a87f6d279e, 1525518 bytes`.
- **Binary.** `scummvm-lv/scummvm` has mtime 2026-10-10 11:00:26.
- **Harness.**
  - Xvfb `:94` (1280x800), with the window at (320,200).
  - `scummvm.ini` sets `usehighres=false`, `scale_factor=2`, `frameLimit=true` and mute. Audio was `SDL_AUDIODRIVER=dummy`, and saves went to a private `saves/`.
  - The driver is the `vmenu` `drv.py`/`h.py`, re-pointed. Projections were scaled ×2 for the low-res window.
- **Picking options.** A menu reader finds the AskGump bullets on screen: centre (213,48,49), with (189,12,8) two pixels out. Each pick was a click on one of those rows. Barks were captured by the NPC's text colour: Tyorvi, Thordis and Atli are (255,133,49), Ezrekal (49,254,49) and Ragnar (205,202,238).
- **Starting talks.** Each talk was a double-click on the NPC, confirmed by `event 1 @ <class>` in the log.
- **Not run, on instruction:** `run_all_tests.sh`, `build_artifacts.sh`, `install_lv.sh`, `build_scummvm.sh` and the fork patch check. The hash match stands in for them.

**The session hit the request budget** before Y2, A1 and the second half of R2.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| Y1 | Apology clears tyorviPissed; next talk normal; healed/gods options answer | **PASS** (cp23 and cp32), with negative control |
| Z2 | "Tell me more of the Great Cataclysm." always tells a story | **PASS**: 14 of 14 picks barked, **0 silent**; 8 early-days / 6 plague |
| Y5 | Tyorvi drunk path end to end | **PASS** (natural cp22-hastea: tea → elixar → potion → heal dreams → Shut up and drink it! → Key) |
| T1 | Thordis "The plant exploded!" / "What is happening to me?" → "Survive, you would…" + Mark | **PASS**, by play from `cp10-passage-stone` (Thordis route, plant scene walked into), no flag writes |
| Z1 | Ezrekal "I have not heard from the Ancient Ones." → "Heard from them you have not?…"; heard/not-heard both gone; Titans/Who-are stay | **PASS** |
| Y3 | "She had little to say." → "Little to say, had she?…" | **PASS** (cp12-pre-cliffs, natural) |
| Y4 | "Are you going to the cliffs?" / "You weren't at the cliffs." reply; the greeting-trap question | **PARTIAL**. "You weren't at the cliffs." **PASS**, and the trap is **confirmed** (finding 1). "Are you going to the cliffs?" was **not shown**: the climb used a non-Tyorvi key (finding 2), so attemptedCliffs and climbedCliffs were set together |
| R1 | Ragnar "Who is Thordis?" → "Know Thordis you do not?…" | **PASS** (cp7-map10-entry) |
| R2 | "Do you like her?" → "Like her? Beautiful she is…"; "None, thank you." → "Good. Then go and find the stone…" | **PARTIAL**: "Do you like her?" **PASS**; "None, thank you." **NOT DEMONSTRATED** (budget; it needs ragnarToldStone, via the Passage Stone thread in the same talk) |
| Y2 | "I already have." → "Already climbed them you have?…" | **NOT DEMONSTRATED** (budget). No natural save has toldCliffs + climbedCliffs + tyorviPissed. Plan: `cp20-cliffs-climbed`, set toldCliffs by Hrodny's thread (`HRODNY.UNK` ~1174), then Tyorvi: Calm down → apology → I have spoken to Ezrekal → She told me of the cliffs |
| A1 | Atli "Former beauty?" → "Green and good this Vale once was…" | **NOT DEMONSTRATED** (budget). Save to use: `run-s10-ezrekal` (poisoned, ezrekalMet) |
| Text | New lines wrap inside the bark box, no second-language leak | **PASS** for every new line shown (Z1, Y3, Y4c, R1, R2b); see "Text" |
| L | Log hygiene | **PASS**. In 6,057 lines there are 0 each of `stuck in process loop`, `Unhandled intrinsic`, Segmentation, Assertion, `Trying to access segment`, `Non-existent process`, `popToContainer`, FIXME and `Cycle in paint`, over 6 map loads |

## Y1: Tyorvi's apology, PASS

**cp23-ceremony-done** (tyorviPissed 1, cured, shieldFixed 1, templeOpen 0). Talk logged `event 1 @ 0473:0354`.
1. The menu was **Calm down, Tyorvi. / Do you have the Key to the Clouds? / bye** (`Y1-01-pissed-menu`).
2. **Calm down, Tyorvi.** gave "Back are you? Wish to speak to you I do not." The menu then gained **I wish to apologize for my rudeness. / Shove off, you lush!** (`Y1-02-*`).
3. **I wish to apologize…** gave "Well, a much better attitude you have now. Speak to you I will." (`Y1-03-apologize-bark0`). The menu gained **I have spoken to Ezrekal.** (`Y1-03-apologize-menu`).
4. **bye**. Then `getGlobal 0x43E` (tyorviPissed) read **0**.
5. **The next talk** offered **I have been healed! / The Shield of the Ancients is repaired! / Are you OK, Tyorvi? / Do you have the Key… / bye** (`Y1-05`). "Are you OK" is the 25 % drunk roll, which is retail.
   - **I have been healed!** gave "So heard I have. Good for you, now at least, have to worry about hauling your body away I do not…" and left the menu (`Y1-06-healed-*`).
   - **The Shield … repaired!** gave "And so supposed to be really excited about this I am, right? …" and left the menu (`Y1-07-*`).
6. **A third talk** offered healed / Shield / Key / bye again (`Y1-09`). So the menu is not a one-off.

**cp32-endgame-done** (tyorviPissed 1, godsFree 1).
- **The first talk** offered **Calm down / Key / bye** (`Y1-11`).
- **Negative control.** Calm down → **Shove off, you lush!** gave "Have to take this I do not!" and ended the talk (`Y1-13`). tyorviPissed read 1. The next talk was **Calm down** again (`Y1-14`).
- **Then the fix.** Calm down → apology → bye (`Y1-15`–`17`). tyorviPissed read **0**.
- **The next talk** offered **I have freed the Ancient Ones. / Key / bye** (`Y1-18`). The pick gave "Well, Pagan, maybe misjudged you I did. A small amount of hope after all there is…" (`Y1-19`).

## Z1: Ezrekal "I have not heard…", PASS

**run-s9-mark-given** (ezrekalMet 0, haveMark 1). Talk logged `event 1 @ 0474:034A`.
1. **May I know your name?** → **I am from Britannia.** → **Yes, I am from outside.** (`Z1-02`–`04`).
2. The menu then read **Can you help me? / The Titans are still in control. / Who are the Ancient Ones? / I have heard from the Ancient Ones. / I have not heard from the Ancient Ones. / What do you do? / bye** (`Z1-04-yes-outside-menu`).
3. **I have not heard…** gave **"Heard from them you have not? Sad this is, but surprised I am not. Answered us the Ancients have not since the Great Cataclysm. For them to speak I still wait."** It took two pages (`Z1-05-not-heard-bark0/1`).
4. The menu after it read **Can you help me? / The Titans… / Who are the Ancient Ones? / What do you do? / bye**. **Both** heard and not-heard are gone, and Titans and Who-are stay (`Z1-05-not-heard-menu`).

## Z2: the Cataclysm story, PASS

The world is the same one as Z1, continued: shieldFixed 0. Who are the Ancient Ones? added **Tell me more of the Great Cataclysm.** (`Z1-06`).
- **The sample.** There were 14 picks, one per talk; each pick ends the talk. The option row was found each time by its red-pixel mask (Jaccard 1.0).
- **Classification.** Each bark's first line was classified against two reference plates:
  - "In the early days of our history…" (`Z2-01-cataclysm`);
  - "Shortly after the Shield of the Ancients was lost, a terrible plague…" (`Z2-04-cataclysm`).
- **The results.**
  - Early days: picks 1, 2, 3, 8, 12, 13 and 14 (7), plus pick 1's reference, for **8** in all.
  - Plague: picks 4, 5, 6, 7, 9, 10 and 11, for **6**.
  - **0 silent.**
- **How the barks ended.** Every bark was clicked through to the end of the talk, in 7-9 pages.
- **Plates.** Each pick's menu and first page are `Z2-NN-cataclysm{-menu,}.png`.
- **Before the fix,** D4 (10-10 dialogue) had 5 of 14 silent.

## Y5: Tyorvi's drunk path, PASS

**cp22-hastea** (tyorviDrunk 1, hasTea 1, givenTea 0). The elixir is in the pack.
- **The tea.** **I have something for you from Ezrekal.** gave "Shomething from Ezkkre…Eshak…" (`Y5-01`).
- **The picks:**
  1. **It is an elixar.** gave "A what?" (`Y5-02`);
  2. **It is a potion.** gave "A poshun?…" (`Y5-03`);
  3. **It will heal your dreams.** gave "Heal -hic- my dreams?…" (`Y5-04`).
- **The drink.** The menu then offered **Shut up and drink it!**. The pick gave "All right, all right! Have to shout you do not! Try it I will." (`Y5-05`), then "Hmmm, taste too bad that did not… Actually feel a little better I do." (`Y5-06-after-drink-bark0`).
- **The Key.** The next menu was **May I have the Key to the Clouds? / bye** (`Y5-06`). The pick gave "Well, treacherous it is, but brave you are… Here, here the Key to the Clouds is." and "Now, rest I must. Maybe dream I will not." (`Y5-07`).
- **Afterwards:**
  - `findShape 868: 0 found`;
  - a new key `12061 (shape 82) q: 0` is in the pack;
  - tyorviDrunk 0 and givenTea 1.

## T1: Thordis's plant options, PASS (played, no flag writes)

**cp10-passage-stone** (testFromAtli 0, thordisMet 0). The Passage Stone 2347 is in the pack.
1. **Meeting Thordis.** **How are you called?**, then bye; thordisMet read 1 (`T1-02`).
2. **The second talk** offered **Why will no one speak to me?** (`T1-04`). Then **How may I become a Zealan?** → **How can I prove myself to you?**, which gave the Test instructions (`T1-07`). thordisToldTest read **1**.
3. **The Test.** I hopped to Map 13 and back (the 10-10 trap). Then I teleported onto the plateau and **walked** to the plant. The egg hatched (`059A:0080`) and the scene teleported **Atli** in, which is the thordisToldTest branch (`T1-09`).
   - **Afterwards:** poisoned 1, haveMark 1, zealanMark 0 and plantScene 1.
   - **Atli's aftermath talk was not reached.** Five strikes missed.
4. **Thordis at home** offered **I have taken your Test. / The plant exploded! / What is happening to me? / Tell me about the other people. / bye** (`T1-11`). I banked this state as `sp/vrepl-t1-pre.sav`.
5. **The plant exploded!** gave **"Survive, you would, think, I did not. Or warned you, I would have. Poisoned, you have been. Sorry, I am. No cure, there is. My people, protect, I must. Here, the Mark, is. Comfortable, make you, we will. Owe you that much, I do."** (`T1-14-*`).
   - **The menu afterwards:** **Poisoned? / No cure? / Tell me about… / bye**. All three test options are gone.
   - zealanMark read **1**.
6. **What is happening to me?** After reloading the bank, zealanMark read 0 again. The pick gave the same reply and the same menu (`T1-16`, `T1-17-*`).

## Y3: "She had little to say.", PASS

**cp12-pre-cliffs** (spokeFuneral 0, toldCliffs 0, not pissed).
- **The greeting** offered **I have spoken to Ezrekal. / bye** (`Y3-01`).
- **The first pick** gave "So, still alive you are…". The menu then read **She had little to say. / bye** (`Y3-02-menu-zoom`).
- **She had little to say.** gave **"Little to say, had she? Then wasted your time she has. Well, still alive you are... for now."** Only bye was left (`Y3-03`).
- **The pause book.** It was open under this talk, from a stray Escape (harness 2). It did not affect the menu.

## Y4: drunk greeting, PARTIAL, and the trap

**Before the climb.** In the same cp22-hastea world (tyorviDrunk 1, attemptedCliffs 0), the menu was **Tell me more of the Cliffs. / Key / something from Ezrekal / bye** (`Y4-01`). That is the normal branch.

**The climb.** I teleported to Map 13 and walked north onto the EggCloudCliffs box. The egg hatched (`05A8:0080`), and **both** attemptedCliffs and climbedCliffs read 1. That was before Tyorvi had given any key (finding 2).

**"You weren't at the cliffs."**
- **The talk** offered **You weren't at the cliffs. / Key / something from Ezrekal / bye** (`Y4-03`). "Tell me more of the Cliffs." is gone.
- **The pick** gave **"Was I not? -hic- Gathering my climbing gear I was... and a drink or two, perhaps. Climbed them without me you did? Then need me you did not."** It left the menu (`Y4-04-*`).
- **The next visit** offered it again, at the top of the same replaced menu (`Y4-06`).

**The trap.** After the drink and the Key (Y5), tyorviDrunk read 0, and the normal menu was back: **Tell me more of the Cliffs. / Are you OK, Tyorvi? / Key / bye** (`Y4-07`). Then:
1. **Tell me more of the Cliffs.** → **I am going there.** → **Yes, accompany me.** (`Y4-08`–`10`).
2. That set tyorviDrunk back to **1**, with attempted and climbed both 1.
3. **The next talk** was only **You weren't at the cliffs. / Key / bye** (`Y4-11`). See finding 1.

**"Are you going to the cliffs?"** It needs attemptedCliffs without climbedCliffs. The only way to get that is the key-less climb attempt, and that attempt was not run.

## R1 / R2: Ragnar

**R1, PASS.** `cp7-map10-entry` (ragnarMet 0, thordisMet 0).
- **The path.** What is your name? → From very far away. → Yes, I'm peaceful. → I am peaceful with all. → You have a point. → You are a cautious fellow. → What have they done? (`R1-02`–`08`).
- **The pick.** **Who is Thordis?** gave **"Know Thordis you do not? A great woman she is, a shrewd leader and wise. Seek her out, and of the acts of Gunnars clan tell you she will."** It left the menu (`R1-09-*`).

**R2, PARTIAL.** `cp7c-ragnar-referral` (ragnarToldStone 0).
- **The path.** Atli sent me to you. → Atli admires you. → I believe that he is sincere. → He spoke of you and Hrodny. (`R2-02`–`05`).
- **The pick.** **Do you like her?** gave **"Like her? Beautiful she is, said that I did. But no Thordis she is."** It left the menu (`R2-06`).
- **Not reached.** I went on to "He said you know many things." (`R2-07`). "None, thank you." needs ragnarToldStone first, and the budget ended there.

## Text

Every new line shown fits the bark box. Each wraps to at most 5 lines per page, and the overflow goes to a second page: Z1 and Y4c used two pages, and Y3, R1 and R2b one. No `\f`/`\g` half or stray marker leaked into a bark or a menu row.

Long menus stack to the top edge but stay on screen. The tallest were Tyorvi's 8-row elixir menu (`Y5-04`) and Ragnar's 8 rows (`R1-06`).

## Findings outside the brief

1. **Tyorvi's drunk greeting is a trap. Once re-armed after the Key, it lasts for the rest of the game.**
   - **What re-arms it.** After the Key, the normal menu offers "Tell me more of the Cliffs." again. **I am going there → Yes, accompany me.** sets tyorviDrunk = 1 (`TYORVI.UNK` ~1039).
   - **The only writer back to 0** is "Shut up and drink it!" (~2280). That needs the tea, and the tea is already given.
   - **The effect.** With attemptedCliffs and climbedCliffs both 1, every visit's menu becomes "You weren't at the cliffs." plus Key/bye (`Y4-11`). That greeting branch is an `if` / `else` around everything else, so the healed, temple and gods options never come back after the cure.
   - **How sure.** The in-engine half is observed. "Lasts for the rest of the game" is read from the source; I did not play to the cure in that world [INFERENCE].
   - **It is the same shape as T5's fix.** Before the Key it is harmless: the Key option stays offered and the drink clears it.
2. **The cliff handholds accept any shape-82 key.**
   - `CLCLIMB.UNK` tests only `type = TypeCliffKey` (82). In cp22-hastea the pack holds Pagan's **q99 key 4528** (`findShape 82`), so the first walk-in set climbedCliffs **before Tyorvi gave the Key**.
   - **Who is affected:** any player carrying a Pagan key, or the Map 10 q20 chest key, can skip the Tyorvi step.
   - **Consequences:**
     - "Are you going to the cliffs?" is unreachable for such a player.
     - "You weren't at the cliffs." becomes reachable without the re-arm in finding 1.
   - **Fix site:** a quality check in CLCLIMB. The Cliff Key is q0, though, the same as a key blank (`playtest-2026-10-08-chest-lock.md`).
3. **Tyorvi's apology always offers "I have spoken to Ezrekal."**
   - It does so even in cured, endgame worlds (`Y1-03`, `Y1-16`). It is retail 1994 behaviour, and it now matters, because T5 makes the apology the normal way back.
   - Picking it after the cure was not tried.
4. **Atli's aftermath talk on the Thordis route is hard to start.** After the plant scene, Atli stood at (13078,29736,64), and five projected double-clicks missed him. The plateau rim may be occluding him [INFERENCE]. Thordis's options did not depend on it.

## Harness anomalies

1. **My first Xvfb died** when the backgrounding shell returned, and ScummVM came up on SDL's `offscreen` driver. I killed it and re-ran both as named services.
2. **An Escape** (a `load()` helper sending three after a load) opened the Pagan pause book in the cp12 world. Barks and menus drew over it (`Y3-*`), and it did not change the picks. A later save went through the book's save gump.
3. **Wandering NPCs.** `talk()` sometimes walked to a stale NPC read, at a distance of up to 14,000 units. Re-teleporting next to the NPC fixed it.

## Disk changes

- **Wrote:** `docs/playtest-2026-10-10-replies.md` and `docs/playtest-2026-10-10-replies/`, which holds 272 plates named by test ID.
- **Scratch,** in `/tmp/claude-1000/vrepl/`:
  - `game/`, `scummvm.ini`, `run.sh` and `lv_run.log` (6,057 lines);
  - `saves/`: `ultima8.001` is the last checkpoint copied in (cp7c), and `ultima8.002` is my T1 bank;
  - `sp/` (frames, plus `vrepl-t1-pre.sav`: Thordis route, poisoned, thordisToldTest 1, zealanMark 0);
  - `py/`, the `*.u8` source copies, `fl.py`, `fl2.py` and `savinfo.py`.
- **Stopped:** my ScummVM and Xvfb `:94`.
- **Not touched:** `~/lv-checkpoints` (read only; cp23 md5 `ef6fd2ad…` unchanged), `shared/`, and every source, builder, map, fork, TODO or HANDOFF file. Nothing was committed.
