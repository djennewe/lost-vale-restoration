#!/usr/bin/env python3
"""Keep Tiny Tar visible between the Map 18 crack and the passage fork."""

import numpy as np

from avatar_visibility import Poses, reference, visibility
from void_audit import Scene


def main():
    scene = Scene(18)
    poses = Poses(scene.painter, scene.anim, shape=867)
    body = scene.painter.info(867)
    assert (body['xd'], body['yd'], body['zd']) == (32, 32, 32)

    # The original raised caps erased the actor before the fork at y 7127.
    # Test the built map with every walking and standing pose of shape 867.
    spots = [(2863, y, 0) for y in range(6783, 7168, 32)]
    spots += [(2863, 7127, 0)]
    spots += [(x, 7127, 0) for x in range(2895, 3296, 32)]
    for spot in spots:
        result = visibility(scene, poses, spot)
        assert result['min_visible'] >= .9, (spot, result)

    # Continue through the west turn, where the remaining middle caps
    # previously covered more than 85% of the shrunken actor.
    west_turn = [((2623, 7199, 0), .65), ((2671, 7199, 0), .9),
                 ((2671, 7231, 0), .5)]
    for spot, minimum in west_turn:
        result = visibility(scene, poses, spot)
        assert result['min_visible'] >= minimum, (spot, result)

    # The named Transition Hall stops retain the full-size actor above
    # their single drawn course, with the invisible upper barrier intact.
    full = Poses(scene.painter, scene.anim)
    for spot in ((3967, 4735, 0), (3455, 5823, 0), (3199, 5951, 0)):
        result = visibility(scene, full, spot)
        assert result['min_visible'] >= .75, (spot, result)

    # Check grouped masks against independent full-frame owner painting.
    fork = (2863, 7127, 0)
    result = visibility(scene, poses, fork, details=True)
    direct = reference(scene, poses, fork)
    grouped = np.array([p['visible'] for p in result['poses']])
    assert np.allclose(direct, grouped, atol=1e-12, rtol=0)
    assert np.all(direct == 1), (fork, float(direct.min()))
    print(f'OK: {len(spots) + len(west_turn)} approach and fork positions, '
          f'{len(poses.frames)} Tiny Tar poses, three full-size hall stops; '
          'all fork pixels visible')


if __name__ == '__main__':
    main()
