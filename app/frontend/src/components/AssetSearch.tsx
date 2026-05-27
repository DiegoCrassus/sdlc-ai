import { useState } from "react";

import { useAssetSearch } from "../hooks/useMarketData";

interface Props {
  onSelect: (symbol: string) => void;
}

export function AssetSearch({ onSelect }: Props) {
  const [query, setQuery] = useState("");
  const { data = [], isFetching } = useAssetSearch(query);

  return (
    <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
      <label className="mb-2 block text-sm text-slate-400" htmlFor="asset-search">
        Search assets
      </label>
      <input
        id="asset-search"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Try BTC, Apple, EUR..."
        className="w-full rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-sm text-white outline-none ring-emerald-500 focus:ring-2"
      />
      {query.length >= 2 && (
        <ul className="mt-3 max-h-40 overflow-y-auto text-sm">
          {isFetching && <li className="text-slate-500">Searching...</li>}
          {!isFetching && data.length === 0 && <li className="text-slate-500">No matches</li>}
          {data.map((hit) => (
            <li key={hit.asset_id}>
              <button
                type="button"
                className="flex w-full items-center justify-between rounded px-2 py-2 text-left hover:bg-slate-800"
                onClick={() => {
                  onSelect(hit.symbol);
                  setQuery("");
                }}
              >
                <span className="font-medium text-white">{hit.symbol}</span>
                <span className="text-slate-400">{hit.name}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
