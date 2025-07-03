import pymysql

try:
    connection = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='emlak_takip',
        charset='utf8mb4'
    )
    print("✓ PyMySQL ile bağlantı başarılı!")
    connection.close()
except Exception as e:
    print(f"✗ Hata: {e}")