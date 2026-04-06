#!/usr/bin/env python3
"""
morning_briefing_v2.py
매일 아침 9시 실행.
1. Google News RSS로 AI/테크, 경제/환율, BOOL/니코틴 뉴스 수집
2. 환율 조회
3. claw 의견 생성 (규칙 기반 + 뉴스 반영)
4. 다크 테마 HTML → GitHub Pages briefing/YYYY-MM-DD.html 저장/푸시
5. 노션 '📋 브리핑 기록' 저장
6. 텔레그램: 핵심 요약 + claw 의견 + GitHub Pages 링크 + 노션 링크
"""

import json, ssl, subprocess, urllib.request, sys, os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET

ctx = ssl.create_default_context()
KST = timezone(timedelta(hours=9))
NOTION_KEY = Path.home() / ".config" / "notion" / "api_key"
NOTION_WS  = Path.home() / ".config" / "notion" / "workspace.json"
REPO_DIR   = Path.home() / ".openclaw" / "briefing_repo"
REPO_URL   = "https://github.com/coolusik-stack/usikclaw.git"

WEEKDAY_KO = ["월","화","수","목","금","토","일"]


# ─── 환율 ────────────────────────────────────────────
def get_rates():
    try:
        req = urllib.request.Request(
            "https://open.er-api.com/v6/latest/USD",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            d = json.loads(r.read())
        krw = d["rates"].get("KRW")
        jpy = d["rates"].get("JPY")
        return {
            "usd_krw": round(krw, 1) if krw else None,
            "jpy_100": round(krw / jpy * 100, 1) if (krw and jpy) else None
        }
    except Exception as e:
        return {"usd_krw": None, "jpy_100": None, "error": str(e)}


# ─── Google News RSS ──────────────────────────────────
def fetch_rss(url, max_items=5):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            root = ET.fromstring(r.read())
        items = []
        for item in root.findall(".//item")[:max_items]:
            title = (item.findtext("title") or "").strip()
            link  = (item.findtext("link")  or "").strip()
            src   = ""
            for child in item:
                if child.tag.endswith("source"):
                    src = child.text or ""
            if title and link:
                items.append({"title": title, "link": link, "source": src})
        return items
    except:
        return []


def get_all_news():
    return {
        "AI / 테크": fetch_rss(
            "https://news.google.com/rss/search?q=AI+인공지능+Claude+OpenAI+Gemini+LLM&hl=ko&gl=KR&ceid=KR:ko",
            max_items=5
        ),
        "경제 / 환율": fetch_rss(
            "https://news.google.com/rss/search?q=환율+원달러+코스피+금리+경기&hl=ko&gl=KR&ceid=KR:ko",
            max_items=4
        ),
        "BOOL / 니코틴파우치": fetch_rss(
            "https://news.google.com/rss/search?q=니코틴파우치+BOOL+더바코+전자담배+규제&hl=ko&gl=KR&ceid=KR:ko",
            max_items=4
        ),
    }


# ─── claw 의견 생성 ────────────────────────────────────
def make_opinion(rates, news):
    parts = []

    usd = rates.get("usd_krw")
    jpy = rates.get("jpy_100")

    # 환율 판단
    if usd:
        if usd >= 1560:
            parts.append(f"환율이 {usd:,.0f}원으로 상당히 높습니다. 수입 원가 부담이 크고, 금리 방향을 주시할 필요가 있습니다.")
        elif usd >= 1520:
            parts.append(f"환율 {usd:,.0f}원 — 안심하기엔 이릅니다. 중동 리스크와 달러 강세가 겹쳐 변동성이 큽니다.")
        elif usd >= 1480:
            parts.append(f"환율 {usd:,.0f}원. 큰 이상 없지만 방향성은 계속 달러 강세 쪽입니다.")
        else:
            parts.append(f"환율 {usd:,.0f}원으로 비교적 안정적입니다.")

    # AI 뉴스 판단
    ai_items = news.get("AI / 테크", [])
    ai_titles = " ".join(i["title"] for i in ai_items).lower()
    if any(k in ai_titles for k in ["agent", "에이전트", "codex", "claude"]):
        parts.append("AI 에이전트 관련 소식이 많습니다. 단순 모델 데모에서 실제 업무 자동화로 중심이 이동하는 흐름이 계속되고 있습니다.")
    if any(k in ai_titles for k in ["gemini", "gemma", "google"]):
        parts.append("Google AI 업데이트도 주목할 만합니다. Gemini/Gemma 생태계가 빠르게 확장되고 있어요.")

    # BOOL 뉴스 판단
    bool_items = news.get("BOOL / 니코틴파우치", [])
    if bool_items:
        bool_titles = " ".join(i["title"] for i in bool_items).lower()
        if any(k in bool_titles for k in ["규제", "금지", "단속", "법"]):
            parts.append(f"⚠️ BOOL/니코틴파우치 관련 규제·단속 뉴스가 {len(bool_items)}건 감지됐습니다. 구체적 내용 확인 권장합니다.")
        else:
            parts.append(f"BOOL/니코틴파우치 관련 기사 {len(bool_items)}건. 큰 이슈 없지만 업계 동향으로 모니터링 중입니다.")
    else:
        parts.append("BOOL/니코틴파우치 관련 주목할 뉴스는 오늘 없습니다.")

    return " ".join(parts) if parts else "오늘은 특이 동향 없습니다."


# ─── HTML 생성 ────────────────────────────────────────
def build_html(date_str, rates, news, opinion):
    now = datetime.now(KST)
    weekday = WEEKDAY_KO[now.weekday()]
    usd = rates.get("usd_krw")
    jpy = rates.get("jpy_100")

    rate_badge = ""
    if usd:
        rate_badge = f'<span class="rate-badge">USD/KRW {usd:,.1f}원</span>'
        if jpy:
            rate_badge += f'<span class="rate-badge">100엔 {jpy:,.1f}원</span>'

    categories_html = ""
    cat_colors = {
        "AI / 테크":           ("#7eb8f7", "#1a2a3a"),
        "경제 / 환율":          ("#f7c97e", "#2a2010"),
        "BOOL / 니코틴파우치": ("#7ef7a0", "#102a18"),
    }

    for cat, items in news.items():
        color, bg = cat_colors.get(cat, ("#aaa", "#1a1a1a"))
        if not items:
            continue
        cards = ""
        for i in items:
            cards += f"""
            <a class="card" href="{i['link']}" target="_blank" rel="noopener">
              <div class="card-title">{i['title']}</div>
              {'<div class="card-source">' + i['source'] + '</div>' if i['source'] else ''}
            </a>"""

        categories_html += f"""
        <div class="cat-section">
          <div class="cat-header">
            <span class="cat-dot" style="background:{color}"></span>
            <span class="cat-label">{cat}</span>
            <div class="cat-line"></div>
          </div>
          {cards}
        </div>"""

    opinion_escaped = opinion.replace("⚠️", "⚠️")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>브리핑 {date_str}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.min.css">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0a0c12;--bg2:#111724;--border:rgba(255,255,255,0.08);
  --text:#edf2ff;--muted:#8892a4;
}}
body{{
  font-family:'Pretendard',-apple-system,sans-serif;
  background:var(--bg);color:var(--text);
  min-height:100vh;line-height:1.72;
}}
.hero{{
  padding:56px 24px 40px;text-align:center;
  border-bottom:1px solid var(--border);
  background:linear-gradient(160deg,#0b1020 0%,#12122a 50%,#0a0c12 100%);
}}
.hero .emoji{{font-size:36px;display:block;margin-bottom:12px}}
.hero .label{{font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:10px}}
.hero h1{{font-size:32px;font-weight:800;color:#fff;letter-spacing:-0.4px}}
.date-badge{{
  display:inline-block;margin-top:12px;padding:6px 16px;border-radius:999px;
  background:rgba(99,210,255,0.12);border:1px solid rgba(99,210,255,0.22);
  color:#aeeaff;font-size:13px;
}}
.rate-row{{margin-top:14px;display:flex;gap:8px;justify-content:center;flex-wrap:wrap}}
.rate-badge{{
  padding:5px 12px;border-radius:999px;
  background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);
  font-size:13px;color:#d8deeb;
}}
.container{{max-width:860px;margin:0 auto;padding:40px 20px 80px}}
.opinion-box{{
  background:#111724;border:1px solid rgba(255,255,255,0.1);
  border-left:3px solid #c41230;border-radius:16px;
  padding:22px 24px;margin-bottom:36px;
}}
.opinion-box .label{{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#f87;margin-bottom:10px}}
.opinion-box p{{font-size:15px;color:#d8deeb;line-height:1.75}}
.cat-section{{margin-bottom:36px}}
.cat-header{{display:flex;align-items:center;gap:10px;margin-bottom:16px}}
.cat-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}
.cat-label{{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);white-space:nowrap}}
.cat-line{{flex:1;height:1px;background:var(--border)}}
.card{{
  display:block;background:#111724;border:1px solid var(--border);
  border-radius:14px;padding:18px 20px;margin-bottom:10px;
  text-decoration:none;color:inherit;
  transition:border-color 0.15s,background 0.15s;
}}
.card:hover{{background:#161f30;border-color:rgba(99,210,255,0.3)}}
.card-title{{font-size:15px;font-weight:600;color:#e8eef8;line-height:1.5}}
.card-source{{margin-top:6px;font-size:12px;color:var(--muted)}}
.footer{{margin-top:60px;text-align:center;font-size:12px;color:var(--muted);border-top:1px solid var(--border);padding-top:20px}}
</style>
</head>
<body>
<div class="hero">
  <span class="emoji">🌅</span>
  <div class="label">Morning Briefing</div>
  <h1>오늘의 브리핑</h1>
  <div class="date-badge">{date_str} ({weekday}요일)</div>
  <div class="rate-row">{rate_badge}</div>
</div>
<div class="container">
  <div class="opinion-box">
    <div class="label">🦊 claw 의견</div>
    <p>{opinion_escaped}</p>
  </div>
  {categories_html}
</div>
<div class="footer">BOOL Korea · usikclaw · 자동 생성</div>
</body>
</html>"""


# ─── GitHub Pages 푸시 ────────────────────────────────
def push_to_github(html, date_str):
    try:
        if not REPO_DIR.exists():
            subprocess.run(["git", "clone", REPO_URL, str(REPO_DIR)],
                           check=True, capture_output=True)
        else:
            subprocess.run(["git", "-C", str(REPO_DIR), "pull", "--rebase"],
                           check=True, capture_output=True)

        d = REPO_DIR / "briefing"
        d.mkdir(exist_ok=True)
        p = d / f"{date_str}.html"
        p.write_text(html, encoding="utf-8")

        subprocess.run(["git", "-C", str(REPO_DIR), "add", str(p)],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(REPO_DIR), "commit", "-m",
                        f"Morning briefing {date_str}"],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(REPO_DIR), "push", "origin", "main"],
                       check=True, capture_output=True)

        return f"https://coolusik-stack.github.io/usikclaw/briefing/{date_str}.html"
    except subprocess.CalledProcessError as e:
        return f"ERROR_GIT: {(e.stderr or b'').decode()[:200]}"
    except Exception as e:
        return f"ERROR: {e}"


# ─── 노션 저장 ────────────────────────────────────────
def save_notion(summary, date_str):
    try:
        key   = NOTION_KEY.read_text().strip()
        ws    = json.loads(NOTION_WS.read_text())
        db_id = ws["databases"]["📋 브리핑 기록"]
        payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "제목": {"title": [{"text": {"content": f"📰 아침 브리핑 {date_str}"}}]},
                "요약": {"rich_text": [{"text": {"content": summary[:1900]}}]}
            }
        }
        req = urllib.request.Request(
            "https://api.notion.com/v1/pages",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            return json.loads(r.read()).get("url", "")
    except Exception as e:
        return f"ERROR: {e}"


# ─── 메인 ─────────────────────────────────────────────
def main():
    now = datetime.now(KST)
    date_str = now.strftime("%Y-%m-%d")
    weekday  = WEEKDAY_KO[now.weekday()]

    print(f"[{now.strftime('%H:%M')}] 브리핑 시작", file=sys.stderr)

    rates   = get_rates()
    news    = get_all_news()
    opinion = make_opinion(rates, news)

    # HTML 빌드 & 푸시
    html       = build_html(date_str, rates, news, opinion)
    pages_url  = push_to_github(html, date_str)
    notion_url = save_notion(
        f"{date_str} 브리핑\n{opinion}",
        date_str
    )

    # 텔레그램용 요약 메시지
    usd = rates.get("usd_krw")
    jpy = rates.get("jpy_100")

    msg_lines = [
        f"🌅 {date_str} ({weekday}) 아침 브리핑이 발행됐어요!",
        f"👉 {pages_url}",
        "",
    ]
    if usd:
        rate_str = f"💰 환율: USD/KRW {usd:,.1f}원"
        if jpy: rate_str += f" · 100엔 {jpy:,.1f}원"
        msg_lines.append(rate_str)

    # 카테고리별 헤드라인 1개씩
    for cat, items in news.items():
        if items:
            msg_lines.append(f"\n{cat}")
            msg_lines.append(f"· {items[0]['title']}")
            if len(items) > 1:
                msg_lines.append(f"· {items[1]['title']}")

    msg_lines += [
        "",
        f"🦊 {opinion}",
    ]
    if notion_url and not notion_url.startswith("ERROR"):
        msg_lines.append(f"\n📝 노션: {notion_url}")

    print("\n".join(msg_lines))
    print(f"\n[GitHub: {pages_url}]", file=sys.stderr)
    print(f"[Notion: {notion_url}]", file=sys.stderr)


if __name__ == "__main__":
    main()
