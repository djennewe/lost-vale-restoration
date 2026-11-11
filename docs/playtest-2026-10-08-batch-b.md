# Batch B: the restored Shield (828 q83) and Aramina's retail bits (2026-10-08)

**Build under test.** `main` at `dfff626`, plus the uncommitted `build_scummvm.sh` and `ARTIFACTS.sha256`.
- The binary is `scummvm-lv/scummvm`, dated 2026-10-08 22:41:40.
- The log reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `usecode/eusecode.flx: e5f36c956873ace1a550c08f7b7a680f, 1525085 bytes`.
- The game copy `/tmp/claude-1000/vsa/game` (rsync of `shared/u8-lv-patched`, no `.bak`) has sha256 EUSECODE `d4915144…`, U8SHAPES `bb0e4cda…`, TYPEFLAG `794d4b80…`, ANIM.DAT `77e9705d…`, and FIXED `1e954b7a…` in both places. These match `ARTIFACTS.sha256`.
- Plates are in `docs/playtest-2026-10-08-batch-b/`, at 640x400.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| S1 | The ceremony uses up both halves and puts an 828 q83 frame-0 shield in the pack, and it draws as the blue-rimmed quartered oval | **PASS** |
| S2 | The shield can be dragged out, dropped and picked up again, and the paperdoll shield slot refuses it | **PASS** (no positive control: there was no equippable item to compare against) |
| S3 | look() barks "Ceremonial Shield of the Ancients Ones" | **PASS** |
| S4 | The Map 18 altar with templeOpen and shieldFixed: the place bark, the god pan, "The Ancient Ones are free", godsFree=1, and the endgame proceeds | **PASS**, but **templeOpen came from a debug teleport into the sanctum** and the endgame egg was not walked (below) |
| S5 | The altar refuses a 539 f2 and an 828 q0 with the "lack the artifact" bark, and Pagan's 828 still looks "Zealan ceremonial shield" | **PASS** |
| S6 | Before the ceremony, the halves look "broken shield" | **PASS** (both halves) |
| S7 | When Atli's "I have this shield!" appears | **Static answer, NOT DEMONSTRATED in-engine**: only in the *first* conversation with Atli (below) |
| A1 | Aramina: 0x207 takes MORDEA's values over time; at_home she walks her route; 0x663 is never written | **NOT DEMONSTRATED** in-engine (the request budget ran out). Static evidence below |
| A2 | 0x207 = 2/3 and 0x58 = 0 gives "attend to her ladyship" plus the find-me-later line | **NOT DEMONSTRATED** (budget) |
| A3 | Pre-Devon dialogue at home is unchanged | **NOT DEMONSTRATED** (budget) |
| A4 | Post-Devon behaviour through retail 0x58 | **NOT DEMONSTRATED**: no checkpoint has 0x58 set (all 113 scanned) |
| A5 | A checkpoint saved before this build loads and plays | **PARTIAL**: `run-s13-shield-halves` (09-07) and `cp34-altar-ready-head` (09-26) loaded and played the whole S-chain. **No Tenebrae save was loaded** |
| L | Log hygiene | **PASS**. 11,656 lines: 0 `Unhandled intrinsic`, 0 `Non-existent process`, 0 `stuck in process loop`, 0 Segmentation, 0 Assertion, 0 `Cycle in paint` |
| C1 | `tools/run_all_tests.sh` | **PASS**: `OVERALL: PASS — 42/42` |
| C2 | Patch equals the fork diff | **PASS**: `PATCH_EQUAL` at `ed924d30` |
| C3 | `build_artifacts.sh` / `install_lv.sh` / `build_scummvm.sh` | **SKIPPED** on instruction: they were already run, and another verifier was running in parallel. The sha256 check above stands in for them |

## Method

