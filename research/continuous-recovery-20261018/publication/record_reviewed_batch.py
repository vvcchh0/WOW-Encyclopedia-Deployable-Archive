"""Record the root's completed visual review and advance mutable recovery counters once."""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
PUB = RUN / 'publication'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', required=True)
    parser.add_argument('--net-id', required=True)
    parser.add_argument('--visual-reviewed', action='store_true')
    parser.add_argument('--note', required=True)
    args = parser.parse_args()
    assert re.fullmatch(r'[a-z0-9-]+', args.name) and re.fullmatch(r'NET\d+', args.net_id)
    source = PUB / f'root-{args.name}-source-acceptance.json'
    gate = read(PUB / f'root-{args.name}-plan-acceptance.json')
    receipt = read(source)
    status_path = RUN / 'status.json'
    status = read(status_path)
    visual = PUB / f'root-{args.name}-visual-acceptance.json'
    assert not visual.exists() and receipt['accepted'] and gate['accepted']
    assert receipt['plan_sha256'] == gate['plan_sha256']
    assert sha(RUN / status['latest_source_acceptance']) == gate['latest_source_acceptance_sha256']
    images = receipt['accepted_images']
    if images:
        assert args.visual_reviewed
        copies = read(PUB / f'root-{args.name}-public-copy-acceptance.json')
        assert copies['accepted'] and len(copies['accepted_images']) == len(images)
        assert {(x['original'], x['sha256'], x['length']) for x in copies['accepted_images']} == {(x['original'], x['sha256'], x['length']) for x in images}
    entries = [b for b in status['network_batches'] if b['id'] == args.net_id]
    assert len(entries) <= 1 and not any(b.get('status') == 'source_accepted' for b in entries)
    before = status['accepted_images']
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'images': len(images),
              'source_acceptance_sha256': sha(source), 'prior_total_images': before,
              'new_total_images': before + len(images), 'scope': args.note}
    if images:
        result['contact_sheet_sha256'] = sha(PUB / f'{args.name}-contact.png')
    status['accepted_images'] += len(images)
    status['accepted_image_bytes'] += sum(x['length'] for x in images)
    status['unpublished_accepted_images'] = status['accepted_images'] - status['published_images_this_run']
    relative = source.relative_to(RUN).as_posix()
    status.update(latest_source_acceptance=relative, latest_network_acceptance=relative, latest_failure_tail=receipt['failure_streak_end'])
    if images:
        status['last_image_source_acceptance'] = relative
    if receipt['stop_reason'] != 'completed_candidate_queue' or receipt['failure_streak_end']:
        status['network_resume_gate_passed'] = False
    entry = entries[0] if entries else {'id': args.net_id}
    if not entries:
        status['network_batches'].append(entry)
    entry.update(plan=Path(gate['plan']).relative_to(RUN.relative_to(ROOT)).as_posix(), status='source_accepted',
                 requests=receipt['requests'], accepted_images=len(images), root_source_acceptance=relative)
    visual.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    temporary = status_path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
    temporary.replace(status_path)
    print(json.dumps({'accepted': True, 'images': len(images), 'total_images': status['accepted_images'],
                      'source_sha256': sha(source), 'network_resume_gate_passed': status['network_resume_gate_passed']}))


if __name__ == '__main__':
    main()
