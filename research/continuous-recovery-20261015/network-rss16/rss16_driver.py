"""NET-RSS-016: bounded exact RSS archive recovery.

The adapter owns only this batch directory.  It reuses the accepted core3
transport/header parser, the control7 dispatch gate, and RSS006's static RSS
and HTML body observers.  Six targets receive one exact pre-anchor CDX page;
two targets use only the exact captures already declared by the approved plan.
No CDX continuation or redirect follow is performed.
"""

from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
import re
import shutil
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
PLAN = ROOT / "research/continuous-recovery-20261015/rss16-approved-plan.json"
PROPOSAL = ROOT / "research/continuous-recovery-20261015/remaining-rss-next-proposal.json"
NET015_ACCEPTANCE = ROOT / "research/continuous-recovery-20261015/guide-prefix15-acceptance.json"
CORE_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"
GATE_PATH = ROOT / "research/continuous-recovery-20261015/network-control7/control7.py"
RSS6_PATH = ROOT / "research/continuous-recovery-20261015/network-rss6/rss_batch6.py"
PROXY = "http://127.0.0.1:7890"
FROM_TS = "20040101000000"
ANCHOR = "20080512210044"
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
REDIRECT_CODES = {301, 302, 303, 307, 308}
STOP_CODES = {429, 503}
MAX_TARGETS = 8
MAX_ATTEMPTS = 32
WINDOW_SECONDS = 480
MIN_INTERVAL = 1.35
MIN_FREE = 11_005_853_696
MAX_TOTAL = 64 * 1024 * 1024
MAX_ENTITY = 16 * 1024 * 1024
USER_AGENT = "wow-recovery-rss16/20261015"
EXPECTED_PLAN_SHA = "4309afda45a518b9843862369ea063ef83c37d44c71eb430f7ca066350181bb2"
EXPECTED_PROPOSAL_SHA = "966e2e3236fad23023fdd57ee6cbd9177ca3d867ba63f2931dbc1cac5ac1dd4c"
EXPECTED_NET015_ACCEPTANCE_SHA = "d04949368cdaa7868984572c8dd03364bb96409f23b2cbb1d12a386f199b3d9b"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load_module(CORE_PATH, "rss16_core3")
gate_mod = load_module(GATE_PATH, "rss16_control7")
rss6 = load_module(RSS6_PATH, "rss16_rss6_observers")
core.OUT = OUT
core.RAW = RAW
core.PROXY = PROXY
core.USER_AGENT = USER_AGENT
core.MIN_INTERVAL_SECONDS = 0.0
core.MAX_ATTEMPTS = MAX_ATTEMPTS
core.WINDOW_SECONDS = WINDOW_SECONDS
core.MIN_FREE_BYTES = MIN_FREE
core.MAX_TOTAL_BODY_BYTES = MAX_TOTAL
core.MAX_ENTITY_BODY_BYTES = MAX_ENTITY
core.FROM_TIMESTAMP = FROM_TS
core.TO_TIMESTAMP = ANCHOR
core.CDX_COLUMNS = FIELDS
core.CDX_LIMIT = 1000
gate_mod.OUT = OUT
gate_mod.RAW = RAW
gate_mod.INTERVAL_SECONDS = MIN_INTERVAL
rss6.OUT = OUT
rss6.RAW = RAW
rss6.core = core


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def digest_info(path: Path) -> dict[str, Any]:
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    return path.relative_to(OUT).as_posix()


def free_bytes() -> int:
    return int(shutil.disk_usage(OUT).free)


def validate_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    for path in (PLAN, PROPOSAL, NET015_ACCEPTANCE):
        if not path.is_file():
            raise RuntimeError(f"missing approved input: {path}")
    observed = {str(path): sha256_file(path) for path in (PLAN, PROPOSAL, NET015_ACCEPTANCE)}
    if observed[str(PLAN)] != EXPECTED_PLAN_SHA:
        raise RuntimeError(f"RSS016 plan SHA mismatch: {observed[str(PLAN)]}")
    if observed[str(PROPOSAL)] != EXPECTED_PROPOSAL_SHA:
        raise RuntimeError(f"remaining proposal SHA mismatch: {observed[str(PROPOSAL)]}")
    if observed[str(NET015_ACCEPTANCE)] != EXPECTED_NET015_ACCEPTANCE_SHA:
        raise RuntimeError(f"NET015 acceptance SHA mismatch: {observed[str(NET015_ACCEPTANCE)]}")
    plan = read_json(PLAN)
    proposal = read_json(PROPOSAL)
    acceptance = read_json(NET015_ACCEPTANCE)
    if plan.get("task_id") != "NET-RSS-016" or len(plan.get("queue") or []) != MAX_TARGETS:
        raise RuntimeError("RSS016 plan identity or queue size mismatch")
    if acceptance.get("accepted") is not True or acceptance.get("batch_policy_accepted") is not True or acceptance.get("errors") not in (None, []):
        raise RuntimeError("NET015 is not accepted healthy startgate evidence")
    if acceptance.get("report_sha256") != sha256_file(ROOT / "research/continuous-recovery-20261015/network-guide-prefix15/batch-report.json"):
        raise RuntimeError("NET015 acceptance does not bind current report")
    for rank, item in enumerate(plan["queue"], start=1):
        if item.get("rank") != rank or not re.fullmatch(r"/news/rss-\d{2}-\d{4}\.xml", str(item.get("target"))):
            raise RuntimeError(f"RSS016 queue drift at rank {rank}")
        original = str(item.get("exact_original_url") or "")
        if not re.fullmatch(r"http://www\.worldofwarcraft\.com/news/rss-\d{2}-\d{4}\.xml", original):
            raise RuntimeError(f"RSS016 exact original drift at rank {rank}")
        if item.get("operation") == "replay_saved_eligible_capture_without_requery":
            if item.get("cdx_url") is not None or not item.get("replay_url") or not item.get("selected_capture"):
                raise RuntimeError(f"saved replay declaration incomplete at rank {rank}")
        else:
            params = item.get("cdx_query_parameters") or {}
            expected = {"url": original, "matchType": "exact", "from": "20040101", "to": ANCHOR, "output": "json", "fl": ",".join(FIELDS), "limit": "1000", "showResumeKey": "true"}
            if any(str(params.get(key)) != value for key, value in expected.items()):
                raise RuntimeError(f"CDX parameter drift at rank {rank}")
            if not item.get("cdx_url") or item.get("replay_url") is not None:
                raise RuntimeError(f"CDX declaration incomplete at rank {rank}")
    return plan, {
        "proposal": proposal,
        "acceptance": acceptance,
        "input_digests": {str(path.relative_to(ROOT)).replace("\\", "/"): digest_info(path) for path in (PLAN, PROPOSAL, NET015_ACCEPTANCE)},
    }


