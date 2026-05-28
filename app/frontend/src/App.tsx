import { Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/layout/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { ForecastPage } from "./pages/ForecastPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/forecast" element={<ForecastPage />} />
      </Route>
    </Routes>
  );
}
