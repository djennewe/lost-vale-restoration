# In-engine RETEST, 2026-07-31 — hardened gates and swapped gateways

Retest of the fixes landed after this morning's playtest
(`docs/playtest-2026-07-31-gates-climb-corridors.md`). Run on kaga/Linux,
branch `agent/village-pipeline` with the working-tree map-builder changes
built in (`FIXED.DAT` sha256 `5b37ab8b…`, matching `ARTIFACTS.sha256`;
`shared/u8-lv-patched/STATIC/FIXED.DAT` verified identical). Text-console
ScummVM (`scummvm-lv-console/scummvm`) on the Xvfb harness
(`tools/playtest-linux/session.sh`). Debug teleports and `Cheat::toggle` used
freely — NOT a clean-room run. No source file, map builder or artifact was
modified; the only writes are this report and
`docs/playtest-2026-07-31-retest/` (83 screenshots).

Two sessions: A'+B' in the first, C'+D' in the second (restarted between, as
briefed). Exactly one `scummvm` pid at all times, verified with `pgrep`.

---

## Verdicts

| Test | Question | Verdict |
|---|---|---|
| **A'** | Does the hardened sanctum perimeter refuse the jump? | **PASS.** Every attempt refused; `templeOpen` read 0 at seven checkpoints, never 1. |
| **B'** | Does the hardened Map 11 pad-room / chamber wall refuse the wall-walk, and does the legit exit work? | **PASS on both.** No jump ever reached a wall top; the swapped pad-room gateway fired live. |
| **C'** | Is the Map 13 bounce gone, and does the deliberate return work? | **PASS on both.** |
| **D'** | Does the map 8↔9 doorway work both ways? | **PARTIAL.** The ping-pong is gone and 9→8 works, but 8→9 could not be exercised: **the double doors do not open** — they answer neither look nor use, with the quality-99 key in the pack. |

---

## TEST A' — Map 18 Inner Sanctum perimeter — **PASS**

Breach criterion (as this morning): Avatar at **y > 6143** (inside the
sanctum) at any z, or `templeOpen` (`0x412`) going 1. Neither ever happened.
Avatar full size (shape 1) throughout, no potion, no shrink.

### A'1. The two spots that climbed on the first burst this morning

| approach | pressed against wall at | after 5 × 2 s jump bursts | z |
|---|---|---|---|
| `teleport 18 2576 6108 0`, walk S | (2576, 6108, 0) | **(2576, 6108, 0)** — zero displacement | 0 |
| `teleport 18 2976 6108 0`, walk S | (2976, 6108, 0) | **(2976, 6108, 0)** — zero displacement | 0 |

`A1-2576-after-5-bursts.png`, `A2-2976-after-5-bursts.png`.
`UCMachine::getGlobal 0x412 1` = `[0412 01] = 0` before and after each set.
This morning both spots reached (x, 6156, **40**) on the *first* burst.

### A'2. Input controls (so the negatives mean something)

* Open ground in the Transition Hall, (3000,5710,0) facing N: one burst →
  **(3000, 5654, 40)** — the engine *does* still climb here, onto a 40-tall
  interior relief 490 units north of the boundary. `A3`, `A4`.
* A 4-frame screenshot burst during a held SPACE at the same spot moved the
  Avatar 132 x / 391 y and ended pressed at the boundary (3132,6101,0), and
  caught the crack bark *"The stone here is split from top to bottom — and
  there is open air beyond it. But the gap is no wider than my hand."*
  (`A15-jumpburst-1.png`). The jump key was live at the end of the session as
  well as the start.

### A'3. Adversarial attempts — all refused

| attempt | result |
|---|---|
| Chain from the z=40 hall ledge (4 bursts from (3000,5654,40)) | no movement at all; ledge is a dead end (`A16`) |
| Walk the ledge east, jump at the east side wall | fell to z=0 at (3704,5878), jumps refused (`A17`) |
| Hall **west** side wall x=2048: pressed at (2120,6006,0), 3 bursts | (2112,6019,**0**) then static (`A6`) |
| **SW shoulder corner**: pressed at (2112,6083,0), 4 bursts | zero displacement (`A7`) |
| Hall **east** side wall x=4095: pressed at (4060,6038,0), 3 bursts | zero displacement (`A8`) |
| **SE shoulder corner**: (4060,6102,0), 4 bursts | zero displacement (`A9`) |
| Void approach from the **west** at z=0: (700,7000,0) walk E | stops at **(992,7044,0)**; 3 bursts, no movement (`A10`, `A13`) |
| Void approach from the **south** at z=0: (3000,9000,0) walk N | stops at **(8768)**, i.e. (3000,8768,0); 3 bursts, no movement (`A11`, `A12`) |

