# Phase C, Map 18: the Inner Sanctum as screen04 shows it (2026-10-17)

Branch `wt/map18`, worktree `lv-wt-map18`, based on main `b6fa347`.

Everything was built into the worktree's private `shared/build`:
- art steps 1-6 of `tools/build_artifacts.sh`, run by hand in order;
- EUSECODE with `build_eusecode.py --full`;
- FIXED with `build_all_maps.py --no-previews`.

None of the following was run: `install_lv.sh`, `integrate.sh`, the full `build_artifacts.sh`, or ScummVM. `ARTIFACTS.sha256` was not re-recorded.

## 1. Scores

All numbers are screen04's window painted from the **built** FIXED.DAT with the built U8SHAPES/TYPEFLAG (`vignette_built_window.py`, `Painter.built()`). The match is all-frame; class and RGB-within-12 agree to 0.001 here.

| state | class | note |
|---|---:|---|
| replay (`vignette_replay.py --built screen04`) | **99.914** | strict 99.902; the published render is identical |
| built window, map items only | 95.400 | no Avatar, no sparkles, no Shield |
| built window `--actors` (Avatar + three 202 sparkles) | 98.887 | before the ceremony: no Shield on the altar |
| `--actors` + the Shield where AOSCENE pops it (879 at (3111,8167,16)) | **99.914** | the shot's ceremony moment |

In the ceremony state, **0 px** differ from the replay. The gap between 98.887 and 99.914 is exactly the Shield, 609 px. The Shield is the ceremony's own item and is not placed on the map (§3).

Evidence, all in this directory:
- `screen04_built_window.png`: shot | built (`--actors`) | diff, ×3.
- `screen04_ceremony_window.png`: the same with the popped Shield, ×2.
- `screen04_context.png`: 3×3 shot windows from the built map, the shot's window outlined in red, with the Avatar and sparkles.
- `gods_860_contact.png`: shape 860, old (b6fa347, at ×2) above new (at ×4, because the 1994 frames are about half the size).

## 2. Gods art (shape 860, 42 frames)

| frames | what | source |
|---|---|---|
| 0-2 | sealed: Felicitar, Doloras, Timyra | registry 2010/2011/2012 PNGs, **index for index** (`indexed_pixels`), at the registry hotspots (15,49), (17,37), (16,62). Single-shot; Felicitar carries 42 inferred px. Read back from the FLX: 3/3 equal over the whole canvas. |
| 3-5 | freed, standing at rest | redrawn by `lv_god_frames.py` |
| 6-41 | three runs of 12 (6 shatter + 6 wake) | redrawn by `lv_god_frames.py` |

What `lv_god_frames.py` does now:
- **Scale.** Every figure keeps its old height × 67/124. 67 is the 1994 Timyra and 124 our encased Timyra; she is the god whose 1994 and 2026 poses agree. The freed gods come out 59 px tall. Shard speeds and canvas margins scale with them.
- **Palette.** The figures are re-quantized to the 58 U8PAL indices the three 1994 statues use: the 163-175 amber/brown ramp, the 50-62 yellows and oranges, and the dark greys of the figures inside.
- **Shards.** These are the 1994 statue's own pixels cut into 15 Voronoi pieces. They are not re-quantized.
- **Continuity.** `test_god_animation` checks both ends of every run. Each run's first frame **is** the 1994 statue, pixel for pixel, at its hotspot, with nothing else drawn. Each run's last frame equals the god's rest frame at the same world point.
- **The figure's feet** are on the god's footprint centre, 8 px above the hotspot.
- **Every frame is now a P-mode PNG.** `run/anchors.json` holds the hotspots, so `lv_god_statues.py` imports all 42 frames indexed. The magenta key and despill are out of the build path.

TYPEFLAG 860: donor 443 with **footpad (2,2,7)**. The old footpad was (6,6,8). anim stays (5,0,6), so usecode class 860 (GODANIM) is still dispatched.
- TYPEFLAG holds one footpad per shape. The registry's per-frame boxes (64×64×40/24/56) therefore become the tallest of the three.
- That box also holds a freed god.
- The built window shows no loss from it.

**New shape 881**, the striped prop on Felicitar's plinth (Main's decision B). It is registry 2014, single-shot and unidentified.
- It is an `indexed` row in `lv_art_props` on donor 443 (fixed) with the reconstruction's 32×32×8 box, flagged `oversize`.
- A (2,2,1) box was tried. It holds the sprite but costs the window 0.07 points (sort against Felicitar).
- Recorded in `lv_shapes.SHAPE_STRIPED_PROP_1994`, `docs/art-track.md` and `.claude/rules/shape-ids.md`. The next free id is 882.

## 3. The Shield: 879 is the restored Shield of the Ancients

screen04's altar Shield is 879, the 1994 art. The ceremony does pop a Shield onto the altar (AOSCENE `shield.pop`), and the quest's own logic points at 879:
- EZREKAL calls Pagan's 828 a forgery: "the same shape it is and the wrong symbols it has".
- The Map 17 halves are already the 1994 878, and those reassemble 879 (608 of 609 px).

