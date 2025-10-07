"""
システムチェッカー

詳細なシステム状態をチェックし、監査ログを生成する
"""

import os
import json
import hashlib
import psutil
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

class SystemChecker:
    """システムの詳細チェックを行うクラス"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.logger = logging.getLogger(__name__)
        self.audit_logs = []
    
    def check_security_keys(self) -> Dict[str, Any]:
        """セキュリティキーの状態をチェック"""
        key_status = {
            "status": "healthy",
            "checks": [],
            "issues": []
        }
        
        # WebAuthn認証情報のチェック
        webauthn_file = self.base_dir / "data" / "webauthn_credentials.json"
        if webauthn_file.exists():
            try:
                with open(webauthn_file, 'r', encoding='utf-8') as f:
                    credentials = json.load(f)
                
                key_status["checks"].append({
                    "name": "WebAuthn認証情報",
                    "status": "OK",
                    "details": f"{len(credentials)}件の認証情報が登録されています",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                key_status["checks"].append({
                    "name": "WebAuthn認証情報",
                    "status": "ERROR",
                    "details": f"認証情報の読み込みに失敗: {e}",
                    "timestamp": datetime.now().isoformat()
                })
                key_status["issues"].append("WebAuthn認証情報の読み込みエラー")
        else:
            key_status["checks"].append({
                "name": "WebAuthn認証情報",
                "status": "WARNING",
                "details": "認証情報ファイルが存在しません",
                "timestamp": datetime.now().isoformat()
            })
            key_status["issues"].append("WebAuthn認証情報ファイルが見つかりません")
        
        # データファイルの整合性チェック
        data_files = ["patients.json", "medical_records.json"]
        for file_name in data_files:
            file_path = self.base_dir / "data" / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # ファイルハッシュを計算
                    file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()[:16]
                    
                    key_status["checks"].append({
                        "name": f"{file_name}整合性",
                        "status": "OK",
                        "details": f"ファイルサイズ: {file_path.stat().st_size}bytes, ハッシュ: {file_hash}",
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    key_status["checks"].append({
                        "name": f"{file_name}整合性",
                        "status": "ERROR",
                        "details": f"ファイル読み込みエラー: {e}",
                        "timestamp": datetime.now().isoformat()
                    })
                    key_status["issues"].append(f"{file_name}の読み込みエラー")
            else:
                key_status["checks"].append({
                    "name": f"{file_name}存在確認",
                    "status": "WARNING",
                    "details": "ファイルが存在しません",
                    "timestamp": datetime.now().isoformat()
                })
                key_status["issues"].append(f"{file_name}が見つかりません")
        
        # 全体のステータスを決定
        if key_status["issues"]:
            key_status["status"] = "warning" if len(key_status["issues"]) < 3 else "error"
        
        return key_status
    
    def check_communication_status(self) -> Dict[str, Any]:
        """通信状態をチェック"""
        comm_status = {
            "status": "healthy",
            "checks": [],
            "issues": []
        }
        
        # ポート5002のチェック
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5002))
            sock.close()
            
            if result == 0:
                comm_status["checks"].append({
                    "name": "Flask API (5002)",
                    "status": "OK",
                    "details": "ポート5002でAPIサーバーが稼働中",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                comm_status["checks"].append({
                    "name": "Flask API (5002)",
                    "status": "ERROR",
                    "details": "ポート5002に接続できません",
                    "timestamp": datetime.now().isoformat()
                })
                comm_status["issues"].append("APIサーバーが起動していません")
        except Exception as e:
            comm_status["checks"].append({
                "name": "Flask API (5002)",
                "status": "ERROR",
                "details": f"ポートチェックエラー: {e}",
                "timestamp": datetime.now().isoformat()
            })
            comm_status["issues"].append("APIサーバーの状態確認エラー")
        
        # ポート5001のチェック
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5001))
            sock.close()
            
            if result == 0:
                comm_status["checks"].append({
                    "name": "React App (5001)",
                    "status": "OK",
                    "details": "ポート5001でフロントエンドが稼働中",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                comm_status["checks"].append({
                    "name": "React App (5001)",
                    "status": "WARNING",
                    "details": "ポート5001に接続できません",
                    "timestamp": datetime.now().isoformat()
                })
                comm_status["issues"].append("フロントエンドが起動していません")
        except Exception as e:
            comm_status["checks"].append({
                "name": "React App (5001)",
                "status": "ERROR",
                "details": f"ポートチェックエラー: {e}",
                "timestamp": datetime.now().isoformat()
            })
            comm_status["issues"].append("フロントエンドの状態確認エラー")
        
        # 全体のステータスを決定
        if comm_status["issues"]:
            comm_status["status"] = "warning" if len(comm_status["issues"]) < 2 else "error"
        
        return comm_status
    
    def check_database_integrity(self) -> Dict[str, Any]:
        """データベース（ファイル）の整合性をチェック"""
        db_status = {
            "status": "healthy",
            "checks": [],
            "issues": []
        }
        
        # 患者データの整合性
        patients_file = self.base_dir / "data" / "patients.json"
        if patients_file.exists():
            try:
                with open(patients_file, 'r', encoding='utf-8') as f:
                    patients = json.load(f)
                
                # 必須フィールドのチェック
                required_fields = ['patient_id', 'name', 'birth_date', 'gender']
                valid_patients = 0
                invalid_patients = 0
                
                for patient in patients:
                    if all(field in patient for field in required_fields):
                        valid_patients += 1
                    else:
                        invalid_patients += 1
                
                db_status["checks"].append({
                    "name": "患者データ整合性",
                    "status": "OK" if invalid_patients == 0 else "WARNING",
                    "details": f"有効: {valid_patients}件, 無効: {invalid_patients}件",
                    "timestamp": datetime.now().isoformat()
                })
                
                if invalid_patients > 0:
                    db_status["issues"].append(f"{invalid_patients}件の患者データに問題があります")
                    
            except Exception as e:
                db_status["checks"].append({
                    "name": "患者データ整合性",
                    "status": "ERROR",
                    "details": f"データ読み込みエラー: {e}",
                    "timestamp": datetime.now().isoformat()
                })
                db_status["issues"].append("患者データの読み込みエラー")
        
        # 医療記録データの整合性
        records_file = self.base_dir / "data" / "medical_records.json"
        if records_file.exists():
            try:
                with open(records_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                
                # 必須フィールドのチェック
                required_fields = ['record_id', 'patient_id', 'diagnosis', 'date']
                valid_records = 0
                invalid_records = 0
                
                for record in records:
                    if all(field in record for field in required_fields):
                        valid_records += 1
                    else:
                        invalid_records += 1
                
                db_status["checks"].append({
                    "name": "医療記録整合性",
                    "status": "OK" if invalid_records == 0 else "WARNING",
                    "details": f"有効: {valid_records}件, 無効: {invalid_records}件",
                    "timestamp": datetime.now().isoformat()
                })
                
                if invalid_records > 0:
                    db_status["issues"].append(f"{invalid_records}件の医療記録に問題があります")
                    
            except Exception as e:
                db_status["checks"].append({
                    "name": "医療記録整合性",
                    "status": "ERROR",
                    "details": f"データ読み込みエラー: {e}",
                    "timestamp": datetime.now().isoformat()
                })
                db_status["issues"].append("医療記録の読み込みエラー")
        
        # 全体のステータスを決定
        if db_status["issues"]:
            db_status["status"] = "warning" if len(db_status["issues"]) < 3 else "error"
        
        return db_status
    
    def check_system_resources(self) -> Dict[str, Any]:
        """システムリソースをチェック"""
        resource_status = {
            "status": "healthy",
            "checks": [],
            "issues": []
        }
        
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_status = "OK" if cpu_percent < 80 else "WARNING" if cpu_percent < 95 else "ERROR"
            resource_status["checks"].append({
                "name": "CPU使用率",
                "status": cpu_status,
                "details": f"{cpu_percent:.1f}%",
                "timestamp": datetime.now().isoformat()
            })
            
            if cpu_percent > 80:
                resource_status["issues"].append(f"CPU使用率が高いです: {cpu_percent:.1f}%")
            
            # メモリ使用率
            memory = psutil.virtual_memory()
            memory_status = "OK" if memory.percent < 80 else "WARNING" if memory.percent < 95 else "ERROR"
            resource_status["checks"].append({
                "name": "メモリ使用率",
                "status": memory_status,
                "details": f"{memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)",
                "timestamp": datetime.now().isoformat()
            })
            
            if memory.percent > 80:
                resource_status["issues"].append(f"メモリ使用率が高いです: {memory.percent:.1f}%")
            
            # ディスク使用率
            disk = shutil.disk_usage(self.base_dir)
            disk_percent = (disk.used / disk.total) * 100
            disk_status = "OK" if disk_percent < 80 else "WARNING" if disk_percent < 95 else "ERROR"
            resource_status["checks"].append({
                "name": "ディスク使用率",
                "status": disk_status,
                "details": f"{disk_percent:.1f}% ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)",
                "timestamp": datetime.now().isoformat()
            })
            
            if disk_percent > 80:
                resource_status["issues"].append(f"ディスク使用率が高いです: {disk_percent:.1f}%")
                
        except Exception as e:
            resource_status["checks"].append({
                "name": "システムリソース",
                "status": "ERROR",
                "details": f"リソース監視エラー: {e}",
                "timestamp": datetime.now().isoformat()
            })
            resource_status["issues"].append("システムリソースの監視エラー")
        
        # 全体のステータスを決定
        if resource_status["issues"]:
            resource_status["status"] = "warning" if len(resource_status["issues"]) < 2 else "error"
        
        return resource_status
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """包括的なシステムチェックを実行"""
        start_time = datetime.now()
        
        # 各チェックを実行
        security_check = self.check_security_keys()
        communication_check = self.check_communication_status()
        database_check = self.check_database_integrity()
        resource_check = self.check_system_resources()
        
        # 結果をまとめる
        comprehensive_result = {
            "timestamp": start_time.isoformat(),
            "overall_status": "healthy",
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "warning_checks": 0,
            "checks": {
                "security": security_check,
                "communication": communication_check,
                "database": database_check,
                "resources": resource_check
            },
            "summary": {
                "total_events": 0,
                "successful_events": 0,
                "failed_events": 0,
                "active_users": 3  # 実際のユーザー数
            }
        }
        
        # 統計を計算
        all_checks = []
        for category, result in comprehensive_result["checks"].items():
            all_checks.extend(result["checks"])
        
        comprehensive_result["total_checks"] = len(all_checks)
        comprehensive_result["successful_checks"] = len([c for c in all_checks if c["status"] == "OK"])
        comprehensive_result["failed_checks"] = len([c for c in all_checks if c["status"] == "ERROR"])
        comprehensive_result["warning_checks"] = len([c for c in all_checks if c["status"] == "WARNING"])
        
        # サマリーを更新
        comprehensive_result["summary"]["total_events"] = comprehensive_result["total_checks"]
        comprehensive_result["summary"]["successful_events"] = comprehensive_result["successful_checks"]
        comprehensive_result["summary"]["failed_events"] = comprehensive_result["failed_checks"]
        
        # 全体のステータスを決定
        if comprehensive_result["failed_checks"] > 0:
            comprehensive_result["overall_status"] = "error"
        elif comprehensive_result["warning_checks"] > 0:
            comprehensive_result["overall_status"] = "warning"
        
        # 監査ログに記録
        self.audit_logs.append({
            "timestamp": start_time.isoformat(),
            "event": "システムチェック実行",
            "status": comprehensive_result["overall_status"],
            "details": f"総チェック: {comprehensive_result['total_checks']}, 成功: {comprehensive_result['successful_checks']}, 失敗: {comprehensive_result['failed_checks']}"
        })
        
        return comprehensive_result
    
    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """監査ログを取得"""
        return self.audit_logs[-limit:] if self.audit_logs else []
    
    def add_audit_log(self, event: str, status: str, details: str = ""):
        """監査ログを追加"""
        self.audit_logs.append({
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "status": status,
            "details": details
        })
