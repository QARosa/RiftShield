describe("Auth Flow (E2E)", () => {
  beforeEach(() => {
    // No auth needed — these tests exercise the login page directly
    cy.visit("/");
  });

  it("should show login form", () => {
    cy.contains("RiftShield").should("be.visible");
    cy.contains("Detecção de Ameaças").should("be.visible");
    cy.get('input[type="email"]').should("be.visible");
    cy.get('input[type="password"]').should("be.visible");
  });

  it("should toggle to register mode", () => {
    cy.contains("Registre-se").click();
    cy.contains("Crie sua conta").should("be.visible");
    cy.contains("Código de Convite").should("be.visible");
  });

  it("should show validation errors on empty login", () => {
    cy.get('button[type="submit"]').click();
    cy.get('input:invalid').should("have.length.at.least", 1);
  });

  it("should toggle language", () => {
    cy.get('[aria-label*="English"]').click();
    cy.contains("Threat Detection").should("be.visible");
    cy.get('[aria-label*="Português"]').click();
    cy.contains("Detecção de Ameaças").should("be.visible");
  });
});
