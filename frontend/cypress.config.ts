import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    baseUrl: "http://127.0.0.1:1999",
    specPattern: "cypress/e2e/**/*.cy.ts",
    supportFile: "cypress/support/e2e.ts",
    downloadsFolder: "cypress/downloads",
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 15000,
    env: {
      TEST_USER_EMAIL: "test@riftshield.com",
      TEST_USER_PASSWORD: "test123",
      API_URL: "http://127.0.0.1:3000",
      // Defina HERMES_API_KEY para validar resposta real do chat no §10-07
      HERMES_API_KEY: "",
    },
    setupNodeEvents(on) {
      // Prevent Chrome renderer crash (exit 27) in CI environments where
      // /dev/shm is limited (64 MB). These flags are safe locally too.
      on("before:browser:launch", (browser, launchOptions) => {
        if (browser.family === "chromium" && browser.name !== "electron") {
          launchOptions.args.push("--disable-dev-shm-usage");
          launchOptions.args.push("--no-sandbox");
          launchOptions.args.push("--disable-gpu");
        }
        return launchOptions;
      });
    },
  },
});
