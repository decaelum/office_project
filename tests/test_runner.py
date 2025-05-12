import unittest
import sys
import os

# Proje kök dizinini PYTHONPATH'e ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_modules = [
        "tests.test_database_service",
        "tests.test_automation_service"
    ]

    for module in test_modules:
        suite.addTests(loader.loadTestsFromName(module))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    run_all_tests()