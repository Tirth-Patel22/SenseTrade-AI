import { formatMoney } from "../utils/formatters";

const mockPortfolio = [
  { ticker: "AAPL", quantity: 12, average_buy_price: 172.4 },
  { ticker: "MSFT", quantity: 6, average_buy_price: 401.12 },
  { ticker: "NVDA", quantity: 9, average_buy_price: 893.2 }
];

export default function PortfolioPanel() {
  return (
    <div className="rounded-lg border border-slate-800 bg-ink-900/70 p-4">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-300">Portfolio</h2>
      <div className="mt-3 space-y-2">
        {mockPortfolio.map((position) => (
          <div
            key={position.ticker}
            className="flex items-center justify-between rounded-md border border-slate-800 bg-ink-950/75 px-3 py-2 text-sm"
          >
            <span className="font-semibold text-slate-200">{position.ticker}</span>
            <span className="text-slate-400">{position.quantity} shares</span>
            <span className="text-slate-300">{formatMoney(position.average_buy_price)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

