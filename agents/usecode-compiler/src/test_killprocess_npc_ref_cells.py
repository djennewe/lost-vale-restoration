#!/usr/bin/env python3
"""test_killprocess_npc_ref_cells.py: three codegen defects found in ScummVM
on 2026-10-02 (docs/playtest-2026-10-02-pt-activity.md, findings 1 and the
Aramina warning flood).

1. LVFREE `killProcess` compiled to `init 00; push byte 0; ret`. Its body
   was `Kernel::resetRef(r,ptype);` and `::` does not parse, so `Kernel`
   became an unknown identifier (push 0) and all 43 call sites killed
   nothing. Retail FREE (class 0x0581 offset 2A56) is
   `init 00; push [BP+08]; push [BP+06]; calli 04 00CB; add sp -4; ret`.
2. An NPC class name in expression position (`within N cells of Aramina`,
   `killProcess(Atli:Referent, ...)`) pushed the CLASS id (0x040D) where
   retail pushes the NPC's object number as a byte (`push byte +13`). The
   engine logged "Invalid item 1037 passed to area search!" about 180
   times a second and the search never matched.
3. `within N cells of X` pushed the bare N. Retail pushes `N; push byte
   32; mul`, in every retail NPC class with an area search.

Exits nonzero on any failure.
"""
import os
import re
import sys
import tempfile

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, os.path.join(os.path.dirname(SRC_DIR), '..', 'usecode-disasm', 'src'))

from u8c_parser import parse_file  # noqa: E402
from u8c_codegen import CodeGenerator  # noqa: E402
from u8c_symbols import create_symbol_table  # noqa: E402

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


def compile_src(src, name_override=None):
    f = tempfile.NamedTemporaryFile('w', suffix='.UNK', delete=False,
                                    encoding='latin-1')
    f.write(src)
    f.close()
    ast = parse_file(f.name)
    cg = CodeGenerator(create_symbol_table(), class_name_override=name_override) \
        if name_override else CodeGenerator(create_symbol_table())
    data = cg.generate_class(ast)
    os.unlink(f.name)
    return bytes(data), cg


def compile_body(body):
    return compile_src("class TypeTest inherits Item;\n"
                       "process TypeTest::t()\n{\n" + body + "\n}\n")


# ---- 1. killProcess -------------------------------------------------------
print("killProcess in lv-patched/FREE.UNK")
free_path = os.path.join(SRC_DIR, 'lv-patched', 'FREE.UNK')
free_src = open(free_path, encoding='latin-1').read()
live = [l for l in free_src.split('\n')
        if 'Kernel::' in l and not l.lstrip().startswith('//')]
check("no live `Kernel::` spelling left in the patched FREE.UNK", not live,
      str(live))

ast = parse_file(free_path)
cg = CodeGenerator(create_symbol_table(), class_name_override='LVFREE')
free_bytes = bytes(cg.generate_class(ast))
RETAIL_KILL = bytes.fromhex('5A00' '3F08' '3F06' '0F04CB00' '6EFC' '50')
check("LVFREE carries retail's killProcess body (calli 04 00CB)",
      RETAIL_KILL in free_bytes)
check("LVFREE has no stub killProcess (init 00; push byte 0; ret)",
      free_bytes.count(bytes.fromhex('5A00' '0A00' '50')) == 0)
check("no `unknown identifier 'Kernel'` warning from FREE.UNK",
      not any("'Kernel'" in w for w in getattr(cg, 'warnings', [])))

# ---- 2. NPC class name as item reference ---------------------------------
print("NPC class name in expression position")
data, _ = compile_body("resetRef(Aramina:Referent, PT_ACTIVITY);")
check("Aramina:Referent pushes npc 13 as a byte, not class 0x040D",
      bytes.fromhex('0B0502' '0A0D') in data and b'\x0B\x0D\x04' not in data)
data, _ = compile_body("resetRef(Xavier:Referent, PT_ACTIVITY);")
check("Xavier:Referent pushes npc 0x19 as a byte",
      bytes.fromhex('0B0502' '0A19') in data)

data, _ = compile_body("resetRef(MapTele:Referent, PT_ACTIVITY);")
check("MapTele (egg class 0x480) pushes word 0x0480, not a sign-extended byte",
      bytes.fromhex('0B0502' '0B8004') in data and bytes.fromhex('0B0502' '0A80') not in data,
      data.hex())

