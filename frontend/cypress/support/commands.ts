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
  const apiUrl = (Cypress.env("API_URL") as string) || "http://127.0.0.1:3000";

  // API login is more reliable in CI than UI form (cookies shared across localhost ports)
  cy.request({
    method: "POST",
    url: `${apiUrl}/api/auth/login`,
    body: { email: ADMIN_EMAIL, password: ADMIN_PASSWORD },
    failOnStatusCode: true,
  }).then((res) => {
    expect(res.status).to.eq(200);
    expect(res.body).to.have.property("user");
  });

  cy.visit("/dashboard");
  cy.url({ timeout: 15000 }).should("include", "/dashboard");
  cy.contains(/dashboard|painel|an[aá]lise/i, { timeout: 15000 }).should("be.visible");
});

Cypress.Commands.add("createAdminInvite", () => {
  const apiUrl = (Cypress.env("API_URL") as string) || "http://127.0.0.1:3000";

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
