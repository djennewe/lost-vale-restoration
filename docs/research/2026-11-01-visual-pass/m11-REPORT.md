# Map 11 visual-quality pass, phases 2 and 3

VQ-020 and VQ-065 are fixed. VQ-035, VQ-038, VQ-043, and VQ-045 are improved, with protected-window filler tails still visible. Quest-band failures fell from 191 to zero, and all six specified black floor cells are repaired. The strict visual test passes. Decorative water D6 and finer background clipping require art-track changes outside this slice’s owned files.

Branch: `wt/vq2-m11`, based on `ba34836`. Phase 2: `cf37c51`. Phase 3: `8bab422`. Work began on 3 November 2026, America/Chicago.

## Measurements

Visibility distributions use 1,979 map cells at step 256 and 8,534 at step 128. Quest bands contain 4,213 cells. The permanent frame distribution uses 437 cameras; each frame contains 256,000 pixels. Minimum visibility is the visible share of opaque Avatar pixels in the worst of 72 poses. Screen05 compares 59,334 pixel classes and screen07 compares 59,520; their acceptance floors are 94.30% and 97.02%, respectively.

| Metric | Before (`ba34836`) | Phase 2 | Phase 3 |
|---|---:|---:|---:|
| Specified or unpainted floor cells | 6 | 6 | 0 |
| Prop-pixel black cells | 165 | 165 | 165 |
| Quest-band cells below 50% | 191 | 9 | 0 |
| Map cells below 50%, step 256 | 11.824% | 10.460% | 10.460% |
| Map cells completely hidden, step 256 | 0.606% | 0.404% | 0.404% |
| Frame black mean, step 512 | 5.297% | 5.344% | 0.312% |
| Frame black p95, step 512 | 21.982% | 23.357% | 1.096% |
| Frame black max, step 512 | 36.041% | 36.041% | 8.102% |
| Raw records | 9,515 | 9,766 | 9,872 |
| Expanded records | 17,825 | 18,076 | 18,182 |

The 128-unit report distributions are measured independently of the permanent test grids:

| Step-128 metric | Before | Phase 2 | Phase 3 |
|---|---:|---:|---:|
| Cells below 50% | 12.093% | 10.816% | 10.816% |
| Cells completely hidden | 5.191% | 4.582% | 4.582% |
| Frame black mean | 8.303% | 8.286% | 0.394% |
| Frame black p95 | 36.039% | 35.063% | 2.755% |
| Frame black max | 56.500% | 56.500% | 12.671% |

All three floods reach exactly 140,466 cells. Phase 2 wall lowering gains zero cells and loses zero cells. Phase 3 moves two ambient rocks: 41 cells become blocked at their new footprints and 41 become reachable at their old footprints, all at z 0. The Earth change comprises a five-by-five cell block and the Water change a four-by-four block. These are the complete geometry changes. Both comparisons retain zero falls, 41 teeter entries, zero void exits, and zero off-map exits. Ground backfill and crest projection alone preserve the full reach set, as recorded in [ground-only-geometry.json](m11/ground-only-geometry.json). Final geometry uses the immutable phase-2 TYPEFLAG bytes. [Phase-2 geometry](m11/phase2-geometry.json), [phase-3 geometry](m11/after-geometry.json).

The 165 prop-pixel black cells remain ratcheted, including the 150 lava-pool cells described in the spec. The combined `void_audit` diagnostic therefore reports `walkable_black_pass: false`; `test_visual_quality` separately verifies zero specified or unpainted cells and the unchanged prop allowance.

## Item results

### VQ-020: fixed

The drawn 48-unit corridor flanks, coincident outer rims, doorway lintels, and pad-room upper courses covered the narrow quest bands. The three near flanks now have coincident 497 and 498 courses at z 0 and 48, a 128-unit verge in the corridor’s own 242 floor, and an outer invisible curb. Connector rims are flush. D8 also covers the doorway lintels, Fire-to-Water near jamb, gate shoulder, and pad-room near courses and crests. Both cited stops reach 100% minimum visibility. Phase 3 also moves the unpinned Earth spire from (2431, 5503) to (2431, 4991) and Water boulder from (12044, 19036) to (12044, 18268), clearing the final nine cells.

