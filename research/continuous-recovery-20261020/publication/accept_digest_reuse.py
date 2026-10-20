"""Independently check the two target-CDX/native-payload reuse chains offline."""
from pathlib import Path
from datetime import datetime, timezone
from io import BytesIO
import base64
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'research/continuous-recovery-20261020'
SHA = lambda b: hashlib.sha256(b).hexdigest()
def read(path):
    data = (ROOT / path).read_bytes()
    return json.loads(data), SHA(data)

def main():
    source, source_sha = read('research/continuous-recovery-20261020/local-audit/digest-reuse/r2/source-chain.json')
    manifest, manifest_sha = read('.scratch/offline-navigation-20261015-v15/build-manifest.json')
    assert manifest_sha == 'd89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002'
    capture, capture_sha = read('research/offline-2008/full-recovery/round-105-final-full-capture-map-validation.json')
    cdx, cdx_sha = read('research/site-recovery-2008/prefix-cdx/003-08c5d92edd079b20.json')
    assert cdx_sha == '54704b347c97dde8e50ca3bc6a26d3242b763643339005c5fd293cb970b8f229'
    assert len(source['routes']) == 2
    accepted = []
    for row in source['routes']:
        target = row['target']; evidence = target['cdx_evidence']
        rows = [dict(zip(cdx[0], r)) for r in cdx[1:] if r[1] == target['requested_original_url'] and r[0] == evidence['timestamp']]
        assert len(rows) == 1
        indexed = rows[0]
        assert indexed['statuscode'] == '200' and indexed['mimetype'] == 'image/jpeg'
        assert indexed['digest'] == evidence['digest']
        assert '20080101000000' <= indexed['timestamp'] <= '20080512210044'
        record = next(r for r in manifest['files'] if r['route'] == target['reuse_source_route'])
        declared = row['accepted_payload_source']['manifest_record']
        for key in ['source_base_url', 'actual_timestamp', 'source_sha256', 'source_length', 'source_local_path']:
            assert record[key] == declared[key], key
        assert record['transformed'] is False and record['source_sha256'] == record['derived_sha256']
        expected = record['source_sha256']; length = record['source_length']
        frames = []
        for path in [record['source_local_path'], record['output_path'], row['v38_payload']['path'], row['staged_local_copy']['path']]:
            data = (ROOT / path).read_bytes()
            assert len(data) == length and SHA(data) == expected, path
            digest = base64.b32encode(hashlib.sha1(data).digest()).decode('ascii').rstrip('=')
            assert digest == indexed['digest'], path
        with Image.open(BytesIO(data)) as image:
            assert image.format == 'JPEG'
            for frame in range(getattr(image, 'n_frames', 1)):
                image.seek(frame); image.load(); frames.append({'frame': frame, 'size': list(image.size)})
        source_rows = [r for block in capture['maps'] for r in block.get('item_evidence', []) if r.get('logical_url') == record['source_base_url'] and r.get('actual_sha256') == expected]
        assert len(source_rows) == 1 and source_rows[0]['accepted'] is True
        prior = source_rows[0]
        assert prior['actual_timestamp'] == record['actual_timestamp'] and prior['actual_length'] == length
        assert prior['calculated_cdx_digest'] == indexed['digest'] and prior['cdx_digest_match'] is True
        assert prior['zip_provenance'] == 'verified'
        assert not (ROOT / '.scratch/pages-resources-20261019-v38' / target['requested_route'].lstrip('/')).exists()
        accepted.append({'target_original_url': target['requested_original_url'], 'target_route': target['requested_route'],
            'recovery_method': 'payload_digest_reuse', 'target_indexed_capture_timestamp': indexed['timestamp'],
            'target_new_memento_observed': False, 'target_cdx_digest': indexed['digest'],
            'payload_source': {'original_url': record['source_base_url'], 'actual_capture_timestamp': record['actual_timestamp'],
                'sha256': expected, 'length': length, 'route': record['route']},
            'local_payload': row['staged_local_copy']['path'], 'decoded_frames': frames,
            'source_validation': {'path': 'research/offline-2008/full-recovery/round-105-final-full-capture-map-validation.json',
                'sha256': capture_sha, 'accepted_capture_row': prior['index']},
            'presentation': 'static_historical_promotion' if 'ordernow' in target['requested_route'] else 'historical_trailer_thumbnail'})
    receipt = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'network_requests': 0,
        'source_chain_sha256': source_sha, 'source_manifest_sha256': manifest_sha, 'target_cdx_file_sha256': cdx_sha,
        'accepted_images': len(accepted), 'routes': accepted,
        'qualifications': [
            'This recovers two image URL bindings from already preserved identical payloads; no fresh replay or new image download.',
            'The target CDX dates and the actual payload-source capture dates are distinct. CDX length is not entity length.',
            'r2 unknowns wrongly says the declared source map is absent; its own stat and this checkout show it exists. Source15 and accepted capture rows independently provide the source chain.',
            'r2 nominal metadata budget excludes 178751370 bytes of repeated earlier source-map hash reads; cumulative reads exceeded the original local audit budget. Frozen observations are retained.'
        ], 'published': False}
    path = BASE / 'publication/root-digest-reuse-source-acceptance.json'
    assert not path.exists()
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted_images': len(accepted), 'receipt': path.relative_to(ROOT).as_posix(), 'sha256': SHA(path.read_bytes())}))

if __name__ == '__main__':
    main()
