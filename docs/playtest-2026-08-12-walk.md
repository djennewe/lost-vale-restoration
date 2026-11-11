# Checkpoint walk, 2026-08-12 — cp2 palace → Map 8 plateau save: DONE

Agent-driven (Douglas is away from kaga for several days and green-lit the
harness doing his ~2-minute walk plus an exit-test rehearsal). Organic
navigation only: right-button walking/running, doors opened by double-click,
zero `setGlobal`, zero debug teleports. The debugger was used for reads
(position, hp, `lbDone`), `loadGame` recovery after deaths, and nothing else.

Screenshots: `docs/playtest-2026-08-12-walk/`. Six Avatar deaths on the way;
every one recovered by reloading a checkpoint and every cause identified.
What took Douglas ~2 minutes took the harness ~3 hours — the difference is
exactly the difference between eyes-plus-hands and a position probe.

## Verdicts

- **Load cp2, verify `lbDone`=0** — PASS
- **Map 40 palace leg** — PASS (route.py BFS waypoints + nav.py driving;
  one dynamic door — shape 68, `uc: DOOR_NS`, item 551 at (12287,6975) —
  identified via `debugflag_enable Object` and opened by double-click)
- **Map 40 → Map 7 teleporter at (13054,2322)** — PASS, walked in
- **Map 7 river crossing** — PASS via the ford lane at x≈12551 (z=8 the
  whole way; the z=48 shape-412 causeway is scenery with no mounting ramp)
- **Map 7 → Map 8 teleporter at (9498,19702)** — PASS after an aggro-kite
  around two seekers stationed at the tunnel mouth
- **Arrival protocol** — PASS: stopped at (31295,19135,0), clear of Mythran
  (~1503,1791) and the LORDBRIT backstop egg (2200,2230)
- **`lbDone` (0x6A6) = 0 on the plateau** — PASS
- **Plateau base save** — DONE: quicksave slot 1 (04:36), archived as
  `~/lv-checkpoints/cp3-plateau.sav`, Avatar hp 30/30

The exit test (steps 1-18 continuous, no debugger) now runs from
`cp3-plateau.sav`.

## Artifact hashes at save time (match `ARTIFACTS.sha256` exactly)

```
6360e6b3cbdd87a9…  TYPEFLAG.DAT
762ca62d473cadc3…  U8SHAPES.FLX
1a41dda192575a25…  EUSECODE.FLX     (the pre-2026-08-12-fixes canonical build)
5f1180d8c96ffa49…  FIXED.DAT
```

Note: the day's compiler fixes (multi-value case dispatch, PT_*/day-period
pins) are committed in source but deliberately NOT yet in the built
artifacts — the rehearsal runs on the canonical build first, and the
rebuild lands afterwards via the /artifact-rehash cascade.

## The six deaths, and what each taught

| # | Where | Cause | Lesson banked |
|---|---|---|---|
| 1 | Map 7 (15095,24127) | nav kept driving after the map changed; blind 2,100-unit drag into the wilds | nav.py now stops the route on map change |
| 2 | Map 7 (10239,24151) | walked into the river at x=10128 — the walk grid reads glob water plates as floor | cross at the ford (x≈12551); route.py carries the water-blindness caveat |
| 3 | Map 7 (10051,23227) | seekers (first contact, unrecognized) | hp now printed on every nav step |
| 4 | Map 7 (10851,23339) | seekers again, walking gait too slow to escape | run gait: 240px offset (nav mag 130→240), speed ≈570 units/s measured |
| 5 | Map 7 (9995,20007) | seekers at the tunnel mouth | F1 quicksave checkpoints — replay cost dropped from ~20 min to ~1 min |
| 6 | Map 7 (9823,19615) | seekers, same station | screenshot caught them (21-before-tunnel.png); aggro-kite east, loop north-west, sprint the dog-leg |

