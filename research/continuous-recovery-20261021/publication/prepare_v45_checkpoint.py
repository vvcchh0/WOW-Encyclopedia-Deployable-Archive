"""Prepare an exact public checkpoint list; leave private payloads untracked."""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = 'research/continuous-recovery-20261021/'
PUB = ROOT / BASE / 'publication'
status_path = ROOT / BASE / 'status.json'
status = json.loads(status_path.read_bytes())
status.update({
    'phase':'v45_root_accepted_main_sync_and_pages_publication',
    'current_local_version':'v45', 'candidate_version':'v45',
    'candidate_publication_accepted':True,
    'latest_local_acceptance':BASE+'publication/root-v45-local-acceptance.json',
    'candidate_review':BASE+'publication/root-v45-local-acceptance.json',
    'network_worker_current_task':'commoncrawl_pages02_three_body_difference_review',
    'local_worker_current_task':'six_related_talent_ui_loader',
    'prepared_network_batch':None, 'in_flight_network_batch':None,
    'latest_network_diagnosis':BASE+'publication/root-wayback-dns-tls-diagnosis.json',
    'accepted_main_new_body_pages_this_run':7,
    'accepted_main_updated_body_pages_this_run':1,
    'accepted_main_aliases_this_run':6,
    'accepted_related_ui_candidates':6,
    'accepted_layout_compatibility_target_paths':10,
    'disk_free_latest_bytes':shutil.disk_usage(ROOT).free,
    'updated_utc':datetime.now(timezone.utc).isoformat(),
})
status_path.write_bytes((json.dumps(status,indent=2)+'\n').encode())
tasks_path = ROOT / BASE / 'tasks.json'
tasks = json.loads(tasks_path.read_bytes())
for row in tasks['tasks']:
    if row['id']=='BUILD01':row['state']='v45_root_accepted_six_ui_followup_in_implementation'
    if row['id']=='FINAL':row['state']='v45_main_and_pages_publication_in_progress_v42_online_v39_release'
    if row['id']=='NET01':row['state']='three_new_cc_entities_acquired_body_difference_review_wayback_stopped'
    if row['id']=='TALENT02':row['state']='986_icons_root_accepted_v45_six_ui_candidate_prototype_passed'
tasks_path.write_bytes((json.dumps(tasks,indent=2)+'\n').encode())
paths = ['README.md','CHANGELOG.md','NOTICE.md','docs/continuous-recovery-20261021.md',
         'docs/non-gallery-restoration-20261021.md','tools/export_github_pages.py',
         'tools/historical_exhibits.py','tools/related_talent_icons.py','tools/source16_layout_compat.py',
         'tests/test_battlegrounds_historical_entry.py','tests/test_related_talent_icons.py',
         'tests/test_related_talent_pages.py','tests/test_source16_layout_compat.py',
         'tests/test_source16_layout_pages.py','tests/test_source16_page_metadata.py',
         BASE+'status.json',BASE+'tasks.json']
