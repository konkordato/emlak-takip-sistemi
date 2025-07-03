# pdf_service.py
import pdfkit
import os
from datetime import datetime
from jinja2 import Template

class PDFService:
    def __init__(self):
        # Windows için wkhtmltopdf yolu
        self.config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
        
    def sozlesme_pdf_olustur(self, sozlesme_data):
        """Sözleşme PDF'i oluştur"""
        
        # PDF için HTML şablonu
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 20px;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #333;
                    padding-bottom: 20px;
                }
                .header h1 {
                    color: #2563eb;
                    margin: 0;
                }
                .section {
                    margin-bottom: 25px;
                    page-break-inside: avoid;
                }
                .section h2 {
                    color: #1e40af;
                    font-size: 18px;
                    margin-bottom: 10px;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 5px;
                }
                .info-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .info-table td {
                    padding: 8px;
                    border-bottom: 1px solid #eee;
                }
                .info-table td:first-child {
                    font-weight: bold;
                    width: 40%;
                    color: #555;
                }
                .footer {
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }
                .imza-alani {
                    margin-top: 50px;
                    display: table;
                    width: 100%;
                }
                .imza-kutu {
                    display: table-cell;
                    width: 45%;
                    text-align: center;
                    padding: 20px;
                }
                .imza-cizgi {
                    border-bottom: 1px solid #333;
                    margin: 50px 20px 10px 20px;
                }
                @page {
                    size: A4;
                    margin: 2cm;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>KİRA SÖZLEŞMESİ</h1>
                <p>Sözleşme No: #{{ sozlesme_no }}</p>
                <p>Düzenleme Tarihi: {{ bugun }}</p>
            </div>
            
            <div class="section">
                <h2>1. TARAFLAR</h2>
                
                <h3 style="color: #333; font-size: 16px;">KİRAYA VEREN (EV SAHİBİ)</h3>
                <table class="info-table">
                    <tr>
                        <td>Ad Soyad:</td>
                        <td>{{ sahip_adsoyad }}</td>
                    </tr>
                    <tr>
                        <td>TC Kimlik No:</td>
                        <td>{{ sahip_tc }}</td>
                    </tr>
                    <tr>
                        <td>Telefon:</td>
                        <td>{{ sahip_tel }}</td>
                    </tr>
                    <tr>
                        <td>E-posta:</td>
                        <td>{{ sahip_email or '-' }}</td>
                    </tr>
                    <tr>
                        <td>IBAN:</td>
                        <td>{{ sahip_iban or '-' }}</td>
                    </tr>
                </table>
                
                <h3 style="color: #333; font-size: 16px; margin-top: 20px;">KİRACI</h3>
                <table class="info-table">
                    <tr>
                        <td>Ad Soyad:</td>
                        <td>{{ kiraci_adsoyad }}</td>
                    </tr>
                    <tr>
                        <td>TC Kimlik No:</td>
                        <td>{{ kiraci_tc }}</td>
                    </tr>
                    <tr>
                        <td>Telefon 1:</td>
                        <td>{{ kiraci_tel1 }}</td>
                    </tr>
                    <tr>
                        <td>Telefon 2:</td>
                        <td>{{ kiraci_tel2 or '-' }}</td>
                    </tr>
                    <tr>
                        <td>E-posta:</td>
                        <td>{{ kiraci_email or '-' }}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>2. KİRALANAN GAYRİMENKUL</h2>
                <table class="info-table">
                    <tr>
                        <td>Gayrimenkul Tipi:</td>
                        <td>{{ gayrimenkul_tipi }}</td>
                    </tr>
                    <tr>
                        <td>İl:</td>
                        <td>{{ il }}</td>
                    </tr>
                    <tr>
                        <td>İlçe:</td>
                        <td>{{ ilce }}</td>
                    </tr>
                    <tr>
                        <td>Mahalle:</td>
                        <td>{{ mahalle }}</td>
                    </tr>
                    <tr>
                        <td>Adres:</td>
                        <td>{{ adres }}</td>
                    </tr>
                    <tr>
                        <td>Daire No:</td>
                        <td>{{ daire_no or '-' }}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>3. KİRA BEDELİ VE ÖDEME KOŞULLARI</h2>
                <table class="info-table">
                    <tr>
                        <td>Aylık Kira Bedeli:</td>
                        <td><strong>{{ kira_bedeli }} TL</strong></td>
                    </tr>
                    <tr>
                        <td>Depozito:</td>
                        <td>{{ depozito or '0' }} TL</td>
                    </tr>
                    <tr>
                        <td>Ödeme Günü:</td>
                        <td>Her ayın {{ odeme_gunu }}. günü</td>
                    </tr>
                    <tr>
                        <td>Kira Artış Oranı:</td>
                        <td>{{ kira_artis_orani or '-' }}%</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>4. SÖZLEŞME SÜRESİ</h2>
                <table class="info-table">
                    <tr>
                        <td>Başlangıç Tarihi:</td>
                        <td><strong>{{ baslangic_tarihi }}</strong></td>
                    </tr>
                    <tr>
                        <td>Bitiş Tarihi:</td>
                        <td><strong>{{ bitis_tarihi }}</strong></td>
                    </tr>
                    <tr>
                        <td>Süre:</td>
                        <td>{{ sure }} gün</td>
                    </tr>
                </table>
            </div>
            
            {% if notlar %}
            <div class="section">
                <h2>5. ÖZEL ŞARTLAR VE NOTLAR</h2>
                <p>{{ notlar }}</p>
            </div>
            {% endif %}
            
            <div class="section">
                <h2>6. DANIŞMAN BİLGİLERİ</h2>
                <table class="info-table">
                    <tr>
                        <td>Portföy Danışmanı:</td>
                        <td>{{ portfolyo_danisman or '-' }}</td>
                    </tr>
                    <tr>
                        <td>Kiraya Veren Danışman:</td>
                        <td>{{ kiraya_veren_danisman }}</td>
                    </tr>
                    {% if komisyon_tutari %}
                    <tr>
                        <td>Komisyon Tutarı:</td>
                        <td>{{ komisyon_tutari }} TL</td>
                    </tr>
                    {% endif %}
                </table>
            </div>
            
            <div class="imza-alani">
                <div class="imza-kutu">
                    <div class="imza-cizgi"></div>
                    <p><strong>KİRAYA VEREN</strong><br>{{ sahip_adsoyad }}</p>
                </div>
                <div class="imza-kutu">
                    <div class="imza-cizgi"></div>
                    <p><strong>KİRACI</strong><br>{{ kiraci_adsoyad }}</p>
                </div>
            </div>
            
            <div class="footer">
                <p>Bu sözleşme {{ bugun }} tarihinde düzenlenmiştir.</p>
                <p>Emlak Takip Sistemi tarafından oluşturulmuştur.</p>
            </div>
        </body>
        </html>
        """
        
        # Template'i oluştur
        template = Template(html_template)
        
        # Tarih hesaplamaları
        baslangic = datetime.strptime(str(sozlesme_data['baslangic_tarihi']), '%Y-%m-%d')
        bitis = datetime.strptime(str(sozlesme_data['bitis_tarihi']), '%Y-%m-%d')
        sure = (bitis - baslangic).days
        
        # HTML'i oluştur
        html = template.render(
            **sozlesme_data,
            bugun=datetime.now().strftime('%d.%m.%Y'),
            baslangic_tarihi=baslangic.strftime('%d.%m.%Y'),
            bitis_tarihi=bitis.strftime('%d.%m.%Y'),
            sure=sure
        )
        
        # PDF ayarları
        options = {
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
            'no-outline': None
        }
        
        # PDF dosya adı
        dosya_adi = f"sozlesme_{sozlesme_data['sozlesme_no']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        try:
            # PDF oluştur
            pdfkit.from_string(html, dosya_adi, options=options, configuration=self.config)
            print(f"✓ PDF oluşturuldu: {dosya_adi}")
            return dosya_adi
        except Exception as e:
            print(f"✗ PDF hatası: {e}")
            return None