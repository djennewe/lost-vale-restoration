#!/usr/bin/env python3
"""vignette_replay.py - replay a 1994-screenshot vignette and score it.

    python3 agents/map-populator/src/vignette_replay.py screen11 [screen12 ...]
    python3 agents/map-populator/src/vignette_replay.py            # all vignettes
        --built          paint retail shapes from shared/build/ instead of the
                         retail .bak files (the 1994 art always comes from the
                         registry), and the `built` actors
        --check          exit 1 unless every replay equals its published render
        --publish        (re)write the published render + diff from the replay
                         (with --built: the built render + diff, verify.built)
        --write-verify   write the score contract into the vignette's `verify`
                         (with --built: into `verify.built`)
        --validate-art   re-run the cross-shot search for every registry
                         frame and print it beside the registry grade (minutes)

One replay manifest:
  * vignettes/screenNN.json - items {shape, frame, x, y, z[, flags]} in the
    vignette-local frame; world = placement.origin_world + local.  `shape` is
    a retail shape (< 860) or a 1994 art id (>= 2000) from the registry.
    Actors carry a concrete frame, or `unrendered: true` plus `art_1994`
    {id, frame} and `screen_xy` (the sprite's top-left in the shot) when the
    actor is 1994-only art the replay does not paint.  `built: true` marks
    an actor whose shape exists only in the built artifacts (the 1994
    actors lv_actor_art.py derives: 872, 888-890): `--built` paints it at
    its solved position; the retail replay treats it as unrendered (not
    painted, its art_1994 pixels the excluded-actor mask), so the retail
    contract never reads shared/build/.
  * vignettes/art_registry.json - every 1994 art id: frames (repo-relative
    P-mode PNG, palette index 255 transparent, numeric hotspot), footprint in
    world units, sort flags, kind and cross-shot grade.
  * camera {sx0, sy0} in the painter's sign, vignette-local frame:
        screen_x = x/4 - y/4 - sx0,  screen_y = x/8 + y/8 - z - sy0
    (C division per term, as the engine).  The replay paints in WORLD
    coordinates - every item at origin_world + local, the camera shifted to
    match (origins are multiples of 8, so the shift is exact) - because that
    is what the engine paints: C division and the 512-unit chunk order both
    depend on the absolute coordinate.

Score contract (percent of all frame pixels, unpainted = mismatch):
  all_frame_strict     painted and RGB-identical to the shot's nearest palette
                       entry
  all_frame_class      painted and in the shot pixel's palette class
                       (shot_decompose.CLS: entries within 12 L1 merged)
  void_as_black_points what counting unpainted void as the engine's black
                       background would add (unpainted and shot class black)
  excluded_actor_points what excluding the unpainted 1994 actors' sprite
                       pixels from the frame would add to all_frame_class
  provenance_points    matched (class) pixels by the art that painted them:
                       retail / cross_shot_validated_1994 / single_shot_1994
                       (single-shot, reference-only and residual grades) /
                       inferred (registry inferred_px) / unmatched; a
                       `built` actor's pixels count by its art_1994
                       frame's grade (its built frame is that cut-out)
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
from shot_decompose import CLS, PAL, SHOTS_DIR  # noqa: E402
from vignette_paint import Painter  # noqa: E402

VIGNETTE_DIR = os.path.join(HERE, 'vignettes')
REGISTRY = os.path.join(VIGNETTE_DIR, 'art_registry.json')
FIRST_1994_ID = 2000
BLACK = CLS[0]


def rel(path):
    return os.path.relpath(path, REPO)


def load_registry(path=REGISTRY):
    with open(path) as f:
        return json.load(f)


def load_vignette(shot):
    with open(os.path.join(VIGNETTE_DIR, f'{shot}.json')) as f:
        return json.load(f)


def save_vignette(vig):
    with open(os.path.join(VIGNETTE_DIR, f"{vig['shot']}.json"), 'w') as f:
        json.dump(vig, f, indent=1)
        f.write('\n')


def all_shots():
    return sorted(f[:-5] for f in os.listdir(VIGNETTE_DIR)
                  if f.startswith('screen') and f.endswith('.json'))


def read_png(path):
    im = Image.open(os.path.join(REPO, path))
    if im.mode != 'P':
        raise ValueError(f'{path}: {im.mode} image; 1994 art must be P-mode U8PAL')
    return np.array(im)


def frame_dict(entry):
    a = read_png(entry['png'])
    hx, hy = entry['hotspot'] if entry['hotspot'] is not None else (0, 0)
    return dict(pixels=a.astype(np.uint8).flatten().tolist(), width=a.shape[1],
                height=a.shape[0], xoff=hx, yoff=hy)


def make_painter(registry, built=False):
    p = Painter.built() if built else Painter()
    for sid, ent in registry['shapes'].items():
        if ent['footprint'] is None:          # residual masks: never placed
            continue
        flags = ent.get('flags') or {}
        p.add_shape(int(sid), [frame_dict(fr) for fr in ent['frames']],
                    *ent['footprint'], solid=flags.get('solid', True),
                    land=flags.get('land', False))
    return p


def shot_size(vig):
    with Image.open(os.path.join(SHOTS_DIR, vig['shot'] + '.gif')) as im:
        return im.size


def shot_index(shot):
    """Nearest U8PAL index of every shot pixel (L1)."""
    rgb = np.array(Image.open(os.path.join(SHOTS_DIR, shot + '.gif')).convert('RGB')).astype(int)
    return np.abs(rgb[:, :, None, :] - PAL[None, None]).sum(-1).argmin(-1)


def world_camera(vig):
    ox, oy, oz = vig['placement']['origin_world']
    if ox % 8 or oy % 8:
        raise ValueError(f"{vig['shot']}: origin_world x,y must be multiples of 8")
    cam = vig['camera']
    return cam['sx0'] + ox // 4 - oy // 4, cam['sy0'] + ox // 8 + oy // 8 - oz


def painted(a, built):
    """Does this replay paint actor `a`?"""
    return not a.get('unrendered') and (built or not a.get('built'))


def scene(vig, built=False):
    """The painted items in world coordinates: map items, then rendered actors."""
    ox, oy, oz = vig['placement']['origin_world']
    out = []
    for it in vig['items']:
        out.append(dict(shape=it['shape'], frame=it['frame'], x=it['x'] + ox,
                        y=it['y'] + oy, z=it['z'] + oz, flags=it.get('flags', 0)))
    for a in vig['actors']:
        if not painted(a, built):
            continue
        out.append(dict(shape=a['shape'], frame=a['frame'], x=a['x'] + ox,
                        y=a['y'] + oy, z=a['z'] + oz, flags=a.get('flags', 0)))
        if a.get('built') and 'art_1994' in a:
            out[-1]['art_1994'] = a['art_1994']    # its frame IS that cut-out
    return out


def replay(vig, painter, built=False):
    """(palette-index image, -1 = unpainted; owner item index; items;
    per-item (left, top, flipped) screen placement)."""
    items = scene(vig, built)
    W, H = shot_size(vig)
    img, seq, own = painter.paint(items, *world_camera(vig), W, H, owner=True)
    place = {painter._kmap[id(si)]: (si.sr[0], si.sr[1], si.flipped) for si in seq}
    return img, own, items, place


def to_rgb(img):
    out = np.zeros(img.shape + (3,), np.uint8)
    d = img >= 0
    out[d] = PAL[img[d]]
    return out


def published_rgb(vig, built=False):
    """The published render as RGB, or None.  Older Vale renders are a
    shot | render | diff composite at x3; read its middle panel."""
    path = os.path.join(REPO, (built_paths(vig) if built
                               else vig['verify'])['render'])
    if not os.path.exists(path):
        return None
    im = np.array(Image.open(path).convert('RGB'))
    W, H = shot_size(vig)
    if im.shape[:2] == (3 * H, 9 * W):
        im = im[:, 3 * W:6 * W][::3, ::3]
    return im


def actor_mask(vig, registry, shape, built=False):
    """Frame pixels of the 1994 actors' sprites this replay does not paint."""
    H, W = shape
    m = np.zeros((H, W), bool)
    for a in vig['actors']:
        if painted(a, built) or 'art_1994' not in a:
            continue
        ref = a['art_1994']
        fr = registry['shapes'][str(ref['id'])]['frames'][ref['frame']]
        spr = read_png(fr['png']) != 255
        x, y = a['screen_xy']
        h, w = spr.shape
        y0, y1, x0, x1 = max(y, 0), min(y + h, H), max(x, 0), min(x + w, W)
        m[y0:y1, x0:x1] |= spr[y0 - y:y1 - y, x0 - x:x1 - x]
    return m


