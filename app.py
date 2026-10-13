
import os
from datetime import datetime
from urllib.parse import urlparse
from xml.sax.saxutils import escape

from flask import (
    Flask, request, redirect, url_for,
    render_template_string, flash, Response, jsonify
)
import yt_dlp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

SITE_NAME = "SnapTiko"
SITE_URL = os.environ.get(
    "SITE_URL",
    "https://brave-cedar-7334.de.deplexo.com"
).rstrip("/")

GOOGLE_TOKEN = "nwb3Nxl9qGs1VLeuGiOUE4YM2Vw0yh5rxD0dMEXNm8M"

HTML = r"""
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#ffffff">
<meta name="description" content="{{ description }}">
<meta name="google-site-verification" content="nwb3Nxl9qGs1VLeuGiOUE4YM2Vw0yh5rxD0dMEXNm8M">
<meta name="robots" content="index,follow,max-image-preview:large">

<link rel="canonical" href="{{ canonical }}">
<meta property="og:site_name" content="SnapTiko">
<meta property="og:title" content="{{ title }} | SnapTiko">
<meta property="og:description" content="{{ description }}">
<meta property="og:url" content="{{ canonical }}">

<title>{{ title }} | SnapTiko</title>

<style>
:root {
  --pink: #ed1760;
  --pink-dark: #cf104e;
  --ink: #24232b;
  --muted: #737582;
  --soft: #fff3f7;
  --border: #eee8ec;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: #fff;
  color: var(--ink);
  font: 16px/1.8 Arial, Tahoma, sans-serif;
}

a { text-decoration: none; }

header {
  min-height: 76px;
  padding: 12px 6%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  border-bottom: 1px solid var(--border);
}

.logo {
  font-size: 29px;
  font-weight: 900;
  color: var(--pink);
  letter-spacing: -1px;
}

.logo span { color: var(--ink); }

nav {
  display: flex;
  gap: 23px;
  flex-wrap: wrap;
}

nav a {
  color: #45434b;
  font-size: 14px;
}

nav a:hover { color: var(--pink); }

.hero {
  text-align: center;
  padding: 66px 18px 55px;
  background: linear-gradient(180deg, #fff2f7, #fff);
}

.hero h1 {
  font-size: clamp(29px, 5vw, 46px);
  line-height: 1.4;
  margin: 0 0 14px;
  font-weight: 900;
}

.pink { color: var(--pink); }

.subtitle {
  max-width: 650px;
  margin: 0 auto 30px;
  color: var(--muted);
}

.download-box {
  max-width: 760px;
  margin: auto;
  padding: 8px;
  background: white;
  border: 1px solid #f0dce4;
  box-shadow: 0 12px 35px #8e345014;
  border-radius: 15px;
  display: flex;
  gap: 8px;
}

.download-box input {
  flex: 1;
  min-width: 0;
  padding: 13px 15px;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--ink);
  font-size: 15px;
}

button {
  border: 0;
  border-radius: 10px;
  background: var(--pink);
  color: white;
  font-size: 16px;
  font-weight: bold;
  padding: 13px 25px;
  cursor: pointer;
}

button:hover { background: var(--pink-dark); }
button:disabled { opacity: .65; cursor: wait; }

.hint {
  font-size: 12px;
  color: #85818a;
  margin-top: 15px;
}

.alert {
  max-width: 760px;
  margin: 15px auto;
  padding: 12px 16px;
  background: #fff0f3;
  color: #a20d40;
  border: 1px solid #ffd1df;
  border-radius: 10px;
}

.section {
  max-width: 1080px;
  margin: auto;
  padding: 48px 20px;
}

.section h2 {
  text-align: center;
  font-size: 29px;
  margin: 0 0 10px;
}

.section-intro {
  text-align: center;
  color: var(--muted);
  margin: 0 auto 30px;
  max-width: 650px;
}

.cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.card {
  border: 1px solid var(--border);
  border-radius: 15px;
  padding: 23px;
  background: #fff;
}

.icon {
  display: inline-grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 12px;
  background: var(--soft);
  font-size: 23px;
}

.card h3 {
  font-size: 18px;
  margin: 12px 0 5px;
}

.card p, .step p, details p {
  color: var(--muted);
  font-size: 14px;
  margin: 0;
}

.steps, .faq {
  max-width: 780px;
  margin: auto;
}

.step {
  display: flex;
  gap: 15px;
  align-items: flex-start;
  margin: 14px 0;
  padding: 18px;
  border: 1px solid var(--border);
  border-radius: 13px;
}

.number {
  flex: 0 0 38px;
  height: 38px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--pink);
  color: white;
  font-weight: bold;
}

.step h3 { margin: 0 0 4px; font-size: 17px; }

details {
  border-bottom: 1px solid var(--border);
  padding: 17px 5px;
}

summary { cursor: pointer; font-weight: bold; }

.info {
  max-width: 850px;
  margin: 45px auto;
  padding: 28px;
  border: 1px solid var(--border);
  border-radius: 15px;
}

.info h1 { font-size: 29px; }
.info p { color: #5f5d66; }
.info a, .result a { color: var(--pink); }

.result {
  max-width: 760px;
  margin: 18px auto;
  padding: 18px;
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow-wrap: anywhere;
}

footer {
  background: #fff8fa;
  border-top: 1px solid var(--border);
  padding: 28px 18px;
  text-align: center;
  color: var(--muted);
  font-size: 13px;
}

.footer-links {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 18px;
  margin: 10px 0;
}

.footer-links a { color: #514d56; }

@media (max-width: 700px) {
  header {
    padding: 15px;
    flex-direction: column;
    gap: 8px;
  }

  nav { gap: 14px; justify-content: center; }
  .hero { padding: 45px 15px 35px; }
  .download-box { flex-direction: column; }

  .download-box input {
    padding: 13px 10px;
    width: 100%;
  }

  .download-box button { width: 100%; }
  .cards { grid-template-columns: 1fr; }
  .section { padding: 35px 16px; }

  .info {
    margin: 25px 15px;
    padding: 20px;
  }
}
</style>
</head>

<body>
<header>
  <a class="logo" href="/">Snap<span>Tiko</span></a>
  <nav>
    <a href="/">الرئيسية</a>
    <a href="/#how">طريقة الاستعمال</a>
    <a href="/#features">المميزات</a>
    <a href="/about">من نحن</a>
  </nav>
</header>

{% with messages = get_flashed_messages() %}
  {% if messages %}
    {% for message in messages %}
      <div class="alert">{{ message }}</div>
    {% endfor %}
  {% endif %}
{% endwith %}

{% if page == "home" %}
<main>
<section class="hero">
  <h1>
    تعامل مع روابط فيديوهات TikTok عبر<br>
    <span class="pink">SnapTiko</span>
  </h1>

  <p class="subtitle">
    لسق رابط فيديو عام متاح للمعالجة وجرب.
    النتائج كتختلف حسب توفر الفيديو ودعم أداة المعالجة.
  </p>

  <form class="download-box" action="/download" method="post"
        onsubmit="let b=this.querySelector('button');b.disabled=true;b.textContent='جاري المعالجة...';">
    <input type="url" name="video_url"
           placeholder="لسق رابط TikTok هنا..."
           aria-label="رابط فيديو TikTok" required>
    <button type="submit">معالجة الرابط ↓</button>
  </form>

  <p class="hint">
    استعمل الخدمة غير للفيديوهات ديالك أو المحتوى اللي عندك الإذن بتحميله.
  </p>

  {% if result %}
  <div class="result">
    <h2>{{ result.title }}</h2>

    {% if result.thumbnail %}
    <p>
      <img src="{{ result.thumbnail }}" alt="صورة الفيديو"
           style="max-width:220px;width:100%;border-radius:10px">
    </p>
    {% endif %}

    <p>المدة: {{ result.duration }} ثانية</p>

    {% if result.download_url %}
    <p>
      <a href="{{ result.download_url }}" rel="nofollow noopener" target="_blank">
        فتح رابط الفيديو
      </a>
    </p>
    {% else %}
    <p>ما لقيناش رابط مباشر مدعوم لهاد الفيديو.</p>
    {% endif %}

    <p class="hint">
      الرابط المباشر قد تنتهي صلاحيته. حمّل فقط المحتوى المسموح لك به.
    </p>
  </div>
  {% endif %}
</section>

<section class="section" id="features">
  <h2>علاش تستعمل <span class="pink">SnapTiko</span>؟</h2>
  <p class="section-intro">
    واجهة بسيطة باش تسهّل عليك التعامل مع روابط الفيديو.
  </p>

  <div class="cards">
    <article class="card">
      <div class="icon">⚡</div>
      <h3>سهل الاستعمال</h3>
      <p>لسق الرابط واضغط على زر المعالجة باش تبدأ.</p>
    </article>

    <article class="card">
      <div class="icon">📱</div>
      <h3>متجاوب مع الهاتف</h3>
      <p>تصميم كيتأقلم مع شاشات الهواتف والكمبيوتر.</p>
    </article>

    <article class="card">
      <div class="icon">🌐</div>
      <h3>واجهة عربية</h3>
      <p>استعمل الموقع بسهولة باللغة العربية.</p>
    </article>
  </div>
</section>

<section class="section" id="how">
  <h2>كيفاش تستعمل الموقع؟</h2>
  <p class="section-intro">ثلاث خطوات بسيطة.</p>

  <div class="steps">
    <div class="step">
      <div class="number">1</div>
      <div>
        <h3>نسخ الرابط</h3>
        <p>نسخ رابط فيديو عام وعندك الحق تستعمله.</p>
      </div>
    </div>

    <div class="step">
      <div class="number">2</div>
      <div>
        <h3>لصق الرابط</h3>
        <p>حط الرابط فالمربع الموجود فوق الصفحة.</p>
      </div>
    </div>

    <div class="step">
      <div class="number">3</div>
      <div>
        <h3>معالجة الرابط</h3>
        <p>ضغط على الزر وانتظر النتيجة.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <h2>الأسئلة الشائعة</h2>

  <div class="faq">
    <details>
      <summary>واش جميع الروابط كتخدم؟</summary>
      <p>لا، النتيجة كتختلف حسب توفر الفيديو وتغييرات المنصة.</p>
    </details>

    <details>
      <summary>واش خاصني حساب؟</summary>
      <p>الواجهة ما كتطلبش إنشاء حساب للاستعمال الأساسي.</p>
    </details>

    <details>
      <summary>واش نقدر نعالج أي فيديو؟</summary>
      <p>
        استعمل الخدمة غير للمحتوى ديالك أو اللي عندك الإذن بتحميله،
        واحترم حقوق النشر وشروط المنصة.
      </p>
    </details>
  </div>
</section>
</main>

{% else %}
<main class="info">
  <h1>{{ heading }}</h1>
  {{ body|safe }}
</main>
{% endif %}

<footer>
  <a class="logo" href="/">Snap<span>Tiko</span></a>
  <p>أداة بسيطة لمعالجة روابط الفيديوهات العامة المتاحة.</p>

  <div class="footer-links">
    <a href="/">الرئيسية</a>
    <a href="/about">من نحن</a>
    <a href="/privacy">سياسة الخصوصية</a>
    <a href="/terms">شروط الاستخدام</a>
    <a href="/contact">اتصل بنا</a>
  </div>

  <p>© {{ year }} SnapTiko</p>
</footer>
</body>
</html>
"""


