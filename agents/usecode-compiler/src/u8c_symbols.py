#!/usr/bin/env python3
"""
u8c_symbols.py — Symbol table for the U8 usecode compiler.

Manages:
- Intrinsic function signatures (258 entries from the disassembler)
- Base game class names and IDs (516 classes)
- Global flag allocation
- Type references (TypeAbacus, TypeMonskul, etc.)
- Class hierarchy (inherits relationships)
"""

import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import the intrinsics table from the disassembler
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'usecode-disasm', 'src'))
from u8_usecode_disasm import U8_INTRINSICS, U8_EVENTS

# lv_manifest.py lives alongside this file; insert this file's own
# directory defensively so `import lv_manifest` resolves regardless of
# what the caller has already put on sys.path (M0.6).
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
from lv_manifest import ManifestError

# Path resolution: relative to this file (repo root three levels up), same
# convention as lv_manifest.py.
REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, '..', '..', '..'))


# ─── Type-to-Shape Mapping ─────────────────────────────────────────────────
# Maps TypeXXX identifiers to their U8 shape numbers.
# Base game types are from TYPEFLAG.DAT / U8SHAPES.FLX.
# LV-specific types use base game placeholder shapes (noted with #LV).
#
# NOTE (2026-07-01 audit — verify before trusting a value here):
#  - get_type_shape() (below) is only consulted when a bare TypeXXX
#    identifier is evaluated as a VALUE in compiled .UNK source (e.g.
#    `where (type = TypeCliffKey)`, `x.create(TypeShades, 0)`); appearing
#    only inside a `typeclass TypeX inherits ...` / `process
#    TypeX::method()` declaration header does NOT go through this table.
#    Confirmed live examples from the Phase 4a corpus: TypeAOArtifact
#    (AOSCENE.UNK then; lv-patched/ATLI.UNK since 2026-10-17, when
#    AOSCENE moved to TypeSacredShield), TypeCliffKey (CLCLIMB.UNK), TypeElementalColumn
#    (COLPUZZL.UNK). TypeMonskul, by contrast, is declared as a typeclass
#    but never referenced as a value anywhere in the corpus -- its entry
#    below is dead weight, right or wrong.
#    A grep of every directory build_eusecode.py actually compiles
#    (lv-patched/, LOST VALE/, UNK files/UNK/, lv-new/) found most of this
#    table's entries genuinely live (roughly three quarters at the
#    2026-07-01 pass) -- do not assume an entry is "unreferenced legacy"
#    without checking; confirm with a grep first.
#    CORRECTION (2026-07-25, L7): this note previously said "102 entries"
#    and named TypeMythranLVDlg as a second dead entry. The table holds 103
#    entries, and TypeMythranLVDlg is not one of them and never was -- it is
#    a class name, not a TYPE_SHAPES key. Re-derive the live count before
#    quoting one; the "~75" figure was never recomputed after 2026-07-01.
#  - Several entries -- live or dead -- hold shape IDs proven wrong by
#    rendering. The AUTHORITATIVE audit is now
#    agents/map-populator/docs/art-placeholder-audit-2026-07-19.md;
#    shared/docs/art-placeholder-audit.md is the superseded 2026-07-01 pass
#    that these four examples came from (still correct on them):
#    158 (TypeBook/TypeScroll/TypeMagicScroll/TypeGrimoire) is a wooden
#    stool, not a book; 338 (TypeSword/TypeSword2/TypeBladeOfStriking/...)
#    is a green sparkle/particle VFX, not a sword; 400 (TypeAirTitan/
#    TypeDemon/TypeSkeleton/... "generic NPC") is a fire VFX sprite, not an
#    NPC; 205 (TypeChest) is a wooden desk, not a treasure chest.
#  - This table only controls what compiled usecode PUSHES as a shape
#    constant, and it is legacy: it does not need to (and often does not)
#    match map data. The verified source of truth for shapes the MAP
#    POPULATOR actually places in FIXED.DAT is
#    agents/map-populator/src/lv_shapes.py -- check there first for
#    anything map-related. It is NOT kept in sync with this table.
#
# RETAIL AUDIT (2026-10-07). Every Type* identifier evaluated as a value in
# a compiled source was looked up in the base-game sources whose class
# exists in retail (shared/data/lv-usecode/U8/, and the dev copies of
# ARAMINA/AVATAR/METHOD/AIRSPEL/ABACUS), and each use was matched in source
# order against the shape constant at the same site in the retail class:
# a loop script's `%` int before `@` (shape), an Item::create shape
# argument, a getType() compare, a FREE give/take/createNear argument.
# Comments beside the corrected entries cite `class 0xNNNN :srcline` and
# the retail offset (`@XXXX`: the first loopscr of a search, the push of a
# constant, or the calli of a create/getType). Where no retail source uses
# an identifier, a value is pinned only if a retail class of the item's
# own name exists (class id = shape id) and its look() string names it.
# RETAIL means shared/data/USECODE.FLX (1,251,108 bytes, = the GOG
# ENGLISH/USECODE/EUSECODE.FLX). shared/data/u8-install/USECODE/EUSECODE.FLX
# is our INSTALLED BUILD, not retail; never cite it. Entries left alone on
# purpose: LV-only identifiers whose items our map builders place (they
# must equal lv_shapes), TypeBottle (the elixir's custom 868 since
# 2026-10-09; see its entry for why not retail 180), TypeShields (retail
# 539 collides with the Map 17 shield half), and
# entries no retail source or class name pins.

