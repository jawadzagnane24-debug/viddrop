
import os
import re
import shutil
import tempfile
import logging
from urllib.parse import urlparse
from flask import (
    Flask, Response, render_template_string,
    request, send_file
)
import yt_dlp

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

SITE_URL = "https://brave-cedar-7334.de.deplexo.com"
GOOGLE_VERIFICATION = "nwb3Nxl9qGs1VLeuGiOUE4YM2Vw0yh5rxD0dMEXNm8M"

logging.basicConfig(level=logging.INFO)

HTML = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="{{ verification }}">
<meta name="description" content="SnapVideo أداة بسيطة للتعامل مع روابط فيديو TikTok المتاحة للتنزيل.">
<meta name="robots" content="index,follow">
<meta name="theme-color" content="#0b0b0f">
<title>{{ title }} | SnapVideo</title>
<style>
*{box-sizing:border-box}
body{
 margin:0;background:radial-gradient(ellipse at top,#241018,transparent 48%),#0b0b0f;
 color:#f8f8fc;font-family:Arial,Tahoma,sans-serif;min-height:100vh
}
a{color:inherit;text-decoration:none}
.container{width:min(100% - 32px,900px);margin:auto}
header,footer{border-color:#2c2c37;border-style:solid}
header{border-width:0 0 1px}
.nav{display:flex;justify-content:space-between;align-items:center;padding:17px 0}
.brand{font-size:23px;font-weight:bold;display:flex;gap:10px;align-items:center}
.logo{background:#f22e46;padding:10px 13px;border-radius:12px}
.muted{color:#aaaab8}
.hero{text-align:center;padding:48px 0 25px}
h1{font-size:clamp(30px,6vw,46px);margin:18px 0}
.hero p,.description{color:#aaaab8;line-height:1.9}
.card{max-width:680px;margin:0 auto 28px;padding:25px;border:1px solid #2c2c37;border-radius:20px;background:#15151c}
.platform{text-align:center;padding:13px;border:1px solid #f22e46;background:#32121b;border-radius:12px;margin-bottom:20px;font-weight:bold}
label{display:block;margin-bottom:10px}
input[type=url]{width:100%;padding:16px;border:1px solid #393946;border-radius:12px;background:#0d0d12;color:white;font-size:15px;direction:ltr;text-align:left}
button{width:100%;padding:16px;margin-top:14px;border:0;border-radius:12px;background:#f22e46;color:white;font-size:17px;font-weight:bold;cursor:pointer}
button:hover{background:#d92139}
.notice,.message{margin-top:17px;padding:13px;border-radius:10px;line-height:1.8;font-size:13px}
.notice{background:#101016;color:#aaaab8}
.message{background:#32121b;color:#ffb7c0}
.features{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;margin:30px 0}
.feature{background:#131319;border:1px solid #2c2c37;border-radius:14px;padding:18px}
.feature p{font-size:13px;line-height:1.8;color:#aaaab8}
.ad{min-height:70px;display:grid;place-items:center;border:1px dashed #363641;border-radius:12px;color:#777784;margin:22px auto}
footer{border-width:1px 0 0;margin-top:45px;padding:24px 0;color:#aaaab8;font-size:13px}
.links{display:flex;flex-wrap:wrap;gap:16px;margin-top:14px}
@media(max-width:600px){.features{grid-template-columns:1fr}.card{padding:18px}.hero{padding-top:35px}}
</style>
</head>
<body>
<header>
<div class="container nav">
<a class="brand" href="/"><span class="logo">▶</span>SnapVideo</a>
<a class="muted" href="#how">كيفاش كيخدم؟</a>
</div>
</header>
<main class="container">
<section class="hero">
<div class="muted">منصة بسيطة وسهلة الاستعمال</div>
<h1>{{ heading }}</h1>
<p>لسق رابط TikTok، واضغط على زر التحميل. واجهة بسيطة ومتوافقة مع الهاتف والكمبيوتر.</p>
</section>

<div class="ad">مساحة إعلانية</div>

{% if page == "home" %}
<section class="card">
<div class="platform">♪ TikTok فقط</div>
<form action="/download" method="post">
<label for="video-url">رابط فيديو TikTok</label>
<input id="video-url" type="url" name="url"
placeholder="https://www.tiktok.com/..." required maxlength="2000">
<button type="submit">↓ تحميل الفيديو</button>
</form>
{% if error %}<div class="message" role="alert">{{ error }}</div>{% endif %}
<div class="notice">
استعمل الخدمة مع الفيديوهات التي تملكها أو لديك إذن بتنزيلها، واحترم حقوق النشر وشروط TikTok.
بعض الروابط قد لا تكون متاحة.
</div>
</section>

<section class="features">
<article class="feature"><strong>⚡ واجهة سهلة</strong><p>خطوات واضحة وبسيطة.</p></article>
<article class="feature"><strong>📱 مناسب للهاتف</strong><p>تصميم متجاوب مع مختلف الشاشات.</p></article>
<article class="feature"><strong>♪ TikTok</strong><p>مصمم للتعامل مع روابط TikTok فقط.</p></article>
</section>

<section id="how">
<h2>كيفاش تستعمل SnapVideo؟</h2>
<p class="description">1. نسخ رابط فيديو TikTok. 2. لصق الرابط في الخانة. 3. الضغط على تحميل الفيديو وانتظار النتيجة. قد تفشل بعض الروابط بسبب قيود المنصة.</p>
</section>
{% else %}
<section class="card">
<h2>{{ heading }}</h2>
<p class="description">{{ body }}</p>
</section>
{% endif %}
<div class="ad">مساحة إعلانية</div>
</main>
<footer><div class="container">
<strong>SnapVideo</strong><p>© 2026 SnapVideo</p>
<div class="links">
<a href="/">الرئيسية</a><a href="/about">من نحن</a>
<a href="/privacy">سياسة الخصوصية</a><a href="/contact">اتصل بنا</a>
<a href="/sitemap.xml">خريطة الموقع</a>
</div></div></footer>
</body>
</html>
"""

def render_page(page="home", heading="تحميل فيديوهات TikTok",
                body="", error=None, title="تحميل TikTok"):
    return render_template_string(
        HTML, page=page, heading=heading, body=body,
        error=error, title=title,
        verification=GOOGLE_VERIFICATION
    )

def allowed_tiktok_url(url):
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
    except ValueError:
        return False

    if parsed.scheme not in ("http", "https"):
        return False

    if not re.fullmatch(r"[a-z0-9.-]+", host):
        return False

    domains = (
        "tiktok.com",
        "tiktokv.com",
        "tiktokcdn.com",
    )
    return any(host == d or host.endswith("." + d) for d in domains)

@app.route("/")
def home():
    return render_page()

@app.route("/about")
def about():
    return render_page(
        page="info", heading="من نحن", title="من نحن",
        body="SnapVideo واجهة للتعامل مع روابط TikTok المتاحة. لا ندّعي ملكية الفيديوهات الموجودة على المنصة."
    )

@app.route("/privacy")
def privacy():
    return render_page(
        page="info", heading="سياسة الخصوصية", title="سياسة الخصوصية",
        body="يتم إرسال رابط الفيديو الذي تدخله لمعالجة طلبك. قد تحتفظ الاستضافة بسجلات تقنية. لا تدخل معلومات شخصية حساسة. يجب تحديث هذه السياسة إذا أضفت خدمات تحليل أو إعلانات."
    )

@app.route("/contact")
def contact():
    return render_page(
        page="info", heading="اتصل بنا", title="اتصل بنا",
        body="للاستفسارات أو الإبلاغ عن مشكلة، أضف وسيلة اتصال رسمية خاصة بصاحب الموقع."
    )

@app.route("/robots.txt")
def robots():
    return Response(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
        mimetype="text/plain"
    )

@app.route("/sitemap.xml")
def sitemap():
    paths = ("/", "/about", "/privacy", "/contact")
    entries = "".join(
        f"<url><loc>{SITE_URL}{path}</loc></url>" for path in paths
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + entries + '</urlset>'
    )
    return Response(xml, mimetype="application/xml")

@app.route("/download", methods=["POST"])
def download():
    video_url = request.form.get("url", "").strip()

    if len(video_url) > 2000:
        return render_page(error="الرابط طويل بزاف.")

    if not allowed_tiktok_url(video_url):
        return render_page(error="دخل رابط TikTok صحيح.")

    temp_dir = tempfile.mkdtemp(prefix="snapvideo_")

    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": os.path.join(temp_dir, "video.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "max_filesize": 100 * 1024 * 1024,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([video_url])

        files = [
            os.path.join(temp_dir, name)
            for name in os.listdir(temp_dir)
            if os.path.isfile(os.path.join(temp_dir, name))
        ]

        if not files:
            raise RuntimeError("No output file created")

        file_path = max(files, key=os.path.getsize)
        filename = "SnapVideo" + os.path.splitext(file_path)[1]

        response = send_file(
            file_path, as_attachment=True, download_name=filename
        )
        response.call_on_close(
            lambda: shutil.rmtree(temp_dir, ignore_errors=True)
        )
        return response

    except Exception:
        app.logger.exception("TikTok download failed")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return render_page(
            error="تعذر تنزيل هذا الفيديو. جرّب رابطاً عمومياً آخر؛ بعض الفيديوهات لا يمكن تنزيلها."
        )

@app.errorhandler(413)
def too_large(_error):
    return render_page(error="حجم الطلب كبير بزاف."), 413

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
