#!/usr/bin/env python3
"""Check paint beneath Map 8's hidden ceilings against the built archive."""

from collections import Counter
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np

from avatar_visibility import Poses, visibility
from base_input import pristine_base
from build_map_08 import BASE_ITEM_REMOVALS, LV_SHELF_CEILINGS, LV_SHELF_FLOORS
from lv_shapes import SHAPE_CAVE_BACKDROP_SMALL, SHAPE_CAVE_BACKDROP_LARGE
from map_preview import GlobReader, expand_globs
from u8_map import MapArchive
from void_audit import Scene, camera


class Map08Backdrop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene = Scene(8)
        repo = Path(__file__).resolve().parents[3]
        retail = MapArchive(pristine_base(str(
            repo / 'shared/data/u8-install/STATIC/FIXED.DAT')))
        cls.retail = retail.get_map_items(8)
        expanded = expand_globs(cls.retail, GlobReader())
        cls.ceilings = [
            vars(item) for item in expanded
            if (item.x, item.y, item.z) in LV_SHELF_CEILINGS
            and item.shape in (334, 564)]
        cls.floors = [
            vars(item) for item in expanded
            if item.z == 56 and (item.x, item.y) in LV_SHELF_FLOORS
            and (item.shape == 334 or (item.shape, item.frame) == (564, 2))]
        cls.poses = Poses(cls.scene.painter, cls.scene.anim)

    def test_backdrops_supply_no_support_or_collision(self):
        for shape in (SHAPE_CAVE_BACKDROP_SMALL, SHAPE_CAVE_BACKDROP_LARGE):
            with self.subTest(shape=shape):
                info = self.scene.painter.info(shape)
                self.assertTrue(info['fixed'] and info['draw'])
                self.assertFalse(info['solid'] or info['land'] or info['roof']
                                 or info['occl'] or info['editor'] or info['trans'])

    def test_every_replaced_surface_has_opaque_underpaint(self):
        painter = self.scene.painter
        surfaces = self.ceilings + self.floors
        rects = np.array([painter._make(SimpleNamespace(**item), 0, 0).sr
                          for item in surfaces])
        sx, sy = int(rects[:, 0].min()), int(rects[:, 1].min())
        width = int(rects[:, 2].max()) - sx
        height = int(rects[:, 3].max()) - sy
        underlays = [vars(item) for item in self.scene.raw if item.shape in (
            SHAPE_CAVE_BACKDROP_SMALL, SHAPE_CAVE_BACKDROP_LARGE)]
        old, _, _ = painter.paint(surfaces, sx, sy, width, height, owner=True)
        new, _, _ = painter.paint(underlays, sx, sy, width, height, owner=True)
        self.assertGreater(int((old >= 0).sum()), 0)
        self.assertEqual(int(np.count_nonzero((old >= 0) & (new < 0))), 0)

    def test_ceiling_pixels_are_painted(self):
        # The engine retains previous pixels with usehighres=false.
        # A cleared offline canvas exposes exactly those missing writes.
        self.assertTrue(self.ceilings)
        for x in (29279, 29343):
            spot = (x, 26495, 56)
            with self.subTest(camera=spot):
                sx, sy = camera(*spot)
                old, _, _ = self.scene.painter.paint(
                    self.ceilings, sx, sy, 640, 400, owner=True)
                current, _, _, _ = self.scene.paint(spot, avatar=True)
                self.assertGreater(int((old >= 0).sum()), 0)
                self.assertEqual(int(np.count_nonzero(
                    (old >= 0) & (current < 0))), 0)

    def test_avatar_remains_visible(self):
        for x in (29279, 29343):
            spot = (x, 26495, 56)
            with self.subTest(camera=spot):
                result = visibility(self.scene, self.poses, spot)
                self.assertGreaterEqual(result['min_visible'], 0.97)

    def test_first_seam_floor_pixels_are_painted(self):
        spot = (29311, 24415, 56)
        sx, sy = camera(*spot)
        old, _, _ = self.scene.painter.paint(
            self.floors, sx, sy, 640, 400, owner=True)
        current, _, _, _ = self.scene.paint(spot, avatar=True)
        self.assertGreater(int((old >= 0).sum()), 0)
        self.assertEqual(int(np.count_nonzero((old >= 0) & (current < 0))), 0)

    def test_pristine_records_outside_authorised_chunks_survive(self):
        retained = Counter(i.to_bytes() for i in self.retail
                           if (i.x, i.y, i.z, i.shape) not in BASE_ITEM_REMOVALS)
        built = Counter(i.to_bytes() for i in self.scene.raw)
        self.assertFalse(retained - built)

    def test_route_witness_visibility_and_first_seam_black(self):
        # These witnesses cover both seam approaches and the retained shelf.
        for spot, minimum in (((29680, 24400, 56), 0.407),
                              ((30430, 26380, 56), 0.6007),
                              ((30430, 26200, 56), 0.8369)):
            with self.subTest(camera=spot):
                self.assertGreaterEqual(
                    visibility(self.scene, self.poses, spot)['min_visible'], minimum)
        for spot, maximum in (((29745, 23677, 0), 0.2082),
                              ((29279, 23967, 56), 0.5128)):
            with self.subTest(camera=spot):
                frame, _, _, _ = self.scene.paint(spot, avatar=True)
                black = (frame < 0) | self.scene.black_indices[np.maximum(frame, 0)]
                self.assertLessEqual(float(black.mean()), maximum)

    def test_removed_first_wall_pixels_are_repainted(self):
        wall = dict(x=29695, y=24447, z=56, shape=32, frame=1)
        for spot, hole in (((29745, 23677, 0), (130, 205)),
                           ((29279, 23967, 56), (320, 290))):
            with self.subTest(camera=spot):
                sx, sy = camera(*spot)
                old, _, _ = self.scene.painter.paint(
                    [wall], sx, sy, 640, 400, owner=True)
                current, _, _, _ = self.scene.paint(spot)
                self.assertEqual(int(np.count_nonzero(
                    (old >= 0) & (current < 0))), 0)
                x, y = hole
                self.assertGreaterEqual(int(current[y, x]), 0)
                self.assertTrue(self.scene.black_indices[current[y, x]])

    def test_first_seam_views_have_no_detached_skirt_tiles(self):
        for spot in ((29745, 23677, 0), (29279, 23967, 56)):
            sx, sy = camera(*spot)
            ids = self.scene.select((sx, sy, sx+640, sy+400))
            fragments = [self.scene.items[k] for k in ids
                         if (self.scene.items[k]['shape'],
                             self.scene.items[k]['frame']) ==
                         (SHAPE_CAVE_BACKDROP_LARGE, 0)]
            self.assertFalse(fragments, spot)

    def test_slice_record_budget(self):
        self.assertLessEqual(self.scene.record_counts['fixed_records'], 6500)
        self.assertLessEqual(
            self.scene.record_counts['items_after_glob_expansion'], 31000)


if __name__ == '__main__':
    unittest.main()
