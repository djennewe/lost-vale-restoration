#!/usr/bin/env python3
"""
u8_flag_graph.py — M1 flag-graph and reachability tool (PLAN.md 2.3 / 2.1).

Disassembles every class in a built EUSECODE.FLX (via the reference
disassembler, imported read-only — see the do-not-modify rule in
CLAUDE.md), joins every global flag access against the savegame-pin
manifest (shared/build/lv_manifest.json), and computes an inbound
reference count per class using the engine's four dispatch mechanisms
(PLAN.md section 0):

    (a) default item dispatch     class_id = shape
    (b) LV npcNum patch           class_id = npcNum + 1024, npcNum != 0
    (c) UnkEgg quality dispatch   class_id = quality + 0x47F, shape has
                                   the SF_UNKEGG typeflag family
    (d) usecode-internal          0x11 call / 0x57 spawn from any class

Classes reachable by NONE of the above are orphans: compiled and shipped,
but nothing in the game invokes them. See docs/flag-graph.md for the full
model, the savegame blind spot (permanent-NPC dispatch via a runtime
objId < 256, which is not visible in FIXED.DAT and therefore not audited
here), and a discovered field-reuse caveat on mechanism (b).

Usage:
    python3 u8_flag_graph.py <EUSECODE.FLX> \\
        [--manifest shared/build/lv_manifest.json] \\
        [--fixed shared/build/FIXED.DAT] \\
        [--typeflag shared/build/TYPEFLAG.DAT] \\
        [--out shared/docs/wiring-data.md]

All paths are resolved relative to the repository root if not absolute,
except that the four --xxx overrides accept any path (absolute or
relative to the current working directory) as given.

Read-only: this tool imports u8_usecode_disasm.py as a library and never
modifies it, per the project's hard rule (CLAUDE.md). u8_map.py and
parse_typeflag.py are local copies of the map-populator agent's readers
(per the project's per-agent-copy convention for u8_flex.py); do not
import them across agent directories, and do not edit the originals from
here.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)

from u8_flex import UsecodeFlexArchive          # noqa: E402
from u8_usecode_disasm import UsecodeDisassembler, DisassemblyError  # noqa: E402
from u8_map import MapArchive                    # noqa: E402
from parse_typeflag import load_typeflag         # noqa: E402

# agents/usecode-disasm/src -> agents/usecode-disasm -> agents -> repo root
REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, '..', '..', '..'))

DEFAULT_MANIFEST = os.path.join(REPO_ROOT, 'shared', 'build', 'lv_manifest.json')
DEFAULT_FIXED = os.path.join(REPO_ROOT, 'shared', 'build', 'FIXED.DAT')
DEFAULT_TYPEFLAG = os.path.join(REPO_ROOT, 'shared', 'build', 'TYPEFLAG.DAT')
DEFAULT_OUT = os.path.join(REPO_ROOT, 'shared', 'docs', 'wiring-data.md')

LV_WINDOW_START = 1024      # global flag bit window (manifest-design.md)
UNKEGG_CLASS_BASE = 0x47F   # 1151 — quality + 0x47F = class id (engine fact)
GLOBAL_BITSET_CAPACITY = 4096  # UCMachine creates BitSet(0x1000) — manifest-design.md sec 2

# Egg/glob "family" shapes whose 16-bit npcnum-position field is reused by
# the map authoring API (u8_map.py) for something other than an actor's
# NPC number: SHAPE_GLOB_EGG stores nothing there, SHAPE_STANDARD_EGG's
# frame distinguishes egg kinds, SHAPE_MONSTER_EGG reuses the field for a
# spawn count, SHAPE_TELEPORT_EGG reuses it for a teleport destination's
# npc slot. See docs/flag-graph.md "Discovered quirk" for why this matters
# to mechanism (b).
EGG_FAMILY_SHAPES = {2, 73, 500, 508}


def load_manifest(path):
    with open(path) as f:
        m = json.load(f)
    return m


def build_bit_index(manifest):
    """bit -> {'name':..., 'width':..., 'retail_shared':bool} for every
    pinned flag. Bits are guaranteed unique by the manifest's own
    append-only invariant (M0.6); we still guard it here."""
    bit_index = {}
    for name, info in manifest.get('global_flags', {}).items():
        bit = info['bit']
        if bit in bit_index:
            raise ValueError(
                f"manifest bit collision: {name!r} and "
                f"{bit_index[bit]['name']!r} both claim bit {bit}")
        bit_index[bit] = {
            'name': name,
            'width': info.get('width', 1),
            'retail_shared': bool(info.get('retail_shared')),
            'retired': bool(info.get('retired')),
        }
    return bit_index


def disassemble_all(flx_path):
    """Return {classid: summary_dict} plus a list of (classid, error) for
    classes that failed to disassemble."""
    flx = UsecodeFlexArchive(flx_path)
    disasm = UsecodeDisassembler()
    summaries = {}
    errors = []
    for classid, name, data in flx.all_classes():
        try:
            summaries[classid] = disasm.disassemble_class_summary(data, classid, name)
        except (DisassemblyError, Exception) as e:  # keep scanning on one bad class
            errors.append((classid, str(e)))
    return flx, summaries, errors


def compute_inbound(summaries, map_archive, unkegg_shape_ids):
    """Per-class inbound reference tally across all four mechanisms.

    A class referring to ITSELF is not reachability (H3, 2026-07-25). A
    self-call, self-spawn, or spawn-inline cannot start the class — something
    else has to reach it first — so those edges are collected under 'self'
    and deliberately excluded from inbound_total(). Counting them was
    inflating the tally in the dangerous direction: 54 classes in the built
    FLX have a self-edge as their ONLY inbound reference and were being
    reported reachable on that basis alone, which is a MASKED orphan rather
    than the false orphan the review predicted. All 20 base-game 0x58 edges
    are self-edges, so adding them to the tally (the fix as originally
    specified) would have made this worse, not better.

    Returns:
        inbound: {classid: {'shape': int, 'npcnum': int, 'npcnum_field_reuse': int,
                             'unkegg': int, 'call': set(src_classid),
                             'spawn': set(src_classid), 'self': set(kind)}}
    """
    inbound = defaultdict(lambda: {
        'shape': 0, 'npcnum': 0, 'npcnum_field_reuse': 0, 'unkegg': 0,
        'call': set(), 'spawn': set(), 'self': set(),
    })

    # (a) default item dispatch, (b) LV npcNum patch, (c) UnkEgg quality
    for map_num in map_archive.non_empty_maps():
        for item in map_archive.get_map_items(map_num):
            inbound[item.shape]['shape'] += 1
            if item.npcnum != 0:
                target = item.npcnum + LV_WINDOW_START
                if item.shape in EGG_FAMILY_SHAPES:
                    # Field reuse (teleport dest_npc / monster-egg count),
                    # not an authored NPC placement — see module docstring.
                    inbound[target]['npcnum_field_reuse'] += 1
                else:
                    inbound[target]['npcnum'] += 1
            if item.shape in unkegg_shape_ids and item.quality:
                target = item.quality + UNKEGG_CLASS_BASE
                inbound[target]['unkegg'] += 1

    # (d) usecode-internal call / spawn / spawn-inline. Self-edges are
    # recorded separately and never count toward reachability.
    for classid, summary in summaries.items():
        for kind, key in (('call', 'class_calls'), ('spawn', 'spawns'),
                          ('spawn-inline', 'spawn_inline')):
            for target, _offset in summary.get(key, ()):
                if target == classid:
                    inbound[target]['self'].add(kind)
                elif kind == 'spawn-inline':
                    # Not seen in any FLX examined (all 0x58 edges are
                    # self-edges), but a cross-class one is a real inbound
                    # reference and is treated as a spawn.
                    inbound[target]['spawn'].add(classid)
                else:
                    inbound[target][kind].add(classid)

    return inbound


def inbound_total(entry):
    """Total inbound reference count for orphan/reachable determination.
    npcnum_field_reuse counts per the literal engine rule (any nonzero
    npcNum byte dispatches) but is reported separately so a reader can
    see when a class's only 'reachability' is an incidental field
    collision rather than an authored trigger.

    'self' is deliberately NOT summed (H3): a class that only calls or
    spawns itself still has nothing that can start it."""
    return (entry['shape'] + entry['npcnum'] + entry['npcnum_field_reuse']
            + entry['unkegg'] + len(entry['call']) + len(entry['spawn']))


def inbound_breakdown(entry):
    parts = []
    if entry['shape']:
        parts.append(f"shape:{entry['shape']}")
    if entry['npcnum']:
        parts.append(f"npcnum:{entry['npcnum']}")
    if entry['npcnum_field_reuse']:
        parts.append(f"npcnum(field-reuse):{entry['npcnum_field_reuse']}")
    if entry['unkegg']:
        parts.append(f"unkegg:{entry['unkegg']}")
    if entry['call']:
        parts.append(f"call:{len(entry['call'])}")
    if entry['spawn']:
        parts.append(f"spawn:{len(entry['spawn'])}")
    if entry['self']:
        # Shown so a reader can see WHY a class with internal activity is
        # still an orphan, but never counted — see inbound_total().
        parts.append(f"self-only:{'/'.join(sorted(entry['self']))}")
    return ', '.join(parts) if parts else '(none)'


def build_flag_report(summaries, bit_index):
    """Returns (lv_flags, retail_summary) where lv_flags is a dict keyed
    by bit (>=1024) with reader/writer classid sets, and retail_summary
    is aggregate counts for bit < 1024."""
    readers = defaultdict(set)   # bit -> {classid}
    writers = defaultdict(set)
    retail_bits_seen = set()
    retail_read_ops = 0
    retail_write_ops = 0

    for classid, summary in summaries.items():
        for bit, _width in summary['globals_read']:
            if bit < LV_WINDOW_START:
                retail_bits_seen.add(bit)
                retail_read_ops += 1
            else:
                readers[bit].add(classid)
        for bit, _width in summary['globals_written']:
            if bit < LV_WINDOW_START:
                retail_bits_seen.add(bit)
                retail_write_ops += 1
            else:
                writers[bit].add(classid)

    lv_bits = sorted(set(readers) | set(writers) | set(bit_index))
    lv_flags = {}
    for bit in lv_bits:
        info = bit_index.get(bit)
        name = info['name'] if info else f"bit_{bit}"
        width = info['width'] if info else None
        retail_shared = info['retail_shared'] if info else None
        lv_flags[bit] = {
            'name': name,
            'width': width,
            'retail_shared': retail_shared,
            'readers': readers.get(bit, set()),
            'writers': writers.get(bit, set()),
        }

    retail_summary = {
        'distinct_bits': len(retail_bits_seen),
        'read_ops': retail_read_ops,
        'write_ops': retail_write_ops,
    }
    return lv_flags, retail_summary


def find_anomalous_bit_offsets(flx, classid, bit):
    """Re-disassemble one class at the instruction level (not the deduped
    summary) to find the exact byte offset(s) of push/pop global
    instructions referencing an out-of-range bit. Used only for the rare
    anomaly case, so re-running the disassembler once per hit is cheap."""
    from u8_usecode_disasm import UsecodeClass
    disasm = UsecodeDisassembler()
    data = flx.get_class_data(classid)
    uc = UsecodeClass(classid, flx.get_class_name(classid), data)
    instrs = disasm.disassemble_bytecode(uc.bytecode, start_offset=0x80)
    hits = []
    for instr in instrs:
        if instr.opcode in (0x4E, 0x4F) and instr.operands[0][1] == bit:
            hits.append(instr.offset)
    return hits


def find_bitset_anomalies(flx, lv_flags, manifest_names=None):
    """Flag bits >= GLOBAL_BITSET_CAPACITY: the engine's global flag
    BitSet cannot hold them, so a push/pop global at one of these bits
    cannot be a genuine flag access. It is a strong signal the linear
    instruction walk (or, more likely, the compiled bytecode itself) has
    drifted out of true instruction alignment at that point — worth a
    manual look at the class, not a flag to route through the normal
    reader/writer report."""
    anomalies = []
    for bit in sorted(lv_flags):
        if bit < GLOBAL_BITSET_CAPACITY:
            continue
        f = lv_flags[bit]
        classids = sorted(f['readers'] | f['writers'])
        detail = []
        for cid in classids:
            offsets = find_anomalous_bit_offsets(flx, cid, bit)
            detail.append((cid, classname(flx, cid, manifest_names), offsets))
        anomalies.append((bit, detail))
    return anomalies


def classname(flx, classid, manifest_names=None):
    """Prefer the manifest's full pinned name (not truncated to the FLX
    name table's 9-byte field) when one is pinned for this class id."""
    if manifest_names and classid in manifest_names:
        return manifest_names[classid]
    name = flx.get_class_name(classid)
    return name if name else f"Class_{classid:04X}"


