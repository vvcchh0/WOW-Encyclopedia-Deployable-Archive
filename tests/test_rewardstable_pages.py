"""Exporter integration of the exact reward-table script repair."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tests'))
import export_github_pages as pages
import rewardstable_compat as compat

class RewardstablePagesTests(unittest.TestCase):
    def _fixture(self, root, *, drift=False):
        from test_github_pages_export import GithubPagesExportTests
        base, site, manifest_path=GithubPagesExportTests()._fixture(root)
        manifest=json.loads(manifest_path.read_bytes())
        raw=(ROOT/'tests/fixtures/rewardstable_source16/rewardstable-new.js').read_bytes()
        if drift:raw+=b'\n// drift\n'
        rel=compat.REWARDSTABLE_ROUTE.lstrip('/')
        path=site/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        manifest['files'].append({'route':compat.REWARDSTABLE_ROUTE,'output_path':'offline/site/'+rel,'derived_sha256':hashlib.sha256(raw).hexdigest(),'derived_length':len(raw),'kind':'js','mime':'application/javascript'})
        manifest_path.write_text(json.dumps(manifest),encoding='utf-8')
        return base,site,manifest_path,raw

    def test_export_preserves_everything_except_two_image_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,site,manifest,raw=self._fixture(Path(tmp))
            result=pages.export_pages(source_site=site,manifest_path=manifest,output=root/'out',workspace_root=root,min_free_bytes=0)
            text=raw.decode('utf-8-sig')
            for side in ('alliance','horde'):
                text=text.replace(f'url(images/button-{side}.jpg)',f'url({pages.DEFAULT_BASE_PATH}info/basics/factions/rewardstable/images/button-{side}.jpg)')
            self.assertEqual((root/'out'/compat.REWARDSTABLE_ROUTE.lstrip('/')).read_bytes(),text.encode('utf-8'))
            self.assertEqual(result['stats']['rewardstable_compat_scripts'],1)

    def test_export_rejects_unreviewed_reward_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,site,manifest,raw=self._fixture(Path(tmp),drift=True)
            with self.assertRaisesRegex(pages.PagesExportError,'rewardstable source SHA mismatch'):
                pages.export_pages(source_site=site,manifest_path=manifest,output=root/'out',workspace_root=root,min_free_bytes=0)
            self.assertFalse((root/'out').exists())

if __name__=='__main__':unittest.main()
