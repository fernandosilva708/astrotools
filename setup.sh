#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-only

# AstroTools - Setup para Raspberry Pi / Linux
# Executar: chmod +x setup.sh && ./setup.sh

echo "--- AstroTools: Iniciando configuração para Raspberry Pi ---"

# 1. Instalar dependências do sistema
echo "Instalando dependências do sistema (necessita de sudo)..."
sudo apt update
sudo apt install -y python3-venv python3-dev build-essential rclone libopenjp2-7 libtiff6 libjpeg-dev

# 2. Criar e ativar ambiente virtual
echo "Criando ambiente virtual Python (venv)..."
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependências Python
echo "Instalando dependências Python (isto pode demorar no Pi 2)..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Criar estrutura de diretórios
echo "Criando pastas de sistema..."
mkdir -p uploads/gallery
mkdir -p instance

# 5. Inicializar base de dados
echo "Inicializando base de dados..."
export FLASK_APP=run.py
flask db upgrade

# 6. Configurar .env
if [ ! -f .env ]; then
    echo "Criando ficheiro .env inicial..."
    cp .env.example .env
    echo "AVISO: Edite o ficheiro .env para configurar as chaves de API e caminhos."
fi

echo "--- Configuração concluída com sucesso! ---"
echo "Para iniciar o servidor, execute:"
echo "source venv/bin/activate"
echo "gunicorn -c gunicorn_config.py run:app"
