# HANDOFF.md

> Working memory for Claude Code sessions. Updated at end of each session.
> Last updated: 2026-07-31, ninth session CLOSED (on kaga/Linux)

## Current State

**Where the work is.** Branch `agent/village-pipeline`; the tip is
`e64336b` (2026-07-31, six commits: `c453b4d` route reachability,
`f78587a` self-audit, `7e61bdb` gate hardening + gateway swaps,
`81d884c` retest absorption, `e64336b` doors resolution). `origin/HEAD`
still points at `agent/npc-dialogue`, which is why worktree subagents get
created on a stale Phase-3 commit and must
`git reset --hard agent/village-pipeline` first.

**START HERE — THE NEXT ACTION IS DOUGLAS'S ~2-MINUTE WALK (he said he
will do it "tomorrow", i.e. 2026-08-01).** Load cp2
(`cp ~/lv-checkpoints/cp2-palace.sav ~/.local/share/scummvm/saves/ultima8.001`,
then `Ultima8Engine::loadGame 1` or the diary), walk north through the
palace to the teleporter at **(13054,2322)** → map 7 (15071,26239) → walk
to **(9498,19702)** → map 8 (31583,19135), **stop on arrival** (never
approach Mythran or (2200,2230), the LORDBRIT backstop egg), F5-save as
the plateau base. Verify **`lbDone` (`0x6A6`) reads 0** on load; record
the four artifact hashes. The exit test (steps 1-18 continuous, no
debugger) is then run from that save. **Nothing agent-shaped stands in
front of it any more** — the ninth session cleared the queue.

**NINTH SESSION (2026-07-31): the quest route is now walk-verified end
to end, both quest gates hold against the jump button in-engine, all 11
teleport gateways are bounce-audited, and the front doors are proven
working.** Full detail in the blocks below and in the three session
docs: `docs/playtest-2026-07-31-gates-climb-corridors.md` (morning, 35
screenshots), `docs/playtest-2026-07-31-retest-hardened-gates.md`
(evening, 83), `docs/playtest-2026-07-31-doors-investigation.md` (night,
26). The session started on Next Step 1 — re-check the two reachability
suspicions with exact box maths — and the instrument it needed turned
into the session's main deliverable.

- **`agents/map-populator/src/exact_reach.py`** floods with the engine's
  own arithmetic instead of the 32-unit cell raster: it reimplements
  `CurrentMap::getPositionInfo` (blocked = a SOLID box overlapping the
  mover; supported = some XY-overlapping top *exactly* at the standing z;
  land = a LAND/ROOF top within 8 units under the mover's bottom CENTRE;
  z<=0 always supported) and `Box::overlaps`/`overlapsXY`/`isBelow`
  verbatim, over an 8-unit lattice aligned to the `x % 32 == 31` that every
  map item sits on. Vertical movement is capped at 8 units per step because
  that is `scanForValidPosition`'s scan window (`scansize`), which
  `AnimationTracker::step` falls back to. numpy, run-labelled row
  propagation; a whole map is 1-8 s.
  **It reproduces the DD-005 mechanic from a cold flood** — full-size
  Avatar stops at the crack, shrunken one walks through — which is the
  best evidence available that the model is right.
- **THE TWO SUSPICIONS SPLIT.** Map 10's Sacred Circle and Ezrekal's
  dwelling are **fine** (98.1% of the map reached from the arrival pad);
  that was `flood(body_cells=2)` over-restricting on grid-misaligned
  corridors, exactly as 07-30 feared. Map 17's shield halves were
  **really unreachable**.
- **MAP 17: both shield halves were behind a strip of nothing.** Floor
  tiles stop at y=4607 and resume at y=5247; nothing spans y 4735..5119
  anywhere across the map. God's Hall A, God's Hall B, the Scroll Chamber
  and the Memorial Hall form one connected block with **no walking route
  over real floor from the only entrance**. It hid this long for a plain
  reason: map 17 had NO terrain at all until 2026-07-25
  (`GLOB_STONE_FLOOR` was an empty glob), so no walkability pass ever had a
  floor to flood. Fixed by `build_hall_corridors()` — the two branch
  corridors `map-13-17-cloud-areas.md` has always drawn.
  **Severity corrected by the same-day audit (below): probably NOT
  hard-blocking in-engine.** `getPositionInfo` ends with `if (target._z
  <= 0) info.supported = true;` (current_map.cpp:773), so the engine will
  walk the Avatar across a floorless void at z=0 — the strip likely read
  as a stretch of blackness you could walk anyway. A data hole and a
  blackness-rule violation for certain; a wall only if something subtler
  intervenes. Not verified in-engine either way.
- **MAP 13: the climb to Cloud City was six disconnected ribbons.** Each
  elevation zone laid its own path with its own hardcoded z, and every seam
  was a **9-unit riser** (23->32, 47->56, 107->118). Walking allows **8**
  (`scanForValidPosition`). Plus a 512-unit hole between the switchbacks
  and the ledge, and a zigzag that stepped diagonally by (256,-128)
  between tiles only 128 across, so every turn had a missing tile.
  Rebuilt as ONE polyline (`build_map_13.climb_tiles()`, 89 tiles, every
  riser 1 or 2); the zone builders no longer place path tiles at all, so a
  seam cannot be reintroduced by editing one zone. Also: a solid
  `SHAPE_BONES_B` sat dead centre of the one-tile-wide ledge, and the
  summit's cliff-edge picket had a segment exactly across the path's last
  tile. **Audit scope note: the risers alone were a walking-seal, not an
  absolute one** — the jump button auto-climbs up to 72 units (see the
  audit bullet), so a determined jumper might have scaled them. The
  512-unit hole is beyond any jump, so the summit stayed out of reach
  pre-fix, but the mechanism was the hole more than the risers.
- **`test_route_reach.py` (23 asserts, ~16 s)** pins it, arrival pad to
  goal, for maps 9/10/11/13/17/18 — and pins the two *designed* barriers as
  barriers: map 11's sealing boulders (removing them opens the exit, so the
  puzzle is the only thing in the way) and map 18's crack.
- **What this does NOT see.** FIXED.DAT only. NPCs, doors and everything
  else in NONFIXED.DAT/NPCDATA are invisible — the palace-door lesson (F2)
  still stands. And it checks positions, not the swept volume between them.
- **SAME-DAY SELF-AUDIT (prompted, and it found things): the model is
  STRICTER than the engine in two documented ways, and the second opened a
  new hole.** Both deviations bias the same direction — REACHED verdicts
  are solid, UNREACHED means "no walking route over real geometry", not
  "the engine refuses". (1) **z<=0 is supported unconditionally in the
  engine** (current_map.cpp:773) — it walks the Avatar over floorless void
  at ground zero; the model demands a real surface there on purpose.
  (2) **The jump button is not modeled**: `u8_avatar_mover_process.cpp`
  auto-tries `Animation::climb72` down to `climb16` on jump, so any
  barrier <= 72 tall with a bare top may be climbable. Measured against
  the built FIXED.DAT: **the map 18 sanctum wall around the Tiny Tar
  crack is 40 tall (tops z=40) with only two zero-height roof plates
  above it, and map 11's sealing boulders are 40 tall standing in a hole
  of the pad-room's sparse roof** (128-wide tiles at a 512 stride). Both
  designed barriers are within climb range on paper — see the new Open
  Question.
- **THE AFTERNOON: the playtest confirmed both gate bypasses live, and
  the fixes landed the same day.** Full record in
  `docs/playtest-2026-07-31-gates-climb-corridors.md` (35 screenshots).
  The full-size Avatar CLIMBED the sanctum wall on the first jump —
  `templeOpen` went 0→1 with no potion, no shrink — and left the
  Elemental Dungeon over the chamber's south wall with both sealing
  boulders intact. The new climb (test C) and corridors + shield pickup
  (test D) both PASSED. Fixes, all static-checked, in-engine retest run
  the same evening:
  - **Map 18**: the sanctum boundary is now a 120-tall triple stack
    (`build_sanctum_gate_hardening()`) on every line INCLUDING the
    Transition Hall side walls (they were elevated walkways to the
    boundary corner), and the sanctum's **south glob doorways are
    closed** — they had been open to the walkable void the whole time
    (the morning climber exited that way at (2815,9189)).
  - **Map 11**: pad-room perimeter + chamber south wall are 144-tall
    triple stacks with a lintel over the boulder doorway (the boulders
    and the post-puzzle walker pass under at 0..48).
  - **THE TELEPORT-INVERSION BOUNCE CLASS, found systemic.** The morning
    run bounced off Map 13's arrival (report C1). A static audit of every
    LV gateway found **8 of 11 had the ACTIVE trigger on the quest
    walking line** — the 07-25 relocation comments were written under the
    pre-771d5c7 inverted helper names, so each carefully-reasoned
    placement landed swapped (map 17's, placed live in July, was correct;
    so were the 07-04 in-engine ones). Fixed by swapping POSITIONS only —
    ids and roles untouched, so every cross-map dial still pairs. The
    map 8↔9 doorway was a mutual ping-pong (return from map 9 was
    impossible); map 10's vale entry bounced both arrival pads to map 8;
    the cloud/temple approach triggers sat BEFORE their key-locked gates
    (the keys gated nothing) and now sit past them — NECESSARY but not
    yet sufficient: both gates are still single 128-wide items in open
    zones that can be walked around (Next Step 1's funnel walls are what
    makes the keys actually gate).
  - **`test_route_reach.py` grew from 23 to 58 asserts**: the full
    gateway table pinned, a per-pad quest-egress bounce audit (trigger
    hatch boxes are invisible to every flood — only this sees them), and
    anti-climb wall-coverage checks (every gate line must be a continuous
    solid stack to 120/144 — no ledge for a chained climb), and a
    quest-items-clear-of-trigger-boxes guard (the Map 8 chest lesson).
