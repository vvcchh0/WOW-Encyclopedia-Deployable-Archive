"""Extract and syntax-check unique executable inline JavaScript in v45 HTML."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import html.parser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time


ROOT = Path(__file__).resolve().parents[4]
SITE = ROOT / ".scratch/pages-resources-20261021-v45"
PROVENANCE = SITE / "export-provenance.json"
NODE = Path(r"C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe")
OUT = Path(__file__).resolve().parent
TEMP = ROOT / ".scratch/test-temp-20261021/inline-js-pass01"
DISK_FLOOR = 11_005_853_696
EXCLUDED_MARKERS = (
    "gallery",
    "screenie",
    "screenshot",
    "screenshots",
    "ssotd",
    "artwork",
)
EXECUTABLE_TYPES = frozenset({"", "text/javascript", "application/javascript"})


def disk_check() -> int:
    free = shutil.disk_usage(ROOT.anchor).free
    if free < DISK_FLOOR:
        raise RuntimeError(f"D: free space below floor: {free} < {DISK_FLOOR}")
    return free


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def excluded_record(record: dict) -> str | None:
    source = str(record.get("source_offline_path") or "").replace("\\", "/")
    if "/site/" in source:
        source = source.split("/site/", 1)[1]
    value = " ".join(
        [str(record.get("route") or ""), str(record.get("output_path") or ""), source]
    ).casefold()
    for marker in EXCLUDED_MARKERS:
        if marker in value:
            return f"explicit gallery/SSOTD/original-art marker: {marker}"
    return None


class InlineScriptParser(html.parser.HTMLParser):
    """Collect script bodies and positions without executing page content."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.scripts: list[dict] = []
        self._current: dict | None = None
        self._script_index = 0

    @staticmethod
    def _attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str | None]:
        return {str(name).casefold(): value for name, value in attrs}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() != "script":
            return
        values = self._attrs(attrs)
        raw_type = str(values.get("type") or "").split(";", 1)[0].strip().casefold()
        executable = "src" not in values and raw_type in EXECUTABLE_TYPES
        self._current = {
            "script_index": self._script_index,
            "line": self.getpos()[0],
            "column": self.getpos()[1],
            "type": raw_type,
            "has_src": "src" in values,
            "executable": executable,
            "chunks": [],
        }
        self._script_index += 1

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._current["chunks"].append(data)

    def handle_entityref(self, name: str) -> None:
        if self._current is not None:
            self._current["chunks"].append("&" + name + ";")

    def handle_charref(self, name: str) -> None:
        if self._current is not None:
            self._current["chunks"].append("&#" + name + ";")

    def handle_comment(self, data: str) -> None:
        if self._current is not None:
            self._current["chunks"].append("<!--" + data + "-->")

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() != "script" or self._current is None:
            return
        current = self._current
        self._current = None
        body = "".join(current.pop("chunks"))
        current["body_length"] = len(body.encode("utf-8"))
        current["body_sha256"] = sha256_bytes(body.encode("utf-8"))
        current.pop("executable", None)
        self.scripts.append(current | {"body": body})


def parse_scripts(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    parser = InlineScriptParser()
    parser.feed(text)
    parser.close()
    return parser.scripts


def load_provenance() -> dict:
    if not PROVENANCE.is_file():
        raise RuntimeError(f"v45 provenance missing: {PROVENANCE}")
    value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("files"), list):
        raise RuntimeError("v45 provenance has no files list")
    return value


