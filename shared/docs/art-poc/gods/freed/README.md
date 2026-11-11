# The three gods, freed — final art (2026-09-13)

The gods as the box cover depicts them: humanoid figures, not statues. These
are the FREED state (frames 3/4/5 of shape 860); the encased state is the same
figures inside amber blocks, built from these. The parent directory's README
carries the correction that sent the earlier carved-statue set to `attempts`.

| God | Pose | Source | Sprite |
|---|---|---|---|
| Felicitar (Joy, q301) | standing, both arms raised overhead, head back | `felicitar_final_raw.png` | 24 × 110 px |
| Doloras (Sorrow, q302) | kneeling, folded over the knees, head bowed | `doloras_final_raw.png` | 53 × 72 px |
| Timyra (Fear, q303) | turned right, knees bent, hands at her face | `timyra_final_raw.png` | 43 × 110 px |

Poses come from the cover's three figures; which god gets which is our
reading of the affect. Timyra is female, as the cover plainly shows.

## Two things that are easy to get wrong when re-encoding these

**Doloras builds at height 72, not 110.** A kneeling figure that stands as
tall as the other two reads as a giant. At 110 she encodes 81 px wide and
crowds the ±128 prop spacing; at 72 she is 53 px and sits right.

**`--key-tolerance 130`.** The generator's magenta bleeds into the
anti-aliased edge, and png2shape's default tolerance of 60 leaves a pink
fringe all round the silhouette. Nothing else about the encode is unusual:

```bash
tools/png2shape.py shared/docs/art-poc/gods/freed/felicitar_final_raw.png \
    --donor 443 --height 110 --key-tolerance 130 --shape-id 860 \
    --flx /tmp/scratch.flx --no-typeflag --force --preview /tmp/f_x3.png
```

## Doll anatomy, and where it stopped

Douglas asked for no clothing with no anatomy visible — smooth unbroken bronze
as on a cast figurine. Both standing goddesses re-rendered that way on the
first ask, through `agy`/Nano Banana with the cover crop as reference.

**The kneeling figure was refused three times** — worded plainly, as a bronze
figurine, and as a wooden artist's mannequin. Each returned `no image
generated in response` with no file written. A trivial probe generated
instantly straight afterwards, so this was a content refusal on the kneeling
pose in combination, not the quota the skill warns about.

`codex`/gpt-image-2 did produce one (`attempts/doloras_free4_raw.png`, 37 × 55)
and it is genuinely featureless, but it comes out glossier, brighter and more
abstract — a different material next to two matte dithered figures. **Decision
2026-09-13: Doloras keeps the loincloth.** One garment on one god is a smaller
inconsistency than one figure made of different metal. If she is ever wanted
bare, hand-edit the few pixels at 53 × 72 rather than generating again.

## attempts/

Every render that did not ship, kept because the set only matches if it comes
from one run and a re-roll cannot reproduce a discarded one. Timyra took four
passes (male-reading with folded arms; female but facing left and standing
straight; turned right but twisted at the waist; whole body turned together)
and Doloras three before the kneel was compact enough to use.
