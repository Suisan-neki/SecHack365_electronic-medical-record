@echo off
echo ========================================
echo 患者情報共有システム 停止スクリプト
echo ========================================
echo.

echo プロセスを停止中...
taskkill /f /im python.exe
taskkill /f /im node.exe

echo.
echo すべてのシステムが停止されました。
echo ========================================
pause
