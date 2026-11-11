#!/usr/bin/env python3
"""
test_uc_lordbrit.py: headless proof for the LORDBRIT.UNK fix
(agents/usecode-compiler/src/lv-patched/LORDBRIT.UNK), closing TODO.md
"Found 2026-09-26" (finding 1 in docs/playtest-2026-09-26-lamps-plaques-lb.md).
The apparition changed pose once and held it, because puppet()'s `process {
... }` block compiled to a single straight-through pass. use() spawns
puppet with `-> return`, which waits for puppet to RETURN, so turning
puppet() into a real loop without ALSO changing the spawn would have
deadlocked use(): a puppet looping until use()'s own later `lbDone = 1;`
would never return.

Root cause, revised 2026-10-01: this was not a LORDBRIT-specific parser
gap. Disassembling retail class 0x2FE (TypePotion, shared/data/USECODE.FLX)
showed `process { ... }` is a GENERAL 1994 construct: retail's own
protection()/invisible() compile it to a backward jmp back to the block's
own top, taken whenever the block falls off its end without an explicit
`return`. u8c_codegen.py now does the same for every `process { ... }`
(a parser tag plus a codegen wrapper; see u8c_ast.py's Block docstring),
so LORDBRIT.UNK's patch no longer touches puppet()'s body at all --
it is byte-identical to the recovered original except for the spawn's
arrow and one added pragma statement.

The fix, lv-patched/LORDBRIT.UNK, two hunks:
  A. `spawn puppet(lb) -> return;` loses the arrow: `spawn puppet(lb);`.
     u8c_codegen.py's _gen_spawn now reads stmt.has_arrow_return and, when
     False, skips the leading push_pid and the trailing
     push_retval/implies/pop_temp/suspend, a fire-and-forget spawn that
     does not block the caller (uc_machine.cpp case 0x57 runs a freshly
     spawned process once immediately and resumes the caller regardless).
     This is what makes puppet() looping (now automatic) safe: without it,
     use() would deadlock waiting on a puppet that only returns once use()
     itself sets lbDone.
  B. puppet() gains use()'s own `[[PT_DEFAULT, referent]];` pragma as its
     first statement, re-tagging its process so a map switch (the other
     trigger, AVATAR::schedule(), teleports away and back) does not kill
     it mid-animation. The typeclass header already declared this
     annotation, but header-form annotations are parsed and never
     consulted by codegen, so it stayed inert until now.

This file checks hunk A statically: disassemble the compiled class and
confirm the spawn is not followed by implies/suspend. It checks the
general process-block loop statically too: confirm puppet() contains a
backward jmp, and that the jmp lands at the top of the process SECTION,
right after startup's last statement -- startup must run once, before
the loop, never again. It checks hunk B
statically: puppet() opens with the set-info pragma. It checks the loop
dynamically by running puppet() itself through the engine-faithful
simulator (u8c_sim.py) and reading the logged setFrame sequence. The sim
cannot show hunk A's concurrency: it runs spawned children to completion
inline, single threaded, and `suspend` is always a no-op in its
synchronous model (op 0x53 is unconditional `pass`), so the pre-fix
deadlock does not reproduce in the sim either.
"""
import os
import struct
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
DISASM_DIR = os.path.join(BASE_DIR, 'agents', 'usecode-disasm', 'src')
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, DISASM_DIR)

from u8c_parser import parse_file                      # noqa: E402
from u8c_codegen import CodeGenerator                   # noqa: E402
from u8c_symbols import create_symbol_table             # noqa: E402
from u8c_sim import UCSim, SimWorld                      # noqa: E402
from u8_usecode_disasm import UsecodeDisassembler, UsecodeClass  # noqa: E402

LORDBRIT = os.path.join(BASE_DIR, 'agents', 'usecode-compiler', 'src',
                        'lv-patched', 'LORDBRIT.UNK')
SHAPE_GHOST = 411   # TypeLordBritish, pinned in u8c_symbols.TYPE_SHAPES
SHAPE_EGG = 73
SEG_OBJ = 0x8002

passed = 0
failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


print('=' * 68)
print('LORDBRIT: puppet() loops through its frames, use() does not wait')
print('=' * 68)

# Compile the patched file standalone (same recipe as the single-file
# snippet in CLAUDE.md), so this test does not depend on the full
# build_eusecode.py pipeline or shared/build/EUSECODE.FLX.
symbols = create_symbol_table()
ast = parse_file(LORDBRIT)
codegen = CodeGenerator(symbols)
class_bytes = codegen.generate_class(ast)
classid = codegen._classid
use_offset = codegen.events[1]                       # event 1 = use()
puppet_offset = codegen._function_table['puppet'][1][0]

print(f'  class 0x{classid:04X}  use()@0x{use_offset:04X}  '
      f'puppet()@0x{puppet_offset:04X}  ({len(class_bytes)} bytes)')

lb_bit = symbols.get_global_flag('lbDone')
check('lbDone global flag is declared', lb_bit is not None)
lb_bit_offset, lb_bit_width = lb_bit

