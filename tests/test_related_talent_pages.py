"""Portable checks at the exporter/related-icon boundary."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
if str(ROOT / 'tests') not in sys.path:
    sys.path.insert(0, str(ROOT / 'tests'))
import export_github_pages as pages


class RelatedTalentPagesTests(unittest.TestCase):
    route = '/shared/global/talents/druid/images/balance/fixture.jpg'

    def fixture(self, root):
        # Reuse the portable baseline fixture without importing its TestCase
        # into this module's discovered test namespace.
        from test_github_pages_export import GithubPagesExportTests
        base, site, manifest = GithubPagesExportTests()._fixture(root)
        records = json.loads(manifest.read_bytes())
        marker = '/__offline/missing-image.svg?requested=' + quote('http://www.worldofwarcraft.com' + self.route, safe='')
        data = ('<html><head></head><body><h1>Druid talents</h1><img src="' + marker + '"></body></html>').encode()
        target = site / 'info/classes/druid/talents.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        records['files'].append({
            'route':'/info/classes/druid/talents.html', 'output_path':'offline/site/info/classes/druid/talents.html',
            'derived_sha256':hashlib.sha256(data).hexdigest(), 'derived_length':len(data), 'kind':'html',
            'mime':'text/html; charset=UTF-8', 'source_base_url':'http://www.worldofwarcraft.com/info/classes/druid/talents.html',
        })
        records['origin_index']['www.worldofwarcraft.com/info/classes/druid/talents.html'] = '/info/classes/druid/talents.html'
        manifest.write_text(json.dumps(records), encoding='utf-8')
        return base, site, manifest

    def bundle(self, *, collision=False):
        route = '/style.css' if collision else self.route
        data = b'fixture bytes already validated by the separate bundle loader'
        asset = SimpleNamespace(route=route, relative=route[1:], data=data, mime='image/jpeg',
                                metadata={'sha256':hashlib.sha256(data).hexdigest(),'git_blob_sha1':'a'*40})
        catalog = b'{"classification":"later_related_source"}\n'
        return SimpleNamespace(assets=(asset,), catalog_relative='__offline/related-talent-icons.json',
            catalog_bytes=catalog, estimated_bytes=len(data)+len(catalog),
            source_metadata={'classification':'later_related_source','original_capture_timestamp':None,
                             'repository_url':'https://example.invalid/pinned-source','retrieved_utc':'2026-10-21T00:00:00+00:00'},
            per_class_counts={'druid':1}, notice_html='<p>2008 talent data; later related icons.</p>', map_sha256='b'*64)

    def test_registered_icon_heals_frozen_placeholder_preserves_bytes_and_labels_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self.fixture(Path(tmp))
            bundle = self.bundle()
            with mock.patch.object(pages.related_talent_icons, 'load_related_talent_bundle', return_value=bundle):
                result = pages.export_pages(source_site=site,manifest_path=manifest,output=root/'out',workspace_root=root,
                                            min_free_bytes=0,related_talent_icon_map=Path('accepted-map.json'))
            output = root/'out'
            self.assertEqual((output/bundle.assets[0].relative).read_bytes(),bundle.assets[0].data)
            html = (output/'info/classes/druid/talents.html').read_text(encoding='utf-8')
            self.assertIn('src="'+pages.DEFAULT_BASE_PATH+self.route[1:]+'"',html)
            self.assertEqual(html.count('id="__offline-related-talent-icons"'),1)
            self.assertNotIn('__offline-related-talent-icons',(output/'article.xml.html').read_text(encoding='utf-8'))
            prov = json.loads((output/'export-provenance.json').read_bytes())
            row = next(r for r in prov['files'] if r['kind']=='related_talent_icon')
            self.assertFalse(row['transformed'])
            self.assertEqual(row['source_refs'][0]['classification'],'later_related_source')
            self.assertIsNone(row['source_refs'][0]['original_capture_timestamp'])
            self.assertNotIn('payload_path',json.dumps(row))
            self.assertEqual(result['stats']['related_talent_icons'],1)
            self.assertEqual(result['stats']['related_talent_icon_notice_pages'],1)

    def test_existing_resource_collision_fails_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self.fixture(Path(tmp))
            with mock.patch.object(pages.related_talent_icons,'load_related_talent_bundle',return_value=self.bundle(collision=True)):
                with self.assertRaisesRegex(pages.PagesExportError,'collides'):
                    pages.export_pages(source_site=site,manifest_path=manifest,output=root/'out',workspace_root=root,
                                       min_free_bytes=0,related_talent_icon_map=Path('accepted-map.json'))
            self.assertFalse((root/'out').exists())
            self.assertFalse((root/'out.partial').exists())

    def test_default_does_not_load_supplement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, site, manifest = self.fixture(Path(tmp))
            with mock.patch.object(pages.related_talent_icons,'load_related_talent_bundle',side_effect=AssertionError('unexpected icon loader')) as loader:
                result=pages.export_pages(source_site=site,manifest_path=manifest,output=root/'out',workspace_root=root,min_free_bytes=0)
            loader.assert_not_called()
            self.assertNotIn('related_talent_icons',result['stats'])

    def test_notice_uses_real_body_and_is_limited_to_nine_routes(self):
        text='<html><head><script>var fake="<body>";</script></head><body><h1>Talents</h1></body></html>'
        changed, used=pages.annotate_related_talent_icons(text,route='/info/classes/druid/talents.html',notice_html='<p>source</p>')
        self.assertTrue(used)
        self.assertIn('var fake="<body>";',changed)
        self.assertGreater(changed.index('id="__offline-related-talent-icons"'),changed.index('</head>'))
        unchanged,used=pages.annotate_related_talent_icons(text,route='/info/classes/deathknight/talents.html',notice_html='<p>source</p>')
        self.assertFalse(used)
        self.assertEqual(unchanged,text)


if __name__=='__main__':
    unittest.main()
