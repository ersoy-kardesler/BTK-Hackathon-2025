"""
Kullanıcı kimlik doğrulama modülü

Bu modül kullanıcı girişi, çıkışı ve oturum yönetimi
fonksiyonlarını sağlar.
"""

import bcrypt
import logging
import secrets

from database.database_connection import get_db
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple


logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Kimlik doğrulama hataları için özel exception"""

    pass


class SessionManager:
    """Oturum yönetimi sınıfı"""

    def __init__(self):
        self.db = get_db()
        self.session_duration = timedelta(hours=24)  # 24 saat

    def generate_session_token(self) -> str:
        """
        Güvenli oturum token'ı oluşturur

        Returns:
            str: Oturum token'ı
        """
        return secrets.token_urlsafe(32)

    def create_session(
        self, user_id: int, ip_address: str = None, user_agent: str = None
    ) -> str:
        """
        Kullanıcı için yeni oturum oluşturur

        Args:
            user_id (int): Kullanıcı ID'si
            ip_address (str, optional): IP adresi
            user_agent (str, optional): User agent bilgisi

        Returns:
            str: Oturum token'ı
        """
        try:
            token = self.generate_session_token()
            expires_at = datetime.now() + self.session_duration

            query = """
                INSERT INTO user_sessions
                 (user_id, session_token, expires_at, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s)
            """

            self.db.execute_insert(
                query, (user_id, token, expires_at, ip_address, user_agent)
            )

            # Kullanıcının son giriş zamanını güncelle
            self.update_last_login(user_id)

            logger.info(f"Kullanıcı {user_id} için yeni oturum oluşturuldu")
            return token

        except Exception as e:
            logger.error(f"Oturum oluşturma hatası: {e}")
            raise AuthenticationError("Oturum oluşturulamadı")

    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Oturum token'ını doğrular

        Args:
            token (str): Oturum token'ı

        Returns:
            Dict[str, Any] | None: Kullanıcı bilgileri veya None
        """
        try:
            query = """
                SELECT s.user_id, s.expires_at, u.username, u.email,
                 u.full_name, u.role, u.is_active
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = %s AND s.expires_at > NOW()
            """

            result = self.db.execute_single(query, (token,))

            if result and result["is_active"]:
                return result

            # Süresi dolmuş veya geçersiz token
            if result and not result["is_active"]:
                logger.warning(f"Pasif kullanıcı oturum girişi:" "{result['username']}")

            return None

        except Exception as e:
            logger.error(f"Oturum doğrulama hatası: {e}")
            return None

    def destroy_session(self, token: str) -> bool:
        """
        Oturumu sonlandırır

        Args:
            token (str): Oturum token'ı

        Returns:
            bool: İşlem başarılıysa True
        """
        try:
            query = "DELETE FROM user_sessions WHERE session_token = %s"
            affected_rows = self.db.execute_update(query, (token,))

            if affected_rows > 0:
                logger.info("Oturum başarıyla sonlandırıldı")
                return True

            return False

        except Exception as e:
            logger.error(f"Oturum sonlandırma hatası: {e}")
            return False

    def destroy_user_sessions(self, user_id: int) -> bool:
        """
        Kullanıcının tüm oturumlarını sonlandırır

        Args:
            user_id (int): Kullanıcı ID'si

        Returns:
            bool: İşlem başarılıysa True
        """
        try:
            query = "DELETE FROM user_sessions WHERE user_id = %s"
            affected_rows = self.db.execute_update(query, (user_id,))

            logger.info(
                f"Kullanıcı {user_id} için " "{affected_rows} oturum sonlandırıldı"
            )
            return True

        except Exception as e:
            logger.error(f"Kullanıcı oturumları sonlandırma hatası: {e}")
            return False

    def update_last_login(self, user_id: int) -> bool:
        """
        Kullanıcının son giriş zamanını günceller

        Args:
            user_id (int): Kullanıcı ID'si

        Returns:
            bool: İşlem başarılıysa True
        """
        try:
            query = "UPDATE users SET last_login = NOW() WHERE id = %s"
            self.db.execute_update(query, (user_id,))
            return True

        except Exception as e:
            logger.error(f"Son giriş zamanı güncelleme hatası: {e}")
            return False

    def cleanup_expired_sessions(self) -> int:
        """
        Süresi dolmuş oturumları temizler

        Returns:
            int: Temizlenen oturum sayısı
        """
        try:
            query = "DELETE FROM user_sessions WHERE expires_at < NOW()"
            affected_rows = self.db.execute_update(query)

            if affected_rows > 0:
                logger.info(f"{affected_rows} süresi dolmuş oturum temizlendi")

            return affected_rows

        except Exception as e:
            logger.error(f"Oturum temizleme hatası: {e}")
            return 0


