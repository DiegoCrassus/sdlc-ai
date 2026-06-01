import { useState, type FormEvent } from "react";

import type { AlertDirection } from "@shared/types/alerts";

interface Props {
  symbol: string;
  currentPrice: number;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: { direction: AlertDirection; target_price: number }) => Promise<void>;
  isSubmitting: boolean;
  error: Error | null;
}

export function AlertModal({
  symbol,
  currentPrice,
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
  error,
}: Props) {
  const [direction, setDirection] = useState<AlertDirection>("above");
  const [targetPrice, setTargetPrice] = useState("");

  if (!isOpen) {
    return null;
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const parsed = Number.parseFloat(targetPrice);
    if (Number.isNaN(parsed) || parsed <= 0) {
      return;
    }
    await onSubmit({ direction, target_price: parsed });
    setTargetPrice("");
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      role="presentation"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-xl border border-slate-700/60 bg-surface-card p-6 shadow-xl"
        role="dialog"
        aria-modal="true"
        aria-labelledby="alert-modal-title"
        onClick={(event) => event.stopPropagation()}
      >
        <h2 id="alert-modal-title" className="mb-1 text-lg font-semibold text-white">
          Set price alert
        </h2>
        <p className="mb-4 text-sm text-slate-400">
          {symbol} — current price ${currentPrice.toLocaleString()}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <fieldset>
            <legend className="mb-2 block text-sm text-slate-400">Notify when price goes</legend>
            <div className="flex gap-3">
              <label className="flex flex-1 cursor-pointer items-center justify-center rounded-lg border border-slate-600 px-3 py-2 text-sm has-[:checked]:border-emerald-500 has-[:checked]:bg-emerald-500/10">
                <input
                  type="radio"
                  name="direction"
                  value="above"
                  checked={direction === "above"}
                  onChange={() => setDirection("above")}
                  className="sr-only"
                />
                <span className="text-white">Above</span>
              </label>
              <label className="flex flex-1 cursor-pointer items-center justify-center rounded-lg border border-slate-600 px-3 py-2 text-sm has-[:checked]:border-emerald-500 has-[:checked]:bg-emerald-500/10">
                <input
                  type="radio"
                  name="direction"
                  value="below"
                  checked={direction === "below"}
                  onChange={() => setDirection("below")}
                  className="sr-only"
                />
                <span className="text-white">Below</span>
              </label>
            </div>
          </fieldset>

          <div>
            <label className="mb-2 block text-sm text-slate-400" htmlFor="target-price">
              Target price
            </label>
            <input
              id="target-price"
              type="number"
              step="any"
              min="0"
              required
              value={targetPrice}
              onChange={(event) => setTargetPrice(event.target.value)}
              placeholder={currentPrice.toLocaleString()}
              className="w-full rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-sm text-white outline-none ring-emerald-500 focus:ring-2"
            />
          </div>

          {error && (
            <p className="text-sm text-rose-400" role="alert">
              {error.message}
            </p>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-4 py-2 text-sm text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !targetPrice.trim()}
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
            >
              {isSubmitting ? "Creating…" : "Create alert"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
