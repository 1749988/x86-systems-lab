import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from cache_sim import Cache, addresses, main


class CacheTests(unittest.TestCase):
    def test_spatial_locality(self):
        cache = Cache(64, 16, 1)
        self.assertFalse(cache.access(0).hit)
        self.assertTrue(cache.access(15).hit)
        self.assertFalse(cache.access(16).hit)
        self.assertEqual(cache.summary()["hits"], 1)

    def test_direct_mapped_conflict(self):
        cache = Cache(64, 16, 1)
        results = [cache.access(x) for x in [0, 64, 0, 64]]
        self.assertTrue(all(not item.hit for item in results))
        self.assertEqual(results[1].evicted_tag, 0)

    def test_associativity_removes_this_conflict(self):
        cache = Cache(64, 16, 2)
        self.assertEqual([cache.access(x).hit for x in [0, 64, 0, 64]], [False, False, True, True])

    def test_hits_refresh_lru(self):
        cache = Cache(32, 16, 2)
        for address in [0, 16, 0]:
            cache.access(address)
        self.assertEqual(cache.access(32).evicted_tag, 1)
        self.assertTrue(cache.access(0).hit)
        self.assertFalse(cache.access(16).hit)

    def test_set_index_and_tag(self):
        item = Cache(128, 16, 2).access(144)
        self.assertEqual((item.block, item.set_index, item.tag), (9, 1, 2))

    def test_empty_summary(self):
        self.assertEqual(Cache(16, 16, 1).summary(), {"accesses": 0, "hits": 0, "misses": 0, "hit_rate": 0.0})

    def test_invalid_geometry(self):
        for values in [(0, 16, 1), (64, 0, 1), (64, 16, 0), (63, 16, 1), (16, 16, 2), (True, 1, 1)]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                Cache(*values)

    def test_invalid_address(self):
        cache = Cache(64, 16, 1)
        for value in [-1, 2**64, 1.5, True]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                cache.access(value)

    def test_trace_parsing_and_cli(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trace.txt"
            path.write_text("# synthetic trace\n0x00\n64 # conflict\n0\n64\n", encoding="utf-8")
            self.assertEqual(list(addresses(path)), [0, 64, 0, 64])
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([str(path), "--ways", "2", "--trace"]), 0)
            records = [json.loads(line) for line in output.getvalue().splitlines()]
            self.assertEqual(len(records), 5)
            self.assertEqual(records[-1]["hit_rate"], 0.5)

    def test_malformed_trace(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trace.txt"
            path.write_text("0\nhello\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 2"):
                list(addresses(path))


if __name__ == "__main__":
    unittest.main()
