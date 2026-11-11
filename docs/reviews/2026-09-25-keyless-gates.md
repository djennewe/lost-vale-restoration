# The two keyless gates, locks 170 and 180 (2026-09-25)

Research for the HANDOFF open question "give them keys and funnel walls, or
make them scenery?". Nothing was changed. Every claim carries its source.

**Both gates are best treated as scenery.** Neither can be locked the way the
question assumes: shape 114 has no door behaviour, the retail key routine
never targets it, and no 1994 file gives either gate a key quality.

## The mechanism, common to both

- `KEY::use()` and `KEYRING::use()` target only shapes 68, 69, 340 and 342,
  and compare the door's quality low byte with the key's full quality
  (`docs/playtest-2026-07-31-doors-investigation.md:165-180`).
- Shape 114 has no usecode on the item: double-click does nothing
  (`docs/playtest-2026-09-02-quest-chain.md:447-450`).
- Qualities 170 and 180 lack the 0x400 locked bit (`build_map_08.py:74`,
  `build_map_18.py:143-145`), so the "lock id" is a number stored on scenery.
- HANDOFF's pointer to Plan §6 is a wrong citation: §6 is the risk register
  (`PLAN.md:312-324`) and does not mention the gates.

## Gate 170, the Key to the Clouds

- **Where.** Map 10 cloud terrace (7168, 23552, 8) in front of the Map 13
  trigger 206, open lanes either side (`build_map_10.py:1298-1330`), walked
  around on 2026-09-18. Map 13 at the climb's foot (4096, 10752, 4)
  (`build_map_13.py:365-379`), where the Avatar wedged against it and went
  round in four waypoints (`quest-chain.md:486-490`).
- **1994 record.** "Sealed off the way to the Cliffs, the High Priestess did.
  Now, approach the Cliffs only those who bear the Key to the Clouds may"
  (`LOST VALE/EZREKAL.UNK:1747-1749`); Tyorvi holds it (`:1816-1818`). The
  key is a token that lets the bearer cross the lava safely
  (`EZREKAL.UNK:1771-1776`; Tyorvi's French calls it "la Roche Magique",
  `TYORVI.UNK:348`). Tyorvi creates it with quality 0
  (`TYORVI.UNK:2132`), and nothing in 1994 matches a key quality to a door.
- **The check already exists.** `CLCLIMB.UNK:29-63` tests for `TypeCliffKey`,
  and the climb's handholds refuse a player without it.

## Gate 180, the temple

- **Where.** Map 10 processional (18432, 23040, 0) in front of trigger 210 to
  Map 18, both outer lanes open (`build_map_10.py:1386-1436`). Its comment
  says "opens after ceremony, usecode controlled"; no usecode controls it.
  Map 18 sets one into solid wall (`build_map_18.py:142-149`).
- **1994 record.** There is no temple key. The temple opens through Hrodny's
  potions and her chest key (quality 20, `UNK files/UNK/HRODNY.UNK:1086-1119`);
  the way in is the crack, and the egg that sets `templeOpen` is beyond it
  (`build_map_18.py:619-632`).

## Option (a): a key and funnel walls

Pros
- For 170 only, the map would enforce Ezrekal's "sealed off the way" line.
- Tyorvi is the natural giver, at quest steps 11-12.

Cons
- Shape 114 must be replaced by 342 door leaves with the 0x400 bit, as Map 8
  does (`build_map_08.py:66-80`), or the retail keyring class 0x4F patched.
- Tyorvi's `give` quality must become 170 (a second `lv-patched/TYORVI.UNK`
  change and an EUSECODE rehash), or the lock id becomes 0, which any
  quality-0 key blank would open.
- Keying 180 has no source: a key and a giver 1994 never had, stacked on the
  crack.
- Cost: FIXED.DAT on Maps 10, 13 and 18, re-derived `map_pins.json`, a
  geometry test, an in-engine playtest.
- Risk: a one-body aperture must be sized against half-open boxes, never the
  cell flood (`.claude/rules/map-geometry.md`); a wall whose key never fits
  ends the quest.

## Option (b): scenery

Pros
- Matches 1994: the token check lives in `CLCLIMB`, and the temple's barrier
  is the crack.
- Removing the walk-path gates costs one FIXED.DAT rehash; keeping them costs
  nothing.

Cons
- A "locked" gate beside an open lane invites a bug report.
- The Map 13 gate still wedges the Avatar at the climb's foot.

## Recommendation

- **170:** scenery. Remove the Map 13 gate (it blocks the climb's foot and
  duplicates `CLCLIMB`'s check); on Map 10 keep the stubs as a ruined wall
  and drop the 114 or set it open.
- **180:** scenery. Delete the Map 10 gate and its stale comment; keep the
  Map 18 one as wall dressing.
