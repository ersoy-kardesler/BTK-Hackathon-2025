# BTK Hackathon 2025 - Yapılandırma (Config) Rehberi

Bu doküman, projenin yapılandırma (config) adımlarını ve config.ini dosyasının nasıl hazırlanacağını açıklar.

## 1. Konfigürasyon Dosyasını Oluşturma

1. `config/config.ini.example` dosyasını `config/config.ini` olarak kopyalayın:
   ```bash
   cp config/config.ini.example config/config.ini
   ```
2. `config/config.ini` dosyasını bir metin düzenleyici ile açın ve aşağıdaki alanları doldurun:

### config.ini Örneği
```ini
[database]
DB_HOST = localhost
DB_PORT = 3306
DB_USER = root
DB_PASSWORD = your_password_here
DB_NAME = btk_hackathon_2025
DB_CHARSET = utf8mb4
DB_COLLATION = utf8mb4_unicode_ci

[security]
SECRET_KEY = your_secret_key_here

[app]
DEBUG = False
HOST = 127.0.0.1
PORT = 5000
```

- `DB_PASSWORD`: MariaDB/MySQL root şifrenizi girin.
- `SECRET_KEY`: Flask için güçlü bir gizli anahtar oluşturun.
- Diğer alanları ihtiyaca göre düzenleyebilirsiniz.

## 2. Yapılandırma Yükleyici

- `config/config_loader.py` dosyası, `config.ini` dosyasını okuyarak uygulama ayarlarını yükler.
- Dosya yoksa veya eksikse, varsayılan ayarlarla çalışır.
- Sistem ve kullanıcı bazında API anahtarı yönetimi kodda desteklenmektedir. Sistem anahtarı sadece fallback olarak kullanılır.
- Flask session ayarları ve güvenlik anahtarı kodda detaylandırılmıştır.

## 3. Sık Karşılaşılan Sorunlar

- `config.ini` eksik veya hatalıysa uygulama başlatılamaz ya da varsayılan ayarlarla çalışır.
- `DB_PASSWORD` veya `SECRET_KEY` gibi alanlar boş bırakılırsa güvenlik riski oluşur.
- Ortam değişkenleri eksikse API bağlantıları başarısız olur.
- Kullanıcı bazında API anahtarı tanımlanmazsa Gemini AI fonksiyonları çalışmaz.

Daha fazla bilgi için `README.md` ve `SETUP.md` dosyalarına bakınız.
