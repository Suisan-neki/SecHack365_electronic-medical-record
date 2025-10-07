"""
患者同意管理モジュール

患者のデータ利用に関する同意を管理し、透明性を確保する
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConsentManager:
    """患者同意を管理するクラス"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.consent_file = self.data_dir / 'patient_consents.json'
        self.consent_log_file = self.data_dir / 'consent_logs.json'
        self._initialize_files()
    
    def _initialize_files(self):
        """同意管理ファイルを初期化する"""
        if not self.consent_file.exists():
            with open(self.consent_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2, ensure_ascii=False)
        
        if not self.consent_log_file.exists():
            with open(self.consent_log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
    
    def get_consent_purposes(self) -> List[Dict[str, str]]:
        """
        利用目的の一覧を取得する
        
        Returns:
            利用目的のリスト
        """
        return [
            {
                'purpose_id': 'medical_treatment',
                'name': '医療・診療',
                'description': '診断、治療、処方などの医療行為のために使用します'
            },
            {
                'purpose_id': 'medical_research',
                'name': '医学研究',
                'description': '新しい治療法や診断法の開発のために使用します'
            },
            {
                'purpose_id': 'ai_development',
                'name': 'AI開発',
                'description': '医療AIの学習データとして使用します'
            },
            {
                'purpose_id': 'quality_improvement',
                'name': '品質改善',
                'description': '医療サービスの品質向上のために使用します'
            },
            {
                'purpose_id': 'statistical_analysis',
                'name': '統計分析',
                'description': '統計的な分析や研究のために使用します'
            }
        ]
    
    def create_consent(self, patient_id: str, purposes: List[str], 
                      anonymization_level: str = 'level1', 
                      duration_days: Optional[int] = None) -> Dict[str, Any]:
        """
        患者の同意を作成する
        
        Args:
            patient_id: 患者ID
            purposes: 同意する利用目的のリスト
            anonymization_level: 匿名化レベル
            duration_days: 同意期間（日数、Noneの場合は無期限）
            
        Returns:
            作成された同意情報
        """
        # 現在の同意情報を読み込む
        with open(self.consent_file, 'r', encoding='utf-8') as f:
            consents = json.load(f)
        
        # 新しい同意を作成
        consent_info = {
            'patient_id': patient_id,
            'purposes': purposes,
            'anonymization_level': anonymization_level,
            'granted_at': datetime.now().isoformat(),
            'expires_at': self._calculate_expiration(duration_days),
            'status': 'active',
            'revoked_at': None,
            'revocation_reason': None
        }
        
        # 同意情報を保存
        consents[patient_id] = consent_info
        with open(self.consent_file, 'w', encoding='utf-8') as f:
            json.dump(consents, f, indent=2, ensure_ascii=False)
        
        # ログに記録
        self._log_consent_action(patient_id, 'granted', purposes, anonymization_level)
        
        logger.info(f"患者 {patient_id} の同意を作成しました")
        return consent_info
    
    def revoke_consent(self, patient_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        患者の同意を取り消す
        
        Args:
            patient_id: 患者ID
            reason: 取り消し理由
            
        Returns:
            更新された同意情報
        """
        # 現在の同意情報を読み込む
        with open(self.consent_file, 'r', encoding='utf-8') as f:
            consents = json.load(f)
        
        if patient_id not in consents:
            raise ValueError(f"患者 {patient_id} の同意情報が見つかりません")
        
        # 同意を取り消す
        consents[patient_id]['status'] = 'revoked'
        consents[patient_id]['revoked_at'] = datetime.now().isoformat()
        consents[patient_id]['revocation_reason'] = reason or '患者からの要求'
        
        # 同意情報を保存
        with open(self.consent_file, 'w', encoding='utf-8') as f:
            json.dump(consents, f, indent=2, ensure_ascii=False)
        
        # ログに記録
        self._log_consent_action(patient_id, 'revoked', reason=reason)
        
        logger.info(f"患者 {patient_id} の同意を取り消しました")
        return consents[patient_id]
    
    def update_consent(self, patient_id: str, purposes: Optional[List[str]] = None,
                      anonymization_level: Optional[str] = None) -> Dict[str, Any]:
        """
        患者の同意を更新する
        
        Args:
            patient_id: 患者ID
            purposes: 新しい利用目的のリスト
            anonymization_level: 新しい匿名化レベル
            
        Returns:
            更新された同意情報
        """
        # 現在の同意情報を読み込む
        with open(self.consent_file, 'r', encoding='utf-8') as f:
            consents = json.load(f)
        
        if patient_id not in consents:
            raise ValueError(f"患者 {patient_id} の同意情報が見つかりません")
        
        # 同意を更新
        if purposes is not None:
            consents[patient_id]['purposes'] = purposes
        
        if anonymization_level is not None:
            consents[patient_id]['anonymization_level'] = anonymization_level
        
        consents[patient_id]['updated_at'] = datetime.now().isoformat()
        
        # 同意情報を保存
        with open(self.consent_file, 'w', encoding='utf-8') as f:
            json.dump(consents, f, indent=2, ensure_ascii=False)
        
        # ログに記録
        self._log_consent_action(patient_id, 'updated', purposes, anonymization_level)
        
        logger.info(f"患者 {patient_id} の同意を更新しました")
        return consents[patient_id]
    
    def get_consent(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        患者の同意情報を取得する
        
        Args:
            patient_id: 患者ID
            
        Returns:
            同意情報（存在しない場合はNone）
        """
        with open(self.consent_file, 'r', encoding='utf-8') as f:
            consents = json.load(f)
        
        return consents.get(patient_id)
    
    def check_consent(self, patient_id: str, purpose: str) -> bool:
        """
        特定の利用目的に対する同意をチェックする
        
        Args:
            patient_id: 患者ID
            purpose: 利用目的ID
            
        Returns:
            同意が有効な場合True
        """
        consent = self.get_consent(patient_id)
        
        if not consent:
            return False
        
        # ステータスのチェック
        if consent['status'] != 'active':
            return False
        
        # 有効期限のチェック
        if consent['expires_at']:
            expiration = datetime.fromisoformat(consent['expires_at'])
            if datetime.now() > expiration:
                return False
        
        # 利用目的のチェック
        return purpose in consent['purposes']
    
    def get_all_consents(self) -> Dict[str, Dict[str, Any]]:
        """
        全ての同意情報を取得する
        
        Returns:
            全患者の同意情報
        """
        with open(self.consent_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_consent_statistics(self) -> Dict[str, Any]:
        """
        同意統計情報を取得する
        
        Returns:
            統計情報
        """
        consents = self.get_all_consents()
        
        # 統計を計算
        total_consents = len(consents)
        active_consents = sum(1 for c in consents.values() if c['status'] == 'active')
        revoked_consents = sum(1 for c in consents.values() if c['status'] == 'revoked')
        
        # 利用目的ごとの統計
        purpose_stats = {}
        for consent in consents.values():
            if consent['status'] == 'active':
                for purpose in consent['purposes']:
                    purpose_stats[purpose] = purpose_stats.get(purpose, 0) + 1
        
        # 匿名化レベルごとの統計
        level_stats = {}
        for consent in consents.values():
            if consent['status'] == 'active':
                level = consent['anonymization_level']
                level_stats[level] = level_stats.get(level, 0) + 1
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_consents': total_consents,
            'active_consents': active_consents,
            'revoked_consents': revoked_consents,
            'consent_rate': (active_consents / total_consents * 100) if total_consents > 0 else 0,
            'purpose_distribution': purpose_stats,
            'anonymization_level_distribution': level_stats
        }
    
    def get_consent_logs(self, patient_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        同意ログを取得する
        
        Args:
            patient_id: 患者ID（Noneの場合は全患者）
            limit: 取得する最大ログ数
            
        Returns:
            同意ログのリスト
        """
        with open(self.consent_log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        # 患者IDでフィルタリング
        if patient_id:
            logs = [log for log in logs if log['patient_id'] == patient_id]
        
        # 最新のログを返す
        return logs[-limit:] if len(logs) > limit else logs
    
    def _calculate_expiration(self, duration_days: Optional[int]) -> Optional[str]:
        """
        有効期限を計算する
        
        Args:
            duration_days: 有効期間（日数）
            
        Returns:
            有効期限のISO文字列（無期限の場合はNone）
        """
        if duration_days is None:
            return None
        
        from datetime import timedelta
        expiration = datetime.now() + timedelta(days=duration_days)
        return expiration.isoformat()
    
    def _log_consent_action(self, patient_id: str, action: str, 
                           purposes: Optional[List[str]] = None,
                           anonymization_level: Optional[str] = None,
                           reason: Optional[str] = None):
        """
        同意アクションをログに記録する
        
        Args:
            patient_id: 患者ID
            action: アクション（'granted', 'revoked', 'updated'）
            purposes: 利用目的のリスト
            anonymization_level: 匿名化レベル
            reason: 理由
        """
        # ログを読み込む
        with open(self.consent_log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        # 新しいログエントリを追加
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'patient_id': patient_id,
            'action': action,
            'purposes': purposes,
            'anonymization_level': anonymization_level,
            'reason': reason
        }
        
        logs.append(log_entry)
        
        # ログを保存
        with open(self.consent_log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
