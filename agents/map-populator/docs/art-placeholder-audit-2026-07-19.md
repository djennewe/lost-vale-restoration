# Art Placeholder Audit — 2026-07-19

Completes the long-deferred audit tracked in `shared/docs/art-placeholder-audit.md`
and in CLAUDE.md's "Known Limitations". That earlier document was a *plan* written
largely from usage and naming; this one is an *evidence pass*. Every shape below was
identified three ways before any conclusion was drawn:

1. **Rendered and looked at** — actual pixels, via `shape_render.py` plus a
   frame-indexed grid renderer, against the effective `U8SHAPES.FLX`.
2. **Named by the engine** — `shape_names.engine_name()`, the authoritative identity
   source (usecode class = shape + 2). This is what the player literally sees printed
   when they click the object, and it caught defects that renders alone did not.
3. **Flag-checked** — `parse_typeflag.py`, for `SI_FIXED` (can it be picked up?),
   `SI_DAMAGING` (does it hurt the player?), family, and footpad (collision).

Renderer trustworthiness was calibrated first: shape 613 frame 6 renders as a
brown-cover book, exactly as `lv_shapes.py` documents, so frame indices are reliable.

## The governing constraint: most placeholders are NOT map-side fixable

This is the single most important finding, and it is why this audit kept stalling.

A placed item's **shape ID is its identity to the usecode VM**. LV scripts locate quest
objects with `foreach item where (type = TypeXXX)`, and each `TypeXXX` resolves to a
shape ID through `TYPE_SHAPES` in `agents/usecode-compiler/src/u8c_symbols.py` — a file
this agent does not own. Some scripts go further and declare a `typeclass TypeXXX` whose
`look()`/`use()` handlers are dispatched by that same shape ID.

So for most placeholders, changing the shape map-side alone does not improve the game —
**it breaks the quest**, because the item silently stops matching the filter that finds it.
Those items require a coordinated two-file change and are listed as such below rather than
being unilaterally "fixed".

Cross-referencing every placeholder shape against all 77 LV `.UNK` sources produced this
split:

| Shape | Engine name | Usecode-coupled? | Map-side fixable alone? |
|-------|-------------|------------------|--------------------------|
| 400 | `fire field` | `TypeSkeleton`/`TypeGhoul`/`TypeDemon` exist in TYPE_SHAPES but **no LV `foreach` and no `typeclass`** | **YES** |
| 721 | `chimney` | `TypeStatue` foreach exists, but only in `PLNTST.UNK`, scoped `within 100 cells of referent` on Map 10 | **YES on Map 18** |
| 580 | *(none)* | `foreach type = TypeAOFrizbee` (SHADES.UNK), `TypeAOArtifact` (AOSCENE.UNK) | NO |
| 399 | `eye of newt` | `foreach (type = TypeWeedz) and (frame = 9)` ×2 (EZREKAL.UNK) | NO |
| 395 → **868** | `vial` → custom | `foreach (type = TypeBottle) and (frame = 0)` ×2 (TYORVI.UNK; frame 13, then 5 from 2026-10-08, then the elixir's own shape 868 frame 0 from 2026-10-09) | NO |
| 158 | *(none)* | `typeclass TypeNSGoldPlaque` with `look()`/`use()` (PLAQUENS.UNK) | NO |
| 73 | *(none)* | `TypeShades`, `TypePathMarker` (16 files) | NO |

---

## Changes made

All four changes are map-side only, verified non-coupled, and target objects that were
*actively lying to the player* rather than merely looking bland.

### 1. Map 17 Memorial Hall corpses — shape 400 → 332 (2 items)

`build_map_17.py`, the two fallen figures (Snori/Flossie, Hoskuld).

**Before:** shape 400 frame 7. Shape 400's engine name is literally **`fire field`**.
It rendered the corpses as open flame, printed "fire field" on click, and — because
TYPEFLAG marks 400 `SI_DAMAGING` — **burned the Avatar standing on the exact spot where
the Shield halves are collected**. This was a damage hazard disguised as scenery.

**After:** `SHAPE_SKELETON_SPRAWLED` = 332, frames 0 and 1. Engine name `skeleton`;
render shows a skeleton sprawled flat; TYPEFLAG `[SI_SOLID, SI_LAND]`, `SF_CONTAINER`,
footpad (2,3,1) — the same family and same flat z=1 footpad as shapes 235/237, the
already-blessed fix from commit 5c78f60.

**Evidence for the pick:** 332 satisfies all three identity checks and matches the
precedent set by the accepted bones fix.

### 2. Map 18 Inner Sanctum — the three Zealan gods — shape 400 → 443 (3 items)

`build_map_18.py`, Felicitar / Doloras / Timyra.

**Before:** shape 400 frames 0/1/2 — the same `fire field`. The endgame climax staged
three divine figures as open flames that damage the player walking the ceremony triangle.

**After:** `SHAPE_STATUE_STONE` = 443, frames 0/1/2 (three visually distinct carved stone
statues). Engine name `statue`; TYPEFLAG `[SI_FIXED, SI_SOLID]`, footpad (3,3,3).

**Evidence for the pick, including what was rejected:**
- 275 is also named `statue` and is more monumental (stone dragons), but footpad (6,6,6)
  is too large for the sanctum's spacing and the ±128 flanking resin props.
- 700 renders as the best *humanoid* statue, but its engine name is **`statue of Mordea`** —
  a U8 Pagan lore collision that a Zealan sanctum must not print on click.
- 443 is generic in name, modest in footpad, and offers three distinct frames.

**This is a mitigation, not a fix** — see "Genuinely unsolvable" below.

### 3. Map 18 ceremony altar — shape 721 → 550 (1 item)

**Before:** shape 721, engine name **`chimney`**. The endgame ceremony centerpiece — the
one object `AOSCENE.UNK` narrates the Avatar placing the artifact upon — was a squat brick
chimney that announced itself as such.

**After:** `SHAPE_ALTAR_STONE` = 550. Engine name `altar`; render is a carved stone altar
block; TYPEFLAG `[SI_SOLID, SI_LAND]`, footpad (2,4,2).

**Evidence for the pick:** 429 is also named `altar` but carries `SI_BAG`, so clicking a
ceremony altar would pop an empty container gump. 206 is named `Altar of Focus` — a
specific unrelated U8 artifact whose name would mislead. 550 is the clean choice.

**Safety:** the only `foreach` over `TypeStatue` (721) is `PLNTST.UNK`'s, scoped
`within 100 cells of referent` on Map 10, so it can never see a Map 18 item.

### 4. `lv_shapes.py` — three new verified constants

`SHAPE_SKELETON_SPRAWLED` (332), `SHAPE_STATUE_STONE` (443), `SHAPE_ALTAR_STONE` (550),
each documented with its engine name, render description, TYPEFLAG, what it replaced,
and which candidates were rejected and why.

---

## Verified correct — no action needed

- **Rock spires, shape 66** (the 5c78f60 partial fix). Confirmed: 12 frames of natural
  jagged rock-spire clusters. The swap away from 721 (`chimney`) was right.
- **Key to the Clouds, shape 82.** Confirmed: engine name `key blank`, 4 frames of a gold
  key lying flat, TYPEFLAG `SF_QUALITY`, not `SI_FIXED` (pickable). Reads correctly.
- **Elemental talismans, shape 596** (`gemstone ring`), and the **Passage Stone, shape 798**
  (`rock`). Both previously swept off the `SI_FIXED` shape 580; both confirmed carryable.

## Deliberately left alone

- **Decorative columns, shape 721** (37 on Map 17, 18 on Map 18). At frame 0 these render
  as a genuine grey-brown *stone* pillar — only frames 2/3 are red brick. Visually they
  are acceptable temple columns. The `chimney` click-name is a minor tell, not a
  category error. This is the "bland but fine" bucket; leaving them avoids churn and
  footpad risk for no real player gain.
- **Shapes 235/237** (bones). Already correct per commit 5c78f60.
- **Shades trigger egg, shape 73**, in its role as an invisible trigger egg. Correct
  *as a trigger*; its separate defect is listed below.

---

## Confirmed defects that this agent must NOT fix alone

These are real, evidence-backed defects. Each needs a coordinated change in
`u8c_symbols.py` (usecode-compiler agent) **together with** the map side. Doing only
half breaks the quest, so none were touched.

### A. BLOCKING — the Shield of the Ancients halves cannot be picked up

Map 17 places both halves as shape 580. **TYPEFLAG 580 is `SI_FIXED`** — they are
unpickable scenery. The Shield is the central quest item, and `AOSCENE.UNK` refuses to
run the endgame ceremony without it. This is the exact trap already swept twice (the
elemental talismans → 596, the Passage Stone → 798); nobody swept the Shield.

Shape 580 also has no engine name and renders as a 120-frame white magic-burst VFX, so
the halves currently look like a flash of light rather than an object.

**Recommended coordinated fix: 580 → 828.** Shape **828's engine name is
`Zealan ceremonial shield`** — an exact thematic match for the Shield of the Ancients in
a Zealan story. It renders as a dark oval shield with a red device, and TYPEFLAG is
`[SI_SOLID]` only (**not** `SI_FIXED`), so it is carryable, wt 3 / vol 10.

Requires: `TypeAOFrizbee` and `TypeAOArtifact` → 828 in `TYPE_SHAPES`, plus
`SHAPE_TALISMAN` in `build_map_17.py`. Caveat: 828 has a single frame, so the two halves
would look alike (they are already distinguished by quality 81/82, which no script reads);
and `SHADES.UNK` calls `create(TypeAOFrizbee, 4)` and `create(..., 2)`, so those two frame
arguments must drop to 0.

**Resolved in two steps.** 2026-07-19: the halves went to 539, carryable and
four-framed, because 828's single frame cannot tell them apart. 2026-10-08
(Douglas): the *restored* shield alone went to 828. `SHADES.UNK` creates it as
`TypeAOArtifact` (828) frame 0 with quality 83, the altar accepts only that
quality, and `lv-new/AORTA.UNK` replaces retail class 828 to name it.

### B. HIGH — the special root renders as a snake

The 2026-07-05 playtest report ("I see a 'snake skin' at the standing stones") is
**correct and reproducible**. Shape 399 is a reagent sheet: frames 0-1 are small blue
items, 2-3 bat wings, 4-8 snakes, 10-16 fire, 17-19 vials. **Frame 9 — the frame the quest
requires — renders at 10× as a large mottled green-and-brown coiled serpent.** The engine
name is `eye of newt`.

There is **no frame anywhere in shape 399 that reads as a root**, so no frame change can
rescue this. Both shape and frame are pinned by `EZREKAL.UNK`'s two
`foreach (type = TypeWeedz) and (frame = 9)` filters.

A genuinely root-shaped base-game shape does not appear to exist: an engine-name sweep for
root/weed/herb/tuber/vine returned only mushrooms (65, 217, 465, 466, 625, 626),
`plant bud` (376), and `potted plant` (753). The most plausible coordinated stand-in is a
mushroom cluster (a foraged organic reagent reads far better than a serpent), but it is a
compromise; this item is a candidate for new art.

### C. HIGH — the nightmare elixir renders as a crystal shard

**RESOLVED 2026-10-08** (Douglas's decision, lv-patched `EZREKAL.UNK`/`TYORVI.UNK`
V1): the four `13`s moved together, to **frame 5**, not the `0` recommended below.
All of frames 0-5 are the necromancy reagent Blood (retail `look()`: "vial of blood");
0 is the frame the Bag of Reagents stocks and the commonest blood frame placed in the
base game, and Tyorvi's drink filter destroys every carried item of the elixir's frame.
**SUPERSEDED 2026-10-09** (Douglas, V3): frame 5 still read "1 vial of blood" and merged
with carried blood, so the elixir got its own shape: `TypeBottle` → **868**, the vial
recoloured sea-green on donor 180's `SF_GENERIC` TYPEFLAG row, frame 0, class 868
(`lv-new/ELIXIR.UNK`) barking "Tyorvi's elixir" (`docs/art-track.md` contract 11).
The original finding follows.

**The comment at `u8c_symbols.py:191` is factually wrong.** It claims shape 395 frame 13
is "a blue/purple filled vial render, exactly the nightmare-elixir". It is not.
Frame 13 renders as an angular blue-grey **crystal/rock shard**. The actual vials on shape
395 are **frames 0-5** (red-filled vials). Frames 6-7 are rubble and 14-15 are mounds.

Cause: frame 13 is 1994 authorial intent, chosen when `TypeBottle` was shape **340**. The
2026-07-05 remap moved `TypeBottle` 340 → 395 to obtain a carryable vial but did not
re-check what frame 13 looks like on the new shape.

**Recommended fix: change the frame, not the shape.** Four hard-coded `13`s must move to
`0` together: `EZREKAL.UNK:3339` and `:3342` (`give`/`createNear`), and `TYORVI.UNK:2058`
and `:2088` (the two `foreach ... and (frame = 13)` filters). Shape 395's engine name is
already `vial`, so only the frame is wrong.

### D. MEDIUM — gold plaques render as a wooden stool

Map 17 places wall inscriptions as shape 158, which is a wooden stool (`SI_FIXED`, footpad
(3,1,3)). Shapes **599 and 614 are both named `plaque`** and are `SI_FIXED, SI_SOLID`
`SF_QUALITY` with wall-flat footpads ((0,2,2) and (2,0,2) — one per wall orientation),
which is exactly right.

Not fixable map-side: `PLAQUENS.UNK` declares `typeclass TypeNSGoldPlaque` with `look()`
and `use()` handlers dispatched off shape 158. Changing the map alone would leave a
correct-looking plaque that no longer responds to being read.

### E. MEDIUM — the Shades are invisible

Shape 73 has no sprite. The Sacred Circle ceremony depends on visible spirits speaking.
Shape **411 (`ghost`)** already exists in `lv_shapes.py` as `SHAPE_LB_APPARITION` and is
the obvious candidate, but `TypeShades` → 73 lives in `TYPE_SHAPES`.

### F. MEDIUM — elemental columns and the magnetic obelisk are chimneys

Both are shape 721 (`chimney`). The elemental puzzle requires telling four pillars apart,
and they are currently four identical chimneys. `COLPUZZL.UNK:139` does
`foreach pillar where type = TypeElementalColumn within 300 of referent`, so the shape is
pinned. For the obelisk specifically, shapes 442 (`obelisk tip`) and 793
(`glowing obelisk tip`) exist and are non-`SI_FIXED`.

**Status 2026-10-17.** The columns are custom art 865 (2026-09-24, `TypeElementalColumn`
re-pointed). The obelisk was custom art 861 from 2026-09-15 until 2026-10-17, when it
was retired for screen11's 1994 obelisk, which is retail pieces (12 f14-f17, cap 545,
skull 814) on banded 1994 columns (875); 861 is never reused (`.claude/rules/shape-ids.md`).

