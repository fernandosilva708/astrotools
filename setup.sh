#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-only
set -e

# AstroTools - Setup para Raspberry Pi / Linux
# Executar: chmod +x setup.sh && ./setup.sh

echo "--- AstroTools: Iniciando configuração para Raspberry Pi ---"

# 1. Instalar dependências do sistema
echo "Instalando dependências do sistema..."
sudo apt update
sudo apt install -y python3-venv python3-dev python3-pip build-essential libffi-dev libssl-dev rclone libopenjp2-7 libtiff6 libjpeg-dev libopenblas-dev wget unzip

# 1.1 Instalar ASTAP CLI e Catálogo
echo "Instalando ASTAP CLI e catálogo D80..."
sudo apt update
sudo apt install -y astap-cli

# Instalar catálogo D80 (copiar da pasta local)
echo "Instalando catálogo D80..."
sudo mkdir -p /opt/astap/d80
sudo cp -r D80/* /opt/astap/d80/

# 2. Criar e configurar o .env
echo "Configurando .env..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Ficheiro .env criado a partir de .env.example."
else
    echo "Ficheiro .env já existe."
fi

# 3. Criar e ativar ambiente virtual
echo "Configurando ambiente virtual Python (venv)..."
if [ -d "venv" ]; then
    echo "Removendo venv antigo para garantir integridade..."
    rm -rf venv
fi

# Tentar criar venv. Em algumas distros, o venv não traz o pip por defeito.
python3 -m venv venv || { echo "Erro ao criar venv"; exit 1; }
source venv/bin/activate

# Garantir que o pip existe dentro do venv
if ! python3 -m pip --version > /dev/null 2>&1; then
    echo "Pip não encontrado no venv, tentando instalar com ensurepip..."
    python3 -m ensurepip || {
        echo "ensurepip falhou, tentando baixar get-pip.py..."
        curl -sS https://bootstrap.pypa.io/get-pip.py | python3
    }
fi

# 3. Instalar dependências Python
echo "Instalando dependências Python (isto pode demorar no Pi 2)..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# 4. Criar estrutura de diretórios
echo "Criando pastas de sistema..."
mkdir -p uploads/gallery
mkdir -p instance

# 5. Inicializar base de dados
echo "Inicializando base de dados..."
export FLASK_APP=run.py
flask db upgrade
python3 seed_db.py

echo "--- Configuração concluída com sucesso! ---"
echo "Para iniciar o servidor, execute:"
echo "source venv/bin/activate"
echo "gunicorn -c gunicorn_config.py run:app"
