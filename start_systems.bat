@echo off
taskkill /f /im python.exe >nul 2>&1 & timeout /t 1 /nobreak >nul
start "Dummy EHR (5002)" /D "%~dp0dummy_ehr_system" python run_dummy_ehr.py
timeout /t 2 /nobreak >nul
start "Patient Info (5001)" /D "%~dp0SecHack365_project\info_sharing_system" python run_app.py
echo Systems started: http://localhost:5001 ^& http://localhost:5002
pause
