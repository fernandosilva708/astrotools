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
- **Cálculos Skyfield:** Quando utilizar o ficheiro de efemérides local `de440.bsp` para obter a posição de planetas, mapear os alvos para os seus respetivos baricentros (ex: `'mars barycenter'`, `'jupiter barycenter'`, `'venus barycenter'`), uma vez que os nomes simples dos planetas não constam desse kernel.

## Estrutura da Base de Dados
A base de dados utiliza **SQLite** gerido pelo **SQLAlchemy**. Abaixo descreve-se a estrutura das tabelas principais:

### 1. `users` (Utilizadores)
Armazena as informações de autenticação e preferências.
- `id`: Identificador único (Primary Key).
- `username`: Nome de utilizador único.
- `email`: Endereço de correio eletrónico.
- `password_hash`: Palavra-passe encriptada.
- `astrometry_api_key`: Chave API encriptada para serviços de resolução astrométrica.
- `telescopius_base_url`: URL base personalizada para o proxy.

### 2. `gallery_images` (Imagens da Galeria)
Regista todas as astrofotografias importadas ou carregadas.
- `id`: Identificador único.
- `filename`: Nome original do ficheiro.
- `title`: Título atribuído pelo utilizador.
- `description`: Notas sobre a captura.
- `filepath`: Caminho no sistema de ficheiros (Raspberry Pi).
- `ra` / `dec`: Coordenadas celestes após resolução astrométrica.
- `plate_solved`: Booleano, indica se a imagem foi resolvida.
- `observation_id`: Foreign Key para a tabela `observations`.
- `backup_status`: Booleano, indica sucesso da sincronização via rclone.

### 3. `observations` (Diário de Observações)
Regista sessões de observação no diário.
- `id`: Identificador único.
- `target`: Nome do objeto alvo.
- `notes`: Observações detalhadas da sessão.
- `observed_at`: Data e hora da observação.
- `ra` / `dec`: Coordenadas do alvo.
- `user_id`: Foreign Key para o `users` (autor).
- `images`: Relação (One-to-Many) com `gallery_images`.

---
## Plano de Implementação (Estado do Projeto)
... (mantém o plano existente) ...

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
- [x] **Módulo de Meteorologia:** Previsões específicas para astronomia via Open-Meteo.
- [x] **Gráficos de visibilidade no Planeador:** Gráfico de altitude dinâmica via Chart.js.
- [x] **Módulo de Efemérides:** Implementar o blueprint e rotas em `app/ephemeris/routes.py` que estão em falta e impedem o arranque da aplicação.
- [x] **Integração de Coordenadas ASTAP:** Extrair dados do ficheiro `.wcs` para atualizar `image.ra` e `image.dec` na base de dados após o solve.
- [x] **Controlo Remoto do Seestar S50:** Substituir os stubs em `app/seestar.py` por lógica real do protocolo REST/Alpaca e integrar com a interface.
- [x] **Localização Dinâmica no Planeador:** Corrigir as coordenadas de latitude/longitude hardcoded no planeador de sessões para utilizar o `LocationService`.
- [x] Melhorar a UI da Galeria (filtros, paginação) — Filtros avançados e paginação unificada implementados.
- [x] Integração avançada entre Observações e Imagens.

Trabalho de equipa. 🚀
