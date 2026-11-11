# Playtest — the three Zealan gods in the Inner Sanctum (2026-09-13)

First in-engine look at shape 860, and the first time any map builder has
placed a custom-art shape at all.

## Verdicts

| ID | Test | Verdict |
|---|---|---|
| A1 | Timyra (frame 2) draws in the world | **PASS** |
| A2 | Doloras (frame 1) draws in the world | **PASS** |
| A3 | Felicitar (frame 0) draws in the world | **PASS** |
| B1 | All three placed at the ceremony triangle, right frames | **PASS** |
| B2 | All six frames decode from the installed `U8SHAPES.FLX` | **PASS** |
| C1 | Depth sort against neighbouring walls and floor | **PARTIAL** |
| C2 | The gods obstruct, and obstruct nothing on the route | **PASS** |
| E1 | The gods stand in the box art's left-to-right order | **PASS** |
| E2 | The encased blocks read as solids, not flat cards | **PASS** (v2 art) |
| G1 | The ceremony frees them: frames 0/1/2 → 3/4/5 | **PASS** |
| G2 | The freed state survives leaving and re-entering the map | **PASS** |
| G3 | The freed sprites are clean over a lit floor | **PASS** (after a fix) |

## A1/A2/A3 — the crystals draw — PASS

All three read the way the box art does: a dark silhouette suspended inside a
glowing amber mass, surviving quantization to `U8PAL.PAL` and the drop to
game scale.

- `A3-felicitar-in-world.png` — frame 0 at (3072, 6656), the 46x120 slab with
  the standing figure, arms raised. Avatar at (2752, 6336).
- `A1-timyra-in-world.png` — frame 2 at (3840, 7680), 60x124. Avatar at
  (3560, 7150).
- `A2-doloras-in-world.png` — frame 1 at (2304, 7680), the 92x81 block, the
  widest of the three and the one the clearance check was about.

`D1`/`D2`/`D3` are a matched set shot after the **box-art re-staging**
(below), framed identically for the artifact *The Gods From the Cover*.
Avatar positions: (1984, 7360), (3520, 7360), (2752, 6336) — derived by
inverting the `px` arithmetic in the traps file.

## E1 — the gods stand in the cover's order — PASS

The cover reads Timyra, Felicitar, Doloras left to right. The sanctum did not:
it read Doloras, Timyra, Felicitar. Which god stands where is decided by
screen x, which in U8's projection is `(wx - wy) / 4`, and that ranks the
ceremony triangle's three points:

| screen x | point | now holds |
|---|---|---|
| −1344 | south-west (2304, 7680) | Timyra — frame 2, quality 303 |
| −960 | south-east (3840, 7680) | Felicitar — frame 0, quality 301 |
| −896 | north (3072, 6656) | Doloras — frame 1, quality 302 |

The triangle did not move; only which frame stands on which point, quality
carried along with it. Confirmed in-engine: `findShape 860` returns those
three pairings, and with the Avatar at (2752, 6336) their camera offsets come
back at −448, −64 and 0 — the cover's order.

**No single frame holds all three.** They span 896 screen pixels on a
640-pixel surface, which is why `D1`/`D2`/`D3` are three plates rather than
one. Only `FIXED.DAT` moved in the rehash, and the estate stayed 27/27 —
`test_sanctum_clearance.py` asserts the crack-doorway clearance by *position*,
so it holds whichever god stands at the north point.

**A line that landed for free.** Walking in fired `TEMPLENT.UNK`'s entry egg:
*"Three shapes stand in the dark ahead of me, and something about them is
wrong — they do not move at all."* Written against the placeholder statues,
and much better aimed at three figures frozen in amber.

Each is anchored bottom-centre on the floor with no clipping into it and no
seam against the wall stubs beside it.

**A retracted claim.** The first version of this report said Felicitar "reads
as a torch flame" and recommended a palette change. That was wrong: the
screenshot behind it showed a `SHAPE_TORCH` (295), not the god, and it was
identified by eye rather than by `findShape`. Felicitar carries the same
clearly visible dark figure the other two do. The nearest torch to any god is
512 units away — the sanctum's north row sits at y = 6400, the gods at 6656
and 7680 — so they do not overlap on screen either.

## B1 — placement — PASS

```
] ObjectManager::findShape 860
Item 5229 (class Item, shape 860), 0, (3072, 6656, 0) q: 301, ... shapeinfo f: 3
Item 5230 (class Item, shape 860), 1, (2304, 7680, 0) q: 302, ... shapeinfo f: 3
Item 5231 (class Item, shape 860), 2, (3840, 7680, 0) q: 303, ... shapeinfo f: 3
findShape 860: 3 found
```

