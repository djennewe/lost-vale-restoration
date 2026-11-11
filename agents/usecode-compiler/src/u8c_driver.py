#!/usr/bin/env python3
"""
u8c_driver.py — Compilation driver for the U8 usecode compiler.

Orchestrates the full pipeline:
  .UNK source -> lexer -> parser -> symbols -> codegen -> assembler -> bytecode

Usage:
    python3 u8c_driver.py <source.unk>           # compile single file
    python3 u8c_driver.py --all <dir>             # compile all files in dir
    python3 u8c_driver.py --build <output.flx>    # build final EUSECODE.FLX
"""

import sys
import os
import glob
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from u8c_lexer import tokenize
from u8c_parser import parse_file, parse_source
from u8c_symbols import SymbolTable, create_symbol_table
from u8c_codegen import CodeGenerator

# Path resolution: relative to this file (repo root three levels up), same
# convention as lv_manifest.py — so a worktree checkout reads its own
# shared/data/, never the main checkout's.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, '..', '..', '..'))


class CompilationResult:
    """Result of compiling a single .UNK file."""

    def __init__(self, filename):
        self.filename = filename
        self.class_name = ''
        self.class_id = None
        self.bytecode = None
        self.errors = []
        self.warnings = []
        self.success = False
        # Recovered (non-fatal) parse errors: each one is a DROPPED
        # statement. success=True with parse_errors non-empty is a
        # partial compile — the build's ratchet gate bounds these.
        self.parse_errors = []

    def __repr__(self):
        status = 'OK' if self.success else 'FAIL'
        size = len(self.bytecode) if self.bytecode else 0
        return f"CompilationResult({self.filename}: {status}, {size} bytes)"


