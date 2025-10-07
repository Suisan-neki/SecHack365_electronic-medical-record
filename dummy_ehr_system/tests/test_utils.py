"""
ユーティリティ関数のテスト

システム管理、設定管理などのユーティリティをテストする
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.system_manager import SystemManager
from app.config_manager import ConfigManager, Environment, SystemConfig

class TestSystemManager(unittest.TestCase):
    """システム管理クラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.test_dir = tempfile.mkdtemp()
        self.manager = SystemManager(self.test_dir)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_system_manager_initialization(self):
        """システム管理クラスの初期化テスト"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(str(self.manager.base_dir), self.test_dir)
    
    def test_create_directories(self):
        """必要なディレクトリの作成テスト"""
        # 必要なディレクトリが作成されていることを確認
        self.assertTrue(self.manager.backup_dir.exists())
        self.assertTrue(self.manager.config_file.parent.exists())
        self.assertTrue(self.manager.log_file.parent.exists())
    
    def test_system_health_check(self):
        """システム健全性チェックのテスト"""
        health_status = self.manager.check_system_health()
        
        self.assertIn('timestamp', health_status)
        self.assertIn('overall_status', health_status)
        self.assertIn('checks', health_status)
        self.assertIn('disk_usage', health_status['checks'])
        self.assertIn('memory_usage', health_status['checks'])
        self.assertIn('data_integrity', health_status['checks'])
        self.assertIn('configuration', health_status['checks'])
    
    def test_create_backup(self):
        """バックアップ作成のテスト"""
        # テスト用のデータファイルを作成
        data_dir = Path(self.test_dir) / "data"
        data_dir.mkdir(exist_ok=True)
        
        test_data = {"test": "data"}
        test_file = data_dir / "test.json"
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # バックアップを作成
        result = self.manager.create_backup("test_backup")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['backup_name'], 'test_backup')
        
        # バックアップファイルが作成されていることを確認
        backup_path = self.manager.backup_dir / "test_backup"
        self.assertTrue(backup_path.exists())
        self.assertTrue((backup_path / "data" / "test.json").exists())
    
    def test_list_backups(self):
        """バックアップ一覧取得のテスト"""
        # 初期状態ではバックアップが空であることを確認
        backups = self.manager.list_backups()
        self.assertEqual(len(backups), 0)
        
        # バックアップを作成
        self.manager.create_backup("backup1")
        self.manager.create_backup("backup2")
        
        # バックアップ一覧を取得
        backups = self.manager.list_backups()
        self.assertEqual(len(backups), 2)
        
        # 作成日時でソートされていることを確認
        backup_names = [backup['backup_name'] for backup in backups]
        self.assertIn('backup1', backup_names)
        self.assertIn('backup2', backup_names)
    
    def test_restore_backup(self):
        """バックアップ復元のテスト"""
        # テスト用データを作成
        data_dir = Path(self.test_dir) / "data"
        data_dir.mkdir(exist_ok=True)
        
        original_data = {"original": "data"}
        original_file = data_dir / "original.json"
        with open(original_file, 'w') as f:
            json.dump(original_data, f)
        
        # バックアップを作成
        backup_result = self.manager.create_backup("restore_test")
        self.assertEqual(backup_result['status'], 'success')
        
        # 元のデータを変更
        modified_data = {"modified": "data"}
        with open(original_file, 'w') as f:
            json.dump(modified_data, f)
        
        # バックアップから復元
        restore_result = self.manager.restore_backup("restore_test")
        self.assertEqual(restore_result['status'], 'success')
        
        # 復元されたデータを確認
        with open(original_file, 'r') as f:
            restored_data = json.load(f)
        
        self.assertEqual(restored_data, original_data)
    
    def test_cleanup_old_backups(self):
        """古いバックアップのクリーンアップテスト"""
        # 複数のバックアップを作成
        for i in range(10):
            self.manager.create_backup(f"backup_{i}")
        
        # バックアップ一覧を確認
        backups = self.manager.list_backups()
        self.assertEqual(len(backups), 10)
        
        # 古いバックアップをクリーンアップ（5個保持）
        cleanup_result = self.manager.cleanup_old_backups(keep_count=5)
        self.assertEqual(cleanup_result['status'], 'success')
        
        # クリーンアップ後のバックアップ数を確認
        backups_after = self.manager.list_backups()
        self.assertEqual(len(backups_after), 5)
    
    def test_get_system_info(self):
        """システム情報取得のテスト"""
        system_info = self.manager.get_system_info()
        
        self.assertIn('system_name', system_info)
        self.assertIn('version', system_info)
        self.assertIn('python_version', system_info)
        self.assertIn('base_directory', system_info)
        self.assertIn('disk_usage', system_info)
        self.assertIn('memory_usage', system_info)
        self.assertIn('backup_count', system_info)


class TestConfigManager(unittest.TestCase):
    """設定管理クラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.test_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.test_dir)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_config_manager_initialization(self):
        """設定管理クラスの初期化テスト"""
        self.assertIsNotNone(self.config_manager)
        self.assertEqual(str(self.config_manager.config_dir), self.test_dir)
    
    def test_load_config_default(self):
        """デフォルト設定の読み込みテスト"""
        config = self.config_manager.load_config()
        
        self.assertIsNotNone(config)
        self.assertEqual(config.environment, Environment.DEVELOPMENT)
        self.assertIsNotNone(config.database)
        self.assertIsNotNone(config.security)
        self.assertIsNotNone(config.logging)
        self.assertIsNotNone(config.api)
        self.assertIsNotNone(config.webauthn)
    
    def test_load_config_environment(self):
        """環境別設定の読み込みテスト"""
        config = self.config_manager.load_config(Environment.PRODUCTION)
        
        self.assertEqual(config.environment, Environment.PRODUCTION)
        self.assertFalse(config.api.debug)
    
    def test_save_and_load_config(self):
        """設定の保存と読み込みテスト"""
        # 設定を作成
        config = SystemConfig(environment=Environment.TEST)
        config.api.port = 9999
        config.security.session_timeout = 1800
        
        # 設定を保存
        save_result = self.config_manager.save_config(config, Environment.TEST)
        self.assertTrue(save_result)
        
        # 設定ファイルが作成されていることを確認
        config_file = Path(self.test_dir) / "test.json"
        self.assertTrue(config_file.exists())
        
        # 設定を読み込み
        loaded_config = self.config_manager.load_config(Environment.TEST)
        
        self.assertEqual(loaded_config.environment, Environment.TEST)
        self.assertEqual(loaded_config.api.port, 9999)
        self.assertEqual(loaded_config.security.session_timeout, 1800)
    
    def test_config_validation(self):
        """設定検証のテスト"""
        config = SystemConfig()
        
        # 正常な設定の検証
        validation_result = self.config_manager.validate_config(config)
        self.assertIn('valid', validation_result)
        self.assertIn('errors', validation_result)
        self.assertIn('warnings', validation_result)
    
    def test_config_validation_errors(self):
        """設定検証エラーのテスト"""
        config = SystemConfig()
        config.webauthn.origin = "invalid-origin"  # 無効なorigin
        config.database.host = ""  # 空のホスト
        config.database.port = 99999  # 無効なポート
        
        validation_result = self.config_manager.validate_config(config)
        self.assertFalse(validation_result['valid'])
        self.assertTrue(len(validation_result['errors']) > 0)
    
    def test_create_default_configs(self):
        """デフォルト設定ファイル作成のテスト"""
        self.config_manager.create_default_configs()
        
        # 各環境の設定ファイルが作成されていることを確認
        for env in [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION]:
            config_file = Path(self.test_dir) / f"{env.value}.json"
            self.assertTrue(config_file.exists())
    
    def test_get_database_url(self):
        """データベースURL生成のテスト"""
        config = SystemConfig()
        config.database.host = "localhost"
        config.database.port = 5432
        config.database.name = "testdb"
        config.database.user = "testuser"
        config.database.password = "testpass"
        
        db_url = self.config_manager.get_database_url(config)
        expected_url = "postgresql://testuser:testpass@localhost:5432/testdb"
        
        self.assertEqual(db_url, expected_url)


