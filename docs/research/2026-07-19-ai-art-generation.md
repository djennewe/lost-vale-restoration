# Research + Proof of Concept: AI Art Generation for Lost Vale Assets

Companion to `docs/reviews/2026-07-19-improvement-plan.md` section 6 and
`agents/map-populator/docs/art-placeholder-audit-2026-07-19.md` (the
authoritative placeholder inventory, not duplicated here). This document
covers two things run 2026-07-19: (1) web research into current AI sprite
generation workflows, and (2) a hands-on proof of concept that generated
three assets with Codex (gpt-image-2) and agy (Nano Banana) and pushed them
through this repo's own shape-encoding pipeline end to end.

---

## Part 1: Research — current AI sprite generation workflows (2025-2026)

Original sweep agent stubbed on this question; answered by a gap-filler
follow-up. Confidence and sourcing as reported by the researcher.

**Headline assessment**: current tools can produce palette-locked,
transparent-background, multi-frame sprites, but the ~45-degree dimetric
overhead angle Ultima 8 shapes use is the weakest-supported constraint and
typically needs a 3D-render or manual assist. Static props are low-risk with
any route; animated creatures (Water Zombie, Harpie) need a dedicated
pixel-art tool or a render-then-palettize pipeline, not one-shot
text-to-sprite.

**Three viable routes, in order of fit:**

1. **Dedicated pixel-art SaaS.**
   - **PixelLab** (pixellab.ai): "Create 8-directional sprite (Pro)" generates
     all 8 rotational views (S, SE, E, NE, N, NW, W, SW) of a character or
     object in one 3x3 grid, explicitly aimed at top-down and isometric
     games; also supports 4-directional views. Skeleton-based animation
     (skeletons savable/reusable across characters), text-driven animation,
     and preset action cycles including walking, running, and attacking. Has
     an API. High confidence, sources pixellab.ai/docs and pixellab.ai
     (2026). **This is the closest off-the-shelf match to U8's directional
     dimetric sprite needs** — recommended first pilot for the animated
     creatures.
   - **Retro Diffusion** (Astropulse): its own model trained on licensed
     pixel-art assets; accepts a custom uploaded palette to constrain output
     colors (API `input_palette` parameter); k-means Palettize for color
     reduction; Color Style Transfer added January 2025; fixed-resolution
     grid control (32x32, 64x64); has an API with the same features as the
     web app. Source: astropulse.itch.io devlog, 2025-01. High confidence.
   - Astropulse also publishes **sd-palettize**
     (github.com/Astropulse/sd-palettize), an Automatic1111 extension that
     locks Stable Diffusion output to a chosen limited palette — a direct
     open-source route to the sub-256-color constraint.

2. **Open ComfyUI/A1111 stacks.**
   - SD1.5/SDXL/FLUX + **ControlNet** (OpenPose strength 0.6-0.8 plus Depth)
     for consistent poses; **LoRA** (Kohya SS, 15-25 pose-varied images) for
     per-character identity; generate-high-then-nearest-neighbor-downscale
     plus color reduction/dithering for palette results; `rembg` for
     background removal. Source: a November 2025 open-source guide
     (apatero.com/blog, medium confidence).
   - **LayerDiffuse** (Lvmin Zhang and Maneesh Agrawala, SIGGRAPH 2024) makes
     diffusion models generate **true RGBA transparent images natively**
     via latent transparency and a transparent VAE, trained on 1M
     transparent layer pairs; 97% of a user study preferred it over
     post-hoc matting. Community ports support SDXL and FLUX. High
     confidence, lllyasviel.github.io/pages/layerdiffuse/, 2024-07.
   - An active open pipeline, **mor-o/comfyui-2d-character-pipeline** (~53
     GitHub stars), turns a single character image into layered RGBA sprite
     sheets using WAN 2.2 i2v for motion, Qwen-Image-Edit plus InstantX
     ControlNet-Union for pose, BiRefNet for background removal, and SAM3
     for per-frame segmentation, achieving pixel-identical frame layout via
     video-sequence processing. High confidence, 2025-2026.
   - Frame-to-frame consistency is achieved mainly by **reference-
     conditioning** (IPAdapter transfers subject/style from a reference
     image) and by training a **per-character LoRA** from multi-angle
     images; img2img-seeding later frames from the first frame is a
     lighter-weight method. Medium confidence.
   - Active research direction: **Sprite Sheet Diffusion**
     (arxiv.org/html/2412.03685v1, 2024-12) targets generating game-character
     animation frames from a single design with pose control — the field is
     still maturing, not a solved problem.

