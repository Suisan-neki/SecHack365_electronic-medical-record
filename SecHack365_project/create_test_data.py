#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, '.')
sys.path.insert(0, 'core')

from core.authentication import UserAuthenticator
from core.data_encryption import DataEncryptor

def main():
    print("=== 患者データ作成 ===")
    
    auth = UserAuthenticator('info_sharing_system/app/user_db.json')
    username, password = 'doctor1', 'secure_pass_doc'
    
    salt = auth.get_user_encryption_salt(username)
    if not salt:
        print(f"[ERROR] ユーザー {username} のソルトが見つかりません")
        return False
    
    encryption_key = auth.derive_encryption_key(password, salt)
    print(f"[SUCCESS] 暗号化キー生成完了")
    
    patient_data = {
        'P001': {
            'patient_info': {'id': 'P001', 'name': '山下真凜', 'age': 28, 'gender': '女性', 'contact': '03-1234-5678', 'address': '東京都渋谷区'},
            'medical_records': [
                {'timestamp': '2024-01-15T10:30:00Z', 'data': {'diagnosis': '軽度の貧血', 'medication': '鉄剤 100mg', 'notes': '食事指導を実施。1ヶ月後に再検査予定。', 'doctor': 'Dr. 田中', 'blood_pressure': '120/80', 'temperature': '36.5°C'}, 'signature': 'yamashita_signature_1'},
                {'timestamp': '2024-01-10T14:00:00Z', 'data': {'diagnosis': '定期健診', 'medication': 'なし', 'notes': '全体的に健康状態は良好。軽度の貧血が見つかったため経過観察。', 'doctor': 'Dr. 佐藤', 'blood_pressure': '118/78', 'temperature': '36.3°C'}, 'signature': 'yamashita_signature_2'}
            ]
        }
    }
    
    encryptor = DataEncryptor(encryption_key)
    encrypted_data = encryptor.encrypt_json(patient_data)
    
    encrypted_content = {
        'encrypted_data': encrypted_data,
        'encryption_info': encryptor.get_encryption_info(),
        'last_updated': datetime.now().isoformat(),
        'version': '1.0',
        'created_by': username,
        'encryption_method': 'password_based'
    }
    
    output_file = 'info_sharing_system/app/demo_karte_encrypted.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(encrypted_content, f, ensure_ascii=False, indent=4)
    
    print(f"[SUCCESS] データ保存: {output_file}\n患者ID: P001 | 患者名: 山下真凜 | 診断記録: 2件")
    
    try:
        test_decrypted = encryptor.decrypt_json(encrypted_data)
        if test_decrypted == patient_data:
            print("[SUCCESS] 復号テスト成功")
            return True
        else:
            print("[ERROR] 復号テスト失敗 - データ不一致")
            return False
    except Exception as e:
        print(f"[ERROR] 復号テスト失敗: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print("\n✅ 患者データ作成完了" if success else "\n❌ 患者データ作成失敗")
    input("\nEnterキーを押して終了...")
