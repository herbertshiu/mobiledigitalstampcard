#!/usr/bin/env python3
"""Authority / SEO upgrade for mobiledigitalstampcard.hk (UTF-8 safe)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
BASE = "https://www.mobiledigitalstampcard.hk"
OG_IMAGE = f"{BASE}/og-default.png"
AHREFS = (
    '<script src="https://analytics.ahrefs.com/analytics.js" '
    'data-key="Maf9NSwSyFgLmWeoy05n+g" async></script>'
)

FOOTER = """
    <footer class="foot foot--wide shell">
      <div class="foot__grid">
        <div class="foot__col">
          <h3>來信與心聲</h3>
          <ul>
            <li><a href="letters.html">全部顧客來信</a></li>
            <li><a href="quotes.html">語錄牆</a></li>
            <li><a href="replies.html">店東怎麼做</a></li>
          </ul>
        </div>
        <div class="foot__col">
          <h3>閱讀</h3>
          <ul>
            <li><a href="articles.html">專題文章</a></li>
            <li><a href="membership-system-guide.html">香港會員系統指南</a></li>
            <li><a href="article-choose-loyalty-tool.html">顧客想要怎樣的 App</a></li>
            <li><a href="faq.html">常見問答</a></li>
            <li><a href="glossary.html">詞彙表</a></li>
          </ul>
        </div>
        <div class="foot__col">
          <h3>本站</h3>
          <ul>
            <li><a href="/">首頁</a></li>
            <li><a href="about.html">關於常客心聲</a></li>
            <li><a href="sitemap.xml">網站地圖</a></li>
          </ul>
        </div>
      </div>
      <p>© 2026 常客心聲 · 顧客視角，供香港店東參考</p>
    </footer>
