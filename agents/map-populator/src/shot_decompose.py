#!/usr/bin/env python3
"""
shot_decompose.py — explain a 1994 Lost Vale screenshot as U8 shape frames.

The 1994 screenshots in shared/data/lv-screenshots/ are native-resolution
(1 game pixel = 1 GIF pixel) captures re-saved as GIFs. Their palettes are
U8PAL scaled 6-bit -> 8-bit slightly differently (every colour lands within
8 RGB units of a U8PAL entry), so a screenshot pixel maps back to a palette
entry unambiguously once near-duplicate palette entries are merged into
classes. Every on-screen sprite is then a frame of some U8SHAPES shape pasted
at a pixel offset, so the screenshot can be decomposed by exact template
matching:

  1. map each screenshot pixel to a palette class;
  2. for every frame of every shape, find offsets where most of 16 anchor
     pixels agree, then score the full frame (occluded / off-screen pixels
     are allowed: a hit needs >= --full-frac of its on-screen pixels equal);
  3. greedily accept hits in order of matched-pixel count, each one only if
     it explains enough pixels no earlier hit already explained;
  4. write the accepted hits (screen position of the frame's hotspot), a
     re-render of the accepted hits, and a coverage image whose red pixels
     are what no retail frame explains: 1994-only art, effects, the mouse
     cursor, or a hit the search missed.

Turning a screen hotspot into world coordinates needs a z per item; that is a
separate, per-shot step. The projection is the engine's:
    sx = (x - y) / 4 + cx,   sy = (x + y) / 8 - z + cy.

Usage:
    python3 shot_decompose.py screen19 [--out DIR] [--jobs N] [--shapes 0-859]
"""

