import sqlite3

# Veritabanına bağlan
conn = sqlite3.connect('emlak.db')
cursor = conn.cursor()

# Sözleşme yılları tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS sozlesme_yillari (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sozlesme_id INTEGER,
    yil_no INTEGER,
    baslangic_tarihi DATE,
    bitis_tarihi DATE,
    aylik_kira REAL,
    kira_artis_orani REAL,
    odenme_durumu TEXT DEFAULT 'beklemede',
    notlar TEXT,
    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sozlesme_id) REFERENCES sozlesmeler(id)
)
''')

conn.commit()
conn.close()

print("Veritabanı başarıyla güncellendi!")