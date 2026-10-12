
import os
import re
import shutil
import tempfile
import logging
from urllib.parse import urlparse

from flask import Flask, request, render_template_string, send_file
import yt_dlp

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2000

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("viddrop")

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#11102b">
<title>VidDrop | YouTube و TikTok</title>
<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  font-family: Arial, sans-serif;
  color: white;
  background:
    radial-gradient(ellipse at 15% 0%, #5632a5, transparent 42%),
    radial-gradient(ellipse at 90% 35%, #143b83, transparent 38%),
    #0c0b20;
}
header, footer {
  width: min(100% - 32px, 950px);
  margin: auto;
}
header {
  padding: 22px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.logo {
  font-size: 28px;
  font-weight: 900;
}
.logo span {
  background: linear-gradient(90deg, #c4b5fd, #60a5fa);
  -webkit-background-clip: text;
  color: transparent;
}
.pill {
  padding: 8px 13px;
  border: 1px solid #ffffff25;
  background: #ffffff0b;
  border-radius: 30px;
  font-size: 12px;
  color: #ddd6fe;
}
main {
  width: min(100% - 32px, 680px);
  margin: 40px auto 55px;
}
.hero { text-align: center; margin-bottom: 28px; }
h1 {
  font-size: clamp(34px, 7vw, 52px);
  line-height: 1.3;
  margin: 20px 0 14px;
}
.gradient {
  background: linear-gradient(90deg, #c4b5fd, #60a5fa, #f0abfc);
  -webkit-background-clip: text;
  color: transparent;
}
p { line-height: 1.9; }
.muted { color: #c3c3e0; }
.panel {
  padding: clamp(20px, 5vw, 35px);
  background: #1a193aee;
  border: 1px solid #ffffff20;
  border-radius: 24px;
  box-shadow: 0 24px 70px #0005;
}
label {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
}
input, button {
  width: 100%;
  min-height: 54px;
  border-radius: 13px;
  font-size: 16px;
}
input {
  padding: 14px;
  border: 1px solid #ffffff25;
  background: #0c0b20;
  color: white;
  direction: ltr;
  text-align: left;
}
button {
  margin-top: 13px;
  padding: 14px;
  border: 0;
  color: white;
  font-weight: bold;
  cursor: pointer;
  background: linear-gradient(100deg, #7c3aed, #4f46e5, #2563eb);
}
button:hover { filter: brightness(1.12); }
.notice {
  margin-top: 18px;
  padding: 13px;
  border: 1px solid #ffffff25;
  border-radius: 12px;
  background: #ffffff0c;
  overflow-wrap: anywhere;
}
.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 22px;
}
.feature {
  padding: 16px 12px;
  border: 1px solid #ffffff20;
  background: #ffffff09;
  border-radius: 16px;
  text-align: center;
  color: #c3c3e0;
  font-size: 13px;
  line-height: 1.8;
}
.feature strong {
  display: block;
  color: white;
  margin-bottom: 7px;
}
footer {
  padding: 22px 0 30px;
  text-align: center;
  border-top: 1px solid #ffffff20;
  color: #c3c3e0;
  font-size: 12px;
}
@media (max-width: 560px) {
  .features { grid-template-columns: 1fr; }
  .feature { text-align: right; }
  main { margin-top: 25px; }
}
</style>
</head>
<body>
<header>
  <div class="logo">Vid<span>Drop</span></div>
  <span class="pill">YouTube • TikTok</span>
</header>

<main>
  <section class="hero">
    <span class="pill">منصة تنزيل الفيديوهات</span>
    <h1>الفيديو ديالك،<br><span class="gradient">بسهولة.</span></h1>
    <p class="muted">
      لسق رابط YouTube أو TikTok وجرب التحميل.
    </p>
  </section>

  <section class="panel">
    <form method="post">
      <label for="url">رابط الفيديو</label>
      <input
        id="url"
        name="url"
        type="url"
        placeholder="https://www.youtube.com/... أو TikTok"
        maxlength="1900"
        autocomplete="url"
        required
      >
      <button type="submit">↓ تحميل الفيديو</button>
    </form>

    {% if message %}
      <div class="notice" role="status">{{ message }}</div>
    {% endif %}

    <p class="muted">
      استعمل الموقع فقط مع الفيديوهات ديالك أو المحتوى
      اللي عندك الإذن أو الحق فتنزيله.
    </p>
  </section>

  <section class="features">
    <div class="feature">
      <strong>▶ YouTube</strong>
      روابط الفيديوهات المدعومة
    </div>
    <div class="feature">
      <strong>♪ TikTok</strong>
      روابط الفيديوهات المدعومة
    </div>
    <div class="feature">
      <strong>📱 الهاتف</strong>
      تصميم مناسب للشاشات
    </div>
  </section>
</main>

<footer>
  <p>VidDrop منصة مستقلة، وليست تابعة لـ YouTube أو TikTok.</p>
  <p>احترم حقوق النشر وشروط المنصات.</p>
</footer>
</body>
</html>
"""


def valid_video_url(url):
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()

        if parsed.scheme not in ("http", "https"):
            return False

        allowed_hosts = (
            host == "youtu.be"
            or host == "youtube.com"
            or host.endswith(".youtube.com")
            or host == "youtube-nocookie.com"
            or host.endswith(".youtube-nocookie.com")
            or host == "tiktok.com"
            or host.endswith(".tiktok.com")
        )

        return allowed_hosts
    except ValueError:
        return False


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template_string(HTML, message="")

    url = request.form.get("url", "").strip()

    if len(url) > 1900 or not valid_video_url(url):
        return render_template_string(
            HTML,
            message="دخل رابط صحيح ديال YouTube أو TikTok."
        ), 400

    temp_dir = tempfile.mkdtemp(prefix="viddrop_")
    output = os.path.join(temp_dir, "video.%(ext)s")

    options = {
        "outtmpl": output,
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "max_filesize": 100 * 1024 * 1024,
        "socket_timeout": 25,
        "retries": 1,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        files = [
            os.path.join(temp_dir, name)
            for name in os.listdir(temp_dir)
            if os.path.isfile(os.path.join(temp_dir, name))
        ]

        if not files:
            raise RuntimeError("No video file was created")

        video_path = files[0]
        extension = os.path.splitext(video_path)[1]

        response = send_file(
            video_path,
            as_attachment=True,
            download_name="VidDrop-video" + extension
        )

        @response.call_on_close
        def cleanup():
            shutil.rmtree(temp_dir, ignore_errors=True)

        return response

    except Exception:
        logger.exception("Video download failed")
        shutil.rmtree(temp_dir, ignore_errors=True)

        return render_template_string(
            HTML,
            message=(
                "ما قدرناش نحملو الفيديو. ممكن الرابط غير مدعوم، "
                "أو الفيديو غير متاح، أو المنصة رفضت الطلب."
            )
        ), 400


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 3000))
    )
