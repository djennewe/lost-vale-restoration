# Improvement Plan, 2026-07-19

Companion to `2026-07-19-adversarial-review.md` (finding ids C1..C3, H1..H10,
M1..M22, L1..L22 refer to that file) and to the same-day research sweep
(ScummVM state, Pentagram docs, Lost Vale history, sister projects, AI art
workflows) and art proof of concept. Full sourcing for every research claim
summarized below lives in `docs/research/2026-07-19-ecosystem-and-history.md`
(ScummVM/Pentagram/Lost Vale history/sister projects) and
`docs/research/2026-07-19-ai-art-generation.md` (AI art workflows plus the
hands-on pipeline proof of concept); this plan distills those into action
items and does not repeat their citations. PLAN.md remains the strategic
roadmap; this document is the review-driven work queue that feeds it. Nothing
here changes the M1 goal (playable 18-step spine); most of it exists to stop
the toolchain from lying about progress toward it.

> **Progress (2026-07-24):** Section 1's commit gate is cleared (C2, M13
> fixed; H1 held as a finding; L22 closed). **C1** (compound-assignment
> miscompile) fixed with a regression test. **C3** (engine patch-survival)
> and **M17** (pinned clone) fixed: engine work is now a tracked, SHA-pinned,
> apply-or-fail patch series. All three criticals are now resolved. Next up:
> the map-pipeline hardening (H4 signed-z, H5 teleport gate, M12 monster
> eggs), the map gates (M9-M11), the Map 13/17 terrain + H6, and the compiler
> and test-estate items (H2, M2, M3, M5-M8). That tier is now COMPLETE.
> The packer addendum (P1/P2) is done too. **H8 and H9 are now done**
> (2026-07-25): `test_flx_packer.py` (9 tests) and `test_map_roundtrip.py`
> (12 tests) take the packer and the whole map pipeline from zero coverage,
> and H8 caught a live name-table bug on the way in. **M18 is done** too:
> `tools/run_all_tests.sh` runs the whole 14-file estate in ~7s and is what
> clean-room Step 6 now calls, and **L12** (FIXED.DAT stage-verify-promote).
> Section 3 is COMPLETE — including P3/P4. **M22** is done: the merged
> artifacts are untracked and the history purge has RUN (one outstanding
> step, a GitHub-side gc, blocks going public — see
> `docs/history-purge-plan.md` §6a). **Section 5, docs reconciliation, is
> COMPLETE.**
>
> **Status audit 2026-08-12**: the "Remaining: H7, P3/P4, M4, H3" line that
> stood here was stale — all five were already fixed in the code, each with
> a finding-labeled comment at the fix site: P3 repinned 2026-07-25
> (`test_patch_mythran.py` BYTE_IDENTITY_CASES block, plus
> `test_deployed_case_matches_manifest()` so it can't re-stale), P4 caught
> and routed through `failures` (`build_eusecode.py:849`), H7 subtracts
> `origin_z` (`building_prefab.py:157`), M4 resolves `this` against the
> parent stack (`u8c_sim.py:437`), H3 documented done in CLAUDE.md
> 2026-07-25. L21 (manifest indent) is also done — the stored file is
> indent=2. Remaining from this review: **the art/asset work in sections
> 6-7 only.**

---

## 1. Commit gate for the in-flight changeset (same day, before anything else)

The worktree-diff audit cleared the uncommitted 2026-07-19 changeset on the
savegame invariants (manifest strictly appends givenElixir/iAmDrunk, no pin
moved, detection hash untouched, FLAGS.UNK consistent with the bit-1024
window). Three items block a clean commit:

- [x] **C2** (2026-07-24, `9acf0e6`): shield half 2 restored to frame=1;
      SHADES.UNK keys on getFrame()=0/1, quality is cosmetic. FIXED.DAT
      rebuilt and verified.
- [x] **M13** (2026-07-24, `9acf0e6`): the two contradictory shield comments
      collapsed into one correct 539-state block.
- [~] **H1** (2026-07-24): the "prove the semantics" half is DONE — confirmed
      real from base-game bytecode; `startup{}/process{}` = loop once per tick
      with an implicit `suspend`. The codegen fix is specified but NOT applied
      (it would hang the no-wait monitors if done naively, and needs in-game
      timing verification). Held as a finding:
      `docs/reviews/2026-07-23-h1-process-block-semantics.md`.

The changeset was committed and pushed (`9acf0e6` code + artifacts, `e248d39`
docs) since H1 no longer blocks it — the once-through puppet is a documented
cosmetic limitation, not a regression. It also carried the Shield SI_FIXED
fix (580→539), EQ_* constants, the givenElixir/iAmDrunk flag allocation
(closes L22), the Map 17/18 shape-400 swaps, and a build-arg guard.

## 2. Quest-visible correctness fixes (next 1-2 sessions)

Ordered by blast radius:

- [x] **C1** (2026-07-24) compound assignment codegen (`u8c_codegen.py`):
      `+=`/`-=` on numeric locals now emit `push var; push rhs; add/sub; pop
      var`; String `+=` emits the base-game concat idiom; globals get
      read-modify-write; `^=` on a non-slist target warns instead of
      miscompiling. Operand order verified against uc_machine.cpp and
      base-game DOOR_NS. Regression test `test_compound_assign.py` (8/8);
      LVFREE re-emits real arithmetic; FLX grew +189 bytes.
- [x] **M12** (2026-07-24) monster egg quality encoding: `MapItem.monster_egg`
      packs `(prob<<11)|shape`; all 12 sites (maps 09/10/11/13/18) pass real
      family-6 creatures at prob 6 via lv_shapes.SHAPE_MON_*; validator rule
      (family-6 + nonzero prob) added and confirmed to catch a broken egg.
- [x] **H6** (2026-07-25) Map 13 return trigger 207 moved 1024 west to
      (3072,11776), off the north corridor to the gate. Fixed together with
      the root cause of the whole Map 13/17 mess: both maps tiled their floors
      with EMPTY globs (50 and 75), so the arrival pads had no ground at all.
      Now globs 49 / 65; summit platform paved at its true 128-unit tile size
      instead of a 512 stride. Validator: 11 WARN -> 0 WARN, 0 ERROR.
- [x] **H7** (2026-07-25) fixed, but NOT where the finding pointed, and the
      finding's model of the defect was wrong in a way that mattered.
      Ground truth first: the engine renders each glob item at
      `egg.z + item.z`, and the base game varies the EGG with the ground
      under it (globs 49/51 at egg z=48, glob 65 at 8/48/56) while placing
      all six house globs at egg z=0. So **the egg's z is the destination
      terrain datum**, and a glob's internal z values are authored relative
      to it.
      That makes `GlobPrefab.origin_z = min(item z)` the actual bug: it
      conflated "the structure's lowest item" with "the terrain level this
      structure expects", which is what `origin_z` means for BuildingPrefab
      (the Map 37 prefab documents it as "Map 37 terrain sits at z=64").
      For the two-storey house globs min-item-z is 40 — their ground-floor
      plate, shape 286, an 8x8 SI_LAND slab — and that is a DESIGNED raised
      floor, not a grounding offset: verified against the base game, where
      glob 573 sits on Tenebrae terrain whose LAND items are at z=0/8 with
      its own plate at 40. `origin_z` is now 0 for every glob, with
      `min_item_z` kept for diagnostics.
      The root cause, though, was in the CALLER: `village_layout` passed each
      prefab's own `origin_z` as `z_base`, i.e. a source datum as a
      destination height, making every relocation a no-op. That hit
      BuildingPrefab too — `hut_small_red` (origin_z=64) floated 64 units,
      which the finding did not mention. VillageSpec now carries an explicit
      `ground_z` (default 0, where Map 10's terrain globs put their walkable
      surface), used for the ground tiles and as `z_base` for every stamp.
      Also: `expand()` now uses the same egg z as `stamp()`, so previews stop
      lying, and an egg z outside 0..255 raises instead of wrapping to a
      ceiling-height byte.
      **No shipped bytes changed** — `village_layout`/`build_villages` are
      standalone and nothing imports them, so Map 10's villages do not come
      from this path yet and there is nothing to re-verify in-game. The fix
      stops the defect from shipping when the pipeline IS wired in. Covered
      by `test_glob_grounding`, which anchors on the base game's own egg z
      read live out of FIXED.DAT rather than a hardcoded number, and which
      fails if `origin_z` is reverted.
- [x] **H3** (2026-07-25) done, with the fix INVERTED from what the finding
      specified — following its recipe would have made the audit worse.
      The edge count is exactly as reported (20 edges, 8 classes, base FLX;
      19/7 built). What the finding missed: **every one of those edges is a
      self-edge** (PYROS→PYROS, DAEMSPEL→DAEMSPEL, …), which is what
      spawn-inline is — a coroutine started within the class at
      `offset+delta`. So there were ZERO false orphans, and adding those
      edges to the inbound tally would only have marked classes reachable
      because they refer to themselves.
      Checking that exposed the larger bug: `compute_inbound` was ALREADY
      counting self-edges from 0x11 and 0x57. 16 classes call themselves,
      130 spawn themselves, and for **54 the self-edge was their only
      inbound reference** — reported reachable purely for referring to
      themselves. That is a MASKED orphan, the dangerous direction, where
      the finding predicted only false orphans.
      Fix: (a) `spawn_inline` recorded in the summary — additive key, see the
      documented exception below; (b) self-edges collected under a `self`
      bucket and deliberately excluded from `inbound_total()`, since a class
      that only calls itself still has nothing to start it; (c) the ORPHAN
      row's hardcoded "(none)" replaced by the real breakdown, so an orphan
      with internal activity reads as `self-only:spawn` instead of looking
      like dead weight.
      **Result: 7 more LV classes now flagged** — EGGMAGNET, TYPEPOTION,
      TYPEPOISONPLANT, TYPEPEDESTALS, TYPENSGOLDPLAQUE, EGGSHADES,
      TYPEAOFRIZBEE — each previously "reachable" on a self-edge alone.
      These are candidates for investigation, not confirmed defects; the
      audit's job is to raise them. `shared/docs/wiring-data.md` regenerated.
      **Rule exception (CLAUDE.md, Technical Constraints):** scoped to
      `disassemble_class_summary()` only. That method has exactly two
      consumers (the disassembler's own `summary` CLI and
      `u8_flag_graph.py`), and round-trip/encoder both use
      `disassemble_class()` — the listing path — so the summary layer cannot
      affect round-trip byte-identity. Verified rather than asserted:
      round-trip 516/516 and the encoder test both unchanged after the edit.
- [x] **M4** (2026-07-25) `_run_child` now resolves `this` BEFORE installing
      the child's stack. `thisptr` is almost always a stack pointer into the
      PARENT's frame — the `push dword [BP+06]` idiom in front of nearly
      every spawn — and `ptr_to_object()` dereferences stack pointers through
      `self.stack`, so resolving it after the swap read a freshly zeroed
      child stack and silently produced objid 0.
      Reproduced before fixing, with a synthetic two-class FLX driven through
      the real sim: parent holds item 1, child observed `this=0`. With the
      fix the child observes 1; reverting the ordering makes it 0 again.
      Also added a warning when a spawn's `this` resolves to 0, so the null
      case can never again be silent.
      **Blast radius, measured rather than assumed:** instrumenting every
      `_run_child` call across all three sim-driven test modules (dialogue
      92, plntst 20, sim 35) found exactly ONE followed spawn — the new
      synthetic fixture. No current quest scenario reaches a followed spawn
      with a stack-pointer `this` (the wait()/FX spawns go to retail FREE
      0x581, which is deliberately not followed), so no existing assertion
      changed. The defect was real and is now fixed and covered; it simply
      was not yet reachable from the scenarios in the suite.
      Regression test lives in `test_uc_sim.py` (35 checks) and asserts the
      mechanism on a synthetic class pair, so it cannot drift when quest
      bytecode changes.

## 3. Guardrails: make the lying-build class structurally impossible

The M0 milestone closed exit-0-on-failure in `build_eusecode.py`; the same
discipline has not reached the map pipeline or the test layer.

Build gates:
- [x] **H5** (2026-07-24) teleport-pair failure now `sys.exit(1)`s before `archive.save()`.
- [x] **M9** (2026-07-25) duplicate teleport ids detected (lists per id); also fails on an in-range id missing from TELEPORT_TABLE.
- [x] **M11** (2026-07-25) post-save read-back asserts every written map's
      count and that untouched base maps are unchanged; mismatch exits 1. No
      manifest change needed — intended counts are captured at build time.
- [x] **M10** (2026-07-25) misleading "(ERROR)" comment fixed + a ratchet
      (`KNOWN_FLOATING_LV_TELEPORTS = 5`): any NEW floating LV teleport is a
      build-blocking ERROR. Straight escalation was impossible — 5 real
      violations exist on the incomplete Map 13/17 terrain, two of them
      arrival DESTs that drop the player.
- [x] **H4** (2026-07-24) z packed unsigned (`<B`) both directions, byte-safe
      (FIXED.DAT identical, 4258 high-z base items round-trip). The audit
      found 49 INTENTIONAL negative-z LV placements, so z<0 is NOT rejected;
      it is flagged pre-serialization as a NOTE. The `z>200` validator was
      NOT re-aimed — base legitimately uses high z 6,229x, so a threshold
      only floods. **(2026-07-25) The 49 stray placements are now DELETED**
      after a render proved them redundant floating debris; 0 remain.

Compiler and binary layer:
- [x] **M2 + M19** (2026-07-25) event handlers are marked with `__event_N`
      labels and `build_class()` reads their corrected offsets back out of
      `_labels` (reusing the in-place shift machinery rather than replaying
      the insertion log, whose positions are not mutually comparable).
      `test_trampoline.py` (5/5) synthesizes a >32KB class and asserts every
      event entry lands on an instruction start. Same-class call/spawn
      offsets were already safe via `funcoffset` fixups. Confirmed ATLI has
      12 relays but all handlers precede the first one — the bug was latent,
      exactly as diagnosed; FLX byte-identical.
- [x] **P2** (2026-07-25) the build stages to `EUSECODE.FLX.staging`, runs
      Gate 6 against it, and `os.replace()`s only on success; a rejected build
      is quarantined as `.failed` and the previous artifact is untouched.
      Both byproducts gitignored. Verified with a forced Gate-6 rejection.
- [x] **P1** (2026-07-25) `lv_patched_results` added to the Gate 7 sweep,
      duplicated `provider_results` dropped. Verified with a temporary
      patched-tier file carrying a recovered parse error.
- [x] **P3/P4** (2026-07-25).
      **P3**: the 'real' case pinned bits 678/796 and class 0x0279; the
      deployed values are bits 1702/1820 and class 0x05AB. Both produce 85
      bytes, so the stale pin locked a same-length, different-content blob
      the build never emits — an operand-encoding regression on the real
      offsets would have sailed through. Rather than re-point it and lose
      evidence, the old case is KEPT as `historical` (its digest is the only
      one captured from the pre-M0.8 hand-rolled implementation) and a new
      `deployed` case carries the live parameters. The new digest was
      computed from the current BytecodeEmitter implementation, which is
      sound precisely because the other four cases still pin that
      implementation to the hand-rolled bytes.
      New `test_deployed_case_matches_manifest()` reads
      `lv_manifest.json` and fails the moment the pinned parameters diverge
      from what the build actually passes, naming each drifted field and how
      to re-pin — so P3 cannot recur silently.
      **P4**: the four Mythran guards (zero use offset, moved use event,
      preamble hash mismatch, 16-bit overflow) now report through `failures`
      like every other gate instead of escaping as a raw traceback. Catching
      them also stops the UNPATCHED 0x421 being handed to Gate 6 as though it
      had been patched. Verified by forcing the preamble-hash guard: 1
      failure line, nonzero exit, no traceback, no FLX written.
      Neither change moves a byte — all four artifacts still match their
      canonical hashes.
- [x] **M3** (2026-07-25) `lv_manifest.validate()` asserts both cursors sit
      past every pin and that the class cursor is not itself pinned; verified
      with a rolled-back-cursor negative control.

Test estate:
- [x] **M5/M6/M7** (2026-07-25) all three now exit nonzero on failure;
      test_parser_all fails hard on a missing corpus and ratchets parse issues
      at the baseline of 23 (zero is not achievable — the sweep includes
      base-game /U8/ sources the build never compiles).
- [x] **M8** (2026-07-25) instruction-shaped lines that fail the regex are
      recorded in `parse_drops` and fail test_encoder; 0 across the base FLX.
- [x] **H2** (2026-07-25) new `assemble_class_encoded()` + `test_encoder.py`:
      499/516 classes reassemble byte-identically through the real encoder,
      and disagreements are recorded/asserted instead of silently overwritten
      by raw hex (closes L8 too). Two listing-format limits pinned and
      ratcheted (7 lossy non-ASCII strings, 17 unparseable classes).
      test_roundtrip now says outright that its Phase 2 is the raw-hex path.
- [x] **H8** (2026-07-25) `test_flx_packer.py`, 9 tests: synthetic
      multi-entry pack with an interior empty slot (reread byte-identity,
      offset monotonicity, count, determinism, gapless data area);
      original-offset ordering; the usecode name-table layout; the real base
      EUSECODE.FLX round trip plus the two mutations the real build performs
      (larger replacement class, new class into an empty interior slot AND
      past the end) proving nothing else shifts; and the retired stealth
      path asserted STILL BROKEN — the reclaim-before-place allocator gives
      the first of two adjacent oversized replacements all the merged space
      and leaves the second's index pointing into the overwrite, so it reads
      back as neither its old nor its new data. The `--stealth` CLI gate is
      checked too.
      **Found and fixed a live bug:** `UsecodeFlxPacker.from_existing()`
      required a full 13-byte name record, but the base game's name table
      ends in a truncated one (18603 = 4 + 1430*13 + 9). Class 1430's name
      (`AIRSPEL`) was therefore dropped from every rebuilt name table — the
      shipped `shared/build/EUSECODE.FLX` had it blank. Fixed by matching
      the reader's 9-byte tolerance; FLX rebuilt. Detection is unaffected
      (the name table lives past the md5-5000 window and the file size is
      unchanged), so no ScummVM relink was needed.
- [x] **H9** (2026-07-25) `test_map_roundtrip.py`, 12 tests:
      `from_bytes(to_bytes(item))` byte- and field-identical across all
      87,603 base-game records; the signed-x/y, unsigned-z (H4) and
      out-of-range edges; the egg encoders including the M12
      `(prob<<11)|shape` packing and its guards; base FIXED.DAT
      save/reload item-identity with an index-table structural sweep;
      validator rule regression from known-bad synthetic items (missing
      shape, out-of-range frame, egg exemption, monster-egg family/prob
      warnings, `LV_TELEPORT_NO_FLOOR` with a paved positive control); the
      shipped FIXED.DAT pinned at 0 ERROR / 0 WARN; teleport-pair
      completeness on the shipped artifact plus four negative controls
      (missing dest, duplicate trigger, wrong map, id outside
      `TELEPORT_TABLE`) and the deliberate Map 22 debug id 250; and the M10
      ratchet proven to block a build. Mutation-checked for non-vacuity.
- [x] **M18** (2026-07-25) `tools/run_all_tests.sh`. It DISCOVERS tests
      (`agents/*/src/test_*.py`) rather than listing them, so a file added by
      one agent is never invisible to the next, and it fails outright if
      discovery turns up fewer than `MIN_TESTS` (pinned at 14, may only go
      UP) — a bad glob or a deleted test cannot read as a green suite. The
      exit code is the verdict, with a secondary net: output containing a
      top-level `FAILED` or a traceback fails the test even at exit 0, which
      catches a regression in the exit discipline M5/M6/M7 established.
      (`FAIL` alone is unusable as a marker: test_parser_all prints per-file
      FAIL lines for its 23 pinned sources while passing.) Prints each
      artifact's md5 up front so a result says which bits it was about, the
      failing tests' full output at the end, and one `OVERALL:` line. Flags:
      `-v`, `-l`, and substring filters. Whole estate: 14 files, ~7s.
      Clean-room Step 6 now calls it instead of naming three files by hand —
      the other eleven had never run in the clean room. Verified against a
      real fresh clone (tracked artifacts + symlinked game data): 14/14.
      A GitHub Actions workflow stays optional until the repo has a remote.
- [x] **L12** (2026-07-25) FIXED.DAT now gets the same stage-verify-promote
      treatment P2 gave the FLX, at two layers. `MapArchive.save()` writes to
      a unique `<name>.<random>.staging` file beside the target and
      `os.replace()`s it in, cleaning up on any exception including
      KeyboardInterrupt — a Ctrl-C or a full disk part-way through 1.6 MB can
      no longer leave a truncated FIXED.DAT at the path install_lv.sh
      installs from. `build_all_maps.py` then stages to
      `FIXED.DAT.staging`, runs the M11 read-back against the STAGED file,
      and only promotes on success; a mismatch is quarantined as
      `FIXED.DAT.failed` with the previous known-good artifact untouched.
      Previously the read-back ran against a file that had already replaced
      the last good build, so it exited 1 with the bad artifact in place.
      Verified both ways: a forced item-loss bug quarantined correctly
      (exit 1, target byte-identical, no staging left), and two clean
      rebuilds reproduce the committed FIXED.DAT byte-identically. Covered
      by a new `test_save_is_atomic` in test_map_roundtrip.py (13 tests now).

## 4. Reproducibility and the upstream path (research-informed)

The research sweep changes the upstream picture materially: ScummVM already
ships a detection entry for a fan-modified `usecode/eusecode.flx` (Spanish
translation, bug #14484, committed with the comment crediting the contributor),
plus Ultima 4 and Ultima 6 fan-translation entries added in 2025, and a
2025-07-14 policy commit "always keep all detection entries". Detection is
Advanced-Detector md5 plus filesize on eusecode.flx. Active ultima8 committers
2025-2026: Cameron Cawley, Matthew Jimenez, Michael Kuerbis, sluicebox, with
Eugene Sandulenko and Paul Gilbert landing detection changes. No Lost Vale
mention exists anywhere in ScummVM's tracker, forums, or wiki: this project is
the first mover.

- [x] **C3** (2026-07-24): engine work exported to
      `tools/scummvm-patches/0001-lost-vale-engine.patch` (item.cpp npcNum
      dispatch, map.cpp NPC Actor promotion, kernel.cpp resetRef debug; +78
      lines, detection hunks excluded since the script regenerates them).
      `build_scummvm.sh` pins the clone to base SHA `01bd8879`, applies the
      patch after clone, and exits nonzero if any hunk fails. `--clean` is now
      safe. Validated end-to-end against a fresh GitHub fetch.
- [x] **M17** (2026-07-24): folded into the C3 fix — the clone is pinned to a
      tested SHA (`01bd8879`) via `git fetch --depth 1 origin <sha>`; the
      rebase recipe lives in `tools/scummvm-patches/README.md`.
- [~] **M22** (2026-07-25) untracking DONE, purge EXECUTED, one remote-side
      step outstanding (see the end of this entry).
      The four `shared/build` artifacts are `git rm --cached`ed and
      gitignored, plus a FIFTH the review's inventory missed:
      `shared/maps/FIXED_TEST.DAT` (1.4 MB — the base game's 42 maps plus one
      122-item test map, referenced only by March devlogs, read by no code).
      Preconditions established first: all four artifacts were proven
      byte-reproducible from owned game data before anything was untracked,
      via the new `tools/build_artifacts.sh` (TYPEFLAG → U8SHAPES →
      EUSECODE → FIXED, in that order because the map validator reads the
      *patched* TYPEFLAG/U8SHAPES). Reproducibility survives without the
      bytes: `shared/build/ARTIFACTS.sha256` is tracked, `shasum -c`
      compatible, and `--record` rewrites it as the decision record for a
      deliberate artifact change. Clean-room Step 3's
      committed-vs-run1 comparison — impossible now — is replaced by a
      canonical-hash check plus a new Step 3b that builds the other three
      artifacts the way a player will. `install_lv.sh` now names all four
      missing artifacts and points at the build script. Verified end to end
      in a fresh clone with zero artifacts: build → all four match the
      canonical hashes → estate 14/14.
      **The history purge RAN the same day** (`docs/history-purge-plan.md`
      §6): `git filter-repo` stripped the five paths plus `gog/` from all 162
      commits, local `.git` went 99 MB → 5.4 MB, and all 6 origin branches
      were force-pushed. **Still outstanding, and it blocks going public:**
      force-pushing does not garbage-collect, so GitHub still serves the
      pre-purge commit and the 15 MB U8SHAPES.FLX blob by SHA (verified via
      the API). A GitHub Support request to run `gc` is required; §6a has the
      two checks that must both 404. That document
      corrects the review's figures — 61 commits touch the artifacts, and
      because FIXED.DAT/EUSECODE.FLX were re-committed on nearly every
      content change, history holds dozens of ~1.5 MB revisions of each,
      well above the review's "roughly 18 MB". It also records a separate
      find: a `git stash -u` from 2026-03-21 swept the raw GOG downloads
      (41 MB of bundle extras) into `refs/stash`. That commit was never
      pushed — no disclosure — but it is most of why local `.git` is 99 MB,
      and clearing it is a purely local `stash drop` + `gc`, not a rewrite.
- [ ] Deterministic canonical build: two clean builds already byte-match
      (M0.6 exit test); extend that guarantee across machines (no
      timestamps, stable ordering) so ONE canonical md5+size exists per
      release. Detection needs a stable hash; note the md5 covers only the
      first 1 MB of a ~1.4 MB file, and the FLX index at the file head
      changes on every content change, so no free pass there.
- [ ] Submission plan, two decoupled asks:
      1. Detection entry only, modeled verbatim on bug #14484 (bug tracker
         report with md5+size of the canonical build, one-line
         detection_tables.h row, extra label "The Lost Vale", ADGF_UNSTABLE
         initially). Interim option that needs zero upstream work: ScummVM's
         launcher add-anyway flow for unknown variants.
      2. The npcNum dispatch engine patch as a separate later PR, reframed as
         either gated behind the LV detection flag (inert for stock Pagan) or
         generalized; an engine change that exists only for unofficial
         content is the harder sell, so land detection first.
- [ ] Provenance dossier for the submission and release notes: the recovered
      usecode chain (Sheri Graner Ray's WIP diskette, Joe Garrity's Origin
      Museum, Dominus Dragon, Ultima Codex 2025-02-20 release), explicit
      statement that the bundle ships zero Origin bytes and never
      redistributes the recovered source, build-from-owned-copy alignment
      with the FAQ language. Watch items: no rights-holder statement exists
      (tolerance is inferred, not granted), and Richard Garriott's reported
      2027 copyright reclamation could change who the rights holder even is.

## 5. Documentation reconciliation (one mechanical session) — DONE 2026-07-25

The audit found the docs stratified in time with TODO.md the only current one.

- [x] **H10** (2026-07-25) CLAUDE.md and PLAN.md now name TODO.md as the live
      tracker in both the Architecture and Coordination Protocol sections,
      and both say outright that no root MEMORY.md exists. docs/MEMORY.md is
      explicitly archived: a banner marks it a frozen 2026-03-21 Phase 0-3
      snapshot, explains that 5cec802 moved it and it then went unmaintained
      for four months, and routes the reader to the five live documents.
- [x] **M20** (2026-07-25) CLAUDE.md's artifact stats corrected — and the
      review's own figures were already stale: it is **49 maps / 97,019
      items** (not 96,948) and EUSECODE.FLX is 1458 entries / **548
      non-empty classes (516 base + 32 new LV)**, replacing the old
      "1431 base + 34 new" line that conflated class SLOTS with classes.
      The Known Limitations "2 of 47 files" is now "2 of the 43 the build
      compiles", with a note that both are allowlisted.
- [x] **M21** (2026-07-25) HANDOFF.md regenerated from actual state via the
      handoff-init skill. The old one was frozen at 2026-04-04 with all five
      Next Steps complete (wood-wall injection, Map 10 villages, Map 17
      terrain, the Map 18 and Map 8 verifications) and wrong stats
      throughout (1,404,253-byte FLX, 45/47 compiling, 95,385 items).
- [x] **M15** (2026-07-25) the stock-ScummVM fallback is gone from both
      install_lv.sh and play.sh — it only ever worked with a --stealth build,
      so it silently launched plain Pagan. Both now fail with a pointer to
      build_scummvm.sh. install_lv.sh's dead `size != 1251108` branch (always
      true post-stealth) became a useful check: equality now warns that the
      BASE game FLX got installed by mistake.
