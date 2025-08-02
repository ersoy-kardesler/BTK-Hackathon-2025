"""
BTK Hackathon 2025 - Eğitim Asistanı Uygulaması

Bu uygulama, Google Gemini AI kullanarak eğitim içeriği oluşturan bir Flask web
uygulamasıdır.

Özellikler:
    - Eğitim oluşturma
    - Ödev değerlendirme
    - Kullanıcı kimlik doğrulama (MariaDB)
    - Oturum yönetimi

Gereksinimler:
    - Python 3.8+
    - Flask
    - google-generativeai
    - python-dotenv
    - mysql-connector-python
    - bcrypt

Kullanım:
    1. .env dosyasında GEMINI_API_KEY ve veritabanı ayarlarını tanımlayın
    2. requirements.txt'deki paketleri yükleyin
    3. database_schema.sql'i MariaDB'de çalıştırın
    4. python app.py ile uygulamayı başlatın

Yazarlar: Ersoy Kardeşler
"""

import re
import logging
import google.generativeai as genai
from datetime import timedelta
from flask import Flask, render_template, request, jsonify, g, session

from auth.auth_manager import get_auth
from auth.flask_auth import (
    login_required,
    optional_auth,
    get_current_user_safe,
    get_client_info,
    login_user_session,
    logout_user_session,
    get_session_token,
    success_response,
    role_required,
)
from config.config_loader import load_config, get_secret_key
from database.database_connection import (
    init_database,
    get_db,
    get_system_config,
    get_user_settings,
    save_user_settings,
    get_user_gemini_api_key,
)
from education.generate_education import generate_education
from education.evaluate_assignment import evaluate_assignment

# Konfigürasyon ayarlarını yükle
config = load_config()


def get_user_gemini_model(user_id: int):
    """
    Kullanıcının Gemini modelini ve API anahtarını alır ve modeli başlatır.

    Args:
        user_id (int): Kullanıcı ID'si

    Returns:
        tuple: (model, api_key) veya (None, None) hata durumunda
    """
    try:
        api_key = get_user_gemini_api_key(user_id)
        if not api_key:
            return None, None

        user_settings = get_user_settings(user_id)
        if not user_settings:
            return None, None

        model_name = user_settings.get("gemini_model", "gemini-2.5-flash")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        return model, api_key
    except Exception as e:
        print(f"Gemini model oluşturma hatası: {e}")
        return None, None


# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Auth manager'ı al
auth_manager = get_auth()

# Flask uygulamasını başlat
app = Flask(__name__)

# Konfigürasyonu Flask uygulamasına uygula
app.secret_key = get_secret_key()
app.config.update(config)

# Session ayarları
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)
app.config["SESSION_COOKIE_SECURE"] = False  # HTTPS'de True yapın
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Veritabanını başlat
if not init_database():
    print("HATA: Veritabanı bağlantısı kurulamadı!")
    print("Lütfen config.ini dosyasında veritabanı ayarlarını kontrol edin:")
    print("- DB_HOST (varsayılan: localhost)")
    print("- DB_PORT (varsayılan: 3306)")
    print("- DB_USER (varsayılan: root)")
    print("- DB_PASSWORD")
    print("- DB_NAME (varsayılan: btk_hackathon_2025)")
    exit(1)

# Google Gemini API'yi yapılandır
# Artık API anahtarı kullanıcı bazında alınacak, sistem başlangıcında genel API
# kontrolü yapmıyoruz
# API anahtarını sistem konfigürasyonundan al (sadece fallback için)
system_api_key = get_system_config("GEMINI_API_KEY")
if not system_api_key:
    # Eğer veritabanında yoksa config.ini dosyasından al ve kaydet
    system_api_key = config.get("GEMINI_API_KEY")
    if system_api_key:
        from database.database_connection import set_system_config

        set_system_config("GEMINI_API_KEY", system_api_key)
        print("Sistem Gemini API anahtarı veritabanına kaydedildi.")

