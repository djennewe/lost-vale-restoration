# Organic maps pass 2 — art direction & macro design (FableDesigner)

All output under `/tmp/lv-maps-research/v2/FableDesigner/`. Repo untouched.
Context: AstraVale and AstraInteriors died mid-pass (usage limit), AstraCloud died
after two iterations; their partials are folded in below, and the Map 10 layout is
written implementation-grade because no Vale v2 mock exists.

## 1. Game-scale critique of the pass-1 mocks

Method: v1 mock crops are scale-2 renders (confirmed by 128-px tile-period
autocorrelation), resized ×1.5 to match the ×3 reference shots (0.75 px/world-unit)
and cropped to one camera frame. Sheets: `crit_map10_village.png`,
`crit_map10_lake.png`, `crit_map17_obelisk.png`, `crit_map13_summit.png`.

| Sheet | What still reads synthetic, and why |
|---|---|
| Map 10 village vs screen20 | **Material inversion**: ref frame is 62-77% dirt with rock at the margins; mock is rock-majority with dirt as scattered rust-colored crumbs (the 434/435/437 glob pool reads burnt, not earthen). **No elevation**: ref has three tiers in one frame (hut above, yard, drop below); mock is one plane with a uniform 2-course wall far away. **No composition**: ref is a ravine 6-8 tiles wide; mock huts float in an open field. Density ~1 prop/frame vs ref 4-6. |
| Map 10 lake vs screen02 | Black void corner visible IN frame; bank is a brown 126 causeway floating in water instead of ref's grey 128 teeth on rock shore; water fills the frame with no shore composition; zero props (ref: body, zombies, jawed creature, spikes). |
| Map 17 obelisk vs screen11 | Pillars are stacked square crates (233 recolour) vs smooth 15-16-px cylinders; drum mound too small so the pinned 861 dwarfs it; a dark marble pad under the obelisk that 1994 doesn't have; ring radius too big (2 pillars in frame vs 7); cloud slightly flatter/bluer than ref stipple. |
| Map 13 summit vs screen01 | Cloud patches are untextured flat white diamonds ("spilled paint"); dirt/rock boundary is chunk-quantised diagonals; dirt frames too dark/noisy; cliff faces repeat one striation frame; bones 1 cluster vs ref's litter. |
| Interiors (AstraInteriors' own v1 panels, `v2/AstraInteriors/map09_screen10_v1_v2.png` mid panel) | v1 floor = open moss plain with lone red mushrooms; no dais, no walls in frame — nothing a screen10 camera could recognise. |

Root causes carried into design rules: judge every change inside a 320×200 frame;
dirt/rock ratio per region; ≥2 elevation tiers or faces per frame near features;
edges lobed/ragged at sub-chunk resolution; props clustered (R≈0.2-0.3).

## 2. V2 macro layouts (all eight maps)

Delivered, with every pin at exact x/y/z, ASCII plans, world-coordinate regions,
z tiers + ramps, first-view-per-teleporter, material legends, acceptance windows:

- **`layout-map10.md`** — region plan (Hoskuld basin, Gunnar ravine, central scrub,
  southern lakes, mushroom garden, lava field + cliff gate, temple approach with
  gargoyle stair, Sacred Circle with z=96 horseshoe crest BEHIND the pinned z=0
  circle, z=64 south shelf anchored on the two pinned z=64 items, terraced NW
  cliffs to 288), road polylines, and a full implementation recipe (lattice
  autotile, glob pools, corner tables, budget ≈20k vs cap 32,510, test list) —
  self-contained for a fresh implementer.
- **`layout-map17-13.md`** — processional axis pad→gold street→obelisk forum→
  walkway Y→terraces→throne court; z rhythm cloud 0 / walkway 8 / terraces+obelisk
  plinth 16 / drum mound 16-96; colonnade every 192u both sides; ring radius 420;
  no void within 1500u of routes; gold laid first, cloud lobes lap over. Map 13:
  same xyz re-skin + valley pool with stepping stones (flagged), skull-ring harpie
  ledge, summit cloud shelf (cloud past the parapet, not black).
- **`layout-interiors.md`** — Maps 9/11/18 cave composition beats (arrival fissure →
  guardian chamber with 240 dais → south passage; four elemental wing identities;
  forecourt → outer hall → crack passage → sanctum), camera rule (wall within ~3
  tiles + 1 feature per frame on the spine), Map 8's three retail fixes, Map 39
  hedge/bush/void-band polish.

## 3. Sibling v2 partials: what landed, what's still owed

**AstraCloud** (`v2/AstraCloud/`): `m17_iterations_screen12.png` panels 3-4 are the
pass's best result — drawn 16-px banded posts, kerbed walkway, throne nook; close to
ref. `draft_art_sheet.png` drafts art 874-881 including an 18-frame cloud lobe set
(880) and cloud-over-gold set (881) — exactly the 1994 "Cloud globs". Outstanding
(my last review, unapplied): macro outline still diamond-stair-cornered — 880 must
be applied to every lobe rim; cloud too pure-white at game scale (restore 862's
blue-grey shadow ramp); obelisk pad must go, mound widen to 7-9 drums; screen13
panel's isolated puffs must become a connected sheet; gold 875 slightly
oversaturated; terraces/arrival unfurnished. Measurements to keep: ref posts ≈15px
wide (233 donor is 32 — recolours fail, drawn art required); obelisk foot in
screen11 sits ~40px above cloud — perch needs obelisk z40/56 = **user decision**,
default is the shallow pedestal.

**AstraInteriors** (`v2/AstraInteriors/`): `map09_screen10_v1_v2.png` v2 tomb dais
is a real screen10 read; `map18_screen04_v1_v2.png` sanctum-as-cave works;
`map11_pillar_screen07.png` niche staging works; `map39_hedge_v2.png` moat
bank/clumps good. Outstanding: black void stair-steps still visible in-frame on
every interior panel (floor-hole rule not yet fully applied); floors monotone 301
f0-6 (need f7-37/6/122 variation + bone scatter); dais lacks blood/stair; wall
texture repeats; fire-wing lava inlet too small; receptacle plinth too "Tenebrae".
Draft art: screen04 god plinths ×3 + fire-pillar cap (`draft_*_U8PAL.png`).

**AstraVale**: nothing produced — Map 10 has no v2 mock; `layout-map10.md` §recipe
is the hand-off.

## 4. Art needs (draft exists unless marked NEW)

| Pri | Item | State |
|---|---|---|
| 1 | 874 flat cloud + **880 lobe edges + 881 cloud-over-gold** | drafted (AstraCloud); fix shadow contrast |
| 2 | 877 banded column (16×~48 drawn) + 878 gem pillars ×5 | drafted, correct size confirmed |
| 3 | 875 gold brick, 876 drum, 879 marble walkway + trim | drafted; de-saturate 875 |
| 4 | screen04 god plinth | drafted (AstraInteriors) |
| 5 | 865 f2 banded fire-pillar cap (screen07 shows column, not flame) | drafted |
| 6 | Waterfall (screen09) | NEW — no shape identified, only art gap with no draft |
| 7 | Narrower 861 obelisk redraw | optional, flag only |

## 5. Risks
Unchanged from pass 1 (objID cap, overlay order, curbs, route/monster/paint tests —
each layout lists its own) plus: corner tables 386:5/6/10/14/15, 128:4/8/16 still
disputed, verify by eye before any builder work; user decisions pending: A glob
budget, B city translation (keep), C water/air lethality, D promontory (layout
fakes it with a rear crest), obelisk z raise, red keep replacement, real spring
water, Map 13 valley pool.

## 6. Ranked remaining gaps (v2 mocks → 1994 look)

1. **Map 10 has no v2 mock at all** — placement work, biggest absolute gap; recipe ready.
2. **Cloud edge application** (17/13): 880/881 drawn but not applied to rims — placement.
3. **Cloud shading contrast** — art tweak to 874 ramp.
4. **Interior floor holes + monotone floors** (9/11/18) — placement (void plates, frame variety, scatter).
5. **Dressing density/clustering everywhere** — placement (retail ~10/100 tiles clustered; all v2 panels still thin).
6. **Obelisk base mound + pad removal** (17) — placement.
7. **Walkway/terrace furnishing rhythm** (17) — placement.
8. **Gold palette + marble lavender tint** — minor art recolours.
9. **Waterfall** — new art, blocks only screen09 fidelity.
10. **Map 8/39 polish** — small, specified, unstarted in render form (39 partial exists).

Placement beats art 7:3 — the drafted art track is nearly sufficient; the remaining
distance to the 1994 shots is mostly builder geometry and density.
