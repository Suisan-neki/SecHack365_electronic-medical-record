import hashlib
import hmac
import time
import json
from datetime import datetime, timedelta

class AuthorizationToken:
    def __init__(self, secret_key="medical_dx_secret_2024"):
        self.secret_key = secret_key.encode('utf-8')
    
    def generate_token(self, user_id, role="doctor", expires_in_hours=8):
        """医療従事者用のセキュリティトークンを生成"""
        payload = {
            "user_id": user_id,
            "role": role,
            "issued_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=expires_in_hours)).isoformat(),
            "permissions": self._get_permissions(role)
        }
        
        payload_json = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.secret_key,
            payload_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        token = {
            "payload": payload,
            "signature": signature
        }
        
        return token
    
    def verify_token(self, token):
        """トークンの有効性を検証"""
        try:
            payload = token["payload"]
            signature = token["signature"]
            
            # 署名の検証
            payload_json = json.dumps(payload, sort_keys=True)
            expected_signature = hmac.new(
                self.secret_key,
                payload_json.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return False, "無効な署名"
            
            # 有効期限の確認
            expires_at = datetime.fromisoformat(payload["expires_at"])
            if datetime.utcnow() > expires_at:
                return False, "トークンが期限切れ"
            
            return True, "有効なトークン"
            
        except Exception as e:
            return False, f"トークン検証エラー: {str(e)}"
    
    def _get_permissions(self, role):
        """役割に応じた権限を取得"""
        permissions = {
            "doctor": ["read_patient_data", "write_patient_data", "prescribe_medication", "update_vitals"],
            "nurse": ["read_patient_data", "update_vitals"],
            "admin": ["read_patient_data", "write_patient_data", "manage_users"]
        }
        return permissions.get(role, [])
