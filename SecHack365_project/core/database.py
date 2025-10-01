"""
データベース操作モジュール
新しいシステムフロー用のSQLiteデータベース管理
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

class DatabaseManager:
    """医療記録データベース管理クラス"""
    
    def __init__(self, db_path: str = "medical_records.db"):
        """
        データベースマネージャーを初期化
        
        Args:
            db_path (str): データベースファイルのパス
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベースとテーブルを初期化"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 医療記録テーブル
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS medical_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        patient_id TEXT NOT NULL,
                        doctor_id TEXT NOT NULL,
                        diagnosis TEXT,
                        diagnosis_details TEXT,
                        medication TEXT,
                        medication_instructions TEXT,
                        treatment_plan TEXT,
                        follow_up TEXT,
                        patient_explanation TEXT,
                        risk_benefit_explanation TEXT,
                        doctor_notes TEXT,
                        status TEXT DEFAULT 'draft',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 患者同意テーブル
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS patient_consents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        patient_id TEXT NOT NULL,
                        consent_status TEXT NOT NULL,
                        consent_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        patient_questions TEXT,
                        consent_details TEXT,
                        FOREIGN KEY (session_id) REFERENCES medical_records (session_id)
                    )
                ''')
                
                # 電子カルテ転送ログテーブル
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ehr_transfer_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        ehr_system_id TEXT NOT NULL,
                        transfer_status TEXT NOT NULL,
                        transfer_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        error_message TEXT,
                        transfer_data TEXT,
                        FOREIGN KEY (session_id) REFERENCES medical_records (session_id)
                    )
                ''')
                
                # 患者質問テーブル
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS patient_questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        patient_id TEXT NOT NULL,
                        question_text TEXT NOT NULL,
                        is_urgent BOOLEAN DEFAULT FALSE,
                        share_with_family BOOLEAN DEFAULT FALSE,
                        question_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        doctor_response TEXT,
                        response_timestamp TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES medical_records (session_id)
                    )
                ''')
                
                # 症状タグテーブル
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS symptom_tags (
                        tag_id TEXT PRIMARY KEY,
                        category TEXT NOT NULL,
                        tag_name TEXT NOT NULL,
                        description TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 医療記録タグ関連テーブル
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS medical_record_tags (
                        record_tag_id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        tag_id TEXT NOT NULL,
                        tag_value TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES medical_records (session_id),
                        FOREIGN KEY (tag_id) REFERENCES symptom_tags (tag_id)
                    )
                ''')
                
                conn.commit()
                print(f"[DATABASE] データベース初期化完了: {self.db_path}")
                
        except Exception as e:
            print(f"[ERROR] データベース初期化エラー: {e}")
            raise
    
    def _get_connection(self):
        """データベース接続を取得"""
        return sqlite3.connect(self.db_path)
    
    def create_medical_record(self, patient_id: str, doctor_id: str, **kwargs) -> str:
        """
        新しい医療記録を作成
        
        Args:
            patient_id (str): 患者ID
            doctor_id (str): 医師ID
            **kwargs: その他の医療記録データ
            
        Returns:
            str: セッションID
        """
        session_id = str(uuid.uuid4())
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO medical_records (
                        session_id, patient_id, doctor_id, diagnosis, diagnosis_details,
                        medication, medication_instructions, treatment_plan, follow_up,
                        patient_explanation, risk_benefit_explanation, doctor_notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, patient_id, doctor_id,
                    kwargs.get('diagnosis'),
                    kwargs.get('diagnosis_details'),
                    kwargs.get('medication'),
                    kwargs.get('medication_instructions'),
                    kwargs.get('treatment_plan'),
                    kwargs.get('follow_up'),
                    kwargs.get('patient_explanation'),
                    kwargs.get('risk_benefit_explanation'),
                    kwargs.get('doctor_notes')
                ))
                
                conn.commit()
                print(f"[DATABASE] 医療記録作成完了: {session_id}")
                return session_id
                
        except Exception as e:
            print(f"[ERROR] 医療記録作成エラー: {e}")
            raise
    
    def update_medical_record(self, session_id: str, **kwargs) -> bool:
        """
        医療記録を更新
        
        Args:
            session_id (str): セッションID
            **kwargs: 更新するデータ
            
        Returns:
            bool: 更新成功の可否
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 更新可能なフィールドを動的に構築
                update_fields = []
                values = []
                
                for key, value in kwargs.items():
                    if key in ['diagnosis', 'diagnosis_details', 'medication', 
                             'medication_instructions', 'treatment_plan', 'follow_up',
                             'patient_explanation', 'risk_benefit_explanation', 'doctor_notes', 'status']:
                        update_fields.append(f"{key} = ?")
                        values.append(value)
                
                if not update_fields:
                    return False
                
                values.append(session_id)
                query = f"UPDATE medical_records SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE session_id = ?"
                
                cursor.execute(query, values)
                conn.commit()
                
                if cursor.rowcount > 0:
                    print(f"[DATABASE] 医療記録更新完了: {session_id}")
                    return True
                else:
                    print(f"[WARNING] 更新対象の医療記録が見つかりません: {session_id}")
                    return False
                    
        except Exception as e:
            print(f"[ERROR] 医療記録更新エラー: {e}")
            return False
    
    def get_medical_record(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        医療記録を取得
        
        Args:
            session_id (str): セッションID
            
        Returns:
            Optional[Dict[str, Any]]: 医療記録データ
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM medical_records WHERE session_id = ?
                ''', (session_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                else:
                    return None
                    
        except Exception as e:
            print(f"[ERROR] 医療記録取得エラー: {e}")
            return None
    
    def record_patient_consent(self, session_id: str, patient_id: str, 
                             consent_status: str, **kwargs) -> bool:
        """
        患者同意を記録
        
        Args:
            session_id (str): セッションID
            patient_id (str): 患者ID
            consent_status (str): 同意状況 ('consented', 'declined', 'pending')
            **kwargs: その他の同意データ
            
        Returns:
            bool: 記録成功の可否
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO patient_consents (
                        session_id, patient_id, consent_status, patient_questions, consent_details
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    session_id, patient_id, consent_status,
                    kwargs.get('patient_questions'),
                    kwargs.get('consent_details')
                ))
                
                conn.commit()
                print(f"[DATABASE] 患者同意記録完了: {session_id} - {consent_status}")
                return True
                
        except Exception as e:
            print(f"[ERROR] 患者同意記録エラー: {e}")
            return False
    
    def get_patient_consent(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        患者同意情報を取得
        
        Args:
            session_id (str): セッションID
            
        Returns:
            Optional[Dict[str, Any]]: 同意情報
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM patient_consents WHERE session_id = ? ORDER BY consent_timestamp DESC LIMIT 1
                ''', (session_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                else:
                    return None
                    
        except Exception as e:
            print(f"[ERROR] 患者同意取得エラー: {e}")
            return None
    
    def record_ehr_transfer(self, session_id: str, ehr_system_id: str, 
                          transfer_status: str, **kwargs) -> bool:
        """
        電子カルテ転送ログを記録
        
        Args:
            session_id (str): セッションID
            ehr_system_id (str): 電子カルテシステムID
            transfer_status (str): 転送状況 ('success', 'failed', 'pending')
            **kwargs: その他の転送データ
            
        Returns:
            bool: 記録成功の可否
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO ehr_transfer_logs (
                        session_id, ehr_system_id, transfer_status, error_message, transfer_data
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    session_id, ehr_system_id, transfer_status,
                    kwargs.get('error_message'),
                    kwargs.get('transfer_data')
                ))
                
                conn.commit()
                print(f"[DATABASE] 電子カルテ転送ログ記録完了: {session_id} - {transfer_status}")
                return True
                
        except Exception as e:
            print(f"[ERROR] 電子カルテ転送ログ記録エラー: {e}")
            return False
    
    def record_patient_question(self, session_id: str, patient_id: str, 
                              question_text: str, **kwargs) -> bool:
        """
        患者質問を記録
        
        Args:
            session_id (str): セッションID
            patient_id (str): 患者ID
            question_text (str): 質問内容
            **kwargs: その他の質問データ
            
        Returns:
            bool: 記録成功の可否
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO patient_questions (
                        session_id, patient_id, question_text, is_urgent, share_with_family
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    session_id, patient_id, question_text,
                    kwargs.get('is_urgent', False),
                    kwargs.get('share_with_family', False)
                ))
                
                conn.commit()
                print(f"[DATABASE] 患者質問記録完了: {session_id}")
                return True
                
        except Exception as e:
            print(f"[ERROR] 患者質問記録エラー: {e}")
            return False
    
    def get_patient_questions(self, session_id: str) -> List[Dict[str, Any]]:
        """
        患者質問一覧を取得
        
        Args:
            session_id (str): セッションID
            
        Returns:
            List[Dict[str, Any]]: 質問一覧
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM patient_questions WHERE session_id = ? ORDER BY question_timestamp DESC
                ''', (session_id,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"[ERROR] 患者質問取得エラー: {e}")
            return []
    
    def get_medical_records_by_patient(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        患者の医療記録一覧を取得
        
        Args:
            patient_id (str): 患者ID
            
        Returns:
            List[Dict[str, Any]]: 医療記録一覧
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM medical_records WHERE patient_id = ? ORDER BY created_at DESC
                ''', (patient_id,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"[ERROR] 患者医療記録取得エラー: {e}")
            return []
    
    def get_medical_records_by_doctor(self, doctor_id: str) -> List[Dict[str, Any]]:
        """
        医師の医療記録一覧を取得
        
        Args:
            doctor_id (str): 医師ID
            
        Returns:
            List[Dict[str, Any]]: 医療記録一覧
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM medical_records WHERE doctor_id = ? ORDER BY created_at DESC
                ''', (doctor_id,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"[ERROR] 医師医療記録取得エラー: {e}")
            return []
    
    def get_transfer_logs(self, session_id: str) -> List[Dict[str, Any]]:
        """
        電子カルテ転送ログを取得
        
        Args:
            session_id (str): セッションID
            
        Returns:
            List[Dict[str, Any]]: 転送ログ一覧
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM ehr_transfer_logs WHERE session_id = ? ORDER BY transfer_timestamp DESC
                ''', (session_id,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"[ERROR] 転送ログ取得エラー: {e}")
            return []
    
    def get_symptom_tags(self, category=None):
        """症状タグを取得"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("SELECT * FROM symptom_tags WHERE category = ? AND is_active = 1 ORDER BY tag_name", (category,))
            else:
                cursor.execute("SELECT * FROM symptom_tags WHERE is_active = 1 ORDER BY category, tag_name")
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def add_symptom_tag(self, category, tag_name, description=None):
        """新しい症状タグを追加"""
        tag_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO symptom_tags (tag_id, category, tag_name, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (tag_id, category, tag_name, description, now, now))
            conn.commit()
        return tag_id

    def add_medical_record_tag(self, session_id, tag_id, tag_value=None):
        """医療記録にタグを追加"""
        record_tag_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO medical_record_tags (record_tag_id, session_id, tag_id, tag_value, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (record_tag_id, session_id, tag_id, tag_value, now))
            conn.commit()
        return record_tag_id

    def get_medical_record_tags(self, session_id):
        """医療記録のタグを取得"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT mrt.*, st.category, st.tag_name, st.description
                FROM medical_record_tags mrt
                JOIN symptom_tags st ON mrt.tag_id = st.tag_id
                WHERE mrt.session_id = ?
                ORDER BY st.category, st.tag_name
            """, (session_id,))
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def initialize_default_tags(self):
        """デフォルトの症状タグを初期化"""
        default_tags = [
            # 症状カテゴリ - 風邪・呼吸器系
            ("症状-風邪", "発熱", "発熱"),
            ("症状-風邪", "悪寒", "悪寒"),
            ("症状-風邪", "咳", "咳"),
            ("症状-風邪", "痰", "痰"),
            ("症状-風邪", "鼻水", "鼻水"),
            ("症状-風邪", "鼻づまり", "鼻づまり"),
            ("症状-風邪", "のどの痛み", "咽頭痛"),
            ("症状-風邪", "くしゃみ", "くしゃみ"),
            ("症状-風邪", "声がれ", "嗄声"),
            ("症状-風邪", "息苦しさ", "呼吸困難"),
            ("症状-風邪", "喘鳴", "喘鳴"),
            
            # 症状カテゴリ - 痛み系
            ("症状-痛み", "頭痛", "頭痛"),
            ("症状-痛み", "腹痛", "腹痛"),
            ("症状-痛み", "胸痛", "胸痛"),
            ("症状-痛み", "背部痛", "背部痛"),
            ("症状-痛み", "腰痛", "腰痛"),
            ("症状-痛み", "関節痛", "関節痛"),
            ("症状-痛み", "筋肉痛", "筋肉痛"),
            ("症状-痛み", "歯痛", "歯痛"),
            
            # 症状カテゴリ - 消化器系
            ("症状-消化器", "吐き気", "悪心"),
            ("症状-消化器", "嘔吐", "嘔吐"),
            ("症状-消化器", "下痢", "下痢"),
            ("症状-消化器", "便秘", "便秘"),
            ("症状-消化器", "腹部膨満感", "腹部膨満"),
            ("症状-消化器", "胸やけ", "胸やけ"),
            ("症状-消化器", "げっぷ", "げっぷ"),
            ("症状-消化器", "食欲不振", "食欲不振"),
            ("症状-消化器", "血便", "血便"),
            
            # 症状カテゴリ - 全身症状
            ("症状-全身", "だるさ", "倦怠感"),
            ("症状-全身", "疲労感", "疲労感"),
            ("症状-全身", "めまい", "めまい"),
            ("症状-全身", "ふらつき", "ふらつき"),
            ("症状-全身", "体重減少", "体重減少"),
            ("症状-全身", "むくみ", "浮腫"),
            ("症状-全身", "発汗", "発汗"),
            ("症状-全身", "寝汗", "寝汗"),
            
            # 症状カテゴリ - 循環器系
            ("症状-循環器", "動悸", "動悸"),
            ("症状-循環器", "息切れ", "息切れ"),
            ("症状-循環器", "不整脈感", "不整脈感"),
            
            # 症状カテゴリ - その他
            ("症状-その他", "不眠", "不眠"),
            ("症状-その他", "しびれ", "しびれ"),
            ("症状-その他", "かゆみ", "かゆみ"),
            ("症状-その他", "発疹", "発疹"),
            ("症状-その他", "頻尿", "頻尿"),
            ("症状-その他", "排尿痛", "排尿痛"),
            
            # 診断カテゴリ（内科の主要診断）
            ("診断", "急性上気道炎", "風邪"),
            ("診断", "インフルエンザ", "インフルエンザ"),
            ("診断", "急性胃腸炎", "急性胃腸炎"),
            ("診断", "感染性胃腸炎", "感染性胃腸炎"),
            ("診断", "高血圧症", "高血圧"),
            ("診断", "2型糖尿病", "2型糖尿病"),
            ("診断", "脂質異常症", "脂質異常症"),
            ("診断", "逆流性食道炎", "逆流性食道炎"),
            ("診断", "便秘症", "便秘症"),
            ("診断", "過敏性腸症候群", "過敏性腸症候群"),
            ("診断", "気管支炎", "気管支炎"),
            ("診断", "気管支喘息", "気管支喘息"),
            ("診断", "アレルギー性鼻炎", "アレルギー性鼻炎"),
            ("診断", "花粉症", "花粉症"),
            ("診断", "片頭痛", "片頭痛"),
            ("診断", "緊張型頭痛", "緊張型頭痛"),
            ("診断", "不眠症", "不眠症"),
            ("診断", "貧血", "貧血"),
            ("診断", "尿路感染症", "尿路感染症"),
            ("診断", "膀胱炎", "膀胱炎"),
            
            # 薬剤名（内科でよく使われる薬剤 60個）
            # 解熱鎮痛剤
            ("薬剤名", "カロナール", "解熱鎮痛剤"),
            ("薬剤名", "ロキソニン", "解熱鎮痛剤"),
            ("薬剤名", "ボルタレン", "NSAIDs"),
            ("薬剤名", "セレコックス", "NSAIDs"),
            
            # 咳・痰・喘息
            ("薬剤名", "カルボシステイン", "去痰剤"),
            ("薬剤名", "ムコダイン", "去痰剤"),
            ("薬剤名", "ムコソルバン", "去痰剤"),
            ("薬剤名", "メジコン", "鎮咳剤"),
            ("薬剤名", "アスベリン", "鎮咳剤"),
            ("薬剤名", "フスコデ", "鎮咳剤"),
            ("薬剤名", "メプチン", "気管支拡張剤"),
            ("薬剤名", "テオドール", "気管支拡張剤"),
            ("薬剤名", "キュバール", "吸入ステロイド"),
            ("薬剤名", "フルタイド", "吸入ステロイド"),
            ("薬剤名", "シムビコート", "吸入薬"),
            ("薬剤名", "アドエア", "吸入薬"),
            ("薬剤名", "スピリーバ", "吸入薬"),
            ("薬剤名", "ホクナリンテープ", "貼付薬・気管支拡張"),
            
            # 感冒薬・抗ウイルス
            ("薬剤名", "PL配合顆粒", "総合感冒薬"),
            ("薬剤名", "タミフル", "抗インフルエンザ薬"),
            ("薬剤名", "イナビル", "抗インフルエンザ薬"),
            ("薬剤名", "ゾフルーザ", "抗インフルエンザ薬"),
            
            # 消化器系
            ("薬剤名", "ガスター", "H2ブロッカー"),
            ("薬剤名", "タケキャブ", "PPI"),
            ("薬剤名", "ネキシウム", "PPI"),
            ("薬剤名", "ナウゼリン", "制吐剤"),
            ("薬剤名", "プリンペラン", "制吐剤"),
            ("薬剤名", "ビオフェルミン", "整腸剤"),
            ("薬剤名", "ミヤBM", "整腸剤"),
            ("薬剤名", "ロペミン", "止瀉剤"),
            ("薬剤名", "マグミット", "緩下剤"),
            ("薬剤名", "酸化マグネシウム", "緩下剤"),
            ("薬剤名", "ラキソベロン", "緩下剤"),
            
            # 抗アレルギー薬
            ("薬剤名", "アレロック", "抗アレルギー薬"),
            ("薬剤名", "アレジオン", "抗アレルギー薬"),
            ("薬剤名", "ザイザル", "抗アレルギー薬"),
            ("薬剤名", "アレグラ", "抗アレルギー薬"),
            ("薬剤名", "クラリチン", "抗アレルギー薬"),
            ("薬剤名", "ビラノア", "抗アレルギー薬"),
            
            # 抗生物質
            ("薬剤名", "クラリス", "マクロライド系"),
            ("薬剤名", "クラリスロマイシン", "マクロライド系"),
            ("薬剤名", "ジスロマック", "マクロライド系"),
            ("薬剤名", "フロモックス", "セフェム系"),
            ("薬剤名", "メイアクト", "セフェム系"),
            ("薬剤名", "サワシリン", "ペニシリン系"),
            
            # 循環器系
            ("薬剤名", "アムロジン", "Ca拮抗薬"),
            ("薬剤名", "ノルバスク", "Ca拮抗薬"),
            ("薬剤名", "ブロプレス", "ARB"),
            ("薬剤名", "ディオバン", "ARB"),
            ("薬剤名", "ニューロタン", "貼付薬・降圧"),
            
            # 糖尿病
            ("薬剤名", "メトグルコ", "ビグアナイド薬"),
            ("薬剤名", "ジャヌビア", "DPP-4阻害薬"),
            ("薬剤名", "トラゼンタ", "DPP-4阻害薬"),
            
            # 脂質異常症
            ("薬剤名", "リピトール", "スタチン"),
            ("薬剤名", "クレストール", "スタチン"),
            
            # 漢方薬
            ("薬剤名", "葛根湯", "漢方"),
            ("薬剤名", "麻黄湯", "漢方"),
            ("薬剤名", "小青竜湯", "漢方"),
            ("薬剤名", "補中益気湯", "漢方"),
            ("薬剤名", "六君子湯", "漢方"),
            ("薬剤名", "大建中湯", "漢方"),
            
            # 用量
            ("用量", "5mg", "用量"),
            ("用量", "10mg", "用量"),
            ("用量", "20mg", "用量"),
            ("用量", "25mg", "用量"),
            ("用量", "50mg", "用量"),
            ("用量", "75mg", "用量"),
            ("用量", "100mg", "用量"),
            ("用量", "200mg", "用量"),
            ("用量", "250mg", "用量"),
            ("用量", "500mg", "用量"),
            
            # 頻度
            ("頻度", "1日1回", "頻度"),
            ("頻度", "1日2回", "頻度"),
            ("頻度", "1日3回", "頻度"),
            ("頻度", "1日4回", "頻度"),
            ("頻度", "1日5回", "頻度"),
            ("頻度", "1日6回", "頻度"),
            ("頻度", "1週1回", "頻度"),
            ("頻度", "1週2回", "頻度"),
            ("頻度", "1ヶ月1回", "頻度"),
            ("頻度", "頓服", "頻度"),
            
            # 日数
            ("日数", "1日分", "日数"),
            ("日数", "2日分", "日数"),
            ("日数", "3日分", "日数"),
            ("日数", "4日分", "日数"),
            ("日数", "5日分", "日数"),
            ("日数", "7日分", "日数"),
            ("日数", "10日分", "日数"),
            ("日数", "14日分", "日数"),
            ("日数", "21日分", "日数"),
            ("日数", "30日分", "日数"),
            
            # 服薬タイミング
            ("服薬タイミング", "食前", "服薬タイミング"),
            ("服薬タイミング", "食後", "服薬タイミング"),
            ("服薬タイミング", "食間", "服薬タイミング"),
            ("服薬タイミング", "就寝前", "服薬タイミング"),
            ("服薬タイミング", "起床時", "服薬タイミング"),
            ("服薬タイミング", "頓服", "服薬タイミング"),
            ("服薬タイミング", "症状時", "服薬タイミング"),
            ("服薬タイミング", "朝食前", "服薬タイミング"),
            ("服薬タイミング", "朝食後", "服薬タイミング"),
            ("服薬タイミング", "夕食後", "服薬タイミング"),
        ]
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 既存のタグを削除して新しく初期化
            cursor.execute("DELETE FROM symptom_tags")
            cursor.execute("DELETE FROM medical_record_tags")
            
            for category, tag_name, description in default_tags:
                tag_id = str(uuid.uuid4())
                now = datetime.now().isoformat()
                cursor.execute("""
                    INSERT INTO symptom_tags (tag_id, category, tag_name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (tag_id, category, tag_name, description, now, now))
            conn.commit()
            print(f"[DATABASE] デフォルト症状タグを初期化しました: {len(default_tags)}個")

    def close(self):
        """データベース接続を閉じる"""
        # SQLiteは自動的に接続が閉じられるため、特に処理は不要
        pass

# グローバルデータベースマネージャーインスタンス
db_manager = DatabaseManager()
