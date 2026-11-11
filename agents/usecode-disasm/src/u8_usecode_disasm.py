#!/usr/bin/env python3
"""
u8_usecode_disasm.py — Disassembler for Ultima 8 usecode bytecode.

Reads raw usecode class data (from USECODE.FLX via u8_flex.py) and produces
human-readable assembly listings with symbolic intrinsic names.

Format spec: agents/usecode-disasm/docs/usecode-format.md
Primary reference: Pentagram UCMachine.cpp

Usage:
    from u8_usecode_disasm import UsecodeDisassembler
    disasm = UsecodeDisassembler()
    listing = disasm.disassemble_class(class_data, classid=0x123, class_name="FOO")

    # Or from USECODE.FLX:
    from u8_flex import UsecodeFlexArchive
    flx = UsecodeFlexArchive("USECODE.FLX")
    for classid, name, data in flx.all_classes():
        listing = disasm.disassemble_class(data, classid, name)
"""

import struct
from io import BytesIO

# ─── U8 Intrinsic names ──────────────────────────────────────────────────────
# From ConvertUsecodeU8::_intrinsics[] in pentagram convert/u8/ConvertUsecodeU8.h

U8_INTRINSICS = [
    # 0x0000
    "process target()",
    "Item::getNext()",
    "Item::touch()",
    "word Item::getX()",
    "word Item::getY()",
    "word Item::getZ()",
    "word Item::getCX()",
    "word Item::getCY()",
    "word Item::getCZ()",
    "word Item::getGumpX()",
    "word Item::getGumpY()",
    "void Item::setGumpXY(word x, word y)",
    "Item::getPoint(WorldPoint*)",
    "uword Item::getType()",
    "void Item::setType(uword type)",
    "uword Item::getFrame()",
    # 0x0010
    "void Item::setFrame(uword frame)",
    "uword Item::getQuality()",
    "uword Item::getUnkEggType()",
    "uword Item::getQuantity()",
    "Item::getContents()",
    "Item::getContainer()",
    "Item::getRootContainer()",
    "uword Item::getGlobNum()",
    "void Item::setGlobNum(uword)",
    "uword Item::getQ()",
    "void Item::setQ(uword)",
    "void Item::setQuality(word value)",
    "void Item::setUnkEggType(word value)",
    "void Item::setQuantity(word value)",
    "word Item::getFamily()",
    "bool Item::getTypeFlag(word bit)",
    # 0x0020
    "word Item::getStatus()",
    "void Item::orStatus(word mask)",
    "void Item::andStatus(word mask)",
    "Item::getFootpad(word*, word*, word*)",
    "Item::touches(uword)",
    "Item::overlaps(uword)",
    "Item::overlapsXY(uword)",
    "Item::isOn(uword)",
    "Item::isCompletelyOn(uword)",
    "Item::isAbove(uword)",
    "Item::isUnder(uword)",
    "Item::ascend(word)",
    "Item::getWeight()",
    "Item::getWeightIncludingContents()",
    "Item::getSurfaceWeight()",
    "Item::getVolume()",
    # 0x0030
    "Item::getCapacity()",
    "Item::legal_create(uword, uword, uword, uword, uword)",
    "Item::create(uword, uword)",
    "Item::legal_create(uword, uword, WorldPoint*)",
    "Item::legal_create(uword, uword, uword, word)",
    "Item::push()",
    "Item::pop(uword, uword, ubyte)",
    "Item::pop(uword)",
    "Item::pop()",
    "Item::popToEnd(uword)",
    "Item::destroy()",
    "Item::removeContents()",
    "Item::destroyContents()",
    "Item::isExplosive()",
    "Item::move(uword, uword, ubyte)",
    "Item::move(WorldPoint*)",
    # 0x0040
    "Item::legal_move(WorldPoint*, uword, uword)",
    "Item::legal_move(uword*, uword)",
    "Item::isNpc()",
    "Item::isInNpc()",
    "process Item::hurl(word, word, word, word)",
    "Item::shoot(WorldPoint*, word, word)",
    "Item::fall()",
    "Item::grab()",
    "Item::findTarget(word, word)",
    "process Item::bark(char* str)",
    "strptr process Item::ask(uword slist)",
    "word Item::getSliderInput(word min, word max, word step)",
    "Item::openGump(word)",
    "Item::closeGump()",
    "Item::isGumpOpen()",
    "Item::getNpcArray()",
    # 0x0050
    "Item::getMapArray()",
    "Item::setNpcArray(word)",
    "Item::setMapArray(word)",
    "Item::receiveHit(uword, byte, word, uword)",
    "Item::explode()",
    "Item::canReach(uword, word)",
    "Item::getRange(uword)",
    "Item::getRange(uword, uword, uword)",
    "Item::getDirToCoords(uword, uword)",
    "Item::getDirFromCoords(uword, uword)",
    "Item::getDirToItem(uword)",
    "Item::getDirFromItem(uword)",
    "process Item::look()",
    "process Item::use()",
    "process Item::anim()",
    "process Item::cachein()",
    # 0x0060
    "Item::hit(uword, word)",
    "process Item::gotHit(uword, word)",
    "process Item::release()",
    "process Item::equip()",
    "process Item::unequip()",
    "process Item::combine()",
    "process Item::calledFromAnim()",
    "process Item::enterFastArea()",
    "process Item::leaveFastArea()",
    "process Item::cast(uword)",
    "process Item::justMoved()",
    "process Item::AvatarStoleSomething(uword)",
    "process Item::animGetHit(uword)",
    "process Item::guardianBark(word)",
    "process Book::read(char*)",
    "process Scroll::read(char*)",
    # 0x0070
    "process Grave::read(word,char*)",
    "process Plaque::read(word,char*)",
    "Egg::getEggXRange()",
    "Egg::getEggYRange()",
    "Egg::setEggXRange(uword)",
    "Egg::setEggYRange(uword)",
    "Egg::getEggId()",
    "Egg::setEggId(uword)",
    "Egg::hatch()",
    "MonsterEgg::hatch()",
    "MonsterEgg::getMonId()",
    "MonsterEgg::getActivity()",
    "MonsterEgg::getShapeType()",
    "MonsterEgg::setMonId(word)",
    "MonsterEgg::setActivity(word)",
    "MonsterEgg::setShapeType(word)",
    # 0x0080
    "Npc::isBusy()",
    "Npc::areEnemiesNear()",
    "Npc::isInCombat()",
    "Npc::setInCombat()",
    "Npc::clrInCombat()",
    "Npc::setTarget(uword)",
    "Npc::getTarget()",
    "Npc::setAlignment(ubyte)",
    "Npc::getAlignment()",
    "Npc::setEnemyAlignment(ubyte)",
    "Npc::getEnemyAlignment()",
    "Npc::isEnemy(uword)",
    "Npc::isDead()",
    "Npc::setDead()",
    "Npc::clrDead()",
    "Npc::isImmortal()",
    # 0x0090
    "Npc::setImmortal()",
    "Npc::clrImmortal()",
    "Npc::isWithstandDeath()",
    "Npc::setWithstandDeath()",
    "Npc::clrWithstandDeath()",
    "Npc::isFeignDeath()",
    "Npc::setFeignDeath()",
    "Npc::clrFeignDeath()",
    "Npc::freeEquip(uword)",
    "Npc::clearEquip()",
    "Npc::getNpcSlot()",
    "Npc::freeNpcSlot()",
    "Npc::getDir()",
    "Npc::getMap()",
    "Npc::teleport(uword, uword, ubyte, ubyte)",
    "process Npc::doAnim(AnimSet, word, word, ubyte)",
    # 0x00A0
    "Npc::getLastAnimSet()",
    "process Npc::pathfind(uword, uword, uword, uword)",
    "process Npc::pathfind(uword, uword)",
    "byte Npc::getStr()",
    "byte Npc::getInt()",
    "byte Npc::getDex()",
    "ubyte Npc::getHp()",
    "word Npc::getMana()",
    "void Npc::setStr(byte str)",
    "void Npc::setInt(byte int)",
    "void Npc::setDex(byte dex)",
    "void Npc::setHp(ubyte hp)",
    "void Npc::setMana(word mana)",
    "Npc::create(uword, uword)",
    "process Npc::cSetActivity(Activity)",
    "Npc::setAirWalkEnabled(ubyte)",
    # 0x00B0
    "Npc::getAirWalkEnabled()",
    "Npc::schedule(ulong)",
    "Npc::getEquip(word)",
    "Npc::setEquip(word, uword)",
    "closeAllGumps()",
    "process Camera::scrollTo(uword, uword, ubyte, word)",
    "urandom(word)",
    "rndRange(word,word)",
    "castGrantPeaceSpell()",
    "numToStr(uword)",
    "strToNum(char*)",
    "playMusic(byte)",
    "getName()",
    "igniteChaos(uword, uword, ubyte)",
    "Camera::setCenterOn(uword)",
    "Camera::move_to(uword, uword, ubyte, word)",
    # 0x00C0
    "Camera::move_rel(word, word, word)",
    "Camera::set_roof(word)",
    "Camera::roof()",
    "Camera::getX()",
    "Camera::getY()",
    "Camera::getZ()",
    "Camera::startQuake(word)",
    "Camera::stopQuake()",
    "Camera::invertScreen(ubyte)",
    "U8MousePointer::getDir()",
    "Kernel::getNumProcesses(uword, ProcessType)",
    "Kernel::resetRef(uword, ProcessType)",
    "process teleportToEgg(word, word, ubyte)",
    "resetRef(uword, uword)",
    "setRef(uword, uword, uword)",
    "getAvatarInStasis()",
    # 0x00D0
    "setAvatarInStasis(word)",
    "getEtherealTop()",
    "getCurrentTimerTick()",
    "canGetThere(uword, uword, uword)",
    "canExistAt(uword, uword, uword, uword, ubyte, uword, word)",
    "createSprite(word, word, word, word, word, word, uword, uword, ubyte)",
    "createSprite(word, word, word, word, uword, uword, ubyte)",
    "word getFamilyOfType(uword type)",
    "TimeInGameHours()",
    "TimeInMinutes()",
    "TimeInSeconds()",
    "SetTimeInGameHours(word)",
    "SetTimeInMinutes(long)",
    "SetTimeInSeconds(long)",
    "process FadeToBlack()",
    "process FadeFromBlack()",
    # 0x00E0
    "process FadeToPalette(word, word)",
    "process LightningBolt()",
    "process FadeToWhite()",
    "process FadeFromWhite()",
    "playEndgame()",
    "FeedAvatar(word)",
    "AccumulateStrength(word)",
    "AccumulateIntelligence(word)",
    "AccumulateDexterity(word)",
    "ClrAvatarInCombat()",
    "SetAvatarInCombat()",
    "IsAvatarInCombat()",
    "playSFX(word)",
    "playSFX(word, ubyte)",
    "playSFX(word, word, uword)",
    "playAmbientSFX(word)",
    # 0x00F0
    "playAmbientSFX(word, word)",
    "playAmbientSFX(word, word, uword)",
    "isSFXPlaying(word)",
    "setVolumeSFX(word, word)",
    "stopSFX(word)",
    "stopSFX(word, uword)",
    "soundInit(word, word, word)",
    "soundDeInit()",
    "musicStop()",
    "musicSlowStop()",
    "musicPlay(word)",
    "TonysBalls(word, word, uword, uword, uword)",
    "AvatarCanCheat()",
    "MakeAvatarACheater()",
    "isGameRunning()",
    "unused_00FF",
    # 0x0100
    "unused_0100",
    "unused_0101",
]

