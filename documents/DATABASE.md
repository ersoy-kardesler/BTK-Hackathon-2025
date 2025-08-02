# BTK Hackathon 2025 - MariaDB ve Kimlik Doğrulama Entegrasyonu

Bu doküman, projeye eklenen MariaDB bağlantısı, kullanıcı kimlik doğrulama sistemi ve veritabanı yapısı hakkında bilgi verir.

## 🗄️ Veritabanı Yapısı

### Tablolar

1. **users** - Kullanıcı bilgileri
   - id, username, email, password_hash
   - full_name, role (student/teacher/admin)
   - is_active, created_at, updated_at, last_login

2. **user_sessions** - Oturum yönetimi
   - session_token, user_id, expires_at
   - ip_address, user_agent

3. **education_contents** - Eğitim içerikleri
   - user_id, subject, content
   - generated_at, is_favorite

4. **assignment_evaluations** - Ödev değerlendirmeleri
   - user_id, assignment_text, criteria
   - evaluation_result, score, evaluated_at

5. **user_activity_logs** - Kullanıcı aktivite logları
6. **password_reset_tokens** - Şifre sıfırlama tokenları
7. **api_keys** - API anahtarları
   - user_id, key_name, api_key_encrypted
   - is_active, created_at, last_used

8. **user_settings** - Kullanıcı ayarları
   - user_id, gemini_api_key, gemini_model
   - dark_mode, created_at, updated_at

### SQL Dosyası

```sql
-- Veritabanı şemasını oluşturmak için:
mysql -u root -p btk_hackathon_2025 < database_schema.sql
```

## 🔧 Kurulum

### 1. Gerekli Paketleri Yükleyin

```bash
pip install -r requirements.txt
```

Yeni eklenen paketler:
- `mysql-connector-python==8.2.0` - MariaDB/MySQL bağlantısı
- `bcrypt==4.1.2` - Şifre hash'leme
- `cryptography==45.0.5` - Şifreleme ve güvenlik

### 2. Çevre Değişkenlerini Ayarlayın

`.env.example` dosyasını `.env` olarak kopyalayın ve değerlerinizi girin:

```bash
cp .env.example .env
```

`.env` dosyası içeriği:
```env
# Google Gemini AI API Anahtarı
GEMINI_API_KEY=your_gemini_api_key_here

# MariaDB/MySQL Veritabanı Ayarları
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_database_password
DB_NAME=btk_hackathon_2025

# Flask Güvenlik Anahtarı (isteğe bağlı)
SECRET_KEY=your_secret_key_here

# Varsayılan Gemini Modeli
GEMINI_MODEL=gemini-2.5-flash

# Güvenlik Ayarları
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
PERMANENT_SESSION_LIFETIME=3600
```

### 3. MariaDB Veritabanını Hazırlayın

```sql
-- MariaDB'ye giriş yapın
mysql -u root -p

-- Veritabanını oluşturun
CREATE DATABASE btk_hackathon_2025 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Kullanıcı oluşturun (isteğe bağlı)
CREATE USER 'btk_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON btk_hackathon_2025.* TO 'btk_user'@'localhost';
FLUSH PRIVILEGES;

-- Çıkış yapın
exit;
```

### 4. Veritabanı Şemasını Yükleyin

```bash
mysql -u root -p btk_hackathon_2025 < database_schema.sql
```

### 5. Uygulamayı Başlatın

```bash
python app.py
```

## 🔐 Kimlik Doğrulama Sistemi

### Özellikler

- **Güvenli şifre hash'leme** (bcrypt)
- **Oturum yönetimi** (session tokens)
- **Rol tabanlı erişim kontrolü** (student/teacher/admin)
- **API anahtarı desteği**
- **Şifre değiştirme**
- **Kullanıcı kayıt sistemi**

### API Endpoint'leri

#### Kimlik Doğrulama
- `POST /auth/login` - Kullanıcı girişi
- `POST /auth/logout` - Kullanıcı çıkışı
- `POST /auth/register` - Kullanıcı kaydı
- `GET /auth/profile` - Kullanıcı profili
- `POST /auth/change-password` - Şifre değiştirme
- `GET /auth/check-session` - Oturum kontrolü

#### Kullanıcı Verileri
- `GET /api/user/education-history` - Eğitim geçmişi
- `GET /api/user/assignment-history` - Ödev geçmişi
- `GET /api/user/dashboard-stats` - Dashboard istatistikleri
- `POST /api/user/toggle-favorite` - Favori eğitimleri

