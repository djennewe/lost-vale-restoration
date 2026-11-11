#!/usr/bin/env python3
"""
lv_art_props.py — inject the art track's STATIC PROPS as custom shapes.

WHY THIS EXISTS
---------------
The art track (docs/art-track.md, from the map cleanup plan's section 5)
replaces base-game placeholders with custom shapes one at a time, each
landing whenever its art is ready. A shape injected by hand into
shared/build/U8SHAPES.FLX survives exactly until the next artifact rebuild
(.claude/rules/shape-ids.md), so every custom shape needs a build step. The
gods have their own (lv_god_statues.py — 42 frames and a TYPEFLAG anim entry
that dispatches usecode). Static props do not need any of that: one shape,
one TYPEFLAG entry copied from a donor with the right flags, a footpad sized
to the art. So they share this ONE table-driven step, and a new prop is a row
in PROPS plus its art, and the build's step count does not grow per prop.

THE TABLE IS THE CONTRACT
-------------------------
Each row is the engine-side half of that prop's written contract in
docs/art-track.md: shape id (from lv_shapes, the map side's table of truth),
donor, footpad, and the frame recipe (file, game-scale height, chroma key,
key tolerance, despill margin — the same tuple lv_god_statues.py uses, fed
to png2shape.build_frame). The map builder that places the prop imports its
FOOTPAD from here so the box it centres on a tile is the box the engine
collides with.

WHAT IS IN IT
-------------
RETIRED (2026-10-17): 861 the Magnetic Obelisk and 862 the cloud floor tile
were rows here until the 1994 screenshot art replaced them (screen11's
retail obelisk composite and 874). lv_shapes.RETIRED_SHAPE_IDS lists them;
their slots stay the base game's and are never reused. 870, the Shield
halves cut from retail 828, was replaced by 878 the same day but is NOT
retired: it is 878's legacy alias, a copy row below.

863  the Sacred Rock (Map 10's Sacred Circle). The one prop on the track
     with NO 1994 original: "Sacred Smallish Unusual-Colored Rock" was a
     joke placeholder in Plot v1.1/v1.2 that became "Sacred Circle" before
     the usecode snapshot. The look was decided instead (Douglas,
     2026-09-20): a NINTH STONE, kin to the eight shape-38 monoliths on
     the ring, so the generator's reference is the ring itself. Candidate
     C2 of six: a dressed tapering shaft with shallow weathering bands and
     a rough broken crown, one continuous piece of stone. The v1 trio read
     as stacked masonry with a black keyline; the keyline and the neutral
     grey both disappeared in the U8PAL quantize, so the v2 pass was about
     the silhouette. Donor 66, the shape it replaces.
     tools/art/gen_sacred_rock.sh, shared/docs/art-poc/sacred-rock/.

864  the Message Scroll (Map 17's Scroll Chamber). A document, and the
     third item on the track with no 1994 art to redraw, so the reference
     is the GAME'S OWN SCROLL: base shape 159 frames 0 and 3, rendered
     clean at shared/docs/art-poc/message-scroll/reference-base-scroll.png.
     Donor 159 too, which is the whole engine-side point: no SI_FIXED, so
     the Avatar can carry it to Ezrekal as Plot v1.2 beat 14 asks, and
     SF_QUALITY, so quality 80 is readable by any class that asks
     (Item::I_getQuality answers for that family alone, item.cpp:2841).
     Candidate A2 of five: the v1 trio all read as a BLANK sheet at 22 px
     because the ink survived the downscale as three grey pixels, so v2
     pinned the ink as its own clause. tools/art/gen_message_scroll.sh,
     shared/docs/art-poc/message-scroll/.

865  the elemental pillars (Map 11's Four Pillars chamber), FOUR FRAMES in
     the map's element order, the track's first multi-frame row. Frame 2
     is the 1994 Pillar of Fire cut from screen07 (registry 2023, phase D,
     2026-10-25). Frames 0, 1 and 3 (Earth, Air, Water) are its column
     redrawn for each element (registry 2024-2026, 2026-10-30, Douglas's
     card 4): the same banded dark column on 2023's canvas and hotspot,
     the red gem, the flames and the lava recoloured by luminance onto an
     element ramp (earth ochre-brown, air pale grey, water blue), the
     lower-left of the shaft the shot hides drawn from the rows above.
     tools/art/pillar_1994_style.py. They replaced the AI-drawn columns of
     2026-09-24 (sheets C2/C3, tools/art/gen_pillars.sh, still under
     shared/docs/art-poc/pillars/). Donor 38, the ring stone
     (SI_FIXED|SI_SOLID, not 721's SI_NOISY); footpad (2,2,10), a 64x64
     box 80 units tall, which the flames and foot pools overhang on
     purpose. That height is over the chamber's old "nothing tops 40"
     invariant on purpose: distance is what protects the anti-climb wall
     there (build_map_11.py, test_route_reach).

866  the pillar receptacles, one frame: a squat stone socket at knee height
     with a hollow for a gem, approved as generated. Donor 443 `statue`
     with its own (3,3,3). The shape number carries no usecode meaning:
     the receptacles dispatch every event to class 1144 off npcnum 120
     through the engine patch, whatever their shape.

868  Tyorvi's elixir (never placed: EZREKAL.UNK creates it, TYORVI.UNK's
     drink destroys it). The first RECOLOUR row: no PNG, the frame is the
     base game's necromancy vial, shape 395 frame 5, with only its red
     liquid (palette 41-46) walked onto the sea-green ramp 85-92, so the
     glass, the cork and the outline are the vial's own and no Origin
     pixel is committed (lv_tiny_tar.py's approach for 859). No frame of
     the potion 766 or of 395 uses any index of that ramp (84-95).
     Donor 180, the engine's bottle: SF_GENERIC with 395's own footprint
     and weight, so the elixir is carryable but NOT SF_REAGENT and never
     merges with a stack of blood. Class 868 (lv-new/ELIXIR.UNK) barks its
     name.
     tools/art/elixir_plate.py renders the plate.

869  the special root (Map 10, by the Sacred Circle's east stone; contract
     12). A pale gnarled root with a small tuft of violet leaves, the one
     colour Ezrekal remembers ("maybe purple", EZREKAL.UNK:3142): candidate
     C of three, Douglas's pick (2026-10-11), tools/art/gen_special_root.sh.
     Donor 180, the elixir's: 399's row without SI_NOISY and SI_TRANSL, so
     carryable, SF_GENERIC, drawn opaque. Footpad (2,2,1), a 32x24 box for
     a root lying on the ground. Despill 0: the hue despill eats violet.
     Class 869 (lv-new/SPROOT.UNK) barks "special root"; TypeWeedz resolves
     here at frame 0. shared/docs/art-poc/special-root/.

871  the Passage Test plant (Map 10 test grounds, q10; contract 13). A squat
     yellow-green bulb ringed with dark-tipped spines and a red fruit at its
     heart, Plot v1.2 beat 8's "nasty plant with delectable fruit at its
     heart": candidate A of three, Douglas's pick (2026-10-11),
     tools/art/gen_test_plant.sh. Sized by width (48 px, the box) and
     despill 0, which keeps the purple-black spine tips. Donor 65, the
     mushroom cluster: SI_FIXED|SI_SOLID, no SI_LAND, so it is walked round,
     not over. Footpad (3,3,4): the five plants PLNTST pops stand 96-128
     units apart, so 3x3 boxes only touch. Class 871 (lv-new/TESTPLNT.UNK)
     barks the 1994 "Strange plant". shared/docs/art-poc/test-plant/.

874-879  THE 1994 ART (2026-10-16): the pieces of the published 1994
     screenshots that are not retail art, cut pixel-exact
     (shared/data/lv-1994-art/, vignettes/art_registry.json), so the build
     can redraw those shots. The first INDEXED rows: no key, trim, rescale
     or quantize, the PNG's U8PAL indices go into the frame verbatim
     (png2shape.indexed_pixels) at the registry hotspot. 874 the cloud
     floor (5 frames; it replaced the retired custom tile 862), 875 the
     white column (plain, banded), 876 the gold brick floor (2), 877 the
     marble walkway slab, 878 the Shield halves (sun, eye; they replaced
     the retired 828 split 870), 879 the reassembled
     Shield on the altar. Floor rows draw one pixel higher than the
     registry hotspot (FLOOR_Z0_SHIFT): the engine's floor is z=0, the
     reconstruction drew it at z=1. Phase C's report has the proof:
     docs/research/2026-10-16-screenshot-reconstruction/phaseC-art.md.

880  the gem pillar's cap (Map 17, screen11; 2026-10-17). The first COPY
     row: no PNG, the frames are retail 596's eight, copied verbatim at
     build time (so no Origin pixel is committed), on donor 443 `statue`
     (SI_FIXED|SI_SOLID) with 596's own (1,1,1) footpad. The 1994 shot puts
     the retail gem on its pillars, but 596 is TypeTalisman, carryable, and
     frames 0-3 are Map 11's element talismans: one taken off a pillar would
     open a receptacle. 880 looks the same and cannot be picked up.

870  the Shield halves' LEGACY ALIAS (2026-10-17). A save made 2026-10-11
     ..10-17 can carry the halves as 870 in the Avatar's pack, and with
     870's slot empty, opening the pack aborts ScummVM (ContainerGump::run
     asserts every contained item has a shape; verify3 claim 2). So the
     row copies 878's two frames, built by the row above it in this run,
     and its TYPEFLAG donor is 878 itself with 878's footpad, so the row
     is 878's byte for byte: an old half looks and behaves as the 1994
     half. Never placed; SHADES and REAPPLY accept it by literal.

881  the striped prop on Felicitar's plinth (Map 18, screen04; 2026-10-17).
     An indexed row, registry 2014: SINGLE-SHOT and unidentified (bones or
     a ribcage; no retail frame matches). In the shot it hides the right
     foot of the 1994 Felicitar (860 frame 0), whose 42 pixels there are
     inferred. Donor 443 (fixed), the reconstruction's 32x32x8 box.

Like the other injection steps this writes into the U8SHAPES.FLX built by
the steps before it and patches the TYPEFLAG.DAT built in step 1; it must
run after both (tools/build_artifacts.sh keeps the order).

Usage:
    python3 lv_art_props.py [--out PATH] [--src PATH] [--preview]
"""

