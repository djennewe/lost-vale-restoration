#!/usr/bin/env python3
"""Measure the Avatar's final visible sprite fraction on the dry flood.

    python3 -B avatar_visibility.py 18 --step 32 --out /tmp/claude-1000/audits

Every unique (sprite frame, flipped) in WALK and STAND is evaluated for all
eight headings, using avatar_mover.sprite_frames and the built ANIM.DAT.
The final paint order comes from Painter.built().order, with the roof cut.
Pixels painted after the Avatar are accumulated using ItemSorter.mask.

Frames with identical sorter relations share one sort. The Avatar's body,
listLessThan key, and below decisions are pose-independent. Only rectangle
intersection and occlusion containment change with pose. Grouping on those
two exact predicates preserves the dependency graph and whole-item culls.
The Avatar has no SI_OCCL flag, so adding him cannot cull a static item.

test_route_reach is an executable test script with reachability targets,
and exposes no importable route paths. The route fallback includes every
reachable cell and is recorded explicitly in JSON and the low-cell list.
"""

import json
import time

import numpy as np
from PIL import Image

import avatar_mover as AM
import item_sorter as IS
from void_audit import (Scene, arguments, groups, heatmap, parallel, provenance,
                        reachable, validation_stops, write_json, distribution)

ROUTE_SOURCE = ('all reachable cells: test_route_reach executes tests on import '
                'and supplies reachability targets, without importable leg paths')
_SCENE = None
_POSES = None


class Poses:
    """Walking and standing sprites for the selected built actor body."""

    def __init__(self, painter, anim=AM.DEFAULT_ANIM, shape=1):
        self.shape = shape
        self.headings = {
            h: sorted({p for action in (AM.WALK, AM.STAND)
                       for p in AM.sprite_frames(action, direction, path=str(anim),
                                                 shape=shape)})
            for h, direction in AM.DIRS.items()}
        self.frames = sorted({p for poses in self.headings.values() for p in poses})
        self.rects, sprites = [], []
        for frame, flipped in self.frames:
            si = painter._make(IS._Item(shape, frame, 0, 0, 0,
                                       IS.FLG_FLIPPED if flipped else 0), 0, 0)
            if si is None:
                raise ValueError(f'missing Avatar frame {frame}')
            self.rects.append(si.sr)
            sprites.append(si)
        self.rects = np.array(self.rects, dtype=np.int32)
        self.bounds = (int(self.rects[:, 0].min()), int(self.rects[:, 1].min()),
                       int(self.rects[:, 2].max()), int(self.rects[:, 3].max()))
        l, t, r, b = self.bounds
        self.masks = np.zeros((len(sprites), b - t, r - l), dtype=bool)
        for k, si in enumerate(sprites):
            a, c, d, e = si.sr
            self.masks[k, c-t:e-t, a-l:d-l] = painter.mask(si)
        self.sizes = self.masks.sum(axis=(1, 2))
        if not self.sizes.all():
            raise ValueError('an Avatar pose has no opaque pixels')
        if painter.info(shape)['occl']:
            raise ValueError('pose grouping requires a non-occluding Avatar')


