#!/usr/bin/env python3
"""
build_eusecode.py — Build the final EUSECODE.FLX for the Lost Vale.

Process:
1. Start with base game EUSECODE.FLX (516 named classes, 1431 total slots)
2. Load the M0.6 id/flag manifest (shared/build/lv_manifest.json), or
   bootstrap one if absent
3. Compile all LV source files
4. Replace modified base classes with LV versions
5. Add new LV classes at manifest-pinned ids, or the next free id above
   the base game's highest used class id (1431+; see NEW_CLASS_START)
6. Add new dialogue classes
7. Update name table
8. Write to shared/build/EUSECODE.FLX, appending any newly-allocated
   manifest pins

Build mode: --full is the only supported mode. It requires the patched
scummvm-lv detection table (see build_scummvm.sh) and carries the full
expansion with no class-count or size constraints.

Stealth mode is retired (DD-006 option b, M0.3). It preserved the base
game's original md5-5000 hash and file size so an unmodified FLX would pass
stock ScummVM's detection check, but it cannot carry the expansion: any new
class past FLX entry 610 that doesn't fit in reclaimed space from a
same-slot replacement is silently skipped, and the packer's
reclaim-before-place allocator corrupts the FLX outright on oversized
replacement classes (Mythran being the case that actually hits this).
`write_stealth()` stays in u8_flx_packer.py as documentation of the
md5-5000 window reverse-engineering finding, but this driver no longer
calls it. Passing --stealth prints a retirement notice and exits nonzero
without loading or writing anything.

Build failure gating (M0.4): this script exits nonzero, with the failure
reasons printed one per line at the end of output, when any of the
following hold:
  1. A file in lv-new/ fails to compile.
  2. A file in shared/data/lv-usecode/LOST VALE/ or in lv-patched/
     (versioned patched 1994 sources, highest precedence — see
     LV_PATCHED below) fails to compile.
  3. A file in shared/data/lv-usecode/UNK files/UNK/ fails to compile,
     unless it is in DEV_ALLOWLIST below (documented 1994 source defects).
  4. The Mythran patch step (5b) has to SKIP instead of patching.
  5. A class in QUEST_CRITICAL_CLASSES is absent from the successful
     compilation results.
  6. (M0.6) The manifest is internally inconsistent (overlapping flag bit
     pins, cross-group class id collisions), a pinned class id cannot be
     honored (collides with a base-game id, an LV NPC id, or another
     class assigned this build), a pinned flag width disagrees with the
     source declaration, or an unpinned allocation landed inside a pinned
     bit range. There is no re-pin code path; fixing a pin means a human
     edits shared/build/lv_manifest.json with a written justification.
  7. (post-write verify, found during ATLI relay-splice bug) Any class
     this build REPLACED or ADDED disassembles (via the reference
     disassembler) to an unknown-opcode fallback ("db" line) or a global
     bit reference >= 4096 (the engine's BitSet capacity). Both are
     symptoms of a trampoline/relay block landing mid-instruction — see
     BytecodeEmitter._instr_starts / _find_safe_insertion() in
     u8c_codegen.py. Untouched base-game classes are not re-verified.
A build with none of the above prints the same summary as before and
exits 0.
"""

import sys
import os
import glob
import hashlib
import re
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from u8_flex import UsecodeFlexArchive
from u8_flx_packer import UsecodeFlxPacker
from u8c_driver import Driver
from u8c_symbols import create_symbol_table, LV_NPC_SHAPES
from patch_mythran import patch_mythran_class, _event_offset
import lv_manifest
import struct

# Reference disassembler — imported read-only via sys.path, same convention
# test_roundtrip.py uses. Do NOT modify u8_usecode_disasm.py; it is the
# format-of-record the assembler round-trips against. Used only by the
# post-write verification gate (Gate 6) below.
_disasm_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            '..', '..', 'usecode-disasm', 'src')
sys.path.insert(0, _disasm_dir)
from u8_usecode_disasm import UsecodeDisassembler


# ─── Configuration ──────────────────────────────────────────────────────────

# Path resolution: everything is resolved RELATIVE TO THIS FILE (repo root
# three levels up), same convention as lv_manifest.py, so a build run from a
# worktree checkout reads/writes that worktree's shared/, never the main
# checkout's.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, '..', '..', '..'))

BASE_FLX = os.path.join(REPO_ROOT, 'shared', 'data', 'USECODE.FLX')
OUTPUT_DIR = os.path.join(REPO_ROOT, 'shared', 'build')
OUTPUT_FLX = os.path.join(OUTPUT_DIR, 'EUSECODE.FLX')

# LV source directories
LV_FINAL = os.path.join(REPO_ROOT, 'shared', 'data', 'lv-usecode', 'LOST VALE')
LV_DEV = os.path.join(REPO_ROOT, 'shared', 'data', 'lv-usecode', 'UNK files', 'UNK')
LV_NEW = os.path.join(_THIS_DIR, 'lv-new')
# Patched 1994 sources (step-7 repair, 2026-07-04). The recovered tree
# under shared/data/lv-usecode/ is gitignored, so a 1994 file that needs
# a source-level fix (e.g. RAGNAR.UNK's dead "I have no fight with you."
# ask and its menu/case string mismatches) gets a VERSIONED copy here,
# with every change documented in a header comment block. This tier has
# the HIGHEST precedence: a basename present here overrides both
# LOST VALE/ and UNK files/UNK/, the same skip-by-basename mechanism the
# LOST-VALE-over-dev preference uses (see final_basenames below).
LV_PATCHED = os.path.join(_THIS_DIR, 'lv-patched')

# Known base game classes that are MODIFIED by LV
# These get their existing class IDs from the base game
MODIFIED_BASE_CLASSES = {
    'AVATAR', 'FREE', 'FLAGS', 'METHOD', 'AIRSPEL',
}

