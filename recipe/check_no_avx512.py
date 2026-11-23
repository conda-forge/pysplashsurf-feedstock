"""Fail if the pysplashsurf extension contains AVX-512 instructions.

Usage: python check_no_avx512.py [path/to/extension.so]
Without an argument, checks the installed extension (without importing it).
"""
import importlib.util
import pathlib
import re
import subprocess
import sys

# zmm registers, xmm/ymm 16-31 and opmask registers k0-k7 exist only in AVX-512.
AVX512 = re.compile(r"%zmm\d|%[xy]mm(1[6-9]|2\d|3[01])\b|%k[0-7]\b")

if len(sys.argv) > 1:
    libs = [pathlib.Path(sys.argv[1])]
else:
    pkg = pathlib.Path(importlib.util.find_spec("pysplashsurf").origin).parent
    libs = sorted(pkg.glob("*.so"))
assert libs, "no extension found"

failed = False
for lib in libs:
    asm = subprocess.run(
        ["objdump", "-d", "--no-show-raw-insn", str(lib)],
        check=True, capture_output=True, text=True,
    ).stdout
    hits = [line for line in asm.splitlines() if AVX512.search(line)]
    print(f"{lib}: {len(hits)} AVX-512 instructions")
    for line in hits[:5]:
        print("  " + line.strip())
    failed = failed or bool(hits)

sys.exit(1 if failed else 0)
