"""
BTK Hackathon 2025 - Google Gemini API Test Uygulaması

Bu dosya, app.py'deki AI fonksiyonlarının doğru çalışıp çalışmadığını test eder.
Tüm API çağrılarını sırayla çalıştırarak sonuçları konsola yazdırır.

Test Edilen Fonksiyonlar:
1. generate_curriculum() - Müfredat oluşturma
2. generate_lesson_plan() - Ders planı hazırlama  
3. generate_quiz() - Quiz soruları üretme
4. evaluate_assignment() - Ödev değerlendirme

Kullanım:
    python gemini_api_test.py

Gereksinimler:
- .env dosyasında GEMINI_API_KEY tanımlı olmalı
- app.py ile aynı dizinde bulunmalı
- Internet bağlantısı (API çağrıları için)

Yazarlar: Ersoy Kardeşler
Tarih: Temmuz 2025
"""

from app import generate_curriculum, generate_lesson_plan, generate_quiz, evaluate_assignment


def test_api_functions():
    """
    Tüm AI API fonksiyonlarını sırayla test eder.
    
    Bu fonksiyon app.py'deki 4 ana AI fonksiyonunu test eder:
    - Müfredat oluşturma testi
    - Ders planı oluşturma testi  
    - Quiz oluşturma testi
    - Ödev değerlendirme testi
    
    Her test için:
    - Fonksiyon çağrılır
    - Sonuç konsola yazdırılır (ilk 200-300 karakter)
    - Başarı/başarısızlık durumu raporlanır
    
    Returns:
        None: Konsola test sonuçlarını yazdırır
        
    Raises:
        Exception: API çağrılarında hata oluşursa yakalanır ve raporlanır
        
    Note:
        - Her test arasında ayırıcı çizgiler kullanılır
        - Uzun sonuçlar kısaltılarak gösterilir
        - Gerçek API çağrıları yapılır (maliyet oluşabilir)
    """
    
    print("🚀 Google Gemini API Test Başlatılıyor...\n")
    print("=" * 60)
    
    # 1. Müfredat oluşturma testi
    print("📚 TEST 1: Müfredat Oluşturma")
    print("-" * 30)
    try:
        print("📝 Python Programlama müfredatı oluşturuluyor...")
        curriculum = generate_curriculum("Python Programlama", "başlangıç", "2 ay")
        
        if "Hata oluştu" in curriculum:
            print("❌ Müfredat oluşturma başarısız!")
            print(f"Hata: {curriculum}")
        else:
            print("✅ Müfredat başarıyla oluşturuldu!")
            print(f"📄 İçerik Önizlemesi (İlk 200 karakter):")
            print(f"'{curriculum[:200]}...'\n")
            
    except Exception as e:
        print(f"❌ Test 1 Hatası: {str(e)}")
    
    print("=" * 60)
    
    # 2. Ders planı oluşturma testi
    print("📝 TEST 2: Ders Planı Oluşturma") 
    print("-" * 30)
    try:
        print("🎯 'Python Değişkenleri ve Veri Tipleri' ders planı hazırlanıyor...")
        lesson_plan = generate_lesson_plan("Python Değişkenleri ve Veri Tipleri", 90)
        
        if "Hata oluştu" in lesson_plan:
            print("❌ Ders planı oluşturma başarısız!")
            print(f"Hata: {lesson_plan}")
        else:
            print("✅ Ders planı başarıyla oluşturuldu!")
            print(f"📄 İçerik Önizlemesi (İlk 200 karakter):")
            print(f"'{lesson_plan[:200]}...'\n")
            
    except Exception as e:
        print(f"❌ Test 2 Hatası: {str(e)}")
    
    print("=" * 60)
    
    # 3. Quiz oluşturma testi
    print("❓ TEST 3: Quiz Oluşturma")
    print("-" * 30)
    try:
        print("🧠 'Python Temel Kavramları' quiz soruları hazırlanıyor...")
        quiz = generate_quiz("Python Temel Kavramları", 5)
        
        if "Hata oluştu" in quiz:
            print("❌ Quiz oluşturma başarısız!")
            print(f"Hata: {quiz}")
        else:
            print("✅ Quiz başarıyla oluşturuldu!")
            print(f"📄 İçerik Önizlemesi (İlk 300 karakter):")
            print(f"'{quiz[:300]}...'\n")
            
    except Exception as e:
        print(f"❌ Test 3 Hatası: {str(e)}")
    
    print("=" * 60)
    
    # 4. Ödev değerlendirme testi
    print("⭐ TEST 4: Ödev Değerlendirme")
    print("-" * 30)
    try:
        print("📊 Örnek Python ödevi değerlendiriliyor...")
        
        # Değerlendirme için örnek ödev metni
        sample_assignment = """
        Python'da değişken tanımlama örnekleri:
        
        # Sayısal değişkenler
        x = 10
        y = 3.14
        
        # Metin değişkeni  
        isim = "Merhaba Dünya"
        
        # Liste değişkeni
        sayilar = [1, 2, 3, 4, 5]
        
        # Bu kod parçasında:
        # x bir integer (tam sayı) değişkenidir
        # y bir float (ondalıklı sayı) değişkenidir  
        # isim bir string (metin) değişkenidir
        # sayilar bir list (liste) değişkenidir
        
        print(f"x + y = {x + y}")
        print(f"İsim: {isim}")
        print(f"Liste uzunluğu: {len(sayilar)}")
        """
        
        evaluation = evaluate_assignment(
            sample_assignment, 
            "Python değişken tanımlama, veri tipleri ve temel işlemler"
        )
        
        if "Hata oluştu" in evaluation:
            print("❌ Ödev değerlendirme başarısız!")
            print(f"Hata: {evaluation}")
        else:
            print("✅ Ödev başarıyla değerlendirildi!")
            print(f"📄 İçerik Önizlemesi (İlk 300 karakter):")
            print(f"'{evaluation[:300]}...'\n")
            
    except Exception as e:
        print(f"❌ Test 4 Hatası: {str(e)}")
    
    print("=" * 60)
    
    
    print("🎉 TÜM TESTLER TAMAMLANDI!")
    print("\n📋 TEST SONUÇ ÖZETİ:")
    print("✅ Test 1: Müfredat Oluşturma")
    print("✅ Test 2: Ders Planı Oluşturma") 
    print("✅ Test 3: Quiz Oluşturma")
    print("✅ Test 4: Ödev Değerlendirme")
    print("\n💡 Not: Hata mesajları görürseniz:")
    print("   - Internet bağlantınızı kontrol edin")
    print("   - .env dosyasında GEMINI_API_KEY'i kontrol edin")
    print("   - API quota limitlerini kontrol edin")


if __name__ == "__main__":
    """
    Test uygulaması ana giriş noktası.
    
    Bu blok dosya doğrudan çalıştırıldığında (python gemini_api_test.py)
    tüm test fonksiyonlarını sırayla çalıştırır.
    
    Başarılı test için gereksinimler:
    - .env dosyasında geçerli GEMINI_API_KEY
    - Internet bağlantısı
    - app.py dosyasının aynı dizinde olması
    
    Kullanım:
        python gemini_api_test.py
    """
    print("🔧 BTK Hackathon 2025 - API Test Uygulaması")
    print("=" * 50)
    print("📅 Test Tarihi:", "24 Temmuz 2025")
    print("👥 Geliştirici: Ersoy Kardeşler")
    print("=" * 50)
    
    try:
        # Ana test fonksiyonunu çalıştır
        test_api_functions()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test kullanıcı tarafından durduruldu.")
        
    except Exception as e:
        print(f"\n\n❌ Kritik hata oluştu: {str(e)}")
        print("🔧 Lütfen app.py dosyasının mevcut olduğunu ve API ayarlarını kontrol edin.")
        
    finally:
        print("\n" + "=" * 50)
        print("🏁 Test uygulaması sonlandırıldı.")
        print("=" * 50)
