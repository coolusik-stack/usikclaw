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
import importlib.util as _ilu

# briefing_template.py 로드 (build_html 대체)
_tpl_path = Path(__file__).parent / "briefing_template.py"
_spec = _ilu.spec_from_file_location("briefing_template", _tpl_path)
_tpl = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_tpl)
build_html = _tpl.build_html

ctx = ssl.create_default_context()
KST = timezone(timedelta(hours=9))
NOTION_KEY = Path.home() / ".config" / "notion" / "api_key"
NOTION_WS  = Path.home() / ".config" / "notion" / "workspace.json"
REPO_DIR   = Path.home() / ".openclaw" / "briefing_repo"
REPO_URL   = "https://github.com/coolusik-stack/usikclaw.git"
VAULT_DIR  = Path.home() / "claw-vault"
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
                pub_clean = ""
                if pub:
                    try:
                        from email.utils import parsedate_to_datetime
                        dt = parsedate_to_datetime(pub).astimezone(KST)
                        pub_clean = dt.strftime("%Y.%m.%d")
                    except:
                        pub_clean = pub[:10] if pub else ""
                items.append({"title": title, "link": link, "desc": desc, "pub": pub_clean, "source": source})
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

# ─── Obsidian Vault 저장 ─────────────────────────────
def save_to_vault(date_str, rates, items_analyzed, big_picture, pages_url):
    """Obsidian vault briefings/ 폴더에 마크다운 저장"""
    try:
        vault_briefings = VAULT_DIR / "01_RAW"
        vault_briefings.mkdir(parents=True, exist_ok=True)
        usd = rates.get("usd_krw")
        jpy = rates.get("jpy_100")
        now = datetime.now(KST)
        weekday = WEEKDAY_KO[now.weekday()]

        lines = [f"# 브리핑 {date_str} ({weekday})", ""]
        lines.append(f"웹에서 보기: {pages_url}\n")
        if usd:
            rate_str = f"USD/KRW {usd:,.1f}원"
            if jpy: rate_str += f" · 100엔 {jpy:,.1f}원"
            lines.append(f"**환율**: {rate_str}\n")

        lines.append("## 오늘 먼저 볼 것")
        lines.append(big_picture + "\n")

        for item in items_analyzed:
            lines.append(f"## [{item['source']}] {item['headline']}")
            lines.append(f"**제목**: [{item['title'][:70]}]({item['link']})")
            if item.get('pub'): lines.append(f"**날짜**: {item['pub']}")
            lines.append(f"\n**핵심 내용**: {item['summary']}")
            lines.append(f"\n**왜 중요한지**: {item['why_matters']}")
            lines.append(f"\n**우석 입장 인사이트**: {item['usuk_insight']}\n")

        lines.append("---")
        lines.append("#briefing #daily")

        out_path = vault_briefings / f"{date_str}.md"
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"  Vault 저장: {out_path}", file=sys.stderr)

        # 00_Index.md 업데이트
        index_path = VAULT_DIR / "00_Index.md"
        if index_path.exists():
            idx = index_path.read_text(encoding="utf-8")
            new_row = f"| [[01_RAW/{date_str}]] | {date_str} 아침 브리핑 |"
            if date_str not in idx:
                idx = idx.replace(
                    "| [[01_RAW/decisions]] |",
                    f"{new_row}\n| [[01_RAW/decisions]] |"
                )
                index_path.write_text(idx, encoding="utf-8")
                print(f"  Index 업데이트 완료", file=sys.stderr)

        return str(out_path)
    except Exception as e:
        print(f"  Vault ERROR: {e}", file=sys.stderr)
        return ""


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
    save_to_vault(date_str, rates, items_analyzed, big_picture, pages_url)

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
