# 患者情報共有システム - 開発者向け詳細

医療従事者と患者の間で安全に医療情報を共有するためのWebアプリケーションです。

> **開発者向け詳細**  
> このREADMEは開発者向けの技術詳細とセットアップガイドです。  
> プロダクト概要は [../README.md](../README.md) を参照してください。

## プロジェクト構造

```
SecHack365_project/
├── info_sharing_system/         # メインアプリケーション
│   ├── app/
│   │   ├── app.py              # Flaskアプリケーション
│   │   ├── templates/          # HTMLテンプレート
│   │   ├── static/             # CSS/JavaScript
│   │   └── certs/              # SSL証明書
│   └── run_app.py              # 起動スクリプト
│
├── core/                        # 共通セキュリティモジュール
│   ├── authentication.py       # 認証システム
│   ├── digital_signature.py    # デジタル署名
│   ├── data_encryption.py      # データ暗号化
│   └── audit_logger.py         # 監査ログ
│
├── scripts/
│   └── generate_cert.py        # SSL証明書生成
│
├── requirements.txt
└── README.md
```

## セットアップ

### 環境準備

```bash
# リポジトリのクローン
git clone https://github.com/Suisan-neki/SecHack365_electronic-medical-record.git
cd SecHack365_electronic-medical-record/SecHack365_project

# 仮想環境の作成（推奨）
python -m venv venv

# 仮想環境の有効化
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### アプリケーションの起動

```bash
# 情報共有システムディレクトリに移動
cd info_sharing_system

# アプリケーションを起動
python run_app.py
```

### アクセス

- URL: http://localhost:5001
- デモアカウント: doctor1, admin1, patient1

## 実装済み機能

### 🔐 セキュリティ機能
- **デジタル署名**: RSA 2048bit + PSS padding + SHA-256による患者データの署名検証
- **暗号化**: AES-256-GCMによるデータ暗号化とPBKDF2-SHA256によるキー導出
- **多要素認証**: TOTP（Time-based One-Time Password）+ WebAuthn（FIDO2）対応
- **アクセス制御**: RBAC（Role-Based Access Control）とABAC（Attribute-Based Access Control）
- **監査ログ**: 全操作の記録と追跡、ハッシュチェーンによる整合性検証

### 👥 ユーザーインターフェース
- **医師向け管理画面**: 患者情報の抽出・管理・表示、セキュリティ検証ダッシュボード
- **患者向け表示画面**: 分かりやすい医療情報の表示、アクセシビリティ機能
- **アクセシビリティ**: 大きな文字・ふりがな表示機能（DOM操作による動的変換）
- **リアルタイム表示**: 現在時刻の自動更新、WebSocket通信による即座の反映

### 📊 システム管理
- **セキュリティ検証**: システム全体のセキュリティ状況を総合チェック（6項目検証）
- **WebAuthn管理**: FIDO2認証器の登録・削除・管理、Credential ID管理
- **監査ダッシュボード**: 操作履歴と統計情報の表示、JSON形式でのログ出力

## 技術スタック

- **バックエンド**: Python 3.9+, Flask 2.3+, Jinja2
- **セキュリティ**: cryptography, WebAuthn, passlib, pyotp
- **認証**: Flask-Login, TOTP, FIDO2, PBKDF2-SHA256
- **フロントエンド**: HTML5, CSS3, JavaScript (ES6+), DOM操作
- **データ形式**: JSON, PEM証明書形式
- **暗号化**: RSA 2048bit, AES-256-GCM, SHA-256

## デモアカウント

- **doctor1** (医師): パスワード認証 + MFA/WebAuthn対応
- **admin1** (管理者): パスワード認証 + MFA対応
- **patient1** (患者): パスワード認証対応

## 開発用コマンド

```bash
# SSL証明書の手動生成
python scripts/generate_cert.py --cert-dir ./custom_cert_dir

# 特定のコモンネームで証明書生成
python scripts/generate_cert.py --common-name example.com

# 開発サーバーの起動（デバッグモード）
cd info_sharing_system
python run_app.py
```

## 今後の開発予定

- [ ] ラズパイ表示機能の実装（Chromium kiosk mode）
- [ ] FHIR標準への対応（R4準拠）
- [ ] より多くの患者データの管理
- [ ] モバイルアプリ対応（PWA）

## トラブルシューティング

### SSL証明書エラー
```bash
python scripts/generate_cert.py --cert-dir info_sharing_system/app/certs
```

### 依存関係エラー
```bash
pip install -r requirements.txt --force-reinstall
```

### ポートエラー
5001番ポートが使用中の場合は、他のアプリケーションを停止するか、`run_app.py`内のポート番号を変更してください。

## ライセンス

このプロジェクトはSecHack365の一環として開発されています。