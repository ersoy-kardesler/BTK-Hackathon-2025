"""
BTK Hackathon 2025 - MariaDB Bağlantı Modülü

Telif Hakkı © 2025 Ercan Ersoy, Erdem Ersoy
Tüm hakları saklıdır.

Bu modül config.ini dosyasını okuyarak uygulama yapılandırmalarını yükler.
"""


# Gerekli kütüphanelerin içe aktarılması
import configparser
import os
import secrets

from typing import Dict, Any


# Yapılandırma dosyasından yapılandırmaları yükleme fonksiyonu
def load_config(config_file: str = "config/config.ini") -> Dict[str, Any]:
    """
    Yapılandırma dosyasından yapılandırmaları yükleme fonksiyonu

    Parametreler:
        config_file (str): Yapılandırma dosyasının yolu

    Döndürülenler:
        Dict[str, Any]: Yapılandırmaları
    """
    # Yapılandırma dosyasının varlığını denetle
    if not os.path.exists(config_file):
        print(
            f"Uyarı: {config_file} dosyası bulunamadı."
            "Varsayılan yapılandırmalar kullanılacak."
        )
        return get_default_config(config_file)

    try:
        config = configparser.ConfigParser()
        config.read(config_file)

        # Tüm yapılandırmaları varsayılan değerlerle birlikte al
        return {
            # Flask yapılandırmaları
            "SECRET_KEY": config.get(
                "flask",
                "SECRET_KEY",
                fallback="default-secret-key"
            ),
            # Uygulama yapılandırmaları
            "DEBUG": config.getboolean("app",
                                       "DEBUG",
                                       fallback=False),
            "HOST": config.get("app",
                               "HOST",
                               fallback="0.0.0.0"),
            "PORT": config.getint("app",
                                  "PORT",
                                  fallback=5000),
            # Veri tabanı yapılandırmaları
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
            # Mevcut uygulama yapılandırmaları
            "DEBUG": config.getboolean("app",
                                       "DEBUG",
                                       fallback=False),
            "HOST": config.get("app",
                               "HOST",
                               fallback="0.0.0.0"),
            "PORT": config.getint("app",
                                  "PORT",
                                  fallback=5000),
            # GMevcut güvenlik yapılandırmaları
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


# Varsayılan yapılandırmaları döndürür ve config.ini dosyasını oluşturma
# fonksiyonu
def get_default_config(config_file: str =
                       "config/config.ini") -> Dict[str, Any]:
    """
    Varsayılan yapılandırmaları döndürür ve config.ini dosyasını oluşturma
    fonksiyonu

    Flask için güvenli rastgele gizli anahtar oluşturur.

    Döndürülenler:
        Dict[str, Any]: Varsayılan yapılandırmalar
    """
    # Flask için rastgele güvenli gizli anahtar oluştur
    # 64 karakter uzunluğunda 16 tabanındaki sayıların
    # oluşturduğu sözce
    secret_key = secrets.token_hex(32)

    # Varsayılan yapılandırmalar
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


# Yapılandırma dosyasından gizli anahtarı alma fonksiyonu
def get_secret_key(config_file: str = "config/config.ini") -> str:
    """
    Yapılandırma dosyasından gizli anahtarı alma fonksiyonu

    Parametreler:
        config_file (str): Yapılandırma dosyasının yolu

    Döndürülenler:
        str: Gizli anahtar değeri
    """

    # Yapılandırma dosyasından oku
    config = load_config(config_file)
    return config.get("SECRET_KEY", "default-secret-key")
