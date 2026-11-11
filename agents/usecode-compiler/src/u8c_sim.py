#!/usr/bin/env python3
"""
u8c_sim.py — Headless U8 usecode simulator for pre-playtest vetting.

Executes classes out of the BUILT shared/build/EUSECODE.FLX with
engine-exact semantics, ported opcode-by-opcode from ScummVM's
uc_machine.cpp / uc_process.cpp / item.cpp (scummvm-lv checkout). The
point is to catch the "compiles clean, dies in-game" class of defect
without a human playtest: calling-convention mismatches, loopscript
byte order, pointer write-back, and family-dependent intrinsic
behavior are all reproduced faithfully.

Deliberately faithful details (each one caught a real in-game bug):
  - Intrinsic args are read FORWARD from the stack top (args pushed
    right-to-left, itemptr last).
  - `loop` (0x70) pops its operands as (ui16a=LAST pushed=center item /
    FFFF marker, ui16b=range / container) and pops the loopscript off
    the stack with a forward copy — reversed emission required.
  - Item::I_create writes the new objid back through a stack pointer
    (assignPointer); readers dereference via ptrToObject.
  - Item::I_getQuality returns the stored quality ONLY for SF_QUALITY
    (family 1) shapes and 0 otherwise; I_getQ is unconditional.
  - spawn (0x57) unconditionally pop4's a this pointer.
  - checkLoopScript ported verbatim, including the 'A'..'Z' optimized
    shape checks and 'a'..'z' frame checks.
  - Item::pop family (0x36/0x37/0x38/0x39): ARG_NULL32 first (the
    itemptr is unused — the popped item is the TOP of the ethereal
    void), then per-slot args; popToContainer moves into the container
    (step-7 repair: RAGNAR/HRODNY's bag-and-key drops).

The world is a fixture: SimItem objects with shape/frame/quality/
position/containment, with family and flags looked up in the REAL
TYPEFLAG.DAT so shape-semantics bugs surface here, not in-game.

Non-goals: scheduling (spawn/implies/suspend run synchronously with
spawns recorded, not executed, unless a test opts in), animation,
pathfinding, rendering.
"""

import os
import struct
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8_flex import FlexArchive  # noqa: E402

# The built FLX the simulator executes. LV_EUSECODE_FLX overrides it so a
# harness can be pointed at a TEMP build (build_eusecode.build(output_path=...))
# and verify source changes without clobbering the real shared/build artifact.
BUILD_FLX = (os.environ.get('LV_EUSECODE_FLX')
             or os.path.join(BASE_DIR, 'shared', 'build', 'EUSECODE.FLX'))
TYPEFLAG = os.path.join(BASE_DIR, 'shared', 'data', 'u8-install',
                        'STATIC', 'TYPEFLAG.DAT')

# UCMachine pointer segments (uc_machine.cpp:74-79)
SEG_STACK_FIRST = 0x0001
SEG_STACK_LAST = 0x7FFE
SEG_STRING = 0x8000
SEG_OBJ = 0x8002
SEG_GLOBAL = 0x8003

# TYPEFLAG families (ShapeInfo)
SF_GENERIC = 0
SF_QUALITY = 1
SF_QUANTITY = 2
SF_GLOBEGG = 3
SF_UNKEGG = 4
SF_BREAKABLE = 5
SF_CONTAINER = 6
SF_REAGENT = 9


class ShapeFlags:
    """Minimal TYPEFLAG.DAT reader (8 bytes/shape; layout mirrors
    agents/map-populator/src/parse_typeflag.py, kept local per the
    per-agent-copy convention)."""

    def __init__(self, path=TYPEFLAG):
        data = open(path, 'rb').read()
        self.records = [data[i:i + 8] for i in range(0, len(data), 8)]

    def flags0(self, shape):
        return self.records[shape][0]

    def family(self, shape):
        return (self.records[shape][1] >> 4) & 0x0F

    def footpad(self, shape):
        """ShapeInfo::getFootpadWorld, unflipped (shape_info.h:184):
        x/y in 32-unit cells, z in 8-unit steps (type_flags.cpp U8 rows:
        x = data[2] >> 4, y = data[3] & 0x0F, z = data[3] >> 4)."""
        r = self.records[shape]
        return (r[2] >> 4) * 32, (r[3] & 0x0F) * 32, (r[3] >> 4) * 8

    def blockflags(self, shape):
        """SI_SOLID (data[0] & 0x02) | SI_DAMAGING (data[0] & 0x40): the
        blockmask getPositionInfo tests overlaps against."""
        return self.records[shape][0] & 0x42


class SimItem:
    """A fixture world item. Family/flags come from real TYPEFLAG."""

    def __init__(self, objid, shape, frame=0, quality=0, quantity=0,
                 x=0, y=0, z=0, npcnum=0, mapnum=0):
        self.objid = objid
        self.shape = shape
        self.frame = frame
        # ENGINE-FAITHFUL: quality and quantity are the SAME backing field
        # (item.cpp: I_getQuantity/I_setQuantity call getQuality()/
        # setQuality() under a family gate; I_getQ/I_setQ read and write
        # the identical field unconditionally). `quantity=` exists only as
        # a readability alias for fixtures that build a reagent stack
        # (TypeReagent, SF_REAGENT, where the frame is the reagent's
        # identity): it sets this same attribute `quality=` sets, and the
        # `quantity` property below reads it back under that name.
        self.quality = quantity or quality
        self.x, self.y, self.z = x, y, z
        self.npcnum = npcnum
        self.mapnum = mapnum     # Actor::getMapNum (Npc::getMap intrinsic)
        self.contents = []       # objids
        self.parent = None       # objid of container
        self.destroyed = False
        self.ethereal = False
        # Actor equipment: {raw getEquip slot arg -> objid}. The engine's
        # Actor::I_getEquip does getEquip(type+1) internally; the sim keys
        # by the RAW intrinsic argument (EQ_BACKPACK=6 etc), so tests set
        # avatar.equipment[6] = pack.objid.
        self.equipment = {}

    @property
    def quantity(self):
        return self.quality

    @quantity.setter
    def quantity(self, value):
        self.quality = value


