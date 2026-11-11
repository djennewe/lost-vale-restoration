# TODO.md — Ultima: The Lost Vale Restoration

> Remaining work to bring the cancelled 1994 expansion from recovered source to playable state.
> Last updated: 2026-10-09
>
> **This file is the live status tracker** (H10). `PLAN.md` holds strategy,
> `HANDOFF.md` is the session baton, and the review-driven work queue is
> `docs/reviews/2026-07-19-improvement-plan.md` (all that remains of it is
> the art/asset work — the 2026-08-12 status audit found every other
> "remaining" finding already fixed). `docs/id-legend.md` decodes the
> H*/M*/L*/P*/DD-* codes.
>
> **Pruned 2026-08-11**: completed-item narratives (and the full history of
> how each fix landed) moved to `docs/archive/TODO-full-2026-08-11.md`. This
> file now carries open work plus dated one-line records where a completed
> item still constrains future work. A checkbox flips only with a
> verification note: date plus what was run in ScummVM.

## Legend

- `[x]` Done
- `[-]` Partially done / in progress
- `[ ]` Not started
- `[!]` Blocked or needs investigation

---

## Phase 4c: Integration & Testing

The active phase. Phases 0–4b are complete (see Completed Phases below).

**Where the quest stands (2026-10-18).** The whole no-cheats 1-18 run has
been replayed on one pinned build twice: 2026-10-11 (EUSECODE `4182e079`)
and 2026-10-17/18 on the current build, EUSECODE `2e3b71c2` / FIXED
`8db11ee3`, after the monsters, the 1994 art and the rebuilt Maps 9-18
(`docs/playtest-2026-10-17-replay-leg1..6.md`). What is open below is
mostly design calls, art, and things a player cannot reach; the next
action is in `HANDOFF.md`. The narrative of how each step got here was
moved to `docs/archive/TODO-narrative-2026-10-07.md`.

Standing facts from that narrative that still bind:
- Let a cutscene run untouched, then query: an attached debugger pauses the
  world, and polling a scene's flag freezes it.
- A save carries its map's fixed items; verify a placement change on a fresh
  world or after re-entering the map.
- Map 8: Mythran's house is a floating island. `exact_reach` must scan
  glob-expanded items, not raw records. Not proven: the 2026-10-08 run read
  retail egg class MYTHAUS 04C6 out of NONFIXED, where the 09-01 FIXED-only
  scan could not see it. Its egg 1 on the plateau at (13988, 15084, 48)
  `teleportToEgg`s into the house (egg 20), and egg 2 at (3071, 1791, 0)
  sends the Avatar back to egg 22 when his z is 48 or more. If that holds,
  the house is reached on foot through retail eggs [INFERENCE: static, not
  walked; `docs/playtest-2026-10-08-full-run-1-18.md` finding 1].

- [x] **DECISION: bless or revise the two Map 8 terrain edits.** Blessed by
  Douglas 2026-10-08: they stay as the project's only deliberate departures
  from retail terrain. `build_map_08.py` drops one wall from retail glob 933
  (the seam at (29695, 24447, 56)) and one from glob 936 (shape 26 at
  (30463, 26399, 56)), so the south cave is walkable end to end. They were
  verified in ScummVM on 2026-09-01
  (`docs/playtest-2026-09-01-stock-bindings-climb.md`).
- [x] A complete 1-18 run, cheats off. **Done 2026-10-10/11 as one
  continuous save chain**: a prologue played without cheats, then steps 1-18
  by input only. It ended in the endgame scene with godsFree,
  endgameStarted and the reagent bag, and the closing barks were readable.
  The chain ran in seven legs on successive builds (each leg loaded the
  previous leg's save, so maps changed between legs reached it only after
  a map hop):
  - legs 1-2: steps 1-2, `docs/playtest-2026-10-09-full-run-1-18.md`,
    `-10-10-full-run-1-18.md` and `-full-run-part2.md`;
  - legs 3-4: step 3 (the spitter corridors, the doors and Map 9) and
    step 4 (the talismans), `-part3.md` and `-part4.md`;
  - leg 5: steps 4-11, `-part5.md`;
  - leg 6: steps 12-16 and the temple, `docs/playtest-2026-10-11-full-run-part6.md`;
  - leg 7: steps 17-18 with music on, `-part7.md`.

  Final save: `~/lv-checkpoints/run1010-s18c-m10-reagent-bag.sav`. Each
  leg's defects are filed below under "Found 2026-10-10".

  **Single-build replay done 2026-10-11**, in five legs on one pinned
  build: EUSECODE `4182e079`, FIXED `122b4374`, after the spare-key
  removal. Reports: `docs/playtest-2026-10-11-replay-leg1..5.md`. It ran
  from a fresh prologue to the endgame and the reagent bag, with input
  only and 0 cheats. Final save:
  `~/lv-checkpoints/replay1011-s18c-m10-reagent-bag.sav`. Two results:
  - leg 2 found the Map 8 212 slab on the first-visit route, now gated in
    `f99b9a9`;
  - the art and monster work landed after that build, so they are checked
    by their own reports (`-tiny-avatar`, `-static-art`, `-monsters2`,
    `-gates`), not by this chain.

  **Single-build replay on the current build done 2026-10-17/18**, in six
  legs on one pinned game copy: EUSECODE `2e3b71c2`, FIXED `8db11ee3`,
  U8SHAPES `efb16af1`, TYPEFLAG `d26d1531`, ANIM `696dbeb9`, hashes
  re-checked at the start and end of every leg. A fresh prologue to
  godsFree, endgameStarted and Ezrekal's reagent bag, by input only;
  `Cheat` 0 in every leg's log. 8 deaths and 9 reloads, all on legs 1, 2
  and 5 (causes in each report); legs 3, 4 and 6 had none. It covers
  what the 10-11 chain could not: the live monster eggs, the 1994 art (the
  878 halves, the 879 Shield on the altar, the 860 gods), and the rebuilt
  Maps 9, 10, 11, 13, 17 and 18. Reports: `docs/playtest-2026-10-17-replay-leg1..6.md`.
  Final save: `~/lv-checkpoints/replay1017-s18c-m10-reagent-bag-hp30.sav`.
  Step 8 took the Passage Stone from Ragnar's bag, so the Lake's Water
  Zombie crossing is covered by `-monsters2` and later, not by this
  chain. The findings are filed below under "Found 2026-10-17/18".

  Earlier attempts:
  - First attempt 2026-10-08 (`docs/playtest-2026-10-08-full-run-1-18.md`)
    stopped in the retail prologue on Map 3 when its session ran out: two
    walker deaths (the harbour, and the Map 39 gate pool at (17834, 17750)
    after a z 48 to z 8 drop, where the 10-03 run also died) and three new
    games. No LV step was reached.
  - Banked `~/lv-checkpoints/run1008-s00-prologue-after-execution.sav`.
  - Next run: start from that save, walk Map 3 to 40 to 39, and approach
    the LB egg on a hand-checked route clear of the gate pool. With trigger
    boxes masked, `exact_reach` finds no walking route from any arrival pad
    to the LB egg lane, although the engine does walk out of the east-gate
    pocket.
  - Rerun after the 2026-10-08 decision batch lands.
  - Second attempt 2026-10-09 (`docs/playtest-2026-10-09-full-run-1-18.md`),
    on the final 10-09 build with no cheats, stopped when its session ran
    out on Map 8, standing on a pool stone. The chain is banked as
    `~/lv-checkpoints/run1009-s00-map8-pool-stone-g.sav` (lbSpoke 1 from
    the Map 40 detour; lbStarted/lbDone 0). The report has the resume route
    from there through the trench, the gate-wall climb and the MYTHAUS egg.
    Map 7 killed the unarmed prologue Avatar twice (a flying creature,
    retail content).
- [x] **Step 1's primary trigger could not be reached on foot.** Every
  walking route from Tenebrae city to the Map 39 LB courtyard went through
  the east-gate trigger to Map 40, because in retail every way out of the
  city is a teleport egg. **Douglas 2026-10-09: open a lane.** Landed
  `7e9308c`: the east niche of the gate wall west of the main south gate
  is now a 128-wide tunnel (three retail glob-742 bottom courses cut, LV
  side walls and lintels; a documented retail deviation like Map 8's).
  `test_map39_lane.py` proves the walk with every trigger masked. Verified
  in ScummVM 2026-10-09 (`docs/playtest-2026-10-09-lane.md`): from a world
  new to Map 39, the Avatar walked with no cheats from the Map 40 gate pad
  through the tunnel to the LB egg, which fired on its own (lbStarted, then
  lbDone 1). Banked `~/lv-checkpoints/run1009b-s01-lb-done.sav`.
  - **Fixed (L3d):** a keyboard jump at the tunnel's side walls used to
    pass into the hollow gate block or wedge the Avatar at z 54. The cause
    was an upstream ScummVM bug, not the map: `AnimationTracker` passed
    `GetInterpolatedCoords(end, start)`, so a blocked jump frame landed
    almost a full step inside the wall. Fork `bbcfa209` fixes it. Verified
    in ScummVM 2026-10-10 (`docs/playtest-2026-10-09-engine.md` E4):
    - 24 jumps at both tunnel walls and at retail's niche walls stopped at
      the wall;
    - the pool-stone hops landed on aim;
    - the cave ascent went 5/5.
  - **Fixed: the jump fix's z -4 landing.** After the fix, a rise cut by
    an overhang still played its full descent, so a keyboard jump from
    (29500, 23622, 0) on Map 8 ended at z -4. Fork `11bb31bd` records the
    height each blocked rising step loses, and the descent pays it back
    first. Verified in ScummVM 2026-10-10
    (`docs/playtest-2026-10-10-jumps.md`):
    - J1: 11 of 11 jumps there end at z 0;
    - J2: jumps under the Map 39 arch and tunnel lintel end at z 48;
    - J3: 16- and 40-unit ledges still climb;
    - J4/J5: tunnel walls, pool hops, the cave ascent and the 512-unit
      open jump are unchanged.

    Route-guide note (finding 1): aim a pool-stone hop at the front
    (screen-bottom) third of the stone. The Avatar's location is his
    front corner, so a centre aim drowns him.
  - The canal-bank waypoint warning is resolved: `test_map39_lane.py`
    prints the safer line.

**Found 2026-10-08 in the retail engine's intrinsic table** (`U8.EXE`
decompiled; record `docs/research/2026-10-08-u8-intrinsic-table.md`). The
table is `USECODE/UNKCOFF.DAT`, 256 far pointers loaded at startup, and
every slot has its own retail implementation:
- [x] **Intrinsic 0xFE `isGameRunning()` returns 1 again.** Retail returns
  `[DS:59fa]`, which starts at 1 and is never written. So a locked chest
  (LCHST_EW/NS, shape 618) barks "locked chest" until its key turns it into
  shape 78, and a plain chest calls `use()` on the TRAP items inside it,
  which is how retail booby traps fire. Fork `9be627c0` (`I_false`, from
  the mistaken 09-02 Z-c diagnosis) had let every locked chest open without
  its key and disarmed every trap. Fixed 2026-10-08 in fork `f50c1d45`
  (comments `ed924d30`). Verified in ScummVM
  (`docs/playtest-2026-10-08-intrinsics.md`):
  - Hrodny's locked chest barks and opens no gump.
  - A Map 41 retail locked chest barks, and the wrong key is refused.
  - Map 51's plain chest opens.
  - Map 8's trapped chest explodes, as in retail.
  - All three Tiny Tar are taken.

  The `Unhandled intrinsic 254` line on each chest use is expected (the
  `I_true` stub warning).
- [x] **Hrodny's chest had no lock: any key opened it.** KEYRING reads the
  lock from a TRAP (shape 756) inside the chest, with quality
  `0x100 | keyid`, not from the chest's quality. Fixed 2026-10-08:
  `build_map_10.py` places `contained_item(SHAPE_TRAP, quality=0x114)`, FIXED
  `6dc98430`; `test_chest_locks.py` guards every locked chest the builders
  place. Verified in ScummVM on a fresh Map 10
  (`docs/playtest-2026-10-08-chest-lock.md`):
  - A quality-0 key, which is what the Cliff Key is, and a Pagan quality-99
    key are both refused.
  - The quality-20 key unlocks it, and the lock TRAP's `use()` is a no-op
    (no explosion, hp unchanged). The gump does not draw the TRAP.
  - All three potions come out.
- [x] **Bound 0x98 `Npc::freeEquip(item)` and 0x43 `Item::isInNpc()`** to
  their retail behaviour (fork `f50c1d45`). Tooling only, no engine surface
  yet: the only callers, `TypeAOFrizbee` (frame 3, never created) and
  EGGMAGNE (unplaced), cannot run in play. The verifier confirmed that from
  the build (`docs/playtest-2026-10-08-intrinsics.md` C8).
- [ ] **U8 equip/unequip usecode events never fire in ScummVM.** Retail
  fires event 0x0A when an item is equipped through the Avatar's gump and
  0x0B when one leaves; ScummVM fires them only from the null intrinsics
  0x63/0x64. Only `TypeAOFrizbee.equip()` handles either. It acts at frame
  3, which nothing creates, and as written it would reject the Defender
  itself (it counts the shield slot as armour). Leave it until the Defender
  is designed in. Record: research doc §3.
- `Npc::getNpcSlot()` (0x9A) allocates a free NPC slot and takes no item, so
  the 2026-10-04 compiler workaround for `enterConvo()` stands. Never bind it
  as "this NPC's slot". The Camera getX/Y/Z binding (`10d59e56`) matches
  retail.

**Found 2026-10-09 by the decision-batch verifiers** (each still open; design
calls unless noted):
- [x] The temple altar did not use up the restored Shield. **Douglas
  2026-10-09: place it on the altar.** Landed `9c16795`. Verified in
  ScummVM 2026-10-10 (`docs/playtest-2026-10-09-questbits.md` Q1): from the
  ceremony to the altar, the Shield landed on the altar top with the bark
  and looks "Ceremonial Shield of the Ancients Ones". godsFree 1, then
  endgameStarted 1. Negative control: without it the altar refuses.
- [x] Ezrekal's "…ready yet?" was silent 1 time in 4. **Douglas
  2026-10-09: always reply.** `urandom(3) + 1` (`62166bd`). Verified in
  ScummVM 2026-10-09 (`-quirks.md` Q4): 16 of 16 picks barked.
- [x] Atli's first-meeting "I have this shield!" matched any 828. **Douglas
  2026-10-09: exclude the restored Shield.** A `getQ() != 83` guard
  (`9c16795`; test_uc_dialogue D17). Verified in ScummVM 2026-10-10:
  - `docs/playtest-2026-10-10-leftovers.md` T2: with Pagan's q0 828 and
    atliMet 0, the option appears and answers.
  - `docs/playtest-2026-10-10-dialogue.md` D7 (a labelled debugger check:
    Item::setQuantity 764 83): with q83 the option is absent.
- [x] The elixir was a Blood reagent. **Douglas 2026-10-09: its own custom
  shape 868** (`62166bd`): a sea-green recolour built from the base vial at
  build time, TYPEFLAG from bottle 180 (generic, never stacks), class
  `lv-new/ELIXIR.UNK`. Verified in ScummVM 2026-10-09 (`-quirks.md` Q3):
  - it draws as a sea-green vial and looks "Tyorvi's elixir";
  - it does not merge with blood;
  - both of Tyorvi's drink paths consume it and give the Key;
  - carried blood is untouched.
- [x] Thordis left the Passage Test plateau one hour pass late when the
  scene-end talk was skipped: she (106) ran `schedule()` before Atli (107)
  cleared `plantScene`. Her `schedule()` now self-heals the flag the way
  Atli's does (`bb6967a`; lv-patched THORDIS change 6; test_uc_dialogue
  D14c). Verified in ScummVM 2026-10-10 (`-leftovers.md` T1): in one pass
  she went home to (4415, 7423, 0) and plantScene read 0. Negative
  control: with the Avatar left on the plateau she stays. The talk path is
  unchanged.
- [x] Sigrid's and Atli's map starts were not on their schedule points.
  Moved onto their homes (`cd6d63a`; `test_schedule_destinations.py`
  check 5). Verified in ScummVM 2026-10-10 (`-engine.md` E5): created at
  (4896, 8992, 0) and (19232, 6944, 0), on open ground.
- [x] A conversation replaced Aramina's route process with a plain
  LoiterProcess. **Douglas 2026-10-09: call retail METHOD
  enterConvo/exitConvo.** Landed `7cc1051`: every LV NPC spawns retail
  0x57C 0BCF/1090 byte for byte, and nothing after (`c44b84a`). The NPC
  restarts through the retail intrinsic, which fork `dccab1e7` makes fire
  as U8.EXE 10d8:2577 does. ScummVM had skipped NPCs already in the fast
  area, so retail NPCs too got no activity back after a talk. Verified in
  ScummVM:
  - `docs/playtest-2026-10-09-convo.md`: C1-C4 and the Ragnar, Passage
    Test and Ezrekal chains.
  - `docs/playtest-2026-10-09-engine.md`, after the fork fix:
    - E1: 9 of 9 NPCs have exactly one activity process after bye;
    - E2: Devon and Orlok resume;
    - E3: an invisible talk no longer freezes the NPC;
    - 0 `PID (0) in implies` at farewells.
  - `-questbits.md` Q4/Q6: Hrodny's temple talk and the Sacred Circle
    ceremony work under the new bracket.

  Mythran's camera scrolls back exactly once (`-leftovers.md` T4, filmed).
  Not shown: Tyorvi's drunk Key path on this build. Old checkpoints from
  Map 8 on load with 0x0F stuck at 1 until the first LV farewell.

**Found 2026-10-10:**
- [x] An Avatar embedded in geometry froze the world, and the runaway guard
  then killed the Avatar mover and the SchedulerProcess
  (`docs/research/2026-10-10-lb-egg-freeze.md`). The trigger was
  `run-s1-lbdone.sav`, saved inside a table: every refused animation woke
  the mover in the same kernel pass. Fork `8af4f74e`: the mover makes at
  most one decision per tick. Verified in ScummVM 2026-10-10
  (`docs/playtest-2026-10-10-mover.md`):
  - M1: 0 guard kills on that save; the scheduler and mover stay alive;
    a reverted control binary froze;
  - M2: per-tick walk, run, jump, climb, combat, drag and talk figures
    match the unfixed binary.

  `run-s1-lbdone.sav` still loads embedded: teleport before moving.
- [x] 1994 menu near-misses: an option added under one spelling and handled
  or removed under another, so it was dead or never left the menu. Fixed in
  lv-patched ATLI, HRODNY, INGYALD, TYORVI, THORDIS, EZREKAL and RAGNAR
  (merge `b1788b3`; the per-item table is in `lv-patched-inventory.md`;
  test_uc_dialogue D19a-c). Verified in ScummVM 2026-10-10
  (`docs/playtest-2026-10-10-dialogue.md`): D1 Atli, D3 Thordis, D4
  Ezrekal and D5 Ragnar. `docs/playtest-2026-10-10-menus.md` D2: all 10
  temple/gods cells pass (Hrodny, Ingjald, Tyorvi). Not shown: Tyorvi's
  drunk Key path on this build.
- [x] Menu mismatches the near-miss scan missed, such as Ragnar's "What do
  you do?". An exhaustive scan (D19b: removals never offered, adds never
  answered, shadowed labels) fixed RAGNAR 15a/15b, EZREKAL M3a/M3b, HRODNY
  7a/7b and THORDIS 8 (merge `4e1eb70`). Verified in ScummVM 2026-10-10
  (`-menus.md`): R1, R2, E1, E2, H1 and H2 pass. T1 (Thordis's sibling
  labels give the Mark) is not shown.
- [-] **Douglas 2026-10-10: write short replies** for the 9 options with
  no 1994 reply:
  - Ezrekal: "I have not heard from the Ancient Ones."
  - Tyorvi: "I already have.", "You weren't at the cliffs.", "Are you
    going to the cliffs?", "She had little to say."
  - Ragnar: "Who is Thordis?", "Do you like her?", "None, thank you."
  - Atli: "Former beauty?"

  Each new line is marked as LV restoration text, not 1994. **Douglas
  2026-10-10: Ezrekal's Cataclysm reply always speaks** (it was silent 1
  time in 3). Both landed in `fce4723` (EZREKAL M4/R2, TYORVI T4a-d,
  RAGNAR 16, ATLI 8). Verified in ScummVM 2026-10-10
  (`docs/playtest-2026-10-10-replies.md`):
  - Z1, Y3, R1 and R2's "Do you like her?" are answered, and the text wraps
    in the bark box with no second-language leak;
  - Z2: 14 of 14 Cataclysm picks told a story.

  Not shown: Y2 "I already have.", R2 "None, thank you." and A1 "Former
  beauty?".
- [x] Tyorvi stayed angry for good: "I wish to apologize…" never cleared
  `tyorviPissed`. TYORVI T5 clears it on the accepted apology. Verified in
  ScummVM 2026-10-10 (`-replies.md` Y1): on cp23 and cp32 his normal and
  post-cure menus return, and "Shove off, you lush!" re-angers him. Also
  shown: Y5, the drunk Key path on this build, and T1, Thordis's sibling
  labels giving the Mark.
