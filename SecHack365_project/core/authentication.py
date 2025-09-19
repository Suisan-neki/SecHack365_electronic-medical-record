#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SecHack365 患者中心の医療DXプロジェクト
認証モジュール（MFA対応版） - ユーザー登録・認証・多要素認証・役割管理

このモジュールは、セキュアなパスワードハッシュ化（PBKDF2）と
役割ベースアクセス制御（RBAC）、そしてTOTPベースのMFA機能を提供します。
"""

import hashlib
import os
import json
import pyotp  # TOTP（Time-based One-Time Password）ライブラリ
import qrcode  # QRコード生成用（オプション）
from webauthn import generate_registration_options, verify_registration_response, generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria, 
    UserVerificationRequirement, 
    RegistrationCredential, 
    AuthenticationCredential,
    AuthenticatorAttestationResponse,
    AuthenticatorAssertionResponse
)
import base64
from io import BytesIO

class UserAuthenticator:
    """
    ユーザー認証クラス（MFA対応版）
    
    セキュリティ機能:
    - PBKDF2-HMAC-SHA256によるパスワードハッシュ化
    - ランダムソルトによるレインボーテーブル攻撃対策
    - TOTP（Time-based One-Time Password）によるMFA
    - 役割ベースアクセス制御（医師、患者、管理者）
    """
    
    def __init__(self, user_db_path="user_db.json"):
        """
        認証システムの初期化
        
        Args:
            user_db_path (str): ユーザーデータベースファイルのパス
        """
        self.user_db_path = user_db_path
        self.users = self._load_users()
        
        # WebAuthn設定
        self.rp_id = "localhost"  # Relying Party ID（本番環境では実際のドメイン）
        self.rp_name = "SecHack365 PHR System"
        self.origin = "https://localhost:5000"

    def _load_users(self):
        """
        ユーザーデータベースを読み込む
        実際の本番環境ではセキュアなデータベース（PostgreSQL等）を使用すべき
        
        Returns:
            dict: ユーザーデータ辞書
        """
        if os.path.exists(self.user_db_path):
            with open(self.user_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_users(self):
        """
        ユーザーデータベースを保存する
        """
        print(f"[DEBUG] 保存先パス: {self.user_db_path}")
        print(f"[DEBUG] 保存前のusersデータ: {json.dumps(self.users, ensure_ascii=False, indent=2)}")
        
        with open(self.user_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=4)
        
        print(f"[DEBUG] ファイル保存完了")

    def hash_password(self, password, salt=None):
        """
        PBKDF2-HMAC-SHA256を使用してパスワードをハッシュ化
        
        Args:
            password (str): 平文パスワード
            salt (str, optional): 既存のソルト（16進数文字列）
            
        Returns:
            tuple: (ハッシュ化されたパスワード, ソルト)
        """
        if salt is None:
            salt = os.urandom(16)  # 16バイトのランダムなソルトを生成
        else:
            salt = bytes.fromhex(salt)
        
        # PBKDF2-HMAC-SHA256でハッシュ化（100,000回イテレーション）
        hashed_password = hashlib.pbkdf2_hmac(
            'sha256',  # ハッシュアルゴリズム
            password.encode('utf-8'),  # パスワードをバイト列にエンコード
            salt,  # ソルト
            100000  # イテレーション回数（NIST推奨値）
        ).hex()
        return hashed_password, salt.hex()

    def register_user(self, username, password, role="user", enable_mfa=False):
        """
        新しいユーザーを登録（MFA対応）
        
        Args:
            username (str): ユーザー名
            password (str): パスワード
            role (str): 役割（doctor, nurse, patient, admin等）
            enable_mfa (bool): MFA（多要素認証）を有効にするか
            
        Returns:
            tuple: (成功フラグ, メッセージ, MFAシークレット)
        """
        if username in self.users:
            return False, "ユーザーは既に存在します", None
        
        # パスワードの強度チェック（基本的なもの）
        if len(password) < 8:
            return False, "パスワードは8文字以上である必要があります", None
        
        hashed_password, salt = self.hash_password(password)
        
        # MFAが有効な場合、TOTPシークレットを生成
        mfa_secret = pyotp.random_base32() if enable_mfa else None
        
        self.users[username] = {
            "password": hashed_password,
            "salt": salt,
            "role": role,
            "mfa_enabled": enable_mfa,
            "mfa_secret": mfa_secret,
            "created_at": json.dumps({"timestamp": "auto-generated"}, default=str),
            "last_login": None,
            "mfa_backup_codes": self._generate_backup_codes() if enable_mfa else None,
            "webauthn_credentials": [],  # WebAuthn認証器情報
            "webauthn_challenges": {}    # WebAuthnチャレンジ情報
        }
        self._save_users()
        
        return True, "ユーザー登録に成功しました", mfa_secret

    def authenticate_user(self, username, password):
        """
        ユーザー認証を実行（MFA対応）
        
        Args:
            username (str): ユーザー名
            password (str): パスワード
            
        Returns:
            tuple: (認証成功フラグ, メッセージ, MFA必要フラグ)
        """
        user_data = self.users.get(username)
        if not user_data:
            return False, "ユーザーが見つかりません", False
        
        # パスワードを検証
        hashed_password_attempt, _ = self.hash_password(password, user_data["salt"])
        if hashed_password_attempt == user_data["password"]:
            if user_data.get("mfa_enabled", False):
                return True, "MFAが必要です", True  # 認証成功、MFAが必要
            else:
                # 最終ログイン時刻を更新
                self.users[username]["last_login"] = json.dumps({"timestamp": "auto-generated"}, default=str)
                self._save_users()
                return True, "認証成功", False  # 認証成功、MFA不要
        else:
            return False, "パスワードが間違っています", False

    def verify_mfa(self, username, mfa_code):
        """
        MFA（TOTP）コードを検証
        
        Args:
            username (str): ユーザー名
            mfa_code (str): 6桁のTOTPコード
            
        Returns:
            tuple: (検証成功フラグ, メッセージ)
        """
        user_data = self.users.get(username)
        if not user_data or not user_data.get("mfa_enabled", False):
            return False, "MFAが有効ではありません"
        
        # TOTPコードの検証
        totp = pyotp.TOTP(user_data["mfa_secret"])
        if totp.verify(mfa_code, valid_window=1):  # 前後30秒の時間窓を許可
            # 最終ログイン時刻を更新
            self.users[username]["last_login"] = json.dumps({"timestamp": "auto-generated"}, default=str)
            self._save_users()
            return True, "MFA認証成功"
        
        # バックアップコードの確認
        backup_codes = user_data.get("mfa_backup_codes", [])
        print(f"[DEBUG] 入力されたMFAコード: '{mfa_code}' (型: {type(mfa_code)})")
        print(f"[DEBUG] バックアップコード: {backup_codes}")
        print(f"[DEBUG] バックアップコードの型: {[type(code) for code in backup_codes]}")
        
        # 文字列として比較
        if str(mfa_code) in [str(code) for code in backup_codes]:
            # 使用されたバックアップコードを削除
            backup_codes.remove(mfa_code)
            self.users[username]["mfa_backup_codes"] = backup_codes
            self.users[username]["last_login"] = json.dumps({"timestamp": "auto-generated"}, default=str)
            self._save_users()
            return True, "バックアップコードによる認証成功"
        
        return False, "MFAコードが間違っています"

    def get_user_role(self, username):
        """
        ユーザーの役割を取得
        
        Args:
            username (str): ユーザー名
            
        Returns:
            str: 役割名（存在しない場合はNone）
        """
        return self.users.get(username, {}).get("role")
    
    def get_mfa_status(self, username):
        """
        ユーザーのMFA状態を取得
        
        Args:
            username (str): ユーザー名
            
        Returns:
            tuple: (MFA有効フラグ, MFAシークレット)
        """
        user_data = self.users.get(username)
        if user_data:
            return user_data.get("mfa_enabled", False), user_data.get("mfa_secret")
        return False, None
    
    def generate_mfa_qr_code(self, username, issuer_name="SecHack365 Medical DX"):
        """
        MFA設定用のQRコードを生成
        
        Args:
            username (str): ユーザー名
            issuer_name (str): 発行者名
            
        Returns:
            str: Base64エンコードされたQRコード画像
        """
        user_data = self.users.get(username)
        if not user_data or not user_data.get("mfa_enabled", False):
            return None
        
        # TOTP URIを生成
        totp = pyotp.TOTP(user_data["mfa_secret"])
        provisioning_uri = totp.provisioning_uri(
            name=username,
            issuer_name=issuer_name
        )
        
        # QRコードを生成
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # 画像をBase64エンコード
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def _generate_backup_codes(self, count=8):
        """
        MFA用のバックアップコードを生成
        
        Args:
            count (int): 生成するバックアップコードの数
            
        Returns:
            list: バックアップコードのリスト
        """
        backup_codes = []
        for _ in range(count):
            # 8桁のランダムなバックアップコードを生成
            code = ''.join([str(os.urandom(1)[0] % 10) for _ in range(8)])
            backup_codes.append(code)
        return backup_codes
    
    # WebAuthn関連のメソッド
    def generate_webauthn_registration_options(self, username):
        """
        WebAuthn認証器登録のためのオプションを生成
        
        Args:
            username (str): ユーザー名
            
        Returns:
            dict: 登録オプション（チャレンジ、ユーザー情報など）
        """
        user_data = self.users.get(username)
        if not user_data:
            return None
            
        # ユーザーIDをバイト形式で生成（既存のユーザーには一意なIDを割り当て）
        user_id = hashlib.sha256(username.encode()).digest()[:32]
        
        try:
            registration_options = generate_registration_options(
                rp_id=self.rp_id,
                rp_name=self.rp_name,
                user_id=user_id,
                user_name=username,
                user_display_name=f"{username} ({user_data.get('role', 'user')})",
                authenticator_selection=AuthenticatorSelectionCriteria(
                    user_verification=UserVerificationRequirement.PREFERRED
                )
            )
            
            # チャレンジをセッション用に保存（実際の実装ではRedisやデータベースを使用）
            if 'webauthn_challenges' not in user_data:
                user_data['webauthn_challenges'] = {}
            user_data['webauthn_challenges']['registration'] = base64.urlsafe_b64encode(registration_options.challenge).decode()
            self._save_users()
            
            return {
                'challenge': base64.urlsafe_b64encode(registration_options.challenge).decode(),
                'rp': {
                    'name': registration_options.rp.name,
                    'id': registration_options.rp.id
                },
                'user': {
                    'id': base64.urlsafe_b64encode(registration_options.user.id).decode(),
                    'name': registration_options.user.name,
                    'displayName': registration_options.user.display_name
                },
                'pubKeyCredParams': [{'alg': param.alg, 'type': param.type} for param in registration_options.pub_key_cred_params],
                'timeout': registration_options.timeout,
                'attestation': registration_options.attestation,
                'authenticatorSelection': {
                    'userVerification': registration_options.authenticator_selection.user_verification
                }
            }
        except Exception as e:
            print(f"WebAuthn登録オプション生成エラー: {e}")
            return None
    
    def verify_webauthn_registration_response(self, username, registration_response, challenge):
        """
        WebAuthn認証器登録レスポンスを検証
        
        Args:
            username (str): ユーザー名
            registration_response (dict): フロントエンドからの登録レスポンス
            challenge (str): 登録時のチャレンジ
            
        Returns:
            tuple: (成功フラグ, メッセージ)
        """
        user_data = self.users.get(username)
        if not user_data:
            return False, "ユーザーが見つかりません"
            
        try:
            # チャレンジの検証
            stored_challenge = user_data.get('webauthn_challenges', {}).get('registration')
            if not stored_challenge or stored_challenge != challenge:
                return False, "無効なチャレンジです"
            
            # Base64パディングを修正する関数
            def fix_base64_padding(data):
                missing_padding = len(data) % 4
                if missing_padding:
                    data += '=' * (4 - missing_padding)
                return data
            
            # RegistrationCredentialオブジェクトを作成
            from webauthn.helpers.structs import AuthenticatorAttestationResponse
            
            attestation_response = AuthenticatorAttestationResponse(
                client_data_json=base64.urlsafe_b64decode(fix_base64_padding(registration_response['response']['clientDataJSON'])),
                attestation_object=base64.urlsafe_b64decode(fix_base64_padding(registration_response['response']['attestationObject']))
            )
            
            credential = RegistrationCredential(
                id=registration_response['id'],
                raw_id=base64.urlsafe_b64decode(fix_base64_padding(registration_response['rawId'])),
                response=attestation_response,
                type=registration_response['type']
            )
            
            # 登録レスポンスを検証
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=base64.urlsafe_b64decode(challenge),
                expected_origin=self.origin,
                expected_rp_id=self.rp_id
            )
            
            # verification オブジェクトの属性を確認
            print(f"[DEBUG] verification object attributes: {dir(verification)}")
            print(f"[DEBUG] verification object: {verification}")
            
            # VerifiedRegistrationオブジェクトが返された場合、検証は成功
            # エラーが発生した場合は例外がスローされる
            if hasattr(verification, 'credential_id'):
                print(f"[DEBUG] WebAuthn登録処理開始")
                
                # 認証器情報をユーザーデータに保存
                if 'webauthn_credentials' not in user_data:
                    user_data['webauthn_credentials'] = []
                    print(f"[DEBUG] webauthn_credentials フィールドを初期化")
                
                credential_data = {
                    'credential_id': base64.urlsafe_b64encode(verification.credential_id).decode(),
                    'public_key': base64.urlsafe_b64encode(verification.credential_public_key).decode(),
                    'sign_count': verification.sign_count,
                    'created_at': json.dumps({"timestamp": "auto-generated"}, default=str)
                }
                
                print(f"[DEBUG] credential_data作成: {credential_data}")
                
                user_data['webauthn_credentials'].append(credential_data)
                print(f"[DEBUG] webauthn_credentials追加後: {len(user_data['webauthn_credentials'])}個")
                
                # チャレンジを削除
                if 'webauthn_challenges' in user_data:
                    user_data['webauthn_challenges'].pop('registration', None)
                    print(f"[DEBUG] registrationチャレンジを削除")
                
                print(f"[DEBUG] _save_users()実行前")
                self._save_users()
                print(f"[DEBUG] _save_users()実行後")
                
                return True, "WebAuthn認証器の登録が成功しました"
            else:
                return False, "WebAuthn登録の検証に失敗しました"
                
        except Exception as e:
            print(f"WebAuthn登録検証エラー: {e}")
            return False, f"登録検証中にエラーが発生しました: {str(e)}"
    
    def generate_webauthn_authentication_options(self, username):
        """
        WebAuthn認証のためのオプションを生成
        
        Args:
            username (str): ユーザー名
            
        Returns:
            dict: 認証オプション（チャレンジ、許可される認証器など）
        """
        user_data = self.users.get(username)
        if not user_data or not user_data.get('webauthn_credentials'):
            return None
            
        try:
            # 登録済み認証器のCredential IDを取得
            allow_credentials = []
            for cred in user_data['webauthn_credentials']:
                allow_credentials.append({
                    'type': 'public-key',
                    'id': cred['credential_id']
                })
            
            authentication_options = generate_authentication_options(
                rp_id=self.rp_id,
                allow_credentials=[
                    {'type': 'public-key', 'id': base64.urlsafe_b64decode(cred['credential_id'])}
                    for cred in user_data['webauthn_credentials']
                ],
                user_verification=UserVerificationRequirement.PREFERRED
            )
            
            # チャレンジをセッション用に保存
            if 'webauthn_challenges' not in user_data:
                user_data['webauthn_challenges'] = {}
            user_data['webauthn_challenges']['authentication'] = base64.urlsafe_b64encode(authentication_options.challenge).decode()
            self._save_users()
            
            return {
                'challenge': base64.urlsafe_b64encode(authentication_options.challenge).decode(),
                'timeout': authentication_options.timeout,
                'rpId': authentication_options.rp_id,
                'allowCredentials': [
                    {
                        'type': 'public-key',
                        'id': cred['credential_id']
                    } for cred in user_data['webauthn_credentials']
                ],
                'userVerification': authentication_options.user_verification
            }
            
        except Exception as e:
            print(f"WebAuthn認証オプション生成エラー: {e}")
            return None
    
    def verify_webauthn_authentication_response(self, username, authentication_response, challenge):
        """
        WebAuthn認証レスポンスを検証
        
        Args:
            username (str): ユーザー名
            authentication_response (dict): フロントエンドからの認証レスポンス
            challenge (str): 認証時のチャレンジ
            
        Returns:
            tuple: (成功フラグ, メッセージ)
        """
        user_data = self.users.get(username)
        if not user_data or not user_data.get('webauthn_credentials'):
            return False, "WebAuthn認証器が登録されていません"
            
        try:
            # チャレンジの検証
            stored_challenge = user_data.get('webauthn_challenges', {}).get('authentication')
            if not stored_challenge or stored_challenge != challenge:
                return False, "無効なチャレンジです"
            
            # 使用された認証器を特定
            credential_id = authentication_response['rawId']
            print(f"[DEBUG] 認証で使用されたcredential_id: {credential_id}")
            print(f"[DEBUG] 登録済みのcredential_ids: {[cred['credential_id'] for cred in user_data['webauthn_credentials']]}")
            
            # Base64パディングを正規化する関数
            def normalize_base64(data):
                # パディングを追加
                missing_padding = len(data) % 4
                if missing_padding:
                    data += '=' * (4 - missing_padding)
                return data
            
            # credential_idを正規化
            normalized_credential_id = normalize_base64(credential_id)
            print(f"[DEBUG] 正規化されたcredential_id: {normalized_credential_id}")
            
            matching_credential = None
            for cred in user_data['webauthn_credentials']:
                if cred['credential_id'] == normalized_credential_id:
                    matching_credential = cred
                    break
            
            if not matching_credential:
                print(f"[DEBUG] 認証器が見つかりません - 使用されたID: {credential_id}")
                return False, "認証器が見つかりません"
            
            print(f"[DEBUG] マッチした認証器: {matching_credential}")
            
            # Base64パディングを修正する関数
            def fix_base64_padding(data):
                missing_padding = len(data) % 4
                if missing_padding:
                    data += '=' * (4 - missing_padding)
                return data
            
            # AuthenticationCredentialオブジェクトを作成
            from webauthn.helpers.structs import AuthenticatorAssertionResponse
            
            assertion_response = AuthenticatorAssertionResponse(
                client_data_json=base64.urlsafe_b64decode(fix_base64_padding(authentication_response['response']['clientDataJSON'])),
                authenticator_data=base64.urlsafe_b64decode(fix_base64_padding(authentication_response['response']['authenticatorData'])),
                signature=base64.urlsafe_b64decode(fix_base64_padding(authentication_response['response']['signature']))
            )
            
            credential = AuthenticationCredential(
                id=authentication_response['id'],
                raw_id=base64.urlsafe_b64decode(fix_base64_padding(authentication_response['rawId'])),
                response=assertion_response,
                type=authentication_response['type']
            )
            
            # 認証レスポンスを検証
            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=base64.urlsafe_b64decode(challenge),
                expected_origin=self.origin,
                expected_rp_id=self.rp_id,
                credential_public_key=base64.urlsafe_b64decode(matching_credential['public_key']),
                credential_current_sign_count=matching_credential['sign_count']
            )
            
            # verification オブジェクトの属性を確認
            print(f"[DEBUG] auth verification object attributes: {dir(verification)}")
            print(f"[DEBUG] auth verification object: {verification}")
            
            # VerifiedAuthenticationオブジェクトが返された場合、検証は成功
            # エラーが発生した場合は例外がスローされる
            if hasattr(verification, 'new_sign_count'):
                # サインカウントを更新
                new_sign_count = getattr(verification, 'new_sign_count', matching_credential['sign_count'])
                matching_credential['sign_count'] = new_sign_count
                
                # チャレンジを削除
                if 'webauthn_challenges' in user_data:
                    user_data['webauthn_challenges'].pop('authentication', None)
                
                # 最終ログイン時刻を更新
                user_data['last_login'] = json.dumps({"timestamp": "auto-generated"}, default=str)
                
                self._save_users()
                return True, "WebAuthn認証が成功しました"
            else:
                return False, "WebAuthn認証の検証に失敗しました"
                
        except Exception as e:
            print(f"WebAuthn認証検証エラー: {e}")
            return False, f"認証検証中にエラーが発生しました: {str(e)}"
    
    def get_user_info(self, username):
        """
        ユーザーの詳細情報を取得（セキュア版）
        
        Args:
            username (str): ユーザー名
            
        Returns:
            dict: ユーザー情報（パスワードとMFAシークレットは除外）
        """
        user_data = self.users.get(username)
        if not user_data:
            return None
        
        # セキュリティのためパスワードとMFAシークレットを除外
        safe_user_data = {
            "username": username,
            "role": user_data.get("role"),
            "mfa_enabled": user_data.get("mfa_enabled", False),
            "backup_codes_remaining": len(user_data.get("mfa_backup_codes", [])),
            "created_at": user_data.get("created_at"),
            "last_login": user_data.get("last_login")
        }
        return safe_user_data
    
    def enable_mfa_for_user(self, username):
        """
        既存ユーザーのMFAを有効化
        
        Args:
            username (str): ユーザー名
            
        Returns:
            tuple: (成功フラグ, メッセージ, MFAシークレット)
        """
        if username not in self.users:
            return False, "ユーザーが見つかりません", None
        
        if self.users[username].get("mfa_enabled", False):
            return False, "MFAは既に有効です", None
        
        # MFAシークレットとバックアップコードを生成
        mfa_secret = pyotp.random_base32()
        backup_codes = self._generate_backup_codes()
        
        self.users[username]["mfa_enabled"] = True
        self.users[username]["mfa_secret"] = mfa_secret
        self.users[username]["mfa_backup_codes"] = backup_codes
        self._save_users()
        
        return True, "MFAが有効化されました", mfa_secret
    
    def disable_mfa_for_user(self, username):
        """
        既存ユーザーのMFAを無効化
        
        Args:
            username (str): ユーザー名
            
        Returns:
            tuple: (成功フラグ, メッセージ)
        """
        if username not in self.users:
            return False, "ユーザーが見つかりません"
        
        self.users[username]["mfa_enabled"] = False
        self.users[username]["mfa_secret"] = None
        self.users[username]["mfa_backup_codes"] = None
        self._save_users()
        
        return True, "MFAが無効化されました"


# デモ用実行部分
if __name__ == "__main__":
    print("SecHack365 認証システム（MFA対応版） - デモンストレーション")
    print("=" * 60)
    
    # 既存のuser_db.jsonを削除してクリーンな状態にする
    if os.path.exists("user_db.json"):
        os.remove("user_db.json")
        print("[INFO] 既存のユーザーデータベースを削除しました")

    authenticator = UserAuthenticator("user_db.json")

    # ユーザー登録のデモ（MFA有効なユーザーと無効なユーザー）
    print("\n[1] ユーザー登録テスト（MFA対応）")
    print("-" * 40)
    
    # MFA有効なユーザー
    success, message, mfa_secret = authenticator.register_user("doctor1", "secure_pass_doc", "doctor", enable_mfa=True)
    print(f"登録結果 (doctor1, MFA有効): {message}")
    if mfa_secret:
        print(f"  MFAシークレット: {mfa_secret}")
    
    # MFA無効なユーザー
    success, message, mfa_secret = authenticator.register_user("patient1", "secure_pass_pat", "patient", enable_mfa=False)
    print(f"登録結果 (patient1, MFA無効): {message}")

    # 認証テストのデモ
    print("\n[2] 認証テスト（MFA対応）")
    print("-" * 40)
    
    # MFA有効ユーザーの認証
    auth_success, auth_message, mfa_required = authenticator.authenticate_user("doctor1", "secure_pass_doc")
    print(f"認証結果 (doctor1): {auth_message}, MFA必要: {mfa_required}")
    
    if mfa_required:
        # 実際のTOTPコードを生成（デモ用）
        totp = pyotp.TOTP(authenticator.users["doctor1"]["mfa_secret"])
        mfa_code = totp.now()
        print(f"  生成されたTOTPコード: {mfa_code}")
        
        mfa_verified, mfa_message = authenticator.verify_mfa("doctor1", mfa_code)
        print(f"  MFA検証結果: {mfa_message}")

    # MFA無効ユーザーの認証
    auth_success, auth_message, mfa_required = authenticator.authenticate_user("patient1", "secure_pass_pat")
    print(f"認証結果 (patient1): {auth_message}, MFA必要: {mfa_required}")

    # 認証失敗のテスト
    auth_success, auth_message, mfa_required = authenticator.authenticate_user("patient1", "wrong_pass")
    print(f"認証結果 (patient1, 間違ったパスワード): {auth_message}")

    # MFA状態の確認
    print("\n[3] MFA状態確認")
    print("-" * 40)
    
    mfa_enabled, mfa_secret = authenticator.get_mfa_status("doctor1")
    print(f"doctor1のMFA状態: 有効={mfa_enabled}")
    
    mfa_enabled, mfa_secret = authenticator.get_mfa_status("patient1")
    print(f"patient1のMFA状態: 有効={mfa_enabled}")

    # ユーザー情報の取得
    print("\n[4] ユーザー情報取得（セキュア）")
    print("-" * 40)
    
    user_info = authenticator.get_user_info("doctor1")
    if user_info:
        print("doctor1の情報:")
        for key, value in user_info.items():
            print(f"  {key}: {value}")

    # バックアップコードのテスト
    print("\n[5] バックアップコード認証テスト")
    print("-" * 40)
    
    backup_codes = authenticator.users["doctor1"]["mfa_backup_codes"]
    if backup_codes:
        test_backup_code = backup_codes[0]
        print(f"テスト用バックアップコード: {test_backup_code}")
        
        backup_verified, backup_message = authenticator.verify_mfa("doctor1", test_backup_code)
        print(f"バックアップコード検証結果: {backup_message}")

    # ユーザーデータベースの内容を確認
    print("\n[6] ユーザーデータベースの内容")
    print("-" * 40)
    
    with open("user_db.json", "r", encoding="utf-8") as f:
        db_content = json.load(f)
        print("User Database Structure (MFA対応):")
        for username, user_data in db_content.items():
            print(f"  {username}:")
            print(f"    role: {user_data['role']}")
            print(f"    mfa_enabled: {user_data.get('mfa_enabled', False)}")
            print(f"    backup_codes_count: {len(user_data.get('mfa_backup_codes', []))}")
            print(f"    password_hash: {user_data['password'][:20]}...")
    
    print("\n[SUCCESS] MFA対応認証システムのデモが完了しました")
    print("[INFO] 本番環境では以下を実装してください:")
    print("  - セキュアなデータベース（PostgreSQL等）")
    print("  - QRコード表示機能")
    print("  - MFAアプリとの連携（Google Authenticator等）")
    print("  - バックアップコードの安全な管理")