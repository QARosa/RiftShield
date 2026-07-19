import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    baseUrl: "http://localhost:1999",
    specPattern: "cypress/e2e/**/*.cy.ts",
    supportFile: false,
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 8000,
    requestTimeout: 10000,
    env: {
      // Seed user created via backend bootstrap (rosalijustino@hotmail.com / senha123)
      TEST_USER_EMAIL: "rosalijustino@hotmail.com",
      TEST_USER_PASSWORD: "senha123",
      API_URL: "http://localhost:3000",
    },
  },
});
