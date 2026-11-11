V1 **PARTIAL**: both Map 8 seams, the exposed shelf, and low-resolution ceiling repaint pass. The complete entrance-to-plateau activation was not demonstrated. Black floor remains in the original retail pocket.

V2 **PARTIAL**: all four Map 10 visual regions were walked and pass their local floor audits. Ragnar's cache and the temple approach work. Three Water Zombies prevented a complete lake pier crossing.

V3 **PASS**: player arrivals through 204, the visible star pad, the relocated lamp, the sealed doorway, the opened doorway after the pillars, and exits through 205 are demonstrated.

V4 **PASS**: player arrival through 209, the readable Message Scroll, both Shield half approaches, both cloud regions, and return through 208 are demonstrated.

V5 **PARTIAL**: player arrival through 211, Tiny Tar use, and the crack crossing are demonstrated. The rock has visible faces, and screen04 matches SCORES. An engine capture of the shrunken Avatar at exactly `(2863,7127,0)` was not obtained.

V6 **PASS**: Map 9 geometry and screen10 pixels are unchanged. A player walk reaches the photographed dais position with its black cover retained.

V7 **FAIL**: four `Cycle in paint` lines occur beside Map 17's sun Shield half. Assertions, `ERROR`, and unhandled intrinsics have zero matches across both captured logs.

## Failures and limits

The session does not establish full acceptance of phase 1. V1, V2, and V5 contain incomplete engine demonstrations; V7 contains a reproduced paint defect.

The log failure is reproducible at Map 17 `(4332,7144,8)`:

```text
session.log:19777: Cycle in paint dependency graph 219 -> 875 -> ... -> 219
session.log:19778: Cycle in paint dependency graph 219 -> 875 -> ... -> 219
session.log:19780: Cycle in paint dependency graph 219 -> 875 -> ... -> 219
session.log:19839: Cycle in paint dependency graph 219 -> 875 -> ... -> 219
```

The same pair and location appear in [17 October leg 5, finding 4](playtest-2026-10-17-replay-leg5.md). The 78 fixed records around the half are byte-identical to the phase 1 baseline, as recorded in [cycle-region-invariant.json](playtest-2026-11-02-vq1-verify/cycle-region-invariant.json). Confidence is high that this is an existing defect. Its presence still fails the requested session log-hygiene claim.

V1 stopped short of a continuous cave-to-plateau traversal. Retail fire-trap knockback repeatedly interrupted the connecting shelf, one attempt died, and the plateau approach never activated its trigger. Independent setup positions were used to walk each seam and the exposed shelf. The pool and ascent also required player jumps and a climb. These are segmented demonstrations.

V2 reached the lake pier junction, where three Water Zombies occupied the route. Repeated walking and combat attempts did not clear the junction. The island deck and shore were tested from separate setup positions after a genuine map arrival. Their visual results cannot establish the full pier crossing.

V5 reached the fork vicinity while shrunken at `(2851,7167,0)`. Frame stepping, animation state, and potion expiry prevented the exact requested engine plate. A regrowing capture near the target was rejected. The independent exact-position visibility audit passes, but it does not replace the missing engine demonstration.

## Test conditions and evidence

Verification began at `94cc07d593d6af1e8d3cae57fc2dc0fb8c342db9`. During the session, HEAD advanced to `84450225fb6cc9c3122943c48bbdcd59b9e9f9e8` through a concurrent commit that adds only `docs/research/2026-11-01-visual-pass/phase23-design.md`. The tested installed artifacts and binary remained unchanged. Existing tracked files match the content snapshot taken at the start. See [scope-check.json](playtest-2026-11-02-vq1-verify/scope-check.json).

ScummVM used the requested console binary, display `:86`, runtime `/tmp/claude-1000/fable-verify`, and installed game `shared/u8-lv-patched`. The private [scummvm.ini](playtest-2026-11-02-vq1-verify/scummvm.ini) sets `usehighres=false` and a 640 by 400 surface. The binary SHA-256 is `e0518ced08224fe21ee9fea217b465a85e5f553277ec4fc851fbfada1e5474ff`; fork HEAD is `e48f87165ae8cbdf80e27414709e31987a68842f`. The binary postdates that fork commit.