class TestEnvironmentDetection(unittest.TestCase):
    """環境検出のテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.test_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.test_dir)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_environment_detection_development(self):
        """開発環境の検出テスト"""
        with unittest.mock.patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            env = self.config_manager._detect_environment()
            self.assertEqual(env, Environment.DEVELOPMENT)
    
    def test_environment_detection_production(self):
        """本番環境の検出テスト"""
        with unittest.mock.patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            env = self.config_manager._detect_environment()
            self.assertEqual(env, Environment.PRODUCTION)
    
    def test_environment_detection_default(self):
        """デフォルト環境の検出テスト"""
        with unittest.mock.patch.dict(os.environ, {}, clear=True):
            env = self.config_manager._detect_environment()
            self.assertEqual(env, Environment.DEVELOPMENT)


class TestDataValidation(unittest.TestCase):
    """データ検証のテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.test_dir = tempfile.mkdtemp()
        self.manager = SystemManager(self.test_dir)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_data_integrity_check_valid(self):
        """有効なデータの整合性チェック"""
        # 有効なJSONファイルを作成
        data_dir = Path(self.test_dir) / "data"
        data_dir.mkdir(exist_ok=True)
        
        valid_data = [{"test": "data"}]
        with open(data_dir / "patients.json", 'w') as f:
            json.dump(valid_data, f)
        
        result = self.manager._check_data_integrity()
        self.assertEqual(result['status'], 'healthy')
    
    def test_data_integrity_check_invalid_json(self):
        """無効なJSONファイルの整合性チェック"""
        # 無効なJSONファイルを作成
        data_dir = Path(self.test_dir) / "data"
        data_dir.mkdir(exist_ok=True)
        
        with open(data_dir / "patients.json", 'w') as f:
            f.write('invalid json')
        
        result = self.manager._check_data_integrity()
        self.assertEqual(result['status'], 'warning')
        self.assertTrue(len(result['issues']) > 0)
    
    def test_data_integrity_check_missing_file(self):
        """存在しないファイルの整合性チェック"""
        result = self.manager._check_data_integrity()
        self.assertEqual(result['status'], 'warning')
        self.assertTrue(len(result['issues']) > 0)


if __name__ == '__main__':
    # テストスイートの実行
    unittest.main(verbosity=2)
