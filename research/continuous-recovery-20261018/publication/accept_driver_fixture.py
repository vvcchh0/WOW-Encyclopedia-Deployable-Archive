"""Verify the fixture-only migration and replay the core offline contract."""
import ast
import copy
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "research/continuous-recovery-20261018"
OLD = ROOT / "research/continuous-recovery-20261016/network/reusable-image-driver-v2/reusable_image_driver.py"
NEW = BASE / "network/reusable-image-driver-v3/reusable_image_driver.py"
PLAN = BASE / "network/neighbors5-v3/plan.json"
OUT = BASE / "publication/root-v3-driver-fixture-adaptation-acceptance.json"

def main():
    assert not OUT.exists()
    before, after = OLD.read_text(encoding="utf-8"), NEW.read_text(encoding="utf-8")
    assert hashlib.sha256(OLD.read_bytes()).hexdigest() == "1faae294465f5e1ad6e2925870890cdb9512bd2251090d533637245ee6a3d8e4"
    normalized = after.replace('NETWORK = ROOT / "research" / "continuous-recovery-20261018" / "network"', 'NETWORK = ROOT / "research" / "continuous-recovery-20261016" / "network"', 1)
    normalized = normalized.replace('FROZEN_NETWORK = ROOT / "research" / "continuous-recovery-20261016" / "network"\n', '', 1)
    trees = [ast.parse(text) for text in (before, normalized)]
    for tree in trees:
        tree.body = [node for node in tree.body if not (isinstance(node, ast.FunctionDef) and node.name == "run_fixtures")]
    assert ast.dump(trees[0], include_attributes=False) == ast.dump(trees[1], include_attributes=False)
    spec = importlib.util.spec_from_file_location("root_checked_driver_v3", NEW)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.configure_from_plan(PLAN)
    original_loader = module.load_and_validate_inputs
    def canonical_synthetic_context():
        plan, bindings = original_loader()
        plan = copy.deepcopy(plan)
        # The old synthetic headers append :80. Supplying an already ported
        # first original would produce :80:80; this only normalizes the
        # synthetic fixture input, after validating the actual untouched plan.
        plan["candidates"][0]["original"] = plan["candidates"][0]["original"].replace(":80/", "/")
        return plan, bindings
    module.load_and_validate_inputs = canonical_synthetic_context
    def no_network(*args, **kwargs):
        raise AssertionError("offline fixture attempted network")
    module._curl_request = no_network
    network = module.NETWORK
    fixture_path = BASE / "network/neighbors5-v3/root-canonical-fixture-results.json"
    assert not fixture_path.exists()
    fixture = module.run_fixtures(fixture_path)
    assert module.NETWORK == network, "fixture boundary not restored"
    assert fixture["all_passed"] and fixture["passed"] == fixture["total"] == 32
    result = {
        "accepted": True,
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "new_driver_sha256": hashlib.sha256(NEW.read_bytes()).hexdigest(),
        "execution_and_acceptance_ast_unchanged": True,
        "fixture_boundary_restored": True,
        "fixture_context": "canonical unported HTTP first URL only for synthetic header generation; actual plan unchanged",
        "fixture_passed": fixture["passed"], "fixture_total": fixture["total"],
        "network_requests": 0,
        "fixture_only_change_review": "Frozen positive cache validation temporarily uses the frozen directory and always restores NETWORK in finally.",
        "plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
        "execution_authorized_by_this_receipt": False,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))

if __name__ == "__main__":
    main()
