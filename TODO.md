# TODO List - AstroTools

## 🚀 Planeamento de Expansão (Features)
### 1. Efemérides & Catálogos
- [ ] Finalizar o parser detalhado para elementos orbitais (formato Soft00) para suporte completo de Cometas e Asteroides.
- [ ] Implementar a gestão dinâmica de catálogos (migrar `target_map` de hardcoded para Base de Dados/JSON).
- [ ] Expandir o suporte a busca de satélites além da ISS.

### 2. Galeria e Imagens
- [ ] Implementar *background workers* (ex: Celery ou threads dedicadas) para Plate Solving automático após ingestão.
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
- [ ] Implementar gestão de perfis de utilizador (avatar, alteração de password robusta).
- [ ] Refatorar os cálculos de Seeing/Transparência para usar modelos meteorológicos mais precisos em vez de stubs baseados em nuvens/vento.
- [ ] Verificar se os ficheiros em falta na galeria precisam de ser importados manualmente ou se a ingestão do Seestar precisa de ser revista para garantir que todos os ficheiros são lidos.

---
*Estado: Revisão concluída em 03/05/2026. Projeto funcional e estável.*
