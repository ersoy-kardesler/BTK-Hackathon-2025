"""
BTK Hackathon 2025 - Eğitim Asistanı Uygulaması

Bu uygulama, Google Gemini AI kullanarak eğitim içeriği oluşturan
bir Flask web uygulamasıdır.
Özellikler:
- Müfredat oluşturma
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
Tarih: Temmuz 2025
"""

from flask import Flask, render_template, request, jsonify

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Fonksiyonları ayrı dosyalardan import et
from generate_curriculum import generate_curriculum
from evaluate_assignment import evaluate_assignment

# .env dosyasından çevre değişkenlerini yükle
# Bu dosya API anahtarları ve diğer gizli bilgileri içerir
load_dotenv()

# Flask uygulamasını başlat
# __name__ parametresi Flask'a uygulama dosyasının konumunu söyler
app = Flask(__name__)
# Güvenlik için secret key ayarla (session yönetimi için gerekli)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-secret-key")

# Google Gemini API'yi yapılandır
# Çevre değişkeninden API anahtarını al
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY çevre değişkeni bulunamadı!")
    print("Lütfen .env dosyasında GEMINI_API_KEY=your_api_key_here"
          "şeklinde tanımlayın")
    exit(1)

# Gemini AI modelini yapılandır ve başlat
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")
print("✅ Google Gemini API başarıyla bağlandı!")


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


# Müfredat oluşturma sayfası (GET)
@app.route("/curriculum", methods=["GET"])
def curriculum():
    """
    Müfredat oluşturma sayfası - Formu gösterir.
    """
    return render_template("curriculum.html")


# Müfredat oluşturma API endpoint (POST)
@app.route("/api/curriculum", methods=["POST"])
def api_curriculum():
    """
    Müfredat oluşturma API endpoint'i.
    JSON formatında subject alır ve müfredat oluşturur.
    """
    try:
        # JSON verisini al
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON verisi bulunamadı"}), 400

        subject = data.get("subject", "").strip()
        if not subject:
            return jsonify({"error": "Ders adı boş olamaz"}), 400

        # Müfredat oluştur
        curriculum_result = generate_curriculum(subject, model=model)

        return jsonify({
            "success": True,
            "curriculum": curriculum_result,
            "subject": subject
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Müfredat oluşturulurken hata oluştu: {str(e)}"
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
    print("🚀 BTK Hackathon 2025 - Ersoy Kardeşler")
    print("📱 Uygulama URL: http://127.0.0.1:5000")
    print("🛑 Durdurmak için Ctrl+C tuşlayın")

    # Flask development server'ı başlat
    app.run(
        debug=True,        # Geliştirme modu - production'da False olmalı
        host="127.0.0.1",  # Sadece localhost'tan erişim
        port=5000          # Default Flask portu
    )
