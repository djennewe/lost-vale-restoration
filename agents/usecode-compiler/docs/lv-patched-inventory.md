# `lv-patched/` inventory

What each patched file changes and why. Moved out of `CLAUDE.md` on
2026-08-11 — it had grown to 28 lines there and had gone stale twice (commit
`012b907` exists only to correct its file count).

The standing rule lives in `.claude/rules/recovered-source-is-evidence.md`:
the recovered 1994 source is read-only evidence, and a fix goes here as a
byte-copy plus one documented minimal change. **When you add a file to
`lv-patched/`, add a row here.**

Precedence: `lv-patched/` outranks the same basename in
`shared/data/lv-usecode/` (both the `LOST VALE/` and `UNK files/UNK/` tiers).
The skip is by basename and automatic — you never edit or delete the original
to make a patch take effect.

**Currently 17 files.**

---

### Encoding fidelity restored (2026-09-05)

`ATLI.UNK` and `EZREKAL.UNK` were **not byte-copies**. A lossy re-encode had
replaced every high-bit character in their German and French dialogue with
U+FFFD (`ef bf bd`) — 527 characters over 372 lines in ATLI, 838 over 584 in
EZREKAL. The recovered files are CP437 (`0x94` = o-umlaut, `0x82` = e-acute),
so the original characters were destroyed in the patched copies.

**No gameplay impact:** the compiler strips `\f`/`\g` language sections, so
the German never reached `EUSECODE.FLX` (verified — zero occurrences of
"Seid"/"gegr" in both the built and the retail FLX). It was purely a
corruption of the archival evidence, which the byte-copy rule exists to
prevent.

Both files were restored line-by-line from the recovered originals on every
line that differed *only* by encoding, leaving their documented edits
untouched. Both now diff against their originals with **zero encoding-only
differences** and only their documented hunks. If you regenerate a patched
copy, copy the BYTES; do not round-trip the text through UTF-8.

### Schedule destinations retargeted (S1, 2026-10-08, Douglas's decision)

Seven patched files (`ATLI`, `EZREKAL`, `RAGNAR`, `TYORVI`, `THORDIS`,
`HRODNY`, and the new `INGYALD`) plus `lv-new/SIGRID.UNK` change only the
x/y/z literals of their two `schedule()` destinations; slot timing is
untouched. The 1994 points belonged to a Map 10 that no longer exists (void,
lake, bare ground at z 64 over z-0 ground; `docs/playtest-2026-10-07-wave1.md`),
which is why retail METHOD `safeTeleport`/`canSafeTeleport` were held out of
`u8c_symbols.METHOD_ROUTINES` (as `DEFERRED_METHOD_ROUTINES`) until this
change. They are called for real now. Retail teleports to the point exactly as
written once the Avatar is over 700 units from the NPC and the point, so
`agents/map-populator/src/test_schedule_destinations.py` reads every
destination out of the built `EUSECODE.FLX` and checks it with `exact_reach`
on the built `FIXED.DAT` (standable at its z, not over the lake, reachable
with 64 units of clearance). Each file's header carries its own S1 entry
(RAGNAR numbers it 13); the points:

| NPC | slot (periods) | 1994 point | new point | place |
|---|---|---|---|---|
| Atli | "Eating" (daytide, eventide, threemoons) | 18943,19711,64 | 19615,9855,0 | east edge of the Gunnar crop rows (HRODNY's and INGYALD's "Where is Atli?" say "in the field" at daytide) |
| Atli | "Lab 1" (firstebb, lastebb, bloodwatch) | 18175,20095,64 | 19231,6943,0 | outside his hut's south door |
| Ezrekal | inside (daytide, eventide, bloodwatch, threemoons) | 19327,29439,64 | 12799,12543,0 | in the stockade, at the bedroll |
| Ezrekal | outside (firstebb, lastebb) | 18431,29311,64 | 12895,13439,0 | the herb garden south of the stockade |
| Ragnar | home (eventide) | 14207,13055,64 | 5439,10527,0 | south of the Hoskuld edge hut |
| Ragnar | in the field (the other five; he hunts) | 13695,19071,64 | 7039,17151,0 | the west clearing south of Hoskuld |
| Tyorvi | home (daytide, eventide, bloodwatch) | 11519,14079,64 | 7423,7519,0 | east of the Hoskuld spring hut; his map start moved here too |
| Tyorvi | at stash (threemoons, firstebb, lastebb) | 13695,15743,64 | 21823,8031,0 | south of the Gunnar still-house by the still kettle, 192 units west of Ingjald's still point (was 22335,7647,0 until 2026-10-09, see below) |
| Thordis | in the fields (daytide) | 12904,13976,64 | 5247,9343,0 | the Hoskuld farm plots |
| Thordis | at home (otherwise) | 11052,12724,64 | 4415,7423,0 | in front of the Hoskuld Elder's hut |
| Hrodny | at work (daytide) | 17506,22354,64 | 22015,10143,0 | the Gunnar workshop's work station |
| Hrodny | at home (otherwise) | 17686,21806,64 | 21759,8447,0 | east of her hut's door, her map start |
| Ingjald | at the still (daytide) | 19935,19775,64 | 22015,8031,0 | the Gunnar still station |
| Ingjald | at home (otherwise) | 18175,20639,64 | 20767,7455,0 | outside his hut's south door |
| Sigrid | hunting grounds (daytide, firstebb) | 13500,16000,64 | 5503,16383,0 | the west clearing south of Hoskuld |
| Sigrid | home (otherwise) | 12000,13500,64 | 4895,8991,0 | south of the Hoskuld Hunter/Farmer home |

