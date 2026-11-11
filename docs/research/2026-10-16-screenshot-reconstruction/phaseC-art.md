# Phase C, art: the 1994 pixels as shapes 874-879 (2026-10-16)

Branch `wt/art-1994` (worktree `lv-wt-art`). The cross-shot-validated 1994
art, plus the single-shot floor pieces the brief named, is now built into
`U8SHAPES.FLX` + `TYPEFLAG.DAT` by the art-props step, index for index. No
map places these shapes yet: 862 and 870 stay placed until the builders
switch over (phase C maps). No vignette JSON was edited.

## 1. Exact-pixel import path

- **`tools/png2shape.py --indexed`** and **`png2shape.indexed_pixels()`**.
  The PNG's U8PAL indices go into the frame verbatim. Nothing is keyed,
  trimmed, scaled or quantized, and 255 stays the transparency key. The
  anchor must be given (`--anchor explicit|donor`).
- Two refusals:
  - a non-P-mode PNG;
  - a PNG whose palette differs from U8PAL at any index it uses, since
    copying indices from a foreign palette would recolour the art silently.
  - `--indexed` with `--height/--width/--key-despill` is a usage error.
- **`lv_art_props.py` `indexed` rows.** An entry is `(registry id, frame[, (xoff, yoff)])`:
  - the PNG path and hotspot come from `vignettes/art_registry.json`;
  - `hotspot_shift` adjusts the hotspot for the floor rows;
  - an explicit `(xoff, yoff)` covers a frame the registry has no hotspot
    for.
  - Frames graded `reference-only` or `residual` are refused (blocker 1).
- **`oversize`** (a stated reason) lets `check_fit` pass art that is
  deliberately taller than its box. The only user is the walkway's back rim.
- The traps from D-track turned out not to bite these 13 frames. None
  contains a higher duplicate index (144, 28, 51, 15, 140, 191, 239). The
  RGB path with `--no-key --no-trim` and an explicit anchor would also have
  reproduced every frame (0 index differences, measured). The indexed path
  guarantees by construction what the RGB path managed by luck on this set.

## 2. Shape ids allocated

The next free static ids were 874+ (`.claude/rules/shape-ids.md`). No
EUSECODE class exists at 874-879 and no manifest pin falls in that range
(both tested). `lv_manifest.json` pins only classes and flags, so it does
not change; no existing art row touches it either.

| id | `lv_shapes` constant | frames (registry) | grade | TYPEFLAG | anchor |
|---|---|---|---|---|---|
| 874 | `SHAPE_CLOUD_1994` | 0-4 = 2000:0-4 (3/4 are mirror f0/f2) | cross-shot-validated | **163's row** = 301's with `SI_DRAW` swapped for `SI_OCCL` (`1b00400400010101`), (4,4,0) | (31,32) |
| 875 | `SHAPE_WHITE_COLUMN_1994` | 0 = 2001:0 plain, 1 = 2001:1 banded | single-shot / cross-shot | 443 `statue` with (1,1,5) | (8,47) |
| 876 | `SHAPE_GOLD_BRICK_1994` | 0-1 = 2004:0-1 | single-shot | 163's row, (4,4,0) | (31,32) |
| 877 | `SHAPE_MARBLE_WALKWAY_1994` | 0 = 2003:0 (slab + gold trim + back rim in one frame) | single-shot, 19 inferred px | 113 raised platform, (4,4,1) | (31,52) |
| 878 | `SHAPE_SHIELD_HALVES_1994` | 0 = 2002:0 sun (left), 1 = 2005:0 eye (right): 870's order | cross-shot-validated | 828 whole, (1,3,3) | (6,32), (-4,36) |
| 879 | `SHAPE_SACRED_SHIELD_1994` | 0 = 2013:0, the altar Shield | cross-shot-validated | 828 whole, (1,3,3) | (6,32) |

