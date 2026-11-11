# Playtest 2026-10-11 (2): LV monster eggs, waves, the hub axe and the Harpie stats

This is the verifier pass on main `e5a36dd` (9e8ea8a + e5a36dd, fork `e48f8716`).

**Setup**
- Display and window: Xvfb :92, ScummVM at 320x200 ×2, frameLimit on.
- Binary: a pinned copy at `/tmp/claude-1000/vmon2/bin/scummvm`, sha256 `21f07b14…`, identical to `scummvm-lv/scummvm`. It was built 20:33, after the fork commit at 20:31.
- Game data: an isolated copy of `shared/u8-lv-patched` at `/tmp/claude-1000/vmon2/game`.
- Hashes, all equal to `ARTIFACTS.sha256`: EUSECODE `f0a9e709`, FIXED `9552dee0` (both copies), U8SHAPES `e0af51ea`, TYPEFLAG `7c1d8454`, ANIM `696dbeb9`.
- Fork patch: the tracked patch equals the fork diff (`diff -q` was silent).

**Base save:** `~/lv-checkpoints/replay1011-s07-m10-ragnar-told-stone.sav`, used read-only. I reloaded it twice, once after each Avatar death or drowning. Every map I tested was entered from a different map, so its fixed items were freshly loaded. `findShape 500` and `findShape 73` matched the shipped egg table every time.

**Cheats and debug aids used:**
- **Positioning teleports** to a spot short of each trigger, followed by a walk in:
  - Map 9: arrival pad, and next to Galjeron's body.
  - Map 10: the shore south of the pier.
  - Map 11: entry hall, hub, earth corridor, air corridor, the water corridor's foot, and the water side of the fire doorway.
  - Map 13: the climb at (4031,4415,84).
  - Map 18: the court south of the arrival pad.
- **`Cheat::toggleInvincibility`** for the fights. With it on, the Avatar's hp stayed at 30, and some hits still log `Damage: N`.
- **`Cheat::items`**, three times by accident in the first session. That session was then reloaded away.
- **`MainActor::toggleCombat`**, `useInventory` and `useBackpack`.
- **Weapons were not cheated in.** Galjeron's sword (420, Map 9) and the hub axe (419) were both carried by dragging them from the floor onto the paperdoll.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| M1 | Map 10 Lake: waves 2/1/2, dry, drawn, attack, look, die to axe/sword, one-shot | **PARTIAL**: waves 1 and 2 PASS, including one-shot. The Avatar **drowned fighting wave 2 on the pier** (finding 2). Wave 3 was NOT DEMONSTRATED |
| M2 | Map 13: lane pair hatches and attacks; rest point heals, summit pair stays asleep; summit hatch; look; sword damages; hp 30-45 | **PARTIAL**: lane hatch, attack, sword damage and hp PASS. On the 2nd run only 1 of the 2 lane harpies hatched (finding 4). Rest point, summit and look: NOT DEMONSTRATED |
| M3 | Map 11: each doorway hatches its group out of the walk's way; axe visible and carryable; axe hurts a golem, sword does not | **PARTIAL**: all four doorways hatch, and the axe and sword checks PASS. **Monsters hatched off-screen arrive passive** (finding 1), and they **stack on re-entry** (finding 3) |
| M4 | Map 9 troll only at the lair mouth; Map 18 golem at the north doorway, stays in the east aisle | **PASS** |
| M5 | 0 "failed to set stats", 0 "Cycle in paint", no crash | **PASS** |
| L | Log hygiene | **PASS**, with notes |
| Fork | Hatched monsters no longer misdispatch | **PASS**: zombie objId 149 (formerly hijacked by MORDHAT 0x495) ran `event 0 @ 0368:0080` and barked "water zombie" |
| Patch | Tracked patch == fork diff | **PASS** |
| Estate | `run_all_tests.sh` / `build_artifacts.sh` | **NOT RUN**: the brief barred build/install scripts, and the request budget ran out |

## M1 Map 10 Lake: PARTIAL

**Wave 1: PASS.** I walked north from (13824,20800) onto the pier.
- `Item 25716 (shape 73) … event 7 @ 0481:0080` fired at (13824,20304,8).
- Two zombies hatched at z 8, on the pier, at (13760,19974) and (13881,20151). Their hp was 43 and 39, and their flags were 0x800 (combat).
- The 2 group-1 eggs disappeared from `findShape 500`; the 3 later-wave eggs remained.
- **They attacked unprovoked:** `Actor 1 received hit from 125 (dmg=…,type=1)` while the Avatar was out of combat mode.
- **Look** on 124 ran `event 0 @ 0368:0080` and barked "water zombie".
- **They die to the axe:** hits of 5-11 (`type=6`), both at hp 0 with flags 0x1000.
- The zombies chased him off the pier onto the shore at z 0. That ground is dry, so it is not a problem.
- Plates: `M1-wave1-0/1`, `M1-wave1-hatched-onpier`, `M1-look-water-zombie`, `M1-wave1-killed-axe`.

