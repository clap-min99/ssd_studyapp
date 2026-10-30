"""Check chapter 6 examples against integer models and, optionally, Clang.

Run: python scripts/check_chapter06_asm.py [--assemble]
The small instruction interpreter checks only the lesson subset, not a full ISA,
privileged execution, real timing, or a deployed application.
"""
import argparse
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "digest/content/foundations/chapter06"
MASK = 0xFFFFFFFF
ALIASES = {"zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4,
           **{f"t{i}": n for i, n in enumerate([5, 6, 7, 28, 29, 30, 31])},
           **{f"s{i}": n for i, n in enumerate([8, 9, *range(18, 28)])},
           **{f"a{i}": 10+i for i in range(8)}}
ALIASES.update({f"x{i}": i for i in range(32)})


def signed(value, width=32):
    return value - (1 << width) if value & (1 << (width-1)) else value


def blocks(filename):
    return re.findall(r"```asm\n(.*?)```", (CONTENT / filename).read_text(encoding="utf-8"), re.S)


class Machine:
    def __init__(self, source, initial=None, words=None, data=None, entry=None):
        self.reg = [0] * 32
        for name, value in (initial or {}).items():
            self.reg[ALIASES[name]] = value & MASK
        self.mem = dict(data or {})
        for address, value in (words or {}).items():
            for i in range(4):
                self.mem[address+i] = (value >> (8*i)) & 255
        self.labels, self.code = {}, []
        for raw in source.splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            if ":" in line:
                label, line = line.split(":", 1)
                self.labels[label] = 0x400 + 4*len(self.code)
                line = line.strip()
            if line:
                self.code.append(re.split(r"[\s,]+", line))
        self.pc = self.labels[entry] if entry else 0x400
        self.reads, self.writes = [], []

    def value(self, name):
        return self.reg[ALIASES[name]]

    def put(self, name, value):
        if ALIASES[name]:
            self.reg[ALIASES[name]] = value & MASK

    def run(self):
        for _ in range(10000):
            if self.pc == 0x184 or self.pc == 0x400 + 4*len(self.code):
                return self
            index = (self.pc - 0x400) // 4
            assert self.pc % 4 == 0 and 0 <= index < len(self.code), self.pc
            op, *args = self.code[index]
            next_pc = self.pc + 4
            if op in ("add", "sub"):
                d, a, b = args
                self.put(d, self.value(a) + (self.value(b) if op == "add" else -self.value(b)))
            elif op in ("addi", "slli"):
                d, a, imm = args
                n = int(imm, 0)
                self.put(d, self.value(a)+n if op == "addi" else self.value(a) << n)
            elif op in ("beq", "bge"):
                a, b, label = args
                take = self.value(a) == self.value(b) if op == "beq" else signed(self.value(a)) >= signed(self.value(b))
                if take:
                    next_pc = self.labels[label]
            elif op == "jal":
                d, label = args
                self.put(d, next_pc)
                next_pc = self.labels[label]
            elif op == "jalr":
                d, operand = args
                offset, base = re.fullmatch(r"(-?\d+)\((\w+)\)", operand).groups()
                target = (self.value(base) + int(offset)) & 0xFFFFFFFE
                self.put(d, next_pc)
                next_pc = target
            elif op in ("lw", "sw", "lbu"):
                r, operand = args
                offset, base = re.fullmatch(r"(-?\d+)\((\w+)\)", operand).groups()
                address = (self.value(base)+int(offset)) & MASK
                size = 1 if op == "lbu" else 4
                assert size == 1 or address % 4 == 0, address
                if op == "sw":
                    self.writes.append(address)
                    for i in range(size):
                        self.mem[address+i] = (self.value(r) >> (i*8)) & 255
                else:
                    self.reads.append(address)
                    # Missing bytes are a validation failure, not silently zero RAM.
                    self.put(r, sum(self.mem[address+i] << (8*i) for i in range(size)))
            else:
                raise AssertionError(f"Unsupported interpreter instruction: {op}")
            self.pc = next_pc
        raise AssertionError("Example did not terminate within 10000 instructions")


def check_execution():
    count = 0
    for filename, entry in [("10-arrays.md", None), ("30-review.md", "sum_words")]:
        source = blocks(filename)[0]
        for values in [[], [0], [4, -2, 9], [0x7FFFFFFF, 1], [MASK, 1], [5, 8, 2]]:
            initial = {"a0": 0xA00, "a1": len(values), "ra": 0x184, "sp": 0x2000,
                       **{f"s{i}": 100+i for i in range(12)}}
            words = {0xA00+4*i: value for i, value in enumerate(values)}
            machine = Machine(source, initial, words=words, entry=entry).run()
            result = "a0" if entry else "t0"
            assert machine.value(result) == sum(values) & MASK, (filename, values)
            assert machine.reads == list(words), (filename, machine.reads)
            assert machine.writes == []
            assert machine.value("sp") == 0x2000
            assert all(machine.value(f"s{i}") == 100+i for i in range(12))
            count += 1
    for n in range(12):
        machine = Machine(blocks("15-recursion.md")[0], {"a0": n, "ra": 0x184, "sp": 0x3000}, entry="sum_down").run()
        assert machine.value("a0") == n*(n+1)//2
        assert machine.value("sp") == 0x3000
        assert machine.value("ra") == 0x184
        assert min(machine.writes) == 0x3000 - 16*(n+1) + 8
        count += 1
    for n in [0, 1, 7, 123, MASK]:
        machine = Machine(blocks("14-nonleaf.md")[0], {"a0": n, "ra": 0x184, "sp": 0x2000}, entry="outer").run()
        assert machine.value("a0") == (3*n) & MASK
        assert machine.value("sp") == 0x2000
        assert machine.value("ra") == 0x184
        count += 1
    machine = Machine(blocks("13-stack.md")[0], {"a0": 4, "a1": 9, "s0": 77, "sp": 0x1000, "ra": 0x184}).run()
    assert machine.value("a0") == 15 and machine.value("s0") == 77 and machine.value("sp") == 0x1000
    count += 1
    machine = Machine(blocks("09-loops.md")[0]).run()
    assert machine.value("s0") == 4 and machine.value("s1") == 6
    count += 1
    for raw in [b"\0", b"OK\0", b"abcXYZ\0"]:
        machine = Machine(blocks("11-bytes-strings.md")[0], {"a0": 0x700}, data={0x700+i: v for i, v in enumerate(raw)}).run()
        assert machine.value("t1") == len(raw)-1
        assert len(machine.reads) == len(raw)
        count += 1
    print(f"PASS: {count} source-assembly execution scenarios (bounded lesson interpreter)")