class Driver:
    """Compilation driver."""

    def __init__(self, symbols=None, flx_path=None):
        """Create a compilation driver.

        Args:
            symbols: pre-built SymbolTable, or None to create default
            flx_path: path to base EUSECODE.FLX for class name resolution
        """
        self.symbols = symbols or create_symbol_table(flx_path=flx_path)
        self.results = {}  # filename -> CompilationResult

    def compile_file(self, path, verbose=False, class_name_override=None):
        """Compile a single .UNK source file.

        Args:
            path: path to the .UNK file
            verbose: print progress
            class_name_override: optional class name to compile a
                headerless (no `class` declaration) file under — passed
                through to CodeGenerator (see its __init__ docstring) and
                recorded as result.class_name so downstream id assignment
                treats the file as that class (build_eusecode.py compiles
                FREE.UNK as 'LVFREE' this way). Ignored when the source
                declares its own class.

        Returns:
            CompilationResult
        """
        result = CompilationResult(path)

        try:
            if verbose:
                print(f"  Compiling: {os.path.basename(path)}")

            # Parse
            ast = parse_file(path)
            result.parse_errors = list(getattr(ast, 'parse_errors', []))

            # Get class info
            if ast.class_decl:
                result.class_name = ast.class_decl.name
                result.class_id = self.symbols.get_class_id(result.class_name)
            elif class_name_override:
                result.class_name = class_name_override
                result.class_id = self.symbols.get_class_id(class_name_override)

            # Register global flags
            for gf in ast.globalflags:
                self.symbols.allocate_global_flag(gf.name, gf.bits)

            # Generate bytecode
            codegen = CodeGenerator(self.symbols, filename=os.path.basename(path),
                                    class_name_override=class_name_override)
            result.bytecode = codegen.generate_class(ast)
            result.warnings = codegen.warnings
            result.success = True

            if verbose:
                size = len(result.bytecode) if result.bytecode else 0
                cid = f"0x{result.class_id:04X}" if result.class_id is not None else "???"
                print(f"    -> {result.class_name} (ID {cid}): {size} bytes")

        except Exception as e:
            result.errors.append(str(e))
            if verbose:
                print(f"    ERROR: {e}")

        self.results[path] = result
        return result

    def compile_directory(self, dir_path, verbose=False):
        """Compile all .UNK files in a directory.

        Returns:
            list of CompilationResult
        """
        results = []
        for path in sorted(glob.glob(os.path.join(dir_path, '*.UNK'))):
            result = self.compile_file(path, verbose=verbose)
            results.append(result)
        return results

    def compile_all_lv(self, verbose=False):
        """Compile all Lost Vale source files.

        Returns:
            list of CompilationResult
        """
        base = os.path.join(REPO_ROOT, 'shared', 'data', 'lv-usecode')
        dirs = [
            os.path.join(base, 'LOST VALE'),
            os.path.join(base, 'UNK files', 'UNK'),
        ]

        results = []
        for d in dirs:
            if os.path.isdir(d):
                if verbose:
                    print(f"\nCompiling {d}/:")
                results.extend(self.compile_directory(d, verbose=verbose))

        return results

    def build_flx(self, output_path, base_flx_path=None, verbose=False):
        """Build a complete EUSECODE.FLX from compiled classes.

        Args:
            output_path: path for the output FLX file
            base_flx_path: path to base game EUSECODE.FLX (to merge with)
            verbose: print progress
        """
        from u8_flex import UsecodeFlexArchive
        from u8_flx_packer import UsecodeFlxPacker

        if base_flx_path:
            reader = UsecodeFlexArchive(base_flx_path)
            packer = UsecodeFlxPacker.from_existing(reader)
        else:
            packer = UsecodeFlxPacker()

        replaced = 0
        added = 0

        for path, result in self.results.items():
            if not result.success or not result.bytecode:
                continue

            if result.class_id is not None:
                # Replace existing class
                packer.replace_class(result.class_id, result.bytecode,
                                    result.class_name)
                replaced += 1
                if verbose:
                    print(f"  Replaced class 0x{result.class_id:04X} ({result.class_name})")
            else:
                # New class — assign next available ID
                next_id = packer.class_count
                packer.add_new_class(next_id, result.bytecode, result.class_name)
                result.class_id = next_id
                added += 1
                if verbose:
                    print(f"  Added new class 0x{next_id:04X} ({result.class_name})")

        size = packer.write(output_path)
        if verbose:
            print(f"\nWrote {output_path}: {size} bytes")
            print(f"  Replaced: {replaced} classes, Added: {added} classes")

        return size

    def print_report(self):
        """Print compilation report."""
        total = len(self.results)
        ok = sum(1 for r in self.results.values() if r.success)
        fail = total - ok
        total_bytes = sum(len(r.bytecode) for r in self.results.values()
                         if r.success and r.bytecode)
        total_warnings = sum(len(r.warnings) for r in self.results.values())

        print(f"\n{'='*60}")
        print(f"Compilation Report")
        print(f"{'='*60}")
        print(f"  Files compiled: {total}")
        print(f"  Successful:     {ok}")
        print(f"  Failed:         {fail}")
        print(f"  Total bytecode: {total_bytes} bytes")
        print(f"  Warnings:       {total_warnings}")

        if fail > 0:
            print(f"\nFailures:")
            for path, result in self.results.items():
                if not result.success:
                    name = os.path.basename(path)
                    err = result.errors[0] if result.errors else 'unknown'
                    print(f"  {name}: {err[:80]}")

        if total_warnings > 0:
            print(f"\nWarnings by file:")
            for path, result in self.results.items():
                if result.warnings:
                    name = os.path.basename(path)
                    print(f"  {name}: {len(result.warnings)} warning(s)")

        print(f"{'='*60}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='U8 Usecode Compiler')
    parser.add_argument('input', nargs='?', help='.UNK source file or directory')
    parser.add_argument('--all', action='store_true', help='Compile all LV files')
    parser.add_argument('--build', metavar='OUTPUT', help='Build EUSECODE.FLX')
    parser.add_argument('--base', metavar='FLX', help='Base game EUSECODE.FLX',
                       default=os.path.join(REPO_ROOT, 'shared', 'data', 'USECODE.FLX'))
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--hex', action='store_true', help='Dump hex output')

    args = parser.parse_args()

    driver = Driver(flx_path=args.base)

    if args.all:
        driver.compile_all_lv(verbose=args.verbose)
        driver.print_report()
    elif args.build:
        driver.compile_all_lv(verbose=args.verbose)
        driver.build_flx(args.build, base_flx_path=args.base, verbose=args.verbose)
        driver.print_report()
    elif args.input:
        if os.path.isdir(args.input):
            driver.compile_directory(args.input, verbose=True)
        else:
            result = driver.compile_file(args.input, verbose=True)
            if result.success and args.hex:
                data = result.bytecode
                for off in range(0, len(data), 16):
                    hexb = ' '.join(f'{data[i]:02X}'
                                   for i in range(off, min(off + 16, len(data))))
                    print(f"  {off:04X}: {hexb}")
        driver.print_report()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
