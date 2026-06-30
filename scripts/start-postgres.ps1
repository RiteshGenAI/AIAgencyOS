# Start PostgreSQL container for local development
$ErrorActionPreference = 'Stop'

$containerName = 'agency-os-postgres'

$existing = docker ps -a --filter "name=$containerName" --format "{{.Names}}"
if ($existing -eq $containerName) {
    docker start $containerName | Out-Null
    Write-Host "Started existing container: $containerName" -ForegroundColor Green
} else {
    docker run -d `
        --name $containerName `
        -e POSTGRES_USER=postgres `
        -e POSTGRES_PASSWORD=postgres `
        -e POSTGRES_DB=agency_os `
        -p 5432:5432 `
        -v agency_os_postgres_data:/var/lib/postgresql/data `
        postgres:16 | Out-Null
    Write-Host "Created and started container: $containerName" -ForegroundColor Green
}

Write-Host 'PostgreSQL ready on localhost:5432 (db: agency_os)' -ForegroundColor Cyan
