"""
briefing_template.py — 브리핑 HTML 템플릿 (일러스트 포함)
morning_briefing_v3.py 에서 import해서 사용.
"""

WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]

CAT_ACCENT = {
    "OpenAI 뉴스":    "#1a3a5c",
    "Anthropic 뉴스": "#7b2d8b",
    "AI 테크 트렌드":  "#1a5c3a",
    "경제 매크로":     "#c0392b",
    "Lenny's":        "#5c3a1a",
    "Sandhill":       "#1a4a5c",
    "Chamath":        "#3a3a1a",
}

# ─── SVG 일러스트 ──────────────────────────────────────

SVG_SUN = """<svg width="160" height="100" viewBox="0 0 160 100" fill="none"
  xmlns="http://www.w3.org/2000/svg" style="opacity:.18" aria-hidden="true">
  <line x1="0" y1="70" x2="160" y2="70" stroke="#0e0e0e" stroke-width="1.2"/>
  <circle cx="80" cy="44" r="18" stroke="#0e0e0e" stroke-width="1.2"/>
  <line x1="80" y1="14" x2="80" y2="8" stroke="#0e0e0e" stroke-width="1"/>
  <line x1="50" y1="44" x2="44" y2="44" stroke="#0e0e0e" stroke-width="1"/>
  <line x1="110" y1="44" x2="116" y2="44" stroke="#0e0e0e" stroke-width="1"/>
  <line x1="58.5" y1="22.5" x2="54.4" y2="18.4" stroke="#0e0e0e" stroke-width="1"/>
  <line x1="101.5" y1="22.5" x2="105.6" y2="18.4" stroke="#0e0e0e" stroke-width="1"/>
  <line x1="58.5" y1="65.5" x2="54.4" y2="69.6" stroke="#0e0e0e" stroke-width="1"/>
  <line x1="101.5" y1="65.5" x2="105.6" y2="69.6" stroke="#0e0e0e" stroke-width="1"/>
  <path d="M0 82 Q20 76 40 82 Q60 88 80 82 Q100 76 120 82 Q140 88 160 82"
    stroke="#0e0e0e" stroke-width="1" fill="none"/>
  <path d="M0 90 Q20 84 40 90 Q60 96 80 90 Q100 84 120 90 Q140 96 160 90"
    stroke="#0e0e0e" stroke-width="1" fill="none" opacity=".5"/>
</svg>"""

SVG_CHART = """<svg width="100%" height="60" viewBox="0 0 200 60" fill="none"
  xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <line x1="20" y1="8" x2="20" y2="52" stroke="#0e0e0e" stroke-width="1.2"/>
  <line x1="20" y1="52" x2="190" y2="52" stroke="#0e0e0e" stroke-width="1.2"/>
  <polyline points="20,44 50,30 80,36 110,18 140,24 170,10 190,14"
    stroke="#0e0e0e" stroke-width="1.4" fill="none" stroke-linejoin="round"/>
  <circle cx="50" cy="30" r="2" fill="#0e0e0e"/>
  <circle cx="110" cy="18" r="2" fill="#0e0e0e"/>
  <circle cx="170" cy="10" r="2" fill="#0e0e0e"/>
  <line x1="16" y1="20" x2="20" y2="20" stroke="#0e0e0e" stroke-width="1"/>
  <line x1="16" y1="36" x2="20" y2="36" stroke="#0e0e0e" stroke-width="1"/>
</svg>"""

SVG_FOX = """<svg width="80" height="60" viewBox="0 0 80 60" fill="none"
  xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <ellipse cx="40" cy="38" rx="18" ry="14" stroke="#0e0e0e" stroke-width="1.2"/>
  <path d="M26 28 L18 12 L30 22" stroke="#0e0e0e" stroke-width="1.2"
    stroke-linejoin="round" fill="none"/>
  <path d="M54 28 L62 12 L50 22" stroke="#0e0e0e" stroke-width="1.2"
    stroke-linejoin="round" fill="none"/>
  <circle cx="34" cy="36" r="2" stroke="#0e0e0e" stroke-width="1"/>
  <circle cx="46" cy="36" r="2" stroke="#0e0e0e" stroke-width="1"/>
  <ellipse cx="40" cy="42" rx="3" ry="2" stroke="#0e0e0e" stroke-width="1"/>
  <path d="M58 44 Q70 38 72 50 Q60 52 58 44" stroke="#0e0e0e" stroke-width="1" fill="none"/>
</svg>"""

