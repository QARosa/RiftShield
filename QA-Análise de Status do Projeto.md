# QA — Análise de Status do Projeto

**Projeto:** RiftShield — Plataforma de Detecção de Ameaças com IA (FIAP Software Security)  
**Versão do documento:** 1.1  
**Data:** 2026-07-20  
**Referências:** `qa.md`, `.cursor/skills/best-practices/SKILL.md`, `evidencias/2026-07-20/`

---

## 1. Resumo executivo

| Dimensão | Cobertura | Status |
|---|---|---|
| Pirâmide de testes (QA) | Alta | **Coberto** para entrega TC Fase 5 |
| CI / automação | Alta | **Coberto** |
| Compatibilidade browser | Alta | **Coberto** |
| Segurança (best practices) | Média-alta | **Parcial** (melhorado) |
| Qualidade de código (best practices) | Média | **Parcial** (melhorado) |
| Checklist manual QA §10 | Alta | **Coberto** (automatizado E2E) |

**Classificação final:** `PASS WITH CONCERNS` em hardening de produção · `PASS` em automação de testes e checklist §10.

**Conclusão:** O projeto evoluiu de 176 para **196 testes automatizados** (116 backend + 35 Vitest + 45 Cypress), com gaps críticos de RBAC, smoke YOLO, checklist §10 e integração E2E real endereçados. Permanecem débitos menores: `npm audit fix` completo, gate de coverage Vitest e TLS/HSTS em produção.

---

## 2. Evidências de execução (2026-07-20)

### 2.1 Resultados

| Camada | Comando | Resultado | Evidência |
|---|---|---|---|
| Backend (pytest) | `python -m pytest src/ -v -p no:flask` | **116/116 ✅** | `evidencias/2026-07-20/pytest.log`, `pytest-results.xml` |
| Frontend (Vitest) | `npm run test:unit` | **35/35 ✅** | `evidencias/2026-07-20/vitest.log` |
| E2E (Cypress) | `npx cypress run --browser chrome --headless` | **45/45 ✅** | `evidencias/2026-07-20/cypress.log` |
| Checklist §10 E2E | `npx cypress run --spec cypress/e2e/checklist_manual.cy.ts` | **11/11 ✅** | Execução local 2026-07-20 |
| Health check | `GET http://localhost:3000/api/health` | **OK** | `evidencias/2026-07-20/health-check.json` |
| Seed E2E | `python scripts/seed.py` | **OK** | `evidencias/2026-07-20/seed.log` |

**Total automatizado:** 196 testes — **100% pass**

### 2.2 Ambiente de execução

- **SO:** Windows · Python 3.12 · Node 24
- **Docker:** Mongo `27020` + Backend `3000`
- **Frontend:** Vite `1999` (proxy `/api` → `:3000`)
- **Usuário seed:** `test@riftshield.com` / `test123`

### 2.3 Detalhamento Cypress (45 casos)

| Spec | Casos | Tipo |
|---|---|---|
| `auth.cy.ts` | 4/4 ✅ | UI login/registro (intercept) |
| `dashboard.cy.ts` | 7/7 ✅ | UI dashboard (intercept) |
| `export.cy.ts` | 6/6 ✅ | UI exportação (intercept) |
| `inference.cy.ts` | 5/5 ✅ | UI inferência (intercept) |
| `main_flow.cy.ts` | 7/7 ✅ | Navegação sidebar (intercept) |
| `ui_features.cy.ts` | 2/2 ✅ | **Login real** — tema + i18n |
| `export_real.cy.ts` | 1/1 ✅ | **Backend real** — download JSON |
| `real_flows.cy.ts` | 2/2 ✅ | **Backend real** — logout + Hermes UI |
| `checklist_manual.cy.ts` | 11/11 ✅ | **Backend real** — checklist §10 completo |

### 2.4 Observações técnicas

- **pytest Windows:** plugin global `pytest-flask` conflita com FastAPI; usar `-p no:flask`.
- **E2E misto:** 29 specs usam `cy.intercept`; **16 specs** validam backend real (login JWT, YOLO, export, checklist §10).
- **Cookies localhost:** login via `cy.request` em `:3000` compartilha cookies com `:1999` (mesmo domínio); `createAdminInvite` limpa cookies após gerar convite.
- **Docker:** `DATABASE_URL=mongodb://mongo:27017/riftshield` configurado no `docker-compose.yml` para o container backend.

---

## 3. Quality Gate

