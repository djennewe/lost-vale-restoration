#!/bin/bash
# tools/art/gen_wake_inbetweens.sh — the twelve wake in-between poses.
#
# Four per god, so shape 860's wake is six DRAWN poses (released, mid1..mid4,
# standing) and never a blend. It cannot be a blend: the U8 shape format has
# no alpha, so a cross-dissolve is composited against the magenta key and
# comes back pink.
#
# SAFE TO RE-RUN. Every pose already on disk is skipped, so this is the one
# command that finishes the set however many attempts it takes.
#
# After it, recomposite and rebuild:
#
#   python3 agents/map-populator/src/lv_god_frames.py
#   tools/integrate.sh --record
#
# TWO WAYS THIS FAILS, AND THEY NEED DIFFERENT RESPONSES:
#
#   "no image generated in response", no file written — a CONTENT refusal on
#   that particular pose. Not deterministic: the same prompt shape produced
#   timyra_mid1 and all three standing poses first time and was refused three
#   times running for timyra_mid2/3/4. This script retries three times and
#   rewords on the third. If a pose still will not come, leave it out — a god
#   with fewer in-betweens is a steppier wake, not a broken one.
#
#   HTTP 429 with a quotaResetTimeStamp — a wall. Stop; do not loop. On
#   2026-09-14 it was a three-and-a-half hour reset, and the alternate route
#   (codex / gpt-image-2) is no help: it returns moderation_blocked,
#   safety_violations=[sexual] for this subject, including for Doloras, who
#   is clothed.
#
# Each attempt's full output is kept in $LV_GEN_LOGDIR (default /tmp/lv-genlogs)
# so the two can be told apart afterwards. An earlier version filtered agy's
# stdout out of the log and neither could be diagnosed.
set -u
A="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/shared/docs/art-poc/gods"
W=$A/wake
LOGD="${LV_GEN_LOGDIR:-/tmp/lv-genlogs}"
mkdir -p "$LOGD"

TAIL='Whole figure inside the frame with a margin of background all round, no shadow on the ground, no other objects. If image generation fails for any reason (quota exhausted, 429, rate limit, capacity error), report the exact error and STOP. Do NOT create a substitute image by any other means (no procedural generation, no PIL/numpy/matplotlib drawing, no placeholder) — a fabricated image reported as a success is worse than a clear failure.'

FEMALE='one full-body female figure made of matte dark bronze, smooth and unbroken like a cast figurine with no clothing and no anatomical detail, lit from the upper left, matte and dithered rather than glossy.'
MALE='one full-body bald male figure made of matte dark bronze, smooth and unbroken like a cast figurine, wearing only a plain cloth wrap at the hips, lit from the upper left, matte and dithered rather than glossy.'

gen () {   # gen <outfile> <reference> <body> <pose> [alt-pose]
  local out="$1" ref="$2" body="$3" pose="$4" alt="${5:-}"
  local base; base=$(basename "$out" .png)
  if [ -s "$out" ]; then echo "SKIP $base"; return 0; fi
  local i txt
  for i in 1 2 3; do
    txt="$pose"
    [ "$i" = 3 ] && [ -n "$alt" ] && txt="$alt"
    local p="Generate exactly one image with Nano Banana and save it to $out. Use $ref as the character reference — the SAME figure, same proportions, same material, same lighting, redrawn in a different pose. Image description: a 1024x1024 image on a completely flat pure magenta #FF00FF background, showing $body $txt $TAIL"
    echo "=== $base attempt $i"
    script -q -c "agy --dangerously-skip-permissions -p \"$p\"" /dev/null \
        < /dev/null > "$LOGD/$base.$i.log" 2>&1
    if [ -s "$out" ]; then echo "OK   $base (attempt $i)"; return 0; fi
    echo "     no file. agy: $(grep -oiE 'no image generated|quota|429|rate limit|capacity|refus[a-z]*' "$LOGD/$base.$i.log" | sort -u | tr '\n' ' ')"
  done
  echo "MISS $base after 3 attempts"
}

REL_T=$A/freed/timyra_final_raw.png
STD_T=$W/timyra_stand_raw.png
gen "$W/timyra_mid1_raw.png" "$REL_T" "$FEMALE" 'She is beginning to recover from fright. Still turned to her right with knees bent, but her hands have come down from her face to chest height and her head is starting to lift.'
gen "$W/timyra_mid2_raw.png" "$REL_T" "$FEMALE" 'She is straightening. Her hands have lowered to waist height, her knees are only slightly bent, and her body has begun turning from her right towards the viewer.' 'Caught mid-movement as she straightens up out of a frightened crouch, her arms coming down and her shoulders opening, still angled to her right.'
gen "$W/timyra_mid3_raw.png" "$STD_T" "$FEMALE" 'She is almost upright and almost front-on to the viewer, knees nearly straight, arms hanging nearly at her sides, head coming up but not yet level.' 'Caught a moment before she comes to rest: nearly upright, nearly square to the viewer, her head still rising.'
gen "$W/timyra_mid4_raw.png" "$STD_T" "$FEMALE" 'She stands upright and square to the viewer, arms at her sides, head level — an instant before coming fully to rest, shoulders still settling.' 'Standing calmly and facing the viewer, one instant before she is completely still.'

REL_F=$A/freed/felicitar_final_raw.png
STD_F=$W/felicitar_stand_raw.png
gen "$W/felicitar_mid1_raw.png" "$REL_F" "$FEMALE" 'Her raised arms have come down to shoulder height and are still spread wide, elbows soft, head tipped back a little less than before.'
gen "$W/felicitar_mid2_raw.png" "$REL_F" "$FEMALE" 'Her arms have lowered to chest height and drawn in closer to her body, head coming level, body square to the viewer.' 'Caught mid-movement as her arms come down out of a triumphant reach, head levelling, facing the viewer.'
gen "$W/felicitar_mid3_raw.png" "$STD_F" "$FEMALE" 'Her arms are near her hips and still slightly away from her body, head level, standing upright and front-on to the viewer.' 'Caught a moment before she comes to rest: upright and square to the viewer, her arms still settling.'
gen "$W/felicitar_mid4_raw.png" "$STD_F" "$FEMALE" 'She stands upright and square to the viewer, arms almost at her sides with the hands just barely lifted — an instant before coming fully to rest.' 'Standing calmly and facing the viewer, one instant before she is completely still.'

REL_D=$A/freed/doloras_final_raw.png
STD_D=$W/doloras_stand_raw.png
gen "$W/doloras_mid1_raw.png" "$REL_D" "$MALE" 'He is still kneeling and folded forward over his knees, but his back has begun to straighten and his head is lifting from his chest.'
gen "$W/doloras_mid2_raw.png" "$REL_D" "$MALE" 'He has risen onto one knee, the other foot flat on the ground, one hand resting on the raised knee, back upright, head up.'
gen "$W/doloras_mid3_raw.png" "$STD_D" "$MALE" 'He is pushing up onto both feet from the kneel — legs mostly straightened but still in a slight crouch, torso upright, arms hanging loose, head up and facing the viewer.'
gen "$W/doloras_mid4_raw.png" "$STD_D" "$MALE" 'He stands fully upright and square to the viewer, arms almost at his sides — an instant before coming fully to rest, shoulders still settling.'

echo "ALL DONE: $(ls "$W" | grep -c mid)/12"
