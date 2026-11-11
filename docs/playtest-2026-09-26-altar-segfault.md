# The altar segfault is SFX 0: RUMBLE1 compiled as push 0 (2026-09-26)

**Cause found and fix verified.** AOSCENE's `spawn safePlaySFX(RUMBLE1, 255)`
names a sample that does not exist. The compiler warned
(`AOSCENE.UNK:63: unknown identifier 'RUMBLE1' compiled as push 0`) and
emitted `playSFX(0, 255)`. SOUND.FLX entry 0 is the 1,760-byte table of
8-byte sample names ("ARMHIT1AAROWFYR1..."), and the engine decodes it as
Sonarc audio: `audio_decode` takes its frame size from the first two name
bytes ("AR" = 21057) and runs a checksum loop over 21,057 bytes of a
1,760-byte heap buffer, 19,297 bytes past the end. Whether that read
crosses into an unmapped page depends on the heap layout, which is why the
shipped binary died one hatch in three and survived under gdb.

The fix is one token in `lv-new/AOSCENE.UNK`: `RUMBLE1` becomes `QUAKE3`
(sample 49), the rumble the 1994 sources use (three sites in
`shared/data/lv-usecode/`). It changes one byte of EUSECODE.FLX. Confidence:
high. Under AddressSanitizer the unfixed scene faulted 3 of 3 hatches at
12 to 13 s; the fixed build ran 3 of 3 hatches to "It is done..." with no
report, and `godsFree` read 1 after the last.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| S1 | Shipped binary under gdb, cp34, one hatch (loop run g1) | scene completed, no SIGSEGV | no repro (as on 2026-09-26 R1, R2) |
| S2 | ASan build of the same source, cp34, unfixed EUSECODE | heap-buffer-overflow in `SonarcAudioSample::audio_decode`, 3 of 3 hatches (runs a1, u2, u3), at +12.1, +13.3, +12.2 s | **REPRODUCED** |
| S3 | Shipped binary under gdb, breakpoint on `playSFX` with `sfxNum == 0` (run b3) | hit once, from the AOSCENE spawn; decoder handed `size` 21057 for a `_bufferSize` of 1760 | **CONFIRMED on the shipped binary** |
| S4 | ASan build, EUSECODE with the `QUAKE3` fix | 3 of 3 hatches (f2, f3, f4) reach "It is done. The Ancient Ones are free..." with zero ASan reports; `godsFree` = 1 | **PASS** |

A fourth fixed run (f1) never hatched: the harness console would not open
after the fresh start, so the run did no walk. It is excluded from the
counts above.

## Backtrace

ASan, run a1 (`docs/playtest-2026-09-26-altar-segfault/asan-report-run1.txt`),
resolved with `addr2line` against the ASan binary. Paths are under
`engines/ultima/ultima8/`:

    READ of size 1, 0 bytes after a 1760-byte region
    #0 SonarcAudioSample::audio_decode        audio/sonarc_audio_sample.cpp:178
    #1 SonarcAudioSample::decompressFrame     audio/sonarc_audio_sample.cpp:213
    #2 SonarcAudioSample::makeStream          audio/sonarc_audio_sample.cpp:232
    #3 AudioChannel::playSample               audio/audio_channel.cpp:46
    #4 AudioMixer::playSample                 audio/audio_mixer.cpp:100
    #5 AudioProcess::playSample               audio/audio_process.cpp:212
    #6 AudioProcess::playSFX                  audio/audio_process.cpp:263
    #8 AudioProcess::I_playSFX                audio/audio_process.cpp:479
    #9 UCMachine::execProcess                 usecode/uc_machine.cpp:399   (safePlaySFX's calli 00ED)
    #11 Kernel::addProcessExec                kernel/kernel.cpp:136
    #12 UCMachine::execProcess                usecode/uc_machine.cpp:1387  (AOSCENE's spawn)
    #14 Kernel::runProcesses                  kernel/kernel.cpp:166

    allocated by: FlexFile::getObject (filesys/flex_file.cpp:112)
      <- SoundFlex::cache (audio/sound_flex.cpp:94)
      <- SoundFlex::getSample (audio/sound_flex.cpp:78)
      <- AudioProcess::playSFX (audio/audio_process.cpp:256)

