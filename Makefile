# 患者情報共有システム - 開発用Makefile

.PHONY: help install run test clean setup-dev

# デフォルトターゲット
help:
	@echo "患者情報共有システム - 利用可能なコマンド:"
	@echo ""
	@echo "  make install    - 依存関係をインストール"
	@echo "  make run        - アプリケーションを起動"
	@echo "  make setup-dev  - 開発環境をセットアップ"
	@echo "  make test       - テストを実行"
	@echo "  make clean      - キャッシュファイルを削除"
	@echo "  make help       - このヘルプを表示"

# 依存関係のインストール
install:
	@echo "依存関係をインストールしています..."
	pip install -r SecHack365_project/requirements.txt

# アプリケーションの起動
run:
	@echo "患者情報共有システムを起動しています..."
	python run_app.py

# 開発環境のセットアップ
setup-dev:
	@echo "開発環境をセットアップしています..."
	python -m venv venv
	@echo "仮想環境を作成しました。以下のコマンドでアクティベートしてください:"
	@echo "  Windows: venv\\Scripts\\activate"
	@echo "  macOS/Linux: source venv/bin/activate"
	$(MAKE) install

# テストの実行（将来的に実装予定）
test:
	@echo "テストを実行しています..."
	@echo "注意: テスト機能は今後実装予定です"

# キャッシュファイルの削除
clean:
	@echo "キャッシュファイルを削除しています..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	@echo "キャッシュファイルを削除しました"

# 本番環境用のセットアップ
setup-prod:
	@echo "本番環境用セットアップ..."
	@echo "注意: 本番環境では適切な環境変数の設定が必要です"
	@echo "SECRET_KEY, DATABASE_URL, WEBHOOK_SECRET等を設定してください"
