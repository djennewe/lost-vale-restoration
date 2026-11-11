# Fork f50c1d45: retail intrinsics 0x43, 0x98 and 0xFE (2026-10-08)

Change under test: `scummvm-lv-console` branch `lost-vale` commit `f50c1d45`
("Match retail U8 for intrinsics 0x43, 0x98 and 0xFE") on `10d59e56`. The
binary is `scummvm-lv/scummvm` (2026-10-08 09:28:45, 30 s after the commit).
The session log reads `usecode/eusecode.flx: e1fed4c8…, 1524731 bytes` and
`Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)`. Plates
are in `docs/playtest-2026-10-08-intrinsics/` at 640x400.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| C1 | Tracked patch equals the fork diff; `scummvm-lv/` carries the three files; binary postdates the commit | **PASS** |
| C2 | `run_all_tests.sh`; full `build_artifacts.sh`, hashes unchanged | **PASS**. 41/41 test files. 4/4 hashes OK. Compilation Report 46/48, and the 2 failures are exactly `EALOGO.UNK` and `TJORVI.UNK` |
| C3 | Hrodny's locked chest barks "locked chest" and opens no gump; 0 `Unhandled intrinsic 254` | **PARTIAL**. The behaviour passes: it barks and opens no gump, and `f` stays `0x2000` without `FLG_GUMP_OPEN`. The log part fails: there are **11** `Unhandled intrinsic 254` lines, one per chest `use()`. They are cosmetic (finding 3) |
| C4 | The q20 key turns 618 into 78 and the next double-click opens it; the q0 key does not unlock it | **FAIL**. The positive path passes. The negative control fails: **the quality-0 "key blank" also unlocks Hrodny's chest** (finding 1). The fork commit did not cause this |
| C5 | The chest's Tiny Tar can be taken | **PASS**. The chest holds 3 frame-8 potions (859). All 3 went to the pack, and the chest ended with 0 items. Weight went 260 → 290 |
| C6 | A plain chest opens on double-click | **PASS**. Retail CHEST_EW 20060 on Map 51 opened, and so did the unlocked Hrodny chest. One more result: a booby-trapped plain chest now explodes when opened (finding 2) |
| C7 | A Pagan locked chest barks and does not open | **PASS**. Map 41 LCHST_EW 31301 barked "locked chest" and opened no gump. Negative control: the q20 key is refused on it (its lock is key 30) |
| C8 | 0x43/0x98 cannot run in play today | **NOT DEMONSTRATED** in-engine, as expected. The static checks pass: nothing places an `EGGMAGNET` egg (281), no item is a frame-3 TypeAOFrizbee, and U8 never fires event 0x0A |
| C9 | Log hygiene | 2,974 lines: **11** `Unhandled intrinsic` (all 254, one per chest `use()`), **1** `Non-existent process` (when Map 41 loaded, before any chest), **0** `stuck in process loop`, **0** Segmentation, **0** Assertion. No line for intrinsic 67 or 152 |

## Method

- **Isolation.** I used display `:79` and the game copy `/tmp/claude-1000/vif/game`. That is `shared/u8-lv-patched` after `cmp` against all five `shared/build` destinations, all equal. Config was `vif/scummvm.ini` and saves were in `vif/saves/`, with `SDL_AUDIODRIVER=dummy`. The command line was `scummvm --config … --savepath … --debuglevel=1 -p vif/game -x 1 ultima8`. One pid ran the whole session.
- **Save.** `~/lv-checkpoints/cp26-chest-key.sav` (md5 `0f203c14…`) was copied to slot 1. It loads on Map 10 at (19568, 23180) carrying:
  - the q20 key 6161, inside Hrodny's bag 6159;
  - two q0 keys, 4713 and 4782.

  That save carries the *old* Map 10: the chest sits in the wall and is empty. I hopped to Map 18 and back, after which `findShape 618` showed chest 8982 at (21152, 8832, 0), `q: 20`, `items: 3`.
- **Game-state writes.**
  - Teleports with cheats on, each followed by a toggle back off.
  - `debugflag_enable Object`.
  - One `Item::grab 8984` (C5).

  Every chest and key action was a mouse click on the screen.
- `./install_lv.sh` ran first (rc 0). The four installed files `cmp`-equal `shared/build/`.

## C1: fork, PASS

```
$ cd scummvm-lv-console && git diff 01bd8879… HEAD -- engines/ ':!engines/ultima/detection_tables.h' | diff -q - ../tools/scummvm-patches/0001-lost-vale-engine.patch
(no output) → PATCH_EQUAL
```

