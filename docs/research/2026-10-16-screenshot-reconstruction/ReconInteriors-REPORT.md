# ReconInteriors — screens 04, 05, 07, 10

Tooling (all in this directory / the eval kernel):
- `cands_<shot>.json`: full retail candidate scan (shot_decompose.find_hits over shapes 0-859, af/ff 0.6, min_px 20); `scan.py` runs it.
- Engine-faithful renderer: item_sorter.ItemSorter's AddItem/below/occludes/PaintSortItem port (sort_item.cpp), with a blit at paint time. Shape 1 (Avatar, 1,550 frames) is searched through item_sorter's _FrameTable (shot_decompose skips it).
- Floor: per-lattice-cell argmax over all 38 frames of 301 (or the shot's floor shape); cells whose best frame matches < 90 % of visible pixels are marked `lattice-fill`.
- Coordinates: projection `sx = x//4 - y//4 + sx0`, `sy = x//8 + y//8 - z + sy0` (C truncation per term); floor on x,y = 127 mod 128; other items solved for the 32-aligned (31 mod 32) x,y nearest the projection inverse.
- Metrics: `frame_px_match` = share of the shot's pixels whose palette class the render reproduces; `covered_px_match` = same over pixels the render draws (equal here because floors fill the frame).

## screen04 — Map 18 sanctum, three gods in amber

Files: `screen04.vignette.json`, `screen04_verify_render.png`, `screen04_verify_diff.png` (shot | render | mismatches red, x3), `screen04_gods_vs_860.png`, `art/s04_*.png`.

- Decomposer coverage 84.9 % → retail-only vignette 91.4 % → with 5 extracted 1994 sprites **99.91 %** (49 px left: a wall-top fragment at the top-right corner, the x=319 column, a 6 px sparkle residue).
- 106 items: 83 floor 301 (frames 0-6, 12, 33), cave walls 27/28/29/31/32/566 (one 566 at z=48, a second course), plinths = retail **37:10 at z0 + 37:13 at z8** (all three), altar **550:0 at z=0 (no dais)**, Shield 828 on it.
- Actors/effects: Avatar shape 1 frame 6 (100 % match; the decomposer's 357:130 hit is the same pixels); three retail sparkle effects **202:9/10** around the gods. They paint over the plinths and under the amber in the shot, which the engine sort reproduces only with the 202s at z=16 (flat at plinth-top height).
- 1994 art (all exact shot pixels, U8PAL-indexed):
  - gods: P1 west 29x53 (hunched figure in profile — Felicitar by elimination [INFERENCE]), P2 north-east 43x38 (kneeling figure in a horizontal block = Doloras), P3 south 31x67 (standing, hand at face = Timyra). Screen-x order Timyra < Felicitar < Doloras, the box-cover order build_map_18 already uses.
  - Our 860:0/1/2 are 2-3x larger (Felicitar 860:0 is ~55x200) and stand on the floor, not on plinths. **Replace 860 frames 0-2 with the 1994 pixels**; the shatter/freed frames 3-41 are drawn at our scale and would need redrawing to match [INFERENCE].
  - Shield: retail 828:0 disc, but with 1994 emblems (yellow sun, red ring, blue drop) where retail has hand/bell/ankh. 828 is a base-game shape, so this belongs in a new LV shape/frame, not an overwrite.
  - A black/white striped prop (ribcage/bones?) lying on the P1 plinth; no retail frame fits (best 146/690 px).
- God layout in the shot (plinth item x,y; gods stand at plinth-32 on the plinth top z=16): P1 (0,0), P2 (+256,-128), P3 (+256,+384) — the whole trio spans 384 x 512 units, vs 1536 x 1024 for the pins.
- Placement: origin (1408,6912,0). Altar → (3127,8175,0); Felicitar (3840,7680,0)→(2783,8031,16); Doloras (3072,6656,0)→(3039,7903,16); Timyra (2304,7680,0)→(3039,8415,16); AOSCENE shield.pop (3056,8176,40)→(3111,8167,16) and camera targets follow; skull 331 off-frame; ceremony egg z 24→0; dais/way/candelabra/rune columns/cushions removed; sanctum south wall y 8703→≥9215 (it paints 12,769 px into the frame where it is). Crack line y=6143 untouched; no 596/865/q299-66 involved.

## screen07 — Map 11 Fire pillar chamber

Files: `screen07.vignette.json`, `screen07_verify_render.png`, `screen07_verify_diff.png`, `screen07_pillar_vs_865.png`, `art/s07_*.png`.

- Coverage: decomposer 89.6 % → retail-only vignette 89.0 % (engine sort, so occlusion is honest) → with 1994 sprites **95.2 %**.
- 137 items: 62 floor 301, cave walls 26/27/28/29/32 in two 48-unit courses (upper course at z=48 over the lower one's x,y; placing it at z=0 further north lets the lower wall's top paint over it, a visible band), black cap flats 334/393/138 at z=48, rubble mound of 98/99/100/112 blocks, two candle posts 453:6, pebbles 782.
- Avatar shape 1 frame 0 at local (1054,739,0) (100 % match).
- 1994-only: the **Fire pillar** (dark banded column, black rings, rust, red gem cap) — nothing like our 865:2 flame, so 865 f2 must be redrawn after it. `s07_fire_pillar.png` is a **reference crop, not a sprite** (it carries pit/wall pixels and a lava lick; D-track 2026-10-16); the clean upper two thirds are `s07_fire_pillar_upper.png` (art_registry 2021), the lower third still to be drawn. It fits the 64x64x80 footpad. Lava light/pit composite around it, and 10 wall spikes (no retail match; small-frame local fit best 92/1453 px; D-track found spike 0 is retail 26:5).
- Placement: origin (6272,20608); the pillar sits exactly on its pin (7680,21504,0). **The Fire receptacle 866 at y+256 paints 899 px into the frame** where 1994 shows the rubble mound → proposal: the candle post 453 beside the pillar becomes the receptacle (npcnum 120 dispatch is shape-independent), (7743,21503,0), 63 units away (COLPUZZL range 300). Vignette walls split the pillar chamber → rerun gate/exact_reach checks.
- Unexplained 4.8 %: right cliff course seam (z=-48 pit walls tested: worse), small wall seams, a white sphere top-left and a text fragment at the bottom (UI [INFERENCE]).

## screen05 — Map 11 Fire wing, daemon's torture chamber

Files: `screen05.vignette.json`, `screen05_verify_render.png`, `screen05_verify_diff.png`.
- Coverage: decomposer 92.2 % → vignette **95.5 %**, all from retail shapes. 124 items (54 floor 301, walls 26-32 in courses, caps 334/393, torture rack 309:0 with a dead body, fire fields 400, wall weapons 308).
- Actors: daemon 96:43 and red-robed figure 200:145 (both 100 %), Avatar 1:253 lying (730/861 px, partly hidden behind the robed figure).
- No 1994-only sprite. Unexplained 4.5 %: the floor-to-void lip and a rock outcrop at the bottom left (no edge frame fits), the fire behind the daemon (no red base ring in the shot), wall seams.
- Placement: Map 11 Fire section, origin (2048,14080), on the group-3 daemon egg (2848,15104) → optional egg move to (2808,15064). In-frame conflicts: fire pit 318 (3072,14848), 436 (3200,15104), causeway edge 70 at x 3455, north-wall pieces, and **lava lake chunk (2,1)** (x 2048-2559, y 14848-15359), where the shot shows ledge and floor.

## screen10 — Map 9 guardian chamber (stepped dais), AUTOMATED PASS ONLY

Files: `screen10.vignette.json`, `screen10_verify_render.png`, `screen10_verify_diff.png`.
- Map 9 [INFERENCE]: the tomb-kit dais (240 tiers, 98/99/100/112 steps, 259 claws), ghouls 581:3 and 142:95, and a body and blood match the guardian chamber's "signs of struggle"; no other LV map uses the tomb kit or ghouls.
- Coverage: decomposer 93.2 % → vignette 91.9 %. **Unfinished:** the Avatar, altar, skull and body on the dais top are solved at z=0, not at the tier height; the stair front and the dais east face are unresolved. No 1994 art isolated.
- Placement: origin (12928,11520), so the dais is centred near the planned (14400,12900). Trigger 200 (14336,12416) falls inside the frame (an invisible egg, so nothing to see). Current Map 9 walls 26/32/564 paint into the frame and must give way.
