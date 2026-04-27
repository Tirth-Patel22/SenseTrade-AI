# SenseTrade AI

SenseTrade AI is a full-stack financial intelligence platform scaffold that combines:

- LSTM time-series forecasting on OHLCV market data
- FinBERT-powered sentiment scoring from financial news
- A hybrid prediction API that returns Buy/Sell/Hold + confidence + forecast
- A React dashboard with candlestick charts and sentiment heat overlays

## Monorepo Layout

```text
backend/   Django + DRF + JWT + ML services
frontend/  React + Tailwind + Recharts dashboard
```

## Quick Start (Scaffold)

1. Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

2. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Core Endpoints

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET /api/watchlist/`
- `GET /api/portfolio/`
- `GET /api/market/<ticker>/`
- `GET /api/predict/<ticker>/`

## Notes

- This is an initial production-grade scaffold focused on architecture and integration points.
- The model training/inference pipeline is implemented as boilerplate and can be expanded with persisted model artifacts, feature stores, and background task queues.
