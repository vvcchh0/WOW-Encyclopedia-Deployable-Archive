"""Verify the complete derived export and retained image overlays locally."""
import hashlib
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/continuous-recovery-20261015'
SITE=ROOT/'.scratch/pages-resources-20261015-v9'
def sha(data):
    return hashlib.sha256(data).hexdigest()
def main():
    provenance=json.loads((SITE/'export-provenance.json').read_text(encoding='utf-8'))
    prior=json.loads((ROOT/'.scratch/pages-resources-20261015-v8/export-provenance.json').read_text(encoding='utf-8'))
    spec=importlib.util.spec_from_file_location('wow_hygiene',ROOT/'research/github-publication-20261012/full-tree-hygiene.py')
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    expected={x['output_path']:x for x in provenance['files']}
    errors=[]
    findings=[]
    checked_bytes=0
    public_defaults={
        'info/basics/mounts/special.html':{'credential_literal_assignment'},
        'shared/wow-com/includes-client/detection.js':{'cookie_literal_assignment'},
        'wrath/js/detection.js':{'cookie_literal_assignment'},
    }
    for path in SITE.rglob('*'):
        if not path.is_file():
            continue
        relative=path.relative_to(SITE).as_posix()
        data=path.read_bytes()
        checked_bytes+=len(data)
        if relative in expected:
            record=expected[relative]
            if len(data)!=record['derived_length'] or sha(data)!=record['derived_sha256']:
                errors.append({'path':relative,'reason':'derived_hash_or_length'})
        elif relative!='export-provenance.json':
            errors.append({'path':relative,'reason':'undeclared_file'})
        for pattern in module.PATTERNS:
            if pattern.category in {'cookie_handling_field','authorization_field_without_value'}:
                continue
            matches=list(pattern.regex.finditer(data))
            if not matches:
                continue
            resolved=pattern.category in public_defaults.get(relative,set())
            if resolved:
                # A previous review identifies these fixed public markup and
                # cookie feature probes. Ensure each matching byte sequence
                # also exists in the accepted v8 output, without recording it.
                old=(ROOT/'.scratch/pages-resources-20261015-v8'/relative).read_bytes()
                resolved=all(match.group(0) in old for match in matches)
            findings.append({'path':relative,'category':pattern.category,'count':len(matches),
                'review':'unchanged previously reviewed public default' if resolved else 'needs review',
                'resolved':resolved})
        if re.search(rb'(?im)^(?:set-cookie|x-archive-orig-set-cookie|authorization|proxy-authorization):\s*\S+',data):
            errors.append({'path':relative,'reason':'raw_sensitive_http_header'})
    missing=[name for name in expected if not (SITE/name).is_file()]
    current={x['route']:x for x in provenance['files']}
    overlays=[]
    for old in prior['files']:
        if old['kind']!='image_overlay':
            continue
        new=current.get(old['route'],{})
        unchanged=all(new.get(key)==old.get(key) for key in ['original_url','derived_length','derived_sha256','source_sha256','actual_capture_timestamp','temporal_class'])
        overlays.append({'route':old['route'],'unchanged':unchanged})
    stats=provenance['stats']
    build=json.loads((OUT/'build-v9.json').read_text(encoding='utf-8'))
    report={'checked_utc':datetime.now(timezone.utc).isoformat(),'network_requests':0,
        'export_provenance_sha256':sha((SITE/'export-provenance.json').read_bytes()),
        'checked_declared_files':len(expected),'checked_tree_bytes':checked_bytes,'stats':stats,
        'missing_declared_files':missing,'errors':errors,'publication_findings':findings,
        'retained_overlay_checks':overlays,'implementation_stable':build['implementation_unchanged_during_export'],
        'manifest_matches_accepted':provenance['source_manifest_sha256']==json.loads((OUT/'root-v9-source-acceptance.json').read_text(encoding='utf-8'))['manifest_sha256']}
    report['accepted']=not(errors or missing) and all(x['resolved'] for x in findings) and len(overlays)==38 and all(x['unchanged'] for x in overlays) and stats['source_records']==8328 and stats['image_overlay_records']==38 and report['implementation_stable'] and report['manifest_matches_accepted']
    (OUT/'root-v9-export-acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:report[key] for key in ['accepted','checked_declared_files','checked_tree_bytes','stats','errors','publication_findings']}))
    if not report['accepted']:
        raise SystemExit(1)
if __name__=='__main__':
    main()
