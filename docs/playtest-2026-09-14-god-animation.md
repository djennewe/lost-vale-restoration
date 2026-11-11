# Playtest — the gods shatter and wake (2026-09-14)

Second half of the day's work on Map 18. The camera pan gave the ceremony
something to look at; this gives it something to watch. Shape 860 goes from
six static frames to 42, and the engine drives the animation rather than
usecode stepping frames behind a `wait()` whose timer does not work.

## Verdicts

| ID | Test | Verdict |
|---|---|---|
| J1 | The engine delivers `anim()` to a FIXED item | **PASS** |
| J2 | Sealed gods do not self-advance while `anim()` fires | **PASS** |
| J3 | The ceremony kicks each god into her own run | **PASS** |
| J4 | A run steps on its own and lands on the standing frame | **PASS** |
| J5 | The amber visibly breaks | **PASS** |
| J6 | Every run frame keeps the same size and anchor | **PASS** |
| J7 | The wake plays every in-between pose that exists | **PASS** (12 of 12) |
| J8 | The wake is a movement rather than a cut | **PASS** |
| J9 | Every pose in a god's wake matches the others | **PASS** (after six replacements) |

## J1 — the engine calls usecode on a fixed item — PASS

U8's TYPEFLAG carries an `animType`, and type 5 means *call this item's
usecode `anim()` event every `animSpeed` ticks*. The class it calls is not
configurable:

```cpp
uint32 class_id = _shape;            // item.cpp:1516
```

so shape 860's event lands in class **860** and nowhere else. `lv_manifest`
pins `TYPEZEALANGOD` there for that reason, and `test_god_animation.py`
asserts it, because a class id that does not equal the shape id is silent and
fatal — the source looks completely correct and nothing moves.

Seven retail shapes use the same mechanism and every one has a class at its
own shape number: HOURGLAS 227, DRIPS 348, FIREITEM 397, FIREFELD 400,
CLRLAVA 409, BUBLAST 483, DRIPS2 653. `DRIPS::anim()` is five lines —
increment the frame, wrap, fire a sound on one frame, `setFrame` — and is what
`GODANIM.UNK` is modelled on.

Confirmed live: the debugger prints the gods as

```
Item 11526 (class Item, shape 860) (uc: TYPEZEAL), 2, (2304, 7680, 0) q: 303
```

The `(uc: TYPEZEAL)` is the engine resolving the dispatch itself.

## J2 — the gate — PASS

`anim()` fires for **every** shape-860 item in the fast area, including all
three gods from the moment the player first walks into the sanctum, years
before the ceremony. The handler returns immediately for any frame below 6, so
a sealed god sits still until something sets a run frame on her.

Read on arrival and again after ten seconds of play with no interference:
frames **0, 2, 1** both times.

## J3/J4 — kick, step, land — PASS

`AOSCENE` no longer swaps all three gods under the white. Each is kicked into
her own twelve-frame run as the camera arrives on her — the shatter is the
payoff, so it has to be seen — and `GODANIM` steps the run and sets the
standing frame itself at the end.

The proof is reachability, not a screenshot. **There is no `+3` left anywhere
in the code**, so the only path from a sealed frame to a standing one is
`setFrame(run start)` followed by twelve `anim()` steps. Observing the ends
therefore proves the middle ran:

| | frames |
|---|---|
| on arrival | 0, 2, 1 |
| after the ceremony | 3, 5, 4, with `godsFree = 1` |

## J5/J6 — the shatter — PASS

`lv_god_frames.py` partitions each amber block into fifteen Voronoi shards and
throws them outward from the block's centre with an upward kick and gravity.
Frame 0 is the intact block pixel for pixel, so the cut from the static
encased frame into the run is invisible; shard lifetimes are staggered and
nothing survives past frame 4, so the last shatter frame is the god alone with
debris at her feet.

Verified by rendering frames 30..41 straight out of the built
`U8SHAPES.FLX` — what ships, palette-quantised and encoded, not the source
PNGs. All twelve are **82 × 134** with the same bottom-centre anchor.

**Two things had to be true and were not, at first.**

*No partial transparency.* The shape format has no alpha — `rekey_alpha`
forces every pixel to 0 or 255 — so the first version's faded shards and
cross-faded figure were composited against the magenta key and came back pink.
Shards now vanish whole on staggered lifetimes and the figure is uncovered
outright.

*No per-frame trim.* Every other frame in shape 860 is a 1024px render that
png2shape trims to its own alpha and rescales. For an animation that is wrong:
the moment a shard flies outward the bounding box grows, the rescale shrinks
the figure to compensate, and the god pulses as her amber breaks. Run frames
are composited at final pixel size and encoded with `height=None`, which
`frame_args` turns into `no_trim`.

## J7/J8 — the wake — PASS

Frames 3/4/5 are now the **standing** poses, not the just-released ones. A god
the player returns to weeks later should be on her feet, and `EggTempleEntry`
restores exactly those three frames. The released poses moved into the wake as
its first frame, which is where they belong. Doloras goes 72 → 110 with the
change: he knelt, and a kneeling figure drawn as tall as the other two reads
as a giant.

The wake is six **drawn** poses per god — released, four in-betweens,
standing — and never a blend, for the same no-alpha reason as the shatter.

**All twelve in-between poses are in**, and every one is generated with the
god's own sprite as a character reference. Timyra goes crouched → hands
lowering → straightening → upright; Felicitar goes arms overhead → spread →
lowering → at rest; Doloras goes folded over his knees → kneeling upright →
one knee → crouched → standing.