| Stop | Walkable black | Frame black | Minimum visible | Captures |
|---|---:|---:|---:|---|
| m11-49 | 0 → 0 | 32.82% → 0.00% | 5.66% → 100.00% | [before](m11/before/m11-49.png), [after](m11/after/m11-49.png) |
| m11-50 | 0 → 0 | 35.47% → 0.00% | 67.25% → 100.00% | [before](m11/before/m11-50.png), [after](m11/after/m11-50.png) |

Records: 9,515 → 9,872 raw; 17,825 → 18,182 expanded. Screen05: 94.55287% → 94.55287%, zero unpainted non-black pixels. Screen07: 97.27655% → 97.27655%, zero unpainted non-black pixels.

### VQ-043: improved

The screen07 rock mask lacked top paint, and four eight-unit lip probes sampled black cover. 98 crest copies follow the 96-unit view ray by (−384, −384) to z 0, retaining their screen projection while drawing beneath the Avatar. Raised caps regressed visibility, which is why this uses T7 within the Map 11 builder. A 301 floor at (6751, 21119, 0) fills the four probes. A 35:10 tile at (6879, 21119, 0) preserves 15 upper-edge window pixels. The pinned pillar, stand-ins, and 891 and 892 face swaps retain their original records. Black top and backfill tails remain where a full plate intersects a protected window or real ground.

| Stop | Walkable black | Frame black | Minimum visible | Captures |
|---|---:|---:|---:|---|
| m11-11 | 0 → 0 | 7.27% → 6.73% | 100.00% → 100.00% | [before](m11/phase2/m11-11.png), [after](m11/after/m11-11.png) |
| m11-12 | 0 → 0 | 7.10% → 5.91% | 100.00% → 100.00% | [before](m11/phase2/m11-12.png), [after](m11/after/m11-12.png) |
| m11-13 | 0 → 0 | 5.80% → 3.67% | 100.00% → 100.00% | [before](m11/phase2/m11-13.png), [after](m11/after/m11-13.png) |

Records: 9,766 → 9,872 raw; 18,076 → 18,182 expanded. Screen05: 94.55287% → 94.55287%, zero unpainted non-black pixels. Screen07: 97.27655% → 97.27655%, zero unpainted non-black pixels.

### VQ-045: improved

Two eight-unit alcove-lip probes looked through to black cover along their view rays. Ground-level 301:0 backfill at (2559, 15103, 0) and (2687, 14911, 0) clears those probes. The cover calculation sees these floors before choosing filler. The relifted fire field and the original lip remain unchanged. The two probes are repaired; portions of the large visible black polygons remain in the retained filler tails.

| Stop | Walkable black | Frame black | Minimum visible | Captures |
|---|---:|---:|---:|---|
| m11-06 | 0 → 0 | 33.51% → 12.67% | 100.00% → 100.00% | [before](m11/phase2/m11-06.png), [after](m11/after/m11-06.png) |

Records: 9,766 → 9,872 raw; 18,076 → 18,182 expanded. Screen05: 94.55287% → 94.55287%, zero unpainted non-black pixels. Screen07: 97.27655% → 97.27655%, zero unpainted non-black pixels.

### VQ-035: improved

Black exterior plates beyond the intact section rims occupied visible frame area. D5 replaces exterior cover with 256-unit decorative 895:0 plates. The final map has 2,786 such plates, with no new collision or standing surface from those plates. Built-sprite window intersection checks retain 14 original large black plates and 58 small black tiles where a full plate would affect a published window or paint over real ground. An independent built-archive audit finds zero plate overlaps with DRAW ground; the rejected widened variant had 34 overlapping plates and 75 pairs. Frame black falls within the D5 mean target of 5%.

