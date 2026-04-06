#!/usr/bin/env python3
"""
morning_briefing_v2.py
매일 아침 9시 실행.
1. 뉴스 검색 (web_search 대신 Google News RSS 직접 파싱)
2. 환율 조회
3. GitHub Pages에 briefing/YYYY-MM-DD.html 저장/푸시
4. 노션 '📋 브리핑 기록' 저장
5. 텔레그램 전송 (GitHub Pages 링크 + 노션 링크 포함)
"""

import json, ssl, subprocess, urllib.request, urllib.parse, sys, os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET

ctx = ssl.create_default_context()
KST = timezone(timedelta(hours=9))
NOTION_KEY = Path.home() / ".config" / "notion" / "api_key"
NOTION_WS  = Path.home() / ".config" / "notion" / "workspace.json"
REPO_DIR   = Path.home() / ".openclaw" / "briefing_repo"
REPO_URL   = "https://github.com/coolusik-stack/usikclaw.git"


# ── 환율 ──────────────────────────────────────────────
def get_rates():
    try:
        req = urllib.request.Request(
            "https://open.er-api.com/v6/latest/USD",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            data = json.loads(r.read())
        rates = data["rates"]
        krw = rates.get("KRW")
        jpy = rates.get("JPY")
        return {
            "usd_krw": round(krw, 1) if krw else None,
            "jpy_100": round(krw / jpy * 100, 1) if (krw and jpy) else None
        }
    except Exception as e:
        return {"error": str(e)}


# ── Google News RSS 파싱 ──────────────────────────────
def fetch_rss(url, max_items=5):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            raw = r.read()
        root = ET.fromstring(raw)
        items = []
        for item in root.findall(".//item")[:max_items]:
            title = item.findtext("title", "").strip()
            link  = item.findtext("link", "").strip()
            pub   = item.findtext("pubDate", "").strip()
            if title and link:
                items.append({"title": title, "link": link, "pub": pub})
        return items
    except Exception as e:
        return []


def get_news():
    sources = [
        ("AI/테크",    "https://news.google.com/rss/search?q=AI+인공지능+Claude+OpenAI+Gemini&hl=ko&gl=KR&ceid=KR:ko"),
        ("경제/환율",  "https://news.google.com/rss/search?q=환율+원달러+코스피+금리&hl=ko&gl=KR&ceid=KR:ko"),
        ("BOOL/니코틴","https://news.google.com/rss/search?q=니코틴파우치+BOOL+더바코&hl=ko&gl=KR&ceid=KR:ko"),
    ]
    result = {}
    for label, url in sources:
        result[label] = fetch_rss(url, max_items=4)
    return result


# ── GitHub Pages 저장/푸시 ────────────────────────────
def push_to_github(html: str, date_str: str) -> str:
    """briefing/YYYY-MM-DD.html 푸시 후 URL 반환"""
    try:
        repo = REPO_DIR
        if not repo.exists():
            subprocess.run(["git", "clone", REPO_URL, str(repo)],
                           check=True, capture_output=True)
        else:
            subprocess.run(["git", "-C", str(repo), "pull", "--rebase"],
                           check=True, capture_output=True)

        briefing_dir = repo / "briefing"
        briefing_dir.mkdir(exist_ok=True)

        html_path = briefing_dir / f"{date_str}.html"
        html_path.write_text(html, encoding="utf-8")

        subprocess.run(["git", "-C", str(repo), "add", str(html_path)],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-m",
                        f"Add morning briefing {date_str}"],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(repo), "push", "origin", "main"],
                       check=True, capture_output=True)

        return f"https://coolusik-stack.github.io/usikclaw/briefing/{date_str}.html"
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.stderr.decode()[:200] if e.stderr else str(e)}"
    except Exception as e:
        return f"ERROR: {e}"


# ── 노션 저장 ─────────────────────────────────────────
def save_to_notion(summary: str, date_str: str, pages_url: str) -> str:
    try:
        key = NOTION_KEY.read_text().strip()
        ws  = json.loads(NOTION_WS.read_text())
        db_id = ws["databases"]["📋 브리핑 기록"]

        payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "제목": {"title": [{"text": {"content": f"📰 아침 브리핑 {date_str}"}}]},
                "요약": {"rich_text": [{"text": {"content": summary[:1900]}}]}
            }
        }
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            "https://api.notion.com/v1/pages",
            data=data,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            resp = json.loads(r.read())
        return resp.get("url", "")
    except Exception as e:
        return f"ERROR: {e}"


