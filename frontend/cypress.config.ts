import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    baseUrl: "http://localhost:1999",
    specPattern: "cypress/e2e/**/*.cy.ts",
    supportFile: "cypress/support/e2e.ts",
    downloadsFolder: "cypress/downloads",
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 8000,
    requestTimeout: 10000,
    env: {
      TEST_USER_EMAIL: "test@riftshield.com",
      TEST_USER_PASSWORD: "test123",
      API_URL: "http://localhost:3000",
      // Defina HERMES_API_KEY para validar resposta real do chat no §10-07
      HERMES_API_KEY: "",
    },
  },
});
