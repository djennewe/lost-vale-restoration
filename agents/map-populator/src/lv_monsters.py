#!/usr/bin/env python3
"""
lv_monsters.py — the expansion's own actors, as actor clones of a donor.

WHY THIS EXISTS
---------------
The 1994 Art List names two monsters for the Lost Vale, the Water Zombie of
the Lake and the Harpie of the Cloud Cliffs, and no art for either survives
(docs/art-track.md contract 9). Until 2026-10-11 the Lake's eggs hatched
the base ghoul 142 and the harpie zone's the base torax 120. Douglas,
2026-10-11: generated key poses, every frame of the donor's animation set
derived toward them.

WHAT THIS BUILDS — an actor needs four things
---------------------------------------------
Each row of MONSTERS is a new shape that is its donor in every file the
engine reads for an actor, except for the pixels:

  U8SHAPES.FLX  the donor's frames, in the donor's frame layout, with the
                row's art. A frame layout kept means ANIM.DAT's frame
                numbers stay right.
  TYPEFLAG.DAT  the donor's row verbatim: flags, family SF_CONTAINER (6, the
                actor family map_validate's monster-egg rule checks), the
                footpad that decides where an egg can hatch it, weight.
  ANIM.DAT      the new shape's offset-table entry = the donor's, so both
                share one action table (lv_tiny_avatar.clone_anim_entry):
                the donor's timing, hit windows and sound effects.
  u8monsters.ini  a row keyed by the new shape: the donor's stats, with
                the row's 'stats' overrides. This is engine data, not a
                game file: install_lv.sh writes it into the game directory
                (`python3 lv_monsters.py ini ...`, below). Without it
                TypeFlags has no MonsterInfo for the shape, and
                MonsterEgg::hatch spawns a monster with no hit points.

THE STATS. The Water Zombie began with the ghoul's (35-50 hp, 6-12 a
blow, dex 14-16, armour 15), and one of them killed an Avatar armed with
the axe in about 10 s, 2 of 2, with a wave of two taking about 8 s
(docs/playtest-2026-10-25-phaseD-verify.md F2). Douglas (2026-10-30):
weaken it. Its row is now softer than the harpie's, because the Lake
sends zombies two at a time on a narrow pier over water: hp 25-35, 3-7 a
blow, dex 10-12 (fewer hits landed, a longer pause between blows),
armour 8 (an axe or sword blow keeps 76% after armour, against 55% at
the ghoul's 15). It keeps the ghoul's undead defense.
The Harpie does not keep the torax's: armour 28 and defense
0x82 (blade-proof, blunt halved, 84% off what is left: Actor::
calculateAttackDamage) made it close to unkillable for the Avatar the
Cloud Cliffs see, whose only weapon on the quest's way is Galjeron's
sword on Map 9 (shape 420, blade) — the starting sword never hurt one
and the Deceiver did 1-2 (playtest-2026-10-11-monsters finding 5). Its
row is retail's changeling's — the open-ground beast of the same weight
(30-45 hp, armour 11, defense 0) — with talons between its 7-10 and the
ghoul's 6-12, 5-10, and the torax's own slow dex (8-12, 45 ticks between
blows): hp 30-45, 5-10 a talon, armour 11, defense 0. A sword's 10-23
(str 26: MainActor::getDamageAmount) lands 6-15 after armour, three or
four blows a harpie. The climb meets them one at a time since 2026-10-24
(build_map_13 THE HARPIES). Even one at a time, the summit harpie killed
an axe-armed 30-hp Avatar 3 of 3 times: each talon interrupts his run, so
he cannot break off (docs/playtest-2026-10-30-phaseE-verify.md F1).
Douglas (2026-10-31): weaken it, as the zombie was. One row serves every
harpie, so all of them are now hp 22-32, 3-7 a talon, armour 8 (a blow
keeps 76% after armour), with the torax's slow dex kept.

THE WATER ZOMBIE (872) is the ghoul's own 451 frames recoloured to the
1994 zombie of screen02 and screen09, with the shots' three poses at the
frames they show (lv_actor_art.py: ZOMBIE_REMAP, ZOMBIE_POSES; 2026-10-25,
replacing candidate A's blue-grey table of 2026-10-11). One table over
every frame keeps the ghoul's dithering, shading and motion pixel for
pixel. It is built from the pristine base ghoul here, the way
lv_tiny_tar.py builds 859 and lv_art_props.py 868, so no Origin pixel is
committed.

THE HARPIE (873) is drawn new in the torax 120's frame layout: the 86
frames the torax's ANIM.DAT entry references, sequenced from candidate A's
generated sheets (four wing phases per direction for the walk, five phases
for the attack and the death) by tools/art/monster_frames.py. Its build
input is those frames as palette-indexed PNGs plus anchors.json
(HARPIE_FRAMES): our art, so committed, and nothing is re-quantized here.

THE 1994 NPC BODIES (NPCS: 888 the Zealan elder, 889 and 890 the spear
children; 2026-10-25) are built in the same step the same way: the donor's
TYPEFLAG row and ANIM.DAT table, frames derived by lv_actor_art.py from the
pristine donor (Mythran 190, the child 708) and the 1994 cut-outs. They
are bodies for placed NPCs (build_map_10.py), not monsters: no
u8monsters.ini row and no usecode class (a placed LV NPC dispatches by its
npcnum).

ORDER. Build step 6/8 runs this after lv_tiny_avatar.py, which writes
ANIM.DAT from the pristine base; this step patches that ANIM.DAT and the
U8SHAPES/TYPEFLAG the earlier steps produced. Run the whole of step 6, not
this script twice: inject_shape refuses an occupied slot. Outputs are staged
as `<artifact>.staging`, verified, then promoted; a rejected build is
quarantined as `.failed` and the previous artifacts are left untouched.

Usage:
    python3 lv_monsters.py                          # the build step
    python3 lv_monsters.py ini ENGINE_INI OUT_INI   # u8monsters.ini + rows
"""

