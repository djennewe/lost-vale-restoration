# The gods waking — standing poses (2026-09-14)

The end state of the shatter-and-wake run: each god on her own feet, neutral,
facing the Avatar. Asked for in those words — "assuming a neutral stance, and
turning to face the Avatar".

| God | From (frame 3/4/5 today) | To |
|---|---|---|
| Timyra (Fear, q303) | turned right, knees bent, hands at her face | `timyra_stand_raw.png` |
| Felicitar (Joy, q301) | standing, both arms raised overhead, head back | `felicitar_stand_raw.png` |
| Doloras (Sorrow, q302) | kneeling, folded over the knees, head bowed | `doloras_stand_raw.png` |

All three generated through `agy`/Nano Banana with **that god's own freed
sprite passed as the character reference**, which is what keeps the material,
proportions and dithering matching across a pose change. Same magenta key,
same `--key-tolerance 130 --key-despill 16` encode as the freed set.

## Two things to know before re-rolling any of these

**Doloras is male, and that is not a slip.** The reference
(`freed/doloras_final_raw.png`) is a bald muscular male figure kneeling in a
cloth wrap, so the standing render matched it. Timyra and Felicitar are
female. The set has always been two goddesses and one god; do not "correct"
him.

**Doloras changes height when he stands.** The freed set builds him at
`--height 72` because a kneeling figure that stands as tall as the other two
reads as a giant. Standing, he belongs at 110 like the others — the height
entry in `lv_god_statues.py` has to move with the pose.

## Where these go

They become frames **3/4/5** — the freed REST state — replacing the
just-released poses, which move into the wake run as its first frame. That is
what makes `EggTempleEntry`'s restore put a standing god in the sanctum when
the player walks back in later, rather than one still flinching.

## The in-betweens (`*_mid1..4_raw.png`)

Four per god, so a wake is six DRAWN poses — released, mid1..mid4, standing —
and never a blend. That constraint is not stylistic: the U8 shape format has
no alpha, so a cross-dissolve between two poses is half-transparent across the
overlap, gets composited against the magenta key, and comes back pink. The
first attempt at the wake did exactly that.

Each in-between is referenced against the NEAREST end pose — the released
sprite for mid1/mid2, the standing sprite for mid3/mid4 — so a generated frame
always sits next to the key it has to match and the set does not drift across
the sequence.

The motion, per god:

| | Timyra (fear) | Felicitar (joy) | Doloras (sorrow) |
|---|---|---|---|
| released | hands at her face, turned right, knees bent | arms overhead, head back | kneeling, folded over his knees |
| mid1 | hands down to chest, head lifting | arms down to shoulder height, still spread | still kneeling, back straightening, head lifting |
| mid2 | hands at waist, turning to front | arms at chest, drawn in, head levelling | up on one knee, hand on the raised knee |
| mid3 | almost upright and front-on | arms near the hips, upright | pushing up onto both feet, still crouched |
| mid4 | upright, shoulders still settling | hands just barely lifted | upright, shoulders still settling |
| standing | neutral, facing the Avatar | neutral, facing the Avatar | neutral, facing the Avatar |

`lv_god_frames.py` scales each one on the ramp between the released and
standing heights rather than to a flat height, which matters only for Doloras
— he rises from a kneel and genuinely grows over the sequence, so a flat
height would snap him taller on the last frame.

If any of these are ever regenerated, regenerate the whole god's four: they
are a set, and a single re-roll will not match the three beside it.

## Status: COMPLETE — all twelve in-betweens, all through `agy`

Every wake pose is generated with the god's own sprite as a character
reference. That is the whole trick: the route matches material, proportions
and hair for free, and it does not refuse these subjects.

**The nine poses first made through `codex` / gpt-image-2 were all replaced,
and `rejected/` keeps them.** They were made during a window when `agy` was
quota-walled, and six of them were wrong in ways only visible once each god's
six poses were rendered side by side at game scale:

| what went wrong | which |
|---|---|
| draped in a floor-length classical gown | `felicitar_mid2/3/4`, `timyra_mid4` |
| lighter, different hair — an outlier in the row | `timyra_mid2` |
| smooth blank featureless head, no hair | `timyra_mid3` (an early `agy` attempt) |

**The drapery was caused by the workaround, not by the model being awkward.**
gpt-image-2 refuses these figures unless they are described as a "cast bronze
STATUE" — and given that framing it reaches for classical sculpture and puts
them in robes. The statue wording was only ever needed because `agy` was
unavailable. With `agy` back, no statue framing is needed and no drapery
appears.

If a pose ever has to come from gpt-image-2 again, rule out both failure modes
by name — "NO gown, NO robe, NO drapery of any kind" and "the SAME long hair
and face as the reference; do NOT give her a smooth blank featureless head" —
and then **render the god's whole six-pose row at game scale and look at it**.
Checking one pose and assuming the rest of the batch matched is exactly how
six wrong frames got as far as a build.

