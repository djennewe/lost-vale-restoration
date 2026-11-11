# Wave 2 final build, instance B: Tiny Tar and the Sacred Circle (2026-10-07)

Build under test: uncommitted work on top of `a2aaf16`. EUSECODE `8c5a8419`
(1,524,630 bytes), FIXED `c3d29a1f`, U8SHAPES `a611e9be`, TYPEFLAG `9f534e59`.
Every session log reads `usecode/eusecode.flx: e1fed4c81e85b86ff1b59810ab50f94a,
1524630 bytes`. The binary is `scummvm-lv/scummvm` (14:17:43), built after
fork commit `10d59e56` (13:53:31). Plates are in
`docs/playtest-2026-10-07-wave2-final-b/` at 640x400.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| B1 | Tiny Tar: shrink and regrow visible, no black screen, 0 `Camera::get*` warnings; window measured; crack walked; full-size push refused | **PASS**. Window 1,370-1,374 ticks. One harness caveat and one design-path finding (findings 1 and 2) |
| B2 | Sacred Circle: kneels play as kneels, enter-cast before exit-cast, end mark, cure, shield, walk home, Avatar free | **PARTIAL**. The Avatar's two kneels PASS, as do the cure, `shieldFixed`, the shield, the walk home and the release. **Thordis does not kneel** at "Wise Priestess..." (finding 3). Atli and Ezrekal's casts are not judged (no plate). The end mark is (20456, **17080**), 96 units north of the 09-26 mark (finding 4) |
| B3 | Tyorvi duplicate-key negative control | **NOT DEMONSTRATED**: the request budget ran out |
| B4 | Gold plaque and Message Scroll gumps | **NOT DEMONSTRATED**: budget. `cp22-shield-halves.sav` loads with `findShape 614` = 0 and `findShape 864` = 0, so it needs a map hop first (the traps.md "old save" entry) |
| B5 | Map 10 conversation exits (Ingjald, Hrodny, Ragnar) | **NOT DEMONSTRATED**: budget |
| B6 | Aramina's greeting spacing | **NOT DEMONSTRATED**: budget |
| B7 | Log hygiene | **PASS**: 0 `Unhandled intrinsic`, 0 `Non-existent process`, 0 stuck, 0 segfaults, 0 assertions. There were 42 `Cycle in paint`, all after the deliberate regrow death in finding 2 |
| — | Fork patch equals the fork diff | **PASS**: `git diff 01bd8879 HEAD -- engines/ ':!…detection_tables.h' \| diff -q - …0001-lost-vale-engine.patch` reported no difference |

The brief forbade `run_all_tests.sh`, `build_artifacts.sh`, `install_lv.sh` and
`build_scummvm.sh`, so none of them was run. I checked the isolated copy's five
artifact paths with sha256 against `shared/build`, and all five matched.

## Method and isolation

- **Display and files.** I used display `:78` and the game copy
  `/tmp/claude-1000/w3b/game`, which is `shared/u8-lv-patched` with the four
  `shared/build` artifacts copied over it the way `sync_one` does. Config was
  `w3b/scummvm.ini`, saves `w3b/saves/`, and ScummVM ran with `-x 1`.
- **Driver.** A copy of the w2c `drv.py`/`h.py`, re-pointed at `:78`, with
  its pgrep narrowed to `w3b/[g]ame`.
- **Sessions.** One pid per session. The logs are `lv_run.s01.log`,
  `lv_run.s02.log` and `lv_run.s03.log` (all from `run-s16-tinytar.sav`), and
  `lv_run.log` (from `cp22-shield-halves.sav`).
- **Game-state writes:**
  - teleports with cheats on, each followed by a toggle back to off;
  - `debugflag_enable Object`;
  - `traceClass` on 1454 (FREE), 1253 (POTION) and 1445 (SHADES);
  - 4× `CameraProcess::moveToAvatar` in session 1, before drink 1 only.
- **What I did by hand.** I drank every potion with a double-click in the
  pack. I walked through the crack. I walked into the ceremony egg from
  (20304, 17600): a 1.5 s north walk. I clicked every menu answer from the
  screen. There was no `setGlobal` and no `Item::grab`.

## B1: Tiny Tar, PASS

**Negative control.** At full size, three 1.5 s south pushes from
(2848, 5996) stopped at (2848, 6100, 0) every time (`B1-01`).

**Drink 1** (session 1, from (2848, 6100)):
- **Trace.** The use event is `event 1 @ 04E5:00A9`, process 5080. The
  makeAvatarTiny process 5084 ends at tick 1790420 (`setAvatarInStasis(false)`).
  The POTION process's last run, which starts makeAvatarBig (process 1391), is
  at tick 1791794. That gives a free tiny window of **1,374 ticks**.
