"""Create and verify the additive 17-gap evidence package, preserving old archives."""
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = 'WOW_Encyclopedia_20080512_gap_review_20261011.zip'
OLD = {
    'WOW_Encyclopedia_20101203_source.zip': '9b074874780d93c55a9edd98e2dd2d498c524e4dddd2d09fd4c981e03550437d',
    'WOW_Encyclopedia_20080512_sample_and_reassessment.zip': '5d23d49010d98049162ea7ce64a0c6f4b84ad8f519cc435c0d5e3a3ed8c2bd25',
    'WOW_Encyclopedia_20080512_full_source.zip': 'a8a41a5cb1e6a1a85fc5a379a6b3a53f860c720ca4f028c716fbee8ee7eb4e34',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def old_hashes():
    actual = {name: sha((ROOT/'artifacts'/name).read_bytes()) for name in OLD}
    if actual != OLD:
        raise RuntimeError('An old package differs from its recorded SHA-256')
    return actual


def guard(extra=0):
    used = sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
    free = shutil.disk_usage(ROOT).free
    if used + extra > 14_000_000_000 or free - extra < 10*1024**3 + 256*1024**2:
        raise RuntimeError('Workspace or D-drive safety boundary')
    return {'workspace_bytes':used, 'disk_free_bytes':free}


def main():
    destination = ROOT/'artifacts'/NAME
    if destination.exists():
        raise RuntimeError('Evidence package already exists; refusing to overwrite it')
    before = guard()
    unchanged_before = old_hashes()
    roots = [ROOT/'research/gap-review-20261011', ROOT/'backups/gap-review-20261011']
    paths = {p for root in roots for p in root.rglob('*') if p.is_file()
             and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    paths.update(ROOT/p for p in ['docs/gap-review-20261011.md', 'docs/acquisition-2008.md',
                                'README.md', 'packaging/package_gap_review.py'])
    files = []
    for p in sorted(paths):
        if p.is_symlink():
            raise RuntimeError('No symlinks allowed in package')
        name = p.relative_to(ROOT).as_posix()
        if ':' in name or '..' in Path(name).parts:
            raise RuntimeError('Nonportable archive path')
        data = p.read_bytes()
        files.append({'path':name,'bytes':len(data),'sha256':sha(data)})
    guard(sum(x['bytes'] for x in files) + 1_048_576)
    sums = ''.join(f'{x["sha256"]}  {x["path"]}\n' for x in files).encode('utf-8')
    with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for x in files:
            data = (ROOT/x['path']).read_bytes()
            if len(data) != x['bytes'] or sha(data) != x['sha256']:
                raise RuntimeError('Source changed during packaging')
            z.writestr(x['path'],data)
        z.writestr('FILE_SHA256SUMS.txt',sums)
    with zipfile.ZipFile(destination) as z:
        crc_failure = z.testzip()
        if crc_failure is not None:
            raise RuntimeError('Package CRC failure')
        if set(z.namelist()) != {x['path'] for x in files} | {'FILE_SHA256SUMS.txt'}:
            raise RuntimeError('Unexpected package member list')
        if z.read('FILE_SHA256SUMS.txt') != sums:
            raise RuntimeError('Checksum manifest mismatch')
        for x in files:
            data = z.read(x['path'])
            if sha(data) != x['sha256'] or len(data) != x['bytes']:
                raise RuntimeError('Packaged member mismatch')
            if sha((ROOT/x['path']).read_bytes()) != x['sha256']:
                raise RuntimeError('Source changed after packaging')
    digest = sha(destination.read_bytes())
    (ROOT/'artifacts'/(NAME+'.sha256')).write_text(f'{digest}  {NAME}\n',encoding='utf-8')
    result = {'created_utc':datetime.now(timezone.utc).isoformat(),
              'package':destination.relative_to(ROOT).as_posix(),'package_sha256':digest,
              'package_bytes':destination.stat().st_size,'source_files':len(files),
              'zip_entries':len(files)+1,'source_uncompressed_bytes':sum(x['bytes'] for x in files),
              'zip_crc_ok':True,'every_member_sha256_ok':True,'sources_unchanged':True,
              'old_packages_before':unchanged_before,'old_packages_after':old_hashes(),
              'old_packages_unchanged':True,'space_before':before,'space_after':guard(),'files':files}
    (ROOT/'artifacts/gap-review-20261011-package-verification.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
