#!/usr/bin/env python3
"""test_symbol_retail_pins.py — the 2026-10-07 retail audit of TYPE_SHAPES,
the NPC schedule-state constants and DMG_FULL (u8c_symbols.py), and the
M1 shared-flag migration of every global flag ARAMINA reads or writes onto
its retail bit (lv_manifest.json; old bits retired): araminaSchedule/
devonInRule on 2026-10-08, the other eleven on 2026-10-09.

Before the audit, ARAMINA's route search compiled shape 73 (any egg) where
retail searches 174, her plate/tankard/grenade/door filters were 377/340/
435/69 against retail 284/178/592/68, `at_home`/`on_throne`/`chow_down`
compiled to 0, and DMG_FULL compiled to 0 (so receiveHit(..., DMG_FULL)
dealt no damage). Thirty-odd other live TYPE_SHAPES entries were wrong the
same way.

Two halves:
  1. Codegen: a value compiles to the retail constant in the retail
     position (loop-script shape token, create argument, byte literal for a
     schedule compare, word for a damage type).
  2. Evidence: each pinned value is the constant at the cited offset of the
     cited class in the RETAIL shared/data/USECODE.FLX. Skipped (not
     failed) when that gitignored file is absent. Never point this at
     shared/data/u8-install/USECODE/EUSECODE.FLX: that is our installed
     build.

Exits nonzero on any failure.
"""
import contextlib
import io
import os
import re
import sys
import tempfile

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
DISASM_DIR = os.path.join(BASE_DIR, 'agents', 'usecode-disasm', 'src')
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, DISASM_DIR)

from u8c_parser import parse_file  # noqa: E402
from u8c_codegen import CodeGenerator  # noqa: E402
from u8c_symbols import (create_symbol_table, TYPE_SHAPES,  # noqa: E402
                         SCHEDULE_CONSTANTS, LV_SCHEDULE_CONSTANTS,
                         DMG_CONSTANTS, STATUS_CONSTANTS, DIR_CONSTANTS,
                         LITERAL_CONSTANTS, ANIM_CONSTANTS,
                         LV_ANIM_CONSTANTS)

RETAIL_FLX = os.path.join(BASE_DIR, 'shared', 'data', 'USECODE.FLX')

PASS = 0
FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name} {detail}")


def compile_body(body, symbols=None):
    src = ("class TypeTest inherits Item;\n"
           "process TypeTest::t()\n{\n" + body + "\n}\n")
    f = tempfile.NamedTemporaryFile('w', suffix='.UNK', delete=False,
                                    encoding='latin-1')
    f.write(src)
    f.close()
    ast = parse_file(f.name)
    cg = CodeGenerator(symbols or create_symbol_table())
    data = bytes(cg.generate_class(ast))
    os.unlink(f.name)
    return data, cg


def loopscript_shape(v):
    # The loop script is built with one `74 xx` per byte and read back
    # reversed, so shape token 'A' + word arrives as hi, lo, 'A'.
    return bytes([0x74, v >> 8, 0x74, v & 0xFF, 0x74, 0x41])