- **THE EVENING RETEST (docs/playtest-2026-07-31-retest-hardened-gates.md,
  83 screenshots): the hardening HOLDS.** A': both morning breach spots
  refuse 5x2s jump bursts, twelve adversarial chain attempts refused,
  `templeOpen` 0 at all seven checkpoints — while a control jump on open
  hall ground still climbs to z=40, proving the input was live. B': the
  chamber wall-walk is dead at three x positions, and the legit pad-room
  exit fired live (pad → slab → Map 10 (12904,2560), no bounce after).
  C': the Map 13 bounce is gone (the morning's exact line reached
  (5304,8344) with zero teleports) and the deliberate return works. D':
  the 8↔9 ping-pong is fixed in both tested directions — but the 8→9 leg
  itself is blocked on a separate find, see Open Questions: **the Map 8
  double doors would not open** even with the legitimately-fetched key.
- **Two engine rules the retest established, both HANDOFF-grade.**
  (1) **`justTeleported` invalidates teleport-based tests of teleport
  eggs**: `egg_hatcher_process.cpp` skips teleport eggs while the flag is
  set, `MainActor::teleport` sets it, and it clears only on a frame where
  the Avatar is out of range of EVERY teleporter — so standing directly
  on a trigger after a debug teleport never fires it. Walk into trigger
  boxes from outside; never judge one by teleporting onto it.
  (2) The Map 8 key chest sat 16 units inside trigger 212's hatch box —
  approaching it from the south teleported you to Map 10. Chest moved 64
  west (build_map_08), and `test_route_reach` now asserts no quest item
  (chest/key/shield shapes) sits in or beside any trigger box.
- **Estate 24/24, walkability 136 PASS, artifacts 4/4 with FIXED.DAT
  recorded** (EUSECODE untouched all day — detection never moved).
  `install_lv.sh` run; harness copy refreshed byte-identical.

**Sixth/seventh session background (2026-07-29/30), condensed — the walk
recipe itself is at the top of this file.** The first clean-room attempt
(`docs/playtest-2026-07-28-cleanroom-run1.md`, 63 screenshots) ran fresh
game → Devon → the Toran execution cutscene → through the Tenebrae gate,
map 3 → map 40, zero cheats — the base game is fully intact under the
merged artifacts; it stopped on palace NAVIGATION, no LV step verified or
falsified. The seventh session replayed the prologue hands-off and banked
the checkpoints in `~/lv-checkpoints/`: **cp1-map40.sav** (map 40 south
end) and **cp2-palace.sav** (palace west wing, two doors opened) — cp2 is
the one the walk starts from.

**Eighth session (2026-07-30), condensed** (`46c381f`, `4698a63`): the
picket-fence solidification only works with DESIGNED doorways — on these
maps the wall porosity IS the circulation, so Map 09 landed (solid + one
doorway + `run_map9` guard) and Maps 10/17 were reverted pending a visual
pass (still open, Next Step 1). Also landed:
`SHAPE_WOOD_BUILDING_WALL_EW` = 149, a second 489/492 orientation-bug
instance on Map 10's huts. Standing process rule from that session:
**re-read TODO/HANDOFF and `git log` before acting on anything you
"remember" being outstanding** — it opened on three-day-stale notes and
nearly redid `plantScene` (`375954d`).

What stopped the agent in the palace, all recorded in the run doc: U8
doors live in **NONFIXED.DAT** — invisible to WalkGrid both ways (closed
doors on "free" cells; locked q=512 doors on routed cells; q=0 doors open
on double-click but only at point-blank range), and a patrolling guard
body-blocks the west wing (NPCs are in NPCDATA/ITEMCACH, invisible to every
static tool). Also: the Avatar can DROWN — one attempt died to the Lurker
when a blind stuck-recovery walk backed into dock water, and a dead
Avatar's game-over diary cannot be closed (MenuGump refuses Close on
ACT_DEAD).

**The plateau is NOT story-gated** — this was the session's key correction.
`TeleportEgg::hatch()` teleports unconditionally; the eggs carry no usecode
and no flag check, so map 40 → 7 → 8 is pure navigation. Route:

```
map 40 teleporter (13054, 2322, 48)  -> map 7 arrive (15071, 26239, 8)
map  7 teleporter ( 9498, 19702,  8) -> map 8 arrive (31583, 19135, 0)
Mythran ~map 8 (1503, 1791); LORDBRIT backstop egg map 8 (2200, 2230, 8)
```

**Two inversions were found and fixed on the way (commit 771d5c7), and the
map data was never wrong.** `u8_map.py`'s teleport helpers were named
backwards relative to `TeleportEgg::isTeleporter()` (`_frame != 1`), and
`TELEPORT_TABLE` recorded every LV id's direction backwards on top of that.
`verify_teleport_pairs()` carried the matching inversion in its expectation,
so the two cancelled and the gate passed for months. Renamed to
`teleporter()` / `teleport_target()` and `is_teleporter` /
`is_teleport_target`; table and gate corrected together. **FIXED.DAT rebuilt
byte-identical (`8e5d27ec…`), all four artifacts match ARTIFACTS.sha256,
estate 23/23.** If you touch teleports, read `TODO.md`'s two entries first —
the old names are the reason the run lost a leg.

**Still open from the attempt.** (F2) The Toran execution egg lives in
`SAVEGAME/U8SAVE.000 → NONFIXED.DAT` (map 3, (11732, 5844, 48), quality 4 →
class 1155), *not* FIXED.DAT — so every scan run against FIXED.DAT alone,
`map_walkability.run_event_eggs()` included, is blind to base-game dynamic
eggs and cannot detect an LV item colliding with one. (F3)
`WalkGrid.flood()` is a connectivity check, **not** a pathfinder: it handed
back a 268-cell map-40 corridor the engine flatly refuses, the same
centre-of-cell limitation already recorded for the Tiny Tar crack.

**Harness lessons, all cost real time.** `dbg` leaves the console
**attached, and attached means PAUSED** — clicks and drags sent then are
silently discarded (one "the door will not open" dead end was exactly
this). ScummVM appends a command's reply to the **same line** as the
`debug>` prompt, so a log reader must start one line earlier than "lines
present before I sent" (`tools/playtest-linux/nav.py` has the fix). And the
command pipeline still degrades after a long session — it went unresponsive
again at the end of this one. Restart between phases.

**STEPS 17 AND 18 HAVE RUN IN THE ENGINE — THE QUESTLINE'S FINAL SCENES
ARE PLAYED (2026-07-28, fifth session).** After the WorldPoint compiler
fix (commit a5acf5e) the whole tail of the game executed live:

```
Sacred Circle ceremony (full, again, on the fixed build)
   -> the reforged shield APPEARS on the ground at (Avatar.x, Avatar.y+20),
      exactly where the sim predicted -- picked up, carried (weight +40)
altar egg (Map 18, quality 296 -> AOSCENE 1447)
   -> all four gates pass (godsFree=0, templeOpen, shieldFixed, artifact
      in container Avatar), the ceremony plays: symbols glow, RUMBLE1,
      FadeToWhite, "ancient presences awakening", godsFree 0 -> 1
endgame egg (Map 10, quality 299 -> ENDGAME 1450)
   -> "The Zealans gather around me... hope."
      "An elder steps forward... They are thanking me.
       The Vale is restored."
```

Every quest-critical scene in the restoration has now executed in
ScummVM. Notes from the run: AOSCENE takes ~60s of real time (waits +
fades + bark durations) and the DEBUGGER PAUSES IT — poll godsFree
sparingly or the scene appears hung at the white fade. templeOpen and
shieldFixed were set by debugger in the final leg (both writers had
already been proven live: the crack walk and the ceremony); the artifact
gate was satisfied honestly, and note AOSCENE's foreach accepts any
shape-539 item — a Map 17 HALF works, not just the reforged whole. A
same-map teleport away from the Sacred Circle leaves the ceremony's
CameraProcess pinned (camera stays at the circle; a cross-map teleport
resets it) — that plus a second ScummVM instance ate one attempt; check
`pgrep -c` and prefer cross-map hops after scenes.

