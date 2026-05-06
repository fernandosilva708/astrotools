# Setup para AstroTools (PowerShell 7.6.1+)
# Executar: .\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "--- AstroTools: Iniciando configuração para Windows 11 (PowerShell) ---" -ForegroundColor Cyan

# 1. Verificar ambiente
# ... (manter o que já existe)

# 1.1 ASTAP para Windows (Automação)
Write-Host "Configurando ASTAP para Windows..." -ForegroundColor Cyan
if (-not (Test-Path "C:\ASTAP")) {
    New-Item -ItemType Directory -Path "C:\ASTAP" | Out-Null
}

if (-not (Test-Path "C:\ASTAP\astap_cli.exe")) {
    Write-Host "Baixando ASTAP CLI..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "http://www.hnsky.org/astap_cli_win64.exe" -OutFile "C:\ASTAP\astap_cli.exe"
}

if (-not (Test-Path "C:\ASTAP\d80")) {
    Write-Host "Baixando e extraindo catálogo D80..." -ForegroundColor Yellow
    $zipPath = "C:\ASTAP\d80.zip"
    Invoke-WebRequest -Uri "http://www.hnsky.org/astap_d80_star_database.zip" -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath "C:\ASTAP\d80" -Force
    Remove-Item $zipPath
}

# Adicionar ao .env
$envContent = Get-Content ".env" -ErrorAction SilentlyContinue
if ($envContent -notmatch "ASTAP_CLI_PATH") {
    Add-Content ".env" "`nASTAP_CLI_PATH=C:\ASTAP\astap_cli.exe"
    Add-Content ".env" "ASTAP_CATALOG_PATH=C:\ASTAP\d80"
}

# 2. Criar e configurar o venv
if (Test-Path "venv") {
    Write-Host "Removendo venv antigo..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv"
}

Write-Host "Criando ambiente virtual..." -ForegroundColor Cyan
python -m venv venv
$env:PATH = ".\venv\Scripts;" + $env:PATH

# 3. Garantir pip e instalar dependências
Write-Host "Atualizando pip e instalando dependências..." -ForegroundColor Cyan
python -m ensurepip
python -m pip install --upgrade pip
if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt
} else {
    Write-Warning "requirements.txt não encontrado."
}

# 4. Criar estrutura de diretórios e pastas
Write-Host "Preparando pastas de sistema..." -ForegroundColor Cyan
$dirs = @("uploads/gallery", "instance")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
}

# 5. Configurar .env
if (-not (Test-Path ".env")) {
    Write-Host "Criando .env a partir de .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# 6. Inicializar base de dados
Write-Host "Inicializando base de dados..." -ForegroundColor Cyan
$env:FLASK_APP = "run.py"
python -m flask db upgrade
python seed_db.py

Write-Host "--- Configuração concluída! ---" -ForegroundColor Green
Write-Host "Para iniciar, execute: .\venv\Scripts\Activate.ps1; python run.py" -ForegroundColor White
