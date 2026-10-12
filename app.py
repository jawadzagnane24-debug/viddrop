
import os
import tempfile
import shutil
from urllib.parse import urlparse

from flask import Flask, request, render_template_string, send_file, Response
import yt_dlp

app = Flask(__name__)

GOOGLE_VERIFICATION = (
    "nwb3Nxl9qGs1VLeuGiOUE4YM2Vw0yh5rxD0dMEXNm8M"
)

SITE_URL = "https://brave-cedar-7334.de.deplexo.com"

HTML = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="google-site-verification"
          content="{{ google_verification }}">
    <meta name="description"
          content="VidDrop أداة سهلة لتحميل الفيديوهات من الإنترنت.">
    <title>VidDrop - تنزيل فيديوهات بسهولة</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            background: #101010;
            color: white;
            font-family: Arial, sans-serif;
        }
        header {
            padding: 22px;
            text-align: center;
            background: #181818;
            border-bottom: 2px solid #e50914;
        }
        header h1 {
            margin: 0;
            color: #ff3038;
            font-size: 30px;
        }
        main {
            max-width: 700px;
            margin: 45px auto;
            padding: 20px;
            text-align: center;
        }
        .panel {
            background: #1c1c1c;
            border: 1px solid #333;
            border-radius: 15px;
            padding: 25px;
        }
        h2 { font-size: 27px; }
        p { color: #ccc; line-height: 1.8; }
        .platforms {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        .platforms button {
            flex: 1;
            background: #292929;
            color: white;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 12px;
            cursor: pointer;
        }
        .platforms button.active {
            background: #e50914;
            border-color: #e50914;
        }
        input {
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border: 1px solid #444;
            background: #111;
            color: white;
            font-size: 16px;
            direction: ltr;
        }
        .download {
            width: 100%;
            padding: 15px;
            margin-top: 10px;
            background: #e50914;
            color: white;
            border: 0;
            border-radius: 8px;
            font-size: 18px;
            cursor: pointer;
        }
        .download:hover { background: #bd0710; }
        .ad {
            margin: 22px 0;
            padding: 20px 10px;
            border: 1px dashed #555;
            color: #999;
            border-radius: 8px;
        }
        footer {
            text-align: center;
            color: #999;
            padding: 25px;
        }
        a { color: #ff5158; }
        @media (max-width: 480px) {
            main { margin: 20px auto; }
            .panel { padding: 18px; }
            h2 { font-size: 23px; }
        }
    </style>
</head>
<body>
    <header>
        <h1>VidDrop</h1>
    </header>

    <main>
        <div class="ad">مساحة إعلانية</div>

        <section class="panel">
            <h2>تنزيل فيديوهات بسهولة</h2>
            <p>حط رابط الفيديو واختار المنصة باش تبدا.</p>

            <div class="platforms">
                <button type="button" id="youtube"
                        onclick="choosePlatform('youtube')">
                    YouTube
                </button>
                <button type="button" id="tiktok"
                        onclick="choosePlatform('tiktok')">
                    TikTok
                </button>
            </div>

            <form action="/download" method="post">
                <input type="hidden" name="platform"
                       id="platform" value="youtube">
                <input type="url" name="url" required
                       placeholder="لسق رابط الفيديو هنا"
                       aria-label="رابط الفيديو">
                <button class="download" type="submit">
                    تنزيل الفيديو
                </button>
            </form>

            {% if error %}
                <p style="color:#ff6268">{{ error }}</p>
            {% endif %}

            <p>
                استعمل الخدمة غير مع الفيديوهات اللي عندك الحق
                تحملها، واحترم حقوق النشر وشروط المنصة.
            </p>
        </section>

        <div class="ad">مساحة إعلانية</div>
    </main>

    <footer>
        <p>© 2026 VidDrop</p>
        <a href="/sitemap.xml">خريطة الموقع</a>
    </footer>

    <script>
        function choosePlatform(platform) {
            document.getElementById('platform').value = platform;
            document.getElementById('youtube').classList.toggle(
                'active', platform === 'youtube'
            );
            document.getElementById('tiktok').classList.toggle(
                'active', platform === 'tiktok'
            );
        }
        choosePlatform('youtube');
    </script>
</body>
</html>
"""


def render_home(error=None):
    return render_template_string(
        HTML,
        google_verification=GOOGLE_VERIFICATION,
        error=error
    )


@app.route("/")
def home():
    return render_home()


@app.route("/sitemap.xml")
def sitemap():
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE_URL}/</loc>
  </url>
</urlset>"""
    return Response(xml, mimetype="application/xml")


@app.route("/robots.txt")
def robots():
    text = f"""User-agent: *
Allow: /
Sitemap: {SITE_URL}/sitemap.xml
"""
    return Response(text, mimetype="text/plain")


@app.route("/download", methods=["POST"])
def download():
    video_url = request.form.get("url", "").strip()

    try:
        parsed = urlparse(video_url)
        host = (parsed.hostname or "").lower()

        allowed_domains = (
            "youtube.com",
            "youtu.be",
            "tiktok.com",
        )

        valid_host = any(
            host == domain or host.endswith("." + domain)
            for domain in allowed_domains
        )

        if parsed.scheme not in ("http", "https") or not valid_host:
            return render_home(
                "الرابط غير صالح. استعمل رابط YouTube أو TikTok."
            )

        temp_dir = tempfile.mkdtemp(prefix="viddrop_")

        options = {
            "format": "best[ext=mp4]/best",
            "outtmpl": os.path.join(temp_dir, "video.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
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
                shutil.rmtree(temp_dir, ignore_errors=True)
                return render_home(
                    "ما قدرناش نجهزو الفيديو. جرّب رابط آخر."
                )

            file_path = files[0]

            response = send_file(
                file_path,
                as_attachment=True,
                download_name="viddrop_video" + os.path.splitext(file_path)[1]
            )

            response.call_on_close(
                lambda: shutil.rmtree(temp_dir, ignore_errors=True)
            )
            return response

        except Exception:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return render_home(
                "ما قدرناش نحملو الفيديو. ممكن الرابط ما خدامش أو المنصة بدلات طريقة الوصول."
            )

    except Exception:
        return render_home("وقع خطأ. عاود جرّب من فضلك.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
