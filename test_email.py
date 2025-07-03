# test_email.py
from email_service import EmailService

# E-posta servisini test et
email_service = EmailService()

# Test e-postası gönder
test_email = input("Test e-postası göndermek için e-posta adresinizi girin: ")

test_result = email_service.send_email(
    to_email=test_email,
    subject="Emlak Takip Sistemi - Test E-postası",
    body="""
    <html>
    <body>
        <h2>Test E-postası</h2>
        <p>Bu bir test e-postasıdır. E-posta sisteminiz başarıyla çalışıyor! ✅</p>
        <p>Emlak Takip Sistemi</p>
    </body>
    </html>
    """
)

if test_result:
    print("✅ Test e-postası başarıyla gönderildi! E-postanızı kontrol edin.")
else:
    print("❌ E-posta gönderilemedi. Config ayarlarınızı kontrol edin.")