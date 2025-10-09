@echo off
taskkill /f /im python.exe >nul 2>&1
start "E" /D "%~dp0dummy_ehr_system" python run_dummy_ehr.py & start "I" /D "%~dp0SecHack365_project\info_sharing_system" python run_app.py
echo http://localhost:5001 ^& http://localhost:5002

REM 1. @echo off: コマンドの実行内容を非表示にして画面をスッキリさせる
REM 2. taskkill: 既存のPythonプロセスを強制終了（ポート競合防止）
REM 3. start: EHRシステム（5002）とInfoシステム（5001）を同時起動
REM 4. echo: アクセスURLを表示
