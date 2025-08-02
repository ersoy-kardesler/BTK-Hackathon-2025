"""
MariaDB veritabanı bağlantı modülü

Bu modül MariaDB veritabanı bağlantısını yönetir ve
veritabanı işlemleri için temel fonksiyonları sağlar.
"""

import logging
import mysql.connector
from mysql.connector import Error
import os
import base64
from cryptography.fernet import Fernet

from contextlib import contextmanager
from typing import Optional, Dict, Any, List, Tuple
from config.config_loader import load_config


# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """MariaDB veritabanı bağlantı sınıfı"""

    def __init__(self):
        """
        Veritabanı bağlantı ayarlarını konfigürasyon dosyasından yükler
        """
        # Konfigürasyon dosyasından yükle
        config = load_config()

        self.config = {
            "host": config.get("DB_HOST", "localhost"),
            "port": int(config.get("DB_PORT", 3306)),
            "user": config.get("DB_USER", "root"),
            "password": config.get("DB_PASSWORD", ""),
            "database": config.get("DB_NAME", "btk_hackathon_2025"),
            "charset": config.get("DB_CHARSET", "utf8mb4"),
            "collation": config.get("DB_COLLATION", "utf8mb4_unicode_ci"),
            "autocommit": True,
            "raise_on_warnings": True,
        }

    def test_connection(self) -> bool:
        """
        Veritabanı bağlantısını test eder

        Returns:
            bool: Bağlantı başarılıysa True, değilse False
        """
        try:
            connection = mysql.connector.connect(**self.config)
            if connection.is_connected():
                connection.close()
                logger.info("MariaDB bağlantısı başarılı!")
                return True
        except Error as e:
            logger.error(f"MariaDB bağlantı hatası: {e}")
            return False

    @contextmanager
    def get_connection(self):
        """
        Context manager olarak veritabanı bağlantısı sağlar

        Yields:
            mysql.connector.connection: Veritabanı bağlantısı
        """
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            yield connection
        except Error as e:
            logger.error(f"Veritabanı bağlantı hatası: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()

    @contextmanager
    def get_cursor(self,
                   dictionary=True):
        """
        Context manager olarak cursor sağlar

        Args:
            dictionary (bool): Sonuçları dict olarak döndürür

        Yields:
            mysql.connector.cursor: Veritabanı cursor'u
        """
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=dictionary)
            try:
                yield cursor
                connection.commit()
            except Error as e:
                connection.rollback()
                logger.error(f"Veritabanı sorgu hatası: {e}")
                raise
            finally:
                cursor.close()

    def execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        SELECT sorgusu çalıştırır ve sonuçları döndürür

        Args:
            query (str): SQL sorgusu
            params (tuple, optional): Sorgu parametreleri

        Returns:
            List[Dict[str, Any]]: Sorgu sonuçları
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Error as e:
            logger.error(f"Sorgu çalıştırma hatası: {e}")
            raise

    def execute_single(
        self, query: str, params: Optional[Tuple] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Tek satır döndüren SELECT sorgusu çalıştırır

        Args:
            query (str): SQL sorgusu
            params (tuple, optional): Sorgu parametreleri

        Returns:
            Dict[str, Any] | None: Sorgu sonucu veya None
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone()
        except Error as e:
            logger.error(f"Tek satır sorgu hatası: {e}")
            raise

    def execute_insert(self,
                       query: str,
                       params: Optional[Tuple] = None) -> int:
        """
        INSERT sorgusu çalıştırır ve eklenen kaydın ID'sini döndürür

        Args:
            query (str): SQL sorgusu
            params (tuple, optional): Sorgu parametreleri

        Returns:
            int: Eklenen kaydın ID'si
        """
        try:
            with self.get_cursor(dictionary=False) as cursor:
                cursor.execute(query, params or ())
                return cursor.lastrowid
        except Error as e:
            logger.error(f"Insert sorgu hatası: {e}")
            raise

    def execute_update(self,
                       query: str,
                       params: Optional[Tuple] = None) -> int:
        """
        UPDATE/DELETE sorgusu çalıştırır ve etkilenen satır sayısını döndürür

        Args:
            query (str): SQL sorgusu
            params (tuple, optional): Sorgu parametreleri

        Returns:
            int: Etkilenen satır sayısı
        """
        try:
            with self.get_cursor(dictionary=False) as cursor:
                cursor.execute(query, params or ())
                return cursor.rowcount
        except Error as e:
            logger.error(f"Update/Delete sorgu hatası: {e}")
            raise

    def execute_many(self,
                     query: str,
                     params_list: List[Tuple]) -> int:
        """
        Aynı sorguyu birden fazla parametre ile çalıştırır

        Args:
            query (str): SQL sorgusu
            params_list (List[Tuple]): Parametre listesi

        Returns:
            int: Etkilenen toplam satır sayısı
        """
        try:
            with self.get_cursor(dictionary=False) as cursor:
                cursor.executemany(query, params_list)
                return cursor.rowcount
        except Error as e:
            logger.error(f"ExecuteMany sorgu hatası: {e}")
            raise


# Singleton instance
db = DatabaseConnection()


def init_database():
    """
    Veritabanı bağlantısını test eder ve başlatır

    Returns:
        bool: Başlatma başarılıysa True
    """
    try:
        if not db.test_connection():
            logger.error("Veritabanı bağlantısı kurulamadı!")
            return False

        logger.info("Veritabanı başarıyla başlatıldı!")
        return True
    except Exception as e:
        logger.error(f"Veritabanı başlatma hatası: {e}")
        return False


def get_db():
    """
    Veritabanı instance'ını döndürür

    Returns:
        DatabaseConnection: Veritabanı bağlantı nesnesi
    """
    return db


# Yardımcı fonksiyonlar
def escape_string(value: str) -> str:
    """
    SQL injection'a karşı string'i güvenli hale getirir

    Args:
        value (str): Temizlenecek string

    Returns:
        str: Temizlenmiş string
    """
    if not isinstance(value, str):
        return str(value)

    # Temel karakterleri escape et
    return value.replace("'", "''").replace("\\", "\\\\")


def build_where_clause(conditions: Dict[str, Any]) -> Tuple[str, Tuple]:
    """
    WHERE şartlarını oluşturur

    Args:
        conditions (Dict[str, Any]): Şart koşulları

    Returns:
        Tuple[str, Tuple]: WHERE clause ve parametreler
    """
    if not conditions:
        return "", ()

    where_parts = []
    params = []

    for key, value in conditions.items():
        where_parts.append(f"{key} = %s")
        params.append(value)

    where_clause = " WHERE " + " AND ".join(where_parts)
    return where_clause, tuple(params)


# API Anahtar Yönetimi Fonksiyonları
class APIKeyManager:
    """API anahtar yönetimi için yardımcı sınıf"""

    @staticmethod
    def generate_key() -> str:
        """Şifreleme için anahtar üretir"""
        return base64.urlsafe_b64encode(os.urandom(32)).decode()

    @staticmethod
    def encrypt_api_key(api_key: str, encryption_key: str) -> str:
        """API anahtarını şifreler"""
        try:
            f = Fernet(encryption_key.encode())
            encrypted_key = f.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted_key).decode()
        except Exception as e:
            logger.error(f"API anahtar şifreleme hatası: {e}")
            return ""

    @staticmethod
    def decrypt_api_key(encrypted_api_key: str, encryption_key: str) -> str:
        """Şifrelenmiş API anahtarını çözer"""
        try:
            f = Fernet(encryption_key.encode())
            encrypted_data = base64.urlsafe_b64decode(
                             encrypted_api_key.encode())
            decrypted_key = f.decrypt(encrypted_data)
            return decrypted_key.decode()
        except Exception as e:
            logger.error(f"API anahtar şifre çözme hatası: {e}")
            return ""


