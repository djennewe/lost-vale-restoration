# Phase C, Map 17: Cloud City as the 1994 shots show it (2026-10-17)

Branch `wt/vignettes-map17`, worktree `lv-wt-map17`, based on `wt/art-1994`.
The builds went into the worktree's private `shared/build`:
- FIXED.DAT, by `build_all_maps.py --no-previews`;
- EUSECODE.FLX, by `build_eusecode.py --full`;
- the 880 row of the art props step, injected by itself.

None of the following was run: `install_lv.sh`, `integrate.sh`, the full `build_artifacts.sh`, ScummVM. `ARTIFACTS.sha256` was not re-recorded.

## 1. Vignettes re-solved to the z=0 encoding

I applied the rule in `phaseC-art.md` §3 to `screen11.json` and `screen12.json`. Each JSON's `origin_note` and `verify.phase_c` record the conversion:
- the 2000/2004/2003 floors became 874/876/877 at z−1;
- every other item and actor at z ≥ 2 moved to z−2 at `resolve(x, y)`;
- the 2001 column became 875 and the 2002 sun half became 878.

Scores below use `vignette_paint.Painter(typeflag=, shapes=)` on the built `TYPEFLAG.DAT`/`U8SHAPES.FLX`, measured with `vignette_replay.score`. `vignette_replay.py --built screen11 screen12` reproduces them, and the published renders were re-published from that replay.

| shot | z=1 replay (class / strict) | re-solved, built | phaseC-art bar | final |
|---|---|---|---|---|
| screen11 | 99.940 / 99.919 | **99.929 / 99.909** | 99.929 | **99.929 / 99.909** |
| screen12 | 82.823 / 82.489 | **83.179 / 82.840** | 83.179 | **87.413 / 87.095** |

What I added to screen12's open gaps (+4.23 points over the re-solve):
- **Eye Shield half.** 878 f1 matches the shot exactly (274/274 px at screen (122,94)) and is placed at world (3559,3311,0). It is now quest half 2.
- **Avatar.** Shape 1 f72 matches exactly (742/742 px at (204,115)) and is placed as an actor at (3807,3231,0).
- **Tile frames.** Each lattice-fill cloud or gold tile now takes the frame (874 f0-4 / 876 f0-1) that matches the shot. 19 tiles changed.
- **Nook dais.** One 877 slab at local (2175,2271,0) matches the dais's marble: +0.18.

What I tried and dropped:
- 874 tiles on a 64 grid over the gold/cloud edge (330 candidates): none helps. The edge lobes are not floor tiles.
- Left throne: the best 223 placement is f3 at 497/1260 px, and it lowers the score. A full search of shapes 0-859 found no match.
- The translucent blue-rimmed object over the nook skeleton has no retail match.

`score()` counts ids below 2000 as retail. Its provenance split therefore lumps 874-880 in with retail, so the JSONs keep the z=1 split.

## 2. The map (`build_map_17.py`, rewritten)

The two shots are stamped verbatim with `vignette_place.stamp(..., art_map={596: 880}, fill=(874, (0,1,2)))`. The city around them:
- **Floors.** Open 874 cloud, and gold 876 with ragged edges for the streets and courts: scroll court, forecourt, aisles between the strips, processional, south street, arrival landing, east court.
- **Walkways.** Raised 877 strips (A y 3103, B y 3583, C y 5759). Banded 875 f1 posts stand at 192 units on both sides: on the slab's front edge at z 8, and on the cloud behind it, every fourth post two drums tall.
- **Pillars.** Gem pillars (875 f0 with an 880 cap) line the streets and fill the courts. Screen11's outer square of plain columns is carried round the plaza.
- **Plaques** stand on single stone steles.
- **Edges.** The cloud outline runs 8-10 cells past the features, lobed and smoothed. 497/498 curbs guard every walkable side facing the void, and `void_floor` plates cover the void in view.
- **No stone rooms, tapestries, lamps or daises.**
- **Windows.** `window_clear` drops every generated item whose sprite would enter either shot's window.
- **Size.** 5,571 raw items. No globs.

`fill_gaps` covers one defect in `vignette_place.hidden_ground`. A walkway slab's y is ≡ 31 mod 128, so its box grazes a second cell row, and that row is counted as floored. Four cells (19-21,24) and (34,24) were left bare; `fill_gaps` clouds them.

Built window vs 1994 GIF, class contract, via `/tmp/map17/bw.py` (built FIXED.DAT, built shapes, vignette actors injected):

| shot | built window class / strict | px differing from the vignette replay |
|---|---|---|
| screen11 | **99.929 / 99.909** | **0** |
| screen12 | **87.413 / 87.095** | **0** |

Evidence files:
- `screenNN_built_window.png`: shot | built | diff at ×3.
- `screenNN_context.png`: a 3×3 grid of shot windows from the built map, the shot's own window outlined in magenta, at ×2.
- `map17_whole.png`: the whole built map at 50%.

## 3. Pins and usecode

**Obelisk.** 861 is retired from the map. The obelisk is screen11's retail composite. The front drum, 875 f1 at (4127,7199,0), carries q90. `derive_map_pins` was updated to match:
- the DECORATIVE row is now the drum;
- the DEFERRED EGGMAGNET row is located at the drum.

No usecode references 861.

