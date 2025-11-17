import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import type { Transaction, Portfolio, Stock } from '../services/api';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import './Transactions.css';

export const Transactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    portfolio_id: 1,
    ticker_symbol: '',
    transaction_type: 'buy' as 'buy' | 'sell',
    quantity: 0,
    price: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [transactionsRes, portfoliosRes, stocksRes] = await Promise.all([
        apiService.transactions.getAll(),
        apiService.portfolios.getAll(),
        apiService.stocks.getAll(),
      ]);
      setTransactions(transactionsRes.data);
      setPortfolios(portfoliosRes.data);
      setStocks(stocksRes.data);
      if (portfoliosRes.data.length > 0) {
        setFormData({ ...formData, portfolio_id: portfoliosRes.data[0].id });
      }
      if (stocksRes.data.length > 0) {
        setFormData({ ...formData, ticker_symbol: stocksRes.data[0].ticker_symbol });
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.transactions.create(formData);
      await loadData();
      setShowForm(false);
      setFormData({
        portfolio_id: portfolios[0]?.id || 1,
        ticker_symbol: stocks[0]?.ticker_symbol || '',
        transaction_type: 'buy',
        quantity: 0,
        price: 0,
      });
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error creating transaction');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this transaction?')) return;
    try {
      await apiService.transactions.delete(id);
      await loadData();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error deleting transaction');
    }
  };

  if (loading) {
    return (
      <div className="transactions">
        <div className="container">
          <div className="loading">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="transactions">
      <div className="container">
        <div className="page-header slide-up">
          <h1>Transactions</h1>
          <p>Track your buy and sell transactions</p>
        </div>

        <div className="transactions-actions">
          <Button onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : '+ Add Transaction'}
          </Button>
        </div>

        {showForm && (
          <Card className="form-card fade-in">
            <h2 className="card-title">Add New Transaction</h2>
            <form onSubmit={handleCreate} className="transaction-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Portfolio</label>
                  <select
                    value={formData.portfolio_id}
                    onChange={(e) => setFormData({ ...formData, portfolio_id: parseInt(e.target.value) })}
                    required
                  >
                    {portfolios.map((portfolio) => (
                      <option key={portfolio.id} value={portfolio.id}>
                        {portfolio.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Ticker Symbol</label>
                  <select
                    value={formData.ticker_symbol}
                    onChange={(e) => setFormData({ ...formData, ticker_symbol: e.target.value })}
                    required
                  >
                    {stocks.map((stock) => (
                      <option key={stock.id} value={stock.ticker_symbol}>
                        {stock.ticker_symbol} - {stock.company_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Type</label>
                  <select
                    value={formData.transaction_type}
                    onChange={(e) => setFormData({ ...formData, transaction_type: e.target.value as 'buy' | 'sell' })}
                    required
                  >
                    <option value="buy">Buy</option>
                    <option value="sell">Sell</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Quantity</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.quantity}
                    onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Price</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
                    required
                  />
                </div>
              </div>
              <Button type="submit" variant="primary">Add Transaction</Button>
            </form>
          </Card>
        )}

        {transactions.length === 0 ? (
          <Card className="empty-card fade-in">
            <p className="empty-state">No transactions yet. Add your first transaction to get started!</p>
          </Card>
        ) : (
          <Card className="transactions-list-card fade-in">
            <h2 className="card-title">All Transactions</h2>
            <div className="transactions-table">
              <div className="table-header">
                <div>Date</div>
                <div>Portfolio</div>
                <div>Ticker</div>
                <div>Type</div>
                <div>Quantity</div>
                <div>Price</div>
                <div>Total</div>
                <div>Actions</div>
              </div>
              {transactions.map((transaction) => (
                <div key={transaction.id} className="table-row">
                  <div>{new Date(transaction.executed_at).toLocaleDateString()}</div>
                  <div>{transaction.portfolio_id}</div>
                  <div className="ticker-cell">{transaction.ticker_symbol}</div>
                  <div>
                    <span className={`transaction-type-badge ${transaction.transaction_type}`}>
                      {transaction.transaction_type.toUpperCase()}
                    </span>
                  </div>
                  <div>{transaction.quantity}</div>
                  <div>${transaction.price.toFixed(2)}</div>
                  <div className="total-cell">
                    ${(transaction.quantity * transaction.price).toFixed(2)}
                  </div>
                  <div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(transaction.id)}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