TYPE_SHAPES = {
    # ── Doors & Keys ──
    # DOORS FIXED 2026-10-07 (retail audit, shared/data/USECODE.FLX — see
    # the audit note above): NS/EW were swapped and both tall doors were
    # the plain doors. Retail class names: 68 DOOR_NS, 69 DOOR_EW,
    # 340 TDOOR_NS, 342 TDOOR_EW. Source-correlated searches: ARAMINA
    # 0x040D @4CFB, SALKIND 0x0403 @0DAF and XAVIER 0x0419 @1359 search
    # TypeDoorNS as `0A 44` (68); JENNA 0x0418 searches TypeDoorEW then
    # TypeDoorNS (:375/:398) as `0A 45` (69) @0B26 then `0A 44` @0BB9; CYRRUS
    # 0x0416 :1975 `TypeDoorEW or TypeTallDoorEW` is 69 + 342 @5370; AIRSPEL
    # 0x0596 :609-610 tests DoorNS/DoorEW/TallDoorNS/TallDoorEW as getType
    # = 68 @13EB, 69 @13F7, 340 @1404, 342 @1412.
    'TypeDoorEW':          69,
    'TypeDoorNS':          68,
    'TypeTallDoorEW':      342,  # = lv_shapes.SHAPE_LV_DOORS
    'TypeTallDoorNS':      340,  # = lv_shapes.SHAPE_LV_DOORS_E
    # TypeKey FIXED 2026-07-05 (the 641 skull trap again): 641 is the
    # unpickable SI_FIXED skull-in-cage scenery — HRODNY.UNK:1117 spawns
    # the lost chest key as TypeKey with setQuality(20), which 641 can
    # neither hold (not SF_QUALITY) nor be picked up. Now 82 "key blank":
    # SF_QUALITY family (holds the lock id), carryable, and the SAME
    # shape the map side already uses for real keys (Maps 8/10, prop
    # audit 2026-07-02). Compiled consumers: HRODNY (chest-key spawn),
    # ARAMINA, MAGNET.
    'TypeKey':             82,
    # TypeCliffKey FIXED 2026-07-05 (TYPE_SHAPES trap, step 9-12 poison-cure
    # sweep): was 641 — engine name "skull" (skull-in-a-cage scenery),
    # TYPEFLAG SI_FIXED, SF_GENERIC. Twice broken, exactly the TypeKey trap:
    # Tyorvi's give() of the Key to the Clouds could never be picked up, and
    # CLCLIMB's inventory search for it could never match (SI_FIXED items
    # cannot be carried). Now 82 "key blank" — the SAME carryable key shape
    # TypeKey moved to (SF_QUALITY holds the lock id, not SI_FIXED, frame 0
    # present = the give's frame). Consumers in the compiled corpus (all
    # give/check frame 0, no frame filter that 82 lacks):
    #   - TYORVI.UNK:2132 (LOST VALE/) give(Avatar:Referent,TypeCliffKey,0,0,1)
    #     — the Key to the Clouds handed over after the elixir (quest step 12).
    #   - TYORVI.UNK:2135 createNear(myMan,TypeCliffKey,0,0,1) — the drop
    #     fallback when the backpack give fails.
    #     Both make it at quality 170 since lv-patched/TYORVI.UNK T7
    #     (2026-10-10): quality 0 is the retail "key blank".
    #   - CLCLIMB.UNK:51 (lv-new, EggCloudCliffs) `foreach recursive item
    #     where (type = TypeCliffKey) within container Avatar`, then
    #     `getQ() = 170` — the cliff-climb gate; only matches if the key is
    #     a carryable inventory item, which 641 (SI_FIXED) never was, and
    #     only Tyorvi's, since 82 is every key in the game.
    'TypeCliffKey':        82,   #LV: Key to the Clouds (carryable key, q170)
    # FIXED 2026-10-07 (retail audit): was 641 ENDSKUL. Retail AVATAR 0x0401
    # createNear(myMan,TypeKeyOfTheNecromancer,0/3,...) (:1165-1166) pushes
    # `0B E8 00` @34C5/@34D8; class 232 is KEYONEC.
    'TypeKeyOfTheNecromancer': 232,
    # FIXED 2026-07-04 (TYPE_SHAPES trap #6, step 7-8 quest-item sweep):
    # was 641 — engine name "skull" (skull-in-a-cage scenery), TYPEFLAG
    # SI_FIXED. Twice broken: the stone RAGNAR.UNK spawns could never be
    # picked up, and the Passage Test egg searches the Avatar's INVENTORY
    # for a shape that can never be in one. Now 798 "rock" (engine-name-
    # verified small gray stone; SI_SOLID only, wt 1, frame 0 = the
    # PLNTST filter frame). Consumers in the compiled corpus:
    #   - RAGNAR.UNK:835 (UNK files/UNK/) stone.create(TypeBushKey, 0)
    #     into the quest bag dropped at (16447,25727,64) — quest step 7.
    #   - PLNTST.UNK:24 (LOST VALE/, same line in the dev copy)
    #     `foreach ... (type = TypeBushKey) and (frame = 0) within
    #     container Avatar` — consumed on match, quest step 8.
    # This value MUST equal the island stone build_map_10.py places
    # (lv_shapes.SHAPE_PASSAGE_STONE) — two sources of one stone is
    # 1994-intended: the island is the find, Ragnar's bag is the hint
    # path. (TypeCliffKey was also swept off 641 in the step 9-12 pass —
    # see its fix block above.)
    'TypeBushKey':         798,  #LV: the Passage Test stone ("rock")
    'TypeLargeGate':       114,  # large gate (SF_QUALITY)

    # ── Containers ──
    # FIXED 2026-07-04 (TYPE_SHAPES trap #7, step 7-8 quest-item sweep):
    # was 225 — a long wooden DINING TABLE (lv_shapes.SHAPE_TABLE_DINING,
    # render-verified), not a bag: Ragnar's "small bag hidden in the
    # ruins" spawned as furniture with the Passage stone inside. Now 637,
    # engine name "bag" (brown drawstring pouch, SF_CONTAINER + SI_BAG,
    # wt 1; TYPEFLAG volume 0, which ScummVM's Container::getCapacity()
    # maps to capacity 32 — the pop()'d contents fit). Consumers in the
    # compiled corpus:
    #   - RAGNAR.UNK:834 (UNK files/UNK/) bag.create(TypeBag, 0) — the
    #     quest-step-7 stone bag popped to (16447,25727,64) on Map 10.
    #   - HRODNY.UNK:1117 (UNK files/UNK/) bag.create(TypeBag, 0) — the
    #     stolen-key bag popped to (19588,23284,64) on Map 10.
    # TypeBackPack had its audited pass 2026-10-07 (now 529, below).
    # TypeBagOReagents 225 (MAGNET.UNK inventory foreach) still carries the
    # old dining-table id: no retail source names it, so it stays unpinned.
    'TypeBag':             637,  #LV: quest bag ("bag", drawstring pouch)
    # TypeBackPack/TypeBarrel FIXED 2026-10-07 (retail audit): AVATAR 0x0401
    # :888 `cont.getType() = TypeBackPack` is getType = 529 @2853 (class
    # BACKPACK, = lv_shapes.SHAPE_BACKPACK); AIRSPEL 0x0596 :612
    # `getType() = TypeBarrel` is 115 @143C (class BARREL).
    'TypeBackPack':        529,
    'TypeBarrel':          115,
    'TypeChest':           205,
    'TypeCrate':           307,
    'TypeBagOReagents':    225,  #LV: Bag of Reagents (reuses backpack)
    # ADDED 2026-09-05 for ENDGAME.UNK's Bag of Reagents hand-over.
    # 395 is the SF_REAGENT shape (family 9); its FRAME selects which
    # reagent, which is why quanFrame() skips reagents ('reagents don't
    # set frame', FREE.UNK:713). Same shape as TypeBottle above — that
    # alias is the nightmare elixir at frame 5 (a blood vial) — but named for what the
    # endgame is actually creating. Do NOT use TypeBagOReagents (225) as
    # the container: it is SF_GENERIC and still carries the old
    # dining-table id (see the audit note above), so it holds nothing.
    'TypeReagent':         395,  #LV: reagent stack (frame = which reagent)

    # ── Books & Scrolls ──
    # FIXED 2026-09-25: all four were 158, SI_FIXED scenery that renders as
    # a wooden stool, so FREE.UNK's debug grant created a bench. Each now
    # points at the base-game class of its own name (class id = shape id,
    # base-game-symbols.yaml), all carryable SF_QUALITY:
    #   159 BASESCRL, 288 GRIMOIRE ("template book"), 613 BASEBOOK,
    #   827 MAGSCROL ("default scroll").
    # Compiled consumers: FREE.UNK:1338/1342 (TypeScroll, TypeGrimoire,
    # debug grant) and MAGNET.UNK:86/282 (TypeMagicScroll, pack search).
    # TypeBook is not evaluated as a value anywhere the build compiles.
    'TypeBook':            613,
    'TypeScroll':          159,
    'TypeMagicScroll':     827,
    'TypeGrimoire':        288,

    # ── Weapons ──
    # FIXED 2026-10-07 (retail audit). 338 is class WEB, 337/339 have no
    # class. TypeSword: retail AVATAR 0x0401 :1174 createNear(myMan,
    # TypeSword,0,0,1) pushes `0B F3 00` @354A (class 243 SWORD). The seven
    # named artifacts have no retail source use; each is pinned to the
    # retail class of its own name, whose look() string is the item's name
    # (base-game-symbols.yaml): 815 HAMOSTR "Bone Crusher", 816 SLAYER,
    # 817 FLAMSTNG, 818 PROTECTR, 819 BLADSTRK, 820 KORGFANG, 821 SCIMOKG
    # "Scimitar of Khumash-Gor". Consumers: ATLI.UNK:1084-1129 (frame-0
    # inventory checks that add dialogue options) and MAGNET.UNK.
    'TypeSword':           243,
    'TypeSword2':          338,
    'TypeBladeOfStriking': 819,
    'TypeHammerOfStrength': 815,
    'TypeKorghinsFang':    820,
    'TypeFlameSting':      817,
    'TypeScimitarOfKumashGor': 821,
    'TypeSlayer':          816,
    'TypeBullwhip':        338,  #LV: whip (reuses weapon shape)

    # ── Armor & Equipment ──
    # FIXED 2026-10-07 (retail audit); 579 is GRENADE ("flask of oil").
    #   TypeArmour 523 ARMOR: AVATAR 0x0401 :1176 createNear(...,TypeArmour,
    #     2,...) `0B 0B 02` @3570; DARION 0x0405 :589 `typearmor =
    #     TypeArmour` `0B 0B 02` @129E. DARION's next three assignments
    #     (:604/:620/:636) pin ArmGuards 530 @1349, Leggings 532 @13E4,
    #     Helmets 531 @1468 (classes ARMGUARD/LEGGING/HELMET).
    #   TypeMagArmor 841 MAGARM: AIRSPEL 0x0596 :602 getType = 841 @13C5.
    #   TypeMagArms 844 MAGARMS: retail PYROS 0x006D creates 442 frame 4,
    #     288 frame 1 and 844 frame 0 @46F1-4729 -- FREE.UNK:1356-1366's
    #     Tongue-of-Flame grant (TypeBlackrockFragments,4 / TypeGrimoire,1 /
    #     TypeMagArms,0) in the same order.
    #   Name-pinned (class of the same name, "magic ..." look string):
    #     MagShield 842 MAGSHLD, MagHelm 843 MAGHELM, MagLegs 845 MAGLEGS,
    #     MagArmorTwo 64 MAGARMR2, Protector 818, Deceiver 822.
    # TypeShields is NOT changed: retail AVATAR :1175 pushes 539 (SHIELD,
    # `0B 1B 02` @355D). It was held at 587 because Map 17 placed shield
    # half 1 as 539 frame 0, which EZREKAL.UNK:1691's `(type = TypeShields)
    # and (frame = 0) within container Avatar` would then match ("I have
    # the Ancient Shield." -> the forgery reply). The halves were 870 from
    # 2026-10-11 (art track contract 10; retired) and are 878 since
    # 2026-10-17, so that reason is gone; the retail value is a separate
    # decision (it would let a carried Pagan shield open the forgery reply,
    # which may be the 1994 intent).
    'TypeArmour':          523,
    'TypeShields':         587,
    'TypeMagShield':       842,
    'TypeMagHelm':         843,
    'TypeMagArms':         844,
    'TypeMagArmor':        841,
    'TypeMagArmorTwo':     64,
    'TypeMagLegs':         845,
    'TypeHelmets':         531,
    'TypeLeggings':        532,
    'TypeArmGuards':       530,
    'TypeProtector':       818,
    'TypeDeceiver':        822,
    'TypeFedora':          578,  #LV: hat (reuses helmet shape)

    # ── Food & Consumables ──
    # FIXED 2026-10-07 (retail audit). ARAMINA 0x040D, the class this source
    # compiles over, in source order: feedMordea's search and create of
    # TypePlateWithFood are 284 @0E0F and `0B 1C 01` @0F1E (class
    # PLATEFOO; MORDEA 0x0407 agrees, getType = 284 @074E and searches
    # @1E8A/@1F6C); dropDrink's TypeTankard search is 178 @0F79 and its
    # create `0B B2 00` @10D4 (class TANKARD); its TypeFrictionGrenade search
    # (below) is 592 @1049. TypeFood 537 / TypeMorefood 538: JENNA 0x0418
    # :628 `thetype = TypeFood` `0B 19 02` @1488, TORWIN 0x041A :1423
    # create(TypeMorefood,15) @375D (classes FOOD/MOREFOOD).
    'TypeFood':            537,
    'TypeMorefood':        538,
    'TypePlateWithFood':   284,
    'TypeTankard':         178,
    # TypeBottle FIXED 2026-07-05 (TYPE_SHAPES trap, step 9-12 poison-cure
    # sweep): was 340 — no engine name (nameless scenery; lv_shapes.py notes
    # 340 as an LV east-door shape), and critically only frames 0-2 exist so
    # the elixir's frame 13 could never render, while the shape is SI_BAG
    # (a container) rather than a bottle. Then 395 "vial", whose frame 13
    # drew as a blue-grey shard (retail look(): "sliced executioner's
    # hood"); FRAME 13 -> 5 on 2026-10-08 (lv-patched EZREKAL/TYORVI V1),
    # a red vial that was the necromancy reagent Blood: it read "1 vial of
    # blood", merged with carried blood, and Tyorvi's drink destroyed
    # carried frame-5 blood with it.
    # RE-POINTED 395 -> 868 on 2026-10-09 (Douglas; docs/art-track.md
    # contract 11): the elixir's own custom shape, the vial recoloured
    # sea-green, on donor 180's TYPEFLAG row (SF_GENERIC, not SF_REAGENT,
    # so it never merges), class 868 lv-new/ELIXIR.UNK naming it. MUST equal
    # lv_shapes.SHAPE_ELIXIR; test_art_props asserts the pair. The frame is
    # 0 (lv-patched EZREKAL/TYORVI V3). The identifier is the 1994 author's
    # name for this bottle, and these four sites are its only compiled uses
    # (every tier build_eusecode.py reads, grepped 2026-10-09), so the
    # re-point moves nothing else:
    #   - EZREKAL.UNK (lv-patched) give(Avatar:Referent,TypeBottle:Type,
    #     0:Frame,0,1) — Ezrekal hands the brewed elixir to the Avatar
    #     (quest step 11).
    #   - EZREKAL.UNK (lv-patched) createNear(myMan,TypeBottle:Type,
    #     0:Frame,0,1) — drop fallback if the give fails.
    #   - TYORVI.UNK (lv-patched) `foreach recursive item where (type =
    #     TypeBottle) and (frame = 0) within container Avatar { destroy }`
    #     — Tyorvi drinks the elixir (the "give it to me" path).
    #   - TYORVI.UNK (lv-patched) the same foreach on the "shut up and
    #     drink it!" path.
    # TypeTankard has since had its audited pass (178, above); TypePotion
    # and TypeTinytar too — see below.
    # Deliberately NOT retail (2026-10-07 audit): retail JENNA 0x0418 gives
    # TypeBottle as `0B B4 00` (180, class BOTTLE) @10E7. JENNA is not
    # recompiled, so that site keeps 180; 180 lends 868 its TYPEFLAG row.
    'TypeBottle':          868,  #LV: Tyorvi's elixir (custom art, frame 0)

    # ── Potions ──
    # BOTH FIXED 2026-07-27 (DD-005, the Tiny Tar temple entry). They were
    # both 340, which is not a potion at all: usecode class 340 is
    # TDOOR_NS — one leaf of the Lost Vale double doors (see
    # lv_shapes.SHAPE_LV_DOORS). The consequences were different for each:
    #
    #   TypePotion  -> 766, engine name "potion", 8 frames (0-7), the shape
    #     build_map_10.py already places on Ezrekal's shelf as
    #     SHAPE_POTION_REAL. Only value-use is MAGNET.UNK's two
    #     `foreach ... type = TypePotion` inventory sweeps, which were
    #     therefore hunting for a DOOR and would never have magnetised a
    #     potion. (MAGNET is not wired yet; this makes it correct for when
    #     it is.)
    #
    #   TypeTinytar -> 708. This one was actively dangerous. Its only
    #     value-use is FREE.UNK:1331 `Avatar.setType(TypeTinytar)` in
    #     makeAvatarTiny() — so drinking Tiny Tar would have set the
    #     AVATAR's shape to a door: footpad (1,4,10) = 32x128x80 against
    #     the Avatar's (2,2,5) = 64x64x40, i.e. TWICE AS TALL and twice as
    #     deep — the shrink potion made you BIGGER — with only 3 frames
    #     where the code immediately does setFrame(60)..(69), and family
    #     SF_QUALITY rather than SF_CONTAINER, so the quality word would be
    #     read as a door lock id and inventory would break.
    #
    # 708 is not a guess. Scanning all 2048 TYPEFLAG entries for footpad
    # <= (1,1,4) with >= 70 frames yields five shapes, four of which are
    # weapons; 708 is the only actor. It is the base game's child actor
    # (engine name "dead child", but 707/708 are the generic peasant/child
    # actor shapes — build_map_10.py already uses it for the village
    # children): footpad (1,1,4) = 32x32x32, family SF_CONTAINER so
    # inventory survives the swap, 100 frames so 60-69 exist.
    #
    # INTERIM ART (Douglas, 2026-07-27): a child is a stand-in, not a
    # miniature Avatar. The real 1994 tiny-Avatar art — a 10-frame shrink
    # ramp at frames 60-69 — does NOT survive in retail U8; a scan of every
    # shape for a descending-height sequence at those frames found only
    # frames collapsing to 1px, never a scale ramp. A bespoke sprite is on
    # the art list; this makes the mechanic work meanwhile.
    # 766 -> 859 on 2026-07-27, the last step of DD-005. POTION.UNK::use()
    # branches on frames 0-8, but the base game's potion (766) has only
    # frames 0-7 — the expansion's ninth frame, TINY TAR, did not survive.
    # 859 is a 9-frame copy built by agents/map-populator/src/lv_tiny_tar.py
    # (frames 0-7 re-encoded unchanged, frame 8 = frame 1 with its 36 liquid
    # pixels recoloured onto the palette's warm dark ramp) and injected as a
    # step of tools/build_artifacts.sh so it survives artifact rebuilds.
    # Without this the Map 18 crack seals the Inner Sanctum against every
    # possible player, because nothing can shrink the Avatar.
    'TypePotion':          859,  #LV: 9-frame potion; frame 8 = Tiny Tar

    # TypeAvatar ADDED 2026-07-27 (DD-005). It was never in this table, so
    # all four 1994 uses compiled to `push 0` — and they are the RETURN half
    # of the shrink:
    #   FREE.UNK:1410  Avatar.setType(TypeAvatar)  — grow back
    #   FREE.UNK:1380  canExistAt(TypeAvatar, x,y,z, ...) — the lethal
    #                  "would a full-size body fit here?" test
    # With push 0 the first would have set the AVATAR'S SHAPE TO 0 (no
    # sprite, no footpad, no shape info) when the potion wore off, and the
    # second would have asked whether shape 0 fits — deciding life or death
    # on a meaningless answer. Unreachable until today only because no
    # frame-8 potion existed to drink.
    #
    # The Avatar is shape 1 in U8: its usecode dispatches on objId + 1024
    # (class 1025 AVATAR), not on shape, so this value is used purely as a
    # shape id here and is safe.
    'TypeAvatar':          1,    #LV: the Avatar's own shape (grow-back target)
    # 708 -> 867 on 2026-10-08 (Douglas; docs/reviews/2026-09-30-four-
    # anomalies.md §1). setType() swaps the Avatar's OWN shape, and an Actor
    # is a Container that reads its weight and capacity from that shape's
    # TYPEFLAG row (container.cpp:219-245): on 708 the pack read weight 520
    # against capacity 200, and every pickup/equip was checked against
    # those. 708 is also two placed village children, so its row could not
    # be patched in place. 867 is a clone of 708 in U8SHAPES (all 100
    # frames, so 60-69 exist), TYPEFLAG (footpad (1,1,4), family
    # SF_CONTAINER) and ANIM.DAT (the engine keys actor animation by shape),
    # with shape 1's weight 1 / volume 250 — built by
    # agents/map-populator/src/lv_tiny_avatar.py, build_artifacts.sh step 6.
    # Still the child's art; a bespoke sprite keeping 708's frame layout
    # can now replace 867's frames without touching anything else.
    'TypeTinytar':         867,  #LV: the shrunken Avatar (708 clone, own slot)

    # ── Quest Items ──
    # TypeAOFrizbee/TypeAOArtifact FIXED 2026-07-19 (the SI_FIXED trap, 4th
    # occurrence — after the talismans -> 596, the Passage Stone -> 798 and
    # the keys -> 82): 580 is TYPEFLAG SI_FIXED, so the Shield of the
    # Ancients and its two halves were UNPICKABLE SCENERY. This is the
    # central quest object of steps 13-15 (find the broken halves, restore
    # the Shield at the ceremony, place it on the Temple altar), so the
    # arc could not be completed at all.
    #
    # Now 539 "shield": carryable (not SI_FIXED), weight 33, and crucially
    # equipType 1 = the shield paperdoll slot with 4 frames present, which
    # is what the 1994 source actually requires:
    #   - ZEALSHLD.UNK:15/:19 TypeAOFrizbee::look() branches on
    #     getFrame() = 2 and = 3.
    #   - ZEALSHLD.UNK:121 TypeAOFrizbee::equip() branches on
    #     getFrame() = 3 and equips to the shield slot.
    #   - AOSCENE.UNK:42 `foreach recursive item where
    #     (type = TypeAOArtifact) within container Avatar` — an inventory
    #     search, which an SI_FIXED shape can never satisfy.
    # RE-POINTED 539 -> 870 on 2026-10-11 (art track contract 10): the
    # halves are custom art, retail 828 split in two (lv_shapes.
    # SHAPE_SHIELD_HALVES, frames 0/1), on 828's TYPEFLAG row, which is no
    # equip-slot item. At 539 any Pagan shield of frame 0 passed SHADES's
    # half-1 check. Compiled consumers: lv-patched/SHADES.UNK:138 (the
    # backpack search, frames 0/1) and :440 (the frame-4 anchor, a frame
    # 870 lacks, destroyed at once). MUST stay equal to SHAPE_SHIELD_HALVES
    # (build_map_17 places the halves); test_art_props asserts the pair.
    # RE-POINTED 870 -> 878 on 2026-10-17 (phase C, Map 17): the halves are
    # the 1994 art cut from the screenshots (sun half frame 0, eye half
    # frame 1, 870's order), on the same 828 TYPEFLAG row, and placed where
    # screen11/screen12 show them. 878 has two frames too, so the frame-4
    # anchor still names a frame the shape lacks. 870 is no longer a
    # halves type: since 2026-10-17 it is 878's legacy alias
    # (lv_shapes.SHAPE_SHIELD_HALVES_LEGACY, a copy of 878's frames and
    # TYPEFLAG row, never placed), kept so an old save's halves open in
    # the pack. SAVE COMPATIBILITY: saves made before 2026-10-17 hold the
    # halves as 870 or 539 (frame 0 q81, frame 1 q82). lv-patched/SHADES.UNK
    # (header note 9) and lv-new/REAPPLY.UNK fall back to those by LITERAL,
    # not by a TYPE_SHAPES name: no entry may resolve to 870
    # (test_art_props section 14) and 539 is retail's SHIELD, a half only
    # at those qualities.
    'TypeAOFrizbee':       878,  #LV: Shield of the Ancients halves (1994 art)
    # TypeAOArtifact RE-POINTED 539 -> 828 on 2026-10-08 (Douglas: the
    # restored Shield is 828, "Zealan ceremonial shield"). Retail evidence:
    # class 828 is AORTA (look() "Zealan ceremonial shield "), and retail
    # ANCTONES 0x048B searches for 828 near its egg (`0B 3C 03` @009A);
    # Pagan places two (U8SAVE.000 NONFIXED, Maps 8 and 54).
    # NO LONGER THE RESTORED SHIELD since 2026-10-17: that is
    # TypeSacredShield (879, below), and SHADES and AOSCENE moved to it.
    # The one remaining compiled consumer is lv-patched/ATLI.UNK's 1994
    # `(type = TypeAOArtifact) and (frame = 0)` "I have this shield!" ("I
    # got this in the Shrine of the Ancients"), which Douglas decided
    # (2026-10-09, ATLI change 5) is offered for Pagan's own 828 and not
    # for the restored Shield; with the Shield on 879 that now holds by
    # type, and ATLI's getQ() != 83 guard is redundant but kept as written.
    # SAVE COMPATIBILITY: saves made before 2026-10-17 between the ceremony
    # and the altar carry the Shield as 828 quality 83, so AOSCENE's altar
    # also accepts a TypeAOArtifact at quality 83 (Pagan's are quality 0),
    # and lv-new/AORTA.UNK, which replaces retail class 828, still gives it
    # the 1994 look() text. 828 is carryable (no SI_FIXED), one frame,
    # equipType 0.
    'TypeAOArtifact':      828,  #LV: Pagan's Zealan ceremonial shield (ATLI's look-alike)
    # TypeSacredShield, 2026-10-17: the restored Shield of the Ancients is
    # the 1994 art, lv_shapes.SHAPE_SACRED_SHIELD_1994 (879), built by
    # lv_art_props on 828's TYPEFLAG row (footpad 1x3x3, carryable,
    # SF_GENERIC). screen04 shows it on the sanctum altar; EZREKAL's forgery
    # speech says Pagan's 828 is "the same shape ... and the wrong symbols";
    # and the Map 17 halves are already the 1994 art 878 (sun + eye), which
    # reassemble 879's 608/609 px. Compiled consumers: lv-patched/
    # SHADES.UNK creates it (TypeSacredShield, 0) with setQ(83);
    # lv-new/AOSCENE.UNK's altar search takes it (and still tests q83)
    # and pops it onto the altar top. Its look() is class 879,
    # lv-new/SACSHLD.UNK (class = shape, item.cpp:1516), pinned
    # TYPESACREDSHIELD in lv_manifest.json. MUST equal
    # SHAPE_SACRED_SHIELD_1994.
    'TypeSacredShield':    879,  #LV: Shield of the Ancients, restored (1994 art)
    'TypeMonskul':         189,  #LV: Monster Skull (bone decoration shape)
    # TypeZealanGod: CUSTOM ART, not a base-game shape. Six frames — 0/1/2
    # the three gods sealed in amber, 3/4/5 the same three freed — injected
    # by agents/map-populator/src/lv_god_statues.py. AOSCENE and TEMPLENT
    # foreach over this to swap frame n -> n+3 at the ceremony.
    # MUST stay equal to lv_shapes.SHAPE_GOD_CRYSTAL, which is what
    # build_map_18 places; test_sanctum_clearance.py asserts the pair.
    # SI_FIXED here is FINE and is not the trap that caught TypeAOArtifact:
    # that one failed on `within container Avatar`, an inventory search a
    # fixed shape can never satisfy. These are searched `within N of
    # referent` in the map, the same as TypeElementalColumn (COLPUZZL:139).
    'TypeZealanGod':       860,  #LV: Zealan god in amber (custom art)
    # RE-POINTED 721 -> 865 on 2026-09-24 (art track contract 5): the pillars
    # are custom art now (lv_shapes.SHAPE_ELEMENTAL_PILLAR, four frames), and
    # COLPUZZL.UNK:139 compiles THIS number into the search that destroys a
    # pillar, so it MUST equal what build_map_11 places; test_art_props
    # asserts the pair. The one live re-point on the track: everything else
    # that resolved to 721 (TypeStatue, TypeWoodThrone, TypePedestals) is
    # dead in the compiled corpus (audited 2026-09-22, contract 5).
    'TypeElementalColumn': 865,  #LV: elemental pillar (matches map pillar shape)
    # TypeTalisman/TypeTokens FIXED 2026-07-04 (in-game): 580 is TYPEFLAG
    # SI_FIXED — placed talismans could not be picked up, dead-ending the
    # column puzzle at step one. Now 596 "gemstone ring" (carryable, frames
    # 0-3 = element identity), matching lv_shapes.SHAPE_TALISMAN_GEM and the
    # Map 11 placements. Consumers: COLPUZZL's inventory search and LVFREE's
    # TypeTokens counting (makeAgent) — both must equal the placed shape.
    'TypeTalisman':        596,
    'TypeTokens':          596,
    'TypeSealingBoulder':  66,   #LV: solid boulder (FIXED|SOLID, footpad 4x4x5)
                                 # plugging the Map 11 pillar-chamber doorway;
                                 # COLPUZZL destroys quality-299 instances only
                                 # (66 is also ambient rubble on LV maps)
    # The Map 18 breach (2026-09-26): the sanctum wall's 128-wide piece
    # (lv_shapes.SHAPE_GLOB_WALL_PIECE) and its 64-wide stub. TEMPLENT and
    # CRACKHNT destroy only instances carrying build_map_18.BREACH_QUALITY
    # (307); both shapes build every temple wall line.
    'TypeTempleWallPiece': 15,
    'TypeTempleWallStub':  47,
    # NOTE 2026-07-04: 'TypePassageStone' is DEAD in the compiled corpus
    # (grep of LOST VALE/, UNK files/UNK/ and lv-new/ finds no value
    # reference — the 1994 sources call the Passage stone TypeBushKey,
    # fixed above). Aligned from 580 to 798 anyway so the next reader
    # doesn't inherit the SI_FIXED trap from a stale entry.
    'TypePassageStone':    798,  #LV: test passage stone (dead entry; see note)
    # FIXED 2026-10-07 (retail audit): was 580 (SI_FIXED scenery). AVATAR
    # 0x0401 :1177 createNear(myMan,TypeObsidianCoin,0,0,200) pushes
    # `0B 8F 00` @3584; retail ABACUS 0x0177 (ABACUS.UNK:21's search) is
    # 143 @00C8. Class 143 is COINS (SF_QUANTITY).
    'TypeObsidianCoin':    143,

    # ── Magic & Effects ──
    'TypeMagicCandle':     295,  # candle/torch shape
    # FIXED 2026-10-07 (retail audit): was 73 (any egg). AVATAR 0x0401 :338
    # `(type = TypePentagramBase) and (frame = 2)` is shape 124, frame 2
    # @0E3A (class PENT).
    'TypePentagramBase':   124,
    'TypeMagicWallNS':     489,  # stone wall
    'TypeMagicWall2NS':    490,
    # FIXED 2026-10-07 (retail audit): was 73. AIRSPEL 0x0596 :512 and :882
    # magic2.create(TypeMagicYellowCircle,0) are create 202 @0FA6, @223D
    # (interleaved in source order with the 587 sparkle creates).
    'TypeMagicYellowCircle': 202,
    # FIXED 2026-07-03 (TYPE_SHAPES trap #5, shared/docs/wiring.md "Quest
    # step 1: LORDBRIT"): was 73 (the invisible SF_UNKEGG egg shape — dead
    # wrong for a VISIBLE sparkle VFX). Proven correct value 587 from
    # RETAIL bytecode: base STRATOS.UNK source says
    # `magic.create(TypeMagicSparkle, 11)`, and the shipped STRATOS class
    # (0x181, offset 149C) compiles that call as `push byte 11; push
    # 024Bh; Item::create` — 0x24B = 587. Only consumer in the corpus is
    # LORDBRIT.UNK (blue/yellow/red sparkle .create() calls); no other
    # compiled source references TypeMagicSparkle as a value.
    'TypeMagicSparkle':    587,
    # The next five FIXED 2026-10-07 (retail audit); 435/436 are the floor
    # trap-burst shapes our maps place (lv_shapes.SHAPE_TRAP_BURST_A/B),
    # 580 is fixed scenery.
    #   TypeFireField 400 FIREFELD: AVATAR 0x0401 :1276 search 400 @3840;
    #     METHOD 0x057C :498 search 400 @0809.
    #   TypeFireGlobe 703 FIREGLOB: AVATAR :1247 search 703 @37B5.
    #   TypeFrictionGrenade 592 FGRENADE: ARAMINA 0x040D :563 search @1049.
    #   TypeBlackrockFragments 442 BROCK: AVATAR :160-164 legal_create
    #     `0B BA 01` @04AD (frames 0-4); STRATOS 0x0181 :101 search @040A;
    #     PYROS 0x006D create 442 frame 4 @46F1 (FREE.UNK:1356).
    #   TypeEnergizedBlackRock 793 EBROCK: AVATAR :168-172 legal_create
    #     `0B 19 03` @062B (frames 0-4).
    'TypeFireField':       400,
    'TypeFireGlobe':       703,
    'TypeFrictionGrenade': 592,
    'TypeEnergizedBlackRock': 793,
    'TypeBlackrockFragments': 442,

    # ── Elemental Items ──
    # FIXED 2026-10-07 (retail audit); all were 580 (fixed scenery) or 435.
    #   TypeEarthItem 746: no retail source use; class ERTHITEM ("Death
    #     Speak"/"Mask of Death"/"Rock Flesh"), the earth foci. Name-pinned.
    #   TypeEarthReagent 395 ERTHREAG: AVATAR 0x0401 :1168-1172 createNear
    #     frames 6/15/10/0/16 push `0B 8B 01` @34EB..@3537, same frames.
    #   TypeFireItem 397 FIREITEM: AVATAR :205 createNear(point,TypeFireItem,
    #     20,0,4) `0B 8D 01` @089C; METHOD 0x057C :928 getType = 397 @1103;
    #     AIRSPEL 0x0596 :650 getType = 397 @1612.
    #   TypeFireblast 480 / TypeLightning 511: MORDEA 0x0407 :1269
    #     lightning.create(TypeLightning,0) `0B FF 01` @2670 and :1281
    #     fire.create(TypeFireblast,0) `0B E0 01` @2702. TypeLightning was
    #     missing, so FREE.UNK:1908 created shape 0.
    #   TypeAirFocus 396 AIRFOCUS: STRATOS 0x0181 :554 create(...,13) @14DF;
    #     TORWIN 0x041A :1325 create(...,9) @337C.
    'TypeEarthItem':       746,
    'TypeEarthReagent':    395,
    'TypeFireItem':        397,
    'TypeFireblast':       480,
    'TypeLightning':       511,
    'TypeAirFocus':        396,
    'TypeAirTitan':        400,  # NPC shape for creature
    # FIXED 2026-10-07: was 400, which is the FIREFELD fire field (retail
    # class 0x190: its anim()/gotHit() burn overlapping NPCs, and it has
    # only 30 frames). PLNTST's Passage Test popped five fire fields and
    # stepped them to frames 25-34, burning Thordis to 8 of 20 hp and
    # leaving her in combat with the Avatar. Proven 481 from RETAIL
    # bytecode: STRATOS.UNK's `item.create(TypeMiniAirTitan,0)` compiles
    # in the shipped class 0x181 at 0164 as `push 01E1h; Item::create`,
    # and class 0x1E1 is MINIAIR (36 frames, look/use only).
    'TypeMiniAirTitan':    481,

    # ── Furniture & Props ──
    # Lever/WallSwitch/PathMarker/WoodThrone/BarCounter FIXED 2026-10-07
    # (retail audit):
    #   TypeLever 672 LEVER / TypeWallSwitch 505 WALLSWIT: AIRSPEL 0x0596
    #     :611 getType = 672 @1420, = 505 @142E. (295 is lv_shapes.SHAPE_TORCH.)
    #   TypePathMarker 174: ARAMINA 0x040D :225/:236/:445/:456 search
    #     `0B AE 00` @0470, @04B1, @0BCB, @0C0C; AVATAR 0x0401 :1057
    #     create `0B AE 00` @306A; 102 retail search/getType sites use 174
    #     (THURGIST, LITHOS, GUARDMAN, every scheduled NPC). Shape 174 is
    #     SF_QUALITY with 30 frames (the frame is the route step); 73 is
    #     the UNKEGG egg.
    #   TypeWoodThrone 223 WTHRONE: MORDEA 0x0407 :892 search @1A84, :897
    #     create @1AB4. TypeBarCounter 160: JENNA 0x0418 :192/:197 search
    #     @03F7/@042C.
    'TypeLever':           672,
    'TypeWallSwitch':      505,
    'TypePathMarker':      174,
    'TypeStatue':          721,  # pillar/statue
    # RE-POINTED 126 -> 871 on 2026-10-11 (art track contract 13): the
    # Passage Test plant is custom art (lv_shapes.SHAPE_TEST_PLANT). 126 was
    # a blue-crystal ground tile. Compiled consumers: lv-patched/PLNTST.UNK
    # :72 (destroy, frame 0) and its five creates, lv-new/REAPPLY.UNK:99
    # (quality 10, frame 0). MUST equal what build_map_10 places.
    'TypeShortmushroom':   871,  #LV: the Passage Test plant (custom art)
    'TypeWoodThrone':      223,
    'TypePedestals':       721,
    'TypeBarCounter':      160,
    'TypeAbacus':          158,  #LV: modified abacus (book placeholder)
    'TypeBedroll':         225,  #LV: bedroll (backpack placeholder)

    # ── NPCs & Creatures ──
    # FIXED 2026-10-07 (retail audit; Salkind/BlackStag are dead entries):
    #   TypeSalkind 404: MORDEA 0x0407 :1208 search `0B 94 01` @249B.
    #   TypeDemon 96 DEMON: AVATAR 0x0401 :565 search 96 @1787.
    #   TypeSorcerer 200: METHOD 0x057C :989 `mage.getType() = TypeSorcerer`
    #     is getType = 200 @12A1 (= lv_shapes.SHAPE_NPC_SORCERER).
    #   TypeBlackStag 152: TORWIN 0x041A :1435 getType `0B 98 00` @37EC.
    #   TypeWoundedTorax 209 WOUNDTOR: STELLOS 0x0417 :1559 create @44C9;
    #     AIRSPEL 0x0596 :479/:846 getType = 209 @0E12/@2073.
    # TypeGhoul/TypeSkeleton (dead) keep 400: no retail source use.
    'TypeSalkind':         404,
    'TypeShades':          411,  #LV: the Hoskuld/Gunnar shades, SHADES.UNK
                                 #    shadeTalk() create(TypeShades, 0/1).
                                 #    Was 73 (the invisible egg shape — the
                                 #    ceremony spirits never rendered); 411
                                 #    is the engine's `ghost` shape, frames
                                 #    0/1 verified non-empty sprites
                                 #    (art audit 2026-07-19 §E, applied
                                 #    2026-07-27 with the EGGSHADES wiring).
                                 #    Only SHADES.UNK references this name.
    'TypeDemon':           96,
    'TypeGhoul':           400,
    'TypeSkeleton':        400,
    'TypeSorcerer':        200,
    'TypeBlackStag':       152,
    'TypeWoundedTorax':    209,
    # FIXED 2026-07-27 with TypeTinytar above (DD-005): this is the SAME
    # thing under its earlier 1994 name. The dev-tier copies of the shrink
    # code (UNK files/UNK/FREE.UNK:1331 and CHANGTAR.UNK:25 — the scratch
    # file the routines were drafted in, headed "Stick these in FREE.UNK")
    # say TypeTinyAvatar where the final LOST VALE/FREE.UNK says
    # TypeTinytar. Both must resolve to the same shape or the dev tier
    # would shrink the Avatar into a 30-frame fire-field effect. See the
    # TypeTinytar comment for why 708, and why 867 since 2026-10-08.
    'TypeTinyAvatar':      867,  #LV: alias of TypeTinytar (earlier 1994 name)
    'TypeZealanChild1':    400,  #LV: Zealan child NPC
    # FIXED 2026-07-03 (TYPE_SHAPES trap #4, shared/docs/wiring.md "Quest
    # step 1: LORDBRIT"): was 400 ("fire field" per the audit note above —
    # not an apparition). Adopted placeholder: shape 411 "ghost" (201
    # frames in U8SHAPES.FLX, covers the puppet animation's frames 0-9).
    # The real LB art stays on the art-placeholder-audit list. Only
    # consumer in the corpus is LORDBRIT.UNK's own `foreach item where
    # type = TypeLordBritish within 1024 of Avatar` filter — this value
    # MUST match the shape actually placed for the apparition item in
    # FIXED.DAT (agents/map-populator/src/lv_shapes.py SHAPE_LB_APPARITION)
    # or the scene's foreach never finds it and `lb` stays null.
    'TypeLordBritish':     411,  #LV: LB vision apparition (ghost placeholder)
    # 871 since 2026-10-11 with TypeShortmushroom: the 1994 name of the same
    # plant (TESTPLAN.UNK). Evaluated as a value nowhere in the compiled tree.
    'TypePoisonPlant':     871,  #LV: the Passage Test plant (custom art)
    'TypeEaLogo':          158,  #LV: EA logo (book placeholder)

    # ── Misc ──
    # FIXED 2026-10-07 (retail audit): was 580. AVATAR 0x0401 :1164
    # createNear(myMan,TypeRecallItem,0,0,1) pushes `0B 41 03` @34B2;
    # class 833 is RECALL.
    'TypeRecallItem':      833,
    # TypeWeedz RE-POINTED 399 -> 869 on 2026-10-11 (art track contract 12):
    # the special root is custom art, one frame (lv_shapes.SHAPE_SPECIAL_
    # ROOT), on donor 180's TYPEFLAG row, with class 869 (lv-new/SPROOT.UNK)
    # barking "special root". Before that it was 399 "eye of newt" frame 9
    # (from 2026-07-05; a vine that read as a snake, drawn translucent by
    # 399's SI_TRANSL), and 126 before that, SI_FIXED scenery no container
    # could hold. Consumers in the compiled corpus, both FRAME 0 since
    # lv-patched/EZREKAL.UNK R2:
    #   - EZREKAL.UNK:364 (original line) `foreach recursive item where
    #     (type = TypeWeedz) and (frame = 0) within container Avatar`, the
    #     menu-detect that offers "I have found the root." (quest step 10).
    #   - EZREKAL.UNK:3168 the same foreach in the "I have found the root."
    #     case, which destroys the root on hand-in.
    # This value MUST equal the root build_map_10 places
    # (lv_shapes.SHAPE_SPECIAL_ROOT, frame 0) or the root can never be found.
    'TypeWeedz':           869,  #LV: the special root (custom art, frame 0)
    'TypeUnkEgg':          73,   # retail TORWIN 0x041A :1436 getType = 73 @37F3
    'TypeNSGoldPlaque':    158,  #LV: gold inscription (book shape)
}