# CORRECTED 2026-07-03 (uses-imports work): of MODIFIED_BASE_CLASSES, only
# AVATAR declares a `class`/`npcclass` header (ast.class_decl); FREE,
# FLAGS, METHOD, and AIRSPEL are routine-library-style files with NO class
# declaration at all. The class-id assignment loop below used to key
# entirely off `result.class_name` (empty for all four), so
# `existing_id = symbols.get_class_id(class_name)` was always None and
# `elif class_name:` was always false too — these four classes' compiled
# bytecode was silently DROPPED, never written to the FLX. FREE was NOT
# actually replacing base class 0x581 despite CLAUDE.md/wiring.md saying
# so; base 0x581 in every build to date is untouched 1994 bytecode. Fixed
# below by falling back to the file's own basename (matching
# _compiled_identity()'s existing QUEST_CRITICAL_CLASSES fallback) for
# exactly this set. Scoped to MODIFIED_BASE_CLASSES specifically — NOT
# applied to every class-less dev file (CHANGTAR, ORLOK1, PSCEND,
# ZZVFLAGS also have no class_decl) since those aren't part of this work
# and newly adding them as classes is an unaudited behavior change
# outside its scope.
#
# UNSAFE_TO_REPLACE (2026-07-03, coordinator review of the fix above):
# the silent-drop bug was accidentally PROTECTING the base game. A scan of
# retail bytecode (0x11 call + 0x57 spawn operands across every class in
# shared/data/USECODE.FLX; coordinator's counts re-verified independently
# in this worktree with the reference disassembler) counts retail classes
# calling into each MODIFIED_BASE_CLASSES id at HARDCODED offsets:
#
#     FREE    (0x581): 190 retail caller classes
#     METHOD  (0x57C): 126 retail caller classes
#     AIRSPEL (0x596):   5 retail caller classes
#     FLAGS   (0x582):   0
#     AVATAR  (0x401):   0
#
# Our compiler necessarily lays code out differently than the 1994 one, so
# replacing any of the first three would corrupt every one of those
# callers' call sites (the 1994 team could replace FREE because they
# recompiled all 516+ classes consistently; we cannot). Members of this
# set are therefore NEVER written over their retail class id — their
# compiled results stay dropped, now deliberately and documented, gated on
# the M1 bytecode-alignment audit. Consequences:
#   - FREE: compiled under the NEW manifest-pinned class name LVFREE
#     instead (PROVIDER_CLASS_NAMES below); LV consumers' `uses "free"`
#     calls target LVFREE, retail 0x581 ships byte-identical. This also
#     keeps _gen_wait()'s hardcoded retail spawn target 0x581:0x1C19
#     (u8c_codegen.py) valid — replacing 0x581 would have broken every
#     compiled wait() too.
#   - METHOD: its callables are Item::method() members (out of the
#     uses-import feature's scope anyway); nothing LV-side targets a
#     recompiled METHOD yet.
#   - AIRSPEL: the LV source's intended air-spell behavior changes are
#     DEFERRED — a known, documented gap until the M1 audit decides how
#     to carry them (candidate: the Mythran append-and-repoint wrapper
#     pattern, patch_mythran.py, which leaves retail call sites intact).
# AVATAR (0 retail callers) keeps its replacement: already-shipped,
# in-game-verified behavior. FLAGS (0 retail callers, trivial ~150-byte
# class, no event handlers) also keeps its replacement — it became
# reachable via the basename fix, Gate 6 verifies it clean, and keeping
# it replaced avoids a third code path (replace/drop/rename) for a
# zero-risk class.
UNSAFE_TO_REPLACE = {'FREE', 'METHOD', 'AIRSPEL'}

# Dev-tier drafts compiled (so Gate 7 still counts their parse errors) but
# never written to the FLX. ORLOK1.UNK declares `npcclass Orlok`; until
# 2026-10-07 its class header failed to parse (`routine getDrink():String;`,
# a member return type) so it compiled class-less and was dropped. With
# the header parsing it would REPLACE retail ORLOK 0x040A, the Tenebrae
# barkeep, with this 203-line 1994 draft: an unaudited change nobody asked
# for, so it stays out.
DEV_NOT_SHIPPED = {'ORLOK1'}

# Headerless provider files compiled under a NEW class name instead of
# their basename, so the provider's routines live at a manifest-pinned LV
# class id and no retail class is disturbed (see UNSAFE_TO_REPLACE).
# Consumers still write `uses "free";` — the provider registry key stays
# the FILE basename ('free'); only the class id the emitted calls target
# changes.
PROVIDER_CLASS_NAMES = {'FREE': 'LVFREE'}
#
# PROVIDER_BASENAMES: real `uses`-imported bare-routine providers,
# investigated against the corpus (grep for `uses "x"` in every LV source
# dir, then checked whether the named file/class defines any bare
# `routine`/`process funcName(...)` — as opposed to `ClassName::method`
# member functions, which resolve as method calls / intrinsics, not `uses`
# targets):
#   free    -> FREE.UNK   — 40+ bare routines/processes (getPeriod,
#                            killProcess, scrollBack, safePlaySFX, ...).
#                            REAL provider; the only one with consumers in
#                            the M0.5 warning corpus.
#   item, npc, egg, flags, snddefs, types, plaque -> not compilable
#     bare-routine providers: `item`/`npc`/`egg` name base-class method
#     namespaces resolved as intrinsics or `ClassName::method` defs
#     (METHOD.UNK — e.g. Item::toggleStatus, Item::legal_moveItemTo — all
#     called via `obj.method()`, never as a bare `uses`-resolved
#     FunctionCall/SpawnStmt; out of this work's scope, see the design
#     note in the task write-up); `flags` (FLAGS.UNK) declares globalflags
#     only, no callable routines; `snddefs`/`types`/`plaque` are constant
#     tables, not compiled files at all.
PROVIDER_BASENAMES = {'FREE'}

# New LV class ID allocation starts here — 0x0597 (1431), one past the
# base game's highest used class id (1430). Only a fallback default now:
# the real cursor is lv_manifest.Manifest.next_free['class_id'] (M0.6);
# this constant matches lv_manifest.BOOTSTRAP_CLASS_ID and is used only if
# a manifest is somehow present without a next_free.class_id entry.
#
# CORRECTED 2026-07-03 (M0.6): this used to be 0x0260 ("FLX entry 610 —
# past the 5000-byte boundary that stealth mode used to rely on"), which
# was WRONG — the base FLX is a dense, mostly-unnamed class table all the
# way to id 1430, and 0x0260 (608) is a real named class (DEMNSTAT) with
# live bytecode. Every prior --full build silently overwrote DEMNSTAT and
# ~27 classes after it (add_new_class() is byte-identical to
# replace_class() in u8_flx_packer.py — there was no collision check).
# See the longer note above lv_manifest.BOOTSTRAP_CLASS_ID.
NEW_CLASS_START = lv_manifest.BOOTSTRAP_CLASS_ID

# Known-defective 1994 source files in the dev directory (UNK files/UNK/).
# These fail to compile because of corruption/truncation in the recovered
# source snapshot itself, not a compiler bug, and are allowed to fail
# without failing the build. Every other .UNK file in this directory (and
# everything in LOST VALE/ and lv-new/) must compile.
DEV_ALLOWLIST = {
    'EALOGO': 'truncated block comment in the recovered 1994 source',
    'TJORVI': 'unterminated string literal; this is an early draft of '
              'TYORVI.UNK (LOST VALE/), which compiles cleanly and is the '
              'version actually built',
}

