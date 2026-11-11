Map 17 passes strict visual acceptance on FIXED `abd14635501999361122b176321f4655603cf4b109c259fc4cfeded5063ac648`. The final estate passes 56 of 57 files, with the permitted installation-state exception.

## Verdicts

| Check | Result and evidence |
|---|---|
| Quest visibility | Pass. `test_visual_quality.py 17 --strict`: zero failures, zero leg cells below half visibility, and 9,284 raw and expanded records. `verifier-strict.log` retains the output. |
| Full estate | Pass within the authorized exception. `tools/run_all_tests.sh`: 56 of 57 files pass. The eight-map visual check passes in 86.951 seconds. `verifier-estate.log.gz` retains the complete result. |
| Canonical rebuild | Pass. `tools/build_artifacts.sh` completes after the estate and matches all five canonical hashes. Compilation succeeds for 55 of 57 files; EALOGO and TJORVI remain the two allowed failures. `verifier-build.log.gz` retains the output. |
| Route and map edges | Pass. The final estate passes 166 route assertions, 76 paint-cycle assertions, 201 schedule assertions, 60 hygiene assertions, and the map-edge test. Individual compressed logs accompany this report. |
| Original records | Pass. All original Map 17 records remain unchanged; all other 255 archive entries are identical. The source emits exactly the 1,331 added editor records found in the built archive. |
| Reachability | Pass. Reached cells fall from 62,424 to 61,084. All 1,340 lost cells directly overlap the explicit recesses with the 64×64×40 body. There are zero added cells and zero extra disconnected cells. |
| Item clearance | Pass. All 26 movable item boxes and every typed item box clear the added walls. The definition uses positive weight and the engine's FIXED bit, `0x01`. `verifier-geometry.json` records the complete scan. |
| Interaction approaches | Pass for the static collision model. Every movable item and the typed obelisk drum has a reachable ground-level approach within the engine's 128-unit range with a clear origin, centre, or top ray. Restoring the removed half-81 recess makes all three example rays fail. `verifier-interaction-source.json` records all targets and the negative control. |
| New footing | Pass for the geometry check. The column barrier ends at 192, above the highest 88-unit post by 104 units. The obelisk barrier ends at 240, above its 128-unit cap by 112 units. The retained upper course blocks standing on the exposed drum or skull. The six ground strips beginning at z=8 still block the body after container pickup and overlap the course beginning at z=48. |
| Shot windows | Pass. Before and after palettes are pixel-identical: screen11 scores 99.92932374894417%, and screen12 scores 97.94289587393035%. Both retain zero unpainted pixels. `verifier-window-bytes.log` records the comparison; the final estate passes all 39 vignette assertions. |

## Failure

`test_integration_state.py` reports 10 passed, one failed, and three skipped assertions. Its sole failure is the symlinked installation target's `STATIC/FIXED.DAT != canonical FIXED.DAT`. The private capture harness holds canonical bytes. The three skips concern the absent worktree ScummVM source tree and binary. The user authorized this worktree exception and prohibited changing the main installation.

## Corrected findings and limits

Earlier recesses intersected both Shield halves, the movable skull, a small prop, and two movable bone containers. The final bounds, omitted obelisk ground strip, and six raised ground strips clear every movable full box. An isolated four-cell pocket was removed from the design, and higher backstops prevent new invisible footing from nearby posts.

Interaction evidence models the engine's three 2×2×2 sight rays and strict box geometry. In-engine pickup actions were outside this verifier run. The parent owns the required fresh-world tour captures. No additional source or scope finding remains.

## Disk changes

This verifier wrote `verifier-REPORT.md`, `verifier-geometry.json`, `verifier-interaction-source.json`, their two executable `.py.txt` evidence scripts, the strict and window logs, and compressed estate, build, and individual-check logs under this directory. `candidate1-*` retains the earlier completed candidate's checks; `candidate2-*` retains the interrupted candidate's evidence. The canonical rebuild regenerated private build outputs with unchanged final hashes. This verifier made no source edits, installation changes, commits, or ScummVM launches.
