Build, install, and launch Lost Vale in ScummVM.

Steps:

1. Build all five artifacts and verify them against the canonical hashes:
   `tools/build_artifacts.sh`

   This is the whole build — eight steps in a load-bearing order (TYPEFLAG →
   U8SHAPES wood walls → U8SHAPES+TYPEFLAG Tiny Tar potion → Zealan gods →
   art-track static props → U8SHAPES+TYPEFLAG+ANIM.DAT Tiny Tar body →
   EUSECODE → FIXED). Running `build_eusecode.py` and `build_all_maps.py` by
   hand skips the custom-art steps and the hash verification, which is how
   injected art gets silently dropped.

2. If step 1 fails on a hash mismatch, STOP and report it. Do not pass
   `--record` to make it green. Either the change was intended — in which
   case this is the `/artifact-rehash` procedure, not this one — or a builder
   changed behaviour unexpectedly and that is the finding.

3. Rebuild ScummVM only if the binary is missing or `EUSECODE.FLX`'s
   md5-5000/size changed: `./build_scummvm.sh`. It computes both from
   `shared/build/EUSECODE.FLX` (no hand-edited constants), and it re-syncs
   an existing `scummvm-lv/` to base + the tracked engine patch before
   compiling, failing loudly on any mismatch it cannot fix.
   `tools/integrate.sh` runs steps 1-4 plus the harness sync and the
   test estate in one go (`/integrate`).

   One trap that has cost a session:
   - **`scummvm-lv-console/scummvm` is a stale binary** unless you have just
     rebuilt it. Do not pass `LV_SCUMMVM=$PWD/scummvm-lv-console/scummvm`;
     the default `scummvm-lv/scummvm` is what this script produces.

4. Install and launch: `./install_lv.sh --run`

Run each step sequentially. If a step fails, stop and report. Show the build
summary and any warnings.