def score(vig, registry, img, own, items, place, sidx, built=False):
    Sc = CLS[sidx]
    drawn = img >= 0
    safe = np.where(drawn, img, 0)
    strict = drawn & (PAL[safe] == PAL[sidx]).all(-1)
    match = drawn & (CLS[safe] == Sc)
    total = img.size
    pct = lambda n: round(100.0 * float(n) / total, 3)   # noqa: E731
    ex = actor_mask(vig, registry, img.shape, built)
    excl = (100.0 * match[~ex].sum() / (~ex).sum() - 100.0 * match.mean()) if ex.any() else 0.0

    prov = dict(retail=0, cross_shot_validated_1994=0, single_shot_1994=0, inferred=0)
    inferred_sets = {}
    for k, it in enumerate(items):
        sel = match & (own == k)
        n = int(sel.sum())
        if not n:
            continue
        sid = it['shape']
        if 'art_1994' in it:
            ref = it['art_1994']
            g = registry['shapes'][str(ref['id'])]['frames'][ref['frame']]['grade']
            prov['cross_shot_validated_1994' if g == 'cross-shot-validated'
                 else 'single_shot_1994'] += n
            continue
        if sid < FIRST_1994_ID:
            prov['retail'] += n
            continue
        fr = registry['shapes'][str(sid)]['frames'][it['frame']]
        inf = 0
        if fr.get('inferred_px'):
            key = (sid, it['frame'])
            if key not in inferred_sets:
                inferred_sets[key] = {tuple(p) for p in fr['inferred_px']}
            l, t, flipped = place[k]
            w = fr['width']
            ys, xs = np.nonzero(sel)
            for y, x in zip(ys, xs):
                fx = x - l
                if flipped:
                    fx = w - 1 - fx
                if (fx, y - t) in inferred_sets[key]:
                    inf += 1
        prov['inferred'] += inf
        bucket = ('cross_shot_validated_1994' if fr['grade'] == 'cross-shot-validated'
                  else 'single_shot_1994')
        prov[bucket] += n - inf
    out = dict(frame_px=int(total),
               all_frame_strict=pct(strict.sum()),
               all_frame_class=pct(match.sum()),
               void_as_black_points=pct((~drawn & (Sc == BLACK)).sum()),
               excluded_actor_points=round(float(excl), 3),
               provenance_points={k: pct(v) for k, v in prov.items()})
    out['provenance_points']['unmatched'] = round(100.0 - out['all_frame_class'], 3)
    return out


