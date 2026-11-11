# Four anomalies, diagnosed (2026-09-30)

Read-only investigation. No files built, installed, or launched; nothing
committed. All four are root-caused from engine source, usecode source, and
the built `shared/build/FIXED.DAT` / `shared/build/TYPEFLAG.DAT` already on
disk.

| # | Anomaly | Root cause (one line) | Confidence |
|---|---|---|---|
| 1 | Pack weight/capacity swings while Tiny Tar | `Actor` is a `Container`; its own weight/capacity read the TYPEFLAG row of whatever shape the Avatar currently wears, and `setType` is `setShape` | High (numbers match exactly) |
| 2 | Empty bottle blocks the stack | `TraceObjId` hit-tests `_contents` in reverse; the potion that answers the first click stays last in the list after `setFrame(0)` | High (the mechanism); the 1994 behavior is a step removed (see below) |
| 3 | Both eggs re-hatch at the regrow | `makeAvatarBig()`'s `teleport(0,0,0)` / `teleport(back)` round trip clears both eggs' fast-area state via the camera-follow chunk recalc | High for the mechanism (confirmed against source); Medium for the "barks twice" claim (read off the code, screen evidence still pending) |
| 4 | Frame 5/7 potions unplaced | Never placed by any map builder; omitted from the 2026-07-26/07-27 placement passes, and silently inert until a 2026-09-25 compiler fix | High (unplaced); Medium (why, and what the pre-fix symptom actually was) |

## 1. Carry weight/capacity while Tiny Tar

**Root cause.** `Actor : public Container`
(`scummvm-lv-console/engines/ultima/ultima8/world/actors/actor.h:37`). Both
`Container::getTotalWeight()` and `Container::getCapacity()`
(`world/container.cpp:219-245`) start from the container's own shape info:
`Item::getWeight()` (`world/item.cpp:786-797`, default case `weight * 10`)
and `getCapacity()` is `getShapeInfo()->_volume`. For the Avatar, "own
shape" is whatever `_shape` currently is. Equipment (backpack, weapon,
armor) lives as ordinary items inside the Actor's own `_contents`
(`world/actors/actor.cpp:396-421`, `setEquip`/`getEquip`), added there by
`Container::addItem`, so the Avatar's own `getTotalWeight()` sums its own
body weight plus every equipped item's weight, recursively.

`makeAvatarTiny()`/`makeAvatarBig()` (`agents/usecode-compiler/src/lv-patched/FREE.UNK:1388`,
`:1479`) call `Avatar.setType(TypeTinytar)` / `Avatar.setType(TypeAvatar)`.
Usecode `setType` reassigns the Avatar's own shape id, a far bigger effect
than a cosmetic frame change: in the U8 intrinsic table,
`"void Item::setType(uword type)"` is entry index 14
(`convert/u8/convert_usecode_u8.h:56`, counting from `"process target()"` at
line 42), and intrinsic index 14 is `Item::I_setShape`
(`usecode/u8_intrinsics.h:72`). So `setType` reassigns the Avatar's own
`_shape` (`Item::setShape`, `world/item.cpp:483`; `Item::I_setShape`,
`world/item.cpp:2807`), the same field `Container::getWeight()`/
`getCapacity()` read.

