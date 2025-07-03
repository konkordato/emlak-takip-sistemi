# database.py
import pymysql
from pymysql import Error
from config.config import DB_CONFIG
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.connection = None
        
    def connect(self):
        """Veritabanına bağlan"""
        try:
            self.connection = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                charset=DB_CONFIG['charset'],
                cursorclass=pymysql.cursors.DictCursor
            )
            return True
        except Error as e:
            print(f"Veritabanı bağlantı hatası: {e}")
            return False
    
    def disconnect(self):
        """Veritabanı bağlantısını kapat"""
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query, params=None):
        """Sorgu çalıştır (INSERT, UPDATE, DELETE)"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return True
        except Error as e:
            print(f"Sorgu hatası: {e}")
            return False
        finally:
            self.disconnect()
    
    def fetch_all(self, query, params=None):
        """Tüm sonuçları getir (SELECT)"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Veri çekme hatası: {e}")
            return []
        finally:
            self.disconnect()
    
    def fetch_one(self, query, params=None):
        """Tek sonuç getir"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Veri çekme hatası: {e}")
            return None
        finally:
            self.disconnect()
    
    def get_next_sozlesme_no(self):
        """Yeni sözleşme numarası al"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            
            # Mevcut numarayı al ve güncelle
            cursor.execute("UPDATE sozlesme_sayac SET son_numara = son_numara + 1 WHERE id = 1")
            self.connection.commit()
            
            # Yeni numarayı al
            cursor.execute("SELECT son_numara FROM sozlesme_sayac WHERE id = 1")
            result = cursor.fetchone()
            
            return result['son_numara'] if result else 1
        except Error as e:
            print(f"Sözleşme numarası hatası: {e}")
            return None
        finally:
            self.disconnect()
    
    def get_yaklasan_sozlesmeler(self):
        """60 gün içinde bitecek sözleşmeleri getir"""
        try:
            bugun = datetime.now().date()
            alti_ay_sonra = bugun + timedelta(days=60)
            
            query = """
                SELECT * FROM sozlesmeler 
                WHERE durum = 'aktif' 
                AND bitis_tarihi BETWEEN %s AND %s
                AND uyari_gonderildi = FALSE
                ORDER BY bitis_tarihi ASC
            """
            
            return self.fetch_all(query, (bugun, alti_ay_sonra))
        except Error as e:
            print(f"Yaklaşan sözleşmeler hatası: {e}")
            return []