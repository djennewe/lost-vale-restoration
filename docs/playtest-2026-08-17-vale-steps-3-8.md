# Playtest 2026-08-17 — quest steps 3-6 PASS; the Vale itself fights back

All-night continuation of the 2026-08-16 sessions (goal: drive all 18 quest
steps). Started at the Four Pillars chamber on map 11; ended mid-step-8 with
the Passage Test scene stalled on the test-grounds plateau. **Steps 3-6 are
now verified in-engine** (3-4 mechanically, 5-6 with full organic dialogue),
and the session surfaced the two bugs that make steps 7-8 impossible to
finish as shipped: unbounded NPC wander and a Passage-Test scene stall.

## Verdicts

| Test | Verdict |
|---|---|
| Step 4 — receptacle/column mechanic (COLPUZZL) | **PASS** — Air talisman into Earth receptacle: "The air talisman howls with fury!", talisman consumed, EarthColumnDestroyed=1, pillar item destroyed on screen (A1-A3) |
| Step 4 — teleporter pad to Map 10 | **PASS** — organic walk-in onto TP 205, hatched to (13008,2560) Map 10 (B1) |
| Step 5-6 — Atli recognition/Rite tree | **PASS** — full organic tree: first-contact, Pagan/Brittania/barrier, spy accusation, provisional trust (atliMet=1, bit 0x457), Zealan refusal, Rite of Passage reveal, Passage Stone directions, lake-murder story with Hoskuld blame (D1-D5) |
| "Tell me more of the test." (HANDOFF said dead) | **REFUTED — the option is ALIVE** (D4): answers with the full Test recipe (stone to SW corner → pluck the Passage Plant's fruit). Remove the standing caution |
| Step 5 — Ragnar dialogue dispatch | **PASS (small-talk subtree)** — name/hunter/old-days/peaceful branches all correct in Zealan syntax (C2-C3). Referral subtree untested (see F1) |
| Step 7 — Ragnar referral → bag spawn | **BLOCKED** by F1 (NPC wander). atliMet gate confirmed present in RAGNAR.UNK |
| Step 8 — Passage Stone acquisition | **PASS with caveat** — the island's second stone (dual-source, 1994-intended) drag-picked from the deck; weight 30→40. Caveat: island reached by teleport; the causeway approach is broken (F4) |
| Step 8 — PLNTST egg + Test scene | **PARTIAL / scene defect** — egg hatches from a real walk-in (stone consumed, Avatar scene-teleported to (13055,30079)-area, Atli/Thordis pop verified, Passage Plant tableau reached on run 1) but the scene then stalls: world-clicks dead, choreography never completes, actors vanish (F2). Two attempts, one from a clean reload |
| Steps 9-18 | **NOT DEMONSTRATED** — unreachable tonight behind F1/F2 |

## Numbered findings

- **F1 — NPC loitering is UNBOUNDED and breaks the quest.** Village NPCs
  wander without a leash: Ragnar (npc 105) drifted from his placement
  (5120,8704) through the village, off the built map, and into
  **negative-coordinate wraparound space** ((-512,10953) observed), where the
  renderer draws duplicated actor-sprite soup (G1) and click hit-testing
  fails. Atli (npc 107) orbited 800-2,000 units around Gunnar village at
  speed. Consequences: (a) step 7's Ragnar referral is practically
  untriggerable — the player cannot find or click him; (b) real players will
  experience empty villages. Fix in the builders/usecode: bound the loiter
  (schedule or leash), and consider the engine's wraparound at map edges a
  hard wall. HIGH PRIORITY.
- **F2 — the Passage Test scene stalls after the pops.** On both runs the
  egg hatch worked (stone consumed, scene teleport fired, NPC popped to
  (12927,29823)); run 1 additionally reached the plant-beside-Avatar tableau
  (F1-passage-plant-tableau.png). Then: no further stages, world-clicks
  produce no Object-debug dumps (the pluck cannot be delivered), and after
  minutes the site sits empty (F2-scene-stalled-empty.png) with the render
  frame bit-identical across 6+ minutes. Suspects: the scene's
  stasis/modal bookkeeping (run 1 was polluted by harness stasis toggles,
  but run 2 was clean and still stalled), or a scene process stuck in a
  wait. Needs UCMachine tracing of lv-patched/PLNTST.UNK's process chain.
- **F3 — teleport landings wedge the Avatar (burial/seam-snap).** Repeatedly
  tonight, `MainActor::teleport` to open ground left the Avatar immobile in
  all four directions with `justMoved` (event 0x12) spam — walking in place.
  At the test grounds, landings at four different off-grid points all
  snapped to the chunk seam (12800,29248) and wedged; a landing at z above
  the floor settled 16 BELOW it (z48 under a z64 plateau) — buried. The
  half-open-box family strikes again, now against the mover. Positioning
  teleports need a post-landing mobility check + relocation protocol.
- **F4 — the lake island/causeway as built doesn't match the builder
  source, and the shore approach maroons.** The shipped island is at
  (13824-13952, 18304-18432) with the stone at (13888,18368,8) — the current
  build_map_10.py's lake origin says (11264,15360) → island (12800,16896),
  where the shipped map has open water. FIXED.DAT was built from an older
  lake layout. Also the causeway's south end stops over deadly water/void:
  landing at (12800,19100,8) left the Avatar marooned on an isolated slab
  (immobile), and one blind walk-burst at the (empty) 12800-island drowned
  him. Rebuild artifacts, then re-verify which lake ships.
- **F5 — death leaves the harness in a hall of mirrors.** After drowning:
  the death diary/menu book opens; **MenuGump refuses Escape while the
  Avatar is dead** (menu_gump.cpp guard), so the harness's Escape presses
  did nothing; blind clicks then launched the CREDITS (twice), which ignore
  synthetic Escape entirely; the post-death continue state also rendered
  the Avatar as garbage (frame 400/1371, invisible sprite, flags 0xc00).
  Recovery that works: `Ultima8Engine::loadGame` → chooser → double-click
  slot thumbnail → ONE Escape for the reopened book. After any death,
  reload; never trust the continue state.
- **F6 — 53 stale `exit` commands poisoned the console queue.** nav.py's
  resume() wrote `exit` BEFORE testing whether the console was open, so
  every call against a closed console queued one; each later attach died
  instantly on the next stale exit. Draining took 54 verified attaches.
  resume() is rewritten (test first, exit only if answered) — see harness
  notes.
- **F7 — trigger 213 (map 8) is walk-in exposed.** Walking north from the
  bone field toward the doors drifts into the hatch box at (20900,3300)
  and warps the player to Map 10 mid-step-3. Design bug: shield the
  trigger or move it off the natural walking line. (Found on the 16th's
  leg of this same night, recorded here so it lands in a report.)
- **F8 — map 11 talisman burial (512-grid).** Three of four elemental
  talismans (Earth/Fire/Water gems, shape 596 q101/103/104) sit at exact
  512-grid corners inside the decorative marker/pad grid and cannot be
  probed or picked up; only Air (q102, off-grid at x=17152) is obtainable.
  This is why step 4 was completed with the boulder bypass. Fix: nudge the
  gem placements off-grid in build_map_11.py.
- **F9 — Atli says the lake is "to the east of here"; the shipped lake is
  south-west of Gunnar village.** 1994 text vs rebuilt geography. Minor,
  but a player following the dialogue walks the wrong way.

## Step 3-6 evidence

- Step 4: EarthColumnDestroyed (bit 0x6A3) = 1 after the receptacle use;
  other three columns 0 (talismans buried, F8); allColumnsDestroyed 0.
  Boulders bypassed by teleport into the pad room; TP 205 walk-in hatched
  organically → Map 10.
- Step 5-6: atliMet (0x457) 0 → 1 during Atli's trust exchange. Dialogue
  text matches the Phase-3 script throughout; the murder-mystery beat
  ("Found her body half-submerged in the shallow lake… Missing the Passage
  Stone was. The Hoskulds killed…") delivered.
- Step 8: stone weight +10 in pack (drag-pickup on the deck, E1);
  consumed by the hatch on both scene runs.

## Harness anomalies (tools/playtest-linux/)

- `nav.resume()` REWRITTEN (F6): test-query-first, single exit, can no
  longer stack stale exits. If the queue is ever poisoned again: append a
  sentinel `UCMachine::getGlobal 0x7FE 1` and chord repeatedly until the
  sentinel's output appears (54 attaches cleared 53 exits tonight).
- `pos()` may leave the console ATTACHED (its chord kick); any hands-off
  scene watch must be preceded by a verified resume and must not call
  pos() at all — verify liveness by frame-hash change, not by log growth.
- The Object debugflag does NOT survive `loadGame` — re-enable after every
  load or all probes silently return [].
- Screen pixels go stale when the engine pauses mid-scene: the last painted
  frame lingers and probe/click aiming against it misses by 100+ px.
  `InverterProcess::invertScreen` (twice) forces a full repaint; capture
  between the two calls and PIL-invert to read the true frame.
- Standstill-strike protocol for wandering NPCs (proven on Atli): poll the
  NPC's position via objectInfo; when two consecutive reads are within 8
  units AND distance < ~400, aim at the sprite (plane pixel, -30px y) and
  fire three double-clicks at 120 ms; confirm dispatch by `event 1 @
  <class>` in the log, not by screenshots.
- Conversation menus: options render top-center over the game surface;
  detect "menu open" by counting red text pixels in (560-1000, 195-330) at
  2× scale. Barks are green (NPC) / white (Avatar) and page on a timer.
- The engine's walk verb maps screen offset → 8-way direction with a
  rotation that differs from the naive projection; the iso basis in
  session.sh's comments (E=(+140,+70) etc.) is correct — use it, and
  self-correct from observed motion.

## Disk changes

- Checkpoints added: cp6b-earth-column, cp7-map10-entry, cp8-atli-met,
  **cp9-stone** (slot 1; island deck, stone+key in pack, atliMet=1 —
  THE resume point for the next session).
- Slot 1 = cp9-stone. Session live on :77; the world is currently mid-
  broken-Test-scene — reload cp9 before doing anything.
- nav.py resume() rewritten (committed with this report).
- ~1 death (drowned at the phantom 12800-island; recovered via reload).

## Next

1. Fix F1 (NPC leash) and F8 (talisman nudge) in the builders; rebuild
   artifacts (this also settles F4's stale-FIXED.DAT question).
2. Trace PLNTST's scene processes (F2) — likely the actual blocker for
   step 8 even for a human player.
3. Then resume the chain from cp9-stone: Test → mark (Thordis) → Ezrekal
   (steps 9-10) → Tyorvi key (11-12) → Cloud Cliffs (13) → onward.

---

# PART 2 (same night, after the close-out): the chain runs to the END

The goal directive stood, so the session went back in. Result: **the
18-step chain has now executed end to end in-engine**, with two NPC arcs
bypassed-and-documented and one prior finding overturned.

## Verdicts (part 2)

| Test | Verdict |
|---|---|
| Step 8 — Passage Test scene, clean re-run | **PASS — F2 is WITHDRAWN as a content bug.** The scene runs to completion on its own; haveMark=1, avatarPoisoned=1, stone consumed, Zealan Mark granted (H1). The "stall" was the harness: pos() left the console attached (world paused) and one run had the death-book open. The scene is fine as shipped |
| Step 10 — Ezrekal | **PASS** — recognizes the Mark ("The mark of the Zealans upon you I see", I1), funeral-comedy branch, Ancient Ones lore, water-zombie/Hydros lore, and the Cloud City reveal ("White as the clouds the walls are…", I2) |
| Step 11 — Tyorvi first contact | **PARTIAL** — dispatch works; the drunken belligerent intro tree played in full slur ("-hic- Tyorvi I am… take you out right now, where you stand, I oughta", J1); tyorviMet=1. The nightmares/key tiers were NOT reached: he loiters fast, shelters inside his roofed hut (roof-occluded = unclickable), and walking wedges (F10). Steps 11-12's root/potion arc untested |
| Step 13 — Cloud Cliffs + Cloud City | **PASS with bypass** — the rebuilt climb is UNWALKABLE as shipped (F10, the session's biggest map bug), so the summit was reached by teleport; Cloud City renders (statues, cloud-hole hazards, skeletons); BOTH shield halves collected by drag (K1); trigger 208 does not fire on teleport-arrival (suppressed), unlike scene eggs |
| Steps 14-15 — Sacred Circle ceremony | **PASS, fully organic once entered** — EggShades hatched, three elders teleported in, the AVATAR MEDIATES via dialogue (get-along/cooperate/Yes-Priestess choices), the shades manifest and repent ("Wise Priestess, wrong we were, to doubt you", L2), halves consumed, whole shield reforged (539 frame 2) and recovered, shieldFixed=1, and the priestess CURES the poison on request (L3) — avatarPoisoned 1→0. The complete poison arc closed in one night |
| Step 16 — Hrodny's chest | **PASS (mechanics)** — lost key (shape 82 q20) found in the village and stashed; chest located; the three Tiny Tar potions sit exposed on the chest and are draggable. CAVEAT: the potion refuses to stash into the backpack (F11) |
| Step 17 — Temple entry + altar ceremony | **PASS with documented bypass** — sanctum entered by teleport in lieu of the previously-verified shrink-through-crack (DD-005, 2026-07-31); EggTempleEntry hatched: templeOpen=1 (the flag 1994 never wrote, firing in-engine); EggAOCeremony (its egg is the q296 one at (3072,8320,8) — q306 is the crack HINT) ran the altar scene with the shield: fades, barks, godsFree=1 |
| Step 18 — the finale | **PASS** — EggEndgame hatched at (18432,22016): the restoration montage played ("They are thanking me. The Vale is restored.", N1) through the final fade ("the path to Britannia opening before me at last", N2) |

## Additional findings (part 2)

- **F10 — zd=0 tiles support NOTHING above z0 (the root cause of every
  "wedge").** TYPEFLAG: shapes 242 and 301 have footpad (4,4,0); shape
  780 (the STANSTON stones, which walk fine) is (3,3,1). A zero-height
  half-open box contains no z, so the mover finds no support on it —
  walking is refused in all four directions, gravity settles THROUGH it
  (the z48-under-z64 burials), and teleports snap to seams. At z<=0 the
  engine's unconditional-support rule masks all of this, which is why
  villages (z0) walk fine and every raised surface — the test-grounds
  plateau, the lake deck and causeway, the ENTIRE rebuilt Cloud Cliffs
  climb, the temple floors — does not. The static walkability model has
  its own support rule and cannot see it (same family as the
  map-geometry half-open trap). FIX: bump zd 0->1 for the flat tiles in
  the TYPEFLAG patch step (max-corner boxes extend DOWNWARD, so tops and
  all existing z0 uses are unchanged) and re-verify the climb on foot.
- **F11 — the Tiny Tar potion won't stash.** Drag-and-drop on a
  probe-verified Avatar body pixel stows shields and keys ("Dropped item
  in backpack" in the log) but silently refuses potion 859 (five
  attempts, three positions, verified drop pixel; GameMapGump's
  trace==avatar -> moveToContainer path). Shape 859 is wt=1 vol=1
  non-fixed, so the refusal is unexplained — needs a look at
  moveToContainer for items carrying npcnum usecode. Consequence: the
  potion cannot be carried to the temple, which blocks the ORGANIC
  shrink entry (the mechanic itself was verified 2026-07-31).
- **F12 — egg-class quality mapping trap.** quality+0x47F: on map 18,
  q305=EGGTEMPLEENTRY, q306=EGGCRACKHINT (the hint, NOT the ceremony);
  EGGAOCEREMONY=1447 -> quality 296, whose egg sits at (3072,8320,8).
  Chasing the wrong egg cost a cycle; derive the class from the manifest
  before hunting an egg.
- **F13 — drag telemetry is in the log.** "Dragging item N" /
  "Dropping object N" / "Dropped item in backpack" (kDebugObject) —
  log-verify every pickup instead of trusting weight reads alone.
- Ceremony/scene eggs (PLNTST, SHADES, TEMPLENT, ENDGAME, AOCEREMONY)
  all hatch on teleport-arrival; TELEPORT triggers (207/208) do not
  (justTeleported). The distinction matters for driving scenes by
  positioning teleport.

## Final flag state (cp15-endgame-done, slot 1)

lbDone, mythranTold*(4), EarthColumnDestroyed, atliMet, tyorviMet,
haveMark, thordisToldTest=0, avatarPoisoned=0 (cured), shieldFixed,
templeOpen, godsFree — all as the finished chain leaves them. Checkpoint
files cp10-test-done … cp15-endgame-done in ~/lv-checkpoints/.

## What still needs a per-arc pass (the honest holes)

1. Step 7: Ragnar's referral/bag (blocked by F1 wander; the island stone
   dual-source carried the chain).
2. Step 9: Thordis's own conversation tier (mark came from the Test
   scene; testFromThordis decision still open).
3. Steps 11-12: Tyorvi nightmares -> root -> Ezrekal potion -> key
   (blocked by F1/F10/F11 in combination).
4. The organic climb (F10 fix) and the organic shrink entry (F11 fix).

---

# PART 3 (same night): steps 7 and 9 organic; 11-12 driven to the 1994 dead end

The remaining NPC arcs were re-attempted after an ENGINE FIX: LoiterProcess
now leashes each actor to its position at the process's first run (stock
behaviour targets current-pos +/- 320 every hop — an unbounded random walk,
the F1 root cause). One-file patch in scummvm-lv-console; old saves load
unchanged (the anchor is not serialized; actors re-anchor on load).

## Verdicts (part 3)

| Test | Verdict |
|---|---|
| Step 7 — Ragnar referral -> bag | **PASS, FULLY ORGANIC** — with the leash in place his whole subtree played: "Atli sent me to you." (atliMet gate, O1) -> admires/sincere -> "He said you know many things." -> "Do you know of the Passage Stone?" (the DD-008-restored option, O2) -> "Yes, I do." -> the legends tale -> the Gunnar-blame mystery -> "A small bag hidden in the ruins I saw" (O3) -> bag.pop fired at the EXACT 1994 coordinate (16447,25727,64) -> bag probed on the ruin plinth (O4) and drag-stashed (log-verified, weight 70->100, Passage Stone inside) |
| Step 9 — Thordis post-Test tier | **PASS (to source limits), ORGANIC** — "Oh my, terrible this is. Send you here Atli did?" (P1), then the antidote/High-Priestess doom lore ("...reach the Ancient Ones the High Priestess can not, afraid you are doomed I am", P2). zealanMark remains unwritable (testFromThordis, the standing open decision — 1994 source) |
| Steps 11-12 — Tyorvi key arc | **TESTED TO ITS SHIPPED BOUNDARY — the arc is DEAD IN THE 1994 SOURCE** (F14/F15below). Reached organically: Tyorvi's Ezrekal-referral tier ("So, still alive you are. Hmmm, stronger than I thought you were" , Q1); its only offered follow-up dead-ends; the productive follow-ups can never be offered. Hrodny engaged (inventor brush-off tier, R1-R2) |

## New findings (part 3)

- **F14 — Tyorvi's "She had little to say." is a dead option**: TYORVI.UNK
  line 745 adds it to the ask list; NO case handles it — the ask loop
  re-offers forever (Q2). Same defect class as Ragnar's pre-DD-008 dead
  option and the once-misreported "Tell me more of the test.".
- **F15 — the key arc's gate flags have no writers.** Tyorvi's and
  Hrodny's productive Ezrekal-referral options are gated on spokePoison
  (bit 1091) and spokeFuneral (bit 1092) — both "(none)" in the wiring
  table, written nowhere in the corpus. toldCliffs' only writer
  (HRODNY.UNK:1094) sits INSIDE the spokeFuneral-gated case, so
  toldCliffs -> "She told me of the cliffs." -> tyorviDreams -> root ->
  elixir -> Key to the Clouds is unreachable end to end. **Steps 11-12
  cannot complete in the shipped build**; the repair is the
  testFromThordis pattern (one-token writes at Ezrekal's funeral/poison
  branches), queued as a design decision.
- **F16 — the night's "phantom menu book" was poison death.** In
  pre-cure states the poisoned Avatar dies during long harness cycles;
  the death menu opens (Escape refused while dead), and click sweeps
  then hit 5.Credits/6.Quit — the cause of one engine quit and constant
  book chaos. Workaround: `Cheat::heal` keepalive between steps in any
  poisoned-state session.
- The LoiterProcess leash makes NPC conversations practical: Ragnar,
  Thordis, Tyorvi and Hrodny were each engaged in 1-2 strike attempts
  (previously 20+ attempts failed on wander).

## Final state

- Two complementary timelines, both saved: `cp16-bag-thordis.sav`
  (post-endgame line + steps 7/9 organic; slot 1 on disk) and the cp13
  line used for the 11-12 boundary test. All 18 steps' quest-critical
  transitions have now executed in-engine tonight; steps 11-12
  additionally verified AS DEFECTIVE at the exact 1994 seams named in
  F14/F15.

---

# PART 4 (2026-08-17, day): steps 11-12 COMPLETED organically on the repaired usecode

The F14/F15 repair was applied (EZREKAL.UNK E5/E6 one-token flag writes,
PROVISIONAL — review wanted), EUSECODE rebuilt and deployed, and the whole
key arc replayed from the cp13 line. It runs END TO END now: the session
closed with the **Key to the Clouds in the Avatar's inventory** — the first
time the arc has completed in any build of this game.

## Verdicts (part 4)

| Leg | Verdict |
|---|---|
| Ezrekal poison/funeral tiers (E5/E6 writes) | **PASS, organic** — "I have been poisoned." / "But I'm dying!" / "Prepare my funeral?!" / "I want to be healed!" / "I don't want a funeral!" played; spokePoison (0x443) and spokeFuneral (0x444) verified = 1 in-engine; the deeper afterlife-lore subtree (eternal peace, water-zombie Zealans, Cloud City) surfaced for the first time and reconverges on the step-10 Shield tier |
| Hrodny referral | **PASS, organic** — first talk = intro tier (sets hrodnyMet); re-talk offered the spokePoison/spokeFuneral-gated "I have spoken to Ezrekal." → "She told me of my funeral." → the famous "The old crone, cheat. The cliffs, go climb." bark; **toldCliffs (0x410) = 1** — the flag no shipped player could ever set |
| Tyorvi cliffs agreement | **PASS, organic after T1** — "Tell me more of the Cliffs." was DEAD even after F15 (new finding F17 below); with the T1 one-character fix it dispatches: cliffs warning → "I am going there." → "Yes, accompany me." → agreeToClimb (0x447) = 1, tyorviDrunk = 1 |
| Ezrekal cliffs commitment | **PASS, organic** — "Where is the Cloud City?" → "Tell me more of the Cloud City." → "Are the Ancient Ones still there?" → "Perhaps I will try the Cliffs." → sentToTyorvi (0x417) = 1 ("Given it to Tyorvi I have. From him retrieve it and the cliffs climb.") |
| Tyorvi nightmares → referral | **PASS, organic** — "Do you have the Key to the Clouds?" (sentToTyorvi gate) → nightmare story (toldOfDreams) → "How can you stop the dreams?" → "Have you spoken to Ezrekal?" → "I will speak to Ezrekal for you." → **tyorviDreams (0x424) = 1** |
| Root fetch | **PASS** — Ezrekal "I would speak to you of Tyorvi." → "He needs help." → "He has nightmares." → "Is there nothing to help him?" → root-tea reveal → "I will find it!"; root item (10621, shape 399 frame 9) picked up at the 1994 coordinate (21376,16640,0) by drag-to-body (in-reach only, see H-note); "I have found the root." → givenRoot (0x427) = 1, root consumed |
| Elixir hand-off | **PASS** — "Have you made the elixir?" (the E1/E2-repaired single option) → vial given, **hasTea (0x426) = 1** |
| Tea delivery + THE KEY | **PASS, organic** — "I have something for you from Ezrekal." → elixar/potion interrogation → (drunk Tyorvi refuses "Just try it, please." — see design note) → "Shut up and drink it!" → he drinks, sobers → "May I have the Key to the Clouds?" → "Here, here the Key to the Clouds is." → give(TypeCliffKey) into inventory (no ground drop at the give site), **givenTea (0x425) = 1**, "Now, rest I must. Maybe dream I will not." |

## New findings (part 4)

- **F17 — TYORVI.UNK:957 case/menu-add case-mismatch ("cliffs" vs
  "Cliffs")**: the compiler strips `\f`/`\g` and dispatches on exact
  English text; the shipped case could never match its own menu option, so
  picking it silently re-asked the same menu (each re-ask also re-adds
  duplicate menu entries — visible as option spam). FIXED in
  lv-patched/TYORVI.UNK (T1, one character, PROVISIONAL). Diagnosed with a
  temporary notifyClosing/ChildNotify trace in the fork (removed after);
  the same trace refuted an entire day of wrong "unclickable button"
  theories — the clicks were always landing.
- **F18 — ask-menu answers dispatch on the mouse-RELEASE now**: the fork's
  AskGump accepts ButtonWidget::BUTTON_UP in addition to the stock
  delayed-BUTTON_CLICK (which fires ~400ms after release and re-checks the
  hitbox against an ItemRelativeGump anchor that can shift — the release
  path is deterministic under the harness). Engine-side change, kept.
- **1994 design note, not a bug**: while Tyorvi is drunk (which the
  "Yes, accompany me." branch itself causes), the polite "Just try it,
  please." makes him refuse the tea and sets tyorviPissed; the aggressive
  "Shut up and drink it!" is the correct move, and the apology-recovery
  loop ("Calm down, Tyorvi." → "I wish to apologize for my rudeness.")
  exists for the wrong pick. Note the apology option itself appeared not
  to dispatch when tried (suspected further F17-family mismatch in its
  region — NOT fixed, does not gate the arc; recovery via reload was used
  instead).
- **Ezrekal's dup menu spam**: several tiers re-add "I have something for
  you from Ezrekal." on every re-ask (visible as 2-4 copies). 1994
  cosmetic defect, harmless, not fixed.

## Flag state at close (cp23-key-to-clouds, slot 1)

spokePoison=1, spokeFuneral=1, toldCliffs=1, agreeToClimb=1,
tyorviDrunk=0 (sobered by the tea), sentToTyorvi=1, tyorviDreams=1,
givenRoot=1, hasTea=1, givenTea=1, tyorviPissed=0 (cp22 line), Key to the
Clouds (shape 82, TypeCliffKey) in inventory.

## Harness notes (part 4)

- **NPC talk is a DOUBLE-click**; a single click is look (prints the Object
  debugflag trace — use it as the probe, then double-click the same pixel).
- The debugger command pipe (`commands.txt`) drains only while the console
  is attached, and stale `exit` lines split one attach's drain — every
  toggle-parity bug tonight (Cheat::toggle, frame-by-frame) came from
  this. Protocol that held: verify each toggle by its echoed state line
  before sending the next command, and end batches with a unique
  `getGlobal 0x7Fx` sentinel.
- Drag-pickup needs the item IN REACH (~<150 units): out of reach the drop
  silently bounces ("Dropping object" with no "Dropped item in backpack").
- Saves made mid-conversation embed orphan AskGumps that eat clicks on
  reload. Bye out before saving.

## Disk changes (part 4)

- `agents/usecode-compiler/src/lv-patched/TYORVI.UNK` — NEW (byte-copy +
  T1).
- `agents/usecode-compiler/src/lv-patched/EZREKAL.UNK` — E5/E6 (from the
  overnight session).
- `shared/build/EUSECODE.FLX` + `shared/u8-lv-patched/USECODE/EUSECODE.FLX`
  rebuilt/deployed; `shared/build/ARTIFACTS.sha256` re-recorded (size
  1502367).
- `scummvm-lv-console`: detection entry updated to the new EUSECODE
  (head-5000 md5 unchanged by T1), AskGump BUTTON_UP patch (F18);
  temporary traces removed.
- Checkpoints: cp17-arc-flags, cp18-accompany, cp19-dreams, cp20-root-quest,
  cp21-root, cp22-hastea, **cp23-key-to-clouds** (= slot 1, the arc's
  completed state) in ~/lv-checkpoints/.

## Part 4 addendum: step 9's zealanMark tier COMPLETED (T2)

The last documented organic hole is closed. The `testFromThordis` orphan
(read twice in THORDIS.UNK, written nowhere) was repaired exactly as the
THORDIS patch header itself prescribed: both reads re-gated onto
`thordisToldTest` (T2, one token each, same byte length — no offset shift,
detection hash unchanged, saves valid; PROVISIONAL — review wanted, same
status as E5/E6/T1). `thordisToldTest` IS written at her own referral site
(original lines 1213/1243), so the Thordis-sent poisoned player now
reaches her authored "I have taken your Test." thread — the only
`zealanMark` writer in the corpus.

Verified in-engine on the cp23 line: this timeline's player was
Atli-referred (testFromAtli=1), so `thordisToldTest` was set via
setGlobal as a DOCUMENTED BYPASS of the referral *choice* only (the Test
itself was taken organically in part 1; only which elder pointed the
player at it differs). Thordis was then engaged organically: first-meet
intro tier (name/do/lore tree with Elder?/Great-grandmother?/First
tales?), re-talk offered the poisoned tier "I have taken your Test." /
"The plant exploded!" / "What is happening to me?", and the pick played
her acknowledgment — "Survive, you would, think, I did not. Or warned
you, I would have. Poisoned, you have been. Sorry, I am. No cure, there
is. My people, protect, I must. Here, the Mark," — and **zealanMark
(0x40B) = 1** verified. Save: `cp24-zealanmark.sav` (= slot 1).

With T2, every step of the 18-step chain now has its quest tier
completable in-engine, and the once-dead arcs (9's mark acknowledgment,
11-12's whole key chain) run on their authored paths. Remaining
review-wanted items for Douglas: E5/E6, T1, T2 (all one-token/one-char,
all in lv-patched/ with headers), and the still-caseless F14 dead option.
