"""Check private DNS wire evidence and publish only its relevant findings."""
import hashlib
import ipaddress
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261020'
PACKET = RUN / 'network/dns-diagnosis01'
OUT = RUN / 'publication/root-dns-diagnosis-acceptance.json'
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


def main():
    assert not OUT.exists()
    report = READ(PACKET / 'diagnosis-report.json')
    correction = READ(PACKET / 'diagnosis-correction.json')
    assert SHA(PACKET / 'diagnosis-report.json') == 'de3617bfe3cd2eb19ab9e2d2ef42614920ea46221eb83f4c9cacaa4984651948'
    assert correction['source_report']['sha256'] == SHA(PACKET / 'diagnosis-report.json')
    rows = report['requests'] + [report['rdap']]
    assert len(rows) == 5 and [r['request_number'] for r in rows] == list(range(1, 6))
    summaries = []
    for row in rows:
        path = ROOT / row['raw']['body']
        body = path.read_bytes() if path.exists() else b''
        assert len(body) == row['body_bytes'] <= 65536
        assert hashlib.sha256(body).hexdigest() == row['body_sha256']
        assert row['disk_free_before_bytes'] >= 11005853696
        assert row['elapsed_seconds'] <= 15
        headers = (ROOT / row['raw']['headers']).read_bytes()
        statuses = [int(m.group(1)) for m in re.finditer(rb'^HTTP/\S+\s+(\d{3})', headers, re.M)]
        assert (statuses[-1] if statuses else None) == row['source_status']
        if row['source_status'] == 200:
            data = json.loads(body)
            if row['kind'] == 'dns':
                assert data['Status'] == 0
                answers = sorted({r['data'] for r in data['Answer'] if r.get('type') == 1 and r['name'].rstrip('.') == 'web.archive.org'})
                assert answers == ['207.241.237.3']
                summaries.append({'provider': row['label'], 'answer_a': answers, 'comments': data.get('Comment', []), 'raw_body_sha256': row['body_sha256']})
            else:
                assert data['name'] == 'DROPBOX'
                assert data['startAddress'] == '108.160.160.0' and data['endAddress'] == '108.160.175.255'
        else:
            assert row['transport'] == 'direct' and row['curl_exit'] in (28, 35)
    actual_bytes = sum(row['body_bytes'] for row in rows)
    assert actual_bytes == correction['corrected_observation']['actual_total_body_bytes'] == 7797
    assert correction['corrected_observation']['actual_http_requests_total'] == 5
    assert correction['corrected_observation']['min_started_utc'] == min(row['started_utc'] for row in rows)
    assert correction['corrected_observation']['max_finished_utc'] == max(row['finished_utc'] for row in rows)
    tls_path = RUN / 'publication/root-dns-route-tls-diagnosis.json'
    tls = READ(tls_path)
    lookup, handshake = tls['observations']
    assert lookup['addresses'] == ['108.160.163.108']
    assert ipaddress.ip_address(lookup['addresses'][0]) in ipaddress.ip_network('108.160.160.0/20')
    assert handshake['tcp_connected'] and not handshake['tls_verified'] and handshake['failure_phase'] == 'tls'
    receipt = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
               'private_report_sha256': SHA(PACKET / 'diagnosis-report.json'), 'correction_sha256': SHA(PACKET / 'diagnosis-correction.json'),
               'actual_http_requests_total': 5, 'wayback_http_requests': 0, 'actual_total_body_bytes': actual_bytes,
               'actual_http_started_utc': min(row['started_utc'] for row in rows), 'actual_http_finished_utc': max(row['finished_utc'] for row in rows),
               'accounting_correction': 'Original total/body sum omitted RDAP and original start field was written after requests. Frozen observations retained; totals and HTTP span recomputed independently.',
               'public_recursive_dns_answers': summaries, 'trace_ip_allocation': {'network': '108.160.160.0/20', 'registry_name': 'DROPBOX', 'provider': 'ARIN RDAP'},
               'fresh_system_dns': lookup['addresses'], 'canonical_address_tcp_connected': True, 'canonical_address_tls_completed': False,
               'tls_diagnosis_sha256': SHA(tls_path), 'resume_gate_passed': False, 'settings_changed': False,
               'conclusion': 'System answers differ from two public recursive DNS observations and point to the Dropbox allocation. A fixed canonical-address TCP connection worked but verified TLS could not complete because it was reset. DNS cache flushing alone is insufficient; proxy HTTP429 remains a separate acquisition stop. No single network intervention point is asserted.'}
    OUT.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
