# Phase D, actors: the 1994 elder, the spear children and the Water Zombie (2026-10-25)

Douglas (2026-10-25) chose to draw the 1994 actors that no retail shape draws. This slice
derives them as actor clones and builds them into the game.

## Shapes

| ID | What | Donor (TYPEFLAG row, ANIM.DAT table, frame layout) | Body of |
|---|---|---|---|
| 872 | Water Zombie, restyled in place: `ZOMBIE_REMAP` (teal skin, dark green kilt, green slime) plus three shot poses | ghoul 142, 451 frames | Lake eggs (unchanged) |
| 888 | Zealan elder: Mythran's body restyled (robe browns, long white hair) plus two shot poses | Mythran 190, 350 frames | Atli, npc 107 (record frame 60, stand SE) |
| 889 | dark-haired spear child (grey tunic, black cloak, spear) at 0.8 scale | child 708, 100 frames | npc 104 |
| 890 | blond spear child | child 708, 100 frames | npc 111 |

891-893 are unallocated. The NPC bodies have no `u8monsters.ini` row and no class: a placed
LV NPC dispatches by npcnum, objId + 1024.

## Method

`agents/map-populator/src/lv_actor_art.py` derives every frame at build time from two
sources: the pristine base shapes and the committed 1994 cut-outs (`art_registry.json`
2041, 2042 and 2050). No Origin pixel is committed. `lv_monsters.py` (build step 6/8)
builds `MONSTERS + NPCS`:

- the frames come from `actor_frames()`;
- the TYPEFLAG row is the donor's;
- the ANIM.DAT entry points at the donor's table.

`WATER_ZOMBIE_REMAP` and `recolour_shape` / `check_remap` are gone.

Each shot pose is the registry PNG index for index, with two adjustments:

- cycling indices are swapped for their static same-colour twins (9 → 28, 2 → 144);
- the `POSE_HOLES` are filled from the GIF.

The donors' own cycling index 9 also becomes 28. The screen19 pose's anchor moved one
pixel, from (14,45) to (13,45). From x 14, no z-0 world position puts the pose on the
shot's pixels. Per-frame provenance is recorded as `built_as` in `art_registry.json`:

| Shape | Shot pose (1994 pixels) | Drawn | Derived |
|---|---|---|---|
| 888 | 60, 70-72 | 110, 136, 160, 185, 209 (combatStand: copies of that direction's stand); 108, 133, 158, 183, 208 (die/standUp: 707's corpse with the hair whitened); 90-94, 96, 98-102 (climb) | the other 125 frames |
| 889 / 890 | 1 | — | 0, 2-74 |
| 872 | 40, 81, 112 | — | 166 frames |

## Scores (all-frame palette class, %)

| Shot | Retail replay (unchanged) | Built replay, before → after | Built window with actors, before → after (`test_vignettes` floor) | In-engine `SCORES.md` |
|---|---|---|---|---|
| screen02 | 96.037 | 96.04 → **98.481** | 95.96 → **98.40** | 91.26 (not re-run) |
| screen09 | 93.680 | 93.68 → **94.774** | 93.75 → **94.84** | 82.65 (not re-run) |
| screen19 | 96.066 | 96.07 → **97.261** | 95.85 → **97.09** | 94.46 (not re-run) |
| screen20 | 95.435 | 95.44 → **97.444** | 95.69 → **97.70** | 90.83 (not re-run) |

The actors' world positions were solved so that their pixels land exactly. Every cut-out
pixel of all 7 actors is painted by the actor, index-equal: 685, 722, 695, 703, 757, 200
and 203 of 685, 722, 695, 703, 757, 200 and 203. The only extra pixels are the
`POSE_HOLES`.

The retail replay keeps its contract: `built: true` actors are painted only by
`--built`, and `vignette_built_window`. The built contract lives in `verify.built`, with
renders `screenNN_{render,diff}_built.png`. In the built window, an actor that carries
`npcnum` replaces the map's start record for that NPC (Atli in screen19).

## Tests

All run in the worktree on FIXED `469787ab`:

- `tools/build_artifacts.sh --record`;
- `tools/run_all_tests.sh`: 54/54 PASS;
- `test_lv_monsters.py`: 72 passed, with sections 1-2 rewritten and 2c new;
- `test_tiny_tar.py`: 36 passed;
- `test_vignettes.py`: 39 passed;
- `test_schedule_destinations.py`: 200 passed.

EUSECODE is unchanged (md5 `4664e5cc…`, same as main).

## In-engine plates (`ingame/`)

Setup:

- binary: `scummvm-lv-console`, on Xvfb :97;
- game: a private copy of `u8-lv-patched` with the worktree's artifacts;
- cheats on, a new game, teleported to Map 10 (20250,8150).

Each NPC was placed with `Actor::hold <npc> dx dy` 176 units out on each of the 8 sides
of the Avatar. The game then ran while it was captured.

- **Atli (107):** captured with `Actor::talk` too. He stands, walks up, barks "A moment,
  good sir.", "May I speak with you?" and "Farewell" (the talk action), then walks
  away. Plates: `npc107-from-{N..NW}.png`.
- **Children (104, 111):** captured standing, then walking off on their activity.
  Plates: `npc104-*`, `npc111-*`. They have no class, so they have no bark.

Every sprite seen draws whole, with no missing or garbage frames.

**Not done:**

- (8a) zombie walking, attacking and dying in-engine. That needs a pier hatch and a
  fight. 872's frames are verified offline: all 451 built, the 3 poses index-equal,
  166 frames pixel-equal to the remapped ghoul.
- (8b) `vignette_capture.py` re-scores for 02/09/19/20.

## Contact sheet

`../../phaseD-actors-contact.png` shows each 1994 crop beside the built replay at 2x,
then every drawn frame of 888, 889, 890 and 872 at 2x.

## Known issues for Douglas

1. **Atli's start frame is 60 (SE).** In the doorway, Mythran's wider body facing
   N or NE (frames 0, 15, 30) is 16-27% covered by the east jamb. Check 4 of
   `test_schedule_destinations` now measures the record's frame (7%). The engine starts
   actors facing north, so this is cosmetic after his first animation.
2. **Staff pop.** Mythran-derived frames carry a tall knobbed staff, but the 1994
   screen20 elder carries a short cane. The staff top pops when he starts or stops
   facing SE.
3. **Static SE talk.** SE talk (70-72) is the static screen19 pose, without the staff.
4. **Die frame.** The elder's die is a single frame: 707's corpse, slimmer than his body.
5. **Children.** Their spear angles and grip are guesses. 708's long hair dominates the
   rear views, and the non-shot frames keep a black outline.
6. **Zombie club.** The club exists only at frame 81, so it pops in during the NW
   attack.
7. **Mythran resemblance.** 888 reads as a restyled Mythran, who is also an LV
   character.
8. **Unverified pairings.** The npc-to-hair pairing (104 dark, 111 blond) and "the
   screen20 elder is Atli" are inferences.
9. **Pre-existing replay drift.** `vignette_replay.py --check` reports screen11 and
   screen12 as differing from their published renders. Those files were not touched
   here.
