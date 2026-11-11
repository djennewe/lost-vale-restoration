# Steps 15 to 18 unbroken, the exit-test tier (2026-09-26)

HEAD `449f954` (code at `da1ca4b`, which makes AOSCENE play QUAKE3 in place of
SFX 0). `shared/build/` matched `ARTIFACTS.sha256` for all four artifacts;
`session.sh start` synced `USECODE/EUSECODE.FLX` into `shared/u8-lv-patched/`
(the engine logged `eusecode.flx: aae44805...`, 1,505,327 bytes). Binary
`scummvm-lv/scummvm` (built 25 September 23:13), 640x400 canvas, crop
`+565+336`, `usehighres=true`. Plates are in
`docs/playtest-2026-09-26-steps-15-18-unbroken/`, named by test ID.

**One ScummVM process ran the whole chain: PID 3024718, started 03:04:52 CDT,
still alive at 04:32:21 CDT when `session.sh stop` killed it.** Cheats stayed
off and no debugger write was sent.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| U0 | One process, no writes | PID 3024718 at start and at end; 0 `Cheats =` lines, 0 teleport, `setGlobal`, `Item::grab`, `CameraProcess`, or `toggleCombat` in the log; no `Segmentation` line | **PASS** |
| A1 | Map 17 to Map 10 on foot | Map 17 exit fired south of (5440, 11060); Map 13 descended z 116 to 0 on the climb tiles, no fall; trigger 206 landed (7168, 23296, 8) on Map 10 | **PASS** |
| A2 | Sacred Circle ceremony (step 15) | hatched (`05A5:0080`) on a walk north from (20304, 17528); answers **Let's be reasonable!**, **Yes, Priestess.**, **Please, High Priestess.**; `avatarPoisoned` 1 to 0, `shieldFixed` 0 to 1, `inShadeScene` 0 | **PASS** |
| A3 | Restored shield into the pack | "I take up the Shield..." bark; `findShape 539` = 1, item 12490 frame 2, in the pack; weight 320 to 280 | **PASS** |
| A4 | Camera follows afterwards | view on the Avatar with the elders gone; `f: 0x2041` at every read over the walk north to the Gunnar village | **PASS** |
| A5 | Send-home | Atli (107) at (19200, 6400), Thordis (106) at (6144, 6656), Ezrekal (116) at (12800, 12544) | **PASS** |
| A6 | Hrodny's key (step 16) | first talk name and job only (**What is your name?**, **bye**); second talk **I have been healed!** then **How can I open the temple?**; bag 14775 at (19588, 23284, 0) holding key 14774 q 20; `hrodnyMet` 1, `spokeTemple` 1 | **PASS** |
| A7 | Key and chest | bag dragged in (`Dropped item in backpack`), weight 280 to 300; key on chest: `Target result: Item 8980 ... shape 618`, then `findShape 78` lists 8980 | **PASS** |
| A8 | Tiny Tar from the chest | three frame-8 potions (8981, 8982, 8983) dragged in; weight 300 to 330; chest empty | **PASS** |
| A9 | Crack at full size (negative control) | three south pushes from (2868, 6108), inside the crack column: zero displacement | **PASS** |
| A10 | Crack as Tiny Tar, `templeOpen` (step 16 end) | 8982 drunk (`04E5:00A9`), shape 708; south to (2868, 6284); `EggTempleEntry` (`05B0`) fired; `templeOpen` 0 to 1; "I am through..." bark | **PASS** |
| A11 | **Shield on the altar (step 17)** | `EggAOCeremony` hatched (`05A7:0080`); first bark, about 7 s longer before the white fade than on 09-26 R2, white, the three-god pan, "It is done. The Ancient Ones are free..."; `godsFree` 0 to 1; god frames 0/1/2 to 3/4/5; **no fault, same PID** | **PASS** |
| A12 | Leaving the sanctum | full size north from (2848, 6288): refused (slid to 2920, 6216); 8983 drunk at x 2848; shape 708 out to (2848, 6016); trigger 210 to Map 10 | **PASS (second potion needed, as before)** |
| A13 | Endgame (step 18) | `EggEndgame` (`05AA:0080`) hatched on a walk north from the pad; `endgameStarted` 1, `hasBag` 1; bag 13047 (vol 18/32) holds six reagent stacks, frames 0, 6, 8, 9, 10, 14, each q 25; weight 330 to 490; a walk east moved him 208 units | **PASS** |
| A14 | Closing bark of the endgame | 11 frames over about 22 s fully black apart from the cursor (70 lit pixels each); the last line is not seen | **FAIL (unchanged from 09-26)** |
| A15 | QUAKE3 rumble audible | the harness's ScummVM opened PulseAudio but `pactl list sink-inputs` listed no stream; no screen shake in any frame (shift search, 0 px) | **NOT DEMONSTRATED** |

