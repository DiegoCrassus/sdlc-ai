/**
 * Auth identity types — canonical contract for email-only sessions (ADR-010).
 *
 * Endpoints (prefix `/api/v1`):
 * - POST `/auth/identify` — body IdentifyRequest → IdentifyResponse + Set-Cookie
 * - GET `/auth/me` — AuthMeResponse or 401 SessionError
 * - POST `/auth/logout` — 204 No Content (clears cookie)
 *
 * Session transport: HttpOnly cookie only — never send Authorization from the SPA.
 */

/** Default cookie name; override via backend `SESSION_COOKIE_NAME`. */
export const SESSION_COOKIE_NAME = "mp_session";

/** Fixed session TTL (seconds); rotation on each successful identify (ADR-010). */
export const SESSION_TTL_SECONDS = 604800;

/**
 * How the browser carries the session (documented for SHARED consumers).
 * - Use `fetch(url, { credentials: "include" })` so the cookie is sent.
 * - Cookie flags (backend): HttpOnly, SameSite=Lax, Path=/, Secure per environment.
 * - Not readable from JavaScript (HttpOnly).
 */
export const SESSION_TRANSPORT = "cookie" as const;

export type SessionTransport = typeof SESSION_TRANSPORT;

export interface User {
  id: string;
  email: string;
}

export interface IdentifyRequest {
  email: string;
}

/** POST /api/v1/auth/identify — 200 response body (cookie set out-of-band). */
export interface IdentifyResponse {
  user: User;
}

/** GET /api/v1/auth/me — 200 response body. */
export interface AuthMeResponse {
  user: User;
}

/** ADR-010 alias for GET /auth/me success body. */
export type MeResponse = AuthMeResponse;

export type AuthErrorCode = "UNAUTHORIZED" | "VALIDATION_ERROR";

export interface ApiErrorBody {
  code: AuthErrorCode;
  message: string;
  details?: Record<string, unknown>;
}

/** 401 / 422 auth error envelope (`{ error: { code, message, details? } }`). */
export interface SessionError {
  error: ApiErrorBody;
}

export const AUTH_API_PATHS = {
  identify: "/api/v1/auth/identify",
  me: "/api/v1/auth/me",
  logout: "/api/v1/auth/logout",
} as const;
