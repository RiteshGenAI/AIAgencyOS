# Start backend + frontend in separate windows (requires PostgreSQL)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot

Write-Host '=== Starting AI Agency OS locally ===' -ForegroundColor Cyan
Write-Host 'Ensure PostgreSQL is running (.\scripts\start-postgres.ps1)' -ForegroundColor Yellow

$backendScript = Join-Path $PSScriptRoot 'start-backend.ps1'
$frontendScript = Join-Path $PSScriptRoot 'start-frontend.ps1'

Start-Process powershell -ArgumentList "-NoExit", "-File", $backendScript
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-File", $frontendScript

Write-Host 'Backend: http://localhost:8000' -ForegroundColor Green
Write-Host 'Frontend: http://localhost:5173' -ForegroundColor Green
