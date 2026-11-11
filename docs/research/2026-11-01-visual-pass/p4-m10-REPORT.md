# Map 10 dressing pass

10 November 2026. Branch `wt/vq4-m10`, based on main `af6fd649`.

Verification checkpoint. All twelve measured regions meet their targets and preserve main’s regional ratchets. Final capture inspection, the estate, and the follow-up review remain in progress.

## Result and budgets

The map reads as a dead mountain valley of grey rock and brown earth, with two poor villages beside a dark lake. Thirteen regional compositions use explicit world coordinates and `Site.set_piece`; the long hall has an additional paving composition. Ground variation follows named washes, drainage fans, and compact focal patches. Low rubble supplies seam dressing.

Raw records: **21,864 → 13,455**, below the 20,000 phase-exit ceiling and the 25,000 hard cap. Expanded records: **48,204 → 51,286**. The expanded-record pin rises under Douglas’s explicit §4.2 record-growth exception. Expanded items per ground cell: **1.4845**, below 2.0. Every improved bound is ratcheted against main’s pins, including regional minimum bounds.

[Full baseline measurements](p4-m10/metrics-before.json), [final measurements and failed bounds](p4-m10/metrics-after.json), and [geometry comparison](p4-m10/constraints-after.json).

| Region | Target failures before → after | Props per 100 land cells | Dressed share | Top material |
|---|---:|---:|---:|---:|
| entry | 7 → 0 | 1.35 → 12.08 | 0.127 → 0.468 | 0.789 → 0.543 |
| hoskuld village | 5 → 0 | 7.34 → 17.97 | 0.239 → 0.577 | 0.482 → 0.476 |
| north plain | 6 → 0 | 0.40 → 10.29 | 0.040 → 0.430 | 0.658 → 0.458 |
| gunnar village | 3 → 0 | 11.25 → 21.72 | 0.438 → 0.656 | 0.532 → 0.532 |
| ezrekal | 7 → 0 | 4.69 → 17.01 | 0.368 → 0.597 | 0.816 → 0.477 |
| west clearing | 6 → 0 | 0.52 → 11.20 | 0.089 → 0.432 | 0.854 → 0.424 |
| lake | 3 → 0 | 1.55 → 8.20 | 0.118 → 0.287 | 0.455 → 0.540 |
| sacred circle | 3 → 0 | 1.69 → 11.46 | 0.283 → 0.503 | 0.758 → 0.475 |
| cloud approach | 3 → 0 | 1.08 → 9.21 | 0.322 → 0.515 | 0.704 → 0.458 |
| moriens ruins | 4 → 0 | 1.39 → 13.02 | 0.142 → 0.470 | 0.729 → 0.413 |
| temple approach | 5 → 0 | 3.12 → 12.79 | 0.387 → 0.605 | 0.784 → 0.531 |
| passage test | 3 → 0 | 0.85 → 11.08 | 0.082 → 0.406 | 0.676 → 0.528 |

Inside the outline, props per 100 land cells rise from 2.093 to 10.422; bare share falls from 0.2104 to 0.0488; top material falls from 0.6944 to 0.4802. Dressing eggs rise from 0 to 160 inside the outline (163 across the whole map), meeting the 150-egg target.

Ragnar’s cache is absent from the shared twelve-region target table. It receives its required authored scene and remains inside the whole-map measurements. No separate target allowance or pin was invented for it.

## Regional compositions

### Entry

Reads as: the head of the pass, a paved court gone to ruin.

Four surviving white column bases mark the portico line. Four drums lie in the same direction across breached steps; a split lintel and rubble collect at the feet. The steps use `walkable_set_piece`, with an open central track and a proved retained walking area. The court remains the visual centre; narrow soil fans break the surrounding rock.

Set piece: **Fallen court portico**, [640×400 capture](p4-m10/setpieces/fallen-court-portico.png).

Target failures: 7 → 0. Main-pin regressions: zero. Raw records: 341 → 180; expanded records: 1,151 → 1,261. Protected windows: none inside this region; scores are recorded below.

### Hoskuld village

Reads as: a fenced hamlet of plank huts round a well.

A post, fence panel, fallen timber, broken jars, and displaced rubble form a repair yard beside the well. Lot one uses an elongated red-roof plank hall with a small cobbled apron. Eighteen crops form two uneven beds.

Set piece: **Well yard fence repair**, [640×400 capture](p4-m10/setpieces/well-yard-fence-repair.png).

