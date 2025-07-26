# Müfredatı oluşturan fonksiyon
def generate_curriculum(subject, duration="14 hafta", lesson_duration=60, question_count=10, model=None):
    """
    Belirtilen konu için müfredat, ders planı ve quiz soruları oluşturur ve hepsini bir defada yazdırır.
    """
    try:
        # Tek bir istekle tüm içerikleri oluşturma
        prompt = f"""
        Bilgisayar alanında \"{subject}\" konusunda {duration} süresinde 
        bir eğitim müfredatı oluştur. Müfredat şu şekilde olmalı:

        1. Eğitim Hedefleri (Somut ve ölçülebilir hedefler)
        2. Eğitim Müfredatında Yer Alan Dersler (Temelden Uzmanlığa kadar sıralama)
        3. Haftalık Konular ve Alt Başlıklar (Kronolojik sıralama)
        4. Pratik Projeler (Uygulamalı öğrenme için)
        5. Değerlendirme Kriterleri (Objektif ölçüm yöntemleri)
        6. Kaynaklar (Kitap, video, online platform önerileri)

        Ayrıca, aşağıdaki içerikleri de oluştur:

        - Her ders için {lesson_duration} dakikalık detaylı ders planı:
          1. Ders Hedefleri
          2. Giriş (%5)
          3. Ana İçerik (%50)
          4. Pratik Uygulamalar (%40)
          5. Değerlendirme ve Kapanış (%5)
          6. Ödev/Öneriler

        - {question_count} adet açık uçlu quiz sorusu:
          Soru formatı:
          Soru: [Soru metni buraya]
          Cevap: [Sorunun cevabı buraya]

        Tüm içerikleri Türkçe olarak, detaylı ve düzenli bir formatta hazırla.
        """
        response = model.generate_content(prompt).text
        print("\n✅ İçerikler oluşturuldu!\n")
        print(response)

    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")
