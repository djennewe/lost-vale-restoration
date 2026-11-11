# HANDOFF.md

The baton between sessions: next action, current state, blocking questions,
and nothing else. Durable content goes to `TODO.md`, `.claude/rules/`, a skill
or `docs/`.

Last updated: 2026-11-09.

## 2026-11-09: phases 2-3 merged; walkable viewer with live feedback

**Phases 2-3 are merged and integrated** (FIXED `f1c3ccc1`, estate 57/57
after every merge, each map's pins identical to its slice). Eight map
slices, plus two follow-ups:
- `wt/vq2-art`: shape 896 decorative water in Map 11's Water section, 897
  see-through 566 in Map 18's west passage, clipped 895 frames for Map 11's
  last black edges;
- `wt/vq2-m17b`: Map 17's quest-leg occlusions 46 -> 0.

Reports: `docs/research/2026-11-01-visual-pass/mNN-REPORT.md`, `art-` and
`m17b-REPORT.md`. Merge helper: `/tmp/claude-1000/vq2/merge.sh NN [branch]`.

Astra graded the eight slices' pairs: 9 fixed, 13 improved, 13 unchanged,
**13 regressed**. The page is
`https://devhost.invalid/a/lostvale-art/phase23.html`. The regressions
are mostly:
- void outside walls filled with floor-like tiles (Maps 11, 18, part of 13),
  so it reads as more floor;
- Map 10's D3 flush edge, a strip of tiles over flat navy.

**Not yet done:**
- the ScummVM verify walk of phases 2-3 (§5's walks);
- `TODO.md` notes.

**Walkable viewer** (committed `1020290`, regenerated on `f1c3ccc1`):
- Address: `https://devhost.invalid/lostvale-maps/` (user unit
  `lv-map-viewer.service`, `tools/map_viewer/README.txt`).
- Douglas walks and pins notes (F / right-click). Notes land in
  `docs/map-feedback/events.jsonl` and `OPEN.md`.
- Answer with `curl localhost:8460/api/notes/<id>/reply|status`.
- No collision.
- **Regenerate it after every FIXED change.**

**Next: phase 4 (dressing).** Douglas, walking the viewer: "the retail maps
look notably nicer than ours".
- Measured: retail has 17-73 small props per 100 floor tiles; ours have 3-16.
- Retail content is 5-11x glob-expanded; ours is 1-2x.
- Map 10 is twice a retail map's area at a sixth of its density, and it is
  near its 25,000 raw-record cap, so dressing has to come mostly from globs.
- **Direction done** by Fable 5.2:
  `docs/research/2026-11-01-visual-pass/phase4-direction.md` (`0636479`),
  measured with `dressing_metrics.py` (`--regions`: 118 target failures
  across 39 regions today).
  - Mocks: `https://devhost.invalid/a/lostvale-art/phase4.html`.
  - Douglas's D1-D8 are in §8 (`43cdeb5`). D1 is (c): a hand-authored set
    piece in every region. D2 is (a): GLOB.FLX becomes a sixth artifact.
  - The other six are as recommended: darkness beyond cave walls, stars
    beyond the cloud sea, a rock shore for the Vale, reeds by water, the
    keep replaced, lobes only if needed.
- **Shores corrected** (`cc50402`): Douglas said "map13 shores look wrong
  ... wrong tiles". Every shore is now the 1994 cliff shore from screens
  02/09/15/16. Retail river-shore globs 1537-1554 are excluded, and
  `lv_dressing` refuses them on Maps 10 and 13.
- **Slice 0 merged** (`4d3d514`): `lv_dressing.py`, `lv_globs.py`,
  `test_dressing.py`, `dressing_pins/`, and GLOB.FLX as the sixth artifact
  (`aabc1ad3`, 3,072 retail slots plus 60 LV); FIXED unchanged, estate
  58/58. Douglas's CLAUDE.md line 77 still says "five artifacts".
- **Merged and in the viewer:** every map except 10. That is Maps 39, 8, 9,
  18, 13, 11 (two runs) and 17 (two runs plus the edge fix, `af6fd649`), and
  shared slices 0.1 (`be6aea39`) and 0.2 (`9a201022`). The estate passed
  58/58 after every merge.
  - 0.1 added the forest copses, the moat bank, decorative shapes 898-904,
    the lv_globs import fix, and VQ-091.
  - 0.2 made density targets land-only (water and stars are backdrop) and
    added stars beyond the cloud sea, `walkable_set_piece`, the wall rock
    skin, crest placement, loose-floor transitions, the `exact_reach`
    FLG_INVISIBLE fix (0 route verdicts changed), and shapes 905-928.
- **Engine FLEX cap raised** (Douglas, 2026-11-10), fork `ede55adf`
  (`flex_file.cpp`: 4095 -> 65536 entries), with the patch regenerated
  (`4cb35453`).
  - Stock ScummVM rejects a FLEX over 4,095 entries, and a rejected
    GLOB.FLX loads empty, so every prefab silently vanishes.
  - GLOB.FLX is now 4,239 entries; 144 Map 17 eggs sit on slots 4096-4238.
  - `test_dressing` asserts the cap is at least 65,536 and that the built
    file fits.
  - Verified in the console build: three Map 17 stops land, there are no
    "Flex invalid" lines, and pixels match the approved captures to 0.1%.
  - The console binary needs `make -C scummvm-lv-console` after a fork
    commit; `integrate.sh` rebuilds only `scummvm-lv/`.
  - Douglas's CLAUDE.md still names fork tip `e48f8716`.
- **Merge-script bug fixed:** `merge.sh` once committed "estate green"
  after a failed build (`25716aff`, reverted). It now runs
  `set -o pipefail` and stops before committing.
- **Review rule:** look at every slice's captures against its direction
  sentence before merging. First runs of Maps 8, 9, 13 and 17 passed the
  numbers and were sent back for set pieces that were scatter, material
  sheets, tile rows or box rocks.
- **Map 10 merged** (`6ac733d5`), so all eight maps carry phase 4
  dressing. Main estate 58/58; viewer on FIXED `70f90c1f`.
  - 105 of 126 after-shots were not taken; the re-tour below covers them.
  - Builder speed fix `01c88c4d` (incremental `_refresh_appended`, cached
    `register_packed`): Map 10 549 s -> 302 s, identical output. Most of
    the rest is the `walkable_set_piece` route proof, kept.
- **Next (not started):**
  - an Astra re-tour of all maps against the direction, and a card page on
    the hub;
  - a verifier walk in ScummVM;
  - the single full quest replay that plan §8 requires at the end of phase 4.
- Merge with `/tmp/claude-1000/vq2/merge.sh NN wt/vq4-mNN` (it resolves the
  manifest per map and commits the regenerated one), then regenerate the
  viewer.
- **How Fable runs now:** `claude -p --model claude-fable-5-2
  --permission-mode bypassPermissions` (Claude Code CLI, subscription).
  The omp bridge refuses it as a subagent, and `omp -p` has no Anthropic
  key (`models.yml` is empty; the backup is `models.yml.bak-20261109`).

## 2026-11-02: visual-quality pass, phase 1 done; phase 2-3 designed

Phase 1 (16 backlog items on Maps 8-11, 17 and 18) is merged and
integrated: TYPEFLAG `ac0b3348`, U8SHAPES `aad6ed7b`, FIXED `89da4e16`,
estate 56/56. Map 8 added shapes 894/895, opaque cave backdrops.
- Before/after cards with Astra's grades:
  `https://devhost.invalid/a/lostvale-art/phase1.html`
  (`lv-art-review/phase1.py`). Fixed: 11; improved: 2 (Map 8);
  unchanged by decision: VQ-001, VQ-016; **regressed: VQ-003** (the Map 8
  first-seam doorway is now partly covered), which goes to Map 8's phase 2-3
  slice.
- In-game check (Codex in the verifier role, because Fable hit the API
  limit mid-run): `docs/playtest-2026-11-02-vq1-verify.md`.
  - PASS: Map 11, Map 17, Map 9.
  - PARTIAL: Map 8 (segmented walk), Map 10 (zombies blocked the pier),
    Map 18 (no exact-build fork plate).
  - "FAIL" V7 is the existing Map 17 `219 -> 875` knot that Douglas kept
    on 2026-10-24; its records are byte-identical to before phase 1.

Fable designed phases 2-3:
`docs/research/2026-11-01-visual-pass/phase23-design.md` (`8445022`).
It has a gate 0 (tooling and `test_visual_quality.py`, FIXED unchanged),
then one Codex slice per map, in the order 18, 9, 11, 10, 13, 17, 39, 8.
Douglas answered all eleven on 2026-11-03 (§6 table, `616d151`). Gate 0
merged as `ba34836`: `test_visual_quality.py` (86 s, pins = measured
debts, `--strict` for final acceptance), `quest_legs.py`, record budgets;
FIXED unchanged, estate 57/57. **Now:** eight Codex slices
(`wt/vq2-mNN`, worktrees `../lv-wt-vq2-mNN`, briefs and logs in
`/tmp/claude-1000/vq2/`), then merge in the order 18, 9, 11, 17, 13, 10,
39, 8 (§5) with integrate, Astra and a ScummVM verify.

## 2026-11-01: visual-quality pass, phase 0 done

The plan is `docs/research/2026-11-01-visual-quality-plan.md`. Fable
reviewed it on API credits and approved it with ten changes (§11). Phase 0
outputs are in `docs/research/2026-11-01-visual-pass/`:
- **Backlog:** 198 items, 39 high, tagged retail/LV, shot window and
  landing.
- **Astra's check of the high items:** 14 confirmed, 17 downgraded, 5 false
  positives, 3 unclear.
- **Audit tools:** `void_audit.py` and `avatar_visibility.py`, checked
  against real captures.
- **Retail calibration:** thresholds for towns and outdoors (black 7% or
  less on average) and for caves (47% or less); no walkable black on our
  routes.
- **Landing check:** all 370 tour stops recaptured; 356 landed. The Map 13
  "skull ring not drawn" item was a capture artifact.
- **`tour_capture.py`:** now waits 22 s, past the first-teleport Guardian
  cutscene. That cutscene is also the "ghost follower" seen in the tour
  frames.

How the agents run:
- Codex: `codex exec -m gpt-6.1-sol --sandbox danger-full-access`. The
  bwrap sandbox fails here.
- Astra: `codex exec -m gpt-6-astra -i …`.
- Fable: `omp -p --model anthropic/claude-fable-5-1`. It bills the API key
  through `~/.omp/agent/models.yml` (1Password); the credit expires
  2026-11-07.

## 2026-11-01: screenshot tour of every region

`https://devhost.invalid/a/lostvale-art/tour.html` has 370 ScummVM
captures covering Maps 8 (LV parts), 9, 10, 11, 13, 17, 18 and 39's lane.
Each was reviewed for visual problems: 111 high, 399 medium, 288 low. The
review data is in `~/projects/lv-art-review/tour/<area>/review.json`
and the page builder is `tour.py`. The capture tool is
`tools/playtest-linux/tour_capture.py`. `session.sh` now stops only its own
display's game, so parallel sessions are safe.

## 2026-10-30..31: art review round 2 (phase E)

Douglas accepted round-1 cards 1, 5 and 8, and sent back 2, 3, 4, 6 and 7.
All five are done, merged, integrated and verified in ScummVM
(`docs/playtest-2026-10-30-phaseE-verify.md`):
- screen13's cloud now floats over the tree: 97.02.
- screen07 is at 96.00.
- The four pillars are in the 1994 style.
- The elder has the short cane and a SE talk gesture.
- The children hold their spears.

The round-2 page is
`https://devhost.invalid/a/lostvale-art/phaseE.html`, built by
`~/projects/lv-art-review/phaseE.py`. `session.sh stop` no
longer kills other sessions' console feeds.

## 2026-10-30: zombie, potions, summit harpies

All three are Douglas's decisions, verified in ScummVM and recorded in
`TODO.md`:
- **Water Zombie weakened** (`docs/playtest-2026-10-30-zombie-balance.md`):
  hp 25-35, damage 3-7, dex 10-12, armour 8. Armed, the Avatar wins 10 of
  10.
- **Map 10 potions**: protection and invisibility are now one-time; health,
  mana and the Tiny Tars still restock
  (`docs/playtest-2026-10-30-potions-summit.md`).
- **Map 13 summit harpies** hatch one at a time. The neck is not widened,
  because that costs screen01 up to 4.6 points, so a body can still block
  it by decision.
- **Art review pages** are on the tailnet:
  `https://devhost.invalid/a/lostvale-art/simple.html` (the decision
  cards) and `index.html` (the detail). Both are built by
  `~/projects/lv-art-review/{build,simple}.py`.

## 2026-10-25..26: phase D of the 1994 shots

Douglas chose: draw every missing actor, cut and redraw the screen12/13
pieces, and accept the black past Map 13's north edge. Done and merged
(`wt/static`, `wt/actors`):
- **Static art:** 882-886 and the 1994 Pillar of Fire (865 f2).
- **Actors:** 888 Zealan elder (Atli), 889/890 spear children (npc
  104/111), and 872 restyled to the 1994 Water Zombie.
- **In-engine scores:** screen12 85.9 → 96.4, screen13 76.0 → 94.0,
  screen07 86.1 → 89.9. No shot regressed
  (`docs/playtest-2026-10-25-phaseD-verify.md`,
  `docs/research/2026-10-16-screenshot-reconstruction/ingame/SCORES-2026-10-25.md`).
- **Merge slip, fixed:** my merge lost npc 111's pin, and the child
  vanished from Map 10. Restored in FIXED `9e666935` and re-checked in
  engine (`docs/playtest-2026-10-25-npc111-check.md`).
  test_schedule_destinations now guards npcNum 100-116.
- **Contact sheets for sign-off:**
  `docs/research/2026-10-16-screenshot-reconstruction/phaseD-{static,actors}-contact.png`.

## 2026-10-24: the Map 13 lane harpies hatch one at a time

Douglas chose this option after the armed test (5 of 10 wins against the
pair). A new trigger at y 6143 hatches the first harpie on the level z-76
stretch. The y-4479 trigger now hatches the second, alone. FIXED is
`1a9ce209`. Verified in ScummVM in
`docs/playtest-2026-10-24-harpies-one-at-a-time.md`: armed 6 of 8 wins,
each trigger hatches exactly one harpie, and nothing is alive between
the two fights. Details are in `TODO.md`.

Later the same day (FIXED `ef2ed0f4`), three more replay findings were
settled. All are verified in ScummVM in
`docs/playtest-2026-10-24-fixes-211-rats-corpses.md`, and GPT-6.1 Sol
reviewed them with no findings:
- **Trigger 211 on Map 10** now has range 0x33, so walking off the stair
  foot below the pad 210 shelf no longer bounces the player to Map 18.
- **The Map 11 rats** moved off the south-half entrance into the
  north-east bay.
- **Harpie bodies** stay solid, as retail monster bodies do.
  `test_harpie_corpses.py` proves one body never closes the lanes.

Douglas kept the Map 17 `219 -> 875` knot as it is.

## The single-build replay (2026-10-17..18)

**The single-build replay on the current build is done.** It ran in six
legs on one pinned game copy, from a fresh prologue to godsFree,
endgameStarted and Ezrekal's reagent bag. Every move was input, and the
`Cheat` count was 0.

- **Build.** EUSECODE `2e3b71c2`, FIXED `8db11ee3` (before the harpie
  change), U8SHAPES `efb16af1`,
  TYPEFLAG `d26d1531`, ANIM `696dbeb9`. The hashes were re-checked at the
  start and end of each leg.
- **Reports.** `docs/playtest-2026-10-17-replay-leg1..6.md`, with plates.
  Each leg's Resume section names its save.
- **Final save.** `~/lv-checkpoints/replay1017-s18c-m10-reagent-bag-hp30.sav`.
- **Deaths.** 8 deaths and 9 reloads, all on legs 1, 2 and 5. The Map 13
  lane harpie pair caused 2 of the deaths.
- **No blockers.** The findings are filed in `TODO.md` under "Found
  2026-10-17/18".
- **Harness.** The replay driver is in `/tmp/claude-1000/replay1017/py/`
  (`lv.py`, `rnav.py`, `follow.py`, `leg3_helpers.py`), along with the
  pinned game copy. It is scratch: copy it out before /tmp is cleared if
  another replay is planned. Leg 1's report documents it.

The session before this one (2026-10-12..17) put all 19 of the 1994
screenshots into the build: `docs/research/2026-10-16-screenshot-reconstruction.md`
and `docs/playtest-2026-10-17-vignettes-verify{,2,3,4}.md`.

## Next action

- **Douglas: pick what to fix from the screenshot tour** (`tour.html`).
- Earlier items:
  - The harpies are weakened (2026-10-31; armed 14/14). The summit
    run-past death stays by decision.
  - The art track is signed off (round 2: 1b, 2-5 a).
  - The Map 11 talisman duplicates (phaseE-verify F4) were a debug-teleport
    artifact, not a defect (`docs/playtest-2026-10-31-talisman-reentry.md`).
  - The next work is the open items in `TODO.md`.

## Current state

- Branch **`main`**, nothing pushed. No ScummVM or Xvfb running. The
  worktrees `../lv-wt-static` and `../lv-wt-actors` are removed, and their
  branches are merged. Run `tools/integrate.sh` after every merge that
  moves an artifact (`.claude/skills/integrate/SKILL.md`).
- Artifacts (2026-10-30, phase E):

  | Artifact | Hash | Notes |
  |---|---|---|
  | EUSECODE | `b47c324c` | 1,529,089 bytes, md5-5000 `84615e29` |
  | FIXED | `fc92ee5f` | |
  | U8SHAPES | `2b274856` | |
  | TYPEFLAG | `e25d7224` | |
  | ANIM | `97ae5fc9` | |

  The estate is 54/54. The Compilation Report reads 57 compiled, 55 ok;
  the 2 failures are the allowlisted EALOGO and TJORVI. CLAUDE.md's "53
  files / 51 succeed" line is stale.
- Fork `scummvm-lv-console` (branch `lost-vale`), tip `e48f8716`,
  unchanged. The patch equals the fork diff. Whenever EUSECODE changes,
  refresh the console build's `detection_tables.h`: run
  `cp scummvm-lv/engines/ultima/detection_tables.h scummvm-lv-console/engines/ultima/`,
  then `make -C scummvm-lv-console -j14`.
- Uncommitted and not mine: `CLAUDE.md`, `.claude/settings.json`,
  `.claude/agents/`, `docs/art-gallery-2026-10-12.html` and `usage.pkl`.
  Keep them out of commits.

## Open questions

- The REA NE-support upstream PR stays held (`TODO.md` §7).
