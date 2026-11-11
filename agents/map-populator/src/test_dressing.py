#!/usr/bin/env python3
"""Built-map dressing ratchets; --strict enforces the phase 4 exit targets.

--record accepts improvements only. Each map owns one JSON pin file.
Allowances have a metric, region, bound, and reason; strict runs apply them
explicitly while reporting every outstanding target failure.
"""
import argparse
from collections import Counter
import contextlib
import hashlib
import io
import json
import subprocess
from pathlib import Path
import tempfile

import dressing_metrics as dm
import lv_dressing as dress
import lv_globs
from u8_flex import FlexArchive
from u8_map import MapItem

PIN_DIR = Path(__file__).resolve().parent / 'dressing_pins'
EPS = 1e-12


def limits(metrics):
    return {path: (direction, dm.pick(metrics, path)) for path, direction in dm.RATCHET
            if dm.pick(metrics, path) is not None}


def regression(values, pins):
    return [f'{p}={dm.pick(values,p)} violates {kind} pin {bound}'
            for p, (kind, bound) in pins.items()
            if dm.pick(values,p) is None or
            (dm.pick(values,p) < bound - EPS if kind == 'min' else dm.pick(values,p) > bound + EPS)]


def structural(src, mapnum):
    """Inspect shipped dressing, using provenance emitted by Site.pack()."""
    raw = src.raw(mapnum)
    doc = lv_globs.registry()
    provenance = doc.get('dressing', {}).get(str(mapnum), {})
    keys = set(provenance.get('records', ()) + provenance.get('eggs', ()))
    dressed = [i for i in raw if i.to_bytes().hex() in keys or (i.is_glob_egg and i.quality >= lv_globs.FIRST)]
    if not dressed:
        return []
    from parse_typeflag import load_typeflag
    shapes = load_typeflag(str(lv_globs.ROOT/'shared/build/TYPEFLAG.DAT'))
    original = [i for i in raw if i not in dressed]
    # Leg bands must come from the complete map; removal of packed floors
    # would remove the surface on which the path is measured.
    bands = dress.leg_cells(mapnum, raw, shapes)
    band_cells = {(x//32,y//32) for band in bands.values() for x,y,z in band}
    windows = dress.shot_windows(mapnum)
    bad = []
    eggs = {(i.x//512,i.y//512): i.quality for i in raw if i.is_glob_egg}
    for i in dressed:
        if i.is_glob_egg and i.quality != 262:
            x,y = i.x//512,i.y//512
            for dx,dy in ((1,0),(0,1)):
                if all(eggs.get((x+k*dx,y+k*dy)) == i.quality for k in range(3)):
                    bad.append(f'prefab {i.quality} repeats three times at {x},{y}')
        expanded = src.globs.glob_to_items(i.quality,i.x,i.y,i.z) if i.is_glob_egg else [i]
        for p in expanded:
            inf = src.info(p.shape)
            # Packed ground is allowed in a leg band; props are measured by
            # their full footprint, including one-dimensional brush pieces.
            cls = dm.item_class(inf,p.shape,p.frame)
            if cls not in ('ground','void') and max(inf['xd'],inf['yd']) >= 64:
                if dress.cells32(dress.box(p,src.sorter)) & band_cells:
                    bad.append(f'prop {p.shape} inside leg band at {p.x},{p.y}')
            if dress.paints_window(p,src.sorter,windows):
                bad.append(f'dressing {p.shape} paints a shot window at {p.x},{p.y}')
    return sorted(set(bad))


def contract_checks():
    from unittest.mock import patch
    from parse_typeflag import load_typeflag
    from glob_catalog import GlobReader
    import sys
    sys.path.insert(0,str(lv_globs.ROOT/'agents/usecode-compiler/src'))
    from lv_manifest import Manifest

    # Compiler-first imports must still select the sibling archive writer.
    probe = subprocess.run([
        sys.executable, '-c',
        "import sys; sys.path.insert(0, sys.argv[1]); import u8_flex; "
        "assert not hasattr(u8_flex.FlexArchive, 'write'); "
        "sys.path.insert(0, sys.argv[2]); import lv_globs; "
        "assert hasattr(lv_globs.FlexArchive, 'write')",
        str(lv_globs.ROOT/'agents/usecode-compiler/src'),
        str(lv_globs.ROOT/'agents/map-populator/src')],
        capture_output=True, text=True)
    assert probe.returncode == 0, probe.stderr

    retail = FlexArchive(lv_globs.RETAIL)
    shipped = FlexArchive(lv_globs.OUTPUT)
    assert all(retail[i] == shipped[i] for i in range(3072)), 'retail glob slots changed'
    globs = lv_globs.registry()['globs']
    assert shipped.count == 3072 + len(globs), 'built glob count disagrees with pins'
    # The engine refuses a FLEX with more entries than its readMetadata cap
    # (flex_file.cpp). Lost Vale appends every map's prefab rows to one
    # GLOB.FLX, so the built file must fit, and the cap must still cover a
    # glob egg's whole 16-bit quality range. A stock 4095 cap once failed
    # the build as Map 17 merged (2026-11-10).
    import re
    flex_src = (lv_globs.ROOT/'scummvm-lv-console/engines/ultima/ultima8/'
                'filesys/flex_file.cpp')
    if flex_src.exists():
        cap = int(re.search(r'if \(count > (\d+)\)', flex_src.read_text()).group(1))
        assert cap >= 65536, f'engine FLEX cap {cap} cannot hold glob quality 65535'
        assert shipped.count <= cap, f'GLOB.FLX has {shipped.count} entries; engine cap {cap}'
    for name,pin in globs.items():
        payload = shipped[pin['id']]
        want = pin.get('sha256',name.removeprefix('packed_'))
        assert payload and hashlib.sha256(payload).hexdigest() == want, name
    # Writer preserves empty slots, object bytes, and title header bytes.
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)/'test.flx'
        FlexArchive.write(path,[None,b'ab',b'cd',None])
        a = FlexArchive(path)
        assert a.count == 4 and [a[i] for i in range(4)] == [None,b'ab',b'cd',None]
        for bad in [[(0,1,0,4,0)],[(513,1,0,4,0)]]:
            try: lv_globs.encode(bad)
            except ValueError: pass
            else: raise AssertionError('unrepresentable glob coordinate accepted')
        # Both compiler and prefab writers must preserve each other's pins.
        manifest = Path(directory)/'manifest.json'
        manifest.write_text(lv_globs.MANIFEST.read_text())
        before = json.loads(manifest.read_text())
        m = Manifest.load(str(manifest)); m.save(str(manifest))
        after = json.loads(manifest.read_text())
        assert before.get('globs') == after.get('globs')
        assert before.get('dressing') == after.get('dressing')
        first = lv_globs.register_packed([(127,127,0,4,30)],manifest)
        again = lv_globs.register_packed([(127,127,0,4,30)],manifest)
        assert first == again and first >= 3132
        staged = Path(directory)/'GLOB.FLX'
        with contextlib.redirect_stdout(io.StringIO()):
            lv_globs.build(output=staged,manifest=manifest)
        retail, built = FlexArchive(lv_globs.RETAIL), FlexArchive(staged)
        assert all(retail[i] == built[i] for i in range(3072))
        extra = ('earth_extra_0',4,(30,),())
        with patch.object(lv_globs,'PREFABS',lv_globs.PREFABS+(extra,)), contextlib.redirect_stdout(io.StringIO()):
            lv_globs.build(output=staged,manifest=manifest)
        appended = json.loads(manifest.read_text())['globs']
        assert appended['earth_extra_0']['id'] > first
        assert appended['packed_'+hashlib.sha256(lv_globs.encode([(127,127,0,4,30)])).hexdigest()]['id'] == first
        sorter = dm.Source().sorter
        for row in lv_globs.PREFABS:
            for x,y,z,shape,frame in lv_globs.authored(row):
                assert sorter.frame(shape,frame) is not None, (row[0],shape,frame)

    shapes = load_typeflag(str(lv_globs.ROOT/'shared/build/TYPEFLAG.DAT'))
    floors = [MapItem.glob_egg(x*512+255,y*512+255,glob_index=397)
              for x in range(2,10) for y in range(2,10)]
    # An asymmetric trigger protects its high-nibble x range.
    with patch.object(dress,'leg_cells',return_value={}), patch.object(dress,'shot_windows',return_value=[]):
        trigger = MapItem(x=5000,y=5000,shape=73,npcnum=0x82)
        egg_site = dress.Site(9,[trigger],shapes,42)
        assert egg_site.reason(MapItem.placed_item(5240,5000,0,465,0)) == 'egg hatch or teleport'
        assert (5000//32,5240//32) not in egg_site.mask
        # The occupied-chunk API must honor the decoded hatch box too.
        floor = MapItem.glob_egg(4863,4863,glob_index=397)
        hatch = MapItem(x=4863,y=4863,shape=73,npcnum=0xff)
        hatch_site = dress.Site(9,[floor,hatch],shapes,42)
        assert not hatch_site.place_prefab(877,x=4863,y=4863)
        assert 'egg hatch or teleport' in hatch_site.ledger[-1]['rejected']
    # Synthetic geometry isolates exclusions from existing map content.
    with patch.object(dress,'leg_cells',return_value={}), patch.object(dress,'shot_windows',return_value=[]), \
         patch.object(dress.Site,'_exclusions'):
        for mapnum in (10,13):
            shore_site = dress.Site(mapnum,floors,shapes,42)
            assert 'riverbank' in shore_site.reason(MapItem.placed_item(3007,3007,0,301,6),ground=True)
            assert shore_site.reason(MapItem.placed_item(3007,3007,0,301,5),ground=True) is None
            for operation in (
                lambda: shore_site.swap_chunks(plain=397,family=dress.SHORE_SE,share=.4,where=(1024,1024,5119,5119)),
                lambda: shore_site.beyond('shore',where=(512,1024,1023,1535)),
            ):
                try: operation()
                except ValueError as exc: assert 'river-shore' in str(exc)
                else: raise AssertionError('excluded retail riverbank accepted')
        site = dress.Site(9,floors,shapes,42)
        before = [i.to_bytes() for i in floors]
        changed = site.swap_chunks(plain=397,family=(956,957,396,398),share=.5,where=(1024,1024,5119,5119))
        assert changed and len(site.items) == len(floors)
        assert before == [i.to_bytes() for i in floors], 'caller list mutated'
        counts = Counter(i.quality for i in changed)
        assert len(counts) >= 4 and max(counts.values())/len(changed) <= .25
        site.reserve('riverbed',(2000,2000,2400,2400))
        p = MapItem.placed_item(2208,2208,0,465,0)
        assert 'riverbed' in site.reason(p)
        assert site.reason(p,allow_reservation='riverbed') is None
        try: site.set_piece('bench',[p])
        except ValueError as exc: assert 'bench' in str(exc) and 'riverbed' in str(exc)
        else: raise AssertionError('reserved set piece accepted')
        site.leg_mask = dress.cells32((3000,3000,3300,3300))
        assert 'leg band' in site.reason(MapItem.placed_item(3200,3200,0,875,0))
        # Flat-only debris remains available beside a route.
        assert site.reason(MapItem.placed_item(3200,3200,0,6,0)) is None
        clustered = dress.Site(9,floors,shapes,42)
        clustered.reserve('dry bed',(1500,1500,1700,1700))
        pieces = clustered.clusters(kit=dress.KIT_DEADWOOD,per100=1,
                                   where=(1024,1024,5119,5119),floors={301},anchor='wall')
        assert 2 <= len(pieces) <= 5 and all(p.x%32==p.y%32==0 for p in pieces)
        assert len({p.shape for p in pieces}) >= 2
        ledger = clustered.ledger[-1]
        assert ledger['anchored']/ledger['seeds'] >= .60
        clean_site = dress.Site(9,floors,shapes,42)
        for row in lv_globs.PREFABS:
            pieces = [MapItem.placed_item(2048+x,2048+y,z,shape,frame)
                      for x,y,z,shape,frame in lv_globs.authored(row)]
            assert clean_site._accept(pieces,ground=True) is None, row[0]
        assert clean_site.reason(MapItem.placed_item(4000,4000,0,235,0)) == 'new reachable standing top'
        authored = [MapItem.placed_item(4000,2304+160*k,0,875,0) for k in range(4)]
        placed = clean_site.set_piece('column group',authored)
        assert [i.to_bytes() for i in placed] == [i.to_bytes() for i in authored]
        backdrop = clean_site.beyond('stars',where=(512,1024,1023,1535))
        assert len(backdrop)==1 and backdrop[0].quality in dress.STARS
        assert not clean_site._run_three(backdrop[0].quality,1,2)
        pair = [MapItem.placed_item(4000,4000,0,465,0), MapItem.placed_item(4000,4000,0,875,0)]
        assert clean_site._accept(pair) and clean_site._accept(pair[::-1])
        existing_prop = dress.Site(9,[pair[0]],shapes,42)
        assert existing_prop.reason(pair[1]) == 'overlapping solid'
        try: existing_prop.set_piece('column',[pair[1]])
        except ValueError: pass
        else: raise AssertionError('new solid buries an existing prop')
        assert dress.paints_window(MapItem.placed_item(1023,1023,0,465,0),site.sorter,
                                   [dict(rect=(-20,230,40,50))])
        # Pack round-trips world coordinates, dedupes, and refuses quest data.
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory)/'lv_manifest.json'
            manifest.write_text(lv_globs.MANIFEST.read_text())
            out = Path(directory)/'GLOB.FLX'
            loose = [MapItem.placed_item(1151,1151,0,4,30),MapItem.placed_item(1279,1151,0,4,31),
                     MapItem.placed_item(1407,1151,0,4,32)]
            loose[-1].quality = 12
            packed_site = dress.Site(9,loose,shapes,42)
            original = sorted(i.to_bytes() for i in loose)
            real_build = lv_globs.build
            def build_private(): return real_build(output=out,manifest=manifest)
            with patch.object(lv_globs,'MANIFEST',manifest), \
                 patch.object(lv_globs,'register_packed',side_effect=lambda items: lv_globs_register(items,manifest)), \
                 patch.object(lv_globs,'registry',side_effect=lambda path=None: json.loads(manifest.read_text())), \
                 patch.object(lv_globs,'build',side_effect=build_private), \
                 patch.object(dress,'GlobReader',side_effect=lambda: GlobReader(out) if out.exists() else GlobReader()), \
                 contextlib.redirect_stdout(io.StringIO()):
                prefix_site = dress.Site(39,loose,shapes,42)
                assert [i.to_bytes() for i in prefix_site.pack()] == [i.to_bytes() for i in loose]
                result = packed_site.pack()
            assert any(i.quality==12 and not i.is_glob_egg for i in result)
            expanded = []
            for i in result:
                expanded.extend(GlobReader(out).glob_to_items(i.quality,i.x,i.y,i.z) if i.is_glob_egg else [i])
            # glob_to_items marks no metadata; FIXED world geometry survives.
            assert sorted((i.x,i.y,i.z,i.shape,i.frame) for i in expanded) == sorted((i.x,i.y,i.z,i.shape,i.frame) for i in loose)
    shared_slice_checks(shapes)
    slice02_checks(shapes)
    assert dm.measure(dm.Source(fixed=False),9,raw=[])['records']['raw'] == 0
    row = [MapItem.placed_item(5000,5000+k*160,0,875,0) for k in range(4)]
    bent = dress.loosen_rows(row,17,42)
    assert len(bent)==4 and sum(i.shape!=875 for i in bent)==1
    assert all(abs(i.x-5000) in (32,64) for i in bent)
    assert [i.to_bytes() for i in bent] == [i.to_bytes() for i in dress.loosen_rows(row,17,42)]
    assert regression({'x':2},{'x':('min',3)})
    assert regression({'x':4},{'x':('max',3)})
    assert not regression({'x':3},{'x':('min',3)})


def shared_slice_checks(shapes):
    from unittest.mock import patch
    from lv_shapes import SHAPE_CAVE_CREST_DECORATIVE as crest
    from lv_art_props import CREST_CROPS
    # Missing stride evidence stays absent until six instances of a shape.
    assert dm.stride_share([]) is None
    five = [('small', 128*k, 0, 0, 465, 0, None) for k in range(5)]
    assert dm.stride_share(five) is None
    six = five + [('small', 640, 0, 0, 465, 0, None)]
    assert dm.stride_share(six) == 1.0
    assert 'props.stride_share' not in limits({'props': {'stride_share': None}})
    assert regression({'props': {'stride_share': 1.0}},
                      {'props.stride_share': ('max', .65)})
    with patch.object(dress, 'leg_cells', return_value={}), \
         patch.object(dress, 'shot_windows', return_value=[]), \
         patch.object(dress.Site, '_exclusions'):
        grass = [MapItem.glob_egg(x*512+255, y*512+255, glob_index=1)
                 for x in range(2, 10) for y in range(2, 10)]
        family = dress.prefab_family('grass_wood_')
        assert len(family) == 4 and min(family) > 3215
        trunk_positions = set()
        for row in lv_globs.PREFABS:
            if not row[0].startswith('grass_wood_'):
                continue
            props = row[3]
            trees = [p for p in props if p[3] in (199,75,152)]
            assert 2 <= len(trees) <= 4 and len({p[3:5] for p in trees}) >= 2
            for x,y,z,shape,frame in trees:
                assert (x,y) not in trunk_positions
                trunk_positions.add((x,y))
                assert x % 32 == y % 32 == 31 and z == 0
            assert {434,414,57,65} <= {p[3] for p in props}
            for x,y,z,shape,frame in props:
                assert z == 0
                if shape == 65:
                    assert any(abs(x-t[0])+abs(y-t[1]) <= 160
                               and x+y >= t[0]+t[1] for t in trees)
        copse = dress.Site(9, grass, shapes, 42)
        changed = copse.swap_chunks(plain=1, family=family, share=.5,
                                    where=(1024,1024,5119,5119))
        assert len(changed) == 32
        assert set(Counter(i.quality for i in changed).values()) == {8}
        blocked = dress.Site(9, grass, shapes, 42)
        blocked.leg_mask = dress.cells32((1024,1024,5119,5119))
        assert not blocked.swap_chunks(plain=1, family=family, share=.5,
                                       where=(1024,1024,5119,5119))
        # Real solids remain collisions even with safe copse internals.
        oak = MapItem.placed_item(2431,2431,0,199,0)
        blocked = dress.Site(9, grass + [oak], shapes, 42)
        assert blocked.reason(oak) == 'overlapping solid'
        # A partly occupied chunk retains its floor and unrelated prop.
        floor = MapItem.glob_egg(2303,2303,glob_index=397)
        marker = MapItem.placed_item(2079,2079,0,465,0)
        partial = dress.Site(9, [floor, marker], shapes, 42)
        before = [i.to_bytes() for i in partial.items]
        got = partial.place_prefab(877, x=2303, y=2303)
        assert got and [i.to_bytes() for i in partial.items[:2]] == before
        assert all(dm.item_class(partial.sorter.info(i.shape),i.shape,i.frame)
                   not in ('ground','void') for i in got)
        # Every prop path observes the shared mask and standing-level rule.
        partial = dress.Site(9, [floor, marker], shapes, 42)
        partial._mark((2048,2048,2559,2559),'map pin')
        assert not partial.place_prefab(877,x=2303,y=2303)
        assert partial.ledger[-1]['rejected']
        partial = dress.Site(9, [floor], shapes, 42)
        partial.leg_mask = dress.cells32((2048,2048,2559,2559))
        got = partial.place_prefab(877,x=2303,y=2303)
        assert all(not partial.sorter.info(i.shape)['solid'] for i in got)
        assert partial.reason(MapItem.placed_item(2303,2303,0,235,0)) == 'quest leg band with 64-unit margin'
        partial.leg_mask = set()
        assert partial.reason(MapItem.placed_item(2303,2303,0,235,0)) == 'new reachable standing top'
        assert partial.reason(MapItem.placed_item(2303,2303,0,900,0)) is None
        # Moat families are paint overlays on the existing grass level.
        bank_floor = [MapItem.glob_egg(cx*512+255,2303,48,glob_index=1)
                      for cx in (26,27)]
        for side in ('west','east'):
            bank = dress.Site(39,bank_floor,shapes,42)
            saved = [i.to_bytes() for i in bank.items]
            got = bank.moat_bank(side,where=(13312,2047,14335,2559))
            assert len(got) == 8, (side,len(got))
            assert [i.to_bytes() for i in bank.items[:2]] == saved
            assert all((i.shape,i.z) in ((903,40),(904,8)) for i in got)
            assert all(not (dress.box(i,bank.sorter)[0] < 14080 and i.x >= 13568) for i in got)
            dry = dress.Site(39,[],shapes,42)
            assert not dry.moat_bank(side,where=(13312,2047,14335,2559))
            bank = dress.Site(39,bank_floor,shapes,42)
            bank._mark((13312,2048,14335,2559),'egg hatch or teleport')
            assert not bank.moat_bank(side,where=(13312,2047,14335,2559))
        try: dress.Site(9,[],shapes,42).moat_bank('west',where=(0,0,65535,65535))
        except ValueError: pass
        else: raise AssertionError('moat bank accepted on another map')
        # Decorative crests remove paint at a protected shot boundary.
        cap = MapItem.placed_item(4095,4095,96,crest,0)
        clear = dress.Site(18,[],shapes,42)
        full = clear.sorter._make(cap,0,0)
        x0,y0,x1,y1 = full.sr
        clear.windows = [dict(rect=(x0-20,y0+36,x1-x0+40,100))]
        placed = clear.cave_crest('clipped crest',[cap])
        assert len(placed) == 1 and placed[0].frame != 0
        assert not dress.paints_window(placed[0],clear.sorter,clear.windows)
        assert not clear.sorter.info(crest)['land']
        assert not clear.sorter.info(crest)['solid']
        blocked = dress.Site(18,[],shapes,42)
        blocked.windows = [dict(rect=(x0-20,y0-20,x1-x0+40,y1-y0+40))]
        try: blocked.cave_crest('covered crest',[cap])
        except ValueError: pass
        else: raise AssertionError('crest paints protected shot')
        assert not blocked.added
        # A real route actor is visible before the proposed foreground cap.
        route = dress.Site(18,[],shapes,42)
        label,a,b,body,actor = dress.LEGS[18][-1]
        route.bands = {label:{(4095,4095,0)}}
        cap.z = 16
        assert route._crest_occludes(cap)
        assert 'occlusion' in route.reason(cap)
        # A walking pose can extend beyond frame zero's silhouette.
        hall = dress.Site(18,[],shapes,42)
        hall.bands = {dress.LEGS[18][0][0]: {(4095,4095,0)}}
        stride_cap = MapItem.placed_item(4047,4223,8,crest,0)
        assert hall.sorter.overdrawn([stride_cap],1,0,4095,4095,0)[0] == 0
        assert hall._crest_occludes(stride_cap)
        # Existing covered pixels remain permitted without adding debt.
        inherited = dress.Site(18,[stride_cap],shapes,42)
        inherited.bands = hall.bands
        assert not inherited._crest_occludes(stride_cap)
        contained = MapItem.placed_item(4047,4223,8,crest,0)
        contained.flags |= MapItem.FLG_CONTAINED
        packed_inventory = dress.Site(18,[contained],shapes,42)
        packed_inventory.bands = hall.bands
        assert packed_inventory._crest_occludes(stride_cap)
        # Sprites can paint after the actor without a footprint dependency.
        ambiguous = MapItem.placed_item(4095,4255,8,crest,0)
        assert hall._crest_occludes(ambiguous)
        # Missing floor and an empty prefab are distinct rejected requests.
        empty = dress.Site(9,[],shapes,42)
        assert not empty.place_prefab(877,x=2303,y=2303)
        try: empty.place_prefab(65535,x=2303,y=2303)
        except ValueError: pass
        else: raise AssertionError('empty prefab accepted')


def slice02_checks(shapes):
    from unittest.mock import patch
    from exact_reach import ExactReach, FLG_INVISIBLE, FLG_EQUIPPED
    import numpy as np
    def rejected(call, message=None):
        try: call()
        except ValueError as exc:
            if message: assert message in str(exc), str(exc)
        else: raise AssertionError('unsafe shared operation accepted')
    # Invisible collision must survive both the flag table and a real flood.
    assert FLG_INVISIBLE == 0x10 and FLG_EQUIPPED == 0x200
    floor = [MapItem.placed_item(x,y,0,301,0) for x in range(1151,1664,128) for y in range(1151,1664,128)]
    walls = [MapItem.placed_item(x,1407,0,15,0) for x in range(1151,1664,128)]
    for wall in walls: wall.flags |= FLG_INVISIBLE
    er = ExactReach(floor+walls,shapes,(1024,1024,1663,1663),step=8)
    reach,_ = er.flood([(1279,1151,0)])
    assert not reach[0][er.index_of(1279,1599)]
    er = ExactReach(floor,shapes,(1024,1024,1663,1663),step=8)
    reach,_=er.flood([(1279,1151,0)])
    assert reach[0][er.index_of(1279,1599)]
    src=dm.Source(fixed=False)
    for shape in (347,351):
        assert dm.item_class(src.info(shape),shape,0)=='void'
    water=[MapItem.placed_item(1151,1151,0,347,16)]
    assert dm.measure(src,9,raw=water)['ground'].get('cells',0)==0
    assert dm.measure(src,9,raw=water,legacy_area=True)['ground']['cells']==1
    # Cloud exemption follows the final pixel owner, preserving black debris
    # and missing pixels even when a star tile exists underneath them.
    import test_visual_quality as vq
    from types import SimpleNamespace
    scene=SimpleNamespace(black_indices=np.array([True,False]))
    out=np.array([[0,0,-1,1]])
    own=np.array([[0,1,-1,0]])
    items=[dict(shape=351),dict(shape=465)]
    assert vq.frame_black(scene,out,own,items,True).tolist()==[[False,True,True,False]]
    assert vq.frame_black(scene,out,own,items,False).tolist()==[[True,True,True,False]]
    items[0]['shape']=916
    assert vq.frame_black(scene,out,own,items,True).tolist()==[[False,True,True,False]]
    # Equal RGB pixels can have different sky owners in a camera atlas.
    # Owner disagreement must use the reference frame's black prop.
    import void_audit as va
    pixels=np.zeros((va.H,va.W),dtype=int)
    sx,sy=va.camera(0,0,0)
    fake=SimpleNamespace(black_indices=np.array([True]),items=[dict(shape=351),dict(shape=465)],
        paint=lambda spot:(pixels,None,None,np.ones_like(pixels)),
        select=lambda rect,roof:[0,1],roof=lambda spot:None,
        chunk=lambda key:((sx,sy,sx+va.W,sy+va.H),[0,1]),
        painter=SimpleNamespace(paint=lambda *args,**kwargs:(pixels,[],np.zeros_like(pixels))))
    with patch.object(vq,'_SCENE',fake),patch.object(vq,'_FRAME_CLASS','cloud'):
        assert all(row['frame_black_share']==1.0 for row in vq.frames((None,[(0,0,0),(0,0,0)])))
    with patch.object(dress,'leg_cells',return_value={}), patch.object(dress,'shot_windows',return_value=[]):
        hub=dress.Site(11,[],shapes,42)
        assert 'monster box' not in hub.mask.get((9000//32,5000//32),set())
        assert 'monster box' in hub.mask[(9700//32,14000//32)]
    with patch.object(dress,'leg_cells',return_value={}), patch.object(dress,'shot_windows',return_value=[]), patch.object(dress.Site,'_exclusions'):
        # A low dais and a border beside a quest band add only their own tops.
        for border in (False,True):
            site=dress.Site(9,floor,shapes,42)
            if border:
                site.bands={'test':{(1407,1407,0)}}
                site.leg_mask=dress.cells32((1407,1407,1407,1407),64)
            slab=MapItem.placed_item(1279,1279,0,877,0)
            saved=[i.to_bytes() for i in site.items]
            assert site.walkable_set_piece('border' if border else 'dais',[slab],seeds=[(1535,1151,0)])
            assert [i.to_bytes() for i in site.items[:len(saved)]]==saved
        site=dress.Site(9,floor,shapes,42)
        rejected(lambda:site.set_piece('generated slab',[slab]),'new reachable standing top')
        site.bands={'test':{(1279,1279,0)}}
        rejected(lambda:site.walkable_set_piece('leg slab',[slab],seeds=[(1535,1151,0)]),'quest leg cell')
        # Two 40-unit courses form an 80-unit anti-climb wall. Eight units
        # of new step would bring the top within the engine's climb72.
        wall80=walls+[MapItem.placed_item(i.x,i.y,40,15,0) for i in walls]
        site=dress.Site(9,floor+wall80,shapes,42)
        step=MapItem.placed_item(1279,1375,0,877,0)
        rejected(lambda:site.walkable_set_piece('wall step',[step],seeds=[(1279,1151,0)]),'new route')
        lintel_floor=[MapItem.placed_item(x,y,0,301,0)
                       for x in range(1151,1664,128) for y in range(1151,1920,128)]
        lintel=[MapItem.placed_item(x,1407,z,15,0)
                for x in range(1151,1664,128) for z in (40,80)]
        steps=[MapItem.placed_item(x,1471,0,877,0) for x in range(1151,1664,128)]
        site=dress.Site(9,lintel_floor+lintel,shapes,42)
        rejected(lambda:site.walkable_set_piece('lintel step',steps,seeds=[(1279,1791,0)]),'closes a retained route')
        for reason in ('map pin','egg hatch or teleport','movable clear box and reach rays'):
            site=dress.Site(9,floor,shapes,42);site._mark((1024,1024,1663,1663),reason)
            rejected(lambda:site.walkable_set_piece('masked slab',[slab],seeds=[(1535,1151,0)]),reason)
        off=MapItem.placed_item(1279,1279,1,877,0)
        rejected(lambda:dress.Site(9,floor,shapes,42).walkable_set_piece('off lattice',[off]),'lattice')
        # Crest props require a pre-existing reachable top, with no new top.
        cap=MapItem.placed_item(1279,1279,0,125,12)
        crest=dress.Site(9,floor+[cap],shapes,42)
        prop=MapItem.placed_item(1247,1247,8,465,0)
        with patch.object(dress.Site,'_arrival',return_value=[(1535,1151,0)]):
            assert crest.reason(prop) is None
            assert crest.reason(MapItem.placed_item(1247,1247,0,465,0))=='overlapping solid'
            high=MapItem.placed_item(1279,1279,96,125,12)
            blocked=dress.Site(9,floor+[high],shapes,42)
            assert blocked.reason(MapItem.placed_item(1247,1247,104,465,0))=='solid top face'
        # Retail LV maps use their quest-leg seeds, including Map 8's
        # disconnected shelf and door-chamber approaches.
        for mapnum in (8,39):
            retail=dress.Site(mapnum,floor+[cap],shapes,42)
            assert retail._arrival()
            why=retail.reason(prop)
            assert why is None or isinstance(why,str)
        # A retained rim in a chunk leaves its other cells available.
        surround=dress.Site(9,[MapItem.glob_egg(2303,2303,glob_index=397),MapItem.placed_item(1663,2175,0,125,12)],shapes,42)
        before=[i.to_bytes() for i in surround.items]
        added=surround.beyond('deep_water',where=(1536,2048,2047,2559))
        assert added and all(i.shape==347 for i in added)
        assert [i.to_bytes() for i in surround.items[:len(before)]]==before
        assert not any(i.x==1663 and i.y==2175 for i in added)
        fire=dress.Site(9,[MapItem.glob_egg(2303,2303,glob_index=397),MapItem.placed_item(1663,2175,0,125,12)],shapes,42)
        got=fire.beyond('lava',where=(1536,2048,2047,2559),partial=True,family=(802,))
        assert got and all(i.shape==409 for i in got)
        assert not any(i.x==1663 and i.y==2175 for i in got)
        fire=dress.Site(9,[MapItem.glob_egg(2303,2303,glob_index=397),MapItem.placed_item(1663,2175,0,125,12)],shapes,42)
        fire._mark((1536,2048,2047,2559),'FIRE_LINES and LAVA_MARGIN')
        assert not fire.beyond('lava',where=(1536,2048,2047,2559),partial=True,family=(802,))
        rejected(lambda:surround.beyond('deep_water',where=(0,0,4095,4095),family=(298,)),'262')
        plain=dress.Site(9,[MapItem.glob_egg(2303,2303,glob_index=397)],shapes,42)
        got=plain.beyond('deep_water',where=(512,1024,2047,2559))
        assert sum(i.is_glob_egg and i.quality==262 for i in got)>=3
        masked=dress.Site(9,[MapItem.glob_egg(2303,2303,glob_index=397)],shapes,42)
        masked._mark((512,1024,2047,2559),'map pin')
        assert not masked.beyond('deep_water',where=(512,1024,2047,2559))
        override=dress.Site(9,[MapItem.glob_egg(2303,2303,glob_index=397)],shapes,42)
        got=override.beyond('rock',where=(1024,2048,1535,2559),z=96,family=(388,))
        assert got and all(i.quality==388 and i.z==96 for i in got)
        blocked_override=dress.Site(9,[MapItem.glob_egg(2303,2303,glob_index=397)],shapes,42)
        blocked_override.leg_mask=dress.cells32((1024,2048,1535,2559))
        assert not blocked_override.beyond('rock',where=(1024,2048,1535,2559),z=96,family=(388,))
        reachable_tier=dress.Site(9,[MapItem.glob_egg(1791,2303,200,glob_index=397)],shapes,42)
        assert not reachable_tier.beyond('rock',where=(1024,2048,1535,2559),z=96,family=(388,))
        # North-of-zero rays are represented by the raised, shifted stars.
        north=dress.Site(17,[MapItem.placed_item(1151,127,0,874,0)],shapes,42)
        got=north.beyond('stars',where=(0,0,2047,511),partial=True,north=True)
        virtual=[i for i in got if 916<=i.shape<=928]
        assert virtual
        assert all(i.x>=0 and i.y>=0 for i in virtual)
        from vignette_paint import Painter
        import void_audit as va
        from lv_furnish import VIEW_RX,VIEW_RY
        canvas=Painter.built()
        for height in (0,120,252):
            north=dress.Site(17,[MapItem.placed_item(1151,127,height,874,0)],shapes,42)
            north.beyond('stars',where=(0,0,4095,4095),partial=True,north=True)
            assert any(916<=i.shape<=928 for i in north.items)
            sx,sy=va.camera(1151,127,height)
            actual=canvas.paint([vars(i) for i in north.expanded],sx,sy,va.W,va.H)[0]
            floor_only=canvas.paint([vars(i) for i in north.expanded if i.shape==874],sx,sy,va.W,va.H)[0]
            assert np.array_equal(actual[floor_only>=0],floor_only[floor_only>=0]), 'sky overwrites cloud lobes'
            virtual_tiles=[MapItem.placed_item(1151+128*dx,127+128*dy,0,351,0)
                           for dx in range(-24,25) for dy in range(-24,25)
                           if min(1151+128*dx,127+128*dy)<0]
            reference=canvas.paint([vars(i) for i in north.expanded+virtual_tiles],sx,sy,va.W,va.H)[0]
            assert not np.any((actual<0) & (reference>=0)), 'visible star rays left unpainted'
            # Existing painted rays must neither breed nor repeat.
            assert not north.beyond('stars',where=(0,0,4095,4095),partial=True,north=True)
        # CurrentMap::ChunkOnScreen filters chunks before sprite bounds.
        # Displaced stars must survive both retail viewport sizes.
        for x,y,z in ((127,127,252),(1151,127,252),(127,1151,252),(127,127,120),(127,127,0)):
            sky=dress.Site(17,[MapItem.placed_item(x,y,z,874,0)],shapes,42)
            sky.beyond('stars',where=(0,0,4095,4095),partial=True,north=True)
            for width,height in ((320,200),(640,400)):
                sl,sr=(x-y)//4-width//2-128,(x-y)//4+width//2+128
                st,sb=(x+y)//8-z-height//2-64,(x+y)//8-z+height//2+64
                def chunk_visible(it):
                    cx,cy=it.x//512,it.y//512
                    scx,scy=(cx-cy)*128,(cx+cy)*64
                    return scx+128>sl and scx-128<sr and scy-256<sb and scy+128>st
                sx,sy=x//4-y//4-width//2,x//8+y//8-z-height//2
                full=canvas.paint([vars(i) for i in sky.expanded],sx,sy,width,height)[0]
                filtered=canvas.paint([vars(i) for i in sky.expanded if chunk_visible(i)],sx,sy,width,height)[0]
                assert not np.any((full>=0)&(filtered<0)), 'star paint outside engine-visible chunks'
        retained=MapItem.placed_item(1151,127,0,874,0)
        retail_sky=dress.Site(39,[retained],shapes,42)
        assert retail_sky.beyond('stars',where=(0,0,4095,4095),partial=True,north=True)
        assert retail_sky.items[0].to_bytes()==retained.to_bytes(), 'sky moved the retail prefix'
        # Basalt keeps cold land, hot lava, and causeway bytes.
        lake=dress.Site(9,[MapItem.placed_item(1151,1151,0,301,0),MapItem.placed_item(1279,1151,0,409,0)],shapes,42)
        saved=[i.to_bytes() for i in lake.items]
        assert lake.basalt_shore('cold lip',[(8,8,2)])[0].frame==2
        rejected(lambda:lake.basalt_shore('bad shore frame',[(8,8,30)]),'missing shape frame')
        assert [i.to_bytes() for i in lake.items[:2]]==saved
        rejected(lambda:lake.basalt_shore('hot lip',[(9,8)]),'cold floor')
        rejected(lambda:dress.Site(9,floor,shapes,42).basalt_shore('dry lip',[(8,8)]),'lava neighbour')
        # Flat loose replacements preserve each tile's place among overlays.
        loose=[MapItem.placed_item(x,y,0,874,0) for x in range(1151,3072,128) for y in range(1151,3072,128)]
        site=dress.Site(17,loose,shapes,42)
        family=dress.prefab_family('cloud_gold_')[:4]
        raised=dress.Site(17,loose,shapes,42)
        snapshot=[i.to_bytes() for i in raised.items]
        assert not raised.swap_loose_chunks(floors={874},family=(555,577,585,family[0]),share=1,where=(1024,1024,3071,3071))
        assert [i.to_bytes() for i in raised.items]==snapshot, 'loose replacement changed standing heights'
        large_floor=[MapItem.placed_item(i.x,i.y,0,165,0) for i in loose]
        footprint=dress.Site(17,large_floor,shapes,42)
        assert not footprint.swap_loose_chunks(floors={165},family=family,share=1,where=(1024,1024,3071,3071))
        assert [i.to_bytes() for i in footprint.items]==[i.to_bytes() for i in large_floor]
        got=site.swap_loose_chunks(floors={874},family=family,share=1,where=(1024,1024,3071,3071))
        assert got and len(site.items)==len(loose)
        assert [(i.x,i.y,i.z) for i in site.items]==[(i.x,i.y,i.z) for i in loose]
        overlay=MapItem.placed_item(1151,1151,0,71,0)
        tied=dress.Site(17,loose+[overlay],shapes,42)
        assert tied.swap_loose_chunks(floors={874},family=family,share=1,where=(1024,1024,3071,3071))
        assert tied.items[-1].to_bytes()==overlay.to_bytes()
        assert tied.ground[8,8][0]==71
        with tempfile.TemporaryDirectory() as directory:
            manifest=Path(directory)/'manifest.json'
            manifest.write_text(lv_globs.MANIFEST.read_text())
            saved=[i.to_bytes() for i in tied.items]
            with patch.object(lv_globs,'MANIFEST',manifest), patch.object(lv_globs,'register_packed',side_effect=AssertionError('packing reorders tied floors')):
                assert [i.to_bytes() for i in tied.pack()]==saved
        blocked=dress.Site(17,loose,shapes,42)
        blocked._mark((1024,1024,3071,3071),'map pin')
        assert not blocked.swap_loose_chunks(floors={874},family=family,share=1,where=(1024,1024,3071,3071))
        window=dress.Site(17,loose,shapes,42)
        window.windows=[dict(rect=(-10000,-10000,20000,20000))]
        assert not window.swap_loose_chunks(floors={874},family=family,share=1,where=(1024,1024,3071,3071))
        # Panels can sit in a margin with no collision or additional pose cover.
        panel=MapItem.placed_item(1800,1800,0,912,0)
        site=dress.Site(9,[],shapes,42)
        site.leg_mask=dress.cells32((1600,1600,1900,1900))
        assert site.paint_only('panel',[panel])
        bad=dress.Site(9,[],shapes,42);bad._mark((1600,1600,1900,1900),'map pin')
        rejected(lambda:bad.paint_only('bad panel',[panel]),'map pin')
        rejected(lambda:site.paint_only('solid panel',[MapItem.placed_item(1800,1800,0,246,0)]),'decorative')
        wall=MapItem.placed_item(4095,4095,0,15,0)
        skin=MapItem.placed_item(4095,4095,0,915,0)
        wall_floor=[MapItem.placed_item(x,y,0,301,0) for x in range(3839,4352,128) for y in range(3839,4480,128)]
        site=dress.Site(13,wall_floor+[wall],shapes,42)
        site._mark((3967,3967,4095,4095),'VALLEY_CLEAR')
        saved=[i.to_bytes() for i in site.items]
        with patch.object(dress.Site,'_arrival',return_value=[(4095,4351,0)]):
            assert site.paint_only('rock skin',[skin],replaces=[wall])
            assert [i.to_bytes() for i in site.items[:len(saved)]]==saved
            short=MapItem.placed_item(4351,4351,64,902,1)
            rejected(lambda:dress.Site(13,wall_floor+[wall],shapes,42).paint_only('short skin',[short],replaces=[wall]))
        with patch.object(dress.Site,'_skin_occludes',return_value=True):
            rejected(lambda:site.paint_only('bad visibility',[skin],replaces=[wall]),'visibility')
        # The shared pose check protects walking pixels for panels and skins.
        with patch.object(dress.Site,'_crest_occludes',return_value=True):
            rejected(lambda:dress.Site(9,[],shapes,42).paint_only('pose panel',[panel]),'quest pose')


lv_globs_register = lv_globs.register_packed


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('maps',type=int,nargs='*')
    ap.add_argument('--record',action='store_true')
    ap.add_argument('--strict',action='store_true')
    ap.add_argument('--record-stride', action='store_true',
                    help='remove only zero stride pins from unmeasurable baselines')
    args = ap.parse_args()
    contract_checks()
    if args.record_stride:
        for mapnum in args.maps or sorted(dm.REGIONS):
            path = PIN_DIR / f'map{mapnum:02d}.json'
            doc = json.loads(path.read_text())
            scopes = [(f'region {name}', row['pins'])
                      for name, row in doc['regions'].items()]
            scopes += [(name, doc[name]) for name in ('whole', 'budget') if name in doc]
            for name, pins in scopes:
                if pins.get('props.stride_share') == ['max', 0.0]:
                    del pins['props.stride_share']
                    print(f'map {mapnum} {name}: removed unmeasurable stride pin')
            path.write_text(json.dumps(doc, indent=2) + '\n')
        return 0
    src, failures, debt = dm.Source(), [], 0
    hashes = {n:hashlib.sha256((lv_globs.ROOT/'shared/build'/n).read_bytes()).hexdigest()
              for n in ('TYPEFLAG.DAT','U8SHAPES.FLX','ANIM.DAT','EUSECODE.FLX','FIXED.DAT','GLOB.FLX')}
    for mapnum in args.maps or sorted(dm.REGIONS):
        path = PIN_DIR/f'map{mapnum:02d}.json'
        old = json.loads(path.read_text()) if path.exists() else None
        if old is None and not args.record:
            failures.append(f'map {mapnum}: missing pins'); continue
        current = {'regions':{},'whole':{}}
        whole = dm.measure(src,mapnum)
        current['whole'] = limits(whole)
        regions = dm.measure_regions(src,mapnum)
        for name,kind,m,bad in regions:
            # Regional pins retain their recorded area. Land-only targets
            # above are independent of this historical regression measure.
            region_box = next(b for n,k,b in dm.REGIONS[mapnum] if n==name)
            ratchet = dm.measure(src,mapnum,box=region_box,legacy_area=True)
            current['regions'][name] = dict(kind=kind,pins=limits(ratchet))
            for p,v,direction,bound in bad:
                debt += 1
                message = f'map {mapnum} {name}: {p}={v:.6f}, target {direction} {bound}'
                allowances = (old or {}).get('allowances',[])
                allowed = any(a['region']==name and a['metric']==p and a.get('reason') and
                              (v>=a['bound'] if direction=='min' else v<=a['bound']) for a in allowances)
                print(('ALLOW ' if allowed else 'DEBT ')+message)
                if args.strict and not allowed: failures.append(message)
            if old:
                failures.extend(f'map {mapnum} {name}: {s}' for s in regression(ratchet,old['regions'][name]['pins']))
        if old:
            failures.extend(f'map {mapnum}: {s}' for s in regression(whole,old['whole']))
        from build_all_maps import RECORD_BUDGET,EXPANDED_RECORD_BUDGET
        if whole['records']['raw'] > RECORD_BUDGET[mapnum] or whole['records']['expanded'] > EXPANDED_RECORD_BUDGET.get(mapnum,float('inf')):
            failures.append(f'map {mapnum}: hard record cap exceeded')
        if args.strict and whole['records']['raw'] > dress.RAW_CEILING[mapnum]:
            failures.append(f'map {mapnum}: raw phase-exit ceiling exceeded')
        m = dm.measure(src,mapnum,box=dress.BUDGET_BOX.get(mapnum))
        for metric,value,direction,bound in dm.check(m,dress.map_targets(mapnum)):
            message = f'map {mapnum} whole: {metric}={value:.6f}, target {direction} {bound}'
            print('MAP DEBT '+message)
            if args.strict: failures.append(message)
        current['budget'] = limits(m)
        if old and 'budget' in old:
            failures.extend(f'map {mapnum} budget area: {s}' for s in regression(m,old['budget']))
        ratio = m['records']['expanded']/max(1,m['ground'].get('cells',0))
        if mapnum in dress.EXPANDED_PER_CELL and ratio > dress.EXPANDED_PER_CELL[mapnum]+EPS:
            failures.append(f'map {mapnum}: expanded per cell {ratio} exceeds limit')
        failures.extend(f'map {mapnum}: {s}' for s in structural(src,mapnum))
        if args.record:
            if failures: raise ValueError('recording would weaken pins or violate a structural contract: '+str(failures))
            PIN_DIR.mkdir(exist_ok=True)
            current.update(map=mapnum,artifact_hashes=hashes,allowances=(old or {}).get('allowances',[]),
                           target_failures=[dict(region=name,metric=p,value=v,direction=d,bound=b)
                                            for name,kind,m,bad in regions for p,v,d,b in bad],
                           expanded_per_ground_cell=ratio)
            path.write_text(json.dumps(current,indent=2)+'\n')
        print(f'map {mapnum}: {len(regions)} regions; raw {whole["records"]["raw"]}, expanded {whole["records"]["expanded"]}, per cell {ratio:.3f}')
    print(f'dressing: {len(failures)} failures; {debt} target failures')
    for f in failures: print('FAIL '+f)
    return bool(failures)


if __name__=='__main__':
    raise SystemExit(main())