- [x] **L19** (2026-07-25) lv-patched/ documented in CLAUDE.md as the
      highest-precedence source tier, with all four files and why each
      exists, plus the rule that fixes go there rather than into the
      read-only recovered snapshot. Known Limitations refreshed: the art
      audit is no longer "pending" (both docs named, the 2026-07-19 one
      marked authoritative), and the Ragnar entry now says the dead-end is
      still unfixed while noting lv-patched/RAGNAR.UNK exists — the review
      called that patch "in flight" for the dead-end, but it is a spelling
      sweep that explicitly changes no other byte.
- [x] **L7/L18** (2026-07-25) the TYPE_SHAPES note is corrected in place: it
      claimed 102 entries (there are 103) and named TypeMythranLVDlg as a
      dead entry, but that is a class name and has never been a TYPE_SHAPES
      key. The stale "~75 of 102 live" figure is now flagged as never
      recomputed. All six agent MEMORY.md files carry a FROZEN banner with
      their real last-touched date (four at 2026-03-21, one 2026-03-20, one
      2026-07-05). shared/docs/art-placeholder-audit.md is marked SUPERSEDED
      while preserving what only it still carries: the 1500-1700 new-shape
      id allocation and the four placeholder call-outs u8c_symbols.py cites.

## 6. Art completion strategy

