# Verifier pass 2: `integrate/vignettes2` (2026-10-17)

The branch was HEAD c9958a5. The only uncommitted edits were to docs: `.claude/rules/build-artifacts.md` and `TODO.md`. `CLAUDE.md` and `.claude/settings.json` had user edits, which I ignored.

I deleted all five `shared/build/` artifacts first, then rebuilt them from source with `tools/integrate.sh`. For the baseline, I rebuilt main's b76099f in a throwaway worktree (`/tmp/vv2/main-wt`, since removed). That build reproduced main's recorded hashes exactly (FIXED 64f0e85a…, U8SHAPES f151f945…, TYPEFLAG 33e15c95…, EUSECODE 2048fc6e…, ANIM 696dbeb9…).

ScummVM ran from `scummvm-lv-console/scummvm`, the text-console build of 07:00. It postdates fork tip e48f8716, and its detection entry carries EUSECODE 1528485 bytes. The game dir was `shared/u8-lv-patched`, which integrate had just verified as canonical.

## Verdicts

| # | Claim | Verdict |
|---|---|---|
| 1a | integrate reproducible; estate 52/52 | **PASS** |
| 1b | EUSECODE failures are exactly the DEV_ALLOWLIST pair | **PASS** |
| 1c | SACSHLD pinned the documented way; no pin renumbered | **PASS** |
| 1d | An old save holding 828 q83 still completes the altar | **PASS** (usecode sim + code reading); **NOT DEMONSTRATED** in-engine |
| 2 | Sacred Circle → altar, end to end, with gods 860 and Shield 879 | **PARTIAL**. SHADES → Shield 879 PASSED in-engine. Walk to the sanctum, crack, altar, camera, shatter and ending: **NOT DEMONSTRATED** |
| 3a | Walk the climb base → summit → trigger 209 and back | **PASS**, with two warps, both explained |
| 3b | No bounce: 8 headings × walk/run, 8 s, from pad 208 and pad 209 | **PASS**: 64 holds, 0 bounces |
| 3c | screen01 window has no black holes in-engine | **NOT DEMONSTRATED** |
| 3d | No `Cycle in paint` lines on Map 13 | **FAIL**: 4 lines (`1 -> 125 -> ... -> 1`) |
| 4 | 861/862/870 retired: empty in U8SHAPES, on no map, referenced nowhere | **PASS** |
| 5 | FIXED.DAT differs from main only on maps 13 and 18 | **PASS** |
| 6 | SCORES.md reproduces for screen04, screen13, screen01 | **NOT DEMONSTRATED** |
| — | Fork patch equals the fork diff | **PASS** (integrate step 1: 26 files) |

## 1. Build, estate, pins, save compatibility

**1a (PASS).** `tools/integrate.sh` ran in verify mode, starting with the five artifacts deleted. Log: `/tmp/vv2/integrate1.log`, step logs in `/tmp/lv-integrate.axWJHr/`. The steps reported:

- `build rebuilt; all 5 match ARTIFACTS.sha256`
- `pins unchanged`
- `patch equals the fork diff (26 files)`
- install and harness canonical
- `estate PASS — 52/52`
- `RESULT: PASS`

The rebuilt hashes equal the committed `ARTIFACTS.sha256`: FIXED 1482caca…, U8SHAPES 7676b65f…, TYPEFLAG ad64d96d…, EUSECODE 51c23f56…, ANIM 696dbeb9…. The `--record` result therefore reproduces from source.

**1b (PASS).** The Compilation Report shows 57 compiled, 55 succeeded and 2 failed. The two failures are `EALOGO.UNK: Line 14:4: Unterminated block comment` and `TJORVI.UNK: Line 575:11: Unterminated string literal`. AOSCENE, SACSHLD and TEMPLENT have no warnings.

