# Independent screenshot-reconstruction review — AstraReview

## Verdict

**Do not integrate these assets/vignettes verbatim or describe the result as exact reconstruction yet.** This is strong archaeological/template-matching work, but a successful reconstruction of a photographed view is not independent recovery of complete sprites, physical geometry, or runtime behaviour.

| Area | Trust / 10 | Assessment |
|---|---:|---|
| Retail sprite identification and 2-D composition | **8** | Substantial real matches; three independently repainted saved renders reproduced byte-for-byte in RGB. |
| Published verification percentages as “exact share of shot pixels” | **4** | Mixed denominators, tolerances and treatment of missing actors; same-image extracted pixels dominate some scores. |
| Extracted art as production-ready game sprites | **4** | Palette encoding is excellent; completeness and segmentation are uneven. Some assets are clearly residual masks, not sprites. |
| Relative tier/layout reconstruction | **6** | Retail lattice/stacking evidence is useful; physically constrained solutions are better than unconstrained fits. |
| Absolute placement, forced pin moves, and integration readiness | **3** | Origins are design choices, several heights/hotspots are underdetermined, and full-engine conditions are not captured. |

**Scope:** read all five Recon reports, reconstruction document, relevant painter/decomposer/sorter code and four required vignette datasets; independently painted screen11, screen04, screen12 and Vale screen02. Inspected all 47 non-preview extracted PNGs, produced ×4 contact sheets and source-crop comparisons, and rendered current built shapes 860/861/862/865:2/870/872 through `shape_viewer`. No repository/artifact edits, builds, engine launches or test estate runs. All outputs are under `/tmp/lv-shots/review/AstraReview/`.

## Ranked findings

### B1 — Blocker: some proposed direct replacements contain scene/background pixels or missing surfaces

The proposed “feed the 1994 frames into builders” step is not safe as written (`docs/research/2026-10-16-screenshot-reconstruction.md:138–142`).

* **Fire pillar:** `shared/data/lv-1994-art/ReconInteriors/s07_fire_pillar.png` is a 31×91 crop with 1,525 opaque pixels. Every one matches source screen07 box **[170,60,201,151]**, but the lower-right portion, approximately sprite-local **x18–30,y70–90**, contains pit/wall material rather than a clean pillar silhouette. Source and extraction are shown in `s07_fire_pillar_source_pair_x4.png`. Its hotspot **(2,104)** is outside the image and explicitly chosen to land on the old pin (`screen07.json:1821–1833`); an out-of-image hotspot is legal, but this is not independent evidence of the pillar’s real base. Replacing 865:2 with it would transplant background scenery along with the column.
* **Doorway elder:** `art_s19_elder_draft.png`, source screen19 **[140,60,171,103]**, matches 819/819 opaque pixels but includes the red/brown doorway above the head and timber down the right edge. See `art_s19_elder_draft_source_pair_x4.png`; this would move with the actor.
* **Water Zombies:** s02_a includes isolated opaque pixels at local **(34,0)** and **(0,57)**, separate from its 658-pixel actor component. s09 includes a detached four-pixel patch inside **[0,40,3,43]**, separate from its 647-pixel main component. The s02_b mask has one connected 701-pixel component, but connectivity alone cannot certify its segmentation. These masks were defined as pixels not explained by the render, not recovered full actor silhouettes (`ReconVale-REPORT.md:137–150`, screen02 art notes).
* **Cloud f3/f4:** only **288/1024** and **481/1024** tile pixels exist. `screen11.json:994,1009` nevertheless says “completed from screen13.” The PNGs are still visibly partial wedges. Gold f1 has **1016/1024** pixels. These must not be distributed as complete repeating ground tiles.

**Required change:** separate observed pixels, inferred completion and unrelated residuals; clean sprite masks against source crops, complete hidden surfaces explicitly, and validate each frame on contrasting backgrounds and in motion before replacement.

### M1 — Major: §2 combines incompatible metrics and omits actor exclusions

The main report defines “Match” as share of shot pixels reproduced (`:44–45`). But:

