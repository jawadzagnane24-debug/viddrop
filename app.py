
import os
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

HTML = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0a0a0a">
<meta name="description" content="VidDrop - منصة لتنزيل فيديوهات YouTube وTikTok المسموح بتنزيلها.">
<title>VidDrop — Video Downloader</title>

<style>
:root {
  --bg: #090909;
  --panel: #141414;
  --panel2: #1b1b1b;
  --red: #ff2438;
  --red-dark: #bd1024;
  --white: #f7f7f7;
  --muted: #a5a5a5;
  --border: #2b2b2b;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  min-height: 100vh;
  font-family: Arial, sans-serif;
  background:
    radial-gradient(ellipse at 50% 0%, #361015 0%, transparent 42%),
    var(--bg);
  color: var(--white);
}

a {
  color: inherit;
  text-decoration: none;
}

.container {
  width: min(1120px, calc(100% - 36px));
  margin: auto;
}

header {
  border-bottom: 1px solid #ffffff12;
  background: #090909d9;
}

.nav {
  min-height: 78px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 27px;
  font-weight: 900;
  letter-spacing: -1px;
}

.logo-mark {
  width: 39px;
  height: 39px;
  display: grid;
  place-items: center;
  background: var(--red);
  border-radius: 12px;
  box-shadow: 0 0 28px #ff243833;
  color: white;
  font-size: 21px;
}

.logo span {
  color: var(--red);
}

.nav-tag {
  color: #d4d4d4;
  font-size: 12px;
  border: 1px solid var(--border);
  padding: 9px 13px;
  border-radius: 30px;
  background: #ffffff05;
}

.hero {
  padding: 76px 0 42px;
  text-align: center;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  border: 1px solid #ff243844;
  border-radius: 30px;
  background: #ff24380c;
  color: #ff8995;
  font-size: 12px;
  font-weight: bold;
}

.live-dot {
  width: 7px;
  height: 7px;
  background: var(--red);
  border-radius: 50%;
  box-shadow: 0 0 12px var(--red);
}

h1 {
  margin: 24px 0 16px;
  font-size: clamp(39px, 7vw, 70px);
  line-height: 1.14;
  letter-spacing: -2px;
}

h1 span {
  color: var(--red);
}

.hero p {
  max-width: 570px;
  margin: 0 auto;
  color: var(--muted);
  font-size: 16px;
  line-height: 1.9;
}

.platforms {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 22px;
  padding: 24px 0 54px;
}

.platform-card {
  position: relative;
  overflow: hidden;
  padding: 29px;
  border: 1px solid var(--border);
  border-radius: 22px;
  background: linear-gradient(145deg, #1a1a1a, #101010);
  transition: transform .2s, border-color .2s;
}

.platform-card:hover {
  transform: translateY(-4px);
  border-color: #ff243866;
}

.platform-card::before {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  height: 3px;
  background: var(--red);
}

.platform-head {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 23px;
}

.platform-icon {
  width: 60px;
  height: 60px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  border-radius: 17px;
  background: #ff243815;
  border: 1px solid #ff24382b;
  color: var(--red);
  font-size: 28px;
  font-weight: 900;
}

.platform-head h2 {
  margin: 0 0 7px;
  font-size: 22px;
}

.platform-head p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}

label {
  display: block;
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: bold;
}

input {
  width: 100%;
  min-height: 54px;
  padding: 14px;
  direction: ltr;
  text-align: left;
  color: white;
  background: #090909;
  border: 1px solid #353535;
  border-radius: 12px;
  font-size: 14px;
  outline: none;
}

input::placeholder {
  color: #737373;
}

input:focus {
  border-color: var(--red);
  box-shadow: 0 0 0 3px #ff243818;
}

.download-btn {
  width: 100%;
  min-height: 53px;
  margin-top: 13px;
  border: 0;
  border-radius: 12px;
  background: var(--red);
  color: white;
  font-size: 15px;
  font-weight: bold;
  cursor: pointer;
  transition: background .2s, transform .2s;
}

.download-btn:hover {
  background: #e7192d;
  transform: translateY(-1px);
}

.download-btn:focus-visible {
  outline: 2px solid white;
  outline-offset: 3px;
}

.hint {
  margin: 15px 0 0;
  color: #909090;
  font-size: 12px;
  line-height: 1.8;
}

.notice {
  margin-top: 17px;
  padding: 13px;
  border: 1px solid #ff24384a;
  border-radius: 12px;
  background: #ff24380d;
  color: #ffb6be;
  font-size: 13px;
  line-height: 1.8;
  overflow-wrap: anywhere;
}

.notice[hidden] {
  display: none;
}

.info-section {
  margin: 0 0 55px;
  padding: 29px;
  border: 1px solid var(--border);
  border-radius: 20px;
  background: #111111;
}

.info-section h2 {
  margin-top: 0;
  font-size: 21px;
}

.steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.step {
  padding: 18px;
  border-radius: 14px;
  background: #191919;
}

.step-number {
  display: inline-grid;
  place-items: center;
  width: 32px;
  height: 32px;
  margin-bottom: 10px;
  border-radius: 10px;
  background: #ff24381a;
  color: var(--red);
  font-weight: bold;
}

.step h3 {
  margin: 5px 0 8px;
  font-size: 15px;
}

.step p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.9;
}

footer {
  padding: 27px 0;
  border-top: 1px solid var(--border);
  text-align: center;
  color: #858585;
  font-size: 12px;
  line-height: 2;
}

footer strong {
  color: #d4d4d4;
}

