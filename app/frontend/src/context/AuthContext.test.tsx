import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AppLayout } from "../components/layout/AppLayout";

import { AuthProvider } from "./AuthContext";

const identifyMock = vi.fn();
const logoutMock = vi.fn();
const meMock = vi.fn();
const invalidateQueriesMock = vi.fn();

vi.mock("../api/client", () => ({
  api: {
    auth: {
      me: () => meMock(),
      identify: (email: string) => identifyMock(email),
      logout: () => logoutMock(),
    },
  },
}));

vi.mock("@tanstack/react-query", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@tanstack/react-query")>();
  return {
    ...actual,
    useQueryClient: () => ({
      invalidateQueries: invalidateQueriesMock,
    }),
  };
});

function renderAuthHeader() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <MemoryRouter initialEntries={["/"]}>
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/" element={<div>Dashboard content</div>} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    </QueryClientProvider>,
  );
}

describe("AuthContext identify flow", () => {
  beforeEach(() => {
    identifyMock.mockReset();
    logoutMock.mockReset();
    meMock.mockReset();
    invalidateQueriesMock.mockReset();
    meMock.mockResolvedValue(null);
    identifyMock.mockResolvedValue({
      user: { id: "user-1", email: "alice@example.com" },
    });
    logoutMock.mockResolvedValue(undefined);
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("shows Sign in when anonymous and email in header after identify", async () => {
    renderAuthHeader();

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Sign in" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    const emailInput = screen.getByLabelText("Email");
    fireEvent.change(emailInput, { target: { value: "alice@example.com" } });
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));

    await waitFor(() => {
      expect(identifyMock).toHaveBeenCalledWith("alice@example.com");
    });

    await waitFor(() => {
      expect(screen.getByTestId("header-user-email").textContent).toBe("alice@example.com");
    });

    expect(invalidateQueriesMock).toHaveBeenCalledWith({ queryKey: ["watchlist"] });
    expect(invalidateQueriesMock).toHaveBeenCalledWith({ queryKey: ["alerts"] });
    expect(screen.queryByRole("button", { name: "Sign in" })).toBeNull();
  });

  it("clears header session after logout", async () => {
    meMock.mockResolvedValue({ id: "user-1", email: "bob@example.com" });

    renderAuthHeader();

    await waitFor(() => {
      expect(screen.getByTestId("header-user-email").textContent).toBe("bob@example.com");
    });

    fireEvent.click(screen.getByRole("button", { name: "Log out" }));

    await waitFor(() => {
      expect(logoutMock).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Sign in" })).toBeTruthy();
    });

    expect(screen.queryByTestId("header-user-email")).toBeNull();
  });
});