**1c (PASS).**
- `lv_manifest.json` against b76099f: the one change is `classes/TYPESACREDSHIELD: None -> 879`. No other key or value changed, and `next_free` is unchanged.
- The build log shows `TypeSacredShield (ID 0x036F): 214 bytes` and `PIN 0x036F TYPESACREDSHIELD`. This is the same class = shape pattern as TYPEELIXIR 868, TYPEMESSAGESCROLL 864 and TYPEWATERZOMBIE 872.
- Retail EUSECODE slot 881 (class 879) is empty, so no retail class was displaced.
- Diffing EUSECODE against main's build, only five entries change: entry 1, class 0x36F (SACSHLD), 0x5A5 (EGGSHADES), 0x5A7 (EGGAOCEREMONY) and 0x5B0 (EGGTEMPLEENTRY). ATLI and AORTA are byte-identical; only their comments changed.
- `TYPE_SHAPES['TypeSacredShield']` is 879, which equals `lv_shapes.SHAPE_SACRED_SHIELD_1994`. build_map_18 uses the constant.

**1d (PASS by sim and code; not in-engine).**
- `AOSCENE.UNK` accepts the new Shield with `TypeSacredShield` q83. When none is found, it falls back to `TypeAOArtifact` (828) at q83, and pops whichever it found to (3111,8167,16).
- `test_uc_eggs` P5b/P7b and `test_uc_shades` P8/P7 pass in the estate:
  - a legacy 828 q83 sets godsFree, pops onto the altar top, and AORTA still names it;
  - Pagan's 828 q0 is refused and stays in the pack.
- The in-engine legacy runs were planned but not reached before the session budget ran out. Those were: `replay1011-s16b` (Map 10, 828 q83, Tiny Tars) → Map 18; and `replay1011-s17c` (saved on Map 18).

## 2. The ceremony chain (PARTIAL)

How I reached the start: I loaded `~/lv-checkpoints/replay1011-s13b-m17-cloud-city-arrival.sav` (copied over slot 1, since restored). I left Map 17 and came back so the new FIXED.DAT loaded. Then I took both 878 halves with `Item::grab 9766` / `Item::grab 30123`. Pack weight went 30 → 90.

**Walked from Map 17 to Map 10.** The Map 17 → 13 hop was trigger 208 (§3). I walked down the climb to trigger 206 and logged `Loading Fixed items in map 10`.