- [x] Two Tyorvi traps found by `-replies.md`:
  - After the Key, the "accompany me" chain set `tyorviDrunk` again, so
    every later visit showed only "You weren't at the cliffs." (finding 1).
    TYORVI T6 clears the flag in that reply.
  - The cliffs accepted any shape-82 key: a Pagan q99 key skipped Tyorvi
    (finding 2). His key is now q170 (TYORVI T7), and CLCLIMB requires
    it.

  Both landed in `5c818f3`. Verified in ScummVM 2026-10-11:
  - `docs/playtest-2026-10-11-build7.md` T1: the q170 key climbs, and a q99
    key gets "require some sort of key";
  - `-fix7.md` T2: after the "accompany" chain, "You weren't at the cliffs."
    shows once and clears the flag, and the next visit is normal.

  Follow-ups `6eb3c87`, verified in `-fix9.md` T1/T2: the Key question
  leaves the menu once he has given the Key (T10), and "I am going there." /
  "No reason, really." leave together (T11).
- [x] Gateway bounces: a held key carried the Avatar from an arrival pad
  onto the return trigger in 5 of 14 pairs. Fixed in three rounds:
  - `d665e3c` fixed 212, 205 and 200;
  - `03e3e8a` added an engine-faithful mover model (`avatar_mover.py`:
    ±45° slides and keyboard wall-following) and moved pads 200/213,
    trigger 212, pad 204 and trigger 206;
  - `7123ffa` put 212 on a flush, visible slab and made the 206 marker
    visible.

  Verified in ScummVM:
  - `docs/playtest-2026-10-10-maps3.md` G1-G3 and G5-G7;
  - `docs/playtest-2026-10-11-build7.md` G1: 7 of 7 walks onto 212 fire it
    with the Avatar drawn, doorway walks north don't fire it, and the 206
    slab is visible and fires.

  The held keyboard run through Map 9 into 203 (about 7.5 s) is accepted:
  203 is the route's next gateway.
- [x] Map 13's summit had no north edge, and walking off killed the
  Avatar. `f971dda` re-laid the paving onto its chunks, put faces on every
  summit edge and parapets along the lethal upper climb. test_map_edges now
  fails on lethal falls and walks off the map, and exact_reach covers the
  y<64 band. Verified in ScummVM 2026-10-10 (`-maps3.md` E1/E2): N, W, E
  and S stop at the faces with no fall, and 209/208 work. Not shown: E3
  (the parapets) and E4 (paint at the new faces).
- [x] **The Map 11 column puzzle undid itself on re-entry**: the engine
  reloads fixed items from FIXED.DAT on every map switch, as retail does. An
  audit of every LV change to a fixed item found two that did not persist:
  the Map 11 pillars and boulders, and the Map 10 Test Plant. A new
  EggReapply on every Map 10/11 arrival pad re-applies them from the
  globals (`5ac8540`; `test_uc_reentry.py`). Verified in ScummVM 2026-10-11
  (`-build7.md` P1/P2): solved, then hopped, they stay gone; unsolved
  controls come back.
- [x] Engine hang: the audio thread spun in
  `MidiParser::determineNextEvent` after combat-music transitions
  (`-maps3.md` finding 2). The cause is a data race in upstream
  `Ultima8::MidiPlayer`: the game thread reset the parsers while the audio
  thread was in `onTimer` (`docs/research/2026-10-11-midi-hang.md`). Fork
  `b867a30c` adds a mutex. Verified in ScummVM 2026-10-11: `-build7.md` M1
  ran 280 combat toggles with no hang, and full run part 7 played 102
  toggles with music on. Upstream candidate.
- [x] Full run part 5 (`docs/playtest-2026-10-10-full-run-part5.md`):
  steps 4-11 walked without cheats. All fixed and verified in ScummVM
  2026-10-11:
  - F1: Map 11 lava and firepits hurt on contact, so they moved off the
    Fire-talisman lines, and the hurt shapes come from a gotHit survey
    (`76e9d84`). `-fix8.md` L1: 4 of 4 lines kept full hp.
  - F2: Ezrekal's duplicate "Tell me of the Shield." (EZREKAL M5). `-fix7.md`
    E1: it is listed once.
  - F3: the plateau rim is flush. `-build7.md` R1: the Avatar and Thordis
    are drawn.
  - F8: Ezrekal's east door. The desk and potions moved (`afaf4a9`).
    `-fix8.md` D1: walks pass and the potions pick up. The leftover "run
    stops" were a harness double-click jump
    (`docs/research/2026-10-11-ezrekal-door-run-stop.md`).
- [x] Full run part 6 (`docs/playtest-2026-10-11-full-run-part6.md`),
  fixed in `f904415` and verified in ScummVM 2026-10-11 (`-fix7.md`):
  - F1: Tyorvi's drink pause `wait(1000)` was 16.7 s of silence; it is now
    `wait(60)` (TYORVI T9) and measures about 1.2-1.4 s;
  - F2: the Map 13 climb is now three lanes, and walking it gives 0 falls;
  - F6: the Hrodny's-chest wedge is gone (5 of 5).
- [x] Running on the Map 13 climb left the lane. Fixed in three steps:
  - `9cf3151` added curbs for mouse runs (`-fix9.md` C1, 13 of 13);
  - `f86aacd` widened the foot-wall gap (C2, 10 of 10);
  - `d2e202e` put invisible curbs on both edges of every raised climb cell
    and round every bend, with keyboard-run and past-the-bend holds in
    `test_climb_width.py`.

  Verified in ScummVM 2026-10-11 (`docs/playtest-2026-10-11-fix10.md`):
  - C1: Shift+Up runs on every leg stay on the climb, 31 of 31; the old
    FIXED fell 7 of 7;
  - C2: 52 holds past the bends with 0 drops;
  - C3: no visible change and 0 paint cycles.

  Also verified there (T1): TYORVI T12 takes the apology options off the
  menu once he accepts.
- [ ] Map 13: the foot boulder (shape 796 at (3968,9984,4)) leaves one body
  width beside the west lane, so runs up or down that lane stall
  (`-fix10.md` finding 2). Middle- and east-lane starts are unaffected.
  Low priority.
- [x] Menu labels a case answered but did not remove: a new D19b "sibling"
  class (`6eb3c87`) fixed TYORVI T11, ATLI 9, EZREKAL M7 and RAGNAR 17.
  Verified in ScummVM 2026-10-11 (`-fix9.md` T2, E1, R1).
- [x] A spare q20 key lay in the village and opened Hrodny's chest, so a
  player who found it skipped the "How can I open the temple?" errand (full
  run part 6, F3). It was not in the 1994 code or design: our 2026-03 map
  builder read her "gone, the key is" line as "lying in the village". In
  1994 the errand pops the key in a bag. **Douglas 2026-10-11: remove it.**
  Removed from `build_map_10.py`. `test_chest_locks` now forbids a placed
  key for a script-keyed lock, and `test_uc_dialogue` "HRODNY key errand"
  checks that the bag holds a q20 key. Verified in ScummVM 2026-10-11
  (`docs/playtest-2026-10-11-key-removal.md`):
  - K1: after a map hop there is no q20 key on Map 10, and the chest stays
    locked;
  - K2: the errand bag lands at (19588,23284,0), and its key opens the chest
    with the three Tiny Tars.

  Old Map 10 checkpoints still carry the spare until a map hop.
- [ ] Hrodny's chest relocks and refills on every Map 10 load, but the
  errand runs once. A player who loses the q20 key can't reopen it; only
  the refill is lost, since the first three potions are already out
  (`-key-removal.md` finding 3). Low priority.
- [x] "Unhandled intrinsic 254 isGameRunning()" is cosmetic. The fork
  already binds slot 0xFE to `I_true`, matching retail `U8.EXE` 1298:1873;
  the warning is printed for every `I_true` slot. Left as is.
- [x] About 22,590 "Cycle in paint" lines on Map 10 came from stale
  checkpoints, not the shipped map
  (`docs/research/2026-10-10-map10-paint-cycles.md`). The two real knots
  with the Avatar were removed in `b66db3c`: the Map 10 spire and the Map
  13 summit face. Verified 2026-10-10 (`-gateways.md` G3): 0 lines at both
  spots, against 228 and 205 on the old FIXED.
- [x] **Douglas 2026-10-10: step 3 stays hard.** On foot, Map 8's north
  corridor (two unkillable retail SPITTERs and five MISSTRAPs) killed the
  unarmed prologue Avatar 5 of 5 times
  (`docs/playtest-2026-10-10-full-run-part2.md`). The retail traps are the
  intended difficulty, so the harness keeps trying the safest line from
  that report.

**Found 2026-10-17/18 (the single-build replay on `2e3b71c2`):**
- [x] **The Map 13 lane harpie pair killed the Avatar.** Unarmed, each hit
  (5-10) interrupts his run, so two harpies stun-lock a 30-hp Avatar: 2
  deaths and 3 reloads in the replay (`-leg5.md` findings 1-2). Armed, he
  still won only 5 of 10 fights against the pair (2026-10-18,
  `docs/playtest-2026-10-18-armed-harpie-pair.md`; new-game stats, a
  scripted loop that never blocks, retreats or drinks).
  **Douglas 2026-10-24: hatch them one at a time.** `build_map_13.py`
  now has a new group 3: its trigger at (5119,6143,76) hatches one harpie
  at (5183,5631,76) on the level z-76 stretch. The y-4479 trigger now
  hatches one harpie at (5183,3967,96). The summit pair is unchanged.
  `test_monster_eggs` pins the rule: south of the rest point, waves of one
  harpie each. FIXED `1a9ce209`. **Verified in ScummVM 2026-10-24**
  (`docs/playtest-2026-10-24-harpies-one-at-a-time.md`), on a pinned copy
  of that build:
  - each trigger hatched exactly one harpie (17/17 and 14/14 walk-ons);
  - the second hatched only after the first fight, and nothing was alive
    between the two fights;
  - the rest point stayed quiet, the summit pair still hatched, and the
    logs held 0 `Cycle in paint`.

  Armed wins went from 6 of 8 against 5 of 10 before: sword 3/5, axe 3/3.
  One unarmed run won. One harpie can still kill a fresh armed Avatar
  (run SW5), but a player can now heal between the two.
- [x] A dead harpie's 128x128 solid corpse stalls the walk north on the
  lanes until a sidestep (8 of 14 walk-ons; `-harpies-one-at-a-time.md`,
  and 10-18 finding 2). **Retail behaviour, left as is (2026-10-24).**
  Actor::dieU8 leaves a dead monster solid in place; getPositionInfo has
  no dead-actor exemption; no usecode runs at a U8 death. So a retail
  torax's body stalls the walk the same way. One body never closes the
  three lanes; `test_harpie_corpses.py` pins that. Re-seen in ScummVM
  (`docs/playtest-2026-10-24-fixes-211-rats-corpses.md` C3): a straight
  walk stalls, and a sidestep passes.
- [x] **The summit neck.** One harpie body in the neck between screen01's
  boulder (66:8, x 4127-4255) and the east curb (x 4479), or in the
  ~240-wide column below it, closes the walk to teleporter 209 (Map 17)
  until it leaves the fast area. Walking about 2 chunks back down the leg
  clears it. Offline, 15 of 591 body spots seal it.
  - **Widening was measured and dropped.** Any ground at z 120 east of the
    plateau draws into screen01's window: the full fix cost 95.35 → 90.78,
    the neck alone 93.65 with 8 seals left.
  - **Douglas 2026-10-30: don't widen; hatch the summit harpies one at a
    time.** The pair became two single waves: new group 4, trigger
    (5119,2687,120) → harpie (5183,2175,120); group 2 (4863,1663,120) →
    (4287,2175,120) only. `test_monster_eggs` now requires every Map 13
    wave to be one harpie. FIXED 039f6775.
  - **Verified in ScummVM 2026-10-30**
    (`docs/playtest-2026-10-30-potions-summit.md` H1-H4):
    - the rest point stays quiet (4/4);
    - each trigger hatches exactly one harpie (4/4, 5/5);
    - teleporter 209 reached 2/2;
    - sword fights: top harpie 3/4 wins, summit harpie 2/4 (started at
      22-24 hp), with no rest between them.
  - The seal itself stays possible, by decision.
- [ ] "Cycle in paint" `219 -> 875` on Map 17 beside the 878 sun half: 8
  lines while the Avatar stood at about (4348,7104,8) to pick the half up
  (`-leg5.md` finding 4). The port reproduces it: the Avatar, screen11's
  column 875 at (4351,7199,0) and its skeleton 219 at (4383,7199,0). The
  skeleton sorts under him by z, the column over him by y, and the
  skeleton over the column by x. `test_paint_cycles` §8 covers the shot's
  Avatar spot ±64 only. Moving the skeleton 32 north clears it, but it
  moves a screen11 item off the 1994 shot. **Douglas 2026-10-24: keep it
  as is for now** (the shot wins over a few log lines).
- [x] Map 11's rebuilt south half has one entrance (x 9560-9980, y ≈ 14350),
  and the water-zone trigger (9728,14528) covered its mouth: 4 rats, hp
  30 → 18 (`-leg3.md` finding 4). **Douglas 2026-10-24: not deliberate.**
  The group 4 trigger is now a strip at (13056,14880), and its 5 rats sit
  in the Water section's north-east bay, off every quest line.
  `test_monster_eggs` pins it: no trigger covers the south-half way in or
  lies within 512 of the lines between its ends. FIXED `ef2ed0f4`.
  **Verified in ScummVM 2026-10-24** (`-fixes-211-rats-corpses.md`
  C2a/C2b):
  - the walk hub → mouth → Fire doorway → Water talisman → pillars
    doorway hatched 0 rats;
  - an east walk across the strip hatched 5, and they fought;
  - control: the old trigger hatched 4 at the mouth.

  Not walked: entering the bay from the south, which bypasses the strip.
- [x] Map 10: walking SW/S/SE off the stair foot below the pad 210 shelf
  fired trigger 211 and sent the Avatar back to Map 18 (`-leg6.md`
  finding 3; offline, 309 of 1008 SW/W/NW holds fired). 211's hatch
  range went 0xD3 → 0x33: box x [18336,18592), y [23456,23712). The egg
  and screen17's stair did not move. `test_route_reach.temple_stair_foot`
  pins it. FIXED `ef2ed0f4`. **Verified in ScummVM 2026-10-24**
  (`-fixes-211-rats-corpses.md` C1a-c):
  - 0 of 71 SW/W/NW holds off the foot fired;
  - the deliberate entries still fire: a walked descent then S, 3/3;
    forecourt N, with the box edges exact; leg 6's NW walk-in, 2/2;
  - control: the old box sent the same SW walk to Map 18.

  Trade-off: a keyboard S hold down the stair now turns SW at the foot
  and fired 0 of 12. A mouse S hold or a forecourt walk-in enters.
- [ ] Low, and not a regression: SW/W holds that start ON the stair
  (z 16-48), or at the bottom step's NW corner (18400-18402,23231,8),
  still fire 211. In the engine 6 of 10 holds at the predicted cells did;
  offline, 139 of 23,976. No spot where a walked descent came to rest
  fires (`-fixes-211-rats-corpses.md` finding 1).
- [ ] Pre-existing: a mouse N hold through 211 lands at (3072,~1792) on
  Map 18, just south of trigger 210. A button still held walks into 210
  and back to the Map 10 shelf (`-fixes-211-rats-corpses.md`).
- [ ] Map 8 plateau gate teleporter (29407,30335) q257 (retail, unchanged):
  its hatch box starts at x 29279, and on the line y ≈ 30401 the wall stops
  the Avatar at x 29277. A walk E there never fires it; a jump does
  (`-leg1.md` finding 3). 10-11 fired it walking E from (29263,30443), so
  the walk-in line matters. Route-guide note, not a map change.
- Retail, carried as route notes and covered by "step 3 stays hard" below:
  a Torax from the plateau eggs waiting at the MYTHAUS hut door (`-leg1`
  F1); the island LITZAPEW gates (`-leg2` F1); the invisible 808 pair at
  the doors-chamber exit, which now has to be run past, because the
  gated 212 slab removed 10-11's detour (`-leg2` F4, `-leg3` F2); the
  Avatar drawn black in the spitter corridor (`-leg3` F1; the area matches
  retail item for item).
- Not reproduced: verify3 F1's pad 210 knot (0 lines across the 215 s
  finale, Object channel on, `-leg6` F4). No GHOST 411 follower was seen;
  leg 2 saw one retail ghost on the Map 8 island, and it did not follow.

**Found 2026-10-11/12 (art, monsters, replay):**
- [x] Map 8's return trigger 212 sat on the first-visit route: walking
  over it skipped Maps 9 and 11 (`docs/playtest-2026-10-11-replay-leg2.md`
  defect 1). It is now a usecode egg, EggValeReturn, gated on
  `allColumnsDestroyed` (`f99b9a9`; `test_route_reach.quest_order`).
  Verified in ScummVM (`-gates.md` G1): with the flag at 0 the slab does
  nothing; with it at 1 it sends the Avatar to Map 10.
- [x] Quest items came back on every map re-entry. A second pair of
  Shield halves re-ran the ceremony, and a second Passage stone replayed
  the Test. EggReapply now removes items once used or carried, and SHADES
  and PLNTST latch (`b931fb4`). Verified in `-gates.md` Q1.
- [x] **Douglas 2026-10-11: enable all LV monster eggs.** None could
  hatch: no MONEGG triggers existed. Fixed over four rounds:
  - 33 eggs wired, placed dry and standable, with combat activity
    (`9e8ea8a`);
  - the decisions applied: Lake waves 2/1/2 and one-shot; Harpie pairs
    with a rest point; an axe at the Map 11 hub (`e5a36dd`);
  - triggers that hatch inside the fast area, railed pier, deck and
    shores, and one-shot eggs everywhere (`18bea87`, `f2418dd`);
  - fork `e48f8716`: hatched monsters dispatch by shape.

  Verified in ScummVM: `-monsters2.md`, `docs/playtest-2026-10-12-monsters3.md`
  and `-monsters4.md`. `test_monster_eggs.py` holds every rule.
- [ ] **Balance note.** The off-path heavies (golems, the troll, daemons)
  still beat a 30-hp Avatar. The axe makes golems damageable but not
  beatable early, and golem 6 killed the step-7 Avatar within seconds
  (`-monsters3.md` finding 4). They stay off the shortest walk, as Douglas
  chose. Revisit if playtesters wander into them.
- [ ] "Cycle in paint" 126→871 at the Passage Test grounds after the Test
  scene (`-gates.md` finding 4). Not traced.