- **Build tree.** `cmp` reports `u8_intrinsics.h`, `actor.h` and `actor.cpp` identical between the fork and `scummvm-lv/`. `diff -rq` of `engines/ultima` differs only in the generated `detection_tables.h` and in `libultima.a`.
- **Recompiled objects.** `ultima8.o` (the only includer of `u8_intrinsics.h`), `actor.o` and `uc_machine.o` are dated 09:28:32–36. The commit is 09:28:15 and the binary 09:28:45.
- **The binary.** `strings` finds `freeEquip` in it.

## C2: standard checks, PASS

- **Tests.** `tools/run_all_tests.sh` gave `OVERALL: PASS — 41/41`, including `test_scummvm_patch_sync.py PASS`.
- **Build.** `tools/build_artifacts.sh` returned rc 0 with `RESULT: PASS — all 4 artifacts match`. The hashes were TYPEFLAG `9f534e59`, U8SHAPES `a611e9be`, EUSECODE `1ca0e93b` and FIXED `c3d29a1f`, the same as before the build.
- **Compilation Report.** 48 files: 46 compiled and 2 failed, `EALOGO.UNK` and `TJORVI.UNK`.

## C3: locked chest barks, PARTIAL

**Look.** A single click on chest 8982 logs `event 0 @ 026A:0080`, and the bark is "locked chest" (`C3-01`).

**Use.** I waited for the screen to clear (`C3-04`, no bark), then double-clicked:

```
Item 8982 (class Container, shape 618) (uc: LCHST_EW), 0, (21152, 8832, 0) q: 20 … f: 0x2000 … items: 3
Item: 8982 (shape 618) calling usecode event 1 @ 026A:00B0
WARNING: Unhandled intrinsic 254 'isGameRunning()'? called!
```

- The plate at 0.35 s shows "locked chest" over the chest (`C3-05`), and at 3.5 s it is gone (`C3-06`). The zoomed sequence is `C3-07`.
- No gump opened. `objectInfo 8982` afterwards still reads `f: 0x2000`, frame 0.
- The same result held on the fresh chest 14891 after a map reload (`C4-06`).

**The log criterion fails, harmlessly.** `uc_machine.cpp:391-393` prints `Unhandled intrinsic N … called` for every intrinsic bound to `UCMachine::I_true` (or `I_dummyProcess`), and then runs it. Over the session, 11 warnings matched 11 chest `use()` calls one for one (7 at `004E:00A9`, 4 at `026A:00B0`). Upstream has the same `I_true` on slot 254 and so the same line.

## C4: the key path, FAIL (negative control)

**Negative control first, chest 8982.**
- **The key.** I single-clicked the pack key: `Item 4782 (shape 82) (uc: KEY) … q: 0` (look bark "key blank").
- **Use on the chest.** I double-clicked it, which gave a target cursor (`C4-02`), then clicked the chest:

```
Item: 4782 (shape 82) calling usecode event 1 @ 0052:04BB
Target result: Item 8982 (class Container, shape 618) (uc: LCHST_EW) … q: 20 …
findShape 618: 0 found
Item 8982 (class Container, shape 78) (uc: CHEST_EW) … q: 20 … items: 3
```

- **Result.** The q0 key unlocked the q20 chest, and the next double-click opened it (`C4-05`, frame 4, `f: 0x2100`). Finding 1 explains why.

**Positive path, after a map hop reset the chest** (chest 14891: shape 618, 3 items, still barks, `C4-06`):
- **The key.** Bag 6159 opened, and I single-clicked `Item 6161 … KEY … q: 20` (`C4-07`).
- **Use on the chest.** Double-click, then a click on the chest gave `Target result: Item 14891 … shape 618`. Then `findShape 618: 0 found`, `14891 … shape 78 (uc: CHEST_EW)` (`C4-08`, `C4-09`).
- **Open.** The next double-click gave `event 1 @ 004E:00A9`, frame 4, `f: 0x2100`, and the gump shows the three potions (`C4-10`).

## C5: Tiny Tar taken, PASS

The chest gump showed three potions (`C4-05`).
- **Potion 8984** went into the pack with `Item::grab 8984`, after two drags dropped at the pack's edge were refused (harness anomalies).
- **Potions 8985 and 8983** were dragged from the chest gump into the pack (`Dragging item …` / `Dropping object …`).

Afterwards:
- The chest reads `vol: 0/200 … items: 0`.
- All three potions read `f: 0x200c` in the pack (`C5-03`).
- The Avatar's weight went 260 → 290.

## C6: plain chests open, PASS

