# Phase D, static slice: screen12, screen13, screen07 (2026-10-25)

Branch `wt/static`, worktree `lv-wt-static`. Builds went into the worktree's
private `shared/build` (`tools/build_artifacts.sh --record`). The main
checkout's build, install and ScummVM trees were not touched. EUSECODE did not
change (`2e3b71c2…`), so the detection md5 is unchanged.

Douglas's rule for this phase: cut what each shot shows, index for index, and
draw what it hides in the same style. Every new frame is in
`vignettes/art_registry.json`, with its source shot, a grade and the list of
pixels that were drawn rather than cut. All new frames are single-use art and
need Douglas's sign-off.

## Shape IDs

| id | what | registry | grade | TYPEFLAG |
|---|---|---|---|---|
| 882 | screen12 throne-nook dais, 3 frames | 2006 | single-shot | 113, (4,4,1), as 877 |
| 883 | walkway strips' east end: 877 cut along the screen vertical through its front corner | 2007 | single-shot | 113, (4,4,1) |
| 884 | gold brick meeting the cloud: f0/f1 cloud lobes over gold, f2 the gold corner | 2008 | f0/f1 single-shot; f2 **cross-shot** | 163, (4,4,0), as 876 |
| 885 | screen12's left throne, seen side on | 2009 | single-shot, 27 drawn px | 223, (1,2,5) |
| 886 | screen13 floor tiles, 35 single-use frames | 2015 | single-shot | 163, (4,4,0) |
| 865 f2 | the Pillar of Fire, completed (shape and class kept; only the art changed) | 2023 | single-shot, drawn lower part | 865's row, unchanged |

887 is the next free id. Nothing reuses 861 or 862.

`lv_art_props`: a `frames` row now accepts a dict entry `{'indexed': (sid, f)}`. The 865 row uses it for frame 2; frames 0, 1 and 3 are unchanged.

## What the shots turned out to be

### screen12

- **Nook dais.** This is 877's marble run along y, lit two steps lighter
  (240-242 where 877 uses 242-244). A mirror of 877 matches 732 of 1006 marble
  pixels exactly. It is three tiles at local (2207, 2207/2335/2079); the third
  crosses strip A. The tiles' textures differ, so each tile is its own frame:
  shot pixels where the tile is visible, the lightened mirror of 877 where it
  is hidden.
- **Strip ends.** Both walkway strips end at local x 3071, behind a two-drum
  post at (3103, y). The cut runs along x−y = const. The camera sees that
  plane edge-on, so the strip shows no end face (883).
  - The upper strip's end post at the right frame edge was missing from the
    vignette: +0.87.
  - `build_map_17.STRIPS` A and B now end at x 3967 and finish with the 883
    piece at 4095.
- **Gold/cloud edge.** The edge sits on the 128 lattice. Five cells in the
  shot are only two distinct frames (A ×3 and B ×2, 0 conflicts between
  copies).
  - The bottom-right corner cell, C, appears in full in screen13 at (200,152):
    all 470 pixels screen12 shows are equal, and screen13 shows the rest.
- **Left throne.** No retail frame matches it, mirrored frames included (223's
  best is 478 pixels). It was cut from the shot; the seat's right edge under
  the pot is drawn (885).
- **"Translucent blue-rimmed object".** This is retail 843 f0, an exact
  142/142 match. It was sorting under the skeleton; at z 1 it lies on top.
- **Other changes:**
  - straw 720 f0 ×4 in the nook;
  - the back colonnade posts at (x+32, y+32, z 8). This puts the same pixels
    on the same view ray, but the posts now sort over the strip's 12-pixel
    rim, as the shot draws them. `build_map_17.walkways()` lays every back
    post this way;
  - three sort-only nudges along the view ray: rubble 526 (z 2), bottle 471
    (z 2) and vase 663 (z 4).

### screen13

Five things:
- **The tree.** It is 74 f1 (a stump) with 74 f0 on top at z 40. That is how
  retail stacks a tall tree. Gain +2.1.
- **The Avatar.** He is 1:197, matching 745 of 816 pixels at (205,97). He is
  now an actor at local (2907,2331,0). Gain +1.5.
- **Earth frames.** Chosen by match, from 4 f30-33 only.
- **Cloud texture.** 5,271 pixels were cloud texture in the wrong class. The
  shot's cloud patches overlap on a 32-unit grid in at least three phases,
  so no lattice of reusable rim tiles reproduces them. Each of the window's
  floor tiles is therefore cut to the pixels the shot shows it owning:
  - earth in those pixels becomes transparent (a bite);
  - lobe pixels that no tile drew go to the nearest tile;
  - everything else keeps the 1994 tile's own pixels;
  - the result is 886's 35 frames.
- **The gold corner** is 884 f2 (registry 2008, f2).

### screen07

