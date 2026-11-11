# Phase 4 slice zero: shared dressing contracts

Branch `wt/vq4-s0` starts at `43cdeb5`. Main advanced independently to `cc50402` during this work; its cliff-shore exclusion is honored by the shared API. The five existing artifacts remain byte-identical to main. GLOB.FLX appends 60 LV prefabs after the 3,072 retail slots. Builders import the shared module through `build_all_maps.py`; map builders make no dressing calls.

## Artifacts and layout

`tools/build_artifacts.sh --record` rebuilt all six artifacts. A second full recording run began with the private FIXED.DAT removed, exercising first-build assembly. It reproduced the original five hashes. Byte comparisons with main confirmed all five files match.

| Artifact | SHA-256 |
|---|---|
| TYPEFLAG.DAT | `999bc6afa6dae596a1e0062ab1fb1c882489366eadc2e9afe77432692400667a` |
| U8SHAPES.FLX | `99ac982244eae904a61e4ff688a721a4bb86ec458dca7614661f3d2dd95529d5` |
| ANIM.DAT | `97ae5fc9ddaa6ef515427103264a3095a6d42776ac51e530954fb4846b4d0443` |
| EUSECODE.FLX | `b47c324cdad77646c27755acfdd5bca53a9d92e16268db229f18e7dd780d4205` |
| FIXED.DAT | `f1c3ccc143facda3076057039467e76cb44cd2a47c1691bc0917ad244befe378` |
| GLOB.FLX | `aabc1ad36f42c6bdd01cfcb7271f0765983a9914489d62a96a9bcb5e1d7c88ca` |

GLOB.FLX is 303,960 bytes and contains 3,132 slots. The FLX header retains retail's bytes except its count; directory offsets change to accommodate the larger directory. Each retail slot's payload, including empty and zero-item slots, is byte-identical. The permanent test compares the shipped archive with retail and checks appended payload hashes against the manifest.

Each appended payload contains a little-endian uint16 count followed by six-byte records: x, y, z, shape as uint16, and frame. Local world x and y are odd coordinates from one through 511; encoding divides them by two, and expansion restores `chunk + 2 * offset + 1`. Height is added directly.

| Slots | Family |
|---|---|
| 3072 to 3077 | barren earth and dry brush |
| 3078 to 3083 | barren earth, dead tree, stump, and brush |
| 3084 to 3089 | barren earth and debris |
| 3090 to 3095 | mixed rock and earth, retaining retail 455's oriented 386 corners |
| 3096 to 3101 | cloud and gold |
| 3102 to 3107 | cloud and white columns |
| 3108 to 3113 | cloud edge over stars |
| 3114 to 3119 | gold floor |
| 3120 to 3125 | filled flagstone and pebbles |
| 3126 to 3131 | earth yards, crates, pots, and brush |

`PREFABS` holds appendable data rows. Existing names, IDs, and payload hashes are frozen in `lv_manifest.json`. New authored rows allocate after every existing pin, including packed rows. Packed rows retain ordered item content and a content-addressed name; matching content reuses its ID. The compiler manifest reader preserves the new `globs` and `dressing` groups when saving class and flag pins.

GLOB.FLX builds at step eight of nine, after art and usecode and before FIXED. Map assembly also rebuilds globs before validation, so rows registered during a future builder's `pack()` are available to validators. The writer stages, round-trips every slot, and promotes with `os.replace`; rejected staged output is quarantined.

## Six-artifact consumers

These files now carry the sixth artifact or consume its built bytes:

