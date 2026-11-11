---
paths:
  - "shared/build/**"
  - "tools/build_artifacts.sh"
  - "agents/usecode-compiler/src/build_eusecode.py"
  - "agents/map-populator/src/build_all_maps.py"
---

# Never commit a merged artifact. Never renumber a pinned ID.

## The six artifacts are not tracked, and must never become tracked (M22)

`TYPEFLAG.DAT`, `U8SHAPES.FLX`, `ANIM.DAT`, `EUSECODE.FLX`, `FIXED.DAT`, and `GLOB.FLX` under
`shared/build/` each fuse our work with Origin-copyrighted bytes. The repo has
no right to redistribute them. They were tracked until 2026-07-25 and were
purged from history; do not undo that. `ANIM.DAT` joined them on 2026-10-08
(the Tiny Tar body, shape 867) and was never tracked.

A fresh clone has none of them. Build from your own game data:

```bash
tools/build_artifacts.sh     # builds all six, verifies the canonical hashes
```

`.staging` and `.failed` byproducts are gitignored too. `.failed` in
particular is a known-corrupt artifact quarantined for inspection — never
commit one, never promote one by hand.

## What IS tracked

`shared/build/ARTIFACTS.sha256` — the canonical hash of each artifact. This is
how the reproducibility guarantee survives without committing a byte of game
data. `tools/build_artifacts.sh` verifies against it; `--record` rewrites it
for a deliberate artifact change.

`shared/build/lv_manifest.json` — the pinned IDs. See below.

## Build order is load-bearing

Nine steps:

```
TYPEFLAG → U8SHAPES (wood walls) → U8SHAPES+TYPEFLAG (Tiny Tar potion 859)
        → U8SHAPES+TYPEFLAG (Zealan gods 860)
        → U8SHAPES+TYPEFLAG (art-track static props, 863+; 861/862 retired, 870 = copy of 878)
        → U8SHAPES+TYPEFLAG+ANIM.DAT (actors: Tiny Tar 867, Water Zombie 872, Harpie 873)
        → EUSECODE → GLOB → FIXED
```

The map build's validator reads the *patched* `TYPEFLAG.DAT` and
`U8SHAPES.FLX`, so those come first. Reordering silently produces a build that
validates against the wrong inputs.

Every custom-art injection is a numbered step here. Static props share one
table-driven step (`lv_art_props.py`, a row per prop — `docs/art-track.md`),
so the count grows only for a shape that needs its own anim entry or class.
An actor shape needs all three of sprite, TYPEFLAG row and `ANIM.DAT` entry
(the engine keys actor animation by shape number), and step 6 is the actor
step: `lv_tiny_avatar.py` writes `ANIM.DAT` from the pristine base (867's own
appended table), then `lv_monsters.py` adds a row per monster clone (872,
the Water Zombie, sharing the ghoul's table; 873, the Harpie, the torax's).
A monster also needs a
`u8monsters.ini` row keyed by its shape, or it hatches with no hit points;
that is engine data, not an artifact, and `install_lv.sh` writes it into
the game directory (`docs/art-track.md` contract 9).
A shape injected by hand into `shared/build/U8SHAPES.FLX` survives exactly
until the next rebuild — see `.claude/rules/shape-ids.md`.

## Savegame-visible IDs are frozen forever (M0.6)

Class IDs and global flag bits are pinned in `shared/build/lv_manifest.json`.
**Never renumber a pin. Never reuse a retired bit.** Both break existing
saves, and a broken save is not recoverable by rebuilding.

The build enforces this — it fails on overlapping flag-bit pins, cross-group
class-ID collisions, a pin that cannot be honored, a pinned flag width that
disagrees with the source declaration, or an unpinned allocation landing
inside a pinned range. If you are fighting that gate, the gate is right.

## Builds stage, verify, then promote (P2, L12)

`EUSECODE.FLX` `FIXED.DAT`, and `GLOB.FLX` are written to `<artifact>.staging`, verified
there, and only then `os.replace()`d over the canonical path. A rejected build
is quarantined as `<artifact>.failed` and the previous good artifact is left
byte-for-byte untouched. Step 6 (`lv_tiny_avatar.py`) does the same for all
three files it writes: none is promoted unless all three verify.

Preserve this shape in any new build step. Writing directly to the canonical
path destroys the last verified build on failure — that is the exact bug P2
existed to fix.

## Changing an artifact deliberately

Use the `/artifact-rehash` skill. The hash change cascades into the
ScummVM detection entry, the binary, the install and the playtest harness.
`tools/integrate.sh --record` runs that cascade (`/integrate`). Skipping it
ships a build ScummVM will not detect.

`GLOB.FLX` preserves all 3,072 retail slots and appends LV slots from 3072.
Glob IDs and content hashes are append-only pins in `lv_manifest.json`.
The glob build stages and round-trips every slot before promotion.