* Vale excludes Water Zombie pixels (`ReconVale-REPORT.md:16–26`), including while showing them as red mismatches in the diff. `screen02.json.verify.note` says “ignore mask = actor pixels.”
* Cliffs counts unpainted black as background and uses RGB L1 ≤12 (`ReconCliffs-REPORT.md:18–23`).
* Interiors uses palette-class equality (`ReconInteriors-REPORT.md:8`), and the same scheme is used by the four-shot measurements here.
* Palette classes are a **transitive union**, not a bounded colour tolerance (`shot_decompose.py:61–74`). I measured 233 classes and a maximum within-class L1 diameter of **40**, in entries [174,175,220,221,222,223].

The four-shot strict-versus-lenient gap is generally small; the **missing-actor denominator** matters more. screen02 is **96.037%**, not 98.4%, when every shot pixel is counted. Excluding the 1,361 opaque pixels in the two delivered zombie masks yields **98.446%**. The original 98.37% therefore used a slightly different exclusion mask, which is not part of the published score contract.

**Required change:** publish one all-pixel strict score, one separately labelled tolerant score, explicit immutable masks for any diagnostic exclusions, and foreground/actor/region scores. Do not call a palette-class or exclusion-based score “exact.”

### M2 — Major: near-perfect numbers largely measure reinsertion of extracted source pixels

The score is not fabricated: independent Painter runs reproduce the published Cloud/Interiors render images exactly. Its interpretation is the problem.

* screen11: **92.681 percentage points** come from extracted art and only **7.261** from visible retail pixels. That is **92.74% of matched pixels** supplied by extracted material. Floor alone contributes 78.630 points; columns 13.466; sun half 0.584.
* screen04: **8.662 points** from five extracted objects, **91.252** from visible retail pixels. Source extraction explains almost the entire jump from the separately reported retail-only 91.4% to 99.91% (`ReconInteriors-REPORT.md:14–21`).
* screen12: **74.193 points** extracted versus **8.630** retail. However, this is not all same-shot copying: cloud/column reuse contributes **37.050 points**, while walkway/gold contributes **37.143 points**. Cross-shot reuse is genuine evidence and should be distinguished from source-shot reconstruction.
* screen02: the measured render uses **no extracted sprite pixels**; it has 96.037 retail match points and missing zombie poses.

Positive cross-shot evidence exists: independently searching complete cloud f0/f2 against screen13 found **1019/1024** and **1012/1024** agreement at crop origins **(72,96)** and **(40,48)**. That is more probative of reusable recovered art than pasting it back into screen11. These are best opaque-pixel overlaps, not a proof that every mismatch is contamination rather than occlusion.

**Required change:** distinguish retail-explained, independently cross-shot validated, same-shot reconstructed, inferred, and unresolved pixels; use leave-one-shot-out recovery where possible. Extracted art is a valid reconstruction tool, but its source-shot agreement is an in-sample fit.

### M3 — Major: “exact/recovered” overstates missing or inferred art

Main report `:31` says every 1994-only piece was extracted pixel for pixel; Interiors `:17` calls all exact shot pixels. Yet:

* Felicitar has **42 inferred pixels** filled from neighbouring rows/columns (`screen04.json` first art note). Independent source-crop comparison measures **1460/1502**, exactly 42 nonmatching opaque pixels, at screen04 **[111,29,144,82]**.
* Walkway has **34 inferred hidden rim pixels** and its right end face is never observed (`screen12.json:1313`).
* Sun half’s right edge is occluded; the eye half is explicitly a colour-keyed, rubble-occluded draft with **null hotspot** (`screen11.json` sun note; `screen12.json:1353–1355`).
* Wall spikes are ten separately cut, nonidentical masks; the vignette itself recommends drawing a single clean sprite from spike 6 (`screen07.json:1852–1860`).
* Foam, halo and pen beam are documented residuals with no proposed footprint (`ReconVale-REPORT.md:149–150`), not finished game shapes.

**Required change:** preserve per-pixel provenance/masks and per-frame completeness status. Unknown opaque pixels must not silently become transparent; inferred art must not be labelled recovered.

### M4 — Major: 2-D fit does not force the advertised world coordinates or pin moves