# ─── U8 Event names ──────────────────────────────────────────────────────────

U8_EVENTS = [
    "look()",                       # 0x00
    "use()",                        # 0x01
    "anim()",                       # 0x02
    "setActivity()",                # 0x03
    "cachein()",                    # 0x04
    "hit(uword, word)",             # 0x05
    "gotHit(uword, word)",          # 0x06
    "hatch()",                      # 0x07
    "schedule()",                   # 0x08
    "release()",                    # 0x09
    "equip()",                      # 0x0A
    "unequip()",                    # 0x0B
    "combine()",                    # 0x0C
    "func0D",                       # 0x0D
    "calledFromAnim()",             # 0x0E
    "enterFastArea()",              # 0x0F
    "leaveFastArea()",              # 0x10
    "cast(uword)",                  # 0x11
    "justMoved()",                  # 0x12
    "AvatarStoleSomething(uword)",  # 0x13
    "animGetHit()",                 # 0x14
    "guardianBark(word)",           # 0x15
    "func16",                       # 0x16
    "func17",                       # 0x17
    "func18",                       # 0x18
    "func19",                       # 0x19
    "func1A",                       # 0x1A
    "func1B",                       # 0x1B
    "func1C",                       # 0x1C
    "func1D",                       # 0x1D
    "func1E",                       # 0x1E
    "func1F",                       # 0x1F
]

