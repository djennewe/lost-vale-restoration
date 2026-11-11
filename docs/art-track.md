# The art track

The queue and the contracts for replacing base-game placeholder art with
custom shapes, as `docs/reviews/2026-09-14-map-cleanup-plan.md` §5 lays it
out: each replacement lands whenever it is ready, the map cleanup has built
each item's *setting*, and **each item gets a written contract here before
its art is made**. The contract says what the thing is to the engine, so the
art is made to fit the integration and not the other way round.

Started 2026-09-15 with the Magnetic Obelisk. The pipeline is
`tools/png2shape.py` (one PNG → injected, TYPEFLAG-patched shape) and the
build steps that keep an injection alive across `tools/build_artifacts.sh`
(`.claude/rules/shape-ids.md`: an injection made outside a build step is
dropped on the next rebuild). Shape 860, the gods, is the worked example for
anything animated; shape 863, the Sacred Rock, is the worked example for a
static prop (861, the obelisk, was the first, and is retired).

## Custom shape IDs

| ID | What | Build step | Placed by |
|---|---|---|---|
| 856–858 | wood-plank walls | `lv_wood_wall.py` (2/8) | Maps 10, 11 |
| 859 | Tiny Tar potion, frame 8 | `lv_tiny_tar.py` (3/8) | Map 10 |
| 860 | the three Zealan gods, 42 frames: 0-2 sealed in amber, the 1994 pixels (screen04, registry 2010-2012, single-shot; Felicitar 42 inferred px), 3-41 redrawn at the 1994 scale and palette by `lv_god_frames.py` (2026-10-17); footpad (2,2,7) | `lv_god_statues.py` (4/8) | Map 18 |
| 861 | **RETIRED 2026-10-17** — was the Magnetic Obelisk (contract 1). Replaced by screen11's 1994 obelisk, retail pieces (12 f14-f17, cap 545, skull 814) on four 875 drums. No longer built; slot stays base; never reused | — | nothing |
| 862 | **RETIRED 2026-10-17** — was the cloud floor tile (contract 2). Replaced by **874**, the 1994 cloud floor, on Maps 13 and 17. No longer built; slot stays base; never reused | — | nothing |
| 863 | the Sacred Rock | `lv_art_props.py` (5/8) | Map 10 |
| 864 | the Message Scroll | `lv_art_props.py` (5/8) | Map 17 |
| 865 | the elemental pillars, 4 frames, class 865 behind them | `lv_art_props.py` (5/8) | Map 11 |
| 866 | the pillar receptacles | `lv_art_props.py` (5/8) | Map 11 |
| 867 | the Tiny Tar body (an actor): shape 1's 1550 frames at 0.6 with the glow shrink ramp at 60-69 (1558 frames), its own `ANIM.DAT` table (shape 1's), 708's TYPEFLAG row with shape 1's weight/volume (contract 8) | `lv_tiny_avatar.py` (6/8) | never placed; `setType(TypeTinytar)` |
| 868 | Tyorvi's elixir: the blood vial 395 frame 5 recoloured sea-green, class 868 behind it | `lv_art_props.py` (5/8), the first recolour row | never placed; EZREKAL creates it (`TypeBottle`) |
| 869 | the special root, 1 frame (candidate C), class 869 `lv-new/SPROOT.UNK` behind it | `lv_art_props.py` (5/8) | Map 10 |
| 870 | **LEGACY ALIAS of 878 since 2026-10-17** — was the Shield halves, retail 828 split at build time (contract 10), replaced by **878**, the 1994 halves (`TypeAOFrizbee` 870 → 878). Retired that day, then restored as a verbatim copy of 878's frames and TYPEFLAG row (a `copy` row, donor 878), because a 2026-10-11..17 save can hold 870 halves in the pack and an empty slot aborts the engine when the pack opens (verify3 claim 2) | `lv_art_props.py` (5/8), a `copy` row of 878 | nothing (old saves only; SHADES and REAPPLY accept it by literal) |
| 871 | the Passage Test plant, 1 frame (candidate A), class 871 `lv-new/TESTPLNT.UNK` behind it | `lv_art_props.py` (5/8) | Map 10; PLNTST creates five more |
| 872 | the Water Zombie (an actor): ghoul 142's 451 frames through `lv_actor_art.ZOMBIE_REMAP` (the 1994 zombie's teal skin, green kilt and slime, 2026-10-25; candidate A's blue-grey `WATER_ZOMBIE_REMAP` until then) with screen02's and screen09's poses at frames 40, 81 and 112, 142's TYPEFLAG row and `ANIM.DAT` table, the ghoul's `u8monsters.ini` row (written by `install_lv.sh`); class 872 `look()` barks "water zombie" (contract 9, **landed 2026-10-11**) | `lv_monsters.py` (6/8) | Map 10, five lake eggs |
| 873 | the Harpie (an actor): drawn new in torax 120's 240-frame layout (the 86 frames its `ANIM.DAT` entry uses, candidate A), 120's TYPEFLAG row and `ANIM.DAT` table, the torax's `u8monsters.ini` row (written by `install_lv.sh`); class 873 `look()` barks "harpie" (contract 9, **landed 2026-10-11**) | `lv_monsters.py` (6/8) | Map 13, four harpie-zone eggs |
| 874 | the 1994 cloud floor, 5 flat frames (3/4 = 0/2 mirrored), cut from screen11, cross-shot-validated; retail 163's row (301's with `SI_DRAW` swapped for `SI_OCCL`) (2026-10-16, `docs/research/2026-10-16-screenshot-reconstruction/phaseC-art.md`) | `lv_art_props.py` (5/8), the first `indexed` row | Map 17 (2026-10-17, phase C: the whole city's floor) |
| 875 | the 1994 white column, frame 0 plain, frame 1 orange-banded; donor 443, (1,1,5) | `lv_art_props.py` (5/8), `indexed` | Map 17: gem pillars, plaza ring, obelisk drums, walkway colonnades |
| 876 | the 1994 gold brick floor, 2 flat frames (single-shot); 163's row like the cloud | `lv_art_props.py` (5/8), `indexed` | Map 17: streets, courts, the arrival landing |
| 877 | the 1994 marble walkway slab with its trim, 1 frame (single-shot, 19 inferred px); donor 113, (4,4,1) | `lv_art_props.py` (5/8), `indexed` | Map 17: the walkway strips, the scroll plinth |
| 878 | the 1994 Shield halves, frame 0 sun, frame 1 eye; donor 828 whole | `lv_art_props.py` (5/8), `indexed` | Map 17: the quest halves since 2026-10-17 (`TypeAOFrizbee` 870 → 878; q81 by the obelisk in screen11, q82 in screen12's throne nook, npcnum 236) |
| 879 | the 1994 Sacred Shield (828's disc with the 1994 emblems); donor 828 whole | `lv_art_props.py` (5/8), `indexed` | never placed: since 2026-10-17 it is the restored Shield of the Ancients (`TypeSacredShield`, class 879), which SHADES creates and AOSCENE pops onto the altar at screen04's spot |
| 880 | the gem pillar's cap: retail 596's 8 frames copied verbatim at build time onto donor 443 (SI_FIXED) with 596's (1,1,1). 596 is `TypeTalisman`, carryable, frames 0-3 the Map 11 talismans, so screen11's gems cannot be 596 in the map (2026-10-17) | `lv_art_props.py` (5/8), the first `copy` row | Map 17: every gem pillar (the vignettes keep 596; `build_map_17` stamps them with `art_map` {596: 880}) |
| 881 | the striped prop on Felicitar's plinth in screen04 (registry 2014, **single-shot**, unidentified); donor 443, (1,1,1) (2026-10-17) | `lv_art_props.py` (5/8), `indexed` | Map 18: Felicitar's plinth |
| 882 | screen12's throne-nook dais: 877's marble run along y, lit two steps lighter (registry 2006, 3 single-use frames, visible px index for index, hidden px the mirrored 877 texture); donor 113, (4,4,1) (2026-10-25, phase D) | `lv_art_props.py` (5/8), `indexed` | Map 17: screen12's nook (vignette) |
| 883 | the walkway strips' east end: 877 cut on the screen vertical through its front corner (registry 2007); donor 113, (4,4,1) (2026-10-25) | `lv_art_props.py` (5/8), `indexed` | Map 17: strips A and B end at x 4095 |
| 884 | gold brick meeting the cloud (registry 2008): f0/f1 lobed cloud over gold (screen12, 5 instances), f2 the gold corner (screen12 + screen13, cross-shot); 163's row (2026-10-25) | `lv_art_props.py` (5/8), `indexed` | Map 17: screen12's forecourt edge; Map 13: screen13's street corner |
| 885 | screen12's left throne, side on (registry 2009, single-shot, 27 drawn px); donor 223, (1,2,5) (2026-10-25) | `lv_art_props.py` (5/8), `indexed` | Map 17: screen12's nook |
| 886 | screen13's floor tiles, each cut to the pixels the shot shows it owning, earth transparent, lobed rims (registry 2015, 35 single-use frames); 163's row (2026-10-25). Since 2026-10-30 (cloud13) the tiles float 96 over the earth, so the pixels the tree crown and the spires used to cover are the tiles' own (frames 3, 12, 16, 17), branch tips past a rim are transparent, and frame 3's cap beyond the window is drawn (180 `inferred_px`) | `lv_art_props.py` (5/8), `indexed` | Map 13: screen13 (vignette, `ART_STANDIN` 2015 → 886, `FLOATING` at z 216) |
| 887 | historical unbuilt slot; current allocations continue at 898 | no build row | none |
| 888 | the Zealan elder of screen19/20 (an actor): Mythran 190's 350 frames restyled (robe browns, long white hair), the staff cut back to screen20's short cane in every frame (nothing above the hand, no knob; 2026-10-30), the shot poses at 60 (stand SE) and 71 (screen19, plus its cane where the shot's Avatar hides it), 70/72 the SE talk gesture (forearm turned; 2026-10-30), Mythran's blank table frames drawn; 190's TYPEFLAG row and `ANIM.DAT` table, no ini row, no class (2026-10-25, `docs/research/2026-10-16-screenshot-reconstruction/phaseD/actors/REPORT.md`; `phaseE/actorfix/REPORT.md`) | `lv_monsters.py` (6/8) via `lv_actor_art.py` | Map 10: Atli's body (npc 107) |
| 889 | screen20's dark-haired spear child (an actor): the child 708's 100 frames at 0.8 with grey tunic, black cloak, no black outline (2026-10-30) and a spear held in the right hand (grip at the hand per frame, the shot's angle per facing; 2026-10-30), the shot pose at frame 1 (shown mirrored, W); 708's row and table (2026-10-25) | `lv_monsters.py` (6/8) via `lv_actor_art.py` | Map 10: npc 104's body |
| 890 | screen20's blond spear child: as 889, blond hair (2026-10-25) | `lv_monsters.py` (6/8) via `lv_actor_art.py` | Map 10: npc 111's body |
| 891 | screen07's cave walls (26 family): each piece of the window with the 1994 pixels the shot shows it owning (the spears, the right cliff's course seam, the back wall's pointed east end) over its retail 26 frame (registry 2043, 8 single-use frames, a `patch` row composed at build time, so no Origin pixel is committed); donor 26, (4,1,6) (2026-10-30, phase E, `tools/art/screen07_cuts.py`) | `lv_art_props.py` (5/8), the first `patch` row | Map 11: screen07's cliffs (`build_map_11.screen07_faces` swaps each retail piece for its frame) |
| 892 | screen07's floor round the Pillar of Fire: each 301 tile with the lava pit's glow and lip the shot shows on it (registry 2027, 17 single-use frames, `patch`); donor 301, (4,4,0) (2026-10-30) | `lv_art_props.py` (5/8), `patch` | Map 11: screen07's floor |
| 894 | retail 334 decorative cave backdrop, 29 frames, donor 202, (4,4,0) | `lv_art_props.py` (5/8), `copy` | Maps 8, 11, 18, 39 |
| 895 | retail 564 decorative cave backdrop, seven original frames and 84 clipped frames, donor 202, (8,8,0) | `lv_art_props.py` (5/8), `copy` | Maps 8, 11, 18, 39 |
| 896 | navy decorative water, retail 347 frame 16, donor 202, (4,4,0); no SEA, LAND, or SOLID | `lv_art_props.py` (5/8), `copy_frames` | Map 11, existing dry support beneath bounded pools |
| 897 | decorative sanctum rock, all 15 retail 566 frames and (6,1,6) box, donor 202; anchor y offset reduced by 32 | `lv_art_props.py` (5/8), `copy_shifts` | Map 18 west passage, projected over separate invisible collision |

The next unused shape is 929. Shapes 896 and 897 have no usecode class
or animation entry. Both use donor 202's FIXED and DRAW flags, with no
collision, support, roof, sea, or occlusion flags. Shape 897's sort box
moves from (2943,7551,48) to (2623,7231,0); the anchor shift preserves its
painted projection. Two 497 strips preserve the original collision union.
Three inaccessible island caps become 763 editor plates at their existing
coordinates and levels. Screen04 must retain every pixel.

Since 2026-10-25 **865 frame 2** (the Fire pillar) is the 1994 Pillar of Fire, registry 2023 (screen07, single-shot; the lower shaft drawn behind the candle post): a dict `{'indexed': ...}` entry inside the 865 `frames` row. Since 2026-10-30 (phase E, Douglas's card 4) **frames 0, 1 and 3** are its column redrawn for Earth, Air and Water (registry 2024-2026, grade `derived`, `tools/art/pillar_1994_style.py`): 2023's canvas and hotspot, the red gem, flames and lava recoloured onto an ochre, pale-grey or blue ramp, the shaft's hidden lower-left drawn from the rows above. The AI-drawn columns of 2026-09-24 (sheets C2/C3 below) no longer feed the build. The same day 2023 took the shot's left flame and lava where the phase-D cut stopped short (41 px) and its 88 index-9 greys became 28 (the same colour, outside the cycling range).

Static props share one table-driven step, `agents/map-populator/src/lv_art_props.py`,
so a new prop is a row there plus its art, and the build's step count does
not grow per prop. Anything that needs its own TYPEFLAG anim entry, its
own usecode class (the gods) or an `ANIM.DAT` entry (the Tiny Tar body)
keeps its own step.

## The three integration contracts (from plan §5)

- **Static prop.** A shape injected by a build step; TYPEFLAG copied from a
  donor with the right flags and the footpad set to the art; the map-side
  constant swapped; the `map_pins.json` row (if the item has one) re-derived;
  a `TYPE_SHAPES` re-point *only if* a compiled `foreach … type =` names a
  type that resolves to the old shape. Nothing else. No usecode class exists
  at the new number, so double-clicking prints nothing — that is what
  "nothing else" buys, and it beats the placeholder's wrong name.
- **Interactive object.** The engine dispatches `look()`/`use()`/`gotHit()`
  from the class whose number equals the shape (`item.cpp:1516`). A new
  shape for one of these needs its class compiled at the new number, and
  class numbers are pinned in `lv_manifest.json`. A manifest decision plus a
  compile, before any art.
- **Interactive by `npcnum`.** The LV hunk in `Item::callUsecodeEvent`
  replaces `class_id` with `npcNum + 1024` for every event on any non-egg
  item carrying a nonzero `npcNum` whose target class is non-empty, so the
  shape number carries no usecode
  meaning at all: the class is pinned to the npcnum, a class at the shape
  would never run, and the art is a static-prop swap with nothing else to
  decide. Map 11's pillar receptacles are the case (contract 5). Check for
  this before classifying an item as interactive.
- **Actor.** `AnimationTracker::init` looks the animation up by shape and
  refuses to move an actor with none. A new actor shape needs animation
  data bound to it; the usecode-driven frame cycling of shape 860 is not
  that. The binding exists since 2026-10-08: `STATIC/ANIM.DAT` is the fifth
  built artifact, and `lv_tiny_avatar.clone_anim_entry` points a new
  shape's entry at a donor's action table (2048 uint32 offsets, one per
  shape; the loader reads each shape's table independently, so sharing is
  safe). Art that keeps the donor's frame layout needs nothing more from
  the data files; art with a different layout must append its own action
  table instead, as 867 does since 2026-10-11
  (`lv_tiny_avatar_art.avatar_anim_table`, contract 8).
  One thing a clone does NOT carry: the engine's `u8monsters.ini` is keyed
  by shape (`type_flags.cpp:436`), so a cloned MONSTER loses its HP, dex,
  damage, armour and treasure row. Harmless for the Avatar (867: `MainActor`
  overrides armour, defense and damage amount, and the child's damage type
  is the engine default, `DMG_NORMAL`); a real cost for item 9.

## Queue

| # | Item | Kind | Where | Today | State |
|---|---|---|---|---|---|
| 1 | Magnetic Obelisk | static | Map 17 main plaza | **retail composite (screen11)**; 861 retired | **landed 2026-09-15** as custom 861, verified in ScummVM (`docs/playtest-2026-09-15-obelisk.md`); **retired 2026-10-17**: the 1994 obelisk is retail pieces on 875 drums, and 861 is no longer built; contract below |
| 2 | Cloud tiles | static, terrain | Map 17 cloud islands | **874, the 1994 cloud**; 862 retired | **landed 2026-09-15** as custom 862; **retired 2026-10-17**: 874, cut from screen11, floors Maps 13 and 17, and 862 is no longer built; contract 2 below |
| 3 | Sacred Rock | static | Map 10 Sacred Circle centre, q100 | **863, custom** | **landed 2026-09-20**, verified in ScummVM; contract 3 below. The queue used to rate this low on "a rock already reads as a rock"; the before plate says otherwise, and there is no 1994 original |
| 4 | Message scroll | carryable prop | Map 17 scroll chamber, q80 | **864, custom** | **landed 2026-09-21**, verified in ScummVM (`docs/playtest-2026-09-21-message-scroll.md`); contract 4 below. Carryable on donor 159, and class 864 reads Odion's letter |
| 5 | Elemental pillars and receptacles | static, and one live re-point | Map 11, q201–204 | **865 and 866, custom** | **landed 2026-09-24**, verified in ScummVM (`docs/playtest-2026-09-24-elemental-pillars.md`: the engine binds class 865 to the shape, a receptacle dispatches `use()` off npcnum 120 on shape 866, and the re-pointed search destroyed the Earth pillar with a real talisman); contract 5 below. The receptacle `look()` (decision 2) and the paper-types fix landed 2026-09-25 on a third EUSECODE move (`f9a9aba`) |
| 6 | Gold plaques | interactive, no new art | Map 17 plazas | **retail 614, npcnum 235** | **landed 2026-09-25** (`f9a9aba`, read fixed in `1b0bf9a`), verified in ScummVM (`docs/playtest-2026-09-25-ceremony-plaques.md` P5-P7): three plaques reading new qualities 68-70 of `lv-patched/PLAQUENS.UNK`, text approved 2026-09-25; contract 6 below |
| 7 | Wired obelisk | closed | Map 17 | **was 861; the retail composite since 2026-10-17** | **closed 2026-09-22 with no art and no class** (contract 7 below): `MAGNET.UNK` is an egg class that names the obelisk only as a `pop()` coordinate, so the row's condition resolves to "nothing" whether or not MAGNET is wired. The wiring itself is a quest task, `TODO.md` EGGMAGNET 281 |
| 8 | Tiny Tar Avatar | actor | Map 18 | **867, the Avatar scaled down** | **landed 2026-10-11, in-engine verification outstanding** (contract 8 below). Slot allocated 2026-10-08 (Douglas): `TypeTinytar` → 867, at first a copy of the child actor 708's frames, TYPEFLAG row (footpad (1,1,4)) and `ANIM.DAT` entry, with shape 1's weight 1 / volume 250 so the pack no longer read 520/200 while shrunk. 2026-10-11 (Douglas): the Avatar's own sprites scaled by code, on the Avatar's animation table; picked O60, the glow ramp, a scaled stride. (This row used to say a sprite in 708's layout could replace the frames without touching anim data; it could not: 708's frames 60-69 are its death frames, contract 8 finding 2.) |
| 9 | Water Zombie, Harpie | actor | Map 10 lake (5 eggs), Map 13 harpie zone (4 eggs) | **872 and 873, custom** | **landed 2026-10-11, in-engine verification outstanding** (contract 9 below). Douglas picked zombie A (drowned, blue-grey) and harpie A (classic). 872 is the ghoul's 451 frames recoloured; 873 is 86 frames drawn new in the torax's layout from 12 generated sheets; each takes its donor's TYPEFLAG row and `ANIM.DAT` table (`lv_monsters.py`, step 6/8), a `u8monsters.ini` row (`install_lv.sh`) and a `look()` class (`lv-new/WZOMBIE.UNK`, `HARPIE.UNK`) |
| 10 | Shield halves as halves | quest item | Map 17 | **878, the 1994 halves**; 870 a legacy alias of 878 | **landed 2026-10-11** as custom 870 (Douglas picked B): retail 828, the restored Shield, split at build time on its divider bar along a zigzag, frames 0/1 on 828's non-equip TYPEFLAG row; `TypeAOFrizbee` 539 → 870; contract 10 below. **Replaced 2026-10-17**: the quest halves are 878 (`TypeAOFrizbee` 870 → 878), and 870 is built as a copy of 878 so old saves' halves still draw |
| 11 | Tyorvi's elixir | carryable quest item, created at runtime | EZREKAL hands it over, TYORVI drinks it | **868, custom** | **landed 2026-10-09** (Douglas): its own one-frame vial on donor 180, class 868 `lv-new/ELIXIR.UNK` barking "Tyorvi's elixir", `TypeBottle` re-pointed 395 → 868 at frame 0; contract 11 below. It was 395 frame 5, the Blood reagent |
| 12 | Special root | carryable quest item | Map 10, by the Sacred Circle's east stone | **869, custom** | **landed 2026-10-11** (Douglas picked C): a pale root with violet leaves on donor 180, class 869 barks "special root", `TypeWeedz` 399 → 869 with Ezrekal's two filters 9 → 0 (EZREKAL R2); contract 12 below. In-engine check pending |
| 13 | Passage Test plant | static, created at runtime too | Map 10 test grounds, q10 | **871, custom** | **landed 2026-10-11** (Douglas picked A): the spined yellow-green bulb on donor 65, class 871 barks "Strange plant", `TypeShortmushroom` and `TypePoisonPlant` 126 → 871; contract 13 below. In-engine check pending |

---

## Contract 1 — the Magnetic Obelisk (shape 861, retired 2026-10-17)

**What it is.** Cloud City's centrepiece, the MAGNET puzzle's landmark: the
Avatar's magic items are pulled to it. In the 1994 Cloud City screenshot
(`shared/data/lv-screenshots/screen11.gif`, cropped to
`shared/docs/art-poc/obelisk/reference-screen11*.png`) it is a tall dark
slate-blue monolith, a smooth domed cap, two columns of green glyphs down
each visible face, a flared foot with a small green-eyed face at its
centre, standing on a cluster of the city's banded white drums with a
sword, a shield and a bow stuck to its foot. This is the only placeholder
on the list with a photograph of the real thing, so the art is a redraw of
it, generated with that crop as the reference the way the wake poses were
generated from each god's own sprite.

**What is generated.** The obelisk alone. The drums are the plaza's own
columns (screen12 shows the same white-and-gold cylinders lining the
plaza), and its setting is the two-tier dais `build_map_17.py` already
stands it on; the weapons are MAGNET's job when it is wired.

**Engine identity.**

| | |
|---|---|
| Shape | **861** (860 is the gods; 855 unallocated; `.claude/rules/shape-ids.md`) |
| Frames | 1 |
| TYPEFLAG donor | 443 `statue` — `SI_FIXED \| SI_SOLID`, `SF_GENERIC`, the flags the gods copy. Not 721: it carries `SI_NOISY`. |
| Footpad | **(4,4,12)** — one 128-unit dais tile, 96 tall: the box is the tile it stands on. A's 58×127 sprite sits inside the 64×128 screen box that projects to (`suggest_footpad` says (3,4,12); the symmetric box wins because it is the tile). Not the donor's (3,3,3). |
| Anchor | bottom-centre (`xoff=w/2, yoff=h`), the prop convention |
| Anim | none (`animType 0`) |
| Usecode class 861 | **none.** EUSECODE entry 863 is empty; a double-click prints nothing. The chimney printed "chimney". |
| `TYPE_SHAPES` | **no re-point.** `TypeStatue` → 721 exists in the table but no compiled file in `lv-patched/` or `lv-new/` names it; every `foreach` in `MAGNET.UNK` filters an inventory type (`TypePotion`, `TypeKey`, the magic armour set). Verified 2026-09-15. |

**Placement.** `build_map_17.py` main plaza, on the top tier of the dais at
z = 16, quality `QUALITY_OBELISK` (90) kept, max corner **(4095, 7167)** —
the top tier's centre tile itself, one unit off the chimney's (4096, 7168),
which sat a unit past the floor grid. With bottom-centre anchoring the
sprite's foot is the box's near vertex, so the builder shifts a box smaller
than the tile by (128 − 32·fx)/2 on each axis to keep it centred; for the
(4,4) box the shift is zero. The `map_pins.json` row is "free to move" and
records the new position.

**Pins.** `derive_map_pins.py` `DECORATIVE` row for map 17 changes from
shape 721 to 861 (it locates the row by (map, shape, quality)); re-derive
after the FIXED build. `test_map_hygiene.py` counts 721 not in the pins as
a placeholder — Map 17 goes to zero 721s, so its row stays 0.

**Build.** New step 5/7, `lv_art_props.py`, between the gods and EUSECODE;
the step labels, CLAUDE.md's "six steps", and `.claude/rules/build-artifacts.md`
follow. `inject_shape` refuses an occupied slot, so a stale 861 fails loud.

**Verification.** A `Box::overlaps` assertion that the obelisk's box lies
within the dais top tier and overlaps neither tier-one candelabrum
(`test_route_reach` is FIXED-only and `map_walkability` has no Map 17 run,
so nothing else sees a footpad change); route 17 still green; then the
plaza in-engine at 640×400 with a column beside it for scale, walked up
to and around. Report: `docs/playtest-2026-09-15-obelisk.md`.

**Height.** **128 px**, a decision made against a real plaza shot
(`shared/docs/art-poc/obelisk/compare-ABC-1x.png`): the plaza columns
(8 + 40 + 40 world-z) top out near 90 px, the 1994 sprite was about 98 px
on 30 px of drums, and ours stands on a 16-unit dais, so 128 puts its top
where the original's was and a little above — overtopping the columns by
about half again. The god heights (110–124) are figures, not a landmark.

### Record (filled as the work lands)

- 2026-09-15 — contract written; three candidates generated through `agy`
  with `tools/art/gen_obelisk.sh` (A faithful, B heavier foot, C plain
  stone with only the glyphs coloured). C shipped first on the engine-side
  read (foot on the tile's diamond, glyphs legible at 1x); **Douglas picked
  A the same day** ("I like A") for the 1994 screenshot's near-black tone
  and the skull at the foot, and A is what ships — one filename in
  `lv_art_props.py` and a rehash, as the contract promised. B's foot
  overhangs the tile and stays rejected. Record and
  plates: `shared/docs/art-poc/obelisk/README.md`. Landed as build step
  5/7 (`lv_art_props.py`), `SHAPE_MAGNETIC_OBELISK` in `lv_shapes.py`,
  the swap and re-centring in `build_map_17.py`, the pins row, and
  `test_art_props.py` (shape, TYPEFLAG, box on the tile, clear of the
  furniture, no 721 left). Rehashed (`TYPEFLAG`, `U8SHAPES`, `FIXED`
  moved; `EUSECODE` did not, so no ScummVM rebuild), reproduced by a second
  build, estate 30/30, and verified in-engine on a fresh world:
  `docs/playtest-2026-09-15-obelisk.md`.
- 2026-10-17 — **retired.** The 1994 screenshot reconstruction found
  screen11's obelisk is entirely retail art (12 f14-f17, cap 545, skull
  814) standing on four banded 1994 columns (875 f1), and 861 matches none
  of it (`docs/research/2026-10-16-screenshot-reconstruction/ReconCloud-REPORT.md`).
  Douglas approved retiring it; phase C Map 17 places the composite, with
  `QUALITY_OBELISK` on the front drum. The `lv_art_props.py` row,
  `SHAPE_MAGNETIC_OBELISK`, `tools/art/gen_obelisk.sh` and
  `shared/docs/art-poc/obelisk/` are gone (git history keeps them); 861 is
  in `lv_shapes.RETIRED_SHAPE_IDS`, its slots stay the base game's, and the
  number is never reused (`.claude/rules/shape-ids.md`).

---

## Contract 2 — the cloud tiles (shape 862, retired 2026-10-17)

**What it is.** The floor of Cloud City. On Map 17 today it is the three
cloud islands south of the Arrival Plaza's wall — "seen, never reached" —
built by `build_cloud_islands()` as three stepped daises of the flagstone
platform kit (shape 113): 34 + 9 + 35 = 78 tiles at z 0/8/16, with two
rock spires. The design brief says cloud-like terrain; the kit says pale
stone. The 1994 Cloud City screenshot (`screen11.gif`, the obelisk's
reference) shows the real floor around the obelisk: a **flat** texture of
white cloud with pale blue-violet shadow, a fine three-tone stipple, no
tile edges, no puff, no perspective. Sampled, its colours land exactly on
`U8PAL` entries 11 (white, 53%), 2 (235,235,255, 32%) and 3 (223,223,255,
7%). The 2026-07-19 proof asked for "puffy" and got a 3D block seen from a
steep angle — the wrong idiom; the floor is a texture, and the tile is a
window onto it.

**What is made.** One flat ground tile, generated as a *seamless top-down
texture* (agy, the screenshot as the style reference) and then projected
onto the floor plane and cut to the donor's diamond by a repo tool
(`tools/art/cloud_tile.py`), so tessellation is by construction rather
than by asking a generator for it: a screen pixel (x, y) of the tile
samples the texture at (u, v) = (x + 2y, x − 2y) mod 64, which is periodic
under the tile lattice's two generators (32, 16) and (32, −16). The
projected luminance is then dithered into the three 1994 tones, at those
proportions, so the stipple is drawn at 1x rather than quantized from a
render. The autocorrelation of the screenshot's floor shows no recoverable
tile period (the GIF is a squeezed 317×183 capture), so the texture is
generated, not lifted.

**Engine identity.**

| | |
|---|---|
| Shape | **862** |
| Frames | 1 — the flat top. `raised_platform`'s four roles (inner, south, east, corner) all use it: a cloud has no faces, and the tier below shows around a tier as a lower layer. Face art, if ever wanted, is frames 1–3. |
| TYPEFLAG donor | **113** `raised platform` — `SI_FIXED \| SI_SOLID \| SI_LAND`, footpad (4,4,1): the kit's own entry, copied whole. The tile keeps behaving as the tile it replaces (an 8-unit step, standable if ever reached). Not 35: `SI_DRAW` sorts a flat under a glob floor (`.claude/rules/map-geometry.md`). |
| Frame geometry | **exactly the donor's frame 0**: 63×34, anchor (32, 39), and the donor's own opaque mask (the diamond plus its two-row lip, sampled from the FLX), so the cloud fills precisely the pixels the flagstone did and tessellates as the kit does. The PNG is RGBA at game scale with hard alpha and exact `U8PAL` colours: `no_key`, `no_trim`, no scale, no despill — every pixel on a diamond's boundary touches transparency, so a chroma key and its despill would recolour the seam. `quantize` hits distance 0 on every pixel. |
| Build input | the finished 63×34 PNG in `shared/docs/art-poc/cloud/`, committed; the agy texture beside it is provenance. `cloud_tile.py` is deterministic (error diffusion, no randomness) but runs once; the PNG is canonical for the hash. |
| Outer edge | at an island's outermost tier the flat frame has no face, so the edge is a thin diamond over the void. That is the look, by this contract; a soft underside would be frames 1–3 and a second pass, never "fixed" by borrowing the flagstone faces. |
| Anim | none |
| Usecode class 862 | none; nothing to click on a floor. |
| `TYPE_SHAPES` | no re-point; no compiled filter names a type resolving to 113. |

**Placement.** `build_cloud_islands()` unchanged in geometry: `dais()` gains
`shape`/`frames` arguments and the islands pass `SHAPE_CLOUD_TILE` and
`CLOUD_FRAMES = (0, 0, 0, 0)`. Same 78 positions, same z. The rock spires
stay. No pins (nothing reads the islands; no test floods to them).

**Build.** A second row in `lv_art_props.py`, with the row schema gaining
`anchor: 'donor'` and `no_trim`/`height: None` for game-scale frames (the
option the god runs already use through `lv_god_statues.py`).

**Verification.** `test_art_props.py`: shape 862 has one frame of the
donor's size, offsets and mask; its TYPEFLAG entry equals 113's; Map 17
carries 78 of it south of y 11776 and no 113 there. Then in-engine: a
plate on an island at 640×400 (teleport — they are not reachable by
design) and one from the Arrival Plaza's south edge, checking the seams
between tiles at one z and the step between tiers.

### Record

- 2026-09-15 — contract written; two textures through `agy`
  (`tools/art/gen_cloud.sh`: A small packed puffs, B larger billows), five
  crops through `tools/art/cloud_tile.py`. **B at zoom 2 shipped**: white
  puffs with pale-blue scalloped hollows at the reference's scale; A's
  puffs average into noise at every crop. Thresholds replaced error
  diffusion after the first pass came out a haze. The tile is
  `shared/docs/art-poc/cloud/cloud_tile.png`; the tessellation plate shows
  no seam. Record: `shared/docs/art-poc/cloud/README.md`. Landed as the
  second row of `lv_art_props.py` (schema grew `anchor`/`no_key`/`no_trim`),
  `SHAPE_CLOUD_TILE` in `lv_shapes.py`, `dais()` passthrough in
  `build_map_17.py`, `test_art_props.py` generalised over `PROPS` (38
  checks, the donor-mask equality among them). Rehashed (all three
  artifacts moved, EUSECODE not), reproduced, estate 30/30, hygiene 54/54,
  and verified in-engine on a fresh world with the high-res clear on:
  `docs/playtest-2026-09-15-cloud-tiles.md`. Finding kept there: the void
  the islands stand in is never cleared without `usehighres`, so a player
  looking past the plaza wall sees stale frames — a map or installer
  question, not the tile's.
- 2026-10-17 — **retired.** The 1994 cloud floor is five exact frames cut
  from screen11 and re-found in screen01/12/13; 862 is a different drawing
  on a slab 8 units tall. Shape 874 (an `indexed` row on retail 163's flat
  row) replaced it on Map 17 (phase C) and Map 13. The `lv_art_props.py`
  row (and the `anchor`/`no_key`/`no_trim` row options only it used),
  `SHAPE_CLOUD_TILE`, `tools/art/cloud_tile.py`, `tools/art/gen_cloud.sh`
  and `shared/docs/art-poc/cloud/` are gone (git history keeps them); 862
  is in `lv_shapes.RETIRED_SHAPE_IDS`, its slots stay the base game's, and
  the number is never reused.

---

## Contract 3: the Sacred Rock (shape 863)

**There is no 1994 Sacred Rock.** Contracts 1 and 2 redrew something the
1994 record shows: the obelisk stands in `screen11.gif`, and so does the
cloud floor. This one has no original. `Sacred Smallish Unusual-Colored
Rock` is a **joke placeholder** from Plot v1.1/v1.2 that was replaced by
`Sacred Circle` before the usecode snapshot, with zero occurrences in the
recovered source, verified both ways
(`docs/research/2026-07-25-design-fidelity.md`, the joke-placeholders
list). The stone on the paving is this project's dressing, placed by the
2026-09-15 landscape pass, and the queue's name for it is our coinage. So
the look is a design choice, and the only reference the map offers is the
ring it stands in.

**What is wrong with it today.** `shared/docs/art-poc/sacred-rock/before-circle-640x400.png`,
shot in-engine at 640×400 from (20480, 17100, 0): eight pale dressed
monoliths on the 768 radius (shape 38 frames 2/3, 27×59 px), a 5×5 paving
of pale slabs at the centre, and on that paving a dark striated lump
(shape 66 frame 4, 41×65 px) that reads as rubble from a cave mouth. It
fails on two counts at once. **Material:** near-black and gnarled where
the ring is pale and dressed. **Scale:** 65 px against the ring's 59, so
the centre of a ceremonial circle stands level with its own fence.
`before-rock-4x.png` and `before-ringstone-4x.png` are the two at 4×.

**The look: a ninth stone. Decided by Douglas 2026-09-20.** Two readings
followed from the map, and the first is what ships:

- **A ninth stone. CHOSEN.** The same pale dressed idiom as shape 38,
  taller and heavier, carved if carving is wanted. The centre then belongs
  to the ring, which is the one thing the circle already does well.
- **A Zealan altar.** A table or basin, the ceremony's furniture. Weaker
  on the evidence: `SHADES.UNK` stages the ceremony 320 to 580 units
  SOUTH of this stone (elders at y 17216..17472, the stone at y 16831), so
  it is the altar to nothing, and Contract 1 already gave the "landmark"
  reading to the obelisk.

The deciding constraint either way: **the centre stone must read as
belonging to the ring.**

**Engine identity.**

| | |
|---|---|
| Shape | **863** (861 the obelisk, 862 the cloud tile; `.claude/rules/shape-ids.md`) |
| Frames | 1 |
| TYPEFLAG donor | **66** itself, the shape it replaces: `SI_FIXED \| SI_SOLID`, `SF_GENERIC`, no anim. Its own entry, so nothing about how the stone collides changes except the height below. |
| Footpad | **(4,4,8)**. The x/y stays (4,4) because the placement arithmetic below depends on it; z goes 5 → 8 so the box is 64 world units tall and `footpad_screen_size(4,4,8)` gives the 64×96 screen box a 96 px sprite needs. The box grows upward only, and the Avatar's 40-tall body already collides with the 40-tall box it has, so nothing about walking past it changes. |
| Anchor | bottom-centre (`xoff=w/2, yoff=h`), the prop convention |
| Anim | none (`animType 0`) |
| Usecode class 863 | **none**, and none is lost: EUSECODE entry 865 is empty, and so is entry 68, so shape 66 prints nothing on a double-click today. |
| `TYPE_SHAPES` | **no re-point**, and this is the one contract where a live filter exists on the shape being replaced. `TypeSealingBoulder` resolves to 66 and `lv-new/COLPUZZL.UNK:175` reads it: `foreach item where type = TypeSealingBoulder within 2200 of referent`, guarded by `item.getQ() = 299` and scoped to Map 11's doorway plug. The Sacred Rock is quality 100 on Map 10. Giving it a new id leaves shape 66, the type, and the filter's targets untouched. |
| Height | **96 px**, measured: the ring stones are 59, the placeholder 65, the obelisk 127. Half again the ring reads as the centre; the obelisk's 128 is a city landmark and stays taller. |

**Placement, and the arithmetic is load-bearing.** Position stays exactly
**(20415, 16831, 0)**, quality 100. `map_walkability`'s `MAP10_ROOT_SEED`
is (20480, 16896) and must stay standable: with footpad (4,4) the stone's
box is x 20288..20415, y 16704..16831, and an Avatar standing on the seed
covers x 20417..20480, y 16833..16896. **One world unit of clearance on
each axis.** A wider footpad, or the exact centre point, seals the seed
cell and `map_walkability.run_map10` fails. The stone sits 64 units
north-west of centre for this reason and must stay there.

**Pins, and this one is a source edit.** `derive_map_pins.py`'s
`DECORATIVE` table is hardcoded, matched by (map, shape, quality), and it
files a `surprises` note when nothing matches. So the map-10 spec at
`derive_map_pins.py:303` needs `'shape': 863`, `'kind': 'custom_art'` (the
obelisk's row is the model), and a `why` rewritten to the
`TypeSealingBoulder` chain above, because the one it carries today still
tells the 721 chimney's `TypeStatue` story. Then re-derive after the FIXED
build. Shape 66 stays on every LV map as ambient rubble (29 instances on
Map 10 alone), so the hygiene placeholder count does not move.

**Build.** A third row in `lv_art_props.py`, the table-driven step 5/7, so
the build's step count does not grow:

    {'shape': SHAPE_SACRED_ROCK, 'name': 'Sacred Rock', 'donor': 66,
     'footpad': (4, 4, 8),
     'frames': [('sacred-rock/<pick>.png', 96, MAGENTA, 130, 16)]}

plus `SHAPE_SACRED_ROCK` in `lv_shapes.py` and the constant swap in
`build_map_10.build_sacred_circle()`.

**Verification.** `test_art_props.py` gains the row's checks and one
`Box::overlaps` assertion that the stone's box clears the root seed cell
and the span `SHADES.UNK` teleports the three elders onto (20224..20672,
17216..17472, which lies south of the centre paving). `map_walkability.run_map10` and `test_route_reach` stay
green; hygiene row zero. Then in-engine on a fresh world at 640×400 from
(20480, 17100, 0), the same framing as the before plate, with a ring stone
in shot for scale, and a second from the north on the ceremony's approach
line.

### Record

- 2026-09-20. Contract written, the look decided the same day
  (**Douglas took the ninth stone**), and **landed**. The generator
  reference is the ring itself, `reference-ring-stones.png` (shape 38
  frames 2 and 3 rendered clean on magenta), passed the way the obelisk
  passed its screenshot crop: match this material, these tones, this
  dressing. `tools/art/gen_sacred_rock.sh` rolled six candidates over two
  passes on one axis each: **A** plain, **B** runes down the lit face,
  **C** a dressed shaft with a rough unworked crown.

  **The v1 trio read as stacked masonry in a heavy black keyline, in
  neutral grey, and two of those three complaints were wrong.** The
  keyline and the neutral grey both disappear in the U8PAL quantize, so at
  game scale every candidate is already the ring's cold blue-grey with no
  outline. Judging raw 1024 px output is what produced them. Only the
  stacked-block reading was real; v2 pinned it as its own clause and fixed
  it. **C2 ships**, 57x95 px, **approved by Douglas on 2026-09-20** off the
  before/after and the candidate sheet. Record and plates:
  `shared/docs/art-poc/sacred-rock/README.md`.

  Landed as the third row of `lv_art_props.py`, `SHAPE_SACRED_ROCK` in
  `lv_shapes.py`, the constant swap in `build_map_10.build_sacred_circle`,
  the `derive_map_pins.py` `DECORATIVE` spec (shape 863, `custom_art`, the
  `TypeSealingBoulder` chain in its `why`), and section 5 of
  `test_art_props.py` (60 checks now, the one free world unit against
  `MAP10_ROOT_SEED` among them). Rehashed: `TYPEFLAG`, `U8SHAPES` and
  `FIXED` moved, `EUSECODE` did not, so ScummVM is untouched. Reproduced
  by a second build, estate 30/30, `map_walkability` 137/137, and
  verified in-engine on a fresh world: `findShape 863` returns one item at
  (20415, 16831, 0) quality 100, and it reads as the ring's own stone.

---

## Contract 4: the Message Scroll (shape 864)

**What it is.** A document. Plot v1.2 beat 13 has the Avatar find it in the
deserted Cloud World beside the two Shield halves and the skeletons of the
missing boys; beat 14 has him carry it back to Ezrekal and show it to her
(`shared/corpus/plot-documents/story-beats.yaml:293`, `:304`). The record
gives its errand and one line of content: "message from one of the gods
addressed to Love, Hate, and Apathy explaining the Titans' attack"
(`items.yaml:121`, sourced to Plot v1.2 beat 14). There is no 1994 art for
it and no 1994 usecode: `MAGNET.UNK` is Cloud City's only recovered file
and it never names the scroll. So the look is a design choice, as the
Sacred Rock's was, and the reference the game offers is its own scroll.

**What is wrong with it today.** The chamber's centrepiece is a bench.
Shape 158 is a wooden plank stool, 32x40 px, `SI_FIXED | SI_SOLID |
SI_LAND`, `SF_GENERIC`, footpad (3,1,3), standing frame 0 on a flagstone
plinth at (3328, 1536, 8). Clicking it prints nothing: FLX entry 160 is
empty in the base game and in the LV build, so no class dispatches at
shape 158. Its quality 80 is invisible to usecode as well, because
`Item::I_getQuality` returns 0 for every family except `SF_QUALITY`
(`item.cpp:2841`) and 158 is `SF_GENERIC`.

**The queue line's "needs the `TYPE_SHAPES` re-point" is wrong, and a
re-point would be a defect.** Nothing compiled finds this item by type.
`MAGNET.UNK:86` and `:282` filter `type = TypeMagicScroll` **within
container Avatar**, so they walk the inventory and can never see a map
item. `EZREKAL.UNK` filters `TypeWeedz` and `TypeShields` only, including
in the beat-14 scene where she is shown the scroll. The one other mention
is `lv-patched/FREE.UNK:1338`, `tongue.create(TypeScroll,0)`, a creation
in the debug grant that hands the Avatar blackrock, magic arms, a scroll
and a grimoire. That is what a re-point would break: pointing `TypeScroll`
at 864 makes the debug grant spawn the Message Scroll. Verified
2026-09-21.

**A separate defect, found here and left undone.** `TYPE_SHAPES` resolves
`TypeBook`, `TypeScroll`, `TypeMagicScroll` and `TypeGrimoire` all to 158,
the stool. The engine's own scroll is **159** (`SF_QUALITY`, class 0x9F
`BASESCRL`, whose `look()` barks "scroll of dispelling magic portals" and
its kin by quality, and whose `use()` spawns the spell class for qualities
0 to 15), and its book is **288** (`template book`, 12 frames, one per
binding colour). So `FREE.UNK`'s cheat scroll and grimoire are created as
benches today. Fixing it is a one-line table edit whose blast radius is
`EUSECODE.FLX`: a rehash, a regenerated detection entry, a ScummVM
rebuild. It is unrelated to this item's art and is not done here.

**The look: the game's own scroll, drawn larger.** A single sheet of
aged parchment lying flat on the plinth, one end still rolled, the sheet
open enough to show ink. The reference is base shape 159 rendered clean
(`shared/docs/art-poc/message-scroll/reference-base-scroll.png`), passed
the way the Sacred Rock passed the ring: match this material, these tones,
this idiom. The deciding constraint is that it must read as a document at
1x from the plinth's own scale, which is the 63x34 flagstone top it lies
on.

**Engine identity.**

| | |
|---|---|
| Shape | **864** (861 obelisk, 862 cloud tile, 863 Sacred Rock; `.claude/rules/shape-ids.md`) |
| Frames | 1 |
| TYPEFLAG donor | **159**, the engine's scroll: `SI_SOLID`, `SF_QUALITY`, footpad (2,2,1), no anim. Not 158's `SI_FIXED | SI_LAND`: a document is not furniture, and `SI_LAND` is for what the Avatar walks on. |
| Carryable | **yes, and that is the point.** Donor 159 carries no `SI_FIXED`, so the scroll can be picked up and carried to Ezrekal, which is what beat 14 asks of it. The 539 Shield halves are the precedent for a carryable placed through `FIXED.DAT`. |
| Quality | **80 becomes readable.** `SF_QUALITY` is the family `I_getQuality` answers for, so `QUALITY_MSG_SCROLL` stops being map-side bookkeeping the moment any class asks. |
| Footpad | **(2,2,1)**, the donor's own: a 32x24 screen box, 64x64 world units by 8 tall. The art is authored to fit inside 32x24. |
| Anchor | bottom-centre (`xoff=w/2, yoff=h`), the prop convention |
| Anim | none (`animType 0`) |
| Usecode class 864 | **compiled, 2026-09-21** (`lv-new/MSGSCRL.UNK`, `TYPEMESSAGESCROLL` pinned to 0x0360). `look()` barks "message scroll"; `use()` opens the scroll gump with Odion's letter. The shape number and the class number are one decision now: renumber either and the scroll stops reading. |
| `TYPE_SHAPES` | **no re-point**, per the paragraph above. |
| Height | **22 px**, against the base scroll's 20 and the plinth top's 34. Larger than 159 so it reads as the chamber's object, smaller than the tile it lies on. |

**Placement, unchanged and not free to move.** (3328, 1536, 8), quality 80,
on the flagstone plinth `build_scroll_chamber()` already builds; the
plinth's top is z=8 (donor 113, footpad z 1), so a non-`SI_FIXED` item at
z=8 rests on it. Route 17's goal "the Scroll Chamber is reachable" is that
exact coordinate (`test_route_reach.py:351`, `reached_near` ring 96), and
`derive_map_pins.route_cite` finds the citation by grepping
`test_route_reach.py` for the literal string `3328, 1536,`. A move of one
unit drops the pin row with no complaint, because that loop has no
`surprises` fallback.

**Pins.** `derive_map_pins.py:610` keys the row on `(17, 158)` and quality
80. It becomes `(17, 864)`, with the `why` rewritten: no compiled filter
reads it, the route flood pins the coordinate, and the quality is live
under `SF_QUALITY`. Re-derive after the FIXED build.

**Hygiene.** Shape 158 appears exactly once in all of LV, this item
(counted 2026-09-21 over `FIXED.DAT` maps 9, 10, 11, 13, 17, 18). After
the swap it appears nowhere, so `PLACEHOLDERS[158]` in
`test_map_hygiene.py` guards an empty set and every map's row stays 0.

**Build.** A fourth row in `lv_art_props.py`, the table-driven step 5/7:

    {'shape': SHAPE_MESSAGE_SCROLL, 'name': 'Message Scroll', 'donor': 159,
     'footpad': (2, 2, 1),
     'frames': [('message-scroll/<pick>.png', 22, MAGENTA, 130, 16)]}

plus `SHAPE_MESSAGE_SCROLL` in `lv_shapes.py` and the `SHAPE_BOOK` swap in
`build_map_17.py`, where the constant is an alias of `SHAPE_STOOL` today.

**Verification.** `test_art_props.py` gains the row's checks: the shape
exists with one frame, its TYPEFLAG entry equals 159's, the frame fits the
32x24 box, Map 17 carries one 864 at (3328, 1536, 8) quality 80, and no
map carries a 158. `test_route_reach` route 17 stays green and
`test_map_hygiene` map 17 stays 0. Then in-engine at 640x400: a before
plate and an after plate of the plinth from the chamber's south doorway,
and a 4x crop of the scroll beside the base game's 159 for scale.

**Answered 2026-09-21: the scroll is read.** Douglas took the class and
signed the letter Odion, so `lv-new/MSGSCRL.UNK` compiles at 864 and the
Record below carries it. Three things made it cheap: entry 866 was free,
the gods' `TYPEZEALANGOD` at class 860 was the precedent for a class
pinned at a shape number, and the content was already on record
(`story-beats.yaml:281`).

### Record (filled as the work lands)

- 2026-09-21. Contract written and **landed the same day**. The queue's
  premise for this item, a `TYPE_SHAPES` re-point, was wrong: nothing
  compiled finds the scroll by type, and a re-point would have sent
  `FREE.UNK`'s debug grant into the new shape. What the item actually
  needed was a donor decision, and donor **159** is the contract: the
  engine's own scroll, `SI_SOLID` without `SI_FIXED` (so the Avatar can
  carry it to Ezrekal, which beat 14 asks and the 158 stool made
  impossible) and `SF_QUALITY` (so quality 80 stops reading as 0 through
  `Item::I_getQuality`).

  Five candidates over two passes (`tools/art/gen_message_scroll.sh`), the
  reference being shape 159 rendered clean. **Every v1 candidate read as a
  blank sheet at 22 px**: the ink survived the 1024-to-22 downscale as
  three grey pixels, so v2 pinned the ink as its own clause. **A2 ships**,
  30x22 px, the sheet open flat with four lines of dark strokes,
  **approved by Douglas on 2026-09-21** off the candidate sheet and the
  in-engine plate; B2, the sealed version, was the only real alternative
  and stays one filename away. The resize is deliberately
  non-uniform (`width` 30 with `height` 22, a new optional row key): the
  generator draws the sheet square, seen from above, and the squash is the
  projection onto the 2:1 floor. Record and plates:
  `shared/docs/art-poc/message-scroll/README.md`.

  Landed as the fourth row of `lv_art_props.py`, `SHAPE_MESSAGE_SCROLL` in
  `lv_shapes.py`, the `SHAPE_BOOK` alias swap in `build_map_17.py`, the
  `(17, 864)` key and rewritten `why` in `derive_map_pins.py`, and section
  6 of `test_art_props.py` (83 checks now). Section 2's blanket `SI_FIXED`
  assertion became donor-relative in the same commit, because this is the
  track's first carryable row. Rehashed: `TYPEFLAG`, `U8SHAPES` and
  `FIXED` moved, `EUSECODE` did not, so ScummVM is untouched. Reproduced
  by a second build, estate 30/30, pins re-derived (one row, 158 to 864),
  and verified in-engine on a fresh world: the scroll rests on the plinth
  at z=8, a click prints nothing, and **the Avatar picked it up** (+10
  total weight): `docs/playtest-2026-09-21-message-scroll.md`.

  Two things left standing there. The sprite sits on the near half of
  its tile, because the obelisk's re-centring is unavailable while the
  position is frozen by the pins grep. And `TYPE_SHAPES` still points
  `TypeBook`/`TypeScroll`/`TypeMagicScroll`/`TypeGrimoire` at the 158
  stool; the engine's scroll is 159 and its book 288.

- 2026-09-21, later the same day. **The scroll reads.** Class 864 is
  `lv-new/MSGSCRL.UNK`: `look()` barks "message scroll", `use()` calls
  `Scroll::read` with a three-page letter. `TYPEMESSAGESCROLL` is pinned
  to 0x0360 in `lv_manifest.json`, and the engine finds it off the shape
  number by itself (`findShape 864` now prints `(uc: TYPEMESS)`).

  **The text comes off the 1994 record.** Plot v1.2 beat 13
  (`story-beats.yaml:281`) has the message reveal that the Titans attacked
  the pantheon at the Great Council and that Love, Hate and Apathy lie
  entombed at the shrine of Kumash Ghor. `EZREKAL.UNK:1697` supplies the
  names: the Shield carries the symbols of Felicitar, Doloras and Timyra,
  and a second trio, Amoras, Apathas and Odion, are "the Ancients that did
  not arrive to help defend the Vale". **Odion signs it** (Douglas,
  2026-09-21), which is who can address all three and still be free to
  write. The closing paragraph plants beat 15, where Ezrekal needs the
  people's faith behind the Shield.

  **One compiler change was needed, and it fixed a second class.**
  `Book::read` (0x6E), `Scroll::read` (0x6F), `Grave::read` (0x70) and
  `Plaque::read` (0x71) take the same shape of call, so a bare `read()`
  resolved to whichever slot registered first. The 1994 sources choose
  with the include file's name (`uses "books"` in SGBOOK, `uses "plaque"`
  in PLAQUENS), so `_intrinsic_from_uses` in `u8c_codegen.py` now consults
  the file's `uses` lines when, and only when, the plain lookup is still
  ambiguous. A probe build proved the blast radius is one class besides
  this one: TYPENSGOLDPLAQUE moved from `Grave::read` to `Plaque::read`,
  which is what it always meant. Four slots are pinned by
  `test_uses_imports.py` (38 checks).

  `EUSECODE.FLX` moved for the first time on this track (`40ec62f4…`), so
  the cascade ran: `detection_tables.h` regenerated, `LV_SIZE` in
  `build_scummvm.sh` updated by hand to 1504582 (the md5-5000 did not
  change, because 933 bytes appended past the first 5000 do not touch it),
  ScummVM rebuilt. The other three artifacts are byte-identical. Estate
  30/30, reproduced by a second build, pins re-derived. Verified in-engine
  on a fresh world: `docs/playtest-2026-09-21-scroll-class.md`. The look
  bark is the one thing that stayed NOT DEMONSTRATED, because this harness
  delivers no single-click feedback for any item today, the Avatar
  included. **The signature alone on page 3 is the shipped look**
  (Douglas, 2026-09-21), pinned in `MSGSCRL.UNK`'s header so it is not
  tidied away later.

---

## Contract 5: the elemental pillars and their receptacles (shapes 865, 866)

**What it is.** The four pillars that close the Elemental Dungeon and the
four receptacles beside them, Plot v1.2 beat 6
(`shared/corpus/plot-documents/story-beats.yaml:116`). The Avatar destroys
each pillar by using the opposite element's talisman on the receptacle at
its foot: fire against water, earth against air, "the ancient principle of
balance". All four down, and the sealed doorway to the teleporter pad
crumbles open. Art List v2.5 names "Pillars of Fire, Earth, Water, Air"
with three of the four crossed out, and carries a handwritten addition,
"Pillar receptacle" (`items.yaml:178-211`). No 1994 art survives and no
1994 usecode: "Usecode: Columns (Brian M.)" is a red X on the production
schedule, and `lv-new/COLPUZZL.UNK` is our rewrite to the recovered design
(`agents/npc-dialogue/docs/dialogue-elemental-columns.md`). So the look is
a design choice, as the Sacred Rock's and the Message Scroll's were.

**What is wrong with it today.** The four elemental pillars are four
chimneys and the four receptacles are four carved chests. Plates:
`shared/docs/art-poc/pillars/before-pillars-1x.png` and the same at 4x.

Shape **721** is the engine's `CHIMNEY` (class 0x2D1, `look()` barks
"chimney"), 6 frames at 32x56 (34 wide from frame 3 on), `SI_FIXED | SI_SOLID | SI_NOISY`,
`SF_GENERIC`, footpad (2,2,5). Map 11 places frames 0 to 3 as Earth, Air,
Fire, and Water. Frames 0 and 1 are rough stone stacks in brown and grey;
frames 2 and 3 are **red brick with an open flue at the top**, 3 wearing a
grey capstone. Element identity is unreadable from any of it: brown against
grey says nothing about earth against air, and fire and water are the same
brick chimney twice.

Shape **307** is `WARDEW` (class 0x133, `look()` barks "wardrobe"), 1 frame
at 52x55, `SI_FIXED | SI_SOLID | SI_LAND`, `SF_CONTAINER`, footpad (4,2,5).
It renders as an ornate domed chest with a stag carved on each door, which
is why `build_map_10.py` aliases it `SHAPE_CRATE` and stands five of them in
houses. As a receptacle it reads as treasure, so the puzzle's instruction to
the player is "open the chest", and the thing the player must actually do is
double-click it holding a gem.

**The receptacle's bark is gone, and the engine patch is why.** A single
click on a receptacle prints nothing today. The LV hunk in
`Item::callUsecodeEvent` replaces `class_id` with `npcNum + 1024` for **every
event**. The patch's own comment talks about dialogue, and look() goes through
it too: look() reaches class 1144 (`TYPERECE`), whose event table holds
`use()` and nothing else, so `get_class_event` returns 0 and the engine
returns without barking. Class 307's "wardrobe" is masked by the same
override that makes the puzzle work. Verified 2026-09-22 against
`shared/build/EUSECODE.FLX`.

**This item is the track's first required `TYPE_SHAPES` re-point.** Every
earlier contract found its re-point unnecessary or harmful, and the one
EUSECODE move so far (contract 4's class 864) added a class without touching
an existing one. This one edits `COLPUZZL`'s own bytecode: `COLPUZZL.UNK:139` evaluates the bare identifier as a
value,

    foreach pillar where type = TypeElementalColumn within 300 of referent

so `TYPE_SHAPES['TypeElementalColumn']` (721 today) is compiled into the
bytecode, and a pillar at a new shape is invisible to the search that
destroys it. The re-point is one line in `u8c_symbols.py`, and its blast
radius is the full artifact chain: `EUSECODE.FLX` moves, so
`ARTIFACTS.sha256` is re-recorded, the detection entry is regenerated, and
ScummVM is rebuilt (`/artifact-rehash`). Budget that before the art, because
everything else on this contract rides the same recompile for free.

**Nothing else on 721 moves, and nothing else on 721 is even live.**
`TypeStatue`, `TypeWoodThrone`, and `TypePedestals` resolve to 721 in the
same table. Audited 2026-09-22 across the **47 files the build actually
compiles** (the four source tiers resolved by basename precedence,
`lv-patched/` over `LOST VALE/` over `UNK files/UNK/`, plus `lv-new/`):

- `TypeStatue` appears in **none** of them. The `foreach ... type =
  TypeStatue` in `UNK files/UNK/PLNTST.UNK:34` is shadowed by
  `lv-patched/PLNTST.UNK`, which searches `TypeShortmushroom` instead.
- `TypeWoodThrone` appears in **none** of them. Its only use is
  `U8/MORDEA.UNK:892`, and `U8/` is not a compiled tier: Mordea's 721 is
  already baked into the shipped `USECODE.FLX` bytecode and no rebuild of
  ours touches it.
- `TypePedestals` appears twice in `UNK files/UNK/EAPUZL.UNK`, both times
  in a declaration header (`typeclass`, `process`), which never consults
  the table (`.claude/rules/shape-ids.md`).
- `TypeElementalColumn` appears **once**, at `COLPUZZL.UNK:139`, as a
  value.

So the re-point has a blast radius of one line of bytecode, and after it
shape 721 has no live `TYPE_SHAPES` consumer at all.

**No class is needed at either new shape, and one is wanted at 865.** The
receptacle keeps `npcnum = 120`, so its `use()` keeps dispatching to class
1144 whatever its shape is: the override fires on `_npcNum != 0` and a
non-empty target class, and excludes only the egg families. `TYPERECEPTACLE`
stays pinned at 1144 and must (`.claude/rules/build-artifacts.md`: never
renumber a pin). The pillars have no class today and want one only for
`look()`; see the decision below.

### Engine identity: the pillars, shape 865

| | |
|---|---|
| Shape | **865**, the next free custom-art ID (`.claude/rules/shape-ids.md`) |
| Frames | **4**, and the order is fixed by the map: 0 Earth, 1 Air, 2 Fire, 3 Water (`build_map_11.py:698-737`, receptacle quality 201-204 in the same order). The track's first multi-frame `lv_art_props.py` row; `frames` is already a list. |
| TYPEFLAG donor | **38**, the standing stone: `SI_FIXED \| SI_SOLID`, `SF_GENERIC`, footpad (2,2,5), which is 721's footpad exactly. Not 721 itself, whose `SI_NOISY` is what contract 1 rejected it for. |
| Footpad | **(2,2,10), landed 2026-09-24**: a 32x96 screen box that the 24-px columns fill, 64x64 world units by 80 tall. Every candidate sheet came back about 4:1 slender (four pillars in a square 1024 image cap each at about 250 px wide), so the box followed the art, as this contract said it would, and the (4,4) tile-sized box was set aside: an Avatar would have stopped 20 px short of a visible column. z=10 was paid for the way the anti-climb clause prices it: the chamber comment rewritten, `gate_reach()` added to `test_route_reach.py`. |
| Anchor | bottom-centre (`xoff=w/2, yoff=h`), the prop convention |
| Anim | none (`animType 0`) |
| Usecode class 865 | **compiled, 2026-09-24** (`lv-new/ELMCOLMN.UNK`, `TYPEELEMENTALCOLUMN` pinned to 0x0361). `look()` reads the frame and barks the element: "column of solid stone", "column of swirling wind", "column of roaring flame", "column of shimmering water". Dead until shape 865 is injected and placed; nothing on any map dispatches to it yet. |
| `TYPE_SHAPES` | **`TypeElementalColumn` 721 → 865, required.** The one live re-point on the track so far. |
| Height | **96 px, landed 2026-09-24** (frames 24x95, 24x96, 23x95, 23x96 after the trim; the Earth column measures 93 screen rows in the playtest's north pair plate, where the window renders 1:1), against the chimney's 56, the ring stones' 59, the Sacred Rock's 96 and the obelisk's 128. Decided against candidates on the "The Four Pillars" page: 96 on the box the column fills, Douglas's frame mix and no objection to the height. |

### Engine identity: the receptacles, shape 866

| | |
|---|---|
| Shape | **866** |
| Frames | **1.** Element identity is carried by quality 201-204, which `getQ()` reads and the art cannot. Four frames are available if the look wants a tinted basin per element; the map would place frame 0-3 beside the matching pillar and no usecode would change. |
| TYPEFLAG donor | **443** `statue`: `SI_FIXED \| SI_SOLID`, `SF_GENERIC`, footpad (3,3,3). Dropping `SF_CONTAINER` costs nothing, because `COLPUZZL` reads the quality with `getQ()`, which answers for every family (`I_getQuality` answers for `SF_QUALITY` alone, `item.cpp:2841`), and it stops the item claiming to be a container. |
| Footpad | **(3,3,3)**, the donor's own: a 48x48 screen box, 96x96 world units by 24 tall. A socket at knee height that the Avatar stands beside. |
| Anchor | bottom-centre |
| Anim | none |
| npcnum | **120, unchanged**, and it is the whole dispatch: class 1144 `TYPERECEPTACLE` fires `use()` off the npcNum override, so the shape number carries no usecode meaning. |
| Usecode class 866 | **none, and none is possible.** The override wins over `class_id = _shape` for every event, so a class at 866 would never run. |
| `TYPE_SHAPES` | **no re-point.** Nothing compiled finds a receptacle by type; `COLPUZZL::use()` starts from `referent`. |
| Height | **40 px**, under the pillar it serves and read as a fitting for it. |

**The anti-climb clause: what a taller footpad really costs.**
`build_map_11.py`'s gate hardening (the comment above `stone_room` in the
pillar chamber) stands the chamber's south wall in three courses, 120 tall
and continuous, after the 2026-07-31 playtest walked a one-course wall and
reached the teleporter pad with all four pillars standing. The engine tries
`climb72` down to `climb16` on jump (`u8_avatar_mover_process.cpp:485`), 72
is the ceiling, and support is `SI_SOLID | SI_LAND | SI_ROOF`
(`current_map.cpp:697`), so solid alone is standable and dropping `SI_LAND`
buys nothing.

**Distance is what protects the wall here.** The comment reads as if height
did. A chained climb needs a ledge beside the barrier, and the pillar grid is in the middle of
the room: the south gate line is y=22527, the nearest receptacle is y=21760
(767 units away) and the nearest pillar y=21504 (1023). A taller pillar
hands the Avatar nothing he can reach the wall from.

What a footpad above z=5 does break is the comment's stated invariant,
"nothing in the room tops 40". That sentence is prose, and it is the
reasoning a later reader will trust. So a pillar taller than 40 units of
collision is allowed, on two conditions: **rewrite that comment** to say
what actually holds (no standable within reach of a gate line tops 40), and
**add the assertion** to `test_route_reach.py`, where `gate_coverage(11)`
checks the wall lines alone and would not catch a new ledge. Phrase the
check as "no solid within one climb's reach of a gate line tops 40" so it
survives the next piece of furniture.

**The range math, which the footpads do enter.** `CurrentMap::areaSearch`
builds the search box from the **searcher's** footpad grown by the range, and
matches candidates on their **origin point** alone. So the pillar's footpad
is irrelevant to `within 300 of referent`, and the receptacle's is not: a
receptacle at (x, y) with footpad (fx, fy) searches x from `x - 32·fx - 300`
to `x + 300` and y likewise. For the Earth receptacle at (7680, 20736) with
the (3,3) box that is x [7284, 7980], y [20340, 21036]; its own pillar origin
(7680, 20480) is inside and the next nearest pillar origin (7680, 21504) is
768 away in y and outside. `COLPUZZL`'s header says "nearest other pillar is
1024+", which overstates it: the nearest is 768, on the same x. The margin
is still wide, and any receptacle footpad up to (8,8) keeps it.

**Placement, unchanged.** Map 11's Four Pillars chamber, 2x2 grid on the
3x3 paved squares `pillar_chamber()` already lays: Earth (7680, 20480) q201
frame 0, Air (8704, 20480) q202 frame 1, Fire (7680, 21504) q203 frame 2,
Water (8704, 21504) q204 frame 3, each receptacle 256 units south of its
pillar at the matching quality with `npcnum=120`. A (4,4) pillar box is the
centre tile of its paved square, so the obelisk's re-centring shift
`(128 − 32·fx)/2` is zero and nothing moves.

**Pins.** Nothing to edit; both rows derive themselves. `derive_map_pins.py`
finds the four pillar rows by resolving `COLPUZZL`'s compiled filter through
`TYPE_SHAPES` and matching items of that shape within 300 (Chebyshev,
`dist()`) of an `npcnum = 120` anchor (`WORLD_SCANS`, the
`TypeElementalColumn` spec), and the four receptacle rows off `npcnum` itself.
So the re-point flows through on the next re-derive, and forgetting it fails
loud: with `TypeElementalColumn` still 721 and no 721 on the map, the filter
is reported **dangling**. Re-derive after the FIXED build.

**Hygiene.** `PLACEHOLDERS[721]` in `test_map_hygiene.py` is
'chimney-as-column', and Map 11's four pillars are the only 721s on any
LV-authored map (counted 2026-09-22 over maps 9, 10, 11, 13, 17, and 18;
maps 8 and 39 carry 3 and 13 of Origin's own). After the swap that key
guards an empty set and every map's row stays 0. Shape 307 is not in
`PLACEHOLDERS` and stays out: Map 10 keeps five of them as `SHAPE_CRATE`,
which is an honest use of a carved chest.

**Build, as landed.** The fifth and sixth rows of `lv_art_props.py`, step
5/7, plus `SHAPE_ELEMENTAL_PILLAR` and `SHAPE_PILLAR_RECEPTACLE` in
`lv_shapes.py` and the two aliases in `build_map_11.py`:

    {'shape': SHAPE_ELEMENTAL_PILLAR, 'name': 'Elemental pillar',
     'donor': 38, 'footpad': (2, 2, 10),
     'frames': [('pillars/C2_f0_earth_c3plinth_raw.png', 96, MAGENTA, 130, 16),
                ('pillars/C2_f1_air_c3plinth_raw.png',   96, MAGENTA, 130, 16),
                ('pillars/C3_f2_fire_raw.png',           96, MAGENTA, 130, 16),
                ('pillars/C3_f3_water_raw.png',          96, MAGENTA, 130, 16)]}

The two `_c3plinth_` inputs are `tools/art/pillar_plinth.py`'s output
(2026-09-25): the C2 columns on C3's plinth.

    {'shape': SHAPE_PILLAR_RECEPTACLE, 'name': 'Pillar receptacle',
     'donor': 443, 'footpad': (3, 3, 3),
     'frames': [('pillars/R_raw.png', 40, MAGENTA, 130, 16)]}

plus the `TypeElementalColumn` line in `u8c_symbols.py`, which is what
turned this into an EUSECODE rebuild. The four pillar PNGs are cut from
two four-in-a-row sheets by `tools/art/split_sheet.py`, so a re-roll of one
element is one sheet and one cut.

**Verification.** `test_art_props.py` gains both rows: each shape exists
with its frame count, each TYPEFLAG entry equals its donor's, each frame fits
its box, Map 11 carries four 865s at the four coordinates with frames 0-3 and
qualities 201-204 and four 866s with `npcnum=120`, and no LV map carries a
721. A new check asserts `TYPE_SHAPES['TypeElementalColumn'] ==
SHAPE_ELEMENTAL_PILLAR`, on the pattern `test_sanctum_clearance.py` uses for
the gods. `test_route_reach` route 11 stays green and `gate_coverage(11)`
stays green, with the added assertion from the anti-climb clause: no solid
within one climb's reach of a gate line tops 40.
Then in-engine at 640x400: a before plate and an after plate of the 2x2 grid
from the chamber's north doorway, a 4x crop of one pillar and its receptacle,
and the puzzle run end to end on a fresh world, which is the only proof that
the re-point compiled into the right number.

**A neighbouring finding, recorded here and left open.** The four talismans the
player carries to these receptacles are shape 596 frames 0 to 3, and they do
not read as their elements either: frame 0 (Earth) is a small orange flask,
frame 1 (Air) a gold ring with a purple stone and twice the size of the
others, frame 2 (Fire) a purple gem, and frame 3 (Water) a blue gem. Frames
4 to 7 of the same shape are a matched set of four 5x5 star gems in orange,
red, purple, and blue, which would read as one family of four. Moving to
them is a map change plus `COLPUZZL`'s `oppFrame` mapping, so it is cheap
only while this recompile is open. Rendered and confirmed 2026-09-22
(`shared/docs/art-poc/pillars/reference-talisman-gems.png`).

**Decision 1, answered 2026-09-24: the pillars speak.** Douglas took the
class ("yes take it"), so `lv-new/ELMCOLMN.UNK` compiles at 865 and the
Record below carries it. It landed ahead of the art, on its own EUSECODE
move, because the pin and the barks are decided and the art is not; the
re-point still lands with the art, on a second move. The class declares
`typeclass TypeElementalColumn`, the design doc's name, and that is safe
for `COLPUZZL`: the codegen resolves a Type identifier through
`TYPE_SHAPES` before the class table (`u8c_codegen.py:1686`, `:2267`, with
the class lookup the fallback at `:2354`), so `type = TypeElementalColumn`
still compiles to 721 until the re-point is made on purpose.
Two cautions that shaped the barks. The design doc's **"Pillar Look Barks" table
was stale until 2026-09-22**: it listed the pre-2026-07-04 frame order
(frame 0 water, 1 flame, 2 stone, 3 wind) under a Class Definition section
that had been corrected to 0 Earth, 1 Air, 2 Fire, 3 Water. It is remapped
in place now; map the barks by element all the same. And its "shattered
remains of a column" is unreachable, because `COLPUZZL` calls `destroy()` on
the pillar (`:139-141`), so no item survives to be looked at.

**Decision 2, taken 2026-09-25: a receptacle speaks.** Douglas put it in
the batch ("complete 1"), so `TypeReceptacle` carries `look()` barking
"pillar receptacle", the 1994 Art List's handwritten name
(`story-beats.yaml:124`), in class 1144 where the npcnum override sends it.

### Record (filled as the work lands)

- 2026-09-22. Contract written. Nothing built.
- 2026-09-24. **Class 865 landed, art still to come.** `lv-new/ELMCOLMN.UNK`,
  `look()` only, four barks by frame in the map's element order plus a
  fallback "column" for a frame the map never places; `TYPEELEMENTALCOLUMN`
  pinned to 865 in `lv_manifest.json` (append-only, between TYPEBULLWHIP and
  TYPEFEDORA). The build's Compilation Report went to 46 of 48 (the same
  two 1994 failures), the class is 414 bytes at 0x0361 with a single `look()`
  event and the five strings visible in the disassembly, and **`EUSECODE.FLX`
  alone moved** (1,504,582 to 1,504,996 bytes; the other three hashes
  unchanged). md5-5000 stayed `a9861861…` because the class appends past the
  first 5000 bytes, so `LV_SIZE` in `build_scummvm.sh` went to 1504996 and
  `LV_MD5` did not move. The cascade, as it ran: a second
  `tools/build_artifacts.sh` reproduced all four hashes; `./build_scummvm.sh`
  exited 0; the estate is 30/30 with `test_new_dialogue.py` at 13/13;
  `install_lv.sh` put `USECODE/EUSECODE.FLX b1f29480…` in place; and
  `scummvm-lv/scummvm --detect -p shared/data/u8-install` offers "Ultima
  VIII: Pagan (Gold Edition + Lost Vale/DOS/English)", which stands in for
  the rehash skill's step-9 launch (no display was needed to prove the
  detection entry). **No in-engine bark is possible yet**: no item of shape
  865 exists to click, so the first proof of the bark is the art landing.
- 2026-09-24, later. **v1 candidates, and two decisions.** `tools/art/gen_pillars.sh`
  made three pillar sets as four-in-a-row sheets (A the element as a crown
  on a stone shaft, B the element carved on the face, C the column made of
  its element on a stone plinth) and one receptacle, all through `agy`;
  `tools/art/split_sheet.py` cut the sheets into frames (B and C on clean
  magenta bands, A at the dip minima because its plinths touched) and
  `tools/art/pillar_preview.py` pushed every frame through
  `png2shape.build_frame` and rendered it at 72 and 96 px beside the
  chimney and a ring stone, with a per-frame palette check. At game scale
  B's emblems vanish (Earth and Water share their top indices at 96) and
  A's crowns half survive; **C reads at 1x with no palette index shared
  across its four frames**. Every set came back about 4:1 slender. Page:
  the "The Four Pillars" artifact, 2026-09-24. **Douglas chose C** ("I like
  set C") and asked for the columns to be less rectangular and more
  organic, so a v2 pass (C2 natural, C3 wild) pins the silhouette, a 3:1
  shaft and the plinth's stone as their own clauses. **The receptacle is
  approved as generated** ("Receptacle looks fine"): `R_raw.png`, 40 px on
  donor 443's (3,3,3), 13 colours.
- 2026-09-24, evening. **Landed and verified in the engine.** The v2 pass
  (`gen_pillars.sh` C2 "natural" and C3 "wild") answered the organic brief;
  Douglas mixed them, **Earth and Air from C2, Fire and Water from C3**, and
  they went in at 96 px on the (2,2,10) box the columns fill. Build:
  `lv_shapes.py` constants, two `lv_art_props.py` rows, the `build_map_11.py`
  swap and its anti-climb comment rewritten, `TypeElementalColumn` 721 → 865,
  `test_art_props.py` sections 7 and 8 (131 checks), `gate_reach()` in
  `test_route_reach.py` (76), `test_uc_sim.py` reading the pillar shape from
  `TYPE_SHAPES`. **All four artifacts moved** (`TYPEFLAG 9f534e59…`,
  `U8SHAPES 0db9dbe9…`, `EUSECODE d6b0ad66…`, `FIXED 0193f53d…`); the
  detection entry did not, because the re-point is a same-width immediate
  (size 1,504,996 and md5-5000 unchanged), so ScummVM was not rebuilt.
  Second build reproduced, estate 30/30, pins re-derived (eight rows, 721 →
  865 and 307 → 866, by the derivation alone). In-engine
  (`docs/playtest-2026-09-24-elemental-pillars.md`): `findShape 865` lists
  four `(uc: TYPEELEM)` items at the chimney's coordinates; a receptacle
  double-clicked empty-handed ran `use()` in class 1144 and barked the repel
  line; with the Air talisman in the pack the Earth receptacle consumed it,
  barked "The air talisman howls with fury!", and **`findShape 865` fell to
  three with q201 gone**, which is the re-point proven against the real
  `areaSearch`. The look bark stays NOT DEMONSTRATED for the harness reason
  of 2026-09-21. Two things left standing: the C2 plinths are violet where
  the C3 plinths are the ring stone's grey (a family seam at the foot, one
  re-quantize away), and decision 2, the receptacle `look()`, waits for the
  next EUSECODE move with the paper-types fix.
- 2026-09-25. **One plinth under all four.** Douglas: "fix it now, C3
  plinth under all four." `tools/art/pillar_plinth.py` takes each C2
  frame's plinth as the connected component of violet pixels (the twister's
  blue shading overlaps the top face in 2D and is left alone that way),
  assembles C3's plinth from the Fire, Earth, and Water frames (every C3
  column covers the top face, so that face is C2 Air's texture re-coloured
  from C2's mean to the rim's), and writes `C2_f0_earth_c3plinth_raw.png`
  and `C2_f1_air_c3plinth_raw.png`; the 865 row points at them. Frame
  sizes unchanged (24x95, 24x96, 23x95, 23x96); mean plinth colour per
  built frame went from (55,55,101), (51,51,93), (59,59,75), (58,58,73) to
  (66,66,83), (60,60,76), (59,59,75), (58,58,73). **Only U8SHAPES moved**
  (`0db9dbe9…` → `a611e9be…`), so no detection change and no ScummVM
  rebuild; second build reproduced, estate 30/30. In-engine
  (`docs/playtest-2026-09-25-pillar-plinths.md`): four grey plinths in the
  pair plates and in one frame from beside the Earth pillar, `findShape
  865` still four `(uc: TYPEELEM)` items. Left: C2's block is one row
  taller than C3's at 96 px.