- [x] **The Map 10 potions respawned** on every re-entry (`b931fb4`
  audit). **Douglas 2026-10-30, option c: health and mana (Ezrekal's
  shelf) keep restocking; protection and invisibility (Hrodny's hut) are
  one-time.** The Tiny Tars keep refilling (accepted 2026-10-24).
  - **How:** `lv-patched/POTION.UNK` sets `potionProtectionDrunk` /
    `potionInvisDrunk` (global bits 1830/1831) when frame 5/7 is drunk.
    EggReapply then removes that Map 10 record on arrival, or when the
    Avatar carries one of that frame. `test_uc_reentry` R11 pins it.
  - **Retail, for comparison:** U8 keeps its loose potions (199 of shape
    766) in the new-game save's NONFIXED data, so a taken one never
    returns, and there is no restocking. Our LV maps exist only as FIXED
    records, which reload on every entry.
  - **Verified in ScummVM 2026-10-30**
    (`docs/playtest-2026-10-30-potions-summit.md` P1-P7), every return
    walked in through a pad: protection and invisibility gone once drunk;
    an undrunk one carried off is not doubled; health, mana and the Tiny
    Tars come back; the effects still work.
  - A health potion drunk at full hp sets hp to 15 (1994 behaviour). It
    matters more now that the shelf restocks.

**Found 2026-09-26** (each item carries its own status):
- [x] The Inner Sanctum has no exit at full size: leaving needs a second
  Tiny Tar potion, so a player who took one is trapped. Fixed 2026-09-26:
  opening the temple opens the crack into a breach 192 wide and 120 tall
  (EggTempleEntry destroys six wall records tagged quality 307, and a
  second EggCrackHint at the hall's north doorway reopens it after every
  map switch). Follows the 1994 EZREKAL "I have opened your temple!",
  which sends full-size Zealans there. Verified in ScummVM on
  EUSECODE `e7e19aad` / FIXED `4a3d3e18`: exit at full size carrying no
  Tiny Tar, re-entry without a potion, regrow in the old wall line
  survived (`docs/playtest-2026-09-26-sanctum-breach.md`).
- [-] The breach reads as a cut doorway: straight jambs, no rubble
  (plates D7, D10, E2b in the breach record). The rubble half is done
  (`9b2e890`/`eaf6e72`, D1 PASS in `docs/playtest-2026-10-04-batch-retest.md`);
  the straight jambs and flat top need broken course-end frames or new art,
  an art-track item.
- [x] The Bag of Reagents moves from the outdoor endgame to Ezrekal's
  "I have freed your gods!" (her 1994 line hands it over; the code never
  did). Verified in ScummVM 2026-09-27 on EUSECODE `7f885f5e`: the
  endgame gives no bag, she gives six stacks of 25 once, the top-up
  refills (`docs/playtest-2026-09-27-bag-ezrekal.md`). The endgame egg
  could be walked around, leaving the bag with no top-up; it moved onto
  Map 10's arrival pad from Map 18 and hatches on landing, verified
  2026-09-29 on FIXED `f92973ee`, including the old bypass route
  (`docs/playtest-2026-09-29-endgame-egg-pad.md`).
- [x] The top-up refills any partial reagent stack he carries, so
  splitting a stack onto the ground duplicates reagents (shown in-engine
  2026-09-29, three piles of 12). Verified 2026-10-04 in ScummVM on EUSECODE `c9716c73`, FIXED `079829c1` (`docs/playtest-2026-10-04-batch-retest.md`): only the tagged bag refills, 5 per
  poll on each frame's total up to 25; a split dropped inside the bag
  stays at 25 for 78 s.
- [x] `map_pins.json` still lists FIXED `bf233644` positions. Fixed in
  `db28de4` (2026-09-30); since 2026-10-07 `test_map_pins_fresh.py` also
  compares the pins with the builders' own output, not only the built
  FIXED.DAT. Tooling, no engine surface.
- [x] No map test pins EggEndgame's box over Map 10's target 210.
  `test_endgame_hatch_box.py` (db28de4) was rewritten 2026-10-07 to the
  engine's half-open egg arithmetic for both bodies: landing on 210 hatches
  EggEndgame, no point hatches both it and trigger 211. Tooling.
- [x] `build_map_10.py`'s headings for the teleport pair were swapped.
  Fixed in `db28de4`, builder output byte-identical.
- [x] The endgame's last line ("the path to Britannia...") played over a
  fully black screen. Fixed 2026-09-26 (`3fe7143`, `6e2f0c3`): it plays
  before the fade, as two barks split at the sentence, each whole on one
  page (16 s and 8 s); verified in ScummVM, E3 and E4 in
  `docs/playtest-2026-09-26-steps-15-18-unbroken.md`.
- [x] Lining up on the crack is fiddly: the tiny Avatar must stand in a
  32-unit strip and a walk step is 76 to 96 units. **Needs Douglas**
  (2026-10-07 research): no trigger box governs it, the wall is the gap
  (63 units, the widest that still refuses the full-size body), and the
  mover slides along the wall on a blocked step. Options: (A) an egg each
  side that moves a shape-708 Avatar onto x 2864; (B) a crawlway with a
  lintel at z 32 (needs lintel art); (C) say where the gap is in the
  CRACKHNT hint; (D) accept it. **Douglas 2026-10-08: (C)**, landed
  `a229d63`: "The crack lies hard against the east side of the pale block
  set into the wall." Verified in ScummVM 2026-10-08
  (`docs/playtest-2026-10-08-batch-a.md` E7): the bark plays on the first
  visit and again with potions, it stays silent in the negative control, and
  the pale block is visible. **Passage verified 2026-10-09**
  (`docs/playtest-2026-10-09-crack-aramina.md` C1/C2): a shape-867 Avatar
  at x 2852, against the block, walked south through the crack in four
  pushes, `templeOpen` 1 and "I am through…". Full size at x 2852 and x 2844
  was refused. Per-step displacement was 28-64 units in six directions.
  The first one or two pushes after the shrink are lost to stasis.
- [x] The Lord British apparition changes pose once and holds it:
  `puppet()` sets frame 1 and returns; a looping puppet also needs
  `use()` to stop waiting on it
  (`docs/playtest-2026-09-26-lamps-plaques-lb.md`). Fixed 2026-10-02 in
  the compiler: a `process { }` block loops with a `suspend` at its head,
  as retail compiles it (TypePotion 0x0634, GUARD1 0x103D), and `spawn`
  without `-> return` no longer waits. Verified in ScummVM on EUSECODE
  `c9180526`: frames cycle through the speech and end on 9, `lbDone` 1
  (`docs/playtest-2026-10-02-pt-activity.md`; the two runs before it,
  10-01 and 10-02, record the freeze and the leak this took).
- [x] Map 39's grass lane drops 48 into black void near y 20100.
  Verified 2026-10-04 in ScummVM on EUSECODE `c9716c73`, FIXED `079829c1` (`docs/playtest-2026-10-04-batch-retest.md`): the oak row holds pushes at eight x, and both walking routes into
  the band (the harbour rim and the avenue edge) are refused.
- [x] Map 17 tapestry 7746 at x 6016 is not drawn. The east wall hides
  every spot east of the Hall B doorway; it hangs at x 4607 now. Verified 2026-10-04 in ScummVM on EUSECODE `c9716c73`, FIXED `079829c1` (`docs/playtest-2026-10-04-batch-retest.md`): drawn
  whole.

**Found 2026-10-04 in the conversation-kill run**
(`docs/playtest-2026-10-04-convo-kill.md`):
- [x] FREE.UNK's five `agent.enterConvo()` calls were parse errors that
  error recovery dropped (`Expected IDENT, got ENTERCONVO`). Fixed
  2026-10-07 in the parser and codegen: `x.enterConvo()`/`x.exitConvo()`
  reset and resume `x`, bytes in `test_codegen_retail_forms.py`. No engine
  surface: nothing in game calls LVFREE's first()..final() scenes.
- [x] Sigrid's own `leaveFastArea` left her pathfinder running. Fixed
  2026-10-07 in `lv-new/SIGRID.UNK` (resetRef 0x204/0xF0/0x200 as retail
  PESANT1 does). Verified in ScummVM on EUSECODE `6b12ab85`
  (`docs/playtest-2026-10-07-wave1.md` C10): leaving while a pathfinder ran
  logged all four resetRefs, no process left for 102, she stopped.

**Found 2026-10-04 in the Lord British detour run**
(`docs/playtest-2026-10-04-lb-detour.md`):
- [x] Devon's farewell ends with one `Non-existent process PID (0) in
  implies`. Not a defect (2026-10-07): Devon 0x402 and METHOD 0x57C are
  byte-identical to retail; METHOD 057C:1090 `implies` on the pid of
  `enterFastArea`, which returns 0 for an NPC already in the fast area, and
  the VM warns and carries on. 256 retail sites spawn that routine.
- [x] A conversation's stasis survives a scripted map switch made while it
  runs. Not reachable in play (2026-10-07): the only cross-map Avatar
  teleports in compiled LV source are AVATAR's cheat menu and the lbSpoke
  detour, which releases stasis before teleporting (0x401 1A3B); teleport
  eggs need the Avatar to move, which stasis prevents.
- [x] Map 8's leftover backstop apparition logged ~3,500 paint cycles. Its
  slab and apparition moved clear of the cups (y 2326 -> 2208), 2026-10-07.
  Verified in ScummVM on EUSECODE `f24e5491`, FIXED `14774b0b`
  (`docs/playtest-2026-10-07-wave1.md` R4): 0 `Cycle in paint` over 60 s
  with it on screen.

**Found 2026-10-03 and 2026-10-04 in the batch-merge runs**
(`docs/playtest-2026-10-03-batch-merge.md`, `docs/playtest-2026-10-04-batch-retest.md`):
- [ ] A save taken with EggEndgame's `topUpReagents` running resumes it at
  its saved offset in the new class bytes, with the old 16-byte frame
  against code that now uses `[BP-12h]`..`[BP-16h]`: on the 10-03 bag
  checkpoint a partial drag refilled 13 to 25 in one poll. Any change to a
  looping process's code has this hazard for existing saves. Every bag
  checkpoint in `~/lv-checkpoints/` (newest:
  `bag-q1-poll1200-map10-2026-10-04.sav`) predates the 2026-10-07 ENDGAME
  bytes, so it resumes the old `topUpReagents`; bank a fresh bag save
  before trusting a refill measurement.
- [x] Hrodny's chest holds three Tiny Tars again after Map 10 reloads.
  Cause proven 2026-10-07: the chest and potions are FIXED.DAT records, and
  `World::switchMap` reloads every fixed item of the new map on each entry
  (`world.cpp:178-196`, `map.cpp:191-336`), so the chest comes back locked
  and full. **Accepted by Douglas 2026-10-08 (option A)**: the refill is a
  safety net, so a player who wastes all three Tiny Tar cannot soft-lock the
  temple. Since 2026-10-08 only the quality-20 key opens the chest, and the
  player keeps the key, so a reload gives three more
  (`docs/playtest-2026-10-08-chest-lock.md`). No engine surface changed.
- [x] The harbour's south wall showed a grass-tuft line along its z 48
  course. That course and the north wall's now use shape 15 frame 0, the
  same masonry without tufts (2026-10-07). Verified in ScummVM on FIXED
  `14774b0b` (`docs/playtest-2026-10-07-wave1.md` R5): line gone.
- [ ] Tenebrae's 29-oak south row reads as one repeating hedge (shape 199
  has one frame). A judgement against the map dressing standard.
- [ ] `iso_render.py` showed the Map 17 tapestry in full where ScummVM hid
  it behind the east wall, so it cannot stand in for an engine plate of
  anything wall-mounted.
  2026-10-12: `tools/map_viewer/` (branch `wt/mapviewer`) paints in the
  engine's dependency order (item_sorter's below/overlap/occludes over the
  whole map) and matches ScummVM here: the tapestry re-hung at x 6016 shows
  20 of 999 pixels, at x 5847 loses its bottom 7 rows (C2), at 4607 is
  whole. Not an engine plate (no actors, no animation); its README lists
  the gaps and its `compare_shots.py` scores six ScummVM shots.
- [ ] Tenebrae keeps 7,709 retail drop positions off its z=48 plateau, each
  a fall to z=0 that the engine walks anywhere (`current_map.cpp:773`),
  including the avenue's east edge north of y 17922. Pinned by count in
  `test_map39_south_edge.py`; Douglas chose 2026-10-03 to close only those
  near the Lord British lane.

**Found 2026-10-03** (`docs/playtest-2026-10-03-killprocess.md`):
- [x] Aramina does not walk her route. Fixed 2026-10-07 in the compiler,
  each value from retail ARAMINA 0x40D (`u8c_symbols.py` comments,
  `test_symbol_retail_pins.py`): `TypePathMarker` 174, plate 284, tankard
  178, friction grenade 592, doors 68/69; `frame = counter` compiles the
  run-time compare; `if pathfind(...)` waits; `at_home` 1, `on_throne`/
  `at_court` 2, `chow_down` 3. Verified in ScummVM on EUSECODE `6b12ab85`
  (`docs/playtest-2026-10-07-wave1.md` C2, PARTIAL): with her schedule
  forced to 1 atHome spawns, never more than one pathfinder, she walks and
  barks; marker order not shown. **In normal play she idles**: her
  `araminaSchedule` is our bit 0x663 while untouched retail MORDEA writes
  0x207 (and `devonInRule` 0x4B6 against 0x58), the deferred M1
  shared-flag migration. **Douglas 2026-10-08: migrate both flags**, landed
  `44e52f6` (save-breaking for those two bits only; old bits retired and
  enforced by `lv_manifest.validate()`). All 113 checkpoints hold MORDEA's
  1/2/3 at 0x207 and 0 at 0x663/0x4B6 (static check). In-engine A1-A3 were
  not demonstrated: the session ran out (`docs/playtest-2026-10-08-batch-b.md`).
  **Verified in ScummVM 2026-10-09** (`docs/playtest-2026-10-09-crack-aramina.md`
  A1-A3, A5):
  - with no forced globals, retail MORDEA moved 0x207 from 1 to 3 at the
    hour-4 boundary while 0x663 stayed 0;
  - at_home she walks her route (path markers f0-f5);
  - at 0x207=3 she barks "I must attend to her ladyship…" and exits;
  - the pre-Devon dialogue is unchanged;
  - an old Tenebrae save (cp2) plays.

  Not shown: 0x207=2 (needs hour 8). Her other flags were still on our
  bits, not retail's. **Douglas 2026-10-09: migrate ARAMINA's retail-shared
  flags only.** Landed `4fb5718`: eleven more pins moved onto the bits
  retail ARAMINA uses, found by pairing her 39 global operands with
  retail's (`araminaMet` 0x203, `araminaName` 0x204, `araminaJob` 0x205,
  `somebodyTalking` 0x0F, `hearTruthActive` 0x27, `hydrosFree` 0x36,
  `hasHeart` 0x3C, `lothianDead` 0xBF, `toldDagger` 0xD6, `mordeaDead`
  0x11A, `toldOfTreasure` 0x147); the old bits are retired. Verified in
  ScummVM 2026-10-09 (`docs/playtest-2026-10-09-final.md` F6, F7):
  - asking her name and job sets 0x203, 0x204 and 0x205, while 0x65F,
    0x660 and 0x661 stay 0;
  - ORLOK's "Tell me of Aramina." appears only after meeting her;
  - her route runs;
  - cp2 loads, saves and reloads.
- [x] Thordis ended the Passage Test in combat with the Avatar at 8 of 20
  hp. Cause: `TypeMiniAirTitan` was 400, retail's FIREFELD fire field
  (class 0x190 burns overlapping NPCs; 30 frames, hence the invalid 30-34);
  retail STRATOS 0x181 creates MINIAIR 481. Fixed 2026-10-07. Verified in
  ScummVM on EUSECODE `6b12ab85` and `f24e5491`
  (`docs/playtest-2026-10-07-wave1.md` C1, R2, part 3): MINIAIR 481
  whirlwinds, 0 invalid-shape lines, Thordis 20 of 20, no combat, all four
  flags 1, stone consumed; the Shades scene leaves the elders unhurt. Since
  part 3 (`3943f176`) she stands still on the test grounds until the
  scene-end conversation instead of loitering off the plateau.
- [x] `lv-patched/MAGNET.UNK:564` killProcess was a no-op (no `uses
  "free"`). Fixed 2026-10-07; the call emits. `PT_UNKHATCH` has no retail
  evidence and still pushes 0, and no map places EggMagnet, so nothing in
  game reaches it.
- [x] Map 39's avenue east edge north of y 19412 still drops to void
  (`TENEBRAE_OPEN_EDGES` in commit `dfa73f5`). Closed to y 17922 by six
  oaks; north of that it is a pinned retail drop. Verified 2026-10-04 in ScummVM on EUSECODE `c9716c73`, FIXED `079829c1` (`docs/playtest-2026-10-04-batch-retest.md`): pushes at seven y
  from 19300 to 17960 hold at z 48.

**Design questions for Douglas (from HANDOFF, 2026-09-26):** cloud tiers as
steps; a bark per god during the pan; the 13.9 s white before the pan; the
Message Scroll on the near half of its tile; where to place the frame 5
and 7 potions; whether anything sends the player back to Ezrekal.
**Added 2026-10-07** (options under each item): the crack alignment, Hrodny's
refilling chest, Tiny Tar's weight, Aramina's M1 flags, the NPC schedule
destinations and `TypeShields`.

**Found 2026-10-07** (`docs/playtest-2026-10-07-wave1.md`):
- [x] **NPC schedule destinations predate the Map 10 rebuild.** The 1994
  `schedule()` points of Atli, Ezrekal, Ragnar, Tyorvi, Sigrid, Thordis,
  Hrodny and Ingjald are pre-rebuild coordinates: Ezrekal's two are void,
  Ragnar's field, Tyorvi's stash and Sigrid's hunt are in the lake, the
  rest bare ground far from where our village places them. Calling retail
  METHOD `safeTeleport` for real would move every one there on the first
  schedule run. `safeTeleport`/`canSafeTeleport` therefore stay uncalled
  (`DEFERRED_METHOD_ROUTINES`). **Douglas 2026-10-08: retarget** each NPC's
  schedule points to the rebuilt village and call `safeTeleport` for real.
  Landed `f872e99` and `618c996`:
  - every point is checked standable by `test_schedule_destinations.py`;
  - Tyorvi now lives in Hoskuld;
  - Thordis, Ragnar and Ingjald's embedded map starts and the EggShades
    send-homes moved onto the home points.

  Verified in ScummVM 2026-10-09 (`docs/playtest-2026-10-09-schedules.md`):
  - N1 (PARTIAL): all 8 NPCs stood at their firstebb points after a map
    hop; a second period was not reached.
  - N3: an NPC near the Avatar is not teleported.
  - N5: a fresh Map 10 load starts Thordis, Ragnar, Ingjald and Tyorvi on
    open ground.
  - N6: the step 11-12 chain completes with NPCs at their new points; the
    elixir looks "1 vial of blood" (EZREKAL V2); the sober drink path
    removes the vial from the backpack (TYORVI V2).

  Then:
  - `fdac4f5` moved Tyorvi's stash point out from behind the Gunnar cliff
    to (21823, 8031) and added an occlusion check for every point;
  - fork `e3d2f40c` recreates a missing SchedulerProcess on load (the
    09-06/07 saves had lost theirs);
  - fork `4ccd3fe7` re-anchors the loiter leash after a teleport, which
    used to walk Ingjald back home from the still.

  Verified in ScummVM 2026-10-09 (`docs/playtest-2026-10-09-final.md`):
  - F1: run-s11 logs the recreate, event 8 fires for all 8 NPCs at the
    hour, and a healthy save gets no second scheduler;
  - F2: Tyorvi is fully drawn and clickable at the stash;
  - F5: all 8 NPCs are exact at their points over five periods;
  - F8: Ingjald stays at the still, and loiterers do not drift.
- [x] **`TypeShields`** is 587 where retail AVATAR 0x401 pushes 539. 539 is
  also shield half 1 (frame 0), so EZREKAL.UNK:1691's `(type =
  TypeShields) and (frame = 0)` would fire on the half and open her
  "forgery" lines. **Kept at 587 by Douglas 2026-10-08**: the forgery
  option stays dormant. No change, so nothing to run.
- [x] Thordis stayed on the test grounds after the Passage Test for good.
  Fixed by the 2026-10-08 retarget. Verified in ScummVM 2026-10-09
  (`docs/playtest-2026-10-09-final.md` F3): from cp10-test-done she
  reaches her Hoskuld home (4415, 7423, 0) at the next hour pass without
  leaving z 64-72 first. F4: after the ceremony, EggShades puts Atli,
  Thordis and Ezrekal at their homes.
- [x] The Inner Sanctum's south column plinths crossed the south wall and
  painted on its outside face. The colonnade's south half moved north
  2026-10-07 (spacing 448 -> 403, last plinth y 8720 -> 8495). Verified in
  ScummVM on FIXED `c3d29a1f` (`docs/playtest-2026-10-07-wave2-final-a.md`
  A5): clean outside face from inside and from the south. The corner urns
  sit flush but walls hide them from the camera.
- [ ] God's Hall thrones (289 at (2591, 2719, 8), (6175, 2719, 8)) sink 8
  into the dais's tier 1; (2559, 2687, 16) / (6143, 2687, 16) sits them on
  top. A look judgement; plate first.
- [x] One `Unhandled intrinsic 101 'process Item::combine()'` and one
  `Trying to access segment 0000` per Passage Test (not shape 400, which
  the 10-03 report blamed): LVFREE's `combine(item)` bound the 0-argument
  intrinsic 0x65 instead of FREE's own routine. Fixed in wave 2
  (`c89bf07`). Verified in ScummVM (`docs/playtest-2026-10-07-wave2-a.md`
  A2, `-final-a.md` A6): 0 of either over the Passage Test.
- [ ] Ingjald's `in_house` and `at_still` had no values (both 0, so the
  still branch was dead). `LV_SCHEDULE_CONSTANTS` gives the LV-only names
  distinct values (home 0, away 2); these are design values, not retail
  pins. Not exercised in ScummVM.
- [x] The tracked engine patch had lost the 2026-09-06 mover-recreate fix
  (`ultima8.cpp` loadGame): it lived only in the `scummvm-lv` build tree,
  so a fresh clone built without it. Ported to the fork (`0d1f7b21`),
  patch regenerated, build tree reset to base + patch; patch == fork diff
  == build tree. Verified 2026-10-07 (`docs/playtest-2026-10-07-wave1.md`
  C11): the binary carries it and a save/load cycle leaves the Avatar
  walking.

**Found 2026-10-07 in the wave-2 runs** (`docs/playtest-2026-10-07-wave2-*.md`):
- [x] Compiler wave 2 (`c89bf07`..`a2aaf16` plus the follow-ups): parse gaps
  closed, `return <expr>` values, exit epilogues, statement and value waits
  on process intrinsics, retail METHOD calls (realDoAnim, turnToFace,
  toggleStatus...), `spawn x -> return` detaching, retail event process
  types. Verified in ScummVM on EUSECODE `13ccb939`..`a95a8df0` over seven
  verifier sessions (wave2-a/-b/-c, -final-a/-b, -last-a/-b): LB scene,
  Passage Test, Thordis and Atli dialogue, elixir and Key hand-overs, Tiny
  Tar and the crack, the Sacred Circle, the altar and endgame, the bag
  once plus its top-up, plaques and the Message Scroll, NPC conversation
  exits; 0 segfaults, 0 stuck loops, 0 unhandled intrinsics on the last
  build. The defects those sessions found are the items below.
- [x] Double-clicking the Avatar segfaulted: wave 1 revived AVATAR use()'s
  `openGump` with unpinned constants (0). `CONTAINER_GUMP_OPEN` 0x100 and
  `Gump_MainMenu` 1 pinned from retail AVATAR 0x401. Verified
  (`-final-a.md` A2): the paperdoll opens and closes four times.
- [x] The Tiny Tar shrink and regrow blacked the screen out ~2 s: FREE's
  `Camera::getX/getY/getZ` (now compiled) hit unbound U8 intrinsics
  0xC3-0xC5. Bound in the fork (`10d59e56`). Verified (`-final-b.md` B1,
  `-last-b.md`): no black frames, 0 unhandled intrinsics over 5 drinks.
- [x] Thordis's "Tell me about the other people." showed two ask menus
  (spawn rule c), then soft-locked when a group's last person emptied the
  ask list; `Avatar.ask()` as a value did not wait, so askYesNo answered
  -1 at once. Fixed (THORDIS changes 4-5, value waits). Verified
  (`-last-a.md` L1, L2): one menu at a time, every chain returns to her
  menu, Yes/No waits for the click.
- [x] Kneels played as walk steps (AS_KNEEL_* unpinned): pinned 49/50 as LV
  design values from retail's kneel pair. Verified (`-final-b.md` B2) for
  the Avatar.
- [ ] Thordis and Atli cannot kneel: their shape 707 has no action 49/50 in
  ANIM.DAT (they stand through SHADES.UNK:496). Art-track item.
- [x] Tyorvi handed out a second Key to the Clouds on every re-run of the
  chain: both menu adds now test `givenTea = false`. Verified (`-last-b.md`
  M1): no second offer, key count unchanged.
- [ ] After the Sacred Circle the Avatar ends at (20456, 17080), 96 units
  north of the 2026-09-26 mark, facing south (`-final-b.md` B2). Judgement.
- [ ] The Tiny Tar window is now ~1,375 ticks (~28 s) against ~2,000
  before: the potion's wait(2000) now starts with makeAvatarTiny instead
  of after it (spawn rule c). The crack is still walked in time
  (`-final-b.md` B1). A design call if it should be longer.
- [-] Mythran's LV dialogue left the camera on Mythran (the patch preamble
  runs retail enterConvo; our exitConvo never scrolled back). MYTHRDLG now
  calls `scrollBack(25)` before `exitConvo()`, as retail Npc::exitConvo
  does; bytes checked (class 1451 at 1B6E spawns LVFREE scrollBack and
  waits). Not shown in ScummVM: two clicking sessions could not reach him.
- [-] makeAvatarBig's regrow-failure branch left the camera detached (its
  `Camera::setCenterOn(0)` now compiles): it re-attaches before the kill.
  Not shown: the failure did not reproduce at the same spot.
- [ ] `Cycle in paint dependency graph` debug lines remain at two places:
  Map 8 Mythran's house (shapes 164/149, seen 2026-10-07) and the Map 10
  Passage Plant tiles while Thordis loiters there (475/126/707,
  `-final-a.md` finding 3). Debug-level; nothing visible in plates.
- [ ] Ingjald and Ragnar loiter under their hut roofs, where a click from
  outside hits the roof (`-last-b.md` finding 2); step inside to talk.
- [ ] THORDIS.UNK's two group-header asks (`Your people.` / `The others.`
  blocks) would still ask with an empty list if every person flag of a
  group were set while the group flag was not. Not reachable in play
  (`-last-a.md` finding 2).

**Found 2026-10-02** (`docs/playtest-2026-10-02-pt-activity.md`):
- [x] `killProcess` compiles to nothing (`lv-patched/FREE.UNK:830-832`,
  `Kernel` is an unknown identifier pushed as 0): 43 call sites in 14
  classes do nothing, including Aramina's `leaveFastArea`, so her looping
  `atHome()` runs on Map 41 until the next map switch. Fixed 2026-10-03,
  EUSECODE `a908cb53`: in ScummVM, leaving Map 41 logs `resetRef item=13
  type=0x0205` and kills atHome (`docs/playtest-2026-10-03-killprocess.md`).
- [x] Aramina's `atHome()` searches "within 10 of item 0x040D", which does
  not exist, and logs about 180 `Invalid item 1037` warnings a second
  while it runs. Fixed 2026-10-03, EUSECODE `a908cb53`: 0 warning lines in
  ScummVM (same record). Her schedule constants still compile to 0; that
  item moved to "Found 2026-10-03".
- [x] Every conversation kills every NPC activity process in the world:
  `enterConvo()` passes `Npc::getNpcSlot()` (intrinsic 154, a null entry,
  returns 0) to `resetRef`, and item 0 matches all items. Fixed 2026-10-04
  in `u8c_codegen.py`: it kills the NPC's own 0x205, 0x200, 0xF0, 0x204 on
  `referent`, as retail METHOD does. Verified 2026-10-04 in ScummVM on
  EUSECODE `ec3e66fd` (`docs/playtest-2026-10-04-convo-kill.md`): item 65's
  PESANT3 activity survives two Aramina clicks, Ingjald's loiter survives
  a Hrodny conversation, all 146 `resetRef` lines name the talked-to NPC,
  each NPC resumes after **bye**, and stasis clears.
- [x] NPCs in the fast area at a map switch came back frozen. Fixed
  2026-10-07 in the fork (`976f3125`): `CurrentMap::loadMap` clears
  `FLG_FASTAREA` on each NPC it adds, as `loadItems` does for map items.
  Verified in ScummVM on EUSECODE `6b12ab85` and `f24e5491`
  (`docs/playtest-2026-10-07-wave1.md` C3, R1): after a Map 3 round trip
  Hrodny gets event 15, a loiter, and moves; Thordis and Hrodny also loiter
  on first approach with a never-run schedule global.
- [x] Hrodny's "Tell me more of the Cliffs." did nothing (one capital).
  Fixed 2026-10-07 (`lv-patched/HRODNY.UNK` change 3). Verified in ScummVM
  (`docs/playtest-2026-10-07-wave1.md` C4, R3): picked from the screen, she
  answers "What more to tell is there? Dangerous...".
- [x] Map 10's north-east village logged ~110,000 paint cycles. Shapes 426
  (vine line) and 208 (workbench): both workbenches straddled their hut's
  south wall; moved clear 2026-10-07, and the abacus out of its bench.
  Verified in ScummVM on FIXED `14774b0b` (`docs/playtest-2026-10-07-wave1.md`
  C5): 0 cycles in 60 s at (21760, 8544); the abacus barks the coin count.
  `test_paint_cycles.py` ports the engine's sorter to pin it. An old save
  keeps the old Map 10 items until the map is re-entered.
- [-] The frame-4 poison potion did no damage: `receiveHit` got three of
  four arguments. Fixed 2026-10-07 in a new `lv-patched/POTION.UNK`
  (`DMG_FULL`, pinned 0x80 from retail MORDEA 0x407). Not demonstrated in
  ScummVM: no map places a frame-4 potion and no debugger verb creates one.
- [x] The Lord British scene dies for good if the map-0 detour in
  `AVATAR::schedule` fires mid-scene (`lbStarted` 1, `lbDone` 0), which
  blocks quest step 1. Window: about 240 ticks after first arriving.
  Fixed 2026-10-04 in `lv-patched/AVATAR.UNK`: the detour ends without
  teleporting once `lbStarted` is set. Verified 2026-10-04 in ScummVM on
  EUSECODE `18cc709c` (`docs/playtest-2026-10-04-lb-detour.md`): in two
  fresh worlds with the scene started inside the window, no map 0 load,
  apparition to frame 9, `lbDone` 1, and Mythran opens his `lbDone`
  branch; the ordinary detour still runs when the scene has not started.

**Found 2026-09-25:**
- [x] Two Map 17 wall lamps hung in doorway openings; moved clear
  2026-09-25 (`2f27d51`), verified in ScummVM 2026-09-26 (L1, L2 in
  `docs/playtest-2026-09-26-lamps-plaques-lb.md`).
- [x] Frame 5 and 7 potions (protection, invisible) were placed nowhere.
  **Placed 2026-10-08** (Douglas: Hrodny's home) on the open ground beside
  her chest, outside her door ((21216, 8832, 0) and (21280, 8832, 0),
  `build_map_10.py`, `86ab1d1`). Verified in ScummVM 2026-10-08
  (`docs/playtest-2026-10-08-batch-a.md` P5/P7): both clickable and
  carryable. Frame 5 set `ACT_IMMORTAL`, which cleared at about 50 s.
  Frame 7 set `FLG_INVISIBLE` (translucent), which cleared at about 51 s.
  Its 1994 code leaves `FLG_OWNED` set, with no effect seen.
- [x] While the Avatar is Tiny Tar the pack read weight 520 against
  capacity 200 (`docs/reviews/2026-09-30-four-anomalies.md` §1). **Douglas
  2026-10-08: own slot 867**, landed `60f2caf`. 867 clones the child actor
  708 in U8SHAPES, TYPEFLAG and `STATIC/ANIM.DAT`, the fifth artifact,
  with shape 1's weight 1 and volume 250. Verified in ScummVM 2026-10-08
  (`docs/playtest-2026-10-08-batch-a.md`):
  - T1: the potion turns the Avatar into 867 and the shrink plays.
  - T3: weight 100 and capacity 250 before, during and after.
  - T5: he regrows to shape 1 and walks.
  - T6: the 708 children are unchanged.
  - T2: the tiny Avatar walks and runs (PARTIAL: per-step distance not
    measured).

  The crack passage is tracked under the crack item.
- [x] The keyless gates 170 and 180: researched
  (`docs/reviews/2026-09-25-keyless-gates.md`); Douglas: "remove the two
  walk-path gates". Map 13's 170 and Map 10's 180 removed 2026-09-25, stubs
  kept; Map 10's cloud-terrace 170 and Map 18's 180 stay as scenery. Record:
  `docs/playtest-2026-09-25-gates-removed.md`.


### 1. Dialogue & codegen — open items

Decisions wanted:

- [x] **Steps 11-12's key arc was dead in the shipped source (2026-08-17,
  F14/F15/F17) — E5/E6 + T1 REVIEWED AND CLEARED 2026-09-05.** Each claim was
  re-checked against the corpus rather than taken on trust, and all of them
  hold:
    - `spokePoison` and `spokeFuneral` have **zero writers** anywhere in
      `lv-usecode/`, so the arc really was stranded. E5/E6 add one token each,
      at the branches where the Avatar actually says those lines
      (`lv-patched/EZREKAL.UNK` cases at :1241 and :1270, writes at :1250 and
      :1285). Minimal and correctly placed — **blessed**.
    - T1 is one character (`cliffs` -> `Cliffs`, TYORVI.UNK:957). The compiler
      compares the English text exactly and the menu-add uses a capital C, so
      the case could never match. Patching the CASE rather than the ADD is
      right: the add string is the one players have already seen. **Blessed.**
  Both were verified in-engine on 2026-08-17 (arc played to the Key to the
  Clouds, `givenTea` 1) and remain in the build. **Still open, unchanged:** the
  F14 dead option ("She had little to say.") is still caseless.
- [x] **`testFromThordis` has no writer** (2026-07-28) — **T2 REVIEWED AND
  CLEARED 2026-09-05.** Verified against the corpus: `testFromThordis` has
  **zero writers** anywhere, while `thordisToldTest` is written in the
  *recovered* THORDIS at her own referral sites (original lines 1213, 1243).
  So the two reads really were dead, and re-pointing them at the live flag is
  the exact complement of ATLI's accepted guard. The patch touches only those
  two reads. **Blessed.**

  The same file's restored Passage Test speech was checked line-by-line
  against `TESTPLAN.UNK:195-224` (its source) and **two transcription slips
  were found and fixed**: a dropped comma after "the Great Cataclysm" and
  "can not" for "cannot". The restored speech now matches the 1994 text
  exactly. Verified in the built FLX (4 occurrences of each corrected form,
  zero of the old).
- [ ] **OPEN DECISION for Douglas (2026-07-19)**, (c) only: the special
  root still renders as a snake-skin (no frame of 399 reads as a root);
  it stays on the art list. Done 2026-10-08:
  - **(a)** The restored Shield is shape 828 quality 83, with
    `lv-new/AORTA.UNK` for its look (`2c222ba`). Verified in ScummVM
    (`docs/playtest-2026-10-08-batch-b.md` S1-S6):
    - the ceremony makes 828 q83, which draws as the quartered oval;
    - it can be carried but not equipped, and it looks "Ceremonial Shield
      of the Ancients Ones";
    - the altar sets `godsFree` (S4 reached `templeOpen` after a debug
      teleport into the sanctum);
    - the altar refuses a 539 frame 2 and Pagan's 828 q0, which still looks
      "Zealan ceremonial shield".

    The altar does not use the shield up (finding).
  - **(b)** The elixir uses frame 5, not 0, because frame 0 is the Blood
    reagent and the drink's foreach would consume carried blood
    (`a229d63`). Verified (`-batch-a.md` E4): it draws as a red vial.
    Finding: it is created with quantity 0, so it looks "0 vials of blood".
- [x] **Decision queue from the steps 9-12 repair.** The special root stays
  at the Sacred Circle (Douglas 2026-10-08). Ezrekal's brewing wait is
  restored (`a229d63`). Verified in ScummVM 2026-10-08
  (`docs/playtest-2026-10-08-batch-a.md` E1-E3b, E5):
  - the root gives "…ready yet?";
  - 14 picks gave 9 patience barks, covering all three lines, and 5 silent
    picks (the 1994 `urandom(4)` has no case for 0);
  - no hand-over is offered until she leaves the fast area, then it works;
  - a save/reload or map switch never dead-ends;
  - the replay guard holds.

  Vial, key and newt art stay on the placeholder list.
- [ ] **Orphan decisions** (2026-07-26 triage, decision D residue):
  `TYPEZEALANCHILD1` is an Actor class needing promotion but the npcNum
  window 100-116 is full; `TYPEPOISONPLANT` re-introduces uncurable poison —
  recommend retiring (Douglas 2026-10-08: keep open); `TYPEPEDESTALS`
  blocked on allowlisted EALOGO.

Compiler bugs:

- [x] **"Tell me more of the Test" did nothing** — the multi-value `case`
  codegen invented an idiom retail never used. Fixed in `ae6eda2`
  (2026-08-12). Verified in ScummVM 2026-10-07
  (`docs/playtest-2026-10-07-wave2-final-a.md` A3): picked from the screen,
  Atli answers "Very dangerous it is...".
- [x] **Annotation-less `startup{}process{}` compiled to an empty stub.**
  Fixed 2026-10-02 (`81deebd`): a `process {}` block loops with a suspend at
  its head, as retail compiles it; verified with the LORDBRIT puppet (see the
  Lord British apparition item above).
- [-] **PT_* and day-period constants compiled to `push 0`.** Pinned from
  retail in `d32fa37` (2026-08-12, `test_pt_period_constants.py`); the
  resetRef sites are exercised in every 2026-10 conversation run
  (`I_resetRef ... type=0x0205` etc.). `safeTeleport` stays uncalled (see
  "NPC schedule destinations" under Found 2026-10-07).
- [x] `\g` without a preceding `\f`: not a defect (2026-10-07). 134 compiled
  strings have it; the lexer cuts at whichever marker comes first and no
  compiled class carries a leftover marker byte.
- [x] String concatenation in bark/ask expressions: `+` on strings emitted
  add (0x14), and the lexer stripped a literal's edge spaces ("Yes, I
  amAramina."). Fixed 2026-10-07: concat (0x16) as retail ARAMINA 0x40D
  1146, spaces kept. Verified in ScummVM (`-last-b.md` M3): Aramina's
  "'Tis a grand day, friend Avatar." and "Yes, I am Avatar." read
  correctly.
- [x] Nested `if`/`else if` chains inside case bodies: no defect; covered by
  `test_uc_dialogue.py`'s case-body walks (2026-10-07).
- [ ] **foreach caution** (from the 2026-07-04 loopscript fix): filters were
  match-everything before it, so dialogue foreachs that "worked" may have
  passed by item-order coincidence — re-check during dialogue passes. The
  2026-10-07 TYPE_SHAPES retail audit (41 values) changes what several
  searches find; see its table in `u8c_symbols.py`.
- [x] **Parser silent error-recovery masked partial compiles.** All 57
  recovered errors in the compiled tiers are closed (wave 1 and wave 2,
  2026-10-07); `PARSE_ERROR_BASELINE` is empty and `test_parser_all.py`
  pins 5 issues, all in files the build does not ship. An unresolved call
  used as a value pushes 0, not a stale retval. Verified with the wave-2
  sessions above.

Smaller open threads:

- [ ] Step 11-12 order dependency (playable, no fix needed): Tyorvi must be
  visited before Ezrekal accepts the root (`tyorviDreams`). Documented, works.
- [ ] Cosmetic spellings remaining ("Zeleans"/"Zelean", "Gunnar's"): open in
  ATLI ×1, TESTPLAN ×1, SHADES ×1, RAGNAR:441-442 ("Gunnar clan" variant),
  THORDIS ×10+1 — the THORDIS sweep was left undone ON PURPOSE: three of the
  ten sites are an askList add, its case, and its removal, and must move
  together or the option stops matching its handler.
- [x] Ezrekal's step-18 reagent-bag reward was bark-only in the 1994 source
  (no create/give call). Authored 2026-09-27: her "I have freed your gods!"
  gives the bag once. Verified in ScummVM 2026-09-27
  (`docs/playtest-2026-09-27-bag-ezrekal.md`) and again 2026-10-07
  (`docs/playtest-2026-10-07-wave2-c.md` C1: one bag, six stacks of 25, no
  second bag on a second ask).
- [-] Atli initial bark not displaying ("What? Who are you?") — may be bark
  timing on non-Actor pillar items.
- [-] Orphaned event-script warnings: SIGRID's `daytide`/`firstebb`/
  `ACT_LOITER` are pinned since 2026-08-12 and 2026-10-07; only
  `safeTeleport`, held back on purpose (see "NPC schedule destinations"),
  still warns.
- [-] **Sigrid: slot clean, class alive, `use()` still unobserved**
  (2026-07-28). Slot 102 is a proper Actor again and class 1126 dispatches
  for schedule/enterFastArea/leaveFastArea. The old "never dispatches"
  symptom is explained (the egg-promotion collision, fixed); re-test `use()`
  by pinning her or teleporting on top of her rather than chasing.
- [ ] **EGGMAGNET 281 + EGGCANDLETRICK 280 — deferred**, blocker list exact
  (detail beside the obelisk in `build_map_17.py`): (1) H1 blocks it —
  CANTRK has no explicit wait, a naive loop fix hangs the VM; (2) nothing
  can light a candle; (3) no candle art fits the contract (frame 0 unlit);
  (4) MAGNET's pop coordinate needs retargeting. npcNum 237 → class 1261 is
  free when written.
- [ ] Polish: MYTHRDLG "Let us speak of other matters." restarts the stock
  conversation at "Hello" mid-conversation. Reword the option or (fragile)
  jump past the greeting. Low priority.

### 2. NPC Dialogue — Testing Each NPC

Each named NPC has a stand-in on Map 10. All tested at least partially; none
exhaustively on every branch.

| NPC | Source File | Class ID | Status |
|-----|-----------|----------|--------|
| Atli | `lv-patched/ATLI.UNK` | 0x046B | [-] Working. Some paths untested. |
| Thordis | `lv-patched/THORDIS.UNK` | 0x046A | [-] Tested, not exhaustive |
| Ragnar | `lv-patched/RAGNAR.UNK` | 0x0469 | [-] Tested, not exhaustive |
| Hrodny | `lv-patched/HRODNY.UNK` | 0x0471 | [-] Tested, not exhaustive |
| Ingjald | `UNK files/UNK/INGYALD.UNK` | 0x0470 | [-] Tested, not exhaustive |
| Tyorvi | `lv-patched/TYORVI.UNK` | 0x0473 | [-] Tested, not exhaustive |
| Ezrekal | `lv-patched/EZREKAL.UNK` | 0x0474 | [-] Tested, not exhaustive |
| Sigrid | `lv-new/SIGRID.UNK` | 0x0466 | [-] `use()` unobserved (§1) |

Class id = 0x400 + npcNum (the 10-03 run logs `event 1 @ 046A:0CA7` for
Thordis's `use()`). Corrected 2026-10-07; the table carried 0x0437-0x0446.

**Test procedure**: `MainActor::teleport 10 19200 6400 0` → walk to NPC →
double-click → exercise the tree organically (never force-drive picks — the
game offers dead look-alike options the sim can't see).

### 3. New Dialogue Scripts (Written by Us)

| Script | Purpose | Status |
|--------|---------|--------|
| MYTHRDLG | Mythran quest exposition | [x] Wired + verified in-game 2026-07-03 (all three acceptance paths); re-verified organically 2026-08-16 — full Vale tree, all four mythranTold* flags read 1. CAVEAT: cheats ON turns his talk into the retail dev menu |
| LORDBRIT | Quest step 1 message scene | [x] Verified in-game 2026-07-04 (Tenebrae gate + Map 8 backstop); backstop re-verified ORGANICALLY 2026-08-16 (walk-in at (2200,2230), lbDone=1) — but see the camera defect below |
| SIGRID | Hunter NPC, Cloud Cliffs | [-] Compiles; `use()` unobserved (see §1) |
| AOSCENE | Ancient Ones ceremony | [x] Played in-engine 2026-07-28 (godsFree 0→1); **camera pan added and verified 2026-09-14** — walked in from (3300,8600) on map 18, godsFree 0→1, frames 0/2/1 → 3/5/4, and the camera re-attached: Felicitar read px=(339,−57) after a 232-unit walk, the exact value the projection predicts. `docs/playtest-2026-09-14-camera-pan.md` |
| CLCLIMB | Cloud cliff climbing | [x] Verified in-engine 2026-07-27 (`attemptedCliffs` fired) |
| COLPUZZL | Elemental column puzzle | [x] Full solve in-game 2026-07-04 |
| ENDGAME | Endgame sequence | [x] Played in-engine 2026-07-28 ("The Vale is restored."); since 2026-09-27 it no longer gives the bag (Ezrekal does) and its egg sits on Map 10's arrival pad (2026-09-29); last replayed 2026-10-07 (`docs/playtest-2026-10-07-wave2-c.md` C1) |

- LBSCENE Map 8 backstop confirmation pass DONE 2026-08-16: apparition
  cleanup ✓, but **the backstop path never restores camera tracking** —
  the camera stays scene-anchored forever (persists through save/load).
  The map-39 primary flow is camera-correct, so the fix is scoped to
  LBSCENE.UNK's backstop branch. `docs/playtest-2026-08-16-lb-mythran.md` F2.
- [x] **The engine SIGSEGV is FIXED (2026-08-18) — and it was never the
  climb.** F1 blamed the hang-grab leap; the actual defect is a
  use-after-free of `Ultima8Engine::_avatarMoverProcess`. The engine holds
  a RAW pointer to a process the Kernel owns and deletes, and nothing
  cleared it on death. Loading a savegame trips the kernel's runaway guard
  ("Seem to be stuck in process loop") which fail()s 8 processes — one of
  them the mover — and the first input afterwards dereferences freed
  memory. Jumping is merely the first thing that presses SPACE after a
  load; ANY input crashed it. Fixed in fork commit `312c76e9`:
  `AvatarMoverProcess::terminate()` clears the pointer, and all five
  previously-unguarded dereferences are null-checked (GameMapGump mouse
  handlers, the modal branch that runs for the load book and death diary,
  saveGame's getPid, QuickAvatarMoverProcess). Verified by gdb backtrace
  before and after. Record: `docs/engine-2026-08-18-f1-segfault.md`.
- [x] **The map 8 cave ascent WORKS (2026-08-19).** The Avatar climbs from
  below onto the z=56 main floor: instrumented log shows `climb56 ->
  SUCCESS`, final position (29364, 23622, 56), reproduced 2 of 3. The
  blocker was never geometry and never the engine — it was INPUT.
  `handleNormalMode`'s jump branch needs MOVE_JUMP **and**
  MOVE_ANY_DIRECTION, the climb scan inside it runs only when
  MOVE_MOUSE_DIRECTION is CLEAR (so the direction must come from a
  keyboard action — stock UP/DOWN are MOVE_FORWARD/MOVE_BACK and qualify),
  and critically **SPACE must be HELD, not tapped**: a tap clears MOVE_JUMP
  before any frame where the Avatar is not busy. Recipe: mouse-walk into
  the wall to set facing (checkTurn is mouse-gated), release, hold UP, hold
  SPACE. Caveat: the full ascent was run with an extra MOVE_DOWN binding
  since reverted; on stock bindings a climb was seen (z=8→16) but the full
  48 was not re-run. Record: `docs/engine-2026-08-18-f1-segfault.md`.
- [x] **CONFIRMED ON STOCK KEYBINDINGS (2026-09-01), with two corrections
  to the recipe.** `~/.config/scummvm/scummvm.ini` still carried the four
  `keymap_ultima8_MOVE_*` lines, so they were stripped first; with a
  genuinely stock config the ascent runs **5 of 5** from a standing start
  at (29524, 23622, 0), landing on the z=56 floor at (29364/29372, 23622,
  56). Corrections: (1) **SPACE goes down BEFORE the direction key** — a
  held SPACE buys exactly ONE climb attempt (MOVE_JUMP is set on keydown
  and cleared inside the branch), so leading with UP spends it several
  hundred units short and gives 0/2; (2) the facing is **west** (`dir=12`),
  not north as HANDOFF said. **The window is 17 units wide**: climbs at
  x 29508–29524, fails at 29500 and 29532 (y is wide — 23600/23622/23650
  all climb). Walking at it while mashing SPACE missed 2/2, and from the
  z=8 trench start the one jump fires at the start position and only drops
  him to z=0 — so the ascent is a two-stage move in a black void with no
  landmark. Reachable with the shipped keymap; hard to find by accident.
  Record: `docs/playtest-2026-09-01-stock-bindings-climb.md`.
- [-] **Superseded — the old "blocked by geometry" entry**
  (2026-08-18).** With the crash fixed, the z8→z56 ascent was attacked
  directly and does not work: (a) an `exact_reach` flood over the whole
  south cave reaches levels 0 and 8 ONLY — no walkable route up anywhere;
  (b) the 48-unit face refuses the climb scan, because the Avatar's 64-deep
  body box cannot get closer than 16 units to it and `climb48` fails from
  there; (c) the hang cannot be triggered at all — `AvatarGravityProcess`
  needs `MOVE_ANY_DIRECTION`, which is set only inside `handleNormalMode()`,
  and `AvatarMoverProcess::run()` returns early while falling, so the flag
  can only be set on the ground; dropping beside the face from z=40/48/56/64
  fell straight through every time. **This is now the thing standing between
  the exit test and a continuous playthrough.** Decision needed: add an
  intermediate step to the ascent (two risers of <=32 climb fine and sit on
  the 4-unit lattice) or find the retail route, which may be somewhere this
  session never looked. **Two corrections landed 2026-08-19**: the Avatar
  HAS every climb animation including `climb48` and `hang` (read straight
  out of `STATIC/ANIM.DAT`, shape 1 actions 19-26 and 45 all present), so
  F1's "plain climbs max out at climb40" is wrong; and most of the 309
  "+48 rises" off the trench are the roofed underpass's stacked floors,
  not ledges — (29823,23519) is standable at BOTH z=8 and z=56. Also
  confirmed: the pristine base map gives byte-identical reachability, so
  WE DID NOT BREAK THE CAVE. Try a human-driven running jump at a real
  ledge face before editing retail terrain.
  Record: `docs/engine-2026-08-18-f1-segfault.md`.
- [x] **The "teleport wedge" is DIAGNOSED and FIXED (2026-09-06) — and it was
  never geometry.** For weeks this was recorded as "teleports wedge; landings
  snap to chunk seams and/or settle below the floor". It is not. The Avatar
  emits **zero `event 18`** when wedged — he is not being blocked, the mover
  is not running at all. (A geometry block gives justMoved spam with no
  displacement; that distinction is the whole diagnosis.)

  Chain: the kernel's runaway guard (`Seem to be stuck in process loop`)
  fail()s processes during a heavy save load, and `AvatarMoverProcess` is one
  of them. The 2026-08-18 use-after-free fix stopped the resulting CRASH but
  left the mover **dead**, so input reaches nothing. Worse, a savegame stores
  the kernel's process list, so **the dead mover is baked into every save
  taken afterwards** and reloading cannot recover it — which is why "wedged"
  states seemed to follow the player around.

  Fixed in `ultima8.cpp` `loadGame()`: if the saved mover pid does not resolve
  **or resolves to a terminated process**, recreate it instead of refusing the
  load. Verified against a save that could not move at all: the engine logs
  `Terminated AvatarMoverProcess in savegame; recreating` and the Avatar goes
  from 0 to **65** move events and walks. Tracked patch regenerated (12 files).

  Also cleared on the way: a stray `ACT_INCOMBAT` (0x800) from a leaked `c`
  keystroke will silently stop right-drag walking — check actor `flags:` for
  `c00` before blaming the map.

- [ ] **Undiagnosed: why a savegame load trips the 65534-run guard.**
  Intermittent; `kernel.cpp` already carries a WORKAROUND comment about that
  threshold and U8 map transitions. The crash it caused is fixed, but the
  runaway itself is real and still there.

- [x] **DECISION: does map 8's south route get floored?** **No: accepted
  as-is by Douglas 2026-10-08**; the trial diff stays unapplied. The gate approach is
  reachable from `cp3h` at z=0 with no climb at all, but several thousand
  units of it are floorless void — the engine's `z <= 0` freebie support
  carries the Avatar over nothing and it renders as blackness. That is the
  project's own broken-design rule, on the critical path, in retail geometry.
  Floor it, or accept it. Record:
  `docs/playtest-2026-09-01-stock-bindings-climb.md`. **Rendered 2026-09-25**
  (`docs/playtest-2026-09-25-map8-floor.md`): a 184-tile floor of shape 301
  under the 7,464-unit run is invisible from all five positions, because the
  retail cave above draws over z=0; the floored build climbed the cave
  ascent 4/4 against 2/11 on canonical, cause unread. The trial diff is kept
  there, not applied. **Cause read 2026-09-26**
  (`docs/research/2026-09-25-cave-ascent-jump.md`): the engine checks
  support only where the climb lands, so the floor cannot change it; on
  canonical the ascent went 10/10 with combat mode clear, and both
  combat-on attempts failed, ending where the 09-25 failures ended
  (`docs/playtest-2026-09-26-steps-15-18.md` part C). The 2/11 was leaked
  debugger keys switching combat on. Nothing argues for the floor now but
  the strict path model.
- [x] **DECISION: keep the map 8 cave ascent as-is?** **Kept by Douglas
  2026-10-08.** It works on stock keybindings (5/5), but the launch window
  is **17 units wide** with no landmark, and it is not required: it leads
  to a pocket.
- [ ] **Unexplained, seen once (2026-09-05):** left standing in the trench
  void with no input, the Avatar was found on **map 0** at (15967, 19711, 0)
  and back on map 8 a moment later. No teleport egg is anywhere near. Not
  reproduced. Probably the Guardian cutscene (2026-09-25): `traps.md` has
  that cutscene teleporting the Avatar to the same (15967, 19711, 0).
- [ ] **Map 8 structural facts found during the run — do not rediscover.**
  The map has at least two large disconnected z=0 regions:
  `cp4-mythran-approach` sits in a 5,840-cell pocket that does NOT contain
  Mythran (his is a separate 11,552-cell region; the save name misleads), and
  `exact_reach --map 8` reproduces both. The map-8 LORDBRIT backstop egg is
  **not walk-reachable** — no standable cell inside its +/-128 box is reachable
  from the approach region and its own cell reports `levels here: []`. The
  scene fires correctly once you are in the box, so this is placement, not
  wiring; the primary step-1 trigger is on map 39 at (17150, 19700, 48).

### 4. Map Quality

- [x] **Rebuild the 1994 screenshots exactly (rule set 2026-10-16). DONE
  2026-10-17: all 19 published shots are in the build.** Each published
  shot is one of the only areas whose look we actually know, so the build
  reproduces it and everything else is extrapolated around it.
  - **Method.** Each shot was decomposed by exact template matching
    (`shot_decompose.py`), solved to world coordinates, and is now a
    vignette (`agents/map-populator/src/vignettes/screenNN.json`) stamped
    verbatim by `vignette_place.stamp` with closure terrain around it. The
    1994-only art is shapes 874-881, imported index for index from
    `shared/data/lv-1994-art/` (`png2shape.py --indexed`). The 860 gods
    hold the 1994 statues, with their shatter frames redrawn at the 1994
    scale.
  - **Retired and moved.** 861 and 862 are retired. 870 is kept as a copy
    of 878 so older saves still work. Every pin move the shots imply was
    made, on Maps 9, 10, 11, 13, 17 and 18; the list is in each vignette's
    `placement.pin_moves`.
  - **Guarded by** `test_vignettes.py`, which holds a per-shot floor on the
    built window and limits the void pixels inside it.
  - **Verified 2026-10-17 in ScummVM.** All 19 windows were captured; the
    scores are in
    `docs/research/2026-10-16-screenshot-reconstruction/ingame/SCORES.md`
    (screen11 98.2%, screen04 95.3%). The gap to 100% is the 1994 actors
    the engine does not place, the Avatar's pose, animation, and the GHOST
    follower. Four verifier passes:
    - `docs/playtest-2026-10-17-vignettes-verify.md`, `-verify2`, `-verify3`
      and `-verify4`.
    - The Map 18 ceremony runs end to end with the 1994 gods and Shield 879,
      and on the legacy 828 path. The ending is word for word the same.
    - The Map 13 climb walks with no bounce and no paint knots.
    - Old saves holding 870 halves work.
  - **Phase D, 2026-10-25 (Douglas: draw all the missing actors; cut and
    redraw the screen12/13 pieces; leave the Map 13 north-edge black).**
    - **Static art:** 882 nook dais, 883 walkway east end (strips A and B
      now end at x 4095), 884 gold/cloud edges, 885 side throne, 886
      screen13's floor tiles, and 865 f2 completed as the 1994 Pillar of
      Fire.
    - **Actors:** 888 Zealan elder (Atli's body; Mythran 190's frames
      restyled), 889/890 the spear children (npc 104/111; the child 708's
      frames at 0.8), and 872 restyled to the 1994 Water Zombie. Each holds
      its shot pose verbatim.
    - **Reports:** `docs/research/2026-10-16-screenshot-reconstruction/phaseD/{static,actors}/REPORT.md`;
      contact sheets `phaseD-{static,actors}-contact.png`.
    - **Verified in ScummVM** (`docs/playtest-2026-10-25-phaseD-verify.md`,
      `ingame/SCORES-2026-10-25.md`): screen07 86.06 → 89.93, screen12
      85.90 → 96.37, screen13 75.97 → 93.99. Every new actor frame drew
      whole in play, and the Map 17 route and both halves work. No shot
      regressed on map content.
    - **Actors and scores:** the actor shots (02/09/19/20) cannot gain
      in-engine. The zombies exist only after a hatch, and the NPCs walk
      their schedules. Built-window gains: 02 95.96 → 98.40, 09 → 94.84,
      19 → 97.08, 20 → 97.70.
    - **Merge regression, fixed:** the merge lost npc 111's map pin, so
      the screen19 stamp dropped the child from Map 10 (FIXED 995f4395).
      The pin is restored (FIXED 9e666935), and test_schedule_destinations
      now requires one record for each npcNum 100-116.
  - **Open:**
    - **Douglas's art review, 2026-10-30** (cards on
      `https://devhost.invalid/lostvale-art/simple.html`):
      - **Accepted:** 1 screen12 nook art; 5 the odd 886 tiles; 8 the
        Water Zombie (including the club in frame 81 only).
      - **Phase E, 2026-10-30, the items sent back.** Merged (`wt/cloud13`,
        `wt/pillars11`, `wt/actorfix`); FIXED 7d7e2c93, U8SHAPES 2b274856,
        TYPEFLAG e25d7224. Verified in ScummVM
        (`docs/playtest-2026-10-30-phaseE-verify.md`,
        `ingame/SCORES-2026-10-30.md`; no shot regressed on map content).
        Reports in `docs/research/2026-10-16-screenshot-reconstruction/phaseE/`.
        - Card 2, screen13: the cloud floats 96 above the earth and draws
          over the tree, both mushrooms (the hidden one is retail 65 f0,
          now placed) and the spire feet. 93.99 → 97.02. 73 island cells
          under the cloud are curbed off, so the Avatar is never hidden.
        - Card 3, screen07: 89.93 → 96.00. Changes: the notch was filled,
          the cliff run on, 891 wall faces and 892 lava-glow floor (patch
          rows: shot pixels over retail frames).
        - Card 4: earth, air and water (865 f0/1/3) are redrawn in the
          fire pillar's 1994 style, with the same canvas and footprint.
          All four receptacles were used in the game and each destroyed
          its own pillar.
        - Card 6, elder: the short cane in every frame. The SE talk
          gestures through 70/71/72, with 71 the exact screen19 pose.
        - Card 7, children: no black outline, and the spear is held in
          the right hand in every frame. The verify could not catch them on
          screen; the actorfix slice's own plates show them.
      - [x] **Round 2 sign-off, Douglas 2026-10-31: 1b, 2-5 a.** Cards 2-5
        (screen07, the pillars, the elder, the children) are accepted.
        Card 1 (screen13) is accepted with the island left open under the
        floating cloud: the Avatar can walk there and is hidden while he
        does. The phase E curbs on those cells are removed, which opens 75
        cells (FIXED fc92ee5f). **Verified in ScummVM 2026-10-31**
        (`docs/playtest-2026-10-31-island-open.md`): he walks in and out
        of the cells under the cloud and is hidden there; the outer edge
        holds; screen13 still scores 97.02; the climb route works; there
        are 0 paint cycles. **The phase D/E art track is signed off.**
    - [x] **Water Zombie balance.** One zombie killed an armed 30-hp
      Avatar in about 10 s (2/2), and wave 1 did it in about 8 s
      (`-phaseD-verify.md` F2). **Douglas 2026-10-30: weaken it.** The
      `[waterzombie]` row (`lv_monsters.py`) went from hp 35-50, damage
      6-12, dex 14-16, armour 15 to hp 25-35, damage 3-7, dex 10-12,
      armour 8. **Verified in ScummVM 2026-10-30**
      (`docs/playtest-2026-10-30-zombie-balance.md`):
      - armed, 10 of 10 wins: axe wave 1 4/4 (19.5 hp left on average),
        sword wave 1 3/3 (6.3 left), axe vs a single zombie 3/3;
      - unarmed, wave 1 still kills;
      - no drownings; all 21 hatched zombies read hp 25-35.
    - [x] **Summit harpie strength.** In the phase E verify, the summit harpie
      killed an axe-armed 30-hp Avatar 3 of 3 times (`-phaseE-verify.md`
      F1). **Douglas 2026-10-31: weaken it.** The one `[harpie]` row
      (`lv_monsters.py`) serves every harpie; it went from hp 30-45,
      damage 5-10, armour 11 to hp 22-32, damage 3-7, armour 8. **Verified
      in ScummVM 2026-10-31** (`docs/playtest-2026-10-31-harpie-balance.md`):
      - armed, 14 of 14 fights won, never below 18 hp (summit axe 4/4,
        sword 3/3; top 3/3; the full climb, all four harpies with no rest,
        30 → 25); unarmed vs one lane harpie also won;
      - control, old stats with the same fight loop: the summit with the
        axe was 6/6. Standing and fighting already won; two of F1's
        deaths were runs past the harpie to 209;
      - running past it still kills: 2 of 3 dashes from the turn to 209
        died with the new stats, because the live harpie stands in the
        summit neck the route passes through. Stats cannot fix that.
    - [x] **The run-past death at the summit.** Running past the summit
      harpie to 209 can still kill: it stands in the neck. **Douglas
      2026-10-31: leave it.** The fight is easy now, and fighting is the
      expected answer.
    - [x] Map 11: after a debug hop onto the map (not through a pad), the
      four talismans lay on the floor again while the carried ones stayed
      in the pack (`-phaseE-verify.md` F4). **Not a defect (2026-10-31,
      `docs/playtest-2026-10-31-talisman-reentry.md`).** Real walk-ins
      through pads 203 and 204 fire EggReapply, which removes carried and
      used talismans and keeps a destroyed pillar down. Only a debug
      teleport, which skips the pad, brings them back, and walking onto a
      pad then clears them. Recorded in `traps.md`.
    - Map 13's summit sees past the map's north edge. **Douglas
      2026-10-25: accepted.**
    - The GHOST 411 follower from `AVATAR.UNK` (predates this work).

| Map | Name | Status | Issues |
|-----|------|--------|--------|
| 08 | Plateau (modified) | [x] | Entrance re-verified end to end 2026-07-31 (key → doors → Map 9). Unlock idiom: double-click the KEY, then click the door. Known retail-correct hazard: a wandering ghost can park in the doorway ("blocked" bark) — runtime spawn, not fixable from FIXED.DAT. Record: `docs/playtest-2026-07-31-doors-investigation.md`. The cave stepping-stone chamber (retail geometry) crossed in-engine 2026-08-16 — route + jump physics: `docs/playtest-2026-08-16-pool-crossing.md` |
| 09 | Galjeron's Chamber | [x] | **Rebuilt 2026-09-15** (cleanup plan): continuous cave ceilings over the passages (37 — 34 draws as a red tiled roof in-engine), none over the cavern, two-course cavern walls with lintels, the open north shoulder walled, the lair dressed, the last stretch in worked stone with columns. Hygiene row zero; route/walkability green; three zones shot in-engine at 640x400. Finding: the journal (613 q1) has no LV handler — double-click runs Origin's book class 613 with quality 1 (map_pins.json). First visual test PASS 2026-08-17 (walked zones 1-3 in ScummVM, trigger 202 → Map 11). Record: `docs/playtest-2026-08-17-vale-steps-3-8.md` |
| 10 | Lost Vale overworld | [-] | **Landscape pass 2026-09-15** (cleanup plan): the vale closed by a two-course cliff rim with a crest (lv_landscape.rim over one TERRAIN table; the 80 void chunks inside the outline filled), the 256-spaced pickets, 19 chimneys, Ezrekal's six floating roof squares and the 126/127 "crops" gone; cobble tracks and a gravel riverbed, palisades with gates on the track lines, a wood-plank stockade for Ezrekal, stone ruins at Moriens' and Ragnar's, standing stones on paving at the circle, a deck and pier on the lake, a terrace and canyon at the cloud approach, a colonnade at the temple approach, dead trees and outcrops. **Two quest sites were unwalkable**: the Passage Test corridor climbed 24-unit terraces and Ragnar's cache 16/24-unit steps — the engine steps 0/±4/±8 only; both re-stepped (ramp of 8-unit rows; flagstone stair) and now goals in test_route_reach (70/70). Hygiene row zero; run_map10 37/37; pins unmoved; fourteen sites shot in-engine. Finding: SI_DRAW flats (301, 386) laid over a glob floor draw UNDER it — overlays must be 6/71/425/783 (lv_shapes). Villages Phase 1 visually verified 2026-07-01. 2026-08-17: Atli/Ragnar dialogue trees PASS in-engine, BUT (a) NPC loiter is unbounded — Ragnar wandered into negative-coord wraparound, step 7 referral untriggerable (F1); (b) Passage Test scene stalls after its pops (F2); (c) shipped lake/island does not match current builder source — rebuild and re-derive (F4); (d) Atli's lake line says "east", lake is SW (F9). Record: `docs/playtest-2026-08-17-vale-steps-3-8.md` |
| 11 | Elemental Dungeon | [-] | **Rebuilt 2026-09-15** (cleanup plan): 421 chunk-stride ceiling tiles, 48 loose reliefs, chests and decorative chimneys gone; entry hall, hub, pillars chamber and pad in the stone-wall pair on flagstone with columns, lamps, tapestries (the pad gate is 120 tall now, three stone courses); Fire on scorched earth with lava-yellow lakes and dark raised causeways; Air on grey rock with two stepped terraces and hanging spires; Water's islands real; Earth's talisman in an alcove. Every pin unmoved; `test_route_reach` proves all four talismans and the chamber reachable by a route that never stands on a damaging tile. Hygiene row zero; five rooms shot in-engine at 640x400. Water stays dry (SEA drowns — gameplay queue). First visual test 2026-08-17: Four Pillars chamber renders, COLPUZZL receptacle works in-engine (bark, talisman consumed, pillar destroyed, EarthColumnDestroyed=1). FIXED 2026-09-06: the 3 unclickable talismans were not on a marker grid — frames 0/2/3 of shape 596 are 5x7 and 5x4 sprites that tie the floor tile they rest on in the sort order and are drawn under it (frame 1, 11x14, always worked). They now sit at z=4, which breaks the tie; Earth, Fire and Water all probe and drag into the pack. Records: `docs/playtest-2026-09-06-step4-talismans.md`, `docs/playtest-2026-08-17-vale-steps-3-8.md`. **The map had no edge until 2026-09-19.** `exact_reach` seeded at both arrival pads over the footprint plus 3,000 units reached 309,402 of 314,131 standable positions, bbox x 31..21023 y 31..25119 against a footprint of x 1024..19455 y 1024..23551, so the Avatar could walk off in every direction (the engine supports any position at z<=0). `build_rim()` closes it with `lv_landscape.rim`, the chunk set read off the emitted glob eggs, two courses of the 26/32 cave wall this builder already uses plus a crest, 3,207 items. The same flood now reaches 146,920, bbox x 1119..19423 y 1119..23519. Walked in ScummVM on a fresh world 2026-09-19: twelve north-west bursts from (1400, 1400, 0) stop dead at (1088, 1088), one unit clear of the rim's boxes, and ten east bursts across the air section stop at x=19408. Record: `docs/playtest-2026-09-19-map11-rim.md` |
| 13 | Cloud Cliffs base | [-] | **Dressed as a cliff 2026-09-15** (cleanup plan): each zone's flanking walls stacked in 48-unit courses to the path's height there plus one, one or two courses of rock under the drop side of every ledge tile from z=48 up, dressing on the valley floor or on the path's own lanes at the path's z (the bone piles at z=34..48 beside the path, rocks at z=8+2i, cliff details at z=80+2i and the harpie zone's 36 tiles with 1-unit risers were phantom standing levels and are gone), the wide lanes in the path's own ground shape (128 drew as blue tiles), the gate in two stone stubs, a colonnade ruin on the summit. `climb_tiles()` unchanged; route, riser and lattice checks green; five spots shot in-engine. **Finding:** the gate (114) has lock id 170 and no shape-82 key anywhere carries quality 170 (map_pins.json derivation), so the gate is only ever bypassed — a wall across the valley would end the quest; the stubs leave it open. (Douglas: removed 2026-09-25 with its stubs kept; see the keyless-gates item and `docs/playtest-2026-09-25-gates-removed.md`.) **Climb WALKABLE 2026-08-18** — z quantized to the engine's 4-unit step lattice (`CLIMB_Z_STEP`); walked on foot in ScummVM, z 0→48 on the north leg and 48→56 on the east switchback, no teleport. The 2026-07-31 polyline rebuild was still unwalkable: risers of 1-2 are refused exactly as 9-unit ones are (F10's real cause). **Base→summit walked UNBROKEN 2026-09-01**: (4096,10240,0) → (4052,1012,120) in one run, no teleport after the start, z rising through all 31 lattice levels (0,4,…,120) and both switchback corners cleared. The 2026-08-18 PARTIAL was the harness, not the map — bursts shorter than a turn animation move nothing, a 3-tile look-ahead aims across a bend, and an unbounded stall retry overshoots a corner by 344 units. Records: `docs/playtest-2026-08-18-f10-climb.md`, `docs/playtest-2026-09-01-stock-bindings-climb.md`. **The map had no edge until 2026-09-19.** Walking south from the arrival pad carried the Avatar 3,300 units past the last item through unpainted black, and `exact_reach` over the base zone plus a void margin reached 130,913 of 131,961 standable positions: the whole plane, on every side, because the engine supports any position at z<=0. `build_rim()` now closes the outline with `lv_landscape.rim` (two courses and a crest, chunk set read off the emitted glob eggs), and the same flood reaches 58,722, bounded to x 1615..6655, y 15..12287. Walked in ScummVM on a fresh world 2026-09-19: ten south bursts from (3888, 11900, 0) stop dead at y=12288, the last terrain row. Three props that had always stood outside the terrain (two boulders 257 and 1 units south of it, the summit urn 769 units east of the paving at z=120) moved onto it in the same pass. Record: `docs/playtest-2026-09-19-map13-rim.md` |
| 17 | Cloud City | [-] | **Rebuilt 2026-09-15** (cleanup plan): the 148 ornament-piece picket walls, 37 chimneys, 160 floating roof squares, stool "plaques" and chest furnishings gone; zones re-laid so none overlap; every wall the stone pair, two courses, with designed doorways (plaza ↔ arrival on the teleports' axis, halls ↔ corridors, halls ↔ the rooms north of them); thrones on daises, the obelisk on a two-tier dais (z=16, same x/y), the scroll on a plinth, columns, tapestries, lamps; three cloud islands beyond the arrival wall. Pins unmoved; route goals (both halves, scroll, halls, trigger) green; hygiene row zero; five rooms shot in-engine. **Obelisk is custom art 861 and the cloud islands are custom art 862 since 2026-09-15** (art track items 1 and 2, `docs/art-track.md`; verified in ScummVM, `docs/playtest-2026-09-15-obelisk.md`, `docs/playtest-2026-09-15-cloud-tiles.md`). **The scroll is custom art 864 since 2026-09-21** (art track item 4, and the first carryable one: the Avatar can take it to Ezrekal; `docs/playtest-2026-09-21-message-scroll.md`). Finding: the void beyond the plaza wall is never cleared without `usehighres` — a player sees stale frames there. (Fixed 2026-09-16 by the void floor, see that row.) Northern half reconnected 2026-07-31 (shield halves were floor-disconnected) |
| — | **The void floor** | [x] | **Every LV map showed stale frames where a player can see void** (the engine never clears the frame without `usehighres`; `.claude/rules/map-geometry.md`, last section). `lv_furnish.void_floor` lays black 564 plates under every void cell within view of a floor, as the last line of every builder; `test_map_hygiene.py` counts what is left per map (`void_in_view`) and every map is pinned at **0**. Map 17 on 2026-09-16 (999 plates, `docs/playtest-2026-09-15-cloud-tiles.md` §V); maps 9, 10, 11, 13, 18 on 2026-09-17 (366 / 2,477 / 2,522 / 758 / 568 plates), each plated in-engine at its worst void-facing floor cell with `usehighres=false`: `docs/playtest-2026-09-17-void-floors.md`. Water counts as painted cover (the lake is glob 55, sixteen SI_SEA tiles). |
| 18 | Ancient Temple | [x] | **Rebuilt 2026-09-14** (`cf12959`, `5c88d3a`): glob 80's baked wall lattice gone from all four zones, walls 10/15, colonnades, dais, tapestries; verified in-engine at 640x400 in every zone, walked onto the dais. Record: `agents/map-populator/docs/map-18-ancient-temple.md` |

**Map cleanup queue (2026-09-14)** — plan and per-map briefs in
`docs/reviews/2026-09-14-map-cleanup-plan.md`. A row flips with a date and
what ran in ScummVM.

- [x] Phase 0 (2026-09-15): `map_pins.json` + `derive_map_pins.py` (147
  rows; the Sacred Circle ring is shape 65, and `TypeShortmushroom` is
  126 — the single Test Plant — so the ring is decorative), `lv_furnish.py`
  (`983c435`, Map 18 byte-identical) and `test_map_hygiene.py` (`89211b0`,
  ratcheted per map)
- [x] Map 09 Galjeron's Chamber (2026-09-15) — hygiene row zero, shot
  in-engine; see §4 row 09
- [x] Map 11 Elemental Dungeon (2026-09-15) — hygiene row zero, talisman
  routes in `test_route_reach`, shot in-engine; see §4 row 11
- [x] Map 17 Cloud City (2026-09-15) — hygiene row zero, routes green, shot
  in-engine; see §4 row 17
- [x] Map 13 Cloud Cliffs (2026-09-15) — climb untouched and still green;
  canyon walls stacked to the path's height, rock faces under every ledge,
  phantom-level dressing gone; shot in-engine. Finding: the cliff gate's
  lock (170) matches no key on any map, so the valley stays open around
  it — see §4 row 13
- [x] Map 10 Lost Vale (2026-09-15) — rim, tracks, palisades, ruins, the
  circle, the lake deck, both approaches; villages untouched; two quest
  sites re-stepped onto the z lattice (they were unwalkable); hygiene row
  zero, routes green, shot in-engine — see §4 row 10.
  **Walked 2026-09-18** (`docs/playtest-2026-09-18-map10-walk.md`): the
  quest spine walked in ScummVM, not flooded. The corridor ramp carries the
  Avatar z 0 → 72 and the cache stair z 0 → 56, both in one continuous walk
  with no stall — the two changes that were UNWALKABLE before the landscape
  pass. Arrival → Hoskuld's east gate → the gathering slab walked whole;
  the south gate, the cloud terrace riser, Ezrekal's stockade door and the
  lake pier each walked from their track point. Two findings: an actor
  whose map is 12 (npc 55) renders and answers a look on Map 10's lake
  island, and walking the open lane past the terrace's keyless gate (lock
  170) fires the Map 13 teleport on a player walk
- [x] Maps 08/39 — audited 2026-09-15: the additions are nine hand-placed
  items on Map 8 (chest, key, two z=1 marker slabs, the teleport pair, the
  LB backstop egg/apparition/slab) plus retail glob 933 re-placed without
  its seam wall, and three on Map 39; no wall runs, grids, reliefs or
  placeholders — nothing for the hygiene classes to catch

- [x] **Map 0's limbo items no longer ride into the next map** (2026-09-19)
  — `World::switchMap` guarded its writeback and fixed-item unload with
  `oldmap != 0`, and `CurrentMap::getNum()` returns 0 both for "no map
  loaded yet" and for map 0 itself, so U8's limbo map leaked its 63
  base-game-NPC records into whatever map came next: they drew, answered
  look-clicks, and became permanent in that map's dynamic list. Two of them
  stood on Map 10's lake pier. Guard now asks `CurrentMap::hasMap()`; fork
  commit `e0d6084d`, engine patch regenerated (18 files) and re-checked
  against the pinned base, ScummVM rebuilt. Verified in ScummVM on a new
  game: `MainActor::teleport 10 13895 18700 8` then
  `ObjectManager::findShape 200` gives 9 found with no Container lines (was
  16 with 7), `findShape 142` gives 4 with none (was 8 with 4), and the map
  trace carries the `Unloading map 0` line that only prints inside the
  guard. Gods (860), obelisk (861) and cloud floor (862) all still resolve.
  The map-0 excursion itself is the Guardian's first appearance (class
  0x0401 `AVATAR` at 0x1908, one-shot on global 0405): it stages the
  cutscene in limbo and teleports back, which is correct and is left alone.
  Every player triggers it once on first leaving the starting map, so this
  was a live defect, not a harness artefact. Diagnosis, disassembly and
  acceptance: `docs/2026-09-19-map0-limbo-carryover.md`. **Re-walked
  2026-09-19** on the fixed engine
  (`docs/playtest-2026-09-19-map10-rewalk.md`): all six Map 10 quest-spine
  segments walked again, `findShape 200` is 9 with no Containers and
  `findShape 142` is 4 with none both before and after, and the session made
  the map-0 transit with `Unloading map 0` in the log. The ramp resolved
  every riser this time (8, 16, 32, 40, 48, 56, 64, 72) and the stair
  likewise (8, 16, 32, 48, 56).