Target failures: 5 → 0. Main-pin regressions: zero. Raw records: 1,113 → 770; expanded records: 2,343 → 2,611. Protected windows: none inside this region; scores are recorded below.

Additional composition: [long hall and paving apron](p4-m10/setpieces/long-hall.png).

### North plain

Reads as: open dead ground between the villages, crossed by an earth track.

Gravel and soil trace a dry wash. Two broken bridge decks, surviving posts, a dropped panel, fallen timber, and debris describe its failed crossing. The existing earth track stays clear.

Set piece: **Collapsed dry-bed crossing**, [640×400 capture](p4-m10/setpieces/collapsed-dry-bed-crossing.png).

Target failures: 6 → 0. Main-pin regressions: zero. Raw records: 1,877 → 622; expanded records: 4,112 → 4,509. Protected windows: none inside this region; scores are recorded below.

### Gunnar village

Reads as: the smith's village under a rock shelf.

A dark basalt charcoal hearth sits inside a broken stone ring, with a compact cordwood stack on one side and an anvil, hammer, and bellows on the other. Slag and collapsed stone gather at its edge outside the fixed screenshot windows.

Set piece: **Smith charcoal yard**, [640×400 capture](p4-m10/setpieces/smith-charcoal-yard.png).

Target failures: 3 → 0. Main-pin regressions: zero. Raw records: 2,041 → 1,493; expanded records: 2,821 → 3,023. Protected windows: 19, 20, 22; scores are recorded below.

### Ezrekal

Reads as: a hermit's stockade with the only living garden.

Two posts support a drying panel over five deliberately grouped jars inside the stockade. The original herb rows retain their green. Generated exterior scatter uses stone and rubble.

Set piece: **Hermit drying yard**, [640×400 capture](p4-m10/setpieces/hermit-drying-yard.png).

Target failures: 7 → 0. Main-pin regressions: zero. Raw records: 279 → 157; expanded records: 639 → 707. Protected windows: none inside this region; scores are recorded below.

### West clearing

Reads as: a killing ground.

Two skeletons and four timber posts form a broken ring around a timber barricade and a rubble strongpoint. The logs define the defended north-west side; flat sword, axe, and dagger frames lie beside the formation, and a dead tree stands behind it. The original remains stay in the clearing. The original green boundary cubes leave.

Set piece: **Last stand at the dead tree**, [640×400 capture](p4-m10/setpieces/last-stand.png).

Target failures: 6 → 0. Main-pin regressions: zero. Raw records: 259 → 126; expanded records: 784 → 862. Protected windows: none inside this region; scores are recorded below.

### Lake

Reads as: a black tarn with a rock island.

Jagged native pillars and rock spires form a drowned outcrop beside the western bank. A hand-shaped headland, irregular detached crest rocks, sparse waterline stones, and occasional textured water articulate the bank. Open water remains navy.

Set piece: **Drowned watch cairn**, [640×400 capture](p4-m10/setpieces/drowned-watch-cairn.png).

Target failures: 3 → 0. Main-pin regressions: zero. Raw records: 1,071 → 745; expanded records: 1,866 → 2,018. Protected windows: 02, 09; scores are recorded below.

### Sacred circle

Reads as: standing stones on a bare crest.

Four broken jars, rubble, and two pebble groups form an interrupted votive crescent below the original ring. The eight standing stones, Sacred Rock, and paving remain. Green boundary cubes leave.

Set piece: **Broken votive crescent**, [640×400 capture](p4-m10/setpieces/broken-votive-crescent.png).

Target failures: 3 → 0. Main-pin regressions: zero. Raw records: 531 → 247; expanded records: 936 → 987. Protected windows: none inside this region; scores are recorded below.

### Cloud approach

Reads as: a stair cut into the canyon toward the sky.

A lashed timber frame, fallen timber, collapsed debris, and remains compose a failed worksite. Twenty-two cold cells receive decorative basalt beside the existing lava; all 54 lava tuples remain.

Set piece: **Abandoned canyon scaffold**, [640×400 capture](p4-m10/setpieces/abandoned-canyon-scaffold.png).

Target failures: 3 → 0. Main-pin regressions: zero. Raw records: 808 → 523; expanded records: 1,468 → 1,552. Protected windows: 18, 21; scores are recorded below.

The existing scaffold inside the published reconstruction remains protected. The new lashed-frame scene occupies clear ground outside the windows.

### Moriens ruins

Reads as: a fallen colonnade.