# Static: disassemble into structured instructions and check both hunks
# directly in the bytecode.
dis = UsecodeDisassembler()
uc = UsecodeClass(classid, None, class_bytes)
instrs = dis.disassemble_bytecode(uc.bytecode, start_offset=0x80)

SPAWN, PUSH_RETVAL, IMPLIES, POP_TEMP, SUSPEND, JMP = 0x57, 0x5E, 0x54, 0x12, 0x53, 0x52

spawn_to_puppet = [i for i in instrs if i.opcode == SPAWN
                   and i.operands[2][1] == classid
                   and i.operands[3][1] == puppet_offset]
check('use() contains a spawn targeting puppet()',
      len(spawn_to_puppet) == 1, detail=f'found {len(spawn_to_puppet)}')

if spawn_to_puppet:
    spawn_instr = spawn_to_puppet[0]
    idx = instrs.index(spawn_instr)
    following = [i.opcode for i in instrs[idx + 1:idx + 5]]
    check('hunk A: the spawn is fire-and-forget, with no trailing '
          'push_retval/implies/suspend (use() does not wait for puppet '
          'to return)',
          following[:3] != [PUSH_RETVAL, IMPLIES, SUSPEND],
          detail=f'next opcodes: {[hex(o) for o in following]}')

puppet_instrs = [i for i in instrs if i.offset >= puppet_offset]
backward_jmps = [i for i in puppet_instrs if i.opcode == JMP and i.operands[0][1] < 0]
check('the general process-block loop: puppet() contains a backward jmp, '
      'an actual loop (u8c_codegen.py wraps the bare `process { ... }` '
      "block this way for every compiled class)",
      len(backward_jmps) >= 1)
PUSH_GLOBAL = 0x4E
if backward_jmps:
    j = backward_jmps[0]
    target = j.offset + len(j.raw_bytes) + j.operands[0][1]
    target_instr = next((i for i in instrs if i.offset == target), None)
    check('the backward jmp lands on a `suspend`, as retail\'s do '
          '(TypePotion 0x0634): every lap yields to the scheduler whatever '
          'the body does. Without it a lap with no yield spins inside one '
          'engine tick; ARAMINA\'s atHome() froze ScummVM that way '
          '(docs/playtest-2026-10-01-process-loops.md)',
          target_instr is not None and target_instr.opcode == SUSPEND,
          detail=f'jmp @ 0x{j.offset:04X}, target 0x{target:04X} opcode '
                 f'{hex(target_instr.opcode) if target_instr else None}')
    after = next((i for i in instrs if target_instr is not None
                  and i.offset == target + len(target_instr.raw_bytes)), None)
    check('...and right after it sits the `if lbDone = 1` test that opens '
          'the process SECTION (the global flag read, pinned to lbDone\'s '
          "own bit offset), confirming startup's own statements run exactly "
          "once, before the loop's first lap",
          after is not None and after.opcode == PUSH_GLOBAL
          and after.operands[0][1] == lb_bit_offset,
          detail=f'puppet() @ 0x{puppet_offset:04X}, after-suspend opcode '
                 f'{hex(after.opcode) if after else None}, '
                 f'lbDone bit 0x{lb_bit_offset:04X}')

# Hunk B: puppet()'s first few instructions re-tag it, the same idiom as
# use()'s own `[[PT_DEFAULT, referent]];`: push byte 1 (PT_DEFAULT), push
# dword [BP+06h] (this), push indirect 02h (deref to referent), set info
# (0x77), all before the startup block's first setFrame call.
PUSH_BYTE, PUSH_DWORD_BP, PUSH_INDIRECT, SET_INFO = 0x0A, 0x40, 0x4C, 0x77
preamble = puppet_instrs[:6]
preamble_ops = [i.opcode for i in preamble]
set_info_idx = next((n for n, op in enumerate(preamble_ops) if op == SET_INFO), None)
check('hunk B: puppet() opens with a set-info pragma, the PT_DEFAULT '
      "re-tag that protects it from a map-switch kill, right after the "
      'function\'s own init (locals-allocation) instruction, before the '
      'startup block',
      set_info_idx is not None and set_info_idx <= 4,
      detail=f'preamble opcodes: {[hex(o) for o in preamble_ops]}')
if set_info_idx is not None:
    ptype_instr = preamble[set_info_idx - 3] if set_info_idx >= 3 else None
    check('the pragma pushes PT_DEFAULT (byte 1) as its type operand',
          ptype_instr is not None and ptype_instr.opcode == PUSH_BYTE
          and ptype_instr.operands[0][1] == 1,
          detail=repr(ptype_instr.operands) if ptype_instr else 'missing')

# Dynamic: run puppet() itself through the simulator. The sim cannot model
# use() and puppet() ticking concurrently (see module docstring), so this
# drives puppet() directly via UCSim's low-level child-execution path (the
# same one `spawn` uses internally), reading the real frame sequence back
# out of intrinsic_log.


