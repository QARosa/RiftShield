const USER = { id: "u1", name: "Rosali", email: "rosalijustino@hotmail.com", role: "ADMIN" };

const MOCK_STATS = {
  total_analyses: 5,
  total_threats: 10,
  completed_analyses: 4,
  failed_analyses: 1,
  total_components_analyzed: 17,
  threats_by_risk: { critical: 0, high: 2, medium: 3, low: 5 },
  stride_distribution: { spoofing: 1, tampering: 1, denial_of_service: 1 },
  top_components: [{ label: "api_gateway", count: 4 }],
  recent_analyses: [],
};

describe("Main Application Flow (E2E)", () => {
  beforeEach(() => {
    cy.intercept("GET", "/api/users/me", { statusCode: 200, body: { user: USER } }).as("getMe");
    cy.intercept("GET", "/api/dashboard/stats", { statusCode: 200, body: MOCK_STATS });
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
    cy.visit("/dashboard");
    cy.get('[aria-label="Abrir menu"]').click();
    cy.contains("Exportação").should("exist");
    cy.get('[aria-label="Close"]').click();
  });

  it("should show usage time in sidebar", () => {
    cy.contains("Tempo de Uso").should("exist");
  });

  it("should toggle theme", () => {
    cy.get('button[aria-label*="tema"]').first().click({ force: true });
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
