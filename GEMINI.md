# GEMINI.md

Este ficheiro fornece mandatos fundamentais e contexto do projeto para o Gemini CLI ao trabalhar neste repositório.

## Visão Geral do Projeto
**AstroTools** é uma aplicação web Python Flask que fornece um conjunto de ferramentas para astrónomos amadores, incluindo autenticação, uma galeria de imagens com importação do Seestar, plate-solving (astrometria), cálculos de efemérides, um proxy para o Telescopius e funcionalidade de backup via rclone.

**Ambiente Alvo:** Este projeto foi especificamente desenhado para correr num **Raspberry Pi** com uma distribuição **Linux**. As considerações de desenvolvimento e implementação devem ter em conta as características de desempenho do Raspberry Pi e a arquitetura ARM.

## Estado
O projeto encontra-se atualmente na **fase de scaffolding**. A estrutura de diretórios e os ficheiros iniciais dos módulos foram criados, mas muitos detalhes de implementação core estão pendentes.

## Arquitetura e Stack Tecnológica
- **Framework:** Flask (padrão Application Factory em `create_app()`).
- **Base de Dados:** SQLAlchemy com Flask-Migrate (modelos partilhados em `app/models.py`). SQLite.
- **Autenticação:** Flask-Login para autenticação de utilizadores.
- **Frontend:** Templates Jinja2, Pico.css (CSS Vanilla minimalista).
- **Integrações Externas:**
  - **Astrometria:** Integração com a API do `nova.astrometry.net` (ou `solve-field` local se disponível no Pi).
  - **Efemérides:** Cálculos através da biblioteca Python `skyfield`.
  - **Backup:** Integração externa com `rclone` (dependência ao nível do sistema).
  - **Telescopius:** Proxy para serviços astronómicos externos.
- **Estrutura do Projeto:**
  - `app/`: Lógica principal da aplicação organizada por blueprints.
    - `auth/`: Autenticação de utilizadores (rotas, formulários).
    - `gallery/`: Galeria de imagens com lógica de importação do Seestar (`ingest.py`).
    - `astrometry/`: Integração de plate-solving.
    - `ephemeris/`: Cálculos astronómicos.
    - `telescopius/`: Serviços de proxy.
    - `backup/`: Gestão de backups baseada em rclone.
    - `dashboard/`: Dashboard principal do utilizador.
    - `static/`: Assets (CSS, JS, imagens).
    - `templates/`: Templates Jinja2, espelhados por módulo.
  - `migrations/`: Migrações da base de dados Alembic.
  - `tests/`: Suite de testes usando `pytest`.
  - `run.py`: Ponto de entrada da aplicação.

## Mandatos e Convenções de Desenvolvimento
- **Blueprints:** Cada módulo deve ser registado como um Blueprint do Flask em `app/__init__.py`.
- **Modelos:** Todos os modelos SQLAlchemy devem residir em `app/models.py`.
- **Templates:** Seguir a estrutura `app/templates/<modulo>/`, garantindo que o nome do diretório corresponde ao nome do blueprint.
- **Ambiente:** Usar `.env` para configuração local. Nunca submeter o ficheiro `.env`; usar `.env.example` como modelo.
- **Considerações Específicas para o Pi:**
  - O código deve ser compatível com a arquitetura ARM (Raspberry Pi).
  - Minimizar operações pesadas na thread principal do Flask; usar processos em background quando necessário.
  - Garantir compatibilidade com caminhos específicos de Linux e ferramentas do sistema (`rclone`, etc.).
- **Normas:** Aderir ao PEP 8 para código Python e manter manipuladores de rotas claros e documentados.

## Comandos Comuns
### Configuração e Desenvolvimento (Linux/Pi)
- **Instalar dependências do sistema:** `sudo apt update && sudo apt install rclone astrometry.net` (conforme necessário).
- **Instalar dependências Python:** `pip install -r requirements.txt`.
- **Configurar ambiente:** `cp .env.example .env` (e depois editar conforme necessário).
- **Inicializar/Atualizar Base de Dados:** `flask db upgrade`.
- **Executar Servidor de Desenvolvimento:** `python run.py`.

### Testes e Qualidade
- **Executar testes:** `pytest`.
- **Linting:** `flake8 app/`.

## Plano de Implementação (Próximos Passos)

### 1. Base de Dados (SQLite)
- [x] Garantir que a pasta `instance/` existe e é ignorada pelo Git.
- [x] Inicializar Flask-Migrate se necessário: `flask db init`.
- [x] Criar a migração inicial: `flask db migrate -m "Initial migration"`.
- [x] Aplicar a migração: `flask db upgrade`.
- [x] Verificar a integridade dos modelos em `app/models.py`.

### 2. Frontend (Pico.css)
- [x] Remover assets do template Editorial (JS/CSS antigos).
- [x] Integrar Pico.css v2.1.1 em `app/static/css/`.
- [x] Refatorar `app/templates/base.html` para estrutura semântica Pico.css.
- [x] Atualizar todos os templates de módulos para usar classes/semântica do Pico.css.
- [x] Implementar sistema de internacionalização (PT-PT/EN).
- [x] Estilizar mensagens Flash com cores do Pico.css.
