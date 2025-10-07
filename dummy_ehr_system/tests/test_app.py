"""
メインアプリケーションのテスト

Flask アプリケーションの機能をテストする
"""

import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.app import app, load_patients, load_medical_records, save_patients, save_medical_records

class TestFlaskApp(unittest.TestCase):
    """Flaskアプリケーションのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # テスト用の一時ディレクトリを作成
        self.test_dir = tempfile.mkdtemp()
        
        # テスト用のデータファイルを作成
        self.create_test_data()
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        # 一時ディレクトリを削除
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_data(self):
        """テスト用のデータを作成"""
        test_patients = [
            {
                "patient_id": "TEST001",
                "name": "テスト患者1",
                "name_kana": "テストカンジャ1",
                "birth_date": "1990-01-01",
                "gender": "男性"
            },
            {
                "patient_id": "TEST002", 
                "name": "テスト患者2",
                "name_kana": "テストカンジャ2",
                "birth_date": "1985-05-15",
                "gender": "女性"
            }
        ]
        
        test_records = [
            {
                "patient_id": "TEST001",
                "date": "2024-01-15",
                "diagnosis": "風邪",
                "symptoms": "発熱,咳",
                "treatment": "解熱剤,咳止め"
            },
            {
                "patient_id": "TEST002",
                "date": "2024-01-20",
                "diagnosis": "頭痛",
                "symptoms": "頭痛",
                "treatment": "鎮痛剤"
            }
        ]
        
        # データファイルを保存
        patients_file = os.path.join(self.test_dir, "patients.json")
        records_file = os.path.join(self.test_dir, "medical_records.json")
        
        with open(patients_file, 'w', encoding='utf-8') as f:
            json.dump(test_patients, f, ensure_ascii=False, indent=2)
        
        with open(records_file, 'w', encoding='utf-8') as f:
            json.dump(test_records, f, ensure_ascii=False, indent=2)
    
    def test_app_creation(self):
        """アプリケーションの作成をテスト"""
        self.assertIsNotNone(self.app)
        self.assertTrue(self.app.config['TESTING'])
    
    def test_index_route(self):
        """インデックスルートのテスト"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_api_patients_route(self):
        """患者APIのテスト"""
        with patch('app.app.PATIENTS_FILE', os.path.join(self.test_dir, "patients.json")):
            response = self.client.get('/api/patients')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['patient_id'], 'TEST001')
    
    def test_api_medical_records_route(self):
        """医療記録APIのテスト"""
        with patch('app.app.RECORDS_FILE', os.path.join(self.test_dir, "medical_records.json")):
            response = self.client.get('/api/medical-records')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 2)
    
    def test_api_patient_detail_route(self):
        """患者詳細APIのテスト"""
        with patch('app.app.PATIENTS_FILE', os.path.join(self.test_dir, "patients.json")):
            response = self.client.get('/api/patients/TEST001')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertEqual(data['patient_id'], 'TEST001')
            self.assertEqual(data['name'], 'テスト患者1')
    
    def test_api_patient_detail_not_found(self):
        """存在しない患者の詳細APIテスト"""
        with patch('app.app.PATIENTS_FILE', os.path.join(self.test_dir, "patients.json")):
            response = self.client.get('/api/patients/NOTFOUND')
            self.assertEqual(response.status_code, 404)
    
    def test_api_add_medical_record(self):
        """医療記録追加APIのテスト"""
        with patch('app.app.RECORDS_FILE', os.path.join(self.test_dir, "medical_records.json")):
            new_record = {
                "patient_id": "TEST001",
                "date": "2024-02-01",
                "diagnosis": "新しい診断",
                "symptoms": "新しい症状",
                "treatment": "新しい治療"
            }
            
            response = self.client.post('/api/medical-records', 
                                      data=json.dumps(new_record),
                                      content_type='application/json')
            self.assertEqual(response.status_code, 201)
            
            data = json.loads(response.data)
            self.assertEqual(data['patient_id'], 'TEST001')
    
    def test_api_add_patient(self):
        """患者追加APIのテスト"""
        with patch('app.app.PATIENTS_FILE', os.path.join(self.test_dir, "patients.json")):
            new_patient = {
                "patient_id": "TEST003",
                "name": "テスト患者3",
                "name_kana": "テストカンジャ3",
                "birth_date": "1995-03-20",
                "gender": "男性"
            }
            
            response = self.client.post('/api/patients',
                                      data=json.dumps(new_patient),
                                      content_type='application/json')
            self.assertEqual(response.status_code, 201)
            
            data = json.loads(response.data)
            self.assertEqual(data['patient_id'], 'TEST003')
    
    def test_webauthn_register_begin(self):
        """WebAuthn登録開始のテスト"""
        response = self.client.post('/api/webauthn/register/begin',
                                  data=json.dumps({"username": "testuser"}),
                                  content_type='application/json')
        # WebAuthnが利用できない場合は400を返す
        self.assertIn(response.status_code, [200, 400])
    
    def test_cors_headers(self):
        """CORSヘッダーのテスト"""
        response = self.client.options('/api/patients')
        self.assertIn('Access-Control-Allow-Origin', response.headers)


