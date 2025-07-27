def evaluate_assignment(assignment_text,
                        criteria="Genel değerlendirme kriterleri",
                        model=None):
    """
    Öğrenci ödevini detaylı şekilde değerlendirir ve geri bildirim sağlar.
    ...
    """
    if not assignment_text.strip():
        return "❌ Hata: Ödev metni boş olamaz." \
                "Lütfen değerlendirilecek içeriği girin."
    if len(assignment_text) < 10:
        return "⚠️ Uyarı: Çok kısa ödev metni." \
               "Detaylı değerlendirme için daha uzun içerik önerilir."

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
        response = model.generate_content(prompt).text
        return response
    except Exception as e:
        return f"Ödev değerlendirilirken hata oluştu: {str(e)}"