**One-shot: PASS** (negative control).
- He walked south to y 22470, and the wave-1 trigger logged `event 16 @ 0481:011D`.
- He walked back across the trigger, and `event 7 @ 0481:0080` fired again, but no new zombie appeared. `findShape 872` showed only the two corpses (`M1-oneshot-return-no-new`).

**Wave 2: PASS on the hatch.** It hatched at y 19514, giving 1 zombie (objId 149) at (13888,19049,8).

**Wave 2 fight: FAIL (finding 2).** The Avatar went into the lake mid-fight.

**Wave 3: NOT DEMONSTRATED.** The reload after the drowning cost the remaining budget. The sword-kills-zombie half of the claim was shown by the previous pass. I only showed the axe.

## M2 Map 13 harpies: PARTIAL

**Run 1** (no invincibility, unarmed, not in combat mode).
- The lane trigger `Item 10456 … event 7 @ 0481:0080` hatched 2 harpies:
  - 124: hp 39, at (4037,2688,104);
  - 125: hp 37, at (4076,3324,96).
- Both read `ac: 11, defense: 0, align 4, enemy 2`, which matches the new ini row.
- 125 attacked unprovoked (`dmg=6, Damage: 6`). The pair took a 30-hp Avatar who did not fight back to 5 hp, and then to death (finding 5).
- Plates: `M2-lane-0..3`.

**Run 2** (sword equipped, invincibility toggled):
- **Only one harpie hatched** (finding 4): 125, hp 42, near (3998,3246).
- **The sword damages it:** `Actor 125 received hit from 1 (dmg=12,type=2) Damage: 8`, then 7, 8, 6, 5 and 12, with a single "No damage" (a miss roll). Before this change every hit read "No damage".
- It died: frame 218, flags 0x1000 (`M2-sword-vs-harpie`).
- The Avatar dropped from 30 to 15 hp.

**Rest point: NOT DEMONSTRATED.** The walk from (3983,3799) to (4031,1663) did not move the Avatar. He healed 15 → 18 hp in 154 s where he stood. `HealProcess` heals 1 hp per 1800 frames whatever the place, so this says nothing about the rest point itself.

**Not reached:**
- The summit trigger, the summit pair, and the "none in rock" check at the summit.
- **Look:** my click hit a floor tile (shape 3), not the harpie.

## M3 Map 11: PARTIAL

**Hatch at each doorway: PASS.** In every case the Avatar walked in through the doorway.

| Doorway | Trigger fired | Hatched |
|---|---|---|
| Earth (5988,5444) | `Item 15460` | 4 golems at their egg spots (hp 154-168, `ac 18, defense 8a`) |
| Air (14528,5400) | `Item 16633` | 3 seekers (509) |
| Water (9728,14674) | `Item 8990` | 5 lizards (806) |
| Fire (5950,16640) | `Item 2632` | 5 daemons (96) |

Every monster stood at its egg's own coordinates, 1,300-3,400 units from the doorway (plates `M3-m11-*-doorway-hatched`). Their positions are the builder's, so "out of the shortest walk's way" rests on the test plus those coordinates.

**Axe: PASS.**
- **Visible:** it lies clear on the hub floor (`M3-m11-hub-axe`).
- **Look:** `event 0 @ 01A3:0080`.
- **Carryable:** dragged onto the paperdoll, it was equipped and the weight rose by 50 (`M3-m11-axe-equipped`).

**Sword vs golem: PASS** (negative control). All four sword hits read `received hit from 1 (dmg=12..20,type=2) No damage.` (`M3-m11-sword-no-damage-golem`).

**Axe vs golem: PASS.**
- Hits: `dmg=23,type=6 Damage: 5`, then `Damage: 3`, `Damage: 3`, plus one "No damage" (`M3-m11-axe-hits-golem`).
- The golem went from hp 174 to 163. At 3-5 a hit against 150-175 hp, killing one takes about 40 hits (finding 5).
- The golems hit for 17-25 (`type=4`).

## M4: PASS

**Map 9 troll.**
- **Negative control:** pad → sword → 230 units down the south line: no hatch, and `findShape 83` was empty (`M4-m9-south-line-no-troll`).
- **Lair mouth:** around the spire to (14328,13984): `Item 7115 … event 7 @ 0481:0080`, and the troll (83, hp 208) hatched at its egg. It closed in and hit for 15 and 17 (`M4-m9-troll-comes`).

**Map 18 golem.**
- **Hatch:** walking south from the court through the north doorway fired `Item 28954 … event 7` at (3072,2778). The golem (hp 164) hatched in the east aisle.
- **Tracked for 15 s:** it stayed within x 4260-4448, y 3772-4028 (`M4-m18-golem-after-15s`).
- **Negative control:** walking the nave to (3072,4402) drew no attack. The golem then left the fast area and was destroyed, which is retail FAST_ONLY behaviour (`M4-m18-nave-south`).

## M5 / L: PASS

The run log `/tmp/claude-1000/vmon2/lv_run.log` covers 3 loads and about 55 minutes of play:
- `failed to set stats`: 0
- `Cycle in paint`: 0
- No crash.