| Critério | Threshold | Resultado | Status |
|---|---|---|---|
| Testes backend | 100% pass, 0 flaky | 116/116 ✅ | PASS |
| Testes Vitest | 100% pass | 35/35 ✅ | PASS |
| E2E smoke (P0) | ≥ 5 cenários | 45/45 ✅ | PASS |
| Checklist §10 E2E | 9 itens automatizados | 11/11 ✅ | PASS |
| Endpoints P0 | 100% com ≥1 teste | Cobertos ✅ | PASS |
| Health check API | OK | OK ✅ | PASS |
| CI Pipeline | Existente + ruff + eslint TS | `.github/workflows/ci.yml` ✅ | PASS |
| RBAC admin | Testes no CI | `test_security_rbac.py` ✅ | PASS |
| Bugs críticos abertos | 0 | 0 ✅ | PASS |

**Decisão automatizada:** `PASS`

> **Nota:** Hermes §10-07 valida UI sempre; resposta LLM real requer `HERMES_API_KEY` no `cypress.config.ts`.

---

## 4. Cobertura de testes vs. requisitos

### 4.1 O que está coberto

| Área | Evidência |
|---|---|
| Auth JWT + refresh + logout | `test_integration_auth`, `test_integration_register_refresh`, `test_api_interceptor` |
| RBAC admin (invite, train, activate) | `test_security_rbac.py`, `require_admin` em rotas admin |
| Inferência + STRIDE + CRUD | `test_inference.py`, `test_functional_inference_flow` |
| Smoke YOLO sem mock (REQ-04) | `test_yolo_smoke.py` — imagem real `46d09c7a4ed5_12-saga_pattern.png` |
| Dataset / training / KB / dashboard | `test_dataset.py`, `test_training.py`, `test_kb.py`, `test_dashboard.py` |
| Export / Hermes / Attack | `test_export_unit`, `test_hermes_integration`, `test_attack_integration` |
| Compare / suggest / fine-tune / perfil | `test_phase2_inference_training.py`, `test_integration_auth::test_update_profile` |
| Frontend services + i18n + AuthContext | 5 arquivos Vitest (35 testes) |
| E2E fluxos críticos UI | 9 specs Cypress (45 testes) |
| Checklist manual §10 | `checklist_manual.cy.ts` (11 casos, backend real) |

### 4.2 Lacunas de teste (abertas)

| Item | Status | Impacto |
|---|---|---|
| 29/45 Cypress com `cy.intercept` | Parcial | UI mockada; integração real coberta em 16 casos |
| Cobertura frontend (Vitest) | Gap | Sem gate de coverage no CI |
| `npm audit` high | Gap | Step no CI com `continue-on-error`; vulnerabilidades high pendentes |
| Hermes resposta LLM real | Parcial | UI testada; resposta depende de API key |

### 4.3 Lacunas fechadas (implementação 2026-07-20)

| Item | Situação anterior | Situação atual |
|---|---|---|
| RBAC (`test_security_rbac.py` na raiz) | Gap — fora do CI | ✅ `backend/src/tests/test_security_rbac.py` + `require_admin` |
| Smoke YOLO sem mock (REQ-04) | Gap | ✅ `test_yolo_smoke.py` |
| Hermes UI (REQ-12) | Gap | ✅ `real_flows.cy.ts`, `checklist_manual.cy.ts` §10-07 |
| Checklist manual §10 | Gap | ✅ `checklist_manual.cy.ts` (11 casos) |
| E2E export download (REQ-11) | Gap | ✅ `export_real.cy.ts`, `checklist_manual.cy.ts` §10-04 |
| E2E login/logout real | Parcial | ✅ `ui_features`, `real_flows`, `checklist_manual` §10-08 |

### 4.4 Itens do `qa.md` §6 desatualizados (já implementados)

| Req ID | Gap listado no qa.md | Situação atual |
|---|---|---|
| REQ-14 | Sem teste compare | `test_phase2_inference_training.py` |
| REQ-15 | Sem teste `PUT /me` | `test_integration_auth::test_update_profile` |
| REQ-01 | Falta `POST /invite` | `test_integration_auth::test_generate_invite_as_admin` + RBAC |
| REQ-02 | Falta E2E login real | `ui_features.cy.ts`, `checklist_manual.cy.ts` |
| REQ-04 | Smoke YOLO | `test_yolo_smoke.py` |
| REQ-11 | E2E export download | `export_real.cy.ts`, `checklist_manual.cy.ts` §10-04 |
| REQ-12 | Hermes UI | `real_flows.cy.ts`, `checklist_manual.cy.ts` §10-07 |