"""

# Page SEO: title, description (120-155 chars target), path, og_type, page_kind
PAGES: dict[str, dict] = {
    "index.html": {
        "title": "常客心聲｜顧客為何喜歡會員 App 與數位會員制度",
        "desc": "給香港餐飲、零售、美容店東：顧客親口說為何喜歡會員 App 與會員系統——十二封來信、專題與問答，協助小店規劃數位會員經營。",
        "path": "/",
        "og_type": "website",
        "kind": "home",
    },
    "letters.html": {
        "title": "顧客來信｜常客心聲 — 十一封會員 App 心聲",
        "desc": "十一封虛構顧客來信：掃碼、積分、推播與小店人情——反映香港顧客對會員系統與會員 App 的期待，給餐飲零售店東參考。",
        "path": "/letters.html",
        "og_type": "website",
        "kind": "hub",
    },
    "articles.html": {
        "title": "專題文章｜常客心聲 — 會員 App 與忠誠度",
        "desc": "專題：顧客為何信任有 App 的店、香港節奏下的會員體驗、會員制度與促銷如何並行——從顧客視角給香港店東實用參考。",
        "path": "/articles.html",
        "og_type": "website",
        "kind": "hub",
    },
    "faq.html": {
        "title": "常見問答｜常客心聲 — 會員卡 App 店東必問",
        "desc": "香港店東常問：會員 App 有何好處、如何選會員系統、積分怎麼設計？從顧客心聲整理的問答，協助小店導入數位會員。",
        "path": "/faq.html",
        "og_type": "website",
        "kind": "faq",
    },
    "glossary.html": {
        "title": "詞彙表｜常客心聲 — 會員制度術語解讀",
        "desc": "會員卡、會員 App、會員系統、Customer loyalty program、店家儲值系統——從顧客視角解釋術語，協助店東與顧客對齊語言。",
        "path": "/glossary.html",
        "og_type": "website",
        "kind": "hub",
    },
    "about.html": {
        "title": "關於本站｜常客心聲 — 從顧客視角看會員 App",
        "desc": "常客心聲以虛構來信與文章，探討香港店舖的會員卡 App、會員制度與數位集點，協助小店了解顧客對會員系統的真正期望。",
        "path": "/about.html",
        "og_type": "website",
        "kind": "about",
    },
    "quotes.html": {
        "title": "語錄牆｜常客心聲 — 會員 App 真心話",
        "desc": "二十句虛構顧客真心話：喜歡好用的會員 App、討厭複雜積分、對小店的期待——給香港店東靈感與 customer retention 啟發。",
        "path": "/quotes.html",
        "og_type": "website",
        "kind": "hub",
    },
    "replies.html": {
        "title": "店東怎麼做｜常客心聲 — 聽見心聲後的行動",
        "desc": "聽見顧客喜歡會員 App 之後，如何投資與優化會員系統？從技術選擇到營運策略，給香港餐飲零售美容小店的行動指南。",
        "path": "/replies.html",
        "og_type": "website",
        "kind": "hub",
    },
    "article-choose-loyalty-tool.html": {
        "title": "顧客喜歡怎樣的會員 App？｜常客心聲",
        "desc": "從常客來信整理顧客真正喜歡的會員 App 體驗，並對照香港本地方案——含 Mobile.Cards 等，協助店東把心聲變成選型方向。",
        "path": "/article-choose-loyalty-tool.html",
        "og_type": "article",
        "kind": "article",
    },
    "article-trust.html": {
        "title": "顧客為何信任有 App 的店｜常客心聲",
        "desc": "為什麼顧客比較信任有會員 App 的店？從透明度、一致性與可控感，分析數位會員制度如何建立信任，給香港店東參考。",
        "path": "/article-trust.html",
        "og_type": "article",
        "kind": "article",
    },
    "article-hk-pace.html": {
        "title": "香港節奏與會員 App｜常客心聲",
        "desc": "香港顧客節奏快、耐心少——會員 App 如何適應？分析消費行為並提供適合快節奏市場的會員系統設計建議。",
        "path": "/article-hk-pace.html",
        "og_type": "article",
        "kind": "article",
    },
    "article-loyalty-discount.html": {
        "title": "會員 App 與促銷如何並行｜常客心聲",
        "desc": "促銷拉新客，會員制度留住回頭客——兩者如何相輔相成？分析打折與忠誠度，給香港小店會員經營與促銷整合參考。",
        "path": "/article-loyalty-discount.html",
        "og_type": "article",
        "kind": "article",
    },
    "membership-system-guide.html": {
        "title": "香港會員系統指南｜常客心聲",
        "desc": "什麼是會員系統／會員系統 App？香港餐飲零售店東如何選電子會員卡與積分制度——從顧客視角整理的實用入門指南。",
        "path": "/membership-system-guide.html",
        "og_type": "article",
        "kind": "guide",
    },
    "letter-scan-fatigue.html": {
        "title": "掃一次就搞定｜常客心聲 — 會員 App 整合體驗",
        "desc": "顧客來信：喜歡會員 App 一次完成登記、集點與查餘額，勝過分開掃碼——給香港餐飲店東的會員系統體驗參考。",
        "path": "/letter-scan-fatigue.html",
        "og_type": "article",
        "kind": "letter",
    },
    "letter-rush-hour.html": {
        "title": "尖峰時 App 更快｜常客心聲 — 會員卡省時",
        "desc": "顧客來信：放工後不想翻實體卡，會員 App 一掃完成集點與付款，省下排隊時間——尖峰時段的數位會員價值。",
        "path": "/letter-rush-hour.html",
        "og_type": "article",
        "kind": "letter",
    },
    "letter-math-fatigue.html": {
        "title": "App 幫我算積分｜常客心聲 — 積分視覺化",
        "desc": "顧客來信：討厭牆上複雜積分規則，會員 App 直接顯示進度與還差幾分可兌換——會員制度視覺化為何重要。",
        "path": "/letter-math-fatigue.html",
        "og_type": "article",
        "kind": "letter",
    },
    "letter-staff-whisper.html": {
        "title": "櫃檯與 App 一致｜常客心聲 — 會員系統信任",
        "desc": "顧客來信：最怕店員說「應該有記錄」卻翻不到——會員系統讓櫃檯與 App 顯示一致，建立彼此信任。",
        "path": "/letter-staff-whisper.html",
        "og_type": "article",
        "kind": "letter",
    },
    "letter-late-coupon.html": {
        "title": "App 提醒帶我回來｜常客心聲 — 會員推播",
        "desc": "顧客來信：會員 App 適時提醒優惠券快到期、積分快夠換——恰到好處的提醒會讓我週末特地回來消費。",
        "path": "/letter-late-coupon.html",
        "og_type": "article",
        "kind": "letter",
    },
    "letter-twenty-seconds.html": {
        "title": "二十秒換好用 App｜常客心聲 — 登記流程",
        "desc": "顧客來信：願意花二十秒登記會員 App，因為之後每次消費一秒掃碼、積分自動累積——長期更省時間。",
        "path": "/letter-twenty-seconds.html",
        "og_type": "article",
        "kind": "letter",
    },
    "letter-word-of-mouth.html": {
        "title": "推薦 App 好用的店｜常客心聲 — 口碑",
        "desc": "顧客來信：會主動向朋友推薦會員 App 體驗順暢的店舖——好的會員系統讓消費變成享受，也能帶來口碑。",
        "path": "/letter-word-of-mouth.html",
        "og_type": "article",
        "kind": "letter",
    },
    "letter-push-too-much.html": {
        "title": "有用的 App 提醒｜常客心聲 — 推播頻率",
        "desc": "顧客來信：歡迎差一分可兌換、優惠券快到期的實用推播，但不要每天無關廣告——精準比頻率更重要。",
        "path": "/letter-push-too-much.html",
        "og_type": "article",
        "kind": "letter",
    },
    "letter-data-wary.html": {
        "title": "App 讓我安心查紀錄｜常客心聲 — 資料隱私",
        "desc": "顧客來信：只登記手機號碼就能用會員 App 查消費與積分，比填長篇個資更安心，也更願意成為會員。",
        "path": "/letter-data-wary.html",
        "og_type": "article",
        "kind": "letter",
    },
    "letter-small-shop-feel.html": {
        "title": "小店加 App 更貼心｜常客心聲 — 街坊會員",
        "desc": "顧客來信：街坊小店有人情味，加上會員 App 自動記積分——人情味加科技，是最完整的消費體驗。",
        "path": "/letter-small-shop-feel.html",
        "og_type": "article",
        "kind": "letter",
    },
    "letter-birthday-empty.html": {
        "title": "生日禮在 App 裡｜常客心聲 — 個人化優惠",
        "desc": "顧客來信：會員 App 在生日當天推送配合常點品項的優惠——量身定做比群發「生日快樂」更有誠意。",
        "path": "/letter-birthday-empty.html",
        "og_type": "article",
        "kind": "letter",
    },
}

CONTENT_BOOSTS = {
    "article-trust.html": """
        <h2>顧客會轉傳的信任訊號</h2>
        <p>當積分、餘額與兌換規則在會員 App 裡一目了然，顧客更願意向朋友推薦「這家店有系統」。信任不只留住舊客，也是口碑來源。延伸閱讀：<a href="membership-system-guide.html">香港會員系統指南</a>、<a href="letter-word-of-mouth.html">推薦 App 好用的店</a>。</p>
