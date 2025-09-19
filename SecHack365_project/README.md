# SecHack365 医療情報共有システム

患者の医療情報アクセス権を技術で保障し、医療従事者との協働を促進するシステムです。

## プロジェクト構造

```
SecHack365_project/
├── info_sharing_system/         # 患者向け情報共有システム
│   ├── app/
│   │   ├── app.py              # Flaskアプリケーション
│   │   ├── templates/          # HTMLテンプレート
│   │   ├── static/             # CSS/JavaScript
│   │   └── certs/              # SSL証明書
│   └── run_app.py              # 起動スクリプト
│
├── ehr_system/                  # 電子カルテシステム（開発予定）
│   └── app/
│
├── core/                        # 共通モジュール
│   ├── authentication.py       # 認証機能
│   ├── authorization.py        # 認可機能
│   ├── digital_signature.py    # 電子署名
│   ├── hash_chain.py           # ハッシュチェーン
│   └── ehr_translator.py       # データ翻訳
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
git clone <repository-url>
cd SecHack365_project

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

# アプリケーションを起動（SSL証明書は自動生成）
python run_app.py
```

### アクセス

- URL: https://localhost:5000
- 自己署名証明書の警告が表示された場合は「詳細設定」→「localhost に進む」を選択

## 機能

### セキュリティ機能

- HTTPS通信（TLS暗号化）
- 電子署名（RSA-PSS + SHA-256）
- ハッシュチェーン（SHA-256ベース）
- 認証・認可システム（RBAC/ABAC）
- 多要素認証（TOTP）
- WebAuthn（FIDO2）対応

### 主要機能

- 医療情報の平易化（FHIR → 患者向け日本語）
- 視覚的な情報表示
- 権限管理（職種別アクセス制御）
- 操作履歴の記録
- EHRシステム連携

## 技術情報

### 技術スタック

- バックエンド: Python 3.9+, Flask
- フロントエンド: HTML5, CSS3, JavaScript
- セキュリティ: cryptography, WebAuthn
- データ形式: FHIR準拠JSON

### 開発用コマンド

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

- 院内電子カルテシステムの実装
- システム間連携API
- 監査ログの体系化
- パフォーマンス監視

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
5000番ポートが使用中の場合は、他のアプリケーションを停止するか、`run_app.py`内のポート番号を変更してください。