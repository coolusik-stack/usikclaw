#!/usr/bin/env python3
import json, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timedelta, timezone

CFG = json.loads((Path.home()/'.openclaw'/'graph-calendar-config.json').read_text())

def get_token():
    url = f"https://login.microsoftonline.com/{CFG['tenant_id']}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        'client_id': CFG['client_id'],
        'client_secret': CFG['client_secret'],
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials'
    }).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())['access_token']

def graph_get(token, path):
    req = urllib.request.Request(
        'https://graph.microsoft.com/v1.0' + path,
        headers={'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

if __name__ == '__main__':
    token = get_token()
    start = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    end = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat().replace('+00:00','Z')
    path = f"/users/{urllib.parse.quote(CFG['user_email'])}/calendar/calendarView?startDateTime={urllib.parse.quote(start)}&endDateTime={urllib.parse.quote(end)}&$top=10"
    data = graph_get(token, path)
    for ev in data.get('value', []):
        print(ev.get('subject','(no subject)'), '|', ev.get('start',{}).get('dateTime'), '|', ev.get('id'))
