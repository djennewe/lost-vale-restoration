# Compiler wave 2, instance B: steps 11-16 hand-overs, Tiny Tar, Sacred Circle (2026-10-07)

Change under test: compiler wave 2 (commits `c89bf07..a2aaf16` on `main`).
Artifacts: EUSECODE `13ccb939` (1,524,536 bytes), FIXED `14774b0b`, U8SHAPES
`a611e9be`, TYPEFLAG `9f534e59`. The session log names the same bytes:
`usecode/eusecode.flx: dbce29589ae46b798dc8056c84dddcd3, 1524536 bytes`.
Plates are in `docs/playtest-2026-10-07-wave2-b/` (640x400).

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| B1 | Ezrekal's elixir lands the shape-395 frame-13 bottle in the pack | **PASS** |
| B2 | Tyorvi's Key to the Clouds chain: key in the pack, `givenTea` 1 | **PASS**; the negative control fails, with a duplicate key (finding 3, an older defect) |
| B3 | Tiny Tar: duration measured, crack walked before it ends | **PASS**: 1,378 ticks (about 25.8 s) of tiny and free, down from 2,000. **New visual defect:** about 2 s of black screen at the shrink and again at the regrow (finding 1) |
| B4 | Sacred Circle: cure, `shieldFixed`, shield in pack, walk home, Avatar free | **PASS** on every stated end state. **New animation defect:** every kneel plays as a walk step (finding 2) |
| B5 | Log hygiene | **PASS** on the five named counts, all 0. The other 96 warnings are `Unhandled intrinsic`, all `Camera::getX/Y/Z`, and they cause finding 1 |

Neither new defect blocks the quest. Both come from wave 2: rule 1 for finding
1, and rule 4 for finding 2.

## Method and isolation

This was an isolated instance. I used display `:78`, game copy
`/tmp/claude-1000/w2b/game`, config `/tmp/claude-1000/w2b/scummvm.ini` and
saves `/tmp/claude-1000/w2b/saves/`. The game copy is a copy of
`shared/u8-lv-patched` with the four `shared/build` artifacts copied over it
the way `session.sh` `sync_one` does. I checked `sha256` for all five
destination paths, and every one matched `shared/build`. There was one ScummVM
pid for the whole session. I did not touch display `:77`, `shared/u8-lv-patched`,
`~/.config/scummvm` or `~/.local/share/scummvm`.

The driver is a copy of `/tmp/claude-1000/v1007/py/drv.py` and `h.py`,
re-pointed at `:78` and at my log. It runs the overlay console, which it
verifies open before it types and closed afterwards.

I loaded each checkpoint by copying it to `saves/ultima8.001` and running
`Ultima8Engine::loadGame 1`:
- `run-s12-root-given.sav` for B1 and B2;
- `run-s16-tinytar.sav` for B3;
- `cp22-shield-halves.sav` for B4.

These actions changed the game state:
- teleports, with cheats on only around each teleport;
- `MainActor::toggleCombat` once, because `run-s12` loads in combat;
- `debugflag_enable Object`;
- `UCMachine::traceClass` on `0x5AE` (FREE), `0x4E5` (TYPEPOTION) and `0x5A5`
  (SHADES), each with a matching `stopTrace`.

There was no `setGlobal` and no `Item::grab`. I picked every menu answer from
the screen. I drank the potion by double-clicking it in the pack, and I entered
the ceremony egg on foot.

The trace's `tick N running process P ... class C, offset O` lines time the
processes. I also took screenshots every 0.4-0.8 s, each stamped with wall time
and log offset.

## B1: Ezrekal's elixir, PASS

`run-s12-root-given.sav` loads with `hasTea` 0, `givenTea` 0, `sentToTyorvi` 1,
`haveMark` 1 and `avatarPoisoned` 1. `findShape 395` = 0, and `findShape 82`
lists the pack's q99 key 4528 and the Map 10 q20 key 8500.

Double-clicking Ezrekal logged `event 1 @ 0474:0333`, and her menu offered
**Can you help me?**, **Have you made the elixir?** and **bye**
(`B1-ezrekal-menu.png`). I picked **Have you made the elixir?**. She answered
"Yes, I have. Take it to him now you can." (`B1-ezrekal-elixir-answer.png`),
then "Hope it helps him, I do." (`B1-ezrekal-hope-it-helps.png`).

