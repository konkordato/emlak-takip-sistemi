from database import Database

# Veritabanı bağlantısı
db = Database()

# Tablo oluşturma sorgusu
create_table_query = """
CREATE TABLE IF NOT EXISTS sozlesme_yillari (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sozlesme_id INT,
    yil_no INT,
    baslangic_tarihi DATE,
    bitis_tarihi DATE,
    aylik_kira DECIMAL(10,2),
    kira_artis_orani DECIMAL(5,2),
    odenme_durumu VARCHAR(20) DEFAULT 'beklemede',
    notlar TEXT,
    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sozlesme_id) REFERENCES sozlesmeler(id)
)
"""

# Tabloyu oluştur
if db.execute_query(create_table_query):
    print("✓ sozlesme_yillari tablosu başarıyla oluşturuldu!")
else:
    print("✗ Tablo oluşturulurken hata oluştu!")

# Tablonun oluşup oluşmadığını kontrol et
tables = db.fetch_all("SHOW TABLES")
print("\nMevcut tablolar:")
for table in tables:
    print(f"- {list(table.values())[0]}")