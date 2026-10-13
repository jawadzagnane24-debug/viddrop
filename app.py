
import os
import re
import shutil
import tempfile
from urllib.parse import urlparse
from xml.sax.saxutils import escape

from flask import (
    Flask,
    Response,
    abort,
    render_template_string,
    request,
    send_file,
)
import yt_dlp

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

SITE_URL = "https://brave-cedar-7334.de.deplexo.com"
SITE_NAME = "SnapVideo"
GOOGLE_VERIFICATION = (
    "nwb3Nxl9qGs1VLeuGiOUE4YM2Vw0yh5rxD0dMEXNm8M"
)

HTML = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <meta name="google-site-verification"
          content="{{ google_verification }}">
    <meta name="description"
          content="SnapVideo - واجهة سهلة لتحميل الفيديوهات من الروابط المدعومة.">
    <meta name="robots" content="index,follow">
    <meta name="theme-color" content="#0b0b0f">

    <title>{{ title }} | SnapVideo</title>

    <style>
        :root {
            color-scheme: dark;
            --bg: #0b0b0f;
            --panel: #15151c;
            --border: #2c2c37;
            --red: #f22e46;
            --text: #f8f8fc;
            --muted: #aaaab8;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            background:
                radial-gradient(ellipse at top, #241018 0, transparent 48%),
                var(--bg);
            color: var(--text);
            font-family: Arial, Tahoma, sans-serif;
            min-height: 100vh;
        }

        a { color: inherit; text-decoration: none; }

        .container {
            width: min(100% - 32px, 980px);
            margin-inline: auto;
        }

        header {
            border-bottom: 1px solid var(--border);
            background: rgba(11, 11, 15, .92);
        }

        .nav {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding-block: 18px;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 23px;
            font-weight: 800;
        }

        .brand-icon {
            display: grid;
            place-items: center;
            width: 42px;
            height: 42px;
            border-radius: 13px;
            background: var(--red);
            color: white;
        }

        .nav a:last-child {
            color: var(--muted);
            font-size: 14px;
        }

        .hero {
            padding: 62px 0 32px;
            text-align: center;
        }

        .eyebrow {
            display: inline-block;
            padding: 8px 13px;
            border: 1px solid #51212b;
            border-radius: 99px;
            background: #241117;
            color: #ff9ca8;
            font-size: 13px;
        }

        h1 {
            margin: 20px 0 12px;
            font-size: clamp(30px, 6vw, 48px);
            line-height: 1.35;
        }

        .hero p {
            max-width: 620px;
            margin: auto;
            color: var(--muted);
            line-height: 1.9;
        }

        .card {
            max-width: 700px;
            margin: 0 auto 30px;
            padding: clamp(18px, 4vw, 32px);
            border: 1px solid var(--border);
            border-radius: 22px;
            background: rgba(21, 21, 28, .96);
            box-shadow: 0 18px 60px rgba(0, 0, 0, .25);
        }

        .platforms {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 22px;
        }

        .platform {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 9px;
            min-height: 54px;
            border: 1px solid var(--border);
            border-radius: 12px;
            background: #101016;
            color: var(--text);
            font-size: 16px;
            cursor: pointer;
        }

        .platform.active {
            border-color: var(--red);
            background: #32121b;
            box-shadow: inset 0 0 0 1px var(--red);
        }

        label {
            display: block;
            margin-bottom: 10px;
            font-size: 14px;
        }

        input[type=url] {
            width: 100%;
            min-height: 54px;
            padding: 14px;
            border: 1px solid #393946;
            border-radius: 12px;
            outline: none;
            background: #0d0d12;
            color: white;
            font-size: 15px;
            direction: ltr;
            text-align: left;
        }

        input[type=url]:focus {
            border-color: var(--red);
        }

        .submit {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            width: 100%;
            min-height: 54px;
            margin-top: 14px;
            border: 0;
            border-radius: 12px;
            background: var(--red);
            color: white;
            font-size: 17px;
            font-weight: 700;
            cursor: pointer;
        }

        .submit:hover { background: #d92139; }

        .notice {
            margin-top: 18px;
            padding: 13px;
            border-radius: 10px;
            background: #101016;
            color: var(--muted);
            font-size: 13px;
            line-height: 1.8;
        }

        .message {
            margin-top: 16px;
            padding: 14px;
            border-radius: 10px;
            background: #32121b;
            color: #ffb7c0;
            line-height: 1.8;
        }

        .ad {
            display: grid;
            place-items: center;
            min-height: 80px;
            margin: 22px auto;
            border: 1px dashed #363641;
            border-radius: 12px;
            color: #777784;
            font-size: 13px;
        }

        .features {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin: 32px 0;
        }

        .feature {
            padding: 20px 14px;
            border: 1px solid var(--border);
            border-radius: 15px;
            background: #131319;
        }

        .feature strong {
            display: block;
            margin: 10px 0 7px;
        }

        .feature p {
            margin: 0;
            color: var(--muted);
            font-size: 13px;
            line-height: 1.8;
        }

        .section-title {
            margin-top: 38px;
            font-size: 24px;
        }

        .description {
            color: var(--muted);
            line-height: 2;
        }

        footer {
            margin-top: 55px;
            border-top: 1px solid var(--border);
            padding: 24px 0;
            color: var(--muted);
            font-size: 13px;
        }

        .footer-links {
            display: flex;
            flex-wrap: wrap;
            gap: 18px;
            margin-top: 14px;
        }

        .footer-links a:hover { color: white; }

        @media (max-width: 600px) {
            .hero { padding-top: 42px; }
            .features { grid-template-columns: 1fr; }
            .feature { padding: 16px; }
            .nav { padding-block: 14px; }
        }
    </style>
</head>
<body>
<header>
    <div class="container nav">
        <a class="brand" href="/" aria-label="SnapVideo الصفحة الرئيسية">
            <span class="brand-icon">▶</span>
            <span>SnapVideo</span>
        </a>
        <a href="#how">كيفاش كيخدم؟</a>
    </div>
</header>

<main class="container">
    <section class="hero">
        <span class="eyebrow">منصة بسيطة وسهلة الاستعمال</span>
        <h1>{{ heading }}</h1>
        <p>
            اختار المنصة، لسق رابط الفيديو، واتبع التعليمات.
            واجهة بسيطة ومتوافقة مع الهاتف والكمبيوتر.
        </p>
    </section>

    <div class="ad" aria-label="مساحة إعلانية">
        مساحة إعلانية
    </div>

    {% if page == "home" %}
    <section class="card">
        <form action="/download" method="post">
            <div class="platforms">
                <button type="button" class="platform active"
                        id="youtube" onclick="choosePlatform('youtube')">
                    ▶ YouTube
                </button>
                <button type="button" class="platform"
                        id="tiktok" onclick="choosePlatform('tiktok')">
                    ♪ TikTok
                </button>
            </div>

            <input type="hidden" name="platform" id="platform"
                   value="youtube">

            <label for="video-url">رابط الفيديو</label>
            <input id="video-url" type="url" name="url"
                   placeholder="https://..." required
                   maxlength="2000"
                   autocomplete="url">

            <button class="submit" type="submit">
                <span>↓</span>
                <span>تحميل الفيديو</span>
            </button>
        </form>

        {% if error %}
        <div class="message" role="alert">{{ error }}</div>
        {% endif %}

        <div class="notice">
            استعمل الخدمة فقط مع الفيديوهات التي تملكها أو لديك إذن
            بتنزيلها. احترم حقوق النشر وشروط المنصات.
        </div>
    </section>

    <section class="features">
        <article class="feature">
            <span>⚡</span>
            <strong>واجهة سهلة</strong>
            <p>خطوات واضحة وبسيطة للمستخدم.</p>
        </article>
        <article class="feature">
            <span>📱</span>
            <strong>مناسب للهاتف</strong>
            <p>تصميم متجاوب مع مختلف الشاشات.</p>
        </article>
        <article class="feature">
            <span>🔗</span>
            <strong>لصق الرابط</strong>
            <p>أدخل رابطاً مدعوماً وابدأ العملية.</p>
        </article>
    </section>

    <section id="how">
        <h2 class="section-title">كيفاش تستعمل SnapVideo؟</h2>
        <p class="description">
            1. اختار المنصة المدعومة.
            2. لسق رابط الفيديو في الخانة.
            3. اضغط على زر التحميل وانتظر النتيجة.
            قد لا تعمل بعض الروابط بسبب قيود المنصة أو تغييراتها.
        </p>
    </section>
    {% else %}
    <section class="card">
        <h2>{{ heading }}</h2>
        <div class="description">{{ body }}</div>
    </section>
    {% endif %}

    <div class="ad" aria-label="مساحة إعلانية">
        مساحة إعلانية
    </div>
</main>

<footer>
    <div class="container">
        <strong>SnapVideo</strong>
        <div>© 2026 SnapVideo</div>
        <div class="footer-links">
            <a href="/">الرئيسية</a>
            <a href="/about">من نحن</a>
            <a href="/privacy">سياسة الخصوصية</a>
            <a href="/contact">اتصل بنا</a>
            <a href="/sitemap.xml">خريطة الموقع</a>
        </div>
    </div>
</footer>

<script>
function choosePlatform(platform) {
    document.getElementById("platform").value = platform;
    document.getElementById("youtube").classList.toggle(
        "active", platform === "youtube"
    );
    document.getElementById("tiktok").classList.toggle(
        "active", platform === "tiktok"
    );
}
</script>
</body>
</html>
"""


def render_page(page="home", heading="تنزيل فيديوهات بسهولة",
                body="", error=None, title="تنزيل فيديوهات بسهولة"):
    return render_template_string(
        HTML,
        page=page,
        heading=heading,
        body=body,
        error=error,
        title=title,
        google_verification=GOOGLE_VERIFICATION,
    )


def allowed_video_url(url, platform):
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
    except ValueError:
        return False

    if parsed.scheme not in ("http", "https"):
        return False

    if not host or not re.fullmatch(r"[a-z0-9.-]+", host):
        return False

    domains = {
        "youtube": ("youtube.com", "youtu.be"),
        "tiktok": ("tiktok.com",),
    }

    return any(
        host == domain or host.endswith("." + domain)
        for domain in domains.get(platform, ())
    )


@app.route("/")
def home():
    return render_page()


@app.route("/about")
def about():
    return render_page(
        page="info",
        heading="من نحن",
        title="من نحن",
        body=(
            "SnapVideo واجهة ويب تساعد المستخدمين على التعامل مع "
            "روابط الفيديوهات المدعومة. لا ندّعي ملكية الفيديوهات "
            "الموجودة على المنصات الأخرى."
        ),
    )


@app.route("/privacy")
def privacy():
    return render_page(
        page="info",
        heading="سياسة الخصوصية",
        title="سياسة الخصوصية",
        body=(
            "يرجى عدم إرسال معلومات شخصية حساسة. تتم معالجة رابط "
            "الفيديو الذي تدخله من أجل تنفيذ طلبك. قد تحتفظ خدمة "
            "الاستضافة بسجلات تقنية وفق إعداداتها. يجب تحديث هذه "
            "السياسة بما يعكس فعلياً أي تحليلات أو ملفات تعريف ارتباط "
            "أو خدمات خارجية تستعملها قبل نشر الموقع للعامة."
        ),
    )


@app.route("/contact")
def contact():
    return render_page(
        page="info",
        heading="اتصل بنا",
        title="اتصل بنا",
        body=(
            "للاستفسارات أو للإبلاغ عن مشكلة، تواصل مع صاحب الموقع "
            "عبر وسيلة اتصال يضيفها مدير الموقع هنا."
        ),
    )


@app.route("/robots.txt")
def robots():
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    return Response(content, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    urls = [
        "/",
        "/about",
        "/privacy",
        "/contact",
    ]
    entries = "\n".join(
        f"<url><loc>{escape(SITE_URL + path)}</loc></url>"
        for path in urls
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{entries}</urlset>"
    )
    return Response(xml, mimetype="application/xml")


@app.route("/download", methods=["POST"])
def download():
    video_url = request.form.get("url", "").strip()
    platform = request.form.get("platform", "youtube").lower()

    if len(video_url) > 2000:
        return render_page(error="الرابط طويل بزاف.")

    if not allowed_video_url(video_url, platform):
        return render_page(
            error="دخل رابطاً صحيحاً من المنصة اللي اخترتي."
        )

    temp_dir = tempfile.mkdtemp(prefix="snapvideo_")

    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": os.path.join(temp_dir, "video.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 25,
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
            raise RuntimeError("لم يتم إنشاء ملف فيديو.")

        file_path = max(files, key=os.path.getsize)
        filename = "SnapVideo" + os.path.splitext(file_path)[1]

        response = send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
        )
        response.call_on_close(
            lambda: shutil.rmtree(temp_dir, ignore_errors=True)
        )
        return response

    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return render_page(
            error=(
                "تعذر تنزيل الفيديو. تأكد من الرابط، وجرب لاحقاً. "
                "قد لا تكون بعض الفيديوهات متاحة للتنزيل."
            )
        )


@app.errorhandler(413)
def request_too_large(_error):
    return render_page(error="حجم الطلب كبير بزاف."), 413


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
