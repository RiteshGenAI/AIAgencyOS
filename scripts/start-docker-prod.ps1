# Start production stack via Docker Compose
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot

Write-Host '=== Starting AI Agency OS (production compose) ===' -ForegroundColor Cyan

try {
    docker info *> $null
} catch {
    Write-Host 'Docker is not running. Start Docker Desktop and try again.' -ForegroundColor Red
    exit 1
}

Push-Location $Root
docker compose -f docker-compose.prod.yml up --build -d
Write-Host 'Production stack running at http://localhost' -ForegroundColor Green
Pop-Location
