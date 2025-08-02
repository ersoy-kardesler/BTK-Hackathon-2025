"""
BTK Hackathon 2025 - Eğitim Oluşturma Sınama Uygulaması

Telif Hakkı © 2025 Ersoy Kardeşler
Bütün hakları saklıdır.

Bu dosya, eğitim oluşturma işlevini sınar.

Kullanım:
    python test_generating_education.py

Gereksinimler:
- Ortam değişkenlerinde GEMINI_API_KEY tanımlı olmalı
- app.py ile aynı dizinde bulunmalı
- Internet bağlantısı (API çağrıları için)

Yazarlar: Ersoy Kardeşler
"""


# Gerekli kütüphanelerin içe aktarılması
import os
import google.generativeai as genai

from dotenv import load_dotenv
from education.generate_education import generate_education


# Gemini modellerinden birini döndüren fonksiyon
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


# generate_all fonksiyonunun sınayan fonksiyon
def test_generate_all():
    """
    generate_all fonksiyonunu sınar ve sonuçları konsola yazdırır.
    """

    # Başlığı yaz
    print("Eğitim Oluşturma Sınaması Başlatılıyor...")
    print("=" * 60)

    # Modeli al
    model = get_gemini_model()

    # Çeşitli yapılandırmalar
    subject = "Bilgisayar Mühendisliği"
    duration = "14 hafta"
    lesson_duration = 60
    question_count = 10

    # generate_all fonksiyonunu çağır
    response = generate_education(subject,
                                  duration,
                                  lesson_duration,
                                  question_count,
                                  model=model)

    # Sınama sonucunu dosyaya yaz
    with open("test/result_education.txt", "w", encoding="utf-8") as f:
        f.write(response)

    # Sınama sonucunu döndür
    return response


# Uygulamayı çalıştır
if __name__ == "__main__":
    """
    Ana sınama fonksiyonu. Tüm sınamaları çalıştırır ve
    sonuçları konsola yazdırır.
    """

    # Başlığı yaz
    print("BTK Hackathon 2025 - Eğitim Oluşturma Sınaması")
    print("=" * 60)
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
