# BTK Hackathon 2025

**Bilgisayar Alanında Yapay Zeka Destekli Eğitim Müfredatı Oluşturup Eğitim Veren Eğitim Yönetim Sistemi**

Bu proje, Google Gemini AI entegrasyonu ile eğitim içerikleri oluşturabilen bir Flask web uygulamasıdır. Hem web arayüzü hem de backend API fonksiyonları sunmaktadır.

## Özellikler

### Web Arayüzü
- **Ana Sayfa**: Kullanıcı dostu arayüz ile eğitim araçlarına erişim
- **Müfredat Oluşturucu**: İnteraktif form ile müfredat hazırlama
- **Ödev Değerlendirici**: Öğrenci ödevlerini AI ile otomatik değerlendirme
- **Responsive Tasarım**: Mobil ve masaüstü uyumlu arayüz

### Backend API Fonksiyonları
- **Müfredat Oluşturma**: `generate_curriculum()` - Detaylı eğitim müfredatı oluşturma
- **Ödev Değerlendirme**: `evaluate_assignment()` - Öğrenci ödevlerini değerlendirme ve geri bildirim
- **Google Gemini AI Entegrasyonu**: Gelişmiş AI destekli içerik üretimi

## Gereksinimler

- Python 3.8+
- Flask 3.0.0
- Google Gemini API Key
- python-dotenv 1.0.0
- google-generativeai 0.8.3

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

4. **Çevre değişkenlerini ayarlayın:**
   - Proje klasöründe `.env` dosyası oluşturun
   - Aşağıdaki içeriği `.env` dosyasına ekleyin:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here
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
python test_generating_curriculum.py
```

### Web Uygulamasını Test Etme
1. Uygulamayı başlatın: `python app.py`
2. Tarayıcıda http://localhost:5000 adresine gidin
3. Ana sayfa üzerinden farklı özelliikleri test edin:
   - **Müfredat Oluşturma**: Konu, süre ve ders süresi belirleyerek müfredat oluşturun
   - **Ödev Değerlendirme**: Öğrenci ödevlerini yükleyip AI ile değerlendirin

## Proje Yapısı

```
BTK-Hackathon-2025/
├── app.py                            # Ana Flask uygulaması ve route'lar
├── generate_curriculum.py            # Müfredat oluşturma fonksiyonu
├── evaluate_assignment.py            # Ödev değerlendirme fonksiyonu
├── test_generating_curriculum.py     # Backend fonksiyon test scripti
├── requirements.txt                  # Python bağımlılıkları
├── README.md                         # Bu dosya
├── .gitignore                        # Git için dışlanma dosyası
├── .env                              # API anahtarları (gizli dosya)
├── templates/
│   ├── index.html                    # Ana sayfa
│   ├── curriculum.html               # Müfredat oluşturma sayfası
│   └── assignment_evaluate.html      # Ödev değerlendirme sayfası
└── static/
    └── css/
        └── style.css                 # CSS stilleri
```

## API Kullanımı

Proje ayrıca backend fonksiyonlarını doğrudan Python scriptlerinde kullanabilmenizi sağlar:

### Müfredat Oluşturma
```python
from generate_curriculum import generate_curriculum
import google.generativeai as genai

# API'yi yapılandır
genai.configure(api_key="your_api_key")
model = genai.GenerativeModel('gemini-pro')

# Müfredat oluştur
result = generate_curriculum(
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
from evaluate_assignment import evaluate_assignment

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
- **Frontend**: HTML5, CSS3, JavaScript
- **Paket Yönetimi**: pip, requirements.txt
- **Çevre Değişkenleri**: python-dotenv

### Modüler Yapı
- `app.py`: Flask uygulaması ve route tanımları
- `generate_curriculum.py`: Müfredat oluşturma algoritması
- `evaluate_assignment.py`: Ödev değerlendirme algoritması
- `templates/`: HTML şablonları
- `static/`: CSS ve statik dosyalar

## Lisans

Telif Hakkı © 2025 Ersoy Kardeşler

Bütün hakları saklıdır.
