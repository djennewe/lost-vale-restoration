#!/usr/bin/env python3
"""
lv_manifest.py — M0.6 savegame-visible id/flag pin manifest.

Loads, saves, and validates shared/build/lv_manifest.json — the checked-in
pin table that freezes every savegame-visible number the build allocates
dynamically (global flag bits, new usecode class ids). Design doc:
agents/usecode-compiler/docs/manifest-design.md. PLAN.md item M0.6.

Schema (design doc section 3):
    {
      "version": 1,
      "comment": "...",
      "global_flags": {"name": {"bit": int, "width": int,
                                 ["retail_shared": true], ["retired": true]}},
                      # retired: the bit range is dead forever. A flag that
                      # moves keeps its live name; the old range stays as
                      # "<name>_<oldbit>" with "retired": true.
      "classes": {"name": class_id},
      "npc_classes": {"name": class_id},          # recorded, not allocated
      "modified_base_classes": {"name": class_id}, # recorded, not allocated
      "next_free": {"global_bit": int, "class_id": int}
    }

`global_flags` and `classes` are the pins consulted by the allocators.
`npc_classes` / `modified_base_classes` are recorded for conflict detection
only — code (LV_NPC_SHAPES, MODIFIED_BASE_CLASSES in build_eusecode.py)
stays the source of truth for those two groups.

Path resolution: the manifest is resolved RELATIVE TO THIS FILE (repo
root three levels up), never against build_eusecode.py's absolute
OUTPUT_DIR constant (which always points at the main checkout). That way
a manifest generated/updated in a worktree lands in that worktree's
shared/build/, not silently in the main repo.
"""

import json
import os
import re

# ─── Path resolution ────────────────────────────────────────────────────────

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
# lv_manifest.py lives at agents/usecode-compiler/src/lv_manifest.py —
# three levels up (src -> usecode-compiler -> agents) is the repo root.
REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, '..', '..', '..'))
DEFAULT_MANIFEST_PATH = os.path.join(REPO_ROOT, 'shared', 'build', 'lv_manifest.json')

# ─── Bootstrap constants (design doc section 2) ─────────────────────────────
# No manifest present = bootstrap mode. LV global flags rebase into a
# reserved window starting at bit 1024 (clear of retail's dense sub-600
# range and the sparse outliers at 2560+; capacity is 4096 bits).
#
# New class ids: the design doc's original instruction was "treat class ids
# exactly as today starting 0x0260" — verified WRONG during M0.6
# implementation (2026-07-03) and corrected here. build_eusecode.py's old
# NEW_CLASS_START = 0x0260 (608) comment claimed it was "past FLX entry
# 610", i.e. past every used class id. Checked against the base
# USECODE.FLX directly: the archive is a DENSE, mostly-unnamed class table
# all the way out to class id 1430 (AIRSPEL, one of our own modified base
# classes, sits at 1430); id 608 is a real named class (DEMNSTAT) with live
# bytecode, as are ~27 ids right after it (FEBARSEW, FEBARSNS, NSSHELF,
# BASEBOOK, PLAQUEEW, GRAVEII, ... — assorted décor/utility classes). Every
# prior --full build silently overwrote those with new LV classes via
# add_new_class(), which is byte-identical to replace_class() in
# u8_flx_packer.py. class id 1431 is the first genuinely free id (entry
# 1433 in the archive; the base FLX has 1433 entries total, 0-1432, all
# populated through class id 1430). Starting new-class allocation there
# both fixes the corruption going forward and is what M0.6's own conflict
# detection (build_eusecode.py's "collides with a base-game class id"
# check) would have refused to build at 0x0260 anyway.

BOOTSTRAP_GLOBAL_BIT = 1024
BOOTSTRAP_CLASS_ID = 1431  # 0x0597 — one past the base game's highest used class id (1430)

MANIFEST_VERSION = 1
DEFAULT_COMMENT = "Savegame-visible id/flag pins. Append-only. Never renumber."

_GLOBALFLAG_RE = re.compile(r'^\s*globalflag\s+([A-Za-z_][A-Za-z0-9_]*)', re.MULTILINE)


class ManifestError(Exception):
    """Raised for manifest conflicts: duplicate/overlapping bit pins,
    class id collisions, or a pinned width that disagrees with a source
    declaration. There is no re-pin code path — these are always build
    failures (M0.6 design doc section 4)."""


