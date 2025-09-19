from functools import wraps
from flask import session, jsonify

def require_permission(required_permission):
    """
    権限が必要なエンドポイント用のデコレーター
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # セッションからトークンを取得
            token = session.get('auth_token')
            if not token:
                return jsonify({
                    "error": "認証が必要です",
                    "required_permission": required_permission,
                    "user_permission": None
                }), 401
            
            # ユーザーの権限を確認
            user_permissions = token['payload'].get('permissions', [])
            if required_permission not in user_permissions:
                return jsonify({
                    "error": f"権限が不足しています。必要な権限: {required_permission}",
                    "required_permission": required_permission,
                    "user_permissions": user_permissions,
                    "user_role": token['payload'].get('role', 'unknown')
                }), 403
            
            # 権限チェックに成功した場合、元の関数を実行
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_user_permissions():
    """現在のユーザーの権限を取得"""
    token = session.get('auth_token')
    if not token:
        return []
    return token['payload'].get('permissions', [])

def has_permission(permission):
    """特定の権限を持っているかチェック"""
    return permission in get_user_permissions()

def get_user_info():
    """現在のユーザー情報を取得"""
    token = session.get('auth_token')
    if not token:
        return None
    return token['payload']
