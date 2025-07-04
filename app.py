# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import Database
from config.config import SECRET_KEY
from datetime import datetime
import os
from email_service import EmailService
from pdf_service import PDFService
from flask import send_file
from functools import wraps
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user 

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
# Admin kontrolü decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Kullanıcının rolünü session'dan kontrol et
        if session.get('user_rol') != 'super_admin':
            flash('Bu sayfaya erişim yetkiniz yok!', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
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


# Kullanıcı listesi (sadece super admin)
@app.route('/kullanicilar')
@admin_required
def kullanici_listesi():
    # Debug için yazdıralım
    print("Kullanıcı listesi çağrıldı!")
    
    kullanicilar = db.fetch_all("""
        SELECT id, kullanici_adi, ad_soyad, email, rol 
        FROM kullanicilar 
        ORDER BY id DESC
    """)
    
    # Kaç kullanıcı bulundu yazdıralım
    print(f"Toplam {len(kullanicilar)} kullanıcı bulundu")
    
    return render_template('kullanici_listesi.html', kullanicilar=kullanicilar)
# Yeni kullanıcı ekle
@app.route('/kullanici/ekle', methods=['GET', 'POST'])
@admin_required
def kullanici_ekle():
    if request.method == 'POST':
        kullanici_adi = request.form.get('kullanici_adi')
        sifre = request.form.get('sifre')
        ad_soyad = request.form.get('ad_soyad')
        email = request.form.get('email')
        rol = request.form.get('rol')
        
        # Kullanıcı adı kontrolü
        mevcut = db.fetch_one("SELECT id FROM kullanicilar WHERE kullanici_adi = %s", (kullanici_adi,))
        if mevcut:
            flash('Bu kullanıcı adı zaten kullanılıyor!', 'error')
            return render_template('kullanici_ekle.html')
        
        # Şifreyi hashle
        from werkzeug.security import generate_password_hash
        hash_sifre = generate_password_hash(sifre)
        
        # Kullanıcıyı ekle
        db.execute_query("""
            INSERT INTO kullanicilar (kullanici_adi, sifre, ad_soyad, email, rol)
            VALUES (%s, %s, %s, %s, %s)
        """, (kullanici_adi, hash_sifre, ad_soyad, email, rol))
        
        flash('Kullanıcı başarıyla eklendi!', 'success')
        return redirect(url_for('kullanici_listesi'))
    
    return render_template('kullanici_ekle.html')

# Kullanıcı düzenle
@app.route('/kullanici/<int:id>/duzenle', methods=['GET', 'POST'])
@admin_required
def kullanici_duzenle(id):
    if request.method == 'POST':
        ad_soyad = request.form.get('ad_soyad')
        email = request.form.get('email')
        rol = request.form.get('rol')
        yeni_sifre = request.form.get('yeni_sifre')
        
        if yeni_sifre:
            # Yeni şifre varsa hashle ve güncelle
            from werkzeug.security import generate_password_hash
            hash_sifre = generate_password_hash(yeni_sifre)
            db.execute_query("""
                UPDATE kullanicilar 
                SET ad_soyad = %s, email = %s, rol = %s, sifre = %s
                WHERE id = %s
            """, (ad_soyad, email, rol, hash_sifre, id))
        else:
            # Şifre yoksa diğer bilgileri güncelle
            db.execute_query("""
                UPDATE kullanicilar 
                SET ad_soyad = %s, email = %s, rol = %s
                WHERE id = %s
            """, (ad_soyad, email, rol, id))
        
        flash('Kullanıcı bilgileri güncellendi!', 'success')
        return redirect(url_for('kullanici_listesi'))
    
    kullanici = db.fetch_one("SELECT * FROM kullanicilar WHERE id = %s", (id,))
    return render_template('kullanici_duzenle.html', kullanici=kullanici)

# Kullanıcı sil
@app.route('/kullanici/<int:id>/sil')
@admin_required
def kullanici_sil(id):
    # Kendini silmeye çalışıyor mu kontrol et
    if current_user.id == id:
        flash('Kendinizi silemezsiniz!', 'error')
        return redirect(url_for('kullanici_listesi'))
    
    db.execute_query("DELETE FROM kullanicilar WHERE id = %s", (id,))
    flash('Kullanıcı silindi!', 'success')
    return redirect(url_for('kullanici_listesi'))
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
            session['user_rol'] = user['rol']  
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
    
    # Sözleşme yıllarını getir
    sozlesme_yillari = db.fetch_all("""
        SELECT * FROM sozlesme_yillari 
        WHERE sozlesme_id = %s 
        ORDER BY yil_no DESC
    """, (id,))
    
    # Datetime objesi olarak kontrol et
    from datetime import datetime as dt
    return render_template('sozlesme_detay.html', 
                         sozlesme=sozlesme, 
                         sozlesme_yillari=sozlesme_yillari,
                         now=dt)
# Sözleşmeye yeni yıl ekle
@app.route('/sozlesme/<int:id>/yeni-yil', methods=['GET', 'POST'])
@login_required
def sozlesme_yeni_yil(id):
    if request.method == 'POST':
        # Form verilerini al
        yil_no = request.form.get('yil_no')
        baslangic_tarihi = request.form.get('baslangic_tarihi')
        bitis_tarihi = request.form.get('bitis_tarihi')
        aylik_kira = request.form.get('aylik_kira')
        kira_artis_orani = request.form.get('kira_artis_orani')
        notlar = request.form.get('notlar')
        
        # Veritabanına ekle
        db.execute_query("""
            INSERT INTO sozlesme_yillari 
            (sozlesme_id, yil_no, baslangic_tarihi, bitis_tarihi, 
             aylik_kira, kira_artis_orani, notlar)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id, yil_no, baslangic_tarihi, bitis_tarihi, 
              aylik_kira, kira_artis_orani, notlar))
        
        flash('Yeni sözleşme yılı eklendi!', 'success')
        return redirect(url_for('sozlesme_detay', id=id))
    
    # En son yılın bilgilerini al
    son_yil = db.fetch_one("""
        SELECT * FROM sozlesme_yillari 
        WHERE sozlesme_id = %s 
        ORDER BY yil_no DESC 
        LIMIT 1
    """, (id,))
    
    sozlesme = db.fetch_one("SELECT * FROM sozlesmeler WHERE id = %s", (id,))
    
    # Yeni başlangıç tarihini hesapla
    from datetime import datetime, timedelta
    yeni_baslangic = None
    if son_yil and son_yil.get('bitis_tarihi'):
        if isinstance(son_yil['bitis_tarihi'], str):
            bitis = datetime.strptime(son_yil['bitis_tarihi'], '%Y-%m-%d').date()
        else:
            bitis = son_yil['bitis_tarihi']
        yeni_baslangic = (bitis + timedelta(days=1)).strftime('%Y-%m-%d')
    
    return render_template('sozlesme_yeni_yil.html', 
                         sozlesme=sozlesme,
                         son_yil=son_yil,
                         yeni_baslangic=yeni_baslangic)
# Sözleşme yılı düzenle    <--- BURADAN İTİBAREN YENİ KODLARI EKLEYİN
@app.route('/sozlesme/<int:sozlesme_id>/yil/<int:yil_id>/duzenle', methods=['GET', 'POST'])
@login_required
def sozlesme_yil_duzenle(sozlesme_id, yil_id):
    if request.method == 'POST':
        # Form verilerini al
        baslangic_tarihi = request.form.get('baslangic_tarihi')
        bitis_tarihi = request.form.get('bitis_tarihi')
        aylik_kira = request.form.get('aylik_kira')
        kira_artis_orani = request.form.get('kira_artis_orani')
        notlar = request.form.get('notlar')
        
        # Güncelle
        db.execute_query("""
            UPDATE sozlesme_yillari 
            SET baslangic_tarihi = %s, bitis_tarihi = %s, 
                aylik_kira = %s, kira_artis_orani = %s, notlar = %s
            WHERE id = %s
        """, (baslangic_tarihi, bitis_tarihi, aylik_kira, 
              kira_artis_orani, notlar, yil_id))
        
        flash('Sözleşme yılı güncellendi!', 'success')
        return redirect(url_for('sozlesme_detay', id=sozlesme_id))
    
    # Mevcut yıl bilgilerini getir
    yil = db.fetch_one("SELECT * FROM sozlesme_yillari WHERE id = %s", (yil_id,))
    sozlesme = db.fetch_one("SELECT * FROM sozlesmeler WHERE id = %s", (sozlesme_id,))
    
    return render_template('sozlesme_yil_duzenle.html', 
                         sozlesme=sozlesme,
                         yil=yil)

# Sözleşme yılı sil
@app.route('/sozlesme/<int:sozlesme_id>/yil/<int:yil_id>/sil')
@login_required
def sozlesme_yil_sil(sozlesme_id, yil_id):
    # Yıl kaydını sil
    db.execute_query("DELETE FROM sozlesme_yillari WHERE id = %s", (yil_id,))
    
    flash('Sözleşme yılı silindi!', 'success')
    return redirect(url_for('sozlesme_detay', id=sozlesme_id))
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
# Favicon için özel route

@app.route('/favicon.ico')
def favicon():
    return '', 204

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