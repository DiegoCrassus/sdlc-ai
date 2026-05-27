import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiClientError } from "../api/client";
import type { Asset, HistoryResponse, Quote } from "../api/types";
import { AsyncState } from "../components/AsyncState";
import { SourceBadge } from "../components/SourceBadge";
import {
  changeClass,
  formatDate,
  formatMoney,
  formatPercent,
} from "../utils/format";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import styles from "./pages.module.css";

export function AssetDetail() {
  const { assetId: rawId } = useParams<{ assetId: string }>();
  const assetId = rawId ? decodeURIComponent(rawId) : "";

  const [asset, setAsset] = useState<Asset | null>(null);
  const [quote, setQuote] = useState<Quote | null>(null);
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [watchLoading, setWatchLoading] = useState(false);
  const [watchMsg, setWatchMsg] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!assetId) return;
    setLoading(true);
    setError(null);
    try {
      const [assetRes, quoteRes, historyRes] = await Promise.all([
        api.getAsset(assetId),
        api.getQuote(assetId),
        api.getHistory(assetId),
      ]);
      setAsset(assetRes);
      setQuote(quoteRes);
      setHistory(historyRes);
    } catch (err) {
      setAsset(null);
      setQuote(null);
      setHistory(null);
      setError(
        err instanceof ApiClientError
          ? err.message
          : "Failed to load asset",
      );
    } finally {
      setLoading(false);
    }
  }, [assetId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleAddWatchlist() {
    setWatchLoading(true);
    setWatchMsg(null);
    try {
      await api.addWatchlistItem({ asset_id: assetId });
      setWatchMsg("Added to watchlist");
    } catch (err) {
      setWatchMsg(
        err instanceof ApiClientError
          ? err.message
          : "Could not add to watchlist",
      );
    } finally {
      setWatchLoading(false);
    }
  }

  const chartData =
    history?.points.map((p) => ({
      date: new Date(p.timestamp).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      }),
      close: p.close,
    })) ?? [];

  return (
    <div>
      <p style={{ marginBottom: "1rem" }}>
        <Link to="/" style={{ color: "var(--text-muted)" }}>
          ← Back to Discover
        </Link>
      </p>

      <AsyncState loading={loading} error={error}>
        {asset && quote && (
          <>
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                alignItems: "flex-start",
                justifyContent: "space-between",
                gap: "1rem",
                marginBottom: "1.5rem",
              }}
            >
              <div>
                <h2 className={styles.pageTitle}>
                  <span className={styles.symbol}>{asset.symbol}</span>
                  <span className={styles.classTag}>{asset.class}</span>
                </h2>
                <p className={styles.pageLead} style={{ marginBottom: 0 }}>
                  {asset.name}
                  {asset.exchange ? ` · ${asset.exchange}` : ""}
                </p>
              </div>
              <div className={styles.rowActions}>
                <SourceBadge source={quote.source} />
                <button
                  type="button"
                  className={styles.btnPrimary}
                  disabled={watchLoading}
                  onClick={() => void handleAddWatchlist()}
                >
                  {watchLoading ? "Adding…" : "Add to watchlist"}
                </button>
              </div>
            </div>

            {watchMsg && (
              <div
                className={
                  watchMsg.includes("Added")
                    ? styles.feedbackSuccess
                    : styles.feedbackError
                }
              >
                {watchMsg}
              </div>
            )}

            <div className={styles.grid2}>
              <div className={styles.statCard}>
                <p className={styles.statLabel}>Last price</p>
                <p className={styles.statValue}>
                  {formatMoney(quote.price, quote.currency)}
                </p>
              </div>
              <div className={styles.statCard}>
                <p className={styles.statLabel}>Change</p>
                <p
                  className={`${styles.statValue} ${changeClass(quote.change_percent)}`}
                >
                  {formatPercent(quote.change_percent)}
                </p>
              </div>
              <div className={styles.statCard}>
                <p className={styles.statLabel}>Updated</p>
                <p className={styles.statValue} style={{ fontSize: "1rem" }}>
                  {formatDate(quote.timestamp)}
                </p>
              </div>
            </div>

            <div className={styles.card}>
              <div
                className={styles.cardHeader}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span>Price history (close)</span>
                <SourceBadge source={history?.source} />
              </div>
              <div className={styles.chartWrap}>
                {chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={chartData}>
                      <CartesianGrid stroke="#2a3544" strokeDasharray="3 3" />
                      <XAxis
                        dataKey="date"
                        tick={{ fill: "#8b9bb0", fontSize: 11 }}
                        interval="preserveStartEnd"
                      />
                      <YAxis
                        tick={{ fill: "#8b9bb0", fontSize: 11 }}
                        domain={["auto", "auto"]}
                        tickFormatter={(v: number) =>
                          v >= 1000 ? `${(v / 1000).toFixed(1)}k` : String(v)
                        }
                      />
                      <Tooltip
                        contentStyle={{
                          background: "#1a2332",
                          border: "1px solid #2a3544",
                          borderRadius: 8,
                        }}
                        labelStyle={{ color: "#8b9bb0" }}
                      />
                      <Line
                        type="monotone"
                        dataKey="close"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <p style={{ color: "var(--text-muted)" }}>
                    No history points available.
                  </p>
                )}
              </div>
            </div>

            {history && history.points.length > 0 && (
              <div className={styles.card} style={{ marginTop: "1.25rem" }}>
                <div className={styles.cardHeader}>OHLCV table</div>
                <div style={{ maxHeight: 320, overflow: "auto" }}>
                  <table className={styles.table}>
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Open</th>
                        <th>High</th>
                        <th>Low</th>
                        <th>Close</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[...history.points].reverse().slice(0, 14).map((p) => (
                        <tr key={p.timestamp}>
                          <td className="mono">
                            {formatDate(p.timestamp)}
                          </td>
                          <td className="mono">{p.open.toFixed(2)}</td>
                          <td className="mono">{p.high.toFixed(2)}</td>
                          <td className="mono">{p.low.toFixed(2)}</td>
                          <td className="mono">{p.close.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </AsyncState>
    </div>
  );
}