def inventory() -> dict:
    provenance = load_provenance()
    html_records = [
        record
        for record in provenance["files"]
        if record.get("kind") in {"html", "menu_html"}
        and record.get("source_offline_path")
    ]
    entries = []
    excluded = []
    missing = []
    unique: dict[str, dict] = {}
    for record in html_records:
        reason = excluded_record(record)
        output_path = SITE / str(record.get("output_path") or "")
        if reason is not None:
            excluded.append({
                "route": record.get("route"),
                "output_path": record.get("output_path"),
                "source_offline_path": record.get("source_offline_path"),
                "reason": reason,
            })
            continue
        if not output_path.is_file():
            missing.append({
                "route": record.get("route"),
                "output_path": record.get("output_path"),
                "reason": "provenance output file missing",
            })
            continue
        try:
            scripts = parse_scripts(output_path)
        except OSError as exc:
            missing.append({
                "route": record.get("route"),
                "output_path": record.get("output_path"),
                "reason": f"cannot read output HTML: {exc}",
            })
            continue
        executable = []
        for script in scripts:
            if script["has_src"] or script["type"] not in EXECUTABLE_TYPES:
                continue
            if not script.get("body", "").strip():
                continue
            occurrence = {
                "route": record.get("route"),
                "output_path": record.get("output_path"),
                "source_offline_path": record.get("source_offline_path"),
                "script_index": script["script_index"],
                "line": script["line"],
                "column": script["column"],
                "body_sha256": script["body_sha256"],
                "body_length": script["body_length"],
            }
            executable.append(occurrence)
            unique.setdefault(script["body_sha256"], {
                "body_sha256": script["body_sha256"],
                "body_length": script["body_length"],
                "occurrences": [],
            })["occurrences"].append(occurrence)
        entries.append({
            "route": record.get("route"),
            "output_path": record.get("output_path"),
            "source_offline_path": record.get("source_offline_path"),
            "output_sha256": sha256_file(output_path),
            "output_length": output_path.stat().st_size,
            "script_tag_count": len(scripts),
            "executable_inline_count": len(executable),
            "executable_inline": executable,
        })
    return {
        "schema": "wow-v45-inline-js-inventory/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "site": ".scratch/pages-resources-20261021-v45",
        "provenance": ".scratch/pages-resources-20261021-v45/export-provenance.json",
        "scope": {
            "provenance_html_records": len(html_records),
            "included_html_records": len(entries),
            "excluded_gallery_or_ssotd_records": len(excluded),
            "missing_output_records": len(missing),
            "exclusion_policy": "route/output/source path contains gallery, screenie, screenshot, ssotd, or artwork",
        },
        "inline": {
            "executable_occurrences": sum(item["executable_inline_count"] for item in entries),
            "unique_body_count": len(unique),
            "json_or_non_executable_and_external_scripts_not_checked": True,
        },
        "entries": entries,
        "excluded": excluded,
        "missing": missing,
        "unique_scripts": list(unique.values()),
    }


def error_fields(stderr: str) -> tuple[str | None, str | None]:
    summary = None
    location = None
    match = re.search(r"SyntaxError:\s*([^\r\n]+)", stderr)
    if match:
        summary = "SyntaxError: " + match.group(1).strip()
    loc = re.search(r":(\d+)(?::(\d+))?\r?\n", stderr)
    if loc:
        location = ":".join(value for value in loc.groups() if value is not None)
    return summary, location


def run_node(body: str, body_sha: str, *, label: str) -> dict:
    TEMP.mkdir(parents=True, exist_ok=True)
    script_path = TEMP / f"{body_sha}.js"
    disk_check()
    script_path.write_bytes(body.encode("utf-8"))
    environment = os.environ.copy()
    environment["TEMP"] = str(TEMP)
    environment["TMP"] = str(TEMP)
    environment["TMPDIR"] = str(TEMP)
    started = time.monotonic()
    status = "pass"
    returncode = None
    summary = None
    location = None
    try:
        completed = subprocess.run(
            [str(NODE), "--check", str(script_path)],
            cwd=str(ROOT),
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
        )
        returncode = completed.returncode
        if returncode != 0:
            status = "fail"
            summary, location = error_fields(completed.stderr)
    except subprocess.TimeoutExpired:
        status = "timeout"
    finally:
        try:
            script_path.unlink()
        except FileNotFoundError:
            pass
    return {
        "label": label,
        "body_sha256": body_sha,
        "status": status,
        "returncode": returncode,
        "duration_ms": round((time.monotonic() - started) * 1000, 1),
        "error_summary": summary,
        "error_location": location,
    }


def source_comparison(occurrence: dict) -> dict:
    source_path = ROOT / str(occurrence["source_offline_path"])
    result = {
        "source_path": occurrence["source_offline_path"],
        "source_exists": source_path.is_file(),
        "source_script_index": occurrence["script_index"],
        "source_body_sha256": None,
        "source_body_length": None,
        "source_node": None,
        "classification": "unknown",
    }
    if not source_path.is_file():
        return result
    try:
        scripts = parse_scripts(source_path)
    except OSError:
        return result
    index = int(occurrence["script_index"])
    source_script = next((item for item in scripts if item["script_index"] == index), None)
    if source_script is None or source_script["has_src"] or source_script["type"] not in EXECUTABLE_TYPES:
        return result
    source_body = str(source_script.get("body") or "")
    if not source_body.strip():
        return result
    source_sha = source_script["body_sha256"]
    result["source_body_sha256"] = source_sha
    result["source_body_length"] = source_script["body_length"]
    cached = run_node(source_body, source_sha, label="source")
    result["source_node"] = {key: cached[key] for key in ("status", "returncode", "duration_ms", "error_summary", "error_location")}
    if cached["status"] == "pass":
        result["classification"] = "conversion_damage"
    elif cached["status"] == "fail":
        result["classification"] = "source_already_bad"
    return result


