import { formatMoney } from "../utils/formatters";

function signalTheme(signal) {
  if (signal === "BUY") return "text-mint";
  if (signal === "SELL") return "text-coral";
  return "text-amber";
}

export default function PredictionCard({ prediction }) {
  if (!prediction) return null;
  return (
    <div className="rounded-lg border border-slate-800 bg-ink-900/70 p-4">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-300">Hybrid Signal</h2>
      <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-slate-400">Action</p>
          <p className={`text-lg font-semibold ${signalTheme(prediction.signal)}`}>{prediction.signal}</p>
        </div>
        <div>
          <p className="text-slate-400">Confidence</p>
          <p className="text-lg font-semibold text-slate-100">{(prediction.confidence * 100).toFixed(1)}%</p>
        </div>
        <div>
          <p className="text-slate-400">Current</p>
          <p className="font-medium text-slate-100">{formatMoney(prediction.current_price)}</p>
        </div>
        <div>
          <p className="text-slate-400">Forecast</p>
          <p className="font-medium text-slate-100">{formatMoney(prediction.price_forecast)}</p>
        </div>
      </div>
    </div>
  );
}