class SimWorld:
    def __init__(self):
        self.items = {}
        self._next_objid = 0x100
        self.ethereal_stack = []   # engine's ethereal void (create/pop)
        self.shapeflags = ShapeFlags()

    def add(self, shape, **kw):
        objid = kw.pop('objid', None) or self._alloc()
        it = SimItem(objid, shape, **kw)
        self.items[objid] = it
        return it

    def _alloc(self):
        self._next_objid += 1
        return self._next_objid

    def get(self, objid):
        it = self.items.get(objid)
        if it is None or it.destroyed:
            return None
        return it

    def put_in_container(self, item, container):
        item.parent = container.objid
        container.contents.append(item.objid)

    # ── engine-port: Item::checkLoopScript (item.cpp:823) ──────────────
    def check_loop_script(self, item, script):
        stack = [1]  # default true if empty
        i = 0
        n = len(script)
        while i < n:
            op = script[i]
            if op == 0:
                stack.append(0)
            elif op == 1:
                stack.append(1)
            elif op == ord('$'):
                return stack.pop() != 0
            elif op == ord('%'):
                stack.append(script[i + 1] | (script[i + 2] << 8))
                i += 2
            elif op == ord('&'):
                a, b = stack.pop(), stack.pop()
                stack.append(1 if (a and b) else 0)
            elif op == ord('+'):
                a, b = stack.pop(), stack.pop()
                stack.append(1 if (a or b) else 0)
            elif op == ord('!'):
                a = stack.pop()
                stack.append(0 if a else 1)
            elif op == ord('?'):
                stack.append(0)  # status flags: not modeled
            elif op == ord('*'):
                stack.append(item.quality)
            elif op == ord('#'):
                stack.append(item.npcnum)
            elif op == ord('='):
                a, b = stack.pop(), stack.pop()
                stack.append(1 if a == b else 0)
            elif op == ord('>'):
                a, b = stack.pop(), stack.pop()
                stack.append(1 if b > a else 0)
            elif op == ord('<'):
                a, b = stack.pop(), stack.pop()
                stack.append(1 if b < a else 0)
            elif op == ord(']'):
                a, b = stack.pop(), stack.pop()
                stack.append(1 if b >= a else 0)
            elif op == ord('['):
                a, b = stack.pop(), stack.pop()
                stack.append(1 if b <= a else 0)
            elif op == ord(':'):
                stack.append(self.shapeflags.family(item.shape))
            elif op == ord('@'):
                stack.append(item.shape)
            elif ord('A') <= op <= ord('Z'):
                count = op - ord('@')
                match = 0
                for _ in range(count):
                    val = script[i + 1] | (script[i + 2] << 8)
                    if item.shape == val:
                        match = 1
                    i += 2
                stack.append(match)
            elif op == ord('`'):
                stack.append(item.frame)
            elif ord('a') <= op <= ord('z'):
                count = op - ord('`')
                match = 0
                for _ in range(count):
                    val = script[i + 1] | (script[i + 2] << 8)
                    if item.frame == val:
                        match = 1
                    i += 2
                stack.append(match)
            else:
                raise SimError(f'unknown loopscript token {op:#x}')
            i += 1
        return stack.pop() != 0

    def area_search(self, script, center_item, range_, recurse=False):
        """CurrentMap::areaSearch approximation: box range around the
        center item's location; skips contained, destroyed, ethereal."""
        cx, cy = center_item.x, center_item.y
        out = []
        for it in self.items.values():
            if it.destroyed or it.ethereal or it.parent is not None:
                continue
            if abs(it.x - cx) <= range_ and abs(it.y - cy) <= range_:
                if self.check_loop_script(it, script):
                    out.append(it.objid)
        return out

    def container_search(self, script, container, recurse):
        out = []
        for objid in list(container.contents):
            it = self.get(objid)
            if it is None:
                continue
            if self.check_loop_script(it, script):
                out.append(it.objid)
            if recurse and it.contents:
                out.extend(self.container_search(script, it, recurse))
        return out

    # ── engine-port: CurrentMap::I_canExistAt (current_map.cpp:1257) ───
    def can_exist_at(self, shape, x, y, z):
        """getPositionInfo(x, y, z, shape, 0).valid: the shape's footpad
        box, anchored at its max x/y corner and min z (Box, box.h), is
        invalid if it overlaps any world item whose SOLID/DAMAGING flags
        meet its own. Half-open on every axis (Box::overlaps). Support is
        not part of the answer, and id 0 excludes no item."""
        xd, yd, zd = self.shapeflags.footpad(shape)
        mask = self.shapeflags.blockflags(shape)
        for it in self.items.values():
            if it.destroyed or it.ethereal or it.parent is not None:
                continue
            if not self.shapeflags.blockflags(it.shape) & mask:
                continue
            ixd, iyd, izd = self.shapeflags.footpad(it.shape)
            if (x <= it.x - ixd or it.x <= x - xd
                    or y <= it.y - iyd or it.y <= y - yd
                    or z + zd <= it.z or it.z + izd <= z):
                continue
            return False
        return True


class SimError(Exception):
    pass


