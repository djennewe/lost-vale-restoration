---
paths:
  - "agents/map-populator/src/build_map_*.py"
  - "agents/map-populator/src/lv_shapes.py"
  - "agents/usecode-compiler/src/u8c_symbols.py"
---

# Two shape-ID tables exist and they do not agree. Know which one binds.

## The map side is the source of truth

The per-map `SHAPE_*` constants in `agents/map-populator/src/build_map_XX.py`
are the single verified record of what shape IDs actually get placed in
`FIXED.DAT`. If you need to know what is in the world, read these.

## The `TYPE_SHAPES` table is something else

`TYPE_SHAPES` in `u8c_symbols.py` maps `TypeXXX` identifiers to shape IDs for
*compiled bytecode*. It is largely legacy, it is **not** guaranteed to match
the map-side IDs, and in several known cases it does not.

Before trusting or editing either table, read the audit note above
`TYPE_SHAPES` in `u8c_symbols.py`. Three things it establishes:

- **Most entries do nothing.** `get_type_shape()` is consulted only when a
  bare `TypeXXX` identifier is evaluated as a *value* in compiled source
  (`where (type = TypeCliffKey)`, `x.create(TypeShades, 0)`). Appearing in a
  `typeclass TypeX inherits ...` or `process TypeX::method()` declaration
  header does not go through this table.
- **But "unreferenced" is not the default.** A grep of every directory the
  build compiles found roughly three quarters of the entries genuinely live at
  the 2026-07-01 pass. Confirm with a grep before calling an entry dead.
- **Several live entries hold IDs proven wrong by rendering.** 158
  (`TypeBook` and friends) is a wooden stool. 338 (`TypeSword`…) is a green
  sparkle VFX. 400 (generic NPC) is a fire VFX sprite. 205 (`TypeChest`) is a
  wooden desk.

The authoritative placeholder inventory is
`agents/map-populator/docs/art-placeholder-audit-2026-07-19.md`.
`shared/docs/art-placeholder-audit.md` (2026-07-01) is superseded except for
its 1500-1700 new-shape ID allocation.

## Custom art IDs

Custom-art shape IDs start at **859**. 855 is unallocated; 856-858 are the
wood-plank walls; 859 is the Tiny Tar potion, 860 the Zealan gods (861 and
862 are retired, below), 863 the Sacred Rock, 864 the
Message Scroll, 865 the elemental pillars (four frames, class 865 behind
them) and 866 their receptacles (`docs/art-track.md` contract 5, landed
2026-09-24); 867 is the Tiny Tar body, the shrunken Avatar `TypeTinytar`
resolves to — the Avatar's own 1550 frames scaled to 0.6 plus a shrink ramp
at 60-69 and 1558 frames in all, on its own `ANIM.DAT` table (shape 1's), with
708's TYPEFLAG row and shape 1's weight/volume, built by `lv_tiny_avatar.py`
(slot 2026-10-08, art 2026-10-11, contract 8);
868 is Tyorvi's elixir, the blood vial 395 frame 5 recoloured
sea-green with class 868 behind it, which `TypeBottle` resolves to
(`docs/art-track.md` contract 11, 2026-10-09). 869 is the special root
(`TypeWeedz`, frame 0, class 869) and 871 the Passage Test
plant (`TypeShortmushroom`, class 871), both 2026-10-11 (contracts 12 and
13); 872 and 873 are the Water
Zombie and the Harpie, actors built by `lv_monsters.py` (step 6) on their
donors' TYPEFLAG rows and `ANIM.DAT` tables (the ghoul 142's frames
recoloured to the 1994 zombie of screen02/09 with its three shot poses in,
2026-10-25; 86 frames drawn new in the torax 120's layout), with classes
872/873, hatched by the Lake's and the harpie zone's eggs (contract 9,
2026-10-11). 874-879 are the 1994 art cut from the published screenshots
(cloud floor, white column, gold brick, marble walkway, Shield halves, the
altar Shield), `indexed` rows in `lv_art_props.py` that copy the PNGs'
palette indices verbatim (2026-10-16); since 2026-10-17 Map 17 places them
and the quest Shield halves are 878 (`TypeAOFrizbee`), where 870 was. 870
is now 878's **legacy alias** (`lv_shapes.SHAPE_SHIELD_HALVES_LEGACY`,
below).
880 is the gem pillar's cap, retail 596's frames on a fixed row (a
`copy` row: 596 is `TypeTalisman`). 881 is the striped prop on Felicitar's
plinth in screen04 (registry 2014, single-shot, an `indexed` row on donor
443; 2026-10-17). 882-886 are phase D's screen12/13 pieces (2026-10-25,
`indexed` rows): 882 the throne-nook dais, 883 the walkway's east end, 884
the gold/cloud edge tiles, 885 the side throne, 886 screen13's cut floor
tiles; 865 frame 2 became the 1994 Pillar of Fire the same day (frames 0,
1 and 3 its column redrawn per element on 2026-10-30). Static props use
rows in `lv_art_props.py` (`docs/art-track.md` keeps the table); current
allocations continue at 929. This
supersedes the older audit's 1500-1700 allocation for anything
`tools/png2shape.py` injects.

