import { describe, expect, it } from "vitest";

import {
  isValidCompareSelection,
  parseCompareSymbols,
  serializeCompareSymbols,
} from "./compareQueryParams";

describe("compareQueryParams", () => {
  describe("parseCompareSymbols", () => {
    it("returns empty array for null or blank input", () => {
      expect(parseCompareSymbols(null)).toEqual([]);
      expect(parseCompareSymbols("")).toEqual([]);
      expect(parseCompareSymbols("   ")).toEqual([]);
    });

    it("parses comma-separated symbols and uppercases them", () => {
      expect(parseCompareSymbols("btc,eth")).toEqual(["BTC", "ETH"]);
      expect(parseCompareSymbols(" BTC , AAPL ")).toEqual(["BTC", "AAPL"]);
    });

    it("deduplicates symbols preserving first occurrence order", () => {
      expect(parseCompareSymbols("BTC,ETH,BTC,ETH")).toEqual(["BTC", "ETH"]);
    });

    it("caps selection at four unique symbols", () => {
      expect(parseCompareSymbols("BTC,ETH,SOL,AAPL,MSFT")).toEqual([
        "BTC",
        "ETH",
        "SOL",
        "AAPL",
      ]);
    });

    it("skips empty segments from trailing commas", () => {
      expect(parseCompareSymbols("BTC,ETH,")).toEqual(["BTC", "ETH"]);
    });
  });

  describe("serializeCompareSymbols", () => {
    it("serializes unique uppercase symbols joined by comma", () => {
      expect(serializeCompareSymbols(["btc", "eth"])).toBe("BTC,ETH");
    });

    it("deduplicates and caps at four symbols", () => {
      expect(serializeCompareSymbols(["BTC", "ETH", "BTC", "SOL", "AAPL", "MSFT"])).toBe(
        "BTC,ETH,SOL,AAPL",
      );
    });

    it("returns empty string for empty input", () => {
      expect(serializeCompareSymbols([])).toBe("");
    });
  });

  describe("isValidCompareSelection", () => {
    it("returns false when fewer than two symbols", () => {
      expect(isValidCompareSelection([])).toBe(false);
      expect(isValidCompareSelection(["BTC"])).toBe(false);
    });

    it("returns true for two to four symbols", () => {
      expect(isValidCompareSelection(["BTC", "ETH"])).toBe(true);
      expect(isValidCompareSelection(["BTC", "ETH", "SOL"])).toBe(true);
      expect(isValidCompareSelection(["BTC", "ETH", "SOL", "AAPL"])).toBe(true);
    });

    it("returns false when more than four unique symbols", () => {
      expect(isValidCompareSelection(["BTC", "ETH", "SOL", "AAPL", "MSFT"])).toBe(false);
    });
  });
});
