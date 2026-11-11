# Playtest — Map 10's quest spine re-walked on the fixed engine (2026-09-19)

A repeat of `docs/playtest-2026-09-18-map10-walk.md` on the engine with the
map-0 guard fix (`docs/2026-09-19-map0-limbo-carryover.md`), to confirm the
terrain results hold and that the limbo phantoms are gone from a walking
session rather than only from a four-command acceptance test. Segment
definitions and coordinates are yesterday's; they are not repeated here.

Fresh world, the canonical build (`FIXED.DAT e9f6cc60…`, no artifact
rebuilt), ScummVM from the 2026-09-19 build, the 640×400 canvas, plates
cropped at `+565+336`. Cheats confirmed on by reading the reply. Route 1
walked continuously from the arrival court; the other five segments entered
by teleport to the track point at the foot of the feature, as yesterday.

## Verdicts

| ID | Segment | Verdict |
|---|---|---|
| P | No limbo phantoms on Map 10, before and after the walk | **PASS** |
| X5 | The corridor ramp to the Passage Test plant | **PASS**, every riser resolved |
| X6 | The cache stair to Ragnar's boulder crown | **PASS**, every riser resolved |
| X1 | Arrival court → Hoskuld's east gate → the gathering slab | **PASS** |
| X2a | Hoskuld's south gate | **PASS**, no probe |
| X2b | The cloud terrace and its 8-unit riser | **PASS**, no probe |
| X3 | Ezrekal's stockade door, and Ezrekal's post inside | **PASS** |
| X4 | The lake pier to the Passage Stone | **PASS**, no probe |

## P — the phantoms are gone

Measured on Map 10 before the first leg and again after all six segments:

| Query | 2026-09-18, same spot | today, before | today, after |
|---|---|---|---|
| `findShape 200` | 16 found, 7 Container | 9 found, 0 Container | 9 found, 0 Container |
| `findShape 142` | 8 found, 4 Container | 4 found, 0 Container | 4 found, 0 Container |

Nine is right: seven base-game actors plus npc 114 and npc 116, Map 10's own
stand-ins. The session made four map loads (3, 10, 0, 10) and the log carries
one `Unloading map 0`, the line that only prints inside the fixed guard. The
map-0 transit is the Guardian's first appearance, so this session exercised
the exact path that used to deposit the 63 limbo items.

`X4-lake-pier-island.png` is the plate that carries this: the island deck
with the Avatar alone on it, where yesterday two robed figures stood.

## X5 — the corridor ramp — PASS

```
-> (12799,28159)   … (12799,28095,0)  (12799,28175,8)
-> (12799,28800)   (12799,28415,16) (12799,28655,32) (12799,28735,40) (12799,28815,48)
-> (12800,29300)   (12799,29055,56) (12799,29215,64) (12799,29295,72)
final: (12799, 29295, 72, 10)
```

z reads 8, 16, 32, 40, 48, 56, 64, 72 — the eight 8-unit rows that replaced
the two 24-unit terraces, every one of them resolved in a separate position
read. Yesterday's run crossed the same ramp but skipped rows between reads
(0, 8, 32, 40, 72), so this is the better evidence. No stall on the ramp.

## X6 — the cache stair — PASS

```
(17350,25727,0) → (17278,25727,8) → (17134,25727,16) → (16918,25727,32)
                → (16630,25727,48) → (16448,25727,56)
final: (16448, 25727, 56, 10)
```

One unit from `RAGNAR_BAG_DROP` (16447, 25727), on the crown the quest bag
pops 8 above. Four legs, one short stall at a waypoint, none on the steps.

## X1 — arrival to the gathering slab — PASS

Five legs from (13311, 2943) through the east gate to (7935, 7807) walked
with no probe at all. The sixth, the 792-unit hop to (7679, 7039) inside the
palisade, exhausted its budget oscillating around the waypoint at
(7639, 6783); a fresh `walkto` invocation from there reached the slab in
three legs, `final: (5239, 7159, 0, 10)`. The same leg needed probing
yesterday. Terrain there is continuous z=0 barren ground and the only items
within 500 units are four 32-unit track tiles, so this is the walker's stall
counter, not the map. See harness anomaly 2.

## X2a, X2b, X3, X4 — the confirmations

- **South gate** — three legs, no probe, through the opening in the palisade
  at y=11263 to (5247, 11980, 0). `X2a-hoskuld-south-gate.png`.
- **Cloud terrace** — three legs, no probe, z 0 → 8 at the riser,
  `final: (7167, 23420, 8, 10)`. `X2b-cloud-terrace.png` shows the Avatar on
  the flagstone beside the keyless gate.
- **Ezrekal's stockade** — the Avatar walked in through the east opening on
  the first attempt; the walker then exhausted its budget oscillating in the
  doorway, which is what `X3-ezrekal-stockade.png` shows (inside the
  enclosure, bedroll and both benches visible). A re-run routed north of the
  reagent bench reached `final: (12814, 12506, 0, 10)`, 40 units from
  Ezrekal's post, in six legs with no probe at all. Yesterday's run needed a
  detour too; giving the detour up front removes every stall.
- **Lake pier** — four legs, no probe, z 0 → 8 at the step, held 8 the whole
  2,300-unit causeway, 16 on the deck beside the stone.
  `final: (13887, 18396, 16, 10)`, hp 30 throughout. The two water-zombie
  eggs did not hatch, as yesterday.

## Findings that were not part of the plan

None. Every terrain verdict from 2026-09-18 reproduced, and the two findings
from that report are both resolved or recorded: the lake figures are fixed
(above), and Map 13's missing southern edge was not revisited.

## Harness anomalies

1. **The first teleport of a session fires the Guardian cutscene.** The
   Avatar goes into stasis, hops to map 0 for about ten seconds and comes
   back. A walk started inside that window pushes a frozen Avatar on the
   wrong map, which is very likely what made yesterday's route 1 open with
   `BUDGET` on a 638-unit hop. Teleport, wait 20 seconds, confirm `m: 10`,
   then walk.
2. **A leg that exhausts its budget oscillating clears on a fresh
   invocation.** `walkto.py` carries its stall counter across the whole run,
   so a leg that thrashes early poisons the ones after it. Re-invoking with
   the remaining waypoints reset it both times it happened today.
3. **The backpack gump would not dismiss with `i`** at Ezrekal's post, over
   three attempts with the window focused. The gump-free plate from the
   earlier attempt is used instead.

## Disk changes

- `docs/playtest-2026-09-19-map10-rewalk.md` and its seven plates.
- No artifact rebuilt; `shared/build/` and `shared/u8-lv-patched/` untouched.
- `~/.config/scummvm/scummvm.ini` unchanged.
- The playtest session was stopped at the end.