The first setup teleport received a 24-second wait and an Avatar objectInfo check. Saved current-map items were avoided by leaving and re-entering affected maps. Claims involving EggReapply use actual player pad arrivals. Cheats were disabled for decisive movement; invincibility was used after the Map 8 death and during the unsuccessful lake combat attempts. No hack mover was used.

The raw [actions.jsonl](playtest-2026-11-02-vq1-verify/actions.jsonl) records setup, commands, failed attempts, and positions. [movement.json](playtest-2026-11-02-vq1-verify/movement.json) extracts player movements and map transitions. [plates.csv](playtest-2026-11-02-vq1-verify/plates.csv) records positioned captures, timestamps in CST, log lines, and hashes. [evidence.txt](playtest-2026-11-02-vq1-verify/evidence.txt) collects relevant objectInfo and flag lines.

### V1: Map 8

The Map 7 entrance was approached from `(9803,19699,0)`. A westward player move changed the map to 8 at `(30391,19135,0)`. The [arrival plate](playtest-2026-11-02-vq1-verify/V1-map8-arrival.png) follows that crossing.

Both seam apertures admit ordinary player movement at z 56:

| Segment | Player movement | Evidence |
|---|---|---|
| First seam | East from `(29600,24383,56)` to `(29808,24383,56)` | [West](playtest-2026-11-02-vq1-verify/V1-seam1-west-live.png), [east](playtest-2026-11-02-vq1-verify/V1-seam1-east-live.png) |
| Second seam | South from `(30440,26240,56)` to `(30408,26688,56)` | [North](playtest-2026-11-02-vq1-verify/V1-seam2-north-live.png), [south](playtest-2026-11-02-vq1-verify/V1-seam2-south-live.png) |
| Exposed shelf | South to `(30408,28776,56)`, then `(30408,30664,56)` | [Visible Avatar](playtest-2026-11-02-vq1-verify/V1-exposed-shelf-walked.png), [south shelf](playtest-2026-11-02-vq1-verify/V1-south-shelf-live.png) |

`exact_reach.py`, with an 8-unit lattice and the normal 64 by 64 by 40 body, also reaches both seam target neighborhoods. The [first](playtest-2026-11-02-vq1-verify/exact-seam1.log) and [second](playtest-2026-11-02-vq1-verify/exact-seam2.log) results use the default 96-unit target ring. Exact engine crossing positions above are the decisive aperture evidence.

The retained-wall negative control refused two eastward holds at `(29663,24511,56)`: [plate](playtest-2026-11-02-vq1-verify/V1-retained-wall-refuses.png). The [floor audit](playtest-2026-11-02-vq1-verify/map8-floor-audit.json) finds zero black samples among 15,454 reached samples outside the original retail pocket. Inside that pocket, 256 of 304 samples remain black. This supports the exposed-shelf claim and prevents a map-wide zero-black verdict. The plan's retail distinction remains material.

Five captures after back-and-forth camera movement have zero stale nonblack pixels in their exposed background masks, ranging from 4,964 to 6,024 pixels. The [results](playtest-2026-11-02-vq1-verify/lowres-ceiling-check.json) include actual positions. The same 5,195-pixel mask detects 4,985 nonblack pixels in the archived broken low-resolution capture, compared with zero now: [negative control](playtest-2026-11-02-vq1-verify/lowres-negative-control.json). This establishes a detector that catches the original repaint defect.

### V2: Map 10

Ragnar's cache was approached on foot through its rising tiers to `(16536,25767,56)`. The [crown plate](playtest-2026-11-02-vq1-verify/V2-cache-crown-walked.png) shows the props supported by ground. Double-clicking bag 1767, shape 637 at `(16447,25727,64)`, opens its inventory: [bag plate](playtest-2026-11-02-vq1-verify/V2-cache-bag-open.png).

The island deck was walked south from `(13631,18175,8)` to `(13631,18535,8)`. The shore was walked from `(14047,17919,8)` to `(14047,18151,8)`. Both show filled ground: [deck](playtest-2026-11-02-vq1-verify/V2-island-deck-walked.png), [shore](playtest-2026-11-02-vq1-verify/V2-island-shore-walked.png). Repeated northward holds stop at `(14067,17731,8)`, providing the [water-boundary negative control](playtest-2026-11-02-vq1-verify/V2-lake-water-refused.png).

