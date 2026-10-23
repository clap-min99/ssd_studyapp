"""Check chapter 5 arithmetic formulas against independent integer arithmetic.

This checks the mathematical models, not HDL simulation or physical timing.
"""

from fractions import Fraction
from itertools import product
import struct


def signed4(value):
    return value - 16 if value & 8 else value


def check(condition, context):
    if not condition:
        raise AssertionError(context)


def main():
    count = 0
    for a, b, cin in product(range(2), repeat=3):
        s = a ^ b ^ cin
        carry = (a & b) | ((a ^ b) & cin)
        check(2 * carry + s == a + b + cin, (a, b, cin, "full adder"))
        count += 1

    for a, b, cin in product(range(16), range(16), range(2)):
        g = [((a >> i) & 1) & ((b >> i) & 1) for i in range(4)]
        p = [((a >> i) & 1) | ((b >> i) & 1) for i in range(4)]
        block_g = g[3] | (p[3] & g[2]) | (p[3] & p[2] & g[1]) | (p[3] & p[2] & p[1] & g[0])
        block_p = p[3] & p[2] & p[1] & p[0]
        check((block_g | (block_p & cin)) == ((a+b+cin) >> 4), (a, b, cin, "CLA"))
        # Combine adjacent prefix ranges, preserving high/low bit order.
        def merge(high, low):
            return high[0] | (high[1] & low[0]), high[1] & low[1]
        high = merge((g[3], p[3]), (g[2], p[2]))
        low = merge((g[1], p[1]), (g[0], p[0]))
        check(merge(high, low) == (block_g, block_p), (a, b, "prefix"))
        count += 1

    for a, b, sub in product(range(16), range(16), range(2)):
        extended = a + (b ^ (15 if sub else 0)) + sub
        result, carry = extended & 15, (extended >> 4) & 1
        n = (result >> 3) & 1
        overflow = (((a ^ result) >> 3) & 1) & (1 ^ (((a ^ b) >> 3) & 1) ^ sub)
        mathematical = signed4(a) - signed4(b) if sub else signed4(a) + signed4(b)
        check(bool(overflow) == (not -8 <= mathematical <= 7), (a, b, sub, "overflow"))
        if sub:
            check(bool(n ^ overflow) == (signed4(a) < signed4(b)), (a, b, "signed less"))
            check(bool(1 ^ carry) == (a < b), (a, b, "unsigned less"))
        count += 1

    for a, b in product(range(16), range(1, 16)):
        remainder = quotient = 0
        for i in range(3, -1, -1):
            trial = 2 * remainder + ((a >> i) & 1)
            bit = int(trial >= b)
            remainder = trial - b if bit else trial
            quotient |= bit << i
            check(0 <= remainder < b, (a, b, i, "partial remainder"))
        check((quotient, remainder) == divmod(a, b), (a, b, "division"))
        count += 1

    for a, shift in product(range(256), range(8)):
        rotate = ((a >> shift) | (a << (8-shift))) & 255
        bits = f"{a:08b}"
        reference = bits[-shift:] + bits[:-shift] if shift else bits
        check(rotate == int(reference, 2), (a, shift, "rotate"))
        count += 1

    check(Fraction(10, 8) + Fraction(-3, 8) == Fraction(7, 8), "Q3.3 addition")
    check(Fraction(10 * 4, 64) == Fraction(5, 8), "fixed multiplication")
    check(struct.unpack(">I", struct.pack(">f", 6.5))[0] == 0x40D00000, "binary32 encoding")
    midpoint = 1 + 2**-24
    check(struct.unpack(">f", struct.pack(">f", midpoint))[0] == 1.0, "binary32 ties to even")
    q = 0
    actual = []
    for reset, en, data in [(0, 1, 9), (0, 0, 7), (0, 1, 7), (1, 1, 5)]:
        carry_before = (q + data) >> 4
        q = 0 if reset else ((q + data) % 16 if en else q)
        actual.append((carry_before, q))
    check(actual == [(0, 9), (1, 9), (1, 0), (0, 0)], "accumulator table")
    print(f"PASS: {count} exhaustive input cases and fixed-point, binary32, accumulator examples")


if __name__ == "__main__":
    main()
