# Hrodny's chest gets a TRAP lock; FIXED.DAT `6dc98430…` (2026-10-08)

This report tests a fix for finding 1 of `docs/playtest-2026-10-08-intrinsics.md`.
**The change:**
- `build_map_10.py` puts a contained TRAP right after Hrodny's locked chest. The TRAP is shape 756, with quality `0x100 | 20` = 276.
- `lv_shapes.py` gains `SHAPE_TRAP = 756`.
- FIXED.DAT is rehashed to `6dc98430…`, and `map_pins.json` is regenerated.
- A new test, `test_chest_locks.py`, is added.
- Fork commit `ed924d30` carries comment-only corrections.

**Session:**
- The binary is `scummvm-lv/scummvm`, built 2026-10-08 10:16:18, four seconds after the commit.
- The log reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `usecode/eusecode.flx: e1fed4c8…, 1524731 bytes`.
- One pid ran the whole session.
- The plates are in `docs/playtest-2026-10-08-chest-lock/`, at 640x400.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| L1 | Tracked patch equals the fork diff at `ed924d30`; `scummvm-lv/` carries the changed files; binary postdates the commit | **PASS** |
| L2 | `run_all_tests.sh` passes (42 files, including `test_chest_locks.py`); full `build_artifacts.sh` reproduces all 4 hashes | **PASS**. 42/42 test files pass. All 4 hashes are OK, with FIXED at `6dc98430…`. The Compilation Report is 46/48, and its 2 failures are exactly `EALOGO.UNK` and `TJORVI.UNK`. Run against the old FIXED (`c3d29a1f`), the new test **fails**, as it should |
| L3 | On a fresh Map 10, the chest is shape 618 with TRAP 756 q 0x114 inside; a double-click barks "locked chest" and opens no gump | **PASS** |
| L4 | Negative controls: the key blank / quality-0 key and the Cliff Key are refused, and the chest stays 618 | **PASS**. The q0 key 4782 was refused. The Cliff Key *is* a q0 shape-82 key (below), so this one result covers both. As an extra control, a Pagan q99 key was refused too |
| L5 | The q20 key turns 618 into 78. The next double-click opens the gump with no explosion, no "Ouch", and no FIRESPEL | **PASS**. TRAP `use()` fires (`02F4:0080`) and does nothing. hp stays 30. **The TRAP is not drawn in the chest gump**, and a click on its slot hits nothing |
| L6 | The three Tiny Tar potions can be taken | **PASS**. All 3 were dragged out by mouse. Weight went 270 → 300. The chest ends with `vol: 0/200, items: 1`, and that one item is the TRAP |
| L7 | Log hygiene | 2,201 lines: **4** `Unhandled intrinsic`, all 254, one per chest `use()` (1 locked, 3 plain). **0** `Non-existent process`, **0** `stuck in process loop`, **0** Segmentation, **0** Assertion. 0 `0583`/FIRESPEL and 0 `Ouch` |

## Method

- **Isolation.**
  - Display `:79` at 1770x1072. The window sat at (725, 436).
  - The game copy was `/tmp/claude-1000/vcl/game`: an rsync of `shared/data/u8-install`, the copy `./install_lv.sh` had just written (rc 0), minus the `.bak` files.
  - I `sha256sum`-checked all four artifacts in that copy against `shared/build`. FIXED was `6dc98430…`, TYPEFLAG `9f534e59`, U8SHAPES `a611e9be` and EUSECODE `1ca0e93b`. The copy has no top-level `FIXED.DAT`.
  - Config was `vcl/scummvm.ini` (`usehighres=true`). Saves were in `vcl/saves/`. Audio was `SDL_AUDIODRIVER=dummy`.
  - Command: `scummvm --config … --savepath … --extrapath scummvm-lv/dists/engine-data --debuglevel=1 -p vcl/game -x 1 ultima8`.
- **Save.** `~/lv-checkpoints/cp26-chest-key.sav` (md5 `0f203c14…`) went into slot 1. It loads on Map 10 at (19568, 23180) carrying:
  - q0 keys 4713 and 4782;
  - q20 key 6161, inside Hrodny's bag 6159.