- **Through the crack.** I held south. `EggTempleEntry` hatched
  (`event 7 @ 05B0:0080`, between ticks 1790420 and 1790436), the bark was
  "I am through. The air in here is old, and very still." (`B1-03`), and
  `templeOpen` went 0 → 1.
- **Regrow.** The Avatar regrew at (2812, 8356, 8) with hp 30 (`B1-04`).
  There were 0 `Unhandled intrinsic` lines, and no frame darker than a mean of
  52, against 0.0-0.3 for the black frames in the wave-2 report.

**Drinks 3, 4 and 5** (sessions 2 and 3):
- **Windows.** 1,370 ticks (drink 3) and 1,374 ticks (drink 2).
- **Drink 3.** It crossed the crack again (`05B0` hatched) and regrew at
  (2848, 6516) with hp 30.
- **Drink 5.** I drank on the open floor at (2848, 5520), with the following
  camera, so the whole animation could be filmed. The shrink plays lightning,
  the shape-708 lying frames and then the tiny figure (`B1-02-shrink-visible-open-floor.png`,
  also `B1-02-shrink-visible-strip-drink2.png` at the crack). The regrow plays
  "Uh oh...", lightning, the lying frames reversed and then the full Avatar
  (`B1-05-regrow-visible-open-floor.png`).
- **Warnings and brightness.** Every drink logged 0 `Unhandled intrinsic`.
  The lowest mean frame brightness across all five films was 52.0.
- **Wall time.** At about 49 ticks/s, the window is about 28 s here, or
  about 23 s at the nominal 60 ticks/s.

## B2: Sacred Circle, PARTIAL

**The hatch.** The walk-in logged `Item: 9205 (shape 73) calling usecode
event 7 @ 05A5:0080`, then `event 15` on 107, 106 and 116. The hatch
process ran as `type 528` (0x210, the retail hatch type). I picked from the
screen, in order:
1. **Let's be reasonable!** (`B2-01`);
2. **Yes, Priestess.** (`B2-02`);
3. **Please, High Priestess.** (`B2-03`).

**Avatar kneels: PASS.**
- **"Here are both pieces, Priestess."** He bends and kneels; the two halves
  pop out beside him; he stands and walks north to the altar (f446-f453,
  `B2-04-avatar-kneel-here-are-both-pieces.png`).
- **The heal.** He kneels down at f1044, stays down while Ezrekal casts
  (f1046-f1062, about 9 s), rises at f1064, and stands in the same spot
  (`B2-05-avatar-kneel-heal.png`).
- **Bytecode.** It agrees: the 8 SHADES realDoAnim sites push 49 (0x31) or
  50 (0x32). Engine 49 is `kneel2` and 50 is `stopKneeling` (`animation.h:81-82`).

**Thordis kneel: FAIL (finding 3).** Through her whole "Wise Priestess,
wrong we were..." bark (f858-f894) and on to f930, she stands upright. The
zoom is `/tmp/claude-1000/w3b/sp/thordis.png`. I did not make a plate of it.

**Not judged.** Atli's kneel at "You we blamed...", and Ezrekal's enter-cast
before her exit-cast. The film is on disk (`/tmp/claude-1000/w3b/sp/b2film/`,
JPEG every 0.35 s, f0-f1330), but I did not review those frames before the
budget ran out.

**End state:**
- `avatarPoisoned` 0, `shieldFixed` 1, `inShadeScene` 0.
- `findShape 539` = 1: `Item 14869 (shape 539) (uc: SHIELD), 2, (0, 0) q: 0,
  f: 0xc`, and weight went 320 → 280.
- **The elders went home:** Thordis 106 at (6144, 6656), Atli 107 at
  (19200, 6400) and Ezrekal 116 at (12800, 12544). I watched them walk out
  first (f1202 shows Ezrekal walking north).
- **The Avatar is free:** at (20456, 17080), `f: 0x2041`. A 1.2 s walk moved
  him to (20456, 17416) (`B2-06-after-walk-free.png`).
- **His mark is 96 units north of 09-26's (20456, 17176).** In the final
  frames he faces south (screen lower-left).

## Findings

1. **Harness caveat for Tiny Tar: `CameraProcess::moveToAvatar` parks the
   camera at the actor's centre with z = the Avatar's z (0).**
   - **Where it is.** `debugger.cpp:1268` uses `getCentre()`, and
     `item.cpp:461` keeps z as it is.
   - **What it does to the potion.** makeAvatarTiny's first
     `Camera::move_to(getX, getY, getZ() - 1)` then sends -1 into
     `ARG_UINT8`, which wraps to 255. During drink 1's shrink the view jumped
     about 255 px to a different part of the hall, and the Avatar was not on
     screen (`B1-06-drink1-shrink-camera-offset-harness-zcam0.png`).
   - **What a player sees.** With a camera that follows the Avatar
     (z = Avatar z + 20) the effect does not occur (drinks 2-5).
   - **Risk.** The same wrap would hit any player whose camera z is below
     18 when he drinks. It is not reachable by ordinary play as far as I
     know. Confidence: high on the mechanism.
