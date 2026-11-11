# Review of the four pending pieces (A, B, C, D), 3 October 2026

Read-only review of the work awaiting commit on `main`. Nothing was built,
installed, launched, or merged; every claim below rests on `git diff`,
`git show`, `git merge-tree` (read-only form), compiling single classes to
`/tmp`, reading the retail `EUSECODE.FLX.bak` and the pristine `FIXED.DAT`,
and reading the ScummVM fork.

| Piece | Verdict | Blocking fixes |
|---|---|---|
| A, staged on `main` (b943ed2) | **ship** | one stale filename in a comment |
| B, f1a1302 | **ship with fixes** | one in-engine poll cycle before the commit's verification note |
| C, b356e42 | **hold Map 39, ship Map 17 with a shot** | the treeline does not close the drop; Map 17 needs a 640x400 in-engine shot |
| D, 9b2e890 | **ship with fixes** | FLAGS.UNK back to CRLF with the line inside the file; `map_pins.json` regenerated; the once-only guard narrowed to the three observation barks; untracked playtest docs removed before the merge |

## Severity 1: C's Map 39 treeline leaves the drop open on both sides

`build_map_39.py:181-189` places two shape-199 oaks at x 17151 and 17439,
y 20479, z 48. Their half-open boxes cover x (16863, 17439]. The retail
geometry around them, read from the pristine `FIXED.DAT` with globs expanded:

- Every retail solid in x 15800..18800 ends at y 19967 (the Tenebrae wall
  structure: shapes 622, 15, 670, 55, 54, 564 all have y-high 19967). No
  solid box spans any of y 20000..20479.
- The shape-3 grass at y 20479, z 48 runs x 15487..18431 inside that window
  (24 tiles), and the module docstring itself says 11903..20479 overall.
- Nothing exists south of y 20479 down to y 21600.

So between the wall's end (y 19967) and the grass edge (y 20479) there are
512 units of open grass in every direction, and a player who steps 100 units
east or west of the trees reaches the identical 48-unit drop. The void plates
(`_ACCEPT_X = (16000, 18300)`, `build_map_39.py:228-229`) stop at x 16000 and
18300, so the drop beyond them lands on unplated void, the stale-frame case
`.claude/rules/map-geometry.md` describes.

The docstring's "documented lane (17023-17279)" is the 2026-07-03 scan
(`build_map_39.py:81-84`) that the same docstring says the 2026-09-30 scan
superseded. The commit message's "stops the 48-unit drop" and "closes the
climb-over" therefore describe a 576-unit stretch of a 3,000-unit edge. The
trees are a landmark on the straight-south route; they are a barricade of
nothing.

What is right about the half: 199 is 288x288x80 `SI_FIXED|SI_SOLID|SI_DRAW`
(no `SI_LAND`), top at z 128 from a z 48 lane, 80 units, above the 72-unit
jump climb; the rock scatter (`TENEBRAE_LANE_SCATTER`, shape 66, 128x128x40)
sits 181 units north of the tree boxes (rock y-high 20010 against tree y-low
20192), so no two-hop chain; trees stand on zd=0 grass, so nothing is buried;
all z on the 4-lattice; `void_floor()` is called last.

Options, in the order I would take them:

1. Treat the edge for its visible width: a treeline or cliff run along
   y 20479 for x 15487..18431 (the grass this camera can reach from the
   lane), with the void plates' accept window widened to match. That is the
   fix the docstring already argues for and declines on scope grounds.
2. Keep the two trees as dressing and withdraw the "closes the drop" claim
   from the docstring, the commit message, and the `lv_shapes.py:230-237`
   comment, with a TODO naming the open edge.

I would pick 1, because the egg at (17150, 19700) and the apparition 150
units south draw the player exactly here, and the retail design never routed
anyone to this edge.

