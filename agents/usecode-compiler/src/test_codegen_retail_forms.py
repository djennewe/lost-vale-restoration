#!/usr/bin/env python3
"""test_codegen_retail_forms.py: codegen forms pinned to retail bytes
(shared/data/USECODE.FLX), found 2026-10-07 from the 2026-10-03 killProcess
playtest (docs/playtest-2026-10-03-killprocess.md findings 1 and 4) and
TODO.md's compiler-bug list.

1. A foreach filter against a run-time value (`frame = counter`, `type = t`)
   pushes the value into the loopscript: retail ARAMINA 0x40D 04A5-04AB
   `74 3D 74 60 3F FC 74 25`. We compiled it as a constant 0.
2. A process intrinsic used as a value waits for and yields its result:
   retail ARAMINA 0x40D 04C4-04D8 (`if pathfind(...)`).
3. `npc.enterConvo()` / `npc.exitConvo()` are the convo statements aimed at
   that NPC (FREE.UNK's `agent.enterConvo()` was a parse error).
4. String `+` is concat (0x16) and a literal keeps its edge space: retail
   ARAMINA 0x40D 1146-115F `"Yes, I am " ... concat ... concat`.
5. `&` is bit_and (0x39): retail ARAMINA 0x40D 05C1-05C4.
6. A foreach search centre is a full postfix expression
   (`within 30 cells of caster.referent`, AVATAR.UNK).
7. The NPC-ref byte push covers only the NPC window (0x401-0x474).

Exits nonzero on any failure.
"""
import os
import re
import sys
import struct
import tempfile

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC_DIR)

from u8c_parser import parse_file  # noqa: E402
from u8c_codegen import CodeGenerator  # noqa: E402
from u8c_symbols import create_symbol_table  # noqa: E402

PASS = FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name} {detail}")


def compile_body(body, decl=''):
    f = tempfile.NamedTemporaryFile('w', suffix='.UNK', delete=False,
                                    encoding='latin-1')
    f.write("class TypeTest inherits Item;\n" + decl +
            "process TypeTest::t()\n{\n" + body + "\n}\n")
    f.close()
    ast = parse_file(f.name)
    os.unlink(f.name)
    return bytes(CodeGenerator(create_symbol_table()).generate_class(ast))


def loopscr(*bs):
    return b''.join(bytes([0x74, b]) for b in bs)


print("1. run-time loopscript operands")
data = compile_body("pathEgg:Item;\ncounter:Number;\n"
                    "foreach pathEgg where (type = 174) and (frame = counter) "
                    "within 50 cells of referent {\n}")
# emission order: $ & = ` <push counter> % <shape-174 compact form>
check("`frame = counter` pushes the local between ` and %",
      loopscr(0x24, 0x26, 0x3D, 0x60) + bytes.fromhex('3F') in data
      and loopscr(0x25) in data, data.hex())
# A 0xAE 0x00 (3) + % <word> ` = (5) + & $ (2) = 10 script bytes
check("script size counts the pushed word as 2 bytes (10)",
      any(data[i] == 0x70 and data[i + 2:i + 4] == b'\x0A\x02'
          for i in range(len(data) - 3)), data.hex())
data = compile_body("i:Item;\nt:Number;\n"
                    "foreach i where type = t within container referent {\n}")
check("`type = <local>` is '% <word> @ =', not shape 0",
      loopscr(0x24, 0x3D, 0x40) + b'\x3F' in data and loopscr(0x41) not in data,
      data.hex())

print("2. process intrinsic as a value")
data = compile_body("e:Item;\nif pathfind(e.referent, 20) {\n}")
check("push pid ... calli pathfind; push retval; implies; pop temp; suspend; "
      "push process result; long to int",
      bytes.fromhex('59') in data and
      bytes.fromhex('0F08A200' '6EF8' '5E' '540101' '12' '53' '6D' '61') in data,
      data.hex())
data = compile_body("e:Item;\npathfind(e.referent, 20);")
check("statement form waits too, without the result (ARAMINA 0x40D 0C1F)",
      bytes.fromhex('59') in data and
      bytes.fromhex('0F08A200' '6EF8' '5E' '540101' '12' '53') in data and
      b'\x6D\x61' not in data, data.hex())

print("3. npc.enterConvo()")
data = compile_body("agent:Npc;\nagent.enterConvo();\nagent.exitConvo();")
check("enterConvo spawns retail METHOD enterConvo on the named NPC "
      "(push pid; push addr; spawn 057C:0BCF; wait), as 0x4B5 02F2",
      bytes.fromhex('59 4BFC 5700027C05CF0B 5E 540101 12 53') in data,
      data.hex())
check("exitConvo spawns retail METHOD exitConvo on the named NPC and adds "
      "nothing (no cSetActivity), as SORCHAT 0x4B5 034C (section 26)",
      bytes.fromhex('59 4BFC 5700027C059010 5E 540101 12 53') in data
      and bytes.fromhex('0F06AE00') not in data, data.hex())

print("4. string concatenation")
data = compile_body('s:String;\ns = "Yes, I am "+getName()+".";')
check('"Yes, I am " keeps its trailing space',
      b'Yes, I am \x00' in data, data.hex())
check("string + is concat (16), not add (14) (ARAMINA 0x40D 1154)",
      bytes.fromhex('0F00BC00' '5E' '16') in data and
      data.count(b'\x16') >= 2, data.hex())

print("5. bitwise and")
data = compile_body("x:Number;\nx = Avatar.getStatus() & 16;")
check("`&` emits bit_and (39)", bytes.fromhex('5E' '0A10' '39') in data,
      data.hex())

print("6. foreach centre is a postfix expression")
data = compile_body("i,c:Item;\nforeach i where type = 174 "
                    "within 30 cells of c.referent {\n}")
check("`within 30 cells of c.referent` parses and compiles",
      bytes.fromhex('0A1E' '0A20' '1E') in data and b'\x70' in data, data.hex())

