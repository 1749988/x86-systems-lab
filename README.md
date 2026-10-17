# x86 Systems Lab

An executable **C + x86-64 Assembly + Python** learning project connecting low-level code with memory behavior: array routines called from C, differential tests, and a trace-driven cache simulator.

Inspired by university work on registers, indexed addressing, the stack, and cache organization. The examples are original portfolio exercises, not copied assignment solutions. They are written for clarity; no performance advantage over optimized C is claimed.

## 1. Run the assembly demo

Requires **Linux x86-64**, GCC, GNU Make and Python 3.10+. Windows users can use an x86-64 WSL Linux environment. Native Windows/MSVC, macOS and ARM builds are not supported.

```bash
make
./build/array-demo 4 -2 4 0
```

```text
sum: 6
occurrences of 4: 2
reversed: 0 4 -2 4
```

The C program parses at most 1,024 signed 32-bit decimal integers and rejects invalid or out-of-range input. The assembler implements:

| Function | Result | Key concept |
| --- | --- | --- |
| `sum_i32` | Signed 64-bit sum | Sign extension with `movsxd` |
| `count_equal_i32` | Number of matches | Indexed addressing and conditional branches |
| `reverse_i32` | In-place reversal | Two indices, memory writes and boundary handling |

The functions use GNU assembler Intel syntax and the **System V AMD64 ABI**: arguments in RDI/RSI/RDX, return value in RAX, and caller-saved scratch registers. They are leaf functions and leave callee-saved registers untouched. See `array_ops.h` for pointer and overflow preconditions. Empty arrays are supported by the library even though the CLI requires one value.

## 2. Explore cache conflicts

The Python tool models byte addresses, fixed-size lines, configurable associativity and **LRU** replacement. It starts with an empty cache. One trace line represents one read of a byte address.

```bash
python3 cache_sim.py conflict-trace.txt --size 64 --line-size 16 --ways 1
python3 cache_sim.py conflict-trace.txt --size 64 --line-size 16 --ways 2
```

For the included synthetic trace:

| Organization | Accesses | Hits | Misses |
| --- | --- | --- | --- |
| Direct mapped, 64 bytes | 6 | 0 | 6 |
| 2-way LRU, 64 bytes | 6 | 4 | 2 |

Add `--trace` to emit JSON Lines containing the block number, set index, tag, hit/miss and evicted tag for every access, followed by a summary. Decimal and `0x` hexadecimal addresses and `#` comments are supported. Invalid input exits with code 2; when tracing, records emitted before an error remain partial output.

The mapping is `block = address // line_size`, `set = block % number_of_sets`, and `tag = block // number_of_sets`. LRU order is tracked separately in each set.

**Model limits:** this is not a CPU benchmark or a cycle-accurate simulator. It has no writes, dirty bits, prefetching, multi-level hierarchy, virtual memory or hardware performance counters. The supplied trace is not a measurement of the assembly routines. It illustrates cache geometry independently.

## Verification

```bash
make test
```

- C reference checks compare all three assembly routines across **5,140 deterministic generated cases**, plus signed extremes and empty arrays.
- Guard pages check accesses at both ends of arrays. This matters because ordinary compiler sanitizers do not instrument handwritten assembly.
- Ten Python tests cover cache mapping, spatial locality, conflict misses, LRU refresh, validation and CLI output.
- CLI checks reject malformed and out-of-range integers.
- GitHub Actions runs the same suite on Ubuntu x86-64.

## Inspect the machine code

```bash
make disassemble
gdb ./build/array-demo
```

Inside GDB (install separately if absent):

```text
set disassembly-flavor intel
break sum_i32
run 4 -2 4 0
info registers rdi rsi rax rcx
x/4dw $rdi
disassemble sum_i32
stepi
```

See [LEARN.md](LEARN.md) for a Spanish walkthrough and exercises.

References: [GNU assembler Intel syntax](https://www.sourceware.org/binutils/docs/as/i386_002dVariations.html) and [x86-64 System V ABI](https://gitlab.com/x86-psABIs/x86-64-ABI/-/tree/master).