# ─── snddefs SFX constants ─────────────────────────────────────────────────
# The 1994 sources import SFX names from a `uses "snddefs"` header that was
# NOT in the recovered snapshot, so these identifiers compiled as `push 0`
# (silent SFX 0) until 2026-07-04.
#
# RECOVERED via SOUND.FLX: entry 0 of the retail SOUND/SOUND.FLX is the
# original fixed-width (8-byte) sample-name table, and
#   sound number = name-table record index + 1.
# That law was proven by 20+ independent source-to-retail bytecode matches
# (e.g. MORDEA.UNK `spawn safePlaySFX(LTNING1A,100)` x3 <-> retail MORDEA
# 0x0407 spawn 0581:29D8 args(100,6); STRATOS.UNK's 7-call playSFX sequence
# matching retail 0x0181 positionally 7-for-7; AVATAR.UNK 4-for-4). See the
# 2026-07-04 SFX-recovery report referenced in shared/docs/wiring.md.
#
# This table is the complete 220-name namespace, regenerated verbatim from
# SOUND.FLX entry 0 (all-caps names, exact-match lookup only — see
# SymbolTable.get_snd_constant). If it ever needs regenerating:
#   names = FlexArchive('SOUND.FLX').get_object(0)  # 8 bytes per record
#   SND_CONSTANTS[name_at(i)] = i + 1

