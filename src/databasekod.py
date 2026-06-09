import sqlite3
import os

import os

# Veritabanının kodla aynı klasörde oluşmasını zorunlu kılıyoruz:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "yesiliz.db")
def create_database():
    # Klasör yoksa oluşturur
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_soyad TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        tohum_puan INTEGER DEFAULT 0,
        fidan_sayisi INTEGER DEFAULT 0
    )
    """)

    # Atık Türleri Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS waste_types(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        atik_adi TEXT NOT NULL,
        puan_katsayisi INTEGER NOT NULL,
        karbon_katsayisi REAL NOT NULL
    )
    """)

    # Geri Dönüşümler Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recycling(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        atik_turu TEXT,
        miktar REAL,
        puan INTEGER,
        karbon_tasarrufu REAL,
        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Etkinlikler Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        baslik TEXT,
        yer TEXT,
        tarih TEXT
    )
    """)

    # Geri Dönüşüm Noktaları Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recycling_points(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isim TEXT,
        adres TEXT
    )
    """)

    # Adminler Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()

    # Varsayılan Atık Türleri Ekleme
    cursor.execute("SELECT COUNT(*) FROM waste_types")
    if cursor.fetchone()[0] == 0:
        waste_data = [
            ("Plastik", 10, 2.5),
            ("Kağıt", 5, 1.2),
            ("Cam", 7, 1.8),
            ("Metal", 12, 3.0),
            ("Elektronik", 20, 5.0)
        ]
        cursor.executemany("INSERT INTO waste_types (atik_adi, puan_katsayisi, karbon_katsayisi) VALUES(?,?,?)", waste_data)

    # Örnek Etkinlikler Ekleme
    cursor.execute("SELECT COUNT(*) FROM events")
    if cursor.fetchone()[0] == 0:
        events = [
            ("Kampüs Temizliği", "Balıkesir Üniversitesi", "2026-06-20"),
            ("Fidan Dikim Etkinliği", "Atatürk Parkı", "2026-07-01")
        ]
        cursor.executemany("INSERT INTO events (baslik, yer, tarih) VALUES(?,?,?)", events)

    # Örnek Geri Dönüşüm Noktaları Ekleme
    cursor.execute("SELECT COUNT(*) FROM recycling_points")
    if cursor.fetchone()[0] == 0:
        points = [
            ("Merkez Geri Dönüşüm Noktası", "Atatürk Caddesi"),
            ("Belediye Toplama Merkezi", "Altıeylül")
        ]
        cursor.executemany("INSERT INTO recycling_points (isim, adres) VALUES(?,?)", points)

    # Varsayılan Admin Ekleme
    cursor.execute("SELECT COUNT(*) FROM admins")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO admins(username, password) VALUES(?,?)", ("admin", "12345"))

    conn.commit()
    conn.close()
    print("Veritabanı başarıyla oluşturuldu.")


# ==========================================
#  ARAYÜZ İÇİN GEREKLİ SQL FONKSİYONLARI
# ==========================================

def user_register(ad_soyad, username, email, password):
    """Yeni kullanıcı kaydeder. Başarılı ise True, kullanıcı adı/mail varsa False döner."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (ad_soyad, username, email, password) VALUES (?, ?, ?, ?)", 
                       (ad_soyad, username, email, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def check_login(username, password, is_admin=False):
    """Giriş bilgilerini sorgular. Başarılı ise user_id döner, değilse None."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if is_admin:
        # Admin kontrolü: admins tablosundan sorgular
        cursor.execute("SELECT id FROM admins WHERE username = ? AND password = ?", (username, password))
    else:
        # Normal kullanıcı kontrolü: users tablosundan sorgular
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        
    res = cursor.fetchone()
    conn.close()
    
    if res:
        return res[0]  # Eşleşme varsa kullanıcının ID'sini döndür
    return None

def get_user_stats(user_id):
    """Kullanıcının anlık puan, fidan ve ad-soyad bilgilerini çeker."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ad_soyad, tohum_puan, fidan_sayisi FROM users WHERE id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    
    if res:
        return res[0], res[1], res[2]
    return "Bilinmeyen Kullanıcı", 0, 0

def add_recycling_activity(user_id, atik_adi, miktar):
    """Atık ekleme işlemi yapar, puan ve karbon hesaplayıp kullanıcının bakiyesini günceller."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Katsayıları çekelim
    cursor.execute("SELECT puan_katsayisi, karbon_katsayisi FROM waste_types WHERE atik_adi = ?", (atik_adi,))
    katsayi = cursor.fetchone()
    if not katsayi:
        return False
    
    puan_kat, karbon_kat = katsayi
    kazanilan_puan = int(miktar * puan_kat)
    karbon_tasarrufu = round(miktar * karbon_kat, 2)
    
    # 1. Geri dönüşüm kaydını ekle
    cursor.execute("""
    INSERT INTO recycling (user_id, atik_turu, miktar, puan, karbon_tasarrufu) 
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, atik_adi, miktar, kazanilan_puan, karbon_tasarrufu))
    
    # 2. Kullanıcının toplam puanını güncelle
    cursor.execute("SELECT tohum_puan, fidan_sayisi FROM users WHERE id = ?", (user_id,))
    current_puan, current_fidan = cursor.fetchone()
    
    yeni_puan = current_puan + kazanilan_puan
    
    # Oyunlaştırma mantığı: Her 100 puan = 1 Fidan
    yeni_fidan = yeni_puan // 100
    
    cursor.execute("UPDATE users SET tohum_puan = ?, fidan_sayisi = ? WHERE id = ?", (yeni_puan, yeni_fidan, user_id))
    
    conn.commit()
    conn.close()
    return kazanilan_puan, karbon_tasarrufu

def get_leaderboard():
    """Liderlik tablosu için en yüksek fidan ve puana sahip ilk 10 kullanıcıyı getirir."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, fidan_sayisi, tohum_puan FROM users ORDER BY fidan_sayisi DESC, tohum_puan DESC LIMIT 10")
    res = cursor.fetchall()
    conn.close()
    return res

def get_events():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT baslik, yer, tarih FROM events")
    res = cursor.fetchall()
    conn.close()
    return res

def get_recycling_points():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT isim, adres FROM recycling_points")
    res = cursor.fetchall()
    conn.close()
    return res

# Admin Paneli için Ekleme Fonksiyonları
def add_event_by_admin(baslik, yer, tarih):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (baslik, yer, tarih) VALUES (?, ?, ?)", (baslik, yer, tarih))
    conn.commit()
    conn.close()

def add_point_by_admin(isim, adres):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO recycling_points (isim, adres) VALUES (?, ?)", (isim, adres))
    conn.commit()
    conn.close()

    # --- ADMIN KULLANICI YÖNETİMİ ---
def get_all_users():
    """Sistemdeki tüm normal kullanıcıları listeler (Adminleri listelemez)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, ad_soyad, username, email, tohum_puan, fidan_sayisi FROM users")
    res = cursor.fetchall()
    conn.close()
    return res

def delete_user_by_admin(user_id):
    """Seçilen kullanıcıyı ve o kullanıcıya ait tüm geçmiş atık kayıtlarını siler."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Önce kullanıcının atık geçmişini silelim (Foreign key bütünlüğü için)
    cursor.execute("DELETE FROM recycling WHERE user_id = ?", (user_id,))
    # Sonra kullanıcının kendisini silelim
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()