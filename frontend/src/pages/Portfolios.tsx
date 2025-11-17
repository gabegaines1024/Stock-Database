import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import type { Portfolio, User } from '../services/api';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import './Portfolios.css';

export const Portfolios: React.FC = () => {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', user_id: 1 });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [portfoliosRes, usersRes] = await Promise.all([
        apiService.portfolios.getAll(),
        apiService.users.getAll(),
      ]);
      setPortfolios(portfoliosRes.data);
      setUsers(usersRes.data);
      if (usersRes.data.length > 0) {
        setFormData({ ...formData, user_id: usersRes.data[0].id });
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
      await apiService.portfolios.create(formData);
      await loadData();
      setShowForm(false);
      setFormData({ name: '', user_id: users[0]?.id || 1 });
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error creating portfolio');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this portfolio?')) return;
    try {
      await apiService.portfolios.delete(id);
      await loadData();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error deleting portfolio');
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
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  placeholder="My Portfolio"
                />
              </div>
              <div className="form-group">
                <label>User</label>
                <select
                  value={formData.user_id}
                  onChange={(e) => setFormData({ ...formData, user_id: parseInt(e.target.value) })}
                  required
                >
                  {users.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.username} ({user.email})
                    </option>
                  ))}
                </select>
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
            {portfolios.map((portfolio) => (
              <Card key={portfolio.id} hover className="portfolio-card fade-in">
                <div className="portfolio-header">
                  <h3 className="portfolio-name">{portfolio.name}</h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(portfolio.id)}
                  >
                    🗑️
                  </Button>
                </div>
                <div className="portfolio-info">
                  <div className="info-item">
                    <span className="info-label">User ID:</span>
                    <span className="info-value">{portfolio.user_id}</span>
                  </div>
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
      </div>
    </div>
  );
};