""",
    "article-hk-pace.html": """
        <h2>設計原則：快而清楚</h2>
        <p>香港顧客要的不是更多步驟，而是更少摩擦。會員系統 App 應讓結帳、集點、查進度在幾秒內完成。延伸閱讀：<a href="letter-rush-hour.html">尖峰時 App 更快</a>、<a href="membership-system-guide.html">香港會員系統指南</a>。</p>
""",
    "article-loyalty-discount.html": """
        <h2>把促銷放進會員制度</h2>
        <p>打折能帶來首次進店；會員 App 負責讓顧客成為回頭客。透過 App 精準送券，比無差別降價更能保護利潤。延伸閱讀：<a href="letter-late-coupon.html">App 提醒帶我回來</a>、<a href="faq.html">常見問答</a>。</p>
""",
}


def make_og_image() -> None:
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), "#1a2332")
    draw = ImageDraw.Draw(img)
    # warm accent band
    draw.rectangle([0, 0, w, 12], fill="#c45c26")
    draw.rectangle([0, h - 12, w, h], fill="#c45c26")
    # subtle panel
    draw.rectangle([80, 120, w - 80, h - 120], outline="#d4a574", width=2)
    try:
        font_lg = ImageFont.truetype(
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 96
        )
        font_sm = ImageFont.truetype(
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 40
        )
    except OSError:
        try:
            font_lg = ImageFont.truetype(
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 96
            )
            font_sm = ImageFont.truetype(
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 40
            )
        except OSError:
            font_lg = ImageFont.load_default()
            font_sm = font_lg
    title = "常客心聲"
    sub = "顧客為何喜歡會員 App｜香港店東參考"
    # center-ish text
    draw.text((120, 220), title, fill="#f7f1e8", font=font_lg)
    draw.text((120, 360), sub, fill="#d4a574", font=font_sm)
    draw.text((120, 440), "mobiledigitalstampcard.hk", fill="#8a93a3", font=font_sm)
    out = ROOT / "og-default.png"
    img.save(out, "PNG", optimize=True)
    print("wrote", out)


def org_website_jsonld() -> str:
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{BASE}/#organization",
                "name": "常客心聲",
                "url": f"{BASE}/",
                "description": "從顧客視角談香港店舖會員 App、會員系統與數位會員制度。",
                "logo": OG_IMAGE,
            },
            {
                "@type": "WebSite",
                "@id": f"{BASE}/#website",
                "url": f"{BASE}/",
                "name": "常客心聲",
                "publisher": {"@id": f"{BASE}/#organization"},
                "inLanguage": "zh-Hant",
            },
        ],
    }
    return (
        '<script type="application/ld+json">'
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )


def article_jsonld(title: str, desc: str, path: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "inLanguage": "zh-Hant",
        "mainEntityOfPage": f"{BASE}{path}",
        "author": {"@type": "Organization", "name": "常客心聲"},
        "publisher": {
            "@type": "Organization",
            "name": "常客心聲",
            "logo": {"@type": "ImageObject", "url": OG_IMAGE},
        },
        "image": [OG_IMAGE],
    }
    return (
        '<script type="application/ld+json">'
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )


def faq_jsonld(html: str) -> str:
    items = []
    for m in re.finditer(
        r'<article class="faq-item">\s*<h2>(.*?)</h2>\s*<p>(.*?)</p>',
        html,
        flags=re.S,
    ):
        q = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        a = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if q and a:
            items.append(
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                }
            )
    if not items:
        return ""
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}
    return (
        '<script type="application/ld+json">'
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )


def build_head(meta: dict, extra_jsonld: str = "") -> str:
    title = meta["title"]
    desc = meta["desc"]
    url = f"{BASE}{meta['path']}"
    parts = [
        f"    <title>{title}</title>",
        f'    <meta name="description" content="{desc}" />',
        f'    <link rel="canonical" href="{url}" />',
        f'    <meta property="og:title" content="{title}" />',
        f'    <meta property="og:description" content="{desc}" />',
        f'    <meta property="og:url" content="{url}" />',
        f'    <meta property="og:type" content="{meta["og_type"]}" />',
        '    <meta property="og:site_name" content="常客心聲" />',
        '    <meta property="og:locale" content="zh_HK" />',
        f'    <meta property="og:image" content="{OG_IMAGE}" />',
        '    <meta property="og:image:width" content="1200" />',
        '    <meta property="og:image:height" content="630" />',
        '    <meta name="twitter:card" content="summary_large_image" />',
        f'    <meta name="twitter:title" content="{title}" />',
        f'    <meta name="twitter:description" content="{desc}" />',
        f'    <meta name="twitter:image" content="{OG_IMAGE}" />',
        f"    {AHREFS}",
        f"    {org_website_jsonld()}",
    ]
    if meta["kind"] in ("article", "letter", "guide"):
        parts.append(f"    {article_jsonld(title, desc, meta['path'])}")
    if extra_jsonld:
        parts.append(f"    {extra_jsonld}")
    return "\n".join(parts)


def replace_head_seo(html: str, meta: dict, extra_jsonld: str = "") -> str:
    # Remove existing SEO / analytics / jsonld blocks we manage
    html = re.sub(r"\s*<title>.*?</title>", "", html, count=1, flags=re.S)
    html = re.sub(
        r'\s*<meta\s+name="description"\s+content="[^"]*"\s*/?>',
        "",
        html,
        flags=re.S,
    )
    # multiline description
    html = re.sub(
        r'\s*<meta\s*\n\s*name="description"\s*\n\s*content="[^"]*"\s*\n\s*/?>',
        "",
        html,
        flags=re.S,
    )
    html = re.sub(r'\s*<link\s+rel="canonical"[^>]*>', "", html)
    html = re.sub(r'\s*<meta\s+property="og:[^"]+"\s+content="[^"]*"\s*/?>', "", html)
    html = re.sub(
        r'\s*<meta\s*\n\s*property="og:[^"]+"\s*\n\s*content="[^"]*"\s*\n\s*/?>',
        "",
        html,
        flags=re.S,
    )
    html = re.sub(r'\s*<meta\s+name="twitter:[^"]+"\s+content="[^"]*"\s*/?>', "", html)
    html = re.sub(
        r'\s*<meta\s*\n\s*name="twitter:[^"]+"\s*\n\s*content="[^"]*"\s*\n\s*/?>',
        "",
        html,
        flags=re.S,
    )
    html = re.sub(
        r'\s*<script src="https://analytics\.ahrefs\.com/analytics\.js"[^>]*></script>',
        "",
        html,
    )
    html = re.sub(
        r'\s*<script type="application/ld\+json">.*?</script>',
        "",
        html,
        flags=re.S,
    )

    head_block = build_head(meta, extra_jsonld)
    # Insert before stylesheet or before </head>
    if re.search(r'<link[^>]+href="styles\.css"', html):
        html = re.sub(
            r'(<link[^>]+href="styles\.css"[^>]*>)',
            r"\1\n" + head_block,
            html,
            count=1,
        )
    else:
        html = html.replace("</head>", head_block + "\n  </head>", 1)
    return html


def replace_footer(html: str) -> str:
    html = re.sub(
        r"<footer class=\"foot[\s\S]*?</footer>",
        FOOTER.strip(),
        html,
        count=1,
    )
    return html


def normalize_home_links(html: str) -> str:
    html = html.replace('href="index.html"', 'href="/"')
    return html


def boost_content(html: str, filename: str) -> str:
    addition = CONTENT_BOOSTS.get(filename)
    if not addition or addition.strip() in html:
        return html
    if '<div class="essay-body">' in html:
        html = html.replace(
            "</div>\n    </main>",
            addition + "      </div>\n    </main>",
            1,
        )
    return html


def write_guide_page() -> None:
    meta = PAGES["membership-system-guide.html"]
    body = f"""<!DOCTYPE html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="keywords" content="會員系統,會員系統App,電子會員卡系統,會員管理系統,會員積分系統,會員卡App,香港" />
    <link href="https://fonts.googleapis.com/css2?family=Karla:wght@400;500&family=Lora:wght@600&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <header class="bar">
      <div class="bar__inner">
        <a class="bar__logo" href="/">常客<em>心聲</em></a>
        <nav class="bar__links" aria-label="站內導覽">
          <a class="bar__link" href="letters.html">來信</a>
          <a class="bar__link bar__link--active" href="articles.html">文章</a>
          <a class="bar__link" href="faq.html">問答</a>
          <a class="bar__link" href="glossary.html">詞彙</a>
        </nav>
      </div>
    </header>
    <main class="essay shell">
      <p class="essay__crumb"><a href="/">首頁</a> / <a href="articles.html">文章</a> / 指南</p>
      <header class="page-head">
        <h1>香港會員系統指南：店東如何選會員系統 App？</h1>
        <p>從顧客視角解釋「會員系統」「會員系統 App」「電子會員卡」是什麼，以及香港小店導入時該先問什麼。</p>
      </header>
      <div class="essay-body">
        <p>在香港搜尋「會員系統」或「會員系統 App」時，店東常被功能清單淹沒。常客心聲換一個角度：顧客真正在意的是什麼？本指南整理可分享、可對照的選型框架，並連回站內來信與專題。</p>

        <h2>會員系統是什麼？</h2>
        <p>會員系統（membership / loyalty system）是店舖用來登記會員、累積積分或儲值、發送優惠與查詢紀錄的一套規則與工具。可以是紙本集點卡，也可以是<strong>會員系統 App</strong>或電子會員卡。對顧客來說，好的系統等於「我的進度看得見、不會無故消失」。</p>

        <h2>為什麼香港店東常搜「會員系統 App」？</h2>
        <p>節奏快、排隊短、手機付款普及——紙卡容易丟、蓋章糊掉。顧客來信反覆提到：結帳要快、積分要自己查得到、提醒要有用。這些需求，剛好對應到數位會員系統與會員卡 App。可先讀：</p>
        <ul>
          <li><a href="letter-scan-fatigue.html">掃一次就搞定</a></li>
          <li><a href="letter-rush-hour.html">尖峰時 App 更快</a></li>
          <li><a href="article-hk-pace.html">香港節奏與會員 App</a></li>
        </ul>

        <h2>選會員系統前，先對齊這五件事</h2>
        <ol>
          <li><strong>一次完成</strong>：登記、集點、查餘額是否在同一流程？（見來信「二十秒換好用 App」）</li>
          <li><strong>櫃檯與手機一致</strong>：店員與顧客看到的積分是否相同？（見<a href="article-trust.html">信任專題</a>）</li>
          <li><strong>規則看得見</strong>：進度條、還差幾分，是否比牆上小字更清楚？</li>
          <li><strong>推播要精準</strong>：到期提醒可以；無關廣告會讓顧客關通知。</li>
          <li><strong>資料要克制</strong>：能用手機號碼完成的，就不要逼填長表單。</li>
        </ol>

        <h2>會員系統、電子會員卡、CRM：差在哪？</h2>
        <p>電子會員卡常指放進手機錢包的卡片；會員系統 App 通常還包含積分、兌換、推播與後台報表；CRM 會員系統則偏重顧客資料與行銷自動化。小店可先滿足「顧客每天會打開、櫃檯不會吵架」的體驗，再擴充報表與自動化。詞彙對照見<a href="glossary.html">詞彙表</a>。</p>

        <h2>會員積分系統怎樣才算對顧客友善？</h2>
        <p>規則可以複雜，但呈現必須簡單。顧客討厭心算雙倍日與例外條款；他們喜歡「再開兩次可換小食」這種目標感。促銷與會員制度可以並行，但應透過 App 精準送券，而不是無差別打折——詳見<a href="article-loyalty-discount.html">會員 App 與促銷如何並行</a>。</p>

        <h2>讀完指南，下一步</h2>
        <p>若你已聽懂顧客心聲、想把需求對照到具體方案，可讀<a href="article-choose-loyalty-tool.html">顧客喜歡怎樣的會員 App？</a>；若還在評估值不值得投資，先看<a href="faq.html">常見問答</a>與<a href="replies.html">店東怎麼做</a>。</p>
        <p>本指南供香港餐飲、零售、美容店東分享與內部討論。歡迎連回常客心聲原文，並標明出處。</p>
      </div>
    </main>
    {FOOTER.strip()}
  </body>