Open tasks:

- [x] **Picket-fence walls — READ THIS BEFORE TRYING AGAIN (2026-07-30).**
  Closed by the 2026-09-15 cleanup: Map 17's walls are the stone pair with
  designed doorways and Map 10 has palisades with gates on the track lines,
  each walked or shot in ScummVM (cleanup rows above). The 2026-07-30
  lesson still binds any new wall: Maps 10 and 17 were first attempted and
  REVERTED. The porosity IS the circulation on those maps —
  the walls were never given real doorways, so solidifying them SEALS the
  map (Map 09's zone-2 wall put the dungeon exit out of reach; Map 10's cut
  off the temple approach; both caught only by an Avatar-width flood). Each
  map needs doorways designed per route: make the run solid, then pass
  `gaps=[...]` to `wall_run_x/_y` centred on the passage. Wall shapes are
  directional pairs — 489(NS)/492(EW), 145(NS)/149(EW); Map 17 also needs
  492. Maps 09/13/17 have NO connectivity suite, so any wall work there must
  hand-verify with an Avatar-width flood from the arrival teleport. Related:
  the hardened quest gates are single walk-aroundable items until this
  visual pass adds funnel walls (2026-07-31).
- [x] 128-stride treatment for the remaining maps (2026-09-15: no LV map
  places a 26/32 run on a 256 stride any more — test_map_hygiene's
  glob80/baked/orn counters and the cleanup rows above). Still open:
  `u8_map.py` parses item z signed while the engine reads unsigned —
  normalize or lint negative z in builders.