def store_api_key(user_id: int, api_key: str) -> bool:
    """
    Kullanıcının Gemini API anahtarını veritabanında şifreli olarak saklar

    Args:
        user_id (int): Kullanıcı ID'si
        api_key (str): API anahtarı

    Returns:
        bool: İşlem başarılı ise True
    """
    try:
        # Şifreleme anahtarını config'den al veya oluştur
        config = load_config()
        encryption_key = config.get("ENCRYPTION_KEY")

        if not encryption_key:
            encryption_key = APIKeyManager.generate_key()
            # Bu anahtarı system_config tablosuna kaydet
            if not set_system_config("ENCRYPTION_KEY", encryption_key):
                logger.error("Şifreleme anahtarı kaydedilemedi")
                return False

        # API anahtarını şifrele
        encrypted_key = APIKeyManager.encrypt_api_key(api_key, encryption_key)
        if not encrypted_key:
            return False

        # Önce mevcut kaydı kontrol et
        existing = db.fetch_one(
            "SELECT id FROM api_keys WHERE user_id = %s",
            (user_id,),
        )

        if existing:
            # Güncelle
            success = db.execute(
                """UPDATE api_keys
                    SET api_key_encrypted = %s, updated_at = NOW()
                    WHERE user_id = %s""",
                (encrypted_key, user_id),
            )
        else:
            # Yeni kayıt ekle
            success = db.execute(
                """INSERT INTO api_keys (user_id, api_key_encrypted)
                    VALUES (%s, %s)""",
                (user_id, encrypted_key),
            )

        if success:
            logger.info(f"API anahtarı kaydedildi: user_id={user_id}")
            return True

        return False

    except Exception as e:
        logger.error(f"API anahtar kaydetme hatası: {e}")
        return False