import json
import os
import re
import struct
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shape_viewer import read_flx_entry, SHAPES_FLX              # noqa: E402
from lv_wood_wall import (encode_frame, encode_shape_blobs,       # noqa: E402
                          inject_shape, validate_shape, num_frames)
from patch_typeflag import patch_entry_in_file, ENTRY_SIZE     # noqa: E402
from base_input import pristine_base                           # noqa: E402
from lv_tiny_avatar import actor_anim, clone_anim_entry        # noqa: E402
from lv_tiny_avatar_art import anim_offset                     # noqa: E402
from lv_shapes import (SHAPE_WATER_ZOMBIE, SHAPE_HARPIE,       # noqa: E402
                       SHAPE_ZEALAN_ELDER, SHAPE_SPEAR_CHILD_DARK,
                       SHAPE_SPEAR_CHILD_BLOND)
from lv_actor_art import ACTOR_ART, actor_frames               # noqa: E402

SHARED = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      '..', '..', '..', 'shared')
BUILD = os.path.join(SHARED, 'build')
OUT_SHAPES = os.path.join(BUILD, 'U8SHAPES.FLX')
OUT_TYPEFLAG = os.path.join(BUILD, 'TYPEFLAG.DAT')
OUT_ANIM = os.path.join(BUILD, 'ANIM.DAT')
HARPIE_FRAMES = os.path.join(SHARED, 'docs', 'art-poc', 'harpie', 'frames-A')

# Palette indices 1-14 are rewritten every tick by the engine's CycleProcess
# (gfx/cycle_process.cpp), and 255 is the shape format's transparency: a
# drawn frame may never use a cycling index.
CYCLING = frozenset(range(1, 15))

# One row per monster. 'art' names the lv_actor_art.py derivation that
# builds the frames from the donor's; 'frames_dir' a drawn monster's
# committed frames; 'ini' the donor's u8monsters.ini section and the new
# section; 'stats' replaces those keys of the donor's row (THE STATS, above).
MONSTERS = [
    {
        'name': 'Water Zombie',
        'shape': SHAPE_WATER_ZOMBIE,
        'donor': 142,                  # ghoul
        'frames': 451,
        'art': 'zombie',
        'ini': ('ghoul', 'waterzombie'),
        'stats': {'hp_min': 25, 'hp_max': 35, 'dex_min': 10, 'dex_max': 12,
                  'damage_min': 3, 'damage_max': 7, 'armour': 8},
    },
    {
        # Drawn new in the torax's layout: the 86 frames its ANIM.DAT entry
        # references (walk/run/advance/stand, attack/combat stance/idle,
        # die/standUp/stumble), from candidate A's generated sheets.
        'name': 'Harpie',
        'shape': SHAPE_HARPIE,
        'donor': 120,                  # torax
        'frames': 240,
        'frames_dir': HARPIE_FRAMES,
        'ini': ('torax', 'harpie'),
        'stats': {'hp_min': 22, 'hp_max': 32, 'damage_min': 3,
                  'damage_max': 7, 'armour': 8, 'defense_type': '0x0000'},
    },
]

# The 1994 NPC bodies: built like MONSTERS, no u8monsters.ini row.
NPCS = [
    {'name': 'Zealan elder', 'shape': SHAPE_ZEALAN_ELDER, 'donor': 190,
     'frames': 350, 'art': 'elder'},                       # Mythran
    {'name': 'spear child (dark)', 'shape': SHAPE_SPEAR_CHILD_DARK,
     'donor': 708, 'frames': 100, 'art': 'child-dark'},
    {'name': 'spear child (blond)', 'shape': SHAPE_SPEAR_CHILD_BLOND,
     'donor': 708, 'frames': 100, 'art': 'child-blond'},
]