3. **Blender-render-then-palettize** (the reliability fallback).
   - Text-to-image AI defaults to side/front views; isometric output needs
     explicit perspective prompting and often ControlNet guidance from
     isometric references, and may still need manual perspective
     correction. Medium confidence, sprite-ai.art guide, 2025.
   - **Blender To Pixels** (Astropulse, astropulse.itch.io/blender-to-pixels)
     is a compositor-based tool (no custom models/materials) that renders
     any 3D model as pixel art at a chosen setting, Windows/macOS/Linux.
     This sidesteps AI angle inconsistency entirely by using a real,
     calibratable camera. Medium confidence, 2024-2025.
   - Recommended as the fallback or primary route for creatures where AI
     angle drift is unacceptable: gives a deterministic ~45-degree camera
     and true per-frame consistency, feeding clean frames into our existing
     PNG-to-shape encoder.

**Palette and transparency, downstream not upstream**: for multi-image
palette consistency, the documented solution is one **global palette** built
from all source frames combined, applied via fixed mapping (optionally with
Floyd-Steinberg dithering to reduce banding) rather than per-image
quantization, which produces mismatched colors between frames of the same
object. This matches how our own quantizer already works (against the fixed
U8PAL.PAL, by construction).

**Watch items:**
- Angle mismatch: PixelLab's 8-direction grid may not exactly match U8's
  specific projection; expect per-frame cleanup or a Blender camera
  calibrated to the engine angle.
- Licensing: Retro Diffusion and PixelLab are proprietary SaaS trained on
  licensed datasets; confirm output license terms fit the no-copyrighted-
  bytes distribution model before shipping any generated art.
- Frame consistency is still imperfect even with IPAdapter/LoRA/i2v; budget
  for hand-fixing, especially multi-frame attack cycles.
- Tool churn: Retro Diffusion is phasing out its Aseprite extension for a
  native editor; the ComfyUI stack (WAN 2.2, SAM3, Qwen-Image-Edit) has no
  stable releases and moves fast — pin versions if adopted.
- Community reception: AI-generated art in retro fan-restoration projects has
  real backlash precedent. Disclose the toolchain in release notes, keep
  AI-generated assets clearly separable and originally authored, and treat
  the 22 recovered screenshots as the non-negotiable fidelity bar.

---

## Part 2: Repo audit — the existing shape-injection pipeline

A read-only repo audit (separate from the web research above) mapped exactly
what exists today for turning an image into an in-game shape, ahead of the
hands-on PoC. Full detail preserved here since the improvement plan only
summarized the recipe.

**Palette**: `shared/data/u8-install/STATIC/U8PAL.PAL`, 772 bytes: 4-byte
header (observed `00 00 00 01`) then 256×3 bytes of 6-bit RGB (0-63 per
channel). Convert to 8-bit via `(x<<2)|(x>>4)`. Loaded by
`shape_viewer.load_palette` into a 256-entry `list[(r,g,b)]`. **Palette
index 0xFF (255) is the transparent keycolor** throughout the decoder and
encoder and must never be assigned to an opaque pixel.

