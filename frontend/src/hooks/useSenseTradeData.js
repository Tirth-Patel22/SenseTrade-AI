import { useEffect, useState } from "react";
import api from "../api/client";

export function useSenseTradeData(initialTicker = "AAPL") {
  const [ticker, setTicker] = useState(initialTicker);
  const [marketData, setMarketData] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    const run = async () => {
      setLoading(true);
      setError("");
      try {
        const [marketResp, predResp] = await Promise.all([
          api.get(`market/${ticker}/`),
          api.get(`predict/${ticker}/`)
        ]);
        if (!active) return;
        setMarketData(marketResp.data.candles || []);
        setPrediction(predResp.data);
      } catch (err) {
        if (!active) return;
        setError(err?.response?.data?.detail || "Failed to load SenseTrade data.");
      } finally {
        if (active) setLoading(false);
      }
    };
    run();
    return () => {
      active = false;
    };
  }, [ticker]);

  return {
    ticker,
    setTicker,
    marketData,
    prediction,
    loading,
    error
  };
}

