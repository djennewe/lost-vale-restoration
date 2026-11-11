# The elemental pillars (shape 865) and their receptacles (866)

Art track item 5, `docs/art-track.md` contract 5. **Landed 2026-09-24**,
verified in ScummVM (`docs/playtest-2026-09-24-elemental-pillars.md`);
one plinth under all four since 2026-09-25
(`docs/playtest-2026-09-25-pillar-plinths.md`).

## What ships

**Superseded for 865 (2026-10-30).** All four 865 frames are now the 1994
Pillar of Fire's column (registry 2023, screen07) and its redraws for
Earth, Air and Water (registry 2024-2026, `tools/art/pillar_1994_style.py`,
Douglas's card 4; `docs/art-track.md`). The 865 sheets below no longer feed
the build and stay as history. The receptacle, 866 `R_raw.png`, still
ships. The rest of this section describes 2026-09-24 to 10-29.

Shape 865 is four frames cut from two four-in-a-row sheets: **Earth and
Air from `C2_raw.png`** (the "natural" take: a rock spire, a whirlwind
funnel) and **Fire and Water from `C3_raw.png`** (the "wild" take: a
flaring blaze, a surging column), Douglas's mix of 2026-09-24, at 96 px on
donor 38 with footpad (2,2,10). Shape 866 is `R_raw.png`, the receptacle,
approved as generated, at 40 px on donor 443's (3,3,3). The build inputs
are `C2_f0_earth_c3plinth_raw.png` and `C2_f1_air_c3plinth_raw.png` (the
C2 columns on C3's plinth, made by `tools/art/pillar_plinth.py` from the
cut frames `C2_f0_earth_raw.png` and `C2_f1_air_raw.png`),
`C3_f2_fire_raw.png`, `C3_f3_water_raw.png`, and `R_raw.png`; the sheets
they came from stay beside them.

## The passes

`tools/art/gen_pillars.sh` made everything through `agy`, one sheet per
candidate so the four frames share one style. **v1**: A (the element as a
crown on a stone shaft), B (the element carved on the face), C (the column
made of its element on a stone plinth, which is what the 1994 barks say).
At game scale B's emblems vanished and A's crowns half survived; C read at
1x with no palette index shared across its four frames. Douglas took C and
asked for columns "less rectangular and more organic". **v2**: C2 natural
and C3 wild, both organic, both read at 1x. Every sheet came back about 4:1
slender, because four pillars in a square 1024 image cap each at about
250 px wide; the box followed the art, and no third pass was needed.

`tools/art/split_sheet.py` cuts a sheet on the empty magenta bands between
the pillars, or at the dip minima when plinths touch (A did; C2 and C3 cut
clean). `tools/art/pillar_preview.py` pushes every frame through
`png2shape.build_frame` and renders it at 72 and 96 px beside the chimney
and a ring stone, with a palette check that strips the shared family
indices before comparing frames; `*_h72_*`, `*_h96_*`, `R_h40_*` and
`preview_report.json` are its output. "The Four Pillars" artifact
(2026-09-24) was the approval page built from them.

The seam the 2026-09-24 plates showed, C2's violet plinths under Earth
and Air against C3's blue-grey under Fire and Water, closed on 2026-09-25:
`tools/art/pillar_plinth.py` puts C3's plinth under the C2 columns
(`plinth_check.png` is its check plate, `plinth_report.json` its counts;
`LANDED_h96_*` and `C23_h96_*` are the before and after at game scale).
What is left of it is one row of height at 96 px, C2's block being the
taller cut.

## Before plates and references

Regenerate with:

    python3 tools/art/pillar_plates.py

## What Map 11 shows today

`before-pillars-4x.png` (and the same at 1x) is shape 721 frames 0 to 3
beside shape 307 frame 0, straight out of the base game's `U8SHAPES.FLX`.

The four "elemental pillars" are **four chimneys**. Frames 0 and 1 are
rough stone stacks in brown and grey; frames 2 and 3 are red brick with an
open flue at the top, frame 3 capped in grey. Map 11 reads them as Earth,
Air, Fire, and Water, and a player reads them as masonry: brown against
grey says nothing about earth against air, and fire and water are the same
brick chimney twice. Class 0x2D1 at that shape is the engine's `CHIMNEY`,
and a click barks "chimney".

The receptacle is shape 307, an **ornate domed chest** with a stag carved
on each door. `build_map_10.py` aliases the same shape `SHAPE_CRATE` and
stands five of them in houses, which is the honest use of it. Beside a
pillar it tells the player to open it, where what the puzzle wants is a
double-click while carrying the opposite element's talisman.

## The references

`reference-ring-stones-4x.png` is shape 38, the dressed standing stones of
Map 10's Sacred Circle, and the contract's TYPEFLAG donor for 865: the
chimney's flags without `SI_NOISY`, and the same (2,2,5) footpad. It is the
game's own idiom for worked standing stone, and the Sacred Rock (863) was
generated against frames 2 and 3 of it.

`reference-talisman-gems.png` is shape 596 frames 0 to 3, the four
talismans as Map 11 places them, at 8x. It is in this folder because it is
a finding, and it belongs beside the plates: **the talismans do not read as their
elements either.** Earth is a small orange flask, Air is a gold ring with a
purple stone at twice the size of the rest, Fire is a purple gem, and Water
is a blue gem. Frames 4 to 7 of the same shape are a matched set of four
5x5 star gems in orange, red, purple, and blue. Switching to them is a map
frame change plus `COLPUZZL`'s `oppFrame` mapping, and it is cheap only
while contract 5's recompile is open. The contract records it; nobody has
decided it.

## Why this item costs more than 861, 862, or 863

`COLPUZZL.UNK:139` compiles `type = TypeElementalColumn` into the shape
number, so the pillars cannot move without `TYPE_SHAPES` moving with them,
and that rebuilds `EUSECODE.FLX`, re-records the hashes, regenerates the
detection entry, and rebuilds ScummVM. The receptacles cost nothing extra:
their `use()` comes off `npcnum = 120` through the engine patch, which is
independent of the shape.
