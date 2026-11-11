# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fan restoration of *Ultima 8: The Lost Vale* — a cancelled 1994 expansion to Ultima 8: Pagan. Target runtime: ScummVM (which absorbed the Pentagram U8 engine). The user must own a legal copy of Ultima 8.

The project uses a **multi-agent coordinator model**. Each agent has its own directory under `agents/`, with a `MEMORY.md` (agent state), `docs/` (design documents, devlogs), and `src/` (Python tools).

## Which document is authoritative

**Live status lives in `TODO.md`** (H10). There is no root `MEMORY.md` — it moved to `docs/MEMORY.md` in commit 5cec802 (2026-03-28) and froze there; that file is now an **archived Phase 0-3 snapshot**, not a dashboard. `PLAN.md` is the strategic roadmap, and `docs/reviews/2026-07-19-improvement-plan.md` is the review-driven work queue. `HANDOFF.md` is the session-to-session baton and is deliberately short — its pre-2026-08-11 log is archived under `docs/archive/`. The agent `MEMORY.md` files are per-agent history and are mostly frozen at each agent's completion date — check the date stamp at the top before trusting one.

`docs/id-legend.md` decodes every `C*`/`H*`/`M*`/`L*`/`P*`/`DD-*` code these docs cite. Consult it before acting on one: `DD-005` and bare `M1`-`M4` each mean two different things depending on which file you read them in.

Standing per-area constraints live in `.claude/rules/` and load when you open a matching file. Occasional procedures are skills: `/artifact-rehash`, `/playtest`, `/build-and-run`.

## Common Commands

```bash
tools/integrate.sh   # after any merge touching usecode/maps/art/fork: build, pins, engine, install, harness, tests (/integrate)

# Build everything and verify against the canonical hashes. This is the
# supported build: eight steps in a load-bearing order (TYPEFLAG → U8SHAPES
# wood walls → U8SHAPES+TYPEFLAG Tiny Tar → U8SHAPES+TYPEFLAG Zealan gods →
# U8SHAPES+TYPEFLAG art-track static props → U8SHAPES+TYPEFLAG+ANIM.DAT
# actors: Tiny Tar body 867, Water Zombie 872, Harpie 873 → EUSECODE →
# FIXED). Running the individual builders by hand skips the custom-art steps
# and the hash check.
tools/build_artifacts.sh

# Rebuild EUSECODE.FLX alone — full mode (requires patched ScummVM). Exits
# nonzero on any compile failure (outside the documented allowlist), a
# skipped Mythran patch, or a missing quest-critical class (M0.4).
python3 agents/usecode-compiler/src/build_eusecode.py --full

# --stealth is RETIRED (DD-006b, M0.3): it can't carry the expansion (new
# classes get skipped past FLX entry 610; the packer's reclaim-before-place
# allocator corrupts the FLX on oversized replacements like Mythran).
# Running it prints a retirement notice and exits nonzero. Use --full.

# Rebuild FIXED.DAT alone (all 7 maps + base game maps)
python3 agents/map-populator/src/build_all_maps.py

# Build patched ScummVM (adds Lost Vale detection entry)
./build_scummvm.sh

# Install + launch (auto-detects patched ScummVM at scummvm-lv/scummvm)
./install_lv.sh --run

# Run the whole test estate (discovers agents/*/src/test_*.py, aggregates
# exit codes, ~7s). This is what clean-room Step 6 calls. Add -v to stream
# output, -l to list, or a substring to filter (e.g. `run_all_tests.sh map`).
tools/run_all_tests.sh

# Round-trip validation (assembler integrity: disassemble → reassemble → byte-compare)
python3 agents/usecode-compiler/src/test_roundtrip.py

# Test all LV files parse successfully
python3 agents/usecode-compiler/src/test_parser_all.py

# Compile a single .UNK file
python3 -c "
import sys; sys.path.insert(0, 'agents/usecode-compiler/src')
from u8c_parser import parse_file
from u8c_codegen import CodeGenerator
from u8c_symbols import create_symbol_table
ast = parse_file('path/to/FILE.UNK')
data = CodeGenerator(create_symbol_table()).generate_class(ast)
print(f'{len(data)} bytes')
"
```

## Build artifacts and game data

The five merged artifacts under `shared/build/` (`TYPEFLAG.DAT`, `U8SHAPES.FLX`, `ANIM.DAT`, `EUSECODE.FLX`, `FIXED.DAT`) are **not tracked in git** — they fuse our work with Origin-copyrighted bytes (M22). A fresh clone has none of them; build them with `tools/build_artifacts.sh`. What *is* tracked is `ARTIFACTS.sha256` (canonical hashes) and `lv_manifest.json` (pinned IDs). Details and the never-renumber rule: `.claude/rules/build-artifacts.md`.

