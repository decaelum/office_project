
import unittest
from services.automation_services import check_url_change

class TestAutomationService(unittest.TestCase):
    def test_check_url_change_no_change(self):
        old = "https://site.com/product/abc-def-p-12345"
        new = "https://site.com/product/abc-def-p-12345"
        prefix_changed, content_id_changed = check_url_change(old, new)
        self.assertFalse(prefix_changed)
        self.assertFalse(content_id_changed)

    def test_check_url_change_prefix_change(self):
        old = "https://site.com/product/abc-def-p-12345"
        new = "https://site.com/product/xyz-ghi-p-12345"
        prefix_changed, content_id_changed = check_url_change(old, new)
        self.assertTrue(prefix_changed)
        self.assertFalse(content_id_changed)

    def test_check_url_change_content_id_change(self):
        old = "https://site.com/product/abc-def-p-12345"
        new = "https://site.com/product/abc-def-p-67890"
        prefix_changed, content_id_changed = check_url_change(old, new)
        self.assertFalse(prefix_changed)
        self.assertTrue(content_id_changed)

if __name__ == "__main__":
    unittest.main()
