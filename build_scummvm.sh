#!/bin/bash
# build_scummvm.sh — Build ScummVM with Lost Vale detection entry
#
# Clones ScummVM (or re-syncs an existing tree), applies the tracked engine
# patch, writes the Lost Vale detection entry for the current EUSECODE.FLX,
# then builds with only the Ultima engine.
#
# Prerequisites:
#   brew install sdl2
#   Xcode command-line tools (xcode-select --install)
#
# Usage:
#   ./build_scummvm.sh           # Build patched ScummVM
#   ./build_scummvm.sh --clean   # Remove build directory
#
# Normally run by tools/integrate.sh as one step of the integration cascade.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# LV_SCUMMVM_DIR builds a SECOND tree beside the normal one, and
# LV_CONFIGURE_EXTRA adds configure flags. Together they let one host
# carry both the normal binary and a --enable-text-console binary,
# whose debugger reads stdin instead of the in-game overlay.
SCUMMVM_DIR="${LV_SCUMMVM_DIR:-$SCRIPT_DIR/scummvm-lv}"
BUILD_FLX="$SCRIPT_DIR/shared/build/EUSECODE.FLX"

# The upstream ScummVM commit the engine patch is generated against. Its one
# copy lives in tools/lv_scummvm.py (bump it there, with the patch; see
# tools/scummvm-patches/README.md). The clone is pinned to it so a fresh
# build is reproducible and the tracked patch is guaranteed to apply.
LV_TOOL="$SCRIPT_DIR/tools/lv_scummvm.py"
SCUMMVM_BASE_SHA="$(python3 "$LV_TOOL" base)"
# The engine changes that make the restoration work (npcNum dispatch, NPC
# Actor promotion) live ONLY as this tracked patch. Without applying it a
# fresh clone builds a mute engine (adversarial-review C3).
ENGINE_PATCH="$SCRIPT_DIR/tools/scummvm-patches/0001-lost-vale-engine.patch"

# The detection entry's EUSECODE values (md5 of the first 5000 bytes, size)
# are COMPUTED from shared/build/EUSECODE.FLX on every run. They used to be
# hand-edited constants here, re-recorded after every usecode change, and
# they went stale silently for weeks more than once (a size-only change, an
# "unchanged" claim on bytes that had changed). Nothing to edit any more.
# eintro.skf is a base-game file and never moves.
EINTRO_MD5="b34169ece4286735262ac3430c441909"
EINTRO_SIZE="1297731"

if [ "${1:-}" = "--clean" ]; then
    echo "Removing ScummVM build directory..."
    rm -rf "$SCUMMVM_DIR"
    echo "Done."
    exit 0
fi

# ── Check prerequisites ──────────────────────────────────────────────────

if ! command -v git &>/dev/null; then
    echo "ERROR: git not found. Install Xcode command-line tools: xcode-select --install"
    exit 1
fi

if [ "$(uname -s)" = "Darwin" ]; then
    if ! brew list sdl2 &>/dev/null 2>&1; then
        echo "Installing SDL2..."
        brew install sdl2
    fi
elif ! pkg-config --exists sdl2 2>/dev/null; then
    echo "ERROR: SDL2 development files not found."
    echo "  Debian/Ubuntu: sudo apt install libsdl2-dev"
    exit 1
fi

if [ ! -f "$BUILD_FLX" ]; then
    echo "ERROR: EUSECODE.FLX not found at $BUILD_FLX"
    echo "  Run first: python3 agents/usecode-compiler/src/build_eusecode.py --full"
    exit 1
fi

# The detection values for THIS EUSECODE.FLX (md5 of its first 5000 bytes,
# and its size). Computed, never recorded: see the note at EINTRO_MD5.
read -r LV_MD5 LV_SIZE < <(python3 "$LV_TOOL" values "$BUILD_FLX")
if [ -z "${LV_MD5:-}" ] || [ -z "${LV_SIZE:-}" ]; then
    echo "ERROR: could not compute detection values from $BUILD_FLX"
    exit 1
fi
echo "EUSECODE.FLX detection values: md5-5000=$LV_MD5 size=$LV_SIZE"

# ── Clone ScummVM ────────────────────────────────────────────────────────

