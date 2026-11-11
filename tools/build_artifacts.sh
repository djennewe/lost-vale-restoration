#!/bin/bash
# tools/build_artifacts.sh — rebuild all six merged game-data artifacts from
# the player's own Ultima 8 install, then verify them against the canonical
# hashes. (Adversarial-review finding M22; PLAN 4.3.)
#
# The six outputs under shared/build/ are DERIVED FROM ORIGIN-COPYRIGHTED
# GAME DATA and are therefore NOT tracked in git:
#
#   TYPEFLAG.DAT    base TYPEFLAG.DAT + entries for LV shapes 856-886
#   U8SHAPES.FLX    base U8SHAPES.FLX + the injected LV shapes 856-886
#                   (wood-plank walls, the Tiny Tar potion, the gods, the
#                   art track's static props and Tyorvi's elixir, the Tiny
#                   Tar body, the Water Zombie, the Harpie, and the 1994
#                   screenshot art 874-886, with 870 a copy of 878 for old
#                   saves' halves). 861 and 862 are retired
#                   (lv_shapes.RETIRED_SHAPE_IDS): their slots stay base.
#   ANIM.DAT        base actor animation table + shape 867's own action
#                   table (the Tiny Tar body: shape 1's, stride scaled) and
#                   entries 872-873 and 888-890 (the Water Zombie, the
#                   Harpie, the 1994 elder and spear children: the ghoul's,
#                   the torax's, Mythran's and the child 708's tables)
#   EUSECODE.FLX    base usecode + the compiled Lost Vale classes
#   GLOB.FLX        retail slots 0-3071, LV prefabs from 3072
#   FIXED.DAT       base maps + the seven Lost Vale maps
#
# Each is a MERGE of our work with bytes we have no right to redistribute,
# which is why PLAN 4.3 ships an installer that rebuilds them locally rather
# than a bundle containing them. This script is that rebuild, and it is what
# a fresh clone runs before anything can be installed or tested.
#
# What IS tracked is shared/build/ARTIFACTS.sha256 — the canonical hash of
# each artifact. That keeps the reproducibility guarantee (one canonical
# md5+size per release, needed for the ScummVM detection entry) without
# committing a single Origin-derived byte.
#
# Build order matters: the map build's validator reads the PATCHED
# TYPEFLAG.DAT and U8SHAPES.FLX, so those two come first, and every custom-art
# injection has to land before the maps that place it.
#
# Usage:
#   tools/build_artifacts.sh              # build all six, verify against the manifest
#   tools/build_artifacts.sh --verify     # verify what is already on disk, build nothing
#   tools/build_artifacts.sh --record     # build, then REWRITE the manifest (see below)
#
# --record is for a DELIBERATE artifact change (new content, a fixed
# builder). It rewrites the canonical hashes, so the diff on
# ARTIFACTS.sha256 is the record of that decision — review it before
# committing. A verify failure without --record means either a builder
# changed behaviour unexpectedly, or your game data differs from the copy
# the canonical hashes were recorded against (a different GOG revision will
# legitimately produce different bytes; see the mismatch message).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$REPO_DIR/shared/build"
MANIFEST="$BUILD_DIR/ARTIFACTS.sha256"

ARTIFACTS=(TYPEFLAG.DAT U8SHAPES.FLX ANIM.DAT EUSECODE.FLX FIXED.DAT GLOB.FLX)

MODE="build"
case "${1:-}" in
    --verify)  MODE="verify" ;;
    --record)  MODE="record" ;;
    -h|--help) sed -n '2,44p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    "")        ;;
    *)         echo "unknown option: $1" >&2; exit 2 ;;
esac

cd "$REPO_DIR" || exit 2

sha_of() { shasum -a 256 "$1" | awk '{print $1}'; }

fail() { echo; echo "ERROR: $*" >&2; exit 1; }

