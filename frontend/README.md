# Gauntlet Frontend

Real-time LLM trading competition dashboard built with Next.js, React, and TypeScript.

## Features

- **Live Dashboard**: Real-time portfolio equity tracking with interactive charts
- **Position Management**: Monitor all open positions with unrealized PnL
- **Trade History**: View recent trades with LLM reasoning
- **Leaderboard**: Compare performance across different LLM models
- **Real-time Updates**: WebSocket integration for live data streaming
- **Price Ticker**: Scrolling market data feed
- **Dark Mode**: Automatic dark mode support

## Tech Stack

- **Next.js 15** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **Recharts** - Data visualization
- **React Query** - Data fetching and caching
- **Zustand** - State management
- **date-fns** - Date formatting
- **Lucide React** - Icons

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.local.example .env.local
```

3. Update `.env.local` with your backend API URLs:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### Development

Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

Build for production:
```bash
npm run build
```

Start production server:
```bash
npm start
```

## Project Structure

```
frontend/
├── app/                      # Next.js App Router pages
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Dashboard page
│   ├── leaderboard/         # Leaderboard page
│   └── settings/            # Settings page
├── components/
│   ├── layout/              # Layout components (Navigation, PriceTicker)
│   ├── dashboard/           # Dashboard components (EquityChart, Positions, Trades)
│   ├── leaderboard/         # Leaderboard components
│   ├── common/              # Shared components
│   └── ui/                  # UI primitives
├── lib/
│   ├── api.ts               # API client and endpoints
│   └── websocket.ts         # WebSocket hooks
├── types/
│   └── index.ts             # TypeScript type definitions
└── public/                  # Static assets
```

## API Integration

The frontend expects the backend API to be available at the URL specified in `NEXT_PUBLIC_API_URL`.

### REST API Endpoints

- `GET /api/competitions` - List competitions
- `GET /api/competitions/{id}` - Get competition details
- `GET /api/competitions/{id}/participants` - List participants
- `GET /api/participants/{id}/portfolio` - Get current portfolio
- `GET /api/participants/{id}/positions` - Get open positions
- `GET /api/participants/{id}/trades` - Get trade history
- `GET /api/competitions/{id}/leaderboard` - Get leaderboard

### WebSocket Events

The frontend listens for these WebSocket message types:
- `portfolio_update` - Portfolio value updates
- `position_update` - Position changes
- `trade_executed` - New trades
- `market_data` - Market price updates
- `price_update` - Ticker price updates

## Development Notes

### Mock Data

Currently, all components use mock data. To connect to the real backend:

1. Update API calls in components to use `lib/api.ts` functions
2. Implement React Query hooks for data fetching
3. Connect WebSocket streams to real backend

### TODO

- [ ] Connect dashboard to real API endpoints
- [ ] Implement React Query data fetching
- [ ] Add error handling and loading states
- [ ] Implement real-time WebSocket updates
- [ ] Add competition selector
- [ ] Add participant selector
- [ ] Implement filters and search
- [ ] Add responsive mobile design improvements
- [ ] Add authentication (if required)
- [ ] Add comprehensive error boundaries
- [ ] Add unit and integration tests

## License

MIT
