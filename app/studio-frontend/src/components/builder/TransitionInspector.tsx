import type { WorkflowTransitionDraft } from "../../types/builder";

type TransitionInspectorProps = {
  draft: WorkflowTransitionDraft | null;
  onChange: (draft: WorkflowTransitionDraft) => void;
  onRemove: (edgeDisplayId: string) => void;
  onClose: () => void;
};

function parseList(value: string): string[] {
  return value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

function joinList(items: string[]): string {
  return items.join("\n");
}

export function TransitionInspector({
  draft,
  onChange,
  onRemove,
  onClose,
}: TransitionInspectorProps) {
  if (!draft) {
    return (
      <div className="rounded-xl border border-dashed border-slate-700 bg-surface-card/40 p-4 text-sm text-slate-500">
        Select a transition edge to edit agent, skill, and preconditions.
      </div>
    );
  }

  const update = (patch: Partial<WorkflowTransitionDraft>) => {
    onChange({ ...draft, ...patch });
  };

  return (
    <div className="flex flex-col gap-4 rounded-xl border border-slate-800 bg-surface-card p-4">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">Transition</p>
          <p className="mt-1 font-mono text-xs text-studio-accent">{draft.id}</p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded px-2 py-1 text-xs text-slate-400 hover:bg-slate-800 hover:text-white"
        >
          Close
        </button>
      </div>

      <label className="block text-sm">
        <span className="text-slate-400">Name</span>
        <input
          className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white"
          value={draft.name}
          onChange={(event) => update({ name: event.target.value })}
        />
      </label>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <label className="block">
          <span className="text-slate-400">From stage</span>
          <input
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs text-white"
            value={draft.from_stage}
            onChange={(event) => update({ from_stage: event.target.value })}
          />
        </label>
        <label className="block">
          <span className="text-slate-400">To stage</span>
          <input
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs text-white"
            value={draft.to_stage}
            onChange={(event) => update({ to_stage: event.target.value })}
          />
        </label>
      </div>

      <label className="block text-sm">
        <span className="text-slate-400">Description</span>
        <textarea
          className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white"
          rows={2}
          value={draft.description}
          onChange={(event) => update({ description: event.target.value })}
        />
      </label>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <label className="block">
          <span className="text-slate-400">Agent</span>
          <input
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs text-white"
            value={draft.agent}
            onChange={(event) => update({ agent: event.target.value })}
          />
        </label>
        <label className="block">
          <span className="text-slate-400">Skill</span>
          <input
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs text-white"
            value={draft.skill}
            onChange={(event) => update({ skill: event.target.value })}
          />
        </label>
      </div>

      <label className="block text-sm">
        <span className="text-slate-400">Preconditions (one per line)</span>
        <textarea
          className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs text-white"
          rows={3}
          value={joinList(draft.preconditions)}
          onChange={(event) => update({ preconditions: parseList(event.target.value) })}
        />
      </label>

      <label className="block text-sm">
        <span className="text-slate-400">Outputs (one per line)</span>
        <textarea
          className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs text-white"
          rows={3}
          value={joinList(draft.outputs)}
          onChange={(event) => update({ outputs: parseList(event.target.value) })}
        />
      </label>

      <button
        type="button"
        onClick={() => onRemove(draft.edgeDisplayId)}
        className="rounded-md border border-studio-fail/40 px-3 py-2 text-sm text-studio-fail hover:bg-red-950/40"
      >
        Remove transition
      </button>
    </div>
  );
}