- **Isolation.**
  - Display `:83` (1280x800). The window sat at (480, 300).
  - Scratch dir `/tmp/claude-1000/vsa/`, config `vsa/scummvm.ini` (`usehighres=true`), saves in `vsa/saves/`, and `SDL_AUDIODRIVER=dummy`.
  - Command: `scummvm-lv/scummvm --config=… --savepath=… --extrapath=scummvm-lv/dists/engine-data --debuglevel=1 --path=vsa/game --save-slot=1 ultima8`.
  - One pid ran the whole session. I started and stopped only my own Xvfb and ScummVM; the other verifier's `:82` was not touched.
- **Saves.** Each save was copied over `ultima8.001`, then loaded with `Ultima8Engine::loadGame 1`:
  - `run-s13-shield-halves.sav` (md5 `5200e87e…`): S6, S1, S2, S3;
  - `cp34-altar-ready-head-20260926.sav`: S5;
  - my own `vsa/sp/vsa-after-ceremony.sav`, saved right after S1: S4.
- **Game-state writes.**
  - Teleports with cheats on, each followed by a toggle back to off (`Cheats = false` is in the log each time).
  - `MainActor::toggleCombat` once.
  - `debugflag_enable Object` after every load.
  - `Item::grab` twice: shield half 2932, after a look-test throw, and Pagan 828 16262.
  - One `Ultima8Engine::saveGame`.
  - No `setGlobal` was used.
- **What was played, not set.** Every egg was walked into, and every menu answer was clicked on screen.

## S6: the halves before the ceremony, PASS

`findShape 539` shows both halves in the pack: 12073 (frame 0, q81) and 2932 (frame 1, q82), both `n: 236`. A single click on each logs `calling usecode event 0 @ 04EC:0080`, and each barks **"broken shield"**:
- frame 0 in the pack (`S6-02`);
- frame 1 after I threw it to the ground (`S6-03`, both looks side by side).

Afterwards I put 2932 back with `Item::grab 2932` → `grab: 2932 in pack`.

## S1: the ceremony, PASS

I teleported to Map 10 (20304, 17600), turned cheats off, and walked north. The log shows `Item: 4474 (shape 73) calling usecode event 7 @ 05A5:0080` (EggShades). From the screen I picked:
1. **Let's be reasonable!** (`S1-02`);
2. **Yes, Priestess.** (`S1-03`);
3. **Please, High Priestess.** (`S1-05`).

In the scene:
- The halves are popped and blasted.
- A blue-rimmed shield appears on the grass by Ezrekal (`S1-04`, zoom `S1-04b`).
- The bark "I take up the Shield of the Ancients. Its place is on the temple altar." follows (`S1-06`).

Afterwards:
```
findShape 828: Item 24553 (class Item, shape 828) (uc: AORTA), 0, (0, 0) q: 83, m: 0, n: 0, f: 0xc ... et: 0
findShape 539: 0 found
shieldFixed 1, avatarPoisoned 0, inShadeScene 0, godsFree 0; weight 130 -> 80
```

In the pack it draws as the blue-rimmed oval, quartered, with red elemental sigils (`S1-07`, zoom `S1-08`). The q83 survived a save and a reload (`findShape` after the reload: `q: 83`).

## S3: look(), PASS

A click on 24553 in the pack logs `calling usecode event 0 @ 033C:0080`, which is the replaced AORTA. The bark is **"Ceremonial Shield of the Ancients Ones"** (`S3-01`, `S3-02`).

## S2: drag, drop, pick up, paperdoll, PASS

- **Drag out.** Pack to ground: `Dragging item 24553` / `Dropping object 24553` / `Throwing item to (20862, 17218, 0)`. It lies at (20816, 17175, 0), `f: 0x2004`, and draws on the grass (`S2-02`).
- **Pick up.** I walked adjacent and dragged it onto the Avatar: `Dropped item in backpack`. Weight went 50 → 80 (`S2-03`).
- **Paperdoll.** A double-click on the Avatar opened the paperdoll (`S2-04`), and I dragged the shield from the pack onto the figure's arm (`S2-06`, mid-drag).
  - On release the paperdoll shows no shield (`S2-07`).
  - The shield is back in the pack at a new random spot, (6,32) → (19,35), with `f: 0x200c`, which has no `FLG_EQUIPPED` (0x200).
  - This is `PaperdollGump::DropItem`'s `equiptype == 0` branch (`paperdoll_gump.cpp:402-407`): `moveToContainer(backpack)` plus `randomGumpLocation()`.
