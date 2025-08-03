# BTK Hackathon 2025 - MariaDB ve Kimlik Doğrulama Entegrasyonu

Bu doküman, projeye eklenen veritabanı yapısı hakkında bilgi verir.

## Veritabanı Yapısı

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
