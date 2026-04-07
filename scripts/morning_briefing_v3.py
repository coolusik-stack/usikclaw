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
def fetch_rss(url, max_items=6):
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
            source  = ""
            pub_dt  = None
            for child in item:
                if "source" in child.tag.lower():
                    source = child.text or ""
            if pub:
                try:
                    from email.utils import parsedate_to_datetime
                    pub_dt = parsedate_to_datetime(pub).astimezone(KST)
                except:
                    pub_dt = None
            if title and link:
                pub_clean = pub_dt.strftime("%Y.%m.%d") if pub_dt else (pub[:10] if pub else "")
                items.append({
                    "title": title,
                    "link": link,
                    "desc": desc,
                    "pub": pub_clean,
                    "pub_dt": pub_dt.isoformat() if pub_dt else "",
                    "source": source,
                })
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

def collect_items(target_date=None):
    """전날(KST) 올라온 아이템만 소스별 1개 수집"""
    if target_date is None:
        target_date = (datetime.now(KST) - timedelta(days=1)).date()
    collected = {}
    for name, url in SOURCES.items():
        items = fetch_rss(url, max_items=6)
        matched = []
        for item in items:
            if item.get("pub_dt"):
                try:
                    item_date = datetime.fromisoformat(item["pub_dt"]).date()
                    if item_date == target_date:
                        matched.append(item)
                except Exception:
                    pass
        if matched:
            collected[name] = matched[0]
            print(f"  [{name}] 전날 기사 채택: {matched[0]['title'][:60]}", file=sys.stderr)
        else:
            print(f"  [{name}] 전날 기사 없음", file=sys.stderr)
    return collected

# ─── Gemini로 각 아이템 분석 ──────────────────────────
def analyze_item(name: str, item: dict, key: str) -> dict:
    """각 소스 아이템에 대해 한국어 분석 생성"""
    title = item['title']
    desc  = item.get('desc', '')
    link  = item['link']

    prompt = f"""당신은 우석을 위한 한국어 비즈니스 브리핑 에디터다. 목표는 '읽자마자 중요한 변화가 무엇인지 바로 보이는' 짧고 날카로운 요약이다.

다음 콘텐츠를 분석해서 JSON으로만 응답하라. JSON 외 텍스트 금지.

소스: {name}
제목: {title}
발행일: {item.get('pub', '(미상)')}
내용 요약: {desc[:300] if desc else '(없음)'}
링크: {link}

핵심 규칙:
- 이 브리핑은 전날 새로 올라온 소식만 다룬다.
- 오래된 발표/기존 제품 재소개 기사라면 '이번 기사에서 새로 추가된 업데이트'만 잡아라.
- 과장 금지. 모호한 표현 금지. 확인 불가능한 추정 금지.
- '혁신', '게임체인저', '무섭다', '엄청나다' 같은 과한 말 금지.
- 기사 제목을 한국어로 단순 번역하지 말고, 실제 변화 포인트를 짚어라.
- 우석 입장 인사이트는 BOOL 비즈니스, OpenClaw 자동화, 비용/운영 관점 중 하나에 연결해 실무적으로 써라.

문체 규칙:
- 자연스러운 한국어.
- 짧고 단정하게.
- 마케팅 문구처럼 쓰지 말 것.

다음 JSON 형식으로만 응답:
{{
  "headline": "12~18자 한국어 한 줄 제목. 이번 업데이트의 본질이 드러나게.",
  "summary": "핵심 내용 2문장. 이번에 새로 확인된 변화가 무엇인지 중심으로.",
  "why_matters": "왜 중요한지 1~2문장. 업계/시장/운영 관점에서.",
  "usuk_insight": "우석 입장 인사이트 1~2문장. 바로 연결되는 실무 판단이나 시사점."
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

    prompt = f"""우석의 아침 브리핑 '오늘 먼저 볼 것' 문단을 쓴다.

오늘 수집된 주요 소식:
{headlines}
환율: USD/KRW {usd}원

작성 규칙:
- 3문장 이내.
- 오늘 기사들에서 공통으로 보이는 변화 1개만 잡아라.
- 우석에게 왜 중요한지 1문장으로 연결.
- 마지막 1문장은 오늘의 실무적 우선순위 제안.
- 뜬구름 잡는 미래예측 금지. 과장 금지.
- 문체는 차분하고 선명하게. claw의 의견이 느껴지되 과하지 않게.
- '좋은 아침', '무섭다', '엄청나다', '핵심 자산' 같은 상투적 표현 금지.

JSON/마크다운 없이 순수 텍스트만 출력."""

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