Notes:
- **The walkway trim is in the walkway frame itself.** The 62×52 tile
  carries the gold/white back rim and the gold-trimmed front face, and the
  registry has no separate trim asset. Its 19 `inferred_px` are listed in the
  registry and boxed in magenta on the contact sheet. They cannot be flagged
  inside a shape.
- **The eye half has no registry hotspot**: it is never placed whole.
  (-4,36) is where screen04's altar Shield puts it against the sun half's
  (6,32), offset (+10,-4). So 878's two frames at one position reassemble
  879, 608 of 609 px (`test_art_props` §13).
- **The column donor is 443, not retail 12.** 12 carries `SI_OCCL|SI_LAND`.
  443 matches the registry's sort flags (solid, not land) and the existing
  art-track convention for statues.
- **The floor flags.** The task specified "301's flags, no SI_DRAW trap".
  The proof below (§3) chose `SI_OCCL` in place of `SI_DRAW`, and retail 163
  carries exactly that row.
- **Untouched art:** every shape and TYPEFLAG row outside 874-879 is
  byte-identical to before the rebuild, 860-873 included (checked over all
  2048 slots). `ANIM.DAT` is unchanged.

## 3. Cloud z-encoding (Fable fix #8): decision and proof

**Decision: floors at z=0, objects standing on them at z=0.**
- **Floors.** 874, 876 and 877 carry the registry hotspot with **yoff + 1**:
  (31,32), (31,32) and (31,52). A tile at z=0 therefore paints exactly the
  pixels the reconstruction's z=1 tile painted.
- **Objects.** Objects that the cloud vignettes lifted to floor + 1 drop by
  2 in z, to the nearest (x, y) that projects to the same pixel. For their
  32k positions that is **(x-1, y-1, z-2)**: the retail 31 residue, so it is
  the engine's own convention and pixel-identical. The few off-grid items
  need (-5,-5) or (-5,-8): the sun half, nook clutter.
