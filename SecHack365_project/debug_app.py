#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
アプリケーションデバッグスクリプト
"""

import sys
import os
import traceback

# パスを設定
project_root = os.path.dirname(os.path.abspath(__file__))
info_sharing_root = os.path.join(project_root, 'info_sharing_system')
sys.path.insert(0, project_root)
sys.path.insert(0, info_sharing_root)

print("=== アプリケーションデバッグ ===")
print(f"プロジェクトルート: {project_root}")
print(f"情報共有システムルート: {info_sharing_root}")

# 1. 基本的なインポートテスト
print("\n[1] 基本インポートテスト")
try:
    from flask import Flask
    print("✅ Flask インポート成功")
except Exception as e:
    print(f"❌ Flask インポート失敗: {e}")
    sys.exit(1)

try:
    from flask_login import LoginManager
    print("✅ Flask-Login インポート成功")
except Exception as e:
    print(f"❌ Flask-Login インポート失敗: {e}")

# 2. coreモジュールのインポートテスト
print("\n[2] coreモジュールインポートテスト")
try:
    from core.authentication import UserAuthenticator
    print("✅ UserAuthenticator インポート成功")
except Exception as e:
    print(f"❌ UserAuthenticator インポート失敗: {e}")
    traceback.print_exc()

try:
    from core.data_encryption import DataEncryptor
    print("✅ DataEncryptor インポート成功")
except Exception as e:
    print(f"❌ DataEncryptor インポート失敗: {e}")
    traceback.print_exc()

# 3. アプリケーションのインポートテスト
print("\n[3] アプリケーションインポートテスト")
try:
    from app.app import app
    print("✅ アプリケーション インポート成功")
    
    # ルート確認
    print("\n[4] 登録されているルート:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint} ({list(rule.methods)})")
    
    # テストクライアントでAPIテスト
    print("\n[5] APIテスト")
    with app.test_client() as client:
        response = client.get('/api/test')
        print(f"  /api/test -> {response.status_code}: {response.get_json()}")
        
        # 認証が必要なエンドポイントのテスト（認証なし）
        response = client.get('/api/patient/P001')
        print(f"  /api/patient/P001 (認証なし) -> {response.status_code}")
        
except Exception as e:
    print(f"❌ アプリケーション インポート失敗: {e}")
    traceback.print_exc()

# 4. ファイル存在確認
print("\n[6] 重要ファイル存在確認")
important_files = [
    'info_sharing_system/app/user_db.json',
    'info_sharing_system/app/demo_karte_encrypted.json',
    'info_sharing_system/app/webauthn_encryption_keys.json'
]

for file_path in important_files:
    full_path = os.path.join(project_root, file_path)
    if os.path.exists(full_path):
        print(f"✅ {file_path} 存在")
        # ファイルサイズも表示
        size = os.path.getsize(full_path)
        print(f"   サイズ: {size} bytes")
    else:
        print(f"❌ {file_path} 不存在")

print("\n=== デバッグ完了 ===")
