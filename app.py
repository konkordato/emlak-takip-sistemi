# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import Database
from config.config import SECRET_KEY
from datetime import datetime
import os
from email_service import EmailService
from pdf_service import PDFService
from flask import send_file

app = Flask(__name__)
app.secret_key = SECRET_KEY

db = Database()

# Giriş kontrolü
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Ana sayfa
@app.route('/')
@login_required
def index():
    # Yaklaşan sözleşmeleri al
    yaklasan_sozlesmeler = db.get_yaklasan_sozlesmeler()
    
    # İstatistikleri al
    aktif_sozlesme_sayisi = db.fetch_one("SELECT COUNT(*) as sayi FROM sozlesmeler WHERE durum = 'aktif'")
    pasif_sozlesme_sayisi = db.fetch_one("SELECT COUNT(*) as sayi FROM sozlesmeler WHERE durum = 'pasif'")
    
    return render_template('dashboard.html', 
                         yaklasan_sozlesmeler=yaklasan_sozlesmeler,
                         aktif_sayi=aktif_sozlesme_sayisi['sayi'] if aktif_sozlesme_sayisi else 0,
                         pasif_sayi=pasif_sozlesme_sayisi['sayi'] if pasif_sozlesme_sayisi else 0)

# Giriş sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        kullanici_adi = request.form.get('kullanici_adi')
        sifre = request.form.get('sifre')
        
        print(f"Giriş denemesi - Kullanıcı: {kullanici_adi}, Şifre: {sifre}")  # Debug için
        
        user = db.fetch_one("SELECT * FROM kullanicilar WHERE kullanici_adi = %s AND sifre = %s", 
                           (kullanici_adi, sifre))
        
        print(f"Veritabanı sonucu: {user}")  # Debug için
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['ad_soyad']
            print(f"Giriş başarılı! Yönlendiriliyor...")  # Debug için
            return redirect(url_for('index'))
        else:
            flash('Kullanıcı adı veya şifre hatalı!', 'error')
            print(f"Giriş başarısız!")  # Debug için
    
    return render_template('login.html')

# Çıkış
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Sözleşme ekleme
@app.route('/sozlesme/ekle', methods=['GET', 'POST'])
@login_required
def sozlesme_ekle():
    if request.method == 'POST':
        # Form verilerini al
        data = request.form.to_dict()
        
        # Yeni sözleşme numarası al
        sozlesme_no = db.get_next_sozlesme_no()
        
        # Veritabanına kaydet
        query = """
            INSERT INTO sozlesmeler (
                sozlesme_no, kiraci_adsoyad, kiraci_tc, kiraci_tel1, kiraci_tel2, 
                kiraci_email, sahip_adsoyad, sahip_tc, sahip_tel, sahip_email, 
                sahip_iban, sahip_banka, il, ilce, mahalle, adres, daire_no, 
                gayrimenkul_tipi, portfolyo_danisman, kiraya_veren_danisman, 
                baslangic_tarihi, bitis_tarihi, kira_bedeli, depozito, odeme_gunu,
                kira_artis_orani, komisyon_tutari, komisyon_notu, notlar
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        params = (
            sozlesme_no,
            data.get('kiraci_adsoyad'), data.get('kiraci_tc'), 
            data.get('kiraci_tel1'), data.get('kiraci_tel2'), data.get('kiraci_email'),
            data.get('sahip_adsoyad'), data.get('sahip_tc'), data.get('sahip_tel'), 
            data.get('sahip_email'), data.get('sahip_iban'), data.get('sahip_banka'),
            data.get('il'), data.get('ilce'), data.get('mahalle'), data.get('adres'), 
            data.get('daire_no'), data.get('gayrimenkul_tipi'),
            data.get('portfolyo_danisman'), data.get('kiraya_veren_danisman'),
            data.get('baslangic_tarihi'), data.get('bitis_tarihi'), 
            data.get('kira_bedeli'), data.get('depozito'), data.get('odeme_gunu'),
            data.get('kira_artis_orani'), data.get('komisyon_tutari'), 
            data.get('komisyon_notu'), data.get('notlar')
        )
        
        if db.execute_query(query, params):
            flash(f'Sözleşme başarıyla eklendi! Sözleşme No: {sozlesme_no}', 'success')
            
            # E-posta gönder
            try:
                email_service = EmailService()
                email_data = {
                    'kiraci_adsoyad': data.get('kiraci_adsoyad'),
                    'kiraci_email': data.get('kiraci_email'),
                    'kiraci_tel1': data.get('kiraci_tel1'),
                    'sahip_adsoyad': data.get('sahip_adsoyad'),
                    'sahip_email': data.get('sahip_email'),
                    'sahip_tel': data.get('sahip_tel'),
                    'sahip_iban': data.get('sahip_iban'),
                    'adres': data.get('adres'),
                    'il': data.get('il'),
                    'ilce': data.get('ilce'),
                    'kira_bedeli': data.get('kira_bedeli'),
                    'depozito': data.get('depozito'),
                    'baslangic_tarihi': data.get('baslangic_tarihi'),
                    'bitis_tarihi': data.get('bitis_tarihi'),
                    'odeme_gunu': data.get('odeme_gunu'),
                    'kiraya_veren_danisman': data.get('kiraya_veren_danisman')
                }
                
                if email_service.sozlesme_bildirimi(email_data):
                    flash('Bilgilendirme e-postaları gönderildi!', 'success')
            except Exception as e:
                print(f"E-posta gönderim hatası: {e}")
                flash('E-posta gönderilemedi ama sözleşme kaydedildi.', 'warning')
            
            return redirect(url_for('sozlesme_listesi'))
        else:
            flash('Sözleşme eklenirken hata oluştu!', 'error')
    
    return render_template('sozlesme_ekle.html')
# Aktif sözleşmeler listesi
@app.route('/sozlesme/aktif')
@login_required
def sozlesme_listesi():
    sozlesmeler = db.fetch_all("SELECT * FROM sozlesmeler WHERE durum = 'aktif' ORDER BY sozlesme_no DESC")
    return render_template('sozlesme_liste.html', sozlesmeler=sozlesmeler, baslik='Aktif Sözleşmeler')

# Pasif sözleşmeler listesi
@app.route('/sozlesme/pasif')
@login_required
def pasif_sozlesmeler():
    sozlesmeler = db.fetch_all("SELECT * FROM sozlesmeler WHERE durum = 'pasif' ORDER BY sozlesme_no DESC")
    return render_template('sozlesme_liste.html', sozlesmeler=sozlesmeler, baslik='Pasif Sözleşmeler')

# Sözleşme detay
@app.route('/sozlesme/<int:id>')
@login_required
def sozlesme_detay(id):
    sozlesme = db.fetch_one("SELECT * FROM sozlesmeler WHERE id = %s", (id,))
    if not sozlesme:
        flash('Sözleşme bulunamadı!', 'error')
        return redirect(url_for('sozlesme_listesi'))
    
    # Datetime objesi olarak kontrol et
    from datetime import datetime as dt
    return render_template('sozlesme_detay.html', sozlesme=sozlesme, now=dt)
# PDF oluştur ve indir
@app.route('/sozlesme/pdf/<int:id>')
@login_required
def sozlesme_pdf(id):
    """Sözleşme PDF'ini oluştur ve indir"""
    
    # Sözleşme bilgilerini al
    sozlesme = db.fetch_one("SELECT * FROM sozlesmeler WHERE id = %s", (id,))
    
    if not sozlesme:
        flash('Sözleşme bulunamadı!', 'error')
        return redirect(url_for('sozlesme_listesi'))
    
    try:
        # PDF servisini başlat
        pdf_service = PDFService()
        
        # PDF oluştur
        pdf_dosya = pdf_service.sozlesme_pdf_olustur(sozlesme)
        
        if pdf_dosya and os.path.exists(pdf_dosya):
            # PDF'i indir
            response = send_file(
                pdf_dosya,
                as_attachment=True,
                download_name=f"Sozlesme_{sozlesme['sozlesme_no']}.pdf",
                mimetype='application/pdf'
            )
            
            # İndirme sonrası dosyayı sil (opsiyonel)
            @response.call_on_close
            def remove_file(response):
                try:
                    os.remove(pdf_dosya)
                except:
                    pass
                    
            return response
        else:
            flash('PDF oluşturulamadı!', 'error')
            return redirect(url_for('sozlesme_detay', id=id))
            
    except Exception as e:
        print(f"PDF hatası: {e}")
        flash('PDF oluşturulurken hata oluştu!', 'error')
        return redirect(url_for('sozlesme_detay', id=id))
