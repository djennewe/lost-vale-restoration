# Playtest — the ceremony's camera pan (2026-09-14)

Follow-up to `docs/playtest-2026-09-13-god-placement.md`, which ended on the
one thing the freed gods still lacked: from anywhere inside the altar egg's
box all three are off-screen, so the ceremony was a white flash and a walk
back. `AOSCENE::hatch` now takes the camera off the Avatar and walks the
triangle.

## Verdicts

| ID | Test | Verdict |
|---|---|---|
| H1 | The camera leaves the Avatar under the white, cut unseen | **PASS** |
| H2 | Each of the three freed gods gets its own centred frame | **PASS** |
| H3 | The pan runs in the box-cover order, left to right | **PASS** |
| H4 | The camera re-attaches; the Avatar walks and is followed | **PASS** |
| H5 | The scene still completes: `godsFree` 0→1, frames 3/5/4 | **PASS** |
| H6 | Each god's hold is long enough to read | **PASS** (after a retime) |
| H7 | The pan does not depth-sort cleanly against the low walls | **PARTIAL** |

## H1 — the cut happens under the white — PASS

`setCenterOn(0)` then `move_to(2304, 7680, 20, 0)` sit between `FadeToWhite()`
and `FadeFromWhite()`, so the camera has already left the Avatar and arrived at
Timyra before anything is visible. `P0-under-the-white.png` is the screen
during that window.

The white runs **13.9 s** (t=18.8 s to t=32.7 s in the capture). That is
mostly the pre-existing "The ground trembles" bark, which plays under it and
is therefore invisible; the pan added the two instant camera calls and nothing
else to that window.

## H2/H3 — three gods, cover order — PASS

Three plates, each the middle of a measured still window, cursor parked in the
corner so it is not sitting on the framed god:

- `P1-timyra.png` — frame 5, (2304, 7680). Hands to the face, recoiling. Fear.
- `P2-felicitar.png` — frame 3, (3840, 7680). Arms raised. Joy.
- `P3-doloras.png` — frame 4, (3072, 6656). Bowed, head down. Sorrow.
- `P4-back-on-avatar.png` — the camera home, the closing bark up.

The order on screen is Timyra, Felicitar, Doloras, which is the cover's
left-to-right (`docs/playtest-2026-09-13-god-placement.md` E1). The opening
shot is a `move_to`, so it is instant and hidden by the white; the other two
are `scrollTo` hops.

## H4 — the camera re-attaches — PASS

This is the check the whole change hangs on, because a finished `scrollTo`
calls `SetCameraProcess(nullptr)`, which parks a **detached** camera over the
destination rather than resuming the follow.

Measured rather than eyeballed. `findShape` prints each item's `px` offset
from the camera centre, and U8's projection makes that predictable: with the
Avatar at (3240, 8540), Felicitar at (3840, 7680) reads `px=(365, -12)`. Walk
him to (3472, 8668) and, **if and only if the camera followed**, the same god
must read

```
px_x = (3840-7680)/4 - (3472-8668)/4          = -960 + 1299 = 339
px_y = (3840+7680)/8 - (3472+8668)/8 + 20     = 1440 - 1517 + 20 = -57
```

Observed after the walk: `px=(339,-57)`. The other two matched their own
predictions too (`(-45,-249)` and `(403,-281)`). The Avatar also walked 232
units without freezing, which is the behavioural half of the same check.

## H5 — the scene still completes — PASS

Walked in from (3300, 8600) on map 18 with `templeOpen` and `shieldFixed` set,
`godsFree` cleared, and slot 30's reforged shield (shape 539) in the pack.

- On arrival, `findShape 860` reads frames **0, 2, 1** — sealed.
- After the scene, `godsFree = 1` and `findShape 860` reads **3, 5, 4** — freed.
- The `EggAOCeremony` process is gone from `Kernel::listProcesses`; a
  `CameraProcess` is back.

Run twice end to end under gdb (`r1`, `r2`) plus three more times without, all
five completing — including once on the final retimed build, which ended
`godsFree = 1`, frames 3/5/4, and the gods' `px` tracking a 112-unit diagonal
walk (`px_x` unchanged, `px_y` −28, which is what a walk along the screen's
y axis should do).

## H6 — the holds are long enough — PASS, after a retime

First pass gave each god about **0.5 s**, which is a flicker. Retimed, then
re-measured off a 13 fps capture by finding runs of byte-identical frames:

| Beat | First pass | Overshoot | Shipped |
|---|---|---|---|
| Timyra, after the fade | `wait(90)` → 0.60 s | `wait(360)` → 5.07 s | `wait(160)` → **1.70 s** |
| Felicitar | `wait(75)` → 0.52 s | `wait(300)` → 4.21 s | `wait(145)` → **1.67 s** |
| Doloras | `wait(75)` → 0.48 s | `wait(300)` → 4.28 s | `wait(145)` |
| Home + re-attach | `wait(40)`/`wait(20)` → 1.60 s | unchanged | `wait(90)`/`wait(45)` |

Each measurement is the length of a run of byte-identical frames in a 13 fps
capture, so it reads slightly short — the fade tail and the start of the next
scroll are outside the identical run. The shipped holds are a little under two
seconds each; the whole pan, fade-up to closing bark, is about ten.

