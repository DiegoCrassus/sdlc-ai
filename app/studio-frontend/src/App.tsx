import { Route, Routes } from "react-router-dom";

import { StudioLayout } from "./components/shell/StudioLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { ObservabilityPage } from "./pages/ObservabilityPage";
import { StubPage } from "./pages/StubPage";
import { WorkflowBuilderPage } from "./pages/WorkflowBuilderPage";
import { WorkflowsPage } from "./pages/WorkflowsPage";

const stubs: { path: string; title: string; phase: string }[] = [
  { path: "agents", title: "Agents & Subagents", phase: "S4–S5" },
  { path: "rules", title: "Rules & Skills", phase: "S4–S5" },
  { path: "commands", title: "Commands", phase: "S4–S5" },
  { path: "registry", title: "Registry", phase: "S5" },
  { path: "validation", title: "Validation", phase: "S5" },
  { path: "simulation", title: "Simulation", phase: "S5" },
  { path: "assistance", title: "Assistance", phase: "S5" },
  { path: "evidence", title: "Evidence & Delivery", phase: "S6" },
  { path: "settings", title: "Settings", phase: "meta" },
];

export default function App() {
  return (
    <Routes>
      <Route element={<StudioLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="workflows" element={<WorkflowsPage />} />
        <Route path="builder" element={<WorkflowBuilderPage />} />
        <Route path="observability" element={<ObservabilityPage />} />
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
