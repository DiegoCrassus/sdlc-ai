import type { WatchlistItem } from "../types/market";

interface Props {
  items: WatchlistItem[];
  selectedSymbol: string;
  onSelect: (symbol: string) => void;
  isLoading: boolean;
}

export function WatchlistTable({ items, selectedSymbol, onSelect, isLoading }: Props) {
  if (isLoading) {
    return <div className="h-64 animate-pulse rounded-xl bg-surface-card" />;
  }

  return (
    <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
      <h2 className="mb-3 text-lg font-semibold text-white">Watchlist</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="pb-2 pr-4">Symbol</th>
              <th className="pb-2 pr-4">Name</th>
              <th className="pb-2 pr-4">Price</th>
              <th className="pb-2">Change</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => {
              const active = item.symbol === selectedSymbol;
              const positive = item.change_percent >= 0;
              return (
                <tr
                  key={item.symbol}
                  className={`cursor-pointer border-t border-slate-700/40 ${active ? "bg-slate-800/60" : "hover:bg-slate-800/30"}`}
                  onClick={() => onSelect(item.symbol)}
                >
                  <td className="py-2 pr-4 font-medium text-white">{item.symbol}</td>
                  <td className="py-2 pr-4 text-slate-300">{item.name}</td>
                  <td className="py-2 pr-4 text-slate-200">${item.price.toLocaleString()}</td>
                  <td className={`py-2 ${positive ? "text-emerald-400" : "text-rose-400"}`}>
                    {positive ? "+" : ""}
                    {item.change_percent.toFixed(2)}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
