# PLAN.md - Road to a Complete Lost Vale

> Completion roadmap from the current state (2026-07-02) to a releasable fan restoration.
> Companion to TODO.md: TODO.md tracks fine-grained tasks; this document defines the
> milestones, exit tests, open decisions, and risks that order that work.
>
> **Definition of done (applies to every item below):** a feature is done when it has
> been exercised in ScummVM and the result recorded (date, debug teleport used, what was
> observed). "Compiles", "placed in FIXED.DAT", or "validator passes" are progress
> states, not done. This rule exists because the project's two worst defects to date
> (five orphaned quest scripts; a Mythran patch that null-derefs on both paths) were
> invisible to every static check and would have been caught by one in-game click.

---

## 0. Verified state snapshot (2026-07-02)

**Working, verified in-game:**
- Compiler toolchain: 43/45 files compile; round-trip validation 516/516 base classes.
  (Corrected 2026-08-11: this said "45/47", which conflated the success count
  with the total. Verified against a live `--full` build — 45 compiled, 43
  succeeded, 2 known-defective. M21 had already flagged 45/47 as a wrong stat
  in 2026-07-25; it survived here and in README.md until now.)
- All 7 recovered NPC dialogues reachable via the `npcnum + 1024` ScummVM dispatch patch.
- Map 8 sealed double doors open with the restored key/chest (verified 2026-07-02).
- Map 10 villages Phase 1 (wood-plank huts, wells, work-stations) verified 2026-07-01.
- Build gating: placement validator aborts bad FIXED.DAT builds; shape identity single-sourced.

**Broken (found in 2026-07-02 review, fixes are Milestone 0):**
- `patch_mythran.py` omits the `this` push before both calls: Mythran conversation dies
  on both paths. The defective handler is in the current working-tree EUSECODE.FLX.
