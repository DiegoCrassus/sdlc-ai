import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";

import { studioApi } from "../api/client";
import { ProposalPanel } from "../components/builder/ProposalPanel";
import { ProposedBanner } from "../components/builder/ProposedBanner";
import { TransitionInspector } from "../components/builder/TransitionInspector";
import { WorkflowBuilderCanvas } from "../components/builder/WorkflowBuilderCanvas";
import {
  buildWorkflowProposalRequest,
  createTransitionDraft,
  draftsFromCanvas,
} from "../components/builder/workflowDraft";
import type { WorkflowTransitionDraft } from "../types/builder";
import type { ProposalResponse } from "../types/proposals";

export function WorkflowBuilderPage() {
  const [searchParams] = useSearchParams();
  const highlightedNodeId = searchParams.get("node");

  const [drafts, setDrafts] = useState<WorkflowTransitionDraft[]>([]);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [proposalTitle, setProposalTitle] = useState("Workflow transition update");
  const [simulatedCard, setSimulatedCard] = useState("INVES-N");
  const [proposal, setProposal] = useState<ProposalResponse | null>(null);
  const [initialized, setInitialized] = useState(false);

  const canvasQuery = useQuery({
    queryKey: ["studio", "canvas", "full", "builder"],
    queryFn: () => studioApi.canvasFull({ entity_type: "stage" }),
    refetchInterval: 60_000,
  });

  const sessionQuery = useQuery({
    queryKey: ["studio", "session", "gate"],
    queryFn: studioApi.sessionGate,
  });

  useEffect(() => {
    const card = sessionQuery.data?.gate?.card;
    if (card) {
      setSimulatedCard(card);
    }
  }, [sessionQuery.data?.gate?.card]);

  useEffect(() => {
    if (canvasQuery.data && !initialized) {
      setDrafts(draftsFromCanvas(canvasQuery.data.nodes, canvasQuery.data.edges));
      setInitialized(true);
    }
  }, [canvasQuery.data, initialized]);

  const nodes = canvasQuery.data?.nodes ?? [];
  const nodesById = useMemo(() => new Map(nodes.map((node) => [node.id, node])), [nodes]);

  const selectedDraft = useMemo(
    () => drafts.find((draft) => draft.edgeDisplayId === selectedEdgeId) ?? null,
    [drafts, selectedEdgeId],
  );

  const updateDraft = useCallback((updated: WorkflowTransitionDraft) => {
    setDrafts((current) =>
      current.map((draft) => (draft.edgeDisplayId === updated.edgeDisplayId ? updated : draft)),
    );
    setProposal(null);
  }, []);

  const onConnectStages = useCallback(
    (sourceDisplayId: string, targetDisplayId: string) => {
      const existing = drafts.find(
        (draft) =>
          draft.sourceDisplayId === sourceDisplayId && draft.targetDisplayId === targetDisplayId,
      );
      if (existing) {
        setSelectedEdgeId(existing.edgeDisplayId);
        return;
      }

      const created = createTransitionDraft(sourceDisplayId, targetDisplayId, nodesById);
      if (!created) {
        return;
      }

      setDrafts((current) => [...current, created]);
      setSelectedEdgeId(created.edgeDisplayId);
      setProposal(null);
    },
    [drafts, nodesById],
  );

  const onRemoveEdge = useCallback((edgeDisplayId: string) => {
    setDrafts((current) => current.filter((draft) => draft.edgeDisplayId !== edgeDisplayId));
    setSelectedEdgeId((current) => (current === edgeDisplayId ? null : current));
    setProposal(null);
  }, []);

  const createProposalMutation = useMutation({
    mutationFn: () => {
      const body = buildWorkflowProposalRequest(drafts, proposalTitle.trim(), simulatedCard.trim());
      return studioApi.createProposal(body);
    },
    onSuccess: setProposal,
  });

  if (canvasQuery.isError) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <ProposedBanner />
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/40 p-4 text-red-200">
          <p className="font-medium">Cannot load workflow builder</p>
          <p className="mt-1 text-sm">
            Start the backend with <code className="text-red-100">make studio-dev</code>, then
            refresh.
          </p>
          <p className="mt-2 text-xs text-red-300/80">{canvasQuery.error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex max-w-[1600px] flex-col gap-4">
      <ProposedBanner />

      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">Workflow Builder</h1>
          <p className="mt-1 text-sm text-slate-400">
            Connect stage nodes to draft transitions, then export a propose-only patch via{" "}
            <code className="text-slate-300">POST /studio/proposals</code>.
          </p>
        </div>
        <Link
          to="/workflows"
          className="rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800"
        >
          Back to canvas
        </Link>
      </div>

      <div className="grid gap-4 rounded-xl border border-slate-800 bg-surface-card/30 p-4 lg:grid-cols-[1fr_320px]">
        <div className="space-y-3">
          <p className="text-xs text-slate-500">
            Drag from one stage handle to another to add a transition. Select an edge to edit
            metadata. Press Delete to remove.
          </p>
          {canvasQuery.isLoading ? (
            <p className="text-slate-400">Loading stages…</p>
          ) : (
            <div className="h-[calc(100vh-22rem)] min-h-[420px]">
              <WorkflowBuilderCanvas
                nodes={nodes}
                drafts={drafts}
                selectedEdgeId={selectedEdgeId}
                highlightedNodeId={highlightedNodeId}
                onSelectEdge={setSelectedEdgeId}
                onConnectStages={onConnectStages}
                onRemoveEdge={onRemoveEdge}
              />
            </div>
          )}
        </div>

        <div className="space-y-4">
          <TransitionInspector
            draft={selectedDraft}
            onChange={updateDraft}
            onRemove={onRemoveEdge}
            onClose={() => setSelectedEdgeId(null)}
          />

          <div className="rounded-xl border border-slate-800 bg-surface-card p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">Export proposal</p>
            <label className="mt-3 block text-sm">
              <span className="text-slate-400">Title</span>
              <input
                className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white"
                value={proposalTitle}
                onChange={(event) => setProposalTitle(event.target.value)}
              />
            </label>
            <label className="mt-3 block text-sm">
              <span className="text-slate-400">Simulated gate card</span>
              <input
                className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs text-white"
                value={simulatedCard}
                onChange={(event) => setSimulatedCard(event.target.value)}
              />
            </label>
            <button
              type="button"
              disabled={createProposalMutation.isPending || drafts.length === 0}
              onClick={() => createProposalMutation.mutate()}
              className="mt-4 w-full rounded-md bg-studio-accent px-4 py-2 text-sm font-medium text-slate-950 hover:bg-sky-300 disabled:opacity-50"
            >
              {createProposalMutation.isPending ? "Creating proposal…" : "Create proposal"}
            </button>
            {createProposalMutation.error ? (
              <p className="mt-2 text-sm text-red-300">
                {(createProposalMutation.error as Error).message}
              </p>
            ) : null}
          </div>
        </div>
      </div>

      {proposal ? (
        <ProposalPanel
          proposal={proposal}
          onUpdated={setProposal}
          onDiscard={() => setProposal(null)}
        />
      ) : null}
    </div>
  );
}
