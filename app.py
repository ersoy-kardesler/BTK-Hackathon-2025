"""
BTK Hackathon 2025 - Eğitim Asistanı Uygulaması

Bu uygulama, Google Gemini AI kullanarak eğitim içeriği oluşturan
bir Flask web uygulamasıdır.
Özellikler:
- Eğitim oluşturma
- Ödev değerlendirme

Gereksinimler:
- Python 3.8+
- Flask
- google-generativeai
- python-dotenv

Kullanım:
1. .env dosyasında GEMINI_API_KEY tanımlayın
2. requirements.txt'deki paketleri yükleyin
3. python app.py ile uygulamayı başlatın

Yazarlar: Ersoy Kardeşler
"""

import google.generativeai as genai
import os

from config.config_loader import load_config, get_secret_key
from dotenv import load_dotenv
from education.generate_education import generate_education
from education.evaluate_assignment import evaluate_assignment
from flask import Flask, render_template, request, jsonify
from configparser import ConfigParser

# .env dosyasından çevre değişkenlerini yükle
# Bu dosya API anahtarları ve diğer gizli bilgileri içerir
load_dotenv()

# Konfigürasyon ayarlarını yükle
config = load_config()

# Flask uygulamasını başlat
# __name__ parametresi Flask'a uygulama dosyasının konumunu söyler
app = Flask(__name__)

# Konfigürasyonu Flask uygulamasına uygula
app.secret_key = get_secret_key()
app.config.update(config)

# Google Gemini API'yi yapılandır
# Çevre değişkeninden API anahtarını al
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY çevre değişkeni bulunamadı!")
    print("Lütfen .env dosyasında GEMINI_API_KEY=your_api_key_here"
          "şeklinde tanımlayın")
    exit(1)

# Gemini AI modelini yapılandır ve başlat
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")
print("Google Gemini API başarıyla bağlandı!")


# Ana sayfaya (/) gelen istekleri karşıla
@app.route("/")
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
    """
    return render_template("index.html")


# Eğitim oluşturma sayfası (GET)
@app.route("/education", methods=["GET"])
def education():
    """
    Eğitim oluşturma sayfası - Formu gösterir.
    """
    return render_template("education.html")


# Eğitim oluşturma API endpoint (POST)
@app.route("/api/education", methods=["POST"])
def api_education():
    """
    Eğitim oluşturma API endpoint'i.
    JSON formatında bilgi alır ve eğitim oluşturur.
    """
    try:
        # JSON verisini al
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON verisi bulunamadı"}), 400

        subject = data.get("subject", "").strip()
        if not subject:
            return jsonify({"error": "Ders adı boş olamaz"}), 400

        # Eğitim oluştur
        education_result = generate_education(subject, model=model)

        return jsonify({
            "success": True,
            "education": education_result,
            "subject": subject
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Eğitim oluşturulurken hata oluştu: {str(e)}"
        }), 500


# Ödev değerlendirme sayfası (GET)
@app.route("/assignment_evaluate", methods=["GET"])
def assignment_evaluate():
    """
    Ödev değerlendirme sayfası - Formu gösterir.
    """
    return render_template("assignment_evaluate.html")


# Ödev değerlendirme API endpoint (POST)
@app.route("/api/assignment_evaluate", methods=["POST"])
def api_assignment_evaluate():
    """
    Ödev değerlendirme API endpoint'i.
    JSON formatında assignment_text ve criteria alır ve değerlendirme yapar.
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

        # Ödev değerlendirmesi yap
        evaluation_result = evaluate_assignment(assignment_text,
                                                criteria,
                                                model=model)

        return jsonify({
            "success": True,
            "evaluation": evaluation_result,
            "assignment_text": assignment_text,
            "criteria": criteria
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Ödev değerlendirilirken hata oluştu: {str(e)}"
        }), 500


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
        debug=config.get('DEBUG', False),
        host=config.get('HOST', '0.0.0.0'),
        port=config.get('PORT', 5000)
    )
