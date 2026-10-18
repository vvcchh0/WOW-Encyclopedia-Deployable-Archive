from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BUILDER_PATH = HERE.parent / "build_pages_v33.py"


def load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load("v33_browser_contract_builder", BUILDER_PATH)
runner = load("v33_browser_contract_runner", HERE.parent / "execute_v33.py")


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_binding(path: pathlib.Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)}


class V33BrowserContractTests(unittest.TestCase):
    def test_real_popup24_receipts_validate_all_21_and_audit(self):
        rows = []
        for name in ("root-popup24-batch1", "root-popup24-batch2", "root-popup24-batch3"):
            source_path = ROOT / "research/continuous-recovery-20261018/publication" / f"{name}-source-acceptance.json"
            public_path = ROOT / "research/continuous-recovery-20261018/publication" / f"{name}-public-copy-acceptance.json"
            public = json.loads(public_path.read_text(encoding="utf-8"))
            batch = {
                "id": name,
                "role": "primary",
                "expected_count": len(public["accepted_images"]),
                "expected_bytes": int(public["image_bytes"]),
                "source_acceptance": repo_binding(source_path),
                "public_copy_acceptance": repo_binding(public_path),
            }
            batch_rows, _, _ = builder.validate_batch(batch, len(rows) + 1)
            rows.extend(batch_rows)
        self.assertEqual(len(rows), 21)
        audit = builder.build_source_audit(rows)
        self.assertEqual(audit["source_count"], 21)
        self.assertEqual(audit["primary_count"], 21)
        self.assertEqual(audit["supplement_count"], 0)
        self.assertEqual(audit["total_bytes"], 2_386_986)
        self.assertTrue(audit["all_byte_match"])

    def test_mixed_receipt_derives_roles_from_exact_hosts(self):
        source_a = ROOT / "research/continuous-recovery-20261018/publication/root-popup24-batch1-source-acceptance.json"
        public_a = ROOT / "research/continuous-recovery-20261018/publication/root-popup24-batch1-public-copy-acceptance.json"
        source_b = ROOT / "research/continuous-recovery-20261018/publication/root-static38-batch3-source-acceptance.json"
        public_b = ROOT / "research/continuous-recovery-20261018/publication/root-static38-batch3-public-copy-acceptance.json"
        source_row_a = json.loads(source_a.read_text(encoding="utf-8"))["accepted_images"][0]
        public_row_a = json.loads(public_a.read_text(encoding="utf-8"))["accepted_images"][0]
        source_row_b = json.loads(source_b.read_text(encoding="utf-8"))["accepted_images"][2]
        public_row_b = json.loads(public_b.read_text(encoding="utf-8"))["accepted_images"][2]
        with tempfile.TemporaryDirectory(dir=HERE) as temporary:
            tmp = pathlib.Path(temporary)
            synthetic_source = tmp / "mixed-source.json"
            synthetic_public = tmp / "mixed-public.json"
            synthetic_source.write_text(json.dumps({"accepted": True, "accepted_images": [source_row_a, source_row_b]}), encoding="utf-8")
            synthetic_source_binding = repo_binding(synthetic_source)
            public_rows = [dict(public_row_a), dict(public_row_b)]
            synthetic_public.write_text(json.dumps({
                "accepted": True,
                "copy_mode": "original_bytes",
                "source_acceptance": synthetic_source_binding,
                "image_bytes": int(public_row_a["length"]) + int(public_row_b["length"]),
                "accepted_images": public_rows,
            }), encoding="utf-8")
            batch = {
                "id": "synthetic-mixed",
                "role": "mixed",
                "expected_count": 2,
                "expected_primary_count": 1,
                "expected_supplement_count": 1,
                "expected_bytes": int(public_row_a["length"]) + int(public_row_b["length"]),
                "source_acceptance": synthetic_source_binding,
                "public_copy_acceptance": repo_binding(synthetic_public),
            }
            rows, _, _ = builder.validate_batch(batch, 1)
            self.assertEqual([row["_role"] for row in rows], ["primary", "supplement"])
            audit = builder.build_source_audit(rows)
            self.assertEqual((audit["primary_count"], audit["supplement_count"]), (1, 1))
            self.assertTrue(audit["all_byte_match"])

    def test_clean_exporter_import_uses_tools_path(self):
        exporter = builder.import_exporter()
        self.assertEqual(exporter._OVERLAY_URL_HOSTS, {"www.worldofwarcraft.com", "worldofwarcraft.com"})

    def test_required_bindings_can_bind_a_prepared_fake_input(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temporary:
            fake = pathlib.Path(temporary) / "bound.bin"
            fake.write_bytes(b"v33 fake binding")

            class FakeBuilder:
                ROOT_SOURCE_INPUT_MANIFEST = fake

                @staticmethod
                def frozen_maps():
                    return None, (), (), {}

                @staticmethod
                def load_source_input_manifest(path):
                    return {}, [], []

            builder_names = [
                "V28_BUILDER", "V29_PRIMARY_MAP", "V30_PRIMARY_MAP", "V30_SUPPLEMENT_MAP", "V30_PROVENANCE",
                "V30_BUILD_RECEIPT", "V32_PRIMARY_MAP", "V32_SUPPLEMENT_MAP", "V32_PROVENANCE", "V32_BUILD_RECEIPT",
                "V32_INPUT_ACCEPTANCE", "V32_EXPORT_ACCEPTANCE", "SOURCE_MANIFEST", "ORIGINAL_MANIFEST",
                "GUIDE_PREVIEW_MAP", "GUIDE_COLLECTION_MAP", "EXPORTER", "HISTORICAL_EXHIBITS",
                "ROOT_POPUP_ACCEPTANCE", "ROOT_NAVIGATION_ACCEPTANCE", "ROOT_RETIRED_ACCEPTANCE", "ROOT_MASK_ACCEPTANCE",
            ]
            for name in builder_names:
                setattr(FakeBuilder, name, fake)

            runner_names = [
                "BUILDER_PATH", "PRIMARY_MAP", "SUPPLEMENT_MAP", "IMPACT", "SOURCE_AUDIT",
                "PREPARATION", "PREFLIGHT", "PROPOSAL", "RUNNER_NOTE",
            ]
            original = {name: getattr(runner, name) for name in runner_names}
            try:
                for name in runner_names:
                    setattr(runner, name, fake)
                bindings = runner.required_bindings(FakeBuilder)
            finally:
                for name, value in original.items():
                    setattr(runner, name, value)
            self.assertIn(fake.relative_to(ROOT).as_posix(), bindings)
            self.assertEqual(bindings[fake.relative_to(ROOT).as_posix()], digest(fake))


if __name__ == "__main__":
    unittest.main()
