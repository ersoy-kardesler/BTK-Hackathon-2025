"""
Konfigürasyon dosyası okuyucu modülü

Bu modül config.ini dosyasını okuyarak uygulama ayarlarını yükler.
"""

import configparser
import os
import secrets
from typing import Dict, Any


def load_config(config_file: str = "config/config.ini") -> Dict[str, Any]:
    """
    INI dosyasından konfigürasyon ayarlarını yükler.

    Args:
        config_file (str): Konfigürasyon dosyasının yolu

    Returns:
        Dict[str, Any]: Konfigürasyon ayarları
    """
    # INI dosyasının varlığını kontrol et
    if not os.path.exists(config_file):
        print(
            f"Uyarı: {config_file} dosyası bulunamadı."
            "Varsayılan ayarlar kullanılacak."
        )
        return get_default_config(config_file)

    try:
        config = configparser.ConfigParser()
        config.read(config_file)

        # Tüm ayarları varsayılan değerlerle birlikte al
        return {
            # Flask ayarları
            "SECRET_KEY": config.get(
                "flask",
                "SECRET_KEY",
                fallback="default-secret-key"
            ),
            # Uygulama ayarları
            "DEBUG": config.getboolean("app",
                                       "DEBUG",
                                       fallback=False),
            "HOST": config.get("app",
                               "HOST",
                               fallback="0.0.0.0"),
            "PORT": config.getint("app",
                                  "PORT",
                                  fallback=5000),
            # Veritabanı ayarları
            "DB_HOST": config.get("database",
                                  "DB_HOST",
                                  fallback="localhost"),
            "DB_PORT": config.getint("database",
                                     "DB_PORT",
                                     fallback=3306),
            "DB_USER": config.get("database",
                                  "DB_USER",
                                  fallback="root"),
            "DB_PASSWORD": config.get("database",
                                      "DB_PASSWORD",
                                      fallback=""),
            "DB_NAME": config.get("database",
                                  "DB_NAME",
                                  fallback="btk_hackathon_2025"),
            "DB_CHARSET": config.get("database",
                                     "DB_CHARSET",
                                     fallback="utf8mb4"),
            "DB_COLLATION": config.get(
                "database",
                "DB_COLLATION",
                fallback="utf8mb4_unicode_ci"
            ),
            # Uygulama ayarları (mevcut)
            "DEBUG": config.getboolean("app",
                                       "DEBUG",
                                       fallback=False),
            "HOST": config.get("app",
                               "HOST",
                               fallback="0.0.0.0"),
            "PORT": config.getint("app",
                                  "PORT",
                                  fallback=5000),
            # Güvenlik ayarları (mevcut)
            "SESSION_COOKIE_SECURE": config.getboolean(
                "security",
                "SESSION_COOKIE_SECURE",
                fallback=True
            ),
            "SESSION_COOKIE_HTTPONLY": config.getboolean(
                "security",
                "SESSION_COOKIE_HTTPONLY",
                fallback=True
            ),
            "PERMANENT_SESSION_LIFETIME": config.getint(
                "security",
                "PERMANENT_SESSION_LIFETIME",
                fallback=3600
            ),
        }

    except Exception as e:
        print(f"Konfigürasyon dosyası okunurken hata oluştu: {e}")
        return get_default_config()


def get_default_config(config_file: str =
                       "config/config.ini") -> Dict[str, Any]:
    """
    Varsayılan konfigürasyon ayarlarını döndürür ve
    config.ini dosyasını oluşturur.
    Flask için güvenli rastgele secret key oluşturur.

    Returns:
        Dict[str, Any]: Varsayılan ayarlar
    """
    # Flask için rastgele güvenli secret key oluştur
    secret_key = secrets.token_hex(32)  # 64 karakter uzunluğunda hex string

    # Varsayılan ayarlar
    defaults = {
        "SECRET_KEY": secret_key,
        "DEBUG": False,
        "HOST": "0.0.0.0",
        "PORT": 5000,
        "DB_HOST": "localhost",
        "DB_PORT": 3306,
        "DB_USER": "root",
        "DB_PASSWORD": "",
        "DB_NAME": "btk_hackathon_2025",
        "DB_CHARSET": "utf8mb4",
        "DB_COLLATION": "utf8mb4_unicode_ci",
        "GEMINI_API_KEY": "",
        "GEMINI_MODEL": "gemini-2.5-flash",
        "SESSION_COOKIE_SECURE": True,
        "SESSION_COOKIE_HTTPONLY": True,
        "PERMANENT_SESSION_LIFETIME": 3600,
    }

    config = configparser.ConfigParser()
    config.add_section("flask")
    config.set("flask", "SECRET_KEY", defaults["SECRET_KEY"])

    config.add_section("app")
    config.set("app", "DEBUG", str(defaults["DEBUG"]))
    config.set("app", "HOST", defaults["HOST"])
    config.set("app", "PORT", str(defaults["PORT"]))

    config.add_section("database")
    config.set("database", "DB_HOST", defaults["DB_HOST"])
    config.set("database", "DB_PORT", str(defaults["DB_PORT"]))
    config.set("database", "DB_USER", defaults["DB_USER"])
    config.set("database", "DB_PASSWORD", defaults["DB_PASSWORD"])
    config.set("database", "DB_NAME", defaults["DB_NAME"])
    config.set("database", "DB_CHARSET", defaults["DB_CHARSET"])
    config.set("database", "DB_COLLATION", defaults["DB_COLLATION"])

    config.add_section("security")
    config.set(
        "security", "SESSION_COOKIE_SECURE",
        str(defaults["SESSION_COOKIE_SECURE"])
    )
    config.set(
        "security", "SESSION_COOKIE_HTTPONLY",
        str(defaults["SESSION_COOKIE_HTTPONLY"])
    )
    config.set(
        "security",
        "PERMANENT_SESSION_LIFETIME",
        str(defaults["PERMANENT_SESSION_LIFETIME"]),
    )

    with open(config_file, "w") as configfile:
        config.write(configfile)

    return defaults


def get_secret_key(config_file: str = "config/config.ini") -> str:
    """
    INI dosyasından SECRET_KEY'i alır.
    Sadece INI dosyasından okur, çevre değişkeni kullanmaz.

    Args:
        config_file (str): Konfigürasyon dosyasının yolu

    Returns:
        str: Secret key değeri
    """

    # INI dosyasından oku
    config = load_config(config_file)
    return config.get("SECRET_KEY", "default-secret-key")