`templeOpen` was re-read after every group: **0** each time (7 reads total).

### A'4. Two supporting observations, neither a breach

* **The wall tops are still standable if you cheat onto them.**
  `teleport 18 2976 6143 120` sticks at (2992,6159,120); `… 2976 6156 120`
  sticks; `… 2976 6143 80` sticks. So the defence is entirely "no reachable
  chain gets to 120", not "the top is unstandable". Arithmetic backs it:
  the tallest reachable ledge is 40, `climb72` from 40 tops out at 112 < 120,
  and the stacks are continuous so there is no 80-top ledge to break the
  climb into two steps. `teleport 18 2976 6100 40` (in front of the wall)
  falls straight back to z=0, as this morning.
* **Jumps in the open void (z≤0, no floor) produce no displacement at all** —
  see `A14`. That makes "no movement" from a void-side jump weaker evidence
  than the same result from real floor; the load-bearing refusals above are
  all from inside the hall on real floor, where the control proves the climb
  scan runs.

---

## TEST B' — Map 11 pad room and chamber south wall — **PASS**

### B'1. This morning's exact repro

`teleport 11 8480 22350 0` → walk SW. (The SW walk overshoots: it carried the
Avatar to (6208,22494) rather than (8328,22494), so the repro was then run
from fresh teleports at three separate x positions, all pressed against the
chamber south wall with a short S walk, all at y ≤ 22400 as report B3
requires.)