print("7. NPC window")
from u8c_codegen import npc_num_of_class  # noqa: E402
check("EZREKAL 0x474 is npcNum 116", npc_num_of_class(0x474) == 116)
check("AVATAR 0x401 is npcNum 1", npc_num_of_class(0x401) == 1)
check("TYPERECE 0x478 and MAPTELE 0x480 are not NPCs",
      npc_num_of_class(0x478) is None and npc_num_of_class(0x480) is None)


# ── Retail citations. Every form below is first checked to be present in
# shared/data/USECODE.FLX at the cited (class, offset): offset as the
# reference disassembler prints it, i.e. into the class data after its
# 12-byte header. Missing retail data fails loudly, never skips.
from u8_flex import UsecodeFlexArchive  # noqa: E402
RETAIL = UsecodeFlexArchive(os.path.join(SRC_DIR, '..', '..', '..', 'shared',
                                         'data', 'USECODE.FLX'))


def retail(classid, offset, hexbytes):
    want = bytes.fromhex(hexbytes)
    got = RETAIL.get_class_data(classid)[12 + offset:12 + offset + len(want)]
    check(f"retail {classid:04X}:{offset:04X} is {hexbytes}", got == want,
          got.hex())
    return want


def compile_src(src):
    f = tempfile.NamedTemporaryFile('w', suffix='.UNK', delete=False,
                                    encoding='latin-1')
    f.write(src)
    f.close()
    ast = parse_file(f.name)
    os.unlink(f.name)
    check("  (source parses clean)", not ast.parse_errors, ast.parse_errors)
    return ast, bytes(CodeGenerator(create_symbol_table()).generate_class(ast))


print("8. Item List / String List locals (FREE 0x581 give/take/countStrList)")
retail(0x581, 0x1F61, '3FFE 0E0201 64F8 01F8')          # L = <<item>>
retail(0x581, 0x1FBF, '42F802 3FFE 0E0201 17 64F8 01F8')  # L += <<item>>
retail(0x581, 0x1FCF, '42F802 0BFFFF 75FE020B00')       # foreach item in L
retail(0x581, 0x22E8, '3FFC 3FF8 440200')               # L[element]
retail(0x581, 0x29BA, '4306 0BFFFF 76FE02')             # foreach in slist
_, data = compile_src(
    "routine r(t:Number) {\n item : Item;\n L : Item List;\n"
    " n : Number = 1;\n L = <<item>>;\n L += <<item>>;\n"
    " foreach item in L {\n  item.destroy();\n }\n item = L[n];\n}\n")
# item [BP-04h] (our Item slot is 4 bytes), L [BP-06h], n [BP-08h]
check("L = <<item>>: push item; create list; free list L; pop L",
      bytes.fromhex('3FFC 0E0201 64FA 01FA') in data, data.hex())
check("L += <<item>>: push list L (copy); item; create; append; free; pop",
      bytes.fromhex('42FA02 3FFC 0E0201 17 64FA 01FA') in data, data.hex())
check("foreach item in L: push list; FFFF; for each [item] rel16 past jmp",
      bytes.fromhex('42FA02 0BFFFF 75FC020B00 4BFC 0F043A00 6EFC 52F0FF')
      in data, data.hex())
check("L[n]: push L (handle, no copy); push n; push element 02 00",
      bytes.fromhex('3FFA 3FF8 440200 01FC') in data, data.hex())
_, data = compile_src("routine c(list:String List) {\n m : String;\n"
                      " foreach m in list {\n }\n}\n")
check("foreach over a String List param: push slist [BP+06]; for each str",
      bytes.fromhex('4306 0BFFFF 76FC02') in data, data.hex())
_, data = compile_src("routine c(list:Number List) {\n m : Number;\n"
                      " foreach m in list {\n }\n}\n")
check("foreach over a Number List param: push list [BP+06] 02",
      bytes.fromhex('420602 0BFFFF 75FE02') in data, data.hex())

print("9. modulo, |, /=")
retail(0x581, 0x28EB, '5E 0A18 22')          # getHour: ... modulo 24
retail(0x57C, 0x084E, '0A08 0A04 3A')         # boom: DMG_FIRE|DMG_BLUNT
retail(0x581, 0x2900, '5E 0A04 20 01FE')    # getPeriod: getHour() / 4
data = compile_body("h:Number;\nh = TimeInGameHours() modulo 24;")
check("`modulo` is mod (0x22)", bytes.fromhex('5E 0A18 22') in data,
      data.hex())
data = compile_body("h:Number;\nh = 8 | 4;")
check("`|` is bit_or (0x3A)", bytes.fromhex('0A08 0A04 3A') in data,
      data.hex())
data = compile_body("d:Number;\nd /= 32;")
check("`d /= 32` is push d; push 32; div; pop d (operand order of +=)",
      bytes.fromhex('3FFE 0A20 20 01FE') in data, data.hex())

print("10. Camera:: scoped intrinsic calls (FREE 0x581)")
retail(0x581, 0x1C7D, '0F08B500')                 # Camera::scrollTo
retail(0x581, 0x1CD9, '0A01 0F02BE00 6EFE')       # setCenterOn(Avatar)
data = compile_body("Camera::setCenterOn(Avatar:Referent);")
check("Camera::setCenterOn(Avatar:Referent) = retail 1CD9 exactly",
      bytes.fromhex('0A01 0F02BE00 6EFE') in data, data.hex())
_, data = compile_src("process scrollTo(x:Number,y:Number,z:Number,v:Number)"
                      "\n{\n Camera::scrollTo(x, y, z, 6:Number);\n}\n")
check("Camera::scrollTo inside FREE's own scrollTo binds intrinsic 0xB5, "
      "args right-to-left, no `this`",
      bytes.fromhex('0A06 3F0A 3F08 3F06 0F08B500') in data and
      b'\x57' not in data, data.hex())