The projection has a null direction: adding **(128,128,32)** to an item preserves both projected coordinates exactly. Occlusion, support and known retail footprints constrain choices but do not eliminate all alternatives. An overall camera/world translation also leaves the image unchanged. I applied each of the four proposed world translations with the corresponding camera adjustment: **zero changed pixels** in all four. This establishes bookkeeping consistency, not evidence for those absolute origins.

Evidence of design-dependent choices is already present in the reports:

* Cloud screen12 origin is explicitly a proposal; the main report `:132–134` admits the relation between the two city views is extrapolated.
* Vale screen02 origin was searched to accommodate existing eggs/pins (`ReconVale-REPORT.md:174–179`), rather than recovered from the screenshot.
* Hrodny chest movement depends on a **hidden, inferred wall** (`ReconVillage-REPORT.md:96–98`).
* Map 9 association and dais-top heights remain inferred/unresolved (`ReconInteriors-REPORT.md:44–49`).
* Vale pen stair z has not been checked as a physical stack (`ReconVale-REPORT.md:101–102`); screen17’s physically consistent alternative deliberately sacrifices 0.6 match points (`:63–69`), an appropriate distinction.
* Cloud odd z is derived using an assumed hotspot; a one-pixel hotspot shift is observationally interchangeable with a one-unit z shift. Cliffs itself identifies this ambiguity for 796:0 (`ReconCliffs-REPORT.md:65–68`).

Thus “pin moves the shots force” (`main report:122`) should become “proposed integration moves given the selected origins/geometry.” Relative god spacing and removal of objects visibly intruding into a chosen camera frame are well motivated; absolute destination coordinates and route redesign are not uniquely dictated by the photographs.

**Required change:** mark recovered screen constraints separately from selected world solutions; document support/collision, reachability and alternate-solution reasoning; retain uncertain heights as unresolved until supported independently.

### M5 — Major: offline painter success is not full-engine equivalence

`vignette_paint.py:55–106` ports sorting and `:108–128` directly copies non-255 indices. It does not reproduce all `GameMapGump::PaintThis` state:

* Engine camera/roof cutoff (`game_map_gump.cpp:91–106,131–132`), fast chunks (`:116–123`), interpolation (`:128–129`), and invisibility handling (`:135–148`) are absent from Painter’s corresponding path.
* Extra shapes receive hard-coded flags, including `occl=False`, `trans=False`, `anim=False` (`vignette_paint.py:38–42`). Actual TYPEFLAG choices affect both sorting and appearance.
* Synthetic IDs (2000+/9000+) are not the final shipped shape IDs, and shape/frame IDs are sort tie breakers (`item_sorter.py:216–218`). **[INFERENCE]** Final-ID migration can alter ambiguous ordering; re-render after migration rather than assume equivalence.
* Frames, NPC poses and camera locations are frozen. **[INFERENCE]** NPC schedules/loiter, monster spawning, actor animation, animated water/fire, palette cycling/transforms and translucent effects can invalidate an otherwise identical map.
* Suppressing generated terrain only inside XY footprints (`main report:144–147`) does not exclude tall or overhanging sprites whose hotspots/footprints lie outside the window. They can still paint into the camera view. Roof cutoffs and global objects can likewise differ.

**Required change:** test the actual built window with **all potentially visible neighbouring items**, final shapes/TYPEFLAG/IDs and actual insertion ordering. The final engine fixture must pin camera, crop/scale, actor states/positions, frame tick, palette/effect state and UI/cursor policy. Do not treat the offline render as a substitute for that proof.

### M6 — Major: data contract is not yet unambiguous or sufficient for §5’s regression test

Cloud camera values are subtracted, whereas Interiors screen04 values are added. Cloud footprints use packed dimensions, e.g. **[4,4,0]**, while Interiors uses world-unit **[64,64,40]**; conversion is ×32 XY and ×8 Z (`item_sorter.py:230–239`). Interior item records require `render_id` overrides and sometimes nonnumeric art frame values; Cloud synthetic-shape registration is not specified as a single authoritative registry. One spike path still points into `/tmp` (`screen07.json:1852`).

The proposed FIXED.DAT-only test (`main report:151–155`) also cannot reproduce the current score without supplying separately listed actors/effects and camera/runtime state. A single whole-frame threshold allows a lost quest-critical object to be offset by improvements elsewhere and permanently accepts today’s unresolved 17–26% on some shots.

