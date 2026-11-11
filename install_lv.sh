#!/bin/bash
# install_lv.sh — Install Lost Vale build artifacts for ScummVM
#
# By default this installs into a SEPARATE copy of your game,
# shared/u8-lv-patched/ (created from shared/data/u8-install/ on first run),
# and launches ScummVM on that copy by path. It never touches the Ultima 8
# folder registered in your ScummVM configuration, and never edits that
# configuration: the launch uses its own config file and save folder inside
# the copy (scummvm-lv.ini, saves/).
#
# --in-place is the development workflow (tools/integrate.sh uses it): it
# installs over the folder registered as [ultima8] in your ScummVM config,
# or over shared/data/u8-install if none is registered, keeping .bak copies,
# and points the [ultima8] entry at that folder.
#
# Usage:
#   ./install_lv.sh                    # Install into shared/u8-lv-patched/
#   ./install_lv.sh --run              # Install and launch ScummVM on it
#   ./install_lv.sh --in-place [--run] # Development: install in place
#   ./install_lv.sh --clean            # Restore files an --in-place install replaced
#   (remove the separate copy with: rm -rf shared/u8-lv-patched)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_GAME="$SCRIPT_DIR/shared/data/u8-install"
BUILD_DIR="$SCRIPT_DIR/shared/build"
PLAYER_DIR="$SCRIPT_DIR/shared/u8-lv-patched"

RUN=0; IN_PLACE=0; CLEAN=0
for arg in "$@"; do
    case "$arg" in
        --run)      RUN=1 ;;
        --in-place) IN_PLACE=1 ;;
        --clean)    CLEAN=1 ;;
        -h|--help)  sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *)          echo "Unknown option: $arg (try --help)"; exit 2 ;;
    esac
done

# ── Detect ScummVM's registered ultima8 game path ─────────────────────────

detect_scummvm_path() {
    local prefs=""
    # macOS
    if [ -f "$HOME/Library/Preferences/ScummVM Preferences" ]; then
        prefs="$HOME/Library/Preferences/ScummVM Preferences"
    # Linux / XDG
    elif [ -f "$HOME/.config/scummvm/scummvm.ini" ]; then
        prefs="$HOME/.config/scummvm/scummvm.ini"
    fi

    if [ -n "$prefs" ]; then
        # Extract path from [ultima8] section. The `|| true` matters: with
        # `set -euo pipefail`, a config that has no [ultima8] path= line
        # (normal on a host that only ever launches via -p, like the Linux
        # playtest harness) makes grep exit 1 inside this command
        # substitution and the whole script dies BEFORE ITS FIRST ECHO —
        # exit 1, zero output. Cost a debugging session on 2026-07-26.
        sed -n '/^\[ultima8\]/,/^\[/p' "$prefs" | grep '^path=' | head -1 | cut -d= -f2- || true
    fi
}

SCUMMVM_U8_PATH="$(detect_scummvm_path)"

# ── Preflight checks ──────────────────────────────────────────────────────

check_prereqs() {
    local ok=true

    if [ ! -d "$BASE_GAME" ]; then
        echo "ERROR: Base game not found at $BASE_GAME"
        echo "  Extract your Ultima 8 GOG install there first."
        ok=false
    fi

    # M22: the merged artifacts are not tracked in git — they fuse our work
    # with Origin-copyrighted bytes — so a fresh clone has none of them and
    # must build them from the player's own install first.
    local missing_artifacts=()
    for artifact in EUSECODE.FLX FIXED.DAT U8SHAPES.FLX TYPEFLAG.DAT ANIM.DAT GLOB.FLX; do
        [ -f "$BUILD_DIR/$artifact" ] || missing_artifacts+=("$artifact")
    done
    if [ "${#missing_artifacts[@]}" -gt 0 ]; then
        echo "ERROR: missing build artifact(s) in $BUILD_DIR:"
        printf '         %s\n' "${missing_artifacts[@]}"
        echo "  These are built from your own game data, not shipped."
        echo "  Run: tools/build_artifacts.sh"
        ok=false
    fi

    if [ "$IN_PLACE" != 1 ]; then
        :
    elif [ -z "$SCUMMVM_U8_PATH" ]; then
        echo "WARNING: No 'ultima8' target found in ScummVM config."
        echo "  Add Ultima 8 to ScummVM first (Add Game → browse to U8 directory)."
    elif [ ! -d "$SCUMMVM_U8_PATH" ]; then
        echo "WARNING: ScummVM ultima8 path does not exist: $SCUMMVM_U8_PATH"
        echo "  Will update ScummVM config to use the base game directory."
        SCUMMVM_U8_PATH=""
    fi

    if [ "$ok" = false ]; then
        exit 1
    fi
}

