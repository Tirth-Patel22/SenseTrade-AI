export default function ExplainablePanel({ prediction }) {
  const headlines = prediction?.explanations || [];
  return (
    <div className="rounded-lg border border-slate-800 bg-ink-900/70 p-4">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-300">Explainable AI</h2>
      <p className="mt-1 text-xs text-slate-400">Top headlines used for current sentiment aggregation.</p>
      <div className="mt-3 space-y-3">
        {headlines.length === 0 && <p className="text-sm text-slate-400">No explanation headlines available yet.</p>}
        {headlines.map((item, idx) => (
          <div key={`${item.headline}-${idx}`} className="rounded-md border border-slate-800 bg-ink-950/80 p-3">
            <p className="text-sm text-slate-100">{item.headline}</p>
            <p className="mt-1 text-xs text-slate-400">
              Label: <span className="uppercase">{item.label}</span> | Score: {Number(item.score).toFixed(3)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

