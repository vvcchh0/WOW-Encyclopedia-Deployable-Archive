import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import approve_recovery_maps as adapter


class MapAdapterTests(unittest.TestCase):
    def test_directory_capture_base_survives_slashless_replay_alias(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'source.json'
            source.write_text(json.dumps({'files': [{
                'logical_url': 'http://www.worldofwarcraft.com/info/faq',
                'capture_original': 'http://www.worldofwarcraft.com/info/faq/',
                'source_base_url': 'http://www.worldofwarcraft.com/info/faq/',
                'actual_url': 'https://web.archive.org/web/20080512205518id_/http://www.worldofwarcraft.com/info/faq',
                'actual_timestamp': '20080512205518', 'local_path': 'entity.bin',
                'zip_file': 'objects.zip', 'mime': 'text/html', 'kind': 'html',
            }]}), encoding='utf-8')
            destination = root / 'approved.json'
            with patch.object(adapter, 'ROOT', root):
                adapter.approve(source, destination)
            item = json.loads(destination.read_text(encoding='utf-8'))['files'][0]
            self.assertTrue(item['source_base_url'].endswith('/faq/'))
            self.assertEqual(item['derived_route'], '/info/faq/index.html')
            self.assertEqual(item['route_aliases'], ['/info/faq', '/info/faq/'])


if __name__ == '__main__': unittest.main()