# ── Equip-slot constants (EQ_*) ───────────────────────────────────────────
#
# The 1994 sources reference EQ_SHIELD/ARM/HEAD/BODY/LEGS/BACKPACK but the
# snapshot never included the header that defines them, so they compiled as
# `push 0` until 2026-07-19.
#
# RECOVERED from the engine, not guessed. Three links:
#   1. gfx/type_flags.cpp:86 — U8's 8-byte TYPEFLAG entries store the slot as
#      `si._equipType = data[2] & 0x0F`.
#   2. gumps/paperdoll_gump.cpp:48 — the `equipcoords[]` table names each
#      _equipType in order: 1 shield, 2 arm, 3 head, 4 body, 5 legs,
#      6 weapon; and `getEquip(7)` is the backpack (paperdoll_gump.cpp:398,
#      actor.cpp:429).
#   3. world/actors/actor.cpp:2756 — the intrinsic OFFSETS BY ONE:
#      `return actor->getEquip(type + 1);`. Corroborated on the write side by
#      I_setEquip's assertion (actor.cpp:2770):
#      `item->getZ() == type + 1 || (shape == BACKPACK_SHAPE && type == 6)`.
#
# So the usecode-side value is engine _equipType minus one.
#
# CAUTION when reading old emission: EQ_SHIELD is 0, which is exactly the
# unresolved-identifier fallback. That made the shield branch accidentally
# correct while silently ALIASING every other slot onto the shield — most
# consequentially EQ_BACKPACK (6), referenced by the shipping base-class
# replacements LOST VALE/FREE.UNK and LOST VALE/MAGNET.UNK.
EQ_CONSTANTS = {
    'EQ_SHIELD': 0,
    'EQ_ARM': 1,
    'EQ_HEAD': 2,
    'EQ_BODY': 3,
    'EQ_LEGS': 4,
    'EQ_WEAPON': 5,
    'EQ_BACKPACK': 6,
}

# Map-number constants from the 1994 headers, which were not recovered.
# Every value below is PINNED against retail bytecode (2026-07-27, Fix 2a),
# never guessed — the fallback for an unlisted Map* name is the loud
# unknown-identifier warning, and that is the correct behavior for the
# three names deliberately left out (MapFishermansReef, MapShepherdValley,
# MapEastRoad: retail AIRSPEL's case chain has 6 entries before the first
# anchor where the source lists 4-5, so their alignment is ambiguous).
#
# Evidence, by method:
#  * storms-chain: retail AVATAR::schedule's 19-literal cmp chain aligns
#    1:1 in order with the 19-name storm-suppression list at
#    AVATAR.UNK:1317-1325, with two independent end/mid anchors:
#    MapLBBlackness = 0 (the observed LB-vision teleport target) and
#    MapPlaneOfEarth47 = 47 (the name encodes the number).
#  * needle: a teleport's coordinate literals locate the same call in
#    retail bytecode; the adjacent map literal is the value.
#    MapDaemonsCrag: teleport(17382,19549,56,·)→12 AND recall "Pyros"
#    (19751,16172,56,·)→12. MapDocks: recall "Execution"
#    (11619,3170,48,·)→3 (also the observed new-game start map).
#    MapArgentrockIsle: recall "Stratos" (14787,19195,56,·)→37.
#  * airspel-suffix: retail AIRSPEL's getMap case chain, from
#    MapBrimstoneCliffs on, aligns 1:1 with the source case list at
#    AIRSPEL.UNK:52-263 (5 anchor hits: 15,14,28,31,37; the LavaRiver
#    pair lands consecutively at 24,25); the chain tail ...37,39,40,41
#    reads off West/Central/EastTenebrae.
#  * context: MapLostVale = 10 is the one non-retail pin. Every use is a
#    Hoskuld-village NPC or scene (SHADES/THORDIS/HRODNY/INGYALD),
#    EggShades is placed on map 10, and TODO.md's TESTPLAN note
#    independently treats SHADES-adjacent 1994 coordinates as map-10
#    coordinates.
# Process-type constants from the 1994 headers (not recovered). PINNED
# against retail bytecode + engine source (2026-08-12), never guessed —
# unlisted PT_* names (PT_FX, PT_USE, PT_LOOK, PT_ANIM_UNK, PT_UNKHATCH,
# PT_GOT_HIT — 17 corpus sites total) fall through to the loud
# unknown-identifier warning until someone pins them the same way.
#
# Evidence, two independent lines that agree:
#  * sequence: the 1994 canonical kill block is
#      resetRef(referent,PT_ACTIVITY); ...PT_PATHFIND; ...PT_ANIM; ...PT_BARK
#    (ZCHILD.UNK:15-18, TJORVI.UNK:72-75, and variants). Retail bytecode
#    contains the compiled counterpart as a 4-in-a-row resetRef run with
#    immediates 0205, 0204, 00F0, 0200 in that order — 33 occurrences —
#    plus the 3-call variant (0204, 00F0, 0200 = TYORVI.UNK:107-109's
#    PATHFIND/ANIM/BARK block) 34 more times.
#  * engine: each value is a Process subclass's _type constant in ScummVM:
#    0x205 LoiterProcess (the default NPC activity), 0x204
#    PathfinderProcess (pathfinder_process.h:59), 0x00F0 ActorAnimProcess
#    (actor_anim_process.h:46), 0x200 GumpNotifyProcess (a bark gump's
#    completion process, gump_notify_process.cpp:38).
# PT_DEFAULT = 1 matches PRAGMA_TYPES in u8c_codegen.py (the statement-form
# pragma path), pinned there 2026-07-27; listed here so an expression-
# position use agrees with the pragma value.
# Shape-family constants from the 1994 headers, which were not recovered.
# PINNED against the engine enum, not guessed: ShapeInfo::SF_* in
# scummvm-lv-console/engines/ultima/ultima8/gfx/shape_info.h, which is the
# same numbering TYPEFLAG stores and `Item::getFamily()` returns.
#
#   SF_GENERIC 0  SF_QUALITY 1  SF_QUANTITY 2  SF_GLOBEGG 3  SF_UNKEGG 4
#   SF_BREAKABLE 5  SF_CONTAINER 6  SF_MONSTEREGG 7  SF_TELEPORTEGG 8
#   SF_REAGENT 9
#
# WHY THIS MATTERS (found 2026-09-02, in-engine, on the exit test's critical
# path). Every one of these names compiled to `push 0` — the unresolved
# identifier fallback — so FREE.UNK:274's guard
#
#     if item.getFamily() != CONTAINER_FAMILY { return false; }
#
# read `getFamily() != 0`. The Avatar is SF_CONTAINER = 6, so the guard was
# true for him and `give()` returned at its first instruction, every time,
# for every caller. Disassembly of the shipped EUSECODE confirms it:
# class 05AE offset 03B3 emits `push byte +0` where the 6 belongs.
#
# Three quest hand-overs died silently on this, all using the same
# `if give(...) {} else if createNear(...) {}` idiom: the Zealan Mark
# (PLNTST), Ezrekal's elixir bottle, and Tyorvi's Key to the Clouds. The
# Key is the blocker — CLCLIMB.UNK:51 gates the cliff climb on the ITEM
# (`foreach recursive item where (type = TypeCliffKey) within container
# Avatar`), so the Cloud City, the poison cure and the endgame all sat
# behind a constant that was zero. `take()` (FREE.UNK:363) carries the
# identical guard and was equally dead.
FAMILY_CONSTANTS = {
    'GENERIC_FAMILY':     0,
    'QUAL_FAMILY':        1,
    'QUAN_FAMILY':        2,
    'GLOBEGG_FAMILY':     3,
    'UNKEGG_FAMILY':      4,
    'BREAKABLE_FAMILY':   5,
    'CONTAINER_FAMILY':   6,
    'MONSTEREGG_FAMILY':  7,
    'TELEPORTEGG_FAMILY': 8,
    'REAGENT_FAMILY':     9,
}

