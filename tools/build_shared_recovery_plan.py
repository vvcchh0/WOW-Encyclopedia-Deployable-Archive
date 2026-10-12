"""Build bounded recovery plans from stopped shared-asset batches.

Only items without a verified success record are emitted.  The source plan
fields are copied intact and each item carries its original target output so a
later operator can run the groups independently without guessing ownership.
"""

from __future__ import annotations

import argparse
import datetime as _datetime
import json
from pathlib import Path
from typing import Any


def _records(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    if not path.exists():
        return latest
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        latest[(str(record.get("original", "")), str(record.get("requested_timestamp", "")))] = record
    return latest


def build(group_specs: list[tuple[str, Path, Path]], destination: Path) -> dict[str, Any]:
    groups: list[dict[str, Any]] = []
    all_items: list[dict[str, Any]] = []
    anchor: str | None = None
    for name, plan_path, output_dir in group_specs:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        if anchor is None:
            anchor = str(plan["anchor_timestamp"])
        elif anchor != str(plan["anchor_timestamp"]):
            raise ValueError("recovery plans must use the same anchor_timestamp")
        latest = _records(output_dir / "manifest.jsonl")
        group_items: list[dict[str, Any]] = []
        for original in plan.get("items", []):
            key = (str(original.get("original")), str(original.get("timestamp")))
            previous = latest.get(key)
            if previous is not None and previous.get("status") == "success":
                continue
            item = dict(original)
            item["source_plan"] = str(plan_path)
            item["target_output"] = str(output_dir)
            item["recovery_reason"] = (
                "prior_failed_attempt" if previous is not None else "not_attempted_after_stop"
            )
            group_items.append(item)
            all_items.append(item)
        groups.append({
            "name": name,
            "source_plan": str(plan_path),
            "target_output": str(output_dir),
            "item_count": len(group_items),
            "items": group_items,
        })

    result = {
        "schema_version": 1,
        "generated_at": _datetime.datetime.now(_datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "anchor_timestamp": anchor,
        "notes": (
            "Recovery-only plan generated from shared batch manifests. "
            "Run each target_output group with healthy connection and bounded retry; "
            "user-authorized acquisition."
        ),
        "item_count": len(all_items),
        "items": all_items,
        "groups": groups,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-1", type=Path, required=True)
    parser.add_argument("--out-1", type=Path, required=True)
    parser.add_argument("--plan-2", type=Path, required=True)
    parser.add_argument("--out-2", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = build(
        [("shared-1", args.plan_1, args.out_1), ("shared-2", args.plan_2, args.out_2)],
        args.out,
    )
    print(json.dumps({
        "output": str(args.out),
        "item_count": result["item_count"],
        "groups": {group["name"]: group["item_count"] for group in result["groups"]},
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