- **Retail chest.** Map 51 CHEST_EW 20060 (a treasure room) has no trap. A single click identified it (`C6-01`). A double-click logged `event 1 @ 004E:00A9` and the gump opened with its contents (`C6-02`, frame 4, `f: 0x2500`). A second double-click closed it (frame 0).
- **Hrodny's unlocked chest (shape 78).** It opened (`C4-10`) and closed (`C6-00`).
- **Not used.** The first try, Map 8 CHEST_NS 10981, failed `canReach` from behind its fence. That is not a chest defect.

## C7: Pagan locked chest, PASS

Map 41 LCHST_EW 31301 is at (14240, 13920, 0). It contains TRAP 31302 (`q: 0`, a booby trap) and TRAP 31307 (`q: 286` = `0x100 | 30`, the lock).

**Use.** A double-click logged `event 1 @ 026A:00B0` and the bark was "locked chest". No gump opened, and `f` stayed `0x2400` (`C7-02`..`C7-05`).

**Negative control.** I used the q20 key 6161 on it, and the log shows `Target result: Item 31301 …`. The chest stays shape 618, because the key does not match lock 30 (`C7-06`, `C7-07`).

## C8: 0x43 / 0x98 reachability, NOT DEMONSTRATED (static checks PASS)

I disassembled all of `shared/build/EUSECODE.FLX` with `u8_usecode_disasm.py … all`. The callers are:
- `calli 00FEh`: CHEST_EW 004E, CHEST_NS 0075, LCHST_EW 026A and LCHST_NS 02A1. Their bytes are identical to retail `shared/data/USECODE.FLX`.
- `calli 0043h`: 21 sites, all in `0598 EGGMAGNE`.
- `calli 0098h`: 6 sites, all in `04EC TYPEAOFR`, at 0162, 01A5, 022E, 02B7, 0340 and 03C9.

**Why none of it runs today:**
- **TYPEAOFR.**
  - **Events.** Its event table holds only `00 look()` and `0A equip()`. The freeEquip routines are reached only from `equip()`'s `getFrame() = 3` branch (`spawn 04EC:012E/016A` at 04FA/050A), and no other class calls into 04EC.
  - **No equip events.** U8 never fires event 0x0A: `I_equip` is bound only in the Crusader tables.
  - **Map items.** FIXED.DAT holds exactly two npcnum-236 items, both on Map 17: shape 539 at frame 0 and frame 1. The base NONFIXED.DAT has shape-539 items with npcnum 0, and none at frame 3.
  - **Usecode.** `EGGSHADE` creates shape 539 only at frames 4 and 2, and the build contains no `setNpcNum`.
- **EGGMAGNET** (class 1432 = quality 281 + 0x47F). No family-4 egg on any map, in FIXED.DAT or NONFIXED.DAT, has quality 281. No usecode pushes 0119h.
- **The session log** has no line for intrinsic 67 or 152.

## C9: log hygiene

| Pattern | Count | Note |
|---|---|---|
| `Unhandled intrinsic` | 11 | All are 254, one per chest `use()` (C3) |
| `Non-existent process` | 1 | `PID (0) in implies`, logged as Map 41 loaded among `LV: I_resetRef` lines, before any chest |
| `stuck in process loop` | 0 | |
| Segmentation / Assertion | 0 / 0 | |
| `Invalid item … passed to area search` | 17 | Shape-804 fire items on Map 8. They started before the trap (item 1393), and the trap explosion added some |

## Findings

1. **Hrodny's chest has no lock: any key opens it.**
   - **How retail locks a chest.** Retail LCHST locks are keyed by a **TRAP item (shape 756) inside the chest whose quality is `0x100 | keyid`**, not by the chest's own quality. KEYRING `004F:0445-04DB`, which is byte-identical to retail:
     1. scans the chest for shape 756 with `quality/256 == 1`;
     2. if it finds none, sets "unlocked" for any key;
     3. otherwise compares `trapQuality & 0xFF` with the key's quality.
   - **Retail data.** Every retail locked chest in NONFIXED carries such a TRAP: q 286, 287, 291, 304, 314, 336 and others.
   - **Our chest.** `build_map_10.py:823-857` places the chest with `quality=HRODNY_KEY_ID` and only the three potions inside. The comment at 777-778 ("its usecode class handles the quality=key-ID lock") is wrong.
   - **Effect.** Any key (the q0 key blank above, the Key to the Clouds, any Pagan key) unlocks it.
   - **Likely fix.** Add `contained_item(shape=756, quality=0x100 | 20)` to the chest. With `quality/256 == 1`, TRAP `use()` does nothing.
   - **History.** This also contradicts the 2026-09-02 Z-d note that the Cliff Key does not unlock it.
   - **Confidence.** High: in-engine result, disassembly and retail data all agree.
