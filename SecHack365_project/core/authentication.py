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
from io import BytesIO
import base64

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
        with open(self.user_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=4)

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
            "mfa_backup_codes": self._generate_backup_codes() if enable_mfa else None
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
        if mfa_code in backup_codes:
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