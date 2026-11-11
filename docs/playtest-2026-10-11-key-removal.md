# Key removal verification: Hrodny's chest key now comes only from her errand (2026-10-11)

**Change under test.** The working tree on main `99df069`. `build_map_10.py` no longer places the spare q20 key ("lost somewhere in the village") at (22016,6144,0); Douglas removed it on 2026-10-11. `test_chest_locks.py` now requires that no key of quality 20 is placed, and `test_uc_dialogue.py` gains the "HRODNY key errand" checks. `map_pins.json` and `ARTIFACTS.sha256` were updated to match: FIXED went from `eff07302…` (1,852,016 bytes) to `122b4374…` (1,852,000 bytes).

**Game copy.** `/tmp/claude-1000/vkey/game` was made from vf10's copy, and all five artifacts were copied from `shared/build/`, with FIXED in both places it lives. Every file matches `shared/build/ARTIFACTS.sha256`:

| File | sha256 |
|---|---|
| FIXED | `122b4374…` (root and `STATIC/`) |
| EUSECODE | `4182e079…`. The log reads `usecode/eusecode.flx: d00d0d59…, 1526311 bytes`, and the game was identified |
| U8SHAPES | `69fbd861…` |
| TYPEFLAG | `6bdb3036…` |
| ANIM | `77e9705d…` |

**What changed in FIXED.** I compared old FIXED `eff07302` with new FIXED `122b4374` one map entry at a time. The only difference is in Map 10, which is 16 bytes shorter. The one record removed is `00560018005200000000140000000000`: shape 82, frame 0, at (22016,6144,0), quality 20. It sat at offset 102320. Taking it out of the old entry gives the new entry byte for byte, so nothing was reordered, and the chest, its TRAP and its potions keep their sequence.

**Binary and display.** The binary is `scummvm-lv/scummvm`, built 2026-10-11 04:17, which is after fork `b867a30c` (2026-10-10 20:30). Xvfb `:93` ran with vf10's ini: 320×200, no width/height keys, `frameLimit=true`, `SDL_AUDIODRIVER=dummy`.

**Driver.** `vkey/py/vk.py` is vf10's `vf.py` with its paths changed and `PRIME = False`, so no left click comes before a right hold. A sacrificial Shift press followed each load and each teleport. Combat bit 0x800 read `flags: 0` at every `objectInfo 1`.

**Cheats.** Cheats were on only for teleports, and every talk, click and drag happened with cheats off. Each toggle was confirmed by its echoed `Cheats = …` line.

**Save.** The test started from `run1010-s15-m10-shield-restored-cured.sav` (`200eda7d…`), copied from `~/lv-checkpoints` without changing it.

