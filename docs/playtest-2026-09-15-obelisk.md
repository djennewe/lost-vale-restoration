# Playtest — the Magnetic Obelisk, shape 861, on Map 17 (2026-09-15)

First in-engine look at the art track's first item (`docs/art-track.md`,
contract 1): the Cloud City obelisk as custom art on the main plaza's dais,
where a 721 `chimney` had stood since the first build. Fresh world, the
canonical build (`FIXED.DAT 7a8ccfb0…`, `U8SHAPES.FLX 260eca56…` for
sections A–C and `fc7cabfb…` after the swap in section D,
`TYPEFLAG.DAT 21ef01bc…`, `EUSECODE.FLX` unchanged at `a71868ae…`), the
640×400 canvas, plates cropped at `+565+336`.

## Verdicts

| ID | Test | Verdict |
|---|---|---|
| A1 | Shape 861 draws in the world, on the dais top tier, at the recorded position | **PASS** |
| A2 | Depth sort: the Avatar behind the obelisk is drawn behind it; the whole sprite reads at 1x | **PASS** |
| A3 | A single click on it prints nothing (no usecode class at 861) | **PASS** (plate evidence; see anomaly 1) |
| A4 | The obelisk's box blocks: a walk up the dais stops at its edge | **PASS** |
| B1 | `findShape 861` returns exactly one item with the contract's flags and quality | **PASS** |
| C1 | Scale against the plaza columns and the 1994 screenshot | **PASS** (a decision, recorded) |
| D | Candidate A swapped in on Douglas's pick; only `U8SHAPES.FLX` moved; same item, same box | **PASS** |

## A1 — it draws — PASS

`A1-obelisk-from-the-south.png`, Avatar at (4352, 7424, 0), the same
framing as `A0-plaza-before-721-chimney.png` taken on the previous build
that morning. The chimney is gone; the obelisk stands on the top tier's
centre tile, foot on the flagstone, glyphs legible, the north candelabrum
correctly hidden behind its shaft. Its top runs a few pixels past the
viewport edge at this framing, which A2 resolves.

## A2 — the whole sprite, the Avatar behind it — PASS

`A2-whole-sprite-avatar-behind.png`, Avatar at (3584, 6656, 0), north-west
of the dais. The full 69×126 sprite is in frame: the stepped foot sits on
the tile's 2:1 diamond, the cap's lit top plane shows, both faces read with
the left lighter than the right. The Avatar, whose sprite overlaps the
obelisk's top by a dozen pixels, is drawn behind it — the (4,4,12) box
sorts as a solid should. No fringe, no key bleed over the lit stone.

## A3 — a click prints nothing — PASS

`A3-click-no-bark.png`, shot 0.35 s after a single left click on the shaft
(cursor visible on it). No bark, no gump, no name — the chimney printed
"chimney" here. Structural confirmation: `EUSECODE.FLX` entry 863
(= class 861) is empty (offset 0, size 0), so the engine's shape-number
dispatch (`item.cpp:1516`) has nothing to call; entry 862, the gods'
GODANIM, is 248 bytes beside it, as expected.

## A4 — the box blocks — PASS

From (4352, 7424, 0) the `walk 0 -70 3` verb walked the Avatar up both
dais tiers (8-unit steps, fine) and into the obelisk. He stopped at
**(4080, 7232, 16)**: on the top tier, his 64-unit body box spanning
y 7168..7232, one unit clear of the obelisk's box (y 7039..7167). That is
`Box::overlaps` refusing the next step, and it is what
`test_art_props.py` asserts from the built artifacts.
`A4-walked-up-to-the-foot.png` shows him against the foot, his near arm
drawn behind the shaft.

## B1 — the engine's own description — PASS

```
] ObjectManager::findShape 861
Item 8290 (class Item, shape 861), 0, (4095, 7167, 16) q: 90, m: 0, n: 0,
  f: 0x2000, ef: 0x3 shapeinfo f: 3, fam: 0, et: 0) px=(0,-61)
findShape 861: 1 found
```

