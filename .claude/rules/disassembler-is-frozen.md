---
paths:
  - "agents/usecode-disasm/**"
---

# The disassembler is the reference implementation. Do not modify it.

`u8_usecode_disasm.py` is what the assembler round-trips against
(`test_roundtrip.py`, `test_encoder.py`). Any change to how it decodes
bytecode or renders a listing invalidates that check — and that check is the
only thing proving the assembler encodes correctly. Change the disassembler
and you have not broken a test, you have deleted the evidence.

The 258 intrinsic signatures in `U8_INTRINSICS` are part of this. They are the
source of truth cited elsewhere in the project.

If a disassembler change looks necessary, the fix almost always belongs in the
assembler or the codegen instead. Say what you want to change and why before
touching this file.

## The one documented exception (2026-07-25, H3)

`disassemble_class_summary()` only. A `spawn_inline` key was added there to
record `0x58` edges, which the tally had no branch for.

This was safe on inspection, not on assertion:

- That method has exactly two consumers — the disassembler's own `summary`
  CLI command, and `u8_flag_graph.py`.
- The round-trip and encoder paths both use `disassemble_class()`, the
  listing path. The summary layer cannot affect round-trip byte-identity.
- The change was purely additive: no existing key's contents changed.
- Both round-trip tests were re-run and were unchanged.

**The exception is scoped to that one method.** Decoding, listing format,
`U8_INTRINSICS`, and everything else remain do-not-modify. A future gap in the
summary layer may follow this precedent; a gap anywhere else may not.

If you extend the exception, re-run both round-trip tests and record the
result here the way the H3 entry above does.

## Also in this directory

`u8_flex.py` is canonical here. Other agents hold copies in their own `src/`.
If you change it, the copies drift — check
`grep -rl "u8_flex" agents/*/src/` before assuming your change is local.