---

## 5. Análise best practices (skill)

Referência: `.cursor/skills/best-practices/SKILL.md` — segurança, compatibilidade browser e qualidade de código.

### 5.1 Scorecard consolidado

```
                    COBERTO    PARCIAL    GAP
Testes auto           ████████   ██        
CI / pipeline         ████████             
Compat. browser       ████████             
Auth JWT/cookies      ██████     ██        
Segurança HTTP/CSP    ████       ██    ██  
Lint TS/Python        ████       ██    ██  
Resiliência UI        ████       ██        
E2E integração real   ██████     ██        
Checklist manual QA   ████████             
```

| Área | Coberto | Parcial | Gap |
|---|---|---|---|
| **Segurança** | 5 | 4 | 3 |
| **Qualidade de código** | 4 | 4 | 2 |
| **Compatibilidade browser** | 6 | 0 | 0 |
| **Testes** | 7 | 2 | 1 |

### 5.2 Segurança

| Item | Status | Evidência / observação |
|---|---|---|
| HTTPS / sem mixed content | Parcial | Dev HTTP; HSTS apenas em `NODE_ENV=production` |
| Cookies seguros | Coberto | `auth_controller.py` + `refresh_middleware.py` usam `settings.is_production` |
| JWT + refresh | Coberto | `token.py`, interceptor `api.ts`, testes auth |
| CORS restrito | Coberto | `main.py` — origin = `FRONTEND_URL` |
| CSP | Parcial | `SecurityHeadersMiddleware` — CSP permissivo em dev, restritivo em prod |
| Security headers | Coberto | X-Frame-Options, nosniff, Referrer-Policy, Permissions-Policy, HSTS prod |
| `npm audit` | Parcial | Step no CI (`--audit-level=critical`, `continue-on-error`); high pendentes |
| Segredos no código | Coberto | Roboflow → `ROBOFLOW_API_KEY` env em `download_datasets.py` |
| Input sanitization | Coberto | Pydantic no backend; `rehype-sanitize` no Hermes (`ChatMessageList.tsx`) |
| RBAC admin | Coberto | `require_admin` em `/invite`, `/training/train`, `/fine-tune`, `/models/activate` |

### 5.3 Qualidade de código

| Item | Status | Evidência / observação |
|---|---|---|
| ESLint | Coberto | `eslint.config.js` cobre `**/*.{js,jsx,ts,tsx}` com `typescript-eslint` |
| Ruff backend | Coberto | `ruff check src/` no job backend CI; config em `pyproject.toml` |
| CI pipeline | Coberto | 3 jobs: pytest+cov+ruff, lint+vitest+audit, Cypress real |
| Error handling BE | Parcial | `AppError` + `ValidationError`; sem handler global 500 |
| Error handling FE | Parcial | Refresh token ok; `console.error` espalhado |
| React ErrorBoundary | Coberto | `ErrorBoundary.tsx` em `main.tsx` |
| Global error handlers | Coberto | `unhandledrejection` + `window.error` em `main.tsx` |
| Source maps prod | Parcial | Vite default ok; não explícito |

### 5.4 Compatibilidade browser

| Item | Status |
|---|---|
| `<!doctype html>` | Coberto |
| `charset` primeiro no `<head>` | Coberto |
| Viewport responsivo | Coberto |
| `lang="pt-BR"` | Coberto |
| APIs depreciadas | Coberto — não usadas no `src/` |
| Passive listeners | N/A |
| Feature detection vs userAgent | Coberto |

---

## 6. Checklist manual §10 (`qa.md`) — automatizado E2E

Spec: `frontend/cypress/e2e/checklist_manual.cy.ts` · Comandos: `cypress/support/commands.ts`

| Item | Status | Caso E2E |
|---|---|---|
| Registro com convite admin | ✅ | §10-01 — `createAdminInvite()` + registro UI |
| Upload diagrama → inferência → threats page | ✅ | §10-02 — `fixtures/diagram.png` + YOLO real |
| Filtro vulnerabilidades por categoria STRIDE | ✅ | §10-03 — filtro componente + busca por tag |
| Export PDF/JSON do relatório | ✅ | §10-04 — export real JSON + PDF |
| Toggle idioma PT ↔ EN em 3 páginas | ✅ | §10-05 — dashboard, inference, export |
| Toggle tema claro/escuro | ✅ | §10-06 — persistência após reload |
| Hermes chat (se API key configurada) | ✅ | §10-07 — UI sempre; LLM se `HERMES_API_KEY` |
| Logout + tentativa acesso rota protegida | ✅ | §10-08 — logout + bloqueio dashboard |
| Responsividade mobile (sidebar) | ✅ | §10-09 — viewport iPhone + drawer |