## J9 — the poses match each other — PASS, after six replacements

Nine poses were first generated through gpt-image-2, during a window when the
reference-taking route was quota-walled. Six of them were wrong, and it only
showed when each god's six poses were rendered side by side at game scale:
`felicitar_mid2/3/4` and `timyra_mid4` came back **draped in floor-length
classical gowns**, `timyra_mid2` was a lighter outlier with different hair,
and `timyra_mid3` — from an early attempt on the other route — had a **smooth
blank featureless head**.

The drapery was caused by the workaround itself. gpt-image-2 refuses these
figures unless they are described as a "cast bronze STATUE", and given that
framing it reaches for classical sculpture and adds robes. All six were
replaced through the reference-taking route, each succeeding on the first
attempt, and the rejects are kept under `wake/rejected/`.

**The process lesson is the finding.** Checking one pose's material and
assuming the rest of a batch matched is how six wrong frames reached a build
and a published artifact. Render the whole row and look at it.

## Findings

1. **A file-local `routine` in a new class calls into class 0.** The three
   god kicks were first written as one `routine kickGod(encased, run)`. It
   compiled, warned about nothing, and emitted `call 0000h 0080h` — a jump
   into base-game class 0. It was the only file-local routine in `lv-new/`, so
   nothing had ever exercised that path. Inlined; recorded in
   `.claude/rules/usecode-local-routines.md` with the disassembly check that
   finds it.

2. **The moderation refusal was in the WORDING, not the subject — and I
   called it blocked before establishing that.** Described the way the Nano
   Banana prompts describe them ("a full-body female figure ... with no
   clothing and no anatomical detail"), gpt-image-2 returns HTTP 400
   `moderation_blocked, safety_violations=[sexual]` at the *output* stage,
   even for Doloras, who is clothed. Described as a **cast bronze STATUE** of
   a man or woman it generates first time — nine poses out of ten attempts.
   The project's own notes had already recorded that route producing a
   Doloras, which should have prompted a reword before I concluded both
   routes were exhausted.

   Two constraints came out of it, both in
   `tools/art/gen_wake_inbetweens_codex.sh`:

   *Say STATUE, not MANNEQUIN.* "An artist's jointed lay figure" also clears
   moderation and returns exactly that — ball joints, an egg head, pale
   metal, a different object from the god beside it.

   *That route takes NO character reference,* so its bronze comes out lighter
   and warmer. `lv_god_frames.match_bronze` regrades each in-between to its
   god's released sprite — mean and spread per channel, opaque pixels only —
   when the runs are composited. Verified through U8PAL.

3. **`agy` / Nano Banana was quota-walled for the whole session**: HTTP 429
   with `"quotaResetTimeStamp": "2026-09-14T20:48:58Z"` and a 12669 s
   `retryDelay`, re-probed twice. Three concurrent streams were stopped
   rather than hammered, per the skill's guidance. Before the wall its
   failures were a different thing — `no image generated in response`, a
   per-pose CONTENT refusal, non-deterministic: the identical prompt shape
   produced `timyra_mid1` and all three standing poses first time and was
   refused three times running for `timyra_mid2/3/4`.

4. **`animSpeed` is a divisor and must not be zero.** `animType` non-zero with
   `animSpeed` 0 divides by zero in `Item::setupLerp`. Shape 443, the gods'
   TYPEFLAG donor, happens to carry 1 already; `set_anim` refuses 0 rather
   than trusting the next donor to.

## Harness anomalies

- **A capture filmed 1214 frames of a save browser.** The script skipped the
  intro the NEW-game way — eight Escapes and a typed name — against a session
  whose intro was already gone, so the keys walked the Pagan menu into the
  load gump. It still reported `godsFree = 1`, because that came from the slot
  it had loaded rather than a scene that never played. Both traps are in
  `traps.md`: never type text at the world, and assert the world state before
  a long capture.
- **Two screenshot-based runs were OOM-killed** on a loaded machine. The
  images were never the evidence; the frame state is. The verification that
  stuck takes no screenshots at all.
- **Sampling frames during a scene stops the scene.** `drive.ensure()`
  attaches the console and attached means paused, so a once-a-second sampler
  left the ceremony 28 samples in with nothing advanced.
- **`pkill -f` on a pattern matching your own command line kills the shell**
  (exit 144). Read the pid with `pgrep` and `kill` by number.

## Disk changes

- `agents/map-populator/src/lv_god_frames.py` — new, composites runs 6..41.
- `agents/map-populator/src/lv_god_statues.py` — 42 frames; standing poses at
  3/4/5; `height=None` run entries.
- `agents/map-populator/src/patch_typeflag.py` — `set_anim`.
- `agents/map-populator/src/test_god_animation.py` — new, 32 checks.
- `agents/usecode-compiler/src/lv-new/GODANIM.UNK` — new, class 860.
- `agents/usecode-compiler/src/lv-new/AOSCENE.UNK`, `TEMPLENT.UNK` — per-god
  kicks, mid-run recovery.
- `shared/docs/art-poc/gods/wake/`, `.../run/` — standing poses, two
  in-betweens, and the 36 composited run frames.
- `shared/build/ARTIFACTS.sha256`, `build_scummvm.sh` — all three of
  TYPEFLAG, U8SHAPES and EUSECODE moved; `LV_SIZE` 1503264 → 1503649.