class UCSim:
    """One synchronous process execution against the built FLX."""

    STACK_SIZE = 0x1000

    def __init__(self, flx_path=BUILD_FLX, world=None, globals_bits=None,
                 trace=False):
        self.flx = FlexArchive(flx_path)
        self.world = world if world is not None else SimWorld()
        self.globals = globals_bits if globals_bits is not None \
            else bytearray(0x1000)
        self.trace = trace
        self.trace_log = []
        self.pid = 0x0123

        # Recorders — what the tests assert on.
        self.barks = []          # (objid, text)
        self.spawns = []         # dicts
        self.calls = []          # cross-class 0x11 calls
        self.intrinsic_log = []  # (name, args-tuple, result)
        self.warnings = []
        self.created = []        # objids created via I_create
        self.teleports = []      # {obj,x,y,z,map} per Actor::teleport call
        self.egg_teleports = []  # {map,egg} per teleportToEgg call
        self.strings = {}
        self._next_string = 1
        self._next_pid = 0x200

        # ── conversation machinery ──────────────────────────────────────
        # answer_script: queue of answer TEXTS the "player" picks at each
        # ask(). asks: log of (options_shown, answer_taken). call_returns:
        # canned retvals for cross-class 0x11 calls, keyed (class, offset).
        self.answer_script = []
        self.asks = []
        self.call_returns = {}
        self.process_result = 0  # p->_result, pushed by opcode 0x6D
        self.lists = {}
        self._next_list_id = 0x40
        self.follow_spawns = False  # dialogue tests opt in
        # urandom_script: queue of values the next urandom() calls return
        # (None = unscripted). urandom_rolls: log of (num, value) per call.
        # An unscripted roll is 0, which the engine can return for any num.
        self.urandom_script = []
        self.urandom_rolls = []
        # ── camera (CameraProcess, reduced to where it looks) ───────────
        # The game camera follows the Avatar until usecode says otherwise.
        # camera_follow: objid it tracks at (x, y, z + 20) (the "!!constant"
        # in camera_process.cpp:124/225), or None when parked at
        # camera_pos. camera_moves: (intrinsic, before, after) for every
        # call that re-aims it; setCenterOn and move_to are INSTANT (the
        # next frame draws from `after`), scrollTo glides over 25 frames.
        self.camera_follow = 1
        self.camera_pos = None
        self.camera_moves = []

        self._intrinsics = self._load_intrinsic_names()

    # ── intrinsic name table (from the compiler's own symbol table) ────
    def _load_intrinsic_names(self):
        from u8c_symbols import create_symbol_table
        table = {}
        self._intrinsic_argc = {}  # id -> declared parameter count
        st = create_symbol_table()
        for info in st.intrinsics.values():
            table[info.id] = info.name
            self._intrinsic_argc[info.id] = info.arg_count
        return table

    # ── globals (bit-granular, little-endian within the array) ─────────
    def get_global(self, bit_offset, bits):
        val = 0
        for i in range(bits):
            b = bit_offset + i
            if self.globals[b >> 3] & (1 << (b & 7)):
                val |= (1 << i)
        return val

    def set_global(self, bit_offset, bits, val):
        for i in range(bits):
            b = bit_offset + i
            if val & (1 << i):
                self.globals[b >> 3] |= (1 << (b & 7))
            else:
                self.globals[b >> 3] &= ~(1 << (b & 7))

    # ── pointers (uc_machine.cpp ptrToObject / assignPointer) ──────────
    def ptr_to_object(self, ptr):
        segment = (ptr >> 16) & 0xFFFF
        offset = ptr & 0xFFFF
        if SEG_STACK_FIRST <= segment <= SEG_STACK_LAST:
            if segment != self.pid:
                self.warnings.append(
                    f'ptrToObject into foreign stack pid {segment:#x}')
                return 0
            return self._stk_access2(offset)
        elif segment in (SEG_OBJ, SEG_STRING):
            return offset
        elif segment == SEG_GLOBAL:
            raise SimError('SEG_GLOBAL ptrToObject not modeled')
        else:
            self.warnings.append(f'access to segment {segment:04X}')
            return 0

    def assign_pointer(self, ptr, data):
        segment = (ptr >> 16) & 0xFFFF
        offset = ptr & 0xFFFF
        if SEG_STACK_FIRST <= segment <= SEG_STACK_LAST:
            if segment != self.pid:
                raise SimError('assignPointer to foreign stack')
            self.stack[offset:offset + len(data)] = data
        else:
            raise SimError(f'assignPointer to segment {segment:04X}')

    def string_to_ptr(self, sid):
        return (SEG_STRING << 16) | sid

    # ── stack helpers (UCStack: buffer indexed 0..SIZE, SP grows down) ─
    def _push(self, data):
        self.sp -= len(data)
        if self.sp < 0:
            raise SimError('stack overflow')
        self.stack[self.sp:self.sp + len(data)] = data

    def _push2(self, v):
        self._push(struct.pack('<H', v & 0xFFFF))

    def _push4(self, v):
        self._push(struct.pack('<I', v & 0xFFFFFFFF))

    def _pop(self, n):
        if self.sp + n > self.STACK_SIZE:
            raise SimError('stack underflow')
        data = bytes(self.stack[self.sp:self.sp + n])
        self.sp += n
        return data

    def _pop2(self):
        return struct.unpack('<H', self._pop(2))[0]

    def _pop4(self):
        return struct.unpack('<I', self._pop(4))[0]

    def _stk_access2(self, off):
        return struct.unpack_from('<H', self.stack, off)[0]

    # ── process setup (uc_process.cpp load()) ──────────────────────────
    def run_event(self, class_id, offset, this_objid, max_steps=200000,
                  event=None):
        """Start a process the way the engine dispatches an event:
        this = SEG_OBJ pointer to the item, this_size 4 semantics.
        Pass event=N to resolve the entry offset from the class's event
        table instead of a hardcoded offset (1 = use/talk)."""
        self.stack = bytearray(self.STACK_SIZE)
        self.sp = self.STACK_SIZE
        self.temp32 = 0

        # Usecode class N is stored at FLX entry N+2 (the first two
        # entries of EUSECODE.FLX are reserved) — same mapping the
        # engine's UsecodeFlex and the disassembler use.
        code = self.flx.get_object(class_id + 2)
        if not code:
            raise SimError(f'class {class_id} empty in FLX')
        # Class blob = 12-byte header, then the addressed space (32x4
        # event table at 0x00-0x7F, bytecode from 0x80). Event offsets
        # and jumps address blob[12:], same as the disassembler's
        # base_offset = 0x0C.
        self.code = code[12:]
        self.class_id = class_id
        # Event table: 32 x 4-byte offsets at the head of the addressed
        # space. Event 1 = use (double-click / talk), 0 = look, 7 = hatch.
        self.events = {}
        for ev in range(32):
            off = struct.unpack_from('<I', self.code, ev * 4)[0]
            if off:
                self.events[ev] = off

        # load(): push dereferenced this (2 bytes of objid), then the
        # new this-ptr pointing at that copy, then the call frame.
        self._push2(this_objid)
        thissp = self.sp
        self._push4((self.pid << 16) | thissp)
        # call frame: prev class, prev ip, prev bp (0xFFFF marks root)
        self._push2(0xFFFF)
        self._push2(0xFFFF)
        self._push2(0x0000)
        self.bp = self.sp

        if event is not None:
            if event not in self.events:
                raise SimError(
                    f'class {class_id} has no event {event}; '
                    f'table: {sorted(self.events)}')
            offset = self.events[event]
        self.ip = offset
        self._max_sp_used = self.sp
        return self._exec(max_steps)

    def _run_child(self, classid, offset, thisptr, this_size, args,
                   max_steps=500000):
        """Execute a spawned process inline on its own stack (the sim's
        per-process state is saved/restored; heaps and recorders are
        shared). Mirrors UCProcess::load()."""
        self._spawn_depth = getattr(self, '_spawn_depth', 0) + 1
        if self._spawn_depth > 8:
            self._spawn_depth -= 1
            raise SimError('spawn depth > 8 (spawn loop?)')

        # M4: resolve `this` HERE, against the parent's stack, before the
        # swap below replaces self.stack with a zeroed child stack.
        # thisptr is usually a stack pointer into the PARENT's frame — the
        # `push dword [BP+06]` idiom that precedes almost every spawn — and
        # ptr_to_object() dereferences stack pointers through self.stack.
        # Resolving it after the swap read the zeroed child stack and
        # silently produced objid 0, so followed children ran with a null
        # `this` in the sim while the engine gives them a real item. That is
        # sim-green diverging from game-green with no warning, which is the
        # one thing this simulator exists not to do.
        this_objid = None
        if thisptr and this_size > 0:
            if this_size != 2:
                # U8 this is a 2-byte objid deref; larger sizes are
                # dereferencePointer reads we do not model.
                self.warnings.append(
                    f'spawn this_size {this_size} truncated to 2')
            this_objid = self.ptr_to_object(thisptr)
            if this_objid == 0:
                self.warnings.append(
                    f'spawn into class {classid} resolved this to objid 0 '
                    f'(thisptr {thisptr:#010x}) — the child will run with a '
                    f'null this')

        saved = (self.stack, self.sp, self.bp, self.ip, self.code,
                 self.class_id, self.events, self.temp32)
        try:
            self.stack = bytearray(self.STACK_SIZE)
            self.sp = self.STACK_SIZE
            code = self.flx.get_object(classid + 2)
            if not code:
                self.warnings.append(
                    f'followed spawn into empty class {classid}')
                return
            self.code = code[12:]
            self.class_id = classid
            self.events = {}
            for ev in range(32):
                off = struct.unpack_from('<I', self.code, ev * 4)[0]
                if off:
                    self.events[ev] = off
            # UCProcess::load(): deref'd this, args, new this-ptr, frame.
            # `this` was resolved above, against the parent's stack (M4).
            thissp = 0
            if this_objid is not None:
                self._push2(this_objid)
                thissp = self.sp
            if args:
                self._push(args)
            if thissp:
                self._push4((self.pid << 16) | thissp)
            self._push2(0xFFFF)
            self._push2(0xFFFF)
            self._push2(0x0000)
            self.bp = self.sp
            self.ip = offset
            try:
                self._exec(max_steps)
            except SimError as e:
                # follow_spawns is best-effort (see the class docstring). A
                # spawned FREE utility/FX process — wait() and safePlaySFX
                # live in retail FREE (0x581) and LVFREE, and their tick
                # loops use 32-bit opcodes outside the sim's core set — must
                # NOT abort the PARENT scene. The engine schedules these off
                # asynchronously; the synchronous sim can't, so it drops
                # them. They carry no gameplay side effects (verified: the
                # scene's globals, teleports, and created items are identical
                # with or without them), and the parent's saved state is
                # restored in the finally below so it resumes right after the
                # spawn. Deduped, so a 100-iteration animation-wait loop
                # leaves one note rather than a hundred.
                note = (f'follow_spawns: dropped un-runnable spawn into '
                        f'class {classid} ({e})')
                if note not in self.warnings:
                    self.warnings.append(note)
        finally:
            (self.stack, self.sp, self.bp, self.ip, self.code,
             self.class_id, self.events, self.temp32) = saved
            self._spawn_depth -= 1

    # ── the interpreter ────────────────────────────────────────────────
    def _exec(self, max_steps):
        steps = 0
        while steps < max_steps:
            steps += 1
            self._max_sp_used = min(self._max_sp_used, self.sp)
            op = self.code[self.ip]
            ip0 = self.ip
            if self.trace:
                self.trace_log.append((self.class_id, ip0, op))
            self.ip += 1

            if op == 0x00:      # pop byte [BP+xx]
                # uc_machine.cpp:193 — pop 16 bits, assign the low 8 into
                # bp+xx. Emitted by WorldPoint .z writes (2026-07-28).
                off = self._sbyte()
                v = self._pop2()
                self.stack[(self.bp + off) & 0xFFFF] = v & 0xFF
            elif op == 0x01:    # pop2 [BP+xx]
                off = self._sbyte()
                v = self._pop2()
                struct.pack_into('<H', self.stack, (self.bp + off) & 0xFFFF, v)
            elif op == 0x0E:    # create list: pop yy elements of size xx
                esize = self.code[self.ip]
                count = self.code[self.ip + 1]
                self.ip += 2
                # Engine walks from the FIRST-pushed element down, so the
                # list ends up in push order; then frees all elements.
                data = []
                for i in range(count):
                    off = self.sp + esize * (count - 1 - i)
                    data.append(bytes(self.stack[off:off + esize]))
                self.sp += esize * count
                self._push2(self._new_list(esize, data))
            elif op == 0x17:    # append lists (B ++ A, free A, push B)
                a = self._pop2()
                b = self._pop2()
                la, lb = self.lists.get(a), self.lists.get(b)
                if la is not None and lb is not None:
                    lb['data'].extend(la['data'])
                    del self.lists[a]
                    self._push2(b)
                elif la is not None:
                    self._push2(a)
                elif lb is not None:
                    self._push2(b)
                else:
                    self._push2(0)
            elif op == 0x19:    # union slist (dedup by string content)
                self.ip += 1    # elementsize operand (always 02)
                a = self._pop2()
                b = self._pop2()
                la, lb = self.lists.get(a), self.lists.get(b)
                if la is not None and lb is not None:
                    have = {self._str_of_elem(e) for e in lb['data']}
                    for e in la['data']:
                        if self._str_of_elem(e) not in have:
                            lb['data'].append(e)
                            have.add(self._str_of_elem(e))
                        else:
                            self._free_elem_string(e)
                    del self.lists[a]
                self._push2(b)
            elif op == 0x1A:    # subtract slist
                self.ip += 1
                a = self._pop2()
                b = self._pop2()
                la, lb = self.lists.get(a), self.lists.get(b)
                if la is not None and lb is not None:
                    remove = {self._str_of_elem(e) for e in la['data']}
                    kept = []
                    for e in lb['data']:
                        if self._str_of_elem(e) in remove:
                            self._free_elem_string(e)
                        else:
                            kept.append(e)
                    lb['data'] = kept
                    for e in la['data']:
                        self._free_elem_string(e)
                    del self.lists[a]
                self._push2(b)
            elif op == 0x0A:    # push sbyte as 16-bit
                v = self._sbyte()
                self._push2(v & 0xFFFF)
            elif op == 0x0B:    # push word
                self._push2(self._word())
            elif op == 0x0C:    # push dword
                self._push4(self._dword())
            elif op == 0x0D:    # push string
                # Engine (case 0x0D): reads len bytes, then ONE more
                # byte that must be the NUL terminator.
                ln = self._word()
                s = self.code[self.ip:self.ip + ln]
                self.ip += ln
                if self.code[self.ip] != 0:
                    raise SimError('push string missing NUL terminator')
                self.ip += 1
                text = s.decode('latin-1')
                # pre-increment like every other allocator here (a
                # post-increment collided with _dup_string's fresh id)
                self._next_string += 1
                self.strings[self._next_string] = text
                self._push2(self._next_string)
            elif op == 0x0F:    # calli
                arg_bytes = self.code[self.ip]
                self.ip += 1
                intrinsic = self._word()
                self.temp32 = self._call_intrinsic(intrinsic, arg_bytes)
            elif op == 0x11:    # call class:offset
                classid = self._word()
                offset = self._word()
                self.calls.append({'class': classid, 'offset': offset})
                if classid == self.class_id:
                    # Same-class call: execute for real (engine call()):
                    # push prev class/ip/bp, jump, new BP = SP.
                    self._push2(self.class_id)
                    self._push2(self.ip)
                    self._push2(self.bp)
                    self.bp = self.sp
                    self.ip = offset
                else:
                    # Cross-class: stub with a canned return
                    # (call_returns), default 0. The caller's own
                    # add-sp cleanup keeps the stack balanced.
                    self.temp32 = self.call_returns.get(
                        (classid, offset), 0)
            elif op == 0x08:    # pop result: a process's `return <expr>`
                # (uc_machine.cpp case 0x08). The sim shares one result
                # register between a followed child and its waiting parent,
                # which is what the engine's wakeUp(result) hands over.
                self.process_result = self._pop4()
            elif op == 0x12:    # pop temp
                self.temp32 = self._pop2()
            elif op == 0x14:    # add
                a, b = self._pop2(), self._pop2()
                self._push2(b + a)
            elif op == 0x16:    # concat: extend the FIRST-pushed string,
                # free the second, push the first (uc_machine.cpp 0x16)
                a, b = self._pop2(), self._pop2()
                self.strings[b] = (self.strings.get(b, '')
                                   + self.strings.pop(a, ''))
                self._push2(b)
            elif op == 0x1C:    # sub
                a, b = self._pop2(), self._pop2()
                self._push2(b - a)
            elif op == 0x1E:    # mul (`within N cells` scales N by 32)
                a, b = self._pop2(), self._pop2()
                self._push2(b * a)
            elif op == 0x39:    # bit_and
                a, b = self._pop2(), self._pop2()
                self._push2(b & a)
            elif op == 0x24:    # cmp
                a, b = self._pop2(), self._pop2()
                self._push2(1 if a == b else 0)
            elif op == 0x26:    # strcmp: content compare, frees BOTH
                a = self._pop2()
                b = self._pop2()
                self._push2(1 if self.strings.get(b, '')
                            == self.strings.get(a, '') else 0)
                self.strings.pop(a, None)
                self.strings.pop(b, None)
            elif op == 0x28:    # lt (signed)
                a = self._s16(self._pop2())
                b = self._s16(self._pop2())
                self._push2(1 if b < a else 0)
            elif op == 0x2a:    # le (signed) — 16-bit less-or-equal
                # Emitted by every `for i = lo to hi` counter loop (the
                # frame-animation loops in the plant-test wind scene). The
                # baseline classes never used it, so adding it changes no
                # existing behavior (an unused branch cannot fire).
                a = self._s16(self._pop2())
                b = self._s16(self._pop2())
                self._push2(1 if b <= a else 0)
            elif op == 0x2C:    # gt (signed)
                a = self._s16(self._pop2())
                b = self._s16(self._pop2())
                self._push2(1 if b > a else 0)
            elif op == 0x2E:    # ge (signed) — 16-bit greater-or-equal
                # uc_machine.cpp:815. Emitted by the plantScene scene-end
                # self-heal's plateau box test (lv-patched/ATLI.UNK change
                # 3); like 0x2a above, no baseline class used it, so adding
                # it cannot change any existing behavior.
                a = self._s16(self._pop2())
                b = self._s16(self._pop2())
                self._push2(1 if b >= a else 0)
            elif op == 0x30:    # not
                self._push2(0 if self._pop2() else 1)
            elif op == 0x32:    # and
                a, b = self._pop2(), self._pop2()
                self._push2(1 if (a and b) else 0)
            elif op == 0x34:    # or
                a, b = self._pop2(), self._pop2()
                self._push2(1 if (a or b) else 0)
            elif op == 0x36:    # ne
                a, b = self._pop2(), self._pop2()
                self._push2(1 if a != b else 0)
            elif op == 0x3E:    # push sign-extended byte local
                off = self._sbyte()
                v = self.stack[(self.bp + off) & 0xFFFF]
                if v & 0x80:
                    v |= 0xFF00
                self._push2(v)
            elif op == 0x3F:    # push word local
                off = self._sbyte()
                self._push2(self._stk_access2((self.bp + off) & 0xFFFF))
            elif op == 0x40:    # push dword local
                off = self._sbyte()
                v = struct.unpack_from(
                    '<I', self.stack, (self.bp + off) & 0xFFFF)[0]
                self._push4(v)
            elif op == 0x41:    # push string local (duplicated)
                off = self._sbyte()
                sid = self._stk_access2((self.bp + off) & 0xFFFF)
                self._push2(self._dup_string(sid))
            elif op == 0x43:    # push slist local (deep duplicate)
                off = self._sbyte()
                lid = self._stk_access2((self.bp + off) & 0xFFFF)
                src = self.lists.get(lid)
                if src is None:
                    # engine tolerates this (Devon's talk code)
                    self._push2(0)
                else:
                    data = [struct.pack(
                        '<H', self._dup_string(
                            struct.unpack('<H', e)[0]))
                        if src['esize'] == 2 else e
                        for e in src['data']]
                    self._push2(self._new_list(src['esize'], data))
            elif op == 0x45:    # push huge: yy bytes from BP+xx
                                # (uc_machine.cpp 0x45). A WorldPoint
                                # argument, e.g. NPC schedule()'s
                                # canSafeTeleport(point, map).
                off = self._sbyte()
                size = self.code[self.ip]
                self.ip += 1
                at = (self.bp + off) & 0xFFFF
                self._push(bytes(self.stack[at:at + size]))
            elif op == 0x4B:    # push addr of BP+xx
                off = self._sbyte()
                self._push4((self.pid << 16) | ((self.bp + off) & 0xFFFF))
            elif op == 0x6F:    # push addr of SP-xx (uc_machine.cpp 0x6F:
                                # the SP before this push, minus xx).
                                # Retail METHOD enterConvo's
                                # `Avatar.getMap()` at 0x57C 0C4D.
                off = self._sbyte()
                self._push4((self.pid << 16) | ((self.sp - off) & 0xFFFF))
            elif op == 0x4C:    # push indirect
                size = self.code[self.ip]
                self.ip += 1
                ptr = self._pop4()
                if size == 2:
                    self._push2(self.ptr_to_object(ptr))
                else:
                    raise SimError(f'push indirect size {size}')
            elif op == 0x4E:    # push global
                off = self._word()
                bits = self.code[self.ip]
                self.ip += 1
                self._push2(self.get_global(off, bits))
            elif op == 0x4F:    # pop global
                off = self._word()
                bits = self.code[self.ip]
                self.ip += 1
                self.set_global(off, bits, self._pop2())
            elif op == 0x50:    # ret
                prev_bp = self._stk_access2(self.bp)
                prev_ip = self._stk_access2(self.bp + 2)
                prev_class = self._stk_access2(self.bp + 4)
                if prev_class == 0xFFFF:
                    return steps
                if prev_class != self.class_id:
                    raise SimError('cross-class return frame')
                # pop the frame (engine ret(): SP = BP + 6) and resume
                self.sp = self.bp + 6
                self.bp = prev_bp
                self.ip = prev_ip
            elif op == 0x51:    # jne (jump when comparison FALSE)
                delta = self._sword()
                if self._pop2() == 0:
                    self.ip += delta
            elif op == 0x52:    # jmp
                delta = self._sword()
                self.ip += delta
            elif op == 0x53:    # suspend — synchronous model: continue
                pass
            elif op == 0x54:    # implies
                self._word()    # the 01 01
                a = self._pop2()
                b = self._pop2()
                self._push2(a)
            elif op == 0x57:    # spawn
                arg_bytes = self.code[self.ip]
                this_size = self.code[self.ip + 1]
                self.ip += 2
                classid = self._word()
                offset = self._word()
                thisptr = self._pop4()
                args = bytes(self.stack[self.sp:self.sp + arg_bytes])
                self.spawns.append({
                    'class': classid, 'offset': offset,
                    'thisptr': thisptr, 'this_size': this_size,
                    'args': args,
                })
                self._next_pid += 1
                self.temp32 = self._next_pid
                # Retail FREE (0x581) is the wait()/delay utility library:
                # _gen_wait() (u8c_codegen) compiles `wait(n)` to a spawn of
                # 0x581:0x1C19. Those routines are asynchronous delays with
                # no observable effect in a headless conversation, and their
                # retail bytecode uses the full VM opcode set — running them
                # inline (synchronous model) would descend into unmodelled
                # territory for nothing. Record the spawn (pid in temp32) but
                # do NOT follow it: wait() returns immediately, the caller
                # continues to the next statement, exactly the resume the
                # engine reaches after the delay elapses.
                if self.follow_spawns and classid != 0x581:
                    # Engine-faithful enough for conversations: the
                    # engine executes a freshly spawned process
                    # immediately (addProcessExec), and dialogue use()
                    # spawns its talk process then waits on it. Run the
                    # child inline on its own stack; world/globals/
                    # strings/lists/recorders are shared.
                    self._run_child(classid, offset, thisptr, this_size,
                                    args)
            elif op == 0x59:    # push pid
                self._push2(self.pid)
            elif op == 0x5A:    # init
                n = self.code[self.ip]
                self.ip += 1
                if n & 1:
                    n += 1
                if n:
                    self._push(b'\x00' * n)
            elif op == 0x5D:    # push byte retval
                self._push2(self.temp32 & 0xFF)
            elif op == 0x5E:    # push retval
                self._push2(self.temp32 & 0xFFFF)
            elif op == 0x60:    # int to long (sign-extend 16->32); e.g.
                                # wait(1000) widens its literal to a Long
                v = self._pop2()
                if v & 0x8000:
                    v |= 0xFFFF0000
                self._push4(v)
            elif op == 0x61:    # long to int
                self._push2(self._pop4() & 0xFFFF)
            elif op == 0x62:    # free string [BP+xx]
                off = self._sbyte()
                sid = self._stk_access2((self.bp + off) & 0xFFFF)
                self.strings.pop(sid, None)
            elif op == 0x63:    # free slist [BP+xx]
                off = self._sbyte()
                self._free_slist(self._stk_access2((self.bp + off) & 0xFFFF))
            elif op == 0x64:    # free list [BP+xx] (word/Item list: its
                # elements own nothing, uc_machine.cpp case 0x64)
                off = self._sbyte()
                self.lists.pop(self._stk_access2((self.bp + off) & 0xFFFF),
                               None)
            elif op == 0x65:    # free string [SP+xx]
                off = self._sbyte()
                sid = self._stk_access2(self.sp + off)
                self.strings.pop(sid, None)
            elif op == 0x67:    # free slist [SP+xx]
                off = self._sbyte()
                self._free_slist(self._stk_access2(self.sp + off))
            elif op == 0x6D:    # push process result (32-bit)
                self._push4(self.process_result)
            elif op == 0x6B:    # str to ptr
                sid = self._pop2()
                self._push4(self.string_to_ptr(sid))
            elif op == 0x6E:    # add sp
                # _sbyte() is already sign-extended. Downward stack:
                # "add sp -2" FREES 2 bytes (sp moves up), positive
                # allocates. sp -= v covers both.
                v = self._sbyte()
                self.sp -= v
            elif op == 0x70:    # loop
                self._op_loop()
                # falls through to loopnext in the engine:
                self._op_loopnext()
            elif op == 0x73:    # loopnext
                self._op_loopnext()
            elif op == 0x74:    # loopscr byte
                b = self.code[self.ip]
                self.ip += 1
                self._push(bytes([b]))
            elif op == 0x77:    # set info
                self._pop2()    # item num (via indirect earlier)
                self._pop2()    # type
            elif op == 0x78:    # process exclude
                pass
            elif op == 0x79:    # end
                return steps
            else:
                raise SimError(
                    f'unhandled opcode {op:#04x} at {ip0:04X}')
        raise SimError('step limit exceeded (infinite loop?)')

    # add sp fix: engine semantics are simply sp -= signed_operand *
    # -1?  UCStack::addSP(int) does _SP += val with negative freeing?
    # In uc_machine 0x6E: p->_stack.addSP(si8a) and "add sp -2" frees 2
    # bytes -> SP moves UP by 2 in a downward stack: sp += -si8a.

    def _op_loop(self):
        bpoff = self._sbyte()
        scriptsize = self.code[self.ip]
        searchtype = self.code[self.ip + 1]
        self.ip += 2

        ui16a = self._pop2()
        ui16b = self._pop2()
        script = self._pop(scriptsize)   # forward copy off the top

        if searchtype in (2, 3):
            stacksize = 0x34
            center = self.world.get(ui16a)
            if center is None:
                self.warnings.append(
                    f'area search: invalid center item {ui16a}')
                found = []
            else:
                found = self.world.area_search(script, center, ui16b,
                                               searchtype == 3)
        elif searchtype in (4, 5):
            stacksize = 0x28 + (2 if searchtype == 5 else 0)
            if ui16a != 0xFFFF:
                self.warnings.append('container search missing FFFF marker')
            cont = self.world.get(ui16b)
            if cont is None:
                self.warnings.append(
                    f'container search: invalid container {ui16b}')
                found = []
            else:
                found = self.world.container_search(script, cont,
                                                    searchtype == 5)
        else:
            raise SimError(f'search type {searchtype} not modeled')

        self._push(b'\x00' * (stacksize - scriptsize - 8))
        self._push(script)
        self._push2(scriptsize)
        self._push2(bpoff & 0xFFFF)
        self._push2(0)
        self._lists = getattr(self, '_lists', {})
        self._next_list = getattr(self, '_next_list', 0) + 1
        self._lists[self._next_list] = found
        self._push2(self._next_list)

    def _op_loopnext(self):
        listid = self._stk_access2(self.sp)
        index = self._stk_access2(self.sp + 2)
        bpoff = self._stk_access2(self.sp + 4)
        if bpoff & 0x8000:
            bpoff -= 0x10000
        itemlist = self._lists.get(listid)
        if itemlist is None:
            raise SimError('invalid item list in loopnext')
        valid = False
        while index < len(itemlist):
            objid = itemlist[index]
            struct.pack_into('<H', self.stack,
                             (self.bp + bpoff) & 0xFFFF, objid)
            if self.world.get(objid) is not None:
                valid = True
                break
            index += 1
        if not valid:
            self._push2(0)
            self._lists.pop(listid, None)
        else:
            self._push2(1)
            struct.pack_into('<H', self.stack, self.sp + 2 + 2, index + 1)

    # ── list/string helpers ─────────────────────────────────────────────
    def _new_list(self, esize, data):
        self._next_list_id += 1
        self.lists[self._next_list_id] = {'esize': esize, 'data': data}
        return self._next_list_id

    def _dup_string(self, sid):
        text = self.strings.get(sid, '')
        self._next_string += 1
        self.strings[self._next_string] = text
        return self._next_string

    def _free_slist(self, lid):
        lst = self.lists.pop(lid, None)
        if lst and lst['esize'] == 2:
            for e in lst['data']:
                self._free_elem_string(e)

    def _str_of_elem(self, e):
        return self.strings.get(struct.unpack('<H', e)[0], '')

    def _free_elem_string(self, e):
        self.strings.pop(struct.unpack('<H', e)[0], None)

    @staticmethod
    def _s16(v):
        return v - 0x10000 if v & 0x8000 else v

    # ── operand readers ─────────────────────────────────────────────────
    def _sbyte(self):
        v = self.code[self.ip]
        self.ip += 1
        return v - 0x100 if v & 0x80 else v

    def _word(self):
        v = struct.unpack_from('<H', self.code, self.ip)[0]
        self.ip += 2
        return v

    def _sword(self):
        v = struct.unpack_from('<h', self.code, self.ip)[0]
        self.ip += 2
        return v

    def _dword(self):
        v = struct.unpack_from('<I', self.code, self.ip)[0]
        self.ip += 4
        return v

    # ── intrinsics ──────────────────────────────────────────────────────
    class _Args:
        """Reads the args buffer forward, exactly like the ARG_ macros."""

        def __init__(self, sim, arg_bytes):
            self.buf = bytes(sim.stack[sim.sp:sim.sp + arg_bytes])
            self.pos = 0
            self.sim = sim

        def uint16(self):
            v = struct.unpack_from('<H', self.buf, self.pos)[0]
            self.pos += 2
            return v

        def uint8(self):
            v = self.buf[self.pos]
            self.pos += 1
            return v

        def uc_ptr(self):
            v = struct.unpack_from('<I', self.buf, self.pos)[0]
            self.pos += 4
            return v

        def item_from_ptr(self):
            objid = self.sim.ptr_to_object(self.uc_ptr())
            return self.sim.world.get(objid)

        def string(self):
            ptr = self.uc_ptr()
            if (ptr >> 16) == SEG_STRING:
                return self.sim.strings.get(ptr & 0xFFFF, '')
            return ''

    def _call_intrinsic(self, num, arg_bytes):
        name = self._intrinsics.get(num, f'intrinsic_{num:04X}')
        a = self._Args(self, arg_bytes)
        w = self.world
        result = 0

        base = name.split('(')[0]
        if base in ('Camera::setCenterOn', 'Camera::move_to',
                    'Camera::scrollTo', 'Camera::getX', 'Camera::getY',
                    'Camera::getZ'):
            # Ahead of the item getters below, which would take
            # Camera::getX for Item::getX. The Camera class is static:
            # no item pointer in the args.
            result = self._camera_intrinsic(base, a)
        elif base == 'canExistAt':
            # CurrentMap::I_canExistAt (current_map.cpp:1257): ARG_UINT16
            # shape, x, y, ARG_UINT8 z, then three words it ignores.
            shape = a.uint16()
            x = a.uint16()
            y = a.uint16()
            z = a.uint8()
            result = 1 if w.can_exist_at(shape, x, y, z) else 0
        elif base.endswith('getQ'):
            it = a.item_from_ptr()
            result = it.quality if it else 0
        elif base.endswith('getQuality'):
            it = a.item_from_ptr()
            # ENGINE-FAITHFUL: only SF_QUALITY families report quality.
            if it and w.shapeflags.family(it.shape) == SF_QUALITY:
                result = it.quality
        elif base.endswith('getQLo'):
            it = a.item_from_ptr()
            result = (it.quality & 0xFF) if it else 0
        elif base.endswith('getQHi'):
            it = a.item_from_ptr()
            result = ((it.quality >> 8) & 0xFF) if it else 0
        elif base.endswith('Item::setQ'):
            # ENGINE-FAITHFUL arg order, confirmed against the compiled
            # call site (ENDGAME.UNK's topUpReagents): the item pointer is
            # the FIRST 4 bytes of arg_bytes (pushed last, at the top of
            # the UC stack, per the standard this-pushed-last method-call
            # convention) and the value is the remaining 2 bytes. Reading
            # value-then-pointer (the order setFrame's and setType's
            # handlers below used until 2026-10-11) decodes a bogus
            # segment from the wrong half of the buffer and drops the
            # write with no error, caught by a
            # dedicated probe script when setQuantity below looked like a
            # no-op. Writes the same backing field getQ reads,
            # unconditional of family: item.cpp's I_setQ has no family
            # gate at all, which is the whole reason ENDGAME.UNK's
            # topUpReagents uses it to tag an SF_CONTAINER bag (setQuality
            # below would also have worked for that family, but getQuality
            # would then refuse to read it back).
            it = a.item_from_ptr()
            value = a.uint16()
            if it:
                it.quality = value
        elif base.endswith('setQuality'):
            # ENGINE-FAITHFUL (item.cpp I_setQuality): writes unless the
            # family is SF_GENERIC (every other family, including
            # SF_CONTAINER, is allowed).
            it = a.item_from_ptr()
            value = a.uint16()
            if it and w.shapeflags.family(it.shape) != SF_GENERIC:
                it.quality = value
        elif base.endswith('getQuantity'):
            # ENGINE-FAITHFUL (item.cpp I_getQuantity): quantity and
            # quality are the SAME field (SimItem.quantity is a property
            # over .quality); only SF_QUANTITY/SF_REAGENT report it.
            it = a.item_from_ptr()
            if it and w.shapeflags.family(it.shape) in (SF_QUANTITY, SF_REAGENT):
                result = it.quantity
        elif base.endswith('setQuantity'):
            # ENGINE-FAITHFUL (item.cpp I_setQuantity): same family gate
            # as getQuantity, and the same confirmed arg order as setQ
            # above (item pointer first).
            it = a.item_from_ptr()
            value = a.uint16()
            if it and w.shapeflags.family(it.shape) in (SF_QUANTITY, SF_REAGENT):
                it.quantity = value
        elif base.endswith('getFrame'):
            it = a.item_from_ptr()
            result = it.frame if it else 0
        elif base.endswith('setFrame'):
            # Item::I_setFrame (item.cpp:2828): ARG_ITEM_FROM_PTR, then
            # ARG_UINT16 frame, the order setQ above found. Reading the
            # frame first decoded the pointer's low word as a frame and a
            # bogus pointer from the rest, so no setFrame ever landed (a
            # makeAvatarBig ramp `while getFrame() > 60` never ended).
            it = a.item_from_ptr()
            frame = a.uint16()
            if it:
                it.frame = frame
        elif base.endswith('setType'):
            # Item::I_setShape (item.cpp:2807): ARG_ITEM_FROM_PTR, then
            # ARG_UINT16 shape, as setFrame. This is the whole Tiny Tar
            # mechanic: the Avatar's shape (and therefore its footpad, per
            # getFootpadWorld) is swapped to the shrunken form and back.
            it = a.item_from_ptr()
            shape = a.uint16()
            if it:
                it.shape = shape
        elif base.endswith('getType'):
            it = a.item_from_ptr()
            result = it.shape if it else 0
        elif base.endswith('getX'):
            it = a.item_from_ptr()
            result = it.x if it else 0
        elif base.endswith('getY'):
            it = a.item_from_ptr()
            result = it.y if it else 0
        elif base.endswith('getZ'):
            it = a.item_from_ptr()
            result = it.z if it else 0
        elif base.endswith('Npc::getMap'):
            # Actor::I_getMap (actor.cpp:2114) — returns the actor's map
            # number. Fixtures set it explicitly (SimItem(mapnum=...));
            # the default 0 matches an actor that has never been placed.
            it = a.item_from_ptr()
            result = it.mapnum if it else 0
        elif base.endswith('Item::destroy'):
            it = a.item_from_ptr()
            if it:
                it.destroy_recorded = True
                it.destroyed = True
                if it.parent is not None:
                    parent = w.items.get(it.parent)
                    if parent and it.objid in parent.contents:
                        parent.contents.remove(it.objid)
        elif base.endswith('Item::create'):
            ptr = a.uc_ptr()
            shape = a.uint16()
            frame = a.uint16()
            it = w.add(shape, frame=frame)
            it.ethereal = True
            w.ethereal_stack.append(it.objid)
            self.created.append(it.objid)
            # ENGINE-FAITHFUL: objid written back through the pointer.
            self.assign_pointer(ptr, struct.pack('<H', it.objid))
            result = 1
        elif base.endswith('Item::getPoint'):
            # ENGINE-FAITHFUL (item.cpp I_getPoint): write the item's
            # absolute position into a caller-supplied WorldPoint through a
            # stack pointer. WorldPoint._buf is 5 bytes, x/y little-endian
            # uint16 then z (world_point.h). Scenes that stage a set-piece
            # capture positions this way and compute everything else from
            # them -- SHADES.UNK's reforge is one -- so without this the
            # sim silently computed from zeros.
            # ENGINE CONVENTION: ARG_ITEM_FROM_PTR (4-byte pointer,
            # dereferenced to an objid) then ARG_UC_PTR (4 bytes) = 8 arg
            # bytes. An earlier version of this stub read 4+2 — reverse-
            # engineered from our own compiler's output, which was WRONG
            # (it pushed the WorldPoint as a 2-byte value), so the sim
            # green-lit bytecode the engine rejected. The stub must encode
            # what item.cpp does, never what our emitter happens to emit:
            # that mismatch is exactly what it exists to catch.
            it = a.item_from_ptr()
            ptr = a.uc_ptr()
            if it:
                self.assign_pointer(
                    ptr, struct.pack('<HHB', it.x & 0xFFFF, it.y & 0xFFFF,
                                     it.z & 0xFF))
                result = 1
        elif base.endswith('Item::push'):
            # ENGINE-FAITHFUL (item.cpp I_push): moveToEtherealVoid — the
            # item leaves its container/the world and goes on the ethereal
            # stack, which is where every pop variant takes its item from.
            # Without this, a `push(); pop(x,y,z)` pair (how SHADES.UNK
            # lays the shield halves on the ground) moved nothing and left
            # the halves at x=0, so anything the scene computed FROM their
            # coordinates was garbage in the sim but fine in the engine.
            it = a.item_from_ptr()
            if it:
                if it.parent is not None:
                    parent = w.get(it.parent)
                    if parent and it.objid in parent.contents:
                        parent.contents.remove(it.objid)
                    it.parent = None
                it.ethereal = True
                w.ethereal_stack.append(it.objid)
        elif base.endswith('Item::pop') or base.endswith('Item::popToEnd'):
            # ENGINE-FAITHFUL (item.cpp I_pop/I_popToCoords/
            # I_popToContainer/I_popToEnd): every pop variant starts with
            # ARG_NULL32 — the leading 4-byte itemptr is UNUSED; the
            # popped item is always the TOP of the ethereal void. The
            # U8 slots overload one name (0x36 coords / 0x37 container /
            # 0x38 in-place / 0x39 popToEnd), so dispatch on the slot's
            # declared parameter count, mirroring the ARG_ macros.
            a.uc_ptr()  # ARG_NULL32
            argc = self._intrinsic_argc.get(num, 0)
            if argc == 3:
                # I_popToCoords: ARG_UINT16(x/y), ARG_UINT8(z); move()
                x = a.uint16()
                y = a.uint16()
                z = a.uint8()
                if w.ethereal_stack:
                    it = w.items[w.ethereal_stack.pop()]
                    it.ethereal = False
                    it.x, it.y, it.z = x, y, z
                    result = it.objid
            elif argc == 1:
                # I_popToContainer / I_popToEnd: ARG_ITEM_FROM_ID(citem);
                # moveToContainer(citem)
                cid = a.uint16()
                citem = w.get(cid)
                if citem is None:
                    self.warnings.append(
                        f'{base}: invalid container {cid}')
                elif w.ethereal_stack:
                    it = w.items[w.ethereal_stack.pop()]
                    it.ethereal = False
                    w.put_in_container(it, citem)
                    result = it.objid
            else:
                # I_pop: returnFromEtherealVoid() — back to where it was
                if w.ethereal_stack:
                    it = w.items[w.ethereal_stack.pop()]
                    it.ethereal = False
                    result = it.objid
        elif base.endswith('bark'):
            it = a.item_from_ptr()
            text = a.string()
            self.barks.append((it.objid if it else 0, text))
            self._next_pid += 1
            result = self._next_pid
        elif base.endswith('ask'):
            # "strptr process Item::ask(uword slist)": show the answer
            # slist, "pick" the next scripted answer, deliver it via the
            # process result (opcode 0x6D pushes it after the implies/
            # suspend dance). retval = the ask process pid. Args read
            # top-down: itemptr first, then the slist id.
            a.uc_ptr()
            slist_id = a.uint16()
            options = []
            lst = self.lists.get(slist_id)
            if lst and lst['esize'] == 2:
                options = [self._str_of_elem(e) for e in lst['data']]
            if not self.answer_script:
                raise SimError(
                    f'ask() with empty answer script; options: {options}')
            answer = self.answer_script.pop(0)
            self.asks.append((options, answer))
            if answer not in options:
                raise SimError(
                    f'scripted answer {answer!r} not among ask options '
                    f'{options}')
            self._next_string += 1
            self.strings[self._next_string] = answer
            self.process_result = (SEG_STRING << 16) | self._next_string
            self._next_pid += 1
            result = self._next_pid
        elif 'Convo' in base or 'convo' in base:
            pass  # enterConvo/exitConvo: process/stasis management only
        elif base == 'urandom':
            # UCMachine::I_urandom: ARG_UINT16(num); 0 for num <= 1, else
            # getRandomNumber(num - 1), i.e. 0..num-1 inclusive. A scripted
            # value outside that range is a test bug the engine could never
            # produce, so it is refused rather than returned.
            n = a.uint16()
            v = self.urandom_script.pop(0) if self.urandom_script else None
            if v is None:
                v = 0
            if not 0 <= v < max(n, 1):
                raise SimError(f'scripted urandom value {v} outside the '
                               f'engine range of urandom({n})')
            self.urandom_rolls.append((n, v))
            result = v
        elif base.endswith('getNpcSlot'):
            it = a.item_from_ptr()
            result = it.npcnum if it else 0
        elif base.endswith('getEquip'):
            # Actor::I_getEquip(actor_ptr, uint16 slot) -> objid.
            # Keyed by the raw slot arg (see SimItem.equipment).
            it = a.item_from_ptr()
            slot = a.uint16()
            result = it.equipment.get(slot, 0) if it else 0
        elif base.endswith('getEggXRange'):
            # Egg::I_getEggXRange(egg_ptr): x range = npcnum high nibble
            # (DD-007a; ScummVM stores the hatch box in the npcNum byte).
            it = a.item_from_ptr()
            result = ((it.npcnum >> 4) & 0xF) if it else 0
        elif base.endswith('setEggXRange'):
            # Egg::I_setEggXRange(egg_ptr, uint16 range): write the high
            # nibble, keep the y-range nibble. SHADES.UNK uses range=1 as
            # its once-only ceremony latch.
            it = a.item_from_ptr()
            rng = a.uint16()
            if it:
                it.npcnum = ((rng & 0xF) << 4) | (it.npcnum & 0x0F)
        elif base.endswith('resetRef') or base.endswith('cSetActivity') \
                or base.endswith('setActivity') or base.endswith('isDead'):
            pass  # process/schedule management; isDead=0 means alive
        elif 'SFX' in base or 'Sound' in base:
            pass  # recorded via intrinsic_log below
        elif 'InStasis' in base:
            pass
        elif base.endswith('teleportToEgg'):
            # MainActor::I_teleportToEgg (main_actor.cpp:807), U8's 6-byte
            # form: ARG_UINT16 map, ARG_UINT16 teleport_id, then a word it
            # ignores (retail's stasis byte). The first source argument is
            # pushed last, so the map is at offset 0 (retail CARTHAXH 0x487
            # pushes 1, the id, then the map). It starts a
            # TeleportToEggProcess for the Avatar; record where it sends him.
            tmap = a.uint16()
            tid = a.uint16()
            self.egg_teleports.append({'map': tmap, 'egg': tid})
            self._next_pid += 1
            result = self._next_pid
        elif base.endswith('teleport'):
            # Actor::I_teleport(actor_ptr, x:u16, y:u16, z:u16, map:u16)
            # (scummvm actor.cpp:2121 — ARG_ACTOR_FROM_PTR first, then four
            # ARG_UINT16). The compiler pushes `this` last so it sits at the
            # top of the args buffer (offset 0), then x,y,z,map as words —
            # the same [itemptr, args...] layout getX/setFrame read. Record
            # the destination (scene tests assert where the Avatar lands)
            # and move the actor, mirroring the Item::pop stub's move().
            it = a.item_from_ptr()
            tx = a.uint16()
            ty = a.uint16()
            tz = a.uint16()
            tmap = a.uint16()
            self.teleports.append({'obj': it.objid if it else 0,
                                   'x': tx, 'y': ty, 'z': tz, 'map': tmap})
            if it:
                it.x, it.y, it.z = tx, ty, tz
        else:
            self.warnings.append(f'unstubbed intrinsic {name}')

        self.intrinsic_log.append((base, bytes(a.buf), result))
        return result

    def camera_location(self):
        """CameraProcess::GetCameraLocation: a following camera's _e is
        the item's location with z + 20; a parked one is its point."""
        if self.camera_follow is not None:
            it = self.world.get(self.camera_follow)
            if it is not None:
                return (it.x, it.y, it.z + 20)
        return self.camera_pos if self.camera_pos is not None else (0, 0, 0)

    def _camera_intrinsic(self, base, a):
        """camera_process.cpp's U8 intrinsics. Each re-aim is logged in
        camera_moves so a test can measure what the player sees jump."""
        if base == 'Camera::getX':
            return self.camera_location()[0]
        if base == 'Camera::getY':
            return self.camera_location()[1]
        if base == 'Camera::getZ':
            return self.camera_location()[2]
        before = self.camera_location()
        if base == 'Camera::setCenterOn':
            # I_setCenterOn: ARG_OBJID; new CameraProcess(itemNum). Item 0
            # parks the camera where it is (_e = _s = GetCameraLocation).
            objid = a.uint16()
            if objid and self.world.get(objid) is not None:
                self.camera_follow = objid
            else:
                if objid:
                    self.warnings.append(
                        f'Camera::setCenterOn({objid}): no such item')
                self.camera_follow = None
                self.camera_pos = before
        else:
            # I_moveTo / I_scrollTo: ARG_UINT16 x, y, ARG_UINT8 z, then a
            # word neither reads. A scroll is the same end point reached
            # over 25 frames.
            x = a.uint16()
            y = a.uint16()
            z = a.uint8()
            self.camera_follow = None
            self.camera_pos = (x, y, z)
        self.camera_moves.append((base, before, self.camera_location()))
        return 0