data = compile_body("x:Number;\nx = Camera::getX();")
check("Camera::getX() as a value: calli 00 C3 00; push retval",
      bytes.fromhex('0F00C300') in data and b'\x5E\x01\xFE' in data,
      data.hex())

print("11. within 1 cell (METHOD 0x57C boom)")
retail(0x57C, 0x0814, '0A01 0A20 1E')
data = compile_body("i,c:Item;\nforeach i where type = 400 "
                    "within 1 cell of c.referent {\n}")
check("`within 1 cell` scales by 32 like `cells`",
      bytes.fromhex('0A01 0A20 1E') in data, data.hex())

print("12. switch default (MORDEA 0x407)")
retail(0x407, 0x17DB, '51CF00')     # last case's jne -> 18AD, the default
retail(0x407, 0x18AD, '0A0A 0F02B600')  # default body: urandom(10)
data = compile_body('s:String;\nswitch s {\n case "a" {\n  s = "b";\n }\n'
                    ' default {\n  s = "c";\n }\n}')
i = data.find(b'\x0D\x01\x00c\x00')
j = data.find(b'\x51')
check("default body follows the last case's jne target",
      i > 0 and j > 0 and j + 3 + int.from_bytes(data[j + 1:j + 3], 'little',
                                                  signed=True) == i,
      data.hex())

print("13. bare routine named like an event (FREE combine)")
retail(0x581, 0x200D, '3FFE 11810567 27')
_, data = compile_src("routine combine(i:Item) {\n}\n"
                      "routine g(i:Item) {\n combine(i);\n}\n")
check("combine(i) calls the class's own routine (0x11), not intrinsic 0x65",
      b'\x11' in data and bytes.fromhex('0F046500') not in data, data.hex())

print("14. spawn inline (AVATAR 0x401 look, \"Call Guards\")")
retail(0x401, 0x2FE4, '58 0104 B200 592F 02 00')
retail(0x401, 0x3003, '5E 540101 12 521100')
retail(0x401, 0x300B, '5A00 0A01 0A00 77 53')
_, data = compile_src(
    "process Avatar::look() {\n caster : Npc;\n"
    " spawn caster.doAnim(14, 0, 0, 0) ->\n  [[PT_DEFAULT,NULL_REF]] {\n"
    "   caster.setDead();\n  } -> return;\n}\n")
k = data.find(b'\x58')
code = data[12 + 0x80:]
check("0x58 class func delta 02 00 leads", k > 0 and data[k + 7:k + 9] == b'\x02\x00',
      data.hex())
func = int.from_bytes(data[k + 3:k + 5], 'little')
delta = int.from_bytes(data[k + 5:k + 7], 'little')
body = data[12 + func + delta:12 + func + delta + 8]
check("func+delta lands on `init 00; [[PT_DEFAULT,NULL_REF]]; suspend`",
      body == bytes.fromhex('5A00 0A01 0A00 77 53'), body.hex())
check("no push pid for the awaited spawn, implies, no caller suspend",
      bytes.fromhex('6EF4 5E 540101 12 52') in data and
      bytes.fromhex('59 0A00') not in data[k:k + 12], data.hex())

print("15. `suspend;` statement, forward declarations")
data = compile_body("suspend;")
check("`suspend;` is opcode 0x53, not a stray push 0",
      bytes.fromhex('5A00 53 50') in data and b'\x0A\x00\x50' not in data,
      data.hex())
ast, data = compile_src("process crumble();\nprocess crumble()\n{\n}\n")
check("`process crumble();` is a prototype: one function",
      len(ast.functions) == 1, len(ast.functions))

print("16. x-- / x++ operand order (FREE 0x581 give/countStrList)")
retail(0x581, 0x2019, '3F0E 0A01 1C 010E')     # quan--
retail(0x581, 0x29C4, '0A01 3FFC 14 01FC')     # count++
data = compile_body("n:Number;\nn--;\nn++;")
check("`n--` pushes n first: n - 1, not 1 - n",
      bytes.fromhex('3FFE 0A01 1C 01FE') in data, data.hex())
check("`n++` keeps retail's 1-first add",
      bytes.fromhex('0A01 3FFE 14 01FE') in data, data.hex())
data = compile_body("n:Number;\nn -= 2;\nn += 2;")
check("`-=`/`+=` push the target first (DOOR_NS `pos += delta` order)",
      bytes.fromhex('3FFE 0A02 1C 01FE 3FFE 0A02 14 01FE') in data,
      data.hex())

# Run `while n { n--; }` in the simulator: it must end with n == 0.
from u8c_sim import UCSim  # noqa: E402
_, cls = compile_src(
    "process TypeTest::use() {\n n : Number = 5;\n while n {\n  n--;\n }\n"
    " if n = 0 {\n  bark(\"zero\");\n }\n}\n")


class _OneClassFlx:
    def get_object(self, index):
        return cls if index == 0x777 + 2 else b''


sim = UCSim(flx_path=os.path.join(SRC_DIR, '..', '..', '..', 'shared',
                                  'data', 'USECODE.FLX'))
sim.flx = _OneClassFlx()
try:
    sim.run_event(0x777, None, 1, max_steps=5000, event=1)
    ran = True
except Exception as e:  # SimError on step exhaustion = the old hang
    ran = str(e)
check("sim: `while n { n--; }` from 5 terminates with n == 0",
      ran is True and any(t == 'zero' for _, t in sim.barks),
      f"{ran} barks={sim.barks}")

print("17. return <expr> and the callers that read it")
retail(0x581, 0x1C0B, '0A01 12 520600 0A00 12 520000 50')  # Timer::isDone
retail(0x581, 0x1C5C, '3F06 12 520900')       # abs: return x; jmp exit
retail(0x581, 0x1B1A, '0A01 60 08 522200')    # askYesNo: return true
retail(0x581, 0x1C2E, '11 8105 F11B 6EFC 5D 51')   # if timer.isDone()
retail(0x581, 0x1E70, '11 8105 621D 6EFC 5E 01FE')  # d = getDistance(..)
retail(0x07C, 0x11FE, '59 0C00000000 57 0000 8105 D01A 5E 540101 12 53'
       ' 6D 61 51')                              # PENT: if askYesNo()
