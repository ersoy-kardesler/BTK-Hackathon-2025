"""
Flask kimlik doğrulama dekoratörleri ve yardımcı fonksiyonlar

Bu modül Flask route'ları için kimlik doğrulama dekoratörleri
ve session yönetimi fonksiyonları sağlar.
"""

import logging
from functools import wraps
from flask import request, jsonify, session, g
from typing import Optional, Dict, Any, List
from auth.auth_manager import get_auth, get_session_manager


logger = logging.getLogger(__name__)

# Auth ve session manager'ı al
auth_manager = get_auth()
session_manager = get_session_manager()


def get_session_token() -> Optional[str]:
    """
    Request'ten session token'ını alır

    Token sırasıyla şu yerlerden aranır:
    1. Authorization header (Bearer token)
    2. session cookie
    3. request form data
    4. request args

    Returns:
        str | None: Session token veya None
    """
    # Authorization header'dan
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]

    # Session cookie'den
    if "session_token" in session:
        return session["session_token"]

    # Form data'dan
    if request.is_json:
        data = request.get_json()
        if data and "session_token" in data:
            return data["session_token"]
    elif request.form.get("session_token"):
        return request.form.get("session_token")

    # Query parameter'dan
    if request.args.get("session_token"):
        return request.args.get("session_token")

    return None


def get_client_info() -> Dict[str, str]:
    """
    İstemci bilgilerini (IP, User Agent) alır

    Returns:
        Dict[str, str]: İstemci bilgileri
    """
    # Proxy arkasındaysa gerçek IP'yi al
    ip_address = request.headers.get(
        "X-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr)
    )
    if ip_address and "," in ip_address:
        ip_address = ip_address.split(",")[0].strip()

    user_agent = request.headers.get("User-Agent", "")

    return {"ip_address": ip_address, "user_agent": user_agent}


def login_required(f):
    """
    Giriş yapmış kullanıcı gerektiren route'lar için dekoratör

    Usage:
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


def role_required(*allowed_roles):
    """
    Belirli rollere sahip kullanıcılar için dekoratör

    Args:
        allowed_roles: İzin verilen roller

    Usage:
        @app.route('/admin')
        @login_required
        @role_required('admin', 'teacher')
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


def optional_auth(f):
    """
    İsteğe bağlı kimlik doğrulama dekoratörü
    Giriş yapmış kullanıcı varsa g.current_user'a ekler,
    yoksa None olarak bırakır

    Usage:
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


def api_key_required(f):
    """
    API anahtarı gerektiren endpoint'ler için dekoratör
    Hem session token hem de API key kontrolü yapar

    Usage:
        @app.route('/api/data')
        @api_key_required
        def api_data():
            return jsonify({'data': 'secret'})
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Session token kontrolü
        token = get_session_token()
        if not token:
            return (
                jsonify(
                    {
                        "error": "API anahtarı veya session token gerekli",
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
                        "error": "Geçersiz API anahtarı veya session",
                        "code": "INVALID_API_KEY",
                    }
                ),
                401,
            )

        g.current_user = user
        g.session_token = token

        return f(*args, **kwargs)

    return decorated_function


# Flask utility fonksiyonları
def login_user_session(user_info: Dict[str, Any], session_token: str) -> None:
    """
    Kullanıcıyı Flask session'ına giriş yapar

    Args:
        user_info (Dict[str, Any]): Kullanıcı bilgileri
        session_token (str): Session token
    """
    session["session_token"] = session_token
    session["user_id"] = user_info["id"]
    session["username"] = user_info["username"]
    session["role"] = user_info["role"]
    session.permanent = True


def logout_user_session() -> None:
    """
    Kullanıcıyı Flask session'ından çıkarır
    """
    session.clear()


def get_current_user_safe() -> Optional[Dict[str, Any]]:
    """
    Güvenli şekilde mevcut kullanıcıyı alır
    Hata durumunda None döndürür

    Returns:
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


def is_user_authenticated() -> bool:
    """
    Kullanıcının giriş yapıp yapmadığını kontrol eder

    Returns:
        bool: Giriş yapmışsa True
    """
    return get_current_user_safe() is not None


def has_role(required_role: str) -> bool:
    """
    Mevcut kullanıcının belirli role sahip olup olmadığını kontrol eder

    Args:
        required_role (str): Gerekli rol

    Returns:
        bool: Role sahipse True
    """
    user = get_current_user_safe()
    if not user:
        return False

    return user.get("role") == required_role


def has_any_role(required_roles: List[str]) -> bool:
    """
    Mevcut kullanıcının herhangi bir role sahip olup olmadığını kontrol eder

    Args:
        required_roles (List[str]): Gerekli roller

    Returns:
        bool: Herhangi bir role sahipse True
    """
    user = get_current_user_safe()
    if not user:
        return False

    return user.get("role") in required_roles


# Response helper'ları
def unauthorized_response(message: str = "Giriş yapmanız gerekiyor"):
    """
    401 Unauthorized response döndürür

    Args:
        message (str): Hata mesajı

    Returns:
        Response: Flask response
    """
    return jsonify({"error": message, "code": "UNAUTHORIZED"}), 401


def forbidden_response(message: str = "Bu işlem için yetkiniz yok"):
    """
    403 Forbidden response döndürür

    Args:
        message (str): Hata mesajı

    Returns:
        Response: Flask response
    """
    return jsonify({"error": message, "code": "FORBIDDEN"}), 403


def success_response(data: Any = None, message: str = "İşlem başarılı"):
    """
    200 Success response döndürür

    Args:
        data (Any): Response verisi
        message (str): Başarı mesajı

    Returns:
        Response: Flask response
    """
    response = {"success": True, "message": message}

    if data is not None:
        response["data"] = data

    return jsonify(response), 200
