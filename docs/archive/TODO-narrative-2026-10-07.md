# TODO.md narrative pruned 2026-10-07

Moved verbatim out of `TODO.md`'s Phase 4c section on 2026-10-07, under the
same rule as `TODO-full-2026-08-11.md`: the tracker carries open work and
short dated records; how each fix landed lives here. Statements in the
present tense below were true on their own dates, not necessarily now. The
items still open from these passages were re-filed in `TODO.md`.

## From the head of Phase 4c (was TODO.md:32-124)

**Where the quest stands (2026-07-31):** every quest-critical scene has
executed in ScummVM — steps 1–12 spine, the Passage Test with poison, the
Sacred Circle ceremony with the cure (14–15), the DD-005 shrink chain, and
the altar/endgame close (17–18). The route is walk-verified end to end, both
quest gates hold against the jump button, and all 11 teleport gateways are
bounce-audited. **The remaining tier is one continuous no-debugger
playthrough** — the exit test, run from the plateau save. See `HANDOFF.md`
for the next action.
**Exit test, 2026-09-02: steps 6-15 run unbroken; the temple is sealed.**
One continuous session, cheats off, every metre walked or climbed: Ragnar's
referral -> the Passage Stone -> the Passage Test -> Ezrekal -> Tyorvi and
Ingyald -> the root errand -> the Key to the Clouds -> the Cloud Cliffs ->
Cloud City -> both shield halves -> the Sacred Circle ceremony, which
restored the shield and **cured the poison** (`avatarPoisoned` 0,
`shieldFixed` 1). Checkpoints `cp8`-`cp24` (slots 24-40).

**What unblocked it, and it was corpus-wide.** `CONTAINER_FAMILY`,
`QUAL_FAMILY`, `QUAN_FAMILY` and `REAGENT_FAMILY` were declared nowhere, so
the compiler emitted `push 0` for each; `FREE::give`'s first guard read
`getFamily() != 0`, the Avatar is `SF_CONTAINER` = 6, and **give() returned
at its first instruction for every caller** — `take()` with it. Three quest
hand-overs had been delivering nothing: the Zealan Mark, Ezrekal's elixir and
the Key. Fixed by `FAMILY_CONSTANTS` in `u8c_symbols.py` pinned against
`ShapeInfo::SF_*`; size-neutral, estate 26/26, hashes re-recorded, detection
unaffected.

**STEPS 17-18 COMPLETE (2026-09-05).** The whole endgame ran in-engine:
Shield on the altar -> the Ancient Ones freed -> the restoration sequence.

    shieldFixed (0x409) = 1   templeOpen (0x412) = 1
    godsFree    (0x40E) = 1   endgameStarted (0x716) = 1

`EggAOCeremony` (q296 -> class 1447) played the full scene — stasis, SFX,
`FadeToWhite`, four barks, `FadeFromWhite` — and set `godsFree`; then
`EggEndgame` (q299 -> class 1450) at (18432, 22016) ran the Vale-healing
sequence and set `endgameStarted`. Checkpoint `cp32-endgame-done.sav`.
Record: `docs/playtest-2026-09-05-steps-17-18.md`.

**The "ceremony segfault" reported earlier was a misdiagnosis.** AOSCENE sets
`godsFree` only at the END of ~450 ticks of waits and barks, and **attaching
the debugger pauses the world** — so polling the flag froze the scene and
always read 0. The same pause explains the "wedged" Avatar: `AOSCENE::hatch`
opens with `setAvatarInStasis(true)`, which looks exactly like a teleport
wedge. The one real segfault never recurred; the full chain then ran under
`gdb -batch` with no backtrace. **Rule: let a cutscene run untouched, then
query.**

**The Bag of Reagents is now implemented (2026-09-05).** `ENDGAME.UNK`'s
elder beat creates a `TypeBag` (637), fills it with six `TypeReagent` (395)
stacks at frames 0/6/8/9/10/14 — the set ScummVM's own `Cheat::items` uses —
and pops it into the Avatar's backpack (`popToEnd(Avatar)` fallback, as
`FREE::give()` does). NOT `TypeBagOReagents` (225): SF_GENERIC, still the old
dining-table id, holds nothing. Verified in-engine: weight 290 -> 450, and
dragging one stack out drops it to 425. Quantity was tuned against the engine
— at `give()`'s 666 ceiling the Avatar hit 4296 against a 600 capacity and
could never pick anything up again; 25 apiece keeps him mobile.
Checkpoint `cp33-bag-of-reagents.sav`.

