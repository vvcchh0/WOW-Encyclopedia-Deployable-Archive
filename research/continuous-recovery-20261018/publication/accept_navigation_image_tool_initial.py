"""Root acceptance of exact validated-overlay image-link recovery."""
import ast
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];PUB=Path(__file__).resolve().parent
OUT=PUB/'root-navigation-image-tool-acceptance.json';assert not OUT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
tool=ROOT/'tools/export_github_pages.py';test=ROOT/'tests/test_navigation_image_link_recovery.py'
assert sha(tool.read_bytes())=='2a6fa4256ad0853797ae10748ef7842896614d419bdb7ad208d9b258dc8e6488'
assert sha(test.read_bytes())=='3d9be8f7d4ecf749428a3e0708aec8e5979a1a374d6ad69cc17d61b88a3efa2f'
before=subprocess.check_output(['git','show','7b124b56484c7604dd06e74f06b8b7c4672c44e2:tools/export_github_pages.py'],cwd=ROOT)
assert sha(before)=='8c50b1574f24a0bd2b03492ae8fe0cb7d3c48a50a247ba70d9e1859d58672afb'
old={n.name:n for n in ast.parse(before.decode()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
new={n.name:n for n in ast.parse(tool.read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
assert set(old)==set(new)
changes=[k for k in old if ast.dump(old[k],include_attributes=False)!=ast.dump(new[k],include_attributes=False)]
assert set(changes)=={'PagesLocalizer','export_pages'},changes
previous_methods={n.name:n for n in old['PagesLocalizer'].body if isinstance(n,ast.FunctionDef)}
current_methods={n.name:n for n in new['PagesLocalizer'].body if isinstance(n,ast.FunctionDef)}
assert set(current_methods)-set(previous_methods)=={'_validated_navigation_image_target'}
for name in previous_methods:
    if name not in {'__init__','localize'}:
        assert ast.dump(previous_methods[name],include_attributes=False)==ast.dump(current_methods[name],include_attributes=False)
export=copy.deepcopy(new['export_pages']);removed=0
for node in ast.walk(export):
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='PagesLocalizer':
        prior=len(node.keywords);node.keywords=[k for k in node.keywords if k.arg!='validated_navigation_image_routes'];removed+=prior-len(node.keywords)
assert removed==1 and ast.dump(export,include_attributes=False)==ast.dump(old['export_pages'],include_attributes=False)
result=subprocess.run([sys.executable,'-B','-X','utf8','-m','unittest','-v','tests.test_navigation_image_link_recovery'],cwd=ROOT,capture_output=True,text=True)
log=PUB/'root-navigation-image-tool-tests.log';log.write_text(result.stdout+result.stderr,encoding='utf-8')
assert result.returncode==0 and 'Ran 11 tests' in result.stderr
sys.path.insert(0,str(ROOT/'tools'))
import export_github_pages as pages
import offline_mirror as mirror
source=ROOT/'.scratch/offline-navigation-20261015-v15/site/news/rss-08-2007.xml'
line=source.read_text(encoding='utf-8').splitlines()[4193]
assert '/__offline/missing.html?' in line and 'ss01.jpg' in line
image_url='http://www.worldofwarcraft.com/news/images/07-08/ss01.jpg';route='/news/images/07-08/ss01.jpg';prefix=pages.DEFAULT_BASE_PATH
localizer=pages.PagesLocalizer(route_to_static={'/__offline/missing.html':prefix+'__offline/missing.html',
    '/__offline/missing-image.svg':prefix+'__offline/missing-image.svg',route:prefix+route.lstrip('/')},
    aliases={},origin_index={mirror.origin_key(image_url):route},base_path=prefix,
    validated_navigation_image_routes={route})
recorder=mirror.ReferenceRecorder('/news/rss-08-2007.xml','http://www.worldofwarcraft.com/news/rss-08-2007.xml')
derived=mirror.rewrite_html('<html><body>'+line+'</body></html>',base_url=recorder.source_url if hasattr(recorder,'source_url') else 'http://www.worldofwarcraft.com/news/rss-08-2007.xml',
    localizer=localizer,recorder=recorder,source_sha=sha(source.read_bytes()),compat_assets=[])
assert 'href="'+prefix+route.lstrip('/')+'"' in derived
fixture=PUB/'navigation-image-link-source-fixture.json'
fixture.write_text(json.dumps({'scope':'Actual frozen source line with a synthetic accepted-route fixture; no new image payload or production export is claimed.',
    'source_sha256':sha(source.read_bytes()),'line':4194,'source_snippet':line,'derived_snippet':derived},indent=2)+'\n',encoding='utf-8')
receipt={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
    'baseline_exporter_sha256':sha(before),'exporter_sha256':sha(tool.read_bytes()),
    'test_sha256':sha(test.read_bytes()),'focused_tests':11,'test_exit_code':0,
    'test_log_sha256':sha(log.read_bytes()),'changed_top_level_definitions':changes,
    'new_class_method':'_validated_navigation_image_target','unchanged_export_except_overlay_allowlist':True,
    'actual_frozen_source_fixture':{'path':fixture.relative_to(ROOT).as_posix(),'sha256':sha(fixture.read_bytes())},
    'scope':'Only navigation missing.html markers with exact origin_index and a validated raster overlay route may heal. Existing aliases, image markers, unknown/business links and prefixed idempotence remain covered.',
    'network_requests':0,'export_executed':False}
OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'focused_tests':11,'sha256':sha(OUT.read_bytes())}))