class TestDataFunctions(unittest.TestCase):
    """データ処理関数のテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.test_dir = tempfile.mkdtemp()
        self.patients_file = os.path.join(self.test_dir, "patients.json")
        self.records_file = os.path.join(self.test_dir, "medical_records.json")
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_load_patients_empty_file(self):
        """空の患者ファイルの読み込みテスト"""
        # 空のファイルを作成
        with open(self.patients_file, 'w') as f:
            f.write('')
        
        patients = load_patients(self.patients_file)
        self.assertEqual(patients, [])
    
    def test_load_patients_invalid_json(self):
        """無効なJSONファイルの読み込みテスト"""
        # 無効なJSONファイルを作成
        with open(self.patients_file, 'w') as f:
            f.write('invalid json content')
        
        patients = load_patients(self.patients_file)
        self.assertEqual(patients, [])
    
    def test_load_patients_valid_data(self):
        """有効な患者データの読み込みテスト"""
        test_data = [
            {"patient_id": "TEST001", "name": "テスト患者"}
        ]
        
        with open(self.patients_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)
        
        patients = load_patients(self.patients_file)
        self.assertEqual(len(patients), 1)
        self.assertEqual(patients[0]['patient_id'], 'TEST001')
    
    def test_save_patients(self):
        """患者データの保存テスト"""
        test_data = [
            {"patient_id": "TEST001", "name": "テスト患者"}
        ]
        
        result = save_patients(test_data, self.patients_file)
        self.assertTrue(result)
        
        # ファイルが作成されたことを確認
        self.assertTrue(os.path.exists(self.patients_file))
        
        # データが正しく保存されたことを確認
        with open(self.patients_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, test_data)
    
    def test_load_medical_records(self):
        """医療記録の読み込みテスト"""
        test_data = [
            {"patient_id": "TEST001", "diagnosis": "風邪"}
        ]
        
        with open(self.records_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)
        
        records = load_medical_records(self.records_file)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['patient_id'], 'TEST001')
    
    def test_save_medical_records(self):
        """医療記録の保存テスト"""
        test_data = [
            {"patient_id": "TEST001", "diagnosis": "風邪"}
        ]
        
        result = save_medical_records(test_data, self.records_file)
        self.assertTrue(result)
        
        # ファイルが作成されたことを確認
        self.assertTrue(os.path.exists(self.records_file))


class TestErrorHandling(unittest.TestCase):
    """エラーハンドリングのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_404_error(self):
        """404エラーのテスト"""
        response = self.client.get('/nonexistent-route')
        self.assertEqual(response.status_code, 404)
    
    def test_405_method_not_allowed(self):
        """405メソッド許可エラーのテスト"""
        response = self.client.delete('/')
        self.assertEqual(response.status_code, 405)
    
    def test_invalid_json_request(self):
        """無効なJSONリクエストのテスト"""
        response = self.client.post('/api/patients',
                                  data='invalid json',
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)


class TestWebAuthnIntegration(unittest.TestCase):
    """WebAuthn統合のテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('app.app.WEBAUTHN_AVAILABLE', False)
    def test_webauthn_not_available(self):
        """WebAuthnが利用できない場合のテスト"""
        response = self.client.post('/api/webauthn/register/begin',
                                  data=json.dumps({"username": "testuser"}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_webauthn_missing_username(self):
        """WebAuthnでユーザー名が不足している場合のテスト"""
        response = self.client.post('/api/webauthn/register/begin',
                                  data=json.dumps({}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    # テストスイートの実行
    unittest.main(verbosity=2)
