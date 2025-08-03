# BTK Hackathon 2025 - Yapılandırma (Config) Rehberi

Bu doküman, projenin yapılandırma (config) adımlarını ve config.ini dosyasının nasıl hazırlanacağını açıklar.

## Konfigürasyon Dosyasını Oluşturma

1. `config/config.ini.example` dosyasını `config/config.ini` olarak kopyalayın:
   ```bash
   cp config/config.ini.example config/config.ini
   ```
2. `config/config.ini` dosyasını bir metin düzenleyici ile açın ve aşağıdaki alanları doldurun:

## config.ini Örneği
```ini
[flask]
secret_key = secret-key

[app]
debug = True
host = 0.0.0.0
port = 5000

[database]
db_host = localhost
db_port = 3306
db_user = root
db_password = database_password
db_name = btk_hackathon_2025
db_charset = utf8mb4
db_collation = utf8mb4_unicode_ci

[security]
session_cookie_secure = True
session_cookie_httponly = True
permanent_session_lifetime = 3600

```

- `DB_PASSWORD`: MariaDB/MySQL root şifrenizi girin.
- `SECRET_KEY`: Flask için güçlü bir gizli anahtar oluşturun.
- Diğer alanları ihtiyaca göre düzenleyebilirsiniz.

## Yapılandırma Yükleyici

- `config/config_loader.py` dosyası, `config.ini` dosyasını okuyarak uygulama ayarlarını yükler.
- Dosya yoksa veya eksikse, varsayılan ayarlarla çalışır.
- Sistem ve kullanıcı bazında API anahtarı yönetimi kodda desteklenmektedir. Sistem anahtarı sadece fallback olarak kullanılır.
- Flask session ayarları ve güvenlik anahtarı kodda detaylandırılmıştır.

## Sık Karşılaşılan Sorunlar

- `config.ini` eksik veya hatalıysa uygulama başlatılamaz ya da varsayılan ayarlarla çalışır.
- `DB_PASSWORD` veya `SECRET_KEY` gibi alanlar boş bırakılırsa güvenlik riski oluşur.
- Ortam değişkenleri eksikse API bağlantıları başarısız olur.
- Kullanıcı bazında API anahtarı tanımlanmazsa Gemini AI fonksiyonları çalışmaz.

Daha fazla bilgi için `README.md` ve `SETUP.md` dosyalarına bakınız.