- `.gitignore`: merged GLOB.FLX remains untracked, under M22.
- `.claude/rules/build-artifacts.md`: six-artifact inventory, nine-step order, append-only glob pins, and staged promotion.
- `tools/build_artifacts.sh`: build step, six-file verification, recording, and manifest output.
- `shared/build/ARTIFACTS.sha256`: GLOB.FLX is the sixth hash line.
- `install_lv.sh`: prerequisite, retail backup, STATIC installation, and clean restoration.
- `tools/integrate.sh`: installed and harness GLOB.FLX comparison and synchronization. The harness has seven copies across six artifacts because FIXED appears twice.
- `agents/usecode-compiler/src/test_integration_state.py`: installed and harness STATIC/GLOB.FLX checks.
- `agents/map-populator/src/glob_catalog.py`: default reader selects built GLOB.FLX, with retail fallback.
- `agents/map-populator/src/dressing_metrics.py`: built glob default; explicit retail measurements retain retail inputs; `fixed=False` permits archive-free measurement of supplied records.
- `agents/map-populator/src/test_visual_quality.py`: measurement provenance includes GLOB.FLX.
- `agents/map-populator/src/void_audit.py`: provenance hashes the selected built archive.
- `tools/map_viewer/build_map_viewer.py`, `feedback_server.py`, and `README.txt`: built glob preference, explicit data-root support, and refresh when the glob file changes.
- `lv_globs.py`, `lv_dressing.py`, `test_dressing.py`, and the eight dressing pin files: prefab production, placement, validation, and six-artifact measurement provenance.

Douglas's CLAUDE.md remains untouched. Main's line 77 starts “The five merged artifacts under `shared/build/`” and lists the original five files. That line needs a sixth-artifact update. No other line there contains “five”.

## Dressing API and exclusions

`Site(mapnum, items, shapes, seed)` copies the supplied records, expands globs, derives ground, and reads quest bands, map pins, shot windows, and their FLOORS. Placement checks use 32-unit cells and full item footprints. Sprite bounds supplement projected box bounds for shot checks, with the required 16-pixel margin.

- `swap_chunks(plain=..., family=..., share=..., where=...)` returns changed eggs with zero additional records. Only plain flat-floor eggs with no other raw record in the chunk qualify. A family needs at least four members; accepted shares stay at or below 25% per member. Three identical cardinal neighbours are refused. Solid-bearing chunks keep their whole footprint outside leg bands.
- `clusters(kit=..., per100=..., where=..., floors=..., anchor=...)` returns added records. Seeds stay 448 units apart. Groups contain two to five pieces, with offsets on the 32-unit lattice within 160 units. Groups of three or more mix shapes; each member has a neighbour within 128 units. At least 60% of accepted seeds have an anchor. Exclusions can reduce the requested density.
- `reserve(name, footprint)` protects a builder's set-piece footprint before surrounding dressing. `set_piece(name, pieces)` validates hand-authored records and reserves their resulting footprint. A matching reservation permits its own named piece; other reservations remain protected. `loosen_rows(pieces, mapnum, seed, broken=...)` supplies hashed offsets and one fallen variant in four for generated legacy rows. Unknown fallen variants require an explicit mapping. Set-piece records retain their hand-authored coordinates.
- `beyond(kind, where=..., z=0)` covers wholly void chunks within view with prefab eggs, or four black plates per chunk for `dark`. Kinds are `dark`, `stars`, `lava`, `water`, `shore`, `rock`, and `forest`. Whole chunks containing existing painted ground are retained. Existing black plates can become one egg. Backdrop choices also reject three identical cardinal neighbours; blocked chunks remain available to the final void-floor fallback. Optional z supplies a rim height.
- `pack()` returns final records, persists packed rows and dressing provenance, and enforces raw and expanded caps. Loose ground and added dressing must have odd coordinates, zero quality, zero flags, zero NPC, map, and link metadata, and no pin or shot ownership. Containers, quality-family items, and eggs retain FIXED records. Map 39's 4,623 retail records remain an exact prefix through substitution, backdrop replacement, and packing.
- `report()` returns per-region measurements, target failures, and the operation ledger.

Exclusions protect pinned items by 96 units, teleport pads by at least 128 units, decoded egg hatch boxes, movable clear boxes and reach space, anti-climb walls by 32 units, quest bands with a 64-unit margin, TRACKS, FIRE_LINES with LAVA_MARGIN, monster boxes, VALLEY_CLEAR, the Map 18 breach and entry lane, and tall pieces near scripted points on the south and east sides. Solid overlaps, solid top faces, small flat pieces near tall solids, and unsuitable flat overlay flags are refused. LAND and SOLID props require the 4-unit height lattice and an exact-reach check that finds no new reachable standing top. Cluster kits fall back to non-land pebbles when a selected piece fails these checks.

A future map slice could write this after geometry and quest content, before void fill:

