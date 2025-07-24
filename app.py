"""
BTK Hackathon 2025 - Eğitim Asistanı Uygulaması

Bu uygulama, Google Gemini AI kullanarak eğitim içeriği oluşturan bir Flask web uygulamasıdır.
Özellikler:
- Müfredat oluşturma
- Ders planı hazırlama
- Quiz soruları üretme
- Ödev değerlendirme

Gereksinimler:
- Python 3.8+
- Flask
- google-generativeai
- python-dotenv

Kullanım:
1. .env dosyasında GEMINI_API_KEY tanımlayın
2. requirements.txt'deki paketleri yükleyin
3. python app.py ile uygulamayı başlatın

Yazarlar: Ersoy Kardeşler
Tarih: Temmuz 2025
"""

from flask import Flask, render_template
import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env dosyasından çevre değişkenlerini yükle
# Bu dosya API anahtarları ve diğer gizli bilgileri içerir
load_dotenv()

# Flask uygulamasını başlat
# __name__ parametresi Flask'a uygulama dosyasının konumunu söyler
app = Flask(__name__)
# Güvenlik için secret key ayarla (session yönetimi için gerekli)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')

# Google Gemini API'yi yapılandır
# Çevre değişkeninden API anahtarını al
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY çevre değişkeni bulunamadı!")
    print("Lütfen .env dosyasında GEMINI_API_KEY=your_api_key_here şeklinde tanımlayın")
    exit(1)

# Gemini AI modelini yapılandır ve başlat
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')  # En güncel Gemini modelini kullan
print("✅ Google Gemini API başarıyla bağlandı!")

def generate_curriculum(subject, level="başlangıç", duration="1 ay"):
    """
    Belirtilen konuda eğitim müfredatı oluşturur.
    
    Bu fonksiyon Google Gemini AI kullanarak kapsamlı bir eğitim müfredatı hazırlar.
    Müfredat, hedefler, haftalık konular, projeler ve değerlendirme kriterlerini içerir.
    
    Args:
        subject (str): Eğitim konusu (örn: "Python Programlama", "Web Geliştirme")
        level (str, optional): Eğitim seviyesi. Varsayılan "başlangıç".
                              Seçenekler: "başlangıç", "orta", "ileri"
        duration (str, optional): Eğitim süresi. Varsayılan "1 ay".
                                 Örnek formatlar: "2 hafta", "3 ay", "6 ay"
        
    Returns:
        str: Detaylı müfredat metni. Başarısızlık durumunda hata mesajı döner.
        
    Example:
        >>> curriculum = generate_curriculum("JavaScript", "orta", "2 ay")
        >>> print(curriculum[:100])
        'JavaScript Eğitimi - Orta Seviye\n\n1. Eğitim Hedefleri...'
        
    Note:
        - Internet bağlantısı gereklidir (Gemini API çağrısı için)
        - API limitlerini göz önünde bulundurarak kullanın
    """
    # Detaylı prompt hazırla - Türkçe eğitim içeriği için optimize edilmiş
    prompt = f"""
    Bilgisayar alanında "{subject}" konusunda {level} seviyesinde {duration} süresinde 
    bir eğitim müfredatı oluştur. Müfredat şu şekilde olmalı:

    1. Eğitim Hedefleri (Somut ve ölçülebilir hedefler)
    2. Haftalık Konular ve Alt Başlıklar (Kronolojik sıralama)
    3. Pratik Projeler (Uygulamalı öğrenme için)
    4. Değerlendirme Kriterleri (Objektif ölçüm yöntemleri)
    5. Kaynaklar (Kitap, video, online platform önerileri)

    Türkçe olarak, detaylı ve uygulanabilir bir müfredat hazırla.
    Her hafta için en az 3 alt konu belirle.
    """
    
    try:
        # Gemini API çağrısı yap
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Hata durumunda kullanıcı dostu mesaj döndür
        print(f"❌ Müfredat oluşturma hatası: {str(e)}")
        return f"Müfredat oluşturulurken hata oluştu: {str(e)}"

