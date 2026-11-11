---
paths:
  - "agents/usecode-compiler/src/lv-new/*.UNK"
  - "agents/usecode-compiler/src/lv-patched/*.UNK"
---

# A file-local `routine` in a new class calls into class 0. Inline it.

Writing a helper next to a new class and calling it from that class's process
compiles cleanly, emits **no warning**, and is wrong:

```
routine kickGod(encased:Number, run:Number) { ... }
...
kickGod(2, 30);
```

disassembles to

```
0325: 11 00 00 80 00    call 0000h 0080h    ; class 0000 offset 0080
```

— a jump into base-game class 0 at offset 0x80, not into the class the
routine was written in. Whatever is at that address runs instead.

Found 2026-09-14 in `AOSCENE.UNK`, whose three god-shatter kicks all resolved
this way. It was the **only** file-local routine in `lv-new/`, so there is no
working precedent for one and no reason to believe the resolution has ever
worked.

## What to do instead

**Inline the body at each call site.** Three copies of a six-line `foreach`
cost nine lines and cannot mis-resolve. That is what `AOSCENE.UNK` does now,
with a comment saying why, so nobody factors it back out.

If a helper is genuinely worth having, put it in a class that is already
built and call it qualified (`FREE::wait` is reached this way by
`_gen_wait`'s hard-coded `class 0x0581, offset 0x1C19`), and **disassemble
the call site** before believing it.

## How to catch it

The compiler will not tell you. Disassemble the class and look for
`call 0000h`:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0,'agents/usecode-compiler/src')
sys.path.insert(0,'agents/usecode-disasm/src')
from u8c_parser import parse_file
from u8c_codegen import CodeGenerator
from u8c_symbols import create_symbol_table
from u8_usecode_disasm import UsecodeDisassembler
d = CodeGenerator(create_symbol_table()).generate_class(
        parse_file('agents/usecode-compiler/src/lv-new/YOURFILE.UNK'))
print(UsecodeDisassembler().disassemble_class(d, 0))
PY
```

Any `call 0000h` in a class that did not mean to call class 0 is this bug.