# ── Clean ─────────────────────────────────────────────────────────────────

if [ "$CLEAN" = 1 ]; then
    CLEAN_DIR="${SCUMMVM_U8_PATH:-$BASE_GAME}"
    if [ ! -d "$CLEAN_DIR" ]; then
        CLEAN_DIR="$BASE_GAME"
    fi
    if [ -f "$CLEAN_DIR/USECODE/EUSECODE.FLX.bak" ]; then
        echo "Restoring original EUSECODE.FLX..."
        mv "$CLEAN_DIR/USECODE/EUSECODE.FLX.bak" "$CLEAN_DIR/USECODE/EUSECODE.FLX"
        echo "Restoring original FIXED.DAT..."
        mv "$CLEAN_DIR/STATIC/FIXED.DAT.bak" "$CLEAN_DIR/STATIC/FIXED.DAT"
        if [ -f "$CLEAN_DIR/STATIC/U8SHAPES.FLX.bak" ]; then
            echo "Restoring original U8SHAPES.FLX..."
            mv "$CLEAN_DIR/STATIC/U8SHAPES.FLX.bak" "$CLEAN_DIR/STATIC/U8SHAPES.FLX"
        fi
        if [ -f "$CLEAN_DIR/STATIC/TYPEFLAG.DAT.bak" ]; then
            echo "Restoring original TYPEFLAG.DAT..."
            mv "$CLEAN_DIR/STATIC/TYPEFLAG.DAT.bak" "$CLEAN_DIR/STATIC/TYPEFLAG.DAT"
        fi
        if [ -f "$CLEAN_DIR/STATIC/ANIM.DAT.bak" ]; then
            echo "Restoring original ANIM.DAT..."
            mv "$CLEAN_DIR/STATIC/ANIM.DAT.bak" "$CLEAN_DIR/STATIC/ANIM.DAT"
        fi
        if [ -f "$CLEAN_DIR/STATIC/GLOB.FLX.bak" ]; then
            mv "$CLEAN_DIR/STATIC/GLOB.FLX.bak" "$CLEAN_DIR/STATIC/GLOB.FLX"
        fi
        # Only the file lv_monsters.py wrote: it carries its marker line.
        if grep -qs 'Lost Vale: rows appended by' "$CLEAN_DIR/u8monsters.ini"; then
            echo "Removing the LV u8monsters.ini..."
            rm -f "$CLEAN_DIR/u8monsters.ini"
        fi
        echo "Restored base game files in $CLEAN_DIR"
    else
        echo "Nothing to clean (no .bak files found in $CLEAN_DIR)."
    fi
    if [ -d "$PLAYER_DIR" ]; then
        echo "The separate game copy is untouched: $PLAYER_DIR"
        echo "  Remove it with: rm -rf \"$PLAYER_DIR\""
    fi
    exit 0
fi

check_prereqs

# ── Install ───────────────────────────────────────────────────────────────

if [ "$IN_PLACE" = 1 ]; then
    # If ScummVM path is missing/stale, use our base game copy
    if [ -z "$SCUMMVM_U8_PATH" ]; then
        SCUMMVM_U8_PATH="$BASE_GAME"
    fi
    TARGET_DIR="$SCUMMVM_U8_PATH"
else
    TARGET_DIR="$PLAYER_DIR"
    if [ ! -d "$TARGET_DIR/USECODE" ] || [ ! -d "$TARGET_DIR/STATIC" ]; then
        echo "Creating a separate game copy for Lost Vale:"
        echo "  $BASE_GAME -> $TARGET_DIR"
        mkdir -p "$TARGET_DIR"
        cp -R "$BASE_GAME/." "$TARGET_DIR/"
        # An old --in-place install may have left .bak files in the base.
        find "$TARGET_DIR" -name '*.bak' -type f -delete
    fi
fi

echo "=== Lost Vale Installer ==="
echo ""
echo "Build:      $BUILD_DIR"
echo "Target:     $TARGET_DIR"
echo ""

# Verify target has the expected subdirectories
if [ ! -d "$TARGET_DIR/USECODE" ] || [ ! -d "$TARGET_DIR/STATIC" ]; then
    echo "ERROR: Target directory missing USECODE/ or STATIC/ subdirectories."
    echo "  Expected U8 game layout at: $TARGET_DIR"
    exit 1
fi