# ─── Opcode definitions ──────────────────────────────────────────────────────
# Each entry: (mnemonic, operand_format)
# Operand format chars:
#   b = sint8 displayed as BP offset: [BP+xxh]
#   p = sint8 displayed as SP offset: [SP+xxh]
#   v = sint8 displayed as signed literal value
#   B = uint8 displayed as hex literal
#   w = uint16 displayed as hex
#   W = sint16 displayed as jump target (relative offset)
#   d = uint32 displayed as hex
#   s = string (preceded by uint16 length, followed by 0x00 terminator)

OPCODES = {
    0x00: ("pop byte",      "b"),      # pop word, store low byte at [BP+xx]
    0x01: ("pop",           "b"),      # pop word into [BP+xx]
    0x02: ("pop dword",     "b"),      # pop dword into [BP+xx]
    0x03: ("pop huge",      "bB"),     # pop yy bytes into [BP+xx]
    0x08: ("pop result",    ""),       # pop dword into process result
    0x09: ("assign elem",   "bBB"),    # pop into list element; bp_off, size, slist_flag
    0x0A: ("push byte",     "v"),      # push sign-extended byte as word (LITERAL)
    0x0B: ("push",          "w"),      # push word
    0x0C: ("push dword",    "d"),      # push dword
    0x0D: ("push string",   "s"),      # push string
    0x0E: ("create list",   "BB"),     # create list: elem_size, count
    0x0F: ("calli",         "Bw"),     # intrinsic call: arg_bytes, func_id
    0x11: ("call",          "ww"),     # call class:offset
    0x12: ("pop temp",      ""),       # pop word into temp
    0x13: ("pop long temp", ""),       # pop dword into temp
    0x14: ("add",           ""),       # 16-bit add
    0x15: ("add long",      ""),       # 32-bit add
    0x16: ("concat",        ""),       # concatenate strings
    0x17: ("append",        ""),       # append lists
    0x19: ("union slist",   "B"),      # union string lists
    0x1A: ("subtract slist","B"),      # subtract string list
    0x1B: ("subtract list", "B"),      # subtract list
    0x1C: ("sub",           ""),       # 16-bit subtract
    0x1D: ("sub long",      ""),       # 32-bit subtract
    0x1E: ("mul",           ""),       # 16-bit multiply
    0x1F: ("mul long",      ""),       # 32-bit multiply
    0x20: ("div",           ""),       # 16-bit divide
    0x21: ("div long",      ""),       # 32-bit divide
    0x22: ("mod",           ""),       # 16-bit modulo
    0x23: ("mod long",      ""),       # 32-bit modulo
    0x24: ("cmp",           ""),       # 16-bit equals
    0x25: ("cmp long",      ""),       # 32-bit equals
    0x26: ("strcmp",         ""),      # string compare
    0x28: ("lt",            ""),       # 16-bit less than
    0x29: ("lt long",       ""),       # 32-bit less than
    0x2A: ("le",            ""),       # 16-bit less or equal
    0x2B: ("le long",       ""),       # 32-bit less or equal
    0x2C: ("gt",            ""),       # 16-bit greater than
    0x2D: ("gt long",       ""),       # 32-bit greater than
    0x2E: ("ge",            ""),       # 16-bit greater or equal
    0x2F: ("ge long",       ""),       # 32-bit greater or equal
    0x30: ("not",           ""),       # boolean NOT
    0x31: ("not long",      ""),       # 32-bit boolean NOT
    0x32: ("and",           ""),       # boolean AND
    0x33: ("and long",      ""),       # 32-bit boolean AND
    0x34: ("or",            ""),       # boolean OR
    0x35: ("or long",       ""),       # 32-bit boolean OR
    0x36: ("ne",            ""),       # 16-bit not-equal
    0x37: ("ne long",       ""),       # 32-bit not-equal
    0x38: ("in list",       "BB"),     # test element in list: elem_size, slist_flag
    0x39: ("bit_and",       ""),       # bitwise AND
    0x3A: ("bit_or",        ""),       # bitwise OR
    0x3B: ("bit_not",       ""),       # bitwise NOT
    0x3C: ("lsh",           ""),       # left shift
    0x3D: ("rsh",           ""),       # right shift
    0x3E: ("push byte",     "b"),      # push byte var at [BP+xx]
    0x3F: ("push",          "b"),      # push word var at [BP+xx]
    0x40: ("push dword",    "b"),      # push dword var at [BP+xx]
    0x41: ("push string",   "b"),      # push string var at [BP+xx] (duplicate)
    0x42: ("push list",     "bB"),     # push list at [BP+xx]
    0x43: ("push slist",    "b"),      # push string list at [BP+xx]
    0x44: ("push element",  "BB"),     # push indexed element
    0x45: ("push huge",     "bB"),     # push yy bytes from [BP+xx]
    0x4B: ("push addr",     "b"),      # push pointer to [BP+xx]
    0x4C: ("push indirect", "B"),      # deref pointer, push xx bytes
    0x4D: ("pop indirect",  "B"),      # deref pointer, pop xx bytes
    0x4E: ("push global",   "wB"),     # push global bit-field
    0x4F: ("pop global",    "wB"),     # pop into global bit-field
    0x50: ("ret",           ""),       # return from function
    0x51: ("jne",           "W"),      # jump if false (relative)
    0x52: ("jmp",           "W"),      # unconditional jump (relative)
    0x53: ("suspend",       ""),       # yield execution
    0x54: ("implies",       "BB"),     # link processes (always 01 01)
    0x57: ("spawn",         "BBww"),   # spawn process: arg_bytes, this_size, class, offset
    0x58: ("spawn inline",  "wwwBB"),  # spawn inline: class, offset, delta, this_size, unk
    0x59: ("push pid",      ""),       # push process ID
    0x5A: ("init",          "B"),      # allocate local vars
    0x5B: ("line",          "w"),      # source line number
    0x5C: ("symbol",        "w"),      # debug symbol info (special handling)
    0x5D: ("push byte retval",""),     # push low 8 bits of retval
    0x5E: ("push retval",   ""),       # push low 16 bits of retval
    0x5F: ("push long retval",""),     # push 32-bit retval
    0x60: ("int to long",   ""),       # sign-extend 16→32
    0x61: ("long to int",   ""),       # truncate 32→16
    0x62: ("free string",   "b"),      # free string at [BP+xx]
    0x63: ("free slist",    "b"),      # free string list at [BP+xx]
    0x64: ("free list",     "b"),      # free list at [BP+xx]
    0x65: ("free string",   "p"),      # free string at [SP+xx]
    0x66: ("free list",     "p"),      # free list at [SP+xx]
    0x67: ("free slist",    "p"),      # free string list at [SP+xx]
    0x69: ("str to ptr",    "b"),      # string at [BP+xx] to pointer
    0x6B: ("str to ptr",    ""),       # pop string, push pointer
    0x6C: ("param pid chg", "bB"),     # copy param for spawned process
    0x6D: ("push process result",""),  # push 32-bit process result
    0x6E: ("add sp",        "v"),      # adjust stack pointer by signed value
    0x6F: ("push addr",     "p"),      # push pointer to [SP-xx]
    0x70: ("loop",          "bBB"),    # init object search loop
    0x73: ("loopnext",      ""),       # next loop item
    0x74: ("loopscr",       "B"),      # append byte to loop script
    0x75: ("for each",      "bBW"),    # iterate list
    0x76: ("for each str",  "bBW"),    # iterate string list
    0x77: ("set info",      ""),       # set item_num and type
    0x78: ("process exclude",""),      # exclusive process access
    0x79: ("end",           ""),       # end of function (U8)
    0x7A: ("end",           ""),       # end of function (Crusader)
}


