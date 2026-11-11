#!/bin/bash
# Build the playtest input tools. macOS only; needs the Swift toolchain.
set -euo pipefail
cd "$(dirname "$0")"

for src in postkey postchord postmouse winid; do
    swiftc -O "$src.swift" -o "$src"
    echo "built $src"
done
chmod +x send.py shot.sh
echo "done — see README.md"
