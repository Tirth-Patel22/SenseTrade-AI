export default function WatchlistPanel({ ticker, setTicker }) {
  const watchlist = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"];
  return (
    <div className="rounded-lg border border-slate-800 bg-ink-900/70 p-4">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-300">Watchlist</h2>
      <div className="mt-3 flex flex-wrap gap-2">
        {watchlist.map((symbol) => (
          <button
            key={symbol}
            onClick={() => setTicker(symbol)}
            className={`rounded px-3 py-1.5 text-xs font-semibold ${
              ticker === symbol
                ? "bg-mint/20 text-mint ring-1 ring-mint/40"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            {symbol}
          </button>
        ))}
      </div>
    </div>
  );
}

