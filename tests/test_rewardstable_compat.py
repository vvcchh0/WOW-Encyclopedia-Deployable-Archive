from __future__ import annotations

import hashlib
import sys
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import rewardstable_compat  # noqa: E402


BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
FIXTURE = ROOT / "tests/fixtures/rewardstable_source16/rewardstable-new.js"


def _source() -> tuple[str, str]:
    data = FIXTURE.read_bytes()
    source_sha = hashlib.sha256(data).hexdigest()
    if source_sha != rewardstable_compat.SOURCE16_REWARDSTABLE_SOURCE_SHA256:
        raise AssertionError(f"fixture SHA drifted: {source_sha}")
    return data.decode("utf-8"), source_sha


class RewardstableCompatibilityTests(unittest.TestCase):
    def test_source16_rewrites_only_the_two_reviewed_literals(self) -> None:
        source, source_sha = _source()
        output, handled, stats = rewardstable_compat.rewrite_rewardstable_script(
            source,
            rewardstable_compat.REWARDSTABLE_ROUTE,
            source_sha,
            BASE_PATH,
        )
        expected = source.replace(
            "url(images/button-alliance.jpg)",
            "url(/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/rewardstable/images/button-alliance.jpg)",
            1,
        ).replace(
            "url(images/button-horde.jpg)",
            "url(/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/rewardstable/images/button-horde.jpg)",
            1,
        )
        self.assertTrue(handled)
        self.assertEqual(output, expected)
        self.assertEqual(stats["source_variant"], "source16_utf8_bom")
        self.assertEqual(stats["alliance_replacements"], 1)
        self.assertEqual(stats["horde_replacements"], 1)
        self.assertEqual(stats["absolute_button_replacements"], 2)
        self.assertIn(
            'style.backgroundImage = "url(/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/rewardstable/images/button-alliance.jpg)"',
            output,
        )
        self.assertIn(
            'style.backgroundImage = "url(/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/rewardstable/images/button-horde.jpg)"',
            output,
        )

    def test_v46_bomless_body_is_an_explicitly_bound_variant(self) -> None:
        source, _ = _source()
        bomless = source.removeprefix("\ufeff")
        source_sha = hashlib.sha256(bomless.encode("utf-8")).hexdigest()
        self.assertEqual(source_sha, rewardstable_compat.V46_REWARDSTABLE_DERIVED_SHA256)
        output, handled, stats = rewardstable_compat.rewrite_rewardstable_script(
            bomless,
            rewardstable_compat.REWARDSTABLE_ROUTE,
            source_sha,
            BASE_PATH.rstrip("/"),
        )
        self.assertTrue(handled)
        self.assertEqual(stats["source_variant"], "v46_bomless_same_script_body")
        self.assertFalse(output.startswith("\ufeff"))
        self.assertIn("url(/WOW-Encyclopedia-Deployable-Archive/info/basics/factions/rewardstable/images/button-horde.jpg)", output)

    def test_source16_sha_accepts_only_the_known_bomless_decoder_body(self) -> None:
        source, source_sha = _source()
        bomless = source.removeprefix("\ufeff")
        output, handled, stats = rewardstable_compat.rewrite_rewardstable_script(
            bomless,
            rewardstable_compat.REWARDSTABLE_ROUTE,
            source_sha,
            BASE_PATH,
        )
        self.assertTrue(handled)
        self.assertEqual(stats["actual_source_sha256"], rewardstable_compat.V46_REWARDSTABLE_DERIVED_SHA256)
        self.assertEqual(stats["source_variant"], "source16_utf8_bom_decoded")
        self.assertIn("button-alliance.jpg)", output)

    def test_unrelated_route_and_query_cannot_bypass_scope(self) -> None:
        source, source_sha = _source()
        for route in ("/shared/global/functions.js", "info/basics/factions/rewardstable/scripts/other.js", "//info/basics/factions/rewardstable/scripts/rewardstable-new.js", rewardstable_compat.REWARDSTABLE_ROUTE + "?x=1"):
            output, handled, stats = rewardstable_compat.rewrite_rewardstable_script(
                source,
                route,
                "0" * 64,
                BASE_PATH,
            )
            self.assertEqual(output, source)
            self.assertFalse(handled)
            self.assertFalse(stats["handled"])
        self.assertEqual(source_sha, rewardstable_compat.SOURCE16_REWARDSTABLE_SOURCE_SHA256)

    def test_exact_route_rejects_source_drift_and_repeated_pass(self) -> None:
        source, source_sha = _source()
        with self.assertRaisesRegex(rewardstable_compat.RewardstableCompatError, "source SHA mismatch"):
            rewardstable_compat.rewrite_rewardstable_script(
                source,
                rewardstable_compat.REWARDSTABLE_ROUTE,
                "0" * 64,
                BASE_PATH,
            )
        with self.assertRaisesRegex(rewardstable_compat.RewardstableCompatError, "text SHA mismatch"):
            rewardstable_compat.rewrite_rewardstable_script(
                source + "\n",
                rewardstable_compat.REWARDSTABLE_ROUTE,
                source_sha,
                BASE_PATH,
            )
        output, _, _ = rewardstable_compat.rewrite_rewardstable_script(
            source,
            rewardstable_compat.REWARDSTABLE_ROUTE,
            source_sha,
            BASE_PATH,
        )
        with self.assertRaisesRegex(rewardstable_compat.RewardstableCompatError, "text SHA mismatch"):
            rewardstable_compat.rewrite_rewardstable_script(
                output,
                rewardstable_compat.REWARDSTABLE_ROUTE,
                source_sha,
                BASE_PATH,
            )

    def test_invalid_base_path_is_rejected_before_rewrite(self) -> None:
        source, source_sha = _source()
        for base_path in ("https://example.invalid/", "relative/", "/one/../escape/", "/bad?x=1"):
            with self.subTest(base_path=base_path):
                with self.assertRaises(rewardstable_compat.RewardstableCompatError):
                    rewardstable_compat.rewrite_rewardstable_script(
                        source,
                        rewardstable_compat.REWARDSTABLE_ROUTE,
                        source_sha,
                        base_path,
                    )

    def test_literal_count_guard_rejects_ambiguous_source(self) -> None:
        source, source_sha = _source()
        broken = source.replace("url(images/button-horde.jpg)", "url(images/button-horde.jpg)\nurl(images/button-horde.jpg)", 1)
        broken_sha = hashlib.sha256(broken.encode("utf-8")).hexdigest()
        with mock.patch.object(rewardstable_compat, "ACCEPTED_SOURCE_SHA256", frozenset({broken_sha})):
            with self.assertRaisesRegex(rewardstable_compat.RewardstableCompatError, "literal count mismatch"):
                rewardstable_compat.rewrite_rewardstable_script(
                    broken,
                    rewardstable_compat.REWARDSTABLE_ROUTE,
                    broken_sha,
                    BASE_PATH,
                )


if __name__ == "__main__":
    unittest.main()
