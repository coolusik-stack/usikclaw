#!/usr/bin/env python3
"""
morning_briefing_v3.py
4/4 브리핑 스타일 재현.
- 소스별 (OpenAI, Anthropic, Lenny's, Sandhill, Chamath, Builder Josh 등) 최신 콘텐츠 수집
- Gemini API로 핵심 내용 / 왜 중요한지 / 우석 입장 인사이트 생성
- 4/4 스타일 다크 HTML 생성 → GitHub Pages 푸시
- 노션 저장
- 텔레그램 메시지 출력 (링크 + claw 의견)
"""

import json, ssl, subprocess, sys, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path

ctx = ssl.create_default_context()
KST = timezone(timedelta(hours=9))
NOTION_KEY = Path.home() / ".config" / "notion" / "api_key"
NOTION_WS  = Path.home() / ".config" / "notion" / "workspace.json"
REPO_DIR   = Path.home() / ".openclaw" / "briefing_repo"
REPO_URL   = "https://github.com/coolusik-stack/usikclaw.git"
GEMINI_KEY_PATH = Path.home() / ".openclaw" / "openclaw.json"
WEEKDAY_KO = ["월","화","수","목","금","토","일"]

# ─── Gemini API key 로드 ──────────────────────────────
def get_gemini_key():
    cfg = json.loads(GEMINI_KEY_PATH.read_text())
    return cfg["models"]["providers"]["google"]["apiKey"]

# ─── Gemini 호출 ──────────────────────────────────────
def gemini(prompt: str, key: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        resp = json.loads(r.read())
    return resp["candidates"][0]["content"]["parts"][0]["text"].strip()

# ─── RSS 파싱 ─────────────────────────────────────────
def fetch_rss(url, max_items=3):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            root = ET.fromstring(r.read())
        items = []
        for item in root.findall(".//item")[:max_items]:
            title   = (item.findtext("title")       or "").strip()
            link    = (item.findtext("link")         or "").strip()
            desc    = (item.findtext("description")  or "").strip()[:400]
            pub     = (item.findtext("pubDate")      or "").strip()
            src_el  = item.find(".//{http://www.google.com/schemas/sitemap/0.84}news")
            source  = ""
            for child in item:
                if "source" in child.tag.lower():
                    source = child.text or ""
            if title and link:
                items.append({"title": title, "link": link, "desc": desc, "pub": pub, "source": source})
        return items
    except Exception as e:
        print(f"RSS ERROR {url[:60]}: {e}", file=sys.stderr)
        return []

# ─── 환율 ─────────────────────────────────────────────
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

# ─── 소스 수집 ────────────────────────────────────────
SOURCES = {
    "OpenAI 뉴스":   "https://news.google.com/rss/search?q=OpenAI+GPT+ChatGPT&hl=ko&gl=KR&ceid=KR:ko",
    "Anthropic 뉴스":"https://news.google.com/rss/search?q=Anthropic+Claude+AI&hl=ko&gl=KR&ceid=KR:ko",
    "AI 테크 트렌드": "https://news.google.com/rss/search?q=AI+agent+LLM+Gemini&hl=ko&gl=KR&ceid=KR:ko",
    "경제 매크로":    "https://news.google.com/rss/search?q=USD+KRW+exchange+rate+Korea+economy&hl=ko&gl=KR&ceid=KR:ko",
    "Lenny's":       "https://www.lennysnewsletter.com/feed",
    "Sandhill":      "https://www.sandhill.io/feed",
    "Chamath":       "https://chamath.substack.com/feed",
}

def collect_items():
    """각 소스에서 최신 1~2개 아이템 수집"""
    collected = {}
    for name, url in SOURCES.items():
        items = fetch_rss(url, max_items=2)
        if items:
            collected[name] = items[0]  # 최신 1개
            print(f"  [{name}] {items[0]['title'][:60]}", file=sys.stderr)
        else:
            print(f"  [{name}] 수집 실패", file=sys.stderr)
    return collected

# ─── Gemini로 각 아이템 분석 ──────────────────────────
def analyze_item(name: str, item: dict, key: str) -> dict:
    """각 소스 아이템에 대해 한국어 분석 생성"""
    title = item['title']
    desc  = item.get('desc', '')
    link  = item['link']

    prompt = f"""당신은 AI/테크/경제 전문 에디터입니다. 우석(한국 스타트업 창업자, BOOL 니코틴파우치 비즈니스 운영)의 개인 AI 브리핑을 작성합니다.

다음 콘텐츠를 분석해서 JSON으로 응답하세요. JSON 외 다른 텍스트는 절대 출력하지 마세요.

소스: {name}
제목: {title}
내용 요약: {desc[:300] if desc else '(없음)'}
링크: {link}

다음 JSON 형식으로만 응답:
{{
  "headline": "15자 이내 한국어 핵심 한 줄",
  "summary": "핵심 내용 2-3문장. 구체적이고 사실 중심으로.",
  "why_matters": "왜 중요한지 2문장. AI/테크/경제 맥락에서.",
  "usuk_insight": "우석 입장 인사이트 2문장. 우석의 BOOL 비즈니스, OpenClaw 자동화, 개인 투자/경제 관심사에 맞춰 구체적으로."
}}"""

    try:
        raw = gemini(prompt, key)
        # JSON 파싱
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw.strip())
        result["title"] = title
        result["link"]  = link
        result["source"] = name
        return result
    except Exception as e:
        print(f"  Gemini ERROR [{name}]: {e}", file=sys.stderr)
        return {
            "source": name, "title": title, "link": link,
            "headline": title[:40],
            "summary": desc[:200] if desc else title,
            "why_matters": "내용 분석에 실패했습니다.",
            "usuk_insight": "직접 확인 권장합니다."
        }

