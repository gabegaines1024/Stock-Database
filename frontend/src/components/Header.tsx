import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './Button';
import './Header.css';

export const Header: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Don't show header on login/register pages
  if (!isAuthenticated && (location.pathname === '/login' || location.pathname === '/register')) {
    return null;
  }

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="header-logo">
          <span className="logo-icon">📈</span>
          <span className="logo-text">StockTracker</span>
        </Link>
        
        {isAuthenticated && (
          <>
            <nav className="header-nav">
              <Link
                to="/"
                className={`nav-link ${isActive('/') ? 'active' : ''}`}
              >
                Dashboard
              </Link>
              <Link
                to="/stocks"
                className={`nav-link ${isActive('/stocks') ? 'active' : ''}`}
              >
                Stocks
              </Link>
              <Link
                to="/portfolios"
                className={`nav-link ${isActive('/portfolios') ? 'active' : ''}`}
              >
                Portfolios
              </Link>
              <Link
                to="/transactions"
                className={`nav-link ${isActive('/transactions') ? 'active' : ''}`}
              >
                Transactions
              </Link>
            </nav>

            <div className="header-user">
              <span className="user-name">{user?.username}</span>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </>
        )}
      </div>
    </header>
  );
};

