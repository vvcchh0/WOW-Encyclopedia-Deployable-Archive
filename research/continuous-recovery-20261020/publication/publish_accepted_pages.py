"""Publish one root-accepted current-run tree through the frozen Pages publisher."""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--publish-root-go", action="store_true")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    assert args.publish_root_go and re.fullmatch(r"v[3-9][0-9]", args.version)
    version = args.version
    report = PUB / f"{version}-pages-publication.json"
    gate_path = PUB / f"root-{version}-local-acceptance.json"
    site = ROOT / f".scratch/pages-resources-20261020-{version}"
    assert not report.exists()
    gate = json.loads(gate_path.read_bytes())
    assert gate["accepted"] and gate["published"] is False and gate["local_site"] == site.relative_to(ROOT).as_posix()
    for item in gate["bindings"]:
        assert SHA(ROOT / item["path"]) == item["sha256"], item["path"]
    for item in gate["objects"]:
        assert SHA(site / item["path"]) == item["sha256"]
        assert (site / item["path"]).stat().st_size == item["bytes"]
    assert shutil.disk_usage(ROOT).free >= 11005853696
    tool = ROOT / "tools/publish_github_pages.py"
    assert SHA(tool) == "e7f4992dfdeae9f83f6771c538c8d55b084316fb2f2e73c92e874df319de9934"

    def git(*values):
        return subprocess.check_output(["git", *values], cwd=ROOT, timeout=45)

    head = git("rev-parse", "HEAD").decode().strip()
    assert git("rev-parse", "origin/main").decode().strip() == head
    assert not git("diff", "--cached", "--name-only").strip()
    assert hashlib.sha256(git("show", "HEAD:" + gate_path.relative_to(ROOT).as_posix())).hexdigest() == SHA(gate_path)
    for name in ("tools/export_github_pages.py", "tools/historical_exhibits.py"):
        assert hashlib.sha256(git("show", "HEAD:" + name)).hexdigest() == SHA(ROOT / name)
    assert git("rev-parse", "gh-pages").decode().strip() == gate["previous_pages_commit"]
    if not args.worker:
        assert datetime.now(timezone.utc) + timedelta(seconds=600) < datetime(2026, 10, 20, 14, 0, tzinfo=timezone.utc)
        # Low-speed push limits apply inside the child; this parent bounds the
        # whole publication call and never automatically repeats it.
        with (PUB / f"{version}-pages-publisher.stdout.log").open("xb") as stdout, (PUB / f"{version}-pages-publisher.stderr.log").open("xb") as stderr:
            process = subprocess.run([sys.executable, "-B", "-X", "utf8", str(Path(__file__).resolve()),
                "--version", version, "--publish-root-go", "--worker"], cwd=ROOT, stdout=stdout, stderr=stderr, timeout=600, check=False)
        assert process.returncode == 0
        result = json.loads(report.read_bytes())
        assert result["status"] == "success"
        print(json.dumps({"status": "success", "version": version, "commit": result["new_commit_sha"]}))
        return
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        os.environ.pop(key, None)
    os.environ["NO_PROXY"] = "*"
    os.environ["GIT_CONFIG_COUNT"] = "3"
    for index, (key, value) in enumerate((("http.proxy", ""), ("http.lowSpeedLimit", "1024"), ("http.lowSpeedTime", "30"))):
        os.environ[f"GIT_CONFIG_KEY_{index}"] = key
        os.environ[f"GIT_CONFIG_VALUE_{index}"] = value
    spec = importlib.util.spec_from_file_location("root_current_run_pages_publisher", tool)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.build_commit(root=ROOT, site=site, branch="gh-pages",
        message=f"Publish {version}: restore archive resources and historical page compatibility",
        report_path=report, push=True)


if __name__ == "__main__":
    main()
