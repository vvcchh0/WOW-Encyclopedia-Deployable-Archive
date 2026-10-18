from __future__ import annotations

import ast
import importlib.util
import pathlib
import tempfile
import unittest


HERE = pathlib.Path(__file__).resolve().parent


def load(name: str, filename: str):
    path = HERE / filename
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load("v33_contract_builder", "build_pages_v33.py")
runner_source = (HERE / "execute_v33.py").read_text(encoding="utf-8")


class V33ContractTests(unittest.TestCase):
    def test_roles_are_exact_and_do_not_infer_other_hosts(self):
        self.assertEqual(builder.role_for_url("http://www.worldofwarcraft.com/news/a.jpg"), "primary")
        self.assertEqual(builder.role_for_capture("http://www.worldofwarcraft.com/news/a.jpg", "20070101000000"), "supplement")
        self.assertEqual(builder.role_for_capture("http://www.worldofwarcraft.com/news/a.jpg", "20080401000000"), "primary")
        self.assertEqual(builder.role_for_capture("http://www.worldofwarcraft.com/news/a.jpg", "20090101000000"), "supplement")
        self.assertEqual(builder.role_for_url("https://www.wowarmory.com/images/icons/21x21/a.png"), "supplement")
        self.assertEqual(builder.role_for_url("http://armory.wow-europe.com/images/icons/class/5.png"), "supplement")
        self.assertEqual(builder.role_for_url("https://www.blizzard.com/war3x/images/screens/concept/a.jpg"), "supplement")
        with self.assertRaises(RuntimeError):
            builder.role_for_url("https://www.wow-europe.com/images/a.jpg")

    def test_temporal_class_keeps_actual_capture_buckets(self):
        self.assertEqual(builder.temporal_class("20070401000000"), "pre_2008")
        self.assertEqual(builder.temporal_class("20080402000000"), "baseline_2008")
        self.assertEqual(builder.temporal_class("20081231235959"), "late_2008")
        self.assertEqual(builder.temporal_class("20130612000000"), "post_2008")

    def test_origin_key_matches_exporter_scheme_independence(self):
        self.assertEqual(
            builder.origin_key("http://www.worldofwarcraft.com/a.jpg?x=1"),
            builder.origin_key("https://worldofwarcraft.com/a.jpg"),
        )

    def test_missing_manifest_is_a_hard_input_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RuntimeError):
                builder.read_json(pathlib.Path(directory) / "absent.json", "source manifest")

    def test_builder_mentions_separate_navigation_and_svg_accounting(self):
        tree = ast.parse((HERE / "build_pages_v33.py").read_text(encoding="utf-8"))
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        self.assertIn("parse_qs", names)
        source = (HERE / "build_pages_v33.py").read_text(encoding="utf-8")
        self.assertIn("navigation_href_recovery", source)
        self.assertIn("missing_image_svg_marker_recovery", source)

    def test_runner_has_no_prepare_path_and_requires_both_go_flags(self):
        self.assertIn("if not args.go or not args.root_export_go", runner_source)
        self.assertNotIn("build_pages_v33.main", runner_source)
        self.assertIn("refusing existing v33 output, partial output, or build receipt", runner_source)


if __name__ == "__main__":
    unittest.main()