def _bp_str(val):
    """Format a signed BP offset."""
    signed = val if val < 128 else val - 256
    if signed >= 0:
        return f"[BP+{signed:02X}h]"
    else:
        return f"[BP-{-signed:02X}h]"


def _sp_str(val):
    """Format a signed SP offset."""
    signed = val if val < 128 else val - 256
    if signed >= 0:
        return f"[SP+{signed:02X}h]"
    else:
        return f"[SP-{-signed:02X}h]"


class DisassemblyError(Exception):
    pass


class Instruction:
    """A single disassembled instruction."""

    __slots__ = ('offset', 'opcode', 'mnemonic', 'operands', 'raw_bytes',
                 'comment', 'is_jump_target')

    def __init__(self, offset, opcode, mnemonic, operands, raw_bytes, comment=''):
        self.offset = offset
        self.opcode = opcode
        self.mnemonic = mnemonic
        self.operands = operands  # list of (format_char, value) pairs
        self.raw_bytes = raw_bytes
        self.comment = comment
        self.is_jump_target = False

    def format_operands(self):
        """Return formatted operand string."""
        parts = []
        for fmt, val in self.operands:
            if fmt == 'b':
                parts.append(_bp_str(val))
            elif fmt == 'p':
                parts.append(_sp_str(val))
            elif fmt == 'v':
                # Signed 8-bit literal value
                signed = val if val < 128 else val - 256
                parts.append(f"{signed:+d} ({val:02X}h)")
            elif fmt == 'B':
                parts.append(f"{val:02X}h")
            elif fmt == 'w':
                parts.append(f"{val:04X}h")
            elif fmt == 'W':
                # Jump offset — show target address
                target = self.offset + len(self.raw_bytes) + val
                if val < 0:
                    parts.append(f"{val:+05X}h (-> {target:04X}h)")
                else:
                    parts.append(f"+{val:04X}h (-> {target:04X}h)")
            elif fmt == 'd':
                parts.append(f"{val:08X}h")
            elif fmt == 's':
                parts.append(f'"{val}"')
        return '\t'.join(parts) if parts else ''

    def __repr__(self):
        ops = self.format_operands()
        s = f"{self.offset:04X}: {self.mnemonic}"
        if ops:
            s += f"\t{ops}"
        if self.comment:
            s += f"\t; {self.comment}"
        return s


