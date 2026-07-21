/**
 * TC-EXP-11: Export download with real backend (no cy.intercept)
 */
describe("TC-EXP-11: Export Download (Real Backend)", () => {
  beforeEach(() => {
    cy.loginAsTestAdmin();
  });

  it("downloads a JSON export file from the real API", () => {
    cy.visit("/export");
    cy.get("select").first().select("json");
    cy.get("button").contains(/exportar/i).click();
    cy.contains(/sucesso|downloaded|export/i, { timeout: 15000 }).should("be.visible");
  });
});
