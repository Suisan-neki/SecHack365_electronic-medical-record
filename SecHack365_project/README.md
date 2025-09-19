# SecHack365 患者中心の医療DXプロジェクト（モノレポ版）

## 🏗️ プロジェクト構造

このプロジェクトは、患者の「知る権利」を技術的に保障し、医療従事者との協働を促進する次世代の診療体験を創出するモノレポ構成のシステムです。

```
SecHack365_project/
├── 📁 info_sharing_system/      # 患者向け情報共有システム
│   ├── app/
│   │   ├── app.py              # Flaskアプリケーション
│   │   ├── templates/          # HTMLテンプレート
│   │   ├── static/             # CSS/JavaScript
│   │   ├── certs/              # SSL証明書（自動生成）
│   │   └── *.json              # デモデータ
│   └── run_app.py              # 起動スクリプト
│
├── 📁 ehr_system/               # 院内電子カルテシステム（今後開発）
│   └── app/                    # 将来の拡張用
│
├── 📁 core/                     # 共通コアモジュール
│   ├── authorization.py        # 認可トークン管理
│   ├── digital_signature.py    # 電子署名機能
│   ├── hash_chain.py          # ハッシュチェーン機能
│   ├── permissions.py         # 権限制御システム
│   └── ehr_translator.py      # 電子カルテ翻訳機能
│
├── 📁 scripts/                  # 開発支援スクリプト
│   └── generate_cert.py        # SSL証明書生成ツール
│
├── requirements.txt            # Python依存関係
└── README.md                   # このファイル
```

## 🚀 クイックスタート

### 1. 環境準備

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

### 2. 情報共有システムの起動

```bash
# 情報共有システムディレクトリに移動
cd info_sharing_system

# アプリケーションを起動（SSL証明書は自動生成）
python run_app.py
```

### 3. ブラウザでアクセス

- URL: https://localhost:5000
- 自己署名証明書の警告が表示された場合は「詳細設定」→「localhost に進む」を選択

## 🔐 セキュリティ機能

### 実装済みセキュリティ基盤

- **HTTPS通信**: TLS暗号化による通信保護
- **電子署名**: RSA-PSS方式による医療データの真正性保証  
- **ハッシュチェーン**: SHA-256による操作履歴とデータ完全性の証明
- **認可システム**: 役割ベースアクセス制御（医師・看護師・管理者）
- **自動SSL証明書生成**: 開発用自己署名証明書の自動生成

### セキュリティ検証

アプリケーション内の「セキュリティ検証ページ」で以下を確認できます：

- HTTPS通信の暗号化状態
- 電子署名の生成・検証結果
- ハッシュチェーンの完全性
- 認可トークンの有効性

## 🎯 主要機能

### 患者向け機能
- **医療情報の平易化**: FHIR標準データを患者が理解しやすい日本語に自動翻訳
- **視覚的な情報表示**: アイコンや色分けを使った直感的なUI
- **詳細な説明提供**: 病気や薬について分かりやすい説明を表示

### 医療従事者向け機能  
- **権限管理**: 職種に応じた機能制限
- **操作履歴**: 全ての医療行為をハッシュチェーンで記録
- **EHRシステム連携**: 既存の電子カルテシステムからのデータ抽出

## 🛠️ 開発情報

### 技術スタック

- **バックエンド**: Python 3.9+, Flask
- **フロントエンド**: HTML5, CSS3, JavaScript (Vanilla)
- **セキュリティ**: cryptography library, HTTPS/TLS
- **データ形式**: FHIR標準準拠JSON

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

## 🔄 今後の開発予定

### Phase 1: セキュリティ強化（進行中）
- [ ] JWT ベースの本格的な認証システム
- [ ] リフレッシュトークン機能
- [ ] API セキュリティ強化（Rate limiting, CORS設定）
- [ ] 監査ログの体系化

### Phase 2: EHRシステム開発
- [ ] 院内電子カルテシステムの実装
- [ ] システム間連携API
- [ ] データ同期機能

### Phase 3: 運用機能強化
- [ ] ログ分析機能
- [ ] パフォーマンス監視
- [ ] コンプライアンス対応

## 📞 サポート

### トラブルシューティング

**SSL証明書エラー**
```bash
# 証明書を再生成
python scripts/generate_cert.py --cert-dir info_sharing_system/app/certs
```

**依存関係エラー**
```bash
# 依存関係を再インストール
pip install -r requirements.txt --force-reinstall
```

**ポートエラー（5000番ポートが使用中）**
- 他のアプリケーションを停止するか、`run_app.py`内のポート番号を変更してください

### 開発環境の確認

```bash
# Python バージョン確認
python --version

# 必要パッケージの確認
pip list | grep -E "(Flask|cryptography)"

# 仮想環境の確認
which python  # macOS/Linux
where python  # Windows
```

---

**SecHack365 患者中心の医療DXプロジェクト**  
患者の医療情報アクセス権を技術で保障し、医療DXを推進します。