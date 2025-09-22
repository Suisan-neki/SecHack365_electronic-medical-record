"""
WebAuthn関連のヘルパー関数
"""
import json
import os

def has_webauthn_credentials(username, user_db_path):
    """
    ユーザーがWebAuthn認証器を登録しているかチェック
    """
    try:
        if not os.path.exists(user_db_path):
            return False
            
        with open(user_db_path, 'r', encoding='utf-8') as f:
            users = json.load(f)
            
        if username not in users:
            return False
            
        credentials = users[username].get('webauthn_credentials', [])
        return len(credentials) > 0
    except Exception as e:
        print(f"[ERROR] WebAuthn認証器確認エラー: {e}")
        return False

def get_webauthn_credentials(username, user_db_path):
    """
    ユーザーのWebAuthn認証器一覧を取得
    """
    try:
        if not os.path.exists(user_db_path):
            return []
            
        with open(user_db_path, 'r', encoding='utf-8') as f:
            users = json.load(f)
            
        if username not in users:
            return []
            
        return users[username].get('webauthn_credentials', [])
    except Exception as e:
        print(f"[ERROR] WebAuthn認証器取得エラー: {e}")
        return []
