import { Route, Routes } from "react-router-dom";
import { CreateCampaignPage } from "./pages/CreateCampaignPage";
import { HomePage } from "./pages/HomePage";
import { WorkspacePage } from "./pages/WorkspacePage";

export default function App() {
  return (
    <div className="app-shell">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/create" element={<CreateCampaignPage />} />
        <Route path="/workspace/:id" element={<WorkspacePage />} />
      </Routes>
    </div>
  );
}