# (identifier, value, retail class, offset of the constant, its bytes)
RETAIL_PINS = [
    ('TypePathMarker',        174, 0x040D, 0x0470, '0BAE00'),
    ('TypePlateWithFood',     284, 0x040D, 0x0F1E, '0B1C01'),
    ('TypeTankard',           178, 0x040D, 0x10D4, '0BB200'),
    ('TypeFrictionGrenade',   592, 0x040D, 0x104F, '0B5002'),
    ('TypeDoorNS',             68, 0x040D, 0x4D01, '0A44'),
    ('TypeDoorEW',             69, 0x0418, 0x0B26, '0A45'),
    ('TypeTallDoorNS',        340, 0x0596, 0x140B, '0B5401'),
    ('TypeTallDoorEW',        342, 0x0596, 0x1419, '0B5601'),
    ('TypeLever',             672, 0x0596, 0x1427, '0BA002'),
    ('TypeWallSwitch',        505, 0x0596, 0x1435, '0BF901'),
    ('TypeBarrel',            115, 0x0596, 0x1443, '0A73'),
    ('TypeMagArmor',          841, 0x0596, 0x13CC, '0B4903'),
    ('TypeMagicYellowCircle', 202, 0x0596, 0x0FA1, '0BCA00'),
    ('TypeWoundedTorax',      209, 0x0596, 0x0E19, '0BD100'),
    ('TypeFireItem',          397, 0x0401, 0x089C, '0B8D01'),
    ('TypeBlackrockFragments', 442, 0x0401, 0x04AD, '0BBA01'),
    ('TypeEnergizedBlackRock', 793, 0x0401, 0x062B, '0B1903'),
    ('TypeRecallItem',        833, 0x0401, 0x34B2, '0B4103'),
    ('TypeKeyOfTheNecromancer', 232, 0x0401, 0x34C5, '0BE800'),
    ('TypeEarthReagent',      395, 0x0401, 0x34EB, '0B8B01'),
    ('TypeSword',             243, 0x0401, 0x354A, '0BF300'),
    ('TypeArmour',            523, 0x0401, 0x3570, '0B0B02'),
    ('TypeObsidianCoin',      143, 0x0401, 0x3584, '0B8F00'),
    ('TypePentagramBase',     124, 0x0401, 0x0E4A, '0A7C'),
    ('TypeDemon',              96, 0x0401, 0x178D, '0A60'),
    ('TypeFireGlobe',         703, 0x0401, 0x37C5, '0BBF02'),
    ('TypeFireField',         400, 0x0401, 0x3850, '0B9001'),
    ('TypeBackPack',          529, 0x0401, 0x285A, '0B1102'),
    ('TypeAirFocus',          396, 0x0181, 0x14DA, '0B8C01'),
    ('TypeSorcerer',          200, 0x057C, 0x12A8, '0BC800'),
    ('TypeLightning',         511, 0x0407, 0x2670, '0BFF01'),
    ('TypeFireblast',         480, 0x0407, 0x2702, '0BE001'),
    ('TypeMagArms',           844, 0x006D, 0x472B, '0B4C03'),
    # ANCTONES, the Ancient Ones egg, searches for the Zealan ceremonial
    # shield (class 828 AORTA): Pagan's look-alike, ATLI's TypeAOArtifact.
    # (The restored Shield's shape 2026-10-08..17; it is 879 since.)
    ('TypeAOArtifact',        828, 0x048B, 0x009A, '0B3C03'),
]

# (name, value, retail class, offset, bytes)
CONST_PINS = [
    ('at_home',   1, 0x040D, 0x0219, '0A01'),
    ('chow_down', 3, 0x040D, 0x0231, '0A03'),
    ('on_throne', 2, 0x040D, 0x0249, '0A02'),
    ('at_court',  2, 0x040D, 0x11C8, '0A02'),
    ('DMG_FULL', 0x80, 0x0407, 0x2736, '0B8000'),
    ('INVISIBLE', 0x10, 0x040D, 0x05C2, '0A10'),
    ('OWNED',    0x04, 0x02FE, 0x06BD, '0A04'),
    # FREE getDistance `return differentMap;` (UNK/FREE.UNK:166/174)
    ('differentMap', -1, 0x0581, 0x1D98, '0AFF'),
    ('differentMap', -1, 0x0581, 0x1DBD, '0AFF'),
    # FREE `return NULL_REF;` (UNK/FREE.UNK:499/523), [[PT_DEFAULT,
    # NULL_REF]] (U8/TORWIN.UNK:1459, U8/DARION.UNK:733)
    ('NULL_REF', 0, 0x0581, 0x2536, '0A00'),
    ('NULL_REF', 0, 0x0581, 0x25CD, '0A00'),
    ('NULL_REF', 0, 0x041A, 0x383F, '0A00'),
    ('NULL_REF', 0, 0x0405, 0x17F6, '0A00'),
    # cSetActivity(ACT_LOITER) (U8/DARION.UNK:112/998)
    ('ACT_LOITER', 0, 0x0405, 0x0206, '0A00'),
    ('ACT_LOITER', 0, 0x0405, 0x1C0C, '0A00'),
    # turnToFace `if forceDir = LEFT` (UNK/METHOD.UNK:585)
    ('LEFT', 1, 0x057C, 0x09A1, '0A01'),
    # AVATAR use() (UNK/AVATAR.UNK:24/28); FREE unkCloseAllGumps
    # (UNK/FREE.UNK:1232/1244)
    ('CONTAINER_GUMP_OPEN', 0x100, 0x0401, 0x0094, '0B0001'),
    ('CONTAINER_GUMP_OPEN', 0x100, 0x0581, 0x370E, '0B0001'),
    ('CONTAINER_GUMP_OPEN', 0x100, 0x0581, 0x374B, '0B0001'),
    ('Gump_MainMenu', 1, 0x0401, 0x00A6, '0A01'),
    # turnToFace `return RIGHT;` / `return LEFT;` (UNK/METHOD.UNK:616/619)
    ('RIGHT', 2, 0x057C, 0x0A28, '0A02'),
    ('LEFT', 1, 0x057C, 0x0A32, '0A01'),
]