### 6.1 Pipeline: proven today, one script from in-game

The 2026-07-19 proof of concept generated three assets and pushed them through
the full local pipeline: prompt, generate (Codex gpt-image-2 for the god
statue; agy Nano Banana with 1994-screenshot style references for the Water
Zombie and cloud tile), chroma-key, downscale to game scale, quantize to
U8PAL.PAL (24-30 colors each), encode via `lv_wood_wall.encode_frame` and
`encode_shape_blobs`, and pass `validate_shape` (the engine-faithful SIGBUS
guard). Files: `shared/docs/art-poc/` (raw, game-scale, 3x previews, .shp
blobs in the session scratchpad).

Remaining gap, per the pipeline audit, is one driver script:

- [x] **DONE 2026-07-25.** `tools/png2shape.py`: PNG in, quantize with
      transparency to index 0xFF against palette indices 0..254, anchor
      convention (`--anchor bottom-center` default, `--anchor donor` for
      terrain, `--anchor explicit`), encode, validate, `inject_shape` into an
      EMPTY slot 859+ of shared/build/U8SHAPES.FLX, TYPEFLAG entry copied
      from a donor, in one command. Multiple PNGs become one multi-frame
      shape. Covered by `agents/map-populator/src/test_png2shape.py`
      (31 checks, mostly refusals).
