from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import create_upload_release as release  # noqa: E402


def _dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class InputsFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix=".release-tools-test-", dir=ROOT)
        self.base = Path(self.temp.name)
        self.archive = self.base / "fixture-archive.bin"
        # Deliberately opaque bytes: no production ZIP is created or consumed.
        self.archive.write_bytes(b"offline synthetic archive input\x00")
        self.archive_sha = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.sidecar = self.base / (self.archive.name + ".sha256")
        self.sidecar.write_text(f"{self.archive_sha}  {self.archive.name}\n", encoding="ascii")
        self.notice = self.base / "NOTICE.md"
        self.notice.write_text("Synthetic test fixture only.\n", encoding="utf-8")
        self.acceptance = self.base / "package-acceptance.json"
        self.acceptance_data = {
            "schema": release.PACKAGE_ACCEPTANCE_SCHEMA,
            "status": "accepted",
            "version": "v55",
            "network_performed": False,
            "archive": {
                "path": self.archive.relative_to(ROOT).as_posix(),
                "sha256": self.archive_sha,
                "bytes": self.archive.stat().st_size,
                "sidecar_sha256": hashlib.sha256(self.sidecar.read_bytes()).hexdigest(),
                "sidecar_bytes": self.sidecar.stat().st_size,
                "member_count": 1,
                "whitelist_exact": True,
                "checksums_exact": True,
                "crc_sha_length_all_passed": True,
                "member_inventory_sha256": "1" * 64,
                "archive_metadata_sha256": "2" * 64,
                "checksum_file_sha256": "3" * 64,
            },
        }
        _dump(self.acceptance, self.acceptance_data)
        self.output = self.base / "owned-output"
        self.config_path = self.base / "release-config.json"
        self.config = {
            "schema": release.CONFIG_SCHEMA,
            "version": "v55",
            "repo": "owner/repo",
            "tag": "archive-20080512-browser-20261022-v55",
            "source_head": "a" * 40,
            "archive": self.archive.relative_to(ROOT).as_posix(),
            "sidecar": self.sidecar.relative_to(ROOT).as_posix(),
            "notice": self.notice.relative_to(ROOT).as_posix(),
            "package_acceptance_receipt": self.acceptance.relative_to(ROOT).as_posix(),
            "output_dir": self.output.relative_to(ROOT).as_posix(),
        }
        _dump(self.config_path, self.config)

    def tearDown(self) -> None:
        self.temp.cleanup()


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0
        self.starts: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


class ReleaseStub:
    def __init__(self, fixture: InputsFixture, clock: FakeClock, *, create_ambiguous: bool = True) -> None:
        self.fixture = fixture
        self.clock = clock
        self.release: dict | None = None
        self.create_ambiguous = create_ambiguous
        self.create_calls = 0
        self.upload_calls: list[tuple[list[str], dict[str, str]]] = []
        self.gh_calls: list[tuple[list[str], dict[str, str]]] = []

    def __call__(self, args, env, timeout):
        if args[0] == "git":
            outputs = {
                ("git", "rev-parse", "--abbrev-ref", "HEAD"): "main\n",
                ("git", "rev-parse", "HEAD"): "a" * 40 + "\n",
                ("git", "rev-parse", "origin/main"): "a" * 40 + "\n",
                ("git", "status", "--porcelain=v1", "--untracked-files=all"): "",
                ("git", "remote", "get-url", "origin"): "https://github.com/owner/repo.git\n",
            }
            return release.CommandResult(0, outputs[tuple(args)])

        self.gh_calls.append((list(args), dict(env)))
        self.clock.starts.append(self.clock.monotonic())
        if args[1] == "api":
            endpoint = args[2]
            if "/releases/tags/" in endpoint:
                if self.release is None:
                    return release.CommandResult(1, stderr="HTTP 404: Not Found")
                return release.CommandResult(0, json.dumps(self.release))
            if "/git/ref/tags/" in endpoint:
                return release.CommandResult(1, stderr="HTTP 404: Not Found")
            raise AssertionError(f"unexpected API endpoint: {endpoint}")

        if args[1:3] == ["release", "create"]:
            self.create_calls += 1
            notes = args[args.index("--notes") + 1]
            self.release = {
                "id": 101,
                "tag_name": self.fixture.config["tag"],
                "target_commitish": self.fixture.config["source_head"],
                "draft": True,
                "body": notes,
                "assets": [],
            }
            if self.create_ambiguous:
                self.create_ambiguous = False
                return release.CommandResult(1, stderr="connection reset by peer")
            return release.CommandResult(0)

        if args[1:3] == ["release", "upload"]:
            self.upload_calls.append((list(args), dict(env)))
            source = Path(args[4])
            payload = source.read_bytes()
            self.release["assets"].append({
                "name": source.name,
                "state": "uploaded",
                "size": len(payload),
                "digest": "sha256:" + hashlib.sha256(payload).hexdigest(),
            })
            return release.CommandResult(0)
        raise AssertionError(f"unexpected command: {args}")