---

## 7. Débitos técnicos prioritários

### 7.1 Concluídos (2026-07-20)

| # | Ação | Área |
|---|---|---|
| 1 | `test_security_rbac.py` → `backend/src/tests/` + RBAC em `/invite` e training | Segurança / Testes |
| 3 | ESLint `.ts/.tsx` + `ruff check src/` no CI | Qualidade |
| 4 | `SecurityHeadersMiddleware` em `main.py` | Segurança |
| 5 | Roboflow → `ROBOFLOW_API_KEY` | Segurança |
| 6 | ErrorBoundary + `rehype-sanitize` Hermes | Qualidade |
| 7 | Specs Cypress backend real (`export_real`, `real_flows`, `checklist_manual`) | Testes |
| 8 | Checklist §10 → E2E automatizado | QA |
| 9 | Smoke YOLO `test_yolo_smoke.py` | Testes / ML |

### 7.2 Pendentes

| # | Ação | Área |
|---|---|---|
| 1 | `npm audit fix` + resolver vulnerabilidades high (axios, @babel/core, etc.) | Segurança |
| 2 | Gate de coverage Vitest no CI | Testes |
| 3 | Atualizar `qa.md` §6 (rastreabilidade desatualizada) | Documentação |
| 4 | TLS/HTTPS explícito em ambiente de produção | Segurança |

---

## 8. Comandos de reexecução

```bash
# Backend
cd backend
docker compose up -d
python -m pytest src/ -v -p no:flask
python -m ruff check src/

# Frontend unitário
cd frontend
npm run test:unit
npm run lint

# E2E completo (requer backend :3000 + frontend :1999)
cd backend && python scripts/seed.py   # DATABASE_URL=mongodb://127.0.0.1:27020/riftshield
cd frontend && npm run dev -- --port 1999
npx cypress run --browser chrome --headless

# Checklist §10 isolado
npx cypress run --spec cypress/e2e/checklist_manual.cy.ts --browser chrome --headless
```

---

## 9. Referências

| Documento | Caminho |
|---|---|
| Planejamento QA | `qa.md` |
| Evidências execução | `evidencias/2026-07-20/` |
| Resumo evidências | `evidencias/2026-07-20/RESUMO-EXECUCAO.md` |
| CI Pipeline | `.github/workflows/ci.yml` |
| Best practices skill | `.cursor/skills/best-practices/SKILL.md` |
| Checklist §10 E2E | `frontend/cypress/e2e/checklist_manual.cy.ts` |
| RBAC tests | `backend/src/tests/test_security_rbac.py` |
| YOLO smoke | `backend/src/tests/test_yolo_smoke.py` |

---

## 10. Investigação — E2E "verde local, vermelho no pipeline" (2026-07-22)

### 10.1 Contexto

