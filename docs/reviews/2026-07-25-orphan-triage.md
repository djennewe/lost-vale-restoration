# Orphan triage, 2026-07-25

Follow-up to the H3 fix, which stopped the reachability audit counting
self-edges as inbound references and thereby surfaced seven more flagged
classes. This is the triage of everything the audit now reports.

**Headline: the backlog is real but already known.** `shared/docs/wiring.md`
(2026-07-03) documents it and sets the wiring order. What this triage adds is
a per-class verdict backed by the engine's actual dispatch limits — and it
found that **two of that document's mechanism assignments cannot work as
written**, one of them for the next item in its own wiring order.

---

## 1. What can reach a class at all

Four mechanisms, all engine-verified (`shared/docs/wiring.md`), with the
ranges each can address:

| Mechanism | Rule | Class ids it can reach |
|---|---|---|
| Item shape dispatch | item of shape N runs class N | = the shape id, so ≤ 2047 and only where a class already occupies that slot |
| LV npcNum patch | `class = npcNum + 1024`, non-egg items | **1025-1279** — `npcNum` is a single byte in the 16-byte map record |
| Actor promotion (map.cpp) | `npcNum` 100-116 only, deliberately narrow so base-game npcNum bytes are not misread | **1124-1140** |
| UnkEgg quality | shape 73, `class = quality + 0x47F` | quality is a 16-bit word, so effectively unrestricted |
| usecode call/spawn | 0x11 / 0x57 / 0x58 from a class that is itself reachable | any |

The consequence that drives everything below: **the manifest's class-id
cursor is at 1456 and hands out ids from 1431 up. Every one of those is
outside both npcNum windows.** Only the UnkEgg recipe or a usecode call can
reach them. That is fine for event eggs — it is the design — and impossible
for anything that needs to be an Actor or an interactive item.

## 2. Census

33 pinned LV classes: 26 in `classes`, 7 in `npc_classes`.

| Status | Count | |
|---|---|---|
| Reachable | 13 | 7 NPCs (npcNum 105-116), TYPERECEPTACLE (npcNum 120 ×4, Map 11), EGGPLANTTEST / EGGSPIKE / EGGLBSCENE (UnkEgg q=283/302/304), TYPELORDBRITISH + TYPEMYTHRANLVDLG + LVFREE (called by wired usecode) |
| Shipped but unreachable | 18 | see below |
| Stale manifest pin | 1 | EGGCOLUMNPUZZLE |
| Wired since wiring.md | — | LORDBRIT (step 1), COLPUZZL (3-4), PLNTST (8) |

## 3. Verdicts

### 3a. Stale pin — no defect, bookkeeping only (1)

**EGGCOLUMNPUZZLE (0x05A9)** is pinned but **not in the FLX**: no source
declares it. `COLPUZZL.UNK:24` calls it "the earlier EggColumnPuzzle sketch",
superseded by `TypeReceptacle`, which is wired and verified (npcNum 120, four
receptacles on Map 11). The audit had been reporting it as an orphan forever
because the report iterates manifest ids rather than FLX contents.

Fixed in this pass: `u8_flag_graph.py` now separates "not built (stale pin)"
from "shipped but unreachable". The pin itself should stay — the manifest is
append-only — but wants a `retired` marker, the way retired flag bits already
work.

### 3b. Event eggs — known backlog, proven recipe, map-side work (6)

| Class | Source | Needs UnkEgg quality | Quest |
|---|---|---|---|
| EGGCANDLETRICK | CANTRK.UNK (1994) | 280 | — |
| EGGMAGNET | MAGNET.UNK (1994) | 281 | step 12, the obelisk/ankh puzzle |
| EGGSHADES | SHADES.UNK (1994) | 294 | the ceremony shades |
| EGGAOCEREMONY | AOSCENE.UNK (lv-new) | 296 | steps 15/17 |
| EGGCLOUDCLIFFS | CLCLIMB.UNK (lv-new) | 297 | step 13 |
| EGGENDGAME | ENDGAME.UNK (lv-new) | 299 | **step 18, the endgame** |

