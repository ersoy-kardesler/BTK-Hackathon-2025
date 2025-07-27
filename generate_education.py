"""
BTK Hackathon 2025 - Gemini API ile Müfredat Oluşturma Kaynak Kodları

Telif Hakkı © 2025 Ersoy Kardeşler
Bütün hakları saklıdır.

Bu dosya, Gemini API kullanarak müfredat oluşturmayı sınar.
"""


# Eğitimi oluşturan fonksiyon
def generate_education(subject,
                       duration="14 hafta",
                       lesson_duration=60,
                       question_count=10,
                       model=None):
    """
    Belirtilen konu için müfredat, ders planı, ders içerikleri ve
    sınav soruları oluşturur ve hepsini bir defada yazdırır.
    """

    try:
        prompt_content_of_education = f"""
Bilgisayar alanında \"{subject}\" konusunda {duration} süresinde
bir eğitim müfredatı oluştur. Müfredat şu şekilde olmalı:

1. Eğitim hedefleri (Somut ve ölçülebilir hedefler)
2. Eğitim müfredatında yer alan dersler (Temelden uzmanlığa
kadar sıralama)
3. Her ders için haftalık konular ve
alt başlıklar (Kronolojik sıralama)
4. Pratik projeler (Uygulamalı öğrenme için)
5. Değerlendirme kriterleri (Tarafsız ölçüm yöntemleri)
6. Kaynaklar (Kitap, video, çevrimiçi platform önerileri)

Ayrıca, aşağıdaki içerikleri de oluştur:

    1. Ders Hedefleri
    2. Giriş (%5)
    3. Ana İçerik (%50)
    4. Pratik Uygulamalar (%40)
    5. Değerlendirme ve Kapanış (%5)
    6. Ödev/Öneriler

Tüm içerikleri Türkçe olarak, ayrıntılı ve düzenli bir biçimde
hazırla.

Bu müfredat için her ders için haftalık olarak ders içeriklerinin
hepsini bir defada hazırla. Ders {duration} hafta sürecektir ve
her hafta {lesson_duration} dakikalık ders olacaktır.

Tüm içerikleri Türkçe olarak, ayrıntılı ve düzenli bir biçimde
hazırla.
Bu dersler için bir derse {question_count} adet soru düşüecek
şekilde [Ders Sayısı]x{question_count} adet soru hazırla.
Sorular açık uçlu ve aşağıdaki şekilde hazırlanmalıdır:

Soru: [Soru yer almaktadır.]
Yanıt: [Sorunun yanıtı yer almaktadır.]

"""

        response = model.generate_content(prompt_content_of_education).text

        return response
    except Exception as e:
        return f"Hata oluştu: {str(e)}"
