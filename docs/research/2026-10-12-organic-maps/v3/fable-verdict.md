# FableReview — Round 3 final verdict (2026-10-13)

Round 3 ended early: all three Astra agents died on the gpt-6-astra usage limit ~12 min in (coordinator confirmed). Each still landed at least one full iteration with game-scale pairs, per the quota-safety protocol. All claims below are from ×3 nearest-neighbour side-by-sides against `/tmp/lv-maps-research/RefArtCatalog/x3/`.

## Corrections sent (and their fate)

**To AstraVale3** (3 messages):
- Iteration-0 list from the v2 review: (1) grey-rock/dirt ground polarity, (2) elevation tiers + cliff faces + stairs, (3) dirt frame-repeat, (4) curved varied water rims + screen09 waterfall, (5) no in-frame black void, (6) cluster dressing by function (camp/urns/mushrooms), (7) screen21 coal field + lava pool, (8) keep garden, fix its grey intrusion. → **Applied in iter01/02:** 1, 2 (tiers z48/z64/z96–288, textured cliff drops), 8 (screen22 garden now dirt-ringed — confirmed in `iter02_pair_screen22.png`), partial 5. Vale3 additionally found a real v2 bug (cliff shapes 27/28/30/31 f2/3 are BLACK, 29:f6 black — `iter01_cliff_frames.png`) and fixed frame selection.
- Iter01 list: in-frame black void; bare stair-step tier edges → cliff faces/retail stairs; grey mono-frame; floating ruin walls; Hoskuld 0.904>0.75 + 24.4k>22k budget; screen19/20 clusters. → **Applied in iter02:** Hoskuld→0.765, items→23,274, dressing 1,170→2,447, cliff faces textured, reach run (13/13). **Not applied (died):** grey frame variety, camp composition (screen20), knoll+urn stack (screen19), temple masonry cleanup (screen17), residual black seams, ≤22k, waterfall.
- Ack of their scoped ground split + caution that hidden-back culling must be occlusion-based, not compass-based (they then self-reported visible backs on ridge corners — unfixed at death).

