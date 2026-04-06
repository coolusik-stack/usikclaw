#!/usr/bin/env python3
import json, urllib.request, urllib.parse, ssl
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

CALENDAR_CONFIG = Path.home() / '.openclaw' / 'graph-calendar-config.json'
KST = ZoneInfo('Asia/Seoul')
ctx = ssl.create_default_context()


def get_token(cfg):
    url = f"https://login.microsoftonline.com/{cfg['tenant_id']}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        'grant_type': 'client_credentials',
        'client_id': cfg['client_id'],
        'client_secret': cfg['client_secret'],
        'scope': 'https://graph.microsoft.com/.default'
    }).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    with urllib.request.urlopen(req, context=ctx) as r:
        return json.loads(r.read())['access_token']


def get_tomorrow_events():
    cfg = json.loads(CALENDAR_CONFIG.read_text())
    token = get_token(cfg)
    now = datetime.now(KST)
    tomorrow = (now + timedelta(days=1)).date()
    start = datetime.combine(tomorrow, datetime.min.time(), tzinfo=KST).astimezone(timezone.utc)
    end = datetime.combine(tomorrow, datetime.max.time(), tzinfo=KST).astimezone(timezone.utc)
    url = (f"https://graph.microsoft.com/v1.0/users/{cfg['user_email']}/calendarView"
           f"?startDateTime={start.strftime('%Y-%m-%dT%H:%M:%SZ')}"
           f"&endDateTime={end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
           f"&$select=subject,start,end,location&$orderby=start/dateTime&$top=50")
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req, context=ctx) as r:
        return json.loads(r.read())['value']


def parse_event(e):
    s = e['start']['dateTime']
    t = e['end']['dateTime']
    start = datetime.fromisoformat(s if '+' in s or s.endswith('Z') else s + '+00:00')
    end = datetime.fromisoformat(t if '+' in t or t.endswith('Z') else t + '+00:00')
    start = start.astimezone(KST)
    end = end.astimezone(KST)
    return {
        'subject': e.get('subject', '(제목 없음)'),
        'start': start,
        'end': end,
        'location': e.get('location', {}).get('displayName', '')
    }


def build_message(events):
    tomorrow = (datetime.now(KST) + timedelta(days=1)).date()
    weekday_map = ['월', '화', '수', '목', '금', '토', '일']
    header = f"내일 일정 브리핑 ({tomorrow.month}/{tomorrow.day} {weekday_map[tomorrow.weekday()]}요일)"
    if not events:
        return header + "\n- 확인된 일정 없음"

    lines = [header]
    for ev in events:
        base = f"- {ev['start'].strftime('%H:%M')}–{ev['end'].strftime('%H:%M')} {ev['subject']}"
        if ev['location']:
            base += f" ({ev['location']})"
        lines.append(base)

    overlaps = []
    for i in range(len(events)-1):
        if events[i+1]['start'] < events[i]['end']:
            overlaps.append((events[i], events[i+1]))
    if overlaps:
        lines.append('')
        lines.append('주의')
        for a, b in overlaps:
            lines.append(f"- 일정 겹침: {a['subject']} / {b['subject']}")

    return '\n'.join(lines)


def main():
    raw = get_tomorrow_events()
    events = sorted([parse_event(e) for e in raw], key=lambda x: x['start'])
    print(build_message(events))


if __name__ == '__main__':
    main()
