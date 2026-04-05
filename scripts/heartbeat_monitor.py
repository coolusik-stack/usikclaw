#!/usr/bin/env python3
"""
heartbeat_monitor.py
heartbeat 때 호출하는 모니터링 스크립트.
- Outlook 캘린더 향후 24h 중요 일정 체크
- 환율 조회 (USD/KRW, JPY/KRW)
출력: JSON {"alerts": [...], "summary": "..."}
"""

import urllib.request, urllib.parse, json, ssl, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

STATE_FILE = Path(__file__).parent.parent / "memory" / "heartbeat-state.json"
CALENDAR_CONFIG = Path.home() / ".openclaw" / "graph-calendar-config.json"

ctx = ssl.create_default_context()

# ── 중요 일정 판단 키워드 ──
IMPORTANT_KEYWORDS = [
    "미팅", "meeting", "대표", "발표", "보고", "클라이언트", "client",
    "인터뷰", "interview", "계약", "전화", "call", "lr", "thebacco",
    "bool", "agency", "rfi", "검토", "심사"
]
SKIP_KEYWORDS = ["취소", "cancel", "moat01"]  # 반복/취소 일정 스킵

def is_important(subject: str) -> bool:
    s = subject.lower()
    if any(k in s for k in SKIP_KEYWORDS):
        return False
    return any(k in s for k in IMPORTANT_KEYWORDS)

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

def get_calendar_alerts(cfg):
    token = get_token(cfg)
    now = datetime.now(timezone.utc)
    end = now + timedelta(hours=24)
    start_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end.strftime("%Y-%m-%dT%H:%M:%SZ")

    url = (f"https://graph.microsoft.com/v1.0/users/{cfg['user_email']}/calendarView"
           f"?startDateTime={start_str}&endDateTime={end_str}"
           f"&$select=subject,start,end,location,importance"
           f"&$orderby=start/dateTime&$top=20")

    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, context=ctx) as r:
        events = json.loads(r.read())["value"]

    alerts = []
    for e in events:
        subj = e.get("subject", "(제목없음)")
        if not is_important(subj):
            continue

        raw_start = e["start"]["dateTime"]
        raw_end = e["end"]["dateTime"]
        # Graph API returns UTC without Z sometimes
        if raw_start.endswith("Z") or "+" in raw_start:
            start_dt = datetime.fromisoformat(raw_start.replace("Z","+00:00"))
        else:
            start_dt = datetime.fromisoformat(raw_start).replace(tzinfo=timezone.utc)
        if raw_end.endswith("Z") or "+" in raw_end:
            end_dt = datetime.fromisoformat(raw_end.replace("Z","+00:00"))
        else:
            end_dt = datetime.fromisoformat(raw_end).replace(tzinfo=timezone.utc)
        kst_start = start_dt + timedelta(hours=9)
        kst_end = end_dt + timedelta(hours=9)

        # 2시간 이내 일정만 알림
        minutes_until = (start_dt - now).total_seconds() / 60
        if minutes_until < 0:
            continue  # 이미 시작된 일정 스킵

        alert = {
            "subject": subj,
            "start_kst": kst_start.strftime("%m/%d %H:%M"),
            "end_kst": kst_end.strftime("%H:%M"),
            "minutes_until": int(minutes_until),
            "urgent": minutes_until <= 120
        }
        alerts.append(alert)

    return alerts

def get_exchange_rates():
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            data = json.loads(r.read())
        rates = data.get("rates", {})
        krw = rates.get("KRW")
        jpy = rates.get("JPY")
        return {
            "usd_krw": round(krw, 1) if krw else None,
            "jpy_krw": round(krw / jpy * 100, 1) if krw and jpy else None  # 100엔 기준
        }
    except Exception as e:
        return {"error": str(e)}

CIGAR_KEYWORDS = ["cigar", "stogie", "tobacconist", "toscano", "cohiba", "montecristo",
                  "padron", "fuente", "davidoff", "leaf", "maduro", "habano",
                  "시가", "파이프", "엽궐련"]

def check_cigar_emails():
    """himalaya로 Yahoo 메일에서 시가 관련 메일 감지 후 한국어 요약 반환"""
    try:
        import subprocess, json as _json
        # 최근 30개 메일 JSON으로 가져오기
        result = subprocess.run(
            ["himalaya", "envelope", "list", "--page-size", "30", "--output", "json"],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode != 0:
            return {"error": result.stderr[:200]}

        envelopes = _json.loads(result.stdout)
        cigar_mails = []
        for env in envelopes:
            subj = (env.get("subject") or "").lower()
            sender = (env.get("from", {}).get("addr") or "").lower()
            if any(kw in subj or kw in sender for kw in CIGAR_KEYWORDS):
                cigar_mails.append({
                    "id": env.get("id"),
                    "subject": env.get("subject"),
                    "from": env.get("from", {}).get("addr"),
                    "date": env.get("date")
                })
        return {"cigar_mails": cigar_mails}
    except Exception as e:
        return {"error": str(e)}

def main():
    results = {"alerts": [], "exchange": {}, "cigar_emails": [], "summary": ""}

    # 캘린더
    try:
        cfg = json.loads(CALENDAR_CONFIG.read_text())
        cal_alerts = get_calendar_alerts(cfg)
        results["alerts"] = cal_alerts
    except Exception as e:
        results["calendar_error"] = str(e)

    # 환율
    results["exchange"] = get_exchange_rates()

    # 시가 메일 감지
    cigar_result = check_cigar_emails()
    results["cigar_emails"] = cigar_result.get("cigar_mails", [])
    if cigar_result.get("error"):
        results["cigar_email_error"] = cigar_result["error"]

    # 상태 업데이트
    try:
        import time
        state = json.loads(STATE_FILE.read_text())
        state["lastChecks"]["calendar"] = int(time.time())
        state["lastChecks"]["exchangeRate"] = int(time.time())
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    except:
        pass

    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
