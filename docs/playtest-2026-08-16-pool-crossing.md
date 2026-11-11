# Playtest 2026-08-16 — the map 8 pool chamber is CROSSED

Rehearsal tick (exit test, steps 1-18 continuous). Picked up the session
parked 2026-08-12 at the "west-bank save". Ended with the Avatar standing
on the southern landmass at (29801,22801,8), the entire stepping-stone
chamber behind him, with the route, the physics, and the tooling to make
the crossing repeatable. ~24 deaths en route, all recovered via the slot-1
reload protocol; artifacts untouched, still canonical.

## Verdicts

| Test | Verdict |
|---|---|
| Cross the STANSTON pool (A→C→G→H→I→J) | **PASS** — every hop lands, deterministic with `calibrated_pixel` |
| Exit the pool south (J→shore direct) | **FAIL — impossible by design math** (needs plane 543+, str-15 range cap 470); detour J→D→E→west-strip **PASS** |
| Reach the southern landmass on foot | **PASS** — walked (29737,22377)→(29801,22801), plain ground |
| 2026-08-12 route theory ("west bank, follow south, climb") | **REFUTED** — pocket 1 is a sealed decoy; no climb exits exist (F1, F12) |
| East-shore walking route around the pool | **REFUTED** — the "shore" was the water surface (model artifact F9) |

Route as proven in-engine: north cave bank → (short hops, 2026-08-12) →
chest pocket → **A(29983,21311) → C(30207,21535) → G(30591,21535) →
H(30815,21759) → I(30815,22143) → J(30591,22367) → D(30335,22111) →
E(30111,22367) → west strip (29737,22377)** → walk south → landmass
(29801,22801). Screenshots J1-J6; full-chamber render M1 (from
`GameMapGump::dumpMap`).

## The jump physics (the day's core yield)

Everything below was verified in-engine against the ScummVM source.

1. **SPACE is the targeted jump.** `ACTION_JUMP` ("fake both-button-click",
   metaengine.cpp:71) sets MOVE_JUMP with no mouse buttons. A real
   both-button chord raises MOVE_MOUSE_DIRECTION a tick later, which routes
   to the fixed-distance branch (u8_avatar_mover_process.cpp:468) — that
   was the mechanism of most 2026-08-12 deaths. Only the direction-less
   branch (:510) calls the targeted jump. First tap may be consumed by
   turn-to-face; tap again.
2. **The jump lands at the geometric plane point of the CLICK PIXEL** —
   `TraceCoordinates` Z_FACE equations (game_map_gump.cpp), NOT at the
   clicked artwork. Stone sprites are drawn taller than their 8-unit
   geometric top, so clicking high on the artwork extrapolates the plane
   BEHIND the stone (the deterministic "north pocket" mis-jump).
   `hop.plane_point()` reproduces the equations (camera = avatar origin,
   z+20; screen = 2× native 320×240).
3. **Deliveries fall short at range.** Exact ≤ ~190 units; beyond that the
   measured deficit was 30-170, growing with distance. Compensation =
   "deep aim": pick the artwork pixel whose plane point is ~dist+110
   ALONG the flight line (`hop.calibrated_pixel`), with perpendicular
   error penalized 1.6× (an off-axis plane point = water beside the
   stone; that killed G→H twice before the perp term).
4. **Hard range cap: str × 32 per axis** from the avatar centre
   (u8_avatar_mover_process.cpp jump()); this save has str 15 → 480.
   Over-cap aims get a silent shakeHead. This makes J→shore (543+) and
   J→E (556+) **impossible**, forcing the J→D→E detour. Raising str
   would widen the cap (climbing trains str — no climbable LAND tops
   exist in this chamber, F12).
5. **mouselength==0 dead zone**: cursor inside the walk-threshold box near
   the feet (thresholds 50/255, mouse.cpp) degrades SPACE to a vertical
   jumpUp. Keep the aim pixel far enough.
6. **Careful step (LCTRL) works on stones** (+32 per step until support
   runs out); ordinary walking on a stone is refused.

## Numbered findings

