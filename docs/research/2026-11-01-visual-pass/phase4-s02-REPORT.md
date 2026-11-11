# Phase 4 shared slice 0.2

Shared dressing APIs and decorative art are implemented on `wt/vq4-s02`,
from main `c6e4847e`. Map builders remain unchanged. Adoption belongs to
Map 17's second run, Map 11's second run, and Map 10. No ScummVM session,
installation, merge, push, or main-checkout write occurred.

## Requests 1 and 5: land area and painted stars

347 water and 351 stars are classified as void/backdrop. Land-only metrics
now determine targets and whole-map budgets. Map 13's density becomes
6.368978 props per 100 cells, from 3.786503; bare share becomes 0.091422,
from 0.285455. Both whole-map targets pass under the stated land policy.
No geometry or dressing record changed to produce those improvements.

```python
metrics = dressing_metrics.measure(source, 13)
```

The changed measurement areas are:

| Map | Area | Previous cells | Land cells |
|---|---|---:|---:|
| 8 | whole | 18204 | 15271 |
| 8 | budget | 18204 | 15271 |
| 10 | whole | 39476 | 30998 |
| 10 | budget | 31972 | 27191 |
| 13 | whole | 7157 | 4255 |
| 13 | budget | 7157 | 4255 |
| 39 | whole | 16814 | 15992 |
| 39 | budget | 16814 | 15992 |

Maps 9, 11, 17, and 18 retain their whole-map and budget values.
Regional pins retain their original measurement area through the explicit
`legacy_area=True` regression comparison. Regional targets use land-only
measurements. This preserves the requested whole-map and budget-only pin
scope while continuing to detect regressions against the recorded regional
bounds. Regional pin fields, allowances, provenance hashes, and recorded
target-failure inventories remain unchanged. The area correction exposes
regional target debt under the new measurement, which later map runs must
address. Water anchoring in `clusters` uses a separate water-cell index.

Cloud-class frame-black measurements now exempt pixels whose final painted
owner is star shape 351. Unpainted pixels and black props over stars still
count as black. Both reference frames and cached camera atlases use the same
owner-based rule. Atlas validation also compares owner-derived coverage,
so equal black RGB pixels cannot hide a black prop behind a sky exemption.
Other map classes retain their previous rule. Main's
Map 17 contains no star records, so this rule changes no existing visual
pin value. No visual pin is re-recorded.

## Requests 2 and 5: north star wedges

The opt-in cell path fills negative-coordinate view rays with decorative
star copies anchored in visible ground chunks at z zero. Shapes 916 through
928 provide 337 anchor layouts, with at most 28 nine-frame layouts per shape
because FIXED stores each frame in one byte. The sprite anchors compensate
projection and C-division rounding while preserving every source pixel.
All copies have LAND and SOLID clear and supply no standing surface.

The selector covers the viewing camera lattice with engine-visible anchors
for both 320-by-200 and 640-by-400 viewports. Sky records precede retained
floors and stay loose through `pack()`, preserving cloud lobes and actor
paint. Map 39 retains its mandatory retail prefix before added sky records,
with a dedicated regression. The north and west wedges are included when the supplied box reaches
zero. Physical coordinates remain valid positive world coordinates.

```python
site.beyond('stars', where=NORTH_CLOUD, partial=True, north=True)
```

Existing whole-chunk calls retain their behavior so FIXED.DAT stays
byte-identical. The Map 13 and Map 17 owners adopt the new path in their
builders, replacing their north black fallback at that point. The shared
negative controls require a visible negative-y star plane with valid
unsigned coordinates and preserve window and mask exclusions. A rendered regression compares the resulting sky with the complete virtual
negative-coordinate field and requires zero missing painted wedge pixels.
A second call adds zero records. The selection also accounts for retained
cloud surface height. A 162-case camera audit reports zero pixels lost to
engine chunk filtering. A full Map 13 probe adds 1248 records, reaching
12250 expanded records on 4255 land cells, or 2.878966 against the 2.9 cap.
The old north fallback remains in that conservative budget probe; its
replacement belongs to the owning map run.

