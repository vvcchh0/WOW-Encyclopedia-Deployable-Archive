"""Independently reconcile the saved DNS/TCP/TLS observations, without network."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
NET = ROOT / 'research/continuous-recovery-20261021/network'
OUT = PUB / 'root-wayback-dns-tls-diagnosis.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
local_path = NET / 'wayback-tls-diagnostic01/runtime/public/diagnostic-summary.json'
doh_path = NET / 'wayback-dns-comparison01/public/dns-summary.json'
tls_path = NET / 'wayback-resolved-tls01/public/resolved-tls-summary.json'
doh_raw_path = NET / 'wayback-dns-comparison01/private/dns-comparison-report.json'
tls_raw_path = NET / 'wayback-resolved-tls01/private/resolved-tls-report.json'
local, doh, tls = map(read, (local_path, doh_path, tls_path))
doh_raw, tls_raw = map(read, (doh_raw_path, tls_raw_path))
assert local['selected_ipv4'] == doh['local_ipv4_from_prior_diagnostic'] == '202.160.128.14'
assert local['failure_stage'] == 'tcp' and not local['tcp_success'] and not local['application_bytes_sent']
assert len(doh['services']) == 2
for row in doh['services']:
    assert row['http_status'] == 200 and row['doh_status'] == 0 and row['AD'] is False
    assert {r['data'] for r in row['records'] if r['type'] == 1} == {'207.241.237.3'}
for report in (doh_raw, tls_raw):
    assert report['wayback_application_requests'] == 0
    for attempt in report['attempts']:
        body = ROOT / attempt['body_path']
        assert body.is_file() and body.stat().st_size == attempt['body_bytes']
        assert sha(body) == attempt['body_sha256']
        if attempt['http_status'] == 200:
            data = read(body)
            assert data['Status'] == 0
            assert {r['data'] for r in data['Answer'] if r['type'] == 1} == {'207.241.237.3'}
assert tls_raw['tls_verification'] is True and tls_raw['proxy_used_for_tls'] is False
assert all(tls['tls_probe'].get(k) == v for k, v in tls_raw['tls_probe'].items())
assert set(tls['tls_probe']) - set(tls_raw['tls_probe']) == {
    'certificate', 'certificate_hostname_match', 'cipher', 'protocol', 'tcp_error',
}
assert all(tls['tls_probe'][k] is None for k in set(tls['tls_probe']) - set(tls_raw['tls_probe']))
probe = tls['tls_probe']
assert probe['ip'] == '207.241.237.3' and probe['tcp_success'] and not probe['tls_success']
assert probe['tls_error']['errno'] == 10054 and not probe['application_bytes_sent']
assert tls['prior_doh_summary_sha256'] == sha(doh_path)
assert tls['prior_doh_report_sha256'] == sha(doh_raw_path)
receipt = {
    'accepted_observations': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
    'local_dns_ipv4': local['selected_ipv4'], 'local_dns_tcp_result': 'timeout_before_tls',
    'two_doh_services_agree_ipv4': '207.241.237.3', 'doh_dnssec_AD': False,
    'fresh_doh_observed_utc': tls['doh_observed_at_utc'],
    'resolved_ip_tcp_success': True, 'resolved_ip_tls_result': 'connection_reset_10054',
    'certificate_obtained': False, 'wayback_application_requests': 0,
    'summary_normalization': 'Five unobserved optional TLS fields are explicit nulls in the public summary and absent in the private probe record; all recorded values match.',
    'diagnosis': 'A resolver-answer difference was observed. The public-answer IP reaches TCP but the verified TLS handshake resets; changing DNS alone is not established as a working repair.',
    'unresolved': ['Cause of the local resolver difference', 'Which network endpoint caused the TLS reset'],
    'network_resume_gate_passed': False, 'latest_wayback_http_stop_remains': 429,
    'global_network_changes': False, 'further_identical_probes': 'stopped',
    'public_summaries': [p.relative_to(ROOT).as_posix() for p in (local_path, doh_path, tls_path)],
    'bindings': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)}
                 for p in (local_path, doh_path, tls_path, doh_raw_path, tls_raw_path)],
}
OUT.write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
print(json.dumps({'accepted_observations': True, 'resume_gate': False, 'receipt_sha256': sha(OUT)}))