def built_paths(vig):
    """The built render/diff beside the retail pair: <shot>_render_built.png."""
    return {k: vig['verify'][k].replace('.png', '_built.png')
            for k in ('render', 'diff')}


def publish(vig, img, sidx, built=False):
    """Write the render (P-mode, U8PAL, unpainted = index 0 black) and the
    diff (shot | render | mismatches in red, unpainted dimmed blue) at x3."""
    paths = built_paths(vig) if built else vig['verify']
    pal = PAL.astype(np.uint8).flatten().tolist()
    render = Image.fromarray(np.where(img >= 0, img, 0).astype(np.uint8), 'P')
    render.putpalette(pal)
    render.save(os.path.join(REPO, paths['render']))
    shot = PAL[sidx].astype(np.uint8)
    drawn = img >= 0
    match = drawn & (CLS[np.where(drawn, img, 0)] == CLS[sidx])
    diff = (shot * 0.35).astype(np.uint8)
    diff[match] = shot[match]
    diff[drawn & ~match] = (255, 0, 0)
    diff[~drawn] = (diff[~drawn] // 2 + np.array([0, 0, 110], np.uint8))
    panel = np.concatenate([shot, to_rgb(img), diff], 1)
    im = Image.fromarray(panel).resize((panel.shape[1] * 3, panel.shape[0] * 3), Image.NEAREST)
    im.save(os.path.join(REPO, paths['diff']))


def run(shot, registry, painter, args):
    vig = load_vignette(shot)
    built = args.built
    img, own, items, place = replay(vig, painter, built)
    sidx = shot_index(shot)
    sc = score(vig, registry, img, own, items, place, sidx, built)
    pub = published_rgb(vig, built)
    same = pub is not None and pub.shape == img.shape + (3,) and bool((pub == to_rgb(img)).all())
    ndiff = None if pub is None or pub.shape != img.shape + (3,) else int((pub != to_rgb(img)).any(-1).sum())
    if args.publish and not same:
        publish(vig, img, sidx, built)
        same, ndiff = True, 0
    if args.write_verify:
        if built:
            v = vig['verify'].setdefault('built', {})
            v.update(built_paths(vig))
        else:
            v = vig['verify']
        v.update(sc)
        v['published_render_identical'] = same
        v['replay'] = (f'python3 agents/map-populator/src/vignette_replay.py '
                       f'{shot}{" --built" if built else ""}')
        save_vignette(vig)
    return sc, same, ndiff


def _components(mask):
    """Sizes of the 8-connected components of a small boolean mask, largest first."""
    H, W = mask.shape
    seen = np.zeros_like(mask)
    sizes = []
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]:
            continue
        seen[y, x] = True
        stack, n = [(y, x)], 0
        while stack:
            cy, cx = stack.pop()
            n += 1
            for ny in range(max(cy - 1, 0), min(cy + 2, H)):
                for nx in range(max(cx - 1, 0), min(cx + 2, W)):
                    if mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        sizes.append(n)
    return sorted(sizes, reverse=True)