- **Fresh map.** I hopped to Map 18 and back, and the log reads `Loading Fixed items in map 10`. A second reload came later, after the Map 8 trip.
- **Game-state writes.**
  - Teleports with cheats on, each followed by a toggle back off.
  - `debugflag_enable Object`.
  - One `Item::grab 28964`, to fetch the Map 8 q99 key for the extra negative control.

  Every chest, key, bag and potion action was a mouse click or drag on the screen.

## L1: fork, PASS

```
$ git log --format='%h %ci %s' -3 lost-vale
ed924d30 2026-10-08 10:16:10 -0500 Correct the 0xFE and freeEquip comments after in-engine verification
f50c1d45 2026-10-08 09:28:15 -0500 Match retail U8 for intrinsics 0x43, 0x98 and 0xFE
$ git diff 01bd8879… HEAD -- engines/ ':!engines/ultima/detection_tables.h' | diff -q - ../tools/scummvm-patches/0001-lost-vale-engine.patch
(no output) → PATCH_EQUAL
```

- **What changed.** `git diff f50c1d45 ed924d30` touches only comments: `u8_intrinsics.h:340-347` and `actor.cpp:2776-2783`.
- **Build tree.** `cmp` finds all 22 patched files identical between the fork and `scummvm-lv/`.
- **Timestamps.**
  - `ultima8.o` 10:16:14.40 and `actor.o` 10:16:14.35, both rebuilt from the two changed files.
  - The binary at 10:16:18.72. The commit is at 10:16:10.
- **Test.** `test_scummvm_patch_sync.py` passed in the estate.

## L2: standard checks, PASS

- **Tests.** `tools/run_all_tests.sh` gave `OVERALL: PASS — 42/42 test file(s)`, including `test_chest_locks.py PASS 3 passed, 0 failed`.
- **Build.** `tools/build_artifacts.sh` returned rc 0 with `RESULT: PASS — all 4 artifacts match the canonical hashes`:
  - TYPEFLAG `9f534e59…`
  - U8SHAPES `a611e9be…`
  - EUSECODE `1ca0e93b…`
  - FIXED `6dc984305e89c3e84c23f70e71c4456da2e117cf05ce0c85addddcdeb33d7a21`

  These match `ARTIFACTS.sha256`. The build log reads `Final: 115472 items across 49 maps`.
