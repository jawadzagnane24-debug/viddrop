
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
<meta name="theme-color" content="#090909">
<meta name="description" content="VidDrop لتحميل الفيديوهات من الروابط المدعومة">
<title>VidDrop - تحميل الفيديوهات</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0; min-height: 100vh; color: #f7f7f7;
    background: radial-gradient(ellipse at top, #361015, #090909 55%);
    font-family: Arial, sans-serif;
    display: flex; flex-direction: column;
}
header { border-bottom: 1px solid #292929; }
nav {
    max-width: 950px; margin: auto; padding: 22px;
    display: flex; justify-content: space-between; align-items: center;
}
.logo { font-size: 27px; font-weight: 900; }
.logo span { color: #ff2438; }
.tag {
    color: #bbb; font-size: 11px; border: 1px solid #333;
    border-radius: 30px; padding: 9px 12px;
}
main {
    width: min(650px, calc(100% - 32px));
    margin: auto; padding: 65px 0; text-align: center;
}
.badge {
    display: inline-block; border: 1px solid #6c2029;
    border-radius: 30px; padding: 9px 14px;
    color: #ff8995; background: #ff24380d; font-size: 12px;
}
h1 { font-size: clamp(36px, 8vw, 57px); margin: 25px 0 15px; }
h1 span { color: #ff2438; }
.desc { color: #aaa; line-height: 1.9; margin-bottom: 30px; }
.panel {
    padding: 27px; border: 1px solid #303030;
    border-radius: 22px; background: #141414;
    box-shadow: 0 18px 65px #0006; text-align: right;
}
label { display: block; margin-bottom: 12px; font-weight: bold; }
input {
    width: 100%; padding: 16px; border: 1px solid #383838;
    border-radius: 12px; background: #090909; color: white;
    font-size: 14px; direction: ltr; text-align: left;
}
input:focus { outline: 2px solid #ff2438; border-color: transparent; }
button {
    width: 100%; margin-top: 14px; padding: 16px;
    border: 0; border-radius: 12px; background: #ff2438;
    color: white; font-size: 16px; font-weight: bold; cursor: pointer;
}
button:hover { background: #df182c; }
.hint { color: #999; font-size: 12px; line-height: 1.8; margin-bottom: 0; }
.notice {
    margin-top: 18px; padding: 13px; border-radius: 10px;
    border: 1px solid #633039; color: #ffb6be;
    background: #ff24380d; line-height: 1.8; overflow-wrap: anywhere;
}
footer {
    text-align: center; padding: 22px; color: #888;
    border-top: 1px solid #292929; font-size: 12px; line-height: 2;
}
@media(max-width: 500px) {
    nav { padding: 18px 16px; }
    .panel { padding: 20px; }
    main { padding: 45px 0; }
    .tag { font-size: 9px; }
}
</style>
</head>
<body>
<header>
<nav>
    <div class="logo">Vid<span>Drop</span></div>
    <div class="tag">VIDEO DOWNLOADER</div>
</nav>
</header>
<main>
    <div class="badge">منصة واحدة، خانة واحدة</div>
    <h1>الفيديو ديالك،<br><span>بطريقتك.</span></h1>
    <p class="desc">لسق رابط الفيديو فالمربع، وضغط على تحميل. الواجهة كتدعم روابط YouTube وTikTok.</p>

    <section class="panel">
        <form method="post">
            <label for="video-url">رابط الفيديو</label>
            <input id="video-url" name="url" type="url"
                   placeholder="لسق رابط YouTube أو TikTok هنا"
                   maxlength="1900" required>
            <button type="submit">↓ تحميل الفيديو</button>
        </form>
        {% if message %}
        <div class="notice" role="status">{{ message }}</div>
        {% endif %}
        <p class="hint">حمّل غير الفيديوهات اللي عندك الحق أو الإذن بتنزيلها. بعض الروابط قد لا تكون مدعومة.</p>
    </section>
</main>
<footer>
    VidDrop — منصة مستقلة، ماشي تابعة لـ YouTube أو TikTok.
</footer>
</body>
</html>
"""


def get_platform(url):
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
        return render_template_string(HTML, message="")

    url = request.form.get("url", "").strip()
    platform = get_platform(url)

    if len(url) > 1900 or not platform:
        return render_template_string(
            HTML,
            message="دخل رابط صحيح من YouTube أو TikTok."
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
            raise RuntimeError("No video file created")

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
        logger.exception("Video download failed: %s", platform)
        shutil.rmtree(temp_dir, ignore_errors=True)

        return render_template_string(
            HTML,
            message="ما قدرناش نحملو هاد الفيديو. جرّب رابط آخر متاح للتنزيل."
        ), 400


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 3000))
    )
