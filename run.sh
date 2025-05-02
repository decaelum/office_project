#!/bin/bash

echo "🚀 URL Kontrol Aracı Başlatılıyor..."

# Sanal ortam yoksa oluştur
if [ ! -d "venv" ]; then
    echo "🔧 Sanal ortam oluşturuluyor..."
    python3 -m venv venv
    echo "✅ Sanal ortam oluşturuldu."
fi

# Ortamı aktive et
source venv/bin/activate
echo "🟢 Sanal ortam aktif."

# requirements.txt varsa paketleri yükle
if [ -f "requirements.txt" ]; then
    echo "📦 Gerekli paketler yükleniyor..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt bulunamadı, pip install atlandı."
fi

# GUI uygulamasını çalıştır
echo "📁 GUI başlatılıyor..."
python gui.py