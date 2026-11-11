# Compilation Report — Lost Vale Usecode

## Summary

| Metric | Value |
|--------|-------|
| Total LV source files | 44 |
| Successfully compiled | 36 (82%) |
| Failed | 8 (18%) |
| Total bytecode | 133,764 bytes |

## Successful Compilations

### LOST VALE/ (Final LV Classes)
| File | Class | Bytes | Notes |
|------|-------|-------|-------|
| CANTRK.UNK | EggCandleTrick | 154 | Candle puzzle trigger |
| EZREKAL.UNK | Ezrekal | 791 | NPC (partial - parse warnings) |
| FREE.UNK | (utility) | 626 | Free gods system (partial) |
| MAGNET.UNK | EggMagnet | 271 | Magnet puzzle |
| MONSKUL.UNK | TypeMonskul | 699 | Monster skull item |
| PLNTST.UNK | EggPlantTest | 182 | Plant test egg |
| POTION.UNK | TypePotion | 795 | Potion item |
| TESTPLAN.UNK | TypePoisonPlant | 3,635 | Poison plant |
| ZCHILD.UNK | TypeZealanChild1 | 5,387 | Zealan child NPC |

### UNK files/UNK/ (Development Snapshot)
| File | Class | Bytes | Notes |
|------|-------|-------|-------|
| ABACUS.UNK | TypeAbacus | 238 | Coin counter |
| AIRSPEL.UNK | (utility) | 7,782 | Air spell system |
| AVATAR.UNK | Avatar | 1,217 | Avatar class |
| BEDROLL.UNK | TypeBedroll | 652 | Rest item |
| BULLWHIP.UNK | TypeBullwhip | 184 | Weapon |
| CHANGTAR.UNK | (NPC) | 141 | Changtar NPC |
| EAPUZL.UNK | TypePedestals | 360 | EA puzzle |
| FEDORA.UNK | TypeFedora | 182 | Hat item |
| FLAGS.UNK | (utility) | 149 | Global flags |
| HRODNY.UNK | Hrodny | 19,548 | Zealan NPC |
| INGYALD.UNK | Ingjald | 13,169 | Zealan NPC |
| LORDBRIT.UNK | TypeLordBritish | 1,657 | Lord British |
| MONSKUL.UNK | TypeMonskul | 699 | Monster skull |
| PLAQUENS.UNK | TypeNSGoldPlaque | 7,214 | Gold plaque |
| PLNTST.UNK | EggPlantTest | 182 | Plant test |
| POTION.UNK | TypePotion | 793 | Potion |
| PSCEND.UNK | (utility) | 141 | PSC end |
| RAGNAR.UNK | Ragnar | 21,736 | **MVP gate NPC** |
| SHADES.UNK | EggShades | 1,723 | Shades egg |
| TESTPLAN.UNK | TypePoisonPlant | 3,674 | Poison plant |
| THORDIS.UNK | Thordis | 35,912 | Major Zealan NPC |
| ZEALSHLD.UNK | TypeAOFrizbee | 515 | Zealan shield |
| ZZVFLAGS.UNK | (utility) | 149 | ZZV flags |

## Failures

| File | Error | Notes |
|------|-------|-------|
| ATLI.UNK (x2) | Jump offset overflow | Large NPC (89KB source) |
| TYORVI.UNK (x2) | Jump offset overflow | Large NPC (70KB source) |
| EZREKAL.UNK (UNK/) | Jump offset overflow | Large NPC (112KB source) |
| ARAMINA.UNK | Jump offset overflow | Large NPC (59KB source) |
| EALOGO.UNK | Unterminated block comment | Truncated source file |
| TJORVI.UNK | Unterminated string literal | Earlier version of TYORVI |

## MVP Gate

RAGNAR.UNK (944 lines) compiles successfully to 21,736 bytes. This file
exercises the full language: npcclass inherits, schedule, enterFastArea,
cast, foreach, switch/case, bark, ask, enterConvo/exitConvo, global flags,
method calls, spawn, wait, and complex conversation trees.
