# GEMINI.md

Este ficheiro fornece mandatos fundamentais e contexto do projeto para o Gemini CLI ao trabalhar neste repositório.

## Visão Geral do Projeto
**AstroTools** é uma aplicação web Python Flask que fornece um conjunto de ferramentas para astrónomos amadores, incluindo autenticação, uma galeria de imagens com importação do Seestar, resolução astrométrica (plate-solving), cálculos de efemérides, um proxy para o Telescopius, diário de observações, planeador de sessão e funcionalidade de backup via rclone.

**Ambiente Alvo:** Este projeto foi especificamente desenhado para correr num **Raspberry Pi** com uma distribuição **Linux**. As considerações de desenvolvimento e implementação devem ter em conta as características de desempenho do Raspberry Pi (especialmente modelos com menos RAM) e a arquitetura ARM.

## Estado Atual
O projeto encontra-se na fase de **conclusão das funcionalidades core**. A interface está localizada (PT-PT/EN) e o dashboard fornece um resumo funcional do sistema.

## Arquitetura e Stack Tecnológica
- **Framework:** Flask (padrão Application Factory em `create_app()`).
- **Base de Dados:** SQLAlchemy com Flask-Migrate. SQLite.
- **Autenticação:** Flask-Login.
- **Frontend:** Templates Jinja2, Pico.css, Vanilla JS para i18n.
- **Integrações Externas:**
  - **Astrometria:** ASTAP (local) e API do `nova.astrometry.net`.
  - **Cálculos:** Biblioteca `skyfield`.
  - **Backup:** `rclone`.
  - **Telescopius:** Proxy para evitar CORS.

## Mandatos e Convenções de Desenvolvimento
- **Comentários:** Devem ser sempre em **Português Europeu (PT-PT)**.
- **Traduções:** Novas funcionalidades devem incluir chaves em `app/static/js/translations.js` para PT e EN.
- **UI:** Usar componentes semânticos do Pico.css. Botões que executam ações lentas devem ter `onsubmit="this.querySelector('button').setAttribute('aria-busy', 'true')"`.
- **Modelos:** Relações devem ser explícitas (ex: Imagens ligadas a Observações).

## Plano de Implementação (Estado do Projeto)

### 1. Base de Dados e Modelos
- [x] Migrar modelos para incluir definições de utilizador (API keys).
- [x] Ligar o modelo `Observation` ao modelo `GalleryImage`.
- [x] Garantir migrações consistentes com SQLite (nomes de restrições).

### 2. Frontend e Localização
- [x] Sistema de i18n funcional no lado do cliente.
- [x] Estilização de alertas (Flash Messages) integrada com Pico.css.
- [x] Refatoração do Dashboard para estado "5 Estrelas" (Resumo funcional).
- [x] Termos de sessão: "Iniciar Sessão" e "Terminar Sessão".

### 3. Módulos e Integrações
- [x] Proxy Telescopius funcional.
- [x] Diário de Observações (Módulo 1).
- [x] Planeador de Sessão (Módulo 2).
- [x] Página de detalhes da imagem com edição e eliminação.

### 4. Próximos Passos
- [ ] **Módulo de Meteorologia:** Previsões específicas para astronomia.
- [ ] Melhorar a UI da Galeria (filtros, paginação).
- [ ] Gráficos de visibilidade no Planeador.

Trabalho de equipa. 🚀
