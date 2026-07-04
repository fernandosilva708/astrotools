# TODO List - AstroTools

## 🚀 Planeamento de Expansão (Features)
### 1. Efemérides & Catálogos
- [ ] Finalizar o parser detalhado para elementos orbitais (formato Soft00) para suporte completo de Cometas e Asteroides.
- [ ] Implementar a gestão dinâmica de catálogos (migrar `target_map` de hardcoded para Base de Dados/JSON).
- [ ] Expandir o suporte a busca de satélites além da ISS.

### 2. Galeria e Imagens
- [x] Implementar *background workers* (ex: Celery ou threads dedicadas) para Plate Solving automático após ingestão.
- [ ] Adicionar suporte a edição de metadados em lote.

### 3. Diário de Observações
- [ ] Automatizar a criação de logs de observação a partir de metadados FITS/EXIF extraídos da Galeria.
- [ ] Adicionar exportação de observações (ex: formato CSV ou PDF).

### 4. Integrações
- [ ] Concluir implementação do proxy Telescopius (frontend).
- [ ] Implementar alertas automáticos (push/email) para condições de céu limpo (integrar com worker externo).

## 🛠 Dívida Técnica
- [ ] **Setup Windows**: Investigar falha persistente na instalação de dependências e ativação do venv no Windows (módulos como `skyfield.orbits` e `cryptography` não são encontrados após setup).
- [ ] Centralizar toda a configuração em uma única tabela `system_settings` em vez de múltiplos ficheiros `.env` e chaves individuais.
- [ ] Melhorar a cobertura de testes unitários (atualmente muito baixa).
- [x] Implementar gestão de perfis de utilizador (avatar, alteração de password robusta).
- [ ] Refatorar os cálculos de Seeing/Transparência para usar modelos meteorológicos mais precisos em vez de stubs baseados em nuvens/vento.
- [ ] Verificar se os ficheiros em falta na galeria precisam de ser importados manualmente ou se a ingestão do Seestar precisa de ser revista para garantir que todos os ficheiros são lidos.
- [x] **Localização Dinâmica no Planeador**: Alterar o planeador de sessões (`app/planner/routes.py`) para utilizar o `LocationService.get_current_location()` em vez de coordenadas de latitude/longitude hardcoded.

## 🔴 Correções Críticas & Stubs Pendentes
- [x] **Criar Módulo de Efemérides (routes.py)**: O ficheiro `app/ephemeris/routes.py` está em falta no repositório, impedindo o arranque da aplicação. É urgente criar o blueprint `ephemeris_bp` e as rotas necessárias para a interface (`/`, `/iss`, `/update_ephemeris`, `/calculate`, `/calculate_iss`).
- [x] **Leitura de coordenadas .wcs no ASTAP**: Em `app/astrometry/routes.py`, implementar a extração e leitura das coordenadas RA/Dec reais do ficheiro `.wcs` gerado pelo ASTAP após a resolução astrométrica com sucesso.
- [x] **Controlo Remoto do Seestar S50**: Implementar o protocolo real REST/Alpaca em `app/seestar.py` (atualmente apenas um stub com `pass` no `capture_image` e endpoint hipotético no `get_status`) e integrá-lo com a UI.

---
*Estado: Revisão concluída em 07/06/2026. Atualizado com inconsistências e stubs críticos identificados no código.*
