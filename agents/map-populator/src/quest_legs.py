"""Quest-leg endpoints and deterministic three-cell dry walking bands.

Coordinates follow phase23-design section 1.2. Bands retain reachable
cells at the path's standing level; each leg carries its actor shape.
This module has no executable-test imports.
"""
from exact_reach import ExactReach, AVATAR_BODY, TINY_BODY, SI_SEA
from map_preview import GlobReader, expand_globs


def chain(prefix, points, body=AVATAR_BODY, shape=1):
    return [(f'{prefix}-{i+1}', a, b, body, shape)
            for i, (a, b) in enumerate(zip(points, points[1:]))]


LEGS = {
    8: chain('shelf', [(29680,24400,56), (29808,24383,56),
                       (30400,26768,56), (30400,30712,56)]) +
       chain('door', [(20111,3175,8), (20415,2783,1)]),
    9: chain('tomb', [(13696,14208,0), (14336,16760,0),
                      (13759,12031,0), (14360,12792,56)]),
    10: chain('vale', [(12800,2560,0), (12800,12544,0), (5120,7168,0),
                       (18688,7680,0), (21104,8768,0), (20480,16896,0),
                       (13824,19456,8), (16447,25727,56), (12800,29300,64),
                       (7168,24064,8), (18432,23552,0), (12800,1792,0)]) +
        chain('house', [(12640,12704,0), (12580,13124,0),
                        (12895,13439,0), (14207,12543,0)]),
    11: chain('elements', [(9728,1792,0), (2047,5631,4), (17152,5120,0),
                           (5631,18943,4), (12799,18943,4),
                           (8192,20992,0), (8960,23296,0)]),
    13: chain('climb', [(4096,11776,0), (4351,1919,120), (4351,2303,120)]),
    17: chain('cloud', [(4608,9984,0), (4259,7199,0), (3559,3311,0),
                        (3328,1536,0), (2303,3103,8), (6271,5823,0),
                        (4608,11008,0)]),
    18: chain('hall', [(3072,1792,0), (3072,1408,0), (2848,6080,0)]) +
        chain('sanctum', [(2864,6504,0), (3256,8152,0), (2496,8512,0)],
              TINY_BODY, 867),
    39: chain('town', [(19116,3316,48), (18562,14406,48), (17150,19700,48)]),
}


def leg_cells(mapnum, items, shapes):
    """Return {label: set((x,y,z))}; fail if any endpoint is unreached.

    Each chain floods from its arrival component. The Map 11 final leg models the
    completed pillar puzzle by removing its quality-299 boulders.
    """
    gr = GlobReader()
    dry = [it for it in expand_globs(items, gr)
           if not shapes[it.shape].flags0 & SI_SEA]
    xs = [it.x for it in items if it.x > 64]
    ys = [it.y for it in items if it.y > 64]
    roi = (min(xs)-128, min(ys)-128, max(xs)+128, max(ys)+128)
    models, result = {}, {}
    for label, a, b, body, shape in LEGS[mapnum]:
        drop = mapnum == 11 and label == 'elements-6'
        key = (body, drop, label.startswith("door"))
        if key not in models:
            selected = [it for it in dry if not (drop and it.quality == 299)]
            models[key] = ExactReach(selected, shapes, roi, body=body, step=32,
                                     glob_reader=gr)
        er = models[key]
        seed = LEGS[mapnum][0][1]
        if mapnum == 8 and label.startswith('door'):
            seed = (20111, 3175, 8)
        if shape == 867:
            seed = (2864, 6504, 0)
        if not hasattr(er, '_leg_reach'):
            er._leg_reach, _ = er.flood([seed])
        reach = er._leg_reach
        if mapnum == 39 and label == 'town-2':
            # The unrestricted dry flood can use retail trigger corridors.
            # The specified LV leg must pass through its lane tunnel.
            tunnel = (16191, 19935, 48)
            path = er.shortest_path(reach,a,tunnel)[:-1] + er.shortest_path(reach,tunnel,b)
            if not any(16096 <= x <= 16223 and 19584 <= y <= 19968
                       for x,y,z in path):
                raise ValueError('Map 39 leg missed the lane tunnel')
        else:
            path = er.shortest_path(reach, a, b)
        band = set()
        for x, y, z in path:
            i, j = er.index_of(x, y)
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    ii, jj = i+di, j+dj
                    if (0 <= ii < er.NX and 0 <= jj < er.NY and
                            reach[z][ii, jj]):
                        band.add((int(er.x_of(ii)), int(er.y_of(jj)), int(z)))
        result[label] = band
    return result