class ConfigTests(InputsFixture):
    def test_config_binds_receipt_archive_sidecar_and_notice(self) -> None:
        inputs = release.load_inputs(self.config_path)
        self.assertEqual(inputs.version, "v55")
        self.assertEqual(set(inputs.expected_assets), {"fixture-archive.bin", "fixture-archive.bin.sha256", "NOTICE.md"})

    def test_sidecar_drift_is_rejected(self) -> None:
        self.sidecar.write_text("0" * 64 + "  fixture-archive.bin\n", encoding="ascii")
        with self.assertRaisesRegex(release.ReleaseToolError, "sidecar does not match"):
            release.load_inputs(self.config_path)

    def test_unaccepted_receipt_is_rejected(self) -> None:
        self.acceptance_data["status"] = "review"
        _dump(self.acceptance, self.acceptance_data)
        with self.assertRaisesRegex(release.ReleaseToolError, "not accepted"):
            release.load_inputs(self.config_path)

    def test_package_receipt_must_attest_all_archive_checks(self) -> None:
        self.acceptance_data["archive"]["checksums_exact"] = False
        _dump(self.acceptance, self.acceptance_data)
        with self.assertRaisesRegex(release.ReleaseToolError, "exact whitelist/checksums"):
            release.load_inputs(self.config_path)


class EnvironmentTests(unittest.TestCase):
    def test_child_environment_clears_ambient_proxies_and_tls_bypass(self) -> None:
        names = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy",
                 "GH_INSECURE", "GIT_SSL_NO_VERIFY", "GH_HOST")
        prior = {name: os.environ.get(name) for name in names}
        try:
            os.environ.update({name: "poison" for name in names})
            direct = release._child_env(use_proxy=False)
            proxy = release._child_env(use_proxy=True)
            self.assertTrue(all(name not in direct for name in names))
            self.assertTrue(all(name not in proxy for name in ("GH_INSECURE", "GIT_SSL_NO_VERIFY", "GH_HOST")))
            self.assertEqual(proxy["HTTPS_PROXY"], release.GH_PROXY_URL)
            self.assertEqual(proxy["https_proxy"], release.GH_PROXY_URL)
            self.assertEqual(direct.get("HTTPS_PROXY"), None)
        finally:
            for name, value in prior.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value


