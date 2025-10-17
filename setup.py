"""
セットアップスクリプト
"""
import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """コマンドを実行"""
    print(f"実行中: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} 完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} 失敗: {e}")
        print(f"エラー出力: {e.stderr}")
        return False

def main():
    """メイン処理"""
    print("医療記録システム セットアップを開始します...")
    
    # 1. 環境変数ファイル作成
    print("\n1. 環境変数ファイルを作成中...")
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            os.system('cp env.example .env')
            print("✓ .envファイルを作成しました")
        else:
            print("✗ env.exampleファイルが見つかりません")
            return False
    else:
        print("✓ .envファイルは既に存在します")
    
    # 2. 必要なディレクトリ作成
    print("\n2. 必要なディレクトリを作成中...")
    directories = ['logs', 'uploads', 'alembic/versions']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ {directory} ディレクトリを作成")
    
    # 3. Docker ComposeでPostgreSQL起動
    print("\n3. PostgreSQLを起動中...")
    if not run_command("docker-compose up -d postgres", "PostgreSQL起動"):
        print("Docker Composeが利用できない場合、手動でPostgreSQLを起動してください")
    
    # 4. Python依存関係インストール
    print("\n4. Python依存関係をインストール中...")
    if not run_command("pip install -r requirements.txt", "依存関係インストール"):
        return False
    
    # 5. Alembic初期化
    print("\n5. Alembicを初期化中...")
    if not run_command("alembic revision --autogenerate -m 'Initial migration'", "Alembic初期化"):
        return False
    
    # 6. データベースマイグレーション実行
    print("\n6. データベースマイグレーションを実行中...")
    if not run_command("alembic upgrade head", "データベースマイグレーション"):
        return False
    
    # 7. ダミーデータ生成
    print("\n7. ダミーデータを生成中...")
    if not run_command("python scripts/generate_dummy_data.py", "ダミーデータ生成"):
        print("ダミーデータ生成に失敗しましたが、セットアップは続行します")
    
    print("\n✓ セットアップが完了しました！")
    print("\n次のステップ:")
    print("1. .envファイルを編集して、本番環境用の設定を行ってください")
    print("2. python app.py でアプリケーションを起動してください")
    print("3. http://localhost:5000 でアクセスできます")

if __name__ == "__main__":
    main()
