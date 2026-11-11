---
name: artifact-rehash
description: Deliberately change a build artifact and propagate the new hash. Use when a builder change, new content, or a new custom shape means EUSECODE.FLX / FIXED.DAT / U8SHAPES.FLX / TYPEFLAG.DAT / ANIM.DAT should legitimately differ from the canonical hashes in ARTIFACTS.sha256 — and the ScummVM detection entry has to follow.
---

An artifact hash change cascades. `ARTIFACTS.sha256` pins the bytes, and
the ScummVM detection entry matches on EUSECODE's md5-5000 window and size
to detect the expansion at all. The binary, the install, the playtest
harness and `map_pins.json` all have to follow. `tools/integrate.sh` runs
that cascade. This skill is about the decision to record. The `/integrate`
skill covers the mechanics.

Do this only for a change you *intended*. A verify failure you did not expect
is not a rehash — it means a builder changed behaviour, or your game data is a
different GOG revision than the canonical hashes were recorded against. Find
out which before recording anything.

## Steps

1. **Confirm the current state is clean first.** Run
   `tools/build_artifacts.sh --verify`. If it already fails before your
   change, stop — you are not rehashing, you are debugging.

2. **Make the change** (builder fix, new content, new injected shape).

3. **Rebuild, record and cascade**: `tools/integrate.sh --record`. It runs
   `tools/build_artifacts.sh --record` (build order is load-bearing; never
   run the builders by hand), then the pins, the engine (detection values
   are computed from the FLX, so nothing is edited by hand), the install, the
   harness and the estate. It stops at the first failure. See
   `/integrate` for each step and its failure modes.

4. **Read the `ARTIFACTS.sha256` diff.** It is the record of the decision.
   Exactly the artifacts you expected to move should have moved. If an
   artifact you did not touch changed, find out why before continuing.

5. **Verify twice**: `tools/integrate.sh` (no `--record`). A second build must
   reproduce the same hashes, and the run must be a no-op that passes.
   Non-reproducibility is a bug, not a quirk.

6. **Launch it**: `./install_lv.sh --run`. A detection-entry mistake shows up
   here as the expansion simply not being offered.

## Before committing

The artifacts themselves are gitignored and must stay that way. What you
commit is `ARTIFACTS.sha256`, whatever the summary lists under "to commit",
and whatever source drove the change. Never commit a `.DAT`, `.FLX`,
`.staging`, or `.failed`.

If the change touched savegame-visible IDs, stop and re-read
`.claude/rules/build-artifacts.md`. Pinned class IDs and flag bits are frozen
forever; a rehash is not permission to renumber one.
