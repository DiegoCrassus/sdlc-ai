import { Route, Routes } from "react-router-dom";
import { SessionBar } from "./components/SessionBar";
import { CharacterSheetPage } from "./pages/CharacterSheetPage";
import { CreateWorkspacePage } from "./pages/CreateWorkspacePage";
import { HomePage } from "./pages/HomePage";
import { WorkspacePage } from "./pages/WorkspacePage";

export default function App() {
  return (
    <div className="app-shell">
      <SessionBar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/create" element={<CreateWorkspacePage />} />
        <Route path="/workspace/:id" element={<WorkspacePage />} />
        <Route path="/workspace/:workspaceId/sheet/:sheetId" element={<CharacterSheetPage />} />
      </Routes>
    </div>
  );
}
