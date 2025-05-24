
import time
import os
import psutil
from datetime import datetime

# Dummy logger to file and terminal
def log_and_print(msg, file=None, level="info"):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_msg = f"{timestamp} {msg}"
    print(full_msg)
    if file:
        file.write(full_msg + "\n")

def simulate_automation_run(product_list, log_file):
    total = len(product_list)
    process = psutil.Process(os.getpid())

    with open(log_file, "a", encoding="utf-8") as f:
        log_and_print("🚀 Automation started", file=f)
        start_time = time.time()

        for idx, (barcode, url) in enumerate(product_list, start=1):
            current_mem = process.memory_info().rss / (1024 * 1024)
            current_cpu = process.cpu_percent(interval=0.1)

            log_and_print(f"🔍 [{idx}/{total}] Checking {barcode}: {url}", file=f)
            log_and_print(f"🧠 RAM: {current_mem:.2f} MB | CPU: {current_cpu:.1f}%", file=f)

            # simulate processing delay
            time.sleep(0.05)

            log_and_print(f"✅ [{idx}/{total}] Done with {barcode}", file=f)

        end_time = time.time()
        duration = end_time - start_time
        log_and_print(f"🏁 Automation finished in {duration:.2f} seconds.", file=f)
