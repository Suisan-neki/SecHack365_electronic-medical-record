"""
CSV入出力ハンドラー
既存の電子カルテシステムとCSV形式でデータ連携するためのモジュール
"""

import csv
import io
from typing import Dict, List, Any
from datetime import datetime


class CSVHandler:
    """CSV形式のデータと内部形式の変換を行うハンドラー"""
    
    # CSV列の定義
    CSV_COLUMNS = [
        "patient_id",
        "timestamp",
        "symptoms",
        "diagnosis",
        "diagnosis_details",
        "medication",
        "medication_instructions",
        "treatment_plan",
        "follow_up",
        "patient_explanation"
    ]
    
    def __init__(self):
        pass
    
    def import_from_csv(self, csv_content: str) -> List[Dict[str, Any]]:
        """
        CSV形式の文字列を受け取り、内部形式のリストに変換
        
        Args:
            csv_content: CSV形式の文字列
            
        Returns:
            内部形式の医療記録辞書のリスト
        """
        records = []
        
        try:
            # CSV文字列をパース
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            for row in reader:
                record = {
                    "patient_id": row.get("patient_id", ""),
                    "timestamp": row.get("timestamp", datetime.now().isoformat()),
                    "symptoms": row.get("symptoms", ""),
                    "diagnosis": row.get("diagnosis", ""),
                    "diagnosis_details": row.get("diagnosis_details", ""),
                    "medication": row.get("medication", ""),
                    "medication_instructions": row.get("medication_instructions", ""),
                    "treatment_plan": row.get("treatment_plan", ""),
                    "follow_up": row.get("follow_up", ""),
                    "patient_explanation": row.get("patient_explanation", "")
                }
                records.append(record)
            
            return records
            
        except Exception as e:
            raise ValueError(f"CSV parsing failed: {str(e)}")
    
    def export_to_csv(self, medical_records: List[Dict[str, Any]]) -> str:
        """
        内部形式の医療記録リストをCSV形式の文字列に変換
        
        Args:
            medical_records: 内部形式の医療記録辞書のリスト
            
        Returns:
            CSV形式の文字列
        """
        try:
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=self.CSV_COLUMNS)
            
            # ヘッダー行を書き込み
            writer.writeheader()
            
            # データ行を書き込み
            for record in medical_records:
                row = {
                    "patient_id": record.get("patient_id", ""),
                    "timestamp": record.get("timestamp", datetime.now().isoformat()),
                    "symptoms": record.get("symptoms", ""),
                    "diagnosis": record.get("diagnosis", ""),
                    "diagnosis_details": record.get("diagnosis_details", ""),
                    "medication": record.get("medication", ""),
                    "medication_instructions": record.get("medication_instructions", ""),
                    "treatment_plan": record.get("treatment_plan", ""),
                    "follow_up": record.get("follow_up", ""),
                    "patient_explanation": record.get("patient_explanation", "")
                }
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            raise ValueError(f"CSV export failed: {str(e)}")
    
    def create_template_csv(self) -> str:
        """
        空のテンプレートCSVを作成（サンプル行付き）
        
        Returns:
            テンプレートCSV形式の文字列
        """
        sample_record = {
            "patient_id": "P001",
            "timestamp": datetime.now().isoformat(),
            "symptoms": "発熱、咳、鼻水",
            "diagnosis": "急性上気道炎",
            "diagnosis_details": "3日前から発熱。解熱剤で一時的に下がるが再び上昇。",
            "medication": "カロナール 500mg 1日3回 3日分 食後、ムコダイン 500mg 1日3回 5日分 食後",
            "medication_instructions": "発熱時に服用。空腹時は避けてください。",
            "treatment_plan": "対症療法。安静と水分補給を心がける。",
            "follow_up": "3日後に再診。症状が悪化する場合は早めに受診。",
            "patient_explanation": "風邪の症状です。処方薬で症状を和らげながら、安静にしてください。"
        }
        
        return self.export_to_csv([sample_record])
    
    def validate_csv(self, csv_content: str) -> Dict[str, Any]:
        """
        CSVの形式を検証
        
        Args:
            csv_content: CSV形式の文字列
            
        Returns:
            検証結果の辞書 {"valid": bool, "errors": List[str], "warnings": List[str]}
        """
        errors = []
        warnings = []
        
        try:
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            # ヘッダーの確認
            if reader.fieldnames:
                missing_columns = set(self.CSV_COLUMNS) - set(reader.fieldnames)
                if missing_columns:
                    warnings.append(f"Missing columns: {', '.join(missing_columns)}")
                
                extra_columns = set(reader.fieldnames) - set(self.CSV_COLUMNS)
                if extra_columns:
                    warnings.append(f"Extra columns (will be ignored): {', '.join(extra_columns)}")
            else:
                errors.append("CSV has no header row")
            
            # データ行の確認
            row_count = 0
            for idx, row in enumerate(reader, start=2):  # 2行目から（ヘッダーが1行目）
                row_count += 1
                
                # 必須フィールドのチェック
                if not row.get("symptoms") and not row.get("diagnosis"):
                    warnings.append(f"Row {idx}: Both symptoms and diagnosis are empty")
                
                if not row.get("diagnosis"):
                    warnings.append(f"Row {idx}: Diagnosis is empty")
            
            if row_count == 0:
                warnings.append("CSV contains no data rows")
            
        except Exception as e:
            errors.append(f"CSV parsing error: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


def create_sample_csv() -> str:
    """テスト用のサンプルCSVを作成"""
    handler = CSVHandler()
    
    sample_records = [
        {
            "patient_id": "P001",
            "timestamp": "2025-10-01T10:00:00",
            "symptoms": "発熱、咳、鼻水",
            "diagnosis": "急性上気道炎",
            "diagnosis_details": "3日前から38.5度の発熱が続いている。",
            "medication": "カロナール 500mg 1日3回 3日分 食後",
            "medication_instructions": "発熱時に服用してください。",
            "treatment_plan": "対症療法で経過観察。",
            "follow_up": "3日後に再診。",
            "patient_explanation": "風邪の症状です。処方薬を服用して安静にしてください。"
        },
        {
            "patient_id": "P002",
            "timestamp": "2025-10-01T11:00:00",
            "symptoms": "腹痛、下痢",
            "diagnosis": "急性胃腸炎",
            "diagnosis_details": "昨夜から水様性下痢が続いている。",
            "medication": "ナウゼリン 10mg 1日3回 3日分 食前、ビオフェルミン 3錠 1日3回 7日分 食後",
            "medication_instructions": "脱水に注意し、水分補給を心がけてください。",
            "treatment_plan": "整腸剤と制吐剤で対症療法。",
            "follow_up": "症状が改善しない場合は再受診。",
            "patient_explanation": "急性胃腸炎です。水分補給をしっかり行い、消化の良い食事を摂ってください。"
        }
    ]
    
    return handler.export_to_csv(sample_records)