**888-890 are the 1994 actors** (2026-10-25, `lv_actor_art.py`): actor
clones built in step 6 by `lv_monsters.py` (its `NPCS` rows) on their
donors' TYPEFLAG rows and `ANIM.DAT` tables, no `u8monsters.ini` row and no
class. 888 is the Zealan elder (Mythran 190's 350 frames restyled), Atli's
body (npc 107); 889 and 890 the dark-haired and blond spear children (the
child 708's 100 frames at 0.8), npc 104's and npc 111's bodies. Each holds
its screenshot pose verbatim at the frame the shot shows.

**891-892 are phase E's screen07 pieces** (2026-10-30, `patch` rows in
`lv_art_props.py`, `tools/art/screen07_cuts.py`): 891 the cave walls on
donor 26, 892 the floor round the Pillar of Fire on donor 301, each frame
a retail piece's own frame with the shot's pixels it owns laid over it at
build time; `build_map_11.screen07_faces` swaps the pieces. 893 was left
to phase E's actor slice.

**894-895 are decorative cave backdrops** (2 November 2026,
`lv_art_props.py` copy rows). They copy retail 334's 29 frames and 564's
seven frames onto donor 202's FIXED|DRAW row, with matching flat footpads
and no SOLID, LAND, ROOF, or OCCL flags. Map 8 places them beneath hidden
ceilings and replacement floor plates to repaint their screen area in
low-resolution play. They supply
no walking surface or collision. Slot 893 remains reserved for the actor
slice above. 896 is decorative navy water (347 frame 16) on donor 202, with a
(4,4,0) footpad. Existing dry floors supply support; it has no SEA flag.
897 is the sanctum's decorative 566 clone on donor 202 with 566's
(6,1,6) box. Its anchor shifts 32 pixels up in the frame coordinates;
Map 18 places its sort box 320 units northwest and 48 units lower,
which preserves the original screen projection. Invisible strips retain
the original collision. Both are static copy rows with no class or
animation entry. The next unused shape is 929.

Shape 895 also carries clipped variants of frame zero and black frame two
from frame seven onward.
Binary opacity masks in `shared/data/lv-1994-art/vq2-clips/` remove pixels
at Map 11's protected-window and ground boundaries. Frames zero through
six, all anchors, and donor-202 physics retain their original values.

**Retired IDs: 861, 862** (2026-10-17, `lv_shapes.RETIRED_SHAPE_IDS`).
861 was the Magnetic Obelisk and 862 the cloud floor tile (contracts 1 and
2); the 1994 screenshot art replaced them (screen11's obelisk is retail
pieces on 875 drums, the floor is 874). No build step injects them, so
their `U8SHAPES.FLX` and `TYPEFLAG.DAT` slots stay the base game's (empty,
filler row); no map places them, no class or `TYPE_SHAPES` entry names
them, and `test_art_props.py` section 14 asserts all of it. **Never reuse a
retired ID** and never renumber around one: playtest records, old saves and
the docs still name them, and must not find a different shape there. The
next new shape takes the next unused number, not a retired one.

**870 is not retired: it is a legacy alias of 878.** It was the Shield
halves cut from retail 828 (contract 10, 2026-10-11) until 878 replaced
it, and the halves are carryable, so a 2026-10-11..10-17 save can hold
them as 870 in the Avatar's pack. With the slot empty, opening the pack
aborts ScummVM (`ContainerGump::run`, `Assertion 'sh'`; verify3 claim 2).
So a `copy` row in `lv_art_props.py` builds 870 from 878's frames on 878's
own TYPEFLAG row: an old half looks and behaves as the 1994 half. No map
places 870 and no `TYPE_SHAPES` entry resolves to it; SHADES and REAPPLY
accept it by literal. Section 14 asserts the copy.

**Which retired shapes can a save hold?** A save holds every object of the
map the player stood on (`ObjectManager::save`, fixed items included,
restored by `EXT_INCURMAP`) and only the non-fixed items of the others
(`Map::save` writes `_dynamicItems`). So a carryable shape follows the
player anywhere, which is why 870 needed the alias, while a fixed one is in
a save only if it was saved on its map: 861/862, both `SI_FIXED` scenery
with no class, sit invisible in a Map 17 save made 2026-09-15..10-17 until
the player leaves (an item with no shape draws nothing: the sorter skips
it), and the next entry reloads `FIXED.DAT`. Retire a carryable shape only
as an alias.

