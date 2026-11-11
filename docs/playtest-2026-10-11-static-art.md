# Static art verification: special root 869, Shield halves 870, Passage Test plant 871 (2026-10-11)

**Build under test.** main `cacb4c6` (the merge `b8cdb81` of `b3afce6`; contracts 10, 12 and 13 in `docs/art-track.md`). The game copy is `/tmp/claude-1000/vstatic/game`, a copy of `shared/u8-lv-patched`. All five artifacts match `shared/build/ARTIFACTS.sha256`:

| File | sha256 |
|---|---|
| EUSECODE | `9bf65241…`. The log reads `usecode/eusecode.flx: d00d0d59…, 1526688 bytes`, and the game was identified |
| U8SHAPES | `acd25608…` |
| TYPEFLAG | `b02e135c…` |
| ANIM | `c2e27898…` |
| FIXED | `177ac59a…`, in the root and in `STATIC/` |

**Binary and display.**
- The binary is `scummvm-lv/scummvm` (2026-10-11 17:51). Main pinned it mid-session as `/tmp/claude-1000/pinned-bin/scummvm-9bf65241`, and `cmp` shows the two files are byte-identical.
- Xvfb `:94` ran with the fix10 ini: 320×200, no width/height keys, `frameLimit=true`, `usehighres=false`, `SDL_AUDIODRIVER=dummy`.
- The driver is `vstatic/py/vf.py`, which is fix10's driver with `PRIME = False`: there is no left click before a right hold.

**Cheats.** Cheats were on only for teleports. Every talk, look, drag, egg walk and ceremony ran with cheats off, and each toggle was confirmed by the echoed `Cheats = …`. The combat flag 0x800 was never set: `objectInfo 1` read flags `0`, `400` or `408` throughout.

**Fresh map loads.** Every claim was judged on a map loaded after a hop: a teleport to Map 18 or 17 and back, or a walk through trigger 210. Each load was confirmed by its `Loading Fixed items in map N` line. Before any hop, the old saves showed `findShape 869` = 0 and `findShape 870` = 0, and cp10's Map 10 still held the q10 plant as shape **126** (item 6504). That confirms the traps.md rule.

**Plates.** Each new item has a `-2x` plate (the 640×400 window) and a `-1x` plate (the same frame nearest-downscaled to 320×200, the native pixels). There is also a `zoom4x` crop. They are in `docs/playtest-2026-10-11-static-art/`.

