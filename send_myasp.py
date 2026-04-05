"""
MyASP メルマガ自動配信スクリプト
Notion の「MyASP配信キュー」DBから配信待ちメールを取得し、
MyASPの入稿先アドレスへ送信する。
"""

import os
import smtplib
import json
import urllib.request
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta

# 環境変数
NOTION_TOKEN     = os.environ['NOTION_TOKEN']
NOTION_DB_ID     = os.environ['NOTION_MYASP_DB_ID']
MYASP_ADDRESS    = os.environ['MYASP_ADDRESS']
GMAIL_USER       = os.environ['GMAIL_USER']
GMAIL_APP_PASSWORD = os.environ['GMAIL_APP_PASSWORD']

JST = timezone(timedelta(hours=9))
today = datetime.now(JST).strftime('%Y-%m-%d')


def notion_request(method, path, data=None):
    url = f'https://api.notion.com/v1{path}'
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28',
    }
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode('utf-8'))


def get_pending_emails():
    """配信予定日=今日 かつ ステータス=待機中 のページを取得"""
    data = {
        'filter': {
            'and': [
                {'property': 'ステータス', 'select': {'equals': '待機中'}},
                {'property': '配信予定日', 'date': {'equals': today}},
            ]
        }
    }
    result = notion_request('POST', f'/databases/{NOTION_DB_ID}/query', data)
    return result.get('results', [])


def get_subject(page):
    """ページタイトル（件名）を取得"""
    titles = page['properties']['件名']['title']
    return ''.join(t['plain_text'] for t in titles)


def get_body(page_id):
    """ページのブロックをプレーンテキストに変換して取得"""
    result = notion_request('GET', f'/blocks/{page_id}/children')
    lines = []
    for block in result.get('results', []):
        btype = block.get('type')
        if btype in ('paragraph', 'heading_1', 'heading_2', 'heading_3'):
            texts = block[btype]['rich_text']
            line = ''.join(t['plain_text'] for t in texts)
            line = line.replace('\n', '<br>\n')
            lines.append(line)
        elif btype == 'bulleted_list_item':
            texts = block['bulleted_list_item']['rich_text']
            line = '・' + ''.join(t['plain_text'] for t in texts)
            line = line.replace('\n', '<br>\n')
            lines.append(line)
    return '<br>\n'.join(lines)


def send_email(subject, body):
    """Gmail SMTP 経由で MyASP 入稿先アドレスへ送信"""
    msg = MIMEText(body, 'html', 'utf-8')
    msg['Subject'] = subject
    msg['From']    = GMAIL_USER
    msg['To']      = MYASP_ADDRESS
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)
    print(f'✅ 送信完了: {subject}')


def update_status(page_id, status):
    """Notion のステータスを更新"""
    notion_request('PATCH', f'/pages/{page_id}', {
        'properties': {
            'ステータス': {'select': {'name': status}}
        }
    })


# メイン処理
pages = get_pending_emails()
print(f'配信待ち: {len(pages)} 件 (対象日: {today})')

for page in pages:
    page_id = page['id']
    subject = get_subject(page)
    print(f'処理中: {subject}')
    try:
        body = get_body(page_id)
        send_email(subject, body)
        update_status(page_id, '送信済み')
    except Exception as e:
        print(f'❌ エラー: {e}')
        update_status(page_id, 'エラー')
