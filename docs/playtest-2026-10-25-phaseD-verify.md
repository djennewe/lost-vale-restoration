# Playtest 2026-10-25: phase D in-engine verification (static 882-886 + actors 888-890/872)

This is the verifier pass on main `a6d513a`, the phase D integration.

**Build under test.**
- Artifacts: TYPEFLAG `7faaaf23`, U8SHAPES `f64cbfd8`, ANIM `97ae5fc9`, EUSECODE `2e3b71c2`, FIXED `995f4395`.
- Game directory: a pinned copy of `shared/u8-lv-patched` at `/tmp/claude-1000/phaseD/game`. It was sha256-identical to `ARTIFACTS.sha256` at the start, and `sha256sum -c` was all OK at the end: five artifacts, top-level FIXED, `u8monsters.ini` `7f666fe9`, and the binary.
- Binary: a copy of `scummvm-lv-console/scummvm`, `d371f7ce…`, built 2026-10-17. That postdates fork tip `e48f8716` (2026-10-11).
- Display: Xvfb :95.

**Harness.**
- Shots: `vignette_capture.py` and `session.sh` ran from a scratch copy whose `shared/u8-lv-patched` is a symlink to the pinned copy. There was no `shared/build` beside it, so `session.sh`'s sync step was a no-op. The run used a private `XDG_RUNTIME_DIR`, config and data dir.
- Play: the replay `lv.py` driver, repointed at the scratch dir (640×400, `usehighres`).
- No rebuild was run, nothing was committed, and the estate was not run (the brief bars builds; Main ran `integrate.sh`).

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| V1a | screen07 ≥ 89.9, screen12 ≥ 96.4, screen13 ≥ 94.0 | **PASS**: 89.93 / 96.37 / 93.99, identical to the static slice's own in-engine numbers (its "96.4"/"94.0" are those rounded) |
| V1b | screen02/09/19/20 above SCORES.md (91.26 / 82.65 / 94.46 / 90.83) | **FAIL as stated, with no map regression.** 02 = 91.26 (pixel-identical capture); 09 = 89.81 (+7.16, waterfall phase); 19 = 90.87-91.85 (−3.4, the ghost and Atli's loiter); 20 = 90.58-90.83 (≤ 0). The new actors are never at their shot positions in play, so they cannot lift an in-engine score (F3) |
| V1c | The other 12 shots: no drop > 1 point | **PASS for map content.** Two drops over 1: screen17 −1.41 and screen22 −2.56. In both, every differing pixel is GHOST 411 or the Avatar's pose. New table: `ingame/SCORES-2026-10-25.md` |
| V2 | Water Zombie 872: hatch, walk, attack and die in several directions; no missing or garbage frames; the club only at frame 81 | **PASS for rendering**, using invincibility (approved by Main). Three zombies were hatched by walk-ins on two triggers and killed. Deaths were drawn in two directions (die frames 219 and 181), and every frame drawn was whole. **Frame 81 was not seen in play** (NOT DEMONSTRATED). **Balance finding F2** |
| V3 | 888/889/890 in normal play on Map 10; Atli talks with gestures; doorway jamb | **PARTIAL.** Atli (888) loiters, walks, talks: the menu works and he gestures through the barks; exitConvo re-arms him. Child 104 (889) renders. **npc 111 has no record in the shipped FIXED.DAT, so 890 is never placed (F1, a merge regression).** In the doorway the east jamb hides his staff and the right edge of his robe (F4). Old saves keep 707/708 bodies until a map hop, and keep 111 as 708 for good (F5) |
| V4 | Map 17 walked: arrival from Map 13 → both halves → pad 208; strips end at 4095; no blocked path; no paint knots; halves pick up | **PASS.** One transient knot during a drag (F6). The arrival was walked in from Map 13, but the start point on Map 13 was a positioning teleport (harness note H3) |
| V5 | Log hygiene | **PASS.** Across 8 logs: 0 `stuck in process loop`, 0 Segmentation, 0 Assertion, 0 `Unhandled intrinsic`, 0 ERROR. **12 `Cycle in paint`**, all during one drag (F6). **2 `Non-existent process PID (0) in implies`**, in a fresh-new-game capture session (F7) |

## V1: in-engine shot scores

- Pass 1 ran all 19 shots, each in a fresh session.
- Passes 2 and 3 repeated 01/02/09/19/20/22/17/16. screen01's pass-1 session printed `could not turn cheats on`, and passes 2 and 3 gave 91.99 twice.
- The full table is `docs/research/2026-10-16-screenshot-reconstruction/ingame/SCORES-2026-10-25.md`.
- Captures: `V1-screenNN_ingame.png`.

**Negative control: is anything else on the map moving?** For every shot, the new raw capture was diffed against the 10-17 raw capture taken from the same teleport spot (`V1-*-old-vs-new.png`, magenta = differs; `V1-old-vs-new-montage.png`).
- Differing pixels, as a share of the window: 02 0.00%, 10 0.20%, 20 0.25%, 18 0.40%, 04 0.39%, 16 0.91%, 21 1.76%, 17 1.90%, 22 3.04%, 15 3.73%, 19 3.87%, 05 4.26%, 09 8.92%.
- Each magenta region is one of five transients: GHOST 411, the Avatar's pose, Atli (19), animated water/fire/lava, or a cursor.
- The only exceptions are the intended changes: 07/12/13 (the static slice's art) and 14 (a 1-pixel camera offset; its score moved −0.04).

## V2: Water Zombie 872 (PASS for rendering; balance finding F2)

**Setup.**
- Save: `~/lv-checkpoints/harpie1024-m13-south-axe-hp30.sav` (axe, hp 30).
- A positioning teleport to Map 10, which reloads the map from FIXED. Every hatch was then walked into.
- Debug flags `Object` and `Actor`.

**Without cheats.**
- **Wave 1:** I walked N from (13820,20800) onto the pier. Trigger 25499 logged `event 7 @ 0481`, and zombies 160 (hp 41) and 161 (hp 43) hatched.
  - Hits on the Avatar: `dmg 12`, `11`, `8` (two more were absorbed).
  - He was at hp 7 at the first read after the walk, and dead within about 10 s.
  - Plates: `V2-a`, `V2-b`.
- **Wave 2:** I teleported to (13824,19760,8) and walked N. Trigger 30719 fired, and zombie 160 (hp 49) hatched.
  - Hits on him: 11, 8, 8, 6. His axe landed 2 blows: `dmg 15 → Damage 8`, `18 → 9`.
  - He died about 10 s into the fight with the zombie on 32 hp (`V2-g`).

**With `Cheat::toggleInvincibility`** (approved by Main for these plates only; turned off afterwards, and the log shows `Avatar is no longer invincible.`):

| Zombie | Where | Frames read during the fight | Death |
|---|---|---|---|
| 160 (wave 2) | Pier, attacking from the W/NW | walk 43, 50, 52, 60; attack 404, 407 | die frame **219**, falling W (`V2-c` zoom strip) |
| 161 (wave 1) | Pier foot, attacking from the N/W | 54, 110, 120; attack 417, 419 | frame **219** |
| 162 (wave 1) | Shore, attacking from the S | 90-93, 388-394 | die frame **181**, falling SW (`V2-e`) |

- Every sprite drew whole: teal skin, dark-green kilt. There were no gaps, no garbage pixels and no missing frames, across about 4,000 grabbed frames.
- There were 0 water events: no `shape 347` line and no `I_resetRef item=1`.
- **Frame 81 (the 1994 club pose)** never appeared in a frame read, and no club was spotted in the films. The NW-attack direction was not exercised. The offline render (`V2-f`, frames 78-83 from the installed FLX) shows 81 as a back view holding a raised club, between club-less 80 and 82. So a player who meets a NW attack will see the club appear for one frame: `[INFERENCE]` from the art, not observed.

## V3: Map 10 NPCs (PARTIAL)

**Setup.**
- Save: `replay1017-s13h` (Map 10).
- I hopped to Map 13 and back by debug teleport, so the map reloaded from FIXED. The fork's LV loader logged `Slot 104 already has actor shape 708 … updating`.
- Cheats were off for every talk.

**Atli (npc 107, 888).**
- On load from the old save he was **707**. After the hop he was **888**, and `findShape 888` = 1.
- He loiters in and out of his hut. Plates: `V3-a` and the walk strip `V3-b` (SW walk, N back view, his return). Frames seen: 5, 11, 15-17, 30, 35, 39, 45-53, 246. Everything drew whole.
- **The talk:**
  - Look-click logged `Item 107 (class Actor, shape 888)`.
  - The double-click logged `event 1 @ 046B:0392`.
  - The menu offered "I have spoken with Ezrekal." / "bye". I picked from the screen: the reply bark, then "What cliffs? / Why does she send them to the cliffs? / bye", then "bye".
  - At the farewell: `event 15 @ 046B:0290` (enterFastArea), with no `Non-existent process` line. He walked on afterwards.
- **What a player sees in his own yard** (`V3-c`, `V3-d`): a rock wall south-west of the hut hides most of him during the talk. Only his staff, hand and hair show.
- **To see the gestures** I used `Actor::hold 107 128 128`, then `Actor::hold 107 -128 -128`, to put him on open ground beside the Avatar.
  - He walks up and turns to the Avatar, with one arms-out gesture (`V3-e`).
  - Back view while barking: `V3-f`. Front view: `V3-g`.
  - The pose changes during the barks are small hand and staff moves.
- **Doorway.** `Actor::hold 107 -68 -196` put him on his record (19231,6943). The hold killed his loiter, so he stayed there in frame 45.
  - The hut's east jamb paints over his right side: **the staff and the robe's right edge are hidden** (`V3-h`, zoom `V3-i`).
  - In unheld play I saw him pass the door several times. The Avatar's own sprite stood in the doorway's line in the first film, so the N/NE frames at the door were not isolated.

**Child 104 (889)** at (5376,7424).
- Drawn as the small dark-haired spear child (`V3-j`, `V3-k`).
- It stood still for 48 s and did not answer a double-click. Retail CHILD 708 npc 111 in the same save behaved identically (static, no response), so this is not a regression of 889.

**npc 111 (890): not placed.** See F1. In the old save, slot 111 survives as **708** at (19712,6656) (`V3-l`), and `findShape 890` = 0.

## V4: Map 17 route (PASS)

**Getting there.**
- From `replay1017-s13c`, the run to trigger 209 crosses the summit harpie strip (trigger 20244 at (4863,1663), range x ±32, y ±192). No route avoids it (an `ExactReach` route with that strip forbidden returns none).
- Twice the harpies hatched and pinned or killed the Avatar (`V4-h`).
- I then placed him with a positioning teleport at Map 13 (4479,1791,120), west of the strip, and walked S into trigger 209. The log shows `Unloading map 13` → `Loading Fixed items in map 17`, and EggReapply `event 7 @ 05B2` fired. He arrived at (4608,10216,0) (`V4-a`).

**Fresh Map 17 items.**
- 878: 2, f0 q81 at (4259,7199) and f1 q82 at (3559,3311), both n 236.
- 883: 2, at (4095,3103) and (4095,3583). 882: 3. 884: 6. 885: 1.
- 877: 58, matching the offline count from the pinned FIXED. Both strip rows end at x 3967.

**The halves.**
- **Obelisk half:** look-click logged `Item 31794 (shape 878) q 81`, then `Dragging` → `Dropped item in backpack`, and weight went 60 → 90 (`V4-b`, `V4-c`).
- **Nook half** (`V4-d`, `V4-e`): the first drag from about 190 units bounced. That is the documented reach limit, and the item stayed at (3559,3311). From (3636,3208,8) the drag went through: `Item 30090 q 82` → `Dropped item in backpack`, weight 90 → 120 (`V4-f`).
- `findShape 878` then showed both halves `(255,255) f 0xc` (in the pack).

**The walk.**
- Pad 209 → the plaza → N up the processional street → over strip B at (3792,3484,8) → the nook. Back: E, S, then down the east side to the pier.
- No leg was blocked; the follower needed only short unsticks inside the nook.
- A walk N at (4608,11076) fired trigger 208 → Map 13 pad 208 (5119,1999,120), with hp 30 throughout (`V4-g`).

**Paint knots.**
- The Object channel was on: 2,393 `calling usecode` lines confirm it in the Map 17 window.
- There were **12** `Cycle in paint` lines (F6).
- **Control not available:** there was no older-build knot spot on this route.

## V5: log hygiene

| Log | Session | Cycle in paint | stuck | Segm. | Assert | Non-existent process | Unhandled intrinsic | ERROR |
|---|---|---|---|---|---|---|---|---|
| lv_A | Atli, children | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lv_Z / Z2 | Zombie fights without cheats | 0 / 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lv_Z3 | Zombie fights, invincible | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lv_M / M2 | Map 13 attempts | 0 / 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lv_M3 | Map 17 route | **12** | 0 | 0 | 0 | 0 | 0 | 0 |
| run/lv_run.log | Last capture session (screen16, pass 3, a new game) | 0 | 0 | 0 | 0 | **2** | 0 | 0 |

- The Object channel was on in lv_A, Z*, M* and M3 (`Enabled debug flag 'Object'` after every start or load).
- The 18 earlier capture-session logs were overwritten by `session.sh` and are not counted.

## Findings

**F1. npc 111 (the Elder's child, 890) has no start record in the shipped FIXED.DAT. This is a merge regression.** Severity: medium; an NPC is missing from new games.

- **Evidence:**
  - Offline, Map 10 of the pinned FIXED `995f4395` holds no item with npcnum 111 and no shape 890.
  - The actor slice's own FIXED `469787ab` holds `(890, 19712, 6656, npcnum 111)`. The two Map 10 item sets differ by exactly that one record (20,558 vs 20,559).
  - Rebuilding the Map 10 list in memory reproduces it: `build_map_10()` on main returns no 111; at `e5ca077` it does.
  - The record is dropped by `stamp_vignette(..., 'screen19')`.
- **Cause:** the actor merge `aec8c3e` resolved its `map_pins.json` conflict with the static side.
  - The 111 pin is `(708, …)` at `bee65bf`/`aec8c3e`, `(890, …)` at `e5ca077`, and absent at `a6d513a`.
  - So `stamp_shots` did not hold the 890-shaped record, and screen19's window cleared it.
  - Then `derive_map_pins` regenerated `map_pins.json` without it, so `test_map_pins_fresh` passes.
- **In-engine:** after a map hop, 104 → 889 and 107 → 888, but 111 stays whatever the save holds. In a new game, the fork's loader (`map.cpp:265`) has no record to create slot 111 from `[INFERENCE: new-game objectInfo 111 not run]`.
- **Fix direction:** restore the 890 pin, or hold npcnum records out of `stamp`.

**F2. Balance: the Water Zombie beats an armed 30-hp Avatar.**
- **Single zombie (wave 2):** 2 of 2 attempts killed him in about 10 s.
  - Its hits in the Z2 log: 11, 8, 8, 6, plus one absorbed.
  - His axe landed 2 of about 8 swings, for 8 and 9 damage after armour (ac 15, hp 41-49).
- **Wave 1 (two zombies):** killed him in about 8-10 s. Hits: 12, 11, 8, plus two absorbed.
- Its stats are `u8monsters.ini [waterzombie]`: dmg 6-12, dex 14-16, armour 15. This is a question for Douglas, as with the 10-17 harpies.

**F3. The phase-D actors cannot raise in-engine shot scores.** The zombies exist only after a hatch, and the NPCs walk their schedules. screen19's in-engine score varies 0.98 points with where Atli happens to be. The actor slice's numbers are built-window numbers only.

**F4. Doorway jamb.** Atli held on his record in frame 45 has his staff and the right edge of his robe hidden by the east jamb (`V3-i`). The slice measured SE frame 60 at 7%. Frame 45 is visibly worse.

**F5. Old saves.**
- NPC bodies come from the save: a save made before phase D shows 707/708 until the first map change, when the fork's loader `setShape`s 104/107 from FIXED.
- Slot 111 stays 708 permanently (F1).

**F6. Paint knot while dragging the eye half.**
- Lines: 6 × `874 -> 878 -> … -> 874` and 6 × `720 -> 878 -> … -> 720`.
- They are logged only between `Dragging item 30090` and its drop, as the half lifts off the nook's cloud floor (874) and straw (720).
- There were 0 knots while it lay there and 0 during the walk. A transient.

**F7.** 2 × `Non-existent process PID (0) in implies` in a fresh new-game capture session (log lines 79/84, start-up). Not traced.

**F8.** Atli's yard is boxed by rock walls to its south-west, so a player talking to him there sees mostly the rock (`V3-c`).

## Harness anomalies

- **H1.** `vignette_capture.py` has no game-dir argument and `session.sh` hard-codes `$REPO/shared/u8-lv-patched`. A scratch repo shell, with that path symlinked, was the way to pin it.
- **H2.** The pass-1 screen01 session could not turn cheats on (`cheats_on` toggled 4 times with no `true`). A retry worked.
- **H3.** Map 13 summit → 209 cannot avoid the summit harpie strip. Two runs ended in death or a pin, so the arrival used a positioning teleport west of the strip followed by a walk into 209.
- **H4.** NPC strikes need the click at the sprite's feet (projection −6 px), not −30 px; earlier clicks landed on roofs and crops behind. `lv.q` attaches failed occasionally (`ATTACH FAILED` ×4) and recovered.
- **H5.** After the Avatar died, the leftover blind clicks started the credits (the documented trap). Recovery was a restart.

## Console commands used (every session)

- Reads: `ObjectManager::objectInfo` (1, 104, 107, 111, 30090), `ObjectManager::findShape` (73, 500, 872, 873, 877, 878, 882-885, 888-890), `AskGump::ask` (list only).
- Flags: `debugflag_enable Object`, `debugflag_enable Actor`.
- `Cheat::toggle`: always on and off around teleports, each verified by its echoed state.
- `MainActor::teleport`, for setup only:
  - 13 (4096,11776,0);
  - 10 (19300,7300), (19231,7071), (19800,7800), (5500,7650), (19800,6800);
  - 10 (13820,20800,0) ×2 and (13824,19760,8) ×2;
  - 13 (4479,1791,120);
  - plus the per-shot teleports inside `vignette_capture`.
- `Actor::hold 107` with offsets (−68,−196), (−160,0), (128,128) and (−128,−128), for the plates and the talk positioning.
- `Cheat::toggleInvincibility`: on and off once, for the V2 plates only (approved).
- Not used: heal, item cheats, `Item::grab`, `setGlobal`, `loadGame` (reloads were restarts with `--save-slot`), `saveGame`.

## Disk changes

- **Wrote:**
  - this report;
  - `docs/playtest-2026-10-25-phaseD-verify/` (52 plates);
  - `docs/research/2026-10-16-screenshot-reconstruction/ingame/SCORES-2026-10-25.md`.
- **Scratch only, in `/tmp/claude-1000/phaseD/`:**
  - the game, binary and engine-data copies, with their start hashes;
  - the repo shell, the `py/` drivers and `saves/`, where slot 1 was overwritten by copies of checkpoints;
  - the `lv_*.log` files, `ingame*/`, `diffs/`, `sp/` films and an `src_e5ca077/` export for the F1 diagnosis.
- **Not changed:** `~/lv-checkpoints`, `shared/`, source, TODO and HANDOFF.
- My ScummVM and Xvfb :95 are stopped.
