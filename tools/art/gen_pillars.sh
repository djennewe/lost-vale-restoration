#!/bin/bash
# tools/art/gen_pillars.sh: the elemental pillars (Map 11), shape 865, and
# their receptacles, shape 866.
#
# Art-track item 5 (docs/art-track.md contract 5). No 1994 art: Art List
# v2.5 names the four pillars (three crossed out) and a handwritten "Pillar
# receptacle", and nothing else survives. The look is a design choice. The
# reference for the STONE is the ring itself, as it was for the Sacred
# Rock: shape 38 frames 2 and 3 rendered clean on magenta
# (shared/docs/art-poc/sacred-rock/reference-ring-stones.png). The
# ELEMENTS have no reference in the base game as standing columns, so
# their identity is pinned as four named hues, chosen to survive the
# U8PAL quantize as distinct indices: ochre-brown earth, pale grey-blue
# air, red-orange flame, deep blue water.
#
# ONE SHEET PER CANDIDATE. Shape 865 is four frames of one shape and the
# four must share one shaft to read as a family, so each candidate is a
# single image with the four pillars in a row, Earth Air Fire Water, and
# tools/art/split_sheet.py cuts it into frames on the magenta bands
# between them. A sheet with fewer than three clean bands is a MISS, not a
# candidate: the splitter refuses to guess.
#
# SAFE TO RE-RUN: a candidate already on disk is skipped. Delete the one
# you want re-rolled. Every attempt's full agy output is kept under
# $LV_GEN_LOGDIR (default /tmp/lv-genlogs). Read it before trusting a
# file: on a 429 agy's inner agent has been seen to draw a substitute with
# PIL and report success (see the agy-image skill), and only its own words
# give that away.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
O=$ROOT/shared/docs/art-poc/pillars
REF=$ROOT/shared/docs/art-poc/sacred-rock/reference-ring-stones.png
LOGD="${LV_GEN_LOGDIR:-/tmp/lv-genlogs}"
mkdir -p "$LOGD" "$O"

TAIL='Every object is inside the frame with a margin of background all round, no shadow on the ground, no ground plane, no other objects, no text and no labels anywhere. If image generation fails for any reason (quota exhausted, 429, rate limit, capacity error), report the exact error and STOP. Do NOT create a substitute image by any other means (no procedural generation, no PIL/numpy/matplotlib drawing, no placeholder) — a fabricated image reported as a success is worse than a clear failure.'

# Pin the geometry, and no adjectives: the clauses that fixed the
# encased gods, the obelisk and the Sacred Rock.
PROJ='Drawn in the fixed camera of Ultima VIII (1994 MS-DOS VGA pixel art): seen from above at the steep angle of a 2:1 isometric floor tile, so the foot of each pillar stands on a diamond footprint exactly twice as wide as it is tall, the near vertical edge runs straight down the middle of each pillar, the LEFT face is mid-value and the RIGHT face is clearly darker, and the top shows a lit upper surface. Single light from the upper left. Hand-dithered pixel shading, matte, muted VGA colours, sharp readable silhouette, no glow halo or bloom outside the silhouette, no anti-aliasing against the background.'

MATCH='Match the two reference stones exactly in MATERIAL and PALETTE for every part that is stone: the same COLD BLUE-GREY stone with a violet cast, never neutral grey, and the same narrow range of muted mid values, cut by the same hands.'

FIXES='Each stone part is ONE SINGLE PIECE OF STONE, with no bricks, blocks, courses, joints or mortar lines. There is NO BLACK OUTLINE and no keyline anywhere: the edge pixels of each object are the object own colours meeting the background directly, exactly as the reference sprites have no outline.'

# The sheet rule. The splitter cuts on empty magenta columns, so the gap is
# pinned as geometry, and the four are pinned as the same object four times.
ROW='The image shows FOUR SEPARATE STANDING PILLARS side by side in one row, left to right EARTH, AIR, FIRE, WATER. All four are exactly the same height and the same width, each about four times as tall as it is wide, and each is drawn as the same pillar differing only in its element. Between every pair of neighbours there is a clear vertical band of flat magenta background at least as wide as one pillar, so that no two pillars touch or overlap and nothing is shared between them: no common base, no ground, no line. The row fills the width of the image and the pillars fill most of its height.'

# The element hues, named once and reused by every axis. Chosen as four
# hues the U8 palette keeps apart: earth and fire are both warm, so earth
# is pinned brown and fire is pinned toward red and yellow.
HUES='The element colours are: EARTH is ochre and earthy brown; AIR is pale grey-blue, almost white, with soft curling strokes; FIRE is red-orange with yellow at its heart; WATER is deep saturated blue with pale highlights. These four hues must be clearly different from each other and from the blue-grey of the stone.'

gen () {   # gen <name> <description>
  local name="$1" desc="$2"
  local out="$O/${name}_raw.png"
  if [ -s "$out" ]; then echo "SKIP $name"; return 0; fi
  local p="Generate exactly one image with Nano Banana and save it to $out. Use $REF as the reference image: it shows two views of one carved standing stone from a 1994 game, whose material every stone part below must match. Do NOT redraw the reference stone. $MATCH $FIXES Image description: a 1024x1024 image on a completely flat pure magenta #FF00FF background showing $desc $HUES $PROJ $TAIL"
  echo "=== $name  $(date +%H:%M:%S)"
  script -q -c "agy --dangerously-skip-permissions -p \"$p\"" /dev/null \
      < /dev/null > "$LOGD/pillars_$name.log" 2>&1
  if [ -s "$out" ]; then echo "OK   $name  $(date +%H:%M:%S)"; else
    echo "MISS $name. agy: $(grep -oiE 'no image generated|quota|429|rate limit|capacity|refus[a-z]*|synthesi[a-z]*|numpy|PIL' "$LOGD/pillars_$name.log" | sort -u | tr '\n' ' ')"
  fi
}

