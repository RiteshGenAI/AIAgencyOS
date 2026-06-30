# Native local development instructions
$ErrorActionPreference = 'Stop'

Write-Host '=== AI Agency OS Local Development ===' -ForegroundColor Cyan
Write-Host '1. Run .\scripts\setup.ps1 (once)' -ForegroundColor White
Write-Host '2. Run .\scripts\start-postgres.ps1' -ForegroundColor White
Write-Host '3. Run python backend\seed_for_run.py from repo root' -ForegroundColor White
Write-Host '4. Run .\scripts\start-all.ps1' -ForegroundColor White
Write-Host ''
Write-Host 'Agents service (optional, separate terminal):' -ForegroundColor Yellow
Write-Host '  cd agents && ..\.venv\Scripts\python.exe -m uvicorn agents.app.main:app --reload --port 8081' -ForegroundColor White
