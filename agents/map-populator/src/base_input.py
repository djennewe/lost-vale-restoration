"""Select a pristine base-game input file, surviving install_lv.sh.

install_lv.sh installs the five merged artifacts INTO shared/data/u8-install
-- the same directory the artifact builders read their base-game inputs from
-- keeping a one-time `X.bak` of the pre-install pristine file. A rebuild
after an install therefore silently merges LV content into itself. This was
caught live 2026-07-27: the "base" FIXED.DAT was the previous night's built
artifact (installed at 00:21, one minute after the build), so the next
build_all_maps.py run produced duplicate Map 8 teleport eggs and failed its
own teleport verification. TYPEFLAG.DAT and U8SHAPES.FLX were clobbered the
same way (their patches happen to be idempotent, which only means the trap
stays invisible there until it isn't -- e.g. a hand-run png2shape injection
in the install dir would silently become part of the "canonical" build).

Rule: if `X.bak` exists and differs from `X`, then X has been overwritten by
an install -- read the .bak (install_lv.sh's contract is that .bak is the
pre-first-install pristine file, and --clean restores it). An optional
sanity predicate then proves the chosen file really is pristine; if it
fails, abort rather than build garbage.

The EUSECODE.FLX builder is not exposed: it reads shared/data/USECODE.FLX,
a separate copy install_lv.sh never touches.
"""

import os


def _same_bytes(a, b):
    if os.path.getsize(a) != os.path.getsize(b):
        return False
    with open(a, 'rb') as fa, open(b, 'rb') as fb:
        while True:
            ca, cb = fa.read(1 << 20), fb.read(1 << 20)
            if ca != cb:
                return False
            if not ca:
                return True


def pristine_base(path, is_pristine=None, what=''):
    """Return the path to read the base-game input from.

    path        -- the canonical base file under shared/data/u8-install
    is_pristine -- optional predicate(path) -> bool proving the candidate
                   contains no LV content; a False result is a hard abort
    what        -- label for messages (e.g. 'FIXED.DAT base')
    """
    label = what or os.path.basename(path)
    chosen = path
    bak = path + '.bak'
    if os.path.exists(bak) and not _same_bytes(path, bak):
        print(f"   NOTE: {label}: the file differs from its .bak — an "
              f"install_lv.sh run has overwritten the base with a built "
              f"artifact. Reading the pristine .bak instead:\n"
              f"   {bak}")
        chosen = bak
    if is_pristine is not None and not is_pristine(chosen):
        raise SystemExit(
            f"ERROR: {label}: {chosen} already contains Lost Vale content "
            f"and no pristine copy could be found beside it. Restore the "
            f"base game file (re-extract from your GOG data, or run "
            f"install_lv.sh --clean) and rebuild.")
    return chosen
