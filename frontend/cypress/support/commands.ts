/// <reference types="cypress" />

const ADMIN_EMAIL = "test@riftshield.com";
const ADMIN_PASSWORD = "test123";

declare global {
  namespace Cypress {
    interface Chainable {
      loginAsTestAdmin(): Chainable<void>;
      createAdminInvite(): Chainable<string>;
      toggleLanguage(to: "en" | "pt"): Chainable<void>;
      toggleTheme(to: "light" | "dark"): Chainable<void>;
    }
  }
}

Cypress.Commands.add("loginAsTestAdmin", () => {
  cy.visit("/");
  cy.get("#email").clear().type(ADMIN_EMAIL);
  cy.get("#password").clear().type(ADMIN_PASSWORD);
  cy.get('button[type="submit"]').click();
  cy.url().should("include", "/dashboard", { timeout: 15000 });
});

Cypress.Commands.add("createAdminInvite", () => {
  const apiUrl = Cypress.env("API_URL") as string;

  return cy
    .request({
      method: "POST",
      url: `${apiUrl}/api/auth/login`,
      body: { email: ADMIN_EMAIL, password: ADMIN_PASSWORD },
      failOnStatusCode: true,
    })
    .then(() =>
      cy.request({
        method: "POST",
        url: `${apiUrl}/api/auth/invite`,
        failOnStatusCode: true,
      }),
    )
    .then((response) => {
      expect(response.body.invite.code).to.be.a("string").and.not.be.empty;
      const code = response.body.invite.code as string;
      cy.clearAllCookies();
      return cy.wrap(code);
    });
});

Cypress.Commands.add("toggleLanguage", (to: "en" | "pt") => {
  const enLabel = '[aria-label="Switch to English"]';
  const ptLabel = '[aria-label="Mudar para Português"]';

  if (to === "en") {
    cy.get("body").then(($body) => {
      if ($body.find(enLabel).length) {
        cy.get(enLabel).click();
      }
    });
  } else {
    cy.get("body").then(($body) => {
      if ($body.find(ptLabel).length) {
        cy.get(ptLabel).click();
      }
    });
  }
});

Cypress.Commands.add("toggleTheme", (to: "light" | "dark") => {
  cy.get("html").then(($html) => {
    const current = $html.attr("data-theme") || "dark";
    if (current !== to) {
      const label =
        to === "light" ? "Mudar para tema claro" : "Mudar para tema escuro";
      cy.get(`button[aria-label="${label}"]`).click();
      cy.get("html").should("have.attr", "data-theme", to);
    }
  });
});

export {};
