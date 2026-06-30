# AI Agency OS - one-time setup
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot

Write-Host '=== AI Agency OS Setup ===' -ForegroundColor Cyan

$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')

Write-Host '[1/4] Backend dependencies...' -ForegroundColor Yellow
Push-Location (Join-Path $Root 'backend')
if (-not (Test-Path '.venv')) {
    python -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install --upgrade pip -q
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -q
Pop-Location

Write-Host '[2/4] Agents dependencies...' -ForegroundColor Yellow
Push-Location (Join-Path $Root 'agents')
if (-not (Test-Path '.venv')) {
    python -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install --upgrade pip -q
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -q
Pop-Location

Write-Host '[3/4] Frontend dependencies...' -ForegroundColor Yellow
Push-Location (Join-Path $Root 'frontend\app')
npm install
Pop-Location

Write-Host '[4/4] Environment files...' -ForegroundColor Yellow
$backendEnv = Join-Path $Root 'backend\.env'
if (-not (Test-Path $backendEnv)) {
    Copy-Item (Join-Path $Root 'backend\.env.example') $backendEnv
    Write-Host 'Created backend/.env' -ForegroundColor Green
}
$agentsEnv = Join-Path $Root 'agents\.env'
if (-not (Test-Path $agentsEnv)) {
    Copy-Item (Join-Path $Root 'agents\.env.example') $agentsEnv
    Write-Host 'Created agents/.env' -ForegroundColor Green
}

Write-Host ''
Write-Host 'Setup complete!' -ForegroundColor Green
Write-Host 'Run:  .\scripts\start-docker.ps1   (recommended)' -ForegroundColor White
Write-Host '  or: .\scripts\start-all.ps1    (native PostgreSQL + local processes)' -ForegroundColor White