- **Missing control.** No equippable shield was available as a positive control, because the halves were consumed.

## S5: negative controls at the altar, PASS

**539 frame 2.** `cp34` loads on Map 18 (3400, 7696) with templeOpen 1, shieldFixed 1, godsFree 0, and in the pack `Item 12938 … shape 539, 2 … q: 0`. I hopped Map 10 → Map 18 to get fresh fixed items, landed at (3072, 8640) and walked north. The log shows `Item: 7908 (shape 73) calling usecode event 7 @ 05A7:0080`, and the bark is **"I sense great power here, but I lack the artifact needed for the ceremony."** (`S5-02`, `S5-02b`). godsFree stayed 0.

**Pagan 828, quality 0.** Map 8 (Mythran's house) has `Item 16262 … shape 828 … (1090, 1678, 64) q: 0, f: 0x3400`, hanging on the wall (`S5-03`).
- **Look.** A click logs `event 0 @ 033C:0080` and the bark is **"Zealan ceremonial shield"** (`S5-04`).
- **To the altar alone.** I took it with `Item::grab 16262` and threw the 539 f2 out of the pack, so the q0 828 was the only candidate. After a fresh Map 18 entry I walked onto the altar egg: `event 7 @ 05A7:0080`, the same "lack the artifact" bark (`S5-06`, `S5-06b`). godsFree stayed 0.

## S4: the altar ceremony, PASS (with a shortcut)

**The shortcut.** I loaded `vsa-after-ceremony.sav` (24553 q83 in the pack; templeOpen 0, shieldFixed 1). Then I **debug-teleported into the Inner Sanctum** at (2864, 6560), south of EggTempleEntry, and walked north across it:
```
Item: 25151 (shape 73) calling usecode event 7 @ 05B0:0080   (EggTempleEntry)
Item: 24905 (shape 73) calling usecode event 7 @ 05B1:0080   (EggCrackHint)
templeOpen 1
```
The Tiny Tar route through the crack was not walked. templeOpen was set by its own egg, not forced.

**The ceremony.** I walked onto the altar egg from the south-west (`event 7 @ 05A7:0080`, egg 25152) and left the scene untouched:
1. "I place the artifact upon the altar. The ancient symbols begin to glow." (`S4-01`, `S4-01b`);
2. the fade to white (`S4-02`);
3. the pan across the god crystals, which shatter in turn (`S4-03`, `S4-04`, sheet `S4-06`);
4. the camera's return to the Avatar and "It is done. The Ancient Ones are free. I can feel their gratitude -- and their power." (`S4-05`, `S4-05b`).

Afterwards: `godsFree 1, templeOpen 1, shieldFixed 1, endgameStarted 0`. The shield is still in the pack (AOSCENE does not consume it).

**"Endgame proceeds" is only partly shown.** godsFree is the gate EggEndgame reads (Map 10 arrival pad, q299). I did not walk back to Map 10 to fire it, which is why endgameStarted is 0.

## S7: Atli's "I have this shield!" option, static answer

The option is added in `lv-patched/ATLI.UNK:1076-1082`, inside the `"I -am- from Brittania!"` case. That case is reachable only through the chain that starts at `"May I speak with you?"`. That first option is offered only when `atliMet` is false (`:647`), and its own case sets `atliMet = true` (`:678`). So the option appears **only in the player's first conversation with Atli**, and only if an 828 frame 0 is already in the inventory. With the ceremony's shield, that means only a player who reached the Shades scene without ever opening that conversation with Atli. With a Pagan 828, it means one carried into the Vale before meeting him.

In normal play it never appears afterwards: every post-ceremony checkpoint has `atliMet` 1. I had no budget for an in-engine first meeting carrying Pagan's 828 (`cp7-map10-entry`, which has atliMet 0, plus Map 8's shield would do it).

## A1–A4: Aramina, static evidence only

