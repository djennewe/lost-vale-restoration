# enterConvo kills only the talked-to NPC's processes, verified in engine (2026-10-04)

Change under test: `agents/usecode-compiler/src/u8c_codegen.py`, the
`EnterConvoStmt` branch. `enterConvo()` now pushes the type, then
`referent` (`push dword [BP+06]; push indirect 02`), and calls
`Kernel::resetRef` for 0x205, 0x200, 0xF0, 0x204 in that order, in place of
`Npc::getNpcSlot()` (a null intrinsic returning 0) for 0x205, 0xF0, 0x204.
Plus `test_killprocess_npc_ref_cells.py` and the rehash in `build_scummvm.sh`
and `shared/build/ARTIFACTS.sha256`. It answers
`docs/playtest-2026-10-02-pt-activity.md` finding 2.

Artifacts: EUSECODE `ec3e66fd...`, 1,507,226 bytes, first 5000 bytes md5
`aaa24be5...`; FIXED `079829c1...`. Plates are in
`docs/playtest-2026-10-04-convo-kill/`, 640x400.

## Verdicts

| ID | Claim | Observed | Verdict |
|---|---|---|---|
| C0 | Build and detection | build exit 0, four OK; estate 38/38 (`test_killprocess_npc_ref_cells.py` 27 passed); 46 of 48 compiled; 0 `calli 04h 009Ah` (getNpcSlot) left in the FLX; both session logs read `aaa24be56663d448c719c6121d8eb85d, 1507226 bytes`; binary built 20:45 | **PASS** |
| C1 | Bystander processes survive; every conversation resetRef names only the talked-to NPC | Aramina twice: PESANT3 (pid 19) alive throughout, resetRef item 13 only; Hrodny: Ingjald's loiter 4371 alive throughout, resetRef item 113 only; Ingjald and Thordis the same; 146 resetRef lines in two sessions, none for item 0 | **PASS** |
| C2 | Talked-to NPC's activity stopped during the conversation and resumed after; Avatar frozen during, free after | each NPC's loiter, pathfinder, and anim gone while talking, a new loiter after; stasis `true` during the Hrodny, Ingjald, and Thordis menus and `false` after; the Avatar walked after each | **PASS** |
| C3 | Two or three more conversations open, run their menus, close | Ingjald (name, what do you do, bye) and Thordis (four options, what is this place, bye), besides Hrodny; each answered and closed on **bye** | **PASS** |
| C4 | 0 `Unhandled intrinsic 154`, 0 non-existent-process lines, no segfaults or assertions | 0 `Unhandled intrinsic 154`, 0 segfaults, 0 assertions, 0 `stuck`; one `Non-existent process PID (0) in implies` per session, at Devon's farewell on Map 3 before any LV conversation | **PARTIAL** (one line per session, outside the changed code, finding 1) |

## Method and harness writes

Saves (48 files, md5 list) and `scummvm.ini` (`a143fa3b`) were copied to the
scratchpad (`cvbak/`) first and restored at the end; `md5sum -c` passes on
all 48, the names match, and the ini reads `a143fa3b`. `./install_lv.sh`
exited 0; `session.sh start` synced EUSECODE into `shared/u8-lv-patched/`.
Two sessions, each a fresh world, one ScummVM pid each. Devon's opening menu
was answered by clicking **Goodbye**, and his farewell was waited out (45 s)
before any console use.

The 10-02 record used `cp22-hastea.sav` for Map 10. That save holds NPC
processes from an earlier build, and this change shifts offsets in every
class with a bare `enterConvo()`, so the Map 10 work here used a fresh world.

Writes, all disclosed:

- **Teleports with cheats on**, each followed by `Cheat::toggle` back to
  `Cheats = false` before any click on an NPC (each confirmed in the log).
  Session 1: Map 41 (16671, 19200, 48). Session 2: Map 10 (22148, 8260, 0)
  and (6344, 6956, 0), the second a same-map hop to Thordis.
- **`Ultima8Engine::toggleAvatarInStasis`**, in pairs only (each call prints
  the new value; the second restores it), to read the freeze.
- `debugflag_enable Object`; reads: `Kernel::listProcesses`, `objectInfo`.
- No save written, no checkpoint loaded, no trace.

Every NPC was reached on foot within its map and talked to by a double-click
on its sprite. Every menu answer was clicked from the screen.

## C0: build and bytecode, PASS

- `tools/run_all_tests.sh`: `OVERALL: PASS — 38/38 test file(s)`;
  `test_killprocess_npc_ref_cells.py PASS ... 27 passed, 0 failed`.
- `tools/build_artifacts.sh`: exit 0; `EUSECODE.FLX OK ec3e66fd`,
  `FIXED.DAT OK 079829c1`, TYPEFLAG and U8SHAPES OK. Compilation Report 46
  of 48, failures `EALOGO.UNK` and `TJORVI.UNK`.
- EUSECODE 1,507,226 bytes, md5-5000 `aaa24be56663d448c719c6121d8eb85d`,
  matching `build_scummvm.sh:54-55` and `detection_tables.h:297`; the fork
  patch equals the fork diff (tip `e0d6084d`); `scummvm-lv/scummvm` built
  2026-10-04 20:45 CDT.