def build_candidates(plan: dict[str, Any], aux: dict[str, Any]) -> dict[str, Any]:
    targets: list[dict[str, Any]] = []
    for item in plan["queue"]:
        original = item["exact_original_url"]
        match = re.search(r"rss-(\d{2})-(\d{4})\.xml$", original)
        assert match
        target = {
            "rank": item["rank"],
            "target": item["target"],
            "query_original": original,
            "year": int(match.group(2)),
            "month": int(match.group(1)),
            "operation": item["operation"],
            "state": item.get("state"),
            "prior": item.get("prior") or [],
            "menu_evidence": item.get("menu_evidence") or [],
            "reason": item.get("reason"),
            "cdx_query_parameters": item.get("cdx_query_parameters"),
            "cdx_query_url": item.get("cdx_url"),
            "saved_capture": item.get("selected_capture"),
            "saved_replay_url": item.get("replay_url"),
        }
        targets.append(target)
    return {
        "schema": "continuous-wow-net-rss16-candidates/v1",
        "batch_id": "NET-RSS-016",
        "mode": "prepared",
        "generated_utc": utc(),
        "network_requests": 0,
        "approved_plan_sha256": sha256_file(PLAN),
        "input_digests": aux["input_digests"],
        "policy": {
            "target_count": MAX_TARGETS,
            "max_attempts": MAX_ATTEMPTS,
            "network_window_seconds": WINDOW_SECONDS,
            "minimum_dispatch_interval_seconds": MIN_INTERVAL,
            "minimum_free_bytes": MIN_FREE,
            "max_total_body_bytes": MAX_TOTAL,
            "max_entity_body_bytes": MAX_ENTITY,
            "preanchor_from": FROM_TS,
            "preanchor_to": ANCHOR,
            "cdx_pages_per_target": 1,
            "cdx_limit": 1000,
            "collapse": None,
            "automatic_redirects": 0,
            "manual_redirect_follow": 0,
            "continuation_pages": 0,
            "strict_origin": "same scheme/host/path/query; only default ports normalize; bare/www and HTTP/HTTPS stay separate",
            "body_classification": "RSS/Atom/XML parsed from actual body; expanded HTML independently observed; XML extension does not imply XML",
            "integration": "hold accepted entities for later source version; do not modify v11/source/export",
        },
        "targets": targets,
    }


def prepare() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    plan, aux = validate_inputs()
    candidates = build_candidates(plan, aux)
    config = {
        "schema": "continuous-wow-net-rss16-config/v1",
        "batch_id": "NET-RSS-016",
        "mode": "prepared",
        "generated_utc": utc(),
        "inputs": aux["input_digests"],
        "helpers": {"core3": str(CORE_PATH.relative_to(ROOT)).replace("\\", "/"), "control7": str(GATE_PATH.relative_to(ROOT)).replace("\\", "/"), "rss6_observers": str(RSS6_PATH.relative_to(ROOT)).replace("\\", "/"), "curl": r"C:\Windows\System32\curl.exe", "proxy": PROXY},
        "policy": candidates["policy"],
        "network_requests": 0,
        "prepared": True,
        "raw_note": "Raw headers, traces, stderr and bodies remain local. A zero-byte body after no source status is a local placeholder, not source response content.",
    }
    write_json(OUT / "candidates.json", candidates)
    write_json(OUT / "config.json", config)
    print(json.dumps({"mode": "prepared", "targets": MAX_TARGETS, "cdx_targets": sum(x["cdx_query_url"] is not None for x in candidates["targets"]), "known_replay_targets": sum(x["cdx_query_url"] is None for x in candidates["targets"]), "network_requests": 0}, ensure_ascii=False))
    return 0


def canonical_field(value: Any) -> str | None:
    aliases = {"urlkey": "urlkey", "timestamp": "timestamp", "original": "original", "url": "original", "mimetype": "mimetype", "mime": "mimetype", "mime_type": "mimetype", "statuscode": "statuscode", "status": "statuscode", "status_code": "statuscode", "digest": "digest", "length": "length"}
    return aliases.get(str(value).strip().lower().replace("-", "_"))


def parse_rows_with_header(header: list[str], rows: list[Any]) -> tuple[list[dict[str, str]], bool, str | None]:
    positions: dict[str, int] = {}
    for index, value in enumerate(header):
        key = canonical_field(value)
        if key and key not in positions:
            positions[key] = index
    if any(key not in positions for key in FIELDS):
        return [], False, "cdx_header_missing_required_field"
    records: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, list):
            return [], False, "cdx_row_not_array"
        records.append({key: str(row[index]) if index < len(row) else "" for key, index in positions.items()})
    return records, True, None


def parse_cdx_body(body: bytes) -> dict[str, Any]:
    text = body.decode("utf-8", errors="replace")
    if not text.strip() or text.strip().lower() in {"[]", "no captures", "no captures found"}:
        return {"parse_valid": True, "parse_error": None, "header_fields_observed": None, "rows": [], "resume_keys": [], "metadata_records": []}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return {"parse_valid": False, "parse_error": f"json_decode:{type(exc).__name__}", "header_fields_observed": None, "rows": [], "resume_keys": [], "metadata_records": []}
    rows: list[dict[str, str]] = []
    metadata: list[dict[str, Any]] = []
    resume_keys: list[str] = []
    header: list[str] | None = None
    if isinstance(payload, list):
        for index, item in enumerate(payload):
            if isinstance(item, list):
                values = [str(value) for value in item]
                if header is None and [canonical_field(value) for value in values] == FIELDS:
                    header = values
                    metadata.append({"record_index": index, "kind": "header", "value": values})
                elif len(values) == 1 and values[0]:
                    resume_keys.append(values[0])
                    metadata.append({"record_index": index, "kind": "resume_key", "value": values[0]})
                elif header is None:
                    metadata.append({"record_index": index, "kind": "row_before_header", "value": values})
                else:
                    records, valid, error = parse_rows_with_header(header, [item])
                    if not valid:
                        return {"parse_valid": False, "parse_error": error, "header_fields_observed": header, "rows": [], "resume_keys": resume_keys, "metadata_records": metadata}
                    records[0]["record_index"] = str(index)
                    rows.extend(records)
            elif isinstance(item, dict):
                for key in ("resumeKey", "resume_key", "next_resume_key"):
                    if item.get(key):
                        resume_keys.append(str(item[key]))
                        metadata.append({"record_index": index, "kind": "resume_key", "value": str(item[key])})
                metadata.append({"record_index": index, "kind": "metadata", "value": {str(k): str(v) for k, v in item.items() if k not in {"resumeKey", "resume_key", "next_resume_key"}}})
            else:
                metadata.append({"record_index": index, "kind": "metadata", "value": item})
    elif isinstance(payload, dict):
        for key in ("resumeKey", "resume_key", "next_resume_key"):
            if payload.get(key):
                resume_keys.append(str(payload[key]))
        raw_rows = payload.get("records") or payload.get("captures") or payload.get("rows") or []
        if not isinstance(raw_rows, list) or (raw_rows and not all(isinstance(row, dict) for row in raw_rows)):
            return {"parse_valid": False, "parse_error": "cdx_dict_row_shape", "header_fields_observed": None, "rows": [], "resume_keys": resume_keys, "metadata_records": metadata}
        if raw_rows:
            header = list(dict.fromkeys(str(key) for row in raw_rows for key in row.keys()))
            positions = {canonical_field(key): key for key in header if canonical_field(key)}
            if any(key not in positions for key in FIELDS):
                return {"parse_valid": False, "parse_error": "cdx_dict_missing_required_field", "header_fields_observed": header, "rows": [], "resume_keys": resume_keys, "metadata_records": metadata}
            for index, row in enumerate(raw_rows):
                value = {key: str(row.get(raw_key, "")) for key, raw_key in positions.items()}
                value["record_index"] = str(index)
                rows.append(value)
    else:
        return {"parse_valid": False, "parse_error": "cdx_json_shape", "header_fields_observed": None, "rows": [], "resume_keys": [], "metadata_records": []}
    if rows and header is None:
        return {"parse_valid": False, "parse_error": "cdx_header_missing", "header_fields_observed": None, "rows": [], "resume_keys": resume_keys, "metadata_records": metadata}
    return {"parse_valid": True, "parse_error": None, "header_fields_observed": header, "rows": rows, "resume_keys": resume_keys, "unique_resume_keys": list(dict.fromkeys(resume_keys)), "metadata_records": metadata}


