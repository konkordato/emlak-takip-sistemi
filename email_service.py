# email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import EMAIL_CONFIG
from datetime import datetime

class EmailService:
    def __init__(self):
        self.smtp_server = EMAIL_CONFIG['smtp_server']
        self.smtp_port = EMAIL_CONFIG['smtp_port']
        self.email = EMAIL_CONFIG['email']
        self.password = EMAIL_CONFIG['password']
        self.enabled = EMAIL_CONFIG['enabled']
        
    def send_email(self, to_email, subject, body, is_html=True):
        """E-posta gönder"""
        if not self.enabled:
            print("E-posta servisi devre dışı")
            return False
            
        try:
            # E-posta oluştur
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # HTML veya düz metin
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # SMTP bağlantısı
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
                
            print(f"✓ E-posta gönderildi: {to_email}")
            return True
            
        except Exception as e:
            print(f"✗ E-posta hatası: {e}")
            return False
    
    def sozlesme_bildirimi(self, sozlesme_data):
        """Yeni sözleşme bildirim e-postası"""
        
        # Kiracı için e-posta içeriği
        kiraci_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Kira Sözleşmeniz Oluşturuldu</h2>
                
                <p>Sayın {sozlesme_data['kiraci_adsoyad']},</p>
                
                <p>Kira sözleşmeniz başarıyla oluşturulmuştur. Detaylar aşağıdadır:</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2563eb; margin-top: 0;">Sözleşme Detayları</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0;"><strong>Adres:</strong></td>
                            <td style="padding: 8px 0;">{sozlesme_data['adres']}, {sozlesme_data['ilce']}/{sozlesme_data['il']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Kira Bedeli:</strong></td>
                            <td style="padding: 8px 0;">{sozlesme_data['kira_bedeli']} TL</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Başlangıç Tarihi:</strong></td>
                            <td style="padding: 8px 0;">{sozlesme_data['baslangic_tarihi']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Bitiş Tarihi:</strong></td>
                            <td style="padding: 8px 0;">{sozlesme_data['bitis_tarihi']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Ödeme Günü:</strong></td>
                            <td style="padding: 8px 0;">Her ayın {sozlesme_data['odeme_gunu']}. günü</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="color: #1976d2; margin-top: 0;">Ev Sahibi Bilgileri</h4>
                    <p style="margin: 5px 0;"><strong>Ad Soyad:</strong> {sozlesme_data['sahip_adsoyad']}</p>
                    <p style="margin: 5px 0;"><strong>Telefon:</strong> {sozlesme_data['sahip_tel']}</p>
                    <p style="margin: 5px 0;"><strong>IBAN:</strong> {sozlesme_data['sahip_iban'] or 'Belirtilmemiş'}</p>
                </div>
                
                <p style="margin-top: 30px;">Herhangi bir sorunuz olursa bizimle iletişime geçebilirsiniz.</p>
                
                <p>Saygılarımızla,<br>
                <strong>{sozlesme_data['kiraya_veren_danisman']}</strong><br>
                Emlak Danışmanı</p>
            </div>
        </body>
        </html>
        """
        
        # Ev sahibi için e-posta içeriği
        sahip_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Gayrimenkulünüz Kiralandı</h2>
                
                <p>Sayın {sozlesme_data['sahip_adsoyad']},</p>
                
                <p>Gayrimenkulünüz başarıyla kiralanmıştır. Detaylar aşağıdadır:</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2563eb; margin-top: 0;">Kiralama Detayları</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0;"><strong>Kiracı:</strong></td>
                            <td style="padding: 8px 0;">{sozlesme_data['kiraci_adsoyad']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Kiracı Telefon:</strong></td>
                            <td style="padding: 8px 0;">{sozlesme_data['kiraci_tel1']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Kira Bedeli:</strong></td>
                            <td style="padding: 8px 0;">{sozlesme_data['kira_bedeli']} TL</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Depozito:</strong></td>
                            <td style="padding: 8px 0;">{sozlesme_data['depozito'] or '0'} TL</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;"><strong>Başlangıç:</strong></td>
                            <td style="padding: 8px 0;">{sozlesme_data['baslangic_tarihi']}</td>
                        </tr>
                    </table>
                </div>
                
                <p style="color: #666; font-style: italic;">
                    Kira ödemeleri her ayın {sozlesme_data['odeme_gunu']}. günü hesabınıza yatırılacaktır.
                </p>
                
                <p style="margin-top: 30px;">Saygılarımızla,<br>
                <strong>{sozlesme_data['kiraya_veren_danisman']}</strong><br>
                Emlak Danışmanı</p>
            </div>
        </body>
        </html>
        """
        
        # E-postaları gönder
        kiraci_sonuc = False
        sahip_sonuc = False
        
        if sozlesme_data.get('kiraci_email'):
            kiraci_sonuc = self.send_email(
                sozlesme_data['kiraci_email'],
                "Kira Sözleşmeniz Oluşturuldu",
                kiraci_html
            )
        
        if sozlesme_data.get('sahip_email'):
            sahip_sonuc = self.send_email(
                sozlesme_data['sahip_email'],
                "Gayrimenkulünüz Kiralandı",
                sahip_html
            )
        
        return kiraci_sonuc or sahip_sonuc
    
    def bitis_uyari_email(self, sozlesme_data, kalan_gun):
        """Sözleşme bitiş uyarı e-postası"""
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 8px;">
                    <h2 style="color: #856404; margin-top: 0;">⚠️ Kira Sözleşmeniz Sona Eriyor</h2>
                    
                    <p>Sayın {sozlesme_data['kiraci_adsoyad']},</p>
                    
                    <p><strong>Kira sözleşmenizin bitimine {kalan_gun} gün kaldı.</strong></p>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <p style="margin: 5px 0;"><strong>Adres:</strong> {sozlesme_data['adres']}</p>
                        <p style="margin: 5px 0;"><strong>Bitiş Tarihi:</strong> {sozlesme_data['bitis_tarihi']}</p>
                        <p style="margin: 5px 0;"><strong>Mevcut Kira:</strong> {sozlesme_data['kira_bedeli']} TL</p>
                    </div>
                    
                    <p>Sözleşmenizi yenilemek veya tahliye işlemleri için lütfen en kısa sürede bizimle iletişime geçin.</p>
                    
                    <p style="margin-top: 20px;">
                        <strong>İletişim:</strong><br>
                        Danışman: {sozlesme_data['kiraya_veren_danisman']}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        if sozlesme_data.get('kiraci_email'):
            return self.send_email(
                sozlesme_data['kiraci_email'],
                f"Kira Sözleşme Uyarısı - {kalan_gun} Gün Kaldı",
                html_content
            )
        return False