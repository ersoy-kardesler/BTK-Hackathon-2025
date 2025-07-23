from flask import Flask, render_template

# Flask uygulamasını başlat
app = Flask(__name__)

# Ana sayfaya (/) gelen istekleri karşıla
@app.route("/")
def index():
    # 'index.html' şablonunu render et
    return render_template("index.html")

# Uygulamayı çalıştır
if __name__ == "__main__":
    app.run(debug=True)