if [ ! -d "$SCUMMVM_DIR" ]; then
    if [ ! -f "$ENGINE_PATCH" ]; then
        echo "ERROR: engine patch not found at $ENGINE_PATCH"
        echo "  Cannot build a working Lost Vale engine without it (C3)."
        exit 1
    fi
    echo "Cloning ScummVM pinned to $SCUMMVM_BASE_SHA (depth 1)..."
    git init -q "$SCUMMVM_DIR"
    git -C "$SCUMMVM_DIR" remote add origin https://github.com/scummvm/scummvm.git
    # GitHub serves reachable commit SHAs directly, so a depth-1 fetch of the
    # exact base is minimal and reproducible.
    if ! git -C "$SCUMMVM_DIR" fetch --depth 1 --no-tags origin "$SCUMMVM_BASE_SHA"; then
        echo "ERROR: could not fetch pinned ScummVM base $SCUMMVM_BASE_SHA"
        rm -rf "$SCUMMVM_DIR"
        exit 1
    fi
    git -C "$SCUMMVM_DIR" checkout -q FETCH_HEAD

    # Apply the tracked engine patch. Fail loudly on any hunk that does not
    # apply — never silently build an engine missing the LV dispatch.
    echo "Applying Lost Vale engine patch..."
    if ! git -C "$SCUMMVM_DIR" apply --check "$ENGINE_PATCH" 2>/dev/null; then
        echo "ERROR: $ENGINE_PATCH does not apply cleanly to base"
        echo "  $SCUMMVM_BASE_SHA. Upstream likely drifted; regenerate the"
        echo "  patch (see tools/scummvm-patches/README.md) and update the pin."
        rm -rf "$SCUMMVM_DIR"
        exit 1
    fi
    git -C "$SCUMMVM_DIR" apply "$ENGINE_PATCH"
    python3 "$LV_TOOL" engine-check "$SCUMMVM_DIR" || exit 1
    echo "  Engine patch applied cleanly."
else
    echo "Using existing ScummVM source at $SCUMMVM_DIR"
    # An existing tree is NOT re-cloned, so a newer patch never reached it
    # and fork commits had to be copied in by hand. Compare its engines/
    # with base + the current patch, and rewrite exactly the files that
    # differ. A fork (commits past the base, e.g. scummvm-lv-console) is
    # never rewritten: its commits must equal the patch, or this fails and
    # says to regenerate the patch. Any other mismatch fails the build.
    if ! python3 "$LV_TOOL" engine-sync "$SCUMMVM_DIR"; then
        echo "ERROR: $SCUMMVM_DIR does not carry base + the current engine patch."
        exit 1
    fi
fi

# ── Patch detection table ────────────────────────────────────────────────

DETECTION_FILE="$SCUMMVM_DIR/engines/ultima/detection_tables.h"

if [ ! -f "$DETECTION_FILE" ]; then
    echo "ERROR: detection_tables.h not found at expected path."
    echo "  Looking for it..."
    find "$SCUMMVM_DIR/engines/ultima" -name "detection*" 2>/dev/null
    exit 1
fi

# Three-way: current entry / stale entry / no entry. "Current" means BOTH
# values match: md5-5000 alone was the old test, and a size-only change (a
# class appended past the first 5000 bytes) passed it and kept the stale
# size, which is enough to break detection.
if python3 "$LV_TOOL" detection-check "$DETECTION_FILE" "$BUILD_FLX" 2>/dev/null; then
    echo "Detection table already carries the current values."
elif grep -q "Lost Vale" "$DETECTION_FILE" 2>/dev/null; then
    echo "Detection table has a stale Lost Vale entry — updating it in place..."
    # Bounded to the Lost Vale entry: the vanilla U8 variants also list
    # eusecode.flx, and an unbounded replacement once corrupted stock-game
    # detection. (build_eusecode.py's auto-update carries the same bound.)
    python3 "$LV_TOOL" detection-update "$DETECTION_FILE" "$BUILD_FLX" || exit 1
else
    echo "Patching detection table..."
    # Insert our entry right after the GOG Gold Edition entry.
    # We search for the Gold Edition entry's unique MD5 and insert after the closing brace.
    python3 -c "
import sys

detection_file = sys.argv[1]
lv_md5 = sys.argv[2]
lv_size = sys.argv[3]
eintro_md5 = sys.argv[4]
eintro_size = sys.argv[5]

with open(detection_file, 'r') as f:
    content = f.read()

