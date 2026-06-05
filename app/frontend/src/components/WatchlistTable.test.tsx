import { render, screen, within } from "@testing-library/react";
import type { ComponentProps } from "react";
import { describe, expect, it, vi } from "vitest";

import type { WatchlistItem } from "../types/market";

import { WatchlistTable } from "./WatchlistTable";

function buildItem(overrides: Partial<WatchlistItem> = {}): WatchlistItem {
  return {
    symbol: "AAPL",
    name: "Apple Inc.",
    asset_class: "stock",
    price: 150,
    change_percent: 1.25,
    ...overrides,
  };
}

function renderTable(items: WatchlistItem[], extra: Partial<ComponentProps<typeof WatchlistTable>> = {}) {
  return render(
    <WatchlistTable
      items={items}
      selectedSymbol={items[0]?.symbol ?? ""}
      onSelect={vi.fn()}
      isLoading={false}
      onUpdateAllocation={vi.fn().mockResolvedValue(undefined)}
      isUpdatingAllocation={false}
      updateAllocationError={null}
      onUpdateInvested={vi.fn().mockResolvedValue(undefined)}
      isUpdatingInvested={false}
      updateInvestedError={null}
      alerts={[]}
      onCreateAlert={vi.fn().mockResolvedValue(undefined)}
      isCreatingAlert={false}
      createAlertError={null}
      {...extra}
    />,
  );
}

function rowForSymbol(symbol: string) {
  const cell = screen.getByText(symbol);
  const row = cell.closest("tr");
  if (!row) {
    throw new Error(`No table row found for symbol ${symbol}`);
  }
  return row;
}

describe("WatchlistTable", () => {
  describe("drift band badges", () => {
    it("renders on_target, warning, and off_target status badges", () => {
      renderTable([
        buildItem({
          symbol: "AAA",
          name: "On Target Co",
          drift_band: "on_target",
          drift_percent: 0.1,
          current_weight_percent: 25,
        }),
        buildItem({
          symbol: "BBB",
          name: "Warning Co",
          drift_band: "warning",
          drift_percent: 4.5,
          current_weight_percent: 30,
        }),
        buildItem({
          symbol: "CCC",
          name: "Off Target Co",
          drift_band: "off_target",
          drift_percent: -8.2,
          current_weight_percent: 12,
        }),
      ]);

      expect(within(rowForSymbol("AAA")).getByText("On target")).toBeTruthy();
      expect(within(rowForSymbol("BBB")).getByText("Warning")).toBeTruthy();
      expect(within(rowForSymbol("CCC")).getByText("Off target")).toBeTruthy();
    });

    it("shows signed drift percentages in the Drift column", () => {
      renderTable([
        buildItem({
          symbol: "DRF",
          drift_percent: 3.75,
          current_weight_percent: 40,
        }),
        buildItem({
          symbol: "NEG",
          drift_percent: -2.5,
          current_weight_percent: 10,
        }),
      ]);

      expect(within(rowForSymbol("DRF")).getByText("+3.75%")).toBeTruthy();
      expect(within(rowForSymbol("NEG")).getByText("-2.50%")).toBeTruthy();
    });
  });

  describe("empty and null states", () => {
    it("shows em dash for weight and drift when values are null (zero invested)", () => {
      renderTable([
        buildItem({
          symbol: "ZERO",
          invested_amount: 0,
          current_weight_percent: null,
          drift_percent: null,
          drift_band: null,
          suggestion_amount: null,
        }),
      ]);

      const row = rowForSymbol("ZERO");
      const dashes = within(row).getAllByText("—");
      expect(dashes.length).toBeGreaterThanOrEqual(3);
    });

    it("shows em dash for drift band when band is null", () => {
      renderTable([
        buildItem({
          symbol: "NOBAND",
          drift_band: null,
          current_weight_percent: null,
          drift_percent: null,
        }),
      ]);

      expect(within(rowForSymbol("NOBAND")).getAllByText("—").length).toBeGreaterThanOrEqual(1);
    });
  });

  describe("suggestion formatting", () => {
    it("formats buy suggestions with a leading plus and emerald styling", () => {
      renderTable([
        buildItem({
          symbol: "BUY",
          suggestion_amount: 1500.5,
          current_weight_percent: 20,
          drift_percent: -5,
          drift_band: "warning",
        }),
      ]);

      const suggestion = within(rowForSymbol("BUY")).getByText("+$1,500.50");
      expect(suggestion.className).toContain("text-emerald-400");
    });

    it("formats sell suggestions with rose styling", () => {
      renderTable([
        buildItem({
          symbol: "SELL",
          suggestion_amount: -750,
          current_weight_percent: 35,
          drift_percent: 6,
          drift_band: "off_target",
        }),
      ]);

      const suggestion = within(rowForSymbol("SELL")).getByText("$750.00");
      expect(suggestion.className).toContain("text-rose-400");
    });

    it("shows em dash when suggestion_amount is null", () => {
      renderTable([
        buildItem({
          symbol: "NOSUG",
          suggestion_amount: null,
          current_weight_percent: 15,
          drift_percent: 0,
        }),
      ]);

      expect(within(rowForSymbol("NOSUG")).getAllByText("—").length).toBeGreaterThanOrEqual(1);
    });
  });
});