The pass condition holds: ceremony (`avatarPoisoned` 1 to 0, `shieldFixed`
0 to 1, shield in pack), `templeOpen` 0 to 1, `godsFree` 0 to 1 with the pan,
`endgameStarted` 1 and `hasBag` 1, in one process lifetime with no debugger
write.

## Method

Saves and `scummvm.ini` were copied to the scratchpad first (md5
`3e7dc241...`, `083de199...`, `a143fa3b...`). `cp22-shield-halves.sav` was
copied over `ultima8.001` before the engine started. After `start`, Devon's
opening menu was closed with **Goodbye.**, then `Ultima8Engine::loadGame 1`
(chord, command, Return, no `exit`) loaded cp22: Map 17, (7212, 1652, 0),
halves 2632 and 7936 in the pack, weight 320, `avatarPoisoned` 1, all other
quest flags 0 (`A0-start-map17-memorial-hall.png`). That load is the one
harness action before play; everything after it is in the one process.

Console use after the load: `debugflag_enable Object` (logging only),
`ObjectManager::objectInfo`, `ObjectManager::findShape`, and
`UCMachine::getGlobal`. The driver (the 09-26 scratchpad `drv.py`) confirms
the console is open from its border row before typing and closed after, so no
command letters reached the world. Combat mode never came on: of 512
`objectInfo 1` reads, none had `0x800` in `flags` (values 0, 8, 400, 408), so
no `toggleCombat` was needed. Every walk was a right-button burst, every
answer, pickup, key use, and potion a mouse action on what the screen showed.

Routes were the 09-26 record's waypoints, with two changes noted in the
sections below.

## A1: Cloud City to the vale, PASS

Map 17 route (6064, 1648), (6064, 2096), (5392, 2096), (5392, 6000),
(5392, 11000) to (5440, 11060), two stalls freed by the eight-direction
probe. One 2.2 s burst south crossed the exit: `Unloading map 17` /
`Loading Fixed items in map 13` at (4096, 1384, 116); the burst carried him
past the 09-26 arrival point (4096, 832, 120)
(`A1-map13-summit-arrival.png`). The climb-tile descent ran 54 read-and-walk
cycles from tile 3 to the base at (4064, 10144, 0), z falling monotonically,
hp 30 throughout (`A1-map13-base-after-descent.png`). The walk west to
trigger 206 landed on Map 10 at (7168, 23296, 8).

## A2 to A5: the Sacred Circle, PASS

The 09-26 Map 10 route reached (20456, 17976, 4); the sidestep
(20330, 17736), (20330, 17520) ended at (20304, 17528)
(`A2-circle-approach-before-hatch.png`). A 1.5 s walk north hatched
`EggShades` (`Item: 9205 (shape 73) ... 05A5:0080`), and the elders arrived
(`event 15` on 107, 106, 116; `A3-ceremony-hatched-elders-arrive.png`).

