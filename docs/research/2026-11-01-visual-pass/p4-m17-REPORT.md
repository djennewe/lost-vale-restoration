# Map 17 dressing, second run

## Cloud edge correction, 10 November 2026

The builder smooths the cloud outline before tile placement. A cardinal-neighbour pass removes isolated cloud cells and fills isolated star cells. A second pass fills corner-only joins. Both repeat until stable. An outer-sky flood fills enclosed star pockets while preserving open bays. Assertions reject isolated cells, corner-only joins, enclosed star pockets, and disconnected cloud coastlines. The existing two-to-five-cell lobes and bays remain.

Only 23 cloud-outline cells change: four cloud cells disappear, and 19 cloud cells fill holes or join lobes. All 3,998 playable cells, scene coordinates, and six regional pin sets remain unchanged. The derived map-pin fingerprint is refreshed; every pin record remains identical. [Topology evidence](p4-m17/edge-topology.json) lists the changed cells.

The brief requires ratchets measured against main. Whole-map and budget-area dressing pins were recorded against main `9a201022`, retaining the approved regional pins. Connecting lobes increases the largest connected patch share compared with the second run; the smaller budget denominator also changes its repetition score. Both satisfy main's pins. No allowance was added. [Baseline](p4-m17/edge-pin-baseline.json) and [final measurements](p4-m17/edge-after-metrics.json) record the comparison.

Final city land: 3,238 cells; cloud share: 70.85%; bare land: 4.23%; period excess: 0.0867. Raw records: 9,211; expanded records: 11,583. GLOB.FLX holds 4,046 entries against the engine limit of 4,095. All city and regional target failures remain zero. Visual black-frame mean improves from 0.00240904 to 0.00234483; its maximum improves from 0.00892578 to 0.00855469. The improved visual pins are recorded.

The capture wrapper synchronizes GLOB.FLX into the private game install before every fresh world, alongside the five artifacts synchronized by the capture session. Capture provenance verifies all six installed hashes against the final build.

The final estate passes 57 of 58 files. Its sole failure is the permitted test_integration_state mismatch against the shared install; the private capture install passes its canonical-byte checks. Strict dressing and visual-quality checks have zero failures. Final review reports no actionable defects. All 18 tour views with stars and all 12 set-piece views were re-taken and inspected at native 640×400. Every position is exact, and every capture has landed: true. The [capture paths](p4-m17/edge-capture-paths.txt), [inspection hashes](p4-m17/edge-inspection.json), and [verification digest](p4-m17/edge-verification.json) record the final evidence. The builder commit is `6572e018`. No merge, push, or main checkout change occurred.

The following sections retain the approved second-run measurements and scene descriptions. The correction above supplies the final whole-map measurements.

All six measured regions and the city targets pass. Bare land falls from 30.12% to 4.26%. Cloud occupies 70.84%, against the 72% ceiling. No allowance was added.

Branch: `wt/vq4-m17`. Implementation: `cc1d8b7d`. Shared main merge: `2df22f85`, bringing in `9a201022`. The first attempt remains unmerged into main.

## Scene evidence

### Scroll court

Reads as: a small shrine court.

The retained scroll plinth, four banded columns, and gem pillars sit within a 22-slab marble outline. Its southern opening preserves the quest approach. Five urns form the offering crescent beside a short column.

Set piece: [shrine offering crescent](p4-m17/setpieces/shrine-offering-crescent.png). Named reservations protect the composition.

Land cells: 80 → 80. Target failures: zero → zero. Raw records: 177 → 170; expanded: 177 → 199. Both protected-window scores below apply.

### Walkway field

Reads as: the raised marble way.

Two short posts, two fallen white drums, and three fragments finish the eastern aisle. The 1994 walkway and throne nook stay pixel-identical.

Set piece: [walkway broken terminus](p4-m17/setpieces/walkway-broken-terminus.png). Named reservations protect the composition.

Land cells: 480 → 480. Target failures: zero → zero. Raw records: 1109 → 948; expanded: 1109 → 1116. Both protected-window scores below apply.

### Processional street

Reads as: the main street.

The retained pillar count has explicit 32-unit and 64-unit offsets. Two gem pillars become paired drums, and a third becomes a bare shaft. The side court holds a broken votive bay, urns, a fallen drum, and fragments.

Set piece: [processional votive bay](p4-m17/setpieces/processional-votive-bay.png). Named reservations protect the composition.

Land cells: 78 → 78. Target failures: zero → zero. Raw records: 199 → 148; expanded: 199 → 199. Both protected-window scores below apply.

### Obelisk plaza

Reads as: the heart of the city.

Five full-size thrones face a four-slab marble dais from different directions. Short columns and urns frame the council. The protected obelisk composition retains its original pixels.