- [x] Fix the 18 placement WARNs — the build has reported 0 WARNs since
  MAX_KNOWN_WARNS went to 0 (test_map_roundtrip), and the 2026-09-15
  cleanup put the Map 10 lake props on the shores. Still open: escalate
  no-floor-support to ERROR (map_validate.validate_placement).
- [ ] Base-map placement validation is blind to terrain (globs never
  expanded; shape-73 eggs match no rule; black-water rule can be silenced by
  paving). Needed: glob-expanded floor-support + water checks for LV items
  on base maps. Related findings from the clean-room attempt (2026-07-29):
  **F2** — base-game dynamic eggs live in `U8SAVE.000 → NONFIXED.DAT`,
  invisible to every FIXED.DAT scan, so `run_event_eggs()` cannot see an LV
  item colliding with one; **F3** — `WalkGrid.flood()` is connectivity, not
  a pathfinder (centre-of-cell limitation).
- [ ] Intermittent post-teleport blackout after cross-map debug teleports
  (all fixed items stop rendering until the teleport is re-run). Engine
  fast-area/camera behaviour; debug-only so far. **Also (2026-09-15): the
  previous map's items can keep drawing around the Avatar after a
  cross-map `MainActor::teleport`** — Map 3's docks scenery and NPCs
  around Map 18's court and Map 9's throat, Map 18's gods around Map 9's
  throat — while a second teleport within the destination map, or a
  different destination spot, shows the map clean. Debug-only (egg
  arrivals are unaffected in every playtest so far); screenshot the same
  spot twice before believing a foreign item.
