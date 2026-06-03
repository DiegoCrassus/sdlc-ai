import { Route, Routes } from "react-router-dom";

import { StudioLayout } from "./components/shell/StudioLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { ObservabilityPage } from "./pages/ObservabilityPage";
import { ConfigBuilderPage } from "./pages/ConfigBuilderPage";
import { RulesSkillsBuilderPage } from "./pages/RulesSkillsBuilderPage";
import { StubPage } from "./pages/StubPage";
import { WorkflowBuilderPage } from "./pages/WorkflowBuilderPage";
import { WorkflowsPage } from "./pages/WorkflowsPage";

const stubs: { path: string; title: string; phase: string }[] = [
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
        <Route
          path="agents"
          element={
            <ConfigBuilderPage
              kind="agent"
              title="Agents & Subagents"
              subtitle="Browse .cursor/agents, edit or draft from template, export propose-only patches."
            />
          }
        />
        <Route path="rules" element={<RulesSkillsBuilderPage />} />
        <Route
          path="commands"
          element={
            <ConfigBuilderPage
              kind="command"
              title="Commands"
              subtitle="Browse .cursor/commands, edit or draft slash commands as propose-only patches."
            />
          }
        />
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