class FlowTests(InputsFixture):
    def test_direct_create_and_upload_path_succeeds_without_proxy(self) -> None:
        inputs = release.load_inputs(self.config_path)
        clock = FakeClock()
        stub = ReleaseStub(self, clock, create_ambiguous=False)
        now_utc = lambda: release.datetime(2026, 10, 22, 10, 0, tzinfo=release.timezone.utc)
        receipt = release.ReleaseCreator(inputs, runner=stub, monotonic=clock.monotonic,
                                         sleeper=clock.sleep, utcnow=now_utc).create_upload()
        self.assertTrue(receipt["accepted"])
        self.assertFalse(receipt["ambiguous_write_recovered_by_readback"])
        self.assertEqual(receipt["proxy_process_attempts"], 0)
        self.assertEqual(stub.create_calls, 1)
        self.assertEqual(len(stub.upload_calls), 3)
        self.assertEqual(receipt["operation_cutoff_utc"], "2026-10-22T14:51:33Z")
        self.assertTrue(receipt["subprocess_timeout_capped_before_cutoff"])

    def test_owned_draft_recovery_uploads_exact_assets_and_never_publishes(self) -> None:
        inputs = release.load_inputs(self.config_path)
        clock = FakeClock()
        stub = ReleaseStub(self, clock)
        now_utc = lambda: release.datetime(2026, 10, 22, 10, 0, tzinfo=release.timezone.utc)
        creator = release.ReleaseCreator(inputs, runner=stub, monotonic=clock.monotonic,
                                         sleeper=clock.sleep, utcnow=now_utc)
        receipt = creator.create_upload()

        self.assertTrue(receipt["accepted"])
        self.assertTrue(receipt["draft"])
        self.assertFalse(receipt["published"])
        self.assertFalse(receipt["published_by_helper"])
        self.assertTrue(receipt["ambiguous_write_recovered_by_readback"])
        self.assertEqual(stub.create_calls, 1)
        self.assertEqual(len(stub.upload_calls), 3)
        self.assertEqual(set(receipt["remote_assets"]), set(inputs.expected_assets))
        self.assertTrue(all("--clobber" not in args for args, _ in stub.upload_calls))
        self.assertTrue(all(proxy.get("HTTP_PROXY") is None for _, proxy in stub.upload_calls))
        self.assertEqual(len(clock.starts), len(stub.gh_calls))
        self.assertEqual(len(receipt["gh_process_events"]), len(stub.gh_calls))
        self.assertEqual(receipt["gh_process_events"][0]["operation"], "api_read")
        self.assertEqual(receipt["gh_process_events"][2]["operation"], "release_create")
        self.assertTrue(all(b - a >= release.MIN_PROCESS_START_INTERVAL - 1e-9
                            for a, b in zip(clock.starts, clock.starts[1:])))
        self.assertIn("internal gh REST subrequests are not individually scheduled",
                      receipt["network_spacing_scope"])
        self.assertTrue((inputs.output_dir / release.INTENT_NAME).is_file())
        receipt_path = inputs.output_dir / release.RECEIPT_NAME
        self.assertTrue(receipt_path.is_file())

        # A matching saved receipt is read-only recovery: it verifies the remote
        # draft and does not create or upload a second time.
        calls_before = (stub.create_calls, len(stub.upload_calls))
        recovered = release.ReleaseCreator(inputs, runner=stub, monotonic=clock.monotonic,
                                            sleeper=clock.sleep, utcnow=now_utc).create_upload()
        self.assertEqual(recovered, receipt)
        self.assertEqual((stub.create_calls, len(stub.upload_calls)), calls_before)

    def test_direct_transport_read_uses_one_process_proxy_with_spacing(self) -> None:
        inputs = release.load_inputs(self.config_path)
        clock = FakeClock()
        calls = []

        def runner(args, env, timeout):
            calls.append((list(args), dict(env)))
            clock.starts.append(clock.monotonic())
            if "HTTP_PROXY" not in env:
                return release.CommandResult(1, stderr="connection reset by peer")
            return release.CommandResult(0, '{"id": 7}')

        creator = release.ReleaseCreator(inputs, runner=runner, monotonic=clock.monotonic,
                                         sleeper=clock.sleep,
                                         utcnow=lambda: release.datetime(2026, 10, 22, 10, 0,
                                                                         tzinfo=release.timezone.utc))
        result = creator._gh_read(["api", "repos/owner/repo/releases/tags/tag"])
        self.assertEqual(result, {"id": 7})
        self.assertEqual(len(calls), 2)
        self.assertNotIn("HTTP_PROXY", calls[0][1])
        self.assertEqual(calls[1][1]["HTTP_PROXY"], release.GH_PROXY_URL)
        self.assertEqual(creator.proxy_attempts, 1)
        self.assertGreaterEqual(clock.starts[1] - clock.starts[0], release.MIN_PROCESS_START_INTERVAL)

    def test_http_429_does_not_trigger_proxy_fallback(self) -> None:
        inputs = release.load_inputs(self.config_path)
        clock = FakeClock()
        calls = []

        def runner(args, env, timeout):
            calls.append((list(args), dict(env)))
            clock.starts.append(clock.monotonic())
            return release.CommandResult(1, stderr="HTTP 429: Too Many Requests")

        creator = release.ReleaseCreator(inputs, runner=runner, monotonic=clock.monotonic,
                                         sleeper=clock.sleep,
                                         utcnow=lambda: release.datetime(2026, 10, 22, 10, 0,
                                                                         tzinfo=release.timezone.utc))
        with self.assertRaisesRegex(release.ReleaseToolError, "without a transport error"):
            creator._gh_read(["api", "repos/owner/repo/releases/tags/tag"])
        self.assertEqual(len(calls), 1)
        self.assertEqual(creator.proxy_attempts, 0)

    def test_process_timeout_is_capped_at_cutoff_and_near_cutoff_refuses_start(self) -> None:
        inputs = release.load_inputs(self.config_path)
        clock = FakeClock()
        observed_timeouts = []

        def runner(args, env, timeout):
            observed_timeouts.append(timeout)
            clock.starts.append(clock.monotonic())
            return release.CommandResult(0, '{"id": 9}')

        creator = release.ReleaseCreator(
            inputs, runner=runner, monotonic=clock.monotonic, sleeper=clock.sleep,
            utcnow=lambda: release.datetime(2026, 10, 22, 14, 51, 25,
                                            tzinfo=release.timezone.utc),
        )
        self.assertEqual(creator._gh_read(["api", "repos/owner/repo/releases/tags/tag"]), {"id": 9})
        self.assertEqual(observed_timeouts, [7.0])

        calls_before = len(observed_timeouts)
        near_cutoff = release.ReleaseCreator(
            inputs, runner=runner, monotonic=clock.monotonic, sleeper=clock.sleep,
            utcnow=lambda: release.datetime(2026, 10, 22, 14, 51, 32, 500000,
                                            tzinfo=release.timezone.utc),
        )
        with self.assertRaisesRegex(release.ReleaseToolError, "too near"):
            near_cutoff._gh_read(["api", "repos/owner/repo/releases/tags/tag"])
        self.assertEqual(len(observed_timeouts), calls_before)

    def test_unowned_existing_draft_is_not_adopted(self) -> None:
        inputs = release.load_inputs(self.config_path)
        clock = FakeClock()
        stub = ReleaseStub(self, clock, create_ambiguous=False)
        stub.release = {
            "id": 303,
            "tag_name": inputs.tag,
            "target_commitish": inputs.source_head,
            "draft": True,
            "body": "release not created by this output intent",
            "assets": [],
        }
        creator = release.ReleaseCreator(inputs, runner=stub, monotonic=clock.monotonic,
                                         sleeper=clock.sleep,
                                         utcnow=lambda: release.datetime(2026, 10, 22, 10, 0,
                                                                         tzinfo=release.timezone.utc))
        with self.assertRaisesRegex(release.ReleaseToolError, "not owned by this output directory"):
            creator.create_upload()
        self.assertEqual(stub.create_calls, 0)
        self.assertFalse((inputs.output_dir / release.INTENT_NAME).exists())


if __name__ == "__main__":
    unittest.main()

