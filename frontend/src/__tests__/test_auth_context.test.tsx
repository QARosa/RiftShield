/**
 * TC-FE-01: AuthContext — refresh on mount
 *
 * Tests the checkSession() logic inside AuthProvider:
 *  1. /users/me succeeds  → user is populated
 *  2. /users/me fails, /auth/refresh succeeds → user is populated via retry
 *  3. both /users/me and /auth/refresh fail → user is null (logged out)
 *  4. signIn() sets the user object
 *  5. signOut() calls /auth/logout and clears the user
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import React from "react";
import { MemoryRouter } from "react-router-dom";

// ── Mock dependencies ──────────────────────────────────────────────────────
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return { ...actual, useNavigate: () => mockNavigate };
});

const mockApi = { get: vi.fn(), post: vi.fn() };
vi.mock("../middleware/api", () => ({ default: mockApi }));

// ── Helper: wrap AuthProvider in a MemoryRouter ───────────────────────────
function wrapper({ children }: { children: React.ReactNode }) {
  return <MemoryRouter>{children}</MemoryRouter>;
}

// ── Import after mocks are set up ─────────────────────────────────────────
async function importContext() {
  const mod = await import("../context/AuthContext");
  return mod;
}

// ─────────────────────────────────────────────────────────────────────────
describe("TC-FE-01: AuthContext — checkSession on mount", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  it("populates user when GET /users/me succeeds", async () => {
    const { AuthProvider, useAuth } = await importContext();

    mockApi.get.mockResolvedValueOnce({
      data: { user: { id: "u1", name: "Rosali", email: "r@test.com", role: "ADMIN" } },
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => (
        <MemoryRouter>
          <AuthProvider>{children}</AuthProvider>
        </MemoryRouter>
      ),
    });

    await waitFor(() => expect(result.current.loadingAuth).toBe(false));
    expect(result.current.user?.email).toBe("r@test.com");
    expect(result.current.isAuthenticated).toBe(true);
  });

  it("retries via /auth/refresh when /users/me fails then succeeds", async () => {
    const { AuthProvider, useAuth } = await importContext();

    mockApi.get
      .mockRejectedValueOnce(new Error("401"))
      .mockResolvedValueOnce({
        data: { user: { id: "u2", name: "Retry", email: "retry@test.com" } },
      });
    mockApi.post.mockResolvedValueOnce({});

    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => (
        <MemoryRouter>
          <AuthProvider>{children}</AuthProvider>
        </MemoryRouter>
      ),
    });

    await waitFor(() => expect(result.current.loadingAuth).toBe(false));
    expect(result.current.user?.email).toBe("retry@test.com");
    expect(mockApi.post).toHaveBeenCalledWith("/auth/refresh");
  });

  it("sets user to null when both /users/me and /auth/refresh fail", async () => {
    const { AuthProvider, useAuth } = await importContext();

    mockApi.get.mockRejectedValue(new Error("401"));
    mockApi.post.mockRejectedValue(new Error("401"));

    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => (
        <MemoryRouter>
          <AuthProvider>{children}</AuthProvider>
        </MemoryRouter>
      ),
    });

    await waitFor(() => expect(result.current.loadingAuth).toBe(false));
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it("signIn sets user and navigates to dashboard", async () => {
    const { AuthProvider, useAuth } = await importContext();

    mockApi.get.mockRejectedValue(new Error("401"));
    mockApi.post.mockRejectedValue(new Error("401"));

    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => (
        <MemoryRouter>
          <AuthProvider>{children}</AuthProvider>
        </MemoryRouter>
      ),
    });

    await waitFor(() => expect(result.current.loadingAuth).toBe(false));

    act(() => {
      result.current.signIn({ id: "u3", name: "Sign", email: "sign@test.com", role: "user" });
    });

    expect(result.current.user?.email).toBe("sign@test.com");
    expect(mockNavigate).toHaveBeenCalledWith("/dashboard", { replace: true });
  });

  it("signOut calls /auth/logout and clears user", async () => {
    const { AuthProvider, useAuth } = await importContext();

    mockApi.get.mockResolvedValueOnce({
      data: { user: { id: "u4", name: "Out", email: "out@test.com" } },
    });
    mockApi.post.mockResolvedValueOnce({});

    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => (
        <MemoryRouter>
          <AuthProvider>{children}</AuthProvider>
        </MemoryRouter>
      ),
    });

    await waitFor(() => expect(result.current.user?.email).toBe("out@test.com"));

    await act(async () => {
      await result.current.signOut();
    });

    expect(mockApi.post).toHaveBeenCalledWith("/auth/logout");
    expect(result.current.user).toBeNull();
    expect(mockNavigate).toHaveBeenCalledWith("/", { replace: true });
  });
});