SVG_DOTS = """<svg width="28" height="14" viewBox="0 0 28 14" fill="none"
  xmlns="http://www.w3.org/2000/svg" style="opacity:.25;flex-shrink:0" aria-hidden="true">
  <circle cx="4" cy="7" r="3" stroke="#0e0e0e" stroke-width="1"/>
  <line x1="8" y1="7" x2="14" y2="7" stroke="#0e0e0e" stroke-width="1"/>
  <circle cx="18" cy="7" r="3" stroke="#0e0e0e" stroke-width="1"/>
  <line x1="22" y1="7" x2="28" y2="7" stroke="#0e0e0e" stroke-width="1"/>
</svg>"""

SVG_FOOTER_DECO = """<svg width="40" height="10" viewBox="0 0 40 10" fill="none"
  aria-hidden="true" style="opacity:.3">
  <line x1="0" y1="5" x2="12" y2="5" stroke="#7a7060" stroke-width="1"/>
  <circle cx="20" cy="5" r="3" stroke="#7a7060" stroke-width="1"/>
  <line x1="28" y1="5" x2="40" y2="5" stroke="#7a7060" stroke-width="1"/>
</svg>"""

# 기사별 소스 타입에 맞는 미니 일러스트
def get_article_illo(source):
    if "AI" in source or "OpenAI" in source or "Anthropic" in source:
        # AI 칩/회로 느낌
        return """<svg width="32" height="32" viewBox="0 0 32 32" fill="none"
          xmlns="http://www.w3.org/2000/svg" style="opacity:.18;margin-bottom:8px" aria-hidden="true">
          <rect x="8" y="8" width="16" height="16" stroke="#0e0e0e" stroke-width="1.2"/>
          <rect x="11" y="11" width="10" height="10" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="12" y1="8" x2="12" y2="4" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="16" y1="8" x2="16" y2="4" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="20" y1="8" x2="20" y2="4" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="12" y1="24" x2="12" y2="28" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="16" y1="24" x2="16" y2="28" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="20" y1="24" x2="20" y2="28" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="8" y1="12" x2="4" y2="12" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="8" y1="16" x2="4" y2="16" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="8" y1="20" x2="4" y2="20" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="24" y1="12" x2="28" y2="12" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="24" y1="16" x2="28" y2="16" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="24" y1="20" x2="28" y2="20" stroke="#0e0e0e" stroke-width="1"/>
        </svg>"""
    elif "경제" in source:
        # 코인/달러 느낌
        return """<svg width="32" height="32" viewBox="0 0 32 32" fill="none"
          xmlns="http://www.w3.org/2000/svg" style="opacity:.18;margin-bottom:8px" aria-hidden="true">
          <circle cx="16" cy="16" r="11" stroke="#0e0e0e" stroke-width="1.2"/>
          <circle cx="16" cy="16" r="7" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="16" y1="9" x2="16" y2="7" stroke="#0e0e0e" stroke-width="1.2"/>
          <line x1="16" y1="23" x2="16" y2="25" stroke="#0e0e0e" stroke-width="1.2"/>
          <path d="M13 13 Q16 11 19 13 Q19 16 16 17 Q19 18 19 21 Q16 23 13 21"
            stroke="#0e0e0e" stroke-width="1" fill="none"/>
        </svg>"""
    else:
        # 책/문서 느낌
        return """<svg width="32" height="32" viewBox="0 0 32 32" fill="none"
          xmlns="http://www.w3.org/2000/svg" style="opacity:.18;margin-bottom:8px" aria-hidden="true">
          <rect x="7" y="5" width="18" height="22" rx="1" stroke="#0e0e0e" stroke-width="1.2"/>
          <line x1="11" y1="11" x2="21" y2="11" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="11" y1="15" x2="21" y2="15" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="11" y1="19" x2="17" y2="19" stroke="#0e0e0e" stroke-width="1"/>
          <line x1="7" y1="5" x2="7" y2="27" stroke="#0e0e0e" stroke-width="2"/>
        </svg>"""