# Back up originals (only if not already backed up)
if [ ! -f "$TARGET_DIR/USECODE/EUSECODE.FLX.bak" ]; then
    echo "1. Backing up original files..."
    cp "$TARGET_DIR/USECODE/EUSECODE.FLX" "$TARGET_DIR/USECODE/EUSECODE.FLX.bak"
    cp "$TARGET_DIR/STATIC/FIXED.DAT" "$TARGET_DIR/STATIC/FIXED.DAT.bak"
else
    echo "1. Backups already exist (use --clean to restore originals)"
fi

# Patch EUSECODE.FLX
echo "2. Installing EUSECODE.FLX ($(du -h "$BUILD_DIR/EUSECODE.FLX" | cut -f1) — the Lost Vale usecode)..."
cp "$BUILD_DIR/EUSECODE.FLX" "$TARGET_DIR/USECODE/EUSECODE.FLX"

# Patch FIXED.DAT
echo "3. Installing FIXED.DAT ($(du -h "$BUILD_DIR/FIXED.DAT" | cut -f1) — base maps plus the Lost Vale maps)..."
cp "$BUILD_DIR/FIXED.DAT" "$TARGET_DIR/STATIC/FIXED.DAT"

# Patch U8SHAPES.FLX (the Lost Vale shapes)
if [ -f "$BUILD_DIR/U8SHAPES.FLX" ]; then
    if [ ! -f "$TARGET_DIR/STATIC/U8SHAPES.FLX.bak" ]; then
        cp "$TARGET_DIR/STATIC/U8SHAPES.FLX" "$TARGET_DIR/STATIC/U8SHAPES.FLX.bak"
    fi
    echo "4. Installing U8SHAPES.FLX ($(du -h "$BUILD_DIR/U8SHAPES.FLX" | cut -f1) — the Lost Vale shapes)..."
    cp "$BUILD_DIR/U8SHAPES.FLX" "$TARGET_DIR/STATIC/U8SHAPES.FLX"
fi

# Patch TYPEFLAG.DAT (entries for the Lost Vale shapes)
if [ -f "$BUILD_DIR/TYPEFLAG.DAT" ]; then
    if [ ! -f "$TARGET_DIR/STATIC/TYPEFLAG.DAT.bak" ]; then
        cp "$TARGET_DIR/STATIC/TYPEFLAG.DAT" "$TARGET_DIR/STATIC/TYPEFLAG.DAT.bak"
    fi
    echo "5. Installing TYPEFLAG.DAT ($(du -h "$BUILD_DIR/TYPEFLAG.DAT" | cut -f1) — entries for the Lost Vale shapes)..."
    cp "$BUILD_DIR/TYPEFLAG.DAT" "$TARGET_DIR/STATIC/TYPEFLAG.DAT"
fi

# Install append-only LV prefabs, preserving the player's retail archive.
if [ ! -f "$TARGET_DIR/STATIC/GLOB.FLX.bak" ]; then
    cp "$TARGET_DIR/STATIC/GLOB.FLX" "$TARGET_DIR/STATIC/GLOB.FLX.bak"
fi
cp "$BUILD_DIR/GLOB.FLX" "$TARGET_DIR/STATIC/GLOB.FLX"

# Patch ANIM.DAT (actor animation for shape 867, the Tiny Tar body). Without
# it the shrunken Avatar is an actor shape with no animation entry, which
# the engine refuses to move.
if [ -f "$BUILD_DIR/ANIM.DAT" ]; then
    if [ ! -f "$TARGET_DIR/STATIC/ANIM.DAT.bak" ]; then
        cp "$TARGET_DIR/STATIC/ANIM.DAT" "$TARGET_DIR/STATIC/ANIM.DAT.bak"
    fi
    echo "6. Installing ANIM.DAT ($(du -h "$BUILD_DIR/ANIM.DAT" | cut -f1) — animation entry for the Tiny Tar body, shape 867)..."
    cp "$BUILD_DIR/ANIM.DAT" "$TARGET_DIR/STATIC/ANIM.DAT"
fi

# Write u8monsters.ini (the monster stats for the LV actor shapes, 872 the
# Water Zombie and 873 the Harpie). The engine reads the file by bare name through ScummVM's
# search path (game_data.cpp:261); its own copy is inside the engine-data
# zip ultima8.dat, and the game directory is searched before that zip
# (docs/art-track.md contract 9). So the game directory gets the WHOLE
# engine file, regenerated from the patched build's own ultima8.dat every
# install so it cannot drift, plus one row per LV monster copied from its
# donor's with the monster's own overrides (the Harpie's hp, damage, armour
# and defense: agents/map-populator/src/lv_monsters.py MONSTERS). Without the rows a
# hatched Water Zombie has no MonsterInfo: no hit points, no alignment.
U8DAT=""
for cand in "$SCRIPT_DIR/scummvm-lv/ultima8.dat" \
            "$SCRIPT_DIR/scummvm-lv/dists/engine-data/ultima8.dat"; do
    if [ -f "$cand" ]; then U8DAT="$cand"; break; fi
