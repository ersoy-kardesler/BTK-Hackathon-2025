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

## Kurulum Adımları

1. **Depoyu Klonlayın**

   ```bash
   git clone https://github.com/ersoy-kardesler/BTK-Hackathon-2025.git
   cd BTK-Hackathon-2025
   ```

2. **Sanal Ortam Oluşturun ve Aktif Edin**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Bağımlılıkları Yükleyin**

   ```bash
   pip install -r requirements.txt
   ```

4. **Veritabanını Ayarlayın**

   - MariaDB sunucusunu başlatın:
     ```bash
     sudo systemctl start mariadb
     ```
   - Veritabanını oluşturun ve şemayı yükleyin:
     ```bash
     mysql -u root -p < database/database_schema.sql
     ```

5. **Çevre Değişkenlerini Ayarlayın**

   - `.env.example` dosyasını kopyalayarak `.env` dosyasını oluşturun:
     ```bash
     cp .env.example .env
     ```
   - `.env` dosyasını düzenleyerek veritabanı bilgilerinizi girin.

6. **Uygulamayı Çalıştırın**

   ```bash
   python app.py
   ```

7. **Tarayıcıda Açın**

   - Uygulama varsayılan olarak `http://127.0.0.1:5000` adresinde çalışacaktır.
