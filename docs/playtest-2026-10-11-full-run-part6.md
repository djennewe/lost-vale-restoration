# Full 1→18 run, cheats off, part 6: steps 9 and 12-16 done, step 17 partway (temple open). NOT COMPLETED (2026-10-10/11)

**Build under test.** main `2475274`. Game copy `/tmp/claude-1000/vrun6/game`; sha256 matches `shared/build/ARTIFACTS.sha256`: EUSECODE `4103122a…` (log: `eusecode.flx … 1525545 bytes`), FIXED `332bdeb2…` (root and `STATIC/`), U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…`, ANIM `77e9705d…`.
- **Harness.** Xvfb `:96`, part 5's ini (320×200, no width/height keys) plus `music_driver=null`. Driver `vrun6/py/v6.py` + `nav6.py` (renamed: a module called `nav` is shadowed by `tools/playtest-linux/nav.py` on reload).
- **Start.** `~/lv-checkpoints/run1010-s12b-m10-root-inside-ezrekal-stockade.sav` (md5 `560da6fb`).
- **Cheats: 0** (`Cheat` appears 0 times in `vrun6/lv_run.log`). Console use: `objectInfo`, `findShape`, `getGlobal`, `debugflag_enable Object`, `saveGame` only. No loads, no deaths.

## Outcome

- **Furthest step completed: 16.** Step 17 is partway: **templeOpen (1042) = 1**, but the Shield is not yet on the altar (godsFree 1038 = 0).
- **Step 9 (deferred from part 5) is done:** endOfPlantScene 1050 = 1.

## Verdicts

| Step / leg | Verdict | Evidence |
|---|---|---|
| 12: reach Ezrekal in the garden | **PASS** | North fence gap (x≈12880-12940) → inside → south fallen panel (x≈13132-13196) → garden. Strike at (12847,13553) logged `event 1 @ 0474:034A` |
| 12: root hand-over | **PASS** | Menu "I have found the root. / Can you help me? / bye" → "Ah, good that is. Take it I will and brew the tea I will." (`s12-01`). givenRoot 1063 = 1, justGotRoot 1064 = 1, weight 30 → 20. Next menu offered "Is Tyorvi's elixir ready yet?" |
| 12: brewing wait | **PASS** | Walk-away to (14583,14023): log `Item: 116 … event 16 @ 0474:0264`; 1064 → 0 |
| 12: elixir | **PASS** | "Have you made the elixir?" → "Yes, I have. Take it to him now you can." (`s12-02`). 1827 = 1, 1062 = 1, weight 20 → 30 |
| 12: Key from Tyorvi | **PASS (drunk path, second talk)** | Talk 1 (drunk): something from Ezrekal → It is an elixar. → It is a potion. → It will heal your dreams. → **Just try it, please.** → refusal + exit (by design, `LP:TYORVI.UNK:2256-2268`, sets iAmDrunk 1828 = 1). Talk 2: same chain → **Shut up and drink it!** → "All right, all right! … Try it I will." → (≈20 s+ silent pause, finding 1) → menu "May I have the Key to the Clouds? / bye" (`s12-03`) → Key. findShape 82: item 10999 **q 170**, `f: 0xc` (contained); givenTea 1061 = 1; weight 30 (vial −10, key +10) |
| 9: Thordis's Mark speech at home | **PASS** | Thordis at (4415,7423) → (4595,7603); double-click logged `event 1 @ 046A:0ECD`. Barks "Oh my, terrible this is. Send you here Atli did?" … "But give you the Zealan Mark I will…" … "Well, speak to Ezrekal you can…" (`s09-01`). endOfPlantScene 1050 = 1, plantScene 1049 = 0 |
| 13: Map 10 → Map 13 | **PASS** | Terrace via the x≈7250 lane; read Map 13 (4096,11880,0) (`s13-01`) |
| 13: EggCloudCliffs with the q170 Key | **PASS** | Bark "The ancient handholds carved into the cliff face glow faintly as I approach. This must be the path." (`s13-02`). climbedCliffs 1031 = 1 and attemptedCliffs 1039 = 1 (1031 read 0 until the 210-tick waits ran unpaused) |
| 13: the climb | **PASS after 6 falls** (finding 2) | Summit → trigger 209 → **Map 17 (5376,11136,0)** (`s13-03`). No damage from any fall (hp 30 throughout); no torax attacked |
| 13: Shield halves | **PASS** | Drag 1: `Dragging item 30508` → `Dropped item in backpack`, weight 30 → 70. Drag 2: `Dragging item 7901` → `Dropped item in backpack`, 70 → 110. Both `f: 0xc`. The skeleton no longer overlaps the second half (guide is out of date) |
| 13: return to the Vale | **PASS** | Map 17 y 11520 → Map 13 (3948,660,128) → descent → trigger 206 → **Map 10 (7168,23296,8)** |
| 14-15: Sacred Circle ceremony | **PASS** | Route south of the lake (y≈21500) to (20364,17532), walk N. Elders' quarrel (`cer1` frames) → **Let's be reasonable!** (`s15-01`) → **Yes, Priestess.** → halves fuse, shades (`s15-00` grid) → **Please, High Priestess.** → "I feel better... But I'm still so weak!" (`s15-02`). shieldFixed 1033 = 1, avatarPoisoned 1028 = 0, inShadeScene 1106 → 0 after the scene. Shape 828 q83 item 26343 in the pack (`f: 0xc`), weight 110 → 60 |
| 16: Hrodny | **PASS** | She was at Tyorvi's stash area (21859,8345). Talk 1: "What is your name?" → hrodnyMet 1116 = 1 → bye. Talk 2 menu: **I have been healed! / The Shield of the Ancients is restored! / bye** → I have been healed! → **How can I open the temple?** → spokeTemple 1782 = 1. Bag 637 (item 19051) appeared at (19588,23284,0) holding a q20 key |
| 16: chest | **PASS (with the pre-placed spare key)** | Took the spare q20 key at (22016,6144) (item 25460, `Dropped item in backpack`, +10) rather than the 15,000-unit round trip to the bag. Key double-click `event 1 @ 0052:04BB`, then click on the chest: chest became **shape 78** q20 (item 26034). Double-click: `event 1 @ 004E:00A9` and the TRAP `event 1 @ 02F4:0080`, no damage. Three 859 potions dragged to the pack: weight 70 → 100 |
| 17: Map 10 → Map 18 | **PASS** | Processional → trigger 211 → Map 18 (3276,1996,0) (`s17-01`). The route crossed EggEndgame's box (18388,22930) with godsFree 0; no scene. [INFERENCE: if the egg is consumed on a no-op hatch it re-arms on the next map entry] |
| 17: crack hint | **PASS** | crackHintGiven 1829 = 1 on arrival at (2817,5988); barks not captured |
| 17: crack with Tiny Tar | **PASS on the second potion** (harness, see anomalies) | Potion 1 (item 11499, `event 1 @ 04E5:00A9`): 13 S bursts at mouse offset 60-80 px moved y 6088 → 6108 only, then full size again. Potion 2 (item 11498): 12 bursts of 0.5 s at offset 200 → (2849,6532,0), **templeOpen 1042 = 1** (`s17-03`) |
| 17: altar / AOSCENE | **NOT DEMONSTRATED** (budget) | Last position (3307,8207,8), stalled south of the dais (`s17-04`). godsFree 1038 = 0 |
| 18 | **NOT DEMONSTRATED** (budget) | — |
| Log hygiene (`vrun6/lv_run.log`) | **PARTIAL** | 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`. 2 × `Unhandled intrinsic 254 'isGameRunning()'`; 8 × `Cycle in paint dependency graph 35 -> 539 -> ... -> 35` (539 = shield half; Map 17 or the circle) — not traced |

