# Agent F — Map Populator

> **FROZEN 2026-07-05 — per-agent history, not current project state (L18).**
> This agent's work is COMPLETE: Phase 4b (map builders to FIXED.DAT). The file records how that work was
> done and what was decided; it has not been maintained since.
>
> Live status is `TODO.md`; strategy is `PLAN.md`; the review-driven
> queue is `docs/reviews/2026-07-19-improvement-plan.md`.


## Status: COMPLETE

## Task Summary

Built all 6 new maps and Map 8 modification for the Lost Vale expansion,
producing a complete FIXED.DAT.

## Completed Tasks

| Task | Status | Items | Notes |
|------|--------|-------|-------|
| F1: Map 8 mod | DONE | 11 | Double doors, key, 4 teleport eggs, decor |
| F2: Map 9 | DONE | 148 | Galjeron's Chamber — body, journal, guardian |
| F3: Map 11 | DONE | 1,771 | Elemental Dungeon — 5 sections + 4 pillars + teleporter |
| F4: Map 10 | DONE | 1,701 | Lost Vale Overworld — 10 zones, 16 NPCs, 8 teleport eggs |
| F5: Map 13 | DONE | 599 | Cloud Cliffs — vertical climb, 4 harpie monsters |
| F6: Map 17 | DONE | 714 | Cloud City — obelisk, shield halves, scroll |
| F7: Map 18 | DONE | 407 | Ancient Temple — 3 gods, altar, Tiny Tar entry |
| F8: Assembly | DONE | 92,954 | 48 maps total, all 14 teleport pairs verified |

## Output File

`shared/build/FIXED.DAT` — 48 maps, 92,954 items (5,351 new items added to base game's 87,603)

## Teleport Connections

All 14 teleport IDs (200-213) verified with matching trigger/dest pairs:
- IDs 200-201: Map 8 <-> Map 9
- IDs 202-203: Map 9 <-> Map 11
- IDs 204-205: Map 11 <-> Map 10
- IDs 206-207: Map 10 <-> Map 13
- IDs 208-209: Map 13 <-> Map 17
- IDs 210-211: Map 10 <-> Map 18
- IDs 212-213: Map 10 <-> Map 8 (Pagan return)

## NPC Placements (Map 10)

16 NPCs across two villages + Ezrekal's dwelling:
- Hoskuld Village: npcnum 50-56 (Elder, Veteran, Hunter, Farmer, Child, Ragnar, Thordis)
- Gunnar Village: npcnum 60-68 (Atli, Inventor, Moonshiner, Farmer, Child, Ingyald, Hrodny, Changtar, Tyorvi)
- Ezrekal's Dwelling: npcnum 70 (Ezrekal)

## Key Design Decisions

- Shape 114 (large gate) for double doors on Map 8
- Shape 721 for elemental pillars and sacred rock
- Shape 580 for shield halves (STALE for the rest: talismans moved to 596 "gemstone ring" and the Passage Stone to 798 "rock" on 2026-07-04 — 580 is SI_FIXED/unpickable; see lv_shapes.py)
- Shape 400 for NPC placeholders (all need proper shapes when art is available)
- Shape 73 (standard egg) for usecode triggers (PLNTST, MAGNET, POTION, FREE, SHADES)
- Monster quality values: 10-13 for elemental dungeon, 20 for guardian, 30 for water zombies, 31 wilderness, 32 wilderness, 40 for harpies, 50 for temple guardian

## Dependencies on Other Agents

- NPC dialogue agent: conversation files for all 16+ NPCs
- Art agent: new shapes needed for gods (encased + speaking), shield halves, water zombie, harpie, cloud terrain
- Usecode agent: FREE.UNK, MAGNET.UNK, POTION.UNK, PLNTST, SHADES implementation
