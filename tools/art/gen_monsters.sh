#!/bin/bash
# tools/art/gen_monsters.sh — key poses for the Water Zombie (872) and the
# Harpie (873), and the Harpie's walk-cycle phase sheets.
#
# Art-track item 9 (docs/art-track.md contract 9). Douglas, 2026-10-11:
# "generate key poses, derive the rest". This script makes the GENERATED
# half; tools/art/monster_frames.py splits, derives and plates.
#
#   keys    three key-pose candidates per monster. Each candidate is ONE
#           image with four poses in a row (idle, walk, attack, dead), so
#           the four share one creature; monster_frames.py split cuts it.
#           The reference is the donor itself: the ghoul (142) in the four
#           matching poses, facing the viewer (direction 3), at 8x
#           (monster_frames.py refs). For the zombie that is the creature
#           to redraw; for the harpie it pins only the camera, the pixel
#           scale and the shading.
#   walk    the Harpie's flap cycle for one candidate, one sheet per drawn
#           direction (the donor draws 5 of the 8; the other 3 are its
#           mirror images, ANIM.DAT's flip bit). Each sheet is four wing
#           phases of the same body, so a direction's frames come out of
#           one image and stay the same creature. The candidate's key sheet
#           is the character reference and a ghoul walk frame
#           (reference-facing-d<N>.png) the facing cue. Pass the letter:
#               tools/art/gen_monsters.sh walk A
#           The Water Zombie needs no walk generation: its frames are
#           derived from the donor's own (monster_frames.py, ramp transfer).
#
# SAFE TO RE-RUN: an output already on disk is skipped; delete one to
# re-roll it. Every attempt's full output is kept under $LV_GEN_LOGDIR
# (default /tmp/lv-genlogs). READ IT before trusting a file: on a 429
# agy's inner agent has been seen to draw a substitute with PIL and report
# success (the agy-image skill), and only its own words give that away.
# Both routes have walls: Nano Banana answered a 429 after four images on
# 2026-10-11 ("Your quota will reset after 4h42m"), codex after four more
# ("You've hit your usage limit ... try again at 4:05 PM"). A codex log
# echoes the prompt, so the wall check reads only codex's reply. gpt-image-2
# ignores the magenta request and returns real transparency;
# monster_frames.keyed handles both.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
Z=$ROOT/shared/docs/art-poc/water-zombie
H=$ROOT/shared/docs/art-poc/harpie
REF=$Z/reference-ghoul-dir3.png
LOGD="${LV_GEN_LOGDIR:-/tmp/lv-genlogs}"
mkdir -p "$LOGD" "$Z" "$H"

TAIL='Every figure is inside the frame with a margin of background all round, no shadow on the ground, no ground plane, no other objects, no text and no labels anywhere. If image generation fails for any reason (quota exhausted, 429, rate limit, capacity error), report the exact error and STOP. Do NOT create a substitute image by any other means (no procedural generation, no PIL/numpy/matplotlib drawing, no placeholder) — a fabricated image reported as a success is worse than a clear failure.'

# The camera, pinned as geometry (the clauses that fixed the encased gods).
PROJ='Drawn in the fixed camera of Ultima VIII (1994 MS-DOS VGA pixel art): seen from high above at the steep angle of a 2:1 isometric floor tile, so the figure is foreshortened, the top of the head and shoulders are visible and the feet sit close under the body. Single light from the upper left. Hand-dithered pixel shading, matte, muted VGA colours, a dark one-pixel outline like the reference sprites, sharp readable silhouette, no glow, no anti-aliasing against the background.'

# The sheet rule: the splitter cuts on empty magenta columns.
ROW='The image is 1536x512 and shows FOUR SEPARATE FIGURES side by side in one row, all the SAME creature at the SAME size. Between every pair of neighbours there is a clear vertical band of flat magenta background, so no two figures touch or overlap and nothing is shared between them.'

POSES='Left to right: (1) IDLE, standing still; (2) WALK, caught mid-stride; (3) ATTACK, lunging and striking with its arms; (4) DEAD, lying collapsed flat on the ground.'

# Two routes. ROUTE=agy (default) is Nano Banana, which takes the reference
# by path. ROUTE=codex is gpt-image-2 through `codex exec`, the agy-image
# skill's named fallback for a 429 wall; it gets the same references as
# attachments (-i). Both carry the anti-fabrication clause, and both logs
# must be read before a file is trusted.
ROUTE="${ROUTE:-agy}"