public_files = [
    'accept_main_pages_sources.py','accept_source16.py','accept_v43_tree.py','accept_v45_tree.py',
    'accept_dns_diagnostics.py','check_v45_code.py','execute_v45_once.py','make_v45_local_acceptance.py',
    'prepare_v45_checkpoint.py','verify_accepted_pages.py','curate_v44_browser_receipt.py',
    'root-main-pages-source-acceptance.json','root-source16-build-go.json',
    'root-source16-guide-rebinding-acceptance.json','root-source16-layout-reuse-decision.json',
    'root-source16-local-acceptance.json','root-talent-original-evidence-acceptance.json',
    'root-talent-related-source-acceptance.json','root-talent-repository-metadata-acceptance.json',
    'root-related-talent-icon-integration-decision.json','talent-related-image-inventory.json',
    'root-v43-code-acceptance.json','root-v43-entry-browser.json','root-v43-export-acceptance.json',
    'root-v43-export-go-r2.json','root-v43-local-acceptance.json','root_v43_entry_probe.js',
    'root-v44-candidate-review.json','root-v44-code-acceptance.json','root-v44-export-go.json',
    'root-v45-browser-acceptance.json','root-v45-browser-attempt1.json','root-v45-browser-attempt2.json',
    'root-v45-code-acceptance.json','root-v45-export-acceptance.json','root-v45-export-go.json',
    'root-v45-local-acceptance.json','root_v45_browser.js','root_v45_browser_attempt1.js',
    'root-wayback-dns-tls-diagnosis.json','v43-export-execution-r2.json',
    'v44-export-execution.json','v44-related-icon-code-tests.json','v44-related-icon-code-tests.log',
    'v45-code-tests.log','v45-export-execution.json','v45-export-execution.log',
]
paths += [BASE+'publication/'+name for name in public_files]
paths += [BASE+p for p in (
    'integration/main-pages-review/source16-input-map.json','integration/source16/build_source16.py',
    'integration/source16/execution-receipt.json','integration/source16/layout-compatibility/input-map.json',
    'integration/source16/layout-compatibility/prepare-receipt.json',
    'integration/source16/dependency-audit/README.md','integration/source16/dependency-audit/SUMMARY.md',
    'integration/source16/dependency-audit/audit_dependencies.py',
    'integration/source16/dependency-audit/dependency-audit.json',
    'integration/source16/original-resource-audit/README.md',
    'integration/source16/original-resource-audit/audit_source16_original.py',
    'integration/source16/original-resource-audit/curated-inventory.json',
    'integration/source16/original-resource-audit/candidate-summary.json',
    'integration/related-talent-icons/input-map.json',
    'integration/related-talent-icons/prepare-receipt-r2.json',
    'integration/v43/export_v43_r2_once.py','integration/v43/v43-build-receipt-r2.json',
    'integration/v43/source16-guide-preview-map.json','integration/v43/source16-guide-image-collection-map.json',
    'integration/v44/export_v44_once.py','integration/v44/v44-build-receipt.json',
    'integration/v45/export_v45_once.py','integration/v45/v45-input-preparation.json',
    'integration/v45/v45-build-receipt.json',
    'local-audit/v43/v43-browser-receipt.json','local-audit/v43/SUMMARY.md',
    'local-audit/v44/v44-browser-summary.json','local-audit/v44/v44-gap-union-reconciliation.json',
    'local-audit/v44/v44-gap-union-reconciliation.md','local-audit/v44/run_v44_browser_audit.js',
    'network/talent-repo-metadata01/runtime/public/repository-metadata.json',
    'network/wayback-tls-diagnostic01/runtime/public/diagnostic-summary.json',
    'network/wayback-dns-comparison01/public/dns-summary.json',
    'network/wayback-resolved-tls01/public/resolved-tls-summary.json',
)]
paths += [BASE+'publication/v45-screenshots-r2/'+name for name in (
    'tinfoil-tooltip.png','tinfoil-page.png','moltencore-footer.png','contest-note.png',
)]
assert len(paths)==len(set(paths))
for name in paths:
    assert (ROOT/name).is_file(),name
    assert not any(part in {'private','raw','runtime-r2'} for part in Path(name).parts), name
config = {
    'paths':paths,'receipt':BASE+'publication/root-v45-staged-hygiene.json',
    'scope':'Accepted Source16/v45 reading pages, 986 separately attributed icons, ten layout reuses, historical contest wording and exact root checks. No raw HTTP or forensic payloads.',
}
out = PUB / 'v45-stage-config-r2.json'
assert not out.exists()
out.write_bytes((json.dumps(config,indent=2)+'\n').encode())
print(json.dumps({'public_paths':len(paths),'bytes':sum((ROOT/p).stat().st_size for p in paths),'disk_free_bytes':status['disk_free_latest_bytes']}))