def get_api_key(user_id: int) -> Optional[str]:
    """
    Kullanıcının Gemini API anahtarını şifreli veritabanından alır ve çözer

    Args:
        user_id (int): Kullanıcı ID'si

    Returns:
        Optional[str]: Çözülmüş API anahtarı veya None
    """
    try:
        # Şifrelenmiş anahtarı al
        result = db.fetch_one(
            """SELECT api_key_encrypted FROM api_keys
                WHERE user_id = %s AND is_active = 1""",
            (user_id,),
        )

        if not result:
            return None

        # Şifreleme anahtarını al
        encryption_key = get_system_config("ENCRYPTION_KEY")
        if not encryption_key:
            logger.error("Şifreleme anahtarı bulunamadı")
            return None

        # API anahtarını çöz
        decrypted_key = APIKeyManager.decrypt_api_key(
            result["api_key_encrypted"], encryption_key
        )
        return decrypted_key if decrypted_key else None

    except Exception as e:
        logger.error(f"API anahtar alma hatası: {e}")
        return None


def delete_api_key(user_id: int) -> bool:
    """
    Kullanıcının Gemini API anahtarını siler

    Args:
        user_id (int): Kullanıcı ID'si

    Returns:
        bool: İşlem başarılı ise True
    """
    try:
        success = db.execute(
            "DELETE FROM api_keys WHERE user_id = %s",
            (user_id,),
        )

        if success:
            logger.info(f"API anahtarı silindi: user_id={user_id}")
            return True

        return False

    except Exception as e:
        logger.error(f"API anahtar silme hatası: {e}")
        return False


def set_system_config(key: str,
                      value: str,
                      config_type: str = "string") -> bool:
    """
    Sistem konfigürasyon değeri kaydeder

    Args:
        key (str): Konfigürasyon anahtarı
        value (str): Değer
        config_type (str): Değer türü

    Returns:
        bool: İşlem başarılı ise True
    """
    try:
        # Önce mevcut kaydı kontrol et
        existing = db.fetch_one(
            "SELECT id FROM system_config WHERE config_key = %s", (key,)
        )

        if existing:
            # Güncelle
            success = db.execute(
                """UPDATE system_config
                    SET config_value = %s, config_type = %s, updated_at = NOW()
                    WHERE config_key = %s""",
                (value, config_type, key),
            )
        else:
            # Yeni kayıt ekle
            success = db.execute(
                """INSERT INTO system_config
                    (config_key, config_value, config_type)
                    VALUES (%s, %s, %s)""",
                (key, value, config_type),
            )

        return success

    except Exception as e:
        logger.error(f"Sistem konfigürasyon kaydetme hatası: {e}")
        return False


def get_system_config(key: str) -> Optional[str]:
    """
    Sistem konfigürasyon değerini alır

    Args:
        key (str): Konfigürasyon anahtarı

    Returns:
        Optional[str]: Konfigürasyon değeri veya None
    """
    try:
        result = db.fetch_one(
            "SELECT config_value FROM"
            " system_config WHERE config_key = %s", (key,)
        )

        return result["config_value"] if result else None

    except Exception as e:
        logger.error(f"Sistem konfigürasyon alma hatası: {e}")
        return None