All six are compiled and shipped (555-10,587 bytes each). The fix is entirely
map-side and the recipe is proven in-game: place a shape-73 item with
`quality = classid − 0x47F`, hatch range packed in the npcNum nibbles
(verified 2026-07-03 with EGGSPIKE, class 1453 / quality 302). This is exactly
the backlog `wiring.md` describes; no mechanism problem, just unplaced eggs.

### 3c. SIGRID — the wiring doc assigns a mechanism that cannot work (1)

`wiring.md:180` says: *"SIGRID (11-12, npcnum mechanism, needs Map 13
placement)"*. **SIGRID is pinned at class 1452.** npcNum dispatch tops out at
1279, and Actor promotion — which an NPC needs in order to exist as an actor
at all — is limited to npcNum 100-116, i.e. classes 1124-1140. She cannot be
reached by the mechanism assigned to her, at any npcNum value.

This is not hypothetical: SIGRID.UNK compiles to 2,402 bytes of dialogue,
`test_new_dialogue` covers it, and she is the **next item in the documented
wiring order**. As built, she is a fully written NPC nobody can talk to.

Two ways out, both needing a decision:

1. **New pin in the Actor window.** Free npcNum slots today: 100-104, 108-111,
   114 → classes 1124-1128, 1132-1135, 1138. The manifest is append-only and
   says "never renumber", so the clean form is: retire the 1452 pin, add a new
   one in range. Nothing has shipped to a player save, so the risk is
   procedural rather than real.
2. **Mythran-style wrapper.** A small class inside the reachable window whose
   `use()` calls 1452. Proven pattern (MYTHRAN → TYPEMYTHRANLVDLG), renumbers
   nothing, costs one extra class and one indirection.

### 3d. Item classes — the other unworkable assignment (11)

`wiring.md:183` calls these *"shape-dispatch candidates (class = shape id
needs TYPE_SHAPES-verified placements)"*. Shape dispatch means the class id
**is** the shape id. These are pinned at 1431-1446. So as written this cannot
work either: it would require re-pinning each class onto its shape's id, which
means replacing the base game's class for that shape.

| Class | Source | Note |
|---|---|---|
| TYPEPOISONPLANT | TESTPLAN.UNK | likely superseded — `lv-patched/PLNTST.UNK` merged the Passage Test scene into the egg hatch, and EGGPLANTTEST *is* wired |
| TYPEAOFRIZBEE | ZEALSHLD.UNK | the Zealan shield |
| TYPENSGOLDPLAQUE | PLAQUENS.UNK | overlaps the "gold plaques 158→599/614" art fix |
| TYPEPEDESTALS | EAPUZL.UNK | |
| TYPEPOTION | POTION.UNK | |
| TYPEMONSKUL, TYPEZEALANCHILD1 | MONSKUL.UNK, ZCHILD.UNK | |
| TYPEABACUS, TYPEBEDROLL, TYPEBULLWHIP, TYPEFEDORA | flavour items | |

Three real options, and the choice differs per item:

- **(i) Replace the base class at the item's shape id.** Architecturally the
  U8-native answer, and the pattern already used for the 11 modified base NPCs
  and MYTHRAN. Cost: our behaviour applies to *every* item of that shape,
  including base-game ones.
- **(ii) Re-pin into the npcNum window (≤1279) and set `npcNum` on each placed
  item.** Proven — this is exactly what TYPERECEPTACLE does. Scoped per
  placement rather than per shape, and needs no base-class replacement.
- **(iii) Leave inert.** Honest for the flavour items; they carry no quest
  weight.

Recommendation: (ii) for the quest-relevant five, (iii) for the flavour six,
and confirm TYPEPOISONPLANT is genuinely superseded before spending anything
on it.

## 4. What changed in this pass

- `u8_flag_graph.py` distinguishes stale pins from unreachable shipped
  classes, in both the report table and the stdout summary.