# The entry to insert (after the GOG Gold Edition entry)
new_entry = '''
\t// GOG Gold Edition + The Lost Vale expansion (fan restoration)
\t{
\t\t{
\t\t\t\"ultima8\",
\t\t\t\"Gold Edition + Lost Vale\",
\t\t\tAD_ENTRY2s(\"usecode/eusecode.flx\", \"''' + lv_md5 + '''\", ''' + lv_size + ''',
\t\t\t\t\t   \"static/eintro.skf\", \"''' + eintro_md5 + '''\", ''' + eintro_size + '''),
\t\t\tCommon::EN_ANY,
\t\t\tCommon::kPlatformDOS,
\t\t\tADGF_NO_FLAGS,
\t\t\tGUI_OPTIONS_ULTIMA8
\t\t},
\t\tGAME_ULTIMA8,
\t\t0
\t},
'''

# Find the GOG Gold Edition entry by its unique MD5
marker = 'c61f1dacde591cb39d452264e281f234'
pos = content.find(marker)
if pos < 0:
    print('ERROR: Could not find GOG Gold Edition entry in detection_tables.h', file=sys.stderr)
    sys.exit(1)

# Find the closing '},' of this entry block (search for '0\\n\\t},' pattern)
# The entry ends with: GAME_ULTIMA8,\\n\\t\\t0\\n\\t},
end_marker = 'GAME_ULTIMA8,\n\t\t0\n\t},'
end_pos = content.find(end_marker, pos)
if end_pos < 0:
    # Try with different whitespace
    end_marker = 'GAME_ULTIMA8,\n\t0\n\t},'
    end_pos = content.find(end_marker, pos)
if end_pos < 0:
    print('ERROR: Could not find end of GOG Gold Edition entry', file=sys.stderr)
    sys.exit(1)

insert_pos = end_pos + len(end_marker)
content = content[:insert_pos] + new_entry + content[insert_pos:]

with open(detection_file, 'w') as f:
    f.write(content)

print('  Inserted Lost Vale detection entry after GOG Gold Edition entry.')
" "$DETECTION_FILE" "$LV_MD5" "$LV_SIZE" "$EINTRO_MD5" "$EINTRO_SIZE"
fi

# Whatever path was taken above, the entry must now carry this FLX's values.
python3 "$LV_TOOL" detection-check "$DETECTION_FILE" "$BUILD_FLX" || exit 1

# ── Configure & Build ────────────────────────────────────────────────────

cd "$SCUMMVM_DIR"

NCPUS=$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 4)

if [ ! -f "config.mk" ]; then
    echo ""
    echo "Configuring ScummVM (Ultima engine only)..."
    # --disable-gtk: the gtk dialog backend (native file-open dialogs) is not
    # needed to run the game, and gtk+3 is a recurring breakage on this
    # machine — Homebrew has removed/renamed it twice, leaving a config.mk
    # that references gtk headers no longer on disk and failing the link on
    # backends/dialogs/gtk/gtk-dialogs.o. Disabling it removes that fragility.
    ./configure --disable-all-engines --enable-engine=ultima --disable-gtk \
        ${LV_CONFIGURE_EXTRA:-}
fi

# Ensure Ultima 8 sub-engine is enabled (configure only enables the meta-engine)
if grep -q '^# ENABLE_ULTIMA8' config.mk 2>/dev/null; then
    echo "Enabling Ultima 8 sub-engine..."
    # BSD sed needs an explicit empty suffix after -i; GNU sed rejects it.
    if sed --version >/dev/null 2>&1; then
        sed -i    's/^# ENABLE_ULTIMA8/ENABLE_ULTIMA8 = STATIC_PLUGIN/' config.mk
    else
        sed -i '' 's/^# ENABLE_ULTIMA8/ENABLE_ULTIMA8 = STATIC_PLUGIN/' config.mk
    fi
fi

echo ""
echo "Building ScummVM with $NCPUS parallel jobs..."
echo "  (This may take 5-15 minutes on first build)"
echo ""
make -j"$NCPUS"

BINARY="$SCUMMVM_DIR/scummvm"
if [ ! -f "$BINARY" ]; then
    echo "ERROR: Build failed — scummvm binary not found."
    exit 1
fi

echo ""
echo "=== Build complete ==="
echo ""
echo "Patched ScummVM binary: $BINARY"
echo "  engine sources: base ${SCUMMVM_BASE_SHA:0:8} + $(basename "$ENGINE_PATCH")"
echo "  detection:      md5-5000=$LV_MD5 size=$LV_SIZE"
echo ""
echo "To use it:"
echo "  $BINARY --debuglevel=1 ultima8"
echo ""
echo "Or update install_lv.sh to use it:"
echo "  SCUMMVM=$BINARY ./install_lv.sh --run"
