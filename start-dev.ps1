#!/usr/bin/env pwsh
# start-dev.ps1 — inicia backend + frontend em paralelo
# Uso: .\start-dev.ps1

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "[1/2] Iniciando backend na porta 3000..." -ForegroundColor Cyan
$backendLog = "$env:TEMP\riftshield-backend.log"
$backendErr = "$env:TEMP\riftshield-backend-err.log"
Start-Process -NoNewWindow `
    -FilePath "python" `
    -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port 3000" `
    -WorkingDirectory "$root\backend\src" `
    -RedirectStandardOutput $backendLog `
    -RedirectStandardError $backendErr

# Aguarda backend ficar pronto (até 15s)
$ready = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    try {
        $r = Invoke-RestMethod -Uri "http://127.0.0.1:3000/api/health" -ErrorAction Stop
        if ($r.status -eq "ok") { $ready = $true; break }
    } catch {}
}

if ($ready) {
    Write-Host "[OK] Backend pronto em http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Backend nao respondeu. Verifique: Get-Content $backendErr" -ForegroundColor Red
    exit 1
}

Write-Host "[2/2] Iniciando frontend..." -ForegroundColor Cyan
Set-Location "$root\frontend"
npm run dev