So the restored Shield became 879. The work was done by subagent UcShield under my spec:
- **New symbol `TypeSacredShield` = 879** (`u8c_symbols`).
- **New class 879, `lv-new/SACSHLD.UNK`.** Its look() is "Ceremonial Shield of the Ancients Ones". It is pinned `TYPESACREDSHIELD: 879` in `lv_manifest.json`: one appended line, no existing pin or flag moved, and the build printed `PIN 0x036F`.
- **`lv-patched/SHADES.UNK` change 6** creates `TypeSacredShield` q83.
- **AOSCENE** searches `TypeSacredShield` q83.
- **`TypeAOArtifact` stays 828.** Its one remaining reader is ATLI change 5 (Douglas, 2026-10-09: "I have this shield!" is offered for Pagan's 828 and not for the restored Shield). That now holds by type. ATLI's code is unchanged; only a note was added to its header.
- **Save compatibility, required by Main.** A save made before 2026-10-17, between the Sacred Circle and the altar, carries the Shield as 828 q83. AOSCENE also accepts that item and pops it to the same spot. `lv-new/AORTA.UNK` stays, so that 828 keeps its 1994 name. Both paths are tested.
- **The map places no Shield.** A copy on the altar would be a second, free Shield from the start (`test_art_props` §10c).

## 4. Usecode

- **AOSCENE.**
  - `shield.pop(3056,8176,40)` → `(3111,8167,16)`. That is altar + (−16,−8,+16), screen04's spot, inside the altar's top face (box x 3064..3127, y 8048..8175, top z 16).
  - Camera: `move_to(3039,8415,36)` (Timyra), then `scrollTo(2783,8031,36)` (Felicitar) and `scrollTo(3039,7903,36)` (Doloras). z is the god's z 16 + 20, per `.claude/rules/camera-intrinsics.md`.
  - The order and the run kicks (2→30, 0→6, 1→18) are unchanged.
- **TEMPLENT.** The god re-apply sweep is now `within 2400` (it was 2200). Timyra is 2175 from the egg on y, which left a 25-unit margin.
- EUSECODE was rebuilt. 54/56 compiled; the two failures are the allowlisted EALOGO and TJORVI.

## 5. The map (`build_map_18.py`)

- **The stamp.** screen04 is stamped verbatim at origin (1408,6912,0) with `lv_cave_vignette.stamp`. art_map: 2010-2012 → 860 f0-2, 2013 → 879 (dropped), 2014 → 881. The gods and altar are the vignette's own items; they are tagged q301/302/303/310 after the stamp.
- **The cave.** `lv_cave_vignette.Cave` builds it from `SANCTUM_MASK` (cells x 1024..5119, y 6144..9343):
  - an antechamber behind the breach;
  - two passages round the rock at the shot's top;
  - the shrine, its floor run past the frame on every side, south edge y 9215.
  - Rock north/west of the floor gets cave wall (two 48-unit courses); rock south/east of it gets invisible wall.
  - Rubble and bones are dressed against the rock.
  - Nothing generated paints into the window.
  - The west passage is a cell narrower than the antechamber. `Cave._face` makes a whole run invisible if any of its pieces would paint into the window, and one long run on x 2303 lost all its walls that way.
- **Temple pieces kept as built.** The hall's side walls end on y=6144, the mask's first row. The closure had dropped those last pieces as rock-cell clutter, which opened the hall's corners onto the void (`test_map_edges`). They are now held out of the closure.
- **The outline.** The old rectangle's outline (shoulders y=6175, x=1024, x=5119, south y=9343) is retail's invisible wall (497/498), three courses (144). The anti-climb gate lines therefore still hold.
- **The void.** It is covered by `lv_cave_vignette.void_cover(items, within=SANCTUM_BOX)` (see §8).
- **Removed:** the two-tier dais and processional way, candelabra, rune columns, cushions, candlesticks, colonnade, tapestries, lamps, urns, the sanctum's flagstone globs, and the west/east/south temple walls.
- **Unchanged:** the crack line y=6143 (shapes 15/47, `BREACH_PIECES`, `tag_breach`), the breach rubble and EggTempleEntry.
- Map 18 has 1,737 raw items.

### Pin moves

| pin | from | to |
|---|---|---|
| Felicitar 860 f0 q301 | (3840,7680,0) | (2783,8031,16), on her plinth |
| Doloras 860 f1 q302 | (3072,6656,0) | (3039,7903,16) |
| Timyra 860 f2 q303 | (2304,7680,0) | (3039,8415,16) |
| altar 550 q310 | (3072,8192,24) | (3127,8175,0), no dais |
| EggAOCeremony q296 | (3072,8320,24) | (3072,8320,0); its ±192 box holds screen04's Avatar (3256,8152) |
| skull 331 npcnum 228 | (2976,8128,24) | (2496,8448,0), off the frame |
| sanctum south boundary | wall y=8703 | cave floor to y 9215, outline y=9343 |
| AOSCENE shield.pop | (3056,8176,40) | (3111,8167,16) |
| AOSCENE camera | (2304,7680,20) / (3840,7680,20) / (3072,6656,20) | (3039,8415,36) / (2783,8031,36) / (3039,7903,36) |
| TEMPLENT god sweep | within 2200 | within 2400 |

`map_pins.json` was regenerated (`derive_map_pins.py`).

## 6. Tests (worktree build)

All were run on the final worktree build. Every test passes.

| test | result |
|---|---|
| test_map_hygiene | 60/0 |
| test_map_edges | all 6 LV maps contained |
| test_route_reach | 160/0 (Map 18: full size sealed at the crack; shrunken reaches the antechamber, the altar at screen04's Avatar spot and the skull; gate lines continuous) |
| test_paint_cycles | 40/0 (879 on the altar top, no cycle) |
| test_schedule_destinations | 200/0 |
| test_monster_eggs | 420/0 |
| test_map_roundtrip | 14/14 |
| test_climb_width | 24/0 |
| test_endgame_hatch_box | 20/0 |
| test_art_props | 334/0 |
| test_crack_geometry | 10/0 (32 shrunken positions 2848..2879, 0 full-size; opened breach 129 positions, 120 headroom) |
| test_sanctum_clearance | 20/0 |
| test_map_pins_fresh | 3/0 |
| test_png2shape | 42/0 |
| test_god_animation | 48/0 |
| test_uc_dialogue / eggs / lordbrit / plntst / reentry / shades / sim / tiny_regrow / vale_return | 467 / 115 / 13 / 20 / 140 / 65 / 38 / 30 / 19, all 0 failed |
| test_symbol_retail_pins | 279/0 |
| test_manifest | 6/6 |

Test changes:
- `test_sanctum_clearance`: rewritten for the cave. It checks GOD_POS, footpad (2,2,7), each god on a two-tile plinth at z 16, the entry lane, no dais, the altar on the floor at screen04's spot, the egg on the floor with screen04's Avatar in its box, and nothing solid in the lane.
- `test_god_animation`: the new frame table, and run continuity at both ends.
- `test_art_props`:
  - §13 covers 881;
  - §10c is new: 881 is fixed, on Felicitar's plinth, and no Shield is placed;
  - the oversize check now accepts width as well as height.
- `test_route_reach`:
  - the Map 18 gate lines follow the outline;
  - the shrunken route now also reaches the altar at screen04's Avatar spot and the skull.
- `test_paint_cycles`: the Shield on the altar is 879.
- usecode tests: by UcShield (§3).

## 7. Commits

- `37c4edb`: the whole milestone: art 860/881, the 879 Shield usecode, the Map 18 cave, tests, docs and pins. The commit that adds this line records the commit list.

## 8. Open issues

- **Rehash.** TYPEFLAG (860 footpad, 881), U8SHAPES (860, 881), EUSECODE (879 class, AOSCENE, TEMPLENT, SHADES) and FIXED (Map 18) all changed. Run `tools/integrate.sh` (`/artifact-rehash`). Worktree hashes: TYPEFLAG `cdc40aed…`, U8SHAPES `3636cc90…`, ANIM unchanged `696dbeb9…`, EUSECODE `51c23f56…`, FIXED `74742141…`.
- **Not checked in ScummVM.** Needs: the ceremony with 879 popped at (3111,8167,16); the pan on the new triangle; each shatter starting on the 1994 statue; re-entry re-applying the freed frames; a legacy save holding 828 q83.
- **Single-shot art.** 860 frames 0-2 and 881 are single-shot (881 is also unidentified), and Felicitar has 42 inferred px. They need Douglas's sign-off, as D-track open issue 5 asks for the other single-shot art.
- **`lv_cave_vignette.void_cover` gained an optional `within` box.** Without it, every SI_DRAW glob floor on Map 18 (the temple court and halls) bred black LAND tiles view after view, and the halls could be walked off. With the default `None`, Maps 9 and 11 are unchanged. No edits were made to `vignette_place`, `vignette_paint`, `vignette_replay` or `item_sorter`.
- **The rock at the shot's top** reads from other cameras as a pillar with a black top. That is the 1994 caves' style, but it can look like a pit from the north.
- **The west wall** of the shrine on x 2303 rows 59-60 (y 7552..7807) has invisible wall only. Its run would paint into the window (the `Cave._face` rule), so from the north-west the floor ends at black there for 256 units.
- **Stale descriptions not updated here** (another agent's directory, or a tracker for Main): `CLAUDE.md`'s Known Limitations bullet on 860, `TODO.md`, `npc-dialogue/docs/dialogue-ao-scene.md:52-53`, `agents/map-populator/docs/art-placeholder-audit-2026-07-19.md:165-167`.