- A full disassembly of the built FLX has 0 `calli 04h 009Ah`. HRODNY's
  `enterConvo()` (class 0x471, 0x0D0F..0x0D45): `push 0205h`, `push 0200h`,
  `push 00F0h`, `push 0204h`, each followed by `push dword [BP+06h]; push
  indirect 02h; calli 04h 00CBh` (Kernel::resetRef), then `push byte 1;
  calli 02h 00D0h` (setAvatarInStasis).

Every bare `enterConvo()` in the compiled sources is in an NPC class member
(SIGRID, ATLI, HRODNY, MYTHRDLG, EZREKAL twice, THORDIS, TYORVI, RAGNAR, and
the unpatched ARAMINA and INGYALD), where `[BP+06]` is `this`. FREE's five
calls are `agent.enterConvo()`, which the parser reads as a method call on
`agent`, not an `EnterConvoStmt` (0 such nodes in FREE's AST), so this
change does not reach FREE.

## C1 and C2: Aramina, Map 41, PASS

Teleport, detour round trip waited out, walk north to (16599, 17256), inside
the garden fence with Aramina at (16671, 16671, 48) beyond it
(`C1-01-aramina-area-before.png`).

**First click** (`Item: 13 (shape 282) calling usecode event 1 @
040D:0991`): she barked "I am sorry, but I can not talk to you now. I must
attend to her ladyship." (`C1-02-aramina-bark.png`). Log from the click:
`I_resetRef item=13` for 0x0205, 0x0200, 0x00F0, 0x0204, then only item 65's
own anim resets (0x00F0). PESANT3 on item 65 (pid 19, `0344:0B99`) was in
the list before and after (`C1-03-after-aramina-bark.png`). This list was
taken after a 300-unit walk, so the absence of GUARDMAN (64) and a loiter on
66 from it is not attributed to the click; the second click below was
measured without moving.

**Second click**, lists taken in place:

| When | Aramina (13) | PESANT3 (65) |
|---|---|---|
| right before | LoiterProcess 427 (0x205), PathfinderProcess 137, ActorAnimProcess 76 | UCProcess 19 (0x205) |
| right after | UCProcess 461 (type 0x209, `040D:0BAF`), ActorBarkNotifyProcess 428 | UCProcess 19 |
| 15 s later | LoiterProcess 175 (0x205) | UCProcess 19 |

Log: `I_resetRef item=13` for 0x0205, 0x0200, 0x00F0, 0x0204 and nothing
else from the conversation (item 65's eight anim resets are its own). Aramina
moved from (16891, 16515) to (16687, 16567) under the new loiter
(`C1-04-aramina-second-click.png`). The 10-02 build killed PESANT3's
activity on the same click.

## C1 and C2: Hrodny with Ingjald as the control, Map 10, PASS

Fresh world. After the detour's round trip both NPCs read `f: 0x2040` with
no process (10-02 finding 3); a walk out and back gave Ingjald (112) loiter
4371. Hrodny (113) stayed without one. With the Avatar at (21300, 7748),
Hrodny was identified by a single click (`Item 113 (class Actor, shape
707)`) and talked to by a double-click (`event 1 @ 0471:0BA4`):

| When | Hrodny (113) | Ingjald (112) | Avatar stasis |
|---|---|---|---|
| before | none | LoiterProcess 4371, PathfinderProcess 4157, ActorAnimProcess 4144 | `false` |
| menu up | UCProcess 3568 (0x209, `0471:0FE2`) | LoiterProcess 4371, PathfinderProcess 3564, ActorAnimProcess 3560 | `true` |
| after **bye** | LoiterProcess 3503 | LoiterProcess 4371, PathfinderProcess 3492, ActorAnimProcess 3489 | `false` |

Menu **What is your name?**, **What do you do?**, **bye**
(`C1-07-hrodny-during.png`); picked the first: "Hrodny, daughter of Ulvar,
I am." (`C3-01-hrodny-name-answer.png`); then **bye** from **What do you
do?**, **bye** (`C3-02-hrodny-second-menu.png`, `C2-01-after-hrodny-bye.png`).
Every resetRef from her `use()` to the end: item 113 for 0x0205, 0x0200,
0x00F0, 0x0204. Afterwards Hrodny moved (21880, 8328) to (21844, 8268), and a
1.2 s walk moved the Avatar from (21300, 7748) to (21468, 7812).

## C3: Ingjald and Thordis, PASS

**Ingjald** (`event 1 @ 0470:08ED`), with Hrodny's new loiter 3503 as the
control: during the menu Ingjald had only UCProcess 2984 (`0470:0D30`) and
Hrodny kept 3503 with fresh pathfinder and anim children; stasis `true`.
Menu **What is your name?**, **What do you do?**, **bye**
(`C3-03-ingjald-menu.png`); picked **What do you do?**: "A brewer, I am.
Make potions for sweet dreams, I do." (`C3-04-ingjald-answer.png`); then
**bye**. After: Ingjald LoiterProcess 2836, moved (20822, 6512) to
(21039, 6360); Hrodny still 3503; stasis `false`; the Avatar walked 400
units (`C3-05-after-ingjald-bye.png`). resetRef: item 112 only, the same
four types.

**Thordis** (106), reached by a same-map teleport to (6344, 6956):
before, Thordis LoiterProcess 1374 and Sigrid (102) LoiterProcess 1368.
Talk (`event 1 @ 046A:0CA7`): during the menu Thordis had UCProcess 1292
(`046A:1759`) and a GumpNotifyProcess; stasis `true`. Menu **How are you
called?**, **What is it you do?**, **What is this place?**, **bye**
(`C3-06-thordis-opens.png`); picked **What is this place?**: "Home of the
Hrodny's, it is. Ours, always this water has been. Keep it safe, we do, from
those dangerous Gunnar's." (`C3-07-thordis-answer.png`); then **bye** from
the shorter menu (`C3-08-thordis-second-menu.png`). After: Thordis
LoiterProcess 1159 with PathfinderProcess 1151 and ActorAnimProcess 1145;
stasis `false`; the Avatar walked 208 units (`C3-09-after-thordis-bye.png`).
resetRef from her `use()`: item 106 only, the four types.

Sigrid's loiter 1368 was gone by the time the menu was up, which looked like
a bystander kill. The log settles it: between the two listings, `Item: 102
(shape 707) calling usecode event 16 @ 0466:01CD` and `I_resetRef item=102
type=0x0205` came before Thordis's `event 1`. That is Sigrid's own
leaveFastArea, and she read `f: 0x40` at (7680, 6100) afterwards. Her
pathfinder 1314 kept running after the loiter died (finding 2).

## C4: log health, PARTIAL

| Session | Content | Lines | Non-existent | stuck | Segmentation | Assertion | Unhandled 154 | resetRef lines | resetRef item=0 | Cycle in paint |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Map 3, Map 41, Aramina | 5,117 | 1 | 0 | 0 | 0 | 0 | 99 | 0 | 0 |
| 2 | Map 3, Map 10, Hrodny, Ingjald, Thordis | 76,682 | 1 | 0 | 0 | 0 | 0 | 47 | 0 | 72,817 |

The non-existent-process line is finding 1. The paint cycles are all shapes
526, 426, and 208 on Map 10 (35,808 `526 -> 426`, plus `208 -> 526` and
`426 -> 208`), the village cycle `docs/playtest-2026-10-01-process-loops.md`
reported as finding 12; this change does not touch FIXED.DAT.

## Findings outside the plan

1. **Devon's farewell logs `Non-existent process PID (0) in implies`.** At
   log line 71 in both sessions, after Devon's (item 2) conversation
   resetRefs (retail code: 0x0205, 0x0200, 0x00F0, 0x0204, then a run of
   0x00F0), on Map 3, before any LV class runs a conversation. It also
   appeared in `docs/playtest-2026-10-04-lb-detour.md` (finding 2). Not
   produced by this change; whether it predates the LV build was not
   established. About four chances in five that it is Devon's code by
   position.
2. **leaveFastArea kills the loiter but not its pathfinder.** Sigrid's
   `resetRef(102, 0x205)` left PathfinderProcess 1314 (notifying a
   DelayProcess that notifies the dead loiter) still walking her outside the
   fast area for over a minute. Same family as 10-02's "the old loiter
   survived and kept walking the NPC outside the fast area"; predates this
   change.
3. **Retail's own conversations already kill only their NPC.** Devon's
   farewell resetRefs name item 2 (and once item 1), in the same 0x205,
   0x200, 0xF0, 0x204 order, which is independent confirmation that the new
   order matches retail.

## Harness anomalies

1. The standstill strike missed Aramina twice and Hrodny once; the hits came
   from a single click to identify the sprite, then a double-click on the
   same pixel.
2. The first Map 41 process comparison straddled a 300-unit walk and is not
   used as evidence; the second was taken in place.
3. The `C1-06-hrodny-menu.png` plate was taken before the menu appeared;
   `C1-07-hrodny-during.png` shows it.

## Disk changes

- `docs/playtest-2026-10-04-convo-kill.md` (this record) and 18 plates in
  `docs/playtest-2026-10-04-convo-kill/`.
- `shared/build/` rebuilt by `tools/build_artifacts.sh` (recorded hashes);
  `shared/data/u8-install/` by `./install_lv.sh`;
  `shared/u8-lv-patched/USECODE/EUSECODE.FLX` synced to `ec3e66fd`.
- Saves and `scummvm.ini` restored and verified; no save was written.
- Scratch only, under
  `/tmp/claude-1000/-home-douglas-projects-lost-vale/3b99e1ce-cfb9-4426-91ac-2a8e98a8eca2/scratchpad/`:
  `cvbak/`, `cvlogs/` (tests, build, install, two session logs), `cvsp/`
  (process-list snapshots as JSON, the full FLX disassembly).
- No tracked file modified; nothing committed; `TODO.md` not touched.
