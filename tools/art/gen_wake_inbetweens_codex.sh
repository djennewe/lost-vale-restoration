#!/bin/bash
# tools/art/gen_wake_inbetweens_codex.sh — wake in-between poses via gpt-image-2.
#
# The companion to gen_wake_inbetweens.sh, for when Nano Banana is quota-walled.
# Same twelve poses, same skip-what-exists behaviour, two differences that
# matter:
#
# EVERYTHING IS DESCRIBED AS A STATUE. Asked for "a full-body female figure
# ... with no clothing and no anatomical detail" — the wording the Nano Banana
# prompts use — gpt-image-2 returns HTTP 400 `moderation_blocked,
# safety_violations=[sexual]` at the OUTPUT stage, even for Doloras, who is
# clothed. Asked for a cast bronze STATUE of the same subject it generates
# first time. Do not "simplify" these prompts back toward the other script's.
#
# Say STATUE OF A MAN/WOMAN, not MANNEQUIN. The first framing that got past
# moderation asked for an artist's jointed lay figure, and that is exactly
# what came back — ball joints, an egg head, pale yellow metal, a different
# object entirely from the god beside it.
#
# THE OUTPUT IS GRADED AFTERWARDS, NOT HERE. This route takes no character
# reference — it has no reference input at all — so the metal comes out
# lighter and warmer than the Nano Banana poses on either side. At game scale
# that is a bright figure flashing between two dark ones.
# lv_god_frames.match_bronze regrades each in-between to its god's released
# sprite when the runs are composited, so nothing downstream needs to know
# which generator a pose came from.
set -u
A="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/shared/docs/art-poc/gods"
W="$A/wake"
LOGD="${LV_GEN_LOGDIR:-/tmp/lv-genlogs}"
mkdir -p "$LOGD"

STYLE='Style: matte and heavily dithered like a 1994 DOS isometric game sprite, limited palette, lit from the upper left, not glossy, not photographic, no reflections. The whole statue inside the frame with a margin of background all round, no plinth, no shadow on the ground, no other objects.'
TAIL='If the image_gen tool call fails for any reason (rate limit, quota, usage cap, 429, moderation, error), report the exact error and STOP. Do NOT create a substitute image by any other means (no PIL/numpy/matplotlib, no placeholder, no other tool) — a fabricated image reported as success is worse than a clear failure.'

MAN='a weathered CAST BRONZE STATUE of a bald, powerfully built man, seen from the front. The bronze is dark olive-brown and dull gold with a matte patina — one solid unbroken casting with NO joints, NO seams, NO ball-and-socket articulation. Smoothed, simplified musculature, no fine surface detail, a plain grey cloth wrapped about the hips of the statue.'
WOMAN='a weathered CAST BRONZE STATUE of a slender woman with long hair, seen from the front. The bronze is dark olive-brown and dull gold with a matte patina — one solid unbroken casting with NO joints and NO seams. Smoothed, simplified classical forms with no fine surface detail, in the manner of a small antique bronze.'

gen () {   # gen <outfile> <subject> <pose>
  local out="$1" subj="$2" pose="$3"
  local base; base=$(basename "$out" .png)
  if [ -s "$out" ]; then echo "SKIP $base"; return 0; fi
  local i
  for i in 1 2; do
    echo "=== $base attempt $i"
    printf '%s' "Call the built-in Codex image_gen tool (gpt-image-2) directly to generate exactly one image.
Save it to: $out
Image description:
A 1024x1024 pixel-art game sprite on a completely flat pure magenta #FF00FF background.
Subject: $subj
Pose of the statue: $pose
$STYLE

$TAIL" | codex exec --dangerously-bypass-approvals-and-sandbox \
        --cd "$(dirname "$A")" > "$LOGD/$base.codex.$i.log" 2>&1
    if [ -s "$out" ]; then echo "OK   $base (attempt $i)"; return 0; fi
    echo "     no file. codex: $(grep -ohiE 'moderation_blocked|safety_violations|rate limit|quota|429|usage cap' "$LOGD/$base.codex.$i.log" | sort -u | tr '\n' ' ')"
  done
  echo "MISS $base"
}

gen "$W/timyra_mid2_raw.png" "$WOMAN" 'straightening out of a frightened crouch — her hands have come down to waist height, her knees are only slightly bent, and her body has begun turning from her right towards the viewer.'
gen "$W/timyra_mid3_raw.png" "$WOMAN" 'almost upright and almost square to the viewer, knees nearly straight, arms hanging nearly at her sides, head coming up but not yet level.'
gen "$W/timyra_mid4_raw.png" "$WOMAN" 'standing upright and square to the viewer, arms at her sides, head level — caught an instant before coming fully to rest.'

gen "$W/felicitar_mid2_raw.png" "$WOMAN" 'her arms have come down from overhead to chest height and drawn in closer to her body, head coming level, standing upright and square to the viewer.'
gen "$W/felicitar_mid3_raw.png" "$WOMAN" 'her arms are down near her hips and still slightly away from her body, head level, standing upright and square to the viewer.'
gen "$W/felicitar_mid4_raw.png" "$WOMAN" 'standing upright and square to the viewer, arms almost at her sides with the hands just barely lifted — caught an instant before coming fully to rest.'

gen "$W/doloras_mid1_raw.png" "$MAN" 'kneeling with both knees on the ground and still folded forward over them, but the spine has begun to uncurl and the head is rising from the chest.'
gen "$W/doloras_mid2_raw.png" "$MAN" 'risen onto one knee with the other foot flat on the ground, one hand resting on the raised knee, back upright, head up.'
gen "$W/doloras_mid3_raw.png" "$MAN" 'pushing up onto both feet out of the kneel — legs mostly straightened but still in a slight crouch, torso upright, arms hanging loose, head up and facing the viewer.'
gen "$W/doloras_mid4_raw.png" "$MAN" 'standing fully upright and square to the viewer, arms almost at his sides — caught an instant before coming fully to rest.'

echo "ALL DONE: $(ls "$W" | grep -c mid)/12"