**Two follow-ups it leaves.** (1) It is a generous pouch, not the literally
endless "Bottomless Bag" of Plot v1.2 — a true one cannot be a stack; it needs
usecode that refills on use. Design call. (2) The six stacks share gump slot
(0,0) and draw on top of each other: `moveToContainer` zeroes the gump
position, no intrinsic exposes it to usecode, and only (255,255) triggers the
randomiser — inherent U8 behaviour for usecode-created contents.

**Resolved 2026-09-25: the restored Shield is handed over.** It used to pop
at `firePoint1 - (60,30)` and stay on the grass, so the 2026-09-02 run walked
off with a shape-332 `BONES3` skeleton and left the shield at (20480, 17148).
Douglas: "hand it over". `lv-patched/SHADES.UNK` change 14 moves it into the
backpack at the end of the scene, with a provisional Avatar bark. **Verified
in ScummVM 2026-09-25** from `cp22`: the bark shows, `findShape 539` finds
one frame-2 shield inside a container, nothing is left on the grass, and the
camera follows the Avatar for 2,430 units after the scene (`ef` carries
0x20). Record: `docs/playtest-2026-09-25-ceremony-plaques.md` (C, S).

**Steps 15-18 on HEAD, 2026-09-26** (`docs/playtest-2026-09-26-steps-15-18.md`):
one session from `cp22`, no debugger write, every step to the finale ran:
the ceremony cured the poison and handed over the shield, the camera
followed 8,000 units, the Tiny Tar entry set `templeOpen`, the altar freed
the gods, and the endgame gave the bag (`hasBag` 1, six stacks of 25). The
session broke once: ScummVM segfaulted about 10 s into the altar scene
(one run in three; two replays completed). **Cause found and fixed
2026-09-26**: AOSCENE played `RUMBLE1`, which is not a sound, so it compiled
to SFX 0, the sound-name table, and decoding that as audio read about
19,300 bytes past the buffer. Now `QUAKE3`; an ASan engine faulted 3/3 before
and ran 3/3 clean after, `godsFree` 1
(`docs/playtest-2026-09-26-altar-segfault.md`). **Re-run unbroken on the
fix, 2026-09-26: PASS.** One ScummVM process (PID 3024718, 03:04 to 04:32
CDT) from `cp22` to the finale, cheats off, no debugger write, every leg
walked: `avatarPoisoned` 1->0, `shieldFixed` 0->1, shield in the pack,
`templeOpen` 0->1, `godsFree` 0->1 with the pan, `endgameStarted` 1,
`hasBag` 1 (`docs/playtest-2026-09-26-steps-15-18-unbroken.md`).

## From the middle of Phase 4c (was TODO.md:483-843)

**Steps 16-17 walked: the Tiny Tar route into the Inner Sanctum WORKS
(2026-09-04).** On a fresh world, cheats used only to position: the pre-placed
q20 key was found and stowed, it unlocked Hrodny's chest (618 -> 78), the chest
opened on three Tiny Tar potions, one went into the pack, and it survived a map
change. At the crack, a **full-size Avatar pushed south four times and moved
zero units**; after drinking frame 8 (`TYPEPOTION` dispatched, class 0x04E5) he
became `shape 708 (uc: CHILD)` and the *same* three pushes carried him from
(2848, 6100) to **(2804, 6664)** — through the crack into the Inner Sanctum —
then `makeAvatarBig()` returned him to shape 1 alive, hp 31. DD-005 is
demonstrated end to end. **Still NOT demonstrated:** the rest of step 17 (Shield
on altar, gods) and step 18 (Bag of Reagents), which need the restored Zealan
shield from step 15 and so belong to the continuous-playthrough tier. Record:
`docs/playtest-2026-09-04-steps-16-17.md`.

