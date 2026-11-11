# Finding: H1 — `startup{}/process{}` compiles without its per-tick loop

Follow-up investigation of finding **H1** from
`docs/reviews/2026-07-19-adversarial-review.md`, which asked to "prove the
process-block semantics before trusting the LORDBRIT fix." This document is
that proof. It is a **written finding only** — no code change was made. The
fix is specified at the end for a future session that can pair it with an
in-game playtest.

## TL;DR

The U8 `startup { A } process { B }` construct means **"run A once, then loop
B once per game tick, yielding (`suspend`) each iteration."** Our compiler
emits `A` then `B` once, with a trailing `ret` and no loop and no yield. So
every such process runs a single iteration and dies. LORDBRIT's ghost
"puppet" sets one frame and freezes; the candle/magnet puzzle monitors and
the Zealan shield-strip monitor poll once and stop.

The 2026-07-19 empty-stub fix (which made an annotation-less `startup{}` body
emit real code instead of `init 00h; ret`) is a genuine improvement — the
puppet went from *nothing* to *one iteration* — but it did not restore the
loop, and the "byte-identical to the annotated form" reasoning does not
rescue it: the annotated form never looped either. Both forms emit the body
once.

## Evidence

### Our emission runs once (no back-edge)

`TypeLordBritish::puppet` lives at class `0x05A3` (TYPELORD) in the built
`shared/build/EUSECODE.FLX`. It is spawned exactly once, `spawn puppet(lb)`
at `LORDBRIT.UNK:57`. Disassembled, its body is `init 04h`, the `startup`
block once (init `count`/`fram`, `setFrame(0)`), then the `process` block
straight through to `075C: ret`. Every jump inside it is a **forward** `jne`
skipping a branch; there is **no backward jump**. The source's `count`
0→4 cycling and `getFrame()=8` reset only make sense across many iterations,
so the intent is a loop.

### The base game compiles these as loops with a per-tick `suspend`

Disassembling the retail `EUSECODE.FLX` (`shared/data/u8-install/`):

- **634** backward-jmp loops contain a `suspend`.
- **97** of them end in a **bare `suspend` immediately before the backward
  jump** — a `suspend` that is *not* part of a `wait()` call (no
  `spawn 0581h` in the preceding instructions). This is the per-tick yield.

Two concrete animation loops:

- `0044 DOOR_NS` `[0565..059A]` — a door slide:
  `.loop(0565): suspend` → push counter, `jne` exit-when-0 → `counter--` →
  `pos += delta` → `setFrame(pos)` → `spawn wait + suspend` → `suspend` →
  `jmp 0565`. The loop *begins* by suspending.
- `003B LITZAPEW` `[01E0..0210]` — a frame stepper:
  `while var<=5 { setFrame(var); wait(7); var++ }` compiled as
  `setFrame` → `spawn 0581 wait` → `suspend` → `var++` → `jmp` back.

So `process{}` is not linear code; it is a loop, and each iteration yields
control to the scheduler via `suspend`.

## Why a naive fix hangs the VM (the load-bearing constraint)

U8 processes are **cooperative**: a process runs until it `suspend`s or
`ret`s. A `process{}` loop with a back-edge but *no* yield is a tight
infinite loop that never returns control — it freezes the game.

The seven shipping functions that use `startup{}/process{}` split exactly on
whether they contain an explicit `wait()`:

| Class::function | explicit `wait()` | bare `jmp` loop | loop + implicit `suspend` |
|---|---|---|---|
| TypeLordBritish::puppet | yes | ok | correct |
| EggShades::squabble | yes | ok | correct |
| TypePotion::protection | yes | ok | correct |
| TypePotion::invisible | yes | ok | correct |
| EggCandleTrick::hatch | **no** | **HANG** | correct (polls per tick) |
| EggMagnet::hatch | no (early `return`) | risky | correct |
| TypeAOFrizbee::shieldMonitor | **no** | **HANG** | correct (paces per tick) |

`shieldMonitor` is the clearest case: its process body is `if c = 100 { strip
all Avatar equipment } c++`. Without a yield, `c` races 0→100 in a single
tick and the loop spins forever. With the implicit per-tick `suspend`, `c`
advances one per tick and the strip fires every 100 ticks — which is why the
recovered 1994 source has no explicit `wait` there. The yield is the
compiler's job, not the source's.

This is also why the fix cannot be "wrap `process{}` in `jmp .loop`": that
form freezes the candle puzzle, the magnet puzzle, and the shield monitor.
The implicit `suspend` is mandatory and it is what makes the transform safe
for all seven at once (every iteration yields, so none can be a tight loop).

## Specified fix (not yet applied)

1. Parser/AST: restore the `startup_block` / `process_block` distinction that
   the 2026-07-19 empty-stub fix collapsed. (The current statement-path
   handling emits both blocks linearly.)
2. Codegen for a function composed of `startup{ A }` and/or `process{ B }`:
   ```
   A                     ; startup body, once (may be empty)
   .loop:
     suspend             ; implicit per-tick yield  <-- the missing piece
     B                   ; process body
     jmp .loop
   ```
   `suspend` at the loop top matches DOOR_NS. Only-`startup` (no `process`)
   emits `A` and no loop; only-`process` emits the loop alone.
3. Exits remain the source's own `return`s and the loop-condition `jne`s
   inside `B`; explicit `wait()`s stay as-is and stack on top of the per-tick
   yield.

## Verification plan for whoever implements it

- Structural (headless, closes the hang risk): `test_roundtrip.py` stays
  516/516, and each of the seven functions disassembles to
  `.loop: suspend; <body>; jmp .loop` — proving no back-edge lacks a yield,
  so none is a tight loop. Compare the puppet against DOOR_NS/LITZAPEW.
- Behavioral (needs a playtest, cannot be done headlessly): the LB ghost
  actually animates at the right cadence; the candle and magnet puzzles run
  without freezing; the shield monitor strips gear on the intended interval.

Because the structural check eliminates the freeze risk by construction, the
remaining in-game step is about *timing and appearance*, not *does the game
hang*. That is the up-tier, in-game-verification class the improvement plan
(section 1, H1) flagged — hence this is held as a finding rather than shipped.

## Cross-references

- Supersedes the stale claim in `lv-patched/PLNTST.UNK:24-27` ("the compiler
  drops startup/process blocks") — review finding **L20**. PLNTST::hatch was
  rewritten to a plain body and set its flags inline precisely to dodge this
  bug, so it is unaffected by the fix above.
- Related review findings: **H1** (this), **L20**.
- Project memory: `project-u8-calling-conventions` records the empty-stub bug
  as "still open"; this finding refines it from "empty stub" to "runs once,
  needs the per-tick loop."