retail(0x581, 0x1CB9, '59 3F06 3EFB 0A14 14 3FFC 3FFE 0C00000000'
       ' 57 0800 8105 6D1C 6EF8 5E 540101 12 53')  # scrollTo(...);
_, data = compile_src(
    "routine isDone():Boolean {\n if getCurrentTimerTick() >= 5 {\n"
    "  return true;\n }\n return false;\n}\n")
check("routine return: push; pop temp; jmp to the one exit (isDone exact)",
      bytes.fromhex('0A01 12 520600 0A00 12 520000 50 79') in data,
      data.hex())
check("no bare `ret` for a `return`: one 50 per function",
      data[12 + 0x80:].count(b'\x50') == 1, data.hex())
_, data = compile_src("process yes():Number {\n return true;\n}\n")
check("process return: push; int to long; pop result; jmp exit",
      bytes.fromhex('0A01 60 08 520000 50 79') in data, data.hex())
retail(0x57C, 0x06F2, '528401')     # boom: bare `return;` -> jmp 0879 (exit)
_, data = compile_src("process p() {\n return;\n}\n")
check("bare return jumps to the exit (METHOD 0x57C boom 06F2)",
      data[12 + 0x80:] == bytes.fromhex('5A00 520000 50 79 79'), data.hex())
ast, data = compile_src(
    "process askYesNo():Number {\n return true;\n}\n"
    "routine ok():Boolean {\n return true;\n}\n"
    "routine two():Number {\n return 2;\n}\n"
    "process scrollTo(a:Number,b:Number) {\n}\n"
    "process TypeTest::use() {\n n : Number;\n"
    " if askYesNo() {\n }\n if ok() {\n }\n n = two();\n scrollTo(1, 2);\n}\n")
# Function offsets: each starts right after the previous one's `end`.
offs, pos, code = [], 0x80, data[12:]
while pos < len(code) - 1:
    offs.append(pos)
    pos = code.index(b'\x50\x79', pos) + 2
w = lambda off: off.to_bytes(2, 'little')  # noqa: E731
ask_off, ok_off, two_off, scroll_off = offs[:4]
check("value call of a process spawns and reads the process result "
      "(PENT 0x7C 11FE)",
      bytes.fromhex('59 0C00000000 57 0000 0000') + w(ask_off) +
      bytes.fromhex('5E 540101 12 53 6D 61 51') in data, data.hex())
check("Boolean routine: call; push byte retval (FREE 1C2E)",
      b'\x11\x00\x00' + w(ok_off) + b'\x5D\x51' in data, data.hex())
check("Number routine: call; push retval (FREE 1E70)",
      b'\x11\x00\x00' + w(two_off) + bytes.fromhex('5E 01FE') in data,
      data.hex())
check("statement call of a process spawns and waits, no 6D (FREE 1CB9)",
      bytes.fromhex('59 0A02 0A01 0C00000000 57 0400 0000') + w(scroll_off) +
      bytes.fromhex('6EFC 5E 540101 12 53 50') in data, data.hex())
check("a process is never `call`ed",
      b'\x11\x00\x00' + w(ask_off) not in data and
      b'\x11\x00\x00' + w(scroll_off) not in data, data.hex())

# The sim runs it: each value must reach its caller.
_, cls = compile_src(
    "routine addTwo(n:Number):Number {\n return n + 2;\n}\n"
    "routine isSeven(n:Number):Boolean {\n if n = 7 {\n  return true;\n }\n"
    " return false;\n}\n"
    "process less4(n:Number):Number {\n return n - 4;\n}\n"
    "process TypeTest::use() {\n r : Number = addTwo(5);\n"
    " if isSeven(r) {\n  bark(\"seven\");\n }\n"
    " if isSeven(6) {\n  bark(\"six is seven\");\n }\n"
    " h : Number = less4(r + 1);\n if h = 4 {\n  bark(\"four\");\n }\n}\n")


class _AnyClassFlx:
    def get_object(self, index):
        return cls


sim = UCSim(flx_path=os.path.join(SRC_DIR, '..', '..', '..', 'shared',
                                  'data', 'USECODE.FLX'))
sim.flx = _AnyClassFlx()
sim.follow_spawns = True
try:
    sim.run_event(0, None, 1, max_steps=5000, event=1)
    ran = True
except Exception as e:
    ran = str(e)
said = [t for _, t in sim.barks]
check("sim: routine word result reaches the caller (addTwo(5) = 7)",
      ran is True and 'seven' in said, f"{ran} barks={said}")
check("sim: routine Boolean false reaches the caller (isSeven(6))",
      ran is True and 'six is seven' not in said, f"{ran} barks={said}")
check("sim: process result reaches the spawning caller (less4(8) = 4)",
      ran is True and 'four' in said and not sim.warnings,
      f"{ran} barks={said} warnings={sim.warnings}")

print("18. the exit frees String / String List / List locals")
retail(0x581, 0x1B43, '62FE 63FC 50 79')   # askYesNo: key, keyList
retail(0x581, 0x20B4, '64F8 50 79')        # give: itemList
retail(0x57C, 0x010D, '63FE 62FC 50 79')   # ask: keyList, key
retail(0x57C, 0x0879, '64FA 50 79')        # boom: the bare return's exit
retail(0x581, 0x3670, '63FE 50 79')        # listTop: its local, not params
_, data = compile_src(
    "process ask():Number {\n key : String;\n keyList : String List;\n"
    " n : Number;\n L : Item List;\n if n {\n  return 1;\n }\n return 0;\n}\n")
check("frees in declaration order, then ret: 62 key; 63 keyList; 64 L",
      data.endswith(bytes.fromhex('0A00 60 08 520000 62FC 63F8 64F4 50 79 79')),
      data.hex())
