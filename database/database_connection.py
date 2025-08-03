"""
BTK Hackathon 2025 - MariaDB Bağlantı Modülü

Telif Hakkı © 2025 Ersoy Kardeşler
Bütün hakları saklıdır.

Bu modül MariaDB bağlantısını yönetir ve veri tabanı işlemleri için
temel fonksiyonları sağlar.
"""


# Gerekli kütüphanelerin içe aktarılması
import base64
import logging
import mysql.connector
import os
import textwrap

from contextlib import contextmanager
from cryptography.fernet import Fernet
from mysql.connector import Error
from typing import Optional, Dict, Any, List, Tuple

from config.config_loader import load_config


# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Veri tabanı bağlantı sınıfı
class DatabaseConnection:
    """MariaDB veri tabanı bağlantı sınıfı"""

    # Yapıcı fonksiyon
    def __init__(self):
        # Yapılandırma dosyasından yükle
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

    # Veri tabanı bağlantısını sınama fonksiyonu
    def test_connection(self) -> bool:
        """
        Veri tabanı bağlantısını sınama fonksiyonu

        Döndürülenler:
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

    # Bağlam yöneticisi olarak veri tabanı bağlantısı sağlama fonksiyonu
    @contextmanager
    def get_connection(self):
        """
        Bağlam yöneticisi olarak veri tabanı bağlantısı sağlama fonksiyonu

        Yields:
            mysql.connector.connection: Veri tabanı bağlantısı
        """
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            yield connection
        except Error as e:
            logger.error(f"Veri tabanı bağlantı hatası: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()

    # Bağlam yöneticisi olarak imleç sağlama fonksiyonu
    @contextmanager
    def get_cursor(self, dictionary=True):
        """
        Bağlam yöneticisi olarak imleç sağlama fonksiyonu

        Parametreler:
            dictionary (bool): Sonuçları sözlük olarak döndürür

        Yields:
            mysql.connector.cursor: Veri tabanı imleci
        """
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=dictionary)
            try:
                yield cursor
                connection.commit()
            except Error as e:
                connection.rollback()
                logger.error(f"Veri tabanı sorgu hatası: {e}")
                raise
            finally:
                cursor.close()

    # SELECT sorgusu çalıştırır ve sonuçları döndürme fonksiyonu
    def execute_query(
        self, query: str, params: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        SELECT sorgusu çalıştırır ve sonuçları döndürme fonksiyonu

        Parametreler:
            query (str): SQL sorgusu
            params (tuple, optional): Sorgu parametreleri

        Döndürülenler:
            List[Dict[str, Any]]: Sorgu sonuçları
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Error as e:
            logger.error(f"Sorgu çalıştırma hatası: {e}")
            raise

    # Tek satır döndüren SELECT sorgusu çalıştırma fonksiyonu
    def execute_single(
        self, query: str, params: Optional[Tuple] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Tek satır döndüren SELECT sorgusu çalıştırma fonksiyonu

        Parametreler:
            query (str): SQL sorgusu
            params (tuple, optional): Sorgu parametreleri

        Döndürülenler:
            Dict[str, Any] | None: Sorgu sonucu veya None
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone()
        except Error as e:
            logger.error(f"Tek satır sorgu hatası: {e}")
            raise

    # INSERT sorgusu çalıştırma ve eklenen kaydın kimliğini döndürme
    # fonksiyonu
    def execute_insert(
            self, query: str, params: Optional[Tuple] = None
    ) -> int:
        """
        INSERT sorgusu çalıştırma ve eklenen kaydın kimliğini döndürme
        fonksiyonu

        Parametreler:
            query (str): SQL sorgusu
            params (tuple, optional): Sorgu parametreleri

        Döndürülenler:
            int: Eklenen kaydın kimliği
        """
        try:
            with self.get_cursor(dictionary=False) as cursor:
                cursor.execute(query, params or ())
                return cursor.lastrowid
        except Error as e:
            logger.error(f"Insert sorgu hatası: {e}")
            raise

    # UPDATE/DELETE sorgusu çalıştırma ve etkilenen satır sayısını
    # döndürme fonksiyonu
    def execute_update(
            self, query: str, params: Optional[Tuple] = None
    ) -> int:
        """
        UPDATE/DELETE sorgusu çalıştırma ve etkilenen
        satır sayısını döndürme fonksiyonu

        Parametreler:
            query (str): SQL sorgusu
            params (tuple, optional): Sorgu parametreleri

        Döndürülenler:
            int: Etkilenen satır sayısı
        """
        try:
            with self.get_cursor(dictionary=False) as cursor:
                cursor.execute(query, params or ())
                return cursor.rowcount
        except Error as e:
            logger.error(f"Update/Delete sorgu hatası: {e}")
            raise

    # Aynı sorguyu birden fazla parametre ile çalıştırma fonksiyonu
    def execute_many(
            self, query: str, params_list: List[Tuple]
    ) -> int:
        """
        Aynı sorguyu birden fazla parametre ile çalıştırma
        fonksiyonu

        Parametreler:
            query (str): SQL sorgusu
            params_list (List[Tuple]): Parametre listesi

        Döndürülenler:
            int: Etkilenen toplam satır sayısı
        """
        try:
            with self.get_cursor(dictionary=False) as cursor:
                cursor.executemany(query, params_list)
                return cursor.rowcount
        except Error as e:
            logger.error(f"ExecuteMany sorgu hatası: {e}")
            raise

    # SELECT sorgusu çalıştırır ve tek satır döndürme fonksiyonu
    def fetch_one(
        self, query: str, params: Optional[Tuple] = None
    ) -> Optional[Dict[str, Any]]:
        """
        SELECT sorgusu çalıştırır ve tek satır döndürme
        fonksiyonu

        Parametreler:
            query (str): SQL sorgusu
            params (tuple, optional): Sorgu parametreleri

        Döndürülenler:
            Dict[str, Any] | None: Sorgu sonucu veya None
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone()
        except Error as e:
            logger.error(f"fetch_one sorgu hatası: {e}")
            raise