Three items, the three triangle points, frames 0/1/2, qualities 301/302/303,
`shapeinfo f: 3` = `SI_FIXED|SI_SOLID` from donor 443. `px` in that listing is
the offset from the Avatar, who is the camera centre — useful for locating a
sprite you cannot identify by eye.

## B2 — the shipped bytes — PASS

`B2-shape-860-from-installed-flx.png` is shape 860 rendered straight out of
`shared/u8-lv-patched/STATIC/U8SHAPES.FLX` by `png2shape.render_preview`:
six frames, 46x120 / 92x81 / 60x124 encased and 24x110 / 53x72 / 43x110
freed, every anchor bottom-centre. This is the decode path the engine uses,
run against the installed artifact rather than a scratch FLX.

## C1 — depth sort — PARTIAL

Nothing wrong is visible in A1 or A2, but neither shot puts a god *behind*
something the Avatar can walk in front of, which is where U8's sort actually
gets tested. The gods stand clear of the walls by design, so the case may
simply not arise. Not demonstrated either way.

## C2 — the gods obstruct, and obstruct nothing that matters — PASS

The walk test the first version of this report said was missing. Avatar as
shape 1 (64-unit body — the player arrives shrunk to 32, so this is the
stricter case), teleported to the DD-005 crack landing (2804, 6664) and then
driven with the right mouse button, position read from
`ObjectManager::objectInfo 1` after every step.

| Leg | Result |
|---|---|
| landing → god1's south face | ARRIVED (2908, 6768) |
| → triangle centre | STALLED (3000, 7132) |
| → god2's east face | ARRIVED (2368, 7644) |
| → god3's west face | ARRIVED (3640, 7556) |
| → altar approach | STALLED (3072, 7644) |

**The two stalls are not the gods.** Both sit a few units north of a solid
shape-15 wall stub, at y 7148 and y 7660. Those come out of the temple-floor
glob (`GLOB_TEMPLE_FLOOR`, quality 80), which carries wall stubs in **bands
across the sanctum every 512 units of y, pierced by a doorway every 512 units
of x**. The Inner Sanctum is a grid of low walls, not an open hall — those
are the grey stubs visible in every screenshot above. The driver walked
straight into a band between two doorways; a player would walk around.

`agents/map-populator/src/test_sanctum_clearance.py` (new, 21 checks) settles
the rest offline against the built `FIXED.DAT` with globs expanded, using
`Box::overlaps` verbatim:

- **The gods obstruct.** Shape 860 is `SI_SOLID` with the authored 6x6x8
  footpad, all three are solid boxes in the shipped FIXED.DAT at the triangle
  points, and a 64-unit body standing on one is refused. This is the only
  positive check that the TYPEFLAG patch took — every other result here also
  passes with an unpatched entry.
- **The route survives.** The shrunken Avatar has a way through each of the
  four band edges the crack-to-altar route crosses — y 6655, 7167, 7679, 8191
  — each with margin rather than an exact fit. Every band shows the same
  eight doorways; the one the player uses is x 2784..2876, directly below the
  crack at x 2817..2879.
- **God1 clears that doorway by five units.** It stands at (3072, 6656), on
  the y=6655 band, with its box running x 2881..3072 against a doorway ending
  at 2876. That has its own named check, because a later nudge west would
  seal the way into the temple and the set comparison below would only report
  "a doorway is gone".
- **Enlarging the gods closed nothing.** The doorway set at every band is
  identical between the 192-unit footpad and the donor's original 96, at both
  body sizes. The footpad change is not a regression risk.

Probe on the band edge, not near it: the first version of the test probed
6700/7200/7700/8220 and two of those were vacuous. Boxes are half-open, so a
stub row ending at 7167 misses a 32-tall body at 7200 by one unit, and the
probe reported the whole sanctum open. Corrected before the test was trusted.

**One placement smell, pre-existing.** Doloras (2304, 7680) and Timyra
(3840, 7680) stand centred in two of the y=7680 band's eight doorways,
leaving those two impassable to a full-size body and 24 units wide for a
shrunken one. That was equally true at the old 96-unit footpad, and neither
doorway is on the player's route. A god standing in a doorway is still odd
staging if anyone wants to move them.

## Not covered

- **The freed frames (3/4/5) have never been drawn in the engine.** Nothing
  calls `setFrame(n+3)`; `AOSCENE.UNK` still narrates the freeing.
- **A real player's approach.** Every position here was reached by
  `MainActor::teleport` at full size. C2 covers the geometry, but nobody has
  walked in through the crack shrunken and crossed the sanctum as the game
  asks. `test_route_reach.py` remains FIXED.DAT-only and still cannot see a
  footpad; `test_sanctum_clearance.py` is what covers this map now.


## G1 — the ceremony breaks the amber — PASS