# Gemini AI modelini yapılandır (model başlatması kullanıcı bazında yapılacak)
print("Google Gemini API modülü yüklendi!")
print("API anahtarları kullanıcı bazında yönetilecek.")


# Ana sayfaya (/) gelen istekleri karşıla
@app.route("/")
@optional_auth
def index():
    """
    Ana sayfa route'u - Uygulamanın giriş sayfasını görüntüler.

    Bu route Flask uygulamasının ana sayfasını render eder.
    Kullanıcılar buradan eğitim asistanı özelliklerine erişebilir.

    Returns:
        str: Render edilmiş HTML sayfası (templates/index.html)

    Note:
        - GET metoduyla erişilebilir
        - templates/index.html dosyası mevcut olmalıdır
        - Static dosyalar (CSS, JS) otomatik olarak yüklenir
        - İsteğe bağlı kimlik doğrulama desteklenir
    """
    # Kullanıcı bilgilerini template'e gönder
    current_user = get_current_user_safe()
    return render_template("index.html", current_user=current_user)


# Eğitim oluşturma sayfası (GET)
@app.route("/education", methods=["GET"])
@login_required
def education():
    """
    Eğitim oluşturma sayfası - Formu gösterir.
    Giriş yapmış kullanıcılar gereklidir.
    """
    return render_template("education.html", current_user=g.current_user)


# Eğitim oluşturma API endpoint (POST)
@app.route("/api/education", methods=["POST"])
@login_required
def api_education():
    """
    Eğitim oluşturma API endpoint'i.
    JSON formatında bilgi alır ve eğitim oluşturur.
    Giriş yapmış kullanıcılar gereklidir.
    """
    try:
        # JSON verisini al
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON verisi bulunamadı"}), 400

        subject = data.get("subject", "").strip()
        if not subject:
            return jsonify({"error": "Ders adı boş olamaz"}), 400

        # Kullanıcının Gemini modelini al
        model, api_key = get_user_gemini_model(g.current_user["user_id"])
        if not model:
            return (
                jsonify(
                    {
                        "error": "Gemini API anahtarı bulunamadı. "
                        "Lütfen ayarlar sayfasından API anahtarınızı girin."
                    }
                ),
                400,
            )

        # Eğitim oluştur
        education_result = generate_education(subject, model=model)

        # Veritabanına kaydet (isteğe bağlı)
        try:
            db = get_db()

            query = """
                INSERT INTO education_contents (user_id, subject, content)
                VALUES (%s, %s, %s)
                """
            db.execute_insert(
                query, (g.current_user["user_id"], subject, education_result)
            )
        except Exception as db_error:
            # Veritabanı hatası logla ama devam et
            print(f"Eğitim veritabanına kaydedilemedi: {db_error}")

        return jsonify(
            {
                "success": True,
                "education": education_result,
                "subject": subject,
                "user": g.current_user["username"],
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Eğitim oluşturulurken hata oluştu: {str(e)}",
                }
            ),
            500,
        )


# Ödev değerlendirme sayfası (GET)
@app.route("/assignment_evaluate", methods=["GET"])
@login_required
def assignment_evaluate():
    """
    Ödev değerlendirme sayfası - Formu gösterir.
    Giriş yapmış kullanıcılar gereklidir.
    """
    return render_template("assignment_evaluate.html",
                           current_user=g.current_user)


