# Maps 17 (Cloud City) + 13 (Cloud Cliffs) — macro layout v2 (FableDesigner, 2026-10-12)

For AstraCloud. World units; tile = 128, chunk = 512. All pins exact.

## Why v1 failed at game scale
Compare mock17_obelisk.png to x3/screen11:
1. **Void in frame.** screen11 is 100% cloud to every frame edge; v1 has black void
   intruding beside the obelisk and at every mock edge. Rule: no void pixel within
   1.5 screens (~1500 units) of any walkable route or vista point. Void appears only
   past deliberate "cloud banks" at the map rim.
2. **Edges are 128 stair-steps.** screen13's cloud lobes are puffy half-disc bites
   192-384 across with scalloped art. Needs edge art (874 f1-4) + lobed geometry.
3. **Black sorting tears** along gold↔cloud seams in v1. Gold field must be laid
   first, cloud lobes lap OVER its boundary by 1 tile (screen12/13 both show cloud
   overlapping gold, never a hard butt joint).
4. **No elevation.** screen12's walkway is raised with kerb trim; v1 is one plane.
5. **Rhythm wrong.** screen12 has a drum column roughly every tile BOTH sides of the
   walkway; v1's ring pillars are ~5 tiles apart and read as lost chess pieces.
   screen11's ring is tight: pillars ~2-3 tiles from the drums.
6. **Pillars read as stacked crates** (233 f3 square caps). Art 877/878 (smooth round
   banded column, gem cap) is the single highest-leverage art item for this map.
7. **Obelisk base too small.** screen11 shows ~7-9 drums in a 2-high mound; v1 has a
   thin cluster that the obelisk dwarfs.

## Macro plan (1 char = 512 units; x → 0..16, y ↓ 0..24; map corner 0,0)
```
      x 0   2   4   6   8   10  12  14  16
 y 0   ..~~~~~KK~~~SS.HH~HH~~~....        K = scroll kiosk (3328,1536,8)
   2   .~~~AAA~~~~~BBB~~~~~~~.           S/H = skeletons + shield halves (6208,1568)(7232,1568)
   4   .~~AAAA~.P.~BBBB~~~..             A/B = god's terraces, route goals (2304,3328)(5888,3328)
   6   ..~~WWW~~~~WWW~~~..               P = plaques 69/70 steles (2495,5121,16)(5055,5121,16)
   8   ...~~~RRROOORR~~~~..              O = obelisk (4095,7167,16), R = pillar ring + drums
  10   ..~~~~~RRPRR~~~~~..               P(y8-10) = plaques 55/68 (4127,7680,16)(5055,9217,16)
  12   .....~~~GGG~~~~....               G = gold forum
  14   ....~~~~GGG~~~....
  16   ......~~GGG~~~....                ~ = cloud sea (fills everything between features)
  18   .....~~~GGG~~~....                . = void, only past the outer cloud banks
  20   ....~~~~GTG~~....                 T = pad 209 (5376,11136,0) + trigger 208 (5376,11520,0)
  22   ......~~~T~~~....
  24   ..........
```
North (low y) = throne court + kiosk; south (high y) = arrival. Processional axis:
arrival gold landing → gold street N → obelisk forum → walkway Y → terraces A/B →
throne court + scroll kiosk. (Screen-space: lower y projects up-right.)

## Elevation (the fix for flatness)
| Level | z | What | Edge |
|---|---|---|---|
| cloud sea | 0 | 874 flat cloud everywhere walkable | lobed scallop vs void, invisible curbs |
| walkways | 8 | 37 f11/13/14/15 marble spine from forum to terraces + throne court | 45 f3 / 84 f4 gold kerbs BOTH long edges, continuous |
| terraces/steles | 16 | god's terraces A/B, plaque steles, obelisk plinth disc r≈400 | kerb + one marble step (8→16) on the axis |
| drum mound | 16-96 | obelisk base: 3×3 drums at z16 + 2×2 second course z56 (obelisk pinned (4095,7167,16) rises from the mound centre) | — |
Pinned z respected: scroll 864 (3328,1536,8) sits on walkway level; plaques all z=16
on stele terraces; shield halves z=0 on cloud in throne court; pads z=0 on cloud/gold.