**Required change:** define one versioned replay manifest with explicit units/camera convention, complete shape/frame/flag registry, actors/effects and provenance masks; verify it against final artifacts. Preserve region-specific golden expectations, not only a global minimum percentage.

### Minor findings

* screen02 `_render.png` and `_diff.png` are byte-identical **2781×540** three-panel composites, not a raw render and a diff. Cloud/Interiors raw renders have native dimensions. The saved Vale middle panel differs from the independent JSON replay at **118 RGB pixels / 19 palette-class pixels**, with differences inside **[82,60,233,161]**. Its all-frame lenient score is **96.014%**, versus my **96.037%**. This is small, but should be resolved by a canonical replay script.
* The “native 320×18x” description is approximate: measured GIF sizes here are screen11 **317×183**, screen04 **320×185**, screen12 **319×185**, screen02 **309×180**. The engine fixture needs exact per-image crops, not a universal 320-wide assumption.
* Current built 860 dimensions are **36×124,96×71,54×124**, not the report’s approximate Felicitar “55×200” (`ReconInteriors-REPORT.md:19`). They are still materially larger than recovered **33×53,43×38,31×67**, so the visual conclusion stands; comparisons should identify the artifact being measured.

## Independent remeasurements

Strict: map each GIF RGB to nearest U8PAL by the same RGB-L1 method as `shot_decompose.load_shot`, then require identical palette **RGB** (duplicate palette-index aliases are equivalent). Lenient: `shot_decompose.CLS` equality. Both include the entire GIF, including missing actors; neither excludes inconvenient pixels. Unpainted output is black, but **none of these four scores gains a matched unpainted pixel**. Strict here is palette-normalized equality, not literal GIF-RGB equality.

| Shot | Claimed % | My strict % | My lenient % | Retail match points | Extracted match points |
|---|---:|---:|---:|---:|---:|
| screen11 | 99.9 | **99.921** | **99.941** | 7.261 | 92.681 |
| screen04 | 99.9 | **99.902** | **99.914** | 91.252 | 8.662 |
| screen12 | 82.8 | **82.489** | **82.823** | 8.630 | 74.193 |
| screen02 | 98.4 | **95.730** | **96.037** | 96.037 | 0.000 |

Attribution is the final visible owner of a matched pixel, not the counterfactual score of removing custom art. Extracted fractions of the lenient matched total are **92.74%, 8.67%, 89.58%, 0%**, respectively. Cross-shot reuse versus same-shot extraction is discussed in M2.

Black-class target fractions are only **1.119%,1.316%,2.186%,2.024%** respectively. Strict accuracy after excluding black targets is **99.956%,99.904%,82.871%,95.699%**: black pixels are not the cause of the headline Cloud/Interiors success. Other shots explicitly use background conventions that should nevertheless be standardized.

For independent painting I used `Painter`, registered extracted PNGs with supplied hotspots and inferred/declared footprint-unit conversions, applied Interior `render_id` overrides, and included all actors with a concrete frame. Cloud and Interior saved renders match my output **at every RGB pixel**. Raw statistics: `measurements.json`; renders: `screenNN_independent_x4.png`; strict diffs: `screenNN_strict_diff_x4.png`.

## Art verdicts

**Measured globally:** all **47** non-preview PNGs are indexed P-mode, contain the exact 256-entry U8PAL RGB palette, and declare transparent index **255**. This meets encoding expectations; it does not certify the masks. “Usable as-is” below means the visible static frame is a plausible integration candidate, **not** that animation, collision or full-engine validation is complete. File roots are `shared/data/lv-1994-art/<pass>/`.