ACTORS = MONSTERS + NPCS

BLANK = dict(width=1, height=1, xoff=0, yoff=0, pixels=[255])


def drawn_frames(frames_dir, count):
    """A drawn monster's frames: one palette-indexed PNG per drawn frame
    (pixel value = U8PAL index, 255 transparent) and anchors.json, written
    by tools/art/monster_frames.py from the frames it read back from a
    scratch FLX. Every frame the file does not list is BLANK, a 1x1
    transparent frame (the donor draws them, nothing references them)."""
    meta = json.load(open(os.path.join(frames_dir, 'anchors.json')))
    if meta['frames'] != count:
        raise SystemExit(f"{frames_dir}: {meta['frames']} frames, expected "
                         f"{count}")
    out = [BLANK] * count
    for k, (xoff, yoff) in meta['anchors'].items():
        im = Image.open(os.path.join(frames_dir, f'{int(k):03d}.png'))
        if im.mode != 'P':
            raise SystemExit(f"{frames_dir}/{int(k):03d}.png is {im.mode}, "
                             f"not palette-indexed")
        pixels = list(im.tobytes())
        bad = sorted(set(pixels) & CYCLING)
        if bad:
            raise SystemExit(f"frame {k} uses cycling indices {bad}")
        out[int(k)] = dict(width=im.width, height=im.height, xoff=xoff,
                           yoff=yoff, pixels=pixels)
    return out


def drawn_shape(frames_dir, count):
    frames = drawn_frames(frames_dir, count)
    return encode_shape_blobs([encode_frame(f['pixels'], f['width'],
                                            f['height'], f['xoff'], f['yoff'])
                               for f in frames]), frames


# ---------------------------------------------------------------------------
# u8monsters.ini
# ---------------------------------------------------------------------------

def ini_sections(text):
    """{section name: [lines]} of an INI text, in order."""
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r'^\s*\[([^\]]+)\]\s*$', line)
        if m:
            cur = m.group(1)
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return out


INI_MARKER = '# Lost Vale: rows appended by agents/map-populator/src/lv_monsters.py'


def lv_monsters_ini(engine_text):
    """The engine's u8monsters.ini with one row per MONSTERS entry appended:
    the donor's section copied key for key, `shape=` set to the new shape
    and the entry's 'stats' put over the donor's values. Copied, not
    transcribed, so every key not overridden cannot drift from the donor's."""
    sections = ini_sections(engine_text)
    rows = [engine_text.rstrip('\n'), '', INI_MARKER]
    for m in MONSTERS:
        donor, new = m['ini']
        if donor not in sections:
            raise SystemExit(f"u8monsters.ini has no [{donor}] section")
        if new in sections:
            raise SystemExit(f"u8monsters.ini already has a [{new}] section")
        body = [ln for ln in sections[donor] if ln.strip()]
        shapes = [ln for ln in body if ln.split('=')[0].strip() == 'shape']
        if len(shapes) != 1 or int(shapes[0].split('=')[1]) != m['donor']:
            raise SystemExit(f"[{donor}] is not shape {m['donor']}: {shapes}")
        stats = dict(m.get('stats', {}), shape=m['shape'])
        keys = [ln.split('=')[0].strip() for ln in body]
        missing = sorted(set(stats) - set(keys))
        if missing:
            raise SystemExit(f"[{donor}] has no {missing} to override")
        rows.append(f'[{new}]')
        rows += [f"{k}={stats[k]}" if k in stats else ln
                 for k, ln in zip(keys, body)]
        rows.append('')
    return '\n'.join(rows) + '\n'


def cmd_ini(engine_ini, out_ini):
    text = open(engine_ini, encoding='latin-1').read()
    with open(out_ini, 'w', encoding='latin-1') as f:
        f.write(lv_monsters_ini(text))
    print(f"wrote {out_ini}: the engine's u8monsters.ini + "
          f"{', '.join(m['ini'][1] for m in MONSTERS)}")


# ---------------------------------------------------------------------------
# The build step
# ---------------------------------------------------------------------------