# Ödev değerlendirme API endpoint (POST)
@app.route("/api/assignment_evaluate", methods=["POST"])
@login_required
def api_assignment_evaluate():
    """
    Ödev değerlendirme API endpoint'i.
    JSON formatında assignment_text ve criteria alır ve değerlendirme yapar.
    Giriş yapmış kullanıcılar gereklidir.
    """
    try:
        # JSON verisini al
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON verisi bulunamadı"}), 400

        assignment_text = data.get("assignment_text", "").strip()
        criteria = data.get("criteria", "").strip()

        if not assignment_text:
            return jsonify({"error": "Ödev metni boş olamaz"}), 400
        if not criteria:
            return jsonify({"error": "Değerlendirme kriteri boş olamaz"}), 400

        # Kullanıcının Gemini modelini al
        model, api_key = get_user_gemini_model(g.current_user["user_id"])
        if not model:
            return (
                jsonify(
                    {
                        "error": "Gemini API anahtarı bulunamadı."
                        "Lütfen ayarlar sayfasından API anahtarınızı girin."
                    }
                ),
                400,
            )

        # Ödev değerlendirmesi yap
        evaluation_result = evaluate_assignment(assignment_text,
                                                criteria,
                                                model=model)

        # Veritabanına kaydet (isteğe bağlı)
        try:
            db = get_db()

            # Puan çıkarmaya çalış (basit regex ile)
            score_match = re.search(
                r"(\d+(?:\.\d+)?)\s*(?:puan|point|/)",
                evaluation_result.lower(),
            )
            score = float(score_match.group(1)) if score_match else None

            query = """
                INSERT INTO assignment_evaluations
                 (user_id, assignment_text, criteria, evaluation_result, score)
                VALUES (%s, %s, %s, %s, %s)
                """
            db.execute_insert(
                query,
                (
                    g.current_user["user_id"],
                    assignment_text,
                    criteria,
                    evaluation_result,
                    score,
                ),
            )
        except Exception as db_error:
            # Veritabanı hatası logla ama devam et
            print(f"Ödev değerlendirmesi veritabanına"
                  "kaydedilemedi: {db_error}")

        return jsonify(
            {
                "success": True,
                "evaluation": evaluation_result,
                "assignment_text": assignment_text,
                "criteria": criteria,
                "user": g.current_user["username"],
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Ödev değerlendirilirken hata oluştu: {str(e)}",
                }
            ),
            500,
        )


# Giriş ve kayıt sayfaları
@app.route("/login", methods=["GET"])
def login_page():
    """
    Giriş sayfası
    """
    return render_template("login.html")


@app.route("/register", methods=["GET"])
def register_page():
    """
    Kayıt sayfası
    """
    return render_template("register.html")


# =============== AUTH API ENDPOINTS ===============


@app.route("/auth/login", methods=["POST"])
def auth_login():
    """
    Kullanıcı giriş endpoint'i

    Request Body:
    {
        "username": "kullanici_adi_veya_email",
        "password": "sifre"
    }

    Response:
    {
        "success": true,
        "message": "Giriş başarılı",
        "data": {
            "user": {
                "id": 1,
                "username": "kullanici",
                "email": "email@example.com",
                "full_name": "Tam Ad",
                "role": "student"
            },
            "session_token": "token_here"
        }
    }
    """
    try:
        # JSON verisini al
        data = request.get_json()
        if not data:
            return jsonify({"success": False,
                            "error": "JSON verisi bulunamadı"}),
            400

        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return (
                jsonify({"success": False,
                         "error": "Kullanıcı adı ve şifre gerekli"}),
                400,
            )

        # İstemci bilgilerini al
        client_info = get_client_info()

        # Giriş yap
        success, session_token, user_info = auth_manager.login(
            username,
            password,
            client_info["ip_address"],
            client_info["user_agent"]
        )

        if not success:
            return (
                jsonify({"success": False,
                         "error": "Kullanıcı adı veya şifre hatalı"}),
                401,
            )

        # Flask session'ına kaydet
        login_user_session(user_info, session_token)

        logger.info(
            f"Başarılı giriş: {user_info['username']}"
            " - IP: {client_info['ip_address']}"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Giriş başarılı",
                    "data": {"user": user_info,
                             "session_token": session_token},
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Giriş endpoint hatası: {e}")
        return (
            jsonify({"success": False,
                     "error": "Giriş işlemi sırasında hata oluştu"}),
            500,
        )


@app.route("/auth/logout", methods=["POST"])
@login_required
def auth_logout():
    """
    Kullanıcı çıkış endpoint'i

    Response:
    {
        "success": true,
        "message": "Çıkış başarılı"
    }
    """
    try:
        # Session token'ı al
        session_token = get_session_token()

        if session_token:
            # Oturumu sonlandır
            auth_manager.logout(session_token)

        # Flask session'ını temizle
        logout_user_session()

        logger.info("Kullanıcı çıkışı yapıldı")

        return success_response(message="Çıkış başarılı")

    except Exception as e:
        logger.error(f"Çıkış endpoint hatası: {e}")
        return (
            jsonify({"success": False,
                     "error": "Çıkış işlemi sırasında hata oluştu"}),
            500,
        )


@app.route("/auth/register", methods=["POST"])
def auth_register():
    """
    Kullanıcı kayıt endpoint'i

    Request Body:
    {
        "username": "kullanici_adi",
        "email": "email@example.com",
        "password": "sifre",
        "full_name": "Tam Ad",
        "role": "student"  // optional: student, teacher, admin
    }

    Response:
    {
        "success": true,
        "message": "Kayıt başarılı"
    }
    """
    try:
        # JSON verisini al
        data = request.get_json()
        if not data:
            return jsonify({"success": False,
                            "error": "JSON verisi bulunamadı"}),
            400

        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")
        full_name = data.get("full_name", "").strip()
        role = data.get("role", "student").strip()

        # Validasyon
        if not username or not email or not password:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Kullanıcı adı, e-posta ve şifre gerekli",
                    }
                ),
                400,
            )

        if role not in ["student", "teacher", "admin"]:
            role = "student"

        # Kullanıcıyı kaydet
        success, error_message = auth_manager.register_user(
            username, email, password, full_name, role
        )

        if not success:
            return jsonify({"success": False, "error": error_message}), 400

        logger.info(f"Yeni kullanıcı kaydedildi: {username}")

        return success_response(message="Kayıt başarılı")

    except Exception as e:
        logger.error(f"Kayıt endpoint hatası: {e}")
        return (
            jsonify({"success": False,
                     "error": "Kayıt işlemi sırasında hata oluştu"}),
            500,
        )


