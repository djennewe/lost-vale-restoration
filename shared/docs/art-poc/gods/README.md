# Zealan god statues — candidate renders, 2026-09-13

Nine candidates for the three gods imprisoned in the Inner Sanctum of Map 18
(`build_map_18.py:431-460`), which ship today as base-game shape 443
(`statue`, frames 0/1/2) — a mitigation the builder's own comment calls out as
not the thing the 1994 art list asks for.

Three design directions × three gods. Generated with `codex-image`
(Codex CLI's built-in `image_gen`, gpt-image-2), prompt-only, no reference
image — the route the 2026-07-19 proof statue used, and the one
`docs/research/2026-07-19-ai-art-generation.md:280` recommends for static
props. `generate.sh` in this directory is the run, prompts included; it skips
any candidate whose `_raw.png` already exists, so delete a file to re-roll it.

## Douglas picked (2026-09-13)

| God | Quality | Direction | File |
|---|---|---|---|
| Felicitar (Joy) | 301 | **B — standing** | `felicitar_B_raw.png` |
| Doloras (Sorrow) | 302 | **B — standing** | `doloras_B_raw.png` |
| Timyra (Fear) | 303 | **C — non-human** | `timyra_C_raw.png` |

The three directions were **A** enthroned (seated on a carved throne, closest
to the 2026-07-19 proof statue), **B** standing (robed figure on a stepped
plinth), **C** non-human (six-limbed chitinous idol on a rough-hewn base).
The six unpicked candidates are kept: a re-roll costs a subscription call and
the prompt set is here, but the *set* only matches if it comes from one run.

## Files

- `*_raw.png` — the generation, untouched. These are the pipeline's inputs.
  gpt-image-2 returned most of them with an alpha channel despite the flat
  magenta instruction, so they need `--no-key`; `doloras_B_raw.png` came back
  RGB and does need keying. Check before assuming.
- `*_x3.png` — the sprite **read back out of a patched `U8SHAPES.FLX`** at 3×,
  with `png2shape`'s own provenance label. This is what the engine draws.
- `contact-sheet.png` — all nine together.
- `generate.sh` — the generation run.

## Reproducing a render

```bash
tools/png2shape.py shared/docs/art-poc/gods/felicitar_B_raw.png \
    --donor 443 --height 110 --shape-id 860 --no-key \
    --flx /tmp/scratch.flx --no-typeflag --force \
    --preview /tmp/felicitar_B_x3.png
```

`--height 110` matches the proof statue's game scale. Encoded sizes ran
44×106 to 100×110 px, anchor bottom-centre on every one.

## CORRECTION (2026-09-13): the box art is the reference, and these are not it

`shared/data/lv-screenshots/box-smfront.jpg` — the Denis Loubet cover, which
Loubet authenticated himself (`docs/research/2026-07-19-ecosystem-and-history.md:241`)
— depicts the three gods directly, and they are **not statues**. They are nude
humanoid figures, dark bronze, suspended inside glowing faceted amber blocks:
a tall angular prism (standing, arms folded at the chest), a narrow vertical
slab (standing, arms raised overhead), and a cube (kneeling, head bowed).
`reference-box-art.png` here is that detail, enlarged.

So the nine candidates in this directory are carved temple statuary, which is
what shape 443 `statue` made everyone assume, and it is the wrong asset. They
are kept as a fallback set and because the sanctum has other statuary, but the
gods themselves get re-generated against the cover.

**The order inverts.** The box gives only the ENCASED state; the figure is the
thing to generate and the amber is the thing to add — the reverse of what
`resin/` did. The Art List's other entry, "Zealan God 1/2/3, speaking", has no
canonical depiction at all, so the free figure is derived from the one inside
the block.

**Pose stays identical between states** (decided 2026-09-13). The block
shatters and the same figure is still standing there, which reads as one being
in two states rather than one object swapped for another.

**Wanted later, and deliberately not built yet: frames for a freed god that
MOVES.** Seeing the Ancient Ones mobile — turning, gesturing, speaking — is
part of what the player earns at step 17, and a static freed frame is the
cheap version of that. Frames 6/7/8+ on shape 860, driven by `doAnim` or a
frame cycle in `AOSCENE`, is the shape of it. Filed in `TODO.md` §5.

## What this does NOT settle

- **No resin.** These are the bare idols. The 1994 Art List asks for both
  "Zealan God 1/2/3, encased in resin" **and** "…, speaking"
  (`shared/corpus/plot-documents/story-beats.yaml:372`), and nothing in
  `AOSCENE.UNK` currently touches the god items — the freeing is narrated, so
  the sprites are static for the whole game. Carrying both states as frames of
  one shape (0/1/2 encased, 3/4/5 free) is what makes the beat stageable
  later, via `setFrame` (proven idiom, `lv-patched/SHADES.UNK:658`).
- **Footpad.** `png2shape` reads donor 443's (3,3,3) box as too small for art
  this size and suggests `--footpad 6,6,8`. Unauthored so far.
- **Width.** The gods stand at the points of the ceremony triangle with props
  at ±128 units. Direction B is 44-60 px wide; A and C are 90-100. Timyra C,
  the pick, is the widest of all nine at 100 px — check its clearance when it
  is placed.
- **Nothing is injected.** The candidates went into a throwaway FLX. Custom
  art survives `tools/build_artifacts.sh` only if a build step injects it
  (`.claude/rules/shape-ids.md`); 859 is taken by the Tiny Tar, so the gods'
  shape is **860**.
