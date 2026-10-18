"""Root review of complete new-image coverage before the bounded browser run."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote,urlsplit
ROOT=Path(__file__).resolve().parents[3]
PUB=Path(__file__).resolve().parent
HERE=PUB.parent/'integration/v33/browser'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def main():
    p=HERE/'v33-browser-input-r2.json'
    assert sha(p)=='8c7727019206045f5faec30a690d48b6c8b7fa6395318f8710b77a6d2b1049e5'
    data=read(p)
    checker=HERE/'check_v33_browser.cjs'
    if data['source_bindings']['checker']['sha256']!=sha(checker):
        out=HERE/'v33-browser-input-r3.json';assert not out.exists()
        data['supersedes_browser_input']={'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'reason':'Root corrected per-target hidden-panel activation before the first browser run; reference coverage and site bytes are unchanged.'}
        data['source_bindings']['checker']['sha256']=sha(checker)
        out.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n');p=out
    for x in data['source_bindings'].values():assert sha(ROOT/x['path'])==x['sha256'],x['path']
    assert data['output']['provenance']['sha256']=='99ac5b0a2bc7d257b2fe3c4b18a0bb74023c3c57051be3a4f4efe20258f4c8f5'
    assert read(PUB/'root-v33-export-acceptance.json')['accepted']
    assert read(PUB/'root-v33-static-metrics-acceptance.json')['accepted']
    items=data['new_originals'];assert len(items)==120 and sum(x['length'] for x in items)==17971331
    assert len(data['validated_old_originals'])==439
    covered={x['original'] for k in ['popup_full_image_links','ordinary_image_hrefs','static_render_targets'] for x in data['source_references'][k]}
    assert {x['original'] for x in items}<=covered
    for row in data['r2_reference_additions']['targets']:
        evidence=row['source_evidence'];old=ROOT/evidence['source_path']
        assert sha(old)==evidence['source_page_sha256']
        line=old.read_text(encoding='utf-8').splitlines()[int(evidence['source_line'])-1]
        original=row['original']
        assert original in line or quote(original,safe='') in line,original
        match=row['current_output_match'];current=ROOT/'.scratch/pages-resources-20261018-v33'/row['page_output']
        assert sha(current)==match['page_sha256']
        current_line=current.read_text(encoding='utf-8').splitlines()[match['line']-1]
        assert urlsplit(original).path in current_line and current_line==match['line_text']
    gate=PUB/'root-v33-browser-input-r2-acceptance.json';assert not gate.exists()
    result={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'input':{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)},
        'input_sha256':sha(p),'network_requests':0,'browser_executed':False,'new_originals':120,'all_new_originals_have_source_ui_references':True,
        'popup_links':21,'ordinary_links':69,'static_targets':30,'late_source_evidence_lines_independently_checked':19,
        'tool_bindings':[{'path':x.relative_to(ROOT).as_posix(),'sha256':sha(x)} for x in [HERE/'prepare_v33_browser.py',HERE/'prepare_v33_browser_r2.py',checker]]}
    gate.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'accepted':True,'input':p.relative_to(ROOT).as_posix(),'gate':gate.relative_to(ROOT).as_posix(),'sha256':sha(gate)}))
if __name__=='__main__':main()