| Piece | Verdict | Completeness / reason |
|---|---|---|
| Cloud f0, f1, f2 | **Usable as-is** | Complete 62×32/1024-pixel diamonds, clean masks, retail-like hotspot (31,31); source crops each match 1024/1024. Strong cross-shot support. Use flat footprint, not current raised slab. |
| Cloud f3, f4 | **Needs cleanup/completion** | Only 288 and 481 pixels of 1024; unknown is encoded transparent. Reject as complete repeatable tiles. |
| Plain and banded white columns | **Usable as-is** | 16×47, 710/698 opaque pixels, coherent silhouettes; (8,47) hotspot and 32×32×40 footprint plausible. Cap combines observations across shots, not one fully observed object. |
| Marble walkway | **Needs cleanup/completion** | 62×52, 1527 pixels; 34 inferred rim pixels, unseen right end face. Plausible repeating slab, not a recovered complete freestanding/end tile. |
| Gold brick f0 | **Usable as-is** | Complete 1024-pixel diamond, no obvious background bleed; still retain consensus provenance. |
| Gold brick f1 | **Needs cleanup/completion** | 1016/1024; eight missing pixels cannot silently be transparent ground. |
| Shield sun half | **Needs cleanup** | Clean-looking left-half draft, 339 pixels; right edge occluded. Hotspot (6,32) is inherited/composite-style rather than independently recovered. |
| Shield eye half | **Needs cleanup** | 274 pixels, rubble occlusion and stray black specks; null hotspot, colour-key mask explicitly uncertain. |
| Felicitar | **Needs cleanup/provenance** | 1502 pixels, including 42 invented hidden-foot pixels. Original is 33×53, not report’s 29×53. Suitable reference after explicit completion, not wholly recovered art. |
| Doloras / Timyra | **Usable as-is, static poses** | Coherent amber silhouettes, 1181/1712 pixels, plausible declared hotspots/footpads. Shatter/freed frames remain missing at this scale. |
| Full shield on altar | **Usable as-is, static prop** | 609-pixel coherent disc with 1994 emblems; ship a new LV shape/frame rather than overwrite base-game 828. |
| P1 striped prop | **Needs cleanup/identification** | Sparse 166-pixel bones-like cut; unknown object composition and hotspot (-2,18), not independently established geometry. |
| Fire pillar | **Reject as direct replacement** | Scene background attached at lower right, pin-driven hotspot (2,104); recover clean column and separate pit first. |
| Lava glow/pit composite | **Reject as reusable sprite** | 1376-pixel irregular residual with occlusion holes; useful reference for layered pit/effect reconstruction. |
| Wall spikes 0–9 | **Needs cleanup** | Ten scene-conditioned masks, 86–125 pixels, not identical reusable frames; spike 6 is documented as best unoccluded source. |
| Water Zombie s02_a | **Needs cleanup; partial actor set** | 660-pixel mask includes two isolated floor pixels; observed pose only, absent hidden pixels not proved transparent. |
| Water Zombie s02_b | **Needs cleanup; partial actor set** | One connected 701-pixel component, visually useful back pose; no complete animation or independently checked footpad. |
| Water Zombie s09 | **Needs cleanup; partial actor set** | 651 pixels, four-pixel detached floor patch; missing animation and possible occluded-body pixels. |
| Fish halo | **Reject as independent sprite** | 427-pixel render residual around retail fish; may encode variant/palette/animation state rather than an object [INFERENCE]. |
| Waterfall foam residual | **Reject as independent sprite** | 1549-pixel multi-tile residue, not a recovered animation frame; investigate retail foam phase instead. |
| Pen skull beam | **Needs cleanup/completion** | 1037-pixel composite includes disconnected wood/stone scraps; separate actual beam from residual terrain and determine footprint. |
| screen19 elder | **Reject current actor mask** | Door frame/background baked in; useful source reference only until resegmented. |
| screen20 staff elder | **Needs cleanup/animation** | Cleaner 757-pixel pose; staff/hotspot and silhouette should be validated independently of screenshot difference mask. |
| Two spear children | **Needs cleanup/animation** | 200/203-pixel coherent poses, but only one direction/state each; incomplete actor shapes. |
| Two blue plants | **Needs cleanup/footprints** | 159/142-pixel colour-keyed drafts; plausible visible plant bodies but missing/ambiguous stems or obscured pixels remain. |
| screen01 observed cloud | **Reject as a game frame** | Full-screen 320×186 observation mask, 5250 pixels, including edge material; provenance/evidence only. |
| screen14 rib; screen15 rib/red blob | **Needs identification** | Tiny 10/11/25-pixel scraps; insufficient evidence for a standalone complete object. |
| screen16 rib/trail | **Needs cleanup/completion** | 99/125-pixel partial bone observations, not a complete proven sprite or scatter footprint. |

