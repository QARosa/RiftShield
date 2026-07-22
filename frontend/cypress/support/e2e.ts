import "./commands";

/**
 * Force pt-BR as the app language for every E2E test, independent of the
 * OS/browser locale of the machine running Cypress.
 *
 * The app falls back to `navigator.language` when `localStorage.rift_lang`
 * is unset (see `frontend/src/context/LanguageContext.tsx`). Most specs
 * assert Portuguese copy by default, which matches developer machines
 * (commonly pt-BR locale) but not GitHub Actions `ubuntu-latest` runners,
 * whose default locale is en-US — causing widespread, CI-only assertion
 * failures on Portuguese text/aria-labels that never reproduce locally.
 */
Cypress.on("window:before:load", (win) => {
  win.localStorage.setItem("rift_lang", "pt-BR");
});
