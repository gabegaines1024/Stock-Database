# Stock Tracker Frontend

A beautiful, Apple-inspired frontend for the Stock Tracker application built with React, TypeScript, and Vite.

## Features

- 🎨 **Stormy Morning Design** - Elegant dark theme with stormy gray and blue color palette
- 📱 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- ⚡ **Fast & Smooth** - Built with Vite for lightning-fast development and optimized builds
- 🎭 **Apple-like Interactions** - Smooth animations and transitions throughout
- 📊 **Dashboard** - Overview of portfolios, stocks, and transactions
- 🔍 **Stock Search** - Real-time stock search with price lookup
- 💼 **Portfolio Management** - Create and manage investment portfolios
- 💰 **Transaction Tracking** - Track buy and sell transactions

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file (optional, defaults to `http://localhost:8000`):
```bash
cp .env.example .env
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser to `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/       # Reusable UI components
│   ├── Button.tsx
│   ├── Card.tsx
│   └── Header.tsx
├── pages/           # Page components
│   ├── Dashboard.tsx
│   ├── StockSearch.tsx
│   ├── Portfolios.tsx
│   └── Transactions.tsx
├── services/        # API service layer
│   └── api.ts
├── App.tsx          # Main app component with routing
└── main.tsx         # Entry point
```

## Design System

The app uses a custom design system with CSS variables for:
- **Colors**: Stormy morning palette (dark grays, blues)
- **Typography**: System fonts for native feel
- **Spacing**: Consistent spacing scale
- **Shadows**: Layered shadow system
- **Transitions**: Smooth cubic-bezier animations

## API Integration

The frontend communicates with the FastAPI backend through the `apiService` in `src/services/api.ts`. All API calls are typed with TypeScript interfaces.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