# Quest-critical classes that must appear among the successful compilation
# results, or the build fails. This is a stopgap pinned by hand against a
# real --full build's reported class names (2026-07-03); M0.6's
# shared/build/lv_manifest.json is meant to become the source of truth for
# this list once it lands.
#
# Identity is `class_name.upper()` for files that declare a class, except
# FREE, which is a routines-only library file with no `class` declaration
# (`ast.class_decl` is None, so `result.class_name` is '') — for that one
# entry identity falls back to the source file's basename. See
# _compiled_identity() below.
QUEST_CRITICAL_CLASSES = {
    'TYPEMYTHRANLVDLG',  # MYTHRDLG.UNK (lv-new)     — Mythran LV intro dialogue
    'SIGRID',            # SIGRID.UNK   (lv-new)     — Sigrid NPC dialogue
    'EGGAOCEREMONY',     # AOSCENE.UNK  (lv-new)     — Sacred Circle ceremony egg
    'EGGCLOUDCLIFFS',    # CLCLIMB.UNK  (lv-new)     — cliff-climbing trigger egg
    'TYPERECEPTACLE',    # COLPUZZL.UNK (lv-new)     — elemental column puzzle
                          #   receptacle (npcnum 120 dispatch, pinned 1144;
                          #   replaced the retired EggColumnPuzzle sketch
                          #   2026-07-04 — pin 1449 stays in the manifest,
                          #   append-only, but nothing compiles into it)
    'EGGENDGAME',        # ENDGAME.UNK  (lv-new)     — victory sequence egg
    'EGGREAPPLY',        # REAPPLY.UNK  (lv-new)     — re-applies Map 11's
                          #   destroyed pillars and boulders (and Map 10's
                          #   Test Plant) after a map switch reloads them;
                          #   without it a player back from the Vale is
                          #   sealed in Map 11's pad room. Also removes the
                          #   respawned carryable quest items (root, stone,
                          #   talismans, Shield halves) once they are used
                          #   or already carried
    'TYPELORDBRITISH',   # LORDBRIT.UNK (dev UNK/)   — quest step 1 message item
    'EGGLBSCENE',        # LBSCENE.UNK  (lv-new)     — quest step 1 trigger egg
    'EGGPLANTTEST',      # PLNTST.UNK   (LOST VALE/) — Passage Test plant egg
    'EGGSHADES',         # SHADES.UNK   (dev UNK/)   — Sacred Circle shades egg
    'LVFREE',            # FREE.UNK     (LOST VALE/) — routine library,
                          #   compiled under the LVFREE override
                          #   (PROVIDER_CLASS_NAMES; retail FREE/0x581 is
                          #   UNSAFE_TO_REPLACE), so its compiled identity
                          #   is the override name, not the basename
    # Seven recovered NPC dialogues (each replaces an existing base-game
    # NPC class id via LV_NPC_SHAPES in u8c_symbols.py):
    'RAGNAR',            # RAGNAR.UNK   (dev UNK/)
    'THORDIS',           # THORDIS.UNK  (dev UNK/)
    'ATLI',              # ATLI.UNK     (LOST VALE/)
    'INGJALD',           # INGYALD.UNK  (dev UNK/) — the recovered file name has
                          #   the 1994-era spelling "Ingyald"; the class the
                          #   source actually declares is "Ingjald"
    'HRODNY',            # HRODNY.UNK   (dev UNK/)
    'TYORVI',            # TYORVI.UNK   (LOST VALE/) — TJORVI.UNK in the dev dir
                          #   is the defective early draft (DEV_ALLOWLIST above)
    'EZREKAL',           # EZREKAL.UNK  (LOST VALE/)
}

STEALTH_RETIRED_MSG = """\
ERROR: --stealth mode is retired.

Stealth mode preserved the base game EUSECODE.FLX's original md5-5000 hash
and file size so the rebuilt archive would pass stock ScummVM's detection
check unmodified. It cannot carry the Lost Vale expansion: new classes
placed past FLX entry 610 are silently skipped whenever they don't fit in
space reclaimed from a same-slot replacement, and the packer's
reclaim-before-place allocator corrupts the FLX outright when a replacement
class (Mythran, in practice) is larger than the space it's reclaiming. The
md5-5000 window this relied on is documented in write_stealth() in
u8_flx_packer.py, which stays in the tree as a record of that
reverse-engineering finding, but is no longer called from this build.

Use --full instead, with the patched scummvm-lv binary (see
build_scummvm.sh) that carries the correct detection entry for the rebuilt
FLX.\
"""


def _compiled_identity(path, result):
    """Identity string used to look up a compiled class in
    QUEST_CRITICAL_CLASSES: the declared class name, or the source file's
    basename for files with no `class` declaration (e.g. FREE.UNK)."""
    if result.class_name:
        return result.class_name.upper()
    return os.path.splitext(os.path.basename(path))[0].upper()


def _sorted_unk_paths(dir_path, reverse=False):
    """.UNK files in dir_path, sorted (or reverse-sorted). Every directory
    walk in build() goes through this one function so a single `reverse`
    flag can flip compile order everywhere at once — the M0.6 order-
    independence test (manifest-design.md section 5, criterion 1) uses
    this to prove a pinned manifest makes compile order irrelevant to the
    output FLX."""
    if not os.path.isdir(dir_path):
        return []
    return sorted(glob.glob(os.path.join(dir_path, '*.UNK')), reverse=reverse)


def _retail_shared_flag_names():
    """Flag names declared in the 5 modified-base-class sources
    (AVATAR/FREE/FLAGS/METHOD/AIRSPEL), searched across both LV source
    directories. Used to tag manifest entries "retail_shared": true at
    allocation time (M0.6 design doc section 2 step 4) — informational
    only, does not affect allocation."""
    return lv_manifest.retail_shared_flag_names(
        (LV_FINAL, LV_DEV), MODIFIED_BASE_CLASSES)


# NOTE: gates 1-3 below key off CompilationResult.success only (an
# exception raised out of parse_file/codegen), matching the definition of
# "compiles" the rest of this codebase (and driver.print_report()) already
# uses. u8c_parser.py has a separate, broader failure mode: for some
# syntax errors it recovers instead of raising, printing "Parse error in
# <path>" to stderr and returning a partial AST that codegen happily
# generates bytecode from, so `success` stays True on a truncated class.
# That currently affects a dozen-plus files (EZREKAL, FREE, MAGNET,
# ARAMINA, AVATAR, POTION, SHADES, ...) on every build today, unconditional
# on anything M0.3/M0.4 touch. Gating on it here would fail today's
# baseline build, which is out of scope for this milestone — silent
# codegen fallbacks are M0.5 ("Kill silent codegen fallbacks", PLAN.md
# section 1).