# ---- 3. cells * 32 -------------------------------------------------------
print("within N cells")
data, _ = compile_body(
    "pathEgg:Item;\n"
    "foreach pathEgg where (type = TypePathMarker) within 10 cells of Aramina {\n"
    "}")
# push 10, push 32, mul, push byte 13 (npcnum), loop
check("`within 10 cells of Aramina` = push 10; push 32; mul; push byte 13",
      bytes.fromhex('0A0A' '0A20' '1E' '0A0D' '70') in data)
check("no class id 0x040D left as the search centre", b'\x0B\x0D\x04' not in data)

data, _ = compile_body(
    "pathEgg:Item;\n"
    "foreach pathEgg where (type = TypePathMarker) within 2000 of referent {\n"
    "}")
check("`within 2000 of referent` (no `cells`) is not scaled",
      bytes.fromhex('0BD007' '4006') in data and bytes.fromhex('0A20' '1E') not in data)

data, _ = compile_body(
    "pathEgg:Item;\n"
    "foreach pathEgg where (type = TypePathMarker) within 50 cells of referent {\n"
    "}")
check("`within 50 cells of referent` = push 50; push 32; mul",
      bytes.fromhex('0A32' '0A20' '1E' '4006') in data)

# ---- 4. enterConvo() kills the NPC's own processes ------------------------
# docs/playtest-2026-10-02-pt-activity.md finding 2: enterConvo() passed
# Npc::getNpcSlot() (intrinsic 0x9A, a null entry that returns 0) to
# resetRef, and resetRef(0, type) kills that type for every item, so one
# conversation stopped every NPC's activity in the world. Since 2026-10-09
# enterConvo() spawns retail METHOD enterConvo (0x57C 0BCF) on `this`,
# which kills 0x205, 0x200, 0xF0 and 0x204 on `referent` itself (offset
# 0x0C0E pushes the type, then push dword [BP+06]; push indirect 2; the
# retail agreement check below), so the compiled class names no process
# type and no slot at all.
print("enterConvo()")
data, _ = compile_src("class TypeTest inherits Item;\n"
                      "process TypeTest::use()\n{\n\tenterConvo();\n"
                      "\texitConvo();\n}\n")
check("enterConvo spawns retail METHOD enterConvo on this (057C:0BCF)",
      bytes.fromhex('59' '4006' '5700027C05CF0B') in data)
check("enterConvo never calls Npc::getNpcSlot (calli 04 009A)",
      bytes.fromhex('0F049A00') not in data)
check("and emits no resetRef of its own (calli 04 00CB)",
      bytes.fromhex('0F04CB00') not in data)

# ---- retail agreement ----------------------------------------------------
RETAIL = os.path.join(BASE_DIR, 'shared', 'data', 'u8-install', 'USECODE',
                      'EUSECODE.FLX.bak')
if os.path.exists(RETAIL):
    print("retail EUSECODE.FLX.bak")
    from u8_flex import UsecodeFlexArchive  # noqa: E402
    flx = UsecodeFlexArchive(RETAIL)
    pat = re.compile(rb'\x0a(.)\x0a\x20\x1e\x0a(.)\x70', re.S)
    for cid in (0x40D, 0x416, 0x419, 0x405, 0x407, 0x403, 0x417, 0x41A):
        hits = pat.findall(bytes(flx.get_class_data(cid)))
        npcs = {h[1][0] for h in hits}
        check(f"retail {cid:04X}: every area search is `N*32` around its own npc "
              f"{cid - 0x400} (or the Avatar)", bool(hits) and (cid - 0x400) in npcs and npcs <= {1, cid - 0x400},
              str(npcs))
    retail_method = bytes(flx.get_class_data(0x57C))
    seq = b''.join(bytes.fromhex('0B' + t + '4006' '4C02' '118105562A' '6EFC')
                   for t in ('0502', '0002', 'F000', '0402'))
    check("retail METHOD enterConvo kills referent's 0x205, 0x200, 0xF0, "
          "0x204 the same way", seq in retail_method)
    retail_free = bytes(flx.get_class_data(0x581))
    check("retail FREE contains the same killProcess body",
          RETAIL_KILL in retail_free)
else:
    print("  skip retail checks (EUSECODE.FLX.bak absent)")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
