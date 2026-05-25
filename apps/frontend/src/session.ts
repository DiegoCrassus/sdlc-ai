const SESSION_KEY = "rpg-op-session";

export interface DevSession {
  email: string;
  role: "player" | "gm";
}

const DEFAULT_SESSION: DevSession = {
  email: "mestre@local.dev",
  role: "gm",
};

export function getSession(): DevSession {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    if (!raw) return DEFAULT_SESSION;
    const parsed = JSON.parse(raw) as DevSession;
    if (parsed.role !== "player" && parsed.role !== "gm") return DEFAULT_SESSION;
    if (!parsed.email) return DEFAULT_SESSION;
    return parsed;
  } catch {
    return DEFAULT_SESSION;
  }
}

export function setSession(session: DevSession): void {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function sessionHeaders(): HeadersInit {
  const s = getSession();
  return {
    "X-Session-Role": s.role,
    "X-Session-Email": s.email,
  };
}

export const PLAYER_PRESETS: DevSession[] = [
  { email: "mestre@local.dev", role: "gm" },
  { email: "lyra@jogador.dev", role: "player" },
  { email: "thorin@jogador.dev", role: "player" },
];