PT_CONSTANTS = {
    'PT_DEFAULT': 0x001,
    'PT_ANIM': 0x0F0,
    'PT_BARK': 0x200,
    'PT_PATHFIND': 0x204,
    'PT_ACTIVITY': 0x205,
}

# Day-period constants from the 1994 headers (not recovered). PINNED against
# retail bytecode (2026-08-12): retail class 0x00E3 (a clock) calls
# FREE::getPeriod (call 0581h:28F9h) six times and compares the result
# against literals 0..5, each comparison's match arm concatenating the
# period's own display name — "Bloodwatch." for 0, "FirstEbb." for 1,
# "DayTide." for 2, "ThreeMoons." for 3, "LastEbb." for 4, "EvenTide." for
# 5 (offsets 0x180-0x258). Needle-grade: every value is labeled by its own
# string. The names below use the 1994 source spelling (AIRSPEL.UNK:282-307
# switches on getPeriod() with these exact identifiers, in an order
# consistent with these values).
DAY_PERIOD_CONSTANTS = {
    'bloodwatch': 0,
    'firstebb': 1,
    'daytide': 2,
    'threemoons': 3,
    'lastebb': 4,
    'eventide': 5,
}

# NPC schedule-state constants from the 1994 headers (not recovered). Until
# 2026-10-07 every one compiled to `push 0`, so ARAMINA's enterFastArea
# could not tell at_home from chow_down from on_throne. PINNED against the
# retail shared/data/USECODE.FLX (NOT u8-install/USECODE/EUSECODE.FLX,
# which is our installed build). Retail pushes byte literals:
#   - ARAMINA 0x040D, the very class these names serve, global 0207h
#     (araminaSchedule, 2 bits): enterFastArea() compares at_home /
#     chow_down / on_throne as `0A 01` @0219, `0A 03` @0231, `0A 02`
#     @0245 (source order :105/:111/:117); AvatarStoleSomething()
#     `!= at_home` is `0A 01` @02DE; use() `= at_court or = chow_down`
#     is `0A 02` @11C8, `0A 03` @11CF.
#   - MORDEA 0x0407 schedule() stores araminaSchedule (0207h) from `0A 01`
#     @026E, `0A 02` @041E, `0A 03` @05C4 (U8/MORDEA.UNK:104/165/225:
#     at_home / on_throne / chow_down), and SalkindSchedule (01D1h) from
#     `0A 01` @02E5, `0A 02` @0495, `0A 01` @063B (at_home / at_court /
#     at_home, :122/:182/:242).
#   - SALKIND 0x0403 enterFastArea(): U8/SALKIND.UNK:102 `= at_court` then
#     :107 `= at_home` compile `0A 02` @0280 and `0A 01` @0298.
# Only names the compiled corpus uses are listed; the LV-only names are in
# LV_SCHEDULE_CONSTANTS below.
# The global itself: until 2026-10-08 our araminaSchedule was pinned at bit
# 0x663, so MORDEA's writes to 0207h never reached our ARAMINA and she idled
# in normal play. lv_manifest.json now pins araminaSchedule at 0x207 (and
# devonInRule, read at ARAMINA 0x040D @017A, at retail 0x58); the old bits
# are retired. Her other eleven globals followed on 2026-10-09, so every
# global operand she compiles now matches retail ARAMINA's.
# test_symbol_retail_pins.py checks all of them.
SCHEDULE_CONSTANTS = {
    'at_home': 1,
    'on_throne': 2,
    'at_court': 2,
    'chow_down': 3,
}

# LV-ONLY schedule names. NOT RETAIL-PINNED: no retail class uses them, so
# these values are a design choice, not recovered data. They exist because
# every unknown name compiles to 0, so an NPC's two names collided at 0 and
# the second enterFastArea branch was dead (INGYALD.UNK:128 `at_still`).
# Each LV NPC's schedule global is 2 bits; the rule is that one NPC's names
# are mutually distinct and never equal the retail value of a name on the
# same global. Per NPC (schedule() sets "away" at daytide, home otherwise;
# enterFastArea tests home first; global 0 = schedule() has not run yet):
#   - Thordis (thordisSchedule): at_home 1 (retail) / in_field 2.
#   - Hrodny (hrodnySchedule): at_home 1 (retail) / at_work 2.
#     For these two the 1994 default is home, but home is the
#     retail-pinned 1, so global 0 can match it only by un-pinning at_home.
#     2 rather than 0 means an unscheduled NPC (until the first
#     SchedulerProcess run, at most 900 game seconds) spawns no bark
#     process. With 0 she would bark the away lines while at home.
#   - Ingjald (ingyaldSchedule): in_house 0 / at_still 2. Both LV, so home
#     keeps 0: an unscheduled Ingjald takes the home branch, which is what
#     every build before these pins compiled.
LV_SCHEDULE_CONSTANTS = {
    'in_field': 2,
    'at_work': 2,
    'in_house': 0,
    'at_still': 2,
}

# Damage-type constants from the 1994 headers (not recovered). Before
# 2026-10-07 DMG_FULL compiled to `push 0`, and a zero type makes
# Actor::calculateAttackDamage return no damage, so every
# `receiveHit(..., DMG_FULL)` in the corpus hit for nothing. PINNED against
# the retail shared/data/USECODE.FLX: U8/MORDEA.UNK:1284
# `Avatar.receiveHit(referent, 4, Avatar.getHp(), DMG_FULL)` is class
# 0x0407 offset 2736 `0B 80 00` (push 0080h, the last argument, pushed
# first), then getHp, `0A 04`, the referent, and 274C `0F 0C 53 00`
# (calli Item::receiveHit). 0x80 is the engine's DMG_PIERCE
# (weapon_info.h:64): no armour, no to-hit roll. Retail pushes a word, so
# emit push word. DMG_HAND/DMG_BLUNT/DMG_FIRE (METHOD.UNK only, a dropped
# class) have no retail correlation here and stay unpinned.
DMG_CONSTANTS = {
    'DMG_FULL': 0x80,
}

# Item status-flag constants from the 1994 headers (not recovered). They
# compiled to `push 0` until 2026-10-07, so `getStatus() & INVISIBLE` was
# always 0 and toggleStatus(OWNED) toggled nothing. PINNED against the
# retail shared/data/USECODE.FLX, byte literals (emit push byte):
#   - INVISIBLE 0x10: ARAMINA 0x040D, U8/ARAMINA.UNK:281
#     `(Avatar.getStatus() & INVISIBLE) = false` is `5E 0A 10 39` @05C1
#     (push retval; push byte 10h; bit_and), then `0A 00 24` (= false);
#     TypePotion 0x02FE invisible() `0A 10 39` @0700.
#   - OWNED 0x04: TypePotion 0x02FE `if Avatar.getStatus() & OWNED` is
#     `5E 0A 04 39` @06BC; the toggleStatus argument after it is `0A 04`
#     @06C8.
# Both equal ScummVM item.h FLG_OWNED = 0x0004, FLG_INVISIBLE = 0x0010.
#   - CONTAINER_GUMP_OPEN 0x100, a WORD literal (push 0100h): AVATAR 0x0401
#     use(), UNK/AVATAR.UNK:24 `if getStatus() & CONTAINER_GUMP_OPEN`, is
#     `5E 0B 00 01 39` @0093; FREE 0x0581 unkCloseAllGumps (UNK/FREE.UNK:
#     1232/1244) `0B 00 01 39` @370E and @374B. ScummVM item.h
#     FLG_GUMP_OPEN = 0x0100. Unpinned, it compiled to push byte 0, so
#     the Avatar's use() never saw its paperdoll open.
# A value above 0xFF is pushed as a word, as retail does.
STATUS_CONSTANTS = {
    'OWNED': 0x04,
    'INVISIBLE': 0x10,
    'CONTAINER_GUMP_OPEN': 0x100,
}

# Retail METHOD (class 0x57C) routines and processes, called by offset.
# METHOD is never recompiled or shipped (build_eusecode UNSAFE_TO_REPLACE),
# so the target is retail's own class and every offset below comes from
# retail call sites in shared/data/USECODE.FLX: the callee's first
# instruction, its argument bytes from the spawn/call cleanup, matched to
# UNK files/UNK/METHOD.UNK by declaration order (the 26 retail functions
# and the 26 source functions line up one-to-one, and every arg size
# agrees). Functions retail never calls (lookBark, loiter, follow, lead,
# pace) are left out: no call site, no pinned offset. enterConvo/
# exitConvo are reached through the EnterConvoStmt/ExitConvoStmt codegen
# (they are keywords), which spawns the two entries below. enterConvo2
# (0x0E4F, 9 retail sites, the seated variant) has no LV caller.
#
#   name -> (offset, kind, has_this, param kinds, return kind)
#   param kinds: 'word' (2 bytes), 'string' (push string; str to ptr: 4,
#   freed after the spawn), 'worldpoint' (push huge [BP+xx] 05: 5 bytes)
#   return kinds as CodeGenerator._classify_return_kind.
METHOD_CLASS_ID = 0x057C
METHOD_ROUTINES = {
    # TypePotion 0x2FE 06C6 `Avatar.toggleStatus(OWNED)`: 0A 01 0A 04 6F FE
    # 11 7C05 1301 6E F8; FREE 0x581 3811 `push byte 10h; push addr
    # [BP+06h]; call 057Ch 0113h; add sp -6`.
    'toggleStatus': (0x0113, 'routine', True, ('word',), 'none'),
    # spawn 08h 02h 057Ch 013Eh (7 sites)
    'legal_moveItemTo': (0x013E, 'process', True, ('word',) * 4, 'process'),
    # spawn 08h 02h 057Ch 03CDh (7 sites)
    'moveItemTo': (0x03CD, 'process', True, ('word',) * 4, 'process'),
    # spawn 00h 02h 057Ch 0610h (3 sites)
    'candleAnim': (0x0610, 'process', True, (), 'process'),
    # 0x243 017B `push byte 1; push dword [BP+06h]; spawn 02h 02h 057Ch
    # 0676h` (11 sites)
    'boom': (0x0676, 'process', True, ('word',), 'process'),
    # 0x6D 1D69 `push pid; ..; push string; str to ptr; push byte 50h;
    # push addr; spawn 06h 02h 057Ch 087Dh; free string [SP+02h]` (81)
    'timedBark': (0x087D, 'process', True, ('word', 'string'), 'process'),
    # 0x7C 02AA `push pid; push addr [BP-07h]; spawn 00h 02h 057Ch 08B9h;
    # push retval; implies; pop temp; suspend; push process result`
    'isInWorld': (0x08B9, 'process', True, (), 'process'),
    # 0x44 0B70 `Avatar.turnToFace([BP-06h], 0, 0)`: push pid; push byte 1
    # (Avatar objid temp); push byte 0; push byte 0; push [BP-06h]; push
    # addr [SP-06h]; spawn 06h 02h 057Ch 091Ch; add sp -8 (448 sites)
    'turnToFace': (0x091C, 'process', True, ('word',) * 3, 'process'),
    # spawn 00h 02h 057Ch 0AC6h (2 sites)
    'wander': (0x0AC6, 'process', True, (), 'process'),
    # 0x7C 450C `push [BP+0Ch]; call 057Ch 10FFh; add sp -2; push retval`
    'focusCheck': (0x10FF, 'routine', False, ('word',), 'word'),
    # AVATAR 0x401 09C6 `push addr [BP-17h]; call 057Ch 1220h; add sp -4;
    # push retval`
    'isMage': (0x1220, 'routine', True, (), 'word'),
    # 0x586 135A `push addr [BP-08h]; spawn 02h 02h 057Ch 12CEh`
    'downUp': (0x12CE, 'process', True, ('word',), 'process'),
    # 0x44 0B8F `Avatar.realDoAnim(0, [BP-06h])`: push pid; push byte 1
    # (Avatar objid temp); push [BP-06h]; push byte 0; push addr [SP-04h];
    # spawn 04h 02h 057Ch 15E7h; add sp -6 (1305 sites)
    'realDoAnim': (0x15E7, 'process', True, ('word', 'word'), 'process'),
    # 0x402 0248 `push pid; push [BP-07h]; push huge [BP-05h] 05h; push
    # dword [BP+06h]; spawn 07h 02h 057Ch 133Fh; add sp -7` (44 sites).
    # Retail 133F (UNK/METHOD.UNK:1029) checks nothing about the point
    # itself: if the NPC is alive, the Avatar is on another map or > 700
    # (getDistance, FREE 0x581 1CE3) from the NPC, AND on another map than
    # destMap or > 700 from the destination, it calls Npc::teleport(x, y,
    # z, map) and returns true. So a destination must be standable as
    # given; nothing corrects it.
    'safeTeleport': (0x133F, 'process', True, ('worldpoint', 'word'),
                     'process'),
    # 0x405 0135, same shape, spawn 07h 02h 057Ch 143Ah (39 sites); ARAMINA
    # 0x40D 01A3 reads it as `push retval; implies; pop temp; suspend; push
    # process result; long to int; jne`. The same two distance tests as
    # safeTeleport, no teleport.
    'canSafeTeleport': (0x143A, 'process', True, ('worldpoint', 'word'),
                        'process'),
    # The conversation bracket. All 49 retail enterConvo and 256 exitConvo
    # call sites are `push pid; push dword [BP+06h]; spawn 00h 02h 057Ch
    # <off>; push retval; implies 01 01; pop temp; suspend` (ARAMINA 0x40D
    # 1136/11B1), except one each through a local, `push addr [BP-02h]`
    # (0x4B5 02F2/034C). 0BCF (UNK/METHOD.UNK:766): aborts the caller
    # (kills referent's PT_USE 0x207) if the NPC is dead or the Avatar
    # invisible; else closes gumps, kills referent's 0x205/0x200/0xF0/
    # 0x204, stasis on, NPC and Avatar turn to face, camera to the NPC,
    # somebodyTalking (global 0x0F) = 1 at 0E49. 1090 (METHOD.UNK:908):
    # Item::enterFastArea() on the NPC, scrollBack(30 or 25), global 0x0F
    # = 0 at 10F1, stasis off.
    'enterConvo': (0x0BCF, 'process', True, (), 'process'),
    'exitConvo': (0x1090, 'process', True, (), 'process'),
}

