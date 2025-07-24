# BTK Hackathon 2025

**Bilgisayar Alanında Yapay Zeka Destekli Eğitim Müfredatı Oluşturup Eğitim Veren Eğitim Yönetim Sistemi**

Bu proje, Google Gemini AI entegrasyonu ile eğitim içerikleri oluşturabilen bir Flask web uygulamasıdır. Hem web arayüzü hem de backend API fonksiyonları sunmaktadır.

## 🌟 Özellikler

### Web Arayüzü
- **Ana Sayfa**: Kullanıcı dostu arayüz ile eğitim araçlarına erişim
- **Müfredat Oluşturucu**: İnteraktif form ile müfredat hazırlama
- **Responsive Tasarım**: Mobil ve masaüstü uyumlu arayüz

### Backend API

- **generate_curriculum()**: Belirtilen konu, seviye ve süreye göre detaylı eğitim müfredatı oluşturur
- **generate_lesson_plan()**: Herhangi bir konu için interaktif ders planları hazırlar
- **generate_quiz()**: Konulara özel çoktan seçmeli quiz soruları üretir
- **evaluate_assignment()**: Öğrenci ödevlerini otomatik olarak değerlendirir

## 📋 Gereksinimler

- Python 3.8+
- Flask 3.0.0
- Google Gemini API Key
- python-dotenv
- google-generativeai

## 🛠️ Kurulum

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

## 🔑 Google Gemini API Key Alma

1. [Google AI Studio](https://aistudio.google.com/) adresine gidin
2. Google hesabınızla giriş yapın
3. "Get API Key" butonuna tıklayıp oluşturulan key'i kopyalayın
4. `.env` dosyasına ekleyin

## 🧪 Test Etme

### Backend Fonksiyonlarını Test Etme
```bash
python gemini_api_test.py
```

### Web Uygulamasını Test Etme
1. Uygulamayı başlatın: `python app.py`
2. Tarayıcıda http://localhost:5000 adresine gidin
3. Müfredat oluşturma formunu deneyin

## 📁 Proje Yapısı

```
BTK-Hackathon-2025/
├── app.py                 # Ana Flask uygulaması ve backend fonksiyonları
├── gemini_api_test.py     # Backend fonksiyon test scripti
├── requirements.txt       # Python bağımlılıkları
├── README.md             # Bu dosya
├── templates/
│   └── index.html        # Ana sayfa
└── static/
    └── css/
        └── style.css     # CSS stilleri
```

## 🔒 Güvenlik

- API anahtarlarınızı asla kod içinde saklamayın
- `.env` dosyası projeye dahil değildir, kendiniz oluşturmalısınız
- `.env` dosyasını `.gitignore`'a ekleyin
- Üretim ortamında `debug=False` kullanın
- Flask secret key'ini güvenli bir şekilde oluşturun
- Google Gemini API key'i ücretsiz kullanım limitine sahiptir
- İnternet bağlantısı gereklidir (API çağrıları için)

## 📝 Lisans

Telif Hakkı (c) 2025 Ercan Ersoy, Erdem Ersoy

Bütün hakları saklıdır.
