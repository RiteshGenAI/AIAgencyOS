# Start frontend dev server
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot

Push-Location (Join-Path $Root 'frontend\app')
npm run dev -- --host 0.0.0.0
