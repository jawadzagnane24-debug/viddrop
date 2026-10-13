
import os
import re
import shutil
import tempfile
from urllib.parse import urlparse

from flask import (
    Flask, request, render_template_string,
    send_file, flash, redirect, url_for
)
import yt_dlp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "viddrop-change-this-key")

DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), "viddrop")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HTML = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} - VidDrop</title>
<style>
*{box-sizing:border-box}
body{margin:0;font-family:Arial,Tahoma,sans-serif;background:#101014;color:#fff;line-height:1.8}
header{padding:18px 6%;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #292932}
.logo{font-size:27px;font-weight:bold;color:#ff3158;text-decoration:none}
nav a{color:#ddd;text-decoration:none;margin:0 8px;font-size:14px}
nav a:hover{color:#ff3158}
.hero{text-align:center;padding:65px 18px 45px;background:radial-gradient(ellipse at top,#35131f,#101014 68%)}
h1{font-size:clamp(30px,5vw,48px);line-height:1.4;margin:0 0 15px}
.pink{color:#ff3158}
.subtitle{color:#c5c5cf;max-width:650px;margin:0 auto 28px}
.form{max-width:720px;margin:0 auto;display:flex;gap:10px;padding:9px;background:#202027;border:1px solid #393943;border-radius:15px}
.form input{flex:1;min-width:0;background:transparent;border:0;outline:none;color:white;padding:12px;font-size:16px}
button{background:#ff3158;color:white;border:0;border-radius:10px;padding:13px 22px;font-size:16px;font-weight:bold;cursor:pointer}
button:hover{background:#e82149}
.notice{max-width:700px;margin:18px auto 0;color:#aaa;font-size:13px}
.container{max-width:1000px;margin:auto;padding:35px 18px}
h2{text-align:center;font-size:28px;margin-bottom:25px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}
.card{background:#1b1b22;border:1px solid #30303a;border-radius:15px;padding:22px}
.card h3{margin-top:0;color:#ff5474}
.card p{color:#c4c4cd;margin-bottom:0}
.steps{max-width:650px;margin:auto}
.step{padding:15px 18px;margin:12px 0;background:#1b1b22;border-radius:12px}
.step b{color:#ff5474}
.content{max-width:800px;margin:35px auto;padding:25px;background:#1b1b22;border-radius:15px}
.content a{color:#ff6680}
.alert{max-width:720px;margin:15px auto;padding:12px 16px;border-radius:10px;background:#35212a;color:#ffd9e1}
footer{text-align:center;padding:25px 12px;border-top:1px solid #292932;color:#999}
footer a{color:#ccc;text-decoration:none;margin:0 7px}
@media(max-width:600px){header{flex-direction:column;gap:10px}.form{flex-direction:column}.form input{width:100%}.form button{width:100%}.hero{padding-top:45px}}
</style>
</head>
<body>
<header>
<a class="logo" href="/">VidDrop</a>
<nav>
<a href="/">الرئيسية</a>
<a href="/about">من نحن</a>
<a href="/privacy">الخصوصية</a>
<a href="/contact">اتصل بنا</a>
</nav>
</header>

{% with messages = get_flashed_messages() %}
{% if messages %}
{% for message in messages %}
<div class="alert">{{ message }}</div>
{% endfor %}
{% endif %}
{% endwith %}

{% if page == 'home' %}
<section class="hero">
<h1>حمّل فيديوهاتك بسهولة مع <span class="pink">VidDrop</span></h1>
<p class="subtitle">أداة بسيطة لمعالجة روابط فيديوهات TikTok المتاحة للتحميل. سريعة وسهلة الاستعمال، وبدون الحاجة إلى إنشاء حساب.</p>
<form class="form" action="/download" method="post">
<input type="url" name="video_url" placeholder="لسق رابط فيديو TikTok هنا..." required>
<button type="submit">معالجة الرابط</button>
</form>
<p class="notice">استعمل الخدمة فقط للفيديوهات ديالك أو المحتوى اللي عندك الإذن بتحميله. نجاح المعالجة كيعتمد على توفر الفيديو وسياسات المنصة.</p>
</section>

<section class="container">
<h2>علاش تختار <span class="pink">VidDrop</span>؟</h2>
<div class="cards">
<div class="card"><h3>⚡ سهل الاستعمال</h3><p>لسق الرابط واضغط على الزر باش تبدأ معالجة الفيديو.</p></div>
<div class="card"><h3>📱 مناسب للهاتف</h3><p>واجهة كتخدم على الهاتف والكمبيوتر.</p></div>
<div class="card"><h3>🔒 بدون حساب</h3><p>ما محتاجش تنشئ حساب باش تستعمل الواجهة.</p></div>
</div>
</section>

<section class="container">
<h2>كيفاش تستعمل الموقع؟</h2>
<div class="steps">
<div class="step"><b>1.</b> نسخ رابط الفيديو اللي عندك الحق تحمّلو.</div>
<div class="step"><b>2.</b> لسق الرابط فالمربع اللي فوق.</div>
<div class="step"><b>3.</b> ضغط على «معالجة الرابط» وانتظر النتيجة.</div>
</div>
</section>
{% else %}
<div class="content">
<h1 style="font-size:30px">{{ heading }}</h1>
{{ body|safe }}
</div>
{% endif %}

<footer>
<p>© {{ year }} VidDrop — جميع الحقوق محفوظة</p>
<a href="/">الرئيسية</a>
<a href="/terms">شروط الاستخدام</a>
<a href="/privacy">الخصوصية</a>
<a href="/contact">اتصل بنا</a>
</footer>
</body>
</html>
"""


def valid_tiktok_url(value):
    try:
        parsed = urlparse(value.strip())
        host = (parsed.hostname or "").lower()
        allowed_hosts = {
            "tiktok.com", "www.tiktok.com", "m.tiktok.com",
            "vm.tiktok.com", "vt.tiktok.com"
        }
        return (
            parsed.scheme == "https"
            and host in allowed_hosts
            and parsed.username is None
            and parsed.password is None
        )
    except Exception:
        return False


def page(title, heading="", body="", page_name="info"):
    return render_template_string(
        HTML,
        title=title,
        heading=heading,
        body=body,
        page=page_name,
        year=__import__("datetime").datetime.now().year
    )


@app.route("/")
def home():
    return render_template_string(
        HTML, title="تحميل فيديوهات TikTok",
        heading="", body="", page="home",
        year=__import__("datetime").datetime.now().year
    )


@app.route("/download", methods=["POST"])
def download():
    video_url = request.form.get("video_url", "").strip()

    if not valid_tiktok_url(video_url):
        flash("عافاك دخل رابط TikTok صحيح كيبدا بـ https://")
        return redirect(url_for("home"))

    # مجلد مؤقت منفصل لكل عملية تحميل
    job_dir = tempfile.mkdtemp(prefix="viddrop_", dir=DOWNLOAD_DIR)

    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": os.path.join(job_dir, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 20,
        "retries": 1,
        "max_filesize": 100 * 1024 * 1024,
        "restrictfilenames": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

        if not os.path.isfile(filename):
            candidates = [
                os.path.join(job_dir, name)
                for name in os.listdir(job_dir)
                if os.path.isfile(os.path.join(job_dir, name))
            ]
            if not candidates:
                raise RuntimeError("ما تلقاش ملف الفيديو بعد المعالجة.")
            filename = candidates[0]

        return send_file(
            filename,
            as_attachment=True,
            download_name=os.path.basename(filename),
            mimetype="application/octet-stream"
        )

    except Exception:
        shutil.rmtree(job_dir, ignore_errors=True)
        flash("ما قدرناش نعالجو هاد الرابط. تأكد أن الفيديو متاح وجرب من جديد.")
        return redirect(url_for("home"))


@app.route("/about")
def about():
    return page(
        "من نحن",
        "من نحن",
        "<p>VidDrop واجهة بسيطة لتسهيل معالجة روابط الفيديوهات المتاحة للتحميل.</p>"
        "<p>الخدمة غير مضمونة لجميع الروابط، وقد تتوقف إذا تغيرت المنصة أو طريقة الوصول للفيديو.</p>"
    )


@app.route("/privacy")
def privacy():
    return page(
        "سياسة الخصوصية",
        "سياسة الخصوصية",
        "<p>ما تدخلش معلومات شخصية حساسة فالموقع.</p>"
        "<p>الرابط اللي كتدخلو كيتعالج باش نحاولو نجيبو الفيديو. خاص صاحب الموقع يراجع إعدادات الاستضافة والسجلات والملفات المؤقتة قبل النشر العمومي.</p>"
    )


@app.route("/terms")
def terms():
    return page(
        "شروط الاستخدام",
        "شروط الاستخدام",
        "<p>استعمل VidDrop غير للمحتوى ديالك أو المحتوى اللي عندك إذن قانوني بتحميله.</p>"
        "<p>ممنوع استعمال الخدمة للوصول إلى محتوى خاص أو تجاوز قيود الوصول، واحترم حقوق النشر وشروط المنصة.</p>"
    )


@app.route("/contact")
def contact():
    return page(
        "اتصل بنا",
        "اتصل بنا",
        "<p>للتواصل مع إدارة الموقع، زِد عنوان بريد إلكتروني خاص بالمشروع هنا قبل نشر الموقع.</p>"
    )


@app.route("/health")
def health():
    return {"status": "ok", "service": "VidDrop"}


@app.errorhandler(404)
def not_found(error):
    return page(
        "الصفحة غير موجودة",
        "الصفحة غير موجودة",
        '<p>الصفحة اللي كتقلب عليها ما كايناش.</p><p><a href="/">رجع للرئيسية</a></p>'
    ), 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        debug=False
    )
