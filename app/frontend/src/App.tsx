import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AssetDetail } from "./pages/AssetDetail";
import { Discover } from "./pages/Discover";
import { PortfolioPage } from "./pages/Portfolio";
import { WatchlistPage } from "./pages/Watchlist";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Discover />} />
          <Route path="watchlist" element={<WatchlistPage />} />
          <Route path="assets/:assetId" element={<AssetDetail />} />
          <Route path="portfolio" element={<PortfolioPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
