import os
import json
import secrets
import string
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
import pyotp
import qrcode
from io import BytesIO
import base64
from core.authentication import UserAuthenticator

class UserManager(UserAuthenticator):
    """
    ユーザー管理クラス（認証機能を継承）
    
    追加機能:
    - ユーザー登録
    - パスワードリセット
    - MFA設定管理
    - プロフィール管理
    - 管理者機能
    """
    
    def __init__(self, user_db_path="user_db.json"):
        super().__init__(user_db_path)
        self.reset_tokens = {}  # パスワードリセットトークンの一時保存
        
    def register_user(self, username, password, email, role="patient", full_name="", phone=""):
        """
        新規ユーザーを登録
        
        Args:
            username (str): ユーザー名
            password (str): パスワード
            email (str): メールアドレス
            role (str): 役割 (doctor, nurse, patient, admin)
            full_name (str): フルネーム
            phone (str): 電話番号
            
        Returns:
            dict: 登録結果 {'success': bool, 'message': str, 'user_id': str}
        """
        try:
            # ユーザー名重複チェック
            if username in self.users:
                return {
                    'success': False,
                    'message': 'ユーザー名が既に存在します',
                    'user_id': None
                }
            
            # パスワード強度チェック
            password_check = self._validate_password_strength(password)
            if not password_check['valid']:
                return {
                    'success': False,
                    'message': f'パスワードが要件を満たしていません: {password_check["message"]}',
                    'user_id': None
                }
            
            # メールアドレス形式チェック
            if not self._validate_email(email):
                return {
                    'success': False,
                    'message': '無効なメールアドレス形式です',
                    'user_id': None
                }
            
            # 役割の妥当性チェック
            valid_roles = ['doctor', 'nurse', 'patient', 'admin']
            if role not in valid_roles:
                return {
                    'success': False,
                    'message': f'無効な役割です。有効な役割: {", ".join(valid_roles)}',
                    'user_id': None
                }
            
            # パスワードハッシュ化
            salt = secrets.token_urlsafe(32)
            hashed_password = pbkdf2_sha256.hash(password + salt)
            
            # ユーザーデータ作成
            user_data = {
                'password': hashed_password,
                'salt': salt,
                'role': role,
                'email': email,
                'full_name': full_name,
                'phone': phone,
                'mfa_enabled': False,
                'mfa_secret': None,
                'mfa_backup_codes': None,
                'created_at': datetime.utcnow().isoformat() + 'Z',
                'last_login': None,
                'is_active': True,
                'failed_login_attempts': 0,
                'account_locked_until': None,
                'webauthn_credentials': [],
                'webauthn_challenges': {},
                'profile': {
                    'avatar': None,
                    'department': '',
                    'license_number': '',
                    'specialization': ''
                }
            }
            
            # ユーザー追加
            self.users[username] = user_data
            self._save_users()
            
            return {
                'success': True,
                'message': 'ユーザーが正常に登録されました',
                'user_id': username
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'ユーザー登録中にエラーが発生しました: {str(e)}',
                'user_id': None
            }
    
    def _validate_password_strength(self, password):
        """
        パスワード強度をチェック
        
        Args:
            password (str): チェックするパスワード
            
        Returns:
            dict: {'valid': bool, 'message': str}
        """
        if len(password) < 8:
            return {'valid': False, 'message': '8文字以上である必要があります'}
        
        if not any(c.isupper() for c in password):
            return {'valid': False, 'message': '大文字を含む必要があります'}
        
        if not any(c.islower() for c in password):
            return {'valid': False, 'message': '小文字を含む必要があります'}
        
        if not any(c.isdigit() for c in password):
            return {'valid': False, 'message': '数字を含む必要があります'}
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return {'valid': False, 'message': '特殊文字を含む必要があります'}
        
        return {'valid': True, 'message': 'パスワードは要件を満たしています'}
    
    def _validate_email(self, email):
        """
        メールアドレス形式をチェック
        
        Args:
            email (str): チェックするメールアドレス
            
        Returns:
            bool: 有効なメールアドレスかどうか
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def generate_password_reset_token(self, username):
        """
        パスワードリセットトークンを生成
        
        Args:
            username (str): ユーザー名
            
        Returns:
            dict: {'success': bool, 'token': str, 'expires_at': str}
        """
        if username not in self.users:
            return {'success': False, 'token': None, 'expires_at': None}
        
        # トークン生成（32文字のランダム文字列）
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)  # 1時間で期限切れ
        
        # トークン保存
        self.reset_tokens[token] = {
            'username': username,
            'expires_at': expires_at,
            'used': False
        }
        
        return {
            'success': True,
            'token': token,
            'expires_at': expires_at.isoformat() + 'Z'
        }
    
    def reset_password_with_token(self, token, new_password):
        """
        トークンを使用してパスワードをリセット
        
        Args:
            token (str): リセットトークン
            new_password (str): 新しいパスワード
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        # トークン検証
        if token not in self.reset_tokens:
            return {'success': False, 'message': '無効なリセットトークンです'}
        
        token_data = self.reset_tokens[token]
        
        # 期限切れチェック
        if datetime.utcnow() > token_data['expires_at']:
            del self.reset_tokens[token]
            return {'success': False, 'message': 'リセットトークンの期限が切れています'}
        
        # 使用済みチェック
        if token_data['used']:
            return {'success': False, 'message': 'このトークンは既に使用されています'}
        
        username = token_data['username']
        
        # パスワード強度チェック
        password_check = self._validate_password_strength(new_password)
        if not password_check['valid']:
            return {'success': False, 'message': f'パスワードが要件を満たしていません: {password_check["message"]}'}
        
        try:
            # パスワード更新
            salt = secrets.token_urlsafe(32)
            hashed_password = pbkdf2_sha256.hash(new_password + salt)
            
            self.users[username]['password'] = hashed_password
            self.users[username]['salt'] = salt
            self.users[username]['failed_login_attempts'] = 0
            self.users[username]['account_locked_until'] = None
            
            # トークンを使用済みにマーク
            self.reset_tokens[token]['used'] = True
            
            self._save_users()
            
            return {'success': True, 'message': 'パスワードが正常にリセットされました'}
            
        except Exception as e:
            return {'success': False, 'message': f'パスワードリセット中にエラーが発生しました: {str(e)}'}
    
    def setup_mfa(self, username):
        """
        MFA（TOTP）をセットアップ
        
        Args:
            username (str): ユーザー名
            
        Returns:
            dict: {'success': bool, 'secret': str, 'qr_code': str, 'backup_codes': list}
        """
        if username not in self.users:
            return {'success': False, 'secret': None, 'qr_code': None, 'backup_codes': None}
        
        try:
            # TOTP秘密鍵生成
            secret = pyotp.random_base32()
            
            # QRコード生成
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=username,
                issuer_name="SecHack365 PHR System"
            )
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # QRコードをBase64エンコード
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # バックアップコード生成（8個）
            backup_codes = [
                ''.join(secrets.choice(string.digits) for _ in range(8))
                for _ in range(8)
            ]
            
            # 一時的に保存（確認後に正式保存）
            temp_mfa_data = {
                'secret': secret,
                'backup_codes': backup_codes
            }
            
            return {
                'success': True,
                'secret': secret,
                'qr_code': f'data:image/png;base64,{qr_code_base64}',
                'backup_codes': backup_codes,
                'temp_data': temp_mfa_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'secret': None,
                'qr_code': None,
                'backup_codes': None,
                'message': f'MFAセットアップ中にエラーが発生しました: {str(e)}'
            }
    
    def confirm_mfa_setup(self, username, verification_code, temp_mfa_data):
        """
        MFAセットアップを確認・完了
        
        Args:
            username (str): ユーザー名
            verification_code (str): 検証コード
            temp_mfa_data (dict): 一時MFAデータ
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        if username not in self.users:
            return {'success': False, 'message': 'ユーザーが見つかりません'}
        
        try:
            secret = temp_mfa_data['secret']
            totp = pyotp.TOTP(secret)
            
            # 検証コードチェック
            if not totp.verify(verification_code):
                return {'success': False, 'message': '検証コードが正しくありません'}
            
            # MFA設定を正式に保存
            self.users[username]['mfa_enabled'] = True
            self.users[username]['mfa_secret'] = secret
            self.users[username]['mfa_backup_codes'] = temp_mfa_data['backup_codes']
            
            self._save_users()
            
            return {'success': True, 'message': 'MFAが正常に設定されました'}
            
        except Exception as e:
            return {'success': False, 'message': f'MFA確認中にエラーが発生しました: {str(e)}'}
    
    def disable_mfa(self, username, current_password):
        """
        MFAを無効化
        
        Args:
            username (str): ユーザー名
            current_password (str): 現在のパスワード
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        if username not in self.users:
            return {'success': False, 'message': 'ユーザーが見つかりません'}
        
        # パスワード確認
        auth_result = self.authenticate(username, current_password)
        if not auth_result['success']:
            return {'success': False, 'message': 'パスワードが正しくありません'}
        
        try:
            self.users[username]['mfa_enabled'] = False
            self.users[username]['mfa_secret'] = None
            self.users[username]['mfa_backup_codes'] = None
            
            self._save_users()
            
            return {'success': True, 'message': 'MFAが無効化されました'}
            
        except Exception as e:
            return {'success': False, 'message': f'MFA無効化中にエラーが発生しました: {str(e)}'}
    
    def get_user_list(self, requesting_user_role):
        """
        ユーザー一覧を取得（管理者用）
        
        Args:
            requesting_user_role (str): 要求者の役割
            
        Returns:
            dict: {'success': bool, 'users': list, 'message': str}
        """
        if requesting_user_role != 'admin':
            return {'success': False, 'users': [], 'message': '管理者権限が必要です'}
        
        try:
            users_list = []
            for username, user_data in self.users.items():
                users_list.append({
                    'username': username,
                    'role': user_data.get('role', 'unknown'),
                    'email': user_data.get('email', ''),
                    'full_name': user_data.get('full_name', ''),
                    'is_active': user_data.get('is_active', True),
                    'mfa_enabled': user_data.get('mfa_enabled', False),
                    'created_at': user_data.get('created_at', ''),
                    'last_login': user_data.get('last_login', ''),
                    'webauthn_credentials_count': len(user_data.get('webauthn_credentials', []))
                })
            
            return {'success': True, 'users': users_list, 'message': ''}
            
        except Exception as e:
            return {'success': False, 'users': [], 'message': f'ユーザー一覧取得中にエラーが発生しました: {str(e)}'}
    
    def update_user_profile(self, username, profile_data, requesting_user, requesting_role):
        """
        ユーザープロフィールを更新
        
        Args:
            username (str): 更新対象のユーザー名
            profile_data (dict): 更新するプロフィールデータ
            requesting_user (str): 要求者のユーザー名
            requesting_role (str): 要求者の役割
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        if username not in self.users:
            return {'success': False, 'message': 'ユーザーが見つかりません'}
        
        # 権限チェック（自分自身または管理者のみ）
        if requesting_user != username and requesting_role != 'admin':
            return {'success': False, 'message': 'プロフィール更新権限がありません'}
        
        try:
            user_data = self.users[username]
            
            # 更新可能なフィールド
            updatable_fields = ['full_name', 'email', 'phone']
            profile_fields = ['department', 'license_number', 'specialization']
            
            # 基本情報更新
            for field in updatable_fields:
                if field in profile_data:
                    if field == 'email' and not self._validate_email(profile_data[field]):
                        return {'success': False, 'message': '無効なメールアドレス形式です'}
                    user_data[field] = profile_data[field]
            
            # プロフィール情報更新
            if 'profile' not in user_data:
                user_data['profile'] = {}
            
            for field in profile_fields:
                if field in profile_data:
                    user_data['profile'][field] = profile_data[field]
            
            self._save_users()
            
            return {'success': True, 'message': 'プロフィールが更新されました'}
            
        except Exception as e:
            return {'success': False, 'message': f'プロフィール更新中にエラーが発生しました: {str(e)}'}
    
    def deactivate_user(self, username, requesting_role):
        """
        ユーザーを無効化（管理者用）
        
        Args:
            username (str): 無効化するユーザー名
            requesting_role (str): 要求者の役割
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        if requesting_role != 'admin':
            return {'success': False, 'message': '管理者権限が必要です'}
        
        if username not in self.users:
            return {'success': False, 'message': 'ユーザーが見つかりません'}
        
        try:
            self.users[username]['is_active'] = False
            self._save_users()
            
            return {'success': True, 'message': f'ユーザー {username} が無効化されました'}
            
        except Exception as e:
            return {'success': False, 'message': f'ユーザー無効化中にエラーが発生しました: {str(e)}'}
    
    def reactivate_user(self, username, requesting_role):
        """
        ユーザーを再有効化（管理者用）
        
        Args:
            username (str): 再有効化するユーザー名
            requesting_role (str): 要求者の役割
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        if requesting_role != 'admin':
            return {'success': False, 'message': '管理者権限が必要です'}
        
        if username not in self.users:
            return {'success': False, 'message': 'ユーザーが見つかりません'}
        
        try:
            self.users[username]['is_active'] = True
            self.users[username]['failed_login_attempts'] = 0
            self.users[username]['account_locked_until'] = None
            self._save_users()
            
            return {'success': True, 'message': f'ユーザー {username} が再有効化されました'}
            
        except Exception as e:
            return {'success': False, 'message': f'ユーザー再有効化中にエラーが発生しました: {str(e)}'}

# デモ用
if __name__ == "__main__":
    manager = UserManager("test_user_db.json")
    
    # ユーザー登録テスト
    result = manager.register_user(
        username="test_doctor",
        password="SecurePass123!",
        email="doctor@hospital.com",
        role="doctor",
        full_name="田中太郎",
        phone="090-1234-5678"
    )
    print(f"ユーザー登録結果: {result}")
    
    # MFAセットアップテスト
    mfa_result = manager.setup_mfa("test_doctor")
    if mfa_result['success']:
        print(f"MFAセットアップ成功")
        print(f"バックアップコード: {mfa_result['backup_codes']}")