</html>
"""
    # inject head via same pipeline later
    path = ROOT / "membership-system-guide.html"
    path.write_text(body, encoding="utf-8")
    print("wrote guide skeleton", path)


def write_sitemap() -> None:
    urls = [
        "/",
        "/letters.html",
        "/articles.html",
        "/membership-system-guide.html",
        "/article-choose-loyalty-tool.html",
        "/faq.html",
        "/glossary.html",
        "/about.html",
        "/quotes.html",
        "/replies.html",
        "/letter-scan-fatigue.html",
        "/letter-rush-hour.html",
        "/letter-math-fatigue.html",
        "/letter-staff-whisper.html",
        "/letter-late-coupon.html",
        "/letter-twenty-seconds.html",
        "/letter-word-of-mouth.html",
        "/letter-push-too-much.html",
        "/letter-data-wary.html",
        "/letter-small-shop-feel.html",
        "/letter-birthday-empty.html",
        "/article-trust.html",
        "/article-hk-pace.html",
        "/article-loyalty-discount.html",
    ]
    lastmod = "2026-09-11"
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{BASE}{u}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote sitemap")


def link_guide_on_hubs() -> None:
    # articles.html: insert preview card after catalog__sub
    articles = ROOT / "articles.html"
    html = articles.read_text(encoding="utf-8")
    card = """
      <a class="preview-card" href="membership-system-guide.html" style="display:block;margin-bottom:1rem">
        <p class="preview-card__type">指南 · 選型</p>
        <h3>香港會員系統指南：店東如何選會員系統 App？</h3>
        <p>會員系統、電子會員卡、積分制度——從顧客視角整理的入門框架，適合分享給團隊。</p>
      </a>