done
if [ -z "$U8DAT" ]; then
    echo "ERROR: no ultima8.dat in scummvm-lv/ or scummvm-lv/dists/engine-data/."
    echo "  Build the patched ScummVM first: ./build_scummvm.sh"
    exit 1
fi
ENGINE_INI="$(mktemp)"
unzip -p "$U8DAT" u8monsters.ini > "$ENGINE_INI"
echo "7. Writing u8monsters.ini (engine rows from $U8DAT + the LV monsters)..."
python3 "$SCRIPT_DIR/agents/map-populator/src/lv_monsters.py" ini \
    "$ENGINE_INI" "$TARGET_DIR/u8monsters.ini"
rm -f "$ENGINE_INI"

# Update ScummVM config to point at our target directory
SCUMMVM_PREFS=""
if [ -f "$HOME/Library/Preferences/ScummVM Preferences" ]; then
    SCUMMVM_PREFS="$HOME/Library/Preferences/ScummVM Preferences"
elif [ -f "$HOME/.config/scummvm/scummvm.ini" ]; then
    SCUMMVM_PREFS="$HOME/.config/scummvm/scummvm.ini"
fi
if [ "$IN_PLACE" = 1 ] && [ -n "$SCUMMVM_PREFS" ]; then
    # Update the path= line in the [ultima8] section
    ESCAPED_PATH=$(echo "$TARGET_DIR" | sed 's/[&/]/\\&/g')
    if grep -q '^\[ultima8\]' "$SCUMMVM_PREFS"; then
        python3 -c "
import re, sys
new_path = sys.argv[2]
with open(sys.argv[1], 'r') as f:
    text = f.read()
text = re.sub(
    r'(\[ultima8\][^\[]*?)(path=)[^\n]*',
    r'\g<1>\g<2>' + new_path,
    text, count=1, flags=re.DOTALL)
with open(sys.argv[1], 'w') as f:
    f.write(text)
" "$SCUMMVM_PREFS" "$TARGET_DIR"
        echo "4. Updated ScummVM config: path=$TARGET_DIR"
    fi
fi

echo ""
echo "=== Installation complete ==="
echo ""

# The installed FLX is always larger than the base game's 1,251,108 bytes now
# that stealth is retired (M15), so the patched engine is always required.
# The size comparison is kept only to catch the "you installed the base game
# FLX by mistake" case.
INSTALLED_SIZE=$(wc -c < "$TARGET_DIR/USECODE/EUSECODE.FLX" | tr -d ' ')
BASE_FLX_SIZE=1251108

if [ "$INSTALLED_SIZE" -eq "$BASE_FLX_SIZE" ]; then
    echo "WARNING: the installed EUSECODE.FLX is exactly the base game's size"
    echo "  ($INSTALLED_SIZE bytes) — the Lost Vale build did not get installed."
    echo ""
elif [ ! -x "$SCRIPT_DIR/scummvm-lv/scummvm" ]; then
    echo "NOTE: Lost Vale EUSECODE.FLX installed ($INSTALLED_SIZE bytes)."
    echo "  Only the patched ScummVM can detect it. Build it:"
    echo "    ./build_scummvm.sh"
    echo ""
