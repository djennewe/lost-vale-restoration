# ScummVM engine patches for The Lost Vale

These patches are the **only tracked copy** of the ScummVM engine changes that
make the restoration function. Before they existed here, the changes lived
solely as commits inside the gitignored `scummvm-lv/` checkout, and
`./build_scummvm.sh --clean` (`rm -rf scummvm-lv`) would have destroyed them
with no backup (adversarial-review finding **C3**).

`build_scummvm.sh` applies `0001-lost-vale-engine.patch` automatically after
cloning, and **fails the build loudly** if any hunk does not apply — never
silently producing an engine without the Lost Vale changes. On an EXISTING
tree it compares `engines/` with base + this patch and rewrites exactly the
files that differ (`tools/lv_scummvm.py engine-sync`), so a newer patch
reaches `scummvm-lv/` without a re-clone. A fork tree (commits past the
base) is never rewritten; its commits must equal the patch or the build
fails. `tools/integrate.sh --fork` regenerates the patch from the fork.

## Base commit (pin)

The patch is generated against, and must be applied to, upstream ScummVM:

    01bd88796f47b21ce8e985a94a6c284439b6f032
    "PSP2: Use toolchain pkg-config"  (master, 2026-03-22)

`build_scummvm.sh` pins its clone to this SHA, so a fresh build is
reproducible and the patch is guaranteed to apply. The pin's one copy is
`BASE_SHA` in `tools/lv_scummvm.py` (build_scummvm.sh and the tests read it
from there). To move to a newer upstream base, check the patch still
applies to the new SHA (`git apply --check`), regenerate it if upstream
touched the same lines, then update both `BASE_SHA` and the SHA above.

## What `0001-lost-vale-engine.patch` contains

Three files, +78 lines, no deletions. Detection-table entries are **not**
included here — `build_scummvm.sh` regenerates those itself (md5 + size change
every build).

- `engines/ultima/ultima8/world/item.cpp` — `npcNum + 1024` usecode dispatch
  for FIXED.DAT NPC items, so placed NPCs reach their dialogue usecode without
  being in `ITEMCACH.DAT`. Excludes egg families (they pack hatch x/y ranges
  into `_npcNum`) and only fires when the target class actually has usecode.
- `engines/ultima/ultima8/world/map.cpp` — promotes FIXED.DAT items with
  `npcNum` 100-116 on LV maps (9/10/11/13/17/18) to real `Actor`s in the
  `ObjectManager`, with default village-NPC stats, so `npcNum+1024` dispatch
  has an actor to run against.
- `engines/ultima/ultima8/kernel/kernel.cpp` — one `debug(1, ...)` trace in
  `I_resetRef` (diagnostic only, gated behind `--debuglevel=1`).

## Regenerating the patch

From a `scummvm-lv/` checkout whose HEAD carries the engine work:

    git diff <SCUMMVM_BASE_SHA> HEAD -- \
      engines/ultima/ultima8/world/item.cpp \
      engines/ultima/ultima8/world/map.cpp \
      engines/ultima/ultima8/kernel/kernel.cpp \
      > tools/scummvm-patches/0001-lost-vale-engine.patch