**Shape/FLX container format** (as implemented, cross-checked against
Pentagram's `shapes.cmp.txt`):
- FLX: 0x80-byte header; `uint32` entry count at offset `0x54` (U8SHAPES.FLX
  = 2048, matching TYPEFLAG's 2048 shape ids); index table at `0x80` with
  8-byte entries (`uint32` file-offset, `uint32` size); an empty slot is
  `(0,0)`. Injection = append the blob at EOF, write offset+size into that
  slot.
- Shape blob: 6-byte header (4 unknown bytes + `uint16` num_frames), then
  `num_frames` frame-table entries of 6 bytes each (`uint24` frame_offset
  relative to shape-blob start + 1 unknown byte + `uint16` frame_length),
  then the concatenated frame blobs (frames may differ in size).
- Frame blob: 18-byte header (8 unknown/zero bytes + `uint16` compression
  [0=uncompressed, the path we use] + `sint16` width + `sint16` height +
  `sint16` xoff + `sint16` yoff), then a height-entry `uint16` line-offset
  table where the **stored** value is `running_rle_byte_offset + (height -
  y)*2` (the decoder subtracts that back), then RLE rows. An uncompressed
  row is repeated chunks of `[skip:u8 transparent-run, dlen:u8, dlen literal
  palette-index bytes]`; a trailing skip terminates the row.
- **Critical invariant**: for uncompressed frames, `dlen` is the **raw**
  literal pixel count, *not* `count<<1` — the engine only right-shifts
  `dlen` when the compressed flag is set. Getting this backward overruns the
  RLE buffer and SIGBUSes the engine.
- Observed/enforced limits: the parser rejects `num_frames==0` or `>500`,
  and width/height `>1024`; `frame_offset` is `uint24` (16 MB cap within a
  shape); `frame_length` is `uint16` (frames must stay under 65,536 bytes).

**Existing tools** (all in `agents/map-populator/src/` unless noted):
- `lv_wood_wall.py` — the proven injection pipeline. `encode_frame` /
  `encode_shape_blobs` / `encode_shape` build engine-exact shape blobs;
  `validate_shape` is a faithful port of the engine's RLE pointer-walk and
  returns `[]` when safe (any non-empty result means the shape would
  overrun the buffer and must not ship). `inject_shape(shape_blob, shape_id,
  src_path, dst_path)` appends a blob to a copy of U8SHAPES.FLX and rewrites
  that slot's index entry. Its shipped `main()` path is **procedural**
  (paints vertical wood planks over a base-game shape's silhouette) — it
  never reads an image. Image helpers `crop_se_face()`, `synth_se_face()`,
  `build_palette_image()`/`quantize_to_u8()` exist in the file but are
  **dead code**, never called by `main()`, and `quantize_to_u8` does not
  reserve index 255 for transparency (a real bug if it were wired up
  as-is).
- `shape_viewer.py` — canonical shape **decoder** and palette loader; the
  round-trip reference the encoder must match.
- `shape_render.py` — standalone renderer, dumps any shape id (or a range)
  to a PNG contact sheet, auto-preferring `shared/build/U8SHAPES.FLX`. Use
  to visually verify an injected shape without launching the game.
- `patch_typeflag.py` — produces `shared/build/TYPEFLAG.DAT` by copying an
  existing donor shape's 8-byte TYPEFLAG entry into a new shape's slot
  (`REMAP` dict, `new_id -> donor_id`); currently hardcoded to slots
  856-858.
- `parse_typeflag.py` — TYPEFLAG.DAT reader/decoder with `--find` and
  `--footpad` queries to pick a good donor for a new shape's entry. Layout:
  2048×8 bytes; byte0 physics flags, byte1 lo flags + hi family, byte2
  equip + footpad_x, byte3 footpad_y/z, byte4 anim, byte5 flags, byte6
  weight, byte7 volume.
- `u8_flex.py` — read-only FLX archive class; documents the container layout
  but injection is **not** done through it (`lv_wood_wall.inject_shape`
  hand-writes the index instead).
- `build_shape_gallery.py` — the pattern for placing a shape into a test map
  (Map 22) via `u8_map.MapItem.placed_item`; good template for dropping a
  new shape into the world for verification.
- `iso_render.py` — isometric-context previewer used by
  `lv_wood_wall.preview()`; an alternative visual check.
- `install_lv.sh` — the build-to-game bridge: copies
  `shared/build/{U8SHAPES.FLX,TYPEFLAG.DAT,FIXED.DAT,EUSECODE.FLX}` into the
  game's STATIC/USECODE dirs (creates `.bak` on first run) and, with
  `--run`, launches `scummvm-lv`.

**Injection safety pattern** (proven on the wood-wall shapes, ids 855-858):
read the **pristine** `shared/data/u8-install/STATIC/U8SHAPES.FLX` as `src`,
append each blob to end-of-file, rewrite that slot's 8-byte index entry, and
write to `shared/build/U8SHAPES.FLX` as `dst`; chain subsequent injections
with `src=dst`. Always target an **empty** slot (index `(0,0)`) rather than
replacing a base-game shape — replacing in place is the oversized-
replacement corruption class that retired `--stealth` (see CLAUDE.md). Pair
every new id with a `patch_typeflag` REMAP entry, and always run
`validate_shape()` before installing. Appending grows the FLX and changes its
md5, which per existing project memory can require a `build_scummvm.sh`
relink or the game reports "Game data not found." The build copy already
holds shapes 856-858, so any new work should claim **859+**.

**Gaps identified** (what does not exist yet, ahead of building it):
1. A real PNG-to-shape **encoder with transparency**: `quantize_to_u8` needs
   to read PNG alpha (or a designated key color) and map to index `0xFF` for
   transparent pixels, quantizing only opaque pixels against indices
   `0..254` — ideally a hand-rolled nearest-RGB search rather than relying on
   PIL's quantizer, to control the 255 collision explicitly.
2. **Anchor/offset logic**: `encode_frame` takes `xoff`/`yoff` but nothing
   computes sensible values for an arbitrary sprite. U8 positions a sprite by
   these offsets relative to the item's world footprint; a wrong anchor
   makes it float or sink. Convention needed (e.g. `xoff=width/2,
   yoff=height`, or copy a donor shape's offsets).
3. **A single driver/CLI** tying it together: PNG + target shape id + a
   TYPEFLAG donor id → quantize → encode_frame → encode_shape_blobs →
   validate_shape → inject_shape → patch_typeflag, all in one command. Today
   these are separate functions across two files with hardcoded ids and a
   hardcoded REMAP dict.
4. Multi-frame/animation slicing: the frame table format supports it, but no
   tooling slices a sprite sheet into per-frame blobs.
5. TYPEFLAG authoring for genuinely novel objects: the current approach only
   copies an existing donor's 8 bytes; an object with no good donor needs
   flags/footpad set by hand.
6. The ScummVM relink step is documented in project memory but not scripted
   into the art pipeline itself.

**STATUS UPDATE 2026-07-25.** Gaps 1, 2, 3 and 5 are closed by
`tools/png2shape.py` (improvement plan 6.1): transparency-aware nearest-RGB
quantization over indices 0..254, three anchor modes, one command end to end,
and `--footpad X,Y,Z` to author a box when no donor has the right volume.
Gap 4 (sprite-sheet slicing) is unstarted, though one PNG per frame works.
Gap 6 is unchanged. Two corrections to the tool notes above: the dead image
helpers in `lv_wood_wall.py` (`crop_se_face`, `synth_se_face`,
`derive_sw_face`, `make_lighter`, `build_palette_image`, `quantize_to_u8`)
were deleted rather than wired up, precisely because of the index-255 bug
noted there; and `inject_shape` now REFUSES a non-empty slot instead of
warning (`force=True` to override, review finding L15). Also corrected: the
wood-wall ids are **856-858**, not 855-858 — 855 was declared but never
injected (L14) and is unallocated. Two format limits the audit above did not
list, both now enforced by `encode_frame`: the RLE skip and run-length fields
are single bytes, so a frame must be 1..255 px wide, and the per-row
line-offset table is `uint16`, so a frame's RLE payload must stay under 64 KB.

---

## Part 3: Proof of concept — three assets, full pipeline, 2026-07-19

Ran the full chain by hand for three assets to validate every claim in Part
2 before committing to building the driver script. Outputs live in
`shared/docs/art-poc/` (raw generations, game-scale quantized PNGs, 3x
nearest-neighbor previews for inspection) plus encoded `.shp` blobs kept in
the session scratchpad (not committed — see "what's not yet in the repo"
below).

### Generation

- **Water Zombie** (via `agy`/Nano Banana): prompted with the actual 1994
  screenshot `shared/data/lv-screenshots/screen19.gif` loaded as an explicit
  style reference, requesting the same oblique dimetric camera, hand-
  dithered shading, and muted VGA palette, on a flat `#FF00FF` background.
  Result: a rotting, waterlogged corpse mid-shamble, one arm reaching,
  algae drips, fish bones in the ribs — matched the requested style well on
  the first attempt.
- **Cloud terrain tile** (via `agy`/Nano Banana): prompted with
  `screen11.gif` (Cloud City) as style reference, requesting a diamond-
  footprint dimetric ground tile of puffy white cloud with pale blue-grey
  dither shading. Result: a clean diamond tile with overhanging cloud edges;
  the diamond angle came back steeper than U8's standard 2:1 ground-plane
  ratio — a concrete example of the "angle mismatch" watch item from Part 1.
  A follow-up prompt pinning the exact 2:1 ratio, or supplying a donor
  shape's silhouette as a second reference image, is the fix to try next.
- **Zealan god statue** (via Codex/gpt-image-2, no style reference image,
  prompt-only): a seated ancient deity on a glyph-and-serpent-carved stone
  throne, weathered grey-green stone, same camera and lighting instructions,
  flat magenta background. Result: the strongest of the three — proportions,
  material read, and camera angle all landed close to a native U8 prop shape
  with no reference image needed.

### Post-processing (the quantize/key script)

Wrote a standalone script (`quantize_u8.py`, session scratchpad — see "what's
not yet in the repo") that: keys out magenta (generous threshold to catch
anti-aliased fringing), crops to the alpha bounding box, resizes to a target
game-scale height via Lanczos, re-keys after resampling (Lanczos can bleed
the key color at edges), then quantizes every opaque pixel to the nearest
`U8PAL.PAL` color by brute-force Euclidean RGB search over the 256-entry
palette (excluding index 255). Results:

| Asset | Game-scale size | Distinct U8PAL colors used |
|---|---|---|
| Water Zombie | 44×64 px | 24 |
| Cloud tile | 80×64 px | 19 |
| God statue | 58×110 px | 30 |

All three read clearly as native-palette sprites at 3x preview scale — no
banding or muddy color collapse from the quantization step, which validates
that palette-locking downstream (rather than during generation) is
sufficient, matching the research in Part 1.

### Encoding and validation (closing the pipeline's identified gap)

Wrote a second script that reuses the repo's own encoder unmodified: builds a
per-pixel index list (alpha < 128 → `0xFF`, else nearest-palette index via
the same search as above), calls `lv_wood_wall.encode_frame(pixels, w, h,
xoff=w//2, yoff=h)`, wraps it with `encode_shape_blobs([frame])`, and runs
`validate_shape()`.

**Result: all three produced shape blobs that passed `validate_shape()` with
zero errors** — Water Zombie 1,700 bytes, cloud tile 3,362 bytes, statue
4,779 bytes. This confirms gaps 1 and 2 from Part 2 (transparency-aware
quantization, anchor offsets) are solvable with straightforward code, and
that the existing `encode_frame`/`encode_shape_blobs`/`validate_shape` chain
needs no modification to accept AI-generated input once it's been quantized
correctly.

**What was proven**: prompt → generate → key → downscale → quantize → encode
→ validate, end to end, twice over (two different generation tools), for
both a style-referenced organic creature and a prompt-only static prop.

**What was not yet done** (the remaining gap, unchanged from Part 2's list):
injecting any of these three blobs into an actual `U8SHAPES.FLX`, patching a
TYPEFLAG entry, placing one in a map, rebuilding, and looking at it in
ScummVM. The `.shp` blobs and the two ad-hoc scripts
(`quantize_u8.py`, `encode_poc.py`) exist only in the session's temporary
scratchpad directory, not in the repository — they were proof-of-concept
throwaways, not the production driver. **The improvement plan (section 6.1)
specifies building `tools/png2shape.py` as the real, committed version of
this glue**, folding in the transparency-aware quantizer and anchor
convention validated here, plus the injection and TYPEFLAG steps this PoC
didn't reach. That script, plus the in-game verification step, is the actual
next action — this PoC de-risked it but didn't finish it.

### Recommended next prompts (learned from this run)

- For terrain tiles: explicitly state the 2:1 width-to-height diamond ratio
  in the prompt, or supply a donor shape's rendered silhouette
  (`shape_render.py`) as a second reference image alongside the screenshot.
- For creatures: the screenshot-as-style-reference technique worked well
  enough to repeat for Harpie, using `screen15.gif` or `screen16.gif`
  (Cloud Cliffs) as the reference instead of the Water Zombie's lake
  reference.
- For static props generally: prompt-only (no reference image) already
  produces strong results per the statue — reserve reference images for
  cases where camera angle or environment context matters most (terrain,
  creatures matching a specific screenshot).