@app.route("/auth/profile", methods=["GET"])
@login_required
def auth_profile():
    """
    Kullanıcı profil bilgileri endpoint'i

    Response:
    {
        "success": true,
        "data": {
            "id": 1,
            "username": "kullanici",
            "email": "email@example.com",
            "full_name": "Tam Ad",
            "role": "student"
        }
    }
    """
    try:
        user_info = {
            "id": g.current_user["user_id"],
            "username": g.current_user["username"],
            "email": g.current_user["email"],
            "full_name": g.current_user["full_name"],
            "role": g.current_user["role"],
        }

        return success_response(data=user_info)

    except Exception as e:
        logger.error(f"Profil endpoint hatası: {e}")
        return jsonify({"success": False,
                        "error": "Profil bilgileri alınamadı"}),
        500


@app.route("/auth/change-password", methods=["POST"])
@login_required
def auth_change_password():
    """
    Şifre değiştirme endpoint'i

    Request Body:
    {
        "old_password": "eski_sifre",
        "new_password": "yeni_sifre"
    }

    Response:
    {
        "success": true,
        "message": "Şifre başarıyla değiştirildi"
    }
    """
    try:
        # JSON verisini al
        data = request.get_json()
        if not data:
            return jsonify({"success": False,
                            "error": "JSON verisi bulunamadı"}),
            400

        old_password = data.get("old_password", "")
        new_password = data.get("new_password", "")

        if not old_password or not new_password:
            return (
                jsonify({"success": False,
                         "error": "Eski ve yeni şifre gerekli"}),
                400,
            )

        # Şifre değiştir
        success, error_message = auth_manager.change_password(
            g.current_user["user_id"], old_password, new_password
        )

        if not success:
            return jsonify({"success": False, "error": error_message}), 400

        logger.info(f"Şifre değiştirildi: {g.current_user['username']}")

        return success_response(message="Şifre başarıyla değiştirildi")

    except Exception as e:
        logger.error(f"Şifre değiştirme endpoint hatası: {e}")
        return (
            jsonify(
                {"success": False,
                 "error": "Şifre değiştirme sırasında hata oluştu"}
            ),
            500,
        )