- Once `lbDone` is set, the wrapper locks the player out of stock Mythran forever.
- Stealth mode cannot carry the expansion (new classes skipped; oversized Mythran
  corrupts the FLX via the packer's reclaim-before-place bug).
- The build cannot fail: compile errors, skipped patches, and packer warnings all
  exit 0.

**Orphaned (compiled and shipped, but nothing in the game invokes them):**
- SIGRID, AOSCENE, CLCLIMB, COLPUZZL, ENDGAME. Class ids 0x0260+ are assigned
  sequentially; no map item, egg, npcnum, or patched class points at them.
- Reachability of other recovered non-dialogue classes (LORDBRIT, PLNTST, MAGNET,
  POTION, CANTRK, SHADES, FREE) has never been audited. Step 1 of the quest depends
  on LORDBRIT and its trigger is currently unknown.

**Engine dispatch facts (verified in scummvm-lv `world/item.cpp`, `callUsecodeEvent`):**
- Default: `class_id = shape`.
- Permanent NPCs (`objId < 256`, EXT_PERMANENT_NPC): `class_id = objId + 1024`.
- UnkEgg-family items: `class_id = quality + 0x47F`.
- LV patch: any FIXED.DAT item with `npcNum != 0` dispatches `npcNum + 1024` when that
  class has data.

---

## 1. Milestone 0 - Repair and guardrails

> Status 2026-07-03 (2nd update): M0.1/M0.2 DONE and verified in-game
> (note in TODO.md section 3). M0.3/M0.4/M0.5/M0.7 DONE via parallel
> worktree agents, acceptance-tested: stealth is an error stub; the build
> exits nonzero on compile failures / Mythran-patch skips / missing
> quest-critical classes (list pinned in build_eusecode.py pending the
> manifest) and never writes a failing FLX; codegen warns on every silent
> fallback with per-file counts; the Mythran patch guards use-offset and a
> pinned preamble hash (test_patch_mythran.py 4/4). Rebuilt FLX is
> byte-identical to the verified artifact. M0.6 design complete with
> decisive experiments (agents/usecode-compiler/docs/manifest-design.md):
> FLAGS.UNK order refuted as retail bit assignment; LV flags currently
> collide with retail's dense sub-600 bit range; adopted design rebases LV
> flags to a reserved window at bit 1024+ (one savegame reset). M0.6
> implementation and optional M0.8 remain.
>
> Status 2026-07-03 (3rd update): **Milestone 0 COMPLETE.** M0.6 landed:
> shared/build/lv_manifest.json pins 645 flags (583 retail_shared) and 22
> classes; LV flags rebased to the bit-1024 window (lbDone 0x6A6); one
> savegame reset; test_manifest.py 5/5 (order independence proven
> byte-identical). M0.8 landed: wrapper built on BytecodeEmitter,
> byte-identity regression-pinned. M0.6 also surfaced and fixed three
> pre-existing defects: NEW_CLASS_START=0x0260 silently overwrote ~28 live
> base classes every build (new classes now start at 1431); dev-dir dedup
> compiled 4 files twice under two ids; _find_safe_insertion() misparsed
> string operands during trampoline relay insertion. Exit test PASSED
> 2026-07-03 (tools/cleanroom_test.sh: fresh clone + data symlink, two
> byte-identical builds, break-one-file exits nonzero, stealth stub exits
> nonzero, all suites green; toolchain paths now repo-relative). Mythran
> re-verified in-game at the manifest bits (ask-width fix confirmed).

Goal: fix what the review found and make this class of failure structurally impossible.
Everything else in the plan builds on a pipeline that fails loudly.

| # | Item | Detail | Acceptance |
|---|------|--------|------------|
| M0.1 | Fix the `this` pointer bug | In `patch_mythran.py build_new_use()`, emit `push dword [BP+06]` (bytes `40 06`) immediately before each `0x11` call. The wrapper's own `[BP+06]` holds the valid item pointer pushed by the engine. | Talk to Mythran in-game on the stock path (fresh game) and the LV path (after `lbDone`); both conversations run. |
| M0.2 | Ungate stock Mythran | Implement DD-005 (see section 5). Recommended: route on `lbDone AND NOT mythranIntroDone`; MYTHRDLG sets `mythranIntroDone` at Farewell, so the LV intro plays once and Mythran then returns to his full stock conversation. The LV ask topics that must persist ("the Lost Vale", key hint) get grafted as follow-up visits per the design doc. | After finishing the LV intro, Mythran offers his normal base-game topics again; key hint remains accessible on a repeat visit. |
| M0.3 | Retire stealth mode | Implement DD-006. Recommended: `--stealth` prints a clear "retired, use --full with the patched ScummVM" error and exits nonzero. Remove Step 6b's exposure to it. Closes the packer corruption finding without fixing dead code. | `--stealth` cannot produce a FLX; README/CLAUDE.md updated. |
| M0.4 | Build fails loudly | `build_eusecode.py` exits nonzero when: any lv-new or LOST VALE file fails to compile, the Mythran patch skips, or a quest-critical class (list in the manifest, M0.6) is missing. `build_all_maps.py` already gates; mirror the pattern. | A deliberately broken MYTHRDLG.UNK makes the build exit nonzero with a one-line reason at the bottom of output. |
| M0.5 | Kill silent codegen fallbacks | Unknown identifier currently compiles to `push 0` with no diagnostic (`u8c_codegen.py` ~1218). Emit a warning with file/line, count warnings in the driver report, and add `globalflag lbDone;` to MYTHRDLG.UNK so single-file compiles are order-independent. | Compiling a file that references an undeclared flag prints a warning naming it; build report shows warning counts per file. |
| M0.6 | Pin ids in a manifest | New checked-in `shared/build/lv_manifest.json` (extending the existing map manifest pattern): every LV class name to class id, every global flag name to bit offset. Allocators consult it first and append new entries; the build fails if an allocation would move an existing pin. This freezes savegame-visible numbering forever. | Reordering source compilation produces a byte-identical EUSECODE.FLX; unpinned new flag gets appended and reported. |
| M0.7 | Harden the Mythran patch | Add the two residual guards: fail if `lv_use_off == 0`, and verify the copied preamble bytes against a pinned hash so a different base EUSECODE.FLX fails at build time instead of executing garbage in-game. | Corrupting one preamble byte in a test copy of the base FLX makes the build fail with a clear message. |
| M0.8 | (Optional) Rebuild `build_new_use` on the codegen Emitter | `u8c_codegen.py` already has `emit_init/emit_call/emit_push_global/emit_jne_label/emit_ret/emit_end` plus fixup resolution. Hand-rolled byte literals are how M0.1's bug happened. Low urgency once M0.1 lands with a test. | Patch output byte-identical to the hand-rolled version (except the fixed push). |

**Exit test:** clean-room rebuild (fresh clone plus game data) exits 0, produces
identical artifacts twice in a row, and a scripted "break one file" run exits nonzero.
Mythran verified in-game both sides of `lbDone`.

Estimated effort: 1-2 working sessions. M0.1 alone unblocks committing the currently
uncommitted work.

---

## 2. Milestone 1 - Playable spine

Goal: all 18 quest steps completable in one continuous playthrough, placeholder
visuals allowed everywhere.

### 2.1 Reachability audit (do this first)

Extend the flag-graph tool (2.3) or write a one-off: for each of the 34 new LV classes
plus the 11 modified base classes, determine what invokes it (shape placement, egg
quality, npcnum, patched call, or nothing). Output a wiring table checked into
`shared/docs/wiring.md`. The five known orphans are the floor, not the ceiling:
LORDBRIT (quest step 1!), PLNTST (step 8), SHADES (step 15), FREE (step 17), MAGNET,
POTION, CANTRK have never been audited.

### 2.2 Wire every script

Mechanism decision is DD-007. The two engine-verified candidates:

- **UnkEgg quality dispatch:** place an UnkEgg-family item with quality Q; the engine
  calls class `Q + 0x47F`. Requires pinning script class ids at 0x0480+ in the
  manifest and confirming which shapes carry SF_UNKEGG in TYPEFLAG.DAT
  (`parse_typeflag.py` exists for exactly this).
- **npcnum dispatch (our ScummVM patch):** any placed item with `npcNum = N` reaches
  class `N + 1024`. Already proven by the 7 dialogue NPCs.

Recommended: npcnum dispatch for SIGRID (she is an NPC; mirror the existing seven:
`LV_NPC_SHAPES` entry, npcnum slot, Map 13 placement) and a **spike test before
committing** for the four event eggs: place one UnkEgg on the Map 22 shape gallery,
pin one class to its quality, confirm the hatch event fires on approach in ScummVM.
Whichever mechanism wins, the map builders place the trigger and `wiring.md` records
script, class id, trigger item, map, coordinates, and verification date.

Initial wiring targets:

| Script | Quest step | Map | Trigger concept |
|--------|-----------|-----|-----------------|
| LORDBRIT | 1 | TBD by audit | Lord British's message delivery (mechanism unknown; audit first) |
| MYTHRDLG | 2 | Mythran's house | Patched class 0x421 (done in M0) |
| COLPUZZL | 3-4 | 11 | Column puzzle trigger in the elemental dungeon |
| PLNTST | 8 | 10 | Passage Test plant at the lake |
| SIGRID | 11-12 | 13 | Hunter NPC, npcnum dispatch |
| CLCLIMB | 13 | 13 | Cliff climbing sequence trigger |
| AOSCENE | 15, 17 | 10 / 18 | Sacred Circle ceremony, shrine scene |
| ENDGAME | 18 | 18 | Victory sequence after the gods are freed |

### 2.3 Flag-graph tool

New tool in `agents/usecode-disasm/src/` (read-only consumer of the disassembler, per
the do-not-modify rule): disassemble all classes in a built EUSECODE.FLX, extract every
`push global` / `pop global` with its bit offset, join against the manifest's flag
names, and report: writers and readers per flag, read-never-written, written-never-read,
and classes with zero inbound references (no shape, egg quality, npcnum, or `call`
pointing at them). Run inside the build gate; orphan quest-critical classes fail the
build. This mechanically prevents the orphan-script class of defect.

### 2.4 Quest-step tracking

The 18-step outline in TODO.md becomes the tracking spine. Current best-known state:

| Step | Beat | Blocking work |
|------|------|---------------|
| 1 | Lord British's message | LORDBRIT reachability unknown (2.1) |
| 2 | Mythran exposition | VERIFIED 2026-07-03 (both paths + stock handoff) |
| 3 | Find key, enter dungeon | Doors and key VERIFIED 2026-07-02; dungeon entry teleport verify |
| 4 | Collect 4 tokens | COLPUZZL not wired; token items unaudited |
| 5-7 | Meet Zealans, clan intro, Ragnar's tale | Dialogue reachable; quest-flag flow untested end to end |
| 8 | Passage Stone, Test, poisoning | PLNTST unaudited; water zombies not placed |
| 9-10 | Zealan mark, Ezrekal history | Dialogue reachable; flag flow untested |
| 11-12 | Tyorvi's key, nightmare potion | Dialogue reachable; root item and potion flow untested |
| 13 | Climb to Cloud City | CLCLIMB not wired; Map 17 terrain void |
| 14-15 | Sacred Circle ceremony, shades | AOSCENE not wired |
| 16-17 | Tiny Tar, enter Temple, free gods | Hrodny dialogue reachable; temple entry and FREE flow unaudited |
| 18 | Bag of Reagents, end | ENDGAME not wired |

### 2.5 Close the open dialogue defects

Atli's missing initial bark, the dead "Tell me more of the Test" option, and the
RAGNAR "no fight with you" dead end (needs a patched RAGNAR.UNK in `LOST VALE/`,
which the manifest and M0 build make safe to do).

### 2.6 Playthroughs

First an assisted run (debug teleports allowed, one step at a time, updating 2.4 as
steps verify), then the milestone exit test.

**Exit test:** one continuous no-cheat playthrough from a fresh game through
"Receive Bag of Reagents. END.", recorded (screen capture or step-by-step log with
screenshots), zero crashes, zero progression dead ends.

Estimated effort: 8-12 sessions over 2-3 weeks. The wiring itself is mechanical once
DD-007 is decided; the playthroughs will surface a tail of small fixes, which is the
point.

---

## 3. Milestone 2 - It looks and plays like 1994 intended

Goal: each area passes a side-by-side comparison against the 19 recovered screenshots,
and the encounters/puzzles hold up as gameplay. This is the creative long pole;
workstreams are ordered by quest order so partial progress is always playable.

### 3.1 Per-area visual passes

| Area | Map | Known issues |
|------|-----|--------------|
| Galjeron's Chamber | 9 | Never visually tested; prop fixes from the 2026-07-01 audit need in-game confirmation |
| Lost Vale overworld | 10 | Villages Phase 2 (interiors, clutter, paths); lake props on black water (2 placement WARNs) |
| Elemental Dungeon | 11 | Never visually tested; 3 placement WARNs; four element sections need distinct dressing |
| Cloud Cliffs | 13 | Never visually tested; entry teleports lack floor support (WARNs) |
| Cloud City | 17 | Worst gap: glob 78 void, nine floating placements, needs the white-and-gold palette from screenshots; likely needs custom cloud terrain shapes (wood-wall injection technique is the proven path) |
| Ancient Temple | 18 | Teleport entry needs ScummVM confirmation; shrine inner sanctum dressing |

Cross-cutting: fix all 18 placement WARNs, then escalate the no-floor-support rule
from WARN to ERROR so regressions gate the build.

### 3.2 Encounters

Design-from-scratch within the corpus framework (GAP-ANALYSIS): water zombies at the
lake (step 8), per-element dungeon monsters, harpies on the cliffs. Approach: base-game
monster eggs with tuned stats first; bespoke behavior usecode only where a quest step
requires it. Difficulty target is DD-009.

### 3.3 Puzzle depth

COLPUZZL and CLCLIMB are compiled sketches. Play them, then iterate the mechanics
(element matching, the climbing gauntlet, the Passage Test failure-that-poisons) until
they read as designed set pieces, not triggers. The 1994 docs give the framework
(four columns, opposite-element destruction, collapsing cloud ground); the specifics
are ours to author.

**Exit test:** screenshot comparison sheet per area (ours vs 1994) checked into
`shared/docs/`, and one full playthrough by a playtester who is not Douglas,
finishing without hints.

Estimated effort: 15-25 sessions over 4-8 weeks elapsed. Parallelizes well across
agents (one area per worktree, the village-pipeline pattern).

---

## 4. Milestone 3 - Release engineering

### 4.1 Art placeholder resolution

Finish `shared/docs/art-placeholder-audit.md`, then per item decide: repainted
base-game shape (proven cheap: wood walls), acceptable stand-in (document it), or
bespoke art needed. Static items first (Shield halves, god statues, talismans,
obelisk); animated creatures (Water Zombie, Harpie) are the only expensive class and
both have serviceable base-game stand-ins for v1. Publish the "what a future artist
would replace" list as part of the release notes; it invites contribution.

### 4.2 Audio

Map each LV area to a base-game music track (the engine already plays per-map music);
document the mapping as a deliberate v1 choice. No new SFX for v1 beyond what placed
base-game shapes already carry. DD-010 records the decision.

### 4.3 Distribution

The repo must never ship merged game data. Release form (DD-011, recommended):

- A release bundle containing only: our .UNK sources and compiled new-class data, map
  builder scripts plus manifests, the shape-injection scripts, the ScummVM patch, and
  an installer.
- The installer (evolved `install_lv.sh`) verifies the player's own GOG/original U8
  install by hash, then builds EUSECODE.FLX, FIXED.DAT, and U8SHAPES.FLX locally,
  exactly as the dev pipeline does today. No Origin-copyrighted bytes in the bundle.
- ScummVM: ship the detection-entry patch script for self-builds now; open an upstream
  ScummVM PR with the Lost Vale detection entry once the content stabilizes (removes
  the custom-binary requirement entirely).
- Repo hygiene before any visibility change: purge tracked merged artifacts
  (EUSECODE.FLX, FIXED.DAT, TYPEFLAG.DAT, U8SHAPES.FLX in `shared/build/`) from
  history, keep them gitignored like `shared/data/`.
- Note: no savegame patching is needed; the retail U8SAVE.000 already contains the
  locked doors, and all our additions live in FIXED.DAT and the FLX archives.

### 4.4 Beta

Small private beta with the community that made this possible (the Ultima Codex and
Ultima Dragons folks who recovered and analyzed the source), with a feedback template
keyed to the 18 quest steps. Their findings drive a stabilization pass, then public
release with credits honoring the 1994 team and the preservation chain.

**Exit test:** a person with only a GOG copy and the release bundle completes the
game start to finish on a machine this repo has never touched.

Estimated effort: 5-8 sessions plus beta calendar time.

---

## 5. Open design decisions (need sign-off)

| ID | Decision | Options | Recommendation |
|----|----------|---------|----------------|
| DD-005 | Mythran graft mechanism | (a) wrapper routes on `lbDone AND NOT mythranIntroDone`, intro plays once; (b) LV dialogue tail-calls stock use(); (c) inject LV topics into stock ask list via deeper binary patch | (a): smallest safe patch, matches the design doc's "door is always open", keeps the intro special |
| DD-006 | Stealth mode fate | (a) delete; (b) keep as error stub; (c) fix and scope to modified-base-only | (b): the code documents a real reverse-engineering finding (md5-5000 window); the stub costs nothing and cannot corrupt |
| DD-007 | Event-script dispatch | (a) UnkEgg quality (`quality + 0x47F`), no engine changes; (b) npcnum dispatch via our patch; (c) extend the ScummVM patch with a bespoke LV egg mechanism | (a) for eggs after the Map 22 spike passes, (b) for SIGRID; avoid (c), less engine divergence is better for eventual upstreaming. **Engine read done 2026-07-03:** SF_UNKEGG = shape 73 only (TYPEFLAG family 4); instantiated as Egg, hatch event fires once on avatar proximity; hatch x/y ranges are PACKED INTO npcNum (nibbles), which collided with our npcnum dispatch — engine patch now excludes egg families (scummvm-lv b818f9a0). Recipe: place shape 73, quality = class − 0x47F, range in npcNum nibbles. **Spike VERIFIED IN-GAME 2026-07-03** (Map 22, EGGSPIKE class 1453: hatch fired once on proximity, no re-fire). DD-007 DECIDED: (a) for event eggs, (b) for SIGRID. |
| DD-008 | RAGNAR dead-end fix | (a) patched RAGNAR.UNK in `LOST VALE/` adding the missing case; (b) leave as 1994 authenticity | (a): it reads as a bug, not a period quirk; note the change in release notes |
| DD-009 | Encounter difficulty | (a) tuned to base-game mid-game; (b) endgame-tier | (a): the expansion was pitched as post-mid-game content and the Avatar may arrive under-equipped |
| DD-010 | v1 audio scope | (a) base-track mapping only; (b) commission or arrange new music | (a) for v1; the pitch doc names no composer and silence on this blocks nothing |
| DD-011 | Release form | (a) build-from-owned-copy installer; (b) binary patches (xdelta) against known GOG files; (c) both | (a) first, it already exists as install_lv.sh; add (b) later if hash drift across GOG revisions bites |

---

## 6. Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Egg dispatch spike fails (UnkEgg hatch semantics differ from assumption) | Medium | M1 slips | Fallback is npcnum dispatch (proven) or a minimal engine-patch egg hook (DD-007c); spike is scheduled first in M1 |
| Savegame breakage from renumbered flags/classes | High without M0.6, near zero after | Players lose progress mid-quest | Manifest pinning (M0.6); never reuse a retired bit |
| Map 17 needs real custom terrain art, not just palette work | Medium | M2 long pole grows | Wood-wall injection is the proven path for custom shapes; timebox a spike; ugly-but-navigable cloud floor is an acceptable v1 floor |
| Creative fatigue on design-from-scratch content (dungeon, ceremony, endgame) | Medium | Project stalls in M2 | Quest-order sequencing keeps the game playable at every stop; each area is a bounded worktree task; the corpus framework constrains scope |
| ScummVM upstream churn breaks the local patch or build (brew/config.mk precedent) | Medium | Rebuild friction | Pin the scummvm-lv checkout; document the rebuild recipe; upstream the detection entry in M3 to exit the fork business |
| Legal posture of distributing restored 1994 source derivatives | Low-Medium | Release blocked or takedown | Build-from-owned-copy keeps EA bytes out of the bundle; the recovered source is already public via the Discord/Codex release; follow the community precedent (Lazarus, U6P); credits and non-commercial framing |
| Single-maintainer bus factor | Ongoing | Stall | PLAN.md, wiring.md, the manifests, TODO.md, and the dated review/devlog docs keep every decision reconstructable; beta community as eventual co-maintainers |

---

## 7. Sequencing, ownership, and model assignment

Strict order: M0 before anything (days). M1 before M2 polish makes sense (the spine
tells us which areas matter most). M2 and M3.1/M3.2 can interleave; M3.3/M3.4 last.

Model tiering principle: match the model to the cost of being wrong and the distance
to verification, not to how important the task feels. Volume work goes down-tier
behind mechanical gates; judgment work (debugging with distant causes, design within
canon, review synthesis) goes up-tier. The orphaned-scripts defect was a process
failure no model tier would have caught; a twenty-line validator catches it forever.
Gates first, then volume: that ordering is also the token-efficient one.

| Workstream | Owning agent(s) | Model | Effort | Mode |
|-----------|-----------------|-------|--------|------|
| M0.1/M0.2 surgical bytecode fixes (`this` push, Mythran graft) | usecode-compiler | Fable 5 or Opus 4.8 | high | Main session; verify in-game the same day |
| M0.3/M0.4/M0.7/M0.8 mechanical guardrails | usecode-compiler | Sonnet 5 | medium | Subagents in worktrees; acceptance tests are written |
| M0.6 id/flag manifest | usecode-compiler | Fable 5 design, Sonnet 5 implement | high, then medium | Savegame integrity rides on the design; the code is routine |
| M1 reachability audit, flag-graph tool | usecode-disasm (new read-only tool) | Sonnet 5 workers, Opus 4.8 verifiers | medium finders, high verify | Ultracode workflow fan-out (the prop-audit pattern) |
| M1 DD-007 egg dispatch spike | usecode-compiler | Fable 5 or Opus 4.8 | high | Main session; one decisive engine read plus a Map 22 test |
| M1 wiring placements | map-populator with usecode-compiler | Sonnet 5 | medium | Subagents per map; mechanical once the spike lands |
| M1/M2 playthrough verification and bug triage | coordinator, in-game | Fable 5 | max on debugging turns | Main session; bytecode-to-engine symptoms sit far from causes |
| M2 area visual passes | map-populator, one worktree per area | Sonnet 5 builders; Opus 4.8 or Douglas judging | medium | Parallel worktrees; aesthetic judgment is the bottleneck, not construction |
| M2 encounter and puzzle design | npc-dialogue (design docs) then usecode-compiler | Fable 5 docs, Sonnet 5 implement | high, then medium | Design doc gates implementation |
| M3 packaging and installer | coordinator | Sonnet 5 | medium | Spec is section 4.3 |
| M3 ScummVM upstream PR | coordinator | Opus 4.8 or Fable 5 | high | Code that strangers will review |
| Milestone-exit review | coordinator | (cloud) | n/a | /code-review ultra on each integration branch before merge |

Effort defaults: high for the main session; max reserved for debugging turns where
the first hypotheses have already died (leaving max on for mechanical work slows the
loop for no gain). Subagents run medium unless verifying. Opus /fast fits interactive
build-look-tweak iteration in M2 where latency dominates. Ultracode earns its tokens
on audit-shaped and adversarial work (reachability, flag-graph, pre-merge review,
screenshot comparison panels); it is waste on single-file fixes with a written spec.

Rough calendar at observed cadence (the village pipeline went decision-to-verified in
11 days; the prop audit ran in a day with parallel agents): playable spine around
end of July 2026; screenshot-faithful content through August-September; beta and
release in October 2026. These are planning anchors, not commitments.

## 8. Tracking conventions

- TODO.md checkboxes flip only with a verification note: date plus what was run in
  ScummVM (the Map 8 entry is the model).
- `shared/docs/wiring.md` is the single source of truth for script reachability;
  the flag-graph tool regenerates its data section on every build.
- Quest-step table (2.4) status lives in TODO.md once M1 starts; PLAN.md stays
  strategic and gets a status line per milestone, not per task.
- TODO.md is the live tracker and is updated at each milestone exit. (This line
  used to name a root MEMORY.md dashboard; that file moved to docs/MEMORY.md in
  March and froze as a Phase 0-3 archive. Agent MEMORY.md files are per-agent
  history, frozen at each agent's completion date.)