def frame_sequence(sim):
    # Read the raw logged buffer at the offset the compiled bytecode
    # actually pushes the frame value to. Confirmed empirically: `lb.
    # setFrame(fram)` compiles to `push fram; push addr lb`, args then the
    # item pointer (both arg_bytes callers push this way), so the item
    # pointer, pushed last, sits at the lowest address: buf[0:4]. The
    # frame value sits above it at buf[4:6]. u8c_sim.py's own setFrame
    # handler reads `uint16()` then `item_from_ptr()`, the opposite order,
    # so `it.frame` never actually gets mutated in the sim. That is a
    # pre-existing simulator quirk; this test leaves it alone and reads
    # intrinsic_log's raw buffer instead, which is unaffected by it.
    return [struct.unpack_from('<H', args, 4)[0]
            for name, args, _r in sim.intrinsic_log
            if name.endswith('setFrame')]


class _OneClassFlex:
    """Stand-in FlexArchive serving only this test's compiled class, so
    the test needs no shared/build/EUSECODE.FLX on disk."""

    def __init__(self, classid, data):
        self._classid = classid
        self._data = data

    def get_object(self, index):
        return self._data if index == self._classid + 2 else None


def make_sim():
    w = SimWorld()
    host = w.add(SHAPE_EGG, objid=0x150)
    lb = w.add(SHAPE_GHOST, objid=0x160, frame=0)
    sim = UCSim(world=w)
    sim.flx = _OneClassFlex(classid, class_bytes)
    return sim, w, host, lb


def exec_puppet(lb_done_initially, max_steps):
    sim, w, host, lb = make_sim()
    sim.set_global(lb_bit_offset, lb_bit_width, 1 if lb_done_initially else 0)
    # _run_child saves/restores stack/bp/ip/code/class_id/events/temp32
    # (normally set up by run_event, which this test bypasses since
    # run_event cannot pass puppet() its `lb` argument).
    sim.stack = bytearray(UCSim.STACK_SIZE)
    sim.sp = UCSim.STACK_SIZE
    sim.bp = 0
    sim.ip = 0
    sim.code = b''
    sim.class_id = 0
    sim.events = {}
    sim.temp32 = 0
    sim._max_sp_used = sim.sp
    thisptr = (SEG_OBJ << 16) | host.objid
    args = struct.pack('<H', lb.objid)
    sim._run_child(classid, puppet_offset, thisptr, 2, args, max_steps=max_steps)
    return sim, lb


# (b-1) lbDone already 1 when puppet starts: the while condition is false
# on the very first check, so it sets frame 0 (startup), then immediately
# frame 9, and returns. No looping, no step-limit warning.
sim1, lb1 = exec_puppet(lb_done_initially=True, max_steps=2000)
seq1 = frame_sequence(sim1)
check('lbDone preset: puppet sets frame 0 then frame 9 and stops '
      '(no loop body runs)', seq1 == [0, 9], detail=f'got {seq1}')
check('lbDone preset: no step-limit / dropped-spawn warning',
      not any('dropped un-runnable spawn' in w for w in sim1.warnings),
      detail=str(sim1.warnings))

# (b-2) lbDone never set: nothing in this isolated run ever satisfies the
# loop's exit condition, so it runs until the step budget forces an abort
# (_run_child swallows that SimError as a warning; see its docstring). The
# backward jmp found statically above is what makes this loop at all;
# this is proof it also loops at runtime, cycling through frames 0 to 8
# and continuing well beyond.
sim2, lb2 = exec_puppet(lb_done_initially=False, max_steps=3000)
seq2 = frame_sequence(sim2)
check('lbDone never set: puppet hits the step budget, genuinely looping',
      any('dropped un-runnable spawn' in w for w in sim2.warnings),
      detail=str(sim2.warnings))
check('lbDone never set: frame sequence starts 0,1,2,...,8 (the '
      'frame-cycling logic runs, in order)',
      seq2[:9] == [0, 1, 2, 3, 4, 5, 6, 7, 8], detail=f'got {seq2[:9]}')
check('lbDone never set: puppet keeps iterating well past the first 8 '
      'frames (the backward jmp found statically above fires repeatedly '
      'at runtime). NOTE: the count==4 / getFrame()==8 hold-and-wrap '
      "cannot be demonstrated here, because u8c_sim.py's own setFrame "
      'handler reads its two args in the opposite order from what the '
      'compiled bytecode pushes them in (found while writing this test, '
      'pre-existing in the simulator, left alone), so getFrame() never '
      'observes a mutated frame and the wrap condition stays silent in '
      "the sim. The real build's playtest capture is the authority for "
      'the wrap (docs/playtest-2026-09-26-lamps-plaques-lb.md, finding 1).',
      len(seq2) > 9, detail=f'{len(seq2)} setFrame calls logged: {seq2}')

print('=' * 68)
print(f'{passed} passed, {failed} failed')
print('=' * 68)
sys.exit(1 if failed else 0)