## Findings

1. **Tyorvi's drunk "Shut up and drink it!" leaves the player in a long silent conversation.** After "All right, all right! Have to shout you do not! Try it I will." the screen shows no text and no menu for about 20 s or more (`F1-tyorvi-silent-wait-start.png`; the menu appeared only after several further frames, `F1-tyorvi-key-menu-after-wait.png`). The case does `wait (1000)` before its second bark (`lv-patched/TYORVI.UNK:2294-2318`; the sober case has the same `wait (1000)` at `:2280`). My console reads paused the world inside the wait, so the exact wall time is not measured. A player sees a frozen conversation and may click away; the menu still came back here. Also: the follow-up bark "Hmmm, taste too bad…" was not seen. Low-medium severity.
2. **The cloud-cliff climb drops a walking Avatar to z 0 at several points, and an aim on the planner's own lattice edge falls.** 21 `DROP` lines in `vrun6/trace.txt`; the repeat spots are (4005-4081, 7176-7679, z 24-40) going north, and the bend at (4295,5388,z 66) / (4396,5474,z 76). `exact_reach` (erosion 0) lists the climb as standable for Avatar x 4004..4124 at y 6800-8200 and finds **no route at erosion 1-3**, so the column is barely one body wide; points at x≈4005-4009 sit on the lattice edge yet fall in-engine. Centring on x≈4064 and shortening bursts at bends got through. Falls do no damage (hp 30 every time) and land on a z-0 floor under the whole climb, so this costs time, not the game.
3. **Hrodny's q20 key is not needed:** the pre-placed spare at (22016,6144,0) opens the chest. A player who finds it skips "How can I open the temple?". Not a blocker; noted as a design question (`MP:build_map_10.py` places it deliberately per the route guide).
4. **First mouse input after a console close is often swallowed** (harness, but it shapes every movement figure above): alternate bursts produced zero displacement throughout. A priming left-click did not fully cure it.
5. **The checkpoint's stockade start wedges** at (12779,12155) in the north fence: every direction except NW refused (the save carries its own fixed items). Freed by a 0.8 s NW walk.
6. **Hrodny wanders as far as Tyorvi's stash** (talked at (21859,8345)), and the direct path from the chest's west side wedges at (21049,8857) on the chest corner; the route south of the chest (y≈8903) works.
7. Route guide drift: the BONES3 skeleton no longer covers the second shield half; Tyorvi's drunk path did not offer "Are you OK, Tyorvi?" — iAmDrunk was set instead by the refused "Just try it, please." talk.

