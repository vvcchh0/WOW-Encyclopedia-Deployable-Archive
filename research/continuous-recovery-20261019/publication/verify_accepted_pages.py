"""Reuse the frozen HTTPS-object verifier with this run's exact accepted delta."""
import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
FROZEN = ROOT / "research/continuous-recovery-20261018/publication/verify_pages_v32.py"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    assert re.fullmatch(r"v[3-9][0-9]", args.version)
    version = args.version
    final = PUB / f"root-{version}-pages-online-acceptance.json"
    assert not final.exists()
    gate = json.loads((PUB / f"root-{version}-local-acceptance.json").read_bytes())
    assert gate["accepted"]
    assert hashlib.sha256(FROZEN.read_bytes()).hexdigest() == "82f9c2bce15c618e33d31bb583192a217a2f419d0e7cf85714f47709d5d09289"
    spec = importlib.util.spec_from_file_location("root_current_run_pages_verifier", FROZEN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = PUB
    module.SITE = ROOT / gate["local_site"]
    module.PUBLISH_REPORT = PUB / f"{version}-pages-publication.json"
    module.PROGRESS_REPORT = PUB / f"{version}-pages-online-progress.json"
    module.FINAL_REPORT = final
    module.OBJECTS = [dict(row, mime=set(row["mime"])) for row in gate["objects"]]
    assert 1 <= len(module.OBJECTS) <= 128
    module.MAX_ATTEMPTS = 2 * len(module.OBJECTS)
    module.MAX_SECONDS = 600
    module.MAX_BODY_BYTES = 64 * 1024 * 1024
    raise SystemExit(module.main())


if __name__ == "__main__":
    main()
