# Playtest — walking Map 10's quest spine (2026-09-18)

The outstanding next action from HANDOFF: the 2026-09-15 landscape pass was
verified by exact-reach floods and fourteen debug-teleport screenshots, never
by walking. Two of its changes sit on the quest spine and were UNWALKABLE
before it — the corridor to the Passage Test grounds (was 24-unit terraces)
and the stair to Ragnar's boulder crown (was 16/24-unit steps). Both are now
walked, with the Avatar's z reported at every step.

Fresh world, the canonical build (`FIXED.DAT e9f6cc60…`, the other three
artifacts unchanged), the 640×400 canvas, plates cropped at `+565+336`,
`usehighres=true`; `shared/u8-lv-patched/FIXED.DAT` checked against
`shared/build/ARTIFACTS.sha256` before the walk. No cheats beyond
`MainActor::teleport` to reach the foot of each feature, and
`ObjectManager::objectInfo`/`findShape` plus `debugflag_enable Object` to
read state.

**How the segments were entered.** Route 1 was walked continuously from the
arrival court. Segments 2–6 were entered by a debug teleport to the track
point at the foot of the feature and then walked. That is a valid terrain
test and it is not a continuous playthrough. `justTeleported` is not in play
for any of it: the only egg on these routes is the Map 13 teleport past the
cloud terrace's gate, and the Avatar reached it by walking roughly 1,200
units from where he was set down, so it hatched on a real walk-in (R2c).

## Verdicts

| ID | Segment | Verdict |
|---|---|---|
| R5 | The corridor ramp to the Passage Test plant — z 0 → 72, no stall | **PASS** |
| R6 | The cache stair to Ragnar's boulder crown — z 0 → 56, no stall | **PASS** |
| R1 | Arrival court → Hoskuld's east gate → the gathering slab, walked whole | **PASS** |
| R2a | Hoskuld's south gate | **PASS** |
| R2b | The cloud terrace, the 8-unit riser onto it | **PASS** |
| R2c | The terrace's locked gate (lock 170) is walked around, and the lane past it teleports to Map 13 | **PASS as a route, FINDING as design** |
| R3 | Ezrekal's stockade door, and Ezrekal reached inside | **PASS** |
| R4 | The lake pier to the Passage Stone — z 8 the whole causeway | **PASS** |
| F1 | The figures on the lake: cause chased 2026-09-19, an engine map-0 carry-over, not LV content | **DIAGNOSED** |

## R5 — the corridor ramp to the plant — PASS

Teleport to (12799, 24575, 0), the track's Moriens point, then walk
`12799,26367  12799,28159  12799,28800  12800,29300` at walk gait:

```
-> (12799,26367)   (12799,24575,0) … (12799,26335,0)
-> (12799,28159)   (12799,27855,0)  (12799,28191,8)
-> (12799,28800)   (12799,28655,32) (12799,28783,40)
-> (12800,29300)   (12799,29351,72)
final: (12799, 29351, 72, 10)
```

The z sequence 0 → 8 → 32 → 40 → 72 is the evidence: every riser the walking
actor took was inside `scanForValidPosition`'s 0/±4/±8 probe, and the eight
8-unit rows that replaced the two 24-unit terraces carried him the whole way.
No stall, no probe, no jump. `R5-passage-test-plateau.png` is the Avatar on
the plateau with the plant at his feet.

## R6 — the cache stair to the crown — PASS

Teleport to (17350, 25727, 0), east of the stair's lowest column, then walk
west:

```
(17350,25727,0) → (17150,25727,16) → (16750,25727,40)
               → (16530,25727,56) → final (16456, 25727, 56, 10)
```

The crown is z=56 and `RAGNAR_BAG_DROP` is (16447, 25727, 64), so the Avatar
stands 9 units from the drop point on the surface the bag pops 8 above.
Four bursts, no stall. `R6-ragnar-boulder-crown.png`.

