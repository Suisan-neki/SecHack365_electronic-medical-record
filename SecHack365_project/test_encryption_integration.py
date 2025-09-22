#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SecHack365 暗号化機能統合テスト
"""

import os
import json
from core.authentication import UserAuthenticator
from core.data_encryption import DataEncryptor

def test_encryption_integration():
    print("=" * 60)
    print("SecHack365 暗号化機能統合テスト")
    print("=" * 60)
    
    # テスト用のuser_db.jsonを削除（クリーンな状態でテスト）
    test_db_path = "test_user_db.json"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # UserAuthenticatorを初期化
    auth = UserAuthenticator(test_db_path)
    
    print("\n[1] ユーザー登録テスト")
    print("-" * 40)
    
    # テストユーザーを登録
    success, message, mfa_secret = auth.register_user(
        username="test_doctor",
        password="test_password_123",
        role="doctor",
        enable_mfa=False
    )
    
    print(f"ユーザー登録結果: {success}")
    print(f"メッセージ: {message}")
    
    if not success:
        print("❌ ユーザー登録に失敗しました")
        return False
    
    print("\n[2] 暗号化キー導出テスト")
    print("-" * 40)
    
    # ソルトを取得
    salt = auth.get_user_encryption_salt("test_doctor")
    print(f"ソルト取得: {'✅ 成功' if salt else '❌ 失敗'}")
    
    if not salt:
        print("❌ ソルトが取得できませんでした")
        return False
    
    # 暗号化キーを導出
    encryption_key = auth.derive_encryption_key("test_password_123", salt)
    print(f"暗号化キー長: {len(encryption_key)}バイト")
    print(f"暗号化キー導出: {'✅ 成功 (32バイト)' if len(encryption_key) == 32 else '❌ 失敗'}")
    
    if len(encryption_key) != 32:
        print("❌ 暗号化キーの長さが正しくありません")
        return False
    
    print("\n[3] データ暗号化・復号テスト")
    print("-" * 40)
    
    # DataEncryptorを初期化
    encryptor = DataEncryptor(encryption_key)
    
    # テストデータ
    test_data = {
        "patient_id": "P001",
        "name": "テスト太郎",
        "diagnosis": "高血圧症",
        "medication": "アムロジピン 5mg",
        "notes": "定期検査で血圧値改善を確認。継続治療が必要。",
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    print("元データ:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    try:
        # データを暗号化
        encrypted_data = encryptor.encrypt_json(test_data)
        print(f"\n暗号化完了:")
        print(f"  暗号化データ長: {len(encrypted_data)}文字")
        print(f"  暗号化データ（先頭50文字）: {encrypted_data[:50]}...")
        
        # データを復号
        decrypted_data = encryptor.decrypt_json(encrypted_data)
        print(f"\n復号完了:")
        
        # データ整合性確認
        data_match = test_data == decrypted_data
        print(f"データ整合性: {'✅ 一致' if data_match else '❌ 不一致'}")
        
        if not data_match:
            print("❌ 暗号化・復号後のデータが一致しません")
            return False
            
    except Exception as e:
        print(f"❌ 暗号化・復号エラー: {e}")
        return False
    
    print("\n[4] 認証テスト")
    print("-" * 40)
    
    # パスワード認証テスト
    authenticated, auth_message, mfa_required = auth.authenticate_user("test_doctor", "test_password_123")
    print(f"認証結果: {'✅ 成功' if authenticated else '❌ 失敗'}")
    print(f"メッセージ: {auth_message}")
    print(f"MFA必要: {mfa_required}")
    
    if not authenticated:
        print("❌ 認証に失敗しました")
        return False
    
    print("\n[5] Flaskアプリケーション統合テスト準備")
    print("-" * 40)
    
    # app.pyで使用される暗号化データファイルのテスト
    encrypted_file_path = "info_sharing_system/app/demo_karte_encrypted.json"
    
    # テスト用の患者データ
    karte_test_data = {
        "P001": {
            "patient_info": {
                "id": "P001",
                "name": "テスト太郎",
                "age": 45,
                "gender": "男性"
            },
            "medical_records": [
                {
                    "timestamp": "2024-01-15T10:30:00Z",
                    "data": {
                        "diagnosis": "高血圧症",
                        "medication": "アムロジピン 5mg",
                        "notes": "定期検査で血圧値改善を確認"
                    },
                    "signature": "dummy_signature_for_test"
                }
            ]
        }
    }
    
    try:
        # 暗号化してファイルに保存
        encrypted_karte_data = encryptor.encrypt_json(karte_test_data)
        
        # 暗号化データとメタデータを保存
        encrypted_content = {
            "encrypted_data": encrypted_karte_data,
            "encryption_info": encryptor.get_encryption_info(),
            "last_updated": "2024-01-15T10:30:00Z",
            "version": "1.0"
        }
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(encrypted_file_path), exist_ok=True)
        
        with open(encrypted_file_path, 'w', encoding='utf-8') as f:
            json.dump(encrypted_content, f, ensure_ascii=False, indent=4)
        
        print(f"✅ テスト用暗号化ファイル作成: {encrypted_file_path}")
        
        # 読み込みテスト
        with open(encrypted_file_path, 'r', encoding='utf-8') as f:
            loaded_content = json.load(f)
        
        decrypted_karte_data = encryptor.decrypt_json(loaded_content["encrypted_data"])
        
        karte_match = karte_test_data == decrypted_karte_data
        print(f"ファイル暗号化・復号: {'✅ 成功' if karte_match else '❌ 失敗'}")
        
        if not karte_match:
            print("❌ ファイル暗号化・復号後のデータが一致しません")
            return False
            
    except Exception as e:
        print(f"❌ ファイル暗号化・復号エラー: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 全ての暗号化機能統合テストが成功しました！")
    print("=" * 60)
    
    print("\n✅ テスト結果サマリー:")
    print("  - ユーザー登録: 正常")
    print("  - 暗号化キー導出: 正常 (32バイト AES-256)")
    print("  - データ暗号化・復号: 正常")
    print("  - 認証機能: 正常")
    print("  - ファイル暗号化・復号: 正常")
    
    print("\n📋 次のステップ:")
    print("  1. Flaskアプリケーションを起動: python info_sharing_system/run_app.py")
    print("  2. ブラウザで https://localhost:5000 にアクセス")
    print("  3. test_doctor / test_password_123 でログイン")
    print("  4. 患者データの閲覧・追加をテスト")
    
    # テストファイルをクリーンアップ
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"\n🧹 テストファイルをクリーンアップ: {test_db_path}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_encryption_integration()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
