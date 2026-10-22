"""Curate the second checkpoint without adding raw HTTP or forensic archives."""
from pathlib import Path
import argparse,json,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[3];HERE=ROOT/'research/continuous-recovery-20261022'

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--stage',action='store_true');args=parser.parse_args()
 rels='accept_v55_online_partial.py accept_v55_online.py prepare_v56_inputs.py prepare_v56.py accept_v56_export.py accept_v56_browser.py\n root-v55-online-partial-acceptance9.json root-v55-online-acceptance.json root-v55-remaining60-go.json\n root-v56-code-acceptance.json root-v56-export-acceptance.json root-v56-browser-acceptance.json v56-remaining-resource-targets.json\n integration/v56-input-preparation.json integration/v56-build-receipt.json integration/v56-root-focused-tests.log\n integration/v56-root-visual-recheck.cjs integration/v56-root-visual-software-recheck.cjs\n publication/v55-public-release-publish.json publication/v55-public-assets-acceptance.json publication/v55-release-notes.md\n publication/publish_v55_release.py publication/publish_v55_release.initial.py publication/verify_v55_public_assets.py\n publication/v55-release-runtime-r3/create-upload-intent.json publication/v55-release-runtime-r3/create-upload-receipt.json publication/v55-release-runtime-r3/draft-visible-adapter-receipt.json\n publication/release-tools/recover_draft_upload.py publication/release-tools/test_draft_visible.py\n publication/prepare_v56_commit.py publication/v56-portable-config.json publication/v56-portable-package-report.json'.split()
 paths={HERE/r for r in rels}
 v56=HERE/'integration/related-talent-icons-v56'
 for name in ['input-map.json','input-map.initial-draft.json','decision.json','root-input-pins.json','root-source-acceptance.json','source-preparation.json']:
  paths.add(v56/name)
 paths.update(p for p in (v56/'assets').iterdir() if p.is_file())
 for name in ['README.md','validation.json','browser-check.cjs']:paths.add(v56/'implementation'/name)
 for directory in ['talent-icon-remaining-audit','integration/v56-root-visual-recheck','integration/v56-root-visual-software-recheck','integration/v56-local-paint-comparison','integration/v56-paint-prototype']:
  base=HERE/directory
  for p in base.rglob('*'):
   if p.is_file() and p.suffix in ['.json','.png','.md','.cjs','.py'] and '__pycache__' not in p.parts:paths.add(p)
 for run in ['v56-2026-10-22T12-41-13-622Z','v56-2026-10-22T12-42-28-056Z']:
  paths.update(p for p in (v56/'implementation/runs'/run).iterdir() if p.is_file() and p.suffix in ['.json','.png'])
 for batch in ['github-pages-v55-changes69','github-pages-v55-remaining60','github-pages-v56-changes22']:
  base=HERE/'network'/batch
  paths.update(p for p in base.iterdir() if p.is_file() and p.suffix in ['.json','.md','.py'])
  p=base/'runtime/object-match-summary.json'
  if p.exists():paths.add(p)
 paths.update(p for p in (HERE/'publication').glob('pages-build-20261022T1151*.json'))
 relative=[]
 for p in sorted(paths):
  assert p.is_file() and not p.is_symlink(),p
  assert not any(x in ['private','raw','__pycache__'] for x in p.parts),p
  assert p.stat().st_size<8*1024*1024,p
  relative.append(p.relative_to(ROOT).as_posix())
 output=HERE/'publication-paths-v56.json';payload=(json.dumps(relative,indent=2)+'\n').encode()
 if output.exists():assert output.read_bytes()==payload,'Refuse allowlist drift'
 else:output.write_bytes(payload)
 relative.append(output.relative_to(ROOT).as_posix())
 code_docs=['.gitignore','tools/related_talent_icons.py','tests/test_related_talent_icons_v3.py','README.md','CHANGELOG.md','docs/README.md','docs/talent-image-sources-20261022.md','docs/continuous-recovery-20261022.md','research/continuous-recovery-20261022/status.json','research/continuous-recovery-20261022/tasks.json']
 ignore=ROOT/'.gitignore';data=ignore.read_bytes().replace(b'\r\n',b'\n')
 for rel in relative+code_docs:
  rule=('!/'+rel).encode()
  if rule not in data.splitlines():data+=rule+b'\n'
 ignore.write_bytes(data)
 if args.stage:
  subprocess.run(['git','add','--']+relative+code_docs,cwd=ROOT,check=True)
  subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
 print(json.dumps({'files':len(relative),'bytes':sum((ROOT/r).stat().st_size for r in relative),'staged':args.stage,'allowlist_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