# Tekil örnek
db = DatabaseConnection()


# Veri tabanı bağlantısını sınama ve başlatma fonksiyonu
def init_database():
    """
    Veri tabanı bağlantısını sınama ve başlatma fonksiyonu

    Döndürülenler:
        bool: Başlatma başarılıysa True
    """
    try:
        if not db.test_connection():
            logger.error("Veri tabanı bağlantısı kurulamadı!")
            return False

        logger.info("Veri tabanı başarıyla başlatıldı!")
        return True
    except Exception as e:
        logger.error(f"Veri tabanı başlatma hatası: {e}")
        return False


# Veri tabanı örneğini döndürme fonksiyonu
def get_db():
    """
    Veri tabanı örneğini döndürme fonksiyonu

    Döndürülenler:
        DatabaseConnection: Veri tabanı bağlantı nesnesi
    """
    return db


# SQL enjektesine karşı sözcesi güvenli hale getirme fonksiyonu
def escape_string(
        value: str
) -> str:
    """
    SQL injection'a karşı  sözcesi güvenli hale getirme fonksiyonu

    Parametreler:
        value (str): Temizlenecek sözce

    Döndürülenler:
        str: Temizlenmiş sözce
    """
    if not isinstance(value, str):
        return str(value)

    # Temel karakterleri escape et
    return value.replace("'", "''").replace("\\", "\\\\")


# WHERE şartlarını oluşturma fonksiyonu
def build_where_clause(
        conditions: Dict[str, Any]
) -> Tuple[str, Tuple]:
    """
    WHERE şartlarını oluşturma fonksiyonu

    Parametreler:
        conditions (Dict[str, Any]): Şart koşulları

    Döndürülenler:
        Tuple[str, Tuple]: WHERE cümlesi ve parametreler
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


# API anahtar yönetimi için yardımcı sınıf fonksiyonu
class APIKeyManager:
    """API anahtar yönetimi için yardımcı sınıf"""

    @staticmethod
    def generate_key() -> str:
        """Şifreleme için anahtar üretir"""
        return base64.urlsafe_b64encode(os.urandom(32)).decode()

    @staticmethod
    def encrypt_api_key(
        api_key: str, encryption_key: str
    ) -> str:
        """API anahtarını şifreler"""
        try:
            f = Fernet(encryption_key.encode())
            encrypted_key = f.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted_key).decode()
        except Exception as e:
            logger.error(f"API anahtar şifreleme hatası: {e}")
            return ""

    @staticmethod
    def decrypt_api_key(
        encrypted_api_key: str, encryption_key: str
     ) -> str:
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


# Kullanıcının Gemini API anahtarını veri tabanında
# şifreli olarak saklama fonksiyonu
def store_api_key(
        user_id: int, api_key: str
) -> bool:
    """
    Kullanıcının Gemini API anahtarını veri tabanında şifreli olarak
    saklama fonksiyonu

    Parametreler:
        user_id (int): Kullanıcı ID'si
        api_key (str): API anahtarı

    Döndürülenler:
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

        # Önce mevcut kaydı denetle
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


