#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SecHack365 患者中心の患者情報共有プロジェクト - 情報共有システム
モノレポ構成対応版 起動スクリプト
"""

import os
import sys

# プロジェクトルートを確認（モノレポ対応）
project_root = os.path.dirname(os.path.abspath(__file__))
monorepo_root = os.path.dirname(project_root)  # SecHack365_project

# パスを設定
sys.path.insert(0, project_root)
sys.path.insert(0, monorepo_root)  # coreモジュールが含まれるディレクトリ

# アプリケーションをインポートして実行
from app.app import app

if __name__ == '__main__':
    print("SecHack365 患者中心の患者情報共有プロジェクト - 情報共有システム")
    print("プロジェクトルート:", project_root)
    print("モノレポルート:", monorepo_root)
    print("HTTP サーバーを起動中...")
    print("ブラウザで http://localhost:5001 にアクセスしてください")
    print("SSL証明書を一時的に無効化しています")
    print("=" * 60)
    
    # SSL証明書のディレクトリを作成
    cert_dir = os.path.join(project_root, 'app', 'certs')
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
        print(f"[INFO] 証明書ディレクトリを作成: {cert_dir}")
    
    # cert.pem と key.pem のパスを確認
    cert_path = os.path.join(cert_dir, 'cert.pem')
    key_path = os.path.join(cert_dir, 'key.pem')
    
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("[INFO] SSL証明書が見つかりません。")
        print("[INFO] 証明書を自動生成します...")
        
        # 証明書生成スクリプトのパス（モノレポ対応）
        generate_cert_script = os.path.join(os.path.dirname(project_root), 'scripts', 'generate_cert.py')
        
        if os.path.exists(generate_cert_script):
            import subprocess
            try:
                # 証明書生成を実行
                result = subprocess.run([
                    sys.executable, 
                    generate_cert_script, 
                    '--cert-dir', cert_dir
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("[SUCCESS] SSL証明書の生成が完了しました")
                else:
                    print(f"[ERROR] 証明書生成エラー: {result.stderr}")
                    sys.exit(1)
            except Exception as e:
                print(f"[ERROR] 証明書生成中にエラーが発生: {e}")
                sys.exit(1)
        else:
            print(f"[ERROR] 証明書生成スクリプトが見つかりません: {generate_cert_script}")
            print("[INFO] 手動で証明書を生成してください")
            sys.exit(1)
    
    # 証明書の有無に関係なく、HTTPでアプリケーションを起動
    try:
        print("[INFO] アプリケーションをポート5001で起動します（HTTP）")
        print("ブラウザで http://localhost:5001 にアクセスしてください")
        print("[WARNING] SSL証明書を一時的に無効化しています")
        print("[DEBUG] Flask app.run() を呼び出し中...")
        
        app.run(
            debug=True,
            host='0.0.0.0',  # localhost から 0.0.0.0 に変更
            port=5001,
            use_reloader=False  # リローダーを無効化
            # ssl_context=(cert_path, key_path)  # 一時的にコメントアウト
        )
    except Exception as e:
        print(f"[ERROR] サーバー起動エラー: {e}")
        import traceback
        traceback.print_exc()
        print("[HINT] 仮想環境がアクティブになっているか確認してください")
        print("[HINT] 必要なパッケージがインストールされているか確認してください")
