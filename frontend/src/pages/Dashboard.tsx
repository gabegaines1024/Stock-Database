import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import { stockPriceWebSocket } from '../services/websocket';
import type { Portfolio, Transaction, Stock } from '../services/api';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import './Dashboard.css';

export const Dashboard: React.FC = () => {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);
  const [livePrices, setLivePrices] = useState<Map<string, number>>(new Map());

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    // Subscribe to live price updates for unique tickers in transactions
    const uniqueTickers = new Set(transactions.map((t: Transaction) => t.ticker_symbol));
    
    const handlePriceUpdate = (ticker: string, price: number) => {
      setLivePrices((prev: Map<string, number>) => {
        const updated = new Map(prev);
        updated.set(ticker, price);
        return updated;
      });
    };

    Array.from(uniqueTickers).forEach((ticker: string) => {
      stockPriceWebSocket.subscribe(ticker, handlePriceUpdate);
    });

    return () => {
      // Cleanup: unsubscribe from all tickers
      Array.from(uniqueTickers).forEach((ticker: string) => {
        stockPriceWebSocket.unsubscribe(ticker, handlePriceUpdate);
      });
    };
  }, [transactions]);

  const loadData = async () => {
    try {
      const [portfoliosRes, transactionsRes, stocksRes] = await Promise.all([
        apiService.portfolios.getAll().catch((err: unknown) => {
          console.error('Error loading portfolios:', err);
          return { data: [] };
        }),
        apiService.transactions.getAll().catch((err: unknown) => {
          console.error('Error loading transactions:', err);
          return { data: [] };
        }),
        apiService.stocks.getAll().catch((err: unknown) => {
          console.error('Error loading stocks:', err);
          return { data: [] };
        }),
      ]);
      setPortfolios(portfoliosRes.data || []);
      setTransactions((transactionsRes.data || []).slice(0, 5));
      setStocks(stocksRes.data || []);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalPortfolios = portfolios.length;
  const totalStocks = stocks.length;
  const recentTransactions = transactions.length;

  if (loading) {
    return (
      <div className="dashboard">
        <div className="container">
          <div className="loading">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="container">
        <div className="dashboard-hero slide-up">
          <h1>Welcome to StockTracker</h1>
          <p className="hero-subtitle">
            Manage your portfolios, track stocks, and monitor your investments
          </p>
        </div>

        <div className="dashboard-stats">
          <Card hover className="stat-card fade-in">
            <div className="stat-icon">📊</div>
            <div className="stat-value">{totalPortfolios}</div>
            <div className="stat-label">Portfolios</div>
            <Link to="/portfolios">
              <Button variant="ghost" size="sm" className="stat-link">
                View All →
              </Button>
            </Link>
          </Card>

          <Card hover className="stat-card fade-in">
            <div className="stat-icon">📈</div>
            <div className="stat-value">{totalStocks}</div>
            <div className="stat-label">Tracked Stocks</div>
            <Link to="/stocks">
              <Button variant="ghost" size="sm" className="stat-link">
                Explore →
              </Button>
            </Link>
          </Card>

          <Card hover className="stat-card fade-in">
            <div className="stat-icon">💼</div>
            <div className="stat-value">{recentTransactions}</div>
            <div className="stat-label">Recent Transactions</div>
            <Link to="/transactions">
              <Button variant="ghost" size="sm" className="stat-link">
                View All →
              </Button>
            </Link>
          </Card>
        </div>

        <div className="dashboard-content">
          <Card className="recent-transactions">
            <div className="card-header">
              <h2 className="card-title">Recent Transactions</h2>
            </div>
            <div className="card-body">
              {transactions.length === 0 ? (
                <p className="empty-state">No transactions yet. Start by adding a transaction!</p>
              ) : (
                <div className="transactions-list">
                  {transactions.map((transaction: Transaction) => {
                    const livePrice = livePrices.get(transaction.ticker_symbol);
                    const priceChangeNum = livePrice 
                      ? ((livePrice - transaction.price) / transaction.price * 100)
                      : null;
                    const priceChange = priceChangeNum !== null ? priceChangeNum.toFixed(2) : null;
                    return (
                      <div key={transaction.id} className="transaction-item">
                        <div className="transaction-info">
                          <span className="transaction-ticker">{transaction.ticker_symbol}</span>
                          <span className={`transaction-type ${transaction.transaction_type}`}>
                            {transaction.transaction_type.toUpperCase()}
                          </span>
                        </div>
                        <div className="transaction-details">
                          <span>{transaction.quantity} @ ${transaction.price.toFixed(2)}</span>
                          {livePrice && (
                            <span className="transaction-live-price">
                              Now: ${livePrice.toFixed(2)} 
                              {priceChange && priceChangeNum !== null && (
                                <span className={priceChangeNum >= 0 ? 'price-up' : 'price-down'}>
                                  {' '}({priceChangeNum >= 0 ? '+' : ''}{priceChange}%)
                                </span>
                              )}
                              <span className="live-indicator"> ●</span>
                            </span>
                          )}
                          <span className="transaction-date">
                            {new Date(transaction.executed_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
            <div className="card-footer">
              <Link to="/transactions">
                <Button variant="outline">View All Transactions</Button>
              </Link>
            </div>
          </Card>

          <Card className="quick-actions">
            <div className="card-header">
              <h2 className="card-title">Quick Actions</h2>
            </div>
            <div className="card-body">
              <div className="actions-grid">
                <Link to="/stocks">
                  <Button variant="primary" size="lg" className="action-btn">
                    🔍 Search Stocks
                  </Button>
                </Link>
                <Link to="/portfolios">
                  <Button variant="secondary" size="lg" className="action-btn">
                    ➕ Create Portfolio
                  </Button>
                </Link>
                <Link to="/transactions">
                  <Button variant="outline" size="lg" className="action-btn">
                    💰 Add Transaction
                  </Button>
                </Link>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
