"""
データ品質管理モジュール

医療記録の標準化、検証、整合性チェックを行う
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataQualityManager:
    """データ品質を管理するクラス"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.validation_rules = self._load_validation_rules()
        self.quality_metrics = {
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'warnings': 0,
            'errors': []
        }
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """検証ルールを読み込む"""
        return {
            'patient': {
                'required_fields': ['patient_id', 'name', 'birth_date', 'gender'],
                'optional_fields': ['name_kana', 'phone', 'address', 'allergies', 'blood_type'],
                'field_types': {
                    'patient_id': str,
                    'name': str,
                    'birth_date': str,
                    'gender': str
                },
                'field_patterns': {
                    'patient_id': r'^P\d{3,}$',
                    'birth_date': r'^\d{4}-\d{2}-\d{2}$',
                    'gender': r'^(男性|女性|その他)$'
                }
            },
            'medical_record': {
                'required_fields': ['record_id', 'patient_id', 'date', 'diagnosis'],
                'optional_fields': ['treatment', 'notes', 'doctor', 'department'],
                'field_types': {
                    'record_id': str,
                    'patient_id': str,
                    'date': str,
                    'diagnosis': str
                },
                'field_patterns': {
                    'record_id': r'^REC\d{3,}$',
                    'patient_id': r'^P\d{3,}$',
                    'date': r'^\d{4}-\d{2}-\d{2}'
                }
            }
        }
    
    def validate_patient_data(self, patient: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        患者データを検証する
        
        Args:
            patient: 患者データの辞書
            
        Returns:
            (is_valid, errors): 検証結果とエラーメッセージのリスト
        """
        errors = []
        rules = self.validation_rules['patient']
        
        # 必須フィールドのチェック
        for field in rules['required_fields']:
            if field not in patient or not patient[field]:
                errors.append(f"必須フィールド '{field}' が欠落しています")
        
        # フィールド型のチェック
        for field, expected_type in rules['field_types'].items():
            if field in patient and not isinstance(patient[field], expected_type):
                errors.append(f"フィールド '{field}' の型が正しくありません（期待: {expected_type.__name__}）")
        
        # フィールドパターンのチェック
        for field, pattern in rules['field_patterns'].items():
            if field in patient and patient[field]:
                if not re.match(pattern, str(patient[field])):
                    errors.append(f"フィールド '{field}' のフォーマットが正しくありません（パターン: {pattern}）")
        
        # 生年月日の妥当性チェック
        if 'birth_date' in patient:
            try:
                birth_date = datetime.strptime(patient['birth_date'], '%Y-%m-%d')
                if birth_date > datetime.now():
                    errors.append("生年月日が未来の日付です")
                if birth_date.year < 1900:
                    errors.append("生年月日が1900年以前です")
            except ValueError:
                errors.append("生年月日の形式が正しくありません")
        
        return len(errors) == 0, errors
    
    def validate_medical_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        医療記録を検証する
        
        Args:
            record: 医療記録の辞書
            
        Returns:
            (is_valid, errors): 検証結果とエラーメッセージのリスト
        """
        errors = []
        rules = self.validation_rules['medical_record']
        
        # 必須フィールドのチェック
        for field in rules['required_fields']:
            if field not in record or not record[field]:
                errors.append(f"必須フィールド '{field}' が欠落しています")
        
        # フィールド型のチェック
        for field, expected_type in rules['field_types'].items():
            if field in record and not isinstance(record[field], expected_type):
                errors.append(f"フィールド '{field}' の型が正しくありません（期待: {expected_type.__name__}）")
        
        # フィールドパターンのチェック
        for field, pattern in rules['field_patterns'].items():
            if field in record and record[field]:
                if not re.match(pattern, str(record[field])):
                    errors.append(f"フィールド '{field}' のフォーマットが正しくありません（パターン: {pattern}）")
        
        # 日付の妥当性チェック
        if 'date' in record:
            try:
                record_date_str = record['date'].split('T')[0] if 'T' in record['date'] else record['date']
                record_date = datetime.strptime(record_date_str, '%Y-%m-%d')
                if record_date > datetime.now():
                    errors.append("記録日が未来の日付です")
            except ValueError:
                errors.append("記録日の形式が正しくありません")
        
        # 診断内容の長さチェック
        if 'diagnosis' in record and len(record['diagnosis']) < 2:
            errors.append("診断内容が短すぎます")
        
        return len(errors) == 0, errors
    
    def standardize_patient_data(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """
        患者データを標準化する
        
        Args:
            patient: 患者データの辞書
            
        Returns:
            標準化された患者データ
        """
        standardized = patient.copy()
        
        # 性別の標準化
        if 'gender' in standardized:
            gender_map = {
                '男': '男性',
                'male': '男性',
                'Male': '男性',
                'M': '男性',
                '女': '女性',
                'female': '女性',
                'Female': '女性',
                'F': '女性'
            }
            standardized['gender'] = gender_map.get(standardized['gender'], standardized['gender'])
        
        # 電話番号の標準化
        if 'phone' in standardized and standardized['phone']:
            phone = re.sub(r'[^\d]', '', standardized['phone'])
            if len(phone) == 11:
                standardized['phone'] = f"{phone[0:3]}-{phone[3:7]}-{phone[7:11]}"
            elif len(phone) == 10:
                standardized['phone'] = f"{phone[0:3]}-{phone[3:6]}-{phone[6:10]}"
        
        # 名前の空白削除
        if 'name' in standardized:
            standardized['name'] = standardized['name'].strip()
        
        return standardized
    
    def standardize_medical_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        医療記録を標準化する
        
        Args:
            record: 医療記録の辞書
            
        Returns:
            標準化された医療記録
        """
        standardized = record.copy()
        
        # 日付の標準化
        if 'date' in standardized:
            try:
                if 'T' in standardized['date']:
                    date_obj = datetime.fromisoformat(standardized['date'].replace('Z', '+00:00'))
                else:
                    date_obj = datetime.strptime(standardized['date'], '%Y-%m-%d')
                standardized['date'] = date_obj.isoformat()
            except:
                pass
        
        # 診断名の標準化（全角スペースを半角に）
        if 'diagnosis' in standardized:
            standardized['diagnosis'] = standardized['diagnosis'].replace('　', ' ').strip()
        
        # 治療内容の標準化
        if 'treatment' in standardized:
            standardized['treatment'] = standardized['treatment'].replace('　', ' ').strip()
        
        return standardized
    
    def check_data_integrity(self) -> Dict[str, Any]:
        """
        データ全体の整合性をチェックする
        
        Returns:
            整合性チェックの結果
        """
        integrity_report = {
            'timestamp': datetime.now().isoformat(),
            'patients': {'total': 0, 'valid': 0, 'invalid': 0, 'errors': []},
            'medical_records': {'total': 0, 'valid': 0, 'invalid': 0, 'errors': []},
            'orphaned_records': [],
            'missing_patients': []
        }
        
        # 患者データの読み込みと検証
        patients_file = self.data_dir / 'patients.json'
        if patients_file.exists():
            with open(patients_file, 'r', encoding='utf-8') as f:
                patients = json.load(f)
            
            patient_ids = set()
            for patient in patients:
                integrity_report['patients']['total'] += 1
                is_valid, errors = self.validate_patient_data(patient)
                
                if is_valid:
                    integrity_report['patients']['valid'] += 1
                    patient_ids.add(patient.get('patient_id'))
                else:
                    integrity_report['patients']['invalid'] += 1
                    integrity_report['patients']['errors'].append({
                        'patient_id': patient.get('patient_id', 'UNKNOWN'),
                        'errors': errors
                    })
        else:
            integrity_report['patients']['errors'].append('患者データファイルが見つかりません')
        
        # 医療記録の読み込みと検証
        records_file = self.data_dir / 'medical_records.json'
        if records_file.exists():
            with open(records_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            for record in records:
                integrity_report['medical_records']['total'] += 1
                is_valid, errors = self.validate_medical_record(record)
                
                if is_valid:
                    integrity_report['medical_records']['valid'] += 1
                    
                    # 孤立した記録のチェック
                    if record.get('patient_id') not in patient_ids:
                        integrity_report['orphaned_records'].append({
                            'record_id': record.get('record_id'),
                            'patient_id': record.get('patient_id')
                        })
                else:
                    integrity_report['medical_records']['invalid'] += 1
                    integrity_report['medical_records']['errors'].append({
                        'record_id': record.get('record_id', 'UNKNOWN'),
                        'errors': errors
                    })
        else:
            integrity_report['medical_records']['errors'].append('医療記録ファイルが見つかりません')
        
        return integrity_report
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """
        データ品質のメトリクスを取得する
        
        Returns:
            品質メトリクスの辞書
        """
        integrity_report = self.check_data_integrity()
        
        # 品質スコアの計算
        total_patients = integrity_report['patients']['total']
        valid_patients = integrity_report['patients']['valid']
        patient_quality_score = (valid_patients / total_patients * 100) if total_patients > 0 else 0
        
        total_records = integrity_report['medical_records']['total']
        valid_records = integrity_report['medical_records']['valid']
        record_quality_score = (valid_records / total_records * 100) if total_records > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_quality_score': (patient_quality_score + record_quality_score) / 2,
            'patient_quality_score': patient_quality_score,
            'record_quality_score': record_quality_score,
            'total_patients': total_patients,
            'valid_patients': valid_patients,
            'invalid_patients': total_patients - valid_patients,
            'total_records': total_records,
            'valid_records': valid_records,
            'invalid_records': total_records - valid_records,
            'orphaned_records': len(integrity_report['orphaned_records']),
            'issues': {
                'patient_errors': len(integrity_report['patients']['errors']),
                'record_errors': len(integrity_report['medical_records']['errors']),
                'orphaned_records': len(integrity_report['orphaned_records'])
            }
        }
