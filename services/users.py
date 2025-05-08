import sqlite3
import os
import hashlib

DB_PATH = "users.db"

# ---------------------------------------------------------------------------- #
#                          Ortak Hash ve DB Bağlantısı                         #
# ---------------------------------------------------------------------------- #

def hashle(parola):
    return hashlib.sha256(parola.encode()).hexdigest()

def veritabani_baglantisi():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn, conn.cursor()
    except sqlite3.Error as e:
        print(f"❌ Veritabanı bağlantı hatası: {e}")
        return None, None

# ---------------------------------------------------------------------------- #
#                          Veritabanı Kurulum Fonksiyonu                       #
# ---------------------------------------------------------------------------- #

def db_olustur():
    if not os.path.exists(DB_PATH):
        conn, cursor = veritabani_baglantisi()
        if not conn:
            return
        try:
            cursor.execute("""
                CREATE TABLE users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    is_admin INTEGER DEFAULT 0,
                    role TEXT DEFAULT 'user'
                )
            """)
            cursor.execute("INSERT INTO users (username, password, is_admin, role) VALUES (?, ?, ?, ?)",
                           ("admin", hashle("admin123"), 1, "admin"))
            conn.commit()
            print("✅ Kullanıcı veritabanı ve admin hesabı oluşturuldu.")
        except Exception as e:
            print(f"❌ Veritabanı oluşturulamadı: {e}")
        finally:
            conn.close()

# ---------------------------------------------------------------------------- #
#                             Kullanıcı İşlemleri                              #
# ---------------------------------------------------------------------------- #

def kullanici_var_mi(username):
    conn, cursor = veritabani_baglantisi()
    if not conn:
        return False
    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"❌ Kullanıcı kontrol hatası: {e}")
        return False
    finally:
        conn.close()

def dogrula(username, password):
    conn, cursor = veritabani_baglantisi()
    if not conn:
        return False
    try:
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                       (username, hashle(password)))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"❌ Doğrulama hatası: {e}")
        return False
    finally:
        conn.close()

def kullanici_ekle(username, password, is_admin=False):
    if kullanici_var_mi(username):
        return False
    conn, cursor = veritabani_baglantisi()
    if not conn:
        return False
    try:
        cursor.execute("INSERT INTO users (username, password, is_admin, role) VALUES (?, ?, ?, ?)",
                       (username, hashle(password), int(is_admin), "admin" if is_admin else "user"))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Kullanıcı ekleme hatası: {e}")
        return False
    finally:
        conn.close()

def kullanici_sil(username):
    if username == "admin":
        return False
    conn, cursor = veritabani_baglantisi()
    if not conn:
        return False
    try:
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ Kullanıcı silme hatası: {e}")
        return False
    finally:
        conn.close()

def sifre_guncelle(username, yeni_sifre):
    conn, cursor = veritabani_baglantisi()
    if not conn:
        return False
    try:
        cursor.execute("UPDATE users SET password = ? WHERE username = ?",
                       (hashle(yeni_sifre), username))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Şifre güncelleme hatası: {e}")
        return False
    finally:
        conn.close()

# ---------------------------------------------------------------------------- #
#                        Yetki & Kullanıcı Listeleme                           #
# ---------------------------------------------------------------------------- #

def is_admin_kullanici(username):
    conn, cursor = veritabani_baglantisi()
    if not conn:
        return False
    try:
        cursor.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        return result is not None and result[0] == 1
    except Exception as e:
        print(f"❌ Yetki kontrol hatası: {e}")
        return False
    finally:
        conn.close()

def tum_kullanicilari_getir():
    conn, cursor = veritabani_baglantisi()
    if not conn:
        return []
    try:
        cursor.execute("SELECT username FROM users")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"❌ Kullanıcı listeleme hatası: {e}")
        return []
    finally:
        conn.close()

def get_all_users():
    conn, cursor = veritabani_baglantisi()
    if not conn:
        return []
    try:
        cursor.execute("SELECT username, password, role FROM users")
        return cursor.fetchall()
    except Exception as e:
        print(f"❌ Kullanıcıları çekme hatası: {e}")
        return []
    finally:
        conn.close()

def ensure_role_column_exists():
    conn, cursor = veritabani_baglantisi()
    if not conn:
        return
    try:
        cursor.execute("PRAGMA table_info(users)")
        kolonlar = [satir[1] for satir in cursor.fetchall()]
        if "role" not in kolonlar:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            print("✅ 'role' sütunu eklendi.")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Role kontrol hatası: {e}")
    finally:
        conn.close()