Line 178 is the checksum loop, `for (int i = 0; i < size / 2; ++i)`, with
`size` read at line 175 from the buffer's own first two bytes.

The same path on the shipped `scummvm-lv/scummvm` (gdb, run b3,
`gdb-sfx0-shipped-binary.txt`):

    AudioProcess::playSFX (sfxNum=0, priority=255, objId=0, ...) at audio_process.cpp:256
    ...
    SonarcAudioSample::audio_decode (source="ARMRHIT4LTNING1ATELEPORT...") at sonarc_audio_sample.cpp:176
    size = 21057, _bufferSize = 1760, _frameSize = 21069, _length = 1213026881

That run did not fault. The over-read happened and landed on mapped memory.

## Evidence chain

1. **Source.** `lv-new/AOSCENE.UNK:63` (before the fix):
   `spawn safePlaySFX(RUMBLE1, 255) -> return;`. `RUMBLE1` is absent from
   `SND_CONSTANTS` (`u8c_symbols.py:484` onward, the 220 names regenerated
   from SOUND.FLX entry 0). No file in `shared/data/lv-usecode/` uses the
   name; AOSCENE is a 2026 file.
2. **Compiler.** A temp-path build (`build_eusecode.build(output_path=...)`,
   byte-identical to `shared/build/EUSECODE.FLX`) logs
   `WARN AOSCENE.UNK:63: unknown identifier 'RUMBLE1' compiled as push 0`
   (`u8c_codegen.py:2405-2408`).
3. **Bytecode.** Class 05A7 EGGAOCER, offset 0241:
   `push 00FFh; push byte +0; push dword 0; spawn 04h 00h 05AEh 0C65h`,
   the LVFREE `safePlaySFX(soundNum, priority)` body at 05AE:0C65, which
   calls `playSFX` (intrinsic 00ED) and loops on `isSFXPlaying`. The
   MAGIC3 spawn at 019D pushes 3Ah (58), correct. A scan of every class in
   EUSECODE.FLX for `playSFX` or LVFREE `safePlaySFX` with a literal 0
   sound finds this one site and no other.
4. **Data.** SOUND.FLX entry 0: 1,760 bytes, 220 names of 8 bytes; its
   first two bytes are `41 52` ("AR"), so the decoder's frame size is
   21,057.
5. **Engine.** `SoundFlex::getSample` (`sound_flex.cpp:75-80`) rejects only
   `index >= _count`. `cache()` (`sound_flex.cpp:98-107`) sends anything
   without an "ASFX" tag to `SonarcAudioSample`, so entry 0 in U8 becomes
   a sample built on the name table. Nothing in the decoder checks a
   frame's size against the buffer.
6. **Timing.** The spawn runs after `wait(30)`, the first bark, and
   `wait(120)`; ASan fired 12.1 to 13.3 s after the hatch, and the
   2026-09-26 crash landed 8 to 10 s after the hatch "before the white
   fade", which is the next statement (`FadeToWhite()`).

The 2026-09-25 method-frame change (`2f27d51`) is not involved. The hatch
is an event, so its frame did not move, and the faulting spawn reads no
`this`. The 2026-09-05 record's unreproduced AOSCENE segfault fits the same
cause: `RUMBLE1` has been in the file since it was added (`928ab4b`,
21 March 2026).

## The fix

Applied in the working tree; uncommitted:

    -	spawn safePlaySFX(RUMBLE1, 255) -> return;
    +	spawn safePlaySFX(QUAKE3, 255) -> return;

(with a comment above it pointing here). The temp-path build differs from
`shared/build/EUSECODE.FLX` in one byte, offset 1479826, 00 to 31h. The
size (1,505,327) and the first 5,000 bytes are unchanged, so the ScummVM
detection entry does not move; `ARTIFACTS.sha256` does, and
`shared/build/` was not rebuilt. The canonical rebuild and rehash is
`/artifact-rehash`.