"""
    if "membership-system-guide.html" not in html or "香港會員系統指南：店東如何選" not in html:
        html = html.replace(
            '<p class="catalog__sub">',
            card + '      <p class="catalog__sub">',
            1,
        )
        articles.write_text(html, encoding="utf-8")

    # about.html list item
    about = ROOT / "about.html"
    ahtml = about.read_text(encoding="utf-8")
    if "membership-system-guide.html" not in ahtml:
        ahtml = ahtml.replace(
            '<li><a href="articles.html">專題文章</a>',
            '<li><a href="membership-system-guide.html">香港會員系統指南</a>——可分享的選型入門</li>\n          <li><a href="articles.html">專題文章</a>',
            1,
        )
        about.write_text(ahtml, encoding="utf-8")

    # index footer reading column
    index = ROOT / "index.html"
    ihtml = index.read_text(encoding="utf-8")
    if "membership-system-guide.html" not in ihtml:
        ihtml = ihtml.replace(
            '<li><a href="articles.html">專題文章</a></li>',
            '<li><a href="articles.html">專題文章</a></li>\n              <li><a href="membership-system-guide.html">香港會員系統指南</a></li>',
            1,
        )
        index.write_text(ihtml, encoding="utf-8")


def main() -> None:
    make_og_image()
    write_guide_page()
    write_sitemap()
    link_guide_on_hubs()

    for filename, meta in PAGES.items():
        path = ROOT / filename
        if not path.exists():
            print("missing", filename)
            continue
        html = path.read_text(encoding="utf-8")
        extra = ""
        if filename == "faq.html":
            extra = faq_jsonld(html)
        html = normalize_home_links(html)
        html = boost_content(html, filename)
        html = replace_head_seo(html, meta, extra)
        html = replace_footer(html)
        # ensure UTF-8 write
        path.write_text(html, encoding="utf-8")
        print(f"updated {filename} title_len={len(meta['title'])} desc_len={len(meta['desc'])}")

    # verify no mojibake
    for f in ROOT.glob("*.html"):
        t = f.read_text(encoding="utf-8")
        if "Õ©©" in t:
            raise SystemExit(f"mojibake detected in {f}")
    print("all ok")


if __name__ == "__main__":
    main()