run_img () {   # run_img <out> <logname> <body> [reference...]
  local out="$1" log="$2" body="$3" i p
  shift 3
  if [ -s "$out" ]; then echo "SKIP $(basename "$out")"; return 0; fi
  for i in 1 2; do
    echo "=== $(basename "$out") attempt $i ($ROUTE)"
    if [ "$ROUTE" = codex ]; then
      local att=() r
      for r in "$@"; do att+=(-i "$r"); done
      p="Call the built-in Codex image_gen tool (gpt-image-2) directly to generate exactly one image, using the attached image(s) as the reference(s) named below. Save it to: $out
$body"
      printf '%s' "$p" | codex exec --dangerously-bypass-approvals-and-sandbox \
          --cd "$ROOT" "${att[@]}" > "$LOGD/$log.codex.$i.log" 2>&1
      local L="$LOGD/$log.codex.$i.log"
    else
      p="Generate exactly one image with Nano Banana and save it to $out. $body"
      script -q -c "agy --dangerously-skip-permissions -p \"$p\"" /dev/null \
          < /dev/null > "$LOGD/$log.$i.log" 2>&1
      local L="$LOGD/$log.$i.log"
    fi
    if [ -s "$out" ]; then echo "OK   $(basename "$out") — now READ $L"; return 0; fi
    # a codex log opens with the prompt, whose anti-fabrication clause names
    # every wall word: scan only codex's reply and its ERROR lines
    local said
    if [ "$ROUTE" = codex ]; then said=$(sed -n '/^codex$/,$p;/^ERROR:/p' "$L"); else said=$(cat "$L"); fi
    echo "     no file. log: $(grep -oiE 'no image generated|moderation_blocked|safety_violations|quota|429|rate limit|usage (cap|limit)|capacity|refus[a-z]*|synthesi[a-z]*|numpy|PIL' <<< "$said" | sort -u | tr '\n' ' ')"
    grep -qiE 'quota|429|rate limit|usage (cap|limit)|capacity' <<< "$said" && { echo "WALL: stop"; return 1; }
  done
  echo "MISS $(basename "$out")"
}

zombie () {   # zombie <letter> <description>
  run_img "$Z/keys_$1_raw.png" "wzombie_keys_$1" "Use $REF as the reference image: four sprites of one creature from a 1994 game, a shambling ghoul facing the viewer, standing, walking, attacking and lying dead. Redraw the SAME creature in the SAME four poses, the same build, the same proportions and the same camera, as a WATER ZOMBIE that has risen out of a lake: $2 $ROW $POSES $PROJ $TAIL" "$REF"
}

harpie () {   # harpie <letter> <description>
  run_img "$H/keys_$1_raw.png" "harpie_keys_$1" "Use $REF ONLY as a reference for the camera angle, the pixel size and the shading style: it is four sprites of a ghoul from the same 1994 game. Do NOT draw a ghoul. Draw a HARPY, a winged monster that nests on mountain cliffs, facing the viewer: $2 $ROW Left to right: (1) IDLE, hovering low with its wings spread level; (2) WALK, flapping, its wings raised high above its back; (3) ATTACK, lunging at the viewer with both taloned feet thrust forward and wings swept back; (4) DEAD, lying crumpled flat on the ground with one wing spread out. $PROJ $TAIL" "$REF"
}

face_of () {   # face_of <dir>: the facing clause for a drawn direction
  case $1 in
    3) echo 'facing the viewer, its body pointing straight down the screen towards the viewer';;
    4) echo 'facing down and to the LEFT of the screen, three-quarter view, its left side towards us';;
    5) echo 'facing straight to the LEFT of the screen, seen in side profile';;
    6) echo 'facing up and to the LEFT of the screen, away from the viewer, three-quarter back view';;
    7) echo 'facing straight AWAY from the viewer, up the screen, seen from behind';;
  esac
}

