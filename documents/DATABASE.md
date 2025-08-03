# BTK Hackathon 2025 - MariaDB ve Kimlik Doğrulama Entegrasyonu

Bu belge, projeye eklenen veri tabanı yapısı hakkında bilgi verir.

## Veri Tabanı Yapısı

### Tablolar

1. **users** - Kullanıcı bilgileri
   - id, username, email, password_hash
   - full_name, role (student, admin)
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
   - id, user_id, action, details, ip_address, user_agent, created_at

6. **password_reset_tokens** - Parola sıfırlama işaretçileri
   - id, user_id, token, expires_at, created_at

7. **api_keys** - API anahtarları
   - id, user_id, key_name, api_key_encrypted
   - is_active, created_at, updated_at, last_used, usage_count
   - Not: API anahtarları kullanıcı bazında yönetilir. Sistem anahtarı sadece yedek anahtar olarak kullanılır.

8. **user_settings** - Kullanıcı ayarları
   - user_id, gemini_api_key, gemini_model
   - dark_mode, created_at, updated_at