**Shield halves.** These became **878**, the 1994 art: frame 0 is the sun half, frame 1 the eye half, in 870's order, on the same 828 TYPEFLAG row.
- Changes:
  - `u8c_symbols.TYPE_SHAPES['TypeAOFrizbee']` went 870 → 878.
  - `lv_shapes.SHAPE_SHIELD_HALVES` now equals `SHAPE_SHIELD_HALVES_1994`.
  - The split-828 row was renamed `SHAPE_SHIELD_HALVES_828_SPLIT` (870), still built and placed nowhere.
- EUSECODE was rebuilt (`build_eusecode.py --full`: 54/56 compiled, the 2 allowlisted failures; it warns that `detection_tables.h` is absent in the worktree).
- Every usecode reader that finds the halves reads `TypeAOFrizbee`: SHADES:153, REAPPLY:253/264, ZEALSHLD via npcnum 236. The frame-4 anchor still names a frame 878 lacks, as it did for 870.

| pin | from | to |
|---|---|---|
| half 1 878 f0 q81 npcnum 236 | 870 (6208,1568,0) | (4259,7199,0), screen11 |
| half 2 878 f1 q82 npcnum 236 | 870 (7232,1568,0) | (3559,3311,0), screen12 |
| pad 209 + EggReapply | (5376,11136,0) | (4608,9984,0) |
| trigger 208 → Map 13 | (5376,11520,0) | (4608,11008,0), on the pier beyond the channel |
| plaques 614 q69 / q70 / q55 / q68 | (2495,5121) / (5055,5121) / (4127,7680) / (5055,9217) | (3615,4544) / (4671,4544) / (4127,8256) / (4127,9600), all z 16 on steles |
| scroll 864 q80 | (3328,1536,8) | unchanged, now on an 877 plinth |
| obelisk q90 | 861 (4095,7167,16) | 875 f1 front drum (4127,7199,0) |

**Arrival.** This answers the Map 13 constraint: the player now arrives heading south. On Map 17, trigger 208 sits south of a void channel whose curbed edge runs 1152 units either side of the pad's x. The hatch box of 208 is ±416.
- A hold S stops at the curb.
- A hold SE or SW slides along the curb past the channel's end and keeps going away from 208.
- From Map 13's side, the heading from pad 209 to trigger 208 is S, a heading Map 13 already models.
- Checked with `/tmp/map17/holds.py`, a mirror of `test_route_reach.arrival_corridors` using `avatar_mover.hold`: all 8 headings × all mover modes, at 1.5 s and 4 s. **No trigger, fall or teeter.**
- The in-tree gateway-209 check passes with Map 13's current heading.

`map_pins.json` was regenerated (`derive_map_pins.py`).

**New shape 880, the gem pillar cap.** Screen11's gems are retail 596, which is `TypeTalisman`: carryable, and frames 0-3 are the Map 11 element talismans. `test_uc_reentry` caught it ("no other re-applied map carries a 596 — also on [17]").
- 880 is a new `copy` row in `lv_art_props`: 596's 8 frames, copied verbatim at build time, on donor 443 (SI_FIXED), footpad (1,1,1).
- It was injected into this worktree's build by that row alone (`/tmp/map17/inject880.py`, the same calls `lv_art_props.main()` makes).
- The vignettes keep 596; the builder maps 596 → 880.
- Recorded in `lv_shapes`, `docs/art-track.md` and `.claude/rules/shape-ids.md`. The next free id is 881.

**`vignette_place.py`** (Main's (a)):
- a synthetic id ≥ 2000 not in `art_map` is refused, and real ids < 2000 place directly;
- an `art_map` value may be an int (the item keeps its frame) or a `(shape, frame)` pair;
- `ShapeFlags` reads the built TYPEFLAG, falling back to the install copy.

**`test_map_edges.py`.** A map with no glob eggs takes its footprint from its floor tiles instead (flat LAND items, not counting the black void plates). Map 17 has no globs now.

## 4. Tests (worktree build)

| test | result |
|---|---|
| test_map_hygiene | 10/0 (map 17) |
| test_map_edges (6 LV maps) | all contained |
| test_route_reach | 154/0; map 17: both halves, scroll court, walkway top, east court, trigger 208; gateway 209/208 holds clear |
| test_paint_cycles | 40/0 |
| test_schedule_destinations | 200/0 |
| test_monster_eggs | 420/0 |
| test_map_roundtrip | 14/14 |
| test_art_props | 316/0 (§3 obelisk composite, §4 the 874 floor and no 862 on Map 17, §6 the 877 plinth, §10 halves 878, §10b gem cap 880, §1 `copy` rows) |
| test_map_pins_fresh | 3/0 |
| test_png2shape | 42/0 |
| test_uc_* (9 files) | all pass (reentry 140/0, shades 58/0) |

## 5. Open issues

- The art rows for 861, 862 and 870 are still built. 862 is still Map 13's phase-B stand-in. Retiring the rows needs an art rebuild; this is the integration's call.
- Run `tools/integrate.sh` (`/artifact-rehash`). U8SHAPES, TYPEFLAG (880), EUSECODE (878) and FIXED all changed.
- Not yet checked in ScummVM.
- screen12 is still at 87.4%. What remains: the 1994 cloud-lobe edge art over the gold, the nook dais rims, the left throne, and the translucent object. None of these is recoverable from retail.
- The vignettes need `vignette_replay.py --built`. The retail painter has no 874-880.
- The `--write-verify` provenance split mislabels 874-880 as retail, because `vignette_replay` was not edited.
- 875 f0 (the plain paint), 876 and 877 are single-shot art (D-track open issue 5) and need Douglas's sign-off.
