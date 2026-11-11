# Breach rubble and the crack's floor cue, verified in engine (2026-10-01)

Change under test: the uncommitted merge of `worktree-agent-ac6b8951772c5e65c`
on `main` (HEAD `db28de4`). `build_map_18.py` gains `build_breach_rubble()`
(four shape-6 gravel flats at x 2815/2943, y 6271/6399, and two shape-524
rubble piles at (2687, 6271) frame 2 and (3007, 6271) frame 3, all on the
sanctum side) and one shape-6 plate on the hall floor at (2848, 6047).
`lv-new/CRACKHNT.UNK`'s hint bark gains "Grit has sifted down from the crack
and lies heaped on the flags below it." `map_pins.json` is regenerated.

Artifacts: the full `tools/build_artifacts.sh` exited 0 and reproduced all
four canonical hashes byte for byte (EUSECODE `6e6386f9`, FIXED `e2336bf9`).
`./install_lv.sh` exited 0. `session.sh start` synced the new bytes into
`shared/u8-lv-patched/` (it held the old `7f885f5e` / `f92973ee` before), and
the engine logged `usecode/eusecode.flx: aae44805..., 1505651 bytes` and
`Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)`. Binary
`scummvm-lv/scummvm` built 19:35:33 today and embeds `1505651` in its
`detection_tables.h`. One ScummVM process (PID 526988) ran every test; no
`Segmentation`, `Assertion`, or `Cycle in paint dependency graph` line in its
log. Plates are in `docs/playtest-2026-10-01-breach-rubble/`, 640x400, named
by test ID.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| S1 | Test estate | `tools/run_all_tests.sh`: 34/34 | **PASS** |
| S2 | Full build and hashes | exit 0; all four OK; bytes identical to those on disk before the build | **PASS** |
| S3 | Compilation Report | 48 files, 46 succeed; failures `EALOGO.UNK` and `TJORVI.UNK`, the allowlist pair; EUSECODE 1,505,651 bytes | **PASS** |
| S4 | Geometry, engine box arithmetic | `exact_reach` with and without the seven new records: totals unchanged (open full 11,595; closed tiny 12,204; closed full 6,016); the only change is 608 origins over the two pile footprints moving from z 0 to z 8 | **PASS** |
| S5 | Shape IDs | neither shape is new or renumbered (both already ship on Map 10, `lv_shapes.py:244`, `:256`); `grep -nw 524 u8c_symbols.py` and `grep -rlw 524 lv-new lv-patched` return nothing, and the only `6` values in `u8c_symbols.py` are `EQ_BACKPACK`, `CONTAINER_FAMILY`, and a sound id | **not triggered** |
| S6 | ScummVM fork | no fork commit since `e0d6084d` (19 September); tracked patch equals the fork diff (`diff -q` silent) | **PASS** |
| 1a | Hall-side gravel cue visible on approach | the plate is behind the 120-unit wall from the fixed camera at every approach position; the Avatar standing on it is invisible too | **FAIL** |
| 1b | New hint bark shows whole | two pages, no single-word page; page 1 ends on a dangling "But" | **PASS** (with a note) |
| 2 | Sanctum-side gravel and both piles render, before and after `templeOpen` | all render over the SI_DRAW floor, in front of the whole wall and in front of the open breach | **PASS** |
| 3 | The breach reads as a collapse | debris now says "something fell here"; the opening itself is still a straight-jambed rectangle and the gravel is a hard-edged square mat | **PARTIAL** (judgement) |
| 4 | No regression: shrunken entry, full-size exit and re-entry, diagonal approaches | `templeOpen` 0 to 1; out to Map 10 and back; reseal and reopen; four diagonals all crossed, two of them over a pile at z 8 | **PASS** |
| 5 | No paint-order spam near the rubble | 0 `Cycle in paint dependency graph` lines over the whole session, including frames with the Avatar on the piles and the gravel | **PASS** |

## Method and harness writes

Saves and `scummvm.ini` were copied to the scratchpad first
(`bak1001/`). `~/lv-checkpoints/run-s16-tinytar.sav` was copied over
`ultima8.001` and loaded with `Ultima8Engine::loadGame 1`: Map 10 at
(21760, 8544), `templeOpen` 0, three frame-8 Tiny Tar in the pack.

