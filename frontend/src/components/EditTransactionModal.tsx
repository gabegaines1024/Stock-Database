import React, { useState, useEffect } from 'react';
import { Modal } from './Modal';
import { Button } from './Button';
import { apiService } from '../services/api';
import type { Transaction, Portfolio, Stock } from '../services/api';

interface EditTransactionModalProps {
  isOpen: boolean;
  onClose: () => void;
  transaction: Transaction | null;
  portfolios: Portfolio[];
  stocks: Stock[];
  onUpdate: (id: number, data: {
    portfolio_id: number;
    ticker_symbol: string;
    transaction_type: 'buy' | 'sell';
    quantity: number;
    price: number;
  }) => Promise<void>;
}

export const EditTransactionModal: React.FC<EditTransactionModalProps> = ({
  isOpen,
  onClose,
  transaction,
  portfolios,
  stocks,
  onUpdate,
}) => {
  const [formData, setFormData] = useState({
    portfolio_id: 1,
    ticker_symbol: '',
    transaction_type: 'buy' as 'buy' | 'sell',
    quantity: 0,
    price: 0,
  });
  const [currentPosition, setCurrentPosition] = useState<number | null>(null);
  const [positionLoading, setPositionLoading] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (transaction) {
      setFormData({
        portfolio_id: transaction.portfolio_id,
        ticker_symbol: transaction.ticker_symbol,
        transaction_type: transaction.transaction_type,
        quantity: transaction.quantity,
        price: transaction.price,
      });
    } else {
      setFormData({
        portfolio_id: portfolios[0]?.id || 1,
        ticker_symbol: stocks[0]?.ticker_symbol || '',
        transaction_type: 'buy',
        quantity: 0,
        price: 0,
      });
    }
  }, [transaction, isOpen, portfolios, stocks]);

  // Fetch position when transaction type is "sell" and portfolio/ticker are selected
  useEffect(() => {
    const fetchPosition = async () => {
      if (
        formData.transaction_type === 'sell' &&
        formData.portfolio_id &&
        formData.ticker_symbol
      ) {
        setPositionLoading(true);
        try {
          const response = await apiService.transactions.getPosition(
            formData.portfolio_id,
            formData.ticker_symbol
          );
          // For edit, we need to account for the current transaction's quantity
          // If editing a sell transaction, add its quantity back to available
          let availablePosition = response.data.position;
          if (transaction && transaction.transaction_type === 'sell') {
            availablePosition += transaction.quantity;
          }
          setCurrentPosition(availablePosition);
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
  }, [formData.transaction_type, formData.portfolio_id, formData.ticker_symbol, transaction]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!transaction) return;

    // Client-side validation for sell transactions
    if (formData.transaction_type === 'sell') {
      if (currentPosition === null) {
        // Error will be shown by parent component
        throw new Error('Unable to verify available holdings. Please try again.');
      }
      
      if (formData.quantity > currentPosition) {
        throw new Error(
          `Insufficient holdings. You can only sell ${currentPosition} shares, but you're trying to sell ${formData.quantity}.`
        );
      }
    }

    setLoading(true);
    try {
      await onUpdate(transaction.id, formData);
      onClose();
    } catch (error) {
      // Error handling is done in parent component via toast
      console.error('Error updating transaction:', error);
      throw error; // Re-throw to let parent handle it
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Edit Transaction">
      <form onSubmit={handleSubmit} className="edit-transaction-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="edit-portfolio">Portfolio</label>
            <select
              id="edit-portfolio"
              value={formData.portfolio_id}
              onChange={(e) => setFormData({ ...formData, portfolio_id: parseInt(e.target.value) })}
              required
              disabled={loading}
            >
              {portfolios.map((portfolio) => (
                <option key={portfolio.id} value={portfolio.id}>
                  {portfolio.name}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="edit-ticker">Ticker Symbol</label>
            <select
              id="edit-ticker"
              value={formData.ticker_symbol}
              onChange={(e) => setFormData({ ...formData, ticker_symbol: e.target.value })}
              required
              disabled={loading}
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
            <label htmlFor="edit-type">Type</label>
            <select
              id="edit-type"
              value={formData.transaction_type}
              onChange={(e) => setFormData({ ...formData, transaction_type: e.target.value as 'buy' | 'sell' })}
              required
              disabled={loading}
            >
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="edit-quantity">Quantity</label>
            <input
              id="edit-quantity"
              type="number"
              step="0.01"
              min="0"
              value={formData.quantity}
              onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) || 0 })}
              required
              disabled={loading}
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
            <label htmlFor="edit-price">Price</label>
            <input
              id="edit-price"
              type="number"
              step="0.01"
              min="0"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) || 0 })}
              required
              disabled={loading}
            />
          </div>
        </div>
        <div className="modal-actions">
          <Button
            type="button"
            variant="outline"
            onClick={handleClose}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="primary" 
            disabled={loading || !formData.ticker_symbol || formData.quantity <= 0 || formData.price <= 0}
          >
            {loading ? 'Updating...' : 'Update Transaction'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