import argparse
import json
import os
import struct
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shape_viewer import (  # noqa: E402
    PALETTE_FILE, SHAPES_FLX, load_palette, parse_shape_frames, read_flx_entry,
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SHOTS_DIR = os.path.join(BASE_DIR, "shared", "data", "lv-screenshots")
TRANSPARENT = 255
PAD = 260            # larger than any frame we expect to straddle the edge
CLASS_TOL = 12       # palette entries within this L1 distance are one class
FIRST_LV_SHAPE = 860  # our custom art starts here; it is not 1994 evidence
ANCHORS = 24        # anchor pixels sampled per frame for the coarse search
MAX_ANCHOR_HITS = 4000  # above this many coarse hits a frame is "low detail"
NMS_PX = 3          # hits of one frame closer than this are the same placement

PAL = np.array(load_palette(PALETTE_FILE), dtype=int)


def palette_classes(tol=CLASS_TOL):
    parent = list(range(256))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(256):
        for j in range(i + 1, 256):
            if np.abs(PAL[i] - PAL[j]).sum() <= tol:
                parent[root(j)] = root(i)
    return np.array([root(i) for i in range(256)])


CLS = palette_classes()


def load_shot(name):
    """Return (padded class image, (H, W), rgb array)."""
    path = os.path.join(SHOTS_DIR, name if name.endswith(".gif") else name + ".gif")
    rgb = np.array(Image.open(path).convert("RGB")).astype(int)
    h, w, _ = rgb.shape
    nearest = np.abs(rgb[:, :, None, :] - PAL[None, None, :, :]).sum(-1).argmin(-1)
    img = np.full((h + 2 * PAD, w + 2 * PAD), -1, int)
    img[PAD:PAD + h, PAD:PAD + w] = CLS[nearest]
    return img, (h, w), rgb


_FLX = None


def shape_frames(shape):
    global _FLX
    if _FLX is None:
        with open(SHAPES_FLX, "rb") as f:
            _FLX = f.read()
    try:
        return parse_shape_frames(read_flx_entry(_FLX, shape))
    except Exception:
        return []


_FRAME_CACHE = {}


def frame_arrays(shape, fi, frame):
    key = (shape, fi)
    if key not in _FRAME_CACHE:
        a = np.array(frame["pixels"], dtype=int).reshape(frame["height"], frame["width"])
        m = a != TRANSPARENT
        ac = np.where(m, CLS[np.where(m, a, 0)], -9)
        # Black void fills whole regions of the cave shots, so black anchors
        # agree with any frame that has black in it; anchor on colour instead.
        ys, xs = np.nonzero(m & (ac != CLS[0]))
        if len(ys) < 8:  # an (almost) all-black frame: anchor on anything
            ys, xs = np.nonzero(m)
        rng = np.random.default_rng(shape * 1000 + fi)
        sel = rng.choice(len(ys), size=min(ANCHORS, len(ys)), replace=False) if len(ys) else []
        _FRAME_CACHE[key] = (a, ac, m, ys[sel], xs[sel])
    return _FRAME_CACHE[key]


def find_hits(img, hw, shape, fi, frame, anchor_frac, full_frac, min_px):
    a, ac, m, ay, ax = frame_arrays(shape, fi, frame)
    h, w = ac.shape
    H, W = hw
    if m.sum() < min_px or h > PAD or w > PAD:
        return []
    y0, y1 = PAD - h + 1, PAD + H
    x0, x1 = PAD - w + 1, PAD + W
    agree = np.zeros((y1 - y0, x1 - x0), int)
    inb = np.zeros_like(agree)
    for y, x in zip(ay, ax):
        sub = img[y0 + y:y1 + y, x0 + x:x1 + x]
        agree += sub == ac[y, x]
        inb += sub >= 0
    ok = (inb >= 8) & (agree >= anchor_frac * inb)
    if ok.sum() > MAX_ANCHOR_HITS:
        # A low-detail frame (flat colour, fine stipple) agrees almost
        # everywhere; demand near-unanimous anchors before scoring it.
        ok = (inb >= 12) & (agree >= 0.9 * inb)
    hits = []
    for yy, xx in zip(*np.nonzero(ok)):
        top, left = y0 + yy, x0 + xx
        win = img[top:top + h, left:left + w]
        vis = m & (win >= 0)
        n = int(vis.sum())
        if n < min_px:
            continue
        eq = int((win[vis] == ac[vis]).sum())
        if eq >= full_frac * n and eq >= min_px:
            hits.append(dict(
                shape=shape, frame=fi,
                left=int(left - PAD), top=int(top - PAD),
                hx=int(left - PAD + frame["xoff"]), hy=int(top - PAD + frame["yoff"]),
                matched=eq, onscreen=n, total=int(m.sum()),
            ))
    # Non-maximum suppression: a true placement beats its 1-3 px neighbours.
    hits.sort(key=lambda d: -d["matched"])
    kept = []
    for hit in hits:
        if all(abs(hit["left"] - k["left"]) > NMS_PX or abs(hit["top"] - k["top"]) > NMS_PX
               for k in kept):
            kept.append(hit)
    return kept


_IMG = None
_HW = None
_ARGS = None


def _init(name, args):
    global _IMG, _HW, _ARGS
    _IMG, _HW, _ = load_shot(name)
    _ARGS = args


def _scan_shape(shape):
    out = []
    for fi, frame in enumerate(shape_frames(shape)):
        if frame is None or frame.get("width", 0) <= 0:
            continue
        out += find_hits(_IMG, _HW, shape, fi, frame,
                         _ARGS["anchor_frac"], _ARGS["full_frac"], _ARGS["min_px"])
    return out


def explain(img, hw, hits, min_new):
    """Greedy: biggest matches first; keep a hit only if it explains new pixels."""
    H, W = hw
    explained = np.zeros((H, W), bool)
    accepted = []
    for hit in sorted(hits, key=lambda d: (-d["matched"], d["shape"], d["frame"])):
        frame = shape_frames(hit["shape"])[hit["frame"]]
        _, ac, m, _, _ = frame_arrays(hit["shape"], hit["frame"], frame)
        h, w = ac.shape
        win = img[hit["top"] + PAD:hit["top"] + PAD + h, hit["left"] + PAD:hit["left"] + PAD + w]
        good = m & (win >= 0) & (win == ac)
        ys, xs = np.nonzero(good)
        ys = ys + hit["top"]
        xs = xs + hit["left"]
        new = ~explained[ys, xs]
        if new.sum() >= max(min_new, 0.25 * hit["matched"]):
            explained[ys[new], xs[new]] = True
            accepted.append(dict(hit, new=int(new.sum())))
    return accepted, explained


def render(accepted, hw):
    """Paint accepted frames back-to-front by screen hotspot y (a proxy: the
    true engine order needs world boxes)."""
    H, W = hw
    out = np.zeros((H, W, 3), np.uint8)
    for hit in sorted(accepted, key=lambda d: (d["hy"], d["hx"])):
        frame = shape_frames(hit["shape"])[hit["frame"]]
        a, _, m, _, _ = frame_arrays(hit["shape"], hit["frame"], frame)
        h, w = a.shape
        for yy, xx in zip(*np.nonzero(m)):
            y, x = hit["top"] + yy, hit["left"] + xx
            if 0 <= y < H and 0 <= x < W:
                out[y, x] = PAL[a[yy, xx]]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("shot", help="screenshot name, e.g. screen19")
    ap.add_argument("--out", default="/tmp/lv-shots")
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    ap.add_argument("--shapes", default=f"0-{FIRST_LV_SHAPE - 1}",
                    help="inclusive range of shapes to search (default: retail only)")
    ap.add_argument("--anchor-frac", type=float, default=0.6)
    ap.add_argument("--full-frac", type=float, default=0.6)
    ap.add_argument("--min-px", type=int, default=24)
    ap.add_argument("--min-new", type=int, default=16)
    args = ap.parse_args()

    lo, hi = (int(v) for v in args.shapes.split("-"))
    name = args.shot.replace(".gif", "")
    os.makedirs(args.out, exist_ok=True)
    knobs = dict(anchor_frac=args.anchor_frac, full_frac=args.full_frac, min_px=args.min_px)

    with Pool(args.jobs, initializer=_init, initargs=(name, knobs)) as pool:
        hits = [h for part in pool.imap_unordered(_scan_shape, range(lo, hi + 1), chunksize=8)
                for h in part]

    img, hw, rgb = load_shot(name)
    accepted, explained = explain(img, hw, hits, args.min_new)
    coverage = float(explained.mean())

    rend = render(accepted, hw)
    cov = rgb.astype(np.uint8).copy()
    cov[~explained] = (cov[~explained] * 0.3 + np.array([255, 0, 0]) * 0.7).astype(np.uint8)
    side = np.concatenate([rgb.astype(np.uint8), rend, cov], 1)
    Image.fromarray(side).resize((side.shape[1] * 3, side.shape[0] * 3), Image.NEAREST) \
        .save(os.path.join(args.out, f"{name}_decomp.png"))

    with open(os.path.join(args.out, f"{name}.json"), "w") as f:
        json.dump(dict(shot=name, size=list(hw), coverage=coverage,
                       search=dict(shapes=[lo, hi], **knobs, min_new=args.min_new),
                       items=accepted, candidates=len(hits)), f, indent=1)
    print(f"{name}: {len(hits)} candidate hits, {len(accepted)} accepted, "
          f"coverage {coverage:.1%} -> {args.out}/{name}.json, {name}_decomp.png")


if __name__ == "__main__":
    main()