def generate_lesson_plan(topic, duration_minutes=60):
    """
    Belirtilen konu için detaylı ders planı oluşturur.
    
    Bu fonksiyon Google Gemini AI kullanarak eğitim amaçlı ders planı hazırlar.
    Plan, giriş, ana içerik, pratik uygulamalar ve değerlendirme bölümlerini içerir.
    
    Args:
        topic (str): Ders konusu (örn: "Python Değişkenleri", "HTML Temelleri")
        duration_minutes (int, optional): Ders süresi dakika cinsinden. 
                                        Varsayılan 60 dakika.
                                        Önerilen aralık: 30-180 dakika
        
    Returns:
        str: Detaylı ders planı metni. Başarısızlık durumunda hata mesajı döner.
        
    Example:
        >>> plan = generate_lesson_plan("Python Fonksiyonları", 90)
        >>> print("Ders Planı:" in plan)
        True
        
    Note:
        - Süre 30 dakikadan az ise uyarı mesajı eklenir
        - Plan, belirtilen süreye uygun şekilde bölümlendirilir
    """
    # Süre kontrolü ve uyarı
    if duration_minutes < 30:
        print("⚠️  Uyarı: 30 dakikadan kısa dersler için detaylı plan oluşturmak zor olabilir.")
    
    # Süreye göre özelleştirilmiş prompt
    prompt = f"""
    "{topic}" konusunda {duration_minutes} dakikalık bir ders planı oluştur.
    Ders planı şu bölümleri içermelidir:

    1. Ders Hedefleri (Öğrenci neler öğrenecek?)
    2. Giriş (5-10 dakika) - Konuya motivasyon ve ön bilgi kontrolü
    3. Ana İçerik (toplam sürenin %60-70'i) - Konunun detaylı açıklanması
    4. Pratik Uygulamalar (toplam sürenin %20-30'u) - Hands-on aktiviteler
    5. Değerlendirme ve Kapanış (5-10 dakika) - Öğrenilenlerin pekiştirilmesi
    6. Ödev/Öneriler - Ders sonrası çalışma önerileri

    Her bölüm için tahmini süre belirt.
    Türkçe olarak, eğitici ve anlaşılır bir ders planı hazırla.
    Interaktif öğeler ve öğrenci katılımını artıracak yöntemler öner.
    """
    
    try:
        # Gemini API çağrısı yap
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Hata durumunda detaylı log ve kullanıcı dostu mesaj
        print(f"❌ Ders planı oluşturma hatası: {str(e)}")
        return f"Ders planı oluşturulurken hata oluştu: {str(e)}"

def generate_quiz(topic, question_count=10):
    """
    Belirtilen konu için çoktan seçmeli quiz soruları oluşturur.
    
    Bu fonksiyon Google Gemini AI kullanarak eğitim amaçlı quiz soruları hazırlar.
    Her soru 4 seçenekli, doğru cevap belirtilen ve açıklamalı olarak üretilir.
    
    Args:
        topic (str): Quiz konusu (örn: "Python Listeleri", "CSS Selectors")
        question_count (int, optional): Oluşturulacak soru sayısı. 
                                       Varsayılan 10 soru.
                                       Önerilen aralık: 5-20 soru
        
    Returns:
        str: Formatlı quiz soruları metni. Başarısızlık durumunda hata mesajı döner.
        
    Example:
        >>> quiz = generate_quiz("JavaScript Değişkenleri", 5)
        >>> "Soru 1:" in quiz
        True
        
    Note:
        - Sorular kolay, orta ve zor seviyede karma olarak hazırlanır
        - Her soru için detaylı açıklama eklenir
        - Maksimum 25 soru önerilir (API limitleri nedeniyle)
    """
    # Soru sayısı kontrolü ve optimizasyon
    if question_count > 25:
        print("⚠️  Uyarı: 25'ten fazla soru API limitlerini aşabilir. 25 soru ile sınırlandırılıyor.")
        question_count = 25
    elif question_count < 3:
        print("⚠️  Uyarı: En az 3 soru önerilir. 3 soru olarak ayarlandı.")
        question_count = 3
    
    # Detaylı ve yapılandırılmış prompt
    prompt = f"""
    "{topic}" konusunda {question_count} adet çoktan seçmeli quiz sorusu oluştur.
    
    Her soru için MUTLAKA şu format kullanılmalı:
    
    Soru X: [Soru metni buraya]
    A) [Seçenek A]
    B) [Seçenek B] 
    C) [Seçenek C]
    D) [Seçenek D]
    
    Doğru Cevap: [A/B/C/D]
    Açıklama: [Neden bu cevap doğru, diğerleri neden yanlış]
    
    ---
    
    Sorular şu kriterlere uymalı:
    - %40 kolay seviye (temel kavramlar)
    - %40 orta seviye (uygulama)
    - %20 zor seviye (analiz/sentez)
    - Türkçe ve anlaşılır dil
    - Gerçekçi senaryolar içeren sorular
    - Tuzak seçenekler ekleyerek zorluğu artır
    
    Düzenli formatı koruyarak hazırla.
    """
    
    try:
        # Gemini API çağrısı yap
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Hata durumunda detaylı log ve kullanıcı dostu mesaj
        print(f"❌ Quiz oluşturma hatası: {str(e)}")
        return f"Quiz soruları oluşturulurken hata oluştu: {str(e)}"

