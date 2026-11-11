Lost Vale walkable map viewer
=============================

One page per Lost Vale map (10, 11, 13, 17, 18, 9, and the retail maps the
expansion edits, 8 and 39) and an index. Walk the
Avatar about with WASD or the arrow keys (Shift runs), drag to pan, wheel or
the selector to zoom, click a location in the sidebar to jump there. The URL
hash (#x,y,z,zoom) is a link to where you stand.

LIVE FEEDBACK

Served through tools/map_viewer/feedback_server.py, every page can take
notes pinned to a world position: F drops one where the Avatar stands,
right-click drops one on the surface under the cursor. A note carries a kind
(bug, visual, walkability, idea, looks right), the text, the FIXED.DAT hash
it was made against, an optional snapshot of the view, and the items the
server finds within 96 units of the pin (shape:frame, name, x/y/z,
footpad), so an agent can go straight to the record. Pins and the sidebar
list update live (Server-Sent Events) in every open page; replies and
fixed / won't-fix status flow back the same way and pop a toast.

  events.jsonl   docs/map-feedback/, append-only, one event per line;
                 `tail -f` it to follow a walk as it happens
  OPEN.md        docs/map-feedback/, the open notes with their nearby items,
                 regenerated on every change
  snapshots      <site>/feedback-shots/ (Origin art: never committed)

Agents answer with curl, which the walker sees at once:

  curl -s localhost:8460/api/notes/7/reply \
       -d '{"who":"agent:codex","text":"moved the wall to x 20480"}'
  curl -s localhost:8460/api/notes/7/status \
       -d '{"who":"agent:codex","status":"fixed"}'

Opened as a file or from a plain static host, the Feedback section says
"offline" and the rest of the viewer works as before.

On kaga it runs as the user unit lv-map-viewer.service (127.0.0.1:8460) and
is published on the tailnet at https://devhost.invalid/lostvale-maps/
(`tailscale serve --set-path /lostvale-maps/`). The site directory is
~/projects/lost-vale-maps/site; regenerate it after a FIXED.DAT change with
the command below and `--out ~/projects/lost-vale-maps/site`. Notes made
against an older build say so in the sidebar.

HOW IT WAS MADE

  tools/map_viewer/build_map_viewer.py   (generator)
  tools/map_viewer/viewer.html            (page template; no CDN, no deps)
  tools/map_viewer/locations.json         (named places, with sources)

The generator reads the BUILT artifacts in shared/build (FIXED.DAT,
U8SHAPES.FLX, TYPEFLAG.DAT, ANIM.DAT, GLOB.FLX) plus U8PAL.PAL from the
install, and reuses the map-populator toolchain rather than a second
renderer:

  * u8_map.MapArchive reads the map; map_preview.expand_globs and
    glob_catalog.GlobReader expand every glob egg as GlobEgg::enterFastArea
    does (x/y * 2 + 1 inside the egg's 512 chunk, z added);
  * item_sorter.py (the port of ScummVM's ItemSorter / SortItem) gives the
    projection, the frame decoding and the paint rules. The projection is
    SortItem::setBoxBounds': screen x = x/4 - y/4, screen y = x/8 + y/8 - z,
    C division per term, the frame's hotspot on that point (mirrored for
    FLG_FLIPPED). The generator builds the engine's dependency graph over the
    WHOLE map (below() / overlap() / occludes(), insertion in the engine's
    list order, a spatial hash instead of the all-pairs loop) and paints it
    depth-first as PaintSortItem does, so occlusion is the engine's, not a
    (x + y, z) sort. SI_OCCL culling is applied as the engine applies it.
  * SI_TRANSL shapes are blended as RenderSurface::PaintTranslucent blends
    them: palette indices with a U8XFormPal entry (8-14) become
    (dst * (256 - a) + 256 * c) >> 8; every other index is opaque.
  * Not drawn, as GameMapGump does not draw them: SI_EDITOR shapes (eggs,
    the invisible 497/498 rails), FLG_INVISIBLE and FLG_CONTAINED items.
    They are in the overlay instead (toggle per kind), with the hatch box
    of every egg and teleporter (x +/- 32 * xrange, y +/- 32 * yrange) and
    map_pins.json's explanation on hover.

Tiles: 512 px lossless WebP, level 0 = 1x game pixels, then 1/2, 1/4, 1/8
(box-filtered). 2x, 3x and 4x are the 1x tiles drawn pixelated (identical to
rendering at 2x). Only tiles with content exist; the page loads the ones in
view, drawing a coarser loaded tile until the right one arrives.

Roofs: a second layer, rendered only for tiles a roof touches (Map 10 only;
the other maps have no SI_ROOF items). It cuts what GameMapGump cuts with
the Avatar under a roof: every item at or above the z of an SI_ROOF item
whose bottom is 36 or more above the cell's floor (the camera box top,
CameraProcess::findRoof) and that covers the item's centre, unless SI_DRAW.
The page switches to it automatically while the Avatar stands under a roof,
as the game does, or everywhere with the "roofs off" box.

Walking: the Avatar is shape 1 drawn at game scale, frame by frame from
ANIM.DAT (stand = action 2, walk = action 0, run = action 1), each frame's
step distance taken from the animation and played at the engine's 30
frames a second with the action's frame repeat. That is the game's walking
speed (about 100 world units a second). Keys are screen directions, as the
game's mouse is: up = north-west, right = north-east. There is no collision:
the marker walks through walls. Height follows the surfaces (SI_LAND or
SI_SOLID tops on a 32-unit grid): a step of up to 8 is taken
(scanForValidPosition probes 0, +/-4, +/-8), anything higher is not, and a
drop is followed. Q / E move to the surface above / below. The yellow
diamond under the Avatar is his 64 x 64 footpad, so he can be found behind
a wall; the sprite is always drawn on top.

REGENERATING

From the main checkout, after tools/build_artifacts.sh (the published site):

  python3 tools/map_viewer/build_map_viewer.py \
      --data-root ~/projects/lost-vale \
      --out ~/projects/lost-vale-maps/site

(--maps 10 13 to do a subset; --format png for PNG tiles.) It rewrites the
map directories, the pages, avatar.png, index.html and this README; it does
not touch compare/ or screens/. Then, for the comparison sheets:

  python3 tools/map_viewer/compare_shots.py \
      --data-root ~/projects/lost-vale \
      --out /tmp/claude-1000/gallery/maps

The tiles contain Origin art: they are not committed.

FAITHFULNESS (checked 2026-10-12 against in-engine ScummVM screenshots)

tools/map_viewer/compare_shots.py writes compare/<spot>.png: left the
ScummVM shot, middle this viewer's tiles at the shot's scale, right in
magenta every pixel that differs by more than 12/255 in any channel. Each
pair is aligned by searching +/-8 px for the best offset (the engine's
camera does not sit exactly on the logged position). compare/results.txt:

  spot            map  shot (docs/...)                               match
  plateau          10  playtest-2026-10-11-static-art/P1-...-1x       98.4%
  sacred-circle    10  playtest-2026-10-11-static-art/R1-...-1x       98.9%
  lake-deck        10  playtest-2026-10-12-monsters3/P3-deck-fight    95.9%
  map17-arrival    17  playtest-2026-10-11-replay-leg4/D3-...         98.6%
  map18-arrival    18  playtest-2026-10-11-replay-leg5/A2-...         98.6%
  map13-arrival    13  playtest-2026-10-11-full-run-part6/s13-01      65.9%

In the first five every differing pixel is a live actor or the cursor: the
Avatar, the three Water Zombies on the deck, the blue target arrow, and on
the plateau a one-pixel line along the bottom edge (cause not examined).
Floors, walls, props, water, stones, the Test plant (871), the root (869),
the columns and the occlusion between them match pixel for pixel. The
Map 13 shot predates a map change: it shows the valley's south rim (two
courses of rock and a crest) beside pad 207, and build_map_13.py build_rim
made that edge flush after build 7 ("a hold S off pad 207 ended against the
south rim ... its 96-high courses covered 100% of the Avatar"). The ground
itself matches; the rock is gone from today's FIXED.DAT, so it is gone here.

screens/ holds the headless-browser check: one shot per page after a
location jump and a walk, plus Map 10 at 1/8x and the index.

What differs, and why:
  * Actors. The Avatar, the monsters and the cursor arrows in the shots are
    live actors. NPCs ARE drawn here, at their FIXED.DAT start positions;
    in the game they move on their schedules. Monsters only exist once their
    egg hatches, so none are drawn; the overlay marks the eggs and triggers.
  * Runtime items. Anything usecode creates or moves at runtime (scene
    props, dropped items, opened doors, the crack once templeOpen is set)
    is shown as FIXED.DAT has it.
  * Animation. Shapes TYPEFLAG marks animated (the wall lamps 314/317, the
    candlesticks 452/453, Map 11's 409 floor and 435-437, 318, the gods
    860) are drawn at their placed frame and do not cycle.
  * Lighting. U8 has no lighting model; the palette is the same. The
    6-bit-to-8-bit palette scale here is (v << 2) | (v >> 4); ScummVM's is
    v * 255 / 63 (graphics/palette.h), at most one step apart, inside the
    12/255 tolerance above.
  * Paint-order cycles. Where below() is intransitive the engine breaks the
    cycle where its walk meets it; this viewer sorts the whole map at once,
    so a cycle may break at a different item than in a 640x400 view.
  * Camera and roofs. The roof cut is computed per 32-unit cell from the
    roofs over each floor, not live from the camera, and the cut layer
    shows every roof cut at once.

The iso_render gap (TODO.md: "iso_render.py showed the Map 17 tapestry in
full where ScummVM hid it behind the east wall"). This viewer does not use
iso_render's (x + y, z) order; it paints in the engine's dependency order.
Re-hanging the tapestry (shape 329 frame 5) at its two retired spots on
today's Map 17 and rendering with this painter:
  * x 6016 (until 2026-10-03; ScummVM: the east wall paints in front of all
    of it, a sliver at most): 20 of its 999 pixels visible, rows 0-5 only;
  * x 5847 (ScummVM 2026-10-04 C2: "the bottom 7 or so rows are behind a
    wall top"): the bottom 7 rows hidden, 863 of 999 pixels visible;
  * x 4607 (today's spot; ScummVM: drawn whole): drawn whole.
So for wall-mounted flats this viewer agrees with the engine. (Today's
iso_render.py hides the tapestry at both retired spots too, 33 and 29
pixels visible, so the 2026-10-03 disagreement in that TODO line did not
reproduce on today's FIXED.DAT; its cause was not examined.)
