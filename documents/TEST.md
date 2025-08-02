# Proje Test Rehberi

Bu doküman, BTK Hackathon 2025 projesinin test süreçleri hakkında bilgi vermektedir.

## Testlerin Amacı

Bu projede testler, geliştirilen modüllerin doğru çalıştığını ve beklenen sonuçları verdiğini doğrulamak amacıyla hazırlanmıştır. Testler, hem birim testlerini hem de entegrasyon testlerini kapsamaktadır.

## Testlerin Çalıştırılması

Testleri çalıştırmak için aşağıdaki adımları izleyebilirsiniz:

1. Gerekli bağımlılıkların yüklü olduğundan emin olun:
   ```bash
   pip install -r requirements.txt
   ```

2. Test dosyalarını çalıştırın:
   ```bash
   python -m unittest discover -s . -p "test_*.py"
   ```

## Test Sonuçlarının Değerlendirilmesi

- Testler başarılı bir şekilde geçtiyse, tüm testler "OK" olarak işaretlenecektir.
- Eğer bir veya daha fazla test başarısız olursa, hata mesajları ve başarısız olan testlerin detayları terminalde görüntülenecektir.

## Test Kapsamı

- **Eğitim Modülü Testleri:** `test_generating_education.py` dosyasında yer alır ve eğitim materyallerinin doğru oluşturulmasını test eder.
- **Değerlendirme Modülü Testleri:** `test_evaluate_assignment.py` dosyasında yer alır ve ödev değerlendirme fonksiyonlarının doğruluğunu test eder.

Daha fazla bilgi için ilgili test dosyalarına göz atabilirsiniz.