else
    # The detection entry is keyed on md5-5000 + file size, so a rebuilt FLX
    # whose first 5000 bytes changed needs the engine relinked (documented
    # trap: "Game data not found" after a full rebuild).
    DETECTION_FILE="$SCRIPT_DIR/scummvm-lv/engines/ultima/detection_tables.h"
    if [ -f "$DETECTION_FILE" ]; then
        INSTALLED_MD5=$(python3 -c "
import hashlib, sys
data = open(sys.argv[1], 'rb').read()
print(hashlib.md5(data[:5000]).hexdigest())
" "$TARGET_DIR/USECODE/EUSECODE.FLX")
        if ! grep -q "$INSTALLED_MD5" "$DETECTION_FILE" 2>/dev/null; then
            echo "WARNING: Installed EUSECODE.FLX hash ($INSTALLED_MD5) not in ScummVM detection table."
            echo "  ScummVM won't recognize this build. Rebuild ScummVM:"
            echo "    ./build_scummvm.sh"
            echo ""
        fi
    fi
fi

# ── Verify ────────────────────────────────────────────────────────────────

echo "Verification:"
echo "  EUSECODE.FLX: $(wc -c < "$TARGET_DIR/USECODE/EUSECODE.FLX") bytes"
echo "  FIXED.DAT:    $(wc -c < "$TARGET_DIR/STATIC/FIXED.DAT") bytes"
echo ""

TELEPORT_HELP="ScummVM debugger (Ctrl+Option+D on Mac, then type commands):

  First enable cheats:
    Cheat::toggle

  Then teleport:
    MainActor::teleport 8  20430 3250  0   — Map 8  (Bonecrusher cave — THE LV double doors)
    MainActor::teleport 9  14336 12544 0   — Map 9  (Galjeron's Chamber)
    MainActor::teleport 10 5120  7168  0   — Map 10 (Lost Vale — clan village, center)
    MainActor::teleport 10 19968 7424  0   — Map 10 (Lost Vale — Atli's village, center)
    MainActor::teleport 10 12800 2560  0   — Map 10 (Lost Vale — entry area)
    MainActor::teleport 11 9728  1536  0   — Map 11 (Elemental Dungeon)
    MainActor::teleport 13 4096  11776 0   — Map 13 (Cloud Cliffs base)
    MainActor::teleport 17 5376  11520 0   — Map 17 (Cloud City)
    MainActor::teleport 18 3072  1792  0   — Map 18 (Ancient Temple)

  Type 'exit' to return to the game."

# ── Launch ────────────────────────────────────────────────────────────────

if [ "$RUN" = 1 ]; then
    # The patched ScummVM is REQUIRED (M15) — see play.sh for the same note.
    # Stock ScummVM only ever worked with a --stealth build, and stealth is
    # retired (DD-006b), so a fallback would silently launch the wrong thing.
    SCUMMVM="${SCUMMVM:-}"
    if [ -z "$SCUMMVM" ]; then
        LV_SCUMMVM="$SCRIPT_DIR/scummvm-lv/scummvm"
        if [ -x "$LV_SCUMMVM" ]; then
            SCUMMVM="$LV_SCUMMVM"
            echo "Using patched ScummVM: $SCUMMVM"
        else
            echo "ERROR: patched ScummVM not found at $LV_SCUMMVM"
            echo "  Build it:  ./build_scummvm.sh"
            echo "  (Stock ScummVM cannot detect the Lost Vale build.)"
            exit 1
        fi
    fi

    if [ "$IN_PLACE" = 1 ]; then
        echo "Launching ScummVM (registered 'ultima8' target)..."
    else
        echo "Launching ScummVM on $TARGET_DIR ..."
    fi
    echo ""
    echo "$TELEPORT_HELP"
    echo ""

    # Point ScummVM at the engine data files (ultima.dat, ultima8.dat). A
    # fresh build tree keeps them in dists/engine-data/; without them the
    # engine dies in an "Error" dialog with nothing in the log
    # (tools/playtest-linux/session.sh has the same search).
    EXTRA=()
    SVM_DIR="$(dirname "$SCUMMVM")"
    for d in "$SVM_DIR/dists/engine-data" "$SVM_DIR"; do
        if [ -f "$d/ultima.dat" ] || [ -f "$d/ultima8.dat" ]; then
            EXTRA=(--extrapath="$d"); break
        fi
    done
    if [ "$IN_PLACE" = 1 ]; then
        "$SCUMMVM" --debuglevel=1 ${EXTRA[@]+"${EXTRA[@]}"} ultima8
    else
        # Its own config file and save folder: ScummVM housekeeping never
        # touches the player's scummvm.ini, and Lost Vale saves (which stock
        # Ultima 8 cannot load) never land beside, or over, the player's
        # ordinary Ultima 8 saves.
        mkdir -p "$TARGET_DIR/saves"
        "$SCUMMVM" --debuglevel=1 ${EXTRA[@]+"${EXTRA[@]}"} \
            --config="$TARGET_DIR/scummvm-lv.ini" --savepath="$TARGET_DIR/saves" \
            -p "$TARGET_DIR" ultima8
    fi
else
    echo "To launch: ./install_lv.sh --run"
    if [ "$IN_PLACE" = 1 ]; then
        echo "To restore originals: ./install_lv.sh --clean"
    fi
    echo ""
    echo "$TELEPORT_HELP"
fi
