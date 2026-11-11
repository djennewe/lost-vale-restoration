# Map 8 double doors — diagnosis, 2026-07-31

Investigation of the blocking regression reported as test D'2 in
`docs/playtest-2026-07-31-retest-hardened-gates.md` ("the double doors do not
open — they answer neither look nor use").

Run on kaga/Linux, branch `agent/village-pipeline`, tip `81d884c`. Artifacts
verified against `shared/build/ARTIFACTS.sha256` before starting, and
`shared/u8-lv-patched/` confirmed byte-identical to all four. Text-console
ScummVM (`scummvm-lv-console/scummvm`) on the Xvfb harness. Exactly one
`scummvm` pid at all times; the session was stopped at the end (0 pids).

**No source file, map builder, artifact or configuration was modified.** The
only writes are this report and `docs/playtest-2026-07-31-doors/`
(26 screenshots).

---

## Verdict

**The doors work. The retest's D'2 findings were wrong, and the real defect is
a different, intermittent one: a wandering base-game GHOST (shape 411,
`SI_SOLID`) parks itself inside the doorway and the door's own retail usecode
then refuses to open with the bark `"blocked"`.**

Opened end to end this session, with the key fetched legitimately:

```
key (shape 82, q=99) from the chest  ->  weight 20 -> 30
double-click the key in the pack     ->  target cursor
click a door leaf                    ->  west q 0x663 -> 0x263, east q 0x463 -> 0x63
                                         (the 0x400 LOCKED bit cleared on BOTH leaves)
double-click a door leaf             ->  both leaves become shape 340 TDOOR_NS,
                                         q 0x363 / 0x163 (0x100 OPEN bit set)
walk north through the doorway       ->  trigger 201 fires -> MAP 9 (14276,12740,0)
```

`21-DOORS-OPEN.png`, `24-through-doorway.png`, `25-arrived-map9.png`.

So the 2026-07-02 claim stands, and the "walk north through the doors" half of
test D' is now demonstrated live, including the 8→9 gateway.

---

## 1. The three cheap hypotheses, all eliminated

### (a) SEEDING — the door items exist, in pristine data and in the live game

`SAVEGAME/U8SAVE.000` parses as a named-section container (23-byte magic,
uint16 count at `0x18`, entries from `0x1A` — the reader in
`agents/map-populator/src/scan_npc_slots.py`). Its `NONFIXED.DAT` section
(242,096 B) is the same FLX-header + 16-byte-record format as FIXED.DAT. Map 8
holds 584 dynamic items, and both leaves are there exactly as documented:

| record | shape | frame | position | quality |
|---|---|---|---|---|
| 186 | 342 | 0 | (20351, 3071, 0) | 1635 = **0x663** |
| 184 | 342 | 1 | (20479, 3071, 0) | 1123 = **0x463** |

All four ENGLISH copies of `U8SAVE.000` on this machine are byte-identical
(sha256 `2475bc03…`), including `shared/u8-lv-patched/SAVEGAME/U8SAVE.000`,
the pristine `shared/data/u8-install/` copy, and the copy inside the expanded
GOG package. **There is no `.bak` and no divergence — the savegame template is
untouched retail.** (FRENCH and GERMAN differ in size; irrelevant here.)

Live, the leaves are objids 14577 / 14575 (session 2), reachable, clickable,
and at their pristine qualities before the key is used.

### (b) USECODE — byte-identical on every door-path class

`shared/build/EUSECODE.FLX` vs the pristine GOG `EUSECODE.FLX`: 39 FLX entries
differ out of 1460. **None of them is on the door path.** Specifically
identical:

| class | FLX entry | name | role |
|---|---|---|---|
| 0x156 (342) | 344 | `TDOOR_EW` | the door leaves' own class |
| 0x154 (340) | 342 | `TDOOR_NS` | the open form |
| 0x044 (68) | 70 | `DOOR_NS` | the shared door library (use/look/lock/open) |
| 0x04F (79) | 81 | `KEYRING` | contains the unlock routine at offset `0119` |
| 0x052 (82) | 84 | `KEY` | the key |
| 0x581 (1409) | 1411 | `FREE` | `2411` = the type-swap helper doors open through |

Of the 39 differences, **34 are new LV classes written into previously-empty
entries**. Only five touch an entry that already had content: FLX entry 1
(the globals block) and classes 1025, 1037, 1057 and 1410 — none of them
reachable from a door.

Correction for the record: **"class 0x4F, FLX entry 0119" in `TODO.md:897` and
`agents/map-populator/docs/map-08-plateau-entry.md:35` is a misreading.**
`0119` is a *code offset inside class 0x4F*, not an FLX entry — it is the
`spawn 004F 0119` target that both `KEYRING::use()` and `KEY::use()` jump to.

### (c) TYPEFLAG — identical except our four new shapes

`shared/build/TYPEFLAG.DAT` vs pristine differs in exactly 4 of 2048 entries:
shapes **856, 857, 858, 859** (the wood-plank walls and the Tiny Tar potion).
Shape 342's entry is untouched: `221040a100010001` → `SI_SOLID`, family 1
(`SF_QUALITY`), footpad 4×1×10, not `SI_FIXED`.

Note a trap for anyone repeating this: `shared/data/u8-install/STATIC/*` and
`USECODE/*` have been **overwritten by the installer with our built
artifacts**. The pristine bytes are the `.bak` files beside them, which are
byte-identical to
`shared/data/u8-pkg-expanded/…/ENGLISH/{STATIC,USECODE}/`. Diffing against
`shared/data/u8-install/` compares the build against itself and always
reports zero differences.

---

## 2. What the retest actually saw, and why its conclusions were wrong

The retest reported four things about the doors. Three are contradicted
directly.

| retest claim (D'2) | this session |
|---|---|
| "double-clicks on the door leaves do nothing — no unlock, no open, no bark" | **False.** Double-click barks **`Locked Door`** every time (`05-dclick-use.png`). |
| "single-click look also produces no bark" | **False.** Single-click barks **`Locked Door`** (`04-look-bark.png`). |
| "the cursor stays the blue walk arrow over the door pixels — i.e. the engine's click trace finds no item at those pixels" | **False, and the inference is invalid** (below). |
| "`MainActor::useKeyring` produced nothing either" | **True but expected** — the Avatar has no keyring at that point, and the keyring path is not the one that works. |

**The cursor never reflects what is under it.** Over the game map the cursor is
`MOUSE_NORMAL`, and `Mouse::getMouseFrame()`
(`scummvm-lv/engines/ultima/ultima8/kernel/mouse.cpp`) computes its frame from
`getMouseDirectionScreen()` and `getMouseLength()` — direction and distance
from screen centre, plus combat state. It never consults the item under the
pointer. "The cursor stayed a walk arrow" is therefore no evidence at all about
the trace.

**The trace works.** With `debugflag_enable Object` on, both
`GameMapGump::onMouseClick` and `onMouseDouble` log `item->dumpInfo()` before
doing anything (`gumps/game_map_gump.cpp:302`, `:352`). Two eight-click probe
sweeps across the closed door art, one per session, hit a door leaf on **8/8**
in session 1 and **6/8** in session 2 (the two misses were the Avatar's own
sprite and a floor slab at the very bottom edge of the art). Not one click
anywhere on the leaves returned nothing. Example line:

```
Item 14576 (class Item, shape 342) (uc: TDOOR_EW), 0, (20351, 3071, 0)
    q: 1635, m: 0, n: 0, f: 0x2000, ef: 0x2 shapeinfo f: 22, fam: 1, et: 0
```

Most likely explanation for the retest's negatives: **barks are transient
floating text and they render at the very top edge of the viewport** for an
item this tall — see `04-look-bark.png`, where `Locked Door` sits at y≈207,
11 px below the top of the 640×480 surface, nowhere near the door. A
screenshot taken a second or two late, or an eye on the door rather than the
frame edge, misses it. The other candidate is HANDOFF's own trap #1: input sent
while the debugger is attached (= engine paused) does nothing at all.

One genuine and useful observation from the retest survives: in *its* session,
every probe click found only the **west** leaf. That is consistent with what
was actually in the way — see below.

---

## 3. The correct interaction (this is the part that was never written down)

**You do not open a locked U8 door by clicking the door. You double-click the
KEY in your inventory, which gives a target cursor, and then click the door.**

Decoded from the retail usecode, and confirmed live:

* `KEY::use()` (class `0x52`, event 1, offset `04BB`) and `KEYRING::use()`
  (class `0x4F`, event 1) both do the same thing: `spawn 004F 0119`.
* `004F:0119` is the unlock routine:
  1. `calli 00 0000` → **`process target()`** — raises the targeting cursor and
     suspends.
  2. `Item::canReach(…, 0x80)` on the target → range **128**; on failure it
     barks `"can't reach  "`.
  3. Shape whitelist: target type must be **68, 69, 0x154 (340) or 0x156
     (342)**. Shape 342 is in it, as documented.
  4. If `target.quality & 0x100` → barks `"it's open "`.
  5. Match test: if the used item is type 82 (a key), compare
     `target.getQuality() & 0x00FF` (the lock ID) against the **key's full
     quality**. Our key is q=99, the doors' low byte is 0x63 = 99. Match.
     (If the used item is type 79, it loops over type-82 keys *inside* the
     keyring instead — which is why `MainActor::useKeyring` does nothing when
     the key is loose in the pack.)
  6. On a match it calls `0044:05E4` and `004F:00C8`, which clear the **0x400
     LOCKED** bit on the leaf *and its partner*.

Live confirmation that the target cursor is real, taken from
`Kernel::listProcesses` while it was up:

```
Process 2899 UCProcess, item 14182, classname: KEY,     IP: 0052:04D6
Process 2900 UCProcess, item 14182, classname: KEYRING, IP: 004F:012E   <- suspended
Process 2901 GumpNotifyProcess, gump: 15333
```

`004F:012E` is the instruction immediately after the `suspend` that follows
`target()`. Then:

```
Target result: Item 14576 (shape 342) (uc: TDOOR_EW), (20351,3071,0) q: 1635
west leaf 14577: q 1635 (0x663) -> 611 (0x263)
east leaf 14575: q 1123 (0x463) ->  99 (0x063)
```

One key press unlocks **both** leaves. Screenshots `12`, `13`, `20`.

Double-clicking the door itself is *not* useless — it is how you open an
already-unlocked door, and while locked it correctly reports `Locked Door`
(class `0044` offset `08B4` → `0886` isLocked → bark at `0913`). Both
behaviours are retail-correct.

**Practical player recipe** (and the reason the doors need a note in the docs,
not a code change):

1. Open the chest in the bone field, drag the key onto the Avatar's sprite.
   Verify `total weight` went 20 → 30.
2. Stand within 128 units of a door leaf (y ≈ 3140–3170 at x ≈ 20300–20470).
3. Press `i`, drag the pack gump clear of the doorway, **double-click the key**.
4. Click either door leaf. Both unlock.
5. **Double-click a leaf** to swing them open.
6. Walk north.

---

## 4. The real defect: `"blocked"`

With both leaves unlocked, the first session still would not open them.
Double-clicking produced the bark **`blocked`** (`15-blocked-bark.png`) and the
leaves stayed shape 342.

### How a door opens

`TDOOR_EW::use()` (class `0156`, event 1) → `0044:08B4`. The relevant chain,
with `0x51` read correctly as **jump-if-FALSE** (`uc_machine.cpp:1270-1282`):

```
0987  Item::push()          on objid 1  -- the AVATAR is removed to the ethereal
                                           void so he can never block a door
0993  call 0044:016C        on SELF     -- try to open this leaf
099F  Item::pop()  + bark "blocked "    -- on failure, on SELF
09D5  ...                               -- on success
0A02  call 0044:016C        on PARTNER  -- try to open the other leaf
0A21  bark "blocked "       on PARTNER  -- on failure, on the PARTNER  <-- the one we saw
```

`0044:016C` computes the open shape/frame/position and calls
`FREE::2411` (`0581:2411`), which is a guarded type-swap:

```
2419  getFamilyOfType(newtype) == this.getFamily() ?   else bail
242F  Item::push()          -- take this leaf out of the map
2449  Item::legal_create(&probe, newtype, newframe, x, y, z)
2450  if it FAILED -> 248E (abort)      else destroy the probe and setType() in place
```

`Item::I_legalCreateAtCoords` (`world/item.cpp`) is the gate:

```cpp
PositionInfo info = cm->getPositionInfo(x, y, z, shape, 0);
if (!info.valid) return 0;
```

and `CurrentMap::getPositionInfo` sets `info.valid = (info.blocker == nullptr)`,
where a blocker is **any item carrying `SI_SOLID`** whose world box overlaps
the target box. `id` is passed as `0`, so nothing is exempted except the leaf
itself, which `push()` already removed.

Observed open geometry (read back live from the engine, not inferred):

| leaf | closed | open |
|---|---|---|
| west | shape 342 @ (20351, 3071, 0) | shape **340** @ (**20255**, 3071, 0), q 0x363 |
| east | shape 342 @ (20479, 3071, 0) | shape **340** @ (20479, 3071, 0), q 0x163 |

Shape 340 footpad is 1×4×10 = 32 × 128 × 80, so the open boxes are

```
west open : x(20223..20255]  y(2943..3071]  z[0..80)
east open : x(20447..20479]  y(2943..3071]  z[0..80)
```

### What was in the way

Exhaustive static check over **all** map-8 items — 4,317 in built
`FIXED.DAT` plus 584 from `NONFIXED.DAT` — finds **zero** `SI_SOLID`
overlaps with either open box. The doorway is a perfect fit: the flanking
stalagmites (shape 394) stop at x ≤ 20223 and resume at x ≥ 20480, and the
floor slabs (shape 301) have `zd = 0` so they never overlap anything.

The blocker was **dynamic**. In session 1 a single click at (780,330) returned:

```
Item 15302 (class Container, shape 411) (uc: GHOST), 9, (20470, 3130, 40) q: 0
```

Shape 411 is `SI_SOLID` (TYPEFLAG `2260306300010105`) with footpad 3×3×6 =
96 × 96 × 48, so its world box is

```
ghost : x(20374..20470]  y(3034..3130]  z[40..88)
```

which overlaps the **east leaf's open box** (x 20447–20470, y 3034–3071,
z 40–80) and not the west leaf's. That is exactly the observed failure: the
west leaf's own `016C` succeeded, the **partner's** failed, and the bark came
from the partner at `0044:0A21`.

It also explains the retest's odd side-observation that every click found only
the west leaf: the ghost sprite is drawn over the east leaf and wins the depth
sort. You can see it directly — compare `03-door-site.png` (session 1: a large
wispy grey apparition draped across the doorway, only one ring handle visible)
with `17-fresh-doorsite.png` (session 2, identical teleport: doorway clean,
both ring handles visible).

In session 2 no ghost was present, and the doors opened on the first
double-click.

### Is it ours?

**No.** Shape 411 has usecode class `GHOST`, objid 15302 was created at
runtime (dynamic id range, well above the map-load block), and there is no
shape-411 record in `NONFIXED.DAT` map 8 at all. The one shape-411 item we
place is the Lord British apparition backstop at (2200, 2326, 8) — 18,000
units away, frame 0, and its egg never hatched in either session. Bonecrusher's
cave is a base-game ghost haunt; the apparition wandered into the doorway on
its own.

Nothing in tonight's diffs, and nothing in the restoration at all, touches
this. It is retail behaviour: U8 doors refuse to open through a solid body,
and a wandering ghost is a solid body.

---

## 5. How 2026-07-02 did it

**It is not recorded.** There is no session document, devlog or commit message
for that run. The only artefacts are three restatements of the same claim —
`TODO.md:897`, `HANDOFF.md:772`, and
`agents/map-populator/docs/map-08-plateau-entry.md:44` — plus the
`MainActor::teleport 8 20430 3250 0` line. None of them says whether the key,
the keyring, or a cheat was used, and none records the interaction idiom.

That gap is what turned an intermittent ghost into a five-hour "blocking
regression": with no recorded method, the retest could not tell a wrong input
idiom from a broken door, and reasonably reported the worst case.

Sample size on the ghost is two sessions, one blocked and one clear, both
entered by the identical debug teleport. That is enough to call it
intermittent, not enough to put a frequency on it.

---

## 6. Recommendations

**Nothing to fix in code, data, or the map builders.** In priority order:

1. **Documentation — the fix belongs here.** Add the key recipe from §3 to
   `agents/map-populator/docs/map-08-plateau-entry.md` and to `HANDOFF.md`'s
   harness section. "Double-click the key in the pack, then click the door"
   is the single most load-bearing undocumented fact in this project, and its
   absence has now cost two sessions.
2. **Correct the three stale records**: `TODO.md:878` (the map-8 row's
   "REGRESSED OR ENVIRONMENT-DEPENDENT" verdict), the D'2 section of
   `docs/playtest-2026-07-31-retest-hardened-gates.md`, and the
   "class 0x4F, FLX entry 0119" misreading in `TODO.md:897` /
   `map-08-plateau-entry.md:35`.
3. **Record `blocked` as a known, retail-correct hazard.** If a player's doors
   bark `blocked`, something solid is standing in the doorway — usually a
   ghost. Kill it, or wait for it to drift off, and try again. Worth one line
   in the player-facing notes; it is not worth engineering around, and it
   cannot be engineered around from FIXED.DAT since the ghost is a runtime
   spawn.
4. **Two harness gaps, both of which cost time here.** Barks are transient and
   render at the top edge of the viewport — screenshot within ~0.5 s of the
   click, and look at the frame edge, not the item. And
   `debugflag_enable Object` should be part of the standard session setup:
   it makes every click print `dumpInfo()`, which turns "did my click land?"
   from guesswork into a log line. Both are worth adding to `session.sh`
   /HANDOFF.
5. **Also fix the stale docstring in `build_map_08.py`** (lines 20-32): it
   claims "WHAT WE ADD: 4x shape-342 leaves … Rock spires sealing the open
   floor at the doorway's flanks", none of which the code does — the function
   adds a chest, a key, four eggs, two slabs and the LB backstop, and line 77
   correctly says "WE DO NOT PLACE ANY DOORS". The docstring contradicts the
   code it heads. Cosmetic, but it is the first thing a reader hits.

---

## Disk changes

* `docs/playtest-2026-07-31-doors/` — 26 screenshots.
* This report.
* Nothing else. No source, map builder, artifact or config was touched, and no
  game was saved.
