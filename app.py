
import os
import tempfile
import shutil
from flask import Flask, request, render_template_string, send_file
import yt_dlp

app = Flask(__name__)

GOOGLE_VERIFICATION = (
    "nwb3Nxl9qGs1VLeuGiOUE4YM2Vw0yh5rxD0dMEXNm8M"
)

HTML = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#090909">
    <meta name="google-site-verification"
          content="{{ google_verification }}">
    <title>VidDrop - تنزيل فيديوهات بسهولة</title>

    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --red: #ff3040;
            --bg: #090909;
            --card: #151515;
            --border: #292929;
            --text: #ffffff;
            --muted: #a3a3a3;
        }

        body {
            background:
                radial-gradient(
                    ellipse at top,
                    #351014 0%,
                    transparent 45%
                ),
                var(--bg);
            color: var(--text);
            font-family: Arial, Tahoma, sans-serif;
            min-height: 100vh;
            line-height: 1.7;
        }

        .container {
            width: min(1000px, 92%);
            margin: auto;
        }

        header {
            border-bottom: 1px solid var(--border);
            background: rgba(9, 9, 9, 0.92);
        }

        .navbar {
            min-height: 76px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 15px;
        }

        .logo {
            font-size: 29px;
            font-weight: 900;
            letter-spacing: -1px;
        }

        .logo span,
        .hero h1 span,
        footer span {
            color: var(--red);
        }

        .nav-label {
            color: #ddd;
            border: 1px solid #333;
            padding: 6px 13px;
            border-radius: 30px;
            font-size: 12px;
        }

        .ad-space {
            min-height: 90px;
            margin: 22px auto;
            padding: 12px;
            border: 1px dashed #444;
            border-radius: 13px;
            background: #111;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: #777;
            font-size: 13px;
        }

        .ad-space small {
            display: block;
            color: #555;
            margin-top: 4px;
        }

        .hero {
            text-align: center;
            padding: 35px 0;
        }

        .badge {
            display: inline-block;
            background: #291014;
            border: 1px solid #572027;
            color: #ff9da5;
            border-radius: 30px;
            padding: 5px 14px;
            font-size: 12px;
        }

        .hero h1 {
            font-size: clamp(30px, 5vw, 48px);
            line-height: 1.3;
            margin: 18px 0 12px;
        }

        .hero p {
            color: var(--muted);
            max-width: 600px;
            margin: auto;
        }

        .download-card {
            background: linear-gradient(145deg, #191919, #101010);
            border: 1px solid #303030;
            border-radius: 23px;
            padding: clamp(20px, 5vw, 35px);
            box-shadow: 0 20px 65px #0008;
        }

        .platforms {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 25px;
        }

        .platform {
            border: 1px solid #333;
            background: #101010;
            border-radius: 13px;
            padding: 14px;
            text-align: center;
            cursor: pointer;
            color: white;
            font-size: 15px;
            font-weight: bold;
        }

        .platform.active,
        .platform:hover {
            border-color: var(--red);
            background: #301115;
        }

        .field-label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
        }

        .url-input {
            width: 100%;
            background: #080808;
            color: white;
            border: 1px solid #373737;
            border-radius: 12px;
            padding: 16px;
            font-size: 15px;
            outline: none;
            direction: ltr;
            text-align: left;
        }

        .url-input:focus {
            border-color: var(--red);
        }

        .download-button {
            display: block;
            width: 100%;
            margin-top: 14px;
            padding: 15px;
            border: none;
            border-radius: 12px;
            background: linear-gradient(
                100deg,
                #ff3040,
                #e51d30
            );
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }

        .download-button:disabled {
            opacity: 0.6;
            cursor: wait;
        }

        .hint {
            color: #888;
            font-size: 12px;
            margin-top: 12px;
        }

        .message {
            margin-top: 16px;
            padding: 12px;
            border: 1px solid #572027;
            border-radius: 10px;
            background: #241114;
            color: #ffd9dc;
            font-size: 14px;
        }

        .features {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin: 25px 0;
        }

        .feature {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 20px;
        }

        .feature .icon {
            font-size: 25px;
            margin-bottom: 8px;
        }

        .feature h3 {
            font-size: 15px;
            margin-bottom: 5px;
        }

        .feature p {
            color: var(--muted);
            font-size: 13px;
        }

        .notice {
            color: #777;
            text-align: center;
            font-size: 12px;
            padding: 20px 0;
        }

        footer {
            border-top: 1px solid var(--border);
            padding: 25px 0;
            text-align: center;
            color: #777;
            font-size: 12px;
        }

        @media (max-width: 600px) {
            .navbar {
                min-height: 65px;
            }

            .logo {
                font-size: 25px;
            }

            .nav-label {
                font-size: 10px;
            }

            .features {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>
<header>
    <div class="container navbar">
        <div class="logo">Vid<span>Drop</span></div>
        <div class="nav-label">تنزيل فيديوهات بسهولة</div>
    </div>
</header>

<main class="container">

    <div class="ad-space">
        <div>
            مساحة إعلانية علوية
            <small>مكان مخصص للإعلانات</small>
        </div>
    </div>

    <section class="hero">
        <span class="badge">مرحباً بك في VidDrop</span>
        <h1>تنزيل فيديوهات <span>بسهولة</span></h1>
        <p>
            اختار المنصة، لصق رابط الفيديو،
            واستعمل واجهة بسيطة على الهاتف والحاسوب.
        </p>
    </section>

    <section class="download-card">

        <div class="platforms">
            <button class="platform active"
                    type="button"
                    data-platform="youtube">
                ▶ YouTube
            </button>

            <button class="platform"
                    type="button"
                    data-platform="tiktok">
                ♪ TikTok
            </button>
        </div>

        <form id="downloadForm" action="/download" method="post">
            <label class="field-label" for="videoUrl">
                رابط الفيديو
            </label>

            <input
                class="url-input"
                id="videoUrl"
                name="video_url"
                type="url"
                placeholder="https://..."
                required
            >

            <input
                type="hidden"
                id="platform"
                name="platform"
                value="youtube"
            >

            <button class="download-button"
                    id="downloadButton"
                    type="submit">
                ↓ تنزيل الفيديو
            </button>

            <p class="hint">
                نزّل فقط المحتوى اللي عندك الحق تنزّلو.
            </p>
        </form>

        {% if message %}
        <div class="message" role="status">{{ message }}</div>
        {% endif %}
    </section>

    <div class="ad-space">
        <div>
            مساحة إعلانية وسط الصفحة
            <small>مكان مخصص للإعلانات</small>
        </div>
    </div>

    <section class="features">
        <article class="feature">
            <div class="icon">📱</div>
            <h3>متوافق مع الهاتف</h3>
            <p>تصميم متجاوب مع مختلف الشاشات.</p>
        </article>

        <article class="feature">
            <div class="icon">⚡</div>
            <h3>واجهة بسيطة</h3>
            <p>اختار المنصة ولصق الرابط بسهولة.</p>
        </article>

        <article class="feature">
            <div class="icon">🔒</div>
            <h3>استعمال مسؤول</h3>
            <p>احترم حقوق النشر وشروط المنصات.</p>
        </article>
    </section>

    <p class="notice">
        VidDrop خدمة مستقلة وليست تابعة لـ YouTube أو TikTok.
    </p>

    <div class="ad-space">
        <div>
            مساحة إعلانية أسفل الصفحة
            <small>مكان مخصص للإعلانات</small>
        </div>
    </div>

</main>

<footer>
    © 2026 <span>VidDrop</span> — جميع الحقوق محفوظة
</footer>

<script>
    const buttons = document.querySelectorAll(".platform");
    const platformInput = document.getElementById("platform");
    const urlInput = document.getElementById("videoUrl");
    const form = document.getElementById("downloadForm");
    const downloadButton = document.getElementById("downloadButton");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            buttons.forEach(item => item.classList.remove("active"));
            button.classList.add("active");

            platformInput.value = button.dataset.platform;

            urlInput.placeholder =
                platformInput.value === "youtube"
                ? "https://www.youtube.com/watch?v=..."
                : "https://www.tiktok.com/@user/video/...";
        });
    });

    form.addEventListener("submit", () => {
        downloadButton.disabled = true;
        downloadButton.textContent = "جاري تجهيز الفيديو...";
    });