# Retail-shared global flags moved onto their retail bits (the M1
# shared-flag migration): name -> (bit, width, old LV bit). The old bits
# are retired in lv_manifest.json, never to be reused. The first two moved
# 2026-10-08; the rest on 2026-10-09 complete ARAMINA, whose 39 global
# operands now match retail ARAMINA's one for one (checked below).
SHARED_FLAG_PINS = {
    'araminaSchedule': (0x207, 2, 0x663),
    'devonInRule':     (0x58, 1, 0x4B6),
    'araminaMet':      (0x203, 1, 0x65F),
    'araminaName':     (0x204, 1, 0x660),
    'araminaJob':      (0x205, 1, 0x661),
    'somebodyTalking': (0x0F, 1, 0x46D),
    'hearTruthActive': (0x27, 1, 0x485),
    'hydrosFree':      (0x36, 2, 0x494),
    'hasHeart':        (0x3C, 1, 0x49A),
    'lothianDead':     (0xBF, 1, 0x51D),
    'toldDagger':      (0xD6, 1, 0x534),
    'mordeaDead':      (0x11A, 1, 0x576),
    'toldOfTreasure':  (0x147, 1, 0x5A3),
}
# (flag, retail class, offset, bytes): push/pop global <bit> <width>
SHARED_FLAG_SITES = [
    ('araminaSchedule', 0x0407, 0x0270, '4F070202'),  # MORDEA at_home
    ('araminaSchedule', 0x0407, 0x0420, '4F070202'),  # MORDEA on_throne
    ('araminaSchedule', 0x0407, 0x05C6, '4F070202'),  # MORDEA chow_down
    ('araminaSchedule', 0x040D, 0x01B9, '4F070202'),  # ARAMINA.UNK:86
    ('araminaSchedule', 0x040D, 0x0215, '4E070202'),  # ARAMINA.UNK:105
    ('devonInRule',     0x040D, 0x017A, '4E580001'),  # ARAMINA.UNK:72
    ('devonInRule',     0x0401, 0x33F5, '4F580001'),  # AVATAR.UNK:1135
    ('devonInRule',     0x057E, 0x1032, '4F580001'),  # LOGBOOK4
    ('araminaMet',      0x040D, 0x1633, '4F030201'),  # ARAMINA.UNK:743
    ('araminaMet',      0x040A, 0x962C, '4E030201'),  # ORLOK "Tell me of Aramina."
    ('araminaName',     0x040D, 0x16C6, '4F040201'),  # ARAMINA.UNK:758
    ('araminaJob',      0x040D, 0x174A, '4F050201'),  # ARAMINA.UNK:776
    ('somebodyTalking', 0x040D, 0x04FD, '4E0F0001'),  # ARAMINA.UNK:247
    ('somebodyTalking', 0x057C, 0x0E49, '4F0F0001'),  # METHOD
    ('hearTruthActive', 0x040D, 0x1B82, '4E270001'),  # ARAMINA.UNK:868
    ('hearTruthActive', 0x0596, 0x2E7E, '4F270001'),  # AIRSPEL
    ('hydrosFree',      0x040D, 0x1556, '4E360002'),  # ARAMINA.UNK:717
    ('hydrosFree',      0x0050, 0x152C, '4F360002'),  # HYDROS
    ('hasHeart',        0x040D, 0x1164, '4E3C0001'),  # ARAMINA.UNK:597
    ('hasHeart',        0x0405, 0x1CDD, '4E3C0001'),  # DARION
    ('lothianDead',     0x040D, 0x1524, '4EBF0001'),  # ARAMINA.UNK:709
    ('lothianDead',     0x0415, 0x0F57, '4FBF0001'),  # VIVIDOS "I am he"
    ('lothianDead',     0x0401, 0x33FB, '4FBF0001'),  # AVATAR.UNK:1136
    ('toldDagger',      0x040D, 0x1520, '4ED60001'),  # ARAMINA.UNK:709
    ('toldDagger',      0x0415, 0x49E4, '4FD60001'),  # VIVIDOS dagger
    ('mordeaDead',      0x040D, 0x3916, '4E1A0101'),  # ARAMINA.UNK:1513
    ('mordeaDead',      0x041A, 0x2CA5, '4E1A0101'),  # TORWIN
    ('toldOfTreasure',  0x040D, 0x1418, '4E470101'),  # ARAMINA.UNK:663
    ('toldOfTreasure',  0x040A, 0x4560, '4F470101'),  # ORLOK lost treasures
]

