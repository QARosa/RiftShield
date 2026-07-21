/**
 * TC-UI-01 / TC-UI-02 — Theme toggle and i18n (real backend login)
 */
describe("UI Features", () => {
  beforeEach(() => {
    cy.loginAsTestAdmin();
  });

  it("TC-UI-01: should toggle between light and dark themes and persist the choice", () => {
    cy.get("html").should("have.attr", "data-theme", "dark");

    cy.get('button[aria-label="Mudar para tema claro"]').click();
    cy.get("html").should("have.attr", "data-theme", "light");

    cy.reload();
    cy.contains(/dashboard|painel/i).should("be.visible");
    cy.get("html").should("have.attr", "data-theme", "light");

    cy.get('button[aria-label="Mudar para tema escuro"]').click();
    cy.get("html").should("have.attr", "data-theme", "dark");
  });

  it("TC-UI-02: should switch language and reflect on the UI", () => {
    cy.contains("Análise de Diagramas").should("be.visible");

    cy.get('[aria-label="Switch to English"]').click();

    cy.contains("Diagram Analysis").should("be.visible");
    cy.contains(/dashboard/i).should("be.visible");
  });
});
