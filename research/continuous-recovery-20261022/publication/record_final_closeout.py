"""Record the completed publication and the bounded local closeout, without new source requests."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess

ROOT = Path.cwd()
HERE = ROOT / 'research/continuous-recovery-20261022'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
outpath = HERE / 'publication/final-local-closeout.json'
assert not outpath.exists()
baseline = read(HERE / 'baseline-acceptance.json')
bindings = []
for row in baseline['frozen_bindings']:
    path = ROOT / row['path']
    assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
    bindings.append({**row, 'unchanged': True})
proof_paths = [
    HERE / 'root-v56-export-acceptance.json',
    HERE / 'root-v56-browser-acceptance.json',
    HERE / 'root-v56-online-acceptance.json',
    HERE / 'publication/v56-portable-acceptance.json',
    HERE / 'publication/v56-public-release-publish.json',
    HERE / 'publication/v56-public-assets-acceptance.json',
]
proofs = []
for path in proof_paths:
    record = read(path)
    assert record.get('accepted') is True or record.get('status') == 'accepted'
    proofs.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'accepted': True})
proc = subprocess.run([
    'powershell.exe', '-NoProfile', '-Command',
    "Get-CimInstance Win32_Process -Filter \"Name = 'python.exe' OR Name = 'node.exe' OR Name = 'curl.exe' OR Name = 'gh.exe'\" | Select-Object ProcessId,CommandLine | ConvertTo-Json -Depth 3"
], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=45, check=True)
processes = json.loads(proc.stdout.lstrip('\ufeff'))
if isinstance(processes, dict):
    processes = [processes]
known = ['tools/serve_pages_preview.py --site .scratch/pages-resources-202610',
         'archivecraft_dungeons01.py --execute', 'verify_v56_changes22.py --execute',
         'verify_pages_v55_remaining60.py --execute', 'recover_draft_upload.py --config',
         'publish_reviewed_release.py --config', 'verify_v56_public_assets.py']
active = [p for p in processes if any(s in (p.get('CommandLine') or '') for s in known)]
assert not active
free = shutil.disk_usage(ROOT).free
assert free >= 11005853696
now = datetime.now(timezone.utc)
assert now < datetime.fromisoformat('2026-10-22T14:51:33+00:00')
out = {
    'schema': 'wow-root-local-closeout/v1', 'accepted': True, 'checked_utc': now.isoformat(),
    'deadline_utc': '2026-10-22T14:51:33Z', 'within_budget': True, 'version': 'v56',
    'proofs': proofs, 'frozen_manifest_bindings': bindings,
    'frozen_scope': 'The four pinned manifests/provenance files were rehashed; prior accepted source/image/file inventories cover their payloads. No new full historical-ZIP pass was run.',
    'owned_preview_processes_stopped': [32040, 18428, 35312, 38116, 40912],
    'active_owned_preview_or_batch_processes': active,
    'unrelated_processes_untouched': True,
    'worker_states_observed': {'local_dungeon_trace_20261022': 'completed', 'network_dungeon_trace_20261022': 'completed'},
    'continuation_automation': {'id': 'wow-7-5', 'status': 'deleted', 'evidence': 'Native automation_update returned deleteStatus=deleted during root closeout'},
    'continuation_enabled': False, 'source_batches_closed': True,
    'new_source_network_after_cutoff': False, 'new_export_after_cutoff': False,
    'wayback_resume_gate_passed': False,
    'disk_free_bytes': free, 'disk_floor_bytes': 11005853696,
    'remaining_work': 'Commit and normally push the final documentation and curated receipts; no source acquisition remains active.',
}
outpath.write_bytes((json.dumps(out, ensure_ascii=False, indent=2)+'\n').encode())
print(json.dumps({'accepted': True, 'within_budget': True, 'active_owned_processes': len(active),
                  'disk_free_bytes': free, 'sha256': sha(outpath)}))
