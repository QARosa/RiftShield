/**
 * TC-INF-04: InferencePage — upload → analyze → display threats (E2E)
 * Uses cy.intercept to stub API calls so the test runs without a live backend.
 */

const USER = { id: "u1", name: "Rosali", email: "rosalijustino@hotmail.com", role: "ADMIN" };

const MOCK_INFERENCE = {
  id: "inf1",
  filename: "arch.png",
  status: "completed",
  components: [{ class_id: 0, label: "api-gateway", confidence: 0.95, bbox: { x: 0, y: 0, width: 50, height: 50 } }],
  processing_time_ms: 350,
  created_at: "2026-01-01T00:00:00",
};

const MOCK_THREAT_REPORT = {
  id: "thr1",
  inference_id: "inf1",
  status: "completed",
  stride_summary: { Spoofing: 1, Tampering: 0 },
  component_analyses: [
    {
      component_label: "api-gateway",
      component_class_id: 0,
      stride_threats: [{ category: "Spoofing", description: "Risco de spoofing no gateway", risk_level: "HIGH" }],
      vulnerabilities: [],
      countermeasures: [],
    },
  ],
  overall_risk_score: 0.6,
  created_at: "2026-01-01T00:00:00",
  updated_at: "2026-01-01T00:00:00",
};

describe("TC-INF-04: InferencePage — upload and analyze flow", () => {
  beforeEach(() => {
    // Stub auth so the app loads as authenticated
    cy.intercept("GET", "/api/users/me", { statusCode: 200, body: { user: USER } }).as("getMe");
    cy.intercept("GET", "/api/inference/reports*", { statusCode: 200, body: { total: 0, items: [] } }).as("getReports");
    cy.intercept("GET", "/api/inference/threats*", { statusCode: 200, body: { total: 0, items: [] } }).as("getThreats");
    cy.intercept("GET", "/api/dashboard/stats", { statusCode: 200, body: { total_analyses: 1, total_threats: 1, risk_distribution: {} } }).as("getDash");
    cy.intercept("GET", "/api/users/usage-time", { statusCode: 200, body: { total_seconds: 0, hours: 0, minutes: 0, seconds: 0 } }).as("getUsage");
    cy.visit("/inference");
  });

  it("renders the upload zone", () => {
    cy.contains("Análise de Diagramas").should("be.visible");
    cy.contains("Upload").should("be.visible");
  });

  it("upload tab shows drop zone", () => {
    cy.get('input[type="file"]').should("exist");
  });

  it("analyze button is disabled with no file", () => {
    cy.contains("button", /analis|analyze/i).should("be.disabled");
  });

  it("upload a file and trigger analysis → shows results", () => {
    cy.intercept("POST", "/api/inference/analyze-threat", {
      statusCode: 200,
      body: { inference: MOCK_INFERENCE, threat_report: MOCK_THREAT_REPORT },
    }).as("analyzeAndThreat");
    cy.intercept("GET", "/api/inference/reports*", { statusCode: 200, body: { total: 1, items: [MOCK_INFERENCE] } });
    cy.intercept("GET", "/api/inference/threats*", { statusCode: 200, body: { total: 1, items: [MOCK_THREAT_REPORT] } });

    // Upload file via the hidden file input
    cy.get('input[type="file"]').selectFile(
      { contents: Cypress.Buffer.from("fake-png"), fileName: "arch.png", mimeType: "image/png" },
      { force: true }
    );

    // File name should appear in preview area
    cy.contains("arch.png").should("be.visible");

    // Analyze button becomes enabled
    cy.contains("button", /analis|analyze/i).should("not.be.disabled").click();
    cy.wait("@analyzeAndThreat");

    // Results: at least one component label shown
    cy.contains("api-gateway", { timeout: 8000 }).should("be.visible");
  });

  it("reports tab shows previous analyses", () => {
    cy.intercept("GET", "/api/inference/reports*", { statusCode: 200, body: { total: 1, items: [MOCK_INFERENCE] } });
    cy.visit("/inference");
    cy.contains("Relatórios").click();
    cy.contains("arch.png").should("be.visible");
  });
});
