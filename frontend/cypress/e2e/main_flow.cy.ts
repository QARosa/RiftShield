const USER = { id: "u1", name: "Rosali", email: "rosalijustino@hotmail.com", role: "ADMIN" };

describe("Main Application Flow (E2E)", () => {
  beforeEach(() => {
    cy.intercept("GET", "/api/users/me", { statusCode: 200, body: { user: USER } }).as("getMe");
    cy.intercept("GET", "/api/dashboard/stats", { statusCode: 200, body: { total_analyses: 5, total_threats: 10, risk_distribution: {} } });
    cy.intercept("GET", "/api/users/usage-time", { statusCode: 200, body: { total_seconds: 7200, hours: 2, minutes: 0, seconds: 0 } });
    cy.visit("/dashboard");
  });

  it("should navigate to all pages via sidebar", () => {
    const pages = [
      { label: "Dashboard", path: "/dashboard" },
      { label: "Análise de Diagramas", path: "/inference" },
      { label: "Dataset", path: "/dataset" },
      { label: "Treinamento", path: "/training" },
      { label: "Exportação", path: "/export" },
    ];

    pages.forEach((page) => {
      cy.contains(page.label).click();
      cy.url().should("include", page.path);
    });
  });

  it("should render dashboard stats", () => {
    cy.contains("Total de Análises").should("be.visible");
    cy.contains("Total de Ameaças").should("be.visible");
  });

  it("should open and close sidebar on mobile", () => {
    cy.viewport(375, 667);
    cy.get('[aria-label="Abrir menu"]').click();
    cy.contains("Exportação").should("be.visible");
    cy.get('[aria-label="Close"]').click();
  });

  it("should show usage time in sidebar", () => {
    cy.contains("Tempo de Uso").should("be.visible");
  });

  it("should toggle theme", () => {
    cy.get("header").within(() => {
      cy.get("button").eq(0).click();
    });
  });

  it("should open profile page", () => {
    cy.contains("Perfil").click();
    cy.url().should("include", "/profile");
    cy.contains("Informações Pessoais").should("be.visible");
  });

  it("should open settings page", () => {
    cy.contains("Configurações").click();
    cy.url().should("include", "/settings");
  });
});