## Rhythm + furniture
- **Walkway colonnade:** white/gold drums (876, interim recolour 233 f2) every **192
  units both sides**, height 2 drums (80). This is the screen12 signature — do not
  thin it out.
- **Obelisk ring:** 10 gem pillars (878/877; interim 233 stack + 346 gem) at radius
  **420** from (4095,7167) — pillars 2-3 tiles outside the drum mound, as screen11.
- **Throne court (6100-7400, 1200-2000):** two 223 thrones at (6656,1280,0) and
  (7040,1280,0) facing SE, rubble 524 f2/3 ring, blue vases 183 f2, checker inlay
  under the rubble (556 pale frames), skeletons pinned (6144,1536)(7168,1536), shield
  halves pinned. Boxes must not overlap pins (v1 buried half 1 once).
- **Scroll kiosk (3328,1536):** 4 drums + 2 gem pillars around the pinned plinth.
- **Gold areas:** organic patches (noisy capsules), brick 875 (interim 34), cloud lobes
  lapping every boundary; the arrival landing and the forum are gold.
- Scatter: bottles 180, bone piles near skeletons — Cloud City is a dead city.

## First view at pad 209 (5376,11136)
Gold landing underfoot lapped by cloud; drum colonnade marching up-screen; obelisk +
pillar ring on the horizon up-left; no void visible in any direction at scale 1.

## Edges / safety
Invisible 497/498 curbs on every cloud lobe rim (~600+); exact_reach flood after.
Route goals Hall A (2304,3328) / Hall B (5888,3328) stay on terrace floor.

## Acceptance windows (scale 1, ×3, side-by-side)
- (4095,7167) centred vs x3/screen11 — ring spacing, drum mound, zero void.
- (6700,1500) throne court vs x3/screen12 — kerbed raised walkway + 192-unit colonnade in frame.
- (5376,11136) arrival — gold lapped by cloud, colonnade leading away.

---

# Map 13 Cloud Cliffs v2

Every walkable tile keeps x/y/z; curbs/parapets/eggs/teleports/CLIMB_WAYPOINTS frozen.
Pins: valley trigger 206 (3328,11520,0) → Map 10, pad 207 (4096,11776,0) arrival;
summit pad 208 (4096,512,120) arrival from 17, trigger 209 (4096,128,120) → 17;
harpie eggs (3328,512,120)(3584,256,120)(4000-4192,3072,100), triggers (4096,1152,120)
(4096,3584,92); egg q297 (4096,11264,0).

Composition goal per screen16/01: at game scale a climb screen shows the face you are
on, the tier above, and the drop below — three tiers in frame. v1 re-skin keeps
geometry, so the work is material + dressing + the two ends:
1. Valley (y 10200-12280): glob 397 rock; dirt path (4/386) from pad 207 to the climb
   foot; 425 only at the very foot. **Base water feature** (screen15/16): a dark
   347 f14-16 pool against the east wall (4600-5600, 10400-11300) with 128 rim and
   186/796 stepping stones — clear of trigger 206's hatch box (±384×448) and the
   path; rails on deep edges. Flag: new water on 13 → re-run monster/route tests.
2. Climb: faces get striation variety (26-32 full family, short runs), bone clusters
   (235/237/332) on ledges, skull ring 745 + blood at the (4000,3072,100) harpie
   ledge (screen14), spires 66 on crest noses.
3. Summit (y<1600, z=120): dirt + flat-cloud (874) noise mix, cloud fraction rising
   toward north edge; **north/top edge drops into cloud, not black** (screen01) —
   cloud shelf 2-3 tiles wide past the parapet line (non-walkable, curbed). Gold-brick
   corner by trigger 209 (approach to the city). Trunk 74 f1 at (3200,896,120),
   spires, bones.
4. Avoid 435-438 (SEA|DAMAGING foam).

Acceptance: (4096,3200) climb window vs x3/screen16; (4096,512) summit vs x3/screen01
(cloud past the edge); (4800,11000) valley pool vs x3/screen15.