def get_user_settings(user_id: int) -> Optional[Dict]:
    """
    Kullanıcının ayarlarını alır

    Args:
        user_id (int): Kullanıcı ID'si

    Returns:
        Optional[Dict]: Kullanıcı ayarları veya None
    """
    try:
        result = db.fetch_one(
            """SELECT gemini_api_key, gemini_model, dark_mode
                FROM user_settings WHERE user_id = %s""",
            (user_id,),
        )

        if result:
            return {
                "gemini_api_key": result["gemini_api_key"],
                "gemini_model": result["gemini_model"],
                "dark_mode": bool(result["dark_mode"]),
            }
        else:
            # Varsayılan ayarları döndür
            return {
                "gemini_api_key": None,
                "gemini_model": "gemini-2.5-flash",
                "dark_mode": False,
            }

    except Exception as e:
        logger.error(f"Kullanıcı ayarları alma hatası: {e}")
        return None


def save_user_settings(
    user_id: int,
    gemini_api_key: str = None,
    gemini_model: str = None,
    dark_mode: bool = None,
) -> bool:
    """
    Kullanıcının ayarlarını kaydeder veya günceller

    Args:
        user_id (int): Kullanıcı ID'si
        gemini_api_key (str, optional): Gemini API anahtarı
        gemini_model (str, optional): Gemini model adı
        dark_mode (bool, optional): Gece modu durumu

    Returns:
        bool: İşlem başarılıysa True, değilse False
    """
    try:
        # Önce mevcut kaydı kontrol et
        existing = db.fetch_one(
            "SELECT id FROM user_settings WHERE user_id = %s", (user_id,)
        )

        if existing:
            # Sadece gönderilen alanları güncelle
            update_fields = []
            params = []

            if gemini_api_key is not None:
                update_fields.append("gemini_api_key = %s")
                params.append(gemini_api_key)

            if gemini_model is not None:
                update_fields.append("gemini_model = %s")
                params.append(gemini_model)

            if dark_mode is not None:
                update_fields.append("dark_mode = %s")
                params.append(dark_mode)

            if update_fields:
                update_fields.append("updated_at = NOW()")
                params.append(user_id)

                query = f"UPDATE user_settings SET"
                "{', '.join(update_fields)} WHERE user_id = %s"
                success = db.execute(query, tuple(params))
            else:
                # Hiçbir alan güncellenmedi ama başarılı sayalım
                success = True
        else:
            # Yeni kayıt ekle
            success = db.execute(
                "INSERT INTO user_settings (user_id, gemini_api_key, "
                "gemini_model, dark_mode) VALUES (%s, %s, %s, %s)",
                (
                    user_id,
                    gemini_api_key if gemini_api_key is not None else None,
                    gemini_model if gemini_model is not None
                    else "gemini-2.5-flash",
                    dark_mode if dark_mode is not None else False,
                ),
            )

        return success

    except Exception as e:
        logger.error(f"Kullanıcı ayarları kaydetme hatası: {e}")
        return False


def get_user_gemini_api_key(user_id: int) -> Optional[str]:
    """
    Kullanıcının Gemini API anahtarını alır.
    Eğer kullanıcının kendi anahtarı yoksa
    sistem varsayılan anahtarını döndürür.

    Args:
        user_id (int): Kullanıcı ID'si

    Returns:
        Optional[str]: API anahtarı veya None
    """
    try:
        # Önce kullanıcının kendi anahtarını kontrol et
        result = db.fetch_one(
            "SELECT gemini_api_key FROM user_settings "
            "WHERE user_id = %s AND gemini_api_key IS NOT NULL",
            (user_id,),
        )

        if result and result["gemini_api_key"]:
            return result["gemini_api_key"]

        # Kullanıcının anahtarı yoksa sistem anahtarını al
        return get_system_config("GEMINI_API_KEY")

    except Exception as e:
        logger.error(f"Kullanıcı Gemini API anahtarı alma hatası: {e}")
        return None
