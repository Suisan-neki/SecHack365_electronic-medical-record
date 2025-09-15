#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SecHack365 患者中心の医療DXプロジェクト
メインアプリケーション起動スクリプト
"""

import os
import sys

# プロジェクトルートを確認
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# アプリケーションをインポートして実行
from app.app import app

if __name__ == '__main__':
    print("🏥 SecHack365 患者中心の医療DXプロジェクト")
    print("📍 プロジェクトルート:", project_root)
    print("🚀 HTTPS サーバーを起動中...")
    print("📱 ブラウザで https://localhost:5000 にアクセスしてください")
    print("⚠️  自己署名証明書のため、ブラウザで「安全でない」警告が表示される場合があります")
    print("=" * 60)
    
    # cert.pem と key.pem のパスを確認
    cert_path = os.path.join(project_root, 'app', 'cert.pem')
    key_path = os.path.join(project_root, 'app', 'key.pem')
    
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("❌ SSL証明書が見つかりません。generate_cert.py を実行してください。")
        sys.exit(1)
    
    try:
        app.run(
            debug=True,
            host='localhost',
            port=5000,
            ssl_context=(cert_path, key_path)
        )
    except Exception as e:
        print(f"❌ サーバー起動エラー: {e}")
        print("💡 ヒント: 仮想環境がアクティブになっているか確認してください")
