# MyASP メルマガ自動配信

毎朝5:00 (JST) に Notion の「MyASP配信キュー」DBをチェックし、
配信待ちのメールをMyASP入稿先アドレスへ自動送信するGitHub Actionsです。

## 必要なGitHub Secrets（5つ）

GitHubリポジトリ → Settings → Secrets and variables → Actions → New repository secret

| Secret名 | 値 |
|---|---|
| `NOTION_TOKEN` | Notion Integration Token（要取得）|
| `NOTION_MYASP_DB_ID` | 335a9baf-dd42-8116-a589-ea075cee8dae |
| `MYASP_ADDRESS` | MyASPの入稿先アドレス（要確認）|
| `GMAIL_USER` | takana1026@gmail.com |
| `GMAIL_APP_PASSWORD` | GmailのアプリパスワードURL（要取得）|

## Gmail アプリパスワードの取得手順

1. https://myaccount.google.com/security を開く
2. 「2段階認証プロセス」が有効になっているか確認（なければ有効化）
3. https://myaccount.google.com/apppasswords を開く
4. アプリ名に「MyASP送信」と入力 → 「作成」
5. 表示された16桁のパスワードをコピー → GMAIL_APP_PASSWORD に設定

## Notion DB

「MyASP配信キュー」DB（メルマガページ内）に以下の形式でデータを追加：
- 件名：メールの件名
- ステータス：待機中
- 配信予定日：送信したい日付（例：2026-04-02）
- ページ本文：メール本文

Claudeがブログ公開後に自動でここにデータを追加します。
