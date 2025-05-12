#!/bin/bash

# Çalışma dizinine git
cd /Users/yagizcigirgan/Desktop/office_project

# Ortamı aktif et (eğer virtualenv kullanıyorsan)
source venv/bin/activate

echo "🚀 Testler başlatılıyor..."

# Gereksinimleri yükle (İstersen yoruma alabilirsin)
pip install -r requirements_tests.txt

# Testleri çalıştır
python3 tests/test_runner.py

echo "✅ Testler tamamlandı. Sonuçlar ve grafik rapor 'results/' klasörüne kaydedildi."

# Rapor dosyasını otomatik aç (MacOS için)
if [ -d "results" ]; then
    latest_report=$(ls -t results/final_test_summary_*.png | head -n1)
    if [ -f "$latest_report" ]; then
        open "$latest_report"
    else
        echo "⚠️ Rapor dosyası bulunamadı."
    fi
fi