"""Bounded offline Ruffle helpers for the three validated Flash exhibits.

This module does not discover or rewrite arbitrary Flash content.  It only
marks the three exact historical pages that have a validated local SWF and
stages a fixed, hash-checked subset of the self-hosted Ruffle distribution.
"""

from __future__ import annotations

import binascii
import hashlib
import html
import re
import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


SOCKET_ROUTE = "/info/items/socketeditems.html"
DANCE_ROUTE = "/info/races/dancing.html"
TUSKARR_ROUTE = "/wrath/features/factions/tuskarr.xml.html"

RUFFLE_ZIP_SHA256 = "ef12edbee135d581a9cd523837d746da30a07a64dbf1cf472d2e472c656f4b5e"

SWF_EXHIBITS = {
    "socket_anim": {
        "path": "info/items/images/socket_anim.swf",
        "sha256": "c289e5fea2d04180d0615d8956049649d6f0362134e71c62589bbb41a7c26576",
        "width": 48,
        "height": 47,
    },
    "dwarf_male": {
        "path": "info/races/images/dancing/gifs/dwarf_male.swf",
        "sha256": "00d7e4fff668eb4a58da18571c1b9a5082c83e7197d82361c990f87942a135a9",
        "width": 250,
        "height": 250,
    },
    "tuskarr_idle": {
        "path": "wrath/flash/global/tuskarr_idle.swf",
        "sha256": "544e29b972fbf8547c304232a3f7461aaa69f6431b98f627a3762e8192c9bf3e",
        "width": 360,
        "height": 450,
    },
}


# The maps are intentionally omitted.  These are the only runtime members
# copied into a generated site; the ZIP itself is verified before extraction.
RUFFLE_MEMBER_EXPECTATIONS = {
    "LICENSE_MIT": (1097, 682155339),
    "LICENSE_APACHE": (9723, 1534941245),
    "README.md": (2328, 586158125),
    "package.json": (418, 1007906333),
    "ruffle.js": (465885, 3418172434),
    "core.ruffle.16d61072ac7fdc4d5013.js": (108322, 1198367822),
    "core.ruffle.994eeef0a471a88cd0e3.js": (114743, 3089648612),
    "172de42e6619eac8f371.wasm": (14302754, 1333758784),
    "878d548199cddef07035.wasm": (14227884, 364897941),
}
MAX_ZIP_MEMBER_BYTES = 64 * 1024 * 1024


class OfflineFlashError(ValueError):
    """Raised when an exact-page or runtime staging contract is violated."""


_COMMENT_RE = re.compile(r"<!--.*?(?:-->|$)", re.DOTALL | re.IGNORECASE)
_SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.DOTALL | re.IGNORECASE)


def _hidden_ranges(text: str) -> list[tuple[int, int]]:
    """Return comment/script-body ranges where markup-looking text is inert."""

    ranges = [(match.start(), match.end()) for match in _COMMENT_RE.finditer(text)]
    for match in _SCRIPT_RE.finditer(text):
        opening_end = text.find(">", match.start(), match.end()) + 1
        if opening_end > 0:
            ranges.append((opening_end, match.end()))
    return ranges


def _real_markup_match(text: str, pattern: re.Pattern[str]) -> re.Match[str] | None:
    ranges = _hidden_ranges(text)
    for match in pattern.finditer(text):
        if not any(start <= match.start() < end for start, end in ranges):
            return match
    return None


def _normalise_route(route: str) -> str:
    if not isinstance(route, str) or not route:
        raise OfflineFlashError("route must be a non-empty string")
    if any(token in route for token in ("?", "#")):
        raise OfflineFlashError("route queries and fragments are not accepted")
    if "\\" in route or "\x00" in route:
        raise OfflineFlashError("route must use a local URL path")
    normalised = "/" + route.lstrip("/")
    if normalised.startswith("//") or any(part == ".." for part in normalised.split("/")):
        raise OfflineFlashError("route must not escape the local route root")
    return normalised


def _normalise_base_path(base_path: str) -> str:
    if not isinstance(base_path, str) or not base_path:
        raise OfflineFlashError("base_path must be a non-empty local URL path")
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", base_path):
        raise OfflineFlashError("base_path must be a local URL path, not a URI")
    if any(token in base_path for token in ("?", "#", "\\", "\x00")):
        raise OfflineFlashError("base_path must not contain a query, fragment, or backslash")
    normalised = "/" + base_path.lstrip("/")
    if normalised.startswith("//") or any(part == ".." for part in normalised.split("/")):
        raise OfflineFlashError("base_path must not escape the local route root")
    return normalised.rstrip("/") + "/"


def _page_kind(route: str) -> str | None:
    return {
        SOCKET_ROUTE: "socket",
        DANCE_ROUTE: "dance",
        TUSKARR_ROUTE: "tuskarr",
    }.get(route)


