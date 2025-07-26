"""
BTK Hackathon 2025 - Google Gemini API Test Uygulaması

Bu dosya, app.py'deki AI fonksiyonlarının doğru çalışıp çalışmadığını test eder.
Tüm API çağrılarını sırayla çalıştırarak sonuçları konsola yazdırır.

Kullanım:
    python test_generating.py

Gereksinimler:
- .env dosyasında GEMINI_API_KEY tanımlı olmalı
- app.py ile aynı dizinde bulunmalı
- Internet bağlantısı (API çağrıları için)

Yazarlar: Ersoy Kardeşler
Tarih: Temmuz 2025
"""

# Gerekli kütüphanelerin içe aktarılması
import os  # Çevresel değişkenlere erişim için
import google.generativeai as genai  # Google Gemini API için

from generate_curriculum import generate_curriculum # Müfredat oluşturma fonksiyonu
from dotenv import load_dotenv  # .env dosyasını yüklemek için

def get_gemini_model():
    """
    Google Gemini API modelini yapılandırır ve döndürür.
    """
    load_dotenv()  # .env dosyasını yükle
    api_key = os.getenv('GEMINI_API_KEY')  # API anahtarını al
    if not api_key:
        raise RuntimeError('GEMINI_API_KEY .env dosyasında tanımlı olmalı!')  # Hata fırlat
    genai.configure(api_key=api_key)  # API anahtarını yapılandır
    return genai.GenerativeModel('gemini-2.5-flash')  # Modeli döndür

def test_generate_all():
    """
    generate_all fonksiyonunu test eder ve sonuçları konsola yazdırır.
    """
    print("🚀 Google Gemini API Test (Tüm İçerikler) Başlatılıyor...\n")
    print("=" * 70)  # Görsel ayırıcı
    model = get_gemini_model()  # Modeli al
    subject = "Bilgisayar Mühendisliği"  # Test konusu
    duration = "14 hafta"  # Test süresi
    lesson_duration = 60  # Ders süresi (dakika)
    question_count = 10  # Quiz soru sayısı

    # generate_all fonksiyonunu çağır
    generate_curriculum(subject, duration, lesson_duration, question_count, model=model)

if __name__ == "__main__":
    """
    Ana test fonksiyonu. Tüm testleri çalıştırır ve sonuçları konsola yazdırır.
    """
    print("🔧 BTK Hackathon 2025 - API Test Uygulaması (Tüm İçerikler)")
    print("=" * 60)  # Görsel ayırıcı
    print("📅 Test Tarihi:", "26 Temmuz 2025")  # Test tarihi
    print("👥 Geliştirici: Ersoy Kardeşler")  # Geliştirici bilgisi
    print("=" * 60)
    try:
        test_generate_all()  # Test fonksiyonunu çalıştır
    except KeyboardInterrupt:
        print("\n\n⏹️  Test kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n\n❌ Kritik hata oluştu: {str(e)}")
        print("🔧 Lütfen .env dosyasını ve API ayarlarını kontrol edin.")
    finally:
        print("\n" + "=" * 60)
        print("🏁 Test uygulaması sonlandırıldı.")
        print("=" * 60)
