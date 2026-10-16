from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import export_github_pages as pages  # noqa: E402


def _winerror(code: int) -> OSError:
    error = PermissionError(f"synthetic Windows error {code}")
    error.winerror = code  # type: ignore[attr-defined]
    return error


class ExportPromotionTests(unittest.TestCase):
    def _clock(self):
        now = [0.0]
        sleeps: list[float] = []

        def monotonic() -> float:
            return now[0]

        def sleep(seconds: float) -> None:
            sleeps.append(seconds)
            now[0] += seconds

        return monotonic, sleep, sleeps, now

    def test_transient_windows_permission_error_retries_then_promotes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            partial = base / "pages.partial"
            output = base / "pages"
            partial.mkdir()
            (partial / "marker.txt").write_text("complete", encoding="utf-8")
            original_replace = Path.replace
            calls = [0]
            monotonic, sleep, sleeps, _ = self._clock()

            def flaky_replace(source: Path, target: Path) -> Path:
                calls[0] += 1
                if calls[0] == 1:
                    raise _winerror(5)
                return original_replace(source, target)

            pages._promote_partial_output(partial, output, replace=flaky_replace, sleep=sleep, monotonic=monotonic)
            self.assertEqual(calls[0], 2)
            self.assertEqual(sleeps, [0.1])
            self.assertEqual((output / "marker.txt").read_text(encoding="utf-8"), "complete")
            self.assertFalse(partial.exists())

    def test_existing_target_is_refused_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            partial = base / "pages.partial"
            output = base / "pages"
            partial.mkdir()
            output.mkdir()
            (partial / "marker.txt").write_text("partial", encoding="utf-8")
            (output / "marker.txt").write_text("existing", encoding="utf-8")
            with self.assertRaisesRegex(pages.PagesExportError, "refusing to overwrite existing output"):
                pages._promote_partial_output(partial, output)
            self.assertEqual((output / "marker.txt").read_text(encoding="utf-8"), "existing")
            self.assertEqual((partial / "marker.txt").read_text(encoding="utf-8"), "partial")

    def test_non_transient_error_is_not_retried(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            partial = base / "pages.partial"
            output = base / "pages"
            partial.mkdir()
            calls = [0]
            monotonic, sleep, sleeps, _ = self._clock()

            def bad_replace(_source: Path, _target: Path) -> Path:
                calls[0] += 1
                raise _winerror(1234)

            with self.assertRaises(PermissionError):
                pages._promote_partial_output(partial, output, replace=bad_replace, sleep=sleep, monotonic=monotonic)
            self.assertEqual(calls[0], 1)
            self.assertEqual(sleeps, [])
            self.assertTrue(partial.is_dir())

    def test_generic_errno_five_without_winerror_is_not_retried(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            partial = base / "pages.partial"
            output = base / "pages"
            partial.mkdir()
            calls = [0]
            monotonic, sleep, sleeps, _ = self._clock()

            def generic_replace(_source: Path, _target: Path) -> Path:
                calls[0] += 1
                raise OSError(5, "generic errno 5")

            with self.assertRaises(OSError):
                pages._promote_partial_output(partial, output, replace=generic_replace, sleep=sleep, monotonic=monotonic)
            self.assertEqual(calls[0], 1)
            self.assertEqual(sleeps, [])
            self.assertTrue(partial.is_dir())

    def test_target_appearing_after_transient_failure_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            partial = base / "pages.partial"
            output = base / "pages"
            partial.mkdir()
            (partial / "marker.txt").write_text("partial", encoding="utf-8")
            calls = [0]
            monotonic, _unused_sleep, sleeps, now = self._clock()

            def sleep_then_create_target(seconds: float) -> None:
                sleeps.append(seconds)
                now[0] += seconds
                output.mkdir()
                (output / "marker.txt").write_text("existing", encoding="utf-8")

            def transient_then_replace(_source: Path, _target: Path) -> Path:
                calls[0] += 1
                raise _winerror(5)

            with self.assertRaisesRegex(pages.PagesExportError, "refusing to overwrite existing output"):
                pages._promote_partial_output(
                    partial,
                    output,
                    replace=transient_then_replace,
                    sleep=sleep_then_create_target,
                    monotonic=monotonic,
                )
            self.assertEqual(calls[0], 1)
            self.assertEqual((output / "marker.txt").read_text(encoding="utf-8"), "existing")
            self.assertEqual((partial / "marker.txt").read_text(encoding="utf-8"), "partial")

    def test_retry_exhaustion_preserves_complete_partial_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            partial = base / "pages.partial"
            output = base / "pages"
            partial.mkdir()
            (partial / "marker.txt").write_text("complete", encoding="utf-8")
            calls = [0]
            monotonic, sleep, sleeps, now = self._clock()

            def always_denied(_source: Path, _target: Path) -> Path:
                calls[0] += 1
                raise _winerror(32)

            with self.assertRaises(PermissionError):
                pages._promote_partial_output(
                    partial,
                    output,
                    replace=always_denied,
                    sleep=sleep,
                    monotonic=monotonic,
                    max_seconds=0.25,
                )
            self.assertGreater(calls[0], 1)
            self.assertLessEqual(now[0], 0.25)
            self.assertTrue((partial / "marker.txt").is_file())
            self.assertFalse(output.exists())
            self.assertTrue(sleeps)

    def test_pre_promotion_export_error_still_cleans_partial(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            site = base / "offline/site"
            site.mkdir(parents=True)
            missing = site / "missing.xml"
            manifest = base / "offline/build-manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "anchor_timestamp": "20080512210044",
                        "route_aliases": {"/": "/index.xml"},
                        "files": [
                            {
                                "route": "/index.xml",
                                "output_path": "offline/site/missing.xml",
                                "derived_sha256": hashlib.sha256(b"missing").hexdigest(),
                                "derived_length": 7,
                                "mime": "application/xml",
                                "kind": "xml",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output = base / "pages"
            with self.assertRaisesRegex(pages.PagesExportError, "frozen entity missing"):
                pages.export_pages(
                    source_site=site,
                    manifest_path=manifest,
                    output=output,
                    workspace_root=base,
                    min_free_bytes=0,
                )
            self.assertFalse(output.exists())
            self.assertFalse(output.with_name(output.name + ".partial").exists())


if __name__ == "__main__":
    unittest.main()