There were 50 WARNING lines:
- 35 × `ActorAnimProcess: ANIMLOCK set on actor N, skipping anim`, all from monsters in combat;
- 6 MIDI transitions;
- 4 `Invalid procid N in waitlist`;
- 1 `Item 3126 FLG_CONTAINED or FLG_EQUIPPED set but item has no _parent!`, from my own drag of the sword from the paperdoll to the pack;
- the rest are ScummVM GUI start-up noise.

## Findings outside the brief

**1. Monsters hatched outside the fast area arrive passive.**
- **Mechanism.** `MonsterEgg::hatch` calls `move()` and then `setActivity(1)`. An actor that lands outside the fast area keeps combat, but `CombatProcess::run` returns early while it is not FASTAREA. When the Avatar later comes near, `Item::enterFastArea` (`world/item.cpp:1913-1917`) runs `clearInCombat()` and resets the actor to `stand`.
- **Observed.**
  - Golems 127, 128, 131 and 132 read flags 0x800 until the Avatar approached, then 0x0. They stood beside him without attacking (`M3-m11-golem-passive`).
  - Lizard 137 hatched inside the fast area; it kept 0x800c08 and walked toward him.
- **Scope.** Emulating `updateFastArea` (320x200, camera at the trigger) puts **21 of the 33 LV eggs** outside the fast area at hatch time:
  - every Map 11 golem, seeker and daemon;
  - 4 of the 5 lizards;
  - Map 10 wilderness groups 4, 5 and 6. At 640x400, group 6 and one lizard fall inside.
- **Effect.** The "combat activity" change does not take effect for these: the Map 11 sections' monsters never attack unprovoked. A combat egg must stand within one screen of its trigger, or the trigger must sit closer to its eggs.
- **Confidence:** high (code, plus the flag transitions observed in the log).

**2. The Avatar drowned fighting a zombie on the pier.**
- **Setup.** In combat mode at (13738,19514,8), attacking wave-2 zombie 149 by double-click only (no movement input). His x was 21 units over the west lane edge (13695): the walk had drifted west.
- **What happened.** The log shows, in order:
  - `received hit from 149`, then `Item 8668 (shape 347) calling usecode event 6 @ 015B:0080` (CLRWATER);
  - `I_resetRef item=1`, then `Main actor leaving fast area`, then `Actor 1 received hit from 0 (dmg=30,type=a8)`.
- **Result.** With invincibility on he ended up at (0,0,0), in stasis (`M1-wave2-avatar-drowned-limbo`). The zombie then drowned the same way (`I_resetRef item=149`, moved to (3315,4847)).
- **Assessment.** "Placed dry" holds at hatch, but a fight on the 256-wide pier with lethal water on both sides kills a player.
- **Confidence:** high that he drowned. The push into the water (hit recoil or attack step) is `[INFERENCE]`.

**3. Frame-0 groups stack on re-entry.**
- Monsters that never entered the fast area are never destroyed. After a second pass through the earth doorway, `findShape 214` listed **125 and 129 both at (3040,2048,0)**, and **126 and 130 both at (2688,2496,0)**.
- Each pass adds another four golems, overlapping in place, until the player goes near them.
- This applies to every non-one-shot group whose eggs hatch off-screen (finding 1).

**4. One lane harpie failed to hatch on run 2.**
- Run 1 hatched both lane harpies. Run 2, with a fresh map load and the same walk at x 4031, hatched only one (`findShape 873` showed only 125).
- The cause was not found. `canExistAt` refusing the egg spot is one candidate `[INFERENCE]`.

**5. Balance, measured against the step-7 Avatar (30 hp, no armour).**

| Monster | Damage to the Avatar | Its hp | Notes |
|---|---|---|---|
| Lane harpie | 5-10 a blow | 30-45 | The pair killed an Avatar who did not fight back |
| Troll | 15-17 a blow | 208 | Kills him in two blows |
| Golem | 17-25 a blow | 150-175 | The axe does 3-5 a hit, so about 40 hits each; the section has 4 golems (8 after a re-entry) |

**6. Map 18 golem.** The east-aisle golem is destroyed whenever the nave walk takes it off-screen, so the temple guardian is usually gone before the player sees it.

## Harness anomalies

- **First input lost.** The first walk after each console use was often lost, and some walks went in an unintended direction. One goto drifted the Avatar to the pier edge, the drift behind finding 2.
- **Interrupted console.** One eval timeout interrupted a console command mid-type, which leaked keys and opened the pause book. The Avatar also died there (run 1).
- **Combat attack.** It is a double left click. A single click does nothing in combat mode.
- **Sword reach.** It only lands when the Avatar's box sits within about 32 units of the target's along the facing direction.

## Disk changes

- This report.
- `docs/playtest-2026-10-11-monsters2/`: plates.
- Scratch only: `/tmp/claude-1000/vmon2/` (game copy, binary copy, engine-data copy, ini, saves, `lv_run.log`, `sp/` frames, `py/vm.py`).
- I reused the idle Xvfb :92 left by the earlier pass and did not kill it.
- Nothing in source, maps, the fork, `shared/`, `~/lv-checkpoints`, TODO or HANDOFF was changed.