`TypeTinytar` is pinned to shape 708, the base game's generic child actor,
picked for its footpad (1,1,4) = 32x32 and 70+ frames (reasoning recorded at
`agents/usecode-compiler/src/u8c_symbols.py:259-265`, which notes "family
SF_CONTAINER so inventory survives the swap": equipment survival was
checked, but weight/capacity leakage from the same field went unchecked.
TYPEFLAG for
shapes 1 and 708, read directly from the built artifact and identical in
the unmodified base-game copy:

```
$ python3 -c "...parse_typeflag.load_typeflag('shared/build/TYPEFLAG.DAT')..."
Shape    1:  footpad=(2,2,5)  wt=1  vol=250
Shape  708:  footpad=(1,1,4)  wt=50 vol=200
```

Own-weight contribution: shape 1 gives `1*10=10`; shape 708 gives
`50*10=500`. With the Avatar's actual equipment contributing a constant
near 20 (backpack plus its remaining contents, consistent with F11's
"Avatar total weight 20 -> 30" baseline,
`docs/playtest-2026-08-18-f10-climb.md`), total weight is `500+20=520`
shrunk and `10+20=30` grown; capacity is `getShapeInfo()->_volume` directly,
**200** shrunk and **250** grown. Both pairs match TODO.md's numbers
exactly, and this is the mechanism that produces them, closed numerically.

**What "the pack" actually is here.** The backpack's own shape (529) has a
fixed TYPEFLAG volume of 175 (`parse_typeflag.load_typeflag(...)[529]` ->
`vol=175`), matching the "capacity 175" already on record from F11
(TODO.md, the 2026-08-18 entry). 175 never appears in this anomaly's
numbers, so 200/250 cannot be the backpack's own capacity; they are the
Avatar's, read the same way the 09-03 chest report read the chest's
(`Container::dumpInfo`, `world/container.cpp:312-316`, format
`"Container vol: %u/%u, total weight: %u"`). The one number the player
actually sees in the gump is the paperdoll's `WGHT` stat
(`gumps/paperdoll_gump.cpp:169-178`, `a->getTotalWeight()/10`): 52 while
shrunk versus 3 at normal size, both derived from the same 520/30 figures.

**Gameplay consequence: this reaches more than a debug readout.**
`Container::CanAddItem`
(`world/container.cpp:96-131`) is reached on every attempt to pick up or
equip an item: line 117 rejects on volume (`getContentVolume() + newVolume >
capacity`, so the Avatar's own capacity drops to 200 while shrunk, down from
250, cutting into whatever volume headroom equipped gear already used), and
line 129 rejects
on weight for anything moving in from outside the Avatar's inventory
(`p->getTotalWeight() + item->getTotalWeight() > 40 * str`, where `p` is the
Avatar). Shrunk, the Avatar's own weight term is 490 heavier for the same
strength, so picking up or equipping new items while tiny has measurably
less headroom than the UI's single `WGHT` number would suggest.

These are stock base-game TYPEFLAG values, untouched by any LV build step.
Shape 708 is also used, unmodified, for two decorative village children
(`agents/map-populator/src/build_map_10.py:591,726`). Nobody authored these
particular weight/volume bytes for this purpose; they describe what a dead
child NPC weighs and can hold, applied here as a side effect of reusing the
shape for a disguise.

**Proposed fix.** Give `TypeTinytar` its own shape slot, separate from the
reused 708, so the swap touches nothing else and the Avatar's own weight/capacity
can be pinned to sane values (for example `wt=1, vol=250`, matching shape
1, so the disguise changes nothing about what the player can carry). This
is also the direction the project already intends: the header comment at
`u8c_symbols.py:267-272` already calls 708 "interim art" pending a bespoke
tiny-Avatar sprite. Two things are needed together:

- **Art.** A new slot needs the 100 frames of shape 708 copied into
  `U8SHAPES.FLX`, the same way `agents/map-populator/src/lv_tiny_tar.py`
  injects shape 859 as a `tools/build_artifacts.sh` step. A TYPEFLAG remap
  alone draws nothing; without the matching shape injection the Avatar would
  render as an empty slot while shrunk.
- **TYPEFLAG.** `agents/map-populator/src/patch_typeflag.py`: add a
  `REMAP` entry copying 708's footpad/family/frame count to a new slot (the
  next free custom id per `.claude/rules/shape-ids.md`, currently 867), then
  overwrite its weight/volume bytes to match shape 1 (a small
  `set_weight_volume()` helper alongside the existing `set_footpad()`).
- `agents/usecode-compiler/src/u8c_symbols.py`: point `TypeTinytar` /
  `TypeTinyAvatar` at the new id.
