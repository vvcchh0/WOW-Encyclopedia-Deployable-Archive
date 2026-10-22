"""Record the root-reviewed, single-use control03 authorization; no network."""
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / 'research/continuous-recovery-20261022/network/wayback-positive-control03/wayback_positive_control03.py'
spec = importlib.util.spec_from_file_location('control03', RUNNER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
go_path = module.GO_PATH
if go_path.exists() or module.RUNTIME.exists():
    raise SystemExit('single-use authorization/runtime already exists')
free = shutil.disk_usage(ROOT).free
if free < module.DISK_FLOOR:
    raise SystemExit('disk floor')
now = datetime.now(timezone.utc)
go = dict(module.go_hashes())
go.update({
    'schema': 'wow-root-wayback-positive-control03-go/v1',
    'accepted': True, 'root_go': True, 'network_authorized': True,
    'historical_failure_tail_retained': True, 'no_image_replay': True,
    'direct_first': True, 'tls_verification': True, 'no_automatic_retries': True,
    'no_redirects': True, 'no_pagination': True,
    'maximum_logical_requests': 1, 'maximum_http_attempts': 2,
    'parent_watchdog_seconds': 180, 'maximum_seconds_child': 90,
    'maximum_body_bytes': 1048576, 'cdx_record_length': '10259',
    'mime': 'image/jpeg', 'digest': 'TJ2TFHNGVSA64RRRP3UD2CQZCP4TTRND',
    'inherited_transport_failure_streak': 0, 'free_bytes_before': free,
    'authorized_at_utc': now.isoformat(), 'not_before_utc': now.isoformat(),
    'expires_utc': (now + timedelta(minutes=30)).isoformat(),
    'root_review': {
        'offline_fixtures_passed': 25,
        'request_seconds_target': 35,
        'child_seconds_target': 90,
        'external_hard_cap_seconds': 180,
        'header_slow_trickle_boundary_accepted': True,
        'reason': 'A parent subprocess watchdog is the hard bound even if header reads trickle past the child target. No other request is allowed after timeout.',
        'latest_429_gate_remains_closed_until_fresh_control_positive': True,
        'transport_streak_reason': 'The most recent historical attempt is an HTTP 429 response, not a transport failure; the failed control and cooldown remain bound separately.',
    },
})
go_path.write_bytes((json.dumps(go, ensure_ascii=False, indent=2) + '\n').encode())
module.validate_go(go_path)
status_path = ROOT / 'research/continuous-recovery-20261022/status.json'
status = json.loads(status_path.read_text(encoding='utf-8'))
status.update({'in_flight_network_batch': 'wayback-positive-control03', 'updated_utc': now.isoformat(), 'disk_free_latest_bytes': free})
status_path.write_bytes((json.dumps(status, ensure_ascii=False, indent=2) + '\n').encode())
print(json.dumps({'go': go_path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(go_path.read_bytes()).hexdigest(), 'free_bytes': free, 'validated': True}))
