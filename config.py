"""
アプリケーション設定
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """基本設定"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', '32-character-encryption-key-here')
    
    # データベース設定
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://medical_user:medical_password@localhost:5432/medical_records')
    
    # Redis設定
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # セッション設定
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # ログ設定
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # ファイルアップロード設定
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    # CORS設定
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
    
    # MFA設定
    MFA_ISSUER_NAME = os.getenv('MFA_ISSUER_NAME', 'Medical Records System')
    
    # セキュリティ設定
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1時間
    
    # パスワード設定
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SYMBOLS = True
    
    # セッションタイムアウト
    PERMANENT_SESSION_LIFETIME = 3600  # 1時間

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    FLASK_ENV = 'development'
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    FLASK_ENV = 'production'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'

class TestingConfig(Config):
    """テスト環境設定"""
    TESTING = True
    DATABASE_URL = 'postgresql://medical_user:medical_password@localhost:5432/medical_records_test'
    WTF_CSRF_ENABLED = False

# 設定の選択
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