Results:
- `hasTea` = 1.
- `findShape 395` returned **exactly one** item: `Item 5853 (shape 395)
  (uc: ERTHREAG), 13, (7, 9) q: 0, f: 0x200c` (`FLG_CONTAINED|FLG_OWNED|fast`).
  It is in the pack (`B1-pack-after-elixir.png`). Weight stayed at 30, since a
  family-9 item at q 0 weighs nothing.
- **`give()` returned true.** The call site is `if give(...) {} else if
  createNear(myMan, TypeBottle, 13, ...)`. If give returned false, or a stale
  register read as false, there would be a second bottle on the ground. There is
  one item world-wide.
- **Nothing was created and then destroyed.** The only `give` site in
  `lv-patched/EZREKAL.UNK` is line 3431, with `quan` 0. In `FREE::give` the
  reagent branch skips `setQuantity` when `quan` is 0, so the bottle lives on at
  q 0. Line 3233 of the current file is not a give site.

**Negative control.** When I talked to Ezrekal again after the Key hand-over,
her menu had **Can you help me?**, **I would speak to you of Tyorvi.** and
**bye**. The elixir option was gone (`B1x-ezrekal-menu-after-elixir.png`), so
no second bottle can be got.

## B2: Key to the Clouds, PASS (negative control fails, finding 3)

I teleported beside Tyorvi (115) on Map 10. Double-clicking him logged
`event 1 @ 0473:033D`. His menu was **I have spoken to Ezrekal.**, **Do you have
the Key to the Clouds?**, **I have something for you from Ezrekal.** and
**bye** (`B2-tyorvi-menu-1.png`). He was sober on the first roll; his drunk
lines are the "Shomething from Ezkkre..." set.

I clicked, from the screen:

    I have something for you from Ezrekal.  -> "Want nothing from that old hag do I..."
    It is an elixar.                        (B2-tyorvi-menu-2/3)
    It will heal your dreams.               -> "Heal my dreams, you say? ..."
    Just try it, please.                    -> "Oh, all right. Give it to me."  (B2-tyorvi-give-it-to-me)
       ... wait(1000): about 33 s with no menu ...
    May I have the Key to the Clouds?       (B2-tyorvi-may-i-have-key-menu)
                                            -> "Well, treacherous it is, but brave you are... Here, here the Key to the Clouds is."
                                            -> "Now, rest I must. Maybe dream I will not."  (B2-tyorvi-rest-i-must)

Results:
- `givenTea` (`0x425`) = 1.
- `findShape 82` went from 2 to **3**. The new item is
  `Item 14552 (shape 82) (uc: KEY), 0, (0, 0) q: 0, f: 0xc` (contained, owned).
- Weight went from 30 to 40.
- Again exactly one item was created, so `give()` returned true and
  `createNear` did not run (rule 2).

**Note for whoever reads the wave-1 R6 note.** "Want nothing from that old
hag" is the **sober** reply. After "Oh, all right. Give it to me." the case runs
`wait(1000)`, so the **May I have the Key...** menu takes about 33 s to
appear. R6's "the conversation closed by itself" was most likely that wait,
and not a dead branch.

**Negative control: FAIL (finding 3).** `hasTea` stays 1, so a second talk
offers **I have something for you from Ezrekal.** again
(`B2x-tyorvi-menu-after-key.png`). I ran the same chain again. It ended in
**May I have the Key to the Clouds?** (`B2x-second-chain-may-i-have-key.png`)
and a **second key**: `Item 4676 (shape 82) ... (0, 0) q: 0, f: 0xc`.
`findShape 82` was then 4, and weight was 50 (`B2x-second-key-handed-over.png`).

## B3: Tiny Tar, PASS, with a new visual defect

`run-s16-tinytar.sav` loads with three frame-8 potions in the pack (3963,
8603, 14459), `shieldFixed` 1, `templeOpen` 0 and `avatarPoisoned` 0. I
teleported to Map 18 (2848, 6100, 0).

**Negative control, PASS.** Three 1.2 s south pushes at full size left the
Avatar at (2848, 6100, 0) every time.

I turned on `traceClass` for 0x5AE and 0x4E5, then double-clicked potion 14459
in the pack. I started pushing south 6 s later and kept pushing.

