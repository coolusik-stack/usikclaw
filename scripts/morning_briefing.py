#!/usr/bin/env python3
"""
morning_briefing.py
매일 아침 9시 실행. 브리핑 생성 후 노션 저장 + 텔레그램 전송.
"""

import urllib.request, urllib.parse, json, ssl, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

ctx = ssl.create_default_context()
CALENDAR_CONFIG = Path.home() / ".openclaw" / "graph-calendar-config.json"
NOTION_KEY_PATH = Path.home() / ".config" / "notion" / "api_key"
NOTION_WS_PATH = Path.home() / ".config" / "notion" / "workspace.json"

KST = timezone(timedelta(hours=9))

def get_token(cfg):
    url = f"https://login.microsoftonline.com/{cfg['tenant_id']}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": cfg["client_id"],
        "client_secret": cfg["client_secret"],
        "scope": "https://graph.microsoft.com/.default"
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, context=ctx) as r:
        return json.loads(r.read())["access_token"]

def get_today_events():
    try:
        cfg = json.loads(CALENDAR_CONFIG.read_text())
        token = get_token(cfg)
        now = datetime.now(KST)
        start = now.replace(hour=0, minute=0, second=0).astimezone(timezone.utc)
        end = now.replace(hour=23, minute=59, second=59).astimezone(timezone.utc)
        url = (f"https://graph.microsoft.com/v1.0/users/{cfg['user_email']}/calendarView"
               f"?startDateTime={start.strftime('%Y-%m-%dT%H:%M:%SZ')}"
               f"&endDateTime={end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
               f"&$select=subject,start,end,location&$orderby=start/dateTime&$top=20")
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, context=ctx) as r:
            events = json.loads(r.read())["value"]
        result = []
        for e in events:
            subj = e.get("subject", "")
            s = datetime.fromisoformat(e["start"]["dateTime"].replace("Z","+00:00"))
            kst_s = (s + timedelta(hours=9)).strftime("%H:%M")
            result.append(f"• {kst_s} {subj}")
        return result
    except Exception as ex:
        return [f"(캘린더 오류: {ex})"]

def get_exchange_rates():
    try:
        req = urllib.request.Request(
            "https://open.er-api.com/v6/latest/USD",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            data = json.loads(r.read())
        rates = data.get("rates", {})
        krw = rates.get("KRW", 0)
        jpy = rates.get("JPY", 1)
        return f"USD/KRW {krw:,.1f}원  |  100엔/{krw/jpy*100:,.1f}원"
    except:
        return "환율 조회 실패"

def get_cigar_emails():
    try:
        result = subprocess.run(
            ["himalaya", "envelope", "list", "--page-size", "20", "--output", "json"],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode != 0:
            return []
        envelopes = json.loads(result.stdout)
        keywords = ["cigar", "stogie", "tobacconist", "toscano", "cohiba",
                    "montecristo", "padron", "fuente", "davidoff", "maduro", "habano"]
        found = []
        for env in envelopes:
            subj = (env.get("subject") or "").lower()
            sender = str(env.get("from") or "").lower()
            if any(k in subj or k in sender for k in keywords):
                found.append(f"• [{env.get('from','')}] {env.get('subject','')}")
        return found
    except:
        return []

def save_to_notion(briefing_text: str, today_str: str):
    try:
        key = NOTION_KEY_PATH.read_text().strip()
        ws = json.loads(NOTION_WS_PATH.read_text())
        db_id = ws["databases"].get("📋 브리핑 기록")
        if not db_id:
            return None

        payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "제목": {"title": [{"text": {"content": f"📰 아침 브리핑 {today_str}"}}]},
                "날짜": {"date": {"start": today_str}},
                "카테고리": {"select": {"name": "일일 브리핑"}},
                "요약": {"rich_text": [{"text": {"content": briefing_text[:1800]}}]}
            }
        }
        req = urllib.request.Request(
            "https://api.notion.com/v1/pages",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {key}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, context=ctx) as r:
            result = json.loads(r.read())
            page_id = result.get("id", "").replace("-", "")
            return f"https://notion.so/{page_id}"
    except Exception as ex:
        return None

def main():
    now_kst = datetime.now(KST)
    today_str = now_kst.strftime("%Y-%m-%d")
    today_display = now_kst.strftime("%Y년 %m월 %d일")
    weekday = ["월", "화", "수", "목", "금", "토", "일"][now_kst.weekday()]

    # 오늘 일정
    events = get_today_events()
    events_text = "\n".join(events) if events else "• 오늘 일정 없음"

    # 환율
    fx = get_exchange_rates()

    # 시가 메일
    cigar = get_cigar_emails()
    cigar_text = "\n".join(cigar) if cigar else None

    # 브리핑 텍스트 구성
    lines = [
        f"🌅 {today_display} ({weekday}) 아침 브리핑",
        "",
        "📅 오늘 일정",
        events_text,
        "",
        f"💱 환율  {fx}",
    ]
    if cigar_text:
        lines += ["", "🚬 시가 관련 메일", cigar_text]

    briefing = "\n".join(lines)

    # 노션 저장
    notion_url = save_to_notion(briefing, today_str)

    # 출력 (cron이 텔레그램으로 전달)
    output = briefing
    if notion_url:
        output += f"\n\n📝 노션 저장: {notion_url}"

    print(output)

if __name__ == "__main__":
    main()