# ── Build ────────────────────────────────────────────────────────────────
if [ "$MODE" != "verify" ]; then
    if [ ! -d "shared/data/u8-install" ]; then
        fail "shared/data/u8-install is missing. These artifacts are built
       FROM your own Ultima 8 install; see CLAUDE.md for what must be
       extracted there."
    fi
    mkdir -p "$BUILD_DIR"

    echo "════════════════════════════════════════════════════════════"
    echo "Rebuilding Lost Vale artifacts from shared/data/u8-install"
    echo "════════════════════════════════════════════════════════════"

    echo
    echo "-- 1/9  TYPEFLAG.DAT (LV shape slots 856-858) --"
    python3 agents/map-populator/src/patch_typeflag.py \
        || fail "patch_typeflag.py failed"

    echo
    echo "-- 2/9  U8SHAPES.FLX (wood-plank shape injection) --"
    python3 agents/map-populator/src/lv_wood_wall.py \
        || fail "lv_wood_wall.py failed"

    echo
    echo "-- 3/9  U8SHAPES.FLX + TYPEFLAG.DAT (Tiny Tar potion, DD-005) --"
    # Must run AFTER both 1 and 2: it injects shape 859 into the U8SHAPES
    # built in step 2 and patches the TYPEFLAG built in step 1. Without it
    # there is no frame-8 potion, nothing shrinks the Avatar, and the Map 18
    # crack seals the Inner Sanctum against every possible player.
    python3 agents/map-populator/src/lv_tiny_tar.py \
        || fail "lv_tiny_tar.py failed"

    echo
    echo "-- 4/9  U8SHAPES.FLX + TYPEFLAG.DAT (the three Zealan gods) --"
    # Shape 860, 42 frames: 0/1/2 the gods sealed in amber (the 1994
    # pixels of screen04), 3/4/5 the same three freed, 6-41 the shatter
    # runs. Same ordering rule as step 3 — it injects into the
    # U8SHAPES built in step 2 and patches the TYPEFLAG built in step 1.
    # Without it Map 18 stages the endgame with base-game statues.
    python3 agents/map-populator/src/lv_god_statues.py \
        || fail "lv_god_statues.py failed"

    echo
    echo "-- 5/9  U8SHAPES.FLX + TYPEFLAG.DAT (art-track static props) --"
    # The table-driven step every static prop on the art track shares
    # (docs/art-track.md): a row per prop in lv_art_props.PROPS, 863 the
    # Sacred Rock first. Same ordering rule as steps 3 and 4. Without it the
    # maps place shapes with no data and the props are invisible.
    python3 agents/map-populator/src/lv_art_props.py \
        || fail "lv_art_props.py failed"

    echo
    echo "-- 6/9  U8SHAPES.FLX + TYPEFLAG.DAT + ANIM.DAT (actors: Tiny Tar body 867, Water Zombie 872, Harpie 873, 1994 elder 888, spear children 889-890) --"
    # The actor shapes, each in all three files the engine reads for an
    # actor (the sprite, the TYPEFLAG row, the ANIM.DAT entry, without
    # which AnimationTracker will not move it). Same ordering rule as
    # steps 3-5. First the shape drinking Tiny Tar turns the Avatar into:
    # the Avatar's own frames scaled down with a shrink ramp at 60-69
    # (derived from the pristine shape 1 here, docs/art-track.md contract
    # 8); the TYPEFLAG row, 708's with shape 1's weight and volume, so the
    # pack reads the same shrunk as grown; and its own ANIM.DAT action
    # table, shape 1's. lv_tiny_avatar.py writes ANIM.DAT from the pristine
    # base, so it runs first. Without it makeAvatarTiny() turns the Avatar
    # into an empty slot with no animation, and the Map 18 crack is
    # unreachable. Then the expansion's own actors (lv_monsters.py,
    # contract 9): the Water Zombie 872 (the ghoul's frames recoloured to
    # the 1994 zombie), the Harpie 873 (drawn new in the torax's layout)
    # and the 1994 NPC bodies 888-890 (lv_actor_art.py: Mythran's and the
    # child 708's frames restyled, the shot poses in), each with its
    # donor's TYPEFLAG row and ANIM.DAT entry. The Lake's and the harpie
    # zone's eggs hatch the monsters and Map 10 places the NPC bodies, and
    # FIXED's validator checks the shape is an actor, so they land before
    # step 8.
    python3 agents/map-populator/src/lv_tiny_avatar.py \
        || fail "lv_tiny_avatar.py failed"
    python3 agents/map-populator/src/lv_monsters.py \
        || fail "lv_monsters.py failed"

    echo
    echo "-- 7/9  EUSECODE.FLX (compile all LV usecode) --"
    python3 agents/usecode-compiler/src/build_eusecode.py --full \
        || fail "build_eusecode.py --full failed"

    echo
    echo "-- 8/9  GLOB.FLX (retail slots and appended LV prefabs) --"
    python3 agents/map-populator/src/lv_globs.py \
        || fail "lv_globs.py failed"

    echo
    echo "-- 9/9  FIXED.DAT (assemble all LV maps) --"
    # Previews are QA output, not an artifact; render them separately with
    # build_all_maps.py when you want them.
    python3 agents/map-populator/src/build_all_maps.py --no-previews \
        || fail "build_all_maps.py failed"
