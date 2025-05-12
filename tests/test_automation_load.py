test_summary_results = {}

import unittest
import os
import random
import time
import matplotlib.pyplot as plt
import requests
from services.automation_services import check_url_change


class TestAutomationLoad(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.total_urls = 1000
        cls.urls = cls().generate_test_urls(cls.total_urls, change_ratio=0.2, ban_ratio=0.1, error_ratio=0.1)
        print("🔍 Starting URL Change Detection Test...")
        correct, incorrect = cls().test_url_changes(cls.urls)
        print(f"✅ Correct: {correct} | ❌ Incorrect: {incorrect}")

        print("\n🛡️ Starting Ban Detection Test...")
        bans, normal = cls().ban_detection(cls.urls)
        print(f"🚨 Ban Detected: {bans} | 🟢 Normal Responses: {normal}")

        image_file = cls().plot_results(correct, incorrect, bans, normal)

        global test_summary_results
        test_summary_results.update({
            "Correct": correct,
            "Incorrect": incorrect,
            "Bans": bans,
            "Normal": normal,
            "ReportFile": image_file
        })

    def generate_test_urls(self, n=1000, change_ratio=0.2, ban_ratio=0.1, error_ratio=0.1):
        base_url = "https://trendyol.com/product-x-p-"
        urls = []
        for i in range(1, n + 1):
            content_id = f"{10000 + i}"
            if random.random() < change_ratio:
                new_content_id = f"{20000 + i}"
            else:
                new_content_id = content_id
            old_url = f"{base_url}{content_id}"
            new_url = f"{base_url}{new_content_id}"

            # Simulate status for testing purposes
            rand = random.random()
            if rand < ban_ratio:
                simulated_status = "ban"
            elif rand < ban_ratio + error_ratio:
                simulated_status = "error"
            else:
                simulated_status = "normal"

            urls.append((old_url, new_url, simulated_status))
        return urls

    @staticmethod
    def test_url_changes(urls):
        correct, incorrect = 0, 0
        total = len(urls)
        for idx, (old_url, current_url, _) in enumerate(urls, start=1):
            prefix_changed, content_id_changed = check_url_change(old_url, current_url)
            if (old_url != current_url and content_id_changed) or (old_url == current_url and not content_id_changed):
                correct += 1
            else:
                incorrect += 1
            if idx % 100 == 0 or idx == total:
                print(f"🔧 Processed {idx}/{total} URLs...")
        return correct, incorrect

    @staticmethod
    def ban_detection(urls):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2_1)...",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        ban_detected, normal_response = 0, 0
        total = len(urls)

        for idx, (old_url, _, simulated_status) in enumerate(urls, start=1):
            print(f"🔍 Checking URL {idx}/{total}: {old_url} | Simulated Status: {simulated_status}")
            try:
                if simulated_status == "ban":
                    ban_detected += 1
                    print(f"🚨 Simulated Ban! Status Code: 429 | URL: {old_url}")
                elif simulated_status == "error":
                    raise requests.RequestException("Simulated Connection Error")
                else:
                    normal_response += 1
                    print(f"🟢 Normal Response | URL: {old_url}")
            except Exception as e:
                print(f"❌ Simulated Error for URL: {old_url} | Error: {e}")
            time.sleep(0.2)  # Daha hızlı test için azaltıldı

        print(f"\n📊 Ban Detection Complete: Bans: {ban_detected}, Normal: {normal_response}")
        return ban_detected, normal_response

    @staticmethod
    def plot_results(correct, incorrect, bans, normal):
        if not os.path.exists("results"):
            os.makedirs("results")

        labels = ['Correct', 'Incorrect', 'Bans', 'Normal']
        values = [correct, incorrect, bans, normal]
        colors = ['green', 'red', 'orange', 'blue']

        plt.bar(labels, values, color=colors)
        plt.title('Automation Test Results')
        plt.xlabel('Result Types')
        plt.ylabel('Counts')
        plt.grid(True, linestyle='--', alpha=0.7)

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"results/test_summary_{timestamp}.png"
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        print(f"📊 Report saved as: {filename}")
        return filename


if __name__ == "__main__":
    unittest.main()