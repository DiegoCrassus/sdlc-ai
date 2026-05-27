import { FormEvent, useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiClientError, encodeAssetId } from "../api/client";
import type {
  Holding,
  Portfolio,
  Transaction,
  TransactionType,
} from "../api/types";
import { AsyncState } from "../components/AsyncState";
import { SourceBadge } from "../components/SourceBadge";
import {
  changeClass,
  formatDate,
  formatMoney,
  formatNumber,
} from "../utils/format";
import styles from "./pages.module.css";

export function PortfolioPage() {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [txType, setTxType] = useState<TransactionType>("buy");
  const [txAssetId, setTxAssetId] = useState("stock:AAPL");
  const [txQty, setTxQty] = useState("1");
  const [txNote, setTxNote] = useState("");
  const [txSubmitting, setTxSubmitting] = useState(false);
  const [txFeedback, setTxFeedback] = useState<{
    kind: "success" | "error";
    text: string;
  } | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [port, holds, txs] = await Promise.all([
        api.getPortfolio(),
        api.getHoldings(),
        api.getTransactions(50),
      ]);
      setPortfolio(port);
      setHoldings(holds.items);
      setTransactions(txs.items);
    } catch (err) {
      setError(
        err instanceof ApiClientError
          ? err.message
          : "Failed to load portfolio",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleTrade(e: FormEvent) {
    e.preventDefault();
    const quantity = parseFloat(txQty);
    if (!Number.isFinite(quantity) || quantity <= 0) {
      setTxFeedback({ kind: "error", text: "Quantity must be greater than 0" });
      return;
    }

    setTxSubmitting(true);
    setTxFeedback(null);
    try {
      const result = await api.createTransaction({
        type: txType,
        asset_id: txAssetId.trim(),
        quantity,
        note: txNote.trim() || undefined,
      });
      setPortfolio(result.portfolio);
      setTxFeedback({
        kind: "success",
        text: `${txType === "buy" ? "Bought" : "Sold"} ${quantity} @ ${formatMoney(result.transaction.price)} (${result.transaction.source})`,
      });
      const [holds, txs] = await Promise.all([
        api.getHoldings(),
        api.getTransactions(50),
      ]);
      setHoldings(holds.items);
      setTransactions(txs.items);
    } catch (err) {
      setTxFeedback({
        kind: "error",
        text:
          err instanceof ApiClientError
            ? err.message
            : "Transaction failed",
      });
    } finally {
      setTxSubmitting(false);
    }
  }

  function pickHoldingAsset(h: Holding) {
    return h.asset?.symbol ?? h.asset_id.split(":")[1] ?? h.asset_id;
  }

  return (
    <div>
      <h2 className={styles.pageTitle}>Portfolio</h2>
      <p className={styles.pageLead}>
        Simulated cash and holdings — trades execute at the current quote price.
      </p>

      <AsyncState loading={loading} error={error}>
        {portfolio && (
          <>
            <div className={styles.grid2}>
              <div className={styles.statCard}>
                <p className={styles.statLabel}>Cash balance</p>
                <p className={styles.statValue}>
                  {formatMoney(
                    portfolio.cash_balance,
                    portfolio.base_currency,
                  )}
                </p>
              </div>
              <div className={styles.statCard}>
                <p className={styles.statLabel}>Total value</p>
                <p className={styles.statValue}>
                  {formatMoney(
                    portfolio.total_value,
                    portfolio.base_currency,
                  )}
                </p>
              </div>
              <div className={styles.statCard}>
                <p className={styles.statLabel}>Unrealized P&amp;L</p>
                <p
                  className={`${styles.statValue} ${changeClass(portfolio.unrealized_pnl)}`}
                >
                  {formatMoney(
                    portfolio.unrealized_pnl,
                    portfolio.base_currency,
                  )}
                </p>
              </div>
            </div>

            <div
              style={{
                display: "grid",
                gap: "1.25rem",
                gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
                marginBottom: "1.5rem",
              }}
            >
              <div className={styles.card}>
                <div className={styles.cardHeader}>Buy / Sell</div>
                {txFeedback && (
                  <div
                    style={{ padding: "0 1.25rem", paddingTop: "1rem" }}
                    className={
                      txFeedback.kind === "success"
                        ? styles.feedbackSuccess
                        : styles.feedbackError
                    }
                  >
                    {txFeedback.text}
                  </div>
                )}
                <form className={styles.form} onSubmit={(e) => void handleTrade(e)}>
                  <div className={styles.formRow}>
                    <label htmlFor="tx-type">Type</label>
                    <select
                      id="tx-type"
                      value={txType}
                      onChange={(e) =>
                        setTxType(e.target.value as TransactionType)
                      }
                    >
                      <option value="buy">Buy</option>
                      <option value="sell">Sell</option>
                    </select>
                  </div>
                  <div className={styles.formRow}>
                    <label htmlFor="tx-asset">Asset ID</label>
                    <input
                      id="tx-asset"
                      value={txAssetId}
                      onChange={(e) => setTxAssetId(e.target.value)}
                      placeholder="stock:AAPL"
                      list="holding-ids"
                      required
                    />
                    <datalist id="holding-ids">
                      {holdings.map((h) => (
                        <option key={h.asset_id} value={h.asset_id} />
                      ))}
                      <option value="stock:AAPL" />
                      <option value="crypto:BTC" />
                      <option value="crypto:ETH" />
                    </datalist>
                  </div>
                  <div className={styles.formRow}>
                    <label htmlFor="tx-qty">Quantity</label>
                    <input
                      id="tx-qty"
                      type="number"
                      min="0.0001"
                      step="any"
                      value={txQty}
                      onChange={(e) => setTxQty(e.target.value)}
                      required
                    />
                  </div>
                  <div className={styles.formRow}>
                    <label htmlFor="tx-note">Note (optional)</label>
                    <input
                      id="tx-note"
                      value={txNote}
                      onChange={(e) => setTxNote(e.target.value)}
                    />
                  </div>
                  <div className={styles.formActions}>
                    <button
                      type="submit"
                      className={styles.btnPrimary}
                      disabled={txSubmitting}
                    >
                      {txSubmitting ? "Submitting…" : "Submit trade"}
                    </button>
                  </div>
                </form>
              </div>

              <div className={styles.card}>
                <div className={styles.cardHeader}>Holdings</div>
                {holdings.length === 0 ? (
                  <p
                    style={{
                      padding: "1.25rem",
                      color: "var(--text-muted)",
                      margin: 0,
                    }}
                  >
                    No positions yet. Submit a buy order to get started.
                  </p>
                ) : (
                  <table className={styles.table}>
                    <thead>
                      <tr>
                        <th>Asset</th>
                        <th>Qty</th>
                        <th>Value</th>
                        <th>Source</th>
                      </tr>
                    </thead>
                    <tbody>
                      {holdings.map((h) => (
                        <tr key={h.asset_id}>
                          <td>
                            <Link
                              className={styles.assetLink}
                              to={`/assets/${encodeAssetId(h.asset_id)}`}
                            >
                              {pickHoldingAsset(h)}
                            </Link>
                          </td>
                          <td className="mono">{formatNumber(h.quantity, 4)}</td>
                          <td className="mono">
                            {formatMoney(h.market_value)}
                          </td>
                          <td>
                            <SourceBadge source={h.source} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>

            <div className={styles.card}>
              <div className={styles.cardHeader}>Recent transactions</div>
              {transactions.length === 0 ? (
                <p
                  style={{
                    padding: "1.25rem",
                    color: "var(--text-muted)",
                    margin: 0,
                  }}
                >
                  No transactions recorded.
                </p>
              ) : (
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>When</th>
                      <th>Type</th>
                      <th>Asset</th>
                      <th>Qty</th>
                      <th>Total</th>
                      <th>Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((tx) => (
                      <tr key={tx.id}>
                        <td className="mono" style={{ fontSize: "0.8rem" }}>
                          {formatDate(tx.executed_at)}
                        </td>
                        <td>
                          <span
                            className={
                              tx.type === "buy" ? "positive" : "negative"
                            }
                            style={{ textTransform: "uppercase", fontWeight: 600 }}
                          >
                            {tx.type}
                          </span>
                        </td>
                        <td>
                          <Link
                            to={`/assets/${encodeAssetId(tx.asset_id)}`}
                            className={styles.symbol}
                          >
                            {tx.asset_id}
                          </Link>
                        </td>
                        <td className="mono">{formatNumber(tx.quantity, 4)}</td>
                        <td className="mono">{formatMoney(tx.total)}</td>
                        <td>
                          <SourceBadge source={tx.source} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}
      </AsyncState>
    </div>
  );
}
