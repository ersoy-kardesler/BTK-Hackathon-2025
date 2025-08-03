"""
BTK Hackathon 2025 - Flask Kimlik Doğrulama ve Oturum Modülü

Telif Hakkı © 2025 Ersoy Kardeşler
Bütün hakları saklıdır.

Bu modül Flask yönlendirmeleri için kimlik doğrulama ve
oturum yönetimi fonksiyonları sağlar.
"""


# Gerekli kütüphanelerin içe aktarılması
import logging
from functools import wraps
from flask import request, jsonify, session, g
from typing import Optional, Dict, Any, List
from auth.auth_manager import get_auth, get_session_manager


logger = logging.getLogger(__name__)

# Kullanıcı doğrulamayı ve oturum yöneticisini al
auth_manager = get_auth()
session_manager = get_session_manager()


# İstekten oturum işaretçisini alma fonksiyonu
def get_session_token() -> Optional[str]:
    """
    İstekten oturum işaretçisini alma fonksiyonu

    Oturum işaretçisi sırasıyla şu yerlerden aranır:
    1. Kullanıcı doğrulama başlığı
    2. Oturum çerezi
    3. JSON veya form verisi isteği
    4. Parametre isteği

    Döndürülenler:
        str | None: Oturum işaretçisi veya None
    """
    # Kullanıcı doğrulama başlığından
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]

    # Oturum çerezinden
    if "session_token" in session:
        return session["session_token"]

    # Form verisinden
    if request.is_json:
        data = request.get_json()
        if data and "session_token" in data:
            return data["session_token"]
    elif request.form.get("session_token"):
        return request.form.get("session_token")

    # Parametre isteğinden
    if request.args.get("session_token"):
        return request.args.get("session_token")

    return None


# İstemci bilgilerini alma fonksiyonu
def get_client_info() -> Dict[str, str]:
    """
    İstemci bilgilerini alma fonksiyonu

    Döndürülenler:
        Dict[str, str]: İstemci bilgileri
    """
    # Proxy arkasındaysa gerçek IP adresini al
    ip_address = request.headers.get(
        "X-Forwarded-For", request.headers.get("X-Real-IP",
                                               request.remote_addr)
    )
    if ip_address and "," in ip_address:
        ip_address = ip_address.split(",")[0].strip()

    user_agent = request.headers.get("User-Agent", "")

    return {"ip_address": ip_address, "user_agent": user_agent}