@app.route("/auth/check-session", methods=["GET"])
def auth_check_session():
    """
    Oturum durumu kontrol endpoint'i

    Response:
    {
        "success": true,
        "data": {
            "authenticated": true,
            "user": {
                "id": 1,
                "username": "kullanici",
                "role": "student"
            }
        }
    }
    """
    try:
        session_token = get_session_token()

        if not session_token:
            return jsonify(
                {"success": True,
                 "data": {"authenticated": False,
                          "user": None}}
            )

        user = auth_manager.get_current_user(session_token)

        if not user:
            return jsonify(
                {"success": True,
                 "data": {"authenticated": False,
                          "user": None}}
            )

        user_info = {
            "id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        }

        return jsonify(
            {"success": True,
             "data": {"authenticated": True,
                      "user": user_info}}
        )

    except Exception as e:
        logger.error(f"Oturum kontrol hatası: {e}")
        return jsonify({"success": False,
                        "error": "Oturum kontrol edilemedi"}),
        500


# =============== USER DATA API ENDPOINTS ===============


@app.route("/api/user/education-history", methods=["GET"])
@login_required
def user_education_history():
    """
    Kullanıcının eğitim geçmişini getirir
    """
    try:
        # Sayfalama parametreleri
        page = int(request.args.get("page", 1))
        limit = min(int(request.args.get("limit", 10)), 50)  # Max 50
        offset = (page - 1) * limit

        db = get_db()

        # Toplam kayıt sayısı
        count_query = """
            SELECT COUNT(*) as total
             FROM education_contents
             WHERE user_id = %s
        """
        total_result = db.execute_single(count_query,
                                         (g.current_user["user_id"],))
        total = total_result["total"] if total_result else 0

        # Eğitim verilerini getir
        query = """
            SELECT id, subject, content, generated_at, is_favorite
             FROM education_contents
             WHERE user_id = %s
             ORDER BY generated_at DESC
             LIMIT %s OFFSET %s
        """

        educations = db.execute_query(query,
                                      (g.current_user["user_id"],
                                       limit, offset))

        # Sayfa sayısını hesapla
        pages = (total + limit - 1) // limit

        return jsonify(
            {
                "success": True,
                "data": {
                    "educations": educations,
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "pages": pages,
                },
            }
        )

    except Exception as e:
        logger.error(f"Eğitim geçmişi hatası: {e}")
        return jsonify({"success": False,
                        "error": "Eğitim geçmişi alınamadı"}),
        500


@app.route("/api/user/assignment-history", methods=["GET"])
@login_required
def user_assignment_history():
    """
    Kullanıcının ödev değerlendirme geçmişini getirir
    """
    try:
        # Sayfalama parametreleri
        page = int(request.args.get("page", 1))
        limit = min(int(request.args.get("limit", 10)), 50)
        offset = (page - 1) * limit

        db = get_db()

        # Toplam kayıt sayısı ve istatistikler
        stats_query = """
            SELECT
             COUNT(*) as total,
             AVG(score) as avg_score
             FROM assignment_evaluations
             WHERE user_id = %s
        """
        stats_result = db.execute_single(stats_query,
                                         (g.current_user["user_id"],))
        total = stats_result["total"] if stats_result else 0
        avg_score = float(stats_result["avg_score"]) \
            if stats_result["avg_score"] else 0

        # Ödev verilerini getir
        query = """
            SELECT id, assignment_text, criteria, evaluation_result,
             score, evaluated_at
             FROM assignment_evaluations
             WHERE user_id = %s
             ORDER BY evaluated_at DESC
             LIMIT %s OFFSET %s
        """

        assignments = db.execute_query(
            query, (g.current_user["user_id"], limit, offset)
        )

        # Sayfa sayısını hesapla
        pages = (total + limit - 1) // limit if total > 0 else 0

        return jsonify(
            {
                "success": True,
                "data": {
                    "assignments": assignments,
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "pages": pages,
                    "stats": {
                        "avg_score": round(avg_score, 2),
                        "total_assignments": total,
                    },
                },
            }
        )

    except Exception as e:
        logger.error(f"Ödev geçmişi hatası: {e}")
        return jsonify({"success": False,
                        "error": "Ödev geçmişi alınamadı"}),
    500


@app.route("/api/user/dashboard-stats", methods=["GET"])
@login_required
def user_dashboard_stats():
    """
    Kullanıcı dashboard istatistikleri
    """
    try:
        user_id = g.current_user["user_id"]
        db = get_db()

        # Eğitim sayısı
        education_count_query = """
            SELECT COUNT(*) as count
             FROM education_contents
             WHERE user_id = %s
        """
        education_result = db.execute_single(education_count_query, (user_id,))
        education_count = education_result["count"] if education_result else 0

        # Ödev sayısı ve ortalama puan
        assignment_stats_query = """
            SELECT COUNT(*) as count, AVG(score) as avg_score
             FROM assignment_evaluations
             WHERE user_id = %s
        """
        assignment_result = db.execute_single(assignment_stats_query,
                                              (user_id,))
        assignment_count = assignment_result["count"] \
            if assignment_result else 0
        avg_score = (
            float(assignment_result["avg_score"])
            if assignment_result["avg_score"]
            else 0
        )

        # Son aktiviteler (son 5 kayıt)
        recent_query = """
            (SELECT 'education' as type, subject as title, generated_at as date
             FROM education_contents
             WHERE user_id = %s)
             UNION ALL
             (SELECT 'assignment' as type,
             CONCAT('Ödev: ', LEFT(assignment_text, 50), '...') as title,
             evaluated_at as date
             FROM assignment_evaluations
             WHERE user_id = %s)
             ORDER BY date DESC
             LIMIT 5
        """
        recent_activity = db.execute_query(recent_query, (user_id, user_id))

        return jsonify(
            {
                "success": True,
                "data": {
                    "education_count": education_count,
                    "assignment_count": assignment_count,
                    "avg_score": round(avg_score, 2),
                    "recent_activity": recent_activity,
                },
            }
        )

    except Exception as e:
        logger.error(f"Dashboard istatistikleri hatası: {e}")
        return jsonify({"success": False,
                        "error": "İstatistikler alınamadı"}),
        500


@app.route("/api/user/toggle-favorite", methods=["POST"])
@login_required
def user_toggle_favorite():
    """
    Eğitim içeriğini favorilere ekler/çıkarır

    Request Body:
    {
        "education_id": 123
    }

    Response:
    {
        "success": true,
        "data": {
            "is_favorite": true
        }
    }
    """
    try:
        data = request.get_json()
        if not data or "education_id" not in data:
            return jsonify({"success": False,
                            "error": "education_id gerekli"}),
            400

        education_id = data["education_id"]
        user_id = g.current_user["user_id"]

        db = get_db()

        # Eğitimin bu kullanıcıya ait olduğunu kontrol et
        check_query = """
            SELECT is_favorite FROM education_contents
             WHERE id = %s AND user_id = %s
        """
        education = db.execute_single(check_query, (education_id, user_id))

        if not education:
            return jsonify({"success": False,
                            "error": "Eğitim bulunamadı"}),
            404

        # Favori durumunu tersine çevir
        new_favorite = not education["is_favorite"]

        update_query = """
            UPDATE education_contents
             SET is_favorite = %s
             WHERE id = %s AND user_id = %s
        """
        db.execute_update(update_query,
                          (new_favorite,
                           education_id,
                           user_id))

        return jsonify({"success": True,
                        "data": {"is_favorite": new_favorite}})

    except Exception as e:
        logger.error(f"Favori toggle hatası: {e}")
        return jsonify({"success": False,
                        "error": "Favori durumu güncellenemedi"}),
        500


@app.route("/api/user/admin/users", methods=["GET"])
@login_required
@role_required("admin")
def admin_get_users():
    """
    Admin - Tüm kullanıcıları listeler

    Query Parameters:
    - page (int): Sayfa numarası
    - limit (int): Sayfa başına kayıt
    - search (str): Arama terimi

    Response:
    {
        "success": true,
        "data": {
            "users": [...],
            "total": 50,
            "page": 1,
            "limit": 10
        }
    }
    """
    try:
        # Sayfalama ve arama parametreleri
        page = int(request.args.get("page", 1))
        limit = min(int(request.args.get("limit", 20)), 100)
        search = request.args.get("search", "").strip()
        offset = (page - 1) * limit

        db = get_db()

        # Base query
        base_where = "WHERE u.id IS NOT NULL"
        params = []

        # Arama filtresi
        if search:
            base_where += (
                " AND (u.username LIKE %s"
                "OR u.email LIKE %s "
                "OR u.full_name LIKE %s)"
            )
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])

        # Toplam kayıt sayısı
        count_query = f"SELECT COUNT(*) as total FROM users u {base_where}"
        total_result = db.execute_single(count_query, tuple(params))
        total = total_result["total"] if total_result else 0

        # Kullanıcı listesi
        query = f"""
            SELECT u.id, u.username, u.email, u.full_name, u.role,
                   u.is_active, u.created_at, u.last_login,
                   COUNT(DISTINCT ec.id) as education_count,
                   COUNT(DISTINCT ae.id) as assignment_count
             FROM users u
             LEFT JOIN education_contents ec ON u.id = ec.user_id
             LEFT JOIN assignment_evaluations ae ON u.id = ae.user_id
             {base_where}
             GROUP BY u.id, u.username, u.email, u.full_name, u.role,
                     u.is_active, u.created_at, u.last_login
             ORDER BY u.created_at DESC
             LIMIT %s OFFSET %s
        """

        params.extend([limit, offset])
        users = db.execute_query(query, tuple(params))

        pages = (total + limit - 1) // limit if total > 0 else 0

        return jsonify(
            {
                "success": True,
                "data": {
                    "users": users,
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "pages": pages,
                },
            }
        )

    except Exception as e:
        logger.error(f"Admin kullanıcı listesi hatası: {e}")
        return jsonify({"success": False,
                        "error": "Kullanıcı listesi alınamadı"}),
        500


