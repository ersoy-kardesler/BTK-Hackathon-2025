# BTK Hackathon 2025

**Bilgisayar Alanında Yapay Zeka Destekli Eğitim Oluşturup Eğitim Veren Eğitim Yönetim Sistemi**

Bu proje, Google Gemini AI entegrasyonu ile eğitim içerikleri oluşturabilen bir Flask web uygulamasıdır. Hem web arayüzü hem de backend API fonksiyonları sunmaktadır.

## Özellikler

### Web Arayüzü
- **Ana Sayfa**: Kullanıcı dostu arayüz ile eğitim araçlarına erişim
- **Eğitim Oluşturucu**: İnteraktif form ile eğitim hazırlama
- **Ödev Değerlendirici**: Öğrenci ödevlerini AI ile otomatik değerlendirme
- **Responsive Tasarım**: Mobil ve masaüstü uyumlu arayüz

### Backend API Fonksiyonları
- **Eğitim Oluşturma**: `generate_education()` - Detaylı eğitim müfredatı oluşturma
- **Ödev Değerlendirme**: `evaluate_assignment()` - Öğrenci ödevlerini değerlendirme ve geri bildirim
- **Google Gemini AI Entegrasyonu**: Gelişmiş AI destekli içerik üretimi

## Gereksinimler

- Python 3.8+
- Flask 3.0.0
- python-dotenv 1.0.0
- google-generativeai 0.8.3
- mysql-connector-python 8.2.0
- bcrypt 4.1.2
- cryptography 45.0.5

## Kurulum

1. **Projeyi klonlayın:**
```bash
git clone https://github.com/ersoy-kardesler/BTK-Hackathon-2025.git
cd BTK-Hackathon-2025
```

2. **Sanal ortam oluşturun ve aktifleştirin:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows
```

3. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

4. **Konfigürasyon dosyasını ayarlayın:**

   **Ana Konfigürasyon (config.ini dosyası):**
   - `config.ini.example` dosyasını `config.ini` olarak kopyalayın
   - Aşağıdaki bölümleri doldurun:
   ```ini
   [database]
   DB_HOST = localhost
   DB_PORT = 3306
   DB_USER = root
   DB_PASSWORD = your_password_here
   DB_NAME = btk_hackathon_2025

   [api]
   # İlk çalıştırmada veritabanına kaydedilir
   GEMINI_API_KEY = your_gemini_api_key_here
   GEMINI_MODEL = gemini-2.5-flash

   [security]
   SECRET_KEY = your_secret_key_here

   [app]
   DEBUG = False
   HOST = 127.0.0.1
   PORT = 5000
   ```

   **Not:** Gemini API anahtarı ilk çalıştırmada config.ini dosyasından alınıp veritabanına kaydedilir. Sonraki çalıştırmalarda veritabanından kullanılır.

5. **MariaDB/MySQL veritabanını ayarlayın:**
```bash
# MariaDB veya MySQL'e bağlanın
mysql -u root -p

# Veritabanını oluşturun
CREATE DATABASE btk_hackathon_2025;

# Şemayı import edin
mysql -u root -p btk_hackathon_2025 < database_schema.sql
```

5. **Uygulamayı başlatın:**
```bash
python app.py
```

6. **Tarayıcınızda açın:**
   - http://localhost:5000 adresine gidin

## Google Gemini API Key Alma

1. [Google AI Studio](https://aistudio.google.com/) adresine gidin
2. Google hesabınızla giriş yapın
3. "Get API Key" butonuna tıklayıp oluşturulan key'i kopyalayın
4. `.env` dosyasına ekleyin

## Test Etme

### Backend Fonksiyonlarını Test Etme
```bash
python test_generating_education.py
python test_evaluate_assignment.py
```

### Web Uygulamasını Test Etme
1. Uygulamayı başlatın: `python app.py`
2. Tarayıcıda http://localhost:5000 adresine gidin
3. Ana sayfa üzerinden farklı özellikleri test edin:
   - **Eğitim Oluşturma**: Konu, süre ve ders süresi belirleyerek eğitim oluşturun
   - **Ödev Değerlendirme**: Öğrenci ödevlerini yükleyip AI ile değerlendirin

## Proje Yapısı

```
BTK-Hackathon-2025/
├── app.py                            # Ana Flask uygulaması ve route'lar
├── config/
│   └── config_loader.py              # INI dosyası okuyucu modülü
├── requirements.txt                  # Python bağımlılıkları
├── README.md                         # Bu dosya
├── .env                              # API anahtarları (gizli dosya)
├── .gitignore                        # Git için dışlanma dosyası ('.env' mutlaka eklenmeli)
├── test_generating_education.py      # Eğitim oluşturma test scripti
├── test_evaluate_assignment.py       # Ödev değerlendirme test scripti
├── education/
│   ├── generate_education.py         # Eğitim oluşturma fonksiyonu
│   └── evaluate_assignment.py        # Ödev değerlendirme fonksiyonu
├── templates/
│   ├── index.html                    # Ana sayfa
│   ├── education.html                # Eğitim oluşturma sayfası
│   └── assignment_evaluate.html      # Ödev değerlendirme sayfası
├── static/
│   └── css/
│       └── style.css                 # CSS stilleri
└── test/
    └── README.txt                    # Test sonuçları açıklaması
```

## API Kullanımı

Proje ayrıca backend fonksiyonlarını doğrudan Python scriptlerinde kullanabilmenizi sağlar:

### Eğitim Oluşturma
```python
from education.generate_education import generate_education
import google.generativeai as genai

# API'yi yapılandır
genai.configure(api_key="your_api_key")
model = genai.GenerativeModel('gemini-pro')

# Eğitim oluştur
result = generate_education(
    subject="Python Programlama",
    duration="12 hafta",
    lesson_duration=90,
    question_count=15,
    model=model
)
print(result)
```

### Ödev Değerlendirme
```python
from education.evaluate_assignment import evaluate_assignment

# Ödev değerlendir
evaluation = evaluate_assignment(
    assignment_text="Öğrenci ödev metni...",
    criteria="Kod kalitesi, algoritma verimliliği, dokümantasyon",
    model=model
)
print(evaluation)
```

## Güvenlik

- API anahtarlarınızı asla kod içinde saklamayın
- `.env` dosyası projeye dahil değildir, kendiniz oluşturmalısınız
- `.env` dosyasını `.gitignore`'a ekleyin
- Üretim ortamında `debug=False` kullanın
- Flask secret key'ini güvenli bir şekilde oluşturun
- Google Gemini API key'i ücretsiz kullanım limitine sahiptir
- İnternet bağlantısı gereklidir (API çağrıları için)

## Teknik Detaylar

### Kullanılan Teknolojiler
- **Backend**: Flask (Python Web Framework)
- **AI**: Google Gemini API (Generative AI)
- **Database**: MySQL/MariaDB
- **Şifreleme**: bcrypt, cryptography
- **Frontend**: HTML5, CSS3, JavaScript
- **Paket Yönetimi**: pip, requirements.txt
- **Çevre Değişkenleri**: python-dotenv

### Modüler Yapı
- `app.py`: Flask uygulaması programı
- `education/generate_education.py`: Eğitim oluşturma programı
- `education/evaluate_assignment.py`: Ödev değerlendirme programı
- `config/config_loader.py`: Konfigürasyon yönetimi
- `templates/`: HTML şablonları
- `static/`: CSS ve statik dosyalar
- `test/`: Test sonuçları ve dokümantasyon

## Lisans

Telif Hakkı © 2025 Ersoy Kardeşler

Bütün hakları saklıdır.