The south-west stairs reach `(9367,20063,104)` and the neighboring tier. The [tier plate](playtest-2026-11-02-vq1-verify/V2-southwest-tier-walked.png) shows the former band filled. The temple ascent reaches `(18455,22471,112)` and crosses east to `(18871,22471,112)`: [processional shelf](playtest-2026-11-02-vq1-verify/V2-processional-shelf-walked.png). Walking back down the temple approach and south through 211 changes Map 10 to Map 18 at `(3072,2256,0)`.

The independently rerun regional floor audit uses exact reachability at 32-unit sampling. Its [before/current results](playtest-2026-11-02-vq1-verify/map10-region-floor-audit.json) are:

| Region | Reached samples | Black before | Black now |
|---|---:|---:|---:|
| Cache | 2,196 | 0 | 0 |
| Lake island | 1,964 | 2 | 0 |
| Temple | 2,342 | 77 | 0 |
| South-west tier | 533 | 24 | 0 |

The old lake, temple, and tier defects act as detector controls. These counts cover the four named bounds. Map 10's eight teleport records, 10 monster eggs, and 15 ordinary eggs remain byte-identical to the baseline: [route invariants](playtest-2026-11-02-vq1-verify/route-invariants.json). Full lake crossing remains unproved; [the blocked junction](playtest-2026-11-02-vq1-verify/V2-pier-monsters.png) records the obstruction.

### V3: Map 11

A northward walk on Map 10 enters 204 and lands at `(8291,22607,0)` on Map 11. With `allColumnsDestroyed=0` (`[06EC 01] = 0`), two northward holds at `(8499,22607,0)` are refused. ObjectInfo identifies both sealing objects, 20428 and 20429, as shape 66, q299. The [sealed-door plate](playtest-2026-11-02-vq1-verify/V3-seal-refuses-walking.png) shows the clear lamp and star marker.

A south-east player walk through the star pad activates 205 and returns to Map 10 at `(12996,2756,0)`: [exit plate](playtest-2026-11-02-vq1-verify/V3-trigger205-exit.png).

The pillars-down checkpoint was then loaded, followed by a fresh walked arrival through 204. With `[06EC 01] = 1`, both q299 objects are absent, and the northward walk reaches `(8579,21927,0)` through the doorway. Returning south and crossing 205 reaches Map 10 again: [open doorway](playtest-2026-11-02-vq1-verify/V3-open-door-after-pillars.png), [second exit](playtest-2026-11-02-vq1-verify/V3-open-trigger205-exit.png). The sealed and opened states provide opposing controls for the same passage.

### V4: Map 17

Setup on Map 13 stopped outside the hatch activation box at `(4351,2400,120)`. A northward player walk activates 209 and reaches Map 17 `(4608,9784,0)`: [before](playtest-2026-11-02-vq1-verify/V4-before209-outside-box.png), [arrival](playtest-2026-11-02-vq1-verify/V4-pad209-arrival.png).

The scroll approach reaches `(3388,1387,0)`. Object 24030 is shape 864, q80 at `(3328,1536,8)`. It is fully exposed on the [dais plate](playtest-2026-11-02-vq1-verify/V4-scroll-dais-walked.png). A real double-click dispatches event 1 at `0360:00B1` and opens the [readable letter](playtest-2026-11-02-vq1-verify/V4-scroll-letter-open.png).

After another walked 209 arrival, the sun half is approached at `(4332,7144,8)` and the eye half at `(3412,3248,16)`: [sun](playtest-2026-11-02-vq1-verify/V4-sun-shield-half-walked.png), [eye](playtest-2026-11-02-vq1-verify/V4-eye-shield-half-walked.png). Both halves remain in place; collection was outside this claim.

The [arrival channel](playtest-2026-11-02-vq1-verify/V4-arrival-channel-cloud.png) and [south bay](playtest-2026-11-02-vq1-verify/V4-south-bay-cloud.png) show cloud. Repeated channel pushes stop at `(4608,10480,0)`. Bay pushes slide along the boundary near `(6396,7904,0)` and remain contained. The baseline's 400 curb records are unchanged. These are the cloud-fill collision controls.

