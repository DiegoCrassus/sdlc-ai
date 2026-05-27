import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiClientError, encodeAssetId } from "../api/client";
import type { WatchlistItem } from "../api/types";
import { AsyncState } from "../components/AsyncState";
import { SourceBadge } from "../components/SourceBadge";
import {
  changeClass,
  formatMoney,
  formatPercent,
} from "../utils/format";
import styles from "./pages.module.css";

export function WatchlistPage() {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [removingId, setRemovingId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.getWatchlist();
      setItems(result.items);
    } catch (err) {
      setError(
        err instanceof ApiClientError
          ? err.message
          : "Failed to load watchlist",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleRemove(assetId: string) {
    setRemovingId(assetId);
    try {
      await api.removeWatchlistItem(assetId);
      setItems((prev) => prev.filter((i) => i.asset_id !== assetId));
    } catch (err) {
      setError(
        err instanceof ApiClientError
          ? err.message
          : "Failed to remove item",
      );
    } finally {
      setRemovingId(null);
    }
  }

  return (
    <div>
      <h2 className={styles.pageTitle}>Watchlist</h2>
      <p className={styles.pageLead}>
        Tracked assets with latest quotes. Fallback badge means catalog pricing.
      </p>

      <AsyncState
        loading={loading}
        error={error}
        empty={!loading && !error && items.length === 0}
        emptyMessage="Your watchlist is empty. Discover assets on the home page."
      >
        <div className={styles.card}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Asset</th>
                <th>Price</th>
                <th>Change</th>
                <th>Source</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => {
                const asset = item.asset;
                const quote = item.quote;
                const symbol = asset?.symbol ?? item.asset_id.split(":")[1];
                return (
                  <tr key={item.asset_id}>
                    <td>
                      <Link
                        className={styles.assetLink}
                        to={`/assets/${encodeAssetId(item.asset_id)}`}
                      >
                        <span className={styles.symbol}>{symbol}</span>
                      </Link>
                      {asset && (
                        <div
                          style={{
                            color: "var(--text-muted)",
                            fontSize: "0.85rem",
                          }}
                        >
                          {asset.name}
                        </div>
                      )}
                    </td>
                    <td className="mono">
                      {quote
                        ? formatMoney(quote.price, quote.currency)
                        : "—"}
                    </td>
                    <td
                      className={`mono ${changeClass(quote?.change_percent)}`}
                    >
                      {quote ? formatPercent(quote.change_percent) : "—"}
                    </td>
                    <td>
                      <SourceBadge source={quote?.source} />
                    </td>
                    <td>
                      <button
                        type="button"
                        className={styles.btnDanger}
                        disabled={removingId === item.asset_id}
                        onClick={() => void handleRemove(item.asset_id)}
                      >
                        {removingId === item.asset_id ? "…" : "Remove"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </AsyncState>
    </div>
  );
}