# LV design values (LV_ANIM_CONSTANTS): no retail source names them, so
# they are checked against retail USAGE (the 49 -> 50 realDoAnim pair) and
# STATIC/ANIM.DAT, not against a named retail site.
LV_ANIM_PAIRS = [  # (retail class, spawn offset of anim 49, of anim 50)
    (0x00B4, 0x0361, 0x0382),   # BOTTLE
    (0x015A, 0x0148, 0x01C1),   # LOGO
    (0x041C, 0x54DB, 0x5797),   # VARDION
    (0x0587, 0x0443, 0x0609),   # ENCHANT
]

# ── 1. codegen ─────────────────────────────────────────────────────────────
print("codegen")
for ident, val, *_ in RETAIL_PINS:
    check(f"TYPE_SHAPES['{ident}'] == {val}", TYPE_SHAPES.get(ident) == val,
          f"got {TYPE_SHAPES.get(ident)}")

data, _ = compile_body(
    "e : Item;\n"
    "foreach e where (type = TypePathMarker) within 10 cells of Avatar {\n"
    "  e.getFrame();\n}")
check("Aramina's route search compiles loop-script shape 174 (was 73)",
      loopscript_shape(174) in data and loopscript_shape(73) not in data)

data, _ = compile_body("p : Item;\np.create(TypePlateWithFood, 4);")
check("create(TypePlateWithFood) pushes word 284", b'\x0B\x1C\x01' in data)

for name, val in SCHEDULE_CONSTANTS.items():
    data, cg = compile_body(f"x : Integer;\nx = {name};")
    check(f"{name} -> push byte {val}", bytes([0x0A, val]) in data)
    check(f"{name} raises no unknown-identifier warning",
          not any(name in w for w in getattr(cg, 'warnings', [])))

# LV-only schedule names (not retail-pinned): each NPC's names must be
# mutually distinct, or the second enterFastArea branch is dead.
NPC_SCHEDULE_NAMES = {
    'araminaSchedule': ['at_home', 'chow_down', 'on_throne'],
    'thordisSchedule': ['at_home', 'in_field'],
    'hrodnySchedule':  ['at_home', 'at_work'],
    'ingyaldSchedule': ['in_house', 'at_still'],
}
ALL_SCHEDULE = {**LV_SCHEDULE_CONSTANTS, **SCHEDULE_CONSTANTS}
check("LV-only names never shadow a retail-pinned name",
      not set(LV_SCHEDULE_CONSTANTS) & set(SCHEDULE_CONSTANTS))
for var, names in NPC_SCHEDULE_NAMES.items():
    vals = [ALL_SCHEDULE.get(n) for n in names]
    check(f"{var}: {names} all pinned", None not in vals, str(vals))
    check(f"{var}: {names} -> {vals} mutually distinct",
          len(set(vals)) == len(vals))
    check(f"{var}: values fit the 2-bit global",
          all(v is not None and 0 <= v <= 3 for v in vals))
check("an unscheduled Ingjald (global 0) takes the home branch",
      LV_SCHEDULE_CONSTANTS['in_house'] == 0)
check("an unscheduled Thordis/Hrodny (global 0) takes no away branch",
      LV_SCHEDULE_CONSTANTS['in_field'] != 0
      and LV_SCHEDULE_CONSTANTS['at_work'] != 0)
