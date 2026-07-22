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

function applyAuthCookiesFromLoginBody(body: {
  accessToken?: string;
  refreshToken?: string;
}) {
  if (body.accessToken) {
    cy.setCookie("accessToken", body.accessToken, {
      path: "/",
      httpOnly: true,
      secure: false,
      sameSite: "lax",
    });
  }
  if (body.refreshToken) {
    cy.setCookie("refreshToken", body.refreshToken, {
      path: "/api/auth",
      httpOnly: true,
      secure: false,
      sameSite: "lax",
    });
  }
}

/**
 * Login via same-origin /api (Vite proxy) + explicit cy.setCookie from JSON tokens.
 * HttpOnly Set-Cookie via cy.request alone is unreliable across CI proxy setups.
 */
Cypress.Commands.add("loginAsTestAdmin", () => {
  cy.request({
    method: "POST",
    url: "/api/auth/login",
    body: { email: ADMIN_EMAIL, password: ADMIN_PASSWORD },
    failOnStatusCode: true,
  }).then((res) => {
    expect(res.status).to.eq(200);
    expect(res.body).to.have.property("user");
    expect(res.body).to.have.property("accessToken");
    applyAuthCookiesFromLoginBody(res.body);
  });

  cy.visit("/dashboard");
  cy.url({ timeout: 20000 }).should("include", "/dashboard");
  // Scope to the page heading (<h2>) instead of a bare text match: sidebar
  // nav items share the same words ("Dashboard", "Análise de Diagramas")
  // and stay in the DOM (display:none) behind the mobile hamburger menu,
  // so an unscoped cy.contains() can match a hidden element on mobile
  // viewports and time out even though the dashboard loaded correctly.
  cy.contains("h2", /dashboard|painel/i, { timeout: 15000 }).should(
    "be.visible",
  );
});

Cypress.Commands.add("createAdminInvite", () => {
  return cy
    .request({
      method: "POST",
      url: "/api/auth/login",
      body: { email: ADMIN_EMAIL, password: ADMIN_PASSWORD },
      failOnStatusCode: true,
    })
    .then((res) => {
      applyAuthCookiesFromLoginBody(res.body);
    })
    .then(() =>
      cy.request({
        method: "POST",
        url: "/api/auth/invite",
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
