"""One system DNS lookup and one verified TLS handshake, without HTTP."""
import argparse
import hashlib
import json
import shutil
import socket
import ssl
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OUT = PUB / 'root-dns-route-tls-diagnosis.json'
DIAG = ROOT / 'research/continuous-recovery-20261020/network/dns-diagnosis01'
HOST = 'web.archive.org'
IP = '207.241.237.3'
FLOOR = 11005853696


def child(operation):
    start = time.monotonic()
    result = {'operation': operation, 'started_utc': datetime.now(timezone.utc).isoformat(), 'http_requests': 0}
    if operation == 'system-dns':
        result['addresses'] = sorted({row[4][0] for row in socket.getaddrinfo(HOST, 443, type=socket.SOCK_STREAM)})
    elif operation == 'tls-only':
        result.update(hostname=HOST, address=IP, tcp_connected=False, tls_verified=False)
        phase = 'tcp'
        try:
            with socket.create_connection((IP, 443), timeout=5) as raw:
                result['tcp_connected'] = True
                raw.settimeout(8)
                phase = 'tls'
                context = ssl.create_default_context()
                assert context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED
                with context.wrap_socket(raw, server_hostname=HOST) as tls:
                    result.update(tls_verified=True, tls_version=tls.version(), certificate_expires=tls.getpeercert().get('notAfter'))
        except (OSError, ssl.SSLError) as exc:
            result.update(failure_phase=phase, error_type=type(exc).__name__, error=str(exc)[:300])
    result.update(finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.monotonic()-start)
    print(json.dumps(result))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--child', choices=['system-dns', 'tls-only'])
    args = p.parse_args()
    if args.child:
        child(args.child)
        return
    assert not OUT.exists() and shutil.disk_usage(ROOT).free >= FLOOR
    # One fixed canonical address from the independently matching HTTPS DNS
    # responses. No alternate IP list, proxy, HTTP request, or system mutation.
    bindings = []
    for name in ['02-google-proxy.body', '04-cloudflare-proxy.body']:
        path = DIAG / 'raw' / name
        body = path.read_bytes()
        data = json.loads(body)
        assert data['Status'] == 0 and not data.get('TC')
        assert any(row.get('type') == 1 and row.get('data') == IP and row.get('name', '').rstrip('.') == HOST for row in data['Answer'])
        bindings.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(body).hexdigest()})
    observations = []
    for operation in ['system-dns', 'tls-only']:
        try:
            run = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(Path(__file__).resolve()), '--child', operation], cwd=ROOT, capture_output=True, timeout=20)
            assert run.returncode == 0, run.stderr.decode('utf-8', 'replace')[:300]
            observations.append(json.loads(run.stdout))
        except subprocess.TimeoutExpired:
            observations.append({'operation': operation, 'timed_out': True, 'hard_timeout_seconds': 20, 'http_requests': 0})
    assert shutil.disk_usage(ROOT).free >= FLOOR
    receipt = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'dns_response_bindings': bindings,
               'observations': observations, 'wayback_http_requests': 0, 'tls_connections_maximum': 1,
               'http_rate_limit_bypassed': False, 'settings_changed': False,
               'disk_free_bytes': shutil.disk_usage(ROOT).free,
               'scope': 'Read-only system DNS refresh plus one certificate-verified TLS-only connection to a fixed canonical DNS answer. No HTTP/CDX/image request, proxy rotation, alternate IP iteration, hosts edit or global resolver change.'}
    OUT.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
