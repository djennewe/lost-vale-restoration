#!/usr/bin/env python3
"""
test_vignettes.py — the published 1994 screenshots stay in the build.

Each of the 19 published Lost Vale screenshots is reconstructed as a
vignette (vignettes/screenNN.json) and stamped into its map
(docs/research/2026-10-16-screenshot-reconstruction.md). This test paints
every shot's window from the BUILT FIXED.DAT, U8SHAPES.FLX and TYPEFLAG.DAT
in the engine's draw order, with the shot's retail actors at their recorded
spots (vignette_built_window.window), and holds two things per shot:

  1. the palette-class match against the 1994 GIF stays at or above its
     floor: the score recorded when the shot entered the build, less 0.25
     points of slack for an incidental neighbour. A builder change that
     lets generated terrain paint into a known view, drops a shot's item,
     or moves a shot fails here even when every other test passes;
  2. nothing is unpainted inside the window where the 1994 shot is not
     black (a void hole in a known view), beyond the few pixels each shot
     already leaves at its frame edges.

A built window can score above its reconstruction's replay: the replay
counts the shot's black void as matched only where nothing paints, and the
builders close some of that with ground the shot shows.

The floors are this table; raise one when a shot genuinely improves.
Scores in-engine (tools/playtest-linux/vignette_capture.py) run a few points
lower than these because ScummVM places no vignette actors where the shot
has them and animates water, lava and foam: ingame/SCORES.md.
"""

import os
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC)

from vignette_built_window import window     # noqa: E402
from vignette_paint import Painter           # noqa: E402

SLACK = 0.25

# shot: (class score when it entered the build, unpainted px allowed where
# the shot is not black). Recorded 2026-10-17 on FIXED.DAT 1482caca;
# screen01 re-recorded the same day on 8db11ee3 after its black sliver and
# left-edge wedge were filled (verify3 4b: the corner post 29:7 in the
# vignette, build_map_13.WINDOW_FILLS and UNFACED_BY_HAND). screen07, 12
# and 13 re-recorded 2026-10-25 (phase D, the 1994 art 882-886 and the
# completed Pillar of Fire, 865 f2): 87.41 -> 91.20, 87.41 -> 97.94,
# 75.97 -> 95.88. screen02, 09, 19 and 20 re-recorded 2026-10-25 when
# their 1994 actors became built shapes painted at their solved spots
# (872, 888-890, lv_actor_art.py): 95.96 -> 98.40, 93.75 -> 94.84,
# 95.85 -> 97.08, 95.69 -> 97.70. screen13 re-recorded 2026-10-30
# (cloud13: the cloud floats over the tree, the mushrooms and the spires'
# feet, build_map_13.FLOATING): 95.88 -> 98.91. screen07 re-recorded
# 2026-10-30 (phase E: the notch filled, the cliff run on, 891/892's 1994
# faces and floor): 91.20 -> 97.27.
FLOORS = {
    'screen01': (95.35, 49),
    'screen02': (98.40, 0),
    'screen04': (98.89, 0),
    'screen05': (94.55, 0),
    'screen07': (97.27, 6),
    'screen09': (94.84, 148),
    'screen10': (89.52, 794),
    'screen11': (99.93, 0),
    'screen12': (97.94, 0),
    'screen13': (98.91, 0),
    'screen14': (89.86, 3),
    'screen15': (95.98, 495),
    'screen16': (94.59, 240),
    'screen17': (93.69, 59),
    'screen18': (98.58, 55),
    'screen19': (97.08, 0),
    'screen20': (97.70, 0),
    'screen21': (93.53, 540),
    'screen22': (97.26, 0),
}

passed = failed = 0


def check(name, ok, detail=''):
    global passed, failed
    if ok:
        passed += 1
        print(f'  PASS  {name}')
    else:
        failed += 1
        print(f'  FAIL  {name}  {detail}')


def main():
    print('=' * 70)
    print('The 1994 screenshots in the built maps')
    vig_dir = os.path.join(SRC, 'vignettes')
    shots = sorted(f[:-5] for f in os.listdir(vig_dir)
                   if f.startswith('screen') and f.endswith('.json'))
    check('every reconstructed shot has a floor', set(shots) == set(FLOORS),
          f'no floor for {sorted(set(shots) - set(FLOORS))}, '
          f'floor without a shot {sorted(set(FLOORS) - set(shots))}')
    painter = Painter.built()
    for shot in sorted(FLOORS):
        floor, holes = FLOORS[shot]
        out, rgb, _, cls = window(shot, actors=True, painter=painter)
        check(f'{shot}: class {cls:.2f}% >= floor {floor - SLACK:.2f}%',
              cls >= floor - SLACK)
        unpainted = int(((out < 0) & (rgb.sum(-1) > 12)).sum())
        check(f'{shot}: {unpainted} unpainted non-black px <= {holes}',
              unpainted <= holes)
    print()
    print('=' * 70)
    print(('OK' if not failed else 'FAILED') + f': {passed} passed, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