## Harness anomalies

- `importlib.reload(nav)` picked up `tools/playtest-linux/nav.py` (the module's own `sys.path[:0]` insert); renamed the driver copy to `nav6.py`.
- Tiny Tar pushes with a mouse offset of 60-80 px did not move the shrunken Avatar; 200 px did.
- `saveGame` at the end (south of the dais) failed silently — the slot mtime did not move — so the last banked state is `s17b`.

## Checkpoints (all new)

| Name | md5 | State |
|---|---|---|
| `run1010-s12c-m10-elixir-in-pack.sav` | `ce70130f…` | Garden, vial in pack, 1827/1062 = 1 |
| `run1010-s12d-m10-cliff-key-q170.sav` | `955ffaaa…` | Tyorvi's stash, Key q170, givenTea 1 |
| `run1010-s09-m10-thordis-mark-speech-done.sav` | `97c62780…` | Hoskuld, 1050 = 1 |
| `run1010-s13a-m13-cliffs-climbed-flag.sav` | `0ce5c7b3…` | Map 13 foot, climbedCliffs 1 |
| `run1010-s13c-m17-cloud-city-arrival.sav` | `00a45893…` | Map 17 pad 209 |
| `run1010-s13d-m17-both-shield-halves.sav` | `1b132485…` | Memorial Hall, both halves |
| `run1010-s13e-m10-back-with-halves.sav` | `1fe8ff03…` | Map 10 pad 206, halves |
| `run1010-s15-m10-shield-restored-cured.sav` | `9f6a00b4…` | Sacred Circle, shieldFixed 1, cured, Shield 828 in pack |
| `run1010-s16a-m10-hrodny-spoke-temple.sav` | `c98ae952…` | Near the stash, 1116/1782 = 1 |
| `run1010-s16b-m10-three-tiny-tar.sav` | `97b3bcc3…` | Chest open, 3 Tiny Tar, weight 100 |
| `run1010-s17a-m18-arrival.sav` | `a8666c8c…` | Map 18 (3276,1996,0) |
| **`run1010-s17b-m18-temple-open.sav`** | `3b7c71c4…` | Map 18 (2849,6532,0) inside the breach, templeOpen 1, Shield 828 q83 + 1 Tiny Tar in pack. **Resume point** |

## Resume here

1. Load `run1010-s17b-…`, `debugflag_enable Object`, one look-click.
2. Sanctum: (3263,6300) → (3263,7600) → (3460,7730) → (3460,8600) → walk W into (3240,8600) for EggAOCeremony (route guide step 17). Avoid the candelabrum at (3248,7928) and the dais rim at (3307,8207) where this run stalled. Leave the console closed for ~60 s.
3. Step 18: out through the breach and gap x≈3080, north onto trigger 210, 1.4 s north into EggEndgame, then Ezrekal "I have freed your gods!".

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-full-run-part6/` (17 plates).
- **Wrote** the 12 checkpoints above in `~/lv-checkpoints/`.
- **Scratch** `/tmp/claude-1000/vrun6/` (game copy, saves, `sp/`, `py/`, `lv_run.log`, `trace.txt`, `er_*.pkl`).
- **Stopped** my ScummVM (pid 3473089) and Xvfb `:96` (pid 3473084).
- **Not touched:** source, builders, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`.
