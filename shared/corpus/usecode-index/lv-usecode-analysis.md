# Lost Vale Usecode Analysis

Source: Ultima Codex article (Feb 2025) + Ultima Dragons Discord analysis by Armitage (Feb 2025)
URL: https://ultimacodex.com/2025/02/a-look-at-the-usecode-for-ultima-8-the-lost-vale/

## Discovery

On January 28, 2025, Dominus Dragon posted a ZIP archive (`Sheri-U8-LV.zip`, 526 KB) to
the `#ultima-8-exult` channel of the Ultima Dragons Discord Chapter. He described it as
"a small little bomb from the files formerly preserved at the Origin Museum" — Sheri Graner
Ray's Usecode work on U8 and LV. He noted: "Not the complete LV, just what she had been
working on."

The archive was subsequently published at ultimacodex.com. A Discord user named Armitage
then dove into the usecode to analyze its contents.

## Archive Contents

The ZIP contains three directories with 71 files total:

### `LOST VALE/` — Final LV usecode (11 files, Sep 1994)
These represent the latest versions of Sheri's LV work:

| File | Size | Date | Identity |
|------|------|------|----------|
| ATLI.UNK | 89 KB | 1994-09-12 | NPC: Atli — Zealan elder/leader |
| EZREKAL.UNK | 118 KB | 1994-09-09 | NPC: Ezrekal — High Priestess, central quest-giver |
| TYORVI.UNK | 70 KB | 1994-09-13 | NPC: Tyorvi — Zealan who suffers nightmares |
| FREE.UNK | 40 KB | 1994-09-09 | System: Free the three imprisoned Zealan gods |
| MAGNET.UNK | 11 KB | 1994-09-11 | System: Magnetic obelisk in Cloud City |
| ZCHILD.UNK | 7.2 KB | 1994-09-08 | NPC: Zealan child |
| TESTPLAN.UNK | 6.9 KB | 1994-08-25 | QA: Test plan / test framework |
| POTION.UNK | 4.6 KB | 1994-08-19 | Item: Potion (likely Tiny-tar shrinking potion) |
| CANTRK.UNK | 1.8 KB | 1994-09-07 | System: Candle rack / candlestick puzzle |
| PLNTST.UNK | 1.0 KB | 1994-07-25 | System: Passage Test (Rite of Passage) |
| MONSKUL.UNK | 750 B | 1994-08-11 | Item: Monster skull |

### `U8/` — Base game usecode from Sheri's disk (23 files, mostly Jul 1994)
Base game NPC conversations Sheri was working on, plus documentation.

### `UNK files/UNK/` — Development snapshot (33 files, mixed dates)
Earlier drafts of both LV and U8 content. Includes characters and systems not in the
final `LOST VALE/` directory.

## Armitage's Discord Analysis (Feb 1, 2025)

### Key identifications:
- **Two new NPCs** not in base game: **Ragnar** and **Tjorvi** (note: Tjorvi is distinct from Tyorvi)
- **First Zealan community** = **Clan Hoskuld**
- **Second Zealan community** = **Clan Gunnar**
- **Cliffs of Insanity** = **Cloud Cliffs** (path to the Cloud City)

### Usecode symbol meanings:
- **PLNTST** = Passage Test (the Rite of Passage the Avatar must take)
- **SHADES** = Moot / Shield Restoration ceremony
- **FREE** = Freeing the three imprisoned gods
- **MAGNET** = Cloud City magnetic obelisk puzzle (equipment sticks to it)
- **POTION** = Tiny-tar shrinking potion
- **CANTRK** = Candlestick puzzle mechanism

### Missing content (not found in the archive):
- Mythran dialogue (the NPC who directs the Avatar to the Lost Vale)
- End-game events and conclusion
- Elemental Dungeon content (the four-section dungeon to reach the Lost Vale)
- Some map/terrain usecode (Columns, Cliffs marked with red X on schedule)

