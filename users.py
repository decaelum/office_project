import sqlite3
import os  
import hashlib 

DB_PATH = "users.db"

def hashle(parola):
    return hashlib.sha256(parola.encode()).hexdigest()

def db_olustur():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)

        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       ("admin", hashle("admin123")))
        conn.commit()
        conn.close()
        print("✅ Kullanıcı veritabanı ve admin hesabı oluşturuldu.")

def kullanici_var_mi(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def dogrula(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, hashle(password))  # ✅ HASHLENMİŞ ŞİFREYİ KULLANIYOR
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def kullanici_ekle(username, password, is_admin=False):
    if kullanici_var_mi(username):
        return False
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
        (username, hashle(password), int(is_admin))
    )
    conn.commit()
    conn.close()
    return True

def is_admin_kullanici(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None and result[0] == 1