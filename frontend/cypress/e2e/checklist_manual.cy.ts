/**
 * QA Checklist Manual §10 — casos E2E com backend real
 * Ref: QA-Análise de Status do Projeto.md §6
 *
 * Requer: backend :3000 + frontend :1999 + seed (test@riftshield.com / test123)
 */
describe("QA Checklist §10 — Manual → E2E (backend real)", () => {
  // ─── §10-01: Registro com convite admin ───────────────────────────────────
  describe("§10-01 — Registro com convite admin", () => {
    it("registra novo usuário usando código gerado pelo admin via API", () => {
      cy.createAdminInvite().then((inviteCode) => {
        const email = `e2e-${Date.now()}@riftshield.com`;

        cy.visit("/");
        cy.get("#email", { timeout: 15000 }).should("be.visible");
        cy.get("a").contains(/registre-se|register/i).click();
        cy.get("#name", { timeout: 10000 }).should("be.visible");

        cy.get("#name").type("E2E Checklist User");
        cy.get("#email").clear().type(email);
        cy.get("#password").clear().type("TestPass123!");
        cy.get("#inviteCode").type(inviteCode);
        cy.get('button[type="submit"]').click();

        cy.url().should("include", "/dashboard", { timeout: 15000 });
        cy.contains(/e2e checklist user/i).should("be.visible");
      });
    });
  });

  // ─── §10-02: Upload → inferência → threats page ───────────────────────────
  describe("§10-02 — Upload diagrama → inferência → threats page", () => {
    beforeEach(() => {
      cy.loginAsTestAdmin();
    });

    it("envia diagrama, analisa e exibe relatório na página de ameaças", () => {
      cy.visit("/inference");

      cy.get('input[type="file"]').selectFile("cypress/fixtures/diagram.png", {
        force: true,
      });

      cy.contains(/diagram\.png|saga|preview/i, { timeout: 5000 }).should("exist");
      cy.get("button").contains(/analisar|analyze/i).click();

      cy.contains(/componentes|components/i, { timeout: 120000 }).should("be.visible");
      cy.contains(/ameaças|threats|risco/i).should("be.visible");

      cy.visit("/threats");
      cy.contains(/relatório|report|ameaças|threats/i).should("be.visible");
      cy.get("button").contains(/detalhes|details/i).should("have.length.at.least", 1);
    });
  });

  // ─── §10-03: Filtro vulnerabilidades (componente / tag STRIDE) ────────────
  describe("§10-03 — Filtro vulnerabilidades por categoria", () => {
    beforeEach(() => {
      cy.loginAsTestAdmin();
    });

    it("filtra vulnerabilidades por componente e por tag STRIDE via busca", () => {
      cy.visit("/vulnerabilities");
      cy.contains(/vulnerabilidades|vulnerabilities/i).should("be.visible");

      cy.get("select").select("database");
      cy.contains(/database|banco de dados/i, { timeout: 10000 }).should("be.visible");
      cy.contains(/injeção|injection|sql/i).should("be.visible");

      cy.visit("/vulnerabilities");
      cy.get('input[placeholder*="Buscar"], input[placeholder*="Search"]')
        .clear()
        .type("Autenticação{enter}");
      cy.contains(/autenticação|authentication/i, { timeout: 10000 }).should("be.visible");
    });
  });

  // ─── §10-04: Export PDF/JSON ──────────────────────────────────────────────
  describe("§10-04 — Export PDF/JSON do relatório", () => {
    beforeEach(() => {
      cy.loginAsTestAdmin();
    });

    it("exporta relatório em JSON e PDF via API real", () => {
      cy.visit("/export");

      cy.get("select").first().select("json");
      cy.get("button").contains(/exportar|export/i).click();
      cy.contains(/sucesso|success|downloaded|export/i, { timeout: 15000 }).should(
        "be.visible",
      );

      cy.get("select").first().select("pdf");
      cy.get("button").contains(/exportar|export/i).click();
      cy.contains(/sucesso|success|downloaded|export/i, { timeout: 15000 }).should(
        "be.visible",
      );
    });
  });

  // ─── §10-05: Toggle idioma PT ↔ EN em 3 páginas ───────────────────────────
  describe("§10-05 — Toggle idioma PT ↔ EN em 3 páginas", () => {
    beforeEach(() => {
      cy.loginAsTestAdmin();
    });

    const pages = [
      { path: "/dashboard", pt: /análise de diagramas|painel/i, en: /diagram analysis|dashboard/i },
      { path: "/inference", pt: /análise de diagramas|upload/i, en: /diagram analysis|upload/i },
      { path: "/export", pt: /exportar|exportação/i, en: /export/i },
    ];

    pages.forEach(({ path, pt, en }) => {
      it(`alterna idioma em ${path}`, () => {
        cy.visit(path);
        cy.contains(pt).should("be.visible");

        cy.toggleLanguage("en");
        cy.contains(en).should("be.visible");

        cy.toggleLanguage("pt");
        cy.contains(pt).should("be.visible");
      });
    });
  });

  // ─── §10-06: Toggle tema claro/escuro ──────────────────────────────────────
  describe("§10-06 — Toggle tema claro/escuro", () => {
    beforeEach(() => {
      cy.loginAsTestAdmin();
    });

    it("alterna tema e persiste após reload", () => {
      cy.get("html").should("have.attr", "data-theme", "dark");

      cy.toggleTheme("light");
      cy.reload();
      cy.url().should("include", "/dashboard");
      cy.get("html").should("have.attr", "data-theme", "light");

      cy.toggleTheme("dark");
      cy.get("html").should("have.attr", "data-theme", "dark");
    });
  });

  // ─── §10-07: Hermes chat ──────────────────────────────────────────────────
  describe("§10-07 — Hermes chat", () => {
    beforeEach(() => {
      cy.loginAsTestAdmin();
    });

    it("abre painel Hermes e envia mensagem (resposta real se API key configurada)", () => {
      cy.get('button[aria-label="Abrir Hermes"]').click();
      cy.contains(/Hermes/i).should("be.visible");

      const testMessage = "Quais ameaças STRIDE afetam uma API REST?";
      cy.get('input[placeholder*="Hermes"], input[placeholder*="segurança"], input[placeholder*="security"]')
        .type(`${testMessage}{enter}`);

      if (Cypress.env("HERMES_API_KEY")) {
        cy.contains(/spoofing|tampering|STRIDE|autenticação|authentication/i, {
          timeout: 60000,
        }).should("be.visible");
      } else {
        cy.log("HERMES_API_KEY não configurada — validando apenas UI do chat");
        cy.get('input[placeholder*="Hermes"], input[placeholder*="segurança"], input[placeholder*="security"]')
          .should("be.visible");
      }
    });
  });

  // ─── §10-08: Logout + rota protegida ──────────────────────────────────────
  describe("§10-08 — Logout + tentativa acesso rota protegida", () => {
    beforeEach(() => {
      cy.loginAsTestAdmin();
    });

    it("logout encerra sessão e bloqueia dashboard", () => {
      cy.toggleLanguage("pt");
      cy.get(
        'button[aria-label="Sair"], button[aria-label="Logout"], button[title="Sair"], button[title="Logout"]',
      )
        .first()
        .click({ force: true });

      cy.url({ timeout: 15000 }).should("eq", `${Cypress.config().baseUrl}/`);
      cy.get("#email").should("be.visible");

      cy.visit("/dashboard");
      cy.get("#email", { timeout: 10000 }).should("be.visible");
      cy.contains(/distribuição stride|stride distribution/i).should("not.exist");
    });
  });

  // ─── §10-09: Responsividade mobile (sidebar) ──────────────────────────────
  describe("§10-09 — Responsividade mobile (sidebar)", () => {
    beforeEach(() => {
      cy.viewport("iphone-x");
      cy.loginAsTestAdmin();
    });

    it("exibe menu hambúrguer e drawer de navegação no mobile", () => {
      cy.get('button[aria-label="Abrir menu"]').should("be.visible").click();
      cy.get('button[aria-label="Close"]', { timeout: 10000 }).should("be.visible");

      cy.get('[role="dialog"]').within(() => {
        cy.contains(/análise de diagramas|diagram analysis/i).click();
      });

      cy.url().should("include", "/inference");
    });
  });
});