**To AstraInteriors3** (2 messages):
- Iteration01 list: (1) black void rims (dais bottom, lava fields), (2) cameras miss dais/shrine money shots, (3) hub single-frame paving, (4) lava banks + smaller extent, (5) black rubble reads as holes, (6) ragged grey/blue floor boundary. → **Applied in iteration02:** dais rebuilt (48u tomb dais, six 8u stair courses, real blood 839+423 — their catch that memo's 332 is severed arms), 256u cap-footprint fix. **Not applied (died):** all of 1–6 otherwise; `iteration02_map11_fire_lava.png` and `_map11_hub.png` are byte-identical to iteration01.
- Ruling on the screen04 trio: pins win; impossible to frame all three gods in one native 320px window (1536u = 384px spacing) — logged as a **user decision**, not a defect.

**To AstraCloud3:** none from me — they died before producing renders I had reviewed (iter01 pairs landed 04:52, death ~04:54). Their iter01 did apply my round-2 pre-loaded list (862 blue-grey ramp, lobed rims, desaturated gold, 3×3+2×2 drum mound, 192u colonnade, r420 ring, connected processional sheet) and their own REPORT honestly lists what's still wrong.

## Verdict per map (closeness to 1994 at game scale, 1–10)

| Map | Score | Justifying side-by-side | Notes |
|---|---|---|---|
| Map 10 Vale village (screens 19/20/22) | **6** | `v3/AstraVale3/iter02_pair_screen22.png` | Garden panel genuinely close (7); hut panel lacks knoll/urns; camp absent. |
| Map 10 Vale highlands (screens 17/18/02/09) | **4** | `v3/AstraVale3/iter02_pair_screenshelf.png` | Tiers + textured cliffs landed; mono-frame grey, black seams, no waterfall, temple masonry clutter. |
| Map 17 Cloud City | **5** | `v3/AstraCloud3/iter01_m17_pair_screen11.png` | Obelisk/drums/colonnade/gem-ring correct; gold floor dominates where cloud should sit; cloud texture striped; screen12 missing railing walls + ritual carpet. |
| Map 13 summit/climb | **3** | `v3/AstraCloud3/iter01_m13_pair_screen16.png` | Large black facade voids, no blue water/falls, peat floor reads wrong; furthest from reference. |
| Map 9 arrival/dais | **5** | `v3/AstraInteriors3/iteration02_map09_dais.png` | Dais + stairs + blood now real; camera cuts altar, black wedges at frame bottom, tile repetition. |
| Map 11 catacomb wings | **4** | `v3/AstraInteriors3/iteration02_map11_fire_lava.png` | Wings exist, pins honoured; lava wallpaper with raw sawtooth edges over black; hub monotone. |
| Map 18 shrine | **4** | `v3/AstraInteriors3/iteration02_map18_godwest.png` | Draft god-slab art good; plinth is a flat placeholder plate; trio composition pin-blocked (user decision). |
| Map 39 hedge/forest | **5** | `v3/AstraInteriors3/iteration02_map39_hedge.png` | Direction right (unchanged since iteration01). |

## Best render per map
- Map 10: `AstraVale3/iter02_pair_screen22.png` (whole map: `iter02_whole_map.png`; reach 13/13 in `reach.json`, 23,274 raw items, 65/65 pins).
- Map 17: `AstraCloud3/iter01_m17_pair_screen11.png` (5,772 items, 11 pins exact + 2 deferred).
- Map 13: `AstraCloud3/iter01_m13_pair_screen01.png` (8,230 items, 11/11 pins).
- Map 9: `AstraInteriors3/iteration02_map09_dais.png` (1,905 items).
- Map 11: `AstraInteriors3/iteration02_map11_pillars.png` (22,943 items).
- Map 18: `AstraInteriors3/iteration02_map18_shrine.png` (4,209 items).
- Map 39: `AstraInteriors3/iteration02_map39_hedge.png` (6,177 items).

## Ranked remaining gaps

**Placement / generator fixes (no new art):**
1. In-frame black void — still the #1 credibility killer on Vale shelf/screen20 seams, m13 facades, map09 frame-bottom, map11 lava surrounds. Occlusion-correct backfill everywhere within ~1500u of routes.
2. Grey ground mono-frame (Vale highlands, map18/map9 cave floor, map11 hub paving): frame mixing by coord hash + boulder/stalagmite/rubble clusters.
3. Functional dressing clusters: screen20 camp (fire 267 + logs + bedroll), screen19 urn stack + knoll, mushroom colonies at cliff lips.
4. Composition cameras + money shots: map09 dais framing; map18 plinths (stepped stone, not flat plate); Vale temple masonry cleanup; lava banks/extent on map11.
5. Cloud City: cloud sheet directly under gem ring, gold forum pushed south; furniture clustering; remove old summit columns; m13 climb rebuilt toward screen16 (water + falls + ledges).
6. Budgets/thresholds: Vale ≤22k items; Hoskuld 76.5%→≤75%; Cloud/Interiors pin-flood audits never ran.

**New art (874–881 contracts in `AstraCloud3/art_contracts.json`, drafts in `art/` and Interiors `draft_*`):**
1. Cloud tile de-striping (862-family fills) + 880/881 lobe polish — gates every Map 17/13 shot.
2. Waterfall frames for Vale screen09 and m13 (v2 drafts exist, never placed).
3. God shrine slabs + fire-pillar (drafts good; need plinth art and shape-ID allocation via art-track).
4. Iron-railing fence for the garden (nice-to-have; wood rails pass at 6/10).

**User decisions:**
1. Map 18 trio: accept pin-true wide spacing, or approve moving flanking god pins ~500u inward to enable the 1994 screen04 composition.
2. Vale red keep: keep as-is or commission replacement (Vale3 kept it, flagged explicitly).
3. Element-wing naming: accept source/pin assignment (Earth NW, Air NE, Fire SW, Water SE) over my round-2 memo — I endorse the pins.

## Iteration log
- Vale3 confirmed scoped ground split (grey highlands, 60–75% dirt basins); I ack'd.
- 04:47 Vale3 iter01 reviewed → 6 ranked fixes sent.
- 04:48 Interiors3 iteration01 reviewed → 6 ranked fixes sent; element-name correction accepted.
- 04:49–04:52 Vale3 iter02, Interiors3 iteration02, Cloud3 iter01 landed.
- ~04:54 all three Astra agents died on provider usage limit; no further renders.