Two broken native wall runs frame a small irregular cobbled court. Fallen white drums, a retained pillar, and rubble face the original tall columns and inscription. A nearby lone spire becomes low rubble.

Set piece: **Fallen west colonnade**, [640×400 capture](p4-m10/setpieces/fallen-west-colonnade.png).

Target failures: 4 → 0. Main-pin regressions: zero. Raw records: 303 → 130; expanded records: 603 → 687. Protected windows: none inside this region; scores are recorded below.

### Temple approach

Reads as: a processional stair under a cliff.

Two worn gargoyles, a fallen marble offering drum, an urn, and rubble describe a roadside memorial below the protected stair. The stair-head shelf and trigger keep their clear space.

Set piece: **Processional memorial**, [640×400 capture](p4-m10/setpieces/processional-memorial.png).

Target failures: 5 → 0. Main-pin regressions: zero. Raw records: 1,238 → 951; expanded records: 1,838 → 1,937. Protected windows: 17; scores are recorded below.

### Passage test

Reads as: a bare ledge where one plant grows.

Three timber markers surround bones, broken jars, and a small gravel hearth at the ramp approach. The Test Plant remains the sole living green here.

Set piece: **Failed pilgrim bivouac**, [640×400 capture](p4-m10/setpieces/failed-pilgrim-bivouac.png).

Target failures: 3 → 0. Main-pin regressions: zero. Raw records: 298 → 69; expanded records: 358 → 406. Protected windows: none inside this region; scores are recorded below.

### Ragnar's cache

Reads as: a boulder with something behind it.

Two timber posts, a fallen panel, an excavated marble drum, a bedroll, and a loose pebble crescent suggest an abandoned excavation beside the original boulder and ruins. D1 requires this authored scene; the boulder, stairs, bag drop, hat, and whip retain their tuples.

Set piece: **Abandoned excavation**, [640×400 capture](p4-m10/setpieces/abandoned-excavation.png).

Raw records: 43 → 36; expanded records: 133 → 157. Props per 100 land cells: 2.08 → 29.17; dressed share: 0.365 → 0.646; top material: 0.917 → 0.927.

Target failures: unscored. The original boulder, stairs, bag drop, hat, and whip are retained. D1 overrides the earlier pebble-only recommendation.

## Protected windows

The eight scores compare with the frozen main baseline. Source windows and their FLOORS entries are unchanged. The whole test checks all 19 published shots.

| Window | Before | After | Delta | Unpainted non-black pixels after |
|---|---:|---:|---:|---:|
| screen02 | 98.4160% | 98.4160% | 0.0000 points | 0 |
| screen09 | 94.8418% | 94.8418% | 0.0000 points | 148 |
| screen17 | 93.7236% | 93.7236% | 0.0000 points | 59 |
| screen18 | 98.5798% | 98.5798% | 0.0000 points | 55 |
| screen19 | 97.0867% | 97.0867% | 0.0000 points | 0 |
| screen20 | 97.7035% | 97.7035% | 0.0000 points | 0 |
| screen21 | 93.9392% | 93.9392% | 0.0000 points | 0 |
| screen22 | 97.2583% | 97.2583% | 0.0000 points | 0 |

## Stand-ins and VQ items

The keep becomes a plank long hall. Exposed household furnishings leave; covered furnishings remain. Desks 205 fall from three to one, and desks 208 from six to one. All five covered wardrobes 307 remain. Green rock patches 92 fall from 10 to zero, and 94 from 17 to zero. Ten generated grey stumps become low rubble.

Thirty-three native spire records become 32: one Moriens stand-in becomes rubble, and eight eligible outcrops gain explicit decorative spire and pebble companions. Twenty-four retain their original tuples because the proposed companions fail the exclusion checks. A shared change for these protected outcrops is requested below.

VQ-025 and VQ-028 are claimed for regrading: cliff lips, hand-shaped headlands, sparse waterline stones, and irregular offshore rocks address the broken rim fringe. Witness pairs: [m10b-32 before](p4-m10/before/m10b-32.png), [after](p4-m10/after/m10b-32.png); [m10b-58 before](p4-m10/before/m10b-58.png), [after](p4-m10/after/m10b-58.png).

VQ-041 and VQ-042 receive the same cliff vocabulary at the lake. Open water remains 347:16, with textured frames confined to occasional shoreline cells. No retail shore glob 1537 through 1554 is present. Witness pairs: [m10b-10 before](p4-m10/before/m10b-10.png), [after](p4-m10/after/m10b-10.png); [m10b-12 before](p4-m10/before/m10b-12.png), [after](p4-m10/after/m10b-12.png).

