#!/usr/bin/env python3
"""Visual-quality ratchets against built FIXED.DAT, phase23-design gate 0.

Default: eight maps, 32-unit floors and leg bands, 256-unit visibility and 512-unit frame samples.
--record writes current pins and report evidence; --strict applies the
phase-exit rules, including zero outstanding floor and leg failures.
Existing failures remain visible in pins until their map slice fixes them.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from PIL import Image, ImageDraw

import avatar_visibility as av
import void_audit as va
from build_all_maps import RECORD_BUDGET, EXPANDED_RECORD_BUDGET
from parse_typeflag import load_typeflag
from quest_legs import LEGS, leg_cells

PIN_DIR = Path(__file__).resolve().parent / 'visual_pins'
MAPS = tuple(LEGS)
EXIT_CEILING = {8: 6500, 9: 1800, 10: 23000, 11: 11700,
                13: 8000, 17: 10500, 18: 2400, 39: 6000}
CLASS = {8: 'cave', 9: 'cave', 10: 'exterior', 11: 'cave',
         13: 'exterior', 17: 'cloud', 18: 'cave', 39: 'town'}
_SCENE = None
_POSES = None
_FRAME_CLASS = None


def artifact_hashes():
    return {name: hashlib.sha256((Path(va.BUILD)/name).read_bytes()).hexdigest()
            for name in ('TYPEFLAG.DAT','U8SHAPES.FLX','ANIM.DAT','EUSECODE.FLX','FIXED.DAT','GLOB.FLX')}


def inside(spot, boxes):
    x, y, z = spot
    return any(b['box'][0] <= x <= b['box'][2] and
               b['box'][1] <= y <= b['box'][3] and
               b.get('z', [0, 255])[0] <= z <= b.get('z', [0, 255])[1]
               for b in boxes)


def frame_black(scene, out, own, items, cloud=False):
    """Only the final painted owner can exempt a star pixel."""
    black = (out < 0) | scene.black_indices[np.maximum(out,0)]
    if cloud and items:
        stars = np.array([i['shape']==351 or 916<=i['shape']<=928 for i in items],dtype=bool)
        black &= ~((own >= 0) & stars[np.maximum(own,0)])
    return black


def frames(task):
    key, spots = task
    scene = _SCENE
    def single(spot):
        out,_,_,own = scene.paint(spot)
        x,y = va.camera(*spot)
        ids = scene.select((x,y,x+va.W,y+va.H),scene.roof(spot))
        return frame_black(scene,out,own,[scene.items[k] for k in ids],_FRAME_CLASS == 'cloud')
    if len(spots) == 1:
        spot = spots[0]
        return [dict(x=spot[0],y=spot[1],z=spot[2],frame_black_share=float(single(spot).mean()))]
    (sx,sy,right,bottom),ids = scene.chunk(key)
    items = [scene.items[k] for k in ids]
    out,seq,own = scene.painter.paint(items,sx,sy,right-sx,bottom-sy,owner=True)
    cycle = any(d.order > s.order for s in seq for d in s.depends)
    for index in sorted({0,len(spots)//2,len(spots)-1}):
        x,y = va.camera(*spots[index])
        reference,_,_,reference_owner=scene.paint(spots[index])
        crop=out[y-sy:y-sy+va.H,x-sx:x-sx+va.W]
        if not np.array_equal(reference,crop):
            cycle=True
        if _FRAME_CLASS=='cloud':
            selected=scene.select((x,y,x+va.W,y+va.H),scene.roof(spots[index]))
            expected=frame_black(scene,reference,reference_owner,
                                 [scene.items[k] for k in selected],True)
            actual=frame_black(scene,crop,own[y-sy:y-sy+va.H,x-sx:x-sx+va.W],items,True)
            if not np.array_equal(expected,actual):cycle=True
    black = frame_black(scene,out,own,items,_FRAME_CLASS == 'cloud')
    rows=[]
    for spot in spots:
        x,y = va.camera(*spot)
        sub=single(spot) if cycle else black[y-sy:y-sy+va.H,x-sx:x-sx+va.W]
        rows.append(dict(x=spot[0],y=spot[1],z=spot[2],frame_black_share=float(sub.mean())))
    return rows


def visible(task):
    shape, drop, spots = task
    rows = []
    for p in spots:
        ids = None
        if drop:
            hx = av.IS._div(p[0],4)-av.IS._div(p[1],4)
            hy = av.IS._div(p[0],8)+av.IS._div(p[1],8)-p[2]
            rect = tuple(a+(hx if k%2 == 0 else hy)
                         for k,a in enumerate(_POSES[shape].bounds))
            ids = [k for k in _SCENE.select(rect,_SCENE.roof(p))
                   if _SCENE.items[k].get('quality') != 299]
        rows.append(av.visibility(_SCENE,_POSES[shape],p,ids))
    return rows


def batches(shape, drop, spots, size=128):
    points = sorted(spots)
    return [(shape, drop, points[i:i+size]) for i in range(0, len(points), size)]


def sampled(rows, step):
    return [r for r in rows if (r['x']-31) % step == 0 and (r['y']-31) % step == 0]


def metrics(floors, frame_rows, visibility, legs, pin, counts):
    inherited = {tuple(p) for p in pin['inherited_black']}
    if inherited:
        actual_inherited = {(r['x'],r['y'],r['z']) for r in floors
                            if r['reason'] == 'specified_black_floor'} & inherited
        if actual_inherited != inherited:
            raise ValueError('inherited black coordinates changed')
    specified = [r for r in floors if r['reason'] in
                 ('specified_black_floor', 'unpainted_floor') and
                 (r['x'], r['y'], r['z']) not in inherited]
    leg_low = sum(r['min_visible'] < .5 and
                  not inside((r['x'],r['y'],r['z']), pin['occlusion_allow'])
                  for r in legs)
    values = [r['frame_black_share'] for r in frame_rows
              if not inside((r['x'],r['y'],r['z']), pin['frame_allow'])]
    if not values or not visibility:
        raise ValueError('empty visual sample')
    dist = va.distribution(values)
    return dict(walkable_black_specified=len(specified),
                walkable_black_prop=sum(r['reason'] == 'black_floor_pixel' for r in floors),
                leg_cells_below_half=int(leg_low),
                cells_below_half_share=sum(r['min_visible'] < .5 for r in visibility)/len(visibility),
                cells_hidden_share=sum(r['min_visible'] == 0 for r in visibility)/len(visibility),
                median_min_visible=float(np.median([r['min_visible'] for r in visibility])),
                frame_black_mean=dist['mean'], frame_black_p95=dist['p95'],
                frame_black_max=dist['max'], records=counts['fixed_records'],
                expanded_records=counts['items_after_glob_expansion'])


def limits(mapnum):
    cave = CLASS[mapnum] == 'cave'
    return dict(walkable_black_specified=0, leg_cells_below_half=0,
                cells_below_half_share=.58 if cave else .21,
                cells_hidden_share=.37 if cave else .06,
                frame_black_mean=.47 if cave else .07,
                frame_black_p95=.77 if cave else .38,
                frame_black_max=.91 if cave else .62)


def plot(mapnum, rows, bands, path, leg_rows=()):
    """Visibility at report spacing, with the full 32-unit leg bands."""
    points = [(r['x'], r['y']) for r in rows] + [(x,y) for b in bands.values() for x,y,z in b]
    x0, y0 = map(min, zip(*points)); x1, y1 = map(max, zip(*points))
    scale = min(1000/max(1,x1-x0), 1000/max(1,y1-y0))
    img = Image.new('RGB', (max(640,int((x1-x0)*scale)+10),int((y1-y0)*scale)+80), (24,24,30))
    draw = ImageDraw.Draw(img)
    def xy(x,y): return int((x-x0)*scale)+4, int((y-y0)*scale)+70
    for layer, spacing in ((rows,128),(leg_rows,32)):
        for r in sorted(layer, key=lambda r: -r['min_visible']):
            x,y=xy(r['x'],r['y']); v=1-r['min_visible']
            radius=max(1,int(spacing*scale/2))
            draw.rectangle((x-radius,y-radius,x+radius,y+radius),
                           fill=(int(255*v),int(210*(1-v)),45))
    for b in bands.values():
        for x,y,z in sorted(b):
            px,py=xy(x,y); draw.point((px,py),fill=(60,180,255))
    draw.text((8,8),f'Map {mapnum}: worst-pose visibility; blue = 32-unit quest bands',fill='white')
    draw.text((8,26),'Green = visible; red = hidden; x east, y south; worst level per cell',fill='white')
    draw.text((8,44),'; '.join(bands),fill='white')
    img.save(path)


def measure(mapnum, pin, workers, record=False, out=None):
    start = time.monotonic()
    global _SCENE, _POSES, _FRAME_CLASS
    _FRAME_CLASS = CLASS[mapnum]
    scene = _SCENE = va.Scene(mapnum)
    va._SCENE = scene
    _POSES = {shape: av.Poses(scene.painter, scene.anim, shape)
              for shape in {leg[4] for leg in LEGS[mapnum]}}
    arrival = (29680,24400,56) if mapnum == 8 else None
    cells, _ = va.reachable(mapnum, scene.raw, arrival, scene.typeflag)
    bands = leg_cells(mapnum, scene.raw, load_typeflag(str(scene.typeflag)))
    sample_step = 128 if record else pin['sample_step']
    frame_step = 128 if record else pin.get('frame_step', pin['sample_step'])
    frame_rows = [r for batch in va.parallel(frames, va.groups(scene,cells,frame_step),workers) for r in batch]
    floor_rows = [r for batch in va.parallel(va.walkable_chunk,va.groups(scene,cells,32),workers) for r in batch]
    if record and mapnum == 8 and not pin['inherited_black']:
        pin['inherited_black'] = sorted([[r['x'],r['y'],r['z']] for r in floor_rows
                                        if r['reason'] == 'specified_black_floor'])
        if len(pin['inherited_black']) != 256:
            raise ValueError('Map 8 inherited black differs from 256 cells')
    map_spots = {p for _, spots in va.groups(scene,cells,sample_step) for p in spots}
    by_shape = {(1,False): set(map_spots)}
    for label, a, b, body, shape in LEGS[mapnum]:
        drop = mapnum == 11 and label == 'elements-6'
        by_shape.setdefault((shape,drop),set()).update(bands[label])
    vis = {}
    for (shape,drop), spots in by_shape.items():
        vis[shape,drop] = {(r['x'],r['y'],r['z']):r for batch in
                      va.parallel(visible,batches(shape,drop,spots),workers) for r in batch}
    map_rows = [vis[1,False][p] for p in sorted(map_spots)]
    leg_keys = {(shape,mapnum == 11 and label == 'elements-6',p)
                for label,a,b,body,shape in LEGS[mapnum] for p in bands[label]}
    leg_rows = [vis[shape,drop][p] for shape,drop,p in sorted(leg_keys)]
    current = metrics(floor_rows,sampled(frame_rows,pin.get('frame_step',pin['sample_step'])),
                      sampled(map_rows,pin['sample_step']),leg_rows,pin,scene.record_counts)
    evidence = dict(map=mapnum, artifact_hashes=artifact_hashes(),
                    sample_step=pin['sample_step'],
                    frame_step=pin.get('frame_step',pin['sample_step']), measured=current,
                    reachable_cells=len(cells), leg_cells=len(leg_keys),
                    leg_band_counts={k:len(v) for k,v in bands.items()})
    if record:
        evidence['step128'] = metrics(floor_rows,frame_rows,map_rows,leg_rows,pin,scene.record_counts)
        # Unfiltered distributions reproduce the design section 0 table.
        full_pin = dict(pin, frame_allow=[])
        evidence['step128_unfiltered'] = metrics(floor_rows,frame_rows,map_rows,leg_rows,full_pin,scene.record_counts)
        plot(mapnum,map_rows,bands,out/f'map{mapnum:02d}-legs.png',leg_rows)
    evidence['runtime_seconds'] = round(time.monotonic()-start,3)
    return evidence


def contract_checks():
    """Negative controls for the shared APIs and blocking record errors."""
    from contextlib import redirect_stdout
    from io import StringIO
    from types import SimpleNamespace
    from unittest.mock import patch
    import build_all_maps as build
    from exact_reach import ExactReach, TINY_BODY
    from lv_cave_vignette import Cave, COURSE, INVISIBLE
    from lv_furnish import floor_cells

    er = ExactReach.__new__(ExactReach)
    er.X0 = er.Y0 = 31
    er.NX = er.NY = 3
    er.step, er.step_z = 32, 8
    er.reached_near = lambda reach, x, y, z, ring: (x, y, z)
    er.levels = [0, 1, 8]
    reach = {z: np.ones((3,3),dtype=bool) for z in er.levels}
    assert er.shortest_path(reach,(31,31,0),(95,95,0)) == [
        (31,31,0),(31,63,0),(31,95,0),(63,95,0),(95,95,0)]
    # A one-unit riser is outside the engine offset table.
    er.levels = [0, 1]
    disconnected = {z: np.ones((3,3),dtype=bool) for z in er.levels}
    try:
        er.shortest_path(disconnected,(31,31,0),(95,95,1))
    except ValueError:
        pass
    else:
        raise AssertionError('illegal riser accepted')
    er.levels = [0]
    disconnected = {0: np.ones((3,3),dtype=bool)}
    disconnected[0][1,:] = False
    try:
        er.shortest_path(disconnected,(31,31,0),(95,95,0))
    except ValueError:
        pass
    else:
        raise AssertionError('disconnected route accepted')

    shot = SimpleNamespace(classify=lambda: {}, paints_window=lambda _: False)
    default = Cave(shot,(0,0),['..'])
    explicit = Cave(shot,(0,0),['..'],near_courses=2)
    for side in ('S','E','N','W'):
        assert [vars(i) for i in default._face(side,2,0,256)] == [
            vars(i) for i in explicit._face(side,2,0,256)]
        for n in (0,1):
            face = Cave(shot,(0,0),['..'],near_courses=n)._face(side,2,0,256)
            assert {i.z for i in face} == {0,COURSE}
            assert all(i.shape in INVISIBLE for i in face if i.z >= n*COURSE)
    # Short jagged pieces must retain a blocker above their drawn course.
    real_shapes = load_typeflag(str(Path(va.BUILD)/'TYPEFLAG.DAT'))
    for side in ('S','E'):
        for n in (0,1,2):
            face = Cave(shot,(0,0),['..'],jag=True,near_courses=n)._face(side,2,0,1024)
            er_face = ExactReach(face,real_shapes,(-64,-64,1100,1100),
                                 body=TINY_BODY,step=32)
            x,y = (255,415) if side == 'S' else (415,255)
            i,j = er_face.index_of(x,y)
            assert er_face.blocked(48)[i,j], 'jagged upper course exposes a foothold'
            assert not er_face.mask(48)[i,j]
    clipped_shot = SimpleNamespace(classify=lambda: {},
                                   paints_window=lambda it: it.z == COURSE)
    clipped = Cave(clipped_shot,(0,0),['..'],jag=True)._face('S',2,0,1024)
    for n in (0,1):
        assert [vars(i) for i in clipped] == [vars(i) for i in
            Cave(clipped_shot,(0,0),['..'],jag=True,near_courses=n)._face('S',2,0,1024)]
    for n in (-1,3,1.5,True):
        try: Cave(shot,(0,0),['..'],near_courses=n)
        except ValueError: pass
        else: raise AssertionError('invalid near_courses accepted')

    shape = SimpleNamespace(flags0=0,footpad_z=0,footpad_x=8,footpad_y=8)
    shapes = [shape]*896
    for number in (894,895):
        item = SimpleNamespace(shape=number,x=255,y=255)
        assert not floor_cells([item],shapes)
        assert len(floor_cells([item],shapes,painted=True)) == 4
    with patch.object(build,'validate_items',return_value=[]), redirect_stdout(StringIO()):
        _, errors = build.validate_and_gate({9:[None]*2501})
        assert errors, 'raw record overflow failed to block'
        with patch('map_preview.expand_globs',return_value=[None]*31001):
            _, errors = build.validate_and_gate({8:[]})
            assert errors, 'expanded record overflow failed to block'

    # A normal CLI run must replace an old report with current evidence.
    import sys
    import tempfile
    module = sys.modules[__name__]
    pin18 = json.loads((PIN_DIR/'map18.json').read_text())
    with tempfile.TemporaryDirectory() as directory:
        dest = Path(directory)/'map18-metrics.json'
        dest.write_text(json.dumps({'step128': {'frame_black_mean': .999}}))
        fake = dict(measured=pin18['pins'],runtime_seconds=0)
        with patch.object(module,'contract_checks'), \
             patch.object(module,'measure',return_value=fake), \
             patch.object(sys,'argv',['visual','18','--out',directory]), \
             redirect_stdout(StringIO()):
            assert main() == 0
        assert 'step128' not in json.loads(dest.read_text()), 'old report reused'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('maps',type=int,nargs='*',choices=MAPS,default=None)
    ap.add_argument('--record',action='store_true')
    ap.add_argument('--strict',action='store_true')
    ap.add_argument('--report128',action='store_true',help='measure report distributions and draw bands')
    ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--out',type=Path,default=Path('/tmp/lv-gate0-evidence'))
    args = ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    contract_checks()
    failed = []
    started = time.monotonic()
    for m in args.maps or MAPS:
        path = PIN_DIR/f'map{m:02d}.json'
        pin = json.loads(path.read_text())
        evidence = measure(m,pin,args.workers,args.report128,args.out)
        current = evidence['measured']
        if args.record:
            for key, bound in pin['pins'].items():
                value = current[key]
                if (value < bound-1e-12 if key == 'median_min_visible' else value > bound+1e-12):
                    raise ValueError(f'map {m}: recording would weaken {key} pin')
            pin['pins'] = current
            if 'step128' in evidence:
                pin['report_step128'] = evidence['step128']
                pin['report_artifact_hashes'] = evidence['artifact_hashes']
            path.write_text(json.dumps(pin,indent=2)+'\n')
        for key,value in current.items():
            bound = pin['pins'][key]
            lower = key == 'median_min_visible'
            bad = value < bound-1e-12 if lower else value > bound+1e-12
            if bad:
                failed.append(f'map {m}: {key} {value} violates pin {bound}')
            elif abs(value-bound)>1e-12:
                print(f'map {m}: lower these pins: {key} {bound} -> {value}')
        for key,bound in limits(m).items():
            if current[key] > bound+1e-12:
                msg=f'map {m}: phase-exit debt {key}={current[key]} (target {bound})'
                print(msg)
                if args.strict: failed.append(msg)
        median_limit = .25 if CLASS[m]=='cave' else 1.
        if current['median_min_visible'] < median_limit:
            msg=f'map {m}: median below class floor {median_limit}'
            print(msg)
            if args.strict: failed.append(msg)
        if current['records']>RECORD_BUDGET[m] or current['expanded_records']>EXPANDED_RECORD_BUDGET.get(m,float('inf')):
            failed.append(f'map {m}: record budget exceeded')
        if args.strict and current['records']>EXIT_CEILING[m]:
            failed.append(f'map {m}: exit ceiling exceeded')
        evidence['phase_exit_limits']=limits(m)
        evidence_path = args.out/f'map{m:02d}-metrics.json'
        evidence_path.write_text(json.dumps(evidence,indent=2)+'\n')
        print(f'map {m}: {evidence["runtime_seconds"]:.3f}s; {current}',flush=True)
    elapsed=time.monotonic()-started
    print(f'visual quality: {len(failed)} failures; {elapsed:.3f}s total',flush=True)
    for f in failed: print(f'FAIL: {f}')
    return bool(failed)


if __name__ == '__main__':
    raise SystemExit(main())
