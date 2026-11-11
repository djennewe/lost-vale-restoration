# Round-Trip Validation Results

## Assembler Round-Trip (A2)

**Result: 516/516 classes PASS (ZERO byte differences)**

Tested against: `USECODE.FLX` (Ultima 8 base game, 1,251,108 bytes)
- 516 usecode classes disassembled and reassembled
- Every class produces byte-identical output
- Both raw-hex and operand-based encoding paths validated

### Method
For each class:
1. Read raw class data from EUSECODE.FLX
2. Disassemble to text using `u8_usecode_disasm.py`
3. Reassemble text to binary using `u8_assembler.py`
4. Byte-compare original vs reassembled

### Bugs Found During Validation
1. **Event table regex**: `\([^)]*\)` failed on nested parens like `look()`. Fixed with `\(.*\)`.
2. **'db' substring check**: `if 'db' in stripped` accidentally matched hex bytes `64 62` (the ASCII for "db" in strings like "Goodbye"). Removed the check.

## FLX Packer Round-Trip (A3)

**Result: PASS (1,251,108 bytes, byte-identical)**

Tested: read EUSECODE.FLX -> rebuild -> byte-compare
- Header preserved (including non-zero reserved area)
- Data entry ordering preserved (original offset order)
- Name table preserved byte-for-byte
- All 516 class entries preserved