check("the early return jumps to the frees (60 08 52 0700)",
      bytes.fromhex('0A01 60 08 520700 0A00 60 08 520000 62FC') in data,
      data.hex())
_, data = compile_src(
    "routine listTop(list:String List,line:String):String List {\n"
    " l2 : String List;\n return list;\n}\n")
check("params are not freed: only the local l2 (FREE listTop 3670)",
      data.endswith(bytes.fromhex('4306 12 520000 63FC 50 79 79')),
      data.hex())
_, cls = compile_src("process TypeTest::use() {\n s : String = \"abc\";\n"
                     " L : Item List;\n}\n")
sim = UCSim(flx_path=os.path.join(SRC_DIR, '..', '..', '..', 'shared',
                                  'data', 'USECODE.FLX'))
sim.flx = _AnyClassFlx()
try:
    sim.run_event(0, None, 1, max_steps=5000, event=1)
    ran = True
except Exception as e:
    ran = str(e)
check("sim: a String local is freed at exit (no leaked 'abc')",
      ran is True and 'abc' not in sim.strings.values(),
      f"{ran} strings={sim.strings}")

print("19. a process intrinsic called as a statement waits")
retail(0x40D, 0x0C1F, '59 0A19 3FFE 4006 0F08A200 6EF8 5E 540101 12 53')
retail(0x581, 0x1C74, '59 0A06 3E0A 3F08 3F06 0F08B500 6EF8 5E 540101 12 53')
retail(0x10D, 0x03E3, '59 0A00 4006 0F06AE00 6EFA 5E 540101 12 53')
data = compile_body("Camera::scrollTo(1, 2, 3, 6);")
check("Camera::scrollTo statement: push pid; args; calli; wait (FREE 1C74)",
      bytes.fromhex('59 0A06 0A03 0A02 0A01 0F08B500 6EF8 5E 540101 12 53')
      in data, data.hex())
data = compile_body("cSetActivity(0);")
check("a source cSetActivity(0) waits like retail 0x10D 03E3 (exitConvo "
      "no longer adds one: section 26)",
      bytes.fromhex('59 0A00 4006 0F06AE00 6EFA 5E 540101 12 53') in data,
      data.hex())
data = compile_body("x:Number;\nx = getX();")
check("a non-process intrinsic statement still does not wait",
      b'\x54' not in data, data.hex())

print("20. no `add sp 0` after a zero-argument call")
retail(0x581, 0x1BE6, '0F00D200 5F')         # getCurrentTimerTick()
retail(0x07C, 0x1204, '57 0000 8105 D01A 5E')  # spawn askYesNo()
retail(0x40D, 0x1154, '0F00BC00 5E 16')        # getName() in section 4
data = compile_body("x:Number;\nx = TimeInGameHours();\n"
                    "if getCurrentTimerTick() {\n}")
check("calli 00h straight into push retval, no 6E 00",
      bytes.fromhex('0F00D800 5E') in data and b'\x6E\x00' not in data,
      data.hex())

print("21. METHOD (0x57C) routines by retail offset; AS_*/compass names")
retail(0x2FE, 0x06C6, '0A01 0A04 6FFE 11 7C05 1301 6EF8')  # Avatar.toggle..
retail(0x581, 0x3811, '0A10 4B06 11 7C05 1301 6EFA')    # tony.toggleStatus
retail(0x044, 0x0B8F, '59 0A01 3FFA 0A00 6FFC 57 0402 7C05 E715 6EFA'
       ' 5E 540101 12 53')                               # realDoAnim
retail(0x40D, 0x032F, '4006 57 0602 7C05 1C09 6EFA 5E 540101 12 53')
retail(0x401, 0x09C6, '4BE9 11 7C05 2012 6EFC 5E')     # caster.isMage()
retail(0x402, 0x0248, '59 3FF9 45FB05 4006 57 0702 7C05 3F13 6EF9'
       ' 5E 540101 12 53')                               # safeTeleport
retail(0x06D, 0x1D7D, '57 0602 7C05 7D08 6502')        # timedBark
retail(0x581, 0x1C2C, '4BF8 11 8105 F11B 6EFC 5D')     # timer.isDone()
retail(0x581, 0x377D, '0A1B')                           # AS_ENTER_CAST
retail(0x581, 0x38A3, '0A1C')                           # AS_EXIT_CAST
retail(0x401, 0x0CCB, '0A00 01ED')                      # count = north
retail(0x401, 0x0D5E, '0A07 01ED')                      # count = northwest
retail(0x401, 0x0D63, '0A07 0A00 3FED')                 # (count,RANDOM,7)
data = compile_body(
    "caster : Npc;\np : WorldPoint;\nAvatar.toggleStatus(OWNED);\n"
    "caster.toggleStatus(INVISIBLE);\nturnToFace(north, RANDOM, 10);\n"
    "caster.realDoAnim(AS_ENTER_CAST, northwest);\n"
    "if caster.isMage() != 2 {\n}\nsafeTeleport(p, 5);\n"
    "timedBark(40, \"hi\");\n")
check("toggleStatus: arg; receiver pointer; call 057Ch 0113h; add sp -6",
      bytes.fromhex('0A04 0C01000280 11 7C05 1301 6EFA') in data and
      bytes.fromhex('0A10 4BFC 11 7C05 1301 6EFA') in data, data.hex())
check("bare turnToFace on this: args; push dword [BP+06h]; spawn 06h 02h "
      "057Ch 091Ch; wait (ARAMINA 0x40D 032F)",
      bytes.fromhex('59 0A0A 0A00 0A00 4006 57 0602 7C05 1C09 6EFA'
                    ' 5E 540101 12 53') in data, data.hex())
check("caster.realDoAnim(AS_ENTER_CAST, northwest): spawn 04h 02h 15E7h",
      bytes.fromhex('59 0A07 0A1B 4BFC 57 0402 7C05 E715 6EFC'
                    ' 5E 540101 12 53') in data, data.hex())
