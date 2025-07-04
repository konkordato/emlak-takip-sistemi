from database import Database

db = Database()

# Tüm kullanıcıları listele
print("=== TÜM KULLANICILAR ===")
kullanicilar = db.fetch_all("SELECT * FROM kullanicilar")

for kullanici in kullanicilar:
    print(f"\nKullanıcı ID: {kullanici['id']}")
    print(f"Kullanıcı Adı: {kullanici['kullanici_adi']}")
    print(f"Ad Soyad: {kullanici['ad_soyad']}")
    print(f"Rol: {kullanici['rol']}")
    print(f"Şifre (ilk 20 karakter): {str(kullanici['sifre'])[:20]}...")
    print("-" * 40)