One look note: the boulder crown reads as part of the rim rock from the east
camera, so the stair appears to climb into the cliff rather than onto a
boulder. The stair itself is unmistakable.

## R1 — arrival to Hoskuld's gathering slab — PASS

Walked continuously from (13311, 2943) through the eight `TRACKS` waypoints
to (5247, 7167), final (5208, 7128, 0, 10). The east gate (the palisade at
x=8191, opening y 7551..7935) was crossed on the track without a probe.
`R1-hoskuld-gathering-slab.png` is the endpoint: the clan hall, a hut, a
villager, the worn track.

The first attempt at this route ran at the harness's default RUN gait and
could not cross the village at all — see harness anomaly 1.

## R2a — Hoskuld's south gate — PASS

Teleport to (5247, 10700, 0) inside the palisade, walked south through the
opening (x 4991..5375 in the fence at y=11263) to (5247, 11980). Five bursts,
no stall, no probe. `R2a-hoskuld-south-gate.png`.

## R2b / R2c — the cloud terrace and its gate — PASS, with a finding

Teleport to (7167, 22300, 0) on the track, walked south onto the terrace: z
went 0 → 8 at the riser and the Avatar crossed the flagstone at z=8.
`R2b-cloud-terrace-gate.png` shows him on it with the locked gate ahead and
the canyon walls either side.

Walking further south on the track's own line wedges him at (7167, 23420, 8).
That is correct: the gate box is (7040..7168] and the track runs at x=7167,
straight into it. The gate's lock is 170, which matches no key on any map, so
the way is meant to be the open lanes at (6911..7040] and (7168..7295].

**Walking the east lane fires the Map 13 teleport.** From (7247, 23556, 8) the
next position read was (4096, 11776, 0) on **map 13**. So the vale → cliffs
transition works on a player walk with no debug teleport, and it is reachable
without the Key to the Clouds by stepping one tile around the gate. This is
the walk-around that `TODO.md` §6 and the 2026-07-31 hardened-gates note
predicted; it is now demonstrated rather than inferred.

## R3 — Ezrekal's stockade — PASS

Teleport to (14250, 12550, 0) east of the stockade, walked west through the
opening in the east wall (x=13983, y 12415..12671) into the enclosure.
Reaching Ezrekal's post then needed a detour: his reagent bench (shape 208 at
(13568, 12544), a 96×160 box spanning y 12384..12544) sits across the straight
line from the door to the bedroll, and the straight-line walker pressed into
its north face at (13534, 12378) until it gave up. Routing north of the bench
and back down reached (12834, 12518) — 4 units from Ezrekal's start point.

A player steps around a table without thinking about it, so this is a walker
limitation. It is worth knowing that the door-to-bedroll line is not clear.
`R3-ezrekal-stockade.png` shows the Avatar inside with Ezrekal, the bedroll,
both benches and the potions.

## R4 — the lake pier to the Passage Stone — PASS

Teleport to (13887, 20700, 0) on the south shore, walked north up the
causeway: z went 0 → 8 at the pier's step and held 8 for the whole 2,300-unit
crossing, then 16 on the island deck beside the stone at (13888, 18368, 8).
Sixteen bursts, no stall.

HP stayed at 30 the whole way. The two water-zombie eggs the pier threads
between (12800, 19456) and (14592, 19200) did not hatch: `findShape 142`
returns 8 ghouls, all on map 31. The crossing is meant to be dangerous and on
this run it was not.

`R4-lake-pier-island.png`, and `R4b-island-figures-3x.png` at 3×.

## Findings that were not part of the plan