**Trace (ticks are the engine's tick counter):**

| tick | Δ from drink | event |
|---|---|---|
| 1784572 | 0 | `event 1 @ 04E5:00A9`. POTION process 4368 starts; makeAvatarTiny 4293 (FREE, offset 8121) runs the **same tick**. The caller does not wait: rule 5 is live |
| 1785064 | 492 | shrink loop (FREE 0x2140-0x218A); the first `Unhandled intrinsic 'Camera::getZ()'` |
| 1785196 | 624 | makeAvatarTiny's last run: `setAvatarInStasis(false)`. **The tiny Avatar can move from here** |
| (wall +12.7 s) | about 650 | `event 7 @ 05B0:0080` (EggTempleEntry): through the crack |
| 1786574 | 2002 | POTION's last run (end of `wait(2000)`); makeAvatarBig 6096 starts and sets stasis |
| 1786802 | 2230 | makeAvatarBig ends at full size |

- **Measured window:** the Avatar was tiny and able to move for 1786574 −
  1785196 = **1,378 ticks**. Shape 708 lasted about 1,738 ticks in total,
  including the two animations.
- **Previous window:** the potion used to wait for makeAvatarTiny before
  starting `wait(2000)`, so the window was 2,000 ticks. Wave 2 cuts it by 31%,
  which matches the brief's "~1400".
- **Wall clock:** during the run the counter advanced 2,002 ticks in about 37.5
  s (about 53 per second; three instances shared the CPU). So the window was
  about 25.8 s here, and about 23 s at the nominal 60 ticks per second.
- **The crack:** the Avatar went through it at about 12.7 s, about 1 s after
  release, because I was already pushing. `templeOpen` 0 → 1.
- **Regrow:** it ended at (2848, 6996, 8) inside the sanctum, shape 1, hp 30.
  The re-grow did not kill him.

Plates:
- `B3-01-drink-feeling-funny.png`
- `B3-02-shrink-lightning.png`
- `B3-03-crack-hint-bark.png`
- `B3-04-tiny-through-crack.png`
- `B3-05-temple-entry-bark.png`
- `B3-06-regrow-lightning.png`
- `B3-07-regrown-in-sanctum.png`

**The shrink and the regrow are not shown: the screen goes black for about 2
s each time** (finding 1). Frames 14-17 (10.0-12.2 s) and 56-59 (40.1-42.2 s)
have a mean brightness of 0.0-0.3, against about 65 for a normal frame
(`B3-08-shrink-black-frames-strip.png`, `B3-09-regrow-black-frames-strip.png`).

## B4: Sacred Circle, PASS, with a new animation defect

`cp22-shield-halves.sav` loads on Map 17 with halves 2632 (frame 0) and 7936
(frame 1) in the pack, weight 320, `avatarPoisoned` 1, `shieldFixed` 0 and
`inShadeScene` 0.

I teleported to Map 10 (20304, 17600, 4), then made one 1.5 s walk north. The
log shows `Item: 9205 (shape 73) calling usecode event 7 @ 05A5:0080`, then
`event 15` on 107, 106 and 116.

From the screen I clicked **Let's be reasonable!** (`B4-01-first-ask.png`),
**Yes, Priestess.** (`B4-02-second-ask.png`) and **Please, High Priestess.**
(`B4-03-heal-ask.png`). The scene ran from hatch to release in about 623 s of
wall time; the hatch process 2832 ran from tick 1195486 to 1230234.

**End state:**
- `avatarPoisoned` 0, `shieldFixed` 1, `inShadeScene` 0.
- **The shield is in the pack:** `findShape 539` = 1, `Item 14869 (shape 539)
  (uc: SHIELD), 2, (0, 0) q: 0, f: 0xc`. Both halves were consumed, and weight
  went 320 → 280. The "I take up the Shield of the Ancients..." bark showed
  (`B4-07b-take-up-shield-bark.png`). There were no frame-4 shield and no
  `Skipping invalid shape` line during the scene.
- **They walk home.** Ezrekal walked west and then north out of view, followed
  by Thordis and then Atli (`B4-07c`, `B4-07d`,
  `B4-10-send-home-sequence-strip.png`). Each was then teleported home: Atli
  (19200, 6400, 0), Thordis (6144, 6656, 0), Ezrekal (12800, 12544, 0).
- **The Avatar ends free.** He was at (20456, 17324, 0) with `f: 0x2041`. A
  1.2 s walk moved him to (20456, 17124), and the camera stayed on him
  (`B4-08-after-walk-free.png`).
- The three send-home processes ran one after another (3640 Ezrekal, 3659
  Thordis, 3849 Atli; about 50 s together), and the Avatar stayed in stasis
  until the last finished. This is expected, because the hatch calls them as
  statements, which is rule 2.

**Negative control, PASS.** After the scene I walked south out of the egg box
and back in. The log shows no `event 7`, and the flags and the elders'
positions were unchanged. `doneShades` holds.

What played on screen:
- the squabble with the Avatar's look-left/right;
- "Here are both pieces, Priestess.";
- the whole shield (`B4-04-halves-whole.png`);
- the white reforge flash (`B4-05-reforge-flash.png`);
- the shades' yellow lines;
- "I feel better... But I'm still so weak!" (`B4-07-cured-bark.png`).

**Overlapping barks.** At the reforge, Ezrekal's "Yes! Yes! Knew, done it could
be, I did!" (spawned, so no wait under rule 5) stood on screen together with
Atli's "Whole, it is! Forgiven us, the gods have!" for about 4 s. Both stayed
readable (`B4-06-reunited-overlapping-barks.png`). I saw no other overlaps.

**Animation glitch (finding 2).** Every kneel in the scene plays as a walk step.
At **Please, High Priestess.** the Avatar strides instead of kneeling, twice
(KNEEL_DOWN, then KNEEL_UP). He ends about 150 units further south, beside
Ezrekal: (20456, 17324) against the (20456, 17176) recorded on 09-26
(`B4-09-heal-kneel-plays-as-walk-strip.png`). Thordis's and Atli's "kneel" at
"Wise Priestess..." and "You we blamed..." are single steps as well.

## B5: log hygiene, PASS on the named counts

Whole session (7,699 lines; log at `/tmp/claude-1000/w2b/lv_run.log`):

| pattern | count |
|---|---|
| `Non-existent process` | 0 |
| `stuck in process loop` | 0 |
| `Segmentation` | 0 |
| `Assertion` | 0 |
| `Cycle in paint` | 0 |
| `Unhandled intrinsic` | **96**: 32 each of `Camera::getX()`, `Camera::getY()` and `Camera::getZ()`, all during the potion's shrink and regrow loops (finding 1) |
| `Skipping invalid shape` | 1: `539,4`, at the load of `run-s16-tinytar.sav` (09-07), which predates LV-RESTORE change 13. None during this session's ceremony |
| `segment 0000`, `Item::combine` | 0 (the Passage Test was not run here) |

## Findings

1. **New (wave 2, rule 1): the Tiny Tar shrink and regrow now black out the
   screen for about 2 s each, and the animations cannot be seen.**
   - **What is happening.** `lv-patched/FREE.UNK:1395-1410` (makeAvatarTiny)
     and `:1440-1484` (makeAvatarBig) do `Camera::setCenterOn(0)`, then on
     every frame step
     `Camera::move_to(Camera::getX(), Camera::getY(), Camera::getZ() ∓ 1, map)`.
     Until wave 2 the parser dropped every `Camera::` call. Now they compile:
     `free.dis` 0x2120-0x212D has `calli 00C5h/00C4h/00C3h`. This engine does
     not implement those three intrinsics (`convert_usecode_u8.h:249-251`
     marks them "Unused"). Each call logs `Unhandled intrinsic` and returns
     0, so `move_to` parks the camera near (0, 0, 255).
   - **Evidence.** Frames 14-17 and 56-59 are black. The 96 warnings fall
     exactly in the two loops (first at tick 1785064, the shrink loop at
     0x2140). The final `Camera::setCenterOn(Avatar)` restores the view.
   - **What does not break.** Nothing in the quest: the Avatar shrinks,
     passes the crack and regrows.
   - **The same idiom elsewhere.** `changeRef` (`FREE.UNK:864-865`) reads
     `Camera::getX/getY` too, and the AOSCENE comment already warns about
     them.
   - **Fix candidates.** Drop the `Camera::move_to(Camera::get*…)` lines
     from the lv-patched copy, or implement the three getters in the fork.
   - **Confidence:** high.
2. **New (wave 2, rule 4): `AS_KNEEL_DOWN` and `AS_KNEEL_UP` compile to
   0 (`AS_WALK`), so every kneel in SHADES is now a walk step.**
   - **Where it shows.** `u8c_symbols.py:988` lists both as unpinned, and
     `test_symbol_retail_pins.py:144` keeps them in `UNPINNED`. `shades.dis`
     0x1E74 shows `push byte +0` before `spawn 057Ch 15E7h` (realDoAnim)
     for `Avatar.realDoAnim(AS_KNEEL_DOWN, Avatar.getDir())`. SHADES has 8
     such sites (lines 353, 366, 483, 489, 499, 500, 515, 527).
   - **Why it is new.** Before rule 4 those realDoAnim calls did nothing.
     Now the Avatar takes two steps in his facing direction at the heal and
     two at "Here are both pieces", and Thordis and Atli each take steps
     where they should kneel.
   - **Effect on play.** Harmless here, because the scene does not depend on
     the Avatar's final spot. Engine `Animation::startKneeling` = 34 and
     `stopKneeling` = 50 (`animation.h:66, 82`) are the likely values, but
     the pin is the author's call.
   - **The same kind of gap.** `RIGHT` is also unpinned (push 0 = RANDOM),
     at `Thordis.turnToFace(0, RIGHT, …)`.
   - **Confidence:** high on the cause; the bytes and the 148-unit
     displacement agree.
3. **Older defect: a duplicate Key to the Clouds on every re-run of
   Tyorvi's chain.**
   - **What happens.** `TYORVI.UNK:374-377` adds **I have something for you
     from Ezrekal.** whenever `hasTea` and `haveMark` are set, and nothing
     clears `hasTea` or tests `givenTea` there. Each further conversation
     re-offers the chain, and **May I have the Key to the Clouds?** gives
     another key. I got two keys in two conversations (14552, 4676).
   - **Why it is not wave 2.** The chain needs the `give()` repair from
     09-02 and nothing from wave 2. Wave 2 only makes `if give` read the
     true Boolean, which removed the chance of a ground copy as well.
   - **Fix.** Gate the option on `givenTea = false` as well.
4. **Older defect: Tyorvi does not drink the elixir; the bottle stays in the
   pack.**
   - **What happens.** The sober **Just try it, please.** branch
     (`TYORVI.UNK:2081`) searches `foreach item where (type = TypeBottle)
     and (frame = 13) within container Avatar` without `recursive`. The
     bottle is inside the backpack, so the search finds nothing.
   - **Evidence.** Item 5853 was still in the pack after both chains.
     Wave-1 R6 saw the same thing (11991 "still in a container").
   - **The other branch.** The drunk **Shut up and drink it!** branch
     (`:2111`) does use `recursive`.
   - Faithful to the 1994 text; a one-word fix in the lv-patched copy.
5. **`sendThordisHome` walks Atli.** The second loop of `SHADES.UNK:803-825`
   says `Atli.realDoAnim(AS_WALK, north)`, a 1994 typo. Since rule 4 it is
   visible: during Thordis's send-home she stands still while Atli takes
   about 26 steps north, and then Thordis is teleported.
6. **Wave-1 R6's "the conversation closed by itself" was most likely the
   `wait(1000)` after "Oh, all right. Give it to me."** The Key menu came up
   about 33 s later on both of my runs.

## Harness anomalies

1. `CameraProcess::moveToAvatar` never matched the driver's expect pattern, so
   it reported "no reply" twice per call. It is harmless here: every teleport
   was followed by a follow-capable camera (`f: 0x2041`).
2. My first `goto` at the crack bounced between (2804, 6080) and
   (2908, 6080), because the crack's walls reject the approach at an angle. A
   direct teleport to (2848, 6100) gave the documented spot.
3. At the start, the redirect `>` failed on existing files (noclobber), so
   Xvfb never started on the first try. `start.sh` uses `>|`.

## Disk changes

- Wrote `docs/playtest-2026-10-07-wave2-b.md` (this file) and the 39 plates in
  `docs/playtest-2026-10-07-wave2-b/`.
- Scratch, all under `/tmp/claude-1000/w2b/`:
  - the isolated game copy `game/` and `scummvm.ini`;
  - `saves/` (`ultima8.001` holds `cp22-shield-halves.sav`, the last loaded;
    ScummVM wrote `ultima8.000` and `timestamps`);
  - the session log `lv_run.log`;
  - `start.sh` and the driver `py/`;
  - frame films `sp/b3film/` and `sp/b4film/`;
  - disassemblies `sp/shades.dis` and `sp/free.dis`.
- Nothing under `shared/`, `~/.config/scummvm`, `~/.local/share/scummvm` or
  `~/lv-checkpoints` was written. No source, builder, map, fork, TODO, HANDOFF
  or commit was touched. The session and Xvfb `:78` are stopped.