Diagnosis notes for the record: the deaths were silent in the log — no
event 5/6 (hit/gotHit) fired, which initially pointed away from combat.
The event-18 spam that dominated the log is `Avatar::justMoved` — the
Endure/Armor spell-follower — firing on every step, harmless here. The
storm-suppression chain in `Avatar::schedule` correctly leaves storms
active on map 7 (it is absent from the 19-map retail suppression list),
but storms were not the killer; the seekers were, confirmed by sight.

## Route knowledge for the rehearsal (steps 2-3 retrace this)

- **Map 40 palace**: exit the checkered room by its NE doorway
  (~12100,6900 → walk screen (+90,-25) then (+90,+45)), east through the
  DOOR_NS at (12287,6975) — it resets closed on every reload — then the
  x≈13040 corridor north to the teleporter at (13054,2322).
- **Map 7**: land (15071,~26100). West along y≈26100 (a fenced field with
  a gate pocket sits north of y≈25150 — stay south of it), ford the river
  at x≈12551 (grass-to-grass at z=8), west along y≈23500, then the
  double-burst: west (-240,-106) 3.5s + north (240,-136) 5s lands at
  (10855,20375) deterministically. Pass approach: (-240,-199) 2s +
  (-110,-60) 1s. The tunnel dog-leg wants south-to-y≈19740-then-west;
  the seekers hold the mouth — kite or time them.
- **Speeds**: run gait ≈570 units/s. Total map 7 exposure ≈20s when it
  goes clean.

## Harness additions this session

- `tools/playtest-linux/route.py` (new): BFS corner waypoints over the
  built FIXED.DAT via WalkGrid. Guidance, not proof: water globs read as
  floor, dynamic doors are invisible.
- `nav.py`: map-change stop, hp on every step line, one position-read
  retry, flushed output, run gait, retuned step timing.
- Idioms that earned their keep: `debugflag_enable Object` + single click
  = ground-truth identification of any blocker; F1 = quicksave (slot 1 —
  the same slot `loadGame 1` reads, so it doubles as the resume point);
  F5 opens the save *dialog* — don't use it headless.
- The game-over diary cannot be closed while dead (`MenuGump` refuses) —
  a stuck diary means check hp, not focus.

## Disk changes

- `~/.local/share/scummvm/saves/ultima8.001` — now the plateau base
  (quicksave 04:36)
- `~/lv-checkpoints/`: `cp2b-map7-landing.sav`, `cp2c-map7-north-bank.sav`,
  `cp2d-pass-approach.sav`, `cp3-plateau.sav` (new); `cp2-palace.sav`
  untouched; `backup-slot1-20260811.sav` from before the first load
- No tracked repo file touched by the game; all four artifacts still match
  `ARTIFACTS.sha256`

## Rehearsal opening (same session): the plateau ascent is the first wall

From cp3, step 1 requires crossing map 8 to the LORDBRIT backstop near
Mythran (~2200,2230) — and `route.py` reports **NO PATH** from the arrival
shelf at either body width. Flood analysis: the shelf is a closed pocket
(x 29440-32256, y 18688-21504) whose only frontier toward Mythran is the
northwest corner at (29824,18688) — a cliff notch under a blue marker
(screenshots 25-30). The notch triggers U8's free-climb animation but the
Avatar slides back; standing jump-grabs (SPACE = fake both-button-click)
and mid-run jumps don't take either. **The canonical plateau ascent route
is unresearched** — next session: consult the U8 walkthrough sources in
TODO's Key Sources (Dino's guide) for the retail climb path, then continue.
The rehearsal is otherwise staged: cp3 loads clean, hp 30, lbDone 0.

