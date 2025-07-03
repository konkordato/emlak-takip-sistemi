import mysql.connector

print("MySQL bağlantısı deneniyor...")

# Farklı bağlantı yöntemleri dene
tests = [
    {'host': '127.0.0.1', 'user': 'root', 'password': ''},
    {'host': 'localhost', 'user': 'root', 'password': ''},
    {'host': '127.0.0.1', 'port': 3306, 'user': 'root', 'password': ''},
]

for i, config in enumerate(tests):
    try:
        print(f"\nDeneme {i+1}: {config['host']}")
        connection = mysql.connector.connect(**config)
        print("✓ Bağlantı başarılı!")
        
        # Veritabanlarını listele
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        print("Veritabanları:")
        for db in cursor:
            print(f"  - {db[0]}")
        
        connection.close()
        break
    except Exception as e:
        print(f"✗ Hata: {e}")