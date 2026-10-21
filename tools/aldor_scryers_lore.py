#!/usr/bin/env python3
"""Load the two reviewed Aldor/Scryers lore literals as a tiny helper.

The main Aldor/Scryers page includes ``rewards-aldor-scryers.js`` but the
historical lore assignments are preserved in the separately saved token
script.  This module validates those exact Source16 records, extracts only
the two string literals without executing JavaScript, and returns an in-memory
helper for the exporter to inject on the non-token page.  It never writes a
site, copies the token script, or imports its reward data.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping


EXPECTED_MANIFEST_SHA256 = "e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a"
TOKENS_ROUTE = "/info/basics/factions/aldorscryers/scripts/rewards-aldor-scryers-tokens.js"
TOKENS_SHA256 = "2d5bb9fac83f0869f23bf7781e92664f1e64a1ab78b53a7ed431530b1becbcad"
TOKENS_LENGTH = 19923
MAIN_ROUTE = "/info/basics/factions/aldorscryers/scripts/rewards-aldor-scryers.js"
MAIN_SHA256 = "c1b039a530592be71bfcb1cbaa1cf3f3cea5e9a64f2028baef5a55300b76b3e3"
MAIN_LENGTH = 58140
PAGE_ROUTE = "/info/basics/factions/aldorscryers/aldor-scryers.xml"
GENERATED_RELATIVE = "__offline/aldor-scryers-lore.js"
EXPECTED_SCHEMA_VERSION = 1
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_IDENT_RE = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")


class AldorScryersLoreError(ValueError):
    """Raised when the exact Source16 lore source or local path is invalid."""


@dataclass(frozen=True)
class GeneratedLoreFile:
    """The helper bytes the exporter may stage under ``__offline``."""

    relative: str
    data: bytes
    mime: str
    sha256: str
    length: int


@dataclass(frozen=True)
class LoreBundle:
    """Validated helper and public source metadata, without token-script data."""

    generated_file: GeneratedLoreFile
    source_metadata: Mapping[str, Any]
    expected_page_route: str


def _fail(message: str) -> AldorScryersLoreError:
    return AldorScryersLoreError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_relative(value: Any, label: str) -> str:
    if isinstance(value, os.PathLike):
        value = os.fspath(value)
    if not isinstance(value, str) or not value:
        raise _fail(f"{label} must be a non-empty relative path")
    if "\x00" in value or "\\" in value or value.startswith("/"):
        raise _fail(f"{label} must be a safe relative POSIX path: {value!r}")
    if PureWindowsPath(value).is_absolute():
        raise _fail(f"{label} must not be absolute: {value!r}")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts) or ":" in parts[0]:
        raise _fail(f"{label} contains traversal or drive syntax: {value!r}")
    return value


def _inside_workspace(workspace_root: Path, value: Any, label: str, *, directory: bool) -> Path:
    """Resolve a workspace path while rejecting symlink components."""

    root = Path(workspace_root).resolve(strict=True)
    candidate = Path(value)
    if candidate.is_absolute():
        raw = candidate
    else:
        # Callers commonly pass a relative ``Path`` on Windows, whose
        # rendered form contains backslashes.  Reject those in manifest
        # strings but preserve normal Path semantics for API arguments.
        if isinstance(value, os.PathLike):
            if ".." in candidate.parts:
                raise _fail(f"{label} contains parent traversal: {value!r}")
            raw = root / candidate
        else:
            raw = root / _safe_relative(value, label)
    try:
        raw_abs = raw.absolute()
        relative = raw_abs.relative_to(root)
    except (OSError, ValueError) as exc:
        raise _fail(f"{label} escapes workspace: {value!r}") from exc
    current = root
    try:
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise _fail(f"{label} traverses a symlink: {value!r}")
        resolved = raw_abs.resolve(strict=True)
        resolved.relative_to(root)
        mode = resolved.stat().st_mode
    except AldorScryersLoreError:
        raise
    except (OSError, ValueError) as exc:
        raise _fail(f"{label} cannot resolve inside workspace: {value!r}: {exc}") from exc
    if directory:
        if not stat.S_ISDIR(mode):
            raise _fail(f"{label} is not a directory: {value!r}")
    elif not stat.S_ISREG(mode):
        raise _fail(f"{label} is not a regular file: {value!r}")
    return resolved


def _read_manifest(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"cannot read manifest {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise _fail("Source16 manifest must be a JSON object")
    return value, raw


def _record(files: Any, route: str) -> Mapping[str, Any]:
    if not isinstance(files, list):
        raise _fail("manifest files must be a list")
    rows = [item for item in files if isinstance(item, dict) and item.get("route") == route]
    if len(rows) != 1:
        raise _fail(f"manifest route must have exactly one record: {route} (found {len(rows)})")
    return rows[0]


def _record_output_path(
    workspace_root: Path,
    source_site: Path,
    record: Mapping[str, Any],
    route: str,
) -> Path:
    output_path = record.get("output_path")
    if not isinstance(output_path, str) or not output_path:
        raise _fail(f"{route} record has no output_path")
    resolved = _inside_workspace(workspace_root, output_path, f"{route} output_path", directory=False)
    expected = (source_site / route.lstrip("/")).resolve(strict=False)
    try:
        resolved.relative_to(source_site)
    except ValueError as exc:
        raise _fail(f"{route} output_path is outside source_site") from exc
    if resolved != expected:
        raise _fail(
            f"{route} output_path does not match source_site route: {resolved} != {expected}"
        )
    return resolved


def _verify_record_bytes(
    path: Path,
    record: Mapping[str, Any],
    route: str,
    *,
    expected_sha: str | None = None,
    expected_length: int | None = None,
) -> bytes:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise _fail(f"cannot read {route}: {exc}") from exc
    actual_sha = _sha256(data)
    actual_length = len(data)
    record_sha = record.get("derived_sha256")
    record_length = record.get("derived_length")
    if not isinstance(record_sha, str) or not _SHA256_RE.fullmatch(record_sha):
        raise _fail(f"{route} record has invalid derived_sha256")
    if not isinstance(record_length, int):
        raise _fail(f"{route} record has invalid derived_length")
    source_sha = record.get("source_sha256")
    source_length = record.get("source_length")
    if not isinstance(source_sha, str) or not _SHA256_RE.fullmatch(source_sha):
        raise _fail(f"{route} record has invalid source_sha256")
    if not isinstance(source_length, int) or source_length < 0:
        raise _fail(f"{route} record has invalid source_length")
    if record_sha != actual_sha or record_length != actual_length:
        raise _fail(
            f"{route} derived bytes mismatch: record {record_sha}/{record_length}, "
            f"actual {actual_sha}/{actual_length}"
        )
    if expected_sha is not None:
        if record.get("source_sha256") != expected_sha or record_sha != expected_sha:
            raise _fail(f"{route} pinned SHA mismatch")
        if expected_length is not None and (
            record.get("source_length") != expected_length or record_length != expected_length
        ):
            raise _fail(f"{route} pinned length mismatch")
    return data


def _skip_space(text: str, index: int) -> int:
    while index < len(text) and text[index].isspace():
        index += 1
    return index


def _skip_quoted(text: str, index: int) -> int:
    quote = text[index]
    index += 1
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            if index <= len(text) and index and index - 1 < len(text) and text[index - 1] in "\r\n":
                # A line continuation is still one escaped character for the
                # purpose of skipping; CRLF is handled by the next iteration.
                if index < len(text) and text[index] == "\n" and text[index - 1] == "\r":
                    index += 1
            continue
        if char == quote:
            return index + 1
        index += 1
    raise _fail("unterminated JavaScript string while scanning lore source")


def _decode_js_content(raw: str) -> str:
    """Decode the small JS escape subset used by the pinned literals."""

    result: list[str] = []
    index = 0
    escapes = {
        "b": "\b",
        "f": "\f",
        "n": "\n",
        "r": "\r",
        "t": "\t",
        "v": "\v",
        "0": "\0",
        "\\": "\\",
        '"': '"',
        "'": "'",
    }
    while index < len(raw):
        char = raw[index]
        if char != "\\":
            result.append(char)
            index += 1
            continue
        if index + 1 >= len(raw):
            raise _fail("dangling escape in lore literal")
        next_char = raw[index + 1]
        if next_char in "\r\n":
            # JavaScript line continuation contributes no character.
            index += 2
            if next_char == "\r" and index < len(raw) and raw[index] == "\n":
                index += 1
            continue
        if next_char == "x" and index + 3 < len(raw):
            digits = raw[index + 2 : index + 4]
            if re.fullmatch(r"[0-9A-Fa-f]{2}", digits):
                result.append(chr(int(digits, 16)))
                index += 4
                continue
        if next_char == "u" and index + 5 < len(raw):
            digits = raw[index + 2 : index + 6]
            if re.fullmatch(r"[0-9A-Fa-f]{4}", digits):
                result.append(chr(int(digits, 16)))
                index += 6
                continue
        # JS preserves the escaped character for legacy identity escapes.
        result.append(escapes.get(next_char, next_char))
        index += 2
    return "".join(result)


def _parse_js_string(text: str, index: int) -> tuple[str, int]:
    if index >= len(text) or text[index] != '"':
        raise _fail("lore assignment must use a double-quoted string literal")
    index += 1
    raw: list[str] = []
    while index < len(text):
        char = text[index]
        if char == '"':
            return _decode_js_content("".join(raw)), index + 1
        if char in "\r\n":
            raise _fail("unescaped newline in lore string literal")
        if char == "\\":
            if index + 1 >= len(text):
                raise _fail("unterminated lore string literal")
            next_char = text[index + 1]
            raw.append("\\")
            raw.append(next_char)
            index += 2
            if next_char == "\r" and index < len(text) and text[index] == "\n":
                raw.append("\n")
                index += 1
            continue
        raw.append(char)
        index += 1
    raise _fail("unterminated lore string literal")


def _parse_key(text: str, index: int) -> tuple[str, int]:
    quote = text[index] if index < len(text) else ""
    if quote not in {'"', "'"}:
        raise _fail("lore assignment key must be quoted")
    index += 1
    raw: list[str] = []
    while index < len(text):
        char = text[index]
        if char == quote:
            return _decode_js_content("".join(raw)), index + 1
        if char in "\r\n":
            raise _fail("newline in lore assignment key")
        if char == "\\" and index + 1 < len(text):
            raw.extend(("\\", text[index + 1]))
            index += 2
            continue
        raw.append(char)
        index += 1
    raise _fail("unterminated lore assignment key")


def _skip_comment(text: str, index: int) -> int | None:
    if text.startswith("//", index):
        end = text.find("\n", index + 2)
        return len(text) if end < 0 else end + 1
    if text.startswith("/*", index):
        end = text.find("*/", index + 2)
        if end < 0:
            raise _fail("unterminated comment while scanning lore source")
        return end + 2
    return None


def _extract_lore_assignments(text: str) -> dict[str, str]:
    """Extract exactly the two ``loreTexts[...]=\"...\"`` assignments."""

    assignments: dict[str, str] = {}
    index = 0
    while index < len(text):
        skipped = _skip_comment(text, index)
        if skipped is not None:
            index = skipped
            continue
        if text[index] in {'"', "'", "`"}:
            index = _skip_quoted(text, index)
            continue
        match = _IDENT_RE.match(text, index)
        if not match:
            index += 1
            continue
        identifier = match.group(0)
        index = match.end()
        if identifier != "loreTexts":
            continue
        index = _skip_space(text, index)
        if index >= len(text) or text[index] != "[":
            continue
        index = _skip_space(text, index + 1)
        key, index = _parse_key(text, index)
        index = _skip_space(text, index)
        if index >= len(text) or text[index] != "]":
            raise _fail("malformed lore assignment key")
        index = _skip_space(text, index + 1)
        if index >= len(text) or text[index] != "=":
            raise _fail("lore assignment is not a direct assignment")
        index = _skip_space(text, index + 1)
        value, index = _parse_js_string(text, index)
        index = _skip_space(text, index)
        if index >= len(text) or text[index] != ";":
            raise _fail("lore assignment must end after one literal")
        index += 1
        if key not in {"alliance", "horde"}:
            raise _fail(f"unexpected loreTexts key: {key!r}")
        if key in assignments:
            raise _fail(f"duplicate loreTexts assignment: {key}")
        assignments[key] = value
    if set(assignments) != {"alliance", "horde"}:
        raise _fail(f"expected alliance and horde lore assignments, got {sorted(assignments)}")
    return assignments