**One position write:** `Cheat::toggle` (echo `Cheats = true`),
`MainActor::teleport 10 18432 22680 0` (a same-map move to the spot the Map 18
exit lands on; the driver's retry sent it twice to the same point), then
`Cheat::toggle` (echo `Cheats = false`). Cheats were off for all movement
after that. `CameraProcess::moveToAvatar` was needed once, because that save's
camera is parked away from the Avatar (finding 5 of the 26 September report).
From there the Avatar **walked** onto Map 10 trigger 211, and the log shows
`Unloading map 10` / `Loading Fixed items in map 18`: Map 18 came from the
new FIXED.DAT through a real teleport-egg arrival.

Other console use: `objectInfo`, `findShape`, `getGlobal`. No save was
written.

## S4: geometry, PASS

`exact_reach.py` (the engine's half-open `Box::overlaps`) over the built
Map 18, seeded in the sanctum at (2848, 6400), with and without the seven new
records (script `rubble_reach.py` in the scratchpad):

```
OPEN full   with 11595  without 11595   lost 608 gained 608
CLOSED tiny with 12204  without 12204   lost 450 gained 450
lost z 0 608 x 2599..3063 y 6207..6327   gained z 8 608 (same origins)
```

Every lost origin is a 64x64 body overlapping a pile footprint
(x 2592..2687 or 2912..3007, y 6176..6271); the same origins are gained at
z 8, standing on top. The piles are 8-unit steps the walker takes (riser 8 is
in U8's search table). Lane origins 2751..2912, between the piles, are
untouched. The gravel (zd 0) changes nothing, as its docstring argues. The
closed-state route keeps its shape: the full body still cannot cross
(seeded sanctum, hall unreached), the tiny body can.

## 1a: hall-side gravel cue, FAIL

`findShape 6` on arrival lists Item 13736 at (2848, 6047, 0), so the plate
is loaded. Its box is x 2721..2848, y 5920..6047, which is 96 to 223 units
north of the wall's north face (y 6112) and on the far side of it from the
fixed camera. The wall is three 40-unit courses. In the same screen column, a floor point d units north of the wall
also sits d units further west, so it rises d/4 screen pixels against the
wall's 120-pixel top edge: anything closer than about 480 units behind the wall
is hidden. This plate is at most 223 units behind it.

Plates:

- `A1-hall-approach-y5620.png`, `A2-hall-approach-y5820.png`: approaching
  down the crack column; the Avatar is already hidden at y 5820.
- `A3-hint-bark-24s-sheet.png`: the Avatar walked x 2828 from y 5828 to
  6092, straight across the plate (his body x 2765..2828 lies inside the
  plate's 2721..2848), and is visible in none of the 45 frames.
- `A5-avatar-standing-on-hall-plate.png`: Avatar at (2724, 5996), overlapping
  the plate's west edge; not visible.
- `A5b-hall-plate-footprint-overlay.png`: the same frame with projected
  footprints. Magenta is the hall plate: it falls entirely on the wall face.
  The overlay is validated by the sanctum items in the same frame: cyan
  (gravel union) and yellow (piles) land on their sprites.

**The plate appears to show only after the wall is gone**, as a dark sliver
through the open breach (`D2z-breach-open-zoom.png`,
`F1z-breach-open-from-hall-zoom.png`), when it no longer has a job.
`D2b-hall-plate-overlay-through-breach.png` overlays the projected footprints
on that frame: the overlay sits about 19 px high there (the cyan sanctum
outline is offset from its sprite by the same amount), and with that offset
the sliver falls at the hall plate's west corner, north of the wall line. It is
the only dark flat on the hall side, so the identification is likely, read by
position.

**Mitigation the change did not claim:** the *sanctum-side* gravel and both
piles stand in front of the wall, so a player walking the hall sees a dark
spill and two heaps at the foot of the crack from y 5620 on (`A1`, `A2`).
That is a real ground-level cue at the right x, and it is what the new bark
sentence ("heaped on the flags below it") matches on screen. The cue the
change intended (the hall plate) does nothing; the cue it got by accident
works.

The plate is also off-centre: its x 2721..2848 covers only the west half of
the crack column (2817..2879), centre 2784 against the crack's 2848.

## 1b: the hint bark, PASS (with a note)

Walking south onto the plate hatched the wall egg. Filmed every 0.5 s for 24 s
(`A3-hint-bark-24s-sheet.png`):

- Page 1, about 20 s (`A3-hint-bark-page1.png`, zoom `A3z-...`): "The stone
  here is split from top to bottom -- and there is open air beyond it. Grit
  has sifted down from the crack and lies heaped on the flags below it. But"
- Page 2 (`A4-hint-bark-page2.png`, zoom `A4z-...`): "the gap is no wider than
  my hand."
- Then, because three potions were carried, "Hrodny's dark potions are in my
  pack. For the moment of miracles, she said they were. I wonder."

No page holds a single word, so the orphan-page rule holds. Page 1 does end
on the sentence's first word, "But", with the rest of the sentence alone on
page 2. Any reflow that moves "But" down (or splits the bark in two, the way
`6e2f0c3` did for the endgame) would fix it.

## 2: sanctum-side debris renders, PASS

Before `templeOpen`, wall whole: `A2`, `C0-drink-at-crack.png`, and the first
frame of the entry film, `C1-sanctum-debris-before-sweep-wall-whole.png`
(zoom `C1-...-zoom.png`). The 256x256 gravel spill, the grey west pile, and
the grey east pile all paint over the sanctum floor (shape 35, SI_DRAW), with
the shape-47 stub still standing in the crack.

After `templeOpen`: `C4-breach-open-avatar-in-gap.png`, `D1`, `D2` (zooms
`D1z`, `D2z`), `F1`, `F2`. Same three items, same positions, nothing
clipped. After the Map 10 round trip, `findShape 6` read 5 and `findShape 524`
read 2 again: they reload from FIXED.DAT with the wall, and the reopen sweep
leaves them alone (they are q 0).

The flat-sort rule (`.claude/rules/map-geometry.md`) predicts this: shape 6
carries neither SI_DRAW nor SI_OCCL (`TYPEFLAG`: `SI_FIXED, SI_SOLID,
SI_LAND`, footpad 4x4x0), so it sorts after the SI_DRAW floor.

**Negative control:** the only sorter warning in the log is the pre-existing
`Skipping invalid shape in sorter: 539,4!` from the old save's invisShield;
no line names 524 or 6, so frames 2 and 3 of 524 exist.

## 3: does the breach read as a collapse, PARTIAL

Judged from `C4-...-zoom`, `D1z`, `D2z`, `F1z`, against the 26 September
plates `D7`, `D10`, and `E2b`.

What improved: there is now evidently fallen stone. Two grey heaps flank the
opening and a dark spill covers the floor in front of it, so the eye reads
"something came down here" at a glance. Before, the plate showed a clean hole.

What still reads as a cut doorway:

1. **The jambs are unchanged.** Both sides of the opening are full-height,
   straight, vertical course ends, and the top is a clean horizontal line.
   The debris sits in front of a doorway; the doorway itself is not broken.
2. **The gravel is a hard-edged square.** Four 128x128 tiles on the floor
   grid make a 256x256 dark mat with straight edges on all four sides
   (`D2z` shows this most plainly). It reads as a rug or a floor inlay.
   Spilled grit would thin out raggedly, and would lie on the hall side too.
3. **The piles are symmetrical, one per side, outside the lane.** That is the
   placement a sweeper would leave, pushed clear of the path. A collapse
   leaves its biggest stones in the opening. The lane constraint
   (`test_sanctum_clearance`, x 2700..2880) forces this, but the eye reads it.
4. **Nothing on the hall side.** The wall fell south, apparently, and left the
   north floor clean.

My call: an improvement worth keeping, roughly halfway to a collapse. The
cheapest next steps, in order of effect per change: break the gravel's square
outline (a partial tile, 425 or 783 flats at the edges, or one 2x2
`SHAPE_RUBBLE_SMALL` (526) set inside the mat's corners outside the lane), and
put one low piece of rubble at z 0 on the hall side of the gap, outside the
lane, so the debris reads as having come down on both sides. The jambs need art
or broken course-end frames, and are a larger job.

## 4: no regression, PASS

**Shrunken entry.** At (2876, 6108) one potion was drunk from the pack
("I'm feeling funny", `C0`); `objectInfo 1` read shape 708. One 1.2 s walk
south, filmed every 0.5 s for 60 s (`C-entry-film-60s-sheet.png`): "I am
through..." (`C2-entry-bark1`), "Behind me the split stone groans and slumps,
and the crack falls open into a gap a man could walk through." (`C3-entry-bark2`,
the tiny Avatar standing on the new gravel), the regrow, then full size at
(2876, 6228). `templeOpen` read **1**.

**Negative controls, closed wall:** before the drink, three south pushes at
full size stopped at y 6108 (the wall's box starts at 6112), and south-east
and south-west pushes slid along it (`B1-full-size-push-south-refused-closed.png`).
**After the breach:** three full-size north pushes at x 3220 and three at
x 2532 stopped at y 6220 (`E5`, `E6`); the standing wall either side still
blocks.

**Diagonal approaches**, each on a line through the gap's centre that grazes a
pile corner, 0.5 s bursts with position read between them:

| Test | Start, direction | Trail (x, y, z) | Result |
|---|---|---|---|
| T1 | sanctum (2560, 6352), NE | (2640, 6272, **8**), (2744, 6272, **8**), (2824, 6192, 0), (2824, 6096, 0) | crossed to hall, over the west pile (`E1`) |
| T2 | sanctum (3056, 6440), NW | (2996, 6380, 0) ... (2788, 6172, 0), (2788, 6076, 0) | crossed to hall (`E2`) |
| T3 | hall (2512, 5880), SE | ... (2876, 6148, 0), (2876, 6252, 0) | crossed to sanctum (`E3`) |
| T4 | hall (3084, 5868), SW | ... (2788, 6164, 0), (2716, 6244, **8**), (2644, 6316, **8**) | crossed to sanctum, onto the west pile (`E4`) |

No stall. Some bursts register no movement (T1 every other burst, T2 twice,
T4 once), and they happen on open floor and in the lane as often as on a pile:
at T1's and T2's starting points and at (2824, 6192) and (2788, 6172) in the
lane. The next burst always moved. I read it as the harness dropping a walk
after a console close (finding 5), with moderate confidence. The
pile climbs match S4's z 8 positions.

**Full-size exit and re-entry.** From (2532, 6220) the route north through
the breach to (3072, 1300) logged `Unloading map 18`, landing on Map 10 at
(18432, 22688) (`F0`). Walking south onto trigger 211 reloaded Map 18:
shape 15 **265**, shape 47 **2**, q307 stub 16870 at (2816, 6143) listed (the
reseal); gravel 5, piles 2. Past the doorway egg at (3072, 4800): 15 **260**,
47 **1**, no q307 listed (the reopen). A full-size walk from (2832, 5872) to
(2832, 6360, 0) went straight through (`F1`, `F2`).

## 5: paint order, PASS

`grep -c 'Cycle in paint' lv_run.log`: **0** over the whole session, which
includes the Avatar standing on both piles (T1, T4), standing and walking on
the gravel at full and tiny size, and the east pile's box overlapping the east
gravel flat in XY (x 2912..2943, y 6176..6271). The pile is 8 tall on a zd 0
flat with no tall item overlapping it in XY (the wall ends at y 6143), which is
the configuration the rule says is safe.

## Findings outside the plan

1. **The hall plate is a dead item in the closed state.** It costs a FIXED.DAT
   record and a map pin, and the builder comment and CRACKHNT header both
   describe it as the cue the player aims at. Both comments are wrong about
   what the player sees. Moving it south of the wall would duplicate the
   sanctum spill; deleting it, or keeping it and correcting the two comments,
   are the clean options. Same root cause as the hall-side Avatar being
   invisible in the 26 September `C1` plate: everything within about
   480 units north of a 120-tall east-west wall is hidden.
2. **The bark's page break strands "But"** (1b). Cosmetic, cheap.
3. **The hint shows both barks in sequence with potions carried**: the grit
   bark's two pages, then the potion line. The 26 September report (`H0`)
   said the potion line came "instead"; that session filmed too coarsely to
   see the first. A player carrying potions does get the new sentence.
4. **`run-s16-tinytar.sav`'s camera** is still parked away from the Avatar
   after a same-map teleport; `CameraProcess::moveToAvatar` fixes it. A map
   switch also resets it. Worth a line in `traps.md`.
5. Walk bursts sent right after a console close are sometimes lost: the
   same alternating no-move shows in the very first `goto` on Map 10 and on
   open floor in T1 and T2. It accounts for every no-move in the diagonal
   table.

## Harness anomalies

- `con()` retries on no reply, so `MainActor::teleport` was sent twice
  (same coordinates, no effect beyond the first).
- A `pgrep -f` wait loop matched its own command line and ran to its 600 s
  timeout; it was killed. No effect on the game.
- `goto` with a 16 to 20 unit tolerance oscillates by 96 units and exhausts
  its budget; slow walks (mouse 45 px from centre, 0.45 s) position to within
  a few units.

## Disk changes

- This report and `docs/playtest-2026-10-01-breach-rubble/` (36 plates).
- `shared/build/` rewritten by `tools/build_artifacts.sh` with identical bytes
  (new mtimes).
- `shared/data/u8-install/` rewritten by `./install_lv.sh` (it already held
  these hashes).
- `shared/u8-lv-patched/USECODE/EUSECODE.FLX`, `STATIC/FIXED.DAT`, and
  `FIXED.DAT` synced from `shared/build/` by `session.sh start` (untracked);
  they now hold `6e6386f9` and `e2336bf9`.
- `~/.local/share/scummvm/saves/` (all 48 files) and
  `~/.config/scummvm/scummvm.ini` restored from the copies taken first (md5
  `3e7dc241...` slot 0, `083de199...` slot 1, `9231fe1e...` slot 2,
  `e5a2abea...` timestamps, `a143fa3b...` ini, all matching the backup).
- Scratchpad: `bak1001/`, `v1001-*.log`, `rubble-session-1001.log`,
  `rubble_reach.py`, `d.py`, `diag.py`, `film1/`, `film2/`, loose `s*.png`.
- No source edited, nothing committed, the merge left in progress, `TODO.md`
  not edited. Session stopped.
