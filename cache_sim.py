"""Trace-driven set-associative LRU cache model; Python standard library only."""
import argparse
import json
from collections import OrderedDict
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Access:
    address: int
    block: int
    set_index: int
    tag: int
    hit: bool
    evicted_tag: int | None


class Cache:
    def __init__(self, size: int, line_size: int, ways: int):
        if any(type(value) is not int or value <= 0 for value in (size, line_size, ways)):
            raise ValueError("size, line_size and ways must be positive integers")
        if size % (line_size * ways):
            raise ValueError("size must be divisible by line_size * ways")
        self.line_size = line_size
        self.ways = ways
        self.sets: list[OrderedDict[int, None]] = [OrderedDict() for _ in range(size // (line_size * ways))]
        self.hits = 0
        self.misses = 0

    def access(self, address: int) -> Access:
        if type(address) is not int or not 0 <= address < 2**64:
            raise ValueError("address must be an unsigned 64-bit integer")
        block = address // self.line_size
        index = block % len(self.sets)
        tag = block // len(self.sets)
        entries = self.sets[index]
        hit = tag in entries
        evicted = None
        if hit:
            self.hits += 1
            entries.move_to_end(tag)
        else:
            self.misses += 1
            if len(entries) == self.ways:
                evicted, _ = entries.popitem(last=False)
            entries[tag] = None
        return Access(address, block, index, tag, hit, evicted)

    def summary(self) -> dict:
        total = self.hits + self.misses
        return {"accesses": total, "hits": self.hits, "misses": self.misses,
                "hit_rate": self.hits / total if total else 0.0}


def addresses(path: Path):
    with path.open(encoding="utf-8") as source:
        for number, line in enumerate(source, 1):
            value = line.split("#", 1)[0].strip()
            if value:
                try:
                    yield int(value, 16 if value.lower().startswith("0x") else 10)
                except ValueError as error:
                    raise ValueError(f"line {number}: expected one decimal or hexadecimal address") from error


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    parser.add_argument("--size", type=int, default=64, help="cache capacity in bytes")
    parser.add_argument("--line-size", type=int, default=16, help="bytes per cache line")
    parser.add_argument("--ways", type=int, default=1, help="1 = direct mapped")
    parser.add_argument("--trace", action="store_true", dest="show_trace", help="emit access records as JSON Lines")
    args = parser.parse_args(argv)
    try:
        cache = Cache(args.size, args.line_size, args.ways)
        for address in addresses(args.trace):
            result = cache.access(address)
            if args.show_trace:
                print(json.dumps({"type": "access", **asdict(result)}))
        print(json.dumps({"type": "summary", **cache.summary()}))
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