def _match_counts(art, shot_cls):
    """For every top-left (x, y) with any overlap: class-equal opaque pixels
    and visible opaque pixels, by FFT correlation per palette class.
    Arrays are indexed [y + h, x + w]."""
    m = art != 255
    h, w = art.shape
    H, W = shot_cls.shape
    pad = np.full((H + 2 * h, W + 2 * w), -1)
    pad[h:h + H, w:w + W] = shot_cls
    size = (pad.shape[0] + h, pad.shape[1] + w)

    def corr(img, ker):
        r = np.fft.irfft2(np.fft.rfft2(img, size) * np.fft.rfft2(ker[::-1, ::-1], size), size)
        return r[h - 1:pad.shape[0], w - 1:pad.shape[1]]
    ac = np.where(m, CLS[np.where(m, art, 0)], -9)
    match = sum(corr((pad == c).astype(float), (ac == c).astype(float)) for c in np.unique(ac[m]))
    vis = corr((pad >= 0).astype(float), m.astype(float))
    return np.rint(match).astype(int), np.rint(vis).astype(int)


def cross_shot(fr, shot_cls):
    """Best class match of a registry frame in each other shot (shot_cls:
    shot name -> palette-class image), plain and mirrored, fully in bounds
    and >= 50% visible; the auto grade."""
    art = read_png(fr['png'])
    tot = int((art != 255).sum())
    h, w = art.shape
    best = {}
    for shot, sc in shot_cls.items():
        if shot == fr['source']['shot']:
            continue
        for flip in (False, True):
            a = art[:, ::-1] if flip else art
            mt, vis = _match_counts(a, sc)
            for mode, ok in (('inbounds', vis >= tot), ('edge', vis >= 0.5 * tot)):
                frac = np.where(ok, mt / np.maximum(vis, 1), -1.0)
                Y, X = np.unravel_index(np.argmax(frac), frac.shape)
                if frac[Y, X] < 0:
                    continue
                r = dict(shot=shot, xy=[int(X - w), int(Y - h)], flipped=flip,
                         match=int(mt[Y, X]), visible=int(vis[Y, X]))
                b = best.get(mode)
                if b is None or r['match'] / r['visible'] > b['match'] / b['visible']:
                    best[mode] = r
    passed = False
    for r in best.values():
        a = art[:, ::-1] if r['flipped'] else art
        x, y = r['xy']
        sc = shot_cls[r['shot']]
        H, W = sc.shape
        sub = np.full(a.shape, -1)
        y0, y1, x0, x1 = max(y, 0), min(y + h, H), max(x, 0), min(x + w, W)
        sub[y0 - y:y1 - y, x0 - x:x1 - x] = sc[y0:y1, x0:x1]
        m = a != 255
        bad = m & (sub >= 0) & (CLS[np.where(m, a, 0)] != sub)
        r['mismatch_components'] = _components(bad)[:8]
        f, comps = r['match'] / r['visible'], r['mismatch_components']
        if r['visible'] >= max(64, 0.5 * tot) and (
                f >= 0.97 or (f >= 0.85 and len(comps) <= 3 and min(comps) >= 10)):
            passed = True
    return best, 'cross-shot-validated' if passed else 'single-shot'