def visibility(scene, poses, spot, ids=None, details=False):
    """Exact sorter-relation groups, followed by final-order mask coverage."""
    x, y, z = spot
    p = scene.painter
    hx, hy = IS._div(x, 4) - IS._div(y, 4), IS._div(x, 8) + IS._div(y, 8) - z
    rect = tuple(a + (hx if k % 2 == 0 else hy)
                 for k, a in enumerate(poses.bounds))
    if ids is None:
        ids = scene.select(rect, scene.roof(spot))
    else:
        ids = [k for k in ids if IS._intersects(scene.sprites[k].sr, rect)]
    near = [scene.items[k] for k in ids]
    static = [scene.sprites[k] for k in ids]
    av = p._make(IS._Item(poses.shape, 0, x, y, z), 0, 0)
    av.sr = rect
    # The geometric parts of overlap and occludes are identical in all
    # poses. Evaluate those parts once, then vectorize the rectangle parts.
    geometric = np.array([IS.overlap(av, s) for s in static], dtype=bool)
    culls = []
    for s in static:
        av.sr = s.sr             # satisfy only the rectangle-containment test
        culls.append(s.occl and IS.below(av, s) and IS.occludes(s, av))
    bounds = poses.rects + np.array([hx, hy, hx, hy])
    if static:
        sr = np.array([s.sr for s in static])
        l, t, r, b = bounds.T[:, :, None]
        overlap = ((l < sr[:, 2]) & (r > sr[:, 0]) &
                   (t < sr[:, 3]) & (b > sr[:, 1]) & geometric)
        contained = ((sr[:, 0] <= l) & (r <= sr[:, 2]) &
                     (sr[:, 1] <= t) & (b <= sr[:, 3]) & np.array(culls))
        signatures = np.packbits(np.concatenate((overlap, contained), axis=1), axis=1)
        pose_groups = {}
        for k, sig in enumerate(signatures):
            pose_groups.setdefault(sig.tobytes(), []).append(k)
    else:
        pose_groups = {b'': list(range(len(poses.frames)))}
    visible = np.zeros(len(poses.frames))
    for members in pose_groups.values():
        frame, flip = poses.frames[members[0]]
        actor = dict(shape=poses.shape, frame=frame, x=x, y=y, z=z,
                     flags=IS.FLG_FLIPPED if flip else 0)
        seq = p.order([actor] + near, 0, 0, rect)
        position = next((k for k, si in enumerate(seq) if p._kmap[id(si)] == 0), None)
        if position is None:
            continue
        cover = np.zeros(poses.masks.shape[1:], dtype=bool)
        for si in seq[position + 1:]:
            l, t = max(rect[0], si.sr[0]), max(rect[1], si.sr[1])
            r, b = min(rect[2], si.sr[2]), min(rect[3], si.sr[3])
            if l < r and t < b:
                cover[t-rect[1]:b-rect[1], l-rect[0]:r-rect[0]] |= p.mask(si)[
                    t-si.sr[1]:b-si.sr[1], l-si.sr[0]:r-si.sr[0]]
        masks = poses.masks[members]
        visible[members] = np.count_nonzero(masks & ~cover, axis=(1, 2)) / poses.sizes[members]
    worst = int(visible.argmin())
    result = dict(x=x, y=y, z=z, min_visible=float(visible.min()),
                  median_visible=float(np.median(visible)),
                  worst_frame=poses.frames[worst][0],
                  worst_flipped=poses.frames[worst][1])
    if details:
        result['poses'] = [dict(frame=f, flipped=flip, visible=float(v))
                           for (f, flip), v in zip(poses.frames, visible)]
        result['sort_groups'] = len(pose_groups)
    return result


def visibility_chunk(task):
    key, spots = task
    _, ids = _SCENE.chunk(key)
    return [visibility(_SCENE, _POSES, p, ids) for p in spots]


def reference(scene, poses, spot):
    """Independent, ungrouped full-frame Painter.paint owner measurement."""
    from void_audit import camera, W, H
    sx, sy = camera(*spot)
    ids = scene.select((sx, sy, sx + W, sy + H), scene.roof(spot))
    near = [scene.items[k] for k in ids]
    values = []
    for (frame, flip), size in zip(poses.frames, poses.sizes):
        av = dict(shape=poses.shape, frame=frame, x=spot[0], y=spot[1], z=spot[2],
                  flags=IS.FLG_FLIPPED if flip else 0)
        _, _, own = scene.painter.paint([av] + near, sx, sy, W, H, owner=True)
        values.append(float((own == 0).sum() / size))
    return np.array(values)


