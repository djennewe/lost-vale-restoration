# Playtest 2026-08-16 (session 2) — quest steps 1-2 PASS; the cave ascent is an engine crash

Continuation of the same day's pool-crossing session
(`docs/playtest-2026-08-16-pool-crossing.md`). Started on the southern
landmass at (29801,22801,8); ended with **quest steps 1 and 2 both
verified in-engine, organically** — the LORDBRIT backstop scene fired
from a real walk-in and Mythran's full MYTHRDLG tree delivered every
Vale branch — plus one engine-crash discovery that changes the
project's rehearsal plans.

## Verdicts

| Test | Verdict |
|---|---|
| Quest step 1 — LORDBRIT backstop egg (map 8 approach) | **PASS** — organic walk-in at (2200,2230), full apparition scene, message text correct, `lbDone` reads 1 (B2-B4) |
| LBSCENE backstop cleanup (the TODO confirmation pass) | **PARTIAL** — apparition destroyed ✓, but **camera tracking is never restored** (defect, see F2) |
| Quest step 2 — MYTHRDLG full tree | **PASS** — intro routes on lbDone ("Ah. So the message has arrived at last…"), Zealans → survived → Vale reveal → LB acceptance → Galjeron → doors (Bonecrusher's cave) → key; `mythranToldZealans/Galjeron/Doors/Key` all read 1 (C2-C6) |
| Cave traversal, trench system → south exit | **PASS with bypass** — trench slot + roofed underpass walked; the z8→z56 ascent is engine-crash-blocked (F1) and was teleport-bypassed |
| Electric gateway (LITZAPNS) organic passage | **NOT DEMONSTRATED** — the Avatar got stun-pinned in the arc (A1); bypassed. Usecode decoded: zaps overlapping NPCs for 5-9 via class 0x57C on a long random idle cycle |
| Retail dev-cheat menu interaction | Finding F4 — with cheats enabled, talking to Mythran opens the retail developer menu instead of dialogue |

## F1 — ENGINE CRASH: the hang-grab ascent segfaults ScummVM (blocker)

The canonical route out of the cave requires ascending 48-unit cliffs.
The engine's mechanism (avatar_gravity_process.cpp): jump at the wall
with a direction held → mid-fall `tryAnim(climb40)` succeeds → hang;
then SPACE/left-click pulls up (`handleHangingMode`). **Executing the
leap (hold Up + SPACE at a 48-wall, flush or from distance) reliably
crashes the engine**: "Seem to be stuck in process loop - killing
current process!" spam, then SIGSEGV. Reproduced twice at
(30425,23145,8) facing the terrace's north face. No upstream fix exists
(checked scummvm/scummvm history for avatar_gravity_process.cpp; the
only related commit is 2023's "Allow keyboard jump to climb when
hanging").

Consequences: (a) the 2026-08-12 "notch softlock" was this same hang
state — the notch held a hang nobody knew the pull-up input for, and
completing it may ALSO crash; (b) **the continuous no-debugger
rehearsal cannot pass this cave until the engine is fixed** — the
z8→z56 ascent was bypassed with `MainActor::teleport` (cheats toggled
on for the bypass, verifiably off again before dialogue testing);
(c) an engine patch in our ScummVM fork is the likely fix path — we
already ship detection patches.

Also climb-mechanic facts established: plain climbs (branch-2 SPACE
climb scan) require a LAND-flagged top and max out at climb40 —
48-unit glob cliffs need the (crashing) hang path; SOLID-only items
(pillars 65/66, walls 497/713/714) refuse climbs entirely; careful-step
(LCTRL) does work on stone tops (+32/step); the avatar's stand frame
encodes facing (0=N 2=E 4=S 6=W) and is the reliable facing oracle.

## F2 — LBSCENE backstop never restores camera tracking (content defect)

After the backstop scene, the camera stays anchored at the scene point
forever: the Avatar walks off-screen, `CameraProcess::moveToAvatar`
snaps once but tracking does not resume, and the anchored camera even
**persists through save/load** (CameraProcess is serialized). The
map-39 primary flow was verified camera-correct on 2026-07-04, so the
defect is specific to the backstop path in LBSCENE.UNK — it should
restore the item-tracking camera (SetCameraProcess(1)-equivalent) when
the scene ends. Post-rehearsal fix; workaround in harness: snap
moveToAvatar before every interaction batch.

## F3 — the map 8 south cave, decoded

- The z8 areas around the pool's south are a TRENCH system under the
  z56 main floor (cells with both 8 and 56 = roofed underpass). The
  walkable thread: slot at x 30527-30559 (y 23047-23191) → west along
  y≈23200 → south under the roof at x≈30405 → emerges y 23583.
- Shapes 713/714 are bridge spans over the trenches; 497s are their
  side walls. None are standable (SOLID, no LAND).
- The z56 main floor runs south ~4,000 units to the cave mouth at
  y≈29100 where it drops to the z0 outdoor plateau.
- The electric gateway: fence line at y 24383 (shapes 249/287 posts,
  LITZAPNS zapper item 4748 at (30879,24383,56)); the only passage at
  floor level is x≈30815 beside the zapper; the walkthrough's "even
  higher ground" evade is the z112 highland west — out of climb range,
  i.e. also hang-gated (F1).
- The shape-2 "arrows" are a 512-unit decorative grid across the whole
  map (123 in the south half alone), NOT route guides — z of each grid
  item incidentally maps floor height. Both prior sessions' readings
  ("teleport pads", "route guides") were wrong.
- Deaths this leg: 3 (gateway experiments/driving), all recovered.

## F4 — cheats change Mythran's conversation

With cheats enabled, double-clicking Mythran opens the **retail
developer menu** (Demo/Spell-Book/…/Jump ahead) instead of dialogue
(C1). `Cheat::toggle` parity must be verified by reading its reply
("Cheats = false") — the traps.md warning stands. Dialogue testing
requires cheats off.

## Step 1-2 evidence

- Backstop: walked (2500,2250)→(2204,2162) past the egg; the apparition
  scene played in Mythran's parlor — "…Journey with great haste to
  Mythran." — sparkles/ghost cleanup ran; `getGlobal 0x6A6 1` = 1.
- Mythran located as objId 33 (shape 190), wandering his schedule
  across the house (z0 shop, z48 upper rooms). The frame-facing oracle
  plus probe-verified double-clicks landed the talk after several
  chase rounds.
- MYTHRDLG: every Vale-thread branch exercised in order; flags
  0x717/0x718/0x719/0x71A all = 1 afterward. Dialogue text verbatim
  matches the Phase-3 script (Zealans/Ancient Ones, the Vale reveal,
  Galjeron the explorer, Bonecrusher's cave doors, the key).
- Minor perturbation on record: a probe double-click toggled a shop
  item (blue cube ↔ red sphere) on Mythran's counter.

## Disk changes

- Checkpoints added: cp3i-gate-approach, cp3j-past-gate,
  cp4-mythran-approach, cp4b-lb-done, **cp4c-mythran-done** (slot 1;
  Avatar at (2169,1183,48) beside Mythran, steps 1-2 complete).
- Saves: slot 1 = cp4c. Cheats: OFF (verified by reply).
- Session live on :77, camera still scene-anchored pending F2 fix —
  snap moveToAvatar as needed.

## Next

From cp4c: walk to the doors approach (~(20430,3250)) — the paved
chest + quality-99 key (our placement), unlock the double doors
(double-click key → click leaf), enter the black pocket, teleport 200
→ **Map 9, Galjeron's Chamber** (unvisited, "not visually tested") —
quest steps 3-4. The walk from Mythran's island to the doors (~18k
units east) is retail terrain; decide organically vs. positioning
teleport based on the F1 precedent.
