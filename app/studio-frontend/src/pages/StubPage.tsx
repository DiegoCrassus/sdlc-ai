import { DerivedBanner } from "../components/common/DerivedBanner";

type StubPageProps = {
  title: string;
  phase: string;
};

export function StubPage({ title, phase }: StubPageProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <DerivedBanner />
      <div>
        <h1 className="text-2xl font-bold text-white">{title}</h1>
        <p className="mt-2 text-slate-400">
          Placeholder for {phase}. Implementation follows the Studio Service roadmap.
        </p>
      </div>
      <div className="rounded-xl border border-dashed border-slate-700 bg-surface-card/50 p-8 text-center text-sm text-slate-500">
        Screen stub — no API wiring yet.
      </div>
    </div>
  );
}
