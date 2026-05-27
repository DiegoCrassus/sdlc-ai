/**
 * Subtle data provenance badge for asset detail pages.
 *
 * Examples:
 *   "Data from CoinGecko · Updated 2 minutes ago"
 *   "Data from scraped public page · May be delayed"
 */

export type SourceType = "api" | "csv" | "scraping" | "mock" | "cache";
export type ConfidenceLevel = "high" | "medium" | "low";

export interface DataProvenance {
  providerName: string;
  sourceType: SourceType;
  sourceUrl?: string;
  fetchedAt: string;
  cachedAt?: string;
  isRealtime: boolean;
  isDelayed: boolean;
  confidenceLevel: ConfidenceLevel;
  warning?: string;
}

function formatRelativeTime(isoDate: string): string {
  const then = new Date(isoDate).getTime();
  const now = Date.now();
  const diffSec = Math.max(0, Math.floor((now - then) / 1000));
  if (diffSec < 60) return `${diffSec} seconds ago`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin} minute${diffMin === 1 ? "" : "s"} ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr} hour${diffHr === 1 ? "" : "s"} ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay} day${diffDay === 1 ? "" : "s"} ago`;
}

function providerDisplayName(provenance: DataProvenance): string {
  if (provenance.sourceType === "scraping") {
    return "scraped public page";
  }
  if (provenance.sourceType === "mock") {
    return "simulated data";
  }
  if (provenance.sourceType === "cache") {
    return provenance.providerName;
  }
  const names: Record<string, string> = {
    coingecko: "CoinGecko",
    finnhub: "Finnhub",
    brapi: "brapi.dev",
    twelve_data: "Twelve Data",
    bcb_ptax: "Banco Central (PTAX)",
    csv_stooq: "Stooq CSV",
    mock: "Mock",
  };
  return names[provenance.providerName] ?? provenance.providerName;
}

export function formatDataProvenance(provenance: DataProvenance): string {
  const updatedAt = provenance.cachedAt ?? provenance.fetchedAt;
  const base = `Data from ${providerDisplayName(provenance)} · Updated ${formatRelativeTime(updatedAt)}`;
  if (provenance.warning) {
    return `${base} · ${provenance.warning}`;
  }
  if (provenance.isDelayed && provenance.confidenceLevel !== "high") {
    return `${base} · May be delayed`;
  }
  return base;
}

export interface DataProvenanceBadgeProps {
  provenance: DataProvenance;
  className?: string;
}

/**
 * React component — subtle footer line on asset detail pages.
 */
export function DataProvenanceBadge({ provenance, className = "" }: DataProvenanceBadgeProps) {
  const text = formatDataProvenance(provenance);
  const tone =
    provenance.confidenceLevel === "high"
      ? "text-muted-foreground"
      : provenance.confidenceLevel === "medium"
        ? "text-amber-600"
        : "text-orange-600";

  return (
    <p
      className={`text-xs ${tone} ${className}`}
      title={provenance.sourceUrl ?? undefined}
      data-testid="data-provenance-badge"
      data-confidence={provenance.confidenceLevel}
      data-source-type={provenance.sourceType}
    >
      {text}
    </p>
  );
}
