import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiClientError, encodeAssetId } from "../api/client";
import type { Asset } from "../api/types";
import { AsyncState } from "../components/AsyncState";
import { SourceBadge } from "../components/SourceBadge";
import styles from "./pages.module.css";

export function Discover() {
  const [query, setQuery] = useState("");
  const [assetClass, setAssetClass] = useState("");
  const [items, setItems] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionId, setActionId] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const runSearch = useCallback(async (q: string, cls: string) => {
    const trimmed = q.trim();
    if (trimmed.length < 1) {
      setItems([]);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await api.searchAssets(
        trimmed,
        cls || undefined,
        30,
      );
      setItems(result.items);
    } catch (err) {
      setItems([]);
      setError(
        err instanceof ApiClientError
          ? err.message
          : "Search failed. Is the backend running?",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void runSearch(query, assetClass);
    }, 350);
    return () => window.clearTimeout(timer);
  }, [query, assetClass, runSearch]);

  async function handleAdd(asset: Asset) {
    setActionId(asset.id);
    setToast(null);
    try {
      await api.addWatchlistItem({ asset_id: asset.id });
      setToast(`${asset.symbol} added to watchlist`);
    } catch (err) {
      setToast(
        err instanceof ApiClientError
          ? err.message
          : "Could not add to watchlist",
      );
    } finally {
      setActionId(null);
    }
  }

  return (
    <div>
      <h2 className={styles.pageTitle}>Discover</h2>
      <p className={styles.pageLead}>
        Search stocks and crypto, then add assets to your watchlist.
      </p>

      {toast && (
        <div
          className={
            toast.includes("added")
              ? styles.feedbackSuccess
              : styles.feedbackError
          }
        >
          {toast}
        </div>
      )}

      <div className={styles.searchRow}>
        <input
          className={styles.searchInput}
          type="search"
          placeholder="Search by symbol or name (e.g. apple, BTC)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label="Search assets"
        />
        <select
          className={styles.select}
          value={assetClass}
          onChange={(e) => setAssetClass(e.target.value)}
          aria-label="Asset class filter"
        >
          <option value="">All classes</option>
          <option value="stock">Stocks</option>
          <option value="crypto">Crypto</option>
        </select>
      </div>

      <AsyncState
        loading={loading}
        error={error}
        empty={!loading && !error && query.trim().length >= 1 && items.length === 0}
        emptyMessage="No assets matched your search."
      >
        {items.length > 0 && (
          <div className={styles.card}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Asset</th>
                  <th>Class</th>
                  <th>Source</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((asset) => (
                  <tr key={asset.id}>
                    <td>
                      <Link
                        className={styles.assetLink}
                        to={`/assets/${encodeAssetId(asset.id)}`}
                      >
                        <span className={styles.symbol}>{asset.symbol}</span>
                      </Link>
                      <div style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
                        {asset.name}
                      </div>
                    </td>
                    <td>
                      <span className={styles.classTag}>{asset.class}</span>
                    </td>
                    <td>
                      <SourceBadge source={asset.source ?? undefined} />
                    </td>
                    <td>
                      <div className={styles.rowActions}>
                        <button
                          type="button"
                          className={styles.btnPrimary}
                          disabled={actionId === asset.id}
                          onClick={() => void handleAdd(asset)}
                        >
                          {actionId === asset.id ? "Adding…" : "Watchlist"}
                        </button>
                        <Link
                          className={styles.btn}
                          to={`/assets/${encodeAssetId(asset.id)}`}
                        >
                          Details
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </AsyncState>

      {query.trim().length < 1 && !loading && (
        <p style={{ color: "var(--text-muted)" }}>
          Type at least one character to search the market catalog.
        </p>
      )}
    </div>
  );
}