def render_page(title, page="info", heading="", body="", result=None,
                description=None, path="/"):
    return render_template_string(
        HTML,
        title=title,
        page=page,
        heading=heading,
        body=body,
        result=result,
        year=datetime.utcnow().year,
        description=description or
        "SnapTiko أداة بسيطة لمعالجة روابط فيديوهات TikTok العامة المتاحة.",
        canonical=SITE_URL + path
    )


def is_valid_tiktok_url(value):
    try:
        parsed = urlparse(value.strip())
        host = (parsed.hostname or "").lower()

        allowed = {
            "tiktok.com",
            "www.tiktok.com",
            "m.tiktok.com",
            "vm.tiktok.com",
            "vt.tiktok.com"
        }

        return (
            parsed.scheme == "https"
            and host in allowed
            and not parsed.username
            and not parsed.password
        )
    except (ValueError, AttributeError):
        return False


@app.get("/")
def home():
    return render_page(
        "معالجة روابط فيديوهات TikTok",
        page="home",
        description="SnapTiko أداة عربية لمعالجة روابط فيديوهات TikTok العامة المتاحة."
    )


@app.post("/download")
def download():
    video_url = (request.form.get("video_url") or "").strip()

    if not is_valid_tiktok_url(video_url):
        flash("دخل رابط TikTok صحيح كيبدا بـ https://")
        return redirect(url_for("home"))

    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
        "socket_timeout": 20,
        "retries": 1
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(video_url, download=False)

        result = {
            "title": (info.get("title") or "فيديو TikTok")[:200],
            "thumbnail": info.get("thumbnail"),
            "duration": int(info.get("duration") or 0),
            "download_url": info.get("url")
        }

        return render_page(
            "نتيجة معالجة الرابط",
            page="home",
            result=result,
            description="نتيجة معالجة رابط فيديو عام عبر SnapTiko."
        )

    except Exception:
        flash(
            "تعذّر معالجة الرابط. ممكن الفيديو خاص أو غير متاح "
            "أو غير مدعوم. تأكد من الرابط وجرب مرة أخرى."
        )
        return redirect(url_for("home"))