---

## Genuinely unsolvable without new art

These need new sprites; no base-game shape is a defensible stand-in, and this is out of
scope. Recorded so the question is not reopened.

- **Water Zombie** and **Harpie** — no aquatic-undead or winged-predator sprite exists in
  the base game that is not already a named U8 creature.
- ~~**The three Zealan gods.**~~ **RESOLVED 2026-09-13.** All six sprites exist
  (encased + freed × 3) as custom art, shape **860**, injected by
  `agents/map-populator/src/lv_god_statues.py` as step 4 of
  `tools/build_artifacts.sh`, TYPEFLAG from donor 443 with the footpad
  overridden to (6,6,8). `build_map_18.py` places frames 0/1/2 at the ceremony
  triangle — the first custom-art shape any map builder places, so this is the
  worked example for everything still on this list. Verified in ScummVM and
  against the built FIXED.DAT: `docs/playtest-2026-09-13-god-placement.md` and
  `agents/map-populator/src/test_sanctum_clearance.py`. Shape 443 and the nine
  rock-spire "resin" props are gone from the sanctum. **Frames 3/4/5 have
  never been drawn** — nothing calls `setFrame(n+3)`, so the freeing is still
  four barks in `AOSCENE.UNK`.
- ~~**Cloud terrain tiles.**~~ **RESOLVED.** Custom art 862 from 2026-09-15; since
  2026-10-17 the 1994 cloud floor cut from screen11, shape **874**, and 862 is retired.
