# 患者情報共有システム ワンクリック起動スクリプト
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "患者情報共有システム 自動起動スクリプト" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] 既存のプロセスを停止中..." -ForegroundColor Yellow
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

Write-Host "[2/3] 模擬電子カルテ（5002）を起動中..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "run_dummy_ehr.py" -WorkingDirectory "dummy_ehr_system" -WindowStyle Normal
Start-Sleep -Seconds 3

Write-Host "[3/3] Reactアプリ（5001）を起動中..." -ForegroundColor Yellow
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "SecHack365_project" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "起動完了！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "アクセス先:" -ForegroundColor White
Write-Host "- メインシステム: http://localhost:5001" -ForegroundColor Cyan
Write-Host "- 模擬電子カルテ: http://localhost:5002" -ForegroundColor Cyan
Write-Host ""
Write-Host "終了するには、開いたウィンドウを閉じてください。" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green

Read-Host "続行するには何かキーを押してください"
