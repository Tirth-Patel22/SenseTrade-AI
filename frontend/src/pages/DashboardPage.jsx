import ExplainablePanel from "../components/ExplainablePanel";
import MarketChart from "../components/MarketChart";
import PortfolioPanel from "../components/PortfolioPanel";
import PredictionCard from "../components/PredictionCard";
import WatchlistPanel from "../components/WatchlistPanel";
import { useSenseTradeData } from "../hooks/useSenseTradeData";

export default function DashboardPage() {
  const { ticker, setTicker, marketData, prediction, loading, error } = useSenseTradeData("AAPL");

  return (
    <main className="mx-auto max-w-7xl px-4 py-6 md:px-6">
      <header className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">SenseTrade AI</p>
          <h1 className="text-2xl font-semibold text-slate-100">Financial Intelligence Dashboard</h1>
        </div>
        <div className="rounded-md border border-slate-700 bg-slate-900/70 px-3 py-2 text-sm text-slate-300">
          Active Ticker: <span className="font-semibold text-slate-100">{ticker}</span>
        </div>
      </header>

      {error && <div className="mb-4 rounded-md border border-coral/40 bg-coral/10 p-3 text-sm text-coral">{error}</div>}
      {loading && !error && (
        <div className="mb-4 rounded-md border border-slate-700 bg-slate-900/80 p-3 text-sm text-slate-300">Loading data...</div>
      )}

      <section className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <MarketChart candles={marketData} />
          <ExplainablePanel prediction={prediction} />
        </div>
        <div className="space-y-4">
          <PredictionCard prediction={prediction} />
          <WatchlistPanel ticker={ticker} setTicker={setTicker} />
          <PortfolioPanel />
        </div>
      </section>
    </main>
  );
}