class UserAuth:
    """Kullanıcı kimlik doğrulama sınıfı"""

    def __init__(self):
        self.db = get_db()
        self.session_manager = SessionManager()

    def hash_password(self, password: str) -> str:
        """
        Şifreyi güvenli şekilde hash'ler

        Args:
            password (str): Ham şifre

        Returns:
            str: Hash'lenmiş şifre
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Şifreyi doğrular

        Args:
            password (str): Ham şifre
            password_hash (str): Hash'lenmiş şifre

        Returns:
            bool: Şifre doğruysa True
        """
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), password_hash.encode("utf-8")
            )
        except Exception:
            return False

    def login(
        self,
        username_or_email: str,
        password: str,
        ip_address: str = None,
        user_agent: str = None,
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Kullanıcı girişi yapar

        Args:
            username_or_email (str): Kullanıcı adı veya e-posta
            password (str): Şifre
            ip_address (str, optional): IP adresi
            user_agent (str, optional): User agent

        Returns:
            Tuple[bool, Optional[str], Optional[Dict]]:
            (Başarı durumu, Session token, Kullanıcı bilgileri)
        """
        try:
            # Kullanıcıyı bul
            query = """
                SELECT id, username, email, password_hash, full_name, role,
                 is_active
                 FROM users
                 WHERE (username = %s OR email = %s) AND is_active = TRUE
            """

            user = self.db.execute_single(query, (username_or_email, username_or_email))

            if not user:
                logger.warning(f"Geçersiz giriş denemesi: {username_or_email}")
                return False, None, None

            # Şifreyi doğrula
            if not self.verify_password(password, user["password_hash"]):
                logger.warning(f"Hatalı şifre girişi: {user['username']}")
                return False, None, None

            # Oturum oluştur
            session_token = self.session_manager.create_session(
                user["id"], ip_address, user_agent
            )

            # Hassas bilgileri kaldır
            user_info = {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
            }

            logger.info(f"Başarılı giriş: {user['username']}")
            return True, session_token, user_info

        except Exception as e:
            logger.error(f"Giriş hatası: {e}")
            return False, None, None

    def logout(self, session_token: str) -> bool:
        """
        Kullanıcı çıkışı yapar

        Args:
            session_token (str): Oturum token'ı

        Returns:
            bool: İşlem başarılıysa True
        """
        return self.session_manager.destroy_session(session_token)

    def get_current_user(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Oturum token'ından kullanıcı bilgilerini getirir

        Args:
            session_token (str): Oturum token'ı

        Returns:
            Dict[str, Any] | None: Kullanıcı bilgileri
        """
        return self.session_manager.validate_session(session_token)

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str = None,
        role: str = "student",
    ) -> Tuple[bool, Optional[str]]:
        """
        Yeni kullanıcı kaydeder

        Args:
            username (str): Kullanıcı adı
            email (str): E-posta
            password (str): Şifre
            full_name (str, optional): Tam ad
            role (str): Kullanıcı rolü

        Returns:
            Tuple[bool, Optional[str]]: (Başarı durumu, Hata mesajı)
        """
        try:
            # Kullanıcı adı ve e-posta kontrolü
            check_query = """
                SELECT COUNT(*) as count FROM users
                 WHERE username = %s OR email = %s
            """

            existing = self.db.execute_single(check_query, (username, email))
            if existing and existing["count"] > 0:
                return False, "Kullanıcı adı veya e-posta zaten kullanımda"

            # Şifreyi hash'le
            password_hash = self.hash_password(password)

            # Kullanıcıyı kaydet
            insert_query = """
                INSERT INTO users (username, email, password_hash,
                 full_name, role)
                 VALUES (%s, %s, %s, %s, %s)
            """

            user_id = self.db.execute_insert(
                insert_query, (username, email, password_hash, full_name, role)
            )

            if user_id:
                logger.info(f"Yeni kullanıcı kaydedildi: {username}")
                return True, None

            return False, "Kullanıcı kaydedilemedi"

        except Exception as e:
            logger.error(f"Kullanıcı kaydetme hatası: {e}")
            return False, "Kayıt işlemi sırasında hata oluştu"

    def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Kullanıcı şifresini değiştirir

        Args:
            user_id (int): Kullanıcı ID'si
            old_password (str): Eski şifre
            new_password (str): Yeni şifre

        Returns:
            Tuple[bool, Optional[str]]: (Başarı durumu, Hata mesajı)
        """
        try:
            # Mevcut şifreyi kontrol et
            query = "SELECT password_hash FROM users WHERE id = %s"
            user = self.db.execute_single(query, (user_id,))

            if not user:
                return False, "Kullanıcı bulunamadı"

            if not self.verify_password(old_password, user["password_hash"]):
                return False, "Mevcut şifre hatalı"

            # Yeni şifreyi hash'le ve güncelle
            new_hash = self.hash_password(new_password)
            update_query = "UPDATE users SET password_hash = %s WHERE id = %s"

            affected_rows = self.db.execute_update(update_query, (new_hash, user_id))

            if affected_rows > 0:
                # Kullanıcının diğer oturumlarını sonlandır
                self.session_manager.destroy_user_sessions(user_id)
                logger.info(f"Kullanıcı {user_id} şifresi değiştirildi")
                return True, None

            return False, "Şifre güncellenemedi"

        except Exception as e:
            logger.error(f"Şifre değiştirme hatası: {e}")
            return False, "Şifre değiştirme sırasında hata oluştu"


# Singleton instances
auth = UserAuth()
session_manager = SessionManager()


def get_auth():
    """
    Auth instance'ını döndürür

    Returns:
        UserAuth: Auth nesnesi
    """
    return auth


def get_session_manager():
    """
    Session manager instance'ını döndürür

    Returns:
        SessionManager: Session manager nesnesi
    """
    return session_manager
