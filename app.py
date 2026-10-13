
import os
import shutil
import tempfile
from datetime import datetime
from urllib.parse import urlparse

from flask import (
    Flask, request, redirect, url_for,
    render_template_string, send_file, flash
)
import yt_dlp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), "viddrop")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HTML = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#ffffff">
<meta name="description" content="VidDrop أداة بسيطة لمعالجة روابط فيديوهات TikTok المتاحة للتحميل.">
<title>{{ title }} | VidDrop</title>
<style>
:root {
    --pink: #ed1760;
    --pink-dark: #cf104e;
    --ink: #24232b;
    --muted: #737582;
    --bg: #ffffff;
    --soft: #fff3f7;
    --border: #eee8ec;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: Arial, Tahoma, sans-serif;
    line-height: 1.8;
}
a { text-decoration: none; }
header {
    height: 76px;
    padding: 0 6%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    border-bottom: 1px solid var(--border);
    background: white;
}
.logo {
    font-size: 29px;
    font-weight: 900;
    color: var(--pink);
    letter-spacing: -1px;
}
.logo span { color: var(--ink); }
nav { display: flex; gap: 23px; }
nav a { color: #45434b; font-size: 14px; }
nav a:hover { color: var(--pink); }
.hero {
    text-align: center;
    padding: 66px 18px 55px;
    background: linear-gradient(180deg, #fff2f7 0%, #fff 100%);
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
    font-size: 16px;
}
.download-box {
    max-width: 760px;
    margin: 0 auto;
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
    border: none;
    outline: none;
    background: transparent;
    color: var(--ink);
    font-size: 15px;
}
button {
    border: none;
    border-radius: 10px;
    background: var(--pink);
    color: white;
    font-size: 16px;
    font-weight: bold;
    padding: 13px 25px;
    cursor: pointer;
}
button:hover { background: var(--pink-dark); }
button:disabled { opacity: .6; cursor: wait; }
.hint { font-size: 12px; color: #85818a; margin-top: 15px; }
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
.card .icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 46px;
    height: 46px;
    border-radius: 12px;
    background: var(--soft);
    font-size: 23px;
}
.card h3 { font-size: 18px; margin: 12px 0 5px; }
.card p { color: var(--muted); font-size: 14px; margin: 0; }
.steps { max-width: 720px; margin: auto; }
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
.step p { margin: 0; color: var(--muted); font-size: 14px; }
.faq { max-width: 780px; margin: auto; }
details {
    border-bottom: 1px solid var(--border);
    padding: 17px 5px;
}
summary { cursor: pointer; font-weight: bold; }
details p { color: var(--muted); font-size: 14px; }
.info {
    max-width: 850px;
    margin: 45px auto;
    padding: 28px;
    border: 1px solid var(--border);
    border-radius: 15px;
}
.info h1 { font-size: 29px; }
.info p { color: #5f5d66; }
.info a { color: var(--pink); }
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
@media(max-width:700px) {
    header { height: auto; padding: 15px; flex-direction: column; gap: 8px; }
    nav { gap: 14px; flex-wrap: wrap; justify-content: center; }
    .hero { padding: 45px 15px 35px; }
    .download-box { flex-direction: column; }
    .download-box input { padding: 13px 10px; width: 100%; }
    .download-box button { width: 100%; }
    .cards { grid-template-columns: 1fr; }
    .section { padding: 35px 16px; }
    .info { margin: 25px 15px; padding: 20px; }
}
</style>
</head>
<body>

<header>
    <a class="logo" href="/">Vid<span>Drop</span></a>
    <nav>
        <a href="/">الرئيسية</a>
        <a href="#how">طريقة الاستعمال</a>
        <a href="#features">المميزات</a>
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
    <h1>حمّل فيديوهات TikTok مع<br><span class="pink">VidDrop</span></h1>
    <p class="subtitle">
        طريقة سهلة لمعالجة روابط الفيديوهات المتاحة للتحميل.
        لسق الرابط ديالك وجرب.
    </p>

    <form class="download-box" action="/download" method="post"
          onsubmit="this.querySelector('button').disabled=true;
          this.querySelector('button').textContent='جاري المعالجة...';">
        <input type="url" name="video_url"
               placeholder="لسق رابط TikTok هنا..."
               aria-label="رابط فيديو TikTok" required>
        <button type="submit">تحميل الفيديو ↓</button>
    </form>
    <p class="hint">
        استعمل الخدمة غير للفيديوهات ديالك أو المحتوى اللي عندك الإذن بتحميله.
    </p>
</section>

<section class="section" id="features">
    <h2>علاش تستعمل <span class="pink">VidDrop</span>؟</h2>
    <p class="section-intro">واجهة بسيطة باش تسهّل عليك التعامل مع روابط الفيديو.</p>
    <div class="cards">
        <article class="card">
            <div class="icon">⚡</div>
            <h3>سهل وسريع</h3>
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
    <h2>كيفاش تحمّل الفيديو؟</h2>
    <p class="section-intro">ثلاث خطوات بسيطة.</p>
    <div class="steps">
        <div class="step">
            <div class="number">1</div>
            <div><h3>نسخ الرابط</h3><p>نسخ رابط فيديو متاح للتحميل وعندك الحق تستعمله.</p></div>
        </div>
        <div class="step">
            <div class="number">2</div>
            <div><h3>لصق الرابط</h3><p>حط الرابط فالمربع الموجود فوق الصفحة.</p></div>
        </div>
        <div class="step">
            <div class="number">3</div>
            <div><h3>بدا المعالجة</h3><p>ضغط على زر التحميل وانتظر النتيجة.</p></div>
        </div>
    </div>
</section>

<section class="section">
    <h2>الأسئلة الشائعة</h2>
    <div class="faq">
        <details>
            <summary>واش جميع الروابط كتخدم؟</summary>
            <p>لا، النتيجة كتختلف حسب توفر الفيديو ودعم أداة المعالجة وتغييرات المنصة.</p>
        </details>
        <details>
            <summary>واش خاصني حساب؟</summary>
            <p>هاد الواجهة ما كتطلبش إنشاء حساب للاستعمال الأساسي.</p>
        </details>
        <details>
            <summary>واش نقدر نحمل أي فيديو؟</summary>
            <p>حمّل غير المحتوى ديالك أو اللي عندك إذن بتحميله، واحترم حقوق النشر وشروط المنصة.</p>
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
    <a class="logo" href="/">Vid<span>Drop</span></a>
    <p>أداة بسيطة لمعالجة روابط الفيديوهات المتاحة للتحميل.</p>
    <div class="footer-links">
        <a href="/">الرئيسية</a>
        <a href="/about">من نحن</a>
        <a href="/privacy">سياسة الخصوصية</a>
        <a href="/terms">شروط الاستخدام</a>
        <a href="/contact">اتصل بنا</a>
    </div>
    <p>© {{ year }} VidDrop</p>
</footer>

</body>
</html>
"""


def render_page(title, page="info", heading="", body=""):
    return render_template_string(
        HTML,
        title=title,
        page=page,
        heading=heading,
        body=body,
        year=datetime.now().year
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
            "vt.tiktok.com",
        }
        return (
            parsed.scheme == "https"
            and host in allowed
            and not parsed.username
            and not parsed.password
        )
    except (ValueError, AttributeError):
        return False


@app.route("/")
def home():
    return render_page("تحميل فيديوهات TikTok", page="home")


@app.route("/download", methods=["POST"])
def download():
    video_url = request.form.get("video_url", "").strip()

    if not is_valid_tiktok_url(video_url):
        flash("دخل رابط TikTok صحيح كيبدا بـ https://")
        return redirect(url_for("home"))

    job_dir = tempfile.mkdtemp(prefix="job_", dir=DOWNLOAD_DIR)

    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": os.path.join(job_dir, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 20,
        "retries": 1,
        "restrictfilenames": True,
        "max_filesize": 100 * 1024 * 1024,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

        if not os.path.isfile(filename):
            files = [
                os.path.join(job_dir, name)
                for name in os.listdir(job_dir)
                if os.path.isfile(os.path.join(job_dir, name))
            ]
            if not files:
                raise RuntimeError("No output file")
            filename = files[0]

        response = send_file(
            filename,
            as_attachment=True,
            download_name=os.path.basename(filename),
            mimetype="application/octet-stream"
        )

        # حذف الملف المؤقت بعد إرسال الاستجابة
        response.call_on_close(
            lambda: shutil.rmtree(job_dir, ignore_errors=True)
        )
        return response

    except Exception:
        shutil.rmtree(job_dir, ignore_errors=True)
        flash("تعذّر تحميل الفيديو. تأكد من الرابط وجرب مرة أخرى.")
        return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_page(
        "من نحن",
        heading="من نحن",
        body="<p>VidDrop مشروع بسيط لمعالجة روابط الفيديوهات المتاحة للتحميل.</p>"
             "<p>الخدمة ما كتضمنش أن جميع الروابط غادي تخدم.</p>"
    )


@app.route("/privacy")
def privacy():
    return render_page(
        "سياسة الخصوصية",
        heading="سياسة الخصوصية",
        body="<p>الرابط اللي كتدخلو كيتعالج لمحاولة جلب الفيديو. "
             "قد تسجل الاستضافة بعض المعلومات التقنية.</p>"
             "<p>قبل النشر العمومي، راجع إعدادات السجلات وحماية البيانات "
             "وسياسة الاحتفاظ بالملفات المؤقتة.</p>"
    )


@app.route("/terms")
def terms():
    return render_page(
        "شروط الاستخدام",
        heading="شروط الاستخدام",
        body="<p>استعمل الموقع فقط للمحتوى ديالك أو المحتوى اللي عندك "
             "الإذن بتحميله. احترم حقوق النشر وشروط المنصة.</p>"
             "<p>ممنوع استعمال الموقع للوصول إلى محتوى خاص أو تجاوز "
             "قيود الوصول.</p>"
    )


@app.route("/contact")
def contact():
    return render_page(
        "اتصل بنا",
        heading="اتصل بنا",
        body="<p>تواصل مع إدارة VidDrop عبر عنوان البريد الإلكتروني "
             "الذي سيضيفه صاحب الموقع هنا قبل الإطلاق.</p>"
    )


@app.route("/health")
def health():
    return {"status": "ok", "service": "VidDrop"}


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
