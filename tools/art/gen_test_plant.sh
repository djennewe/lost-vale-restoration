#!/bin/bash
# tools/art/gen_test_plant.sh: the Passage Test plant (Map 10), shape 871.
#
# Art-track contract 13 (docs/art-track.md). The "Test of Rutabaga": "a
# nasty plant with delectable fruit at its heart, guarded by long poisonous
# spines" (story-beats.yaml beat 8, from Plot v1.2), the Art List's "Test
# Tree/plant/fruit" (items.yaml:224). It stands on the test grounds plateau
# where lv-patched/PLNTST.UNK blows it away and pops five more of it.
# Today it is shape 126 frame 0, which is not a plant at all: a 62x32
# blue-crystal ground tile, SI_LAND, that the Avatar walks over.
#
# The reference is the GAME'S OWN PLANTS: base 65 frames 0/2/6 (the
# mushroom cluster), 625 (a mushroom cap) and 753 (the potted plant),
# rendered on magenta at shared/docs/art-poc/test-plant/reference-plants.png
# by tools/art/static_items.py refs. Match their idiom, not their shapes.
#
# The deciding constraint: the box is footpad (3,3,4), 48x56 px at game
# scale, the sprite ~48 tall beside a 50-px Avatar, so the spines and the
# fruit must be big enough to survive a 1024 -> 48 downscale.
#
# SAFE TO RE-RUN: a candidate already on disk is skipped. Delete the one
# you want re-rolled. Every attempt's full agy output is kept under
# $LV_GEN_LOGDIR (default /tmp/lv-genlogs). Read it before trusting a
# file: on a 429 agy's inner agent has been seen to draw a substitute with
# PIL and report success (see the agy-image skill), and only its own words
# give that away.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
O=$ROOT/shared/docs/art-poc/test-plant
REF=$O/reference-plants.png
LOGD="${LV_GEN_LOGDIR:-/tmp/lv-genlogs}"
mkdir -p "$LOGD" "$O"

TAIL='The whole plant is inside the frame with a margin of background all round, no shadow on the ground, no ground plane, no soil, no pot, no other objects, no text. If image generation fails for any reason (quota exhausted, 429, rate limit, capacity error), report the exact error and STOP. Do NOT create a substitute image by any other means (no procedural generation, no PIL/numpy/matplotlib drawing, no placeholder) - a fabricated image reported as a success is worse than a clear failure.'

# A standing prop: the obelisk's projection clause, pinned on geometry.
PROJ='Drawn in the fixed camera of Ultima VIII (1994 MS-DOS VGA pixel art): seen from above at the steep angle of a 2:1 isometric floor tile, so the plant grows out of a diamond footprint exactly twice as wide as it is tall, and the top of the bulb shows a lit upper surface. Single light from the upper left, the right side in shadow. Hand-dithered pixel shading, matte, muted VGA colours, a thin dark outline all the way round like the reference sprites, sharp readable silhouette, no glow, no anti-aliasing against the background. The plant is about as wide as it is tall.'

MATCH='Match the reference sprites in IDIOM: the same chunky 1994 game-sprite drawing, the same dark outline, the same three or four tones per material. It is a new plant drawn in that style, and not a copy of any sprite in the reference.'

FIXES='Draw FEW, LARGE features, because the finished sprite is only about fifty pixels tall: one swollen body, eight to twelve long spines each as thick as a fiftieth of the drawing, one fruit. No fine thorns, no small leaves, no flowers, no tendrils, no scattered details.'

gen () {   # gen <name> <description>
  local name="$1" desc="$2"
  local out="$O/${name}_raw.png"
  if [ -s "$out" ]; then echo "SKIP $name"; return 0; fi
  local p="Generate exactly one image with Nano Banana and save it to $out. Use $REF as the reference image: it shows plants and mushrooms from a 1994 game, standing on the floor. $MATCH $FIXES Image description: a 1024x1024 image on a completely flat pure magenta #FF00FF background showing $desc $PROJ $TAIL"
  echo "=== $name"
  script -q -c "agy --dangerously-skip-permissions -p \"$p\"" /dev/null \
      < /dev/null > "$LOGD/testplant_$name.log" 2>&1
  if [ -s "$out" ]; then echo "OK   $name"; else
    echo "MISS $name. agy: $(grep -oiE 'no image generated|quota|429|rate limit|capacity|refus[a-z]*|synthesi[a-z]*|numpy|PIL' "$LOGD/testplant_$name.log" | sort -u | tr '\n' ' ')"
  fi
}