# safeTeleport/canSafeTeleport were held out of METHOD_ROUTINES from
# 2026-10-07 to 2026-10-08 (DEFERRED_METHOD_ROUTINES) because every LV
# call site was an NPC schedule() aimed at a 1994 Map 10 coordinate that
# was void, lake or bare ground on the rebuilt map. The eight LV
# schedules (ATLI, EZREKAL, RAGNAR, TYORVI, THORDIS, HRODNY, INGYALD in
# lv-patched/, SIGRID in lv-new/) now aim at the rebuilt villages, and
# agents/map-populator/src/test_schedule_destinations.py checks every
# compiled destination with exact_reach against the built FIXED.DAT.
# ARAMINA's (16735,16127,48) on map 41 is retail's own literal (ARAMINA
# 0x40D 0185-0199).

# Animation-sequence names (AS_*), the first argument of METHOD realDoAnim.
# PINNED by aligning, class by class, every `realDoAnim(AS_X, ...)` in the
# 1994 sources (U8/ and UNK files/UNK/) with the anim byte each retail
# `spawn ... 057Ch 15E7h` pushes, in the 14 classes whose source and
# retail counts agree (ARAMINA 0x40D, MORDEA 0x407, TORWIN 0x41A, DARION
# 0x405, AVATAR 0x401, POTION 0x2FE, ...). Every name maps to one value
# (AS_FIDGET 108/108 sites; AS_ENTER_CAST and AS_EXIT_CAST 18/19 and 23/24,
# one class having the two calls in the other order). Example: FREE 0x581
# tonyStinks 3770-3786 `realDoAnim(AS_ENTER_CAST, ..)` pushes 0A 1B, and
# 38A3 `AS_EXIT_CAST` pushes 0A 1C. They compiled to push 0 (walk) until
# 2026-10-07, which only mattered once realDoAnim itself was called.
# AS_KNEEL_DOWN/AS_KNEEL_UP have no retail source site; see
# LV_ANIM_CONSTANTS below.
ANIM_CONSTANTS = {
    'AS_WALK': 0, 'AS_RUN': 1, 'AS_STAND': 2, 'AS_VERT_LEAP': 3,
    'AS_GET_UP': 4, 'AS_DRAW_WEAPON': 5, 'AS_SHEATH_WEAPON': 6,
    'AS_SWING_WEAPON': 7, 'AS_FALL_DOWN': 14, 'AS_CLIMB_2': 19,
    'AS_CLIMB_3': 20, 'AS_CLIMB_4': 21, 'AS_CLIMB_5': 22,
    'AS_ENTER_CAST': 27, 'AS_EXIT_CAST': 28, 'AS_CAST1': 29, 'AS_CAST2': 30,
    'AS_CAST3': 31, 'AS_LOOK_LEFT': 32, 'AS_LOOK_RIGHT': 33,
    'AS_EDGE_BALANCE': 42, 'AS_FIDGET': 47, 'AS_SIT_DOWN': 51,
    'AS_SIT_UP': 52,
}

# LV DESIGN VALUES, not retail-pinned. AS_KNEEL_DOWN and AS_KNEEL_UP occur
# only in UNK/SHADES.UNK (4 sites each), an LV class retail never shipped,
# and no recovered source of a retail class names them, so no retail byte
# binds the names. Unpinned they compiled to 0 (AS_WALK), and all eight
# SHADES kneels played as walk steps that left the Avatar 148 units off
# his mark (playtest 2026-10-07 wave 2 B). The values come from two
# sources that agree:
#   - Retail usage: anim 49 then anim 50 is the commonest down/up pair in
#     retail realDoAnim spawns (`0A 31` ... `0A 32` before `57 04 02 7C 05
#     E7 15`), 49 always first and 50 often followed by AS_STAND, the way
#     SHADES writes `AS_KNEEL_UP -> AS_STAND`: BOTTLE 0x0B4 (five pairs,
#     e.g. 0361/0382), LOGO 0x15A 0148/01C1, VARDION 0x41C 54DB/5797, BANE
#     0x41D, GORGROND 0x41F, BEREN 0x420, ENCHANT 0x587 0443/0609 (kneel,
#     cast, rise), PYROS 0x06D 2BAA/2BCF.
#   - ANIM.DAT (STATIC/ANIM.DAT): for the Avatar (shape 1, facing south)
#     action 49 runs frames 1016-1015-1014 down to the kneel, action 50
#     runs 1014-1015-1016 and ends on frame 4, action 2's standing frame;
#     for Ezrekal's sorcerer shape 200, 49 is frames 224..231 and 50 the
#     same in reverse.
# Do not take ScummVM animation.h's names for U8: it calls 34
# startKneeling and 50 stopKneeling, but U8's action 34 is the Avatar
# RISING (1014 to 1016) and 35 the kneel down, the reverse of those names.
# The 35/34 pair (PENT 0x07C 087B/0904, ETHRSPEL 0x585) is a second
# kneel; shape 200 has no action 35, so it would not work for Ezrekal.
LV_ANIM_CONSTANTS = {
    'AS_KNEEL_DOWN': 49,
    'AS_KNEEL_UP': 50,
}

# Compass directions and turnToFace's RANDOM. PINNED against retail AVATAR
# 0x401's "Turn" cheat menu (lv-patched/AVATAR.UNK:282-308, `if key =
# "North" { count = north; }` ...): 0CCB `0A 00 01 ED` for north through
# 0D5E `0A 07 01 ED` for northwest, one byte per direction in source
# order; then `caster.turnToFace(count,RANDOM,7)` at 0D62 pushes `0A 07;
# 0A 00; 3F ED`, so RANDOM = 0. They compiled to push 0 (all north).
# LEFT and RIGHT are turnToFace's forceDir values and its return value.
# Retail METHOD 0x57C 099F-09A9 `push [BP+0Ch]; push byte 1; cmp; jne;
# push byte 0; pop byte [BP-01h]` is `if forceDir = LEFT { right = false;
# }` (UNK/METHOD.UNK:585), right after the `forceDir = RANDOM` test at 0939
# (`0A 00`); the routine's end, UNK/METHOD.UNK:616/619 `return RIGHT;` /
# `return LEFT;`, is `0A 02 60 08` at 0A28 and `0A 01 60 08` at 0A32. So
# RIGHT = 2. As a forceDir any value but 0 and 1 turns right, so the 2
# SHADES `turnToFace(0, RIGHT, ..)` calls behave the same with 2 as with
# any non-LEFT value; unpinned they compiled to 0, RANDOM.
DIR_CONSTANTS = {
    'north': 0, 'northeast': 1, 'east': 2, 'southeast': 3,
    'south': 4, 'southwest': 5, 'west': 6, 'northwest': 7,
    'RANDOM': 0, 'LEFT': 1, 'RIGHT': 2,
}

# Single-value header constants, each pushed by retail as a byte literal.
#   - differentMap -1: FREE 0x581 getDistance (UNK/FREE.UNK:166/174
#     `return differentMap;`) is `0A FF 12` at 1D98 and 1DBD. It compiled
#     to 0, which reads as "same spot" to every `getDistance(..) < n`.
#   - NULL_REF 0: FREE 0x581 2536 and 25CD `0A 00 12` are UNK/FREE.UNK:499
#     and :523 `return NULL_REF;` (the routine with the setQuantity(666)
#     between them); the pragma form `[[PT_DEFAULT, NULL_REF]]` is
#     `0A 01 0A 00 77` at TORWIN 0x41A 383D/38BA and DARION 0x405 17F4.
#   - ACT_LOITER 0: DARION 0x405's only two cSetActivity calls, U8/
#     DARION.UNK:112 and :998 `cSetActivity(ACT_LOITER)`, push `0A 00` at
#     0206 and 1C0C before `calli 06h 00AEh` (Actor activity 0 = loiter).
#   - Gump_MainMenu 1: AVATAR 0x401 use(), UNK/AVATAR.UNK:28
#     `openGump(Gump_MainMenu)`, is `0A 01 40 06 0F 06 4C 00` at 00A6
#     (push byte 1; push this; calli openGump). It compiled to 0, and
#     Item::openGump(0) built a paperdoll from gump shape 0: double-
#     clicking the Avatar segfaulted ScummVM (playtest 2026-10-07 wave 2 A
#     finding 1).
# NULL_REF and ACT_LOITER already compiled to push byte 0 through the
# unknown-identifier fallback; pinning them removes the warning, not a
# byte.
LITERAL_CONSTANTS = {
    'differentMap': -1,
    'NULL_REF': 0,
    'ACT_LOITER': 0,
    'Gump_MainMenu': 1,
}

MAP_CONSTANTS = {
    'MapLBBlackness': 0,            # storms-chain anchor; vision stage
    'MapDocks': 3,                  # needle; new-game start map
    'MapThePlateau': 8,             # storms-chain
    'MapLostVale': 10,              # context (see above) — LV village map
    'MapDaemonsCrag': 12,           # needle ×2
    'MapBrimstoneCliffs': 13,       # airspel-suffix
    'MapObsidianFortress': 14,      # storms-chain + airspel anchor
    'MapRoadTreasure': 15,          # storms-chain + airspel anchor
    'MapCarthaxLake': 16,           # airspel-suffix
    'MapStoneCove': 21,             # airspel-suffix
    'MapLavaRiverBefore': 24,       # airspel-suffix (consecutive pair)
    'MapLavaRiverAfter': 25,        # airspel-suffix (consecutive pair)
    'MapCarthaxII': 26,             # airspel-suffix
    'MapCARTHAXbreakingground': 28, # storms-chain + airspel anchor
    'MapHallOfTheMountainKing': 31, # storms-chain + airspel anchor
    'MapArgentrockIsle': 37,        # storms-chain + needle + airspel anchor
    'MapWestTenebrae': 39,          # airspel-suffix (unused by packed files)
    'MapCentralTenebrae': 40,       # airspel-suffix (unused by packed files)
    'MapEastTenebrae': 41,          # airspel-suffix; ARAMINA's use
    'MapEndGame': 43,               # storms-chain
    'MapPlaneOfFire': 44,           # storms-chain
    'MapPlaneOfWater': 45,          # storms-chain
    'MapPlaneOfAir': 46,            # storms-chain
    'MapPlaneOfEarth47': 47,        # storms-chain; self-naming
    'MapUpperCatacombsII': 49,      # storms-chain
    'MapUpperCatacombsIII': 50,     # storms-chain
    'MapLowerCatacombsI': 51,       # storms-chain
    'MapShrine': 54,                # storms-chain
    'MapLowerCatacombsII': 57,      # storms-chain
    'MapAncientNecs': 62,           # storms-chain
    'MapGhostRoom': 63,             # storms-chain
}