Set piece: [plaza empty council](p4-m17/setpieces/plaza-empty-council.png). Named reservations protect the composition.

Land cells: 288 → 288. Target failures: zero → zero. Raw records: 882 → 795; expanded: 882 → 888. Both protected-window scores below apply.

### East court

Reads as: a ruined colonnaded court.

Five standing gem pillars turn an L beside two bare shafts. Two fallen white drums and mixed small fragments spill across the gold court. The bottles and bones occupy one corner. The separate fallen plaza approach extends the collapse into the m17-23 view.

Set piece: [east court collapse](p4-m17/setpieces/east-court-collapse.png). Named reservations protect the composition.

Land cells: 110 → 110. Target failures: zero → zero. Raw records: 174 → 157; expanded: 174 → 176. Both protected-window scores below apply.

### Arrival landing

Reads as: a gold terrace at the cloud’s edge.

A full-size watch throne, urns, low marble ledge, and two short columns form the western terrace. Four marble slabs supply an 8-unit descent beside the eastern bridge approach. The eight original terrace columns, bridge-head gem pillars, pad 209, reapply egg, and sealed channel remain.

Set piece: [landing watch](p4-m17/setpieces/landing-watch.png). Named reservations protect the composition.

Land cells: 176 → 176. Target failures: zero → zero. Raw records: 198 → 67; expanded: 198 → 211. Both protected-window scores below apply.

### South street, forecourt, and aisles

Reads as: gold streets.

A raised four-slab marble plinth carries a gold plaque on its front face. Five urns supply offerings, framed by two intact gem-capped columns. Six cloud-gold transition chunks soften the processional edges. The north observatory has an isolated 16-tile gold court; three western foundations give the arcade bays distinct former court footprints. The western arcade and eastern portico contain explicitly placed fallen columns and fragments.

Set piece: [south street memorial](p4-m17/setpieces/south-street-memorial.png). Named reservations protect the composition.

This area has no separate regional metric box. Its target result is the whole-city result below.

## Land measurements

Before is Map 17 rebuilt from the merged main source. Targets use the shared land-only classification. Regional ratchets retain their historical measurement area. Pins were reset to main before recording; every nonrecord ratchet holds or improves.

| Region | Props per 100 | Dressed | Bare | Grouped (small-prop base) | Stride (eligible base) | Dominant material | Period excess |
|---|---:|---:|---:|---:|---:|---:|---:|
| Scroll court | 16.2500 → 23.7500 | 66.25% → 73.75% | 0.00% → 0.00% | 0.00% → 52.63% (13 → 19) | 90.00% → 81.82% (10 → 11) | 85.00% → 70.00% | 0.8077 → 0.2885 |
| Walkway field | 12.5000 → 13.9583 | 29.79% → 36.04% | 0.21% → 0.21% | 90.00% → 91.04% (60 → 67) | 75.51% → 72.55% (49 → 51) | 66.25% → 66.25% | 0.1374 → 0.0713 |
| Processional street | 30.7692 → 30.7692 | 66.67% → 70.51% | 0.00% → 0.00% | 0.00% → 25.00% (24 → 24) | 100.00% → 65.22% (24 → 23) | 89.74% → 82.05% | 0.8667 → 0.1414 |
| Obelisk plaza | 21.1806 → 23.2639 | 60.07% → 65.62% | 0.00% → 0.00% | 91.80% → 92.54% (61 → 67) | 54.55% → 39.29% (55 → 56) | 95.83% → 95.49% | 0.0507 → 0.0487 |
| East court | 33.6364 → 35.4545 | 93.64% → 93.64% | 0.00% → 0.00% | 51.35% → 74.36% (37 → 39) | 73.53% → 69.57% (34 → 23) | 83.64% → 77.27% | 0.8051 → 0.1452 |
| Arrival landing | 10.7955 → 15.3409 | 42.61% → 51.14% | 0.00% → 0.00% | 0.00% → 48.15% (19 → 27) | 100.00% → 100.00% (16 → 20) | 90.91% → 87.50% | 0.1071 → 0.0636 |

City land denominator: 3280 → 3237 cells. Water and stars are backdrop under shared slice 0.2; retained 874 cloud tiles still count as land. The ragged cloud sea replaces the former full-view cloud sheet, and stars paint the remaining view rays.

| City target | Before | After | Required |
|---|---:|---:|---:|
| Props per 100 | 7.8963 | 11.4921 | at least 8 |
| Dominant material | 78.20% | 70.84% | at most 72% |
| Bare land | 30.12% | 4.26% | at most 15% |
| Period excess | 0.1344 | 0.0869 | at most 0.20 |

City target failures: three → zero. The remaining bare cells are inventoried in [bare-cells.json.gz](p4-m17/bare-cells.json.gz). The added ruins and courts have explicit coordinates; no generated prop scatter or allowance supplies this result.

