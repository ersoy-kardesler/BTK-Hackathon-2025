"""
BTK Hackathon 2025 - Google Gemini API Sınama Uygulaması

Bu dosya, müfredat oluşturmayı sınar.

Kullanım:
    python test_generating_curriculum.py

Gereksinimler:
- .env dosyasında GEMINI_API_KEY tanımlı olmalı
- app.py ile aynı dizinde bulunmalı
- Internet bağlantısı (API çağrıları için)

Yazarlar: Ersoy Kardeşler
Tarih: Temmuz 2025
"""

# Gerekli kütüphanelerin içe aktarılması
import os
import google.generativeai as genai

from generate_curriculum import generate_curriculum
from dotenv import load_dotenv


def get_gemini_model():
    """
    Google Gemini API modelini yapılandırır ve döndürür.
    """
    # .env dosyasını yükle
    load_dotenv()

    # API anahtarını al
    api_key = os.getenv("GEMINI_API_KEY")

    # Eğer API anahtarı yoksa
    if not api_key:
        # Hata fırlat
        raise RuntimeError("GEMINI_API_KEY .env dosyasında tanımlı olmalı!")

    # API anahtarını yapılandır
    genai.configure(api_key=api_key)

    # Modeli döndür
    return genai.GenerativeModel("gemini-2.5-flash")


def test_generate_all():
    """
    generate_all fonksiyonunu sınar ve sonuçları konsola yazdırır.
    """

    # Başlığı yaz
    print("Müfredat Oluşturma Sınaması Başlatılıyor...")
    print("=" * 70)

    # Modeli al
    model = get_gemini_model()

    # Çeşitli yapılandırmalar
    subject = "Bilgisayar Mühendisliği"
    duration = "14 hafta"
    lesson_duration = 60
    question_count = 10

    # generate_all fonksiyonunu çağır
    return generate_curriculum(subject,
                               duration,
                               lesson_duration,
                               question_count,
                               model=model)


# Uygulamayı çalıştır
if __name__ == "__main__":
    """
    Ana sınama fonksiyonu. Tüm sınamaları çalıştırır ve
    sonuçları konsola yazdırır.
    """

    # Başlığı yaz
    print("BTK Hackathon 2025 - Müfredat Oluşturma Sınaması (Tüm İçerikler)")
    print("=" * 60)
    print("Sınama Tarihi:", "26 Temmuz 2025")
    print("Geliştirici: Ersoy Kardeşler")
    print("=" * 60)
    try:
        # Sınama fonksiyonunu çalıştır ve çıktısını yazdır
        print(test_generate_all())
    except KeyboardInterrupt:
        # Kullanıcı durdurma iletisini yaz
        print("\n\nSınama kullanıcı tarafından durduruldu.")
    except Exception as e:
        # Hata iletisini yaz
        print(f"\n\nKritik hata oluştu: {str(e)}")
        print("Lütfen .env dosyasını ve API ayarlarını kontrol edin.")
    finally:
        # Son iletiyi yaz
        print("\n" + "=" * 60)
        print("Sınama uygulaması sonlandırıldı.")
        print("=" * 60)
