# Research: Design Fidelity Backlog

Worked 2026-07-25 against section 7 of
`docs/reviews/2026-07-19-improvement-plan.md`. One section per backlog item.

Sections 2, 3 and 4 are first-hand analysis of the recovered 1994 source.
Sections 1 and 5 used two parallel researchers for the web and scan work
(Pentagram doc retrieval and cross-check; the 38 Ultima Codex gallery scans).
**Every load-bearing claim either agent returned was re-verified here before
being written down** — the `0x79` terminator count, the intrinsic-table size
and the unimplemented `0x9A` slot, the `killProcesses` wildcard, the
`TypeTinyAvatar` rename, the `Apathos` translation pair, and the pinned-doc
sha256. The 2026-07-19 research doc records that two of its five agents
returned stub output on the first pass; that is why nothing here is passed
through unchecked.

**Evidence rules used throughout.** Every claim is tagged:

- **VERIFIED** — I read it myself, in the artifact named, at the line/offset
  named. Anyone can re-run the command shown and see the same thing.
- **CLAIMED** — a source asserts it and I could not reach the primary.
- **INFERRED** — my reading of verified evidence, not something any source says.

The primary sources ranked, highest first: the shipped base game's own
`EUSECODE.FLX` string table (Origin, 1994) > the recovered 1994 Lost Vale
usecode snapshot (`shared/data/lv-usecode/`, read-only) > the scanned 1994
design documents in `gog/ultima_8_lost_vale_design_documents.zip` > Sheri
Graner Ray's 2009/2014 memoir > fan wikis.

The memoir is a **2009 recollection of 1994 work**. Where it disagrees with
the recovered source, this document treats the source as what was built and
the memoir as what was remembered. Sections 2, 3 and 4 each turn on exactly
that distinction.

---

## 1. Pentagram format docs, pinned and reconciled against ScummVM

Pinned files live in `shared/corpus/pentagram-docs/`. See that directory's
`README.md` for per-document provenance (source URL, fetch status) and
`SCUMMVM-DELTA.md` for the disagreement table.

**Standing rule, restated because it is the whole point of the exercise:**
the Pentagram `docs/` folder is a 2002-2010 reverse-engineering write-up. It
is a *description* of the format, not the format. The live engine is the
format. Where the two disagree we follow
`scummvm-lv/engines/ultima/ultima8/usecode/uc_machine.cpp` for opcode
semantics and `.../usecode/u8_intrinsics.h` for the intrinsic table, and we
record the doc's reading alongside so a future reader knows the doc is not
simply wrong-and-deleted but superseded.

### What was pinned

**7 of 7 requested documents obtained verbatim**, all HTTP 200 from
`raw.githubusercontent.com/pentagram-u8/pentagram/master/docs/`. No mirror and
no archive.org fallback was needed. Each pinned file carries a five-line
provenance header recording the source URL, the byte count and a sha256 of the
body; strip the header and the original file is byte-identical. I spot-checked
`u8usecode.txt` — 2171 bytes, sha256 reproduces. VERIFIED.

Six supplementary files were pinned alongside them, for a reason that changes
the shape of the task:

> **`u8usecode.txt` contains no opcode table.** It is 2171 bytes covering the
> FLX container, the 12-byte class header, and the 32-entry event table.
> Nothing in Pentagram's `docs/` has an opcode table at all — Pentagram's
> opcode knowledge lives in its *source*.

So the opcode cross-check ran against `convert/Convert.h` (the operand-size
switch), `convert/u8/ConvertUsecodeU8.h` (the intrinsic table our own table
descends from), `tools/disasm/Disasm.cpp`, `usecode/u8intrinsics.h`, and
`docs/design/ucmachine.txt`. All six are pinned too.

### Cross-check results

**Opcodes: exact agreement.** 105 opcodes in `uc_machine.cpp`, 105 in our
disassembler, zero difference in either direction, operand sizes matching on
every one including `0x5C` (symbol), `0x58` (spawn inline) and `0x54`
(implies).

**Intrinsics: our 258-entry table matches the engine.** I re-counted the
engine's table myself: `U8Intrinsics[]` in
`scummvm-lv/engines/ultima/ultima8/usecode/u8_intrinsics.h` has exactly **258**
entries, and index alignment against our table is perfect — there is no slot
where ScummVM implements something our table calls unused. VERIFIED. Pentagram's
own table has 257 (it is missing the last slot). The 28 name differences are
naming conventions for the same function (`getType`/`getShape`,
`legal_create`/`legalCreateAtCoords`).

**Map format** agrees across the doc, the engine, and `u8_map.py`.
**TYPEFLAG** is where the doc is weakest — it marks roughly 20 bits "Unknown"
that the engine names — but `parse_typeflag.py` already follows the engine.

The gfx, `shapes.cmp`, anim and encoding docs are pinned but **not**
cross-checked. `SCUMMVM-DELTA.md` says so explicitly rather than implying
coverage it does not have.

### The one place we do NOT follow ScummVM

Opcode **`0x79`**, and it is worth stating carefully because it is the single
exception to the rule this section exists to enforce.

- **ScummVM** (`uc_machine.cpp:1968-1976`) handles `0x79` as "push address of
  global", unconditionally reading a uint16. The comment says "(Crusader
  only)" but **there is no `GAME_IS_U8` guard** — the U8 path falls into the
  same case. `0x7A` is its end-of-function. VERIFIED by reading the switch.
- **Pentagram** (`convert/Convert.h`) makes it game-conditional:
  end-of-function in U8, global-address in Crusader.
- **The retail data settles it.** I scanned every entry of the shipped
  `EUSECODE.FLX` myself: of 518 non-empty entries, **516 end with byte
  `0x79`** and the other two end with `0x00`. Zero end with `0x7A`. VERIFIED,
  independently of the researcher who first raised it.

So on this one row Pentagram-U8 and the data are right and the live engine's
comment is aspirational. **We follow Pentagram here**, as our disassembler and
assembler already do. The reason this is harmless at runtime is that the
trailing `0x79` is a class terminator that execution never reaches — functions
end at `ret`. It matters for *disassembly boundaries*, not for the VM. Recording
it because a future reader who applies "ScummVM wins" mechanically to this row
would break the round-trip.

### The latent bug this turned up

Following the intrinsic table down found a live defect in our own codegen,
distinct from the `enterConvo()` gap already noted in `CLAUDE.md`. Every link
verified by hand:

1. `agents/usecode-compiler/src/u8c_codegen.py:1118-1128` emits
   `calli 0x04, 0x009A` (`Npc::getNpcSlot()`) followed by `push retval` and
   `calli 0x04, 0x00CB` (`Kernel::resetRef`) — **three times per
   `enterConvo()`**, once each for Loiter (0x0205), Anim (0x00F0) and
   Pathfind (0x0204).
2. **ScummVM does not implement intrinsic `0x9A`.** Index 154 of
   `U8Intrinsics[]` is literally `0`. VERIFIED by parsing the array.
3. `uc_machine.cpp:361-363`: on `_intrinsics[func] == 0` the VM sets
   `p->_temp32 = 0`. So `getNpcSlot()` returns **0**.
4. That 0 is pushed and passed to `Kernel::I_resetRef` →
   `killProcesses(0, type, true)` (`kernel.cpp:490`).
5. `kernel.cpp:311`: the guard is
   `(p->_itemNum != 0 && (objid == 0 || objid == p->_itemNum) && …)`.
   **`objid == 0` is a wildcard matching every object.**

INFERRED consequence, not yet observed in a running game: **every conversation
in the expansion kills the Loiter, Anim and Pathfind processes of every NPC on
the map**, not just the NPC being spoken to. That reaches all 19 files with an
`enterConvo()`. `CLAUDE.md` already flags `enterConvo()` as incomplete but
describes a different and much smaller gap (missing `turnToFace`, missing
invisible check), so this is a separate defect and should be logged as one.

Confirming it needs a play test with `debuglevel 1`, watching for the
`LV: I_resetRef item=0` line that `kernel.cpp:489` already prints — the
instrumentation is in the patched engine.

