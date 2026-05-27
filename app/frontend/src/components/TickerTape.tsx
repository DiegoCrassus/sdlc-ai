import type { Quote } from "../types/market";

interface Props {
  quotes: Quote[];
}

function formatPrice(price: number): string {
  if (price >= 1000) return price.toLocaleString(undefined, { maximumFractionDigits: 2 });
  if (price >= 1) return price.toFixed(2);
  return price.toFixed(4);
}

export function TickerTape({ quotes }: Props) {
  if (quotes.length === 0) {
    return (
      <div className="overflow-hidden border-y border-slate-700/60 bg-surface-card py-3">
        <p className="px-4 text-sm text-slate-500">Loading ticker...</p>
      </div>
    );
  }

  const doubled = [...quotes, ...quotes];

  return (
    <div className="overflow-hidden border-y border-slate-700/60 bg-surface-card py-3">
      <div className="flex w-max animate-ticker gap-8 px-4">
        {doubled.map((quote, index) => {
          const positive = quote.change_percent >= 0;
          return (
            <div key={`${quote.symbol}-${index}`} className="flex items-center gap-3 whitespace-nowrap">
              <span className="font-semibold text-white">{quote.symbol}</span>
              <span className="text-slate-300">${formatPrice(quote.price)}</span>
              <span className={positive ? "text-emerald-400" : "text-rose-400"}>
                {positive ? "+" : ""}
                {quote.change_percent.toFixed(2)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