def evaluate_assignment(assignment_text, criteria="Genel değerlendirme kriterleri"):
    """
    Öğrenci ödevini detaylı şekilde değerlendirir ve geri bildirim sağlar.
    
    Bu fonksiyon Google Gemini AI kullanarak öğrenci ödevlerini objektif kriterlerle
    değerlendirir ve yapıcı geri bildirim sağlar. Eğitim amaçlı puanlama yapar.
    
    Args:
        assignment_text (str): Değerlendirilecek ödev metni. 
                              Kod, yazı veya karma içerik olabilir.
        criteria (str, optional): Değerlendirme kriterleri. 
                                 Varsayılan "Genel değerlendirme kriterleri".
                                 Örnek: "Python kod kalitesi ve algoritma mantığı"
        
    Returns:
        str: Detaylı değerlendirme raporu. Başarısızlık durumunda hata mesajı döner.
        
    Example:
        >>> code = "x = 5\\nprint(x * 2)"
        >>> evaluation = evaluate_assignment(code, "Python temel kodlama")
        >>> "Puan:" in evaluation
        True
        
    Note:
        - Değerlendirme 100 üzerinden puanlama yapar
        - Yapıcı ve eğitici geri bildirim sağlar
        - Hem güçlü yönleri hem de gelişim alanlarını belirtir
    """
    # Ödev içeriği kontrolü
    if not assignment_text.strip():
        return "❌ Hata: Ödev metni boş olamaz. Lütfen değerlendirilecek içeriği girin."
    
    if len(assignment_text) < 10:
        print("⚠️  Uyarı: Çok kısa ödev metni. Detaylı değerlendirme için daha uzun içerik önerilir.")
    
    # Eğitim odaklı, yapıcı değerlendirme promptu
    prompt = f"""
    Aşağıdaki öğrenci ödevini eğitici ve yapıcı bir şekilde değerlendir:

    === ÖDEV İÇERİĞİ ===
    {assignment_text}

    === DEĞERLENDİRME KRİTERLERİ ===
    {criteria}

    === DEĞERLENDİRME RAPORU ===
    Lütfen aşağıdaki format kullanarak detaylı değerlendirme yap:

    🎯 GENEL DEĞERLENDİRME
    Puan: [X]/100
    Genel Görüş: [Kısa özet değerlendirme]

    ✅ GÜÇLÜ YÖNLER
    - [Başarılı olan noktalar]
    - [Doğru yaklaşımlar]
    - [İyi uygulamalar]

    📈 GELİŞTİRİLEBİLİR ALANLAR
    - [Eksik olan noktalar]
    - [Hatalı yaklaşımlar]
    - [İyileştirilebilir alanlar]

    💡 ÖNERİLER VE REHBERLIK
    - [Somut iyileştirme önerileri]
    - [Alternatif yaklaşımlar]
    - [Ek kaynak önerileri]

    📝 DETAYLI GERİ BİLDİRİM
    [Satır satır veya bölüm bölüm detaylı analiz]

    🎯 SONUÇ VE ÖZET
    [Öğrencinin gelişimi için somut adımlar]

    Değerlendirme Türkçe, eğitici, yapıcı ve motive edici olmalı.
    Öğrencinin moralini bozmadan gelişim alanlarını belirt.
    """
    
    try:
        # Gemini API çağrısı yap
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Hata durumunda detaylı log ve kullanıcı dostu mesaj
        print(f"❌ Ödev değerlendirme hatası: {str(e)}")
        return f"Ödev değerlendirilirken hata oluştu: {str(e)}"

# Ana sayfaya (/) gelen istekleri karşıla
@app.route("/")
def index():
    """
    Ana sayfa route'u - Uygulamanın giriş sayfasını görüntüler.
    
    Bu route Flask uygulamasının ana sayfasını render eder.
    Kullanıcılar buradan eğitim asistanı özelliklerine erişebilir.
    
    Returns:
        str: Render edilmiş HTML sayfası (templates/index.html)
        
    Note:
        - GET metoduyla erişilebilir
        - templates/index.html dosyası mevcut olmalıdır
        - Static dosyalar (CSS, JS) otomatik olarak yüklenir
    """
    return render_template("index.html")


# Uygulamayı çalıştır
if __name__ == "__main__":
    """
    Uygulama ana giriş noktası.
    
    Bu blok sadece dosya doğrudan çalıştırıldığında (python app.py) 
    çalışır. Import edildiğinde çalışmaz.
    
    Geliştirme modunda (debug=True) çalıştırılır:
    - Kod değişikliklerinde otomatik yeniden başlatma
    - Detaylı hata mesajları
    - Hot reload özelliği
    
    Production ortamında debug=False olmalıdır.
    """
    print("🚀 BTK Hackathon 2025 - Ersoy Kardeşler")
    print("📱 Uygulama URL: http://127.0.0.1:5000")
    print("🛑 Durdurmak için Ctrl+C tuşlayın")
    
    # Flask development server'ı başlat
    app.run(
        debug=True,     # Geliştirme modu - production'da False olmalı
        host='127.0.0.1',  # Sadece localhost'tan erişim
        port=5000       # Default Flask portu
    )
