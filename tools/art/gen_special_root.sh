#!/bin/bash
# tools/art/gen_special_root.sh: the special root (Map 10), shape 869.
#
# Art-track contract 12 (docs/art-track.md). The root Ezrekal brews into
# Tyorvi's elixir, found "by the standing stones" (EZREKAL.UNK:3523) and
# picked up: a carryable reagent-sized item lying on the ground. No 1994
# art; the one description on record is Ezrekal's own, "Brightly colored
# I think it was, maybe purple" (lv-patched/EZREKAL.UNK:3557), and the
# brief (2026-10-11) asks for a gnarled, pale, foraged organic reagent. The
# two disagree on colour, so colour is candidate B's axis.
#
# The reference is the GAME'S OWN REAGENTS: base 395 frames 16/19/20 (the
# wood and forked-stick reagents) and 399 frames 4/7/9 (the vine reagents,
# 9 being the "eye of newt" that stands in for the root today), rendered on
# magenta at shared/docs/art-poc/special-root/reference-reagents.png by
# tools/art/static_items.py refs. Match their idiom, not their shapes.
#
# The deciding constraint: the sprite is ~16 px tall and ~24 wide at game
# scale, lying in grass and on flagstones, so it must survive a 1024 -> 16
# downscale (the Message Scroll's v1 lesson): one silhouette, strong
# value contrast, no fine detail.
#
# SAFE TO RE-RUN: a candidate already on disk is skipped. Delete the one
# you want re-rolled. Every attempt's full agy output is kept under
# $LV_GEN_LOGDIR (default /tmp/lv-genlogs). Read it before trusting a
# file: on a 429 agy's inner agent has been seen to draw a substitute with
# PIL and report success (see the agy-image skill), and only its own words
# give that away.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
O=$ROOT/shared/docs/art-poc/special-root
REF=$O/reference-reagents.png
LOGD="${LV_GEN_LOGDIR:-/tmp/lv-genlogs}"
mkdir -p "$LOGD" "$O"

TAIL='The whole object is inside the frame with a margin of background all round, no shadow on the ground, no ground plane, no soil heap, no other objects, no text. If image generation fails for any reason (quota exhausted, 429, rate limit, capacity error), report the exact error and STOP. Do NOT create a substitute image by any other means (no procedural generation, no PIL/numpy/matplotlib drawing, no placeholder) - a fabricated image reported as a success is worse than a clear failure.'

# A small object LYING on the floor: the Message Scroll's projection clause.
PROJ='Drawn in the fixed camera of Ultima VIII (1994 MS-DOS VGA pixel art): seen from above at the steep angle of a 2:1 isometric floor tile. The root LIES FLAT ON THE GROUND, its long axis running diagonally from lower left to upper right, so the whole drawing is about half again as wide as it is tall. Single light from the upper left. Hand-dithered pixel shading, matte, muted VGA colours, a thin dark outline all the way round like the reference sprites, sharp readable silhouette, no glow, no anti-aliasing against the background.'

MATCH='Match the reference sprites in IDIOM: the same chunky low-detail 1994 game-item drawing, the same dark outline, the same three or four tones per material. It is a new object drawn in that style, larger and cleaner, and not a copy of any sprite in the reference.'

FIXES='Draw FEW, LARGE features, because the finished sprite is only sixteen pixels tall: one thick twisting main root, two or three fat forks at one end, and nothing smaller than a twentieth of the drawing. No leaves unless asked, no flowers unless asked, no fine root hairs, no scattered crumbs, no dirt clods.'

gen () {   # gen <name> <description>
  local name="$1" desc="$2"
  local out="$O/${name}_raw.png"
  if [ -s "$out" ]; then echo "SKIP $name"; return 0; fi
  local p="Generate exactly one image with Nano Banana and save it to $out. Use $REF as the reference image: it shows six small reagent items lying on the floor in a 1994 game (sticks, a forked twig and green vines). $MATCH $FIXES Image description: a 1024x1024 image on a completely flat pure magenta #FF00FF background showing $desc $PROJ $TAIL"
  echo "=== $name"
  script -q -c "agy --dangerously-skip-permissions -p \"$p\"" /dev/null \
      < /dev/null > "$LOGD/specialroot_$name.log" 2>&1
  if [ -s "$out" ]; then echo "OK   $name"; else
    echo "MISS $name. agy: $(grep -oiE 'no image generated|quota|429|rate limit|capacity|refus[a-z]*|synthesi[a-z]*|numpy|PIL' "$LOGD/specialroot_$name.log" | sort -u | tr '\n' ' ')"
  fi
}

# One axis each from A:
#   A  pale:   the brief, a gnarled bone-pale root
#   B  purple: the same root in Ezrekal's colour (EZREKAL.UNK:3557)
#   C  crown:  A's root with a small tuft of purple leaves at its top end,
#              so it reads as a plant pulled up whole and carries her
#              "maybe purple" in the one added mass
DESC_A='a single gnarled root pulled up whole from the earth: one thick knobbly taproot, pale ivory and bone white with cool grey-brown shading in its creases, twisting once along its length and splitting at the far end into two or three fat tapering forks, the top end cut off clean and slightly darker.'

DESC_B='a single gnarled root pulled up whole from the earth: one thick knobbly taproot with a bright violet-purple skin, lighter lilac on its lit upper side and deep plum in its creases, twisting once along its length and splitting at the far end into two or three fat tapering forks, the top end cut off clean and slightly darker.'

DESC_C='a single gnarled root pulled up whole from the earth: one thick knobbly taproot, pale ivory and bone white with cool grey-brown shading in its creases, twisting once along its length and splitting at the far end into two or three fat tapering forks, and at its top end one small tuft of three or four broad violet-purple leaves, the only colour on it.'

gen A "$DESC_A"
gen B "$DESC_B"
gen C "$DESC_C"

echo "DONE: $(ls "$O"/*_raw.png 2>/dev/null | wc -l) candidates"
ls -la "$O"/*_raw.png 2>/dev/null