**The remaining honest gap is a single no-debugger playthrough** (the
clean-room run): every scene has now run, but never all in one sitting
from a fresh Avatar with no setGlobal. That is the last verification tier
left.

**The original finding, for the record: STEP 17 WAS BLOCKED (found
2026-07-28, fix applied, NOT yet confirmed in-engine).** The altar
ceremony (`lv-new/AOSCENE.UNK`) needs `TypeAOArtifact` in the pack, and
the only one in the game is the shield the Sacred Circle ceremony
reforges. That shield is popped by `SHADES.UNK` at

    wholeShield.pop(Frizbee1.getX() - 60, ..., Frizbee1.getZ());

**twenty lines after `Frizbee1.destroy()`** — a destroyed item's
getX/getY/getZ return 0, so it materialises around (-60,-30,0) and is
gone. The same defect is in the recovered 1994 source (SHADES.UNK:368
against the destroy at :350), so it is theirs, not the merge's. It makes
steps 17-18 unreachable: no artifact, no ceremony, no endgame.

`lv-patched/SHADES.UNK` now pops at `firePoint1.x - 60, firePoint1.y - 30,
firePoint1.z` — the position the scene itself captures at the hand-over
beat (`Frizbee1.getPoint(firePoint1)`), while the half is alive on the
ground, reproducing the 1994 offsets exactly. **Do not use `newPoint`
instead**: that comes from `invisShield`, which is created as
`create(TypeAOFrizbee, 4)` — frame 4 of a shape with no frame 4 — and it
was tried first and is equally dead.

**WHAT IS NOT PROVEN, AND EXACTLY HOW TO SETTLE IT.** Three full ceremony
runs later the shield has still never been SEEN. It is not for want of the
scene working — the reforge fires, `shieldFixed` goes true, the shades
speak — the artifact simply has not been observed on the ground.

The fix is right by construction: `Frizbee1.getPoint(firePoint1)` runs
while the half is lying on the ground (`I_getPoint` reads
`getLocationAbsolute`), so firePoint1 is a real world position, and the
pop is `firePoint1 + (-60, -30, 0)`. Working the offsets back through the
hand-over (`Frizbee1.pop(Avatar.getX() + 60, Avatar.getY() + 50, ...)`)
puts the shield at **(Avatar.x, Avatar.y + 20)** — i.e. about 20 units
south of where the Avatar stands during the ceremony, which is very
likely UNDERNEATH HIS OWN SPRITE. That is the most probable reason three
sweeps found nothing.

So, precisely: run the ceremony from a spot whose coordinates you noted,
and BEFORE sweeping, move the Avatar clear — a `MainActor::teleport` 200
units away is enough and avoids the stasis problem that made walking fail
after the scene. Then look at (start.x, start.y + 20). If it is not
there, the create itself is failing and the fix is aimed at the wrong
line. **Do not treat step 17 as unblocked until the artifact has been
picked up and carried.**

Harness caveat learned across those runs: the command pipeline degrades
after long scenes with many menu clicks — `dbg` starts returning stale
replies or none. Restart the session between phases rather than trusting
a long-lived one.

**QUEST STEPS 14-15 ARE PLAYED IN FULL, AND THE POISON ARC IS CLOSED
(2026-07-28, fifth session).** The Sacred Circle ceremony ran start to
finish in the engine, driven by hand, and it works:

```
both halves in the pack (shape 539, weight 20 -> 60 -> 100)
walk into the circle    -> EggShades hatches, past the no-shield ret
                           Atli, Thordis and EZREKAL teleport in
"Hoskuld, the shield stole! Upon your head, the blood of Gunnar is!"
  pick "Let's be reasonable!"   -> the elders concede
  pick "Yes, Priestess."        -> "Here are both pieces, Priestess."
the reforge    -> "Whole, it is! Forgiven us, the gods have!"
the shades     -> "In life, Gunnar, was I named..."
                  "Sealed, I fear they are, within our temple.
                   Free them, you must!"   (the hook for steps 17-18)
  pick "Please, High Priestess!" -> "Then healed, you shall be!"

avatarPoisoned  1 -> 0     THE CURE, executed for the first time
shieldFixed     0 -> 1
godsFree             0     correct — that is the temple, not this scene
inShadeScene    1 -> 0     the scene CLEANS UP after itself
all three elders back at their home coordinates
```

That closes the loop decision A worried about: poisoned at the Passage
Test, cured at the ceremony, both halves now witnessed running. It also
proves the send-home teleports and the `inShadeScene` latch — this scene
does NOT leak its flag the way plantScene did.

**SIGRID'S SLOT IS CLEAN (same session).** Walking into the Sacred Circle dispatches EggShades
(class 1445, hatch at offset 128, then on to offset 417) and Ezrekal's
no-shield bark renders: *"Bring the sacred shield, you must! Without it,
return not!"* That is `lv-patched/SHADES.UNK` running in the engine for
the first time — the scene that holds the corpus's only `avatarPoisoned`
cure. **The full ceremony is still unplayed**: it needs both shield halves
in the pack (Map 17, shape 539 frames 0/1 at (6208,1568) and
(7232,1568)), and picking items up needs a left-button drag onto the
Avatar that I did not get working before the session ran out.
**Sigrid**: slot 102 is now a clean Actor (shape 707, EXT_PERMANENT_NPC)
and her class 1126 demonstrably dispatches — schedule (355),
enterFastArea (397) and leaveFastArea (433) all traced. Her `use()` (459)
stayed unobserved only because she wanders faster than a
screenshot-compute-click cycle. The old "never dispatches" symptom is
consistent with the egg collision: while slot 102 held an egg-shaped
actor, `Item::callUsecodeEvent` dispatched it by egg family
(quality + 0x47F) instead of npcNum + 1024, so her clicks went to an
unrelated class.

**DD-005 IS PLAYED, END TO END, IN THE ENGINE (2026-07-28, fifth
session).** Not simulated — walked. Potion → shrink → through the crack →
`templeOpen`, with the control in the same session:

```
full-size Avatar, right-mouse held at the wall from three angles:
    slides along it, stops at y=6108, never crosses      templeOpen = 0
drink frame-8 potion at Hrodny's:  "I'm feeling funny."
    shape 1 -> shape 708 frame 69
shrunken Avatar, same walk, same spot:
    (2864,6080) -> (2864,6504)  THROUGH the aperture     templeOpen = 1
    EggCrackHint barked at the wall  ("no wider than my hand")
    EggTempleEntry barked on the far side ("I am through...")
re-grow inside the sanctum, 33 s later:
    shape 708 -> shape 1, HP 30/30, still at (2864,6504) — SURVIVED
```

That closes the last open link in the chain and exercises three things
that had never run: the shrink itself, the repaired `makeAvatarBig`
re-grow (lv-patched/FREE.UNK), and the crack as a real gate rather than a
modelled one.