2. **A regrow that cannot fit kills the Avatar, and leaves the camera
   detached.**
   - **What happened.** On drink 2 I kept walking north while tiny, and the
     Avatar ended at (2912, 4676), beside a barred gate. makeAvatarBig's
     `canExistAt` failed, so he regrew and died (hp 0, `B1-07`). 42
     `Cycle in paint 620 -> 15` lines followed.
   - **Design or defect.** Dying there is the 1994 design, and the PATCHED
     2026-07-27 comment confirms it.
   - **The stale comment.** That comment (`FREE.UNK:1450-1456`) says "No
     Camera::setCenterOn here on purpose: `::` is unsupported by our parser,
     so this routine's own Camera::setCenterOn(0) above is dropped". Since
     wave 2, `Camera::` compiles, so the `setCenterOn(0)` at line 1434 is
     real. The failure path returns without `setCenterOn(Avatar)`. The
     comment is now false, and the death screen runs with a parked camera.
   - **Impact.** Low, because the player reloads after a death. The comment
     should still be corrected.
3. **Thordis does not kneel (`SHADES.UNK:496`, `spawn
   Thordis.realDoAnim(AS_KNEEL_DOWN, 5) -> return;`).** She stays upright
   throughout her bark.
   - **Unconfirmed cause [INFERENCE].** One candidate is the `5`: realDoAnim
     resets the actor's anims, and direction 5 is not reachable for her
     facing. Another is that she is still busy from the spawned
     `turnToFace(4, 0, 7)` or a loiter when the kneel is spawned. I did not
     trace which.
   - **Atli** (line 502, direction 3) was not checked.
   - **Confidence:** high that she did not kneel on screen in this run.
4. **The end mark moved: (20456, 17080) against 09-26's (20456, 17176).**
   - **Source.** The scene's walks are relative (`pathfind(referent, 20)`,
     then 2 + 3 `AS_WALK` steps), so the mark depends on the approach and
     on step length.
   - **Before the kneels.** On screen, he walked straight from beside
     Ezrekal to the altar after the pieces kneel, so the kneels themselves
     did not displace him.
   - **The heal kneel.** It left his screen position unchanged
     (f1040 vs f1066).
   - **Reading.** 96 units equals 3 × 32, but I have not decomposed the
     walks. Whether 17080 is acceptable is the author's call.
5. **Class 0x35C (TYPEZEAL, the god statues) logs `event 2` (anim) on every
   animation tick** whenever `debugflag Object` is on: 728 lines in the
   first minute on Map 18. It is harmless, but it floods logs.
6. Process types on the real bytes: POTION `use()` pushes `0207h` (it was
   `0209h` in the w2c disassembly), and the SHADES hatch ran as type 528
   (0x210).

## Harness anomalies

- **The camera wrap in finding 1.** Do not use `moveToAvatar` before a Tiny
  Tar test.
- **The first walk after a Map 18 teleport onto (2848, 6100) did nothing in
  every direction.** The crack-hint bark was up. Mobility returned a few
  seconds later.
- **The empty bottle sits on top of the potion stack after every drink.** A
  drag within the pack to (335, 152) clears it; (345, 170), on the pack's
  bottom edge, does not.
- **`CameraProcess::moveToAvatar` never matches an expect pattern**, so the
  driver retries it, and it runs twice per call.

## Disk changes

- **Wrote** this report, and these plates in
  `docs/playtest-2026-10-07-wave2-final-b/`:
  - `B1-01`, `B1-02` (×2), `B1-03`, `B1-04`, `B1-05`, `B1-06`, `B1-07`;
  - `B2-01`, `B2-02` and `B2-03` (`.jpg`);
  - `B2-04`, `B2-05` and `B2-06`.
- **Scratch in `/tmp/claude-1000/w3b/`:**
  - the game copy, ini and saves (`ultima8.001` = `cp22-shield-halves.sav`;
    ScummVM wrote `ultima8.000` and `timestamps`);
  - the four session logs;
  - the driver `py/` and disassemblies `dis/`;
  - films `sp/b1film*` and `sp/b2film/`.
- **Not touched:** `:77`, `shared/`, `~/.config/scummvm`,
  `~/.local/share/scummvm`, `~/lv-checkpoints`, and any source, builder, map,
  fork, TODO or HANDOFF.
- Nothing was committed. ScummVM and Xvfb `:78` are stopped.