Each `scrollTo` hop takes **0.7-0.8 s**, which is the engine's fixed 25 frames
— `I_scrollTo` reads its speed argument with `ARG_NULL16()` and discards it,
so the fourth argument is decoration.

**The first pass's timing reading was wrong and is worth recording as a
trap.** `wait(90)` measuring 0.60 s implies N/150 s; the overshoot pass gave
N/71 across two values, which is near `FREE::wait`'s documented 60ths, and the
shipped pass gives N/94 and N/87. The three passes do not agree on a rate,
which is the finding: the 0.5 s "holds" were short runs of identical frames in
a noisier capture, and there is a fixed overhead the identical-run method
cannot see. Do not do arithmetic on the nominal unit either — `FREE`'s
`Timer::start` and `Timer::isDone` compile to no-ops in our build. **Set a
scene beat by capturing it and looking, then stop.**

## H7 — depth sort — PARTIAL

`P3-doloras.png` has a low wall stub crossing her legs: the sanctum's
glob-carried shape-15 walls paint in front of a god standing behind one. This
is the same C1 finding as 2026-09-13, now seen at a camera position chosen by
the scene rather than by a screenshot, so it is on screen during the reveal.
Not addressed here.

## Findings not in the plan

> **Corrected 2026-09-25.** Findings 1 and 3 read the wrong class. Class 1409
> is retail FREE (0x581), shipped byte-identical; the offsets 7305 and 7399
> are retail's. Our compile is LVFREE, class 1454 (0x5AE), and there the
> `Camera::` statements are dropped: it carried no `calli 0xBE` at all, so
> `scrollBack` compiled to nothing and finding 3's bug was exactly the
> detached-camera mechanism. Fixed as `lv-patched/FREE.UNK` fix 2; record in
> `docs/playtest-2026-09-25-ceremony-plaques.md`. Finding 2 stands for LVFREE
> but does not affect scenes: every `wait()` spawns retail `0581:1C19`.

1. **`Camera::method(...)` half-compiles; it is not dropped.** `::` in an
   expression is a parse error, but the parser recovers by emitting `Camera`
   as an unknown identifier (`push 0`) and then binds the call to the
   intrinsic anyway. Evidence: the built class 1409 (FREE) carries `calli
   0xB5` at 7305 and `calli 0xBE` at 7399, and the build prints `WARN
   FREE.UNK:159: unknown identifier 'Camera' compiled as push 0` per site.
   `FREE.UNK:1427`'s own comment says these lines emit nothing — it is wrong,
   and this session believed it for an hour before the FLX-wide scan. Write
   the bare form in new code; the stray push is harmless but pointless.

2. **`FREE::wait`'s timer is a no-op.** `Timer::start` and `Timer::isDone`
   produce four `unknown identifier` / `no-op` warnings at `FREE.UNK:117-140`,
   so `wait(N)` is not measuring what its source says it measures. It is
   close enough to 60ths in practice that scenes work, but nothing in the
   build guarantees that.

3. **The Sacred Circle camera bug's cause is still open.** The detached-camera
   mechanism has the right shape, but `SHADES.UNK` scrolls at :168 and calls
   `scrollBack(20)` at :257, :329 and :553, and the built FREE does carry the
   re-attach. `traps.md` has been corrected from "CAUSE" to "a mechanism that
   would do this". Whoever chases it should check whether every exit path from
   the ceremony reaches one of those three calls.

## Harness anomalies

- **One unreproduced SIGSEGV.** ScummVM died about 20 s into a session where
  the Avatar was standing still outside the sanctum and no ceremony was
  running — a frame-mean scan shows no `FadeToWhite`, so it was not in the
  camera path. Two full runs under gdb afterwards, each playing the ceremony
  to completion, produced no crash and no backtrace. Recorded, not diagnosed.
- **The walk cursor sits at the window centre**, which is exactly where the
  pan frames each god, so early captures have a blue arrow on top of the
  subject. Park the pointer in a corner after the walk; `panfast.py` does.
- **`pkill -f` on a pattern that appears in your own command line kills the
  shell** (exit 144). Read the pid with `pgrep` and `kill` by number.
- **`drive.ensure()` attaches the console, and attached means paused.** A
  scene measured across `ensure()` calls looks frozen. The first read of this
  session called a working ceremony a hang for that reason.
- **`... | tail -N` in a backgrounded command buffers the whole run**, so a
  progress monitor watching that file sees nothing until it exits.

## Disk changes

- `agents/usecode-compiler/src/lv-new/AOSCENE.UNK` — the pan.
- `agents/usecode-compiler/src/test_uc_eggs.py` — seven checks on the camera
  sequence, read from the simulator's `intrinsic_log` (P5). 40 passed.
- `.claude/rules/camera-intrinsics.md` — new.
- `.claude/skills/playtest/traps.md` — the Sacred Circle entry, corrected.
- `shared/build/ARTIFACTS.sha256`, `build_scummvm.sh` — EUSECODE.FLX moved
  1503071 → 1503264 bytes; the 5000-byte detection md5 is unchanged.
- `~/.local/share/scummvm/saves/` — untouched. Slot 30 was loaded, never saved
  over; every flag change was made at runtime.