def build(output_path=None, reverse_order=False):
    """Build the final EUSECODE.FLX (full mode only; see module docstring).

    Args:
        output_path: where to write the FLX. Defaults to OUTPUT_FLX (the
            real build location). Tests pass a temp path here so they
            never touch the real artifact; the manifest is only appended
            to and detection_tables.h is only auto-updated when this is
            the real OUTPUT_FLX (see is_real_build below) — a temp-path
            build reads the manifest but never writes it.
        reverse_order: compile every LV source directory in reverse-
            sorted order instead of sorted order. Exists for the M0.6
            order-independence test (manifest-design.md section 5,
            criterion 1): with a fully-pinned manifest, compile order
            must not affect the output FLX.

    Returns:
        (output_path, failures) — failures is a list of one-line strings;
        empty on a fully successful build.
    """
    output_path = output_path or OUTPUT_FLX
    is_real_build = (output_path == OUTPUT_FLX)

    print("=" * 60)
    print("Building EUSECODE.FLX for Ultima: The Lost Vale [full mode]")
    print("=" * 60)

    failures = []

    # Step 1: Load base game
    print(f"\n1. Loading base game: {BASE_FLX}")
    reader = UsecodeFlexArchive(BASE_FLX)
    packer = UsecodeFlxPacker.from_existing(reader)
    print(f"   Base game: {reader.count} entries, {reader.class_count} classes")

    # Step 1b: Load the M0.6 id/flag manifest (or enter bootstrap mode).
    manifest_path = lv_manifest.DEFAULT_MANIFEST_PATH
    print(f"\n1b. Loading manifest: {manifest_path}")
    manifest = lv_manifest.Manifest.load_if_exists(manifest_path)
    bootstrap_mode = manifest is None
    if bootstrap_mode:
        print(f"   No manifest found — BOOTSTRAP MODE "
              f"(global_bit starts at {lv_manifest.BOOTSTRAP_GLOBAL_BIT}, "
              f"class_id starts at 0x{lv_manifest.BOOTSTRAP_CLASS_ID:04X}; "
              f"every allocation this run becomes a new pin)")
        manifest = lv_manifest.Manifest.bootstrap()
    else:
        problems = lv_manifest.validate(manifest)
        if problems:
            print(f"   MANIFEST CORRUPT — {len(problems)} conflict(s), build cannot proceed:")
            for p in problems:
                print(f"     - {p}")
                failures.append(f"manifest conflict: {p}")
            print(f"\n{'='*60}")
            print(f"BUILD FAILED — {len(failures)} issue(s)")
            print(f"{'='*60}")
            for f in failures:
                print(f"FAIL: {f}")
            return output_path, failures
        print(f"   Loaded {len(manifest.global_flags)} flag pin(s), "
              f"{len(manifest.classes)} class pin(s); next_free={manifest.next_free}")

    # Step 2: Create compiler
    symbols = create_symbol_table(flx_path=BASE_FLX)
    # Snapshot base-game class ids BEFORE NPC registration below, so class
    # id conflict messages can distinguish "collides with a base-game id"
    # from "collides with an LV NPC id". Also keep a name->id snapshot
    # (base_game_class_ids) for the class-assignment loop's existing_id
    # lookup below — it must see ONLY real base-game classes, never a
    # manifest-pinned NEW class name (see the pre-registration note a few
    # lines down): using the live `symbols` there would make a PINNED
    # class (e.g. EggCandleTrick @ 0x0597) look like an "existing base
    # class" the moment its own name got pre-registered, routing it
    # through the base-class REPLACE path instead of the pin-aware NEW
    # CLASS path (losing the pin-conflict check and mis-recording it into
    # manifest.modified_base_classes) — caught empirically 2026-07-03 when
    # this pre-registration was added: several manifest-pinned LV classes
    # started printing "REPLACE" instead of "PIN".
    base_game_ids = set(symbols.class_ids.values())
    base_game_class_ids = dict(symbols.class_ids)
    symbols.load_manifest(manifest)
    # Register LV NPC class names so Tyorvi.isDead() etc. resolve correctly
    for name, shape_id in LV_NPC_SHAPES.items():
        symbols.register_class(name, shape_id)
    npc_ids = set(LV_NPC_SHAPES.values())

    # Pre-register every manifest-pinned class name (M0.6 pins, e.g.
    # TypeLordBritish -> 0x05A3) so a cross-file reference to it — e.g.
    # `spawn TypeLordBritish() -> return;` from a different file's egg
    # hatch() — resolves regardless of compile order. Without this,
    # load_manifest() only pins flags; a pinned CLASS name only became
    # known to the symbol table once its own file happened to compile
    # (get_class_id() reads program.class_decl at generate_class() time),
    # so any consumer compiled earlier in the walk saw an unresolved name.
    # Needed by the upcoming LORDBRIT wiring (shared/docs/wiring.md).
    for name, cid in manifest.classes.items():
        symbols.register_class(name, cid)
    driver = Driver(symbols=symbols)

    # Step 2b (bootstrap only): flag-declaration pre-pass. A manifest-
    # loaded build pre-defines every flag before any file compiles, so a
    # flag REFERENCE resolves the same everywhere regardless of compile
    # order (that resolution invariance is precisely what makes the M0.6
    # order-independence guarantee possible). Bootstrap mode must produce
    # the same bytecode the manifest builds will, or the very first FLX
    # would differ from every later one — so before compiling, parse every
    # source in the same walk order the compile steps use and allocate all
    # declared globalflags up front. Allocation order (and therefore the
    # generated pins) is identical to what compiling directly would have
    # produced; the only difference is that references in files compiled
    # BEFORE the declaring file (e.g. LOST VALE/ATLI.UNK before dev
    # FLAGS.UNK) now resolve instead of silently compiling as push 0.
    # Files that fail to parse here (EALOGO, TJORVI) are skipped; the
    # compile steps below report them exactly as before.
    if bootstrap_mode:
        from u8c_parser import parse_file
        print(f"\n1c. Bootstrap flag pre-pass:")
        # Same precedence as the compile steps: lv-patched/ first, then
        # LOST VALE/, then UNK files/UNK/, each later tier skipping
        # basenames already collected.
        prepass_paths = list(_sorted_unk_paths(LV_PATCHED, reverse=reverse_order))
        prepass_basenames = {
            os.path.splitext(os.path.basename(p))[0].upper() for p in prepass_paths}
        for p in _sorted_unk_paths(LV_FINAL, reverse=reverse_order):
            if os.path.splitext(os.path.basename(p))[0].upper() in prepass_basenames:
                continue
            prepass_paths.append(p)
            prepass_basenames.add(
                os.path.splitext(os.path.basename(p))[0].upper())
        for p in _sorted_unk_paths(LV_DEV, reverse=reverse_order):
            if os.path.splitext(os.path.basename(p))[0].upper() in prepass_basenames:
                continue
            prepass_paths.append(p)
        prepass_paths.extend(_sorted_unk_paths(LV_NEW, reverse=reverse_order))
        n_files = 0
        for p in prepass_paths:
            try:
                ast = parse_file(p)
            except Exception:
                continue  # compile steps below report the failure
            n_files += 1
            for gf in ast.globalflags:
                symbols.allocate_global_flag(gf.name, gf.bits)
        print(f"   Pre-allocated {len(symbols.new_allocations)} flag(s) "
              f"from {n_files} parseable source file(s)")

    # Step 2c: `uses`-import provider pre-pass. Consumers resolve a bare
    # function/spawn call against a provider's compiled routine offsets
    # (CodeGenerator self-registers each compiled file's bare routines —
    # see u8c_codegen.py generate_class()), so a provider must compile
    # BEFORE any file that `uses` it. The general LOST VALE/ walk below is
    # alphabetical and would otherwise compile ATLI/CANTRK/EZREKAL (which
    # all `uses "free";`) before FREE.UNK itself. PROVIDER_BASENAMES is the
    # investigated set of real bare-routine providers in the corpus — see
    # the note above MODIFIED_BASE_CLASSES for what was ruled out and why
    # (METHOD.UNK, FLAGS.UNK, and the other `uses` targets are not
    # bare-routine providers in the `uses "free"` sense).
    #
    # A provider with a PROVIDER_CLASS_NAMES override (FREE -> LVFREE)
    # compiles as a NEW class, and codegen needs its class id AT COMPILE
    # TIME (same-class calls inside the provider, e.g. getPeriod() calling
    # getHour(), and every provider-symbol record carry it). Ids are
    # normally assigned AFTER compilation in step 6, so pre-resolve the
    # override id here: the manifest pin if one exists (every build after
    # the first), else the next_free cursor — correct because the provider
    # pre-pass makes this file the FIRST compiled result, hence the first
    # unpinned allocation step 6 performs. A post-assignment gate below
    # (after step 6) fails the build if the two ever disagree.
    print(f"\n2b. Provider pre-pass (uses-imported library files):")
    provider_override_ids = {}  # override name -> pre-resolved class id
    for base, override in PROVIDER_CLASS_NAMES.items():
        oid = manifest.classes.get(override)
        if oid is None:
            oid = manifest.next_free.get('class_id', NEW_CLASS_START)
        symbols.register_class(override, oid)
        provider_override_ids[override] = oid
        print(f"   provider class {override} (from {base}.UNK) -> 0x{oid:04X}"
              f"{' (manifest pin)' if override in manifest.classes else ' (cursor, will pin)'}")
    # lv-patched/ basename -> path map: the patched tier outranks every
    # recovered-source tier, including a provider file, so the pre-pass
    # must compile the patched copy when one exists.
    patched_paths = {
        os.path.splitext(os.path.basename(p))[0].upper(): p
        for p in _sorted_unk_paths(LV_PATCHED, reverse=reverse_order)}

    provider_paths = []
    provider_results = []
    for path in _sorted_unk_paths(LV_FINAL, reverse=reverse_order):
        base = os.path.splitext(os.path.basename(path))[0].upper()
        if base in PROVIDER_BASENAMES:
            provider_paths.append(path)
            if base in patched_paths:
                print(f"   PATCHED {base}.UNK (lv-patched)")
                path = patched_paths[base]
            provider_results.append(driver.compile_file(
                path, verbose=True,
                class_name_override=PROVIDER_CLASS_NAMES.get(base)))

    # Step 2d: Compile lv-patched/ sources (HIGHEST precedence tier —
    # patched copies of recovered 1994 files, see LV_PATCHED above). The
    # LOST VALE/ and dev walks below skip these basenames, mirroring how
    # the dev walk already defers to LOST VALE/.
    print(f"\n2c. Compiling lv-patched/ patched 1994 sources:")
    lv_patched_results = []
    for base, path in patched_paths.items():
        if base in PROVIDER_BASENAMES:
            continue  # compiled in the provider pre-pass above
        overridden = (
            os.path.exists(os.path.join(LV_FINAL, os.path.basename(path)))
            or os.path.exists(os.path.join(LV_DEV, os.path.basename(path))))
        if overridden:
            print(f"   PATCHED {base}.UNK (lv-patched)")
        lv_patched_results.append(driver.compile_file(path, verbose=True))

    # Step 3: Compile LOST VALE/ final classes
    print(f"\n2. Compiling LOST VALE/ final classes:")
    lv_final_results = list(provider_results)
    for path in _sorted_unk_paths(LV_FINAL, reverse=reverse_order):
        if path in provider_paths:
            continue  # already compiled in the provider pre-pass above
        if os.path.splitext(os.path.basename(path))[0].upper() in patched_paths:
            continue  # lv-patched/ override compiled in step 2c above
        lv_final_results.append(driver.compile_file(path, verbose=True))

    # Step 4: Compile selected UNK files/UNK/ development files
    # Only compile files that aren't already in LOST VALE/
    #
    # CORRECTED 2026-07-03 (M0.6): this used to dedupe by comparing the
    # dev file's basename against the set of *class names* compiled from
    # LOST VALE/, which only coincidentally matches when a file's basename
    # equals its declared class name. It doesn't for CANTRK.UNK (declares
    # EggCandleTrick), MONSKUL.UNK (TypeMonskul), PLNTST.UNK
    # (EggPlantTest), and TESTPLAN.UNK (TypePoisonPlant) — all four exist
    # in both LOST VALE/ and UNK files/UNK/ with identical basenames, so
    # every prior build silently compiled BOTH the dev draft and the final
    # version and gave them two different new class ids under the same
    # name (confirmed empirically: the old logic produced duplicate
    # "class NAME: 0x...." allocations for exactly these four names).
    # Dedup on basename (matching the "already have a final version of
    # this file" intent the comment already states) instead.
    print(f"\n3. Compiling UNK files/UNK/ development files:")
    # A dev file is skipped when a higher tier already provided its
    # basename: LOST VALE/ (the original preference) or lv-patched/
    # (step 2c; every lv-patched basename is a patched_paths key, so the
    # union below covers patched provider files too).
    final_basenames = {
        os.path.splitext(os.path.basename(r.filename))[0].upper()
        for r in lv_final_results
    } | set(patched_paths)

    lv_dev_results = []
    for path in _sorted_unk_paths(LV_DEV, reverse=reverse_order):
        name = os.path.splitext(os.path.basename(path))[0].upper()
        # Skip if we have a final version (same source basename in LOST VALE/)
        if name in final_basenames:
            continue
        lv_dev_results.append(driver.compile_file(path, verbose=True))

    # Step 5: Compile new dialogue files
    print(f"\n4. Compiling new dialogue files:")
    lv_new_results = []
    for path in _sorted_unk_paths(LV_NEW, reverse=reverse_order):
        lv_new_results.append(driver.compile_file(path, verbose=True))

    # ── Gate 1/2/3: any LOST VALE/, lv-new/, or (non-allowlisted) dev-dir
    # file that failed to compile fails the build. ──────────────────────────
    for r in lv_final_results:
        if not r.success:
            err = r.errors[0] if r.errors else 'unknown error'
            failures.append(
                f"LOST VALE/{os.path.basename(r.filename)} failed to compile: {err}")

    # lv-patched/ sources are curated, versioned fixes — a compile
    # failure there is always a build failure (no allowlist).
    for r in lv_patched_results:
        if not r.success:
            err = r.errors[0] if r.errors else 'unknown error'
            failures.append(
                f"lv-patched/{os.path.basename(r.filename)} failed to compile: {err}")

    for r in lv_new_results:
        if not r.success:
            err = r.errors[0] if r.errors else 'unknown error'
            failures.append(
                f"lv-new/{os.path.basename(r.filename)} failed to compile: {err}")

    for r in lv_dev_results:
        if not r.success:
            base = os.path.splitext(os.path.basename(r.filename))[0].upper()
            if base in DEV_ALLOWLIST:
                continue  # documented 1994 source defect, not a build failure
            err = r.errors[0] if r.errors else 'unknown error'
            failures.append(
                f"UNK files/UNK/{os.path.basename(r.filename)} failed to compile: {err}")

    # ── Gate 7 (2026-07-04): recovered-parse-error RATCHET. "success"
    # with recovered errors means statements were silently DROPPED from
    # the compiled class — that is how EZREKAL shipped with its entire
    # conversation missing. Every file is bounded by this pinned
    # baseline (absent = 0); counts may only go DOWN. When you fix a
    # construct, tighten the pin in the same commit. ─────────────────────
    # Every compiled tier parses clean as of 2026-10-07 (Item/Number List
    # locals, `foreach x in L`, `L[i]`, `Camera::`/`Kernel::` calls,
    # `/=`, `modulo`, `|`, `within 1 cell`, `String Reference`, member
    # return types, forward declarations and AVATAR's inline spawn block
    # all parse now). Only EALOGO/TJORVI fail, as hard compile failures on
    # DEV_ALLOWLIST, which never reach this tally. Keep it empty.
    PARSE_ERROR_BASELINE = {}
    parse_totals = {}
    # P1: lv_patched_results was MISSING from this sweep — the highest-
    # precedence source tier (versioned patched 1994 files, which override
    # both LOST VALE/ and the dev dir) sat outside the very ratchet that
    # exists because EZREKAL once shipped with its conversation silently
    # dropped. A hand-edit slip in lv-patched/ could drop statements and
    # still exit 0. Dormant when found (all patched files parse clean), but
    # exactly the recurrence this gate is for.
    # Also dropped the duplicated `provider_results`: line ~567 does
    # `lv_final_results = list(provider_results)`, so providers were counted
    # twice. Harmless in effect (the tally takes a max per basename) but
    # misleading to read.
    for r in (lv_patched_results + lv_final_results + lv_new_results
              + lv_dev_results):
        n = len(getattr(r, 'parse_errors', []) or [])
        if not n:
            continue
        base = os.path.basename(r.filename)
        parse_totals[base] = max(parse_totals.get(base, 0), n)
        limit = PARSE_ERROR_BASELINE.get(base, 0)
        if n > limit:
            first = r.parse_errors[0]
            failures.append(
                f"{base}: {n} recovered parse error(s) exceeds the "
                f"pinned baseline {limit} — statements are being "
                f"DROPPED (first: {first})")
    if parse_totals:
        print("\n  Recovered-parse-error census (statements dropped; "
              "ratcheted by Gate 7):")
        for base, n in sorted(parse_totals.items()):
            limit = PARSE_ERROR_BASELINE.get(base, 0)
            marker = 'OVER BASELINE' if n > limit else f'<= pin {limit}'
            print(f"    {base:15s} {n:3d}  ({marker})")

    # Step 6: Assign class IDs and update FLX
    print(f"\n5. Assigning class IDs and updating FLX:")
    next_new_id = manifest.next_free.get('class_id', NEW_CLASS_START)
    replaced = 0
    added = 0
    # (name, id) pairs assigned from the cursor this run — new manifest
    # pins, appended at the end of a successful build.
    new_class_allocations = []
    # id -> name for every id assigned to a *new* class so far this run,
    # so two new classes pinned/allocated to the same id are caught too.
    assigned_ids = {}
    # name -> id groups recorded (not consulted) in the manifest for
    # conflict detection: NPC replacements and base-class replacements.
    recorded_npc_classes = {}
    recorded_base_replacements = {}

    for path, result in driver.results.items():
        if not result.success or not result.bytecode:
            continue
        if (os.path.splitext(os.path.basename(path))[0].upper()
                in DEV_NOT_SHIPPED):
            continue

        class_name = result.class_name.upper() if result.class_name else ''
        if not class_name:
            # No `class` header (see the MODIFIED_BASE_CLASSES note above)
            # — fall back to the file's own basename ONLY for the known
            # class-less modified-base-class files, so they're recognized
            # as base-class replacements below instead of silently
            # dropped. UNSAFE_TO_REPLACE members (FREE/METHOD/AIRSPEL —
            # 190/126/5 retail classes call into them at hardcoded
            # offsets, see the constant's comment) are excluded: their
            # compiled results stay dropped ON PURPOSE so the retail
            # class ships byte-identical. FREE never reaches this branch
            # anyway (compiled under the LVFREE override, so
            # result.class_name is set); the exclusion here is what keeps
            # METHOD and AIRSPEL out of the FLX.
            base = os.path.splitext(os.path.basename(path))[0].upper()
            if base in MODIFIED_BASE_CLASSES and base not in UNSAFE_TO_REPLACE:
                class_name = base

        # Check if this is an LV NPC with a shape-based class ID
        npc_shape = LV_NPC_SHAPES.get(class_name) if class_name else None
        # Check if this is a modified base class. Uses the frozen
        # base_game_class_ids snapshot, NOT the live symbol table — see
        # the comment above its capture: the live table also carries
        # manifest-pinned NEW class ids (from the pre-registration below),
        # which must go through the "elif class_name:" pin-aware branch,
        # not this one.
        existing_id = base_game_class_ids.get(class_name) if class_name else None

        if npc_shape is not None:
            # LV NPC — place at npcnum+1024 class ID for engine dispatch.
            # NPCs are promoted to Actors by the patched map.cpp, so all
            # events (including schedule, enterFastArea, leaveFastArea) are safe.
            packer.replace_class(npc_shape, result.bytecode, class_name)
            result.class_id = npc_shape
            recorded_npc_classes[class_name] = npc_shape
            replaced += 1
            print(f"   NPC     0x{npc_shape:04X} {class_name}")
        elif existing_id is not None:
            # Replace existing base game class
            packer.replace_class(existing_id, result.bytecode, class_name)
            result.class_id = existing_id
            recorded_base_replacements[class_name] = existing_id
            replaced += 1
            print(f"   REPLACE 0x{existing_id:04X} {class_name}")
        elif class_name:
            # New class — consult the manifest pin first (M0.6).
            pinned_id = manifest.classes.get(class_name)
            if pinned_id is not None:
                conflict = None
                if pinned_id in base_game_ids:
                    conflict = "collides with a base-game class id"
                elif pinned_id in npc_ids:
                    conflict = "collides with an LV NPC class id (LV_NPC_SHAPES)"
                elif pinned_id in assigned_ids and assigned_ids[pinned_id] != class_name:
                    conflict = (f"collides with class '{assigned_ids[pinned_id]}' "
                                f"(also assigned 0x{pinned_id:04X} this build)")
                if conflict is not None:
                    failures.append(
                        f"class '{class_name}': pinned id 0x{pinned_id:04X} "
                        f"{conflict} — cannot honor pin, no re-pin code path")
                    continue
                new_id = pinned_id
                packer.add_new_class(new_id, result.bytecode, class_name[:8])
                result.class_id = new_id
                assigned_ids[new_id] = class_name
                added += 1
                print(f"   PIN     0x{new_id:04X} {class_name}")
            else:
                new_id = next_new_id
                if new_id in base_game_ids or new_id in npc_ids or new_id in assigned_ids:
                    failures.append(
                        f"class '{class_name}': next_free.class_id 0x{new_id:04X} "
                        f"is already in use — manifest next_free cursor is corrupt")
                    continue
                next_new_id += 1
                packer.add_new_class(new_id, result.bytecode, class_name[:8])
                result.class_id = new_id
                assigned_ids[new_id] = class_name
                new_class_allocations.append((class_name, new_id))
                added += 1
                print(f"   ADD     0x{new_id:04X} {class_name} (new pin)")

    # ── Gate (provider id consistency): a PROVIDER_CLASS_NAMES override
    # class (LVFREE) had its id pre-resolved BEFORE compilation (step 2b)
    # because codegen bakes it into every same-class call and provider-
    # symbol record. The assignment loop above must have landed it on
    # exactly that id (via its manifest pin, or as the first cursor
    # allocation) — any mismatch means consumer classes were compiled
    # with calls into the wrong class id, so fail the build. ──────────────
    for override, expected_id in provider_override_ids.items():
        r = next((r for r in driver.results.values()
                  if r.success and r.class_name
                  and r.class_name.upper() == override.upper()), None)
        if r is None:
            failures.append(f"provider class {override}: no successful "
                            f"compiled result to verify")
        elif r.class_id != expected_id:
            failures.append(
                f"provider class {override}: pre-resolved id "
                f"0x{expected_id:04X} (baked into compiled call sites) != "
                f"assigned id 0x{r.class_id if r.class_id is not None else -1:04X} "
                f"— consumer call sites target the wrong class")

    # Step 6b: Wire the LV intro dialogue into the base Mythran NPC (0x421).
    # Mythran has no LV override .UNK (41 KB class, no recovered source), so we
    # append a replacement use() handler and repoint event 01 to it. See
    # patch_mythran.py. This must run after class IDs are assigned (we need
    # TypeMythranLVDlg's id) and after all LV sources compiled (we need lbDone's
    # allocated global bit).
    print(f"\n5b. Patching Mythran (0x421) to reach the LV intro dialogue:")
    lv_dlg = next((r for r in driver.results.values()
                   if r.success and r.class_name
                   and r.class_name.upper() == 'TYPEMYTHRANLVDLG'), None)
    lbdone = symbols.get_global_flag('lbDone')
    stockvisit = symbols.get_global_flag('mythranStockVisit')

    mythran_skip_reason = None
    if lv_dlg is None:
        mythran_skip_reason = 'TypeMythranLVDlg not compiled'
    elif lbdone is None:
        mythran_skip_reason = 'lbDone global flag not allocated'
    elif stockvisit is None:
        mythran_skip_reason = 'mythranStockVisit global flag not allocated'

    if mythran_skip_reason is not None:
        print(f"   SKIP: {mythran_skip_reason} — Mythran left unpatched.")
        failures.append(f"Mythran patch skipped: {mythran_skip_reason}")
    else:
        base_mythran = reader.get_class_data(0x421)
        lv_use_off = _event_offset(lv_dlg.bytecode, 1)
        # P4: patch_mythran_class() raises ValueError from four deliberate
        # guards (zero use offset, moved use event, preamble hash mismatch,
        # 16-bit offset overflow). Uncaught, those printed a raw traceback
        # instead of the documented one-line BUILD FAILED summary — the exit
        # code was already nonzero, so this is diagnostic consistency: every
        # other build gate reports through `failures`, and a guard that fires
        # should read like a gate, not a crash. Catching it also stops the
        # unpatched 0x421 being handed to Gate 6 as if it had been patched.
        try:
            patched = patch_mythran_class(
                base_mythran, lbdone[0], lbdone[1], lv_dlg.class_id,
                lv_use_off, stockvisit[0], stockvisit[1])
        except ValueError as exc:
            mythran_skip_reason = f"patch guard rejected the base class: {exc}"
            print(f"   FAIL: {mythran_skip_reason}")
            failures.append(f"Mythran patch failed: {exc}")
        else:
            packer.replace_class(0x421, patched, 'MYTHRAN')
            replaced += 1
            print(f"   PATCH   0x0421 MYTHRAN  (+{len(patched)-len(base_mythran)} bytes; "
                  f"lbDone bit {lbdone[0]}, stockVisit bit {stockvisit[0]} "
                  f"-> call 0x{lv_dlg.class_id:04X}:0x{lv_use_off:04X})")

    # ── Gate 4: quest-critical classes must be among the successful
    # compilation results. ───────────────────────────────────────────────────
    compiled_identities = {
        _compiled_identity(path, result)
        for path, result in driver.results.items()
        if result.success and result.bytecode
    }
    for name in sorted(QUEST_CRITICAL_CLASSES):
        if name not in compiled_identities:
            failures.append(f"quest-critical class missing from compiled results: {name}")

    # ── Gate 5 (M0.6): no unpinned flag allocation this run landed inside
    # a pinned flag's bit range (belt-and-suspenders against a corrupted
    # next_free cursor). ────────────────────────────────────────────────────
    for problem in symbols.check_new_allocations():
        failures.append(f"manifest conflict: {problem}")

    # Step 7: Write output — gated on failures, mirroring build_all_maps.py's
    # validator-before-save pattern: a failing build must not touch
    # output_path or detection_tables.h at all, so a bad run can never leave
    # a half-updated or corrupt artifact behind. The manifest is only
    # appended to and detection_tables.h only auto-updated for a real
    # build (output_path == OUTPUT_FLX) — a temp-path test build reads the
    # manifest but never writes it, so two builds against the same
    # manifest (e.g. the order-independence test) can't race each other.
    size = 0
    if not failures:
        print(f"\n6. Writing output:")
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        # P2: build to a STAGING file and only promote it over the
        # canonical artifact once Gate 6 has verified it. Previously the
        # canonical path was truncated and rewritten in place BEFORE
        # verification, so a Gate-6 failure (or an interrupted write) left
        # corrupt bytes at the path install_lv.sh copies into the game and
        # destroyed the last known-good build. Staging in the same directory
        # keeps os.replace() atomic (same filesystem).
        staging_path = output_path + '.staging'
        size = packer.write(staging_path)
        print(f"   Staged {staging_path}: {size:,} bytes (full: all LV classes)")

        # ── Gate 6: post-write bytecode sanity check ────────────────────────
        # Disassemble every class this build REPLACED or ADDED (NPC
        # replacements, base-class replacements, manifest-pinned/new
        # classes, and the patched Mythran) — not the untouched base-game
        # classes — with the reference disassembler, and fail the build if
        # any listing contains an unknown-opcode fallback ("db" line) or a
        # global bit reference >= 4096 (the engine's BitSet capacity).
        # Both symptoms mean a trampoline/relay block was spliced into the
        # middle of an instruction instead of at an instruction boundary
        # (the ATLI/"Kill her?" bug this gate exists to catch forever).
        print(f"\n6b. Verifying compiled bytecode (disassembly sanity check):")
        touched_classes = dict(assigned_ids)  # id -> name (PIN + ADD)
        touched_classes.update(
            (cid, name) for name, cid in recorded_npc_classes.items())
        touched_classes.update(
            (cid, name) for name, cid in recorded_base_replacements.items())
        if mythran_skip_reason is None:
            touched_classes[0x421] = 'MYTHRAN'

        disasm_ok = True
        bad_count = 0
        _disasm = UsecodeDisassembler()
        verify_reader = UsecodeFlexArchive(staging_path)
        for cid in sorted(touched_classes):
            cname = touched_classes[cid]
            if not verify_reader.class_exists(cid):
                failures.append(f"post-write verify: class 0x{cid:04X} "
                                 f"{cname} missing from written FLX")
                disasm_ok = False
                bad_count += 1
                continue
            cdata = verify_reader.get_class_data(cid)
            try:
                instrs = _disasm.disassemble_bytecode(cdata, start_offset=0x80)
            except Exception as e:
                failures.append(f"post-write verify: class 0x{cid:04X} "
                                 f"{cname} failed to disassemble: {e}")
                disasm_ok = False
                bad_count += 1
                continue
            class_bad = False
            for instr in instrs:
                if instr.mnemonic == 'db':
                    failures.append(
                        f"post-write verify: class 0x{cid:04X} {cname} has "
                        f"an unknown-opcode fallback (db, byte "
                        f"{instr.raw_bytes[0]:02X}) at offset "
                        f"0x{instr.offset:04X} — a relay block likely "
                        f"landed mid-instruction")
                    class_bad = True
                elif instr.opcode in (0x4E, 0x4F):  # push/pop global
                    bit_offset = instr.operands[0][1]
                    if bit_offset >= 4096:
                        failures.append(
                            f"post-write verify: class 0x{cid:04X} {cname} "
                            f"references global bit {bit_offset} (>= 4096 "
                            f"engine BitSet capacity) at offset "
                            f"0x{instr.offset:04X}")
                        class_bad = True
            if class_bad:
                disasm_ok = False
                bad_count += 1

        if disasm_ok:
            print(f"   {len(touched_classes)} classes verified clean")
        else:
            print(f"   {len(touched_classes) - bad_count}/{len(touched_classes)} "
                  f"classes clean — {bad_count} class(es) FAILED verification "
                  f"(see FAIL lines below)")

        # Compute md5-5000 and file size for ScummVM detection entry
        flx_data = Path(staging_path).read_bytes()
        md5_5000 = hashlib.md5(flx_data[:5000]).hexdigest()
        print(f"\n   ScummVM detection entry values:")
        print(f"   md5-5000: {md5_5000}")
        print(f"   size:     {len(flx_data)}")
        print(f"   C++ entry:")
        print(f'   AD_ENTRY2s("usecode/eusecode.flx", "{md5_5000}", {len(flx_data)},')
        print(f'              "static/eintro.skf", "b34169ece4286735262ac3430c441909", 1297731)')

        # ── P2 promotion gate ───────────────────────────────────────────
        # Only now, with the staged file fully verified, does it replace the
        # canonical artifact. On failure the previous good build is left
        # exactly as it was and the bad output is quarantined for debugging.
        if disasm_ok and not failures:
            os.replace(staging_path, output_path)
            print(f"\n   Promoted staged build to {output_path}")
        else:
            quarantine = output_path + '.failed'
            os.replace(staging_path, quarantine)
            print(f"\n   {'!' * 56}")
            print(f"   VERIFICATION FAILED — {output_path} was NOT modified.")
            print(f"   The previous known-good build is intact; the rejected")
            print(f"   output is at {quarantine} for inspection.")
            print(f"   {'!' * 56}")

        if is_real_build and disasm_ok:
            # Auto-update ScummVM detection table. Gated on disasm_ok too:
            # a build that failed Gate 6's post-write verification must not
            # auto-commit detection_tables.h or new manifest pins for a
            # known-corrupt FLX (the FLX itself was already written above
            # for debugging, but nothing downstream treats it as canonical).
            detection_h = os.path.join(
                REPO_ROOT, 'scummvm-lv',
                'engines', 'ultima', 'detection_tables.h')
            if os.path.exists(detection_h):
                det_text = Path(detection_h).read_text()
                # Update ONLY the Lost Vale entry: the detection table is
                # full of vanilla U8 variants that also list eusecode.flx
                # with their own md5s, so the substitution must be bounded
                # to the first eusecode line AFTER the "Lost Vale" comment
                # marker. (An unbounded regex here once clobbered vanilla
                # entries; see devlog 2026-07-03.)
                lv_pos = det_text.find('Lost Vale')
                if lv_pos < 0:
                    print("\n   WARNING: no Lost Vale entry in detection_tables.h; "
                          "run build_scummvm.sh to insert one")
                    new_text = det_text
                else:
                    new_text = det_text[:lv_pos] + re.sub(
                        r'("usecode/eusecode\.flx",\s*")[0-9a-f]{32}(",\s*)\d+',
                        rf'\g<1>{md5_5000}\g<2>{len(flx_data)}',
                        det_text[lv_pos:], count=1)
                if new_text != det_text:
                    Path(detection_h).write_text(new_text)
                    print(f"\n   Auto-updated detection_tables.h: md5={md5_5000}, size={len(flx_data)}")
                else:
                    print(f"\n   detection_tables.h already up to date")
            else:
                print(f"\n   WARNING: detection_tables.h not found at {detection_h}")

            # M0.6: append any newly-allocated flags/classes as pins.
            total_new = len(symbols.new_allocations) + len(new_class_allocations)
            if total_new:
                retail_shared = _retail_shared_flag_names()
                for name, bit, width in symbols.new_allocations:
                    entry = {'bit': bit, 'width': width}
                    if name in retail_shared:
                        entry['retail_shared'] = True
                    manifest.global_flags[name] = entry
                for name, cid in new_class_allocations:
                    manifest.classes[name] = cid
                # Recorded-only groups (conflict detection; code stays the
                # source of truth for these — design doc section 3).
                manifest.npc_classes.update(recorded_npc_classes)
                manifest.modified_base_classes.update(recorded_base_replacements)
                manifest.next_free['global_bit'] = symbols._next_global_bit
                manifest.next_free['class_id'] = next_new_id
                manifest.save(manifest_path)

                print(f"\n{'='*60}")
                print(f"MANIFEST: appended {total_new} new pin(s) to {manifest_path}")
                print(f"{'='*60}")
                for name, bit, width in symbols.new_allocations:
                    tag = ' [retail_shared]' if name in retail_shared else ''
                    print(f"   flag  {name}: bit {bit} (0x{bit:X}), width {width}{tag}")
                for name, cid in new_class_allocations:
                    print(f"   class {name}: 0x{cid:04X}")
                print(f"   next_free: {manifest.next_free}")
                print(f"   >>> COMMIT {manifest_path} <<<")
            elif bootstrap_mode:
                # Should not happen (bootstrap always allocates everything
                # it touches) but write the (empty) manifest anyway rather
                # than silently staying in bootstrap mode forever.
                manifest.save(manifest_path)
                print(f"\n   MANIFEST: bootstrap manifest written to {manifest_path} "
                      f"with 0 pins (unexpected — no flags/classes were compiled?)")
        elif is_real_build and not disasm_ok:
            print(f"\n   detection_tables.h / manifest NOT updated — Gate 6 "
                  f"post-write verification failed, see FAIL lines below")
    else:
        print(f"\n6. Writing output: SKIPPED — build has {len(failures)} failure(s), "
              f"see below. {output_path} was not touched.")

    # Summary
    print(f"\n{'='*60}")
    print(f"Build Summary")
    print(f"{'='*60}")
    print(f"  Base game classes:   {reader.class_count}")
    print(f"  Classes replaced:    {replaced}")
    print(f"  New classes added:   {added}")
    print(f"  Total class slots:   {next_new_id}")
    print(f"  Output size:         {size:,} bytes")

    driver.print_report()

    if failures:
        print(f"\n{'='*60}")
        print(f"BUILD FAILED — {len(failures)} issue(s)")
        print(f"{'='*60}")
        for f in failures:
            print(f"FAIL: {f}")

    return output_path, failures


if __name__ == '__main__':
    if '--stealth' in sys.argv:
        print(STEALTH_RETIRED_MSG)
        sys.exit(1)

    # Reject unknown CLI args instead of silently ignoring them (2026-07-19).
    # This script has never parsed argv beyond the --stealth check, so an
    # invocation like `--output /tmp/test.FLX` looked like a safe temp-path
    # build but actually wrote the REAL shared/build/EUSECODE.FLX. That
    # footgun cost a clobbered artifact. To build elsewhere, import build()
    # and pass output_path= (which correctly disables all shared-state
    # writes); there is deliberately no CLI flag for it.
    _known = {'--full', '--stealth'}
    _unknown = [a for a in sys.argv[1:] if a not in _known]
    if _unknown:
        print(f"ERROR: unrecognized argument(s): {' '.join(_unknown)}")
        print(f"Supported: {' '.join(sorted(_known))}")
        print("To build to another path, import build() and pass "
              "output_path= — there is no CLI flag for it.")
        sys.exit(2)

    _output_path, _failures = build()
    sys.exit(1 if _failures else 0)