- **Floor flags: `SI_OCCL`, not `SI_DRAW`, not neither.** This is retail
  163's row, the glob floors' flag. For two flats on one z, `SortItem::below`
  sorts `SI_DRAW` first, then `SI_OCCL`, then the rest. With `SI_OCCL` the
  cloud draws over the `SI_DRAW` earth it lies on (screen13), and flat props
  with neither flag lie on top of it (screen12's straw, 720).
- **In-engine.** The Avatar stands on a zero-height floor at z=0, which is
  where the re-solved vignette puts him (screen11: (2495,2591,0), pixels
  unchanged). The 1-px settle of the z=1/z=2 scheme goes away.

**The re-solved z rule for phase C** (vignette-local; origins unchanged):
- items of 2000/2004/2003 become 874/876/877 at **z − 1**;
- in screen11/12, every other item and rendered actor with z ≥ 2 (all of
  them rest on the floor layer: columns, gems, obelisk pieces, the shield,
  nook clutter, the Avatar) becomes **z − 2 at `resolve(x, y)`**;
- the single screen11 column at z=0 (the frame-edge column "under the z=1
  cloud") stays where it is;
- in screen01 and 13, non-floor items keep their place. Their floors sit on
  the same z as the cliff course and earth bases (screen01: cloud at local 0
  = world 56, not 57).

```python
def proj(x, y, z):                      # C division per term, world coords
    return x//4 - y//4, x//8 + y//8 - z
def resolve(x, y, z, dz=2):             # nearest pixel-identical (x', y') at z-dz
    want = proj(x, y, z)
    return min(((x+dx, y+dy) for dx in range(-24, 9) for dy in range(-24, 9)
                if proj(x+dx, y+dy, z-dz) == want),
               key=lambda p: abs(p[0]-x+1) + abs(p[1]-y+1))
```

**Proof.** The proof re-solved scratch copies of screen01/11/12/13 (in
`/tmp/art1994/scratch/`; the committed JSONs are untouched). Each was
painted with `vignette_paint.Painter(typeflag=, shapes=)` on the built
`TYPEFLAG.DAT`/`U8SHAPES.FLX` (no registry extras) and scored with
`vignette_replay.score`. The acceptance bar was the current class score
− 0.2 points.

| shot | current class / strict | **engine encoding class / strict** | Δ class | px changed vs current replay | objects without the (x,y) re-solve | floors at retail hotspot (no +1) | floors with neither flag | floors with 301's `SI_DRAW` |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 01 | 94.094 / 94.022 | **94.094 / 94.022** | +0.000 | 0 | 94.094 | 91.349 | 94.094 | 94.094 |
| 11 | 99.940 / 99.919 | **99.929 / 99.909** | −0.011 | 6 | 89.954 | 64.177 | 99.929 | 99.929 |
| 12 | 82.823 / 82.489 | **83.179 / 82.840** | +0.356 | 532 | 69.557 | 51.680 | 82.652 | 83.179 |
| 13 | 74.125 / 73.117 | **74.125 / 73.117** | +0.000 | 0 | 74.125 | 64.120 | 74.125 | **63.407** |

All four pass the bar. The other columns are why each part of the rule is
there:
- the (x, y) re-solve is needed (screen12 drops 13 points without it);
- so is the yoff + 1 (screen11 falls 36 points at the retail hotspot);
- `SI_DRAW` is the trap the brief named: the screen13 cloud lobes sink
  under the earth, −10.7 points;
- with neither flag the screen12 straw sinks under the cloud, −0.17 points.

The changed pixels are all sort changes; no projection moved:
- **screen11, 6 px lost.** The z=0 frame-edge column's foot is no longer
  over-painted by the front cloud tile. With the cloud at z=0 the flat sorts
  under everything standing at z=0.
- **screen12, +367 / −157 px.**
  - The banded posts now draw over the walkway's rim (gain, 367 px).
  - Rubble 526 draws over a walkway tile (−109).
  - A walkway tile covers a column foot (−36).
  - The straw edge (−12).

## 4. Build

The art steps of `tools/build_artifacts.sh`, 1-6, were run by hand in
order into the worktree's private `shared/build`:
- `patch_typeflag`
- `lv_wood_wall`
- `lv_tiny_tar`
- `lv_god_statues`
- `lv_art_props`
- `lv_tiny_avatar`
- `lv_monsters`

`build_eusecode.py`, `build_all_maps.py` and `install_lv.sh` were not run,
and nothing was written under `shared/data`.

Resulting hashes (`ARTIFACTS.sha256` deliberately **not** re-recorded: EUSECODE/FIXED were not rebuilt, and
the record belongs to the integration's `/artifact-rehash`):

| artifact | before | after |
|---|---|---|
| TYPEFLAG.DAT | `7c1d8454…` | `b91f24c0a70ace4b2eca241414038aca961471e82ef90fdf5fa5a05d89889c73` |
| U8SHAPES.FLX | `e0af51ea…` (16,478,258 B) | `428a851dc62dc6c5709e705ad618d28233ad04ffb8dea6cd8ef17374ea02736f` (16,492,071 B) |
| ANIM.DAT | `696dbeb9…` | unchanged |

## 5. Contact sheet and per-frame equality

`phaseC-art-contact.png` (beside this file):
- each built frame is read back from `U8SHAPES.FLX` with
  `shape_viewer.frame_to_image` at ×4;
- the source PNG sits beside it at ×4;
- the walkway's 19 inferred pixels are boxed in magenta.

| shape:frame | source | size | opaque px | index-equal | anchor |
|---|---|---|---:|---|---|
| 874:0 | 2000:0 | 62×32 | 1024 | 1984/1984 ✔ | (31,32) |
| 874:1 | 2000:1 | 62×32 | 1024 | 1984/1984 ✔ | (31,32) |
| 874:2 | 2000:2 | 62×32 | 1024 | 1984/1984 ✔ | (31,32) |
| 874:3 | 2000:3 | 62×32 | 1024 | 1984/1984 ✔ | (31,32) |
| 874:4 | 2000:4 | 62×32 | 1024 | 1984/1984 ✔ | (31,32) |
| 875:0 | 2001:0 | 16×47 | 710 | 752/752 ✔ | (8,47) |
| 875:1 | 2001:1 | 16×47 | 698 | 752/752 ✔ | (8,47) |
| 876:0 | 2004:0 | 62×32 | 1024 | 1984/1984 ✔ | (31,32) |
| 876:1 | 2004:1 | 62×32 | 1016 | 1984/1984 ✔ | (31,32) |
| 877:0 | 2003:0 | 62×52 | 1527 | 3224/3224 ✔ | (31,52) |
| 878:0 | 2002:0 | 30×28 | 339 | 840/840 ✔ | (6,32) |
| 878:1 | 2005:0 | 24×28 | 274 | 672/672 ✔ | (-4,36) |
| 879:0 | 2013:0 | 30×28 | 609 | 840/840 ✔ | (6,32) |

All 13 frames are equal over the whole canvas, transparent pixels
included.

## Tests run

- `python3 agents/map-populator/src/test_png2shape.py`: **42 passed, 0 failed**.
  New: the indexed round trip on a synthetic PNG covers duplicate-RGB high
  indices, the magenta-nearest index, a transparent margin and a negative
  xoff. Also new: both refusals, both CLI guards, and every 1994 frame the
  build injects round-tripping (13).
- `python3 agents/map-populator/src/test_art_props.py`: **306 passed, 1 failed**.
  New §13: built frames equal the PNGs, anchors, the floor yoff + 1, the
  halves reassembling 879 (608/609), and the floor rows (`SI_OCCL`, no
  `SI_DRAW`, equal to 163/301-swapped). It also checks that EUSECODE and the
  manifest are empty at 874-879.
  - The one failure is §5 "the eight ring monoliths are untouched: 9". It is
    pre-existing. It reads only Map 10 in FIXED.DAT, which this work did not
    rebuild, and the phase-A screen18 stamp on this branch is the likely
    source [INFERENCE].
- A scratch CLI smoke test ran `png2shape --indexed` on cloud f0/f1 into
  copies, at slot 880 with re-read OK.

For the main agent to run after integration: `tools/integrate.sh`
(artifact rehash cascade) and the estate (`tools/run_all_tests.sh`), at
minimum `test_art_props`, `test_png2shape` and `vignette_replay.py --built`.

## Commits on `wt/art-1994`

- `84cfa68`: `png2shape --indexed`, the `lv_art_props` indexed rows, 874-879,
  tests, and the doc and rule id ranges.
- The commit that adds this report also adds the contact sheet and switches
  the floors' donor from 425 to 163 after the proof (`git log -1 -- <this file>`).

## Redraw list (out of scope here, recorded)

| item | why it cannot ship from the shots |
|---|---|
| Gods 860, frames 0-2 (2010-2012) | Single-shot (screen04), and Felicitar has 42 inferred px. The 1994 scale (33×53, 43×38, 31×67) breaks the shatter frames 3-41, which need redrawing at that scale. |
| Water Zombie 872 (2050:0-2) | Only three single poses; every other animation frame must be drawn to match. |
| Fire pillar 865 frame 2 (2021) | The lower third (rows 64-90) is missing; 2020 is a reference crop only. |
| Zealan villagers (2041, 2042) | Single-shot actor poses; whole animation sets to draw. |
| Blue root plants (2045) | Single-shot drafts with fence-bar gaps. |
| Foam 2061, halo 2060, skull beam 2062 | Residuals, not sprites. |
| Also still single-shot among the shipped ids | 875:0 plain paint, 876 gold brick, 877 walkway (19 inferred px): built as the brief asked, but they need a second source or Douglas's sign-off before they replace anything (D-track open issue 5). |
