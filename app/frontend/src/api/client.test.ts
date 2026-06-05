import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "./client";

describe("api client", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  function mockJsonResponse(body: unknown, status = 200) {
    return {
      ok: status >= 200 && status < 300,
      status,
      statusText: status === 200 ? "OK" : "Error",
      json: vi.fn().mockResolvedValue(body),
    };
  }

  it("sends credentials include on watchlist requests", async () => {
    fetchMock.mockResolvedValue(
      mockJsonResponse({
        items: [],
        total_invested: 0,
      }),
    );

    await api.watchlist();

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/watchlist",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("sends credentials include on alerts list requests", async () => {
    fetchMock.mockResolvedValue(mockJsonResponse({ items: [] }));

    await api.alerts.list();

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/alerts",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("sends credentials include on auth identify", async () => {
    fetchMock.mockResolvedValue(
      mockJsonResponse({
        user: { id: "u1", email: "user@example.com" },
      }),
    );

    await api.auth.identify("user@example.com");

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/identify",
      expect.objectContaining({
        credentials: "include",
        method: "POST",
        body: JSON.stringify({ email: "user@example.com" }),
      }),
    );
  });

  it("returns null from auth.me on 401", async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 401,
      statusText: "Unauthorized",
      json: vi.fn(),
    });

    await expect(api.auth.me()).resolves.toBeNull();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/me",
      expect.objectContaining({ credentials: "include" }),
    );
  });
});
