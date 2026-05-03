# TODO List - AstroTools

## Planeamento de Expansão de Efemérides

### 1. Motor de Cálculo Polimórfico (Arquitetura)
- [ ] Refatorar `/ephemeris/calculate` para utilizar uma fábrica `get_body_object(target_name)`.
- [ ] Implementar suporte a `EarthSatellite` (ISS) no endpoint `/calculate`.
- [ ] Normalizar o retorno entre objetos celestes (`planets`, `stars`) e satélites (`EarthSatellite`).

### 2. Suporte a Corpos Menores (Cometas/Asteroides/NEOs)
- [ ] Implementar rotina de download automático de elementos orbitais (formato MPC ou JPL Small-Body Database).
- [ ] Adicionar lógica de parse para processar os elementos orbitais descarregados no `skyfield`.
- [ ] Atualizar o método `update_ephemeris` para incluir os novos datasets.

### 3. Gestão de Catálogos
- [ ] Migrar o `target_map` (hardcoded) para uma base de dados ou ficheiro de configuração JSON expansível.

---
*Estado: Planeamento inicial concluído. A executar como prioridade futura.*
