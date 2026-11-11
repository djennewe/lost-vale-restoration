# In-engine captures, 2026-10-17 (all 19 shots)

These captures come from `tools/playtest-linux/vignette_capture.py`, run on
the build in `ARTIFACTS.sha256` (FIXED.DAT 1482caca…), with a fresh ScummVM
session for each shot. Each session:

1. teleports the Avatar to the shot's Avatar spot (screen13 shows no Avatar,
   so its session uses the window's ground centre);
2. captures the 640×400 game surface;
3. aligns the 1994 frame inside it by palette class.

Scores are all-frame percentages. The "Replay class" column is the
reconstruction's own score from `vignette_replay.py`, the ceiling an exact
build can reach.

| Shot | Map | Frame at | Class | RGB ≤12 | Replay class |
|---|---|---|---|---|---|
| screen01 | 13 | +168,+101 | 91.63 | 91.59 | 94.09 |
| screen02 | 10 | +166,+128 | 91.26 | 89.05 | 96.04 |
| screen04 | 18 | +106,+50 | 95.26 | 94.62 | 99.91 |
| screen05 | 11 | +178,+36 | 86.35 | 86.24 | 83.30 |
| screen07 | 11 | +172,+102 | 86.06 | 85.97 | 86.94 |
| screen09 | 10 | +242,+104 | 82.65 | 81.79 | 93.68 |
| screen10 | 9 | +164,+137 | 88.11 | 88.09 | 86.98 |
| screen11 | 17 | +284,+94 | **98.24** | 98.21 | 99.93 |
| screen12 | 17 | +116,+104 | 85.90 | 85.89 | 87.41 |
| screen13 | 13 | +179,+129 | 75.97 | 75.57 | 75.97 |
| screen14 | 13 | +177,+67 | 83.96 | 83.76 | 89.44 |
| screen15 | 13 | +186,+100 | 91.27 | 89.33 | 95.93 |
| screen16 | 13 | +181,+87 | 93.13 | 91.95 | 94.27 |
| screen17 | 10 | +130,+128 | 92.45 | 92.43 | 92.77 |
| screen18 | 10 | +175,+103 | 94.66 | 94.48 | 98.40 |
| screen19 | 10 | +190,+95 | 94.46 | 90.92 | 96.07 |
| screen20 | 10 | +217,+101 | 90.83 | 89.87 | 95.44 |
| screen21 | 10 | +188,+113 | 86.96 | 84.65 | 93.29 |
| screen22 | 10 | +187,+79 | 95.75 | 93.36 | 96.70 |

The gap between an in-engine score and the replay is not map content. It
comes from:

- **1994-only actors that the engine does not place:** Water Zombies,
  villagers, the daemon, the robed figure and the eye-serpent.
- **The Avatar's pose and facing.**
- **The Shield in screen04.** The shot shows the ceremony moment; the Shield
  reaches the altar only during the ceremony.
- **Animated water, lava and foam.** screen09's waterfall loses the most.
- **A grey ghost that follows the Avatar.** This is retail GHOST 411, which
  `AVATAR.UNK` pops after the first map switch. It is in every fresh
  session, and it predates this work.

On map content alone, the offline painter (`vignette_built_window.py`) and
these captures differ on 0.3–4.6% of a window's pixels, and on 12% for
screen09.