## Request 3: protected wall sprites

`paint_only(..., replaces=walls)` retains every original wall record and
adds a collision-free skin. Shape 915 retains retail 15's exact silhouettes
and anchors, filling its opaque pixels with stone from 125 frame 12.
The original shape-15 records continue to supply all collision. There is
no blanket VALLEY_CLEAR exception for ordinary props.

```python
walls = [i for i in site.items if i.shape == 15 and i.y == 10752]
skins = [MapItem.placed_item(i.x, i.y, i.z, 915, i.frame) for i in walls]
site.paint_only('valley rock wall', skins, replaces=walls)
```

A skin must conceal every original wall pixel in the final built-painter
render. It preserves every nearby walking pose throughout the retained
32-unit arrival flood and all quest bands, checking both actor insertion
orders for ambiguous dependencies. Shot windows, pins, hatch boxes,
movable clearances, other reservations, and paint cycles remain protected.
The positive control retains a real shape-15 collision record byte for byte;
negative controls reject uncovered wall pixels and reduced Avatar visibility.
A full-map probe accepts all six skins in 166.52 seconds and preserves every
original Map 13 record byte for byte. The stone skin keeps the wall silhouette,
so it can replace its brick paint
without introducing an overhanging crest silhouette.

## Request 4: crest standing surfaces

Non-standing props can rest on a retained 125 top when their full footprint
fits the cap and the retained arrival flood already reaches that height.
Buried props, unreachable caps, furniture tops, and new standing surfaces
remain refused. The cached arrival flood is reset after site changes.

```python
site.place_prefab(956, x=chunk_x, y=chunk_y, z=crest_top_z)
```

The existing floor-support check uses the cap's top height. No cap record
changes and no new support is created. Synthetic controls cover a reached
eight-unit cap, a buried prop, and an inaccessible raised cap.

## Request 6: named walkable architecture

```python
site.walkable_set_piece('arrival marble descent', authored_slabs)
```

Every piece must have a LAND and SOLID top at most eight units above its
retained floor, on the four-unit lattice. Complete before-and-after
ExactReach models share an eight-unit XY lattice, original seeds, water and
hazard exclusions, and walk-off closure. Added reachability is confined to
the new tops and previously reachable positions at that height. Lost
reachability outside replaced floor footprints is also refused. Every top
must itself be reached.

A separate conservative climb72 guard refuses a new foothold within the
estate's two-tile envelope of an inaccessible raised standing top. Walking
ExactReach probes only zero-, four-, and eight-unit height offsets; this
guard covers the additional climbing risk without changing the route model.
Pins, shots, movables, hatch boxes, anti-climb margins, reservations, and
actual quest-band cells remain protected. A border may occupy the band's
margin only when it changes no actual leg cell. Generated dressing retains
the original standing-top refusal.

Controls accept a dais and a border beside a quest leg, refuse a step that
would assist climbing an 80-unit wall, and refuse a slab row that blocks a
retained passage under a lintel. The lintel control was added after review. A full Map 17 probe also accepts
the cited border slab at (2815,1151,0), using the original arrival seed, in
9.49 seconds.

## Request 7: fallen white drums and rubble

```python
site.place_prefab(lv_dressing.prefab_family('fallen_drum_')[0],
                  x=chunk_x, y=chunk_y)
# Hand-authored scenes can use shape 905 directly.
```

905 copies the screenshot white-column art, turns the cylinder onto its
side, and uses donor 465's decorative flags. It is a 47-by-16-pixel horizontal
drum. The contact sheet shows it lying across cloud floor beside small
white rubble. 910 copies all nine retail 526 frames, including six through
eight, and joins 899 in `KIT_HALL`. Existing 899 frames stay byte-identical.
`KIT_DECORATIVE` exposes the new decorative forms; the broken-column row
variant now resolves to 905.

Four prefabs append after every existing slot:

| Name | Slot | Contents |
|---|---:|---|
| fallen_drum_0 | 3871 | Cloud floor, fallen white drum, rubble 526:6 copy |
| fallen_drum_1 | 3872 | Cloud floor, fallen white drum, rubble 526:7 copy |
| fallen_drum_2 | 3873 | Cloud floor, fallen white drum, rubble 526:8 copy |
| fallen_drum_3 | 3874 | Cloud floor, fallen white drum, rubble 526:6 copy |

Their offsets differ. All earlier retail, authored, and packed slots remain
frozen. The archive has 3875 slots, with its first 3871 payloads preserved.

## Request 8: loose floor transitions

```python
site.swap_loose_chunks(floors={874, 876},
    family=lv_dressing.prefab_family('cloud_gold_'), share=.5, where=GOLD_EDGE)
```

Only complete 16-tile flat loose chunks qualify. Pins, metadata-bearing
records, glob-occupied chunks, shot windows, and the shared masks exclude
replacement. The replacement has the same coordinates, heights, support,
and painter flags as each removed tile. Each new tile occupies that tile's
original record position, preserving precedence with later same-height
floor records. Replaced tiles and overlapping same-height floor peers stay
loose through `pack()` because glob contents load after FIXED records. Four-family balancing and the cardinal-run rule apply.
Partial batches roll back atomically. Controls cover successful cloud-gold
replacement, pin and projected-window refusal, and a retained later cobble
overlay. No new cloud-gold prefab is needed.

## Request 9: invisible collision

`FLG_INVISIBLE` is 0x0010 and `FLG_EQUIPPED` is 0x0200. Invisible records now
remain in collision; contained and equipped records remain excluded.
`exact_reach.py` changes only these constants. A regression flood cannot
cross an invisible solid wall and can cross the same floor with the wall
removed.

```python
reach, seeded = ExactReach(items, shapes, roi).flood(seeds)
```

Before and after logs are byte-identical: route reach passes 166 assertions,
and paint cycles pass 76. No verdict changes. The latent flag defect has no
placed invisible FIXED record in the current LV maps to change those verdicts.

## Request 10: Map 11 shared paths

The Hub rectangle is removed from the unconditional dressing monster mask.
The other unconditional monster box, decoded egg hatch boxes, actual pins,
and quest bands remain protected. Monster-placement tests retain their Hub
constraint. The control checks both rectangles.

```python
site.beyond('deep_water', where=WATER_SEA)
site.beyond('lava', where=FIRE_OUTSIDE, partial=True)
site.beyond('rock', where=EARTH_OUTSIDE, z=96, family=(388,))
site.paint_only('corridor reliefs', [
    MapItem.placed_item(7167, 5183, 48, 913, 0),
    MapItem.placed_item(12799, 5183, 48, 913, 0),
    MapItem.placed_item(9503, 10751, 48, 912, 0),
])
site.paint_only('Air riser faces', authored_914_records)
site.basalt_shore('lake cold lip', [(cx, cy, oriented_frame)], z=0)
```

Plain deep water uses glob 262 alone, exempt from the cardinal-run rule in
placement and structural audit. It retains all masks and shot checks.
Partial surrounds accept lava's eight-unit ground tiles as well as flat
water and star tiles. They fill only genuinely void 128-unit cells, retaining rim
records and fallback plates. Structured tier 388 requires a complete chunk;
its internal supported contacts are validated as a compound prefab and a
local exact flood refuses newly reachable standing positions. Other
exclusions remain in force. Family overrides retain the supplied z.

Cells accept explicit frames so a complete contour can retain its authored
orientation in one atomic placement. Basalt uses decorative 911 on existing
cold 301, 4, or 386 cells adjacent
to lava. It retains lava and causeway bytes. Hot-side placement and dry
cold-side placement are refused. The paint-only API uses decorative relief
and clipped face rows, checks every quest pose, and supplies no collision or
leg-band walking change. The three cited corridor reliefs at z zero
actually hide walking-pose pixels, confirmed by the full painter comparison,
so those exact floor-level proposals remain refused. All three accept at
z 48 through the API above. A separate full arrival-flood painter comparison
confirms zero additional walking-pose occlusion at that height, preserving
every collision record and quest pose.
The map owner can adopt those upper-wall positions in the second run.