VQ-061 is claimed for regrading: 22 decorative basalt pieces occupy existing cold cells beside the lava, and cliff-shore dressing continues around the lower rim. Every byte of the 54 original lava tuples remains. Witness pair: [m10a-54 before](p4-m10/before/m10a-54.png), [after](p4-m10/after/m10a-54.png).

VQ-027 remains inherited protected-relief debt: 336 quest-band cells remain below half visibility. Specified-black floor probes remain zero. Prop-black probes improve from 42 to 32; below-half map-cell share improves from 0.0164714 to 0.0156330; hidden share improves from 0.0083206 to 0.0076466. Frame-black mean improves from 0.0004408634 to 0.0004095734, and its 95th percentile from 0.0020839844 to 0.0019714844. Median minimum visibility stays 1.0. No new claim is made for the already accepted VQ-033, VQ-034, or VQ-057 repairs.

All 2,617 expanded anti-climb records retain their exact bytes. The 68 map-pin rows remain unchanged. Only their derived FIXED.DAT fingerprint is refreshed for the freshness check. Every other map’s raw records match the frozen baseline exactly. The two source crests with negative z are inherited portal records and retain their encoded baseline tuples.

## Shared requests and remaining boundaries

The rock-prefab substitution item is stopped at the shared inventory boundary. Every tested `ROCK_DRESSED` member contains excluded 301 bank frames 6 through 37; the diagnostic is [recorded](p4-m10/rock-prefab-exclusions.log.gz). Main could append at least four cliff-safe LV rock variants using 301 frames zero through five, local 386 transitions, and existing rubble, with the original 512-unit footprint. That family would allow the specified 40% rock-chunk substitution while respecting the 25% member-share limit. North and west loose ground is packed, the existing mass and skirt remain, and northern soil fans provide streaks. Tier-corner substitution also needs cliff-safe variants of 384, 386, 387, 388, and 452 before that item can proceed. No retail river-shore glob is an acceptable replacement.

Protected outcrops need a shared placement helper before their remaining companions can proceed. A proposed `Site.outcrop_companions(existing, pieces)` would allow decorative overlap with that one existing outcrop, constrain added paint to its existing footprint and height, preserve the original reached set, and prove that every quest-band standing and walking pose loses no visible pixels. It would continue enforcing windows, pins, frame validity, and the existing physical geometry. Existing decorative shape 908 and pebbles can supply the art; no new shape ID is requested.

No shared module, prefab definition, test, quest leg, pinned item, or shape ID changed. No merge, push, or shared installation write occurred. Main’s pre-existing local edits remain separate.

## Feedback, captures, and verification

The final `tools/build_artifacts.sh --record` has completed from the corrected source. It reproduces all six hashes in the frozen capture runner, including FIXED.DAT `70f90c1f867d5d41` and GLOB.FLX `ddf6b8083789b7b0`; `--verify` passes. The complete final-source estate is running after this rebuild. [Recorded build result](p4-m10/final-full-record-result.json).


Capture checkpoint: all 14 landmark photographs are committed, and 15 after views have landed. One after view from each of the 12 measured regions was opened and compared with its baseline; the sample shows no new capture-visible defect. `sample-inspection.json` records image hashes and findings, and the official capture checker passes all 12. The remaining tour runs in detached session 2282813, with commits every 30 captures. Detached session 2282815 performs the final recorded rebuild and complete final-source estate. The finisher updates this section only after all 126 after views and the permitted estate result are verified.


The follow-up unrestricted review found no actionable defects. Its focused checks passed, and its extra long-running suite and isolated builder were stopped. The final recorded build and complete final-source estate now run through the durable finisher while the separate frozen runner photographs the tour. Review output is preserved in `p4-m10/review.log.gz`; final counts remain pending.


The completed estate passed 56 of 58 files. Its schedule-visibility failure is repaired: exactly two new props leave Tyorvi’s and Thordis’s destination views, with every other expanded record preserved. `test_schedule_destinations.py` now passes all 201 assertions. Strict dressing and default visual verification pass on the 13,455-raw, 51,286-expanded build. The complete final-source estate rerun is arranged after the final recorded rebuild, with captures using the separate frozen runner. The report will close only when that rerun leaves the permitted integration-state failure.