# One axis each. The shaft is the family; the axis is where the element
# lives.
#   A  crown:    the same plain stone shaft, crowned with its element
#   B  emblem:   the same plain stone shaft, the element carved and painted
#                on the lit face
#   C  column:   the element IS the column, on a common stone base, which
#                is what the 1994 barks say ("column of roaring flame")
DESC_A="$ROW Each pillar is the same plain dressed shaft of cold blue-grey stone, square in section, tapering slightly, and the CROWN of each pillar is its element, sitting on the flat top of the shaft and about a quarter of the pillar's height: the EARTH pillar is crowned with a rough rounded boulder of ochre-brown rock; the AIR pillar with a curling spiral of pale grey-blue wind; the FIRE pillar with a tall red-orange flame with a yellow heart; the WATER pillar with a rising crest of deep blue water with pale foam."
DESC_B="$ROW Each pillar is the same plain dressed shaft of cold blue-grey stone, square in section, tapering slightly, with a plain flat crown, and on the lit LEFT face of each shaft there is one large carved emblem filling the middle third of the face, cut into the stone and painted in its element's colour, bold and simple enough to read from far away: an ochre-brown mountain peak for EARTH, a pale grey-blue spiral for AIR, a red-orange flame with a yellow heart for FIRE, a deep blue wave for WATER."
DESC_C="$ROW Each pillar stands on the same low square plinth of cold blue-grey stone, about one sixth of the pillar's height, and above the plinth the column IS its element, a solid vertical column the full height of the pillar with a clean readable silhouette: the EARTH column is a column of rough ochre-brown rock; the AIR column is a column of swirling pale grey-blue wind, drawn as a solid twisting form, never transparent; the FIRE column is a column of roaring red-orange flame with a yellow heart; the WATER column is a column of shimmering deep blue water with pale highlights."

# The receptacle: one frame of shape 866, a stone socket at knee height
# beside each pillar, into which the Avatar double-clicks holding the
# opposite element's talisman. Last, because it is the one the quota can
# most afford to miss.
DESC_R='a single low stone receptacle: a squat pedestal of cold blue-grey stone about knee high and as wide as it is tall, square-footed and slightly wider at the foot than the top, with a shallow round hollow cut into its flat top as if to hold a gem the size of a fist, plain and uncarved, its edges worn. The object is about as wide as it is tall.'

gen A "$DESC_A"
gen B "$DESC_B"
gen C "$DESC_C"
gen R "$DESC_R"

# v2, 2026-09-24. Douglas took set C ("I like set C") and asked for the
# columns to be "less rectangular and more organic"; R is approved as is.
# v1's C came back as four prisms with straight vertical edges (the water
# column literally a box), and every set came back about 4:1 slender. So
# v2 keeps C's axis (the column IS its element, on a stone plinth) and
# pins three things as their own clauses: the organic silhouette, the
# shaft weight, and the plinth's match to the ring stone. Two takes on
# "organic", one axis each:
#   C2  natural:  each column is its element's own natural shape
#   C3  wild:     the same, leaning, flaring and asymmetric
ORGANIC='Every column is an ORGANIC NATURAL FORM and never an architectural one: no straight vertical edges, no square or rectangular section, no flat top, no stacked blocks, no prism, no cylinder. Its outline changes width along its height, and its top is irregular and open, the way a rock spire, a whirlwind, a flame and a spout of water are each shaped by their own material. Only the small plinth under each column is cut stone.'
HEAVY='Each column is HEAVY: about three times as tall as it is wide at its widest point, and it fills most of its share of the row, so the four columns together fill the width of the image with narrow gaps between them.'
PLINTH='The plinth under each column is the reference stone material and colour exactly, cold blue-grey with a violet cast, a low square block about one sixth of the total height, and it is the only part that is the same on all four.'
DESC_C2="$ROW $ORGANIC $HEAVY $PLINTH Above its plinth: the EARTH column is a single rough spire of ochre-brown rock, broad and cracked at the foot, narrowing unevenly to a broken crown, its surface all boulders and fissures; the AIR column is a whirlwind of pale grey-blue wind drawn as a solid twisting funnel, narrow where it rises from the plinth and widening as it climbs, its edge ragged with curling wisps; the FIRE column is a single great tongue of red-orange flame with a yellow heart, wide and rolling at the base and licking to a forked tip; the WATER column is a spout of deep blue water rising from the plinth, its sides rippling, its top breaking into pale foam."
DESC_C3="$ROW $ORGANIC $HEAVY $PLINTH Each column leans, flares or bulges as if it were alive, and no two lean the same way. Above its plinth: the EARTH column is a crag of ochre-brown boulders piled and fused into one leaning mass, bulging in the middle, its crown a jagged cluster; the AIR column is a pale grey-blue twister braided from three cords of wind, swelling wide in the middle and fraying at the top into loose streamers; the FIRE column is a roaring blaze of red-orange flame with a yellow heart, flaring out sideways in tongues along its whole height; the WATER column is a surging column of deep blue water that swells, twists and throws off pale foam from its sides and its crest."

gen C2 "$DESC_C2"
gen C3 "$DESC_C3"

echo "DONE: $(ls "$O"/*_raw.png 2>/dev/null | wc -l) candidates"
ls -la "$O"/*_raw.png 2>/dev/null