Game data is gitignored and must be provided: `shared/data/u8-install/` (extracted from the GOG `.pkg`), `shared/data/lv-usecode/` (the recovered 1994 source), and `gog/` (raw downloads, READ-ONLY).

## Technical Constraints

- **All bytecode is little-endian.** The U8 VM is a stack-based machine with 16-bit default word size.
- **Jump offsets are sint16** (-32768..32767). Large classes (>32KB bytecode) need trampoline relay chains — handled automatically by `resolve_fixups()` in `u8c_codegen.py`.
- **Class IDs**: Base game 0x0000–0x0203 (516 classes). New LV classes start at 0x0204+. Modified base NPCs (11 classes from `LOST VALE/`) replace their existing class IDs.
- **Teleport IDs**: Base game uses 0–105. LV uses 200–213 (14 pairs).
- **Map slots**: Base game uses 42 of 256 slots. LV adds 9, 10, 11, 13, 17, 18, and modifies Map 8 and Map 39 (Tenebrae — the quest step 1 Lord British trigger, `build_map_39.py`). That file also carries an opt-in Map 3 test path that is never on by default.
- **Two shape-ID tables exist and disagree.** The map builders' `SHAPE_*` constants are the source of truth; `TYPE_SHAPES` in `u8c_symbols.py` is a separate, partly-wrong legacy table. See `.claude/rules/shape-ids.md` before trusting or editing either.
- **Do not modify the disassembler.** It is the reference implementation the assembler round-trips against — changing it deletes the evidence that the assembler encodes correctly. One documented, narrowly scoped exception exists: `.claude/rules/disassembler-is-frozen.md`.
- **The recovered 1994 source is read-only evidence.** Fixes go in `agents/usecode-compiler/src/lv-patched/` as a byte-copy plus one minimal documented change. See `.claude/rules/recovered-source-is-evidence.md`; per-file inventory in `agents/usecode-compiler/docs/lv-patched-inventory.md`.
- **U8 item boxes are half-open**, and the cell flood cannot size a one-body-width aperture. See `.claude/rules/map-geometry.md` — this shipped a sealed route once.
- Each agent copies `u8_flex.py` to its own `src/` directory. The canonical version is in `agents/usecode-disasm/src/`.

## The ScummVM fork

Engine changes live in `scummvm-lv-console/` on local branch **`lost-vale`**
(tip `e0d6084d`). Its only git remote is upstream scummvm.org, so **there is
nowhere to push it** — the branch is just an anchor. What actually travels is
`tools/scummvm-patches/0001-lost-vale-engine.patch`, applied by
`build_scummvm.sh` over the pinned base `01bd8879`; a clean clone rebuilds the
whole engine from it. Regenerate it whenever the fork gains a commit:

```bash
cd scummvm-lv-console
git diff 01bd88796f47b21ce8e985a94a6c284439b6f032 HEAD -- engines/ \
  ':!engines/ultima/detection_tables.h' > ../tools/scummvm-patches/0001-lost-vale-engine.patch
```

(`detection_tables.h` is excluded because `build_eusecode.py` generates it.)
Nothing tests that the patch still equals the fork diff — it was found
carrying 3 of 7 changed files on 2026-08-18, so a fresh clone had been
building without the loiter leash and the AskGump dispatch.

## Coordination Protocol

- Each agent works in `agents/<name>/` and does not modify other agents' directories.
- Shared outputs go to `shared/corpus/`, `shared/data/`, `shared/maps/`, or `shared/build/`.
- `TODO.md` is the live status tracker — update it after significant milestones. A checkbox flips only with a verification note: date plus what was run in ScummVM.
- **Work happens on `main`, and it is now the only branch.** The multi-agent
  fan-out is over: `agent/corpus-builder`, `agent/map-builder`,
  `agent/npc-dialogue`, `agent/usecode-disasm` and `port/linux-kaga` were
  deleted from the remote on 2026-08-19, and `agent/village-pipeline` — the
  last of them, held back in case another machine tracked it — on
  2026-09-01, each verified a fully-merged ancestor of the tip first. The
  GitHub default branch is `main`, so the old stale-default trap (fresh
  clones landing on a Phase-3 commit) is gone: a clone lands on `main` at
  the tip. `git ls-remote --heads origin` should show exactly one ref.
- When launching subagents, use `isolation: "worktree"` for repo-level isolation.

## Known Limitations

