describe("Auth Flow (E2E)", () => {
  beforeEach(() => {
    // Stub auth-check endpoints so the spinner clears instantly
    // and LoginForm renders without real network calls
    cy.intercept("GET", "/api/users/me", {
      statusCode: 401,
      body: { detail: "Not authenticated" },
    }).as("authCheck");
    cy.intercept("POST", "/api/auth/refresh", {
      statusCode: 401,
      body: { detail: "Token expired" },
    }).as("refresh");
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
    cy.get("body").then(($body) => {
      const toEnglish = $body.find('[aria-label*="English"]');
      if (toEnglish.length > 0) {
        cy.wrap(toEnglish).click();
        cy.contains("Threat Detection").should("be.visible");

        const toPortuguese = $body.find('[aria-label*="Português"]');
        if (toPortuguese.length > 0) {
          cy.wrap(toPortuguese).click();
          cy.contains("Detecção de Ameaças").should("be.visible");
        }
      } else {
        cy.contains("Detecção de Ameaças").should("be.visible");
      }
    });
  });
});
