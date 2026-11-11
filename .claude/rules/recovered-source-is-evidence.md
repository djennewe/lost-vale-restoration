---
paths:
  - "shared/data/lv-usecode/**"
  - "agents/usecode-compiler/src/lv-patched/**"
  - "agents/usecode-compiler/src/lv-new/**"
---

# The recovered 1994 source is read-only evidence. Patch it in `lv-patched/`.

`shared/data/lv-usecode/` is the source snapshot recovered from diskette in
February 2025. It is the only copy of this material that exists. Treat it the
way you would treat an archival document: quote it, don't correct it.

**Never edit a file under `shared/data/lv-usecode/`.** When a recovered file
needs a fix, put a patched copy in `agents/usecode-compiler/src/lv-patched/`.

## How precedence works

Four source tiers feed `build_eusecode.py`, highest first:

1. `lv-patched/` — patched copies of recovered files
2. `shared/data/lv-usecode/LOST VALE/` — the final 1994 tier
3. `shared/data/lv-usecode/UNK files/UNK/` — the dev tier
4. `agents/usecode-compiler/src/lv-new/` — files written for this restoration

Each tier skips any basename claimed by a higher one. So `lv-patched/ATLI.UNK`
suppresses both `LOST VALE/ATLI.UNK` and `UNK files/UNK/ATLI.UNK`
automatically — you do not delete or edit the originals to make a patch take
effect.

## What a patched file must be

A byte-copy of the recovered original **plus one documented minimal fix**.
Not a rewrite, not a cleanup, not an opportunistic reformat. The diff against
the recovered file should be readable in one screen and should be explainable
in a sentence.

Record what the fix is and why in the file's header comment, and add a line to
`agents/usecode-compiler/docs/lv-patched-inventory.md`.

## Compile failures that are not yours to fix

`EALOGO.UNK` (truncated block comment) and `TJORVI.UNK` (unterminated string)
fail to compile because the 1994 source is defective. Both are on
`DEV_ALLOWLIST` in `build_eusecode.py` and do not fail the build. `TJORVI` is
an early draft of `TYORVI.UNK`, which compiles fine and is the version
actually built.

Do not "fix" these to make the build cleaner. The allowlist is the record that
the defect is upstream.
