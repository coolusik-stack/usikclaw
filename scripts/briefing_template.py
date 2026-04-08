"""
briefing_template.py — Mono-Chromatic Precision briefing template
"""

WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]

ACCENTS = {
    "OpenAI 뉴스": "#9EFF00",
    "Anthropic 뉴스": "#ff7a00",
    "AI 테크 트렌드": "#9EFF00",
    "경제 매크로": "#ff7a00",
    "Lenny's": "#9EFF00",
    "Sandhill": "#9EFF00",
    "Chamath": "#ff7a00",
}


def build_html(date_str, rates, items_analyzed, big_picture):
    from datetime import datetime, timezone, timedelta
    KST = timezone(timedelta(hours=9))
    now = datetime.now(KST)
    weekday = WEEKDAY_KO[now.weekday()]
    usd = rates.get("usd_krw")
    jpy = rates.get("jpy_100")

    bp_sentences = big_picture.split(". ")
    intro = ". ".join(bp_sentences[:2]) + ("." if len(bp_sentences) > 1 else "")

    rate_strip = []
    if usd:
        rate_strip.append(f"USD/KRW {usd:,.1f}원")
    if jpy:
        rate_strip.append(f"100JPY/KRW {jpy:,.1f}원")
    rate_strip_html = " · ".join(rate_strip)

    cards_html = ""
    toc_html = ""
    for i, item in enumerate(items_analyzed, 1):
        accent = ACCENTS.get(item["source"], "#9EFF00")
        pub = item.get("pub", "")
        toc_html += (
            f'<div class="toc-row"><span class="toc-index">{str(i).zfill(2)}</span>'
            f'<span class="toc-text">{item["headline"]}</span></div>'
        )
        cards_html += f'''
        <article class="entry">
          <div class="entry-kicker-row">
            <span class="entry-kicker" style="color:{accent};border-color:{accent}">{item['source']}</span>
            <span class="entry-date">{pub}</span>
          </div>
          <h2>{item['headline']}</h2>
          <div class="entry-meta">{item['title']}</div>
          <div class="entry-grid">
            <div class="entry-label">SUMMARY</div>
            <div class="entry-body">{item['summary']}</div>
            <div class="entry-label">WHY IT MATTERS</div>
            <div class="entry-body">{item['why_matters']}</div>
            <div class="entry-label insight">INSIGHT</div>
            <div class="entry-body insight-body">{item['usuk_insight']}</div>
          </div>
          <a class="entry-link" href="{item['link']}" target="_blank" rel="noopener">SOURCE ↗</a>
        </article>
        '''

    css = '''
    *{box-sizing:border-box;margin:0;padding:0}
    :root{
      --bg:#050505;
      --panel:#0d0d0d;
      --panel2:#111111;
      --line:#262626;
      --text:#f5f5f5;
      --muted:#8a8a8a;
      --soft:#b3b3b3;
      --lime:#9EFF00;
      --orange:#ff7a00;
    }
    html{scroll-behavior:smooth}
    body{
      font-family:Inter, Space Grotesk, Arial, sans-serif;
      background:var(--bg);
      color:var(--text);
      min-height:100vh;
      line-height:1.65;
    }
    a{text-decoration:none;color:inherit}
    .page{
      width:min(1440px, calc(100vw - 40px));
      margin:20px auto 60px;
      border:1px solid var(--line);
      background:linear-gradient(180deg,#050505 0%, #0a0a0a 100%);
      position:relative;
      overflow:hidden;
    }
    .grid-lines::before,
    .grid-lines::after{
      content:"";
      position:absolute;
      top:0;bottom:0;
      width:1px;
      background:rgba(255,255,255,.06);
      pointer-events:none;
    }
    .grid-lines::before{left:72px}
    .grid-lines::after{right:320px}
    .topbar{
      display:flex;
      justify-content:space-between;
      gap:20px;
      border-bottom:1px solid var(--line);
      padding:12px 24px 12px 88px;
      font-family:"JetBrains Mono", monospace;
      font-size:11px;
      letter-spacing:.12em;
      text-transform:uppercase;
      color:var(--soft);
    }
    .hero{
      display:grid;
      grid-template-columns:minmax(0,1fr) 280px;
      gap:36px;
      padding:32px 24px 32px 88px;
      border-bottom:1px solid var(--line);
    }
    .hero-left{min-width:0}
    .hero-label{
      font-family:"JetBrains Mono", monospace;
      font-size:11px;
      letter-spacing:.18em;
      text-transform:uppercase;
      color:var(--muted);
      margin-bottom:16px;
    }
    .hero h1{
      font-size:clamp(52px, 8vw, 116px);
      line-height:.86;
      letter-spacing:-.07em;
      font-weight:800;
      max-width:9ch;
      margin-bottom:18px;
    }
    .hero-intro{
      max-width:62ch;
      color:#d8d8d8;
      font-size:16px;
    }
    .hero-side{
      border-left:1px solid var(--line);
      padding-left:24px;
      display:flex;
      flex-direction:column;
      gap:18px;
    }
    .meta-block{}
    .meta-label{
      font-family:"JetBrains Mono", monospace;
      font-size:10px;
      letter-spacing:.16em;
      text-transform:uppercase;
      color:var(--muted);
      margin-bottom:6px;
    }
    .meta-value{
      font-size:18px;
      line-height:1.25;
      font-weight:700;
      color:var(--text);
      letter-spacing:-.03em;
    }
    .meta-sub{font-size:13px;color:var(--soft);line-height:1.5}
    .canvas{
      display:grid;
      grid-template-columns:minmax(0,1fr) 280px;
      gap:36px;
      padding:0 24px 32px 88px;
    }
    .main{padding-top:28px}
    .sidebar{padding-top:28px;border-left:1px solid var(--line);padding-left:24px}
    .section-tag{
      font-family:"JetBrains Mono", monospace;
      font-size:10px;
      letter-spacing:.18em;
      text-transform:uppercase;
      color:var(--muted);
      margin-bottom:18px;
    }
    .big-picture{
      padding:0 0 28px;
      border-bottom:1px solid var(--line);
      margin-bottom:24px;
    }
    .big-picture h3{
      font-size:22px;
      line-height:1.15;
      letter-spacing:-.04em;
      margin-bottom:10px;
      max-width:20ch;
    }
    .big-picture p{font-size:15px;color:#d6d6d6;max-width:66ch}
    .entry{
      padding:22px 0 26px;
      border-bottom:1px solid var(--line);
    }
    .entry-kicker-row{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:16px;
      margin-bottom:12px;
    }
    .entry-kicker{
      display:inline-flex;
      align-items:center;
      height:24px;
      padding:0 10px;
      border:1px solid currentColor;
      font-family:"JetBrains Mono", monospace;
      font-size:10px;
      letter-spacing:.16em;
      text-transform:uppercase;
    }
    .entry-date{
      font-family:"JetBrains Mono", monospace;
      font-size:11px;
      color:var(--muted);
    }
    .entry h2{
      font-size:clamp(26px, 3vw, 40px);
      line-height:.98;
      letter-spacing:-.06em;
      margin-bottom:10px;
      max-width:18ch;
    }
    .entry-meta{
      color:var(--muted);
      font-size:13px;
      margin-bottom:16px;
      max-width:70ch;
    }
    .entry-grid{
      display:grid;
      grid-template-columns:140px minmax(0,1fr);
      gap:8px 20px;
      align-items:start;
    }
    .entry-label{
      font-family:"JetBrains Mono", monospace;
      font-size:10px;
      letter-spacing:.14em;
      text-transform:uppercase;
      color:var(--soft);
      padding-top:2px;
    }
    .entry-label.insight{color:var(--lime)}
    .entry-body{
      font-size:15px;
      color:#ededed;
      padding-bottom:6px;
    }
    .insight-body{color:#e9ffd0}
    .entry-link{
      display:inline-block;
      margin-top:12px;
      font-family:"JetBrains Mono", monospace;
      font-size:11px;
      letter-spacing:.14em;
      text-transform:uppercase;
      color:var(--orange);
    }
    .toc-box{
      margin-bottom:26px;
      padding-bottom:22px;
      border-bottom:1px solid var(--line);
    }
    .toc-row{
      display:grid;
      grid-template-columns:34px 1fr;
      gap:12px;
      padding:10px 0;
      border-top:1px solid rgba(255,255,255,.04);
    }
    .toc-index{
      font-family:"JetBrains Mono", monospace;
      color:var(--muted);
      font-size:11px;
    }
    .toc-text{
      font-size:13px;
      color:#ddd;
      line-height:1.45;
    }
    .sidebar-note{
      font-size:14px;
      color:#d0d0d0;
      line-height:1.7;
    }
    .footer{
      border-top:1px solid var(--line);
      display:flex;
      justify-content:space-between;
      gap:16px;
      padding:14px 24px 14px 88px;
      font-family:"JetBrains Mono", monospace;
      font-size:11px;
      letter-spacing:.12em;
      text-transform:uppercase;
      color:var(--muted);
    }
    @media (max-width: 980px){
      .grid-lines::before,.grid-lines::after{display:none}
      .hero,.canvas{grid-template-columns:1fr;padding-left:24px}
      .topbar,.footer{padding-left:24px}
      .hero-side,.sidebar{border-left:none;padding-left:0}
      .entry-grid{grid-template-columns:1fr}
      .hero h1{max-width:none}
    }
    '''

    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Briefing / {date_str}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
  <div class="page grid-lines">
    <div class="topbar">
      <span>MORNING BRIEFING / {date_str} / {weekday}요일</span>
      <span>{rate_strip_html or 'RATE DATA'}</span>
    </div>

    <section class="hero">
      <div class="hero-left">
        <div class="hero-label">Monolithic Canvas / Daily Intelligence</div>
        <h1>Morning<br>Briefing</h1>
        <div class="hero-intro">{intro}</div>
      </div>
      <div class="hero-side">
        <div class="meta-block">
          <div class="meta-label">Date</div>
          <div class="meta-value">{date_str}</div>
          <div class="meta-sub">{weekday}요일</div>
        </div>
        <div class="meta-block">
          <div class="meta-label">Exchange</div>
          <div class="meta-value">{f'{usd:,.1f}원' if usd else '-'}</div>
          <div class="meta-sub">USD/KRW</div>
        </div>
        <div class="meta-block">
          <div class="meta-value">{f'{jpy:,.1f}원' if jpy else '-'}</div>
          <div class="meta-sub">100JPY/KRW</div>
        </div>
      </div>
    </section>

    <section class="canvas">
      <main class="main">
        <div class="section-tag">Big Picture</div>
        <div class="big-picture">
          <h3>{intro}</h3>
          <p>{big_picture}</p>
        </div>

        <div class="section-tag">Entries</div>
        {cards_html}
      </main>

      <aside class="sidebar">
        <div class="section-tag">Index</div>
        <div class="toc-box">{toc_html}</div>

        <div class="section-tag">Notes</div>
        <div class="sidebar-note">
          이 페이지는 전날 업데이트된 소식만 기준으로 정리합니다.<br><br>
          큰 톤은 단색 중심으로 유지하고, 강조는 최소한의 기술적 포인트 컬러로만 처리합니다.<br><br>
          우석 관점에선 새 기능 자체보다, 실제 운영·비용·도입 흐름에 어떤 영향을 주는지가 더 중요합니다.
        </div>
      </aside>
    </section>

    <footer class="footer">
      <span>USIKCLAW / BOOL KOREA</span>
      <span>MONO-CHROMATIC PRECISION</span>
    </footer>
  </div>
</body>
</html>'''
    return html