**A crash was found and fixed on the way.** Contained records loaded from
`FIXED.DAT` came up WITHOUT `FLG_CONTAINED`, because the loader attaches them
with `Container::addItem()`, which never sets it. `Item::moveToContainer` only
unlinks from the old container when that flag is set, so the first potion taken
was in the chest AND the backpack at once, and the next map change freed it
underneath the pack — **ScummVM segfaulted**. Fixed data-side:
`MapItem.contained_item()` writes `flags = 0x0008`. Retail never hit this —
retail `FIXED.DAT` has zero contained records. `FIXED.DAT` rehashed
`2327ca70 -> 278a48c3`.

**The Tiny Tar is now in Hrodny's chest (2026-09-03, DD-005, RESOLVED).**
Decision taken: **containment** (option 1 of the three that were wanted). The
map writer gained `MapItem.contained_item()` — the FIXED format encodes a
record's x as its container depth, so three `SHAPE_POTION_REAL` (859) frame-8
potions placed directly after the chest record now load as its contents.
Verified in a freshly-built world: the chest reads
`class Container, shape 618, (21152, 8832, 0), q: 20, items: 3` (up from 0),
and zero Tiny Tar records remain on the ground. The crack at x 2817..2879,
y 6143, z 0..40 stays the only Inner-Sanctum route, sized for the 32-tall
shrunken Avatar; the shrink is wired (`POTION.UNK:145`, class `02FE POTION`).
Record: `docs/playtest-2026-09-03-tinytar-contained.md`. Key→unlock→open→stow
and the frame-8 shrink were already PASS in prior sessions; only "the potions
exist where the player finds them" was open, and it is now closed.

**Two more blockers fixed getting there.** `build_gunnar_village()` had
Hrodny's chest buried first in the hut's west wall column and then behind its
40-tall south wall — it now sits on open ground at (21152, 8832, 0). And
**no chest in the game could be opened**: all four chest classes compile
`if (intrinsic 254) { look() } else { openGump() }` and ScummVM stubs 254 to
`I_true`; the fork now maps it to `I_false` and the tracked engine patch was
regenerated (it was 21 lines stale).

**Also found**: the ceremony leaves the camera off the Avatar and he freezes
once out of the fast area (recover with `CameraProcess::moveToAvatar`). Cause
found 2026-09-25: LVFREE's `scrollBack` compiled to nothing; fixed as
`lv-patched/FREE.UNK` fix 2 (`docs/playtest-2026-09-25-ceremony-plaques.md`); both
Cloud Cliffs key-gates are inert and bypassable and Tyorvi's key has quality
0 against lock 170; and the Passage Test strands its witness NPC.

**Exit test, 2026-09-02: the chain runs from Ragnar to Ezrekal.** Continuous,
cheats off, every metre walked or climbed (the debugger only read state).
Ragnar's referral tree → the Passage Stone → the bag off the lakeside ruin
dais → the Passage Test → Ezrekal's door. `UCMachine::getGlobal` reads
`ragnarToldStone`, `haveMark`, `avatarPoisoned` and `firstPoisoned` all set,
and Ezrekal — who refused an unmarked Avatar the day before — opens with
*"the Mark you bear!"*. Checkpoints `cp8`-`cp12` in `~/lv-checkpoints/`
(slots 24-31), ending at `cp15-cliffs-lead`. Also verified in the same run:
Tyorvi and Ingyald (`ingyaldMet`/`ingyaldJob`/`tyorviMet` all set), Tyorvi's
menu growing "I have spoken to Ezrekal." with follow-ups matching what she
actually said, and Ezrekal's cliffs/Key-to-the-Clouds thread. Record:
`docs/playtest-2026-09-02-quest-chain.md`. Three things it changed:

- **Two ascents were climbs, not walks — RESOLVED.** Ragnar's bag could not
  be taken from the ground (the drag was refused and the item snapped back):
  it needed the z=24 → 48 dais climb, and each test-grounds terrace riser
  left a 32-unit band nothing could stand in. The 2026-09-15 landscape pass
  re-stepped both onto the ±8 lattice, and the 2026-09-18 walk confirmed it
  in the engine: the cache stair carries the Avatar to the crown at z=56 and
  the corridor ramp to the plateau at z=72, each in one walk-gait run with
  no jump and no stall (`docs/playtest-2026-09-18-map10-walk.md`).
