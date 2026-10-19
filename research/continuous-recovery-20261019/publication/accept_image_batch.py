"""Run the frozen independent image checker against this recovery directory."""
import hashlib
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FROZEN_DIR = ROOT / "research/continuous-recovery-20261016/publication"
FROZEN = FROZEN_DIR / "accept_image_batch.py"
EXPECTED_SHA256 = "b324378862e98b078d64b408bd7a59b0600f8868beb453d22b28cf356a543c05"


def main():
    assert hashlib.sha256(FROZEN.read_bytes()).hexdigest() == EXPECTED_SHA256
    sys.path.insert(0, str(FROZEN_DIR))
    spec = importlib.util.spec_from_file_location("frozen_image_checker_20261019", FROZEN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.B = ROOT / "research/continuous-recovery-20261019"
    module.main()


if __name__ == "__main__":
    main()
