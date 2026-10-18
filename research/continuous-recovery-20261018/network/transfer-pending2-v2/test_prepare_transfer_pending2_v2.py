import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("prepare_transfer_pending2_v2.py")
SPEC = importlib.util.spec_from_file_location("transfer_pending2_factory", MODULE_PATH)
FACTORY = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(FACTORY)


class TransferPending2FactoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue, cls.rows, cls.queue_sources = FACTORY.load_frozen_queue()

    def test_real_queue_has_exact_targets_and_page_citations(self):
        self.assertEqual(FACTORY.sha256(FACTORY.QUEUE_PATH), FACTORY.EXPECTED_QUEUE_SHA)
        self.assertEqual([item["row"]["rank"] for item in self.rows], [1, 2])
        self.assertEqual(
            [item["row"]["original"] for item in self.rows],
            [
                "http://www.worldofwarcraft.com/news/images/08-02/02-06-08-3.jpg",
                "http://www.worldofwarcraft.com/news/images/05-02/EU2.jpg",
            ],
        )
        self.assertEqual(self.rows[0]["primary_evidence"][0]["match"], "url_encoded")
        self.assertEqual(self.rows[1]["primary_evidence"][0]["match"], "url_encoded")
        self.assertEqual(self.rows[0]["primary_evidence"][0]["line"], 3338)
        self.assertEqual(self.rows[1]["primary_evidence"][0]["line"], 2027)
        self.assertEqual(self.rows[0]["row"]["prior_attempt"]["old_cdx_curl_exit"], 35)
        self.assertEqual(self.rows[1]["row"]["prior_attempt"]["old_replay_curl_exit"], 28)
        self.assertEqual(self.rows[1]["row"]["prior_attempt"]["old_replay_source_status"], 200)

    def test_exact_url_guards_and_default_ports(self):
        for value in (
            "https://user:pass@example.invalid/x.jpg",
            "https://@example.invalid/x.jpg",
            "https://example.invalid/x.jpg?x=1",
            "https://example.invalid:8443/x.jpg",
        ):
            with self.assertRaises(RuntimeError):
                FACTORY._parse_url(value)
        FACTORY._parse_url("http://example.invalid:80/x.jpg")
        FACTORY._parse_url("https://example.invalid:443/x.jpg")

    def test_policy_uses_frozen_driver_cap_for_two_target_retry(self):
        policy = FACTORY.make_policy(0)
        self.assertEqual(policy["max_originals"], 20)
        self.assertEqual(policy["max_attempts"], 8)
        self.assertEqual(policy["window_seconds"], 100.0)
        self.assertEqual(policy["max_total_body_bytes"], 8 * 1024 * 1024)
        self.assertEqual(policy["max_entity_body_bytes"], 4 * 1024 * 1024)
        self.assertEqual(policy["direct_attempt_budget"], 4)
        self.assertEqual(policy["proxy_attempt_budget"], 20)
        self.assertEqual(policy["direct_connect_seconds"], 4.0)
        self.assertEqual(policy["proxy_timeout_seconds"], 20.0)
        self.assertEqual(policy["min_dispatch_seconds"], 5.25)
        self.assertEqual(policy["min_request_start_seconds"], 5.0)
        self.assertEqual(policy["automatic_redirects"], 0)
        self.assertEqual(policy["stop_http_codes"], [429, 503])

    def test_real_frozen_driver_loads_generated_plan(self):
        """Exercise the actual frozen loader, without entering its network CLI."""
        plan_path = FACTORY.FACTORY_ROOT / "batch-01" / "plan.json"
        if not plan_path.is_file():
            self.skipTest("prepare batch-01 before running the real frozen loader check")
        spec = importlib.util.spec_from_file_location(
            "frozen_reusable_image_driver_transfer_pending2_v2",
            FACTORY.V3_DRIVER_PATH,
        )
        assert spec is not None and spec.loader is not None
        driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(driver)
        driver.configure_from_plan(plan_path)
        loaded_plan, loaded_bindings = driver.load_and_validate_inputs()
        self.assertEqual(loaded_plan["candidate_count"], 2)
        self.assertEqual(loaded_plan["policy"]["max_originals"], 20)
        self.assertEqual(loaded_bindings["plan_sha256"], FACTORY.sha256(plan_path))
        self.assertEqual(loaded_bindings["driver_sha256"], FACTORY.EXPECTED_DRIVER_SHA)

    def test_dynamic_bindings_and_in_memory_plan_are_current_and_exact(self):
        status, source, source_path, control, control_path, runtime, tail = FACTORY.load_runtime_bindings()
        self.assertTrue(runtime["latest_source_acceptance"]["path"].startswith("research/"))
        self.assertIn("control03", runtime["latest_control_gate"]["path"].lower())
        self.assertEqual(tail, 0)
        snapshot = {"captured_utc": runtime["captured_utc"], "network_requests": 0}
        snapshot_ref = {
            "path": FACTORY.rel(FACTORY.FACTORY_ROOT / "batch-01" / "status-snapshot.json"),
            "sha256": FACTORY.json_sha256(snapshot),
            "bytes": len(FACTORY.json_bytes(snapshot)),
            "role": "offline test snapshot",
        }
        plan, bindings, cache, selection = FACTORY.make_plan(
            1,
            self.queue,
            self.rows,
            FACTORY.sha256(FACTORY.QUEUE_PATH),
            self.queue_sources,
            runtime,
            snapshot_ref,
            source_path,
            FACTORY.sha256(source_path),
            tail,
        )
        self.assertEqual(plan["candidate_count"], 2)
        self.assertEqual(bindings["plan_sha256"], FACTORY.json_sha256(plan))
        self.assertEqual(cache["planned_request_bound"], 8)
        self.assertEqual(selection["selected"][0]["all_references"][0]["match"], "url_encoded")
        self.assertEqual(plan["candidates"][0]["query"]["from"], "20000101000000")
        self.assertEqual(plan["candidates"][0]["query"]["to"], "20080512210044")

    def test_atomic_fixture_has_actual_lf_bytes_and_matching_bindings(self):
        with tempfile.TemporaryDirectory(dir=FACTORY.FACTORY_ROOT, prefix="test-atomic-") as temp:
            original_root = FACTORY.FACTORY_ROOT
            FACTORY.FACTORY_ROOT = Path(temp)
            try:
                snapshot = {"captured_utc": "2026-10-18T00:00:00Z", "network_requests": 0}
                snapshot_ref = {
                    "path": "transfer-pending2-v2/batch-01/status-snapshot.json",
                    "sha256": FACTORY.json_sha256(snapshot),
                    "bytes": len(FACTORY.json_bytes(snapshot)),
                    "role": "offline atomic fixture snapshot",
                }
                plan = {"input_bindings": {"status_snapshot": snapshot_ref}, "candidate_count": 2}
                bindings = {"plan_sha256": FACTORY.json_sha256(plan)}
                result = FACTORY.write_batch_atomic(
                    1,
                    {
                        "status-snapshot.json": snapshot,
                        "plan.json": plan,
                        "input-bindings.json": bindings,
                    },
                )
                target = Path(temp) / "batch-01"
                self.assertEqual(result["batch_dir"], FACTORY.rel(target))
                actual_snapshot = target / "status-snapshot.json"
                actual_plan = target / "plan.json"
                self.assertEqual(actual_snapshot.read_bytes(), FACTORY.json_bytes(snapshot))
                self.assertEqual(FACTORY.sha256(actual_snapshot), snapshot_ref["sha256"])
                self.assertEqual(actual_snapshot.stat().st_size, snapshot_ref["bytes"])
                self.assertEqual(FACTORY.sha256(actual_plan), bindings["plan_sha256"])
                self.assertNotIn(b"\r\n", actual_plan.read_bytes())
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