- **F1 — the 2026-08-12 conclusions were wrong twice.** (a) The chest
  pocket ("west bank") is a sealed decoy: walk south is walled by two
  retail shape-497 walls (128×32×48, SOLID, no LAND) spanning the full
  lane; exact-reach shows zero climb exits ≤72z from the pocket. (b) The
  file `cp3c-west-bank.sav` is MISLABELED — it contains the NORTH cave
  bank (30239,20431), not the west bank. The true west-bank state
  existed only in quicksave slot 1 (since overwritten; the route no
  longer needs it).
- **F2 — the blue arrows are jump-route guides** (shape 2, non-solid,
  FIXED only), one per hop decision point, pointing at the next stone or
  descent. The 2026-08-12 "teleport-pad markers" reading was wrong.
- **F3 — STANSTON stones (shape 780) are LAND, safe footing in both
  frames** (frame 0 "sunken" included). Usecode: release() grants
  +15 AccumulateDexterity when the stone empties — the pool doubles as a
  dex trainer. 100% retail geometry (diffed against retail FIXED.DAT).
- **F4 — deadly water does NOT block walking.** Walkers stroll straight
  in and drown; that (plus the fixed-jump chord) explains most historical
  deaths here. Every blind-walk fallback in the harness was removed;
  probes must verify aim pixels before any pathfinder/jump click.
- **F5 — middle-click = engine PathfinderProcess** (game_map_gump.cpp
  BUTTON_MIDDLE). Excellent short-range driver (threaded the mushroom
  chokepoint), but it walks into water if given a water target and
  refuses targets in unloaded darkness. Probe first, ≤250-unit clicks.
- **F6 — exact_reach models the engine's `z<=0 is always supported` rule
  faithfully, which makes the entire water surface read "standable".**
  The phantom "east shore corridor" this produced cost several deaths.
  For land-truth queries, use its `lands` list (non-SEA LAND items) —
  the SEA-flagged CLRWATER (0x87) is SOLID and satisfies `supports`.
- **F7 — climb requires a LAND-flagged top.** The 497 walls, shape 65/66
  pillars (SOLID-only) refuse tryAnim climbs; they are pure obstacles.
- **F8 — `Ultima8Engine::saveGame <arg>` always writes SLOT 1** (arg is a
  name, not a slot) and `loadGame` always loads slot 1. The checkpoint
  protocol is: `cp <checkpoint>.sav saves/ultima8.001` then loadGame.
- **F9 — `GameMapGump::dumpMap` renders the full current map to
  map_008.png** (globs included — the ground-truth chamber map, M1), but
  it makes a "Pre dumpMap save" in the autosave slot and a modal autosave
  dialog then blocks ALL input including the debugger (H1); click Move.

## Harness anomalies (fixed in tools/playtest-linux/)

- `nav.pos()` rewritten attach-aware (byte-offset watch + verified chord);
  the old tail-count version false-positived "death" on slow attaches.
- `nav.chord()` now verifies attach via "Debugger entered" count.
- `nav.resume()` now verifies detach: blind `exit` writes desynced
  attach-parity and left the game silently PAUSED through entire input
  sequences (walks/jumps doing nothing).
- `hop.py`: new `plane_point` / `calibrated_pixel` (the working aimer),
  probe-verified pixel checks, no blind fallback walking.
- Arrow-key turning taps are unreliable (lost between frames); facing via
  cursor + tap. Keyboard careful-steps (ctrl+Up) are reliable.

## Disk changes

- Saves: slot 1 now "strip-south-22801" (= cp3h). Slot 2: pre-dumpMap
  save (expendable). Slot 3: 2026-08-12 autosave. New checkpoint files in
  ~/lv-checkpoints/: cp3d-stone-c, cp3e-ne-ledge, cp3f-stone-g,
  cp3g-stone-j, **cp3h-west-strip (the forward checkpoint, on the south
  landmass at (29801,22801,8))**.
- `~/projects/lost-vale/map_008.png` — full map render
  (13MB, gitignored artifact of dumpMap; keep or delete freely).
- Session live on :77, console build, debugflag Object enabled.

## Next

From cp3h (29801,22801): continue south/southwest across the landmass to
the fence/gate + bones platform seen in M1's lower-left (the electric
gateway + lever puzzle per the walkthrough), then the south exit and the
dirt road to Mythran — quest steps 1-2 of the continuous run.