# Giriş yapmış kullanıcı gerektiren yönelndirmeler için denetim fonksiyonu
def login_required(f):
    """
    Giriş yapmış kullanıcı gerektiren yönelndirmeler için denetim fonksiyonu

    Kullanım:
        @app.route('/protected')
        @login_required
        def protected_route():
            return f"Merhaba {g.current_user['username']}"
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_session_token()

        if not token:
            return (
                jsonify(
                    {
                        "error": "Giriş yapmanız gerekiyor",
                        "code": "AUTHENTICATION_REQUIRED",
                    }
                ),
                401,
            )

        user = auth_manager.get_current_user(token)
        if not user:
            return (
                jsonify(
                    {
                        "error": "Geçersiz veya süresi dolmuş oturum",
                        "code": "INVALID_SESSION",
                    }
                ),
                401,
            )

        # Kullanıcı bilgilerini g object'ine ekle
        g.current_user = user
        g.session_token = token

        return f(*args, **kwargs)

    return decorated_function


# Belirli rollere sahip kullanıcılar için denetim fonksiyonu
def role_required(*allowed_roles):
    """
    Belirli rollere sahip kullanıcılar için denetim fonksiyonu

    Parametreler:
        allowed_roles: İzin verilen roller

    Kullanım:
        @app.route('/admin')
        @login_required
        @role_required('admin', 'normal')
        def admin_route():
            return "Admin sayfası"
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, "current_user") or not g.current_user:
                return (
                    jsonify(
                        {
                            "error": "Giriş yapmanız gerekiyor",
                            "code": "AUTHENTICATION_REQUIRED",
                        }
                    ),
                    401,
                )

            user_role = g.current_user.get("role")
            if user_role not in allowed_roles:
                return (
                    jsonify(
                        {
                            "error": "Bu işlem için yetkiniz yok",
                            "code": "INSUFFICIENT_PERMISSIONS",
                            "required_roles": list(allowed_roles),
                            "user_role": user_role,
                        }
                    ),
                    403,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# İsteğe bağlı kimlik doğrulama detimi fonksiyonu
def optional_auth(f):
    """
    İsteğe bağlı kimlik doğrulama detimi fonksiyonu

    Giriş yapmış kullanıcı varsa g.current_user'a ekler,
    yoksa None olarak bırakır

    Kullanım:
        @app.route('/public')
        @optional_auth
        def public_route():
            if g.current_user:
                return f"Merhaba {g.current_user['username']}"
            return "Merhaba misafir"
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_session_token()
        g.current_user = None
        g.session_token = None

        if token:
            user = auth_manager.get_current_user(token)
            if user:
                g.current_user = user
                g.session_token = token

        return f(*args, **kwargs)

    return decorated_function


# API anahtarı gerektiren uç noktalar için denetim fonksiyonu
def api_key_required(f):
    """
    API anahtarı gerektiren uç noktalar için denetim fonksiyonu

    Hem oturum işlaretçisi hem de API anahtarı denetimi yapar

    Kullanım:
        @app.route('/api/data')
        @api_key_required
        def api_data():
            return jsonify({'data': 'secret'})
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Oturum işaretçisi denetimi
        token = get_session_token()
        if not token:
            return (
                jsonify(
                    {
                        "error": "API anahtarı veya oturum işaretçisi gerekli",
                        "code": "API_KEY_REQUIRED",
                    }
                ),
                401,
            )

        user = auth_manager.get_current_user(token)
        if not user:
            return (
                jsonify(
                    {
                        "error": "Geçersiz API anahtarı veya oturum",
                        "code": "INVALID_API_KEY",
                    }
                ),
                401,
            )

        g.current_user = user
        g.session_token = token

        return f(*args, **kwargs)

    return decorated_function


# Kullanıcıyı Flask oturumuna giriş yapma fonksiyonu
def login_user_session(user_info: Dict[str, Any], session_token: str) -> None:
    """
    Kullanıcıyı Flask oturumuna giriş yapma fonksiyonu

    Parametreler:
        user_info (Dict[str, Any]): Kullanıcı bilgileri
        session_token (str): Oturum işaretçisi
    """
    session["session_token"] = session_token
    session["user_id"] = user_info["id"]
    session["username"] = user_info["username"]
    session["role"] = user_info["role"]
    session.permanent = True


# Kullanıcıyı Flask oturumundan çıkarma fonksiyonu
def logout_user_session() -> None:
    """
    Kullanıcıyı Flask oturumundan çıkarma fonksiyonu
    """
    session.clear()


# Güvenli şekilde mevcut kullanıcıyı alma fonksiyonu
def get_current_user_safe() -> Optional[Dict[str, Any]]:
    """
    Güvenli şekilde mevcut kullanıcıyı alma fonksiyonu

    Hata durumunda None döndürür

    Döndürülenler:
        Dict[str, Any] | None: Kullanıcı bilgileri
    """
    try:
        if hasattr(g, "current_user"):
            return g.current_user

        token = get_session_token()
        if token:
            return auth_manager.get_current_user(token)

        return None
    except Exception as e:
        logger.error(f"Mevcut kullanıcı alma hatası: {e}")
        return None


# Kullanıcının giriş yapıp yapmadığını denetleme fonksiyonu
def is_user_authenticated() -> bool:
    """
    Kullanıcının giriş yapıp yapmadığını denetleme fonksiyonu

    Döndürülenler:
        bool: Giriş yapmışsa True
    """
    return get_current_user_safe() is not None


# Mevcut kullanıcının belirli role sahip olup olmadığını denetleme fonksiyonu
def has_role(required_role: str) -> bool:
    """
    Mevcut kullanıcının belirli role sahip olup olmadığını denetleme
    fonksiyonu

    Parametreler:
        required_role (str): Gerekli rol

    Döndürülenler:
        bool: Role sahipse True
    """
    user = get_current_user_safe()
    if not user:
        return False

    return user.get("role") == required_role


# Mevcut kullanıcının herhangi bir role sahip olup olmadığını denetleme
# fonksiyonu
def has_any_role(required_roles: List[str]) -> bool:
    """
    Mevcut kullanıcının herhangi bir role sahip olup olmadığını denetleme
    fonksiyonu

    Parametreler:
        required_roles (List[str]): Gerekli roller

    Döndürülenler:
        bool: Herhangi bir role sahipse True
    """
    user = get_current_user_safe()
    if not user:
        return False

    return user.get("role") in required_roles


# Yetkisiz yanıtı döndürürme fonksiyonu
def unauthorized_response(message: str = "Giriş yapmanız gerekiyor"):
    """
    Yetkisiz yanıtı döndürürme fonksiyonu

    HTTP 401 yanıtı döndürür.

    Parametreler:
        message (str): Hata mesajı

    Döndürülenler:
        Response: Flask response
    """
    return jsonify({"error": message, "code": "UNAUTHORIZED"}), 401


# Reddedilen yanıtı döndürme fonksiyonu
def forbidden_response(message: str = "Bu işlem için yetkiniz yok"):
    """
    Reddedilen yanıtı döndürme fonksiyonu

    HTTP 403 yanıtı döndürür.

    Parametreler:
        message (str): Hata mesajı

    Döndürülenler:
        Response: Flask response
    """
    return jsonify({"error": message, "code": "FORBIDDEN"}), 403


# Başarılı yanıtı döndürme fonksiyonu
def success_response(data: Any = None, message: str = "İşlem başarılı"):
    """
    Başarılı yanıtı döndürme fonksiyonu

    HTTP 200 yanıtı döndürür.

    Parametreler:
        data (Any): Yanıt verisi
        message (str): Başarı iletisi

    Döndürülenler:
        Response: Flask yanıtı
    """
    response = {"success": True, "message": message}

    if data is not None:
        response["data"] = data

    return jsonify(response), 200