check("caster.isMage(): push addr; call 057Ch 1220h; add sp -4; push "
      "retval (AVATAR 0x401 09C6)",
      bytes.fromhex('4BFC 11 7C05 2012 6EFC 5E') in data, data.hex())
# safeTeleport: args right to left (map word, then the WorldPoint by
# value), the receiver, spawn 07h 02h 057Ch 133Fh, wait (0x402 0248).
# Held back 2026-10-07 to -08 while the LV schedule destinations were
# still 1994 Map 10 coordinates; retargeted and enabled 2026-10-08.
check("safeTeleport(p, 5): push pid; push byte 5; push huge p 05h; this; "
      "spawn 07h 02h 057Ch 133Fh; add sp -7; wait (0x402 0248)",
      re.search(bytes.fromhex('59 0A05') + b'\x45.\x05'
                + re.escape(bytes.fromhex('4006 57 0702 7C05 3F13 6EF9'
                                          ' 5E 540101 12 53')),
                data, re.S) is not None, data.hex())
check("timedBark: string by pointer, freed after the spawn ([SP+02h])",
      bytes.fromhex('6B 0A28 4006 57 0602 7C05 7D08 6502 6EFA') in data,
      data.hex())
retail(0x40D, 0x019B, '59 3FF9 45FB05 4006 57 0702 7C05 3A14 6EF9'
       ' 5E 540101 12 53 6D 61 51')                      # canSafeTeleport
gen = CodeGenerator(create_symbol_table())
f = tempfile.NamedTemporaryFile('w', suffix='.UNK', delete=False,
                                encoding='latin-1')
f.write("class TypeTest inherits Item;\nprocess TypeTest::t()\n{\n"
        "p : WorldPoint;\nif canSafeTeleport(p, 10) {\n"
        "safeTeleport(p, 10);\n}\n}\n")
f.close()
tdata = bytes(gen.generate_class(parse_file(f.name)))
os.unlink(f.name)
check("if canSafeTeleport(p, 10): spawn 057Ch 143Ah; wait; push process "
      "result; long to int; jne (ARAMINA 0x40D 019B), then safeTeleport",
      re.search(bytes.fromhex('59 0A0A') + b'\x45.\x05'
                + re.escape(bytes.fromhex('4006 57 0702 7C05 3A14 6EF9'
                                          ' 5E 540101 12 53 6D 61 51'))
                + b'..' + bytes.fromhex('59 0A0A') + b'\x45.\x05'
                + re.escape(bytes.fromhex('4006 57 0702 7C05 3F13 6EF9')),
                tdata, re.S) is not None
      and not any('SafeTeleport' in w or 'safeTeleport' in w
                  for w in gen.warnings), (tdata.hex(), gen.warnings))
_, data = compile_src("routine Timer::isDone():Boolean {\n return true;\n}\n"
                      "process w() {\n timer : Timer;\n"
                      " if timer.isDone() {\n }\n}\n")
check("timer.isDone(): push addr; call own method; add sp -4; push byte "
      "retval (FREE 0x581 1C2C)",
      bytes.fromhex('4BFE 11 0000 8000 6EFC 5D 51') in data, data.hex())

print("22. negative literals are one sign-extended push byte")
retail(0x401, 0x39CE, '0AFF 24')                       # x = -1
retail(0x401, 0x3B15, '0AFC 24')                       # x = -4
retail(0x41A, 0x339E, '0AE2 0A0F')                     # hurl(15,-30,..)
retail(0x581, 0x1C62, '0AFF 3F06 1E')                  # return -1 * x
retail(0x581, 0x1D98, '0AFF 12')                       # differentMap
data = compile_body("x : Number;\nx = -1;\nif x = -4 {\n}\nx = -30;\n"
                    "x = -1 * x;\nx = -128;\nx = -200;\nx = differentMap;")
check("-1 is `0A FF`, never `0A 00 0A 01 1C`",
      bytes.fromhex('0AFF 01FE') in data
      and bytes.fromhex('0A00 0A01 1C') not in data, data.hex())
check("-4 / -30 / -128 are `0A FC` / `0A E2` / `0A 80`",
      bytes.fromhex('3FFE 0AFC 24') in data
      and bytes.fromhex('0AE2 01FE') in data
      and bytes.fromhex('0A80 01FE') in data, data.hex())
check("-1 * x is `0A FF; push x; mul` (FREE 0x581 1C62)",
      bytes.fromhex('0AFF 3FFE 1E') in data, data.hex())
check("below -128 (no retail site) keeps 0 - n",
      bytes.fromhex('0A00 0BC800 1C') in data, data.hex())
check("differentMap is `0A FF` (FREE 0x581 1D98)",
      data.count(bytes.fromhex('0AFF 01FE')) == 2, data.hex())

print("23. `spawn x -> return;` does not wait; chains link their spawns")
retail(0x40D, 0x021F, '4006 57 0002 0D04 6004 5E 12 52')  # spawn atHome()
retail(0x405, 0x1C94, '0F08 4900 6504 6EF6 5E 12')     # spawn Avatar.bark
retail(0x581, 0x372C, '4BFD 0F04 5D00 6EFC 5E 12')     # spawn item.use()
retail(0x581, 0x37EF, '57 0500 8305 651F 6EFB 5E 12')  # spawn flameBlast(p)
retail(0x40D, 0x0D55, '57 0602 7C05 1C09 6EFA 5E')     # chain head
retail(0x40D, 0x0D65, '57 0402 7C05 E715 6EFC 5E 540101')  # chain link
retail(0x40D, 0x0D83, '57 0602 7C05 1C09 6EFA 5E 540101 12 52')  # last
_, data = compile_src(
    "class TypeTest inherits Item;\n"
    "process TypeTest::home() {\n}\n"
    "process TypeTest::t() {\n item : Item;\n"
    " spawn home() -> return;\n"
    " spawn item.use() -> return;\n"
    " spawn bark(\"hi\") -> return;\n"
    " spawn turnToFace(2, 0, 10) -> spawn realDoAnim(AS_FIDGET, 3) ->\n"
    "  spawn turnToFace(4, 0, 20) -> return;\n"
    " spawn home();\n"
    " home();\n}\n")
