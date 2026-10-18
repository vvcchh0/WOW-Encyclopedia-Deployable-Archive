import copy
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("prepare_navigation70.py")
SPEC = importlib.util.spec_from_file_location("prepare_navigation70", MODULE_PATH)
FACTORY = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(FACTORY)


class Navigation70FactoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue, cls.rows, cls.queue_sources = FACTORY.load_frozen_queue()

    def test_real_queue_and_first_batch_are_exact(self):
        self.assertEqual(FACTORY.sha256(FACTORY.QUEUE_PATH), FACTORY.EXPECTED_QUEUE_SHA)
        self.assertEqual(len(self.rows), 70)
        self.assertEqual([item["row"]["rank"] for item in self.rows], list(range(1, 71)))
        first = [item["row"]["original"] for item in FACTORY.select_batch(self.rows, 1)]
        self.assertEqual(first, [
            "http://www.worldofwarcraft.com/news/images/07-08/ss01.jpg",
            "http://www.worldofwarcraft.com/news/images/07-08/ss02.jpg",
            "http://www.worldofwarcraft.com/news/images/07-08/tcg01.jpg",
            "http://www.worldofwarcraft.com/news/images/07-08/tcg02.jpg",
            "http://www.worldofwarcraft.com/news/images/07-08/tcg03.jpg",
            "http://www.worldofwarcraft.com/news/images/07-08/wow-bc.jpg",
            "http://www.worldofwarcraft.com/news/images/07-07/comic-full.jpg",
            "http://www.worldofwarcraft.com/news/images/07-11/comic1.jpg",
            "http://www.worldofwarcraft.com/news/images/07-11/comic2.jpg",
            "http://www.worldofwarcraft.com/info/basics/images/trade/ss01.jpg",
        ])

    def test_primary_references_are_separate_from_alternate_context(self):
        item = next(item for item in self.rows if item["row"]["rank"] == 18)
        self.assertEqual(len(item["primary_evidence"]), len(item["row"]["references"]))
        self.assertEqual(len(item["alternate_context"]), 1)
        self.assertNotEqual(item["alternate_context"][0]["original"], item["row"]["original"])

    def test_duplicate_original_is_rejected(self):
        mutated = copy.deepcopy(self.queue)
        mutated["rows"][1]["original"] = mutated["rows"][0]["original"]
        with self.assertRaisesRegex(RuntimeError, "duplicate original"):
            FACTORY.validate_queue_document(mutated, FACTORY.QUEUE_PATH)

    def test_batch_bounds_and_ten_target_contract(self):
        with self.assertRaisesRegex(RuntimeError, "1 through 7"):
            FACTORY.select_batch(self.rows, 0)
        with self.assertRaisesRegex(RuntimeError, "1 through 7"):
            FACTORY.select_batch(self.rows, 8)
        self.assertEqual(len(FACTORY.select_batch(self.rows, 7)), 10)

    def test_exact_url_rejects_credentials_query_and_nondefault_port(self):
        for value in (
            "https://user:pass@example.invalid/x.jpg",
            "https://example.invalid/x.jpg?x=1",
            "https://example.invalid:8443/x.jpg",
        ):
            with self.assertRaises(RuntimeError):
                FACTORY._parse_url(value)

    def test_closed_gate_and_future_cooldown_are_refused(self):
        status = {"network_resume_gate_passed": False}
        with self.assertRaisesRegex(RuntimeError, "resume gate is closed"):
            if status.get("network_resume_gate_passed") is not True:
                raise RuntimeError("network resume gate is closed")
        now = datetime.now(timezone.utc)
        future = (now + timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
        with self.assertRaisesRegex(RuntimeError, "still active"):
            FACTORY._not_in_cooldown({"network_cooldown_not_before_utc": future}, {}, now)

    def test_existing_batch_refusal_does_not_overwrite(self):
        FACTORY.FACTORY_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=FACTORY.FACTORY_ROOT, prefix="test-existing-") as temp:
            existing = Path(temp) / "batch-01"
            existing.mkdir()
            (existing / "plan.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "already exists"):
                FACTORY.ensure_batch_available(existing)

    def test_atomic_fixture_bytes_match_plan_and_snapshot_bindings(self):
        # Keep the real factory directory free of batch artifacts: the actual
        # write/rename happens below a temporary child which is removed by the
        # test harness.
        with tempfile.TemporaryDirectory(dir=FACTORY.FACTORY_ROOT, prefix="test-atomic-") as temp:
            original_factory_root = FACTORY.FACTORY_ROOT
            FACTORY.FACTORY_ROOT = Path(temp)
            try:
                snapshot = {"captured_utc": "2026-10-18T00:00:00Z", "network_requests": 0}
                snapshot_ref = {
                    "path": "research/continuous-recovery-20261018/network/navigation70-v32/batch-01/status-snapshot.json",
                    "sha256": FACTORY.json_sha256(snapshot),
                    "bytes": len(FACTORY.json_bytes(snapshot)),
                    "role": "atomic fixture snapshot",
                }
                plan = {"input_bindings": {"status_snapshot": snapshot_ref}, "candidate_count": 10}
                bindings = {"plan_sha256": FACTORY.json_sha256(plan)}
                result = FACTORY.write_batch_atomic(1, {
                    "status-snapshot.json": snapshot,
                    "plan.json": plan,
                    "input-bindings.json": bindings,
                })
                written = Path(temp) / "batch-01"
                self.assertEqual(result["batch_dir"], FACTORY.rel(written))
                actual_snapshot = written / "status-snapshot.json"
                actual_plan = written / "plan.json"
                self.assertEqual(FACTORY.sha256(actual_snapshot), snapshot_ref["sha256"])
                self.assertEqual(actual_snapshot.stat().st_size, snapshot_ref["bytes"])
                self.assertEqual(FACTORY.sha256(actual_plan), bindings["plan_sha256"])
                self.assertEqual(actual_plan.read_bytes(), FACTORY.json_bytes(plan))
            finally:
                FACTORY.FACTORY_ROOT = original_factory_root

    def test_atomic_writer_rejects_document_escape_and_cleans_inside_factory(self):
        with tempfile.TemporaryDirectory(dir=FACTORY.FACTORY_ROOT, prefix="test-atomic-escape-") as temp:
            original_factory_root = FACTORY.FACTORY_ROOT
            FACTORY.FACTORY_ROOT = Path(temp)
            try:
                with self.assertRaisesRegex(RuntimeError, "document .* escapes"):
                    FACTORY.write_batch_atomic(1, {"../outside.json": {"network_requests": 0}})
                self.assertEqual(list(Path(temp).iterdir()), [])
            finally:
                FACTORY.FACTORY_ROOT = original_factory_root

    def test_policy_has_the_frozen_limits(self):
        policy = FACTORY.make_policy(0)
        self.assertEqual(policy["max_attempts"], 24)
        self.assertEqual(policy["window_seconds"], 240.0)
        self.assertEqual(policy["max_total_body_bytes"], 16 * 1024 * 1024)
        self.assertEqual(policy["max_entity_body_bytes"], 8 * 1024 * 1024)
        self.assertEqual(policy["direct_attempt_budget"], 4)
        self.assertEqual(policy["proxy_attempt_budget"], 20)
        self.assertEqual(policy["automatic_redirects"], 0)
        self.assertEqual(policy["stop_http_codes"], [429, 503])

    def test_in_memory_plan_has_driver_shaped_file_bindings(self):
        status, source, source_path, control, control_path, runtime, tail = FACTORY.load_runtime_bindings()
        batch_dir = FACTORY.FACTORY_ROOT / "batch-01"
        snapshot = {"captured_utc": runtime["captured_utc"], "network_requests": 0}
        snapshot_ref = {
            "path": FACTORY.rel(batch_dir / "status-snapshot.json"),
            "sha256": FACTORY.json_sha256(snapshot),
            "bytes": len(FACTORY.json_bytes(snapshot)),
            "role": "test snapshot",
        }
        plan, bindings, cache, selection = FACTORY.make_plan(
            1, self.queue, self.rows, FACTORY.sha256(FACTORY.QUEUE_PATH),
            self.queue_sources, runtime, snapshot_ref, source_path,
            FACTORY.sha256(source_path), tail)
        self.assertEqual(bindings["plan_sha256"], FACTORY.json_sha256(plan))
        self.assertEqual(plan["candidate_count"], 10)
        for key, entry in plan["input_bindings"].items():
            self.assertIsInstance(entry, dict, key)
            self.assertIn("path", entry, key)
            self.assertIn("sha256", entry, key)


if __name__ == "__main__":
    unittest.main()