def rewrite_page(text: str, *, route: str, base_path: str) -> tuple[str, dict[str, Any]]:
    """Inject the deferred helper on exactly the three validated pages."""

    if not isinstance(text, str):
        raise OfflineFlashError("text must be a string")
    normalised_route = _normalise_route(route)
    normalised_base = _normalise_base_path(base_path)
    kind = _page_kind(normalised_route)
    stats: dict[str, Any] = {
        "route": normalised_route,
        "base_path": normalised_base,
        "enabled": kind is not None,
        "kind": kind,
        "helper_injected": 0,
        "expected_targets": 0,
        "already_present": False,
    }
    if kind is None:
        stats["reason"] = "unsupported-route"
        return text, stats

    marker_pattern = re.compile(
        r"<script\b(?=[^>]*\bdata-offline-flash\s*=\s*[\"']"
        + re.escape(kind)
        + r"[\"'])[^>]*>",
        re.IGNORECASE | re.DOTALL,
    )
    helper_pattern = re.compile(
        r"<script\b(?=[^>]*\bsrc\s*=\s*[\"'][^\"']*__offline/flash-exhibits\.js[\"'])[^>]*>",
        re.IGNORECASE | re.DOTALL,
    )
    if _real_markup_match(text, marker_pattern) or _real_markup_match(text, helper_pattern):
        stats["already_present"] = True
        stats["reason"] = "already-present"
        return text, stats

    stats["expected_targets"] = {"socket": 5, "dance": 1, "tuskarr": 1}[kind]
    script_src = html.escape(normalised_base + "__offline/flash-exhibits.js", quote=True)
    tag = (
        '<script defer data-offline-flash="'
        + kind
        + '" data-base-path="'
        + html.escape(normalised_base, quote=True)
        + '" src="'
        + script_src
        + '"></script>\n'
    )
    head_match = _real_markup_match(text, re.compile(r"</head\s*>", re.IGNORECASE))
    if head_match is None:
        raise OfflineFlashError(f"{normalised_route}: missing </head> for helper injection")
    index = head_match.start()
    new_text = text[:index] + tag + text[index:]
    stats["helper_injected"] = 1
    stats["changed"] = True
    return new_text, stats


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _nearest_existing(path: Path) -> Path:
    current = path
    while not current.exists() and current != current.parent:
        current = current.parent
    return current


def _check_member_name(name: str) -> None:
    if not name or "\x00" in name or "\\" in name:
        raise OfflineFlashError(f"unsafe Ruffle ZIP member path: {name!r}")
    pure = PurePosixPath(name)
    if pure.is_absolute() or any(part in ("", ".", "..") for part in pure.parts):
        raise OfflineFlashError(f"unsafe Ruffle ZIP member path: {name!r}")


def _target_within(root: Path, target: Path) -> None:
    root_resolved = root.resolve()
    target_resolved = target.resolve(strict=False)
    try:
        target_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise OfflineFlashError(f"runtime target escapes staging root: {target}") from exc


