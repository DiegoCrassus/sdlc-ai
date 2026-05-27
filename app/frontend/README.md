# app/frontend — MarketPulse Dashboard

React 19 + TypeScript + Vite dashboard for MarketPulse.

## Stack

- React 19, TypeScript, Vite
- Tailwind CSS v3
- TanStack Query (30s polling)
- Recharts (price chart)

## Setup

```bash
cd app/frontend
npm install
```

Ensure the API is running on port 8000 (see `app/backend/README.md`). Vite proxies `/api` to `http://127.0.0.1:8000`.

## Development

```bash
npm run dev
```

Open http://localhost:5173

## Production build

```bash
npm run build
```

Static output: `app/frontend/dist/`

## Environment

Optional override for API base (default uses Vite proxy `/api/v1`):

```bash
VITE_API_BASE=http://127.0.0.1:8000/api/v1
```

## Layout

```
src/
  pages/DashboardPage.tsx
  components/
  hooks/useMarketData.ts
  api/client.ts
  types/market.ts
```