---

## Contract 6: the gold plaques (retail 599/614, class 1259), no new art

**What it is.** Wall signage in Cloud City, read by double-click in the
plaque gump. The class exists: `TypeNSGoldPlaque`, class 1259, pinned to
npcnum 235 (`PLAQUENS.UNK`), a quality table of 67 texts, all Pagan
signage except 66 (the Moriens birthplace) and 67 ("Through Flame Shall
All Be Released", unplaced). The item was blocked on text, not on art.

**No art is generated, and 867 stays free.** Retail has the plaque twice,
one per wall orientation: 599, footpad (0,2,2), for a west wall, and 614,
(2,0,2), for a north wall; both `SI_FIXED | SI_SOLID`. Each carries a retail
signage class at its own shape id, so an LV plaque must carry npcnum 235:
the engine's npcnum override sends every event to class 1259, and without
it shape 614 barks "plaque" and reads nothing, shape 599 reads retail's
own numbering. Retail hangs plaques 16 above the floor (Map 41).

**The text.** Three new qualities in `lv-patched/PLAQUENS.UNK`, each a
quote from the 1994 dialogue, English only as quality 67 is, approved by
Douglas 2026-09-25:

| q | Where | Text | Source |
|---|---|---|---|
| 68 | Arrival Plaza north wall (5055, 9217, 16), left of the way in | FORBIDDEN / TO / MORTALS | `THORDIS.UNK:1594`, "Forbidden to mortals, it is" |
| 69 | Main Plaza north wall (2495, 5121, 16), left of Hall A's doorway | FELICITAR / DOLORAS / TIMYRA | `EZREKAL.UNK:1536-1538`, the Shield's trio |
| 70 | Main Plaza north wall (5055, 5121, 16), left of Hall B's doorway | AMORAS / APATHAS / ODION | the same passage, the other trio |

Hall A gets the Shield's trio because its back room holds Odion's letter
to them. The plaque gump is 263x103 in font 10: 247 px of line width, 18 px
per line, no height limit, so a fifth line spills off the plate; the
longest line here is 110 px.

**Two more, 2026-09-25.** Quality 66 ("BIRTHPLACE OF MORIENS") hangs on a
one-course stub between the Moriens ruin's tall columns (Map 10, plaque at
(12255, 22208, 16)), and quality 55 ("ADMIRE BUT TOUCH NOT") on a one-piece
stele a tile south of the obelisk's dais (plaque at (4127, 7680, 16)); both
read in engine (`docs/playtest-2026-09-26-lamps-plaques-lb.md` P8, P9,
and the stele's position in `docs/playtest-2026-09-26-steps-15-18.md`).
The Scroll Chamber and Memorial Hall have candidate texts (Casera,
Gudbrand) whose tie to the room is invented, so they were not placed.

**Verification.** `map_validate` skips wall-hung fixed fixtures (their
anchor-as-centre support box reached the void plate beyond the Main
Plaza's wall); `map_pins.json` carries the three rows. In engine
(`docs/playtest-2026-09-25-ceremony-plaques.md`): each plaque hangs at head
height and barks "plaque" on a single click. The first build crashed on
double-click (`I_readPlaque: Assertion 'item' failed`): our same-class
spawn of `readPlaque()` passed a null `this`. `1b0bf9a` hands a spawned
method `this` when its body reads it, as retail does, and the retest read
all three texts with no crash (P5-P7).

---

## Contract 7: the wired obelisk (shape 861, retired 2026-10-17), nothing to make

**The queue row's condition never fires.** Row 7 has read "when MAGNET is
wired: a class at 861 if it needs `use()`, else nothing" since the queue was
written. Reading `MAGNET.UNK` end to end answers it: **else nothing**, and
wiring MAGNET does not change that.

`shared/data/lv-usecode/LOST VALE/MAGNET.UNK` is `eggclass EggMagnet inherits
Egg` with five processes, `hatch()`, `friskAvatar()`, `cleanSweep()`,
`leaveFastArea()`, and `killMagnet()`. Every one of them runs on the egg. The
obelisk appears in the file exactly twice, both times as the literal
destination of a `pop()`: `item.pop(15615, 19839, 120)` at `:225` and `:493`.
The class never finds the obelisk item, never sends it an event, and never
names its shape or type. Contract 1 already established the other half:
every `foreach` in the file filters an inventory type, so no `TYPE_SHAPES`
entry resolving to 861 is read either.

So shape 861 stays what contract 1 made it: art with no class, EUSECODE entry
863 empty, a double-click printing nothing. That silence was chosen over the
"chimney" the placeholder barked, and the MAGNET wiring gives no reason to
revisit it. A `look()` class at 861 is available on the same terms as the
pillars' (entry 863 is free, `MSGSCRL.UNK` is the pattern), and it is an
independent choice about whether Cloud City's centrepiece names itself.

**What MAGNET actually needs is not art.** The blockers are on `TODO.md`
(EGGMAGNET 281 plus EGGCANDLETRICK 280) and in
`docs/research/2026-07-25-design-fidelity.md` §2: the trigger egg at
`build_map_17.py:229` carries quality 3 where the convention `class_id −
0x47F` makes it 281; `CANTRK` has no explicit wait, so a naive loop fix hangs
the VM (H1); nothing in the build can light a candle and no candle art fits
the contract's frame-0-unlit requirement; and MAGNET's `pop()` target
(15615, 19839, 120) is nowhere near Map 17's obelisk at (4095, 7167, 16), so
either the obelisk moves to the 1994 coordinate or an `lv-patched/MAGNET.UNK`
retargets the pop. All four are usecode and map work.

**Verdict.** Item 7 is closed with no art and no class. It leaves the queue
as a pointer to the MAGNET wiring task, which belongs to the quest track.

### Record

- 2026-09-22. Closed on the source. `MAGNET.UNK` dispatches nothing from
  shape 861, so the row's conditional resolves to "nothing" whether or not
  MAGNET is ever wired. No shape ID consumed, no manifest pin taken, no
  rehash.
- 2026-10-17. Shape 861 is retired; the obelisk is screen11's retail
  composite, and the front drum carries quality 90 for the wiring. The
  verdict stands: MAGNET still dispatches nothing from the obelisk.

## Contract 8: the Tiny Tar body (shape 867)

**What it is.** The Avatar after a Tiny Tar potion: `POTION.UNK` frame 8
spawns `makeAvatarTiny()`, waits, and spawns `makeAvatarBig()`. Small
enough for the Map 18 crack (63 units of clear span; the body must be
32x32), the quest's only way into the Inner Sanctum. Today it is the child
actor 708 (queue row 8). Douglas, 2026-10-11: **the Avatar himself, scaled
down, derived by code from shape 1's own sprites, animated by shape 1's own
animation table, plus a generated shrink ramp.**

**What is made, and how.** No image model. Every frame is computed from
shape 1 by `agents/map-populator/src/lv_tiny_avatar_art.py`, so the build
can derive it from the base game at build time, as `lv_tiny_tar.py` does
for 859 and the elixir row does for 868: no build-input PNG, nothing
Origin-derived committed. There is no agy log to read and no 429-PIL
substitution to guard against.

### Findings that fix the design

1. **What the usecode does with 867.** Every use is in lv-patched
   `FREE.UNK`. `makeAvatarTiny()`: `turnToFace(southeast)` (:1388) on
   shape 1, `setType(TypeTinytar)` (:1397), `setFrame(60)` (:1398), a
   loop `setFrame(getFrame() + 1)` to 69 with two `wait(5)` per step
   (:1400-1412), `realDoAnim(AS_STAND, southeast)` (:1414).
   `makeAvatarBig()`: `turnToFace(southeast)` (:1437) on 867, the teleport
   round trip, `setFrame(69)` (:1470), a loop down to 60 with `touch()`
   (:1473-1486), then `setType(TypeAvatar)`, `setFrame(3)`,
   `realDoAnim(AS_STAND)` (:1488-1490); the failure branch sets
   `TypeAvatar` and frame 3 before it kills (:1457-1458). No compiled file
   compares the Avatar's type or shape (`grep` of lv-patched and lv-new for
   `getType`/`== TypeAvatar`). The Avatar's own events dispatch on
   objId + 1024, not on shape (`TODO.md` "Verified feasible"), so class 867
   needs nothing.
   While shrunk (~1,375 ticks, `TODO.md` "The Tiny Tar window") the player
   can still drink the other potions. Frame 6, sleep (`POTION.UNK`), plays
   `AS_FALL_DOWN` (14), `AS_GET_UP` (4), `AS_STAND`, and `AS_LOOK_LEFT` /
   `AS_LOOK_RIGHT` (32/33). Frame 5, protection, plays `AS_VERT_LEAP` (3).
   Frame 7, invisibility, does `setFrame(getFrame())`, which works in any
   layout. Map 10's `SHADES.UNK` adds `AS_KNEEL_DOWN`/`AS_KNEEL_UP` (49/50)
   if the potion is drunk there.
2. **708's layout cannot carry the ramp, and the ramp today is the child
   dying.** 708's `die` action is frames 51-56 / 57-62 / 63-68 / 69-74 for
   directions 0-3 (4-6 mirror 2-0), so frames 60-69 are death frames. 69
   also starts `stumbleBackwards` south-east (base `ANIM.DAT`, decoded with
   `lv_tiny_avatar_art.decode_anim`). What the shrink in the 2026-10-08
   playtest (T1) showed was the child: three frames lying flat, six frames
   falling, then standing at 69 (the `today` row of `ramp-3x.png`). A
   sprite "in 708's layout with 60-69 the shrink" would have broken `die`
   in five of the eight directions (1-5).
3. **708's table is 11 actions and shape 1's is 53.** 708 has walk, run,
   stand, ready/unready, attack, advance, retreat, stumble, die and
   combatStand (and run and advance are its walk). So on 867 today
   `AnimationTracker::init` finds no action (`animation_tracker.cpp:62-73`
   returns false) for every jump, climb, cast, look, kneel, get-up,
   edge-balance, kick and block. The sleep potion's get-up and looks, the
   protection potion's leap and SHADES' kneel all fail silently today, and
   the tiny Avatar cannot jump. On shape 1's table they all play.
4. **Shape 1's table touches the ramp range only at 60-67**, walk direction 5
   (south-west). Every walk direction is frames 10d+10 ... 10d+17; 68 and
   69 are named by no action. So the collision is eight frames, and moving
   them is a frame-number rewrite in 867's own table. The usecode is
   untouched.
5. **The engine does nothing else by shape here.** The weapon overlay is
   drawn only for `_shapeNum == 1` (`item_sorter.cpp:502`), so a shrunk
   Avatar in combat shows no weapon, as today. The full-size overlay would
   be the wrong size anyway. `wpnovlay.dat` is indexed by shape 1's action
   lengths (`wpn_ovlay_dat.cpp:66-70`) and is never consulted for 867. The
   shape 1 special case in `Actor::receiveHit` (`actor.cpp:1029`) is
   skipped while shrunk, as today.
6. **Size.** Shape 1's stands are 49-51 px tall, 19-29 wide; the child's
   are 30 tall, 10-12 wide, a ratio of 0.6. The child's walk cycle travels
   30 deltaDir units against shape 1's 52 (0.58). Shape 1's footpad
   (2,2,5) is 64x64x40 and the tiny box (1,1,4) is 32x32x32, which
   projects to 16 px wide and 40 px tall (`iso_render` projection). The
   ramp ends at the tiny body's own stand frame, so "match the child" and
   "the ramp's end size" are one number: **0.6** is the default and 0.5 /
   0.7 are the alternatives.
7. **Palette and outline.** Shape 1 uses 213 palette indices, and every
   silhouette-edge pixel of frame 3 is index 0, black. Downscaling can
   either point-sample the indices or average colour and re-quantize. The
   re-quantizer is restricted to the Avatar's own 213 indices, so no
   foreign hue appears. Averaging smears the black outline into the edge
   colours, so the third method treats index 0 as line work and redraws
   it.

### Engine identity

| | |
|---|---|
| Shape | **867**, pinned literally: a save made while shrunk stores the shape (`test_tiny_tar.py` 4b). A save made before 2026-10-11, in 708's layout, loads showing whichever shape-1-layout frame has its number until the next animation. Harmless. |
| Frames | **1558.** 0-1549 are shape 1's frames, each scaled by *s* about its own anchor, except **60-69, the shrink ramp**. 1550-1557 are shape 1's 60-67 scaled (tiny walk SW). |
| Ramp | Ten frames of shape 1 frame 3 (stand, SE: makeAvatarTiny faces southeast first, and makeAvatarBig ends on `setFrame(3)`). The scales run geometrically from 1 to *s*, *s*^(k/9). **60 is shape 1 frame 3 verbatim** and **69 is exactly the tiny body's frame 3**, so neither `setType` swap nor `AS_STAND` pops. 61-68 carry the R2 glow: the colour blended toward (210, 235, 255) by 0.4·sin(πk/9) and quantized over the whole palette. It runs at 10 ticks a step, as FREE times it. |
| Anchor | shape 1's anchors scaled: output pixel U covers source anchor coordinates [U/s, (U+1)/s), so feet stay on the anchor in every frame and nothing jitters between frames |
| TYPEFLAG | **unchanged**: today's row `22601041000101fa`, i.e. 708's flags and family (the same flag word as shape 1's), footpad **(1,1,4)** (the crack, sanctum and hatch-box tests size the tiny body as 32x32x32), and shape 1's weight 1 / volume 250 |
| `ANIM.DAT` | **its own action table**, appended (`avatar_anim_table`): shape 1's 53 actions with frame numbers 60-67 rewritten to 1550-1557, and every frame's deltaDir scaled by *s* with cumulative rounding per direction, so a cycle's total travel is shape 1's × *s* and the feet stay planted. Headers, deltaZ (climb heights are world geometry), sfx and frame flags (attack range included) are shape 1's. The file grows 402,184 → 425,740 bytes. |
| Usecode class 867 | none, as today |
| `TYPE_SHAPES` | **no change.** `TypeTinytar` and `TypeTinyAvatar` are already 867 (`u8c_symbols.py:403`, `:624`), and no usecode changes |

**Gameplay consequences of shape 1's table.** These come with Douglas's
choice of the Avatar's table, so they are not open, but they need testing:

- **The tiny Avatar can jump and climb.** The climb heights are the
  full-size ones (deltaZ is not scaled). The sanctum hardening is
  height-based (120-tall stacks beat 46 + 72, `build_map_18.py:894-899`),
  so it holds for any body [INFERENCE: not yet tried in-engine with a
  jumping tiny Avatar].
- **Walking speed.** Shape 1's walk runs at frame repeat 1 and 708's at 2.
  At *s* = 0.6 a walk cycle travels 31 units of deltaDir (124 world units),
  against the child's 30 (120), in half the ticks. Each push therefore
  moves about as far as the verified crack passage did (28-64 units per
  push, `TODO.md`), but the tiny Avatar walks about twice as fast
  [INFERENCE from the tables].

### Candidates (picked 2026-10-11: O60, R2, scaled stride)

All five were made by `tools/art/tiny_avatar_plates.py` and went through
the real pipeline: `encode_frame`/`encode_shape_blobs`, `validate_shape`
clean on all 1558 frames, `inject_shape` into a scratch copy of the
pristine `U8SHAPES.FLX` at 867, the slot read back byte-equal, and
`avatar_anim_table` into a scratch `ANIM.DAT`. Every plate is drawn from
the read-back bytes, through 867's own decoded table.

| ID | Method | Scale | Stand size | Blob | One line |
|---|---|---|---|---|---|
| N60 | nearest | 0.6 | 29-31 × 12-17 | 596,022 | point-sampled indices: exact palette, crisp, but the outline breaks and thin details flicker frame to frame |
| A60 | area | 0.6 | 29-31 × 12-17 | 594,263 | box-filtered colour re-quantized to the Avatar's indices: smoothest, but the edge goes grey and the figure softens |
| **O60** | outline | 0.6 | 29-31 × 12-17 | 594,263 | area colour without the black, then a fresh 1-px index-0 edge: reads most like a U8 sprite at 1x. **Picked.** |
| O50 | outline | 0.5 | 25-26 × 10-15 | 467,841 | half size, the footpad's ratio: unmistakably tiny, smaller than the child |
| O70 | outline | 0.7 | 35-36 × 13-21 | 762,858 | fills the (1,1,4) box's 40 px; more detail, but barely smaller than a Map 10 villager child |

Ramps: **R1**, the plain shrink (each candidate's own); **R2**, the same
with a pale-blue magical tint peaking mid-shrink (sine envelope, peak 0.4,
quantized over the whole palette, not only the Avatar's indices). It is
zero at both ends, so the joins are unchanged. A third choice: **stride**
scaled by *s* (the feet plant) or kept at 1.0 (full speed on short legs:
the feet skate). Douglas picked O60, R2 and the scaled stride.

Plates, `shared/docs/art-poc/tiny-avatar/`:

- `compare-4x.png`, `compare-1x.png`: stand in 8 directions. Shape 1, 867
  before (708), then each candidate, anchors on one baseline.
- `walk-<ID>-3x.png`: walk, 8 directions × 8 frames, shape 1 beside the
  candidate. Direction 5 (row 6) comes from the relocated 1550-1557.
  `walk-<ID>.gif` animates both.
- `ramp-3x.png`, `ramp-1x.png`: shape 1 frame 3, then 60-69, then the tiny
  stand (867's table), for every candidate and for O60 with R2, under a
  `before` row: 708's frames 60-69, what the shrink showed until the pick.
  `ramp-O60-glow.gif` is the shipped shrink at FREE's pace, and
  `ramp-O60.gif` the plain one.
- `crack-1x.png`: the Map 18 crack from `build_map_18`'s own hall and
  sanctum builders, with the full-size Avatar, the tiny body in the crack
  at x 2852 (the verified position) and the child 708, before and for each
  candidate. `crack-<ID>-2x.png` is the same at 2x. `void_floor` is left
  out because it needs a built TYPEFLAG.

### Build, tests, verification

- **Build.** `lv_tiny_avatar.py` (step 6/8) builds 867 with
  `lv_tiny_avatar_art.build_tiny_avatar`: shape 1 and `ANIM.DAT` from the
  pristine base, at the pick (`SCALE` 0.6, `METHOD` outline, `GLOW` 0.4,
  `STRIDE` 0.6, all in `lv_tiny_avatar_art.py`), about 8 s. Its `_verify`
  refuses the staged outputs unless slot 867 is the derived blob of 1558
  frames, the ramp displaced exactly 60-67 to 1550-1557, 867's table is
  appended with shape 1's action set, names no frame past 1557 and no ramp
  frame, and every other byte of all three files is untouched.
  `clone_anim_entry` stays in `lv_tiny_avatar.py` for item 9, whose art
  keeps its donors' frame numbers.
- **The scaling is fixed point.** The blending sums run in int64 (weights
  in 1/4096, linear light in 1/65536), not float matrix products. A float
  matmul goes to BLAS, whose summation order depends on the CPU kernel, and
  the canonical hash cannot. Against the float version that made the
  plates, 129 of the body's 725,055 pixels differ (124 frames) and no
  frame's size or anchor does. The plates were regenerated from the
  fixed-point code: `ramp-O60-glow.gif` came out byte-identical, and the
  O60 walk plates moved by those pixels.
- **Tests.** `test_lv_tiny_avatar_art.py`, 40 checks on the pristine base.
  The table is shape 1's with only 60-67 renumbered, no action reaches
  60-69, travel scales exactly, and `actor_anim` decodes it. The ramp's
  ends equal shape 1 frame 3 and the tiny frame 3. Scaling is anchor-true,
  and the outline edge is index 0. Section 4 pins the pick, and checks
  that the glow keeps the ends and the geometry and pales 61-68.
  `test_tiny_tar.py` 4b, on the built artifacts: 1558 frames,
  `validate_shape` clean, frame 60 = shape 1 frame 3, 69 = the tiny frame
  3, the ramp never grows, frames 0-7 and 1550-1557 equal the derivation
  of shape 1's 0-7 and 60-67, the TYPEFLAG row as before, the built
  `ANIM.DAT` byte-equal to `avatar_anim_table(pristine, 60-67 → 1550-1557,
  0.6)`, a walk cycle travels 0.6 of the Avatar's in all 8 directions,
  and 867 has the jump, die, get-up, look and kneel actions.
- **In ScummVM, outstanding** (the 2026-10-08 T1-T6 again, plus the new
  capabilities): the shrink and regrow play the glow ramp with no pop at
  either end; walk and run in all 8 directions, SW included; the crack
  passage at x 2852; jump and climb while tiny at the crack wall and the
  sanctum boundary (they must still refuse); the sleep and protection
  potions while tiny; regrow to shape 1; save and load while shrunk; the
  708 children unchanged.

### Record

- 2026-10-11. Phase 1: contract, derivation module, plate script, plates
  and the pick-independent test.
- 2026-10-11. Douglas picked O60, R2 and the scaled stride. Landed:
  `lv_tiny_avatar.py` builds the derived body and its own table;
  `test_tiny_tar.py` 4b rewritten; the fixed-point scaling; section 4 of
  `test_lv_tiny_avatar_art.py`. Rehashed with `tools/build_artifacts.sh
  --record`: U8SHAPES 15,621,450 → 16,183,942 bytes, `95e786a5…`; ANIM
  402,184 → 425,740, `c2e27898…`. TYPEFLAG `6bdb3036…`, EUSECODE
  `4182e079…` and FIXED `122b4374…` did not move, and a second clean
  build reproduced all five. `derive_map_pins.py` left `map_pins.json`
  unchanged. Not yet run in ScummVM.

## Contract 11: Tyorvi's elixir (shape 868)

**What it is.** The brew Ezrekal makes from the root for Tyorvi's
nightmares (quest steps 11-12): she hands it over on "Have you made the
elixir?" and he drinks it on "Just try it, please." or "Shut up and drink
it!", which opens the Key to the Clouds. All four sites name it
`TypeBottle` (lv-patched `EZREKAL.UNK` give/createNear, `TYORVI.UNK` the two
drink filters), and those are the identifier's only compiled uses.

**Why it needed a shape.** It was shape 395 frame 5 from 2026-10-08 (frame
13 of 395 drew as a shard). Frames 0-5 of 395 are the necromancy reagent
Blood, `SF_REAGENT`, so the elixir read "1 vial of blood", merged with any
blood the Avatar carried (`Item::canMergeWith` merges a reagent of the same
shape and frame, and treats 395's blood frames 0-5 as one), and Tyorvi's
drink destroyed every carried frame-5
blood with it. Douglas's decision, 2026-10-09: its own shape.

**Engine identity.**

| | |
|---|---|
| Shape | **868** (867 is the Tiny Tar body; `.claude/rules/shape-ids.md`) |
| Frames | 1. The art is 395 frame 5 with its red liquid (palette 41-46) walked tone for tone onto the sea-green ramp 85-92; glass, cork, outline and mask are the vial's own, so it reads as the same vial with a different brew. Built from the base vial at build time (no build-input PNG, `lv_tiny_tar.py`'s approach for 859). No frame of the potion 766 or of 395 uses that ramp, so it is not blood and not a potion. |
| TYPEFLAG donor | **180**, the engine's bottle: `SI_SOLID`, `SF_GENERIC`, footpad (1,1,1), weight 1, volume 1, the same entry as 395 except the family. Carryable (no `SI_FIXED`), and not `SF_QUANTITY` or `SF_REAGENT`, so it never stacks and no reagent code sees it. The potion 766 carries a byte-identical entry; 180 is taken because it is the shape retail's own `TypeBottle` names (JENNA, 0x0418). |
| Anchor | the vial's own (3,10) |
| Usecode class 868 | **compiled** (`lv-new/ELIXIR.UNK`, `TYPEELIXIR` pinned to 0x0364): `look()` barks "Tyorvi's elixir", the name Ezrekal's own menu uses. No `use()`: a double-click does nothing, as before. |
| `TYPE_SHAPES` | **`TypeBottle` 395 → 868**, frame 0 at all four sites (lv-patched EZREKAL/TYORVI V3). Retail JENNA's `TypeBottle` (180) is not recompiled. |
| Quantity | 1, unchanged (EZREKAL V2). For a non-quantity family `FREE::give` runs `quan--; while quan`, so a 0 would create items until the pack refused one. |

**Placement.** None. The elixir exists only between Ezrekal's give and
Tyorvi's drink.

**Verification.** `test_art_props.py` section 9 (the pair with
`TYPE_SHAPES`, the donor's TYPEFLAG row, not a reagent or quantity family,
the pixels equal the vial's through the remap, no 766 or 395 frame uses the
new colours, placed on no map, the pin, class 868 barks its name) and
`test_uc_dialogue.py` D12c/D12d (EZREKAL creates 868 frame 0 quantity 1;
both drink paths consume it, leave carried blood of frames 5 and 0, and
reach the Key; both compiled filters search 868 frame 0). In-engine:
Ezrekal's hand-over puts a sea-green vial in the pack that clicks as
"Tyorvi's elixir" and does not join a stack of blood; either drink takes it
and the Key follows.

### Record

- 2026-10-09. Landed: the `lv_art_props.py` row (a `recolour` key beside
  `frames`, the table's first derived-art row), `SHAPE_ELIXIR` in
  `lv_shapes.py`, `lv-new/ELIXIR.UNK` and its pin, the `TypeBottle`
  re-point, lv-patched EZREKAL/TYORVI V3, and the plate
  `shared/docs/art-poc/elixir/elixir-plate.png` (`tools/art/elixir_plate.py`:
  the elixir beside the blood vial and the eight potions, 1x and 6x).
  Rehashed: `TYPEFLAG`, `U8SHAPES` and `EUSECODE` moved; `ANIM` and `FIXED`
  did not.

---

## Contract 10: the Shield halves (shape 870, a legacy alias of 878 since 2026-10-17)

**What it is.** The two halves of the Shield of the Ancients, found by the
skeletons of the two missing boys in Cloud City's Memorial Hall (Plot v1.2
beat 13, `story-beats.yaml:281`), carried to the Sacred Circle, and fused
by Ezrekal's ceremony (`lv-patched/SHADES.UNK`) into the restored Shield,
retail shape **828** quality 83 at the time of this contract; since
2026-10-17 it is **879**, the 1994 Shield screen04 shows on the altar
(`TypeSacredShield`, class 879 `lv-new/SACSHLD.UNK`). The 1994 Art List
says what they look like: "Magic Frisbee half (like Zealan Ceremonial
Shield)" and "Magic Frisbee other half" (`items.yaml:97`, `:107`), and
"Zealan ceremonial shield" is 828's own retail name (class 828 AORTA).
So the halves are not a design choice: they are 828 broken in two.

**What 828 is, read off its pixels.** 30x28, anchor (6,32), footpad
(1,3,3): a shield standing on its rim, a blue border (0x9C outer,
0x8B-0x8F inner) round a black face, divided by blue bars in a Y into
**three** fields: a tan hand with a red heart on the left, a red blade at
the top right, a violet glyph at the bottom (palette dump of 828 frame 0,
2026-10-11). `lv_shapes.py:851`'s "quartered with the four elemental
sigils" is wrong on both counts. The Y's upright is column 15 from the top
rim to the junction at row 14, so that is where the Shield parts: the left
half carries the hand and the glyph's left side, the right half the blade
and the glyph's right side.

**What is wrong with it today.** Both halves are retail 539 "shield"
frames 0 and 1 on Map 17 (`build_map_17.py:526-541`), a grey studded kite
shield and a bigger one, neither a half of anything. Two engine-side
defects ride on that shape as well:

- **Any Pagan shield is "half 1".** The new game's NONFIXED.DAT places ten
  539 frame-0 shields (U8SAVE.000, counted 2026-10-11), and SHADES finds
  the halves by `type = TypeAOFrizbee` (539) and `getFrame() = 0` / `= 1`
  inside the backpack (`lv-patched/SHADES.UNK:138-150`). A player who
  brings a shield from Pagan and one real half passes the check, and the
  ceremony destroys the Pagan shield as `Frizbee1`.
- **539 is a shield-slot item.** Its TYPEFLAG row is equipType shield, and
  the paperdoll draws an equipped item's frame + 1
  (`paperdoll_gump.cpp:202`) and dereferences that frame unchecked on a
  click (`:248-250`). On 539 a worn half 1 draws as half 2; on a
  two-frame shape a worn half 2 would dereference a frame that does not
  exist. So the new shape must not be equippable, which rules 539 out as
  the donor.

**Engine identity.**

| | |
|---|---|
| Shape | **870** (869 the special root, 871 the Passage Test plant) |
| Frames | **2, and the order is load-bearing**: frame 0 the LEFT half (half 1, quality 81, Snori's), frame 1 the RIGHT half (half 2, quality 82, Hoskuld's). `SHADES.UNK:47/:52` (original lines) tell them apart by `getFrame() = 0` and `= 1`, and ZEALSHLD's look() barks "broken shield" for both. Frames 2-4 must NOT exist: SHADES's `create(TypeAOFrizbee, 4)` invisible anchor relies on a missing frame and is destroyed at once (`lv-patched/SHADES.UNK:440-450`), as on 539. |
| Art | **derived, not generated**: 828 frame 0's own palette indices, split on column 15. Built at build time from the base shape, the way 868 is recoloured from 395 (no build-input PNG, so no Origin pixel is committed): a `split` row key in `lv_art_props.py` beside `frames` and `recolour`. |
| TYPEFLAG donor | **828**: `SI_SOLID`, `SF_GENERIC`, no equip slot, weight 3, volume 10. Carryable (no `SI_FIXED`), not a quantity or reagent family, so the halves never merge (`Item::canMergeWith`, `item.cpp:2558-2565`). |
| Footpad | **(1,1,3)**, a 16x32 screen box: each half is 16x27 / 15x26 (A and C). The donor's (1,3,3) is the whole Shield's. |
| Anchor | bottom-centre (`xoff=w/2, yoff=h`), the prop convention. 828's own (6,32) belongs to its (1,3) box. |
| Usecode class 870 | **none, and none can run.** Both halves carry npcnum 236, which the LV hunk in `Item::callUsecodeEvent` turns into class 1260 TYPEAOFRIZBEE (`build_map_17.py:127-136`); the shape carries no usecode meaning. |
| `TYPE_SHAPES` | **`TypeAOFrizbee` 539 → 870.** Compiled consumers: `lv-patched/SHADES.UNK:138` (the backpack search, frames 0/1) and `:440` (the frame-4 anchor). `TypeAOArtifact` stays 828. |

**Placement, unchanged.** Half 1 frame 0 at (6208, 1568, 0) and half 2
frame 1 at (7232, 1568, 0), qualities 81/82, npcnum 236, by the two
skeletons. Both coordinates are route goals (`test_route_reach.py:967-968`).

**Phase 2 change list** (after the pick; nothing here fixes an art
choice, but every item needs shape 870 to exist, and the re-point moves
`EUSECODE.FLX`, whose cascade runs through `build_scummvm.sh`):

1. `lv_shapes.py`: `SHAPE_SHIELD_HALVES = 870`; `build_map_17.py:118`
   `SHAPE_TALISMAN` points at it, comments at `:101-117` rewritten.
   `SHAPE_SHIELD = 539` stays the retail shield.
2. `lv_art_props.py`: a row `{'shape': 870, 'donor': 828, 'footpad':
   (1,1,3), 'split': (828, 0, <variant>)}` and the `split` key, carrying
   `tools/art/static_items.split_828`'s rule.
3. `u8c_symbols.py:426` `TypeAOFrizbee` → 870, its comment block
   (`:406-425`) rewritten.
4. Tests: `test_route_reach.py:235` `USE_SHAPES` 539 → 870;
   `test_uc_shades.py:68` keeps following `TYPE_SHAPES`, but its "old 539
   frame 2" checks (`:185`, `:354-358`) must name 539 literally, not
   `SHIELD_SHAPE`; `test_art_props.py` section 10 (two frames, each equal
   to 828 split on column 15, donor row, non-equip, both halves placed with
   frames 0/1, qualities 81/82, npcnum 236, no 539 on Map 17, a backpack
   holding a Pagan 539 frame 0 and half 2 fails SHADES's check).
5. `derive_map_pins.py` follows `TYPE_SHAPES` by itself; re-derive
   `map_pins.json` after the FIXED build.

**Unblocked, not done here.** `TypeShields` is held at 587 instead of
retail 539 only because half 1 was 539 frame 0 (`u8c_symbols.py:255-260`:
EZREKAL's "I have the Ancient Shield." forgery check would have matched
it). Once the halves leave 539 that reason is gone.

**Verification.** `test_art_props` section 10 and `test_uc_shades` green,
route 17 green; in-engine: both halves read "broken shield", carry, show in
the pack, refuse the shield slot, and the ceremony consumes exactly the two
of them and leaves a carried Pagan shield alone.

### Record

- 2026-10-11. Contract written; three candidates cut from 828 by
  `tools/art/static_items.py halves`, one axis each: **A** a straight break
  on column 15 with a one-pixel dark edge, **B** the same line made jagged
  (a 2-px zigzag), **C** A's line with each half finished in 828's own
  two-tone rim. Plates: `shared/docs/art-poc/shield-halves/`.
- 2026-10-11, later. **Douglas picked B** (the zigzag break). Landed: the
  `split` row key in `lv_art_props.py` (`split_frame`, `build_split`; 828
  frame 0 split on column 15 along the zigzag, frames anchored
  bottom-centre, 18x27 and 17x26), `SHAPE_SHIELD_HALVES` in `lv_shapes.py`
  (replacing `SHAPE_SHIELD`), `build_map_17.py`'s `SHAPE_TALISMAN`,
  `TypeAOFrizbee` 539 → 870, `test_route_reach` `USE_SHAPES`,
  `test_uc_shades` naming 539 literally, and `test_art_props` section 10.
  Rehashed with the other two items (contract 13's Record).
- 2026-10-17. **Retired.** The 1994 halves were cut from screen11 (the
  sun half) and screen12 (the eye half) and are shape 878; `TypeAOFrizbee`
  went 870 → 878 and Map 17 places them where the shots do. The `split`
  row key (`split_frame`, `build_split`), `SHAPE_SHIELD_HALVES_828_SPLIT`,
  the `shield-halves` item and `halves` command of
  `tools/art/static_items.py`, and `shared/docs/art-poc/shield-halves/` are
  gone (git history keeps them); 870 went into
  `lv_shapes.RETIRED_SHAPE_IDS`, its slots left the base game's.
- 2026-10-17, later. **Un-retired as a legacy alias of 878.** Verify3
  (`docs/playtest-2026-10-17-vignettes-verify3.md`, claim 2) loaded a save
  holding the halves as 870 in the pack: pressing `i` aborted ScummVM
  (`ContainerGump::run(): Assertion 'sh' failed`), and the halves SHADES
  laid down drew nothing (`Skipping invalid shape in sorter: 870,0!`).
  The halves are carryable, so unlike the fixed 861/862 they follow the
  player into any save. 870 left `RETIRED_SHAPE_IDS` and became
  `lv_shapes.SHAPE_SHIELD_HALVES_LEGACY`, a `copy` row in
  `lv_art_props.py` after 878's: 878's two frames verbatim, on donor 878
  with 878's (1,3,3), so the TYPEFLAG row is 878's byte for byte (and
  `build_copy` reads the source from the run's own output). No map places
  870, no `TYPE_SHAPES` entry or class names it, and `test_art_props.py`
  section 14 asserts the copy. The number is still never reused.

---

## Contract 12: the special root (shape 869)

**What it is.** The root Ezrekal brews into Tyorvi's elixir (quest steps
9-12). Her grandmother's bitter tea "Made from a root this tea was", and
"By the standing stones it grew" (`LOST VALE/EZREKAL.UNK:3108`); the
Avatar finds it by the Sacred Circle's east stone, picks it up, and hands
it in ("I have found the root."), and she destroys it. Asked what it looks
like she says: **"Brightly colored I think it was, maybe purple."**
(`LOST VALE/EZREKAL.UNK:3142`). No 1994 art.

**What is wrong with it today.** It is shape 399 frame 9, "eye of newt"
(`lv_shapes.py:437`), a green-and-brown vine that reads as a coiled snake,
19x16. Its retail class is non-empty and the engine names the shape "eye
of newt" (`shape_names.engine_name(399)`), and
399's TYPEFLAG row carries `SI_TRANSL`, so the engine draws it
translucent (`item_sorter.cpp:174`; ScummVM's tree), and `SI_NOISY`. `TYPE_SHAPES` notes
the purple mismatch as a known cosmetic (`u8c_symbols.py:666-668`).

**Engine identity.**

| | |
|---|---|
| Shape | **869** |
| Frames | **1.** The root is frame 0, so Ezrekal's two filters change 9 → 0 (below), contract 11's precedent for the elixir (frame 5 → 0). |
| TYPEFLAG donor | **180**, the engine's bottle and the elixir's donor: `SI_SOLID`, `SF_GENERIC`, weight 1, volume 1. That is 399's own row without `SI_NOISY` and `SI_TRANSL`. Carryable, not a reagent, never merges. |
| Footpad | **(2,2,1)**, a 32x24 box for a ~16-px-tall root lying on the ground (the Message Scroll's footpad), not the donor's (1,1,1), whose 16-px box is narrower than the art. 8 units tall, so it steps like the grass round it. |
| Anchor | bottom-centre |
| Usecode class 869 | **compiled**, decided here: `lv-new/SPROOT.UNK`, `typeclass TypeSpecialRoot`, `look()` barks "special root" (the record's name, `items.yaml:143`), no `use()`. `TYPESPECIALROOT` pinned to 869 in `lv_manifest.json` (class entry 869 is empty in today's EUSECODE). Without it the shape is silent, which beats "eye of newt" but leaves the one quest item a player must find nameless. |
| `TYPE_SHAPES` | **`TypeWeedz` 399 → 869**, frame 0. Its only compiled uses are the two filters below. |
| Usecode change | `lv-patched/EZREKAL.UNK:710` and `:3584` (original lines 364 and 3168): `(type = TypeWeedz) and (frame = 9)` → `(frame = 0)`, a new header entry beside V3. The menu-detect and the hand-in destroy must agree, as TYORVI's two filters had to for 868. |

**Placement, unchanged.** (21376, 16640, 0), quality 0, frame 0 (was 9),
by the east stone (`build_map_10.py:1380-1383`).

**The colour is the open question, and it is candidate B's axis.** The
brief asks for a pale root; Ezrekal's only line says brightly coloured,
maybe purple. A follows the brief, B the 1994 line, C keeps A's pale root
and puts the purple in a small leaf tuft.

**Phase 2 change list.**

1. `lv_shapes.py:437` `SHAPE_SPECIAL_ROOT = 869`; `build_map_10.py:1382`
   frame 9 → 0 and the comment above it; `map_walkability.py:899`
   `MAP10_ROOT_SHAPE` from `SHAPE_SPECIAL_ROOT`, `:1140-1145` frame 9 → 0.
2. `lv_art_props.py` row `{'shape': 869, 'donor': 180, 'footpad':
   (2,2,1), 'frames': [('special-root/<pick>_raw.png', 16, MAGENTA, 130,
   16)]}`, the last element 0 for B or C (despill, Record below).
3. `u8c_symbols.py:669` `TypeWeedz` → 869, comment `:645-668` rewritten.
4. `lv-patched/EZREKAL.UNK` the two filters and the header entry;
   `lv-new/SPROOT.UNK`; the manifest pin.
5. Tests: `test_uc_dialogue.py:399-400` (== 869), `:436-444` and
   `:472-481` frame 9 → 0, plus a check that a carried 399 frame 9 neither
   offers "I have found the root." nor is destroyed; `test_art_props.py`
   section 11 (shape, donor row, one item on Map 10 at frame 0, no 399 on
   Map 10, the pin, class 869 barks its name).
6. `derive_map_pins.py:312` follows `TYPE_SHAPES`; re-derive.

**Verification.** The tests above, `map_walkability` Map 10 (e), and
in-engine: the root is visible from the circle, single-clicks as "special
root", carries, and Ezrekal takes it.

### Record

- 2026-10-11. Contract written; three candidates through `agy`
  (`tools/art/gen_special_root.sh`, the base reagents 395/399 as the
  reference), one axis each: **A** pale, an ivory gnarled taproot with two
  forks, 21x16 at game scale; **B** the same root violet, Ezrekal's colour,
  18x16, which U8PAL turns hot pink at 1x; **C** A's root with a small
  violet leaf tuft at the cut end, 17x16. The three logs read clean.
  **Purple art needs despill 0:** the build recipe's hue-based despill
  (margin 16) ate 102 of B's pixels and 11 of C's leaf pixels, so their
  rows would carry margin 0 (the frame tuple's fifth element). Plates:
  `shared/docs/art-poc/special-root/` (`compare.png`, `site-*.png`).
- 2026-10-11, later. **Douglas picked C** (the pale root with violet
  leaves). Landed: the row (despill 0), `SHAPE_SPECIAL_ROOT` 399 → 869 and
  frame 0 on Map 10, `lv-new/SPROOT.UNK` with `TYPESPECIALROOT` pinned to
  869 (0x0365), `TypeWeedz` → 869, lv-patched EZREKAL R2 (both filters
  frame 0), `map_walkability` (e) at frame 0, `test_uc_dialogue` (a carried
  399 frame 9 is no longer the root), `test_art_props` section 11.

---

## Contract 13: the Passage Test plant (shape 871)

**What it is.** The "Test of Rutabaga": "a nasty plant with delectable
fruit at its heart, guarded by long poisonous spines" (Plot v1.2, beat 8,
`story-beats.yaml:161-167`), the Art List's "Test Tree/plant/fruit"
(`items.yaml:224`). On Map 10's test grounds the Avatar walks up to it
with the Passage stone; `EggPlantTest` (`lv-patched/PLNTST.UNK`) blows it
away, teleports him into the vision, and pops five more of it across the
plateau (`:105`, `:121`, `:137`, `:153`, `:169`). `EggReapply` destroys the
quality-10 one again on every return (`lv-new/REAPPLY.UNK:97-106`). In the
1994 design the plant was its own class with a look() of **"Strange
plant"** (`LOST VALE/TESTPLAN.UNK:20`) and a three-frame burst
(`setFrame(1)`, `setFrame(2)`, `:34-36`).

**What is wrong with it today.** Shape 126 frame 0 is not a plant: it is
a 62x32 blue-crystal ground patch, `SI_FIXED | SI_SOLID | SI_LAND`,
footpad (4,4,1), that the Avatar walks over (render 2026-10-11).
`lv_shapes.py:114` names it `SHAPE_VEGETATION_SPARSE`, "UNVERIFIED — named
from usage", and the name is wrong. Entry 126 of EUSECODE is empty, so a
click prints nothing.

**Engine identity.**

| | |
|---|---|
| Shape | **871** |
| Frames | **1.** The restored scene destroys the plant (`PLNTST.UNK:72-76`) rather than playing TESTPLAN's burst, so frames 1-2 would need a PLNTST change; not in this contract. |
| TYPEFLAG donor | **65**, the mushroom cluster Map 10 already places: `SI_FIXED | SI_SOLID`, `SF_GENERIC`, no `SI_LAND`. Fixed, so neither the placed plant nor the five created ones can be picked up (126 was fixed too); solid, so it is walked round, not over. |
| Footpad | **(3,3,4)**, a 48x56 box, 96x96x32 world units. Three tiles is the largest the 1994 pop coordinates allow: the five created plants sit 96 or 128 units apart, so 3x3 boxes only touch (half-open), and 4x4 ones would overlap. 32 tall is under the 48 that makes a climb (`.claude/rules/shape-ids.md`). |
| Height | **48 px**, beside a 50-px Avatar (shape 1 frame 0) and the 55-px mushroom 65 on the same map. |
| Anchor | bottom-centre |
| Usecode class 871 | **compiled**: `lv-new/TESTPLNT.UNK`, `typeclass TypeTestPlant`, `look()` barks the 1994 "Strange plant", no `use()` (the egg runs the scene). `TYPETESTPLANT` pinned to 871. `TypePoisonPlant` itself is already pinned to 1436 (`lv_manifest.json`), where no item can dispatch it, and pins never renumber, so the look() text moves to a new class at the shape number. The five vision plants share the shape and bark the same. |
| `TYPE_SHAPES` | **`TypeShortmushroom` 126 → 871** (`u8c_symbols.py:583`). Compiled consumers: `PLNTST.UNK:72` (the destroy, frame 0, within 100 cells of the egg), its five `create(TypeShortmushroom, 0)`, `REAPPLY.UNK:99-101` (quality 10, frame 0), and the dead TESTPLAN class 1436's own creates. **`TypePoisonPlant` 126 → 871** too (`:637`): it is the 1994 name of this very plant, and nothing evaluates it as a value (a grep of the compiled tree finds it only in `typeclass`/`process` headers), so the bytecode does not move for it. |
| The other 126s | **One on Map 10, the 1994 shot's own.** Since phase B (2026-10-16) screenshot 21's vignette places 126:13, a walkable tile in its frame that no usecode reads (`test_art_props` allows a 126 only where a shot places one); the Test Plant itself is 871. Before that, the placed Test Plant was the only 126 on Maps 9, 10, 11, 13, 17 and 18 (FIXED.DAT 122b4374, counted 2026-10-11). Maps 8 and 39 carry retail 126 tiles (5 and 27), which no builder places and no compiled LV filter reads; they are not touched. |

**Placement, unchanged.** (12800, 29408, 64), frame 0, quality 10
(`build_map_10.py:1195-1198`). The box x (12704, 12800], y (29312,
29408] stays clear of the PLNTST egg at (12800, 29440) and of the route
goal at (12800, 29300, 64) (`test_route_reach.py:1215-1216`); the egg's
±128 hatch box still has open ground on three sides.

**Phase 2 change list.**

1. `lv_shapes.py`: `SHAPE_TEST_PLANT = 871`; `build_map_10.py:1197` uses
   it. `SHAPE_VEGETATION_SPARSE` gets its true name or goes, since this was
   its only use (`build_map_10.py:78`).
2. `lv_art_props.py` row `{'shape': 871, 'donor': 65, 'footpad': (3,3,4),
   'frames': [('test-plant/<pick>_raw.png', 48, MAGENTA, 130, 0)]}`:
   despill 0, whichever is picked (Record below).
3. `u8c_symbols.py:583`, `:637` → 871; `lv-new/TESTPLNT.UNK`; the pin.
4. `map_walkability.py:894` `MAP10_PLANT_SHAPE` → `SHAPE_TEST_PLANT`, and
   the two checks that stand ON the plant's point (`:1104-1111`,
   "on the z=64 plateau floor", and the flood at `:1117-1127`) become
   `check_support` on the plant, as the root's is: a solid plant blocks
   its own point, where the walkable 126 tile did not. Messages at
   `:1007-1012` name the shape.
5. Tests: `test_uc_plntst.py:55`/`:86` and `test_uc_reentry.py:79`/`:246`
   follow `TYPE_SHAPES` (labels say 126); `test_art_props.py` section 12
   (shape, donor row, the one item at (12800, 29408, 64) q10, no 126 on
   Map 10, the five pop boxes pairwise disjoint, the pin, class 871 barks).
   `derive_map_pins.py:291` follows; its Sacred Circle note
   (`:696-704`, "TypeShortmushroom resolves to 126") is rewritten.

**Verification.** The tests above, routes 10 green, `test_paint_cycles`
on the plateau; in-engine: the plant reads "Strange plant", the Avatar
walks round it into the egg box, the scene destroys it and the five pops
appear, and it stays gone after a trip off the map.

### Record

- 2026-10-11. Contract written; three candidates, one axis each: **A**
  faithful, a squat yellow-green bulb, dark-tipped spines, the red fruit
  (48x46 at game scale); **B** the same plant with purple flesh and bone
  spines (45x48); **C** the bulb on a short stalk, a giant thistle (47x48).
  A and B through `agy` (`tools/art/gen_test_plant.sh`, the base plants
  65/625/753 as the reference); agy's quota ran out on C (`429
  RESOURCE_EXHAUSTED`, no substitute drawn), so C came through the named
  fallback, Codex gpt-image-2 (`--codex C`), which takes no reference and
  returned a transparent background, flattened onto magenta by
  `tools/art/static_items.py flatten`. **Despill 0 for all three:** margin
  16 stripped the purple-black spine tips. Plates:
  `shared/docs/art-poc/test-plant/` (`compare.png`, `site-*.png`).
- 2026-10-11, later. **Douglas picked A** (the yellow-green bulb). Landed:
  the row (sized by width 48, despill 0; 48x46), `SHAPE_TEST_PLANT` on Map
  10 (`SHAPE_VEGETATION_SPARSE`, its only user, removed), `lv-new/
  TESTPLNT.UNK` with `TYPETESTPLANT` pinned to 871 (0x0367),
  `TypeShortmushroom` and `TypePoisonPlant` → 871, so PLNTST's destroy,
  its five creates and EggReapply's q10 sweep all follow; the 126s on Maps
  8 and 39 are untouched. `map_walkability` (d) checks the now-solid plant
  with `check_support`; `test_art_props` section 12. One rehash for all
  three items: `TYPEFLAG` b02e135c, `U8SHAPES` f55f4547, `EUSECODE`
  9bf65241 (1,526,688 bytes, md5 of the first 5000 bytes d00d0d59…),
  `FIXED` 177ac59a; `ANIM` unchanged. EUSECODE moved, so the detection
  entry and ScummVM rebuild are the integration step's; nothing was
  verified in-engine yet.

---

## Contract 9: the Water Zombie and the Harpie (shapes 872, 873)

**What they are.** The two monsters the 1994 Art List v2.5 names for the
expansion: "Water Zombie — import Dicko's art" and the Harpie
(`shared/corpus/plot-documents/characters.yaml:359-372`). The Lake is "full
of water zombies" (`locations.yaml:146-160`), and Ezrekal's lore calls them
"undead water zombies" (`lv-patched/EZREKAL.UNK:2992-2993`); the Harpie is
"home" on the Cloud Cliffs (`locations.yaml:187-190`), and Sigrid calls
them "Flying terrors ... Steal our food and attack the children"
(`lv-new/SIGRID.UNK:171`). No 1994 art survives for either, Dicko's
included, and no stats: `shared/corpus/GAP-ANALYSIS.md:123-124` lists both
behaviours and stats as gaps. So the stats are the donors' (below).

**Where they are today.** Only in monster eggs; nothing else creates them.

- Map 10, the Lake: five eggs at z 0, `build_map_10.py:1311-1318`,
  spawning `SHAPE_MON_ZOMBIE = 142`, the base **ghoul** (`lv_shapes.py:943`).
- Map 13, the harpie zone: four eggs at z 98-110, `build_map_13.py:595-601`,
  spawning `SHAPE_MON_HARPIE = 120`, the base **torax** (`lv_shapes.py:956`;
  it was the kith 76 until 2026-07-25, a spider).
- `map_pins.json` pins all nine (`derive_map_pins.py:479`, kind
  `monster_egg`; counted 2026-10-11: map 10 shape 142 ×5, map 13 shape 120 ×4).
- No usecode: no compiled LV file names a zombie or harpie type, and
  `TYPE_SHAPES` has none. The one `monster.create(TypeGhoul, 0)` in the
  source (`lv-patched/FREE.UNK:1564`) is inside the `/* ... */` block at
  1561-1575.

**The donors, read from the pristine `ANIM.DAT` and `U8SHAPES.FLX`
(2026-10-11).**

| | ghoul 142 → Water Zombie | torax 120 → Harpie |
|---|---|---|
| Frames in the shape | 451 | 240 |
| Drawn frames `ANIM.DAT` references | **162** (+7 drawn, unreferenced: 85, 95, 105, 115, 125, 383, 392) | **86** (+12 drawn, unreferenced) |
| Drawn directions | 5; dirs 0-2 are mirrors of 6-4 (frame flag `AFF_FLIPPED`) | 5, mirrored the same way |
| walk / run / advance (actions 0, 1, 8) | 8 frames × 5: 0-7 (dir 7), 40-47 (3), 50-57 (4), 60-67 (5), 70-77 (6) | 7 × 5 at the same bases |
| stand, retreat, combatStand | the walk's or attack's first frame | the same |
| attack (7) | 5 × 5: 80-84 ... 120-124; hit window frames 2-3 (`attack_range` 2 then 1) | 7 × 5: 80-86, 120-126, 130-136, 140-146, 150-156; hit window frames 3-5, peak 4 |
| die (14) / standUp (4) | die 15 × 2 views (175-189, 205-219), green motes rising off the body; standUp/readyWeapon 14 × 2 (268-281, 296-309) **rising out of the ground** | die 8 × 2 views (211-218, 231-238); standUp is die played backwards |
| idle (47, 48, and 19-21, 55) | 41 frames 380-420, upright | the attack's 80-82, 120-122 ... |
| sfx in the frames | FOOT10D, ZOMBIE1, ZOMBIE3, GHOUL2, AXSWNG1A, STABJCY1 | FOOT11B/D on the walk, MONSTER1 attack, IMPACT1A on death |
| TYPEFLAG | `SI_SOLID \| SI_BAG`, footpad **(2,2,5)**, weight/volume 200/200 | the same flags, footpad **(4,4,4)** |
| Usecode class | GHOUL: `look()` barks "ghoul " and nothing else | TORAX: `look()` barks "torax " |
| `u8monsters.ini` | hp 35-50, dex 14-16, dmg 6-12, armour 15, alignment 0x68, dmg type 0x0001, defense 0x0050, no treasure | hp 40-55, dex 8-12, dmg 7-14, armour 28, alignment 0x24, dmg type 0x0001, defense 0x0082, treasure `type=meat` |

**Engine identity.**

| | Water Zombie | Harpie |
|---|---|---|
| Shape | **872** | **873** |
| Frames | the ghoul's 451-frame layout, every drawn frame recoloured (derivation below) | the torax's 240-frame layout, the 86 referenced frames drawn new; the 12 unreferenced ones left blank |
| TYPEFLAG | row 142 verbatim | row 120 verbatim. The (4,4,4) box is today's torax box on the same lanes, so pathing and `canExistAt` at the eggs do not change |
| `ANIM.DAT` | entry 872 = entry 142's offset (`lv_tiny_avatar.clone_anim_entry`, `lv_tiny_avatar.py:124`): the art keeps the donor's frame numbers, so the action table is shared, and with it the donor's timing, hit windows and sfx | entry 873 = entry 120's, the same way. A harpie therefore plays the torax's footsteps while it flaps; a wing sound would need its own action table (the "different layout" case of the Actor contract) and is not proposed |
| `u8monsters.ini` | `[waterzombie]`: the ghoul's row, `shape=872`; since 2026-10-30 weakened to hp 25-35, damage 3-7, dex 10-12, armour 8 (Douglas, after `docs/playtest-2026-10-25-phaseD-verify.md` F2) | `[harpie]`: the torax's row, `shape=873`, its `type=meat` treasure kept (the donor rule; say if a harpie should drop nothing); since 2026-10-11 ("The eggs hatch" in the Record) with its own hp 30-45, damage 5-10, armour 11, defense 0 over the torax's; since 2026-10-31 weakened to hp 22-32, damage 3-7, armour 8 (Douglas, after `docs/playtest-2026-10-30-phaseE-verify.md` F1) |
| Usecode class | **872**, new `lv-new/WZOMBIE.UNK`, `look()` barks "water zombie", pin `TYPEWATERZOMBIE` → 872 | **873**, new `lv-new/HARPIE.UNK`, `look()` barks "harpie", pin `TYPEHARPIE` → 873 |
| `TYPE_SHAPES` | no entry, no re-point | none |

The classes are the Interactive-object contract's one consequence: the
engine runs `look()` from the class equal to the shape (`item.cpp:1516`),
and retail EUSECODE entries 874 and 875 (classes 872, 873) are empty, so
without a class the new monsters say nothing where the placeholders said
"ghoul" and "torax". The manifest pins are new (`lv_manifest.json` holds
860, 864, 865 and 868 in that range, none at 869-873).

**Where `u8monsters.ini` lives, and how 872/873 get rows.** Not the game
directory, and not `ultima.dat`: `GameData` opens it by bare name
(`config->readConfigFile("u8monsters.ini", "monsters")`,
`games/game_data.cpp:261`) through ScummVM's search path, and the copy that
answers ships inside **`ultima8.dat`**, the engine-data zip
`Ultima8Engine::initialize` mounts (`ultima8.cpp:177-182`;
`dists/engine-data/ultima8.dat`, built from
`devtools/create_ultima8/u8monsters.ini`, byte-identical on 2026-10-11).
`TypeFlags::loadMonsterInfo` keys every row by its `shape=` value
(`gfx/type_flags.cpp:353-436`, the assignment at 436). With no row,
`MonsterEgg::hatch` warns "failed to set stats" and spawns the actor anyway
(`world/monster_egg.cpp:53-65`): `loadMonsterStatsU8` returns before setting
HP, dex or alignment (`world/actors/actor.cpp:132-137`), armour, defense and
damage fall to the actor defaults (`actor.cpp:836-872`), and nothing drops.
A clone without rows is a zero-HP monster of no alignment.

Two ways to add the rows, both decided at phase 2:

- **(a) Recommended: an install-time game-directory file, no engine
  change.** `install_lv.sh` writes `u8monsters.ini` into the game directory
  as the patched build's own `ultima8.dat` copy (`unzip -p`) plus the two
  rows, and `--clean` removes it. The game directory is mounted in the
  `Engine` constructor (`engines/engine.cpp:230`, priority 0) before
  `initialize` adds `ultima8.dat` at the same priority, and
  `SearchSet::insert` places an equal priority after the existing node
  (`common/archive.cpp:334-341`), so the game directory's file is the one
  `File::open` finds [INFERENCE from the code; the in-engine check is
  below]. Regenerated from the installed `ultima8.dat` on every install,
  it cannot drift from the engine's own rows. It shadows the whole file,
  so it must be the full copy, never the two rows alone.
- (b) A fork change: `game_data.cpp` also reads an `lvmonsters.ini` into
  the same `monsters` category. `ConfigFileManager` already merges files
  of one category (`listSections` walks every file, `get` searches the
  last-read first: `conf/config_file_manager.cpp:85, 117`), so the LV file
  carries only its two rows. Cleaner data, but a fork commit, a patch
  regeneration and a ScummVM rebuild.

**Placement.** Unchanged positions. `SHAPE_MON_ZOMBIE` 142 → 872 and
`SHAPE_MON_HARPIE` 120 → 873 in `lv_shapes.py`; the egg quality is
`(prob << 11) | shape`, and 872/873 fit the 11 bits. The nine
`map_pins.json` rows are re-derived. `map_validate`'s monster-egg rule
wants TYPEFLAG family 6 at the spawned shape (`map_validate.py:352-367`),
which the verbatim rows carry, so the actor step must run before FIXED,
as `lv_tiny_avatar.py` already does.

**Build.** Step 6/8, the actor step, runs a second script after
`lv_tiny_avatar.py`: `agents/map-populator/src/lv_monsters.py`, a table of
monster clones (`MONSTERS`), each row a donor, a sprite source and an
`u8monsters.ini` section pair. (Phase 1 planned to generalise
`lv_tiny_avatar.py` itself; by phase 2 contract 8 had made it a scaled
Avatar with its own action table, a different kind of derivation, so the
monsters got their own script in the same step and the step count did not
move.) `lv_tiny_avatar.py` writes `ANIM.DAT` from the pristine base, so it
runs first and `lv_monsters.py` patches its output. The zombie's sprite is
built at build time from the base ghoul through an index table, the way
859 and 868 are built from base shapes, so no Origin-derived pixels are
committed: candidate A's 64-entry `WATER_ZOMBIE_REMAP` until 2026-10-25,
since then `lv_actor_art.ZOMBIE_REMAP` toward the 1994 zombie of
screen02/09 with the shots' three poses in. The same step builds the 1994
NPC bodies 888-890 (`NPCS`, from `lv_actor_art.py`). The harpie's frames
are ours, so its build input is the derived frames as PNGs, assembled into
the 240-frame layout.

**The art, and the method (Douglas 2026-10-11: "generate key poses, derive
the rest").** Generated key poses (idle, walk, attack, dead) in U8's
projection fix the look; every frame of the donor's animation set is then
derived toward it. The two monsters need different derivations, because
one donor is the right body and the other is not.

- **Water Zombie: ramp transfer onto the ghoul's own frames.** The ghoul is
  already a shambling undead with 162 hand-animated frames. The
  candidate's colours are read off its key poses by anatomy (flesh, rags,
  accent), each ghoul material (the palette's own hue groups) is
  quantile-matched by luminance to them, and the result is one
  index-to-index table applied to every frame. It is coherent by
  construction: the ghoul's dithering, shading and motion survive pixel
  for pixel, nothing can flicker, and all 451 frames derive in seconds
  with no further generation. The rising motes of the death become pale
  water, and the ghoul's rise out of the ground becomes a rise out of the
  lake. The cost: the silhouette stays the ghoul's, so what a candidate
  adds outside it (A's bloat, B's trailing weed) is not carried; the
  `keys-plate` shows each candidate beside what the table makes of the
  ghoul's same four frames, so the gap is visible before a pick. If the
  silhouette matters, the next step is a per-frame paint-over of the 162,
  with the coherence problem that brings.
- **Harpie: sheet sequencing.** The torax is a crawling quadruped, so its
  silhouette guides nothing; it gives the frame layout, the timing and the
  hit windows. Each drawn direction gets one generated sheet of four wing
  phases of the same body, with the picked candidate's key sheet as the
  character reference and a ghoul walk frame as the facing cue. One scale
  per sheet (never per figure), aligned on the body column, anchored to
  the torax's own anchor-to-feet offset with the talons 6 px off the
  ground, and sequenced into the torax's 7-frame cycle with a one-pixel
  body bob: up, downstroke, down, down, upstroke, upstroke, up. Four
  drawings, seven frames.
- Per-frame img2img was rejected for both: each frame is repainted
  independently, so detail swims frame to frame, and 162 + 86 generations
  is far past the quota (Nano Banana walled after 4 images on 2026-10-11,
  codex after 4 more).

**Frame-count estimate for the full derivation.**

| | Frames | Generation | Work |
|---|---|---|---|
| Water Zombie | 451 (162 referenced) | **none** past the picked key sheet | the table; a per-frame touch-up pass only if Douglas wants the candidate's silhouette |
| Harpie walk/run/advance/stand | 35 | 5 sheets (the sample) | done for the leading candidate |
| Harpie attack, combatStand, readyWeapon, retreat, idle | 35 | 5 sheets of 4-5 phases (rear back, strike, follow-through, recover) | the strike must land on frames 3-5 of each 7, the torax's hit window |
| Harpie die / standUp / stumble | 16 | 2 sheets (the two die views) of 4-5 phases | the fall from 6 px of hover to the ground; standUp plays it backwards, so the last frame must read as a body on the ground and the first as airborne |
| **Total** | 86 harpie frames | **about 12 sheets** plus re-rolls, at four per session per route | |

**Hard parts.** The harpie's **attack**: the torax's hit window is fixed
in the shared table (`attack_range` 1, 2, 1 on frames 3-5), so the talon
strike has to be drawn there in all five directions; a lunge whose reach
peaks a frame early reads as a miss that hits. The harpie's **death**: a
flyer has to fall, and the torax's die frames carry no `deltaZ`, so the
fall is drawn into eight frames that also have to work backwards as
standUp. **No shadow**: U8 actors draw none, so a hovering sprite reads as
floating only by its talons; 6 px of hover is the guess, and the in-engine
look decides it. The **zombie's death motes** keep the ghoul's green-mote
motion as pale water, which may read as steam. The zombie's ghoul sounds
(GHOUL2, ZOMBIE1/3) suit it; the harpie's torax footsteps do not.

**Verification (phase 2).** A `test_art_props.py`-style section per
monster: 872/873 equal their donors' TYPEFLAG rows and `ANIM.DAT` action
tables (the `_verify` of `lv_tiny_avatar.py`), every frame index the table
references is drawn and no other changed, no pixel lands on a cycling
palette index (1-14, `gfx/cycle_process.cpp`), the eggs name 872/873, the
classes bark their names, and the installed `u8monsters.ini` has both rows
with the donors' values. In-engine: walk into the Lake and the harpie zone,
let each spawn, and check in the console log that no "failed to set stats"
line names 872 or 873; fight one of each to the death (the HP range is the
donor's), watch the attack land on the strike frame, the death fall, and
the corpse; double-click a corpse for its name.

### Record

- 2026-10-11. Phase 1. Shapes 872/873 allocated (Douglas). The generator
  `tools/art/gen_monsters.sh` (two routes: Nano Banana, and codex as the
  named fallback for a wall) and the splitter, derivations and plates in
  `tools/art/monster_frames.py`. References: the ghoul's four key frames
  facing the viewer (`water-zombie/reference-ghoul-dir3.png`) and one ghoul
  walk frame per drawn direction (`harpie/reference-facing-d*.png`).
  Key-pose candidates, all read in the agent's own log as real
  generations: zombie A (drowned, bloated blue-grey), B (weed-wrapped
  olive), C (bone-pale, teal rags, barnacles), all Nano Banana; harpie A
  (brown-feathered, a woman's head and torso) Nano Banana, B (vulture hag)
  and C (storm-grey) codex. Every plated frame went through quantize,
  `encode_frame`, `validate_shape`, `inject_shape` into a scratch copy of
  the built `U8SHAPES.FLX` at 872/873, and read-back.
  Zombie: the 8-direction walk derived for all three candidates
  (`water-zombie/walk-{A,B,C}-{1,3}x.png`, `walk-*.gif` with a `-still.png`,
  `scene-map10-*-{1,2}x.png` on the Lake pier beside the ghoul and the
  Avatar), and candidate A's whole 169-frame set
  (`allframes-A-2x.png`). Harpie: key plate for A-C
  (`harpie/keys-plate-{1,4}x.png`); walk sheets for A drawn for directions
  3 and 4 only. Both routes walled on 2026-10-11 (codex: "try again at
  4:05 PM"), so directions 5-7, and with them `tools/art/monster_frames.py
  harpie A` (walk plate, GIF, Map 13 scene), are still to run:
  `ROUTE=codex tools/art/gen_monsters.sh walk A`, then `monster_frames.py
  split` and `harpie A`.
- 2026-10-11. Phase 2: landed both (Douglas picked zombie A and harpie A).
  **Zombie:** `WATER_ZOMBIE_REMAP` in `lv_monsters.py` is candidate A's
  table, 64 ghoul indices remapped and the outline kept (asserted equal to
  `monster_frames.build_lut('A')` by `test_lv_monsters.py`), applied to all
  451 ghoul frames at build time. **Harpie:** the walk sheets for
  directions 5-7, then five attack sheets (ready, rear, lunge, strike,
  recover; sequenced 0 1 2 3 3 2 4 so the strike sits in the torax's hit
  window, frames 3-5) and two death sheets (struck, falling, dropping,
  landing, dead; 0 1 1 2 2 3 4 4, the talons dropping from 6 px of hover to
  the ground), all codex/gpt-image-2 and each log read as a real
  generation. `monster_frames.py harpie A` sequences them into the 86
  referenced torax frames (the 12 drawn-but-unreferenced torax frames are
  1x1 blanks) and writes the build input
  `shared/docs/art-poc/harpie/frames-A/` (palette-indexed PNGs read back
  from a scratch FLX, plus `anchors.json`), plates `walk-`, `attack-`,
  `die-A-{1,3}x.png` with GIFs, and the Map 13 scene. **Shared:**
  `SHAPE_MON_ZOMBIE`/`SHAPE_MON_HARPIE` re-pointed to 872/873 (the nine
  `map_pins.json` rows re-derived); classes 872/873 pinned
  (`TYPEWATERZOMBIE`, `TYPEHARPIE`); `install_lv.sh` writes the game
  directory's `u8monsters.ini` from the patched build's `ultima8.dat` plus
  `[waterzombie]` (the ghoul's row, shape 872) and `[harpie]` (the torax's,
  873, its `type=meat` treasure kept), and `--clean` removes it.
  `map_validate`'s TYPEFLAG reader now prefers the built file, as its shape
  reader already did: it was reading the install copy, so the new shape
  read as family 0 and the Lake's eggs warned. Rehashed: all five
  artifacts moved. Known weaknesses for the in-engine look: the codex
  sheets drift in facing (the direction-6 attack and the direction-7
  death face more toward the viewer than away), the death's "dropping"
  phase is drawn smaller than the others, and the harpie plays the torax's
  sounds.
- 2026-10-11. The eggs hatch, and the Harpie gets its own stats.
  `playtest-2026-10-11-monsters` found no LV egg had ever hatched (a
  shape-500 egg needs a MONEGG trigger, UnkEgg q2, and the LV maps had
  none), the Lake's eggs stood in drowning water, the harpie zone's in or
  over the cliff, every egg loitered (activity 0), and the torax's armour
  28 / defense 0x82 left a harpie unkillable with early weapons. Every LV
  egg now has a trigger, a standable dry spot and combat activity
  (`lv_monster_eggs.py`, `test_monster_eggs.py`): the Lake's five are on
  the pier and the deck, the harpies on the climb's upper lanes and the
  summit. `lv_monsters.py` MONSTERS rows take `stats` overrides, and the
  Harpie's are the changeling's weight with its own talons (hp 30-45,
  5-10, armour 11, defense 0; the torax's dex 8-12, alignment and
  treasure kept). The Water Zombie keeps the ghoul's row. FIXED.DAT
  rehashed; the ini is install-time engine data, so no artifact moves for
  the stats.
- 2026-10-11. They hatch fighting, once, on safe ground.
  `playtest-2026-10-11-monsters2` saw them hatch and found four faults.
  Monsters hatched outside the fast area arrive passive
  (`Item::enterFastArea` clears combat): every LV egg now hatches inside
  the 320x200 fast area from every spot in its trigger's box, and one
  that does not see the Avatar at once loiters inside it too
  (`lv_monster_eggs.hatch_fast_problem`). Map 11's heavies and Map 10's
  kith and spiders each have a trigger of their own between them and the
  way. Map 11's lizards stand by the water doorway. Every LV egg is
  one-shot (frame 1), so a doorway walked through twice no longer stacks
  a second hatch. The Lake's deck and pier are railed with invisible wall
  (497/498), which stops a blow's 64-unit stumble before it puts the
  Avatar in the water. The lane harpies stand side by side, both in sight
  of the trigger. `test_monster_eggs.py` checks all of it against the
  built map: 33 failures on the old FIXED.DAT, none on the new.
- 2026-10-12. Round 3 (`playtest-2026-10-12-monsters3`) found two more
  faults. Golems 1 and 7 hatched fighting behind Passage 1's wall from
  their triggers. Both triggers now stand north of the wall, in the
  pocket's open east side, and golem 1 moved south of the rock spire that
  blocked its way east. The rails held on the pier, but the fight drifted
  off its foot onto the shore, where the Avatar drowned twice. The lake's
  south and west shores now have a rail on their last 32 units of water.
  `test_monster_eggs.py` adds two checks. The first walks each monster,
  with its own body, to every spot in its trigger's box: at most 1.3
  times the straight line, or 256 over it. The second keeps every spot
  within the seek range of a trigger or an egg off the water, and no
  stumble from one may end in it. On the old FIXED.DAT they fail 7 times;
  on the new one, none.


## Decorative cave backdrops

2 November 2026. Shapes 894 and 895 copy retail 334's 29 frames and 564's
seven frames through `lv_art_props.py`. Donor 202 supplies FIXED and DRAW
with no SOLID, LAND, ROOF, or OCCL flags. Their footpads retain the sources'
(4,4,0) and (8,8,0) sorting bounds. Slot 893 remains reserved for phase E's
actor work.

Map 8 places these sprites at z0 beneath hidden ceilings and replacement
floor plates. Each
source at (x,y,z) becomes (x-4*z,y-4*z,0), preserving its projected pixels.
The Avatar and the shelf draw above the backdrop. The clones supply no
walking surface, collision, or roof cut. The supported build's existing
static-prop step creates both shapes from local retail bytes.

`test_map08_backdrop.py` checks every replaced surface pixel, the two reported
cameras, the first seam's floor border, Avatar visibility, and decorative
physics against built artifacts. Pristine inputs resolve through
`pristine_base()`, including fresh installations without backup files.
The table-driven checks in `test_art_props.py` verify the copied frames
and donor flags.

## Visual-pass decorative clips

Shape 895 retains retail 564 frames zero through six verbatim. Frames
seven through 90 use binary opacity masks under
`shared/data/lv-1994-art/vq2-clips/`. The masks contain transparency decisions;
the build reads the retail texture from the user's game data. The 47
Map 11 texture masks use frame zero, cover the former filler sprites,
exclude screen05 and screen07, and exclude existing flat DRAW ground
pixels. Three Map 18 texture masks cover the former island caps outside
screen04, repainting black exposed by the phase-two visibility repair.

Map 11 retains every original filler support box through editor plates:
763 for a 128-unit tile and 499 for a 256-unit plate. Its 34 black clips
use frame two and paint the original permanent background inside the
protected windows, including beneath animated objects and removable
pillars. Exterior black tails give way to texture or existing
ground. The donor-202 row and (8,8,0) footpad remain unchanged. Bounded
navy pools retain the original flagstone support beneath their paint.


## Phase 4 shared dressing copies

Shared slice 0.1 adds these static `lv_art_props.PROPS` rows. Each sprite is
copied from retail at build time; no retail pixels are committed.

| Shape | Export | Sprite source | TYPEFLAG donor | Footpad |
|---|---|---|---|---|
| 898 | `SHAPE_COURT_COBBLE_FLAT` | 70, all 23 frames | 71 | (4,4,0) |
| 899 | `SHAPE_RUBBLE_DECORATIVE` | 524, six frames | 465 | (3,3,1) |
| 900 | `SHAPE_BONES_DECORATIVE_A` | 235, two frames | 465 | (3,4,1) |
| 901 | `SHAPE_BONES_DECORATIVE_B` | 237, two frames | 465 | (4,3,1) |
| 902 | `SHAPE_CAVE_CREST_DECORATIVE` | 125, 23 frames with seven crops each | 202 | (4,4,0) |
| 903 | `SHAPE_MOAT_BANK_DECORATIVE` | 94, 11 frames | 465 | (4,4,1) |
| 904 | `SHAPE_MOAT_FACE_DECORATIVE` | 85, seven frames | 465 | (1,4,4) |

898 has 71's zero-height support and preserves the retail cobble relief.
899 through 901 retain the source footpads and sprite heights, with FIXED
set and LAND and SOLID clear. `KIT_HALL` includes 899; `KIT_BONES` includes
900 and 901. These rows eliminate the reachable eight-unit tops of their
donors. The raised 37 dais remains excluded by the standing-level rule.

902 uses decorative FIXED and DRAW physics. Each retail frame has full,
upper eight, 16, 24, or 32 pixel strips, and left and right half variants.
Every variant retains the source canvas and anchor. `Site.cave_crest`
accepts authored anchors with retail frame numbers and selects the largest
safe crop, protecting shot windows with a 16-pixel margin and comparing
all walking and standing poses at every quest-band cell. If every crop fails, the named
piece is refused atomically. `Site.reason` also checks route occlusion for
902 placed through other dressing paths.

903 and 904 form clipped bank prefabs for Map 39, preserving inherited
water at z zero and grass at z 48. Caps stand at z 40 and faces at z eight;
their decorative rows supply no collision or support. The west rows keep
the grass-side column ending at x 13567. The east rows begin after x 14079.
`Site.moat_bank` leaves every retained canal record intact and requires
existing grass support before it adds paint.

D8's conditional cloud-rim lobes take the next free shape, **929**, if
requested. No class, usecode dispatch, or animation table is allocated for
these seven rows. Existing shape and TYPEFLAG payloads remain unchanged.


## Shared dressing slice 0.2, decorative surfaces

Allocated on 10 November 2026. These static copy rows use donor 465 and
supply no LAND, SOLID, standing surface, class, or animation entry.

| Shape | Art | Footpad |
|---|---|---|
| 905 | White column 875:0 turned onto its side | (3,2,1) |
| 906 | Roots 57, all four frames | (6,5,2) |
| 907 | Fungus 65, all 26 frames | (2,2,5) |
| 908 | Spires 66, all 12 frames | (4,4,5) |
| 909 | Urn 229, one frame | (1,1,2) |
| 910 | Rubble 526, all nine frames | (2,2,2) |
| 911 | Basalt 122, all 30 frames | (4,4,1) |
| 912 | Relief 246, all 10 frames | (1,4,5) |
| 913 | Relief 252, all 10 frames | (4,1,5) |
| 914 | Face 26, all 15 frames clipped to an eight-unit riser | (4,1,1) |
| 915 | Wall 15's silhouettes filled with crest 125:12 stone | (4,1,5) |

The drum's copy transform preserves palette indices, turns the cylinder
horizontally, and places its lower edge on the floor. Rubble 899 retains
its original six frames; 910 supplies the additional small white fragments
from retail 526:6-8. `KIT_HALL` and `KIT_DECORATIVE` expose decorative rows.
The four `fallen_drum_` prefabs combine the drum with a small white fragment
on cloud floor, using appended manifest IDs.

`paint_only` accepts reliefs, clipped faces, decorative crests, and wall
skins. A wall skin retains every original collision record, covers every
original painted wall pixel, passes the shot and reservation masks, and
compares walking poses throughout the original arrival flood and quest
bands. Frame and pose owners are compared using the built painter. Both
actor insertion orders are checked for ambiguous dependencies.
`basalt_shore` requires retained cold 301, 4, or 386 beside lava and retains
every original record, including causeway 70 and lava 409. Named low
architecture uses `walkable_set_piece` and its complete before-and-after
route proof. Generated dressing retains the standing-top exclusion.

The next free shape is 929. Conditional D8 cloud lobes would use that ID.


916 through 928 append shifted decorative stars on donor 202 with footpad
(4,4,0). All nine retail star frames are copied in 337 anchor layouts.
At most 28 layouts fit a shape's eight-bit FIXED frame field. The copied
anchors compensate projection and C-division rounding across coordinate
zero. No copied row supplies collision or a standing surface.
`beyond(..., north=True)` chooses flat z-zero copies in visible ground
chunks. A greedy cover checks both engine viewport sizes with the engine's
chunk filter. Sky records precede retained floors and remain loose through
packing, preserving the cloud lobes. The next free shape is 929.