SND_CONSTANTS = {
    'ARMHIT1A': 1,   'AROWFYR1': 2,   'AROWFYR2': 3,   'ARMRHIT3': 4,
    'ARMRHIT4': 5,   'LTNING1A': 6,   'TELEPORT': 7,   'ARMRHIT9': 8,
    'AROWFLY1': 9,   'AROWHIT1': 10,  'AROWHIT2': 11,  'AROWHIT4': 12,
    'AROWHIT5': 13,  'AROWHIT6': 14,  'MIXSPELL': 15,  'AXSWNG1A': 16,
    'BODYHIT1': 17,  'BODYHIT2': 18,  'BODYHIT3': 19,  'BODYHIT5': 20,
    'BODYHIT6': 21,  'BODYHIT7': 22,  'BODYHIT8': 23,  'CLOSEPRT': 24,
    'COMBAT1': 25,   'COMBAT2': 26,   'EXPLODE3': 27,  'COMBAT5': 28,
    'COMBAT6': 29,   'CRICKET': 30,   'EXPLODE1': 31,  'LAVASTM1': 32,
    'FIRE1A': 33,    'FYRBAK2A': 34,  'FIRE5B': 35,    'FLMBRST1': 36,
    'FALSPL3A': 37,  'FLMBRST3': 38,  'FALSPL4A': 39,  'FLMBRST5': 40,
    'IMPACT1A': 41,  'FLMBRST7': 42,  'FOOT10C': 43,   'FOOT10D': 44,
    'FOOT11B': 45,   'FOOT11D': 46,   'FTSTEP1': 47,   'QUAKE2': 48,
    'QUAKE3': 49,    'GRUNT9A': 50,   'GRUNT6A': 51,   'GRUNT7A': 52,
    'GRUNT8A': 53,   'MAGIC1': 54,    'HEADCUT1': 55,  'AROWFYR3': 56,
    'MAGIC2': 57,    'MAGIC3': 58,    'MAGIC9': 59,    'MNSTHIT1': 60,
    'MONSTER1': 61,  'MONSTER2': 62,  'MONSTER3': 63,  'MONSTER4': 64,
    'MONSTER5': 65,  'MONSTER6': 66,  'MONSTER7': 67,  'JUMP1A': 68,
    'MONSTER9': 69,  'PRTCLMOV': 70,  'PRTCULIS': 71,  'SHARPEN': 72,
    'SORDHIT1': 73,  'SHLDHT1A': 74,  'SORDHIT3': 75,  'SORDHIT4': 76,
    'SPLASH1A': 77,  'SQDRCLS1': 78,  'SQDROPN1': 79,  'SRDHIT1A': 80,
    'SRDSCR2A': 81,  'SRDSCR3A': 82,  'SRDSWN1A': 83,  'SPLASH3A': 84,
    'STABJCY1': 85,  'STREAM1': 86,   'LAVABUBL': 87,  'LEVER02A': 88,
    'THUNDER2': 89,  'LEVER03A': 90,  'THUNDR1A': 91,  'FALLING1': 92,
    'FYRBAK1A': 93,  'THUNDR2A': 94,  'L_RMBL3A': 95,  'THUNDR2C': 96,
    'AROWFYR4': 97,  'WALHIT2A': 98,  'FALSCRM1': 99,  'FLMWHSH1': 100,
    'FLMBRST9': 101, 'GARDHAND': 102, 'WALHIT5A': 103, 'GROOVY': 104,
    'WAVE1': 105,    'MONSTER8': 106, 'WAVE3': 107,    'WDDRCLS1': 108,
    'WDDROPN1': 109, 'WEPNFIRE': 110, 'WEPNHIT2': 111, 'OOOMPH': 112,
    'RMRCLNK1': 113, 'SQDRCLS2': 114, 'WIND3': 115,    'WIND4': 116,
    'ZOMBIE1': 117,  'ZOMBIE2': 118,  'ZOMBIE3': 119,  'ZOMBIE4': 120,
    'FTSTEP4A': 121, 'FTSTEP4B': 122, 'FTSTEP5A': 123, 'SMOKPUF1': 124,
    'FTSTEP6A': 125, 'FTSTEP6B': 126, 'FTSTEP7A': 127, 'FTSTEP7B': 128,
    'FTSTEP8A': 129, 'FTSTEP8B': 130, 'BAKGRND2': 131, 'SMOKPUF2': 132,
    'FYRCRKL1': 133, 'FYRCRKL2': 134, 'FYRCRKL3': 135, 'MECH1': 136,
    'MECH2': 137,    'CRETURE6': 138, 'CRETURE7': 139, 'DRCLOSE1': 140,
    'MECH3': 141,    'METEOR': 142,   'RUNGRAVL': 143, 'RUNSTONE': 144,
    'RUNWOOD': 145,  'WHOA1A': 146,   'WHOA2B': 147,   'WHOA3A': 148,
    'WALKGRVL': 149, 'BEE3': 150,     'WALKSTON': 151, 'BIGFIRE2': 152,
    'WALKWOOD': 153, 'BUBLING2': 154, 'LAVASTM2': 155, 'CRETUR3A': 156,
    'RUNDOCK': 157,  'EXPLODE2': 158, 'WALKDOCK': 159, 'GARDBST1': 160,
    'TROLLSTP': 161, 'WMNSCRM1': 162, 'DRIP': 163,     'RAIN2': 164,
    'DRIP2': 165,    'SPLASH3B': 166, 'SPLASH3C': 167, 'SPLASH3D': 168,
    'FIREBALL': 169, 'RUNWATER': 170, 'SMOKPUF4': 171, 'SMOKPUF5': 172,
    'SPARK1': 173,   'SPLASH4': 174,  'UNSHEATH': 175, 'VOLCANO1': 176,
    'WMNSCRM2': 177, 'GLASBRK1': 178, 'GLASBRK2': 179, 'GLASBRK3': 180,
    'GLASBRK4': 181, 'GLASBRK5': 182, 'GHOUL2': 183,   'FEMOAN1': 184,
    'FEMOAN2': 185,  'FEMOAN3': 186,  'WMNSCRM3': 187, 'SPELLGO1': 188,
    'SPELLGO2': 189, 'SPELLGO3': 190, 'SPELLGO4': 191, 'SPELLGO5': 192,
    'SPELLGO6': 193, 'WIND1B': 194,   'WIND1C': 195,   'WIND1D': 196,
    'WIND1E': 197,   'STREAM1A': 198, 'STREAM1B': 199, 'STREAM1C': 200,
    'STREAM1D': 201, 'WATRFAL1': 202, 'WATRFAL2': 203, 'WATRFAL4': 204,
    'SMLSPLSH': 205, 'MTLSPHER': 206, 'ZIPUP': 207,    'ZIPDOWN': 208,
    'AVATARP': 209,  'OOF1A': 210,    'OOF3A': 211,    'OOF5A': 212,
    'OOF7A': 213,    'OOF11A': 214,   'OOF14A': 215,   'OOF18A': 216,
    'CHEATER': 217,  'TROODLE': 218,  'EYEBALL': 219,  'EYEBALL8': 220,
}


# ─── LV NPC Class IDs ─────────────────────────────────────────────────────
# Maps LV NPC class names to usecode class IDs using the engine's
# npcnum + 1024 dispatch mechanism. Items with shape 400 and a non-zero
# npcnum field dispatch to class (npcnum + 1024) via a ScummVM patch.
#
# Formula: class_id = npcnum + 0x0400
# These must match the npcnum values assigned in the map builders.

LV_NPC_SHAPES = {
    'RAGNAR':   105 + 0x0400,  # 0x0469 — npcnum 105, Hoskuld Village
    'THORDIS':  106 + 0x0400,  # 0x046A — npcnum 106, Hoskuld Village
    # SIGRID moved here 2026-07-26 (orphan triage, decision B). She was
    # pinned at class 1452 in the manifest's `classes` group, which NO
    # dispatch can reach: npcNum is a single byte in the map record, so the
    # engine patch's npcNum+1024 tops out at class 1279, and Actor promotion
    # (map.cpp) is narrower still at npcNum 100-116. She had 2.4 KB of
    # finished dialogue and no way to be spoken to.
    #
    # npcNum 102 is not an arbitrary free slot — build_map_10.py already
    # places it, already labels it "Hunter", already puts it in the Hoskuld
    # cluster, with the Farmer (103) and Child (104) beside it. Sigrid's
    # character sheet is "Female Hunter, Clan Hoskuld", married to the Male
    # Farmer, one son. The placement had modelled her family all along; only
    # the class was in the wrong window.
    'SIGRID':   102 + 0x0400,  # 0x0466 — npcnum 102, Hoskuld Village
    'ATLI':     107 + 0x0400,  # 0x046B — npcnum 107, Gunnar Village
    'INGJALD':  112 + 0x0400,  # 0x0470 — npcnum 112, Gunnar Village
    'HRODNY':   113 + 0x0400,  # 0x0471 — npcnum 113, Gunnar Village
    'TYORVI':   115 + 0x0400,  # 0x0473 — npcnum 115, Gunnar Village
    'EZREKAL':  116 + 0x0400,  # 0x0474 — npcnum 116, Ezrekal's Dwelling
}


class IntrinsicInfo:
    """Information about a single intrinsic function."""
    __slots__ = ('id', 'signature', 'name', 'class_name', 'method_name',
                 'arg_bytes', 'arg_count', 'has_return', 'is_process')

    def __init__(self, id, signature):
        self.id = id
        self.signature = signature
        self._parse_signature(signature)

    def _parse_signature(self, sig):
        """Parse a signature like 'process Item::bark(char* str)' into components."""
        # 'strptr process Item::ask' is a process too: retail waits on it
        # wherever its answer is used, FREE 0x581 askYesNo 1AF0-1B06
        # (`key = Avatar.ask(keyList)`: push pid ... calli 06h 004Ah; free
        # slist [SP+04h]; add sp; push retval; implies 01 01; pop temp;
        # suspend; push process result; long to int). Testing only for a
        # leading 'process ' left `key` holding the ask's pid, so LVFREE
        # askYesNo answered -1 before the player clicked (playtest
        # 2026-10-07 wave 2 A3b).
        self.is_process = sig.startswith(('process ', 'strptr process '))
        self.has_return = False

        # Strip return type and process prefix
        clean = sig
        for prefix in ('process ', 'strptr process ', 'uword ', 'word ', 'ubyte ',
                       'byte ', 'bool ', 'void '):
            if clean.startswith(prefix):
                clean = clean[len(prefix):]
                if prefix not in ('process ', 'void '):
                    self.has_return = True
                break

        # Extract class::method or bare function name
        paren_pos = clean.find('(')
        if paren_pos >= 0:
            func_part = clean[:paren_pos]
            # arg_part = clean[paren_pos+1:-1] if clean.endswith(')') else ''
        else:
            func_part = clean

        if '::' in func_part:
            self.class_name, self.method_name = func_part.split('::', 1)
        elif '.' in func_part:
            # Some use dot notation
            parts = func_part.split('.', 1)
            self.class_name = parts[0]
            self.method_name = parts[1] if len(parts) > 1 else ''
        else:
            self.class_name = ''
            self.method_name = func_part

        self.name = func_part

        # Calculate arg_bytes from the signature parameters
        self.arg_bytes = self._calc_arg_bytes(sig)
        # Declared parameter COUNT, for overload resolution by arity
        # (step-7 repair, 2026-07-04): U8 overloads several intrinsic
        # names with different signatures (Item::pop x3, Npc::pathfind
        # x2, Item::legal_create x3, ...) and the 1994 compiler resolved
        # them by signature. find_intrinsic() uses this to prefer the
        # candidate whose arity matches the call site.
        self.arg_count = self._calc_arg_count(sig)

    @staticmethod
    def _calc_arg_count(sig):
        """Number of declared parameters in the signature."""
        paren_pos = sig.find('(')
        close_pos = sig.rfind(')')
        if paren_pos < 0 or close_pos < 0:
            return 0
        params_str = sig[paren_pos + 1:close_pos].strip()
        if not params_str:
            return 0
        return len([p for p in params_str.split(',') if p.strip()])

    def _calc_arg_bytes(self, sig):
        """Estimate the argument byte count from the signature."""
        paren_pos = sig.find('(')
        if paren_pos < 0:
            return 0
        close_pos = sig.rfind(')')
        if close_pos < 0:
            return 0
        params_str = sig[paren_pos+1:close_pos].strip()
        if not params_str:
            return 0

        # Count parameter bytes
        total = 0
        for param in params_str.split(','):
            param = param.strip()
            if not param:
                continue
            # Determine size from type
            if any(param.startswith(t) for t in ('word', 'uword', 'Word', 'ubyte', 'byte')):
                total += 2  # 16-bit on stack
            elif any(param.startswith(t) for t in ('long', 'ulong', 'Long')):
                total += 4
            elif param.startswith('char*') or param.startswith('WorldPoint*'):
                total += 4  # pointer
            elif param.startswith('AnimSet') or param.startswith('Activity'):
                total += 2  # enum as word
            elif param.startswith('ProcessType'):
                total += 2
            else:
                total += 2  # default word
        return total

    def __repr__(self):
        return f"Intrinsic(0x{self.id:04X}, {self.signature!r})"


