# AstroTools 🚀

**AstroTools** é uma aplicação web desenvolvida em Python com o framework Flask, desenhada especificamente para astrónomos amadores. O projeto foi otimizado para correr num **Raspberry Pi**, fornecendo um conjunto de ferramentas essenciais para a gestão de astrofotografia e planeamento de observações.

## 🌟 Funcionalidades Concluídas

- **Dashboard 5 Estrelas:** Um resumo completo do estado da aplicação, incluindo imagens recentes, últimas observações do diário, objetos visíveis no céu em tempo real e estado dos backups.
- **Galeria de Imagens:** Gestão de capturas com suporte para importação automática do Seestar S50. Visualização de metadados técnicos (Exposição, Ganho, Alvo).
- **Diário de Observações:** Registo detalhado de sessões de observação, agora ligado diretamente à galeria de imagens.
- **Planeador de Sessão:** Sugestões inteligentes de objetos (Messier e estrelas brilhantes) visíveis na sua localização atual com gráficos de altitude dinâmica baseados em Chart.js.
- **Resolução Astrométrica (Plate Solving):** Integração com ASTAP (offline) e Astrometry.net (online) para identificar e salvar na BD as coordenadas exatas das suas imagens a partir do ficheiro `.wcs`.
- **Efemérides:** Cálculo de altitude/azimute para planetas e posição da ISS em tempo real.
- **Controlo Remoto Seestar S50:** Suporte real para comunicação e controlo do dispositivo via protocolo ASCOM/Alpaca (conexão, status, slew, captura, abort, park).
- **Módulo de Meteorologia:** Previsão específica para astronomia (nebulosidade, seeing e transparência) via Open-Meteo.
- **Backup Automatizado:** Sincronização com serviços na cloud (Google Drive, S3, etc.) via `rclone`.
- **Internacionalização (i18n):** Suporte total para **Português Europeu (PT-PT)** e **Inglês (EN)**.
- **Interface Moderna:** UI responsiva e leve baseada no **Pico.css**.

## 🛠️ Stack Tecnológica

- **Backend:** Flask (Python 3)
- **Base de Dados:** SQLite com SQLAlchemy / Flask-Migrate
- **Cálculos Astronómicos:** Skyfield
- **Visualização de Dados:** Chart.js
- **Frontend:** Jinja2, Pico.css, Vanilla JS
- **Sincronização:** Rclone
- **Plate Solving:** ASTAP / Astrometry.net

## 🚀 Instalação e Execução

### Pré-requisitos (Linux/Raspberry Pi)
```bash
sudo apt update
sudo apt install -y python3-venv python3-dev build-essential rclone astap-cli
```

### Configuração
1. Clone o repositório.
2. Execute o script de configuração para preparar o ambiente virtual:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. Configure as suas chaves de API e caminhos no ficheiro `.env`.
4. Inicialize a base de dados e os dados de teste (seeding):
   ```bash
   export FLASK_APP=run.py
   venv/bin/flask db upgrade
   venv/bin/python3 seed_db.py
   ```

### Executar
```bash
source venv/bin/activate
python run.py
```

## 🗺️ Roteiro (Próximos Passos)

- [ ] **Integração Avançada de Metadados:** Extração automática de metadados FITS/EXIF diretamente após o upload para criar observações automáticas.
- [ ] **Catálogos Dinâmicos:** Migração da lista estática do planeador para uma base de dados totalmente configurável e importável (Soft00 para cometas/asteroides).
- [ ] **Alertas de Transmissão:** Integração de alertas de tempo limpo via webhooks ou notificações.

---
**Desenvolvido por Fernando Silva**
Trabalho de equipa. 🚀
