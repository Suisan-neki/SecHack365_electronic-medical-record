# 医療記録システム - セキュリティ強化版

## 概要

このシステムは、医療情報の安全な管理と共有を目的とした電子カルテシステムです。PostgreSQLデータベースを使用し、医療従事者の法的保護とデータの整合性を重視した設計となっています。

## 主な機能

- **患者情報管理**: 患者の基本情報、診療記録、医療データの管理
- **認証・認可**: 多要素認証（MFA）、WebAuthn対応
- **監査ログ**: すべての操作を記録し、改ざんを防止
- **データ暗号化**: 機密情報の暗号化保存
- **権限管理**: 役割ベースのアクセス制御

## セキュリティ強化点

### 1. データベース移行
- **SQLite → PostgreSQL**: 同時接続、トランザクション、権限管理に対応
- **ACID特性**: データの整合性を保証
- **スケーラビリティ**: 複数ユーザー対応

### 2. 機密情報の保護
- **環境変数**: 秘密鍵、パスワード等を環境変数で管理
- **Git履歴クリーンアップ**: 漏えいした機密情報を完全削除
- **.gitignore強化**: 機密ファイルの再混入を防止

### 3. セキュリティヘッダー
- **X-Content-Type-Options**: MIMEタイプスニッフィング防止
- **X-Frame-Options**: クリックジャッキング防止
- **X-XSS-Protection**: XSS攻撃防止
- **Strict-Transport-Security**: HTTPS強制

### 4. 監査ログ
- **全操作記録**: ユーザーのすべての操作を記録
- **改ざん防止**: ログの整合性を保証
- **追跡可能性**: 問題発生時の原因特定が可能

## セットアップ手順

### 1. 前提条件
- Docker & Docker Compose
- Python 3.8+
- Git

### 2. セットアップ実行
```bash
# リポジトリクローン
git clone <repository-url>
cd SecHack365_electronic-medical-record

# セットアップ実行
python setup.py
```

### 3. 手動セットアップ（必要に応じて）
```bash
# 環境変数設定
cp env.example .env
# .envファイルを編集して本番環境用の設定を行う

# 依存関係インストール
pip install -r requirements.txt

# PostgreSQL起動
docker-compose up -d postgres

# データベースマイグレーション
alembic upgrade head

# ダミーデータ生成
python scripts/generate_dummy_data.py

# アプリケーション起動
python app.py
```

## 環境変数設定

`.env`ファイルで以下の設定を行ってください：

```env
# データベース設定
DATABASE_URL=postgresql://medical_user:medical_password@localhost:5432/medical_records

# セキュリティ設定（本番環境では必ず変更）
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
ENCRYPTION_KEY=your-32-character-encryption-key-here

# その他の設定
MFA_ISSUER_NAME=Medical Records System
LOG_LEVEL=INFO
```

## データベース構造

### 主要テーブル
- **ehr_system.patients**: 患者情報
- **ehr_system.medical_records**: 医療記録
- **ehr_system.encounters**: 診療記録
- **info_sharing.users**: ユーザー認証情報
- **info_sharing.webauthn_credentials**: WebAuthn認証情報
- **audit_logs**: 監査ログ

## API エンドポイント

### 認証
- `POST /api/auth/login` - ログイン
- `POST /api/auth/logout` - ログアウト
- `POST /api/auth/register` - ユーザー登録

### 患者管理
- `GET /api/patients` - 患者一覧
- `GET /api/patients/{patient_id}` - 患者詳細
- `POST /api/patients` - 患者登録
- `PUT /api/patients/{patient_id}` - 患者情報更新

### 医療記録
- `GET /api/patients/{patient_id}/records` - 患者の医療記録
- `POST /api/patients/{patient_id}/records` - 医療記録作成
- `PUT /api/records/{record_id}` - 医療記録更新

## セキュリティ考慮事項

### 1. 本番環境での設定
- 強力なパスワードと秘密鍵を使用
- HTTPSを有効化
- 定期的なセキュリティアップデート
- アクセスログの監視

### 2. データ保護
- 個人情報の適切な管理
- アクセス権限の最小化
- 定期的なバックアップ
- 暗号化の実装

### 3. 監査とコンプライアンス
- 監査ログの定期的な確認
- 法的要件への準拠
- セキュリティインシデント対応

## トラブルシューティング

### よくある問題
1. **データベース接続エラー**: PostgreSQLが起動しているか確認
2. **認証エラー**: 環境変数の設定を確認
3. **権限エラー**: データベースユーザーの権限を確認

### ログ確認
```bash
# アプリケーションログ
tail -f logs/app.log

# データベースログ
docker-compose logs postgres
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。セキュリティに関する問題は、直接連絡してください。

## 連絡先

セキュリティに関する問題や質問がある場合は、プロジェクトのイシューページで報告してください。
