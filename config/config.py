# config/config.py

# MySQL Veritabanı Ayarları
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # XAMPP varsayılan olarak boş
    'database': 'emlak_takip',
    'charset': 'utf8mb4'
}

# Flask Ayarları
SECRET_KEY = 'emlak-takip-gizli-anahtar-2024'

# SMS API Ayarları (Daha sonra dolduracağız)
SMS_API_KEY = ''
SMS_API_URL = ''

# Uygulama Ayarları
UYARI_GUN_SAYISI = 60  # Kaç gün önceden uyarı gönderilecek
# E-posta Ayarları
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': 'ahmetkaraman03@gmail.com',  # Gmail adresiniz
    'password': 'igfwiebbtujuinxz',  # 16 haneli uygulama şifresi (boşluksuz)
    'enabled': True
}