def _make_helper(lore: Mapping[str, str]) -> bytes:
    payload = json.dumps(dict(lore), ensure_ascii=False, separators=(",", ":"))
    source = f'''// Source16 Aldor/Scryers lore supplement; injected only on the main page.
(function () {{
  "use strict";
  var suppliedLore = {payload};
  function installLore() {{
    var target = window.loreTexts;
    if (!target || typeof target !== "object") {{
      target = window.loreTexts = {{}};
    }}
    if (typeof target.alliance === "undefined" || target.alliance === null || target.alliance === "") {{
      target.alliance = suppliedLore.alliance;
    }}
    if (typeof target.horde === "undefined" || target.horde === null || target.horde === "") {{
      target.horde = suppliedLore.horde;
    }}
    var node = document.getElementById("loreText");
    if (!node) return;
    var current = node.innerHTML;
    if (current && current !== "undefined" && current !== "null") return;
    var hordeRewards = document.getElementById("hordeRewards");
    var hordeVisible = false;
    if (hordeRewards) {{
      hordeVisible = window.getComputedStyle
        ? window.getComputedStyle(hordeRewards).visibility === "visible"
        : hordeRewards.style.visibility === "visible";
    }}
    node.innerHTML = target[hordeVisible ? "horde" : "alliance"];
  }}
  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", installLore, false);
  }} else {{
    installLore();
  }}
}})();
'''
    return source.encode("utf-8")