- **`pathfind.py` treated water as floor** and drowned the Avatar twice.
  Fixed with `DryMixin` plus a 128-unit shoreline margin (`--water-margin`,
  `--allow-water`, and `--step-z` to expose the model's step limit).
- **Two RAGNAR quirks confirmed live**: the `No, I don't.` label collision
  closes the Stone thread with the Hrodny rebuke, and `Her body was eaten?!`
  is a permanently dead menu entry. Both were already listed as known-unfixed
  in the file header; neither had been seen in the engine before.

**Exit test, 2026-09-01: one leg advanced.** From `cp3h-west-strip` with
cheats OFF and no teleport, the Avatar walked map 8's south cave and made
**the cave ascent organically** (z=0 → z=56) — the first time that has been
done from a walked-in position rather than a debug teleport. Checkpoint
`~/lv-checkpoints/cp3k-cave-ascended.sav`. Two new tools made it possible:
`tools/playtest-linux/pathfind.py` (BFS waypoints over exact_reach's
lattice — straight-line chasing wedges three times in that cave) and
`walkto.py`. From there he walked ~4,900 units
further south through the trench, **climbed the 48-unit gate wall** with the
same SPACE-then-direction technique, dropped into the corridor and took the
map-8 south teleport out onto the plateau at (14686, 11210, 48) —
checkpoint `cp3l-through-gate`. He then crossed most of the
plateau westward (~5,500 units) to (9258, 12854, 48) — checkpoint
`cp3m-plateau-west`. Two deaths on the way, both from the WALK gait:
`nav.py` already warned "walkers die to chasers" and `walkto.py` had been
written at 130 not 240. It now runs by default, picks the gait per hop
(a run gait cannot stop inside 96 units, so short hops were being skipped)
and reports damage. `tools/playtest-linux/fight.py` is new — combat read
out of `handleCombatMode` (`c`, then double LEFT click, direction from the
cursor, `25 - dex` frame cooldown); its target selector must take the
NEAREST CombatProcess actor, since the first one listed was a ghoul 22,241
units away. The wedge there was a **one-lattice-row
seam**: sampled at step 4, y=12863 is a single open 4-unit row between two
wall blocks — the half-open-box aperture hazard `.claude/rules/map-geometry.md`
exists for. `pathfind.py` gained `--erode N`, which shaves N cells off every
walkable edge and makes that query correctly return NO PATH while still
finding the real route (south to y~13095 first).

**Map 8 is three regions joined by teleports, and the egg table is
misread.** The plateau's westward corridor puts the Avatar on a teleporter
that lands him in a NORTHERN region (x 12815..16495, y 3087..9775) — an
intra-map shuttle whose other end sends him straight back. `npcnum` on
these base-game eggs is NOT the destination map (two of them, npc=69 and
npc=68, both landed him back on map 8). The Mythran region — `cp4` sits at
(2900,3000,0), x 503..7215, y 503..3631 — is entered only via TARGET q=20
at (6078,1786), and map 8 carries no trigger with quality 276. **Read the eggs off `mapnum`, not `npcnum`** —
`mapnum` is the destination map and `npcnum` is the hatch range
(`Map::loadFixedFormatObjects`, `TeleportEgg::hatch`). Map 8's only exit is
id 1 at (31871,19167) to map 7; everything else is an intra-map shuttle.
Scanning all 49 maps with data, **nothing anywhere triggers map 8's targets
id 20, 22 or 30**, so the Mythran region is not entered by teleport, and an
un-eroded flood from cp4's (2900,3000,0) reaches x 407..7223, y 407..3639
and nothing else.

**The exit test has never been runnable, and the reason is on the record.**
`docs/playtest-2026-08-16-lb-mythran.md` marks two bypasses on this
stretch: the ascent (teleport-bypassed) and the **electric gateway
(LITZAPNS) — "NOT DEMONSTRATED, the Avatar got stun-pinned in the arc"**
(zapper item 4748 at (30879,24383,56); only floor passage x~30815 beside
it). The exit test is the run with no bypasses. This session removed the
first bypass, and the trench route it found goes south at z=0 without
approaching the zapper — which may retire the second. **But the gateway route needs its own
ascent, and that one still fails.** `cp3i-gate-approach` (30405,23581,8) ->
`cp3j-past-gate` (30815,24520,56) was ALSO a teleport bypass: a flood from
cp3i reaches z=0/z=8 only and never the z=56 gate shelf. The shelf is a
different component from the ascent pocket this session reached. There are
83 north-, 27 south- and 6 west-facing genuine 48-unit faces from the
walkable trench onto it (stacked underpass floors filtered out); tested at
two with the corrected SPACE-then-direction recipe, the Avatar takes a
plain jump from ~54 units clear and does nothing at all when flush —
F1's result again, with the right key order. The trench window does NOT
transfer: there the target is an overhang approached from z=0 void, where
the body may overlap the ledge footprint; a solid 48-high wall admits no
overlap. All three remaining ideas were then tried and all
three failed: the south face gives a jump (ended (30305,23909,0)), the west
face gives a jump off the ledge, and the running jump CANNOT climb by
construction — `lastanim == run` selects `runningJump` in the branch before
the climb scan. The hang grab does not apply at all: `AvatarGravityProcess`
needs `MOVE_ANY_DIRECTION`, settable only on the ground, and grabbing this
shelf would mean falling past its face when the shelf IS the top.
**Every input route into the climb branch has now been tried at this face
and the engine will not climb it** — F1's "the blocker is map geometry, not
input" survives the input fix that overturned the rest of its findings.
**And the ascent pocket does not reach the gate shelf**: flooding both in
one ROI gives 4,864 vs 61,373 cells with ZERO in common, closest approach
96 units at (29663,24399)->(29759,24399), same z, same y — and that 96 is a
WALL, not a void: standing jump falls short, running jump slides along it,
`hop.py`'s targeted jump cannot resolve a target there, a manual
both-button chord at the projected pixel only turns him, and all four
walking directions are blocked. So the ascent opens a dead end. The seam is a WALL INSIDE A GLOB —
a raw FIXED.DAT scan shows only two harmless 32x32x8 blocks, but the
EXPANDED blockers carry one at (29695,24447,56), box 32x128x48, spanning
x (29663,29695] y (24319,24447] z [56,104). **Scan expanded items, not raw
ones, before concluding anything about map 8.** That is why the naive
remedy failed: 1-4 shape-301 slabs at x=29759 leave the pocket at exactly
4,864 cells, because the floor was never the problem. At x=29695 the z=56
level is standable only for y 23743, 23935, 25151..26239, 26335..26599 —
the seam opens ~550 units SOUTH of where the pocket ends (y=24607). The
pocket is bounded on all four sides. Removing the wall is not a one-item
edit (it is glob-sourced), and any fix must be WALKED in-engine, not
certified by a flood — this session caught the model wrong in both
directions on this map.
**FIXED 2026-09-01 — and it is the project's first deliberate deviation
from retail TERRAIN, so review it.** `build_map_08.py` now sets
`BASE_ITEM_REMOVALS = {(29695, 24575, 56, 2)}` (glob egg 933) and
re-places its other 20 items verbatim via `seam_glob_replacement()`. The
one item not put back is the seam wall, shape 32 frame 1 at
(29695, 24447, 56) — opening a 128-unit doorway in a north-south wall
column. Static: the pocket goes 4,864 -> 66,336 positions and reaches
(30815, 24520, 56). **Walked in-engine on a fresh world** (checkpoints do
not see FIXED.DAT changes): careful-steps east carried the Avatar
29600 -> 29664 -> 29696 -> 29728 -> 29760 -> 29795 -> 29823, all z=56,
straight through the seam; then on foot to (30847, 24582, 56) — cp3j's
position — **past the electric gateway's fence at y=24383**, hp 30 -> 21,
one LITZAPNS zap and through. Checkpoint `cp3n-past-gateway.sav`.
**Both bypasses on this stretch are retired**: the ascent (walked, cp3k)
and the gateway (passed on foot, cp3n). **A SECOND seam exists at y=26399** and is real
in-engine (from cp3n the Avatar walks to (30407,26366,56) and wedges), so
the shelf does NOT reach the cave mouth at y~29100. It is an east-west wall
run inside glob 936, egg (30719,26623,56): shape 26 fr 7 at (30463,26399,56)
and (30591,26399,56), both 128x32x48, plus shape 32 at (30623,26399) and
shape 29 at (30335,26399). **DONE, same one-item pattern**: glob egg 936
also removed, `seam2_glob_replacement()` re-places its other 36 items and
omits only the shape-26 at (30463,26399,56). Shelf 66,336 -> 221,491
positions. Walked cheats-off (30400,26200,56) -> (30400,28960,56) -> 
(30400,30424,56), hp 30 throughout — checkpoint `cp3o-cave-mouth.sav`.
**THE SOUTH CAVE IS NOW TRAVERSABLE END TO END ON FOOT**: ascent, first
doorway, electric gateway, second doorway, cave mouth. A whole-map flood
from the mouth still reaches NONE of Mythran (1503,1791), the LB egg
(2200,2230), cp4 (2900,3000), the doors (20447,2751) or map 8's only
off-map exit (31871,19167) — so **the Mythran leg is the one nobody has
ever walked**, and cp4 was almost certainly a debug teleport like the two
bypasses either side of it. **The disconnection is RETAIL's, not ours**:
flooding map 8 from the map-7 arrival against the pristine `FIXED.DAT.bak`
and against our build gives the same 6,652 cells, neither reaching Mythran,
cp4 or the doors — the LV build is cleared of walling anything off.
In-engine the Avatar reaches (29503,19815,0) from cp3-plateau and stops;
x~29503 is that region's western boundary. **It is a SCRIPTED TELEPORT.** NONFIXED.DAT
(from SAVEGAME/U8SAVE.000) holds ZERO teleport eggs, so the FIXED.DAT egg
graph is complete; and EUSECODE.FLX calls intrinsic 158 (Actor::I_teleport)
in 58 of its 1,460 classes. The base game moves the Avatar by script
constantly, so a region with no walking route and no egg is not a broken
map — it is one the game scripts you into. **This reframes the exit test**:
it is a NO-DEBUGGER playthrough, not a no-teleport one — the game's own
scripted teleports are the game, and a bypass is `MainActor::teleport`
typed at a console. The Mythran leg is "trigger the scene", not "walk
29,000 units". **FOUND**: FLEX entry 625 = class 0x026F
"NEC1" carries `Actor::I_teleport(..., 2399, 2207, ...)` at offset 0x11c6 —
(2399,2207) is inside Mythran's region and **200 units from the LORDBRIT
backstop egg** our builder placed at (2200,2230). NEC1's strings are
Necromancer/Lithos dialogue. So the region is entered by an NPC
conversation that teleports you, which is why no flood found a path, why
nothing triggers targets 20/22/30, and why the pristine map floods exactly
like ours. **The Mythran leg of the exit test is "trigger NEC1's scene"** —
the game's own transport, not a bypass. Caveat, checked: NEC1 has NO
placement — shape 623 is in no map's FIXED.DAT and in none of
ITEMCACH.DAT's 255 NPC slots, so the class is spawned or scene-driven and
*where* you meet it is still open. Traced: NEC1 references only itself, nothing
spawns it, so it may be dead content and that teleport a false lead.
**Mythran is NPC 33**: ITEMCACH.DAT has exactly one NPC on map 8 — npc 33,
shape 190, at (1503,1791,0) — and U8 gives an NPC class `0x400 + npcnum`,
so 0x421 = MYTHRAN. The builder's inferred position was right and he
stands inside the unreachable region, while the game's own book says you
walk there ("I took the leisurely stroll up to the Plateau… this old man,
Mythran is his name"). **RESOLVED — the "isolated" reading was
WRONG.** Between Mythran's region and the doors region there is no wall,
just a ~1,000-unit VOID (standable ground runs x 6527..7199 and
x 8255..13471, nothing between); the strict model refuses to walk it and
the engine does so happily on the same z<=0 support that carries the Avatar
across the trench. Walked cheats-off from (8400,2500,0): 8400 -> 7816 ->
6848 -> 5880 -> 5036 -> 4268, all z=0, hp 30, into Mythran's region, then
round his house to (2056,2624,0) — ~900 units from him. Checkpoint
`cp3p-mythran-region.sav`. **QUEST STEP 5 EXECUTED 2026-09-01**: from `cp5b`, walked to NPC 107
(Atli) at (18811,5779,0) cheats off and opened his conversation —
`Item: 107 calling usecode event 1 @ 046B:036C`, i.e. class 0x400+107, his
own. Played organically through *"A Pagan are you?"* → name → Britannia →
*"the other side of the barrier"* → his Hoskuld-spy accusation → denial.
That is step 5 ("Meet the Zealans") plus step 6's clan suspicion in his own
voice. Checkpoint `cp5c-atli-spoken.sav`. Then walked 13,600 units west to the
village cluster and played **RAGNAR** (NPC 105) the same way: name → "from
very far away" → "come in peace do you?" → the Gunnar/Huskuld clan war →
**"I have no fight with you"**, which dispatched and left the menu —
**DD-008 VERIFIED LIVE**, the option this file records as dead in the 1994
snapshot and restored in `lv-patched/RAGNAR.UNK` on 2026-07-04. Checkpoint
`cp7b-ragnar-spoken.sav`. Then **THORDIS** (NPC 106) at (6268,6592,0):
"Thordis, I am. After my great-grandmother named I was." and "Home of the
Hrodny's, it is... keep it safe, we do, from those dung-beetle Gunnar's."
Checkpoint `cp9b-thordis-spoken.sav`. **Three quest NPCs, cheats off, in
one continuous run from the Vale entry — steps 5-7 content, with the clan
feud heard from all three sides. The rest is the same work repeated.**

**Next: find the compound entrance.** Flooding
from Mythran's own tile gives 23,807 positions (x 1119..3103, y 1119..2527)
with a staircase inside (z 8→16→24→32→40 at x 1471..1847, y 1599..1663) to
a 27,972-cell z=48 floor. The Avatar's region comes within 96 units —
(2623,2527) to (2527,2527) — and that 96 is walled. Tried west at y=2527,
north at x~2624, and the east side (region reaches x 3103 at y 1631..2015):
reached (2688,2112,0), blocked north and west, ~1,200 units from Mythran.
Checkpoint `cp3q-mythran-compound.sav`, then (3144,1736,0) on the east face
(`cp3r-compound-east.sav`). **THERE IS NO ENTRANCE — Mythran's house is a
FLOATING ISLAND IN THE VOID.** Teleporting in for a look
(`docs/playtest-2026-09-01-stock-bindings-climb/D1-mythran-island.png`)
shows a timber hall on a wooden deck whose rock underside hangs in a
starfield. That explains every measurement above: the region is isolated
because you cannot walk onto an island; nothing triggers targets 20/22/30
for the same reason; the pristine FIXED.DAT.bak floods identically because
nothing is broken; the "compound wall" is the island's edge. **And the
earlier claim that the Avatar WALKED into Mythran's region is WITHDRAWN** —
he was walking BENEATH it on the engine's z<=0 freebie support, over the
starfield. So the leg is a scripted arrival. Narrowed but
NOT found: decoding every `calli … 158` and filtering to the island's
bounds leaves exactly two classes and neither is the transport — 0x006D
**PYROS** → (1245,1245), the Titan of Fire's summoning scene, and 0x026F
**NEC1** → (2399,2207), which has no placement and nothing calling it
(likely dead content). **MYTHRAN's own class 0x0421 contains no teleport at
all.** So the island holds Mythran's house AND a Pyros summoning spot, and
the way onto it is not a single teleport this scan can see — answering it
means playing retail U8 or reading the early quest's usecode in order. Douglas: bless or revise BOTH terrain edits;
they are two items, fully reversible, documented in the builder.

**Correction to `docs/engine-2026-08-18-f1-segfault.md`**: "the ascent is
genuinely required… there is no way around" is WRONG. The z=56 floor the
ascent reaches is a pocket (x 29223..29663, y 23591..24607, one climbable
exit, back north). The route continues from the TRENCH FLOOR: modelled with
the engine's own `z <= 0` rule the gate approach is reachable from cp3h with
no climb in the path at all. What it does need is several thousand units of
walking across floorless void — the project's own blackness rule. Record:
`docs/playtest-2026-09-01-stock-bindings-climb.md`.

**Exit-test rehearsal progress (2026-08-16/17): THE 18-STEP CHAIN RAN END
TO END IN-ENGINE.** Steps 1-6 verified (1-2 and 5-6 fully organic), the
Passage Test ran complete (haveMark + poison), Ezrekal delivered the
Cloud City reveal, both shield halves were recovered from Cloud City, the
Sacred Circle ceremony played with organic mediation (reforge +
shieldFixed + THE POISON CURE), templeOpen fired (the flag 1994 never
wrote), the altar ceremony freed the gods (godsFree), and the EggEndgame
finale played to its closing fade. Bypasses were used and documented
where content bugs block the organic path — the two big ones: **zd=0
tile footpads make every raised floor unwalkable** (the whole Cloud
Cliffs climb; fix in the TYPEFLAG patch step) and **unbounded NPC
loiter** (Ragnar in coordinate wraparound; Tyorvi roof-occluded). Steps
7, 9, 11-12 still need their organic arcs after those fixes. The
Passage-Test "stall" reported earlier in the night is WITHDRAWN
(harness-induced). Resume from cp15-endgame-done. Records:
`docs/playtest-2026-08-16-pool-crossing.md`,
`docs/playtest-2026-08-16-lb-mythran.md`,
`docs/playtest-2026-08-17-vale-steps-3-8.md` (all four parts).

**2026-08-17 (day): steps 11-12 COMPLETED organically** on the repaired
usecode (E5/E6 + T1, both PROVISIONAL): Ezrekal poison/funeral tiers →
Hrodny toldCliffs → Tyorvi agreeToClimb → sentToTyorvi → nightmares →
tyorviDreams → root fetch → elixir/hasTea → tea delivery → **Key to the
Clouds given** (givenTea=1, cp23-key-to-clouds). Steps 7 and 9 were
already organic (part 3); of the original organic-arc holes only the
testFromThordis decision (step 9's zealanMark tier) remains open. Part 4
of the same report has verdicts, F17/F18, and flag state.

**2026-08-18 — F10 CLOSED, and its recorded diagnosis was wrong.** The
Cloud Cliffs climb walks. The filed cause (zd=0 footpads starve the mover
of support; fix by bumping zd 0→1 in the TYPEFLAG patch step) is REFUTED:
`getPositionInfo` reads support off an item's TOP face, so a zd=0 tile
does support standing at its own z, and bumping zd would have given every
path tile an 8-unit box overlapping the Avatar's body — turning the whole
ramp into a wall. TYPEFLAG was not touched. The real rule is that
`scanForValidPosition` probes an ENUMERATED table,
`SEARCH_OFFSETS_U8 = {0, -4, 4, -8, 8}`, so a walking actor can change z
by 0, ±4 or ±8 and nothing else; the 2026-07-31 rebuild's 1- and 2-unit
risers were as impassable as the 9-unit seams it replaced.
`exact_reach.py` and `test_route_reach.py` both encoded the same wrong
"anything up to 8" reading — corrected, and the corrected model reproduces
F10 statically for the first time. **F11 — CLOSED, verified in-engine.** Every capacity branch of
`Container::CanAddItem` was ruled out with data (pack held 3 items
against capacity 175; weight 110 against a limit of 600). The defect was
geometry: all three Tiny Tar potions were INTERPENETRATING solid boxes —
the locked chest (618) and the furniture beside it (526) both span
z [0,16) and the potions sat at z=4, i.e. buried inside them, which
defeats `canReach`'s line-of-sight sweep and the drop trace. Moved to
clear floor beside the chest. Verified 2026-08-18 in ScummVM: the potion
stows — `"Dropped item in backpack"`, Avatar total weight 20 → 30 (the
potion's exact weight), item flags 0xc (contained). An intermediate fix
that put them on the furniture TOP was rejected: resting a small box on a
tall neighbour's top face made the depth sort unresolvable
(`Cycle in paint dependency graph 859 -> 526`, ~11,000 times in seconds).
Record: `docs/playtest-2026-08-18-f10-climb.md`.

**Verifying a map fix from a savegame does not work.** A save carries its
own instantiated map, so loading cp24 restored the OLD potion positions
and the fix appeared not to have taken. Map placement changes are only
visible on a world built fresh from FIXED.DAT.