- **2 of the 53 source files the build compiles fail** (51 succeed as of `WZOMBIE.UNK` and `HARPIE.UNK` on 2026-10-11, 49 of 51 as of `REAPPLY.UNK` on 2026-10-10, 48 of 50 as of `ELIXIR.UNK` on 2026-10-09; this bullet read 46/48 then, already one stale, and 45/47 until `ELMCOLMN.UNK` landed on 2026-09-24 and 45/43 before `MSGSCRL.UNK` on 2026-09-21, so re-read the build's own Compilation Report before quoting it), from source-level defects in the original 1994 snapshot: `EALOGO.UNK` (truncated block comment) and `TJORVI.UNK` (unterminated string — an early draft of TYORVI, which compiles fine). Both are on `DEV_ALLOWLIST`, so they do not fail the build.
- `enterConvo()`/`exitConvo()` compile to retail's own call form since 2026-10-09: a spawn of retail METHOD `Npc::enterConvo` (0x57C 0BCF) / `Npc::exitConvo` (0x57C 1090), byte for byte as retail NPCs call them, and nothing after it (`test_codegen_retail_forms.py` section 26). Retail exitConvo restarts the NPC with the `Item::enterFastArea()` intrinsic, which upstream ScummVM skips for an NPC already in the fast area; the fork's `Item::I_enterFastArea` (scummvm-lv-console `dccab1e7`) now fires the NPC's own enterFastArea event as U8.EXE 10d8:2577 does, so retail and LV NPCs alike resume their route or loiter after a talk. A build without that fork commit leaves every talked-to NPC with no activity process (`Non-existent process PID (0) in implies` at each farewell). A class with no enterFastArea handler gets no activity back unless its source says so, as retail's THURGIST and the 1994 ZCHILD write `exitConvo(); cSetActivity(ACT_LOITER);`.
- **Most new art assets are still base-game placeholders** (Shield halves), but the **three Zealan gods, the Magnetic Obelisk, the cloud floor, the Sacred Rock, the Message Scroll, Tyorvi's elixir, the Water Zombie and the Harpie are not**: shape 860 is custom art, injected as step 4 of `tools/build_artifacts.sh` and placed by `build_map_18.py` at the Inner Sanctum's ceremony triangle (verified in ScummVM 2026-09-13, `docs/playtest-2026-09-13-god-placement.md`); shapes 861 (the obelisk), 862 (the cloud tile, a flat ground tile that tessellates by construction — `tools/art/cloud_tile.py`), 863 (the Sacred Rock, Map 10's ninth standing stone), 864 (the Message Scroll, the track's first CARRYABLE prop: donor 159 gives it no `SI_FIXED` and `SF_QUALITY`, and `lv-new/MSGSCRL.UNK` is its class at 864, so a double-click reads Odion's letter in the scroll gump), 865 (Map 11's four elemental pillars, the track's first multi-frame row: frame = element, `lv-new/ELMCOLMN.UNK` is its class, and `TYPE_SHAPES['TypeElementalColumn']` must equal it because `COLPUZZL` compiles that number into the search that destroys a pillar) and 866 (their receptacles, whose `use()` dispatches off npcnum 120 whatever the shape) are injected by the table-driven step 5 (`lv_art_props.py`) that every static prop shares, and placed by `build_map_17.py`, `build_map_10.py` and `build_map_11.py`. Shape 868 (Tyorvi's elixir, 2026-10-09) is a row in the same step that recolours the base blood vial instead of reading a PNG; it is never placed — `TYPE_SHAPES['TypeBottle']` resolves to it for EZREKAL's hand-over and TYORVI's drink, and `lv-new/ELIXIR.UNK` is its class. Shapes 872 (the Water Zombie: the ghoul 142's frames recoloured) and 873 (the Harpie: drawn new in the torax 120's layout) are ACTORS, built by `lv_monsters.py` in step 6 with their donors' TYPEFLAG rows and `ANIM.DAT` tables (2026-10-11, `docs/art-track.md` contract 9); the Lake's and the harpie zone's eggs hatch them, `lv-new/WZOMBIE.UNK` and `HARPIE.UNK` are their classes, and their stats are `u8monsters.ini` rows that `install_lv.sh` writes into the game directory — a monster with no row hatches with no hit points. `tools/png2shape.py` drives PNG → quantize → encode → validate → inject → TYPEFLAG in one command; `agents/map-populator/src/lv_god_statues.py` is the multi-frame version of that. The queue and the per-item integration contracts live in `docs/art-track.md`; the authoritative placeholder inventory is `agents/map-populator/docs/art-placeholder-audit-2026-07-19.md`.
- One recovered-source caution: several 1994 dialogue defects are fixed in `lv-patched/` copies rather than the snapshot — check `agents/usecode-compiler/docs/lv-patched-inventory.md` before concluding a defect you found in `shared/data/lv-usecode/` still ships. (This bullet used to claim Ragnar's dead "I have no fight with you" option was unfixed; the handler was restored in `lv-patched/RAGNAR.UNK` on 2026-07-04 — DD-008 — and the claim survived here for a month. The recovered files are also treated as binary by grep — high-bit German characters — so search them with `grep -a`.)
