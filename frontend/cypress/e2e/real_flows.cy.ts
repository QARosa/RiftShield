/**
 * TC-UI-03 / TC-HERMES-01 — Logout and Hermes UI (real backend login)
 */
describe("Real Backend UI Flows", () => {
  beforeEach(() => {
    cy.loginAsTestAdmin();
  });

  it("TC-UI-03: logout clears session and blocks protected routes", () => {
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
  });

  it("TC-HERMES-01: opens Hermes chat panel and shows input", () => {
    cy.get('button[aria-label="Abrir Hermes"]').should("be.visible").click();
    cy.contains(/Hermes/i).should("be.visible");
    cy.get('input[placeholder*="Hermes"], input[placeholder*="segurança"]').should("be.visible");
  });
});
