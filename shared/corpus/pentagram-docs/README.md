# Pentagram U8 reference specs (pinned)

Pinned copies of the Pentagram project's Ultima 8 file-format and VM
documentation, fetched **2026-07-25**.

Every `.txt` in this directory is the upstream file **byte for byte**, preceded
by a five-line `--- PINNED ... ---` provenance block that records the source
URL, the byte count, and a sha256 of the body. Strip the header block and you
have the original file. Nothing was reflowed, reformatted, or summarised.

Upstream repository: `github.com/pentagram-u8/pentagram`, branch `master`.
All 13 files fetched over HTTPS with `curl`, every one returning **HTTP 200**.
No archive.org fallback was needed and no mirror was used.

## Read this first

**Pentagram's docs are historical, and in several places wrong.** They date
from 1996 to 2005 and predate the working engine. The live ScummVM Ultima 8
engine is the authority for this project.

> Where a document here disagrees with ScummVM, **ScummVM wins**.
> The disagreements we found are enumerated in
> [SCUMMVM-DELTA.md](SCUMMVM-DELTA.md), with file and line evidence on both
> sides. Read that before trusting any byte layout below.

The single most important thing in that file: `u8usecode.txt` **does not contain
an opcode table at all**, so the opcode cross-check had to be run against
Pentagram's source instead. See the "Supplementary" section.

## The seven requested documents

| File | Covers | Source URL | Status |
|---|---|---|---|
| `u8usecode.txt` | EUSECODE.FLX layout: entry numbering (`2+x` for shape *x*, `1026+x` for NPC *x*), the 12-byte class header, and the 32-entry event-id pointer table with per-event meanings. **No opcode table.** | `.../master/docs/u8usecode.txt` | **verbatim** (2171 B) |
| `u8mapfmt.txt` | FIXED.DAT / NONFIXED.DAT header and the 16-byte map item record; GLOB.FLX layout and glob placement formulas; ITEMCACH.DAT; the original 1994 savegame container. | `.../master/docs/u8mapfmt.txt` | **verbatim** (6321 B) |
| `u8typeflag.txt` | TYPEFLAG.DAT: 8 bytes per shape for 2048 shapes, bitfield meanings, and the animation type/data semantics. Most bytes are marked "Unknown". | `.../master/docs/u8typeflag.txt` | **verbatim** (1499 B) |
| `u8gfxfmt.txt` | U8SHAPES.FLX / U8GUMPS.FLX / U8FONTS.FLX shape and frame format, RLE row compression, and the palette format. | `.../master/docs/u8gfxfmt.txt` | **verbatim** (6894 B) |
| `shapes.cmp.txt` | The compressed-shape (`shapes.cmp`) variant format. | `.../master/docs/shapes.cmp.txt` | **verbatim** (2820 B) |
| `u8anim.txt` | ANIM.DAT: the 2048-entry shape lookup, the 64-action tables, frame-sequence headers, and the action name list. | `.../master/docs/u8anim.txt` | **verbatim** (2790 B) |
| `savegame.txt` | **Pentagram's own** savegame container and section list, not the original U8 format. ScummVM replaced the container. | `.../master/docs/savegame.txt` | **verbatim** (9687 B) |

Nothing failed to fetch. **7 of 7 requested documents obtained verbatim.**

## Supplementary files (also pinned)

`u8usecode.txt` turned out to document only the container and the event table.
Pentagram has no opcode-table document: its opcode knowledge lives in source.
These were fetched so the opcode and intrinsic cross-checks had a real
Pentagram-side reference to compare against.

| File | Covers | Source URL | Status |
|---|---|---|---|
| `convert-Convert.h.txt` | **The authoritative Pentagram opcode table.** `readOpGeneric()` is the per-opcode operand-size switch. This is what an "opcode spec" would have been. | `.../master/convert/Convert.h` | **verbatim** (29823 B) |
| `convert-u8-ConvertUsecodeU8.h.txt` | Pentagram's U8 intrinsic name table (`_intrinsics[]`, 257 entries) and event-name table. This is the origin of our own 258-entry table. | `.../master/convert/u8/ConvertUsecodeU8.h` | **verbatim** (13890 B) |
| `tools-disasm-Disasm.cpp.txt` | Pentagram's disassembler print layer: the mnemonic each opcode is rendered as. | `.../master/tools/disasm/Disasm.cpp` | **verbatim** (24136 B) |
| `usecode-u8intrinsics.h.txt` | Pentagram's runtime intrinsic dispatch table, the ancestor of ScummVM's `u8_intrinsics.h`. | `.../master/usecode/u8intrinsics.h` | **verbatim** (7071 B) |
| `design-ucmachine.txt` | VM design notes: the segmented pointer scheme (object / stack / string segments) that ScummVM still implements. | `.../master/docs/design/ucmachine.txt` | **verbatim** (7613 B) |
| `u8encoding.txt` | U8's character encoding (CP850 with `0x40` remapped to U+2022 BULLET). Relevant to string literals in compiled usecode. | `.../master/docs/u8encoding.txt` | **verbatim** (10791 B) |

## Not fetched

The upstream `docs/` folder holds other files that were out of scope for this
task and are not pinned here: `u8bugs.txt`, `u8cheat.txt`, `u8fonts.txt`,
`u8npc.txt`, `u8savfmt.txt`, `u8sfxfmt.txt`, `u8skf.txt`, `u8weapon.txt`,
`u8wpnovlay.txt`, `maps.txt`, `musiceggs.txt`, `musicflx.txt`, `snippets.txt`,
`features.txt`, `cvs_structure.txt`, plus the `docs/design/` and `docs/xml/`
subtrees. They are all reachable at
`https://raw.githubusercontent.com/pentagram-u8/pentagram/master/docs/<name>`.

## Re-verifying a pin

Each header carries the sha256 of the body. To confirm a file has not drifted:

```bash
tail -n +8 u8mapfmt.txt | shasum -a 256
```

(the header is 6 text lines followed by one blank line, so the body starts at
line 8).