One item; position (4095, 7167, 16), the top tier's centre tile; quality
90 kept for the future MAGNET wiring; `shapeinfo f: 3` = SI_FIXED|SI_SOLID,
the donor 443's flags, no SI_NOISY (721's), no SI_DAMAGING.

## C1 — scale — PASS, as a decision

`C1-candidates-on-the-plaza-1x.png`: the three `agy` candidates pushed
through the real pipeline and pasted at 1x onto the A0 plate, the chimney's
foot as the anchor. The plaza columns (8 + 40 + 40 world-z) top out near
90 px; at `--height 128` the obelisk overtops them by about half again,
which is the relationship the 1994 screenshot shows between the obelisk and
the drums it stands on. Candidate C shipped; the reasons and the other two
are in `shared/docs/art-poc/obelisk/README.md`.

## D — candidate A shipped after Douglas's pick — PASS

Douglas, shown the three candidates on the plaza: *"I like A."* The swap
was the one-filename change the contract promised (`lv_art_props.py`, row
1), then `--record`: only `U8SHAPES.FLX` moved (`fc7cabfb…`), because A
takes the same footpad and the same tile, so `TYPEFLAG.DAT`, `FIXED.DAT`
and the pins are byte-identical to the C build. A second build reproduced
it; the estate stayed 30/30; `findShape 861` returns the same item at the
same position.

- `D1-candidate-A-whole-sprite.png` — the A2 viewpoint, Avatar at
  (3584, 6656, 0): the near-black shaft, the skull at the foot's corner,
  the glyphs dimmer than C's but present, the whole sprite in frame and
  the Avatar sorted behind it.
- `D2-candidate-A-from-the-south.png` — the A1 viewpoint, Avatar at
  (4352, 7424, 0).

C stays in `shared/docs/art-poc/obelisk/` as the alternative, one
filename away.

## Findings that were not part of the plan

1. **The installer does not feed the Linux harness.** `install_lv.sh`
   writes into `shared/data/u8-install` (the base install, backed up as
   `.bak`, which the builders read as their pristine base). The harness
   runs `shared/u8-lv-patched`, which nothing in the repo populates: it
   was hand-synced on 2026-09-15 02:12 and again for this test (all four
   artifacts, `FIXED.DAT` in both places it exists there). The
   `/artifact-rehash` skill's "launch it" step runs `install_lv.sh --run`,
   which on this machine launches nothing (no `scummvm` in PATH) and
   touches the wrong directory for the harness.
2. **`session.sh dbg` is dead on this build.** It writes to the command
   file the console no longer drains (`dbg.sh`'s header says the stdin
   pipe stopped being consumed after the 2026-09-03 rebuild). Every `dbg`
   call this session returned "no response after attach+retry".
   `tools/playtest-linux/dbg.sh` (keystrokes into the overlay console)
   works, and `Cheat::toggle` has to go first or every teleport prints
   `Cheats are disabled`.
3. **`session.sh start` comes up with the backpack gump open.** Three
   fresh starts, three times the pack was over the centre of the screen.
   A double-click on the pack's own frame closes it (`ContainerGump::
   onMouseDouble` treats a double-click on the gump as `use` on its
   owner); Escape opens the pause book instead, and `i` reopened it.
4. **The minimap gump is up** in every plate (top-left). Not opened by
   this session's commands; it survived the restarts. Cosmetic.

## Harness anomalies

1. **Clicks do not log.** With `debugflag_enable Object` confirmed in the
   log ("Enabled debug flag 'Object'"), the A3 click grew the log by
   0 bytes — no `dumpInfo()`. The traps file says every click logs the
   item; that was true of earlier sessions and is not true of this one.
   A3's evidence is therefore the plate and the empty usecode entry, not
   a log line.

## Disk changes

- `shared/u8-lv-patched/`: the four artifacts replaced with the
  2026-09-15 canonical build (see finding 1).
- `~/.config/scummvm/scummvm.ini` untouched. It was already at the 640×400
  canvas (`width=640 height=400 aspect_ratio=false scaler=normal`) when
  this session began, despite HANDOFF saying it had been restored.
- The playtest session was stopped at the end.
