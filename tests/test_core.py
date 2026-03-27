import tempfile
from pathlib import Path
import unittest

from src.opencleaner.core import ScanItem, clean_items, human_readable_size


class CoreTests(unittest.TestCase):
    def test_human_readable_size(self) -> None:
        self.assertEqual(human_readable_size(0), "0 B")
        self.assertEqual(human_readable_size(1024), "1.0 KB")
        self.assertEqual(human_readable_size(1048576), "1.0 MB")

    def test_clean_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "a.log").write_text("hello")
            sub = tmp_path / "cache"
            sub.mkdir()
            (sub / "b.tmp").write_text("world")

            item = ScanItem(label="test", paths=[tmp_path], bytes_size=0)
            deleted, reclaimed = clean_items([item])

            self.assertGreaterEqual(deleted, 2)
            self.assertGreater(reclaimed, 0)
            self.assertFalse((tmp_path / "a.log").exists())
            self.assertFalse(sub.exists())


if __name__ == "__main__":
    unittest.main()
