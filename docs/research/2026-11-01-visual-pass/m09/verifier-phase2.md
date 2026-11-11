# Phase two independent verification

The verifier independently read `/tmp/vq2-m09-before-FIXED.DAT` and `/tmp/vq2-m09-phase2-candidate.DAT`.

Exact flood sets match at 5,908 world XYZ cells. `walk_off` outputs match: zero falls, 90 inherited teeter records, zero void, and zero off-map records.

Screen10 class score stays 89.51725310215876%, with 794 total unpainted pixels and zero unpainted nonblack pixels.

Per-leg failing-cell counts fall from 71/54/19 to 46/28/19. Overlap between bands means the union is smaller. Remaining worst-pose occluders:

- Hall `(13599,15327,0)`: 2.965% visible, chiefly ground course 26 at `(13696,15359,0)`, 692 covered actor pixels.
- Worked end `(14303,16671,0)`: 35.176%, chiefly south wall 15 at `(14591,16895,40)`, 437 pixels.
- Guardian `(13951,13087,0)`: 0%, chiefly shell 30 at `(14079,13247,48)`, 448 pixels.
- Trigger-adjacent `(13727,11935,0)`: 33.387%, chiefly 28 at `(13887,12031,48)`, 294 pixels.
- Guardian `(13855,12863,0)`: 27.628%, chiefly screen10 prop 411:14 at `(13919,12959,0)`, 537 pixels.

No replacement-location defect found. Step-128 frame mean and p95 rise slightly in phase two; phase three must recover those pins. Full estate and in-engine captures remain parent work.
