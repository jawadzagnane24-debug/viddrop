
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
<meta name="description" content="VidDrop - واجهة بسيطة لتنزيل فيديوهات TikTok المتاحة للتنزيل.">
<title>VidDrop | حمّل بسهولة</title>
<style>
:root {
  --bg: #0c0b20;
  --panel: rgba(26, 25, 58, .88);
  --text: #fff;
  --muted: #c3c3e0;
  --purple: #a78bfa;
  --blue: #60a5fa;
  --border: rgba(255,255,255,.13);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  font-family: Arial, sans-serif;
  color: var(--text);
  background:
    radial-gradient(ellipse at 15% 0%, #5632a5 0, transparent 42%),
    radial-gradient(ellipse at 90% 35%, #143b83 0, transparent 38%),
    var(--bg);
}
header, footer {
  width: min(100% - 32px, 1000px);
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
  font-size: 27px;
  font-weight: 900;
  letter-spacing: -.7px;
}
.logo span {
  background: linear-gradient(90deg, #c4b5fd, #60a5fa);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.pill {
  padding: 8px 13px;
  border: 1px solid var(--border);
  background: #ffffff0b;
  border-radius: 30px;
  font-size: 12px;
  color: #ddd6fe;
}
main {
  width: min(100% - 32px, 700px);
  margin: 45px auto 55px;
}
.hero { text-align: center; margin-bottom: 28px; }
h1 {
  font-size: clamp(34px, 7vw, 54px);
  line-height: 1.25;
  margin: 20px 0 14px;
}
.gradient-text {
  background: linear-gradient(90deg, #c4b5fd, #60a5fa, #f0abfc);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.hero p, .description {
  color: var(--muted);
  line-height: 1.9;
  font-size: 15px;
}
.panel {
  padding: clamp(20px, 5vw, 36px);
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 24px;
  box-shadow: 0 24px 70px #0005;
  backdrop-filter: blur(14px);
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
input:focus {
  outline: 2px solid var(--purple);
  outline-offset: 2px;
}
button {
  margin-top: 13px;
  padding: 14px;
  border: 0;
  color: white;
  font-weight: bold;
  cursor: pointer;
  background: linear-gradient(100deg, #7c3aed, #4f46e5, #2563eb);
  box-shadow: 0 8px 24px #4f46e544;
  transition: transform .2s, filter .2s;
}
button:hover { filter: brightness(1.12); transform: translateY(-1px); }
button:focus-visible { outline: 2px solid white; outline-offset: 3px; }
.notice {
  margin-top: 18px;
  padding: 13px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #ffffff0c;
  color: #e0e7ff;
  line-height: 1.8;
  overflow-wrap: anywhere;
}
.ad-slot {
  min-height: 100px;
  margin: 24px 0;
  padding: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #c3c3e0;
  font-size: 13px;
  border: 1px dashed #ffffff35;
  border-radius: 16px;
  background: #ffffff06;
}
.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 22px;
}
.feature {
  padding: 18px 12px;
  border: 1px solid var(--border);
  background: #ffffff09;
  border-radius: 16px;
  text-align: center;
  font-size: 13px;
  line-height: 1.8;
  color: var(--muted);
}
.feature strong {
  display: block;
  margin-bottom: 7px;
  color: white;
  font-size: 14px;
}
.how {
  margin-top: 30px;
  padding: 22px;
  border-radius: 18px;
  background: #ffffff07;
  border: 1px solid var(--border);
}
.how h2 { font-size: 20px; }
.how p { color: var(--muted); line-height: 2; }
footer {
  padding: 22px 0 30px;
  text-align: center;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 12px;
  line-height: 2;
}
@media (max-width: 560px) {
  header { padding: 17px 0; }
  .logo { font-size: 24px; }
  .pill { font-size: 11px; padding: 7px 10px; }
  main { margin: 24px auto 38px; }
  .features { grid-template-columns: 1fr; }
  .feature { text-align: right; padding: 15px; }
  .hero p { font-size: 14px; }
}
</style>
</head>
<body>
<header>
  <div class="logo">Vid<span>Drop</span></div>
  <span class="pill">بسيط • سريع • سهل</span>
</header>

<main>
  <section class="hero">
    <span class="pill">أداة تنزيل الفيديوهات</span>
    <h1>الفيديو ديالك،<br><span class="gradient-text">بسهولة.</span></h1>
    <p>لسق رابط فيديو متاح للتنزيل، وجرب VidDrop.</p>
  </section>

  <section class="panel">
    <form method="post">
      <label for="url">رابط فيديو TikTok</label>
      <input
        id="url"
        name="url"
        type="url"
        placeholder="https://www.tiktok.com/..."
        autocomplete="url"
        maxlength="1900"
        required
      >
      <button type="submit">↓　تحميل الفيديو</button>
    </form>

    {% if message %}
    <div class="notice" role="status">{{ message }}</div>
    {% endif %}

    <p class="description">
      استعمل الخدمة مع الفيديوهات اللي عندك الحق تنزّلها.
      التنزيل كيتوقف على توفر الفيديو ودعم المصدر.
    </p>
  </section>

  <div class="ad-slot" aria-label="مساحة إعلانية">
    مساحة إعلانية — غير مفعّلة حالياً
  </div>

  <section class="features">
    <div class="feature">
      <strong>🔗 رابط الفيديو</strong>
      لسق الرابط فالمربع
    </div>
    <div class="feature">
      <strong>📱 مناسب للهاتف</strong>
      تصميم كيتأقلم مع الشاشة
    </div>
    <div class="feature">
      <strong>🛡️ استعمال مسؤول</strong>
      احترم حقوق أصحاب المحتوى
    </div>
  </section>

  <section class="how">
    <h2>كيفاش تستعمل VidDrop؟</h2>
    <p>
      1. نسخ رابط الفيديو.<br>
      2. لصق الرابط فالمربع أعلاه.<br>
      3. ضغط على زر التحميل إذا كان الفيديو متاحاً.
    </p>
  </section>
</main>

<footer>
  <p>VidDrop أداة مستقلة، وليست تابعة لـ TikTok.</p>
  <p>نزّل المحتوى اللي عندك الحق تستعمله فقط.</p>
</footer>
</body>
</html>
"""


def valid_tiktok_url(url):
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        return (
            parsed.scheme in ("http", "https")
            and (host == "tiktok.com" or host.endswith(".tiktok.com"))
        )
    except ValueError:
        return False


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template_string(HTML, message="")

    url = request.form.get("url", "").strip()

    if len(url) > 1900 or not valid_tiktok_url(url):
        return render_template_string(
            HTML, message="عافاك دخل رابط TikTok صحيح."
        ), 400

    temp_dir = tempfile.mkdtemp(prefix="viddrop_")
    output = os.path.join(temp_dir, "video.%(ext)s")

    options = {
        "outtmpl": output,
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "max_filesize": 100 * 1024 * 1024,
        "socket_timeout": 20,
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
        response = send_file(
            video_path,
            as_attachment=True,
            download_name="VidDrop-video" + os.path.splitext(video_path)[1],
        )

        @response.call_on_close
        def cleanup():
            shutil.rmtree(temp_dir, ignore_errors=True)

        return response

    except Exception:
        logger.exception("VidDrop download failed")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return render_template_string(
            HTML,
            message="ما قدرناش نحملو هاد الفيديو. تأكد من الرابط وعاود المحاولة."
        ), 400


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 3000))
    )