The same day `build_map_10.py` moved four map starts onto (one unit from) their
home points, so a new game starts each NPC where the schedule would put it:
Tyorvi (19456,8960 in Gunnar -> 7424,7520), and three starts that were inside
solids — Thordis (6144,6656, the Hoskuld keep's corner -> 4416,7424), Ragnar
(5120,8704, Hut 3's wall -> 5440,10528) and Ingjald (20736,6912, his hut's
chest -> 20768,7456). `SHADES.UNK` change 7 sends the elders home to these
points too. The test also checks the eight starts and all six EggShades
teleports.

Tyorvi's stash point moved on 2026-10-09 from (22335,7647,0), east of the
still-house, to (21823,8031,0). The first point passed all three checks, but
the Gunnar south-east cliff (104 tall from x 22528) is drawn over everything
within about 380 units west of its foot. Tyorvi showed inside the rock and
could not be clicked (`docs/playtest-2026-10-09-schedules.md` finding 2). The
test now has a fourth check: `item_sorter.ItemSorter.overdrawn`, a port of
the engine's paint sort with real sprite pixels, must find at most 10% of the
NPC's sprite covered. It reads 100% at the old point and 0% at every point now
shipped.

Thordis's post-Passage-Test exit is her ordinary schedule: once the scene end
clears `plantScene`, the next scheduler run with the Avatar 700 units away
moves her off the z 64 plateau to one of her two points; when her own
self-heal clears it (THORDIS change 6), the same run does.
Atli's schedule, which has no `canSafeTeleport` guard, does the same for him.

## `EZREKAL.UNK`

Quest 9-12 poison-cure repair.

Also carries the `givenElixir` vial-dupe fix (L22): the guard revert had
re-opened a duplication window for mid-window saves. Closed, not merely
reverted.

E5/E6 (2026-08-17, PROVISIONAL — review wanted): one-token writes
`spokePoison = true;` / `spokeFuneral = true;` at the "I have been
poisoned." / "But I'm dying!" cases. The flags were declared (FLAGS.UNK)
and read (TYORVI, HRODNY) but had NO writer in the 1994 corpus, dead-ending
steps 11-12 (F15). Same pattern as testFromThordis / DD-008. Verified
in-engine 2026-08-17: full arc played to the Key to the Clouds.

B1 (2026-09-26, restoration addition): the Bag of Reagents. The "I have
freed your gods!" case barks "A magical bag it is... Take it" and, in
1994, gave nothing. The hand-over (a TypeBag of six reagent stacks of 25,
then `hasBag = true`) was moved here from `lv-new/ENDGAME.UNK`, so the bag
comes from Ezrekal as the dialogue has it. Verified in ScummVM 2026-09-27
(`docs/playtest-2026-09-27-bag-ezrekal.md`).

B1a (2026-09-30, duplication fix): one line, `bag.setQ(1);`, added right
after `bag.create(TypeBag, 0);`. `docs/playtest-2026-09-29-endgame-egg-
pad.md` finding 4 showed the old `topUpReagents` rule minting unlimited
reagents: splitting a stack onto the ground and waiting put the bag's
remaining stock back to 25 every time, for free. The rewritten rule in
`lv-new/ENDGAME.UNK` needs to find this one bag among whatever TypeBag
items the Avatar carries; an npcnum cannot be assigned to an item created
at runtime, so quality is the only tag available. Ragnar's and Hrodny's
TypeBag/637 bags never set a quality (both read 0 in ScummVM on
2026-10-03, carried in the pack), so neither can collide with this tag.

B1b (2026-10-02, comment only): the header now says `topUpReagents`
refills the bag's stacks 5 per poll up to 25 and recreates a missing frame
at 5 (a slow refill, so dropping reagents on the ground cannot farm 25 per
poll). No code line in `EZREKAL.UNK` changed.

**W1-W3 (2026-10-08, Douglas's decision): the brewing wait is back.**
E1/E2 (2026-07-05) had flattened the 1994 flow to an immediate hand-over
because the patience option was dead: its add read "Is Tyorvi's elixir
ready?" and its case "...ready yet?". W1 restores the add (original line
380) spelled "...ready yet?" like the case; W2 restores the 1994 gate on
"Have you made the elixir?" (line 391, `and (justGotRoot = false)`); W3
(restoration addition, after line 3174) has the root case swap "I have
found the root." for the patience question in the same menu. So: root in,
patience barks while `justGotRoot` is set, hand-over once her
`leaveFastArea` (line 118) clears it as the Avatar walks away. Each state
offers one of the two options, so it cannot dead-end. A map switch skips
`leaveFastArea`, but `CurrentMap::loadMap` clears every NPC's fast-area
flag and enters it afresh on return, and a reload restores the fast area
from the save, so either way the next walk away on Map 10 clears it. The E3/E4
`givenElixir` replay guard is unchanged. `test_uc_dialogue.py` D12c drives
root → patience → `leaveFastArea` (event 0x10) → hand-over.

**V1 (2026-10-08), SUPERSEDED 2026-10-09 by V3 below: the elixir is frame
5, not 13** (lines 3233 and 3236,
with `TYORVI.UNK` V1). Frame 13 of shape 395 draws as a blue-grey shard
(retail `look()`: "sliced executioner's hood"); frames 0-5 are red vials.
All six are the necromancy reagent Blood — retail class 395's `look()`
reads "N vial(s) of blood", no LV class overrides it (built class 395 is
byte-identical to retail), and ScummVM's `Item::canMergeWith` merges
frames 0-5 of 395 with each other. Frame 0 was the audit's suggestion and
was rejected: it is the frame the Bag of Reagents stocks (B1) and the
commonest blood frame in the base game's NONFIXED (13 of 32 vials), and
TYORVI's recursive drink filter destroys every item of the elixir's frame
in the pack. Frame 5 has 3 base-game placements. D12c/D12d read both
frames back out of the compiled classes.

**S1 (2026-10-08):** schedule destinations retargeted; see "Schedule
destinations retargeted" near the top.

**V2 (2026-10-08, verifier finding):** the same two calls pass quantity 1,
not 0 (`FREE::give`/`createNear`'s last argument is the quantity). With 0
the vial looked "0 vials of blood" and landed at gump (0,0)
(`docs/playtest-2026-10-08-batch-a.md` finding 1).

**V3 (2026-10-09, Douglas's decision): the elixir is shape 868 frame 0.**
Lines 3233 and 3236 pass frame 0, with `TYORVI.UNK` V3, and `TypeBottle`
now resolves to 868 in `u8c_symbols.TYPE_SHAPES`: the elixir's own
one-frame vial (395 frame 5 recoloured sea-green, `lv_art_props.py`) on
donor 180's `SF_GENERIC` TYPEFLAG row, with class 868 (`lv-new/ELIXIR.UNK`)
barking "Tyorvi's elixir" (`docs/art-track.md` contract 11). V1's frame 5
was Blood: the elixir read "1 vial of blood", merged with carried blood,
and the drink destroyed carried frame-5 blood. V2's quantity 1 stands, and
matters more now: for a non-quantity family `FREE::give` runs `quan--;
while quan`, so a 0 would create items until the pack refused one.
D12c reads shape, frame and quantity out of the compiled calls.

**R1 (2026-10-09, Douglas's decision): the patience answer always
speaks.** The "Is Tyorvi's elixir ready yet?" case (original line 3182)
rolls `ran = urandom(3) + 1;` instead of `urandom(4)`. `urandom(n)` is
0..n-1 (`UCMachine::I_urandom`) and the case barks only for 1-3, so one
pick in four said nothing. Retail `MORDEA.UNK:906` rolls the same way.
D12c drives the case with every value the roll can return
(`UCSim.urandom_script`) and requires a line each time. Her "bye" case
(original line 3252) has the same `urandom(4)`-against-1-3 shape and is
left alone: not in the decision.

**M1 (2026-10-10): two reachable menu near-misses.** The case "The Ancient
Ones are in Britannia" (original line 780) gains the period its add (768)
and removals (785, 801) have, and the removal "How can I awaken the
Ancients." (1561) ends in "?" like its add (1535) and case (1547), so the
answered option leaves the menu. 1 byte each. Left pinned in D19b: the add
"Prepare my funeral!?" (1186) sits in case "Thordis sent me to you.",
which is never offered — the "I have been poisoned." case (1104-1114) sets
it and then, through a separate `if atliToldTest ... else`, overwrites the
list with "But I'm dying!" because `atliToldTest` has no writer; and the
removal "I climbed the cliffs." (1894) is inert, the next statement
assigning the whole list. Test: `test_uc_dialogue.py` D19c.

**M2 (2026-10-10): "Tell me more of the Great Cataclysm." answers.** Four
in-conversation adds (original lines 590, 656, 880, 944, all reachable
from the first meeting) offered "Tell me more of the Great Cataclysm.",
which no case handles; the one case on the topic, and the top-level add
that `spokeOfCataclysm` gates on later visits, read "Tell me more of the
Cataclysm." (2391, 352). The in-conversation cases set `spokeOfCataclysm`
as they make the offer, so it is one option: the case and the top-level add
now say "Great" (English and German), 2 sites, 6 compiled bytes each.
Pinned dead, not changed: "I have not heard from the Ancient Ones." (912,
the "Yes, I am from outside." menu) has no case anywhere in the corpus,
under any spelling, and the reply to its sibling "I have heard from the
Ancient Ones." (963) is the opposite ("Oh what great news this is!"), so
there is no 1994 answer to route it to; giving it one means new dialogue.
Test: `test_uc_dialogue.py` D19c (both). M4 below gives it new dialogue,
and R2 below makes the story case always speak.

**M3 (2026-10-10): two more options answer.** Found by D19b's exhaustive
scan (every option answered, every removal offered). The case "I found
great treasure!" (original line 2054) had no `\g` before its German half
(2055), so the German stayed in the compiled label and the option (2011,
offered from "I have opened your temple!" once `templeOpen` is set)
matched nothing; `\g ` is inserted, 3 bytes, as `RAGNAR` change 11. And
the in-conversation add "Shield of the Ancients?" (1007, 1030, in "They
did mention you." / "They did not mention you.", reached from the first
meeting's "I have heard from the Ancient Ones.") had no case; it now reads
"Tell me of the Shield." (English only), the text of the shield-story
case (1610) whose removal (1631) clears it, the reply those cases (which
set `mentionShield`, the gate of the top-level "Tell me again of the
Shield." at 346) were written for. Same shape as M2. Pinned, not changed:
the removal "Have you made the tea?" (the quirk noted above; the case
ends the conversation). Test: `test_uc_dialogue.py` D19c.

**M4 (2026-10-10, Douglas's decision; LV restoration text, not 1994):
"I have not heard from the Ancient Ones." answers.** M2 left it pinned
dead because no 1994 reply exists. A new case after original line 991 has
her answer the question she has just asked ("Heard from the Ancient Ones
have you?", 892) from her own lines: the Ancients would not answer at the
Great Cataclysm and she still waits for them to speak (849-858). The German
half is new too, and the case removes the option and its exclusive sibling
"I have heard from the Ancient Ones.". Every new line is marked
`// LV restoration text 2026-10-10 (not 1994)`. Test: `test_uc_dialogue.py`
D19c (EZREKAL M4).

**R2 (2026-10-10, Douglas's decision): the Cataclysm story always
speaks.** The not-shieldFixed branch of "Tell me more of the Great
Cataclysm." (original line 2650) rolls `ran = urandom(2) + 1;` instead of
`urandom (3)`. It barks only for 1 and 2 and then ends the conversation,
so one pick in three said nothing (M2's "not changed" note). R1's shape.
D19c sweeps every value the case's roll can return and requires one of
the two 1994 stories each time, and both over the sweep.

**M5 (2026-10-10): "Tell me of the Shield." is listed once.** The case
"Perhaps I will try the Cliffs." re-offers it while `toldOfShield` is unset
(original line 1842), but the only road to the case starts at the
`askList=` of "How?! How can I be healed?" (1529), whose list already holds
it, and the shield-story case that removes it also sets `toldOfShield`. The
add was `askList+=`, which compiles to list append (0x17) and keeps the
duplicate; it is now `askList^=`, string-list union (0x19 02), which drops
an option already on the list (`UCList::unionStringList`). 1 byte.
`docs/playtest-2026-10-10-full-run-part5.md` finding 2 (plate `s10-01`)
saw the menu with it twice. A 1994 defect, not M3's: 1529's `askList=`
replaces the whole list, so M3's adds at 1007/1030 are not on this road.
Test: `test_uc_dialogue.py` D19c (EZREKAL M5) and the closing check that
no menu in the file lists an option twice.

**M6 (2026-10-10): "I am from Britannia." is listed once.** On a first
meeting without the Mark the greeting sets `yelledAtAvatar` (original line
161), and case "May I know your name?" adds the option in its `if
yelledAtAvatar` branch (429) and again, unconditionally, after the if/else
(449). The second add is now `askList^=`, as M5: 1 byte. On the other
branch the option is not yet on the list and is added as before (union
puts the new options first). Found by the closing no-duplicate-menu check
of `test_uc_dialogue.py`, which every first-meeting walk in the file runs
through.

**M7 (2026-10-11): "Tell me again of the Shield." leaves the menu.** Case
"Tell me of the Shield.", "Tell me again of the Shield." (original line
1610) removed only its first label, so the greeting's "again" option (346,
once `mentionShield` is set) stayed after the story. One added removal
after 1632. Found by D19b's sibling class (a multi-label case that removes
one of its labels and not another an add offers). Test:
`test_uc_dialogue.py` D19c (EZREKAL M7).

## `TYORVI.UNK`

One character (T1, 2026-08-17, PROVISIONAL — review wanted): the
`case "Tell me more of the cliffs."` at original line 957 capitalized to
`Cliffs`, matching the menu-add at line 242. The compiler strips the
`\f`/`\g` language suffixes and dispatches on the exact English text, so
the shipped case could never match its own menu option — picking it
re-asked the same menu forever. Unreachable in 1994 (toldCliffs had no
writer) and exposed by the E5/E6 repair. Verified in-engine 2026-08-17.

**T2 (2026-10-07):** both menu adds of "I have something for you from
Ezrekal." (original lines 351 and 2213) gain `and (givenTea = false)`.
`hasTea` is never cleared and nothing tested `givenTea`, which the Key
handover sets, so every later talk re-offered the delivery and its chain
handed out a second Key to the Clouds (playtest 2026-10-07 wave 2 B).
`test_uc_dialogue.py` D12e drives both menus with `givenTea` 0 and 1.

**V1 (2026-10-08), SUPERSEDED 2026-10-09 by V3:** the two drink filters
`(type = TypeBottle) and (frame = 13)` (original lines 2058 and 2088)
search frame 5, the frame `EZREKAL.UNK` V1 now creates the elixir at. Why
5 and not 0 or 13: see `EZREKAL.UNK` V1 above. The two files must change
together; a filter that disagrees with the created frame finds nothing to
drink.

**V3 (2026-10-09):** the same two filters search frame 0, with
`EZREKAL.UNK` V3: `TypeBottle` is the elixir's own shape 868 and frame 0
its only frame, so the drink no longer destroys carried frame-5 blood.
D12d drives both drink paths with the elixir and blood of frames 5 and 0
in the pack, and requires the elixir gone, the blood kept and the Key
request offered.

**V2 (2026-10-08, verifier finding):** the sober "Just try it, please."
filter is `foreach recursive`, like the drunk path's. Non-recursive, it saw
only the Avatar's top level, so the vial in the backpack survived while the
Key was handed over (`docs/playtest-2026-10-08-batch-a.md` finding 2;
wave-2 B finding 4).

**S1 (2026-10-08):** schedule destinations retargeted; see "Schedule
destinations retargeted" near the top. Home is now Hoskuld, his clan's
village, and `build_map_10.py` starts him there too.

**T3 (2026-10-10):** five menu strings now match their cases or adds. The
healed Avatar's "I have freed the Ancient Ones!" / "I have opened the
Temple." / "I have found your Ancient Ones." (original lines 270,
274-275) become ".", "temple.", "the" (French "tes" -> "les"), as
`HRODNY` change 6. In case "She told me of the cliffs." (773), the case
`"No \f Non."` (790) becomes "No.", the text of its add (786) and of the
"Yes." case's removal (819), and that removal's "Yes" becomes "Yes.", so
the answered "Yes." leaves the menu. All reachable (`templeOpen`/`godsFree`
have writers; `toldCliffs` is Hrodny's). No Tyorvi near-miss is left
pinned in D19b. Test: `test_uc_dialogue.py` D19c.

**T4 (2026-10-10, Douglas's decision; LV restoration text, not 1994):**
D19b's exhaustive scan found four Tyorvi options with no reply anywhere;
each now has a new case (after original line 789), a short bark in his
voice built only from facts already in the file, a French half, and a
removal of the answered option. "I already have." (782, from "She told me
of the cliffs." once `climbedCliffs` is set) gets disbelief and grudging
respect: the cliffs claimed his best friend. "She had little to say." (745,
TODO F14) gets "Then wasted your time she has". "You weren't at the
cliffs." / "Are you going to the cliffs?" (213/217, the greeting once he
agreed to come and the Avatar tried the climb) get his excuse: gathering
his gear, and another drink. Every new line is marked `// LV restoration
text 2026-10-10 (not 1994)`. Test: `test_uc_dialogue.py` D19c (T4a-d).

**T5 (2026-10-10): an apology clears `tyorviPissed`.** Case "I wish to
apologize for my rudeness." (original line 2191) accepts the apology in
both replies, but the flag stayed set, and the greeting's `if
tyorviPissed` (222) assigns the one-option list "Calm down, Tyorvi.", so
every later talk lost the healed, temple and gods options for good
(`docs/playtest-2026-10-10-menus.md` finding 1; every checkpoint with the
restored Shield has the flag set). One statement after the replies,
`tyorviPissed = false;`, the trap `RAGNAR` change 12 fixed for Ragnar.
Test: `test_uc_dialogue.py` T5 angers him, apologizes, and requires the
flag clear and the next talk's top menu to offer "I have been healed!" (or,
with `templeOpen`, the two temple options) and not "Calm down, Tyorvi.".

**T6 (2026-10-10): "You weren't at the cliffs." clears `tyorviDrunk`.**
After the Key, "Tell me more of the Cliffs." -> "I am going there." ->
"Yes, accompany me." (original line 853) sets `tyorviDrunk` again, and the
drink (2094), its only other clearer, is spent. With `attemptedCliffs` and
`climbedCliffs` set, the greeting's `if tyorviDrunk and attemptedCliffs`
(209) replaced every later menu with T4c + Key + bye, so the healed,
temple and gods options never came back (`docs/playtest-2026-10-10-replies.md`
finding 1, seen in-engine). One statement in the T4c case. The re-arm is
kept: it is the 1994 road to that greeting, which now lasts one talk. T4d
("Are you going to the cliffs?") is untouched: before the Key the drink
clears it, after the Key the Avatar holds the key and the climb ends it.
Test: `test_uc_dialogue.py` T6 (accompany after the Key, the real
`EggCloudCliffs` hatch, T4c, then the ordinary, healed, temple and gods
menus; once via T4d).

**T7 (2026-10-10): the Key to the Clouds is quality 170.** Both
`give()` and `createNear()` (original lines 2132, 2135) pass 170 for 0.
Quality 0 is the retail "key blank", so `lv-new/CLCLIMB.UNK`, which now
accepts quality 170 only, could not tell his key from a Pagan one
(`docs/playtest-2026-10-10-replies.md` finding 2). The survey behind 170
(no retail or LV key, door or chest lock uses it) is in `CLCLIMB.UNK`'s
header. Tests: `test_uc_eggs.py` P1-P1d, `test_uc_dialogue.py` D12d's
static check of the compiled give.

**T8 (2026-10-10): the delivery is listed once after an apology.** The
greeting adds "I have something for you from Ezrekal." after the `if
tyorviPissed` "Calm down, Tyorvi." list (original line 353, gated on
`hasTea`, `haveMark` and T2's `givenTea = false`), and case "I wish to
apologize for my rudeness." adds it again (2215, `hasTea` and `givenTea =
false`), so with the Mark and the elixir the menu listed it twice. That
add is now `askList^=`, the same 1-byte change and 1994 defect as
`EZREKAL.UNK` M5. Found by the closing no-duplicate-menu check of
`test_uc_dialogue.py` on D12e's apology walk.

**T9 (2026-10-10): the drink's pause is one second, not 16.7.** Both
drink cases (original lines 2063 and 2093) waited `wait (1000);` before
"Hmmm, taste too bad...", now `wait (60);`. `wait()` compiles to a spawn
of retail FREE `0581:1C19`, which polls `getCurrentTimerTick()` (0xD2,
`Kernel::getTickNum`, 60 ticks a second), so the talk sat silent for
16.7 s with no text and no menu (`docs/playtest-2026-10-11-full-run-part6.md`
finding 1). [INFERENCE] a unit slip, milliseconds meant: no retail or LV
conversation pauses longer than TORWIN's `wait(30)` between barks, and
retail's three `wait(1000)`s are ambient schedule pauses (CYRRUS, PESANT2).
The follow-up bark was always compiled and spoken after the wait. Test:
`test_uc_dialogue.py` D12d requires every wait in both drink talks at most
120 ticks and the follow-up bark spoken.

**T10 (2026-10-11): the Key question ends with the Key.** The greeting's
"Do you have the Key to the Clouds?" add (original line 346) gains `and
(givenTea = false)`, as T2 did for the delivery. Gated on `sentToTyorvi`
and `haveMark` only, it outlived the hand-over (`givenTea`, 2143), and the
sober answer was "Yes, have it I do." (`docs/playtest-2026-10-11-fix7.md`
finding 3). Test: `test_uc_dialogue.py` D19c (TYORVI T10, `givenTea` 0
and 1) and T6, whose post-Key T4d greeting no longer lists it.

**T11 (2026-10-11): "I am going there." clears its menu.** Case "Yes.", "I
am going there." (808) removed "Yes." and the rest of the "She told me of
the cliffs." menu, not the options of the other menu that reaches it ("I
am going there." / "No reason, really.", 964), so both stayed beside "Yes,
accompany me." (same playtest, finding 4). One added removal of those two
after 820. The finding blamed the removal in case "No reason, really."
(978): it already matches, because the lexer cuts both strings at the
`\f`, and D19c's "TYORVI 1207" walk shows that pick clearing both. D19b's
`remove` class could not see the real slip (nothing removed was wrong; a
label was missing), hence its new `sibling` class. Test: D19c (TYORVI
T11).

**T12 (2026-10-11): an accepted apology clears the pissed menu.** Case "I
wish to apologize for my rudeness." (original line 2191) gains, after T5's
`tyorviPissed = false;`, one `askList-=` of "Calm down, Tyorvi.", itself
and "Shove off, you lush!": the pissed greeting's option (225) and the two
that case "Calm down, Tyorvi." adds (2167-2170). Both replies accept the
apology, but none of the three cases removed anything, so all three stayed
beside "I have spoken to Ezrekal.", and "Shove off" then set the flag again
(2182) and ended the talk (`docs/playtest-2026-10-11-fix9.md` finding 3,
plate T1-03). The removal is the 1994 cases' own form: the answered option
and its siblings, English with French, as in "I'm not a Pagan!" or "Drop
dead?". Test: D19c (TYORVI T12, the sober and the drunk reply).

## `PLNTST.UNK`

The Passage Test scene, merged into the egg hatch. Poison re-enabled
2026-07-27.

Holds `EGGPLANTTEST`, a quest-critical class. Note the header comment's claim
that "the compiler drops startup/process blocks" was falsified by the H1
changeset (L20) — don't act on it.

**Guard (2026-10-11): `if haveMark = true return;` at the hatch head.** The
egg is a fixed record with no latch, so a Passage stone carried in after the
Test replayed it: a second teleport, five more plants, and the Avatar
poisoned again after the ceremony's cure. The island stone is a fixed record
and came back on every entry to Map 10 (`docs/playtest-2026-10-11-static-art.md`
finding 2). A stone carried in afterwards now stays in the pack.
`test_uc_reentry.py` R10.

## `FLAGS.UNK`

Declares `givenElixir` and `iAmDrunk`, which the 1994 logic used but never
declared.
Also declares `crackHintGiven` (2026-10-03, bit 1829), EggCrackHint's
once-only guard, a restoration addition with no 1994 counterpart.

## `RAGNAR.UNK`

Seven layers, each with its own header block in the file (read them — line
numbers there refer to the original unpatched file):

1. **2026-07-04 quest-path survey (step-7 repair), changes 1-8**: the 1994
   debug leftover that reset `ragnarMet` on every conversation; six
   menu/case string reconciliations (a menu add must byte-match its `case`
   and its removal, or the option dead-ends — the `Yes, I do.` rename also
   un-shadowed the Passage-Stone case at line 760, which the duplicate had
   made unreachable); and **change 8 = DD-008 implemented**: the restored
   `case "I have no fight with you."` handler (the 1994 menu add at line
   355 had no case — picking it silently looped). Covered by
   `test_uc_dialogue.py:357`.
2. **2026-07-05 playtest reachability repair (change 9+)**: the bag-chain
   gate moved off `sentToRagnar` (declared but written nowhere) onto
   `atliMet && !ragnarToldStone`, plus the greeting-swap and
   duplicate-menu-line fixes from the in-engine punch list.
3. **2026-07-19 spelling sweep**: "Gunnar's('s) clan" → "Gunnars clan" (×3,
   bark text only). That header's "no other byte" claim describes only the
   sweep's own delta, not the file.
4. **2026-10-08, change 13 (S1)**: schedule destinations retargeted; see
   "Schedule destinations retargeted" near the top.
5. **2026-10-10, change 14**: the three menu-string quirks the step-7
   survey had left (its header's "NOT fixed" list): the removals "Yes, I
   am peaceful." (original line 357) and "I believe that is sincere."
   (706) now match their adds ("Yes, I'm peaceful.", "I believe that he
   is sincere."), so an answered option leaves the menu, and the add "Her
   body was eaten?!" (794) loses the "!" its case (798) and removal (802)
   do not have, so it dispatches. All three are on threads a player
   walks (first meeting; the change-9 bag chain). Test:
   `test_uc_dialogue.py` D19c.
6. **2026-10-10, change 15**: the two reachable defects D19b's exhaustive
   scan found. The removal in case "What do you do here?" (original line
   183) read "What do you do?" and now reads "What do you do here?", the
   add's (163) text, so the answered option leaves the first-meeting menu
   (`docs/playtest-2026-10-10-dialogue.md` finding 1). And the
   Passage-Stone answer "No, I don't." (add 756, removals 769 and 852)
   loses its period to match its own 1994 case "No, I don't" (841): with
   the period the pick matched the earlier crush case "No, I don't.",
   "No, I haven't." (542), whose "Blind are you? Stupid?" rant ends the
   conversation — the collision change 4 fixed for "Yes, I do.", which
   the step-7 survey had left on its "NOT fixed" list. Pinned in D19b
   (no reply exists, until change 16): "Who is Thordis?", "Do you like
   her?" and "None, thank you."; the removal "Now do you believe me?" sits
   in a case no add offers. Test: `test_uc_dialogue.py` D19c.
7. **2026-10-10, change 16 (Douglas's decision; LV restoration text, not
   1994)**: replies for those three options, each a new case with a short
   gruff bark from facts already in the file, a German half, and a removal
   of the answered option. "Who is Thordis?" (original line 507, after "tell
   you Thordis will") gets his own praise of her and "Seek her out"; "Do
   you like her?" (873, Hrodny) gets "Beautiful she is ... But no Thordis
   she is."; "None, thank you." (909, after he has told you where the stone
   lies) gets "Then go and find the stone. Beware the undead water
   creatures you must." Every new line is marked `// LV restoration text
   2026-10-10 (not 1994)`. Test: `test_uc_dialogue.py` D19c (RAGNAR 16a-c).
8. **2026-10-11, change 17**: case "Yes, I have met Thordis.", "I met
   someone named Thordis." (original line 582) removed only its first
   label, so the greeting's "I met someone named Thordis." (148,
   `thordisMet` without `spokeOfThordis`) stayed, and a second pick
   appended "Thordis is a good person." / "I was not impressed." again.
   One added removal after 597. Found by D19b's sibling class. Test:
   `test_uc_dialogue.py` D19c (RAGNAR 17).

(A CLAUDE.md bullet claimed the DD-008 handler was "still unfixed" until
2026-08-12; the file itself was always the authority. Note the recovered
originals contain high-bit German characters, so grep them with `-a`.)

## `ATLI.UNK`

Nine changes:

1. Restores the Passage Test aftermath dialogue the `PLNTST` merge dropped —
   `TESTPLAN.UNK:163-193`, the "No antidote there is" exchange.
2. Fixes the `"I have been poisoned."` / `!` menu-vs-case punctuation
   mismatch.
3. Adds the `plantScene` scene-end that unfreezes both elders' schedules.
4. One byte (2026-08-12): the "Tell me more of the test." askList *removal*
   had a TAB where the add and the case have a space (1994 defect, original
   line 1330), so the answered option was never removed from the menu.
   Invisible until the multi-value case dispatch fix landed the same day —
   before that, the case body containing the removal never ran at all.
5. S1 (2026-10-08): schedule destinations retargeted; see "Schedule
   destinations retargeted" near the top. With `safeTeleport` called for
   real, his schedule also takes him off the Test plateau once change 3's
   scene end (or the self-heal) has cleared `plantScene`.
6. Header change 5 (2026-10-09, Douglas's decision): the first-meeting
   "I have this shield!" option (original lines 743-749, the `"Prove it!"`
   branch) is wrapped in `if item.getQ() != 83`, so Pagan's own 828
   (quality 0) still offers it and the restored Shield of the Ancients
   (828 quality 83, made by `SHADES.UNK`, until 2026-10-17) does not.
   Atli's answer calls the item a look-alike of the Shield-Which-Was-Broken,
   which is wrong said to the real one. Three lines added, the body's 1994
   indentation kept. Since 2026-10-17 the restored Shield is shape 879
   (`TypeSacredShield`, SHADES change 5), which this `TypeAOArtifact` (828)
   search cannot match, so for it the decision holds by type. The guard
   still matters for saves made before that day, which can carry the
   Shield as 828 quality 83 (the altar still accepts it). Only the header
   gained a note. Test: `test_uc_dialogue.py` D17 (Pagan's 828 q0 offered;
   an 828 q83 and the 879 q83 Shield not).
7. Header change 6 (2026-10-10), two bytes: the "Hoskuld spy" menu's
   `"I am from Brittania!"` (original line 584) becomes
   `"I am from Brittania."`, the spelling of its only case (line 608) and of
   the first-meeting add (line 352); the French half is changed with it. The
   pick matched no case, so the menu came back unanswered
   (`docs/playtest-2026-10-10-leftovers.md` finding 2). The case's own
   removal, `"Iam from Brittania."` (line 615), still matches nothing and is
   left alone: the next statement assigns the whole list, so it strands
   nothing. Test: `test_uc_dialogue.py` D19a (walks every option on that
   menu) and D19b (a static near-miss scan of every compiled LV source's
   menu adds, removals and cases, with the 1994 near-misses still
   unfixed pinned by name).
8. Header change 7 (2026-10-10): three more near-misses the D19b scan
   found, each on a reachable branch. (a) The case and removal for
   "Hrodny sent me to you." (original lines 1017/1030) spelt her
   "Hrodney"; they now match the add (line 268, offered once `hrodnyMet`
   is set), 4 bytes over both halves. (b) The add and removal of
   "Who is Hrodny?" (2562/2619) read "Hrodney"; they now match the case
   (2601), 1 byte each. (c) The removal in case "Crazy contraptions?"
   (2850) ended in "." and now ends in "?", 1 byte, so the answered option
   leaves the menu. Test: `test_uc_dialogue.py` D19c walks all three.
   Status of the near-misses left alone: "The Hoskulds don't have the
   Stone." / "The Hoskuld's ..." (251/1487/1502) and the removal "Tell me
   again of the Rite of Passage." (1375) are behind `atliToldTest`, which
   has no writer, so they stay pinned in D19b; "Iam from Brittania." is
   inert (item 7).
9. Header change 8 (2026-10-10, Douglas's decision; LV restoration text,
   not 1994): "Former beauty?" (the add, original line 2536, in "Her dirty
   work?" on the poisoned Avatar's Ezrekal thread) had no case anywhere.
   A new case after line 2540 answers in two lines from facts already in
   the file ("here green and good life would be!", 1849; "dying a slow
   death", 2245), with a French half, and removes the option. Every new
   line is marked `// LV restoration text 2026-10-10 (not 1994)`. Test:
   `test_uc_dialogue.py` D19c (ATLI 8).
10. Header change 9 (2026-10-11): case "Who might be able to help me?",
   "Who might know where to look for it?" (original line 2044) removed only
   its first label; one added removal of the second after 2063. Found by
   D19b's sibling class. Unreached in play: the second label is added at
   2926 on the "I have come for the Passage Stone." road, which the
   greeting's `atliToldTest` else overwrites, so D19c (ATLI 9) sets
   `atliToldTest` by hand to drive the dispatch.

Comment-only, 2026-10-09: the two notes saying `exitConvo()` "emits
cSetActivity(0)" (header line 151, restoration line 511) now say it reruns
`Atli::enterFastArea`, which loiters him. Since the fork's
`Item::I_enterFastArea` fix (scummvm-lv-console `dccab1e7`) that rerun is
retail METHOD exitConvo's own (0x57C 109A), not a spawn the compiler adds
after it (`u8c_codegen` `_gen_exit_convo`); the notes still hold as
written. No compiled byte changes.

## `THORDIS.UNK`

The mirror half of Atli's aftermath restoration — `TESTPLAN.UNK:195-224`, the
lines Thordis speaks when the hatch teleports *her* in.

Guarded on `thordisToldTest = false`, which is the exact complement of Atli's
guard. This asymmetry is deliberate: `atliToldTest` has no writer anywhere in
the corpus, so guarding on it would make the branch dead.

**2026-09-05 review:** the restored speech was compared line-by-line with its
source, `TESTPLAN.UNK:195-224`, and two transcription slips were corrected — a
dropped comma after "the Great Cataclysm" and "can not" for "cannot". It now
matches the 1994 text exactly. The `testFromThordis` -> `thordisToldTest`
re-gate was confirmed correct: `testFromThordis` has zero writers anywhere in
the corpus, while `thordisToldTest` is written in the *recovered* THORDIS at
lines 1213 and 1243.

**Change 2 (2026-10-07):** `enterFastArea`'s `if (thordisSchedule = at_home)`
(original line 141) becomes `if (thordisSchedule != in_field)`. `schedule()`
stores the global only after `canSafeTeleport`, which was deferred until S1
(its 1994 destinations predated the rebuilt Map 10), so the global stayed 0;
with `at_home` 1 (retail) and `in_field` 2 (LV-only) a 0 matched neither
branch and Thordis got no activity (finding 1, `docs/playtest-2026-10-07-wave1.md`).
Any value but the field is home, as every build before the pins behaved, and
a save whose scheduler has never run still reads 0.

**S1 (2026-10-08):** schedule destinations retargeted; see the section above.

Comment-only, 2026-10-09: the header note at line 77 saying `exitConvo()`
"emits cSetActivity(0)" now says it reruns `Thordis::enterFastArea`, as for
Atli above, and, as there, the rerun is METHOD exitConvo's own since the
fork's intrinsic fix. No compiled byte changes.

**Change 3 (2026-10-07):** `enterFastArea` returns while `plantScene` is set,
the same guard `schedule()` has. PLNTST teleports her onto the test grounds
mid-scene; entering the fast area there spawned a loiter, and in one run she
walked off the z 64 plateau to z 0 beneath it (part 2, finding 1, of
`docs/playtest-2026-10-07-wave1.md`). She stands where the scene put her
until the scene-end conversation clears `plantScene`.

**Change 4 (2026-10-07):** case "Tell me about the other people." (original
line 971) calls `toldOthersConvo();` instead of `spawn toldOthersConvo() ->
return;`. A `spawn x -> return;` no longer waits (retail rule c, compiler
wave 2), so `use()` asked its own menu while the sub-conversation asked
"Your people. / The others.", and the two menus overlapped (A3a,
`docs/playtest-2026-10-07-wave2-a.md`). The plain call waits (rule a).

**Change 5 (2026-10-07):** in `toldOthersConvo`, each person block's closing
`tempKey = ask(tempList);` is guarded by `if toldMyTribe = false` (You,
Tyorvi, Ragnar) or `if toldOthers = false` (Atli, Ingyald, Hrodny,
Ezrekal). Telling a group's last person empties `tempList`, and `ask()` of
an empty list opens a row-less menu that never answers; with change 4's
wait that froze the Avatar for good (finding 1,
`docs/playtest-2026-10-07-wave2-final-a.md`). The routine now returns to
`use()`'s own menu.

**Change 6 (2026-10-10):** `schedule()`'s `if plantScene = true { return; }`
(original line 93) becomes the self-heal ATLI change 3 site 2 has: return
only while the Avatar is on the Test Grounds plateau, else clear `plantScene`
and go on to the home teleport. `SchedulerProcess::run` calls `schedule()`
for slots 1..255 in ascending order, so with only Atli (107) clearing it she
(106) had already returned in that pass and stood on the plateau one more
game hour (`docs/playtest-2026-10-09-final.md` finding 2). The scene-end
conversation still clears the flag itself, so that path is unchanged. ATLI's
header paragraph on this was corrected the same day (comment only, no ATLI
byte compiled differently). Test: `test_uc_dialogue.py` D14c, which drives
one pass in slot order and needs her home teleport in her own slot.

**Change 7 (2026-10-10):** the pre-Test chain ("Tell me of the Test.",
offered once Atli's "Rite of Passage?" case sets `testFromAtli`) answers
again. The cases `"I will take your Test"`, `"Yes"` and `"No"` (original
lines 1094, 1103, 1115) gain the period their adds (1091, 1100) and
removals (1105, 1117) have, 1 byte each. Inside the first, the option's own
`askList ^=` (1096, the union) becomes `-=`, 1 byte, so the answered
option leaves the menu. The same `^=` in "Not strong enough?" (1128) is
left: that case ends the conversation. Test: `test_uc_dialogue.py` D19c.

**Change 8 (2026-10-10):** the case "I have taken your Test." (original
line 1439) gains the labels "The plant exploded!" and "What is happening
to me?", the two options offered beside it (519-521: poisoned, no Mark,
`thordisToldTest` written — T2's live branch). No case had either text, so
both picks drew no reply; the case's own removal (1441-1443) already names
all three, the evidence that its reply ("Here, the Mark, is.") answers
them. Found by D19b's exhaustive scan. Test: `test_uc_dialogue.py` D19c.

## `SHADES.UNK`

Steps 14-15, the ceremony. Eight changes:

1. Six 1994 teleport coordinates retargeted to our Map 10 Sacred Circle and
   NPC homes.
2. The hatch reordered so the shield check precedes the elder teleport-ins.
3. (2026-09-25, change 14) The reforged shield goes into the Avatar's
   backpack at the end of the scene. 1994 popped it on the grass and never
   mentioned it again, so a player could walk off without the artifact the
   temple altar needs. The move is the 1994 `shieldUnequipper()` idiom
   (push, then `popToEnd` into the backpack), and a new Avatar bark, which
   Douglas approved 2026-09-25, says so.
4. (2026-10-07) Four `spawn X -> return;` statements become plain calls:
   `Avatar.turnToFace(4, 0, 6)` (original line 85) before the AS_WALK loop,
   and `Ezrekal.realDoAnim(AS_ENTER_CAST, north)` (lines 106, 146, 182)
   before the `AS_EXIT_CAST` spawn. Since wave 2 a `spawn -> return` does not
   wait, and the next statement's realDoAnim resets the same actor's anim
   processes (type 0xF0), so the cast never played and the turn and walk cut
   each other short. The plain call waits.
5. (2026-10-08) The reforged shield is `create(TypeAOArtifact, 0)` plus
   `setQ(83)`, was `create(TypeAOFrizbee, 2)` (original line 366). Douglas
   chose shape 828, "Zealan ceremonial shield", for the restored Shield,
   told from Pagan's own two 828s by quality 83, and `lv-new/AORTA.UNK`
   replaced retail class 828 to give it ZEALSHLD's 1994 look() text.
   **Since 2026-10-17 it is `create(TypeSacredShield, 0)` plus `setQ(83)`:**
   shape 879, the 1994 art (`lv_shapes.SHAPE_SACRED_SHIELD_1994`, on
   828's TYPEFLAG row). screen04 shows it on the sanctum altar; EZREKAL's
   forgery speech says Pagan's 828 is "the same shape it is and the wrong
   symbols it has"; the Map 17 halves are already the 1994 art 878, which
   reassemble 879. `lv-new/AOSCENE.UNK`'s altar searches for
   `TypeSacredShield` and still tests quality 83; class 879,
   `lv-new/SACSHLD.UNK` (pinned `TYPESACREDSHIELD`), barks "Ceremonial
   Shield of the Ancients Ones". For save compatibility the altar also
   accepts an 828 at quality 83 (saves made before 2026-10-17 between the
   ceremony and the altar), and `lv-new/AORTA.UNK` stays, replacing retail
   class 828, to name that legacy Shield. Tests: `test_uc_shades.py`
   P1/P6/P7, `test_uc_eggs.py` P5b.
6. (2026-10-08, header change 7) The three send-home teleports go to the
   S1 schedule home points: Atli (19200,6400) -> (19231,6943), Thordis
   (6144,6656) -> (4415,7423), Ezrekal (12800,12544) -> (12799,12543).
   Change 1 had used the map starts, and Thordis's start was inside the
   Hoskuld keep's corner, so the ceremony sent her home into a solid (her
   start moved the same day). 1994 sent each elder to one of their own
   schedule points, which is what this restores. `test_schedule_destinations.py`
   checks all six EggShades teleports.
7. (2026-10-11, header change 8) `if shieldFixed = true return;` at the
   hatch head. The success latch, `setEggXRange(1)`, is held by the egg, a
   fixed record that every map entry re-reads, so it lasted until the player
   left Map 10. Back with a second pair of halves (the Map 17 records
   respawned, `docs/playtest-2026-10-11-static-art.md` finding 2), the
   whole ceremony ran again and made a second restored Shield. shieldFixed
   is set only by the success path and never cleared, so the angry paths
   stay retryable. `test_uc_reentry.py` R9.
8. (2026-10-17, header change 9) Save compatibility for the halves. The
   backpack search finds `TypeAOFrizbee`, 878; a save made before
   2026-10-17 holds them as 870 (2026-10-11..17, retired, so a literal and
   no `TYPE_SHAPES` entry) or 539 (before 2026-10-11) and bailed at "Bring
   the sacred shield" (`docs/playtest-2026-10-17-vignettes-verify2.md`
   finding 1). After the 878 search, each half still missing falls back to
   870 and then 539, the pattern of `AOSCENE.UNK`'s 879 -> 828 altar
   fallback. A legacy half must be frame 0 at quality 81 or frame 1 at
   quality 82, as every build since 2026-03-21 placed them
   (`build_map_17.py` `QUALITY_SHIELD_HALF_1/2`), so Pagan's own 539s
   (quality 0) are not halves. `lv-new/REAPPLY.UNK` counts the same legacy
   halves as carried. Tests: `test_uc_shades.py` P9/P10,
   `test_uc_reentry.py` R8b.

**This scene holds the only `avatarPoisoned` cure.** If it does not run, the
poison has no exit.

Related: shield half 2 must be at `frame=1`, not `frame=2` — the reforge
usecode cannot see it otherwise (C2, fixed in `9acf0e6`).

## `FREE.UNK`

The shared routine library — 40+ bare routines and processes.

Repairs `makeAvatarBig`'s re-grow FAILURE branch, which dealt the killing hit
and then returned without restoring type, position, or stasis. The result was
an Avatar who was dead **and** tiny **and** frozen at (0,0,0). (DD-005, the
*story* decision — the temple is entered by shrinking. See
`docs/id-legend.md`; DD-005 also names an unrelated engineering decision.)

**Fix 2 (2026-09-25): `scrollBack()` re-attaches the camera.** Its last
statement, `Camera::setCenterOn(1)`, does not parse (`::` is unsupported)
and was dropped, so `scrollBack` compiled to nothing and every scene that
panned with the `scrollTo` intrinsic left the camera parked: the Sacred
Circle ceremony and the Lord British backstop. Now a bare
`setCenterOn(1)`, which compiles to retail FREE's own re-attach bytes.
Record: `docs/playtest-2026-09-25-ceremony-plaques.md`.

**Fix 3 (2026-10-02): `killProcess()` binds the engine intrinsic.** Its body,
`Kernel::resetRef(r,ptype);`, does not parse, so `Kernel` compiled as an
unknown identifier (push 0) and the routine was `init 00; push byte 0; ret`:
all 43 call sites killed nothing. Now a bare `resetRef(r,ptype);`, which
compiles to retail FREE's own bytes (class 0x0581 offset 2A56: `init 00; push
[BP+08]; push [BP+06]; calli 04 00CB; add sp -4; ret`).
Record: `docs/playtest-2026-10-02-pt-activity.md`, finding 1. Test:
`test_killprocess_npc_ref_cells.py`.

**Fix 1 follow-up (2026-10-07): the failure branch re-attaches the camera.**
`Camera::` calls compile since the wave-2 parser, so `makeAvatarBig`'s
`Camera::setCenterOn(0)` now detaches the camera before the regrow test; the
failure branch returned with it parked. It now calls
`Camera::setCenterOn(1)` before the kill, as the success path does (seen in
`docs/playtest-2026-10-07-wave2-final-b.md`, finding 2).

**Fix 4 (2026-10-11): a regrow beside a wall shifts instead of killing.** The
tiny (867, 32×32) and full (shape 1, 64×64) footpads share the max-x/max-y
anchor, so the full body reaches 32 units further toward −x and −y. A tiny
Avatar flush against a wall to his north or west therefore failed the
`canExistAt(TypeAvatar, …)` test and died, exactly as one growing inside the
crack does (`docs/playtest-2026-10-11-tiny-avatar.md`, finding 2: the Map 18
hall relief at (2592,5792,8), and the sanctum wall at (2576,6175)). Before
that test, `makeAvatarBig` now tries the spot 32 east, then 32 south, then
both, and moves the regrow there if a full body fits. Every one of those
boxes still covers the ground the tiny body stood on, so he grows out of a
wall and never through one; a gap only the tiny body fits still kills. The
+64 shifts were left out on purpose: inside the pre-breach crack (a 32-deep
wall), +64 south clears the wall entirely, so with it the crack would not
kill. Test: `test_uc_tiny_regrow.py`.

**Fix 5 (2026-10-11): no camera snap at the end of either ramp.** Both ramps
park the camera and move it one z unit per half-step, 16 in all (down while
shrinking, up while growing). That drift is kept. The closing
`Camera::setCenterOn(Avatar:Referent)` put the camera back at the Avatar's
z + 20, which is where the engine's follow camera always sits
(`CameraProcess`, `_e.z += 20; //!!constant`), in one frame: a 16 px jump of
the whole view (finding 1). Both are now `scrollBack(20)`, this library's own
25-frame glide back to the Avatar followed by `setCenterOn(1)`; it is
spawned and waited on (`spawn 05AEh 0254h`), so the Avatar stays in stasis
through it. Test: `test_uc_tiny_regrow.py`.

**Not changed (2026-10-10): the removal "Explain this shifting balace!"**
in `second()` misses its add and case ("balance"), so in that scene the
answered option would stay on the menu. It is pinned in
`test_uc_dialogue.py` D19b and left alone because nothing reaches it:
`second()` is spawned only from `makeAgent()`, and nothing in the compiled
corpus calls `makeAgent` (grep of `lv-patched/`, `lv-new/`, `LOST VALE/`
and `UNK files/UNK/`).

## `PLAQUENS.UNK`

`TypeNSGoldPlaque` (class 1259, npcnum 235). Appends qualities 68-70 after
67 for three Map 17 plaques, each quoted from the 1994 dialogue: 68
"FORBIDDEN*TO*MORTALS" (`THORDIS.UNK:1594`), 69 "FELICITAR*DOLORAS*TIMYRA"
and 70 "AMORAS*APATHAS*ODION" (`EZREKAL.UNK:1536-1538`). English only, as
quality 67 is. Douglas approved the text 2026-09-25
(`docs/art-track.md` contract 6).

## `HRODNY.UNK`

Eight changes:

1. Drops the stolen chest key at `z=0` instead of floating it 64 units up.
2. Adds the location lead her 1994 lines never gave.
3. (2026-10-07) Lowercases the menu entry "Tell me more of the Cliffs."
   (original line 437) to "cliffs". Its `case` (line 1063) and its remove
   (line 1065) are lowercase, so choosing the entry matched nothing and
   Hrodny said nothing. Lowercase is also the sibling entry's form, "She
   told me of the cliffs." (lines 941, 957, 959). The compiled class now
   holds three copies of the lowercase string and none capitalised.
4. (2026-10-07) `sched = in_home;` (original line 102) becomes
   `sched = at_home;`. `in_home` appears nowhere else in the corpus, and
   `enterFastArea` (line 122) tests `at_home`. Once `at_home` was pinned
   to 1 from retail (`SCHEDULE_CONSTANTS` in `u8c_symbols.py`), the
   unpinned `in_home` and `at_work` both compiled to 0, so Hrodny took the
   at-work bark day and night. Before the pin all three were 0 and she
   always took the at-home bark instead. With the LV-only values in
   `LV_SCHEDULE_CONSTANTS` daytide is `at_work` (2) and the rest of the
   day `at_home` (1).
5. (2026-10-07) `enterFastArea`'s `if (hrodnySchedule = at_home)`
   (original line 122) becomes `if (hrodnySchedule != at_work)`.
   `schedule()` stores the global only after `canSafeTeleport`, which was
   deferred until S1 (its 1994 destinations predated the rebuilt Map 10),
   so the global stayed 0, and 0 matched neither branch: Hrodny got no
   activity (finding 1, `docs/playtest-2026-10-07-wave1.md`). Any value
   but work is home, as every build before the pins behaved.
6. S1 (2026-10-08): schedule destinations retargeted; see the section
   near the top.
7. Header change 6 (2026-10-10): the healed Avatar's three menu entries
   (original lines 464 and 468-469) now read exactly as their cases
   (1126, 1141) and removals do: "I have freed the Ancient Ones!" -> ".",
   "I have opened the Temple." -> "temple.", "I have found your Ancient
   Ones." -> "the Ancient Ones.". All three used to match nothing, so she
   said nothing. Every gate on the branch has a writer (`haveMark`,
   `SHADES`'s cure, `templeOpen` from `TEMPLENT`, `godsFree` from
   `AOSCENE`). The third entry is a word swap the D19b scan does not
   flag; D19c's every-option walk found it. Test: `test_uc_dialogue.py`
   D19c.
8. Header change 7 (2026-10-10), from D19b's exhaustive scan. (a) In
   case "Zealan Vale?" (original line 556, offered at 548 on a second
   visit's "What place is this?"), `askList -= <<"Anything new?",
   "Shades?">>` (567) becomes `+=`, 1 byte: her bark ends on both topics,
   both have cases (570, 580) that remove their own option, and nothing
   else offers either, so both cases and "Shades?"'s follow-ups ("Tied to
   the land?", "Pagan?") were unreachable. (b) The case "I have been
   healed!" (1075) gains the label "The Shield of the Ancients is
   restored!", the option offered beside it (474-475, healed, temple not
   open): the case's own removal (1077-1078) already names it, and
   `INGYALD`'s 1994 copy of the case has the same two labels. Pinned: the
   removal "Do you have the Passage Stone?" (its only add is inside a 1994
   block comment). Test: `test_uc_dialogue.py` D19c.

Without the second, quest step 17 dead-ends. (DD-005, story.)

## Process blocks now loop (2026-10-01, `u8c_codegen.py`/`u8c_parser.py`)

Not a `lv-patched/` row by itself (it is a compiler change), but it
changes what every file below needs from its own patch, so it is recorded
here first.

A bare `process { ... }` block (as opposed to the `startup { ... }` block
that precedes it) used to compile as a single straight-through pass.
Disassembling retail class 0x2FE (`TypePotion`, `shared/data/USECODE.FLX`)
on 2026-10-01 showed that is wrong: retail's own `protection()`/
`invisible()` each compile their `process { ... }` section to a backward
`jmp` back to the section's own top (not the whole function's top --
`startup` runs once), taken whenever the block falls off its end without
an explicit `return`. A second retail sample (class 0x404, `GUARD1`'s
`use()`) shows the same shape at a much larger scale with no return at
all, matching the base game's own NPC wander/combat processes, which run
forever until killed externally. `u8c_parser.py` now tags a block parsed
from the bare `process` keyword (`kind='process'`); `u8c_codegen.py`'s
`_generate_statement` wraps a block carrying that tag in the loop
(`_gen_process_block`).

This change is global: it affects every `process { ... }` in the
compiled corpus, including every file that `uses` it. A full-corpus
rebuild and a per-class diff against the pre-change `EUSECODE.FLX` found
9 classes with a real new loop (the remaining 16 of the 25 classes that
differ at all are a pure offset ripple inside LVFREE, which grew by 6
bytes): `ARAMINA` (×3, `PT_ACTIVITY` wander behaviors -- no return needed,
matches the `GUARD1` reading, now loop for the NPC's whole lifetime, where
a single pass previously froze the NPC after one lap), `TypePotion`
(`protection()` only -- see below), `TypeAOFrizbee`
(`shieldMonitor()` -- unreachable, see below), `EggCandleTrick` and
`EggMagnet` (×3 -- patched, see `CANTRK.UNK`/`MAGNET.UNK` below),
`TypePoisonPlant` (`poisonAvatar()`, already well-formed), `EggShades`
(`squabble()`, already well-formed), `LORDBRIT.UNK` (`puppet()`, see
below), and `LVFREE` (×2 -- both dead code, see below).

Two found-but-not-patched items from that audit:

- `TypePotion::invisible()` never compiles its `process { ... }` section
  at all, loop or no loop: a pre-existing, unrelated parse-error cascade
  in `POTION.UNK` (`&`/`OWNED` and a dangling `else`, original lines
  ~217-239) desyncs the parser's error recovery badly enough to drop the
  whole section. Pinned at the Gate 7 ratchet's baseline of 3 for
  `POTION.UNK` and never looked at before now. Out of scope for this
  change; this fix closes the immortality bug in `protection()` only.
- `LVFREE`'s two `process { ... }` blocks (a `wait(time)` routine and
  `changeRef()`) both gained a backward jmp and both are dead: `wait` is
  a reserved keyword (`u8c_lexer.py`), so no call site can ever reach the
  user-defined `wait()` function by that name, and `changeRef` has zero
  callers anywhere in the corpus. Left alone, same as the two
  already-documented dropped classes above.

## `LORDBRIT.UNK`

`TypeLordBritish` (class 0x05A3), the quest step 1 apparition scene. Two
hunks, closing TODO.md "Found 2026-09-26"
(`docs/playtest-2026-09-26-lamps-plaques-lb.md` finding 1): the apparition
changed pose once and held it for the whole ~100 s bark. puppet()'s body
is byte-identical to the recovered original; the process-block change
above is what makes it loop now, so this file only needs to stop the
spawn from waiting on it and protect the now-longer-lived process:

1. `spawn puppet(lb) -> return;` loses its arrow (`spawn puppet(lb);`).
   `u8c_codegen.py`'s `_gen_spawn` reads `stmt.has_arrow_return`
   (previously parsed, never consulted) and, without the arrow, omits the
   `push_pid`/`push_retval`/`implies`/`suspend` pairing, a fire-and-forget
   spawn. `uc_machine.cpp` case 0x57 already runs a freshly spawned process
   once immediately and resumes the caller regardless; that pairing exists
   only to make the caller wait for a RETURN. The corpus has no other
   arrow-less spawn, so this changes no other compiled class. This is what
   makes puppet() looping safe: without it, use() would deadlock waiting
   on a spawn that waits on `lbDone`, which use() itself sets two
   statements later.
2. puppet() gains use()'s own `[[PT_DEFAULT, referent]];` pragma as its own
   first statement. The typeclass header already declared this annotation
   on puppet()'s signature, but header-form annotations are parsed into
   `FunctionDef.annotations`, and `u8c_codegen.py` never reads that field,
   so it stayed inert. This matters because the other trigger,
   `AVATAR::schedule()` (compiled, replacing retail class 0x401), teleports
   to `MapLBBlackness`, fires `lb.use()` as a non-blocking intrinsic
   (`Item::I_use` calls `Kernel::addProcess`, confirmed by reading
   `item.cpp` and `object.cpp`), and teleports back after only 120 ticks,
   long before the scene's ~100 s bark finishes. That return teleport's
   map switch kills every process with itemNum != 0 and type != 1. This
   hunk protects puppet() from that kill; without it, puppet() (now a
   longer-lived process, where pre-fix it returned almost instantly) would
   be the first thing it loses. The egg-hatch trigger
   (`lv-new/LBSCENE.UNK`) never switches maps, so this risk was dormant
   until puppet() gained a lifetime worth killing.

`agents/usecode-compiler/src/test_uc_lordbrit.py` checks both hunks and
the general loop. Statically: it disassembles the compiled class and
confirms the spawn has no trailing implies/suspend, puppet() has a
backward jmp landing at the top of the process section (not the whole
function), and puppet() opens with a set-info call. Dynamically: it runs
puppet() through `u8c_sim.py`'s child-execution path with `lbDone` preset
both ways. An in-engine retest is still needed; see the commit message.

## `AVATAR.UNK`

Source: `shared/data/lv-usecode/UNK files/UNK/AVATAR.UNK` (compiled over
retail class 0x401). Two added lines, 2026-10-04:

1. `globalflag lbStarted;` after line 8, the manifest-pinned flag (bit
   1701) that `LORDBRIT.UNK` and `lv-new/LBSCENE.UNK` declare the same way.
2. `if lbStarted = 1 { return; }` after line 1290 (`wait (240);`) in
   `schedule()`'s lbSpoke branch. The branch teleports the Avatar to
   `MapLBBlackness` and back 240 ticks after the first map switch off the
   Docks; if the egg's Lord British scene had started in that window, the
   teleport's map switch killed `TypeLordBritish::use()` mid-scene, leaving
   `lbStarted` 1 and `lbDone` 0, and quest step 1 could never finish
   (`docs/playtest-2026-10-01-process-loops.md`, 1b and finding 8). Once
   the scene has started, the branch now ends without teleporting; lbSpoke
   is already latched, so it does not fire again.

The branch's own `lb.use()` on a created shape 411 dispatches to retail
class 411, never to the pinned TypeLordBritish class, so the detour shows
nothing but 180 ticks of blackness; it is kept as the 1994 source has it.
`test_avatar_lbspoke_guard.py` runs the built class's schedule event in the
simulator: no teleport once lbStarted is set (it fails on the unpatched
build), and the detour unchanged otherwise.

## `CANTRK.UNK`

`EggCandleTrick` (class 0x0597), a candle-puzzle state check. No map
places it (`build_map_17.py` records it as removed and deferred), so this
fix is checked in bytecode only. One fix: `return;` added as the last statement of
`hatch()`'s `process { ... }` block, which otherwise falls off the end
with no exit. Before the process-block change above, that ran the
candle check once per hatch and stopped (the compiler's own prior bug,
accidentally matching this function's one-shot intent); with blocks
correctly looping, the same code would spin forever re-checking the six
candles every tick with no `wait()` between checks. By design this is a
one-shot check, re-triggered by a fresh hatch each time a candle is
touched, so the fix restores that one-shot behavior with a `return;`.

## `MAGNET.UNK`

`EggMagnet` (class 0x0598), the anti-magnetism trap that would set
`monolithSucks = true`. No map places it (`build_map_17.py` records it as
removed and deferred), so these fixes are checked in bytecode only.
Three fixes. The first two each add `return;` as the last statement of a
`process { ... }` block that otherwise falls off the end:

1. `hatch()`: both branches fall through. The `candlesCorrect = true`
   branch spawns `killMagnet()` with `-> return`, which keeps `hatch()`
   waiting on it but leaves `hatch()` itself to fall through afterward,
   so it would otherwise re-spawn `killMagnet()` every lap forever once
   the puzzle is solved; the `false` branch calls
   `cleanSweep()`/`friskAvatar()` directly, as ordinary same-process
   calls, and would otherwise re-enter them in a tight cycle once they
   return.
2. `friskAvatar()`: falls off the end after its ethereal pop-out loop. It
   had no per-lap yield of its own (until fix 3 its `spawn safePlaySFX`
   emitted nothing, `WARN MAGNET.UNK:266`); the suspend at every process loop's head keeps
   it clear of a hard engine hang, but it
   would replay the SFX and re-scan the Avatar's whole inventory every
   tick forever. This is a one-shot frisk.
3. (2026-10-07) `uses "free";` added after `uses "snddefs";`. Without it,
   `killMagnet()`'s `killProcess(referent, PT_UNKHATCH)` compiled to
   nothing ("unknown function 'killProcess'") and both
   `spawn safePlaySFX(...)` calls emitted nothing. They now compile as
   cross-class calls into LVFREE (`killMagnet` is `call 05AEh 0CDEh`).
   `PT_UNKHATCH` is still unpinned and pushes 0, so the kill targets type
   0, not the egg's hatch process (type 0x20F, the compiler's hatch
   preamble). No retail `resetRef` uses 0x20F, so the value has no retail
   evidence yet; the egg is unplaced, so nothing runs this today.

`cleanSweep()` keeps its current form: it already has its own
`else { return; }` once `candlesCorrect` is true, and is a genuine
forever-watcher (sweeps the area every ~100 ticks while the trap is
active) that the process-block change alone fixes correctly, matching
the `GUARD1` reading above.

Also found, and left unpatched: `TypeAOFrizbee::shieldMonitor()`
(`ZEALSHLD.UNK`, class 0x04EC) also gained a backward jmp, and it too has
no return and no `wait()` inside it, which would be a genuine CPU-spin
hang if it ever ran. It is spawned only from `equip()`'s
`if getFrame() = 3` branch, and nothing in the corpus ever creates a
`TypeAOFrizbee` at frame 3 (the reforged shield is not a `TypeAOFrizbee`
at all since 2026-10-08: SHADES creates it as 828, and as 879 since
2026-10-17; frame 4 is separately dead per that file's own comment).
Unreachable, left alone.

## `POTION.UNK`

Source: `shared/data/lv-usecode/LOST VALE/POTION.UNK` (class `TypePotion`,
manifest-pinned 0x04E5). Two changes. Change 1, 2026-10-07: the frame-4 (poison) branch
passes the damage type that its `receiveHit` call omitted (original line
96, now `urandom(2) + 5, DMG_FULL`). With three of the four arguments, the
engine read the type from past the pushed arguments. A type of 0 makes
`Actor::calculateAttackDamage` (`world/actors/actor.cpp`, the
`if (damage && damage_type)` else branch) return 0, so the potion did no
damage. `DMG_FULL` is the 1994 headers' name, which the compiler now pins
to 0x80 (`u8c_symbols.py`) from `U8/MORDEA.UNK:1284`
`Avatar.receiveHit(referent, 4, Avatar.getHp(),DMG_FULL)`, which is retail
`shared/data/USECODE.FLX` class 0x0407 offset 2736 `0B 80 00`, the first
argument pushed before `calli 0C 0053` at 274C. In
the engine 0x80 is `DMG_PIERCE` (`weapon_info.h:64`): no armour and no
to-hit roll, so the potion deals its full 5 or 6 points. The compiled call is
now `0B 80 00 ... calli 0C 0053` (12 argument bytes, matching retail), and
the `PINNED_1994` entry in `test_calli_arity.py` that recorded the short
call is removed.

Change 2, 2026-10-30 (Douglas, option c of the `b931fb4` respawn audit):
the protection (frame 5) and invisibility (frame 7) potions are drunk once.
Map 10's are FIXED records in Hrodny's hut, which `World::switchMap`
re-reads on every entry, so a drunk one stood there again at the next
visit; retail keeps its loose potions in NONFIXED data, where a taken one
never returns. Two `globalflag` declarations after the `uses` lines
(`potionProtectionDrunk`, `potionInvisDrunk`) and one statement at the head
of each branch, before original lines 102 and 136, setting that frame's
flag. Written in `use()`, which is the drink: `protection()` and
`invisible()` both `setFrame(0)` first thing. `EggReapply`
(`lv-new/REAPPLY.UNK`) destroys Map 10's frame-5 / frame-7 record on
arrival once its flag is set or the Avatar carries one of that frame.
Frames 0-4, 6 and 8 are untouched: Ezrekal's health and mana potions keep
restocking and Hrodny's Tiny Tars keep refilling. Test:
`test_uc_reentry.py` R11.

`TypePotion::invisible()` needs no fix. Its 1994 text is valid; until
2026-10-07 `OWNED` and `INVISIBLE` compiled to 0 and `toggleStatus` to
nothing, so the potion only played its sound and emptied. The compiler now
pins `OWNED` 0x04, `INVISIBLE` 0x10 and `toggleStatus` (retail METHOD
0x057C 0113) from retail's own `TypePotion` 0x02FE (`u8c_symbols.py`).

## `INGYALD.UNK`

New 2026-10-08. A byte-copy of `UNK files/UNK/INGYALD.UNK` (class `Ingjald`)
plus three changes:

1. S1: the two `schedule()` destinations (original lines 93-95 and
   100-102) retargeted; see "Schedule destinations retargeted" near the
   top.
2. Header change 1 (2026-10-10): five menu strings now match their cases
   or adds. "Tell me more of the Cliffs." (original line 343) -> "cliffs",
   the case's (799), as `HRODNY` change 3 did for her copy; the healed
   Avatar's "I have freed the Ancient Ones!" / "I have opened the
   Temple." / "I have found your Ancient Ones." (370, 374-375) -> ".",
   "temple.", "the", as `HRODNY` change 6; and the removal "How can I
   find cure?" (653) -> "How can I find a cure?", so the answered option
   leaves the menu. All reachable (poisoned + marked + `toldCliffs`;
   healed + `templeOpen`/`godsFree`; `toldOfPoison` from his own case).
   Test: `test_uc_dialogue.py` D19c.
3. Header change 2 (2026-10-10): the healed Avatar's "The Shield of the
   Ancients is repaired!" (original line 381) -> "restored!", the second
   label of the `"I have been healed!"` case (809) and that case's removal
   (812). Same length; the option drew no reply. Reachable after the cure
   while `templeOpen` is false. Test: `test_uc_dialogue.py` D19c.