- [x] **DONE 2026-07-25.** Statue injected as shape 859 in a worktree:
      1024x1536 raw → 58x110, 29 U8PAL colours, 4779-byte blob (byte-identical
      in size to the PoC's), `validate_shape` clean, re-reads as
      `58x110@(29,110)`, TYPEFLAG 859 = `030030a400010001`. Preview:
      `shared/docs/art-poc/statue_shape859_preview.png`.
- [ ] Remaining for the in-game test: place shape 859 in the Map 22 gallery,
      rebuild, relink if the md5-keyed detection complains (documented trap),
      teleport, screenshot. Note `tools/build_artifacts.sh` rebuilds
      U8SHAPES.FLX from the base game and drops a hand-made injection, so
      placement needs the injection wired into a builder (and a deliberate
      `--record` of the new artifact hashes).
- [x] **DONE 2026-07-25, earlier than planned.** TYPEFLAG *authoring*: no
      base-game shape has both the right behaviour and a volume matching a
      58x110 monument (the two candidates with a fitting footpad are
      editor-only translucent props), so `--footpad X,Y,Z` overrides the
      donor's box while keeping its flags/family/weight. The wanted footpad
      is computed, not guessed, by inverting the engine's own projection.
- [ ] Later: sprite-sheet slicing for multi-frame shapes (one PNG per frame
      works today; slicing a strip does not).
- [x] **L14/L15 DONE 2026-07-25.** 855 dropped, not completed: its only
      consumer (the shape-556 floor remap) was deliberately removed in
      build_map_10.py because 556's items reference frames 27-29 that a
      4-frame custom tile does not have, so the tile was never generated,
      injected or TYPEFLAG-patched. Constant, dead generator code and stale
      "855-858" references removed; the id is unallocated.
      `inject_shape` now raises without `force=True` (`--force`).

### 6.2 Asset backlog (from the authoritative 2026-07-19 audit)

Coupled fixes (TYPE_SHAPES plus map together, no new art needed):
- [ ] Shades visible: TypeShades 73 (invisible egg) to 411 "ghost" so the
      ceremony spirits exist on screen.
- [ ] Gold plaques: 158 "stool" to 599/614 "plaque" (keeps look()/use()
      dispatch coherent).
- [ ] Obelisk: 721 "chimney" to 442/793 "obelisk tip" as the stand-in tier.
- [ ] Nightmare-elixir vial: move the four hard-coded frame 13s to frame 0
      (EZREKAL.UNK:3339/3342, TYORVI.UNK:2058/2088); frame 13 is a crystal
      shard, the real vials are frames 0-5.

Readability blocker with partial art need:
- [ ] Elemental columns: four identical chimneys make the puzzle unreadable.
      Interim: distinct base-game shapes per element; proper: four new static
      shapes (easy class, see 6.3).

New-art backlog, static (proven generation class):
god statues in two states (encased and freed, 3 gods), distinct shield halves
plus restored shield (3 sprites), cloud terrain tiles (PoC exists), obelisk,
Special Root (no base-game root exists; audit calls it the best new-art
candidate among smalls), talisman polish.

New-art backlog, animated (the expensive class):
Water Zombie and Harpie. Note M12 means the current eggs would not spawn
correctly regardless of art; fix the encoding first, ship tuned base-game
creatures for v1 (PLAN 4.1 already accepts this), and treat bespoke animated
sprites as the stretch goal.

### 6.3 Generation workflow guidance (from the PoC plus research)

- Static props: either tool works today. Nano Banana (agy) followed style
  references (actual 1994 screenshots) noticeably well; gpt-image-2 (codex)
  nailed the statue in one shot. Always generate large on flat magenta,
  key, downscale, quantize downstream (palette lock in-generator is not
  needed; 19-30 U8PAL colors survived quantization cleanly in all three
  tests).
- The U8 camera: prompt for "oblique dimetric, about 45 degrees from above,
  light upper left"; expect to iterate. The cloud tile came back steeper than
  U8's 2:1 ground diamond; a follow-up prompt pinning the 2:1 ratio (or a
  donor-shape silhouette as reference image) is the fix.
