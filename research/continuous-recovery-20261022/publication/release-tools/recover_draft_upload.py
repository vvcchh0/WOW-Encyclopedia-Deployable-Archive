"""Use the authenticated release list so owned drafts are visible on readback.

GitHub's tag endpoint returns published releases; the list endpoint includes
drafts for users with push access. All other reviewed create/upload guards and
process pacing are inherited unchanged. This adapter never publishes.
"""
from datetime import datetime,timezone
import argparse,hashlib,json
from pathlib import Path
import create_upload_release as base

EXPECTED_BASE='e8acc5a27eeb4a4b5b387c074859943adce235f5ea08ca55b4b715c749dee408'

class DraftVisibleCreator(base.ReleaseCreator):
    def _remote_release(self):
        # --jq wraps the list so the reviewed object-only JSON parser still
        # receives an object; filtering and ownership checks remain local.
        data=self._gh_read(['api',f'repos/{self.inputs.repo}/releases?per_page=100','--jq','{releases: .}'])
        rows=data.get('releases')
        if not isinstance(rows,list):raise base.ReleaseToolError('release list is not an array')
        matches=[r for r in rows if isinstance(r,dict) and r.get('tag_name')==self.inputs.tag]
        if len(matches)>1:raise base.ReleaseToolError('multiple release records use the exact tag')
        if not matches:return None
        row=matches[0]
        if row.get('target_commitish')!=self.inputs.source_head:
            raise base.ReleaseToolError('draft target differs from the accepted source head')
        return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--execute',action='store_true',required=True);a=p.parse_args()
    actual=hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest()
    if actual!=EXPECTED_BASE:raise base.ReleaseToolError('reviewed base helper changed')
    inputs=base.load_inputs(a.config)
    result=DraftVisibleCreator(inputs).create_upload()
    proof={'schema':'wow-draft-visible-upload-adapter/v1','accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
      'base_sha256':actual,'adapter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'release_id':result['release_id'],'tag':result['tag'],'target_commit':result['target_commit'],
      'upload_receipt_sha256':hashlib.sha256((inputs.output_dir/base.RECEIPT_NAME).read_bytes()).hexdigest(),
      'documentation':'https://docs.github.com/en/rest/releases/releases#list-releases','published':False}
    base._write_json_new(inputs.output_dir/'draft-visible-adapter-receipt.json',proof)
    print(json.dumps({'accepted':True,'release_id':result['release_id'],'assets':sorted(result['remote_assets']),'published':False}))
if __name__=='__main__':main()