A row's TYPEFLAG donor decides more than its collision box. 864 takes donor
159, the engine's scroll, so the Message Scroll is carryable (no `SI_FIXED`)
and `SF_QUALITY`, the one family `Item::I_getQuality` answers for
(`item.cpp:2841`). 868 takes donor 180, the engine's bottle, for the
opposite reason: the vial it is drawn from (395) is `SF_REAGENT`, which
`Item::canMergeWith` stacks with any vial of blood (frames 0-5), and 180's
`SF_GENERIC` row stacks with nothing. Pick the donor for the behaviour, then
size the footpad.

A footpad's z can be load-bearing beyond the art. The engine tries `climb72`
down to `climb16` on jump, so a solid standing 48 units or taller **within
reach of a 120-tall barrier** hands the player a chained climb over it.
Distance is what decides it. Map 11's pillars stand 80 tall (footpad z=10)
since 2026-09-24 and that is safe because they are 1023 units from the gate
line; `gate_reach()` in `test_route_reach.py` asserts the real condition (no
reachable exposed top of 48 or more within two tiles of a gate line), so a
tall standable placed near a wall fails the estate.

Injecting a shape by hand is not enough to keep it. `tools/build_artifacts.sh`
rebuilds `U8SHAPES.FLX` from the base game every time, so custom art survives
only if a build step like `lv_wood_wall.py` or `lv_tiny_tar.py` injects it.
An injection made outside a build step is silently dropped on the next
rebuild.

## Don't quote counts you haven't recomputed

The audit note carries a correction (L7) for exactly this: it once said "102
entries" and named a dead entry that was never in the table. It held 103
then and 109 after the 2026-10-07 retail audit (which also corrected 41
values, each with its retail citation). Re-derive before citing a number.


**898-904 are shared dressing copies** (Phase 4 shared slice 0.1).
898 (`SHAPE_COURT_COBBLE_FLAT`) copies all 23 retail 70 frames onto donor
71's exact (4,4,0) row. 899 copies 524's six rubble frames onto donor 465
with (3,3,1); 900 and 901 copy the two frames of 235 and 237 onto donor 465
with (3,4,1) and (4,3,1). Those three rows keep their original sort heights
and have FIXED set, with LAND and SOLID clear. The hall and bone kits expose
the decorative IDs.
902 (`SHAPE_CAVE_CREST_DECORATIVE`) copies retail 125 onto donor 202 with
(4,4,0). Seven paint variants per source frame retain its canvas and anchor:
full, upper eight, 16, 24, or 32 pixel rows, left half, and right half.
`Site.cave_crest` chooses the largest variant that clears protected shot
pixels and adds no quest-band walking or standing pose occlusion. Frame number in its input
is the retail frame; output frame is source * seven + crop index.
903 and 904 are the moat's grass caps (94's 11 frames, donor 465,
(4,4,1)) and rooted faces (85's seven frames, donor 465, (1,4,4)).
Their paint supplies no standing surface. `Site.moat_bank` requires retained
grass at z 48 and keeps all paint boxes outside the channel strip.
All seven are static copy rows with no class or animation entry.
D8's conditional cloud-rim lobes take **929**, if requested.


**905-928 are shared slice 0.2 decorative rows** (10 November 2026).
905-915 take donor 465, with FIXED set and LAND and SOLID clear. 905 is the
white column 875 frame zero turned horizontally into a fallen drum on a
(3,2,1) sort box. 906 copies all four root frames of 57 on (6,5,2);
907 copies all 26 fungus frames of 65 on (2,2,5); 908 copies all 12 spire
frames of 66 on (4,4,5). 909 copies urn 229 on (1,1,2), and 910 copies
all nine rubble 526 frames on (2,2,2). 911 copies all 30 basalt 122 frames
on (4,4,1). 912 and 913 copy the 10 frames each of 246 and 252 on
(1,4,5) and (4,1,5). 914 copies 26's 15 face frames, clipping paint to the
bottom eight-unit riser while retaining the original canvas and anchor,
on (4,1,1). 915 copies shape 15's 10 wall silhouettes and anchors, filling
opaque pixels with retail 125 frame 12 stone, on (4,1,5). The retained
shape-15 record supplies collision; its decorative skin supplies paint.
No row adds a class or animation entry. Existing 899 frames remain frozen;
910 frames six through eight extend its decorative rubble kit. The next
unused shape, including the conditional D8 cloud lobes, is **929**.

916 through 928 are shifted decorative star paint on donor 202 and
(4,4,0), without LAND or SOLID. They copy all nine retail 351 frames in
337 anchor layouts, with at most 28 layouts per shape because each FIXED
frame is a byte. All copies stay at z zero in engine-visible ground chunks.
The layouts compensate projection and C-division rounding across coordinate
zero. Sprite palette indices remain unchanged. These rows are backdrop in
dressing metrics and painted star coverage for cloud frame-black checks.
They have no class or animation entry. The next free shape is 929.
