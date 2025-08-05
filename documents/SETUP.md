# BTK Hackathon 2025 - Kurulum Rehberi

Bu belge, yazılımın nasıl kurulacağını adım adım açıklamaktadır.

## Gereksinimler

- Python 3.10 veya üzeri
- MariaDB veri tabanı sunucusu
- `pip` ve `virtualenv` yüklü olmalıdır

## MariaDB Kurulumu

1. **MariaDB'yi Yükleyin**

   - Debian/Ubuntu tabanlı sistemler için:
     ```bash
     sudo apt update
     sudo apt install mariadb-server
     ```

   - Red Hat/CentOS tabanlı sistemler için:
     ```bash
     sudo yum install mariadb-server
     ```

2. **MariaDB Servisini Başlatın**

   ```bash
   sudo systemctl start mariadb
   sudo systemctl enable mariadb
   ```

3. **MariaDB Güvenlik Ayarlarını Yapılandırın**

   ```bash
   sudo mysql_secure_installation
   ```
   - Yönetici kullanıcı (root) parolası belirleyin.
   - Varsayılan ayarları takip edin (örneğin, anonim kullanıcıları kaldırın, sınama veri tabanını silin).

# Kurulum Adımları

1. **Depoyu Alın**

   ```bash
   git clone https://github.com/ersoy-kardesler/BTK-Hackathon-2025.git
   cd BTK-Hackathon-2025
   ```

   > **Not:** Eğer Windows kullanıyorsanız, komutları Git Bash veya PowerShell üzerinden çalıştırabilirsiniz.

2. **Sanal Ortam Oluşturun ve Aktif Edin**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   - **Windows için:**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```

3. **Bağımlılıkları Yükleyin**

   ```bash
   pip install -r requirements.txt
   ```

5. **Yapılandırmayı Düzenleyin**

   - Yapılandırma dosyasını oluşturun:
     ```bash
     cp config/config.ini.example config/config.ini
     ```
   - `config/config.ini` dosyasını düzenleyin:
     ```bash
     nano config/config.ini
     ```
   - Yapılandırma dosyanızı seçeneklerinize göre düzenleyin.

   - **Önemli Yapılandırma Notları:**
     - `DB_PASSWORD`: MariaDB yönetici kullanıcısı (root) parolanızı veya oluşturduğunuz kullanıcının parolasını girin
     - `SECRET_KEY`: Güçlü bir gizli anahtar oluşturun:
       ```bash
       python -c "import secrets; print(secrets.token_hex(32))"
       ```
     - Güvenlik için ayrı veri tabanı kullanıcısı oluşturmanız önerilir
     - Production ortamında `DEBUG = False` olarak bırakın

6. **Uygulamayı Çalıştırın**

   ```bash
   python3 app.py
   ```

   - **Windows için:**
     ```powershell
     python app.py
     ```

7. **Tarayıcıda Açın**

   - Uygulama varsayılan olarak `http://127.0.0.1:5000` adresinde çalışacaktır.
   - Yapılandırmayı değiştirdiyseniz farklı adres ve port bilgilerinde çalışabilir.

---

# Kurulumun Doğrulanması

Kurulumdan sonra aşağıdaki adımları izleyerek uygulamanın doğru çalıştığını sınayabilirisiniz:

1. Web tarayıcınızda uygulamanın HTTP adresine gidin ve ana sayfanın açıldığını doğrulayın.
2. Hatalarla karşılaşırsanız terminaldeki hata iletilerini inceleyin.
3. Gerekirse `config/config.ini` ve veri tabanı ayarlarını tekrar kontrol edin.

---

# Ek Notlar ve Öneriler

- Geliştirme ortamında çalışıyorsanız `DEBUG = True` bırakabilirsiniz, canlı ortamda mutlaka `False` yapın.
- MariaDB yerine MySQL de kullanılabilir, ancak şema ve bağlantı ayarlarını denetleyin.
- Güvenlik için yönetici kullanıcı (root) kullanıcısı yerine ayrı bir veri tabanı kullanıcısı oluşturmanız önerilir.