All new shape rows were allocated together:

| ID | Sprite recipe | Donor | Footpad |
|---|---|---:|---|
| 905 | White 875:0 turned horizontally | 465 | (3,2,1) |
| 906 | Roots 57, four frames | 465 | (6,5,2) |
| 907 | Fungus 65, 26 frames | 465 | (2,2,5) |
| 908 | Spires 66, 12 frames | 465 | (4,4,5) |
| 909 | Urn 229, one frame | 465 | (1,1,2) |
| 910 | Rubble 526, nine frames | 465 | (2,2,2) |
| 911 | Basalt 122, 30 frames | 465 | (4,4,1) |
| 912 | Relief 246, 10 frames | 465 | (1,4,5) |
| 913 | Relief 252, 10 frames | 465 | (4,1,5) |
| 914 | Face 26, 15 frames clipped to eight-unit riser | 465 | (4,1,1) |
| 915 | Wall 15 silhouettes textured with crest 125:12 | 465 | (4,1,5) |
| 916 through 928 | Nine star frames in 337 sprite-anchor layouts | 202 | (4,4,0) |

Every row is FIXED with LAND and SOLID clear, without a class or animation
entry. Shapes 916 through 928 add the shifted star copies on donor 202, with (4,4,0).
Conditional D8 cloud lobes would now take the next free ID, 929.

## Request 11 and adoption boundaries

Map 11's broken ritual crescent and wind-broken ring remain for its second
map run, together with adoption of the shared paths. No builder, protected
shot, map-pin item, or existing prefab payload is edited. Existing surround
calls keep their whole-chunk behavior; partial and virtual coverage require
explicit adoption. The main shared installation remains untouched.

## Pin migration inventory

Only whole-map, budget-area, and expanded-per-land-cell fields change.
The following table lists every re-recorded field. Each row follows the
water-and-stars backdrop classification; adjacency and repetition are
recomputed from the surviving land cells. The exact values and reasons are
also in [pin-changes.json](p4-s02/pin-changes.json).

