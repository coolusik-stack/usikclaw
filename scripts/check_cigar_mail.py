#!/usr/bin/env python3
import imaplib, email, json, re, subprocess, urllib.request
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path.home() / '.openclaw'
CONFIG_PATH = BASE / 'automation-config.json'
STATE_PATH = BASE / 'automation-state.json'

KEYWORDS = [
    'cigar','cigars','시가','시가협회','tobacco','thebacco','foundation cigar','foundationcigarcompany',
    'escobar cigar','el-septimo','el septimo','habanos','cohiba','davidoff','montecristo','partagas'
]


def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text())
    return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def decode_str(value: str) -> str:
    return str(make_header(decode_header(value or '')))


def fetch_body_text(M, mid):
    status, msg_data = M.fetch(mid, '(BODY.PEEK[])')
    raw = b''
    for part in msg_data:
        if isinstance(part, tuple):
            raw += part[1]
    if not raw:
        return None, ''
    msg = email.message_from_bytes(raw)
    text = ''
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get('Content-Disposition') or '')
            if ctype == 'text/plain' and 'attachment' not in disp.lower():
                payload = part.get_payload(decode=True) or b''
                charset = part.get_content_charset() or 'utf-8'
                text = payload.decode(charset, errors='ignore')
                if text.strip():
                    break
    else:
        payload = msg.get_payload(decode=True) or b''
        charset = msg.get_content_charset() or 'utf-8'
        text = payload.decode(charset, errors='ignore')
    return msg, text.strip()


def translate_to_korean(openai_key, content):
    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=json.dumps({
            'model': 'gpt-4o-mini',
            'messages': [
                {'role': 'system', 'content': 'Translate and summarize business email content into concise Korean. Return 3 bullet points max.'},
                {'role': 'user', 'content': content[:12000]}
            ],
            'temperature': 0.2
        }).encode('utf-8'),
        headers={'Authorization': f'Bearer {openai_key}', 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=40) as r:
        data = json.loads(r.read().decode('utf-8'))
    return data['choices'][0]['message']['content'].strip()


def send_telegram(target, text):
    subprocess.run([
        'openclaw', 'message', 'send', '--channel', 'telegram', '--target', str(target), '--message', text
    ], check=True)


def main():
    cfg = load_json(CONFIG_PATH, {})
    state = load_json(STATE_PATH, {'seen_message_ids': [], 'initialized': False})
    seen = set(state.get('seen_message_ids', []))
    M = imaplib.IMAP4_SSL('imap.mail.yahoo.com', 993)
    M.login(cfg['yahoo_email'], cfg['yahoo_app_password'])
    M.select('INBOX', readonly=True)
    status, data = M.search(None, 'SINCE', (datetime.now(timezone.utc)-timedelta(days=7)).strftime('%d-%b-%Y'))
    ids = data[0].split()[-100:]
    new_seen = list(seen)
    matches = []
    if not state.get('initialized'):
        for mid in ids:
            try:
                status, msg_data = M.fetch(mid, '(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])')
                raw = b''
                for part in msg_data:
                    if isinstance(part, tuple):
                        raw += part[1]
                msg = email.message_from_bytes(raw)
                message_id = msg.get('Message-ID') or mid.decode()
                new_seen.append(message_id)
            except Exception:
                continue
        state['initialized'] = True
        state['seen_message_ids'] = new_seen[-2000:]
        save_json(STATE_PATH, state)
        M.logout()
        return
    for mid in ids:
        msg, body = fetch_body_text(M, mid)
        if msg is None:
            continue
        message_id = msg.get('Message-ID') or mid.decode()
        if message_id in seen:
            continue
        subj = decode_str(msg.get('Subject', ''))
        frm = decode_str(msg.get('From', ''))
        hay = (subj + ' ' + frm + ' ' + body[:4000]).lower()
        if any(k.lower() in hay for k in KEYWORDS):
            try:
                dt = parsedate_to_datetime(msg.get('Date', ''))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                when = dt.astimezone(timezone(timedelta(hours=9))).strftime('%m/%d %H:%M')
            except Exception:
                when = msg.get('Date', '')
            content = f"From: {frm}\nSubject: {subj}\nDate: {msg.get('Date', '')}\n\n{body[:6000]}"
            summary_ko = translate_to_korean(cfg['openai_api_key'], content)
            matches.append((message_id, f"시가 관련 메일 도착\n- 보낸 사람: {frm}\n- 제목: {subj}\n- 시각: {when}\n\n한국어 요약\n{summary_ko}"))
        new_seen.append(message_id)
    M.logout()
    for _, text in matches:
        send_telegram(cfg['telegram_target'], text)
    # keep state bounded
    state['seen_message_ids'] = new_seen[-2000:]
    save_json(STATE_PATH, state)


if __name__ == '__main__':
    main()
