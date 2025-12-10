import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import type { Portfolio } from '../services/api';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { EditPortfolioModal } from '../components/EditPortfolioModal';
import { ToastContainer } from '../components/ToastContainer';
import { useToast } from '../hooks/useToast';
import './Portfolios.css';

export const Portfolios: React.FC = () => {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '' });
  const [editingPortfolio, setEditingPortfolio] = useState<Portfolio | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const { toasts, showSuccess, showError, removeToast } = useToast();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const portfoliosRes = await apiService.portfolios.getAll();
      setPortfolios(portfoliosRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await apiService.portfolios.create(formData);
      showSuccess('Portfolio created successfully!');
      await loadData();
      setShowForm(false);
      setFormData({ name: '' });
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      showError(err.response?.data?.detail || 'Error creating portfolio');
    }
  };

  const handleEdit = (portfolio: Portfolio) => {
    setEditingPortfolio(portfolio);
    setIsEditModalOpen(true);
  };

  const handleUpdate = async (id: number, name: string) => {
    try {
      await apiService.portfolios.update(id, { name });
      showSuccess('Portfolio updated successfully!');
      await loadData();
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      showError(err.response?.data?.detail || 'Error updating portfolio');
      throw error; // Re-throw to let modal handle it
    }
  };

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false);
    setEditingPortfolio(null);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this portfolio?')) return;
    try {
      await apiService.portfolios.delete(id);
      showSuccess('Portfolio deleted successfully!');
      await loadData();
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      showError(err.response?.data?.detail || 'Error deleting portfolio');
    }
  };

  if (loading) {
    return (
      <div className="portfolios">
        <div className="container">
          <div className="loading">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="portfolios">
      <ToastContainer toasts={toasts} removeToast={removeToast} />
      <div className="container">
        <div className="page-header slide-up">
          <h1>Portfolios</h1>
          <p>Manage your investment portfolios</p>
        </div>

        <div className="portfolios-actions">
          <Button onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : '+ Create Portfolio'}
          </Button>
        </div>

        {showForm && (
          <Card className="form-card fade-in">
            <h2 className="card-title">Create New Portfolio</h2>
            <form onSubmit={handleCreate} className="portfolio-form">
              <div className="form-group">
                <label>Portfolio Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ name: e.target.value })}
                  required
                  placeholder="My Portfolio"
                />
              </div>
              <Button type="submit" variant="primary">Create Portfolio</Button>
            </form>
          </Card>
        )}

        {portfolios.length === 0 ? (
          <Card className="empty-card fade-in">
            <p className="empty-state">No portfolios yet. Create your first portfolio to get started!</p>
          </Card>
        ) : (
          <div className="portfolios-grid">
            {portfolios.map((portfolio: Portfolio) => (
              <Card key={portfolio.id} hover className="portfolio-card fade-in">
                <div className="portfolio-header">
                  <h3 className="portfolio-name">{portfolio.name}</h3>
                  <div className="portfolio-actions">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEdit(portfolio)}
                      title="Edit portfolio"
                    >
                      ✏️
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(portfolio.id)}
                      title="Delete portfolio"
                    >
                      🗑️
                    </Button>
                  </div>
                </div>
                <div className="portfolio-info">
                  <div className="info-item">
                    <span className="info-label">Created:</span>
                    <span className="info-value">
                      {new Date(portfolio.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        <EditPortfolioModal
          isOpen={isEditModalOpen}
          onClose={handleCloseEditModal}
          portfolio={editingPortfolio}
          onUpdate={handleUpdate}
        />
      </div>
    </div>
  );
};