# Kullanıcının Gemini API anahtarını şifreli veri tabanından alma ve
# çözme fonksiyonu
def get_api_key(
        user_id: int
) -> Optional[str]:
    """
    Kullanıcının Gemini API anahtarını şifreli veri tabanından alma ve
    çözme fonksiyonu

    Parametreler:
        user_id (int): Kullanıcı ID'si

    Döndürülenler:
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
    except Exception as e:
        logger.error(f"API anahtar alma hatası: {e}")
        return False


# Başlangıç veri tabanı şemasını MariaDB'ye uygulama fonksiyonu
def initialize_database_schema():
    """
    Başlangıç veri tabanı şemasını MariaDB'ye uygulama fonksiyonu

    Kurulum sırasında çağrıldığında Veri tabanı ve
     tüm tablolar otomatik olarak oluşturulur.
    """

    config = load_config()
    base_config = dict(config)

    db_name = base_config.get("DB_NAME", "btk_hackathon_2025")
    db_charset = base_config.get("DB_CHARSET", "utf8mb4")
    db_collation = base_config.get("DB_COLLATION", "utf8mb4_unicode_ci")

    schema_sql = textwrap.dedent(
        f"""
        CREATE DATABASE IF NOT EXISTS {db_name}
            CHARACTER SET {db_charset} COLLATE {db_collation};
        USE {db_name};

        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            role ENUM('admin', 'normal') DEFAULT 'normal',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            INDEX idx_username (username),
            INDEX idx_email (email),
            INDEX idx_role (role),
            INDEX idx_is_active (is_active)
        ) ENGINE=InnoDB CHARACTER SET {db_charset} COLLATE {db_collation};

        CREATE TABLE IF NOT EXISTS user_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            session_token VARCHAR(255) NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_session_token (session_token),
            INDEX idx_user_id (user_id),
            INDEX idx_expires_at (expires_at)
        ) ENGINE=InnoDB CHARACTER SET {db_charset} COLLATE {db_collation};

        CREATE TABLE IF NOT EXISTS education_contents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            subject VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_favorite BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_subject (subject),
            INDEX idx_generated_at (generated_at),
            INDEX idx_is_favorite (is_favorite)
        ) ENGINE=InnoDB CHARACTER SET {db_charset} COLLATE {db_collation};

        CREATE TABLE IF NOT EXISTS assignment_evaluations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            assignment_text TEXT NOT NULL,
            criteria TEXT NOT NULL,
            evaluation_result TEXT NOT NULL,
            score DECIMAL(5,2),
            evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_evaluated_at (evaluated_at),
            INDEX idx_score (score)
        ) ENGINE=InnoDB CHARACTER SET {db_charset} COLLATE {db_collation};

        CREATE TABLE IF NOT EXISTS user_activity_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            action VARCHAR(100) NOT NULL,
            details TEXT,
            ip_address VARCHAR(45),
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_action (action),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB CHARACTER SET {db_charset} COLLATE {db_collation};

        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            token VARCHAR(255) NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_token (token),
            INDEX idx_user_id (user_id),
            INDEX idx_expires_at (expires_at)W
        ) ENGINE=InnoDB CHARACTER SET {db_charset} COLLATE {db_collation};

        CREATE TABLE IF NOT EXISTS api_keys (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            key_name VARCHAR(100) NOT NULL,
            api_key_encrypted TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON
                UPDATE CURRENT_TIMESTAMP,
            last_used TIMESTAMP NULL,
            usage_count INT DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_is_active (is_active),
            INDEX idx_last_used (last_used),
            UNIQUE KEY unique_user_key_name (user_id, key_name)
        ) ENGINE=InnoDB CHARACTER SET {db_charset} COLLATE {db_collation};

        CREATE TABLE IF NOT EXISTS user_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            gemini_api_key TEXT,
            gemini_model VARCHAR(100) DEFAULT 'gemini-2.5-flash',
            dark_mode BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON
             UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE KEY unique_user_settings (user_id),
            INDEX idx_user_id (user_id)
        ) ENGINE=InnoDB CHARACTER SET {db_charset} COLLATE {db_collation};

        CREATE TABLE IF NOT EXISTS system_config (
            id INT AUTO_INCREMENT PRIMARY KEY,
            config_key VARCHAR(100) NOT NULL UNIQUE,
            config_value TEXT,
            config_type ENUM('string', 'integer', 'boolean', 'json')
                DEFAULT 'string',
            description TEXT,
            is_encrypted BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON
                UPDATE CURRENT_TIMESTAMP,
            INDEX idx_config_key (config_key),
            INDEX idx_config_type (config_type)
        ) ENGINE=InnoDB CHARACTER SET {db_charset} COLLATE {db_collation};

        INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES
            ('admin',
             'admin@example.com',
             '$2b$12$/8h7BqnsU7KWStkQTXAsPeUlFgxVeO8hVZWBd0tGSdOgxFr3j7kxO',
             'Admin User',
             'admin'),
            ('user',
             'user@example.com',
             '$2b$12$/8h7BqnsU7KWStkQTXAsPeUlFgxVeO8hVZWBd0tGSdOgxFr3j7kxO',
             'Normal User',
             'normal')
        ON DUPLICATE KEY UPDATE id=id;

        INSERT INTO system_config (
            config_key,
            config_value,
            config_type,
            description
        ) VALUES
            ('app_name',
             'BTK Hackathon 2025 - Eğitim Asistanı',
             'string',
             'Uygulama adı'),
            ('app_version',
             '1.0.0',
             'string',
             'Uygulama versiyonu'),
            ('maintenance_mode',
             'false',
             'boolean',
             'Bakım modu durumu'),
            ('max_file_size',
             '10485760',
             'integer',
             'Maksimum dosya boyutu (byte)'),
            ('session_timeout',
             '86400',
             'integer',
             'Oturum zaman aşımı (saniye)'),
            ('gemini_model',
             'gemini-2.5-flash',
             'string',
             'Varsayılan Gemini model'),
            ('max_education_length',
             '5000',
             'integer',
             'Maksimum eğitim içeriği uzunluğu'),
            ('max_assignment_length',
             '3000',
             'integer',
             'Maksimum ödev uzunluğu'),
            ('default_user_role',
             'normal',
             'string',
             'Varsayılan kullanıcı rolü'),
            ('email_notifications',
             'true',
             'boolean',
             'E-posta bildirimleri aktif mi'),
            ('backup_retention_days',
             '30',
             'integer',
             'Yedek dosyaları saklama süresi')
        ON DUPLICATE KEY UPDATE config_value = VALUES(config_value);

        CREATE VIEW user_stats AS
        SELECT
            u.id,
            u.username,
            u.full_name,
            u.role,
            u.created_at,
            u.last_login,
            COUNT(DISTINCT ec.id) AS education_count,
            COUNT(DISTINCT ae.id) AS assignment_count,
            AVG(ae.score) AS avg_assignment_score
        FROM users u
        LEFT JOIN education_contents ec ON u.id = ec.user_id
        LEFT JOIN assignment_evaluations ae ON u.id = ae.user_id
        WHERE u.is_active = TRUE
        GROUP BY u.id, u.username, u.full_name, u.role, u.created_at,
                u.last_login;
    """
    )

    try:
        connection = mysql.connector.connect(
            host=base_config.get("DB_HOST", "localhost"),
            port=int(base_config.get("DB_PORT", 3306)),
            user=base_config.get("DB_USER", "root"),
            password=base_config.get("DB_PASSWORD", ""),
            charset=base_config.get("DB_CHARSET", "utf8mb4"),
            autocommit=True,
        )
        cursor = connection.cursor()
        # Komutları ayırıp sırayla çalıştır
        statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                logger.debug(f"SQL komutu {i}/{len(statements)} başarılı")
            except Exception as exc:
                logger.warning(f"SQL komutu {i}/{len(statements)} atlandı/"
                               f"hata: {exc}\nKomut: {statement[:200]}...")
        cursor.close()
        connection.close()
        logger.info("Veri tabanı şeması başarıyla uygulandı.")
        return True
    except Exception as exc:
        logger.error(f"Veri tabanı şeması oluşturulamadı: {exc}")
        return False


# Kullanıcının Gemini API anahtarını silme fonksiyonu
def delete_api_key(
        user_id: int
) -> bool:
    """
    Kullanıcının Gemini API anahtarını silme fonksiyonu

    Parametreler:
        user_id (int): Kullanıcı ID'si

    Döndürülenler:
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


