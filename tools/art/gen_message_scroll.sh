#!/bin/bash
# tools/art/gen_message_scroll.sh: the Message Scroll (Map 17), shape 864.
#
# Art-track item 4 (docs/art-track.md contract 4). Like the Sacred Rock
# this object has no 1994 art: Plot v1.2 beats 13 and 14 give it its
# errand (found in the deserted Cloud World, carried back to Ezrekal) and
# items.yaml one line of content, and no recovered usecode names it. So
# the reference is the GAME'S OWN SCROLL: base shape 159 frames 0 and 3,
# rendered clean at
# shared/docs/art-poc/message-scroll/reference-base-scroll.png.
#
# The deciding constraint from the contract: it must read as a document at
# 1x, lying on the 63x34 flagstone plinth top. That is the hard part here,
# because the sprite is 22 px tall. Every clause below is about keeping
# the feature count low enough to survive the downscale: one sheet, one
# rod, one band of ink, and a silhouette that is a diamond.
#
# SAFE TO RE-RUN: a candidate already on disk is skipped. Delete the one
# you want re-rolled. Every attempt's full agy output is kept under
# $LV_GEN_LOGDIR (default /tmp/lv-genlogs). Read it before trusting a
# file: on a 429 agy's inner agent has been seen to draw a substitute with
# PIL and report success (see the agy-image skill), and only its own words
# give that away.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
O=$ROOT/shared/docs/art-poc/message-scroll
REF=$O/reference-base-scroll.png
LOGD="${LV_GEN_LOGDIR:-/tmp/lv-genlogs}"
mkdir -p "$LOGD" "$O"

TAIL='The whole object is inside the frame with a margin of background all round, no shadow on the ground, no ground plane, no other objects, no text outside the object. If image generation fails for any reason (quota exhausted, 429, rate limit, capacity error), report the exact error and STOP. Do NOT create a substitute image by any other means (no procedural generation, no PIL/numpy/matplotlib drawing, no placeholder) - a fabricated image reported as a success is worse than a clear failure.'

# Pin the geometry rather than adjectives, the clauses that fixed the gods,
# the obelisk and then the Sacred Rock. This object LIES FLAT, so its
# projection clause is the floor tile's, not a standing prop's.
PROJ='Drawn in the fixed camera of Ultima VIII (1994 MS-DOS VGA pixel art): seen from above at the steep angle of a 2:1 isometric floor tile. The object lies FLAT ON THE GROUND, so its outline is a wide diamond, about half again as wide as it is tall, with its long axis running left to right. Nothing stands up out of the ground plane. Single light from the upper left. Hand-dithered pixel shading, matte, muted VGA colours, sharp readable silhouette, no glow halo or bloom outside the silhouette, no anti-aliasing against the background.'

MATCH='Match the reference sprite exactly in MATERIAL, PALETTE and CONSTRUCTION: the same warm tan and cream parchment in a narrow range of muted mid values, the same soft dark brown shading, and the same thin dark outline running all the way round the object, which the reference has and which must be kept. It is the same kind of object, drawn larger and finer.'

# The whole risk on this item is the downscale: the shipped sprite is 22 px
# tall, so anything smaller than about a twentieth of the drawing is gone.
FIXES='Draw FEW, LARGE features. The sheet fills almost the whole drawing. There are at most three separate things on it: the sheet itself, one rolled end, and one band of dark marks across the middle. The marks are short horizontal dashes suggesting handwriting seen from far away, never readable letters and never a paragraph of fine lines. No border decoration, no illumination, no ribbon, no quill, no tassels, no scattered small details anywhere.'

gen () {   # gen <name> <description>
  local name="$1" desc="$2"
  local out="$O/${name}_raw.png"
  if [ -s "$out" ]; then echo "SKIP $name"; return 0; fi
  local p="Generate exactly one image with Nano Banana and save it to $out. Use $REF as the reference image: it shows two colour variants of one open scroll lying on the floor in a 1994 game. Do NOT redraw the reference scroll exactly; draw the object described below as one clean full-size sprite in that same idiom. $MATCH $FIXES Image description: a 1024x1024 image on a completely flat pure magenta #FF00FF background showing $desc $PROJ $TAIL"
  echo "=== $name"
  script -q -c "agy --dangerously-skip-permissions -p \"$p\"" /dev/null \
      < /dev/null > "$LOGD/msgscroll_$name.log" 2>&1
  if [ -s "$out" ]; then echo "OK   $name"; else
    echo "MISS $name. agy: $(grep -oiE 'no image generated|quota|429|rate limit|capacity|refus[a-z]*|synthesi[a-z]*|numpy|PIL' "$LOGD/msgscroll_$name.log" | sort -u | tr '\n' ' ')"
  fi
}

# One axis each, as every pass on this track has done.
#   A  open:    the sheet open flat, both ends barely curled
#   B  sealed:  the same sheet with a single wax seal, the one added mass
#   C  rolling: one end still rolled into a tube, the rest open
DESC_A='a single sheet of aged cream parchment lying open and flat on the floor, its two short ends curled up in shallow rolls, one band of short dark ink dashes across the middle of the sheet, the parchment edges slightly worn.'

DESC_B='a single sheet of aged cream parchment lying open and flat on the floor, its two short ends curled up in shallow rolls, one band of short dark ink dashes across the middle of the sheet, and near the lower right corner one round seal of deep red wax pressed flat onto the parchment.'

DESC_C='a scroll of aged cream parchment lying on the floor, half of it still rolled into a tight tube at the left end and the other half opened out flat to the right, with one band of short dark ink dashes across the open half, the roll and the open sheet clearly one piece of parchment.'

gen A "$DESC_A"
gen B "$DESC_B"
gen C "$DESC_C"

# v2 (2026-09-21). At 22 px every v1 candidate reads as a BLANK sheet: the
# ink band survived the downscale as two or three grey pixels, so the object
# says "parchment" and never says "a written message". v2 pins the ink as
# its own clause, the way the Sacred Rock's v2 pinned the silhouette.
INK='The band of writing is the DARKEST thing in the drawing and the first thing the eye lands on: very dark brown-black strokes, each stroke as thick as one twentieth of the whole sheet, laid in three or four long lines that cross most of the open parchment. It must still read as writing when the whole image is shrunk to the size of a thumbnail.'

DESC_A2="$DESC_A $INK"
DESC_B2="$DESC_B $INK"

gen A2 "$DESC_A2"
gen B2 "$DESC_B2"

echo "DONE v2: $(ls "$O"/*_raw.png 2>/dev/null | wc -l) candidates"

echo "DONE: $(ls "$O"/*_raw.png 2>/dev/null | wc -l) candidates"
ls -la "$O"/*_raw.png 2>/dev/null
