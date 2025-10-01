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

### 🔗 既存システム連携（NEW!）
- **FHIR対応**: HL7 FHIR R4標準形式でのデータ入出力をサポート
- **CSV入出力**: 汎用的なCSV形式での既存カルテデータのインポート/エクスポート
- **APIエンドポイント**: RESTful APIによる外部システムとの連携
- **完全無料**: オープンソースライブラリのみを使用し、追加コストなし

詳細は [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) を参照してください。

### 👥 ユーザーインターフェース
- **医師向け管理画面**: 患者情報の抽出・管理・表示、セキュリティ検証ダッシュボード
- **患者向け表示画面**: 分かりやすい医療情報の表示、アクセシビリティ機能
- **アクセシビリティ**: 大きな文字・ふりがな表示機能（DOM操作による動的変換）
- **リアルタイム表示**: 現在時刻の自動更新、WebSocket通信による即座の反映

### 📊 システム管理
- **セキュリティ検証**: システム全体のセキュリティ状況を総合チェック（6項目検証）
- **WebAuthn管理**: FIDO2認証器の登録・削除・管理、Credential ID管理
- **監査ダッシュボード**: 操作履歴と統計情報の表示、JSON形式でのログ出力

## 技術仕様

### 全般技術

#### アーキテクチャ設計
- **MVCパターン**: Model-View-Controllerによる責任分離
- **RESTful API**: HTTPメソッドに基づくリソース指向設計
- **セッション管理**: Flask-Loginによる状態管理
- **テンプレートエンジン**: Jinja2による動的HTML生成

#### バックエンド技術
- **Python 3.9+**: 動的型付け、豊富なライブラリエコシステム
- **Flask 2.3+**: 軽量Webフレームワーク、Werkzeug WSGIツールキット
- **SQLAlchemy**: ORM（Object-Relational Mapping）によるデータベース抽象化
- **JSON**: データ交換形式、人間可読性とパース効率のバランス

#### フロントエンド技術
- **HTML5**: セマンティックマークアップ、アクセシビリティ対応
- **CSS3**: Flexbox/Gridレイアウト、CSS変数、アニメーション
- **JavaScript ES6+**: モジュール、アロー関数、Promise/async-await
- **DOM操作**: リアルタイムUI更新、イベントハンドリング
- **WebSocket**: 双方向通信、リアルタイムデータ同期

#### データ管理
- **JSON形式**: 患者データ、設定情報、ログの保存
- **ファイルベース**: シンプルな永続化、スケーラビリティ制限
- **メモリキャッシュ**: セッション情報、一時データの高速アクセス

#### 現在の課題
- **スケーラビリティ**: 単一サーバー構成、データベース未使用
- **パフォーマンス**: 大量データ処理時のメモリ使用量
- **可用性**: 単一障害点、冗長化未対応
- **データ整合性**: ファイルベースによる同時アクセス制御の限界

#### 今後の展望・障壁
- **マイクロサービス化**: 認証、データ処理、表示の分離
- **データベース移行**: PostgreSQL/MySQLへの移行、ACID特性の確保
- **キャッシュ戦略**: Redis/Memcachedによる高速化
- **負荷分散**: Nginx/HAProxyによる水平スケーリング
- **監視・ログ**: Prometheus/Grafanaによる運用監視

### セキュリティ技術

#### 暗号化技術
- **RSA 2048bit**: 非対称暗号化、デジタル署名の基盤
- **AES-256-GCM**: 対称暗号化、認証付き暗号化による改ざん検出
- **PBKDF2-SHA256**: パスワードベースキー導出、ソルト付きハッシュ
- **SHA-256**: ハッシュ関数、データ整合性検証

#### 認証・認可
- **TOTP (Time-based One-Time Password)**: RFC 6238準拠、時間ベースワンタイムパスワード
- **WebAuthn (FIDO2)**: W3C標準、生体認証・ハードウェア認証器対応
- **RBAC (Role-Based Access Control)**: 役割ベースアクセス制御
- **ABAC (Attribute-Based Access Control)**: 属性ベースアクセス制御

#### デジタル署名
- **PSS Padding**: RSA-PSSによる署名、MGF1+SHA-256
- **署名検証**: 公開鍵による署名の真正性確認
- **鍵管理**: PEM形式での鍵保存、秘密鍵の暗号化保護

#### 監査・ログ
- **ハッシュチェーン**: ログの連鎖的整合性検証
- **監査ログ**: 全操作の記録、改ざん防止
- **タイムスタンプ**: UTC時刻による操作時点の記録

#### データ保護
- **暗号化保存**: 患者データのAES-256-GCM暗号化
- **キー分離**: 暗号化キーとアプリケーションの分離
- **メモリ保護**: 機密データのメモリ上での適切な処理

#### 現在の課題
- **鍵管理**: ハードウェアセキュリティモジュール（HSM）未使用
- **量子耐性**: 量子コンピュータ攻撃への対応未実装
- **ゼロトラスト**: ネットワーク境界の信頼モデル未適用
- **セキュリティ監視**: 異常検知・インシデント対応の自動化不足

#### 今後の展望・障壁
- **HSM導入**: ハードウェアベースの鍵管理、FIPS 140-2 Level 3対応
- **量子暗号**: ポスト量子暗号アルゴリズム（NIST選定）への移行
- **ゼロトラストアーキテクチャ**: マイクロセグメンテーション、継続的認証
- **AI/MLセキュリティ**: 異常検知、脅威インテリジェンス統合
- **コンプライアンス**: GDPR、HIPAA、個人情報保護法への完全対応
- **セキュリティ教育**: 医療従事者向けセキュリティ意識向上プログラム

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