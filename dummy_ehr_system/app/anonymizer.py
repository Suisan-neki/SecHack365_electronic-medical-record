"""
データ匿名化モジュール

医療データを段階的に匿名化し、プライバシーを保護する
"""

import json
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class BasicAnonymizer:
    """基本的な匿名化機能を提供するクラス"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.anonymization_levels = {
            'level1': '個人識別情報の削除',
            'level2': '仮名化',
            'level3': '統計的匿名化'
        }
    
    def anonymize_patient_data(self, patient: Dict[str, Any], level: str = 'level1') -> Dict[str, Any]:
        """
        患者データを匿名化する
        
        Args:
            patient: 患者データの辞書
            level: 匿名化レベル（'level1', 'level2', 'level3'）
            
        Returns:
            匿名化された患者データ
        """
        if level == 'level1':
            return self._anonymize_level1_patient(patient)
        elif level == 'level2':
            return self._anonymize_level2_patient(patient)
        elif level == 'level3':
            return self._anonymize_level3_patient(patient)
        else:
            raise ValueError(f"不明な匿名化レベル: {level}")
    
    def _anonymize_level1_patient(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """
        Level 1: 個人識別情報の削除
        
        - 名前を削除
        - 電話番号を削除
        - 詳細な住所を削除
        - 生年月日を年齢に変換
        """
        anonymized = {}
        
        # 患者IDは仮名IDに変換
        if 'patient_id' in patient:
            anonymized['anonymous_id'] = self._generate_pseudonym(patient['patient_id'])
        
        # 性別は保持
        if 'gender' in patient:
            anonymized['gender'] = patient['gender']
        
        # 生年月日を年齢に変換
        if 'birth_date' in patient:
            try:
                birth_date = datetime.strptime(patient['birth_date'], '%Y-%m-%d')
                age = (datetime.now() - birth_date).days // 365
                anonymized['age'] = age
            except:
                pass
        
        # 血液型は保持
        if 'blood_type' in patient:
            anonymized['blood_type'] = patient['blood_type']
        
        # アレルギー情報は保持
        if 'allergies' in patient:
            anonymized['allergies'] = patient['allergies']
        
        # 住所は都道府県レベルに
        if 'address' in patient:
            anonymized['prefecture'] = self._extract_prefecture(patient['address'])
        
        return anonymized
    
    def _anonymize_level2_patient(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """
        Level 2: 仮名化
        
        - Level 1の処理に加えて
        - 年齢を10歳刻みに
        - アレルギー情報を一般化
        """
        anonymized = self._anonymize_level1_patient(patient)
        
        # 年齢を10歳刻みに
        if 'age' in anonymized:
            age = anonymized['age']
            anonymized['age_group'] = f"{(age // 10) * 10}-{(age // 10) * 10 + 9}歳"
            del anonymized['age']
        
        # アレルギー情報を一般化
        if 'allergies' in anonymized and anonymized['allergies'] != 'なし':
            anonymized['has_allergies'] = True
            del anonymized['allergies']
        else:
            anonymized['has_allergies'] = False
            if 'allergies' in anonymized:
                del anonymized['allergies']
        
        return anonymized
    
    def _anonymize_level3_patient(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """
        Level 3: 統計的匿名化
        
        - Level 2の処理に加えて
        - 性別を削除（オプション）
        - 血液型を削除（オプション）
        - より広い地域情報に
        """
        anonymized = self._anonymize_level2_patient(patient)
        
        # 都道府県を地域に変換
        if 'prefecture' in anonymized:
            anonymized['region'] = self._prefecture_to_region(anonymized['prefecture'])
            del anonymized['prefecture']
        
        return anonymized
    
    def anonymize_medical_record(self, record: Dict[str, Any], level: str = 'level1') -> Dict[str, Any]:
        """
        医療記録を匿名化する
        
        Args:
            record: 医療記録の辞書
            level: 匿名化レベル（'level1', 'level2', 'level3'）
            
        Returns:
            匿名化された医療記録
        """
        if level == 'level1':
            return self._anonymize_level1_record(record)
        elif level == 'level2':
            return self._anonymize_level2_record(record)
        elif level == 'level3':
            return self._anonymize_level3_record(record)
        else:
            raise ValueError(f"不明な匿名化レベル: {level}")
    
    def _anonymize_level1_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Level 1: 個人識別情報の削除
        
        - 患者IDを仮名IDに変換
        - 医師名を削除
        - 記録IDを仮名IDに変換
        """
        anonymized = {}
        
        # 記録IDを仮名IDに変換
        if 'record_id' in record:
            anonymized['anonymous_record_id'] = self._generate_pseudonym(record['record_id'])
        
        # 患者IDを仮名IDに変換
        if 'patient_id' in record:
            anonymized['anonymous_patient_id'] = self._generate_pseudonym(record['patient_id'])
        
        # 日付を年月のみに
        if 'date' in record:
            try:
                if 'T' in record['date']:
                    date_obj = datetime.fromisoformat(record['date'].replace('Z', '+00:00'))
                else:
                    date_obj = datetime.strptime(record['date'], '%Y-%m-%d')
                anonymized['year_month'] = date_obj.strftime('%Y-%m')
            except:
                pass
        
        # 診断名は保持
        if 'diagnosis' in record:
            anonymized['diagnosis'] = record['diagnosis']
        
        # 治療内容は一般化
        if 'treatment' in record:
            anonymized['treatment_category'] = self._generalize_treatment(record['treatment'])
        
        # 診療科は保持
        if 'department' in record:
            anonymized['department'] = record['department']
        
        return anonymized
    
    def _anonymize_level2_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Level 2: 仮名化
        
        - Level 1の処理に加えて
        - 診断名を一般化
        - 日付を四半期に
        """
        anonymized = self._anonymize_level1_record(record)
        
        # 日付を四半期に
        if 'year_month' in anonymized:
            year, month = anonymized['year_month'].split('-')
            quarter = (int(month) - 1) // 3 + 1
            anonymized['year_quarter'] = f"{year}-Q{quarter}"
            del anonymized['year_month']
        
        # 診断名を疾患カテゴリに
        if 'diagnosis' in anonymized:
            anonymized['disease_category'] = self._categorize_diagnosis(anonymized['diagnosis'])
            del anonymized['diagnosis']
        
        return anonymized
    
    def _anonymize_level3_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Level 3: 統計的匿名化
        
        - Level 2の処理に加えて
        - 年のみに
        - より広いカテゴリに
        """
        anonymized = self._anonymize_level2_record(record)
        
        # 日付を年のみに
        if 'year_quarter' in anonymized:
            year = anonymized['year_quarter'].split('-')[0]
            anonymized['year'] = year
            del anonymized['year_quarter']
        
        return anonymized
    
    def _generate_pseudonym(self, original_id: str, salt: str = 'medical_record_salt') -> str:
        """
        IDから仮名を生成する
        
        Args:
            original_id: 元のID
            salt: ソルト文字列
            
        Returns:
            仮名ID
        """
        # ハッシュ化して仮名を生成
        hash_obj = hashlib.sha256(f"{original_id}{salt}".encode())
        return f"ANON_{hash_obj.hexdigest()[:12].upper()}"
    
    def _extract_prefecture(self, address: str) -> str:
        """
        住所から都道府県を抽出する
        
        Args:
            address: 住所文字列
            
        Returns:
            都道府県名
        """
        prefectures = [
            '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
            '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
            '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
            '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
            '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
            '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
            '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
        ]
        
        for pref in prefectures:
            if pref in address:
                return pref
        
        return '不明'
    
    def _prefecture_to_region(self, prefecture: str) -> str:
        """
        都道府県を地域に変換する
        
        Args:
            prefecture: 都道府県名
            
        Returns:
            地域名
        """
        regions = {
            '北海道': '北海道',
            '青森県': '東北', '岩手県': '東北', '宮城県': '東北', '秋田県': '東北', 
            '山形県': '東北', '福島県': '東北',
            '茨城県': '関東', '栃木県': '関東', '群馬県': '関東', '埼玉県': '関東',
            '千葉県': '関東', '東京都': '関東', '神奈川県': '関東',
            '新潟県': '中部', '富山県': '中部', '石川県': '中部', '福井県': '中部',
            '山梨県': '中部', '長野県': '中部', '岐阜県': '中部', '静岡県': '中部',
            '愛知県': '中部',
            '三重県': '近畿', '滋賀県': '近畿', '京都府': '近畿', '大阪府': '近畿',
            '兵庫県': '近畿', '奈良県': '近畿', '和歌山県': '近畿',
            '鳥取県': '中国', '島根県': '中国', '岡山県': '中国', '広島県': '中国',
            '山口県': '中国',
            '徳島県': '四国', '香川県': '四国', '愛媛県': '四国', '高知県': '四国',
            '福岡県': '九州', '佐賀県': '九州', '長崎県': '九州', '熊本県': '九州',
            '大分県': '九州', '宮崎県': '九州', '鹿児島県': '九州', '沖縄県': '九州'
        }
        
        return regions.get(prefecture, '不明')
    
    def _generalize_treatment(self, treatment: str) -> str:
        """
        治療内容を一般化する
        
        Args:
            treatment: 治療内容
            
        Returns:
            一般化された治療カテゴリ
        """
        if '手術' in treatment:
            return '外科的治療'
        elif any(drug in treatment for drug in ['薬', '錠', 'mg', '投与', '処方']):
            return '薬物療法'
        elif '理学療法' in treatment or 'リハビリ' in treatment:
            return '理学療法'
        elif '経過観察' in treatment:
            return '経過観察'
        else:
            return 'その他の治療'
    
    def _categorize_diagnosis(self, diagnosis: str) -> str:
        """
        診断名を疾患カテゴリに分類する
        
        Args:
            diagnosis: 診断名
            
        Returns:
            疾患カテゴリ
        """
        categories = {
            '感染症': ['風邪', 'インフルエンザ', '肺炎', '感染'],
            '循環器疾患': ['高血圧', '心筋梗塞', '不整脈', '心不全'],
            '代謝性疾患': ['糖尿病', '高脂血症', 'メタボリック'],
            '呼吸器疾患': ['喘息', '気管支炎', 'COPD'],
            '消化器疾患': ['胃炎', '腸炎', '肝炎', '胃潰瘍'],
            '神経疾患': ['頭痛', '片頭痛', 'めまい', '脳梗塞'],
            '整形外科疾患': ['骨折', '捻挫', '関節炎', '腰痛']
        }
        
        for category, keywords in categories.items():
            if any(keyword in diagnosis for keyword in keywords):
                return category
        
        return 'その他の疾患'
    
    def export_anonymized_dataset(self, level: str = 'level1', output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        匿名化されたデータセットをエクスポートする
        
        Args:
            level: 匿名化レベル
            output_file: 出力ファイル名（Noneの場合は辞書を返すのみ）
            
        Returns:
            匿名化されたデータセット
        """
        anonymized_dataset = {
            'metadata': {
                'anonymization_level': level,
                'description': self.anonymization_levels.get(level, '不明'),
                'exported_at': datetime.now().isoformat(),
                'total_patients': 0,
                'total_records': 0
            },
            'patients': [],
            'medical_records': []
        }
        
        # 患者データの匿名化
        patients_file = self.data_dir / 'patients.json'
        if patients_file.exists():
            with open(patients_file, 'r', encoding='utf-8') as f:
                patients = json.load(f)
            
            for patient in patients:
                anonymized_patient = self.anonymize_patient_data(patient, level)
                anonymized_dataset['patients'].append(anonymized_patient)
            
            anonymized_dataset['metadata']['total_patients'] = len(patients)
        
        # 医療記録の匿名化
        records_file = self.data_dir / 'medical_records.json'
        if records_file.exists():
            with open(records_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            for record in records:
                anonymized_record = self.anonymize_medical_record(record, level)
                anonymized_dataset['medical_records'].append(anonymized_record)
            
            anonymized_dataset['metadata']['total_records'] = len(records)
        
        # ファイルに出力
        if output_file:
            output_path = self.data_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(anonymized_dataset, f, indent=2, ensure_ascii=False)
            logger.info(f"匿名化されたデータセットを {output_path} に出力しました")
        
        return anonymized_dataset