**Map 17 half of C** (`build_map_17.py:610-653`): the plate moves from
y 5119 to y 5087, which keeps `_cell()`'s anchor in the 4992..5119 band
while the plate's box ends at 5087, below the wall's 5088. The 32-unit
sliver y 5088..5119 is then covered only by the wall itself; `floor_cells()`
quantises by anchor, so `test_map_hygiene`'s ratchet cannot see that sliver
either way. The render evidence is `iso_render.py` only. The map dressing
standard calls for an in-engine 640x400 shot before this is done, and none
exists for either half of C.

## Severity 2: D rewrites every line ending of lv-patched/FLAGS.UNK

`git diff --stat 81deebd 9b2e890` shows `FLAGS.UNK | 1653 +++---`; with `-w`
it is one inserted line. The cause: the file had 825 CR bytes at 81deebd (and
at D's first commit 69438b9), and 0 at 9b2e890. The recovered original
(`shared/data/lv-usecode/UNK files/UNK/FLAGS.UNK`, 761 lines) is CRLF with a
trailing 0x1A, and the two prior patches kept CRLF and inserted before the
0x1A. D converted the whole file to LF and appended `globalflag
crackHintGiven;` after the 0x1A (`FLAGS.UNK:827`).

`.claude/rules/recovered-source-is-evidence.md` requires a byte-copy plus one
minimal fix whose diff reads in one screen, and the file's own header
(`FLAGS.UNK:38`) still says "No other byte of the 1994 file is changed." The
lexer does tokenise the appended line (I tokenised D's copy:
`crackHintGiven` is present as an IDENT, and the 0x1A produces no token), so
the build is unaffected; this is a rule and provenance defect, and the
1,653-line diff hides the one real change.

The fix is restoring CRLF, inserting the declaration before the 0x1A as the
`endgameStarted` patch did, extending the header's fix list, and adding the
inventory line that `lv-patched-inventory.md:82-85` lacks for both
`endgameStarted` and `crackHintGiven`.

## Severity 2: D changes FIXED.DAT without regenerating map_pins.json

D's `build_breach_rubble()` adds 14 placed items and one hall rock to Map 18
(`build_map_18.py:124-176`, `:497-506`), so the built `FIXED.DAT` hash moves.
D's diff does not touch `agents/map-populator/src/map_pins.json`;
`test_map_pins_fresh.py:66-70` fails whenever the committed
`fixed_sha256_prefix` differs from the built file, so it fails on a fresh
build of D. Regenerating with
`python3 agents/map-populator/src/derive_map_pins.py` after the last map
merge clears it (C also moves the prefix, to `fa6384b8`).

## Severity 2: D's once-only guard also silences the potion nudge

`CRACKHNT.UNK:89-93` returns on `crackHintGiven` before the three
observation barks, and the "stronger nudge" at `:107-117` (fires when a
frame-8 `TypePotion` is in the pack) sits below them. A player who first
reaches the wall without Hrodny's potions, then fetches them and comes back,
never hears "Hrodny's dark potions are in my pack." Before D, the egg
re-hatched on each Map 18 entry and the nudge played on the return trip.

The fix is a guard around the three observation barks only, with the potion
search running on every hatch while `templeOpen` is clear. The regrow re-hatch
(`docs/reviews/2026-09-30-four-anomalies.md` finding 3) then repeats at
most the one-line nudge, which is the useful reminder at that moment.

The three barks themselves are sequential: `_gen_bark`
(`u8c_codegen.py:1878-1909`) emits `push retval; implies; pop temp; suspend`
per bark, so each waits for the previous gump.

## Severity 3: D merge is refused until two untracked paths are removed

`main`'s working tree holds untracked `docs/playtest-2026-10-01-breach-rubble.md`
and `docs/playtest-2026-10-01-breach-rubble/` (36 files). 9b2e890 adds the
same paths. `git merge` refuses to overwrite untracked files. I compared
every one: the markdown is byte-identical (`cmp`) and all 36 PNG blob hashes
equal D's. Deleting the untracked copies first is safe and loses nothing.

## Severity 3: the working-tree rehash reflects A alone

Unstaged `shared/build/ARTIFACTS.sha256` and `build_scummvm.sh:54-55`
(`LV_MD5 4f47de88...`, `LV_SIZE 1505828`) record the EUSECODE.FLX that A
alone produces. B (ENDGAME, EZREKAL) and D (CRACKHNT, FLAGS) change
EUSECODE; C and D change FIXED. The moment any of them merges, both files
are stale and the detection entry stops matching. One `/artifact-rehash`
after the last merge is the right number. Committing A's rehash now is
harmless as long as that is understood.

The working tree also holds unrelated edits to `CLAUDE.md` (a "Verification
and effort" section) and `.claude/settings.json` (two permissions). They
belong in their own commit.

## A: correct, retail-faithful, no scene it breaks

**killProcess** (`lv-patched/FREE.UNK:839-841`): `resetRef(r,ptype)` compiles
LVFREE to `5A00 3F08 3F06 0F04CB00 6EFC 50`, which is retail FREE class
0x0581 offset 2A56 byte for byte (`test_killprocess_npc_ref_cells.py:84-86`
asserts both). The EUSECODE size delta is +89 bytes, consistent with ~30
three-byte `push 32; mul` insertions, a dozen word-to-byte NPC pushes, and
the 8-byte body.

**NPC class name in expression position** (`u8c_codegen.py:2497-2510`): the
method-call path (`_gen_item_ptr`, `:2358-2362`) already pushed
`SEG_OBJ<<16 | npcnum`, so `Atli.bark()` and `Atli.teleport()` were right
before A. A changes only the 2-byte expression path: `within N cells of X`,
`X:Referent`, and `X.referent` (MemberAccess falls through to
`_gen_expression(expr.obj)`, `:2606`). Retail agreement for the cross-NPC
form, which the shipped test does not cover: retail ARAMINA (0x040D) compiles
its source `getDirToItem(Mordea:Referent)` (`ARAMINA.UNK:496`) as `push byte
+7; push dword [BP+06]; calli 005A` (offset 0D15), and has zero `push 0407h`,
`push 0419h`, or `push 0412h` for Mordea, Xavier, or Rhian. A lexer scan of
every compiled file for NPC class names in expression position found 39
sites (ARAMINA, FREE, METHOD, PLNTST, TESTPLAN, TEMPLENT); every one is an
item reference (`:Referent` cast, area-search centre, or `= Npc` comparison
against an objid), so none wanted the class id. TEMPLENT's `first` is a
declared local and resolves before the class table.

**`within N cells` x32** (`u8c_codegen.py:1703-1711`, `u8c_parser.py:632`):
retail ARAMINA has 8 `push 32; mul` for its 8 `cells` sites; retail AVATAR
has 4 for 4; retail FREE has 2 for FREE.UNK's 2 (`:281` with a variable
range, `:1295`). LVFREE compiles 1 because `:1295`'s foreach is lost to a
pre-existing parse error at `:1296` (`Expected LBRACE, got COLON`), which A
neither causes nor fixes. The one variable range, `findNearest(range, t, f)`
at `FREE.UNK:274-281`, has no caller in `lv-new/`, `lv-patched/`, or
`LOST VALE/`, and its foreach condition already compiles as shape 0 (the
`unknown type 't'` warning at `:280`), so no restoration-era caller can have
passed world units. No `cells` literal exceeds 1023, so no product
overflows sint16 (largest: EAPUZL 140, PLNTST 100). Sites written without
`cells` (`within 2000 of referent` in AOSCENE, TEMPLENT, CRACKHNT, COLPUZZL,
LBSCENE, LORDBRIT) are untouched (`u8c_parser.py:632` keys on the token).

**Newly live kills, scene by scene.** `Kernel::killProcesses`
(`kernel.cpp:309-321`) matches `_itemNum` and exact `_type`; a usecode event
process is type 0 (`process.h:44`) unless a `[[PT_x, ...]]` pragma emits
`set info`. So:

- SHADES.UNK:135-137, `PT_ACTIVITY` (0x205) on Atli, Thordis, Ezrekal: kills
  their LoiterProcess and their `[[PT_ACTIVITY, referent]]` schedule
  processes so they hold position for the ceremony. 1994 intent; the scene
  then drives them with explicit anims and `send*Home` processes.
- SHADES.UNK:200 and :267, `PT_BARK` (0x200) on the egg: kills `squabble()`,
  declared `[[PT_BARK, referent]]` (`:72`), when the Avatar intervenes.
  Bark gumps' notify processes belong to the barking NPC items, so nothing
  else on the egg matches.
- SHADES.UNK:480, `PT_DEFAULT` (1) on the egg: kills `shadeTalk`, declared
  `[[PT_DEFAULT, referent]]` (`:73`). `hatch()` has no pragma and is type 0,
  so it does not kill itself; the kneel-and-forgive beats after `:480` run.
- PLNTST.UNK:85/:91: Atli and Thordis stop loitering at the Passage Test
  (fix 2 makes the referent valid; fix 1 makes the call do anything).
- MAGNET.UNK:564, `PT_UNKHATCH`: not in `PT_CONSTANTS`, compiles to `push 0`
  with a warning, so `killMagnet` kills type-0 processes on the egg, which
  is its own hatch loop on `leaveFastArea`. That is the 1994 intent and was
  a no-op until now; worth one in-engine look that leaving and re-entering
  the obelisk's area behaves.
- NPC `use()` sites (EZREKAL:237, RAGNAR:190, HRODNY:185, ATLI:388,
  THORDIS:276, TYORVI:134, SIGRID:87): kill the NPC's own schedule on
  conversation start, as retail NPC classes do; the hourly scheduler
  restarts it.

**Sim** (`u8c_sim.py:651-653`): `mul` added; `area_search` (`:216-225`)
treats the range as world units, so sim searches with `cells` now cover 32x
the area. No committed sim test exercises a `cells` search in a way that
depends on the radius (lv-new has none; PLNTST's `within 100 cells` is the
only lv-patched site a test could reach), and A's verifier run of the estate
is the check.

**One nit**: `u8c_codegen.py:2507` cites `test_npc_ref_cells.py`; the file is
`test_killprocess_npc_ref_cells.py`.

## B: logic right, tag safe, unaffected by A, unverified in-engine

**Refill rule** (`ENDGAME.UNK:174-407`): per frame, `found=0`; inside the
tagged bag (`within container bag.referent`, recursive) each stack gets
`q<20 → q+5`, `20≤q<25 → 25`, else untouched; only when nothing of that frame
is in the bag does a read-only search across `container Avatar` run, and
only when that is also empty does it `create`, `setQuantity(5)`,
`pop(bag.referent)`. Nothing outside the bag is written. The compiled class
(2,373 bytes with A's compiler) has no `call 0000h`, the local-routine trap
`.claude/rules/usecode-local-routines.md` names, and `if bag` compiles to
`push [BP-08h]; jne` on the 2-byte referent.

**Tag** (`EZREKAL.UNK:2132`, `bag.setQ(1)`): retail class 637 (TypeBag)
calls only `bark`, `getStatus`, `closeGump`, `openGump`, never `getQ` or
`getQuality`. RAGNAR.UNK:963 and HRODNY.UNK:1171 create TypeBag with quality
0 and never set it (HRODNY:1173's `setQuality(20)` is the key). MAGNET.UNK's
"endless bag" search (`:320`) is `TypeBagOReagents`, shape 225, a different
shape. So `getQ() = 1` matches exactly one bag in the game.

**Interaction with A**: A changes codegen only for `cells` ranges and NPC
class names in expression position. ENDGAME uses `within container` and
`Avatar` only, so its bytes are identical under A; `test_uc_eggs.py:341`
reads `TOPUP_OFFSET` from the recorded spawn in any case. `git merge-tree`
reports `u8c_sim.py` and `lv-patched-inventory.md` changed in both A and B
with no conflict hunks (A adds the opcode at `:651`; B adds `SimItem`
fields at `:70-130` and intrinsic stubs at `:1073-1115`).

**Sim stubs** (`u8c_sim.py:1073-1115`): the family gates match what B's
comments quote from `item.cpp` (`getQuantity`/`setQuantity` for
`SF_QUANTITY|SF_REAGENT`, `setQuality` for any family but `SF_GENERIC`,
`getQ`/`setQ` ungated). I did not re-open `item.cpp` for these.

**Residual, named by B itself** (`test_uc_eggs.py:482-496`): a whole stack
dropped on the ground reads as "truly out" and is recreated at 5 per poll.
That is Douglas's 2026-10-02 decision, bounded at 5 per frame per poll.

**Gap**: the recreate path (`create` + `setQuantity(5)` + `pop` into a bag
inside the backpack) and the 5-per-poll clamp exist only in the sim. The
old rule was observed in ScummVM; this one has not been. EGGENDGAME is in
`QUEST_CRITICAL_CLASSES`, so one in-engine poll cycle (split a stack, wait
one poll, read quantities; empty a frame, wait, see 5 appear in the bag)
belongs in the commit's verification note.

## D: rubble geometry sound, in-engine shots still owed

`build_breach_rubble()` (`build_map_18.py:124-176`): shape 6 is 128x128x0
`SI_FIXED|SI_SOLID|SI_LAND` with neither `SI_DRAW` nor `SI_OCCL` (TYPEFLAG
read), so it overlays the floor per `.claude/rules/map-geometry.md`'s flat
tile rule; 524 is 96x96x8 and 526 is 64x64x16, both `SI_LAND`, tops at z 8
and 16 on the 4-lattice, far below the 48-unit climb threshold. Every pile
and chip has `y - depth >= 6143` (lowest: 2975-6231 chip, north edge 6167)
and sits outside x 2700..2880, as the docstring argues. The hall rock at
(2975, 5887) has box x (2911, 2975], clear of the 2848..2879 aperture.

The 2026-10-01 playtest verified the previous layout (four gravel tiles,
two piles) rendering and paint-cycle free; the nine-tile staggered layout
and the hall rock in 9b2e890 are not yet in-engine verified, as the commit
says. The map dressing standard wants the 640x400 shot before this is done.

**Manifest pin**: `crackHintGiven` at bit 1829, `next_free.global_bit` 1830
(`lv_manifest.json:656-659`, `:3229`). A, B, and C add no flag or class pins,
so no cursor collision exists among the four.

## Integration

Pairwise `git merge-tree` (read-only form):

| Pair | Common files | Result |
|---|---|---|
| A, B (base db28de4) | `u8c_sim.py`, `lv-patched-inventory.md` | clean |
| A, C | none | clean |
| A, D (base 81deebd) | none | clean |
| B, C (base db28de4) | `map_pins.json` | **conflict** on the two header lines (`generated`, `fixed_sha256_prefix`) |
| B, D | `lv-patched-inventory.md` | clean |
| C, D | none | clean (both move FIXED.DAT) |

Order is free. I would merge A (staged), then D, then B, then C, because
C's `map_pins.json` is the only conflict and regenerating the file after the
last map change resolves it, and I would run `tools/build_artifacts.sh`,
`derive_map_pins.py`, `/artifact-rehash`, and `tools/run_all_tests.sh` once
at the end, followed by the in-engine checks above (B's poll cycle, C's
Map 17 shot, D's rubble shot, one look at the obelisk under A's live
`killMagnet`).

## Not reviewed

TESTPLAN.UNK and METHOD.UNK sites are reported from the lexer scan; whether
either compiles into the shipped FLX was not re-derived. The `Map 39` grass
extent west of x 15487 and east of x 18431 was not scanned (window limit).