# Sistem yapılandırması değeri kaydetme fonksiyonu
def set_system_config(
        key: str, value: str, config_type: str = "string"
) -> bool:
    """
    Sistem yapılandırması değeri kaydetme fonksiyonu

    Parametreler:
        key (str): Yapılandırma anahtarı
        value (str): Değer
        config_type (str): Değer türü

    Döndürülenler:
        bool: İşlem başarılı ise True
    """
    try:
        # Önce mevcut kaydı denetle
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
        logger.error(f"Sistem yapılandırması kaydetme hatası: {e}")
        return False


# Sistem yapılandırma değerini alma fonksiyonu
def get_system_config(key: str) -> Optional[str]:
    """
    Sistem yapılandırma değerini alma fonksiyonu

    Parametreler:
        key (str): Yapılandırma anahtarı

    Döndürülenler:
        Optional[str]: Konfigürasyon değeri veya None
    """
    try:
        db_instance = get_db()
        result = db_instance.execute_single(
            "SELECT config_value FROM system_config WHERE config_key = %s",
            (key,)
        )
        return result["config_value"] if result else None
    except Exception as e:
        logger.error(f"Sistem yapılandırma alma hatası: {e}")
        return None


# Kullanıcı ayarlarını alma fonksiyonu
def get_user_settings(user_id: int) -> Optional[Dict]:
    """
    Kullanıcının ayarlarını alma fonksiyonu

    Parametreler:
        user_id (int): Kullanıcı ID'si

    Döndürülenler:
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


# Kullanıcının ayarlarını kaydetme fonksiyonu
def save_user_settings(
    user_id: int,
    gemini_api_key: str = None,
    gemini_model: str = None,
    dark_mode: bool = None,
) -> bool:
    """
    Kullanıcının ayarlarını kaydetme fonksiyonu

    Parametreler:
        user_id (int): Kullanıcı ID'si
        gemini_api_key (str, optional): Gemini API anahtarı
        gemini_model (str, optional): Gemini model adı
        dark_mode (bool, optional): Gece modu durumu

    Döndürülenler:
        bool: İşlem başarılıysa True, değilse False
    """
    try:
        # Önce mevcut kaydı denetle
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
                query = f"UPDATE user_settings SET {', '.join(update_fields)}"
                "WHERE user_id = %s"
                params.append(user_id)
                affected = db.execute_update(query, tuple(params))
                success = affected > 0
            else:
                # Hiçbir alan güncellenmedi ama başarılı sayalım
                success = True
        else:
            # Yeni kayıt ekle
            query = (
                "INSERT INTO user_settings (user_id, gemini_api_key, "
                "gemini_model, dark_mode) VALUES (%s, %s, %s, %s)"
            )
            params = (
                user_id,
                gemini_api_key if gemini_api_key is not None
                else None,
                gemini_model if gemini_model is not None
                else "gemini-2.5-flash",
                dark_mode if dark_mode is not None
                else False,
            )
            inserted_id = db.execute_insert(query, params)
            success = inserted_id is not None and inserted_id > 0

        return success

    except Exception as e:
        logger.error(f"Kullanıcı ayarları kaydetme hatası: {e}")
        return False


# Kullanıcının Gemini API anahtarını alma fonksiyonu
def get_user_gemini_api_key(user_id: int) -> Optional[str]:
    """
    Kullanıcının Gemini API anahtarını alma fonksiyonu

    Eğer kullanıcının kendi anahtarı yoksa
    sistem varsayılan anahtarını döndürür.

    Parametreler:
        user_id (int): Kullanıcı ID'si

    Döndürülenler:
        Optional[str]: API anahtarı veya None
    """
    try:
        # Önce kullanıcının kendi anahtarını denetle
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