**THE TINY TAR CRACK WAS IMPASSABLE — AT BOTH SIZES. FIXED 2026-07-28
(fifth session).** The whole DD-005 entry route was sealed, and the proof
that shipped with it was the wrong instrument. Item boxes in U8 are
half-open (`Box::contains` is `px > _x - _xd && px <= _x`), so the 96-wide
filler at x=2848 occupied 2753..**2848 inclusive** and the glob piece east
of it 2880..2943 — a clear span of **31 units for a 32-unit body**, and
`Box::overlaps` is strict, so the shrunken Avatar had **zero** valid
positions. It shipped because `map_walkability` rasterises to 32-unit
cells and marks a cell blocked only when a blocker covers the cell
CENTRE: the filler's last unit vanished, cell 89 read as fully free, and
the footprint flood walked a 1-cell body through a gap the engine
refuses. **A one-body-width aperture cannot be adjudicated by the cell
raster** — `agents/map-populator/src/test_crack_geometry.py` now checks it
with `Box::overlaps` reimplemented verbatim against the built FIXED.DAT.
The aperture is now a **63-unit clear span** (x 2817..2879, closed by the
glob's own 64-wide stub at 2816): 32 valid positions for the shrunken
Avatar, still **zero** for the full-size one, which needs 64 consecutive
units and is refused on every alignment by a whole unit. Chosen over the
minimal one-unit nudge deliberately — that would have left a single
exact-fit alignment the walk code must hit dead-on. FIXED.DAT moved to
`8e5d27ec…`; EUSECODE untouched, so detection did not move.

**TWO OF THE SIX EVENT EGGS WERE SILENTLY DEAD IN THE ENGINE — FIXED
2026-07-28 (fifth session), and only an in-engine run could have found
it.** The patched `Map::loadFixedFormatObjects` promotes FIXED.DAT items
with npcNum 100-116 into Actors. **An egg has no npcNum**: that byte is
its hatch range (`Egg::getXRange` high nibble, `getYRange` low, x32), so a
plain +/-192 range reads as "npcNum 102" and the egg was promoted into an
Actor — which is not an Egg, so it can never hatch. Map 18's
**EggCrackHint (q306)** and **EggAOCeremony (q296, quest step 17)** both
carry 0x66, so both were dead, one clobbering the other's position in
actor slot 102 — **which is also Sigrid's slot on Map 10**. The console
showed it in one line: `Item 102 (class Actor, shape 73) … fam: 4` — an
UnkEgg instantiated as an Actor. `Item::callUsecodeEvent` had always
excluded egg families from npcNum dispatch; the load-time promotion had
not. The exclusion is now in both places (`tools/scummvm-patches/
0001-lost-vale-engine.patch`), pinned by `test_engine_patch.py`, and
verified live: before the fix, standing on EggCrackHint's exact
coordinates dispatched nothing; after it, classes 1457 and 1447 both run.
**The map data was not at fault and did not change** — 0x66 is a
legitimate range. Re-test Sigrid's `use()` (an open question below) now
that the slot collision is gone; this is a strong candidate explanation.

**THE EVENT-EGG QUEUE IS 4-OF-6 DONE, AND IT SURFACED THE REAL BLOCKER.**
CLCLIMB (297, Map 13), AOSCENE (296, Map 18 altar) and ENDGAME (299, Map
10 temple approach) are placed and correct; CLCLIMB is **verified
in-engine** (walked into the box, hatch fired, `attemptedCliffs` read 1 on
the console) and its flag `climbedCliffs` unlocks post-climb dialogue in
five NPCs that previously had no writer at all. Two *harmful* eggs came
out of Map 18: quality 4 was dispatching the base game's **Toran
execution cutscene from Tenebrae** inside the Zealan temple. A new
cross-map guard (`map_walkability.run_event_eggs`) now fails the build if
any egg's quality does not resolve to a manifest-pinned class, so the
label-not-a-class-id error that has now bitten four times cannot ship a
fifth time.

**DD-005 IS FULLY BUILT: quest steps 17-18 are reachable for the first
time.** The temple is sealed by real geometry, the Tiny Tar potion
exists and is placed, and `templeOpen` has a writer. The chain runs
Hrodny → key → chest → potion → shrink → crack → templeOpen →
ceremony → finale. **Never played in-game** — see "Current blocker".

**EGGSHADES IS WIRED AND THE POISON IS BACK ON (2026-07-27, second
session).** The Sacred Circle ceremony (steps 14-15) — the scene holding
the corpus's only `avatarPoisoned` cure — is reachable: Map 10 egg
quality 2→294 + npcnum 0x88, `lv-patched/SHADES.UNK` (6 teleport
coordinates retargeted to our map, hatch reordered so the shield check
precedes the elder teleport-ins, `inShadeScene` re-entry guard),
TypeShades 73→411 so the shades render. Decision A reversed in the same
change: `avatarPoisoned = true` restored in PLNTST, assertions flipped
back. Proven by `test_uc_shades.py` (37 asserts through the built FLX:
full ceremony + cure, no-shield reorder, once-only latch, angry-path
retry, re-entry guard) + 11 new walkability checks (99 PASS) + an
in-engine smoke on kaga (egg dispatches 294→1445, bark fires, elders
verifiably NOT yanked — slot log shows 106/107/116 at home coords).
Found and fixed on the way: **`spawn obj.bark(...)` miscompiled** (string
arg counted as a word, no `str to ptr` — 14 sites emitted `calli 06h`
where retail has zero in 4,533 bark calls; now routed through
`_gen_bark`). Note for later wiring: ATLI.UNK:337 and RAGNAR.UNK:207
call `callTheShades` (unknown-function no-op today) — 1994 had a
dialogue path into this ceremony too.

**THE BASE-POLLUTION TRAP IS FIXED (C3 family, caught live this
session).** install_lv.sh installs the four artifacts INTO
`shared/data/u8-install` — the same dir the builders read their BASE
inputs from. The first rebuild after an install merged LV into itself:
duplicate Map 8 teleport eggs (build refused to write, good) and a
subtler one — the Map 22 shape gallery grew 2 items by copying its
Tenebrae region from the *installed* Map 39. All four bases were
restored from their `.bak`s (verified byte-identical to the GOG pkg
copies). `agents/map-populator/src/base_input.py::pristine_base()` now
guards build_all_maps.py, build_shape_gallery.py, patch_typeflag.py and
lv_wood_wall.py: **if `X.bak` exists and differs from `X`, the base was
clobbered by an install — read the `.bak`.** Verified end to end: a
rebuild AFTER an install now reproduces the canonical FIXED.DAT hash
byte-identically. EUSECODE was never exposed (it reads
`shared/data/USECODE.FLX`, which installs never touch). The playtest
harness's game copy at `shared/u8-lv-patched/` is a THIRD location and
must be refreshed by hand after artifact changes (done this session).

```bash
tools/build_artifacts.sh     # TYPEFLAG → U8SHAPES → EUSECODE → FIXED, then verify
tools/run_all_tests.sh       # 19 files, ~8s, discovers agents/*/src/test_*.py
```

**NEWEST CANONICAL HASHES — 2026-07-31, ninth session CLOSE. Read this
one first; every dated block below it is history.** Only **FIXED.DAT**
moved this session, three times (corridors/climb `b4ae97bb…` → gate
hardening + gateway swaps `5b37ab8b…` → chest nudge), ending at
**sha256 `5f1180d8…`**, recorded via `--record` each time. TYPEFLAG.DAT
`6360e6b3…`, U8SHAPES.FLX `762ca62d…` and EUSECODE.FLX `1a41dda1…`
rebuilt byte-identical all day, so the **ScummVM detection entry never
moved** — neither tree was touched. `sha256sum -c` passes 4/4 at session
close; `install_lv.sh` run and the harness copy at `shared/u8-lv-patched/`
refreshed byte-identical (verified per-file).

Artifacts are not in git (M22); `shared/build/ARTIFACTS.sha256` is tracked and
holds their canonical hashes. **Canonical as of 2026-07-27, second session**
(EGGSHADES + poison + spawn-bark fix recorded together): EUSECODE.FLX
1,498,930 bytes, sha256 `404c953a…`, detection md5-5000 UNCHANGED
`56ae39ad746e58faf45e65f0bacad2ff` (only the size moved — twice this
session, 1,498,874 → 1,498,919 → 1,498,930); FIXED.DAT sha256 `8663ff77…`
(the EGGSHADES egg is the only map change; reproduced byte-identically
across pre- and post-install rebuilds); TYPEFLAG/U8SHAPES unchanged.
`sha256sum -c` passes 4/4. Both ScummVM trees on kaga rebuilt with the
new detection size (`scummvm-lv` auto-patched by build_eusecode.py,
`scummvm-lv-console` + `build_scummvm.sh` defaults updated by hand);
detection verified live: "Running Ultima VIII: Pagan (Gold Edition +
Lost Vale/DOS/English)". install_lv.sh run; harness copy refreshed.

**CANONICAL AS OF THE DD-005 COMPLETION (latest)**: EUSECODE.FLX
**1,500,130** bytes, sha256 `1ce54795…`, detection md5-5000
`00764323ba527948505f4693339a8647`; FIXED.DAT `8f27c956…`;
and for the first time since the wood walls, **TYPEFLAG.DAT
`6360e6b3…` and U8SHAPES.FLX `762ca62d…` MOVED TOO** — shape 859 is
injected into both. All four artifacts now carry LV content. `sha256sum -c` passes 4/4.
**The detection md5-5000 MOVED this time** — to
`8923fdef1988ae685e81731b72a95330` — because adding a class
(EggTempleEntry, 1456) shifts the FLX index table inside the first 5,000
bytes. Both ScummVM trees and `build_scummvm.sh` were repinned on BOTH
values and rebuilt; detection verified live. Watch for this: a size-only
change is the common case, but any NEW class moves the md5 too.

**CANONICAL AS OF THORDIS'S RESTORED HALF (latest, 2026-07-28 fifth
session)**: EUSECODE.FLX **1,501,175** bytes, sha256 `d112e3c9…`;
TYPEFLAG.DAT, U8SHAPES.FLX and FIXED.DAT rebuilt byte-identical again;
detection md5-5000 still `00764323…` (THORDIS replaces an existing class
id, 1130, so no index-table byte inside the first 5,000 moved). Size
repinned in both trees and `build_scummvm.sh`, both rebuilt, detection
verified live on both; install_lv.sh run, harness copy refreshed.