def _verify(m, blob, shapes_in, shapes_out, tf_in, tf_out, anim_in, anim_out):
    errs = []
    sid, donor = m['shape'], m['donor']
    if read_flx_entry(shapes_out, sid) != blob:
        errs.append(f"U8SHAPES slot {sid} is not the derived shape")
    elif num_frames(blob) != m['frames']:
        errs.append(f"U8SHAPES slot {sid} has {num_frames(blob)} frames, "
                    f"expected the donor's {m['frames']}")
    slot = 0x80 + sid * 8
    if (shapes_out[:slot] != shapes_in[:slot]
            or shapes_out[slot + 8:len(shapes_in)] != shapes_in[slot + 8:]):
        errs.append(f"U8SHAPES bytes outside slot {sid} changed")
    lo, hi = sid * ENTRY_SIZE, (sid + 1) * ENTRY_SIZE
    if tf_out[lo:hi] != tf_in[donor * ENTRY_SIZE:(donor + 1) * ENTRY_SIZE]:
        errs.append(f"TYPEFLAG row {sid} is not row {donor}")
    if tf_out[:lo] != tf_in[:lo] or tf_out[hi:] != tf_in[hi:]:
        errs.append(f"TYPEFLAG rows other than {sid} changed")
    if actor_anim(anim_out, sid) != actor_anim(anim_out, donor) \
            or actor_anim(anim_out, sid) is None:
        errs.append(f"ANIM.DAT entry {sid} does not animate as {donor}")
    a = 4 * sid
    if anim_out[:a] != anim_in[:a] or anim_out[a + 4:] != anim_in[a + 4:]:
        errs.append(f"ANIM.DAT bytes outside entry {sid} changed")
    return errs


def build_one(m, base_shapes):
    sid, donor = m['shape'], m['donor']
    donor_blob = read_flx_entry(base_shapes, donor)
    if not donor_blob or num_frames(donor_blob) != m['frames']:
        raise SystemExit(f"donor {donor} missing from the base or not "
                         f"{m['frames']} frames")
    shapes_in = open(OUT_SHAPES, 'rb').read()
    tf_in = open(OUT_TYPEFLAG, 'rb').read()
    anim_in = open(OUT_ANIM, 'rb').read()
    if 'art' in m:
        if ACTOR_ART[m['art']] != donor:
            raise SystemExit(f"{m['name']}: lv_actor_art derives "
                             f"'{m['art']}' from {ACTOR_ART[m['art']]}, "
                             f"not {donor}")
        frames = actor_frames(m['art'], base_shapes, anim_in)
        blob = encode_shape_blobs([encode_frame(f['pixels'], f['width'],
                                                f['height'], f['xoff'],
                                                f['yoff']) for f in frames])
    else:
        blob, _ = drawn_shape(m['frames_dir'], m['frames'])
    errs = validate_shape(blob)
    if errs:
        raise SystemExit(f"{m['name']} ({sid}) failed validation:\n  "
                         + "\n  ".join(errs[:20]))

    staged = {p: p + '.staging' for p in (OUT_SHAPES, OUT_TYPEFLAG, OUT_ANIM)}
    for p in staged.values():
        if os.path.exists(p):
            os.remove(p)

    inject_shape(blob, sid, OUT_SHAPES, staged[OUT_SHAPES])
    with open(staged[OUT_TYPEFLAG], 'wb') as f:
        f.write(tf_in)
    _old, row = patch_entry_in_file(staged[OUT_TYPEFLAG], sid, donor)
    with open(staged[OUT_ANIM], 'wb') as f:
        f.write(clone_anim_entry(anim_in, sid, donor))
    print(f"  {m['name']} {sid} <- {donor}: {num_frames(blob)} frames, "
          f"{len(blob)} bytes, validate_shape clean; TYPEFLAG {row.hex()}; "
          f"ANIM.DAT entry -> {anim_offset(anim_in, donor):#x}")

    errs = _verify(m, blob, shapes_in, open(staged[OUT_SHAPES], 'rb').read(),
                   tf_in, open(staged[OUT_TYPEFLAG], 'rb').read(),
                   anim_in, open(staged[OUT_ANIM], 'rb').read())
    if errs:
        for p, s in staged.items():
            if os.path.exists(s):
                os.replace(s, p + '.failed')
        raise SystemExit("staged outputs REJECTED (quarantined as .failed; "
                         "the previous artifacts are untouched):\n  "
                         + "\n  ".join(errs))
    for p, s in staged.items():
        os.replace(s, p)
    print(f"  verified and promoted: {sid} is {donor} in TYPEFLAG and "
          f"ANIM.DAT, its own art in U8SHAPES, nothing else moved")


def main():
    names = ', '.join(f"{m['name']} {m['shape']}" for m in ACTORS)
    print(f"=== LV actors: {names} ===")
    for path in (OUT_SHAPES, OUT_TYPEFLAG, OUT_ANIM):
        if not os.path.exists(path):
            raise SystemExit(f"{path} is missing — this step patches the "
                             f"artifacts earlier build_artifacts.sh steps "
                             f"produce; run tools/build_artifacts.sh")
    base_shapes = open(pristine_base(SHAPES_FLX, None, 'base U8SHAPES.FLX'),
                       'rb').read()
    for m in ACTORS:
        build_one(m, base_shapes)


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == 'ini':
        cmd_ini(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 1:
        main()
    else:
        raise SystemExit(__doc__)