code = data[12 + 0x80:].hex()
check("spawn home() -> return: no pid; spawn; push retval; pop temp "
      "(ARAMINA 0x40D 021F)",
      re.search('4006570002........' '5e12' '4bfc', code) is not None, code)
check("spawn item.use() -> return: calli; add sp; push retval; pop temp "
      "(FREE 0x581 372C)",
      '4bfc0f045d006efc5e12' in code and '594bfc0f045d00' not in code, code)
check("spawn bark() -> return: calli; free; add sp; push retval; pop temp "
      "(DARION 0x405 1C94)",
      '0f08490065046ef85e12' in code, code)
check("chain: head keeps its pid; each later spawn implies on the one "
      "below; the last pid is popped (ARAMINA 0x40D 0D55-0D90)",
      re.search('57 0602 7c05 1c09 6efa 5e'.replace(' ', '') + '.*?'
                + '57 0402 7c05 e715 6efc 5e 540101'.replace(' ', '')
                + '.*?' + '57 0602 7c05 1c09 6efa 5e 540101 12'.replace(
                    ' ', ''), code) is not None, code)
check("arrowless spawn home(): nothing after the spawn (rule b)",
      re.search('4006570002........' '594006', code) is not None, code)
check("only the plain call home() waits: one push pid, one suspend",
      code.count('5e54010112' '53') == 1
      and re.search('59' '4006570002........' '5e54010112' '53', code)
      is not None, code)
print("U. an unresolved call used as a value")
# HRODNY's `if canSafeTeleport(...)` emitted no call and then `push
# retval`, so the branch read whatever the last real call left in the
# temp register. Nothing was called: the condition must be a fixed 0.
data = compile_body("x:Number;\nif noSuchRoutine(1) {\n x = 1;\n}")
check("unresolved function as a condition: push byte 0; jne",
      bytes.fromhex('0A00' '51') in data
      and not any(op in data for op in (b'\x5d', b'\x5e', b'\x5f')),
      data.hex())
data = compile_body("x:Number;\nx = Avatar.noSuchMethod();")
check("unresolved method as a value: push byte 0; pop into x",
      bytes.fromhex('0A00' '01') in data
      and not any(op in data for op in (b'\x5d', b'\x5e', b'\x5f')),
      data.hex())

print("24. `key = Avatar.ask(keyList)` waits for the answer")
# Item::ask is `strptr process`: the value is the answer, read back after
# the wait. LVFREE askYesNo compiled `calli 06 004A; add sp; push retval`
# and compared the ask's pid against "Yes." (playtest 2026-10-07 wave 2
# A3b: "Make up your mind" before the player clicked).
retail(0x581, 0x1AF0, '59 0A01 43FC 6FFE 0F064A00 6704 6EF8 '
       '5E 540101 12 53 6D 61 62FE 01FE')
data = compile_body('key:String;\nkeyList:String List;\n'
                    'keyList = <<"Yes.", "No.">>;\n'
                    'key = Avatar.ask(keyList);')
# Our receiver is the SEG_OBJ pointer (push dword 80020001h), retail's an
# objid temp (push byte 1; push addr [SP-02h]); see _gen_item_ptr.
check("push pid; push slist; Avatar; calli 06h 004Ah; free slist [SP+04h]; "
      "add sp; push retval; implies; pop temp; suspend; push process "
      "result; long to int; free string; pop key",
      re.search(b'\x59\x43.' + re.escape(bytes.fromhex(
          '0C01000280 0F064A00 6704 6EFA 5E 540101 12 53 6D 61'))
          + b'\x62(.)\x01\\1', data, re.S) is not None, data.hex())
data = compile_body('keyList:String List;\nkeyList = <<"Yes.", "No.">>;\n'
                    'Avatar.ask(keyList);')
check("statement form waits too, without the result",
      bytes.fromhex('0F064A00 6704 6EFA 5E 540101 12 53') in data
      and b'\x6D\x61' not in data, data.hex())

print("25. an event's process type is retail's, not 0x208 + event")
retail(0x401, 0x0080, '5A00 0B0702')   # AVATAR use(): type 0x207
for ev, typ in (('use', '0702'), ('look', '0802'), ('hatch', '1002'),
                ('enterFastArea', '1B02'), ('leaveFastArea', '1C02')):
    _, cls = compile_src("process TypeTest::%s() {\n}\n" % ev)
    check(f"{ev}() preamble pushes {typ[2:]}{typ[:2]}h",
          bytes.fromhex('0B' + typ + '4006 4C02 77 78') in cls, cls.hex())

print("26. enterConvo()/exitConvo() spawn retail METHOD 0x57C, and nothing "
      "more")
