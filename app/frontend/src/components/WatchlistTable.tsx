import { useMemo, useState } from "react";

import type { PriceAlert } from "@shared/types/alerts";

import { AlertModal } from "./AlertModal";
import type { WatchlistItem } from "../types/market";

interface Props {
  items: WatchlistItem[];
  selectedSymbol: string;
  onSelect: (symbol: string) => void;
  isLoading: boolean;
  alerts: PriceAlert[];
  onCreateAlert: (payload: {
    symbol: string;
    direction: "above" | "below";
    target_price: number;
  }) => Promise<void>;
  isCreatingAlert: boolean;
  createAlertError: Error | null;
}

export function WatchlistTable({
  items,
  selectedSymbol,
  onSelect,
  isLoading,
  alerts,
  onCreateAlert,
  isCreatingAlert,
  createAlertError,
}: Props) {
  const [modalSymbol, setModalSymbol] = useState<string | null>(null);

  const triggeredSymbols = useMemo(() => {
    const set = new Set<string>();
    for (const alert of alerts) {
      if (alert.triggered_at !== null) {
        set.add(alert.symbol);
      }
    }
    return set;
  }, [alerts]);

  const modalItem = items.find((item) => item.symbol === modalSymbol);

  if (isLoading) {
    return <div className="h-64 animate-pulse rounded-xl bg-surface-card" />;
  }

  return (
    <>
      <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
        <h2 className="mb-3 text-lg font-semibold text-white">Watchlist</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="pb-2 pr-4">Symbol</th>
                <th className="pb-2 pr-4">Name</th>
                <th className="pb-2 pr-4">Price</th>
                <th className="pb-2 pr-4">Change</th>
                <th className="pb-2">Alert</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => {
                const active = item.symbol === selectedSymbol;
                const positive = item.change_percent >= 0;
                const hasTriggered = triggeredSymbols.has(item.symbol);
                return (
                  <tr
                    key={item.symbol}
                    className={`border-t border-slate-700/40 ${active ? "bg-slate-800/60" : "hover:bg-slate-800/30"}`}
                  >
                    <td
                      className="cursor-pointer py-2 pr-4 font-medium text-white"
                      onClick={() => onSelect(item.symbol)}
                    >
                      <span className="inline-flex items-center gap-2">
                        {item.symbol}
                        {hasTriggered && (
                          <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-xs font-medium text-amber-400">
                            Alert triggered
                          </span>
                        )}
                      </span>
                    </td>
                    <td
                      className="cursor-pointer py-2 pr-4 text-slate-300"
                      onClick={() => onSelect(item.symbol)}
                    >
                      {item.name}
                    </td>
                    <td
                      className="cursor-pointer py-2 pr-4 text-slate-200"
                      onClick={() => onSelect(item.symbol)}
                    >
                      ${item.price.toLocaleString()}
                    </td>
                    <td
                      className={`cursor-pointer py-2 pr-4 ${positive ? "text-emerald-400" : "text-rose-400"}`}
                      onClick={() => onSelect(item.symbol)}
                    >
                      {positive ? "+" : ""}
                      {item.change_percent.toFixed(2)}%
                    </td>
                    <td className="py-2">
                      <button
                        type="button"
                        onClick={() => setModalSymbol(item.symbol)}
                        className="rounded-lg border border-slate-600 px-3 py-1 text-xs text-slate-300 hover:border-emerald-500/50 hover:text-emerald-400"
                      >
                        Set alert
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {modalItem && (
        <AlertModal
          symbol={modalItem.symbol}
          currentPrice={modalItem.price}
          isOpen={modalSymbol !== null}
          onClose={() => setModalSymbol(null)}
          onSubmit={async (payload) => {
            await onCreateAlert({ symbol: modalItem.symbol, ...payload });
          }}
          isSubmitting={isCreatingAlert}
          error={createAlertError}
        />
      )}
    </>
  );
}