# ── HTML 생성 ─────────────────────────────────────────
def build_html(date_str: str, rates: dict, news: dict, claw_opinion: str) -> str:
    weekday = ["월","화","수","목","금","토","일"][datetime.now(KST).weekday()]
    sections = ""
    for label, items in news.items():
        if not items:
            continue
        rows = "".join(
            f'<li><a href="{i["link"]}" target="_blank">{i["title"]}</a></li>'
            for i in items
        )
        sections += f"<h2>{label}</h2><ul>{rows}</ul>"

    rate_str = ""
    if "usd_krw" in rates and rates["usd_krw"]:
        rate_str = f'<p class="rate">USD/KRW <strong>{rates["usd_krw"]:,}원</strong>'
        if rates.get("jpy_100"):
            rate_str += f' &nbsp;·&nbsp; 100엔 <strong>{rates["jpy_100"]:,}원</strong>'
        rate_str += "</p>"

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BOOL 브리핑 {date_str}</title>
<style>
  body{{font-family:'Apple SD Gothic Neo',sans-serif;max-width:720px;margin:40px auto;padding:0 20px;color:#222;line-height:1.7}}
  h1{{font-size:1.6rem;border-bottom:3px solid #111;padding-bottom:8px}}
  h2{{font-size:1.1rem;margin-top:28px;color:#c41230}}
  ul{{padding-left:20px}} li{{margin:6px 0}}
  a{{color:#0052cc;text-decoration:none}} a:hover{{text-decoration:underline}}
  .rate{{background:#f5f5f5;padding:10px 16px;border-radius:6px;font-size:1rem}}
  .opinion{{background:#fff8f0;border-left:4px solid #c41230;padding:12px 16px;margin-top:28px}}
  .footer{{margin-top:40px;font-size:0.8rem;color:#999}}
</style>
</head>
<body>
<h1>📰 아침 브리핑 {date_str} ({weekday})</h1>
{rate_str}
{sections}
<div class="opinion"><strong>🦊 claw 의견</strong><br>{claw_opinion}</div>
<div class="footer">BOOL Korea · usikclaw · 자동 생성</div>
</body>
</html>"""


# ── 메인 ──────────────────────────────────────────────
def main():
    now = datetime.now(KST)
    date_str = now.strftime("%Y-%m-%d")

    print(f"[{now.strftime('%H:%M')}] 브리핑 생성 시작...", file=sys.stderr)

    rates = get_rates()
    news  = get_news()

    # 간단 텍스트 요약 (노션/텔레그램용)
    lines = [f"📰 {date_str} 아침 브리핑\n"]
    usd = rates.get("usd_krw")
    jpy = rates.get("jpy_100")
    if usd:
        lines.append(f"💰 환율: USD/KRW {usd:,}원" + (f" · 100엔 {jpy:,}원" if jpy else ""))

    for label, items in news.items():
        if items:
            lines.append(f"\n{label}")
            for i in items[:3]:
                lines.append(f"· {i['title']}")

    # claw 의견 (간단 고정 + 환율 포함)
    opinion_parts = []
    if usd and usd >= 1550:
        opinion_parts.append(f"환율이 {usd:,}원으로 경계 수준입니다. 수입 비용 구조 재검토가 필요합니다.")
    elif usd and usd <= 1400:
        opinion_parts.append(f"환율이 {usd:,}원으로 안정적입니다.")
    else:
        opinion_parts.append(f"환율 {usd:,}원, 큰 변동 없이 안정적입니다." if usd else "환율 조회 실패.")

    bool_news = news.get("BOOL/니코틴", [])
    if bool_news:
        opinion_parts.append(f"BOOL/니코틴파우치 관련 기사 {len(bool_news)}건 감지됐습니다. 규제 동향 확인 권장.")

    claw_opinion = " ".join(opinion_parts)
    summary = "\n".join(lines)

    # HTML 생성
    html = build_html(date_str, rates, news, claw_opinion)

    # GitHub Pages 푸시
    pages_url = push_to_github(html, date_str)
    print(f"GitHub Pages: {pages_url}", file=sys.stderr)

    # 노션 저장
    notion_url = save_to_notion(summary, date_str, pages_url)
    print(f"Notion: {notion_url}", file=sys.stderr)

    # 최종 출력 (텔레그램용 메시지)
    output = summary
    output += f"\n\n🌐 전체 보기: {pages_url}"
    if notion_url and not notion_url.startswith("ERROR"):
        output += f"\n📝 노션: {notion_url}"

    print(output)


if __name__ == "__main__":
    main()
