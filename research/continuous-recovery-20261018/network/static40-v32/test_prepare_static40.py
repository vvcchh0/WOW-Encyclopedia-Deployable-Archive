import json
import tempfile
import unittest
from pathlib import Path


import prepare_static40 as FACTORY


class Static40FactoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue, cls.rows, cls.sources = FACTORY.load_frozen_queue()

    def test_queue_is_exact_forty_and_excludes_only_literal_space_target(self):
        self.assertEqual(len(self.rows), 40)
        self.assertEqual([item["queue_rank"] for item in self.rows], list(range(1, 41)))
        self.assertEqual([item["candidate_priority_rank"] for item in self.rows], list(range(1, 11)) + list(range(12, 42)))
        excluded = self.queue["excluded_targets"]
        self.assertEqual(len(excluded), 1)
        self.assertEqual(excluded[0]["candidate_priority_rank"], 11)
        self.assertEqual(excluded[0]["requested_url"], "http://www.worldofwarcraft.com/info/basics/images/small pets/icon.gif")

    def test_first_and_last_targets_are_literal_candidate_urls(self):
        self.assertEqual(self.rows[0]["original"], "http://www.worldofwarcraft.com/images/layout/title-overview.png")
        self.assertEqual(self.rows[-1]["original"], "http://www.wowarmory.com/images/icons/21x21/inv_boots_08.png")
        self.assertEqual(self.sources["source_audit"]["sha256"], FACTORY.EXPECTED_SOURCE_AUDIT_SHA)
        self.assertEqual(self.sources["navigation_exclusion_correction"]["sha256"], FACTORY.EXPECTED_CORRECTION_SHA)

    def test_every_candidate_reference_is_page_sha_and_line_bound(self):
        for item in self.rows:
            self.assertTrue(item["verified_references"], item["original"])
            for ref in item["verified_references"]:
                self.assertEqual(ref["sha256"], FACTORY.sha256(FACTORY.ROOT / ref["path"]))
                self.assertGreaterEqual(ref["line"], 1)

    def test_exact_url_rejects_space_query_credentials_and_nondefault_port(self):
        for value in (
            "http://example.invalid/a b.gif",
            "https://example.invalid/image.gif?x=1",
            "https://user:pass@example.invalid/image.gif",
            "https://@example.invalid/image.gif",
            "https://example.invalid:8443/image.gif",
        ):
            with self.assertRaises(RuntimeError):
                FACTORY._parse_url(value)
        FACTORY._parse_url("http://example.invalid:80/image.gif")
        FACTORY._parse_url("https://example.invalid:443/image.gif")

    def test_batch_bounds_and_policy_are_frozen(self):
        self.assertEqual(len(FACTORY.select_batch(self.rows, 1)), 10)
        self.assertEqual(len(FACTORY.select_batch(self.rows, 4)), 10)
        for value in (0, 5):
            with self.assertRaisesRegex(RuntimeError, "1 through 4"):
                FACTORY.select_batch(self.rows, value)
        policy = FACTORY.make_policy(0)
        self.assertEqual(policy["max_attempts"], 24)
        self.assertEqual(policy["window_seconds"], 240.0)
        self.assertEqual(policy["max_total_body_bytes"], 16 * 1024 * 1024)
        self.assertEqual(policy["max_entity_body_bytes"], 8 * 1024 * 1024)
        self.assertEqual(policy["direct_attempt_budget"], 4)
        self.assertEqual(policy["proxy_attempt_budget"], 20)

    def test_atomic_fixture_bindings_match_actual_lf_bytes(self):
        with tempfile.TemporaryDirectory(dir=FACTORY.FACTORY_ROOT, prefix="test-atomic-") as temp:
            original_root = FACTORY.FACTORY_ROOT
            FACTORY.FACTORY_ROOT = Path(temp)
            try:
                snapshot = {"captured_utc": "2026-10-18T00:00:00Z", "network_requests": 0}
                snapshot_ref = {"path": "static40-v32/batch-01/status-snapshot.json",
                                "sha256": FACTORY.json_sha256(snapshot),
                                "bytes": len(FACTORY.json_bytes(snapshot)), "role": "test snapshot"}
                plan = {"input_bindings": {"status_snapshot": snapshot_ref}, "candidate_count": 10}
                bindings = {"plan_sha256": FACTORY.json_sha256(plan)}
                FACTORY.write_batch_atomic(1, {"status-snapshot.json": snapshot,
                                               "plan.json": plan,
                                               "input-bindings.json": bindings})
                target = Path(temp) / "batch-01"
                self.assertEqual((target / "status-snapshot.json").stat().st_size, snapshot_ref["bytes"])
                self.assertEqual(FACTORY.sha256(target / "status-snapshot.json"), snapshot_ref["sha256"])
                self.assertEqual(FACTORY.sha256(target / "plan.json"), bindings["plan_sha256"])
                self.assertEqual((target / "plan.json").read_bytes(), FACTORY.json_bytes(plan))
            finally:
                FACTORY.FACTORY_ROOT = original_root

    def test_atomic_writer_rejects_escape_without_leaving_temp(self):
        with tempfile.TemporaryDirectory(dir=FACTORY.FACTORY_ROOT, prefix="test-escape-") as temp:
            original_root = FACTORY.FACTORY_ROOT
            FACTORY.FACTORY_ROOT = Path(temp)
            try:
                with self.assertRaisesRegex(RuntimeError, "document .* escapes"):
                    FACTORY.write_batch_atomic(1, {"../outside.json": {"network_requests": 0}})
                self.assertEqual(list(Path(temp).iterdir()), [])
            finally:
                FACTORY.FACTORY_ROOT = original_root


if __name__ == "__main__":
    unittest.main()
