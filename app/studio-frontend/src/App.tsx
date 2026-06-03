import { Route, Routes } from "react-router-dom";

import { StudioLayout } from "./components/shell/StudioLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { StubPage } from "./pages/StubPage";

const stubs: { path: string; title: string; phase: string }[] = [
  { path: "workflows", title: "Workflows", phase: "S2 canvas" },
  { path: "builder", title: "Workflow Builder", phase: "S4 propose-only" },
  { path: "agents", title: "Agents & Subagents", phase: "S4–S5" },
  { path: "rules", title: "Rules & Skills", phase: "S4–S5" },
  { path: "commands", title: "Commands", phase: "S4–S5" },
  { path: "registry", title: "Registry", phase: "S5" },
  { path: "validation", title: "Validation", phase: "S5" },
  { path: "simulation", title: "Simulation", phase: "S5" },
  { path: "assistance", title: "Assistance", phase: "S5" },
  { path: "observability", title: "Observability", phase: "S3 SSE" },
  { path: "evidence", title: "Evidence & Delivery", phase: "S6" },
  { path: "settings", title: "Settings", phase: "meta" },
];

export default function App() {
  return (
    <Routes>
      <Route element={<StudioLayout />}>
        <Route path="/" element={<DashboardPage />} />
        {stubs.map((s) => (
          <Route
            key={s.path}
            path={s.path}
            element={<StubPage title={s.title} phase={s.phase} />}
          />
        ))}
      </Route>
    </Routes>
  );
}