- [x] Fix Map 17 Cloud City terrain — "white and gold" palette per
  screenshots + design docs. Superseded by the art track: the cloud floor
  is custom shape 862, cut to the 1994 floor's tones from `screen11.gif`
  (§5, verified 2026-09-15). Since 2026-10-17 it is 874, the 1994 cloud
  floor itself, and 862 is retired.
- [x] Map 18 teleport entry: rebuilt and validated. Confirmed in ScummVM
  2026-09-26: trigger 211 walked in from Map 10 landed at (3072, 2024) on
  Map 18 (`docs/playtest-2026-09-26-steps-15-18-unbroken.md`, A9).
- [-] Roof tile frames (brown/terra-cotta from screenshots, not blue-gray
  Tenebrae).
- [-] Shape gallery map (Map 22) — z-levels still wrong for test huts.
- [x] Visual test all 7 maps and iterate on placement. Every LV map was
  shot in ScummVM in the 2026-09-14..19 cleanup (rows above) and Map 10's
  quest spine walked twice (2026-09-18, 09-19).

### 5. Art Placeholder Audit

Pipeline is CLOSED (`tools/png2shape.py`, PNG → injected TYPEFLAG-patched
shape in one command; custom ids start at 859). Injections are dropped on
artifact rebuild unless a build step places them — see
`.claude/rules/shape-ids.md`. Authoritative inventory:
`agents/map-populator/docs/art-placeholder-audit-2026-07-19.md`.
**The art track started 2026-09-15**: `docs/art-track.md` carries the queue
and one written integration contract per item (static prop / interactive /
actor, per the cleanup plan §5), and static props share one table-driven
build step, `lv_art_props.py` (5/7) — a new prop is a row there.

- [x] **Magnetic Obelisk (Map 17) — DONE 2026-09-15; shape 861 RETIRED
  2026-10-17** for screen11's retail composite (art track contract 1; the
  tool, art and record named below were deleted then, git history keeps
  them). Shape **861**, one
  frame, redrawn from the 1994 Cloud City screenshot (`screen11.gif` shows
  the real obelisk: dark slate, green glyph columns, domed cap) through
  `agy` with the crop as the reference — three candidates, **A shipped**
  (Douglas's pick; C, the first to ship, is one filename away;
  `shared/docs/art-poc/obelisk/README.md`). Donor TYPEFLAG 443, footpad
  (4,4,12) = the dais tile it stands on, placed at (4095, 7167, 16). No
  `TYPE_SHAPES` change (nothing compiled reads it; MAGNET's filters are all
  inventory types) and no class at 861, so a click prints nothing.
  Verified in ScummVM 2026-09-15 on a fresh world: draws on the dais,
  sorts in front of an Avatar behind it, blocks a walk at its box edge
  (Avatar stopped at (4080, 7232, 16)), `findShape 861` one item q90
  `shapeinfo f: 3`. `test_art_props.py` (20 checks) pins shape, TYPEFLAG,
  box-on-tile, furniture clearance and the absence of 721 from Map 17.
  Report: `docs/playtest-2026-09-15-obelisk.md`.
