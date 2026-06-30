# Start full stack via Docker Compose (development)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot

Write-Host '=== Starting AI Agency OS via Docker Compose ===' -ForegroundColor Cyan

try {
    docker info *> $null
} catch {
    Write-Host 'Docker is not running. Start Docker Desktop and try again.' -ForegroundColor Red
    exit 1
}

Push-Location $Root
docker compose up --build
Pop-Location