**SHADES (PASS).**
1. I warped to (20312,17744) on Map 10, which is outside the egg box (egg 19759 q294 at (20480,17152), hatch box ±256).
2. Before the ceremony: `shieldFixed [0409]=0`, `avatarPoisoned [0404]=1`. I turned cheats off ("Cheats = false").
3. A 1.6 s walk N logged `Item: 19759 (shape 73) calling usecode event 7 @ 05A5:0080` (`B1`, `B2`).
4. I picked each menu option from the screen:
   - "Let's be reasonable!" (`B3`)
   - "Yes, Priestess." (`B4`); the halves went down (`B5`)
   - the reforge (`B6`, `B6b`)
   - "Please, High Priestess." (`B7`, `B7b`; the Shield's sun and eye emblems are visible beside Ezrekal)
5. While it lay on the ground, `findShape 879` returned item 25516 `shape 879 (uc: TYPESACR) … q: 83` at (20500,17424,0). After "I take up the Shield…" the same item was contained (`f: 0xc`, in the pack).
6. Final state (`B8`): `shieldFixed=1`, `avatarPoisoned=0`, `findShape 878: 0 found`, weight 60. `inShadeScene` still read 1 at the first read; this is the known lag, 2026-10-11 leg-5 finding 3.

**NOT DEMONSTRATED:** the Map 10 → Map 18 walk, the crack, the altar placement, the camera visiting the three gods at their new spots, the shatter at the new scale, and the ending.

- I had taken two Tiny Tars from Hrodny's chest with `Item::grab 19139/25802`.
- `exact_reach` gives the route from the Circle to trigger 211: `20479,17295 → 19775,17295 → 19775,21823 → 19519,21823 → 19519,23615 → 18847,23615`.
- The run stopped there on the request budget. The in-game save of this state failed: `saveGame 98` wrote nothing, probably because the scene still held the Avatar.
- The static evidence still passes: `test_god_animation` 48/48, `test_sanctum_clearance`, `test_crack_geometry` 10/10, the AOSCENE sim camera checks, and `test_route_reach` "Ancient Temple, shrunken". That is not an in-engine demonstration.

## 3. Map 13

**3a Walk (PASS).** The base, the climb and both triggers were all walked, with two warps:

1. I warped onto pad 207 at (4096,11776,0).
2. I walked N along x≈4200 from z 0 to 60, E to (5000,8000,68), then N along x 4927–4960 (`A1`–`A3`).
3. **Warp 1.** Harpies killed the Avatar at (4928,4348,88), with hp 0 read via `objectInfo`. I reloaded, warped back to (4940,4644,84), a point I had already walked through, and then:
   - turned invincibility on (`Cheat::toggleInvincibility`);
   - moved harpies 124–127 off with `Actor::hold`.
4. I walked on N to (4960,1832,120), then W along the summit (`A4`, `A5`). Walking S, the log showed `Loading Fixed items in map 17` and the Avatar arrived at pad 209 (4608,9984,0).
5. **Back.**
   - **Warp 2.** From pad 209 my driver could not get S past the 875 drum pair at x 5791–5823 and 5919–5951, y 10591–10623. The gap is 96 units, and only x ∈ (5887,5919] passes a 64-unit body. Map 17 is unchanged from main, so I warped to (5007,10815) and walked S into trigger 208. The log showed `Loading Fixed items in map 13`.
   - I walked the whole descent from pad 208: 4927 → 2400 … 7707 (z 120 → 68), W to 4175, then S along x 3935 from z 64 down to 0 at (3735,10895) (`A6`). Walking SW, the log showed `Loading Fixed items in map 10` and the Avatar arrived at (7104,23360,8).

**3b Bounce (PASS).** From each pad I warped onto the pad, which gives the same `justTeleported` state as an arrival, and held a heading for 8 s. That covered 8 headings × 4 modes per pad:

- mouse walk: offset 100 px;
- mouse run: offset 250 px, or 185 px for the screen-vertical headings so the pointer stays on the 400-px surface;
- keyboard walk and keyboard run: facing set by a 0.25 s mouse tap, then `Up` or `Shift+Up` held.

Results:

- **Map 17 pad 209:** 32 holds, no `Loading … map 13`, never left Map 17.
- **Map 13 pad 208:** 32 holds, no `Loading … map 17`.
  - The keyboard NE hold, which used to loop, now ends in the CLIMB_STUB dead end at (4931,1371) walking and (5199,1343) running.
  - Mouse NE ends at (6127,1095).

Negative control: the same pads with a purposeful walk do reach the triggers (3a).

**3c (NOT DEMONSTRATED).** I did not frame screen01's window in-engine. I saw black holes elsewhere on the climb, but those are not in the claimed window (finding 2).

**3d Paint cycles (FAIL).** The session log has 4 lines on Map 13, at log lines 18653, 18697, 18738 and 18852:

```
Cycle in paint dependency graph 1 -> 125 -> ... -> 1
```

- All four fall inside one hold: the mouse run S from pad 208, (5119,2303,120) → (5119,7911,68), which runs down the north leg's lane at x≈5119.
- 1 is the Avatar and 125 is the crest shape.
- The two cycles the brief names are gone: 26→564 (212k lines last pass) and 125→66 (42k).
- Every other hold and walk produced no cycle line.
- The likely cause [INFERENCE] is a dynamic Avatar ↔ crest knot that `test_paint_cycles` does not cover, because it models static items. I did not repeat the run to locate it more precisely.

## 4. Retired 861/862/870 (PASS)

- **U8SHAPES.FLX:** entries 861, 862 and 870 have size 0, as in the base. Entries 879 and 881 are built.
- **TYPEFLAG:** the rows for 861, 862 and 870 are the base filler `1200100110010100`.
- **Maps:** a scan of all 256 FIXED.DAT maps, raw and glob-expanded, found no item of 861, 862 or 870.
- **Classes and types:** EUSECODE has no class at those ids, no `TYPE_SHAPES` value resolves to one, and no manifest class is pinned at one. Main's `TYPE_SHAPES` had none either.
- **Remaining references** are comments, docs and `vignettes/*.json` `"replaces"` metadata. No code reads `replaces`.
- **Negative control, in-engine.** The 10-11 save `replay1011-s13b` still carries retired 861 on Map 17 as item 20948 at (4095,7167,16) q90. It loads without a crash, the obelisk draws as nothing on its dais (`D1`), and the log shows no error.

## 5. FIXED.DAT regression (PASS)

I compared FIXED.DAT across all 256 slots, as multisets of (x, y, z, shape, frame, flags, quality, npcnum, mapnum), main b76099f build against branch build:

- **map 13:** 5578 → 6412 items (742 removed, 1576 added)
- **map 18:** 1424 → 1737 items (595 removed, 908 added)

Every other map is identical, Map 17 included, even though `build_map_17.py` changed (its output is the same).

Other artifacts against main:

- **U8SHAPES:** only 860, 861, 862, 870 and 881 differ.
- **TYPEFLAG:** only rows 860, 861, 862, 870 and 881 differ. 860 goes `0300608605060001` → `0300207205060001`, the (2,2,7) footpad.

## 6. In-engine scores (NOT DEMONSTRATED)

I did not rerun `vignette_capture.py`, for lack of request budget. The published screen04 replay class of 99.91 matches the brief's 99.914.

## Findings outside the brief

1. **Saves from before 2026-10-17 that hold the halves cannot run the ceremony.** SHADES searches the pack for `TypeAOFrizbee` (878). A save holding the halves as 539 (the 10-11 replay saves, e.g. `replay1011-s13c`/`s13e`) or 870 (10-11..10-17) fails that search and bails at Ezrekal's "Bring the sacred shield" branch. 870 halves are now also invisible, because the shape was retired.
   - This predates the branch: main already used 878. The branch adds save compatibility for the Shield and none for the halves.
   - A save made on Map 17 before pickup is fine, because re-entering the map reloads the fixed items.
2. **Black voids still render on the mid-climb faces.** I saw them around (4600–5000, 4300–8000) (`A3`), and the previous pass reported the same as its finding 3. They are outside the claimed screen01 window, and no score covers them.
3. **An old save taken on Map 18 keeps the old sanctum** [INFERENCE from the save format, trap 2026-10-10]. The save carries the old gods, altar (3072,8192,24) and egg. The new AOSCENE would pop the Shield at (3111,8167,16), off the old altar footprint, and pan the camera to the new god spots, where the old gods are not. This is self-healing once the player leaves the map; `replay1011-s17c` is the case to test.
4. **A stale comment:** `lv-patched/SHADES.UNK:504-505` still says "AOSCENE.UNK searches the pack for TypeAOArtifact".
5. **A tight aperture on Map 17's route from pad 209 to trigger 208.** The 875 drums at (5823,10623) and (5951,10623) leave a 96-unit gap, and only a 32-unit band of x lets a 64-unit body through. My mouse driver could not thread it. This is unchanged from main, but the brief's route goes through it, and it is worth an `exact_reach` body-72 check.
6. **Harpies killed a walking Avatar on the climb** (hp 30 → 0 within one leg) at (4928,4348,88). This is monster balance, not geometry, and it is not from this branch.

## Harness anomalies

- **`Cheat::heal` closes the console** without a prompt, like `teleport`. A wrapper that expects a reply desyncs.
- **The mouse offset must stay on the 640×400 surface.** Mouse-run holds at 250 px straight down or up put the pointer off the surface, and the Avatar did not move. Use ≤185 px for the SE and NW world headings.
- **Mouse walk bursts shorter than about 0.8 s at offset ≤105 px do not move the Avatar.** The turn and the animation start eat them.
- **`Ultima8Engine::saveGame 98` wrote nothing** right after the SHADES scene.
- **Intermittent image reads.** The read tool sometimes reported a just-written `/tmp` PNG as not found, and found it on retry.

## Disk changes

- **Written:** this report and `docs/playtest-2026-10-17-vignettes-verify2/` (18 PNGs).
- **Regenerated by `tools/integrate.sh`, identical content:** the `shared/build/` artifacts (I deleted them first), `scummvm-lv` (make, nothing relinked), `shared/data/u8-install` and `shared/u8-lv-patched`.
- **Restored:** `~/.local/share/scummvm/saves/ultima8.001` (cmp-verified against the backup) and `~/.config/scummvm/scummvm.ini` (from the backup).
- **Temporary:** the worktree `/tmp/vv2/main-wt` was removed. Scratch scripts and logs remain in `/tmp/vv2/` (`pathfind_er.py`, `fixdiff.py`, `artdiff.py`, montages).
- **Not touched:** any source, builder, map, the fork, or TODO.md. The session is stopped.