for name, val in LV_SCHEDULE_CONSTANTS.items():
    data, cg = compile_body(f"x : Integer;\nx = {name};")
    check(f"{name} -> push byte {val}", bytes([0x0A, val]) in data)
    check(f"{name} raises no unknown-identifier warning",
          not any(name in w for w in getattr(cg, 'warnings', [])))

# Every schedule name the compiled tiers compare or assign must resolve,
# and every *Schedule global using one must be covered above.
_SCHED_RE = re.compile(r'\b(\w*Schedule|sched)\s*!?=\s*([A-Za-z_]\w*)')
_tiers = [os.path.join(SRC_DIR, 'lv-patched'), os.path.join(SRC_DIR, 'lv-new')]
_lvu = os.path.join(BASE_DIR, 'shared', 'data', 'lv-usecode')
_tiers += [os.path.join(_lvu, 'LOST VALE'), os.path.join(_lvu, 'UNK files', 'UNK')]
_seen, _found = set(), {}
for _d in _tiers:
    if not os.path.isdir(_d):
        continue
    for _f in sorted(os.listdir(_d)):
        if not _f.upper().endswith('.UNK') or _f.upper() in _seen:
            continue
        _seen.add(_f.upper())
        if _f.upper() in ('TJORVI.UNK', 'EALOGO.UNK'):
            continue  # DEV_ALLOWLIST: never compiles
        for _line in open(os.path.join(_d, _f), encoding='latin-1'):
            _line = _line.split('//')[0]
            for _m in _SCHED_RE.finditer(_line):
                if _m.group(2) not in ('sched', 'true', 'false'):
                    _found.setdefault(_m.group(2), set()).add(_f)
for name, where in sorted(_found.items()):
    check(f"schedule name {name} ({', '.join(sorted(where))}) resolves",
          name in ALL_SCHEDULE)

data, cg = compile_body(
    "Avatar.receiveHit(referent, 4, Avatar.getHp(), DMG_FULL);")
check("DMG_FULL -> push word 0080h", b'\x0B\x80\x00' in data)
check("DMG_FULL raises no unknown-identifier warning",
      not any('DMG_FULL' in w for w in getattr(cg, 'warnings', [])))
check("DMG table pins exactly DMG_FULL", DMG_CONSTANTS == {'DMG_FULL': 0x80})

for name, val in STATUS_CONSTANTS.items():
    data, cg = compile_body(
        f"x : Integer;\nx = Avatar.getStatus() & {name};")
    push = (bytes([0x0B]) + val.to_bytes(2, 'little') if val > 0xFF
            else bytes([0x0A, val]))
    check(f"{name} -> push {val:#04x} ({push.hex()}); bit_and",
          push + b'\x39' in data, data.hex())
    check(f"{name} raises no unknown-identifier warning",
          not any(name in w for w in getattr(cg, 'warnings', [])))

# AVATAR.UNK use() is retail 0x401 0093-00AE: both constants in place.
data, cg = compile_body("if getStatus() & CONTAINER_GUMP_OPEN {\n"
                        " closeGump();\n}\nelse {\n"
                        " openGump(Gump_MainMenu);\n}")
check("use(): getStatus() & CONTAINER_GUMP_OPEN is push 0100h; bit_and",
      bytes.fromhex('5E 0B0001 39 51') in data, data.hex())
check("use(): openGump(Gump_MainMenu) is push byte 1; this; calli 4C",
      bytes.fromhex('0A01 4006 0F064C00 6EFA') in data, data.hex())

for name, val in [*LITERAL_CONSTANTS.items(),
                  ('LEFT', DIR_CONSTANTS['LEFT']),
                  ('RIGHT', DIR_CONSTANTS['RIGHT']),
                  *LV_ANIM_CONSTANTS.items()]:
    data, cg = compile_body(f"x : Integer;\nx = {name};")
    check(f"{name} -> push byte {val}", bytes([0x0A, val & 0xFF]) in data,
          data.hex())
    check(f"{name} raises no unknown-identifier warning",
          not any(name in w for w in getattr(cg, 'warnings', [])))
check("LV kneel names are kept out of the retail-pinned ANIM table",
      not set(LV_ANIM_CONSTANTS) & set(ANIM_CONSTANTS))
check("AS_KNEEL_DOWN 49, AS_KNEEL_UP 50",
      LV_ANIM_CONSTANTS == {'AS_KNEEL_DOWN': 49, 'AS_KNEEL_UP': 50})