def check_numbers():
    constants = [0, 1, 2047, 2048, 4095, 4096, 0x17FF, 0x1800, 0x12345678, 0x12345ABC, 0x7FFFFFFF, 0x80000000, MASK]
    for value in constants:
        upper = ((value + 0x800) >> 12) & 0xFFFFF
        lower = signed(value & 0xFFF, 12)
        assert ((upper << 12) + lower) & MASK == value
    assert signed(0xABC, 12) == -1348
    assert signed(0xFFFFFFF9) >> 1 == -4
    assert (0xFFFFFFFF * 2) >> 32 == 1
    assert ((-1 * 2) & ((1 << 64)-1)) >> 32 == MASK
    assert struct.unpack("<I", struct.pack("<f", 1.5+2.25))[0] == 0x40700000
    for displacement in range(-4096, 4096, 2):
        encoded = ((displacement >> 12) & 1) << 31 | ((displacement >> 5) & 63) << 25 | ((displacement >> 1) & 15) << 8 | ((displacement >> 11) & 1) << 7
        decoded = ((encoded >> 31) & 1) << 12 | ((encoded >> 7) & 1) << 11 | ((encoded >> 25) & 63) << 5 | ((encoded >> 8) & 15) << 1
        assert signed(decoded, 13) == displacement
    print("PASS: constant construction, signed shifts, product halves, binary32, all 4096 B displacements")


def text_section(path):
    data = path.read_bytes()
    assert data[:6] == b"\x7fELF\x01\x01", "Expected little-endian ELF32"
    shoff = struct.unpack_from("<I", data, 32)[0]
    shsize, shnum, strindex = struct.unpack_from("<HHH", data, 46)
    sections = [struct.unpack_from("<10I", data, shoff+i*shsize) for i in range(shnum)]
    strings = sections[strindex]
    names = data[strings[4]:strings[4]+strings[5]]
    for section in sections:
        name = names[section[0]:].split(b"\0", 1)[0]
        if name == b".text":
            return data[section[4]:section[4]+section[5]]
    raise AssertionError("No .text section")


def check_clang():
    clang = shutil.which("clang")
    if not clang:
        raise SystemExit("--assemble requires Clang with RISC-V target support")
    expected = [
        ("add x10,x11,x12", 0x00C58533, "17-r-i-encoding.md"),
        ("sub x10,x11,x12", 0x40C58533, "17-r-i-encoding.md"),
        ("addi x5,x6,-20", 0xFEC30293, "17-r-i-encoding.md"),
        ("sw x9,12(x8)", 0x00942623, "18-s-b-encoding.md"),
        ("beq x5,x6,.-16", 0xFE6288E3, "18-s-b-encoding.md"),
        ("lui x5,0x2468A", 0x2468A2B7, "19-u-j-encoding.md"),
        ("jal x1,.+20", 0x014000EF, "19-u-j-encoding.md"),
        ("addi x5,x0,5", 0x00500293, "21-stored-program.md"),
        ("addi x6,x5,3", 0x00328313, "21-stored-program.md"),
        ("sw x6,0(x0)", 0x00602023, "21-stored-program.md"),
    ]
    with tempfile.TemporaryDirectory(prefix="chapter06-") as folder:
        source, obj = Path(folder)/"examples.s", Path(folder)/"examples.o"
        def compile_text(body):
            source.write_text(body, encoding="utf-8")
            subprocess.run([clang, "--target=riscv32", "-march=rv32imfc", "-mabi=ilp32", "-c", str(source), "-o", str(obj)], check=True, capture_output=True, text=True)
        all_blocks = [block for path in sorted(CONTENT.glob("*.md")) for block in blocks(path.name)]
        compile_text(".option norvc\n" + "\n".join(".text\n"+block for block in all_blocks))
        print(f"PASS: Clang assembled all {len(all_blocks)} lesson assembly blocks")
        compile_text(".text\n.option norvc\n.option norelax\n"+"\n".join(row[0] for row in expected))
        actual = struct.unpack("<"+"I"*len(expected), text_section(obj))
        for word, (instruction, reference, lesson) in zip(actual, expected):
            assert f"0x{reference:08X}" in (CONTENT/lesson).read_text(encoding="utf-8")
            assert word == reference, (instruction, hex(word), hex(reference))
        print(f"PASS: Clang independently matched {len(expected)} published instruction words")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()
    check_numbers()
    check_execution()
    if args.assemble:
        check_clang()