The east bridge and pier were walked, followed by a north-west crossing of 208 from `(4692,11096,0)`. ObjectInfo confirms the return to Map 13 `(5075,2259,120)`: [return plate](playtest-2026-11-02-vq1-verify/V4-trigger208-return.png).

### V5: Map 18

The walked temple approach activates 211 and reaches Map 18 `(3072,2256,0)`: [arrival plate](playtest-2026-11-02-vq1-verify/V5-map18-player-arrival.png). The hall was walked to the crack. Full-size attempts stop north of the breach, with `templeOpen=0` (`[0412 01] = 0`): [negative control](playtest-2026-11-02-vq1-verify/V5-fullsize-crack-refused.png).

Tiny Tar was double-clicked in the backpack. ObjectInfo confirms shape 867. From setup north of the crack at `(2863,6063,0)`, right-button movement with native frame advancement walks through `(2863,6159,0)`, `(2863,6255,0)`, and `(2863,6367,0)`. The flag changes to `[0412 01] = 1`: [crossing plate](playtest-2026-11-02-vq1-verify/V5-tiny-crack-crossed.png). The six q307 breach records are unchanged from the baseline.

The [near-fork observation](playtest-2026-11-02-vq1-verify/V5-fork-final-observation.png) follows actual Tiny walking to `(2851,7167,0)`. The small Avatar is visible, and the central rock has drawn faces. It is 40 units south and 12 units west of the requested point. Exact-point engine visibility remains unproved.

The independent [visibility audit](playtest-2026-11-02-vq1-verify/tiny-visibility.json) evaluates all 72 walking and standing poses at exactly `(2863,7127,0)`. Every pose has visible fraction 1.0 in both the grouped painter and independent owner painter. Frame zero retains 279 of 279 opaque pixels. Against the archived broken map, every pose has visible fraction 0.0, including zero of 279 pixels for frame zero. This strong supporting result remains a static check.

The actual `tools/playtest-linux/vignette_capture.py` was run for screen04 through a private wrapper. The wrapper changes console transport, enables Object, and extends the teleport wait to 24 seconds. The capture and scoring functions are unchanged. ObjectInfo confirms Map 18 `(3256,8152,0)` after the wait. The [comparison plate](playtest-2026-11-02-vq1-verify/vignette/screen04_ingame.png) and [command output](playtest-2026-11-02-vq1-verify/vignette-capture.log) report:

```text
screen04: map 18 avatar (3256,8152,0) frame at (+106,+50) class 95.26% rgb 94.62%
```

These values exactly match [SCORES.md, screen04](research/2026-10-16-screenshot-reconstruction/ingame/SCORES.md). The 30 October score was 95.22% class and 94.58% RGB, owing to capture pose and cursor differences. Independently rendered baseline and current screen04 windows have zero changed pixels among 59,200: [offline comparison](playtest-2026-11-02-vq1-verify/offline-checks.json). The vignette teleport is archival-image evidence; the crack demonstration uses player movement.

### V6: Map 9

All 1,019 Map 9 fixed records are byte-identical to the baseline. Its rendered screen10 window also has zero changed pixels among 58,830, with class score 89.517253% before and after: [comparison](playtest-2026-11-02-vq1-verify/offline-checks.json).

A westward player walk from `(14240,12568,0)` reaches the exact photographed Avatar spot `(14136,12568,0)`. The [engine plate](playtest-2026-11-02-vq1-verify/V6-dais-black-retained.png) retains the dais black cover. The archived diagnostic map that removes the 30 shape 35 frame 10 cover records scores 83.454020%, below the 89.27% required floor after slack: [negative control](playtest-2026-11-02-vq1-verify/screen10-negative-control.json). This confirms that the retained black is part of the reference image.

### V7: Session logs

Object logging was enabled at startup and re-enabled after each checkpoint load. The [load audit](playtest-2026-11-02-vq1-verify/object-channel-loads.json) records each re-enable. Live same-channel usecode messages and the four actual cycle lines establish that the channel was active. The [scan](playtest-2026-11-02-vq1-verify/log-scan.json) counts four cycles, zero assertions, zero `ERROR` lines, and zero unhandled intrinsic lines in the main session. The fresh vignette session has zero matches in all four categories.