- **Compilation Report.** 48 files: 46 compiled and 2 failed, `EALOGO.UNK` (unterminated block comment) and `TJORVI.UNK` (unterminated string).
- **Does the test bite?** I ran a scratch copy of `test_chest_locks.py` with `BUILT` pointed at the pre-change FIXED.DAT (`c3d29a1f…`, from the previous session's game copy). It exits 1:
  ```
  FAIL  map 10 chest at (21152, 8832, 0) contains a TRAP lock (shape 756, quality 0x1xx)  found 0; without one KEYRING opens it for any key
  ```
- **Records on disk.** `shared/build/FIXED.DAT`, Map 10, records 6426-6431:
  ```
  6426 shape 618 (21152, 8832, 0) q 20 flags 0
  6427 shape 756 x=1 y=-1 q 276 flags 0x8      <- the lock
  6428-6430 shape 859 frame 8 npcnum 229 x=1 flags 0x8  (Tiny Tar x3)
  6431 shape 82 (22016, 6144, 0) q 20          <- the pre-placed key
  ```
  Map 10 is the only map with a shape-756 record.
- **Retail comparison.** Lock TRAPs in retail NONFIXED carry flags `0x2008`, where `0x2000` is `FLG_FASTAREA` runtime state. Ours carries `0x8`, which is equivalent.

## L3: fresh chest, TRAP inside, locked bark, PASS

**What `findShape` showed after the hop:**
```
Item 8982 (class Container, shape 618) (uc: LCHST_EW), 0, (21152, 8832, 0) q: 20 … f: 0x2000 … Container vol: 3/200, total weight: 230, items: 4
Item 8983 (class Item, shape 756) (uc: TRAP), 0, (255, 255) q: 276, m: 0, n: 0, f: 0x8, ef: 0x9 shapeinfo f: 1002, fam: 1
Item 8984/8985/8986 (class Item, shape 859), 8, (255, 255) … n: 229, f: 0x8
findShape 756: 1 found
```

The chest has `items: 4`, which is three potions plus the TRAP. The TRAP takes volume 0. Its objid follows the chest's directly, and no other shape-756 item exists on the map.

**Look.** A single click logs `event 0 @ 026A:0080`, and the bark is "locked chest" (`L3-02-look-bark`).

**Use.** I double-clicked from (21048, 8864):

```
Item: 8982 (shape 618) calling usecode event 1 @ 026A:00B0
WARNING: Unhandled intrinsic 254 'isGameRunning()'? called!
```

- The bark "locked chest" shows at 0.3 s (`L3-04-use-bark`), and no gump appears (`L3-05-use-no-gump`).
- `objectInfo 8982` afterwards still reads `shape 618 … f: 0x2000`, frame 0.
- An earlier double-click from (21112, 9032), about 200 units away, logged the dump and no `use`. That was out of reach, not a defect.

## L4: negative controls, PASS

**The Cliff Key's quality.**
- `CLIFF_KEY_ID = 170` (`build_map_10.py:1338`) is the lock id of the Map 10 terrace *gate*, not the key's quality.
- The Key to the Clouds is created by `lv-patched/TYORVI.UNK:2165` as `give(Avatar:Referent,TypeCliffKey,0,0,1)`, and `TYPE_SHAPES['TypeCliffKey'] = 82`. So it is a shape-82, frame-0, **quality-0** key. `build_map_13.py:365-366` says the same.
- KEYRING tests only type 82 and quality (`004F:04AE-04DB`), so the Cliff Key and a key blank cannot be told apart.

**q0 key 4782 on chest 8982.**
- A single click logs `Item 4782 (shape 82) (uc: KEY) … q: 0` (`L4-02`).
- A double-click gave the target cursor (`L4-03`), and then I clicked the chest:

```
Item: 4782 (shape 82) calling usecode event 1 @ 0052:04BB
Target result: Item 8982 (class Container, shape 618) (uc: LCHST_EW) … q: 20 … items: 4
-- afterwards --
Item 8982 (class Container, shape 618) (uc: LCHST_EW) … f: 0x2000 … items: 4
findShape 618: 1 found
```

The chest stays closed and shape 618 (`L4-04-q0-4782-refused`). The previous session got `shape 78` here.

**Extra control: Pagan q99 key 28964.** This is the Map 8 key from `build_map_08`, `DOOR_LOCK_ID`. I fetched it with `Item::grab` and returned to a fresh Map 10, where the chest was now 1139 and its TRAP 2405 (`q: 276`).
- A single click identified `Item 28964 … q: 99` in the pack.
- I used it on the chest:

```
Item: 28964 (shape 82) calling usecode event 1 @ 0052:04BB
Target result: Item 1139 (class Container, shape 618) (uc: LCHST_EW) … q: 20 … items: 4
-- afterwards --
Item 1139 (class Container, shape 618) … findShape 618: 1 found
```

It was refused (`L4-06`, `L4-07`). A non-zero key with the wrong id cannot open the chest either.

**Not used.** I did not use key 4713, the second q0 key, on the chest. It sits under 4782 at the same pack slot (4, 7), and its type and quality are identical.

## L5: the q20 key, then an open with no explosion, PASS

**The key.** Bag 6159 opened (`L5-01`), and a single click gave `Item 6161 … KEY … q: 20`. I double-clicked it, then clicked chest 1139 (`L5-02`):

```
Item: 6161 (shape 82) calling usecode event 1 @ 0052:04BB
Target result: Item 1139 (class Container, shape 618) (uc: LCHST_EW) … items: 4
-- afterwards --
Item 1139 (class Container, shape 78) (uc: CHEST_EW), 0, (21152, 8832, 0) q: 20 … items: 4
findShape 618: 0 found
```

The chest is now 78 (`L5-03`). KEYRING swaps the shape in place, so the TRAP stays inside and `items` is still 4.

**The open.** Before it, the Avatar read hp 30. I double-clicked the chest:

```
Item: 1139 (shape 78) calling usecode event 1 @ 004E:00A9
WARNING: Unhandled intrinsic 254 'isGameRunning()'? called!
Item: 2405 (shape 756) calling usecode event 1 @ 02F4:0080
-- afterwards --
Item 1139 (class Container, shape 78) (uc: CHEST_EW), 4, (21152, 8832, 0) … f: 0x2100 … items: 4
Item 2405 (class Item, shape 756) (uc: TRAP), 0, (78, 19) q: 276 … f: 0x2008
Avatar: (21048, 8864, 0) hp 30
```

- **The TRAP fires and does nothing.** CHEST_EW's `isGameRunning` branch calls `use()` on the TRAP. TRAP `use()` (`02F4:0080-0100`) spawns FIRESPEL `0583:233D` and barks "Ouch!" only when `quality/256 == 0`. At 276/256 = 1 it jumps straight to `ret`.
- **Nothing else happened.**
  - The log after the click has no `0583` and no `Ouch`.
  - hp stayed 30.
  - The chest did not move.
  - The TRAP survived.
  - The gump opened: frame 4, `FLG_GUMP_OPEN` (`L5-05` at 0.3 s, `L5-04` at 3.6 s).
- **The TRAP is not drawn in the chest gump.** `L5-06-gump-zoom` shows only the three potions.
  - TYPEFLAG 756 has `data[5] & 0x10` set, which is `SI_EDITOR` (`type_flags.cpp:96`).
  - `ContainerGump` skips editor shapes both when painting and when hit-testing (`container_gump.cpp:171,214`).
  - A click on the TRAP's slot (gump (78, 19), window (368, 139)) logged nothing. The player cannot see, take or click it.
- **Close and reopen.** These are two more `use()` calls, and each again logged `02F4:0080` with no explosion (`L5-07`).

## L6: Tiny Tar taken, PASS

The three potions were 1350, 2009 and 5578 (frame 8, n 229). I dragged each one from the chest gump onto the Avatar:

```
Dragging item 1350 (class=Item) / Dropping object 1350 / Dropped item in backpack
Dragging item 2009 (class=Item) / Dropping object 2009 / Dropped item in backpack
Dragging item 5578 (class=Item) / Dropping object 5578 / Dropped item in backpack
```

**Afterwards:**
- Weight went 270 → 280 → 300.
- All three read `f: 0x200c` in the pack.
- The chest reads `vol: 0/200, total weight: 200, items: 1`, and that item is the TRAP (`L6-02-chest-emptied`).

## L7: log hygiene

| Pattern | Count | Note |
|---|---|---|
| `Unhandled intrinsic` | 4 | All are 254. They match 4 chest `use()` calls one for one: `026A:00B0` ×1 (locked), `004E:00A9` ×3 (open, close, reopen) |
| `Non-existent process` | 0 | |
| `stuck in process loop` | 0 | |
| Segmentation / Assertion | 0 / 0 | |
| TRAP `02F4:0080` | 3 | One per plain-chest `use()`. All were no-ops |
| `0583` (FIRESPEL) / `Ouch` | 0 / 0 | |
| `Cycle in paint dependency graph` | 1,187 | All `590 -> 235`, all on Map 8 at the debug landing (finding 3) |

## Findings

1. **The Map 10 pin pins the wrong item as the lock.** In `map_pins.json` (Map 10), the row for `shape 618 q 20` says "Hrodny's locked chest, lock id 20". It comes from `derive_map_pins.py:614-621`, which keys locks on the quality of shape 114/618.
   - KEYRING never reads the chest's quality. The lock is the TRAP, q 276, and no pin covers it.
   - `test_chest_locks.py` does guard it. But a renumbered `HRODNY_KEY_ID` that kept the chest at 20 and moved the TRAP would leave the pin "correct" and the lock wrong.
   - The derivation's wording should change and the TRAP be added. Low severity.
2. **The Z-d line in `docs/playtest-2026-09-02-quest-chain.md:780-781` is still uncorrected.** It reads "The Cliff Key (quality 0) targets the chest but does not unlock it, which is the lock ids working".
   - It was false when written: the chest had no TRAP, and the 10-08 session showed a q0 key opening it.
   - Today's diff adds a correction to Z-c (line 731) but not to Z-d.
   - As of this FIXED.DAT the observation is true, but its reason ("the lock ids") is not.
3. **Map 8 logs `Cycle in paint dependency graph 590 -> 235` about 1,187 times** while the Avatar stands at the install script's Bonecrusher-cave landing (20430, 3250, 0). This is a debug-level line and nothing was visibly wrong.
   - `TODO.md:360` lists Map 8 paint cycles only at Mythran's house (shapes 164/149), so this is a second Map 8 site.
   - It is outside this change: Map 8's records did not move.
4. **The KEYRING item path (shape 79) was not exercised.** No keyring is in the save. `004F:04DE-0529` loops over the keys in a keyring and uses the same `trap & 0xFF == key quality` test. NOT DEMONSTRATED.
5. **Hrodny's dialogue-spawned key was not exercised in-engine.** Statically it is `setQuality(20)` (`build_map_10.py:783-787`, which cites the FLX at 0x4802), so the new lock fits it.
6. **The relock-and-refill on map reload still happens, as reported on 10-04 and 10-08.** The second Map 10 entry produced a fresh locked chest 1139 with 3 potions and a TRAP. The player keeps the q20 key, so the refill can be farmed. That is unchanged by this fix and only noted.
7. **Carried over from the 10-08 intrinsics report:**
   - `scummvm-lv-console/scummvm` is still dated 2026-10-07 13:53, before both fork commits.
   - `.claude/agents/verifier.md:49` still says "Nothing else tests this" about the patch check. `CLAUDE.md` is corrected in this diff; `verifier.md` is not.

## Harness anomalies

- **Window position.** The game window came up at (725, 436), not the (565, 336) the previous driver assumed. I re-based the driver on `xdotool getwindowgeometry`.
- **Background launch.** A shell-backgrounded Xvfb died with the tool's shell, so I launched Xvfb and ScummVM from a persistent Python kernel with `start_new_session`.
- **Look bark timing.** The look bark was not on screen at 0.35 s on the first click. A 6-frame film caught it at 0.5-1.2 s.

## Disk changes

- **Wrote** this report and 22 plates in `docs/playtest-2026-10-08-chest-lock/` (L0-*, L3-*, L4-*, L5-*, L6-*).
- **Regenerated by the checks:**
  - `shared/build/*`, with all 4 hashes equal to `ARTIFACTS.sha256`;
  - `shared/data/u8-install/` via `install_lv.sh`, with its 4 artifacts `cmp`-equal to `shared/build`.

  The tracked diff (`git diff --stat`) is the same as before the run.
- **Scratch in `/tmp/claude-1000/vcl/`:**
  - the game copy and `saves/` (`ultima8.001` = cp26, plus engine-written history and timestamps);
  - `lv_run.log`, `tests.log`, `build.log` and `install.log`;
  - `keyring.dis` and `trap.dis`, cut from the previous session's full disassembly;
  - `test_chest_locks_oldfixed.py`, the scratch copy pointed at the old FIXED.DAT;
  - the driver in `py/` and frames in `sp/`.
- **Not touched:**
  - `shared/u8-lv-patched`;
  - `~/.config/scummvm/scummvm.ini` (md5 `af255300…`);
  - `~/lv-checkpoints` (read only);
  - any source, builder, map, fork, TODO or HANDOFF file.

  Nothing was committed. ScummVM and Xvfb `:79` are stopped.