| Map | Field | Previous | New |
|---|---|---|---|
| 8 | `whole.props.props_per_100` | min 8.146561195341683 | min 9.711217340056315 |
| 8 | `whole.ground.seam_density` | min 0.1354971518808866 | min 0.14740765842087428 |
| 8 | `whole.props.small_per_100` | min 6.092067677433531 | min 7.262130836225525 |
| 8 | `whole.props.dressed_share` | min 0.46401889694572623 | min 0.5349354986575863 |
| 8 | `whole.props.bare_share` | max 0.21462315974511095 | max 0.1571606312618689 |
| 8 | `whole.ground.top1` | max 0.26126126126126126 | max 0.3114399842839369 |
| 8 | `whole.ground.largest_patch` | max 0.25181278839815424 | max 0.3001768057101696 |
| 8 | `whole.repetition.modal_chunk` | max 0.19573283858998144 | max 0.24794359576968272 |
| 8 | `whole.repetition.period_excess` | max 0.2790272599629925 | max 0.2634666609261592 |
| 8 | `budget.props.props_per_100` | min 8.146561195341683 | min 9.711217340056315 |
| 8 | `budget.ground.seam_density` | min 0.1354971518808866 | min 0.14740765842087428 |
| 8 | `budget.props.small_per_100` | min 6.092067677433531 | min 7.262130836225525 |
| 8 | `budget.props.dressed_share` | min 0.46401889694572623 | min 0.5349354986575863 |
| 8 | `budget.props.bare_share` | max 0.21462315974511095 | max 0.1571606312618689 |
| 8 | `budget.ground.top1` | max 0.26126126126126126 | max 0.3114399842839369 |
| 8 | `budget.ground.largest_patch` | max 0.25181278839815424 | max 0.3001768057101696 |
| 8 | `budget.repetition.modal_chunk` | max 0.19573283858998144 | max 0.24794359576968272 |
| 8 | `budget.repetition.period_excess` | max 0.2790272599629925 | max 0.2634666609261592 |
| 8 | `expanded_per_ground_cell` | 1.609151834761591 | 1.9182109881474692 |
| 10 | `whole.props.props_per_100` | min 1.441382105583139 | min 1.8356022969223822 |
| 10 | `whole.ground.seam_density` | min 0.09974906696218172 | min 0.11262598258260217 |
| 10 | `whole.props.small_per_100` | min 1.2159286655182895 | min 1.5484869991612362 |
| 10 | `whole.props.dressed_share` | min 0.14968588509474112 | min 0.17965675204851925 |
| 10 | `whole.props.bare_share` | max 0.2930388083899078 | max 0.20775533905413252 |
| 10 | `whole.ground.top1` | max 0.5577566116121188 | max 0.7103038905735853 |
| 10 | `whole.ground.largest_patch` | max 0.25488904650927147 | max 0.32460158719917415 |
| 10 | `whole.repetition.modal_chunk` | max 0.28413284132841327 | max 0.37118371719335835 |
| 10 | `whole.repetition.period_excess` | max 0.2468597571772584 | max 0.2967856175489756 |
| 10 | `budget.props.props_per_100` | min 1.7796822219442012 | min 2.0926041704975913 |
| 10 | `budget.ground.seam_density` | min 0.10593640354327612 | min 0.11313108781322032 |
| 10 | `budget.props.small_per_100` | min 1.5013136494432628 | min 1.7652899856570188 |
| 10 | `budget.props.dressed_share` | min 0.14378205930188914 | min 0.16148725681291604 |
| 10 | `budget.props.bare_share` | max 0.25935193294132364 | max 0.21036372329079475 |
| 10 | `budget.ground.top1` | max 0.5905479794820467 | max 0.6943841712331286 |
| 10 | `budget.ground.largest_patch` | max 0.314712873764544 | max 0.3700489132433526 |
| 10 | `budget.repetition.modal_chunk` | max 0.30436966348568556 | max 0.36528028933092227 |
| 10 | `budget.repetition.period_excess` | max 0.272796454340694 | max 0.3120598561997708 |
| 10 | `expanded_per_ground_cell` | 1.193888402352058 | 1.403810084219043 |
| 13 | `whole.props.props_per_100` | min 3.7865027246052816 | min 6.3689776733254995 |
| 13 | `whole.ground.seam_density` | min 0.10855964737665293 | min 0.13399926909489585 |
| 13 | `whole.props.small_per_100` | min 2.0679055470169065 | min 3.4782608695652173 |
| 13 | `whole.props.dressed_share` | min 0.35419868660053094 | min 0.5565217391304348 |
| 13 | `whole.props.bare_share` | max 0.2854547994969959 | max 0.09142185663924794 |
| 13 | `whole.ground.top1` | max 0.30767081179265054 | max 0.3487661574618096 |
| 13 | `whole.ground.largest_patch` | max 0.29663266731870896 | max 0.3238542890716804 |
| 13 | `whole.repetition.modal_chunk` | max 0.2511415525114155 | max 0.06504065040650407 |
| 13 | `whole.repetition.period_excess` | max 0.1480693992948156 | max 0.1220625606715385 |
| 13 | `budget.props.props_per_100` | min 3.7865027246052816 | min 6.3689776733254995 |
| 13 | `budget.ground.seam_density` | min 0.10855964737665293 | min 0.13399926909489585 |
| 13 | `budget.props.small_per_100` | min 2.0679055470169065 | min 3.4782608695652173 |
| 13 | `budget.props.dressed_share` | min 0.35419868660053094 | min 0.5565217391304348 |
| 13 | `budget.props.bare_share` | max 0.2854547994969959 | max 0.09142185663924794 |
| 13 | `budget.ground.top1` | max 0.30767081179265054 | max 0.3487661574618096 |
| 13 | `budget.ground.largest_patch` | max 0.29663266731870896 | max 0.3238542890716804 |
| 13 | `budget.repetition.modal_chunk` | max 0.2511415525114155 | max 0.06504065040650407 |
| 13 | `budget.repetition.period_excess` | max 0.1480693992948156 | max 0.1220625606715385 |
| 13 | `expanded_per_ground_cell` | 1.5372362721810815 | 2.5856639247943596 |
| 39 | `whole.props.props_per_100` | min 21.98762935648864 | min 23.117808904452225 |
| 39 | `whole.ground.seam_density` | min 0.14336432289316123 | min 0.13703042285860068 |
| 39 | `whole.props.small_per_100` | min 18.79386225764244 | min 19.759879939969984 |
| 39 | `whole.props.dressed_share` | min 0.474961341739027 | min 0.48993246623311654 |
| 39 | `whole.props.bare_share` | max 0.10211728321636732 | max 0.11061780890445222 |
| 39 | `whole.ground.top1` | max 0.5846318544070418 | max 0.6146823411705853 |
| 39 | `whole.ground.largest_patch` | max 0.12578803378137265 | max 0.13225362681340672 |
| 39 | `whole.repetition.modal_chunk` | max 0.34990439770554493 | max 0.3948220064724919 |
| 39 | `whole.repetition.period_excess` | max 0.2782922607114753 | max 0.2880450945716344 |
| 39 | `budget.props.props_per_100` | min 21.98762935648864 | min 23.117808904452225 |
| 39 | `budget.ground.seam_density` | min 0.14336432289316123 | min 0.13703042285860068 |
| 39 | `budget.props.small_per_100` | min 18.79386225764244 | min 19.759879939969984 |
| 39 | `budget.props.dressed_share` | min 0.474961341739027 | min 0.48993246623311654 |
| 39 | `budget.props.bare_share` | max 0.10211728321636732 | max 0.11061780890445222 |
| 39 | `budget.ground.top1` | max 0.5846318544070418 | max 0.6146823411705853 |
| 39 | `budget.ground.largest_patch` | max 0.12578803378137265 | max 0.13225362681340672 |
| 39 | `budget.repetition.modal_chunk` | max 0.34990439770554493 | max 0.3948220064724919 |
| 39 | `budget.repetition.period_excess` | max 0.2782922607114753 | max 0.2880450945716344 |
| 39 | `expanded_per_ground_cell` | 1.7900559057927916 | 1.8820660330165082 |