The exported [main log](playtest-2026-11-02-vq1-verify/session.log) excludes 632,582 bytes of pre-existing runtime log content. Its first launch and every later verifier restart are retained. Raw action offsets refer to the original runtime log; the plate index and evidence excerpts use exported-log line numbers. The separate [vignette log](playtest-2026-11-02-vq1-verify/vignette/session.log) contains only that fresh capture session.

## Repository checks

| Check | Verdict and evidence |
|---|---|
| Full test estate | **PASS**: `tools/run_all_tests.sh`, exit zero, 56 of 56 test files. [Output](playtest-2026-11-02-vq1-verify/test-estate.log) |
| Existing build hashes | **PASS**: `tools/build_artifacts.sh --verify`, exit zero, all five canonical artifact hashes match. [Output](playtest-2026-11-02-vq1-verify/hash-verify.log) |
| Installed game | **PASS**: all six installed placements match the built artifacts, including both FIXED.DAT copies. Final hashes remain unchanged. [Results](playtest-2026-11-02-vq1-verify/offline-checks.json) |
| Fork patch | **PASS**: the fork's engines diff against `01bd88796f47b21ce8e985a94a6c284439b6f032`, excluding detection tables, equals the tracked engine patch; `diff -q` exits zero. [Results](playtest-2026-11-02-vq1-verify/offline-checks.json) |
| Raw map records | **PASS**: Map 8: 5,689; Map 9: 1,019; Map 10: 20,571; Map 11: 9,515; Map 13: 6,447; Map 17: 6,665; Map 18: 1,750. All remain below 32,500. [Counts](playtest-2026-11-02-vq1-verify/offline-checks.json) |
| Full build, install, and binary rebuild | **NOT RUN**: the explicit verifier request prohibits rebuilding and identifies the installed copy as ready. Existing artifact and installed-byte checks were used. No fresh compiler failure-count claim is made. |
| Shutdown | **PASS**: `session.sh status` reports display down, with empty ScummVM and Xvfb process fields. [Output](playtest-2026-11-02-vq1-verify/shutdown.txt) |

## Findings outside the brief

1. **Map 8 retains original retail black floor.** The local audit detects 256 black samples inside the 304-sample original pocket. The exposed region passes. A blanket zero-black statement would exceed this evidence.
2. **The lake junction is sensitive to live monsters.** Static teleport and egg records are unchanged, while three Water Zombies prevent this checkpoint's full engine crossing. The report establishes the obstruction without attributing it to the phase 1 geometry changes.
3. **Harness recovery affected continuity.** One early process lifetime ended unexpectedly, and some recovery teleports landed on Map 39. Those attempts were rejected using objectInfo. The raw action record retains the failures. Potion animation and expiry also limited the exact fork capture.
4. **Concurrent documentation changed HEAD.** Commit `8445022` arrived during this read-only verification. It changes one new design document and no game bytes.
5. **Other warnings remain.** The main log contains three invalid-process waitlist warnings, six actor ANIMLOCK warnings, 27 audio instrument warnings, one MIDI transition warning, and eight missing-resource or theme warnings. The fresh vignette log contains three `Non-existent process PID (0) in implies` warnings before Map 18 loads and three resource or theme warnings. These are outside the four requested V7 patterns. Their lines and counts are retained in [warnings.json](playtest-2026-11-02-vq1-verify/warnings.json); their cause was not investigated further.

## Disk changes

This verifier wrote this report and the accompanying `docs/playtest-2026-11-02-vq1-verify/` directory. The directory contains retained PNG captures, logs, JSON audits, CSV capture metadata, the private ini copy, supporting Python scripts, and a SHA-256 manifest. Runtime commands, private saves, helper scripts, and rejected captures remain under `/tmp/claude-1000/fable-verify/`.

Pre-existing modifications to `CLAUDE.md` and `.claude/settings.json`, and the pre-existing untracked files listed in the scope record, were left intact. No source, builder, map, installed artifact, or binary was changed by this verifier. No rebuild, install, or commit was performed. ScummVM and Xvfb on `:86` are stopped.
