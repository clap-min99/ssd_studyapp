"""Export the lessons' complete SystemVerilog blocks into a practice directory.

The repository Markdown remains the source of truth. No simulator is installed
or invoked by this command; select a testbench top in your simulator afterwards.
"""

import argparse
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New directory for exported practice files")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error("Choose a new output directory so existing practice edits are preserved.")
    root = Path(__file__).resolve().parents[1] / "digest/content/foundations"
    sources = []
    for path in sorted(root.glob("chapter0[45]/*.md")):
        blocks = re.findall(r"```systemverilog\n(.*?)```", path.read_text(encoding="utf-8"), re.S)
        if blocks:
            sources.append(f"// {path.parent.name}/{path.name}\n" + "\n".join(blocks))
    if not sources:
        parser.error("No SystemVerilog lesson blocks found.")
    output.mkdir(parents=True)
    (output / "lessons.sv").write_text("`timescale 1ns/1ps\n\n" + "\n\n".join(sources), encoding="utf-8")
    (output / "access_vectors.mem").write_text("00_0\n01_0\n10_0\n11_1\n", encoding="ascii")
    (output / "README.txt").write_text(
        "Run from this directory, using an installed SystemVerilog simulator.\n"
        "Example for Icarus Verilog (SystemVerilog mode):\n\n"
        "iverilog -g2012 -s tb_access -o access.vvp lessons.sv\n"
        "vvp access.vvp\n\n"
        "Other testbench tops: tb_access_file, tb_parity_control, tb_ch5_alu4, tb_ch5_shift8.\n"
        "Compile and run one top at a time. File tests require access_vectors.mem in the working directory.\n"
        "Do not synthesize the testbench modules. RTL simulation does not verify physical timing.\n",
        encoding="utf-8",
    )
    print(f"Exported {len(sources)} lesson sources to {output}")


if __name__ == "__main__":
    main()