class UsecodeClass:
    """Parsed structure of a usecode class."""

    def __init__(self, classid, name, data):
        self.classid = classid
        self.name = name or f"Class_{classid:04X}"
        self.raw_data = data

        if len(data) < 12:
            raise DisassemblyError(f"Class {classid:04X}: data too short ({len(data)} bytes)")

        # Parse header
        self.unknown1 = struct.unpack_from('<I', data, 0)[0]
        self.total_size = struct.unpack_from('<I', data, 4)[0]
        self.unknown2 = struct.unpack_from('<I', data, 8)[0]

        self.base_offset = 0x0C  # always 0x0C for U8

        # Parse event table (32 events × 4 bytes)
        self.events = {}
        if len(data) >= self.base_offset + 128:
            for i in range(32):
                offset = struct.unpack_from('<I', data, self.base_offset + i * 4)[0]
                if offset != 0:
                    self.events[i] = offset

        # Bytecode area — use total_size to determine actual extent
        # total_size field gives the full class size; bytecode is total_size - header
        bytecode_size = self.total_size - self.base_offset
        # Clamp to actual data available
        bytecode_size = min(bytecode_size, len(data) - self.base_offset)
        self.bytecode = data[self.base_offset:self.base_offset + bytecode_size]

    def event_name(self, event_id):
        if event_id < len(U8_EVENTS):
            return U8_EVENTS[event_id]
        return f"event_{event_id:02X}"


