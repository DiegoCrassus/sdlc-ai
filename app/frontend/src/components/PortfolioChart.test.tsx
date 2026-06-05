import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { PortfolioHistoryPoint } from "@shared/types/portfolio";

import { PortfolioChart } from "./PortfolioChart";

vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  LineChart: ({ children, data }: { children: React.ReactNode; data: unknown[] }) => (
    <div data-testid="line-chart" data-point-count={data.length}>
      {children}
    </div>
  ),
  Line: () => <div data-testid="recharts-line" role="img" aria-label="Portfolio value line" />,
  CartesianGrid: () => null,
  XAxis: () => null,
  YAxis: () => null,
  Tooltip: () => null,
}));

function buildPoint(day: number, totalValue: number): PortfolioHistoryPoint {
  const date = new Date(Date.UTC(2026, 0, day));
  const snapshot_date = date.toISOString().slice(0, 10);
  return {
    snapshot_date,
    total_value: totalValue,
    daily_change_pct: day === 1 ? 0 : 0.5,
    cumulative_return_pct: day === 1 ? 0 : (day - 1) * 0.5,
  };
}

describe("PortfolioChart", () => {
  it("renders line chart with seven history points", () => {
    const points = Array.from({ length: 7 }, (_, index) =>
      buildPoint(index + 1, 10_000 + index * 250),
    );

    render(<PortfolioChart points={points} isLoading={false} days={30} />);

    expect(screen.getByTestId("portfolio-chart")).toBeTruthy();
    expect(screen.getByText("Portfolio Value")).toBeTruthy();
    expect(screen.getByTestId("responsive-container")).toBeTruthy();
    expect(screen.getByTestId("line-chart").getAttribute("data-point-count")).toBe("7");
    expect(screen.getByTestId("recharts-line")).toBeTruthy();
  });

  it("shows loading skeleton while fetching", () => {
    render(<PortfolioChart points={[]} isLoading={true} days={30} />);

    expect(screen.getByTestId("portfolio-chart-loading")).toBeTruthy();
  });

  it("shows empty state when no points", () => {
    render(<PortfolioChart points={[]} isLoading={false} days={30} />);

    expect(screen.getByTestId("portfolio-chart-empty")).toBeTruthy();
  });
});
