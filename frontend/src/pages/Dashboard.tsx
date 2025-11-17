import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiService, Portfolio, Transaction, Stock } from '../services/api';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import './Dashboard.css';

export const Dashboard: React.FC = () => {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [portfoliosRes, transactionsRes, stocksRes] = await Promise.all([
        apiService.portfolios.getAll(),
        apiService.transactions.getAll(),
        apiService.stocks.getAll(),
      ]);
      setPortfolios(portfoliosRes.data);
      setTransactions(transactionsRes.data.slice(0, 5));
      setStocks(stocksRes.data);
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
                  {transactions.map((transaction) => (
                    <div key={transaction.id} className="transaction-item">
                      <div className="transaction-info">
                        <span className="transaction-ticker">{transaction.ticker_symbol}</span>
                        <span className={`transaction-type ${transaction.transaction_type}`}>
                          {transaction.transaction_type.toUpperCase()}
                        </span>
                      </div>
                      <div className="transaction-details">
                        <span>{transaction.quantity} @ ${transaction.price.toFixed(2)}</span>
                        <span className="transaction-date">
                          {new Date(transaction.executed_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))}
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