- Artifact rehash (TYPEFLAG, U8SHAPES, and EUSECODE, since the shape
  constant compiles into bytecode) and a verifier pass against the existing
  Tiny Tar and sanctum playtests.

A smaller alternative, patching shape 708's TYPEFLAG entry in place, needs
no new art, but it changes the two village children's own container stats
too, almost certainly inert for them since they never display their own
weight or capacity in play. Worth naming to Douglas as a shared side effect
of reusing a stock shape, for him to decide on explicitly.

## 2. Empty bottle blocks the stack

**Root cause.** Every `TypePotion::use()` branch ends by calling
`setFrame(0)` on itself, never `destroy()` or any reposition
(`shared/data/lv-usecode/LOST VALE/POTION.UNK:40,49,73,97,111,144`, and inside
`protection()`/`invisible()`'s `startup` blocks at lines 166 and 204). The
item persists at frame 0, in the same container, in the same slot.

Gump hit-testing in `ContainerGump::TraceObjId`
(`scummvm-lv-console/engines/ultima/ultima8/gumps/container_gump.cpp:196-231`)
iterates `_contents` backwards (the method's own comment at line 211:
"iterate backwards, since we're painting from begin() to end()") and
returns the first item whose frame rectangle contains the click. `PaintThis`
(lines 168-179) paints begin to end, so the last item in
`Container::_contents` both paints on top and wins every click. Items move
within `_contents` only through `Container::moveItemToEnd`
(`world/container.cpp:156-167`), called only from drag-and-drop
(`gumps/container_gump.cpp:556,565`), never from `use()`. The potion that
happens to be last in the list is, by that same reverse hit-test, the one
the player's first double-click would land on; drinking it changes only its
frame, so it stays last afterward, and keeps answering every later click.

**Would 1994 have done the same?** The usecode half is identical: every
frame branch in the recovered 1994 class, Tiny Tar's frame 8 included, ends
in a self `setFrame(0)`, so the same multi-potion trap exists in any 1994
scenario with two or more identical potions sharing a gump cell. The
hit-test half (`ContainerGump::TraceObjId`) is ScummVM's reimplementation of
the DOS engine's gump code; this repository holds no way to read the
original binary's logic directly, so that half of the claim rests on
ScummVM reproducing documented DOS container behavior; it has not been
confirmed by a byte-level comparison. Lost Vale's DD-005 is, as far as the
recovered design
material shows, the first design in this project to put three identical,
sequentially-needed potions in one place under light time pressure, so a
quirk that may always have been latent becomes a real usability problem
here.

**Proposed fix.** Scope the change to the one frame Lost Vale added,
leaving the other seven retail frames' behavior alone: have the frame-8
branch of `TypePotion::use()` either `destroy()` the bottle or `pop()` it to
the Avatar's feet, so a drunk Tiny Tar bottle leaves the pack and no longer
occupies the gump slot the remaining full potions share. Frame 8's branch does nothing with `referent`/`sub`
afterward (it only drives the Avatar via `makeAvatarTiny`/`makeAvatarBig`),
so either change should be safe, but this is exactly the kind of claim the
`verifier` agent should exercise in engine before it ships. Touches:

- `agents/usecode-compiler/src/lv-patched/POTION.UNK`: new patched copy
  (byte copy of `shared/data/lv-usecode/LOST VALE/POTION.UNK` plus the one
  change in the `fram = 8` branch), per
  `.claude/rules/recovered-source-is-evidence.md`.
- `agents/usecode-compiler/docs/lv-patched-inventory.md`: new entry.
- Artifact rehash (EUSECODE.FLX) and a verifier/playtest pass: drink two of
  the three chest potions in sequence and confirm the third is reachable
  without dragging anything aside.

## 3. Both eggs re-hatch at the regrow

**Root cause.** `Egg::unhatch()` (`world/egg.cpp:45-51`) is a Crusader-only
path (`if (GAME_IS_CRUSADER) { ...clear _hatched... }`), a no-op for U8,
matching `CRACKHNT.UNK`'s own header note that "`Egg::unhatch()` is a
Crusader-only no-op". `EggHatcherProcess::run()`'s call to `unhatch()`
(`world/egg_hatcher_process.cpp:94`) therefore leaves both eggs' `_hatched`
flag alone under U8. The actual reset comes from the fast-area mechanism:
`Egg::leaveFastArea()` (`world/egg.cpp:60-63`) calls `reset()`
(`world/egg.h:63-65`, `_hatched = false`) whenever the egg's map chunk
drops out of the camera's fast-area window.

`makeAvatarBig()` (`lv-patched/FREE.UNK:1412-1487`) does, in order:
`Avatar.teleport(0,0,0,Avatar.getMap())` (line 1436), a synchronous
`canExistAt(TypeAvatar,...)` check (line 1437), then, on the success path,
`Avatar.teleport(teleX,teleY,teleZ,Avatar.getMap())` (line 1457). The two
`Camera::setCenterOn(...)` calls meant to detach and reattach the camera
around this round trip (lines 1425, 1483) do not compile at all: per
`.claude/rules/camera-intrinsics.md`, the `Camera::` spelling is a parse
error that the compiler silently drops, confirmed there specifically for
`lv-patched/FREE.UNK`. The Avatar keeps `EXT_CAMERA` set throughout.
`Item::move()` (`world/item.cpp:165-271`) checks exactly that flag: moving
to a non-fast destination (`(0,0,0)`) while camera-followed takes the
`CameraProcess::GetCameraProcess()->itemMoved()` branch (lines 247-250);
the Avatar itself never gets a direct `leaveFastArea()` call here.
`CameraProcess::itemMoved()` (`world/camera_process.cpp:178-197`) calls
`CurrentMap::updateFastArea(from, to)` (`world/current_map.cpp:442-504`),
which recomputes the fast window spanning the old and new camera positions
and calls `unsetChunkFast()` (lines 514-530) on every chunk that falls
outside it; `unsetChunkFast` calls `item->leaveFastArea()` directly,
synchronously, on every item in that chunk. With the destination at
`(0,0,0)`, the fast window briefly spans from the crack to the map origin,
so both `EggCrackHint` and `EggTempleEntry` (both well within the old fast
area) fall out of the new one and get `leaveFastArea()` called on them in
that same call. The return teleport re-admits their chunks
(`setChunkFast`, line 509-511, calls `enterFastArea()`; the hatch itself
waits for the next `EggHatcherProcess::run()` tick, which finds the Avatar
back in range of both with `_hatched` now false on each, so both `hatch()`
fire again). This
matches the sanctum-breach log, which shows `05B1`/`05B0` hatching on
adjacent lines while the Avatar was "still shape 708", before
`makeAvatarBig`'s closing `setType(TypeAvatar)`, consistent with the
teleport round trip near the start of that routine.

**Is the re-hatch harmless, or does it duplicate a bark?** Depends which
egg, and on `templeOpen`:

- `EggTempleEntry::hatch()` (`TEMPLENT.UNK:36-122`) is idempotent once
  `templeOpen` is true: its local `first` comes out `1` only the one time
  `templeOpen` flips from false, so a later re-hatch re-runs only the
  already-satisfied wall-destroy sweep and returns before the three "I am
  through..." barks (`:76-113`). This matches the playtest report's own
  reading of the same log lines.
- `EggCrackHint::hatch()` (`CRACKHNT.UNK:33-88`) has no such guard. With
  `templeOpen` still false, and for the wall-side instance (`getY() >=
  5500`; the early return at `:70-73` is for the doorway instance only),
  every hatch unconditionally re-runs `Avatar.bark("The stone here is
  split...")` (`:75-76`), plus the stronger follow-up bark if frame-8
  potions remain in the pack (`:82-87`). So with `templeOpen` 0, a
  teleport-round-trip re-hatch would bark the hint a second time: this
  follows directly from the code and needs no further engine change to
  reproduce it, but the 09-26 report did not capture it on screen ("the
  frames were not checked"), so treat the specific "it barked twice" claim
  as medium confidence: read off the code, pending screen confirmation.

No existing test (`agents/usecode-compiler/src/test_uc_eggs.py`) exercises
this path; it checks the pinned class IDs for both eggs but not any
teleport-induced re-hatch.

**Proposed fix.** Two options, complementary and both worth doing over time:

1. **Low-risk, usecode-only.** Give `EggCrackHint` an idempotency guard: a
   `globalflag` (for example `crackHintGiven`), set after the first hint
   bark and checked before barking again. `globalflag` names are picked up
   automatically by a manifest scan of every `.UNK` source
   (`agents/usecode-compiler/src/lv_manifest.py:76,284`;
   `agents/usecode-compiler/docs/manifest-design.md:133`), the same way
   `templeOpen` is simply declared in `CRACKHNT.UNK:26` and `TEMPLENT.UNK:28`
   with no separate allocation file, so the new flag needs no registry edit
   beyond declaring it in `CRACKHNT.UNK` itself. Touches only
   `agents/usecode-compiler/src/lv-new/CRACKHNT.UNK`.
2. **More thorough, engine-level.** `CurrentMap::I_canExistAt`
   (`world/current_map.cpp:1238-1264`) hardcodes the "item to ignore"
   argument of `getPositionInfo()` to `0` and discards three extra usecode
   arguments with a `//!! TODO: figure these out` (lines 1243-1245), which
   is why `makeAvatarBig()` has to physically move the Avatar out of the
   way before testing whether it fits: the engine gives usecode no way to
   exclude the Avatar's own hitbox from the test otherwise. Wiring those
   arguments through to `getPositionInfo()`'s ignore-item parameter would
   let `canExistAt` answer "would a full-size body fit here, ignoring my
   own current box" without moving first, removing the teleport round trip
   from `makeAvatarBig()` and fixing the re-hatch for every nearby egg, not
   only this pair. Larger diff, touches shared engine code
   (`scummvm-lv-console`, tracked via
   `tools/scummvm-patches/0001-lost-vale-engine.patch`), needs a full
   ScummVM rebuild and a verifier pass.

Recommend landing 1 first (contained, fixes the one user-visible symptom)
and filing 2 as a tracked follow-up, since it is the more correct general
fix but a larger piece of work to verify.

## 4. Frame 5/7 potions placed nowhere

**Confirmed by direct scan.** The built `FIXED.DAT` holds exactly five
shape-859 (`SHAPE_POTION_REAL`) records across every map:

```
$ python3 ...u8_map.MapArchive('shared/build/FIXED.DAT')... shape==859
map 10, frame 8, contained, x3   : Hrodny's chest, Tiny Tar
map 10, frame 1, (13824,12672,4) : Ezrekal's shelf, health
map 10, frame 2, (13760,12672,4) : Ezrekal's shelf, mana
```

Zero frame-5 or frame-7 records. A grep of every
`agents/map-populator/src/build_map_*.py` confirms only `build_map_10.py`
ever places shape 859, at exactly those three frames.

**What is and is not recorded about the omission.** The 2026-07-25 orphan
triage (`docs/reviews/2026-07-25-orphan-triage.md:253-286`) is where
`TypePotion`/class 1253 was wired to `npcNum 229` and first placed; its own
table (line 275) lists only "2 at Ezrekal's (frames 1 heal, 2 mana)" and
says placement for this whole group "is a placement chosen in this pass;
none is quest-significant", and gives no reasoning for any of the frames it
left unplaced (3 through 7; frame 8 did not exist yet, since shape 766 then
had only frames 0-7). A later comment in `build_map_10.py:925-937` (written
when DD-005's frame-8 Tiny Tar was added, 2026-07-27) says "Frames 4
(damage) and 6-7 (sleep/invisibility) are deliberately NOT placed: they are
effects with balance consequences", grouping frame 7 (invisibility,
beneficial) with frame 6 (sleep, a hostile trap) under a balance rationale
that fits 4 and 6 more cleanly than 7, and never mentioning frame 5 at all.
Neither document records a reason for frame 5 specifically.

The likelier reason: at the time of both passes, `protection()`/
`invisible()` (frames 5 and 7) were broken by the same-class-spawn
null-`this` bug fixed in `1b0bf9a` (2026-09-25). The pre-fix symptom was
milder than a crash: `Item::I_setFrame` (`world/item.cpp`, `if (!item)
return 0;`) silently no-ops on a null item without asserting, unlike
`I_readPlaque`'s assert, which is what made the gold-plaque bug visible in
the first place. So a drunk frame-5 or frame-7 potion, before the fix,
would have applied its full effect (`Avatar.setImmortal()`, the
invisibility toggle both operate on `Avatar` explicitly), while the bottle
itself would never have emptied, since the only `this`-implicit statement
in either routine is the one `setFrame(0)` call. That reading fits the
1b0bf9a commit message's own phrasing ("now `setFrame(0)` the potion
itself, not item 0") more closely than a crash would. Neither orphan-triage
pass states this as its reason; treat it as the likely explanation, this
review's own reading of the code, absent from both documents.

**Base game comparison, with a gap in what was checked.** The original,
pre-DD-005 potion shape (766, before the 859 remap) is placed six times in
the unmodified base-game `shared/data/u8-install/STATIC/FIXED.DAT`: frame 3
x2, frame 4 x2, frame 5 x1 (map 41, contained at depth 1), frame 6 x1, and
frame 7 zero times. That frame-5 record is dispatched through the base
game's own unmodified usecode class. Lost Vale's `npcNum 229` wiring reaches
a separate, orphaned `TypePotion`/class 1253
(`build_map_10.py:801-804,925-927`), so that base-game record never
exercises the code this review is about. The "frame 7 zero times" count is FIXED.DAT only: retail's
movable items live in `NONFIXED.DAT`, which is not shipped as a static file
(`shared/data/u8-install` has none) and exists only inside a generated
save. Confirming whether retail ever places a frame-7 potion as a movable
item would need an engine run against a fresh save, which this read-only
pass did not do; treat "zero in retail" as true for fixed/scenery
placements only.

**1994 design materials.** A grep of `shared/corpus/plot-documents/`
(`items.yaml`, `story-beats.yaml`, `characters.yaml`, `locations.yaml`,
`known-gaps.md`) turns up only the Tiny Tar potion and the Tyorvi
nightmare-root potion subplot; neither protection nor invisibility potions
are named anywhere in the recovered design material. No quest requirement
drives a placement either way; these are generic, non-critical consumables.

**Proposed fix.** Frame 4 (damage, self-harm risk) and frame 6 (sleep, a
multi-second stasis trap) have an actual balance argument for exclusion;
frame 5 (protection: temporary immortality plus a combat buff) and frame 7
(invisibility) are beneficial, the same as the already-placed frames 1 and
2. The lowest-risk placement mirrors the existing decision: add one frame-5
and one frame-7 `SHAPE_POTION_REAL` item beside the existing frame-1/frame-2
pair on Ezrekal's shelf (`build_map_10.py:938-943`), with the same
`npcnum=NPCNUM_POTION` wiring. Touches:

- `agents/map-populator/src/build_map_10.py`: two new `MapItem(...)` calls
  beside lines 938-943.
- Artifact rehash (FIXED.DAT) and a verifier/playtest pass. This would be
  the first in-engine exercise of `protection()`/`invisible()` through the
  fixed same-class-spawn codegen, so the playtest should include drinking
  both, beyond confirming they appear on the shelf.

**Decision:** place both at Ezrekal's shelf, since nothing in the recovered
1994 material argues for a different location, unless Douglas would rather
hold off placing anything until the fixed `protection()`/`invisible()` path
has been exercised once in engine.
