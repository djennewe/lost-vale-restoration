# Notice

Copyright (C) 2026 Douglas Jennewein and contributors, except as noted below, to the
extent copyright subsists. Much of the code and some of the art were produced with AI
models under human direction; where a part carries no copyright, the licenses below
grant permission to the extent they can.

## What the licenses cover

- **Code** (Python, shell, the compiler, map builders, tests, and the ScummVM patch)
  is licensed under the GNU General Public License, version 3 or any later version.
  The full text is in `LICENSE`. The ScummVM patch in `tools/scummvm-patches/` is a
  derivative of ScummVM and is GPL-3.0-or-later for that reason as well.
  `agents/usecode-disasm/src/u8_usecode_disasm.py` derives its intrinsic table from
  the Pentagram project's `ConvertUsecodeU8.h` (GPL-2.0-or-later), copyright the
  Pentagram team.
- **Documentation** written for this project (Markdown, design notes, devlogs,
  playtest reports) is licensed under Creative Commons Attribution 4.0 International,
  https://creativecommons.org/licenses/by/4.0/. Quoted third-party text inside the
  documentation stays with its authors and is excluded.
- **New `.UNK` usecode** in `agents/usecode-compiler/src/lv-new/` is covered by the
  GPL along with the code.
- **Art made for this project** is covered by the GPL along with the code, with the
  limits that follow.

## What the licenses do not cover

These files contain or derive from material owned by Electronic Arts (Origin
Systems). They are included for preservation and so the restoration can be built.
This project claims no rights in them and grants none:

- `agents/usecode-compiler/src/lv-patched/`: 1994 usecode recovered from Sheri Graner
  Ray's work diskette, with this project's repairs. Most of it is expansion code; two
  files, `AVATAR.UNK` and `FLAGS.UNK`, are 1994 source for classes in the retail game.
  The original archive was released to the community by Dominus Dragon in 2025.
- `shared/data/lv-screenshots/`: the 1994 development screenshots.
- `shared/data/lv-1994-art/`: crops and reconstructions cut from those screenshots,
  which the build uses as art.
- `docs/images/`: in-game screenshots and animations, the 1994 screenshots, and a
  detail of Denis Loubet's box cover, shown for comparison and commentary.
- Recoloured or redrawn retail shapes (for example the Water Zombie, built from the
  ghoul's frames), and art generated with retail sprites, the 1994 screenshots, or
  Denis Loubet's box cover as references. `shared/docs/art-poc/` documents which is
  which.

The build never redistributes Ultima 8 game files. It reads your copy and writes the
merged files on your machine; `shared/build/ARTIFACTS.sha256` publishes only their
hashes.

## Trademarks

*Ultima*, *Ultima 8: Pagan*, and *The Lost Vale* are trademarks of Electronic Arts.
This is a non-commercial fan project, and it is not affiliated with or endorsed by
Electronic Arts.

## Removal requests

If you hold rights in anything here and want it removed, open an issue or contact
the maintainer through GitHub (`@djennewe`), and it will be taken down promptly.