## Verdicts

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| R1 | Root 869 is drawn by the east stone; look gives "special root"; it is carryable; Ezrekal offers "I have found the root." and consumes it; the elixir chain continues; a carried 399 frame 9 does not trigger it | **PASS** | After the hop, `findShape 869` showed item 3494 at **(21376,16640,0)**, frame 0, `TYPESPEC`. It is drawn opaque, south of the east stone (`R1-root-869-east-stone-1x/2x`, `-zoom4x`). **Look:** event 0 @ `0365:0080` barks **"special root"** (`R1-look-special-root`). **Carry:** the drag logged `Dragging item 3494` → `Dropped item in backpack`, and the weight went 30 → 40. **Ezrekal:** the menu read **"I have found the root. / Can you help me? / bye"** (`R1-menu-I-have-found-the-root`). The pick gave "Ah, good that is. Take it I will and brew the tea I will." Afterwards `findShape 869` = 0, the 399 frame 9 was still in the pack, givenRoot 1063 = 1 and justGotRoot 1064 = 1. **Elixir chain:** "Is Tyorvi's elixir ready yet?" gave "Not so quickly…" (`R1-ready-yet-reply`). After a leave-and-return (justGotRoot 0), the menu offered "Have you made the elixir?", which gave "Yes, I have. Take it to him now you can." That produced **item 17857, shape 868 `TYPEELIX`** in the pack, with 1827 = 1 and 1062 = 1 (`R1-elixir-given`). **Negative control:** with only the old **399 frame 9** (item 12208, `ETHEREAG`) in the pack and tyorviDreams 1, the menu was "Can you help me? / I would speak to you of Tyorvi. / bye", with no root option (`R1-neg-menu-399f9-in-pack`) |
| H1 | Both halves are drawn as distinct jagged halves at their spots; look gives "broken shield"; both are carryable; the ceremony takes both and gives Shield 828 q83 | **PASS** | After the hop, `findShape 870` showed item 24966, **frame 0, q81, n236, at (6208,1568,0)**, and item 24964, **frame 1, q82, n236, at (7232,1568,0)**. Both are `et: 0`, so they are not equip items. **Drawing:** the left half is a blue-rimmed crescent with a jagged right edge, and the right half carries the red emblem with a jagged left edge. Each lies over a bone pile (`H1-left-half-870f0-*`, `H1-right-half-870f1-*`, `H1-both-halves-overview-*`). **Look:** both run event 0 @ `04EC:0080` and bark **"broken shield"** (`H1-look-left-half`, `H1-look-right-half`). **Carry:** both drags logged `Dropped item in backpack`, and the weight went 110 → 140 → 170. **Ceremony:** I walked N into EggShades with cheats off. Picks: "Let's be reasonable!" → "Yes, Priestess." → (fusion, `H1-ceremony-fusion-film-sheet-1s`) → "Please, High Priestess." Result: **item 26724, shape 828 `AORTA`, q 83** in the pack, `findShape 870` = 0, shieldFixed 1033 = 1, avatarPoisoned 1028 = 1 → 0, and inShadeScene back to 0 when the scene ended. The plates are `H1-ceremony-halves-in-scene` and `H1-ceremony-take-up-shield`. **Negative control:** with only the old **539** halves in the pack (s13d before the hop), the same walk hatched EggShades (`event 7 @ 05A5`), but the elders only quarrelled. No menu came, and shieldFixed stayed 0 (`H1-neg-old-539-halves-ceremony-bails`). See finding 1 |
| P1 | Plant 871 is drawn on the plateau at (12800,29408,64); look gives "Strange plant"; the Test works end to end; after a hop with haveMark, EggReapply removes the q10 plant | **PASS** | After the hop, `findShape 871` showed item 9047 at **(12800,29408,64), q10**, `TYPETEST`, and `findShape 126` on Map 10 = 0. It is drawn as a spined yellow-green bulb on the plateau (`P1-test-plant-871-plateau-1x/2x`, `-zoom4x`). **Look:** event 0 @ `0367:0080` barks **"Strange plant"** (`P1-look-strange-plant`). **Negative control:** a double-click on the plant ran no usecode, haveMark stayed 0, and the stone stayed in the pack. The 1994 TypePoisonPlant `use()` is not reachable from the item. **Test** (cp10-passage-stone): a 1.2 s walk S from (12876,29180,64) hatched EggPlantTest (`event 7 @ 059A`). In order: the plant vanished, the Avatar fell, the screen faded, and Thordis appeared (`event 15 @ 046A`). Then a whirlwind (`P1-scene-whirlwind-1`), the first new plant (`P1-scene-first-plant-pop`), and five plants in all (`P1-scene-five-plants-after`, `P1-scene-film-sheet-1s`). Afterwards `findShape 871` = **5**, all frame 0 and q0, at exactly PLNTST's five pop points. haveMark 1041 = 1, avatarPoisoned 1028 = 1, firstPoisoned 1034 = 1, plantScene 1049 = 1, the stone was consumed, and the Avatar stood at (13055,30079,64) with hp 30. **Hop:** teleport to Map 18, then a **walk** N into trigger 210, giving `Loading Fixed items in map 10`. Two shape-73 eggs hatched on pad 210, one of them EggReapply (`event 7 @ 05AA`). `findShape 871` then read **5, all q0**: the q10 record that FIXED had just re-read was gone (`P1-five-plants-after-hop-no-q10-1x/2x`). **Gating control:** the hop before the Test (haveMark 0) left the q10 plant standing, as shown above |
| P2 | Ordinary vegetation elsewhere is unchanged (Maps 8/39 126 tiles) | **PASS** | **Statically:** FIXED `177ac59a` against the base `FIXED.DAT.bak` has byte-identical shape-126 records on every map that has them: Map 4 (6), 7 (16), 8 (5), 39 (27) and 222 (4). The shape bytes of 126, 399, 539 and 828 (md5) and their TYPEFLAG rows are identical to retail. **In-engine:** Map 8 `findShape 126` = 21 and Map 39 = 40, all `class Item` with no `TYPETEST` uc, and they are drawn as before (`P2-map8-126-tiles-*`, `P2-map39-126-tiles-*`). Map 10 no longer has any shape 126 |
| L | Log hygiene, especially "Cycle in paint" near the new items | **PASS** | `vstatic/lv_run.log`, 14 map loads: **0 `Cycle in paint`**. Part 6 logged 8 × `35 -> 539 -> … -> 35` with the old halves on their bone piles; the 870 halves lie on the same bones and produced none. The log also has 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Trying to access segment`, ERROR, `Invalid item`, `Unhandled intrinsic`, `Invalid procid` and `Skipping invalid shape`. WARNINGs are the stock ones plus one `popToContainer to invalid container (64)` / `Destroying orphaned ethereal object` (shape 174). That one came on the s13d → Map 10 teleport, not near the new items: item 64 is shape 574's process, and shape 174 is unrelated [INFERENCE: a save-state artefact; not traced] |
| Checks | Test estate; hashes; shape IDs; fork | **PASS**; `build_artifacts.sh` not run | `tools/run_all_tests.sh`: **48/48 PASS** (`test_uc_dialogue` 462/462, `test_uc_plntst` 20/20, `test_uc_reentry` 53/53, `test_uc_shades` 58/58, `test_scummvm_patch_sync` 3/3). The game copy hashes are canonical. **Shape IDs:** TYPE_SHAPES TypeWeedz 869, TypeAOFrizbee 870, TypeShortmushroom 871 and TypePoisonPlant 871 equal `SHAPE_SPECIAL_ROOT`, `SHAPE_SHIELD_HALVES` and `SHAPE_TEST_PLANT`. The manifest pins TYPESPECIALROOT 869 and TYPETESTPLANT 871, and FIXED has exactly 869 ×1 and 871 ×1 on Map 10 and 870 ×2 (frames 0/1, q81/82, npcnum 236) on Map 17. **Not run:** `tools/build_artifacts.sh`, because the assignment forbids build scripts. The fork is untouched |

**Not exercised:** the P1 run from `run1010-s07-m10-ragnar-told-stone.sav`, which first needs the island stone fetched; cp10-passage-stone already carries it. The H1 run from `run-s13-shield-halves.sav`; s13d was used.

## Findings outside the brief

1. **Old saves that already hold the halves cannot finish the ceremony.**
   - **What happens.** A save taken after the pickup, such as `run1010-s13d`, `run1010-s13e` or `cp22-shield-halves` [INFERENCE for the last two: same state per their names], carries both halves as shape **539**. SHADES now searches for 870, so the scene stops after the elders' quarrel. That is the known `ret` at 0x1A1, with no menu and shieldFixed 0 (`H1-neg-old-539-halves-ceremony-bails`).
   - **The way round.** Go back to Map 17 and collect the two 870s, which the FIXED re-read respawns. After the ceremony the two dead 539s stay in the pack (finding 3 has the plate). Weight went 110 → 170, and after the ceremony 140.
   - **Who is affected.** Only saves made before this build, between the pickup and the ceremony. The banked checkpoints from that stretch need the detour.
2. **The root and the halves respawn at every map entry, after they have been used.**
   - **The root.** After the hand-in and a hop, `findShape 869` showed a new root (item 15082) at the east stone.
   - **What a second root does.** I carried it to Ezrekal. The menu offered no root option ("Can you help me? / Have you made the elixir? / bye", `R1-edge-second-root-menu`). "Have you made the elixir?" answered "Yes, and gave it to you already I did…" with no second vial (`R1-edge-second-elixir-refused`; `findShape 868` still showed 1). So there is no dupe. The player is left carrying a useless root.
   - **The halves.** They respawn on Map 17 the same way. I did not try a second ceremony.
   - **Cause.** This is the FIXED re-read that `lv-new/REAPPLY.UNK`'s header describes. It is older than this change: 399 and 539 were FIXED records too [INFERENCE: not retested on the old build]. REAPPLY covers the q10 plant, but nothing covers the root or the halves.
3. **The old 539 halves keep their equip type in the pack** (`et: 1`), while the 870s are `et: 0`. A player holding stale 539 halves could still equip one as a shield. This is harmless, and only matters for finding 1's saves (`H1-pack-870-halves-and-old-539-*`).
4. **The five new Test plants are solid 96×96×32 boxes** (TYPEFLAG `0300304310010100`, SI_FIXED|SI_SOLID). They stand in a cluster west and south of Thordis's spot. A 6 s walk N from the Avatar's wake-up point (13055,30079) reached (13055,28079), so they block neither the wake-up spot nor the ramp lane. I did not probe walking through the cluster itself.

## Harness anomalies

- **First Ezrekal double-clicks missed.** The first two double-clicks at a projected point logged nothing. The standstill-strike that reads `objectInfo 116` hit on try 0-4 every time.
- **A drag grabbed the bone pile.** The first drag on the left half picked up the bone pile under it, item 25373, shape 35, and dropped it back. The second drag, 18 px higher, took the half. The halves still overlap their bones on screen. This is the old traps.md note, now about bones (35) rather than the skeleton.
- **`dbg.sh` was not used.** The overlay console was driven by the chord, as in fix10.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-static-art/` (44 plates).
- **Scratch** `/tmp/claude-1000/vstatic/` holds:
  - `game/`, the copy of `shared/u8-lv-patched` at the hashes above;
  - `scummvm.ini`;
  - `saves/`, with slot 1 overwritten by the loads;
  - `lv_run.log`, `trace.txt`, `estate.log` and `py/vf.py`;
  - `sp/`, the working screenshots.
- **Banked nothing** in `~/lv-checkpoints`.
- **Stopped** my ScummVM (pid 858191). I left Xvfb `:94` (pid 3880104) running: it predates this session (started 2026-10-10 23:59), so I did not start it.
- **No edits** to source, maps, the fork, `TODO.md` or `HANDOFF.md`. No install or build runs.