class Manifest:
    """In-memory representation of lv_manifest.json."""

    def __init__(self, version=MANIFEST_VERSION, comment=DEFAULT_COMMENT,
                 global_flags=None, classes=None, npc_classes=None,
                 modified_base_classes=None, next_free=None, globs=None, dressing=None):
        self.globs = dict(globs or {})
        self.dressing = dict(dressing or {})
        self.version = version
        self.comment = comment
        # name -> {"bit": int, "width": int, ["retail_shared": bool], ["retired": bool]}
        self.global_flags = dict(global_flags or {})
        # name -> class_id
        self.classes = dict(classes or {})
        self.npc_classes = dict(npc_classes or {})
        self.modified_base_classes = dict(modified_base_classes or {})
        self.next_free = dict(next_free or {
            'global_bit': BOOTSTRAP_GLOBAL_BIT,
            'class_id': BOOTSTRAP_CLASS_ID,
        })

    # ── construction ────────────────────────────────────────────────────

    @classmethod
    def bootstrap(cls):
        """An empty manifest seeded at the reserved LV bootstrap window.
        Every allocation made while this is in effect is a "new" allocation
        (design doc section 2's adopted bootstrap)."""
        return cls(next_free={
            'global_bit': BOOTSTRAP_GLOBAL_BIT,
            'class_id': BOOTSTRAP_CLASS_ID,
        })

    @classmethod
    def load(cls, path=None):
        """Load a manifest from disk. Raises on a missing/malformed file —
        use load_if_exists() for the "no manifest yet" bootstrap check."""
        path = path or DEFAULT_MANIFEST_PATH
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(
            version=data.get('version', MANIFEST_VERSION),
            comment=data.get('comment', DEFAULT_COMMENT),
            global_flags=data.get('global_flags', {}),
            classes=data.get('classes', {}),
            npc_classes=data.get('npc_classes', {}),
            modified_base_classes=data.get('modified_base_classes', {}),
            next_free=data.get('next_free', {}),
            globs=data.get('globs', {}),
            dressing=data.get('dressing', {}),
        )

    @classmethod
    def load_if_exists(cls, path=None):
        """Return the loaded manifest, or None if the file is absent
        (the M0.6 bootstrap trigger)."""
        path = path or DEFAULT_MANIFEST_PATH
        if not os.path.exists(path):
            return None
        return cls.load(path)

    # ── serialization ───────────────────────────────────────────────────

    def to_dict(self):
        """Deterministic dict form: keys sorted alphabetically within each
        group, and within each flag/class entry, so re-saving an
        unmodified manifest produces a byte-identical file (clean diffs
        on append)."""
        return {
            'version': self.version,
            'comment': self.comment,
            'global_flags': {
                name: dict(sorted(self.global_flags[name].items()))
                for name in sorted(self.global_flags)
            },
            'classes': {name: self.classes[name] for name in sorted(self.classes)},
            'npc_classes': {name: self.npc_classes[name] for name in sorted(self.npc_classes)},
            'modified_base_classes': {
                name: self.modified_base_classes[name]
                for name in sorted(self.modified_base_classes)
            },
            'next_free': dict(self.next_free),
            **({'globs': self.globs} if self.globs else {}),
            **({'dressing': self.dressing} if self.dressing else {}),
        }

    def save(self, path=None):
        path = path or DEFAULT_MANIFEST_PATH
        out_dir = os.path.dirname(path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
            f.write('\n')

    # ── introspection ───────────────────────────────────────────────────

    def flag_range(self, name):
        info = self.global_flags[name]
        bit = info['bit']
        width = info.get('width', 1)
        return bit, bit + width - 1

    def __repr__(self):
        return (f"Manifest(flags={len(self.global_flags)}, "
                f"classes={len(self.classes)}, "
                f"next_free={self.next_free!r})")


# ─── Validation (M0.6 acceptance criterion 3: hand-edited conflicts must
# fail the build, named clearly) ─────────────────────────────────────────────

def validate(manifest):
    """Structural conflict check over a manifest's own pins (no source
    compilation involved). Returns a list of human-readable conflict
    strings; empty means the manifest is internally consistent.

    Covers:
      - two global flag pins with overlapping (including identical) bit
        ranges.
      - a live global flag pin overlapping a RETIRED flag's bit range
        (a retired bit is dead forever: a save written before the
        retirement may still hold a value there).
      - a class id used by more than one of classes/npc_classes/
        modified_base_classes.

    Width mismatches between a pin and a live `globalflag` declaration are
    NOT caught here (that needs the source's declared width, which isn't
    in the manifest) — see SymbolTable.allocate_global_flag(), which
    raises ManifestError for that case at allocation time.
    """
    problems = []

    # ── global flag bit overlaps ──
    ranges = []
    retired_ranges = []
    for name, info in manifest.global_flags.items():
        bit = info['bit']
        width = info.get('width', 1)
        if info.get('retired'):
            retired_ranges.append((bit, bit + width - 1, name))
            continue
        ranges.append((bit, bit + width - 1, name))
    ranges.sort()
    for i in range(1, len(ranges)):
        prev_start, prev_end, prev_name = ranges[i - 1]
        cur_start, cur_end, cur_name = ranges[i]
        if cur_start <= prev_end:
            problems.append(
                f"global flag bit overlap: '{prev_name}' [{prev_start}-{prev_end}] "
                f"overlaps '{cur_name}' [{cur_start}-{cur_end}]")

    # ── a live pin on a retired bit (never reuse a retired bit) ──
    for r_start, r_end, r_name in retired_ranges:
        for start, end, name in ranges:
            if start <= r_end and r_start <= end:
                problems.append(
                    f"global flag '{name}' [{start}-{end}] reuses retired "
                    f"bits of '{r_name}' [{r_start}-{r_end}]")

    # ── class id collisions across classes / npc_classes / modified_base_classes ──
    id_owner = {}
    for group_name, group in (
        ('classes', manifest.classes),
        ('npc_classes', manifest.npc_classes),
        ('modified_base_classes', manifest.modified_base_classes),
    ):
        for name, cid in group.items():
            if cid in id_owner:
                other_group, other_name = id_owner[cid]
                problems.append(
                    f"class id 0x{cid:04X} pinned to both {other_group}:{other_name} "
                    f"and {group_name}:{name}")
            else:
                id_owner[cid] = (group_name, name)

    # ── allocation cursors must sit PAST every pin (M3) ──
    # The flag side has a post-allocation guard (SymbolTable.
    # check_new_allocations, wired to build Gate 5), but the CLASS-ID side had
    # none and validate() never inspected the cursors at all. A corrupted or
    # hand-edited next_free could then hand out an id that is already pinned
    # to a reserved-but-not-yet-compiled class, silently overwriting live
    # bytecode — the same class of bug that once clobbered DEMNSTAT and ~27
    # classes after it. Cheap invariant, checked here so every caller of
    # validate() gets it.
    cursor_cid = manifest.next_free.get('class_id')
    if cursor_cid is not None and id_owner:
        highest = max(id_owner)
        if cursor_cid <= highest:
            group_name, name = id_owner[highest]
            problems.append(
                f"next_free.class_id 0x{cursor_cid:04X} is not past the "
                f"highest pinned class id 0x{highest:04X} "
                f"({group_name}:{name}) — the next allocation would reuse a "
                f"pinned id")
        if cursor_cid in id_owner:
            group_name, name = id_owner[cursor_cid]
            problems.append(
                f"next_free.class_id 0x{cursor_cid:04X} is itself pinned to "
                f"{group_name}:{name}")

    cursor_bit = manifest.next_free.get('global_bit')
    all_ranges = ranges + retired_ranges
    if cursor_bit is not None and all_ranges:
        highest_bit = max(end for _start, end, _n in all_ranges)
        if cursor_bit <= highest_bit:
            owner = next(n for _s, e, n in all_ranges if e == highest_bit)
            problems.append(
                f"next_free.global_bit {cursor_bit} is not past the highest "
                f"pinned flag bit {highest_bit} ('{owner}') — the next "
                f"allocation would collide with a pinned or retired flag")

    return problems


# ─── Bootstrap helper: retail-shared flag detection (M0.6 step 4) ──────────

def retail_shared_flag_names(source_dirs, class_names):
    """Flag names declared via `globalflag` in the .UNK sources of the
    given modified-base-class names, searched across the given source
    directories (design doc section 2: flags our recompiled base classes
    share with untouched retail bytecode; informational only — does not
    affect allocation).

    Args:
        source_dirs: iterable of directory paths to search for
            "<CLASS_NAME>.UNK" (case-sensitive on the filesystem, so
            callers should pass the exact on-disk basenames they expect).
        class_names: iterable of class name strings, e.g.
            {'AVATAR', 'FREE', 'FLAGS', 'METHOD', 'AIRSPEL'}.

    Returns:
        set of flag name strings.
    """
    names = set()
    for base_dir in source_dirs:
        if not base_dir or not os.path.isdir(base_dir):
            continue
        for class_name in class_names:
            path = os.path.join(base_dir, f'{class_name}.UNK')
            if not os.path.exists(path):
                continue
            with open(path, 'r', encoding='ascii', errors='replace') as f:
                text = f.read()
            names.update(_GLOBALFLAG_RE.findall(text))
    return names


if __name__ == '__main__':
    m = Manifest.load_if_exists()
    if m is None:
        print(f"No manifest at {DEFAULT_MANIFEST_PATH} (bootstrap mode would trigger)")
    else:
        print(m)
        problems = validate(m)
        if problems:
            print(f"\n{len(problems)} conflict(s):")
            for p in problems:
                print(f"  - {p}")
        else:
            print("No conflicts.")