- [x] **Cloud tiles/terrain — DONE 2026-09-15; shape 862 RETIRED 2026-10-17**
  for the 1994 cloud floor 874 (the tool, art and record named below were
  deleted then, git history keeps them; art track item 2, contract
  2). Shape **862**, one flat frame in the exact geometry of the flagstone
  platform's frame 0 (63x34, anchor 32,39, the same mask), so it
  tessellates as the kit does — by construction: `tools/art/cloud_tile.py`
  projects a seamless top-down `agy` texture onto the floor plane
  (`(u,v) = (x+2y, x−2y) mod 64`) and cuts it into the 1994 floor's three
  tones (U8PAL 11/2/3, the proportions sampled from `screen11.gif`, whose
  ground IS the cloud floor: flat, no puff — the 2026-07-19 "puffy block"
  was the wrong idiom). Map 17's three islands are the same 78 dais tiles in
  862 (`dais()` grew `shape`/`frames`). TYPEFLAG is 113's whole. Verified:
  `test_art_props.py` (38 checks, incl. mask-equality with the donor and
  the 78 placements), hygiene 54/54, rehashed and reproduced; in-engine
  plates in `docs/playtest-2026-09-15-cloud-tiles.md`. Record:
  `shared/docs/art-poc/cloud/README.md`.
- [x] **Sacred Rock (Map 10) — DONE 2026-09-20** (art track item 3, contract
  3). Shape **863**, one frame: a ninth standing stone for the Sacred
  Circle, kin to the eight shape-38 monoliths on its ring. **The one item
  on the track with no 1994 original**: "Sacred Smallish Unusual-Colored
  Rock" was a joke placeholder in Plot v1.1/v1.2 that became "Sacred
  Circle" before the snapshot, so the look was decided instead (Douglas:
  the ninth stone) and the ring itself is the generator's reference. It
  replaces shape 66 frame 4, a dark striated lump that read as cave rubble
  and stood 6 px taller than its own fence. Donor 66's own TYPEFLAG,
  footpad (4,4,8); position frozen at (20415, 16831) by the single free
  world unit between its box and an Avatar on `MAP10_ROOT_SEED`. No class
  at 863 and no `TYPE_SHAPES` re-point (`TypeSealingBoulder` -> 66 is read
  by `COLPUZZL.UNK:175` under a `getQ() = 299` guard on Map 11). Verified:
  `test_art_props.py` 60 checks, `map_walkability` 137/137, rehashed and
  reproduced; in-engine on a fresh world, `findShape 863` one item q100,
  before/after plates in `shared/docs/art-poc/sacred-rock/README.md`.
  **Lesson kept there:** the first three candidates were rejected for a
  black keyline and a neutral-grey palette that both vanish in the U8PAL
  quantize. Judge a candidate at game scale, never at 1024.
