-- BTK Hackathon 2025 - Eğitim Asistanı Veritabanı Şeması
-- Bu dosyayı MariaDB'de çalıştırarak veritabanı yapısını oluşturun

-- Veritabanını oluştur (isteğe bağlı)
CREATE DATABASE IF NOT EXISTS btk_hackathon_2025 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE btk_hackathon_2025;

-- Kullanıcılar tablosu (sadece admin ve normal roller)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('admin', 'normal') DEFAULT 'normal',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Oturumlar tablosu (session management için)
CREATE TABLE IF NOT EXISTS user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_session_token (session_token),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Eğitim içerikleri tablosu
CREATE TABLE IF NOT EXISTS education_contents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_favorite BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_subject (subject),
    INDEX idx_generated_at (generated_at),
    INDEX idx_is_favorite (is_favorite)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Ödev değerlendirmeleri tablosu
CREATE TABLE IF NOT EXISTS assignment_evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    assignment_text TEXT NOT NULL,
    criteria TEXT NOT NULL,
    evaluation_result TEXT NOT NULL,
    score DECIMAL(5,2),
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_evaluated_at (evaluated_at),
    INDEX idx_score (score)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Kullanıcı aktivite logları
CREATE TABLE IF NOT EXISTS user_activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Şifre sıfırlama tokenları
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- API anahtarları tablosu (Gemini API Key vb.)
CREATE TABLE IF NOT EXISTS api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    key_name VARCHAR(100) NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_used TIMESTAMP NULL,
    usage_count INT DEFAULT 0,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_active (is_active),
    INDEX idx_last_used (last_used),
    UNIQUE KEY unique_user_key_name (user_id, key_name)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Kullanıcı ayarları tablosu (her kullanıcının kendi ayarları)
CREATE TABLE IF NOT EXISTS user_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    gemini_api_key TEXT,
    gemini_model VARCHAR(100) DEFAULT 'gemini-2.5-flash',
    dark_mode BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_settings (user_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Sistem konfigürasyonu tablosu
CREATE TABLE IF NOT EXISTS system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    config_type ENUM('string', 'integer', 'boolean', 'json') DEFAULT 'string',
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_config_key (config_key),
    INDEX idx_config_type (config_type)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;



-- Başlangıç admin ve normal kullanıcıları oluştur (parolalar boş)
INSERT INTO users (username, email, password_hash, full_name, role) VALUES 
('admin', 'admin@example.com', '', 'Admin User', 'admin'),
('user', 'user@example.com', '', 'Normal User', 'normal')
ON DUPLICATE KEY UPDATE id=id;

-- Sistem konfigürasyonu başlangıç verileri
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('app_name', 'BTK Hackathon 2025 - Eğitim Asistanı', 'string', 'Uygulama adı'),
('app_version', '1.0.0', 'string', 'Uygulama versiyonu'),
('maintenance_mode', 'false', 'boolean', 'Bakım modu durumu'),
('max_file_size', '10485760', 'integer', 'Maksimum dosya boyutu (bytes)'),
('session_timeout', '86400', 'integer', 'Oturum zaman aşımı (saniye)'),
('gemini_model', 'gemini-2.5-flash', 'string', 'Varsayılan Gemini model'),
('max_education_length', '5000', 'integer', 'Maksimum eğitim içeriği uzunluğu'),
('max_assignment_length', '3000', 'integer', 'Maksimum ödev uzunluğu'),
('default_user_role', 'normal', 'string', 'Varsayılan kullanıcı rolü'),
('email_notifications', 'true', 'boolean', 'E-posta bildirimleri aktif mi'),
('backup_retention_days', '30', 'integer', 'Yedek dosyaları saklama süresi')
ON DUPLICATE KEY UPDATE config_value = VALUES(config_value);

-- Süresi dolmuş sessionları temizlemek için stored procedure
DELIMITER //
CREATE PROCEDURE CleanExpiredSessions()
BEGIN
    DELETE FROM user_sessions WHERE expires_at < NOW();
    DELETE FROM password_reset_tokens WHERE expires_at < NOW();
END//
DELIMITER ;

-- Düzenli temizlik için event scheduler (isteğe bağlı)
-- SET GLOBAL event_scheduler = ON;
-- CREATE EVENT IF NOT EXISTS cleanup_expired_tokens
-- ON SCHEDULE EVERY 1 HOUR
-- DO CALL CleanExpiredSessions();

-- Kullanıcı istatistikleri view'i
CREATE VIEW user_stats AS
SELECT 
    u.id,
    u.username,
    u.full_name,
    u.role,
    u.created_at,
    u.last_login,
    COUNT(DISTINCT ec.id) as education_count,
    COUNT(DISTINCT ae.id) as assignment_count,
    AVG(ae.score) as avg_assignment_score
FROM users u
LEFT JOIN education_contents ec ON u.id = ec.user_id
LEFT JOIN assignment_evaluations ae ON u.id = ae.user_id
WHERE u.is_active = TRUE
GROUP BY u.id, u.username, u.full_name, u.role, u.created_at, u.last_login;