1. **Two figures stand on Map 10's lake island and pier that no map places
   there.** They are base-game NPC sprites, and the cause was chased on
   2026-09-19: `docs/2026-09-19-map0-limbo-carryover.md`. Short version —
   the first map switch of a session routes the Avatar through map 0, U8's
   limbo; map 0's `NONFIXED` entry holds 63 records describing base-game
   NPCs; `World::switchMap` skips the writeback and the fixed-item unload
   whenever the old map number is 0, because `CurrentMap::getNum()` cannot
   tell "no map loaded yet" from "currently on map 0"; so all 63 ride into
   the destination map and are written permanently into its dynamic item
   list at the next switch. On Map 10 that is seven robed figures (shape
   200) and four ghouls (shape 142), two of which land on the lake.

   This report originally called it "an actor whose map is 12 renders on Map
   10". That was wrong twice over. The rendered object is a `Container`, not
   the actor — item 55 carries `ef: 0x100` with no `EXT_INCURMAP`, while its
   twin carries `ef: 0x2` — and the cause is the map-0 carry-over, not an
   actor-filter fault. `current_map.cpp:217` filters actors by map correctly.

   **It is not LV content and a player does not see it.** Every plate in
   this report was taken after a debug teleport, so the figures in
   `R4-lake-pier-island.png` and `R4b-island-figures-3x.png` are an artefact
   of how the session was entered. `R4c-map0-phantoms-on-the-lake.png` is the
   same thing reproduced from a new game in four console commands.

2. **Map 13 has no southern edge, and the Avatar walks off it.** After the
   gate bypass (R2c) the walker kept its heading and carried him from the
   arrival at (4096, 11776, 0) to (4368, 17152, 0) — 5,400 units south, at
   z=0, through pure black. `build_map_13` places nothing below y=13823, so
   the last 3,300 units were floorless void walked at the bottom of the world.
   `R2c-map13-after-gate-bypass.png` is the Avatar alone on black. This is the
   same class as the Map 8 south route in `TODO.md` §3; it was not pursued
   here because it is Map 13's business.

3. **The east-gate approach is the only part of Map 10 that needed probing,
   and it was the gait, not the map.** See harness anomaly 1. Terrain there is
   continuous z=0 barren ground and the only items within 800 units are the
   track tiles, the palisade and its posts.

## Harness anomalies

1. **A running Avatar refuses the 8-unit step a walking one takes.** The first
   route-1 attempt ran `walkto.py` at its default RUN gait (240 px offset).
   Inside Hoskuld's palisade it could not move west across the worn-earth
   track for ten probe cycles: every advance came from the 8-direction probe,
   which uses a ~156 px offset and therefore walks. `R1b-run-gait-wedge.png`
   is the Avatar there on open, empty ground with the palisade behind him. The
   same ground at `--walk` crossed at ~500 units per burst with no stall.
   Track tiles (shape 425) are `SI_FIXED|SI_SOLID|SI_LAND` 8 units tall, so
   stepping onto one is an 8-unit rise. **Walk every leg that climbs
   anything.** Recorded in `.claude/skills/playtest/traps.md`.

2. **The backpack gump reopens by itself and eats the walk drag.** It was open
   on three plates and re-opened at least twice more during walking. It sits
   over the screen centre, which is where `nav.walk` puts the cursor, so a
   right-drag at walk magnitude lands on the gump instead of the world and the
   Avatar does not move. Close it with `i`. Escape opens the Pagan menu
   instead, which then swallows the next keypress.

3. **`pgrep -f` matches the shell running it.** `pkill -f 'walkto.py'` killed
   the calling Bash tool (exit 144). Bracket a character: `walkto[.]py`.
   Recorded in traps.md.

4. `session.sh dbg` is still dead; `dbg.sh` used throughout, at ~5 s per
   console command, which is what makes a route take minutes.

## Disk changes

- `docs/playtest-2026-09-18-map10-walk.md` and its screenshot directory.
- `.claude/skills/playtest/traps.md` — the run-gait and `pgrep` entries.
- `tools/playtest-linux/nav.py` — the 2026-09-18 transport rewrite committed
  (it was uncommitted at the start of this session).
- No artifact moved. `shared/build/` and `shared/u8-lv-patched/` untouched.
- `~/.config/scummvm/scummvm.ini` unchanged (`usehighres=true`).
- The playtest session was stopped at the end.
