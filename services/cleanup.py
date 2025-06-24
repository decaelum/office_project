import threading
import psutil
from services.logger_service import log_and_print

def stop_all_threads_and_kill_chromedrivers():
    # 🔁 Çalışan thread'leri listele (bilgilendirme amaçlı)
    current_threads = threading.enumerate()
    for thread in current_threads:
        if thread.name != "MainThread":
            log_and_print(f"⚠️ Aktif thread: {thread.name} (Durdurulması için flag veya terminate() gerekebilir)", level="warning")

    # 🧹 Aktif chromedriver ve selenium chrome işlemlerini kapat
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info['name']
            if name and ("chromedriver" in name.lower() or "chrome" in name.lower()):
                log_and_print(f"🧨 Killing process: {name} (PID {proc.pid})", level="warning")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    log_and_print("✅ Tüm thread bilgileri listelendi ve chromedriver işlemleri sonlandırıldı.")