- Animated creatures, three routes in preference order per the research:
  PixelLab (8-direction sprite rotation, skeleton walk/attack cycles, API);
  Blender-render-then-palettize (deterministic camera and frame consistency);
  reference-chained Nano Banana Pro frames (works for short loops, drift risk
  grows with frame count). Per-frame palette consistency: build one global
  palette per creature and map every frame through it, which the existing
  quantizer already does by construction against U8PAL.
- Community and licensing: GWChapman's public U8-themed sprite trove
  (github.com/GrantWChapman/Ultima-VII-Artwork plus the 2026-03 batch) is a
  candidate source; license is unstated and the format is U7-palette Exult
  .shp, so both permission and conversion are needed. For AI-generated
  assets, the research flags real backlash precedent in retro communities:
  disclose the toolchain in release notes, keep AI assets clearly separable
  and original, and treat the 22 screenshots as the fidelity bar.

## 7. Design fidelity backlog (from the history research)

- [ ] Mine the Pentagram docs/ folder (u8usecode.txt, u8mapfmt.txt,
      u8typeflag.txt, u8gfxfmt.txt, shapes.cmp.txt, u8anim.txt, savegame.txt)
      into shared/corpus as pinned reference specs; when they disagree with
      the live engine, ScummVM source wins (uc_machine.cpp is the opcode
      ground truth; u8_intrinsics.h is a second check against our 258-entry
      table).
