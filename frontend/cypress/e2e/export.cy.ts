/**
 * TC-EXP-04: ExportPage — format selection + submit (E2E)
 * Uses cy.intercept to run without a live backend.
 */
const USER = { id: "u1", name: "Rosali", email: "rosalijustino@hotmail.com", role: "ADMIN" };

describe("TC-EXP-04: Export Flow (E2E)", () => {
  beforeEach(() => {
    cy.intercept("GET", "/api/users/me", { statusCode: 200, body: { user: USER } }).as("getMe");
    cy.intercept("GET", "/api/users/usage-time", { statusCode: 200, body: { total_seconds: 0, hours: 0, minutes: 0, seconds: 0 } });
    cy.intercept("GET", "/api/dashboard/stats", { statusCode: 200, body: { total_analyses: 0, total_threats: 0, risk_distribution: {} } });
    cy.visit("/export");
  });

  it("renders the export page sections", () => {
    cy.contains("Seções para Exportar").should("be.visible");
    cy.contains("Formato e Opções").should("be.visible");
  });

  it("all sections are checked by default", () => {
    cy.get('input[type="checkbox"]').should("have.length.at.least", 6);
    cy.get('input[type="checkbox"]').each(($el) => {
      cy.wrap($el).should("be.checked");
    });
  });

  it("selects different export formats", () => {
    const formats = ["csv", "excel", "pdf", "json"];
    formats.forEach((fmt) => {
      cy.get("select").first().select(fmt);
      cy.get("select").first().should("have.value", fmt);
    });
  });

  it("toggles zip output switch", () => {
    cy.get('[role="switch"]').first().click();
    cy.get('[role="switch"]').first().should("have.attr", "aria-checked", "true");
  });

  it("shows warning toast when no section is selected", () => {
    cy.get('input[type="checkbox"]').uncheck({ multiple: true });
    cy.get("button").contains(/exportar/i).click();
    // Toast warning or inline message should appear
    cy.contains(/selecione|seção|section/i).should("be.visible");
  });

  it("triggers export POST request when all valid", () => {
    cy.intercept("POST", "/api/export/export", {
      statusCode: 200,
      body: { filename: "export_2026.json", content: "{}", error: null },
    }).as("doExport");

    cy.get("select").first().select("json");
    cy.get("button").contains(/exportar/i).click();
    cy.wait("@doExport").its("request.body").should("include", { format: "json" });
  });
});

