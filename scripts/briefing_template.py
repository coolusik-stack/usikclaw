"""
briefing_template.py — Vercel-leaning mono precision briefing template
"""

WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]

ACCENTS = {
    "OpenAI 뉴스": "#8BE26A",
    "Anthropic 뉴스": "#8BE26A",
    "AI 테크 트렌드": "#8BE26A",
    "경제 매크로": "#8BE26A",
    "Lenny's": "#8BE26A",
    "Sandhill": "#8BE26A",
    "Chamath": "#8BE26A",
    "AI 뉴스": "#8BE26A",
}


def build_html(date_str, rates, items_analyzed, big_picture, source_statuses=None):
    from datetime import datetime, timezone, timedelta
    KST = timezone(timedelta(hours=9))
    now = datetime.now(KST)
    weekday = WEEKDAY_KO[now.weekday()]
    usd = rates.get("usd_krw")
    jpy = rates.get("jpy_100")

    bp_sentences = big_picture.split(". ")
    intro = ". ".join(bp_sentences[:2]) + ("." if len(bp_sentences) > 1 else "")

    rate_rows = []
    if usd:
        rate_rows.append(("USD/KRW", f"{usd:,.1f}원"))
    if jpy:
        rate_rows.append(("100JPY/KRW", f"{jpy:,.1f}원"))

    cards_html = ""
    toc_html = ""
    for i, item in enumerate(items_analyzed, 1):
        accent = ACCENTS.get(item["source"], "#8BE26A")
        pub = item.get("pub", "")
        toc_html += (
            f'<div class="toc-row"><span class="toc-no">{str(i).zfill(2)}</span>'
            f'<span class="toc-title">{item["headline"]}</span></div>'
        )
        cards_html += f'''
        <article class="card">
          <div class="card-top">
            <span class="chip" style="color:{accent};border-color:{accent}33;background:{accent}10">{item['source']}</span>
            <span class="date">{pub}</span>
          </div>
          <h2>{item['headline']}</h2>
          <div class="meta">{item['title']}</div>
          <div class="body-grid">
            <div class="label">SUMMARY</div>
            <div class="body">{item['summary']}</div>
            <div class="label">WHY IT MATTERS</div>
            <div class="body">{item['why_matters']}</div>
            <div class="label insight">INSIGHT</div>
            <div class="body insight-body">{item['usuk_insight']}</div>
          </div>
          <a class="source-link" href="{item['link']}" target="_blank" rel="noopener">Open source ↗</a>
        </article>
        '''

    sidebar_rates = "".join(
        f'<div class="stat-row"><span>{k}</span><strong>{v}</strong></div>' for k, v in rate_rows
    )
    source_status_html = ""
    for s in (source_statuses or []):
        if s.get("status") == "updated":
            source_status_html += f'<div class="toc-row"><span class="toc-no">●</span><span class="toc-title">{s["source"]} / 업데이트</span></div>'
        else:
            source_status_html += f'<div class="toc-row"><span class="toc-no">○</span><span class="toc-title">{s["source"]} / 업데이트 없음</span></div>'

    css = '''
    *{box-sizing:border-box;margin:0;padding:0}
    :root{
      --bg:#f6f6f4;
      --panel:#ffffff;
      --panel2:#fbfbfa;
      --line:#e8e8e3;
      --line2:#ddddD6;
      --text:#111111;
      --muted:#6f6f69;
      --soft:#4c4c47;
      --accent:#0f7a2f;
      --radius:22px;
    }
    html{scroll-behavior:smooth}
    body{
      font-family:Inter, Arial, sans-serif;
      background:
        radial-gradient(circle at top, rgba(0,0,0,.03), transparent 38%),
        linear-gradient(180deg, #fafaf8 0%, #f4f4f1 100%);
      color:var(--text);
      min-height:100vh;
      line-height:1.6;
      -webkit-font-smoothing:antialiased;
    }
    a{text-decoration:none;color:inherit}
    .wrap{
      width:min(1400px, calc(100vw - 32px));
      margin:18px auto 56px;
    }
    .topbar{
      display:flex;
      justify-content:space-between;
      gap:20px;
      padding:12px 14px;
      color:var(--muted);
      font-family:"JetBrains Mono", monospace;
      font-size:11px;
      letter-spacing:.14em;
      text-transform:uppercase;
    }
    .shell{
      border:1px solid var(--line);
      background:rgba(255,255,255,.88);
      border-radius:28px;
      overflow:hidden;
      box-shadow:0 12px 40px rgba(0,0,0,.06);
      backdrop-filter: blur(10px);
    }
    .hero{
      display:grid;
      grid-template-columns:minmax(0,1fr) 300px;
      gap:32px;
      padding:46px 34px 34px;
      border-bottom:1px solid var(--line);
    }
    .hero-kicker,
    .section-kicker,
    .label{
      font-family:"JetBrains Mono", monospace;
      font-size:10px;
      letter-spacing:.18em;
      text-transform:uppercase;
    }
    .hero-kicker{color:var(--muted);margin-bottom:16px}
    h1{
      font-size:clamp(52px, 8vw, 96px);
      line-height:.9;
      letter-spacing:-.08em;
      font-weight:800;
      max-width:8ch;
      margin-bottom:18px;
    }
    .hero-intro{
      font-size:16px;
      color:#2d2d29;
      max-width:64ch;
      line-height:1.75;
    }
    .hero-side{
      display:flex;
      flex-direction:column;
      gap:14px;
      padding-left:12px;
    }
    .hero-panel{
      border:1px solid var(--line2);
      background:linear-gradient(180deg,#ffffff 0%,#f7f7f4 100%);
      border-radius:20px;
      padding:16px;
    }
    .hero-panel .title{
      color:var(--muted);
      font-family:"JetBrains Mono", monospace;
      font-size:10px;
      letter-spacing:.16em;
      text-transform:uppercase;
      margin-bottom:10px;
    }
    .hero-panel .value{
      font-size:22px;
      font-weight:700;
      letter-spacing:-.04em;
      line-height:1.15;
    }
    .hero-panel .sub{
      color:var(--muted);
      font-size:13px;
      margin-top:6px;
      line-height:1.5;
    }
    .content{
      display:grid;
      grid-template-columns:minmax(0,1fr) 300px;
      gap:32px;
      padding:28px 34px 34px;
    }
    .section-kicker{color:var(--muted);margin-bottom:16px}
    .big-picture{
      margin-bottom:26px;
      padding:0 0 26px;
      border-bottom:1px solid var(--line);
    }
    .big-picture h3{
      font-size:28px;
      line-height:1.06;
      letter-spacing:-.06em;
      max-width:18ch;
      margin-bottom:12px;
      font-weight:700;
    }
    .big-picture p{
      color:#33332f;
      font-size:15px;
      line-height:1.8;
      max-width:68ch;
    }
    .card{
      border:1px solid var(--line2);
      background:linear-gradient(180deg,#ffffff 0%,#fafaf8 100%);
      border-radius:var(--radius);
      padding:20px;
      margin-bottom:14px;
      transition:transform .18s ease, border-color .18s ease, background .18s ease, box-shadow .18s ease;
    }
    .card:hover{
      transform:translateY(-2px);
      border-color:#cfcfc8;
      background:linear-gradient(180deg,#ffffff 0%,#f7f7f3 100%);
      box-shadow:0 10px 28px rgba(0,0,0,.05);
    }
    .card-top{
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:12px;
      margin-bottom:12px;
    }
    .chip{
      display:inline-flex;
      align-items:center;
      height:24px;
      padding:0 10px;
      border:1px solid currentColor;
      border-radius:999px;
      font-family:"JetBrains Mono", monospace;
      font-size:10px;
      letter-spacing:.16em;
      text-transform:uppercase;
    }
    .date{
      color:var(--muted);
      font-family:"JetBrains Mono", monospace;
      font-size:11px;
    }
    .card h2{
      font-size:clamp(26px, 3vw, 38px);
      line-height:.98;
      letter-spacing:-.06em;
      font-weight:750;
      margin-bottom:10px;
      max-width:19ch;
    }
    .meta{
      color:var(--muted);
      font-size:13px;
      line-height:1.55;
      margin-bottom:16px;
      max-width:70ch;
    }
    .body-grid{
      display:grid;
      grid-template-columns:120px minmax(0,1fr);
      gap:10px 22px;
      align-items:start;
    }
    .label{color:var(--muted);padding-top:3px}
    .label.insight{color:var(--accent)}
    .body{font-size:15px;color:#1f1f1c;line-height:1.78}
    .insight-body{color:#145728}
    .source-link{
      display:inline-block;
      margin-top:14px;
      color:var(--soft);
      font-family:"JetBrains Mono", monospace;
      font-size:11px;
      letter-spacing:.14em;
      text-transform:uppercase;
    }
    .source-link:hover{color:var(--accent)}
    .sidebar-panel{
      border:1px solid var(--line2);
      background:linear-gradient(180deg,#0f0f0f 0%,#0b0b0b 100%);
      border-radius:20px;
      padding:18px;
      margin-bottom:14px;
    }
    .toc-row{
      display:grid;
      grid-template-columns:34px 1fr;
      gap:12px;
      padding:10px 0;
      border-top:1px solid rgba(255,255,255,.04);
    }
    .toc-no{
      color:var(--muted);
      font-family:"JetBrains Mono", monospace;
      font-size:11px;
    }
    .toc-title{
      color:#252521;
      font-size:13px;
      line-height:1.45;
    }
    .stat-row{
      display:flex;
      justify-content:space-between;
      gap:14px;
      padding:10px 0;
      border-top:1px solid rgba(255,255,255,.05);
      color:#dfdfdf;
      font-size:13px;
    }
    .stat-row strong{
      font-weight:700;
      letter-spacing:-.02em;
    }
    .note-body{
      color:#343430;
      font-size:14px;
      line-height:1.75;
    }
    .footer{
      display:flex;
      justify-content:space-between;
      gap:20px;
      padding:16px 34px;
      border-top:1px solid var(--line);
      color:var(--muted);
      font-family:"JetBrains Mono", monospace;
      font-size:11px;
      letter-spacing:.14em;
      text-transform:uppercase;
    }
    @media (max-width: 980px){
      .hero,.content{grid-template-columns:1fr}
      .hero-side{padding-left:0}
      .body-grid{grid-template-columns:1fr}
      .wrap{width:min(100vw - 16px, 1400px)}
      .topbar,.footer{padding-left:18px;padding-right:18px}
      .hero,.content{padding-left:18px;padding-right:18px}
      h1{max-width:none}
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
  <div class="wrap">
    <div class="topbar">
      <span>MORNING BRIEFING / {date_str}</span>
      <span>{weekday}요일</span>
    </div>

    <div class="shell">
      <section class="hero">
        <div>
          <div class="hero-kicker">Daily Intelligence / Vercel-Leaning Mono Precision</div>
          <h1>Morning<br>Briefing</h1>
          <div class="hero-intro">{intro}</div>
        </div>
        <div class="hero-side">
          <div class="hero-panel">
            <div class="title">Date</div>
            <div class="value">{date_str}</div>
            <div class="sub">{weekday}요일</div>
          </div>
          <div class="hero-panel">
            <div class="title">Exchange</div>
            <div class="sub">전날 기준 참고 지표</div>
            {sidebar_rates or '<div class="stat-row"><span>USD/KRW</span><strong>-</strong></div>'}
          </div>
        </div>
      </section>

      <section class="content">
        <main>
          <div class="section-kicker">Big Picture</div>
          <div class="big-picture">
            <h3>{intro}</h3>
            <p>{big_picture}</p>
          </div>

          <div class="section-kicker">Entries</div>
          {cards_html}
        </main>

        <aside>
          <div class="sidebar-panel">
            <div class="section-kicker">Index</div>
            {toc_html}
          </div>
          <div class="sidebar-panel">
            <div class="section-kicker">Source Status</div>
            {source_status_html}
          </div>
          <div class="sidebar-panel">
            <div class="section-kicker">Notes</div>
            <div class="note-body">
              전날 공개된 소식만 기준으로 정리합니다.<br><br>
              업데이트가 없는 소스는 오른쪽에 별도로 표시합니다.<br><br>
              우석 기준에선 새 기능보다 실제 운영과 비용 판단에 어떤 영향을 주는지가 더 중요합니다.
            </div>
          </div>
        </aside>
      </section>

      <footer class="footer">
        <span>USIKCLAW / BOOL KOREA</span>
        <span>VERCEL-LEANING BRIEFING SURFACE</span>
      </footer>
    </div>
  </div>
</body>
</html>'''
    return html