# ─── Big Picture 생성 ─────────────────────────────────
def make_big_picture(items_analyzed: list, rates: dict, key: str) -> str:
    headlines = "\n".join(f"- [{i['source']}] {i['headline']}" for i in items_analyzed)
    usd = rates.get("usd_krw", "N/A")

    prompt = f"""우석의 아침 브리핑 Big Picture 섹션을 작성합니다. 
오늘 수집된 주요 소식들:
{headlines}
환율: USD/KRW {usd}원

오늘 전체 흐름에서 claw(AI 어시스턴트)의 관점으로 3-4문장 Big Picture를 한국어로 써주세요.
- 오늘 전체 소식에서 공통으로 읽히는 큰 흐름/패턴
- 우석에게 특히 의미 있는 부분
- 지금 우선순위 있게 볼 것
딱딱하지 않게, claw의 목소리로. JSON이나 마크다운 없이 순수 텍스트로만."""

    try:
        return gemini(prompt, key)
    except Exception as e:
        return f"오늘 브리핑 분석 중 오류가 발생했습니다: {e}"

# ─── HTML 빌드 ────────────────────────────────────────
CAT_COLORS = {
    "OpenAI":       ("#63d2ff", "#0a1a2a"),
    "Anthropic":    ("#b388ff", "#1a0a2a"),
    "Builder Josh": ("#58d68d", "#0a2a1a"),
    "Species":      ("#ffbf69", "#2a1a0a"),
    "Lenny's":      ("#ff8fab", "#2a0a10"),
    "Sandhill":     ("#a8dadc", "#0a1a1a"),
    "Chamath":      ("#ffd166", "#2a1e00"),
}

