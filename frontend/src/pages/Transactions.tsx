import React, { useEffect, useState, useCallback } from 'react';
import { apiService } from '../services/api';
import type { Transaction, Portfolio, Stock } from '../services/api';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { EditTransactionModal } from '../components/EditTransactionModal';
import { ToastContainer } from '../components/ToastContainer';
import { useToast } from '../hooks/useToast';
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
  const [currentPosition, setCurrentPosition] = useState<number | null>(null);
  const [positionLoading, setPositionLoading] = useState(false);
  const [priceLoading, setPriceLoading] = useState(false);
  const [tickerValid, setTickerValid] = useState<boolean | null>(null);
  const [companyName, setCompanyName] = useState<string>('');
  const [editingTransaction, setEditingTransaction] = useState<Transaction | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const { toasts, showSuccess, showError, showWarning, removeToast } = useToast();

  useEffect(() => {
    loadData();
  }, []);

  // Fetch position when transaction type is "sell" and portfolio/ticker are selected
  useEffect(() => {
    const fetchPosition = async () => {
      if (
        formData.transaction_type === 'sell' &&
        formData.portfolio_id &&
        formData.ticker_symbol &&
        tickerValid
      ) {
        setPositionLoading(true);
        try {
          const response = await apiService.transactions.getPosition(
            formData.portfolio_id,
            formData.ticker_symbol
          );
          setCurrentPosition(response.data.position);
        } catch (error: any) {
          setCurrentPosition(0);
          console.error('Error fetching position:', error);
        } finally {
          setPositionLoading(false);
        }
      } else {
        setCurrentPosition(null);
      }
    };

    fetchPosition();
  }, [formData.transaction_type, formData.portfolio_id, formData.ticker_symbol, tickerValid]);

  // Debounced price fetch when ticker changes
  useEffect(() => {
    const ticker = formData.ticker_symbol.trim().toUpperCase();
    if (ticker.length < 1) {
      setTickerValid(null);
      setCompanyName('');
      setFormData(prev => ({ ...prev, price: 0 }));
      return;
    }

    const timeoutId = setTimeout(async () => {
      await fetchPrice(ticker);
    }, 500); // 500ms debounce

    return () => clearTimeout(timeoutId);
  }, [formData.ticker_symbol]);

  const fetchPrice = async (ticker: string) => {
    setPriceLoading(true);
    setTickerValid(null);
    
    try {
      // Try to get the price
      const priceResponse = await apiService.stocks.getPrice(ticker);
      setFormData(prev => ({ ...prev, price: priceResponse.data.price }));
      setTickerValid(true);
      
      // Check if stock exists in our database, if not try to get info
      const existingStock = stocks.find(s => s.ticker_symbol.toUpperCase() === ticker);
      if (existingStock) {
        setCompanyName(existingStock.company_name);
      } else {
        // Try to search for company name
        try {
          const searchResponse = await apiService.stocks.search(ticker);
          const match = searchResponse.data.results?.find(
            r => r['1. symbol'].toUpperCase() === ticker
          );
          if (match) {
            setCompanyName(match['2. name']);
          } else {
            setCompanyName(ticker); // Use ticker as fallback
          }
        } catch {
          setCompanyName(ticker);
        }
      }
    } catch (error) {
      console.error('Error fetching price:', error);
      setTickerValid(false);
      setFormData(prev => ({ ...prev, price: 0 }));
      setCompanyName('');
    } finally {
      setPriceLoading(false);
    }
  };

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
      
      setFormData(prev => ({
        ...prev,
        portfolio_id: portfoliosRes.data.length > 0 ? portfoliosRes.data[0].id : prev.portfolio_id,
      }));
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const ensureStockExists = async (ticker: string, name: string): Promise<boolean> => {
    const existingStock = stocks.find(s => s.ticker_symbol.toUpperCase() === ticker.toUpperCase());
    if (existingStock) {
      return true;
    }

    // Create the stock
    try {
      await apiService.stocks.create({
        ticker_symbol: ticker.toUpperCase(),
        company_name: name || ticker,
      });
      return true;
    } catch (error: any) {
      // Stock might already exist (race condition) - that's ok
      if (error.response?.status === 409 || error.response?.data?.detail?.includes('already exists')) {
        return true;
      }
      console.error('Error creating stock:', error);
      return false;
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!tickerValid) {
      showError('Please enter a valid ticker symbol');
      return;
    }

    if (formData.price <= 0) {
      showError('Unable to get price for this ticker. Please try again.');
      return;
    }

    // Client-side validation for sell transactions
    if (formData.transaction_type === 'sell') {
      if (currentPosition === null) {
        showError('Unable to verify available holdings. Please try again.');
        return;
      }
      
      if (formData.quantity > currentPosition) {
        showError(
          `Insufficient holdings. You can only sell ${currentPosition} shares, but you're trying to sell ${formData.quantity}.`
        );
        return;
      }
    }

    try {
      // Ensure stock exists in database before creating transaction
      const ticker = formData.ticker_symbol.trim().toUpperCase();
      const stockCreated = await ensureStockExists(ticker, companyName);
      if (!stockCreated) {
        showError('Failed to register stock. Please try again.');
        return;
      }

      await apiService.transactions.create({
        ...formData,
        ticker_symbol: ticker,
      });
      showSuccess('Transaction created successfully!');
      setShowForm(false);
      setCurrentPosition(null);
      setTickerValid(null);
      setCompanyName('');
      setFormData(prev => ({
        ...prev,
        ticker_symbol: '',
        transaction_type: 'buy',
        quantity: 0,
        price: 0,
      }));
      await loadData();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Error creating transaction';
      showError(errorMessage);
    }
  };

  const handleEdit = (transaction: Transaction) => {
    setEditingTransaction(transaction);
    setIsEditModalOpen(true);
  };

  const handleUpdate = async (
    id: number,
    data: {
      portfolio_id: number;
      ticker_symbol: string;
      transaction_type: 'buy' | 'sell';
      quantity: number;
      price: number;
    }
  ) => {
    try {
      await apiService.transactions.update(id, data);
      showSuccess('Transaction updated successfully!');
      await loadData();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Error updating transaction';
      showError(errorMessage);
      throw error;
    }
  };

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false);
    setEditingTransaction(null);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) return;
    try {
      await apiService.transactions.delete(id);
      showSuccess('Transaction deleted successfully!');
      await loadData();
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Error deleting transaction');
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
      <ToastContainer toasts={toasts} removeToast={removeToast} />
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
                  <input
                    type="text"
                    placeholder="Enter ticker (e.g., AAPL, GOOGL)"
                    value={formData.ticker_symbol}
                    onChange={(e) => setFormData({ ...formData, ticker_symbol: e.target.value.toUpperCase() })}
                    className={tickerValid === false ? 'input-error' : tickerValid === true ? 'input-valid' : ''}
                    required
                  />
                  {priceLoading && (
                    <div className="ticker-status loading">Looking up ticker...</div>
                  )}
                  {!priceLoading && tickerValid === true && companyName && (
                    <div className="ticker-status valid">✓ {companyName}</div>
                  )}
                  {!priceLoading && tickerValid === false && (
                    <div className="ticker-status invalid">✗ Invalid ticker symbol</div>
                  )}
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
                    min="0.01"
                    value={formData.quantity || ''}
                    onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) || 0 })}
                    onBlur={() => {
                      if (formData.transaction_type === 'sell' && currentPosition !== null) {
                        if (formData.quantity > currentPosition) {
                          showWarning(
                            `You're trying to sell ${formData.quantity} shares, but you only have ${currentPosition} available.`
                          );
                        }
                      }
                    }}
                    placeholder="Enter quantity"
                    required
                  />
                  {formData.transaction_type === 'sell' && currentPosition !== null && (
                    <div className="position-info">
                      {positionLoading ? (
                        <span className="position-loading">Loading position...</span>
                      ) : (
                        <span className={`position-available ${formData.quantity > currentPosition ? 'position-error' : ''}`}>
                          Available to sell: {currentPosition}
                        </span>
                      )}
                    </div>
                  )}
                </div>
                <div className="form-group">
                  <label>Price (Auto-fetched)</label>
                  <div className="price-display-field">
                    {priceLoading ? (
                      <span className="price-loading">Fetching...</span>
                    ) : formData.price > 0 ? (
                      <span className="price-value">${formData.price.toFixed(2)}</span>
                    ) : (
                      <span className="price-placeholder">Enter ticker to get price</span>
                    )}
                  </div>
                </div>
              </div>
              {formData.quantity > 0 && formData.price > 0 && (
                <div className="transaction-total">
                  Total: <strong>${(formData.quantity * formData.price).toFixed(2)}</strong>
                </div>
              )}
              <Button 
                type="submit" 
                variant="primary"
                disabled={!tickerValid || formData.price <= 0 || formData.quantity <= 0}
              >
                {formData.transaction_type === 'buy' ? 'Buy Stock' : 'Sell Stock'}
              </Button>
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
                  <div>{portfolios.find(p => p.id === transaction.portfolio_id)?.name || transaction.portfolio_id}</div>
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
                  <div className="transaction-actions">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEdit(transaction)}
                      title="Edit transaction"
                    >
                      ✏️
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(transaction.id)}
                      title="Delete transaction"
                    >
                      🗑️
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        <EditTransactionModal
          isOpen={isEditModalOpen}
          onClose={handleCloseEditModal}
          transaction={editingTransaction}
          portfolios={portfolios}
          stocks={stocks}
          onUpdate={handleUpdate}
        />
      </div>
    </div>
  );
};