def build_html(date_str, rates, items_analyzed, big_picture):
    from datetime import datetime, timezone, timedelta
    KST = timezone(timedelta(hours=9))
    now = datetime.now(KST)
    weekday = WEEKDAY_KO[now.weekday()]
    usd = rates.get("usd_krw")
    jpy = rates.get("jpy_100")

    # intro: big_picture 첫 두 문장
    bp_sentences = big_picture.split(". ")
    intro = ". ".join(bp_sentences[:2]) + ("." if len(bp_sentences) > 1 else "")

    # ticker 콘텐츠 (×2 for infinite loop)
    ticker_items = ["USIKCLAW MORNING BRIEFING", date_str + " " + weekday + "요일"]
    if usd:
        ticker_items.append(f"USD/KRW {usd:,.1f}원")
    if jpy:
        ticker_items.append(f"100엔 {jpy:,.1f}원")
    ticker_items.append("BOOL KOREA")
    ticker_inner = "".join(
        f'<span class="ticker-item">{t}</span>' for t in ticker_items * 2
    )

    # 환율 rows
    rate_rows_sidebar = ""
    if usd:
        rate_rows_sidebar += (
            f'<div class="sidebar-rate-row">'
            f'<span class="sidebar-rate-val">{usd:,.1f}</span>'
            f'<span class="sidebar-rate-label">USD / KRW</span></div>'
        )
    if jpy:
        rate_rows_sidebar += (
            f'<div class="sidebar-rate-row">'
            f'<span class="sidebar-rate-val">{jpy:,.1f}</span>'
            f'<span class="sidebar-rate-label">100 JPY / KRW</span></div>'
        )

    rate_masthead = ""
    if usd:
        rate_masthead += f'<div class="rate">USD/KRW <span>{usd:,.1f}원</span></div>'
    if jpy:
        rate_masthead += f'<div class="rate">100엔 <span>{jpy:,.1f}원</span></div>'

    # 기사 카드
    cards_html = ""
    for i, item in enumerate(items_analyzed):
        accent = CAT_ACCENT.get(item["source"], "#333")
        pub_str = (
            f'<span class="source-date">{item["pub"]}</span>'
            if item.get("pub") else ""
        )
        illo = get_article_illo(item["source"])
        cards_html += (
            f'<div class="article" id="s{i+1}">'
            f'<div class="article-num">{str(i+1).zfill(2)}</div>'
            f'<div>'
            f'{illo}'
            f'<div class="article-source">'
            f'<span class="source-tag" style="color:{accent};border-color:{accent}">'
            f'{item["source"]}</span>{pub_str}</div>'
            f'<h2><a href="{item["link"]}" target="_blank" rel="noopener">'
            f'{item["headline"]}</a></h2>'
            f'<div class="article-meta">{item["title"][:80]}</div>'
            f'<div class="subhead">핵심 내용</div>'
            f'<div class="article-body">{item["summary"]}</div>'
            f'<div class="subhead">왜 중요한지</div>'
            f'<div class="article-body">{item["why_matters"]}</div>'
            f'<div class="insight-block">'
            f'<div class="subhead">🦊 우석 입장 인사이트</div>'
            f'<div class="article-body">{item["usuk_insight"]}</div>'
            f'</div></div></div>'
        )

    # 목차
    toc_html = ""
    for i, item in enumerate(items_analyzed):
        toc_html += (
            f'<div class="toc-item">'
            f'<span class="toc-num">{str(i+1).zfill(2)}</span>'
            f'<a class="toc-link" href="{item["link"]}" target="_blank">'
            f'[{item["source"]}] {item["headline"]}</a></div>'
        )

    # 날짜 포맷 (%-m, %-d: mac/linux)
    try:
        date_ko = now.strftime("%Y년 %-m월 %-d일")
    except Exception:
        date_ko = date_str

    css = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --ink:#0e0e0e;
  --paper:#f5f2ec;
  --cream:#ede9e0;
  --rule:#c8c0b0;
  --accent:#c0392b;
  --accent2:#1a3a5c;
  --muted:#7a7060;
}
html{scroll-behavior:smooth}
body{
  font-family:'DM Sans',sans-serif;
  background:var(--paper);
  color:var(--ink);
  min-height:100vh;
  font-size:16px;
  line-height:1.7;
}
a{color:inherit;text-decoration:none}
a:hover{color:var(--accent)}

