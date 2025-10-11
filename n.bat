@echo off
taskkill /f /im python.exe >nul 2>&1
cd dummy_ehr_system & start "EHR" cmd /k python run_dummy_ehr.py & cd .. & timeout /t 2 /nobreak >nul & cd SecHack365_project\info_sharing_system & start "Info" cmd /k python run_app.py & cd ..\..
echo http://localhost:5001 ^& http://localhost:5002

REM 1. @echo off: コマンドの実行内容を非表示にして画面をスッキリさせる
REM 2. taskkill: 既存のPythonプロセスを強制終了してポート競合を防止 (>nul 2>&1でエラーメッセージも非表示)
REM 3. cd^&start: EHRシステム(5002)とInfoシステム(5001)を順次起動
REM 4. echo: 起動完了後にアクセスURLを表示