def validate_art(registry):
    """Re-run the cross-shot search for every registry frame and report it
    beside the registry's grade.  reference-crop/residual kinds keep their
    grades; other differences are the curated overrides each frame's note
    explains (mirror frames, the composite altar shield, retail fragments)."""
    shot_cls = {shot: CLS[shot_index(shot)] for shot in all_shots()}
    for sid, ent in registry['shapes'].items():
        for fi, fr in enumerate(ent['frames']):
            best, auto = cross_shot(fr, shot_cls)
            if ent['kind'] == 'reference-crop':
                auto = 'reference-only'
            elif ent['kind'] == 'residual':
                auto = 'residual'
            b = best.get('inbounds') or best.get('edge')
            where = (f"{b['shot']} {tuple(b['xy'])}{' mirrored' if b['flipped'] else ''} "
                     f"{b['match']}/{b['visible']} blobs {b['mismatch_components']}") if b else '-'
            flag = '' if auto == fr['grade'] else f"   (registry: {fr['grade']}, see note)"
            print(f"{sid}:{fi} {os.path.basename(fr['png']):36s} {auto:20s} {where}{flag}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('shots', nargs='*')
    ap.add_argument('--built', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--publish', action='store_true')
    ap.add_argument('--write-verify', action='store_true')
    ap.add_argument('--validate-art', action='store_true',
                    help='re-run the cross-shot search for every 1994 asset (minutes)')
    args = ap.parse_args(argv)
    registry = load_registry()
    if args.validate_art:
        validate_art(registry)
        return 0
    painter = make_painter(registry, built=args.built)
    shots = args.shots or all_shots()
    print(f"{'shot':9s} {'strict':>7s} {'class':>7s} {'+void':>6s} {'+actor':>6s} "
          f"{'retail':>6s} {'xval':>6s} {'single':>6s} {'infer':>6s} {'unmat':>6s}  published")
    bad = 0
    for shot in shots:
        sc, same, ndiff = run(shot, registry, painter, args)
        p = sc['provenance_points']
        state = 'identical' if same else ('missing' if ndiff is None else f'{ndiff} px differ')
        bad += not same
        print(f"{shot:9s} {sc['all_frame_strict']:7.3f} {sc['all_frame_class']:7.3f} "
              f"{sc['void_as_black_points']:6.2f} {sc['excluded_actor_points']:6.2f} "
              f"{p['retail']:6.2f} {p['cross_shot_validated_1994']:6.2f} "
              f"{p['single_shot_1994']:6.2f} {p['inferred']:6.2f} {p['unmatched']:6.2f}  {state}")
    if args.check and bad:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
