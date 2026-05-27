import type { DataSource } from "../api/types";
import styles from "./SourceBadge.module.css";

interface SourceBadgeProps {
  source: DataSource | null | undefined;
}

export function SourceBadge({ source }: SourceBadgeProps) {
  if (!source) return null;

  const isFallback = source === "fallback";

  return (
    <span
      className={`${styles.badge} ${isFallback ? styles.fallback : styles.live}`}
      title={
        isFallback
          ? "Price from bundled catalog (live providers unavailable)"
          : "Live market data"
      }
    >
      {source}
    </span>
  );
}