- ~~**Shield halves as *distinct* left/right halves.**~~ **RESOLVED.** Retail 828 split
  at build time as shape 870 from 2026-10-11; since 2026-10-17 the 1994 halves cut from
  screen11/screen12, shape **878** (`TypeAOFrizbee`), and 870 is retired. The restored
  Shield is **879**, the 1994 altar Shield.
- **Zealan NPC cultural dress**, **Zealan child**, **Lord British**.

The proposed new-shape ID allocation (1500-1700) in `shared/docs/art-placeholder-audit.md`
remains valid.

---

## Verification

- `map_walkability.py` — **90 PASS, 0 FAIL**, before and after. Identical, so no swap
  changed collision or reachability (the footpad growth from 400's (3,3,9) to 443's
  (3,3,3) and 721's (2,2,5) to 550's (2,4,2) blocks nothing).
- `build_all_maps.py` — completes, **0 ERROR**, teleports **ALL OK**, 96,948 items across
  49 maps. Warnings dropped **13 → 11**; the 11 remaining are pre-existing floor-support
  and black-floor notes on shapes 508/114/78/174/411, none related to these swaps.
- Direct `FIXED.DAT` readback confirms shape **400 is now entirely absent from Maps 17
  and 18** (was 5 items), and that 332 ×2, 443 ×3, and 550 ×1 are placed at the intended
  coordinates with the intended frames and qualities.
- All referenced frames confirmed to exist: 332 has 3 frames (used 0,1); 443 has 4
  (used 0,1,2); 550 has 2 (used 0).
