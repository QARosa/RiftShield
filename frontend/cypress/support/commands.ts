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
      stubAuthenticatedSession(user?: {
        id: string;
        name: string;
        email: string;
        role?: string;
      }): Chainable<void>;
    }
  }
}

/**
 * UI login through Vite (/api proxy) so the browser cookie jar gets HttpOnly
 * cookies on the same origin as cy.visit (baseUrl :1999).
 * cy.request to :3000 stores cookies under a different origin and breaks CI.
 */
Cypress.Commands.add("loginAsTestAdmin", () => {
  cy.visit("/");
  cy.get("#email", { timeout: 15000 }).should("be.visible").clear().type(ADMIN_EMAIL);
  cy.get("#password").clear().type(ADMIN_PASSWORD);
  cy.get('button[type="submit"]').click();
  cy.url({ timeout: 20000 }).should("include", "/dashboard");
  cy.contains(/dashboard|painel|an[aá]lise/i, { timeout: 15000 }).should(
    "be.visible",
  );
});

Cypress.Commands.add("createAdminInvite", () => {
  // Authenticate in the browser first (cookies on :1999), then call invite via proxy
  cy.visit("/");
  cy.get("#email", { timeout: 15000 }).should("be.visible").clear().type(ADMIN_EMAIL);
  cy.get("#password").clear().type(ADMIN_PASSWORD);
  cy.get('button[type="submit"]').click();
  cy.url({ timeout: 20000 }).should("include", "/dashboard");

  return cy
    .request({
      method: "POST",
      url: "/api/auth/invite",
      failOnStatusCode: true,
    })
    .then((response) => {
      expect(response.body.invite.code).to.be.a("string").and.not.be.empty;
      const code = response.body.invite.code as string;
      cy.clearAllCookies();
      return cy.wrap(code);
    });
});

/** Stub /users/me (+ refresh) so mocked specs authenticate without real cookies. */
Cypress.Commands.add("stubAuthenticatedSession", (user) => {
  const sessionUser = user ?? {
    id: "u1",
    name: "Rosali",
    email: "rosalijustino@hotmail.com",
    role: "ADMIN",
  };
  cy.intercept("GET", "**/api/users/me*", {
    statusCode: 200,
    body: { user: sessionUser },
  }).as("getMe");
  cy.intercept("POST", "**/api/auth/refresh*", {
    statusCode: 200,
    body: { message: "ok" },
  }).as("refresh");
  cy.intercept("GET", "**/api/users/usage-time*", {
    statusCode: 200,
    body: { total_seconds: 3661, hours: 1, minutes: 1, seconds: 1 },
  }).as("getUsage");
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
