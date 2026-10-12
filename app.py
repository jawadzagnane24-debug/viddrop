
import os
import re
import tempfile
import shutil
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
<meta name="theme-color" content="#0b1020">
<meta name="description" content="VidDrop أداة بسيطة لتحميل الفيديوهات المتاحة للتنزيل.">
<title>VidDrop | تحميل الفيديوهات</title>
<style>
*{box-sizing:border-box}
body{margin:0;min-height:100vh;font-family:Arial,sans-serif;color:#f6f7ff;background:radial-gradient(ellipse at top,#242c58 0%,transparent 55%),#0b1020}
header,footer{max-width:900px;margin:auto;padding:22px 20px}
header{display:flex;justify-content:space-between;align-items:center;gap:12px}
.logo{font-size:27px;font-weight:800}
.logo span{color:#818cf8}
.tag{display:inline-block;border:1px solid #293653;background:#171f39;color:#c7d2fe;border-radius:30px;padding:8px 14px;font-size:13px}
main{width:min(92%,680px);margin:35px auto}
.hero{text-align:center;margin-bottom:26px}
h1{font-size:clamp(32px,7vw,48px);margin:18px 0 12px}
p{line-height:1.9;color:#aab4d0}
.panel{background:#131b30;border:1px solid #293653;padding:clamp(20px,5vw,34px);border-radius:22px;box-shadow:0 20px 60px #0004}
label{display:block;font-weight:bold;margin-bottom:10px}
input,button{width:100%;min-height:52px;border-radius:12px;font-size:16px}
input{border:1px solid #354263;background:#0c1326;color:white;padding:14px;direction:ltr;text-align:left}
button{margin-top:12px;border:0;padding:14px;background:linear-gradient(100deg,#6366f1,#8b5cf6);color:white;font-weight:bold;cursor:pointer}
.notice{margin-top:18px;padding:12px;border-radius:10px;background:#222d49;color:#e0e7ff;line-height:1.7;overflow-wrap:anywhere}
.ad-slot{margin:24px 0;min-height:90px;padding:16px;border:1px dashed #354263;border-radius:14px;text-align:center;color:#aab4d0;font-size:13px;display:flex;justify-content:center;align-items:center}
.features{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:22px}
.feature{background:#131b30;border:1px solid #293653;border-radius:14px;padding:16px 10px;text-align:center;font-size:14px;line-height:1.8}
.feature strong{display:block;margin-bottom:5px;color:#fff}
footer{border-top:1px solid #293653;text-align:center;font-size:13px;line-height:2.2}
@media(max-width:520px){header{padding:18px 16px}main{margin:24px auto 36px}.features{grid-template-columns:1fr}.feature{text-align:right}}
</style>
</head>
<body>
<header>
<div class="logo">Vid<span>Drop</span></div>
<span class="tag">بسيط • سريع • سهل</span>
</header>
<main>
<section class="hero">
<span class="tag">أداة تنزيل الفيديوهات</span>
<h1>الفيديو ديالك، <span style="color:#a5b4fc">بسهولة.</span></h1>
<p>لسق رابط فيديو مسموح ليك بتنزيله، وخلي VidDrop يتكلف بالباقي.</p>
</section>
<section class="panel">
<form method="post">
<label for="url">رابط فيديو TikTok</label>
<input id="url" name="url" type="url" placeholder="https://www.tiktok.com/..." autocomplete="url" required>
<button type="submit">↓ تحميل الفيديو</button>
</form>
{% if message %}
<div class="notice" role="status">{{ message }}</div>
{% endif %}
<p>استعمل الخدمة غير مع الفيديوهات اللي عندك الحق تنزّلها. نجاح التنزيل كيتوقف على توفر الفيديو ودعم المصدر.</p>
</section>
<div class="ad-slot">مساحة إعلانية — غير مفعلة حالياً</div>
<section class="features">
<div class="feature"><strong>🔗 رابط مباشر</strong>لسق الرابط فالمربع</div>
<div class="feature"><strong>📱 مناسب للهاتف</strong>واجهة متجاوبة مع الشاشة</div>
<div class="feature"><strong>🛡️ استعمال مسؤول</strong>احترم حقوق أصحاب الفيديوهات</div>
</section>
<section style="margin-top:30px">
<h2>كيفاش تستعمل VidDrop؟</h2>
<p>1. نسخ رابط الفيديو من المصدر.<br>2. لصق الرابط في الخانة أعلاه.<br>3. الضغط على زر التحميل إذا كان الفيديو متاحاً.</p>
</section>
</main>
<footer>
<p>VidDrop — أداة مستقلة، وليست تابعة لـ TikTok.</p>
<p>حمّل المحتوى اللي عندك الحق تستعمله فقط.</p>
</footer>
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
            shutil.rmtree(temp_dir, ignore_errors=True)

        return response

    except Exception:
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
