"""Advance mutable tracker timestamps and task entries without resetting gates."""
import json
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(__file__).resolve().parent.parent
status_path, tasks_path = RUN / 'status.json', RUN / 'tasks.json'
status = json.loads(status_path.read_bytes())
tasks = json.loads(tasks_path.read_bytes())
now = datetime.now(timezone.utc).isoformat()
entries = {x['id']: x for x in tasks['tasks']}
for batch in status['network_batches']:
    if not batch['id'].startswith('NET'):
        continue
    task = entries.get(batch['id'])
    if task is None:
        task = {'id': batch['id'], 'owner': 'network_recovery', 'scope': 'Serial bounded source acquisition'}
        tasks['tasks'].append(task)
        entries[batch['id']] = task
    task.update(status=batch['status'], network_executed=bool(batch.get('requests')), accepted_images=batch.get('accepted_images', 0))
    if batch.get('root_source_acceptance'):
        task['root_receipt'] = batch['root_source_acceptance']
    if batch.get('plan'):
        task['plan'] = batch['plan']
status['latest_network_batch'] = max((b['id'] for b in status['network_batches'] if b['id'].startswith('NET')), key=lambda v: int(v[3:]))
status['updated_utc'] = tasks['updated_utc'] = now
for p, obj in [(status_path, status), (tasks_path, tasks)]:
    temporary = p.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(obj, indent=2)+'\n', encoding='utf-8', newline='\n')
    temporary.replace(p)
print(json.dumps({'latest_network_batch': status['latest_network_batch'], 'tasks': len(tasks['tasks']), 'network_resume_gate_passed': status['network_resume_gate_passed'], 'latest_failure_tail': status['latest_failure_tail']}))