def build_html(date_str, rates, items_analyzed, big_picture):
    now = datetime.now(KST)
    weekday = WEEKDAY_KO[now.weekday()]
    usd = rates.get("usd_krw")
    jpy = rates.get("jpy_100")

    rate_badges = ""
    if usd:
        rate_badges += f'<span class="rate-badge">USD/KRW {usd:,.1f}원</span>'
    if jpy:
        rate_badges += f'<span class="rate-badge">100엔 {jpy:,.1f}원</span>'

    cards_html = ""
    for item in items_analyzed:
        color, bg = CAT_COLORS.get(item["source"], ("#aaa", "#1a1a1a"))
        cards_html += f"""
    <div class="card">
      <div class="tag" style="background:{bg};color:{color};border:1px solid {color}44">{item['source']}</div>
      <h3><a href="{item['link']}" target="_blank" rel="noopener">{item['headline']}</a></h3>
      <p class="card-source">{item['title'][:80]}</p>
      <div class="card-section">
        <div class="card-section-label">핵심 내용</div>
        <p>{item['summary']}</p>
      </div>
      <div class="card-section">
        <div class="card-section-label">왜 중요한지</div>
        <p>{item['why_matters']}</p>
      </div>
      <div class="card-section insight">
        <div class="card-section-label">🦊 우석 입장 인사이트</div>
        <p>{item['usuk_insight']}</p>
      </div>
    </div>"""

    # Big Picture에서 첫 두 문장 추출 (intro용)
    bp_sentences = big_picture.split(". ")
    intro = ". ".join(bp_sentences[:2]) + ("." if len(bp_sentences) > 1 else "")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Morning Briefing — {date_str}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.min.css">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0a0c12;--bg2:#111724;--bg3:#171e30;
  --border:rgba(255,255,255,0.08);
  --text:#edf2ff;--muted:#8892a4;
}}
body{{font-family:'Pretendard',-apple-system,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;line-height:1.72}}
a{{color:inherit;text-decoration:none}}
.hero{{
  padding:64px 24px 44px;text-align:center;border-bottom:1px solid var(--border);
  background:linear-gradient(160deg,#0b1020 0%,#12122a 52%,#0a0c12 100%);
}}
.hero .emoji{{font-size:36px;display:block;margin-bottom:12px}}
.hero .label{{font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:14px}}
.hero h1{{font-size:34px;font-weight:800;color:#fff;letter-spacing:-0.4px}}
.date-badge{{display:inline-block;margin-top:14px;padding:7px 16px;border-radius:999px;background:rgba(99,210,255,0.12);border:1px solid rgba(99,210,255,0.22);color:#aeeaff;font-size:13px}}
.hero .sub{{margin-top:12px;font-size:15px;color:var(--muted)}}
.rate-row{{margin-top:12px;display:flex;gap:8px;justify-content:center;flex-wrap:wrap}}
.rate-badge{{padding:5px 12px;border-radius:999px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);font-size:13px;color:#d8deeb}}
.container{{max-width:900px;margin:0 auto;padding:42px 24px 96px}}
.summary{{background:var(--bg2);border:1px solid var(--border);border-radius:22px;padding:26px;margin-bottom:34px}}
.summary h2{{font-size:12px;color:#b8cbff;text-transform:uppercase;letter-spacing:2px;margin-bottom:12px}}
.summary p{{color:#d8deeb;font-size:15px;line-height:1.8}}
.card{{background:var(--bg2);border:1px solid var(--border);border-radius:18px;padding:24px;margin-bottom:16px}}
.tag{{display:inline-block;padding:5px 10px;border-radius:999px;font-size:10px;font-weight:700;letter-spacing:1.3px;text-transform:uppercase;margin-bottom:12px}}
.card h3{{font-size:20px;line-height:1.4;color:#fff;letter-spacing:-0.2px;margin-bottom:6px}}
.card h3 a:hover{{color:#63d2ff}}
.card-source{{font-size:12px;color:var(--muted);margin-bottom:14px}}
.card-section{{margin-top:12px;padding-top:12px;border-top:1px solid var(--border)}}
.card-section-label{{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:6px}}
.card-section p{{font-size:14px;color:#c8d4e8;line-height:1.72}}
.card-section.insight{{background:rgba(99,210,255,0.04);border:1px solid rgba(99,210,255,0.1);border-radius:10px;padding:12px 14px;margin-top:12px}}
.card-section.insight .card-section-label{{color:#63d2ff}}
.card-section.insight p{{color:#d8eeff}}
.big-picture{{background:var(--bg3);border:1px solid rgba(255,255,255,0.12);border-radius:22px;padding:28px;margin-top:40px}}
.big-picture .bp-label{{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#b8cbff;margin-bottom:14px}}
.big-picture p{{font-size:15px;color:#d8deeb;line-height:1.8}}
.footer{{margin-top:60px;text-align:center;font-size:12px;color:var(--muted);border-top:1px solid var(--border);padding-top:24px}}
</style>
</head>
<body>
<div class="hero">
  <span class="emoji">🌅</span>
  <div class="label">Morning Briefing</div>
  <h1>오늘의 브리핑</h1>
  <div class="date-badge">{date_str} ({weekday}요일)</div>
  <div class="hero sub">{intro}</div>
  <div class="rate-row">{rate_badges}</div>
</div>
<div class="container">
  <div class="summary">
    <h2>오늘 먼저 볼 것</h2>
    <p>{big_picture}</p>
  </div>
  {cards_html}
  <div class="big-picture">
    <div class="bp-label">🦊 Big Picture — claw 의견</div>
    <p>{big_picture}</p>
  </div>
</div>
<div class="footer">BOOL Korea · usikclaw · {date_str} 자동 생성</div>
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
        subprocess.run(["git", "-C", str(REPO_DIR), "add", str(p)],   check=True, capture_output=True)
        subprocess.run(["git", "-C", str(REPO_DIR), "commit", "-m", f"Morning briefing {date_str}"],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(REPO_DIR), "push", "origin", "main"],
                       check=True, capture_output=True)
        return f"https://coolusik-stack.github.io/usikclaw/briefing/{date_str}.html"
    except subprocess.CalledProcessError as e:
        err = (e.stderr or b"").decode()[:200]
        # already up to date = still ok
        if "nothing to commit" in err or "already up to date" in err.lower():
            return f"https://coolusik-stack.github.io/usikclaw/briefing/{date_str}.html"
        return f"ERROR_GIT: {err}"
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
    now      = datetime.now(KST)
    date_str = now.strftime("%Y-%m-%d")
    weekday  = WEEKDAY_KO[now.weekday()]

    print(f"[{now.strftime('%H:%M')}] 브리핑 시작 ({date_str})", file=sys.stderr)

    gemini_key = get_gemini_key()
    rates      = get_rates()

    print("  소스 수집 중...", file=sys.stderr)
    raw_items = collect_items()

    print("  Gemini 분석 중...", file=sys.stderr)
    items_analyzed = []
    for name, item in raw_items.items():
        print(f"    [{name}] 분석 중...", file=sys.stderr)
        analyzed = analyze_item(name, item, gemini_key)
        items_analyzed.append(analyzed)

    print("  Big Picture 생성 중...", file=sys.stderr)
    big_picture = make_big_picture(items_analyzed, rates, gemini_key)

    print("  HTML 빌드 & 푸시 중...", file=sys.stderr)
    html       = build_html(date_str, rates, items_analyzed, big_picture)
    pages_url  = push_to_github(html, date_str)
    notion_url = save_notion(big_picture, date_str)

    print(f"  GitHub: {pages_url}", file=sys.stderr)
    print(f"  Notion: {notion_url}", file=sys.stderr)

    # 텔레그램 메시지
    usd = rates.get("usd_krw")
    jpy = rates.get("jpy_100")
    rate_str = ""
    if usd:
        rate_str = f"💰 USD/KRW {usd:,.1f}원"
        if jpy: rate_str += f" · 100엔 {jpy:,.1f}원"

    top_items = "\n".join(f"· [{i['source']}] {i['headline']}" for i in items_analyzed[:5])

    msg = f"""🌅 {date_str} ({weekday}) 아침 브리핑이 발행됐어요!
👉 {pages_url}

{rate_str}

{top_items}

🦊 {big_picture[:280]}"""

    if notion_url and not notion_url.startswith("ERROR"):
        msg += f"\n\n📝 노션: {notion_url}"

    print(msg)

if __name__ == "__main__":
    main()
