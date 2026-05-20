# Flask Gym プラットフォーム ガイド（日本語）

## 1. 概要

本プロジェクトは Flask で実装されたジム管理アプリです。主なロールは3つです。

- Customer: 会員登録、プロフィール管理、コース閲覧/参加
- Coach: プロフィール管理、コース公開
- Manager: ユーザー/コース管理

公開用に以下の改善を実施しました。

- 機密情報のハードコードを削除
- 環境変数ベースの設定へ移行
- 初期起動を SQLite デフォルトに変更

## 2. 構成

既存機能の互換性を維持するため、現状はモノリシック構成です。

- app/__init__.py: アプリ初期化
- app/model.py: ORM モデル
- app/routes.py: ルーティングと業務ロジック
- app/forms.py: フォーム
- app/templates: テンプレート
- app/static: 静的ファイル

## 3. 設定

config/settings.py の Config クラスで設定を一元管理します。

主要な環境変数:

- SECRET_KEY
- DATABASE_URL
- MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER

## 4. ローカル実行（Windows）

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item configs/env.example .env
python scripts/db_create.py
python run.py
```

起動後: http://127.0.0.1:5000

## 5. セキュリティ対応

- SECRET_KEY/DB/Mail 認証情報のハードコードを除去
- パスワードリセット送信元を MAIL_DEFAULT_SENDER に変更
- テスト内メールアドレスを example.com へ置換

## 6. 今後の改善候補

- Application Factory パターンへの移行
- Blueprint 単位への分割
- pytest fixture による独立テスト
- CI（lint/test/security）追加