</script>
</body>
</html>
"""


def render_home(message=None, status=200):
    return render_template_string(
        HTML,
        google_verification=GOOGLE_VERIFICATION,
        message=message
    ), status


@app.route("/", methods=["GET"])
def home():
    return render_home()


@app.route("/download", methods=["POST"])
def download_video():
    url = (request.form.get("video_url") or "").strip()

    if not url.startswith(("https://", "http://")):
        return render_home("دخل رابط فيديو صحيح.", 400)

    from urllib.parse import urlparse
    host = (urlparse(url).hostname or "").lower()
    allowed = (
        host == "youtu.be"
        or host.endswith(".youtu.be")
        or host == "youtube.com"
        or host.endswith(".youtube.com")
        or host == "tiktok.com"
        or host.endswith(".tiktok.com")
    )

    if not allowed:
        return render_home("الرابط خاصو يكون من YouTube أو TikTok.", 400)

    temp_dir = tempfile.mkdtemp(prefix="viddrop_")
    options = {
        "outtmpl": os.path.join(temp_dir, "%(title).80s.%(ext)s"),
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
        "max_filesize": 300 * 1024 * 1024,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if not os.path.isfile(filename):
            stem = os.path.splitext(filename)[0]
            matches = [
                os.path.join(temp_dir, item)
                for item in os.listdir(temp_dir)
                if os.path.splitext(os.path.join(temp_dir, item))[0] == stem
            ]
            if not matches:
                raise FileNotFoundError("Downloaded file not found")
            filename = matches[0]

        response = send_file(
            filename,
            as_attachment=True,
            download_name=os.path.basename(filename)
        )

        @response.call_on_close
        def cleanup():
            shutil.rmtree(temp_dir, ignore_errors=True)

        return response

    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return render_home(
            "ما قدرناش نجهزو الفيديو. تأكد من الرابط وعاود المحاولة.",
            400
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
