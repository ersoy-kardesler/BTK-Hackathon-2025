"""
BTK Hackathon 2025 - Ödev Değerlendirme Sınama Uygulaması

Telif Hakkı © 2025 Ersoy Kardeşler
Bütün hakları saklıdır.

Bu dosya, ödev değerlendirme işlevini sınar.

Kullanım:
    python test_evaluate_assignment.py

Gereksinimler:
- config.ini dosyasında GEMINI_API_KEY tanımlı olmalı
- app.py ile aynı dizinde bulunmalı
- Internet bağlantısı (API çağrıları için)
- MariaDB veritabanı bağlantısı

Yazarlar: Ersoy Kardeşler
"""

# Gerekli kütüphanelerin içe aktarılması
import google.generativeai as genai

from config.config_loader import load_config
from database.database_connection import get_system_config, init_database
from education.evaluate_assignment import evaluate_assignment


# Gemini modellerinden birini döndüren fonksiyon
def get_gemini_model():
    """
    Google Gemini API modelini yapılandırır ve döndürür.
    """
    # Veritabanını başlat
    if not init_database():
        print("HATA: Veritabanı bağlantısı kurulamadı!")
        return None

    # Konfigürasyonu yükle
    config = load_config()

    # Test için Gemini API anahtarını elle girin
    api_key = input("Lütfen Gemini API anahtarınızı girin: ").strip()
    if not api_key:
        raise RuntimeError("Gemini API anahtarı girilmedi!")
    genai.configure(api_key=api_key)

    # Modeli döndür
    gemini_model = config.get("GEMINI_MODEL", "gemini-2.5-flash")
    return genai.GenerativeModel(gemini_model)


# generate_all fonksiyonunun sınayan fonksiyon
def test_generate_all():
    """
    generate_all fonksiyonunu sınar ve sonuçları konsola yazdırır.
    """

    # Başlığı yaz
    print("Ödev Değerlendirme Sınaması Başlatılıyor...")
    print("=" * 60)

    # Modeli al
    model = get_gemini_model()

    # Çeşitli yapılandırmalar
    assignment_text = """
    1. Soru: Yazılım ve donanım arasındaki fark nedir?

Cevap:

    Yazılım, bilgisayarda çalışan programlardır
    (örneğin işletim sistemi, uygulamalar).

    Donanım ise bilgisayarın fiziksel parçalarıdır
    (örneğin CPU, RAM, sabit disk).

2. Soru: Algoritma nedir?

Cevap:
Algoritma, bir problemi çözmek veya belirli bir görevi yerine getirmek için
izlenen adımların mantıksal sıralamasıdır.
3. Soru: İşletim sistemi ne işe yarar?

Cevap:
İşletim sistemi, donanım ile yazılım arasında köprü kurar. Bellek yönetimi,
dosya sistemi, işlem yönetimi gibi işleri kontrol eder.
Örnek: Windows, Linux, macOS.
4. Soru: Nesne yönelimli programlama (OOP) nedir?

Cevap:
OOP, veriyi ve o veri üzerinde çalışan fonksiyonları bir araya getiren
bir programlama yaklaşımıdır. Temel kavramları: sınıf (class),
nesne (object), kalıtım (inheritance), kapsülleme (encapsulation),
çok biçimlilik (polymorphism).
5. Soru: Veri tabanı nedir? Ne için kullanılır?

Cevap:
Veri tabanı, verilerin organize bir şekilde saklandığı sistemdir.
Verilere kolay erişim, güncelleme ve yönetim sağlar.
Örnek: MySQL, PostgreSQL, MongoDB.
6. Soru: CPU’nun temel görevleri nelerdir?

Cevap:
CPU (Merkezi İşlem Birimi), bilgisayardaki komutları işler.
Temel görevleri: veri işleme, hesaplama, kontrol ve veri taşıma.
7. Soru: Compiler (derleyici) ile interpreter (yorumlayıcı)
arasındaki fark nedir?

Cevap:

    Compiler, tüm kodu tek seferde makine diline çevirir
    (örnek: C, C++)

    Interpreter, kodu satır satır çalıştırır
    (örnek: Python, JavaScript)

8. Soru: IP adresi nedir?

Cevap:
IP adresi, internet üzerindeki her cihazın kimliğidir.
Cihazların birbirine veri göndermesini sağlar.
IPv4 örneği: 192.168.1.1
9. Soru: Yazılım geliştirme yaşam döngüsü (SDLC) nedir?

Cevap:
SDLC, yazılım geliştirme sürecini adımlara ayıran bir modeldir.
Adımlar: Gereksinim analizi, tasarım, geliştirme, test,
dağıtım ve bakım.
10. Soru: Bilgisayar ağları (networking) nedir?

Cevap:
Bilgisayar ağları, birden fazla bilgisayarın veri paylaşımı amacıyla
birbirine bağlanmasıdır. Örnek: LAN (yerel ağ), WAN (geniş alan ağı),
İnternet.

    """
    criteria = "Genel değerlendirme kriterleri"

    # generate_all fonksiyonunu çağır
    response = evaluate_assignment(assignment_text, criteria, model)

    # Sınama sonucunu dosyaya yaz
    with open("test/result_assignment.txt", "w", encoding="utf-8") as f:
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
    print("BTK Hackathon 2025 - Ödev Değerlendirme Sınaması")
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
        print("=" * 60)