```python
site = lv_dressing.Site(9, items, shapes, seed=4009)
site.reserve('collapsed arch', (13200, 13800, 13600, 14200))
site.swap_chunks(plain=397, family=lv_dressing.ROCK_FUNGUS,
                 share=0.40, where=HALL)
site.clusters(kit=lv_dressing.KIT_BONES, per100=4.0,
              where=HALL, floors={301}, anchor='wall')
site.set_piece('collapsed arch', authored_arch)
items = site.pack()
items += lv_furnish.void_floor(items, shapes)
```

The example's box and authored records belong to that map slice and must satisfy its exclusions. D1's set pieces remain builder work. `lv_furnish.py`, `lv_landscape.py`, and `lv_cave_vignette.py` remain unchanged. Their existing emission paths continue until the owning map slices replace them.

## Pins and budgets

Each map has one JSON file under `dressing_pins/`. Pins cover every available RATCHET value for every region, the whole map, and the budget measurement area. `props.props_per_100` and `ground.seam_density` join RATCHET because TARGETS uses them. Recording refuses weaker bounds. Allowances require a region, metric, bound, and reason; none were added.

| Map | Regions | Current regional target failures | Raw records | Expanded records |
|---|---:|---:|---:|---:|
| 8 | 2 | 5 | 5923 | 29243 |
| 9 | 3 | 3 | 1226 | 1556 |
| 10 | 12 | 56 | 21864 | 48204 |
| 11 | 8 | 34 | 10065 | 18375 |
| 13 | 3 | 10 | 6298 | 9643 |
| 17 | 6 | 0 | 9284 | 9284 |
| 18 | 4 | 10 | 2388 | 3168 |
| 39 | 1 | 0 | 5085 | 30065 |

The baseline totals 39 regions and 118 regional target failures. Default runs preserve today's measurements. Strict runs add all regional TARGETS, the whole-map targets from section 4.2, and the raw phase-exit ceilings. The measured strict run reports 137 failures: 118 regional targets, 17 whole-map targets, and the raw exit ceilings for Maps 10 and 11.

`build_all_maps.py` retains RECORD_BUDGET as the hard raw cap and the 31,000 expanded caps for Maps 8 and 39. It also checks section 4.2's expanded-per-ground-cell limits before saving FIXED. Raw phase-exit ceilings remain separate because today's Maps 10 and 11 already exceed them. The budget area is `(3072,1024,22528,30208)` for Map 10 and the city box `(1664,1024,6912,11264)` for Map 17; the other limits use whole maps. Exact measurements and six hashes travel in each pin file.

The permanent structural audit expands built dressing eggs and provenance records. It checks cardinal prefab runs, props with footprints of at least 64 units in quest bands, and painting into shot windows. Untouched historical records retain their existing visual-quality ratchets.

## Verification and review

`tools/run_all_tests.sh` completed with 57 of 58 test files passing. The sole failure is the allowed `test_integration_state.py` shared-install check: `STATIC/GLOB.FLX != canonical GLOB.FLX`. The worktree's `shared/data/u8-install` is a symlink to main's installed game. That STATIC/GLOB.FLX is retail and has 3,072 slots; the private built archive has 3,132. Installation would write through that symlink and change main's shared data, so it was left untouched as instructed. The test reports nine assertions passed, one failed, and four skipped because this worktree has no ScummVM tree, binary, or harness directory.

The estate passed dressing, visual quality, all 39 vignette checks, all 76 paint-cycle checks, all 166 route-reach checks, all 60 hygiene checks, geometry, map pins, and round trips. Logs are in `/tmp/lv-tests.tDa1s6`; the captured summary is `/tmp/lv-vq4-estate.log`. The final targeted dressing run after the set-piece identity and backdrop adjacency controls also passed: `dressing: 0 failures; 118 target failures`. Strict mode's 137 phase-exit failures are expected baseline debt and were run separately.

The permanent test includes negative controls for FLX empty slots, retail slot preservation, immutable payload hashes, malformed coordinates, asymmetric hatch ranges, the updated retail-shore exclusion, retail-prefix preservation, compiler manifest round trips, packed-row deduplication, appended authored IDs after packed IDs, zero-record substitution, caller-list ownership, reservations, leg bands, exact-reach standing levels, symmetric self-overlap rejection, authored prefab placement, ordered packing, quality preservation, row variation, archive-free measurement, hand-authored set-piece identity, backdrop substitution, mixed anchored clusters on the 32-unit lattice, and ratchet direction.