- [x] **Message Scroll (Map 17), DONE 2026-09-21** (art track item 4,
  contract 4). Shape **864**, one frame: the parchment on the Scroll
  Chamber's plinth, where a wooden plank bench (shape 158) stood. No 1994
  art and no recovered usecode names it, so the reference is the game's own
  scroll, shape 159, which is also the TYPEFLAG donor, and that is the
  whole engine-side point: no `SI_FIXED`, so the Avatar can pick the scroll
  up and carry it to Ezrekal as Plot v1.2 beat 14 asks, and `SF_QUALITY`,
  the one family `Item::I_getQuality` answers for, so quality 80 stops
  reading as 0. **The queue's premise was wrong**: no `TYPE_SHAPES`
  re-point was needed (MAGNET's `TypeMagicScroll` filters are `within
  container Avatar`), and making one would have sent `FREE.UNK`'s debug
  grant into the new shape. Position frozen at (3328, 1536, 8):
  `derive_map_pins.route_cite` finds its pin row by grepping
  `test_route_reach.py` for the literal `3328, 1536,`. Verified:
  `test_art_props.py` 83 checks, estate 30/30, rehashed and reproduced,
  pins re-derived; in-engine on a fresh world the scroll rests at z=8, a
  click prints nothing, and the Avatar picked it up (+10 weight):
  `docs/playtest-2026-09-21-message-scroll.md`, record in
  `shared/docs/art-poc/message-scroll/README.md`.
  **Lesson kept there:** every v1 candidate read as a blank sheet, because
  a 1024-to-22 downscale eats any mark thinner than a twentieth of the
  drawing. Pin the one feature that must survive as its own clause.
  **The scroll reads, since later the same day:** class 864 is
  `lv-new/MSGSCRL.UNK` (`TYPEMESSAGESCROLL` pinned 0x0360), `look()`
  barks "message scroll" and `use()` opens the scroll gump with a
  three-page letter signed Odion, whose content is Plot v1.2 beat 13
  (`story-beats.yaml:281`) and whose names come from `EZREKAL.UNK:1697`.
  Verified in-engine, `docs/playtest-2026-09-21-scroll-class.md`. This is
  the first EUSECODE move of the art track, so the detection entry and
  ScummVM followed (`LV_SIZE` 1504582).
- [x] **Elemental pillars and receptacles (Map 11), DONE 2026-09-24**, art
  track item 5, contract 5. Shapes **865** (four frames: Earth and Air from
  the C2 "natural" sheet, Fire and Water from the C3 "wild" one, Douglas's
  mix; 96 px on donor 38, footpad (2,2,10)) and **866** (the receptacle, 40 px
  on donor 443's (3,3,3)). `TypeElementalColumn` re-pointed 721 → 865, so all
  four artifacts moved (detection entry unchanged: same size, same md5-5000).
  `test_art_props.py` 131 checks, `gate_reach()` in `test_route_reach.py`
  (the chamber's anti-climb rule as a climb chain with adjacency), estate
  30/30, second build reproduced, pins re-derived. **Verified in ScummVM
  2026-09-24** (`docs/playtest-2026-09-24-elemental-pillars.md`): `findShape
  865` lists four `(uc: TYPEELEM)` items; a receptacle double-clicked
  empty-handed ran `use()` in class 1144 and barked the repel line; with the
  Air talisman in the pack the Earth receptacle consumed it, barked "The air
  talisman howls with fury!", and `findShape 865` fell to three with q201
  gone. Look bark NOT DEMONSTRATED (harness). **Plinths unified 2026-09-25**
  (`tools/art/pillar_plinth.py`, C3's plinth under all four, U8SHAPES-only
  rehash, `docs/playtest-2026-09-25-pillar-plinths.md`: four grey plinths in
  the plates, `findShape 865` still four). Left standing: the receptacle
  `look()` (decision 2) waits for the next EUSECODE move. Record and plates:
  `shared/docs/art-poc/pillars/README.md`. The contract's history follows. Today the four pillars
  are shape 721, the engine's `CHIMNEY` (two stone stacks and two red brick
  ones with an open flue), and the four receptacles are shape 307, an ornate
  chest with a stag on each door; before plates and the references are in
  `shared/docs/art-poc/pillars/` (regenerate with
  `tools/art/pillar_plates.py`). **The queue's blocker was two claims and
  both dissolved.** No class-at-shape is needed: the receptacles' `use()`
  comes off `npcnum = 120` through the engine patch in
  `Item::callUsecodeEvent`, which is shape-independent, so `TYPERECEPTACLE`
  stays pinned at 1144. What IS needed, and what makes this item cost more
  than 861/862/863, is `TYPE_SHAPES['TypeElementalColumn']` 721 → 865:
  `COLPUZZL.UNK:139` compiles the identifier as a value, so the search that
  destroys a pillar would miss a pillar at a new shape. That moves
  `EUSECODE.FLX`, so the rehash, the detection entry and a ScummVM rebuild
  come with it, and the re-point's blast radius is exactly that one line:
  audited over the 47 files the build compiles, `TypeStatue` and
  `TypeWoodThrone` appear in none of them (PLNTST's use is shadowed by the
  `lv-patched/` copy, MORDEA lives in the uncompiled `U8/` tier) and
  `TypePedestals` appears only in declaration headers, which never consult
  the table.
  **Footpad z above 5 has a price**: `build_map_11.py`'s anti-climb comment
  asserts "nothing in the room tops 40", and the geometry that actually
  protects the 120-tall south wall is distance (the nearest standable is 767
  units from the gate line). Raising a pillar means rewriting that comment
  and asserting the real condition, "no solid within a climb's reach of a
  gate line tops 40", in `test_route_reach.py`, where `gate_coverage(11)`
  checks the wall lines alone. **Class 865 landed 2026-09-24** (Douglas: "yes
  take it"): `lv-new/ELMCOLMN.UNK`, `look()` only, barks the element by frame
  in the map's order; `TYPEELEMENTALCOLUMN` pinned 0x0361. It compiled on its
  own EUSECODE move (1,504,582 to 1,504,996 bytes, md5-5000 unchanged,
  `LV_SIZE` updated), and it is dead until shape 865 is injected, so no
  in-engine bark exists to show yet. The typeclass keeps the design doc's
  name safely: the codegen resolves `type = TypeElementalColumn` through
  `TYPE_SHAPES` before the class table, so `COLPUZZL` still compiles to 721
  until the re-point is made on purpose. One `look()` decision is still open:
  `TypeReceptacle` (the receptacles are silent today, because the npcnum
  override takes every event to class 1144 and that class has only `use()`). **A neighbouring finding**: the four
  talismans, shape 596 frames 0-3, do not read as their elements either
  (Earth an orange flask, Air a gold ring, Fire a purple gem, Water a blue
  gem), while frames 4-7 of the same shape are a matched set of four.
- [x] **Wired obelisk: CLOSED 2026-09-22 with no art and no class** (art
  track item 7, contract 7). `MAGNET.UNK` is `eggclass EggMagnet`: every
  process runs on the egg, and the obelisk appears twice, both times as the
  literal `pop(15615, 19839, 120)` destination. Nothing dispatches an event
  from shape 861, so the row's "a class at 861 if it needs `use()`, else
  nothing" resolves to nothing whether or not MAGNET is wired. Shape 861
  keeps contract 1's silence. The MAGNET wiring itself stays a quest task
  with its own four blockers (EGGMAGNET 281 above), none of them art.
  **Closed on the source, so there is nothing to run in ScummVM**: the
  checkbox flips on a read of `MAGNET.UNK` and an empty EUSECODE entry 863.
  The usual rule wants an in-engine note; there is no engine behaviour to
  observe when the answer is that no class exists.
- [x] **Miniature Avatar (Tiny Tar)**, the one Douglas explicitly asked for
  (2026-07-27). **Done 2026-10-11** (Douglas picked O60, the glow ramp,
  and a scaled stride). Shape 867 is now the Avatar's own sprites at 0.6,
  on its own copy of shape 1's 53-action ANIM table (`docs/art-track.md`
  contract 8). Verified in ScummVM (`docs/playtest-2026-10-11-tiny-avatar.md`):
  the shrink and grow ramps, the 8-direction walk, jump and climb, the
  crack and sanctum, and the protection leap. Regrowing beside a wall used
  to kill; it now shifts 32 units, with a camera glide
  (`-gates.md` R1).
- [x] Water Zombie and Harpie. **Done 2026-10-11** (shapes 872/873,
  contract 9; Douglas picked A/A): the ghoul's 451 frames recoloured, and
  86 frames drawn new in the torax layout, with `u8monsters.ini` rows.
  Verified in `-monsters2.md` and `docs/playtest-2026-10-12-monsters3.md`.
- [x] Shield halves (Zealan artifact). **Done 2026-10-11**: shape 870,
  retail 828 split along a jagged break at build time (contract 10, pick
  B). Verified in `-static-art.md` H1. Since 2026-10-17 the halves are
  878, the 1994 art; 870 is kept only as a copy of 878 so halves in older
  saves still draw (and the backpack does not crash).
- [-] **Freed gods that MOVE — BUILT 2026-09-14, wake art outstanding.**
  Shape 860 is 42 frames: 0-2 encased, 3-5 standing (the rest state), then a
  12-frame run per god at 6/18/30 — six frames of the amber shattering, six of
  the god rising. The engine drives it: TYPEFLAG `animType 5` means "call this
  item's usecode `anim()`", and the engine takes that class from the SHAPE
  NUMBER (`item.cpp:1516`), so shape 860 dispatches into class 860
  (`lv-new/GODANIM.UNK`, pinned). Verified in ScummVM — sealed gods held still
  8 s with `anim()` firing, the ceremony kicked the runs, and the gods landed
  on 3/5/4 with `godsFree=1`, a transition only reachable through a run since
  no `+3` remains in the code. `test_god_animation.py` (32 checks) pins the
  frame arithmetic the four files share. The shatter is procedural and done;
  the SIX WAKE FRAMES per god still want their four in-between poses each
  (all 12 generated by 2026-09-14, `ee238a9` — nine first made through
  gpt-image-2 were replaced through `agy` after six came back robed or with
  the wrong hair; `shared/docs/art-poc/gods/wake/README.md`. The in-engine
  run below predates those six replacements, so the finished set has not
  been watched rise yet). A god with fewer in-betweens gets a steppier wake,
  not a broken one. Full chain verified in ScummVM 2026-09-14: sealed 0/2/1, gate held
  10 s with anim() firing, then 3/5/4 with godsFree=1 — and no `+3` remains
  in the code, so that transition is only reachable through the runs.
  Report: `docs/playtest-2026-09-14-god-animation.md`. Original note follows.
- [x] **Freed gods that MOVE — wanted, and now unblocked.** Superseded by the
  item above (built 2026-09-14; the 42-frame shape 860 is in the build).
  The original wish, kept for its constraints: Seeing the
  Ancient Ones mobile (turning, gesturing, speaking) is part of what the player
  earns at step 17; a static freed frame is the cheap version of it. Shape
  860 frames 6/7/8+, driven by `doAnim` or a frame cycle in `AOSCENE::hatch`,
  which already holds each god on screen for about two seconds and has a
  proven `foreach` over the three items. Frames 0/1/2 are encased and 3/4/5
  free at the SAME pose (decided 2026-09-13) so the shell-break reads as one
  being in two states. The camera blocker is gone as of 2026-09-14 — the
  ceremony pans across all three — so animation now has somewhere to play.
  Constraints to respect: `scrollTo` is a fixed 25 frames and discards its
  speed argument, and the hold lengths were measured against a capture rather
  than computed (`.claude/rules/camera-intrinsics.md`).
- [x] **Gods, freed state — DONE 2026-09-13.** Injected as frames 3/4/5 and
  drawn in the engine: `AOSCENE::hatch` swaps 0/1/2 -> 3/4/5 under the
  FadeToWhite, and `EggTempleEntry` re-applies on sanctum entry (FIXED.DAT
  items are re-read on every map switch, so the swap does not survive one).
  Verified from `run-s16-tinytar.sav`: frames 0/2/1 on arrival, 3/5/4 after
  the ceremony, [0,1,2] after a round trip to map 17, [3,4,5] again after
  crossing the entry egg. The sprites needed `png2shape --key-despill 16` —
  a magenta fringe that only shows over a lit floor, invisible on the preview
  plate. Report: `docs/playtest-2026-09-13-god-placement.md` G1-G3.
  **Signed off as-is 2026-09-13**, including the deliberate mass difference
  against the v2 amber prisms: the freed figures are slighter than the blocks
  they came out of, and that contrast is the point. Felicitar
  standing with arms raised (24x110), Doloras kneeling (53x72 — built at
  height 72, since a kneeling figure must not stand as tall as the other
  two), Timyra turned right with knees bent and hands at her face (43x110).
  Unclothed with doll anatomy except Doloras, who keeps a loincloth: the
  kneeling-plus-bare combination was refused three times by the image route
  and the other provider's version does not match the set's finish.
  Renders, encode recipe (`--key-tolerance 130`) and the full record:
  `shared/docs/art-poc/gods/freed/README.md`.
- [x] **Gods, encased state — DONE 2026-09-13.** Injected as shape 860 frames
  0/1/2 by `agents/map-populator/src/lv_god_statues.py` (step 4 of
  `tools/build_artifacts.sh`) and placed by `build_map_18.py` at the ceremony
  triangle. Verified in ScummVM 2026-09-13: `ObjectManager::findShape 860`
  returns items 5229/5230/5231 at (3072,6656), (2304,7680), (3840,7680),
  frames 0/1/2, `shapeinfo f: 3`; all three photographed drawing in the
  sanctum. Report: `docs/playtest-2026-09-13-god-placement.md`. Encoded sizes
  came out 46x120 / 92x81 / 60x124, slightly under the raw-PNG figures below.
  **Generated** (codex-image / gpt-image-2), not composited: the cover's light
  comes from INSIDE the amber, a solid glowing mass with the god a dark
  silhouette backlit in it, and two procedural passes got that backwards —
  `--mode block` drew crates, `--mode gem` drew a bright band around a dark
  window that read as a 2D outline laid over the sprite. Kept in
  `encased/procedural/` as the record. Felicitar 48x124, Doloras **98x86**
  (the widest asset in the set — check her clearance against props at +/-128
  first), Timyra 61x124. These key on BLACK at tolerance 95, not magenta.
  **Trade-off taken:** generating breaks the pixel-identity between encased
  and freed that compositing guaranteed, so the freeing swaps the figure as
  well as the amber; if that jars in-engine, re-derive the freed frames from
  these silhouettes. `shared/docs/art-poc/gods/encased/README.md`.
- [-] God statues (Ancient Ones) — **the superseded carved-statue set. The box
  art depicts the gods and they are not statues.**
  `shared/data/lv-screenshots/box-smfront.jpg` (the Denis Loubet cover, which
  he authenticated) shows three nude humanoid figures suspended in glowing
  faceted amber blocks — a tall prism (arms folded), a narrow slab (arms
  raised), a cube (kneeling). The nine candidates generated on 2026-09-13 are
  carved temple statuary, the framing shape 443 `statue` invited; they are
  kept as a fallback. The gods get re-generated against the cover, figure
  first and amber added, which inverts the order `resin/` used. Detail crop:
  `shared/docs/art-poc/gods/reference-box-art.png`.
- [-] God statues — the superseded pick, **art chosen 2026-09-13, not placed.**
  Nine candidates generated (3 gods x 3 directions) and each one pushed
  through the real pipeline to a read-back preview. Douglas picked
  **standing** for Felicitar (301) and Doloras (302), **non-human** for
  Timyra (303). Renders, prompts and the open questions (no resin yet,
  footpad unauthored, Timyra C is the widest of all nine at 100 px):
  `shared/docs/art-poc/gods/README.md`. What remains is a build step in the
  shape of `lv_tiny_tar.py` injecting them as shape **860** (859 is taken),
  wired into `tools/build_artifacts.sh`, then the constant swap in
  `build_map_18.py` and an `/artifact-rehash`.
- [x] Passage Plant / Poison plant. **Done 2026-10-11**: shape 871
  (contract 13, pick A). Verified in `-static-art.md` P1.
- [x] Elixir vial (shape 868, 2026-10-09) and the special root. **Done
  2026-10-11**: shape 869 (contract 12, pick C). Verified in
  `-static-art.md` R1.

### 6. Puzzle & Event Scripts

All verified in the engine: COLPUZZL full solve (2026-07-04), CLCLIMB
(2026-07-27), Passage Test with poison (2026-07-28), Sacred Circle ceremony
with cure (2026-07-28), AOSCENE + ENDGAME (2026-07-28), all 14 teleport
pairs bounce-audited (2026-07-31); each replayed on the 2026-10-07 build
(`docs/playtest-2026-10-07-wave2-*.md`). The full 1-18 run is recorded in
the Quest Outline below.

- [x] **Make the Bag of Reagents actually bottomless (refill mechanic).**
  DONE 2026-09-07 — approach 2, a top-up process spawned by
  `EggEndgame::hatch`, waiting 200 ticks and restoring every carried
  `TypeReagent` to 25 (guarded `< 25`, so a larger stack elsewhere is not
  trimmed). Approach 1 was ruled out for a reason worth keeping: replacing
  retail class 027D BAG is dispatch-safe (zero retail callers, the same
  test that clears AVATAR) but not expressible — its `use()` toggles on
  `status & 0100h` and this dialect had no bitwise and (it does since
  2026-10-07), so the two quest
  bags that share shape 637 would lose the ability to close their gump.
  `I_setNpcNum` is absent from the U8 intrinsic table, so the fork's
  npcnum dispatch cannot be reached from usecode either.
  Verified in ScummVM 2026-09-07: stacks drained to 0/3/7 restored within
  45 s, and to 0/2/5 within 50 s *after a save and reload*, so the process
  persists. `hasBag` is written at the hand-over in the same change.
  Banked `~/lv-checkpoints/run-s18-bottomless.sav`. Record:
  `docs/playtest-2026-09-07-bottomless-bag.md`.
  Still open: the six stacks share gump slot (0,0) and overdraw.

  **Background from the 2026-09-05 filing, kept because the constraints
  below still bind anything that touches reagents:**

  **Why it is not just a bigger number.** Plot v1.2 beat 19 and Art List v2.5
  call this the "Bottomless Bag" / "Bag of Endless Reagents", and
  `items.yaml` gives its function as *"eliminates the need to collect
  reagents individually for the rest of the game"*. What `ENDGAME.UNK` ships
  is a **pouch**: six `TypeReagent` (395) stacks of 25, frames
  0/6/8/9/10/14. It cannot simply be a larger stack, because **reagent weight
  scales at ~1 per unit and the Avatar's container capacity is 600** —
  measured in-engine, `FREE::give()`'s 666-per-stack ceiling took him from
  290 to **4296** and he could never pick anything up again. "Endless"
  therefore has to come from *refilling*, or from *weightlessness*, not from
  a big initial quantity.

  **Three approaches, in rough order of preference:**

  1. **Refill on open/use.** Give the bag its own usecode class that tops
     each of the six stacks back to N. **The blocker to solve first:** a U8
     item's usecode class comes from its SHAPE, and this bag is shape 637 —
     the same `TypeBag` RAGNAR and HRODNY pop for the stone bag and the
     stolen-key bag. Attaching a class to 637 would give *those* the same
     behaviour. Either pick a distinct shape for the bottomless bag (art
     placeholder problem — see §5) or dispatch by `npcnum`, which the LV
     engine patch already does for placed items but which the bag does not
     get, because ENDGAME creates it at runtime rather than placing it in
     `FIXED.DAT`. Resolve that before writing any usecode.
  2. **A top-up process** spawned by `ENDGAME::hatch` that periodically
     restores the stacks. No shape/class conflict at all, which is its whole
     appeal, but it is a permanent background process and needs a replay
     guard so a reload does not stack several of them.
  3. **Make the reagents weightless instead.** Achieves the same player-facing
     promise — never think about reagents again — with far less machinery,
     at the cost of a TYPEFLAG change to shape 395 that would also make every
     *other* reagent in the game weightless. Cheapest, bluntest, and probably
     worth pricing before building 1 or 2.

  **Constraints already established, do not rediscover them:**

  - Reagents take `setQuantity()` **alone**: no `quanFrame()` (it skips
    REAGENT_FAMILY because the frame IS the reagent's identity,
    `FREE.UNK:713`) and no `combine()` (`give()` calls it only for
    non-reagents).
  - Frames **0, 6, 8, 9, 10, 14** are the vetted reagent set — the one
    ScummVM's own `Cheat::items` builds. Not a guess.
  - **`TypeBagOReagents` (225) is unusable** as the container: SF_GENERIC,
    and it still carries the old dining-table id, so it holds nothing.
    `TypeBag` (637) is the SF_CONTAINER that works.
  - **Container contents land on top of each other** at gump slot (0,0):
    `moveToContainer` zeroes `_x`/`_y`, no intrinsic exposes gump position to
    usecode, and only the literal (255,255) triggers `ContainerGump`'s
    randomiser. Any refill that re-creates items inherits this, so a fix here
    would improve the shipped pouch too.

  **Open design questions for Douglas:** what triggers the refill (opening
  the bag? casting? a timer?), what the per-stack cap should be, whether it
  should top up only below a threshold, and whether option 3 makes 1 and 2
  unnecessary.

  (`cp33-bag-of-reagents.sav` predates the 2026-09-27 move of the bag to
  Ezrekal; for which bag saves are still safe see the `topUpReagents` item
  under "Found 2026-10-03 and 2026-10-04".)

### 7. Build Pipeline Polish

- [x] Automate the ScummVM detection-entry update end to end. **Done
  2026-10-11** (`098ec1f`): `build_scummvm.sh` computes LV_MD5/LV_SIZE from
  `shared/build/EUSECODE.FLX`, and `tools/integrate.sh` runs the whole
  cascade (`.claude/skills/integrate/SKILL.md`). It has run about 10 times
  since.
- [x] `build_scummvm.sh` auto-repatch. **Done 2026-10-11**: an existing
  `scummvm-lv/` is re-synced to base + patch (`tools/lv_scummvm.py
  engine-sync`); it re-synced `item.cpp` for fork `e48f8716`.
  `test_integration_state.py` checks the tree, the detection entry, the
  install and the harness.
- [ ] CI-style build validation (partially covered by `run_all_tests.sh` +
  `cleanroom_test.sh`; no CI runner exists — M18 residue).
- [ ] **Upstream PR for REA's NE support — held (Douglas, 2026-10-08).** The
  `U8.EXE` decompile above used REA (github.com/morluto/rea) extended to
  16-bit NE executables. The work is on local branch `feat/ghidra-ne` in
  `~/src/rea` (`c71e3cba` fixes the DOS lane's `provider_id`; `29045f13`
  adds NE analysis), and is neither pushed nor opened as a PR. It
  passed `npm run verify:ghidra:ne` on Ghidra 12.1.4. Known gaps: NE
  load-image verification returns `unsupported`, and artifact inventory
  reads only 8 KiB, so it lists `U8.EXE` as `unknown`. Before opening the PR,
  rebase onto upstream and rerun `check:fast` and the NE lane.
- [!] **`scummvm-lv/` was missing 8 of the engine patch's 11 files
  (found 2026-09-05) — and it had been that way all along.** The tree
  carried only `kernel.cpp`, `u8_intrinsics.h` and `item.cpp`; absent were
  **`avatar_mover_process.{cpp,h}` and `ultima8.{cpp,h}` (the use-after-free
  crash fix), `game_map_gump.cpp`, `ask_gump.cpp` (the F18 mouse-release
  dispatch) and `loiter_process.{cpp,h}` (the loiter leash)**. So every
  playtest to date ran an engine that crashed on save-load-then-input, mis-
  dispatched ask-menu clicks, and let NPCs wander unleashed — all three of
  which are documented in `traps.md` as harness pain.

  Cause is the documented one: `build_scummvm.sh` applies the patch **only
  when it clones**, and an existing tree is just recompiled, so the fix never
  reached the binary no matter how many rebuilds ran. Symptom in the log is
  `Seem to be stuck in process loop - killing current process!` followed by
  SIGSEGV.

  Fixed 2026-09-05 by applying the missing files individually
  (`git apply --include=<file>` per file, since the three already-present
  ones conflict) and rebuilding. Verified: load a save, walk — no crash,
  where the same sequence segfaulted minutes earlier. **This also retires the
  "AOSCENE segfault" of the same day: that was this bug, not the ceremony.**

  Still to do: make this impossible to regress — either have
  `build_scummvm.sh` re-apply/verify the patch on every run (see §7) or have
  it fail loudly when the tree diff does not equal the tracked patch. The
  patch itself is now checked against the fork by `test_scummvm_patch_sync.py`
  (`db28de4`); the build tree against the patch is still checked by nothing.

- [x] **The tracked engine patch was stale** (found 2026-08-18).
  `tools/scummvm-patches/0001-lost-vale-engine.patch` carried 3 of the
  fork's 7 changed files — missing the loiter leash and the AskGump
  release-dispatch — so a fresh clone silently built without them, which is
  precisely the C3 hazard the patch exists to prevent. Regenerated from the
  pinned base and verified to apply to a clean fetch. Since `db28de4`
  `test_scummvm_patch_sync.py` byte-compares the patch with the fork diff
  in every estate run (PASS on 2026-10-08 at fork `ed924d30`).
- [x] **`shared/u8-lv-patched/` is synced by nothing** (found 2026-08-18,
  FIXED 2026-09-13). `install_lv.sh` installs into `shared/data/u8-install/`,
  but the playtest harness runs out of `shared/u8-lv-patched/`, maintained by
  hand — its `FIXED.DAT` was three weeks stale when that session started. A
  playtest can silently validate the wrong artifacts, with no visible
  symptom, and it did it again on 2026-09-13: a session looking for the new
  god crystals spent several minutes rendering the previous build's rock
  spires. `tools/playtest-linux/session.sh start` now copies all four
  artifacts from `shared/build/` before launching and prints each one it
  replaced.
- [ ] **`ARTIFACTS.sha256` drifted unnoticed for a month** (2026-08-18).
  Commit 8af416d asserted "detection hash unchanged" for a same-length
  token swap, but the flag NUMBERS differ so the bytecode did; and
  `build_scummvm.sh`'s LV_MD5/LV_SIZE had been stale since 2026-07-28.
  Both fixed. The `--verify` gate is only as good as remembering to run it.

  **It drifted again, and the gate caught it (2026-09-13, RESOLVED).** The
  bottomless-bag work of 2026-09-07 rebuilt and installed `EUSECODE.FLX`
  (`a89c11be…`, 1502938 bytes) without re-recording `ARTIFACTS.sha256`, which
  still pinned `077fb0ef…` — so a fresh clone failed its build verification
  for six days. A full rebuild reproduced the installed bytes exactly, and
  only that one artifact moved, so the record was updated with `--record`;
  a second and third build reproduce it. `scummvm-lv`'s detection entry was
  also carrying a third identity (`b5daa832…`/1503127) and is now regenerated
  to `a9861861…`/1502938, with ScummVM rebuilt on it.

  **`scummvm-lv-console`'s detection entry is NOT auto-updated** — only
  `scummvm-lv` is (`build_eusecode.py`'s detection auto-update). The console tree still reads
  size 1502367, so a fresh add-game against the text-console build will not
  detect the expansion; an existing `scummvm.ini` target is unaffected.

### 8. Known Source-Level Issues (1994 Snapshot)

- [x] `EALOGO.UNK` — truncated block comment (allowlisted, not needed)
- [x] `TJORVI.UNK` — unterminated string (early draft; TYORVI is canonical)
- [x] `FREE.UNK` dev copies + `METHOD.UNK` + `CHANGTAR.UNK` — `::` scope
  operator (and `Reference`/`modulo` in METHOD) were unsupported by the
  parser; all parse since the 2026-10-07 wave 2 (0 recovered errors in the
  compiled tiers; METHOD and CHANGTAR still do not ship).
  Note CHANGTAR compiles from the dev dir but **is not wired**: he is placed
  as npcNum 114 and slot 1138 is unpinned (verified 2026-08-11).
- [ ] Some `UNK files/UNK/` files are dev variants of `LOST VALE/` finals —
  compiled but shouldn't conflict (tier precedence handles it).

---

## Quest Outline (18 Steps)

From recovered plot documents and usecode analysis. This is the target playthrough.

**[x] COMPLETED END TO END 2026-09-07.** All 18 steps run in one continuous
save chain, verified by reading the engine's globals and reloading the final
save: `lbSpoke`, the four `*ColumnDestroyed`, `testFromAtli`, `ragnarMet`,
`ragnarToldStone`, `haveMark` + `avatarPoisoned`, `endOfPlantScene`,
`ezrekalMet`, `sentToTyorvi` + `tyorviDreams`, `givenRoot` + `givenTea`,
`climbedCliffs`, `shieldFixed` + `avatarPoisoned = 0`, `hrodnyMet` +
`spokeTemple`, `templeOpen`, `godsFree`, `endgameStarted` — ending with the
Bag of Reagents in the Avatar's pack holding six reagent stacks of 25.
Banked as `~/lv-checkpoints/run-s18-complete.sav`; per-step checkpoints
`run-s4` through `run-s18` sit beside it. Travel between areas used
`MainActor::teleport`; the quest actions are real. Record:
`docs/playtest-2026-09-07-full-run-1-18.md`.

1. Receive message from Lord British
2. Talk to Mythran — learn of Lost Vale, how to open double doors
3. Find key; enter Elemental Dungeon
4. Collect 4 tokens, open way to Lost Vale
5. Meet the Zealans — must pass Rite of Passage to be recognized
6. Neither clan has Passage Stone; each blames the other
7. Ragnar (Clan Hoskuld) tells of young woman killed at the lake; gives bag
8. Find Passage Stone at the lake (water zombies); take Passage Test; get poisoned
9. Thordis and Atli give Zealan mark; seek Ezrekal
10. Ezrekal tells history; gods can cure poison but need to reach Cloud City
11. Tjorvi has Key to the Clouds; won't give it up (nightmares)
12. Get special root for Ezrekal; she brews nightmare potion; cure Tjorvi; get key
13. Climb Cloud Cliffs to Cloud City; find broken Shield halves, no gods
14. Return to Ezrekal; she calls meeting at Sacred Circle
15. Shield restoration ceremony; shades reveal truth; clans reconciled
16. Gods are at Ancient Temple; Hrodny has Tiny Tar but lost chest key
17. Get potions; enter Temple; place Shield on altar; talk to gods
18. Receive Bag of Reagents. END.

Full 21-step questline: `shared/corpus/plot-documents/story-beats.yaml`

## Design Decisions

(The story-decision registry. Engineering decisions DD-005–DD-011 live in
`PLAN.md` §5 — a different registry that collides with this one at 005; see
`docs/id-legend.md`.)

### DD-001: Tjorvi = Tyorvi (same character)
TJORVI.UNK (14 KB, 1994-06-20) and TYORVI.UNK (71 KB, 1994-09-13) are the same character at different development stages. Use "Tyorvi" as canonical name. TJORVI.UNK won't compile (unterminated string) — not needed.

### DD-002: Ancient Temple = Shrine of the Ancient Ones
Same location. Design docs call it "Shrine of the Wheaties"/"Shrine of the Ancient Ones"; Discord analysis calls it "Ancient Temple." Map 18 has the Temple as outer structure, Shrine as inner sanctum where gods are imprisoned.

### DD-003: Plot v1.2 wins for trust-gaining mechanism
Use the Passage Test (PLNTST) from Plot v1.2, not the two-quest mechanism from the Synopsis. PLNTST.UNK exists in the snapshot; flags `completedTest`, `zealanMark`, `avatarPoisoned` confirm this flow.

### DD-004: Romeo & Juliet subplot → CUT
Cut during Phase 3 dialogue writing. Bag of Reagents → LATE (quest reward at end).

### DD-005: The temple is entered by SHRINKING, not by an explosive or a guardian
**Decided by Douglas, 2026-07-27.** `templeOpen` is read in 23 line-sites across
the corpus (9 in what actually compiles) and **written in zero** — the act of
getting into the Ancient Temple was never implemented by anyone in 1994, so this
is authored content, not a repair. Quest steps 17-18 are unreachable without it.

**The choice was three ways, not two** (an earlier note in this file framed it as
explosive-vs-guardian; that was incomplete):

- **A — explosive.** Plot v1.1 §17, Plot v1.2 §17 and Walk Through XI all say
  *"break through the wall which leads into the shrine. (Some sort of explosive
  and a nice piece of usecode will do very well here.)"* Three documents, but one
  sentence copy-pasted across drafts, phrased as a to-do and hedged with
  *"(This can be done here or earlier in the game.)"*. A usable vehicle does
  exist — shape 579 `lit flask of oil`, the game's only `SI_EXPLODE` shape, with
  a complete `GRENADE` class — but no 1994 code, NPC or item ever points at it.
- **B — guardian slain only by the shield-bearer.** The Synopsis reviewer's
  marginal counter-proposal, suggesting the "multi-elemental agent" be reused.
  That agent turns out to be a recurring *warner* in FREE.UNK whose combat
  branch is commented out; there is no guardian to reuse, no death-flag hook
  anywhere, and the restored shield can only be worn while completely
  unarmoured (ZEALSHLD's `shieldMonitor` strips and hurls away armour).
- **C — Hrodny's Tiny Tar potions. CHOSEN.**

**Why C.** The 1994 team built both approach ramps and no span. The *near* ramp is
complete: THORDIS:1297 and INGYALD:821 both route the player to Hrodny by name,
and HRODNY:1086 answers the literal ask topic `"How can I open the temple?"` with
inherited potions *"for the moment of miracles"* locked in a chest, spawning the
stolen quality-20 key into the world. The *far* ramp is complete: six NPCs have
finished post-`templeOpen` dialogue. Only the middle is missing — and nothing in
the game routes the player toward an explosive or a guardian. The shrink itself is
fully written 1994 code (`POTION.UNK` frame 8 → `makeAvatarTiny`/`makeAvatarBig`),
including a lethal re-grow check, which nobody writes unless squeezing through
tight spaces is the point. Lead designer Sheri Graner Ray described it twice,
years apart: *"to get into the ruined temple, the player had to cast the tiny-tar
spell and creep in through a crack in the wall"* (2005) and *"to get to the room
where the gods were sealed in amber, you had to use the TinyTar spell"* (c.2009).
And it reconciles with A rather than contradicting it — the docs say a wall is the
barrier; Ray says you go through a crack *in that wall*. The explosive was the
placeholder for getting past it.

**The Cloud City claim is a wiki error, not a second use.** The Ultima Codex wiki
puts the shrink puzzle in the cloud city. No source anywhere places a crack or
narrow passage there. The same wiki also states the three gods were imprisoned in
the cloud city — which the code contradicts (MONSKUL's letter has them going
*"now to the Temple"*; EZREKAL: *"They are encased in amber… Quickly, to the
temple return"*). Relocate Ray's sentence using that mistaken geography and you
get the wiki's sentence exactly. **The mechanic has exactly one use site**:
`TypePotion::use()` frame 8 is its only caller in the entire corpus.

**Verified feasible in ScummVM before deciding** (this was the risk that could
have sunk it): `setShape()` clears the cached `ShapeInfo`; `canExistAt()` reads
the footpad from the *current* shape; animations resolve via
`getAnim(getShape(), …)` with no Avatar special-case; and the Avatar's usecode
dispatches on `objId + 1024`, not on shape, so a shape swap cannot break its
scripting. Footpads are ×32, so the Avatar is 64×64 and the tiny form 32×32 — a
gap of 32-63 units admits one and blocks the other.

**Interim art, flagged by Douglas as temporary:** the real 1994 tiny-Avatar art
does not survive (a scan of every shape for a descending-height ramp at frames
60-69 found only frames collapsing to 1px). Shape 708, the child actor, is the
stand-in — the only shape in the game smaller than the Avatar with ≥70 frames and
`SF_CONTAINER`. A bespoke miniature-Avatar sprite is on the art list.

## Key Sources

- Usecode analysis: https://ultimacodex.com/2025/02/a-look-at-the-usecode-for-ultima-8-the-lost-vale/
- Plot documents: https://gallery.ultimacodex.com/the-lost-vale-plot-documents/
- Ultima Codex wiki: https://wiki.ultimacodex.com/wiki/Ultima_VIII:_The_Lost_Vale
- Dino's Guide screenshots: https://gigi.nullneuron.net/ultima/u8/u8tlvscr.php
- Dino's Guide box art: https://gigi.nullneuron.net/ultima/u8/u8tlv.php
- Dino's Guide omissions: https://gigi.nullneuron.net/ultima/u8/omission.php
- Pentagram engine (now in ScummVM): https://github.com/pentagram-u8/pentagram

## Source Data Provenance

- **GOG Gold Edition** (`gog/`): Raw GOG downloads, READ-ONLY. Includes game installer, design documents, cluebook, manual, map.
- **LV Usecode Snapshot** (`shared/data/lv-usecode/`): February 2025 recovery from Sheri Graner Ray's diskette, published by Dominus Dragon on the Ultima Dragons Discord. 67 source files, ~60K lines of original 1994 U8 source code (not bytecode). Separate from the GOG design documents.
- **Base game data** (`shared/data/u8-install/`): Extracted from GOG .pkg. Contains EUSECODE.FLX (516 classes), FIXED.DAT (42 maps), TYPEFLAG.DAT, shape/glob archives.

## Completed Phases (Reference)

### Phase 0: Corpus Builder ✓
Analyzed 67 recovered source files, produced YAML inventories, gap analysis docs. Key outputs: `shared/corpus/plot-documents/` (story beats, characters, locations, items), `shared/corpus/usecode-index/` (symbol tables, cross-references).

### Phase 1: Usecode Disassembler ✓
917-line reference disassembler. 258 intrinsics mapped. Round-trip validation: 516/516 classes. Key discovery: LV snapshot is original source code, not bytecode.

### Phase 2: Map Builder ✓
7 map designs documented. FIXED.DAT format fully understood. `u8_map.py` read/write API. 2,048 shapes + 2,129 globs cataloged. Design docs in `agents/map-builder/docs/`.

### Phase 3: NPC Dialogue ✓
6 missing dialogue segments written as prose docs, then compiled to `.UNK` source files. Character name mapping resolved (8 placeholders). Dialogue docs in `agents/npc-dialogue/docs/`.

### Phase 4a: Usecode Compiler ✓
Full toolchain: lexer → parser → AST → codegen → assembler → FLX packer. 46 of
the 48 sources the build compiles succeed (EALOGO, TJORVI are known-bad 1994
files, allowlisted; counts as of 2026-10-07). 13 new `.UNK` files in
`lv-new/`, plus 16 patched copies in `lv-patched/` (inventory:
`agents/usecode-compiler/docs/lv-patched-inventory.md`).

### Phase 4b: Map Populator ✓
8 map builder scripts (maps 8, 9, 10, 11, 13, 17, 18, 39) → FIXED.DAT with 115,472 items across 49 maps (counted 2026-10-08 on FIXED `6dc98430`, one more than 10-07: the lock TRAP in Hrodny's chest; includes the Map 22 shape gallery, the Map 39 quest-step-1 trigger, and the item-class placements from orphan-triage decision D). All 14 teleport pairs verified on every build.

**npcNum allocation is documented in one place** — `NPCNUM_BANDS` in
`agents/map-populator/src/lv_shapes.py`. Any new npcNum must clear two
checks: class `npcNum+1024` empty in the base FLX, and the byte unused on
every map. Free runs left: 76-83, 88-93, 121-127, 214-224, 237-249.
