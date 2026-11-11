# Phase E, actorfix: the elder's cane and SE talk, the children's outline and spears (2026-10-30)

Douglas's art review (2026-10-30), cards 6 and 7, asked for four things:

- **888, the elder:** redraw Mythran's tall knobbed staff as screen20's short cane in every
  direction and action.
- **888, the elder:** give the SE talk (70-72) some movement, with one frame kept as the
  exact screen19 pose.
- **889/890, the children:** drop the black outline.
- **889/890, the children:** put the spear in the hand, with the screen20 pose kept
  index-exact.

No new shape IDs. Only `U8SHAPES.FLX` changes, from `f64cbfd8…` to `12d9e0a0…`.
EUSECODE is unchanged (`b47c324c`, the same as main).

## What changed (`agents/map-populator/src/lv_actor_art.py`)

### 888: the cane in every frame

The rule comes from screen20's cane, which runs from the hand down to the ground:
cut-out rows 22-40, 19 px, with nothing above the hand. Every Mythran frame the table
shows (122 frames) is cut back by this rule:

- `ELDER_STAFF` gives the staff line per frame as knob end K, grip G and far end F, in the
  donor's pixels.
  - The points come from a line fit through each frame's thin protruding pixels and its
    knob colours, with the grip at the skin pixels on that line.
  - 52, 53, 66, 67, 247 and 253 were placed by hand.
- `_cane` removes the staff from the hand up, knob included.
  - A removed pixel with body on both sides of the line takes the body pixel beside it.
  - Any other removed pixel becomes transparent, and the body edge it bares takes the
    outline.
  - Leftover outline spurs are dropped.
- **Walk, stand, talk and cast frames:** the cane is the staff from the hand to the
  ground, 19-34 px.
- **Attacks (230-300):** the cane keeps whichever side of the hand shows more staff, and
  is capped at `CANE_LEN` = 25 px from the hand. This means the thrusts strike with the
  cane.
- 300, 332 and 333 show no staff to cut.

### 888: the SE talk (`talk_gesture`)

Mythran's table plays 70,71,72,70,71,70,71,72,71,70.

- **71** is the screen19 cut-out, index for index, plus `ELDER_TALK_CANE`: 26 px of cane
  in screen20's ramp.
  - The cane leans from just under the outstretched hand to the ground.
  - Every one of those pixels is one the shot's Avatar covers (shape 1 frame 11, hotspot
    (130,124)).
  - The cane could not go straight down. The shot shows ground at (0..2, 28..30) and at
    the foot. A first, straight version cost 11 px of screen19 and was dropped.
- **70 and 72** turn the forearm, hand and cane about the elbow: 70 by −6°, 72 by +18°.
  - 72 lifts and points the cane.
  - The bared robe edge is drawn from the robe beside it.

### 889/890: no outline (`_unoutline`)

Each silhouette-edge index-0 pixel that the `'outline'` scale draws takes the commonest
colour of its inner neighbours.

- Index 0 on silhouette edges went from 4122 of 4738 edge pixels (87%) to 215 of 4915
  (889) and 133 of 4915 (890).
- What stays black is the 1-px strands, as the shot's cloak strands are.

### 889/890: the spear held (`_paint_spear`)

- **Grip:** the right hand, found per frame. It is the outermost silhouette pixel on the
  hand's side, 36-56% down the figure, one pixel out. The shot's hand colour 173 is
  painted over the shaft there.
- **Angle:** one 3-D direction read off screen20, projected per facing.
  - The tip runs 11.3 forward and 1 up; the butt runs 21.2 back and 3.5 down.
  - So N repeats the shot's angle mirrored, NE holds the spear level, and E points it
    forward-down.
  - SE (toward the camera) and NW (away from it) foreshorten it to an upright stick at
    the side.
- **Front or behind:** set by `SPEAR_FRONT`. The end toward the camera passes in front of
  the body (E/SE the tip, NW the butt). N and NE keep the shot's arrangement, with the
  butt behind the body.
- The death frames 45-74 have no spear.

## Images (this folder)

- `phaseE-actorfix-contact.png` has these rows:
  - the 1994 crops;
  - the shot frames before | after (888: 60, 70-72; 889: 0-4);
  - **every changed frame, before | after:** 140 for 888 (the 122 cut frames, 70-72, and
    the stand copies at 90-102, 110, 136, 160, 185), and 74 each for 889 and 890.
- Animated GIFs, all 8 directions side by side (N, NE, E, SE, S, SW, W, NW), each with a
  `-before` twin where one was made:
  - `elder-888-walk-8dirs.gif`
  - `elder-888-talk-8dirs.gif` (SE is the 4th)
  - `child-889-walk-8dirs.gif`
  - `child-890-walk-8dirs.gif`
