# 医療情報共有システム

患者の医療情報アクセス権を技術で保障し、医療従事者との協働を促進するシステムです。

## 概要

このプロジェクトは、患者が自分の医療情報に簡単にアクセスし、理解できるようにすることを目的としています。FHIR標準に準拠した医療データを患者向けの分かりやすい日本語に変換し、セキュアな環境で提供します。

## 主な特徴

- **セキュリティ重視**: HTTPS、電子署名、ハッシュチェーンによる堅牢なセキュリティ
- **多要素認証**: TOTP + WebAuthn（FIDO2）対応
- **医療情報の平易化**: FHIR → 患者向け日本語への自動変換
- **アクセス制御**: 役割ベース・属性ベースの認可システム
- **モノレポ構成**: 複数システムの統合管理

## システム構成

```
SecHack365_project/
├── info_sharing_system/     # 患者向け情報共有システム
├── ehr_system/              # 電子カルテシステム（開発予定）
├── core/                    # 共通セキュリティモジュール
└── scripts/                 # 開発支援ツール
```

## クイックスタート

```bash
# リポジトリのクローン
git clone https://github.com/Suisan-neki/SecHack365_electronic-medical-record.git
cd SecHack365_electronic-medical-record/SecHack365_project

# 依存関係のインストール
pip install -r requirements.txt

# アプリケーションの起動
cd info_sharing_system
python run_app.py
```

アプリケーションは https://localhost:5000 でアクセスできます。

## 技術スタック

- **バックエンド**: Python 3.9+, Flask
- **セキュリティ**: cryptography, WebAuthn
- **認証**: Flask-Login, TOTP, FIDO2
- **データ形式**: FHIR準拠JSON

## デモアカウント

- **doctor1** (医師): パスワード認証 + MFA/WebAuthn対応
- **admin1** (管理者): パスワード認証 + MFA対応
- **patient1** (患者): パスワード認証対応
