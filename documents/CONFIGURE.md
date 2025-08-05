# BTK Hackathon 2025 - Yapılandırma Rehberi

Bu belge, projenin yapılandırma adımlarını ve yapılandırma dosyasının nasıl hazırlanacağını açıklar.

## Yapılandırma Dosyasını Oluşturma

1. `config/config.ini.example` dosyasını `config/config.ini` olarak kopyalayın:

2. `config/config.ini` dosyasını bir metin düzenleyici ile açın ve aşağıdaki alanları doldurun:

## Yapılandırma Yükleyici

- `config/config_loader.py` dosyası, `config.ini` dosyasını okuyarak uygulama ayarlarını yükler.
- Dosya yoksa veya eksikse, varsayılan ayarlarla çalışır.
- Sistem ve kullanıcı temelinde API anahtarı yönetimi kodda desteklenmektedir. Sistem anahtarı sadece yedek anahtar olarak kullanılır.
- Flask oturum ayarları ve güvenlik anahtarı kodda detaylandırılmıştır.

## Sık Karşılaşılan Sorunlar

- `config.ini` eksik veya hatalıysa uygulama başlatılamaz ya da varsayılan ayarlarla çalışır.
- `DB_PASSWORD` veya `SECRET_KEY` gibi alanlar boş bırakılırsa güvenlik riski oluşur.
- Ortam değişkenleri eksikse API bağlantıları başarısız olur.
- Kullanıcı temelinde API anahtarı tanımlanmazsa Gemini ile ilgili fonksiyonlar çalışmaz.

Daha fazla bilgi için `SETUP.md` dosyasına bakınız.
