import unittest
import sys
import os
import matplotlib.pyplot as plt
import time

# 📂 Çalışma dizinini sabitle
PROJECT_ROOT = "/Users/yagizcigirgan/Desktop/office_project"
os.chdir(PROJECT_ROOT)
sys.path.append(PROJECT_ROOT)
print(f"📂 Çalışma dizini: {os.getcwd()}")

# Sonuçları tutacak global değişken
from tests.test_automation_load import test_summary_results

def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_modules = [
        "tests.test_database_service",
        "tests.test_mock_server",
        "tests.test_automation_load"
    ]

    for module in test_modules:
        suite.addTests(loader.loadTestsFromName(module))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

    if test_summary_results:
        print("📊 Test sonuçları bulundu, rapor hazırlanıyor...")
        plot_test_results(test_summary_results)
    else:
        print("⚠️ Test sonuçları bulunamadı. Otomasyon testleri çalıştı mı?")

def plot_test_results(results):
    if not os.path.exists("results"):
        os.makedirs("results")

    labels = ['Correct', 'Incorrect', 'Bans', 'Normal']
    values = [
        results.get("Correct", 0),
        results.get("Incorrect", 0),
        results.get("Bans", 0),
        results.get("Normal", 0)
    ]
    colors = ['green', 'red', 'orange', 'blue']

    plt.bar(labels, values, color=colors)
    plt.title('Automation Test Summary')
    plt.xlabel('Result Types')
    plt.ylabel('Counts')
    plt.grid(True, linestyle='--', alpha=0.7)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"results/final_test_summary_{timestamp}.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

    print(f"📊 Final report saved as: {filename}")

if __name__ == "__main__":
    run_all_tests()