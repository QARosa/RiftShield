/**
 * TC-DASH-02: Dashboard — KPIs after login (E2E)
 * Uses cy.intercept to stub API calls.
 */

const USER = { id: "u1", name: "Rosali", email: "rosalijustino@hotmail.com", role: "ADMIN" };

const MOCK_STATS = {
  total_analyses: 12,
  total_threats: 34,
  completed_analyses: 10,
  failed_analyses: 2,
  total_components_analyzed: 55,
  threats_by_risk: { critical: 1, high: 5, medium: 10, low: 18 },
  total_dataset_entries: 8,
  total_training_runs: 2,
  stride_distribution: { spoofing: 2, tampering: 3, denial_of_service: 1 },
  top_components: [{ label: "api_gateway", count: 10 }],
  recent_analyses: [],
};

describe("TC-DASH-02: Dashboard — KPIs after login", () => {
  beforeEach(() => {
    cy.intercept("GET", "/api/users/me", { statusCode: 200, body: { user: USER } }).as("getMe");
    cy.intercept("GET", "/api/dashboard/stats", { statusCode: 200, body: MOCK_STATS }).as("getStats");
    cy.intercept("GET", "/api/users/usage-time", { statusCode: 200, body: { total_seconds: 3661, hours: 1, minutes: 1, seconds: 1 } }).as("getUsage");
    cy.visit("/dashboard");
  });

  it("renders dashboard heading", () => {
    cy.contains("Dashboard").should("be.visible");
  });

  it("displays Total de Análises KPI with value", () => {
    cy.wait("@getStats");
    cy.contains("Total de Análises").should("be.visible");
    cy.contains("12").should("be.visible");
  });

  it("displays Total de Ameaças KPI with value", () => {
    cy.wait("@getStats");
    cy.contains("Total de Ameaças").should("be.visible");
    cy.contains("34").should("be.visible");
  });

  it("sidebar shows user name", () => {
    cy.contains("Rosali").should("be.visible");
  });

  it("sidebar shows usage time", () => {
    cy.wait("@getUsage");
    cy.contains("Tempo de Uso").should("exist");
  });

  it("navigates to InferencePage via sidebar link", () => {
    cy.intercept("GET", "/api/inference/reports*", { statusCode: 200, body: { total: 0, items: [] } });
    cy.intercept("GET", "/api/inference/threats*", { statusCode: 200, body: { total: 0, items: [] } });
    cy.contains("Análise de Diagramas").click();
    cy.url().should("include", "/inference");
  });

  it("navigates to ExportPage via sidebar link", () => {
    cy.contains("Exportação").click();
    cy.url().should("include", "/export");
  });
});