## Artifacts, verification, and review

`tools/build_artifacts.sh --record` completed. FIXED.DAT remains
byte-identical to main. The first 3871 GLOB payloads remain byte-identical,
including all 3072 retail slots and every existing LV slot. Existing glob
pins and dressing provenance remain unchanged. The only GLOB additions are
the four rows above. Shape and TYPEFLAG entries outside 905 through 928
remain unchanged. ANIM.DAT and EUSECODE.FLX retain their original hashes.

| Artifact | SHA-256 |
|---|---|
| GLOB.FLX | `d497c16d965e780b9c9c072c361ce5218b6cb7f7d5d8c5c7ac297413d50b99b5` |
| FIXED.DAT | `e7ae4760fd273a34afa06e284d905bb1a41f45d947b135057dd28406eb1b51f2` |
| U8SHAPES.FLX | `0f80f38ddfbc28aac9148a65ec0c9cea201c84f0af177f1486c70a9e074f8bde` |
| TYPEFLAG.DAT | `568c4a4e8ea30b132b5e86d667f13f15c9238c8c32f0900d627db31e06f69db0` |
| ANIM.DAT | `97ae5fc9ddaa6ef515427103264a3095a6d42776ac51e530954fb4846b4d0443` |
| EUSECODE.FLX | `b47c324cdad77646c27755acfdd5bca53a9d92e16268db229f18e7dd780d4205` |

