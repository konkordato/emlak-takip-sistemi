from database import Database

db = Database()

# Admin kullanıcısını kontrol et
admin = db.fetch_one("SELECT * FROM kullanicilar WHERE kullanici_adi = 'admin'")
if admin:
    print(f"Admin kullanıcısı:")
    print(f"- Kullanıcı adı: {admin['kullanici_adi']}")
    print(f"- Ad Soyad: {admin['ad_soyad']}")
    print(f"- Rol: {admin['rol']}")
else:
    print("Admin kullanıcısı bulunamadı!")

# Tüm kullanıcıları listele
print("\nTüm kullanıcılar:")
users = db.fetch_all("SELECT kullanici_adi, ad_soyad, rol FROM kullanicilar")
for user in users:
    print(f"- {user['kullanici_adi']} ({user['ad_soyad']}) - Rol: {user['rol']}")