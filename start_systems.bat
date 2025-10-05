@echo off
chcp 65001 >nul
echo ========================================
echo Patient Information Sharing System
echo Auto Startup Script
echo ========================================
echo.

echo [1/3] Stopping existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/3] Starting Dummy EHR (5002)...
start "Dummy EHR (5002)" cmd /k "cd dummy_ehr_system && python run_dummy_ehr.py"
timeout /t 3 /nobreak >nul

echo [3/3] Starting React App (5001)...
start "React App (5001)" cmd /k "cd SecHack365_project && npm run dev"

echo.
echo ========================================
echo Startup Complete!
echo ========================================
echo.
echo Access URLs:
echo - Main System: http://localhost:5001
echo - Dummy EHR: http://localhost:5002
echo.
echo Close the opened windows to stop the systems.
echo ========================================
pause
