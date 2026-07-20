/**
 * TC-UI-01: Theme Toggle Functionality
 *
 * Validates the light/dark theme switching and its persistence across page reloads.
 */
describe("UI Features", () => {
  beforeEach(() => {
    // Perform login with real credentials
    cy.visit("/login");
    cy.get('input[name="email"]').type("test@riftshield.com");
    cy.get('input[name="password"]').type("test123");
    cy.get('button[type="submit"]').click();
    cy.url().should("include", "/dashboard", { timeout: 10000 });
  });

  it("TC-UI-01: should toggle between light and dark themes and persist the choice", () => {
    // 1. Verify initial theme is light
    cy.get("html").should("have.attr", "data-theme", "light");

    // 2. Click toggle to switch to dark theme
    cy.get('button[aria-label="Toggle theme"]').click();
    cy.get("html").should("have.attr", "data-theme", "dark");

    // 3. Reload the page and verify theme is persisted
    cy.reload();
    cy.contains("h1", "Dashboard").should("be.visible"); // Wait for page to be ready
    cy.get("html").should("have.attr", "data-theme", "dark");

    // 4. Click toggle again to switch back to light theme
    cy.get('button[aria-label="Toggle theme"]').click();
    cy.get("html").should("have.attr", "data-theme", "light");
  });

  it("TC-UI-02: should switch language and reflect on the UI", () => {
    // 1. Verify initial language is Portuguese by checking a sidebar link
    cy.contains("nav a", "Análise de Diagramas").should("be.visible");

    // 2. Navigate to profile page to change language
    cy.contains("nav a", "Perfil").click();
    cy.url().should("include", "/profile");
    cy.contains("h1", "Perfil").should("be.visible");

    // 3. Switch language to English
    cy.contains("button", "Inglês").click();

    // 4. Verify the profile page title is now in English
    cy.contains("h1", "Profile").should("be.visible");

    // 5. Verify a sidebar link is now in English
    cy.contains("nav a", "Diagram Analysis").should("be.visible");
  });
});