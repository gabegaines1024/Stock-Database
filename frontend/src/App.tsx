import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { StockSearch } from './pages/StockSearch';
import { Portfolios } from './pages/Portfolios';
import { Transactions } from './pages/Transactions';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="app">
          <Header />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/stocks" element={<StockSearch />} />
              <Route path="/portfolios" element={<Portfolios />} />
              <Route path="/transactions" element={<Transactions />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
