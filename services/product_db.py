import sqlite3 
import pandas as pd 
import os 
from datetime import datetime

DB_PATH = "products.db"

def veritabani_olustur():
    if not os.path.exists(DB_PATH):
        print("📁 Veritabanı oluşturuluyor...")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    barcode TEXT PRIMARY KEY,
                    product_name TEXT,
                    url TEXT,
                    last_control TEXT
                )
            """)
            print("✅ Veritabanı ve tablo hazır.")
    except sqlite3.Error as e:
        print(f"❌ Veritabanı hatası: {e}")


def urun_ekle(barcode, name, url, date=None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (barcode, product_name, url, last_control)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(barcode) DO UPDATE SET
                    product_name = excluded.product_name,
                    url = excluded.url,
                    last_control = excluded.last_control
            """, (barcode, name, url, date))
            return True
    except Exception as e:
        print(f"Hata: {e}")
        return False

def tum_urunleri_getir():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"❌ Ürünleri getirme hatası: {e}")
        return []
    

def urun_sil(barcode):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE barcode = ?", (barcode,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"❌ Ürün silme hatası: {e}")
        return False
    

def urun_guncelle(barcode, product_name=None, url=None, last_control=None):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            sorgu = "UPDATE products SET "
            alanlar = []
            degerler = []

            if product_name:
                alanlar.append("product_name = ?")
                degerler.append(product_name)
            if url:
                alanlar.append("url = ?")
                degerler.append(url)
            if last_control:
                alanlar.append("last_control = ?")
                degerler.append(last_control)

            if not alanlar:
                print("⚠️ Güncellenecek veri yok.")
                return False

            sorgu += ", ".join(alanlar) + " WHERE barcode = ?"
            degerler.append(barcode)

            cursor.execute(sorgu, tuple(degerler))
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"❌ Ürün güncelleme hatası: {e}")
        return False


def urun_ekle_veya_guncelle(barcode, name, url, kontrol_tarihi=None):
    return urun_ekle(barcode, name, url, kontrol_tarihi)

def urunleri_ara(query, sayfa_no, sayfa_boyutu):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            offset = (sayfa_no - 1) * sayfa_boyutu
            search_query = f"%{query}%"
            cursor.execute("""
                SELECT barcode, product_name, url, last_control 
                FROM products 
                WHERE barcode LIKE ? OR product_name LIKE ? OR url LIKE ?
                LIMIT ? OFFSET ?
            """, (search_query, search_query, search_query, sayfa_boyutu, offset))
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"❌ Arama hatası: {e}")
        return []


def urunleri_getir_sayfali(sayfa_no, sayfa_boyutu, arama_query=None):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            offset = (sayfa_no - 1) * sayfa_boyutu
            if arama_query:
                query = """
                    SELECT * FROM products 
                    WHERE barcode LIKE ? 
                    LIMIT ? OFFSET ?
                """
                cursor.execute(query, (f"%{arama_query}%", sayfa_boyutu, offset))
            else:
                query = "SELECT * FROM products LIMIT ? OFFSET ?"
                cursor.execute(query, (sayfa_boyutu, offset))
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"❌ Ürünleri getirme hatası: {e}")
        return []
    
def urun_sayisini_getir(arama_query=None):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            if arama_query:
                cursor.execute("SELECT COUNT(*) FROM products WHERE barcode LIKE ?", (f"%{arama_query}%",))
            else:
                cursor.execute("SELECT COUNT(*) FROM products")
            return cursor.fetchone()[0]
    except sqlite3.Error as e:
        print(f"❌ Kayıt sayısı getirme hatası: {e}")
        return 0