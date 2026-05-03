# Setup para AstroTools (PowerShell 7.6.1+)
# Executar: .\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "--- AstroTools: Iniciando configuração para Windows 11 (PowerShell) ---" -ForegroundColor Cyan

# 1. Verificar ambiente
$pythonVersion = (python --version 2>&1)
if ($null -eq $pythonVersion) {
    Write-Error "Python não encontrado. Instale o Python 3.12+."
    exit 1
}
Write-Host "Python detectado: $pythonVersion" -ForegroundColor Green

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

Write-Host "--- Configuração concluída! ---" -ForegroundColor Green
Write-Host "Para iniciar, execute: .\venv\Scripts\Activate.ps1; python run.py" -ForegroundColor White
