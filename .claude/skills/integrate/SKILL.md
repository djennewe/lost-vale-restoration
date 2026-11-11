---
name: integrate
description: Run the whole integration cascade with one command, tools/integrate.sh. Use after any merge or commit that touches usecode, maps, custom art, build artifacts, or the ScummVM fork, before a playtest or a verifier hand-off, and whenever the installed game, the playtest harness or the scummvm-lv binary might be behind shared/build.
---

After a merge that moves an artifact, seven things have to follow it, in
order. They used to be run by hand about ten times a session, and each one
drifted at least once: the detection values in `build_scummvm.sh` went
stale for weeks, an existing `scummvm-lv/` was recompiled without a newer
engine patch, the patch fell behind the fork, and the playtest harness ran
yesterday's bytes. `tools/integrate.sh` runs all of it, checks each step, and
stops at the first failure.

```bash
tools/integrate.sh                # verify: rebuild, must match ARTIFACTS.sha256
tools/integrate.sh --record       # a DELIBERATE artifact change (/artifact-rehash)
tools/integrate.sh --fork         # the fork gained a commit: regenerate the patch first
tools/integrate.sh --no-engine    # skip build_scummvm.sh
tools/integrate.sh --no-install   # skip install_lv.sh
tools/integrate.sh --force        # run the steps a live game would block
```

It is idempotent. Run it again after it passes: the second run changes no
file content and passes. That second run is also the reproducibility check
— a rebuild that does not reproduce the same hashes fails it.

## The steps

0. **preflight**: refuses at once if a running game would be affected
   (see "Playtests in flight").
1. **patch** — `tools/scummvm-patches/0001-lost-vale-engine.patch` must equal
   `git diff <base> HEAD -- engines/ ':!engines/ultima/detection_tables.h'`
   in `scummvm-lv-console/` (`test_scummvm_patch_sync.py`). `--fork`
   rewrites the patch from the fork first. No fork in this checkout (a
   worktree): not checked, and the summary says so.
2. **build** — `tools/build_artifacts.sh` rebuilds all five artifacts in
   their load-bearing order and verifies them against `ARTIFACTS.sha256`;
   `--record` rewrites that file instead.
3. **pins** — `derive_map_pins.py` regenerates `map_pins.json` from
   FIXED.DAT. A run whose only change is the file's `generated` date keeps
   the old file.
4. **engine** — `./build_scummvm.sh`. It computes md5-5000 and size from
   `shared/build/EUSECODE.FLX` (`tools/lv_scummvm.py values`; nothing in the
   script is hand-edited any more), re-syncs an existing `scummvm-lv/` to
   base + the current patch by rewriting exactly the files that differ,
   writes the detection entry, and runs make. Afterwards the script checks
   the tree is base + patch and the entry carries the FLX's values.
5. **install** — `./install_lv.sh`, then every installed file is compared
   with `ARTIFACTS.sha256`.
6. **harness** — copies the artifacts that differ into
   `shared/u8-lv-patched` (the dir `session.sh` runs: `USECODE/EUSECODE.FLX`,
   `STATIC/U8SHAPES.FLX`, `STATIC/TYPEFLAG.DAT`, `STATIC/ANIM.DAT`, and
   FIXED.DAT both at the top level and in `STATIC/`), then compares all six.
   It also copies the installed `u8monsters.ini` (install_lv.sh's engine
   rows plus the LV monsters 872/873), so harness monsters keep their
   stats. Absent: skipped.
7. **estate** — `tools/run_all_tests.sh`. `test_integration_state.py`
   re-checks steps 4-6 offline: the detection entry matches shared/build,
   the tree is base + patch, the binary is newer than its sources, and the
   harness and install hold the canonical bytes.

The summary prints the five artifact hashes, md5-5000 and size, each step's
result, and the tracked files the run changed (`ARTIFACTS.sha256`,
`lv_manifest.json`, `map_pins.json`, the patch). Commit those. Full logs per
step are kept in the `logs` dir it names.

## Failure modes

| Stops at | Means | Fix |
|---|---|---|
| patch | The fork has a commit the patch lacks. | `--fork`, then commit the patch. |
| build | The rebuilt bytes differ from `ARTIFACTS.sha256`. | Intended change: `--record` and review the diff (`/artifact-rehash`). Not intended: a builder changed behaviour. That is the finding, so don't record over it. |
| pins | `derive_map_pins.py` crashed. | Read `pins.log`. It usually means FIXED.DAT is missing. |
| engine: "is a fork ... does not equal" | `LV_SCUMMVM_DIR` points at the fork, and the fork's commits are not in the patch. | `--fork`. A fork tree is never rewritten. |
| engine: "does not contain the pinned base" / "not a git checkout" | The tree was cloned from another upstream commit. | `./build_scummvm.sh --clean`, then rerun. |
| engine: "does not apply to base" | The patch no longer applies to the pin. | Regenerate it against the pin (`tools/scummvm-patches/README.md`). |
| engine: make error | A compile error, often from the patch just synced. | Read `engine.log`. Fix it in the fork, then `--fork`. |
| install / harness: "bytes differ" | A copy failed, or the target is read-only. | Read the step log. |
| preflight (or a later step): "a running game uses ..." | A live game runs this binary or has this game dir open. See below. | Wait, or pin a copy. `--force` overrides. |
| estate | A test failed. | Read `estate.log`. The run stops there and does not claim green. |

## Playtests in flight

A playtest that restarts ScummVM picks up whatever binary and game dir are
on disk at that moment. A new binary whose detection entry has moved, or new
bytes under a session that was started on old ones, breaks the run, and it
looks like a regression. So a **preflight** lists every running `scummvm`
(pid, binary, game dir, command line). It **refuses** the run while a
process runs this tree's binary (`/proc/PID/exe`) and the engine step is
on. It also refuses while a process has the install or harness dir open
(`-p`/`--path`, resolved against the process's cwd) and that step is on.
The refusal comes before the five-minute build, and each step checks
again in case a session started meanwhile.

- A verifier that needs a stable build should run a **pinned copy**: the
  binary and the game dir copied somewhere else. A pinned copy blocks
  nothing, and integrating under it is safe.
- If the session is yours and you mean to restart it, `--force`, then
  `session.sh stop`/`start`.
- `--no-engine --no-install` still syncs the harness. A running session on
  `shared/u8-lv-patched` blocks that step too.

## Still manual

- Committing what the summary lists under "to commit".
- Restarting a running playtest session after the harness changed.
- `scummvm-lv-console/` as a *build* (`LV_SCUMMVM_DIR=$PWD/scummvm-lv-console
  tools/integrate.sh`). Its detection entry is only written when you build
  it this way: `build_eusecode.py` updates only `scummvm-lv/`.
