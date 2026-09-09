"""동일 관계의 조회와 측정 범주가 어긋나는 회귀를 검사한다."""

import importlib
import json
import unittest


class ReachabilityBenchmarkTests(unittest.TestCase):
    def setUp(self):
        try:
            self.benchmark = importlib.import_module("sparql_bench").benchmark
        except ModuleNotFoundError:
            self.fail("동일 관계 benchmark가 아직 구현되지 않았다")

    def test_direction_cycles_duplicate_edges_and_isolated_seeds(self):
        result = self.benchmark(
            ["a", "b", "c", "d", "isolated", "절 / 10%"],
            [("a", "b"), ("b", "c"), ("c", "a"), ("a", "d"),
             ("a", "b"), ("절 / 10%", "d")],
            ["a", "d", "isolated", "절 / 10%"],
            repeats=2,
        )
        expected = {
            "a": ["a", "b", "c", "d"],
            "d": ["d"],
            "isolated": ["isolated"],
            "절 / 10%": ["d", "절 / 10%"],
        }
        for seed, ids in expected.items():
            self.assertEqual(result["results"][seed]["json"], ids)
            self.assertEqual(result["results"][seed]["sparql"], ids)
            self.assertTrue(result["results"][seed]["equivalent"])
        self.assertTrue(result["exact_equivalence"])
        self.assertEqual(result["node_count"], 6)
        self.assertEqual(result["edge_count"], 5)
        self.assertEqual(json.loads(json.dumps(result)), result)

    def test_preparation_is_separate_from_thirty_warm_seed_batches(self):
        result = self.benchmark(["left", "right"], [("left", "right")], ["left"])
        self.assertEqual(result["repeats"], 30)
        self.assertEqual(result["environment"]["rdflib"], "7.6.0")
        self.assertTrue(result["environment"]["python"])
        self.assertGreaterEqual(result["preparation"]["normalization_ms"], 0)
        for engine in ("json", "rdf"):
            preparation = result["preparation"][engine]
            self.assertGreater(preparation["serialized_bytes"], 0)
            for key in ("build_ms", "serialize_ms", "parse_ms", "query_prepare_ms"):
                self.assertGreaterEqual(preparation[key], 0)
        for engine in ("json", "sparql"):
            stats = result["warm_queries"][engine]
            self.assertEqual(len(stats["samples_ms"]), 30)
            self.assertGreaterEqual(stats["min_ms"], 0)
            self.assertLessEqual(stats["min_ms"], stats["median_ms"])
            self.assertLessEqual(stats["median_ms"], stats["max_ms"])

    def test_rejects_dangling_edges_and_unknown_seeds(self):
        for nodes, edges, seeds in (
            (["a"], [("a", "missing")], ["a"]),
            (["a"], [("missing", "a")], ["a"]),
            (["a"], [], ["missing"]),
        ):
            with self.subTest(nodes=nodes, edges=edges, seeds=seeds):
                with self.assertRaises(ValueError):
                    self.benchmark(nodes, edges, seeds)

    def test_rejects_measurements_without_trials_or_seeds(self):
        for seeds, repeats in ((["a"], 0), (["a"], -1), ([], 1)):
            with self.subTest(seeds=seeds, repeats=repeats):
                with self.assertRaises(ValueError):
                    self.benchmark(["a"], [], seeds, repeats)


if __name__ == "__main__":
    unittest.main()
