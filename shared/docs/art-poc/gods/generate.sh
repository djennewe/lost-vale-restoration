#!/usr/bin/env bash
# The 2026-09-13 god-statue generation run: 3 gods x 3 directions.
# Every gen() call SKIPS a candidate whose _raw.png already exists, so
# re-running this over a populated directory is a no-op. Delete the one you
# want re-rolled first. Needs the codex-image route (Codex CLI, gpt-image-2).
set -u
OUT=${OUT:-$(cd "$(dirname "$0")" && pwd)}   # default: this directory
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1

STYLE='Weathered grey-green stone with warm ochre highlights, hand-dithered pixel shading, single light source from the upper left. Oblique dimetric projection matching Ultima VIII'"'"'s fixed camera: viewed from above at roughly 30 degrees, front-facing, no perspective distortion, sharp readable silhouette. The entire background is flat #FF00FF magenta, completely uniform: no cast shadow on the background, no ground plane, no vignette, no text, no border. The object fills the frame.'

gen () {
  local name="$1" desc="$2"
  if [ -s "$OUT/${name}_raw.png" ]; then echo "SKIP $name"; return; fi
  local prompt
  prompt="Call the built-in Codex image_gen tool (gpt-image-2) directly to generate exactly one image.
Save it to: $OUT/${name}_raw.png
Image description:
Ultima VIII Pagan game sprite art, 1994 MS-DOS VGA style. $desc $STYLE

If the image_gen tool call fails for any reason (rate limit, quota, usage cap, 429, error), report the exact error and STOP. Do NOT create a substitute image by any other means (no PIL/numpy/matplotlib, no placeholder, no other tool) — a fabricated image reported as success is worse than a clear failure."
  printf '%s' "$prompt" | timeout 420 codex exec --dangerously-bypass-approvals-and-sandbox --cd "$PWD" > "$OUT/${name}.log" 2>&1
  if [ -s "$OUT/${name}_raw.png" ]; then echo "OK   $name"; else
    latest=$(ls -t ~/.codex/generated_images/*/*.png 2>/dev/null | head -1)
    if [ -n "$latest" ]; then cp "$latest" "$OUT/${name}_raw.png"; echo "OK   $name (rescued)"; else echo "FAIL $name"; fi
  fi
}

# --- Direction A: seated on a high-backed carved throne -------------------
# felicitar_A was run first, inline, with this same wording.
gen felicitar_A 'A single carved stone idol of an ancient Zealan god of Joy: a serene deity seated on a high-backed stone throne carved with spiral glyphs and coiled serpents, head tilted up, arms opening outward in welcome, a radiant sunburst crown.'
gen doloras_A 'A single carved stone idol of an ancient Zealan god of Sorrow: a mourning deity seated on a high-backed stone throne carved with spiral glyphs and coiled serpents, head bowed low, a heavy veil drawn over the hair, both hands clasped against the chest, carved tear-tracks running down the cheeks.'
gen timyra_A 'A single carved stone idol of an ancient Zealan god of Fear: a rigid deity seated bolt upright on a high-backed stone throne carved with spiral glyphs and coiled serpents, face a blank hollow-eyed mask, arms crossed tight across the chest in a warding gesture, a crown of jagged shards.'

# --- Direction B: standing full-length figure on a stepped plinth ---------
gen felicitar_B 'A single carved stone idol of an ancient Zealan god of Joy: a tall standing robed deity on a low stepped plinth, face upturned, both arms raised open to the sky, a radiant sunburst crown, long carved drapery falling in vertical folds.'
gen doloras_B 'A single carved stone idol of an ancient Zealan god of Sorrow: a tall standing robed deity on a low stepped plinth, shoulders slumped forward, head bowed under a heavy veil, one hand covering the face and the other hanging at the side, long carved drapery falling in vertical folds.'
gen timyra_B 'A single carved stone idol of an ancient Zealan god of Fear: a tall standing robed deity on a low stepped plinth, body rigid and straight, a blank hollow-eyed mask for a face, both palms raised outward in a warding gesture, a crown of jagged shards, long carved drapery falling in vertical folds.'

# --- Direction C: non-human Zealan idol, alien and skeletal ---------------
gen felicitar_C 'A single carved stone idol of a non-human ancient Zealan god of Joy: an alien six-limbed deity with a smooth chitinous skull-like head and a crest of radiating spines, hunched on a rough-hewn stone base, upper limbs spread wide in welcome, carved spiral glyphs across the carapace.'
gen doloras_C 'A single carved stone idol of a non-human ancient Zealan god of Sorrow: an alien six-limbed deity with a smooth chitinous skull-like head bowed low, hunched and folded in on itself on a rough-hewn stone base, upper limbs wrapped around its own thorax, carved spiral glyphs across the carapace.'
gen timyra_C 'A single carved stone idol of a non-human ancient Zealan god of Fear: an alien six-limbed deity with a smooth chitinous skull-like head and hollow socket eyes, reared up rigid on a rough-hewn stone base, upper limbs splayed outward in a warding gesture, mandibles locked shut, carved spiral glyphs across the carapace.'

echo "DONE"
ls -la "$OUT"/*_raw.png