def body_for(attempt: dict[str, Any] | None) -> bytes:
    if not attempt or not attempt.get("executed"):
        return b""
    value = str((attempt.get("raw") or {}).get("body") or "")
    if not value:
        return b""
    path = (OUT / value).resolve()
    if OUT.resolve() not in path.parents:
        raise RuntimeError("raw body path escaped RSS016 directory")
    return path.read_bytes() if path.is_file() else b""


def raw_body_for_validation(validation: dict[str, Any]) -> bytes:
    """Read an already persisted body for offline derivation only."""
    value = str(validation.get("raw_body_path") or "")
    if not value:
        return b""
    path = (OUT / value).resolve()
    if OUT.resolve() not in path.parents:
        raise RuntimeError("raw validation body path escaped RSS016 directory")
    return path.read_bytes() if path.is_file() else b""


def public_attempt(value: dict[str, Any]) -> dict[str, Any]:
    output = dict(value)
    output.pop("cdx_records", None)
    output.pop("cdx_valid_records", None)
    return output


def dispatch_ok(state: Any, window_started: float) -> tuple[bool, str | None]:
    if state.stop_reason:
        return False, state.stop_reason
    if state.attempts >= MAX_ATTEMPTS:
        return False, "attempt_limit"
    if time.monotonic() - window_started >= WINDOW_SECONDS:
        return False, "network_window_exhausted"
    if free_bytes() < MIN_FREE:
        return False, "disk_free_below_threshold"
    if state.total_body_bytes >= MAX_TOTAL:
        return False, "total_body_limit"
    return True, None


def issue(url: str, transport: str, kind: str, key: str, state: Any, gate: Any, window_started: float) -> dict[str, Any]:
    ok, reason = dispatch_ok(state, window_started)
    if not ok:
        return {"executed": False, "attempt": state.attempts + 1, "kind": kind, "target_key": key, "transport": transport, "url": url, "unrequested_reason": reason or "limit_before_request"}
    number = state.attempts + 1
    gate_record = gate.before_dispatch(number, transport, key)
    attempt = core.run_request(url, transport, kind, key, state, number)
    attempt["dispatch_utc"] = gate_record["dispatch_utc"]
    attempt["dispatch_monotonic"] = gate_record["dispatch_monotonic"]
    attempt["dispatch_interval_seconds"] = gate_record["interval_since_previous_dispatch_seconds"]
    attempt["gate_persisted_before_transport"] = gate_record["persisted_before_transport"]
    raw = body_for(attempt)
    attempt["local_zero_byte_body_placeholder"] = bool(attempt.get("source_status") is None and not raw)
    attempt["body_is_source_response"] = attempt.get("source_status") is not None
    return attempt


def issue_confirmed(url: str, kind: str, key: str, transport: str, state: Any, gate: Any, window_started: float) -> tuple[list[dict[str, Any]], str]:
    attempts: list[dict[str, Any]] = []
    current = transport
    first = issue(url, current, kind, key, state, gate, window_started)
    attempts.append(first)
    if current == "direct" and first.get("executed") and first.get("transport_error") and not state.stop_reason:
        second = issue(url, "proxy", kind, key, state, gate, window_started)
        attempts.append(second)
        if second.get("executed") and not second.get("transport_error"):
            current = "proxy"
    return attempts, current


