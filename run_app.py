#!/usr/bin/env python3
"""
メインアプリケーションの起動スクリプト
実際のアプリケーションは SecHack365_project/info_sharing_system/run_app.py にあります
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """メインアプリケーションを起動"""
    # プロジェクトルートを取得
    project_root = Path(__file__).parent
    app_script = project_root / "SecHack365_project" / "info_sharing_system" / "run_app.py"
    
    if not app_script.exists():
        print("エラー: アプリケーションスクリプトが見つかりません")
        print(f"期待されるパス: {app_script}")
        sys.exit(1)
    
    # 実際のアプリケーションを起動
    print("患者情報共有システムを起動しています...")
    print(f"アプリケーション: {app_script}")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, str(app_script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"アプリケーションの起動に失敗しました: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nアプリケーションを終了しています...")
        sys.exit(0)

if __name__ == "__main__":
    main()
