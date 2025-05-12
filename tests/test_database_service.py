
import unittest
from services.database_services import get_all_products

class TestDatabaseService(unittest.TestCase):
    def test_get_all_products_returns_list(self):
        result = get_all_products()
        self.assertIsInstance(result, list)

    def test_get_all_products_structure(self):
        result = get_all_products()
        if result:
            self.assertEqual(len(result[0]), 4)

if __name__ == "__main__":
    unittest.main()
