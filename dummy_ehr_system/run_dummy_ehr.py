"""
模擬電子カルテシステム起動スクリプト
"""

import sys
import os

# パスを追加
sys.path.append(os.path.dirname(__file__))

from app.app import app

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=True)

