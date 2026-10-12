"""Package the derived site without changing earlier preservation archives."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'artifacts/WOW_Encyclopedia_20080512_offline_20261011.zip'
RECOVERY_DEST = ROOT / 'artifacts/WOW_Encyclopedia_20080512_offline_recovery_20261011.zip'
REPORT = ROOT / 'artifacts/offline-20261011-package-verification.json'
RECOVERY_REPORT = ROOT / 'artifacts/offline-20261011-recovery-package-verification.json'
V1_ARCHIVE = 'WOW_Encyclopedia_20080512_offline_20261011.zip'
V1_ARCHIVE_SHA256 = 'cfa0d0b34442759868905b8ab08ec2dde4270d4e7538eba7d7dcc2d9dfb6d5ae'
HISTORICAL = {
    'WOW_Encyclopedia_20101203_source.zip': '9b074874780d93c55a9edd98e2dd2d498c524e4dddd2d09fd4c981e03550437d',
    'WOW_Encyclopedia_20080512_sample_and_reassessment.zip': '5d23d49010d98049162ea7ce64a0c6f4b84ad8f519cc435c0d5e3a3ed8c2bd25',
    'WOW_Encyclopedia_20080512_full_source.zip': 'a8a41a5cb1e6a1a85fc5a379a6b3a53f860c720ca4f028c716fbee8ee7eb4e34',
    'WOW_Encyclopedia_20080512_gap_review_20261011.zip': 'c7dc499ce7daf53422d48ff7b777cd2970e8b47768c6cb02dab925b046a95483',
}


RECOVERY_REQUIRED_DIRECTORIES = (
    'offline/source-entities-pages-recovery',
    'offline/source-entities-resources-recovery',
    'offline/source-entities-static-support',
    'research/site-recovery-2008',
    'research/resource-recovery-2008',
    'backups/site-recovery-2008',
    'backups/resource-recovery-2008',
    'research/finite-gallery-audit',
    'research/runtime-page-audit-round3',
    'research/runtime-page-audit-round4',
    'research/runtime-page-audit-round5',
    'research/runtime-page-audit-round6',
    'research/static-queue-audit',
    'research/pre2008-supplement-validation',
    'research/transport-reuse-study',
    'research/scriptaculous-compat-study',
    'research/resource-gap-coverage-audit',
    'research/browser-audit-concurrency',
    'research/browser-retry-reconciliation',
    'research/final-gap-closure-20261012',
    'research/final-single-image-followup-20261012',
    'backups/final-single-image-followup-20261012',
    'research/final-cdx-image-wave-20261012',
    'backups/final-cdx-image-wave-20261012',
    'research/final-pre2008-image-wave-20261012',
    'backups/final-pre2008-image-wave-20261012',
    'research/navtree-recovery-20261012',
    'research/shared-gap-priority-20261012',
    'research/policy-runtime-recovery-20261012',
    'research/non-image-gap-audit-20261012',
    'research/non-image-gap-followup-20261012',
    'research/shared-image-final-followup-20261012',
    'backups/shared-image-final-followup-20261012',
    'research/pre2008-candidate-followup-20261012',
    'offline/support/vendor/scriptaculous-1.6.5',
)
RECOVERY_REQUIRED_FILES = (
    'research/offline-2008/full-recovery/browser-validation.json',
    'docs/resource-recovery-2008.md',
    'tests/test_offline_mirror.py',
    'tests/test_offline_packaging.py',
    'tests/test_wayback_backup.py',
    'tests/test_wayback_pooled_transport.py',
    'tests/test_recovery_sources.py',
    'tests/test_recovery_map_adapter.py',
    'offline/upstream-compatibility-map.json',
    'tests/test_upstream_compatibility.py',
    'tools/wayback_pooled_transport.py',
    'tools/reconcile_offline_browser_retries.py',
)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def histories() -> dict:
    result = {name: sha((ROOT / 'artifacts' / name).read_bytes()) for name in HISTORICAL}
    if result != HISTORICAL:
        raise RuntimeError('Historical archive hash mismatch')
    return result


def v1_archive_hash() -> str:
    path = ROOT / 'artifacts' / V1_ARCHIVE
    if not path.is_file():
        raise RuntimeError(f'Previous v1 archive is missing: {path}')
    actual = sha(path.read_bytes())
    if actual != V1_ARCHIVE_SHA256:
        raise RuntimeError('Previous v1 archive hash mismatch')
    return actual

def budget() -> None:
    total = sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
    if total >= 14_000_000_000 or shutil.disk_usage(ROOT).free < 10 * 1024**3 + 256 * 1024**2:
        raise RuntimeError('Workspace/disk budget guard stopped packaging')

def root_path(value: str | Path) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else ROOT / path).resolve()


def recovery_gap_summary(browser: dict) -> dict:
    pages = browser.get('pages') if isinstance(browser.get('pages'), list) else []
    sidebar = browser.get('sidebar') if isinstance(browser.get('sidebar'), list) else []
    failed_pages = [
        item.get('route') or item.get('path') or item.get('url')
        for item in pages
        if isinstance(item, dict) and not item.get('accepted', False)
    ]
    uncollected_sidebar = [
        item.get('route') or item.get('original')
        for item in sidebar
        if isinstance(item, dict) and item.get('collected') is False
    ]
    return {
        'restoration_complete': browser.get('restoration_complete'),
        'failed_page_routes': [value for value in failed_pages if value],
        'uncollected_sidebar_routes': [value for value in uncollected_sidebar if value],
        'placeholder_count': len(browser.get('placeholders', [])) if isinstance(browser.get('placeholders'), list) else None,
        'resource_failure_count': len(browser.get('resource_failures', [])) if isinstance(browser.get('resource_failures'), list) else None,
        'page_error_count': len(browser.get('page_errors', [])) if isinstance(browser.get('page_errors'), list) else None,
        'nonlocal_request_count': len(browser.get('nonlocal_requests', [])) if isinstance(browser.get('nonlocal_requests'), list) else None,
        'unavailable_dynamic_data_count': len(browser.get('unavailable_dynamic_data', [])),
        'unavailable_dynamic_data': browser.get('unavailable_dynamic_data', []),
        'accepted_page_count': sum(1 for item in pages if isinstance(item, dict) and item.get('accepted') is True),
        'page_count': len(pages),
        'collected_sidebar_count': sum(1 for item in sidebar if isinstance(item, dict) and item.get('collected') is True),
        'sidebar_count': len(sidebar),
    }


def browser_document_routes(manifest: dict) -> list[str]:
    """Return the exact document route scope used by browser-check.js."""

    def is_document(item: dict) -> bool:
        mime = str(item.get('mime') or '')
        kind = item.get('kind')
        role = item.get('role')
        return (
            kind != 'generated_placeholder'
            and (
                bool(re.search(r'text/html|application/xhtml\+xml', mime, re.I))
                or (kind == 'xml' and role == 'site_recovery_sidebar_page')
            )
        )

    return sorted(
        str(item.get('route'))
        for item in manifest.get('files', [])
        if isinstance(item, dict) and item.get('route') and is_document(item)
    )


def validate_full_browser_record(browser: dict, manifest: dict, manifest_sha: str) -> None:
    """Validate all-manifest browser evidence without requiring zero gaps."""

    if browser.get('accepted') is not True:
        raise RuntimeError('Full recovery browser acceptance did not pass')
    if (
        browser.get('audit_scope') != 'all-manifest-documents'
        or 'requested_routes' not in browser
        or browser.get('requested_routes') is not None
    ):
        raise RuntimeError('Full recovery browser acceptance is not an all-document audit')
    for key in ('targeted_passed', 'build_unchanged', 'server_unchanged'):
        if browser.get(key) is not True:
            raise RuntimeError(f'Full recovery browser acceptance missing true {key}')
    if browser.get('build_manifest_sha256') != manifest_sha:
        raise RuntimeError('Full recovery browser acceptance belongs to another build')
    if browser.get('server_manifest_sha256') != manifest_sha:
        raise RuntimeError('Full recovery browser acceptance served another build')

    expected_routes = browser_document_routes(manifest)
    pages = browser.get('pages')
    if not isinstance(pages, list):
        raise RuntimeError('Full recovery browser acceptance omitted pages')
    observed_routes = [item.get('route') for item in pages if isinstance(item, dict)]
    if len(observed_routes) != len(pages) or any(not isinstance(route, str) or not route for route in observed_routes):
        raise RuntimeError('Full recovery browser pages contain a missing route')
    if len(observed_routes) != len(set(observed_routes)):
        raise RuntimeError('Full recovery browser pages contain duplicate routes')
    if set(observed_routes) != set(expected_routes):
        missing = sorted(set(expected_routes) - set(observed_routes))
        extra = sorted(set(observed_routes) - set(expected_routes))
        raise RuntimeError(f'Full recovery browser pages do not match manifest documents; missing={missing[:3]} extra={extra[:3]}')
    if any(item.get('accepted') is not True for item in pages):
        raise RuntimeError('Full recovery browser contains a failed page')
    if browser.get('expected_pages') != len(expected_routes) or browser.get('all_manifest_documents') != len(expected_routes):
        raise RuntimeError('Full recovery browser page counts do not match the manifest')
    if browser.get('expected_pages') != browser.get('all_manifest_documents'):
        raise RuntimeError('Full recovery browser expected/all-document counts disagree')

    for key in ('page_errors', 'resource_failures', 'nonlocal_requests'):
        value = browser.get(key)
        if not isinstance(value, list) or value:
            raise RuntimeError(f'Full recovery browser has non-empty {key}')

    sidebar = browser.get('sidebar')
    if not isinstance(sidebar, list):
        raise RuntimeError('Full recovery browser acceptance omitted sidebar records')
    if any(not isinstance(item, dict) or not isinstance(item.get('collected'), bool) for item in sidebar):
        raise RuntimeError('Full recovery browser sidebar records are malformed')
    placeholders = browser.get('placeholders')
    if not isinstance(placeholders, list):
        raise RuntimeError('Full recovery browser acceptance omitted placeholder records')
    if any(not isinstance(item, dict) or not isinstance(item.get('scope'), str) for item in placeholders):
        raise RuntimeError('Full recovery browser placeholder records are malformed')
    in_scope = sum(
        1
        for item in placeholders
        if isinstance(item, dict)
        and not str(item.get('scope') or '').startswith('excluded-')
        and item.get('scope') != 'external-excluded'
    )
    if browser.get('in_scope_placeholder_references') != in_scope:
        raise RuntimeError('Full recovery browser in-scope placeholder count is inconsistent')
    excluded = browser.get('excluded_external_placeholder_references')
    if not isinstance(excluded, int) or isinstance(excluded, bool) or excluded != len(placeholders) - in_scope:
        raise RuntimeError('Full recovery browser excluded placeholder count is inconsistent')
    sidebar_complete = all(isinstance(item, dict) and item.get('collected') is True for item in sidebar)
    expected_restoration = bool(browser.get('accepted') is True and sidebar_complete and in_scope == 0)
    if not isinstance(browser.get('restoration_complete'), bool):
        raise RuntimeError('Full recovery browser omitted boolean restoration_complete')
    if browser.get('restoration_complete') is not expected_restoration:
        raise RuntimeError('Full recovery restoration_complete disagrees with sidebar/placeholder evidence')


def validate_browser(manifest_path: Path, *, recovery: bool) -> tuple[dict, dict | None, dict]:
    manifest_sha = sha(manifest_path.read_bytes())
    if recovery:
        browser_path = ROOT / 'research/offline-2008/full-recovery/browser-validation.json'
        browser = json.loads(browser_path.read_text(encoding='utf-8'))
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        validate_full_browser_record(browser, manifest, manifest_sha)
        return browser, None, recovery_gap_summary(browser)

    browser = json.loads((ROOT / 'research/offline-2008/acceptance/browser-validation.json').read_text(encoding='utf-8'))
    if not browser.get('accepted'):
        raise RuntimeError('Current browser acceptance did not pass')
    if browser.get('build_manifest_sha256') != manifest_sha:
        raise RuntimeError('Browser acceptance belongs to another build')
    expansion = json.loads((ROOT / 'research/offline-2008/acceptance/expansion-browser-validation.json').read_text(encoding='utf-8'))
    if not expansion.get('accepted') or expansion.get('build_manifest_sha256') != browser['build_manifest_sha256']:
        raise RuntimeError('Expansion browser acceptance did not pass for the same build')
    return browser, expansion, recovery_gap_summary(browser)


def recovery_assets() -> tuple[list[str], list[str]]:
    missing = [name for name in RECOVERY_REQUIRED_DIRECTORIES if not (ROOT / name).is_dir()]
    missing.extend(name for name in RECOVERY_REQUIRED_FILES if not (ROOT / name).is_file())
    # Recovery maps can live beside the extracted entity directories or at the
    # workspace's offline root.  Include every JSON map that is present while
    # keeping the old v1 file set untouched in default mode.
    map_files: set[Path] = set()
    for base in (ROOT / 'offline', ROOT / 'offline/source-entities-pages-recovery', ROOT / 'offline/source-entities-resources-recovery'):
        if base.is_dir():
            map_files.update(p for p in base.rglob('*.json') if 'map' in p.name.casefold())
    recovery_scripts = sorted({
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / 'tools').glob('*.py')
        if 'recover' in p.name.casefold() or 'recovery' in p.name.casefold()
    })
    if not recovery_scripts:
        missing.append('tools/*recover*.py or tools/*recovery*.py')
    return sorted(p.relative_to(ROOT).as_posix() for p in map_files), recovery_scripts


def select_files(*, recovery: bool) -> tuple[dict[str, Path], list[str], list[str]]:
    roots = ['offline/site', 'offline/support', 'offline/source-entities', 'research/offline-2008',
             'research/site-expansion-2008', 'backups/site-expansion-2008', 'site-expansion-2008']
    names = ['START_OFFLINE.cmd', 'tools/launch_offline_mirror.ps1', 'tools/offline_mirror.py',
             'tools/expand_wayback_site.py', 'tools/wayback_backup.py', 'offline/README.md',
             'docs/offline-reconstruction-2008.md', 'mirror/20080512/url-map.json', 'offline/approved-expansion-map.json']
    recovery_maps: list[str] = []
    recovery_scripts: list[str] = []
    if recovery:
        recovery_maps, recovery_scripts = recovery_assets()
        roots.extend([
            'offline/source-entities-pages-recovery',
            'offline/source-entities-resources-recovery',
            'research/site-recovery-2008',
            'research/resource-recovery-2008',
            'backups/site-recovery-2008',
            'backups/resource-recovery-2008',
            'research/sol-wayback-methods',
            'research/sol-wow-structure',
            'research/page-frontier-audit',
            'research/derived-script-audit',
            'research/runtime-page-audit',
            'research/runtime-page-audit-round2',
            'research/runtime-page-audit-round3',
            'research/runtime-page-audit-round4',
            'research/finite-gallery-audit',
            'research/pre2008-supplement-validation',
            *RECOVERY_REQUIRED_DIRECTORIES,
        ])
        names.extend([
            'docs/resource-recovery-2008.md',
            'docs/sol-wayback-methods.md',
            'docs/sol-wow-structure.md',
            'packaging/package_offline_mirror.py',
            'packaging/smoke_offline_package.py',
            'research/offline-2008/full-recovery/browser-validation.json',
            'tests/test_offline_mirror.py',
            'tests/test_offline_packaging.py',
            *recovery_maps,
            *recovery_scripts,
            *RECOVERY_REQUIRED_FILES,
        ])
    selected: dict[str, Path] = {}
    for name in names:
        p = ROOT / name
        if p.is_file():
            selected[name] = p
    for folder in roots:
        base = ROOT / folder
        if base.exists():
            for p in base.rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc':
                    selected[p.relative_to(ROOT).as_posix()] = p
    selected['offline/build-manifest.json'] = ROOT / 'offline/build-manifest.json'
    if recovery:
        # Report only map JSON files that are actually in the selected ZIP
        # input set; the old directory-only discovery omitted research maps.
        recovery_maps = sorted(
            name for name, path in selected.items()
            if path.suffix.casefold() == '.json' and 'map' in path.name.casefold()
        )
    return selected, recovery_maps, recovery_scripts


def package(*, archive: Path, report: Path, recovery: bool) -> dict:
    archive = archive.resolve()
    report = report.resolve()
    if archive.exists():
        raise FileExistsError(f'Refusing to overwrite {archive}')
    if report.exists():
        raise FileExistsError(f'Refusing to overwrite {report}')
    manifest_path = ROOT / 'offline/build-manifest.json'
    browser, expansion, gap_summary = validate_browser(manifest_path, recovery=recovery)
    budget()
    before = histories()
    before_v1 = v1_archive_hash()
    selected, recovery_maps, recovery_scripts = select_files(recovery=recovery)
    if recovery:
        missing = [name for name in RECOVERY_REQUIRED_DIRECTORIES if not (ROOT / name).is_dir()]
        missing.extend(name for name in RECOVERY_REQUIRED_FILES if not (ROOT / name).is_file())
        if missing:
            raise RuntimeError('Recovery package inputs missing: ' + ', '.join(missing))
    records = []
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, p in sorted(selected.items()):
            data = p.read_bytes()
            records.append({'path': name, 'bytes': len(data), 'sha256': sha(data)})
            z.writestr(name, data)
        z.writestr('FILE_SHA256SUMS.txt', ''.join(f"{r['sha256']}  {r['path']}\n" for r in records))
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad: raise RuntimeError(f'ZIP CRC failed: {bad}')
        for r in records:
            if sha(z.read(r['path'])) != r['sha256']:
                raise RuntimeError(f"ZIP content digest failed: {r['path']}")
    after = histories()
    after_v1 = v1_archive_hash()
    digest = sha(archive.read_bytes())
    archive.with_suffix(archive.suffix + '.sha256').write_text(f'{digest}  {archive.name}\n', encoding='ascii')
    result = {'created_utc': datetime.now(timezone.utc).isoformat(),
              'archive': archive.relative_to(ROOT).as_posix() if archive.is_relative_to(ROOT) else str(archive), 'bytes': archive.stat().st_size,
              'sha256': digest, 'files': len(records), 'source_bytes': sum(x['bytes'] for x in records),
              'crc_verified': True, 'member_sha256_verified': True,
              'historical_archives_unchanged': before == after, 'historical_sha256': after,
              'previous_v1_archive_unchanged': before_v1 == after_v1, 'previous_v1_archive_sha256': after_v1,
              'browser_accepted': bool(browser.get('accepted')), 'expansion_browser_accepted': bool(expansion and expansion.get('accepted')) if expansion else None,
              'recovery_mode': recovery, 'restoration_complete': gap_summary.get('restoration_complete'),
              'recovery_gaps': gap_summary, 'recovery_maps': recovery_maps, 'recovery_scripts': recovery_scripts,
              'build_manifest_sha256': browser['build_manifest_sha256'], 'members': records}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    budget()
    print(json.dumps({k:v for k,v in result.items() if k not in {'members','historical_sha256'}}, ensure_ascii=False))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, help='new ZIP path; defaults to the v1 path or the recovery path with --recovery')
    parser.add_argument('--report', type=Path, help='verification JSON path; defaults beside the selected archive')
    parser.add_argument('--recovery', action='store_true', help='package the full site/resource recovery inputs and require full-recovery browser acceptance')
    args = parser.parse_args(argv)
    archive = root_path(args.archive or (RECOVERY_DEST if args.recovery else DEST))
    if args.report:
        report = root_path(args.report)
    elif args.recovery:
        report = RECOVERY_REPORT
    elif args.archive:
        report = archive.with_name(archive.stem + '-verification.json')
    else:
        report = REPORT
    package(archive=archive, report=report, recovery=args.recovery)
    return 0

if __name__ == '__main__': raise SystemExit(main())