Timing changes slightly: `-> return` makes the hatch wait for QUAKE3
(24,150 bytes of Sonarc) to finish before `FadeToWhite()`. In all three
fixed runs the scene still reached its final bark inside 45 s
(`F1`-`F3-fixed-it-is-done.png`).

## Hardening beyond the minimal fix (unapplied)

- **Engine.** In U8, `SoundFlex::getSample(0)` should return `nullptr`
  (`sound_flex.cpp:76`), because entry 0 is the name table for every U8
  SOUND.FLX. `audio_decode` could also refuse a frame whose `size`
  exceeds the bytes left in the buffer. Either one turns this class of
  bug into silence. Both are fork changes, so the patch would need
  regenerating per CLAUDE.md.
- **Compiler.** An unknown all-caps identifier passed as a sound argument
  compiles to `push 0`, and SFX 0 crashes the engine. Making
  `unknown identifier` fatal for SFX arguments (or for all-caps
  identifiers generally) would have stopped this at build time.

## Method

Checkpoint `~/lv-checkpoints/cp34-altar-ready-head-20260926.sav`, copied
over `ultima8.001` and loaded with `Ultima8Engine::loadGame 1`; the Avatar
walked (3400, 7696) to (3440, 8580), (3268, 8580), and north-west into the
egg's box (12752 at (3072, 8320, 24), range 6, 6); `event 7 @ 05A7:0080`
marked the hatch. Console use: `debugflag_enable Object`,
`ObjectManager::objectInfo`, `UCMachine::getGlobal`. No cheats, no writes.

The ASan binary was a copy of `scummvm-lv/` configured with
`--disable-all-engines --enable-engine=ultima --disable-gtk --enable-asan`
(about five minutes at `make -j8`), run with
`ASAN_OPTIONS=detect_leaks=0:alloc_dealloc_mismatch=0`. The second option
silences upstream `new[]`/`free` mismatches in `World::loadNonFixed` that
fire at every start. The fixed runs used a scratch copy of
`shared/u8-lv-patched/` with the temp-built EUSECODE.FLX, so
`shared/u8-lv-patched/` and `shared/build/` were never written.

## Harness anomalies

- **`scummvm-lv/engines/ultima/detection_tables.h` no longer matches the
  binary built from it.** The header carries md5 `340c7913...` and size
  1,505,516 (modified 25 September 23:59); the binary (23:13) and
  `build_scummvm.sh` carry `aae44805...` and 1,505,327. A bare `make` in that
  tree as it stands would build a binary that does not detect the current
  EUSECODE; `./build_scummvm.sh` rewrites the entry from `LV_MD5` and
  `LV_SIZE` first (`build_scummvm.sh:188` onward). The ASan copy
  failed detection for this reason until the header was corrected in the
  copy.
- A console that will not open after a fresh start lost one run (f1), as
  the steps 15-18 record also saw.

## Disk changes

- `agents/usecode-compiler/src/lv-new/AOSCENE.UNK`: the one-token fix and
  its comment (uncommitted).
- `docs/playtest-2026-09-26-altar-segfault.md` and its directory: the ASan
  report, the gdb excerpt, and three end-of-scene plates from the fixed
  runs.
- `shared/build/` unchanged (`sha256sum -c` against a pre-session copy:
  all four OK). `shared/u8-lv-patched/` unchanged.
- `~/.local/share/scummvm/saves/ultima8.000` to `.009` restored from copies
  taken first (`.000` md5 `3e7dc241...`, `.001` `083de199...`);
  `timestamps` and `scummvm-history.txt` there were rewritten by the
  engine. `~/.config/scummvm/scummvm.ini` restored (md5 `a143fa3b...`).
- The ASan build tree (1.2 GB, `scummvm-lv-asan/`) was deleted after use.
  The session is stopped.