# =============== AYARLAR ENDPOINTS ===============


@app.route("/settings", methods=["GET"])
@login_required
def settings_page():
    """
    Kullanıcı ayarları sayfası
    """
    return render_template("settings.html", current_user=g.current_user)


@app.route("/api/settings", methods=["GET"])
@login_required
def api_get_settings():
    """
    Kullanıcının mevcut ayarlarını getir

    Response:
    {
        "success": true,
        "data": {
            "gemini_api_key": "sk-...",
            "gemini_model": "gemini-2.5-flash",
            "dark_mode": false
        }
    }
    """
    try:
        settings = get_user_settings(g.current_user["user_id"])
        if settings is None:
            return jsonify({"success": False,
                            "error": "Ayarlar alınamadı"}),
        500

        # API anahtarını güvenlik için maskeleme
        if settings.get("gemini_api_key"):
            masked_key = (
                settings["gemini_api_key"][:8] + "..." +
                settings["gemini_api_key"][-4:]
            )
            settings["gemini_api_key_masked"] = masked_key
            settings["has_api_key"] = True
        else:
            settings["gemini_api_key_masked"] = ""
            settings["has_api_key"] = False

        # Gerçek API anahtarını response'tan çıkar
        del settings["gemini_api_key"]

        return jsonify({"success": True, "data": settings})

    except Exception as e:
        logger.error(f"Ayarlar getirme hatası: {e}")
        return jsonify({"success": False, "error": "Ayarlar alınamadı"}), 500