| Stop | Walkable black | Frame black | Minimum visible | Captures |
|---|---:|---:|---:|---|
| m11-03 | 0 → 0 | 10.34% → 0.08% | 100.00% → 100.00% | [before](m11/phase2/m11-03.png), [after](m11/after/m11-03.png) |
| m11-04 | 0 → 0 | 0.45% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-04.png), [after](m11/after/m11-04.png) |
| m11-05 | 0 → 0 | 5.86% → 0.01% | 100.00% → 100.00% | [before](m11/phase2/m11-05.png), [after](m11/after/m11-05.png) |
| m11-07 | 0 → 0 | 10.25% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-07.png), [after](m11/after/m11-07.png) |
| m11-22 | 0 → 0 | 1.07% → 0.09% | 100.00% → 100.00% | [before](m11/phase2/m11-22.png), [after](m11/after/m11-22.png) |
| m11-27 | 0 → 0 | 5.12% → 0.04% | 36.56% → 36.56% | [before](m11/phase2/m11-27.png), [after](m11/after/m11-27.png) |
| m11-30 | 0 → 0 | 12.83% → 0.46% | 100.00% → 100.00% | [before](m11/phase2/m11-30.png), [after](m11/after/m11-30.png) |
| m11-31 | 0 → 0 | 4.78% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-31.png), [after](m11/after/m11-31.png) |
| m11-32 | 0 → 0 | 12.38% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-32.png), [after](m11/after/m11-32.png) |
| m11-34 | 0 → 0 | 26.00% → 0.00% | 37.20% → 37.20% | [before](m11/phase2/m11-34.png), [after](m11/after/m11-34.png) |
| m11-35 | 0 → 0 | 6.32% → 0.08% | 100.00% → 100.00% | [before](m11/phase2/m11-35.png), [after](m11/after/m11-35.png) |
| m11-38 | 0 → 0 | 6.80% → 0.19% | 96.63% → 96.63% | [before](m11/phase2/m11-38.png), [after](m11/after/m11-38.png) |
| m11-43 | 0 → 0 | 4.76% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-43.png), [after](m11/after/m11-43.png) |
| m11-44 | 0 → 0 | 0.38% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-44.png), [after](m11/after/m11-44.png) |
| m11-45 | 0 → 0 | 3.75% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-45.png), [after](m11/after/m11-45.png) |
| m11-46 | 0 → 0 | 26.02% → 0.02% | 37.20% → 37.20% | [before](m11/phase2/m11-46.png), [after](m11/after/m11-46.png) |
| m11-47 | 0 → 0 | 10.95% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-47.png), [after](m11/after/m11-47.png) |
| m11-48 | 0 → 0 | 13.61% → 0.51% | 100.00% → 100.00% | [before](m11/phase2/m11-48.png), [after](m11/after/m11-48.png) |

Records: 9,766 → 9,872 raw; 18,076 → 18,182 expanded. Screen05: 94.55287% → 94.55287%, zero unpainted non-black pixels. Screen07: 97.27655% → 97.27655%, zero unpainted non-black pixels.

### VQ-038: improved

The same black-cover recipe filled spaces between sections and beside the connector ridges. The D5 plate replacement also paints those spaces with decorative dark stone. Existing cave barriers retain the enclosed walk and jump boundaries. Some window-adjacent filler tails remain, as measured below. The 128-unit view audit now measures a frame-black mean of 0.394%.

| Stop | Walkable black | Frame black | Minimum visible | Captures |
|---|---:|---:|---:|---|
| m11-14 | 0 → 0 | 2.67% → 0.29% | 100.00% → 100.00% | [before](m11/phase2/m11-14.png), [after](m11/after/m11-14.png) |
| m11-29 | 0 → 0 | 11.13% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-29.png), [after](m11/after/m11-29.png) |
| m11-37 | 0 → 0 | 0.48% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-37.png), [after](m11/after/m11-37.png) |
| m11-39 | 0 → 0 | 5.25% → 0.00% | 95.50% → 95.50% | [before](m11/phase2/m11-39.png), [after](m11/after/m11-39.png) |
| m11-42 | 0 → 0 | 15.79% → 0.00% | 37.20% → 37.20% | [before](m11/phase2/m11-42.png), [after](m11/after/m11-42.png) |
| m11-49 | 0 → 0 | 30.61% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-49.png), [after](m11/after/m11-49.png) |
| m11-50 | 0 → 0 | 32.74% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-50.png), [after](m11/after/m11-50.png) |
| m11-51 | 0 → 0 | 23.83% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-51.png), [after](m11/after/m11-51.png) |
| m11-52 | 0 → 0 | 23.83% → 0.00% | 100.00% → 100.00% | [before](m11/phase2/m11-52.png), [after](m11/after/m11-52.png) |