Real Site construction on Maps 9, 11, and 18 loaded the expected shot and leg contracts successfully. Their measured construction times were 0.29 s, 3.74 s, and 0.41 s. Shell syntax checks passed for the build, integration, and installer scripts. Compilation succeeded for 55 of 57 sources; EALOGO and TJORVI remain the two documented allowlist failures. `tools/build_artifacts.sh --verify` then matched all six canonical hashes.

The initial `codex exec review --base main` could not inspect files because bubblewrap failed with `Failed RTM_NEWADDR: Operation not permitted`. The unrestricted rerun found a P1 fresh-clone failure: pre-save metrics opened the absent built FIXED.DAT. Archive-free construction fixes it; a full build starting without FIXED passed. A later review identified required untracked modules absent from its patch view; explicit staging included the modules, tests, and pins.

Independent verifier findings corrected before completion:

- Zero-height ground triggered prefab self-overlap rejection. Pair checks now preserve ground support and reject positive-height collisions symmetrically. The same check protects an existing nonsolid prop from a newly placed solid; a set-piece regression covers that insertion order.
- New authored rows collided with packed IDs. Allocation now follows all existing manifest IDs.
- Nonsolid brush escaped the leg-band check. Full-footprint prop checks now match the structural audit.
- Several first-draft prefab layouts collided internally. Corrected layouts pass the shared validator. Barren debris uses non-land pieces; low standable bones remain kit candidates subject to exact reach and fallback.
- Whole-map targets and two target metrics were absent from the ratchet. Strict map targets and complete target-metric pins now cover them.
- Substitution rebuilt the whole safety index for every attempt. Incremental accepted-piece indexing preserves collision checks; full refresh occurs at operation boundaries.

The independent verifier's final dressing run also passed with zero failures and all 118 baseline target debts. The staged follow-up review found no actionable defects. The complete-patch review then found a P2 asymmetric egg-range defect: the high NPC nibble belongs to x, and the low nibble belongs to y. The decoder now follows those axes. A regression check protects a point 240 units east of an `0x82` egg and verifies that the corresponding point south is outside its hatch mask. A subsequent review found a P2 global no-burial defect: a new solid could overlap an existing nonsolid prop. The guard now checks either participant's solidity; the final regression rejects that set piece. Its independent dressing and map-hygiene checks passed; its integration-state check identified the unchanged shared install's retail GLOB.FLX.

## Boundaries and remaining work

Main's concurrent `cc50402` direction update excludes retail river-shore globs 1537 through 1554 on Maps 10 and 13. Both direct substitution and `beyond('shore')` now reject those globs on those maps. Placement also rejects their excluded shape-301 bank-floor frames six through 37. Existing records remain unchanged. Some mixed-earth prefab variants are therefore available only outside those maps; clean variants can be appended with future map work. The names SHORE_SE and SHORE_NW retain the retail families for other maps. The updated direction requires Map 13's 640x400 cliff-shore mock and Douglas's sign-off before shore building; that deliverable belongs to the Map 13 slice. Approved LV cliff-shore rows can then be appended through the shared-module change process. No shoreline art or builder work was added here. `python3 agents/map-populator/src/test_dressing.py` passed after these guards, with zero failures and the same 118 baseline target debts; evidence is `/tmp/lv-vq4-dressing-shore-guard.log`.

Map dressing, visual retours, and hand-authored regional set pieces belong to later slices. No visual pin or shot floor changed. Bone and rubble candidates that create reachable LAND tops use the kit's non-land alternative; the module preserves the standing-level rule. Exclusions can return fewer placements than the requested share or density, with the accepted counts exposed in the ledger.

The raw-ceiling conflict is present in the spec itself: FIXED must remain byte-identical while Maps 10 and 11 begin above their exit ceilings. Hard caps and expanded limits apply now; strict mode reports the two raw-ceiling debts until those map slices reduce records. No allowance hides them.

No ScummVM session, installation, merge, or push occurred. Game-data entries are symlinks to main; shared/build is a private copy. Main's pre-existing CLAUDE.md, settings, agent files, screenshots, and other untracked files remain untouched. The feedback page read “Nothing open” at entry and again before completion.