def build_manifest_name_index(manifest):
    """classid -> full pinned name, from classes + npc_classes +
    modified_base_classes (last-writer-wins is fine; ids don't collide
    across these three sections by manifest invariant)."""
    idx = {}
    for section in ('classes', 'npc_classes', 'modified_base_classes'):
        for name, cid in manifest.get(section, {}).items():
            idx[cid] = name
    return idx


def md5_of(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def render_report(flx, flx_path, summaries, errors, manifest, inbound,
                   lv_flags, retail_summary, lv_target_ids, base_ids,
                   anomalies, manifest_names):
    lines = []
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    lines.append("# Lost Vale wiring data — flag graph & reachability audit")
    lines.append("")
    lines.append(f"Generated by u8_flag_graph.py on {now}.")
    lines.append(f"Input FLX: `{os.path.relpath(flx_path, REPO_ROOT)}` "
                 f"(md5 `{md5_of(flx_path)}`, {flx.class_count} class slots, "
                 f"{len(summaries)} non-empty, {len(errors)} failed to disassemble).")
    lines.append("")
    lines.append("This file is machine-regenerable — do not hand-edit. Re-run:")
    lines.append("")
    lines.append("```")
    lines.append("python3 agents/usecode-disasm/src/u8_flag_graph.py "
                 "shared/build/EUSECODE.FLX")
    lines.append("```")
    lines.append("")
    lines.append("See `agents/usecode-disasm/docs/flag-graph.md` for the dispatch "
                 "model and known blind spots.")
    lines.append("")

    if errors:
        lines.append("## Disassembly errors")
        lines.append("")
        for classid, err in sorted(errors):
            lines.append(f"- class `{classid:04X}`: {err}")
        lines.append("")

    if anomalies:
        lines.append("## Anomalies: flag bits beyond engine capacity")
        lines.append("")
        lines.append(f"The engine's global flag BitSet holds {GLOBAL_BITSET_CAPACITY} bits "
                     f"(`UCMachine` creates `BitSet(0x1000)`, manifest-design.md sec 2). "
                     f"A `push global`/`pop global` referencing a bit at or past "
                     f"{GLOBAL_BITSET_CAPACITY} cannot be a genuine flag access — it is a "
                     f"strong signal that the compiled bytecode contains stray bytes at "
                     f"that offset (verified: the surrounding bytes decode into opcodes "
                     f"0xF2/0xFC, neither of which exists in the ISA). **This is a "
                     f"suspected usecode-compiler codegen defect, not a flag-graph tool "
                     f"bug** — reported here for the compiler team, not fixed (out of "
                     f"scope for this tool; see CLAUDE.md's agent-directory boundary).")
        lines.append("")
        for bit, detail in anomalies:
            lines.append(f"- bit {bit} (`0x{bit:04X}`, capacity is `0x{GLOBAL_BITSET_CAPACITY:04X}`):")
            for cid, name, offsets in detail:
                off_str = ', '.join(f"{o:04X}" for o in offsets) or '(offset not found on re-scan)'
                lines.append(f"  - class {name} ({cid}): bytecode offset(s) {off_str}")
        lines.append("")

    # ── Orphan / reachability table for LV classes ──────────────────────
    lines.append("## LV class reachability (the list that matters)")
    lines.append("")
    lines.append("Every class id pinned in `lv_manifest.json`'s `classes` and "
                 "`npc_classes` sections. Inbound counts sum the four engine "
                 "dispatch mechanisms (PLAN.md section 0); `npcnum(field-reuse)` "
                 "marks hits from teleport/monster-egg items whose npcnum-position "
                 "field is reused for something else (see flag-graph.md) — real "
                 "but likely incidental, not an authored trigger.")
    lines.append("")
    lines.append("| Class id | Name | Status | Inbound references |")
    lines.append("|---|---|---|---|")

    orphans = []
    reachable = []
    not_built = []
    for cid in sorted(lv_target_ids):
        entry = inbound.get(cid)
        total = inbound_total(entry) if entry else 0
        name = classname(flx, cid, manifest_names)
        # A manifest pin whose class is not in the FLX is a STALE PIN, not an
        # orphan (2026-07-25 triage). This list iterates manifest ids, so a
        # retired class — EGGCOLUMNPUZZLE, superseded by TypeReceptacle —
        # showed up as an orphan forever. "Shipped but unreachable" is a
        # defect; "pinned but never built" is bookkeeping. Do not conflate
        # them: the first needs wiring, the second needs the pin retired.
        if not flx.class_exists(cid):
            not_built.append((cid, name))
            lines.append(f"| {cid} (`{cid:04X}`) | {name} | not built | "
                         f"(stale manifest pin — no source declares it) |")
            continue
        if total == 0:
            orphans.append((cid, name))
            # H3: an orphan can still have self-edges. Show them — "ORPHAN |
            # (none)" reads as "this class has no code touching it at all",
            # which is a different diagnosis from "it spawns itself but
            # nothing starts it".
            why = inbound_breakdown(entry) if entry else '(none)'
            lines.append(f"| {cid} (`{cid:04X}`) | {name} | ORPHAN | {why} |")
        else:
            reachable.append((cid, name, total))
            lines.append(f"| {cid} (`{cid:04X}`) | {name} | reachable | "
                         f"{inbound_breakdown(entry)} |")
    lines.append("")

    lines.append(f"**{len(orphans)} orphan(s)** out of {len(lv_target_ids)} "
                 f"pinned LV classes: "
                 + (', '.join(f"{n} ({c})" for c, n in orphans) if orphans else "none"))
    lines.append("")

    # ── Base class count-only summary ────────────────────────────────────
    lines.append("## Base classes (count-only summary)")
    lines.append("")
    base_orphan_count = 0
    for cid in base_ids:
        entry = inbound.get(cid)
        total = inbound_total(entry) if entry else 0
        if total == 0:
            base_orphan_count += 1
    lines.append(f"- {len(base_ids)} base/unpinned classes disassembled.")
    lines.append(f"- {len(base_ids) - base_orphan_count} have at least one inbound "
                 f"reference by the mechanisms above.")
    lines.append(f"- {base_orphan_count} show zero inbound references by these "
                 f"mechanisms — expected noise for base game classes reached only "
                 f"via the runtime objId<256 permanent-NPC path (savegame blind "
                 f"spot, see flag-graph.md) or engine-internal triggers this tool "
                 f"does not model (schedule ticks, combat AI, etc.). Not audited "
                 f"further here.")
    lines.append("")

    # ── LV-window flag table ─────────────────────────────────────────────
    lines.append("## LV-window global flags (bit >= 1024)")
    lines.append("")
    lines.append(f"Retail-range summary (bit < 1024, base-game noise, not itemized): "
                 f"{retail_summary['distinct_bits']} distinct bits observed, "
                 f"{retail_summary['read_ops']} read ops, "
                 f"{retail_summary['write_ops']} write ops across all classes.")
    lines.append("")
    lines.append("| Bit | Name | Width | retail_shared | Writers | Readers |")
    lines.append("|---|---|---|---|---|---|")
    for bit in sorted(lv_flags):
        f = lv_flags[bit]
        writer_names = ', '.join(sorted(classname(flx, c, manifest_names) for c in f['writers'])) or '(none)'
        reader_names = ', '.join(sorted(classname(flx, c, manifest_names) for c in f['readers'])) or '(none)'
        width = f['width'] if f['width'] is not None else '?'
        rs = '' if f['retail_shared'] is None else ('yes' if f['retail_shared'] else 'no')
        lines.append(f"| {bit} | {f['name']} | {width} | {rs} | {writer_names} | {reader_names} |")
    lines.append("")

    # ── Suspicious flags ─────────────────────────────────────────────────
    read_never_written = [bit for bit in sorted(lv_flags)
                          if lv_flags[bit]['readers'] and not lv_flags[bit]['writers']]
    written_never_read = [bit for bit in sorted(lv_flags)
                          if lv_flags[bit]['writers'] and not lv_flags[bit]['readers']]

    lines.append("## Suspicious LV-window flags")
    lines.append("")
    lines.append(f"### Read, never written ({len(read_never_written)})")
    lines.append("")
    if read_never_written:
        for bit in read_never_written:
            lines.append(f"- bit {bit} `{lv_flags[bit]['name']}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append(f"### Written, never read ({len(written_never_read)})")
    lines.append("")
    if written_never_read:
        for bit in written_never_read:
            lines.append(f"- bit {bit} `{lv_flags[bit]['name']}`")
    else:
        lines.append("- none")
    lines.append("")

    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('flx', nargs='?',
                    default=os.path.join(REPO_ROOT, 'shared', 'build', 'EUSECODE.FLX'),
                    help='Path to EUSECODE.FLX (default: shared/build/EUSECODE.FLX)')
    ap.add_argument('--manifest', default=DEFAULT_MANIFEST)
    ap.add_argument('--fixed', default=DEFAULT_FIXED)
    ap.add_argument('--typeflag', default=DEFAULT_TYPEFLAG)
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args()

    t0 = time.time()

    manifest = load_manifest(args.manifest)
    manifest_names = build_manifest_name_index(manifest)
    bit_index = build_bit_index(manifest)
    lv_target_ids = set(manifest.get('classes', {}).values()) | \
        set(manifest.get('npc_classes', {}).values())

    flx, summaries, errors = disassemble_all(args.flx)

    map_archive = MapArchive(args.fixed)
    shapes = load_typeflag(args.typeflag)
    unkegg_shape_ids = {s.shape_id for s in shapes if not s.is_empty and s.family == 4}

    inbound = compute_inbound(summaries, map_archive, unkegg_shape_ids)

    lv_flags, retail_summary = build_flag_report(summaries, bit_index)
    anomalies = find_bitset_anomalies(flx, lv_flags, manifest_names)

    all_ids = set(summaries.keys())
    base_ids = sorted(all_ids - lv_target_ids)

    report = render_report(flx, args.flx, summaries, errors, manifest, inbound,
                           lv_flags, retail_summary, lv_target_ids, base_ids,
                           anomalies, manifest_names)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w') as f:
        f.write(report)

    elapsed = time.time() - t0

    # ── stdout summary for the human/agent running the tool ─────────────
    # inbound is a defaultdict; indexing a never-touched class id yields a
    # correct all-zero entry, so this is a safe orphan test.
    # Same split as the report table: a pin with no class in the FLX is
    # stale bookkeeping, not an unreachable shipped class.
    not_built = [cid for cid in sorted(lv_target_ids)
                 if not flx.class_exists(cid)]
    orphans = [cid for cid in sorted(lv_target_ids)
               if flx.class_exists(cid) and inbound_total(inbound[cid]) == 0]
    print(f"Disassembled {len(summaries)} classes ({len(errors)} errors) "
         f"in {elapsed:.1f}s")
    print(f"LV target classes: {len(lv_target_ids)}; orphans: {len(orphans)}; "
          f"stale pins: {len(not_built)}")
    for cid in orphans:
        print(f"  ORPHAN {cid} ({cid:04X}) {classname(flx, cid, manifest_names)}")
    for cid in not_built:
        print(f"  STALE PIN {cid} ({cid:04X}) "
              f"{classname(flx, cid, manifest_names)} — pinned but not built")
    if anomalies:
        print(f"WARNING: {len(anomalies)} flag bit(s) exceed the engine's "
             f"{GLOBAL_BITSET_CAPACITY}-bit capacity — suspected codegen defect, "
             f"see the report's Anomalies section")
        for bit, detail in anomalies:
            for cid, name, offsets in detail:
                off_str = ', '.join(f"{o:04X}" for o in offsets)
                print(f"  ANOMALY bit {bit} in class {name} ({cid}) at offset(s) {off_str}")
    print(f"Wrote {args.out}")


if __name__ == '__main__':
    main()