data, _ = compile_body("Avatar.realDoAnim(AS_KNEEL_DOWN, 4);")
check("realDoAnim(AS_KNEEL_DOWN, 4) pushes dir 4 then anim 49",
      bytes.fromhex('0A04 0A31') in data, data.hex())

# ── 1b. retail-shared flag pins (lv_manifest.json) ─────────────────────────
print("retail-shared flag pins (lv_manifest.json)")
import lv_manifest  # noqa: E402
_manifest = lv_manifest.Manifest.load()
_flags = _manifest.global_flags
_live = {n: i for n, i in _flags.items() if not i.get('retired')}


def _overlaps(lo, hi, pool):
    return sorted(n for n, i in pool.items()
                  if i['bit'] <= hi and lo <= i['bit'] + i.get('width', 1) - 1)


for name, (bit, width, old) in SHARED_FLAG_PINS.items():
    pin = _flags.get(name, {})
    check(f"{name} pinned at retail bit {bit:#x}, width {width}",
          (pin.get('bit'), pin.get('width', 1)) == (bit, width), str(pin))
    check(f"{name}: no other live pin overlaps {bit:#x}",
          _overlaps(bit, bit + width - 1, _live) == [name],
          str(_overlaps(bit, bit + width - 1, _live)))
    old_hi = old + width - 1
    retired = {n: i for n, i in _flags.items() if i.get('retired')}
    check(f"{name}: old bit {old:#x} retired",
          any(i['bit'] <= old and old_hi <= i['bit'] + i.get('width', 1) - 1
              for i in retired.values()) and not _overlaps(old, old_hi, _live),
          f"retired={_overlaps(old, old_hi, retired)} "
          f"live={_overlaps(old, old_hi, _live)}")
    moved = dict(_flags)
    moved[name] = dict(pin, bit=old)
    check(f"validate() refuses {name} back on its retired bit",
          any('retired' in p for p in lv_manifest.validate(
              lv_manifest.Manifest(global_flags=moved,
                                   next_free=_manifest.next_free))))

_st = create_symbol_table()
_st.load_manifest(_manifest)
data, _ = compile_body("araminaSchedule = at_home;\n"
                       "if devonInRule {\n  araminaSchedule = chow_down;\n}",
                       _st)
check("araminaSchedule = at_home is push byte 1; pop global 0207h 2",
      bytes.fromhex('0A01 4F070202') in data, data.hex())
check("if devonInRule is push global 0058h 1",
      bytes.fromhex('4E580001') in data, data.hex())
check("no operand on the retired bits 0663h/04B6h",
      bytes.fromhex('630602') not in data and bytes.fromhex('B60401')
      not in data, data.hex())

# ── 2. retail evidence ─────────────────────────────────────────────────────
print("retail evidence (shared/data/USECODE.FLX)")
if not os.path.exists(RETAIL_FLX):
    print("  skip: retail USECODE.FLX not present")