def validate(scene, poses, mapnum, tour, outdir):
    # These labels describe the supplied reviewers' actual capture verdicts.
    hidden = {'m18-12', 'm18-15', 'm18-16', 'm09-16', 'm09-17',
              'm11-49', 'm10b-64', 'm10b-52'}
    clean = {'m17-01', 'm13-02'}
    rows = []
    for stop, capture in validation_stops(mapnum, tour):
        if stop['id'] not in hidden | clean:
            continue
        # Reading the actual capture also verifies its size and existence.
        with Image.open(capture) as image:
            if image.size != (640, 400):
                raise ValueError(f'{capture}: expected 640x400')
        spot = tuple(stop[k] for k in ('x', 'y', 'z'))
        result = visibility(scene, poses, spot, details=True)
        direct = reference(scene, poses, spot)
        fast = np.array([v['visible'] for v in result['poses']])
        result.update(id=stop['id'], reviewer_hidden=stop['id'] in hidden,
                      predicted_hidden=result['min_visible'] < .5,
                      reference_max_error=float(np.abs(direct - fast).max()))
        result['agrees'] = result['reviewer_hidden'] == result['predicted_hidden']
        rows.append(result)
    write_json(outdir / f'avatar-map{mapnum:02d}-validation.json', rows)
    return rows


def main():
    args = arguments(__doc__.splitlines()[0])
    start = time.monotonic()
    global _SCENE, _POSES
    _SCENE = Scene(args.map, args.fixed, args.retail_art)
    _POSES = Poses(_SCENE.painter, _SCENE.anim)
    cells, arrival = reachable(args.map, _SCENE.raw, args.arrival, _SCENE.typeflag)
    tasks = groups(_SCENE, cells, args.step)
    print(f'map {args.map}: {len(cells)} reached; {sum(len(s) for k,s in tasks)} '
          f'sampled; {len(_POSES.frames)} walk and stand poses; '
          f'{args.workers} workers', flush=True)
    rows = [r for batch in parallel(visibility_chunk, tasks, args.workers) for r in batch]
    rows.sort(key=lambda r: (r['x'], r['y'], r['z']))
    low = sorted((r for r in rows if r['min_visible'] < .5),
                 key=lambda r: (r['min_visible'], r['median_visible'], r['x'], r['y'], r['z']))
    shares = np.array([r['min_visible'] for r in rows])
    summary = dict(cells=len(rows), reachable_cells=len(cells),
                   status='measured' if cells else 'empty_map',
                   record_counts=_SCENE.record_counts,
                   poses=len(_POSES.frames),
                   min_visible=float(shares.min()) if len(shares) else None,
                   median_min_visible=float(np.median(shares)) if len(shares) else None,
                   min_visible_distribution=distribution(shares),
                   median_visible_distribution=distribution([r['median_visible'] for r in rows]),
                   cells_below_half=len(low),
                   cells_completely_hidden=int((shares == 0).sum()),
                   quest_route_source=ROUTE_SOURCE)
    write_json(args.out / f'avatar-map{args.map:02d}.json',
               dict(map=args.map, step=args.step, arrival=arrival, shares='fractions',
                    camera_z_offset=20, provenance=provenance(_SCENE), summary=summary,
                    frames_by_heading=_POSES.headings, cells=rows))
    write_json(args.out / f'avatar-map{args.map:02d}-quest-low.json',
               dict(route_source=ROUTE_SOURCE, threshold=.5, cells=low))
    # Heatmap uses the worst level at each XY; red means hidden.
    if rows:
        heatmap([dict(r, hidden_share=1-r['min_visible']) for r in rows], 'hidden_share',
                args.out / f'avatar-map{args.map:02d}.png', args.step,
                f'Map {args.map}: worst walk and stand occlusion')
    with (args.out / f'avatar-map{args.map:02d}-quest-low.tsv').open('w') as f:
        f.write(f'# {ROUTE_SOURCE}\nx\ty\tz\tmin_visible\tmedian_visible\tworst_frame\tflipped\n')
        for r in low:
            f.write(f"{r['x']}\t{r['y']}\t{r['z']}\t{r['min_visible']:.6f}\t"
                    f"{r['median_visible']:.6f}\t{r['worst_frame']}\t{r['worst_flipped']}\n")
    if args.validate_tour:
        validate(_SCENE, _POSES, args.map, args.validate_tour, args.out)
    summary['elapsed_seconds'] = round(time.monotonic() - start, 2)
    write_json(args.out / f'avatar-map{args.map:02d}-summary.json', summary)
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
