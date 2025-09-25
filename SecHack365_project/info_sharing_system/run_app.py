#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SecHack365 患者中心の患者情報共有プロジェクト - 情報共有システム
安全なデフォルト設定版
"""

import os
import sys

# プロジェクトルートを確認（モノレポ対応）
project_root = os.path.dirname(os.path.abspath(__file__))          # .../info_sharing_system
monorepo_root = os.path.dirname(project_root)                       # .../SecHack365_project

# パスを設定
sys.path.insert(0, project_root)
sys.path.insert(0, monorepo_root)

from app.app import app  # 既存実装を前提

def bool_env(name: str, default: bool = False) -> bool:
    """環境変数をbool値に変換"""
    v = os.getenv(name)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")

if __name__ == "__main__":
    # 環境変数から設定を取得（安全なデフォルト値）
    HOST = os.getenv("HOST", "127.0.0.1")        # dev既定はローカルのみ
    PORT = int(os.getenv("PORT", "5001"))
    DEBUG = bool_env("FLASK_DEBUG", False)        # デフォルトはFalse
    USE_SSL = bool_env("USE_SSL", False)          # デフォルトはFalse

    # SSL証明書のパスを確認
    cert_dir = os.path.join(project_root, "app", "certs")
    cert_path = os.path.join(cert_dir, "cert.pem")
    key_path = os.path.join(cert_dir, "key.pem")

    ssl_context = None
    if USE_SSL and os.path.exists(cert_path) and os.path.exists(key_path):
        ssl_context = (cert_path, key_path)
        print(f"[INFO] SSL証明書を使用: {cert_path}")

    print("SecHack365 患者中心の患者情報共有プロジェクト - 情報共有システム")
    print("=" * 60)
    print(f"起動設定:")
    print(f"  host={HOST}")
    print(f"  port={PORT}")
    print(f"  debug={DEBUG}")
    print(f"  ssl={'on' if ssl_context else 'off'}")
    print("=" * 60)
    
    if DEBUG:
        print("[WARNING] デバッグモードが有効です（本番環境では無効にしてください）")
    
    if HOST == "0.0.0.0":
        print("[WARNING] 外部アクセスが可能です（本番環境では適切なファイアウォール設定が必要）")
    
    if not ssl_context and not DEBUG:
        print("[WARNING] 本番環境ではHTTPSの使用を強く推奨します")

    print(f"ブラウザで {'https' if ssl_context else 'http'}://{HOST}:{PORT} にアクセスしてください")
    print("=" * 60)

    try:
        # 本番では必ず DEBUG=False、TLSはリバースプロキシ側で正規証明書を使用
        app.run(
            host=HOST,
            port=PORT,
            debug=DEBUG,
            use_reloader=False,  # 本番では必ずFalse
            ssl_context=ssl_context,
        )
    except Exception as e:
        print(f"[ERROR] サーバー起動エラー: {e}")
        import traceback
        traceback.print_exc()
        print("[HINT] 仮想環境がアクティブになっているか確認してください")
        print("[HINT] 必要なパッケージがインストールされているか確認してください")
        sys.exit(1)