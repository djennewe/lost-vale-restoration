# Playtest — the cloud floor, shape 862, on Map 17's islands (2026-09-15)

First in-engine look at the art track's second item (`docs/art-track.md`,
contract 2): the three cloud islands beyond the Arrival Plaza's wall in
the cloud tile instead of the flagstone platform kit. Fresh world, the
canonical build (`FIXED.DAT 5ba14957…`, `U8SHAPES.FLX aba2d6c4…`,
`TYPEFLAG.DAT ab2e914a…`, `EUSECODE.FLX` unchanged at `a71868ae…`), the
640×400 canvas, plates cropped at `+565+336`.

## Verdicts

| ID | Test | Verdict |
|---|---|---|
| B1 | `findShape 862` returns the 78 tiles at the builder's positions | **PASS** |
| C1 | Tessellation: no seam between tiles at one z, on the lattice the items are placed on | **PASS** (tool plate and in-engine) |
| F1 | Island 3 (5×5, 3×3, 1×1 tiers) draws, the Avatar stands on its top at z=24 | **PASS** |
| F2 | Island 1 (5×5, 3×3) draws | **PASS** |
| F3 | Island 2 draws with its rock spire sorted on it | **PASS** |
| F4 | From the plaza's south-west corner an island shows beyond the wall | **PASS** |
| G1 | Tiers read as steps | **NOT the look, by contract** — see below |
| V | The void floor: black beyond the walls without `usehighres` (2026-09-16) | **PASS** |

## B1 — the engine's own count — PASS

```
] ObjectManager::findShape 862
Item 8313 (class Item, shape 862), 0, (2047, 12159, 0) q: 0 … shapeinfo f: b …
…
findShape 862: 78 found
```

78 items, every one at a floor-grid corner (x, y ≡ 127 mod 128) south of
y 11776, z 0/8/16; `shapeinfo f: b` = SI_FIXED|SI_SOLID|SI_LAND, the
flagstone kit's flags. The Avatar teleported to (5087, 13023, 24) stood
there — the top tile's surface — and `objectInfo 1` reported that
position after a walk step.

## C1 — seams — PASS

`C1-tessellation-plate.png` is the finished tile laid 5×5 on the 128-unit
lattice by the tool, at 1x and 3x beside the 1994 floor at 1x: no seam.
In-engine (`F5-island-1-tiles-2x.png`, island 1's top tier at 2x) the
texture runs across the nine tiles without a break. The mapping
`(u, v) = (x + 2y, x − 2y) mod 64` is periodic under both lattice
generators, and the frame carries shape 113 frame 0's exact size, anchor
and mask (`test_art_props.py` asserts the mask pixel for pixel), so the
cloud fills precisely the pixels the flagstone did.

## F1–F4 — the islands — PASS

- `F1-island-3-all-tiers.png` — the Avatar on island 3's top tile; island
  2's corner and a spire top-left, a boulder of the void's edge below.
- `F2-island-1-top-tier.png` — island 1, the Avatar on the 3×3 tier, a
  corner of the 5×5 ring showing at the left.
- `F3-island-2-with-spire.png` — island 2 with its rock spire drawn on the
  cloud, islands 1 and 3 at the corners.
- `F4-arrival-plaza-south-west-corner.png` — Avatar at (4600, 11700, 0)
  inside the plaza: the south and west walls, the void black beyond them,
  and island 3's corner visible past the wall at the bottom left. That is
  the "seen, never reached" the map intends.

At 1x the floor reads as the 1994 one does: near-white with a fine
pale-blue scallop. The tone shares are the screenshot's (8/35/57).

## G1 — tiers do not read as steps — the contract's look

A cloud tier has no face frame, so a higher tier overdraws the one under
it with the same texture shifted 8 px up, and an island reads as one flat
diamond with notched edges (the donor's lip rows). Contract 2 says so
("at an island's outermost tier the edge is a thin diamond over the void,
by this contract"). If Douglas wants the tiers to read, that is frames
1–3 — a soft cloud underside for the south, east and corner roles — and a
second pass; not the flagstone faces.

## V — the void floor, verified without `usehighres` (2026-09-16) — PASS

Douglas chose the map-side fix for finding 1. `lv_furnish.void_floor`
lays a pure-black 256-unit plate (shape 564 frame 2, the plate Map 8
flanks its paving with; `SI_DRAW`, so it sorts under every real floor)
under every 128-cell that is void and within the canvas's view of a real
floor cell — 999 plates on Map 17, 2,504 items in the builder's list. Only
`FIXED.DAT` moved (`d4e7430a…`), reproduced by a second build; the estate
is 30/30 and `test_map_hygiene.py` gained a `void_in_view` class: Map 17
is 0, the other five maps are pinned at their 2026-09-16 counts (9: 1,404;
10: 10,599; 11: 9,941; 13: 3,004; 18: 2,206) until each lays its floor.

Plates taken with `usehighres=false` — the player's default, the
configuration finding 1 was about — after a walk step at each spot:

- `V1-void-floor-plaza-sw-corner-no-highres.png` — Avatar at
  (4600, 11700, 0): the void beyond the south and west walls is black,
  island 3's corner shows past the wall. (The Avatar himself stands
  behind the south wall from this camera and is hidden by it.)
- `V2-void-floor-plaza-south-edge-no-highres.png` — (5376, 11700, 0),
  the same: black.
- `V3-void-floor-island-2-no-highres.png` — on island 2 after a step,
  (3827, 12659, 0): the islands on black, nothing of any earlier frame.

`usehighres` was set back to `true` in the harness's `scummvm.ini`
afterwards, for the other five maps' plates until they have floors.

## Findings that were not part of the plan

1. **The void is never cleared, and it is player-visible** — fixed on Map 17 by section V and on the other five maps on 2026-09-17 (`docs/playtest-2026-09-17-void-floors.md`).
   Original finding:
   `Ultima8Engine::paint()` fills the frame black only when `_highRes`
   (`ultima8.cpp:711`), which the `usehighres` config key sets. Without
   it, wherever no item paints — the void the islands stand in, the void
   beyond the plaza's walls — the previous frame's pixels stay. The first
   island plates (`E2-island-1-stale-void.png` kept as the example) came
   back with the plaza, Map 18's hall and earlier islands painted around
   the cloud, identical across three teleports; the engine confirmed no
   wall or floor item exists south of the plaza (`findShape 10`/`35`:
   none with y > 12000) and FIXED.DAT has only the 78 tiles and two
   spires there. With `usehighres=true` in `scummvm.ini` the void is
   black and the plates are clean. **A player at the plaza's south edge
   without that key sees the plaza's own earlier frames beyond the
   wall.** A map or installer decision: black/darkness tiles around the
   islands, or the installer setting `usehighres` — HANDOFF carries it.
2. **`MainActor::teleport` straight from Map 18 to the island did not
   land once** (the first high-res run: the plate showed a hall, the
   next teleport did land). The runs that hop 18 → plaza → island landed
   every time. Keep the in-map hop.

## Harness anomalies

1. `session.sh dbg` still dead (see the obelisk report); `dbg.sh` used
   throughout.
2. The backpack gump opened on every fresh start and had to be
   double-clicked away before each run; on two runs it was open again by
   the time of the plate.

## Disk changes

- `shared/u8-lv-patched/`: the four artifacts replaced with the
  2026-09-15 cloud-tile build.
- `~/.config/scummvm/scummvm.ini`: `usehighres=true` added under
  `[scummvm]` and left there (backup `scummvm.ini.bak-2026-09-15`). The
  640×400 canvas keys unchanged.
- The playtest session was stopped at the end.
