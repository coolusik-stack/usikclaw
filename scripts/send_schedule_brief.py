#!/usr/bin/env python3
import json, subprocess, urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

CONFIG_PATH = Path.home() / '.openclaw' / 'automation-config.json'


def load_config():
    return json.loads(CONFIG_PATH.read_text())


def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=20) as r:
        return r.read().decode('utf-8', errors='ignore')


def unfold_ics(text: str):
    out = []
    for line in text.splitlines():
        if line.startswith((' ', '\t')) and out:
            out[-1] += line[1:]
        else:
            out.append(line)
    return out


def parse_dt(val: str, tz_name='Asia/Seoul'):
    val = val.strip()
    if val.endswith('Z'):
        dt = datetime.strptime(val, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
        return dt.astimezone(ZoneInfo(tz_name))
    if 'T' in val:
        return datetime.strptime(val[:15], '%Y%m%dT%H%M%S').replace(tzinfo=ZoneInfo(tz_name))
    return datetime.strptime(val[:8], '%Y%m%d').replace(tzinfo=ZoneInfo(tz_name))


def parse_events(ics_text: str, start_date, end_date, tz_name='Asia/Seoul'):
    lines = unfold_ics(ics_text)
    events = []
    cur = None
    for line in lines:
        if line == 'BEGIN:VEVENT':
            cur = {}
        elif line == 'END:VEVENT':
            if cur:
                events.append(cur)
            cur = None
        elif cur is not None and ':' in line:
            k, v = line.split(':', 1)
            cur[k] = v
    parsed = []
    for ev in events:
        if any(k.startswith('RECURRENCE-ID') for k in ev):
            pass
        ds_key = next((k for k in ev if k.startswith('DTSTART')), None)
        de_key = next((k for k in ev if k.startswith('DTEND')), None)
        if not ds_key or not de_key:
            continue
        try:
            ds = parse_dt(ev[ds_key], tz_name)
            de = parse_dt(ev[de_key], tz_name)
        except Exception:
            continue
        d = ds.date()
        if not (start_date <= d < end_date):
            continue
        summary = ev.get('SUMMARY', '(제목 없음)').replace('\\n', ' ').strip()
        location = ev.get('LOCATION', '').replace('\\n', ' ').strip()
        parsed.append({
            'start': ds,
            'end': de,
            'summary': summary,
            'location': location,
            'busy': ev.get('X-MICROSOFT-CDO-BUSYSTATUS', ''),
        })
    # dedupe by (start,end,summary)
    uniq = {}
    for ev in parsed:
        key = (ev['start'].isoformat(), ev['end'].isoformat(), ev['summary'])
        uniq[key] = ev
    return sorted(uniq.values(), key=lambda x: x['start'])


def fmt_event(ev):
    return f"- {ev['start'].strftime('%H:%M')}–{ev['end'].strftime('%H:%M')} {ev['summary']}" + (f" ({ev['location']})" if ev['location'] else '')


def build_message(events, target_date):
    weekday_map = ['월', '화', '수', '목', '금', '토', '일']
    header = f"내일 일정 브리핑 ({target_date.month}/{target_date.day} {weekday_map[target_date.weekday()]}요일)"
    if not events:
        return header + "\n- 확인된 일정 없음"
    lines = [header]
    for ev in events:
        lines.append(fmt_event(ev))
    # overlaps
    overlaps = []
    for i in range(len(events)-1):
        if events[i+1]['start'] < events[i]['end']:
            overlaps.append((events[i], events[i+1]))
    if overlaps:
        lines.append('')
        lines.append('주의')
        for a, b in overlaps:
            lines.append(f"- 일정 겹침: {a['summary']} / {b['summary']}")
    return '\n'.join(lines)


def send_telegram(target, text):
    subprocess.run([
        'openclaw', 'message', 'send',
        '--channel', 'telegram',
        '--target', str(target),
        '--message', text
    ], check=True)


def main():
    cfg = load_config()
    tz = ZoneInfo(cfg.get('timezone', 'Asia/Seoul'))
    now = datetime.now(tz)
    tomorrow = (now + timedelta(days=1)).date()
    events = []
    for url in cfg['calendar_ics_urls']:
        try:
            events.extend(parse_events(fetch_text(url), tomorrow, tomorrow + timedelta(days=1), cfg.get('timezone', 'Asia/Seoul')))
        except Exception:
            continue
    # dedupe again across calendars
    uniq = {}
    for ev in events:
        key = (ev['start'].isoformat(), ev['end'].isoformat(), ev['summary'])
        uniq[key] = ev
    message = build_message(sorted(uniq.values(), key=lambda x: x['start']), tomorrow)
    send_telegram(cfg['telegram_target'], message)


if __name__ == '__main__':
    main()