None of these were run in-engine: the request budget ran out after the S-claims. Here is what static checks show.

**The checkpoints.** I decoded `UCGLOBALS` out of all 113 gzip'd checkpoints in `~/lv-checkpoints`:
- 0x207 already holds 1, 2 or 3 in most of them (`cp2b`–`cp3g` 3, `cp3h`–`cp5` 2, `cp1`/`cp2` 1). Retail MORDEA (byte-identical to retail) was writing it all along.
- **0x663 and 0x4B6 are 0 in every save.**
- **0x58 is 0 in every save**, so A4 has no cheat-free save to test on. The only writer in reach is the dev-menu `Jump ahead → ginaf` cheat (`lv-patched/AVATAR.UNK:1135`).

**The operands.** Disassembled operands of LV ARAMINA 0x40D: `0207h 02h` ×7 and `0058h 01h` ×3, with no 0x663 or 0x4B6.

**Timing for A1 (a checkable expectation).** MORDEA's schedule changes 0x207 only at period boundaries: `getPeriod() = hour/4`, and one game hour is 27,000 frames, about 15 real minutes. So a value change takes up to an hour of real time, or the dev-menu "Time" option (+4 h).

## Findings

1. **ARAMINA's other flags still use LV-only bits, so retail state never reaches her dialogue.** Retail ARAMINA reads araminaMet/Name/Job at 0x203/0x204/0x205, hasHeart at 0x00F, and others at 0x027, 0x036, 0x03C, 0x0BF, 0x0D6, 0x11A and 0x147. Ours reads 0x65F/0x660/0x661, 0x46D, 0x485, 0x494, 0x49A, 0x51D, 0x534, 0x576 and 0x5A3 (from `u8_usecode_disasm` of both FLXs). For example, our `mordeaDead` (LV 1398 = 0x576) is never written by retail MORDEA/LOGBOOK, so her dagger-key branch ("Mordea kept it in a chest…") is unreachable in a real post-Mordea game. The commit says the other retail_shared pins are unmigrated, so this is known in kind, but A3/A4 depend on it. (Mapping each retail bit to a name is [INFERENCE] from operand order.)
2. **The altar ceremony leaves the Shield in the pack** (24553 still `q: 83` after godsFree). Harmless, but the bark says "I place the artifact upon the altar".
3. **Pagan's 828 in Mythran's house can be taken.** It is `Item::grab`-able, and nothing stops a player carrying it into the Vale before meeting Atli. That is the only realistic way S7's option fires.
4. **`findShape 539` after the ceremony is 0.** No stray frame-4 anchor or leftover halves remain.

## Harness anomalies

- Same-pack drags of a shield half were refused twice (`Dropping object` with nothing after it), as in the 10-08 report. A drag to the ground worked.
- The run gait stalled on the sanctum's 8-unit tiers. The walk gait (mag 130) got through.
- From the north, the altar block stopped a straight walk into the egg. Entering from the south-west hatched it.
- Cells that waited on scenes hit the 30 s eval cap twice. No game effect.

## Disk changes

- **Wrote** this report and the plates in `docs/playtest-2026-10-08-batch-b/` (S1-*, S2-*, S3-*, S4-*, S5-*, S6-*).
- **Scratch in `/tmp/claude-1000/vsa/`:**
  - the `game/` copy, `scummvm.ini`, and `saves/` (`ultima8.001` = the post-ceremony save after S4; the engine wrote `ultima8.000` and `timestamps`);
  - `lv_run.log`, `tests.log` and `xvfb.log`;
  - `dis/` (retail and LV 0x407/0x40D disassemblies);
  - the driver in `py/`, and frames plus `vsa-after-ceremony.sav` in `sp/`.
- **Not touched:** `shared/u8-lv-patched`, `shared/build`, `~/lv-checkpoints` (read only), `~/.config/scummvm/scummvm.ini` (md5 `af255300…` unchanged), and any source, builder, map, fork, TODO or HANDOFF file. Nothing was committed.
- **Stopped:** my ScummVM and Xvfb `:83`.