2. **The `isGameRunning` true branch fires chest booby traps, not "the containers inside".**
   - **The code.** CHEST_EW `00FF-0132` loops over shape `02F4h` (756, `TRAP`) inside the chest and calls `use()` on each. TRAP `use()` does nothing for `quality/256 == 1` (lock markers). For `quality/256 == 0`, it spawns FIRESPEL `0583:233D` (an explosion) and barks "Ouch! -That- must have hurt…".
   - **In engine.** Map 8 CHEST_EW 12731 holds TRAP 12732 at q 0. Opening it logged `Item: 12732 (shape 756) calling usecode event 1 @ 02F4:0080`, and an explosion followed (`F1-trap-1`, `-3`).
     - The Avatar went from **hp 30 to 20**.
     - The trap was consumed (5 items → 4).
     - The chest was blown from (23824, 7128) to (23823, 7273).
     - The gump still opened.
   - **Retail behaviour.** This matches retail, and `I_false` had disabled it. 38 TRAP items sit in retail chests.
   - **Wrong wording.** Three places describe this wrongly: the brief, `docs/research/2026-10-08-u8-intrinsic-table.md:94`, and the new fork comment in `u8_intrinsics.h` ("uses the containers inside it before opening").
3. **`Unhandled intrinsic 254` is still logged on every chest use.** This happens because slot 254 is `UCMachine::I_true`, which `uc_machine.cpp:391-393` treats as a stub marker. It is cosmetic. A named `I_isGameRunning` returning 1 would silence it, if wanted.
4. **On every Map 10 reload, Hrodny's chest relocks and refills.** After two hops, `findShape 859` showed 3 more frame-8 potions in a fresh shape-618 chest. Fixed items reload from FIXED.DAT (`world.cpp:178,196`). The refill was already known (2026-10-04 finding 9). The relock is new, because the chest used to open without a key. With finding 1, any key reopens it.
5. **`Actor::I_freeEquip` on the Avatar would leave the item in a state ScummVM never otherwise creates** [INFERENCE, unreachable today].
   - `MainActor::addItem` marks every direct child `FLG_EQUIPPED` (`main_actor.cpp:116-125`).
   - `CanAddItem` counts every direct child by equip type, whatever its flags (`:100-106`).
   - The paperdoll paints only `getEquip(1..7)`.
   - **Result.** A freed shield would vanish from the paperdoll and still block equipping another item in that slot. Retail keeps a separate 8-slot table, so it cannot fall into this state.
6. **`scummvm-lv-console/scummvm` is dated 2026-10-07 13:53**, before `f50c1d45`. Anyone launching with `LV_SCUMMVM=…console` runs the old `I_false`.
7. **Two docs are stale about the patch check.** `CLAUDE.md` ("Nothing tests that the patch still equals the fork diff") and `.claude/agents/verifier.md:49` ("Nothing else tests this") both say no test exists, but `agents/usecode-compiler/src/test_scummvm_patch_sync.py` (commit `db28de4`) does this check and passed.

## Harness anomalies

- **Gump drops.** Drags dropped at the backpack gump's lower edge or onto a covered area were refused silently: the log has `Dropping object` and nothing after it. Dropping at about (330, 150) inside the pack worked. A same-pack move of potion 8984 off the key was refused 3 times, so for C7's negative control I used the q20 key from the bag instead of the q0 key.
- **Map 8 CHEST_NS 10981.** The double-click logs the dump but no `use`, because `canReach` fails from behind its fence.
- **Teleports close the pack gump.** That is the leaked-`exit` trap.

## Disk changes

- **Wrote** this report and 36 plates in `docs/playtest-2026-10-08-intrinsics/` (C3-*, C4-*, C5-*, C6-*, C7-*, F1-*).
- **Regenerated by the checks:**
  - `shared/build/*`, with all 4 hashes unchanged;
  - `shared/data/u8-install/` via `install_lv.sh`, bytes equal to `shared/build`.

  `~/.config/scummvm/scummvm.ini` is unchanged (md5 `af255300…`).
- **Scratch in `/tmp/claude-1000/vif/`:** the game copy, `saves/` (`ultima8.001` = cp26; the engine wrote `ultima8.000`, `timestamps` and the history), `lv_run.log`, `build.log`, `install.log`, the disassembly (`eus_all.dis` and per-class files), `NONFIXED.DAT` extracted from `U8SAVE.000`, the driver in `py/`, and frames in `sp/`.
- **Not touched:** `shared/u8-lv-patched`, `~/.local/share/scummvm`, `~/lv-checkpoints` (read only), and any source, builder, map, fork, TODO or HANDOFF file. Nothing was committed. ScummVM and Xvfb `:79` are stopped.