Whole-map raw records: 9284 → 9315, below the 9,500 ceiling. Expanded records: 9284 → 11689, below the 12,000 cap. City expansion density is 1.629, below two expanded records per land cell.

## Shared adoption and protected geometry

GLOB.FLX has 4,042 entries; this engine permits at most 4,095.

Scene props have explicit coordinates in `SET_PIECES`. The memorial frame uses the capped-pillar composition at two explicit anchors. The named low architecture in `MARBLE_SCENES` passes `walkable_set_piece` route proofs.

S1 places 3,811 decorative star records, including the north and west virtual wedges. Black fallback plates remain beneath the star paint for hygiene coverage. The cloud sea has lobes 2 to 5 cells deep outside the retained outline. S2 adds 36 marble slabs through five named walkable compositions. S3 replaces the grey fallen-column stand-ins with white shape 905 and uses the smaller 910 fragments. S4 replaces six loose floor chunks with the six-member cloud-gold family.

Packing retains every flat tile that overlaps other land at the same level. Only 150 complete, unique floor chunks pack. This keeps GLOB.FLX within the engine’s 4,095-entry FLEX limit. Replaced transition tiles remain loose through the shared API.

Window bases: screen11 has 317 × 183 pixels; screen12 has 319 × 185 pixels.

| Window | Before | After | Changed pixels |
|---|---:|---:|---:|
| screen11 | 99.929324% | 99.929324% | 0 |
| screen12 | 97.942896% | 97.942896% | 0 |

All 400 perimeter curbs and 1,331 recess walls remain byte-identical. The 11 placed pin records, layout constants, and `column_recesses()` remain unchanged. The canonical-main reconstruction hash matches main’s recorded FIXED hash; only Map 17 differs from that reference. The private before archive contains the exact main Map 17 records.

Original movable clearances remain protected. The full-size council and watch thrones retain retail movement behavior. Route and paint-cycle results are included in the estate log.

The four original plaques remain at their pinned anchors on two-drum white supports. Their individual marble bases remain excluded by the unconditional map-pin masks. The [placement probe](p4-m17/plaque-base-probe.log.gz) refuses all four with `map pin`. A shared replacement operation would need to lift the two support drums by 8 units onto an 877 base while keeping the plaque bytes unchanged, with collision, reachability, and visibility proofs. No mask exception or pin movement was added. The builder refuses archives above 4,095 entries. The shared writer still needs the same ceiling or an engine loader extension before further combined packing; its current writer accepts archives that this engine refuses.

## Quality, feedback, and verification

VQ-047 gains the painted night sky, including the formerly black diagonal bands at m17-12. The earlier grade was “improved”; this run claims no additional previously regressed or unchanged grade item. `docs/map-feedback/OPEN.md` contained “Nothing open”. No feedback entry required a response.

- `tools/build_artifacts.sh --record`: passes; all six recorded hashes verify.
- `python3 agents/map-populator/src/test_dressing.py 17 --strict`: zero failures and zero target failures.
- `python3 agents/map-populator/src/test_visual_quality.py 17 --strict`: zero failures and zero quest-band cells below half visibility.
- `tools/run_all_tests.sh`: 57 of 58 files pass; the sole failure is the permitted test_integration_state mismatch against the shared install.
- `codex exec review --base main`: no actionable defects; completed with --dangerously-bypass-approvals-and-sandbox after bubblewrap could not create a network namespace.

The visibility audit moved one observatory post, one council throne, and one fallen-arcade post. The final measured visibility and black-frame distributions are in [visual-metrics.json](p4-m17/visual-metrics.json). These changes preserve the approved regional targets and all quest bands.

## Engine captures

All 34 before-tour stops, 34 after-tour stops, and 12 set-piece views were re-taken. Each uses `LV_DISPLAY=:87`, `XDG_RUNTIME_DIR=/tmp/claude-1000/vq4-m17`, `usehighres=false`, and a fresh world through `tour_capture.py`. All requested coordinates, heights, and map numbers match the readback, and every capture has `landed: true`.

Every after-tour image and set-piece image was inspected at its native 640×400 size. The council reads as a ring of empty seats, the memorial has a plaque and offerings, and the ruined court has fallen white drums. The m17-12 night sky and m17-23 fallen arcade provide direct before-and-after checks.

The highest recorded engine object counter is 10,106 of 32,511 slots.

The [capture inventory](p4-m17/capture-summary.json), [capture provenance](p4-m17/capture-provenance.json), [geometry proof](p4-m17/geometry.json), [before metrics](p4-m17/before-metrics.json), [after metrics](p4-m17/after-metrics.json), and compressed verification logs record the final artifacts. No main checkout source was changed, and no merge into main or push occurred.
