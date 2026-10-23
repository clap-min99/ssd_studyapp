"""Compile complete SystemVerilog blocks from chapters 4–5 using optional pyslang.

Run with Python 3.11+ and pyslang available in the verification environment.
This is a syntax / elaboration check, not a simulator or a timing check.
"""

from pathlib import Path
import re
import sys


def main():
    try:
        import pyslang
    except ImportError:
        raise SystemExit("Install pyslang in a verification environment to run this check.")

    folder = Path(__file__).resolve().parents[1] / "digest/content/foundations"
    compilation = pyslang.ast.Compilation()
    files = sorted(folder.glob("chapter0[45]/*.md"))
    if not files:
        raise SystemExit("No chapter 4–5 lessons found.")
    block_count = 0
    for path in files:
        blocks = re.findall(r"```systemverilog\n(.*?)```", path.read_text(encoding="utf-8"), re.S)
        if not blocks and path.parent.name == "chapter04":
            raise SystemExit(f"No complete SystemVerilog blocks in {path.name}.")
        block_count += len(blocks)
        if not blocks:
            continue
        # Match the lesson testbenches' explicit units for modules without delays.
        # Combining files also checks cross-lesson DUT and submodule references.
        code = "`timescale 1ns/1ps\n" + "\n".join(blocks)
        compilation.addSyntaxTree(pyslang.syntax.SyntaxTree.fromText(code, name=f"{path.parent.name}/{path.name}"))

    diagnostics = compilation.getAllDiagnostics()
    if diagnostics:
        print(pyslang.DiagnosticEngine.reportAll(compilation.sourceManager, diagnostics))
    errors = sum(diagnostic.isError() for diagnostic in diagnostics)
    print(f"{len(files)} lessons, {block_count} code blocks: {errors} errors, {len(diagnostics) - errors} warnings")
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
