"""Prepare an explicit public research allowlist; never stage private sources."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'research/continuous-recovery-20261022'
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');args=parser.parse_args()
 names='''accept_coolwow2_sources.py accept_v54_browser.py accept_v54_export.py accept_v55_browser.py accept_v55_export.py
 prepare_arrow_ui_v54.py prepare_faction_ui_v54.py prepare_talent_remaps_v55.py prepare_v54.py prepare_v55.py
 root-coolwow2-item-icons01-go.json root-coolwow2-item-source-acceptance.json coolwow2-selected-source-tree.json coolwow2-source-lead.json
 root-v53-online-acceptance.json root-v53-online-go.json root-v54-browser-acceptance.json root-v54-code-acceptance.json root-v54-export-acceptance.json
 root-v54-faction-browser-acceptance.json root-v54-talent-ui-code-acceptance.json root-v55-browser-acceptance.json root-v55-code-acceptance.json root-v55-export-acceptance.json
 check_v54_factions.cjs faction-v54-aldor.png faction-v54-zangarmarsh.png v53-known-missing-targets.json v55-remaining-resource-targets.json
 tbc-related-repository-leads.json additional-icon-repository-checks.json push_reviewed_branch.py push-gh-pages-f068318e.json push-main-6e9acf13.json v53-pages-prepare.json'''.split()
 paths={HERE/n for n in names}
 for directory in ('related-talent-ui-v54','related-faction-icons-v54','related-talent-icons-v55'):
  base=HERE/'integration'/directory
  paths.update(base/n for n in ('input-map.json','decision.json','root-input-pins.json'))
  paths.update(p for p in (base/'assets').rglob('*') if p.is_file())
  paths.add(base/'implementation/README.md')
 paths.update(HERE/p for p in (
  'integration/related-faction-icons-v54/implementation/validation-report.json',
  'integration/related-talent-icons-v55/implementation/validation.json',
  'integration/related-talent-icons-v55/implementation/browser-check.cjs',
  'integration/v54-input-preparation.json','integration/v54-build-receipt.json','integration/v54-root-focused-tests.log',
  'integration/v55-input-preparation.json','integration/v55-build-receipt.json','integration/v54-browser/check_v54_talent_ui.cjs',
  'publication/prepare_v55_commit.py','publication/v55-portable-config.json','publication/v55-portable-package-report.json'))
 for directory in ('talent-icon-reuse-audit','faction-related-candidates','publication/portable-check','publication/release-tools'):
  paths.update(p for p in (HERE/directory).iterdir() if p.is_file() and p.suffix in ('.json','.md','.py','.png'))
 for run in ('integration/v54-browser/runs/v54-2026-10-22T10-57-21-881Z','integration/related-talent-icons-v55/implementation/runs/v55-2026-10-22T11-25-38-127Z'):
  paths.update(p for p in (HERE/run).iterdir() if p.is_file() and p.suffix in ('.json','.png'))
 paths.update(p for p in (HERE/'integration/faction-icons-candidates/assets').iterdir() if p.is_file() and p.suffix=='.jpg')
 for batch in ('coolwow2-item-icons01','github-pages-v53-changes06'):
  base=HERE/'network'/batch
  paths.update(p for p in base.iterdir() if p.is_file() and p.suffix in ('.py','.json','.md'))
  for name in ('public-inventory.json','object-match-summary.json'):
   p=base/'runtime'/name
   if p.exists():paths.add(p)
  watch=base/'parent-watchdog-attempt01'
  if watch.is_dir():paths.update(p for p in watch.iterdir() if p.is_file() and p.suffix in ('.json','.py','.md'))
 relative=[]
 for p in sorted(paths):
  assert p.is_file() and not p.is_symlink(),p
  rel=p.relative_to(ROOT).as_posix()
  assert not any(part in ('private','raw','__pycache__') for part in p.parts),p
  assert p.stat().st_size<8*1024*1024,p
  relative.append(rel)
 output=HERE/'publication-paths-v55.json'
 payload=(json.dumps(relative,indent=2)+'\n').encode()
 if output.exists():assert output.read_bytes()==payload,'existing allowlist changed'
 else:output.write_bytes(payload)
 relative.append(output.relative_to(ROOT).as_posix())
 ignore=ROOT/'.gitignore';data=ignore.read_bytes().replace(b'\r\n',b'\n')
 for rel in relative:
  rule=('!/'+rel).encode()
  if rule not in data.splitlines():data+=rule+b'\n'
 ignore.write_bytes(data)
 code_docs=['.gitignore','CHANGELOG.md','README.md','docs/continuous-recovery-20261022.md',
  'research/continuous-recovery-20261022/status.json','research/continuous-recovery-20261022/tasks.json',
  'tools/related_faction_icons.py','tools/related_talent_icons.py','tools/related_talent_ui.py','tools/export_github_pages.py',
  'tests/test_related_faction_icons.py','tests/test_related_faction_icons_pages.py','tests/test_related_talent_icons_v2.py','tests/test_related_talent_ui.py','tests/test_related_talent_ui_pages.py']
 if args.stage:
  subprocess.run(['git','add','--']+code_docs+relative,cwd=ROOT,check=True)
  subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
 print(json.dumps({'research_files':len(relative),'research_bytes':sum((ROOT/p).stat().st_size for p in relative),'stage_requested':args.stage,'allowlist_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
