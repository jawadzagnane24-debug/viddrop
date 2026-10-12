import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

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
h1{color:#8b9cff}input,button{box-sizing:border-box;width:100%;padding:14px;margin-top:12px;border:0;border-radius:9px;font-size:16px}
input{background:white}button{background:#697cff;color:white;font-weight:bold}
p{line-height:1.8;color:#c9cde0}
</style>
</head>
<body>
<main>
<h1>VidDrop</h1>
<h2>تحميل فيديوهات TikTok</h2>
<p>لسق رابط الفيديو باش تبدأ.</p>
<form method="post">
<input name="url" type="url" placeholder="لسق رابط TikTok هنا" required>
<button type="submit">تحميل الفيديو</button>
</form>
{% if message %}<p>{{ message }}</p>{% endif %}
<p>VidDrop — أداة بسيطة لتحميل الفيديوهات المتاحة لك.</p>
</main>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if "tiktok.com/" not in url:
            message = "دخل رابط TikTok صحيح من فضلك."
        else:
            message = "الواجهة خدامة، ولكن خاصنا نضيفو خدمة معالجة الفيديو باش التحميل يخدم."
    return render_template_string(HTML, message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
