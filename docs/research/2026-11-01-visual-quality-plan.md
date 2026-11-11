# Plan: the visual-quality pass after the screenshot tour (2026-11-01)

**Status:** revised after Fable's review, which approved it with changes
(2026-11-01, run on API credits; `2026-11-01-visual-pass/fable-plan-review.md`).
§11 lists the changes adopted, and they override the sections above where
the two disagree. Phase 0's backlog and audit tools are done (`1b0171d`).
Douglas's go-ahead and the decisions in §6 are still pending.
**Input:** the screenshot tour of 2026-11-01, which has 370 in-engine captures,
each reviewed (`https://devhost.invalid/lostvale-art/tour.html`; data
in `~/projects/lv-art-review/tour/<area>/review.json`). The tour
logged 111 high, 399 medium and 288 low issues. By category: void 207,
sparse 125, placeholder 78, transition 69, paint 68, architecture 63,
repetition 63, seam 45, clutter 32, float 27.

**Scope** (Douglas's items 1-4, in order):

1. Specific defects, and black floor on the quest route.
2. The Avatar hidden behind near walls on the quest route.
3. A void pass on every map: edges, holes, slits, black filler.
4. A dressing pass: sparse areas, stand-in art, hard transitions, floating
   props.

## 0. What the tour already tells us about causes

- **Most "void" on the LV maps is our own filler, not missing data.** Shape
  564 frame 2 is a flat black plate. The builders lay it as filler, and it
  draws as walkable black:

  | Map | 564:2 plates on our maps | Retail |
  |---|---|---|
  | 9 | 375 | 0 |
  | 10 | 2,426 | 0 |
  | 11 | 2,792 | 0 |
  | 13 | 785 | 0 |
  | 17 | 743 | 0 |
  | 18 | 527 | 0 |
  | 39 | 274 | 0 |

  There are also 35:10 black tiles: 30 on Map 9, 88 on Map 11 and 26 on
  Map 18. Map 8's 1,714 plates of 564:2 and 1,052 of 334 are all retail.
  Fixing the filler at its source in the builders is one change per map,
  not hundreds of hand fixes.
- **Map 8's black shelves, trench and spitter corridor are retail
  geometry, identical to the pristine FIXED.DAT.** Douglas blessed only two
  Map 8 terrain departures (2026-10-08). Every Map 8 item is therefore a
  decision, not a default fix (§6).
- **"Avatar hidden" has two different causes.** One is tall near walls,
  which we chose: Map 18's 120-tall anti-climb walls and Map 9's 96-tall
  hall walls. The other is retail roofs and ceiling plates (Map 8). The
  first is ours to change; the second is the same retail decision as above.
- **Map edges.** The camera sees past every map edge that has no backdrop
  (Map 10's east and south rims, Map 13's valley, Map 17's cloud plate,
  Map 39's treeline). U8 cannot hold items at negative x or y, so the
  north and west edges at 0 can't be backed. Douglas accepted Map 13's
  north edge on 2026-10-25. Every other edge can carry a "skirt": ground
  beyond the walkable area that fills the camera's view and is never
  reached.

## 1. Roles

| Who | Model / tool | Used for |
|---|---|---|
| Orchestrator (me) | this session | Slicing, contracts between slices, merges, `tools/integrate.sh`, records (`TODO.md`, `HANDOFF.md`), Douglas's review pages |
| Implementation subagents | `task` agents, each in its own git worktree | One map-builder owner per phase (the builders are the conflict surface), plus verifiers |
| Codex agents | `codex exec -C <worktree> --sandbox workspace-write -m gpt-6.1-sol` (non-interactive, own branch) | The audit tooling (§2), independent fixes with crisp specs, and `codex exec review` on each slice branch before merge |
| Fable | `anthropic/claude-fable-5-1` | Reviews this plan, each phase's slice design, the art direction for phase 4, and the final report |
| Astra | `openai-codex/gpt-6-astra` (image input) | Visual assessment: before/after capture pairs per issue, verdicts, art-direction checks. Its provider limit stops it after about 12 minutes (`docs/research/2026-10-12-organic-maps.md` §8), so each run gets about 15 image pairs and writes its verdicts to a file as it goes |

**How each is invoked** (checked 2026-11-01). The `task` tool no longer
accepts a model override, so the other models run as CLI agents:
- **Codex:** `codex exec -C <worktree> -m gpt-6.1-sol --sandbox workspace-write "<spec>"`.
  It answered on 2026-11-01. Reviews use `codex exec review`.
- **Astra:** `codex exec -m gpt-6-astra -i <before.png> -i <after.png> "<rubric>"`
  (Codex's configured default model). It answered on 2026-11-01. Each run
  is one batch of pairs, and its verdicts are written to a file.
- **Fable:** `omp -p --model anthropic/claude-fable-5-1 --auto-approve "<prompt>"`.
  Rate-limited as of 2026-11-01 (see Status).

**Rules carried over:**
- Worktree setup as in phase E: `shared/data` is a real directory with each
  gitignored entry symlinked, and every write uses an absolute path.
- Every agent runs ScummVM on its own display and `XDG_RUNTIME_DIR`. Since
  `b8e8e0e`, `session.sh` scopes `stop` to its own display.
- The `verifier` agent standard applies to anything that touches maps.

## 2. Phase 0: backlog and measuring tools (before any fix)

1. **Backlog.** Merge the eight `review.json` files into one
   `docs/research/2026-11-01-visual-pass/backlog.json`.
   - Merge duplicates. One root cause seen from ten stops (Map 9's dais
     floor appears 11 times) is one item.
   - Give each item an id, the issue, its stops, a root-cause guess, the
     owning builder (`build_map_NN.py`), its phase (1-4), whether it is
     retail or LV (checked against the pristine FIXED.DAT), and whether it
     touches a 1994 shot window.
   - Done by a Codex agent; I review the merge.
2. **Astra confirmation of the high items.** About 111 high issues collapse
   to around 40 root causes. Astra looks at each one's captures and either
   confirms it, downgrades it, or marks it a false positive. Example of what
   to catch: the ghost follower, which is not map art.
   - Separately, a subagent replays the "Avatar invisible" claims in
     ScummVM, because some of them were inferred from map data rather than
     seen on screen.
3. **`void_audit.py`** (Codex). It renders the built map offline at camera
   positions on a grid over every reachable cell. It reuses
   `vignette_paint` / `item_sorter`, the same painter `test_vignettes`
   already trusts.
   - Per frame it reports the share of black and void pixels and where they
     are.
   - Per map it produces a heatmap and a ranked list.
   - Its number is checked against in-engine captures at 10 tour stops
     (target: within 2 points), so we know it can be trusted.
4. **`avatar_visibility.py`** (Codex). For every reachable cell, on a
   32-unit lattice, and for the Avatar's walk and stand frames, it measures
   how much of his sprite stays visible after sorting (the `item_sorter`
   port, with the roof cut). It outputs a per-map heatmap and the list of
   quest-route cells (`test_route_reach` legs) where less than 50% of him
   shows.
5. **Baseline.** Run both tools and archive the numbers. They become the
   before for every phase and later the permanent tests.

**Gate:** Fable reviews the backlog and the tools' method. I fix what it
flags, then phase 1 starts.

## 3. Phase 1: specific defects and black floor on the quest route

One slice per map; the slices run in parallel, each with its own builder:

| Item | Map | First hypothesis to check |
|---|---|---|
| Skull ring (745 at 4159,4895,80) not drawn, Avatar vanishes on it | 13 | Draw order or roof cut. A ring under a SOLID/ROOF neighbour, or z inside a glob tier. Debug in-engine with the Object channel. The screen14 vignette's render check never covered the in-engine draw |
| Message Scroll hidden behind a double-height column | 17 | Move the column or the plinth one cell along the view ray, measured against the screen11/12 windows. Make the plinth read as a pedestal |
| Black walkable floor east of the screen10 dais | 9 | The 30 tiles of 35:10 and 6 plates of 334:? left over from the reconstruction sit on top of the real 301 floor. Remove those outside the shot window |
| Rock island between the passages draws as a black pit | 18 | Missing top face and south/east faces. Give it faces, or replace it with solid rock that draws |
| Black trench across the raised tier (x 9600-10200, y ~19700) | 10 | 564:2 plates sorting over the z 104 tier edge. Drop them under the tier, or remove them |
| Ruin pieces standing on black void west of Ragnar's cache | 10 | Move the props onto ground, or extend the ground under them |
| Island deck hole; black band under the processional lane | 10 | Missing tiles. Fill them |
| Arrival channel black between landing and pier; south void bay | 17 | Cloud-sea channel art, or a cloud fill. The landing's gold needs an edge |
| Map 11 pad room: lamp in the sealed doorway, spire clusters as "sealing boulders", no visible pad | 11 | Move the lamp, use retail boulder art, add a pad marker |

**Acceptance:**
- Each item is re-captured with `tour_capture.py` at its tour stops and
  graded by Astra as fixed.
- `void_audit` shows a lower void share at those stops.
- The full estate passes, with 1994 shot floors unchanged.
- `codex exec review` passes on the slice branch.
- A verifier walks the affected quest legs in ScummVM.
- Douglas sees a before/after card page.

## 4. Phase 2: the Avatar hidden behind near walls (quest route first)

**Policy, for Fable to review:** no walkable spot on a quest leg may leave
less than 50% of the Avatar visible. Elsewhere, minimise occlusion. Fixes,
in order of preference:

1. **Lower the near walls.** These are the south- and east-facing walls on
   the playable side: Map 18's Transition Hall 120 → one course where they
   face the hall, Map 9's hall south and east walls, Map 11's hub-to-Air
   corridor. That is how retail U8 treats near walls in its interiors.
   Check retail rooms for the standard first: a Codex agent measures the
   near-wall heights of retail interiors.
2. **Pull the walkable edge one cell in** where a tall face is required:
   the Map 10 rim walls and the temple pit.
3. **Roof-cut flags** where a ceiling is the culprit. This is an LV item
   only; Map 8's retail roofs are covered in §6.

**Hard constraint:** the anti-climb purpose of Map 18's walls
(`map-geometry.md`, `test_route_reach`) must survive. A lowered wall that
becomes climbable is a sequence break. `exact_reach` proves every change.

**Acceptance:** `avatar_visibility.py` passes on every quest leg and
becomes a permanent test in the estate. Plus in-engine re-captures, Astra
grading and verifier walks, as in phase 1.

## 5. Phase 3: the void pass, every map

Driven by `void_audit`. The fix classes:

1. **Filler plates.** Replace 564:2 and 35:10 where they draw as floor,
   with the area's own ground, rock or cloud material. Where black is
   intended (a chasm), make sure nothing walkable is drawn black.
2. **Edge skirts.** On every south and east map edge the camera can see,
   lay non-walkable backdrop out to the map bounds, in the region's
   material: rock shelves and cliffs on Maps 10 and 13, the cloud sea on
   Maps 13 and 17, trees and ground on Map 39's south edge. The
   north and west edges at 0 can't take items; accept them where they are
   seen, as the Map 13 summit was.
3. **Holes and slits.** Fill gaps between cliff blocks and missing terrace
   tops. Give the cloud sea an edge where it meets rock.
4. **Water.** Re-read the lake (347:16 draws near-black): use a lighter
   retail water frame or the Lake's own palette, and add a shore
   transition.

**Acceptance:**
- `void_audit` shows the void share per frame at reachable cameras below an
  agreed threshold per map. Proposed: no reachable frame over 10% black
  outside an explicit allow-list (true chasms, the accepted north edges).
- It becomes a permanent test, with a ratchet like
  `KNOWN_FLOATING_LV_TELEPORTS`.
- The 1994 shot floors hold. A skirt that shows in a shot window must match
  the shot, or stay out of the window.
- A full re-tour, with Astra grading void items before and after.

## 6. Decisions only Douglas can make (asked before the phase they gate)

1. **Map 8's retail look**, for phases 1-3. The trench, the shelves, the
   seam doorways and the spitter corridor are retail geometry with retail
   black plates and roofs. Options:
   - leave them as retail;
   - change only what hides the Avatar on the quest route;
   - restyle them.

   The same question applies to Map 39's retail treeline edge.
2. **Map 11's Water section has no water** (the tiles were removed on
   2026-07-04 to stop drowning). Options:
   - decorative non-SEA water;
   - leave it dry and dress it differently.
3. **How far phase 4 goes**: a dressing density target, or "make each
   region read as its place" by area.

## 7. Phase 4: dressing and stand-in art

1. **Art direction first.** Fable writes a per-region direction: what each
   area should read as, its props palette and its density targets.
   - It is grounded in retail density measurements; `build_map_13`'s
     dressing comment already measured retail cave densities.
   - It builds on the 1994 shots and the 2026-10-12 organic-maps research
     (Fable's earlier macro layouts).
   - Astra checks a few offline mock renders per region against the
     direction before any builder work.
2. **A shared dressing module**, so every map dresses by the same rules
   instead of each builder inventing its own. Rules: retail densities,
   clustering, nothing in shot windows, nothing on routes,
   `test_paint_cycles` clean. It generalises Map 13's
   `build_dressing`.
3. **Stand-in replacements,** from the tour list:
   - dungeon brick and shape-15 blocks in the cloud city and on the
     cliffs;
   - outdoor desks;
   - the castle keep among huts;
   - the 328/329 frame-5 tapestries that read as portcullises;
   - spire clusters used as boulders;
   - point-down boulders (796) and stalactites (186) with no ceiling;
   - grass cubes on cliff tops;
   - the pale Vale-return slab on Map 8;
   - the Lord British apparition visible in Mythran's house before its
     scene.

   Retail-art swaps come first. New art only where nothing in retail fits,
   through the art track (`docs/art-track.md`, next IDs 887 and 893+).
4. **Transitions.** Verges and rims where materials meet: dirt and lava
   patches, gold and cloud, the cloud sea and rock.

**Acceptance:** an Astra-graded re-tour per region against Fable's
direction. Douglas signs off on a card page, as in phases D/E.

## 8. Integration and verification cadence (every phase)

1. Each slice lands on its own branch.
2. `codex exec review` checks the branch.
3. I merge it. Map pins are resolved per map, never by blindly picking
   one side (the npc 111 lesson).
4. `tools/integrate.sh --record`.
5. The full estate runs.
6. The console build's detection is refreshed if EUSECODE moved.
7. A verifier pass runs in ScummVM: affected quest legs walked, the pads
   and EggReapply behaviour on the affected maps, and log hygiene.
8. A re-tour of the affected stops, graded by Astra.
9. A before/after card page goes to Douglas.
10. `TODO.md` / `HANDOFF.md` are updated and the work committed.

A full single-build quest replay runs once, at the end of phase 4.

## 9. Risks

- **1994 shot regressions.** Any change visible in a shot window can cost
  score, as the Map 13 neck widening did (-4.6). Every slice reports the
  `test_vignettes` windows it touches.
- **Map pins and savegames.** Pins are frozen. FIXED reloads on map entry,
  so old saves pick up map changes. Quest items are cleaned by EggReapply
  only on a pad arrival.
- **Paint cycles.** New dressing near the Avatar's paths can knot. Every
  dressing slice runs `test_paint_cycles` and an in-engine check with the
  Object channel on.
- **Astra's usage limit.** Short runs, checkpointed to files. When it
  stops, a second run resumes from the file.
- **Scope creep.** Medium and low items outside the phases' classes stay in
  the backlog for later; they are not fixed opportunistically.

## 10. Order and size

| Phase | Agents | Parallel slices |
|---|---|---|
| 0 | 2 Codex (tools, backlog), 1-2 Astra, 1 verifier, 1 Fable | |
| 1 | per map | about 6 |
| 2 | per map | about 4 |
| 3 | per map, then a re-tour | about 7 |
| 4 | Fable direction, then per map, then a re-tour | about 7 |

Each phase ends with Douglas's card review before the next begins.

## 11. Changes adopted from Fable's review (2026-11-01)

These override the sections above where the two disagree.

1. **Black filler is not the cause.** The 564:2 plates are `void_floor()`'s
   last-resort cover (`lv_furnish.py:171-291`), so phase 3's levers are a
   backdrop plus 497/498 curbs, not swapping the plates.
   - The void metric splits into two numbers: **walkable black** (tolerance
     0, through `exact_reach`) and **frame black share**.
2. **A per-map raw-record gate.** Replacing 256-unit plates with 128-unit
   tiles would put Map 10 at about 27.8k of the 32.5k object-ID cap before
   phase 4 adds anything.
   - Every phase reports its record count per map.
   - Skirts use glob eggs or 256-unit plates (564:0 exists; recolours go
     through the art track).
3. **Phase 2 is our standard, not retail's.** Retail does not lower near
   walls: Tenebrae uses 10/15 at z 0/48/96 on Maps 3/5/39, and the caves use
   26/27/32 at 0/48/104/160.
   - The 50% rule is calibrated on a retail route first.
   - Drawn courses are lowered behind a coincident 497/498 backstop, so the
     collision is unchanged.
   - Map 18's breach line is a special case: `BREACH_PIECES` q307, the full
     stack over x 2688..2943 before the breach, `test_crack_geometry`.
4. **Map 13's skull ring: check the engine first.** Offline the ring and
   the Avatar draw at m13-26 (`overdrawn()` = 0), but the engine shows
   neither. Check the engine's actual post-teleport Avatar and camera
   before touching the map.
   - `tour_capture.py` must log the actual coordinates after the teleport.
     This is also a precondition for `void_audit`'s calibration.
5. **A three-valued retail field:** `lv`, `retail-exposed-by-lv` and
   `retail`.
   - Retail black that only our cuts expose defaults to a fix: m08-09, 12,
     14 and 49, the trigger-200 pocket, and Map 39's treeline seen from the
     lane.
   - Only retail black visible on retail routes goes to Douglas (§6.1).
6. **§9 savegame correction.** The map a save was made on keeps its saved
   items. Every verifier walk therefore starts from a fresh game, or reaches
   the map by a map switch.
7. **Calibrate thresholds on retail first.** Run `void_audit` and
   `avatar_visibility` on retail Maps 3, 5, 8 and 22 before adopting any
   threshold. A flat 10% black per frame would fail retail caves while
   passing a black floor.
8. **One owner per map carries phases 2 and 3 in sequence.** Lowering a
   wall exposes the void behind it, so the phase 3 baseline is taken after
   phase 2 lands.
9. **Repetition (63 items) moves into phase 4** with its own acceptance: a
   tile-period measure per region, against retail. It was the organic-maps
   research's top cause.
10. **Shot-bound backlog items** carry the shot's window name and
    `test_vignettes` `FLOORS` score. Map 13's black slabs at m13-23..27 are
    screen14's own `SHOT_CUTS` pieces, so they need a shot-fidelity check
    before any change.

**Phase 0 status:**
- Backlog: 198 items, 39 of them high.
- Audit tools: validated against 13 captures, within 0.14 points on
  near-black; visibility agreed at 10 of 10 stops.
- Astra's confirmation of the high items is running.
- Still to do before phase 1:
  - the retail calibration (change 7);
  - the actual-coordinates logging in `tour_capture.py` (change 4);
  - splitting the walkable-black metric in `void_audit` (change 1);
  - tagging the backlog with the retail, `retail-exposed-by-lv` and shot
    fields (changes 5 and 10).

  Codex does all four.