- `shared/docs/wiring.md` corrected: the SIGRID and item-class mechanism
  assignments now state the id-range constraint that makes them unworkable as
  originally written, with the options above.
- No class was wired in this pass. Wiring the six event eggs is map work with
  quest-design consequences, and both remaining mechanism questions need a
  decision, not a guess.

## 5. Suggested order

1. **SIGRID** — decide the mechanism, then wire. She is next in the documented
   order and blocks quest steps 11-12.
2. **EGGENDGAME** — step 18 cannot fire at all today.
3. The other four event eggs, in quest order: CLCLIMB (13), AOSCENE (15/17),
   MAGNET (12), SHADES, CANDLETRICK.
4. Item classes, opportunistically per area, per the decision in 3d.

---

## 6. Decisions taken, 2026-07-26

All eight open points decided. Recorded here so they are not re-litigated.

| # | Decision | Status |
|---|---|---|
| A | Poison off now, place the cure trigger once the ceremony is wired | **done** (poison disabled) |
| B | Give Sigrid a reachable class id | **done** (class 1126, npcNum 102) |
| C | Remove the obelisk trigger now, wire the magnet puzzle as its own work | **done** (trigger removed) |
| D | Wire the item classes via npcNum-per-placement, keep the joke items | **done** (7 wired, 2 deferred, 2 rejected) |
| E | Standardise new art on 859+ | **done** (no revisit needed) |
| F | Hold the statue out of the canonical build until seen in-game | **done** (nothing recorded) |
| G | Keep the inverted syntax | **done** (recorded in speech-patterns.md) |
| H | Move the dropped elder dialogue to Atli | **done** (lv-patched/ATLI.UNK) |

### B, as implemented

Sigrid was pinned at class 1452, which no dispatch can reach. She now
compiles to **class 1126**, reached by **npcNum 102**.

That slot was not an arbitrary free number. `build_map_10.py` already placed
npcNum 102, already commented it "Female Hunter, edge of village facing
outward", already sat it in the Hoskuld cluster with the Male Farmer (103)
and the Child (104) beside it. Sigrid's character sheet is "Female Hunter,
Clan Hoskuld", married to the Male Farmer, one son. The map had modelled her
family from the start; only the class id was in the wrong window, so the
villager stood there mute.

The old pin is recorded in a new `retired_classes` group rather than deleted.
The allocation cursor only counts up (next_free 1456), so 1452 can never be
handed out again. `EGGCOLUMNPUZZLE` was retired the same way.

### E, answered

No revisit needed. Shape slots 859 to 2047 are one contiguous free run of
1,189 slots, with nothing occupied above 858. The older audit's 1500-1700
band is a subset of that same run, not a competing resource.

### H, as implemented

The ~30 lines live in `agents/usecode-compiler/src/lv-patched/ATLI.UNK`, in
`Atli::use()` immediately after `enterConvo()`, before the ask list is built.
They are **Atli's own lines**: `TESTPLAN.UNK` branches on `thordisToldTest`
and, on that branch, teleports *Atli* in to (12927,29823,64) and gives him
this speech. Restoring them to him puts nothing in a mouth it did not come
from. All nine spoken strings are carried over verbatim — verified identical
to `TESTPLAN.UNK:165-190` after the lexer's own normalization — and no
connecting or bridging line was written.

It plays as a scene rather than an ask-list topic, because that is what it
is: Atli's lines alternate with *scripted* Avatar lines ("No!", "No
antidote?!", "This can not be!") that are authored, not chosen. It fired
automatically in 1994, and it carries the only pointer to quest step 9, so a
topic a player can simply never pick would be both less faithful and less
safe.

Guard: `haveMark and thordisToldTest and not endOfPlantScene`.

- **`haveMark`**, deliberately not `avatarPoisoned`. Decision A left
  `avatarPoisoned` with no writer anywhere in the build, so a branch keyed on
  it would be born dead — which is also why Atli's *existing* poison thread
  (line 172) is currently unreachable. `haveMark` is set by
  `lv-patched/PLNTST.UNK:186` and cleared by nothing in the corpus, so the
  block works with the poison off and stays correct when the re-enable pair
  turns it back on. `firstPoisoned` was rejected for the opposite reason: a
  restored `poisonAvatar()` tick process will want it for its own first-bark
  latch.