Records: 9,766 → 9,872 raw; 18,076 → 18,182 expanded. Screen05: 94.55287% → 94.55287%, zero unpainted non-black pixels. Screen07: 97.27655% → 97.27655%, zero unpainted non-black pixels.

### VQ-065: fixed

The Water bay’s north and east wall tops left a visible notch. A 29:0 post at (14335, 14336, 0) fills it. Its box lies entirely within the existing final north-wall piece, so collision extent is unchanged. The outer rim post at (14368, 14336) stays. Nine valid corner cameras across 72 poses produced 648 cycle-free frames; three static views also had zero cycles.

| Stop | Walkable black | Frame black | Minimum visible | Captures |
|---|---:|---:|---:|---|
| m11-08 | 0 → 0 | 30.86% → 0.00% | 92.25% → 92.25% | [before](m11/phase2/m11-08.png), [after](m11/after/m11-08.png) |

Records: 9,766 → 9,872 raw; 18,076 → 18,182 expanded. Screen05: 94.55287% → 94.55287%, zero unpainted non-black pixels. Screen07: 97.27655% → 97.27655%, zero unpainted non-black pixels.


Retained filler outside the protected windows remains visible in the following 256,000-pixel frames:

| Stop | Filler-black pixels outside windows |
|---|---:|
| m11-06 | 17,451 |
| m11-11 | 4,939 |
| m11-12 | 3,311 |
| m11-13 | 880 |

## Remaining work and scope

- Window-adjacent filler tails remain for VQ-035, VQ-038, VQ-043, and VQ-045. Full 256-unit plates cannot cover these retained parts under the current window and ground-footprint protection. Completing them needs clipped 895 frames in the shared art track, preserving frame 0 and donor-202 physics. That requires `lv_art_props.py`, its frame-copy validation in `test_art_props.py`, and supporting art outside the Owns line. A finer placement policy would also require a reviewed change to D5’s plate rule. [Residual black ownership](m11/protected-black.json), [floor-overlap negative control](m11/floor-overlap.json).

- The two ambient restoration props were unpinned. Moving them north clears the last nine quest-band cells. Both new boxes overlap no other non-flat solid and remain more than 1,100 world units from the relevant barriers. The before and after visibility measurements are in [cleared-leg-cells.json](m11/cleared-leg-cells.json). No occlusion allowance was added.
- D6 decorative water is blocked. Shape 896 needs a 347-copy row with donor-202 decorative physics and no `SI_SEA` in `lv_art_props.py`, plus the corresponding constant in `lv_shapes.py`. Both files lie outside §4.3’s Owns line. This slice leaves the Water section dry and adds no shape ID.
- D10’s pinned sealing boulders remain unchanged. Continuous in-engine walking, the merge walkthrough, and Astra grading remain for the orchestrator. This slice’s engine evidence consists of fresh per-stop teleports.
- Crest rendering uses the T7 view-ray treatment because raised T4 caps regressed the visibility ratchet. Every other edit remains in `build_map_11.py`, its visual pins, regenerated hashes and map pins, or the requested report and evidence. Main’s pre-existing edits remain untouched. The branch is local and unmerged.

## Verification