# Sözleşmeyi pasife al
@app.route('/sozlesme/pasif/<int:id>', methods=['POST'])
@login_required
def sozlesme_pasif_yap(id):
    neden = request.form.get('neden', '')
    tarih = datetime.now().date()
    
    query = """
        UPDATE sozlesmeler 
        SET durum = 'pasif', pasife_alma_tarihi = %s, pasife_alma_nedeni = %s 
        WHERE id = %s
    """
    
    if db.execute_query(query, (tarih, neden, id)):
        flash('Sözleşme pasife alındı!', 'success')
    else:
        flash('İşlem sırasında hata oluştu!', 'error')
    
    return redirect(url_for('sozlesme_listesi'))

# Raporlar
@app.route('/raporlar')
@login_required
def raporlar():
    # Aylık istatistikler
    aylik_stats = db.fetch_all("""
        SELECT 
            YEAR(baslangic_tarihi) as yil,
            MONTH(baslangic_tarihi) as ay,
            COUNT(*) as sayi,
            SUM(kira_bedeli) as toplam_kira
        FROM sozlesmeler
        WHERE durum = 'aktif'
        GROUP BY YEAR(baslangic_tarihi), MONTH(baslangic_tarihi)
        ORDER BY yil DESC, ay DESC
        LIMIT 12
    """)
    
    # Gayrimenkul tipi dağılımı
    tip_dagilim = db.fetch_all("""
        SELECT gayrimenkul_tipi, COUNT(*) as sayi
        FROM sozlesmeler
        WHERE durum = 'aktif'
        GROUP BY gayrimenkul_tipi
        ORDER BY sayi DESC
    """)
    
    # Danışman performansı
    danisman_performans = db.fetch_all("""
        SELECT 
            kiraya_veren_danisman,
            COUNT(*) as toplam_kiralama,
            SUM(komisyon_tutari) as toplam_komisyon
        FROM sozlesmeler
        GROUP BY kiraya_veren_danisman
        ORDER BY toplam_kiralama DESC
    """)
    
    return render_template('raporlar.html', 
                         aylik=aylik_stats, 
                         tip_dagilim=tip_dagilim,
                         danisman=danisman_performans)

# 404 hata sayfası
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# 500 hata sayfası
@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Veritabanı bağlantısını test et
    print("Veritabanı bağlantısı test ediliyor...")
    if db.connect():
        print("✓ Veritabanı bağlantısı başarılı!")
        db.disconnect()
    else:
        print("✗ Veritabanı bağlantısı başarısız!")
    
    # Uygulamayı başlat
    app.run(debug=True, host='127.0.0.1', port=5000)