**Canonical as of the plantScene scene-end (2026-07-27 fourth
session)**: EUSECODE.FLX **1,500,228** bytes, sha256 `663771c8…`;
TYPEFLAG.DAT, U8SHAPES.FLX and FIXED.DAT all rebuilt **byte-identical**
to the DD-005 hashes above. `sha256sum -c` passes 4/4. The textbook
size-only change: no new class, so nothing inside the first 5,000 bytes
moved. **Read the md5 note above with care** — the value both detection
tables now carry, and the one the current EUSECODE.FLX actually hashes
to, is `00764323ba527948505f4693339a8647`, not the `8923fdef…` that
paragraph reports; detection was verified live on BOTH trees after this
build, so trust the measurement over the note. Both trees rebuilt on the
new size (`scummvm-lv` auto-patched by build_eusecode.py,
`scummvm-lv-console` + `build_scummvm.sh` by hand) — and note
`build_scummvm.sh` greps for the *md5* to decide whether the table is
current, so on a size-only change it reports "already patched" and will
NOT fix a stale size for you. install_lv.sh run; harness copy at
`shared/u8-lv-patched/` refreshed.

**The 2026-07-19 review queue is closed** except H1 (held by design) and
M22's remote-side `gc`. Landed this session: H8, H9 (packer + map pipeline
test coverage, H8 caught a live name-table bug), M18 (`run_all_tests.sh`),
L12, M22 (untrack + history purge executed), the whole docs-reconciliation
block, H7, P3/P4, M4, H3, and `tools/png2shape.py`.

**Reachability: orphans 19 → 10 → 6.** `docs/reviews/2026-07-25-orphan-triage.md`
is the authoritative per-class verdict and carries the decision record.
`shared/docs/wiring-data.md` was regenerated against the current FLX on
2026-07-27 (fourth session) and is the live count: the four event eggs
(EGGSHADES/EGGAOCEREMONY/EGGCLOUDCLIFFS/EGGENDGAME) now show `unkegg:1`
inbound, and the remaining six are TYPEPEDESTALS, TYPENSGOLDPLAQUE,
EGGCANDLETRICK, EGGMAGNET, TYPEPOISONPLANT, TYPEZEALANCHILD1 — all six
held by an open decision, none by an oversight. It is machine-generated
(`u8_flag_graph.py`); re-run it after any wiring change rather than
hand-editing.

**Working.** The first map change of a new game now completes (LB vision
round-trip verified in-game on kaga). Quest step 1 verified in-game. 14
teleport pairs verified. Map validator 0 ERROR / 0 WARN. Estate **24/24**
(`test_route_reach.py` 23, `test_uc_shades.py` 39, `test_uc_eggs.py` 33,
`test_tiny_tar.py` 16). Walkability **136 PASS**. **The quest route is
walkable arrival-pad to goal on maps 9/10/11/13/17/18**, checked with the
engine's own box arithmetic (`exact_reach.py`) rather than the cell
raster — read the ninth-session block above before trusting the older
"flood" language anywhere in this file. Builds byte-reproducible, including
rebuild-after-install. **CLCLIMB verified in-engine**; quest step 1,
the LB vision round-trip and the Map 8 doors were verified earlier.

**Half-built / known broken.**
- ~~**`plantScene` is set and never cleared**~~ **FIXED 2026-07-27 (fourth
  session), `lv-patched/ATLI.UNK` change 3.** The Passage Test freeze now
  has an end, so both clan elders' routines survive quest step 8. Two clear
  sites, both in the one file already patched: the restored aftermath
  exchange (Atli's own closing line is "Leave you alone now I will"), and a
  **self-heal at the top of `Atli::schedule`** that releases the freeze on
  the first scheduler run after the Avatar has left the Test Grounds
  plateau (map 10, x [12288,13312) y [29184,30208) — build_map_10's
  `TESTGROUNDS_ORIGIN` grid). The self-heal is what covers the two paths
  the dialogue cannot: the **mirror path** (`atliToldTest`, where Thordis
  is teleported in and still has no lines) and the player who never talks
  to the elder at all. **One clear site unfreezes both elders** — plantScene
  is a global and `Thordis::schedule` reads the same bit, so no
  `lv-patched/THORDIS.UNK` was needed; she resumes one in-game hour later
  because `SchedulerProcess::run` walks slots in ascending order and she is
  106 to Atli's 107. Proven by `test_uc_dialogue.py` D13b/D14 (122 asserts,
  +17), which drives event 8 the way the scheduler does. Two sim gaps
  closed on the way: opcode **0x2E (`ge`)** was unimplemented (any `>=` in
  compiled code was a hard sim error) and **`Npc::getMap`** was unstubbed
  (returned 0, so every `Avatar.getMap()` comparison read false).
  **VERIFIED IN-ENGINE** (console build, Xvfb harness): new game →
  `MainActor::teleport 10 19968 7424 0` → `setGlobal 0x419 1 1` → wait one
  in-game hour → `getGlobal 0x419 1` reads **0**. Repeated with the Avatar
  standing on the plateau at (12800,29500,64), the flag still reads **1**
  after a longer window — the guard holds and the release fires, and the
  scheduler demonstrably dispatches event 8 to class 1131 for a promoted
  slot-107 actor. **A game hour is 900 game-seconds at 30fps = ~15 real
  minutes**, and the debugger pauses frames while it is open, so budget
  ~17 minutes per observation and close the console while waiting.
- ~~Two Map 18 UnkEggs carry a quality written as a label.~~ **FIXED
  2026-07-27 (third session).** The altar one became EGGAOCEREMONY (296);
  the "POTION trigger" one was deleted outright (Tiny Tar is a drunk
  potion, never an egg scene). Quality 4 had been dispatching the base
  game's Toran execution cutscene inside the Zealan temple. Guarded
  against recurrence by `map_walkability.run_event_eggs()`.
- **H1** held as a finding, not a fix
  (`docs/reviews/2026-07-23-h1-process-block-semantics.md`).
- **Ragnar dead-end** unfixed: "I have no fight with you"
  (`RAGNAR.UNK:355`) has no `case`. `lv-patched/RAGNAR.UNK` exists, so the
  fix has a home.
- ~~**Restoration is asymmetric**~~ **CLOSED 2026-07-28 (fifth session),
  `lv-patched/THORDIS.UNK` — the 9th patched file.** TESTPLAN.UNK:195-224,
  the lines Thordis speaks when the hatch teleports *her* in, are restored
  into `Thordis::use()` at the same seam Atli's occupy, and they end the
  scene the same way (`endOfPlantScene` latch + `plantScene = false`). The
  Passage Test no longer ends in silence on either branch. Two corpus facts
  came out of it, both verified by scanning every source file:
  **`atliToldTest` has ZERO writers** (declared, read 3× in ATLI and 1× in
  EZREKAL, never set), so her guard is `thordisToldTest = false` — the exact
  complement of Atli's, and what `PLNTST.UNK:83` itself dispatches on, which
  makes the two blocks provably mutually exclusive and therefore safe to
  share the one-shot latch. And **`testFromThordis` has no writer either**
  (read twice in THORDIS, set nowhere) — see the new open item below.
- **Art**: `png2shape.py` works and injected the statue as shape 859 in a
  worktree, but **not in the canonical build** (decision F: hold until seen
  in-game). Injection moves *two* hashes, U8SHAPES and TYPEFLAG.
- **The LB vision is invisible and mute** (found 2026-07-27 while fixing the
  collapse). Shape 411 frame 9 renders nothing visible, and `lb.use()`
  dispatches by shape to class 0x19B GHOST, which has *only* a look() event.
  The scene works — 6 s pause, then the return teleport — but shows nothing.
  Wiring candidate: the LBSCENE pattern (spawn pinned TYPELORDBRITISH 1443,
  puppet the created item) via a future `lv-patched/AVATAR.UNK`.
