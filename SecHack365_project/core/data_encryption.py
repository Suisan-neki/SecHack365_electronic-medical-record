#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SecHack365 患者中心の医療DXプロジェクト
データ暗号化モジュール - AES-256 GCM暗号化によるデータ保護

このモジュールは、医療データの機密性と完全性を保護するため、
AES-256 GCM（Galois/Counter Mode）を使用した認証付き暗号化を提供します。
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
import json

class DataEncryptor:
    """
    AES-256 GCM認証付き暗号化クラス
    
    セキュリティ機能:
    - AES-256暗号化による強力なデータ保護
    - GCM（Galois/Counter Mode）による認証付き暗号化
    - ランダムIV（初期化ベクトル）による攻撃耐性
    - 認証タグによる改ざん検知
    - Base64エンコードによる安全な文字列表現
    """
    
    def __init__(self, key):
        """
        DataEncryptorの初期化
        
        Args:
            key (bytes): AES暗号化鍵（16, 24, 32バイトのいずれか）
                        - 16バイト: AES-128
                        - 24バイト: AES-192  
                        - 32バイト: AES-256（推奨）
                        
        Raises:
            ValueError: 鍵の長さが無効な場合
        """
        if not isinstance(key, bytes):
            raise ValueError("暗号化鍵はbytes型である必要があります")
        
        if len(key) not in [16, 24, 32]:
            raise ValueError("AES鍵の長さは16, 24, 32バイトのいずれかである必要があります")
        
        self.key = key
        self.backend = default_backend()
        
        # 使用する暗号化レベルを表示
        key_sizes = {16: "AES-128", 24: "AES-192", 32: "AES-256"}
        self.encryption_type = key_sizes[len(key)]
        
    def encrypt(self, plaintext):
        """
        プレーンテキストをAES-GCMで暗号化
        
        Args:
            plaintext (str): 暗号化するプレーンテキスト
            
        Returns:
            str: Base64エンコードされた暗号化データ
                 形式: base64(IV + 認証タグ + 暗号文)
                 
        Raises:
            Exception: 暗号化処理中にエラーが発生した場合
        """
        try:
            # 12バイトのランダムなIV（初期化ベクトル）を生成
            # GCMモードでは12バイトのIVが推奨される
            iv = os.urandom(12)
            
            # AES-GCM暗号化オブジェクトを作成
            cipher = Cipher(
                algorithms.AES(self.key), 
                modes.GCM(iv), 
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            # プレーンテキストをUTF-8バイト列に変換
            plaintext_bytes = plaintext.encode("utf-8")
            
            # 暗号化を実行
            ciphertext = encryptor.update(plaintext_bytes) + encryptor.finalize()
            
            # 認証タグを取得（改ざん検知用）
            tag = encryptor.tag
            
            # IV + 認証タグ + 暗号文を結合してBase64エンコード
            encrypted_data = iv + tag + ciphertext
            return base64.b64encode(encrypted_data).decode("utf-8")
            
        except Exception as e:
            raise Exception(f"データ暗号化エラー: {str(e)}")

    def decrypt(self, encrypted_data):
        """
        AES-GCMで暗号化されたデータを復号
        
        Args:
            encrypted_data (str): Base64エンコードされた暗号化データ
            
        Returns:
            str: 復号されたプレーンテキスト
            
        Raises:
            Exception: 復号処理中にエラーが発生した場合（改ざん検知含む）
        """
        try:
            # Base64デコード
            decoded_data = base64.b64decode(encrypted_data)
            
            # データを分解: IV(12バイト) + 認証タグ(16バイト) + 暗号文
            if len(decoded_data) < 28:  # 12 + 16 = 28バイト未満はエラー
                raise ValueError("暗号化データが短すぎます")
                
            iv = decoded_data[:12]           # 初期化ベクトル
            tag = decoded_data[12:28]        # 認証タグ（16バイト）
            ciphertext = decoded_data[28:]   # 暗号文
            
            # AES-GCM復号オブジェクトを作成（認証タグ付き）
            cipher = Cipher(
                algorithms.AES(self.key), 
                modes.GCM(iv, tag), 
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            # 復号を実行（認証タグの検証も同時に行われる）
            plaintext_bytes = decryptor.update(ciphertext) + decryptor.finalize()
            
            # UTF-8文字列に変換して返す
            return plaintext_bytes.decode("utf-8")
            
        except Exception as e:
            raise Exception(f"データ復号エラー: {str(e)}")

    def encrypt_json(self, data_dict):
        """
        辞書データをJSON形式で暗号化
        
        Args:
            data_dict (dict): 暗号化する辞書データ
            
        Returns:
            str: 暗号化されたJSONデータ（Base64エンコード済み）
        """
        try:
            # 辞書をJSON文字列に変換
            json_string = json.dumps(data_dict, ensure_ascii=False, separators=(',', ':'))
            
            # JSON文字列を暗号化
            return self.encrypt(json_string)
            
        except Exception as e:
            raise Exception(f"JSON暗号化エラー: {str(e)}")

    def decrypt_json(self, encrypted_json):
        """
        暗号化されたJSONデータを復号して辞書に変換
        
        Args:
            encrypted_json (str): 暗号化されたJSONデータ
            
        Returns:
            dict: 復号された辞書データ
        """
        try:
            # 暗号化データを復号
            json_string = self.decrypt(encrypted_json)
            
            # JSON文字列を辞書に変換
            return json.loads(json_string)
            
        except Exception as e:
            raise Exception(f"JSON復号エラー: {str(e)}")

    def get_encryption_info(self):
        """
        使用中の暗号化情報を取得
        
        Returns:
            dict: 暗号化情報（アルゴリズム、鍵長など）
        """
        return {
            "algorithm": "AES",
            "mode": "GCM (Galois/Counter Mode)",
            "key_size": len(self.key) * 8,  # ビット単位
            "encryption_type": self.encryption_type,
            "features": [
                "認証付き暗号化",
                "改ざん検知",
                "ランダムIV",
                "Base64エンコード"
            ]
        }


# デモ用実行部分
if __name__ == "__main__":
    print("SecHack365 データ暗号化モジュール - デモンストレーション")
    print("=" * 60)
    
    # テスト用の32バイト鍵を生成（AES-256）
    test_key = os.urandom(32)
    print(f"[INFO] テスト用AES-256鍵を生成: {len(test_key)}バイト")
    
    # DataEncryptorを初期化
    encryptor = DataEncryptor(test_key)
    
    # 暗号化情報を表示
    print(f"\n[1] 暗号化情報")
    print("-" * 40)
    crypto_info = encryptor.get_encryption_info()
    for key, value in crypto_info.items():
        if isinstance(value, list):
            print(f"{key}: {', '.join(value)}")
        else:
            print(f"{key}: {value}")
    
    # テストデータの準備
    test_data = {
        "patient_id": "P001",
        "name": "山田太郎",
        "diagnosis": "高血圧症",
        "medication": "アムロジピン 5mg",
        "notes": "定期検査で血圧値改善を確認。継続治療が必要。",
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    print(f"\n[2] 医療データ暗号化テスト")
    print("-" * 40)
    print("元データ:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    # JSON暗号化テスト
    try:
        encrypted_data = encryptor.encrypt_json(test_data)
        print(f"\n暗号化完了:")
        print(f"  暗号化データ長: {len(encrypted_data)}文字")
        print(f"  暗号化データ（先頭50文字）: {encrypted_data[:50]}...")
        
        # 復号テスト
        decrypted_data = encryptor.decrypt_json(encrypted_data)
        print(f"\n復号完了:")
        print("復号データ:")
        for key, value in decrypted_data.items():
            print(f"  {key}: {value}")
        
        # データ整合性の確認
        data_match = test_data == decrypted_data
        print(f"\nデータ整合性: {'✓ 一致' if data_match else '✗ 不一致'}")
        
    except Exception as e:
        print(f"[ERROR] 暗号化テストエラー: {e}")
    
    # 文字列暗号化テスト
    print(f"\n[3] 文字列暗号化テスト")
    print("-" * 40)
    
    test_message = "これは機密の医療情報です。患者のプライバシーを保護する必要があります。"
    print(f"元メッセージ: {test_message}")
    
    try:
        encrypted_message = encryptor.encrypt(test_message)
        print(f"暗号化メッセージ: {encrypted_message[:50]}...")
        
        decrypted_message = encryptor.decrypt(encrypted_message)
        print(f"復号メッセージ: {decrypted_message}")
        
        message_match = test_message == decrypted_message
        print(f"メッセージ整合性: {'✓ 一致' if message_match else '✗ 不一致'}")
        
    except Exception as e:
        print(f"[ERROR] 文字列暗号化テストエラー: {e}")
    
    # 改ざん検知テスト
    print(f"\n[4] 改ざん検知テスト")
    print("-" * 40)
    
    try:
        # 正常な暗号化データ
        original_encrypted = encryptor.encrypt("正常なデータ")
        
        # 暗号化データを意図的に改ざん
        tampered_data = original_encrypted[:-5] + "XXXXX"
        print("暗号化データを意図的に改ざんしました")
        
        try:
            # 改ざんされたデータの復号を試行
            decryptor_result = encryptor.decrypt(tampered_data)
            print("[WARNING] 改ざんが検知されませんでした")
        except Exception as e:
            print(f"✓ 改ざんが正常に検知されました: {str(e)}")
            
    except Exception as e:
        print(f"[ERROR] 改ざん検知テストエラー: {e}")
    
    print(f"\n[SUCCESS] AES-256 GCM暗号化モジュールのデモが完了しました")
    print("[INFO] 本番環境での使用時の注意点:")
    print("  - 暗号化鍵の安全な管理（HSM、Key Vaultの使用を推奨）")
    print("  - 鍵のローテーション計画")
    print("  - 暗号化データのバックアップ戦略")
    print("  - パフォーマンス監視（大容量データの場合）")
    print("  - 法的要件の遵守（GDPR、個人情報保護法等）")