/* TICKER */
.ticker{
  background:var(--ink);
  color:#f5f2ec;
  font-family:'DM Mono',monospace;
  font-size:11px;
  letter-spacing:.06em;
  padding:8px 0;
  overflow:hidden;
  white-space:nowrap;
}
.ticker-inner{display:inline-block;animation:ticker 28s linear infinite}
@keyframes ticker{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.ticker-item{display:inline-block;padding:0 40px}

/* MASTHEAD */
.masthead{
  border-bottom:3px solid var(--ink);
  padding:40px 48px 28px;
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:24px;
}
.masthead-label{
  font-family:'DM Mono',monospace;
  font-size:10px;
  letter-spacing:.18em;
  text-transform:uppercase;
  color:var(--muted);
  margin-bottom:8px;
}
.masthead h1{
  font-family:'Playfair Display',serif;
  font-size:clamp(40px,6vw,72px);
  font-weight:900;
  line-height:.95;
  letter-spacing:-.02em;
}
.masthead h1 em{font-style:italic;color:var(--accent)}
.masthead-illo{flex-shrink:0;align-self:center}
.masthead-right{text-align:right;flex-shrink:0}
.masthead-date{
  font-family:'Playfair Display',serif;
  font-size:13px;
  font-style:italic;
  color:var(--muted);
  margin-bottom:6px;
}
.masthead-rates{display:flex;flex-direction:column;align-items:flex-end;gap:3px}
.rate{font-family:'DM Mono',monospace;font-size:12px}
.rate span{color:var(--accent);font-weight:500}

/* LAYOUT */
.layout{
  max-width:1200px;
  margin:0 auto;
  padding:0 48px 96px;
  display:grid;
  grid-template-columns:1fr 300px;
  gap:0 60px;
  align-items:start;
}

/* SECTION DIVIDER */
.section-head{
  display:flex;
  align-items:center;
  gap:14px;
  margin:40px 0 20px;
}
.section-head-line{flex:1;height:1px;background:var(--rule)}
.section-head-label{
  font-family:'DM Mono',monospace;
  font-size:10px;
  letter-spacing:.16em;
  text-transform:uppercase;
  color:var(--muted);
  flex-shrink:0;
}

/* LEAD */
.lead{
  margin:40px 0 0;
  padding-bottom:36px;
  border-bottom:2px solid var(--ink);
}
.lead-eyebrow{
  font-family:'DM Mono',monospace;
  font-size:10px;
  letter-spacing:.16em;
  text-transform:uppercase;
  color:var(--accent);
  margin-bottom:12px;
}
.lead-headline{
  font-family:'Playfair Display',serif;
  font-size:clamp(22px,3.5vw,32px);
  font-weight:700;
  line-height:1.25;
  margin-bottom:16px;
  letter-spacing:-.01em;
}
.lead-body{font-size:15.5px;color:#2a2a2a;line-height:1.78;max-width:64ch}

/* ARTICLE CARDS */
.article{
  padding:28px 0;
  border-bottom:1px solid var(--rule);
  display:grid;
  grid-template-columns:auto 1fr;
  gap:0 24px;
}
.article-num{
  font-family:'Playfair Display',serif;
  font-size:11px;
  font-style:italic;
  color:var(--rule);
  padding-top:4px;
  min-width:20px;
}
.article-source{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.source-tag{
  font-family:'DM Mono',monospace;
  font-size:9px;
  letter-spacing:.14em;
  text-transform:uppercase;
  padding:3px 8px;
  border:1px solid currentColor;
  font-weight:500;
}
.source-date{font-family:'DM Mono',monospace;font-size:10px;color:var(--muted)}
.article h2{
  font-family:'Playfair Display',serif;
  font-size:clamp(17px,2.2vw,21px);
  font-weight:700;
  line-height:1.3;
  letter-spacing:-.01em;
  margin-bottom:10px;
}
.article-meta{font-size:11.5px;color:var(--muted);margin-bottom:12px;font-style:italic}
.subhead{
  font-family:'DM Mono',monospace;
  font-size:9px;
  letter-spacing:.14em;
  text-transform:uppercase;
  color:var(--muted);
  margin:12px 0 4px;
}
.article-body{font-size:14px;color:#333;line-height:1.74}
.insight-block{
  margin-top:14px;
  padding:12px 16px;
  border-left:3px solid var(--accent);
  background:rgba(192,57,43,.04);
}
.insight-block .subhead{color:var(--accent);margin-top:0}
.insight-block .article-body{color:#2a2020}

/* SIDEBAR */
.sidebar{
  padding:40px 0 0 40px;
  border-left:1px solid var(--rule);
  position:sticky;
  top:24px;
}
.sidebar-section{margin-bottom:36px}
.sidebar-label{
  font-family:'DM Mono',monospace;
  font-size:9px;
  letter-spacing:.18em;
  text-transform:uppercase;
  color:var(--muted);
  border-bottom:1px solid var(--rule);
  padding-bottom:6px;
  margin-bottom:14px;
}
.sidebar-body{font-size:13.5px;line-height:1.72;color:#2a2a2a}
.sidebar-rate-row{margin-bottom:8px}
.sidebar-rate-val{
  font-family:'DM Mono',monospace;
  font-size:20px;
  font-weight:500;
  display:block;
  letter-spacing:-.01em;
}
.sidebar-rate-label{font-size:11px;color:var(--muted)}
.toc-item{display:flex;gap:10px;margin-bottom:10px;font-size:13px;line-height:1.4}
.toc-num{
  font-family:'DM Mono',monospace;
  font-size:10px;
  color:var(--muted);
  flex-shrink:0;
  padding-top:2px;
}
.sidebar-illo{opacity:.15;text-align:center;margin:4px 0 24px}

/* FOOTER */
.site-footer{
  border-top:3px solid var(--ink);
  padding:20px 48px;
  display:flex;
  justify-content:space-between;
  align-items:center;
  font-family:'DM Mono',monospace;
  font-size:10px;
  letter-spacing:.06em;
  color:var(--muted);
}

/* ANIMATIONS */
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
.lead,.articles,.sidebar{animation:fadeUp .6s ease both}
.articles{animation-delay:.1s}
.sidebar{animation-delay:.2s}

/* RESPONSIVE */
@media(max-width:900px){
  .layout{grid-template-columns:1fr;padding:0 24px 64px}
  .sidebar{border-left:none;border-top:2px solid var(--ink);padding:28px 0 0;margin-top:40px}
  .masthead{padding:28px 24px 20px;flex-direction:column;align-items:flex-start}
  .masthead-illo{display:none}
  .masthead-right{text-align:left}
  .masthead-rates{align-items:flex-start}
  .site-footer{flex-direction:column;gap:6px;padding:16px 24px}
}
"""

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Briefing / {date_str}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>

<div class="ticker"><div class="ticker-inner">{ticker_inner}</div></div>

<header class="masthead">
  <div class="masthead-left">
    <div class="masthead-label">Daily Intelligence · {date_str}</div>
    <h1>Morning<br><em>Briefing</em></h1>
  </div>
  <div class="masthead-illo">{SVG_SUN}</div>
  <div class="masthead-right">
    <div class="masthead-date">{weekday}요일, {date_ko}</div>
    <div class="masthead-rates">{rate_masthead}</div>
  </div>
</header>

<div class="layout">
  <main>
    <div class="lead">
      <div class="lead-eyebrow">🦊 Today's Perspective</div>
      <div class="lead-headline">{intro}</div>
      <div class="lead-body">{big_picture}</div>
    </div>

    <div class="section-head">
      <div class="section-head-label">Sources &amp; Analysis</div>
      <div class="section-head-line"></div>
      {SVG_DOTS}
    </div>

    <div class="articles">{cards_html}</div>
  </main>

  <aside class="sidebar">
    <div class="sidebar-section">
      <div class="sidebar-label">Exchange Rates</div>
      {rate_rows_sidebar}
    </div>

    <div class="sidebar-illo">{SVG_CHART}</div>

    <div class="sidebar-section">
      <div class="sidebar-label">Today's Sources</div>
      {toc_html}
    </div>

    <div class="sidebar-illo" style="margin:24px 0 0">{SVG_FOX}</div>

    <div class="sidebar-section">
      <div class="sidebar-label">About</div>
      <div class="sidebar-body">
        claw의 매일 아침 브리핑.<br>
        AI 트렌드, 스타트업 뉴스, 경제 지표를<br>
        우석 관점으로 요약합니다.
      </div>
    </div>
  </aside>
</div>

<footer class="site-footer">
  <span>USIKCLAW — BOOL KOREA</span>
  {SVG_FOOTER_DECO}
  <span>{date_str} 자동 생성</span>
</footer>

</body>
</html>"""

    return html
