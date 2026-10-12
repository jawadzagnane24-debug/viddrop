
import os
import re
import tempfile
from flask import Flask, request, render_template_string, send_file
import yt_dlp

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2000

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VidDrop - تحميل الفيديوهات</title>
<style>
body{font-family:Arial;background:#101322;color:white;text-align:center;padding:25px}
main{max-width:500px;margin:40px auto;background:#1c2235;padding:25px;border-radius:18px}
h1{color:#8b9cff}
input,button{box-sizing:border-box;width:100%;padding:14px;margin-top:12px;border:0;border-radius:9px;font-size:16px}
input{background:white}
button{background:#697cff;color:white;font-weight:bold;cursor:pointer}
p{line-height:1.8;color:#c9cde0}
</style>
</head>
<body>
<main>
<h1>VidDrop</h1>
<h2>تحميل فيديوهات TikTok</h2>
<p>لسق رابط فيديو عندك الحق تحمّلو.</p>
<form method="post">
<input name="url" type="url" placeholder="لسق رابط TikTok هنا" required>
<button type="submit">تحميل الفيديو</button>
</form>
{% if message %}<p>{{ message }}</p>{% endif %}
<p>VidDrop — حمّل الفيديوهات المسموح لك بتنزيلها.</p>
</main>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template_string(HTML, message="")

    url = request.form.get("url", "").strip()
    match = re.match(r"^https?://([^/]+)", url, re.I)

    if not match or not (
        match.group(1).lower() == "tiktok.com"
        or match.group(1).lower().endswith(".tiktok.com")
    ):
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
            os.path.join(temp_dir, f)
            for f in os.listdir(temp_dir)
            if os.path.isfile(os.path.join(temp_dir, f))
        ]

        if not files:
            raise RuntimeError("ما تلقاش ملف الفيديو.")

        video_path = files[0]
        response = send_file(
            video_path,
            as_attachment=True,
            download_name="VidDrop-video.mp4",
        )

        @response.call_on_close
        def cleanup():
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

        return response

    except Exception:
        import shutil
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
    
