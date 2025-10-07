"""
設定管理モジュール

システムの設定を管理し、環境別の設定ファイルをサポート
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

class Environment(Enum):
    """環境タイプ"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"

@dataclass
class DatabaseConfig:
    """データベース設定"""
    host: str = "localhost"
    port: int = 5432
    name: str = "medical_records"
    user: str = "postgres"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

@dataclass
class SecurityConfig:
    """セキュリティ設定"""
    secret_key: str = "your-secret-key-here"
    session_timeout: int = 3600
    max_login_attempts: int = 5
    lockout_duration: int = 900
    password_min_length: int = 8
    require_special_chars: bool = True
    webauthn_timeout: int = 30000

@dataclass
class LoggingConfig:
    """ログ設定"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/app.log"
    max_size: str = "10MB"
    backup_count: int = 5
    console_output: bool = True

@dataclass
class APIConfig:
    """API設定"""
    host: str = "0.0.0.0"
    port: int = 5002
    debug: bool = False
    cors_origins: list = None
    rate_limit: str = "100/hour"
    timeout: int = 30
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:5001"]

@dataclass
class WebAuthnConfig:
    """WebAuthn設定"""
    rp_id: str = "localhost"
    rp_name: str = "患者情報共有システム"
    origin: str = "http://localhost:5001"
    rp_icon: str = "https://localhost:5001/favicon.ico"
    timeout: int = 30000
    challenge_length: int = 32

@dataclass
class SystemConfig:
    """システム全体の設定"""
    environment: Environment = Environment.DEVELOPMENT
    database: DatabaseConfig = None
    security: SecurityConfig = None
    logging: LoggingConfig = None
    api: APIConfig = None
    webauthn: WebAuthnConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.api is None:
            self.api = APIConfig()
        if self.webauthn is None:
            self.webauthn = WebAuthnConfig()

class ConfigManager:
    """設定管理クラス"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self._config: Optional[SystemConfig] = None
    
    def load_config(self, environment: Environment = None) -> SystemConfig:
        """設定を読み込む"""
        if environment is None:
            environment = self._detect_environment()
        
        # 環境変数から設定を読み込み
        config = self._load_from_env(environment)
        
        # 設定ファイルから読み込み（環境変数を上書き）
        config_file = self.config_dir / f"{environment.value}.json"
        if config_file.exists():
            file_config = self._load_from_file(config_file)
            config = self._merge_configs(config, file_config)
        
        # デフォルト設定ファイルから読み込み
        default_config_file = self.config_dir / "default.json"
        if default_config_file.exists():
            default_config = self._load_from_file(default_config_file)
            config = self._merge_configs(config, default_config)
        
        self._config = config
        self.logger.info(f"設定を読み込みました: {environment.value}")
        return config
    
    def _detect_environment(self) -> Environment:
        """環境を自動検出"""
        env = os.getenv("FLASK_ENV", "development").lower()
        
        if env in ["development", "dev"]:
            return Environment.DEVELOPMENT
        elif env in ["staging", "stage"]:
            return Environment.STAGING
        elif env in ["production", "prod"]:
            return Environment.PRODUCTION
        elif env in ["test", "testing"]:
            return Environment.TEST
        else:
            return Environment.DEVELOPMENT
    
    def _load_from_env(self, environment: Environment) -> SystemConfig:
        """環境変数から設定を読み込む"""
        config = SystemConfig(environment=environment)
        
        # データベース設定
        config.database.host = os.getenv("DB_HOST", config.database.host)
        config.database.port = int(os.getenv("DB_PORT", config.database.port))
        config.database.name = os.getenv("DB_NAME", config.database.name)
        config.database.user = os.getenv("DB_USER", config.database.user)
        config.database.password = os.getenv("DB_PASSWORD", config.database.password)
        
        # セキュリティ設定
        config.security.secret_key = os.getenv("SECRET_KEY", config.security.secret_key)
        config.security.session_timeout = int(os.getenv("SESSION_TIMEOUT", config.security.session_timeout))
        
        # API設定
        config.api.host = os.getenv("API_HOST", config.api.host)
        config.api.port = int(os.getenv("API_PORT", config.api.port))
        config.api.debug = os.getenv("API_DEBUG", "false").lower() == "true"
        
        # WebAuthn設定
        config.webauthn.rp_id = os.getenv("WEBAUTHN_RP_ID", config.webauthn.rp_id)
        config.webauthn.rp_name = os.getenv("WEBAUTHN_RP_NAME", config.webauthn.rp_name)
        config.webauthn.origin = os.getenv("WEBAUTHN_ORIGIN", config.webauthn.origin)
        
        return config
    
    def _load_from_file(self, config_file: Path) -> SystemConfig:
        """設定ファイルから設定を読み込む"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return self._dict_to_config(config_data)
            
        except Exception as e:
            self.logger.warning(f"設定ファイルの読み込みに失敗: {config_file} - {e}")
            return SystemConfig()
    
    def _dict_to_config(self, config_data: Dict[str, Any]) -> SystemConfig:
        """辞書から設定オブジェクトに変換"""
        config = SystemConfig()
        
        if "environment" in config_data:
            config.environment = Environment(config_data["environment"])
        
        if "database" in config_data:
            db_config = config_data["database"]
            config.database = DatabaseConfig(**db_config)
        
        if "security" in config_data:
            sec_config = config_data["security"]
            config.security = SecurityConfig(**sec_config)
        
        if "logging" in config_data:
            log_config = config_data["logging"]
            config.logging = LoggingConfig(**log_config)
        
        if "api" in config_data:
            api_config = config_data["api"]
            config.api = APIConfig(**api_config)
        
        if "webauthn" in config_data:
            webauthn_config = config_data["webauthn"]
            config.webauthn = WebAuthnConfig(**webauthn_config)
        
        return config
    
    def _merge_configs(self, base: SystemConfig, override: SystemConfig) -> SystemConfig:
        """設定をマージする"""
        # 簡単なマージ実装（実際にはより複雑になる可能性）
        if override.database:
            base.database = override.database
        if override.security:
            base.security = override.security
        if override.logging:
            base.logging = override.logging
        if override.api:
            base.api = override.api
        if override.webauthn:
            base.webauthn = override.webauthn
        
        return base
    
    def save_config(self, config: SystemConfig, environment: Environment = None) -> bool:
        """設定をファイルに保存"""
        if environment is None:
            environment = config.environment
        
        config_file = self.config_dir / f"{environment.value}.json"
        
        try:
            config_dict = self._config_to_dict(config)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"設定を保存しました: {config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"設定の保存に失敗: {e}")
            return False
    
    def _config_to_dict(self, config: SystemConfig) -> Dict[str, Any]:
        """設定オブジェクトを辞書に変換"""
        config_dict = {
            "environment": config.environment.value,
            "database": asdict(config.database),
            "security": asdict(config.security),
            "logging": asdict(config.logging),
            "api": asdict(config.api),
            "webauthn": asdict(config.webauthn)
        }
        
        return config_dict
    
    def get_config(self) -> SystemConfig:
        """現在の設定を取得"""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def validate_config(self, config: SystemConfig = None) -> Dict[str, Any]:
        """設定の妥当性を検証"""
        if config is None:
            config = self.get_config()
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # セキュリティ設定の検証
        if len(config.security.secret_key) < 32:
            validation_result["warnings"].append("SECRET_KEYが短すぎます（32文字以上推奨）")
        
        if config.security.session_timeout < 300:
            validation_result["warnings"].append("セッションタイムアウトが短すぎます（5分以上推奨）")
        
        # API設定の検証
        if config.api.port < 1024 and os.name != 'nt':
            validation_result["warnings"].append("ポート番号が1024未満です（管理者権限が必要）")
        
        # WebAuthn設定の検証
        if not config.webauthn.origin.startswith(('http://', 'https://')):
            validation_result["errors"].append("WebAuthnのoriginが無効です")
            validation_result["valid"] = False
        
        # データベース設定の検証
        if not config.database.host:
            validation_result["errors"].append("データベースホストが設定されていません")
            validation_result["valid"] = False
        
        if config.database.port <= 0 or config.database.port > 65535:
            validation_result["errors"].append("データベースポートが無効です")
            validation_result["valid"] = False
        
        return validation_result
    
    def create_default_configs(self):
        """デフォルト設定ファイルを作成"""
        environments = [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION]
        
        for env in environments:
            config = SystemConfig(environment=env)
            
            # 環境別の設定調整
            if env == Environment.PRODUCTION:
                config.api.debug = False
                config.logging.level = "WARNING"
                config.security.session_timeout = 1800
            elif env == Environment.STAGING:
                config.api.debug = True
                config.logging.level = "INFO"
            else:  # DEVELOPMENT
                config.api.debug = True
                config.logging.level = "DEBUG"
                config.logging.console_output = True
            
            self.save_config(config, env)
        
        self.logger.info("デフォルト設定ファイルを作成しました")
    
    def get_database_url(self, config: SystemConfig = None) -> str:
        """データベースURLを生成"""
        if config is None:
            config = self.get_config()
        
        db = config.database
        return f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.name}"
    
    def setup_logging(self, config: SystemConfig = None):
        """ログ設定を適用"""
        if config is None:
            config = self.get_config()
        
        log_config = config.logging
        
        # ログレベルを設定
        log_level = getattr(logging, log_config.level.upper(), logging.INFO)
        
        # ログフォーマットを設定
        formatter = logging.Formatter(log_config.format)
        
        # ファイルハンドラーを設定
        log_file_path = Path(log_config.file_path)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        
        # コンソールハンドラーを設定
        handlers = [file_handler]
        
        if log_config.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(log_level)
            handlers.append(console_handler)
        
        # ルートロガーに設定を適用
        logging.basicConfig(
            level=log_level,
            handlers=handlers,
            force=True
        )
        
        self.logger.info(f"ログ設定を適用しました: {log_config.level}")


def main():
    """メイン関数（コマンドライン実行用）"""
    import argparse
    
    parser = argparse.ArgumentParser(description='設定管理ユーティリティ')
    parser.add_argument('--config-dir', default='config', help='設定ディレクトリ')
    parser.add_argument('command', choices=['validate', 'create-defaults', 'show'], 
                       help='実行するコマンド')
    parser.add_argument('--environment', choices=['development', 'staging', 'production', 'test'],
                       help='環境')
    
    args = parser.parse_args()
    
    manager = ConfigManager(args.config_dir)
    
    if args.command == 'validate':
        env = Environment(args.environment) if args.environment else None
        config = manager.load_config(env)
        result = manager.validate_config(config)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == 'create-defaults':
        manager.create_default_configs()
        print("デフォルト設定ファイルを作成しました")
    
    elif args.command == 'show':
        env = Environment(args.environment) if args.environment else None
        config = manager.load_config(env)
        config_dict = manager._config_to_dict(config)
        print(json.dumps(config_dict, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
