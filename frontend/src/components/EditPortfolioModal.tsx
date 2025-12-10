import React, { useState, useEffect } from 'react';
import { Modal } from './Modal';
import { Button } from './Button';
import type { Portfolio } from '../services/api';

interface EditPortfolioModalProps {
  isOpen: boolean;
  onClose: () => void;
  portfolio: Portfolio | null;
  onUpdate: (id: number, name: string) => Promise<void>;
}

export const EditPortfolioModal: React.FC<EditPortfolioModalProps> = ({
  isOpen,
  onClose,
  portfolio,
  onUpdate,
}) => {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (portfolio) {
      setName(portfolio.name);
    } else {
      setName('');
    }
  }, [portfolio, isOpen]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!portfolio || !name.trim()) return;

    setLoading(true);
    try {
      await onUpdate(portfolio.id, name.trim());
      onClose();
    } catch (error) {
      // Error handling is done in parent component via toast
      console.error('Error updating portfolio:', error);
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
    <Modal isOpen={isOpen} onClose={handleClose} title="Edit Portfolio">
      <form onSubmit={handleSubmit} className="edit-portfolio-form">
        <div className="form-group">
          <label htmlFor="portfolio-name">Portfolio Name</label>
          <input
            id="portfolio-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            placeholder="My Portfolio"
            disabled={loading}
            autoFocus
          />
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
          <Button type="submit" variant="primary" disabled={loading || !name.trim()}>
            {loading ? 'Updating...' : 'Update Portfolio'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
