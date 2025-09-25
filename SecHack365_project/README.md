# 患者情報共有システム

お医者さんと患者さんが、安全に医療情報を共有できるWebアプリケーションです。

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
- **デジタル署名**: データが改ざんされていないことを証明する技術（RSA 2048bit）
- **暗号化**: 情報を暗号化して第三者に見られないように保護（AES-256-GCM）
- **多要素認証**: パスワードに加えて、スマホアプリや指紋認証で二重にセキュリティを確保
- **アクセス制御**: お医者さん、患者さんなど、役割に応じて見られる情報を制限
- **監査ログ**: 誰がいつ何をしたかを記録して、不正アクセスを防ぐ

### 👥 使いやすい画面
- **お医者さん向け画面**: 患者さんの情報を安全に管理・表示
- **患者さん向け画面**: 医療用語を分かりやすく表示
- **アクセシビリティ機能**: 大きな文字・ふりがな表示で、高齢の方にも見やすく
- **リアルタイム表示**: 現在時刻を自動更新

### 📊 システム管理機能
- **セキュリティ検証**: システム全体のセキュリティ状況を自動チェック
- **認証器管理**: 指紋認証などの認証器を登録・削除・管理
- **操作履歴**: 誰がいつ何をしたかの記録を確認

## 使用技術

- **プログラム言語**: Python 3.9+（Webアプリケーション作成）
- **セキュリティ**: 暗号化ライブラリ、指紋認証（WebAuthn）
- **認証システム**: ログイン機能、二段階認証
- **画面表示**: HTML5, CSS3, JavaScript（Webページ作成）
- **データ形式**: JSON（データの保存形式）

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

- [ ] ラズパイ（小型コンピュータ）での表示機能
- [ ] 医療データの標準形式（FHIR）への対応
- [ ] より多くの患者データの管理
- [ ] スマホアプリの開発

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