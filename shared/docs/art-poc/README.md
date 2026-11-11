# Art generation proof of concept, 2026-07-19

Three AI-generated assets pushed through the full local pipeline: generate
(Codex gpt-image-2 / agy Nano Banana) → magenta-key → downscale → quantize to
`U8PAL.PAL` → encode via `lv_wood_wall.encode_frame`/`encode_shape_blobs` →
`validate_shape` (passed on all three, zero errors).

Full write-up, method, sizes, palette-color counts, and next steps:
`docs/research/2026-07-19-ai-art-generation.md` (Part 3).

Files here:
- `*_raw.png` — straight generation output, magenta background
- `*_game.png` — keyed, downscaled, quantized to real U8PAL indices
- `*_x3.png` — 3x nearest-neighbor preview of `*_game.png`, for eyeballing
- `statue_shape859_preview.png` — the statue read back OUT of a patched
  U8SHAPES.FLX as shape 859, with its anchor marked

The intermediate `*_game.png` / `*_x3.png` files are kept as the record of
the 2026-07-19 run; they are not inputs. `tools/png2shape.py` (built
2026-07-25) goes straight from a `*_raw.png` to an injected shape:

    tools/png2shape.py shared/docs/art-poc/statue_codex_raw.png \
        --donor 443 --height 110 --footpad 3,4,10 \
        --preview shared/docs/art-poc/statue_shape859_preview.png

The encoded `.shp` blobs from the original PoC were scratchpad throwaways
and are not committed; the command above reproduces the statue's exactly
(4,779 bytes).
