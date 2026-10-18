"""Retain the first source manifest and explicitly classify older captures as supplements."""
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[3]
PUB=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
old=PUB/'root-v33-source-receipts-manifest.json'
out=PUB/'root-v33-source-receipts-manifest-r2.json'
assert not out.exists()
assert sha(old)=='a7907560e4b57e348a5c865966b4eb8f048e9cb0b8ff76e9ff0c4bf27f786a93'
data=read(old); changes=[]; primary=supplement=0
for batch in data['batches']:
    counts={'primary':0,'supplement':0}
    for row in read(ROOT/batch['public_copy_acceptance']['path'])['accepted_images']:
        canonical=urlsplit(row['original']).hostname in {'www.worldofwarcraft.com','worldofwarcraft.com'}
        baseline='20080101000000'<=row['actual_capture_timestamp']<='20080512210044'
        role='primary' if canonical and baseline else 'supplement'
        counts[role]+=1
        if canonical and not baseline:
            assert row['actual_capture_timestamp']<'20080101000000'
            changes.append({k:row[k] for k in ['original','actual_capture_timestamp','sha256','length']})
    batch.update(expected_primary_count=counts['primary'],expected_supplement_count=counts['supplement'],
        role='mixed' if all(counts.values()) else ('primary' if counts['primary'] else 'supplement'))
    primary+=counts['primary'];supplement+=counts['supplement']
assert len(changes)==2 and sum(x['length'] for x in changes)==474339
assert (primary,supplement)==(109,11)
data.update(new_primary_images=primary,new_supplement_images=supplement,checked_utc=datetime.now(timezone.utc).isoformat(),
    supersedes={'path':old.relative_to(ROOT).as_posix(),'sha256':sha(old)},
    source_origin_counts={'canonical_host':111,'related_host':9},
    overlay_role_policy='Primary overlay requires canonical host AND an exact capture from 2008 through the anchor. Older captured images use the existing explicit dated-supplement loader; all original bytes and capture dates are unchanged.',
    dated_primary_origin_supplements=changes)
out.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'accepted':True,'new_images':data['new_images'],'primary':primary,'supplement':supplement,'sha256':sha(out),'changes':changes}))