## Verdicts

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| K1 | After a map hop, Map 10 has no shape-82 q20 key; the chest at (21024,8832) is still locked, and a q170 key does not open it | **PASS** | **Before the hop**, the s15 checkpoint still carries the old fixed items: `findShape 82` lists key **25460 q20 at (22016,6144,0)**, and it is drawn there (`K1-00`). **After the hop** (Map 10 → 13 → 10, with `Loading Fixed items in map 10`), `findShape 82: 1 found`: only the Avatar's own **q170** cliff key 10999, which is in his pack. The same view has no key at that spot (`K1-01`). The pixel diff against `K1-00` covers only the Avatar, the pointer and the key's pixels. The **chest** 11813 (shape 618 LCHST_EW, q20, 4 items) barks "locked chest" on a double-click (`K1-02`). **Negative control:** I used key 10999 **q170** on the chest. The log has `event 1 @ 0052:04BB` and `Target result: Item 11813 … shape 618`, and afterwards `findShape 618: 1 found` and `findShape 78: 0 found`, so it stayed locked (`K1-03`) |
| K2 | Talk to the healed Hrodny: "I have been healed!" → "How can I open the temple?" sets spokeTemple 1, and a bag appears on the ground at (19588,23284,0). Pick it up; it holds a q20 key; using that key opens the chest, which holds three Tiny Tars | **PASS** | **Flags before:** haveMark 1, avatarPoisoned 0, templeOpen 0, spokeTemple 0. **Talk 1** set hrodnyMet 1 (`K2-01`). **Talk 2**, menu picked from the screen: "I have been healed! / The Shield of the Ancients is restored! / bye" (`K2-02`) → "See, so I do!… open the temple, will you?" (`K2-03`) → "How can I open the temple? / bye" (`K2-04`) → the four errand barks, including the lead "up the old temple road, southward" (`K2-05-*`). **After:** spokeTemple **1**. Bag **24547** (shape 637) appeared at **(19588,23284,0)**, holding key **24546, shape 82, q20**. It is drawn on the ground (`K2-06`). **Pickup by drag:** `Dragging item 24547` → `Dropping object 24547` → `Dropped item in backpack`. Weight went 60 → **80**. The bag opened in the pack showing the key (`K2-07`), and a click on it reads `Item 24546 … shape 82 … q: 20`. **Unlock:** the q20 key used on the chest gave `Target result: Item 11813`, and the chest became **shape 78 CHEST_EW** (`findShape 618: 0 found`; `K2-08`). **Open:** a double-click logged `event 1 @ 004E:00A9` and TRAP `event 1 @ 02F4:0080`, and hp stayed 30. The gump shows three potions (`K2-09`). `findShape 859` lists **3 frame-8 items, 11247, 11812 and 12929, contained** (`f: 0x2008`) |
| K2-neg | The errand cannot be repeated to get a second key | **PASS** | **Talk 3**, with the bag already in the pack: the healed menu comes back (`K2-10`), then "How can I open the temple?" → "Told you, I have… gone, the key to the chest, is…" (`K2-11`). Afterwards `findShape 637`/`82` show **no new bag and no new key**. The only q20 key is still 24546, in the pack |
| K2-persist | An unpicked bag survives leaving Map 10 | **PASS** | I loaded my save taken just after the errand, with the bag still on the ground. After a hop Map 10 → 13 → 10, the bag is still at **(19588,23284,0)** holding a **q20** key: bag 27283 and key 27282, because ids are renumbered on load (`K2-12`). It is usecode-created, not a fixed item, so a reload of the fixed items does not touch it |
| L | Log hygiene | **PASS** (stock noise only) | Over one session: 5 map loads, 2 save loads and the boot. 0 each of `Cycle in paint`, `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Trying to access segment`, `popToContainer`, ERROR, `Invalid item` and `Skipping invalid shape`. **4 × `Unhandled intrinsic 254 'isGameRunning()'`**: three are LCHST/CHEST `use()` calls and one is the open. That is the expected `I_true` stub warning (`TODO.md:412-414`). **1 × `Invalid procid 14578 in waitlist`**, printed right after `UCLISTS: ok` while my own mid-session save loaded; that save was taken about 1 s after Hrodny's `exitConvo`. Fix 9 logged 5 of the same kind. The other WARNINGs are stock: gui-icons, translations.dat and theme. 34 × `Can't use: avatarInStasis` came from talk strikes during the conversation, not from the game. hp stayed 30 throughout |
| Checks | Test estate; hashes; build; fork | **PASS**, partly not run | `tools/run_all_tests.sh`: **46/46 PASS**. That includes `test_chest_locks` 3/3, whose new check reads "no placed key has quality 20". It also includes `test_uc_dialogue` **460/460** (455 + the 5 errand checks), `test_map_pins_fresh` 3/3, `test_route_reach` 138/138 and `test_scummvm_patch_sync` 3/3. The game copy's hashes match the canonical file. I did **not** run `tools/build_artifacts.sh`: the assignment forbids build scripts. The single-record FIXED diff above stands in for it. Usecode, shapes and the fork are untouched: EUSECODE `4182e079` is unchanged, and the fork is still `b867a30c`. So the Compilation Report, shape-table and patch-sync checks do not trigger, beyond the estate's own patch-sync test |

## K1: the spare key is gone after a hop — PASS

| Step | Result |
|---|---|
| s15 loaded, Map 10, before any hop | `findShape 82: 2 found`. They are 10999 q170 (in the pack) and **25460 q20 at (22016,6144,0)**. In a teleport to (21920,6240) the key draws at window (416,228) (`K1-00`) |
| Hop: teleport to Map 13 (4064,10346), then back to Map 10 (21920,6240) | The log has `Unloading Fixed items from map 13` / `Loading Fixed items in map 10` |
| `findShape 82` after the hop | **1 found**: 10999 q170 only. Nothing is at (22016,6144) (`K1-01`) |
| Chest look-click | `Item 11813 (class Container, shape 618) (uc: LCHST_EW), (21024, 8832, 0) q: 20 … items: 4` |
| Chest double-click | `event 1 @ 026A:00B0`. It barks "locked chest" and opens no gump (`K1-02`) |
| q170 key on the chest (negative control) | `event 1 @ 0052:04BB` (KEYRING), `Target result: Item 11813`. The chest is still shape 618, and `findShape 78` finds 0 (`K1-03`) |

The before-and-after pair is also the check that the census works. The same `findShape 82` that finds no key after the hop found the spare key before it, on the same save.

## K2: the errand is the key's only source — PASS

**The talk.** Hrodny (npc 113) wanders between her hut and Tyorvi's stash. Each talk took 1-40 strike attempts (harness anomalies). Every option was clicked from the menu on screen:

1. **Talk 1** (hrodnyMet 0): "What is your name? / What do you do? / bye" (`K2-01`) → "Hrodny, daughter of Ulnar, I am." → bye. hrodnyMet then read **1**.
2. **Talk 2:** the greeting menu was "**I have been healed! / The Shield of the Ancients is restored! / bye**" (`K2-02`).
   - "I have been healed!" → "See, so I do! For you, good! Perhaps something to these god stories, there is. So now, open the temple, will you?" (`K2-03`)
   - The menu then read "**How can I open the temple? / bye**" (`K2-04`).
   - "How can I open the temple?" gave four barks: "Why me, these questions…", "But wait! Perhaps, a way, there is…", "Under my pillow, the key was…", and "Yet one thing more… up the old temple road, southward… Look along that road" (`K2-05-errand-bark-0…5`). Then the conversation closed.
3. **Flags after:** spokeTemple **1**. haveMark 1, templeOpen 0 and hrodnyMet 1 were unchanged.

**The bag.**

| Probe | Result |
|---|---|
| `findShape 637` | Bag **24547 at (19588,23284,0)**, `Container … items: 1`. The other bag in the list, 15913 at (16447,25727,64), was there before the talk |
| `findShape 82` | Key **24546, q 20**, `f: 0x8` (contained) |
| The plate | Teleported to (19460,23170), with cheats off afterwards: a brown sack on the grass beside the road, between two trees (`K2-06`) |
| Reach | `exact_reach.py --map 10 --seed 20880,8800,0 --target 19588,23284,0` gives **REACHED: stand at (19495,23191,0)** from the chest front. I did not walk the 14,450-unit trip (finding 2) |

**Pickup.** I dragged the bag from the ground onto the Avatar. The log reads `Dragging item 24547` → `Dropping object 24547` → `Dropped item in backpack`, and weight went **60 → 80**. Opened in the pack, the bag shows one key (`K2-07`). A click on it logged `Item 24546 (class Item, shape 82) (uc: KEY), … q: 20`.

**Unlocking and opening the chest:**
- **The key, used on the chest:** `event 1 @ 0052:04BB` and `Target result: Item 11813`. The chest was then **shape 78 (CHEST_EW)**: `findShape 78` gives 11813 q20 with 4 items, and `findShape 618` gives 0 (`K2-08`).
- **A double-click opened it:** `event 1 @ 004E:00A9`, then the TRAP `event 1 @ 02F4:0080`. No explosion, and hp stayed 30.
- **Three Tiny Tars inside.** The gump shows three potions (`K2-09`). `findShape 859` lists **11247, 11812 and 12929, all frame 8, npcnum 229, contained**. The two other 859s nearby, at (21216/21280,8832,0), are the frame 5 and 7 potions on the ground outside the hut.

**The repeat (negative control).**
- **Talk 3** offered the healed menu again (`K2-10`).
- "How can I open the temple?" now gives the `spokeTemple` branch: "Told you, I have. Give you the potions, I would. But gone, the key to the chest, is…" (`K2-11`).
- No new bag or key appeared: `findShape 637` shows only the pack bag and the old 15913, and `findShape 82` shows only q170 and q20 24546.

**Persistence.** I reloaded the save taken right after the errand, with the bag unpicked, and hopped Map 10 → 13 → 10. The bag was still at (19588,23284,0) with its q20 key (`K2-12`).

## Findings outside the brief

1. **The open question is still open in the tracking docs.** It is answered by this change, and the following lines will be stale once the change is committed:
   - `TODO.md:408-411` still asks "a spare q20 key lies in the village … Keep it, or remove it?"
   - `HANDOFF.md:19-20` and `:60` list the same question as Douglas's.
   - The frozen duplicate `agents/map-builder/docs/map-10-lost-vale.md:166` still reads "Key to Hrodny's chest (elsewhere in the village — lost)". The diff updated only the map-populator copy.
   - `derive_map_pins.py:637-639` keeps a `KEYS[20]` description for a placed q20 key that no map now has. It is a harmless dead row; `map_pins.json` no longer carries it, and `test_map_pins_fresh` passes.
2. **The round trip is now mandatory and was not walked.**
   - **The distance.** The bag is 14,450 units south of the chest (y 8832 → 23284), and nothing else opens the chest. Full run part 6 skipped this walk with the spare key, so no in-engine walk of it exists.
   - **Is the route open?** `exact_reach` says the bag is reachable from the chest front (above). I teleported to the bag. The pickup itself was a real drag, and that was the part under test.
   - **What remains.** Whether a player can follow the lead "up the old temple road, southward" is a route-guide question, not demonstrated here.
3. **One key, with no replacement.**
   - **What was seen.** The errand runs once: talk 3 gave "Told you…" and no bag (K2-neg).
   - **Why it matters.** The chest relocks and refills on every Map 10 reload (`docs/playtest-2026-10-08-intrinsics.md` finding 4). So a player who drops or loses the q20 key after emptying the chest once can never reopen it.
   - **Severity.** The first three potions are already in the pack by then, so this blocks only a refill [INFERENCE].
4. **Every Map 10 checkpoint taken before today still holds the spare key** (25460 at (22016,6144), `K1-00`) until the Avatar leaves Map 10 and comes back (traps.md, "A checkpoint carries its map's fixed items"). That includes `run1010-s04e` through `s18c` and `vb7`. A playtest of the errand from one of them without a hop can pick up the spare and skip the errand without noticing.

## Harness anomalies

- **Hrodny strikes.**
  - **How many tries:** talk 2 took 1 strike cycle. Talk 1 took 11 cycles of 3 double-clicks, and talk 3 took about 40 polls. She walks almost continuously.
  - **The plate overlap:** my first strike helper aimed at her sprite while she stood over the Avatar's, and one double-click opened the Avatar's paperdoll. I closed it with a double-click and excluded the Avatar's screen box from later aims.
  - **The cell timeouts:** two eval cells timed out at 30 s mid-poll. Both were interrupted cleanly, and the game was not affected.
- **`Can't use: avatarInStasis` ×34:** these are my extra double-clicks during the conversation's own stasis. They are not game errors.
- **First input after a load or teleport:** I sent a sacrificial Shift press each time. No swallowed input was seen.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-key-removal/` (21 plates, `K1-00` … `K2-12`).
- **Scratch** `/tmp/claude-1000/vkey/`:
  - `game/` (the build under test) and `scummvm.ini`;
  - `saves/` (slot 1 overwritten);
  - `lv_run.log`, `trace.txt` and `estate.log`;
  - `py/vk.py`;
  - in `sp/`: `s15.sav` and `s16a.sav` (copies), `vkey-after-errand.sav`, and working plates.
- **Banked nothing** in `~/lv-checkpoints`.
- **Stopped** my ScummVM (pid 385088) and the Xvfb `:93` I started (pid 385083). Xvfb `:94` and the other displayfd Xvfb are not mine and were left running.
- No source, map, fork, `TODO.md` or `HANDOFF.md` edits. No install or build runs.