Shape 860 carried both states as frames from the day it was injected and
nothing swapped them; `AOSCENE.UNK` narrated the freeing in four barks and
touched no god item. It does now: `TypeZealanGod` is pinned to 860, and the
hatch runs

```
foreach god where type = TypeZealanGod within 2000 of referent
{
    if god.getFrame() < 3 { god.setFrame(god.getFrame() + 3); }
}
```

under `FadeToWhite()`, so the player never sees the frame change — only what
is standing there when the white lifts. Range 2000 because the egg sits at
(3072, 8320) and the far god is 1664 units north; only three items on the map
carry the type, so it can match nothing else.

Run from `run-s16-tinytar.sav` with `godsFree` cleared to 0. On arrival
`findShape 860` read frames **0, 2, 1**. Walking into the altar egg's ±192
box ran the scene — the Avatar stops dead mid-step, which is
`setAvatarInStasis(true)`, not a stall — and afterwards `godsFree = 1` and
`findShape 860` read frames **3, 5, 4**. `F1`/`F2`/`F3` are the three freed
gods photographed in the sanctum, same framing and order as the encased set.

## G2 — the freed state survives a map reload — PASS

It did not, at first. Map 18's fixed items are re-read from `FIXED.DAT` on
every map switch, so a round trip to map 17 and back put the frames at
**[0, 1, 2]** — the gods re-sealed themselves, and whether they were free
would have depended on which map the player saved on.

`EggTempleEntry` is the only thing that fires on entering the sanctum, so it
carries the repair behind `if godsFree`, at range 2200 because it sits at the
crack rather than the altar. Verified: back on map 18 the gods read
[0, 1, 2], and crossing the entry egg made them [3, 4, 5] again. Both sites
guard on `getFrame() < 3`, so running either twice is free.

## G3 — a magenta fringe, found only because the gods could finally be freed — PASS after a fix

The freed sprites shipped with a one-pixel purple outline around the whole
silhouette (`F4-magenta-fringe.png`). It is key bleed: what survived
`--key-tolerance 130` on the 1024 px source got averaged into a solid ring by
the ~9x Lanczos downscale, then quantized to the nearest palette entry to
magenta. It is invisible on `png2shape`'s dark preview plate and unmistakable
over the lit temple floor, which is why it shipped — and it could not be seen
at all until something actually drew frames 3/4/5.

Raising the tolerance cannot fix it: at a distance that catches the blend it
also catches the figure. `png2shape --key-despill` discriminates by **hue**
instead — a pixel is bleed when every channel the key is bright in exceeds
every channel it is dark in, which for magenta means `r > g + m and
b > g + m`, something bronze skin never satisfies because its blue is its
lowest channel.

Two thresholds, and the second was needed: above `2m` the reading is
unambiguous and the pixel goes wherever it sits, which is what clears an
**interior seam** like the one-pixel gap between Felicitar's legs — that gap
fills solid at game scale, so it has no transparent neighbour to erode from
and the edge rule alone left a purple column down the middle of her. Between
`m` and `2m` the pixel must touch transparency. Flagging both sets on the
game-scale sprite showed every marked pixel on the silhouette or in a seam,
none inside the body.

Margin 16 on the three freed frames: Timyra 43x110 → 42x109 and three palette
entries gone, all purple. `F5-fringe-fixed.png` is the same close-up as `F4`.
The encased three key on black, show no bleed, and stay at despill 0.


## E2 — the amber reads as a solid — PASS after a re-generation

The v1 blocks read flat in the engine. The cause was **camera angle, not
width**: U8's camera is high, so every solid in the sanctum shows a wide 2:1
diamond on top — the temple-floor glob's own wall stubs do — and v1 was
generated from a much lower angle, all front face and a sliver of top. Doloras
never drew the complaint, and she was the one whose block had a real top plane.

Re-generated with the projection pinned in the prompt rather than described:
*seen from above at the steep angle of a 2:1 isometric floor tile*, *a top face
twice as wide as it is tall*, *left facet mid-value, right facet clearly
darker*, and *the block's near vertical edge crosses in front of part of the
silhouette* — the cue that separates "suspended in" from "painted on". Three
directions were compared on real temple floor at game scale (crate, faceted
boulder, tall prism); Douglas picked the prism as closest to the cover.

`D1`/`D2`/`D3` are the result in-engine. Felicitar 36×124, Doloras 96×71,
Timyra 54×124; the 192-unit footpad is unchanged and
`test_sanctum_clearance.py` still passes, so nothing about the route moved.

**A trap worth the line.** Key tolerance had to drop 95 → 40 with the new art.
v1 was bright everywhere so a generous black key cost nothing; these have a
genuinely dark shadowed facet and a dark silhouette, and at 95 the key ate
both — the blocks came out **hollow**, with the floor visible straight through
them and the figures reduced to wireframe. It presents as a rendering bug and
is a key setting.
