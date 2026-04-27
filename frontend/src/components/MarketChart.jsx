import {
  Bar,
  CartesianGrid,
  Cell,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { formatMoney, sentimentColor } from "../utils/formatters";

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || payload.length === 0) return null;

  const point = payload[0]?.payload || {};
  return (
    <div
      style={{
        background: "#0f172a",
        border: "1px solid #1e293b",
        borderRadius: 10,
        padding: "10px 12px",
        minWidth: 220
      }}
    >
      <div style={{ color: "#e2e8f0", fontWeight: 700, marginBottom: 6 }}>{label}</div>
      <div style={{ color: "#cbd5e1", fontSize: 13, lineHeight: 1.7 }}>
        <div>Open: {formatMoney(point.open)}</div>
        <div>High: {formatMoney(point.high)}</div>
        <div>Low: {formatMoney(point.low)}</div>
        <div>Close: {formatMoney(point.close)}</div>
        <div>Sentiment: {Number(point.sentiment_score || 0).toFixed(3)}</div>
      </div>
    </div>
  );
}

export default function MarketChart({ candles }) {
  const data = (candles || [])
    .map((row) => ({
      ...row,
      open: Number.parseFloat(row.open),
      high: Number.parseFloat(row.high),
      low: Number.parseFloat(row.low),
      close: Number.parseFloat(row.close),
      sentiment_score: Number.parseFloat(row.sentiment_score || 0)
    }))
    .filter(
      (row) =>
        Number.isFinite(row.open) &&
        Number.isFinite(row.high) &&
        Number.isFinite(row.low) &&
        Number.isFinite(row.close)
    );

  return (
    <div className="rounded-lg border border-slate-800 bg-ink-900/70 p-4">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-300">Price + Sentiment Heat</h2>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 8, right: 14, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 11 }} minTickGap={28} />
            <YAxis
              yAxisId="price"
              domain={["dataMin - 2", "dataMax + 2"]}
              tick={{ fill: "#94a3b8", fontSize: 11 }}
            />
            <YAxis yAxisId="sentiment" hide domain={[-1, 1]} />

            <Tooltip content={<CustomTooltip />} />

            <Bar yAxisId="sentiment" dataKey="sentiment_score" barSize={8} opacity={0.22}>
              {data.map((entry) => (
                <Cell key={`s-${entry.date}`} fill={sentimentColor(entry.sentiment_score)} />
              ))}
            </Bar>

            <Line
              yAxisId="price"
              type="monotone"
              dataKey="close"
              connectNulls
              stroke="#22d3ee"
              strokeWidth={3}
              dot={{ r: 1.8, fill: "#22d3ee", strokeWidth: 0 }}
              activeDot={{ r: 5, fill: "#38bdf8" }}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