def decorate_records(records: list[dict[str, str]], original: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        value = dict(record)
        status = int(str(record.get("statuscode") or "")) if str(record.get("statuscode") or "").isdigit() else None
        value["record_index"] = index
        value["statuscode_int"] = status
        value["within_query_range"] = bool(re.fullmatch(r"\d{14}", str(record.get("timestamp") or "")) and FROM_TS <= str(record.get("timestamp")) <= ANCHOR)
        value["original_match_kind"] = core.original_match_kind(str(record.get("original") or ""), original)
        value["exact_original_match"] = value["original_match_kind"] == "exact"
        value["valid_replay_candidate"] = bool(value["within_query_range"] and value["original_match_kind"] is not None and status in ({200} | REDIRECT_CODES) and core.parse_timestamp(str(record.get("timestamp") or "")) is not None)
        output.append(value)
    return output


def select_latest_200(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    values = [row for row in records if row.get("valid_replay_candidate") and row.get("statuscode_int") == 200]
    return max(values, key=lambda row: str(row.get("timestamp") or "")) if values else None


MONTHS = {name.lower(): number for number, name in enumerate(("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"), start=1)}


class _HtmlEvidenceParser(HTMLParser):
    """Collect only source-labelled article dates and every source h1.

    The archived pages contain both ``posted-date`` spans and duplicate
    ``news-entry-date`` list items.  The posted-date nodes are the primary
    article-date field; the list-item nodes are retained as an independent
    cross-check and used only when a page has no posted-date nodes.  Dates in
    descriptions are collected separately by ``html_month_evidence`` and do
    not participate in the article-month verdict.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[dict[str, Any]] = []
        self.nodes: dict[str, list[dict[str, Any]]] = {"posted": [], "news_entry": [], "h1": []}

    @staticmethod
    def _roles(tag: str, attrs: list[tuple[str, str | None]]) -> list[str]:
        values = dict(attrs)
        tokens: set[str] = set()
        for key in ("class", "id"):
            tokens.update(str(values.get(key) or "").lower().split())
        roles: list[str] = []
        if "posted-date" in tokens:
            roles.append("posted")
        if "news-entry-date" in tokens:
            roles.append("news_entry")
        if tag.lower() == "h1":
            roles.append("h1")
        return roles

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack.append({"tag": tag.lower(), "roles": self._roles(tag, attrs), "attrs": dict(attrs), "parts": []})

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        if not data:
            return
        for node in self.stack:
            if node["roles"]:
                node["parts"].append(data)

    def _emit(self, node: dict[str, Any]) -> None:
        if node.get("emitted") or not node.get("roles"):
            return
        node["emitted"] = True
        text = " ".join("".join(str(value) for value in node["parts"]).split())
        record = {"tag": node["tag"], "text": text, "attrs": node["attrs"]}
        for role in node["roles"]:
            self.nodes[role].append(dict(record))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        index = next((index for index in range(len(self.stack) - 1, -1, -1) if self.stack[index]["tag"] == tag), None)
        if index is None:
            return
        nodes = self.stack[index:]
        self.stack = self.stack[:index]
        for node in nodes:
            self._emit(node)

    def finish(self) -> dict[str, list[dict[str, Any]]]:
        for node in self.stack:
            self._emit(node)
        self.stack.clear()
        return self.nodes


DATE_TOKEN_RE = re.compile(
    r"(?P<named>\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+(?:19|20)\d{2}\b)"
    r"|(?P<iso>\b(?:19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}\b)",
    re.I,
)
NODE_DATE_TOKEN_RE = re.compile(
    r"(?P<named>\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+(?:19|20)\d{2}\b)"
    r"|(?P<iso>\b(?:19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}\b)"
    r"|(?P<mdy>\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b)",
    re.I,
)


def _date_token_value(token: str) -> tuple[int, int, int] | None:
    value = " ".join(token.split()).strip()
    named = re.fullmatch(r"(?i)(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+((?:19|20)\d{2})", value)
    if named:
        return int(named.group(3)), MONTHS[named.group(1).lower()], int(named.group(2))
    iso = re.fullmatch(r"((?:19|20)\d{2})[-/](\d{1,2})[-/](\d{1,2})", value)
    if iso:
        parsed = (int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
        return parsed if 1 <= parsed[1] <= 12 and 1 <= parsed[2] <= 31 else None
    mdy = re.fullmatch(r"(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})", value)
    if mdy:
        year = int(mdy.group(3))
        if year < 100:
            year += 2000 if year <= 68 else 1900
        parsed = (year, int(mdy.group(1)), int(mdy.group(2)))
        return parsed if 1 <= parsed[1] <= 12 and 1 <= parsed[2] <= 31 else None
    return None


def _date_tokens(text: str, pattern: re.Pattern[str]) -> list[tuple[str, tuple[int, int, int]]]:
    values: list[tuple[str, tuple[int, int, int]]] = []
    for match in pattern.finditer(text):
        token = " ".join(match.group(0).split())
        parsed = _date_token_value(token)
        if parsed is not None:
            values.append((token, parsed))
    return values


def _date_evidence(values: list[dict[str, Any]], year: int, month: int) -> dict[str, Any]:
    parsed = [value for value in values if value.get("year") is not None]
    matching = [value for value in parsed if (value["year"], value["month"]) == (year, month)]
    mismatch = [value for value in parsed if (value["year"], value["month"]) != (year, month)]
    month_counts = Counter(f"{value['year']:04d}-{value['month']:02d}" for value in parsed)
    dates = [f"{value['year']:04d}-{value['month']:02d}-{value['day']:02d}" for value in parsed if value.get("day") is not None]
    if not parsed:
        state = "unknown" if not values else "unparseable"
    elif mismatch and matching:
        state = "mixed"
    elif mismatch:
        state = "mismatch"
    elif len(parsed) < len(values):
        state = "mixed"
    else:
        state = "match"
    return {
        "expected_year": year,
        "expected_month": month,
        "date_field_count": len(values),
        "parseable_count": len(parsed),
        "unparseable_count": len(values) - len(parsed),
        "matching_count": len(matching),
        "mismatch_count": len(mismatch),
        "matching_examples": [value["token"] for value in matching[:10]],
        "mismatch_examples": [value["token"] for value in mismatch[:10]],
        "month_counts": dict(sorted(month_counts.items())),
        "date_range": {"min": min(dates), "max": max(dates)} if dates else None,
        "state": state,
    }


def html_month_evidence(body: bytes, observation: dict[str, Any], year: int, month: int) -> dict[str, Any]:
    text = body.decode("utf-8", errors="replace")
    parser = _HtmlEvidenceParser()
    parser.feed(text)
    nodes = parser.finish()
    title = str(observation.get("title") or "")
    title_values: list[dict[str, Any]] = []
    for match in re.finditer(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s*,?\s*((?:19|20)\d{2})\b", title, re.I):
        title_values.append({"token": match.group(0), "year": int(match.group(2)), "month": MONTHS[match.group(1).lower()], "day": None})
    primary_kind = "posted" if nodes["posted"] else "news_entry"
    primary_nodes = nodes[primary_kind]
    posted_values: list[dict[str, Any]] = []
    for node in primary_nodes:
        node_dates = _date_tokens(node["text"], NODE_DATE_TOKEN_RE)
        if node_dates:
            for token, parsed in node_dates:
                posted_values.append({"token": token, "year": parsed[0], "month": parsed[1], "day": parsed[2], "node_type": primary_kind, "tag": node["tag"], "raw_text": node["text"]})
        else:
            posted_values.append({"token": node["text"], "year": None, "month": None, "day": None, "node_type": primary_kind, "tag": node["tag"], "raw_text": node["text"]})
    title_ev = _date_evidence(title_values, year, month)
    posted_ev = _date_evidence(posted_values, year, month)
    event_values: list[dict[str, Any]] = []
    for token, parsed in _date_tokens(text, DATE_TOKEN_RE):
        event_values.append({"token": token, "year": parsed[0], "month": parsed[1], "day": parsed[2]})
    event_ev = {"classification": "event_or_description_date_candidates", "date_field_count": len(event_values), "date_tokens": [value["token"] for value in event_values[:100]], "year_months": [[value["year"], value["month"]] for value in event_values[:100]], "examples": event_values[:20], "note": "Body-wide named/ISO dates are retained as event or description evidence and excluded from the article posted-month verdict."}
    title_mismatch = bool(title_values and any((value["year"], value["month"]) != (year, month) for value in title_values))
    body_match = bool(posted_values and posted_ev["state"] == "match")
    posted_mismatch = posted_ev["state"] in {"mismatch", "mixed"} or bool(posted_ev["mismatch_count"])
    source_anomaly = (
        "title_month_differs_but_posted_date_matches" if title_mismatch and body_match
        else "title_and_posted_month_differ_from_declared_url" if title_mismatch and posted_mismatch
        else "posted_date_month_differs_from_declared_url" if posted_mismatch
        else "title_month_differs_from_declared_url" if title_mismatch
        else None
    )
    return {
        "declared_url_year": year,
        "declared_url_month": month,
        "title": title,
        "title_date_tokens": [value["token"] for value in title_values[:20]],
        "title_year_months": [[value["year"], value["month"]] for value in title_values[:20]],
        "title_month_evidence": title_ev,
        "h1_count": len(nodes["h1"]),
        "h1_titles": [node["text"] for node in nodes["h1"]],
        "posted_date_source": primary_kind if primary_nodes else None,
        "posted_date_node_count": len(nodes["posted"]),
        "news_entry_date_node_count": len(nodes["news_entry"]),
        "posted_date_records": posted_values,
        "posted_or_visible_date_tokens": [value["token"] for value in posted_values[:100]],
        "posted_or_visible_year_months": [[value["year"], value["month"]] for value in posted_values[:100] if value["year"] is not None],
        "posted_date_evidence": posted_ev,
        "article_month_evidence": posted_ev,
        "article_posted_date_count": len(posted_values),
        "article_posted_date_month_counts": posted_ev["month_counts"],
        "article_posted_date_range": posted_ev["date_range"],
        "event_date_evidence": event_ev,
        "event_date_tokens": event_ev["date_tokens"],
        "event_date_year_months": event_ev["year_months"],
        "article_month_matches_url": body_match,
        "source_anomaly": source_anomaly,
    }


def validate_replay(item: dict[str, Any], capture: dict[str, Any], attempt: dict[str, Any] | None) -> tuple[str, str, dict[str, Any] | None]:
    if not attempt or not attempt.get("executed"):
        return "not_requested", (attempt or {}).get("unrequested_reason", "replay_not_requested"), None
    status = attempt.get("source_status")
    if attempt.get("transport_error") or status is None:
        return "transport_error", attempt.get("transport_reason") or "no_source_http_response", None
    if status in STOP_CODES:
        return "rate_limited", f"source_status_{status}", {"retry_after": attempt.get("retry_after")}
    if status in REDIRECT_CODES:
        return "redirect_unfollowed", f"source_status_{status}", {"location": attempt.get("location"), "retry_after": attempt.get("retry_after")}
    if status == 404:
        return "not_archived", "replay_http_404", None
    if status != 200:
        return "http_response", f"source_status_{status}", None
    valid, reason, metrics = rss6.validate_body(attempt, capture, item["year"], item["month"])
    metrics["valid"] = valid
    metrics["validation_reason"] = reason
    if metrics.get("body_format") == "html":
        metrics["html_month_evidence"] = html_month_evidence(body_for(attempt), metrics.get("body_observation") or {}, item["year"], item["month"])
    actual = attempt.get("memento_datetime")
    actual_dt = None
    if actual:
        try:
            actual_dt = datetime.fromisoformat(str(actual).replace("Z", "+00:00")).astimezone(timezone.utc)
        except ValueError:
            actual_dt = None
    capture_dt = core.parse_timestamp(str(capture.get("timestamp") or ""))
    metrics["actual_memento_capture_timestamp_match"] = bool(actual_dt and capture_dt and actual_dt == capture_dt)
    metrics["actual_memento_at_or_before_anchor"] = bool(actual_dt and actual_dt <= datetime.strptime(ANCHOR, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc))
    if not metrics["actual_memento_at_or_before_anchor"]:
        return "invalid_payload", "actual_memento_missing_or_after_anchor", metrics
    if valid and metrics.get("body_format") == "rss_xml":
        return "valid_rss_payload", reason, metrics
    if valid and metrics.get("body_format") == "html":
        return "valid_html_payload", reason, metrics
    if reason == "not_archived_or_error_html":
        return "soft404", reason, metrics
    return "invalid_payload", reason, metrics


def issue_replay(item: dict[str, Any], capture: dict[str, Any], transport: str, state: Any, gate: Any, window_started: float) -> tuple[list[dict[str, Any]], str, str, str, dict[str, Any] | None]:
    url = core.replay_url(capture)
    attempts, confirmed = issue_confirmed(url, "replay", item["query_original"], transport, state, gate, window_started)
    executed = [value for value in attempts if value.get("executed")]
    final = executed[-1] if executed else None
    category, reason, validation = validate_replay(item, capture, final)
    return attempts, confirmed, category, reason, validation


def result_from_query(item: dict[str, Any], query_attempts: list[dict[str, Any]], transport: str, state: Any, gate: Any, window_started: float) -> tuple[dict[str, Any], str]:
    executed = [value for value in query_attempts if value.get("executed")]
    final_query = executed[-1] if executed else None
    body = body_for(final_query)
    parsed = {"parse_valid": False, "parse_error": "no_source_200_response", "header_fields_observed": None, "rows": [], "resume_keys": [], "metadata_records": []}
    if final_query and final_query.get("source_status") == 200 and not final_query.get("transport_error"):
        parsed = parse_cdx_body(body)
    records = decorate_records(parsed.get("rows") or [], item["query_original"]) if parsed.get("parse_valid") else []
    eligible = [row for row in records if row.get("valid_replay_candidate") and row.get("statuscode_int") == 200]
    selected = select_latest_200(records)
    replays: list[dict[str, Any]] = []
    confirmed = transport
    category: str
    reason: str
    validation: dict[str, Any] | None = None
    if not final_query:
        category, reason = "not_requested", "query_not_executed"
    elif final_query.get("transport_error"):
        category, reason = "transport_error", final_query.get("transport_reason") or "curl_or_tls_failure"
    elif final_query.get("source_status") in STOP_CODES:
        category, reason = "rate_limited", f"source_status_{final_query.get('source_status')}"
    elif not parsed.get("parse_valid"):
        category, reason = "cdx_invalid", parsed.get("parse_error") or "cdx_parse_failed"
    elif not records:
        category, reason = "cdx_empty_in_scoped_window", "no_index_rows_in_declared_preanchor_window"
    elif selected is None:
        category, reason = "cdx_rows_without_valid_200", "index_rows_without_same_origin_status_200_capture"
    else:
        replay_attempts, confirmed, category, reason, validation = issue_replay(item, selected, confirmed, state, gate, window_started)
        replays.append({"capture": selected, "replay_url": core.replay_url(selected), "attempts": [public_attempt(value) for value in replay_attempts], "category": category, "reason": reason, "validation": validation})
    query_status = final_query.get("source_status") if final_query else None
    result = make_result(item, query_attempts, records, eligible, selected, replays, category, reason, validation, query_status, final_query, query_body=body, query_parse=parsed)
    return result, confirmed


def make_result(item: dict[str, Any], query_attempts: list[dict[str, Any]], records: list[dict[str, Any]], eligible: list[dict[str, Any]], selected: dict[str, Any] | None, replays: list[dict[str, Any]], category: str, reason: str, validation: dict[str, Any] | None, query_status: Any, final_query: dict[str, Any] | None, query_body: bytes = b"", query_parse: dict[str, Any] | None = None) -> dict[str, Any]:
    final_replay_attempt = None
    for replay in replays:
        executed = [value for value in replay.get("attempts") or [] if value.get("executed")]
        if executed:
            final_replay_attempt = executed[-1]
    metrics = validation or {}
    return {
        "rank": item["rank"], "target": item["target"], "query_original": item["query_original"], "year": item["year"], "month": item["month"], "operation": item["operation"], "source_menu": item["menu_evidence"], "query_url": item["cdx_query_url"],
        "cdx": {"query_performed": bool(query_attempts), "source_status": query_status, "source_response_count": sum(value.get("source_status") is not None for value in query_attempts), "capture_index_count": len(records), "eligible_status_200_count": len(eligible), "redirect_index_count": sum(value.get("statuscode_int") in REDIRECT_CODES for value in records), "capture_records": records, "selected_capture": selected, "other_origin_metadata": core.other_origin_metadata(records, item["query_original"]) if records else {}, "attempts": [public_attempt(value) for value in query_attempts], "header_fields_observed": (query_parse or {}).get("header_fields_observed"), "resume_keys_observed": (query_parse or {}).get("resume_keys") or [], "resume_key_used": None, "continuation_followed": False, "body_bytes": len(query_body), "body_sha256": hashlib.sha256(query_body).hexdigest() if query_body else None, "index_distribution": {"statuscode": dict(sorted(Counter(str(value.get("statuscode") or "") for value in records).items())), "mimetype": dict(sorted(Counter(str(value.get("mimetype") or "") for value in records).items())), "origin_match_kind": dict(sorted(Counter(str(value.get("original_match_kind") or "") for value in records).items()))}},
        "selected_capture": selected, "replay_attempt_count": sum(sum(value.get("executed", False) for value in replay.get("attempts") or []) for replay in replays), "replay_source_response_count": sum(sum(value.get("source_status") is not None for value in replay.get("attempts") or []) for replay in replays), "replay_hops": replays, "category": category, "reason": reason, "actual_memento": metrics.get("actual_memento") if metrics else None, "source_status": metrics.get("source_status") if metrics else None, "content_type": metrics.get("content_type") if metrics else None, "body_bytes": metrics.get("body_bytes", 0) if metrics else 0, "body_sha256": metrics.get("body_sha256") if metrics else None, "validation": validation, "entity_valid": category in {"valid_rss_payload", "valid_html_payload"}, "unrequested_reason": reason if category in {"not_requested", "cdx_empty_in_scoped_window", "cdx_rows_without_valid_200", "transport_error"} and not replays else None,
    }


def known_replay_result(item: dict[str, Any], transport: str, state: Any, gate: Any, window_started: float) -> tuple[dict[str, Any], str]:
    capture = dict(item["saved_capture"] or {})
    capture.setdefault("record_index", capture.get("record_index", 0))
    attempts, confirmed, category, reason, validation = issue_replay(item, capture, transport, state, gate, window_started)
    replay = {"capture": capture, "replay_url": item["saved_replay_url"], "attempts": [public_attempt(value) for value in attempts], "category": category, "reason": reason, "validation": validation}
    result = make_result(item, [], [], [], capture, [replay], category, reason, validation, None, None)
    result["cdx"]["query_performed"] = False
    result["cdx"]["query_url"] = None
    result["cdx"]["saved_capture_source"] = "rss16-approved-plan.selected_capture"
    return result, confirmed


def source_map(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for result in results:
        if not result.get("entity_valid"):
            continue
        capture = result.get("selected_capture") or {}
        metrics = result.get("validation") or {}
        observation = metrics.get("body_observation") or {}
        entries.append({"target": result["target"], "query_original": result["query_original"], "captured_original": capture.get("original"), "actual_memento": result.get("actual_memento"), "source_status": result.get("source_status"), "content_type": result.get("content_type"), "body_bytes": result.get("body_bytes"), "body_sha256": result.get("body_sha256"), "cdx_digest": capture.get("digest"), "cdx_digest_calculated": metrics.get("cdx_digest_calculated"), "cdx_digest_match": metrics.get("cdx_digest_match"), "raw_body_path": metrics.get("raw_body_path"), "raw_headers_path": metrics.get("raw_headers_path"), "capture_timestamp": capture.get("timestamp"), "capture_mimetype": capture.get("mimetype"), "cdx_length": metrics.get("cdx_length"), "body_format": metrics.get("body_format"), "rss_observation": observation if metrics.get("body_format") == "rss_xml" else None, "html_observation": observation if metrics.get("body_format") == "html" else None, "html_month_evidence": metrics.get("html_month_evidence"), "action": "hold for parent review; entity remains only in this batch raw directory"})
    return entries


def render_summary(report: dict[str, Any], entries: list[dict[str, Any]]) -> tuple[dict[str, Any], str]:
    targets = []
    for result in report["results"]:
        validation = result.get("validation") or {}
        observation = validation.get("body_observation") or {}
        month_evidence = validation.get("html_month_evidence") or observation.get("month_evidence")
        targets.append({"rank": result["rank"], "target": result["target"], "query_original": result["query_original"], "operation": result["operation"], "category": result["category"], "reason": result["reason"], "cdx_source_status": result["cdx"].get("source_status"), "capture_index_count": result["cdx"].get("capture_index_count"), "eligible_status_200_count": result["cdx"].get("eligible_status_200_count"), "redirect_index_count": result["cdx"].get("redirect_index_count"), "selected_capture_timestamp": (result.get("selected_capture") or {}).get("timestamp"), "actual_memento": result.get("actual_memento"), "body_format": validation.get("body_format"), "title": observation.get("title"), "item_count": observation.get("item_count"), "month_evidence": month_evidence, "article_month_evidence": (month_evidence or {}).get("article_month_evidence"), "posted_date_count": (month_evidence or {}).get("article_posted_date_count"), "posted_date_range": (month_evidence or {}).get("article_posted_date_range"), "posted_date_month_counts": (month_evidence or {}).get("article_posted_date_month_counts"), "h1_count": (month_evidence or {}).get("h1_count"), "event_date_evidence": (month_evidence or {}).get("event_date_evidence"), "source_anomaly": (validation.get("html_month_evidence") or {}).get("source_anomaly"), "body_bytes": result.get("body_bytes", 0), "body_sha256": result.get("body_sha256")})
    summary = {"schema": "continuous-wow-net-rss16-sanitized-summary/v1", "batch_id": "NET-RSS-016", "mode": "executed", "started_utc": report["started_utc"], "request_window_finished_utc": report["request_window_finished_utc"], "finished_utc": report["finished_utc"], "report_updated_utc": report["report_updated_utc"], "network_requests": report["transport_attempt_count"], "source_response_count": report["source_response_count"], "failed_attempt_count": report["failed_attempt_count"], "target_count": len(targets), "cdx_target_count": report["cdx_target_count"], "known_replay_target_count": report["known_replay_target_count"], "capture_index_count": report["capture_index_count"], "valid_payload_count": report["valid_entity_count"], "total_body_bytes": report["total_body_bytes"], "payload_body_bytes": report["payload_body_bytes"], "category_counts": report["category_counts"], "stop_reason": report["stop_reason"], "confirmed_transport": report.get("confirmed_transport") or (report.get("transport") or {}).get("confirmed_transport"), "gate_validation": report["gate_validation"], "disk_free_bytes_before": report["preflight"]["disk_free_bytes_before"], "disk_free_bytes_after": report["preflight"]["disk_free_bytes_after"], "targets": targets, "valid_payloads": entries, "scope_note": "CDX classifications are limited to the declared exact pre-anchor requests; known replays are limited to the two approved captures. No all-time absence claim is made.", "raw_evidence_note": "Raw headers, traces, stderr and bodies remain local. Zero-byte no-response bodies are local placeholders, not source content; CONNECT responses are excluded; CDX length is index metadata."}
    lines = ["# NET-RSS-016 sanitized summary", "", f"- Window: `{report['started_utc']}` to `{report['request_window_finished_utc']}`; report updated `{report['report_updated_utc']}`.", f"- Targets: {len(targets)} ({report['cdx_target_count']} CDX, {report['known_replay_target_count']} saved replays); attempts {report['transport_attempt_count']}; source responses {report['source_response_count']}; CDX rows {report['capture_index_count']}; valid payloads {report['valid_entity_count']}.", f"- Body bytes total `{report['total_body_bytes']}`, valid payloads `{report['payload_body_bytes']}`; stop `{report['stop_reason']}`.", f"- Gate min dispatch `{report['gate_validation']['min_dispatch_interval_seconds']}`, min request-start `{report['gate_validation']['min_request_start_interval_seconds']}`, accepted `{report['gate_validation']['batch_policy_accepted']}`.", "", "| Rank | Target | Operation | Category | Format | CDX rows | Selected | Month/title evidence |", "|---:|---|---|---|---|---:|---|---|"]
    for target in targets:
        month = target.get("month_evidence") or {}
        evidence = target.get("source_anomaly") or month.get("state") or month.get("article_month_evidence", {}).get("state") or month.get("posted_date_evidence", {}).get("state") or month.get("title_month_evidence", {}).get("state") or "unknown"
        lines.append(f"| {target['rank']} | `{target['target']}` | `{target['operation']}` | `{target['category']}` | `{target.get('body_format') or ''}` | {target.get('capture_index_count') or 0} | `{target.get('selected_capture_timestamp') or ''}` | `{evidence}` |")
    for target in targets:
        if target.get("body_format") != "html":
            continue
        event_tokens = ((target.get("event_date_evidence") or {}).get("date_tokens") or [])[:5]
        lines.append(f"- HTML `{target['target']}` full-source evidence: h1 `{target.get('h1_count') or 0}`, posted-date `{target.get('posted_date_count') or 0}`, months `{json.dumps(target.get('posted_date_month_counts') or {}, ensure_ascii=False, sort_keys=True)}`, range `{json.dumps(target.get('posted_date_range'), ensure_ascii=False, sort_keys=True)}`; event/description date candidates retained separately `{json.dumps(event_tokens, ensure_ascii=False)}`.")
    lines.extend(["", "No CDX continuation or redirect follow was performed. Accepted entities remain isolated for parent review and were not integrated."])
    return summary, "\n".join(lines) + "\n"


def execute() -> int:
    if not (OUT / "candidates.json").is_file() or not (OUT / "config.json").is_file():
        raise RuntimeError("run --prepare before --execute")
    if (OUT / "batch-report.json").exists():
        raise RuntimeError("refusing to repeat RSS016 after batch-report.json exists")
    plan, aux = validate_inputs()
    candidates = read_json(OUT / "candidates.json")
    if candidates.get("approved_plan_sha256") != EXPECTED_PLAN_SHA:
        raise RuntimeError("candidate plan digest mismatch")
    disk_before = free_bytes()
    if disk_before < MIN_FREE:
        raise RuntimeError(f"D free space below floor: {disk_before}")
    started_utc = utc()
    window_started = time.monotonic()
    state = core.RunState(window_started)
    journal = {"schema": "continuous-wow-net-rss16-dispatch-log/v1", "batch_id": "NET-RSS-016", "simulation": False, "policy": {"minimum_dispatch_interval_seconds": MIN_INTERVAL, "max_attempts": MAX_ATTEMPTS, "network_window_seconds": WINDOW_SECONDS, "redirects": 0}, "disk_preflight": {"checked_utc": utc(), "disk_free_bytes": disk_before, "minimum_free_bytes": MIN_FREE}, "dispatches": []}
    gate = gate_mod.GateState(datetime.now(timezone.utc) - timedelta(seconds=1), journal_path=OUT / "dispatch-log.json", journal=journal)
    gate.persist()
    results: list[dict[str, Any]] = []
    transport = "direct"
    try:
        for item in candidates["targets"]:
            if state.stop_reason:
                results.append({"rank": item["rank"], "target": item["target"], "query_original": item["query_original"], "year": item["year"], "month": item["month"], "operation": item["operation"], "source_menu": item["menu_evidence"], "query_url": item["cdx_query_url"], "cdx": {"query_performed": False, "source_status": None, "source_response_count": 0, "capture_index_count": 0, "eligible_status_200_count": 0, "redirect_index_count": 0, "capture_records": [], "selected_capture": None, "attempts": [], "resume_keys_observed": [], "resume_key_used": None, "continuation_followed": False}, "selected_capture": None, "replay_attempt_count": 0, "replay_source_response_count": 0, "replay_hops": [], "category": "not_requested", "reason": state.stop_reason, "actual_memento": None, "source_status": None, "content_type": None, "body_bytes": 0, "body_sha256": None, "validation": None, "entity_valid": False, "unrequested_reason": state.stop_reason})
                continue
            if item["cdx_query_url"] is None:
                result, transport = known_replay_result(item, transport, state, gate, window_started)
            else:
                query_attempts, transport = issue_confirmed(item["cdx_query_url"], "cdx", item["query_original"], transport, state, gate, window_started)
                result, transport = result_from_query(item, query_attempts, transport, state, gate, window_started)
            results.append(result)
            if state.stop_reason:
                continue
    finally:
        postflight = gate_mod.persist_postflight(gate, state.attempts, free_fn=free_bytes)
    request_window_finished = utc()
    disk_after = free_bytes()
    dispatch_intervals = [value.get("interval_since_previous_dispatch_seconds") for value in gate.dispatches if value.get("interval_since_previous_dispatch_seconds") is not None]
    starts: list[float] = []
    all_attempts: list[dict[str, Any]] = []
    for result in results:
        all_attempts.extend(result.get("cdx", {}).get("attempts") or [])
        for replay in result.get("replay_hops") or []:
            all_attempts.extend(replay.get("attempts") or [])
    for attempt in all_attempts:
        if attempt.get("started_utc"):
            starts.append(datetime.fromisoformat(str(attempt["started_utc"]).replace("Z", "+00:00")).timestamp())
    starts.sort()
    start_intervals = [starts[index] - starts[index - 1] for index in range(1, len(starts))]
    gate_validation = {"min_dispatch_interval_seconds": min(dispatch_intervals, default=None), "min_request_start_interval_seconds": min(start_intervals, default=None), "required_minimum_seconds": MIN_INTERVAL, "dispatch_intervals_compliant": all(value >= MIN_INTERVAL for value in dispatch_intervals), "request_start_intervals_compliant": all(value >= MIN_INTERVAL for value in start_intervals), "batch_policy_accepted": all(value >= MIN_INTERVAL for value in dispatch_intervals) and all(value >= MIN_INTERVAL for value in start_intervals), "dispatch_count": len(gate.dispatches)}
    entries = source_map(results)
    category_counts = dict(sorted(Counter(str(result.get("category")) for result in results).items()))
    payload_bytes = sum(int(entry.get("body_bytes") or 0) for entry in entries)
    report = {"schema": "continuous-wow-net-rss16-batch-report/v1", "batch_id": "NET-RSS-016", "mode": "executed", "started_utc": started_utc, "request_window_finished_utc": request_window_finished, "finished_utc": request_window_finished, "report_updated_utc": utc(), "inputs": {"approved_plan": digest_info(PLAN), "candidates": digest_info(OUT / "candidates.json"), **aux["input_digests"]}, "policy": candidates["policy"], "transport": {"confirmed_transport": transport, "curl": r"C:\Windows\System32\curl.exe", "proxy": PROXY, "tls_verification": "curl default verification enabled"}, "confirmed_transport": transport, "preflight": {"disk_free_bytes_before": disk_before, "disk_free_bytes_after": disk_after, "minimum_free_bytes": MIN_FREE}, "postflight": postflight, "target_count": len(results), "unique_target_count": len({result["query_original"] for result in results}), "cdx_target_count": sum(result["cdx"].get("query_performed") for result in results), "known_replay_target_count": sum(result["operation"] == "replay_saved_eligible_capture_without_requery" for result in results), "category_counts": category_counts, "transport_attempt_count": state.attempts, "source_request_count": state.attempts, "failed_attempt_count": state.failed_attempts, "source_response_count": state.source_responses, "cdx_source_response_count": sum(result["cdx"].get("source_response_count", 0) for result in results), "replay_source_response_count": sum(result.get("replay_source_response_count", 0) for result in results), "capture_index_count": sum(result["cdx"].get("capture_index_count", 0) for result in results), "valid_entity_count": len(entries), "total_body_bytes": state.total_body_bytes, "payload_body_bytes": payload_bytes, "stop_reason": state.stop_reason or "completed", "stop_detail": state.stop_detail, "rate_limit": state.rate_limit, "gate_validation": gate_validation, "resume_key_policy": {"observed_saved": True, "used": False, "continuation_pages_requested": 0}, "dispatch_log": relative(OUT / "dispatch-log.json"), "results": results, "raw_evidence_note": "Raw headers, traces, stderr and bodies remain only below this batch raw directory. A zero-byte no-response body is a local placeholder, not source content; CONNECT is excluded; CDX length is index metadata, not payload bytes."}
    write_json(OUT / "batch-report.json", report)
    write_json(OUT / "payload-source-map.json", {"schema": "continuous-wow-net-rss16-payload-source-map/v1", "batch_id": "NET-RSS-016", "entries": entries})
    redirects: list[dict[str, Any]] = []
    for result in results:
        for row in result["cdx"].get("capture_records") or []:
            if row.get("statuscode_int") in REDIRECT_CODES:
                redirects.append({"evidence_type": "cdx_index_redirect_row", "target": result["target"], "timestamp": row.get("timestamp"), "original": row.get("original"), "statuscode": row.get("statuscode"), "mimetype": row.get("mimetype"), "action": "index evidence only; no replay/follow"})
        for hop in result.get("replay_hops") or []:
            for attempt in hop.get("attempts") or []:
                if attempt.get("source_status") in REDIRECT_CODES:
                    redirects.append({"evidence_type": "replay_redirect", "target": result["target"], "source_status": attempt.get("source_status"), "location": attempt.get("location"), "action": "redirect observed; no follow"})
    write_json(OUT / "redirect-evidence.json", {"schema": "continuous-wow-net-rss16-redirect-evidence/v1", "entries": redirects})
    summary, markdown = render_summary(report, entries)
    write_json(OUT / "sanitized-summary.json", summary)
    (OUT / "sanitized-summary.md").write_text(markdown, encoding="utf-8")
    print(json.dumps({"mode": "executed", "attempts": state.attempts, "source_responses": state.source_responses, "cdx_rows": report["capture_index_count"], "valid_entities": len(entries), "categories": category_counts, "stop_reason": report["stop_reason"], "min_dispatch_interval": gate_validation["min_dispatch_interval_seconds"], "min_request_start_interval": gate_validation["min_request_start_interval_seconds"]}, ensure_ascii=False))
    return 0


def rebuild_offline() -> int:
    """Rebuild derived summaries and HTML month evidence; never network."""
    report_path = OUT / "batch-report.json"
    map_path = OUT / "payload-source-map.json"
    if not report_path.is_file() or not map_path.is_file():
        raise RuntimeError("cannot rebuild before report and source map exist")
    report = read_json(report_path)
    report["confirmed_transport"] = report.get("confirmed_transport") or (report.get("transport") or {}).get("confirmed_transport")
    corrected_targets: list[str] = []
    for result in report.get("results") or []:
        validation = result.get("validation") or {}
        if validation.get("body_format") != "html":
            continue
        body = raw_body_for_validation(validation)
        if not body:
            raise RuntimeError(f"missing persisted HTML body for offline correction: {result.get('target')}")
        validation["html_month_evidence"] = html_month_evidence(body, validation.get("body_observation") or {}, int(result["year"]), int(result["month"]))
        corrected_targets.append(str(result.get("target")))
    entries_envelope = read_json(map_path)
    entries = entries_envelope.get("entries") or []
    evidence_by_target = {str(result.get("target")): (result.get("validation") or {}).get("html_month_evidence") for result in report.get("results") or []}
    for entry in entries:
        evidence = evidence_by_target.get(str(entry.get("target")))
        if evidence is None:
            continue
        entry["html_month_evidence"] = evidence
        entry["article_month_evidence"] = evidence.get("article_month_evidence")
        entry["posted_date_count"] = evidence.get("article_posted_date_count")
        entry["posted_date_range"] = evidence.get("article_posted_date_range")
        entry["posted_date_month_counts"] = evidence.get("article_posted_date_month_counts")
        entry["h1_count"] = evidence.get("h1_count")
        entry["event_date_evidence"] = evidence.get("event_date_evidence")
    correction = {"performed": True, "network_requests": 0, "reason": "posted-date/news-entry-date semantic correction; event/description dates separated from article posted month", "corrected_html_target_count": len(corrected_targets), "corrected_targets": corrected_targets, "raw_unchanged": True, "journal_unchanged": True}
    report["report_updated_utc"] = utc()
    report["offline_rebuild"] = correction
    write_json(report_path, report)
    entries_envelope["entries"] = entries
    entries_envelope["offline_rebuild"] = correction
    write_json(map_path, entries_envelope)
    summary, markdown = render_summary(report, entries)
    summary["offline_rebuild"] = correction
    write_json(OUT / "sanitized-summary.json", summary)
    (OUT / "sanitized-summary.md").write_text(markdown, encoding="utf-8")
    print(json.dumps({"mode": "offline_rebuild", "network_requests": 0, "confirmed_transport": report["confirmed_transport"], "corrected_targets": corrected_targets, "report_updated_utc": report["report_updated_utc"]}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    if sum(bool(value) for value in (args.prepare, args.execute, args.rebuild)) != 1:
        parser.error("choose exactly one of --prepare, --execute or --rebuild")
    if args.prepare:
        return prepare()
    if args.execute:
        return execute()
    return rebuild_offline()


if __name__ == "__main__":
    raise SystemExit(main())
