import { AssetSearch } from "./AssetSearch";

const MAX_SYMBOLS = 4;

interface Props {
  selectedSymbols: string[];
  onAdd: (symbol: string) => void;
  onRemove: (symbol: string) => void;
}

export function CompareAssetPicker({ selectedSymbols, onAdd, onRemove }: Props) {
  const atMax = selectedSymbols.length >= MAX_SYMBOLS;

  const handleAdd = (symbol: string) => {
    const normalized = symbol.trim().toUpperCase();
    if (!normalized || selectedSymbols.includes(normalized) || atMax) {
      return;
    }
    onAdd(normalized);
  };

  return (
    <div className="flex flex-col gap-4">
      <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
        <h3 className="mb-3 text-sm font-semibold text-white">Selected assets</h3>
        {selectedSymbols.length === 0 ? (
          <p className="text-sm text-slate-500">Add 2–4 symbols to compare.</p>
        ) : (
          <ul className="flex flex-wrap gap-2">
            {selectedSymbols.map((symbol) => (
              <li key={symbol}>
                <button
                  type="button"
                  onClick={() => onRemove(symbol)}
                  className="inline-flex items-center gap-1 rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-sm font-medium text-emerald-400 hover:bg-emerald-500/20"
                  title="Remove symbol"
                >
                  {symbol}
                  <span aria-hidden="true" className="text-emerald-300/80">
                    ×
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
        <p className="mt-3 text-xs text-slate-500">
          {selectedSymbols.length}/{MAX_SYMBOLS} selected
          {atMax ? " · maximum reached" : ""}
        </p>
      </section>

      <AssetSearch
        onSelect={handleAdd}
        disabled={atMax}
        excludeSymbols={selectedSymbols}
        placeholder={atMax ? "Maximum 4 symbols" : "Try BTC, Apple, EUR..."}
      />
    </div>
  );
}
