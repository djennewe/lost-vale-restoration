---
paths:
  - "agents/usecode-compiler/src/lv-new/*.UNK"
  - "agents/usecode-compiler/src/lv-patched/*.UNK"
---

# Camera intrinsics: both spellings compile; always re-attach.

## `scrollTo(...)` and `Camera::scrollTo(...)` are the same call

The bare spelling binds through `find_intrinsic()`'s Camera entries, and
the codegen skips the `this` push for the static Camera class:

```
setCenterOn(0);                     // calli 0xBE — detach
move_to(x, y, z, 0);                // calli 0xBF — instant
scrollTo(x, y, z, 6);               // calli 0xB5 — 25 frames
setCenterOn(1);                     // calli 0xBE — objid 1 is the Avatar
```

`AOSCENE.UNK`'s ceremony pan is the worked example, with seven checks on the
sequence in `test_uc_eggs.py` (P5) that read the simulator's `intrinsic_log`.

**Since 2026-10-07 the `Camera::` spelling compiles too** (wave 2,
`c89bf07`): `Camera::fn()` binds the Camera intrinsic as a static call,
as retail FREE 0x581 does at 1C7D/1CD9. Before that the parser discarded
every `Camera::` statement, so the `Camera::` sites in `lv-patched/FREE.UNK`
(scrollTo, changeRef, makeAvatarTiny, makeAvatarBig) were silent for months;
they now run, and anything timed around their absence needs a fresh look.
Every process intrinsic called as a statement is also waited on now
(retail rule), so `scrollTo(...)` blocks its caller for the 25 frames.

## A finished scroll leaves the camera DETACHED

`CameraProcess::run` calls `SetCameraProcess(nullptr)` when its time expires,
which parks a free camera over the destination. It does **not** resume
following the Avatar, so every scene that scrolls has to re-attach with
`setCenterOn(1)` (or call `FREE::scrollBack`, which does it for you).

This was the Sacred Circle bug (`.claude/skills/playtest/traps.md`): the
Avatar froze off the fast area and NPC strikes missed. `SHADES.UNK` scrolls
at :168 and every exit calls `scrollBack(20)` (:257, :329, :553), but
LVFREE's `scrollBack` compiled to nothing, because its `Camera::setCenterOn(1)`
was dropped. Fixed 2026-09-25 as `lv-patched/FREE.UNK` fix 2 (a bare
`setCenterOn(1)`), verified on the ceremony and on the Lord British scene
(`LORDBRIT.UNK:92`, the same routine). Records:
`docs/playtest-2026-09-25-ceremony-plaques.md`,
`docs/playtest-2026-09-26-lamps-plaques-lb.md`.

## Four engine facts that bite

- **`scrollTo`'s speed argument is discarded.** `I_scrollTo` reads it with
  `ARG_NULL16()` and always builds a 25-frame scroll — measured at 0.7-0.8 s
  in-engine. Pace a pan with `wait()` between hops, not with the speed value.
- **Time scene beats against a capture, not against `wait`'s nominal unit.**
  `FREE::wait` documents its argument as 60ths of a second and measurement
  puts it near N/71 s (wait(360) = 5.07 s, wait(300) = 4.21 s and 4.28 s over
  a 13 fps capture of AOSCENE). But that routine's `Timer::start` and
  `Timer::isDone` compile to no-ops in our build (`unknown identifier`/`no-op`
  warnings at `FREE.UNK:117-140`), so what it measures is not the documented
  thing, and an earlier reading off a noisier capture came out 2.5x adrift.
  Measure, and re-time every scene if `FREE::wait` is ever repaired.
- **`Camera::getX()`/`getY()`/`getZ()` are fork additions.** Upstream leaves
  U8 slots 0xC3-0xC5 empty (retail never calls them) and its getters assert
  `GAME_IS_CRUSADER`; unbound, they returned 0 and FREE's Tiny Tar
  `move_to(getX(), getY(), ...)` parked the camera at the map origin (a
  2 s black screen, `docs/playtest-2026-10-07-wave2-b.md`). Fork `10d59e56`
  binds them for U8 and drops the asserts. An engine built without the
  tracked patch still blanks the screen.
- **Camera z is the subject's z plus 20.** That is what `CameraProcess(itemNum)`
  adds when it centres on an item, so a point camera framing a floor item at
  z=0 wants z=20 to match.