**Route research (Dino's guide, wplateau.php + walkthrough search):** the
map 7→8 transition IS the retail "cave from Herdsman's Valley" — the shelf
pocket is the cave's first chamber. The canonical route: climb the higher
ground (CLIMB = both mouse buttons together while facing the ledge — not
SPACE alone), stepping stones over DEADLY water, evade the electric gateway
via the higher ground, the lever puzzle ("pull every lever that does not
have bones in front of it", then return and skip the first to open the
gate), south exit, dirt road to Mythran's house. Sources:
gigi.nullneuron.net/ultima/u8/wplateau.php and the walkthroughs indexed at
ultimacodex.com/archive/ultima8/u8walkfa.html.

**Correction after aimed-chord attempts (screenshots 31-34):** the notch
holds a climb state but never crests — and the walkthrough sequence says
the route from the cave entrance goes "west and south until you get to some
water", i.e. the STEPPING STONES come first, at the pocket's south/west
edge where the flood stops at SEA cells. The notch is likely not the route
at all. Next: scan the pocket's south/west frontier for stepping-stone
items over water, then hop them with cursor-aimed both-button jumps (the
chord jumps TOWARD the cursor — aim each stone).

**Stepping stones CROSSED (same session, screenshots 39-44).** The corrected
route held: lower chamber via the western descent (30387,19659 →
30311,20343), bank at (30239,20431), then cursor-aimed both-button chord
jumps stone to stone — the chord jumps TOWARD the cursor, so each hop is
"point at the stone, chord". Two hops + a bank hop landed at (29845,21361,8)
on the WEST BANK, with the walkthrough's trapped-chest landmark in frame
(43-hop2.png). The notch at (29824,18688) is a red herring AND a softlock
pocket — entering its climb wedges the Avatar permanently (walk/jump/back-
jump all no-ops; loadGame is the only exit). Checkpoints:
cp3b-cave-bank.sav (before the water), cp3c-west-bank.sav (after).
Next: follow the west bank south to the climb, evade the electric gateway
via the higher ground, then the lever puzzle.

**The pool crossing is precision-gated (deaths 8-12, screenshots 45-57).**
Facts established: chord-jumps land SHORT of the cursor at range — hops only
succeed stone-to-adjacent-stone from the water's edge; the visible stones
are only partly in FIXED.DAT (projection math against the fixed list
mis-predicts — some stones are dynamic); the guide arrow advances to the
next stone after each successful hop; blind repeat-hops at a fixed screen
point die when the camera scrolls; and the death-diary blocks the debugger
chord unpredictably (attach can take 5+ tries — queue the loadGame FIRST,
then chord until "Done"). Death recovery is cheap (~30s) via the west-bank
quicksave. NEXT: calibrate world→screen scale from one standing frame with
a known-coordinate stone in view, then hop by projected aim, one hop per
action, stepping to the water's edge before each.

**Tick close-out:** deaths at the pool now 6 (walk total 13). Established
this tick: the chord refuses to launch from the bank-interior stance (only
launches near the water's edge); the blue arrows are teleport-pad markers,
NOT route guides (following one walked the Avatar into water); and the
west-bank save already IS across the first water — the remaining gap is the
two-stone line at x≈29823 (y 21599, 22047) heading south. NEXT PROTOCOL:
identification-first aiming — `debugflag_enable Object`, single LEFT click
on a candidate stone pixel, read the item + world coords from the log,
and only chord at pixels confirmed as shape-497 stones. No more blind aims.

## Session close-out (2026-08-12, ~07:50)

**The real stepping stones are shape 780, usecode class `STANSTON`** —
probe-clicks identified them positively (the 497s were decoys). Ten-stone
chain mapped from FIXED.DAT, running southeast from (29983,21311) to
(30591,22367); first hop is 148 units from the west-bank save. The
remaining blocker is pure jump aim: the both-button chord lands short
unpredictably, and 14 total deaths (6 at this pool) came down to tens of
pixels. Parked ALIVE at the west-bank save (slot 1 = cp3c).

**Plan for the next session** — build `tools/playtest-linux/hop.py`:
spiral-probe pixels until the Object-log click resolves to the TARGET
stone's item id, chord at that exact pixel, verify landing via objectInfo,
retry-or-reload on miss. Auto-aimed hops make the chain mechanical. Then:
lever puzzle ("pull every lever without bones in front"), south exit, dirt
road, Mythran — quest steps 1-2.

State inventory for pickup: saves cp2/cp2b/cp2c/cp2d/cp3/cp3b/cp3c in
~/lv-checkpoints/ (slot 1 = west bank); session live on :77 (console
build); artifacts untouched, still canonical; compiler fixes await their
post-rehearsal rebuild.
