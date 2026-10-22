import unittest
from types import SimpleNamespace
import recover_draft_upload as tool
class DraftVisibleTests(unittest.TestCase):
    def reader(self,rows):
        obj=tool.DraftVisibleCreator(SimpleNamespace(repo='owner/repo',tag='v55',source_head='a'*40))
        obj._gh_read=lambda args:{'releases':rows}
        return obj
    def test_visible_owned_draft_and_missing_tag(self):
        draft={'tag_name':'v55','target_commitish':'a'*40,'draft':True,'id':1}
        self.assertEqual(self.reader([draft])._remote_release(),draft)
        self.assertIsNone(self.reader([])._remote_release())
    def test_duplicate_or_wrong_target_stops(self):
        draft={'tag_name':'v55','target_commitish':'a'*40}
        with self.assertRaises(tool.base.ReleaseToolError):self.reader([draft,draft])._remote_release()
        with self.assertRaises(tool.base.ReleaseToolError):self.reader([{**draft,'target_commitish':'b'*40}])._remote_release()