else:
    from u8_flex import UsecodeFlexArchive
    from u8_usecode_disasm import UsecodeDisassembler
    flx = UsecodeFlexArchive(RETAIL_FLX)
    classes = {cid: data for cid, _, data in flx.all_classes()}
    disasm = UsecodeDisassembler()
    listings = {}

    def bytes_at(cid, off):
        if cid not in listings:
            listings[cid] = disasm.disassemble_class(classes[cid], cid)
        m = re.search(rf'^\s+{off:04X}: ((?:[0-9A-F]{{2}} )+)',
                      listings[cid], re.M)
        return m.group(1).replace(' ', '') if m else None

    for ident, val, cid, off, want in RETAIL_PINS:
        got = bytes_at(cid, off)
        check(f"{ident}: class {cid:04X} @{off:04X} is {want}", got == want,
              f"got {got}")
    for name, val, cid, off, want in CONST_PINS:
        got = bytes_at(cid, off)
        check(f"{name}: class {cid:04X} @{off:04X} is {want}", got == want,
              f"got {got}")
        table = (DMG_CONSTANTS if name.startswith('DMG_') else
                 STATUS_CONSTANTS if name in STATUS_CONSTANTS else
                 LITERAL_CONSTANTS if name in LITERAL_CONSTANTS else
                 DIR_CONSTANTS if name in DIR_CONSTANTS else
                 SCHEDULE_CONSTANTS)
        check(f"{name} pinned to {val}", table.get(name) == val)
    # LV kneel values: retail's 49 -> 50 realDoAnim pair. The anim byte is
    # the push right below the 2-byte receiver push (6F FC / 40 06).
    realdoanim = bytes.fromhex('5704027C05E715')
    for cid, down, up in LV_ANIM_PAIRS:
        d = classes[cid]
        for off, want in ((down, 49), (up, 50)):
            check(f"retail {cid:04X} @{off:04X}: realDoAnim anim {want}",
                  d[12 + off:12 + off + 7] == realdoanim
                  and d[12 + off - 4:12 + off - 2] == bytes([0x0A, want]),
                  d[12 + off - 4:12 + off + 7].hex())
    for name, cid, off, want in SHARED_FLAG_SITES:
        got = bytes_at(cid, off)
        check(f"{name}: class {cid:04X} @{off:04X} is {want}", got == want,
              f"got {got}")

    # ARAMINA compiled from its recovered source against the manifest
    # emits retail ARAMINA's global operands, in order: each name she
    # reads or writes is on the bit retail uses at the same site.
    src = next((p for p in (
        os.path.join(SRC_DIR, 'lv-patched', 'ARAMINA.UNK'),
        os.path.join(BASE_DIR, 'shared', 'data', 'lv-usecode', 'LOST VALE',
                     'ARAMINA.UNK'),
        os.path.join(BASE_DIR, 'shared', 'data', 'lv-usecode', 'UNK files',
                     'UNK', 'ARAMINA.UNK')) if os.path.exists(p)), None)
    if src is None:
        print("  skip: ARAMINA.UNK source not present")
    else:
        def global_ops(listing):
            return re.findall(r'(push|pop) global\t([0-9A-F]{4})h\t'
                              r'([0-9A-F]{2})h', listing)
        _st = create_symbol_table()
        _st.load_manifest(_manifest)
        # Standalone, the class lacks the build's routine libraries, so
        # the codegen warns about calls; global operands are unaffected.
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            ours = CodeGenerator(_st).generate_class(parse_file(src))
        got = global_ops(disasm.disassemble_class(bytes(ours), 0x040D))
        want = global_ops(disasm.disassemble_class(classes[0x040D], 0x040D))
        bad = [(i, g, w) for i, (g, w) in enumerate(zip(got, want)) if g != w]
        check(f"ARAMINA's {len(got)} global operands match retail 040D's "
              f"{len(want)}", len(got) == len(want) and not bad,
              str(bad[:5]))

ANIM_DAT = os.path.join(BASE_DIR, 'shared', 'data', 'u8-install', 'STATIC',
                        'ANIM.DAT')
print("ANIM.DAT (kneel actions)")
if not os.path.exists(ANIM_DAT):
    print("  skip: STATIC/ANIM.DAT not present")
else:
    import struct
    ad = open(ANIM_DAT, 'rb').read()

    def frames(shape, action, facing=4):
        """Frame numbers of one action, one facing (AnimDat::load)."""
        base = struct.unpack_from('<I', ad, 4 * shape)[0]
        at = struct.unpack_from('<I', ad, base + 4 * action)[0]
        if not at:
            return None
        size = ad[at]
        pos = at + 4 + facing * size * 6
        return [ad[pos + 6 * j] + ((ad[pos + 6 * j + 1] & 7) << 8)
                for j in range(size)]

    stand = frames(1, ANIM_CONSTANTS['AS_STAND'])
    down = frames(1, LV_ANIM_CONSTANTS['AS_KNEEL_DOWN'])
    up = frames(1, LV_ANIM_CONSTANTS['AS_KNEEL_UP'])
    check("Avatar AS_KNEEL_DOWN goes down into the kneel up rises from",
          down and up and down[-1] == up[0] and down[0] == up[-2],
          f"{down} {up}")
    check("Avatar AS_KNEEL_UP ends on the AS_STAND frame",
          up and stand and up[-1] == stand[-1], f"{up} {stand}")
    check("Ezrekal's shape 200 has both kneel actions",
          frames(200, 49) and frames(200, 50))
print(f"\n{'OK' if FAIL == 0 else 'FAILED'}: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
