#!/bin/bash
# tools/art/gen_sacred_rock.sh: the Sacred Rock (Map 10), shape 863.
#
# Art-track item 3 (docs/art-track.md contract 3). Unlike the obelisk and
# the cloud floor this one has NO 1994 reference: "Sacred Smallish
# Unusual-Colored Rock" was a joke placeholder in Plot v1.1/v1.2 that
# became "Sacred Circle" before the usecode snapshot, so there is no
# original object to redraw. The look was decided instead: Douglas took
# the ninth-stone reading on 2026-09-20, so the reference is the RING
# ITSELF: shape 38 frames 2 and 3, the eight monoliths already standing
# on the circle's 768 radius, rendered clean at
# shared/docs/art-poc/sacred-rock/reference-ring-stones.png.
#
# The deciding constraint from the contract: the centre stone must read as
# belonging to the ring. So the reference is passed the way the obelisk
# passed its screenshot crop (match THIS material, these tones, this
# dressing), and each candidate differs in one axis only.
#
# Height is 96 px at game scale, against the ring's measured 59: half
# again, and clearly short of the obelisk's 127. The generator draws large
# and png2shape rescales, as it did for the obelisk.
#
# SAFE TO RE-RUN: a candidate already on disk is skipped. Delete the one
# you want re-rolled. Every attempt's full agy output is kept under
# $LV_GEN_LOGDIR (default /tmp/lv-genlogs). Read it before trusting a
# file: on a 429 agy's inner agent has been seen to draw a substitute with
# PIL and report success (see the agy-image skill), and only its own words
# give that away.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
O=$ROOT/shared/docs/art-poc/sacred-rock
REF=$O/reference-ring-stones.png
LOGD="${LV_GEN_LOGDIR:-/tmp/lv-genlogs}"
mkdir -p "$LOGD" "$O"

TAIL='The whole object is inside the frame with a margin of background all round, no shadow on the ground, no ground plane, no other objects, no text. If image generation fails for any reason (quota exhausted, 429, rate limit, capacity error), report the exact error and STOP. Do NOT create a substitute image by any other means (no procedural generation, no PIL/numpy/matplotlib drawing, no placeholder) — a fabricated image reported as a success is worse than a clear failure.'

# Pin the geometry rather than adjectives, the clauses that fixed the
# encased gods and then the obelisk (shared/docs/art-poc/gods/encased/v2/README.md).
PROJ='Drawn in the fixed camera of Ultima VIII (1994 MS-DOS VGA pixel art): seen from above at the steep angle of a 2:1 isometric floor tile, so the foot of the stone stands on a diamond footprint exactly twice as wide as it is tall, the near vertical edge runs straight down the middle of the drawing, the LEFT face is mid-value and the RIGHT face is clearly darker, and the top shows a lit upper surface. Single light from the upper left. Hand-dithered pixel shading, matte, muted VGA colours, sharp readable silhouette, no glow halo or bloom outside the silhouette, no anti-aliasing against the background.'

MATCH='Match the two reference stones exactly in MATERIAL and PALETTE: the same COLD BLUE-GREY stone with a violet cast, never neutral grey, and the same narrow range of muted mid values. It is taller and heavier than they are and it is unmistakably the same stone, cut by the same hands.'

# The three defects every v1 candidate shared (2026-09-20): drawn as a stack
# of separate masonry blocks, wrapped in a heavy black keyline the ring
# stones do not have, and neutral grey instead of the ring's blue. Each is
# pinned here as its own clause, because adjectives did not carry them.
FIXES='It is ONE SINGLE PIECE OF STONE, a monolith quarried whole and set upright. It is NOT built of bricks, blocks or courses: there are no joints, no mortar lines and no stacked tiers anywhere on it. Any horizontal marking is a shallow weathered band in the surface of the one stone. There is NO BLACK OUTLINE and no keyline anywhere: the edge pixels of the stone are the stone own colours meeting the background directly, exactly as the reference sprites have no outline. The drawing is about twice as tall as it is wide.'

gen () {   # gen <name> <description>
  local name="$1" desc="$2"
  local out="$O/${name}_raw.png"
  if [ -s "$out" ]; then echo "SKIP $name"; return 0; fi
  local p="Generate exactly one image with Nano Banana and save it to $out. Use $REF as the reference image: it shows two views of one carved standing stone from a 1994 game, the eight of which stand in a ring around the object you are drawing. Do NOT redraw the reference stone. Draw the NINTH stone, the tall one at the centre of that ring, as one clean full-size sprite. $MATCH $FIXES Image description: a 1024x1024 image on a completely flat pure magenta #FF00FF background showing $desc $PROJ $TAIL"
  echo "=== $name"
  script -q -c "agy --dangerously-skip-permissions -p \"$p\"" /dev/null \
      < /dev/null > "$LOGD/sacredrock_$name.log" 2>&1
  if [ -s "$out" ]; then echo "OK   $name"; else
    echo "MISS $name. agy: $(grep -oiE 'no image generated|quota|429|rate limit|capacity|refus[a-z]*|synthesi[a-z]*|numpy|PIL' "$LOGD/sacredrock_$name.log" | sort -u | tr '\n' ' ')"
  fi
}

# One axis each, as the obelisk pass did. v1 (A/B/C, kept on disk as
# provenance) established the silhouette: B's tapering shaft and sloped
# crown is the one to keep. v2 (A2/B2/C2) repeats the axes with FIXES.
#   A  plain:     the ring's stone, taller, no carving
#   B  carved:    the same stone with Zealan markings down the lit face
#   C  weathered: dressed shaft, the crown left rough and unworked
DESC_A='a single tall standing stone of cold blue-grey rock, roughly twice the height of a man and about half again the height of the reference stones, a squared base tapering slightly towards a flat sloped crown, plain and uncarved, its faces weathered and its edges worn.'
DESC_B='a single tall standing stone of cold blue-grey rock, roughly twice the height of a man and about half again the height of the reference stones, a squared base tapering slightly towards a flat sloped crown, and on the lit left face a single vertical line of shallow carved angular runic marks cut into the surface, unpainted and the same colour as the stone so they read only as shadow.'
DESC_C='a single tall standing stone of cold blue-grey rock, roughly twice the height of a man and about half again the height of the reference stones: the lower two thirds squared and smoothly dressed, the crown left rough and unworked where it was broken from the quarry, all of it one continuous piece of stone.'

gen A2 "$DESC_A"
gen B2 "$DESC_B"
gen C2 "$DESC_C"

echo "DONE: $(ls "$O"/*_raw.png 2>/dev/null | wc -l) candidates"
ls -la "$O"/*_raw.png 2>/dev/null