# All 49 retail enterConvo and 256 exitConvo sites have this one form
# (u8c_symbols METHOD_ROUTINES). Until 2026-10-09 we emitted four resetRefs
# + stasis and stasis + cSetActivity(0) instead: no gump close, no
# turn-to-face, no camera, no somebodyTalking, no dead/invisible abort,
# and every NPC loitered after a talk (Aramina's route was lost,
# docs/playtest-2026-10-09-final.md finding 3).
# From 7cc1051 until the fork's Item::I_enterFastArea fix (scummvm-lv
# dccab1e7) exitConvo was also followed by a spawn of the class's own
# enterFastArea handler, or cSetActivity(0) without one, because ScummVM's
# intrinsic skipped an NPC already in the fast area. The fixed intrinsic
# fires the event as U8.EXE 10d8:2577 does, so METHOD 109A restarts the
# NPC itself and our addition started a second activity. Retail's compiler
# adds nothing after exitConvo: the 19 sites in its three NPC classes with
# no enterFastArea (THURGIST, PESANT1, CHILD) are followed by a cSetActivity
# their source wrote, and SORCHAT's named one by its next statement.
ENTER = retail(0x40D, 0x1136, '59 4006 5700027C05CF0B 5E 540101 12 53')
EXIT = retail(0x40D, 0x11B1, '59 4006 5700027C059010 5E 540101 12 53')
retail(0x4B5, 0x02F2, '59 4BFE 5700027C05CF0B 5E 540101 12 53')
retail(0x4B5, 0x034C, '59 4BFE 5700027C059010 5E 540101 12 53 0A01')
retail(0x57C, 0x0BCF, '5A00 0B0100 4006 4C02 77')   # enterConvo's head
retail(0x57C, 0x0E47, '0A01 4F0F0001')              # somebodyTalking = 1
retail(0x57C, 0x1090, '5A00 0B0100 4006 4C02 77')   # exitConvo's head
retail(0x57C, 0x109A, '59 4006 0F046700')           # Item::enterFastArea()
retail(0x57C, 0x10EF, '0A00 4F0F0001')              # somebodyTalking = 0
# THURGIST has no enterFastArea: exitConvo, then its SOURCE's loiter.
TAIL_10D = retail(0x10D, 0x03D3, '59 4006 5700027C059010 5E 540101 12 53'
                  '59 0A00 4006 0F06AE00 6EFA 5E 540101 12 53')
# A bare `enterFastArea();` in a class with that handler spawns it.
retail(0x40D, 0x0379, '59 4006 5700020D04D601 5E 540101 12 53')


def compile_cls(src):
    f = tempfile.NamedTemporaryFile('w', suffix='.UNK', delete=False,
                                    encoding='latin-1')
    f.write(src)
    f.close()
    ast = parse_file(f.name)
    os.unlink(f.name)
    gen = CodeGenerator(create_symbol_table())
    return bytes(gen.generate_class(ast)), gen._classid


def own_efa(data, cid):
    """Retail 0x40D 0379's spawn of this class's own enterFastArea."""
    efa_off = struct.unpack_from('<I', data, 12 + 15 * 4)[0]
    return (bytes.fromhex('59 4006 570002') + struct.pack('<HH', cid, efa_off)
            + bytes.fromhex('5E 540101 12 53'))


EFA_SRC = ("class TypeTest inherits Item;\n"
           "process TypeTest::enterFastArea()\n{\n\tcSetActivity(0);\n}\n")
NPC_SRC = EFA_SRC + "process TypeTest::use()\n{\n\tenterConvo();\n%s}\n"
data, cid = compile_cls(NPC_SRC % "\tif urandom(2)\n\t{\n\t\texitConvo();\n"
                        "\t\treturn;\n\t}\n\texitConvo();\n")
check("enterConvo() is retail ARAMINA 0x40D 1136 byte for byte",
      data.count(ENTER) == 1, data.hex())
check("each exitConvo() is retail 0x40D 11B1 byte for byte, and a body "
      "ending in one gets no second one from the epilogue",
      data.count(EXIT) == 2, data.hex())
check("no spawn of the class's own enterFastArea after exitConvo: "
      "METHOD 109A's Item::enterFastArea reruns it",
      own_efa(data, cid) not in data, data.hex())
check("no resetRef and no Npc::getNpcSlot in the conversation bracket "
      "(METHOD kills referent's processes itself)",
      bytes.fromhex('0F04CB00') not in data
      and bytes.fromhex('0F049A00') not in data, data.hex())
check("no cSetActivity(0) in use(): the handler's own is the only one",
      data.count(bytes.fromhex('0F06AE00')) == 1, data.hex())
data, cid = compile_cls(NPC_SRC % "\tx:Number;\n\tx = 1;\n")
check("a body that falls off its end gets exitConvo() from the epilogue, "
      "and nothing after it",
      data.count(EXIT) == 1 and own_efa(data, cid) not in data
      and data.count(bytes.fromhex('0F06AE00')) == 1, data.hex())
data, _ = compile_cls(NPC_SRC % "\texitConvo();\n\tx:Number;\n\tx = 1;\n")
check("but none after a top-level exitConvo() followed by other "
      "statements (ZCHILD's `exitConvo(); cSetActivity(..); }`)",
      data.count(EXIT) == 1, data.hex())
data, _ = compile_cls("class TypeTest inherits Item;\n"
                      "process TypeTest::use()\n{\n\tenterConvo();\n"
                      "\texitConvo();\n}\n")
check("no enterFastArea handler: exitConvo() adds no cSetActivity(0)",
      data.count(EXIT) == 1 and bytes.fromhex('0F06AE00') not in data,
      data.hex())
data, _ = compile_cls("class TypeTest inherits Item;\n"
                      "process TypeTest::use()\n{\n\tenterConvo();\n"
                      "\texitConvo();\n\tcSetActivity(0);\n}\n")
check("ZCHILD's `exitConvo(); cSetActivity(ACT_LOITER);` is retail 0x10D "
      "03D3-03F3 byte for byte, with one loiter",
      data.count(TAIL_10D) == 1
      and data.count(bytes.fromhex('0F06AE00')) == 1, data.hex())
data, cid = compile_cls(EFA_SRC + "process TypeTest::look()\n{\n"
                        "\tenterFastArea();\n}\n")
check("a bare enterFastArea() in a class with that handler spawns it, "
      "retail ARAMINA 0x40D 0379's form",
      data.count(own_efa(data, cid)) == 1
      and bytes.fromhex('0F046700') not in data, data.hex())
data, _ = compile_cls("class TypeTest inherits Item;\n"
                      "process TypeTest::look()\n{\n\tenterFastArea();\n}\n")
check("without the handler it stays intrinsic 0x67 on `this`, as METHOD "
      "0x57C 109A",
      bytes.fromhex('59 4006 0F046700 6EFC 5E 540101 12 53') in data, data.hex())

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
