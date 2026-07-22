---
name: ci-e2e-stabilization
description: Stabilizes flaky CI E2E pipelines with minimal-impact changes and fast root-cause triage. Use when GitHub Actions E2E jobs fail intermittently, especially Cypress browser crashes, Linux dependency issues, or CI-only test instability.
disable-model-invocation: true
---

# CI E2E Stabilization

## Goal
Close failing CI E2E pipelines with the smallest safe change set, avoiding long trial-and-error cycles.

## Principles
- Change CI orchestration first; avoid product code edits unless a functional bug is proven.
- Apply one focused hypothesis per run.
- Prefer deterministic browser/runtime choices over broad fallbacks.
- Keep reversibility high (small commits, clear messages).

## Fast Triage (5-10 minutes)
1. Get latest run status and jobs:
   - `GET /repos/{owner}/{repo}/actions/runs/{run_id}`
   - `GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs`
2. Identify first failing step (not downstream noise).
3. Read check annotations:
   - `GET /repos/{owner}/{repo}/check-runs/{check_run_id}/annotations?per_page=100`
4. Classify failure into one bucket:
   - `env-deps` (apt/package/runtime mismatch)
   - `browser-crash` (exit 27, renderer/dev-shm/GPU)
   - `test-functional` (assertions/timeouts in specs)
   - `startup-race` (backend/frontend not ready)

## Decision Matrix

### A) `env-deps`
- Keep strict install for core packages.
- Install variant packages as best-effort (`|| true`) only for non-critical libs.
- Avoid adding many optional packages blindly.

### B) `browser-crash`
- Prefer one stable browser in CI (usually `chrome --headless`).
- Avoid mixing unstable fallbacks in same run unless required.
- Ensure the script does not abort before fallback/retry logic runs.
- Use `xvfb-run` consistently with same server args.

### C) `startup-race`
- Add/adjust `wait-on` health checks and timeout.
- Keep explicit API smoke checks before E2E execution.
- Do not increase arbitrary `sleep` without a readiness probe.

### D) `test-functional`
- Treat as real defect or flaky selector issue.
- Fix minimal failing spec(s), not the entire suite behavior.
- Preserve local and CI parity for base URL, auth, and data setup.
- **Before touching individual specs**, check for one shared environmental
  cause first, especially if failures are widespread and deterministic
  (same specs, same assertions, every run) while 100% passing locally:
  - **OS/browser locale mismatch**: `ubuntu-latest` runners default to
    `en-US`; a dev machine may default to another locale. If the app
    derives language/format from `navigator.language` (or `Intl`) as a
    fallback, i18n-dependent assertions can fail identically across many
    specs. Force the locale/language deterministically in a global test
    hook (e.g. `localStorage` seed via `window:before:load`) instead of
    editing every spec's copy assertions.
  - Reproduce this class of bug locally *before* spending a CI run: launch
    the same browser with an explicit locale override (e.g. Chrome
    `--lang=en-US`) and confirm the same failure signature appears; then
    confirm the fix passes under both locales.
  - Timezone, viewport default, and font-rendering differences follow the
    same "check shared cause first" logic.

## Minimal-Impact Patch Order
1. Workflow shell/exit-code handling.
2. Browser strategy (single browser + retry).
3. Readiness/smoke gates.
4. Spec-level fixes (only if failures are functional).

## Commit Strategy
- One intent per commit:
  - `fix(ci): ...` for workflow/runtime changes
  - `fix(e2e): ...` for spec/test behavior changes
- Push and observe exactly one new run after each focused patch.

## Stop Conditions (avoid endless reruns)
Stop iterative CI tweaks and escalate if any is true:
- Same failing signature repeats after 2 focused CI commits.
- Different random failures across browsers without deterministic pattern.
- Runtime is stable but specs fail functionally in multiple unrelated areas.

Then propose migration path:
- Keep CI green with temporary stable profile.
- Start Playwright pilot for critical flows in parallel.

## Output Format for Updates
Always report:
1. Run ID and failing job/step.
2. Failure bucket (`env-deps`, `browser-crash`, `startup-race`, `test-functional`).
3. Exact minimal change applied.
4. New run URL.
5. Next decision if fail repeats.
