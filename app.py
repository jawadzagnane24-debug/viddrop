
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#090909">
  <title>VidDrop - تحميل الفيديوهات</title>

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
        radial-gradient(ellipse at top, #351014 0%, transparent 45%),
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

    /* Header */
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

    .logo span {
      color: var(--red);
    }

    .nav-label {
      color: #ddd;
      border: 1px solid #333;
      padding: 6px 13px;
      border-radius: 30px;
      font-size: 12px;
    }

    /* Advertisement spaces */
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

    /* Hero */
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

    .hero h1 span {
      color: var(--red);
    }

    .hero p {
      color: var(--muted);
      max-width: 600px;
      margin: auto;
    }

    /* Main download card */
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
      transition: 0.2s;
      color: white;
      font-size: 15px;
      font-weight: bold;
    }

    .platform.active {
      border-color: var(--red);
      background: #301115;
      box-shadow: inset 0 0 0 1px var(--red);
    }

    .platform:hover {
      border-color: var(--red);
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
      box-shadow: 0 0 0 3px #ff30401a;
    }

    .download-button {
      display: block;
      width: 100%;
      margin-top: 14px;
      padding: 15px;
      border: none;
      border-radius: 12px;
      background: linear-gradient(100deg, #ff3040, #e51d30);
      color: white;
      font-size: 16px;
      font-weight: bold;
      cursor: pointer;
      transition: 0.2s;
    }

    .download-button:hover {
      filter: brightness(1.12);
      transform: translateY(-2px);
    }

    .hint {
      color: #888;
      font-size: 12px;
      margin-top: 12px;
    }

    .status {
      display: none;
      margin-top: 16px;
      padding: 12px;
      border: 1px solid #572027;
      border-radius: 10px;
      background: #241114;
      color: #ffd9dc;
      font-size: 14px;
    }

    /* Features */
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

    footer span {
      color: var(--red);
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

      .ad-space {
        min-height: 75px;
      }
    }
  </style>
</head>
<meta name="google-site-verification" content="nwb3Nxl9qGs1VLeuGiOUE4YM2Vw0yh5rxD0dMEXNm8M" />
<body>

  <header>
    <div class="container navbar">
      <div class="logo">Vid<span>Drop</span></div>
      <div class="nav-label">تحميل الفيديوهات بسهولة</div>
    </div>
  </header>

  <main class="container">

    <!-- إعلان رقم 1 -->
    <div class="ad-space">
      <div>
        مساحة إعلانية علوية
        <small>ضع كود الإعلان ديالك هنا</small>
      </div>
    </div>

    <section class="hero">
      <span class="badge">مرحباً بك في VidDrop</span>

      <h1>
        حمّل الفيديو ديالك
        <span>بسهولة</span>
      </h1>

      <p>
        اختار المنصة، لصق رابط الفيديو، واستمتع بواجهة بسيطة
        وسريعة على الهاتف والحاسوب.
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

      <form id="downloadForm">
        <label class="field-label" for="videoUrl">
          رابط الفيديو
        </label>

        <input
          class="url-input"
          id="videoUrl"
          type="url"
          placeholder="https://..."
          required
        >

        <button class="download-button" type="submit">
          ↓ تحميل الفيديو
        </button>

        <p class="hint">
          حمّل المحتوى اللي عندك الحق تنزّلو فقط.
        </p>
      </form>

      <div class="status" id="status"></div>
    </section>

    <!-- إعلان رقم 2 -->
    <div class="ad-space">
      <div>
        مساحة إعلانية وسط الصفحة
        <small>مكان مخصص للإعلانات المتجاوبة</small>
      </div>
    </div>

    <section class="features">
      <article class="feature">
        <div class="icon">📱</div>
        <h3>متوافق مع الهاتف</h3>
        <p>تصميم متجاوب مع مختلف أحجام الشاشات.</p>
      </article>

      <article class="feature">
        <div class="icon">⚡</div>
        <h3>واجهة بسيطة</h3>
        <p>اختار المنصة ولصق الرابط بكل سهولة.</p>
      </article>

      <article class="feature">
        <div class="icon">🔒</div>
        <h3>استعمال واضح</h3>
        <p>تعليمات بسيطة ورسائل واضحة للمستخدم.</p>
      </article>
    </section>

    <p class="notice">
      VidDrop خدمة مستقلة وليست تابعة لـ YouTube أو TikTok.
      يرجى احترام حقوق النشر وشروط المنصات.
    </p>

    <!-- إعلان رقم 3 -->
    <div class="ad-space">
      <div>
        مساحة إعلانية أسفل الصفحة
        <small>ضع كود الإعلان ديالك هنا</small>
      </div>
    </div>

  </main>

  <footer>
    © 2026 <span>VidDrop</span> — جميع الحقوق محفوظة
  </footer>

  <script>
    let selectedPlatform = "youtube";

    const platformButtons =
      document.querySelectorAll(".platform");

    const form = document.getElementById("downloadForm");
    const urlInput = document.getElementById("videoUrl");
    const statusBox = document.getElementById("status");

    platformButtons.forEach(button => {
      button.addEventListener("click", () => {
        platformButtons.forEach(item =>
          item.classList.remove("active")
        );

        button.classList.add("active");
        selectedPlatform = button.dataset.platform;

        urlInput.placeholder =
          selectedPlatform === "youtube"
            ? "https://www.youtube.com/watch?v=..."
            : "https://www.tiktok.com/@user/video/...";

        statusBox.style.display = "none";
      });
    });

    form.addEventListener("submit", event => {
      event.preventDefault();

      const url = urlInput.value.trim();

      if (!url) return;

      statusBox.style.display = "block";
      statusBox.textContent =
        "التصميم واجد، ولكن خاص ربط هاد الواجهة بسيرفر التحميل باش يخدم الزر فعلياً.";
    });
  </script>

</body>
</html>