@media (max-width: 720px) {
  .hero {
    padding: 53px 0 25px;
  }

  .platforms {
    grid-template-columns: 1fr;
    gap: 18px;
    padding-top: 20px;
  }

  .platform-card {
    padding: 23px;
  }

  .steps {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .info-section {
    padding: 22px;
  }

  .nav {
    min-height: 68px;
  }

  .logo {
    font-size: 24px;
  }

  .nav-tag {
    font-size: 10px;
  }

  h1 {
    letter-spacing: -1px;
  }
}
</style>
</head>

<body>
<header>
  <div class="container nav">
    <a href="/" class="logo" aria-label="VidDrop home">
      <span class="logo-mark">V</span>
      Vid<span>Drop</span>
    </a>
    <span class="nav-tag">VIDEO DOWNLOADER</span>
  </div>
</header>

<main class="container">
  <section class="hero">
    <div class="eyebrow">
      <span class="live-dot"></span>
      منصة واحدة، منصتان
    </div>

    <h1>
      الفيديو ديالك،<br>
      <span>بطريقتك.</span>
    </h1>

    <p>
      اختار المنصة، لسق رابط الفيديو، وجرب التحميل
      من واجهة بسيطة وسريعة.
    </p>
  </section>

  <section class="platforms" aria-label="اختيار المنصة">

    <article class="platform-card">
      <div class="platform-head">
        <div class="platform-icon" aria-hidden="true">▶</div>
        <div>
          <h2>YouTube</h2>
          <p>فيديوهات YouTube المدعومة</p>
        </div>
      </div>

      <form method="post">
        <input type="hidden" name="platform" value="youtube">

        <label for="youtube-url">رابط YouTube</label>
        <input
          id="youtube-url"
          name="url"
          type="url"
          placeholder="https://www.youtube.com/watch?v=..."
          maxlength="1900"
          autocomplete="url"
          required
        >

        <button class="download-btn" type="submit">
          ↓ تحميل من YouTube
        </button>
      </form>

      {% if platform == "youtube" and message %}
      <div class="notice" role="status">{{ message }}</div>
      {% endif %}

      <p class="hint">
        نزّل فقط الفيديوهات اللي عندك الحق أو الإذن بتنزيلها.
      </p>
    </article>

    <article class="platform-card">
      <div class="platform-head">
        <div class="platform-icon" aria-hidden="true">♪</div>
        <div>
          <h2>TikTok</h2>
          <p>فيديوهات TikTok المدعومة</p>
        </div>
      </div>

      <form method="post">
        <input type="hidden" name="platform" value="tiktok">

        <label for="tiktok-url">رابط TikTok</label>
        <input
          id="tiktok-url"
          name="url"
          type="url"
          placeholder="https://www.tiktok.com/..."
          maxlength="1900"
          autocomplete="url"
          required
        >

        <button class="download-btn" type="submit">
          ↓ تحميل من TikTok
        </button>
      </form>

      {% if platform == "tiktok" and message %}
      <div class="notice" role="status">{{ message }}</div>
      {% endif %}

      <p class="hint">
        خاص الفيديو يكون متاحاً، مع احترام حقوق صاحبه.
      </p>
    </article>

  </section>

  <section class="info-section">
    <h2>كيفاش تستعمل VidDrop؟</h2>

    <div class="steps">
      <div class="step">
        <span class="step-number">01</span>
        <h3>اختار المنصة</h3>
        <p>اختار بطاقة YouTube أو TikTok حسب الرابط ديالك.</p>
      </div>

      <div class="step">
        <span class="step-number">02</span>
        <h3>لسق الرابط</h3>
        <p>نسخ رابط الفيديو ولصقو فالمربع المناسب.</p>
      </div>

      <div class="step">
        <span class="step-number">03</span>
        <h3>بدا التحميل</h3>
        <p>ضغط على الزر. نجاح التحميل كيتعلق بتوفر الفيديو ودعم المصدر.</p>
      </div>
    </div>
  </section>
</main>

<footer>
  <div class="container">
    <strong>VidDrop</strong> — منصة مستقلة.
    ماشي تابعة لـ YouTube أو TikTok.<br>
    احترم حقوق النشر وشروط استعمال المنصات.
  </div>
</footer>
</body>
</html>
"""


def get_platform_for_url(url):
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()

        if parsed.scheme not in ("http", "https"):
            return None

        if (
            host == "youtube.com"
            or host.endswith(".youtube.com")
            or host == "youtube-nocookie.com"
            or host.endswith(".youtube-nocookie.com")
            or host == "youtu.be"
        ):
            return "youtube"

        if host == "tiktok.com" or host.endswith(".tiktok.com"):
            return "tiktok"

        return None
    except ValueError:
        return None


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template_string(
            HTML,
            message="",
            platform=""
        )

    url = request.form.get("url", "").strip()
    selected_platform = request.form.get("platform", "").strip()

    actual_platform = get_platform_for_url(url)

    if (
        len(url) > 1900
        or actual_platform is None
        or selected_platform not in ("youtube", "tiktok")
        or actual_platform != selected_platform
    ):
        return render_template_string(
            HTML,
            message="تأكد من الرابط واختار البطاقة المناسبة للمنصة.",
            platform=selected_platform
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
        extension = os.path.splitext(video_path)[1] or ".mp4"

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
        logger.exception(
            "VidDrop download failed for platform: %s",
            actual_platform
        )
        shutil.rmtree(temp_dir, ignore_errors=True)

        return render_template_string(
            HTML,
            message=(
                "تعذّر تحميل الفيديو. تأكد من الرابط، "
                "وجرب فيديو آخر متاح للتنزيل."
            ),
            platform=selected_platform
        ), 400


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 3000))
    )