| x | pressed at | 4-5 × 2 s bursts | screenshot |
|---|---|---|---|
| 6208 (overshoot) | (6208, 22494, 0) | no movement, z stays 0 | `B1`, `B2` |
| **8328** (morning's spot) | (8328, 22486, 0) | no movement, z stays 0 | `B3-southwall-x8328.png` |
| 7600 | (7576, 22494, 0) | no movement, z stays 0 | `B3-southwall-x7600.png` |
| 6900 | (6900, 22486, 0) | no movement, z stays 0 | `B3-southwall-x6900.png` |

This morning the same input at (8328,22494) produced
(8328,22542,**48**) → wall-top walk → drop into the pad room → Map 10.

**Input control on the same map:** from (6900,22382) facing north (away from
the wall) one burst moved the Avatar to (7226,22492) — 326 units (`B4`).

### B'2. The boulder top is no longer a way in

`teleport 11 8640 22450 40` still sticks on the boulder top (unchanged), but
from there three S walks and three jump bursts produce **zero movement**
(`B5`): the new z=48 lintel over the doorway blocks the southward step that
the 40-tall boulder top would otherwise offer. Last-mile confirmation that
raising the boulders was never the fix and that the lintel does not open a
new one.

### B'3. The legit exit works — a swapped gateway firing live

```
teleport 11 8448 23040 0      (pad 204, the new arrival spot)   B6
walk SE toward (8960,23296)   ->  map 10 (12904, 2560, 0)       B7
```
That is trigger 205 at (8960,23296,1) → Map 10 pad at (12800,2560), i.e. the
swapped pair working in the intended direction. Four further walks on Map 10
(S,S,E,N → (13424,3328)) produced **no bounce back** (`B8`).

---

## TEST C' — Map 13 bounce — **PASS**

`teleport 13 4096 11776 0` (the NEW arrival pad, quality 207, frame 1).

```
E 1.5s -> (4408, 11776, 0)
E 1.5s -> (4928, 11776, 0)
E 1.5s -> (5304, 11840, 0)
N 2s   -> (5304, 10744, 0)
N 2s   -> (5304, 10144, 0)
N 2s   -> (5304,  9544, 0)
N 2s   -> (5304,  8944, 0)
N 2s   -> (5304,  8344, 0)
W 2s   -> (4800,  8344, 0)
```
**No teleport fired.** `C1`, `C2`, `C3`. This morning the same first three
eastward bursts ended on Map 10 at (7168,24064,14).

**The deliberate return:** back to the pad, then walk west toward the marked
slab at (3072,11776) — one intermediate sample at (3800,11776,0), then
**Map 10 at (7064,23296,0)**, i.e. the arrival pad 206 at (7168,23296)
(`C4`). Three walks on Map 10 afterwards (N,W,N → (6672,22600)) produced no
bounce (`C5`).

---

## TEST D' — Map 8 ↔ Map 9 — **PARTIAL: the ping-pong is gone, the doors are not**

> **CORRECTION, same night** (`playtest-2026-07-31-doors-investigation.md`):
> the doors ARE fine — this section's "answer neither look nor use" and
> "click trace finds no item" were both wrong. Look/use DO bark
> `Locked Door` (transient, top viewport edge), the trace DOES find the
> doors, and the cursor never reflects the item under it, so the blue
> walk arrow proved nothing. The correct idiom is double-click the KEY →
> target cursor → click the door; done that way the doors opened end to
> end and trigger 201 delivered to Map 9. Keep reading this section for
> the gateway verdicts (D'1/D'3 stand); treat every door claim as
> superseded.

### D'1. From the return pad into the bone field — **PASS**

`teleport 8 20415 3170 0` (the new return-pad spot, `D1`), then
S,S,E,S,E → (20343,3682) → (20343,4378) → (20907,4334) → (20907,5030) →
(21427,5030). **No teleport** (`D2`). Under the old geometry the trigger box
covered the doorway, so this was impossible.

Repeated later from a *genuine* Map 9 arrival (see D'3): S,S,W,S →
(20043,4526), no teleport (`D35`).

### D'2. North through the doors — **NOT DEMONSTRATED; the doors will not open**

Walking north from the pad stops dead at **y ≈ 3138-3140** for every x from
20300 to 20540 (eight probes, `D4`). `GameMapGump::toggleFootpads` (`D7`) and
the `h` highlight (`D30`) both show what is stopping him: **two closed door
leaves with ring handles**, item-highlighted, spanning the doorway.

These are the famous sealed doors, locked with lock id 99 by design, so being
stopped is correct. I obtained the key legitimately and it made no difference:

1. The key chest was opened by double-click from (20440,3400) (`D9`, `D10`).
2. The chest gump was dragged clear and the key dragged onto the Avatar's
   sprite per the HANDOFF recipe (`D11`-`D14`). Confirmed banked:
   `total weight: 20 → 30` (key = TYPEFLAG weight 1 → +10).
3. At the doors with the key in the pack (`D15`), **double-clicks on the door
   leaves do nothing** — no unlock, no open, no bark: five distinct points
   including both ring handles and the panel frames (`D16`, `D19-dclick-0..4`).
4. **Single-click "look" also produces no bark** (`D31`) and the cursor stays
   the blue walk arrow over the door pixels (`D17`) — i.e. the engine's
   click trace finds *no item* at those pixels, even though the highlight
   proves an item is drawn there. `MainActor::useKeyring` and
   `ItemSelectionProcess::startSelection` produced nothing either
   (`D18`, `D20`).

The same double-click technique opened the chest two minutes earlier, so this
is not a harness input failure. **On foot, Map 8 → Map 9 is currently
impassable.** Nothing in today's diff touches the doors, so this is very
likely pre-existing and not a regression from the gateway swap — but it means
the "walk north through the doors" half of D' is untested, and the claim in
`build_map_08.py` that a quality-99 key "unlocks them with zero code changes"
is **not confirmed in engine**.

The trigger itself is in the right place and on the right side: standing on
it at (20415,2786,1) is possible only from inside the alcove, which is only
reachable through the doors.

### D'3. Map 9 side — **PASS**

* `teleport 9 14336 12800 0` (arrival pad 201), then five southward bursts:
  (14336,13496,8) → (14336,14192,0) → (14400,14848,0) and static.
  **No bounce back to Map 8** over ~2000 units of quest-direction travel
  (`D32`, `D33`). This morning's geometry would have bounced within 128.
* Walking back **north** from there fired trigger 200 correctly on the fourth
  burst: (14400,13152,0) → **Map 8 (20415,3138,0)** — south of the doors, on
  the new return pad, with no immediate re-fire (`D34`).

So the 9→8 direction and the arrival-side ping-pong are both fixed and
demonstrated live; only the 8→9 leg is blocked, by the doors.

---

## Two findings that are not part of the four tests

### F1. `justTeleported` makes debug teleports useless for testing teleport eggs

`engines/ultima/ultima8/world/egg_hatcher_process.cpp:79-90`: the hatcher
skips teleport eggs while `MainActor::_justTeleported` is set, and
`MainActor::teleport()` (both overloads, `main_actor.cpp:383,428`) sets it.
The flag is cleared only on a frame where the Avatar is **out of range of
every teleporter egg**.

Observed consequence: teleporting to (20415,3090) and then walking north
deep into trigger 201's hatch box — and even teleporting to *exactly*
(20415,2786,1), standing on the egg for seconds — **never fires it** (`D25`,
`D26`). It is not an inert egg; it is the flag. Ranges are
`(npcNum >> 4) * 32` in x and `(npcNum & 0xF) * 32` in y (`egg.h:38-43`,
`range_mul = 32` for U8), so e.g. npcNum 201 = 0xC9 → ±384 x / ±288 y, and
the test also includes the Avatar's footpad extent.

**Rule for future sessions: any teleport-egg test must be entered on foot
from outside the egg's range.** A `dbg teleport` into or near the box
produces a false negative. All four of this session's positive gateway
results (B'3, C', D'3 ×2) were walked into from outside the box; the one
negative I could not walk into is D'2, and it is reported as untested rather
than as a failure.

### F2. The Map 8 key chest sits inside the Lost-Vale gateway's hatch box

Trigger 212 (Map 8 → Map 10) is at (20900,3300) with npcNum 0xD4 → box
**x 20484..21316, y 3172..3428**. The key chest is at **(20500,3370)** —
16 units inside that box in x, dead centre in y.

Demonstrated: `teleport 8 20500 3560 0` then one northward walk →
**Map 10 (13824,2456)** (`D8`). Approaching the key chest from the south or
east teleports you out of the map before you can open it. It is still
reachable — I opened it from **(20440,3400)**, i.e. from due west, x < 20484
(`D9`) — but the working approach is a ~110-unit-wide corridor and nothing
marks it. Worth moving the chest (or the trigger) a few hundred units apart.

Note the same pair *before* this morning's swap had the active trigger at
(20260,3260), whose box (x 19844..20676, y 3132..3388) contained both the
chest **and** the return pad at (20415,3170) — so the swap strictly improved
this. F2 is a leftover, not a regression.

---

## Harness anomalies

* **`Cheat::toggle` parity, again.** Session 1's first call replied
  `Cheats = true` (it started disabled); session 2's first call returned an
  empty reply, the second `Cheats = false`, the third `Cheats = true`. Always
  call it and *read the reply*, and re-read after any lost response.
* **`ObjectManager::objectInfo 1` occasionally returns nothing** (6 times in
  ~200 calls) — the position parse yields `None` while the very next call
  succeeds with a sane position. Transient log-read race in the `dbg`
  protocol, not a stuck engine. Never treat a single `None` as a result.
* **A fresh `start` still lands mid-conversation with Devon.** Clicking
  "Goodbye" at (915,338), waiting ~8 s, then four more clicks clears the
  farewell text. `session.sh start`'s Escapes do not.
* **Still no `jump` verb in `session.sh`.** Every jump here was
  `xdotool keydown space` / sleep / `keyup space` from a scratchpad helper
  (`lv.py`, not committed, per the write restrictions). Second session in a
  row recommending it be added next to `walk`.
* **`session.sh walk`'s corrected direction basis is right** and was used
  throughout, but note the SW diagonal overshoots badly on open ground — the
  Map 11 repro ran 2100 units past its target on three bursts. Prefer short
  bursts plus a read-back for anything positional.
* **Cosmetic: the new triple-stacked walls hide the Avatar.** Standing
  pressed against Map 18's crack line (`A1`) or Map 11's chamber south wall
  (`B3-*`) the Avatar is not visible at all — the wall row has the larger
  x+y and paints over him, the same class of problem `build_map_08.py`
  documents for the corridor strip in front of the double doors. Not a
  blocker, but a player pressing on a gate sees an empty screen.
* `QuickAvatarMoverProcess::toggleClipping` reads *inverted* from what the
  name suggests: `_clipping = false` is the default and means the quick
  mover passes through geometry. `Cheat::hackMover` returns no reply either
  way. Neither was needed for a result and both are recorded only so the next
  session does not re-derive them.

## Disk changes

* `docs/playtest-2026-07-31-retest/` — 83 screenshots.
* This report.
* Nothing else. No source, map builder, artifact or config was touched, and
  no game was saved.