The Pillar of Fire's art is now 865 frame 2, at the same pin and with the same
quest role: COLPUZZL still destroys `TypeElementalColumn` 865, and the look
still reads "column of roaring flame".
- **Cut from the shot:**
  - the upper two thirds (2021);
  - the lower shaft, where the shot shows it between the rubble mound and the
    candle post;
  - the yellow flames on both flanks;
  - the lava at its foot.
- **Drawn:** the shaft behind the candle post, which continues the rings, and
  the lava pool behind the post's base (173+99 pixels).
- **Left out:** the shaft's lower-left (x 170-176 below y 106). That area is
  the rubble mound's in 1994, and the mound sorts behind the pin in the
  engine.
- **Stand-in:** the mound's right edge, which the old flame art used to cover,
  is a retail stand-in 99 f1 at (7580,21432,0) (`SCREEN07_STANDINS`, +0.34).

## Scores

| shot | replay, built (before → after) | built window --actors (before → after) | in-engine class, SCORES.md → now |
|---|---|---|---|
| screen07 | 86.94 → 86.63 | 87.41 → **91.20** | 86.06 → **89.90** |
| screen12 | 87.41 → **97.94** | 87.41 → **97.94** | 85.90 → **96.37** |
| screen13 | 75.97 → **95.92** | 75.97 → **95.88** | 75.97 → **93.99** |

- **Why screen07's replay drops 0.3.** The replay used to paint the reference
  crop 2020, which carries pit and wall pixels. It now paints the pillar the
  build ships. `test_vignettes` scores the built window.
- **Floors raised:** 91.20, 97.94 and 95.88.
- **In-engine method.** `vignette_capture.py` ran on a pinned copy
  (`/tmp/claude-1000/static/game`, the worktree's `shared/u8-lv-patched`
  symlinked to it) with this build's artifacts. The binary was
  `scummvm-lv-console/scummvm`, on display :96 with a private
  `XDG_RUNTIME_DIR`. The captures are `screen07/12/13_ingame.png` beside this
  file.
  - screen13 now teleports to the Avatar spot (6363,1947,120) rather than the
    ground centre.
  - The session was stopped afterwards.

What remains, and why:
- **screen12, 2.1% left:**
  - the dais's far-left sliver (a fourth tile would overlap strip B);
  - rubble and strip-rim sort ties;
  - the mouse cursor.
- **screen13, 4.1% left:**
  - In 1994 the cloud draws over the tree crown and the spires' feet. The
    cloud patches therefore stood above those objects. Copying that would turn
    walkable cloud into a raised shelf, so I did not.
  - A grey shape behind the tree has no match.
- **screen07:** wall seams and the spikes (left out as before), plus the void.

## Tests (worktree build)

First build, FIXED `0f5c25d8…`, `tools/run_all_tests.sh`: 51 of 54 test files
passed.
- `test_art_props` failed on the new rows. Its checks now allow an overhang
  in any frame, let 865 frame 2 overhang by design, and expect 882-886.
- `test_map_pins_fresh` failed on the FIXED hash, as any rebuild does.
  `map_pins.json` was regenerated.
- `test_integration_state` failed because the install target is main's
  `u8-install`, which the parent's `tools/integrate.sh` updates.

One more change came after that run: three cloud tiles in `screen12.json`
were off the floor lattice, and I removed them. They drew nothing; the
window score is unchanged. The final build is FIXED `b1c523bb…` (TYPEFLAG
`3872c60c…`, U8SHAPES `f5e3de50…`, ANIM and EUSECODE unchanged). On it:
- `test_art_props`: 464 passed;
- `test_map_pins_fresh`: 3 passed;
- `test_vignettes`: 39 passed.

The in-engine captures were taken on `0f5c25d8`. That build differs from
the final one only by those three unseen tiles.

## Open issues for Douglas / the parent

1. **Sign-off on all the new art.** Pay particular attention to these:
   - 886's frames are per-tile cuts, some carrying odd lobe outlines: frames
     13, 22 and 31 carry thin or blocky protrusions where nearest-tile
     assignment handed them stray lobe pixels. They draw exactly the shot in
     place, but they are not reusable rim art.
   - 882's hidden marble is a lightened mirror of 877.
   - 885's seat is drawn under the pot.
   - The pillar's drawn lower shaft and lava pool.
2. **Map 17 extrapolation changed.** Strips A and B now end at x 4095 as the
   shot shows, where they used to run to 6655. The gold aisle east of the
   nook is unchanged.
3. **865 frames 0, 1 and 3** (the AI-drawn earth, air and water pillars) now
   stand beside a 1994-style fire pillar. Redrawing them as banded columns
   with element-coloured caps would match it. That is a design call, not
   done here.
4. **The eye Shield half (878 f1)** matches screen12 274/274 and screen04
   269/274; the only pixel left to add is the seam pixel, which screen12 hides
   behind a post. I left it as it is. "Draft" is only its registry label.
5. **Integration.** U8SHAPES, TYPEFLAG and FIXED changed. Run
   `tools/integrate.sh --record` after merging.