@app.get("/about")
def about():
    return render_page(
        "من نحن",
        heading="من نحن",
        body=(
            "<p>SnapTiko مشروع مستقل بواجهة عربية لمعالجة "
            "روابط فيديوهات TikTok العامة المتاحة.</p>"
            "<p>الخدمة ما كتضمنش أن جميع الروابط غادي تخدم، "
            "وما عندهاش علاقة رسمية بـ TikTok.</p>"
        ),
        path="/about"
    )


@app.get("/privacy")
def privacy():
    return render_page(
        "سياسة الخصوصية",
        heading="سياسة الخصوصية",
        body=(
            "<p>الرابط اللي كتدخلو كيتعالج لمحاولة جلب معلومات الفيديو. "
            "هاد الكود ما كيخزنش الروابط عمداً فقاعدة بيانات، "
            "ولكن الاستضافة تقدر تحتافظ بسجلات تقنية.</p>"
            "<p>إلى زدتي الإعلانات أو التحليلات، حدّث هاد السياسة "
            "باش توضح البيانات اللي كتجمعها الخدمات الخارجية.</p>"
        ),
        path="/privacy"
    )


@app.get("/terms")
def terms():
    return render_page(
        "شروط الاستخدام",
        heading="شروط الاستخدام",
        body=(
            "<p>استعمل الموقع غير للمحتوى ديالك أو المحتوى اللي عندك "
            "الإذن بتحميله. احترم حقوق النشر وشروط المنصة.</p>"
            "<p>ممنوع محاولة الوصول لمحتوى خاص أو مقيد أو انتهاك "
            "حقوق الآخرين.</p>"
        ),
        path="/terms"
    )


@app.get("/contact")
def contact():
    return render_page(
        "اتصل بنا",
        heading="اتصل بنا",
        body="<p>زيد هنا عنوان البريد الإلكتروني ديال إدارة الموقع قبل الإطلاق العمومي.</p>",
        path="/contact"
    )


@app.get("/robots.txt")
def robots():
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /download\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    return Response(content, mimetype="text/plain")


@app.get("/sitemap.xml")
def sitemap():
    paths = ["/", "/about", "/privacy", "/terms", "/contact"]

    urls = "".join(
        f"<url><loc>{escape(SITE_URL + path)}</loc></url>"
        for path in paths
    )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + urls +
        '</urlset>'
    )

    return Response(xml, mimetype="application/xml")


@app.get("/health")
def health():
    return jsonify(status="ok", service=SITE_NAME)


@app.errorhandler(404)
def not_found(error):
    return render_page(
        "الصفحة غير موجودة",
        heading="الصفحة غير موجودة",
        body='<p>هاد الصفحة ما كايناش.</p><p><a href="/">رجع للرئيسية</a></p>'
    ), 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        debug=False
    )
