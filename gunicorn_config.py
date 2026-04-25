# SPDX-License-Identifier: GPL-2.0-only
import multiprocessing
import os

# Configuração Gunicorn para Raspberry Pi 2
# RAM: 1GB, CPU: 4 Cores (ARMv7)

# Bind à porta 5000 em todas as interfaces
bind = "0.0.0.0:5000"

# Número de workers: 2 é o ideal para o Pi 2 para não esgotar a RAM
# (2 * cores + 1 seria 9, o que é demasiado para 1GB RAM)
workers = 2

# Timeout longo para operações de astronomia pesadas
timeout = 120

# Log de erros
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Recarregar se o código mudar (útil se estiver a ser usado para dev em Linux)
reload = False