The scene played as on 09-26: the quarrel ("Liar! Gunnar's clan, tradition
broke!", "Hoskuld, the shield stole!..."; `A3-squabble-*.png`), **Let's be
reasonable!** from **Can't you two get along!?** / **Let's be reasonable!**
(`A3-first-ask.png`), the Priestess's condition
(`A3-priestess-shield-condition.png`), **Yes, Priestess.** from **Yes,
Priestess.** / **No, it is mine now...** (`A3-second-ask.png`), "Here are
both pieces, Priestess." with the halves on the grass
(`A3-halves-on-ground.png`), the whole shield (`A3-shield-restored-whole.png`,
`A3-reunited-bark.png`), the Shades in yellow at the bottom-left
(`A3-shade-*.png`), the heal offer (`A3-priestess-offers-heal.png`),
**Please, High Priestess.** from **Please, High Priestess.** / **No, thanks
anyway.** (`A3-heal-ask.png`), "I feel better..." (`A3-cured-bark.png`),
the temple hint, and the hand-over (`A4-take-up-shield-bark.png`). The white
reforge flash fell between two 2 s frames and was not caught. The console
stayed closed from the hatch until the view was back on the Avatar
(`A4-scene-ended-camera-on-avatar.png`).

Reads after: `avatarPoisoned` 0, `shieldFixed` 1, `inShadeScene` 0,
`godsFree` 0, `templeOpen` 0; Avatar (20456, 17176, 0), weight 280;
`findShape 539` = 1, item 12490 frame 2 at pack slot (8, 19) later
(`A4-restored-shield-in-pack.png`). The three elders read at home
coordinates. The walk north to (21680, 9168) kept `f: 0x2041` at all 40 reads
checked (`A5-walk-north-camera-follows.png`).

## A6 to A8: Hrodny, the key, the potions, PASS

Hrodny (113) wanders; two strikes missed while she moved and a third opened
**What is your name?** / **What do you do?** / **bye**
(`A6-hrodny-first-menu.png`). **What is your name?** ("Hrodny, daughter of
Ulmar, I am."; `A6-hrodny-name-bark.png`), then **bye**. The second talk
(two misses, then a hit) opened **I have been healed!** / **The Shield of the
Ancients is restored!** / **bye** (`A6-hrodny-post-ceremony-tier.png`).
**I have been healed!** ("See, so I do! For you, good!..."), then a menu of
**How can I open the temple?** / **bye**; the shield option was gone, as on
09-26 (`A6-hrodny-how-open-temple.png`). The answer played the potion story
and the thief lead, "A thief-thing, dragging a bright small weight up the old
temple road, southward." (`A6-hrodny-thief-lead.png`), and ended the talk.

`findShape 637` listed bag 14775 at (19588, 23284, 0), one item;
`findShape 82` key 14774 q 20 in it. The route south with the fence detour
(20424, 10388) to (20424, 11460) ran with one stall. The drag from
window (294, 231) onto the Avatar logged `Dragging item 14775` /
`Dropped item in backpack`; weight 280 to 300
(`A7-key-bag-on-temple-road.png`).

Back at the chest, the pack gump was dragged aside; the first bag opened was
the empty 1754, so it was closed and 14775 opened. Double-click on the key
(`event 1 @ 0052:04BB`), then a click on the chest: `Target result: Item 8980
(class Container, shape 618) (uc: LCHST_EW)`. `findShape 618` then read 0 and
`findShape 78` listed 8980 as `CHEST_EW`. The chest opened on the potions
(`A8-chest-open-potions.png`); three drags, each `Dropped item in backpack`
(8982, 8981, 8983); weight 330, chest empty
(`A8-three-potions-taken-chest-empty.png`).

## A9 and A10: the crack, PASS

Trigger 211 landed at (3072, 2024) on Map 18 (`A9-map18-temple-arrival.png`).

**Route change:** the 09-26 route's second leg, (3007, 4671) to
(2847, 4671), ran the Avatar north of the wall that crosses y about 4600, and
it paced between x 2772 and 2876 at y 4572 until the budget ran out. The gap in
that wall is at about x 3072. Routing (3080, 4560), (3080, 4780),
(2847, 4780), (2847, 5700) got through, and a walk south hatched
`EggCrackHint` (`05B1:0080`): "The stone here is split from top to bottom --
and there is open air beyond it. But the gap is no wider than my hand."
(`A10-crack-hint-bark.png`).

One east step put him at x 2868, inside the 2848..2879 column. **Negative
control:** three 1.2 s south pushes at full size from (2868, 6108): position
unchanged (`A10-full-size-at-crack-refused.png`). Double-click on potion 8982
logged `event 1 @ 04E5:00A9`; he read shape 708, weight 820
(`A11-drink-tiny-tar.png`). One south push carried him to (2868, 6284);
`EggTempleEntry` fired (`Item: 16643 ... 05B0:0080`), `templeOpen` read 1,
and he barked "I am through. The air in here is old and very still."
(`A11-through-the-crack.png`). He was back to shape 1, weight 330, at the next
read, about 6 s later (`A11-regrown-in-sanctum.png`).

## A11: the altar, PASS with no fault

State before the walk: `shieldFixed` 1, `templeOpen` 1, `godsFree` 0; shield
12490 in the pack; potions 8981 and 8983 at frame 8, 8982 at frame 0; gods
4821, 4896, 5179 at frames 0, 1, 2. Route (3263, 6300), (3263, 7600),
(3460, 7730), then (3460, 8600), (3280, 8590). The last walk into
(3240, 8600) hatched `EggAOCeremony` (`Item: 16642 (shape 73) ... 05A7:0080`).
From then the console stayed closed and a frame was taken about every 0.84 s
for 100 s, with the process checked alive at each frame. Times are from the
first frame, taken within about 1 s of the hatch.

| t (s) | Screen |
|---|---|
| 0 to 1.7 | altar view, no bark |
| 2.5 to 11.0 | "I place the artifact upon the altar. The ancient symbols begin to glow." (`A12-altar-hatch-place-artifact-bark.png`) |
| 11.9 to 17.7 | same view, no bark, no fault (`A12-altar-t13s-no-fault.png`); on 09-26 the crash fell 8 to 10 s after the hatch |
| 18.5 to 19.4 | fade to white begins (`A13-fade-to-white-begins.png`) |
| 20.2 to 33.1 | full white (`A13-white.png`) |
| 33.9 to 41.6 | fade in on the first god, then the pan across the three gods breaking out of the amber (`A13-fade-in-first-god.png`, `A13-pan-first-god.png`, `A13-pan-god-shattering.png`, `A13-pan-third-god.png`) |
| 42.5 | back on the altar (`A13-pan-return-to-altar.png`) |
| 44.1 to 55.1 | "It is done. The Ancient Ones are free. I can feel their gratitude and their power..." (`A13-it-is-done-bark.png`) |
| 56 to 100 | altar view, still |

**Timing against 09-26:** in R2 the white began about 12 s after the hatch;
here it began at about 19 s. The extra 7 s most likely falls in the stretch where AOSCENE now runs
`spawn safePlaySFX(QUAKE3, 255) -> return` before `FadeToWhite()`. That
reading comes from frame timing only (A15: the sound itself was not heard).

Reads afterwards: `godsFree` 1, `templeOpen` 1, `shieldFixed` 1; gods at
frames 3, 4, 5; `findShape 539` still lists 12490 in the pack; Avatar
(3196, 8556, 0). The log from the hatch to the reads carries only the god
`event 2` ticks, `Cycle in paint` lines, and the Avatar's `event 18`.

## A12: out of the sanctum, PASS with the second potion

Route (3460, 8600), (3460, 7730), (3300, 7650), (3263, 6300), (2868, 6260) to
(2848, 6288). **Negative control:** two full-size north pushes slid him east
to (2920, 6216) and no further (`A14-full-size-north-refused.png`). Diagonal
steps alternate between x 2920 and 2848 (72 units); one attempt did not move
him, with a freed god standing beside him. At (2848, 6288), potion 8983
logged `04E5:00A9` (`A14-drink-second-potion-inside.png`), shape 708, and two
north pushes brought him to (2848, 6176) and (2848, 6016)
(`A14-back-through-crack.png`). The route back through the wall gap at
x 3080 and north to (3056, 1728), then a burst north, fired trigger 210:
Map 10 at (18432, 22584) (`A15-map10-arrival-from-temple.png`).

## A13 and A14: the endgame, PASS with the invisible closing bark

`endgameStarted` read 0 on arrival. One 1.4 s walk north hatched
`EggEndgame` (`Item: 8188 (shape 73) ... 05AA:0080`). The barks played over
the Avatar (`A16-endgame-bark-*.png`), ending with "The elder presses a worn
bag into my hands. However deep I reach into it, there is always more within.
I shall not want for reagents again." (`A16-endgame-bag-bark.png`). Then the
screen went black for about 22 s; every frame in that stretch has only the
cursor's 70 lit pixels (`A16-endgame-black-closing-bark-invisible.png`). It
faded back in on the Avatar (`A16-endgame-after-fade.png`).

Reads: `endgameStarted` 1, `hasBag` 1, `godsFree` 1, `templeOpen` 1,
`shieldFixed` 1, `avatarPoisoned` 0; weight 490; bag 13047 (vol 18/32, six
items, weight 160) and six `ERTHREAG` stacks, frames 0, 6, 8, 9, 10, 14, each
q 25, in it. A walk east moved him from (18432, 22288) to (18640, 22288), so
stasis was released. ScummVM was still PID 3024718.

## Differences from the 09-26 run

1. **No segfault.** The altar scene ran to "It is done..." in the same
   process that had run steps 15 and 16. On 09-26 the same hatch faulted in
   this position in the chain.
2. **The white fade starts about 7 s later** (19 s against 12 s after the
   hatch), which fits AOSCENE waiting on the QUAKE3 sound process.
3. **The Map 18 inbound route needed the wall gap at x 3080.** The recorded
   waypoint (3007, 4671) leaves the Avatar north of the wall at y about 4600.
4. Object ids differ from 09-26 (shield 12490, key bag 14775, key 14774,
   chest 8980, reagent bag 13047), as expected for items spawned at run time.
5. The Map 13 arrival was at (4096, 1384, 116); the exit burst ran on after
   the map load.

## Findings outside the plan

1. **The QUAKE3 rumble cannot be heard in this harness.** ScummVM logged
   `Using SDL Audio Driver "pulseaudio"`, yet `pactl list sink-inputs` showed
   no stream, and QUAKE3 does not shake the view (0 px shift in every frame
   against the first). Confirming the sound needs a listener at a real
   desktop.
2. **`EggTempleEntry` and `EggCrackHint` hatch again on each crossing.**
   `05B0` and `05B1` each logged three times over the in and out trips. The
   entry egg setting `templeOpen` again is harmless; whether the hint bark
   repeating on the way out is wanted was not checked.
3. **The endgame's last line is still invisible**, as on 09-26 (finding 3
   there).
4. **The Sanctum's only exit is still the crack and a second potion.** A
   player with one potion left is sealed in.
5. `Unhandled intrinsic 154 'Npc::getNpcSlot()'` logged six times during the
   Hrodny talks, as on 09-26; the talks worked.
6. 94,636 `Cycle in paint dependency graph` lines in the whole log, the bulk
   near the Gunnar village fence (shapes 526, 426, 707).

## Harness anomalies

- **The mouse cursor defeated the console-open test.** The driver checks row
  y 268 of the window for the console border colour on every sampled pixel;
  the cursor, left at window (80, 263) by the last walk, painted white over
  one sample, and four chords were read as failures. An even count of chords
  left the console open, so nothing leaked. The test now allows three
  mismatched samples, and the chord loop tries nine times with a 2 s pause
  after the fourth.
- Hrodny needed two to three strikes per talk; the standstill test passed
  while she was already moving.
- The key bag and the empty bag in the pack look the same; the empty one was
  opened first.

## Disk changes

- `docs/playtest-2026-09-26-steps-15-18-unbroken.md` and the plates directory
  (new, 64 plates at 640x400 plus one 440x280 pack zoom).
- `~/.local/share/scummvm/saves/ultima8.000`, `ultima8.001`, `timestamps`,
  and `scummvm-history.txt` were overwritten during the session and restored
  from copies taken first; `ultima8.000` md5 `3e7dc241...` and `ultima8.001`
  md5 `083de199...`, as before.
- `~/.config/scummvm/scummvm.ini` restored byte for byte (md5 `a143fa3b...`).
- `shared/u8-lv-patched/USECODE/EUSECODE.FLX` synced from `shared/build/` by
  `session.sh start` (untracked).
- Scratchpad: session log copied to `unbroken.log`; `drv.py` gained the
  cursor-tolerant console test and its plate directory now defaults to this
  run's.
- No source edited, nothing rebuilt or committed; `TODO.md` not edited. The
  session is stopped (Xvfb and ScummVM killed).

## Endgame last line (HEAD)

HEAD `3fe7143`, which moves the closing bark ahead of `FadeToBlack`.
`shared/u8-lv-patched/USECODE/EUSECODE.FLX` sha256 `4a78038d...`, equal to
`shared/build/` and `ARTIFACTS.sha256`; the compiled string ends "It is time
to go home.". One process (PID 1675624) from `cp34-altar-ready-head-20260926.sav`
(copied over `ultima8.001`, loaded with `Ultima8Engine::loadGame 1`) through
the altar, the crack and the endgame. Cheats stayed off; no debugger write was
sent. Plates carry an `E` prefix in this record's folder.

| ID | Test | Observed | Verdict |
|---|---|---|---|
| E1 | Last line readable before the fade | the line is barked over the world for about 21.5 s, first page "And with the power ... It is time to go" (`E1-last-line-over-world.png`, `E1-last-line-zoom.png`), then a second page "home." for under 1 s (`E1-last-line-page2-home.png`, `E1-last-line-page2-home-zoom.png`); the fade starts about 1 s after the bark closes | **PASS** |
| E2 | Fade and return, Avatar walks | black from about 119.4 s to 120.9 s after the hatch (`E2-fade-begins.png`, `E2-black.png`), world back at 122 s (`E2-faded-back-in.png`); `endgameStarted` 1, `hasBag` 1; a walk east moved him from (18432, 22280) to (18640, 22280) (`E2-walked-east-after.png`); same PID, no `Segmentation` or `Assertion` line | **PASS** |

Route: the altar approach (3460, 7730), (3460, 8600), (3356, 8612); a walk
west to (3156, 8612) missed the egg (12752 at (3072, 8320, 24), range 6), and
a step north hatched it (`05A7`). The scene played as in A11 and left
`godsFree` 1. Out through the crack at x 2868 with the second potion (8983,
`04E5:00A9`), the wall gap at x 3080, trigger 210 to Map 10 at
(18432, 22480), then one 1.4 s walk north hatched `EggEndgame`
(`Item: 8657 (shape 73) ... 05AA:0080`). Frames every 0.56 s for 130 s with
the console closed.

| t after hatch (s) | Screen |
|---|---|
| 0.6 | black (opening fade) |
| 1.6 to 14.1 | "With the Ancient Ones freed..." |
| 19.7 to 32.7, 38.3 to 51.1, 53.3 to 71.8 | the three middle barks |
| 74.0 to 93.2 | "The elder presses a worn bag into my hands..." (`E1-reagent-bag-bark.png`) |
| 95.6 to 117.1 | the last line, page 1 |
| 117.1 to 117.7 | page 2, "home." |
| 118.8 to 120.9 | fade to black |
| 122.0 on | world, Avatar on the path |

Reads after: `godsFree` 1, `templeOpen` 1, `shieldFixed` 1, `avatarPoisoned` 0;
weight 330 to 490; bag 13036 (vol 18/32, six items, weight 160) and six
`ERTHREAG` stacks, frames 0, 6, 8, 9, 10, 14, each q 25.

**Finding E-F1: "home." gets a page of its own and shows for under a second.**
The bark's text widget is 194 by 55 (`bark_gump.cpp`, `TextWidget(..., 194,
55)`), five lines of font 6. The line runs one word past five lines, so the
engine pages it, and a page's time scales with its length: five characters
last about 0.6 s. A player reading the first page might miss the last word. A
line that fits five lines would show whole.

Disk: nine `E*` plates added; saves (`ultima8.000` md5 `3e7dc241...`,
`ultima8.001` md5 `083de199...`, `timestamps`, `scummvm-history.txt`) and
`scummvm.ini` (md5 `a143fa3b...`) restored from copies taken first; session
stopped.

## Endgame last line, split (HEAD)

HEAD `6e2f0c3`, which splits the closing line into two barks.
`session.sh start` synced `USECODE/EUSECODE.FLX` into `shared/u8-lv-patched/`,
sha256 `95ef5938...` (1,505,351 bytes), equal to `shared/build/` and
`ARTIFACTS.sha256`; the compiled strings are "And with the power of the
Ancient Ones now restored, I feel the path to Britannia opening before me at
last." and "The Guardian's prison weakens. It is time to go home.". One
process (PID 1938032) from `cp34-altar-ready-head-20260926.sav` (copied over
`ultima8.001`, loaded with `Ultima8Engine::loadGame 1`) through the altar,
the crack and the endgame. Cheats stayed off; no debugger write was sent.
Plates carry an `E3-` or `E4-` prefix in this record's folder.

| ID | Test | Observed | Verdict |
|---|---|---|---|
| E3 | Both barks whole and readable | bark 1 shows as one four-line page for 15.8 to 16.5 s (`E3-bark1-first-frame.png`, `E3-bark1-zoom.png`, `E3-bark1-last-frame.png`); bark 2 follows in the next frame as one two-line page, "...It is time to go home.", for 7.3 to 8.0 s (`E3-bark2-first-frame.png`, `E3-bark2-zoom.png`, `E3-bark2-last-frame.png`); the text mask is identical in all 46 frames of bark 1 and all 22 of bark 2, so neither pages and no word stands alone | **PASS** |
| E4 | Fade and return, Avatar walks | bark 2 closes 1.4 to 1.9 s before the fade (`E4-bark2-closed-before-fade.png`); dimming from about 125.4 s after the hatch (`E4-fade-begins.png`), black 126.4 to 127.4 s (`E4-black.png`), world back at 128.8 s (`E4-faded-back-in.png`); `endgameStarted` 1, `hasBag` 1, weight 490; a walk east moved him from (18432, 22288) to (18640, 22288) (`E4-walked-east-after.png`); same PID, no `Segmentation` or `Assertion` line | **PASS** |

Route as in E1 and E2: altar approach (3460, 7730), (3460, 8600), a step west
to (3200, 8648), and a step north hatched `05A7`; `godsFree` read 1 after an
80 s wait. Out: (3263, 6300) to (2848, 6312); potion 8983 double-clicked in
the pack (`04E5:00A9`), shape 708, three north pushes to (2860, 5996); the
wall gap at x 3080, (3012, 1708), and a burst north fired trigger 210 to
Map 10 at (18432, 22488), `endgameStarted` 0. One 1.4 s walk north hatched
`EggEndgame` (`Item: 4843 (shape 73) ... 05AA:0080`). Frames every 0.35 s for
140 s with the console closed; process count checked every 20 frames. Times
are after the hatch, which fell within 0.4 s before the log poll that saw it,
so each boundary carries about ±0.4 s.

| t after hatch (s) | Screen |
|---|---|
| 2.3 to 14.6 | "With the Ancient Ones freed..." |
| 20.5 to 33.5, 39.1 to 52.5, 55.3 to 73.8 | the three middle barks |
| 76.3 to 96.9 | "The elder presses a worn bag into my hands..." (`E3-reagent-bag-bark.png`) |
| 100.1 to 115.9 | bark 1, one page |
| 116.2 to 123.6 | bark 2, one page |
| 123.9 to 124.9 | world, no bark |
| 125.4 to 128.4 | fade to black and back |
| 128.8 on | world, Avatar on the path |

Finding E-F1 is closed: "home." now shows inside a two-line page for more
than 7 s. The split also shortened the time the first sentence stays up,
from about 21.5 s for the combined page to about 16 s.

Disk: 12 `E3-` and `E4-` plates added; saves (`ultima8.000` md5
`3e7dc241...`, `ultima8.001` md5 `083de199...`, `timestamps`,
`scummvm-history.txt`) and `scummvm.ini` (md5 `a143fa3b...`) restored from
copies taken first; `shared/u8-lv-patched/USECODE/EUSECODE.FLX` synced by
`session.sh start` (untracked); session stopped.
