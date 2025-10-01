# 模擬電子カルテシステム (Dummy EHR System)

既存の電子カルテシステムを模擬し、メインシステムとのデータ連携をデモするためのシステムです。

## 🎯 目的

- メインシステム（患者説明・同意取得システム）との連携をデモで視覚化
- CSV/FHIR形式でのデータ抽出・受信機能を実証
- 実際の運用フローを分かりやすく説明

## 📊 システム構成

```
模擬電子カルテ (port:5002) ←→ メインシステム (port:5001) → 患者ディスプレイ
     │                                  │
     │                                  │
  [患者情報管理]                  [リアルタイム入力・表示]
  [診療記録保存]                  [患者説明・同意取得]
  [CSV/FHIR出力]                  [セキュアなデータ管理]
  [データ受信]
```

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
cd dummy_ehr_system
pip install -r requirements.txt
```

### 2. 起動

```bash
python run_dummy_ehr.py
```

または

```bash
python app/app.py
```

### 3. アクセス

ブラウザで `http://127.0.0.1:5002` を開く

## 📡 API エンドポイント

### データ抽出 (Export)

#### CSV形式でエクスポート
```http
GET /api/export/csv/<patient_id>
```

**例**: `http://127.0.0.1:5002/api/export/csv/P001`

#### FHIR形式でエクスポート
```http
GET /api/export/fhir/<patient_id>
```

**例**: `http://127.0.0.1:5002/api/export/fhir/P001`

### データ受信 (Import)

#### CSVをインポート
```http
POST /api/import/csv
Content-Type: multipart/form-data

file: [CSVファイル]
```

#### FHIRをインポート
```http
POST /api/import/fhir
Content-Type: application/json

{
  "resourceType": "Bundle",
  ...
}
```

## 🔄 連携デモシナリオ

### シナリオ1: 既存カルテ → メインシステム（データ抽出）

```
1. 模擬電子カルテで患者を選択
   http://127.0.0.1:5002/patients
   
2. 「CSV」ボタンをクリック
   → patient_P001_YYYYMMDD.csv がダウンロードされる
   
3. メインシステムでインポート
   http://127.0.0.1:5001/input_form
   → CSVインポート機能を使用
   
4. 診察実施・患者説明・同意取得
```

### シナリオ2: メインシステム → 既存カルテ（データ送信）

```
1. メインシステムで診察完了
   http://127.0.0.1:5001/input_form
   
2. CSVエクスポート
   → medical_record_YYYYMMDD.csv を保存
   
3. 模擬電子カルテでインポート
   Postman等で POST /api/import/csv
   または curlコマンド:
   
   curl -X POST http://127.0.0.1:5002/api/import/csv \
        -F "file=@medical_record_YYYYMMDD.csv"
   
4. 模擬電子カルテで記録を確認
   http://127.0.0.1:5002/records
```

## 📦 サンプルデータ

初回起動時に自動的に作成されます：

### 患者データ (3名)
- P001: 山田太郎
- P002: 佐藤花子
- P003: 鈴木一郎

### 診療記録 (2件)
- 急性上気道炎の診療記録
- 急性胃腸炎の診療記録

## 🔧 開発メモ

### ファイル構成
```
dummy_ehr_system/
├── app/
│   ├── app.py              # メインアプリケーション
│   └── templates/          # HTMLテンプレート
│       ├── index.html      # ダッシュボード
│       ├── patient_list.html
│       ├── patient_detail.html
│       └── records.html
├── data/                   # データ保存先
│   ├── patients.json       # 患者情報
│   └── medical_records.json# 診療記録
├── run_dummy_ehr.py        # 起動スクリプト
└── requirements.txt
```

### データフォーマット

#### patients.json
```json
{
  "patient_id": "P001",
  "name": "山田太郎",
  "birth_date": "1980-05-15",
  "gender": "男性",
  "allergies": "ペニシリン"
}
```

#### medical_records.json
```json
{
  "record_id": "REC001",
  "patient_id": "P001",
  "date": "2025-09-15T10:30:00",
  "diagnosis": "急性上気道炎",
  "treatment": "カロナール 500mg..."
}
```

## 🎬 デモで示すポイント

1. **データの抽出**: 既存カルテからCSV/FHIRでデータを取り出せる
2. **メインシステムでの処理**: リアルタイムで患者に説明・同意取得
3. **データの戻し**: 診察結果を既存カルテに送信できる
4. **標準化対応**: FHIR形式で将来の標準化にも対応

## 💡 今後の拡張

- [ ] リアルタイム同期（WebSocket）
- [ ] HL7 V2.x対応
- [ ] より詳細な患者情報
- [ ] 処方箋・検査結果の管理
- [ ] 画像データの連携

---

**Note**: これは教育・デモ目的の模擬システムです。実際の医療現場での使用は想定していません。