- `tools/build_artifacts.sh --record`: passed, zero map validation warnings or errors. [Build log](m11/after-build.log.gz). The expected EALOGO and TJORVI recovered-source compiler allowlist remains unchanged.
- `derive_map_pins.py`: regenerated; `test_map_pins_fresh.py` checks the built and builder inventories. All pinned map records retain their fields.
- `void_audit.py 11 --step 128 --workers 4`, `avatar_visibility.py 11 --step 128 --workers 4`, and `test_visual_quality.py 11` ran before changes and after both phases. Current report measurement also used `--strict --report128 --record`. [Before ratchet run](m11/before-quality.log.gz), [phase-2 run](m11/phase2-quality.log.gz), [final run](m11/after-quality.log.gz). Phase 2 exposed two frame-ratchet debts; D5 clears them in phase 3. Final result: zero ratchet failures and zero strict phase-exit failures.
- `tools/run_all_tests.sh`: 56 of 57 files pass; the sole permitted failure is test_integration_state.py, owing to unchanged harness and install FIXED copies. [Estate log](m11/estate.log.gz).
- Read-only verifier: final screenshot scores unchanged, all 10 gate coverage and reach checks pass, Water-corner 648-frame cycle sweep passes, and no actionable source defect found.
- `codex exec review --base main`: the first attempt stopped before inspection owing to bubblewrap `Failed RTM_NEWADDR: Operation not permitted`. The retry used `-c 'sandbox_mode="danger-full-access"'`. Completed: no actionable defects; independent route reachability 166 checks, Map 11 hygiene 10 checks, visual quality, and both screenshot windows pass. [Initial review](m11/review-initial.log.gz), [completed review](m11/review.log.gz).
- `git diff --check`: passed. All five canonical SHA-256 checks pass: [hash verification](m11/hash-verification.txt). Display `:63` is stopped: [session status](m11/session-status.txt).

## Capture evidence

Every accepted capture uses display `:63`, `XDG_RUNTIME_DIR=/tmp/claude-1000/vq2-m11`, `usehighres=false`, and a fresh world. The unchanged `tour_capture.py`, `session.sh`, and `shot.sh` run against private immutable artifact copies for each phase. An external xdotool wrapper spaces modifier events by 0.2 s to make debugger entry reliable under concurrent load. [Capture provenance](m11/capture-provenance.json), [stop list](m11/stops.json).

| State | Completed | Landed |
|---|---:|---:|
| before | 32 / 32 | 32 / 32 |
| phase2 | 32 / 32 | 32 / 32 |
| after | 32 / 32 | 32 / 32 |

All 96 PNGs are 640 by 400, with ok and landed true, and have recorded SHA-256 hashes in [capture-inventory.json](m11/capture-inventory.json). Collection completed on 3 November 2026 at 23:55 CST. All 32 final Map 11 log segments contain zero paint-cycle messages and zero process warnings. Fresh startup emitted 96 inherited process warnings on Map 0 during the Guardian scene; the full-session zero-warning target remains unmet and requires a separate usecode or engine investigation outside Map 11. [Log audit](m11/capture-log-audit.json). Failed and superseded attempts were excluded from accepted evidence and replaced.

Raw command and engine logs, and audit arrays larger than 1 MiB, are stored as deterministic gzip files. Log compression preserves the original bytes; [log-inventory.json](m11/log-inventory.json) records their hashes. The six repaired coordinates are recorded independently in [lip-probes.json](m11/lip-probes.json).

## Artifact hashes

The first four artifacts remain byte-identical across all phases:

```text
ac0b33486fc167d98c07c32011de348c11ae0cefb8d89fc2597ef984133a5fd1  TYPEFLAG.DAT
aad6ed7b8961f416b6fae225d467427899a4487db768b6fb486ed5b5cb3e73ba  U8SHAPES.FLX
97ae5fc9ddaa6ef515427103264a3095a6d42776ac51e530954fb4846b4d0443  ANIM.DAT
b47c324cdad77646c27755acfdd5bca53a9d92e16268db229f18e7dd780d4205  EUSECODE.FLX
```

| FIXED state | SHA-256 |
|---|---|
| Before | `89da4e165833bff0b4da526cfa2cbc434336f6816e3964ae9982bd804a2eb767` |
| Phase 2 | `be76caba40b5528e66534971e8e9e61a891413f23957e5ef5ac9af3703c739b9` |
| Phase 3 | `2834077510f6c12ed2a4de262ddc25329102a1433b319beac87ab6108bfa56ee` |

Final raw-record headroom is 1,828 below the 11,700 phase exit ceiling. The 12,000 hard cap and 32,500 object limit also hold.