- **`endOfPlantScene`** is the one-shot, and it cost no new flag bit.
  It is a **1994-declared globalflag (bit 1050) with zero readers and zero
  writers in the entire corpus** — declared and then never used. In TESTPLAN
  this exchange *is* the final beat of the plant scene, so the conversation
  that now carries the words also carries the ending, and therefore the flag.
  Because the block now reads it, the scene-end workstream must not set it
  elsewhere.

Two findings came out of the work, both pre-existing, neither fixed here:

1. **`ATLI.UNK:193` had the EZREKAL root-period bug.** The menu-add spelled
   the option `"I have been poisoned."` while its own case (2331) and its own
   removal (2346) spelled it `"...poisoned!"`. The lexer collapses whitespace
   and truncates at `\f`, so punctuation was the only surviving difference:
   the offered option matched no case and could not even remove itself.
   Fixed at the single add site. The fix is **inert today** — the branch that
   offers it is behind the dead `avatarPoisoned` gate — and correct the
   moment the poison comes back.
2. **`plantScene` is set and never cleared.** `PLNTST.UNK:82` sets it; nothing
   in the corpus clears it. `Atli::schedule` (line 60) and `Thordis::schedule`
   both return early while it is set, so **both elders' schedules are
   permanently disabled from quest step 8 onward**. That is a systems fix with
   map and schedule consequences, so it is recorded rather than made. Clearing
   `plantScene` is the other half of a proper scene-end and belongs with it.

Still asymmetric: on the `atliToldTest` branch TESTPLAN gives the same speech
to **Thordis**, and `lv-patched/PLNTST.UNK` drops that half too — it teleports
her in and leaves her silent. The symmetric fix is a `lv-patched/THORDIS.UNK`
doing for her what this file does for Atli.

### D, as implemented

Nine of the eleven were re-pinned from 1431-1446 into **1252-1260**, reached
by **npcNum 228-236**; the old pins are retired (keyed `NAME_<id>`, since the
live name still exists in `classes`). Seven are placed and reachable.
**Orphans 17 → 10.** No compiler change was needed: the manifest `classes`
pin path already routes an id inside the base-FLX entry range through
`add_new_class`, which is exactly what TypeReceptacle (1144) has always done.