# The named fallback when Nano Banana is quota-walled (2026-10-11: C hit
# `429 RESOURCE_EXHAUSTED` on gemini-3.1-flash-image after A and B). Same
# prompt through Codex's gpt-image-2, which takes NO reference image, so the
# idiom has to come from the words alone and the candidate is less tied to
# the base plants than A and B. Used only as `gen_test_plant.sh --codex C`.
gen_codex () {   # gen_codex <name> <description>
  local name="$1" desc="$2"
  local out="$O/${name}_raw.png"
  if [ -s "$out" ]; then echo "SKIP $name"; return 0; fi
  echo "=== $name (codex)"
  printf '%s' "Call the built-in Codex image_gen tool (gpt-image-2) directly to generate exactly one image.
Save it to: $out
Image description:
A 1024x1024 pixel-art game sprite on a completely flat pure magenta #FF00FF background showing $desc It is drawn in the idiom of the 1994 game Ultima VIII: chunky low-detail VGA pixel art, three or four tones per material, a thin dark outline. $FIXES $PROJ

If the image_gen tool call fails for any reason (rate limit, quota, usage cap, 429, moderation, error), report the exact error and STOP. Do NOT create a substitute image by any other means (no PIL/numpy/matplotlib, no placeholder, no other tool) - a fabricated image reported as success is worse than a clear failure." \
    | codex exec --dangerously-bypass-approvals-and-sandbox --cd "$ROOT" \
      > "$LOGD/testplant_$name.codex.log" 2>&1
  if [ -s "$out" ]; then echo "OK   $name (codex)"; else
    echo "MISS $name. codex: $(grep -ohiE 'moderation_blocked|rate limit|quota|429|usage cap' "$LOGD/testplant_$name.codex.log" | sort -u | tr '\n' ' ')"
  fi
}

# One axis each from A:
#   A  faithful: beat 8 as written, a sickly green bulb, spines, the fruit
#   B  colour:   the same plant in a poisonous palette, livid purple-maroon
#                flesh and pale yellow spines
#   C  form:     A's colours, the bulb lifted on a short thick stalk so the
#                plant stands taller and the spines splay from a head, like
#                a giant thistle
DESC_A='a squat menacing poison plant: a fat swollen bulb-shaped body of mottled sickly yellow-green flesh, low and wide, ringed by a crown of long stiff needle-sharp spines that curve up and outward, darkening to purple-black at their tips; nestled at the heart of the bulb, between the spines, one glossy ripe red-orange fruit, round and tempting.'

DESC_B='a squat menacing poison plant: a fat swollen bulb-shaped body of mottled livid purple and dark maroon flesh, low and wide, ringed by a crown of long stiff needle-sharp spines that curve up and outward, pale bone-yellow along their length; nestled at the heart of the bulb, between the spines, one glossy ripe red-orange fruit, round and tempting.'

DESC_C='a menacing poison plant like a giant thistle: a fat swollen bulb of mottled sickly yellow-green flesh held up on one short thick stalk, a crown of long stiff needle-sharp spines splaying up and outward from the bulb and darkening to purple-black at their tips; nestled at the heart of the bulb, between the spines, one glossy ripe red-orange fruit, round and tempting.'

if [ "${1:-}" = "--codex" ]; then
  shift
  for c in "$@"; do
    eval "d=\$DESC_$c"
    gen_codex "$c" "$d"
  done
else
  gen A "$DESC_A"
  gen B "$DESC_B"
  gen C "$DESC_C"
fi

echo "DONE: $(ls "$O"/*_raw.png 2>/dev/null | wc -l) candidates"
ls -la "$O"/*_raw.png 2>/dev/null