The first resumed estate exposed three packed wall records and 56 roof fragments. The repair unpacks the wall chunks, excludes earth glob 264 because it contains three roof pieces, and replaces two ceiling-role crossing decks with flat wooden floor 163. The two-deck composition remains; ground-cell alignment moves the anchors by at most 64 units per axis. `test_map_hygiene.py 10` now passes all 10 checks. The corrected build has 13,457 raw and 51,288 expanded records, with 1.484575 expanded records per ground cell. Main’s other bounds retain zero regressions.


`docs/map-feedback/OPEN.md` reads “Nothing open.” This applies to every region; no viewer feedback note needs an answer.

The supplied `tour/m10/stops.json` is absent. The combined `m10a` and `m10b` lists provide all 126 stops, including the connecting ground and edge witnesses. Every launch uses official `tools/playtest-linux/tour_capture.py`, `LV_DISPLAY=:88`, `XDG_RUNTIME_DIR=/tmp/claude-1000/vq4-m10`, `usehighres=false`, and a fresh world per stop. The private runner copies game data and freezes all six artifacts, including GLOB.FLX. Its hashes are checked against the final recorded build.

| Capture batch | Recorded | Surface found | Landed |
|---|---:|---:|---:|
| before | 126 | 126 | 126 |
| after | 0 | 0 | 0 |
| setpieces | 10 | 10 | 10 |

PNGs and capture manifests are committed in the requested evidence directories, including all 126 baseline PNGs. Compressed engine logs accompany the captures. Baseline log collection began during the tour, so 110 baseline logs accompany 126 baseline images. The interrupted background build, log watcher, and capture chain were stopped on resumption. The surviving current set-piece batch has 10 landed captures; the after directory must be captured afresh.

Recorded build: HEAD rebuilt on resumption with `tools/build_artifacts.sh --record`; all six hashes match the frozen capture evidence. `--verify` passes. Builder sources match HEAD, existing glob rows are unchanged, and the appended manifest rows are retained in [the checkpoint](p4-m10/resume-head-check.json).
Strict dressing: zero failures and zero target failures.
Visual record: the first six-skeleton version exceeded the frame-black mean and p95 bounds. The replacement uses two skeletons, four timber posts, and the flat retail weapon frames, with [zero opaque black pixels in those weapon frames](p4-m10/flat-weapon-audit.json). Default visual verification now reports zero failures. `records` is re-pinned to 13,455 and `expanded_records` to 51,286 under the §4.2 budget exception. [The pin audit](p4-m10/pin-ratchet-audit.json) compares every bound with main. The owned-map rebuild preserves every other archived map byte; all six canonical hashes verify. A full recorded rebuild will confirm the same hashes during the final tour.
Estate: pending.

The first `codex exec review --base main` was blocked by bubblewrap’s `RTM_NEWADDR` permission error. The unrestricted retry found canonical hashes, the expanded-record pin, and Moriens’s material-patch limit. Canonical hashes are recorded, the expanded count is accepted under the explicit §4.2 exception and checked against the land budget, and the ruins patch now preserves main’s bound. The three requested replacement scenes were rebuilt, captured in fresh worlds, opened, and inspected at 640×400. Every capture landed at its exact requested position, with no paint-cycle warning. The yard camera moved north to expose its tools. [Retake checks](p4-m10/retake-checks.json) and [capture log](p4-m10/retake.log.gz) record the result. Follow-up review findings and the complete after tour remain pending.

## Commits

- `7b218cdb Pack Map 10 loose ground through the dressing module`
- `8fa3ebb0 Compose Map 10 landmarks, long hall, and cliff-shore lips`
- `9b64b70d Record Map 10 dressing baseline and verification checkpoint`
- `26211eab Shape Map 10 coves and restore interior dressing placement`
- `068c06a0 Checkpoint Map 10 captures and measured dressing constraints`
- `c625cbc7 Group low rubble and vary ground through the Vale`
- `6882c7b8 Record all 126 fresh Map 10 baseline captures`
- `7f3c4451 Document Map 10 compositions and remaining verification`
- `e9e00234 Finish authored courts, excavation camp, and lake remnants`
- `19f0911a Record composed-scene capture pass and review findings`
- `8a69ea32 Place bare timber and break the final Vale ground patches`
- `ccc37091 Record dressed Vale artifacts and preserve barren timber scenes`
- `6d255186 Finish the pilgrim hearth with a broken gravel margin`
- `fe840315 Ratchet Map 10 dressing and visual quality measurements`
- `9dddfed5 Verify visual ratchets against frozen Map 10 artifacts`
- `b5009938 Verify recorded artifacts and preserve Map 10 geometry contracts`