def load_lore_bundle(
    workspace_root: str | os.PathLike[str],
    source_site: str | os.PathLike[str],
    manifest_path: str | os.PathLike[str],
    manifest: Mapping[str, Any],
) -> LoreBundle:
    """Validate Source16 and return a helper for the exact main page route."""

    root = Path(workspace_root).resolve(strict=True)
    site = _inside_workspace(root, source_site, "source_site", directory=True)
    manifest_file = _inside_workspace(root, manifest_path, "manifest_path", directory=False)
    manifest_value, manifest_bytes = _read_manifest(manifest_file)
    actual_manifest_sha = _sha256(manifest_bytes)
    if actual_manifest_sha != EXPECTED_MANIFEST_SHA256:
        raise _fail(
            f"Source16 manifest SHA mismatch: expected {EXPECTED_MANIFEST_SHA256}, got {actual_manifest_sha}"
        )
    if not isinstance(manifest, Mapping) or dict(manifest) != manifest_value:
        raise _fail("passed manifest object does not match the pinned manifest file")
    if manifest_value.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        raise _fail("unexpected Source16 manifest schema_version")
    site_root = manifest_value.get("site_root")
    manifest_site = _inside_workspace(root, site_root, "manifest site_root", directory=True)
    if manifest_site != site:
        raise _fail(f"source_site does not match manifest site_root: {site} != {manifest_site}")
    source16 = manifest_value.get("source16")
    if not isinstance(source16, Mapping) or source16.get("network_requests") != 0:
        raise _fail("Source16 manifest must record zero network requests")

    files = manifest_value.get("files")
    page_record = _record(files, PAGE_ROUTE)
    main_record = _record(files, MAIN_ROUTE)
    tokens_record = _record(files, TOKENS_ROUTE)
    for route, record in ((PAGE_ROUTE, page_record), (MAIN_ROUTE, main_record), (TOKENS_ROUTE, tokens_record)):
        if record.get("kind") != "js" and route != PAGE_ROUTE:
            raise _fail(f"{route} is not recorded as JavaScript")
        _record_output_path(root, site, record, route)

    tokens_path = _record_output_path(root, site, tokens_record, TOKENS_ROUTE)
    main_path = _record_output_path(root, site, main_record, MAIN_ROUTE)
    page_path = _record_output_path(root, site, page_record, PAGE_ROUTE)
    token_bytes = _verify_record_bytes(
        tokens_path,
        tokens_record,
        TOKENS_ROUTE,
        expected_sha=TOKENS_SHA256,
        expected_length=TOKENS_LENGTH,
    )
    _verify_record_bytes(
        main_path,
        main_record,
        MAIN_ROUTE,
        expected_sha=MAIN_SHA256,
        expected_length=MAIN_LENGTH,
    )
    _verify_record_bytes(page_path, page_record, PAGE_ROUTE)
    try:
        token_text = token_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _fail(f"token script is not UTF-8: {exc}") from exc
    lore = _extract_lore_assignments(token_text)
    helper_bytes = _make_helper(lore)
    generated = GeneratedLoreFile(
        relative=GENERATED_RELATIVE,
        data=helper_bytes,
        mime="application/javascript",
        sha256=_sha256(helper_bytes),
        length=len(helper_bytes),
    )
    source_metadata: dict[str, Any] = {
        "classification": "source16_text_reuse",
        "source_manifest_sha256": actual_manifest_sha,
        "tokens_route": TOKENS_ROUTE,
        "tokens_sha256": TOKENS_SHA256,
        "tokens_length": TOKENS_LENGTH,
        "tokens_actual_timestamp": tokens_record.get("actual_timestamp"),
        "main_route": MAIN_ROUTE,
        "main_sha256": MAIN_SHA256,
        "main_length": MAIN_LENGTH,
        "main_actual_timestamp": main_record.get("actual_timestamp"),
        "page_route": PAGE_ROUTE,
        "page_source_sha256": page_record.get("source_sha256"),
        "page_derived_sha256": page_record.get("derived_sha256"),
        "page_derived_length": page_record.get("derived_length"),
        "page_actual_timestamp": page_record.get("actual_timestamp"),
        "original_capture_scope": "Source16 manifest records; no new capture",
        "network_requests": 0,
        "injection": "defer",
        "lore_keys": ["alliance", "horde"],
        "lore_body_sha256": {
            key: _sha256(value.encode("utf-8")) for key, value in lore.items()
        },
        "lore_body_lengths": {key: len(value) for key, value in lore.items()},
        "generated_relative": GENERATED_RELATIVE,
    }
    return LoreBundle(generated, source_metadata, PAGE_ROUTE)


__all__ = [
    "AldorScryersLoreError",
    "EXPECTED_MANIFEST_SHA256",
    "GENERATED_RELATIVE",
    "GeneratedLoreFile",
    "LoreBundle",
    "MAIN_LENGTH",
    "MAIN_ROUTE",
    "MAIN_SHA256",
    "PAGE_ROUTE",
    "TOKENS_LENGTH",
    "TOKENS_ROUTE",
    "TOKENS_SHA256",
    "load_lore_bundle",
]