fi

# ── Record ───────────────────────────────────────────────────────────────
if [ "$MODE" = "record" ]; then
    {
        echo "# shared/build/ARTIFACTS.sha256 — canonical hashes of the six merged"
        echo "# game-data artifacts. The artifacts themselves are NOT tracked (M22):"
        echo "# they contain Origin-copyrighted bytes. Rebuild them from your own"
        echo "# game data with tools/build_artifacts.sh, which verifies against this"
        echo "# file. Regenerate it with --record only for a DELIBERATE artifact"
        echo "# change; the diff here is the record of that decision."
        echo "#"
        echo "# Checkable with the standard tool, from shared/build/:"
        echo "#     shasum -a 256 -c ARTIFACTS.sha256"
        echo "#"
        for a in "${ARTIFACTS[@]}"; do
            [ -f "$BUILD_DIR/$a" ] || fail "$a was not built; cannot record it"
            printf '# %-14s %10s bytes\n' "$a" \
                "$(wc -c < "$BUILD_DIR/$a" | tr -d ' ')"
        done
        echo "#"
        for a in "${ARTIFACTS[@]}"; do
            echo "$(sha_of "$BUILD_DIR/$a")  $a"
        done
    } > "$MANIFEST"
    echo
    echo "Recorded canonical hashes in $MANIFEST:"
    grep -v '^#' "$MANIFEST" | sed 's/^/  /'
    exit 0
fi

# ── Verify ───────────────────────────────────────────────────────────────
echo
echo "════════════════════════════════════════════════════════════"
echo "Verifying against $MANIFEST"
echo "════════════════════════════════════════════════════════════"

[ -f "$MANIFEST" ] || fail "$MANIFEST is missing — run with --record to create it"

BAD=0
MISSING=0
for a in "${ARTIFACTS[@]}"; do
    want="$(grep -E "  $a\$" "$MANIFEST" | awk '{print $1}')"
    if [ -z "$want" ]; then
        printf '  %-14s NO CANONICAL HASH RECORDED\n' "$a"
        BAD=$((BAD + 1))
        continue
    fi
    if [ ! -f "$BUILD_DIR/$a" ]; then
        printf '  %-14s MISSING — run tools/build_artifacts.sh\n' "$a"
        MISSING=$((MISSING + 1))
        continue
    fi
    got="$(sha_of "$BUILD_DIR/$a")"
    if [ "$got" = "$want" ]; then
        printf '  %-14s OK    %s\n' "$a" "$got"
    else
        printf '  %-14s DIFFERS\n' "$a"
        printf '    canonical %s\n' "$want"
        printf '    built     %s\n' "$got"
        BAD=$((BAD + 1))
    fi
done

echo
if [ "$MISSING" -gt 0 ] || [ "$BAD" -gt 0 ]; then
    echo "════════════════════════════════════════════════════════════"
    echo "RESULT: FAIL — $BAD differing, $MISSING missing"
    echo "════════════════════════════════════════════════════════════"
    if [ "$BAD" -gt 0 ]; then
        echo
        echo "A differing artifact means one of:"
        echo "  - a builder changed behaviour (investigate; this is the case"
        echo "    the check exists for),"
        echo "  - the change was intended, in which case rerun with --record"
        echo "    and commit the ARTIFACTS.sha256 diff as the decision record,"
        echo "  - or your Ultima 8 install differs from the copy these hashes"
        echo "    were recorded against. A different GOG/CD revision will"
        echo "    legitimately produce different merged bytes; that is not a"
        echo "    defect, but it does mean your build is not THE canonical one"
        echo "    and its md5 will not match the ScummVM detection entry."
    fi
    exit 1
fi

echo "════════════════════════════════════════════════════════════"
echo "RESULT: PASS — all ${#ARTIFACTS[@]} artifacts match the canonical hashes"
echo "════════════════════════════════════════════════════════════"
exit 0