class SymbolTable:
    """Central symbol table for the compiler."""

    def __init__(self):
        # Intrinsics: ID -> IntrinsicInfo
        self.intrinsics = {}
        # Intrinsic lookup by method name: name -> list of IntrinsicInfo
        self.intrinsic_by_name = {}
        # Base game classes: name -> classid
        self.class_ids = {}
        # Class names: classid -> name
        self.class_names = {}
        # Class hierarchy: classname -> parent classname
        self.class_parents = {}
        # Global flags: name -> (bit_offset, bit_width)
        self.global_flags = {}
        self._next_global_bit = 0  # for allocating new flags
        # Event names: name -> event_id
        self.event_ids = {}
        # Type references: TypeName -> class_id (or None if unknown)
        self.type_refs = {}

        # M0.6 manifest state. _pinned_flag_names holds the names that came
        # from a loaded manifest (as opposed to allocated fresh this run);
        # new_allocations records (name, bit, width) for every flag
        # allocated at the cursor this run, in allocation order, so the
        # build can append them to the manifest afterward. Both are always
        # present (empty when load_manifest() was never called) so callers
        # that don't use a manifest see no behavior change.
        self._pinned_flag_names = set()
        self.new_allocations = []

        # `uses`-import provider registry (uses-imports-as-cross-class-calls
        # work, 2026-07-03). A "provider" is a compiled class that exposes
        # bare (unqualified) routine/process names another file's `uses
        # "name";` directive can call into via a class:offset 0x11/0x57
        # cross-call — in practice just FREE.UNK (`uses "free"`; see the
        # investigation note in build_eusecode.py — METHOD.UNK and the
        # other `uses` targets in the corpus are not bare-routine
        # providers). Keyed by the lowercased `uses` string.
        #
        #   provider_name (lower) -> {
        #       'class_id': int,
        #       'funcs': {func_name_lower: [(arity, offset, return_kind), ...]}
        #   }
        #
        # return_kind is 'word' (push retval, 0x5E), 'byte' (push byte
        # retval, 0x5D — Boolean-returning routines), 'none' (no declared
        # return type; never pushed), or 'process' (a process: spawned and
        # waited on, its value read back with push process result, 0x6D).
        self.providers = {}

        self._load_intrinsics()
        self._load_events()

    def _load_intrinsics(self):
        """Load all 258 intrinsic functions from the disassembler."""
        for i, sig in enumerate(U8_INTRINSICS):
            info = IntrinsicInfo(i, sig)
            self.intrinsics[i] = info

            # Index by method name
            key = info.method_name.lower()
            if key not in self.intrinsic_by_name:
                self.intrinsic_by_name[key] = []
            self.intrinsic_by_name[key].append(info)

            # Also index by full name (Class::method)
            if info.class_name:
                full_key = f"{info.class_name}.{info.method_name}".lower()
                if full_key not in self.intrinsic_by_name:
                    self.intrinsic_by_name[full_key] = []
                self.intrinsic_by_name[full_key].append(info)

    def _load_events(self):
        """Load event name -> event ID mapping."""
        for i, name in enumerate(U8_EVENTS):
            # Extract just the function name (before parentheses)
            paren_pos = name.find('(')
            if paren_pos >= 0:
                func_name = name[:paren_pos]
            else:
                func_name = name
            self.event_ids[func_name] = i

    def load_base_game_symbols(self, yaml_path=None):
        """Load base game class names from YAML (requires PyYAML).

        Falls back to FLX if yaml is not available.
        """
        try:
            import yaml
        except ImportError:
            return

        if yaml_path is None:
            yaml_path = os.path.join(
                os.path.dirname(__file__), '..', '..', '..',
                'shared', 'corpus', 'usecode-index', 'base-game-symbols.yaml')

        if not os.path.exists(yaml_path):
            return

        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        if 'classes' not in data:
            return

        for class_id_str, info in data['classes'].items():
            classid = int(class_id_str, 16) if isinstance(class_id_str, str) else class_id_str
            name = info.get('name', '')
            if name:
                self.class_ids[name.upper()] = classid
                self.class_names[classid] = name.upper()

    def load_base_game_from_flx(self, flx_path):
        """Load class names directly from EUSECODE.FLX name table."""
        sys.path.insert(0, os.path.dirname(__file__))
        from u8_flex import UsecodeFlexArchive

        flx = UsecodeFlexArchive(flx_path)
        for classid, name in flx.all_class_names():
            self.class_ids[name.upper()] = classid
            self.class_names[classid] = name.upper()

    def find_intrinsic(self, method_name, class_name=None, arg_count=None):
        """Find an intrinsic by name.

        Args:
            method_name: the method name (e.g., 'bark', 'getType')
            class_name: optional class context (e.g., 'Item', 'Npc')
            arg_count: optional call-site argument count. When given and
                the name is overloaded, the candidate whose declared
                parameter count matches is preferred (step-7 repair,
                2026-07-04: `stone.pop(bag.referent)` must resolve to
                Item::pop(uword)/0x37 popToContainer, not the first-
                registered Item::pop(uword,uword,ubyte)/0x36 popToCoords
                — the engine reads the args per the SLOT's signature, so
                a wrong-overload call site reads garbage). When no
                candidate matches the arity, behavior is EXACTLY the old
                first-candidate fallback.

        Returns:
            IntrinsicInfo or None
        """
        def _pick(cands):
            if not cands:
                return None
            if arg_count is not None and len(cands) > 1:
                matches = [c for c in cands if c.arg_count == arg_count]
                if matches:
                    return matches[0]
            return cands[0]

        # Try class-qualified name first
        if class_name:
            key = f"{class_name}.{method_name}".lower()
            candidates = self.intrinsic_by_name.get(key, [])
            if candidates:
                return _pick(candidates)

        # Try bare method name
        key = method_name.lower()
        candidates = self.intrinsic_by_name.get(key, [])
        if len(candidates) == 1:
            return candidates[0]

        # If multiple candidates, try to disambiguate by class
        if class_name and candidates:
            class_matches = [c for c in candidates
                             if c.class_name.lower() == class_name.lower()]
            if class_matches:
                return _pick(class_matches)

        return _pick(candidates)

    def get_event_id(self, func_name):
        """Get the event ID for a function name, or None."""
        return self.event_ids.get(func_name)

    def get_class_id(self, name):
        """Get the class ID for a class name, or None."""
        return self.class_ids.get(name.upper())

    def register_class(self, name, classid, parent=None):
        """Register a new class."""
        self.class_ids[name.upper()] = classid
        self.class_names[classid] = name.upper()
        if parent:
            self.class_parents[name.upper()] = parent.upper()

    def load_manifest(self, manifest):
        """Pre-populate global_flags from a lv_manifest.Manifest's pins and
        set the allocation cursor from its next_free.global_bit (M0.6
        design doc section 4).

        Args:
            manifest: an lv_manifest.Manifest instance.
        """
        for name, info in manifest.global_flags.items():
            if info.get('retired'):
                continue
            self.global_flags[name] = (info['bit'], info.get('width', 1))
            self._pinned_flag_names.add(name)
        self._next_global_bit = manifest.next_free.get('global_bit', self._next_global_bit)
        self.new_allocations = []

    def allocate_global_flag(self, name, bits=1):
        """Allocate a global flag.

        Args:
            name: flag name
            bits: number of bits (default 1)

        Returns:
            (bit_offset, bit_width) tuple

        Raises:
            ManifestError: `name` is a manifest-pinned flag and `bits`
                disagrees with the pinned width. There is no re-pin code
                path — a genuine width change requires a human editing
                lv_manifest.json with a written justification (M0.6
                design doc section 4).
        """
        if name in self.global_flags:
            offset, width = self.global_flags[name]
            if name in self._pinned_flag_names and width != bits:
                raise ManifestError(
                    f"global flag '{name}' is pinned at bit {offset} with "
                    f"width {width}, but this build declares it with width "
                    f"{bits}. There is no re-pin code path: edit "
                    f"lv_manifest.json by hand with a written justification "
                    f"if the width genuinely needs to change.")
            return (offset, width)

        offset = self._next_global_bit
        self.global_flags[name] = (offset, bits)
        self._next_global_bit += bits
        self.new_allocations.append((name, offset, bits))
        return (offset, bits)

    def get_global_flag(self, name):
        """Get the (bit_offset, bit_width) for a global flag, or None."""
        return self.global_flags.get(name)

    def check_new_allocations(self):
        """Post-allocation invariant (M0.6 design doc section 4): no
        unpinned allocation made this run landed inside a pinned flag's
        bit range. This is a belt-and-suspenders check against a
        corrupted/stale next_free cursor — normally impossible since the
        cursor starts past every pin, but a hand-edited manifest with a
        next_free.global_bit lower than an existing pin could otherwise
        let a "new" allocation silently collide with one.

        Returns:
            list of human-readable conflict strings; empty if clean.
        """
        problems = []
        pinned_ranges = []
        for name in self._pinned_flag_names:
            offset, width = self.global_flags[name]
            pinned_ranges.append((offset, offset + width - 1, name))

        for name, offset, width in self.new_allocations:
            new_start, new_end = offset, offset + width - 1
            for p_start, p_end, p_name in pinned_ranges:
                if new_start <= p_end and p_start <= new_end:
                    problems.append(
                        f"new global flag '{name}' at bits [{new_start}-{new_end}] "
                        f"overlaps pinned flag '{p_name}' at bits [{p_start}-{p_end}]")
        return problems

    def register_provider_function(self, provider_name, func_name, arity,
                                    class_id, offset, return_kind):
        """Register one routine/process a provider file exposes to `uses`
        consumers (uses-imports work). provider_name is the lowercased
        `uses "..."` string (e.g. 'free'); func_name/arity/offset/
        return_kind come from CodeGenerator's per-class function table
        after compiling the provider. Overloads (e.g. FREE's safePlaySFX
        with 2 vs 3 args) are disambiguated purely by arity, matching the
        base-game call-site evidence; two overloads sharing an arity (e.g.
        FREE's two 2-arg getDistance overloads) collide and the
        last-registered one wins — a known limitation, not exercised by
        any consumer this work targets.
        """
        entry = self.providers.setdefault(
            provider_name.lower(), {'class_id': class_id, 'funcs': {}})
        entry['class_id'] = class_id
        entry['funcs'].setdefault(func_name.lower(), {})[arity] = (offset, return_kind)

    def find_provider_function(self, provider_name, func_name, arity):
        """Look up a `uses`-imported routine by exact arity match.

        Returns (class_id, offset, return_kind) or None.
        """
        entry = self.providers.get(provider_name.lower())
        if not entry:
            return None
        overloads = entry['funcs'].get(func_name.lower())
        if not overloads or arity not in overloads:
            return None
        offset, return_kind = overloads[arity]
        return (entry['class_id'], offset, return_kind)

    def get_type_shape(self, type_name):
        """Get the shape ID for a TypeXXX identifier, or None.

        Checks the TYPE_SHAPES table (case-sensitive first, then case-insensitive).
        """
        # Direct lookup
        shape = TYPE_SHAPES.get(type_name)
        if shape is not None:
            return shape
        # Case-insensitive fallback
        name_upper = type_name.upper()
        for k, v in TYPE_SHAPES.items():
            if k.upper() == name_upper:
                return v
        return None

    def get_snd_constant(self, name):
        """Get the SFX number for a 1994 snddefs constant name, or None.

        snddefs names are all-caps 8-char sample names (LTNING1A, QUAKE3);
        require the exact uppercase form so ordinary identifiers/locals
        never collide.
        """
        return SND_CONSTANTS.get(name)

    def get_eq_constant(self, name):
        """Get the equip-slot number for an EQ_* constant name, or None.

        Exact uppercase match only, matching get_snd_constant's discipline,
        so an ordinary identifier can never collide. See EQ_CONSTANTS for
        the engine derivation.
        """
        return EQ_CONSTANTS.get(name)

    def get_map_constant(self, name):
        """Get the map number for a Map* constant name, or None.

        Exact match only. Unlisted Map* names (three deliberately
        unpinnable ones, typos, placeholders like MapNameHere) fall
        through to the unknown-identifier warning — see MAP_CONSTANTS
        for the pinning evidence and why that is correct.
        """
        return MAP_CONSTANTS.get(name)

    def get_family_constant(self, name):
        """Get the shape-family number for a *_FAMILY name, or None.

        Exact match only, like every other constant table here. See
        FAMILY_CONSTANTS for the engine derivation and for what the
        push-0 fallback cost before this existed."""
        return FAMILY_CONSTANTS.get(name)

    def get_pt_constant(self, name):
        """Get the process-type value for a PT_* name, or None.

        Exact match only. The six unpinned PT_* names in the corpus fall
        through to the unknown-identifier warning — see PT_CONSTANTS for
        the pinning evidence and why that is correct."""
        return PT_CONSTANTS.get(name)

    def get_anim_constant(self, name):
        """Animation-sequence number for an AS_* name, or None (exact
        match). Retail-pinned names first (ANIM_CONSTANTS), then the
        LV-only design values (LV_ANIM_CONSTANTS); see both for the
        evidence."""
        value = ANIM_CONSTANTS.get(name)
        if value is None:
            value = LV_ANIM_CONSTANTS.get(name)
        return value

    def get_dir_constant(self, name):
        """Direction number for a compass name or RANDOM, or None (exact
        match). See DIR_CONSTANTS for the retail evidence."""
        return DIR_CONSTANTS.get(name)

    def get_period_constant(self, name):
        """Get the day-period value for a period name, or None.

        See DAY_PERIOD_CONSTANTS for the retail clock-class evidence."""
        return DAY_PERIOD_CONSTANTS.get(name)

    def get_schedule_constant(self, name):
        """Get the NPC schedule-state value for a schedule name, or None.

        Exact match only. Retail-pinned names first (SCHEDULE_CONSTANTS),
        then the LV-only design values (LV_SCHEDULE_CONSTANTS); see both
        for the evidence and the per-NPC reasoning."""
        value = SCHEDULE_CONSTANTS.get(name)
        if value is None:
            value = LV_SCHEDULE_CONSTANTS.get(name)
        return value

    def get_dmg_constant(self, name):
        """Get the damage-type value for a DMG_* name, or None.

        Exact match only. See DMG_CONSTANTS for the retail evidence."""
        return DMG_CONSTANTS.get(name)

    def get_status_constant(self, name):
        """Get the item status-flag value for a status name, or None.

        Exact match only. See STATUS_CONSTANTS for the retail evidence."""
        return STATUS_CONSTANTS.get(name)

    def get_literal_constant(self, name):
        """Value of a single-value header constant (differentMap,
        NULL_REF, ACT_LOITER), or None. See LITERAL_CONSTANTS."""
        return LITERAL_CONSTANTS.get(name)

    def get_method_routine(self, name):
        """A retail METHOD (0x57C) entry by exact name, or None:
        (offset, kind, has_this, param kinds, return kind). See
        METHOD_ROUTINES for the retail call-site evidence."""
        return METHOD_ROUTINES.get(name)

    def set_global_flag_base(self, start_bit):
        """Set the starting bit offset for new flag allocations."""
        self._next_global_bit = start_bit

    def __repr__(self):
        return (f"SymbolTable(intrinsics={len(self.intrinsics)}, "
                f"classes={len(self.class_ids)}, "
                f"flags={len(self.global_flags)}, "
                f"events={len(self.event_ids)})")


def create_symbol_table(flx_path=None, yaml_path=None):
    """Create a fully populated symbol table.

    Args:
        flx_path: path to EUSECODE.FLX (for class names)
        yaml_path: path to base-game-symbols.yaml

    Returns:
        SymbolTable
    """
    st = SymbolTable()

    if flx_path and os.path.exists(flx_path):
        st.load_base_game_from_flx(flx_path)
    elif yaml_path and os.path.exists(yaml_path):
        st.load_base_game_symbols(yaml_path)
    else:
        # Try default paths
        default_flx = os.path.join(REPO_ROOT, 'shared', 'data', 'USECODE.FLX')
        if os.path.exists(default_flx):
            st.load_base_game_from_flx(default_flx)

    return st


if __name__ == '__main__':
    st = create_symbol_table()
    print(st)

    # Show some examples
    print(f"\nIntrinsic examples:")
    for name in ['bark', 'ask', 'getType', 'setFrame', 'doAnim', 'isDead', 'urandom']:
        info = st.find_intrinsic(name)
        if info:
            print(f"  {name}: 0x{info.id:04X} ({info.signature})")

    print(f"\nEvent IDs:")
    for name in ['look', 'use', 'hatch', 'schedule', 'enterFastArea']:
        eid = st.get_event_id(name)
        if eid is not None:
            print(f"  {name}: 0x{eid:02X}")

    print(f"\nClass examples:")
    for name in ['AVATAR', 'MYTHRAN', 'FREE', 'FLAGS', 'METHOD']:
        cid = st.get_class_id(name)
        if cid is not None:
            print(f"  {name}: 0x{cid:04X}")