def _write_owned(path: Path, payload: bytes) -> None:
    if path.is_symlink() or path.exists():
        raise OfflineFlashError(f"refusing to overwrite an existing runtime file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _runtime_mime(member: str) -> str:
    if member.endswith(".wasm"):
        return "application/wasm"
    if member == "package.json":
        return "application/json"
    if member.endswith(".md") or member.startswith("LICENSE_"):
        return "text/plain; charset=utf-8"
    return "application/javascript"


def stage_runtime(
    output: str | Path,
    *,
    archive_path: str | Path,
    base_path: str,
    min_free_bytes: int,
) -> dict[str, Any]:
    """Stage the hash-checked Ruffle runtime and the local helper.

    The returned paths are relative to ``output`` so an exporter can record
    them in its provenance manifest without guessing the staging layout.
    """

    output_root = Path(output)
    archive = Path(archive_path)
    normalised_base = _normalise_base_path(base_path)
    if min_free_bytes < 0:
        raise OfflineFlashError("min_free_bytes must be non-negative")
    if not archive.is_file():
        raise OfflineFlashError(f"Ruffle archive does not exist: {archive}")
    if output_root.exists() and output_root.is_symlink():
        raise OfflineFlashError(f"refusing to stage through an output symlink: {output_root}")
    free_bytes = shutil.disk_usage(_nearest_existing(output_root)).free
    if free_bytes < min_free_bytes:
        raise OfflineFlashError(
            f"insufficient free space before Ruffle staging: {free_bytes} < {min_free_bytes}"
        )
    archive_sha256 = _sha256_file(archive)
    if archive_sha256 != RUFFLE_ZIP_SHA256:
        raise OfflineFlashError(
            f"Ruffle archive SHA mismatch: expected {RUFFLE_ZIP_SHA256}, got {archive_sha256}"
        )

    helper_source = Path(__file__).resolve().parent / "browser_assets" / "offline-flash.js"
    if not helper_source.is_file():
        raise OfflineFlashError(f"offline Flash helper is missing: {helper_source}")

    vendor_root = output_root / "__offline" / "vendor" / "ruffle"
    helper_target = output_root / "__offline" / "flash-exhibits.js"
    _target_within(output_root, vendor_root)
    _target_within(output_root, helper_target)
    # Refuse the complete staging operation before creating any output.  This
    # avoids leaving a partly populated runtime if the helper or a later
    # selected member already exists.
    for member in RUFFLE_MEMBER_EXPECTATIONS:
        target = vendor_root / member
        _target_within(vendor_root, target)
        if target.is_symlink() or target.exists():
            raise OfflineFlashError(f"refusing to overwrite an existing runtime file: {target}")
    if helper_target.is_symlink() or helper_target.exists():
        raise OfflineFlashError(f"refusing to overwrite an existing runtime file: {helper_target}")
    runtime_files: list[dict[str, Any]] = []

    with zipfile.ZipFile(archive) as bundle:
        infos = bundle.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise OfflineFlashError("Ruffle ZIP contains duplicate member names")
        for info in infos:
            _check_member_name(info.filename)
            if info.is_dir() or info.flag_bits & 0x1:
                raise OfflineFlashError(f"Ruffle ZIP member is not a plain readable file: {info.filename}")
            unix_mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(unix_mode):
                raise OfflineFlashError(f"Ruffle ZIP member is a symlink: {info.filename}")
            if info.file_size > MAX_ZIP_MEMBER_BYTES:
                raise OfflineFlashError(f"Ruffle ZIP member is unexpectedly large: {info.filename}")
        for member, (expected_size, expected_crc) in RUFFLE_MEMBER_EXPECTATIONS.items():
            try:
                info = bundle.getinfo(member)
            except KeyError as exc:
                raise OfflineFlashError(f"Ruffle ZIP is missing required member: {member}") from exc
            if info.file_size != expected_size or info.CRC != expected_crc:
                raise OfflineFlashError(
                    f"Ruffle ZIP member metadata mismatch for {member}: "
                    f"expected size/CRC {expected_size}/{expected_crc}, "
                    f"got {info.file_size}/{info.CRC}"
                )
            payload = bundle.read(info)
            actual_crc = binascii.crc32(payload) & 0xFFFFFFFF
            if len(payload) != expected_size or actual_crc != expected_crc:
                raise OfflineFlashError(f"Ruffle ZIP member content mismatch for {member}")
            target = vendor_root / member
            _target_within(vendor_root, target)
            if info.file_size >= 10 * 1024 * 1024:
                free_before_member = shutil.disk_usage(_nearest_existing(output_root)).free
                if free_before_member < min_free_bytes:
                    raise OfflineFlashError(
                        f"insufficient free space before large Ruffle member {member}: "
                        f"{free_before_member} < {min_free_bytes}"
                    )
            _write_owned(target, payload)
            runtime_files.append(
                {
                    "member": member,
                    "path": str(Path("__offline/vendor/ruffle") / member).replace("\\", "/"),
                    "absolute_path": str(target.resolve()),
                    "bytes": len(payload),
                    "length": len(payload),
                    "crc32": actual_crc,
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "mime": _runtime_mime(member),
                    "kind": "flash_license" if member.startswith("LICENSE_") else "flash_runtime",
                }
            )

    helper_payload = helper_source.read_bytes()
    _write_owned(helper_target, helper_payload)
    helper_record = {
        "path": "__offline/flash-exhibits.js",
        "absolute_path": str(helper_target.resolve()),
        "bytes": len(helper_payload),
        "length": len(helper_payload),
        "sha256": hashlib.sha256(helper_payload).hexdigest(),
        "mime": "application/javascript",
        "kind": "flash_helper",
    }
    files = [
        {
            "output_path": helper_record["path"],
            "sha256": helper_record["sha256"],
            "length": helper_record["length"],
            "mime": helper_record["mime"],
            "kind": helper_record["kind"],
            "source_sha256": helper_record["sha256"],
        }
    ]
    files.extend(
        {
            "output_path": record["path"],
            "sha256": record["sha256"],
            "length": record["length"],
            "mime": record["mime"],
            "kind": record["kind"],
            "source_member": record["member"],
            "source_sha256": record["sha256"],
        }
        for record in runtime_files
    )
    return {
        "status": "staged",
        "base_path": normalised_base,
        "archive_path": str(archive.resolve()),
        "archive_sha256": archive_sha256,
        "runtime_version": "0.7.1",
        "output": str(output_root.resolve()),
        "vendor_root": "__offline/vendor/ruffle",
        "helper": helper_record,
        "runtime_files": runtime_files,
        "runtime_file_count": len(runtime_files),
        "files": files,
        "total_bytes": sum(file["length"] for file in files),
        "free_bytes_before": free_bytes,
    }


__all__ = [
    "DANCE_ROUTE",
    "OfflineFlashError",
    "RUFFLE_MEMBER_EXPECTATIONS",
    "RUFFLE_ZIP_SHA256",
    "SOCKET_ROUTE",
    "SWF_EXHIBITS",
    "TUSKARR_ROUTE",
    "rewrite_page",
    "stage_runtime",
]