Three further unimplemented intrinsics are called by our compiled code:
`isInNpc` (MAGNET's `cleanSweep`), `Item::combine` (FREE), and `freeEquip`
(ZEALSHLD). None of the four is called anywhere in retail U8, which is exactly
why ScummVM never implemented them — the expansion is the first code to reach
them. CLAIMED at the level of "these are the only four"; the four names
themselves are VERIFIED.

Two smaller deltas, both recorded in `SCUMMVM-DELTA.md` and neither currently
biting: the glob placement formula in `u8mapfmt.txt` is missing a `+1` on X
and Y that `glob_egg.cpp:64-65` applies (no impact while we write glob eggs
and let the engine expand them), and `u8_map.py:62-63` unpacks X/Y as signed
where the engine treats them as unsigned on disk (harmless — retail max is
exactly 32767, and the failure mode is a loud `struct.error`, not silent
corruption).

---

## 2. MAGNET.UNK vs the ankh staging

### The memoir, verbatim

Sheri Graner Ray, "Looking Back on 20 years — The Lost Vale"
(https://sherigranerray.com/?p=13, reprinting her LiveJournal of 2009-11-24),
fetched 2026-07-25. VERIFIED — quoted from the fetched page:

> When you finally work your way up the mountain (a jumping game) you find the
> cloud city is actually abandoned. There are no sleeping gods. The player
> must try to figure out what happens. Now. .. when you first entered the
> city.. you were hit by a magic spell. This magic spell pulls ALL your
> equipment from your body and sticks it to an obelisk in the center of the
> city. You have to figure out how to get it loose. The answer was in a room
> full of candlesticks. You had to light the candlesticks in the shape of an
> ankh to get it to release your equipment. (And.. I might add.. that was my
> work.. and probably the LAMEST design I've EVER done!!! LOL!)

Five separable assertions: (a) entering strips all equipment, (b) the
equipment sticks to an obelisk at the city centre, (c) the release mechanism
is a separate room of candlesticks, (d) the solution is a *lit subset* of
those candlesticks, (e) that subset forms an ankh.

### What the recovered source actually implements

**(a) and (b) — fully supported. VERIFIED.**
`shared/data/lv-usecode/LOST VALE/MAGNET.UNK` (516 lines) is
`eggclass EggMagnet inherits Egg` with five processes. `friskAvatar()`
(lines 43-228) runs 22 `foreach recursive ... within container Avatar`
sweeps — every potion, the Cloud City key at frame 3, the endless bag of
reagents, magic scrolls, the four elemental foci, both magic armours, shield,
arms, legs, helm, and eight named weapons (Hammer of Strength, Deceiver,
Slayer, Scimitar of Kumash Gor, Korghin's Fang, Flame Sting, Protector, Blade
of Striking) — `push()`es each and then (lines 222-226):

```
for num = 1 to count
{
    item.referent = getEtherealTop();
    item.pop(15615, 19839, 120);
}
```

Every stripped item is popped to **one** hard-coded world coordinate,
`(15615, 19839, 120)`. That single coordinate *is* the obelisk. `cleanSweep()`
(lines 231-502) does the same sweep over a 50-cell radius of the egg to catch
anything the player drops or stashes, explicitly excluding items already at
`x=15615, y=19839` so it does not re-vacuum the pile.

**(c) and (d) — fully supported. VERIFIED.**
`LOST VALE/CANTRK.UNK` is `eggclass EggCandleTrick inherits Egg`. Its `hatch`
returns immediately unless `monolithSucks` is true, then does a single
`foreach candle where (type = TypeMagicCandle) within 50 cells of referent`,
switching on `candle.getQuality()` 1 through 6 and recording each candle's
lit state into `candleOne`..`candleSix` from `getFrame() = 0`. The two
classes are joined by exactly two global flags, and the flag graph confirms
the coupling is real in the compiled artifact
(`shared/docs/wiring-data.md`: bit 1051 `candlesCorrect`, writer
EGGCANDLETRICK, reader EGGMAGNET; bit 1052 `monolithSucks`, writers
EGGCANDLETRICK and EGGMAGNET). VERIFIED.

So the mechanism the memoir describes is not approximately in the source, it
is *literally* in the source, in two files, wired by two flags: strip-to-
obelisk, and a separate candle-state check that releases it.

**(e) — NOT supported by the source, and cannot be. VERIFIED (negative).**
Nothing in `CANTRK.UNK` encodes a shape. The class tests candle *quality*
(an identity tag, 1..6) and candle *frame* (lit/unlit). It never reads a
candle's position. The ankh cannot live in the usecode; it can only ever have
lived in the **map placement** of the six candlesticks. That map is lost. So
the ankh is a map-authoring decision for us, and the source constrains it to
exactly one thing: which of the six numbered candles must burn.

### Which candles — and the revision conflict

The snapshot contains two revisions of CANTRK and they **disagree**. VERIFIED.

| | `LOST VALE/CANTRK.UNK` (142 lines) | `UNK files/UNK/CANTRK.UNK` (127 lines) |
|---|---|---|
| candles 1-5 polarity | `frame = 0` → unlit | same |
| **candle 6 polarity** | `frame = 0` → **unlit** (line 96-104) | `frame = 0` → **lit** (line 96-104) — inverted vs the other five |
| solution test | nested ifs (lines 109-132) | one flat `and` chain (lines 108-117) |
| **candles that must burn** | **2 and 6** | **2 only** (6 must be dark) |

The polarity flip on candle six in the dev-directory copy is a bug: it is the
only one of the six written the other way round. The `LOST VALE/` copy has it
consistent with the other five and restructures the test into nested ifs,
which reads as the fix. `build_eusecode.py` already prefers `LOST VALE/` over
`UNK files/UNK/` (source tiers at `build_eusecode.py:105-116`), so the
version we compile is the **2-and-6** one. VERIFIED.

**Two lit candles out of six does not draw an ankh.** INFERRED, and this is
the honest limit of the evidence. Either the room held more candlesticks than
the six the code tracks and the ankh is traced by the *whole* arrangement with
only two being switchable, or CANTRK was still in flux when the snapshot was
taken. The placeholder-flavoured flag name `monolithSucks` and the surviving
revision conflict both point at "still in flux". I could not resolve this;
the 22-screenshot set does not include a candle room (I checked
`screen10`-`screen14`; `screen11.gif` shows the obelisk itself, ringed by
white pillars, with a stacked cluster of objects at its base consistent with
`pop()`-to-one-coordinate, but no candles).

### What restoring it would take (quest step 12)

Current state: **both classes compile and are pinned, and both are orphans**
— nothing on any map triggers either. `shared/docs/wiring-data.md` lists
EGGCANDLETRICK (1431) and EGGMAGNET (1432) in the 19-orphan list. VERIFIED.

Concretely:

1. **Fix the egg quality on the existing obelisk trigger.**
   `agents/map-populator/src/build_map_17.py:229` places the MAGNET trigger
   egg with `quality=3`. The egg-quality convention is `class_id - 0x47F`
   (documented at `build_map_10.py:63` and used as `PLNTST_EGG_QUALITY = 283`
   for EggPlantTest 1434). EGGMAGNET is 1432, so the quality must be **281**,
   not 3. As written the egg addresses base class 1154. VERIFIED — this is a
   live bug, not a design question.
2. **Add the CANTRK egg**, quality **280** (1431 - 1151), in the candle room.
3. **Place six `TypeMagicCandle` items, qualities 1-6, all at frame 0**,
   within **1600 world units** of that egg (`within 50 cells`; the engine's
   cell is 32 world units — VERIFIED at
   `scummvm-lv/engines/ultima/ultima8/world/super_sprite_process.cpp:120`,
   `getCellsPerRound() * 32.0f`). Arrange the six so that lighting **2 and 6**
   completes an ankh — that arrangement is ours to author and is the only
   place the memoir's ankh can be honoured.
4. **Reconcile the obelisk coordinate.** MAGNET pops to `(15615, 19839, 120)`
   unconditionally. Map 17's obelisk is placed at `x0+2048, y0+2048` =
   `(4096, 7168)` (`build_map_17.py:177-224`). Either move the obelisk to the
   1994 coordinate — which is what map 10 already does for the Passage Test
   grounds — or patch the `pop()` target in an `lv-patched/MAGNET.UNK`.
   Leaving it is the worst option: the player's entire kit teleports into
   unbuilt space. VERIFIED (both coordinates read from source).
5. **Watch the candle shape's frame count.** `TypeMagicCandle` maps to shape
   295 in `u8c_symbols.py:271`, which `lv_shapes.py:231` flags as
   `SHAPE_TORCH = 295 # wall torch/sconce (UNVERIFIED — named from usage)`.
   Shape 295 has **2 frames** and is `SI_FIXED, SI_SOLID, SF_GENERIC` — read
   directly from `U8SHAPES.FLX` and `TYPEFLAG.DAT`. A 2-frame shape makes
   CANTRK's `frame = 0` test safe. It would **not** be safe on an animated
   candle: the base game's own `Item::candleAnim()`
   (`UNK files/UNK/METHOD.UNK:403-422`) skips frames 0, 4, 8 and 12, i.e. a
   16-frame candle is four facings each with an off-frame, and only one of
   those off-frames is 0. Pick a 2-frame candle or CANTRK misreads three
   facings out of four as lit. VERIFIED.

**Verdict on item 2: yes.** The recovered source supports the staging in
full except for the ankh geometry itself, which was never in the usecode to
begin with and is therefore a map-authoring job with a known constraint
(candles 2 and 6 lit).

---

## 3. PLNTST / TESTPLAN vs the poisoned garden

### The memoir, verbatim

Same source, VERIFIED:

> There was a woman who was the "wise woman" of one of the tribes. She wanted
> you to help fix this problem … she's the one who sends you to "wake up the
> gods" and climb to the top of the mountain. But.. before she does that.. she
> sends you to get a particular plant from her garden. When you walked in to
> the garden. When you entered the garden, the gates slammed behind you and
> the plants attacked. They were also very poisonous. You were poisoned.. on a
> timer… and only had so long to get the antidote (which.. unfortuantely..
> escapes me at the moment.) Come to find out.. she didn't trust you would
> actually help the people of the valley and so to make sure you will, she
> holds the antidote as a way to ensure you will finish what you start.

### What the 1994 source implements

Read in full: `LOST VALE/PLNTST.UNK` (68 lines, byte-identical to the
`UNK files/UNK/` copy), `LOST VALE/TESTPLAN.UNK` (325 lines, likewise
identical), and `UNK files/UNK/SHADES.UNK`.

`TESTPLAN.UNK` is the real scene and is `typeclass TypePoisonPlant`, not an
egg. Its header line 1 reads `// @@@ READY TO TRANSLATE F & G 8-11-94` — this
is late, near-final content, three weeks before cancellation. VERIFIED.

`TypePoisonPlant::use()`:

- The **Avatar acts on the plant** (`use`, i.e. double-click). The plant does
  not act on the Avatar. Explosion SFX, `setFrame(1)`, `setFrame(2)`,
  `plant.destroy()`.
- `Avatar.realDoAnim(AS_FALL_DOWN,0)`, `FadeToBlack()`,
  `Avatar.teleport(13055,30079,64, ...)` — the Avatar collapses and wakes in
  the south-west test grounds.
- The elder of **the other clan** teleports in and turns to face him: Atli if
  `thordisToldTest`, Thordis otherwise.
- Five `TypeMiniAirTitan` whirlwinds pop in sequence, each leaving a
  `TypeShortmushroom`.
- A ~10-line exchange in which the elder explains the test is poisonous,
  that "From the Ancient Ones the only antidote was", that the High Priestess
  can no longer reach them, and "afraid you are doomed I am". The Avatar is
  given the `TypeZealMark`; `haveMark = true`.
- `spawn poisonAvatar()`.

`TypePoisonPlant::poisonAvatar()` (lines 243-325) sets `avatarPoisoned` and
`firstPoisoned`, then loops: one of nine random illness barks, then
`Avatar.receiveHit(referent, nodir, 1, DMG_FULL)`, then every third hit
decrement Str and Dex by 1 **but only while both are above 10**, then
`wait(10000)`.

`PLNTST.UNK` is *not* the scene. It is a small egg
(`eggclass EggPlantTest`) that consumes the `TypeBushKey` passage stone from
the pack and blows away nearby `TypeShortmushroom` with whirlwind animation.
That is all it does. VERIFIED.

### Memoir vs source, item by item

| Memoir | 1994 source | Verdict |
|---|---|---|
| It is the wise woman's (Ezrekal's) garden | It is the clans' **Rite of Passage**, staged by Atli/Thordis. Ezrekal is not present and does not send you | **Contradicted** |
| Gates slam shut behind you | No door, gate or barrier manipulation anywhere in PLNTST or TESTPLAN | **Absent** |
| The plants attack | The Avatar `use()`s the plant. Nothing attacks. The five plants that appear afterwards are scenery | **Contradicted** |
| Poisoned on a timer, "only had so long" | `poisonAvatar()` is an unbounded drip: 1 damage per `wait(10000)`, Str/Dex -1 every third tick, **floored at 10**. No deadline, no death state, no timer variable | **Contradicted** |
| She holds the antidote as leverage | The dialogue says flatly there **is** no antidote — `"No antidote there is."` The cure is `avatarPoisoned = false` inside the SHADES set-scene (`SHADES.UNK:429`), granted by Ezrekal *after* the clans reconcile and the Shield is rejoined | **Different mechanism, same intent** |

That last row is the interesting one. The *coercion* the memoir remembers is
genuinely there — you cannot be cured until you have done the work — but it
is implemented structurally (the cure is downstream of the reconciliation)
rather than as a withheld vial. And Ezrekal's line after curing is a better
piece of writing than the memoir's version:

> `Ezrekal.bark("Sorry, I am. The poison, rid I can. Restore your lost health,`
> `only the gods can. To them could you go, if open, the temple was.")`

— she removes the poison but the Str/Dex the drip ate stays gone until the
gods are freed. VERIFIED at `SHADES.UNK:429-441`.

**INFERRED reading:** the memoir is describing an *earlier* design. Plot
v1.1 and v1.2 (see section 5) call this the "Test of Rutabaga", still owned by
the clans, and by the 1994-08-11 TESTPLAN the arcade elements (gates, hostile
plants, countdown) are gone and the encounter is a cutscene about mortality.
The attacking-garden version, if it ever existed in code, is not in the
snapshot.

### What our tree has, and the gap it leaves

`agents/usecode-compiler/src/lv-patched/PLNTST.UNK` merges the TESTPLAN scene
into `EggPlantTest::hatch()` so a map egg can fire it. Its header is unusually
good documentation and I have no argument with the merge. Two fidelity notes:

1. **The patched version drops the elders' dialogue entirely.** Lines 163-224
   of TESTPLAN — the whole "no antidote, you are doomed, take the Zealan Mark"
   exchange, the single most story-bearing part of quest step 8 — has no
   counterpart in the patch. The patch keeps the choreography and the flags
   and loses the scene. VERIFIED by reading both files.
2. **The cure is currently unreachable.** `shared/docs/wiring-data.md` bit
   1028: `avatarPoisoned` is written by EGGPLANTTEST (reachable),
   EGGSHADES and TYPEPOISONPLANT (**both orphans**). So the shipped build can
   poison the Avatar and has no wired path to clear it. Six classes read the
   flag (ATLI, EZREKAL, HRODNY, INGJALD, THORDIS, TYORVI), so the state is
   observable in dialogue — it just never ends. VERIFIED.

That second point is a quest-blocking gap, not a fidelity nicety, and it is
larger than anything else in this document.

---

## 4. The inverted-syntax clan

### The memoir says one tribe

VERIFIED, same source:

> I can't remember the name of the two "tribes" but I think they were based
> around the boys' names. One of the tribes, we (and … actually I'll admit
> it.. it was my idea.. ) decided to make them talk like Yoda. This seemed
> like SUCH a funny, good idea … in the beginning. After three months of
> writing the dialog.. Lisa gave up and said "Here.. YOU translate it…" so I
> ended up having to go through all the conversations for that tribe and
> making them all sound like Yoda.. OMG.. SUCH a bad idea!!!!!!

Note she also says she cannot remember the tribes' names. Section 7 of the
improvement plan repeats "one clan speaking in inverted syntax" from this
passage. I tested it.

### Measurement

I measured inversion density directly on the recovered source. Method: pull
every double-quoted string literal, keep only the segment before the first
`\f` (French) or `\g` (German) marker so localised text cannot skew the count,
count sentence terminators as the denominator, and count clauses **ending**
in subject+auxiliary — `<pronoun> <aux> [not] <terminator>` — which is the
structural fingerprint of the fronted word order ("Sorry I am.", "Have it I do
not.", "The Elder of Clan Gunnar I am."). A secondary "nounal" counter catches
noun subjects ("Stolen the shield was.").

The control group is the base-game Pagan NPC conversations that sit in the
same snapshot under `U8/` — ordinary English by definition, so their density
is the false-positive floor.

| File | Clan / role | Sentences | Inversions/100 |
|---|---|---|---|
| THORDIS.UNK | Hoskuld, elder | 773 | **42.3** |
| SHADES.UNK | both clans, set-scene | 178 | **40.4** |
| HRODNY.UNK | **Gunnar**, inventor | 466 | **38.2** |
| INGYALD.UNK | **Gunnar**, brewer | 295 | **36.9** |
| ATLI.UNK | **Gunnar**, elder | 795 | **32.5** |
| TESTPLAN.UNK | both elders | 53 | **32.1** |
| TYORVI.UNK | Hoskuld, veteran | 684 | **31.7** |
| RAGNAR.UNK | Hoskuld, hunter | 322 | **30.1** |
| EZREKAL.UNK (LOST VALE) | priestess | 1165 | **23.3** |
| EZREKAL.UNK (U8/, earlier draft) | priestess | 652 | 12.9 |
| ZCHILD.UNK | Zealan child | 44 | 11.4 |
| TJORVI.UNK (early draft of TYORVI) | Hoskuld | 188 | 10.1 |
| ARAMINA.UNK (base NPC, LV snapshot) | — | 343 | 2.0 |
| **control: 13 base-game U8 conversations** | — | **3923** | **2.3** |
| **all LV Zealan dialogue** | — | **8968** | **27.3** |

Reproduce: the analyser is small and self-contained; the method is fully
described above and in the docstring of the throwaway script. VERIFIED —
every row is a count over the read-only 1994 files.

### Findings

**F1. It is not one clan. It is both, plus the priestess.** Clan Gunnar
(Atli 32.5, Hrodny 38.2, Ingyald 36.9) and Clan Hoskuld (Thordis 42.3,
Tyorvi 31.7, Ragnar 30.1) are indistinguishable on this measure. The memoir's
"one of the tribes" is a 15-year-old recollection from someone who says in the
same sentence that she cannot remember the tribes' names. **The improvement
plan's framing of item 4 is wrong on the facts**, and so is any restoration
decision built on it.

**F2. The signal is not marginal.** Control floor 2.3 per 100 sentences,
Zealan dialogue 27.3 — a 12x separation, over ~9,000 sentences. There is no
plausible reading in which this is measurement noise.

**F3. The base-game NPCs the LV team edited were left alone.**
`UNK files/UNK/ARAMINA.UNK` scores 2.0, identical to the `U8/` copy of the
same file. The convention was applied to Zealans and to nobody else — which is
the correct instinct, and matches `agents/npc-dialogue/docs/mythran-analysis.md`
holding Mythran to standard English.

**F4. The snapshot preserves the conversion in progress.** Two files exist in
both an earlier and a later revision, and in both cases the later revision is
markedly more inverted: EZREKAL 12.9 → 23.3, and TJORVI 10.1 → TYORVI 31.3.
This is the memoir's "I ended up having to go through all the conversations"
visible as a diff. It also means the drafts are not stylistically neutral
fallbacks — they are half-converted.

**F5. It is load-bearing for localisation.** The recovered source carries
French (`\f`) and German (`\g`) translations inline, and the translators
rendered the inversion into their own languages
(`LOST VALE/EZREKAL.UNK:1581`, `ATLI.UNK:1588`). Dropping it in English would
desynchronise our English from 1994 translated lines we did not write and
cannot re-translate.

### Recommendation

**Keep it. Do not touch it. Do not extend the recommendation into new prose
without a style guide check.** Reasoning, in order of weight:

1. **Dropping it is not an edit, it is a rewrite.** ~2,450 inverted clauses
   across ~9,000 sentences in 10 dialogue files. Every one is hand-authored
   1994 text.
   Any automated de-inversion would produce worse English than either the
   original or a human pass, and a human pass over 60K lines is not a thing
   this project is going to do.
2. **The regret is about the labour, not the result.** Read her sentence
   again: the complaint is that Lisa gave up and Sheri had to convert
   everything herself after three months. "SUCH a bad idea" is about having
   volunteered for three months of manual translation. That cost is already
   paid — the text exists.
3. **It is the only surviving marker of Zealan otherness.** The Zealans have
   no unique art (everything is a base-game placeholder), no unique music, and
   no unique UI. The syntax is the entire cultural signal.
4. **Removing it would break the 1994 French and German lines** (F5).
5. **The one thing the memoir gets right is worth honouring anyway.** If a
   future decision wants to soften it, the *evidence-supported* softening is
   not "drop it from one clan" — the clans are identical — but "let the child
   and the drafts stay lighter", which the source already does (ZCHILD 11.4).

This is a written recommendation only. **No dialogue was changed.** If it is
adopted, it wants a DD entry recording that the plan's "one clan" premise was
tested and found false, so nobody re-opens it from the memoir alone.

---

## 5. Proper-noun spellings

### Method

Three independent evidence layers, each searched exhaustively:

1. **The shipped base game.** Binary string search over
   `shared/data/u8-install/USECODE/EUSECODE.FLX` (Origin's own 1994 build).
   This is the highest authority available for anything that predates the
   expansion.
2. **The recovered 1994 LV snapshot.** Token counts over all 67 files in
   `shared/data/lv-usecode/`.
3. **The GOG design-doc bundle.** All 13 PDFs from
   `gog/ultima_8_lost_vale_design_documents.zip` extracted with
   `pdftotext -layout`. These are scans **with an OCR text layer**; OCR is
   reliable enough to locate a name but **not** to adjudicate a one-letter
   difference, so every spelling below that rests only on OCR is marked as
   such.
4. **The Ultima Codex gallery scans** at
   `gallery.ultimacodex.com/the-lost-vale-plot-documents/` — 38 pages,
   published 2014-03-21, sourced from Bill Randolph via Joe Garrity's Origin
   Museum. A parallel researcher read all 38 **visually at magnification**,
   which is the only way to settle a one-letter difference on a scan. Where
   this document cites a design-doc spelling as settled rather than located,
   that is the basis. This layer overlaps the GOG bundle but is not identical
   to it — the gallery includes pages the bundle does not, and the gallery's
   copy of the annotated Plot Synopsis is missing items 14-16.

Plus a tree-wide count of what we ourselves currently write.

### The gods: base game settles it

The single most useful thing found in this whole exercise. `EUSECODE.FLX`
offset `0x36cbc`, VERIFIED verbatim:

> Even older texts indicate that the Zealans initially believed in not three,
> but six such deities! In addition to the rulers of love, hate, and apathy,
> **Felicitar** controlled joy, **Doloras** ruled grief, and **Timyra** was the
> patron of fear. Though anthropomorphic in nature, some of them had
> animalistic features, such as Doloras and his torax head.

Counts in that same binary: `Felicitar` 1, `Felicitas` **0**, `Doloras` 2,
`Timyra` 1, `Amoras` 4, `Apathas` 3, `Odion` 5, `Zealan` 71.

So the three Lost Vale gods are the *second* triad of the Zealan pantheon
already established in shipped Pagan lore, the first being Amoras / Odion /
Apathas. Two consequences worth recording:

- **Doloras is male** ("his torax head"). VERIFIED. Anything we write must
  agree.
- The base game already ships item shapes literally named `Amoras`
  ("female statue") and `Odion` ("male statue") — VERIFIED at offsets
  `0x968d` and `0xc62c9`. That is directly relevant to the god-statue entry in
  the art placeholder backlog.

The existing decision in `agents/npc-dialogue/docs/naming-decisions.md` §4
already chose Felicitar, but on the strength of "base game wiki". It is now
verified against the base game *binary*, and the note there hedging that
"Felicitas ... may be the original spelling" should be closed: the shipped
game says Felicitar and never says Felicitas.

The recovered LV snapshot is genuinely split — `Felicitar` 3, `Felicitas` 5 —
and the split is by *scene*, not by author error: EZREKAL's Shield-fake
speech uses Felicitar (`LOST VALE/EZREKAL.UNK:1573`, with the German line at
1581 also reading Felicitar), while the Monster Skull message uses Felicitas
(`MONSKUL.UNK:26`, `EZREKAL.UNK:2187`, whose German at 2211 also reads
Felicitas). **Both passages were translated as written**, so this is not a
slip that the translator caught — it is two scenes that disagreed and stayed
disagreeing. Felicitas actually leads on raw count inside the LV snapshot.
The tiebreak has to come from outside, and it does: the shipped game says
Felicitar and never says Felicitas. **Felicitar.** This is a decision, not a
typo correction, and should be recorded as one.

**The gods were never named in the design documents at all.** As late as the
Art List v2.5 (1994-06-28) the assets are listed as "Zealan God 1 / 2 / 3",
and every plot revision calls them "Love, Hate, and Apathy". The 1994-05-10
Art Needs email carries a handwritten margin note beside the god list reading
"(Wrong names, but yes, three Zealan gods are needed)". Felicitar / Doloras /
Timyra were pulled in from the base game's own book text at the *code* stage,
which is exactly why the base game is the right authority for them.
(Gallery scans, read at magnification; **VERIFIED** by the parallel
researcher, and consistent with my own zero-hit grep over the GOG bundle.)

### The priestess: Ezrekal, decisively

| Source | Ezrekal | Ezrakel | Other |
|---|---|---|---|
| Recovered 1994 usecode (67 files) | **294** | **0** | `Ezrkal` 2 (typo) |
| Character List 1.0, 05/17/94 (Sheri's own doc) | yes, l.17 | — | — |
| Plot v1.1 | 10 | 1 (step 17 only) | — |
| Plot v1.2 (05-09-94) | 10 | 1 (step 17 only) | — |
| Resource Schedules (all revisions) | many | — | — |
| Walk Through (early draft) | 3 | 2 (steps XI, XII) | — |
| "Plot Synopsis with Notes" (external reviewer's annotated copy) | 0 | **5-8** | — |
| Art List v2.5 (06-28-94) | yes | — | — |
| "Elean Speak Exerpt" — actual 1994 dialogue | yes (`bark("Ezrekal my name is. …")`) | — | — |
| Art Needs email, Brian Martin, 05/10/94 | — | — | **`Ezrekel`** |
| Walk Through, priestess's slot (circled) | — | — | **`Joan`** (pre-naming placeholder) |

The usecode row is exact-byte and is the row that matters. The design-doc
rows were read at magnification off the gallery scans, so the one-letter
distinctions there are settled, not OCR guesses.

The pattern is diagnostic. `Ezrakel` clusters in exactly two places: the
paragraph numbered 17, which appears near-identically in the Walk Through and
in both plot revisions (one transposition typo in one sentence, copy-pasted
forward through three documents), and the externally-annotated synopsis, which
uses it *uniformly* — the annotating writer normalised to the typo. That
document is the sole ancestor of the modern wiki spelling: `Ezrakel` on
`wiki.ultimacodex.com` traces back through the 2014 gallery to that one page.
Sheri's own documents never use it.

**Authoritative: `Ezrekal`.** Note that our own tree currently disagrees with
itself — see the table below.

### The inline translations are a spell-check oracle

A pattern worth naming, because it settles three separate questions at once.
The recovered source carries French (`\f`) and German (`\g`) translations
**inline in the same string literal** as the English. Where a proper noun is
misspelt on one side, the other side is usually right — the translator was
working from the corpus, not from the line in front of them. Three cases,
all VERIFIED:

| File:line | English | Translation on the adjacent line | Which is wrong |
|---|---|---|---|
| `UNK files/UNK/EZREKAL.UNK:257` | `Ezrekal` ✓ | `\g … Ezrkal` | the **German** |
| `LOST VALE/EZREKAL.UNK:1256` (and `UNK files/…:1237`) | `Tjorvi` | `:1259` `\g … Tyorvi` ✓ | the **English** |
| `LOST VALE/EZREKAL.UNK:1572` | `Apathos` | `:1580` `\g … Apathas` ✓ | the **English** |

In each case the singleton loses to the corpus: `Ezrekal` 294, `Tyorvi` ~190,
`Apathas` 3 in the LV source and 3 in the shipped base game against `Apathos`
2. `Apathos` is the same class of error as `Felicitas` and is worth fixing on
the same terms.

The Felicitar/Felicitas pair is the exception that proves the rule: **both**
sides of **both** passages agree with themselves, which is why it is a design
inconsistency rather than a typo.

### Everything else

| Name | Authoritative | Evidence | Notes |
|---|---|---|---|
| **Felicitar** | `Felicitar` | Base game `EUSECODE.FLX` @0x36cbc, VERIFIED | LV snapshot has Felicitas ×5; base game has it ×0 |
| **Doloras** | `Doloras` | Base game @0x36cd6, VERIFIED | Male |
| **Timyra** | `Timyra` | Base game @0x36cef, VERIFIED | No variants found anywhere |
| **Ezrekal** | `Ezrekal` | LV usecode 294:0, VERIFIED | `Ezrakel` is a reviewer's normalisation, not the team's |
| **Galjeron** | `Galjeron` | Walk Through, Plot v1.1, Plot v1.2, Plot Synopsis, Resource Schedules — consistent, VERIFIED | **Zero occurrences in the recovered usecode.** He was designed and scheduled but never written. Everything we have of him is our own new content. One-off variant `Gulgeron` in the 05/10/94 Art Needs email ("Gulgeron's body (already have him, (dead body))") — a different author, VERIFIED at magnification |
| **Tinytar** | code `TypeTinytar`; prose **TinyTar** | `LOST VALE/FREE.UNK:1331` `Avatar.setType(TypeTinytar)`, VERIFIED. Memoir prose: "you had to use the TinyTar spell", VERIFIED | Genuinely unsettled — there is no canonical form. Only 1 occurrence in the whole 1994 corpus, and the *earlier* revision of that same line reads `TypeTinyAvatar` (`UNK files/UNK/FREE.UNK:1331`, `CHANGTAR.UNK:25` — VERIFIED). So "tar" is a clipped "[Ava]tar" and `TypeTinytar` is the later, final name. The GameBanshee interview hyphenates "Tiny-tar"; the blog writes "TinyTar" |
| **Tyorvi** | `Tyorvi` | Resource Schedules l.564/629, VERIFIED; usecode uses Tyorvi throughout (~190 vs 19) | `Tjorvi` is the abandoned early draft's filename **and** a stray typo inside dialogue text whose adjacent German line reads Tyorvi |
| **Zealan** | `Zealan` | Base game ×71, VERIFIED; LV usecode Zealan(s) 220 vs Zelean(s) 12 | `Zelean` is a typo cluster confined to Ezrekal's introduction bark, and the 1994 editor struck it through on the Elean Speak excerpt |
| **Apathas** | `Apathas` | Base game ×3, VERIFIED; LV usecode `Apathas` 3 vs `Apathos` 2 | Not in the original brief, found on the way. `LOST VALE/EZREKAL.UNK:1572` writes `Apathos` in English with `Apathas` in the German at 1580. Same class of error as `Felicitas`, and unlike `Felicitas` it is unambiguously a slip |
| **Clan Gunnar / Clan Hoskuld** | singular `Clan Gunnar`; plural **`Gunnars`** | `ATLI.UNK:33` `"Atli, Elder of Clan Gunnar"`, VERIFIED | The 1994 text repeatedly writes the *plural* as `Gunnar's`; see below. One fossil of the earlier draft survives: `TJORVI.UNK:366` has Thordis as "the Eldar of **Clan Snori**" |
| **"Eleans"** | **not a clan name** | Zero occurrences as a tribe anywhere in the 1994 source, VERIFIED | Correction to the backlog item's premise. "Elean" survives only in the gallery *filename* `LostVale-EleanSpeakExerpt.jpg` and in this project's own coinage "Elean Speak" for the inverted dialect. The tribes are Gunnar and Hoskuld; the people are Zealans |
| **Snori / Hoskuld** | as spelt | Plot v1.2 §11, Plot Synopsis §11, VERIFIED | The boys were renamed twice. Plot v1.1 §11 calls them **Draesh and Ikanikar**; v1.2 §11 calls them Snori and Hoskuld but still accuses "Ikanikar" in one sentence — an incomplete find-and-replace. The Art List v2.5 and Art Needs email name the two shades **Flossie and Snori**, a third pairing. The annotated synopsis adds the reviewer's note: *"These names sound Norse, and seem incongruous with the rest of the Pagan/Zealan names."* |

### Joke placeholders, all replaced before the snapshot

Recorded so nobody mistakes one for a lost name. Every one of these appears in
the 1994 plot documents and has **zero** occurrences in the recovered usecode:
`Magic Frisbee` (→ Shield of the Ancients, changed between Plot v1.1 and
v1.2), `Cliffs of Insanity` (→ Cloud Cliffs), `Sacred Smallish Unusual-Colored
Rock` (→ Sacred Circle), `Shrine of the Wheaties`, `Test of Rutabaga` (→ Rite
of Passage), `Damn Puzzle`, and `Joan` in the priestess's slot. VERIFIED both
ways.

### Where our tree is inconsistent with itself

Counts over the whole repo excluding `shared/data/`, `gog/`, `scummvm-lv/`,
`shared/build/` and `docs/archive/`. VERIFIED.

| Token | Count | Files | Assessment |
|---|---|---|---|
| `Ezrekal` | 270 | 51 | correct |
| `Ezrakel` | **8** | `docs/research/2026-07-19-ecosystem-and-history.md`, `docs/reviews/2026-07-19-improvement-plan.md`, `shared/corpus/plot-documents/characters.yaml`, `shared/corpus/plot-documents/codex-wiki-summary.md` | **wrong** — and two of the four are the review documents that drive current work |
| `Ezrekel` | **2** | `agents/usecode-disasm/MEMORY.md`, `shared/corpus/plot-documents/characters.yaml` | **wrong**. `characters.yaml` contains *both* wrong variants |
| `Ezrkal` | **1** | `agents/usecode-compiler/src/lv-patched/EZREKAL.UNK:361` | **wrong, and it ships.** Inside the German half of a bark: `"Well met, Ezrekal. \g Ich hoffe, es geht Euch gut, Ezrkal."` A one-character fix in our own highest-precedence tier |
| `Felicitar` | 46 | 21 | correct |
| `Felicitas` | 15 | 5, incl. `lv-patched/EZREKAL.UNK:2293,2317` | Faithful to the 1994 line, which the base game contradicts. A deliberate call is owed, not an accident |
| `Tiny Tar` | 48 | 25 | House style, but matches no source. Memoir says `TinyTar`, code says `Tinytar` |
| `Tiny-tar` | 9 | 7 | from the GameBanshee interview |
| `TinyTar` | 5 | 5 | matches the blog |
| `Tinytar` | 2 | `u8c_symbols.py` | matches the code identifier — correct there |
| `Tjorvi` | 28 | 12, incl. `lv-patched/EZREKAL.UNK:1362` | Mostly legitimate filename references. **Line 1362 is not**: `bark("Ah, not met Tjorvi have you? ...")` with the German line 1365 immediately below reading `Tyorvi`. A live in-dialogue typo in our shipping tier |
| `Galjeron` | 162 | 42 | consistent, and consistent with the design docs |

Four of these are one- or two-character fixes in `lv-patched/EZREKAL.UNK` that
would ship in the next build: `Ezrkal`→`Ezrekal` (line 361, German half),
`Tjorvi`→`Tyorvi` (line 1362, English half), `Apathos`→`Apathas` (line 1678,
English half of the shield-symbols passage), and `Felicitas`→`Felicitar`
(lines 2293, 2317) **if** the base-game spelling is adopted. The first three are
unambiguous slips — in each case the translation on the adjacent line already
has it right. The fourth is a decision. The `Ezrakel`/`Ezrekel` occurrences
are documentation-only and touch no shipped byte.

One more 1994 orthography issue, noted for completeness because it is
pervasive: the plural of the clan is written `Gunnar's` throughout —
`THORDIS.UNK` ×6, `TESTPLAN.UNK:201`, `ATLI.UNK:1053`, and (as the doubled
`Gunnar's's`) `RAGNAR.UNK:435,477`. `lv-patched/RAGNAR.UNK` already fixed
Ragnar's copies; the others are untouched. `TODO.md:79` lists this as a known
minor item and that assessment stands.

### What the design docs do NOT contain

A negative result worth recording so nobody re-searches: **the GOG design-doc
bundle contains no mention of the gods by name, the obelisk, the candlesticks,
an ankh, the magnetic seal, or TinyTar.** I grepped all 13 extracted texts for
`felicit|dolor|timyr|tymir|tinytar|tiny.?tar|ankh|candl|obelisk|monolith|magnet`
and got zero hits. Those documents are April-to-May 1994 planning material;
the Cloud City puzzle and the named pantheon are later, and survive only in
the usecode and the memoir. VERIFIED (negative), subject to the OCR caveat —
a scanned handwritten margin note could hide from a text grep.

---

## 6. Contradictions found, stated plainly

Collected here so they are not buried in the sections above.

1. **The improvement plan's item 4 premise is false.** "One clan speaking in
   inverted syntax" does not survive measurement: both clans and the priestess
   use it at 23-42 inversions per 100 sentences against a 2.3 control floor
   (section 4). The plan inherited the framing from the memoir, and the memoir
   is a 2009 recollection whose author says in the same paragraph that she
   cannot remember the tribes' names.

2. **`docs/research/2026-07-19-ecosystem-and-history.md` uses `Ezrakel`**
   (8 occurrences across it and the improvement plan). The recovered 1994
   source uses `Ezrekal` 294 times and `Ezrakel` zero times. The earlier
   research doc marked its proper nouns "medium confidence" and was right to;
   they can now be upgraded and corrected.

3. **The same research doc's poisoned-garden bullet is accurate as a
   *report of the memoir* and wrong as a *description of the build*.** Gates
   slamming, attacking plants and a countdown are in the memoir and in no line
   of the recovered source (section 3). The doc does attribute the bullet to
   the memoir, so this is a framing risk rather than an error — but the plan
   then asks us to "cross-check PLNTST against her description", and the
   answer is that they describe different designs.

4. **`build_map_17.py:229` sets the MAGNET egg quality to 3.** The convention
   is `class_id - 0x47F`, so EGGMAGNET (1432) needs 281. Quality 3 addresses
   base class 1154. Live bug (section 2).

5. **MAGNET's `pop()` target and Map 17's obelisk are in different places.**
   `(15615, 19839, 120)` versus `(4096, 7168)`. If the egg is ever wired
   without fixing one of the two, the player's entire inventory relocates into
   unbuilt space (section 2).

6. **`avatarPoisoned` has a reachable writer and no reachable clearer.**
   EGGPLANTTEST sets it; the only two classes that clear it, EGGSHADES and
   TYPEPOISONPLANT, are both orphans in `shared/docs/wiring-data.md`. Quest
   step 8 can be entered and not left (section 3).

7. **`lv-patched/PLNTST.UNK` silently drops the Passage Test dialogue.**
   TESTPLAN lines 163-224 — the elders' "no antidote, you are doomed, take the
   Zealan Mark" exchange — have no counterpart in the patch. The patch header
   documents every other deviation it makes; this one is not mentioned
   (section 3).

8. **`naming-decisions.md` §4's hedge on Felicitas can be closed.** It says
   the Monster Skull's "Felicitas" "may be the original spelling". The shipped
   base game contains `Felicitar` and does not contain `Felicitas` at all
   (section 5).

9. **`shared/corpus/plot-documents/characters.yaml` contains two different
   wrong spellings of the priestess** (`Ezrakel` and `Ezrekel`) in one file
   (section 5).

10. **The backlog item's "Eleans" is not a clan.** Item 5 of the plan lists
    the tribes among the names to lock. There is no Elean tribe: the word
    exists only in the 1994 gallery scan's *filename* and in this project's
    own coined term "Elean Speak". The clans are Gunnar and Hoskuld
    (section 5).

11. **`enterConvo()` almost certainly freezes every NPC on the map, not one.**
    Our codegen calls intrinsic `0x9A`, which ScummVM leaves unimplemented and
    therefore returns 0, and 0 is the wildcard object id in
    `Kernel::killProcesses`. `CLAUDE.md`'s "Known Limitations" entry for
    `enterConvo()` describes a different and smaller gap, so this is not
    covered by it (section 1). Needs a play test to confirm the observable
    effect; every step of the chain is verified in source.

12. **Opcode `0x79` is the one place the "ScummVM wins" rule must not be
    applied mechanically.** ScummVM's handler has no `GAME_IS_U8` guard and
    would read a U8 class terminator as a global-address push; the retail data
    (516 of 518 non-empty classes end with `0x79`) says Pentagram is right for
    U8. Our tools already do the right thing; this is a note against a future
    "correction" (section 1).

Nothing here contradicts `CLAUDE.md` or `PLAN.md` on any point other than
item 11's scoping of the `enterConvo()` limitation.

---

## 7. Not answerable with available evidence

Recorded so they are not re-litigated:

- **The ankh geometry.** No surviving artifact encodes candlestick positions.
  The usecode tracks identity and lit-state only; the Cloud City map is lost;
  the 22-screenshot set has no candle room. Any ankh we draw is our invention
  constrained to "candles 2 and 6 burn".
- **Whether CANTRK was finished.** The two revisions disagree about candle
  six and the surviving solution lights only two of six. Both "the room had
  more candlesticks than the six tracked" and "this class was mid-edit" fit
  the evidence; nothing distinguishes them.
- **Whether an attacking-garden version of the poison scene was ever coded.**
  The memoir describes one. No revision in the snapshot resembles it, and the
  earliest plot revisions already describe the sedate clan-administered
  version. Absence of evidence, in a snapshot we know is partial.