sheet () {   # sheet <kind> <letter> <dir> <n figures> <phases>
  local kind="$1" c="$2" d="$3" n="$4" phases="$5" keys="$H/keys_$2_raw.png"
  [ -s "$keys" ] || { echo "no $keys"; return 1; }
  local fref="$H/reference-facing-d$d.png"
  run_img "$H/${kind}_${c}_d${d}_raw.png" "harpie_${kind}_${c}_d${d}" "Use $keys as the character reference: it shows one harpy in four poses. Use $fref only to see which way the figure faces: it is a ghoul sprite from the same game facing that way; do not draw the ghoul. Draw the SAME harpy, same body, same colours, same size, $(face_of "$d"), in $n phases of one movement: The image is 1536x512 and shows $n SEPARATE FIGURES side by side in one row, the same harpy $n times at the same size, facing the same way in all of them. Left to right: $phases Between every pair of neighbours there is a clear vertical band of flat magenta background so no two figures touch. $PROJ $TAIL" "$keys" "$fref"
}

walk () {   # walk <letter>: five direction sheets of four wing phases
  local d
  for d in 3 4 5 6 7; do
    sheet walk "$1" "$d" FOUR "(1) wings raised high above its back; (2) wings sweeping down, level with its shoulders; (3) wings fully down below its body; (4) wings coming back up, half raised. It flies low; its body, head and legs stay in the same place and at the same height above the ground in all four; only the wings move." || return 1
  done
}

# The torax's attack (ANIM.DAT action 7) is 7 frames per direction with its
# hit window on frames 3-5 (attack_range 1, 2, 1); monster_frames.py
# sequences these five phases as 0 1 2 3 3 2 4, so the strike (phase 3)
# is what lands. Phase 0 is also the combat stance and the idle.
attack () {   # attack <letter>: five direction sheets of five phases
  local d
  for d in 3 4 5 6 7; do
    sheet attack "$1" "$d" FIVE "(1) hovering low, ready, wings half spread; (2) rearing back, wings raised high, legs drawn up under the body; (3) lunging forward and down, wings sweeping back; (4) the strike: both taloned feet thrust out in front at full reach, wings swept back; (5) recovering, wings level, legs coming back under the body." || return 1
  done
}

# The torax's death (action 14) is 8 frames in two views, 211-218 (drawn for
# direction 3, mirrored or reused for 1, 2, 4, 5) and 231-238 (direction 7,
# reused for 6 and mirrored for 0); standUp plays it backwards. Five phases,
# sequenced 0 1 1 2 2 3 4 4.
die () {   # die <letter>: two sheets of five phases
  local d
  for d in 3 7; do
    sheet die "$1" "$d" FIVE "(1) struck in mid-air, recoiling, wings flung up; (2) falling, wings crumpling; (3) dropping to the ground, wings folding over its body; (4) hitting the ground, one wing spread out; (5) lying dead and still on the ground, crumpled, one wing spread flat." || return 1
  done
}

case "${1:-keys}" in
  keys)
    zombie A 'a drowned corpse, its skin bloated, waterlogged and pale blue-grey with a cold green cast, wearing rags of dark sodden cloth, strands of dark green lake weed hanging from its shoulders and arms, water dripping from its hands, pale empty eyes.' || exit 1
    zombie B 'its whole body half-wrapped in ropes of olive-green and brown lake weed and algae, its skin mossy olive-green mottled with darker slime, its rags almost hidden under the weed, weed trailing from its arms.' || exit 1
    zombie C 'gaunt and bone-pale, its waterlogged white-grey skin stretched over visible ribs, tattered teal-black cloth at the hips, small grey shells and barnacles crusted on its shoulders and shins, a blue-green tide-line stain up its legs.' || exit 1
    harpie A 'a classic harpy: the head and torso of a fierce woman with wild dark hair, arms that are broad brown-grey feathered wings, a ragged brown feathered lower body and scaly bird legs ending in yellow talons.' || exit 1
    harpie B 'a vulture-like hag: a withered grey-skinned old woman face with a hooked nose and a nearly bald scalp, her body covered in black feathers with a ruff at the neck, broad ragged black-brown vulture wings, scaly grey legs with long hooked talons.' || exit 1
    harpie C 'a storm-grey harpy that matches the cliff rock: a woman head with long black hair and pale skin, her body covered in slate-grey and blue-grey feathers streaked with white, wide grey wings, dark talons.' || exit 1
    ;;
  walk) walk "${2:?candidate letter}" ;;
  attack) attack "${2:?candidate letter}" ;;
  die) die "${2:?candidate letter}" ;;
  *) echo "usage: $0 [keys | walk|attack|die <A|B|C>]"; exit 2 ;;
esac
ls -la "$Z"/*_raw.png "$H"/*_raw.png 2>/dev/null