- `ingame/`: the vignette captures and the plates (see below).

## Scores

| | before | after |
|---|---|---|
| `vignette_built_window --actors` screen19 | 97.07 / class 97.09 | 97.07 / 97.09 |
| `vignette_built_window --actors` screen20 | 97.70 / 97.70 | 97.70 / 97.70 |
| `vignette_replay --built` screen19 (class) | 97.261 | 97.261 (published render identical) |
| `vignette_replay --built` screen20 (class) | 97.444 | 97.444 (identical) |
| `vignette_replay --built` screen02 / 09 | 98.481 / 94.774 | 98.481 / 94.774 (identical) |
| in-engine `vignette_capture` screen19 (class) | 91.67 | 94.42 |
| in-engine `vignette_capture` screen20 (class) | 93.07 | 93.22 |

The shot frames are pixel-identical where the shots can see them, so the offline numbers
do not move. `test_vignettes` floors are unchanged.

The in-engine spread comes from NPC loiter positions, not from art: Atli and the children
are never at their shot spots in play. Both columns were run on pinned copies
(`/tmp/claude-1000/actorfix/game` and `game_b`), on display :98, with the console binary.

## Tests (run in the worktree)

- `tools/build_artifacts.sh --record` was run; only U8SHAPES changed.
- `test_lv_monsters.py`: 81 passed, 0 failed. New checks in 2c:
  - 71 is the cut-out plus only `ELDER_TALK_CANE`;
  - 70 and 72 move, and keep the body;
  - no knob survives in the 122 cut frames;
  - the cane below the hand is kept;
  - every shown Mythran frame is cut or replaced;
  - the children's outline is under 6%;
  - every upright child frame holds its spear.
- `tools/run_all_tests.sh`: 53/54 pass. The one failure is `test_integration_state.py`'s
  "install target holds the canonical bytes" check. The worktree's `shared/data/u8-install`
  is a symlink to main's install, which still holds the old U8SHAPES. That is expected
  until the parent integrates (`tools/integrate.sh`).

## In-engine

Setup:

- the pinned copy of main's `u8-lv-patched` with this build's artifacts synced in
  (U8SHAPES md5 `515b501a…`);
- display :98;
- a private copy of `session.sh`, with its `pkill` narrowed to this session's `CMDS`;
- cheats on, teleported to Map 10 (20250,8150,0).

What was captured:

- **`ingame/screen{19,20}_ingame_{before,after}.png`:** the `vignette_capture` plates
  behind the scores above.
- **`ingame/plates/*.gif`:** per-side bursts. Atli was held 176 units out on each side,
  then given `Actor::talk`; the children were held on each side and left to walk off.
  - The children draw whole, walking with the spear held at the hand.
  - Atli draws whole with the short cane. No staff or knob is seen.

**Not done:**

- **A clean plate of Atli talking SE.** Of the first driver's 8 talk bursts, only W
  survived: the console replies lagged behind the commands, and `Actor::talk` parks the
  camera where the conversation ends. The dedicated SE run (Atli held NW, then talk)
  found him "not an actor" when the hold was sent, so he was never in its frames.
- **What stands in for it:** the SE talk motion is shown offline in
  `elder-888-talk-8dirs.gif` (4th figure) and on the contact sheet. The frames are
  index-checked by `test_lv_monsters`.
- **What the next run needs:** the SE talk plate needs a session that waits for npc 107
  to load before the `Actor::hold`.

## For Douglas

1. **The talk cane leans.** In screen19 the cane cannot hang straight under the hand: the
   shot shows ground there. It leans out behind the Avatar's position instead, and starts
   one pixel off the hand. 71's own cut-out pixels are all unchanged; only hidden pixels
   are added. If he wants 71 to be the bare cut-out with no added pixels at all, the cost
   is the cane vanishing during the SE talk.
2. **The back-view cane is longer.** Mythran holds the staff at shoulder height in the back
   view (0-11), so the cane there runs 24-34 px rather than screen20's 19-21.
3. **The attack frames** (230-300) swing a 25-px cane. In a few back-view sweeps (232-237)
   the cane is mostly hidden behind the shoulders.
4. **The children's spear angle** follows the shot's 3-D direction in every facing. Facing
   SE (toward the camera) it foreshortens to a short upright stick. The shaft is the
   tunic's own grey ramp (25/26), as in the shot, so it reads faintly where it crosses the
   tunic.
5. `vignettes/screen19.json`'s note still says frame 71 is "registry 2041:0 index for
   index". That remains true of every cut-out pixel; the frame also carries the hidden
   cane.