def run_checks(inv: dict) -> tuple[dict, list[dict]]:
    results = []
    for item in inv["unique_scripts"]:
        occurrence = item["occurrences"][0]
        output_path = SITE / str(occurrence["output_path"])
        scripts = parse_scripts(output_path)
        script = next(
            (entry for entry in scripts if entry["script_index"] == occurrence["script_index"]),
            None,
        )
        if script is None:
            results.append({
                "body_sha256": item["body_sha256"],
                "status": "unknown",
                "returncode": None,
                "duration_ms": 0,
                "error_summary": "inline script could not be re-located",
                "error_location": None,
            })
            continue
        results.append(run_node(str(script["body"]), item["body_sha256"], label="v45"))
    by_sha = {item["body_sha256"]: item for item in results}
    failures = []
    for item in inv["unique_scripts"]:
        result = by_sha[item["body_sha256"]]
        if result["status"] not in {"fail", "timeout"}:
            continue
        for occurrence in item["occurrences"]:
            comparison = source_comparison(occurrence)
            failures.append({
                "body_sha256": item["body_sha256"],
                "body_length": item["body_length"],
                "v45_status": result["status"],
                "v45_error_summary": result["error_summary"],
                "v45_error_location": result["error_location"],
                "occurrence": {
                    key: occurrence[key]
                    for key in ("route", "output_path", "source_offline_path", "script_index", "line", "column")
                },
                "source_comparison": comparison,
            })
    payload = {
        "schema": "wow-v45-inline-js-results/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "node": str(NODE),
        "node_command": "node.exe --check <temporary-inline-script.js>",
        "per_unique_script_timeout_seconds": 5,
        "checked_unique_scripts": len(results),
        "pass": sum(item["status"] == "pass" for item in results),
        "fail": sum(item["status"] == "fail" for item in results),
        "timeout": sum(item["status"] == "timeout" for item in results),
        "unknown": sum(item["status"] == "unknown" for item in results),
        "results": results,
    }
    return payload, failures


def write_json(path: Path, value: dict) -> None:
    disk_check()
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_readme(inv: dict, results: dict, failures: list[dict]) -> None:
    lines = [
        "# v45 non-gallery inline JavaScript syntax pass",
        "",
        "This read-only audit parsed the actual v45 HTML records listed as `html` or `menu_html` in export provenance. Records whose route/output/source path identified an explicit gallery, SSOTD, screenshot, or original-art collection were excluded. External scripts and JSON script blocks were not rechecked here; the prior external-JavaScript audit covered the former.",
        "",
        f"Scope: {inv['scope']['provenance_html_records']} provenance HTML records; {inv['scope']['included_html_records']} included; {inv['scope']['excluded_gallery_or_ssotd_records']} excluded; {inv['scope']['missing_output_records']} missing output records.",
        f"HTMLParser found {inv['inline']['executable_occurrences']} executable inline occurrences and {inv['inline']['unique_body_count']} unique bodies after SHA256 deduplication.",
        f"Node `--check`: {results['checked_unique_scripts']} unique bodies checked; {results['pass']} passed, {results['fail']} failed, {results['timeout']} timed out, {results['unknown']} unknown. Each check had a 5-second timeout and used `.scratch/test-temp-20261021/inline-js-pass01` for temporary files.",
        "",
    ]
    if failures:
        lines.append(f"Failures: {len(failures)} occurrence(s). See `failure-analysis.json` for route, location, hash, and Source16 comparison; no inline source text is reproduced.")
        classifications = {}
        for failure in failures:
            classification = failure["source_comparison"]["classification"]
            classifications[classification] = classifications.get(classification, 0) + 1
        lines.append("Failure classifications: " + ", ".join(f"{key}={value}" for key, value in sorted(classifications.items())) + ".")
    else:
        lines.append("No syntax failures were observed in the deduplicated executable inline set.")
    lines.extend([
        "",
        "Evidence: `inline-inventory.json`, `syntax-results.json`, `failure-analysis.json`, and `audit_inline_js.py`. JavaScript was parsed only; no page script, handler, or network request was executed.",
    ])
    disk_check()
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("inventory", "check"))
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    inv = inventory()
    write_json(OUT / "inline-inventory.json", inv)
    if args.phase == "inventory":
        print(json.dumps({
            "provenance_html_records": inv["scope"]["provenance_html_records"],
            "included_html_records": inv["scope"]["included_html_records"],
            "excluded": inv["scope"]["excluded_gallery_or_ssotd_records"],
            "inline_occurrences": inv["inline"]["executable_occurrences"],
            "unique_bodies": inv["inline"]["unique_body_count"],
        }, sort_keys=True))
        return 0
    results, failures = run_checks(inv)
    write_json(OUT / "syntax-results.json", results)
    write_json(OUT / "failure-analysis.json", {
        "schema": "wow-v45-inline-js-failure-analysis/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "failure_count": len(failures),
        "failures": failures,
    })
    write_readme(inv, results, failures)
    print(json.dumps({
        "checked_unique_scripts": results["checked_unique_scripts"],
        "pass": results["pass"],
        "fail": results["fail"],
        "timeout": results["timeout"],
        "unknown": results["unknown"],
        "failure_occurrences": len(failures),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
