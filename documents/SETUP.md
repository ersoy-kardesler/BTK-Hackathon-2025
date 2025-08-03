# BTK Hackathon 2025 - Kurulum Rehberi

Bu doküman, yazılımın nasıl kurulacağını adım adım açıklamaktadır.

## Gereksinimler

- Python 3.10 veya üzeri
- MariaDB veritabanı sunucusu
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
   - Root şifresi belirleyin.
   - Varsayılan ayarları takip edin (örneğin, anonim kullanıcıları kaldırın, test veritabanını silin).

3. **MariaDB Güvenlik Ayarlarını Yapılandırın**

   ```bash
   sudo mysql_secure_installation
   ```
   - Root şifresi belirleyin.
   - Varsayılan ayarları takip edin (örneğin, anonim kullanıcıları kaldırın, test veritabanını silin).

## Kurulum Adımları

1. **Depoyu Klonlayın**

   ```bash
   git clone https://github.com/ersoy-kardesler/BTK-Hackathon-2025.git
   cd BTK-Hackathon-2025
   ```

   > **Not:** Eğer Windows kullanıyorsanız, komutları Git Bash veya PowerShell üzerinden çalıştırabilirsiniz.

2. **Sanal Ortam Oluşturun ve Aktif Edin**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
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

4. **Veritabanını Ayarlayın**


   - Şema dosyasını veritabanına uygulayın:
     ```bash
     mysql -u root -p btk_hackathon_2025 < database/database_schema.sql
     ```
     Eğer ayrı bir kullanıcı oluşturduysanız:
     ```bash
     mysql -u kullanıcı_adı -p btk_hackathon_2025 < database/database_schema.sql
     ```

   > Bu komut, `database/database_schema.sql` dosyasındaki veritabanı şemasını `btk_hackathon_2025` veritabanına uygular ve gerekli tabloları oluşturur. Komutu çalıştırmadan önce veritabanının oluşturulmuş olması gerekmektedir.

5. **Yapılandırmayı Düzenleyin**

   - Konfigürasyon dosyasını oluşturun:
     ```bash
     cp config/config.ini.example config/config.ini
     ```
   - `config/config.ini` dosyasını düzenleyin:
     ```bash
     nano config/config.ini
     ```
   - Aşağıdaki veritabanı ayarlarını yapılandırın:
     ```ini
     [database]
     DB_HOST = localhost
     DB_PORT = 3306
     DB_USER = root
     DB_PASSWORD = your_password_here
     DB_NAME = btk_hackathon_2025
     DB_CHARSET = utf8mb4
     DB_COLLATION = utf8mb4_unicode_ci

     [app]
     SECRET_KEY = buraya_güçlü_bir_anahtar_girin
     DEBUG = True

   - **Önemli Yapılandırma Notları:**
     - `DB_PASSWORD`: MariaDB root şifrenizi veya oluşturduğunuz kullanıcının şifresini girin
     - `SECRET_KEY`: Güçlü bir gizli anahtar oluşturun:
       ```bash
       python -c "import secrets; print(secrets.token_hex(32))"
       ```
     - Güvenlik için ayrı veritabanı kullanıcısı oluşturmanız önerilir
     - Production ortamında `DEBUG = False` olarak bırakın

6. **Uygulamayı Çalıştırın**

   ```bash
   python app.py
   ```

   - **Windows için:**
     ```powershell
     python app.py
     ```

6. **Tarayıcıda Açın**

   - Uygulama varsayılan olarak `http://127.0.0.1:5000` adresinde çalışacaktır.

---

## Kurulumun Doğrulanması

Kurulumdan sonra aşağıdaki adımları izleyerek uygulamanın doğru çalıştığını test edebilirsiniz:

1. Tarayıcınızda `http://127.0.0.1:5000` adresine gidin ve ana sayfanın açıldığını doğrulayın.
2. Hatalarla karşılaşırsanız terminaldeki hata mesajlarını inceleyin.
3. Gerekirse `config/config.ini` ve veritabanı ayarlarını tekrar kontrol edin.

---

## Ek Notlar ve Öneriler

- Geliştirme ortamında çalışıyorsanız `DEBUG = True` bırakabilirsiniz, canlı ortamda mutlaka `False` yapın.
- MariaDB yerine MySQL de kullanılabilir, ancak şema ve bağlantı ayarlarını kontrol edin.
- Güvenlik için root kullanıcısı yerine ayrı bir veritabanı kullanıcısı oluşturmanız önerilir.
