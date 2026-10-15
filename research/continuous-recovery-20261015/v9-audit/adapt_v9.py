from pathlib import Path
root=Path(r"D:\WOW_Encyclopedia")
old=root/"research/continuous-recovery-20261015/sidebar-audit/audit_local.py"
new=root/"research/continuous-recovery-20261015/v9-audit/audit_local_v9.py"
s=old.read_text(encoding="utf-8")
s=s.replace('OUT = ROOT / "research/continuous-recovery-20261015/sidebar-audit"', 'OUT = ROOT / "research/continuous-recovery-20261015/v9-audit"')
s=s.replace('V8', 'V9')
s=s.replace('-v8', '-v9')
s=s.replace('ROOT / "research/resource-repair-20261015/build-v9.json"', 'ROOT / "research/continuous-recovery-20261015/build-v9.json"')
s=s.replace('ROOT / "research/resource-repair-20261015/root-final-acceptance.json"', 'ROOT / "research/continuous-recovery-20261015/root-v9-export-acceptance.json"')
# Use all current v9 audit inputs plus the frozen baseline and v7c receipt.
old_block='''    source_paths = [
        INVENTORY_PATH,
        INVENTORY_MD,
        FINAL_ACCEPTANCE,
        V9_BUILD,
        V7_RECEIPT,
        FROZEN_MANIFEST,
        DOC_PATH,
        CHANGELOG,
        V9_ROUTE_MAP,
        V9_PROVENANCE,
        ROOT / ".scratch/offline-navigation-20261015-v7c/build-manifest.json",
    ]'''
new_block='''    source_paths = [
        INVENTORY_PATH,
        INVENTORY_MD,
        ROOT / "research/continuous-recovery-20261015/v9-audit-task-input.json",
        ROOT / "research/continuous-recovery-20261015/v9-route-independent-precheck.json",
        FINAL_ACCEPTANCE,
        V9_BUILD,
        V7_RECEIPT,
        FROZEN_MANIFEST,
        DOC_PATH,
        CHANGELOG,
        V9_ROUTE_MAP,
        V9_PROVENANCE,
        ROOT / ".scratch/offline-navigation-20261015-v9/build-manifest.json",
        ROOT / ".scratch/offline-navigation-20261015-v7c/build-manifest.json",
    ]'''
if old_block not in s:
    raise SystemExit("source_paths block not found")
s=s.replace(old_block,new_block)
# Point the explanatory literals at the current v9 evidence.
s=s.replace('latest v8 route/page/resource evidence', 'latest v9 route/page/resource evidence')
s=s.replace('against v8', 'against v9')
s=s.replace('Current v8 acceptance gaps retained as context', 'Current v9 browser/source gaps retained as context')
s=s.replace('Known v8 acceptance gaps retained as context', 'Known v9 browser/source gaps retained as context')
new.write_text(s,encoding="utf-8")
print(new)
