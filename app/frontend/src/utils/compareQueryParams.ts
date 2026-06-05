const MIN_SYMBOLS = 2;
const MAX_SYMBOLS = 4;

export function parseCompareSymbols(value: string | null): string[] {
  if (!value?.trim()) {
    return [];
  }

  const seen = new Set<string>();
  const symbols: string[] = [];

  for (const raw of value.split(",")) {
    const symbol = raw.trim().toUpperCase();
    if (!symbol || seen.has(symbol)) {
      continue;
    }
    seen.add(symbol);
    symbols.push(symbol);
    if (symbols.length >= MAX_SYMBOLS) {
      break;
    }
  }

  return symbols;
}

export function serializeCompareSymbols(symbols: string[]): string {
  const unique: string[] = [];
  const seen = new Set<string>();

  for (const raw of symbols) {
    const symbol = raw.trim().toUpperCase();
    if (!symbol || seen.has(symbol)) {
      continue;
    }
    seen.add(symbol);
    unique.push(symbol);
    if (unique.length >= MAX_SYMBOLS) {
      break;
    }
  }

  return unique.join(",");
}

export function isValidCompareSelection(symbols: string[]): boolean {
  const seen = new Set<string>();
  let count = 0;

  for (const raw of symbols) {
    const symbol = raw.trim().toUpperCase();
    if (!symbol || seen.has(symbol)) {
      continue;
    }
    seen.add(symbol);
    count += 1;
  }

  return count >= MIN_SYMBOLS && count <= MAX_SYMBOLS;
}