## Plot Reconstruction from Usecode (Armitage's walkthrough)

1. Receive message from Lord British (via Nystul)
2. Talk to Mythran — learn of Lost Vale and how to open double doors
3. Find key; enter Elemental Dungeon
4. Collect 4 tokens from elemental sections to open way to Lost Vale
5. Meet the Zealans; they refuse to talk until you pass the Rite of Passage and get the Zealan mark. Need to find the Passage Stone first.
6. Avatar talks to Ragnar (Clan Hoskuld), who sends a young woman to guide the Avatar to the test
7. Avatar takes the Passage Test with the stone; teleported to Thordis and Atli who give him the mark and tell him to seek Ezrekal
8. Ezrekal tells the Avatar the history — the Cloud City, the 3 imprisoned gods, the broken Shield of the Ancients
9. Go to the Cloud Cliffs; discover what has been lost
10. Arrive at Cloud City / Cloud World
11. Avatar asks Ezrekal for potion to stop Tyorvi's nightmares; she needs a special root
12. Avatar finds the root, makes potion, gives to Tyorvi who falls asleep
13. Avatar finds the broken shield halves but no gods
14. Avatar returns to Ezrekal; held at Sacred Circle
15. Ritual performed: shield restored, clans reconciled; Avatar cured of poison but still needs gods
16. Hrodny has Tiny Tar potion allowing entry to the Temple, but lost the key to the chest
17. Avatar enters the Temple using the potions
18. Avatar puts restored shield on altar, talks to gods, receives Bag of Reagents

## Resource Schedule (from design docs, annotated by Armitage)

Development team and timeline (April 15 – August 15, 1994):

| Team Member | Role/Focus |
|-------------|------------|
| Brian M. (Martin) | Maps, Lead Designer |
| Sheri G. (Graner Ray) | Conversations, Lead Designer |
| Jason E. | Usecode advice |
| Micael P. | NPCs, terrain/walls, items |
| Andrew | Usecode (Lord British, Mythran, AO scene, Bag o' Reagents) |
| Steve P. | Teach NPC animations |
| Lisa S. | Conversations (Thordis, Hrodny, Ingyald), Usecode (Shade scene) |

### Monthly breakdown:
- **April**: Design Plot, Write Plot Document, Generate art list, Galjeron's scroll
- **May**: Maps (Elemental Dungeon, Lost Vale), Convos (Ezrekal), NPCs (Ezrekal, Male/Female Zealan), Terrain (Cloud City, Cloud Terrain)
- **June**: Maps (Cliffs, Elemental Dungeon, Lost Vale), Convos (Ezrekal, Atli, Tyorvi, Thordis, Hrodny, Ingyald), NPCs (Lord British, Zealans, 3 gods, Harpy, LB), Usecode (Lord British, Mythran, Columns, Cliffs, Shade scene)
- **July**: Maps (Lost Vale, Cloud globs, Cloud City, Building globs), Usecode (Plant scene, AO scene, Bag o' Reagents, Shade scene), Convos (Hunter)
- **July 18**: BETA — Fix bugs
- **August 15**: Sign-off & Ship

### What's confirmed found (green ✓ on Armitage's annotated schedule):
- Convos: Ezrekal ✓, Atli ✓, Tyorvi ✓, Thordis ✓, Hrodny ✓, Ingyald ✓, Hunter ✓
- Usecode: Lord British ✓, Plant scene ✓, Shade scene ✓

### What's confirmed missing (red ✗):
- Usecode: Columns ✗, Cliffs ✗, Mythran ✗, AO scene ✗, Bag o' Reagents ✗
- End-game events

## Download URL

The archive was originally shared on the Ultima Dragons Discord and subsequently hosted at
ultimacodex.com. The local copy is at `shared/data/lv-usecode.zip` (copied from
`shared/data/discord/Sheri-U8-LV.zip`).
