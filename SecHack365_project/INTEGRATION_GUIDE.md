# 既存電子カルテシステム連携ガイド

このシステムは、既存の電子カルテシステムとの連携機能を提供します。

## 対応形式

### 1. FHIR (Fast Healthcare Interoperability Resources)
国際標準規格のHL7 FHIRに対応しています。

### 2. CSV
汎用的なCSV形式でのデータ入出力に対応しています。

---

## FHIR連携

### 概要
- FHIR R4に準拠
- 対応リソース: `Observation`, `Condition`, `MedicationRequest`
- Bundle形式でのインポート/エクスポートをサポート

### APIエンドポイント

#### 1. FHIRデータのインポート
```http
POST /api/import/fhir
Content-Type: application/json

{
  "fhir_bundle": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [...]
  }
}
```

**レスポンス例:**
```json
{
  "success": true,
  "medical_record": {
    "symptoms": "発熱、咳",
    "diagnosis": "急性上気道炎",
    "medication": "カロナール 500mg 1日3回 3日分 食後",
    ...
  }
}
```

#### 2. FHIRデータのエクスポート
```http
GET /api/export/fhir/<session_id>
```

**レスポンス例:**
```json
{
  "success": true,
  "fhir_bundle": {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [...]
  }
}
```

#### 3. サンプルFHIR Bundleの取得
```http
GET /api/sample/fhir
```

### 使用例（Python）

```python
import requests
import json

# ログイン（省略）

# FHIRデータをインポート
fhir_data = {
    "fhir_bundle": {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Observation",
                    "status": "final",
                    "code": {"text": "発熱"},
                    "valueString": "38.5度"
                }
            }
        ]
    }
}

response = requests.post(
    "http://127.0.0.1:5001/api/import/fhir",
    json=fhir_data,
    cookies=session_cookies
)

print(response.json())
```

---

## CSV連携

### 概要
- シンプルなCSV形式
- Excel等の表計算ソフトで編集可能
- 既存システムからのエクスポートが容易

### CSV形式

#### 列定義
| 列名 | 説明 | 必須 |
|------|------|------|
| patient_id | 患者ID | ○ |
| timestamp | タイムスタンプ | - |
| symptoms | 症状 | ○ |
| diagnosis | 診断名 | ○ |
| diagnosis_details | 診断詳細 | - |
| medication | 処方薬 | - |
| medication_instructions | 服薬指導 | - |
| treatment_plan | 治療計画 | - |
| follow_up | フォローアップ | - |
| patient_explanation | 患者向け説明 | - |

#### サンプルCSV
```csv
patient_id,timestamp,symptoms,diagnosis,medication
P001,2025-10-01T10:00:00,発熱、咳、鼻水,急性上気道炎,カロナール 500mg 1日3回 3日分 食後
P002,2025-10-01T11:00:00,腹痛、下痢,急性胃腸炎,ナウゼリン 10mg 1日3回 3日分 食前
```

### APIエンドポイント

#### 1. CSVデータのインポート（ファイルアップロード）
```http
POST /api/import/csv
Content-Type: multipart/form-data

file: <CSVファイル>
```

#### 2. CSVデータのインポート（JSONリクエスト）
```http
POST /api/import/csv
Content-Type: application/json

{
  "csv_content": "patient_id,timestamp,symptoms,diagnosis,...\nP001,2025-10-01,発熱,風邪,..."
}
```

**レスポンス例:**
```json
{
  "success": true,
  "medical_records": [
    {
      "patient_id": "P001",
      "symptoms": "発熱、咳",
      "diagnosis": "急性上気道炎",
      ...
    }
  ],
  "count": 1,
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  }
}
```

#### 3. CSVデータのエクスポート
```http
POST /api/export/csv
Content-Type: application/json

{
  "session_ids": ["session123", "session456"]
}
```

**レスポンス:** CSVファイルのダウンロード

#### 4. CSVテンプレートのダウンロード
```http
GET /api/template/csv
```

**レスポンス:** サンプル行付きのCSVテンプレートファイル

### 使用例（Python）

```python
import requests

# CSVファイルをインポート
with open('medical_records.csv', 'rb') as f:
    response = requests.post(
        "http://127.0.0.1:5001/api/import/csv",
        files={'file': f},
        cookies=session_cookies
    )

print(response.json())

# CSVファイルをエクスポート
response = requests.post(
    "http://127.0.0.1:5001/api/export/csv",
    json={"session_ids": ["session123"]},
    cookies=session_cookies
)

with open('export.csv', 'wb') as f:
    f.write(response.content)
```

---

## セットアップ

### 1. 依存関係のインストール

```bash
cd SecHack365_project
pip install -r requirements.txt
```

### 2. 必要なパッケージ
- `fhir.resources>=7.0.0` - FHIR対応
- `pandas>=2.0.0` - CSV処理

### 3. アプリケーション起動

```bash
cd info_sharing_system
python run_app.py
```

---

## 既存システムとの連携パターン

### パターン1: FHIR対応電子カルテと連携
```
既存電子カルテ (FHIR API)
    ↓ FHIR Bundle
このシステム (/api/import/fhir)
    ↓ 患者説明・同意取得
このシステム (/api/export/fhir)
    ↓ FHIR Bundle
既存電子カルテ (FHIR API)
```

### パターン2: CSV経由で連携
```
既存電子カルテ
    ↓ CSV Export
このシステム (/api/import/csv)
    ↓ 患者説明・同意取得
このシステム (/api/export/csv)
    ↓ CSV Import
既存電子カルテ
```

### パターン3: 単独システムとして使用
```
このシステムで直接入力
    ↓ input_form
患者説明・同意取得
    ↓ 必要に応じてエクスポート
FHIR/CSV形式で保存
```

---

## トラブルシューティング

### FHIR関連

**Q: `fhir.resources` のインポートエラーが出る**
```bash
pip install fhir.resources
```

**Q: FHIR Bundleのパースエラー**
- FHIR R4形式に準拠しているか確認
- サンプルを確認: `GET /api/sample/fhir`

### CSV関連

**Q: CSVの形式エラー**
- テンプレートをダウンロード: `GET /api/template/csv`
- UTF-8エンコーディングを使用
- 必須列（patient_id, symptoms, diagnosis）を含める

**Q: 日本語が文字化けする**
- CSVファイルをUTF-8 BOMで保存
- Excelの場合: 「CSV UTF-8」形式でエクスポート

---

## セキュリティ

- すべてのAPI呼び出しには認証が必要（Flask-Login）
- 医師・管理者権限が必要
- すべての操作は監査ログに記録
- データは暗号化して保存

---

## サポート

問題が発生した場合:
1. 監査ログを確認: `audit.log`
2. アプリケーションログを確認
3. サンプルデータで動作確認

---

## ライセンス

SecHack365 医療情報共有プロジェクト