- [ ] Cross-check MAGNET.UNK against Graner Ray's own description of the
      obelisk puzzle: candlesticks lit "in the shape of an ankh" release the
      sealed equipment. If the recovered source supports it, restoring that
      staging is high-fidelity flavor for step 12.
- [ ] Cross-check PLNTST/the poison arc against her poisoned-garden
      description (gates slam, plants attack, timed antidote).
- [ ] Decision candidate for the dialogue pass: one clan speaking in
      inverted syntax (she wrote it, then regretted it; adopting or dropping
      it is a DD-worthy authenticity call, and the recovered dialogue itself
      is the evidence either way).
- [ ] Lock proper-noun spellings against the design docs and wiki: gods
      Felicitar, Doloras, Timyra; priestess Ezrekal/Ezrakel; Galjeron;
      TinyTar (John Watson's spell). Sources: the 30+ scanned pages at
      gallery.ultimacodex.com (three plot-synopsis revisions, walkthrough,
      character list, art lists, resource schedule) plus the GOG design-doc
      bundle already in gog/.
- [ ] M2 screenshot comparison sheets: the history sweep catalogued what each
      of the 22 screenshots depicts (gods in force fields, obelisk ringed by
      pillared gems, lava-pedestal gem, blue-head throne room, mushroom
      garden by a house); map each to its map slot as the per-area
      comparison target PLAN 3.1 calls for.

## 8. Ecosystem and outreach

- The parallel effort is "Ultima 8: Exult" (Ideal Dragon lead, with Stardrop,
  Agentorangeguy, GWChapman, Son), a from-scratch Pagan remake in the Exult
  engine, active through at least 2026-03, Discord-gated, no formal Lost Vale
  announcement (one "specific major cut content area" tease). Complementary,
  not competing: same recovered usecode corpus, different engine, and this
  project is the only one compiling it to run on ScummVM.
- Venue for announcement or deconfliction: the Ultima Dragons Discord
  #ultima-8-exult channel, where Dominus Dragon released the usecode and
  Armitage published the community storyline analysis this project has since
  substantially exceeded (resolved Passage Test, Shield ceremony, Ragnar bag
  gate, elixir knot). The Ultima Codex reliably features such projects.
- Toolchain neighbor: TITAN (`pip install titan-ultima`, The Grey Wanderer,
  2026-03, dialogue export added 2026-05) overlaps our FLX/map read layer;
  our usecode compiler is unique. A notes exchange is cheap and both sides
  benefit.
- Credits posture for any release: Dominus Dragon and the Origin Museum chain
  for recovery, Sheri Graner Ray and the 1994 team for the design (note the
  wiki's Brian Martin credit conflicts with her memoir naming Lisa Smith and
  Rob Corell; state both rather than adjudicating).
- Correction recorded in project memory: earlier notes attributed the sister
  project to "Yari Wildheart" with a Graner Ray map sketch; public sources
  support neither, and the claims trace to unfetchable Facebook posts. Treat
  as unverified until seen first-hand again.

## 9. Suggested sequencing

| Order | Work | Findings | Size |
|-------|------|----------|------|
| 1 | Commit gate on the in-flight changeset | C2, M13, H1 | hours |
| 2 | ScummVM patch series export + pin | C3, M17 | hours, urgent (data-loss risk) |
| 3 | Compound assignment + egg encoding + teleport bounce | C1, M12, H6 | 1 session |
| 4 | Map pipeline gates + z-signedness + tests | H4, H5, H9, M9-M11 | 1-2 sessions |
| 5 | Compiler guardrails + test exit codes + runner | M2, M3, M5-M8, H2, H8, M18, M19 | 1-2 sessions |
| 6 | Docs reconciliation | H10, M15, M20-M22, L7, L18, L19 | 1 session |
| 7 | png2shape driver + statue in-game + coupled shape fixes | 6.1, 6.2 | 1 session |
| 8 | Reachability audit unblock + resume PLAN M1 wiring | H3, then PLAN 2.1-2.4 | ongoing |
| 9 | Upstream detection entry once content stabilizes | section 4 | PLAN M3 |

Model tiering per PLAN section 7 holds: items 3-5 are mechanical with written
specs (mid-tier agents behind the new gates); H1 and anything touching the VM
contract stays up-tier with in-game verification.