@app.route("/api/settings", methods=["POST"])
@login_required
def api_save_settings():
    """
    Kullanıcının ayarlarını kaydet

    Request Body:
    {
        "gemini_api_key": "sk-...",  // isteğe bağlı
        "gemini_model": "gemini-2.5-flash",  // isteğe bağlı
        "dark_mode": true  // isteğe bağlı
    }

    Response:
    {
        "success": true,
        "message": "Ayarlar başarıyla kaydedildi"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False,
                            "error": "JSON verisi bulunamadı"}),
            400

        # Gelen verileri al
        gemini_api_key = data.get("gemini_api_key")
        gemini_model = data.get("gemini_model")
        dark_mode = data.get("dark_mode")

        # API anahtarı varsa basit validasyon
        if gemini_api_key is not None:
            gemini_api_key = gemini_api_key.strip()
            if gemini_api_key and not \
               gemini_api_key.startswith(("AIza", "sk-")):
                return (
                    jsonify(
                        {"success": False,
                         "error": "Geçersiz API anahtarı formatı"}
                    ),
                    400,
                )

        # Model validasyonu
        valid_models = [
            "gemini-2.5-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro",
            "gemini-pro-vision",
        ]
        if gemini_model is not None and gemini_model not in valid_models:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Geçersiz model. "
                        "Geçerli modeller: {', '.join(valid_models)}",
                    }
                ),
                400,
            )

        # Ayarları kaydet
        success = save_user_settings(
            user_id=g.current_user["user_id"],
            gemini_api_key=gemini_api_key,
            gemini_model=gemini_model,
            dark_mode=dark_mode,
        )

        if not success:
            return jsonify({"success": False,
                            "error": "Ayarlar kaydedilemedi"}),
            500

        return jsonify({"success": True,
                        "message": "Ayarlar başarıyla kaydedildi"})

    except Exception as e:
        logger.error(f"Ayarlar kaydetme hatası: {e}")
        return jsonify({"success": False,
                        "error": "Ayarlar kaydedilemedi"}),
        500


@app.route("/api/settings/test-api-key", methods=["POST"])
@login_required
def api_test_gemini_key():
    """
    Gemini API anahtarını test et

    Request Body:
    {
        "api_key": "AIza..."
    }

    Response:
    {
        "success": true,
        "message": "API anahtarı geçerli"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False,
                            "error": "JSON verisi bulunamadı"}),
            400

        api_key = data.get("api_key", "").strip()
        if not api_key:
            return jsonify({"success": False,
                            "error": "API anahtarı boş olamaz"}),
            400

        # API anahtarını test et
        try:
            genai.configure(api_key=api_key)
            test_model = genai.GenerativeModel("gemini-2.5-flash")

            # Basit bir test sorgusu gönder
            response = test_model.generate_content("Test")

            if response and response.text:
                return jsonify(
                    {"success": True,
                     "message": "API anahtarı geçerli ve çalışıyor"}
                )
            else:
                return (
                    jsonify({"success": False,
                             "error": "API anahtarı yanıt vermedi"}),
                    400,
                )

        except Exception as api_error:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"API anahtarı geçersiz: {str(api_error)}",
                    }
                ),
                400,
            )

    except Exception as e:
        logger.error(f"API anahtarı test etme hatası: {e}")
        return jsonify({"success": False,
                        "error": "API anahtarı test edilemedi"}),
        500


# Uygulamayı çalıştır
if __name__ == "__main__":
    """
    Uygulama ana giriş noktası.

    Bu blok sadece dosya doğrudan çalıştırıldığında (python app.py)
    çalışır. Import edildiğinde çalışmaz.

    Geliştirme modunda (debug=True) çalıştırılır:
    - Kod değişikliklerinde otomatik yeniden başlatma
    - Detaylı hata mesajları
    - Hot reload özelliği

    Production ortamında debug=False olmalıdır.
    """

    print("BTK Hackathon 2025 - Ersoy Kardeşler")
    print("Durdurmak için Ctrl+C tuşlayın")
    print(f"Konfigürasyon dosyasından yüklenen ayarlar:")
    print(f"- DEBUG: {config.get('DEBUG', False)}")
    print(f"- HOST: {config.get('HOST', '0.0.0.0')}")
    print(f"- PORT: {config.get('PORT', 5000)}")

    # Flask development server'ı başlat
    app.run(
        debug=config.get("DEBUG", False),
        host=config.get("HOST", "0.0.0.0"),
        port=config.get("PORT", 5000),
    )
