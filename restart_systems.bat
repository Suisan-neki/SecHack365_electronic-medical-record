@echo off
echo ========================================
echo 患者情報共有システム 再起動スクリプト
echo ========================================
echo.

echo [1/4] 既存のプロセスを停止中...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 3 /nobreak >nul

echo [2/4] 模擬電子カルテ（5002）を起動中...
start "Dummy EHR (5002)" cmd /k "cd dummy_ehr_system && python run_dummy_ehr.py"
timeout /t 5 /nobreak >nul

echo [3/4] Reactアプリ（5001）を起動中...
start "React App (5001)" cmd /k "cd SecHack365_project && npm run dev"

echo [4/4] 起動完了！
echo.
echo ========================================
echo 再起動完了！
echo ========================================
echo.
echo アクセス先:
echo - メインシステム: http://localhost:5001
echo - 模擬電子カルテ: http://localhost:5002
echo.
echo 終了するには、開いたウィンドウを閉じてください。
echo ========================================
pause
