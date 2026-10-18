"""Check that V3 only moves run output and frozen fixture directories."""
import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "research/continuous-recovery-20261016/network/reusable-image-driver-v2/reusable_image_driver.py"
NEW = ROOT / "research/continuous-recovery-20261018/network/reusable-image-driver-v3/reusable_image_driver.py"
OUT = Path(__file__).with_name("root-v3-driver-acceptance.json")

def main():
    assert not OUT.exists()
    old, new = OLD.read_text(encoding="utf-8"), NEW.read_text(encoding="utf-8")
    assert hashlib.sha256(OLD.read_bytes()).hexdigest() == "1faae294465f5e1ad6e2925870890cdb9512bd2251090d533637245ee6a3d8e4"
    # Normalize the three explicitly reviewed directory changes. Requiring an
    # identical full AST also covers transport, acceptance, limits and CLI.
    normalized = new.replace('NETWORK = ROOT / "research" / "continuous-recovery-20261018" / "network"',
                             'NETWORK = ROOT / "research" / "continuous-recovery-20261016" / "network"', 1)
    normalized = normalized.replace('FROZEN_NETWORK = ROOT / "research" / "continuous-recovery-20261016" / "network"\n', '', 1)
    normalized = normalized.replace('FROZEN_NETWORK / "news-shared10"', 'NETWORK / "news-shared10"')
    assert ast.dump(ast.parse(old), include_attributes=False) == ast.dump(ast.parse(normalized), include_attributes=False)
    result = {
        "accepted": True,
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "old_driver_sha256": hashlib.sha256(OLD.read_bytes()).hexdigest(),
        "new_driver_sha256": hashlib.sha256(NEW.read_bytes()).hexdigest(),
        "full_ast_identical_after_directory_normalization": True,
        "approved_changes": ["new run NETWORK directory", "frozen directory constant", "two fixture input paths"],
        "network_requests": 0,
        "execution_authorized_by_this_receipt": False,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))

if __name__ == "__main__":
    main()