Após corrigir um bug de "falso verde" no job `E2E (Cypress · Real Environment)` (o CI reportava `success` mesmo com testes falhando, por captura incorreta do exit code do Cypress no `ci.yml`), a execução real do pipeline passou a reportar o status verdadeiro: **exit code 27 → 27 de 45 testes falhando**, enquanto a mesma suíte passava 100% localmente. Investigação completa em [`RS-TESTS`](https://github.com/QARosa/RiftShield/tree/RS-TESTS), runs [#31](https://github.com/QARosa/RiftShield/actions/runs/29874601067) → [#32](https://github.com/QARosa/RiftShield/actions/runs/29880882027).

### 10.2 Causa raiz #1 (dominante) — idioma padrão dependente do locale do runner

`LanguageContext.tsx` decide o idioma inicial assim:

```ts
const saved = localStorage.getItem("rift_lang");
if (saved === "pt-BR" || saved === "en-US") return saved;
return navigator.language.startsWith("pt") ? "pt-BR" : "en-US";
```

Como nenhum hook do Cypress definia `rift_lang` antes da primeira renderização, o idioma inicial dependia do locale do **sistema operacional/navegador** que executa os testes:

- **Máquina local (Windows, locale `pt-BR`)** → app carrega em português → specs (que assumem cópia em PT por padrão) passam.
- **Runner `ubuntu-latest` do GitHub Actions (locale `en-US`)** → app carrega em inglês → todas as asserções de texto/`aria-label` em português falham (`"Detecção de Ameaças"`, `"Registre-se"`, `"Abrir Hermes"`, `"Total de Análises"`, etc.).

**Evidência empírica:** forçando `--lang=en-US` no Chrome local (simulando o runner do CI) sem a correção, os mesmos padrões de falha do CI reapareceram localmente (`auth.cy.ts` 3/4 falhando, `checklist_manual.cy.ts` 4/11 falhando, `dashboard.cy.ts` com falhas nos KPIs). Após a correção, a suíte completa passou 45/45 **tanto em `pt-BR` quanto em `--lang=en-US`**, comprovando que o fix remove a dependência do locale.

**Correção** (`frontend/cypress/support/e2e.ts`): forçar `rift_lang=pt-BR` via `Cypress.on("window:before:load", ...)` em toda carga de página, em todos os specs, independente do locale do runner.

### 10.3 Causa raiz #2 (pontual) — asserção ambígua em viewport mobile

`§10-09 — Responsividade mobile (sidebar)` falhava mesmo localmente: `loginAsTestAdmin()` (usado por todos os specs com backend real) validava a página logada com `cy.contains(/dashboard|painel|an[aá]lise/i)`, que também casa com os itens de navegação da sidebar (`"Dashboard"`, `"Análise de Diagramas"`). Em viewport mobile esses itens ficam em `display:none` (dentro do drawer recolhido), então o Cypress podia casar com um elemento oculto e expirar o timeout mesmo com o dashboard carregado corretamente.

**Correção** (`frontend/cypress/support/commands.ts`): escopar a asserção ao heading da página (`cy.contains("h2", /dashboard|painel/i)`), que é sempre visível independente do viewport.

### 10.4 Validação e resultado

| Etapa | Resultado |
|---|---|
| Local, Chrome headless, locale `pt-BR` (antes da correção) | 44/45 ✅ (1 falha: §10-09, causa raiz #2) |
| Local, Chrome headless, `--lang=en-US` forçado (antes da correção) | Múltiplas falhas — reproduz o padrão do CI |
| Local, Chrome headless, `pt-BR` (depois da correção) | **45/45 ✅** |
| Local, Chrome headless, `--lang=en-US` forçado (depois da correção) | **45/45 ✅** |
| CI — run [#32](https://github.com/QARosa/RiftShield/actions/runs/29880882027) (`ddad87a`), job `E2E (Cypress · Real Environment)` | **success** — sem screenshots de falha (step `Upload Cypress screenshots on failure` = *skipped*) |

**Commits:** `fix(e2e): force pt-BR language regardless of CI runner locale`, `fix(e2e): scope loginAsTestAdmin dashboard check to page heading` — 2 commits pequenos, um por causa raiz, um único novo run de CI para validar ambos.

### 10.5 Lição para o backlog de QA

- Nenhuma correção de conteúdo dos 9 specs foi necessária (a hipótese inicial de "drift de copy/seletor por spec" não se confirmou) — a causa era 100% ambiental (locale do runner), não drift de UI.
- Recomenda-se manter a skill [`ci-e2e-stabilization`](.cursor/skills/ci-e2e-stabilization/SKILL.md) atualizada com este caso: "specs passam local e falham 100% deterministicamente no CI" → suspeitar primeiro de diferenças de ambiente (locale, timezone, viewport, fonte) antes de reescrever specs.

---

## 11. Changelog do documento

| Versão | Data | Alterações |
|---|---|---|
| 1.0 | 2026-07-20 | Análise inicial — 176 testes, gaps identificados |
| 1.1 | 2026-07-20 | Implementações: RBAC, security headers, lint, ErrorBoundary, checklist §10 E2E, smoke YOLO — **196 testes** |
| 1.2 | 2026-07-22 | Investigação e correção do pipeline E2E: causa raiz de locale (idioma padrão dependente de `navigator.language` no runner `ubuntu-latest`) + asserção ambígua em viewport mobile. CI `E2E (Cypress · Real Environment)` voltou a **45/45 passing** (run #32) sem alterar conteúdo dos specs. |

---

*Documento gerado pela equipe QA — RiftShield TC Fase 5*