- **Map* constants: FIXED 2026-07-27 (Fix 2a).** 31 names pinned against
  retail bytecode in `MAP_CONSTANTS` (`u8c_symbols.py` — the evidence table
  lives in its comment; storms-chain, coordinate needles, AIRSPEL suffix;
  MapLostVale=10 is the one context-derived pin). Size-neutral by
  construction: 33 bytes changed across 5 classes, every one 0x00 → pinned
  value. The AVATAR guard now reads `getMap() != 3 && != 0`, and all six
  EGGSHADES vale-teleports (including Atli's, `SHADES.UNK:682`) now target
  map 10. Three AIRSPEL-only names left unpinned by design (ambiguous
  alignment; loud warnings). Caveat found during audit: THORDIS/HRODNY/
  INGYALD pass MapLostVale to `canSafeTeleport`/`safeTeleport`, which
  compile as unknown-function no-ops — those schedule-teleports were
  already dead for that separate reason, so 2a's value there is latent
  until the FREE-routine wiring lands.
- **`PT_*` constants in expression position compile to `push 0`**: 28
  `resetRef(referent, PT_BARK/PT_PATHFIND/PT_ANIM/PT_ACTIVITY)` sites are
  silent no-ops (`PROC_TYPE_ALL` is 6, so type 0 matches nothing). Live in
  THORDIS/HRODNY/INGYALD. Also 23 statement-form pragmas with unpinned PT_*
  types now warn `DROPPED PRAGMA` at build time — that warning list is the
  work queue. Pin values by retail correlation before emitting; do not guess.

## Recent Decisions

- **Reachability is judged by the engine's box arithmetic from now on, not
  by the cell raster** (2026-07-31). `map_walkability`'s 32-unit flood
  stays for "does this region connect" and for its per-item support and egg
  checks; anything that turns on whether a 64-wide body fits goes through
  `exact_reach.py`. The raster has now been wrong in both directions on
  quest-critical geometry, which is one direction too many.
- **Map 13's climb is generated from ONE polyline, not six zone builders**
  (2026-07-31). The seams were the bug, so the fix removed the seams rather
  than re-tuning six sets of constants. Zone builders keep terrain, walls
  and dressing; none of them place a path tile any more.
- **The picket-fence fix is a VISUAL PASS, not a refactor** (2026-07-30).
  Solidifying these walls seals the maps, because the porosity is the
  circulation. Each wall that carries a route needs a doorway designed
  into it — `wall_run_x/_y` take a `gaps=[...]` argument for exactly this.
  Maps 10 and 17 were reverted rather than guessed at.
- **MAGNET/CANTRK deferred on cost-benefit, not difficulty** (2026-07-30).
  The puzzle gates nothing (`candlesCorrect`/`monolithSucks` have no other
  readers), MAGNET would confiscate the Tiny Tar, and H1 makes it behave
  once-per-visit. Restoring one optional set-piece is not worth an
  inventory-stripping monitor with known-wrong loop semantics.

Eight decisions taken 2026-07-26, recorded in §6 of the orphan triage doc:
A poison off until the cure is reachable; B Sigrid gets a reachable class id;
C remove the misfiring obelisk trigger, wire the magnet puzzle separately;
D wire the item classes by npcNum-per-placement, keep the joke items;
E standardise art ids on 859+; F hold the statue out of the build;
G keep the inverted syntax; H move the dropped elder dialogue to Atli.

- **Dispatch has hard id ranges, and this drives everything.** `npcNum` is one
  byte in the map record, so the engine patch's `npcNum + 1024` reaches only
  classes **1025-1279**, and Actor promotion (map.cpp) only **1124-1140**.
  The manifest cursor hands out ids from 1431 up, which nothing map-side can
  reach. UnkEgg quality is a 16-bit word and reaches anything.
- **Sigrid is class 1126 via npcNum 102.** Not an arbitrary slot: the map
  already placed 102, already labelled it "Female Hunter", already sat it in
  the Hoskuld cluster with the Farmer (103) and Child (104) beside it. Her
  character sheet matches exactly. Old pin 1452 is in a new `retired_classes`
  manifest group; the cursor only counts up so it cannot be reissued.
- **Item classes: nine re-pinned into 1252-1260 / npcNum 228-236, seven
  placed.** Two were correctly refused: TYPEZEALANCHILD1 needs Actor
  promotion (it inherits `pesantBoy`, calls `enterConvo`), and
  TYPEPOISONPLANT would have **re-enabled the poison** via
  `TESTPLAN.UNK:250`, silently undoing decision A.
- **The npcNum band is provably safe**: of 87,603 base-game items, 494 carry
  a npcNum and every one is on an egg shape, which the patch excludes.
- **Self-edges are not reachability** (H3). A class that only calls or spawns
  itself has nothing to start it. All 20 base-game `0x58` edges are
  self-edges, so the review's proposed fix would have *masked* orphans.
- **The disassembler rule has one documented exception**, scoped to
  `disassemble_class_summary()` only (CLAUDE.md). Safe because that method
  has two consumers and is not on the round-trip listing path; verified by
  re-running round-trip and encoder unchanged.
- **Pragma emission is pinned-or-dropped, never guessed** (2026-07-27). The
  statement-form `[[PT_*, ref]]` fix emits only encodings proven by exact
  per-class site-count matches against retail bytecode (PT_DEFAULT=1 with
  three referent spellings — the counts are in `u8c_codegen.py`'s comment).
  Every unpinned form warns `DROPPED PRAGMA` and emits nothing. The same
  count-correlation method is how future PT_* / Map* values get pinned.
- **`--stealth` retired**, stage-verify-promote for both artifacts, ratchets
  over assertions, `lv-patched/` outranks the recovered snapshot, detection is
  md5-5000 + size. (Unchanged from before; all still load-bearing.)

## Open Questions

- ~~**THE MAP 8 DOUBLE DOORS DID NOT OPEN IN THE 2026-07-31 RETEST**~~
  **RESOLVED the same night — the doors are FINE**
  (`docs/playtest-2026-07-31-doors-investigation.md`; opened end to end
  with a legitimately fetched key, walked through, trigger 201 fired
  into Map 9). The retest used the wrong idiom: **you unlock by
  double-clicking the KEY (target cursor), then clicking the door** —
  full recipe now in `agents/map-populator/docs/map-08-plateau-entry.md`.
  Every piece of the retest's supporting evidence was invalid (the doors
  DO bark `Locked Door`, transiently at the top viewport edge; the
  cursor never reflects the item under it). All three deeper hypotheses
  eliminated: door leaves present and pristine in U8SAVE.000, EUSECODE
  byte-identical on the whole door path (the 39 differing entries are
  ours, none door-related). **One real intermittent hazard found**: a
  wandering base-game GHOST (shape 411, SOLID) can park in the doorway,
  and the door's retail open path then barks `blocked` until it drifts
  off — retail-correct, not fixable from FIXED.DAT, kill it or wait.
  Process lesson recorded: the 07-02 "doors opened" claim had NO session
  record of HOW, and that gap is what turned a wandering ghost into a
  five-hour "blocking regression". Record the how, not just the that.

- **GitHub still serves the pre-purge objects by SHA.** The purge ran and all
  branches were force-pushed, but force-pushing does not garbage-collect. A
  GitHub Support `gc` request is required and the two checks in
  `docs/history-purge-plan.md` §6a must both 404 **before the repo goes
  public or gains a collaborator**. Backup mirror at
  `../lost-vale-prepurge-2026-07-25.git` still holds every purged byte.
- **The conversation-freeze theory is unresolved.** Inferred in source: our
  `enterConvo()` calls intrinsic `0x9A`, ScummVM leaves it unimplemented
  returning 0, and `kernel.cpp:311` treats objid 0 as a wildcard matching
  every object. Partial evidence against it: a live run logged 7
  `I_resetRef` calls in the startup path, all with real objids, **none with
  `item=0`**. Those are base-game paths though, not our codegen. Needs one
  LV conversation observed with `--debuglevel=1`.
- **Elemental columns** are four identical chimneys; interim (distinct
  base-game shapes) vs proper (four new static shapes) not chosen.
- **TypeZealanChild1** needs Actor promotion and the window (100-116) is
  full at 17/17. Same shape of problem Sigrid had; needs a decision.
- **What is item 6359?** `AVATAR::cachein` runs with that foreign `this` on
  every map-0 load (it is what clears avatar stasis there). Map 0 has ZERO
  fixed items — scanned — so it is a NonFixed item, and the 494-npcNum
  audit covered fixed items only: **the npcNum-dispatch safety audit has an
  unaudited NonFixed flank.** One `ObjectManager::objectInfo 6359` during
  the vision settles the mechanism (shape-1025 retail dispatch vs npcNum 1
  through our patch). Related sighting: GUARD1 (0404) schedule active on
  map 11 via item 6346.
- **Sigrid's `use()` still never dispatches** — unchanged by the pragma fix,
  and none of 2026-07-27's findings explain it. Engine-side promoted-Actor
  dispatch is the suspect. Do not fold it into the pragma story.
- ~~**TWO REACHABILITY SUSPICIONS, raised 2026-07-30**~~ **BOTH SETTLED
  2026-07-31, and they went opposite ways.** Map 10 was a false alarm —
  `flood(body_cells=2)` over-restricting on grid-misaligned corridors,
  as suspected. Map 17's was real and quest-blocking. The instrument that
  settled them is `exact_reach.py`; the verdicts are pinned by
  `test_route_reach.py`. **The standing lesson**: the 32-unit cell raster
  is wrong at body width in BOTH directions — it shipped the crack sealed
  and it reported walkable corridors impassable. Use `exact_reach` for any
  claim that turns on whether a body fits.
- **The remaining unreached pockets are unexplained, not cleared.** Map 17
  is at 91.5% reached, map 11 at 89.9%, map 9 at 86.6%. Some of that is
  wall-edge slivers and the cloud platforms (scattered 512-stride slabs
  that were never a connected surface), but nobody has walked the list.
  A component-labelling mode on `exact_reach` would turn that percentage
  into a work queue.
- ~~**CAN THE JUMP BUTTON CLIMB OVER THE QUEST GATES?**~~ **YES — CONFIRMED
  IN-ENGINE 2026-07-31 (morning playtest), AND FIXED THE SAME DAY** (see
  the ninth-session block). Both gates were climbed live; both are now
  triple-stacked to 120/144 with the anti-climb coverage pinned in
  `test_route_reach.py`. The evening retest verified the hardening against
  the exact morning repros — see
  `docs/playtest-2026-07-31-retest-hardened-gates.md` for the verdicts.
  The standing lesson for any future gate: **jump auto-climbs up to 72
  units onto any standable top, and wall tops ARE standable** — a gate
  wall must be a continuous stack past 72, with no 40-ish ledge adjacent.

## Next Steps

**0. THE ONE THING THAT IS DOUGLAS'S** — the ~2-minute checkpoint walk at
the top of this file. Everything else here is agent-shaped work; the exit
test (steps 1-18 continuous, no debugger) is gated on that save existing.

*(0b — the Map 8 doors scare — was investigated and closed the same
night: wrong interaction idiom, doors fine, key recipe now documented in
the map-08 doc. One retail-correct hazard noted there: a wandering ghost
can transiently block the doorway.)*

*(Resolved and removed from this list: the temple barrier — decided as
DD-005, Tiny Tar, and fully built; `plantScene`; Thordis's half; the
reachability re-check, done 2026-07-31 and both maps fixed. The DD-005
chain and steps 17-18 have both run in the engine.)*

1. **Picket fences, continued: maps 10 and 17.** Both reverted 2026-07-30.
   The pattern to follow is Map 09: make the run solid, then pass
   `gaps=[...]` to `wall_run_x/_y` centred on the passage the wall leads
   into. **`test_route_reach.py` is now the guard** — it floods every map
   from its arrival pad, so a wall that seals a route fails the estate
   instead of shipping. Map 17 additionally uses 489/490 for east-west
   runs and needs 492. Note what this session found while looking: map
   17's east-west "walls" are 489 laid along its 32-unit axis at a 256
   stride, i.e. 87% hole, and map 13's base-zone gate and map 10's cliff
   gate are single 128-wide items in wide-open zones — you walk around
   them. The gates gate nothing today (the 07-31 gateway swaps put the
   TRIGGERS behind the gates, which was the other half of the same
   problem, but the funnel walls are still this item's job).
2. **MAGNET (281) + CANTRK (280)**, the last two eggs. **Deliberately
   deferred 2026-07-30**, and not for the reasons previously listed: the
   candle art and the candle class are now easy (the `lv_tiny_tar.py`
   pattern solves the first, npcNum 237 → class 1261 the second). What
   remains is **H1** — the finding's own table says CANTRK has no explicit
   wait, so a naive loop fix HANGS the VM, and it compiles today with zero
   suspends. Two further reasons to leave it: MAGNET sweeps `TypePotion`
   with `frame > 0`, which would **confiscate the quest-critical Tiny
   Tar**; and `candlesCorrect`/`monolithSucks` are read by nothing but
   MAGNET and CANTRK themselves, so the puzzle **gates no quest progress**.
   Do H1 first, and only with a playtest available.
3. **LB vision wiring decision**: make it visible and voiced (LBSCENE
   pattern, spawn pinned 1443) or ship the silent pause for now.
4. ~~**Thordis's half** of the Passage Test dialogue~~ **DONE** (fifth
   session). What it uncovered and did NOT fix — the next thing to decide in
   this corner: **`testFromThordis` has no writer**, so `not testFromThordis`
   is permanently true and two authored 1994 threads are mis-routed on the
   *other* branch. Her case `"I have taken your Test."` (the only writer of
   `zealanMark`) is unreachable, and a player Thordis herself sent to the
   Test instead gets `"Help me, I've been poisoned."`, whose barks blame
   Atli — *"Told you, that rotting pile of fish offal, Atli did!"* The
   one-token repair is to re-gate both reads onto `thordisToldTest`, which
   is written exactly where she sends them (original lines 1213/1243). It is
   a live-branch re-gate, so it wants a decision, not a drive-by.
5. **Coupled art fixes needing no new art** (Shades 73→411 DONE this
   session): gold plaques 158→599/614, obelisk 721→442/793, elixir vial
   frame 13→0.
6. **The statue into the canonical build**, once seen in-game (decision F).
7. **PT_* value pinning** (28 no-op resetRef sites + 23 dropped pragmas)
   when NPC behavior work resumes — the build's DROPPED PRAGMA list is the
   queue. The `canSafeTeleport`/`safeTeleport` unknown-function no-ops
   belong to the same NPC-schedule work. The SHADES ceremony's
   `killProcess(x, PT_ACTIVITY)` no-ops are in this family too (benign
   today because `inShadeScene` gates both elders' schedules for the
   ceremony's duration — note that plantScene no longer holds anything
   open, see the scene-end fix above). **A third unpinned-constant family
   surfaced with that fix: the day-period names.** `daytide`, `eventide`,
   `threemoons`, `firstebb`, `lastebb` and `bloodwatch` all compile to
   `push 0`, so in `Atli::schedule` *both* `getPeriod()` branches are false
   and his destination `point` stays (0,0,0) — a latent teleport-to-origin
   that only `safeTeleport`'s unknown-function no-op is currently hiding.
   **Pin the periods before wiring `safeTeleport`, or Atli walks into the
   void.** Same evidence method as Fix 2a (AIRSPEL.UNK:292 has a
   `case daytide`, which is the correlation handle).
8. **`callTheShades` wiring** (ATLI.UNK:337, RAGNAR.UNK:207): 1994's
   dialogue path into the ceremony, currently unknown-function no-ops.

## Driving the game from a session

**Superseded 2026-07-26.** The old note here said an agent must take focus via
`osascript`. That is wrong. Two harnesses now exist and neither takes focus.

- **The console PAUSES the engine, and `dbg` leaves it attached.** Every
  in-world interaction has to be sandwiched: `dbg ...` → `resume` →
  click/walk/keys → `dbg ...`. Keystrokes and mouse drags sent while it is
  attached do nothing whatsoever, which looks exactly like broken input and
  wasted most of an afternoon before the pattern was obvious.

- **Item pickup WORKS — here is the recipe** (2026-07-28, and it took a
  while, so follow it rather than improvising). Open the pack with `i`,
  drag the gump clear of the item by its brown frame, then: move the
  cursor onto the item, `mousedown 1`, **wait ~0.8 s**, move in small
  increments (8 px at a time) until the item lifts onto the cursor —
  screenshot to confirm it lifted, because a single big jump usually does
  NOT start a drag — then release it ON THE AVATAR'S SPRITE, not inside
  the open pack gump (corrected 2026-07-31: dropping onto the pack's dark
  interior gives a red-X refusal; the sprite drop is what banks the item).
  Verify with `total weight` from `ObjectManager::objectInfo 1`, not by
  eye: U8 weights are TYPEFLAG weight x10, so a shield half is +40 and a
  sprawled skeleton is +190.

- **THE SHIELD HALVES SIT UNDER A SKELETON, AND THE SKELETON WINS THE
  CLICK.** `build_map_17` puts each half (shape **539**, the small white
  studded shield) 64/32 units off a sprawled skeleton (shape **332**,
  SHAPE_SKELETON_SPRAWLED — a 2x3 SF_CONTAINER that renders as a grey
  mass). On screen they overlap, the skeleton is the bigger target, and
  grabbing "the shield-looking thing" gets you a corpse: I carried two of
  them around before noticing the weight was +190 each instead of +40.
  The half is the WHITE STUDDED SHIELD, slightly below and right of the
  grey mass.

- **The ceremony bails at a precise, known instruction.** With no halves
  in the pack, `EggShades::hatch` reaches **offset 0x1A1 (417)** — the
  `ret` that closes Ezrekal's "Bring the sacred shield" branch. The
  elder teleport-ins are the three `calli 158` (`Actor::I_teleport`) at
  0x1A8-0x1D6, immediately after `pop global 1106` (`inShadeScene`), so
  they are real calls and would fire; the scene simply never gets there.
  If a run ends with `shieldFixed`/`godsFree` still 0 and all three elders
  at their home coordinates, that is this branch, not a teleport bug.

- **Item pickup was the open gap.** The full Sacred Circle ceremony needs
  both shield halves inside the Avatar's BACKPACK — `SHADES.UNK` does
  `foreach ... TypeAOFrizbee within container Avatar.getEquip(EQ_BACKPACK)`
  and gives up when the pack is empty of them, so equipping is no use.
  Getting a world item into the pack means opening it (`i`), dragging the
  gump clear of the item, and dragging the item into it — and synthetic
  drags have not landed one yet. Two failure modes seen: the drag drops the
  item straight back on the ground, and (worse) an imprecise grab pulls the
  Avatar's OWN BACKPACK off, after which `i` silently does nothing and the
  ceremony's shield search cannot run at all. Restart the session if the
  Avatar's back looks bare.

- **Two more rules from the 2026-07-31 doors investigation.** Add
  `debugflag_enable Object` to standard session setup — every click then
  logs the clicked item's `dumpInfo()`, which is the reliable way to know
  what you hit (the cursor NEVER reflects the item under it, and barks
  render transiently at the top viewport edge — screenshot within ~0.5 s
  or you will conclude "no response" falsely). And **locked doors**: use
  the key ON the door (double-click key → target cursor → click door);
  the door's own use() barking `Locked Door` is it working as intended.

- **Use `session.sh dbg <command>`, not `cmd`.** `cmd` is fire-and-forget:
  it appends to a file ScummVM only drains WHILE THE DEBUGGER IS ATTACHED,
  so anything sent while it is closed queues and executes later, out of
  order — including stale `exit` lines that close it again. That backlog is
  why teleports silently do not happen and why `Cheat::toggle` lands on the
  wrong parity, whose only symptom is `Cheats are disabled`. `dbg` attaches
  if needed, sends one command, waits for the log to grow, and prints the
  reply. `start` now also answers the modal "Give thy name:" book, without
  which the world is never drawn.

- **Linux input, learned the hard way 2026-07-28** (all three now handled
  by `tools/playtest-linux/session.sh`): **the Avatar walks on the RIGHT
  mouse button**, not the left — a held left button makes him turn on the
  spot, which reads exactly like input not reaching the game (use the new
  `session.sh walk <dx> <dy> [secs]` verb, which holds button 3 at an
  offset from the surface centre); **a fresh `start` comes up inside the
  intro movie**, where the debugger answers and teleports land but the
  world is not visible and mouse input goes nowhere (`start` now presses
  Escape for you — and screenshot before debugging anything that looks
  inert); and **X focus is not sticky** without a window manager, so
  `windowfocus` must precede the ctrl+alt+d chord after any mouse use.
  One more: the debugger PAUSES frames, so a walk issued while it is open
  does nothing at all.

- **macOS: `tools/playtest/`.** Input goes through `CGEvent.postToPid`, which
  delivers to a background process, so the game runs while you work in other
  windows. Read its README before using it: modifier chords need real
  `flagsChanged` events, `::` cannot be typed into a background app at all (Tab
  completion supplies it), and captures must use `screencapture -l <window-id>`
  rather than `-R`.
- **Linux: `tools/playtest-linux/session.sh`.** Gives ScummVM a private Xvfb
  display where it is the only client, so plain `xdotool` works and nothing is
  ever taken from the desktop session. Verbs: `start`, `stop`, `status`, `key`,
  `type`, `cmd`, `debugger`.

**The better path is the text-console build.** `--enable-text-console` sets
`USE_TEXT_CONSOLE_FOR_DEBUGGER`, replacing the in-game overlay with a
`fgets(stdin)` loop (`gui/debugger.cpp:282`). Debugger commands become lines on
stdin and every response lands in the log, which removes the `::` problem, the
Tab-completion hack, and all screenshot-reading of console output. Build a
second tree beside the normal one:

```bash
LV_SCUMMVM_DIR=$PWD/scummvm-lv-console \
LV_CONFIGURE_EXTRA="--enable-text-console --disable-readline" ./build_scummvm.sh
LV_SCUMMVM=$PWD/scummvm-lv-console/scummvm tools/playtest-linux/session.sh start
```

Keep the normal `scummvm-lv/` for human play, since the text-console build has
no overlay console.

**Traps that have already cost real time**, all recorded in
`docs/playtest-2026-07-26-results.md`:

- Class ids are offset from FLX entries by two. Use
  `UsecodeFlexArchive.get_class_data(classid)`, never raw `FlexArchive[i]`.
- Village NPCs wander. Use `tools/playtest/talk_to.py`, which locates and
  clicks in one invocation.
- Verify `pgrep -f scummvm-lv/scummvm` returns exactly **one** pid. A stale
  instance silently eats input while you read the fresh one's log.
- Muting needs `mute=true` in **both** `[scummvm]` and `[ultima8]`, and ScummVM
  rewrites its config on exit, so edit with the game stopped.

## Current blocker

**None in the code.** The remaining step is manual and it is yours — see
START HERE at the top of this file: load `cp2-palace.sav`, walk north to
the teleporter at (13054,2322), out to map 8, stop on arrival and F5-save
that as the plateau base. The exit test is steps 1-18 continuous from
there.

### CORRECTION, 2026-07-30: this section used to claim the crack was proved. It was not.

Everything that stood here was written on 2026-07-27. It asserted that
Map 18's Tiny Tar crack was a **32-unit** aperture, "proved" by a
footprint-aware flood, and quoted 11,441 / 21,923 reached cells as
evidence. **All of that is superseded, and the proof was invalid.**
`b95de7a` (2026-07-28) found the crack was **impassable at BOTH sizes** —
the entire DD-005 entry route was sealed — and widened it to 63 units.

**The standing trap, which matters more than the fix. U8 item boxes are
HALF-OPEN.** `Box::contains` is `px > _x - _xd && px <= _x`, so a 96-wide
filler placed at x=2848 occupies **2753..2848 inclusive**, and the glob
piece east of it occupies 2880..2943. The clear span was 2849..2879 =
**31 units** for a body needing 32, and `Box::overlaps` is strict — so the
shrunken Avatar had **zero** valid positions anywhere in the wall line.
Off by one world unit.

**Why the flood missed it.** `map_walkability` quantises to 32-unit cells
and marks a cell blocked only when a blocker covers the cell **centre**.
The filler's last unit — 2848, the first unit of cell 89 — vanished in
that rounding, the cell read as fully free, and the body-width flood
walked a 1-cell body through a gap the engine refuses. **The cell raster
is the right instrument for "can you get from A to B" and the wrong one
for a one-body-width aperture.** `test_crack_geometry.py` now reimplements
`Box::overlaps` verbatim and runs it over the BUILT FIXED.DAT with globs
expanded, so it tests what ships rather than what the builder intended;
`map_walkability`'s aperture assertions were rewritten to stop claiming
they prove the mechanic. **Never size a single-body aperture with the
cell flood again.**

A second bug from the same 07-27 work was caught in the same run:
`cb7fa78`, "Stop the engine promoting eggs into Actors" — two event eggs
were dead because the engine was promoting them.

### The templeOpen archaeology, kept for the record

This is why DD-005 exists at all. The flag was **read in 23 line-sites**
across the 1994 corpus — HRODNY:460, INGYALD:366, THORDIS:491, TJORVI:228,
EZREKAL x3, plus lv-new AOSCENE:27 — and **written in zero**.
`shared/docs/wiring-data.md:83` had already recorded it ("writers:
(none)"). The mechanism was never authored in 1994, and the writer ducked
it in dialogue: Ezrekal, told the temple is open, says *"How managed it
did you? How...oh, never mind."* Every NPC routes the player to Hrodny,
and Hrodny refuses — her `case "How can I open the temple?"`
(HRODNY.UNK:1086-1124) says the chest key is lost and spawns a quality-20
key into the world. She never creates a potion.

The design docs disagreed on the barrier (`story-beats.yaml:344-359`, beat
16): **Plot v1.2** wanted "some sort of explosive and a nice piece of
usecode"; the **Synopsis** wanted "a guardian which can only be slain by
someone bearing the intact shield". Douglas chose neither — see DD-005 in
TODO.md for why the evidence points at Hrodny's Tiny Tar instead.

**A correction that still stands:** an earlier draft of this file claimed
"the design docs put the shrink on the interior Tiny Entry, not the outer
seal". That is **not supportable**. The 13 scanned 1994 design PDFs in
`gog/ultima_8_lost_vale_design_documents.zip` contain **zero** occurrences
of "tiny", "tar", "shrink" or "potion". The interior-Tiny-Entry split is
this project's own invention
(`agents/map-builder/docs/map-18-ancient-temple.md:114-127`) and must not
be cited back as a source.

The three sub-items that used to ride along here are all **done**: the
frame-8 potion exists (shape 859, built by `lv_tiny_tar.py` as step 3/5 of
`build_artifacts.sh`); Hrodny's key bag no longer floats (z 64 -> 0); and
she now gives a location lead, with the potion's effect taught at the wall
by `EggCrackHint` rather than by her.