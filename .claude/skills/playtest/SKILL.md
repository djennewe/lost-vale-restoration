---
name: playtest
description: Run Lost Vale in-engine on a private X display and produce a playtest report. Use when a fix needs verifying in the actual game rather than in tests — quest steps, teleports, dialogue, terrain, climbability — or when the user asks for an in-game test, a repro, or a retest.
---

Verify in the engine. The test estate proves the toolchain encodes correctly;
it cannot tell you the Avatar drowned, a gate was climbable, or a menu option
was dead. Every one of those was found by playing.

Harness: `tools/playtest-linux/` (Linux). `tools/playtest/` is the macOS
harness — different mechanism, don't mix them.

**Read the header comment of `tools/playtest-linux/session.sh` before your
first command in a session.** It documents the verbs and the traps, and it is
more current than this file.

## Two rules that decide whether the results mean anything

**Navigate menus organically.** Do not drive conversations by matching answer
strings. The simulator missed real defects for exactly this reason — the game
offers different, often *dead*, look-alike options, and forcing a pick walks
past the bug you are looking for. Pick from what is actually on screen.

**A debug teleport is not a player arrival.** `justTeleported` suppresses
teleport-egg hatches, so warping onto a pad proves nothing about whether the
pad works (finding F1, 2026-07-31). Walk in for anything egg-triggered.

## Running a session

```bash
tools/playtest-linux/session.sh start     # Xvfb + ScummVM, skips the intro
tools/playtest-linux/session.sh status
tools/playtest-linux/session.sh stop
```

Drive it with `walk` / `key` / `type` / `dbg`, and `nav.py x,y x,y ...` to
follow world waypoints. `dbg` leaves the console attached, and **attached
means paused** — `resume` before expecting the world to move.

Screenshot early. Four unrelated failure modes all look identical to "input is
not reaching the game", and a screenshot separates them in one step.

**Read `traps.md` in this skill directory before a session that involves item
pickup, the Sacred Circle ceremony, locked doors, or the debugger.** Every
trap in it cost real session time at least once — the pickup recipe and the
`dbg`-not-`cmd` rule especially.

## Reporting

Two artifacts, named for the same day and topic:

- `docs/playtest-YYYY-MM-DD-<topic>.md` — the report
- `docs/playtest-YYYY-MM-DD-<topic>/` — screenshots, named by test ID
  (`A1-...png`, `B2-...png`) so a claim in the report points at its evidence

Structure the report the way the existing ones do — `docs/playtest-2026-07-31-retest-hardened-gates.md` is the model:

1. **Verdicts** up top. One line per test, PASS / FAIL / PARTIAL / NOT
   DEMONSTRATED. A reader should get the outcome without scrolling.
2. **One section per test**, with the verdict in the heading. Include the
   negative controls — an adversarial attempt that was correctly refused is
   what makes a PASS mean something.
3. **Findings that were not part of the plan**, numbered separately. These
   are usually the valuable half.
4. **Harness anomalies** — what misbehaved in the tooling, not the game.
5. **Disk changes** — what the session wrote, so the next reader knows what
   state they inherit.

Say NOT DEMONSTRATED when you could not test something. A PARTIAL that names
what went untested is worth more than a PASS that quietly covered less than it
claims.

## After

Update `TODO.md` with the verification note — date plus what was actually run
in ScummVM. A checkbox flips only with one.