class UsecodeDisassembler:
    """Disassemble U8 usecode bytecode."""

    def __init__(self):
        self.intrinsics = U8_INTRINSICS

    def _read_operands(self, stream, fmt, offset):
        """Read operands from stream according to format string."""
        operands = []
        for c in fmt:
            if c in ('b', 'p', 'v'):  # uint8 (displayed as BP offset, SP offset, or literal)
                val = struct.unpack('B', stream.read(1))[0]
                operands.append((c, val))
            elif c == 'B':  # uint8
                val = struct.unpack('B', stream.read(1))[0]
                operands.append(('B', val))
            elif c == 'w':  # uint16
                val = struct.unpack('<H', stream.read(2))[0]
                operands.append(('w', val))
            elif c == 'W':  # sint16 (jump offset)
                val = struct.unpack('<h', stream.read(2))[0]
                operands.append(('W', val))
            elif c == 'd':  # uint32
                val = struct.unpack('<I', stream.read(4))[0]
                operands.append(('d', val))
            elif c == 's':  # string (uint16 length + data + 0x00)
                length = struct.unpack('<H', stream.read(2))[0]
                string_data = stream.read(length)
                terminator = stream.read(1)  # null terminator
                try:
                    s = string_data.decode('ascii', errors='replace')
                except Exception:
                    s = repr(string_data)
                operands.append(('s', s))
        return operands

    def _make_comment(self, opcode, operands):
        """Generate a helpful comment for an instruction."""
        if opcode == 0x0F:  # calli
            func_id = operands[1][1]
            if func_id < len(self.intrinsics):
                return self.intrinsics[func_id]
            return f"intrinsic_{func_id:04X}"
        elif opcode == 0x11:  # call
            classid = operands[0][1]
            offset = operands[1][1]
            return f"class {classid:04X} offset {offset:04X}"
        elif opcode == 0x57:  # spawn
            classid = operands[2][1]
            offset = operands[3][1]
            return f"class {classid:04X} offset {offset:04X}"
        elif opcode == 0x58:  # spawn inline
            classid = operands[0][1]
            offset = operands[1][1]
            delta = operands[2][1]
            return f"class {classid:04X} offset {offset:04X}+{delta:04X}={offset+delta:04X}"
        elif opcode == 0x4E:  # push global
            return f"global bit offset {operands[0][1]:04X}, {operands[1][1]} bits"
        elif opcode == 0x4F:  # pop global
            return f"global bit offset {operands[0][1]:04X}, {operands[1][1]} bits"
        elif opcode == 0x0D:  # push string
            return ""  # string is self-documenting
        elif opcode == 0x70:  # loop
            search_types = {2: "area", 3: "area+recursive", 4: "container",
                          5: "container+recursive", 6: "surface"}
            st = operands[2][1]
            return f"search type: {search_types.get(st, f'unknown({st})')}"
        elif opcode == 0x6C:  # param pid chg
            types = {1: "string", 2: "slist", 3: "list"}
            t = operands[1][1]
            return f"copy {types.get(t, f'type({t})')} for spawned process"
        # SP-relative opcodes now use 'p' format, no extra comment needed
        # 0x6E (add sp) uses 'v' format, also self-documenting
        return ""

    def disassemble_bytecode(self, bytecode, start_offset=0):
        """Disassemble raw bytecode bytes into a list of Instructions.

        Args:
            bytecode: raw bytes of bytecode
            start_offset: byte offset within bytecode to begin disassembly
                          (e.g., 0x80 to skip the 128-byte event table)
        Returns:
            list of Instruction objects
        """
        stream = BytesIO(bytecode)
        stream.seek(start_offset)
        instructions = []
        jump_targets = set()

        while stream.tell() < len(bytecode):
            offset = stream.tell()
            raw_start = offset

            byte = stream.read(1)
            if not byte:
                break
            opcode = byte[0]

            if opcode not in OPCODES:
                # Unknown opcode — emit as data byte
                raw = bytes([opcode])
                instr = Instruction(offset, opcode, f"db", [('B', opcode)], raw,
                                  f"unknown opcode {opcode:02X}")
                instructions.append(instr)
                continue

            mnemonic, fmt = OPCODES[opcode]

            # Special handling for 0x5C (symbol info) — reads 9-byte name + null
            if opcode == 0x5C:
                off_val = struct.unpack('<H', stream.read(2))[0]
                name_bytes = stream.read(9)  # 8 chars + null
                try:
                    name = name_bytes.rstrip(b'\x00').decode('ascii', errors='replace')
                except Exception:
                    name = repr(name_bytes)
                raw = bytecode[raw_start:stream.tell()]
                # Calculate actual debug offset
                dbg_offset = offset + 3 + struct.unpack('<h', struct.pack('<H', off_val))[0]
                instr = Instruction(offset, opcode, mnemonic,
                                  [('w', off_val), ('s', name)], raw,
                                  f"debug offset={dbg_offset:04X}, class name=\"{name}\"")
                instructions.append(instr)
                continue

            operands = self._read_operands(stream, fmt, offset)
            raw = bytecode[raw_start:stream.tell()]
            comment = self._make_comment(opcode, operands)

            instr = Instruction(offset, opcode, mnemonic, operands, raw, comment)
            instructions.append(instr)

            # Track jump targets
            if opcode in (0x51, 0x52):  # jne, jmp
                jump_val = operands[0][1]  # sint16
                target = stream.tell() + jump_val
                jump_targets.add(target)
            elif opcode in (0x75, 0x76):  # for each / for each str
                jump_val = operands[2][1]  # sint16
                target = stream.tell() + jump_val
                jump_targets.add(target)

            # 0x79/0x7A mark end of a function within the class.
            # A class can contain multiple functions (one per event handler),
            # so we do NOT stop here. Only the LAST end in the class marks
            # the true end. We continue until out of bytecode.

        # Mark jump targets
        for instr in instructions:
            if instr.offset in jump_targets:
                instr.is_jump_target = True

        return instructions

    def disassemble_class(self, class_data, classid=0, class_name=None):
        """Disassemble a complete usecode class.

        Args:
            class_data: raw bytes of the class (from USECODE.FLX)
            classid: class ID number
            class_name: optional class name string
        Returns:
            formatted string with complete disassembly listing
        """
        uc = UsecodeClass(classid, class_name, class_data)
        # Event table is 32×4=128=0x80 bytes; actual bytecode starts after it
        EVENT_TABLE_SIZE = 0x80
        instructions = self.disassemble_bytecode(uc.bytecode, start_offset=EVENT_TABLE_SIZE)

        # Build event offset → event info mapping
        event_labels = {}
        for event_id, offset in uc.events.items():
            event_labels[offset] = (event_id, uc.event_name(event_id))

        # Format output
        lines = []
        lines.append(f"; ═══════════════════════════════════════════════════")
        lines.append(f"; Class {classid:04X}: {uc.name}")
        lines.append(f"; Size: {len(class_data)} bytes  Bytecode: {len(uc.bytecode)} bytes")
        lines.append(f"; Header: unknown1={uc.unknown1:08X} total_size={uc.total_size:08X} unknown2={uc.unknown2:08X}")
        lines.append(f"; ═══════════════════════════════════════════════════")
        lines.append("")

        # Event table
        if uc.events:
            lines.append("; Event table:")
            for event_id in sorted(uc.events.keys()):
                offset = uc.events[event_id]
                lines.append(f";   Event {event_id:02X} ({uc.event_name(event_id)}): offset {offset:04X}")
            lines.append("")

        # Instructions
        for instr in instructions:
            # Event label
            if instr.offset in event_labels:
                event_id, event_name = event_labels[instr.offset]
                lines.append("")
                lines.append(f"; ─── Event {event_id:02X}: {event_name} ───")

            # Jump target marker
            if instr.is_jump_target:
                lines.append(f"  .L{instr.offset:04X}:")

            # Hex bytes
            hex_bytes = ' '.join(f'{b:02X}' for b in instr.raw_bytes)

            # Format instruction
            ops = instr.format_operands()
            line = f"  {instr.offset:04X}: {hex_bytes:<24s} {instr.mnemonic}"
            if ops:
                line += f"\t{ops}"
            if instr.comment:
                line += f"\t; {instr.comment}"

            lines.append(line)

        return '\n'.join(lines) + '\n'

    def disassemble_class_summary(self, class_data, classid=0, class_name=None):
        """Return a brief summary of a usecode class (events, call targets, strings)."""
        uc = UsecodeClass(classid, class_name, class_data)
        EVENT_TABLE_SIZE = 0x80
        instructions = self.disassemble_bytecode(uc.bytecode, start_offset=EVENT_TABLE_SIZE)

        summary = {
            'classid': classid,
            'name': uc.name,
            'size': len(class_data),
            'events': {eid: uc.event_name(eid) for eid in sorted(uc.events.keys())},
            'intrinsic_calls': [],
            'class_calls': [],
            'spawns': [],
            # H3 (2026-07-25): 0x58 spawn-inline edges. ADDITIVE — a new key,
            # no existing key's contents change, so every current consumer is
            # unaffected. See the documented exception in CLAUDE.md: this
            # summary layer has exactly two consumers (this file's own
            # `summary` CLI command and u8_flag_graph.py) and is NOT on the
            # listing path the assembler round-trips against, so it cannot
            # affect round-trip byte-identity.
            #
            # In every FLX examined, 0x58's target class is the SAME class
            # (all 20 base-game edges are self-edges — spawn-inline starts a
            # coroutine within the class at offset+delta). The reachability
            # consumer must therefore NOT treat these as inbound references;
            # see inbound_total() in u8_flag_graph.py.
            'spawn_inline': [],
            'strings': [],
            'globals_read': [],
            'globals_written': [],
        }

        for instr in instructions:
            if instr.opcode == 0x0F:  # calli
                func_id = instr.operands[1][1]
                name = self.intrinsics[func_id] if func_id < len(self.intrinsics) else f"intrinsic_{func_id:04X}"
                summary['intrinsic_calls'].append((func_id, name))
            elif instr.opcode == 0x11:  # call
                target_class = instr.operands[0][1]
                target_offset = instr.operands[1][1]
                summary['class_calls'].append((target_class, target_offset))
            elif instr.opcode == 0x57:  # spawn
                target_class = instr.operands[2][1]
                target_offset = instr.operands[3][1]
                summary['spawns'].append((target_class, target_offset))
            elif instr.opcode == 0x58:  # spawn inline
                # Operands: class, offset, delta, this_size, unk. The entry
                # point is offset+delta, matching format_operands() above.
                target_class = instr.operands[0][1]
                target_offset = instr.operands[1][1] + instr.operands[2][1]
                summary['spawn_inline'].append((target_class, target_offset))
            elif instr.opcode == 0x0D:  # push string
                summary['strings'].append(instr.operands[0][1])
            elif instr.opcode == 0x4E:  # push global
                summary['globals_read'].append((instr.operands[0][1], instr.operands[1][1]))
            elif instr.opcode == 0x4F:  # pop global
                summary['globals_written'].append((instr.operands[0][1], instr.operands[1][1]))

        # Deduplicate
        summary['intrinsic_calls'] = sorted(set(summary['intrinsic_calls']))
        summary['class_calls'] = sorted(set(summary['class_calls']))
        summary['spawns'] = sorted(set(summary['spawns']))
        summary['spawn_inline'] = sorted(set(summary['spawn_inline']))
        summary['globals_read'] = sorted(set(summary['globals_read']))
        summary['globals_written'] = sorted(set(summary['globals_written']))

        return summary


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from u8_flex import UsecodeFlexArchive

    if len(sys.argv) < 2:
        print("Usage: u8_usecode_disasm.py <USECODE.FLX> [classid|all|summary]")
        print("  classid: hex class ID to disassemble (e.g. 0x123)")
        print("  all: disassemble all classes")
        print("  summary: print summary of all classes")
        sys.exit(1)

    flx_path = sys.argv[1]
    flx = UsecodeFlexArchive(flx_path)
    disasm = UsecodeDisassembler()

    mode = sys.argv[2] if len(sys.argv) > 2 else 'summary'

    if mode == 'all':
        for classid, name, data in flx.all_classes():
            try:
                listing = disasm.disassemble_class(data, classid, name)
                print(listing)
            except DisassemblyError as e:
                print(f"; ERROR: {e}")
            except Exception as e:
                print(f"; ERROR disassembling class {classid:04X}: {e}")

    elif mode == 'summary':
        print(f"USECODE.FLX: {flx.count} entries, {flx.class_count} classes")
        print()
        total_events = 0
        total_classes = 0
        for classid, name, data in flx.all_classes():
            try:
                summary = disasm.disassemble_class_summary(data, classid, name)
                total_classes += 1
                n_events = len(summary['events'])
                total_events += n_events
                events_str = ', '.join(f"{eid:02X}" for eid in summary['events'])
                strings_preview = '; '.join(summary['strings'][:3])
                if len(summary['strings']) > 3:
                    strings_preview += f' ... (+{len(summary["strings"])-3} more)'
                print(f"  {classid:04X} {name:>10s}  {n_events:2d} events [{events_str}]"
                      f"  {len(summary['intrinsic_calls']):3d} intrinsics"
                      f"  {len(summary['class_calls']):3d} calls"
                      f"  {len(summary['strings']):3d} strings")
                if strings_preview:
                    print(f"       strings: {strings_preview}")
            except Exception as e:
                print(f"  {classid:04X} {'ERROR':>10s}  {e}")
        print(f"\nTotal: {total_classes} classes, {total_events} event handlers")

    else:
        # Disassemble specific class
        classid = int(mode, 0)
        if not flx.class_exists(classid):
            print(f"Class {classid:04X} does not exist or is empty")
            sys.exit(1)
        data = flx.get_class_data(classid)
        name = flx.get_class_name(classid)
        listing = disasm.disassemble_class(data, classid, name)
        print(listing)


if __name__ == '__main__':
    main()