#### Admin (Sadece admin rolü)
- `GET /api/user/admin/users` - Tüm kullanıcıları listele

### Sayfalar

- `/login` - Giriş sayfası
- `/register` - Kayıt sayfası
- `/` - Ana sayfa (isteğe bağlı kimlik doğrulama)
- `/education` - Eğitim oluşturma (giriş gerekli)
- `/assignment_evaluate` - Ödev değerlendirme (giriş gerekli)

## 🛡️ Güvenlik

### Implemented Features

1. **Şifre Güvenliği**
   - bcrypt ile hash'leme
   - Minimum 6 karakter
   - Güçlü şifre kontrolü (frontend)

2. **Oturum Güvenliği**
   - Güvenli token oluşturma
   - Otomatik süre dolumu (24 saat)
   - IP ve User Agent tracking

3. **SQL Injection Koruması**
   - Parameterized queries
   - Input validation

4. **Role-based Access Control**
   - Decorator'lar ile kolay implementasyon
   - Granular yetki kontrolü

### Test Kullanıcıları

Schema yüklendiğinde otomatik oluşturulan test kullanıcıları (şifre: `test123`):

- **admin@example.com** - Admin kullanıcı
- **teacher@example.com** - Öğretmen kullanıcı  
- **student@example.com** - Öğrenci kullanıcı

## 📝 Kullanım Örnekleri

### Backend Dekoratörler

```python
from auth.flask_auth import login_required, role_required

# Giriş gerekli
@app.route('/protected')
@login_required
def protected_route():
    return f"Merhaba {g.current_user['username']}"

# Sadece admin
@app.route('/admin')
@login_required
@role_required('admin')
def admin_route():
    return "Admin sayfası"

# Öğretmen veya admin
@app.route('/teacher')
@login_required
@role_required('teacher', 'admin')
def teacher_route():
    return "Öğretmen sayfası"
```

### Frontend API Çağrıları

```javascript
// Giriş yapma
const response = await fetch('/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'admin',
        password: 'test123'
    })
});

// Session token ile API çağrısı
const educationResponse = await fetch('/api/education', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${sessionToken}`
    },
    body: JSON.stringify({
        subject: 'Python Programlama'
    })
});
```

### Veritabanı İşlemleri

```python
from database.db_connection import get_db

db = get_db()

# Kullanıcının eğitimlerini getir
educations = db.execute_query("""
    SELECT * FROM education_contents 
    WHERE user_id = %s 
    ORDER BY generated_at DESC
""", (user_id,))

# Yeni eğitim kaydet
education_id = db.execute_insert("""
    INSERT INTO education_contents (user_id, subject, content)
    VALUES (%s, %s, %s)
""", (user_id, subject, content))
```

## 🔍 Sorun Giderme

### Veritabanı Bağlantı Sorunları

1. MariaDB servisinin çalıştığından emin olun:
```bash
sudo systemctl status mariadb
```

2. `.env` dosyasındaki veritabanı ayarlarını kontrol edin

3. Veritabanı kullanıcısının yetkileri olduğundan emin olun

### Kimlik Doğrulama Sorunları

1. Session süresi dolmuş olabilir (24 saat)
2. Tarayıcı cookie'lerini temizleyin
3. Veritabanında `user_sessions` tablosunu kontrol edin

### Log Kontrolü

Uygulama loglarını kontrol etmek için:
```bash
# Uygulama çalışırken console'da loglar görünür
python app.py
```

## 📚 Dosya Yapısı

```
BTK-Hackathon-2025/
├── database/
│   └── db_connection.py       # Veritabanı bağlantı modülü
├── auth/
│   ├── auth_manager.py        # Kimlik doğrulama yöneticisi
│   ├── flask_auth.py          # Flask dekoratörleri
│   └── routes.py              # Auth route'ları
├── api/
│   └── user_api.py            # Kullanıcı veri API'leri
├── templates/
│   ├── login.html             # Giriş sayfası
│   └── register.html          # Kayıt sayfası
├── database_schema.sql        # Veritabanı şeması
├── .env.example               # Örnek çevre değişkenleri
└── requirements.txt           # Güncellenmiş bağımlılıklar
```

## ⚠️ Önemli Notlar

1. Production ortamında `DEBUG=False` olarak ayarlayın
2. HTTPS kullanırken `SESSION_COOKIE_SECURE=True` yapın
3. Güçlü `SECRET_KEY` kullanın
4. Düzenli olarak veritabanı backup'ı alın
5. Log dosyalarını düzenli olarak temizleyin
