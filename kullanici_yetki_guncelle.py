from database import Database

db = Database()

# 1. Kullanıcılar tablosuna rol sütunu ekle
alter_query = """
ALTER TABLE kullanicilar 
ADD COLUMN IF NOT EXISTS rol VARCHAR(20) DEFAULT 'kullanici'
"""

try:
    db.execute_query(alter_query)
    print("✓ Rol sütunu eklendi!")
except:
    print("! Rol sütunu zaten mevcut veya hata oluştu")

# 2. Mevcut admin kullanıcısını süper admin yap
update_query = """
UPDATE kullanicilar 
SET rol = 'super_admin' 
WHERE kullanici_adi = 'admin'
"""

db.execute_query(update_query)
print("✓ Admin kullanıcısı süper admin yapıldı!")

# 3. Kullanıcıları kontrol et
users = db.fetch_all("SELECT id, kullanici_adi, ad_soyad, rol FROM kullanicilar")
print("\nMevcut kullanıcılar:")
for user in users:
    print(f"- {user['kullanici_adi']} ({user['ad_soyad']}) - Rol: {user['rol']}")