`test_dressing.py 13 --strict` reports zero failures, with the two retained
summit allowances. The whole-map density and bare-share failures are gone.
Art tests pass 1017 checks. Route reach passes 166, and paint cycles pass 76;
the before and after route and paint logs compare byte for byte.
`git diff --check` and the field-by-field pin boundary audit pass.
[identities.json](p4-s02/identities.json) records artifact and prefix checks.

`codex exec review --base main` in the default sandbox produced only the
bubblewrap namespace warning. The unrestricted reviews identified five
issues that were fixed:

- Low architecture could close a retained route beneath a lintel. The
  before-and-after proof now rejects lost reachability, with a regression.
- Crest checks on Maps 8 and 39 lacked arrival seeds. They now use their
  quest-leg seeds, with regressions for both maps.
- The north star plane left rays beyond the z-shift limit. Decorative
  sprite-anchor copies and rendered comparisons cover the complete wedge.
- Displaced stars could sit in engine-culled chunks. A greedy camera cover
  now anchors flat copies in visible ground chunks, with both viewport
  sizes checked. Sky copies stay before retained cloud paint through packing.

- Flat prefab members with a relative z offset could raise loose floors.
  Replacement now requires each expanded tile's height, footprint, and
  physics flags to match its removed tile. Regressions use retail 555, 577,
  585, and the larger 165 floor.

The final unrestricted review reports no actionable defects; its strict
Map 13 dressing, art, and diff checks pass. The separate route and paint
checks and the complete estate pass as recorded above.
`sha256sum -c ARTIFACTS.sha256` matches all six artifacts. The final targeted
strict run also covers owner agreement, floor heights and footprints, and
the retail-prefix guard.

`tools/run_all_tests.sh` completes with **57 of 58 files passing**. The
only failure is the permitted `test_integration_state` shared-install
comparison: installed U8SHAPES.FLX, TYPEFLAG.DAT, and GLOB.FLX differ from
the private canonical artifacts. Installation remains untouched. Dressing
reports zero failures and 65 regional target debts from the current land
measurements. Visual quality, all 39 vignette checks, all 76 paint-cycle
checks, all 166 route checks, map-pin freshness, and all 1017 art checks pass.

Evidence: [recorded build](p4-s02/build.log.gz),
[complete estate](p4-s02/estate.log.gz), [dressing](p4-s02/dressing.log.gz),
[strict Map 13](p4-s02/strict-map13.log.gz),
[visual quality](p4-s02/visual-quality.log.gz),
[completed review](p4-s02/review.log.gz),
[wall probe](p4-s02/wall-probe.log.gz),
[north budget probe](p4-s02/north-probe.log.gz),
[Map 17 border probe](p4-s02/walkable-probe.log.gz),
[Map 11 relief probe](p4-s02/panels-probe.log.gz),
[floor-level relief visibility](p4-s02/panel-visibility.log.gz),
[upper-wall relief visibility](p4-s02/panel-upper-visibility.log.gz), and
[162-case chunk audit](p4-s02/chunk-audit.log.gz).
The paired route and paint logs are retained as `route-before.log.gz`,
`route-after.log.gz`, `paint-before.log.gz`, and `paint-after.log.gz`.

Shared implementation is complete. Builder adoption, the later Map 11
scene work, and in-engine retours remain for the owning map runs under the
explicit scope of this slice. No requested shared API remains held.



The local PNGs contain Origin art and remain uncommitted:

- `p4-s02/donors.png`: retail donor study.
- `p4-s02/star-wedge.png`: north field over a retained cloud tile.
- `p4-s02/wall-skin.png`: retained brick and decorative rock paint.
- `p4-s02/fallen-drum-prefabs.png`: all four appended prefabs, rendered with
  `phase4/mock.py`'s `Stage.glob_sheet` against the private built archive.

The donor study and complete contact sheet were opened and inspected.
The drum reads as a toppled cylinder on the floor.