import argparse
import json
import os
import sys
from types import SimpleNamespace
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.join(HERE, '..', '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'tools'))

from shape_viewer import (load_palette, read_flx_entry,         # noqa: E402
                          parse_shape_frames, PALETTE_FILE, SHAPES_FLX)
from lv_wood_wall import (encode_frame, encode_shape_blobs,      # noqa: E402
                          inject_shape, validate_shape)
from png2shape import (build_frame, suggest_footpad,              # noqa: E402
                       footpad_screen_size, indexed_pixels, Refused,
                       KEYCOLOR)
from lv_shapes import (SHAPE_SACRED_ROCK, SHAPE_MESSAGE_SCROLL,  # noqa: E402
                       SHAPE_ELEMENTAL_PILLAR, SHAPE_PILLAR_RECEPTACLE,
                       SHAPE_ELIXIR, SHAPE_SPECIAL_ROOT,
                       SHAPE_TEST_PLANT, SHAPE_CLOUD_1994,
                       SHAPE_WHITE_COLUMN_1994, SHAPE_GOLD_BRICK_1994,
                       SHAPE_MARBLE_WALKWAY_1994, SHAPE_SHIELD_HALVES_1994,
                       SHAPE_SACRED_SHIELD_1994, SHAPE_GEM_CAP_1994,
                       SHAPE_STRIPED_PROP_1994, SHAPE_SHIELD_HALVES_LEGACY,
                       SHAPE_NOOK_DAIS_1994, SHAPE_WALKWAY_END_1994,
                       SHAPE_GOLD_EDGE_1994, SHAPE_SIDE_THRONE_1994,
                       SHAPE_CLOUD_RIM_1994, SHAPE_CAVE_FACE_1994,
                       SHAPE_CAVE_FLOOR_1994, SHAPE_CAVE_BACKDROP_SMALL,
                       SHAPE_CAVE_BACKDROP_LARGE, SHAPE_DECORATIVE_WATER,
                       SHAPE_SANCTUM_BACKDROP, SHAPE_COURT_COBBLE_FLAT,
                       SHAPE_RUBBLE_DECORATIVE, SHAPE_BONES_DECORATIVE_A,
                       SHAPE_BONES_DECORATIVE_B, SHAPE_CAVE_CREST_DECORATIVE,
                       SHAPE_MOAT_BANK_DECORATIVE, SHAPE_MOAT_FACE_DECORATIVE)

SHARED = os.path.join(ROOT, 'shared')
OUT_SHAPES = os.path.join(SHARED, 'build', 'U8SHAPES.FLX')
ART = os.path.join(SHARED, 'docs', 'art-poc')
REGISTRY = os.path.join(HERE, 'vignettes', 'art_registry.json')

# The 1994 floor tiles were reconstructed at z=1 with objects at z=2: the
# pixel parity of the shots forbids both on one z with retail hotspots. The
# engine wants floors at z=0 with objects standing on them at z=0, so the
# floor rows take the registry hotspot with yoff + 1, which draws a z=0 tile
# on the pixels the z=1 tile covered; objects drop to z-2 at the nearest
# (x, y) that projects to the same pixel, which is (x-1, y-1) for their 32k
# positions and puts them on the retail 31 residue (phaseC-art.md, "Cloud
# z-encoding").
FLOOR_Z0_SHIFT = (0, 1)

# Registry grades that are not sprites: never fed to a builder
# (screenshot-reconstruction.md section 6, blocker 1).
NOT_A_SPRITE = ('reference-only', 'residual')

MAGENTA = (255, 0, 255)

# The elixir's liquid: the blood vial's six-step red ramp, tone for tone onto
# the palette's sea-green ramp (84-95). The two darkest tones step two
# indices each so the bottom of the vial still reads against its black
# outline.
ELIXIR_REMAP = {
    41: 85,    # (154,4,4) -> (97,178,166)   meniscus highlight
    42: 86,    # (134,4,4) -> (77,166,150)
    43: 87,    # (113,0,0) -> (65,150,130)
    44: 88,    # (97,0,0)  -> (48,134,113)   body
    45: 90,    # (77,0,0)  -> (24,105,81)
    46: 92,    # (56,0,0)  -> (8,77,52)      bottom shadow
}

# One row per static prop. `frames` is a list of
#   (path under shared/docs/art-poc, game-scale height px or None, key rgb,
#    key tolerance, despill margin)
# in frame order. Tolerance 130 / despill 16 is the recipe the freed gods
# settled on for flat-magenta agy output: 60 leaves a pink fringe on the
# anti-aliased edge, and the despill strips the purple ring that only shows
# over a lit floor (lv_god_statues.py has the full story).
#
# Optional key:
#   'width'    game-scale width in px. With a height as well the resize is
#              NON-UNIFORM, which is how a generator's square top-down
#              drawing becomes an object lying on a 2:1 floor tile (the
#              Message Scroll: 1024x1024 -> 30x22).
# A height of None means no rescale. The god runs use the same options
# through lv_god_statues.frame_args.
#
# A row may take 'recolour': (shape, frame, remap) INSTEAD of 'frames': its
# one frame is that base-game frame, geometry and anchor kept, with every
# pixel in `remap` re-indexed. The build fails if the source frame carries
# none of the remap's keys (the base art moved), as lv_tiny_tar.py does.
#
# A row may take 'indexed': [(registry id, frame[, (xoff, yoff)]), ...]
# INSTEAD of 'frames': 1994 art from vignettes/art_registry.json, each frame
# that registry frame's P-mode PNG with its indices copied verbatim, anchored
# at the registry hotspot plus the row's 'hotspot_shift' (dx, dy), or at the
# entry's own (xoff, yoff) when the registry has none. 'oversize' (a reason)
# lets art stand taller than its footpad's screen box on purpose; check_fit
# then prints the overhang instead of refusing.
#
# A row may take 'patch': registry id INSTEAD of 'frames': one frame per
# frame of that registry entry, each its `base` (retail shape, frame) read
# from the base FLX with the registry PNG's opaque pixels laid over it,
# PNG hotspot on the base frame's anchor; the canvas grows to hold both.
# The PNG holds only the 1994 shot's pixels, so no Origin pixel is
# committed (patch_frame).
# Binary opacity masks contain no retail texture. Each clipped frame uses
# retail 564 frame 0 or black frame 2 beneath each mask, retaining its
# size and hotspot. Editor plates preserve the original support boxes.
CAVE_BACKDROP_CLIPS = ({'at': [2047, 15103],
  'frame': 0,
  'mask': 'vq2-clips/m11-2047-15103.png',
  'map': 11,
  'support_shape': 763},
 {'at': [2303, 14847],
  'frame': 0,
  'mask': 'vq2-clips/m11-2303-14847.png',
  'map': 11,
  'support_shape': 499},
 {'at': [2303, 15103],
  'frame': 0,
  'mask': 'vq2-clips/m11-2303-15103.png',
  'map': 11,
  'support_shape': 499},
 {'at': [2303, 15359],
  'frame': 0,
  'mask': 'vq2-clips/m11-2303-15359.png',
  'map': 11,
  'support_shape': 499},
 {'at': [2431, 14591],
  'frame': 0,
  'mask': 'vq2-clips/m11-2431-14591.png',
  'map': 11,
  'support_shape': 763},
 {'at': [2559, 15615],
  'frame': 0,
  'mask': 'vq2-clips/m11-2559-15615.png',
  'map': 11,
  'support_shape': 499},
 {'at': [2815, 14335],
  'frame': 0,
  'mask': 'vq2-clips/m11-2815-14335.png',
  'map': 11,
  'support_shape': 499},
 {'at': [2815, 14591],
  'frame': 0,
  'mask': 'vq2-clips/m11-2815-14591.png',
  'map': 11,
  'support_shape': 499},
 {'at': [2815, 15615],
  'frame': 0,
  'mask': 'vq2-clips/m11-2815-15615.png',
  'map': 11,
  'support_shape': 499},
 {'at': [2815, 15871],
  'frame': 0,
  'mask': 'vq2-clips/m11-2815-15871.png',
  'map': 11,
  'support_shape': 499},
 {'at': [3071, 14591],
  'frame': 0,
  'mask': 'vq2-clips/m11-3071-14591.png',
  'map': 11,
  'support_shape': 499},
 {'at': [2943, 14719],
  'frame': 0,
  'mask': 'vq2-clips/m11-2943-14719.png',
  'map': 11,
  'support_shape': 763},
 {'at': [3071, 14719],
  'frame': 0,
  'mask': 'vq2-clips/m11-3071-14719.png',
  'map': 11,
  'support_shape': 763},
 {'at': [3071, 14847],
  'frame': 0,
  'mask': 'vq2-clips/m11-3071-14847.png',
  'map': 11,
  'support_shape': 763},
 {'at': [3071, 15615],
  'frame': 0,
  'mask': 'vq2-clips/m11-3071-15615.png',
  'map': 11,
  'support_shape': 499},
 {'at': [2943, 15743],
  'frame': 0,
  'mask': 'vq2-clips/m11-2943-15743.png',
  'map': 11,
  'support_shape': 763},
 {'at': [3327, 14847],
  'frame': 0,
  'mask': 'vq2-clips/m11-3327-14847.png',
  'map': 11,
  'support_shape': 499},
 {'at': [3199, 14975],
  'frame': 0,
  'mask': 'vq2-clips/m11-3199-14975.png',
  'map': 11,
  'support_shape': 763},
 {'at': [3199, 15359],
  'frame': 0,
  'mask': 'vq2-clips/m11-3199-15359.png',
  'map': 11,
  'support_shape': 763},
 {'at': [6271, 21759],
  'frame': 0,
  'mask': 'vq2-clips/m11-6271-21759.png',
  'map': 11,
  'support_shape': 763},
 {'at': [6271, 21887],
  'frame': 0,
  'mask': 'vq2-clips/m11-6271-21887.png',
  'map': 11,
  'support_shape': 763},
 {'at': [6655, 19583],
  'frame': 0,
  'mask': 'vq2-clips/m11-6655-19583.png',
  'map': 11,
  'support_shape': 763},
 {'at': [6655, 21119],
  'frame': 0,
  'mask': 'vq2-clips/m11-6655-21119.png',
  'map': 11,
  'support_shape': 763},
 {'at': [6911, 20351],
  'frame': 0,
  'mask': 'vq2-clips/m11-6911-20351.png',
  'map': 11,
  'support_shape': 763},
 {'at': [6911, 20991],
  'frame': 0,
  'mask': 'vq2-clips/m11-6911-20991.png',
  'map': 11,
  'support_shape': 499},
 {'at': [6911, 21119],
  'frame': 0,
  'mask': 'vq2-clips/m11-6911-21119.png',
  'map': 11,
  'support_shape': 763},
 {'at': [7167, 20735],
  'frame': 0,
  'mask': 'vq2-clips/m11-7167-20735.png',
  'map': 11,
  'support_shape': 499},
 {'at': [7039, 20863],
  'frame': 0,
  'mask': 'vq2-clips/m11-7039-20863.png',
  'map': 11,
  'support_shape': 763},
 {'at': [7039, 20991],
  'frame': 0,
  'mask': 'vq2-clips/m11-7039-20991.png',
  'map': 11,
  'support_shape': 763},
 {'at': [7295, 20735],
  'frame': 0,
  'mask': 'vq2-clips/m11-7295-20735.png',
  'map': 11,
  'support_shape': 763},
 {'at': [7423, 20607],
  'frame': 0,
  'mask': 'vq2-clips/m11-7423-20607.png',
  'map': 11,
  'support_shape': 763},
 {'at': [7423, 20735],
  'frame': 0,
  'mask': 'vq2-clips/m11-7423-20735.png',
  'map': 11,
  'support_shape': 763},
 {'at': [7551, 20735],
  'frame': 0,
  'mask': 'vq2-clips/m11-7551-20735.png',
  'map': 11,
  'support_shape': 763},
 {'at': [7551, 20863],
  'frame': 0,
  'mask': 'vq2-clips/m11-7551-20863.png',
  'map': 11,
  'support_shape': 763},
 {'at': [7679, 20991],
  'frame': 0,
  'mask': 'vq2-clips/m11-7679-20991.png',
  'map': 11,
  'support_shape': 763},
 {'at': [7807, 20991],
  'frame': 0,
  'mask': 'vq2-clips/m11-7807-20991.png',
  'map': 11,
  'support_shape': 763},
 {'at': [7807, 21119],
  'frame': 0,
  'mask': 'vq2-clips/m11-7807-21119.png',
  'map': 11,
  'support_shape': 763},
 {'at': [7935, 21119],
  'frame': 0,
  'mask': 'vq2-clips/m11-7935-21119.png',
  'map': 11,
  'support_shape': 763},
 {'at': [7935, 21503],
  'frame': 0,
  'mask': 'vq2-clips/m11-7935-21503.png',
  'map': 11,
  'support_shape': 763},
 {'at': [8191, 21247],
  'frame': 0,
  'mask': 'vq2-clips/m11-8191-21247.png',
  'map': 11,
  'support_shape': 763},
 {'at': [9727, 20607],
  'frame': 0,
  'mask': 'vq2-clips/m11-9727-20607.png',
  'map': 11,
  'support_shape': 763},
 {'at': [9855, 20607],
  'frame': 0,
  'mask': 'vq2-clips/m11-9855-20607.png',
  'map': 11,
  'support_shape': 763},
 {'at': [9855, 20735],
  'frame': 0,
  'mask': 'vq2-clips/m11-9855-20735.png',
  'map': 11,
  'support_shape': 763},
 {'at': [9855, 22271],
  'frame': 0,
  'mask': 'vq2-clips/m11-9855-22271.png',
  'map': 11,
  'support_shape': 763},
 {'at': [9983, 22271],
  'frame': 0,
  'mask': 'vq2-clips/m11-9983-22271.png',
  'map': 11,
  'support_shape': 763},
 {'at': [10111, 22271],
  'frame': 0,
  'mask': 'vq2-clips/m11-10111-22271.png',
  'map': 11,
  'support_shape': 763},
 {'at': [6879, 21119],
  'frame': 0,
  'mask': 'vq2-clips/m11-6879-21119.png',
  'map': 11,
  'support_shape': 763},
 {'at': [2623, 7359], 'frame': 0, 'mask': 'vq2-clips/m18-2623-7359.png', 'map': 18},
 {'at': [2719, 7327], 'frame': 0, 'mask': 'vq2-clips/m18-2719-7327.png', 'map': 18},
 {'at': [2783, 7263], 'frame': 0, 'mask': 'vq2-clips/m18-2783-7263.png', 'map': 18},
 {'at': [2047, 15103],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-2047-15103.png',
  'map': 11,
  'kind': 'window'},
 {'at': [2303, 14847],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-2303-14847.png',
  'map': 11,
  'kind': 'window'},
 {'at': [2303, 15103],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-2303-15103.png',
  'map': 11,
  'kind': 'window'},
 {'at': [2303, 15359],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-2303-15359.png',
  'map': 11,
  'kind': 'window'},
 {'at': [2431, 14591],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-2431-14591.png',
  'map': 11,
  'kind': 'window'},
 {'at': [2559, 15615],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-2559-15615.png',
  'map': 11,
  'kind': 'window'},
 {'at': [2815, 14335],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-2815-14335.png',
  'map': 11,
  'kind': 'window'},
 {'at': [2815, 14591],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-2815-14591.png',
  'map': 11,
  'kind': 'window'},
 {'at': [2815, 15615],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-2815-15615.png',
  'map': 11,
  'kind': 'window'},
 {'at': [2815, 15871],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-2815-15871.png',
  'map': 11,
  'kind': 'window'},
 {'at': [3071, 14591],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-3071-14591.png',
  'map': 11,
  'kind': 'window'},
 {'at': [2943, 14719],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-2943-14719.png',
  'map': 11,
  'kind': 'window'},
 {'at': [3071, 14719],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-3071-14719.png',
  'map': 11,
  'kind': 'window'},
 {'at': [3071, 14847],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-3071-14847.png',
  'map': 11,
  'kind': 'window'},
 {'at': [3071, 15615],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-3071-15615.png',
  'map': 11,
  'kind': 'window'},
 {'at': [3327, 14847],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-3327-14847.png',
  'map': 11,
  'kind': 'window'},
 {'at': [3199, 14975],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-3199-14975.png',
  'map': 11,
  'kind': 'window'},
 {'at': [3199, 15359],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-3199-15359.png',
  'map': 11,
  'kind': 'window'},
 {'at': [6911, 20991],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-6911-20991.png',
  'map': 11,
  'kind': 'window'},
 {'at': [6911, 21119],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-6911-21119.png',
  'map': 11,
  'kind': 'window'},
 {'at': [7167, 20735],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-7167-20735.png',
  'map': 11,
  'kind': 'window'},
 {'at': [7039, 20863],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-7039-20863.png',
  'map': 11,
  'kind': 'window'},
 {'at': [7039, 20991],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-7039-20991.png',
  'map': 11,
  'kind': 'window'},
 {'at': [7295, 20735],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-7295-20735.png',
  'map': 11,
  'kind': 'window'},
 {'at': [7423, 20607],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-7423-20607.png',
  'map': 11,
  'kind': 'window'},
 {'at': [7423, 20735],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-7423-20735.png',
  'map': 11,
  'kind': 'window'},
 {'at': [7551, 20735],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-7551-20735.png',
  'map': 11,
  'kind': 'window'},
 {'at': [7551, 20863],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-7551-20863.png',
  'map': 11,
  'kind': 'window'},
 {'at': [7679, 20991],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-7679-20991.png',
  'map': 11,
  'kind': 'window'},
 {'at': [7807, 20991],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-7807-20991.png',
  'map': 11,
  'kind': 'window'},
 {'at': [7807, 21119],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-7807-21119.png',
  'map': 11,
  'kind': 'window'},
 {'at': [7935, 21119],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-7935-21119.png',
  'map': 11,
  'kind': 'window'},
 {'at': [7935, 21503],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-7935-21503.png',
  'map': 11,
  'kind': 'window'},
 {'at': [6879, 21119],
  'frame': 2,
  'mask': 'vq2-clips/m11-window-6879-21119.png',
  'map': 11,
  'kind': 'window'})

PROPS = [
    {
        # Map 8's hidden ceilings still need opaque background paint in
        # low-resolution play. Donor 202 is FIXED|DRAW with no support,
        # collision, roof, or occlusion flags. Keep retail frame geometry.
        'shape': SHAPE_CAVE_BACKDROP_SMALL,
        'name': 'Cave backdrop (small)',
        'donor': 202,
        'footpad': (4, 4, 0),
        'copy': (334, 29),
    },
    {
        'shape': SHAPE_CAVE_BACKDROP_LARGE,
        'name': 'Cave backdrop (large)',
        'donor': 202,
        'footpad': (8, 8, 0),
        'copy': (564, 7),
        'copy_clips': CAVE_BACKDROP_CLIPS,
    },
    {
        'shape': SHAPE_DECORATIVE_WATER,
        'name': 'Decorative navy water',
        'donor': 202,
        'footpad': (4, 4, 0),
        'copy': (347, 1),
        'copy_frames': (16,),
    },
    {
        'shape': SHAPE_SANCTUM_BACKDROP,
        'name': 'Sanctum rock backdrop',
        'donor': 202,
        'footpad': (6, 1, 6),
        'copy': (566, 15),
        # Move the decorative sort box behind the west passage while
        # retaining the original screen projection and all sprite pixels.
        'copy_shifts': ((0, -32),) * 15,
    },
    {
        # Contract 3. The ninth stone of Map 10's Sacred Circle, and the
        # only item on the track with no 1994 original to redraw: the
        # reference is the RING, shape 38 frames 2 and 3, rendered clean
        # at shared/docs/art-poc/sacred-rock/reference-ring-stones.png.
        # Donor 66, the shape it replaces, so nothing about how it
        # collides changes except the height; footpad x/y stays (4,4)
        # because the box clears MAP10_ROOT_SEED by exactly one world
        # unit, and z goes 5 -> 8 for the 64x96 screen box 96 px needs.
        'shape': SHAPE_SACRED_ROCK,
        'name': 'Sacred Rock',
        'donor': 66,
        'footpad': (4, 4, 8),
        'frames': [('sacred-rock/C2_raw.png', 96, MAGENTA, 130, 16)],
    },
    {
        # Contract 4. The Message Scroll on the Scroll Chamber's plinth,
        # Map 17, where a wooden stool stood. No 1994 original either, so
        # the reference is the game's own scroll: shape 159 frames 0 and 3,
        # rendered clean at message-scroll/reference-base-scroll.png.
        # Donor 159 with its own footpad, which makes the item CARRYABLE
        # (no SI_FIXED, so beat 14 can have the Avatar take it to
        # Ezrekal) and SF_QUALITY (the one family I_getQuality answers
        # for, so quality 80 stops being map-side bookkeeping). The
        # 30x22 resize is deliberately non-uniform: the generator draws
        # the sheet square, seen from straight above, and the squash is
        # the projection onto the 2:1 floor plane.
        'shape': SHAPE_MESSAGE_SCROLL,
        'name': 'Message Scroll',
        'donor': 159,
        'footpad': (2, 2, 1),
        'width': 30,
        'frames': [('message-scroll/A2_raw.png', 22, MAGENTA, 130, 16)],
    },
    {
        # Contract 5. Four frames, one per element, in the ORDER THE MAP
        # PLACES THEM (build_map_11.py: frame 0 Earth q201, 1 Air q202,
        # 2 Fire q203, 3 Water q204). Frame 2, the Fire pillar, is the
        # 1994 Pillar of Fire since 2026-10-25 (registry 2023, screen07:
        # 2021's upper two thirds, the lower shaft cut where the shot shows
        # it and drawn behind the candle post, the flames at its flanks and
        # the lava at its foot). Frames 0, 1 and 3 are its column redrawn
        # for Earth, Air and Water since 2026-10-30 (registry 2024-2026,
        # tools/art/pillar_1994_style.py: 2023's canvas and hotspot, the
        # cap and flare recoloured onto the element's ramp). A dict entry
        # is an `indexed` frame inside a drawn row. Donor 38 is the ring
        # stone; footpad (2,2,10), 80 units tall.
        'shape': SHAPE_ELEMENTAL_PILLAR,
        'name': 'Elemental pillar',
        'donor': 38,
        'footpad': (2, 2, 10),
        'frames': [{'indexed': (2024, 0)},
                   {'indexed': (2025, 0)},
                   {'indexed': (2023, 0)},
                   {'indexed': (2026, 0)}],
        'oversize': "the pillars' flames (the fire's, recoloured for the "
                    'other three) and foot pools spread past the 64x64 box, '
                    'as screen07 draws the Pillar of Fire',
    },
    {
        # Contract 5. The socket beside each pillar. Donor 443's own
        # (3,3,3): a 48x48 box, 24 tall, that a 40-px sprite fits.
        'shape': SHAPE_PILLAR_RECEPTACLE,
        'name': 'Pillar receptacle',
        'donor': 443,
        'footpad': (3, 3, 3),
        'frames': [('pillars/R_raw.png', 40, MAGENTA, 130, 16)],
    },
    {
        # Contract 11. Tyorvi's elixir: the blood vial with a sea-green
        # brew. Donor 180, the engine's bottle, has 395's own flags,
        # footpad and weight but family SF_GENERIC, not SF_REAGENT.
        'shape': SHAPE_ELIXIR,
        'name': "Tyorvi's elixir",
        'donor': 180,
        'footpad': (1, 1, 1),
        'recolour': (395, 5, ELIXIR_REMAP),
    },
    {
        # Contract 12. The special root, candidate C.
        'shape': SHAPE_SPECIAL_ROOT,
        'name': 'Special root',
        'donor': 180,
        'footpad': (2, 2, 1),
        'frames': [('special-root/C_raw.png', 16, MAGENTA, 130, 0)],
    },
    {
        # Contract 13. The Passage Test plant, candidate A, sized by width.
        'shape': SHAPE_TEST_PLANT,
        'name': 'Passage Test plant',
        'donor': 65,
        'footpad': (3, 3, 4),
        'width': 48,
        'frames': [('test-plant/A_raw.png', None, MAGENTA, 130, 0)],
    },
    # ---- The 1994 art: indexed rows, registry ids in vignettes/ ----
    {
        # The cloud floor, registry 2000: f0-f2 cut from screen11, f3/f4
        # their mirror images (FLG_FLIPPED placements in 1994), all five
        # re-found in screen13/01/12. Donor 163, a retail 4x4x0 floor whose
        # row is 301's (the frames sit on 301's mask and hotspot) with
        # SI_DRAW swapped for SI_OCCL, byte for byte: the glob floors'
        # flag. SortItem::below orders two flats on one z by SI_DRAW first,
        # then SI_OCCL (.claude/rules/map-geometry.md), so this tile draws
        # over the SI_DRAW earth it lies on in screen13 (with 301's own
        # SI_DRAW the screen13 replay drops 74.1 -> 63.4%) and under the
        # flat props lying on it, the straw of screen12's nook (with
        # neither flag 82.8 -> 82.7%, with SI_OCCL 83.2%). phaseC-art.md.
        'shape': SHAPE_CLOUD_1994,
        'name': 'Cloud floor (1994)',
        'donor': 163,
        'footpad': (4, 4, 0),
        'indexed': [(2000, f) for f in range(5)],
        'hotspot_shift': FLOOR_Z0_SHIFT,
    },
    {
        # The white column, registry 2001: frame 0 plain (screen11's gem
        # pillar shafts; single-shot paint, its shaft validated through
        # frame 1), frame 1 orange-banded (screen12's posts, screen11's
        # obelisk drums). Donor 443 `statue` (SI_FIXED|SI_SOLID) with the
        # registry's 32x32x40 box, (1,1,5) — retail 12's own footpad, the
        # obelisk drums the column carries.
        'shape': SHAPE_WHITE_COLUMN_1994,
        'name': 'White column (1994)',
        'donor': 443,
        'footpad': (1, 1, 5),
        'indexed': [(2001, 0), (2001, 1)],
    },
    {
        # The gold brick floor, registry 2004 (screen12, single-shot).
        # A flat like the cloud, on the cloud's row.
        'shape': SHAPE_GOLD_BRICK_1994,
        'name': 'Gold brick floor (1994)',
        'donor': 163,
        'footpad': (4, 4, 0),
        'indexed': [(2004, 0), (2004, 1)],
        'hotspot_shift': FLOOR_Z0_SHIFT,
    },
    {
        # The marble walkway slab, registry 2003 (screen12, single-shot):
        # one 62x52 frame, top, gold-trimmed front face and back rim
        # together, repeating every 128 units. 19 pixels no screen12
        # instance shows are inferred (registry inferred_px). Donor 113,
        # the raised platform, (4,4,1): the 128x128x8 slab the
        # reconstruction solved.
        'shape': SHAPE_MARBLE_WALKWAY_1994,
        'name': 'Marble walkway (1994)',
        'donor': 113,
        'footpad': (4, 4, 1),
        'indexed': [(2003, 0)],
        'hotspot_shift': FLOOR_Z0_SHIFT,
        'oversize': 'the back rim stands 12 px over the 8-unit slab, as the '
                    'screen12 walkway does; the slab, not the rim, is what '
                    'is walked on',
    },
    {
        # The Shield halves as 1994 drew them, SHADES.UNK's frame order: 0 the
        # sun half (registry 2002, screen11), 1 the eye half (2005, the
        # screen12 draft, 269/274 in screen04). The registry has no eye
        # hotspot (it is never placed whole); (-4,36) is where screen04's
        # altar Shield (2013) puts it against the sun half's (6,32): the eye
        # sits at (+10,-4) in that composite, so the two halves at one
        # position reassemble 879. Donor 828 whole, (1,3,3): the halves are
        # drawn in the whole Shield's box.
        'shape': SHAPE_SHIELD_HALVES_1994,
        'name': 'Shield halves (1994)',
        'donor': 828,
        'footpad': (1, 3, 3),
        'indexed': [(2002, 0), (2005, 0, (-4, 36))],
    },
    {
        # The reassembled Shield on the sanctum altar, registry 2013
        # (screen04): retail 828's disc carrying the 1994 emblems, 608/609
        # px equal to the sun half plus the eye half. 828's row and anchor.
        'shape': SHAPE_SACRED_SHIELD_1994,
        'name': 'Sacred Shield (1994)',
        'donor': 828,
        'footpad': (1, 3, 3),
        'indexed': [(2013, 0)],
    },
    {
        # The gem on screen11's gem pillars: retail 596's frames, fixed.
        'shape': SHAPE_GEM_CAP_1994,
        'name': 'Gem pillar cap',
        'donor': 443,
        'footpad': (1, 1, 1),
        'copy': (596, 8),
    },
    {
        # The pre-2026-10-17 halves (870) as the 1994 halves: 878's frames
        # and, through donor 878, its TYPEFLAG row. MUST come after the 878
        # row: both the frames and the donor row are read from this run's
        # output (build_copy, main's TYPEFLAG loop).
        'shape': SHAPE_SHIELD_HALVES_LEGACY,
        'name': 'Shield halves (legacy 870)',
        'donor': SHAPE_SHIELD_HALVES_1994,
        'footpad': (1, 3, 3),
        'copy': (SHAPE_SHIELD_HALVES_1994, 2),
    },
    {
        # The striped prop on Felicitar's plinth, registry 2014 (screen04,
        # single-shot, unidentified). Fixed (donor 443) on the box the
        # reconstruction sorted it with, 32x32x8. A 64x64x8 box would hold
        # the sprite but sorts it differently against Felicitar: screen04's
        # window loses 0.07 points.
        'shape': SHAPE_STRIPED_PROP_1994,
        'name': 'Striped prop on the plinth (1994)',
        'donor': 443,
        'footpad': (1, 1, 1),
        'indexed': [(2014, 0)],
        'oversize': 'the 1994 sprite lies across the plinth top past its '
                    '32x32x8 box (twice its screen width), as screen04 '
                    'draws it',
    },
    # ---- Phase D (2026-10-25): screen12/13 pieces no retail frame matches ----
    {
        # screen12's throne-nook dais (registry 2006): the walkway's marble
        # run along y, the 877 tile mirrored and lit two steps lighter where
        # the shot hides it. Three single-use frames: the tiles between the
        # strips (0, 1) and where the dais crosses strip A (2). 877's row.
        'shape': SHAPE_NOOK_DAIS_1994,
        'name': 'Nook dais (1994)',
        'donor': 113,
        'footpad': (4, 4, 1),
        'indexed': [(2006, f) for f in range(3)],
        'hotspot_shift': FLOOR_Z0_SHIFT,
        'oversize': 'the back rim stands 12 px over the slab, as 877 does',
    },
    {
        # The walkway strips' east end (registry 2007): 877 cut on the
        # screen vertical through its front corner, behind screen12's
        # two-drum end posts. 877's row.
        'shape': SHAPE_WALKWAY_END_1994,
        'name': 'Walkway east end (1994)',
        'donor': 113,
        'footpad': (4, 4, 1),
        'indexed': [(2007, 0)],
        'hotspot_shift': FLOOR_Z0_SHIFT,
        'oversize': 'the back rim stands 12 px over the slab, as 877 does',
    },
    {
        # Gold brick meeting the cloud (registry 2008): f0/f1 screen12's
        # lobed cloud over the forecourt's gold (5 instances, 2 variants),
        # f2 the gold corner screen12 and screen13 both show. 876's row.
        'shape': SHAPE_GOLD_EDGE_1994,
        'name': 'Gold/cloud edge (1994)',
        'donor': 163,
        'footpad': (4, 4, 0),
        'indexed': [(2008, f) for f in range(3)],
        'hotspot_shift': FLOOR_Z0_SHIFT,
    },
    {
        # screen12's left throne, side on (registry 2009): no retail frame
        # matches. 223's row (the right throne's), on the 32x64 box the
        # nook's sort needs: behind the pot, in front of the dais.
        'shape': SHAPE_SIDE_THRONE_1994,
        'name': 'Side throne (1994)',
        'donor': 223,
        'footpad': (1, 2, 5),
        'indexed': [(2009, 0)],
    },
    {
        # screen13's floor (registry 2015): each cloud or gold tile of the
        # window cut to the pixels the shot shows it owning, earth there
        # transparent, the lobes no tile drew given to the nearest tile.
        # Single-use frames, one per vignette tile. The floor row.
        'shape': SHAPE_CLOUD_RIM_1994,
        'name': 'screen13 floor (1994)',
        'donor': 163,
        'footpad': (4, 4, 0),
        'indexed': [(2015, f) for f in range(35)],
        'hotspot_shift': FLOOR_Z0_SHIFT,
        'oversize': "the cloud's lobes spill past the 128-unit cell",
    },
    {
        # screen07's cave walls (registry 2043, phase E 2026-10-30): each
        # 26-family piece of the window with the shot's pixels it owns, the
        # spears in the rock, the right cliff's course seam and the back
        # wall's pointed end, over its retail frame. Donor 26 and 26's own
        # footpad: the piece sorts and collides as before.
        'shape': SHAPE_CAVE_FACE_1994,
        'name': 'screen07 cave wall (1994)',
        'donor': 26,
        'footpad': (4, 1, 6),
        'patch': 2043,
        'oversize': "the back wall's pointed east end runs past the piece",
    },
    {
        # screen07's floor round the Pillar of Fire (registry 2027): each
        # 301 tile of the window with the lava pit's glow and lip the shot
        # shows on it, over its retail frame. Donor 301, 301's footpad.
        'shape': SHAPE_CAVE_FLOOR_1994,
        'name': 'screen07 cave floor (1994)',
        'donor': 301,
        'footpad': (4, 4, 0),
        'patch': 2027,
    },
]

# Crest variants retain each source canvas and anchor. Variant zero keeps
# all paint; variants one through four keep the upper 8, 16, 24, or 32
# pixel rows, and variants five and six keep the left or right half.
# Site.cave_crest selects the largest safe variant at each authored anchor.
CREST_CROPS = (None, 8, 16, 24, 32, 'left', 'right')
PROPS.extend([
    {'shape': SHAPE_COURT_COBBLE_FLAT, 'name': 'Flat court cobbles',
     'donor': 71, 'footpad': (4, 4, 0), 'copy': (70, 23),
     'oversize': 'the retail cobble relief paints above its flat support'},
    {'shape': SHAPE_RUBBLE_DECORATIVE, 'name': 'Decorative low rubble',
     'donor': 465, 'footpad': (3, 3, 1), 'copy': (524, 6)},
    {'shape': SHAPE_BONES_DECORATIVE_A, 'name': 'Decorative bones A',
     'donor': 465, 'footpad': (3, 4, 1), 'copy': (235, 2)},
    {'shape': SHAPE_BONES_DECORATIVE_B, 'name': 'Decorative bones B',
     'donor': 465, 'footpad': (4, 3, 1), 'copy': (237, 2)},
    {'shape': SHAPE_CAVE_CREST_DECORATIVE, 'name': 'Decorative cave crest',
     'donor': 202, 'footpad': (4, 4, 0),
     'copy': (125, 23 * len(CREST_CROPS)),
     'copy_frames': tuple(f for f in range(23) for _ in CREST_CROPS),
     'copy_crops': CREST_CROPS * 23,
     'oversize': 'crest relief overhangs the zero-height decorative box'},
    {'shape': SHAPE_MOAT_BANK_DECORATIVE, 'name': 'Decorative moat bank',
     'donor': 465, 'footpad': (4, 4, 1), 'copy': (94, 11)},
    {'shape': SHAPE_MOAT_FACE_DECORATIVE, 'name': 'Decorative moat face',
     'donor': 465, 'footpad': (1, 4, 4), 'copy': (85, 7)},
])



# Shared slice 0.2: all rows supply paint without support or collision.
# The white drum is the screenshot column turned onto its side.
PROPS.extend([
    {'shape': 905, 'name': 'Fallen white drum', 'donor': 465,
     'footpad': (3, 2, 1), 'copy': (875, 1), 'copy_turn': True},
    {'shape': 906, 'name': 'Decorative roots', 'donor': 465,
     'footpad': (6, 5, 2), 'copy': (57, 4)},
    {'shape': 907, 'name': 'Decorative fungus', 'donor': 465,
     'footpad': (2, 2, 5), 'copy': (65, 26)},
    {'shape': 908, 'name': 'Decorative spires', 'donor': 465,
     'footpad': (4, 4, 5), 'copy': (66, 12)},
    {'shape': 909, 'name': 'Decorative urn', 'donor': 465,
     'footpad': (1, 1, 2), 'copy': (229, 1)},
    {'shape': 910, 'name': 'Decorative threshold rubble', 'donor': 465,
     'footpad': (2, 2, 2), 'copy': (526, 9)},
    {'shape': 911, 'name': 'Decorative basalt shore', 'donor': 465,
     'footpad': (4, 4, 1), 'copy': (122, 30)},
    {'shape': 912, 'name': 'Decorative relief x', 'donor': 465,
     'footpad': (1, 4, 5), 'copy': (246, 10)},
    {'shape': 913, 'name': 'Decorative relief y', 'donor': 465,
     'footpad': (4, 1, 5), 'copy': (252, 10)},
    {'shape': 914, 'name': 'Decorative eight-unit Air face', 'donor': 465,
     'footpad': (4, 1, 1), 'copy': (26, 15),
     'copy_crops': ('base8',) * 15,
     'oversize': 'the clipped eight-unit face retains the original transparent canvas'},
    {'shape': 915, 'name': 'Retained-wall rock skin', 'donor': 465,
     'footpad': (4, 1, 5), 'copy': (15, 10), 'copy_texture': (125, 12)},
])


# Each star copy paints from an actual viewing ground chunk at z zero.
# The engine frame field is a byte, so 28 layouts of nine source frames
# fit each row. All offsets preserve the original palette indices.
# Layout order and row and frame allocations are save-visible.
# Keep the existing 337-layout prefix frozen.
STAR_LAYOUTS_PER_SHAPE = 28
STAR_LAYOUTS = ((0,0,False,False),) + tuple((dx,dy,nx,ny)
    for nx,ny in ((False,True),(True,False),(True,True))
    for dx in range(-4096,4097,512) for dy in range(-4096,4097,512)
    if (not nx or dx>0) and (not ny or dy>0))
STAR_LAYOUT_INDEX = {row:k for k,row in enumerate(STAR_LAYOUTS)}
for start in range(0,len(STAR_LAYOUTS),STAR_LAYOUTS_PER_SHAPE):
    layouts=STAR_LAYOUTS[start:start+STAR_LAYOUTS_PER_SHAPE]
    PROPS.append({'shape': 916+start//STAR_LAYOUTS_PER_SHAPE,
        'name': f'Shifted decorative stars {start//STAR_LAYOUTS_PER_SHAPE}',
        'donor': 202, 'footpad': (4,4,0), 'copy': (351,9*len(layouts)),
        'copy_frames': tuple(f for layout in layouts for f in range(9)),
        'copy_shifts': tuple((dx//4-dy//4+int(ny)-int(nx),
                              dx//8+dy//8-int(nx)-int(ny))
                             for dx,dy,nx,ny in layouts for f in range(9))})


def rock_skin_copy(frame, texture):
    """Put crest stone inside the retained wall's exact painted silhouette."""
    w,h = texture['width'],texture['height']
    # The central stone patch supplies opaque rock, without the cap's sky.
    opaque = [p for p in texture['pixels'] if p != KEYCOLOR]
    pixels=[]
    for k,p in enumerate(frame['pixels']):
        x,y = k % frame['width'],k // frame['width']
        q = texture['pixels'][(h//2+y%8)*w+(w//4+x%(w//2))]
        pixels.append(KEYCOLOR if p==KEYCOLOR else q if q!=KEYCOLOR else opaque[k%len(opaque)])
    return dict(frame,pixels=pixels)


def turn_copy(frame):
    """Lay the white cylinder horizontally, preserving palette indices."""
    w, h = frame['width'], frame['height']
    pixels = frame['pixels']
    out = dict(frame, width=h, height=w, xoff=h//2, yoff=w-1)
    out['pixels'] = [pixels[(h-1-x)*w+y] for y in range(w) for x in range(h)]
    return out


def crop_copy(frame, crop):
    """Remove paint outside a crest variant, retaining canvas and anchor."""
    pixels, w = frame['pixels'], frame['width']
    return [px if (crop is None or
                   (isinstance(crop, int) and i // w < crop) or
                   (crop == 'left' and i % w < w // 2) or
                   (crop == 'right' and i % w >= w // 2) or
                   (crop == 'base8' and i // w >= frame['yoff'] - 8 + (i % w - frame['xoff']) // 2)) else KEYCOLOR
            for i, px in enumerate(pixels)]


def frame_args(height, key_rgb, tolerance, despill, prop):
    """png2shape's build_frame() takes an argparse namespace; this is one.
    Every prop is keyed, trimmed, scaled to `height` (or `width`), and
    anchored bottom-centre — the prop convention: the sprite's foot lands on
    the item's world position, which is the near vertex of its footpad box."""
    return SimpleNamespace(
        no_key=False, key_rgb=key_rgb,
        key_tolerance=tolerance, key_despill=despill,
        no_trim=False, height=height,
        width=prop.get('width'),
        alpha_threshold=128, anchor='bottom-center',
        donor=prop['donor'], xoff=None, yoff=None,
    )


def build_copy(prop, flx_bytes, built=None):
    """A 'copy' row -> ([frame blob, ...], [report, ...]): the source
    shape's first n frames or explicit copy_frames selection. Optional
    copy_shifts change anchors while preserving every source pixel.
    copy_clips appends masked frames after the original copies.
    The source comes from an earlier built row or the pristine base FLX."""
    shape, n = prop['copy']
    data = (built or {}).get(shape) or read_flx_entry(flx_bytes, shape)
    if not data:
        raise SystemExit(f"{prop['name']}: source shape {shape} is missing")
    frames = parse_shape_frames(data)
    indices = prop.get('copy_frames', tuple(range(n)))
    if len(indices) != n or any(i < 0 or i >= len(frames) for i in indices):
        raise SystemExit(f"{prop['name']}: source shape {shape} has "
                         f"{len(frames)} frames, not {n}")
    blobs, reports = [], []
    for output_index, index in enumerate(indices):
        f = dict(frames[index])
        if prop.get('copy_turn'):
            f = turn_copy(f)
        if 'copy_texture' in prop:
            ts,tf = prop['copy_texture']
            texture = parse_shape_frames(read_flx_entry(flx_bytes,ts))[tf]
            f = rock_skin_copy(f,texture)
        if 'copy_crops' in prop:
            f['pixels'] = crop_copy(f, prop['copy_crops'][output_index])
        dx, dy = prop.get('copy_shifts', ((0, 0),) * n)[output_index]
        f['xoff'] += dx
        f['yoff'] += dy
        blob = encode_frame(f['pixels'], f['width'], f['height'], f['xoff'],
                            f['yoff'])
        blobs.append(blob)
        reports.append({'size': (f['width'], f['height']),
                        'colors': len({px for px in f['pixels'] if px != 255}),
                        'bytes': len(blob), 'anchor': (f['xoff'], f['yoff'])})
    for clip in prop.get('copy_clips', ()):
        f = frames[clip['frame']]
        path = os.path.join(SHARED, 'data', 'lv-1994-art', clip['mask'])
        mask = Image.open(path).convert('L')
        if mask.size != (f['width'], f['height']):
            raise ValueError(f"{path}: mask size differs from source frame")
        keep = list(mask.getdata())
        if any(v not in (0, 255) for v in keep):
            raise ValueError(f"{path}: opacity mask must be binary")
        pixels = [px if v else 255 for px, v in zip(f['pixels'], keep)]
        if all(px == 255 for px in pixels):
            raise ValueError(f"{path}: clipped frame is empty")
        blob = encode_frame(pixels, f['width'], f['height'], f['xoff'], f['yoff'])
        blobs.append(blob)
        reports.append({'size': (f['width'], f['height']),
                        'colors': len({px for px in pixels if px != 255}),
                        'bytes': len(blob), 'anchor': (f['xoff'], f['yoff'])})
    return blobs, reports


def build_recolour(prop, flx_bytes):
    """A 'recolour' row -> (frame blob, report). The source frame's own
    geometry and anchor are kept; only the remapped indices change."""
    shape, frame, remap = prop['recolour']
    data = read_flx_entry(flx_bytes, shape)
    if not data:
        raise SystemExit(f"{prop['name']}: source shape {shape} is missing")
    frames = parse_shape_frames(data)
    if frame >= len(frames):
        raise SystemExit(f"{prop['name']}: source shape {shape} has "
                         f"{len(frames)} frames, no frame {frame}")
    f = frames[frame]
    hit = sum(1 for px in f['pixels'] if px in remap)
    if not hit:
        raise SystemExit(
            f"{prop['name']}: shape {shape} frame {frame} uses none of "
            f"palette indices {sorted(remap)} — the base art changed; update "
            f"the remap rather than ship the source frame unrecoloured")
    pixels = [remap.get(px, px) for px in f['pixels']]
    blob = encode_frame(pixels, f['width'], f['height'], f['xoff'], f['yoff'])
    return blob, {
        'size': (f['width'], f['height']),
        'colors': len({px for px in pixels if px != 255}),
        'bytes': len(blob), 'anchor': (f['xoff'], f['yoff']),
        'recoloured': hit,
    }


def load_registry(path=REGISTRY):
    with open(path) as f:
        return json.load(f)


def patch_frame(base, png_pixels, w, h, hotspot):
    """`base` (a parsed frame) with a PNG's opaque pixels laid over it, the
    PNG's `hotspot` on the base's anchor -> (pixels, width, height, xoff,
    yoff) of a canvas holding both."""
    hx, hy = hotspot
    bx, by = base['xoff'], base['yoff']
    x0, y0 = min(-bx, -hx), min(-by, -hy)
    x1 = max(base['width'] - bx, w - hx)
    y1 = max(base['height'] - by, h - hy)
    cw, ch = x1 - x0, y1 - y0
    out = [KEYCOLOR] * (cw * ch)
    for src, sw, sh, ax, ay in ((base['pixels'], base['width'],
                                 base['height'], bx, by),
                                (png_pixels, w, h, hx, hy)):
        dx, dy = -ax - x0, -ay - y0
        for n, px in enumerate(src):
            if px != KEYCOLOR:
                out[(n // sw + dy) * cw + n % sw + dx] = px
    return out, cw, ch, -x0, -y0


def patch_sources(prop, registry):
    """A 'patch' row -> its registry frames, refusing non-sprite grades."""
    shape = registry['shapes'].get(str(prop['patch']))
    if shape is None or not shape['frames']:
        raise SystemExit(f"{prop['name']}: registry has no {prop['patch']}")
    for n, fr in enumerate(shape['frames']):
        if fr['grade'] in NOT_A_SPRITE:
            raise SystemExit(f"{prop['name']}: registry {prop['patch']}:{n} "
                             f"is graded {fr['grade']}, not a sprite")
    return shape['frames']


def build_patch(prop, palette, flx_bytes):
    """A 'patch' row -> ([frame blob, ...], [report, ...])."""
    blobs, reports = [], []
    for n, fr in enumerate(patch_sources(prop, load_registry())):
        bs, bf = fr['base']
        data = read_flx_entry(flx_bytes, bs)
        frames = parse_shape_frames(data) if data else []
        if bf >= len(frames):
            raise SystemExit(f"{prop['name']}: base {bs}:{bf} is missing")
        path = os.path.join(ROOT, fr['png'])
        try:
            pixels, w, h, _used = indexed_pixels(path, palette)
        except Refused as exc:
            raise SystemExit(f"{prop['name']}: {exc}")
        px, cw, ch, ax, ay = patch_frame(frames[bf], pixels, w, h,
                                         fr['hotspot'])
        blob = encode_frame(px, cw, ch, ax, ay)
        blobs.append(blob)
        reports.append({'size': (cw, ch),
                        'colors': len(set(px) - {KEYCOLOR}),
                        'bytes': len(blob), 'anchor': (ax, ay),
                        'source': f"{prop['patch']}:{n} on {bs}:{bf}"})
    return blobs, reports


def indexed_sources(prop, registry):
    """An 'indexed' row -> [{'ref', 'png', 'anchor', 'grade', 'inferred_px'},
    ...] per frame: the registry frame's repo-relative PNG and the anchor the
    frame is encoded with (registry hotspot + the row's hotspot_shift, or the
    entry's own). Refuses reference crops and residuals, and a frame with no
    hotspot from either source."""
    dx, dy = prop.get('hotspot_shift', (0, 0))
    out = []
    for entry in prop['indexed']:
        sid, fno = entry[0], entry[1]
        shape = registry['shapes'].get(str(sid))
        if shape is None or fno >= len(shape['frames']):
            raise SystemExit(f"{prop['name']}: registry has no {sid}:{fno}")
        fr = shape['frames'][fno]
        if fr['grade'] in NOT_A_SPRITE:
            raise SystemExit(f"{prop['name']}: registry {sid}:{fno} is graded "
                             f"{fr['grade']}, not a sprite — never build it")
        if len(entry) > 2:
            anchor = tuple(entry[2])
        elif fr['hotspot'] is not None:
            anchor = (fr['hotspot'][0] + dx, fr['hotspot'][1] + dy)
        else:
            raise SystemExit(f"{prop['name']}: registry {sid}:{fno} has no "
                             f"hotspot; give the row entry its own (xoff, yoff)")
        out.append({'ref': f'{sid}:{fno}', 'png': fr['png'], 'anchor': anchor,
                    'grade': fr['grade'],
                    'inferred_px': fr.get('inferred_px') or []})
    return out


def build_indexed(prop, palette):
    """An 'indexed' row -> ([frame blob, ...], [report, ...]): each PNG's
    U8PAL indices verbatim (png2shape --indexed), at its anchor."""
    blobs, reports = [], []
    for src in indexed_sources(prop, load_registry()):
        path = os.path.join(ROOT, src['png'])
        if not os.path.exists(path):
            raise SystemExit(f"missing art for {prop['name']}: {path}")
        try:
            pixels, w, h, used = indexed_pixels(path, palette)
        except Refused as exc:
            raise SystemExit(f"{prop['name']}: {exc}")
        blob = encode_frame(pixels, w, h, *src['anchor'])
        blobs.append(blob)
        reports.append({'size': (w, h), 'colors': len(used),
                        'bytes': len(blob), 'anchor': src['anchor'],
                        'opaque': sum(1 for p in pixels if p != KEYCOLOR),
                        'source': src['ref'], 'grade': src['grade']})
    return blobs, reports



def build_prop(prop, palette, flx_bytes, built=None):
    """One PROPS row -> (shape blob, [frame report, ...]). `built` maps the
    shapes earlier rows of this run built to their blobs ('copy' reads it)."""
    if 'copy' in prop:
        blobs, reports = build_copy(prop, flx_bytes, built)
        return encode_shape_blobs(blobs), reports
    if 'recolour' in prop:
        blob, report = build_recolour(prop, flx_bytes)
        return encode_shape_blobs([blob]), [report]
    if 'indexed' in prop:
        blobs, reports = build_indexed(prop, palette)
        return encode_shape_blobs(blobs), reports
    if 'patch' in prop:
        blobs, reports = build_patch(prop, palette, flx_bytes)
        return encode_shape_blobs(blobs), reports
    blobs, reports = [], []
    for i, entry in enumerate(prop['frames']):
        if isinstance(entry, dict):
            # a 1994 frame inside a drawn row (865 frame 2)
            b, r = build_indexed({**prop, 'indexed': [entry['indexed']]}, palette)
            blobs += b
            reports += r
            continue
        rel, height, key_rgb, tol, despill = entry
        path = os.path.join(ART, rel)
        if not os.path.exists(path):
            raise SystemExit(f"missing art for {prop['name']}: {path}")
        blob, report = build_frame(
            path, frame_args(height, key_rgb, tol, despill, prop),
            palette, flx_bytes, i)
        blobs.append(blob)
        reports.append(report)
    return encode_shape_blobs(blobs), reports


def check_fit(prop, reports):
    """The same check png2shape prints: the authored footpad must contain
    the art, or the engine sorts and collides against the wrong volume."""
    nw = max(r['size'][0] for r in reports)
    nh = max(r['size'][1] for r in reports)
    want = suggest_footpad(nw, nh)
    have = prop['footpad']
    hw, hh = footpad_screen_size(*have)
    print(f"  footpad {have} covers {hw}x{hh}px; art {nw}x{nh}px "
          f"(suggest_footpad says {want})")
    if hw * 1.25 < nw or hh * 1.25 < nh:
        if prop.get('oversize'):
            print(f"  NOTE  art over the box by design: {prop['oversize']}")
            return
        raise SystemExit(
            f"{prop['name']}: footpad {have} is smaller than the art "
            f"({nw}x{nh}px) — author a box that contains it")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=OUT_SHAPES)
    ap.add_argument('--src', default=None,
                    help='source U8SHAPES.FLX (default: the pristine base)')
    ap.add_argument('--preview', action='store_true',
                    help='inject into a temp FLX and render every prop')
    args = ap.parse_args()

    src = args.src
    if src is None:
        from base_input import pristine_base
        src = pristine_base(SHAPES_FLX, None, 'base U8SHAPES.FLX')

    print(f"=== LV art-track static props ({len(PROPS)} shape(s)) ===")
    base = open(src, 'rb').read()
    palette = load_palette(PALETTE_FILE)

    built = []
    done = {}
    props_ids = {p['shape'] for p in PROPS}
    for prop in PROPS:
        # A row that copies another row's frames or TYPEFLAG reads them from
        # this run's output, so that row must come first.
        for dep in (prop.get('copy', (None,))[0], prop['donor']):
            if dep in props_ids and dep not in done:
                raise SystemExit(f"{prop['name']}: copies shape {dep}, which "
                                 f"a later PROPS row builds — move it after")
        blob, reports = build_prop(prop, palette, base, done)
        done[prop['shape']] = blob
        for i, r in enumerate(reports):
            w, h = r['size']
            print(f"  shape {prop['shape']} frame {i}  {prop['name']:<18} "
                  f"{w:>3}x{h:<3} {r['colors']:>3} colours  "
                  f"{r['bytes']:>6} B  anchor {r['anchor']}")
        # validate_shape returns a LIST of errors; empty means safe to load.
        errs = validate_shape(blob)
        if errs:
            raise SystemExit(f"{prop['name']}: shape failed validation:\n  " +
                             "\n  ".join(errs))
        print(f"  shape {prop['shape']}: {len(reports)} frame(s), "
              f"{len(blob)} bytes, validate_shape clean")
        check_fit(prop, reports)
        built.append((prop, blob, len(reports)))

    if args.preview:
        from lv_wood_wall import preview
        dst = '/tmp/U8SHAPES_props.FLX'
        cur = src
        for prop, blob, n in built:
            inject_shape(blob, prop['shape'], cur, dst)
            cur = dst
            out = f"/tmp/prop_{prop['shape']}.png"
            preview(prop['shape'], palette, shapes_flx=dst, out=out, nframes=n)
            print(f"  preview -> {out}")
        return

    from patch_typeflag import patch_entry_in_file
    tf = os.path.join(SHARED, 'build', 'TYPEFLAG.DAT')
    for prop, blob, _n in built:
        # inject_shape refuses an occupied slot, so a stale or colliding id
        # fails loud here rather than re-skinning something.
        inject_shape(blob, prop['shape'],
                     args.out if os.path.exists(args.out) else src, args.out)
        print(f"  shape {prop['shape']} injected into {args.out}")
        old, new = patch_entry_in_file(tf, prop['shape'], prop['donor'],
                                       footpad=prop['footpad'])
        print(f"  TYPEFLAG slot {prop['shape']} <- {prop['donor']} "
              f"footpad {prop['footpad']}: {old.hex()} -> {new.hex()}")


if __name__ == '__main__':
    main()