The band was picked by scan, not by eye. Two properties have to hold, and
both are now documented at `NPCNUM_BANDS` in `lv_shapes.py`: the target class
must be empty in the base FLX (106 of the 255 slots in 1025-1279 are occupied
by the base game's own NPCs), and no item on any map may already carry that
npcNum byte. On the second point the base game is clean — **zero** non-egg
base-game items carry npcNum; every base-game npcNum byte sits on an egg
shape (2/73/500/508), which the engine patch explicitly excludes. So nothing
we add in this window can hijack base-game content.

| Class | New id | npcNum | Placement |
|---|---|---|---|
| TYPEAOFRIZBEE | 1260 | 236 | already placed — the 2 Map 17 shield halves, npcNum byte added only |
| TYPEMONSKUL | 1252 | 228 | **new** — Map 18 Inner Sanctum altar |
| TYPEPOTION | 1253 | 229 | **new** — 2 at Ezrekal's (frames 1 heal, 2 mana) |
| TYPEABACUS | 1254 | 230 | **new** — Gunnar Village inventor's bench |
| TYPEBEDROLL | 1255 | 231 | **new** — 1 at Ezrekal's |
| TYPEBULLWHIP | 1256 | 232 | **new** — lakeside ruins |
| TYPEFEDORA | 1258 | 234 | **new** — lakeside ruins, beside the whip |
| TYPEPEDESTALS | 1257 | 233 | pinned, **not placed** — blocked, see below |
| TYPENSGOLDPLAQUE | 1259 | 235 | pinned, **not placed** — blocked, see below |

Only TYPEAOFRIZBEE required no invention: both halves were already on Map 17
and only needed the npcNum byte. Everything else marked **new** is a
placement chosen in this pass; none is quest-significant, none is read by any
flag, quest step or dialogue, and nothing gates on picking any of them up.
Two are worth calling out rather than filing under "flavour":

- **TypeBedroll is not a joke item.** Its `use()` is the base game's bed
  code: it asks how long to rest, advances the clock and restores HP and mana
  in full. That is a rest point, so exactly one is placed, at Ezrekal's.
- **TypeMonskul carries lore**, a Zealan priestess's letter about the Titans
  closing on the Vale. It is placed on the Temple altar because the letter
  says its writer went to the Temple. That is a reading of the text, not a
  recovered 1994 placement.

**The compiler-side TYPE_SHAPES ids for these classes are mostly wrong**, and
following them would have repeated the SI_FIXED trap. `TypeAbacus` and
`TypeNSGoldPlaque` both point at 158, which is SI_FIXED and renders as a
wooden *stool*; `TypeMonskul` points at 189, a 322-frame container humanoid;
`TypeFedora` at 578, an 81-frame effect shape. Every shape actually used was
picked by name from `shape_names.json` and then checked against TYPEFLAG —
375 abacus, 534 bedroll, 331 skull, 766 potion, none SI_FIXED. This is more
evidence for CLAUDE.md's standing warning that TYPE_SHAPES is legacy.

Two placeholders, stated plainly: U8 contains **no fedora and no whip
anywhere** in its shape table (full name sweep), so those two are a helmet
and a coiled rope. The joke reads from the bark, not the sprite.

### D, the two that should not be wired

- **TYPEZEALANCHILD1 (left at 1437)** is not an item class at all. It
  inherits `pesantBoy` and uses `enterConvo()`, `cSetActivity(ACT_LOITER)`,
  `getTarget()` and `isDead()` — Actor behaviour that plain item dispatch
  cannot support. It needs Actor promotion, and that window (npcNum 100-116)
  is full: 17 slots, 17 placed villagers. This is SIGRID's problem again, and
  it needs the same kind of decision, not a pin.
- **TYPEPOISONPLANT (left at 1436)** is superseded, and wiring it would undo
  decision A. `lv-patched/PLNTST.UNK` says in its own header that
  `TypePoisonPlant::use()` was "the ACTUAL scene" and that it was merged into
  the EggPlantTest hatch — which is wired. On top of that,
  `TESTPLAN.UNK:250` sets `avatarPoisoned`, the uncurable poison decision A
  had just switched off. Recommend retiring the class outright.

### D, follow-up work

- **TYPEPEDESTALS (1257, npcNum 233)** implements only `gotHit()` and returns
  unless the thing that hit it is a `TypeEaLogo`. `EALOGO.UNK` is one of the
  two files on the documented compile-failure allowlist, so the other half of
  the Earth/Air puzzle does not exist. Placing pedestals now would place
  scenery that can never complete. Unblock by fixing EALOGO's truncated block
  comment in `lv-patched/`, then place logos and pedestals together.
- **TYPENSGOLDPLAQUE (1259, npcNum 235)** is a 67-branch quality table whose
  branches are almost entirely base-game Pagan signage. No LV-specific
  quality exists yet, so there is no plaque to place. Belongs with the
  pending "gold plaques 158→599/614" art fix; note the real plaque shapes
  (599/614) are SI_FIXED, which is correct for wall signage.

### Still open after this pass

**H is done** and **D is done for nine of the eleven**; the two it
correctly refused (TYPEZEALANCHILD1, TYPEPOISONPLANT) are explained in
its section above. What remains:

**The re-enable pair.** When the EggShades trigger (quality 294) is placed,
three things move together: restore the poison line in lv-patched/PLNTST.UNK,
flip the two inverted assertions in test_uc_plntst.py, and re-record hashes.
