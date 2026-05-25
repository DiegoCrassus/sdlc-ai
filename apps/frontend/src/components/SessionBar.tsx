import { useEffect, useState } from "react";
import { getSession, PLAYER_PRESETS, setSession, type DevSession } from "../session";

export function SessionBar() {
  const [session, setLocal] = useState<DevSession>(getSession);

  useEffect(() => {
    setSession(session);
    window.dispatchEvent(new Event("rpg-op-session"));
  }, [session]);

  return (
    <div className="session-bar">
      <span className="session-label">Sessão dev:</span>
      <select
        value={`${session.role}:${session.email}`}
        onChange={(e) => {
          const preset = PLAYER_PRESETS.find((p) => `${p.role}:${p.email}` === e.target.value);
          if (preset) setLocal(preset);
        }}
      >
        {PLAYER_PRESETS.map((p) => (
          <option key={`${p.role}:${p.email}`} value={`${p.role}:${p.email}`}>
            {p.role === "gm" ? "Mestre" : "Jogador"} — {p.email}
          </option>
        ))}
      </select>
    </div>
  );
}