Evidence: `art_inventory.json` includes each file’s size/palette/opacity; `source_crop_measurements.json` records best source boxes and matches; `<asset>_source_pair_x4.png` shows crop left/extraction right; `Recon*_contact_x4.png` shows every asset at ×4.

### Comparison with current custom shapes

Generated with `shape_viewer.read_flx_entry`, `parse_shape_frames`, and `frame_to_image` from **shared/build/U8SHAPES.FLX**, without rebuilding:

* **860:** current 36×124 / 96×71 / 54×124 gods differ markedly in scale and pose/detail from 33×53 / 43×38 / 31×67 recovered frames. This supports replacement/redrawing, but all 42 current animation/shatter/freed frames need a consistent redesign, not just three pasted bases.
* **861:** current 58×127 runed obelisk is plainly unlike the source’s retail-stack composite. Its replacement needs the new column base as well as retail 12/545/814; “100% retail obelisk” should not imply the entire supporting structure is retail.
* **862:** current 63×34 slab/hotspot (32,39) differs from recovered 62×32/(31,31) tiles. Changing drawing, hotspot, height, solidity/land flags and support together is necessary.
* **865:2:** current 23×95 flame column is not the dark banded, red-cap pillar. The visual criticism is valid; the supplied replacement mask is not ready.
* **870:** current 18×27 / 17×26 halves have different emblems and origins. New recovered masks require deliberate hotspot/interaction alignment, not raw pixel swap.
* **872:** 451 current ghoul-derived frames have pale blue-grey bodies; source poses are teal/green with a dark kilt. Three poses constrain the redesign but cannot replace a full animation set. Adding arbitrary frames without ANIM.DAT/event mapping would not make the actors assume the photographed pose [INFERENCE].

Readable comparisons: `custom_860_x4.png`, `custom_861_x4.png`, `custom_862_x4.png`, `custom_865_x4.png`, `custom_870_x4.png`, `custom_872_x4.png`.

## Approach assessment and recommended next steps

The decomposer is useful **candidate generation**, not proof. It samples 24 anchors, raises thresholds for low-detail hits, accepts occluded partial matches, suppresses nearby same-frame hits, then greedily counts only newly matching pixels (`shot_decompose.py:108–167,191–209`). Greedy coverage neither penalizes all contradictory pixels nor enforces paint order. Flat-colour ambiguity and nonmaximum suppression can discard the true alternative. The reports appropriately corrected several navy false positives; retain that manual/physical validation rather than equating initial 85–95% coverage with a scene solution.

1. **Repair the evidence contract first:** one reproducible replay command, explicit pixel masks, uniform all-pixel strict/tolerant metrics, final-owner provenance, native crops, regional/actor scores and immutable source hashes.
2. **Clean art before integration:** isolate masks from residual differences, correct cloud completeness claims, record inferred pixels, complete unseen faces/poses intentionally, and establish final hotspots/footprints/flags. Retain original source crops as evidence.
3. **Separate historical constraints from design choices:** publish relative screen/occlusion constraints and selected world coordinates independently; label map assignment, origins, tier lifts, hidden support and pin movements with their inference level.
4. **Integrate with visibility margins:** include neighbours whose projected sprite bounds can enter the view, not merely items inside the floor footprint. Recheck route/collision/support and quest-usecode consequences of every pin/hotspot change.
5. **Repaint final IDs/artifacts and runtime state:** final TYPEFLAG, animation tables, shape IDs, actual list order, actor/effect state and neighbouring terrain must be part of the fixture. Built FIXED.DAT alone is not enough.
6. **Make exactness a real acceptance criterion:** retain the offline fit as a diagnostic, then require controlled in-engine camera captures at the proper native crop. Explicitly decide how cursor/UI, unavoidable source-only effects and unavailable animation phases are represented; do not silently lower “exact” to the current percentages.

**Bottom line:** preserve this work; it substantially improves the visual evidence base and convincingly identifies many retail components. Treat it as an annotated reconstruction proposal with excellent partial evidence—not nineteen exact, physically proven, production-ready scenes.
